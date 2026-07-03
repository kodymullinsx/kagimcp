# kagimcp

## Project Context

- Canonical checkout: `/Users/kodymullins/Workspace/tooling/mcp/kagimcp`.
- This is a fork of Kagi's upstream MCP server. Keep upstream behavior recognizable and isolate local safety fixes.
- Memory context lives at `/Users/kodymullins/Workspace/Memory/tooling/kagi-search/memory.md`. Use it for Kagi API/MCP posture, cost, install, and secret-handling context; use live code/docs for implementation details.

## Key Paths

| Path | Purpose |
|---|---|
| `src/kagimcp/server.py` | MCP server, tool definitions, transport, auth, retry, and URL validation |
| `src/kagimcp/openapi_client/` | Vendored generated Kagi OpenAPI client |
| `tests/test_server.py` | Server behavior, auth, retry, validation tests |
| `tests/test_packaging_imports.py` | Packaging/import regression coverage |
| `pyproject.toml` | Python 3.12 package metadata and console script |
| `Dockerfile` | Hosted-container path; currently installs the published PyPI package, not local source |

## Commands

```bash
uv sync
uv run pytest
KAGI_API_KEY=<redacted> uv run kagimcp
uv run kagimcp --http --host 0.0.0.0 --port 8000
```

Inspector smoke:

```bash
npx @modelcontextprotocol/inspector uv --directory /ABSOLUTE/PATH/TO/kagimcp run kagimcp
```

## Working Rules

- Never print or commit `KAGI_API_KEY`. Use env vars or the machine secrets inventory, and keep values redacted in output.
- Preserve request-scoped auth in HTTP mode. HTTP mode is multi-tenant and should read `Authorization: Bearer ...` per request.
- Preserve the `kagi_extract` HTTPS/SSRF guard. Do not weaken URL validation without an explicit security review.
- Search and Extract are billable POST operations; do not add retry behavior that replays billable requests unless the user explicitly accepts that risk.
- If editing generated OpenAPI client code, identify whether regeneration is available before hand-editing large generated surfaces.

## Verification

- Run `uv run pytest` for Python code changes.
- For MCP contract changes, also inspect `tools/list` through the MCP inspector or HTTP transport with a redacted bearer token.
- For packaging changes, verify `uv run kagimcp` imports the local checkout and `tests/test_packaging_imports.py` still passes.
