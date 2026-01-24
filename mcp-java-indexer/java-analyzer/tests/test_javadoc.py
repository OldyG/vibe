from mcp_server import handlers

from tests.conftest import fixture_path


def test_read_javadoc():
    path = fixture_path("JavadocOnly.java").as_posix()
    index_data = handlers.java_index(path, {})
    cls = index_data["classes"][0]
    method = next(m for m in cls["methods"] if m["name"] == "add")
    result = handlers.java_read_javadoc(path, method["symbolId"], {"includeLineNumbers": True})
    assert result["found"] is True
    assert "Adds two numbers" in result["content"]
    assert result["startLine"] == 4
