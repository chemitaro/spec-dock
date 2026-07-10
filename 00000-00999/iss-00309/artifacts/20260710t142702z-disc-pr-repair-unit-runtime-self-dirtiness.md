---
種別: disc
ID: "20260710t142702z-disc"
タイトル: "PR Repair Unit Runtime Self Dirtiness"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-07-10"
親: ["iss-00309"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260710t142702z-disc PR Repair Unit Runtime Self Dirtiness

## Repair Unit Contract

- source_batch: `20260710t122133z-pr-repair-batch`
- unit_id: U004
- covered_ids: R006
- source_links: PR review comment 3559156685
- failure_class: `review_feedback:preflight-observer-side-effect`
- risk_class: blocking
- disposition: fix-now

## Validity Analysis

Valid. The installed launcher imports the managed runtime before preflight
observes git status, and normal Python bytecode generation makes a clean
consumer repository appear dirty. Existing tests hid the defect by always
setting `PYTHONDONTWRITEBYTECODE=1`.

## Need-To-Fix Decision

The default GitHub-synced authoring route must work without an undocumented
environment override.

## Root Cause

The observer mutates its own observation target before evaluating it.

## Options Considered

- Ignore bytecode in git status: creates a divergent dirty-state interpretation.
- Add gitignore entries: hides the side effect and broadens scaffold policy.
- Disable bytecode before local runtime imports: prevents the side effect at its source.

## Recommended Design

Set `sys.dont_write_bytecode = True` in the installed launcher before importing
`spec_dock_runtime.app`. Keep preflight and git status contracts unchanged.

## Implementation Plan

1. Update provider and dogfooding launchers.
2. Add a fresh-consumer preflight regression without the environment override.
3. Assert pass, no runtime bytecode, and clean porcelain status.

## Validation Plan

Focused regression, installer projection tests, full provider suite, static
analysis, mirror comparison, and latest-head re-observation.

## Implementation Result

Implemented. Fresh-consumer regression, full suite (2274 passed, 75 skipped),
static analysis, provider/dogfooding comparison, and SpecDock validation passed.

## Commit Evidence

Pending.

## Re-observation Result

Pending.

## Residual Risk / Follow-up

Old consumers with already-created cache files may require cleanup before the
first upgraded run.

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
