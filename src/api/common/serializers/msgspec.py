from typing import Any

import msgspec


def msgpack_encoder(obj: Any, *args: Any, **kw: Any) -> bytes:
    return msgspec.msgpack.encode(obj, *args, **kw)


def msgpack_decoder(obj: Any, *args: Any, **kw: Any) -> Any:
    return msgspec.msgpack.decode(obj, *args, strict=kw.pop("strict", False), **kw)


def msgspec_encoder(obj: Any, *args: Any, **kw: Any) -> str:
    return msgspec.json.encode(obj, *args, **kw).decode(encoding="utf-8")


def msgspec_decoder(obj: Any, *args: Any, **kw: Any) -> Any:
    return msgspec.json.decode(obj, *args, **kw)
