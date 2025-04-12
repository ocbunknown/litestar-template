from dataclasses import dataclass

import uuid_utils.compat as uuid

from src.api.common.interfaces.handler import Handler
from src.api.v1 import dtos
from src.api.v1.dtos.base import DTO
from src.database import DBGateway
from src.database.repositories.types.user import UserLoads
from src.database.types import OrderBy


class SelectManyUserQuery(DTO):
    loads: tuple[UserLoads, ...]
    login: str | None = None
    role_uuid: uuid.UUID | None = None
    order_by: OrderBy = "desc"
    offset: int = 0
    limit: int = 10


@dataclass(slots=True)
class SelectManyUserHandler(Handler[SelectManyUserQuery, dtos.OffsetResult[dtos.User]]):
    database: DBGateway

    async def __call__(
        self, query: SelectManyUserQuery
    ) -> dtos.OffsetResult[dtos.User]:
        async with self.database.manager.session:
            total, users = await self.database.user.select_many(
                *query.loads,
                **query.as_mapping(exclude={"loads"}),
            )

            return dtos.OffsetResult[dtos.User](
                data=[dtos.User.from_mapping(user.as_dict()) for user in users],
                offset=query.offset,
                limit=query.limit,
                total=total,
            )
