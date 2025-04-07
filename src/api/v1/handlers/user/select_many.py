from dataclasses import dataclass

import uuid_utils.compat as uuid

from src.api.common.interfaces.handler import Handler
from src.common import dtos
from src.database.repositories.types.user import UserLoads
from src.database.types import OrderBy
from src.services import InternalServiceGateway


class SelectManyUserQuery(dtos.DTO):
    loads: tuple[UserLoads, ...]
    login: str | None = None
    role_uuid: uuid.UUID | None = None
    order_by: OrderBy = "desc"
    offset: int = 0
    limit: int = 10


@dataclass(slots=True)
class SelectManyUserHandler(Handler[SelectManyUserQuery, dtos.OffsetResult[dtos.User]]):
    internal_gateway: InternalServiceGateway

    async def __call__(
        self, query: SelectManyUserQuery
    ) -> dtos.OffsetResult[dtos.User]:
        async with self.internal_gateway.database.manager.session:
            return await self.internal_gateway.user.select_many(
                *query.loads,
                **query.as_mapping(exclude={"loads"}),
            )
