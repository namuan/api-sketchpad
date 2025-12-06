from __future__ import annotations

import json
from typing import TYPE_CHECKING

from api_sketchpad.services.openapi_import_service import OpenAPIImportService

if TYPE_CHECKING:
    from pathlib import Path


def write_spec(tmp_path: Path) -> Path:
    spec = {
        "openapi": "3.0.3",
        "info": {"title": "PetStore", "version": "1.0.0"},
        "paths": {
            "/pets": {
                "get": {
                    "summary": "List pets",
                    "parameters": [
                        {
                            "in": "query",
                            "name": "limit",
                            "schema": {"type": "integer", "default": 10},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "A paged array of pets",
                            "content": {
                                "application/json": {
                                    "example": [
                                        {"id": 1, "name": "Fluffy"},
                                        {"id": 2, "name": "Spot"},
                                    ]
                                }
                            },
                        }
                    },
                },
                "post": {
                    "summary": "Create pet",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"},
                                "example": {"name": "Fluffy"},
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Created",
                            "content": {"application/json": {"example": {"id": 3}}},
                        }
                    },
                },
            }
        },
    }
    p = tmp_path / "openapi.json"
    p.write_text(json.dumps(spec), encoding="utf-8")
    return p


def test_import_creates_interactions(tmp_path: Path) -> None:
    path = write_spec(tmp_path)
    service = OpenAPIImportService()
    success, interactions, error = service.import_file(str(path))
    assert success, error or "import failed"
    assert interactions is not None
    assert len(interactions) == 2

    get_interaction = next(i for i in interactions if i.method == "GET")
    assert get_interaction.path == "/pets"
    assert get_interaction.query_params.get("limit") == "10"
    resp_200 = get_interaction.responses.get(200)
    assert resp_200 is not None
    assert resp_200.headers.get("Content-Type") == "application/json"

    post_interaction = next(i for i in interactions if i.method == "POST")
    assert post_interaction.request_headers.get("Content-Type") == "application/json"
    assert "Fluffy" in post_interaction.request_body
