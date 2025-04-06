from dataclasses import dataclass

import uuid_utils.compat as uuid

from src.api.common.interfaces.handler import Handler
from src.common import dtos
from src.common.interfaces.hasher import AbstractHasher
from src.services import InternalServiceGateway


class CreateUserQuery(dtos.DTO):
    login: str
    password: str
    role_uuid: uuid.UUID


@dataclass(slots=True)
class CreateUserHandler(Handler[CreateUserQuery, dtos.User]):
    internal_gateway: InternalServiceGateway
    hasher: AbstractHasher

    async def __call__(self, query: CreateUserQuery) -> dtos.User:
        async with self.internal_gateway:
            return await self.internal_gateway.user.create(
                login=query.login,
                password=self.hasher.hash_password(query.password),
                role_uuid=query.role_uuid,
            )
