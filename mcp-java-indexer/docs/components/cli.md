# CLI 컴포넌트

CLI 컴포넌트는 개발자가 MCP 서버 없이 직접 Java 인덱싱 기능을 테스트하고 디버깅할 수 있는 커맨드 라인 인터페이스를 제공합니다.

## 📁 파일 구조

```
cli/
├── __init__.py           # 패키지 초기화
└── main.py               # CLI 구현 (123줄)
```

---

## main.py

### 개요
`argparse`를 사용하여 3개의 서브커맨드를 제공하는 CLI 도구를 구현합니다.

**코드 위치**: `/home/user/vibe/mcp-java-indexer/cli/main.py`

### 진입점

```python
def main() -> None:
    """CLI 메인 함수"""
    parser = argparse.ArgumentParser(
        prog="mcp-java-index",
        description="MCP Java Indexer CLI for debugging and testing"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 서브커맨드 등록
    _add_index_command(subparsers)
    _add_range_command(subparsers)
    _add_find_command(subparsers)

    args = parser.parse_args()

    # 서브커맨드 실행
    if args.command == "index":
        _run_index(args)
    elif args.command == "range":
        _run_range(args)
    elif args.command == "find":
        _run_find(args)
```

**코드 위치**: `main.py:95-123`

**실행 방법**:
```bash
# 스크립트로 (권장)
mcp-java-index <command> [args...]

# 또는 모듈로
python -m cli.main <command> [args...]
```

---

## 서브커맨드

### 1. index - 파일 인덱싱

Java 파일을 인덱싱하여 심볼 정보를 출력합니다.

#### 사용법
```bash
mcp-java-index index <file_path> [options]
```

#### 인자

| 인자 | 타입 | 필수 | 설명 |
|-----|------|------|------|
| `file_path` | 위치 인자 | ✅ | 인덱싱할 Java 파일 경로 |
| `--no-private` | 플래그 | ❌ | private 멤버 제외 |
| `--no-fields` | 플래그 | ❌ | 필드 제외 |
| `--no-inner` | 플래그 | ❌ | 내부 클래스 제외 |
| `--no-constructors` | 플래그 | ❌ | 생성자 제외 |
| `--javadoc-preview` | 정수 | ❌ | Javadoc 미리보기 문자 수 (기본: 0) |

#### 예시

**기본 사용**:
```bash
mcp-java-index index src/main/java/com/example/MyClass.java
```

**출력**:
```json
{
  "filePath": "src/main/java/com/example/MyClass.java",
  "language": "java",
  "hash": "a1b2c3d4e5f6...",
  "lineCount": 150,
  "classes": [
    {
      "symbolId": "Class#com.example.MyClass|start:1|end:150",
      "kind": "class",
      "name": "MyClass",
      ...
    }
  ],
  "errors": []
}
```

**private 멤버 제외**:
```bash
mcp-java-index index MyClass.java --no-private
```

**Javadoc 미리보기 포함**:
```bash
mcp-java-index index MyClass.java --javadoc-preview 100
```

#### 구현

**서브파서 등록**:
```python
def _add_index_command(subparsers) -> None:
    index_parser = subparsers.add_parser(
        "index",
        help="Index a Java file and print symbol metadata"
    )
    index_parser.add_argument("file_path", help="Path to Java file")
    index_parser.add_argument("--no-private", action="store_true",
                              help="Exclude private members")
    index_parser.add_argument("--no-fields", action="store_true",
                              help="Exclude fields")
    index_parser.add_argument("--no-inner", action="store_true",
                              help="Exclude inner classes")
    index_parser.add_argument("--no-constructors", action="store_true",
                              help="Exclude constructors")
    index_parser.add_argument("--javadoc-preview", type=int, default=0,
                              help="Max javadoc preview chars")
```

**코드 위치**: `main.py:12-31`

