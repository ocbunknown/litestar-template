from collections.abc import Sequence
from typing import Any, Optional, Unpack

import uuid_utils.compat as uuid
from sqlalchemy import ColumnExpressionArgument, UnaryExpression

import src.database.models as models
from src.database.exceptions import InvalidParamsError
from src.database.models.types import Roles
from src.database.repositories.base import BaseRepository
from src.database.repositories.types.role import (
    CreateRoleType,
    RoleLoads,
)
from src.database.tools import select_with_relationships
from src.database.types import OrderBy


class RoleRepository(BaseRepository[models.Role]):
    __slots__ = ()

    @property
    def model(self) -> type[models.Role]:
        return models.Role

    async def create(self, **data: Unpack[CreateRoleType]) -> Optional[models.Role]:
        return await self._crud.insert(**data)

    async def select(
        self,
        *loads: RoleLoads,
        role_uuid: Optional[uuid.UUID] = None,
        name: Optional[Roles] = None,
    ) -> Optional[models.Role]:
        if not any([role_uuid, name]):
            raise InvalidParamsError("at least one identifier must be provided")

        where_clauses: list[ColumnExpressionArgument[bool]] = []

        if role_uuid:
            where_clauses.append(self.model.uuid == role_uuid)
        if name:
            where_clauses.append(self.model.name == name)

        stmt = select_with_relationships(*loads, model=self.model).where(*where_clauses)
        return (await self._session.scalars(stmt)).unique().first()

    async def select_many(
        self,
        *loads: RoleLoads,
        name: Optional[str] = None,
        order_by: OrderBy,
        offset: int = 0,
        limit: int = 10,
    ) -> tuple[int, Sequence[models.Role]]:
        where_clauses: list[ColumnExpressionArgument[bool]] = []
        order_by_clauses: list[UnaryExpression[Any]] = []

        if name:
            where_clauses.append(self.model.name.ilike(f"%{name}%"))
        if order_by:
            order_by_clauses.append(getattr(self.model.created_at, order_by)())

        total = await self._crud.count(*where_clauses)
        if total <= 0:
            return total, []

        stmt = (
            select_with_relationships(*loads, model=self.model)
            .where(*where_clauses)
            .order_by(*order_by_clauses)
            .limit(limit)
            .offset(offset)
        )

        results = (await self._session.scalars(stmt)).unique().all()
        return total, results

    async def exists(self, name: str) -> bool:
        return await self._crud.exists(self.model.name == name)
