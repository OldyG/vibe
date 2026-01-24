# 텍스트 검색 (Grep)

파일 내용에서 특정 텍스트를 검색하는 명령어입니다. 코드 패턴, 클래스명, 메서드명 등을 찾을 때 필수적입니다.

---

## 📋 기본 사용법

### Windows (PowerShell)

#### 현재 디렉토리에서 검색

```powershell
Get-ChildItem *.java | Select-String "public class"
```

**출력:**

```
UserService.java:10:public class UserService {
OrderService.java:15:public class OrderService {
```

#### 재귀적 검색 (하위 디렉토리 포함)

```powershell
Get-ChildItem -Recurse *.java | Select-String "public class"
```

---

### macOS / Linux

#### 현재 디렉토리에서 검색

```bash
grep "public class" *.java
```

**출력:**

```
UserService.java:public class UserService {
OrderService.java:public class OrderService {
```

#### 재귀적 검색 (하위 디렉토리 포함)

```bash
grep -r "public class" --include="*.java" .
```

---

## 🔥 고급 사용법

### Windows

#### 줄 번호 포함

```powershell
Get-ChildItem -Recurse *.java | Select-String "TODO" |
    Select-Object Filename, LineNumber, Line | Format-Table -AutoSize
```

**출력:**

```
Filename           LineNumber Line
--------           ---------- ----
UserService.java           45 // TODO: 리팩토링 필요
OrderService.java          78 // TODO: 예외 처리 추가
```

#### 대소문자 구분 없이 검색

```powershell
Get-ChildItem -Recurse *.java | Select-String "service" -CaseSensitive:$false
```

#### 여러 패턴 검색 (OR 조건)

```powershell
Get-ChildItem -Recurse *.java | Select-String "TODO|FIXME|HACK"
```

#### 정규식 사용

```powershell
# @Service 어노테이션 찾기
Get-ChildItem -Recurse *.java | Select-String "@Service\b"

# public 메서드 찾기
Get-ChildItem -Recurse *.java | Select-String "public\s+\w+\s+\w+\("
```

#### 컨텍스트 포함 (앞뒤 줄 표시)

```powershell
Get-ChildItem *.java | Select-String "public class" -Context 2,2
```

---

### macOS / Linux

#### 줄 번호 포함

```bash
grep -rn "TODO" --include="*.java" .
```

**출력:**

```
./UserService.java:45:// TODO: 리팩토링 필요
./OrderService.java:78:// TODO: 예외 처리 추가
```

#### 대소문자 구분 없이 검색

```bash
grep -ri "service" --include="*.java" .
```

#### 여러 패턴 검색 (OR 조건)

```bash
grep -rn "TODO\|FIXME\|HACK" --include="*.java" .
```

#### 정규식 사용

```bash
# @Service 어노테이션 찾기
grep -rn "@Service\b" --include="*.java" .

# public 메서드 찾기
grep -rn "public\s\+\w\+\s\+\w\+(" --include="*.java" .
```

#### 컨텍스트 포함 (앞뒤 2줄)

```bash
grep -rn -A 2 -B 2 "public class" --include="*.java" .
```

---

## 💡 실용 예시

### 예시 1: 특정 클래스 사용처 찾기

**Windows:**

```powershell
Get-ChildItem -Recurse *.java | Select-String "UserService" |
    Group-Object Filename |
    Select-Object Count, Name |
    Sort-Object Count -Descending
```

**macOS/Linux:**

```bash
grep -r "UserService" --include="*.java" . | cut -d: -f1 | sort | uniq -c | sort -rn
```

**출력:**

```
  15 ./controller/UserController.java
   8 ./service/OrderService.java
   3 ./config/AppConfig.java
```

---

### 예시 2: 모든 TODO 주석 추출

**Windows:**

```powershell
Get-ChildItem -Recurse *.java | Select-String "TODO|FIXME" |
    ForEach-Object {
        [PSCustomObject]@{
            File = $_.Filename
            Line = $_.LineNumber
            Content = $_.Line.Trim()
        }
    } | Format-Table -AutoSize
```

**macOS/Linux:**

```bash
grep -rn "TODO\|FIXME" --include="*.java" . |
    awk -F: '{printf "%-40s Line %4d: %s\n", $1, $2, $3}'
```

---

### 예시 3: 특정 어노테이션 사용 클래스 찾기

**Windows:**

```powershell
# @Service 어노테이션이 있는 클래스
Get-ChildItem -Recurse *.java | Select-String "@Service" |
    ForEach-Object {
        $file = $_.Filename
        $content = Get-Content $_.Path
        $className = ($content | Select-String "public class (\w+)" |
            Select-Object -First 1).Matches.Groups[1].Value
        [PSCustomObject]@{
            File = $file
            Class = $className
        }
    } | Format-Table -AutoSize
```

**macOS/Linux:**

