---
種別: disc
ID: "20260710t172152z-disc"
タイトル: "PR Repair Unit Compatibility Review Wrapper"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-07-10"
親: ["iss-00309"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260710t172152z-disc PR Repair Unit Compatibility Review Wrapper

## Repair Unit Contract

- source_batch: `20260710t122133z-pr-repair-batch`
- unit_id: U009
- root_cause_family: `compatibility-review-wrapper`
- covered_ids: R015
- source_links: PR review comment 3560691385
- failure_class: `review_feedback:compatibility-review-wrapper`
- decided_priority: P1
- merge_blocking: yes
- disposition: fix-now

## Validity Analysis

Valid. The wrapper parsed legacy preflight, input-kind, and extraction arguments
but did not apply them before delegating to the current reviewer.

## Need-To-Fix Decision

Legacy arguments must retain their safety-gate meaning or fail explicitly.

## Root Cause

Compatibility parsing was preserved while the corresponding legacy adapter
semantics were dropped during delegation.

## Options Considered

- Remove the legacy flags.
- Delegate without parity.
- Apply explicit preflight, input-kind, and safe-extraction gates around the
  current reviewer.

## Recommended Design

Use an explicit legacy argument mode that requires preflight and output-dir,
propagates non-pass preflight states, enforces the requested input kind, and
extracts only files accepted by the current ZIP reviewer.

## Implementation Plan

Implement provider/dogfooding wrapper parity and add stale-preflight,
input-kind, extraction, and modern-route regressions.

## Validation Plan

Focused compatibility tests, authoring CLI suite, full provider suite, static
analysis, mirror comparison, SpecDock validation, and latest-head review.

## Out of Scope

Removal of legacy flags and redesign of the canonical pack reviewer.

## Implementation Result

Implemented. The authoring CLI suite (378 passed, 1 skipped), full suite
(2294 passed, 75 skipped), static analysis, mirrors, and SpecDock validation
passed.

## Commit Evidence

The enclosing final repair commit records this unit.

## Re-observation Result

Pending.

## Residual Risk / Follow-up

Legacy and current report schemas remain separate compatibility surfaces.

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
