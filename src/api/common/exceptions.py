import traceback
from functools import partial
from typing import Any, Callable

from litestar import MediaType, Request, Response
from litestar import status_codes as status
from litestar.exceptions import ClientException
from litestar.types import ExceptionHandlersMap
from uuid_utils.compat import uuid4

import src.common.exceptions as exc
from src.common.logger import log

JsonResponse = Response[dict[str, Any]]
type BasicRequest = Request[Any, Any, Any]


def setup_exception_handlers() -> ExceptionHandlersMap:
    return {
        exc.TooManyRequestsError: error_handler(status.HTTP_429_TOO_MANY_REQUESTS),
        exc.ServiceNotImplementedError: error_handler(status.HTTP_501_NOT_IMPLEMENTED),
        exc.ConflictError: error_handler(status.HTTP_409_CONFLICT),
        exc.AppException: error_handler(status.HTTP_500_INTERNAL_SERVER_ERROR),
        exc.NotFoundError: error_handler(status.HTTP_404_NOT_FOUND),
        exc.UnAuthorizedError: error_handler(status.HTTP_401_UNAUTHORIZED),
        exc.ForbiddenError: error_handler(status.HTTP_403_FORBIDDEN),
        exc.BadRequestError: error_handler(status.HTTP_400_BAD_REQUEST),
        exc.ServiceUnavailableError: error_handler(status.HTTP_503_SERVICE_UNAVAILABLE),
        exc.BadGatewayError: error_handler(status.HTTP_502_BAD_GATEWAY),
        Exception: error_handler(status.HTTP_500_INTERNAL_SERVER_ERROR),
    }


def error_handler(
    status_code: int,
) -> Callable[..., JsonResponse]:
    return partial(app_error_handler, status_code=status_code)


def app_error_handler(
    request: BasicRequest, exc: Exception, status_code: int
) -> JsonResponse:
    return handle_error(
        request,
        exception=exc,
        status_code=status_code,
    )


def handle_error(
    request: BasicRequest,
    exception: Exception,
    status_code: int,
) -> JsonResponse:
    ticket = request.state.get("request_id", uuid4().hex)
    tb_str = "".join(
        traceback.format_exception(type(exception), exception, exception.__traceback__)
    )
    log.error(
        f"Ticket: {ticket}\n"
        f"Method: {request.method}\n"
        f"Path: {request.url.path}\n"
        f"Handle error: {type(exception).__name__} -> {exception.args}\n"
        f"Traceback:\n{tb_str}"
    )
    if isinstance(exception, exc.AppException):
        error_dict = exception.as_dict()
        error_dict["content"] |= {"ticket": ticket}
        return JsonResponse(
            **error_dict,
            status_code=status_code,
            media_type=MediaType.JSON,
        )

    if isinstance(exception, ClientException):
        return JsonResponse(
            content={
                "message": type(exception).__name__,
                "details": exception.extra,
                "ticket": ticket,
            },
            status_code=exception.status_code,
            media_type=MediaType.JSON,
        )

    response = JsonResponse(
        **exc.ForbiddenError(
            message="Something went wrong",
            ticket=ticket,
        ).as_dict(),
        status_code=status_code,
        media_type=MediaType.JSON,
    )
    return response
