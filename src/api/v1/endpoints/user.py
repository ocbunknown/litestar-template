from typing import Annotated

from dishka.integrations.litestar import inject
from litestar import Controller, Request, get, patch, status_codes
from litestar.datastructures import State
from litestar.middleware.rate_limit import RateLimitConfig
from litestar.params import Parameter

from src.api.common.interfaces.mediator import Mediator
from src.api.v1 import handlers
from src.common import dtos
from src.common.di import Depends
from src.database.repositories.types.user import UserLoads


class UserController(Controller):
    path = "/users"
    tags = ["Users"]
    security = [{"BearerToken": []}]

    @get("/me", status_code=status_codes.HTTP_200_OK)
    @inject
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
        request: Request[dtos.User, None, State],
        mediator: Depends[Mediator],
    ) -> dtos.User:
        return await mediator.send(
            handlers.user.SelectUserQuery(loads=s, user_uuid=request.user.uuid)
        )

    @patch(
        status_code=status_codes.HTTP_200_OK,
        middleware=[RateLimitConfig(rate_limit=("minute", 5)).middleware],
    )
    @inject
    async def update_user_endpoint(
        self,
        data: dtos.UpdateUser,
        request: Request[dtos.User, None, State],
        mediator: Depends[Mediator],
    ) -> dtos.User:
        return await mediator.send(
            handlers.user.UpdateUserQuery(
                user_uuid=request.user.uuid, **data.as_mapping()
            )
        )
