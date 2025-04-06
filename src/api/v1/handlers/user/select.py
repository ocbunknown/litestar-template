from dataclasses import dataclass

import uuid_utils.compat as uuid

from src.api.common.interfaces.handler import Handler
from src.common import dtos
from src.database.repositories.types.user import UserLoads
from src.services import InternalServiceGateway


class SelectUserQuery(dtos.DTO):
    loads: tuple[UserLoads, ...]
    user_uuid: uuid.UUID | None = None
    login: str | None = None


@dataclass(slots=True)
class SelectUserHandler(Handler[SelectUserQuery, dtos.User]):
    internal_gateway: InternalServiceGateway

    async def __call__(self, query: SelectUserQuery) -> dtos.User:
        async with self.internal_gateway.database.manager.session:
            return await self.internal_gateway.user.select(
                *query.loads,
                user_uuid=query.user_uuid,
                login=query.login,
            )
