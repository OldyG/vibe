# MCP: Java Symbol Indexer (Preprocessor for LLM Code Navigation)

## 0. One-line Goal
Build an MCP server that pre-indexes Java source files and exposes symbol metadata (methods/fields/classes with line ranges, params, javadoc stats) plus efficient range reads, so LLMs can navigate huge codebases with minimal token usage.

## 1. Non-goals (IMPORTANT)
- Do NOT build a full Java compiler or semantic resolver.
- Do NOT implement full type inference.
- Do NOT attempt perfect call graph across project (optional future).
- Do NOT require a running IDE. This must run standalone from CLI.
- Do NOT rely on internet during runtime.

## 2. Primary Use-case (What the LLM will do)
1) LLM calls `java_index(filePath)` to get a compact index.
2) LLM chooses candidate method(s) by name/signature/javadoc hints.
3) LLM calls `java_read_javadoc(filePath, symbolId)` or `java_read_range(...)` for partial reads.
4) LLM opens only the specific method range if confirmed.

This should feel like “IDE symbol outline + jump-to-definition + peek doc”.

## 3. Implementation constraints
### 3.1 Platform
- Must run on Windows 11 (PowerShell) and also be cross-platform if possible.
- Should be a single repo with clean setup instructions.

### 3.2 Performance expectations
- Indexing single file should be near-instant (<100ms typical; allow slower for huge files).
- Indexing a directory should scale linearly.
- Must support caching: if file unchanged, serve cached index.

### 3.3 Reliability expectations
- Line numbers must be accurate.
- Method `endLine` must be accurate (brace matching errors are NOT acceptable).
- Must handle nested classes, annotations, generics, multiline signatures, and comments.

## 4. Tech stack (You choose)
Choose the stack that is best for correctness + speed + ease:
- Recommended: Python + Tree-sitter Java grammar (accurate ranges, quick to implement).
- Alternative: Java + JavaParser (also accurate, but packaging heavier).
You must pick ONE and justify briefly in README.

## 5. MCP Contract (Tools + Input/Output Schemas)

### 5.1 Tool: java_index
Purpose: Return a symbol outline for a given Java file.

#### Input
- filePath: string (absolute or relative)
- options: object (optional)
  - includePrivate: boolean (default true)
  - includeFields: boolean (default true)
  - includeInnerClasses: boolean (default true)
  - includeConstructors: boolean (default true)
  - maxJavadocPreviewChars: number (default 0; if >0 include preview text truncated)
  - stableIds: boolean (default true; symbolId should be stable across re-index unless code changes)

#### Output (JSON)
{
  "filePath": "...",
  "language": "java",
  "hash": "sha1-or-similar-of-file-content",
  "lineCount": 1234,
  "classes": [
    {
      "symbolId": "Class#com.foo.Bar|start:10|end:400",
      "kind": "class|interface|enum|record|annotation",
      "name": "Bar",
      "qualifiedName": "com.foo.Bar",
      "modifiers": ["public", "final", ...],
      "extends": "BaseBar" | null,
      "implements": ["I1","I2"] | [],
      "startLine": 10,
      "endLine": 400,
      "javadoc": {
        "present": true|false,
        "startLine": 6 | null,
        "endLine": 9 | null,
        "lineCount": 4,
        "preview": "..." | null
      },
      "fields": [
        {
          "symbolId": "Field#com.foo.Bar#count|start:20|end:20",
          "kind": "field",
          "name": "count",
          "typeText": "int",
          "modifiers": ["private","static"] | [],
          "startLine": 20,
          "endLine": 20,
          "javadoc": { ...same shape... }
        }
      ],
      "constructors": [
        {
          "symbolId": "Ctor#com.foo.Bar#Bar(int,String)|start:30|end:60",
          "kind": "constructor",
          "name": "Bar",
          "modifiers": ["public"] | [],
          "params": [
            {"name":"x","typeText":"int"},
            {"name":"name","typeText":"String"}
          ],
          "throws": ["IOException"] | [],
          "startLine": 30,
          "endLine": 60,
          "javadoc": { ... }
        }
      ],
      "methods": [
        {
          "symbolId": "Method#com.foo.Bar#doThing(int,String):Result|start:70|end:120",
          "kind": "method",
          "name": "doThing",
          "returnTypeText": "Result" | "void",
          "modifiers": ["public","synchronized"] | [],
          "typeParamsText": "<T extends Foo>" | null,
          "params": [
            {"name":"a","typeText":"int"},
            {"name":"b","typeText":"String"}
          ],
          "throws": ["Exception"] | [],
          "startLine": 70,
          "endLine": 120,
          "javadoc": { ... },
          "signatureText": "public Result doThing(int a, String b) throws Exception"
        }
      ],
      "innerClasses": [ ...same as class objects, nested recursively... ] | []
    }
  ],
  "errors": [
    {"level":"warning|error", "message":"...", "line": 123 | null}
  ]
}

Rules:
- startLine/endLine are 1-based.
- signatureText must be best-effort, human-readable.
- typeText fields are textual (no semantic resolution required).
- javadoc present detection must be accurate for the symbol.
- If parse fails: still return something + errors with level=error, but do not crash.

### 5.2 Tool: java_read_range
Purpose: Return specific lines for minimal token reading.

