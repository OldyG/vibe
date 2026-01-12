# 개발 가이드

MCP Java Indexer 프로젝트에 기여하거나 개발 환경을 설정하는 방법을 안내합니다.

## 🚀 빠른 시작

### 요구사항
- Python 3.10 이상
- pip (Python 패키지 관리자)
- Git

### 설치

```bash
# 1. 저장소 클론
git clone https://github.com/your-org/mcp-java-indexer.git
cd mcp-java-indexer

# 2. 가상 환경 생성 (권장)
python -m venv venv

# 활성화 (Unix/Mac)
source venv/bin/activate

# 활성화 (Windows)
venv\Scripts\activate

# 3. 개발 모드로 설치
pip install -e .

# 4. 개발 의존성 설치
pip install -e ".[dev]"
```

### 설치 확인

```bash
# CLI 테스트
mcp-java-index --help

# MCP 서버 테스트 (Ctrl+C로 종료)
mcp-java-index-server

# 테스트 실행
pytest
```

---

## 📁 프로젝트 구조 이해

프로젝트를 처음 접한다면 다음 순서로 읽어보세요:

1. **[아키텍처 개요](architecture.md)** - 전체 시스템 구조
2. **[파일 구조](file-structure.md)** - 각 파일의 역할
3. **[API 레퍼런스](api-reference.md)** - MCP 도구 사양
4. **컴포넌트 문서** - 상세 구현
   - [Parser 컴포넌트](components/parser.md)
   - [Cache 컴포넌트](components/cache.md)
   - [MCP Server 컴포넌트](components/mcp-server.md)
   - [CLI 컴포넌트](components/cli.md)

---

## 🛠️ 개발 환경 설정

### IDE 설정

#### VS Code
권장 확장:
- Python (Microsoft)
- Pylance
- Python Test Explorer

`.vscode/settings.json`:
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "editor.formatOnSave": true
}
```

#### PyCharm
- 프로젝트 인터프리터를 가상 환경으로 설정
- pytest를 기본 테스트 러너로 설정
- 코드 스타일: PEP 8

### 코드 품질 도구 (선택사항)

```bash
# Black (코드 포맷터)
pip install black
black mcp-java-indexer/

# Ruff (린터)
pip install ruff
ruff check mcp-java-indexer/

# mypy (타입 체커)
pip install mypy
mypy mcp-java-indexer/
```

---

## 🧪 테스트

### 테스트 실행

```bash
# 전체 테스트
pytest

# 특정 파일
pytest tests/test_indexer.py

# 특정 테스트
pytest tests/test_indexer.py::test_simple_class

# Verbose 모드
pytest -v

# 실패 시 즉시 중단
pytest -x

# 병렬 실행 (pytest-xdist 필요)
pip install pytest-xdist
pytest -n auto
```

### 테스트 커버리지

```bash
# 커버리지 측정
pip install pytest-cov
pytest --cov=mcp-java-indexer --cov-report=html

# 커버리지 리포트 보기 (htmlcov/index.html 생성됨)
open htmlcov/index.html
```

### 새 테스트 작성

**테스트 파일 위치**: `tests/test_*.py`

**예시**:
```python
# tests/test_my_feature.py
from parser.indexer import index_java_file

def test_my_feature():
    """내 기능이 정상 동작하는지 테스트"""
    result = index_java_file("tests/fixtures/SimpleClass.java")
    assert result["language"] == "java"
    assert len(result["classes"]) > 0
