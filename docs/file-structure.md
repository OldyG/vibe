# 파일 구조 및 역할

MCP Java Indexer의 전체 파일 구조와 각 파일의 역할을 상세히 설명합니다.

## 📂 전체 디렉토리 구조

```
mcp-java-indexer/
├── mcp-java-indexer/          # 메인 소스 코드
│   ├── parser/                # 파싱 엔진
│   │   ├── __init__.py
│   │   ├── indexer.py         # 메인 인덱싱 로직
│   │   ├── ast_utils.py       # AST 유틸리티
│   │   ├── javadoc.py         # Javadoc 탐지
│   │   └── readers.py         # 파일 I/O
│   ├── cache/                 # 캐싱 레이어
│   │   ├── __init__.py
│   │   └── cache_store.py     # 캐시 스토어
│   ├── mcp_server/            # MCP 서버
│   │   ├── __init__.py
│   │   ├── server.py          # 서버 설정
│   │   └── handlers.py        # 요청 핸들러
│   ├── cli/                   # CLI 도구
│   │   ├── __init__.py
│   │   └── main.py            # CLI 구현
│   └── tests/                 # 테스트
│       ├── conftest.py        # pytest 설정
│       ├── test_indexer.py    # 인덱서 테스트
│       ├── test_javadoc.py    # Javadoc 테스트
│       ├── test_read_range.py # 범위 읽기 테스트
│       ├── test_snapshots.py  # 스냅샷 테스트
│       ├── fixtures/          # 테스트 픽스처
│       │   ├── SimpleClass.java
│       │   ├── NestedClasses.java
│       │   ├── RecordEnumInterface.java
│       │   ├── JavadocSamples.java
│       │   ├── JavadocWithAnnotations.java
│       │   ├── MethodOverloads.java
│       │   ├── GenericMethods.java
│       │   └── InnerClassMethods.java
│       └── expected/          # 예상 출력
│           ├── SimpleClass.json
│           └── ...
├── docs/                      # 문서 (이 폴더)
│   ├── README.md
│   ├── architecture.md
│   ├── api-reference.md
│   ├── development-guide.md
│   ├── file-structure.md
│   └── components/
│       ├── parser.md
│       ├── cache.md
│       ├── mcp-server.md
│       └── cli.md
├── pyproject.toml             # 프로젝트 메타데이터
├── requirements.txt           # 의존성
├── README.md                  # 메인 README (한글)
├── QUICKSTART.md              # 빠른 시작 가이드 (한글)
├── MCP_JAVA_INDEXER.md        # 원본 사양
└── .mcp-java-index-cache/     # 캐시 디렉토리 (생성됨)
```

---

## 📄 파일별 상세 설명

### 루트 디렉토리

#### `pyproject.toml`
**역할**: Python 프로젝트 메타데이터 및 빌드 설정

**주요 내용**:
- 프로젝트 이름: `mcp-java-indexer`
- 버전: `0.1.0`
- 의존성: `mcp`, `tree-sitter`, `tree_sitter_java`
- 스크립트 엔트리포인트:
  - `mcp-java-index`: CLI 도구
  - `mcp-java-index-server`: MCP 서버
- Python 버전: `>=3.10`

**코드 위치**: `/home/user/vibe/mcp-java-indexer/pyproject.toml`

**라인 수**: 27줄

#### `requirements.txt`
**역할**: pip 의존성 목록

**내용**:
```
mcp>=1.2.0
tree-sitter>=0.23.0
tree_sitter_java>=0.23.0
pytest>=8.0.0  # dev dependency
```

#### `README.md`
**역할**: 프로젝트 메인 설명 (한글)

**주요 섹션**:
- 프로젝트 개요
- 설치 방법
- 사용법 (MCP 서버, CLI)
- 캐싱 설명
- 성능 정보
- 제한사항

**대상**: 처음 프로젝트를 접하는 사용자

#### `QUICKSTART.md`
**역할**: 5분 안에 시작할 수 있는 빠른 가이드 (한글)

**내용**:
- 설치
- 기본 사용법
- 예제

#### `MCP_JAVA_INDEXER.md`
**역할**: 원본 프로젝트 사양 (영문)

**내용**:
- 프로젝트 목표
- 기술 요구사항
- MCP 계약 (도구 스키마)
- 구현 가이드라인
- 자체 검증 체크리스트

**대상**: 프로젝트 개발자 및 기여자

---

### parser/ - 파싱 엔진

#### `parser/__init__.py`
**역할**: 패키지 초기화 (비어있음)

**라인 수**: 0줄

#### `parser/indexer.py`
**역할**: Java 파싱 및 심볼 추출의 핵심 엔진

