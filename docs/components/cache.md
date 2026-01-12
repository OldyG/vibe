# Cache 컴포넌트

Cache 컴포넌트는 인덱싱 결과를 디스크에 저장하여 성능을 최적화합니다.

## 📁 파일 구조

```
cache/
├── __init__.py           # 패키지 초기화
└── cache_store.py        # 캐시 스토어 구현 (54줄)
```

---

## cache_store.py

### 개요
파일 기반 캐시 스토리지를 구현합니다. JSON 형식으로 인덱싱 결과를 저장하고, 콘텐츠 해시를 사용하여 캐시 무효화를 처리합니다.

### 핵심 클래스

## CacheStore

### 생성자
```python
def __init__(self, base_dir: Path) -> None:
    """
    캐시 스토어를 초기화합니다.

    Args:
        base_dir: 캐시 디렉토리를 생성할 기본 디렉토리
                  (실제 캐시는 base_dir/.mcp-java-index-cache/에 생성)
    """
    self.base_dir = base_dir
    self.cache_dir = base_dir / ".mcp-java-index-cache"
    self.cache_dir.mkdir(parents=True, exist_ok=True)
```

**코드 위치**: `/home/user/vibe/mcp-java-indexer/cache/cache_store.py:10-13`

**캐시 디렉토리 구조**:
```
프로젝트_루트/
├── .mcp-java-index-cache/        # 캐시 디렉토리
│   ├── abc123def456-opt789.json  # 파일1 + 옵션A
│   ├── abc123def456-opt012.json  # 파일1 + 옵션B
│   └── 789ghi012jkl-opt789.json  # 파일2 + 옵션A
├── src/
│   └── main/
│       └── java/
│           └── MyClass.java
└── ...
```

### 주요 메서드

#### `load(file_path, content_hash, options_key)`
캐시에서 인덱싱 결과를 로드합니다.

**코드 위치**: `cache_store.py:25-35`

```python
def load(self, file_path: str, content_hash: str,
         options_key: Optional[str] = None) -> Optional[dict]:
    """
    캐시에서 인덱싱 결과를 로드합니다.

    Args:
        file_path: 원본 파일 경로
        content_hash: 파일 콘텐츠의 해시 (SHA1)
        options_key: 인덱싱 옵션의 해시 (옵션별로 캐시 분리)

    Returns:
        캐시된 인덱싱 결과 dict 또는 None (캐시 미스 시)
    """
```

**처리 흐름**:
1. 캐시 파일 경로 계산
2. 파일 존재 여부 확인
3. JSON 파싱 시도 (실패 시 None 반환)
4. 콘텐츠 해시 검증 (불일치 시 None 반환)
5. 유효한 캐시 데이터 반환

**캐시 무효화 조건**:
- 캐시 파일이 존재하지 않음
- JSON 파싱 실패 (손상된 캐시 파일)
- 콘텐츠 해시 불일치 (파일 변경됨)

#### `save(file_path, data, options_key)`
인덱싱 결과를 캐시에 저장합니다.

**코드 위치**: `cache_store.py:37-39`

```python
def save(self, file_path: str, data: dict,
         options_key: Optional[str] = None) -> None:
    """
    인덱싱 결과를 캐시에 저장합니다.

    Args:
        file_path: 원본 파일 경로
        data: 인덱싱 결과 (반드시 "hash" 필드 포함)
        options_key: 인덱싱 옵션의 해시
    """
```

**저장 형식**:
- JSON (들여쓰기 2칸, ASCII 인코딩)
- UTF-8 파일 인코딩

**예시 캐시 파일 내용**:
```json
{
  "filePath": "src/main/java/com/example/MyClass.java",
  "language": "java",
  "hash": "a1b2c3d4e5f6789...",
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

### 헬퍼 메서드

#### `_path_key(file_path)`
파일 경로를 SHA1 해시로 변환합니다.

**코드 위치**: `cache_store.py:15-17`

```python
def _path_key(self, file_path: str) -> str:
    """파일 경로를 해시로 변환하여 캐시 키로 사용합니다."""
    digest = hashlib.sha1(file_path.encode("utf-8", errors="replace")).hexdigest()
    return digest
```

**이유**:
- 파일 경로가 길거나 특수 문자 포함 시 파일 시스템 호환성 문제 방지
- 일관된 길이의 키 생성

#### `_cache_path(file_path, options_key)`
캐시 파일의 전체 경로를 계산합니다.

**코드 위치**: `cache_store.py:19-23`

```python
def _cache_path(self, file_path: str, options_key: Optional[str]) -> Path:
    """캐시 파일의 경로를 계산합니다."""
    key = self._path_key(file_path)
    if options_key:
        key = f"{key}-{options_key}"
    return self.cache_dir / f"{key}.json"
