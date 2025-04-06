from typing import Any, Optional, Unpack

import uuid_utils.compat as uuid
from sqlalchemy import ColumnExpressionArgument, UnaryExpression

import src.database.models as models
from src.database.exceptions import InvalidParamsError
from src.database.repositories.base import BaseRepository
from src.database.repositories.types.user import (
    CreateUserType,
    UpdateUserType,
    UserLoads,
)
from src.database.tools import select_with_relationships
from src.database.types import OffsetPaginationResult, OrderBy


class UserRepository(BaseRepository[models.User]):
    __slots__ = ()

    @property
    def model(self) -> type[models.User]:
        return models.User

    async def create(self, **data: Unpack[CreateUserType]) -> Optional[models.User]:
        return await self._crud.insert(**data)

    async def select(
        self,
        *loads: UserLoads,
        user_uuid: Optional[uuid.UUID] = None,
        login: Optional[str] = None,
    ) -> Optional[models.User]:
        if not any([user_uuid, login]):
            raise InvalidParamsError("at least one identifier must be provided")

        where_clauses: list[ColumnExpressionArgument[bool]] = []

        if user_uuid:
            where_clauses.append(self.model.uuid == user_uuid)
        if login:
            where_clauses.append(self.model.login == login)

        stmt = select_with_relationships(*loads, model=self.model).where(*where_clauses)
        return (await self._session.scalars(stmt)).unique().first()

    async def update(
        self,
        uuid: uuid.UUID,
        /,
        **data: Unpack[UpdateUserType],
    ) -> Optional[models.User]:
        if not any([uuid]):
            raise InvalidParamsError("at least one identifier must be provided")

        result = await self._crud.update(self.model.uuid == uuid, **data)
        return result[0] if result else None

    async def delete(
        self, user_uuid: Optional[uuid.UUID] = None, login: Optional[str] = None
    ) -> Optional[models.User]:
        if not any([user_uuid, login]):
            raise InvalidParamsError("at least one identifier must be provided")

        where_clauses: list[ColumnExpressionArgument[bool]] = []

        if user_uuid:
            where_clauses.append(self.model.uuid == user_uuid)
        if login:
            where_clauses.append(self.model.login == login)

        result = await self._crud.delete(*where_clauses)
        return result[0] if result else None

    async def select_many(
        self,
        *loads: UserLoads,
        login: Optional[str] = None,
        role_uuid: Optional[uuid.UUID] = None,
        order_by: OrderBy,
        offset: int = 0,
        limit: int = 10,
    ) -> OffsetPaginationResult[models.User]:
        where_clauses: list[ColumnExpressionArgument[bool]] = []
        order_by_clauses: list[UnaryExpression[Any]] = []

        if login:
            where_clauses.append(
                self.model.login.ilike(f"%{login}%")
                | self.model.login.ilike(f"%{login}%")
            )
        if role_uuid:
            where_clauses.append(self.model.role_uuid == role_uuid)
        if order_by:
            order_by_clauses.append(getattr(self.model.created_at, order_by)())

        count = await self._crud.count(*where_clauses)
        if count <= 0:
            return OffsetPaginationResult(data=[], limit=limit, offset=offset, total=0)

        stmt = (
            select_with_relationships(*loads, model=self.model)
            .where(*where_clauses)
            .order_by(*order_by_clauses)
            .limit(limit)
            .offset(offset)
        )

        users = (await self._session.scalars(stmt)).unique().all()
        return OffsetPaginationResult(
            data=users, limit=limit, offset=offset, total=count
        )

    async def exists(self, login: str) -> bool:
        return await self._crud.exists(self.model.login == login)
