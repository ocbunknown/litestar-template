from litestar.datastructures import MutableScopeHeaders
from litestar.enums import ScopeType
from litestar.middleware import ASGIMiddleware
from litestar.types import ASGIApp, Message, Receive, Scope, Send
from uuid_utils.compat import uuid4


class XRequestIdMiddleware(ASGIMiddleware):
    scopes = (ScopeType.HTTP,)

    def __init__(self, header_name: str = "X-Request-Id") -> None:
        self.header_name = header_name

    async def handle(
        self, scope: Scope, receive: Receive, send: Send, next_app: ASGIApp
    ) -> None:
        request_id = uuid4().hex
        scope["state"]["request_id"] = request_id

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableScopeHeaders.from_message(message=message)
                headers[self.header_name] = request_id

            await send(message)

        await next_app(scope, receive, send_wrapper)
