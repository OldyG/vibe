# Java 패키지 구조 분석

Java 프로젝트의 패키지 구조를 분석하는 명령어입니다.

---

## 📋 기본 사용법

### Windows (PowerShell)

#### 모든 패키지 목록

```powershell
Get-ChildItem -Recurse *.java | ForEach-Object {
    $package = (Select-String -Path $_.FullName -Pattern "^package\s+([\w.]+);" |
        Select-Object -First 1).Matches.Groups[1].Value
    $package
} | Where-Object {$_} | Sort-Object -Unique
```

**출력:**

```
com.example.controller
com.example.service
com.example.repository
com.example.config
com.example.dto
```

---

### macOS / Linux

#### 모든 패키지 목록

```bash
grep -rh "^package " --include="*.java" . | sed 's/package //;s/;$//' | sort -u
```

---

## 🔥 고급 사용법

### Windows

#### 패키지별 파일 수

```powershell
Get-ChildItem -Recurse *.java | ForEach-Object {
    $package = (Select-String -Path $_.FullName -Pattern "^package\s+([\w.]+);" |
        Select-Object -First 1).Matches.Groups[1].Value

    if ($package) {
        [PSCustomObject]@{
            Package = $package
            File = $_.Name
        }
    }
} | Group-Object Package | ForEach-Object {
    [PSCustomObject]@{
        Package = $_.Name
        Files = $_.Count
    }
} | Sort-Object Files -Descending | Format-Table -AutoSize
```

**출력:**

```
Package                    Files
-------                    -----
com.example.service           18
com.example.controller        12
com.example.repository         8
com.example.dto               15
```

---

#### 패키지 트리 구조

```powershell
Get-ChildItem -Recurse *.java | ForEach-Object {
    (Select-String -Path $_.FullName -Pattern "^package\s+([\w.]+);" |
        Select-Object -First 1).Matches.Groups[1].Value
} | Where-Object {$_} | Sort-Object -Unique | ForEach-Object {
    $depth = ($_ -split '\.').Count - 1
    $indent = "  " * $depth
    $name = ($_ -split '\.')[-1]
    "$indent$name"
}
```

---

### macOS / Linux

#### 패키지별 파일 수

```bash
grep -rh "^package " --include="*.java" . |
    sed 's/package //;s/;$//' |
    sort | uniq -c |
    sort -rn |
    awk '{printf "%-40s %3d files\n", $2, $1}'
```

---

## 💡 실용 예시

### 예시 1: 최상위 패키지 확인

```powershell
# Windows
Get-ChildItem -Recurse *.java | ForEach-Object {
    (Select-String -Path $_.FullName -Pattern "^package\s+([\w.]+);" |
        Select-Object -First 1).Matches.Groups[1].Value -split '\.' | Select-Object -First 3
} | Where-Object {$_} | Group-Object | Select-Object Name, Count | Sort-Object Count -Descending
```

---

## 📚 관련 명령어

- [Java Import 분석](./java-import-analysis.md) - Import 문 분석
- [디렉토리 통계](./directory-stats.md) - 디렉토리별 통계
