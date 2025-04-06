from dataclasses import dataclass, field
from typing import Any, Callable

from src.core.settings import Settings
from src.database import DBGateway

from .external import ExternalServiceGateway
from .internal import InternalServiceGateway
from .provider.base import AsyncProvider


@dataclass(slots=True)
class ServiceGateway:
    database_factory: Callable[[], DBGateway]
    provider: AsyncProvider
    settings: Settings
    _cache: dict[str, Any] = field(default_factory=dict)

    @property
    def internal(self) -> InternalServiceGateway:
        return InternalServiceGateway(self.database_factory())

    @property
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
    "ServiceGateway",
    "InternalServiceGateway",
    "ExternalServiceGateway",
)
