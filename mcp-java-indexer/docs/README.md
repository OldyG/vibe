# MCP Java Indexer 문서

MCP Java Indexer는 대규모 Java 코드베이스를 LLM이 효율적으로 탐색할 수 있도록 도와주는 Model Context Protocol (MCP) 서버입니다.

## 📚 문서 구조

### 핵심 문서
- **[아키텍처 개요](architecture.md)** - 시스템 구조와 설계 철학
- **[API 레퍼런스](api-reference.md)** - MCP 툴 사용법 및 스키마
- **[개발 가이드](development-guide.md)** - 개발 환경 설정 및 기여 방법
- **[파일 구조](file-structure.md)** - 전체 파일 목록 및 역할

### 컴포넌트별 문서
- **[Parser 컴포넌트](components/parser.md)** - Java AST 파싱 및 심볼 추출
- **[Cache 컴포넌트](components/cache.md)** - 캐싱 메커니즘 및 성능 최적화
- **[MCP Server 컴포넌트](components/mcp-server.md)** - MCP 서버 구현
- **[CLI 컴포넌트](components/cli.md)** - 커맨드 라인 인터페이스

## 🎯 프로젝트 목표

**한 줄 요약**: Tree-sitter를 사용하여 Java 소스 파일을 사전 인덱싱하고, LLM이 최소한의 토큰으로 대규모 코드베이스를 탐색할 수 있도록 심볼 메타데이터를 제공하는 MCP 서버

### 핵심 기능
1. **심볼 인덱싱** - 클래스, 메서드, 필드, 생성자 추출
2. **정확한 라인 범위** - 각 심볼의 정확한 시작/종료 라인
3. **Javadoc 지원** - Javadoc 탐지 및 추출
4. **효율적인 범위 읽기** - 필요한 코드 섹션만 읽기
5. **심볼 검색** - 디렉토리 전체에서 심볼 찾기
6. **스마트 캐싱** - 콘텐츠 해시 기반 캐시 무효화

## 🚀 빠른 시작

```bash
# 1. 설치
pip install -e .

# 2. MCP 서버 실행
mcp-java-index-server

# 3. CLI로 테스트 (디버깅용)
mcp-java-index index path/to/File.java
mcp-java-index find --root . --query "MyClass"
mcp-java-index range path/to/File.java 10 50
```

## 💡 사용 사례

### LLM이 하는 작업 흐름
1. `java_index(filePath)` 호출 → 심볼 개요 획득
2. 메타데이터 분석 → 관련 심볼 선택
3. `java_read_javadoc()` 또는 `java_read_range()` 호출 → 상세 정보 읽기
4. 필요한 코드 섹션만 열기

이는 **"IDE 심볼 아웃라인 + 정의로 이동 + 문서 미리보기"** 기능과 유사합니다.

## 🔧 기술 스택

- **Python 3.10+** - 구현 언어
- **Tree-sitter** - 빠르고 정확한 Java 파서
- **MCP (Model Context Protocol)** - LLM 도구 통합
- **FastMCP** - 간소화된 MCP 서버 프레임워크

## 📖 다음 단계

- 처음 사용하신다면 → [아키텍처 개요](architecture.md)
- MCP 도구를 사용하고 싶다면 → [API 레퍼런스](api-reference.md)
- 기여하고 싶다면 → [개발 가이드](development-guide.md)
- 코드를 이해하고 싶다면 → [파일 구조](file-structure.md)

## 🤝 기여하기

기여를 환영합니다! [개발 가이드](development-guide.md)를 참고해주세요.

## 📝 라이선스

MIT License
