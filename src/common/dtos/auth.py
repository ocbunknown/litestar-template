from __future__ import annotations

from src.common.dtos.base import DTO


class Fingerprint(DTO):
    fingerprint: str


class Login(Fingerprint):
    login: str
    password: str


class Register(Fingerprint):
    login: str
    password: str


class VerificationCode(DTO):
    code: str