**실행 핸들러**:
```python
def _run_index(args) -> None:
    options = {
        "includePrivate": not args.no_private,
        "includeFields": not args.no_fields,
        "includeInnerClasses": not args.no_inner,
        "includeConstructors": not args.no_constructors,
        "maxJavadocPreviewChars": args.javadoc_preview,
        "stableIds": True,
    }
    result = index_java_file(args.file_path, options)
    print(json.dumps(result, indent=2, ensure_ascii=False))
```

**코드 위치**: `main.py:64-75`

---

### 2. range - 라인 범위 읽기

파일의 특정 라인 범위를 읽어 출력합니다.

#### 사용법
```bash
mcp-java-index range <file_path> <start_line> <end_line> [options]
```

#### 인자

| 인자 | 타입 | 필수 | 설명 |
|-----|------|------|------|
| `file_path` | 위치 인자 | ✅ | 읽을 파일 경로 |
| `start_line` | 위치 인자 (정수) | ✅ | 시작 라인 (1-based) |
| `end_line` | 위치 인자 (정수) | ✅ | 종료 라인 (1-based) |
| `--no-line-numbers` | 플래그 | ❌ | 라인 번호 제외 |
| `--max-chars` | 정수 | ❌ | 최대 문자 수 (기본: 20000) |

#### 예시

**기본 사용**:
```bash
mcp-java-index range MyClass.java 50 80
```

**출력**:
```json
{
  "filePath": "MyClass.java",
  "startLine": 50,
  "endLine": 80,
  "content": "50: public void doSomething() {\n51:     System.out.println(\"Hello\");\n52: }"
}
```

**라인 번호 없이**:
```bash
mcp-java-index range MyClass.java 50 80 --no-line-numbers
```

**출력**:
```json
{
  "filePath": "MyClass.java",
  "startLine": 50,
  "endLine": 80,
  "content": "public void doSomething() {\n    System.out.println(\"Hello\");\n}"
}
```

#### 구현

**서브파서 등록**:
```python
def _add_range_command(subparsers) -> None:
    range_parser = subparsers.add_parser(
        "range",
        help="Read a specific line range from a file"
    )
    range_parser.add_argument("file_path", help="Path to file")
    range_parser.add_argument("start_line", type=int,
                              help="Start line (1-based)")
    range_parser.add_argument("end_line", type=int,
                              help="End line (1-based)")
    range_parser.add_argument("--no-line-numbers", action="store_true",
                              help="Exclude line numbers")
    range_parser.add_argument("--max-chars", type=int, default=20000,
                              help="Max chars to return")
```

**코드 위치**: `main.py:34-49`

**실행 핸들러**:
```python
def _run_range(args) -> None:
    options = {
        "includeLineNumbers": not args.no_line_numbers,
        "maxChars": args.max_chars,
    }
    result = read_range(args.file_path, args.start_line, args.end_line, options)
    print(json.dumps(result, indent=2, ensure_ascii=False))
```

**코드 위치**: `main.py:78-84`

---

### 3. find - 심볼 검색

디렉토리 전체에서 심볼을 검색합니다.

#### 사용법
```bash
mcp-java-index find --root <root_dir> --query <query> [options]
```

#### 인자

| 인자 | 타입 | 필수 | 설명 |
|-----|------|------|------|
| `--root` | 옵션 | ✅ | 검색할 루트 디렉토리 |
| `--query` | 옵션 | ✅ | 검색 쿼리 (심볼 이름) |
| `--kind` | 옵션 | ❌ | 심볼 종류 (class/method/field/constructor/any) |
| `--max-results` | 정수 | ❌ | 최대 결과 수 (기본: 50) |
| `--case-sensitive` | 플래그 | ❌ | 대소문자 구분 |

#### 예시

**기본 사용**:
```bash
mcp-java-index find --root src/main/java --query "UserService"
```

**출력**:
```json
{
  "rootDir": "src/main/java",
  "query": "UserService",
  "results": [
    {
      "filePath": "com/example/service/UserService.java",
      "symbolId": "Class#com.example.service.UserService|start:10|end:200",
      "kind": "class",
      "qualifiedName": "com.example.service.UserService",
      "startLine": 10,
      "endLine": 200,
      "signatureText": "public class UserService"
    }
  ]
}
```

