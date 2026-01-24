# 파일 줄 수 확인

파일의 코드 줄 수를 확인하는 명령어입니다. AI가 파일 크기를 빠르게 파악할 때 가장 유용합니다.

---

## 📋 기본 사용법

### Windows (PowerShell)

#### 단일 파일

```powershell
(Get-Content YourFile.java | Measure-Object -Line).Lines
```

**출력:**

```
272
```

#### 현재 디렉토리의 모든 .java 파일

```powershell
Get-ChildItem *.java | ForEach-Object {
    "{0,-40} {1,5}" -f $_.Name, (Get-Content $_ | Measure-Object -Line).Lines
}
```

**출력:**

```
EmlLabelPropertyService.java              272
EmlLabelMapper.java                       150
UserService.java                          450
```

---

### macOS / Linux

#### 단일 파일

```bash
wc -l YourFile.java
```

**출력:**

```
272 YourFile.java
```

#### 현재 디렉토리의 모든 .java 파일

```bash
wc -l *.java
```

**출력:**

```
  272 EmlLabelPropertyService.java
  150 EmlLabelMapper.java
  450 UserService.java
  872 total
```

---

## 🔥 고급 사용법

### Windows

#### 재귀적으로 모든 .java 파일 줄 수

```powershell
Get-ChildItem -Recurse *.java | ForEach-Object {
    $lines = (Get-Content $_.FullName | Measure-Object -Line).Lines
    [PSCustomObject]@{
        File = $_.FullName.Replace((Get-Location).Path + "\", "")
        Lines = $lines
    }
} | Sort-Object Lines -Descending | Format-Table -AutoSize
```

#### JSON 형식으로 출력

```powershell
Get-ChildItem *.java | ForEach-Object {
    [PSCustomObject]@{
        file = $_.Name
        lines = (Get-Content $_.FullName | Measure-Object -Line).Lines
    }
} | ConvertTo-Json
```

**출력:**

```json
[
  {
    "file": "EmlLabelPropertyService.java",
    "lines": 272
  },
  {
    "file": "EmlLabelMapper.java",
    "lines": 150
  }
]
```

#### 특정 줄 수 이상 파일만 (1000줄 이상)

```powershell
Get-ChildItem -Recurse *.java | Where-Object {
    (Get-Content $_.FullName | Measure-Object -Line).Lines -gt 1000
} | ForEach-Object {
    "{0,-60} {1,5}" -f $_.FullName, (Get-Content $_.FullName | Measure-Object -Line).Lines
}
```

---

### macOS / Linux

#### 재귀적으로 모든 .java 파일 줄 수

```bash
find . -name "*.java" -exec wc -l {} + | sort -rn
```

#### 파일명만 깔끔하게

```bash
for file in *.java; do
    lines=$(wc -l < "$file")
    printf "%-40s %5d\n" "$file" "$lines"
done
```

#### JSON 형식으로 출력

```bash
echo "["
first=true
for file in *.java; do
    lines=$(wc -l < "$file")
    if [ "$first" = true ]; then
        first=false
    else
        echo ","
    fi
    printf '  {"file": "%s", "lines": %d}' "$file" "$lines"
done
echo ""
echo "]"
```

#### 특정 줄 수 이상 파일만 (1000줄 이상)

```bash
find . -name "*.java" -exec sh -c '
    lines=$(wc -l < "$1")
    if [ $lines -gt 1000 ]; then
        printf "%-60s %5d\n" "$1" "$lines"
    fi
' _ {} \;
```

---

## 💡 실용 예시

### 예시 1: 큰 파일 찾기 (리팩토링 대상)

**Windows:**

```powershell
Get-ChildItem -Recurse *.java |
    Where-Object { (Get-Content $_.FullName | Measure-Object -Line).Lines -gt 500 } |
    Sort-Object { (Get-Content $_.FullName | Measure-Object -Line).Lines } -Descending |
    Select-Object -First 10 |
    ForEach-Object {
        "{0,-60} {1,5} lines" -f $_.FullName, (Get-Content $_.FullName | Measure-Object -Line).Lines
    }
```

**macOS/Linux:**

```bash
find . -name "*.java" -exec sh -c '
    lines=$(wc -l < "$1")
    if [ $lines -gt 500 ]; then
        echo "$lines $1"
    fi
' _ {} \; | sort -rn | head -10
```

---

### 예시 2: 디렉토리별 평균 파일 크기

