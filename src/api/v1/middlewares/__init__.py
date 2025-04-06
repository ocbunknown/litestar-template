from litestar import Router
from litestar.middleware.base import DefineMiddleware

from .auth import AuthenticationMiddleware


def setup_middlewares(router: Router) -> None:
    router.middleware.append(
        DefineMiddleware(
            AuthenticationMiddleware,
            exclude_http_methods=["OPTIONS", "HEAD"],
        )
    )
