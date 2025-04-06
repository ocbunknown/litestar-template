from litestar.types.composite_types import Middleware

from .proccess_time import ProcessTimeHeader
from .request_id import XRequestIdMiddleware


def setup_middlewares() -> tuple[Middleware, ...]:
    return (
        XRequestIdMiddleware(),
        ProcessTimeHeader(),
    )
