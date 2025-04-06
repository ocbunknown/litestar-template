from typing import Any

import orjson

from nats.js.api import StreamConfig
from nats.js.errors import NotFoundError
from src.api.common.broker.nats.core import NatsJetStreamBroker
from src.common.di import Depends, FromDepends, inject
from src.common.tools.files import open_file_sync
from src.core.logger import log
from src.core.settings import path


def load_stream_config() -> list[dict[str, Any]]:
    stream_path = path("jetstream", "stream.json")
    if not stream_path:
        raise FileNotFoundError(f"Config file {stream_path} not found")
    config = orjson.loads(open_file_sync(stream_path, mode="r"))
    return list(config.get("streams", []))


def normalize_config(config: dict[str, Any]) -> dict[str, Any]:
    return {
        key: config.get(key)
        for key in (
            "subjects",
            "storage",
            "max_msgs",
            "max_bytes",
            "max_age",
            "discard",
        )
    }


async def sync_stream(broker: NatsJetStreamBroker, new_config: dict[str, Any]) -> None:
    stream_name = new_config.get("name")
    if not stream_name:
        raise ValueError("Stream configuration must include the 'name' key")

    try:
        stream_info = await broker.js.stream_info(stream_name)
        current_config = stream_info.config

        if current_config.retention != new_config.get("retention"):
            log.info(
                "Retention policy change detected for stream '%s'. Recreating stream...",
                stream_name,
            )
            await broker.js.delete_stream(stream_name)
            await broker.js.add_stream(**new_config)
            return

        if normalize_config(current_config.as_dict()) != normalize_config(
            StreamConfig().evolve(**new_config).as_dict()
        ):
            log.info("Updating stream '%s' configuration", stream_name)
            await broker.js.update_stream(**new_config)

    except NotFoundError:
        log.info("Stream '%s' not found. Creating it.", stream_name)
        await broker.js.add_stream(**new_config)


@inject
async def sync_streams(
    broker: Depends[NatsJetStreamBroker] = FromDepends(),
) -> None:
    try:
        for stream_config in load_stream_config():
            await sync_stream(broker, stream_config)
    except Exception as e:
        log.error("Error syncing streams: %s", e)
