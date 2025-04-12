from collections.abc import Sequence
from typing import Any, Optional

import uuid_utils.compat as uuid
from litestar.connection import ASGIConnection
from litestar.datastructures import State
from litestar.handlers.base import BaseRouteHandler
from litestar.middleware import (
    AbstractAuthenticationMiddleware,
    AuthenticationResult,
)
from litestar.types import ASGIApp, Method, Scopes

from src.api.v1 import dtos
from src.common.di import Depends, FromDepends, inject
from src.common.exceptions import (
    ForbiddenError,
    ServiceNotImplementedError,
    UnAuthorizedError,
)
from src.database import DBGateway
from src.services.internal import InternalServiceGateway


class AuthenticationMiddleware(AbstractAuthenticationMiddleware):
    __slots__ = ("auth_header_name",)

    def __init__(
        self,
        app: ASGIApp,
        auth_header_name: str = "Authorization",
        exclude: str | list[str] = "schema",
        exclude_from_auth_key: str = "exclude_from_auth",
        exclude_http_methods: Sequence[Method] | None = None,
        scopes: Optional[Scopes] = None,
    ) -> None:
        super().__init__(
            app, exclude, exclude_from_auth_key, exclude_http_methods, scopes
        )
        self.auth_header_name = auth_header_name

    async def authenticate_request(
        self, connection: ASGIConnection[BaseRouteHandler, Any, Any, State]
    ) -> AuthenticationResult:
        auth_header = connection.headers.get(self.auth_header_name)
        if not auth_header:
            raise UnAuthorizedError("Authorization is required")

        access_token = auth_header.partition(" ")[-1]

        user = await self._authenticate_token(access_token)
        return AuthenticationResult(user=user, auth=None)

    @inject
    async def _authenticate_token(
        self,
        access_token: str,
        internal_gateway: Depends[InternalServiceGateway] = FromDepends(),
    ) -> dtos.User:
        user_uuid = await internal_gateway.auth.verify_token(access_token, "access")
        return await self._authenticate_user(user_uuid)

    @inject
    async def _authenticate_user(
        self,
        user_uuid: uuid.UUID,
        database: Depends[DBGateway] = FromDepends(),
    ) -> dtos.User:
        async with database.manager.session:
            user = (await database.user.select("role", user_uuid=user_uuid)).result()

        if not user.active:
            raise ForbiddenError("You have been blocked")
        if not user.role:
            raise ServiceNotImplementedError("Role not found")

        return dtos.User.from_mapping(user.as_dict())
