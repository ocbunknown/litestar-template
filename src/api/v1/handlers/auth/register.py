import secrets
from dataclasses import dataclass
from datetime import timedelta
from typing import Annotated

from msgspec import Meta

from src.api.common.interfaces.event_bus import EventBus
from src.api.common.interfaces.handler import Handler
from src.api.v1.constants import (
    MAX_LOGIN_LENGTH,
    MAX_PASSWORD_LENGTH,
    MIN_PASSWORD_LENGTH,
)
from src.api.v1.events.email import SendEmail
from src.api.v1.tools.validate import validate_email
from src.common import dtos
from src.common.exceptions import (
    ConflictError,
)
from src.common.tools.cache import default_key_builder
from src.services import InternalServiceGateway
from src.services.cache.redis import RedisCache


class RegisterQuery(dtos.DTO):
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
class RegisterHandler(Handler[RegisterQuery, dtos.Status]):
    internal_gateway: InternalServiceGateway
    event_bus: EventBus
    redis: RedisCache

    async def __call__(self, query: RegisterQuery) -> dtos.Status:
        async with self.internal_gateway.database.manager.session:
            user_exists = await self.internal_gateway.user.exists(login=query.login)

        if user_exists:
            raise ConflictError("User already exists")

        code = secrets.token_hex(16)

        await self.redis.set(
            default_key_builder(code=code),
            query.as_string(),
            expire=timedelta(minutes=10),
        )

        await self.event_bus.publish(
            SendEmail[dtos.VerificationCode](
                from_="your-email@example.com",
                to=query.login,
                title="OcbUnknown Template",
                template="verify_email",
                props=dtos.VerificationCode(code=code),
            )
        )

        return dtos.Status(status=True)
