from dataclasses import dataclass

from src.api.common.interfaces.handler import Handler
from src.common import dtos
from src.common.dtos.base import DTO
from src.common.exceptions import UnAuthorizedError
from src.services import InternalServiceGateway


class RefreshTokenQuery(DTO):
    data: dtos.Fingerprint
    refresh_token: str


@dataclass(slots=True)
class RefreshTokenHandler(Handler[RefreshTokenQuery, dtos.TokensExpire]):
    internal_gateway: InternalServiceGateway

    async def __call__(self, query: RefreshTokenQuery) -> dtos.TokensExpire:
        if not (refresh_token := query.refresh_token):
            raise UnAuthorizedError("Not allowed")

        return await self.internal_gateway.auth.verify_refresh(
            query.data, refresh_token
        )