#### Input
- filePath: string
- startLine: number (1-based, inclusive)
- endLine: number (1-based, inclusive)
- options:
  - includeLineNumbers: boolean (default true)
  - maxChars: number (default 20000; hard cap to prevent huge responses)

#### Output
{
  "filePath":"...",
  "startLine": 70,
  "endLine": 120,
  "content": "70: ...\n71: ...\n..."
}

Rules:
- Must validate bounds.
- Must hard-cap output (truncate gracefully with a message).

### 5.3 Tool: java_read_javadoc
Purpose: Retrieve only the Javadoc block for a symbolId.

#### Input
- filePath: string
- symbolId: string
- options:
  - includeLineNumbers: boolean (default true)
  - maxChars: number (default 8000)

#### Output
{
  "filePath":"...",
  "symbolId":"...",
  "found": true|false,
  "startLine": 66 | null,
  "endLine": 69 | null,
  "lineCount": 4,
  "content": "66: /** ... */" | ""
}

Rules:
- If not found or no javadoc: found=false, content="".

### 5.4 Tool: java_find_symbol (Optional but recommended)
Purpose: Find symbol candidates by name pattern in a directory.

#### Input
- rootDir: string
- query: string (e.g. "Auth2FaDialog" or "doThing")
- options:
  - matchKind: "class|method|field|any" (default any)
  - maxResults: number (default 50)
  - caseSensitive: boolean (default false)

#### Output
{
  "rootDir":"...",
  "query":"...",
  "results":[
    {
      "filePath":"...",
      "symbolId":"...",
      "kind":"class|method|field|constructor",
      "qualifiedName":"com.foo.Bar#doThing",
      "startLine": 70,
      "endLine": 120,
      "signatureText":"..."
    }
  ]
}

Implementation note:
- This tool may use cached indexes. If index missing, generate on demand.

## 6. ID Strategy (symbolId)
- Must be stable and human-debuggable.
- Recommended: Kind + qualifiedName + signature + start/end lines.
- Must uniquely identify overloaded methods.

## 7. Parsing approach (Choose ONE)
### Option A (recommended): Tree-sitter
- Use tree-sitter Java grammar to parse AST.
- Derive start/end lines from node ranges.
- Extract modifiers, names, params, return type, throws.
- Determine Javadoc by scanning preceding trivia/comments near symbol start.

### Option B: JavaParser
- Parse compilation unit.
- Use node.getRange() for start/end.
- Extract similar metadata.

Regardless of option:
- Must handle:
  - annotations on separate lines
  - multiline parameter lists
  - generics
  - nested/inner classes
  - records, enums
  - interface default/static methods
  - constructors and compact constructors (records)

## 8. Caching
- Cache per file by content hash.
- Store cache in `.mcp-java-index-cache/` under rootDir or next to server.
- Cache format can be JSON.
- Cache invalidation: if hash differs, recompute.

## 9. Repository deliverables
### 9.1 Code
- MCP server implementation exposing tools above.
- Clean modular structure:
  - parser/
  - cache/
  - mcp_server/
  - cli/

### 9.2 Docs
- README.md with:
  - install steps
  - how to run the MCP server
  - examples of calling each tool (sample JSON input/output)
  - limitations and future work
- QUICKSTART.md with a 5-minute run guide.

### 9.3 Tests (MANDATORY)
Provide automated tests:
1) Unit tests for parsing:
   - methods with annotations
   - overloaded methods
   - nested class methods
   - record/enum/interface
2) Range read tests
3) Javadoc detection tests

Include at least 6 Java fixture files under `tests/fixtures/`.

## 10. Self-verification (The AI must do this before declaring done)
The implementation is only “DONE” if:
- All tests pass locally.
- Running `java_index` against fixture files produces exact expected JSON (snapshot tests allowed).
- `java_read_range` returns accurate lines including boundaries.
- `java_read_javadoc` accurately returns the javadoc block for fixture symbols.
- Cache works: re-indexing unchanged file uses cache (log or metrics show cache hit).
- No crashes on parse errors; errors returned in `errors` array.

## 11. UX details (important for LLM usage)
- Outputs must be compact and consistent.
- Avoid huge blobs: cap previews.
- Always include `startLine/endLine` for every symbol.
- Always include `signatureText` for methods/constructors when possible.
- For fields, include `typeText`.

## 12. CLI (Optional but very helpful)
Provide a CLI entry point:
- `mcp-java-index index path/to/File.java`
- `mcp-java-index find --root . --query doThing`
- `mcp-java-index range path/to/File.java 70 120`
This CLI is for human debugging, not required for MCP usage but recommended.

## 13. Coding standards
- Clear types, clean error handling.
- No over-engineering.
- Simple, test-first approach.
- Log parse errors as warnings; never explode unless the file is unreadable.

## 14. Suggested development plan (Follow this sequence)
1) Scaffold MCP server + tool registration.
2) Implement `java_read_range`.
3) Implement parser and `java_index` MVP for class + methods (no fields, no javadoc).
4) Add fields + constructors.
5) Add javadoc detection + `java_read_javadoc`.
6) Add caching.
7) Add tests + fixtures.
8) Optional: `java_find_symbol` and CLI.

## 15. Acceptance criteria (Final checklist)
- [ ] Server starts and tools respond.
- [ ] Index output follows schema.
- [ ] Line ranges accurate.
- [ ] Javadoc detection accurate.
- [ ] Caching works.
- [ ] Tests pass.
- [ ] README + QUICKSTART complete.
