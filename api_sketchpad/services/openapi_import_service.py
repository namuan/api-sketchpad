"""Service to import OpenAPI specifications into Interaction models."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, cast

from openapi_spec_validator import validate
from prance import ResolvingParser
from ruamel.yaml import YAML

from ..models.interaction import Interaction
from ..models.response import Response

logger = logging.getLogger(__name__)


class OpenAPIImportService:
    """Parses an OpenAPI 3.x/2.x spec and maps it to interactions."""

    MAX_FILE_BYTES = 5 * 1024 * 1024

    def import_file(
        self, file_path: str
    ) -> tuple[bool, list[Interaction] | None, str | None]:
        """Import interactions from an OpenAPI spec file.

        Returns (success, interactions, error_message).
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return False, None, "File does not exist"
            size = path.stat().st_size
            if size > self.MAX_FILE_BYTES:
                return False, None, "File too large"

            raw_spec = self._read_raw_spec(path)
            self._validate_raw_spec(raw_spec)

            parser = ResolvingParser(str(path), lazy=False, strict=True)
            spec = cast("dict[str, Any]", parser.specification)
            interactions = self._convert_spec_to_interactions(spec)
            return True, interactions, None
        except Exception as exc:  # noqa: BLE001
            logger.debug("OpenAPI import failed", exc_info=True)
            return False, None, f"OpenAPI import error: {exc!s}"

    def _convert_spec_to_interactions(self, spec: dict[str, Any]) -> list[Interaction]:
        paths: dict[str, Any] = spec.get("paths", {})
        interactions: list[Interaction] = []
        for path, path_item in paths.items():
            for method in ("get", "post", "put", "delete", "patch", "head", "options"):
                op = path_item.get(method)
                if not isinstance(op, dict):
                    continue
                interaction = self._operation_to_interaction(path, method, op)
                interactions.append(interaction)
        return interactions

    def _operation_to_interaction(
        self, path: str, method: str, op: dict[str, Any]
    ) -> Interaction:
        name = op.get("operationId") or f"{method.upper()} {path}"
        description = op.get("summary") or op.get("description") or ""

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        query_params = self._collect_query_params(op)
        body_text, ct_header = self._build_request_body(op)
        if ct_header:
            headers["Content-Type"] = ct_header
        responses_map = self._build_responses(op)

        kwargs: dict[str, Any] = {
            "name": name,
            "description": description,
            "method": method.upper(),
            "path": path,
            "request_headers": headers,
            "query_params": query_params,
            "request_body": body_text,
        }
        if responses_map:
            kwargs["responses"] = responses_map
        return Interaction(**kwargs)

    @staticmethod
    def _extract_example(media_type_obj: dict[str, Any]) -> str:
        ex = media_type_obj.get("example")
        if ex is None:
            examples = media_type_obj.get("examples")
            if isinstance(examples, dict) and examples:
                first = next(iter(examples.values()))
                ex = first.get("value")
        if ex is None:
            schema = media_type_obj.get("schema")
            if isinstance(schema, dict):
                ex = schema.get("example")
        if ex is None:
            return ""

        try:
            return json.dumps(ex, ensure_ascii=False, indent=2)
        except Exception:  # noqa: BLE001
            return str(ex)

    @staticmethod
    def _collect_query_params(op: dict[str, Any]) -> dict[str, str]:
        result: dict[str, str] = {}
        for p in op.get("parameters", []):
            if p.get("in") == "query":
                pname = p.get("name") or "param"
                default_val = p.get("schema", {}).get("default")
                result[str(pname)] = "" if default_val is None else str(default_val)
        return result

    def _build_request_body(self, op: dict[str, Any]) -> tuple[str, str | None]:
        req_body = op.get("requestBody")
        if not isinstance(req_body, dict):
            return "", None
        content = req_body.get("content", {})
        if not isinstance(content, dict) or not content:
            return "", None
        mt, mt_obj = next(iter(content.items()))
        body_text = self._extract_example(mt_obj)
        return body_text, str(mt)

    def _build_responses(self, op: dict[str, Any]) -> dict[int, Response]:
        responses_map: dict[int, Response] = {}
        responses_obj = op.get("responses", {})
        if not isinstance(responses_obj, dict):
            return responses_map
        for code_str, resp_obj in responses_obj.items():
            if code_str == "default":
                continue
            try:
                code = int(code_str)
            except ValueError:
                continue
            if not isinstance(resp_obj, dict):
                continue
            content = resp_obj.get("content", {})
            headers_out: dict[str, str] = {}
            body_out = ""
            if isinstance(content, dict) and content:
                mt, mt_obj = next(iter(content.items()))
                headers_out["Content-Type"] = str(mt)
                body_out = self._extract_example(mt_obj)
            responses_map[code] = Response(
                status_code=code, headers=headers_out, body=body_out
            )
        return responses_map

    @staticmethod
    def _read_raw_spec(path: Path) -> dict[str, Any]:
        if path.suffix.lower() in {".yaml", ".yml"}:
            yaml = YAML(typ="safe")
            with path.open("r", encoding="utf-8") as f:
                data = yaml.load(f) or {}
        else:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        if not isinstance(data, dict):
            return {}
        return cast("dict[str, Any]", data)

    @staticmethod
    def _validate_raw_spec(spec_dict: dict[str, Any]) -> None:
        validate(cast("Any", spec_dict))
