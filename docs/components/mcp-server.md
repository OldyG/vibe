# MCP Server 컴포넌트

MCP Server 컴포넌트는 Model Context Protocol을 통해 LLM에 Java 인덱싱 기능을 노출합니다.

## 📁 파일 구조

```
mcp_server/
├── __init__.py           # 패키지 초기화
├── server.py             # MCP 서버 설정 및 도구 등록 (38줄)
└── handlers.py           # 요청 핸들러 및 옵션 정규화 (70줄)
```

---

## server.py

### 개요
FastMCP를 사용하여 MCP 서버를 구현하고, 4개의 도구를 등록합니다.

**코드 위치**: `/home/user/vibe/mcp-java-indexer/mcp_server/server.py`

### FastMCP 인스턴스
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mcp-java-indexer")
```

**서버 이름**: `"mcp-java-indexer"`
- MCP 클라이언트가 서버를 식별하는 데 사용
- 로그 및 디버깅에 표시

### 등록된 도구

#### 1. java_index
```python
@mcp.tool()
def java_index(filePath: str, options: dict | None = None) -> dict:
    """Java 파일의 심볼 인덱스를 반환합니다."""
    return handlers.java_index(filePath, options)
```

**코드 위치**: `server.py:10-12`

**파라미터**:
- `filePath`: 인덱싱할 Java 파일 경로
- `options`: 인덱싱 옵션 (선택)

**반환**: 인덱싱 결과 dict

#### 2. java_read_range
```python
@mcp.tool()
def java_read_range(
    filePath: str, startLine: int, endLine: int, options: dict | None = None
) -> dict:
    """파일의 특정 라인 범위를 읽습니다."""
    return handlers.java_read_range(filePath, startLine, endLine, options)
```

**코드 위치**: `server.py:15-19`

**파라미터**:
- `filePath`: 읽을 파일 경로
- `startLine`: 시작 라인 (1-based)
- `endLine`: 종료 라인 (1-based)
- `options`: 읽기 옵션 (선택)

#### 3. java_read_javadoc
```python
@mcp.tool()
def java_read_javadoc(filePath: str, symbolId: str, options: dict | None = None) -> dict:
    """심볼의 Javadoc을 읽습니다."""
    return handlers.java_read_javadoc(filePath, symbolId, options)
```

**코드 위치**: `server.py:22-24`

**파라미터**:
- `filePath`: 파일 경로
- `symbolId`: 심볼 ID
- `options`: 읽기 옵션 (선택)

#### 4. java_find_symbol
```python
@mcp.tool()
def java_find_symbol(rootDir: str, query: str, options: dict | None = None) -> dict:
    """디렉토리에서 심볼을 검색합니다."""
    return handlers.java_find_symbol(rootDir, query, options)
```

**코드 위치**: `server.py:27-29`

**파라미터**:
- `rootDir`: 검색할 루트 디렉토리
- `query`: 검색 쿼리
- `options`: 검색 옵션 (선택)

### 메인 함수

```python
def main() -> None:
    """MCP 서버를 시작합니다."""
    mcp.run()

if __name__ == "__main__":
    main()
```

**코드 위치**: `server.py:32-37`

**실행 방법**:
```bash
# 직접 실행
python -m mcp_server.server

# 또는 스크립트로
mcp-java-index-server
```

---

## handlers.py

### 개요
MCP 도구 요청을 처리하고, 옵션을 정규화하며, 파서 및 캐시 레이어를 호출합니다.

**코드 위치**: `/home/user/vibe/mcp-java-indexer/mcp_server/handlers.py`

### 전역 캐시 인스턴스
```python
from cache.cache_store import default_cache_store

