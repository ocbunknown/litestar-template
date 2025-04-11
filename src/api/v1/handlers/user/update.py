from dataclasses import dataclass

import uuid_utils.compat as uuid

from src.api.common.interfaces.handler import Handler
from src.common import dtos
from src.services import InternalServiceGateway
from src.services.interfaces.hasher import AbstractHasher


class UpdateUserQuery(dtos.DTO):
    user_uuid: uuid.UUID
    password: str | None = None


@dataclass(slots=True)
class UpdateUserHandler(Handler[UpdateUserQuery, dtos.User]):
    internal_gateway: InternalServiceGateway
    hasher: AbstractHasher

    async def __call__(self, query: UpdateUserQuery) -> dtos.User:
        async with self.internal_gateway:
            if query.password:
                query.password = self.hasher.hash_password(query.password)

            return await self.internal_gateway.user.update(
                user_uuid=query.user_uuid,
                **query.as_mapping(exclude_none=True, exclude={"user_uuid"}),
            )
