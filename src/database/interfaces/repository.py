from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Repository(Protocol):
    model: type[Any]
