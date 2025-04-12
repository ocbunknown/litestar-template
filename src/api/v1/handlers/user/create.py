from dataclasses import dataclass
from typing import Annotated

import uuid_utils.compat as uuid
from msgspec import Meta

from src.api.common.interfaces.handler import Handler
from src.api.v1 import dtos
from src.api.v1.constants import (
    MAX_LOGIN_LENGTH,
    MAX_PASSWORD_LENGTH,
    MIN_PASSWORD_LENGTH,
)
from src.api.v1.tools.validate import validate_email
from src.database import DBGateway
from src.services.interfaces.hasher import AbstractHasher


class CreateUserQuery(dtos.DTO):
    login: Annotated[
        str,
        Meta(
            max_length=MAX_LOGIN_LENGTH,
            description=(f"Login maximum length `{MAX_LOGIN_LENGTH}`"),
        ),
    ]
    password: Annotated[
        str,
        Meta(
            min_length=MIN_PASSWORD_LENGTH,
            max_length=MAX_PASSWORD_LENGTH,
            description=(
                f"Password between `{MIN_PASSWORD_LENGTH}` and "
                f"`{MAX_PASSWORD_LENGTH}` characters long"
            ),
        ),
    ]
    role_uuid: uuid.UUID

    def __post_init__(self) -> None:
        self.login = validate_email(self.login)


@dataclass(slots=True)
class CreateUserHandler(Handler[CreateUserQuery, dtos.User]):
    database: DBGateway
    hasher: AbstractHasher

    async def __call__(self, query: CreateUserQuery) -> dtos.User:
        async with self.database:
            user = await self.database.user.create(
                login=query.login,
                password=self.hasher.hash_password(query.password),
                role_uuid=query.role_uuid,
            )

            return dtos.User.from_mapping(user.result().as_dict())