**메서드만 검색**:
```bash
mcp-java-index find --root . --query "authenticate" --kind method
```

**대소문자 구분**:
```bash
mcp-java-index find --root . --query "UserService" --case-sensitive
```

**최대 결과 수 제한**:
```bash
mcp-java-index find --root . --query "get" --max-results 10
```

#### 구현

**서브파서 등록**:
```python
def _add_find_command(subparsers) -> None:
    find_parser = subparsers.add_parser(
        "find",
        help="Find symbols in a directory by name"
    )
    find_parser.add_argument("--root", required=True,
                            help="Root directory to search")
    find_parser.add_argument("--query", required=True,
                            help="Symbol name to search for")
    find_parser.add_argument("--kind", default="any",
                            help="Symbol kind (class/method/field/any)")
    find_parser.add_argument("--max-results", type=int, default=50,
                            help="Max results")
    find_parser.add_argument("--case-sensitive", action="store_true",
                            help="Case sensitive search")
```

**코드 위치**: `main.py:52-62`

**실행 핸들러**:
```python
def _run_find(args) -> None:
    options = {
        "matchKind": args.kind,
        "maxResults": args.max_results,
        "caseSensitive": args.case_sensitive,
    }
    result = find_symbols(args.root, args.query, options)
    print(json.dumps(result, indent=2, ensure_ascii=False))
```

**코드 위치**: `main.py:87-92`

---

## JSON 출력 형식

모든 서브커맨드는 결과를 JSON 형식으로 출력합니다.

### 출력 설정
```python
print(json.dumps(result, indent=2, ensure_ascii=False))
```

**설정**:
- `indent=2`: 들여쓰기 2칸 (가독성)
- `ensure_ascii=False`: 한글 등 유니코드 문자 그대로 출력

### 파싱
CLI 출력을 다른 도구로 파싱할 수 있습니다:

```bash
# jq로 필터링
mcp-java-index index MyClass.java | jq '.classes[0].name'

# Python으로 파싱
result=$(mcp-java-index index MyClass.java)
python -c "import json; print(json.loads('$result')['lineCount'])"
```

---

## 사용 사례

### 1. 빠른 파일 확인
파일이 올바르게 파싱되는지 확인:
```bash
mcp-java-index index src/main/java/MyClass.java | head -20
```

### 2. 메서드 목록 추출
특정 파일의 모든 메서드 이름 추출:
```bash
mcp-java-index index MyClass.java | \
  jq '.classes[].methods[].name'
```

### 3. 특정 메서드 코드 읽기
1. 인덱스에서 메서드 찾기:
```bash
mcp-java-index index MyClass.java | \
  jq '.classes[].methods[] | select(.name=="doSomething")'
```

2. 라인 범위 확인 후 읽기:
```bash
mcp-java-index range MyClass.java 50 80
```

### 4. 프로젝트 전체에서 클래스 찾기
```bash
mcp-java-index find --root src/main/java --query "Service" --kind class
```

### 5. 테스트 픽스처 생성
예상 출력 생성:
```bash
mcp-java-index index tests/fixtures/SimpleClass.java > \
  tests/expected/SimpleClass.json
```

### 6. 성능 측정
```bash
time mcp-java-index index large_file.java
```

---

## 디버깅

### 에러 확인
CLI는 예외를 그대로 출력합니다:

```bash
$ mcp-java-index index non_existent.java
Traceback (most recent call last):
  ...
FileNotFoundError: [Errno 2] No such file or directory: 'non_existent.java'
```

### 부분 파싱 에러
파싱 오류가 있어도 부분 결과 + 에러 정보 출력:

```bash
$ mcp-java-index index broken.java | jq '.errors'
[
  {
    "level": "error",
    "message": "Parse error",
    "line": 45
  }
]
```

### Verbose 모드
현재는 없지만, 향후 추가 가능:
```bash
# 미래 개선안
mcp-java-index --verbose index MyClass.java
```

---

## 스크립팅

### Bash 스크립트 예시

