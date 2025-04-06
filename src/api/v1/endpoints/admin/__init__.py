from litestar import Router

from .user import UserController


def setup_admin_controllers() -> Router:
    router = Router("/admin", route_handlers=[])
    router.register(UserController)
    return router