```

**픽스처 추가**:
1. `tests/fixtures/` 에 Java 파일 추가
2. `tests/expected/` 에 예상 출력 JSON 추가 (스냅샷 테스트용)

---

## 🔧 주요 개발 작업

### 1. 새로운 Java 구조 지원 추가

**예시**: 애노테이션 프로세서 지원

**단계**:
1. Tree-sitter 노드 타입 확인
   ```python
   # 디버깅용 코드
   def print_ast(node, indent=0):
       print("  " * indent + node.type)
       for child in node.children:
           print_ast(child, indent + 1)
   ```

2. `parser/indexer.py`에 파싱 함수 추가
   ```python
   def _parse_annotation_processor(node, ctx, qualified_name):
       # 구현
       pass
   ```

3. `_parse_class_body`에 핸들러 추가
   ```python
   if member.type == "annotation_processor":
       processor = _parse_annotation_processor(member, ctx, qualified_name)
       # 결과 저장
   ```

4. 테스트 추가
   ```python
   # tests/test_indexer.py
   def test_annotation_processor():
       result = index_java_file("tests/fixtures/AnnotationProcessor.java")
       # 검증
   ```

### 2. 새로운 MCP 도구 추가

**예시**: `java_get_imports` 도구

**단계**:
1. 파서 함수 구현 (`parser/indexer.py`)
   ```python
   def get_imports(file_path: str) -> list[str]:
       """파일의 import 목록을 반환"""
       source_bytes = _read_file_bytes(file_path)
       tree = _PARSER.parse(source_bytes)
       imports = []
       for child in tree.root_node.named_children:
           if child.type == "import_declaration":
               import_text = node_text(source_bytes, child)
               imports.append(import_text)
       return imports
   ```

2. 핸들러 추가 (`mcp_server/handlers.py`)
   ```python
   def java_get_imports(filePath: str) -> dict:
       imports = get_imports(filePath)
       return {"filePath": filePath, "imports": imports}
   ```

3. 도구 등록 (`mcp_server/server.py`)
   ```python
   @mcp.tool()
   def java_get_imports(filePath: str) -> dict:
       return handlers.java_get_imports(filePath)
   ```

4. CLI 서브커맨드 추가 (선택사항)
   ```python
   # cli/main.py
   def _add_imports_command(subparsers):
       parser = subparsers.add_parser("imports")
       parser.add_argument("file_path")

   def _run_imports(args):
       result = get_imports(args.file_path)
       print(json.dumps(result, indent=2))
   ```

5. 테스트 추가
   ```python
   def test_get_imports():
       result = java_get_imports("tests/fixtures/SimpleClass.java")
       assert "imports" in result
   ```

### 3. 캐시 개선

**예시**: 압축 캐시 추가

**단계**:
1. `cache/cache_store.py` 수정
   ```python
   import gzip
   import json

   def save(self, file_path: str, data: dict, options_key: Optional[str] = None) -> None:
       cache_file = self._cache_path(file_path, options_key)
       json_data = json.dumps(data, ensure_ascii=True, indent=2).encode('utf-8')
       compressed = gzip.compress(json_data)
       cache_file.write_bytes(compressed)

   def load(self, file_path: str, content_hash: str, options_key: Optional[str] = None) -> Optional[dict]:
       cache_file = self._cache_path(file_path, options_key)
       if not cache_file.exists():
           return None
       try:
           compressed = cache_file.read_bytes()
           json_data = gzip.decompress(compressed).decode('utf-8')
           data = json.loads(json_data)
       except Exception:
           return None
       if data.get("hash") != content_hash:
           return None
       return data
   ```

2. 테스트 추가
   ```python
   def test_compressed_cache():
       cache = CacheStore(Path("."))
       data = {"hash": "abc", "test": "data"}
       cache.save("test.java", data)
       loaded = cache.load("test.java", "abc")
       assert loaded == data
   ```

---

## 🐛 디버깅

### 일반적인 문제

#### 1. Tree-sitter 파싱 오류
**증상**: `ERROR` 노드가 AST에 나타남

**디버깅**:
```python
# AST 출력
def print_tree(node, source_bytes, indent=0):
    text = source_bytes[node.start_byte:node.end_byte].decode('utf-8', errors='replace')
    if len(text) > 50:
        text = text[:50] + "..."
    print("  " * indent + f"{node.type}: {text}")
    for child in node.named_children:
        print_tree(child, source_bytes, indent + 1)

source_bytes = Path("test.java").read_bytes()
tree = _PARSER.parse(source_bytes)
print_tree(tree.root_node, source_bytes)
```

**해결**: Java 파일 문법 확인, Tree-sitter 버전 확인

#### 2. 캐시가 작동하지 않음
**증상**: 동일 파일을 반복 인덱싱해도 느림

**디버깅**:
```python
# 캐시 로그 추가
def load(self, file_path, content_hash, options_key):
    print(f"[CACHE] Loading {file_path}, hash={content_hash[:8]}")
    result = ...
    if result:
        print(f"[CACHE] HIT")
    else:
        print(f"[CACHE] MISS")
    return result
```

**해결**:
- 캐시 디렉토리 확인: `.mcp-java-index-cache/`
- 쓰기 권한 확인
- 옵션이 변경되었는지 확인

#### 3. Javadoc 탐지 실패
**증상**: Javadoc이 있는데 `present: false`

**디버깅**:
```python
# javadoc.py에 로그 추가
def find_javadoc(lines, symbol_line_1based):
    print(f"[JAVADOC] Symbol at line {symbol_line_1based}")
    # ... 탐색 로직
    if found:
        print(f"[JAVADOC] Found at lines {start}-{end}")
    else:
        print(f"[JAVADOC] Not found")
```

**해결**:
- Javadoc이 `/** ... */` 형식인지 확인
- 심볼 바로 앞에 있는지 확인 (빈 줄 허용)

### MCP 서버 디버깅

#### stderr 로그 추가
```python
import sys

def java_index(filePath: str, options: Optional[dict] = None) -> dict:
    print(f"[DEBUG] Indexing {filePath}", file=sys.stderr)
    result = index_java_file(filePath, opts, _CACHE)
    print(f"[DEBUG] Found {len(result['classes'])} classes", file=sys.stderr)
    return result
```

#### MCP Inspector 사용
```bash
npm install -g @modelcontextprotocol/inspector
npx @modelcontextprotocol/inspector mcp-java-index-server
```

웹 UI (http://localhost:5173)에서 도구 호출 테스트

---

## 📝 코드 스타일 가이드

### 명명 규칙

- **함수/변수**: `snake_case`
  ```python
  def index_java_file(file_path: str):
      result_data = {...}
  ```

- **클래스**: `PascalCase`
  ```python
  class CacheStore:
      pass
  ```

- **상수**: `UPPER_CASE`
  ```python
  JAVA_MODIFIERS = {"public", "private", ...}
  ```

- **Private 함수**: `_leading_underscore`
  ```python
  def _parse_method_declaration(node, ctx):
      pass
  ```

### 타입 힌트

**필수**:
```python
from __future__ import annotations
from typing import Optional

