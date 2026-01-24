# API 레퍼런스

MCP Java Indexer는 4개의 MCP 도구를 제공합니다.

## 목차
- [java_index](#java_index) - Java 파일의 심볼 인덱스 반환
- [java_read_range](#java_read_range) - 특정 라인 범위 읽기
- [java_read_javadoc](#java_read_javadoc) - 심볼의 Javadoc 읽기
- [java_find_symbol](#java_find_symbol) - 디렉토리에서 심볼 검색

---

## java_index

Java 파일의 심볼 개요(outline)를 반환합니다.

### 입력

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| `filePath` | string | ✅ | - | 인덱싱할 Java 파일의 경로 (절대 또는 상대) |
| `options` | object | ❌ | `{}` | 인덱싱 옵션 |

#### options 객체

| 필드 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `includePrivate` | boolean | `true` | private 멤버 포함 여부 |
| `includeFields` | boolean | `true` | 필드 포함 여부 |
| `includeInnerClasses` | boolean | `true` | 내부 클래스 포함 여부 |
| `includeConstructors` | boolean | `true` | 생성자 포함 여부 |
| `maxJavadocPreviewChars` | number | `0` | Javadoc 미리보기 문자 수 (0이면 미리보기 없음) |
| `stableIds` | boolean | `true` | 안정적인 심볼 ID 사용 여부 |

### 출력

```json
{
  "filePath": "com/example/MyClass.java",
  "language": "java",
  "hash": "a1b2c3d4e5f6...",
  "lineCount": 250,
  "classes": [
    {
      "symbolId": "Class#com.example.MyClass|start:10|end:250",
      "kind": "class",
      "name": "MyClass",
      "qualifiedName": "com.example.MyClass",
      "modifiers": ["public", "final"],
      "extends": "BaseClass",
      "implements": ["Interface1", "Interface2"],
      "startLine": 10,
      "endLine": 250,
      "javadoc": {
        "present": true,
        "startLine": 6,
        "endLine": 9,
        "lineCount": 4,
        "preview": "This is a sample class..."
      },
      "fields": [...],
      "constructors": [...],
      "methods": [...],
      "innerClasses": [...]
    }
  ],
  "errors": []
}
```

#### 클래스 객체

| 필드 | 타입 | 설명 |
|------|------|------|
| `symbolId` | string | 안정적인 심볼 ID |
| `kind` | string | `"class"`, `"interface"`, `"enum"`, `"record"`, `"annotation"` |
| `name` | string | 클래스 이름 |
| `qualifiedName` | string | 패키지를 포함한 전체 이름 |
| `modifiers` | string[] | `["public", "abstract", "static", ...]` |
| `extends` | string \| null | 상속하는 클래스 |
| `implements` | string[] | 구현하는 인터페이스 목록 |
| `startLine` | number | 시작 라인 (1-based) |
| `endLine` | number | 종료 라인 (1-based) |
| `javadoc` | object | Javadoc 메타데이터 |
| `fields` | Field[] | 필드 목록 |
| `constructors` | Constructor[] | 생성자 목록 |
| `methods` | Method[] | 메서드 목록 |
| `innerClasses` | Class[] | 내부 클래스 목록 (재귀적) |

#### 필드 객체

```json
{
  "symbolId": "Field#com.example.MyClass#count|start:20|end:20",
  "kind": "field",
  "name": "count",
  "typeText": "int",
  "modifiers": ["private", "static"],
  "startLine": 20,
  "endLine": 20,
  "javadoc": {...}
}
```

#### 생성자 객체

```json
{
  "symbolId": "Ctor#com.example.MyClass#MyClass(int,String)|start:30|end:35",
  "kind": "constructor",
  "name": "MyClass",
  "modifiers": ["public"],
  "params": [
    {"name": "id", "typeText": "int"},
    {"name": "name", "typeText": "String"}
  ],
  "throws": ["IOException"],
  "startLine": 30,
  "endLine": 35,
  "javadoc": {...},
  "signatureText": "public MyClass(int id, String name) throws IOException"
}
```

#### 메서드 객체

```json
{
  "symbolId": "Method#com.example.MyClass#doSomething(String):Result|start:50|end:80",
  "kind": "method",
  "name": "doSomething",
  "returnTypeText": "Result",
  "modifiers": ["public", "synchronized"],
  "typeParamsText": "<T extends Comparable<T>>",
  "params": [
    {"name": "input", "typeText": "String"}
  ],
  "throws": ["Exception"],
  "startLine": 50,
  "endLine": 80,
  "javadoc": {...},
  "signatureText": "public synchronized <T extends Comparable<T>> Result doSomething(String input) throws Exception"
}
```

#### Javadoc 객체

```json
{
  "present": true,
  "startLine": 45,
  "endLine": 48,
  "lineCount": 4,
  "preview": "Does something with the input..."
}
```

### 사용 예시

```python
# Python (MCP 클라이언트)
result = await mcp_client.call_tool("java_index", {
    "filePath": "src/main/java/com/example/MyClass.java",
    "options": {
        "includePrivate": False,
        "maxJavadocPreviewChars": 100
    }
})
```

```bash
# CLI
mcp-java-index index src/main/java/com/example/MyClass.java
```

---

## java_read_range

파일의 특정 라인 범위를 읽습니다. 토큰 사용량을 최소화하기 위해 사용합니다.

### 입력

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| `filePath` | string | ✅ | 읽을 파일 경로 |
| `startLine` | number | ✅ | 시작 라인 (1-based, inclusive) |
| `endLine` | number | ✅ | 종료 라인 (1-based, inclusive) |
| `options` | object | ❌ | 읽기 옵션 |

#### options 객체

| 필드 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `includeLineNumbers` | boolean | `true` | 라인 번호 포함 여부 |
| `maxChars` | number | `20000` | 최대 문자 수 (초과 시 잘림) |

### 출력

```json
{
  "filePath": "com/example/MyClass.java",
  "startLine": 50,
  "endLine": 80,
  "content": "50: public Result doSomething(String input) {\n51:     // implementation\n52:     return new Result();\n53: }"
}
```

### 사용 예시

```python
# 메서드 50-80라인만 읽기
result = await mcp_client.call_tool("java_read_range", {
    "filePath": "src/main/java/com/example/MyClass.java",
    "startLine": 50,
    "endLine": 80,
    "options": {
        "includeLineNumbers": True
    }
})
```

```bash
# CLI
mcp-java-index range src/main/java/com/example/MyClass.java 50 80
```

---

## java_read_javadoc

특정 심볼의 Javadoc만 읽습니다.

### 입력

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| `filePath` | string | ✅ | 파일 경로 |
| `symbolId` | string | ✅ | 심볼 ID (java_index에서 얻은 값) |
| `options` | object | ❌ | 읽기 옵션 |

#### options 객체

| 필드 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `includeLineNumbers` | boolean | `true` | 라인 번호 포함 여부 |
| `maxChars` | number | `8000` | 최대 문자 수 |

### 출력

```json
{
  "filePath": "com/example/MyClass.java",
  "symbolId": "Method#com.example.MyClass#doSomething(String):Result|start:50|end:80",
  "found": true,
  "startLine": 45,
  "endLine": 48,
  "lineCount": 4,
  "content": "45: /**\n46:  * Does something with the input.\n47:  * @param input the input string\n48:  */"
}
```

Javadoc이 없는 경우:
```json
{
  "filePath": "com/example/MyClass.java",
  "symbolId": "Method#...",
  "found": false,
  "startLine": null,
  "endLine": null,
  "lineCount": 0,
  "content": ""
}
```

### Javadoc 탐지 규칙

1. **형식**: `/** ... */` 형식만 인정 (단일 라인 `//` 주석은 X)
2. **위치**: 심볼 바로 앞에 있어야 함 (빈 줄 허용)
3. **애노테이션**: 애노테이션 앞의 Javadoc도 인식

### 사용 예시

```python
# 메서드의 Javadoc만 읽기
result = await mcp_client.call_tool("java_read_javadoc", {
    "filePath": "src/main/java/com/example/MyClass.java",
    "symbolId": "Method#com.example.MyClass#doSomething(String):Result|start:50|end:80"
})
```

---

## java_find_symbol

디렉토리 전체에서 심볼을 검색합니다.

### 입력

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| `rootDir` | string | ✅ | 검색할 루트 디렉토리 |
| `query` | string | ✅ | 검색 쿼리 (예: "MyClass", "doSomething") |
| `options` | object | ❌ | 검색 옵션 |

#### options 객체

| 필드 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `matchKind` | string | `"any"` | `"class"`, `"method"`, `"field"`, `"constructor"`, `"any"` |
| `maxResults` | number | `50` | 최대 결과 수 |
| `caseSensitive` | boolean | `false` | 대소문자 구분 여부 |

### 출력

```json
{
  "rootDir": "src/main/java",
  "query": "doSomething",
  "results": [
    {
      "filePath": "com/example/MyClass.java",
      "symbolId": "Method#com.example.MyClass#doSomething(String):Result|start:50|end:80",
      "kind": "method",
      "qualifiedName": "com.example.MyClass#doSomething",
      "startLine": 50,
      "endLine": 80,
      "signatureText": "public Result doSomething(String input)"
    },
    {
      "filePath": "com/example/AnotherClass.java",
      "symbolId": "Method#com.example.AnotherClass#doSomething():void|start:20|end:25",
      "kind": "method",
      "qualifiedName": "com.example.AnotherClass#doSomething",
      "startLine": 20,
      "endLine": 25,
      "signatureText": "private void doSomething()"
    }
  ]
}
```

### 사용 예시

```python
# "UserService" 클래스 찾기
result = await mcp_client.call_tool("java_find_symbol", {
    "rootDir": "src/main/java",
    "query": "UserService",
    "options": {
        "matchKind": "class",
        "maxResults": 10
    }
})
```

```bash
# CLI
mcp-java-index find --root src/main/java --query "UserService"
```

---

## 에러 처리

모든 도구는 에러 발생 시에도 가능한 한 부분 결과를 반환합니다.

### 에러 형식

```json
{
  "errors": [
    {
      "level": "error",
      "message": "Parse error",
      "line": 123
    },
    {
      "level": "warning",
      "message": "Unexpected token",
      "line": 456
    }
  ]
}
```

### 에러 레벨
- **error**: 심각한 파싱 오류
- **warning**: 경고 (처리는 계속됨)

### 파일 읽기 실패

파일을 읽을 수 없는 경우:
```json
{
  "filePath": "invalid/path.java",
  "language": "java",
  "hash": "",
  "lineCount": 0,
  "classes": [],
  "errors": [
    {
      "level": "error",
      "message": "Failed to read file: [Errno 2] No such file or directory",
      "line": null
    }
  ]
}
```

---

## 성능 특성

### java_index
- **캐시 히트**: < 5ms
- **캐시 미스**: 50-200ms (파일 크기에 따라)
- **대용량 파일** (5000+ 라인): < 500ms

### java_read_range
- **일반적**: < 10ms
- **대용량 범위**: maxChars 제한으로 안전

### java_read_javadoc
- **캐시 사용**: java_index 캐시 활용
- **Javadoc 추출**: < 5ms

### java_find_symbol
- **선형 확장**: 파일 수에 비례
- **캐시 효과**: 이전에 인덱싱된 파일은 빠름
- **early exit**: maxResults 도달 시 중단

---

## 사용 패턴

### 권장 워크플로우

1. **개요 파악**
   ```python
   index = await java_index("path/to/File.java", {
       "includePrivate": False,
       "maxJavadocPreviewChars": 100
   })
   ```

2. **관심 있는 심볼 찾기**
   ```python
   for cls in index["classes"]:
       for method in cls["methods"]:
           if "authenticate" in method["name"]:
               print(method["symbolId"])
   ```

3. **Javadoc 읽기**
   ```python
   doc = await java_read_javadoc("path/to/File.java", method["symbolId"])
   print(doc["content"])
   ```

4. **구현 읽기**
   ```python
   code = await java_read_range("path/to/File.java",
                                 method["startLine"],
                                 method["endLine"])
   print(code["content"])
   ```

### 안티패턴 (피해야 할 것)

❌ **전체 파일 읽기**
```python
# 나쁜 예: 파일 전체 읽기
code = await java_read_range("File.java", 1, 10000)
```

✅ **필요한 부분만 읽기**
```python
# 좋은 예: 필요한 메서드만 읽기
code = await java_read_range("File.java",
                             method["startLine"],
                             method["endLine"])
```

❌ **캐시 무효화하는 옵션 변경**
```python
# 나쁜 예: 옵션을 자주 바꾸면 캐시 효율 떨어짐
await java_index("File.java", {"includePrivate": True})
await java_index("File.java", {"includePrivate": False})  # 캐시 미스
```

✅ **일관된 옵션 사용**
```python
# 좋은 예: 동일한 옵션 사용
opts = {"includePrivate": False}
await java_index("File1.java", opts)
await java_index("File2.java", opts)
```

---

## 제한사항

1. **타입 해석 없음**: `typeText`는 소스 코드의 텍스트 그대로
2. **임포트 해석 없음**: 완전한 타입 이름(FQCN) 추론 안 함
3. **호출 그래프 없음**: 메서드 간 호출 관계 제공 안 함
4. **Java 8+ 기능**: 람다, 스트림 등은 AST에 포함되지만 별도 심볼로 추출되지 않음

---

## 추가 자료

- [아키텍처 개요](architecture.md) - 시스템 설계
- [개발 가이드](development-guide.md) - 코드 기여 방법
- [파일 구조](file-structure.md) - 코드베이스 구조
