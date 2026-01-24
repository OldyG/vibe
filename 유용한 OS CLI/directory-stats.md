# 디렉토리 통계

디렉토리별 파일 수, 코드 줄 수, 평균 파일 크기 등의 통계를 확인하는 명령어입니다. 프로젝트 구조를 한눈에 파악할 때 유용합니다.

---

## 📋 기본 사용법

### Windows (PowerShell)

#### 현재 디렉토리의 하위 디렉토리별 통계

```powershell
Get-ChildItem -Directory | ForEach-Object {
    $files = Get-ChildItem $_.FullName -Filter *.java
    if ($files.Count -gt 0) {
        $totalLines = ($files | Get-Content | Measure-Object -Line).Lines
        [PSCustomObject]@{
            Directory = $_.Name
            Files = $files.Count
            Lines = $totalLines
        }
    }
} | Format-Table -AutoSize
```

**출력:**

```
Directory    Files  Lines
---------    -----  -----
controller      12   3450
service         18   5230
repository       8   1200
config           5    850
```

---

### macOS / Linux

#### 현재 디렉토리의 하위 디렉토리별 통계

```bash
for dir in */; do
    files=$(find "$dir" -maxdepth 1 -name "*.java" | wc -l)
    if [ $files -gt 0 ]; then
        lines=$(find "$dir" -maxdepth 1 -name "*.java" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}')
        printf "%-30s Files: %3d  Lines: %6d\n" "$dir" "$files" "$lines"
    fi
done
```

**출력:**

```
controller/                    Files:  12  Lines:   3450
service/                       Files:  18  Lines:   5230
repository/                    Files:   8  Lines:   1200
config/                        Files:   5  Lines:    850
```

---

## 🔥 고급 사용법

### Windows

#### 평균 파일 크기 포함

```powershell
Get-ChildItem -Directory | ForEach-Object {
    $files = Get-ChildItem $_.FullName -Filter *.java -Recurse
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
} | Sort-Object TotalLines -Descending | Format-Table -AutoSize
```

**출력:**

```
Directory    Files  TotalLines  AvgLines
---------    -----  ----------  --------
service         18        5230       291
controller      12        3450       288
repository       8        1200       150
config           5         850       170
```

---

#### 재귀적 통계 (모든 하위 디렉토리)

```powershell
$stats = @{}

Get-ChildItem -Recurse *.java | ForEach-Object {
    $dir = $_.DirectoryName
    if (-not $stats.ContainsKey($dir)) {
        $stats[$dir] = @{
            Files = 0
            Lines = 0
        }
    }
    $stats[$dir].Files++
    $stats[$dir].Lines += (Get-Content $_.FullName | Measure-Object -Line).Lines
}

$stats.GetEnumerator() | ForEach-Object {
    [PSCustomObject]@{
        Directory = $_.Key.Replace((Get-Location).Path + "\", "")
        Files = $_.Value.Files
        Lines = $_.Value.Lines
    }
} | Sort-Object Lines -Descending | Format-Table -AutoSize
```

---

#### 파일 크기 분포 포함

```powershell
Get-ChildItem -Directory | ForEach-Object {
    $files = Get-ChildItem $_.FullName -Filter *.java
    if ($files.Count -gt 0) {
        $small = ($files | Where-Object { (Get-Content $_.FullName | Measure-Object -Line).Lines -le 100 }).Count
        $medium = ($files | Where-Object {
            $lines = (Get-Content $_.FullName | Measure-Object -Line).Lines
            $lines -gt 100 -and $lines -le 300
        }).Count
        $large = ($files | Where-Object { (Get-Content $_.FullName | Measure-Object -Line).Lines -gt 300 }).Count

        [PSCustomObject]@{
            Directory = $_.Name
            Total = $files.Count
            Small = $small
            Medium = $medium
            Large = $large
        }
    }
} | Format-Table -AutoSize
```

**출력:**

```
Directory    Total  Small  Medium  Large
---------    -----  -----  ------  -----
controller      12      3       6      3
service         18      5      10      3
repository       8      6       2      0
```

---

### macOS / Linux

#### 평균 파일 크기 포함

```bash
for dir in */; do
    files=$(find "$dir" -name "*.java" | wc -l)
    if [ $files -gt 0 ]; then
        total=$(find "$dir" -name "*.java" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}')
        avg=$((total / files))
        printf "%-30s Files: %3d  Total: %6d  Avg: %4d\n" "$dir" "$files" "$total" "$avg"
    fi
done | sort -k5 -rn
```

---

#### 트리 구조로 표시

```bash
find . -name "*.java" -printf "%h\n" | sort | uniq -c | awk '{printf "%4d files  %s\n", $1, $2}'
```

**출력:**

```
  12 files  ./controller
  18 files  ./service
   8 files  ./repository
   5 files  ./config
```

---

## 💡 실용 예시

### 예시 1: 프로젝트 전체 통계

**Windows:**

```powershell
$allFiles = Get-ChildItem -Recurse *.java
$totalLines = ($allFiles | Get-Content | Measure-Object -Line).Lines

[PSCustomObject]@{
    TotalFiles = $allFiles.Count
    TotalLines = $totalLines
    AvgLinesPerFile = [math]::Round($totalLines / $allFiles.Count)
    LargestFile = ($allFiles | ForEach-Object {
        [PSCustomObject]@{
            Name = $_.Name
            Lines = (Get-Content $_.FullName | Measure-Object -Line).Lines
        }
    } | Sort-Object Lines -Descending | Select-Object -First 1).Name
} | Format-List
```

**출력:**

