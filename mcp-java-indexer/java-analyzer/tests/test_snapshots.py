import json
from pathlib import Path

from mcp_server import handlers

from tests.conftest import fixture_path


def _load_expected(base_name: str) -> dict:
    path = Path("tests") / "expected" / f"{base_name}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_snapshots():
    fixtures = [
        "SimpleClass",
        "AnnotationsAndOverloads",
        "NestedClasses",
        "RecordEnumInterface",
        "MultiLineSignature",
        "JavadocOnly",
        "JavadocWithAnnotation",
        "InnerClassJavadoc",
    ]
    for base in fixtures:
        file_path = fixture_path(f"{base}.java").as_posix()
        actual = handlers.java_index(file_path, {})
        expected = _load_expected(base)
        assert actual == expected
