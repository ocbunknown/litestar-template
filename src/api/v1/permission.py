from litestar.connection import ASGIConnection
from litestar.datastructures.state import State
from litestar.handlers.base import BaseRouteHandler

from src.api.v1 import dtos
from src.common.exceptions import UnAuthorizedError
from src.database.models.types import Roles


class Permission:
    __slots__ = ("roles",)

    def __init__(self, *roles: Roles) -> None:
        self.roles = roles

    async def __call__(
        self,
        connection: ASGIConnection[BaseRouteHandler, dtos.User, None, State],
        _: BaseRouteHandler,
    ) -> None:
        valid_roles = self._ensure_valid_roles(connection.user)
        if not valid_roles:
            raise UnAuthorizedError("Not allowed")

        return

    def _ensure_valid_roles(self, user: dtos.User) -> bool:
        assert user.role is not None
        return any(role in user.role.name for role in self.roles)
