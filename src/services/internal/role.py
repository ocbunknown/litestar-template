from dataclasses import asdict
from typing import Optional, Unpack

import uuid_utils.compat as uuid

from src.common import dtos
from src.common.exceptions import ConflictError, NotFoundError
from src.database.models.types import Roles
from src.database.repositories.role import RoleRepository
from src.database.repositories.types.role import CreateRoleType, RoleLoads
from src.database.tools import on_integrity
from src.database.types import OrderBy


class RoleService:
    __slots__ = ("_repository",)

    def __init__(self, repository: RoleRepository) -> None:
        self._repository = repository

    async def select(
        self,
        *loads: RoleLoads,
        role_uuid: Optional[uuid.UUID] = None,
        name: Optional[Roles] = None,
    ) -> dtos.Role:
        result = await self._repository.select(*loads, role_uuid=role_uuid, name=name)
        if not result:
            raise NotFoundError("Role not found")

        return dtos.Role.from_mapping(result.as_dict())

    @on_integrity("name")
    async def create(self, **data: Unpack[CreateRoleType]) -> dtos.Role:
        result = await self._repository.create(**data)

        if not result:
            raise ConflictError("This role already exists")

        return dtos.Role.from_mapping(result.as_dict())

    async def select_many(
        self,
        *loads: RoleLoads,
        name: str | None = None,
        order_by: OrderBy,
        offset: int = 0,
        limit: int = 10,
    ) -> dtos.OffsetResult[dtos.Role]:
        result = await self._repository.select_many(
            *loads,
            name=name,
            order_by=order_by,
            offset=offset,
            limit=limit,
        )

        return dtos.OffsetResult[dtos.Role].from_mapping(asdict(result))

    async def exists(self, name: str) -> bool:
        return await self._repository.exists(name)
