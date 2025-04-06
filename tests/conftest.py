import os
from typing import (
    AsyncIterator,
    Callable,
    Iterator,
)

import alembic.command
import pytest
from alembic.config import Config as AlembicConfig
from litestar import Litestar
from litestar.testing.client import AsyncTestClient
from sqlalchemy.ext.asyncio import AsyncEngine
from testcontainers.nats import NatsContainer  # type: ignore
from testcontainers.postgres import PostgresContainer  # type: ignore
from testcontainers.redis import RedisContainer  # type: ignore

from src.api.setup import init_app
from src.api.v1.setup import init_v1_router
from src.common.interfaces.hasher import AbstractHasher
from src.common.security.argon2 import get_argon2_hasher
from src.core.settings import (
    DatabaseSettings,
    NatsSettings,
    RedisSettings,
    Settings,
    load_settings,
    path,
)
from src.database import DBGateway, create_database_factory
from src.database.core.connection import create_sa_engine, create_sa_session_factory
from src.database.core.manager import TransactionManager
from src.services.cache.redis import RedisCache, get_redis

pytestmark = pytest.mark.anyio


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
def redis(redis_config: RedisSettings) -> Iterator[RedisCache]:
    yield get_redis(redis_config)


@pytest.fixture(scope="session")
def nats_config() -> Iterator[NatsSettings]:
    nats = NatsContainer()
    if os.name == "nt":
        nats.get_container_host_ip = lambda: "127.0.0.1"

    nats.start()
    with nats:
        yield NatsSettings(
            servers=[nats.nats_uri()],
            user="",
            password="",
        )


@pytest.fixture(scope="function")
async def drop_cache(redis: RedisCache) -> None:
    await redis.clear()


@pytest.fixture(scope="session")
def db_config() -> Iterator[DatabaseSettings]:
    pg = PostgresContainer()

    if os.name == "nt":
        pg.get_container_host_ip = lambda: "127.0.0.1"

    with pg:
        yield DatabaseSettings(
            uri="postgresql+asyncpg://{}:{}@{}:{}/{}",
            name=pg.dbname,
            host=pg.get_container_host_ip(),
            port=pg.get_exposed_port(pg.port),
            user=pg.username,
            password=pg.password,
        )


@pytest.fixture(scope="session")
def redis_config() -> Iterator[RedisSettings]:
    redis = RedisContainer()

    if os.name == "nt":
        redis.get_container_host_ip = lambda: "127.0.0.1"

    with redis:
        yield RedisSettings(
            host=redis.get_container_host_ip(), port=redis.get_exposed_port(redis.port)
        )


@pytest.fixture(scope="session")
def settings(
    redis_config: RedisSettings, db_config: DatabaseSettings, nats_config: NatsSettings
) -> Settings:
    return load_settings(db=db_config, redis=redis_config, nats=nats_config)


@pytest.fixture(scope="function")
async def app(settings: Settings) -> Litestar:
    return init_app(settings, init_v1_router(settings=settings))


@pytest.fixture(scope="session")
def alembic_config(db_config: DatabaseSettings) -> AlembicConfig:
    cfg = AlembicConfig(path("alembic.ini"))

    cfg.set_main_option("sqlalchemy.url", db_config.url)

    return cfg


@pytest.fixture(scope="function", name="engine")
def connection_engine(
    db_config: DatabaseSettings, alembic_config: AlembicConfig
) -> Iterator[AsyncEngine]:
    engine = create_sa_engine(db_config.url)

    alembic.command.upgrade(alembic_config, "head")

    yield engine

    alembic.command.downgrade(alembic_config, "base")

    engine.sync_engine.dispose()


@pytest.fixture(scope="function")
def database_factory(engine: AsyncEngine) -> Callable[[], DBGateway]:
    session_factory = create_sa_session_factory(engine)
    database_factory = create_database_factory(TransactionManager, session_factory)
    return database_factory


@pytest.fixture(scope="function")
async def database(
    database_factory: Callable[[], DBGateway],
) -> AsyncIterator[DBGateway]:
    async with database_factory() as database:
        yield database


@pytest.fixture(scope="function")
async def client(app: Litestar) -> AsyncIterator[AsyncTestClient[Litestar]]:
    async with AsyncTestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
def argon() -> AbstractHasher:
    return get_argon2_hasher()
