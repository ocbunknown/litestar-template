from typing import Annotated

from msgspec import Meta
from uuid_utils.compat import UUID

from src.api.v1.constants import MAX_PASSWORD_LENGTH, MIN_PASSWORD_LENGTH
from src.common.dtos.base import DTO
from src.common.dtos.role import Role


class User(DTO):
    uuid: UUID
    login: str
    active: bool

    # relations
    role: Role | None = None


class UpdateUser(DTO):
    password: (
        Annotated[
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
        | None
    ) = None
