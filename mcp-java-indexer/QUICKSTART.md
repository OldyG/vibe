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
