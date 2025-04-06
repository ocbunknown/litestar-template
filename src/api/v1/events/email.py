import msgspec

from src.api.common.events.nats import NatsEvent, rebuild_nats_event


@rebuild_nats_event(subject="email.send")
class SendEmail[T](NatsEvent, kw_only=True):
    from_: str = msgspec.field(name="from")
    to: str
    title: str
    template: str
    props: T | None = None
