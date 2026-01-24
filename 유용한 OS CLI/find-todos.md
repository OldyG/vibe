# TODO/FIXME 찾기

코드 주석에서 TODO, FIXME, HACK 등의 태그를 찾아 남은 작업을 확인하는 명령어입니다.

---

## 📋 기본 사용법

### Windows (PowerShell)

```powershell
Get-ChildItem -Recurse *.java | Select-String "TODO|FIXME|HACK" |
    Select-Object Filename, LineNumber, Line | Format-Table -AutoSize
```

**출력:**

```
Filename           LineNumber Line
--------           ---------- ----
UserService.java           45 // TODO: 리팩토링 필요
OrderService.java          78 // FIXME: 예외 처리 추가
PaymentService.java       120 // HACK: 임시 해결책
```

---

### macOS / Linux

```bash
grep -rn "TODO\|FIXME\|HACK" --include="*.java" .
```

**출력:**

```
./UserService.java:45:// TODO: 리팩토링 필요
./OrderService.java:78:// FIXME: 예외 처리 추가
./PaymentService.java:120:// HACK: 임시 해결책
```

---

## 🔥 고급 사용법

### Windows

#### 태그별로 그룹화

```powershell
Get-ChildItem -Recurse *.java | Select-String "TODO|FIXME|HACK" |
    ForEach-Object {
        $tag = if ($_.Line -match "TODO") { "TODO" }
               elseif ($_.Line -match "FIXME") { "FIXME" }
               elseif ($_.Line -match "HACK") { "HACK" }

        [PSCustomObject]@{
            Tag = $tag
            File = $_.Filename
            Line = $_.LineNumber
            Content = $_.Line.Trim()
        }
    } | Group-Object Tag | ForEach-Object {
        Write-Host "`n=== $($_.Name) ($($_.Count) items) ===" -ForegroundColor Yellow
        $_.Group | Format-Table File, Line, Content -AutoSize
    }
```

---

#### 파일로 저장 (마크다운 형식)

```powershell
$output = "# TODO List`n`n"

Get-ChildItem -Recurse *.java | Select-String "TODO|FIXME|HACK" |
    Group-Object Filename | ForEach-Object {
        $output += "## $($_.Name)`n`n"
        $_.Group | ForEach-Object {
            $output += "- Line $($_.LineNumber): $($_.Line.Trim())`n"
        }
        $output += "`n"
    }

$output | Out-File -FilePath TODO.md
```

---

### macOS / Linux

#### 태그별로 그룹화

```bash
echo "=== TODO ==="
grep -rn "TODO" --include="*.java" . | head -20

echo -e "\n=== FIXME ==="
grep -rn "FIXME" --include="*.java" . | head -20

echo -e "\n=== HACK ==="
grep -rn "HACK" --include="*.java" . | head -20
```

---

#### 파일로 저장 (마크다운 형식)

```bash
echo "# TODO List" > TODO.md
echo "" >> TODO.md

grep -rn "TODO\|FIXME\|HACK" --include="*.java" . |
    awk -F: '{
        if (file != $1) {
            if (file != "") print ""
            file = $1
            print "## " file
            print ""
        }
        print "- Line " $2 ": " $3
    }' >> TODO.md
```

---

## 💡 실용 예시

### 예시 1: 우선순위별 정리

**Windows:**

```powershell
Get-ChildItem -Recurse *.java | Select-String "TODO|FIXME|HACK|XXX|NOTE" |
    ForEach-Object {
        $priority = if ($_.Line -match "FIXME|XXX") { "High" }
                    elseif ($_.Line -match "TODO") { "Medium" }
                    else { "Low" }

        [PSCustomObject]@{
            Priority = $priority
            File = $_.Filename
            Line = $_.LineNumber
            Content = $_.Line.Trim()
        }
    } | Sort-Object Priority | Format-Table -AutoSize
```

---

### 예시 2: 통계 확인

**Windows:**

```powershell
$stats = @{
    TODO = 0
    FIXME = 0
    HACK = 0
}

Get-ChildItem -Recurse *.java | Select-String "TODO|FIXME|HACK" |
    ForEach-Object {
        if ($_.Line -match "TODO") { $stats.TODO++ }
        if ($_.Line -match "FIXME") { $stats.FIXME++ }
        if ($_.Line -match "HACK") { $stats.HACK++ }
    }

Write-Host "`n=== TODO Statistics ===" -ForegroundColor Cyan
$stats.GetEnumerator() | Sort-Object Value -Descending | ForEach-Object {
    "{0,-10} {1,3} items" -f $_.Key, $_.Value
}
```

**macOS/Linux:**

```bash
echo "=== TODO Statistics ==="
echo "TODO:  $(grep -rc "TODO" --include="*.java" . | awk -F: '{sum+=$2} END {print sum}')"
echo "FIXME: $(grep -rc "FIXME" --include="*.java" . | awk -F: '{sum+=$2} END {print sum}')"
echo "HACK:  $(grep -rc "HACK" --include="*.java" . | awk -F: '{sum+=$2} END {print sum}')"
```

---

## 📚 관련 명령어

- [텍스트 검색](./text-search.md) - 일반 텍스트 검색
- [파일 검색](./file-search.md) - 파일명으로 검색
