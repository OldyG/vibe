# QUICKSTART

## 1) Setup
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2) Run MCP server
```powershell
python -m mcp_server.server
```

## 3) Try CLI
```powershell
mcp-java-index index tests\fixtures\SimpleClass.java
mcp-java-index range tests\fixtures\SimpleClass.java 1 12
mcp-java-index find --root tests --query add --kind method
```

## 4) Large repo tips
Recommended cache root for large repos (fast local disk, outside the repo):
```powershell
$env:MCP_JAVA_INDEX_CACHE_ROOT = "C:\\mcp-cache\\java-index"
```

`java_find_symbol` indexes files on demand if a cache entry is missing.

There is no bulk index command yet. To pre-warm the cache:
```powershell
Get-ChildItem -Recurse -Filter *.java | ForEach-Object { mcp-java-index index $_.FullName | Out-Null }
```

Performance tips:
- Point `--root` to the smallest meaningful subtree (e.g., `src/`).
- Exclude build/output directories when pre-warming.
