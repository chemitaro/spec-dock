---
種別: disc
ID: "20260702t170858z-disc"
タイトル: "PR Repair Unit RU-277-004"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["iss-00276"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260702t170858z-disc PR Repair Unit RU-277-004

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
  - PR #277 latest head `6f9369b7568945454a3b90b9abb8fc1448196cf8` の Codex review P1 `epic-execution.report-gate` を修復する。
- この synthesis が必要な理由:
  - `workflow_epic.md` は Epic `report.md` を evidence ledger として扱うが、`spec-dock-epic-execution` skill の Overview / bootstrap wording が `report.md` を reviewer-gated planning artifact と読ませていた。これは downstream Issue work の default handoff を余分な gate で停止させうる。

## derived question sheets / research (必須)
- `interview`:
  - なし。
- `research`:
  - なし。PR observation result と repository docs / skill wording に基づく。
- その他の根拠:
  - `/private/tmp/spec-dock-pr277-observation-4/result.json`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md`
  - `.agents/skills/spec-dock-epic-execution/SKILL.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`

## synthesis (必須)
- 合意済みのこと:
  - Epic `requirement.md` / `design.md` / `plan.md` は reviewer-gated planning artifacts として読む。
  - Epic `report.md` は unresolved blockers、decisions、handoff state の evidence ledger として読む。
- 未合意 / 未確定のこと:
  - なし。
- source-grounded に解決できたこと:
  - P1修復は skill wording の修正で閉じられる。runtime command や workflow semantics の追加変更は不要。

## 選択肢 / tradeoff (必須)
- Option A:
  - Pros:
    - Overview と bootstrap bullet の両方で `report.md` を evidence ledger と明示できる。
  - Cons:
    - なし。既存 workflow と整合する。
- Option B:
  - Pros:
    - Overview だけを直せば差分はさらに小さい。
  - Cons:
    - bootstrap bullet に同じ誤読余地が残る。

## reflection proposal (必須)
- canonical docs / workflow / template / skill guidance へ反映すべき候補:
  - provider skill と dogfooding skill の `spec-dock-epic-execution` Overview / bootstrap wording。
- まだ proposal に留める理由:
  - 該当なし。P1修復として採用する。

## adoption target / 採用先候補 (必須)
- `requirement.md`:
  - なし。
- `design.md`:
  - なし。
- `plan.md`:
  - なし。
- `ADR`:
  - なし。
- `report.md` Evidence Adoption Ledger:
  - PR repair batch と Issue report の PR repair evidence。

## ADR triage / ADR candidate triage (必須)
- ADR candidate か:
  - no
- hard to reverse:
  - no
- surprising without context:
  - no
- real tradeoff:
  - no
- ADR 化しない場合の反映先:
  - `spec-dock-epic-execution` skill と Issue report evidence。

## 推奨案 (必須)
- 現時点の推奨案と理由を記載する。
  - `spec-dock-epic-execution` skill の Overview と bootstrap bullet を修正し、reviewer-gated artifact を `requirement.md` / `design.md` / `plan.md` に限定する。
  - `report.md` は evidence ledger として読む、と明示する。
  - provider asset と dogfooding mirror の両方を同一文言にする。

## 推奨反映先 (必須)
- `requirement.md`:
  - なし。
- `design.md`:
  - なし。
- `plan.md`:
  - なし。
- `ADR`:
  - なし。
- `report.md` Evidence Adoption Ledger:
  - repair batch / repair unit と、必要なら `iss-00276/report.md` の PR repair evidence。

## 未採用 / deferred 理由 (必須)
- 未採用:
  - P2 `initiative-template.epic-completion-contract` と P2 `epic-handoff.draft-plan-prereq` はこのP1と同一 root cause ではないため、この repair unit では扱わない。
- deferred:
  - P2は non-blocking follow-up として repair batch に記録する。

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - なし。
- 追加で作る artifacts:
  - なし。

## PR Repair Unit Fields

- source_batch: `20260702t170841z-pr-repair-batch`
- unit_id: `RU-277-004`
- root_cause_family: `epic-execution.report-gate`
- covered_ids: `3514851104`, `PRRT_kwDOQ99OK86N-QDD`
- source_links: PR #277 review comment on `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md`
- failure_class: `review_feedback:epic-execution-report-gate`
- decided_priority: `P1`
- merge_blocking: `yes`
- disposition: `fix-now`

## Validity Analysis

- Valid。`workflow_epic.md` では Epic `report.md` を evidence ledger として扱うが、skill Overview / bootstrap wording が `report.md` を reviewer-gated artifact として列挙していた。

## Need-To-Fix Decision

- Need to fix: yes。Default Epic execution handoff を余分な reviewer gate で止めうるため、P1としてこのPR内で修復する。

## Root Cause

- 前回修復で workflow body と coordinator flow 後半は直したが、skill冒頭と bootstrap bullet に古い reviewer-gated `report.md` wording が残った。

## Recommended Design

- reviewer-gated 対象を `requirement.md` / `design.md` / `plan.md` に限定する。
- `report.md` は unresolved blockers / decisions / handoff state の evidence ledger として読む、と明示する。

## Implementation Plan

- provider skill: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md` を修正する。
- dogfooding skill: `.agents/skills/spec-dock-epic-execution/SKILL.md` を同一内容に修正する。
- mirror parity、SpecDock validation、assurance、diff check を確認する。

## Validation Plan

- `diff -u src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md .agents/skills/spec-dock-epic-execution/SKILL.md`
- `./spec-dock/scripts/spec-dock validate`
- `./spec-dock/scripts/spec-dock assurance verify`
- `git diff --check`
- PR #277 latest head re-observation。

## Out of Scope

- P2/P3 follow-up の template / workflow guidance 修正。
- PR merge、review thread resolve、GitHub Issue close。

## Implementation Result

- 実装済み。provider skill と dogfooding skill の Overview / bootstrap bullet を修正した。

## Commit Evidence

- 未コミット。修復検証後に commit hash を external delivery evidence として残す。

## Re-observation Result

- 未実施。commit / push 後に PR #277 を再観測する。

## Residual Risk / Follow-up

- P2 follow-up は repair batch の Non-Blocking Follow-up Register に残す。
