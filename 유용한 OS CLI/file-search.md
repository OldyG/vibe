# 파일 검색

파일명이나 패턴으로 파일을 찾는 명령어입니다.

---

## 📋 기본 사용법

### Windows (PowerShell)

#### 파일명으로 검색

```powershell
Get-ChildItem -Recurse -Filter "*Service.java"
```

#### 여러 패턴 검색

```powershell
Get-ChildItem -Recurse -Include *Service.java,*Controller.java,*Repository.java
```

---

### macOS / Linux

#### 파일명으로 검색

```bash
find . -name "*Service.java"
```

#### 대소문자 구분 없이

```bash
find . -iname "*service.java"
```

---

## 🔥 고급 사용법

### Windows

#### 특정 디렉토리 제외

```powershell
Get-ChildItem -Recurse -Filter *.java |
    Where-Object {$_.FullName -notmatch "\\test\\|\\target\\"}
```

#### 파일 크기로 필터링 (1MB 이상)

```powershell
Get-ChildItem -Recurse *.java |
    Where-Object {$_.Length -gt 1MB}
```

---

### macOS / Linux

#### 특정 디렉토리 제외

```bash
find . -name "*.java" -not -path "*/test/*" -not -path "*/target/*"
```

#### 빈 파일 찾기

```bash
find . -name "*.java" -empty
```

---

## 📚 관련 명령어

- [텍스트 검색](./text-search.md) - 파일 내용으로 검색
- [파일 줄 수 확인](./file-line-count.md) - 파일 크기 확인
