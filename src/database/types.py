from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

type OrderBy = Literal["asc", "desc"]


@dataclass(frozen=True)
class OffsetPaginationResult[T]:
    data: Sequence[T]
    limit: int | None
    offset: int | None
    total: int
