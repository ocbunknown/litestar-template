import re

EMAIL_REGEX = re.compile(r"^[^@]+@[^@]+\.[^@]+$")


def validate_email(value: str) -> str:
    if not EMAIL_REGEX.fullmatch(value):
        raise ValueError(f"Invalid email: {value}")
    return value
