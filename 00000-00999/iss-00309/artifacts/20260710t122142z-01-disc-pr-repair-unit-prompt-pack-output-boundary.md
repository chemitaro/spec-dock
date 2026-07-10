---
種別: disc
ID: "20260710t122142z-01-disc"
タイトル: "PR Repair Unit Prompt Pack Output Boundary"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-07-10"
親: ["iss-00309"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260710t122142z-01-disc PR Repair Unit Prompt Pack Output Boundary

## Repair Unit Contract

- source_batch: `20260710t122133z-pr-repair-batch`
- unit_id: U002
- covered_ids: R003, R004
- source_links: PR review comments 3558754361, 3558754366
- failure_class: `review_feedback:prompt-pack-output-boundary`
- risk_class: blocking
- disposition: fix-now

## Validity Analysis

Both findings are valid. A broken symlink reports `exists() == false`, and the
exact initiatives root lacks the trailing slash expected by the existing match.

## Need-To-Fix Decision

Prompt-pack generation must fail before writing through a symlink or into
canonical SpecDock data.

## Root Cause

Symlink detection was incorrectly gated by existence, and canonical path
detection covered descendants but not the exact initiatives root.

## Options Considered

- Replace all path classification: unnecessary scope expansion.
- Close the two guard gaps in the existing helpers: smallest coherent repair.

## Recommended Design

Check `is_symlink()` independently and add exact-root matching for both lexical
and resolved paths.

## Implementation Plan

1. Update output-dir guard helpers.
2. Add broken-symlink and exact-root regression tests.
3. Run focused and full provider tests.

## Validation Plan

Both inputs return `status=rejected` and create no manifest.

## Implementation Result

Implemented in provider and dogfooding runtime. Focused contract tests (40
cases), the full provider suite (2272 passed, 75 skipped), static analysis, and
`spec-dock validate` passed.

## Commit Evidence

Pending.

## Re-observation Result

Pending.

## Residual Risk / Follow-up

Low; no valid output target is newly rejected beyond the documented canonical
boundary and symlink contract.

## 位置づけ
- 用途: 集まった質問回答や調査をもとに、意思決定前の synthesis、選択肢、tradeoff、reflection proposal、ADR candidate triage、推奨反映先を整理する。
- authority default: `proposed`。通常は artifact type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は synthesis / reflection proposal / adoption target / ADR triage の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 人間から回答を引き出し、回答欄や未回答事項を管理する場合は `interview` を使う。
- 生ログや未整理の思考は `blank`、事実確認や外部根拠は `research`、長期判断の固定は `adr` に分ける。
- この doc は proposal / synthesis であり、issue `report.md` の observed evidence ledger ではない。採否の最終証跡は canonical docs / ADR / `report.md` Evidence Adoption Ledger に昇格する。
- doc が大きくなりすぎたら、質問回答は `interview`、事実調査は `research`、raw capture は `blank`、長期決定は `adr` へ分割する。

## 対象論点 (必須)
- 今回整理する論点:
  - ...
- この synthesis が必要な理由:
  - ...

## derived question sheets / research (必須)
- `interview`:
  - ...
- `research`:
  - ...
- その他の根拠:
  - ...

## synthesis (必須)
- 合意済みのこと:
  - ...
- 未合意 / 未確定のこと:
  - ...
- source-grounded に解決できたこと:
  - ...

## 選択肢 / tradeoff (必須)
- Option A:
  - Pros:
    - ...
  - Cons:
    - ...
- Option B:
  - Pros:
    - ...
  - Cons:
    - ...

## reflection proposal (必須)
- canonical docs / workflow / template / skill guidance へ反映すべき候補:
  - ...
- まだ proposal に留める理由:
  - ...

## adoption target / 採用先候補 (必須)
- `requirement.md`:
  - ...
- `design.md`:
  - ...
- `plan.md`:
  - ...
- `ADR`:
  - ...
- `report.md` Evidence Adoption Ledger:
  - ...

## ADR triage / ADR candidate triage (必須)
- ADR candidate か:
  - yes | no
- hard to reverse:
  - yes | no
- surprising without context:
  - yes | no
- real tradeoff:
  - yes | no
- ADR 化しない場合の反映先:
  - `interview` | `disc` | `requirement.md` | `design.md` | `plan.md` | other

## 推奨案 (必須)
- 現時点の推奨案と理由を記載する。

## 推奨反映先 (必須)
- `requirement.md`:
  - ...
- `design.md`:
  - ...
- `plan.md`:
  - ...
- `ADR`:
  - ...
- `report.md` Evidence Adoption Ledger:
  - ...

## 未採用 / deferred 理由 (必須)
- 未採用:
  - ...
- deferred:
  - ...

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - ...
- 追加で作る artifacts:
  - ...
