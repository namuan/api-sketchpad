import time

import requests

from api_sketchpad.models.interaction import Interaction
from api_sketchpad.models.response import Response
from api_sketchpad.services.mock_server import MockServer


def test_mock_server_serves_interaction() -> None:
    interaction = Interaction(
        name="Ping",
        method="GET",
        path="/ping",
        responses={
            200: Response(
                status_code=200, headers={"Content-Type": "text/plain"}, body="pong"
            ),
        },
    )

    server = MockServer([interaction])
    port = 8765
    server.start(port)
    time.sleep(0.1)
    try:
        resp = requests.get(f"http://localhost:{port}/ping", timeout=2.0)
        assert resp.status_code == 200
        assert resp.text == "pong"
    finally:
        server.stop()
