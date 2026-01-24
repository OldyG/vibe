# 중복 클래스명 찾기 (Java)

같은 이름의 Java 클래스가 여러 패키지에 존재하는지 확인하는 명령어입니다.

---

## 📋 기본 사용법

### Windows (PowerShell)

```powershell
Get-ChildItem -Recurse *.java | Group-Object Name |
    Where-Object {$_.Count -gt 1} |
    ForEach-Object {
        Write-Host "`n=== $($_.Name) ($($_.Count) files) ===" -ForegroundColor Yellow
        $_.Group | Select-Object FullName
    }
```

**출력:**

```
=== UserService.java (2 files) ===

FullName
--------
C:\project\api\service\UserService.java
C:\project\admin\service\UserService.java
```

---

### macOS / Linux

```bash
find . -name "*.java" -printf "%f %p\n" |
    awk '{
        files[$1] = files[$1] " " $2
        count[$1]++
    } END {
        for (name in count) {
            if (count[name] > 1) {
                print "\n=== " name " (" count[name] " files) ==="
                split(files[name], paths, " ")
                for (i in paths) {
                    if (paths[i]) print paths[i]
                }
            }
        }
    }'
```

---

## 📚 관련 명령어

- [파일 검색](./file-search.md) - 파일명으로 검색
- [Java 패키지 분석](./java-package-analysis.md) - 패키지 구조 분석
