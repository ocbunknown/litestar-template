from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

from dishka.integrations.litestar import setup_dishka
from litestar import Litestar
from litestar.config.app import AppConfig
from litestar.config.cors import CORSConfig
from litestar.middleware.logging import LoggingMiddlewareConfig
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import SwaggerRenderPlugin
from litestar.openapi.spec.components import Components
from litestar.openapi.spec.security_scheme import SecurityScheme
from litestar.stores.redis import RedisStore
from litestar.stores.registry import StoreRegistry
from redis.asyncio import Redis

from src.api.common.broker.nats.connection import create_nats_connection
from src.api.common.broker.nats.core import NatsBroker
from src.api.common.exceptions import setup_exception_handlers
from src.api.common.middlewares import setup_middlewares
from src.api.common.tools import ClosableProxy, RouterState
from src.common.di import container
from src.core.settings import Settings


@asynccontextmanager
async def lifespan(app: Litestar) -> AsyncIterator[None]:
    try:
        broker: NatsBroker = await app.state.dishka_container.get(NatsBroker)
        settings: Settings = await app.state.dishka_container.get(Settings)
        await create_nats_connection(broker, settings)

        yield
    finally:
        for value in app.state.values():
            if isinstance(value, ClosableProxy):
                await value.close()


def on_app_init(
    settings: Settings, *router_state: RouterState
) -> Callable[[AppConfig], AppConfig]:
    def wrapped(app_config: AppConfig) -> AppConfig:
        app_config.exception_handlers.update(setup_exception_handlers())
        app_config.middleware.extend(setup_middlewares())

        app_config.cors_config = CORSConfig(
            allow_origins=settings.server.origins,
            allow_credentials=True,
            allow_methods=list(settings.server.methods),
            allow_headers=settings.server.headers,
        )

        if settings.app.debug:
            app_config.middleware.append(LoggingMiddlewareConfig().middleware)

        for r_state in router_state:
            app_config.route_handlers.append(r_state.router)
            app_config.state.update(r_state.state.dict())
            app_config.on_startup.extend(r_state.on_startup)
            app_config.on_shutdown.extend(r_state.on_shutdown)

        return app_config

    return wrapped


def security_components() -> list[Components]:
    return [
        Components(
            security_schemes={
                "BearerToken": SecurityScheme(
                    type="http",
                    scheme="Bearer",
                    name="Authorization",
                    bearer_format="JWT",
                    description=None,
                ),
            },
        ),
    ]


def init_app(settings: Settings, *router_state: RouterState) -> Litestar:
    app = Litestar(
        path=settings.app.root_path,
        openapi_config=(
            OpenAPIConfig(
                title=settings.app.title,
                version=settings.app.version,
                components=security_components(),
                render_plugins=(SwaggerRenderPlugin(),),
            )
        )
        if settings.app.title and settings.app.swagger
        else None,
        debug=settings.app.debug,
        lifespan=[lifespan],
        stores=StoreRegistry(
            default_factory=RedisStore(
                Redis(
                    **settings.redis.model_dump(exclude_none=True),
                    decode_responses=True,
                ),
                handle_client_shutdown=True,
            ).with_namespace,
        ),
        on_app_init=[on_app_init(settings, *router_state)],
    )
    setup_dishka(container.get_container(), app)

    return app
