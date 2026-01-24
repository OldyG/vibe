# Parser 컴포넌트

Parser 컴포넌트는 MCP Java Indexer의 핵심으로, Tree-sitter를 사용하여 Java 소스 코드를 분석하고 심볼 정보를 추출합니다.

## 📁 파일 구조

```
parser/
├── __init__.py           # 패키지 초기화
├── indexer.py            # 메인 인덱싱 엔진 (615줄)
├── ast_utils.py          # AST 유틸리티 함수 (112줄)
├── javadoc.py            # Javadoc 탐지 및 추출 (77줄)
└── readers.py            # 파일 I/O 및 범위 읽기 (123줄)
```

---

## indexer.py

### 개요
Java AST를 파싱하고 클래스, 메서드, 필드, 생성자 등의 심볼을 추출하는 메인 엔진입니다.

### 핵심 함수

#### `index_java_file(file_path, options, cache_store)`
메인 진입점. Java 파일을 인덱싱하여 심볼 정보를 반환합니다.

**처리 흐름**:
1. 파일 읽기 및 해시 계산
2. 캐시 확인
3. Tree-sitter로 파싱
4. AST 순회 및 심볼 추출
5. 에러 수집
6. 결과 캐싱 및 반환

**코드 위치**: `/home/user/vibe/mcp-java-indexer/parser/indexer.py:451-505`

```python
def index_java_file(file_path: str, options: Optional[dict] = None,
                    cache_store: Optional[CacheStore] = None) -> dict:
    """
    Java 파일을 인덱싱하여 심볼 정보를 추출합니다.

    Args:
        file_path: 인덱싱할 Java 파일 경로
        options: 인덱싱 옵션 (includePrivate, includeFields 등)
        cache_store: 캐시 스토어 (None이면 기본 캐시 사용)

    Returns:
        {
            "filePath": str,
            "language": "java",
            "hash": str,
            "lineCount": int,
            "classes": [...],
            "errors": [...]
        }
    """
```

#### `_parse_class_declaration(node, ctx, outer_names)`
클래스 선언을 파싱하여 클래스 객체를 생성합니다.

**지원하는 종류**:
- `class_declaration` → `"class"`
- `interface_declaration` → `"interface"`
- `enum_declaration` → `"enum"`
- `record_declaration` → `"record"`
- `annotation_type_declaration` → `"annotation"`

**코드 위치**: `indexer.py:380-429`

**주요 처리**:
1. 클래스 종류 판별
2. 이름 및 한정된 이름(qualified name) 추출
3. 접근 제어자(modifiers) 추출
4. extends/implements 추출
5. Javadoc 탐지
6. 클래스 바디 파싱 (필드, 메서드, 생성자, 내부 클래스)

#### `_parse_method_declaration(node, ctx, qualified_name)`
메서드 선언을 파싱합니다.

**코드 위치**: `indexer.py:286-335`

**추출 정보**:
- 메서드 이름
- 반환 타입 (`void` 포함)
- 타입 파라미터 (`<T extends Foo>`)
- 파라미터 목록 (이름, 타입)
- throws 절
- 접근 제어자
- 시그니처 텍스트

**예시**:
```java
public <T> Result doSomething(int x, String y) throws IOException
```
↓
```json
{
  "name": "doSomething",
  "returnTypeText": "Result",
  "typeParamsText": "<T>",
  "params": [
    {"name": "x", "typeText": "int"},
    {"name": "y", "typeText": "String"}
  ],
  "throws": ["IOException"]
}
```

#### `_parse_constructor_declaration(node, ctx, qualified_name)`
생성자 선언을 파싱합니다.

**코드 위치**: `indexer.py:253-283`

**특별 처리**:
- 일반 생성자 (`constructor_declaration`)
- 컴팩트 생성자 (`compact_constructor_declaration`) - record용

#### `_parse_field_declaration(node, ctx, qualified_name)`
필드 선언을 파싱합니다.

**코드 위치**: `indexer.py:211-250`

**특징**:
- 한 선언에 여러 변수 가능 (예: `int a, b, c;`)
- 각 변수를 별도의 필드 객체로 반환

