"""Validation service for API SketchPad."""

import json

from defusedxml import ElementTree


class ValidationService:
    """Service for validating user inputs and data structures."""

    @staticmethod
    def validate_json(text: str) -> tuple[bool, str | None]:
        """Validate JSON content format."""
        try:
            json.loads(text)
            return True, None
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {e!s}"

    @staticmethod
    def validate_xml(text: str) -> tuple[bool, str | None]:
        """Validate XML content format."""
        try:
            ElementTree.fromstring(text)
            return True, None
        except ElementTree.ParseError as e:
            return False, f"Invalid XML: {e!s}"

    @staticmethod
    def validate_url_path(path: str) -> tuple[bool, str | None]:
        """Validate URL path syntax."""
        if not path.startswith("/"):
            return False, "Path must start with '/'"
        return True, None

    @staticmethod
    def validate_header_key(key: str) -> tuple[bool, str | None]:
        """Validate header key format."""
        if not isinstance(key, str) or not key.strip():
            return False, "Header key must be a non-empty string"
        return True, None

    @staticmethod
    def validate_http_method(method: str) -> tuple[bool, str | None]:
        """Validate HTTP method is in allowed list."""
        valid_methods = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}
        if method.upper() not in valid_methods:
            return (
                False,
                f"Invalid HTTP method: {method}. Must be one of: {", ".join(valid_methods)}",
            )
        return True, None
