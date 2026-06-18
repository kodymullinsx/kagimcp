import importlib.util
from pathlib import Path

import kagimcp.openapi_client as openapi_client
from kagimcp.openapi_client import ApiClient, ExtractApi, SearchApi


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
