---
name: java-analyzer
description: Java 소스 코드를 Tree-sitter 기반으로 분석하여 클래스, 메서드, 필드 정보를 초경량 JSON으로 제공하는 CLI 도구. AI가 Java 파일을 열기 전에 빠르게 구조를 파악할 수 있도록 토큰 효율적인 출력 모드 제공.
---

# Java Analyzer Skill

## 개요

`java-analyzer`는 Java 소스 코드를 분석하여 **AI 친화적인 초경량 JSON**으로 출력하는 CLI 도구입니다.

**핵심 가치:**

- 🚀 **토큰 효율성**: 200줄 Java 파일 → 37줄 JSON (94% 절감)
- ⚡ **빠른 파악**: 파일을 열기 전에 클래스 구조를 한눈에 파악
- 🎯 **계층적 정보**: 필요한 만큼만 조회 (ultra → compact → full)

---

## 사용 시나리오

### 시나리오 1: Java 파일 빠른 스캔

**사용자 요청:**

> "EmlLabelPropertyService.java 파일이 뭐 하는 건지 빠르게 파악해줘"

**AI 작업:**

```bash
# Ultra 모드로 초고속 스캔
python -m cli.main index path/to/EmlLabelPropertyService.java --mode ultra
```

**결과 (37줄):**

```json
{
  "file": "EmlLabelPropertyService.java",
  "lines": 272,
  "classes": [{
    "name": "EmlLabelPropertyService",
    "annotations": ["@Service", "@RequiredArgsConstructor"],
    "methods": [
      "selectDetailByMailUser(MailUser) [53-69]",
      "changeRuleOrder(MailUser, List<String>) [82-93]",
      "saveLabelRule(MailUser, LabelRule) [110-122]",
      ...
    ],
    "fields": [
      "LabelRuleSupporter labelRuleSupporter",
      "EmlLabelMapper emlLabelMapper"
    ]
  }]
}
```

**AI 응답:**

> "이 파일은 이메일 라벨 자동화 규칙을 관리하는 서비스입니다. 주요 메서드는 규칙 조회, 순서 변경, 저장, 삭제 등이 있습니다."

---

### 시나리오 2: 특정 메서드 상세 분석

**사용자 요청:**

> "changeRuleOrder 메서드가 정확히 뭐 하는지 알려줘"

**AI 작업:**

```bash
# Compact 모드로 시그니처 확인
python -m cli.main index path/to/EmlLabelPropertyService.java --mode compact
```

**결과에서 해당 메서드 찾기:**

```json
{
  "id": "82",
  "name": "changeRuleOrder",
  "sig": "@Transactional public List<LabelRule> changeRuleOrder(@NonNull MailUser mailUser, @NonNull List<String> ruleIds)",
  "range": [82, 93],
  "doc": "라벨 자동화 규칙의 순서를 변경합니다."
}
```

**AI 응답:**

> "changeRuleOrder는 트랜잭션 내에서 사용자의 라벨 규칙 순서를 변경하는 메서드입니다. 82-93줄에 위치하며, 규칙 ID 리스트를 받아 순서를 재정렬합니다."

---

### 시나리오 3: DTO/Bean 클래스 분석

**사용자 요청:**

> "UserDto 클래스에 어떤 필드들이 있는지 확인해줘"

**AI 작업:**

```bash
# Compact 모드 + 필드 포함
python -m cli.main index path/to/UserDto.java --mode compact --with-fields
```

**결과:**

```json
{
  "classes": [
    {
      "name": "UserDto",
      "annotations": ["@Data", "@Builder"],
      "fields": [
        {
          "name": "userId",
          "sig": "@JsonProperty(\"user_id\") private String userId",
          "doc": "사용자 ID"
        },
        {
          "name": "userName",
          "sig": "@NotNull private String userName",
          "doc": "사용자 이름"
        }
      ]
    }
  ]
}
```

---

## 출력 모드

### 1. Ultra 모드 (기본값, AI 추천)

**용도:** 파일 전체 구조를 빠르게 파악

**특징:**

- 📉 **토큰 절감**: 94% (610줄 → 37줄)
- 🎯 **핵심 정보**: 클래스명, 어노테이션, 메서드 시그니처, 필드 타입
- ⚡ **속도**: 초고속

**사용:**

```bash
python -m cli.main index YourFile.java --mode ultra
```

**출력 형식:**

- 메서드: `"methodName(ParamType1, ParamType2) [start-end]"`
- 필드: `"TypeName fieldName"`

---

### 2. Compact 모드 (상세 분석)

**용도:** 각 메서드/필드의 목적과 시그니처 파악

**특징:**

- 📉 **토큰 절감**: 73% (610줄 → 163줄)
- 📝 **상세 정보**: 전체 시그니처, javadoc 첫 줄, ID
- 🔍 **심볼 조회**: ID로 특정 심볼 재조회 가능

**사용:**

```bash
python -m cli.main index YourFile.java --mode compact
```

**출력 형식:**

- 메서드: `{"id": "53", "name": "...", "sig": "...", "range": [53, 69], "doc": "..."}`
- 필드: `{"name": "...", "sig": "...", "doc": "..."}`

---

### 3. Full 모드 (개발자용)

**용도:** 모든 상세 정보 필요 시

**특징:**

- 📊 **완전한 정보**: params, throws, modifiers 등 모든 메타데이터
- 🔧 **개발자 도구**: IDE 통합, 코드 생성 등

