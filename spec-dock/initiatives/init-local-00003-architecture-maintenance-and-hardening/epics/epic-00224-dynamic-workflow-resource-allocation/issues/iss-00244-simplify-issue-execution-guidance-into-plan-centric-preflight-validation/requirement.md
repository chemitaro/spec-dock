---
種別: 要件定義書（Issue）
ID: "iss-00244"
タイトル: "Simplify Issue Execution Guidance Into Plan Centric Preflight Validation"
関連GitHub: ["#244"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-27"
親: ["epic-00224", "init-local-00003"]
---

# iss-00244 Simplify Issue Execution Guidance Into Plan Centric Preflight Validation — 要件定義（何を、なぜ行うか）

## 目的

`guidance issue-execution` を、実行時に次 step / worker / reviewer / context を動的に選ぶ仕組みから、承認済み `plan.md` を実行してよいか確認する preflight / consistency validator へ単純化する。

これにより、agent が `plan.md`、skill、runtime guidance、`report.md`、generated projection の複数 authority を同時に追う状態を解消し、実装時の判断と品質ゲートを `plan.md` に一本化する。

## 背景・現状

- Epic 初期設計では、runtime が current step、worker、reasoning effort、context policy、verification、reviewer を compile し、`guidance issue-execution` に返す方向だった。
- Dogfooding 中、`report.md` に S01-S99 の完了証跡があるにもかかわらず、`guidance issue-execution` が `selected_step: S01` を返し続ける問題が発生した。
- 直接原因は report parser が一部 ledger 形式を読めないことだったが、追加分析では、`report.md` を実行制御 state として parse する model 自体が不安定であると判断した。
- `spec-dock/docs/phase_plan_issue.md` と `spec-dock/docs/authoring/issue-plan.md` は、すでに `plan.md` を planned executable workflow contract / command queue、`report.md` を observed evidence ledger と位置づけている。
- 現行 runtime / tests / skill 文面には、まだ `selected_step`、`step_assurance`、`context_packets`、runtime worker/reviewer/verification inference が残っている。
- ユーザー回答により、この Issue では `hard cutover` を採用する。不要な interface / field は互換期間なしで削除する。

## 情報源

- `discussions/20260627t130116z-research-plan-centric-execution-guidance-handoff.md`
- `discussions/20260627t131746z-research-plan-centric-guidance-requirement-preparation.md`
- `discussions/20260627t132248z-disc-plan-centric-guidance-requirement-scope-synthesis.md`
- `discussions/20260627t132404z-interview-default-guidance-dynamic-fields-cutover.md`
- `spec-dock/docs/workflow_issue.md`
- `spec-dock/docs/workflow_spec_authoring.md`
- `spec-dock/docs/phase_plan_issue.md`
- `spec-dock/docs/authoring/issue-plan.md`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/context_packets.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/context_routing.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/runbook.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/workflow.py`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
- `tests/cli_runtime/test_workflow.py`
- `tests/cli_runtime/test_workflow_context_routing.py`
- `tests/cli_runtime/test_assurance_compose.py`

## スコープ

### 必須

- `guidance issue-execution` の default Markdown / JSON / runbook projection から、authoritative dynamic execution fields を削除する。
- 削除対象には少なくとも `selected_step`、`step_assurance`、`context_packets`、runtime による worker / reviewer / verification / reasoning effort / context mode 推定を含める。
- `guidance issue-execution` は、ready / blocked / planning-required の preflight result、canonical artifact path、commands、stop conditions、contract source、evidence ledger を返す。
- `report.md` の completion evidence は audit evidence として扱い、runtime が次 step を選ぶ control plane には使わない。
- `plan.md` authoring / assurance compose / issue planning docs は、Issue-level Quality Profile と Step-level Obligation Pattern を計画時に作り込める guidance / scaffold を持つ。
- `spec-dock-issue-planning` と `spec-dock-issue-execution` の skill 文面から、runtime-selected step を task checklist / execution authority として扱う記述を削除する。
- 旧 dynamic model を期待する tests を、plan-centric preflight / plan contract lint / hard cutover を検証する tests に置き換える。
- provider source を正本として変更し、必要な dogfooding workspace 確認を行う。
- この Issue planning 作業自体を manual test として扱い、`guidance issue-planning` / `assurance classify` / `assurance compose` / `validate` の観測結果を `report.md` または discussion artifact に残す。

### 禁止

- `selected_step`、`step_assurance`、`context_packets` を deprecated field として default output に残さない。
- `report.md` parser を改善して dynamic step selector を延命しない。
- runtime が `plan.md` の free text から task kind を推定し、worker / reviewer / verification を決める仕組みを default issue execution に残さない。
- generated projection files を agent handoff authority にしない。
- `lite_candidate` を obligation reduction authority として扱わない。
- plan 不備を execution 中の暗黙判断で補わない。

### 対象外

- PR review policy / GitHub Codex review trigger の再設計。
- Issue lifecycle completion、`issue finish`、PR delivery / merge preparation workflow の再設計。
- 自動 Lite default の有効化。
- 新しい external agent invocation framework の導入。
- 既存完了 Issue の retroactive migration。
- 将来の明示的な context packet utility（必要なら別 Issue で扱う）。

## 境界

- 常に行う:
  - `plan.md` を execution contract、`report.md` を observed evidence ledger として扱う。
  - `guidance issue-execution` は execution readiness と consistency を確認し、`may_execute_approved_plan` で実行可否を明示する。実行順や step obligations は `plan.md` を参照するよう促す。
  - `assurance.json` の `authorized_profile` を obligation authority とし、`lite_candidate` は telemetry として扱う。
  - non-executable / scaffold / stale / unresolved な `requirement.md`、`design.md`、`plan.md` は execution-ready にしない。
  - invalid / stale assurance contract は fail-closed とし、`strict` fallback を current authority として偽装しない。
  - hard cutover のため、不要 interface / field は削除対象にする。
- 判断が必要:
  - `context_routing.py` / `context_packets.py` / related store の削除範囲は、残存利用を調査したうえで design で確定する。
  - `NoReview-ReadOnly` を正式 pattern として扱うか、`inspect-only` / `approved-no-op` の rationale として扱うかは design で整理する。
  - S90 / S99 の waiver syntax は、既存 `workflow_issue.md` / `phase_plan_issue.md` と矛盾しない範囲で design / plan へ落とす。
- 行わない:
  - runtime が次 step を選ぶ。
  - runtime が worker / reviewer / verification を計画書の代わりに決める。
  - generated context packet を default execution path で作成・参照させる。

## 非交渉制約

- Provider-side source under `src/spec_dock/assets/` を正本として変更する。
- `spec-dock/` は dogfooding / validation surface として確認する。
- Backward compatibility よりも hard cutover と authority simplification を優先する。
- CLI / Markdown / JSON output の新 contract は tests で固定する。
- `guidance issue-planning` / `guidance issue-execution` の projection は human/debug-only であり、agent authority ではない。
- `report.md` に残す planning workflow manual test 証跡は、raw transcript ではなく観測結果・判断・不具合有無に限定する。

## 受け入れ条件

- AC-001: Ready guidance is plan-centric
  - アクター: issue execution agent
  - 前提: active issue の `requirement.md` / `design.md` / `plan.md` / `assurance.json` が execution-ready である。
  - 操作: `./spec-dock/scripts/spec-dock guidance issue-execution` を実行する。
  - 期待結果: output は `plan.md` を contract source、`report.md` を evidence ledger として示し、approved plan を実行する next action と stop conditions を返す。
  - 観測点: CLI Markdown / JSON、projected runbook JSON / Markdown。

- AC-002: Dynamic execution fields are removed by hard cutover
  - アクター: issue execution agent / test suite
  - 前提: active issue が execution-ready である。
  - 操作: `guidance issue-execution` の Markdown / JSON / runbook projection を確認する。
  - 期待結果: `selected_step`、`step_assurance`、`context_packets` は default output に存在しない。
  - 観測点: CLI tests、projection JSON tests、Markdown assertions。

- AC-003: Report evidence is not a control plane
  - アクター: issue execution agent
  - 前提: `report.md` に S01-S99 の完了 / 未完了 / misleading rows がある。
  - 操作: `guidance issue-execution` を実行する。
  - 期待結果: runtime は `report.md` completion evidence から next step を算出せず、guidance output は report row の内容で変化しない。
  - 観測点: regression tests replacing old S01/S02 selection tests。

- AC-004: Non-executable plan blocks execution
  - アクター: issue execution agent
  - 前提: active issue の `plan.md` が scaffold、placeholder、構造化不足、未解決 marker、必須 gate 欠落のいずれかを含む。
  - 操作: `guidance issue-execution` を実行する。
  - 期待結果: execution-ready にならず、planning-required / blocked として `plan.md` 修正を促す。
  - 観測点: CLI tests、reason_code、stop conditions。

- AC-005: Plan contract captures execution obligations
  - アクター: issue planner
  - 前提: `assurance compose` 後に plan authoring を行う。
  - 操作: `plan.md` を作成する。
  - 期待結果: 各 implementation step は step pattern / worker allocation / allowed paths / forbidden changes / verification evidence / reviewer or no-review rationale / report evidence destination / commit-no-op gate / amendment trigger を持つ。
  - 観測点: plan authoring docs、compose fragments、plan lint / inspection tests。

- AC-006: Planning-time taxonomy prevents under-review
  - アクター: issue planner / spec reviewer
  - 前提: step が docs-only、runtime/tests、mixed code+docs、migration/rollback、auth/security/privacy、read-only/no-op のいずれかである。
  - 操作: plan contract を作成または lint する。
  - 期待結果: step obligation が risk と change type に応じて適切に表現され、canonical artifact mutation を no-review として扱わない。
  - 観測点: authoring docs / template / lint tests。

- AC-007: Skill kernels stop registering runtime-selected step
  - アクター: planning / execution agent
  - 前提: updated installed skill assets がある。
  - 操作: `spec-dock-issue-planning` / `spec-dock-issue-execution` skill を読む。
  - 期待結果: runtime-selected step を task checklist / execution authority として登録する記述がなく、state / next_action / commands / stop conditions / contract source / evidence ledger を扱う記述になっている。
  - 観測点: provider asset text assertions。

- AC-008: Obsolete dynamic tests are replaced
  - アクター: test suite
  - 前提: old context routing tests exist.
  - 操作: CLI runtime tests を実行する。
  - 期待結果: `selected_step` / worker inference / context packet generation を期待する tests は削除または置換され、plan-centric preflight behavior を検証する tests が pass する。
  - 観測点: `uv run pytest tests/cli_runtime/...`。

- AC-009: Issue planning guidance dogfood evidence is recorded
  - アクター: issue planner
  - 前提: この Issue の requirement / design / plan authoring を行う。
  - 操作: authoring 中に `guidance issue-planning`、`assurance classify`、`assurance compose`、`validate` を実行し、観測結果を記録する。
  - 期待結果: guidance が期待通りなら `report.md` に pass evidence を残し、不具合があれば `discussions/` に bug / research artifact を残す。
  - 観測点: `report.md` Spec Authoring Gate / Evidence Adoption Ledger、必要時の discussion artifact。

- AC-010: Provider and dogfooding surfaces stay consistent
  - アクター: maintainer
  - 前提: provider assets / runtime / tests を変更した。
  - 操作: relevant tests と `./spec-dock/scripts/spec-dock validate` を実行する。
  - 期待結果: provider source と dogfooding workspace の意図した差分が説明でき、validation が pass する。`guidance` が表示する `authorized_profile` / authority は current `assurance classify` source binding と矛盾しない。`workflow-plan-unselectable` のような旧 step selector 由来の block reason は issue-execution default path に残らない。
  - 観測点: test output、report evidence、git diff。

## 例外・エッジケース

- EC-001: Legacy issue without `assurance.json`
  - 条件: substantive requirement はあるが `assurance.json` がない。
  - 期待: strict legacy authority として readiness を扱う場合でも、dynamic selected step / context packet は返さない。
  - 観測点: CLI tests。

- EC-002: Stale source binding
  - 条件: `assurance.json` の source binding 後に requirement / design / plan が変わった。
  - 期待: execution-ready にせず、classification / planning repair を促す。
  - 観測点: existing stale binding tests。

- EC-003: Context policy missing or invalid
  - 条件: `context-routing-policy.json` が missing / invalid。
  - 期待: default `guidance issue-execution` は context packet generation に依存しないため、context policy の問題だけで ready issue を block しない。ただし残存機能がある場合は対象機能で fail-closed する。
  - 観測点: updated tests。

- EC-004: Docs-only but canonical workflow change
  - 条件: docs / templates / skill / workflow text の変更 step。
  - 期待: no-review ではなく `SpecOnly` 相当の spec-reviewer / docs inspection obligation を plan に持つ。
  - 観測点: plan lint / spec review。

- EC-005: Mixed code and docs step
  - 条件: runtime code と shipped docs / skill text を同じ step で変更する。
  - 期待: split-first、または `CodePlusSpec` 相当として both reviewer focus を plan に明記する。
  - 観測点: plan lint / reviewer checklist。

- EC-006: Generated projection stale
  - 条件: `.agent/runbooks/current-runbook.*` や `active/current-runbook.*` が古い。
  - 期待: agent は projection を authority として読まず、fresh stdout guidance と canonical docs を使う。projection refresh 後に `Step Assurance` / `Context Packets` / `selected_step` が残らない。
  - 観測点: skill text / tests。

## 用語

- Plan-centric execution:
  - `plan.md` を実行順と品質ゲートの authority とし、runtime guidance は readiness を確認するだけの execution model。
- Preflight validator:
  - 実行を始めてよい条件、足りない artifact、stop conditions を確認する runtime guidance の役割。
- Dynamic execution fields:
  - `selected_step`、`step_assurance`、`context_packets` など、runtime が実行時に step / worker / reviewer / context を選ぶための output fields。
- Hard cutover:
  - 旧 dynamic execution fields / interface を deprecated として残さず、default contract から削除する移行方針。
- Step-level Obligation Pattern:
  - step の change type / risk / evidence level に応じて、worker、verification、reviewer、no-review rationale、commit/no-op gate を計画時に固定する分類。

## 未確定事項

- Q-001:
  - 質問: `selected_step` / `step_assurance` / `context_packets` を互換期間なしで削除してよいか。
  - 回答: hard cutover を採用する。不要な interface / field は削除する。
  - 証跡: `discussions/20260627t132404z-interview-default-guidance-dynamic-fields-cutover.md`
  - 状態: 解決済み。

- Q-002:
  - 質問: `context_routing.py` / `context_packets.py` の削除範囲をどこまでにするか。
  - 推奨案: default issue-execution の旧 interface としては削除対象にし、残存利用がある場合だけ design で根拠付きに限定する。
  - 影響範囲: design / tests。
  - 状態: design で解決する。

- Q-003:
  - 質問: `NoReview-ReadOnly` を正式 pattern として採用するか。
  - 推奨案: canonical artifact mutation を no-review にしない制約を優先し、pattern 名は design / plan authoring の中で整理する。
  - 影響範囲: plan schema / lint / tests。
  - 状態: design で解決する。
