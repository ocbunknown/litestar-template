from typing import Optional, Unpack

import uuid_utils.compat as uuid

from src.common import dtos
from src.common.exceptions import ConflictError, NotFoundError
from src.database.repositories.types.user import (
    CreateUserType,
    UpdateUserType,
    UserLoads,
)
from src.database.repositories.user import UserRepository
from src.database.tools import on_integrity
from src.database.types import OrderBy


class UserService:
    __slots__ = ("_repository",)

    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def select(
        self,
        *loads: UserLoads,
        user_uuid: Optional[uuid.UUID] = None,
        login: Optional[str] = None,
    ) -> dtos.User:
        result = await self._repository.select(*loads, user_uuid=user_uuid, login=login)
        if not result:
            raise NotFoundError("User not found")

        return dtos.User.from_mapping(result.as_dict())

    @on_integrity("login")
    async def create(self, **data: Unpack[CreateUserType]) -> dtos.User:
        result = await self._repository.create(**data)

        if not result:
            raise ConflictError("This user already exists")

        return dtos.User.from_mapping(result.as_dict())

    @on_integrity("login")
    async def update(
        self,
        user_uuid: uuid.UUID,
        **data: Unpack[UpdateUserType],
    ) -> dtos.User:
        result = await self._repository.update(user_uuid, **data)

        if not result:
            raise ConflictError("Cannot update user")

        return dtos.User.from_mapping(result.as_dict())

    async def delete(
        self, login: Optional[str] = None, user_uuid: Optional[uuid.UUID] = None
    ) -> dtos.User:
        result = await self._repository.delete(login=login, user_uuid=user_uuid)

        if not result:
            raise ConflictError("Cannot delete user")

        return dtos.User.from_mapping(result.as_dict())

    async def select_many(
        self,
        *loads: UserLoads,
        login: str | None = None,
        role_uuid: uuid.UUID | None = None,
        order_by: OrderBy = "desc",
        offset: int = 0,
        limit: int = 10,
    ) -> dtos.OffsetResult[dtos.User]:
        total, results = await self._repository.select_many(
            *loads,
            login=login,
            role_uuid=role_uuid,
            order_by=order_by,
            offset=offset,
            limit=limit,
        )
        return dtos.OffsetResult[dtos.User](
            data=[dtos.User.from_mapping(result.as_dict()) for result in results],
            limit=limit,
            offset=offset,
            total=total,
        )

    async def exists(self, login: str) -> bool:
        return await self._repository.exists(login)
