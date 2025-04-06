from __future__ import annotations

from collections import deque
from collections.abc import Awaitable, Callable
from functools import lru_cache, wraps
from typing import (
    TYPE_CHECKING,
    Any,
    Final,
    Optional,
    Union,
)

from sqlalchemy import ColumnExpressionArgument, Select, select, true
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import RelationshipProperty, aliased, contains_eager, subqueryload

from src.common.exceptions import AppException, ConflictError
from src.database._utils import frozendict
from src.database.models import MODELS_RELATIONSHIPS_NODE
from src.database.models.base import Base

if TYPE_CHECKING:
    from sqlalchemy.orm.strategy_options import _AbstractLoad


DEFAULT_RELATIONSHIP_LOAD_LIMIT: Final[int] = 100


def _bfs_search[E: Base](
    start: type[E],
    end: str,
    node: frozendict[type[Base], tuple[RelationshipProperty[type[Base]], ...]]
    | None = None,
) -> list[RelationshipProperty[E]]:
    if node is None:
        node = MODELS_RELATIONSHIPS_NODE

    queue = deque([[start]])
    checked = set()

    while queue:
        path = queue.popleft()
        current_node = path[-1]

        if current_node in checked:
            continue
        checked.add(current_node)

        current_relations = node.get(current_node)

        for relation in current_relations or []:
            new_path: list[Any] = list(path)
            new_path.append(relation)

            if relation.key == end:
                return [
                    rel for rel in new_path if isinstance(rel, RelationshipProperty)
                ]

            queue.append(new_path + [relation.mapper.class_])

    return []


def _construct_strategy[E: Base](
    strategy: Callable[..., _AbstractLoad],
    relationship: RelationshipProperty[E],
    current: _AbstractLoad | None = None,
    **kw: Any,
) -> _AbstractLoad:
    _strategy: _AbstractLoad = (
        strategy(relationship, **kw)
        if current is None
        else getattr(current, strategy.__name__)(relationship, **kw)
    )

    return _strategy


def _construct_loads[E: Base](
    entity: type[E],
    query: Select[tuple[E]],
    relationships: list[RelationshipProperty[E]],
    order_by: tuple[str, ...],
    exclude: set[type[E]],
    self_key: str | None = None,
    limit: int | None = None,
    subquery: frozendict[
        str,
        Callable[[Select[tuple[E]]], Select[tuple[E]]],
    ]
    | None = None,
) -> tuple[Select[tuple[E]], _AbstractLoad | None]:
    if not relationships:
        return query, None

    load: _AbstractLoad | None = None
    for relationship in relationships:
        origin = relationship.mapper.class_

        if origin in exclude:
            continue

        exclude.add(origin)

        if relationship.uselist:
            if limit is None:
                load = _construct_strategy(subqueryload, relationship, load)
            else:
                q = select(origin).limit(limit)
                if order_by:
                    q = q.order_by(*(getattr(origin, by).desc() for by in order_by))
                if (
                    relationship.secondary is not None
                    and relationship.secondaryjoin is not None
                ):
                    query = query.outerjoin(
                        relationship.secondary, relationship.primaryjoin
                    )
                else:
                    if origin is entity and self_key:
                        alias = aliased(origin)
                        query = query.join(
                            alias,
                            getattr(entity, order_by[0]) == getattr(alias, self_key),
                        )
                        load = _construct_strategy(
                            contains_eager, relationship, load, alias=alias
                        )
                        continue

                    q = q.where(relationship.primaryjoin)
                    for key, condition in (subquery or {}).items():
                        if relationship.key == key:
                            q = condition(q)

                lateral = q.lateral().alias()
                query = query.outerjoin(lateral, true())
                load = _construct_strategy(
                    contains_eager, relationship, load, alias=lateral
                )
        else:
            query = query.outerjoin(origin, relationship.primaryjoin)
            load = _construct_strategy(contains_eager, relationship, load)

    return query, load


def add_conditions[E: Base](
    *conditions: ColumnExpressionArgument[bool],
) -> Callable[[Select[tuple[E]]], Select[tuple[E]]]:
    def _add(query: Select[tuple[E]]) -> Select[tuple[E]]:
        return query.where(*conditions)

    return _add


@lru_cache(typed=True)
def select_with_relationships[E: Base](
    *_should_load: str,
    model: type[E],
    query: Select[tuple[E]] | None = None,
    order_by: tuple[str, ...] = (),
    limit: int | None = DEFAULT_RELATIONSHIP_LOAD_LIMIT,
    self_key: str | None = None,
    subquery: Optional[
        frozendict[str, Callable[[Select[tuple[E]]], Select[tuple[E]]]]
    ] = None,
    _node: Optional[
        frozendict[type[Base], tuple[RelationshipProperty[type[Base]], ...]]
    ] = None,
) -> Select[tuple[E]]:
    if _node is None:
        _node = MODELS_RELATIONSHIPS_NODE
    if query is None:
        query = select(model)

    options = []
    to_load = list(_should_load)
    exclude: set[type[E]] = set()
    while to_load:
        result = _bfs_search(model, to_load.pop(), _node)

        if not result:
            continue
        query, construct = _construct_loads(
            model,
            query,
            result,
            subquery=subquery,
            exclude=exclude,
            order_by=order_by,
            limit=limit,
            self_key=self_key,
        )
        if construct:
            options += [construct]

    if options:
        query = query.options(*options)

    return query


def on_integrity[R, **P](
    *uniques: str,
    should_raise: Union[type[AppException], AppException] = ConflictError,
    base_message: str = "already in use",
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    def _wrapper(coro: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @wraps(coro)
        async def _inner_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                return await coro(*args, **kwargs)
            except IntegrityError as e:
                origin = str(e.orig)
                for uniq in uniques:
                    if uniq in origin:
                        if callable(should_raise):
                            message = f"{uniq} {base_message}"
                            raise should_raise(message) from e
                        else:
                            raise should_raise from e
                raise AppException() from e

        return _inner_wrapper

    return _wrapper
