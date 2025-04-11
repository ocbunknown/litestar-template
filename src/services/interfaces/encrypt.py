from typing import Protocol


class AbstractEncrypt(Protocol):
    def encrypt(self, plain_text: str) -> bytes: ...

    def decrypt(self, encrypted_text: bytes) -> str: ...
