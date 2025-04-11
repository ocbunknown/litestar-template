from dataclasses import dataclass

from src.api.common.interfaces.handler import Handler
from src.common import dtos
from src.common.dtos.base import DTO
from src.common.exceptions import NotFoundError
from src.common.tools.cache import default_key_builder
from src.services import InternalServiceGateway
from src.services.cache.redis import RedisCache
from src.services.interfaces.hasher import AbstractHasher


class ConfirmRegisterQuery(DTO):
    code: str


@dataclass(slots=True)
class ConfirmRegisterHandler(Handler[ConfirmRegisterQuery, dtos.TokensExpire]):
    internal_gateway: InternalServiceGateway
    hasher: AbstractHasher
    redis: RedisCache

    async def __call__(self, query: ConfirmRegisterQuery) -> dtos.TokensExpire:
        key = default_key_builder(code=query.code)

        cached_data = await self.redis.get(key)
        if not cached_data:
            raise NotFoundError("Code has expire or invalid")

        await self.redis.delete(key)
        cache_user = dtos.Register.from_string(cached_data)

        async with self.internal_gateway:
            role = await self.internal_gateway.role.select(name="User")
            user = await self.internal_gateway.user.create(
                login=cache_user.login,
                password=self.hasher.hash_password(cache_user.password),
                role_uuid=role.uuid,
            )

        return await self.internal_gateway.auth.login(cache_user.fingerprint, user.uuid)
