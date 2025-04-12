import abc
from typing import Any

from src.api.common.interfaces.dto import DTO


class Handler[Q: DTO, R](abc.ABC):
    __slots__ = ()

    @abc.abstractmethod
    async def __call__(self, query: Q) -> R: ...


type HandlerType = Handler[Any, Any]