def foo(x: int, y: Optional[str] = None) -> dict:
    return {"x": x, "y": y}
```

### Docstring

**복잡한 함수에는 docstring 추가**:
```python
def find_symbols(root_dir: str, query: str, options: Optional[dict] = None) -> dict:
    """
    디렉토리 전체에서 심볼을 검색합니다.

    Args:
        root_dir: 검색할 루트 디렉토리
        query: 검색 쿼리 (심볼 이름)
        options: 검색 옵션 (matchKind, maxResults 등)

    Returns:
        검색 결과 dict (rootDir, query, results)
    """
```

### 에러 처리

**우아한 저하 원칙**:
```python
try:
    result = parse_something()
except Exception as exc:
    # 로그 기록
    print(f"Warning: {exc}", file=sys.stderr)
    # 부분 결과 반환
    return {"data": [], "errors": [{"message": str(exc)}]}
```

**절대 크래시하지 않기** (파일 읽기 실패 제외)

---

## 🚢 릴리스 프로세스

### 버전 관리

**Semantic Versioning** (MAJOR.MINOR.PATCH):
- **MAJOR**: 호환성 깨지는 변경
- **MINOR**: 새 기능 추가 (하위 호환)
- **PATCH**: 버그 수정

### 릴리스 체크리스트

1. **테스트 통과 확인**
   ```bash
   pytest
   ```

2. **버전 업데이트** (`pyproject.toml`)
   ```toml
   version = "0.2.0"
   ```

3. **CHANGELOG 작성** (권장)
   ```markdown
   ## [0.2.0] - 2024-01-15
   ### Added
   - 새 기능 1
   - 새 기능 2

   ### Fixed
   - 버그 수정 1
   ```

4. **커밋 및 태그**
   ```bash
   git commit -m "Release v0.2.0"
   git tag v0.2.0
   git push origin main --tags
   ```

5. **PyPI 배포** (선택사항)
   ```bash
   pip install build twine
   python -m build
   twine upload dist/*
   ```

---

## 🤝 기여 가이드

### 브랜치 전략

- **main**: 안정 버전
- **develop**: 개발 브랜치
- **feature/***: 새 기능
- **fix/***: 버그 수정

### 풀 리퀘스트 프로세스

1. **이슈 생성** (선택사항)
   - 기능 제안 또는 버그 보고

2. **브랜치 생성**
   ```bash
   git checkout -b feature/my-feature
   ```

3. **개발**
   - 코드 작성
   - 테스트 추가
   - 문서 업데이트

4. **테스트 실행**
   ```bash
   pytest
   ```

5. **커밋**
   ```bash
   git add .
   git commit -m "Add: my feature description"
   ```

   **커밋 메시지 형식**:
   - `Add: 새 기능`
   - `Fix: 버그 수정`
   - `Refactor: 리팩토링`
   - `Docs: 문서 업데이트`
   - `Test: 테스트 추가`

6. **푸시**
   ```bash
   git push origin feature/my-feature
   ```

7. **풀 리퀘스트 생성**
   - 변경 내용 설명
   - 관련 이슈 링크

### 코드 리뷰

**리뷰어 확인 사항**:
- [ ] 테스트 통과
- [ ] 코드 스타일 준수
- [ ] 문서 업데이트
- [ ] 하위 호환성
- [ ] 에러 처리

---

## 📚 추가 학습 자료

### Tree-sitter
- [Tree-sitter 공식 문서](https://tree-sitter.github.io/tree-sitter/)
- [Tree-sitter Java 문법](https://github.com/tree-sitter/tree-sitter-java)
- [Tree-sitter Playground](https://tree-sitter.github.io/tree-sitter/playground)

### MCP
- [Model Context Protocol 사양](https://modelcontextprotocol.io/)
- [FastMCP 문서](https://github.com/jlowin/fastmcp)

### Python
- [Python 타입 힌트](https://docs.python.org/3/library/typing.html)
- [pytest 문서](https://docs.pytest.org/)

---

## 💬 커뮤니티

### 질문 및 토론
- GitHub Issues: 버그 리포트, 기능 제안
- GitHub Discussions: 일반 질문, 아이디어

### 기여자
이 프로젝트에 기여해주신 모든 분께 감사드립니다!

---

## 🔄 다음 단계

개발 환경 설정이 완료되었다면:

1. **[파일 구조](file-structure.md)** 읽기 - 코드베이스 이해
2. **[Parser 컴포넌트](components/parser.md)** 읽기 - 핵심 로직 이해
3. **간단한 이슈 해결** - `good first issue` 태그 찾기
4. **첫 PR 제출** - 작은 변경부터 시작

Happy coding! 🎉
