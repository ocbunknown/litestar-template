from contextlib import suppress

from src.api.server import serve
from src.api.setup import init_app
from src.api.v1.setup import init_v1_router
from src.settings.core import load_settings

settings = load_settings()
app = init_app(settings, init_v1_router(settings=settings))


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        serve(settings=settings)
