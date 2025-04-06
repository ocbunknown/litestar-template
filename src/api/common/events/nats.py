from typing import Any, Callable

from src.api.common.events.base import Event


class NatsEvent(Event):
    subject: str = ""
    _reply: str = ""
    _headers: dict[str, Any] | None = None


class NatsJetStreamEvent(Event):
    subject: str = ""
    _stream: str | None = None
    _timeout: float | None = None
    _headers: dict[str, Any] | None = None


def rebuild_nats_event[T: NatsEvent](
    subject: str = "",
    subject_namespace: str | None = None,
    separator: str = ".",
    reply: str = "",
    headers: dict[str, Any] | None = None,
) -> Callable[[type[T]], type[T]]:
    def _wrapper(cls: type[T]) -> type[T]:
        updated_subject = subject

        class UpdatedEvent(cls):  # type: ignore
            subject: str = updated_subject
            _reply: str = reply
            if headers is not None:
                _headers: dict[str, Any] = headers

            def __post_init__(self) -> None:
                if subject_namespace and self.subject:
                    self.subject = f"{subject_namespace}{separator}{self.subject}"
                elif not self.subject and subject:
                    self.subject = subject

        UpdatedEvent.__name__ = cls.__name__
        UpdatedEvent.__qualname__ = cls.__qualname__
        UpdatedEvent.__module__ = cls.__module__
        UpdatedEvent.__parameters__ = cls.__parameters__  # type: ignore
        UpdatedEvent.__orig_bases__ = cls.__orig_bases__  # type: ignore
        return UpdatedEvent

    return _wrapper


def rebuild_jetstream_event[T: NatsJetStreamEvent](
    subject: str = "",
    subject_namespace: str | None = None,
    separator: str = ".",
    stream: str | None = None,
    timeout: float | None = None,
    headers: dict[str, Any] | None = None,
) -> Callable[[type[T]], type[T]]:
    def _wrapper(cls: type[T]) -> type[T]:
        updated_subject = subject

        class UpdatedEvent(cls):  # type: ignore
            subject: str = updated_subject
            if stream is not None:
                _stream: str = stream
            if timeout is not None:
                _timeout: float = timeout
            if headers is not None:
                _headers: dict[str, Any] = headers

            def __post_init__(self) -> None:
                if subject_namespace and self.subject:
                    self.subject = f"{subject_namespace}{separator}{self.subject}"
                elif not self.subject and subject:
                    self.subject = subject

        UpdatedEvent.__name__ = cls.__name__
        UpdatedEvent.__qualname__ = cls.__qualname__
        UpdatedEvent.__module__ = cls.__module__
        UpdatedEvent.__parameters__ = cls.__parameters__  # type: ignore
        UpdatedEvent.__orig_bases__ = cls.__orig_bases__  # type: ignore
        return UpdatedEvent

    return _wrapper
