"""
출력 모드 포맷터 통합 테스트
"""
import pytest
from parser.indexer import index_java_file
from parser.formatters import format_ultra_compact, format_compact


def test_ultra_compact_mode():
    """ultra-compact 모드 테스트"""
    full_data = index_java_file("tests/fixtures/SimpleClass.java", {})
    ultra_data = format_ultra_compact(full_data, {"with_fields": True, "scope": "all"})

    # 필수 필드 존재 확인
    assert "file" in ultra_data
    assert "lines" in ultra_data
    assert "classes" in ultra_data

    # 파일명만 추출되었는지 확인
    assert ultra_data["file"] == "SimpleClass.java"

    # 클래스 정보 확인
    assert len(ultra_data["classes"]) > 0
    cls = ultra_data["classes"][0]
    assert "name" in cls
    assert "annotations" in cls
    assert "range" in cls
    assert "methods" in cls
    assert "fields" in cls

    # 메서드 형식 확인 (문자열 배열)
    assert isinstance(cls["methods"], list)
    if cls["methods"]:
        assert isinstance(cls["methods"][0], str)
        # 메서드 문자열에 줄번호 포함 확인
        assert "[" in cls["methods"][0]
        assert "]" in cls["methods"][0]

    # 필드 형식 확인 (문자열 배열)
    assert isinstance(cls["fields"], list)
    if cls["fields"]:
        assert isinstance(cls["fields"][0], str)


def test_compact_mode():
    """compact 모드 테스트"""
    full_data = index_java_file("tests/fixtures/SimpleClass.java", {"maxJavadocPreviewChars": 500})
    compact_data = format_compact(full_data, {"with_fields": True, "scope": "all"})

    assert len(compact_data["classes"]) > 0
    cls = compact_data["classes"][0]

    # 클래스 doc 확인
    assert "doc" in cls
    assert isinstance(cls["doc"], str)

    # 메서드 형식 확인 (객체 배열)
    assert isinstance(cls["methods"], list)
    if cls["methods"]:
        method = cls["methods"][0]
        assert "id" in method
        assert "name" in method
        assert "sig" in method
        assert "range" in method
        assert "doc" in method
        assert isinstance(method["range"], list)
        assert len(method["range"]) == 2

    # 필드 형식 확인 (객체 배열)
    assert isinstance(cls["fields"], list)
    if cls["fields"]:
        field = cls["fields"][0]
        assert "name" in field
        assert "sig" in field
        assert "doc" in field


def test_javadoc_extraction():
    """Javadoc 추출 테스트"""
    full_data = index_java_file("tests/fixtures/JavadocOnly.java", {"maxJavadocPreviewChars": 500})
    compact_data = format_compact(full_data, {"with_fields": True, "scope": "all"})

    cls = compact_data["classes"][0]

    # 메서드의 javadoc 첫 줄 확인
    method = cls["methods"][0]
    assert method["doc"] != ""
    assert "Adds two numbers" in method["doc"]

    # 필드의 javadoc 확인
    if cls["fields"]:
        field = cls["fields"][0]
        assert "doc" in field


def test_annotations_extraction():
    """어노테이션 추출 테스트"""
    full_data = index_java_file("tests/fixtures/AnnotationsAndOverloads.java", {})
    ultra_data = format_ultra_compact(full_data, {"with_fields": True, "scope": "all"})

    cls = ultra_data["classes"][0]

    # 메서드에 어노테이션이 있는지 확인 (full_data에서)
    full_method = full_data["classes"][0]["methods"][0]
    if full_method.get("annotations"):
        # 어노테이션이 있으면 signatureText에도 포함되어야 함
        assert "@" in full_method["signatureText"]


def test_scope_filter_public():
    """접근 제한자 필터 테스트 - public만"""
    full_data = index_java_file("tests/fixtures/SimpleClass.java", {})

    # public만
    public_only = format_ultra_compact(full_data, {"scope": "public", "with_fields": True})
    cls = public_only["classes"][0]

    # public 메서드만 포함되어야 함
    # SimpleClass.java의 doWork 메서드는 public
    assert len(cls["methods"]) >= 1


def test_no_fields_option():
    """필드 제외 옵션 테스트"""
    full_data = index_java_file("tests/fixtures/SimpleClass.java", {})

    no_fields = format_ultra_compact(full_data, {"with_fields": False, "scope": "all"})

    # fields 키가 없어야 함
    assert "fields" not in no_fields["classes"][0]


def test_token_reduction():
    """토큰 절감 효과 확인"""
    full_data = index_java_file("tests/fixtures/SimpleClass.java", {"maxJavadocPreviewChars": 500})
    ultra_data = format_ultra_compact(full_data, {"with_fields": True, "scope": "all"})
    compact_data = format_compact(full_data, {"with_fields": True, "scope": "all"})

    import json
    full_str = json.dumps(full_data, ensure_ascii=False, indent=2)
    ultra_str = json.dumps(ultra_data, ensure_ascii=False, indent=2)
    compact_str = json.dumps(compact_data, ensure_ascii=False, indent=2)

    full_lines = len(full_str.split("\n"))
    ultra_lines = len(ultra_str.split("\n"))
    compact_lines = len(compact_str.split("\n"))

    print(f"\nFull: {full_lines} lines")
    print(f"Ultra: {ultra_lines} lines ({100 - ultra_lines/full_lines*100:.1f}% reduction)")
    print(f"Compact: {compact_lines} lines ({100 - compact_lines/full_lines*100:.1f}% reduction)")

    # Ultra는 최소 50% 이상 절감
    assert ultra_lines < full_lines * 0.5

    # Compact은 Ultra보다 크고 Full보다 작아야 함
    assert ultra_lines < compact_lines < full_lines


def test_range_with_javadoc():
    """Javadoc 포함 range 테스트"""
    full_data = index_java_file("tests/fixtures/JavadocOnly.java", {"maxJavadocPreviewChars": 500})
    compact_data = format_compact(full_data, {"with_fields": True, "scope": "all"})

    cls = compact_data["classes"][0]
    method = cls["methods"][0]

    # range가 javadoc 시작부터 메서드 끝까지인지 확인
    # JavadocOnly.java의 add 메서드는 javadoc이 있음
    range_start = method["range"][0]
    range_end = method["range"][1]

    # javadoc이 있으면 range 시작이 메서드 시작보다 앞에 있어야 함
    full_method = full_data["classes"][0]["methods"][0]
    if full_method["javadoc"]["present"]:
        assert range_start == full_method["javadoc"]["startLine"]


def test_large_file_reduction():
    """대용량 파일 절감 테스트"""
    # NestedClasses.java 사용 (여러 클래스와 메서드가 있음)
    full_data = index_java_file("tests/fixtures/NestedClasses.java", {"maxJavadocPreviewChars": 500})
    ultra_data = format_ultra_compact(full_data, {"with_fields": True, "scope": "all"})

    import json
    full_str = json.dumps(full_data, ensure_ascii=False, indent=2)
    ultra_str = json.dumps(ultra_data, ensure_ascii=False, indent=2)

    full_lines = len(full_str.split("\n"))
    ultra_lines = len(ultra_str.split("\n"))

    # 복잡한 파일일수록 절감 효과가 커야 함
    reduction = (1 - ultra_lines/full_lines) * 100
    print(f"\nNested classes reduction: {reduction:.1f}%")

    assert reduction > 50  # 최소 50% 이상 절감
