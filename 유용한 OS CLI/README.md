# 유용한 OS CLI 명령어 모음

개발자를 위한 실용적인 CLI 명령어 모음입니다. 특히 Java 개발 시 유용한 명령어들을 중심으로 정리했습니다.

## 📚 카테고리

### 📊 파일 분석

- [파일 줄 수 확인](./file-line-count.md) - 단일/다중 파일의 코드 줄 수 확인
- [파일 크기 확인](./file-size-check.md) - 큰 파일 찾기, 파일 크기 통계
- [디렉토리 통계](./directory-stats.md) - 디렉토리별 파일 수, 줄 수 통계

### 🔍 코드 검색

- [파일 검색](./file-search.md) - 파일명, 패턴으로 파일 찾기
- [텍스트 검색](./text-search.md) - 코드 내용으로 파일 찾기
- [TODO/FIXME 찾기](./find-todos.md) - 주석에서 TODO, FIXME 추출

### 📦 Java 전용

- [패키지 구조 분석](./java-package-analysis.md) - 패키지 목록, 구조 파악
- [Import 분석](./java-import-analysis.md) - 가장 많이 사용되는 라이브러리 확인
- [중복 클래스명 찾기](./java-duplicate-classes.md) - 같은 이름의 클래스 찾기

### 🕐 시간 기반

- [최근 수정 파일](./recently-modified.md) - 최근 N일 내 수정된 파일 찾기
- [오래된 파일 찾기](./old-files.md) - 오랫동안 수정되지 않은 파일 찾기

### 🧹 유틸리티

- [빈 파일 찾기](./find-empty-files.md) - 빈 파일 또는 거의 빈 파일 찾기
- [파일 비교](./file-comparison.md) - 두 디렉토리 비교, 차이점 찾기
- [배치 파일 이름 변경](./batch-rename.md) - 여러 파일 한 번에 이름 변경

---

## 🚀 빠른 시작

### Windows 사용자

대부분의 명령어는 **PowerShell**을 사용합니다.

- Windows 11: 기본 터미널이 PowerShell
- Windows 10: `Win + X` → "Windows PowerShell" 선택

### macOS/Linux 사용자

**Terminal** 또는 **iTerm2**를 사용합니다.

- macOS: `Cmd + Space` → "Terminal" 입력
- Linux: `Ctrl + Alt + T`

---

## 💡 사용 팁

### 1. 현재 디렉토리 확인

```powershell
# Windows
pwd

# macOS/Linux
pwd
```

### 2. 디렉토리 이동

```powershell
# Windows
cd C:\path\to\project

# macOS/Linux
cd /path/to/project
```

### 3. 결과를 파일로 저장

```powershell
# Windows
명령어 > output.txt

# macOS/Linux
명령어 > output.txt
```

---

## 📖 문서 읽는 법

각 문서는 다음 구조로 작성되어 있습니다:

1. **개요** - 명령어가 무엇을 하는지
2. **기본 사용법** - 가장 많이 쓰는 패턴
3. **고급 사용법** - 옵션, 필터링 등
4. **실용 예시** - 실제 프로젝트에서 사용하는 예시
5. **팁 & 트릭** - 알아두면 유용한 정보

---

## 🎯 추천 명령어 (Top 5)

### 1. [파일 줄 수 확인](./file-line-count.md)

AI가 파일 크기를 빠르게 파악할 때 가장 유용

### 2. [디렉토리 통계](./directory-stats.md)

프로젝트 구조를 한눈에 파악

### 3. [텍스트 검색](./text-search.md)

특정 코드 패턴을 찾을 때 필수

### 4. [최근 수정 파일](./recently-modified.md)

최근 작업한 파일 빠르게 찾기

### 5. [TODO/FIXME 찾기](./find-todos.md)

남은 작업 확인

---

## 🤝 기여

새로운 유용한 명령어를 발견하셨나요?
이 문서에 추가해주세요!

---

## 📝 라이선스

MIT