**주요 함수**:
- `index_java_file()`: 메인 진입점
- `_parse_class_declaration()`: 클래스 파싱
- `_parse_method_declaration()`: 메서드 파싱
- `_parse_constructor_declaration()`: 생성자 파싱
- `_parse_field_declaration()`: 필드 파싱
- `_parse_class_body()`: 클래스 바디 파싱
- `find_symbol_by_id()`: 심볼 ID로 검색
- `find_symbols()`: 디렉토리 전체 심볼 검색
- `find_symbols_in_file()`: 파일 내 심볼 검색

**주요 데이터 구조**:
- `ParseContext`: 파싱 컨텍스트
- `CLASS_NODE_KINDS`: 클래스 타입 매핑

**의존성**:
- `tree_sitter`, `tree_sitter_java`
- `cache.cache_store`
- `parser.ast_utils`, `parser.javadoc`

**코드 위치**: `/home/user/vibe/mcp-java-indexer/parser/indexer.py`

**라인 수**: 615줄

#### `parser/ast_utils.py`
**역할**: Tree-sitter AST 노드 조작 유틸리티

**주요 함수**:
- `node_text()`: 노드에서 텍스트 추출
- `extract_modifiers()`: 접근 제어자 추출
- `normalize_whitespace()`: 공백 정규화
- `split_top_level_commas()`: 최상위 쉼표로 분리
- `first_identifier()`: 첫 번째 식별자 찾기
- `first_named_child()`: 특정 타입의 첫 자식 찾기
- `modifier_anchor_line()`: 제어자 시작 라인

**상수**:
- `JAVA_MODIFIERS`: Java 접근 제어자 집합

**코드 위치**: `/home/user/vibe/mcp-java-indexer/parser/ast_utils.py`

**라인 수**: 112줄

#### `parser/javadoc.py`
**역할**: Javadoc 주석 탐지 및 추출

**주요 함수**:
- `find_javadoc()`: 심볼 앞의 Javadoc 찾기
- `build_javadoc_dict()`: Javadoc 메타데이터 생성

**탐지 규칙**:
- `/** ... */` 형식만 인정
- 심볼 바로 앞에 위치 (빈 줄 허용)
- 애노테이션 앞의 Javadoc도 인식

**코드 위치**: `/home/user/vibe/mcp-java-indexer/parser/javadoc.py`

**라인 수**: 77줄

#### `parser/readers.py`
**역할**: 파일 I/O 및 범위 읽기

**주요 함수**:
- `read_range()`: 특정 라인 범위 읽기
- `read_javadoc()`: 심볼의 Javadoc 읽기
- `_read_lines()`: 파일을 라인 단위로 읽기

**기능**:
- 라인 번호 추가 옵션
- 최대 문자 수 제한
- 캐시 통합 (javadoc용)

**코드 위치**: `/home/user/vibe/mcp-java-indexer/parser/readers.py`

**라인 수**: 113줄 (마지막 라인이 113임)

---

### cache/ - 캐싱 레이어

#### `cache/__init__.py`
**역할**: 패키지 초기화 (비어있음)

**라인 수**: 0줄

#### `cache/cache_store.py`
**역할**: 파일 기반 캐시 스토리지 구현

**주요 클래스**:
- `CacheStore`: 캐시 관리 클래스
  - `__init__()`: 초기화
  - `load()`: 캐시 로드
  - `save()`: 캐시 저장
  - `_path_key()`: 파일 경로를 해시로 변환
  - `_cache_path()`: 캐시 파일 경로 계산

**주요 함수**:
- `default_cache_store()`: 기본 캐시 스토어 생성

**캐시 전략**:
- 파일 경로 해시 + 옵션 해시로 캐시 키 생성
- 콘텐츠 해시로 무효화
- JSON 형식 저장
- `.mcp-java-index-cache/` 디렉토리 사용

**환경 변수**:
- `MCP_JAVA_INDEX_CACHE_ROOT`: 캐시 루트 디렉토리 오버라이드

**코드 위치**: `/home/user/vibe/mcp-java-indexer/cache/cache_store.py`

**라인 수**: 54줄

---

### mcp_server/ - MCP 서버

#### `mcp_server/__init__.py`
**역할**: 패키지 초기화 (비어있음)

**라인 수**: 0줄

#### `mcp_server/server.py`
**역할**: MCP 서버 설정 및 도구 등록

**주요 구성**:
- FastMCP 인스턴스 생성
- 4개 도구 등록:
  - `java_index`
  - `java_read_range`
  - `java_read_javadoc`
  - `java_find_symbol`
- `main()`: 서버 실행 함수

**도구 등록 방식**: `@mcp.tool()` 데코레이터

**코드 위치**: `/home/user/vibe/mcp-java-indexer/mcp_server/server.py`

**라인 수**: 38줄

#### `mcp_server/handlers.py`
**역할**: MCP 요청 핸들러 및 옵션 정규화

