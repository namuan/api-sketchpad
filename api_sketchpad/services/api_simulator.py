"""API simulator service for testing API interactions."""

from dataclasses import dataclass
import json
import time


@dataclass
class SimulatedResponse:
    """Dataclass representing a simulated API response."""

    status_code: int
    headers: dict[str, str]
    body: str
    elapsed_time: float


class APISimulator:
    """Simulates API calls for testing and development purposes."""

    def __init__(self, default_delay: float = 1.0) -> None:
        self.default_delay = default_delay

    def execute_request(
        self, method: str, endpoint: str, headers: dict[str, str], body: str
    ) -> SimulatedResponse:
        """Execute a simulated API request with configurable delay."""
        start_time = time.time()

        # Simulate processing delay
        time.sleep(self.default_delay)

        # Generate simulated response based on request
        status_code = self._determine_status_code(method, endpoint)
        response_headers = self._generate_response_headers(headers)
        response_body = self._generate_response_body(
            method, endpoint, body, status_code
        )

        return SimulatedResponse(
            status_code=status_code,
            headers=response_headers,
            body=response_body,
            elapsed_time=time.time() - start_time,
        )

    @staticmethod
    def _determine_status_code(method: str, endpoint: str) -> int:
        """Determine appropriate status code based on request."""
        # Simple simulation logic - could be expanded
        if "error" in endpoint.lower():
            return 500
        if method in {"POST", "PUT", "PATCH"}:
            return 201
        return 200

    @staticmethod
    def _generate_response_headers(request_headers: dict[str, str]) -> dict[str, str]:
        """Generate simulated response headers."""
        # Start with some default headers
        headers = {"Content-Type": "application/json", "X-Simulated-Response": "true"}
        # Mirror some request headers if present
        if "Accept" in request_headers:
            headers["Content-Type"] = request_headers["Accept"]
        return headers

    @staticmethod
    def _generate_response_body(
        method: str, endpoint: str, request_body: str, status_code: int
    ) -> str:
        """Generate simulated response body."""
        response_data = {
            "status": status_code,
            "method": method,
            "endpoint": endpoint,
            "simulated": True,
            "timestamp": time.time(),
            "request_body": request_body if request_body else None,
        }

        try:
            return json.dumps(response_data, indent=2)
        except TypeError:
            return json.dumps({"error": "Failed to generate response body"}, indent=2)
