# Java Analyzer

Tree-sitter 기반 Java 소스 코드 분석 도구입니다. CLI로 독립 실행 가능하며, Java 파일의 심볼(클래스, 메서드, 필드 등)을 인덱싱하고 검색할 수 있습니다.

## 주요 기능

- 📊 **Java 심볼 인덱싱**: 클래스, 인터페이스, enum, record, annotation 분석
- 🔍 **심볼 검색**: 디렉토리 전체에서 심볼 이름으로 검색
- 📖 **Javadoc 추출**: 문서 주석 파싱 및 미리보기
- 📄 **범위 읽기**: 특정 라인 범위의 소스 코드 읽기
- ⚡ **캐싱**: 파싱 결과 자동 캐싱으로 빠른 재실행
- 🌍 **크로스 플랫폼**: Windows, macOS, Linux 모두 지원

## 사전 요구사항

### Python 설치 확인

먼저 Python이 설치되어 있는지 확인하세요:

```powershell
# Windows (PowerShell)
python --version
```

```bash
# macOS / Linux
python3 --version
```

**Python 3.10 이상**이 필요합니다.

### Python 설치가 필요한 경우

#### Windows

1. **공식 설치 (권장)**
   - https://www.python.org/downloads/
   - 설치 시 "Add Python to PATH" 체크 필수!

2. **Microsoft Store**
   - Microsoft Store에서 "Python 3.12" 검색 후 설치

3. **winget (Windows 11)**
   ```powershell
   winget install Python.Python.3.12
   ```

#### macOS

1. **Homebrew (권장)**

   ```bash
   brew install python@3.12
   ```

2. **공식 설치**
   - https://www.python.org/downloads/macos/

#### Linux

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Fedora/RHEL
sudo dnf install python3 python3-pip

# Arch
sudo pacman -S python python-pip
```

## 빠른 시작 (5분 컷)

### 1. 가상환경 생성 및 의존성 설치

#### Windows (PowerShell)

```powershell
# 가상환경 생성
python -m venv .venv

# pip 업그레이드
.\.venv\Scripts\python -m pip install -U pip

# 의존성 설치
.\.venv\Scripts\python -m pip install -r requirements.txt
```

#### macOS / Linux (bash/zsh)

```bash
# 가상환경 생성
python3 -m venv .venv

# pip 업그레이드
./.venv/bin/python -m pip install -U pip

# 의존성 설치
./.venv/bin/python -m pip install -r requirements.txt
```

### 2. CLI 사용 예시

#### Windows

```powershell
# Java 파일 인덱싱
.\.venv\Scripts\python -m cli.main index path\to\YourFile.java

# Javadoc 미리보기 포함
.\.venv\Scripts\python -m cli.main index path\to\YourFile.java --javadoc-preview-chars 80

# 특정 라인 범위 읽기 (1-20줄)
.\.venv\Scripts\python -m cli.main range path\to\YourFile.java 1 20

# 심볼 검색 (현재 디렉토리에서 "add" 메서드 찾기)
.\.venv\Scripts\python -m cli.main find --root . --query add --kind method

# 모든 심볼 검색 (클래스, 메서드, 필드 모두)
.\.venv\Scripts\python -m cli.main find --root . --query MyClass --kind any
```

#### macOS / Linux

```bash
# Java 파일 인덱싱
./.venv/bin/python -m cli.main index path/to/YourFile.java

# Javadoc 미리보기 포함
./.venv/bin/python -m cli.main index path/to/YourFile.java --javadoc-preview-chars 80

# 특정 라인 범위 읽기 (1-20줄)
./.venv/bin/python -m cli.main range path/to/YourFile.java 1 20

# 심볼 검색 (현재 디렉토리에서 "add" 메서드 찾기)
./.venv/bin/python -m cli.main find --root . --query add --kind method

