# MCP Java Indexer

Java 소스 파일을 미리 인덱싱하고, LLM 코드 탐색을 위한 간결한 심볼 메타데이터와 효율적인 범위 읽기를 제공하는 MCP 서버입니다.

## 사용자 가이드 (클론 후 5분 컷)
이 문서만 보고 따라 하면 **누구나/어디서든** 바로 실행되게끔, 초보가 자주 미끄러지는 지점(파이썬/venv/경로/권한/ Cursor 설정)을 한 번에 정리해놨어요. “이게 왜 이러지…?” 싶으면 아래 **문제 해결(Troubleshooting)** 먼저 보자 ㅋㅋ

### 요구사항
- Python **3.10+**
- (Cursor 연동 시) Cursor 최신 버전 권장

### 0) 저장소 클론
```bash
git clone <REPO_URL>
cd mcp-java-indexer
```

### 1) 가상환경(venv) 만들고 의존성 설치
#### Windows (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -U pip
.\.venv\Scripts\python -m pip install -r requirements.txt
```

#### macOS / Linux (bash/zsh)
```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -U pip
./.venv/bin/python -m pip install -r requirements.txt
```

### 2) “로컬에서 동작 확인” (가장 중요)
Cursor에 붙이기 전에, 이 단계에서 한 번이라도 성공하면 거의 끝났다고 보면 돼.

#### Windows
```powershell
.\.venv\Scripts\python -m cli.main index tests\fixtures\SimpleClass.java --javadoc-preview-chars 80
.\.venv\Scripts\python -m cli.main range tests\fixtures\SimpleClass.java 1 20
.\.venv\Scripts\python -m cli.main find --root tests --query add --kind method
```

#### macOS / Linux
```bash
./.venv/bin/python -m cli.main index tests/fixtures/SimpleClass.java --javadoc-preview-chars 80
./.venv/bin/python -m cli.main range tests/fixtures/SimpleClass.java 1 20
./.venv/bin/python -m cli.main find --root tests --query add --kind method
```

### 3) MCP 서버 실행 (수동 실행 테스트)
#### Windows
```powershell
.\.venv\Scripts\python -m mcp_server.server
```

#### macOS / Linux
```bash
./.venv/bin/python -m mcp_server.server
```

> 참고: 이 서버는 **stdio 전송**을 사용합니다 (HTTP 리스너 없음). 보통은 “서버를 직접 켜두는” 게 아니라, Cursor/Claude 같은 MCP 클라이언트가 **프로세스를 실행**합니다.

## Python + Tree-sitter를 선택한 이유
Tree-sitter는 전체 컴파일러 없이도 정확한 AST 범위와 우수한 성능을 제공하며, Python은 구현을 가볍고 크로스 플랫폼으로 유지합니다.

## 설치
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## MCP 서버 실행
```powershell
python -m mcp_server.server
```

## MCP 서버 연결 (stdio)
이 서버는 MCP stdio 전송을 사용합니다 (HTTP 리스너 없음). 프로세스를 시작하도록 MCP 클라이언트를 구성하세요.

### Cursor 예제
Cursor는 `mcp.json`에 “이 서버를 어떤 커맨드로 실행할지”를 등록해요.

- Windows: `C:\Users\<YOU>\.cursor\mcp.json`
- macOS/Linux: `~/.cursor/mcp.json`

가능하면 `"command": "python"`처럼 **PATH에 기대지 말고**, 아래처럼 **venv의 python.exe(또는 bin/python)를 명시**하는 걸 강력 추천!

#### Windows (권장: venv 고정)
```json
{
  "mcpServers": {
    "mcp-java-indexer": {
      "type": "stdio",
      "command": "C:\\path\\to\\mcp-java-indexer\\.venv\\Scripts\\python.exe",
      "args": ["-m", "mcp_server.server"],
      "cwd": "C:\\path\\to\\mcp-java-indexer",
      "env": {
        "MCP_JAVA_INDEX_CACHE_ROOT": "C:\\path\\to\\mcp-cache",
        "PYTHONPATH": "C:\\path\\to\\mcp-java-indexer"
      }
    }
  }
}
```

#### macOS / Linux (권장: venv 고정)
```json
{
  "mcpServers": {
    "mcp-java-indexer": {
      "type": "stdio",
      "command": "/path/to/mcp-java-indexer/.venv/bin/python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/path/to/mcp-java-indexer",
      "env": {
        "MCP_JAVA_INDEX_CACHE_ROOT": "/path/to/mcp-cache",
        "PYTHONPATH": "/path/to/mcp-java-indexer"
      }
    }
  }
}
```

> 설정 후에는 Cursor를 **완전 재시작**(프로세스 종료 후 재실행)하면 반영이 제일 확실해요.

### Claude Desktop 예제
`claude_desktop_config.json`을 업데이트하세요:
```json
{
  "mcpServers": {
    "mcp-java-indexer": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "C:\\path\\to\\mcp-java-indexer",
      "env": {
        "MCP_JAVA_INDEX_CACHE_ROOT": "C:\\path\\to\\mcp-cache"
      }
    }
  }
}
```

## CLI (디버그)
```powershell
mcp-java-index index tests\fixtures\SimpleClass.java
mcp-java-index range tests\fixtures\SimpleClass.java 1 20
mcp-java-index find --root . --query doWork
```

## MCP 도구
### java_index
입력:
```json
{
  "filePath": "tests/fixtures/SimpleClass.java",
  "options": {
    "includePrivate": true,
    "includeFields": true,
    "includeInnerClasses": true,
    "includeConstructors": true,
    "maxJavadocPreviewChars": 80,
    "stableIds": true
  }
}
```
출력 (일부 생략):
```json
{
  "filePath": "tests/fixtures/SimpleClass.java",
  "language": "java",
  "hash": "...",
  "lineCount": 33,
  "classes": [
    {
      "symbolId": "Class#com.example.SimpleClass|start:3|end:32",
      "kind": "class",
      "name": "SimpleClass",
      "qualifiedName": "com.example.SimpleClass",
      "modifiers": ["public"],
      "extends": null,
      "implements": [],
      "startLine": 3,
      "endLine": 32,
      "javadoc": { "present": false, "startLine": null, "endLine": null, "lineCount": 0, "preview": null },
      "fields": [
        {
          "symbolId": "Field#com.example.SimpleClass#count|start:6|end:6",
          "kind": "field",
          "name": "count",
          "typeText": "int",
          "modifiers": ["private"],
          "startLine": 6,
          "endLine": 6,
          "javadoc": { "present": true, "startLine": 4, "endLine": 5, "lineCount": 2, "preview": "..." }
        }
      ],
      "constructors": [],
      "methods": [],
      "innerClasses": []
    }
  ],
  "errors": []
}
```

### java_read_range
입력:
```json
{
  "filePath": "tests/fixtures/SimpleClass.java",
  "startLine": 1,
  "endLine": 8,
  "options": { "includeLineNumbers": true, "maxChars": 20000 }
}
```

### java_read_javadoc
입력:
```json
{
  "filePath": "tests/fixtures/JavadocOnly.java",
  "symbolId": "Method#com.example.docs.JavadocOnly#add(int,int):int|start:9|end:9"
}
```

### java_find_symbol
입력:
```json
{
  "rootDir": ".",
  "query": "doWork",
  "options": { "matchKind": "method", "maxResults": 50, "caseSensitive": false }
}
```

## 캐시
- 캐시 디렉토리: 현재 작업 디렉토리의 `.mcp-java-index-cache/`
- `MCP_JAVA_INDEX_CACHE_ROOT` 환경 변수로 재정의 가능합니다.

## 문제 해결 (Troubleshooting)
### 1) `spawn python ENOENT` (python을 못 찾음)
원인: Cursor가 `"command": "python"`을 실행하려는데, **Cursor 프로세스 기준 PATH에 python이 없음**.

해결:
- `mcp.json`에서 `"command"`를 **venv의 python 경로로 고정**하세요.
  - Windows: `...\\.venv\\Scripts\\python.exe`
  - macOS/Linux: `.../.venv/bin/python`

### 2) `No module named 'mcp_server'`
원인: 파이썬이 뜨긴 떴는데, **프로젝트 루트가 import 경로에 안 잡힘**(cwd 미적용/경로 꼬임 등).

해결:
- `mcp.json`에 `"cwd": "<repo-root>"`가 정확한지 확인
- 그리고 보험으로 `"env": { "PYTHONPATH": "<repo-root>" }`를 추가(위 예제처럼)

### 3) PowerShell에서 `Activate.ps1`이 막힘
원인: Windows 실행 정책(ExecutionPolicy) 때문에 스크립트 실행이 차단될 수 있어요.

해결(권장): 애초에 activate 없이도 됩니다. 아래처럼 **venv python을 직접 호출**하세요.
```powershell
.\.venv\Scripts\python -m pip install -r requirements.txt
```

### 4) “뭔가 안 되는데요…?” 최후의 확인 2종 세트
아래 두 개가 repo 루트에서 성공하면, MCP는 거의 99% 붙습니다.
```powershell
.\.venv\Scripts\python -c "import mcp_server; print('import ok')"
.\.venv\Scripts\python -m cli.main index tests\fixtures\SimpleClass.java
```

## Javadoc 매칭 규칙
- `/** ... */` 블록만 고려됩니다.
- 블록은 심볼의 첫 번째 수정자/어노테이션 줄 바로 위에 있어야 합니다 (빈 줄 허용).
- 블록과 첫 번째 수정자/어노테이션 줄 사이의 다른 비어있지 않은 줄이 있으면 매칭이 깨집니다.
- 어노테이션은 수정자로 취급됩니다. 첫 번째 어노테이션 바로 위의 Javadoc 블록이 연결됩니다.
- 심볼과 같은 줄에 있는 한 줄짜리 Javadoc은 감지되지 않습니다.

## 테스트
```powershell
pip install -r requirements-dev.txt
pytest
```

## 제한사항
- 의미론적 타입 해석이나 전체 Java 컴파일이 없습니다.
- 인터페이스 `extends` 목록은 `extends`에 쉼표로 구분된 문자열로 반환됩니다.
- 심볼 ID는 변경되지 않은 파일에 대해 안정적이지만, 줄 번호가 변경되면 바뀝니다.

## 향후 작업
- 더 풍부한 타입 추출 및 더 나은 인터페이스 `extends` 모델링.
- 호출 그래프 지원 및 파일 간 참조.
- 매우 큰 저장소에 대한 성능 개선.
