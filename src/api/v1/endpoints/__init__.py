from litestar import Router

from .admin import setup_admin_controllers
from .auth import AuthController
from .healthcheck import healthcheck_endpoint
from .user import UserController


def setup_controllers(router: Router) -> None:
    router.register(healthcheck_endpoint)
    router.register(UserController)
    router.register(AuthController)

    router.register(setup_admin_controllers())
