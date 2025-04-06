from dishka import Provider, Scope
from dishka.integrations.litestar import LitestarProvider
from litestar.datastructures import State

from nats.aio.client import Client as NatsClient
from src.api.common import tools
from src.api.common.broker.nats.core import NatsBroker, NatsJetStreamBroker
from src.api.common.bus.core import EventBusImpl
from src.api.common.interfaces.event_bus import EventBus
from src.api.common.interfaces.mediator import Mediator
from src.api.common.mediator import MediatorImpl
from src.api.v1.handlers import setup_handlers
from src.common.di import container
from src.common.interfaces.hasher import AbstractHasher
from src.common.security.argon2 import get_argon2_hasher
from src.common.security.jwt import JWT
from src.common.serializers.msgspec import msgspec_decoder, msgspec_encoder
from src.common.tools.singleton import singleton
from src.core.settings import Settings
from src.database import create_database_factory
from src.database.core.connection import create_sa_engine, create_sa_session_factory
from src.database.core.manager import TransactionManager
from src.services import ServiceGateway
from src.services.cache.redis import RedisCache, get_redis
from src.services.external import ExternalServiceGateway
from src.services.internal import InternalServiceGateway
from src.services.provider.aiohttp import AiohttpProvider
from src.services.provider.base import AsyncProvider


def setup_dependencies(settings: Settings) -> State:
    redis = get_redis(settings.redis)

    engine = create_sa_engine(
        settings.db.url,
        pool_size=settings.db.connection_pool_size,
        max_overflow=settings.db.connection_max_overflow,
        pool_pre_ping=settings.db.connection_pool_pre_ping,
        json_serializer=msgspec_encoder,
        json_deserializer=msgspec_decoder,
    )

    session_factory = create_sa_session_factory(engine)
    database_factory = create_database_factory(TransactionManager, session_factory)

    hasher = get_argon2_hasher()
    jwt = JWT(settings.ciphers)

    aiohttp_provider = AiohttpProvider()
    service_gateway = ServiceGateway(
        database_factory=database_factory,
        provider=aiohttp_provider,
        settings=settings,
    )

    nats_broker = NatsBroker(NatsClient())
    jetstream_broker = NatsJetStreamBroker(nats_broker.nats.jetstream())

    event_bus = (
        EventBusImpl.builder()
        .brokers(nats_broker, jetstream_broker)
        .middleware()
        .build()
    )

    mediator = (
        MediatorImpl.builder()
        .dependencies(
            hasher=hasher,
            redis=redis,
            jwt=jwt,
            settings=settings,
            event_bus=event_bus,
            external_gateway=service_gateway.external,
            internal_gateway=service_gateway.internal,
        )
        .handlers(setup_handlers)
        .middleware()
        .build()
    )

    provider = Provider(scope=Scope.APP)
    provider.provide(singleton(nats_broker), provides=NatsBroker)
    provider.provide(singleton(jetstream_broker), provides=NatsJetStreamBroker)
    provider.provide(singleton(event_bus), provides=EventBus)
    provider.provide(singleton(mediator), provides=Mediator)
    provider.provide(singleton(settings), provides=Settings)
    provider.provide(singleton(redis), provides=RedisCache)
    provider.provide(singleton(aiohttp_provider), provides=AsyncProvider)
    provider.provide(singleton(jwt), provides=JWT)
    provider.provide(singleton(hasher), provides=AbstractHasher)
    provider.provide(
        singleton(service_gateway.internal), provides=InternalServiceGateway
    )
    provider.provide(
        singleton(service_gateway.external), provides=ExternalServiceGateway
    )

    container.add_providers(provider, LitestarProvider())

    return State(
        {
            "container": tools.ClosableProxy(
                container.get_container(), container.get_container().close
            ),
            "nats": tools.ClosableProxy(nats_broker.nats, nats_broker.nats.drain),
            "engine": tools.ClosableProxy(engine, engine.dispose),
            "redis": tools.ClosableProxy(redis, redis.close),
            "aiohttp_provider": tools.ClosableProxy(
                aiohttp_provider, aiohttp_provider.close_session
            ),
        }
    )
