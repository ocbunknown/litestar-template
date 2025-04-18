from dataclasses import dataclass
from typing import Annotated

from msgspec import Meta

from src.api.common.interfaces.handler import Handler
from src.api.v1.constants import (
    MAX_LOGIN_LENGTH,
    MAX_PASSWORD_LENGTH,
    MIN_PASSWORD_LENGTH,
)
from src.api.v1.dtos.base import DTO
from src.api.v1.tools.validate import validate_email
from src.common.exceptions import (
    ForbiddenError,
    UnAuthorizedError,
)
from src.database import DBGateway
from src.services import InternalServiceGateway
from src.services.interfaces.hasher import AbstractHasher
from src.services.internal.auth import TokensExpire


class LoginQuery(DTO):
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
    fingerprint: str

    def __post_init__(self) -> None:
        self.login = validate_email(self.login)


@dataclass(slots=True)
class LoginHandler(Handler[LoginQuery, TokensExpire]):
    internal_gateway: InternalServiceGateway
    database: DBGateway
    hasher: AbstractHasher

    async def __call__(self, query: LoginQuery) -> TokensExpire:
        async with self.database.manager.session:
            user = (await self.database.user.select(login=query.login)).result()

        if not user.active:
            raise ForbiddenError("You have been blocked")
        if not self.hasher.verify_password(user.password, query.password):
            raise UnAuthorizedError("Incorrect password or login")

        return await self.internal_gateway.auth.login(query.fingerprint, user.uuid)