```
TotalFiles      : 43
TotalLines      : 10730
AvgLinesPerFile : 249
LargestFile     : UserServiceImpl.java
```

---

### 예시 2: 패키지별 통계 (Java)

**Windows:**

```powershell
Get-ChildItem -Recurse *.java | ForEach-Object {
    $package = (Select-String -Path $_.FullName -Pattern "^package\s+([\w.]+);" |
        Select-Object -First 1).Matches.Groups[1].Value

    if ($package) {
        [PSCustomObject]@{
            Package = $package
            File = $_.Name
            Lines = (Get-Content $_.FullName | Measure-Object -Line).Lines
        }
    }
} | Group-Object Package | ForEach-Object {
    [PSCustomObject]@{
        Package = $_.Name
        Files = $_.Count
        TotalLines = ($_.Group | Measure-Object -Property Lines -Sum).Sum
    }
} | Sort-Object TotalLines -Descending | Format-Table -AutoSize
```

**macOS/Linux:**

```bash
find . -name "*.java" -exec sh -c '
    package=$(grep "^package " "$1" | sed "s/package //;s/;//")
    lines=$(wc -l < "$1")
    echo "$package|$lines"
' _ {} \; | awk -F'|' '{
    pkg[$1]++
    lines[$1]+=$2
} END {
    for (p in pkg) {
        printf "%-40s Files: %3d  Lines: %6d\n", p, pkg[p], lines[p]
    }
}' | sort -k5 -rn
```

---

### 예시 3: 시간대별 파일 분포

**Windows:**

```powershell
Get-ChildItem -Recurse *.java | Group-Object {
    if ($_.LastWriteTime -gt (Get-Date).AddDays(-7)) { "Last 7 days" }
    elseif ($_.LastWriteTime -gt (Get-Date).AddDays(-30)) { "Last 30 days" }
    elseif ($_.LastWriteTime -gt (Get-Date).AddDays(-90)) { "Last 90 days" }
    else { "Older" }
} | Select-Object Name, Count | Format-Table -AutoSize
```

**출력:**

```
Name          Count
----          -----
Last 7 days      12
Last 30 days     18
Last 90 days     8
Older            5
```

---

## 🎯 AI 사용 시나리오

### 시나리오 1: 프로젝트 구조 파악

**사용자 요청:**

> "이 프로젝트의 구조를 파악해줘"

**AI 작업:**

```powershell
# Windows
Get-ChildItem -Directory | ForEach-Object {
    $files = Get-ChildItem $_.FullName -Filter *.java -Recurse
    [PSCustomObject]@{
        Directory = $_.Name
        Files = $files.Count
        Lines = ($files | Get-Content | Measure-Object -Line).Lines
    }
} | Sort-Object Lines -Descending | Format-Table -AutoSize
```

**AI 응답:**

> "이 프로젝트는 service 패키지가 가장 크고 (18개 파일, 5230줄), controller, repository, config 순입니다."

---

### 시나리오 2: 리팩토링 우선순위 결정

**사용자 요청:**

> "어느 디렉토리부터 리팩토링해야 할까?"

**AI 작업:**

```powershell
# 평균 파일 크기가 큰 디렉토리 찾기
Get-ChildItem -Directory | ForEach-Object {
    $files = Get-ChildItem $_.FullName -Filter *.java
    if ($files.Count -gt 0) {
        $totalLines = ($files | Get-Content | Measure-Object -Line).Lines
        [PSCustomObject]@{
            Directory = $_.Name
            AvgLines = [math]::Round($totalLines / $files.Count)
        }
    }
} | Sort-Object AvgLines -Descending
```

**AI 응답:**

> "service 디렉토리의 평균 파일 크기가 291줄로 가장 크므로, 여기부터 리팩토링하는 것이 좋겠습니다."

---

## 🔧 팁 & 트릭

### Tip 1: CSV로 저장

**Windows:**

```powershell
Get-ChildItem -Directory | ForEach-Object {
    $files = Get-ChildItem $_.FullName -Filter *.java
    if ($files.Count -gt 0) {
        [PSCustomObject]@{
            Directory = $_.Name
            Files = $files.Count
            Lines = ($files | Get-Content | Measure-Object -Line).Lines
        }
    }
} | Export-Csv -Path stats.csv -NoTypeInformation
```

---

### Tip 2: 특정 확장자만 통계

**Windows:**

```powershell
# .xml 파일 통계
Get-ChildItem -Directory | ForEach-Object {
    $files = Get-ChildItem $_.FullName -Filter *.xml
    if ($files.Count -gt 0) {
        [PSCustomObject]@{
            Directory = $_.Name
            XmlFiles = $files.Count
        }
    }
} | Format-Table -AutoSize
```

---

### Tip 3: 여러 확장자 통합 통계

**Windows:**

```powershell
Get-ChildItem -Directory | ForEach-Object {
    $javaFiles = (Get-ChildItem $_.FullName -Filter *.java).Count
    $xmlFiles = (Get-ChildItem $_.FullName -Filter *.xml).Count
    $propFiles = (Get-ChildItem $_.FullName -Filter *.properties).Count

    [PSCustomObject]@{
        Directory = $_.Name
        Java = $javaFiles
        Xml = $xmlFiles
        Properties = $propFiles
        Total = $javaFiles + $xmlFiles + $propFiles
    }
} | Format-Table -AutoSize
```

---

## 📚 관련 명령어

- [파일 줄 수 확인](./file-line-count.md) - 개별 파일 줄 수
- [파일 크기 확인](./file-size-check.md) - 바이트 단위 크기
- [파일 검색](./file-search.md) - 파일명으로 검색
