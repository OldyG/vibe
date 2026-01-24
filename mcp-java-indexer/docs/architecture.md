# 아키텍처 개요

## 시스템 구조

MCP Java Indexer는 4개의 주요 레이어로 구성된 모듈형 아키텍처를 가지고 있습니다.

```
┌─────────────────────────────────────┐
│         MCP Server Layer            │  ← LLM과의 인터페이스
│   (mcp_server/server.py)            │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│       Request Handlers              │  ← 요청 정규화 및 라우팅
│   (mcp_server/handlers.py)          │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│       Core Parser Layer             │  ← Java AST 파싱 및 심볼 추출
│   • indexer.py (메인 로직)          │
│   • ast_utils.py (AST 헬퍼)         │
│   • javadoc.py (Javadoc 탐지)       │
│   • readers.py (파일 I/O)           │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│       Cache Layer                   │  ← 성능 최적화
│   (cache/cache_store.py)            │
└─────────────────────────────────────┘
```

## 설계 원칙

### 1. 정확성 우선 (Accuracy First)
- **라인 번호의 정확성**: 1-based 라인 번호, 정확한 시작/종료 위치
- **중괄호 매칭**: 메서드 `endLine`이 정확해야 함 (오류 불허)
- **복잡한 구조 처리**: 중첩 클래스, 애노테이션, 제네릭, 다중 라인 시그니처

### 2. 성능 (Performance)
- **빠른 인덱싱**: 단일 파일 인덱싱 < 100ms (일반적)
- **선형 확장**: 디렉토리 인덱싱은 선형적으로 확장
- **스마트 캐싱**: 파일 변경되지 않으면 캐시 사용

### 3. 최소 토큰 사용 (Token Efficiency)
- **단계적 정보 공개**: 개요 → 관심 있는 부분만 상세히
- **범위 기반 읽기**: 전체 파일 대신 필요한 라인만
- **Javadoc 분리**: 문서만 따로 읽을 수 있음

### 4. 견고성 (Robustness)
- **우아한 오류 처리**: 파싱 실패 시에도 부분 결과 반환
- **오류 배열**: 발생한 문제를 `errors` 배열에 기록
- **절대 크래시 없음**: 파일을 읽을 수 없는 경우에만 실패

## 데이터 흐름

### 인덱싱 흐름 (java_index)

```
파일 경로 입력
    │
    ▼
파일 읽기 + 해시 계산
    │
    ▼
캐시 확인 ─────► [캐시 히트] ─────► 캐시된 결과 반환
    │                                    ▲
[캐시 미스]                              │
    │                                    │
    ▼                                    │
Tree-sitter로 파싱                        │
    │                                    │
    ▼                                    │
AST 순회 + 심볼 추출                      │
    │                                    │
    ▼                                    │
결과 생성 + 캐시 저장 ───────────────────┘
    │
    ▼
결과 반환 (JSON)
```

### 범위 읽기 흐름 (java_read_range)

```
파일 경로 + 라인 범위
    │
    ▼
범위 유효성 검증
    │
    ▼
파일 읽기 (라인 단위)
    │
    ▼
지정된 범위 추출
    │
    ▼
문자 수 제한 적용 (maxChars)
    │
    ▼
라인 번호 추가 (옵션)
    │
    ▼
결과 반환
```

### 심볼 검색 흐름 (java_find_symbol)

```
루트 디렉토리 + 쿼리
    │
    ▼
*.java 파일 재귀 탐색
    │
    ▼
각 파일 인덱싱 (캐시 활용)
    │
    ▼
쿼리와 매칭되는 심볼 필터링
    │
    ▼
결과 수집 (maxResults까지)
    │
    ▼
결과 반환
```

## 핵심 컴포넌트

### Parser Layer
**역할**: Java 소스 코드를 AST로 파싱하고 심볼 추출

**주요 책임**:
- Tree-sitter Java 문법 사용하여 AST 생성
- 클래스, 인터페이스, 레코드, Enum, 애노테이션 추출
- 메서드, 생성자, 필드 추출 (시그니처, 파라미터, 반환 타입 포함)
- Javadoc 탐지 및 메타데이터 생성
- 중첩 클래스 재귀적 처리

**파일**: `parser/indexer.py`, `parser/ast_utils.py`, `parser/javadoc.py`, `parser/readers.py`

### Cache Layer
**역할**: 인덱싱 결과를 캐싱하여 성능 최적화

**주요 책임**:
- 파일 경로 + 콘텐츠 해시 + 옵션 해시로 캐시 키 생성
- JSON 형식으로 캐시 저장
- 콘텐츠 변경 시 캐시 무효화
- 환경 변수로 캐시 위치 설정 가능

**파일**: `cache/cache_store.py`

