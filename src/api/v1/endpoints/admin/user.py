from typing import Annotated

import uuid_utils.compat as uuid
from dishka.integrations.litestar import inject
from litestar import Controller, get, patch, post, status_codes
from litestar.params import Parameter

from src.api.common.interfaces.mediator import Mediator
from src.api.v1 import handlers
from src.api.v1.permission import Permission
from src.common import dtos
from src.common.di import Depends
from src.database.repositories.types.user import UserLoads


class UserController(Controller):
    path = "/users"
    tags = ["Admin | Users"]
    guards = [Permission("Admin")]
    security = [{"BearerToken": []}]

    @post(status_code=status_codes.HTTP_201_CREATED)
    @inject
    async def create_user_endpoint(
        self,
        data: handlers.user.CreateUserQuery,
        mediator: Depends[Mediator],
    ) -> dtos.User:
        return await mediator.send(data)

    @get("/{user_id:uuid}", status_code=status_codes.HTTP_200_OK)
    @inject
    async def select_user_endpoint(
        self,
        s: Annotated[
            tuple[UserLoads, ...],
            Parameter(
                required=False,
                default=(),
                description="Search for additional user relation",
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
    @inject
    async def update_user_endpoint(
        self,
        data: dtos.UpdateUser,
        user_id: uuid.UUID,
        mediator: Depends[Mediator],
    ) -> dtos.User:
        return await mediator.send(
            handlers.user.UpdateUserQuery(user_uuid=user_id, **data.as_mapping())
        )
