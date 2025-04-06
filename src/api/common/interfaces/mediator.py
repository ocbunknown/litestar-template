from typing import Protocol, runtime_checkable

from src.common.interfaces.dto import DTO


@runtime_checkable
class Mediator(Protocol):
    async def send[Q: DTO, R: DTO](self, query: Q) -> R: ...
