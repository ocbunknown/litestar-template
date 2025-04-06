from sqlalchemy.orm import RelationshipProperty

from src.database._utils import frozendict

from .base import Base
from .role import Role
from .user import User

__all__ = ("Base", "User", "Role")


def _retrieve_relationships() -> dict[
    type[Base], tuple[RelationshipProperty[type[Base]], ...]
]:
    return {
        mapper.class_: tuple(mapper.relationships.values())
        for mapper in Base.registry.mappers
    }


MODELS_RELATIONSHIPS_NODE: frozendict[
    type[Base], tuple[RelationshipProperty[type[Base]], ...]
] = frozendict(_retrieve_relationships())
