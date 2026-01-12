import os
from pathlib import Path

import pytest


@pytest.fixture(scope="session", autouse=True)
def set_repo_root(tmp_path_factory):
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)
    cache_dir = tmp_path_factory.mktemp("mcp_java_index_cache")
    os.environ["MCP_JAVA_INDEX_CACHE_ROOT"] = str(cache_dir)
    return root


def fixture_path(name: str) -> Path:
    return Path("tests") / "fixtures" / name