# 모든 심볼 검색 (클래스, 메서드, 필드 모두)
./.venv/bin/python -m cli.main find --root . --query MyClass --kind any
```

## CLI 명령어 상세

### `index` - Java 파일 인덱싱

Java 파일의 모든 심볼을 추출하여 JSON으로 출력합니다.

```bash
python -m cli.main index <파일경로> [옵션]
```

**옵션:**

- `--javadoc-preview-chars N`: Javadoc 미리보기 문자 수 (기본: 0)
- `--no-private`: private 심볼 제외
- `--no-fields`: 필드 제외
- `--no-inner`: 내부 클래스 제외
- `--no-constructors`: 생성자 제외

**출력 예시:**

```json
{
  "filePath": "SimpleClass.java",
  "language": "java",
  "lineCount": 33,
  "classes": [
    {
      "kind": "class",
      "name": "SimpleClass",
      "qualifiedName": "com.example.SimpleClass",
      "modifiers": ["public"],
      "startLine": 3,
      "endLine": 32,
      "fields": [...],
      "methods": [...],
      "constructors": [...]
    }
  ]
}
```

### `range` - 라인 범위 읽기

파일의 특정 라인 범위를 읽어 출력합니다.

```bash
python -m cli.main range <파일경로> <시작라인> <끝라인> [옵션]
```

**옵션:**

- `--no-line-numbers`: 라인 번호 제외
- `--max-chars N`: 최대 출력 문자 수 (기본: 20000)

**출력 예시:**

```json
{
  "filePath": "SimpleClass.java",
  "startLine": 1,
  "endLine": 10,
  "content": "1: package com.example;\n2: \n3: public class SimpleClass {\n..."
}
```

### `find` - 심볼 검색

디렉토리 전체에서 심볼을 검색합니다.

```bash
python -m cli.main find --root <디렉토리> --query <검색어> [옵션]
```

**옵션:**

- `--kind <타입>`: 심볼 타입 필터 (class|method|field|any, 기본: any)
- `--max-results N`: 최대 결과 수 (기본: 50)
- `--case-sensitive`: 대소문자 구분

**출력 예시:**

```json
{
  "rootDir": ".",
  "query": "add",
  "results": [
    {
      "filePath": "Calculator.java",
      "symbolId": "Method#com.example.Calculator#add(int,int):int|start:10|end:12",
      "kind": "method",
      "qualifiedName": "com.example.Calculator#add",
      "startLine": 10,
      "endLine": 12,
      "signatureText": "public int add(int a, int b)"
    }
  ]
}
```

## 캐시

- **캐시 위치**: `.mcp-java-index-cache/` (현재 작업 디렉토리)
- **환경변수로 변경 가능**: `MCP_JAVA_INDEX_CACHE_ROOT`

```powershell
# Windows
$env:MCP_JAVA_INDEX_CACHE_ROOT = "C:\path\to\cache"

# macOS/Linux
export MCP_JAVA_INDEX_CACHE_ROOT="/path/to/cache"
```

## 테스트

```powershell
# Windows
.\.venv\Scripts\python -m pip install -r requirements-dev.txt
.\.venv\Scripts\python -m pytest

# macOS/Linux
./.venv/bin/python -m pip install pytest
./.venv/bin/python -m pytest
```

## 문제 해결

### `python` 명령어를 찾을 수 없음

**Windows:**

- Python 설치 시 "Add Python to PATH" 체크했는지 확인
- 또는 `python` 대신 `py` 사용: `py -m venv .venv`

**macOS/Linux:**

- `python` 대신 `python3` 사용

### PowerShell 실행 정책 오류

`Activate.ps1` 실행이 막히는 경우, activate 없이 직접 실행하세요:

```powershell
.\.venv\Scripts\python -m cli.main index test.java
```

### 모듈을 찾을 수 없음 (ModuleNotFoundError)

가상환경이 활성화되지 않았거나 의존성이 설치되지 않은 경우:

```powershell
# Windows
.\.venv\Scripts\python -m pip install -r requirements.txt

# macOS/Linux
./.venv/bin/python -m pip install -r requirements.txt
```

## 기술 스택

- **Python 3.10+**: 메인 언어
- **Tree-sitter**: 빠르고 정확한 구문 분석
- **tree-sitter-java**: Java 언어 지원

## 제한사항

- 의미론적 타입 해석이나 전체 Java 컴파일은 수행하지 않습니다
- 심볼 ID는 파일이 변경되지 않은 경우에만 안정적입니다
- 인터페이스 `extends` 목록은 쉼표로 구분된 문자열로 반환됩니다

## 라이선스

MIT

## 관련 프로젝트

이 도구는 MCP 서버로도 제공됩니다:

- **mcp-java-indexer**: MCP 프로토콜을 통해 Cursor, Claude 등에서 사용 가능
