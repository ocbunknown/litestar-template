from litestar import Controller, Request, Response, post, status_codes
from litestar.datastructures import Cookie, State
from litestar.middleware.rate_limit import RateLimitConfig

from src.api.common.interfaces.mediator import Mediator
from src.api.v1 import handlers
from src.common import dtos
from src.common.di import Depends
from src.settings.core import Settings


class AuthController(Controller):
    path = "/auth"
    tags = ["Authorization"]

    @post(
        "/login",
        status_code=status_codes.HTTP_200_OK,
        exclude_auth=True,
        middleware=[RateLimitConfig(rate_limit=("minute", 10)).middleware],
    )
    async def login_endpoint(
        self,
        data: handlers.auth.LoginQuery,
        settings: Depends[Settings],
        mediator: Depends[Mediator],
    ) -> Response[dtos.Token]:
        result: dtos.TokensExpire = await mediator.send(data)
        response = Response(dtos.Token(token=result.tokens.access))
        response.set_cookie(
            Cookie(
                key="refresh_token",
                value=result.tokens.refresh,
                expires=int(result.refresh_expire.timestamp()),
                httponly=True,
                secure=settings.app.production,
                samesite="lax",
            )
        )
        return response

    @post(
        "/register",
        status_code=status_codes.HTTP_200_OK,
        exclude_auth=True,
        middleware=[RateLimitConfig(rate_limit=("minute", 5)).middleware],
    )
    async def register_endpoint(
        self,
        data: handlers.auth.RegisterQuery,
        mediator: Depends[Mediator],
    ) -> dtos.User:
        return await mediator.send(data)

    @post(
        "/register/confirm",
        status_code=status_codes.HTTP_201_CREATED,
        exclude_auth=True,
        middleware=[RateLimitConfig(rate_limit=("minute", 10)).middleware],
    )
    async def register_confirm_endpoint(
        self,
        data: handlers.auth.ConfirmRegisterQuery,
        settings: Depends[Settings],
        mediator: Depends[Mediator],
    ) -> Response[dtos.Token]:
        result: dtos.TokensExpire = await mediator.send(data)
        response = Response(dtos.Token(token=result.tokens.access))
        response.set_cookie(
            Cookie(
                key="refresh_token",
                value=result.tokens.refresh,
                expires=int(result.refresh_expire.timestamp()),
                httponly=True,
                secure=settings.app.production,
                samesite="lax",
            )
        )
        return response

    @post(
        "/refresh",
        status_code=status_codes.HTTP_200_OK,
        exclude_auth=True,
    )
    async def refresh_endpoint(
        self,
        data: dtos.Fingerprint,
        request: Request[None, None, State],
        settings: Depends[Settings],
        mediator: Depends[Mediator],
    ) -> Response[dtos.Token]:
        result: dtos.TokensExpire = await mediator.send(
            handlers.auth.RefreshTokenQuery(
                data=data, refresh_token=request.cookies.get("refresh_token", "")
            )
        )
        response = Response(dtos.Token(token=result.tokens.access))
        response.set_cookie(
            Cookie(
                key="refresh_token",
                value=result.tokens.refresh,
                expires=int(result.refresh_expire.timestamp()),
                httponly=True,
                secure=settings.app.production,
                samesite="lax",
            )
        )
        return response

    @post(
        "/logout",
        status_code=status_codes.HTTP_200_OK,
        security=[{"BearerToken": []}],
    )
    async def logout_endpoint(
        self,
        request: Request[dtos.User, None, State],
        mediator: Depends[Mediator],
    ) -> Response[dtos.Status]:
        result: dtos.Status = await mediator.send(
            handlers.auth.LogoutQuery(
                user_uuid=request.user.uuid,
                refresh_token=request.cookies.get("refresh_token", ""),
            )
        )
        response = Response(result)
        response.delete_cookie(key="refresh_token")
        return response
