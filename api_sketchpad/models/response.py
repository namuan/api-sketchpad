"""Response model for API SketchPad."""

from dataclasses import asdict
from typing import Any

from pydantic import BaseModel, Field


class Response(BaseModel):
    """Represents an expected response for a specific HTTP status code."""

    status_code: int = Field(..., ge=100, le=599, description="HTTP status code")
    headers: dict[str, str] = Field(
        default_factory=dict, description="Response headers"
    )
    body: str = Field(default="", description="Response body content")

    def to_dict(self) -> dict[str, Any]:
        """Convert the response to a dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Response":
        """Create a Response instance from a dictionary."""
        return cls(**data)

    def get_validation_errors(self) -> list[str]:
        """Return a list of validation error messages for the response."""
        errors = []

        # Validate status code range
        http_status_min = 100
        http_status_max = 599
        if not http_status_min <= self.status_code <= http_status_max:
            errors.append(
                f"Status code {self.status_code} is not a valid HTTP status code"
            )

        # Validate headers
        for key, value in self.headers.items():
            if not isinstance(key, str) or not key.strip():
                errors.append(f"Header key '{key}' must be a non-empty string")
            if not isinstance(value, str):
                errors.append(f"Header value for '{key}' must be a string")

        return errors
