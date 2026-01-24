"""
출력 모드별 JSON 포맷터

AI의 토큰 효율성을 극대화하기 위한 3단계 출력 모드:
- ultra-compact: 파일 개요 (98% 토큰 절감)
- compact: 주요 정보 (92% 토큰 절감)
- full: 모든 상세 정보 (기존 방식)
"""
from typing import Dict, List, Any, Optional


def format_ultra_compact(index_data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
    """
    ultra-compact 모드 포맷터

    Args:
        index_data: index_java_file()의 반환값 (full 모드)
        options: 포맷팅 옵션
            - with_fields: bool (기본값: True)
            - scope: str (기본값: "all", 옵션: "public", "protected", "private")

    Returns:
        ultra-compact 형식의 JSON
    """
    result = {
        "file": _get_filename(index_data["filePath"]),
        "lines": index_data["lineCount"],
        "classes": []
    }

    for cls in index_data["classes"]:
        formatted_class = {
            "name": cls["name"],
            "annotations": cls.get("annotations", []),
            "range": _get_range_with_javadoc(cls),
            "methods": _format_methods_ultra(cls["methods"], options)
        }

        if options.get("with_fields", True):
            formatted_class["fields"] = _format_fields_ultra(cls["fields"])

        result["classes"].append(formatted_class)

    return result


def format_compact(index_data: Dict[str, Any], options: Dict[str, Any]) -> Dict[str, Any]:
    """
    compact 모드 포맷터

    Args:
        index_data: index_java_file()의 반환값 (full 모드)
        options: 포맷팅 옵션

    Returns:
        compact 형식의 JSON
    """
    result = {
        "file": _get_filename(index_data["filePath"]),
        "lines": index_data["lineCount"],
        "classes": []
    }

    for cls in index_data["classes"]:
        formatted_class = {
            "name": cls["name"],
            "annotations": cls.get("annotations", []),
            "range": _get_range_with_javadoc(cls),
            "doc": _get_javadoc_first_line(cls.get("javadoc")),
            "methods": _format_methods_compact(cls["methods"], options)
        }

        if options.get("with_fields", True):
            formatted_class["fields"] = _format_fields_compact(cls["fields"])

        result["classes"].append(formatted_class)

    return result


def _get_filename(file_path: str) -> str:
    """파일 경로에서 파일명만 추출"""
    # Windows와 Unix 경로 모두 처리
    return file_path.replace("\\", "/").split("/")[-1]


def _get_range_with_javadoc(symbol: Dict[str, Any]) -> List[int]:
    """
    javadoc 시작부터 심볼 끝까지 range 반환

    Args:
        symbol: 클래스, 메서드, 필드 등의 심볼 정보

    Returns:
        [start_line, end_line] (javadoc 시작 ~ 심볼 끝)
    """
    javadoc = symbol.get("javadoc", {})
    start = javadoc.get("startLine") if javadoc.get("present") else symbol["startLine"]
    return [start, symbol["endLine"]]


def _get_javadoc_first_line(javadoc: Optional[Dict[str, Any]]) -> str:
    """
    javadoc의 첫 줄만 반환 (trim 후)

    Args:
        javadoc: javadoc 정보 dict

    Returns:
        첫 줄 문자열 (없으면 빈 문자열)
    """
    if not javadoc or not javadoc.get("present"):
        return ""

    preview = javadoc.get("preview", "")
    if not preview:
        return ""

    # "/**\n * 첫 줄\n * 둘째 줄\n */" → "첫 줄"
    lines = preview.split("\n")
    for line in lines:
        cleaned = line.strip().lstrip("/*").lstrip("*").rstrip("*/").strip()
        if cleaned:
            return cleaned

    return ""


def _get_full_javadoc_content(javadoc: Optional[Dict[str, Any]]) -> str:
    """
    javadoc 전체 내용 반환 (필드용)

    Args:
        javadoc: javadoc 정보 dict

    Returns:
        전체 javadoc 내용 (멀티라인 가능, 주석 기호 제거)
    """
    if not javadoc or not javadoc.get("present"):
        return ""

    preview = javadoc.get("preview", "")
    if not preview:
        return ""

    # "/**\n * line1\n * line2\n */" → "line1\nline2"
    lines = []
    for line in preview.split("\n"):
        cleaned = line.strip().lstrip("/*").lstrip("*").rstrip("*/").strip()
        if cleaned:
            lines.append(cleaned)

    return "\n".join(lines)


def _format_methods_ultra(methods: List[Dict[str, Any]], options: Dict[str, Any]) -> List[str]:
    """
    ultra-compact 모드: 메서드를 문자열 배열로 포맷

    Format: "methodName(ParamType1, ParamType2) [start-end]"
    Example: "selectDetailByMailUser(MailUser) [53-69]"
    """
    scope = options.get("scope", "all")
    result = []

    for method in methods:
        if not _is_in_scope(method["modifiers"], scope):
            continue

        # 파라미터 타입만 추출
        param_types = [p["typeText"] for p in method.get("params", [])]
        params_str = ", ".join(param_types)

        # range (javadoc 포함)
        range_list = _get_range_with_javadoc(method)
        range_str = f"[{range_list[0]}-{range_list[1]}]"

        result.append(f"{method['name']}({params_str}) {range_str}")

    return result


def _format_methods_compact(methods: List[Dict[str, Any]], options: Dict[str, Any]) -> List[Dict[str, Any]]:
    """compact 모드: 메서드를 객체 배열로 포맷"""
    scope = options.get("scope", "all")
    result = []

    for method in methods:
        if not _is_in_scope(method["modifiers"], scope):
            continue

        range_list = _get_range_with_javadoc(method)

        result.append({
            "id": str(range_list[0]),  # 시작 줄번호 (문자열)
            "name": method["name"],
            "sig": method["signatureText"],
            "range": range_list,
            "doc": _get_javadoc_first_line(method.get("javadoc"))
        })

    return result


def _format_fields_ultra(fields: List[Dict[str, Any]]) -> List[str]:
    """
    ultra-compact 모드: 필드를 문자열 배열로 포맷

    Format: "TypeName fieldName"
    Example: "LabelRuleSupporter labelRuleSupporter"
    """
    result = []
    for field in fields:
        result.append(f"{field['typeText']} {field['name']}")
    return result


def _format_fields_compact(fields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """compact 모드: 필드를 객체 배열로 포맷"""
    result = []

    for field in fields:
        # javadoc 전체 내용 (여러 줄 가능)
        javadoc_content = _get_full_javadoc_content(field.get("javadoc"))

        # signatureText가 없으면 직접 생성
        sig = field.get("signatureText")
        if not sig:
            modifiers_str = " ".join(field.get("modifiers", []))
            type_text = field.get("typeText", "")
            name = field.get("name", "")
            sig = f"{modifiers_str} {type_text} {name}".strip()

        result.append({
            "name": field["name"],
            "sig": sig,
            "doc": javadoc_content
        })

    return result


def _is_in_scope(modifiers: List[str], scope: str) -> bool:
    """
    접근 제한자 필터링

    Args:
        modifiers: 접근 제한자 리스트 (예: ["public", "static"])
        scope: 필터링 범위 ("all", "public", "protected", "private")

    Returns:
        해당 scope에 포함되는지 여부
    """
    if scope == "all":
        return True

    scope_levels = {
        "public": ["public"],
        "protected": ["public", "protected"],
        "private": ["public", "protected", "private"]
    }

    allowed = scope_levels.get(scope, ["public", "protected", "private"])

    for modifier in modifiers:
        if modifier in allowed:
            return True

    # modifier가 없으면 package-private → protected로 취급
    if not any(m in ["public", "protected", "private"] for m in modifiers):
        return "protected" in allowed

    return False
