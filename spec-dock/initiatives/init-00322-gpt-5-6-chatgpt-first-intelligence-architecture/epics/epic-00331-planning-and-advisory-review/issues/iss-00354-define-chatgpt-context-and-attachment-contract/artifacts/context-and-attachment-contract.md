# 補助アーティファクト: ChatGPT Context / Attachment Contract 実例集

> **補助資料 / implementation aid / non-canonical**  
> 本文書は `CAND-ISS-00354-20260803T172642Z` の実装補助であり、`requirement.md`、`design.md`、`plan.md` を置き換えない。

## 1. Contract summary

| Concern | Chat body | Attachments | Runtime |
|---|---|---|---|
| Goal / operation | 必須 | 補足可 | typed operation selection |
| Repository / branch / HEAD | 必須 | 代替不可 | exact preflight / postflight |
| Initiative / Epic / Issue | 必須 | 補足可 | metadata resolution |
| Authority / no mutation | 必須 | 詳細説明可 | apply gate |
| Detailed steps | 最小限のみ | 主な配置先 | directory path direct pass |
| Review criteria | role宣言のみ | 主な配置先 | fresh Red |
| Revision rules | selected identityのみ | 主な配置先 | Blue continuity |
| Output kind | 必須 | schema / examples | strict output validator |
| Attachment inventory / SHA | 禁止 | 自己申告不要 | input側では生成しない |
| Candidate / Review SHA | formal identityとして可 | original evidence | output / Human binding |
| Thread handle | 禁止 | 禁止 | adapter-private |
| Raw transcript | 禁止 | 禁止 | public evidenceへ保存しない |

## 2. Common minimal body

```md
# SpecDock ChatGPT Operation

Operation: <planning|review|revision|clarification>
Objective: <one concise objective>

Repository: <owner/repo>
Branch: <named current branch>
Source HEAD: <40-hex>
Initiative: <init-id>
Epic: <epic-id>
Issue: <iss-id>

Use the connected GitHub repository at the exact named branch and source HEAD.
Do not use the default branch or attachments as a substitute for repository access.
If exact access cannot be verified, return exactly `repository access failed`.

ChatGPT is advisory and read-only. Do not modify repository, Git, GitHub,
canonical documents, Issue state, Candidate state, or Human authority.

Expected output: <authoring ZIP|closed Review JSON|advisory clarification answer>
Read and follow the attached operation instructions.
```

詳細な heading template、review severity、revision policy、JSON schema は本文へ連結せず添付する。

## 3. Planning example

### 3.1 Body

```md
Operation: Issue planning
Objective: Create an evidence-only planning Candidate for existing Issue iss-00354.

Repository: chemitaro/spec-dock
Branch: codex/iss-00354-chatgpt-context-contract
Source HEAD: 88a9fdb567f17f50bee421862d3b7859a5eb6384
Initiative: init-00322
Epic: epic-00331
Issue: iss-00354

Verify the exact repository, named branch, and source HEAD with GitHub.
Do not fall back to the default branch. Do not mutate any repository or canonical state.

Expected output: one downloadable authoring ZIP containing requirement.md,
design.md, plan.md, and exactly one subordinate onboarding companion.
Read the attached planning instructions.
```

### 3.2 Static directory

```text
.../resources/operations/planning/attachments/
├── authoring-instructions.md
├── authority-boundary.md
└── output-contract.md
```

SpecDock は directory tree を列挙しない。上記 tree は保守者向けの例であり、runtime allowlist ではない。

### 3.3 Dynamic attachments

- `--attachment-dir` で operator が指定した directory（任意）。
- original path を direct transport へ追加する。
- Runtime は file count / type / content を調べない。

### 3.4 Output

- one ZIP。
- internal root と required files は existing output expectation。
- Candidate は evidence-only。
- ZIP SHA は output identity / Human binding であり input directory checksum ではない。

## 4. Formal review example

### 4.1 Body

```md
Operation: Formal planning review
Objective: Perform a fresh, read-only, defect-only review of Candidate <candidate-id>.

Repository: <owner/repo>
Branch: <branch>
Source HEAD: <head>
Initiative: <init-id>
Epic: <epic-id>
Issue: <iss-id>
Reviewed Candidate SHA-256: <candidate-sha256>
Reviewed identity SHA-256: <identity-sha256>

Start a fresh Red review thread. Do not continue a Blue or prior Red thread.
Do not modify or replace the Candidate.

Expected output: one closed Review JSON object.
Read the attached review instructions and schema.
```

### 4.2 Attachments

```text
static: .../resources/operations/review/attachments/
dynamic: <original-candidate-path>.zip
```

必要なら reviewed identity を compact body JSON として渡す。temporary
`reviewed-identity.json` / checksum file を生成する場合は、それが output identity evidence として本当に必要かを
先に確認する。単なる attachment index のためには生成しない。

### 4.3 Output

```json
{
  "reviewed_identity": {"mode": "archive-candidate", "issue_id": "iss-00354"},
  "reviewed_identity_sha256": "<64-hex>",
  "verdict": "pass",
  "findings": []
}
```

closed schema、duplicate key rejection、identity equality は既存 Runtime が担当する。

## 5. Semantic revision example

### 5.1 Body

```md
Operation: Semantic planning revision
Objective: Produce a complete replacement Candidate that fixes selected P0/P1 findings.

Repository: <owner/repo>
Branch: <branch>
Source HEAD: <head>
Initiative: <init-id>
Epic: <epic-id>
Issue: <iss-id>
Prior Candidate SHA-256: <candidate-sha256>
Review result SHA-256: <review-sha256>
Selected finding IDs: F-001, F-002
Preserve assumptions: A-01, A-03

Continue only the verified Blue thread for this lineage.
If continuity cannot be verified, start a new Blue thread with all current inputs.
If lineage is ambiguous, stop for Human confirmation.

Expected output: one downloadable authoring ZIP.
Read the attached revision instructions.
```

