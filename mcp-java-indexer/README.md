# MCP Java Indexer

MCP server that pre-indexes Java source files and exposes compact symbol metadata plus efficient range reads for LLM code navigation.

## Why Python + Tree-sitter
Tree-sitter provides accurate AST ranges and good performance without a full compiler, and Python keeps the implementation light and cross-platform.

## Install
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run MCP server
```powershell
python -m mcp_server.server
```

## CLI (debug)
```powershell
mcp-java-index index tests\fixtures\SimpleClass.java
mcp-java-index range tests\fixtures\SimpleClass.java 1 20
mcp-java-index find --root . --query doWork
```

## MCP tools
### java_index
Input:
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
Output (truncated):
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
Input:
```json
{
  "filePath": "tests/fixtures/SimpleClass.java",
  "startLine": 1,
  "endLine": 8,
  "options": { "includeLineNumbers": true, "maxChars": 20000 }
}
```

### java_read_javadoc
Input:
```json
{
  "filePath": "tests/fixtures/JavadocOnly.java",
  "symbolId": "Method#com.example.docs.JavadocOnly#add(int,int):int|start:9|end:9"
}
```

### java_find_symbol
Input:
```json
{
  "rootDir": ".",
  "query": "doWork",
  "options": { "matchKind": "method", "maxResults": 50, "caseSensitive": false }
}
```

## Cache
- Cache directory: `.mcp-java-index-cache/` in the current working directory.
- Override with `MCP_JAVA_INDEX_CACHE_ROOT` environment variable.

## Tests
```powershell
pip install -r requirements-dev.txt
pytest
```

## Limitations
- No semantic type resolution or full Java compilation.
- Interface `extends` lists are returned as a comma-delimited string in `extends`.
- Symbol IDs are stable for unchanged files but will change if line numbers shift.

## Future work
- Richer type extraction and better interface `extends` modeling.
- Call graph support and cross-file references.
- Performance improvements for very large repos.
