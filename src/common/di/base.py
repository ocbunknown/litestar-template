from typing import Any, Callable

from dishka import AsyncContainer
from dishka.integrations.base import wrap_injection

from src.common.di.container import container


def inject[T, **P](func: Callable[P, T]) -> Callable[P, T]:
    def container_getter(*args: Any, **kwargs: Any) -> AsyncContainer:
        return container.get_container()

    return wrap_injection(
        func=func,
        container_getter=container_getter,
        is_async=True,
    )
