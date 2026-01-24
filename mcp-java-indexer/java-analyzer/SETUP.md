# Java Analyzer 설치 가이드 (AI용)

이 문서는 AI가 `java-analyzer`를 처음 설치하고 실행할 때 따라야 할 **단계별 체크리스트**입니다.

---

## ⚠️ 중요: 설치 전 필수 확인사항

### 1단계: Python 설치 확인

**반드시 먼저 실행:**

```powershell
# Windows
python --version
```

```bash
# macOS/Linux
python3 --version
```

**예상 출력:**

```
Python 3.10.x 또는 Python 3.11.x 또는 Python 3.12.x
```

**❌ 만약 "python을 찾을 수 없습니다" 에러가 나면:**

- Python이 설치되지 않았거나 PATH에 없음
- 아래 "Python 설치" 섹션으로 이동

**✅ Python 3.10 이상이 출력되면:**

- 다음 단계로 진행

---

## 2단계: 의존성 설치 (필수!)

**이 단계를 건너뛰면 `ModuleNotFoundError: No module named 'tree_sitter'` 에러 발생!**

### 옵션 A: 가상환경 사용 (권장)

#### Windows (PowerShell)

```powershell
# 1. java-analyzer 디렉토리로 이동
cd path\to\java-analyzer

# 2. 가상환경 생성
python -m venv .venv

# 3. pip 업그레이드
.\.venv\Scripts\python -m pip install --upgrade pip

# 4. 의존성 설치 (tree-sitter, tree_sitter_java)
.\.venv\Scripts\python -m pip install -r requirements.txt
```

**설치 성공 확인:**

```powershell
.\.venv\Scripts\python -c "import tree_sitter; print('✅ tree-sitter installed')"
```

**예상 출력:**

```
✅ tree-sitter installed
```

#### macOS / Linux (bash/zsh)

```bash
# 1. java-analyzer 디렉토리로 이동
cd path/to/java-analyzer

# 2. 가상환경 생성
python3 -m venv .venv

# 3. pip 업그레이드
./.venv/bin/python -m pip install --upgrade pip

# 4. 의존성 설치 (tree-sitter, tree_sitter_java)
./.venv/bin/python -m pip install -r requirements.txt
```

**설치 성공 확인:**

```bash
./.venv/bin/python -c "import tree_sitter; print('✅ tree-sitter installed')"
```

**예상 출력:**

```
✅ tree-sitter installed
```

---

### 옵션 B: 시스템 전역 설치 (간단하지만 비권장)

#### Windows

```powershell
cd path\to\java-analyzer
python -m pip install -r requirements.txt
```

#### macOS / Linux

```bash
cd path/to/java-analyzer
python3 -m pip install -r requirements.txt
```

**설치 성공 확인:**

```powershell
# Windows
python -c "import tree_sitter; print('✅ tree-sitter installed')"

# macOS/Linux
python3 -c "import tree_sitter; print('✅ tree-sitter installed')"
```

---

## 3단계: CLI 실행 테스트

### 가상환경 사용 시

#### Windows

```powershell
# java-analyzer 디렉토리에서
.\.venv\Scripts\python -m cli.main index tests\fixtures\SimpleClass.java --javadoc-preview-chars 80
```

#### macOS / Linux

```bash
# java-analyzer 디렉토리에서
./.venv/bin/python -m cli.main index tests/fixtures/SimpleClass.java --javadoc-preview-chars 80
```

### 시스템 전역 설치 시

#### Windows

```powershell
# java-analyzer 디렉토리에서
python -m cli.main index tests\fixtures\SimpleClass.java --javadoc-preview-chars 80
```

#### macOS / Linux

```bash
# java-analyzer 디렉토리에서
python3 -m cli.main index tests/fixtures/SimpleClass.java --javadoc-preview-chars 80
```

**예상 출력:**

```json
{
  "filePath": "tests/fixtures/SimpleClass.java",
  "language": "java",
  "lineCount": 33,
  "classes": [
    ...
  ]
}
```

**✅ JSON 출력이 나오면 설치 성공!**

---

## 🚨 자주 발생하는 에러와 해결법

### 에러 1: `ModuleNotFoundError: No module named 'tree_sitter'`

**원인:** 의존성이 설치되지 않음

**해결:**

```powershell
# 가상환경 사용 시 (Windows)
.\.venv\Scripts\python -m pip install -r requirements.txt

# 가상환경 사용 시 (macOS/Linux)
./.venv/bin/python -m pip install -r requirements.txt

# 시스템 전역 사용 시
python -m pip install -r requirements.txt
```

---

### 에러 2: `python: command not found`

**원인:** Python이 설치되지 않았거나 PATH에 없음

**해결:**

**Windows:**

1. https://www.python.org/downloads/ 에서 Python 설치
2. 설치 시 **"Add Python to PATH" 반드시 체크**
3. 또는 `python` 대신 `py` 사용

**macOS:**

```bash
brew install python@3.12
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

---

### 에러 3: `No module named 'cli'`

**원인:** `java-analyzer` 디렉토리가 아닌 다른 곳에서 실행

**해결:**

```powershell
# java-analyzer 디렉토리로 이동
cd path\to\java-analyzer

# 그 다음 CLI 실행
.\.venv\Scripts\python -m cli.main index YourFile.java
```

---

### 에러 4: PowerShell 실행 정책 오류

**원인:** Windows PowerShell 실행 정책

**해결:** activate 스크립트 없이 직접 실행

```powershell
# activate 대신 전체 경로 사용
.\.venv\Scripts\python -m cli.main index YourFile.java
```

---

## 📋 AI를 위한 빠른 체크리스트

설치 시 이 순서대로 실행하세요:

### ✅ Windows 체크리스트

```powershell
# [ ] 1. Python 확인
python --version

# [ ] 2. java-analyzer 디렉토리로 이동
cd path\to\java-analyzer

# [ ] 3. 가상환경 생성
python -m venv .venv

# [ ] 4. 의존성 설치
.\.venv\Scripts\python -m pip install -r requirements.txt

# [ ] 5. 설치 확인
.\.venv\Scripts\python -c "import tree_sitter; print('OK')"

# [ ] 6. 테스트 실행
.\.venv\Scripts\python -m cli.main index tests\fixtures\SimpleClass.java
```

### ✅ macOS/Linux 체크리스트

```bash
# [ ] 1. Python 확인
python3 --version

# [ ] 2. java-analyzer 디렉토리로 이동
cd path/to/java-analyzer

# [ ] 3. 가상환경 생성
python3 -m venv .venv

# [ ] 4. 의존성 설치
./.venv/bin/python -m pip install -r requirements.txt

# [ ] 5. 설치 확인
./.venv/bin/python -c "import tree_sitter; print('OK')"

# [ ] 6. 테스트 실행
./.venv/bin/python -m cli.main index tests/fixtures/SimpleClass.java
```

---

## 🎯 핵심 요약

1. **Python 3.10+ 필수**
2. **`pip install -r requirements.txt` 반드시 실행** (tree-sitter 설치)
3. **`java-analyzer` 디렉토리에서 실행**
4. **가상환경 사용 권장** (`.venv`)

이 4가지만 지키면 100% 성공합니다! 🚀