**주요 함수**:
- 옵션 정규화:
  - `_normalize_index_options()`
  - `_normalize_range_options()`
  - `_normalize_javadoc_options()`
  - `_normalize_find_options()`
- 핸들러:
  - `java_index()`
  - `java_read_range()`
  - `java_read_javadoc()`
  - `java_find_symbol()`

**전역 변수**:
- `_CACHE`: 공유 캐시 인스턴스

**코드 위치**: `/home/user/vibe/mcp-java-indexer/mcp_server/handlers.py`

**라인 수**: 70줄

---

### cli/ - CLI 도구

#### `cli/__init__.py`
**역할**: 패키지 초기화 (비어있음)

**라인 수**: 0줄

#### `cli/main.py`
**역할**: 커맨드 라인 인터페이스 구현

**주요 구성**:
- argparse 기반 CLI
- 3개 서브커맨드:
  - `index`: 파일 인덱싱
  - `range`: 라인 범위 읽기
  - `find`: 심볼 검색

**주요 함수**:
- `main()`: CLI 진입점
- 서브커맨드 추가:
  - `_add_index_command()`
  - `_add_range_command()`
  - `_add_find_command()`
- 실행 핸들러:
  - `_run_index()`
  - `_run_range()`
  - `_run_find()`

**출력**: JSON 형식 (들여쓰기 2칸)

**코드 위치**: `/home/user/vibe/mcp-java-indexer/cli/main.py`

**라인 수**: 123줄

---

### tests/ - 테스트

#### `tests/conftest.py`
**역할**: pytest 설정 및 픽스처

**내용**:
- 공통 테스트 설정
- pytest 픽스처 정의

**코드 위치**: `/home/user/vibe/mcp-java-indexer/tests/conftest.py`

#### `tests/test_indexer.py`
**역할**: 인덱서 기능 테스트

**테스트 케이스**:
- 기본 클래스 인덱싱
- 메서드 추출
- 필드 추출
- 생성자 추출
- 중첩 클래스 처리
- private 멤버 필터링
- 오류 처리

#### `tests/test_javadoc.py`
**역할**: Javadoc 탐지 테스트

**테스트 케이스**:
- Javadoc 존재 여부
- Javadoc 위치 (startLine, endLine)
- 애노테이션이 있는 경우
- 내부 클래스의 Javadoc

#### `tests/test_read_range.py`
**역할**: 범위 읽기 기능 테스트

**테스트 케이스**:
- 정상 범위 읽기
- 라인 번호 포함/제외
- 최대 문자 수 제한
- 잘못된 범위 처리

#### `tests/test_snapshots.py`
**역할**: 스냅샷 테스트 (예상 출력 검증)

**테스트 방식**:
- 픽스처 파일 인덱싱
- 예상 출력(JSON)과 비교
- 회귀 방지

#### `tests/fixtures/` - 테스트 픽스처
**역할**: 테스트용 Java 파일 모음

| 파일 | 설명 |
|-----|------|
| `SimpleClass.java` | 기본 클래스 |
| `NestedClasses.java` | 중첩 클래스 |
| `RecordEnumInterface.java` | Record, Enum, Interface |
| `JavadocSamples.java` | 다양한 Javadoc |
| `JavadocWithAnnotations.java` | 애노테이션 + Javadoc |
| `MethodOverloads.java` | 오버로드된 메서드 |
| `GenericMethods.java` | 제네릭 메서드 |
| `InnerClassMethods.java` | 내부 클래스 메서드 |

#### `tests/expected/` - 예상 출력
**역할**: 스냅샷 테스트용 예상 JSON 출력

---

### docs/ - 문서

#### `docs/README.md`
**역할**: 문서 메인 인덱스

**내용**:
- 문서 구조 소개
- 프로젝트 목표
- 빠른 시작 링크

#### `docs/architecture.md`
**역할**: 시스템 아키텍처 설명

**내용**:
- 시스템 구조
- 설계 원칙
- 데이터 흐름
- 컴포넌트 개요
- 심볼 ID 전략
- Tree-sitter 선택 이유
- 캐싱 메커니즘

#### `docs/api-reference.md`
**역할**: MCP 도구 API 레퍼런스

**내용**:
- 4개 도구 상세 설명
- 입력/출력 스키마
- 사용 예시
- 에러 처리
- 성능 특성
- 사용 패턴

#### `docs/file-structure.md`
**역할**: 파일 구조 및 역할 설명 (이 문서)

#### `docs/development-guide.md`
**역할**: 개발 환경 설정 및 기여 가이드

#### `docs/components/` - 컴포넌트별 문서

