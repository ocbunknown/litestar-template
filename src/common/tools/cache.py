import json
from typing import Any

from litestar import Request


def default_key_builder(
    *keys: str,
    data: dict[str, Any] | None = None,
    separator: str = ".",
    **kwargs: Any,
) -> str:
    parts = list(keys)
    if data:
        parts.extend(f"{k}{separator}{v}" for k, v in data.items())

    parts.extend(f"{k}{separator}{v}" for k, v in kwargs.items())
    return separator.join(parts)


async def request_cache_key_builder(request: Request[Any, Any, Any]) -> str:
    query_params = {
        key: request.query_params.getall(key) for key in request.query_params
    }

    raw_body = await request.body()
    body = json.loads(raw_body) if raw_body else {}

    path = request.url.path
    method = request.method
    query_key = default_key_builder(data=query_params)
    body_key = default_key_builder(data=body)

    return default_key_builder(path, method, query_key, body_key, separator=":")
