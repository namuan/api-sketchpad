"""Mock HTTP server that serves configured interactions."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
from typing import TYPE_CHECKING, ClassVar
from urllib.parse import parse_qs, urlparse

if TYPE_CHECKING:
    from ..models.interaction import Interaction


DEFAULT_STATUS: int = 200


class _MockHTTPHandler(BaseHTTPRequestHandler):
    interactions: ClassVar[list[Interaction]] = []

    def _handle(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        method = self.command

        match = None
        for interaction in self.interactions:
            if interaction.method.upper() == method and interaction.path == path:
                match = interaction
                break

        if not match:
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error":"No matching interaction"}')
            return

        requested_status = None
        if "__status" in query:
            try:
                requested_status = int(query["__status"][0])
            except (ValueError, TypeError):
                requested_status = None

        status = requested_status if requested_status in match.responses else None
        if status is None:
            status = (
                DEFAULT_STATUS
                if DEFAULT_STATUS in match.responses
                else next(iter(match.responses.keys()))
            )

        response = match.responses[status]

        self.send_response(response.status_code)
        for k, v in response.headers.items():
            self.send_header(k, v)
        self.end_headers()
        body_bytes = (response.body or "").encode("utf-8")
        self.wfile.write(body_bytes)

    def do_GET(self) -> None:
        self._handle()

    def do_POST(self) -> None:
        self._handle()

    def do_PUT(self) -> None:
        self._handle()

    def do_PATCH(self) -> None:
        self._handle()

    def do_DELETE(self) -> None:
        self._handle()

    def do_OPTIONS(self) -> None:
        self._handle()


class MockServer:
    """Wrapper to start and stop the mock HTTP server."""

    def __init__(self, interactions: list[Interaction]) -> None:
        self._interactions = interactions
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None

    def start(self, port: int) -> None:
        if self._server:
            return
        handler_cls = type(
            "MockHTTPHandler",
            (_MockHTTPHandler,),
            {"interactions": self._interactions},
        )
        self._server = ThreadingHTTPServer(("127.0.0.1", port), handler_cls)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if not self._server:
            return
        self._server.shutdown()
        self._server.server_close()
        self._server = None
        self._thread = None
