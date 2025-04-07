from uuid_utils.compat import UUID

from src.common.dtos.base import DTO
from src.common.dtos.role import Role


class User(DTO):
    uuid: UUID
    login: str
    active: bool

    # relations
    role: Role | None = None


class UpdateUser(DTO):
    password: str | None = None
