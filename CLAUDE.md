# kagimcp

Fork of Kagi's official MCP server, exposing Kagi's Search API (web/news/videos/podcasts/images) and Extract API (page-to-markdown) as tools for MCP clients like Claude Desktop, Claude Code, and Codex CLI.

## Memory Context
- Kagi API/MCP memory lives at `/Users/kodymullins/Workspace/Memory/tooling/kagi-search/memory.md`.
- Use memory for cost, install/config posture, tool availability, and secret-handling context. Use the live checkout (`README.md`, `pyproject.toml`, `src/kagimcp/server.py`) for implementation details.
- Never print, commit, or copy the raw `KAGI_API_KEY`; keep local and MCP config outputs redacted.

## Upstream Status
This is a **fork of an upstream open-source project**, not locally authored code.
- `origin` = `github.com/kodymullinsx/kagimcp.git`, `upstream` = `github.com/kagisearch/kagimcp.git`
- LICENSE (MIT) copyright holder is Kagi Search; `pyproject.toml` author is Kagi's maintainer (Rehan Ali Rana)
- 84 commits of genuine multi-contributor history dating to Dec 2024
- **Local changes: one commit**, `35ea8a4` "Remediate Kagi MCP client safety issues" — relocated the vendored OpenAPI client under `src/kagimcp/`, added request-scoped auth handling, added an HTTPS/SSRF URL guard for `kagi_extract`, and added the two test files

## Tech Stack
- Python 3.12, managed with `uv` / `hatchling`
- `fastmcp~=3.2`, `pydantic~=2.12.5`, `urllib3`
- Vendored, generated OpenAPI client at `src/kagimcp/openapi_client/`

## Structure
```
kagimcp/
├── Dockerfile, LICENSE (MIT), README.md, pyproject.toml, uv.lock
├── src/kagimcp/{__init__.py, server.py, openapi_client/}
└── tests/{test_server.py, test_packaging_imports.py}
```

## Running
```
uvx kagimcp                                          # stdio mode (Claude Desktop/Code config)
uv run kagimcp --http --host 0.0.0.0 --port 8000     # HTTP mode
```
Note: the Dockerfile pulls the published `kagimcp==1.0.0` from PyPI, not local source.

## Authentication
- Stdio mode: `KAGI_API_KEY` environment variable
- HTTP mode: multi-tenant, expects a per-request `Authorization: Bearer <key>` header; pass-through verifier does no local validation — Kagi's API validates the key

## Notable Quirks
- `KAGI_HIDDEN_PARAMS` hides certain search params from the LLM-visible tool schema via fastmcp's `ArgTransformConfig`
- Mutual exclusivity enforced between `lens_id` and domain/time filters
- `/healthz` route for container health checks; `--cors-origins` flag for HTTP mode
- No `.env.example` or `smithery.yaml` present, despite README referencing Smithery (a "drop smithery" commit exists in history)
- Retry policy intentionally skips retries on POST/billable operations (covered by tests)
- `kagi_extract` URL validation rejects `file://`, plain `http://`, and malformed URLs (SSRF guard, locally added)
