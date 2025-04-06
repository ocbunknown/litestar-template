from __future__ import annotations

from uuid_utils.compat import UUID

from src.common.dtos.base import DTO


class Role(DTO):
    uuid: UUID
    name: str
