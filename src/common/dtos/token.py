from __future__ import annotations

from datetime import datetime

from src.common.dtos.base import DTO


class Token(DTO):
    token: str


class Tokens(DTO):
    access: str
    refresh: str


class TokensExpire(DTO):
    refresh_expire: datetime
    tokens: Tokens
