from dataclasses import dataclass, field
from typing import Any, Callable

from src.common.tools.singleton import lazy_single
from src.database import DBGateway
from src.settings.core import Settings

from .external import ExternalServiceGateway
from .internal import InternalServiceGateway
from .provider.base import AsyncProvider


@dataclass(slots=True)
class ServiceFactory:
    database_factory: Callable[[], DBGateway]
    provider: AsyncProvider
    settings: Settings
    _cache: dict[str, Any] = field(default_factory=dict)

    def internal(self) -> Callable[[], InternalServiceGateway]:
        return lazy_single(InternalServiceGateway, self.database_factory)

    def external(self) -> ExternalServiceGateway:
        return self._from_cache(
            "external",
            ExternalServiceGateway,
            provider=self.provider,
            settings=self.settings,
        )

    def _from_cache[S](self, key: str, factory: Callable[..., S], **kwargs: Any) -> S:
        if not (cached := self._cache.get(key)):
            cached = factory(**kwargs)
            self._cache[key] = cached

        return cached


__all__ = (
    "ServiceFactory",
    "InternalServiceGateway",
    "ExternalServiceGateway",
)