**예시**:
```java
private static int count = 0, max = 100;
```
↓
```json
[
  {"name": "count", "typeText": "int", "startLine": 20, "endLine": 20},
  {"name": "max", "typeText": "int", "startLine": 20, "endLine": 20}
]
```

#### `_parse_class_body(body_node, ctx, qualified_name, outer_names)`
클래스 바디를 순회하며 멤버를 추출합니다.

**코드 위치**: `indexer.py:338-377`

**처리 멤버**:
- 필드 (`field_declaration`)
- 메서드 (`method_declaration`)
- 생성자 (`constructor_declaration`, `compact_constructor_declaration`)
- 내부 클래스 (재귀적 처리)
- Enum 바디 (`enum_body_declarations`)

#### `find_symbol_by_id(index_data, symbol_id)`
인덱스 데이터에서 특정 심볼 ID를 찾습니다.

**코드 위치**: `indexer.py:533-537`

**사용처**: `java_read_javadoc`에서 심볼 위치 찾기

#### `find_symbols(root_dir, query, options)`
디렉토리를 재귀적으로 탐색하며 쿼리에 매칭되는 심볼을 찾습니다.

**코드 위치**: `indexer.py:567-614`

**처리 흐름**:
1. `root_dir`에서 `*.java` 파일 재귀 탐색 (`Path.rglob`)
2. 각 파일 인덱싱 (캐시 활용)
3. 쿼리 매칭 (`find_symbols_in_file`)
4. 결과 수집 (`maxResults`까지)

### 헬퍼 함수

#### 심볼 ID 생성

```python
def _build_symbol_id(prefix: str, class_name: str, detail: str,
                     start: int, end: int) -> str:
    return f"{prefix}#{class_name}#{detail}|start:{start}|end:{end}"
```

**예시**:
- Method: `Method#com.foo.Bar#doThing(int,String):Result|start:70|end:120`
- Field: `Field#com.foo.Bar#count|start:20|end:20`
- Ctor: `Ctor#com.foo.Bar#Bar(int)|start:30|end:35`

#### 타입 추출

```python
def _type_text(node, source_bytes: bytes) -> str:
    """AST 노드에서 타입 텍스트를 추출하고 공백을 정규화합니다."""
```

다중 라인 타입도 한 줄로 변환:
```java
Map<String,
    List<Integer>>
```
↓
```
"Map<String, List<Integer>>"
```

#### 시그니처 추출

```python
def _signature_text(node, source_bytes: bytes) -> str:
    """메서드/생성자의 시그니처를 추출합니다 (바디 제외)."""
```

**처리**:
- 바디(`{...}`) 이전까지만 추출
- 세미콜론(`;`) 제거
- 공백 정규화

---

## ast_utils.py

### 개요
Tree-sitter AST 노드를 다루는 유틸리티 함수 모음입니다.

### 핵심 함수

#### `node_text(source_bytes, node)`
AST 노드의 텍스트를 추출합니다.

```python
def node_text(source_bytes: bytes, node) -> str:
    """노드의 바이트 범위를 사용하여 소스 코드에서 텍스트를 추출합니다."""
    return source_bytes[node.start_byte : node.end_byte].decode(
        "utf-8", errors="replace"
    )
```

#### `extract_modifiers(source_bytes, node)`
Java 접근 제어자를 추출합니다.

**지원 제어자**:
```python
JAVA_MODIFIERS = {
    "public", "private", "protected",
    "static", "final", "abstract",
    "synchronized", "native", "strictfp",
    "transient", "volatile", "default"
}
```

**코드 위치**: `ast_utils.py:16-37`

**처리 방식**:
1. 노드의 모든 자식 순회
2. `modifiers` 타입 노드 찾기
3. 자식 노드 중 제어자 키워드 수집

#### `normalize_whitespace(text)`
다중 라인 텍스트를 한 줄로 정규화합니다.

```python
def normalize_whitespace(text: str) -> str:
    """연속된 공백을 하나의 공백으로 합치고 trim합니다."""
    return " ".join(text.split()).strip()
```

**예시**:
```java
Map<String,
    List<Integer>>  value
```
↓
```
"Map<String, List<Integer>> value"
```

#### `split_top_level_commas(text)`
최상위 레벨의 쉼표로 분리합니다 (제네릭 내부 쉼표 무시).

**코드 위치**: `ast_utils.py:56-84`

