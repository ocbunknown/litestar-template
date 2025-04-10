from typing import Annotated

import uuid_utils.compat as uuid
from litestar import Controller, get, patch, post, status_codes
from litestar.params import Parameter

from src.api.common.interfaces.mediator import Mediator
from src.api.v1 import handlers
from src.api.v1.constants import MAX_PAGINATION_LIMIT, MIN_PAGINATION_LIMIT
from src.api.v1.permission import Permission
from src.common import dtos
from src.common.di import Depends
from src.database.repositories.types.user import UserLoads
from src.database.types import OrderBy


class UserController(Controller):
    path = "/users"
    tags = ["Admin | Users"]
    guards = [Permission("Admin")]
    security = [{"BearerToken": []}]

    @post(status_code=status_codes.HTTP_201_CREATED)
    async def create_user_endpoint(
        self,
        data: handlers.user.CreateUserQuery,
        mediator: Depends[Mediator],
    ) -> dtos.User:
        return await mediator.send(data)

    @get("/{user_id:uuid}", status_code=status_codes.HTTP_200_OK)
    async def select_user_endpoint(
        self,
        s: Annotated[
            tuple[UserLoads, ...],
            Parameter(
                required=False,
                default=(),
                description="Search for additional relations",
            ),
        ],
        user_id: uuid.UUID,
        login: Annotated[str | None, Parameter(default=None, required=False)],
        mediator: Depends[Mediator],
    ) -> dtos.User:
        return await mediator.send(
            handlers.user.SelectUserQuery(loads=s, user_uuid=user_id, login=login)
        )

    @patch("/{user_id:uuid}", status_code=status_codes.HTTP_200_OK)
    async def update_user_endpoint(
        self,
        user_id: uuid.UUID,
        data: dtos.UpdateUser,
        mediator: Depends[Mediator],
    ) -> dtos.User:
        return await mediator.send(
            handlers.user.UpdateUserQuery(user_uuid=user_id, **data.as_mapping())
        )

    @get(status_code=status_codes.HTTP_200_OK)
    async def select_users_endpoint(
        self,
        s: Annotated[
            tuple[UserLoads, ...],
            Parameter(
                required=False,
                default=(),
                description="Search for additional relations",
            ),
        ],
        login: Annotated[str | None, Parameter(default=None, required=False)],
        role_uuid: Annotated[uuid.UUID | None, Parameter(default=None, required=False)],
        order_by: Annotated[OrderBy, Parameter(default="desc", required=False)],
        offset: Annotated[int, Parameter(default=0)],
        limit: Annotated[
            int,
            Parameter(
                default=MIN_PAGINATION_LIMIT,
                ge=MIN_PAGINATION_LIMIT,
                le=MAX_PAGINATION_LIMIT,
                required=False,
            ),
        ],
        mediator: Depends[Mediator],
    ) -> dtos.OffsetResult[dtos.User]:
        return await mediator.send(
            handlers.user.SelectManyUserQuery(
                loads=s,
                login=login,
                role_uuid=role_uuid,
                order_by=order_by,
                offset=offset,
                limit=limit,
            )
        )
