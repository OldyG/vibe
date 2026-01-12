from mcp_server import handlers

from tests.conftest import fixture_path


def test_read_range_basic():
    path = fixture_path("SimpleClass.java").as_posix()
    result = handlers.java_read_range(path, 1, 3, {"includeLineNumbers": True})
    content = result["content"]
    assert "1: package com.example;" in content
    assert "3: public class SimpleClass" in content