**처리**:
- `<`, `>` 괄호 추적
- 최상위 레벨에서만 쉼표로 분리

**예시**:
```python
split_top_level_commas("Comparable<T>, Serializable")
# → ["Comparable<T>", "Serializable"]

split_top_level_commas("Map<K,V>, List<T>")
# → ["Map<K,V>", "List<T>"]  # Map 내부의 쉼표는 무시
```

#### `modifier_anchor_line(node)`
접근 제어자의 시작 라인을 반환합니다.

**용도**: Javadoc 탐지 시 올바른 앵커 라인 찾기

```python
@Override  # 애노테이션
public void foo()  # ← 이 라인이 anchor
```

---

## javadoc.py

### 개요
Javadoc 주석을 탐지하고 추출하는 모듈입니다.

### 핵심 함수

#### `find_javadoc(lines, symbol_line_1based)`
심볼 앞의 Javadoc 블록을 찾습니다.

**코드 위치**: `javadoc.py:11-49`

**탐지 규칙**:
1. `symbol_line` 바로 위부터 역방향 탐색
2. 빈 줄은 건너뜀
3. `*/`로 끝나는 주석 블록 찾기
4. `/**`로 시작하는지 확인 (그렇지 않으면 무시)
5. 시작/종료 라인 반환

**예시**:
```java
/**
 * This is a method.
 */
@Override
public void foo() {  // ← symbol_line
```
→ Javadoc: 라인 1-3

**비 Javadoc 주석은 무시**:
```java
/* regular block comment */
// single line comment
public void foo() {
```
→ Javadoc 없음 (found: false)

#### `build_javadoc_dict(lines, anchor_line, max_preview_chars)`
Javadoc 메타데이터 객체를 생성합니다.

**반환 형식**:
```python
{
    "present": bool,
    "startLine": int | None,
    "endLine": int | None,
    "lineCount": int,
    "preview": str | None  # max_preview_chars > 0인 경우
}
```

**코드 위치**: `javadoc.py:52-77`

---

## readers.py

### 개요
파일에서 특정 라인 범위를 읽거나 Javadoc을 추출하는 I/O 모듈입니다.

### 핵심 함수

#### `read_range(file_path, start_line, end_line, options)`
파일의 특정 라인 범위를 읽습니다.

**코드 위치**: `readers.py:10-51`

**처리 흐름**:
1. 파일 읽기 (UTF-8, 오류 시 replace)
2. 라인 범위 검증 및 조정
3. 지정된 범위 추출
4. 라인 번호 추가 (옵션)
5. `maxChars` 제한 적용

**라인 번호 형식**:
```
50: public void foo() {
51:     System.out.println("Hello");
52: }
```

**문자 수 제한**:
```python
if len(content) > max_chars:
    content = content[:max_chars] + f"\n... (truncated at {max_chars} chars)"
```

#### `read_javadoc(file_path, symbol_id, options, cache_store)`
심볼의 Javadoc만 읽습니다.

**코드 위치**: `readers.py:54-123`

**처리 흐름**:
1. 파일 인덱싱 (캐시 활용)
2. `symbol_id`로 심볼 찾기
3. 심볼에 Javadoc 있는지 확인
4. Javadoc 라인 범위 읽기
5. 결과 반환

**캐시 활용**:
- `index_java_file`을 호출하므로 인덱싱 캐시 재사용
- 동일 파일의 여러 심볼 Javadoc 읽기 시 효율적

---

## 데이터 구조

### ParseContext
파싱 중 공유되는 컨텍스트 정보입니다.

```python
@dataclass
class ParseContext:
    source_bytes: bytes      # 원본 소스 코드 (바이트)
    lines: list[str]         # 라인 단위로 분리된 소스 코드
    package_name: str        # 패키지 이름
    options: dict            # 인덱싱 옵션
```

**사용처**: 모든 파싱 함수에 전달되어 공통 데이터 공유

---

## Tree-sitter 사용법

### Parser 초기화
```python
from tree_sitter import Language, Parser
import tree_sitter_java

_JAVA_LANGUAGE = Language(tree_sitter_java.language())
_PARSER = Parser(_JAVA_LANGUAGE)
```

**전역 변수**: 파서는 전역 싱글톤으로 재사용 (성능 최적화)