```bash
grep -l "@Service" --include="*.java" -r . | while read file; do
    class=$(grep "public class" "$file" | sed 's/.*class \(\w\+\).*/\1/')
    echo "$file: $class"
done
```

---

### 예시 4: SQL 쿼리 찾기

**Windows:**

```powershell
Get-ChildItem -Recurse *.java | Select-String "SELECT|INSERT|UPDATE|DELETE" -CaseSensitive:$false |
    Select-Object Filename, LineNumber, Line | Format-Table -Wrap
```

**macOS/Linux:**

```bash
grep -rni "SELECT\|INSERT\|UPDATE\|DELETE" --include="*.java" . | head -20
```

---

### 예시 5: 특정 메서드 호출 찾기

**Windows:**

```powershell
# findById 메서드 호출 찾기
Get-ChildItem -Recurse *.java | Select-String "\.findById\(" |
    Select-Object Filename, LineNumber, Line
```

**macOS/Linux:**

```bash
grep -rn "\.findById(" --include="*.java" .
```

---

## 🎯 AI 사용 시나리오

### 시나리오 1: 특정 API 사용처 찾기

**사용자 요청:**

> "UserRepository를 사용하는 파일들을 찾아줘"

**AI 작업:**

```powershell
# Windows
Get-ChildItem -Recurse *.java | Select-String "UserRepository" |
    Select-Object Filename -Unique
```

**AI 응답:**

> "UserRepository는 3개 파일에서 사용됩니다: UserService.java, UserController.java, UserConfig.java"

---

### 시나리오 2: 에러 처리 패턴 찾기

**사용자 요청:**

> "try-catch 블록이 있는 파일들을 찾아줘"

**AI 작업:**

```bash
# macOS/Linux
grep -rl "try\s*{" --include="*.java" .
```

---

## 🔧 팁 & 트릭

### Tip 1: 결과를 파일로 저장

**Windows:**

```powershell
Get-ChildItem -Recurse *.java | Select-String "TODO" |
    Out-File -FilePath todos.txt
```

**macOS/Linux:**

```bash
grep -rn "TODO" --include="*.java" . > todos.txt
```

---

### Tip 2: 특정 패턴 제외하고 검색

**Windows:**

```powershell
# "test"가 포함된 줄 제외
Get-ChildItem -Recurse *.java | Select-String "UserService" |
    Where-Object { $_.Line -notmatch "test" }
```

**macOS/Linux:**

```bash
# "test"가 포함된 줄 제외
grep -r "UserService" --include="*.java" . | grep -v "test"
```

---

### Tip 3: 파일명만 출력 (중복 제거)

**Windows:**

```powershell
(Get-ChildItem -Recurse *.java | Select-String "UserService").Filename |
    Sort-Object -Unique
```

**macOS/Linux:**

```bash
grep -rl "UserService" --include="*.java" .
```

---

### Tip 4: 빈 줄과 주석 제외하고 검색

**Windows:**

```powershell
Get-ChildItem -Recurse *.java | Select-String "public" |
    Where-Object {
        $_.Line.Trim() -ne "" -and
        -not $_.Line.Trim().StartsWith("//")
    }
```

**macOS/Linux:**

```bash
grep -r "public" --include="*.java" . | grep -v "^[[:space:]]*$\|^[[:space:]]*//\|^[[:space:]]*\*"
```

---

### Tip 5: 검색 결과 개수만 확인

**Windows:**

```powershell
(Get-ChildItem -Recurse *.java | Select-String "TODO").Count
```

**macOS/Linux:**

```bash
grep -rc "TODO" --include="*.java" . | awk -F: '{sum+=$2} END {print sum}'
```

---

## 📊 유용한 검색 패턴

### Java 코드 패턴

```powershell
# 모든 public 클래스
Get-ChildItem -Recurse *.java | Select-String "public class \w+"

# 모든 인터페이스
Get-ChildItem -Recurse *.java | Select-String "public interface \w+"

# 모든 @Override 메서드
Get-ChildItem -Recurse *.java | Select-String "@Override"

# 모든 static 메서드
Get-ChildItem -Recurse *.java | Select-String "public static \w+ \w+\("

# 모든 생성자
Get-ChildItem -Recurse *.java | Select-String "public \w+\("
```

---

### Spring 관련 패턴

```powershell
# 모든 @Service 클래스
Get-ChildItem -Recurse *.java | Select-String "@Service"

# 모든 @Autowired 필드
Get-ChildItem -Recurse *.java | Select-String "@Autowired"

# 모든 @RequestMapping
Get-ChildItem -Recurse *.java | Select-String "@RequestMapping\|@GetMapping\|@PostMapping"

# 모든 @Transactional
Get-ChildItem -Recurse *.java | Select-String "@Transactional"
```

---

## 📚 관련 명령어

- [파일 검색](./file-search.md) - 파일명으로 검색
- [TODO/FIXME 찾기](./find-todos.md) - TODO 주석 전용
- [Java Import 분석](./java-import-analysis.md) - import 문 분석
