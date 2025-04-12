from __future__ import annotations

from uuid_utils.compat import UUID

from src.api.v1.dtos.base import DTO


class Role(DTO):
    uuid: UUID
    name: str
