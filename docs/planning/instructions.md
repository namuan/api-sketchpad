# Project: API SketchPad OpenAPI Import
## Goal
Load interactions from an OpenAPI JSON/YAML document into `api_sketchpad` models and UI.

## Vetted Dependencies
- prance — OpenAPI 2/3 parser with `$ref` resolution and validation backends; mature and active (docs: https://prance.readthedocs.io, repo: https://github.com/RonnyPfannschmidt/prance).
- openapi-spec-validator — Validates OpenAPI 2/3/3.1 documents; CLI + Python API (PyPI: https://pypi.org/project/openapi-spec-validator/).
- ruamel.yaml — Secure YAML loader used by prance; handles modern YAML syntax reliably.

Rationale:
- Keep to ≤3 single-purpose deps; avoid bloated frameworks.
- `prance` resolves external and internal `$ref`s and supports OpenAPI 3.x; pairs with `openapi-spec-validator` per maintainers’ guidance [1][2].
- `ruamel.yaml` is the recommended YAML backend for reliability and safety.

[1] Prance documentation: https://prance.readthedocs.io/en/latest/index.html  
[2] Prance repository: https://github.com/RonnyPfannschmidt/prance

## Structure
```
.
├── api_sketchpad/
│   ├── services/
│   │   └── openapi_import_service.py
│   ├── ui/
│   │   └── import_integration.py
│   ├── controllers/
│   │   └── import_controller.py
├── tests/
│   └── services/
│       └── test_openapi_import_service.py
```

## Security
- Use `ruamel.yaml` safe loading; never use unsafe loaders.
- Validate OpenAPI strictly before import; abort on errors.
- Run parsing in a background worker to avoid UI freeze; reject oversized files.
- Never execute schema examples; treat data as inert.
- Ban wildcard imports; explicit imports only.
- No hardcoded secrets; no `console.log`-style prints in prod.
- Sanitize file paths from `QFileDialog`; local reads only.

## Lint
make check

## Feature Description
- Adds `Import OpenAPI...` under the `File` menu to load a local `.yaml`, `.yml`, or `.json` OpenAPI document into interactions.
- Validates the spec with `openapi-spec-validator` before parsing.
- Parses with `prance` (strict mode) and maps each `paths` operation to an `Interaction`:
  - Name from `operationId` or `METHOD /path`
  - Method from operation key; path from spec
  - Request headers: `Content-Type` from `requestBody.content` (default `application/json`); `Accept` defaults to `application/json`
  - Query params from `parameters` with `in: query` (default values used when present)
  - Request body populated from `example`/`examples`/`schema.example` when available
  - Responses created per status code with `Content-Type` and body examples
- Import runs in a background thread and rejects files over 5 MB to keep the UI responsive.
- Implementation:
  - Service at `api_sketchpad/services/openapi_import_service.py`
  - Controller at `api_sketchpad/controllers/import_controller.py`
  - UI integration at `api_sketchpad/ui/import_integration.py` and menu wiring in `api_sketchpad/ui/main_window.py`
