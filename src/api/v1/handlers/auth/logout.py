from dataclasses import dataclass

import uuid_utils.compat as uuid

from src.api.common.interfaces.handler import Handler
from src.common import dtos
from src.common.dtos.base import DTO
from src.common.exceptions import UnAuthorizedError
from src.services import InternalServiceGateway


class LogoutQuery(DTO):
    user_uuid: uuid.UUID
    refresh_token: str


@dataclass(slots=True)
class LogoutHandler(Handler[LogoutQuery, dtos.Status]):
    internal_gateway: InternalServiceGateway

    async def __call__(self, query: LogoutQuery) -> dtos.Status:
        if not (refresh_token := query.refresh_token):
            raise UnAuthorizedError("Not allowed")

        return await self.internal_gateway.auth.invalidate_refresh(
            refresh_token, query.user_uuid
        )
