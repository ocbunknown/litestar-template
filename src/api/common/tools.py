import inspect
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any

from litestar import Router
from litestar.datastructures import State
from litestar.types import LifespanHook


class ClosableProxy:
    __slots__ = (
        "_target",
        "_close_fn",
    )

    def __init__(self, target: Any, close_fn: Callable[[], Any]) -> None:
        self._target = target
        self._close_fn = close_fn

    async def close(self) -> None:
        if inspect.isawaitable(self._close_fn) or inspect.iscoroutinefunction(
            self._close_fn
        ):
            await self._close_fn()
        else:
            self._close_fn()

    def __getattr__(self, key: str) -> Any:
        return getattr(self._target, key)

    def __repr__(self) -> str:
        return f"{self._target!r}"


@dataclass(frozen=True)
class RouterState:
    router: Router
    state: State
    on_startup: Sequence[LifespanHook] = field(default_factory=list)
    on_shutdown: Sequence[LifespanHook] = field(default_factory=list)
