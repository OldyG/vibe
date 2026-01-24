# 최근 수정 파일 찾기

최근 N일 내에 수정된 파일을 찾는 명령어입니다. 최근 작업한 파일을 빠르게 찾을 때 유용합니다.

---

## 📋 기본 사용법

### Windows (PowerShell)

#### 최근 7일 내 수정된 파일

```powershell
Get-ChildItem -Recurse *.java |
    Where-Object {$_.LastWriteTime -gt (Get-Date).AddDays(-7)} |
    Select-Object Name, LastWriteTime |
    Sort-Object LastWriteTime -Descending
```

---

### macOS / Linux

#### 최근 7일 내 수정된 파일

```bash
find . -name "*.java" -mtime -7 -ls
```

---

## 🔥 고급 사용법

### Windows

#### 수정 시간대별 그룹화

```powershell
Get-ChildItem -Recurse *.java | Group-Object {
    $days = ((Get-Date) - $_.LastWriteTime).Days
    if ($days -eq 0) { "Today" }
    elseif ($days -eq 1) { "Yesterday" }
    elseif ($days -le 7) { "This Week" }
    elseif ($days -le 30) { "This Month" }
    else { "Older" }
} | Select-Object Name, Count | Format-Table -AutoSize
```

**출력:**

```
Name        Count
----        -----
Today          5
Yesterday      8
This Week     12
This Month    18
Older         43
```

---

### macOS / Linux

#### 오늘 수정된 파일

```bash
find . -name "*.java" -mtime 0
```

#### 최근 3일 내 수정, 줄 수 포함

```bash
find . -name "*.java" -mtime -3 -exec sh -c '
    lines=$(wc -l < "$1")
    printf "%-60s %5d lines  %s\n" "$1" "$lines" "$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$1")"
' _ {} \;
```

---

## 📚 관련 명령어

- [파일 검색](./file-search.md) - 파일명으로 검색
- [디렉토리 통계](./directory-stats.md) - 디렉토리별 통계