### AST 파싱
```python
tree = _PARSER.parse(source_bytes)
root = tree.root_node  # 루트 노드 (program)
```

### 노드 탐색
```python
# 자식 노드 순회
for child in node.named_children:
    if child.type == "class_declaration":
        process_class(child)

# 필드로 접근
name_node = node.child_by_field_name("name")
type_node = node.child_by_field_name("type")

# 위치 정보
start_line = node.start_point[0] + 1  # 0-based → 1-based
end_line = node.end_point[0] + 1
```

### 주요 노드 타입

| 노드 타입 | 설명 |
|----------|------|
| `program` | 루트 노드 |
| `package_declaration` | 패키지 선언 |
| `class_declaration` | 클래스 |
| `interface_declaration` | 인터페이스 |
| `enum_declaration` | Enum |
| `record_declaration` | Record |
| `annotation_type_declaration` | 애노테이션 타입 |
| `method_declaration` | 메서드 |
| `constructor_declaration` | 생성자 |
| `field_declaration` | 필드 |
| `modifiers` | 접근 제어자 |
| `formal_parameters` | 파라미터 목록 |
| `type_parameters` | 제네릭 타입 파라미터 |
| `throws` | throws 절 |

---

## 에러 처리

### 파싱 에러 수집
```python
def _collect_errors(node) -> list[dict]:
    """AST에서 ERROR 노드를 찾아 수집합니다."""
    errors: list[dict] = []

    def walk(n):
        if n.type == "ERROR":
            errors.append({
                "level": "error",
                "message": "Parse error",
                "line": n.start_point[0] + 1,
            })
        for child in n.children:
            walk(child)

    walk(node)
    return errors
```

**코드 위치**: `indexer.py:432-448`

### 파일 읽기 에러
```python
try:
    source_bytes = _read_file_bytes(file_path)
except Exception as exc:
    return {
        "filePath": file_path,
        "language": "java",
        "hash": "",
        "lineCount": 0,
        "classes": [],
        "errors": [{
            "level": "error",
            "message": f"Failed to read file: {exc}",
            "line": None,
        }],
    }
```

**철학**: 절대 크래시하지 않고, 가능한 정보와 함께 에러 기록

---

## 성능 최적화

### 1. 전역 Parser 재사용
```python
_PARSER = Parser(_JAVA_LANGUAGE)  # 한 번만 생성
```

### 2. 캐싱 통합
```python
def index_java_file(..., cache_store: Optional[CacheStore] = None):
    cache = cache_store or default_cache_store()
    cached = cache.load(file_path, content_hash, options_key)
    if cached is not None:
        return cached  # ← 빠른 종료
```

### 3. Early Exit
```python
# find_symbols: maxResults 도달 시 즉시 종료
if len(results) >= max_results:
    break
```

### 4. 효율적인 텍스트 추출
```python
# 바이트 슬라이싱 (빠름)
snippet = source_bytes[node.start_byte : node.end_byte]
text = snippet.decode("utf-8", errors="replace")
```

---

## 테스트

관련 테스트:
- `tests/test_indexer.py` - 인덱싱 기능 테스트
- `tests/test_javadoc.py` - Javadoc 탐지 테스트
- `tests/test_read_range.py` - 범위 읽기 테스트
- `tests/test_snapshots.py` - 스냅샷 테스트

---

## 확장 가능성

### 새로운 심볼 타입 추가
1. `CLASS_NODE_KINDS`에 노드 타입 추가
2. 파싱 함수 작성 (예: `_parse_new_symbol`)
3. `_parse_class_body` 또는 메인 루프에 핸들러 추가

### 새로운 언어 지원
Parser 컴포넌트는 Java에 특화되어 있지만, 구조는 다른 언어로 확장 가능합니다:
1. Tree-sitter 언어 바인딩 설치 (예: `tree_sitter_python`)
2. 언어별 노드 타입 매핑
3. 언어별 파서 모듈 작성

---

## 참고 자료

- [Tree-sitter 공식 문서](https://tree-sitter.github.io/)
- [Tree-sitter Java 문법](https://github.com/tree-sitter/tree-sitter-java)
- [Java 언어 명세](https://docs.oracle.com/javase/specs/)