```

**캐시 키 구조**:
```
{path_hash}[-{options_hash}].json
```

**예시**:
- 옵션 없음: `abc123def456.json`
- 옵션 있음: `abc123def456-opt789abc.json`

---

## 캐시 전략

### 캐시 키 생성

캐시 키는 3가지 요소로 구성됩니다:

1. **파일 경로 해시**: `SHA1(file_path)`
2. **콘텐츠 해시**: `SHA1(file_contents)` - 파일 내용
3. **옵션 해시**: `SHA1(JSON.stringify(options))` - 인덱싱 옵션

**옵션 해시 생성** (indexer.py에서):
```python
def _options_cache_key(options: dict) -> str:
    serialized = json.dumps(options, sort_keys=True, ensure_ascii=True)
    return hashlib.sha1(serialized.encode("utf-8")).hexdigest()
```

**코드 위치**: `parser/indexer.py:52-54`

### 캐시 무효화

캐시는 다음 경우에 무효화됩니다:

1. **파일 내용 변경**
   ```python
   if data.get("hash") != content_hash:
       return None  # 캐시 미스
   ```

2. **인덱싱 옵션 변경**
   - 옵션이 다르면 다른 캐시 파일 사용
   - 예: `includePrivate: true`와 `includePrivate: false`는 별도 캐시

3. **캐시 파일 손상**
   ```python
   try:
       data = json.loads(cache_file.read_text(encoding="utf-8"))
   except Exception:
       return None  # JSON 파싱 실패
   ```

### 캐시 히트/미스 시나리오

#### ✅ 캐시 히트
```
1. 파일 읽기: MyClass.java
2. 콘텐츠 해시 계산: abc123...
3. 캐시 확인: abc123... == 캐시된 해시? ✅
4. 캐시 반환 (< 5ms)
```

#### ❌ 캐시 미스 (파일 변경)
```
1. 파일 읽기: MyClass.java (수정됨)
2. 콘텐츠 해시 계산: xyz789... (변경됨)
3. 캐시 확인: xyz789... == abc123...? ❌
4. 전체 인덱싱 수행 (50-200ms)
5. 새 캐시 저장 (xyz789...)
```

#### ❌ 캐시 미스 (옵션 변경)
```
1. 이전 호출: index_java_file(..., {"includePrivate": true})
   → 캐시 파일: abc123-opt456.json
2. 현재 호출: index_java_file(..., {"includePrivate": false})
   → 캐시 파일: abc123-opt789.json (다른 파일)
3. 캐시 미스 → 인덱싱 수행
```

---

## 전역 함수

### `default_cache_store()`
기본 캐시 스토어를 생성합니다.

**코드 위치**: `cache_store.py:42-53`

```python
def default_cache_store() -> CacheStore:
    """
    기본 캐시 스토어를 생성합니다.

    환경 변수 MCP_JAVA_INDEX_CACHE_ROOT가 설정되어 있으면 그 경로를 사용하고,
    그렇지 않으면 현재 작업 디렉토리를 사용합니다.

    Returns:
        CacheStore 인스턴스
    """
    base = Path.cwd()
    env_override = os.environ.get("MCP_JAVA_INDEX_CACHE_ROOT")
    if env_override:
        base = Path(env_override)
    return CacheStore(base)
```

**환경 변수 설정**:
```bash
# Unix/Linux/Mac
export MCP_JAVA_INDEX_CACHE_ROOT=/path/to/cache

# Windows PowerShell
$env:MCP_JAVA_INDEX_CACHE_ROOT = "C:\path\to\cache"

# Windows CMD
set MCP_JAVA_INDEX_CACHE_ROOT=C:\path\to\cache
```

**사용 케이스**:
- CI/CD: 빌드 간 캐시 공유
- 다중 프로젝트: 중앙 캐시 디렉토리 사용
- 임시 디렉토리: `/tmp`에 캐시 저장

---

## 성능 특성

### 캐시 히트 시
- **파일 읽기**: < 1ms (SSD 기준)
- **JSON 파싱**: < 2ms (중간 크기 파일)
- **해시 검증**: < 0.1ms
- **총 시간**: < 5ms

### 캐시 미스 시
- **전체 인덱싱 수행**: 50-200ms (파일 크기에 따라)
- **캐시 저장**: < 5ms

### 디스크 공간
- **파일당 캐시 크기**: 1-50KB (일반적)
- **대형 파일** (1000+ 클래스): 최대 수백 KB
- **압축 없음**: 가독성 우선 (들여쓰기 포함 JSON)

---

## 캐시 관리

### 캐시 정리
캐시는 자동으로 정리되지 않습니다. 필요 시 수동 정리:

```bash
# 프로젝트별 캐시 삭제
rm -rf .mcp-java-index-cache/