**모든 Java 파일 인덱싱**:
```bash
#!/bin/bash
for file in $(find src -name "*.java"); do
  echo "Indexing $file..."
  mcp-java-index index "$file" > "index/${file%.java}.json"
done
```

**메서드 수 계산**:
```bash
#!/bin/bash
total_methods=0
for file in $(find src -name "*.java"); do
  count=$(mcp-java-index index "$file" | \
    jq '[.classes[].methods[]] | length')
  total_methods=$((total_methods + count))
done
echo "Total methods: $total_methods"
```

### Python 스크립트 예시

```python
import subprocess
import json

def index_file(file_path):
    result = subprocess.run(
        ["mcp-java-index", "index", file_path],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

# 사용
data = index_file("MyClass.java")
print(f"Found {len(data['classes'])} classes")
```

---

## 설계 결정 사항

### 왜 JSON 출력인가?
1. **파싱 용이**: 다른 도구와 통합 쉬움
2. **구조화**: MCP 서버 출력과 동일 형식
3. **표준**: 언어 중립적

### 왜 서브커맨드 구조인가?
1. **명확성**: 각 기능이 별도 커맨드
2. **확장성**: 새 커맨드 추가 용이
3. **표준**: git, docker 등과 유사한 UX

### 왜 argparse인가?
1. **표준 라이브러리**: 추가 의존성 없음
2. **기능 충분**: 서브커맨드, 타입 검증 등 지원
3. **자동 도움말**: `--help` 자동 생성

---

## 향후 개선 가능성

### 1. Verbose 모드
```bash
mcp-java-index --verbose index MyClass.java
# [INFO] Reading file: MyClass.java
# [INFO] Computing hash: abc123...
# [INFO] Cache miss, parsing...
# [INFO] Found 3 classes, 15 methods
```

### 2. 다양한 출력 형식
```bash
# YAML
mcp-java-index index --format yaml MyClass.java

# CSV (플랫 데이터)
mcp-java-index index --format csv MyClass.java

# 요약
mcp-java-index index --format summary MyClass.java
# Classes: 3, Methods: 15, Fields: 8
```

### 3. 필터링 옵션
```bash
# 이름 패턴으로 필터링
mcp-java-index index MyClass.java --filter-methods "get*"

# 접근 제어자로 필터링
mcp-java-index index MyClass.java --only-public
```

### 4. 배치 처리
```bash
# 여러 파일 한 번에
mcp-java-index index-batch src/**/*.java

# 또는 stdin에서 읽기
find src -name "*.java" | mcp-java-index index-batch --stdin
```

### 5. 캐시 관리 커맨드
```bash
# 캐시 정보
mcp-java-index cache-info

# 캐시 정리
mcp-java-index cache-clear
```

### 6. 검증 커맨드
```bash
# 프로젝트 전체 검증
mcp-java-index validate src/

# 파싱 오류만 출력
mcp-java-index validate src/ --errors-only
```

---

## 테스트

### 수동 테스트
```bash
# 픽스처 파일로 테스트
mcp-java-index index tests/fixtures/SimpleClass.java
mcp-java-index range tests/fixtures/SimpleClass.java 1 10
mcp-java-index find --root tests/fixtures --query "Simple"
```

### 자동 테스트
```python
# tests/test_cli.py
import subprocess
import json

def test_cli_index():
    result = subprocess.run(
        ["mcp-java-index", "index", "tests/fixtures/SimpleClass.java"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["language"] == "java"
```

### 회귀 테스트
출력을 스냅샷으로 저장하고 비교:
```bash
# 기준 생성
mcp-java-index index tests/fixtures/SimpleClass.java > expected.json

# 비교
mcp-java-index index tests/fixtures/SimpleClass.java | diff - expected.json
```

---

## 참고 자료

- [API 레퍼런스](../api-reference.md) - CLI 출력 형식 = MCP 응답 형식
- [Parser 컴포넌트](parser.md) - CLI가 호출하는 파서 함수
- [개발 가이드](../development-guide.md) - CLI 개발 및 테스트
