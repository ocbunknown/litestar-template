from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self

import msgspec

from src.api.common.converters import convert_from, convert_to
from src.api.common.serializers.msgspec import (
    msgpack_decoder,
    msgpack_encoder,
    msgspec_decoder,
    msgspec_encoder,
)


class DTO(msgspec.Struct):
    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> Self:
        return convert_to(cls, value, strict=False)

    @classmethod
    def from_string(cls, value: str) -> Self:
        return convert_to(cls, msgspec_decoder(value, strict=False), strict=False)

    @classmethod
    def from_attributes(cls, value: Any) -> Self:
        return convert_to(cls, value, strict=False, from_attributes=True)

    @classmethod
    def from_bytes(cls, value: bytes) -> Self:
        return convert_to(cls, msgpack_decoder(value, strict=False), strict=False)

    def as_mapping(
        self, exclude_none: bool = False, exclude: set[str] | None = None
    ) -> Mapping[str, Any]:
        result: dict[str, Any] = convert_from(self)
        if exclude_none:
            result = {k: v for k, v in result.items() if v is not None}
        if exclude:
            result = {k: v for k, v in result.items() if k not in exclude}

        return result

    def as_string(
        self, exclude_none: bool = False, exclude: set[str] | None = None
    ) -> str:
        return msgspec_encoder(
            self.as_mapping(exclude_none=exclude_none, exclude=exclude)
            if exclude_none or exclude
            else self
        )

    def as_bytes(
        self, exclude_none: bool = False, exclude: set[str] | None = None
    ) -> bytes:
        return msgpack_encoder(
            self.as_mapping(exclude_none=exclude_none, exclude=exclude)
            if exclude_none or exclude
            else self
        )

    def copy(self, update: Mapping[str, Any] | None = None) -> Self:
        return type(self)(**{**self.as_mapping(), **(update or {})})


class StrictDTO(msgspec.Struct):
    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> Self:
        return convert_to(cls, value, strict=True)

    @classmethod
    def from_string(cls, value: str) -> Self:
        return convert_to(cls, msgspec_decoder(value, strict=True), strict=True)

    @classmethod
    def from_attributes(cls, value: Any) -> Self:
        return convert_to(cls, value, strict=True, from_attributes=True)

    @classmethod
    def from_bytes(cls, value: bytes) -> Self:
        return convert_to(cls, msgpack_decoder(value, strict=True), strict=True)
