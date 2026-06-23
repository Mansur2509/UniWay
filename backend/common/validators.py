from urllib.parse import urlparse

from django.core.exceptions import ValidationError


def validate_http_url(value: str) -> None:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValidationError("Provide a valid http or https URL.")

