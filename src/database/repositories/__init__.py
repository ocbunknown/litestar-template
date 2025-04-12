from typing import Literal, Optional

from src.common.exceptions import ForbiddenError, NotFoundError

type ExceptionType = Literal["update", "delete", "select", "create", "exists"]

exception_template: dict[ExceptionType, Exception] = {
    "update": ForbiddenError("Cannot be updated"),
    "delete": ForbiddenError("Cannot be deleted"),
    "select": NotFoundError("Not found"),
    "create": ForbiddenError("Cannot be created"),
    "exists": NotFoundError("Not found"),
}


class Result[T]:
    __slots__ = ("data", "exception_type")

    def __init__(self, exception_type: ExceptionType, data: Optional[T]):
        self.data = data
        self.exception_type = exception_type

    def result_or_none(self) -> Optional[T]:
        return self.data

    def result(self) -> T:
        if self.data is not None:
            return self.data

        raise exception_template[self.exception_type]


__all__ = ("Result",)
