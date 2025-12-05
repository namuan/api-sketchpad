"""Interaction model for API SketchPad."""

from dataclasses import asdict
from typing import Any, ClassVar

from pydantic import BaseModel, Field

from .response import Response


class Interaction(BaseModel):
    """Represents a single API interaction configuration."""

    name: str = Field(
        default="New Interaction", max_length=255, description="Name of the interaction"
    )
    description: str = Field(default="", description="Description of the interaction")
    method: str = Field(default="GET", description="HTTP method")
    path: str = Field(default="", description="API endpoint path")
    request_headers: dict[str, str] = Field(
        default_factory=lambda: {
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        description="Request headers",
    )
    request_body: str = Field(default="", description="Request body content")
    responses: dict[int, Response] = Field(
        default_factory=lambda: {
            200: Response(
                status_code=200, headers={"Content-Type": "application/json"}, body=""
            ),
            400: Response(
                status_code=400, headers={"Content-Type": "application/json"}, body=""
            ),
            500: Response(
                status_code=500, headers={"Content-Type": "application/json"}, body=""
            ),
        },
        description="Expected responses by status code",
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert the interaction to a dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Interaction":
        """Create an Interaction instance from a dictionary."""
        # Convert responses dict to Response objects
        if "responses" in data:
            responses = {}
            for status_code, response_data in data["responses"].items():
                if isinstance(response_data, dict):
                    responses[int(status_code)] = Response.from_dict(response_data)
                else:
                    responses[int(status_code)] = response_data
            data["responses"] = responses

        return cls(**data)

    MAX_NAME_LENGTH: ClassVar[int] = 255

    def validate(self) -> list[str]:
        """Validate the interaction and return a list of error messages."""
        errors = []

        # Validate name length
        if len(self.name) > self.MAX_NAME_LENGTH:
            errors.append("Interaction name cannot exceed 255 characters")

        # Validate HTTP method
        valid_methods = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}
        if self.method not in valid_methods:
            errors.append(f"Invalid HTTP method: {self.method}")

        # Validate path (basic URL path validation)
        if not self.path.startswith("/") and self.path:
            errors.append("Path must start with '/'")

        # Validate request headers
        for key, value in self.request_headers.items():
            if not isinstance(key, str) or not key.strip():
                errors.append(f"Request header key '{key}' must be a non-empty string")
            if not isinstance(value, str):
                errors.append(f"Request header value for '{key}' must be a string")

        # Validate responses
        for status_code, response in self.responses.items():
            if not isinstance(response, Response):
                errors.append(
                    f"Response for status code {status_code} must be a Response object"
                )
            else:
                response_errors = response.validate()
                errors.extend([
                    f"Response {status_code}: {error}" for error in response_errors
                ])

        return errors

    def update_response(self, status_code: int, response: Response) -> None:
        """Update or add a response for a specific status code."""
        self.responses[status_code] = response

    def remove_response(self, status_code: int) -> bool:
        """Remove a response for a specific status code. Returns True if removed, False if not found."""
        if status_code in self.responses:
            del self.responses[status_code]
            return True
        return False

    def get_response(self, status_code: int) -> Response | None:
        """Get a response for a specific status code."""
        return self.responses.get(status_code)
