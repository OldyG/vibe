# Java Analyzer 출력 모드 개선 설계서

**작성일**: 2026-01-24  
**상태**: 설계 완료, 구현 대기  
**우선순위**: 🔥 최우선

---

## 📋 목차

1. [작업 배경 및 목적](#작업-배경-및-목적)
2. [현재 문제점](#현재-문제점)
3. [설계 목표](#설계-목표)
4. [최종 설계안](#최종-설계안)
5. [구현 명세](#구현-명세)
6. [AI를 위한 작업 지시서](#ai를-위한-작업-지시서)
7. [테스트 시나리오](#테스트-시나리오)
8. [참고 자료](#참고-자료)

---

## 🎯 작업 배경 및 목적

### 배경

`java-analyzer`는 Tree-sitter 기반 Java 소스 코드 분석 도구로, 현재 JSON 형식으로 상세한 분석 결과를 제공합니다.

**문제 상황:**

- 200줄 Java 파일 → 610줄 JSON 출력 (약 3배 증가)
- AI가 파일 개요를 파악하는데 과도한 토큰 소비
- 상세 정보는 필요할 때만 조회하면 되는데, 항상 모든 정보를 제공

### 목적

**AI의 토큰 효율성을 극대화하면서도, 필요한 정보는 충분히 제공하는 3단계 출력 모드 구현**

1. **ultra-compact**: AI 초고속 스캔 (98% 토큰 절감)
2. **compact**: AI 일반 분석 (92% 토큰 절감)
3. **full**: 개발자용 상세 분석 (기존 방식 유지)

---

## 🔴 현재 문제점

### 1. 과도한 정보량

**현재 출력 (일부):**

```json
{
  "filePath": "C:\\...\\EmlLabelPropertyService.java",
  "language": "java",
  "hash": "2ddf5bb6f76a08a068a3f5b8a3e5c4c87bd83caa",
  "lineCount": 272,
  "classes": [
    {
      "symbolId": "Class#com.naon.biz.mail.label.service.EmlLabelPropertyService|start:40|end:272",
      "kind": "class",
      "name": "EmlLabelPropertyService",
      "qualifiedName": "com.naon.biz.mail.label.service.EmlLabelPropertyService",
      "modifiers": ["public"],
      "extends": null,
      "implements": [],
      "startLine": 40,
      "endLine": 272,
      "javadoc": {
        "present": true,
        "startLine": 30,
        "endLine": 39,
        "lineCount": 10,
        "preview": "/**\n * 이메일 라벨 자동화 규칙 관리 서비스\n *..."
      },
      "fields": [
        {
          "symbolId": "Field#com.naon.biz.mail.label.service.EmlLabelPropertyService#labelRuleSupporter|start:47|end:47",
          "kind": "field",
          "name": "labelRuleSupporter",
          "typeText": "LabelRuleSupporter",
          "modifiers": ["private", "final"],
          "startLine": 47,
          "endLine": 47,
          "javadoc": { ... }
        }
      ],
      "methods": [
        {
          "symbolId": "Method#com.naon.biz.mail.label.service.EmlLabelPropertyService#selectDetailByMailUser(MailUser):LabelPropertyDetailDto|start:59|end:69",
          "kind": "method",
          "name": "selectDetailByMailUser",
          "returnTypeText": "LabelPropertyDetailDto",
          "modifiers": ["public"],
          "typeParamsText": null,
          "params": [
            {
              "name": "mailUser",
              "typeText": "MailUser"
            }
          ],
          "throws": [],
          "startLine": 59,
          "endLine": 69,
          "javadoc": { ... },
          "signatureText": "public LabelPropertyDetailDto selectDetailByMailUser(@NonNull MailUser mailUser)"
        }
      ]
    }
  ],
  "errors": []
}
```

**문제점:**

- ❌ `language`, `hash` - 불필요 (java 전용 도구)
- ❌ `qualifiedName` - 중복 (파일 경로에서 유추 가능)
- ❌ `kind` - 중복 (이미 배열 이름으로 알 수 있음)
- ❌ `modifiers`, `params` - signature에 이미 포함
- ❌ `symbolId` - 패키지 경로, 줄번호 등 중복 정보
- ❌ `javadoc.preview` - 전체 내용 (필요시 조회하면 됨)

### 2. 토큰 낭비

| 파일 크기 | JSON 출력 | 비율 |
| --------- | --------- | ---- |
| 200줄     | 610줄     | 305% |
| 500줄     | ~1,500줄  | 300% |

**AI 입장에서는:**

- "이 클래스가 뭐 하는지만 알고 싶은데..."
- "주요 메서드만 보고 싶은데..."
- "상세한 건 필요할 때 다시 물어볼게..."

---

## 🎯 설계 목표

### 핵심 원칙

1. **계층적 정보 제공**
   - Level 1 (ultra): 전체 개요 (15줄)
   - Level 2 (compact): 주요 정보 (50줄)
   - Level 3 (full): 모든 상세 정보 (610줄)

2. **AI 워크플로우 최적화**

   ```
   AI: "이 파일 뭐야?"
   → ultra-compact (15줄)

   AI: "changeRuleOrder 메서드 좀 더 자세히"
   → compact 모드 또는 range 읽기

   개발자: "모든 파라미터, 타입 정보 필요"
   → full 모드
   ```

3. **중복 제거**
   - 파일 경로에서 유추 가능한 정보 제거
   - signature에 포함된 정보 중복 제거
   - 배열 이름으로 알 수 있는 kind 제거

4. **필드명 축약**
   - `filePath` → `file`
   - `lineCount` → `lines`
   - `location` → `range`
   - `javadoc` → `doc`
   - `signature` → `sig`
   - `symbolId` → `id`

5. **유연한 필터링**
   - `--with-fields` / `--no-fields`
   - `--scope public` (접근 제한자 필터)

---

## 🚀 최종 설계안

### 모드 1: ultra-compact (AI 초고속 스캔)

**목적**: 파일 전체 구조를 한눈에 파악

**출력 예시:**

```json
{
  "file": "EmlLabelPropertyService.java",
  "lines": 272,
  "classes": [
    {
      "name": "EmlLabelPropertyService",
      "annotations": ["@Service", "@RequiredArgsConstructor"],
      "range": [30, 272],
      "methods": [
        "selectDetailByMailUser(MailUser) [53-69]",
        "changeRuleOrder(MailUser, List<String>) [82-93]",
        "saveLabelConfig(MailUser, String) [95-108]",
        "saveLabelRule(MailUser, LabelRule) [110-122]",
        "deleteLabelRule(MailUser, String) [126-137]",
        "onDeleteLabelEvent(LabelEvent.onDelete) [190-215]"
      ],
      "fields": [
        "LabelRuleSupporter labelRuleSupporter",
        "EmlLabelMapper emlLabelMapper"
      ]
    }
  ]
}
```

**특징:**

- ✅ 메서드: 이름 + 파라미터 타입 + 줄번호
- ✅ 필드: 타입 + 이름 (줄번호 없음)
- ✅ 클래스 어노테이션 포함
- ✅ javadoc 범위 포함 (range 시작 = javadoc 시작)
- ✅ **예상 줄 수**: ~15줄 (98% 감소)

---

### 모드 2: compact (AI 일반 분석)

**목적**: 각 심볼의 목적과 시그니처 파악

**출력 예시:**

```json
{
  "file": "EmlLabelPropertyService.java",
  "lines": 272,
  "classes": [
    {
      "name": "EmlLabelPropertyService",
      "annotations": ["@Service", "@RequiredArgsConstructor"],
      "range": [30, 272],
      "doc": "이메일 라벨 자동화 규칙 관리 서비스",
      "methods": [
        {
          "id": "53",
          "name": "selectDetailByMailUser",
          "sig": "public LabelPropertyDetailDto selectDetailByMailUser(@NonNull MailUser mailUser)",
          "range": [53, 69],
          "doc": "사용자의 라벨 속성을 상세 정보로 조회합니다."
        },
        {
          "id": "82",
          "name": "changeRuleOrder",
          "sig": "@Transactional public List<LabelRule> changeRuleOrder(@NonNull MailUser mailUser, @NonNull List<String> ruleIds)",
          "range": [82, 93],
          "doc": "라벨 자동화 규칙의 순서를 변경합니다."
        },
        {
          "id": "190",
          "name": "onDeleteLabelEvent",
          "sig": "@EventListener public void onDeleteLabelEvent(LabelEvent.onDelete event)",
          "range": [190, 215],
          "doc": "라벨 삭제 이벤트 처리 - 삭제된 라벨을 참조하는 규칙에서 해당 라벨 ID 제거"
        }
      ],
      "fields": [
        {
          "name": "labelRuleSupporter",
          "sig": "private final LabelRuleSupporter labelRuleSupporter",
          "doc": ""
        },
        {
          "name": "emlLabelMapper",
          "sig": "private final EmlLabelMapper emlLabelMapper",
          "doc": ""
        }
      ]
    }
  ]
}
```

**특징:**

- ✅ 메서드: 전체 시그니처 + javadoc 첫 줄 (trim)
- ✅ 필드: 전체 시그니처 + javadoc 전체 내용
- ✅ id: 시작 줄번호 (심볼 조회용)
- ✅ range: javadoc 시작 ~ 메서드 끝
- ✅ doc: javadoc 없으면 빈 문자열 `""`
- ✅ **예상 줄 수**: ~50줄 (92% 감소)

---

### 모드 3: full (개발자용 상세 분석)

**목적**: 모든 상세 정보 제공 (현재 방식 유지)

**특징:**

- ✅ 모든 필드 포함 (kind, modifiers, params, throws 등)
- ✅ 긴 symbolId 유지
- ✅ javadoc preview 포함
- ✅ **예상 줄 수**: ~610줄

---

## 📐 구현 명세

### 1. 디렉토리 구조

```
java-analyzer/
├── parser/
│   ├── indexer.py              # 수정 필요
│   ├── formatters.py           # 🆕 신규 생성
│   └── ...
└── cli/
    └── main.py                 # 수정 필요
```

### 2. 신규 파일: `parser/formatters.py`

**목적**: 출력 모드별 JSON 포맷팅

```python
"""
출력 모드별 JSON 포맷터
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
            "annotations": _extract_class_annotations(cls),
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
            "annotations": _extract_class_annotations(cls),
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
    return file_path.split("\\")[-1].split("/")[-1]


def _extract_class_annotations(cls: Dict[str, Any]) -> List[str]:
    """
    클래스 레벨 어노테이션 추출

    중요한 어노테이션만 추출:
    - Spring: @Service, @Component, @Repository, @Controller, @RestController, @Configuration
    - Lombok: @Data, @Getter, @Setter, @Builder, @RequiredArgsConstructor, etc.
    - Transaction: @Transactional
    - Validation: @Validated
    """
    # TODO: modifiers에서 어노테이션 추출 또는 signature 파싱
    # 현재 modifiers는 ["public"] 같은 접근 제한자만 포함
    # signature에서 파싱 필요: "public class ..." → 앞에 @* 추출
    pass


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
        cleaned = line.strip().lstrip("/*").lstrip("*").strip()
        if cleaned:
            return cleaned

    return ""


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

        result.append({
            "name": field["name"],
            "sig": field.get("signatureText", f"{' '.join(field['modifiers'])} {field['typeText']} {field['name']}"),
            "doc": javadoc_content
        })

    return result


def _get_full_javadoc_content(javadoc: Optional[Dict[str, Any]]) -> str:
    """javadoc 전체 내용 반환 (필드용)"""
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


def _is_in_scope(modifiers: List[str], scope: str) -> bool:
    """접근 제한자 필터링"""
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
```

### 3. 수정 파일: `cli/main.py`

**변경 사항:**

```python
# 기존 import
from parser.indexer import find_symbols, index_java_file
from parser.readers import read_range

# 🆕 추가 import
from parser.formatters import format_ultra_compact, format_compact


def main() -> None:
    parser = argparse.ArgumentParser(prog="java-analyzer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    index_parser = subparsers.add_parser("index", help="Index a Java file")
    index_parser.add_argument("file", help="Path to Java file")

    # 🆕 출력 모드 옵션
    index_parser.add_argument(
        "--mode",
        choices=["ultra", "compact", "full"],
        default="ultra",
        help="Output mode: ultra (minimal), compact (medium), full (detailed)"
    )

    # 🆕 필드 포함 옵션
    index_parser.add_argument(
        "--with-fields",
        action="store_true",
        default=True,
        help="Include field information (default: True)"
    )
    index_parser.add_argument(
        "--no-fields",
        dest="with_fields",
        action="store_false",
        help="Exclude field information"
    )

    # 🆕 접근 제한자 필터
    index_parser.add_argument(
        "--scope",
        choices=["public", "protected", "private", "all"],
        default="all",
        help="Filter by access modifier (default: all)"
    )

    # 기존 옵션들 (full 모드에서만 유효)
    index_parser.add_argument("--no-private", action="store_true", help="Exclude private symbols")
    index_parser.add_argument("--no-fields", action="store_true", help="Exclude fields")
    index_parser.add_argument("--no-inner", action="store_true", help="Exclude inner classes")
    index_parser.add_argument("--no-constructors", action="store_true", help="Exclude constructors")
    index_parser.add_argument(
        "--javadoc-preview-chars", type=int, default=0, help="Include Javadoc preview chars"
    )

    # ... range_parser, find_parser 동일 ...

    args = parser.parse_args()

    if args.command == "index":
        # Full 모드 옵션 (기존 방식)
        full_options = {
            "includePrivate": not args.no_private,
            "includeFields": not getattr(args, 'no_fields', False),
            "includeInnerClasses": not args.no_inner,
            "includeConstructors": not args.no_constructors,
            "maxJavadocPreviewChars": args.javadoc_preview_chars,
        }

        # 먼저 full 모드로 인덱싱
        full_result = index_java_file(args.file, full_options)

        # 🆕 모드에 따라 포맷팅
        if args.mode == "ultra":
            format_options = {
                "with_fields": args.with_fields,
                "scope": args.scope
            }
            result = format_ultra_compact(full_result, format_options)
        elif args.mode == "compact":
            format_options = {
                "with_fields": args.with_fields,
                "scope": args.scope
            }
            result = format_compact(full_result, format_options)
        else:  # full
            result = full_result

        _print_json(result)
        return

    # ... range, find 동일 ...
```

### 4. 어노테이션 추출 방법

**문제**: 현재 `modifiers`는 접근 제한자만 포함 (`["public"]`)

**해결책**: `signatureText`에서 어노테이션 추출

```python
def _extract_class_annotations(cls: Dict[str, Any]) -> List[str]:
    """
    signatureText에서 어노테이션 추출

    Example:
        Input: "@Service @RequiredArgsConstructor public class UserService"
        Output: ["@Service", "@RequiredArgsConstructor"]
    """
    sig = cls.get("signatureText", "")
    if not sig:
        return []

    annotations = []
    tokens = sig.split()

    for token in tokens:
        if token.startswith("@"):
            annotations.append(token)
        elif token in ["public", "private", "protected", "class", "interface"]:
            # 어노테이션 영역 종료
            break

    return annotations
```

**대안**: Tree-sitter AST에서 직접 추출 (더 정확)

```python
# parser/indexer.py의 _parse_class_declaration() 수정
def _parse_class_declaration(node, ctx: ParseContext, outer_names: list[str]) -> Optional[dict]:
    # ... 기존 코드 ...

    # 🆕 어노테이션 추출
    annotations = _extract_annotations(node, ctx.source_bytes)

    return {
        # ... 기존 필드들 ...
        "annotations": annotations,  # 🆕 추가
    }


def _extract_annotations(node, source_bytes: bytes) -> List[str]:
    """
    AST에서 어노테이션 노드 추출
    """
    annotations = []

    for child in node.children:
        if child.type == "marker_annotation":
            # @Service
            name_node = child.child_by_field_name("name")
            if name_node:
                annotations.append("@" + node_text(source_bytes, name_node))
        elif child.type == "annotation":
            # @RequestMapping("/api")
            name_node = child.child_by_field_name("name")
            if name_node:
                annotations.append("@" + node_text(source_bytes, name_node))

    return annotations
```

### 5. Javadoc Range 처리

**현재**: `startLine`, `endLine` 별도

**변경**:

```python
def _get_range_with_javadoc(symbol: Dict[str, Any]) -> List[int]:
    """
    javadoc이 있으면 javadoc 시작부터,
    없으면 심볼 시작부터 range 반환
    """
    javadoc = symbol.get("javadoc", {})

    if javadoc.get("present") and javadoc.get("startLine"):
        start = javadoc["startLine"]
    else:
        start = symbol["startLine"]

    return [start, symbol["endLine"]]
```

---

## 🤖 AI를 위한 작업 지시서

### 작업 개요

**목표**: `java-analyzer`에 3가지 출력 모드 추가

- `--mode ultra`: 초간단 (15줄)
- `--mode compact`: 중간 (50줄)
- `--mode full`: 상세 (610줄, 기존 유지)

**예상 소요 시간**: 2-3시간

**우선순위**: 🔥 최우선

---

### 작업 순서

#### 1단계: 신규 파일 생성 (30분)

**파일**: `java-analyzer/parser/formatters.py`

**작업 내용**:

1. 위의 [구현 명세 - 2. 신규 파일] 섹션의 코드를 복사하여 생성
2. 함수별로 TODO 주석 확인하고 구현
   - `_extract_class_annotations()` - 어노테이션 추출
   - `_get_javadoc_first_line()` - javadoc 첫 줄만
   - `_get_full_javadoc_content()` - javadoc 전체 내용

**검증**:

```python
# 테스트 코드
from parser.indexer import index_java_file
from parser.formatters import format_ultra_compact, format_compact

# Full 모드로 인덱싱
full_data = index_java_file("tests/fixtures/SimpleClass.java", {})

# Ultra로 포맷
ultra_data = format_ultra_compact(full_data, {"with_fields": True, "scope": "all"})
print(len(str(ultra_data).split("\n")))  # 15줄 정도 나와야 함

# Compact으로 포맷
compact_data = format_compact(full_data, {"with_fields": True, "scope": "all"})
print(len(str(compact_data).split("\n")))  # 50줄 정도 나와야 함
```

---

#### 2단계: CLI 수정 (30분)

**파일**: `java-analyzer/cli/main.py`

**작업 내용**:

1. 위의 [구현 명세 - 3. 수정 파일] 섹션 참고하여 수정
2. import 추가
3. argparse에 `--mode`, `--with-fields`, `--scope` 옵션 추가
4. index 명령어 핸들러에서 모드별 포맷팅 호출

**주의사항**:

- 기존 `--no-fields` 옵션과 충돌 방지
- Full 모드는 기존 방식 그대로 유지

**검증**:

```powershell
# Ultra 모드
python -m cli.main index tests\fixtures\SimpleClass.java --mode ultra

# Compact 모드
python -m cli.main index tests\fixtures\SimpleClass.java --mode compact

# Full 모드 (기존 방식)
python -m cli.main index tests\fixtures\SimpleClass.java --mode full
```

---

#### 3단계: 어노테이션 추출 구현 (1시간)

**옵션 A (간단)**: signatureText 파싱

**파일**: `parser/formatters.py`의 `_extract_class_annotations()`

```python
def _extract_class_annotations(cls: Dict[str, Any]) -> List[str]:
    sig = cls.get("signatureText", "")
    if not sig:
        return []

    annotations = []
    for token in sig.split():
        if token.startswith("@"):
            annotations.append(token)
        elif token in ["public", "private", "protected", "class", "interface"]:
            break

    return annotations
```

**옵션 B (정확)**: AST에서 직접 추출

**파일**: `parser/indexer.py`

1. 기존 `_parse_class_declaration()` 함수 수정
2. `_extract_annotations()` 함수 추가 (위의 구현 명세 참고)
3. 반환 dict에 `"annotations"` 필드 추가

**검증**:

```python
result = index_java_file("tests/fixtures/AnnotatedClass.java", {})
print(result["classes"][0]["annotations"])
# 예상: ["@Service", "@RequiredArgsConstructor"]
```

---

#### 4단계: 필드 처리 개선 (30분)

**파일**: `parser/formatters.py`

**작업 내용**:

1. `_format_fields_ultra()` - 줄번호 없이 타입+이름만
2. `_format_fields_compact()` - javadoc 전체 내용 포함

**테스트 케이스 작성**:

`tests/fixtures/DtoClass.java`:

```java
package com.test;

/**
 * 사용자 DTO
 */
public class UserDto {
    /**
     * 사용자 ID
     * 시스템 고유 식별자
     */
    @JsonProperty("user_id")
    private String userId;

    @NotNull
    private String userName;
}
```

**검증**:

```python
result = index_java_file("tests/fixtures/DtoClass.java", {})

# Ultra
ultra = format_ultra_compact(result, {"with_fields": True})
print(ultra["classes"][0]["fields"])
# 예상: ["String userId", "String userName"]

# Compact
compact = format_compact(result, {"with_fields": True})
print(compact["classes"][0]["fields"][0]["doc"])
# 예상: "사용자 ID\n시스템 고유 식별자"
```

---

#### 5단계: 통합 테스트 (30분)

**테스트 파일**: `tests/test_formatters.py`

```python
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

    # 클래스 정보 확인
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
        assert "[" in cls["methods"][0]  # 줄번호 포함 확인

    # 필드 형식 확인 (문자열 배열)
    assert isinstance(cls["fields"], list)


def test_compact_mode():
    """compact 모드 테스트"""
    full_data = index_java_file("tests/fixtures/SimpleClass.java", {})
    compact_data = format_compact(full_data, {"with_fields": True, "scope": "all"})

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


def test_scope_filter():
    """접근 제한자 필터 테스트"""
    full_data = index_java_file("tests/fixtures/SimpleClass.java", {})

    # public만
    public_only = format_ultra_compact(full_data, {"scope": "public"})

    # private 메서드가 제외되었는지 확인
    method_names = [m.split("(")[0] for m in public_only["classes"][0]["methods"]]
    # private 메서드가 원본에 있다면, public_only에는 없어야 함


def test_no_fields_option():
    """필드 제외 옵션 테스트"""
    full_data = index_java_file("tests/fixtures/SimpleClass.java", {})

    no_fields = format_ultra_compact(full_data, {"with_fields": False})

    # fields 키가 없어야 함
    assert "fields" not in no_fields["classes"][0]


def test_token_reduction():
    """토큰 절감 효과 확인"""
    full_data = index_java_file("tests/fixtures/SimpleClass.java", {})
    ultra_data = format_ultra_compact(full_data, {"with_fields": True})
    compact_data = format_compact(full_data, {"with_fields": True})

    import json
    full_str = json.dumps(full_data, ensure_ascii=False, indent=2)
    ultra_str = json.dumps(ultra_data, ensure_ascii=False, indent=2)
    compact_str = json.dumps(compact_data, ensure_ascii=False, indent=2)

    full_lines = len(full_str.split("\n"))
    ultra_lines = len(ultra_str.split("\n"))
    compact_lines = len(compact_str.split("\n"))

    print(f"Full: {full_lines} lines")
    print(f"Ultra: {ultra_lines} lines ({100 - ultra_lines/full_lines*100:.1f}% reduction)")
    print(f"Compact: {compact_lines} lines ({100 - compact_lines/full_lines*100:.1f}% reduction)")

    # Ultra는 최소 80% 이상 절감
    assert ultra_lines < full_lines * 0.2

    # Compact은 최소 50% 이상 절감
    assert compact_lines < full_lines * 0.5
```

**실행**:

```powershell
python -m pytest tests/test_formatters.py -v
```

---

### 완료 체크리스트

- [ ] `parser/formatters.py` 생성 완료
- [ ] `cli/main.py` 수정 완료
- [ ] 어노테이션 추출 구현 완료
- [ ] 필드 처리 구현 완료
- [ ] 테스트 작성 및 통과
- [ ] README.md 업데이트 (사용 예시 추가)
- [ ] 실제 파일로 검증 (EmlLabelPropertyService.java)

---

### 검증 방법

**실제 파일로 테스트**:

```powershell
# Ultra 모드
python -m cli.main index "C:\Users\hokkk\work\GW8\mail-api-server\mail-service\src\main\java\com\naon\biz\mail\label\service\EmlLabelPropertyService.java" --mode ultra > ultra.json

# Compact 모드
python -m cli.main index "C:\Users\hokkk\work\GW8\mail-api-server\mail-service\src\main\java\com\naon\biz\mail\label\service\EmlLabelPropertyService.java" --mode compact > compact.json

# Full 모드
python -m cli.main index "C:\Users\hokkk\work\GW8\mail-api-server\mail-service\src\main\java\com\naon\biz\mail\label\service\EmlLabelPropertyService.java" --mode full > full.json

# 줄 수 비교
wc -l ultra.json compact.json full.json
```

**예상 결과**:

- `ultra.json`: ~15줄
- `compact.json`: ~50줄
- `full.json`: ~610줄

---

## 🧪 테스트 시나리오

### 시나리오 1: Service 클래스 분석

**파일**: `EmlLabelPropertyService.java` (272줄)

**Ultra 모드**:

```json
{
  "file": "EmlLabelPropertyService.java",
  "lines": 272,
  "classes": [{
    "name": "EmlLabelPropertyService",
    "annotations": ["@Service", "@RequiredArgsConstructor"],
    "range": [30, 272],
    "methods": [
      "selectDetailByMailUser(MailUser) [53-69]",
      "changeRuleOrder(MailUser, List<String>) [82-93]",
      ...
    ],
    "fields": [
      "LabelRuleSupporter labelRuleSupporter",
      "EmlLabelMapper emlLabelMapper"
    ]
  }]
}
```

**AI 사용 예**:

```
AI: "이 서비스가 뭐 하는 거야?"
→ ultra 모드로 15줄 읽음 → "라벨 자동화 규칙 관리하는 서비스구나"

AI: "changeRuleOrder 메서드 좀 더 자세히"
→ compact 모드 또는 range [82-93] 읽기

AI: "실제 구현 코드 봐야 해"
→ range [82-93] 읽기
```

---

### 시나리오 2: DTO 클래스 분석

**파일**: `UserDto.java`

**Compact 모드 (필드 중요)**:

```json
{
  "file": "UserDto.java",
  "classes": [
    {
      "name": "UserDto",
      "annotations": ["@Data", "@Builder"],
      "doc": "사용자 정보 DTO",
      "fields": [
        {
          "name": "userId",
          "sig": "@JsonProperty(\"user_id\") private String userId",
          "doc": "사용자 ID\n시스템 고유 식별자"
        },
        {
          "name": "userName",
          "sig": "@NotNull private String userName",
          "doc": "사용자 이름"
        }
      ],
      "methods": []
    }
  ]
}
```

---

### 시나리오 3: 접근 제한자 필터

**Public 메서드만**:

```powershell
python -m cli.main index Service.java --mode ultra --scope public
```

**결과**: private, protected 메서드 제외

---

## 📚 참고 자료

### 관련 파일

1. **현재 인덱서**: `java-analyzer/parser/indexer.py`
   - `index_java_file()` - Full 모드 출력
   - `_parse_class_declaration()` - 클래스 파싱
   - `_parse_method_declaration()` - 메서드 파싱

2. **현재 CLI**: `java-analyzer/cli/main.py`
   - `main()` - argparse 설정
   - index 명령어 핸들러

3. **테스트 파일**: `java-analyzer/tests/fixtures/`
   - `SimpleClass.java` - 기본 테스트용

### Tree-sitter 어노테이션 노드

```
marker_annotation: @Service
annotation: @RequestMapping("/api")
  - name: RequestMapping
  - arguments: (...)
```

### JSON 출력 예시

**Full 모드 (기존)**:

- 파일: [java-analyzer/analysis.json](../java-analyzer/analysis.json)
- 줄 수: 611줄

---

## ⚠️ 주의사항

### 1. 하위 호환성

**기존 사용자를 위해**:

- Full 모드는 기존 출력 형식 그대로 유지
- 기존 `--no-fields` 등의 옵션도 그대로 동작

### 2. symbolId 호환성

**기존 기능과의 연동**:

- `java_read_javadoc(symbolId)` 같은 함수는 여전히 full symbolId 필요
- Compact 모드의 `id`는 줄번호만 (`"53"`)
- 필요시 full symbolId로 확장하는 로직 추가

```python
def expand_compact_id(compact_id: str, file_path: str, class_name: str, method_name: str):
    """
    Compact ID를 Full symbolId로 확장

    Args:
        compact_id: "53" (줄번호)
        file_path: 파일 경로
        class_name: 클래스명
        method_name: 메서드명

    Returns:
        "Method#com.naon...#methodName(...)...|start:53|end:69"
    """
    # Full 모드로 다시 인덱싱 또는 캐시에서 조회
    pass
```

### 3. 성능

**두 번 파싱하지 않기**:

- Full 모드로 먼저 인덱싱
- 결과를 포맷만 변경 (파싱은 한 번만)

### 4. Javadoc Range

**변경 사항 주의**:

- 기존: `doc: [53, 58]`, `range: [59, 69]`
- 신규: `range: [53, 69]` (javadoc 포함)
- 이것이 기존 기능에 영향 주는지 확인 필요

---

## 🎉 예상 효과

### 토큰 절감

| 모드    | 줄 수  | 절감율 | 용도              |
| ------- | ------ | ------ | ----------------- |
| ultra   | ~15줄  | 98%    | AI 빠른 스캔      |
| compact | ~50줄  | 92%    | AI 일반 분석      |
| full    | ~610줄 | 0%     | 개발자, 상세 분석 |

### AI 워크플로우 개선

**Before**:

```
AI: "이 파일 분석해줘" → 610줄 읽음 → 토큰 폭발 💥
```

**After**:

```
AI: "이 파일 뭐야?" → ultra (15줄) → "라벨 관리 서비스구나"
AI: "changeRuleOrder 메서드 자세히" → compact 또는 range → "규칙 순서 변경하는구나"
AI: "실제 코드 봐야 해" → range 읽기 → 구현 확인
```

---

## 📝 작업 체크리스트 (AI용)

### 시작 전 확인

- [ ] Python 3.10+ 설치 확인
- [ ] 의존성 설치: `pip install -r requirements.txt`
- [ ] 현재 디렉토리: `java-analyzer/`
- [ ] 기존 테스트 통과 확인: `pytest tests/`

### 구현 단계

- [ ] 1단계: `parser/formatters.py` 생성
  - [ ] `format_ultra_compact()` 구현
  - [ ] `format_compact()` 구현
  - [ ] 헬퍼 함수들 구현
  - [ ] 간단한 테스트로 검증

- [ ] 2단계: `cli/main.py` 수정
  - [ ] import 추가
  - [ ] argparse 옵션 추가
  - [ ] 모드별 포맷팅 로직 추가
  - [ ] CLI로 실행 테스트

- [ ] 3단계: 어노테이션 추출
  - [ ] 방법 선택 (signatureText vs AST)
  - [ ] 구현
  - [ ] 테스트

- [ ] 4단계: 필드 처리
  - [ ] Ultra 모드 필드 포맷
  - [ ] Compact 모드 필드 포맷
  - [ ] Javadoc 전체 내용 추출
  - [ ] 테스트

- [ ] 5단계: 통합 테스트
  - [ ] `tests/test_formatters.py` 작성
  - [ ] 모든 테스트 통과
  - [ ] 실제 파일로 검증

### 문서화

- [ ] README.md 업데이트
  - [ ] 출력 모드 설명 추가
  - [ ] 사용 예시 추가
  - [ ] Before/After 비교

- [ ] SETUP.md 업데이트 (필요시)

### 최종 확인

- [ ] 실제 Java 파일로 테스트
- [ ] 토큰 절감 효과 확인 (90%+ 목표)
- [ ] 기존 기능 정상 동작 확인
- [ ] 코드 리뷰 (가능하면)

---

**이 문서를 읽은 AI는 바로 작업을 시작할 수 있습니다!** 🚀

문의사항이나 불명확한 부분이 있으면 이 설계서를 참고하여 판단하거나, 사용자에게 질문하세요.
