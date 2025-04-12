from .auth import Fingerprint, Login, Register, VerificationCode
from .base import DTO
from .role import Role
from .status import Status
from .user import UpdateUser, User

__all__ = (
    "DTO",
    "User",
    "Register",
    "Fingerprint",
    "Login",
    "Role",
    "Status",
    "VerificationCode",
    "UpdateUser",
)


class OffsetResult[T](DTO):
    data: list[T]
    offset: int
    limit: int
    total: int
