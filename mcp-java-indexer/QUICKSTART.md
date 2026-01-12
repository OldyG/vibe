# 빠른 시작

## 1) 설정
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2) MCP 서버 실행
```powershell
python -m mcp_server.server
```

## 3) CLI 사용해보기
```powershell
mcp-java-index index tests\fixtures\SimpleClass.java
mcp-java-index range tests\fixtures\SimpleClass.java 1 12
mcp-java-index find --root tests --query add --kind method
```

## 4) 대규모 저장소 팁
대규모 저장소를 위한 권장 캐시 루트 (빠른 로컬 디스크, 저장소 외부):
```powershell
$env:MCP_JAVA_INDEX_CACHE_ROOT = "C:\\mcp-cache\\java-index"
```

`java_find_symbol`은 캐시 항목이 없으면 필요 시 파일을 인덱싱합니다.

아직 일괄 인덱싱 명령은 없습니다. 캐시를 미리 준비하려면:
```powershell
Get-ChildItem -Recurse -Filter *.java | ForEach-Object { mcp-java-index index $_.FullName | Out-Null }
```

성능 팁:
- `--root`를 가장 작은 의미 있는 하위 트리로 지정하세요 (예: `src/`).
- 미리 준비할 때 빌드/출력 디렉토리는 제외하세요.
