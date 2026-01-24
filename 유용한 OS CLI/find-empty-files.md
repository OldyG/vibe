# 빈 파일 찾기

빈 파일 또는 거의 빈 파일을 찾는 명령어입니다. 불필요한 파일을 정리할 때 유용합니다.

---

## 📋 기본 사용법

### Windows (PowerShell)

#### 완전히 빈 파일 (0 바이트)

```powershell
Get-ChildItem -Recurse *.java | Where-Object {$_.Length -eq 0}
```

#### 거의 빈 파일 (10줄 이하)

```powershell
Get-ChildItem -Recurse *.java | Where-Object {
    (Get-Content $_.FullName | Measure-Object -Line).Lines -le 10
} | Select-Object Name, @{Name="Lines";Expression={(Get-Content $_.FullName | Measure-Object -Line).Lines}}
```

---

### macOS / Linux

#### 완전히 빈 파일

```bash
find . -name "*.java" -empty
```

#### 거의 빈 파일 (10줄 이하)

```bash
find . -name "*.java" -exec sh -c '
    lines=$(wc -l < "$1")
    if [ $lines -le 10 ]; then
        echo "$1: $lines lines"
    fi
' _ {} \;
```

---

## 📚 관련 명령어

- [파일 크기 확인](./file-size-check.md) - 바이트 단위 크기
- [파일 줄 수 확인](./file-line-count.md) - 코드 줄 수
