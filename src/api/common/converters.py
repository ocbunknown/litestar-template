from __future__ import annotations

import uuid
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Any

import msgspec
from litestar.serialization.msgspec_hooks import (
    default_deserializer,
    default_serializer,
)


def convert_to[T](cls: type[T], value: Any, **kw: Any) -> T:
    return msgspec.convert(
        value,
        cls,
        dec_hook=default_deserializer,
        builtin_types=(
            bytes,
            bytearray,
            datetime,
            time,
            date,
            timedelta,
            uuid.UUID,
            Decimal,
        ),
        **kw,
    )


def convert_from(value: Any, **kw: Any) -> Any:
    return msgspec.to_builtins(
        value,
        enc_hook=default_serializer,
        builtin_types=(
            datetime,
            date,
            timedelta,
            Decimal,
            uuid.UUID,
            bytes,
            bytearray,
            memoryview,
            time,
        ),
        **kw,
    )