_CACHE = default_cache_store()
```

**코드 위치**: `handlers.py:10`

**이유**: 모든 핸들러가 동일한 캐시 인스턴스를 공유하여 효율성 극대화

### 옵션 정규화 함수

옵션 정규화는 다음을 보장합니다:
1. 기본값 설정
2. 타입 안전성
3. 일관된 동작

#### `_normalize_index_options(options)`
인덱싱 옵션을 정규화합니다.

**코드 위치**: `handlers.py:13-22`

```python
def _normalize_index_options(options: Optional[dict]) -> dict:
    opts = options or {}
    return {
        "includePrivate": opts.get("includePrivate", True),
        "includeFields": opts.get("includeFields", True),
        "includeInnerClasses": opts.get("includeInnerClasses", True),
        "includeConstructors": opts.get("includeConstructors", True),
        "maxJavadocPreviewChars": opts.get("maxJavadocPreviewChars", 0),
        "stableIds": opts.get("stableIds", True),
    }
```

**기본값**:
| 옵션 | 기본값 | 설명 |
|-----|-------|------|
| `includePrivate` | `true` | private 멤버 포함 |
| `includeFields` | `true` | 필드 포함 |
| `includeInnerClasses` | `true` | 내부 클래스 포함 |
| `includeConstructors` | `true` | 생성자 포함 |
| `maxJavadocPreviewChars` | `0` | Javadoc 미리보기 문자 수 (0=미리보기 없음) |
| `stableIds` | `true` | 안정적인 심볼 ID 사용 |

#### `_normalize_range_options(options)`
범위 읽기 옵션을 정규화합니다.

**코드 위치**: `handlers.py:25-30`

```python
def _normalize_range_options(options: Optional[dict]) -> dict:
    opts = options or {}
    return {
        "includeLineNumbers": opts.get("includeLineNumbers", True),
        "maxChars": opts.get("maxChars", 20000),
    }
```

**기본값**:
| 옵션 | 기본값 | 설명 |
|-----|-------|------|
| `includeLineNumbers` | `true` | 라인 번호 포함 |
| `maxChars` | `20000` | 최대 문자 수 |

#### `_normalize_javadoc_options(options)`
Javadoc 읽기 옵션을 정규화합니다.

**코드 위치**: `handlers.py:33-38`

```python
def _normalize_javadoc_options(options: Optional[dict]) -> dict:
    opts = options or {}
    return {
        "includeLineNumbers": opts.get("includeLineNumbers", True),
        "maxChars": opts.get("maxChars", 8000),
    }
```

**기본값**:
| 옵션 | 기본값 | 설명 |
|-----|-------|------|
| `includeLineNumbers` | `true` | 라인 번호 포함 |
| `maxChars` | `8000` | 최대 문자 수 (range보다 작음) |

#### `_normalize_find_options(options)`
심볼 검색 옵션을 정규화합니다.

**코드 위치**: `handlers.py:41-47`

```python
def _normalize_find_options(options: Optional[dict]) -> dict:
    opts = options or {}
    return {
        "matchKind": opts.get("matchKind", "any"),
        "maxResults": opts.get("maxResults", 50),
        "caseSensitive": opts.get("caseSensitive", False),
    }
```

**기본값**:
| 옵션 | 기본값 | 설명 |
|-----|-------|------|
| `matchKind` | `"any"` | 매칭할 심볼 종류 |
| `maxResults` | `50` | 최대 결과 수 |
| `caseSensitive` | `false` | 대소문자 구분 |

### 핸들러 함수

#### `java_index(filePath, options)`
Java 파일을 인덱싱합니다.

**코드 위치**: `handlers.py:50-52`

```python
def java_index(filePath: str, options: Optional[dict] = None) -> dict:
    opts = _normalize_index_options(options)
    return index_java_file(filePath, opts, _CACHE)
```

**처리 흐름**:
1. 옵션 정규화
2. `parser.indexer.index_java_file()` 호출 (캐시 포함)
3. 결과 반환

#### `java_read_range(filePath, startLine, endLine, options)`
파일의 특정 라인 범위를 읽습니다.

**코드 위치**: `handlers.py:55-59`

```python
def java_read_range(
    filePath: str, startLine: int, endLine: int, options: Optional[dict] = None
) -> dict:
    opts = _normalize_range_options(options)
    return read_range(filePath, startLine, endLine, opts)
