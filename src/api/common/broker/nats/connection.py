from nats.aio.client import Client as NatsClient
from src.api.common.broker.nats.core import NatsBroker
from src.settings.core import Settings


async def create_nats_connection(broker: NatsBroker, settings: Settings) -> NatsClient:
    await broker.nats.connect(
        servers=settings.nats.servers,
        user=settings.nats.user,
        password=settings.nats.password,
    )
    return broker.nats
