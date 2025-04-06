from dishka import AsyncContainer, Provider, make_async_container


class DynamicContainer:
    __slots__ = ("_container",)

    def __init__(self) -> None:
        self._container: AsyncContainer | None = None

    def add_providers(self, *providers: Provider) -> None:
        new_container = make_async_container(*providers)
        new_container.parent_container = self._container
        self._container = new_container

    def get_container(self) -> AsyncContainer:
        if not self._container:
            raise RuntimeError("Container is not initialized")
        return self._container


container = DynamicContainer()