```

**처리 흐름**:
1. 옵션 정규화
2. `parser.readers.read_range()` 호출
3. 결과 반환

#### `java_read_javadoc(filePath, symbolId, options)`
심볼의 Javadoc을 읽습니다.

**코드 위치**: `handlers.py:62-64`

```python
def java_read_javadoc(filePath: str, symbolId: str, options: Optional[dict] = None) -> dict:
    opts = _normalize_javadoc_options(options)
    return read_javadoc(filePath, symbolId, opts, _CACHE)
```

**처리 흐름**:
1. 옵션 정규화
2. `parser.readers.read_javadoc()` 호출 (캐시 활용)
3. 결과 반환

#### `java_find_symbol(rootDir, query, options)`
디렉토리에서 심볼을 검색합니다.

**코드 위치**: `handlers.py:67-69`

```python
def java_find_symbol(rootDir: str, query: str, options: Optional[dict] = None) -> dict:
    opts = _normalize_find_options(options)
    return find_symbols(rootDir, query, opts)
```

**처리 흐름**:
1. 옵션 정규화
2. `parser.indexer.find_symbols()` 호출
3. 결과 반환

---

## MCP 프로토콜 통합

### FastMCP 란?
FastMCP는 Model Context Protocol 서버를 쉽게 구축할 수 있는 Python 프레임워크입니다.

**주요 기능**:
- 데코레이터 기반 도구 등록 (`@mcp.tool()`)
- 자동 타입 검증
- JSON-RPC 통신 처리
- stdio/SSE 전송 지원

### 도구 등록 메커니즘

```python
@mcp.tool()
def my_tool(param1: str, param2: int) -> dict:
    """도구 설명"""
    return {"result": "..."}
```

FastMCP는 다음을 자동으로 처리합니다:
1. **함수 시그니처 분석**: 파라미터 타입 추출
2. **JSON 스키마 생성**: MCP 도구 스키마 생성
3. **타입 검증**: 입력 파라미터 검증
4. **에러 처리**: 예외를 MCP 에러로 변환
5. **직렬화**: 결과를 JSON으로 직렬화

### MCP 통신 흐름

```
LLM 클라이언트                    MCP 서버
    │                                │
    ├─── 도구 목록 요청 ────────────►│
    │                                │
    │◄─── 도구 목록 응답 ────────────┤
    │    (java_index, java_read_range, ...)
    │                                │
    ├─── java_index 호출 ───────────►│
    │    {"filePath": "Foo.java"}    │
    │                                │
    │                      ┌─────────┤
    │                      │ 파일 인덱싱
    │                      │ (캐시 확인)
    │                      └─────────┤
    │                                │
    │◄─── 인덱싱 결과 ───────────────┤
    │    {"classes": [...]}          │
```

---

## 서버 실행

### 직접 실행
```bash
python -m mcp_server.server
```

### 스크립트로 실행
```bash
mcp-java-index-server
```

**스크립트 정의** (`pyproject.toml`):
```toml
[project.scripts]
mcp-java-index-server = "mcp_server.server:main"
```

### stdio 모드
MCP 서버는 기본적으로 stdio를 사용하여 통신합니다:
- **입력**: stdin (JSON-RPC 요청)
- **출력**: stdout (JSON-RPC 응답)
- **로그**: stderr

**예시 요청** (stdin):
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "java_index",
    "arguments": {
      "filePath": "src/main/java/com/example/MyClass.java",
      "options": {"includePrivate": false}
    }
  }
}
```

**예시 응답** (stdout):
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "filePath": "src/main/java/com/example/MyClass.java",
    "language": "java",
    "hash": "abc123...",
    "lineCount": 150,
    "classes": [...]
  }
}
```

---

## 에러 처리

### 핸들러 에러
핸들러 함수가 예외를 발생시키면 FastMCP가 자동으로 MCP 에러로 변환합니다.

**예시**:
```python
# 파일이 존재하지 않는 경우
def java_index(filePath: str, options: Optional[dict] = None) -> dict:
    # index_java_file에서 예외 발생
    # → FastMCP가 MCP 에러로 변환
```

**MCP 에러 응답**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32603,
    "message": "Internal error",
    "data": "Failed to read file: ..."
  }
}
```