### MCP Server Layer
**역할**: MCP 프로토콜을 통해 LLM에 기능 노출

**주요 책임**:
- 4개의 MCP 도구 등록 (java_index, java_read_range, java_read_javadoc, java_find_symbol)
- FastMCP 사용하여 서버 구현
- 요청/응답 JSON 직렬화

**파일**: `mcp_server/server.py`, `mcp_server/handlers.py`

### CLI Layer
**역할**: 디버깅 및 개발을 위한 커맨드 라인 인터페이스

**주요 책임**:
- `index`, `range`, `find` 서브커맨드 제공
- JSON Pretty-print 출력
- 개발자가 MCP 없이 직접 테스트 가능

**파일**: `cli/main.py`

## 심볼 ID 전략

### 안정적이고 고유한 ID
모든 심볼은 `symbolId`를 가지며, 다음 형식을 따릅니다:

```
{Kind}#{QualifiedName}#{Detail}|start:{lineNum}|end:{lineNum}
```

### 예시
- **클래스**: `Class#com.foo.Bar|start:10|end:400`
- **메서드**: `Method#com.foo.Bar#doThing(int,String):Result|start:70|end:120`
- **생성자**: `Ctor#com.foo.Bar#Bar(int,String)|start:30|end:60`
- **필드**: `Field#com.foo.Bar#count|start:20|end:20`

### 왜 이 형식인가?
1. **안정성**: 코드 변경 없으면 ID 동일
2. **고유성**: 오버로드된 메서드도 구분 가능
3. **디버깅 용이**: 사람이 읽을 수 있음
4. **위치 정보**: 시작/종료 라인 포함

## Tree-sitter를 선택한 이유

### JavaParser 대비 장점
1. **정확한 범위**: 컴파일 없이 정확한 AST 범위 제공
2. **빠른 성능**: 경량 파서, 빠른 파싱 속도
3. **크로스 플랫폼**: Python 바인딩, 쉬운 설치
4. **의존성 최소화**: 무거운 Java 도구 불필요

### 지원하는 Java 구조
- ✅ 애노테이션 (별도 라인에 있어도 OK)
- ✅ 다중 라인 파라미터 리스트
- ✅ 제네릭 (타입 파라미터)
- ✅ 중첩/내부 클래스
- ✅ 레코드, Enum
- ✅ 인터페이스 (default/static 메서드)
- ✅ 생성자 및 컴팩트 생성자

## 캐싱 메커니즘

### 캐시 키 생성
```python
cache_key = SHA1(file_path) + "-" + SHA1(options)
```

### 캐시 무효화
파일의 `content_hash`가 변경되면 캐시 무효화:
```python
if cached_hash != current_hash:
    recompute_index()
```

### 캐시 위치
```
.mcp-java-index-cache/
├── abc123-opt456.json  ← 파일1 + 옵션A
├── abc123-opt789.json  ← 파일1 + 옵션B
└── def456-opt456.json  ← 파일2 + 옵션A
```

환경 변수 `MCP_JAVA_INDEX_CACHE_ROOT`로 위치 변경 가능

## 에러 처리 전략

### 우아한 저하 (Graceful Degradation)
파싱 오류가 발생해도:
1. 가능한 심볼은 추출
2. `errors` 배열에 오류 기록
3. 절대 크래시하지 않음 (파일을 읽을 수 없는 경우 제외)

### 오류 레벨
```json
{
  "errors": [
    {
      "level": "warning|error",
      "message": "설명",
      "line": 123
    }
  ]
}
```

## 성능 고려사항

### 인덱싱 성능
- **목표**: 단일 파일 < 100ms
- **실제**: 대부분 파일 < 50ms
- **큰 파일**: 수천 줄도 < 200ms

### 캐시 효과
- **캐시 히트**: < 5ms (파일 읽기 + 역직렬화)
- **캐시 미스**: 전체 인덱싱 수행

### 메모리 사용
- **AST**: 파싱 후 즉시 해제
- **캐시**: 디스크 기반, 메모리 압박 없음

## 확장성 고려사항

### 현재 제한사항
- **완전한 타입 추론 없음**: 타입은 텍스트로만 처리
- **프로젝트 간 호출 그래프 없음**: 향후 추가 가능
- **의미론적 분석 없음**: AST 기반만

### 향후 개선 가능성
- 프로젝트 전체 캐시 (디렉토리 단위)
- 증분 인덱싱 (변경된 파일만)
- 의미론적 정보 (타입 해석)
- 호출 그래프 생성

## 참고 자료

- [MCP 사양](../GENERATE_PROMPT.md) - 원본 사양 문서
- [Tree-sitter Java](https://github.com/tree-sitter/tree-sitter-java) - Java 문법
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP 공식 문서
