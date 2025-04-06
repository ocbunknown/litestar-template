import abc
from typing import Any

from src.common.interfaces.dto import DTO


class Handler[Q: DTO, R: DTO](abc.ABC):
    __slots__ = ()

    @abc.abstractmethod
    async def __call__(self, query: Q) -> R: ...


type HandlerType = Handler[Any, Any]
