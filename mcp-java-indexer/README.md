# MCP Java Indexer

Java 소스 파일을 미리 인덱싱하고, LLM 코드 탐색을 위한 간결한 심볼 메타데이터와 효율적인 범위 읽기를 제공하는 MCP 서버입니다.

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
`~/.cursor/mcp.json`을 생성하거나 업데이트하세요:
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
