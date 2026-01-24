from mcp_server import handlers

from tests.conftest import fixture_path


def _index(file_name: str) -> dict:
    path = fixture_path(file_name)
    file_path = path.as_posix()
    return handlers.java_index(file_path, {})


def test_index_simple_class():
    data = _index("SimpleClass.java")
    assert data["classes"], "Expected at least one class"
    cls = data["classes"][0]
    assert cls["qualifiedName"] == "com.example.SimpleClass"
    assert cls["startLine"] == 3

    fields = cls["fields"]
    assert len(fields) == 1
    assert fields[0]["name"] == "count"
    assert fields[0]["javadoc"]["present"] is True

    ctors = cls["constructors"]
    assert len(ctors) == 1
    assert ctors[0]["name"] == "SimpleClass"

    methods = cls["methods"]
    method_names = {m["name"] for m in methods}
    assert "doWork" in method_names

    inner = cls["innerClasses"]
    assert len(inner) == 1
    assert inner[0]["name"] == "Inner"


def test_annotations_and_overloads():
    data = _index("AnnotationsAndOverloads.java")
    cls = data["classes"][0]
    methods = [m for m in cls["methods"] if m["name"] == "doThing"]
    assert len(methods) == 2
    assert methods[0]["symbolId"] != methods[1]["symbolId"]

    fields = cls["fields"]
    assert fields[0]["name"] == "value"
    assert "protected" in fields[0]["modifiers"]


def test_nested_classes():
    data = _index("NestedClasses.java")
    outer = data["classes"][0]
    inner = outer["innerClasses"][0]
    deep = inner["innerClasses"][0]
    assert deep["qualifiedName"] == "com.example.nested.Outer.Inner.DeepInner"
    deep_methods = [m["name"] for m in deep["methods"]]
    assert "deepMethod" in deep_methods


def test_record_enum_interface():
    data = _index("RecordEnumInterface.java")
    kinds = {cls["name"]: cls["kind"] for cls in data["classes"]}
    assert kinds.get("Person") == "record"
    assert kinds.get("Status") == "enum"
    assert kinds.get("Worker") == "interface"

    person = next(cls for cls in data["classes"] if cls["name"] == "Person")
    assert person["constructors"], "Record should include constructor entry"


def test_multiline_signature():
    data = _index("MultiLineSignature.java")
    cls = data["classes"][0]
    method = next(m for m in cls["methods"] if m["name"] == "sortAndFilter")
    assert "sortAndFilter" in method["signatureText"]
    assert "throws" in method["signatureText"]
    assert len(method["params"]) == 2
    assert method["params"][0]["typeText"].startswith("java.util.List")