# 전역 캐시 삭제 (환경 변수 설정 시)
rm -rf /path/to/cache/.mcp-java-index-cache/
```

### 캐시 통계 확인
캐시 디렉토리 크기 확인:

```bash
# Unix/Linux/Mac
du -sh .mcp-java-index-cache/

# Windows PowerShell
Get-ChildItem .mcp-java-index-cache -Recurse |
    Measure-Object -Property Length -Sum
```

### 캐시 파일 수 확인
```bash
# Unix/Linux/Mac
find .mcp-java-index-cache -name "*.json" | wc -l

# Windows PowerShell
(Get-ChildItem .mcp-java-index-cache -Filter "*.json" -Recurse).Count
```

---

## 설계 결정 사항

### 왜 디스크 기반 캐시인가?
1. **메모리 압박 없음**: 인메모리 캐시는 큰 프로젝트에서 OOM 위험
2. **영구성**: 서버 재시작 후에도 캐시 유지
3. **디버깅 용이**: JSON 파일로 직접 확인 가능

### 왜 JSON 형식인가?
1. **가독성**: 사람이 읽고 디버깅 가능
2. **호환성**: 다양한 도구로 검사 가능
3. **간단함**: 직렬화/역직렬화 용이

### 왜 옵션별로 캐시를 분리하는가?
```python
# includePrivate: true
{"classes": [{"methods": [..., private_method, ...]}]}

# includePrivate: false
{"classes": [{"methods": [...]}]}  # private_method 제외
```

동일 파일이지만 결과가 다르므로 별도 캐시 필요

---

## 잠재적 개선 사항

### 1. 캐시 만료 (TTL)
현재는 파일 변경 전까지 캐시가 영구 유지됩니다.
향후 시간 기반 만료 추가 가능:

```python
# 미래 개선안
{
  "cached_at": "2024-01-15T10:30:00Z",
  "ttl": 86400,  # 24시간
  ...
}
```

### 2. 압축
큰 프로젝트의 경우 캐시 압축으로 디스크 공간 절약:

```python
# 미래 개선안
import gzip
cache_file.write_bytes(gzip.compress(json_data))
```

### 3. 캐시 통계
캐시 히트율, 평균 로드 시간 등 메트릭 수집:

```python
# 미래 개선안
{
  "cache_hits": 1543,
  "cache_misses": 87,
  "hit_rate": 0.947
}
```

### 4. 디렉토리 단위 캐시
현재는 파일별 캐시. 향후 프로젝트 전체 인덱스 캐싱 가능:

```
.mcp-java-index-cache/
├── project-index.json     # 전체 프로젝트 인덱스
├── file1-hash.json        # 파일별 인덱스
└── file2-hash.json
```

---

## 문제 해결

### 캐시가 작동하지 않는 것 같아요
1. **캐시 디렉토리 확인**:
   ```bash
   ls -la .mcp-java-index-cache/
   ```

2. **쓰기 권한 확인**:
   ```bash
   touch .mcp-java-index-cache/test.txt
   ```

3. **캐시 파일 내용 확인**:
   ```bash
   cat .mcp-java-index-cache/*.json | jq .
   ```

### 캐시가 계속 미스됩니다
1. **옵션이 자주 바뀌는지 확인**: 동일한 옵션 사용하기
2. **파일이 자주 변경되는지 확인**: 정상 동작
3. **해시 불일치**: 파일 수정 시간이 아닌 콘텐츠로 판단 (정상)

### 캐시 디렉토리가 너무 큽니다
1. **오래된 캐시 삭제**:
   ```bash
   find .mcp-java-index-cache -mtime +30 -delete  # 30일 이상 된 파일 삭제
   ```

2. **전체 캐시 재구축**:
   ```bash
   rm -rf .mcp-java-index-cache/
   ```

---

## 테스트

캐시 기능은 다음 테스트에서 간접적으로 검증됩니다:
- `tests/test_indexer.py` - 인덱싱 기능 (캐시 통합 테스트)
- `tests/test_snapshots.py` - 스냅샷 테스트 (캐시 활용)

**캐시 테스트 예시**:
```python
# 첫 호출: 캐시 미스
result1 = index_java_file("Test.java")

# 두 번째 호출: 캐시 히트 (빠름)
result2 = index_java_file("Test.java")

assert result1 == result2
```

---

## 참고 자료

- [아키텍처 개요](../architecture.md) - 캐싱 메커니즘 설명
- [Parser 컴포넌트](parser.md) - 캐시 통합 방법
