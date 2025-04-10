from functools import wraps
from typing import Callable, override

from dishka.integrations.litestar import inject, inject_websocket
from litestar import Controller, Router
from litestar.handlers import BaseRouteHandler, HTTPRouteHandler, WebsocketListener
from litestar.handlers.websocket_handlers import WebsocketListenerRouteHandler
from litestar.handlers.websocket_handlers._utils import ListenerHandler
from litestar.routes import BaseRoute
from litestar.types import ControllerRouterHandler


def _inject_based_on_handler_type(
    value: BaseRouteHandler,
) -> BaseRouteHandler:
    if isinstance(value, HTTPRouteHandler):
        value._fn = inject(value._fn)

    if isinstance(value, WebsocketListenerRouteHandler) and isinstance(
        value._fn,
        ListenerHandler,
    ):
        value = value(inject_websocket(value._fn._fn))

    return value


def _inject_route_handlers[**P](
    get_route_handlers: Callable[P, list[BaseRouteHandler]],
) -> Callable[P, list[BaseRouteHandler]]:
    @wraps(get_route_handlers)
    def _wrapper(*args: P.args, **kwargs: P.kwargs) -> list[BaseRouteHandler]:
        return [
            _inject_based_on_handler_type(route)
            for route in get_route_handlers(*args, **kwargs)
        ]

    return _wrapper


def _resolve_value(
    router: Router,
    value: ControllerRouterHandler,
) -> ControllerRouterHandler:
    if isinstance(value, Router):
        return value

    if isinstance(value, BaseRouteHandler):
        return _inject_based_on_handler_type(value)

    if isinstance(value, type):
        if issubclass(value, Controller):
            value.get_route_handlers = _inject_route_handlers(  # type: ignore[method-assign]
                value.get_route_handlers,
            )
        if issubclass(value, WebsocketListener):
            return _inject_based_on_handler_type(value(router).to_handler())

    return value


class DishkaRouter(Router):
    __slots__ = ()

    @override
    def register(self, value: ControllerRouterHandler) -> list[BaseRoute]:
        return super().register(_resolve_value(self, value))
