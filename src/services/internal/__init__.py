from typing import Any, Callable

from src.common.interfaces.gateway import BaseGateway
from src.database import DBGateway

from .auth import AuthService
from .role import RoleService
from .user import UserService


class InternalServiceGateway(BaseGateway):
    __slots__ = ("database", "_cache")

    def __init__(self, database: DBGateway) -> None:
        super().__init__(database)
        self.database = database
        self._cache: dict[str, Any] = {}

    @property
    def user(self) -> UserService:
        return self._from_cache("user", UserService)

    @property
    def role(self) -> RoleService:
        return self._from_cache("role", RoleService)

    @property
    def auth(self) -> AuthService:
        return AuthService()

    def _from_cache[S](self, key: str, factory: Callable[..., S], **kwargs: Any) -> S:
        if not (cached := self._cache.get(key)):
            cached = factory(getattr(self.database, key), **kwargs)
            self._cache[key] = cached

        return cached


__all__ = ("InternalServiceGateway",)
