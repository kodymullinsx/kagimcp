import importlib.util
from pathlib import Path

import kagimcp.openapi_client as openapi_client
from kagimcp.openapi_client import ApiClient, ExtractApi, SearchApi
from kagimcp.openapi_client.api.search_api import SearchApi as GeneratedSearchApi
from kagimcp.openapi_client.models.page_output import PageOutput


def test_generated_client_is_vendored_under_kagimcp():
    assert openapi_client.__name__ == "kagimcp.openapi_client"
    assert ApiClient.__module__.startswith("kagimcp.openapi_client")
    assert SearchApi.__module__.startswith("kagimcp.openapi_client")
    assert ExtractApi.__module__.startswith("kagimcp.openapi_client")


def test_top_level_openapi_client_source_package_is_absent():
    root = Path(__file__).resolve().parents[1]

    assert not (root / "src" / "openapi_client").exists()


def test_top_level_openapi_client_is_not_importable_from_source_tree():
    assert importlib.util.find_spec("openapi_client") is None


def test_extract_page_output_preserves_upstream_error():
    output = PageOutput.from_dict(
        {
            "url": "https://example.com",
            "markdown": None,
            "error": "Extraction was blocked",
        }
    )

    assert output.error == "Extraction was blocked"
    assert output.to_dict()["error"] == "Extraction was blocked"


def test_search_generated_client_requests_json_only():
    class SerializationClient:
        def __init__(self):
            self.accept_options = None

        def select_header_accept(self, options):
            self.accept_options = options
            return options[0]

        def select_header_content_type(self, options):
            return options[0]

        def param_serialize(self, **kwargs):
            return kwargs

    client = SerializationClient()
    api = GeneratedSearchApi(client)

    api._search_serialize(
        search_request=None,
        _request_auth=None,
        _content_type=None,
        _headers=None,
        _host_index=0,
    )

    assert client.accept_options == ["application/json"]


def test_docker_image_installs_the_checked_out_source():
    root = Path(__file__).resolve().parents[1]
    dockerfile = (root / "Dockerfile").read_text()

    assert "COPY src ./src" in dockerfile
    assert "RUN pip install ." in dockerfile
    assert "pip install kagimcp==" not in dockerfile
