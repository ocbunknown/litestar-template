from collections.abc import Mapping
from datetime import datetime
from typing import Any

import msgspec
from uuid_utils.compat import UUID, uuid4

from src.api.common.converters import convert_from
from src.api.common.serializers.msgspec import msgpack_encoder


class Event(msgspec.Struct, kw_only=True):
    event_id: UUID = msgspec.field(default_factory=uuid4)
    event_timestamp: float = msgspec.field(default_factory=datetime.now().timestamp)

    def as_mapping(
        self, exclude_none: bool = False, exclude: set[str] | None = None
    ) -> Mapping[str, Any]:
        result: dict[str, Any] = convert_from(self)
        if exclude_none:
            result = {k: v for k, v in result.items() if v is not None}
        if exclude:
            result = {k: v for k, v in result.items() if k not in exclude}

        return result

    def as_bytes(
        self, exclude_none: bool = False, exclude: set[str] | None = None
    ) -> bytes:
        return msgpack_encoder(
            self.as_mapping(exclude_none=exclude_none, exclude=exclude)
            if exclude_none or exclude
            else self
        )
