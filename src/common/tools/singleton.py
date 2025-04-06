from typing import Callable


def singleton[DependencyType](
    dependency: DependencyType,
) -> Callable[[], DependencyType]:
    def singleton_factory() -> DependencyType:
        return dependency

    return singleton_factory
