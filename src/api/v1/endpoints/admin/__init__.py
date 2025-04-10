from src.api.v1.integration.dishka import DishkaRouter

from .user import UserController


def setup_admin_controllers() -> DishkaRouter:
    router = DishkaRouter("/admin", route_handlers=[])
    router.register(UserController)
    return router
