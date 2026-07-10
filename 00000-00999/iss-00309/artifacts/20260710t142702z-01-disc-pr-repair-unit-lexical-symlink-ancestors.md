---
種別: disc
ID: "20260710t142702z-01-disc"
タイトル: "PR Repair Unit Lexical Symlink Ancestors"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-07-10"
親: ["iss-00309"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260710t142702z-01-disc PR Repair Unit Lexical Symlink Ancestors

## Repair Unit Contract

- source_batch: `20260710t122133z-pr-repair-batch`
- unit_id: U005
- covered_ids: R007
- source_links: PR review comment 3559156692
- failure_class: `review_feedback:lexical-symlink-ancestor-write`
- risk_class: blocking
- disposition: fix-now

## Validity Analysis

Valid. An existing descendant reached through a symlink appears as a normal
directory and caused the previous loop to stop before inspecting the symlink
component.

## Need-To-Fix Decision

Generated-file writes must not begin until all user-controlled lexical path
components have been checked.

## Root Cause

`exists()` was used as an implicit trust boundary. Existence says nothing
about whether an earlier lexical component is a symlink.

## Options Considered

- Keep the first-existing-parent trust rule: reproduces the escape.
- Resolve then compare: loses the user-supplied namespace.
- Walk every lexical component to the trusted cwd boundary: preserves identity and is deterministic.

## Recommended Design

Inspect the leaf and every parent before resolve/write. Never stop because a
component exists; retain the established blocker names. Treat only an
OS-managed root-level alias such as macOS `/var` as a trusted boundary.

## Implementation Plan

1. Replace the loop with a lexical component helper local to `pack_prepare.py`.
2. Mirror provider runtime into dogfooding.
3. Add the existing-descendant symlink reproduction and no-write assertions.

## Validation Plan

Focused regression plus direct, broken, canonical-root, and Windows-path tests;
then full provider gates and latest-head review.

## Implementation Result

Implemented. Focused prepare tests, full suite (2274 passed, 75 skipped),
static analysis, provider/dogfooding comparison, and SpecDock validation passed.

## Commit Evidence

Pending.

## Re-observation Result

Pending.

## Residual Risk / Follow-up

Read-side ancestors, TOCTOU, hardlinks, and Windows reparse points remain
separate follow-up concerns.

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
