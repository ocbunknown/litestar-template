from typing import Final, Literal

import uuid_utils.compat as uuid
from litestar.concurrency import sync_to_thread

from src.common import dtos
from src.common.di import Depends, FromDepends, inject
from src.common.exceptions import ForbiddenError
from src.common.security.jwt import JWT
from src.services.cache.redis import RedisCache

DEFAULT_TOKENS_COUNT: Final[int] = 5

TokenType = Literal["access", "refresh"]


class AuthService:
    @inject
    async def login(
        self,
        fingerprint: str,
        user_uuid: uuid.UUID,
        jwt: Depends[JWT] = FromDepends(),
        cache: Depends[RedisCache] = FromDepends(),
    ) -> dtos.TokensExpire:
        _, access = await sync_to_thread(jwt.create, typ="access", sub=str(user_uuid))
        expire, refresh = await sync_to_thread(
            jwt.create, typ="refresh", sub=str(user_uuid)
        )
        tokens = await cache.get_list(str(user_uuid))

        if len(tokens) > DEFAULT_TOKENS_COUNT:
            await cache.delete(str(user_uuid))

        await cache.set_list(str(user_uuid), f"{fingerprint}::{refresh.token}")

        return dtos.TokensExpire(
            refresh_expire=expire,
            tokens=dtos.Tokens(access=access.token, refresh=refresh.token),
        )

    @inject
    async def verify_refresh(
        self,
        body: dtos.Fingerprint,
        refresh_token: str,
        jwt: Depends[JWT] = FromDepends(),
        cache: Depends[RedisCache] = FromDepends(),
    ) -> dtos.TokensExpire:
        user_uuid = await self.verify_token(refresh_token, "refresh")
        token_pairs = await cache.get_list(str(user_uuid))
        verified = None
        for pair in token_pairs:
            data = pair.split("::")
            if len(data) < 2:
                await cache.delete(str(user_uuid))
                raise ForbiddenError(
                    "Broken separator, try to login again. Token is not valid anymore"
                )
            fp, cached_token, *_ = data
            if fp == body.fingerprint and cached_token == refresh_token:
                verified = pair
                break

        if not verified:
            await cache.delete(str(user_uuid))
            raise ForbiddenError("Token is not valid anymore")

        await cache.discard(str(user_uuid), verified)
        _, access = await sync_to_thread(jwt.create, typ="access", sub=str(user_uuid))
        expire, refresh = await sync_to_thread(
            jwt.create, typ="refresh", sub=str(user_uuid)
        )
        await cache.set_list(str(user_uuid), f"{body.fingerprint}::{refresh.token}")

        return dtos.TokensExpire(
            refresh_expire=expire,
            tokens=dtos.Tokens(access=access.token, refresh=refresh.token),
        )

    @inject
    async def invalidate_refresh(
        self,
        refresh_token: str,
        user_uuid: uuid.UUID,
        cache: Depends[RedisCache] = FromDepends(),
    ) -> dtos.Status:
        await self.verify_token(refresh_token, "refresh")
        token_pairs = await cache.get_list(str(user_uuid))
        for pair in token_pairs:
            data = pair.split("::")
            if len(data) < 2:
                await cache.delete(str(user_uuid))
                break
            _, cached_token, *_ = data
            if cached_token == refresh_token:
                await cache.discard(str(user_uuid), pair)
                break

        return dtos.Status(status=True)

    @inject
    async def verify_token(
        self,
        token: str,
        token_type: TokenType,
        jwt: Depends[JWT] = FromDepends(),
    ) -> uuid.UUID:
        payload = await sync_to_thread(jwt.verify_token, token)
        actual_token_type = payload.get("type")
        user_id = payload.get("sub")

        if actual_token_type != token_type:
            raise ForbiddenError("Invalid token")

        return uuid.UUID(user_id)
