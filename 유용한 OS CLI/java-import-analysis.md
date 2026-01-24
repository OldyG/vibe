# Java Import 분석

Java 파일의 import 문을 분석하여 가장 많이 사용되는 라이브러리를 확인하는 명령어입니다.

---

## 📋 기본 사용법

### Windows (PowerShell)

#### 모든 import 문 추출

```powershell
Get-ChildItem -Recurse *.java | ForEach-Object {
    Select-String -Path $_.FullName -Pattern "^import\s+([\w.]+);" |
        ForEach-Object { $_.Matches.Groups[1].Value }
} | Group-Object | Sort-Object Count -Descending | Select-Object -First 20 |
    Format-Table Count, Name -AutoSize
```

**출력:**

```
Count Name
----- ----
   45 java.util.List
   38 org.springframework.stereotype.Service
   32 lombok.RequiredArgsConstructor
   28 java.util.Optional
```

---

### macOS / Linux

#### 가장 많이 사용되는 import Top 20

```bash
grep -rh "^import " --include="*.java" . |
    sed 's/import //;s/;$//' |
    sort | uniq -c | sort -rn | head -20
```

---

## 🔥 고급 사용법

### Windows

#### 패키지별 그룹화

```powershell
Get-ChildItem -Recurse *.java | ForEach-Object {
    Select-String -Path $_.FullName -Pattern "^import\s+([\w.]+);" |
        ForEach-Object {
            $import = $_.Matches.Groups[1].Value
            $package = ($import -split '\.')[0..2] -join '.'
            $package
        }
} | Group-Object | Sort-Object Count -Descending |
    Select-Object -First 10 | Format-Table Count, Name -AutoSize
```

**출력:**

```
Count Name
----- ----
  150 org.springframework.stereotype
   98 java.util
   76 lombok
   54 com.example.dto
```

---

### macOS / Linux

#### Spring 관련 import만

```bash
grep -rh "^import " --include="*.java" . |
    grep "springframework" |
    sed 's/import //;s/;$//' |
    sort | uniq -c | sort -rn
```

---

## 💡 실용 예시

### 예시 1: 외부 라이브러리 의존성 확인

```powershell
# Windows - java, javax 제외
Get-ChildItem -Recurse *.java | ForEach-Object {
    Select-String -Path $_.FullName -Pattern "^import\s+([\w.]+);" |
        ForEach-Object {
            $import = $_.Matches.Groups[1].Value
            if ($import -notmatch "^java\.|^javax\.") {
                ($import -split '\.')[0..1] -join '.'
            }
        }
} | Group-Object | Sort-Object Count -Descending | Format-Table Count, Name -AutoSize
```

---

## 📚 관련 명령어

- [Java 패키지 분석](./java-package-analysis.md) - 패키지 구조 분석
- [텍스트 검색](./text-search.md) - 일반 텍스트 검색
