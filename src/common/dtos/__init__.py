from __future__ import annotations

import re

from .auth import Fingerprint, Login, Register, VerificationCode
from .base import DTO
from .role import Role
from .status import Status
from .token import Token, Tokens, TokensExpire
from .user import UpdateUser, User

__all__ = (
    "DTO",
    "User",
    "Register",
    "Tokens",
    "Token",
    "TokensExpire",
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


EMAIL_REGEX = re.compile(r"^[^@]+@[^@]+\.[^@]+$")


class EmailStr(str):
    def __new__(cls, value: str) -> EmailStr:
        if not EMAIL_REGEX.fullmatch(value):
            raise ValueError(f"Invalid email: {value}")
        return super().__new__(cls, value)
