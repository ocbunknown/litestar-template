from litestar import Router

from src.api.common import tools
from src.api.v1.di import setup_dependencies
from src.api.v1.endpoints import setup_controllers
from src.api.v1.integration.dishka import DishkaRouter
from src.api.v1.middlewares import setup_middlewares
from src.settings.core import Settings


def init_v1_router(
    *sub_routers: Router, path: str = "/v1", settings: Settings
) -> tools.RouterState:
    router = DishkaRouter(path, route_handlers=sub_routers)

    setup_controllers(router)
    setup_middlewares(router)
    state = setup_dependencies(settings)

    return tools.RouterState(router=router, state=state)
