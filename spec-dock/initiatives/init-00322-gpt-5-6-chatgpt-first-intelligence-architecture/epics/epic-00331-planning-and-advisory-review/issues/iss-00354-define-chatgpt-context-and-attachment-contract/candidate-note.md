# Candidate Note

## Identity

| Field | Value |
|---|---|
| Logical filename | `iss-00354-chatgpt-context-attachment-contract-candidate-20260803t172642z.zip` |
| Internal logical root | `iss-00354-chatgpt-context-attachment-contract-candidate-20260803t172642z/` |
| Candidate ID | `CAND-ISS-00354-20260803T172642Z` |
| Repository | `chemitaro/spec-dock` |
| Branch | `codex/iss-00354-chatgpt-context-contract` |
| Source HEAD | `88a9fdb567f17f50bee421862d3b7859a5eb6384` |
| Generated UTC | `2026-08-03T17:26:42Z` |
| Generated JST | `2026-08-04T02:26:42+09:00` |
| Authority | `evidence_only` |
| Adoption status | `unreviewed` |

## GitHub verification

GitHub Connector で requested branch を確認し、requested source HEAD と比較した結果は identical
（ahead 0 / behind 0）だった。default branch fallback は使用していない。

## Scope inspected

- Initiative `init-00322` canonical documents / report。
- Epic `epic-00331` canonical documents / report。
- Issue `iss-00354` metadata、assurance、requirement / design / plan / report。
- Parent Issue `#334` requirement / design / plan / report と implementation history。
- Issue #354 `artifacts/` directory の17ファイル全件。
- provider / dogfood の prompt synthesis、application orchestration、domain contracts、direct Oracle adapter、CLI。
- operation resources、Issue Planning / Clarification skills。
- focused unit / CLI / integration tests。
- workflow / prompt-pack docs と親 Epic の矛盾箇所。

## Candidate contents

1. `requirement.md`
2. `design.md`
3. `plan.md`
4. `onboarding.md` — exactly-one onboarding companion。補助資料であり第四のcanonical specificationではない。
5. `artifacts/context-and-attachment-contract.md`
6. `artifacts/decision-and-migration-ledger.md`
7. `artifacts/implementation-and-test-matrix.md`
8. `candidate-note.md`

本 Candidate は一つの logical root を持つ。入力 Option C と混同されるため、内部 `MANIFEST` /
`CHECKSUMS` は作成していない。ZIP SHA-256 は archive 生成後の delivery metadata として外部報告する。

## Authority boundary

この ZIP は manual ChatGPT Use による Blue Team authoring Candidate である。canonical files を変更せず、
Red Team review、PASS / FAIL、reviewer artifact、patch、PR、commit、push、merge、Issue close を含まない。