### 5.2 Attachments

```text
static:  .../resources/operations/revision/attachments/
dynamic: <prior-candidate>.zip
dynamic: <planning-review-result>.json
dynamic: <planning-revision-request>.json
```

prior documents を `prior-requirement.md` などへ複製しない。Candidate ZIP が exact prior Candidate である。

### 5.3 Output

new authoring ZIP。P2 / P3-only observation は semantic revision trigger にしない。

## 6. Clarification example

### 6.1 Body

```md
Operation: Clarification
Objective: Resolve one user-intent blocker before Issue planning.

Repository: <owner/repo>
Branch: <branch>
Source HEAD: <head>
Initiative: <init-id>
Epic: <epic-id>
Issue: <iss-id>
Question: <one essential question>
Mode: analysis-only

Do not mutate repository or canonical documents.
Expected output: an advisory answer with resolved assumptions, remaining gap,
one next question if still blocking, and the handoff target.
Read the attached clarification workflow.
```

### 6.2 Attachments

```text
static:  .../spec-dock-clarification/resources/chatgpt-operation/attachments/
dynamic: <selected-interview-or-research-paths>
```

Issue #354 はこの convention を定義するが、current clarification skill に unsupported public runtime invocation を
追加しない。

## 7. Direct attachment directory semantics

Runtime の責務は次に限定する。

```text
select known operation root
+ accept operator-supplied path
+ append original dynamic evidence paths
+ hand paths to direct Oracle
```

Runtime が行わないこと:

```text
walk
glob
stat each entry
open
decode
hash
classify
filter
copy
rename
archive
generate manifest
retry after exclusion
```

### 7.1 Entry examples

| Entry | SpecDock behavior |
|---|---|
| `instructions.md` | directory pathを渡すだけ |
| `.hidden-guidance.md` | hidden と判定しない |
| `nested/example.json` | extension / subdirectory meaning を判定しない |
| symlink | resolve / reject / copyしない |
| FIFO / socket / device | special と判定しない |
| oversized file | size precheckしない |
| secret-like content | scanしない |
| missing path | Oracle transport の通常結果へ委ねる |

「何もしない」を test するには、tree API を monkeypatch で例外化し、argv assembly が成功することを確認する。

## 8. Output format matrix

| Operation | Formal output | Validator | Thread |
|---|---|---|---|
| Planning | authoring ZIP | existing ZIP / inventory / Candidate validator | Blue start / reuse |
| Formal Review | closed JSON | strict Review parser / identity equality | fresh Red |
| Semantic Revision | authoring ZIP | existing ZIP / Candidate validator | verified Blue / new Blue |
| Clarification | advisory text / artifact | owning workflow semantics | Blue convention |
| Mechanical Revision | no ChatGPT output | deterministic local revision validator | no thread |

## 9. Thread state matrix

| Existing state | Operation | Result |
|---|---|---|
| no Blue binding | planning | new Blue |
| exact Blue binding | semantic revision | continue Blue |
| Blue source HEAD mismatch | revision | invalidate; new Blue with complete input |
| Blue handle unavailable, lineage exact | revision | new Blue with complete input |
| Candidate lineage ambiguous | revision | Human-blocked before submit |
| any Blue binding | review | ignore for review; fresh Red |
| prior Red PASS | new Candidate review | do not reuse; fresh Red |
| retryable same-invocation timeout | same operation | existing harvest recovery |
| cross-operation continuity failure | revision | not harvest fallback; binding recovery rules |

## 10. GitHub identity

Exact GitHub verification is independent from attachments.

- repository: owner/name。
- branch: current named branch。
- source HEAD: 40-hex。
- no default branch fallback。
- no attachment / memory substitution。
- local / remote parity and postflight remain Runtime responsibilities。

Attachment directory を GitHub source の代替にしてはならない。逆に、GitHub exact HEAD が確認済みでも attachment
contents の安全性を SpecDock が保証したとは主張しない。

## 11. Evidence handling

### 11.1 Formal evidence

- Candidate ZIP + SHA / logical filename / source identity。
- Review JSON + SHA / reviewed identity。
- Human decision bound to exact Review / Candidate。
- apply operation record。
- source preflight / postflight。

### 11.2 Operational evidence

- operation type。
- exact repository / branch / HEAD。
- `blue_continued` / `blue_restarted` / `fresh_red_started` の content-free outcome。
- Oracle version / supported capability。
- public status / reason。
- tests / validation result。

### 11.3 Do not persist

- attachment contentsの複製。
- generated input manifest。
- raw transcript。
- provider conversation / session handle。
- credentials / secret-like values。
- private absolute path。
- remote private URL。

## 12. Operator responsibilities

- operation directory を適切に管理する。
- material の追加 / 削除時に intent を review する。
- transport limit を考慮して pack を準備する。ただし Runtime に quota policy を実装しない。
- failure 時に directory を修正して明示的に再実行する。
- Candidate / Review を canonical と呼ばない。
- personal wrapper output を formal runtime evidence と混同しない。

## 13. Non-goals

- global attachment schema。
- manifest / checksum。
- content DLP。
- symlink policy。
- automatic ZIP。
- default branch fallback。
- wrapper fallback。
- output validator removal。
- arbitrary ChatGPT role registration。
