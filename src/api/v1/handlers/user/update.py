from dataclasses import dataclass

import uuid_utils.compat as uuid

from src.api.common.interfaces.handler import Handler
from src.api.v1 import dtos
from src.api.v1.dtos.base import DTO
from src.database import DBGateway
from src.services.interfaces.hasher import AbstractHasher


class UpdateUserQuery(DTO):
    user_uuid: uuid.UUID
    password: str | None = None


@dataclass(slots=True)
class UpdateUserHandler(Handler[UpdateUserQuery, dtos.User]):
    database: DBGateway
    hasher: AbstractHasher

    async def __call__(self, query: UpdateUserQuery) -> dtos.User:
        async with self.database:
            if query.password:
                query.password = self.hasher.hash_password(query.password)

            user = await self.database.user.update(
                query.user_uuid,
                **query.as_mapping(exclude_none=True, exclude={"user_uuid"}),
            )

            return dtos.User.from_mapping(user.result().as_dict())
