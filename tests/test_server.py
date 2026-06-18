import importlib
from types import SimpleNamespace

import pytest

import kagimcp.server as server


class _RawResponse:
    status = 200
    headers = {}
    data = b"ok"


class _ExtractResponse:
    meta = None
    errors = None
    data = [SimpleNamespace(markdown="markdown")]


class _SearchApi:
    def __init__(self, _api_client):
        self.calls = []

    def search_without_preload_content(self, request, **kwargs):
        self.calls.append((request, kwargs))
        return _RawResponse()


class _ExtractApi:
    def __init__(self, _api_client):
        self.calls = []

    def extract_content(self, request, **kwargs):
        self.calls.append((request, kwargs))
        return _ExtractResponse()


@pytest.fixture(autouse=True)
def clear_clients_cache():
    server._clients.cache_clear()
    yield
    server._clients.cache_clear()


def _search(query):
    return server.kagi_search_fetch(
        query,
        workflow="search",
        extract_count=0,
        limit=10,
        include_domains=None,
        exclude_domains=None,
        time_relative=None,
        after=None,
        before=None,
        file_type=None,
        lens_id=None,
    )


def test_retry_policy_does_not_retry_post():
    retry = server._retry_policy()

    assert retry.allowed_methods == server.Retry.DEFAULT_ALLOWED_METHODS
    assert "POST" not in retry.allowed_methods


def test_max_retries_zero_disables_retries(monkeypatch):
    monkeypatch.setenv("KAGI_MAX_RETRIES", "0")
    reloaded = importlib.reload(server)
    try:
        assert reloaded._retry_policy().total == 0
    finally:
        monkeypatch.delenv("KAGI_MAX_RETRIES", raising=False)
        importlib.reload(reloaded)


def test_request_auth_is_request_scoped_and_clients_are_shared(monkeypatch):
    monkeypatch.setattr(server, "SearchApi", _SearchApi)
    monkeypatch.setattr(server, "ExtractApi", _ExtractApi)
    monkeypatch.setattr(server, "_resolve_api_key", lambda: "token-one")

    assert _search("first") == "ok"
    search_api, extract_api = server._clients()
    first_auth = search_api.calls[-1][1]["_request_auth"]

    monkeypatch.setattr(server, "_resolve_api_key", lambda: "token-two")
    assert _search("second") == "ok"
    second_search_api, second_extract_api = server._clients()
    second_auth = second_search_api.calls[-1][1]["_request_auth"]

    assert search_api is second_search_api
    assert extract_api is second_extract_api
    assert first_auth == {
        "type": "bearer",
        "in": "header",
        "key": "Authorization",
        "value": "Bearer token-one",
    }
    assert second_auth["value"] == "Bearer token-two"


def test_extract_passes_request_scoped_auth(monkeypatch):
    monkeypatch.setattr(server, "SearchApi", _SearchApi)
    monkeypatch.setattr(server, "ExtractApi", _ExtractApi)
    monkeypatch.setattr(server, "_resolve_api_key", lambda: "extract-token")

    assert server.kagi_extract("https://example.com/path") == "markdown"
    _, extract_api = server._clients()

    assert extract_api.calls[-1][1]["_request_auth"]["value"] == "Bearer extract-token"


@pytest.mark.parametrize(
    "url",
    ["", "not-a-url", "http://example.com", "file:///etc/passwd", "https:///path"],
)
def test_extract_rejects_invalid_urls_without_upstream_call(monkeypatch, url):
    monkeypatch.setattr(server, "SearchApi", _SearchApi)
    monkeypatch.setattr(server, "ExtractApi", _ExtractApi)
    monkeypatch.setattr(server, "_resolve_api_key", lambda: "token")

    with pytest.raises(ValueError):
        server.kagi_extract(url)

    _, extract_api = server._clients()
    assert extract_api.calls == []


def test_extract_accepts_https_url(monkeypatch):
    monkeypatch.setattr(server, "SearchApi", _SearchApi)
    monkeypatch.setattr(server, "ExtractApi", _ExtractApi)
    monkeypatch.setattr(server, "_resolve_api_key", lambda: "token")

    assert server.kagi_extract("https://example.com/path") == "markdown"
    _, extract_api = server._clients()
    assert len(extract_api.calls) == 1


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        ('{"error": [{"message": "singular"}]}', "singular"),
        ('{"errors": [{"message": "plural"}]}', "plural"),
        ('{"error": [{"message": "one"}, {"message": "two"}]}', "one; two"),
    ],
)
def test_format_error_body_extracts_messages(body, expected):
    assert server._format_error_body(body) == expected


@pytest.mark.parametrize(
    "body",
    [
        "not json",
        '{"error": ["bad", {"detail": "missing message"}]}',
        '{"error": []}',
        '{"unexpected": true}',
    ],
)
def test_format_error_body_falls_back_to_body(body):
    assert server._format_error_body(body) == body