### 우아한 저하 (Graceful Degradation)
핸들러는 가능한 한 부분 결과를 반환합니다:

```python
# 파싱 오류가 있어도 결과 반환
{
  "filePath": "BadFile.java",
  "classes": [...],  # 파싱된 부분
  "errors": [
    {"level": "error", "message": "Parse error", "line": 123}
  ]
}
```

---

## 성능 고려사항

### 캐시 재사용
전역 `_CACHE` 인스턴스를 사용하여:
- 동일 파일에 대한 반복 호출 최적화
- 메모리 효율적 (디스크 기반 캐시)

### 블로킹 I/O
현재 구현은 동기식 (blocking):
- 한 번에 하나의 요청만 처리
- LLM 사용 사례에는 충분 (순차적 요청)

**향후 개선**: 비동기 I/O 지원 가능

---

## 디버깅

### 서버 로그
stderr로 로그 출력:

```python
import sys
print("DEBUG: indexing file", file_path, file=sys.stderr)
```

### MCP Inspector
MCP 공식 디버깅 도구 사용:

```bash
npx @modelcontextprotocol/inspector mcp-java-index-server
```

웹 UI에서 도구 호출 테스트 가능

### 직접 JSON-RPC 테스트
```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | mcp-java-index-server
```

---

## 설계 결정 사항

### 왜 FastMCP인가?
1. **간단함**: 보일러플레이트 최소화
2. **타입 안전**: 파이썬 타입 힌트 활용
3. **표준 준수**: MCP 사양 완전 지원

### 왜 옵션 정규화를 하는가?
1. **기본값 보장**: 클라이언트가 모든 옵션을 지정할 필요 없음
2. **타입 안전**: 잘못된 타입 방지
3. **유지보수성**: 옵션 변경 시 한 곳만 수정

### 왜 전역 캐시 인스턴스인가?
1. **효율성**: 모든 핸들러가 캐시 공유
2. **일관성**: 동일한 캐시 정책 적용

---

## 향후 개선 가능성

### 1. 비동기 I/O
```python
# 미래 개선안
@mcp.tool()
async def java_index(filePath: str, options: dict | None = None) -> dict:
    return await async_index_java_file(filePath, opts, _CACHE)
```

### 2. 배치 요청
여러 파일을 한 번에 인덱싱:

```python
@mcp.tool()
def java_index_batch(filePaths: list[str], options: dict | None = None) -> list[dict]:
    return [index_java_file(fp, opts, _CACHE) for fp in filePaths]
```

### 3. 스트리밍 응답
큰 결과를 스트리밍:

```python
@mcp.tool()
def java_index_stream(filePath: str, options: dict | None = None):
    # 클래스별로 스트리밍
    for cls in classes:
        yield cls
```

### 4. 메트릭 및 모니터링
```python
@mcp.tool()
def java_index(filePath: str, options: dict | None = None) -> dict:
    start = time.time()
    result = index_java_file(filePath, opts, _CACHE)
    duration = time.time() - start
    log_metric("index_duration", duration)
    return result
```

---

## 테스트

MCP 서버는 다음과 같이 테스트할 수 있습니다:

### 1. 단위 테스트 (핸들러 함수)
```python
# tests/test_handlers.py
from mcp_server.handlers import java_index

def test_java_index():
    result = java_index("tests/fixtures/SimpleClass.java")
    assert result["language"] == "java"
    assert len(result["classes"]) > 0
```

### 2. 통합 테스트 (MCP 클라이언트)
```python
# MCP 클라이언트를 사용한 통합 테스트
async with Client() as client:
    await client.connect_stdio("mcp-java-index-server")
    result = await client.call_tool("java_index", {
        "filePath": "test.java"
    })
    assert result is not None
```

### 3. MCP Inspector
웹 UI를 통한 수동 테스트

---

## 참고 자료

- [API 레퍼런스](../api-reference.md) - MCP 도구 상세 사양
- [Parser 컴포넌트](parser.md) - 핸들러가 호출하는 파서 함수
- [Cache 컴포넌트](cache.md) - 캐싱 메커니즘
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP 공식 문서
