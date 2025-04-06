import re
from typing import Any, Dict

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    __abstract__: bool = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()

    def as_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for attr, value in self.__dict__.items():
            if attr.startswith("_"):
                continue
            if isinstance(value, Base):
                result[attr] = value.as_dict()
            elif isinstance(value, list | tuple):
                result[attr] = type(value)(
                    v.as_dict() if isinstance(v, Base) else v for v in value
                )
            else:
                result[attr] = value

        return result
