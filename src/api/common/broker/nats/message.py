from dataclasses import dataclass
from typing import Any

from src.api.common.interfaces.broker import BrokerMessage


@dataclass
class NatsMessage(BrokerMessage):
    subject: str = ""
    payload: bytes = b""
    reply: str = ""
    headers: dict[str, Any] | None = None


@dataclass
class NatsJetStreamMessage(BrokerMessage):
    subject: str = ""
    payload: bytes = b""
    timeout: float | None = None
    stream: str | None = None
    headers: dict[str, Any] | None = None