**Windows:**

```powershell
Get-ChildItem -Directory | ForEach-Object {
    $files = Get-ChildItem $_.FullName -Filter *.java
    if ($files.Count -gt 0) {
        $totalLines = ($files | Get-Content | Measure-Object -Line).Lines
        $avgLines = [math]::Round($totalLines / $files.Count)
        [PSCustomObject]@{
            Directory = $_.Name
            Files = $files.Count
            TotalLines = $totalLines
            AvgLines = $avgLines
        }
    }
} | Format-Table -AutoSize
```

**macOS/Linux:**

```bash
for dir in */; do
    files=$(find "$dir" -maxdepth 1 -name "*.java" | wc -l)
    if [ $files -gt 0 ]; then
        total=$(find "$dir" -maxdepth 1 -name "*.java" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}')
        avg=$((total / files))
        printf "%-30s Files: %3d  Total: %6d  Avg: %4d\n" "$dir" "$files" "$total" "$avg"
    fi
done
```

---

### 예시 3: 파일 크기 분포 확인

**Windows:**

```powershell
$ranges = @{
    "0-100" = 0
    "101-300" = 0
    "301-500" = 0
    "501-1000" = 0
    "1000+" = 0
}

Get-ChildItem -Recurse *.java | ForEach-Object {
    $lines = (Get-Content $_.FullName | Measure-Object -Line).Lines
    if ($lines -le 100) { $ranges["0-100"]++ }
    elseif ($lines -le 300) { $ranges["101-300"]++ }
    elseif ($lines -le 500) { $ranges["301-500"]++ }
    elseif ($lines -le 1000) { $ranges["501-1000"]++ }
    else { $ranges["1000+"]++ }
}

$ranges.GetEnumerator() | Sort-Object Name | ForEach-Object {
    "{0,-15} {1,3} files" -f $_.Key, $_.Value
}
```

---

## 🎯 AI 사용 시나리오

### 시나리오 1: 파일 크기 빠르게 파악

**AI 작업:**

```powershell
# Windows
(Get-Content Service.java | Measure-Object -Line).Lines
```

**AI 판단:**

- 272줄 → "적당한 크기, 전체 읽어도 됨"
- 1500줄 → "큰 파일, java-analyzer로 구조 먼저 파악"

---

### 시나리오 2: 디렉토리 전체 파악

**AI 작업:**

```powershell
# Windows
Get-ChildItem *.java | ForEach-Object {
    "{0,-40} {1,5}" -f $_.Name, (Get-Content $_ | Measure-Object -Line).Lines
}
```

**AI 응답:**

> "이 디렉토리에는 5개 파일이 있고, 가장 큰 파일은 UserService.java (450줄)입니다."

---

## 🔧 팁 & 트릭

### Tip 1: 결과를 파일로 저장

**Windows:**

```powershell
Get-ChildItem -Recurse *.java | ForEach-Object {
    "{0},{1}" -f $_.FullName, (Get-Content $_.FullName | Measure-Object -Line).Lines
} | Out-File -FilePath line-counts.csv
```

**macOS/Linux:**

```bash
find . -name "*.java" -exec wc -l {} + > line-counts.txt
```

---

### Tip 2: 빈 줄 제외하고 세기

**Windows:**

```powershell
(Get-Content YourFile.java | Where-Object { $_.Trim() -ne "" } | Measure-Object -Line).Lines
```

**macOS/Linux:**

```bash
grep -v "^[[:space:]]*$" YourFile.java | wc -l
```

---

### Tip 3: 주석 제외하고 세기 (간단 버전)

**Windows:**

```powershell
(Get-Content YourFile.java | Where-Object {
    $_.Trim() -ne "" -and
    -not $_.Trim().StartsWith("//") -and
    -not $_.Trim().StartsWith("/*") -and
    -not $_.Trim().StartsWith("*")
} | Measure-Object -Line).Lines
```

**macOS/Linux:**

```bash
grep -v "^[[:space:]]*$" YourFile.java | grep -v "^[[:space:]]*//\|^[[:space:]]*\*" | wc -l
```

---

## 📚 관련 명령어

- [파일 크기 확인](./file-size-check.md) - 바이트 단위 파일 크기
- [디렉토리 통계](./directory-stats.md) - 디렉토리별 종합 통계
- [텍스트 검색](./text-search.md) - 특정 코드 패턴 찾기