| 파일 | 설명 |
|-----|------|
| `parser.md` | Parser 컴포넌트 상세 |
| `cache.md` | Cache 컴포넌트 상세 |
| `mcp-server.md` | MCP Server 컴포넌트 상세 |
| `cli.md` | CLI 컴포넌트 상세 |

---

## 📊 코드 통계

### 라인 수 (주석 제외)

| 컴포넌트 | 파일 | 라인 수 |
|---------|------|--------|
| **Parser** | indexer.py | 615 |
|  | ast_utils.py | 112 |
|  | javadoc.py | 77 |
|  | readers.py | 113 |
|  | **소계** | **917** |
| **Cache** | cache_store.py | 54 |
|  | **소계** | **54** |
| **MCP Server** | server.py | 38 |
|  | handlers.py | 70 |
|  | **소계** | **108** |
| **CLI** | main.py | 123 |
|  | **소계** | **123** |
| **전체** |  | **1,202** |

### 파일 수

| 카테고리 | 파일 수 |
|---------|--------|
| 소스 코드 (.py) | 13 |
| 테스트 (.py) | 5 |
| 픽스처 (.java) | 8 |
| 문서 (.md) | 10 |
| 설정 파일 | 2 |
| **전체** | **38** |

---

## 🔍 의존성 그래프

### 모듈 간 의존성

```
cli.main
  └─→ parser.indexer
  └─→ parser.readers

mcp_server.server
  └─→ mcp_server.handlers
        └─→ parser.indexer
        └─→ parser.readers
        └─→ cache.cache_store

parser.indexer
  └─→ tree_sitter, tree_sitter_java
  └─→ parser.ast_utils
  └─→ parser.javadoc
  └─→ cache.cache_store

parser.readers
  └─→ parser.indexer
  └─→ cache.cache_store

parser.javadoc
  (외부 의존성 없음)

parser.ast_utils
  (외부 의존성 없음)

cache.cache_store
  (외부 의존성 없음)
```

### 외부 의존성

```
mcp (>=1.2.0)
  └─→ FastMCP 프레임워크

tree-sitter (>=0.23.0)
  └─→ AST 파싱 라이브러리

tree_sitter_java (>=0.23.0)
  └─→ Java 문법 바인딩

pytest (>=8.0.0) [dev]
  └─→ 테스트 프레임워크
```

---

## 🗂️ 데이터 파일

### 캐시 디렉토리
```
.mcp-java-index-cache/
├── {path_hash1}-{opt_hash1}.json
├── {path_hash1}-{opt_hash2}.json
├── {path_hash2}-{opt_hash1}.json
└── ...
```

**생성 시점**: 첫 인덱싱 시 자동 생성

**위치**: 현재 디렉토리 또는 `MCP_JAVA_INDEX_CACHE_ROOT` 환경 변수

**내용**: 인덱싱 결과 JSON

---

## 🎯 진입점

### 1. MCP 서버
**스크립트**: `mcp-java-index-server`
**모듈**: `mcp_server.server:main`
**용도**: LLM과의 통신

### 2. CLI
**스크립트**: `mcp-java-index`
**모듈**: `cli.main:main`
**용도**: 개발자 디버깅 및 테스트

---

## 🧪 테스트 실행

### 전체 테스트
```bash
pytest
```

### 특정 테스트 파일
```bash
pytest tests/test_indexer.py
```

### 커버리지 포함
```bash
pytest --cov=mcp-java-indexer --cov-report=html
```

---

## 📝 코드 스타일

### 포맷팅
- **줄 길이**: 최대 120자 (권장)
- **들여쓰기**: 4 스페이스
- **문자열 인용부호**: 큰따옴표 (`"`) 선호

### 타입 힌트
- Python 3.10+ `from __future__ import annotations` 사용
- 모든 함수에 타입 힌트 권장
- 예: `def foo(x: int) -> str:`

### Docstring
- 복잡한 함수에는 docstring 추가
- 간단한 유틸리티는 생략 가능

---

## 🔄 향후 파일 추가 가능성

### 1. 추가 파서 기능
```
parser/
├── type_resolver.py   # 타입 해석 (향후)
├── call_graph.py      # 호출 그래프 (향후)
└── incremental.py     # 증분 인덱싱 (향후)
```

### 2. 추가 캐시 전략
```
cache/
├── distributed.py     # 분산 캐시 (향후)
└── metrics.py         # 캐시 메트릭 (향후)
```

### 3. 추가 출력 형식
```
cli/
└── formatters/
    ├── yaml.py        # YAML 출력
    ├── csv.py         # CSV 출력
    └── summary.py     # 요약 출력
```

---

## 참고 자료

- [아키텍처 개요](architecture.md) - 시스템 구조
- [API 레퍼런스](api-reference.md) - MCP 도구
- [개발 가이드](development-guide.md) - 개발 환경
- [컴포넌트 문서](components/) - 상세 설명