**사용:**

```bash
python -m cli.main index YourFile.java --mode full
```

---

## 주요 옵션

### 필드 제어

```bash
# 필드 포함 (기본값)
python -m cli.main index YourFile.java --with-fields

# 필드 제외 (메서드만)
python -m cli.main index YourFile.java --no-fields-output
```

**사용 예:**

- Service 클래스: 메서드 중심 → `--no-fields-output`
- DTO/Bean: 필드 중심 → `--with-fields`

---

### 접근 제한자 필터

```bash
# Public 메서드만
python -m cli.main index YourFile.java --scope public

# Public + Protected
python -m cli.main index YourFile.java --scope protected

# 모두 포함 (기본값)
python -m cli.main index YourFile.java --scope all
```

**사용 예:**

- API 인터페이스 파악: `--scope public`
- 내부 구현 포함: `--scope all`

---

## AI 워크플로우 예시

### 1단계: 빠른 스캔 (Ultra)

```bash
python -m cli.main index Service.java --mode ultra
```

**AI 판단:**

- "이 클래스가 뭐 하는지 알겠어"
- "어떤 메서드들이 있는지 파악했어"

---

### 2단계: 관심 메서드 확인 (Compact)

```bash
python -m cli.main index Service.java --mode compact
```

**AI 판단:**

- "changeRuleOrder 메서드가 트랜잭션이구나"
- "82-93줄에 있네, 필요하면 읽어볼게"

---

### 3단계: 실제 코드 읽기 (Range)

```bash
python -m cli.main range Service.java 82 93
```

**AI 판단:**

- "실제 구현을 봤어, 이렇게 동작하는구나"

---

## 빠른 참조

### 명령어 치트시트

```bash
# 가장 많이 쓰는 명령어
python -m cli.main index YourFile.java --mode ultra

# DTO 분석
python -m cli.main index UserDto.java --mode compact --with-fields

# Public API만
python -m cli.main index ApiService.java --mode ultra --scope public

# 특정 줄 읽기
python -m cli.main range YourFile.java 50 100

# 심볼 검색
python -m cli.main find --root . --query methodName --kind method
```

---

## 상세 문서

### 설치 및 설정

- 📖 **설치 가이드**: [SETUP.md](./SETUP.md) - Python 설치부터 단계별 안내
- 📚 **전체 사용법**: [README.md](./README.md) - 모든 CLI 명령어 상세 설명

### 개발자용

- 🔧 **구현 설계**: [../plan/output-mode-design.md](../plan/output-mode-design.md) - 출력 모드 설계 명세

---

## 실행 전 체크리스트

### 최초 1회 설정

```bash
# 1. Python 설치 확인
python --version  # 3.10 이상

# 2. java-analyzer 디렉토리로 이동
cd path/to/java-analyzer

# 3. 의존성 설치
python -m pip install -r requirements.txt

# 4. 설치 확인
python -c "import tree_sitter; print('OK')"
```

**문제 발생 시:** [SETUP.md](./SETUP.md) 참고

---

## 팁 & 트릭

### 💡 Tip 1: 대용량 파일은 Ultra로

1000줄 이상 파일은 Ultra 모드로 먼저 파악하세요.

```bash
python -m cli.main index LargeFile.java --mode ultra
```

---

### 💡 Tip 2: JSON 파일로 저장

나중에 다시 참조할 수 있도록 저장하세요.

```bash
python -m cli.main index Service.java --mode ultra > service_structure.json
```

---

### 💡 Tip 3: 여러 파일 비교

```bash
# 파일 A
python -m cli.main index FileA.java --mode ultra > a.json

# 파일 B
python -m cli.main index FileB.java --mode ultra > b.json

# JSON 비교 도구로 차이 확인
```

---

### 💡 Tip 4: Public API만 빠르게

외부에 노출되는 API만 보고 싶을 때:

```bash
python -m cli.main index ApiController.java --mode ultra --scope public --no-fields-output
```

---

## 출력 예시 비교

### 같은 파일 (272줄 Service 클래스)

| 모드        | 줄 수 | 절감율 | 용도            |
| ----------- | ----- | ------ | --------------- |
| **Ultra**   | 37줄  | 94%    | AI 빠른 스캔 ⭐ |
| **Compact** | 163줄 | 73%    | AI 상세 분석    |
| **Full**    | 610줄 | 0%     | 개발자 도구     |

---

## 문제 해결

### "ModuleNotFoundError: No module named 'tree_sitter'"

**원인:** 의존성 미설치

**해결:**

```bash
python -m pip install -r requirements.txt
```

---

### "No module named 'cli'"

**원인:** 잘못된 디렉토리에서 실행

**해결:**

```bash
# java-analyzer 디렉토리로 이동
cd path/to/java-analyzer

# 그 다음 실행
python -m cli.main index YourFile.java
```

---

## 요약

**java-analyzer는 AI가 Java 코드를 효율적으로 이해하도록 돕는 도구입니다.**

1. ⚡ **Ultra 모드로 빠르게 스캔** (94% 토큰 절감)
2. 🔍 **Compact 모드로 상세 확인** (73% 토큰 절감)
3. 📄 **필요시 실제 코드 읽기** (range 명령어)

**기본 사용법:**

```bash
python -m cli.main index YourFile.java --mode ultra
```

**더 자세한 내용:** [README.md](./README.md) | [SETUP.md](./SETUP.md)
