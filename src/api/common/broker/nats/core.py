from nats.aio.client import Client as NatsClient
from nats.js import JetStreamContext
from src.api.common.broker.nats.message import NatsJetStreamMessage, NatsMessage
from src.api.common.events.nats import NatsEvent, NatsJetStreamEvent
from src.api.common.interfaces.broker import Broker


class NatsBroker(Broker[NatsEvent, NatsMessage]):
    def __init__(self, nats: NatsClient) -> None:
        self.nats = nats

    async def publish(self, message: NatsMessage) -> None:
        await self.nats.publish(
            subject=message.subject,
            payload=message.payload,
            reply=message.reply,
            headers=message.headers,
        )

    def _build_message(self, event: NatsEvent) -> NatsMessage:
        return NatsMessage(
            subject=event.subject,
            payload=event.as_bytes(
                exclude={
                    "subject",
                    "_reply",
                    "_headers",
                },
            ),
            reply=event._reply,
            headers=event._headers or {},
        )


class NatsJetStreamBroker(Broker[NatsJetStreamEvent, NatsJetStreamMessage]):
    def __init__(self, jetstream: JetStreamContext) -> None:
        self.js = jetstream

    async def publish(self, message: NatsJetStreamMessage) -> None:
        await self.js.publish(
            subject=message.subject,
            payload=message.payload,
            stream=message.stream,
            timeout=message.timeout,
            headers=message.headers,
        )

    def _build_message(self, event: NatsJetStreamEvent) -> NatsJetStreamMessage:
        return NatsJetStreamMessage(
            subject=event.subject,
            payload=event.as_bytes(
                exclude={
                    "subject",
                    "_reply",
                    "_headers",
                    "_stream",
                    "_timeout",
                },
            ),
            stream=event._stream,
            timeout=event._timeout,
            headers=event._headers or {},
        )
