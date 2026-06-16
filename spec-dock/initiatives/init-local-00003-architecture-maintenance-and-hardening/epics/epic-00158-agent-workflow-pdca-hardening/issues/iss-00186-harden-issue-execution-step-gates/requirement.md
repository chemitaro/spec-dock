---
種別: 要件定義書（Issue）
ID: "iss-00186"
タイトル: "Harden Issue Execution Step Gates"
関連GitHub: ["#186"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-16"
親: ["epic-00158", "init-local-00003"]
---

# iss-00186 Harden Issue Execution Step Gates — 要件定義

## 目的

`spec-dock-issue-execution` の first-read surface と issue execution detail docs を、実装 step の逐次実行、per-step review、per-step commit、委任前提の file mutation を踏み外しにくい形へ強化する。

この issue は、既存 ADR `Skill Docs Template Context Surface Ownership` に従い、skill には compact workflow spine、docs には detail semantics、templates には scaffold / evidence slots という責務分担を維持したまま、issue execution の入口ゲートを harden する。

## 背景・現状

- 現状の挙動:
  - `spec-dock/docs/workflow_issue.md` は、`1 implementation step = 1 review scope = 1 commit`、delegation gate、reviewer gate、commit gate、completion policy を詳細に定義している。
  - `.agents/skills/spec-dock-issue-execution/SKILL.md` は `workflow_issue.md` を source of truth とする concise reminder であり、runtime / tests / scaffold behavior は `dev-coder`、shipped docs / templates / skills / workflow text は `doc-writer` へ route すると説明している。
  - `spec-dock/docs/authoring/issue-plan.md` は executable step schema、delegation contract、具体テストケース一覧、step gate の field semantics を定義している。
- 現状の課題:
  - 実行入口である `spec-dock-issue-execution` skill では、`single current step -> required verification -> fresh reviewer pass -> commit -> post-commit clean -> next step unlock` の loop が十分に top-loaded されていない。
  - `approved-local-execution`、`degraded mode`、`final commit`、`step result approval` の境界が誤読されると、親 agent の直接実装、複数 step の同時実装、per-step review / commit 省略につながる。
  - workflow docs だけを補強しても、agent が first-read skill surface で踏み外す問題は残る。
- 観測された failure mode:
  - 複数 implementation step を同時並行で実装し、1 review / 1 commit にまとめる。
  - step reviewer pass 前、または commit / clean check 前に次 step へ進む。
  - `dev-coder` / `doc-writer` ではなく、main orchestrator が通常の実装者として file mutation を行う。
  - reviewer fail の修正を bounded delegated follow-up ではなく親 agent が直接修正する。
  - final commit を、過去 step の未 commit implementation diff をまとめる救済 commit と誤読する。
- 情報源:
  - `spec-dock/active/issue/discussions/20260613t082454z-research-issue-execution-step-gate-analysis.md`
  - `spec-dock/active/issue/discussions/20260613t082641z-research-skill-workflow-spine-policy-analysis.md`
  - `spec-dock/active/issue/discussions/20260613t083027z-research-deep-consultant-skill-policy-findings.md`
  - `spec-dock/active/issue/discussions/20260613t084318z-disc-issue-execution-skill-update-direction.md`
  - `spec-dock/active/issue/discussions/20260615t152809z-interview-issue-execution-hardening-scope-boundary.md`
  - `spec-dock/active/epic/discussions/20260605t080509z-adr-skill-docs-template-context-surface-ownership.md`
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/authoring/issue-plan.md`
  - `.agents/skills/spec-dock-issue-execution/SKILL.md`

## 対象ユーザー / 利用シナリオ

- 主な利用者:
  - SpecDock issue execution を行う main orchestrator。
  - `dev-coder` / `doc-writer` へ bounded implementation step を委任する agent。
  - per-step / final review を行う `spec-reviewer`、`code-reviewer`、`qa-reviewer`。
- 代表シナリオ:
  - Agent が `spec-dock-issue-execution` skill を読んだ時点で、承認済み `plan.md` の single current step だけを対象にし、次 step へ進む前に reviewer pass、commit、clean check が必要だと理解できる。
  - Agent は file mutation を通常 path として `dev-coder` / `doc-writer` に委任し、親直接実装は事前記録済み `Parent Implementation Exception` に限定する。
  - Completion claim 時、final commit / degraded mode / approved-local-execution を通常の per-step gate 代替として扱わない。

## スコープ

- 必須:
  - Provider-side `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md` を、compact issue execution gate spine として強化する。
  - Provider-side `src/spec_dock/assets/spec_dock/docs/workflow_issue.md` に、必要最小限の exact semantics 補強を行う。
  - 関連する provider-side tests / assertions を、変更後の required wording と既存 fragment preservation に合わせて更新する。
  - Dogfooding mirror `.agents/skills/spec-dock-issue-execution/SKILL.md` と `spec-dock/docs/workflow_issue.md` を provider source と整合させ、`sync` / `validate` / targeted inspection の証跡を残す。
  - `spec-dock/docs/authoring/issue-plan.md`、provider templates、`.codex/prompts/execute-issue.md` は alignment check 対象にする。
  - Alignment check で重大な矛盾が見つかった場合だけ、この issue 内で小さく補正するか、blocking / non-blocking follow-up として記録する。
- 禁止:
  - `workflow_issue.md` の lifecycle / completion policy 全文を skill へ移植して、skill と docs の二重正本を作る。
  - Templates を compliance authority、phase promotion authority、issue completion authority として扱う。
  - Empirical compliance harness、runtime enforcement、CLI validation gate をこの issue の必須実装にする。
  - `dev-coder` / `doc-writer` agent definition や global sub-agent 権限モデルをこの issue に吸収する。
  - 既存 ADR の context-surface ownership を reopen する。
- 対象外:
  - Provider templates の全面 rewrite。
  - `/execute-issue` prompt の大規模再設計。
  - Past issue report の backfill。
  - Runtime command behavior、SpecDock CLI lifecycle implementation、GitHub integration behavior の変更。
  - Automated empirical prompt tuning / compliance harness の新設。

## 境界

- 常に行う:
  - Skill には agent が first-read で守る mandatory next action、stop condition、route、exit gate を置く。
  - Detailed lifecycle policy、field meanings、hard cases、completion matrix は docs に残す。
  - Provider-side source を shipped asset authority とし、dogfooding mirror は validation target として扱う。
  - Skill 変更時は、既存 test fragments を不用意に壊さず、additive な wording を優先する。
  - `report.md` Evidence Adoption Ledger に、research / discussion / interview の採用判断を残す。
- 判断が必要:
  - Alignment check で見つかった authoring docs / templates / prompt の矛盾を、この issue 内の小修正に含めるか follow-up にするか。
  - `approved-local-execution` / `degraded mode` の語彙を置換するか、既存語彙を残して例外境界だけ明確化するか。
- 行わない:
  - Skill を long schema / field manual にしない。
  - Workflow docs だけを更新して skill first-read surface を放置しない。
  - Final review や final commit を per-step review / per-step commit の代替にしない。
  - Sub-agent unavailable / denied / host conflict を degraded success または親直接実装の自動承認にしない。

## 非交渉制約

- `1 implementation step = 1 review scope = 1 commit` を first-read skill と workflow detail の両方から読み取れること。
- 次 step の実装 / 委任 / review / commit を始める前に、現在 step の required verification、fresh step reviewer pass、Step Commit Gate、post-commit clean check が必要だと読み取れること。
- File mutation は通常 path で `dev-coder` / `doc-writer` へ委任され、parent direct implementation は事前記録済み `Parent Implementation Exception` に限定されること。
- `approved-local-execution`、`degraded mode`、`waived`、unavailable / denied / host conflict は required reviewer gate pass や normal implementation success と誤読されないこと。
- `final commit` は earlier implementation step の未 commit diff をまとめる catch-up commit ではないこと。
- Templates are not compliance authorities.
- Additional ADR is not required unless implementation introduces a new durable ownership model beyond the accepted ADR.

## 前提

- Active issue は `iss-00186` である。
- User interview `20260615t152809z-interview-issue-execution-hardening-scope-boundary.md` で Option B が採用済みである。
- Accepted ADR `20260605t080509z-adr-skill-docs-template-context-surface-ownership.md` が、skills / docs / templates の責務分担を固定している。
- `iss-00166` が template scaffold consistency の主領域を持つため、本 issue は template 全面 rewrite を扱わない。

## 受け入れ条件

- AC-001: First-read single-step gate
  - アクター: issue execution を開始する main orchestrator。
  - 前提: 承認済み `requirement.md` / `design.md` / executable `plan.md` がある。
  - 操作: `spec-dock-issue-execution` skill を読む。
  - 期待結果: agent は single current implementation step だけを対象にし、次 step へ進む前に required verification、fresh step reviewer pass、commit/no-op gate、post-commit clean check が必要だと判断できる。
  - 観測点: provider skill、dogfooding mirror skill、targeted wording assertion / inspection。
- AC-002: Delegated mutation gate
  - アクター: file mutation を伴う implementation step を進める main orchestrator。
  - 前提: step が runtime / tests / scaffold behavior、または shipped docs / templates / skills / workflow text を変更する。
  - 操作: skill と workflow detail を確認する。
  - 期待結果: runtime / tests / scaffold behavior は `dev-coder`、shipped docs / templates / skills / workflow text は `doc-writer` へ route し、parent direct implementation は事前記録済み `Parent Implementation Exception` だけに限定される。
  - 観測点: provider skill、`workflow_issue.md`、report evidence slots。
- AC-003: Reviewer fail and follow-up gate
  - アクター: step reviewer fail を受けた main orchestrator。
  - 前提: per-step reviewer が `fail` を返す。
  - 操作: follow-up path を確認する。
  - 期待結果: 親 agent は通常 direct fix を行わず、bounded delegated follow-up と fresh re-review を必要とする。親 direct fix には別途 `Parent Implementation Exception` が必要だと分かる。
  - 観測点: provider skill、`workflow_issue.md`、targeted assertion / inspection。
- AC-004: Completion terminology boundary
  - アクター: issue completion を報告しようとする main orchestrator。
  - 前提: implementation delegation availability、reviewer state、final commit、step commit evidence が混在している。
  - 操作: `workflow_issue.md` の completion policy を確認する。
  - 期待結果: `approved-local-execution` / `degraded mode` / `waived` / unavailable / denied / host conflict / final commit が、required reviewer pass や per-step commit の代替ではないと判断できる。
  - 観測点: provider workflow docs、dogfooding mirror docs、targeted assertion / inspection。
- AC-005: Context-surface ownership compliance
  - アクター: maintainer / reviewer。
  - 前提: issue-wide diff を確認する。
  - 操作: skill / docs / templates / prompt の責務分担を inspect する。
  - 期待結果: skill は compact workflow spine、docs は detail semantics、templates は scaffold / evidence slots として読める。Skill bloat、docs-only hidden workflow、template compliance authority 化がない。
  - 観測点: changed files、alignment check、spec-reviewer verdict。
- AC-006: Provider and dogfooding validation
  - アクター: maintainer。
  - 前提: provider-side shipped assets が変更される。
  - 操作: dogfooding mirror を同期 / 確認し、SpecDock validation を実行する。
  - 期待結果: provider source と installed mirror の意図した整合が確認され、`./spec-dock/scripts/spec-dock validate` が pass する。
  - 観測点: sync / validate command output、targeted file inspection、report evidence。
- AC-007: Evidence adoption and planning readiness
  - アクター: main orchestrator。
  - 前提: research / discussion / interview artifacts が存在する。
  - 操作: requirement / design / plan / report へ採用判断を反映する。
  - 期待結果: 採用 / 部分採用 / deferred / rejected が `report.md` Evidence Adoption Ledger に残り、fresh `spec-reviewer` pass なしに次 phase へ進まない。
  - 観測点: `report.md` Evidence Adoption Ledger、Spec Authoring Gate、reviewer verdict。

## 例外・エッジケース

- EC-001: Multiple-step bundling attempt
  - 条件: S01 と S02 が同じ file family を触るため、agent がまとめて実装しようとする。
  - 期待: skill / workflow detail から、同時実装ではなく single current step、per-step review、per-step commit、post-commit clean が必要だと分かる。
  - 観測点: skill wording、workflow wording、plan step gate。
- EC-002: Sub-agent unavailable / denied / host conflict
  - 条件: required delegated worker または reviewer が利用不可、拒否、host policy conflict になる。
  - 期待: degraded success や親直接実装の自動承認にはならず、blocked / incomplete、waiver、または `Parent Implementation Exception` の明示手続きが必要だと分かる。
  - 観測点: `workflow_issue.md`、report gate evidence。
- EC-003: Skill-text-only / docs-only implementation step
  - 条件: code test を置かない docs-only / skill-text-only change。
  - 期待: code test 不要理由と inspect-only / docs diff / spec-review evidence が固定され、review 不要とは扱われない。
  - 観測点: plan concrete test cases、step reviewer gate、spec-reviewer verdict。
- EC-004: Final commit catch-up misconception
  - 条件: S99 final quality gate 時に未 commit implementation diff が残っている。
  - 期待: final commit は catch-up implementation commit ではなく、missing per-step commit は incomplete / repair path として扱われる。
  - 観測点: `workflow_issue.md`、report Step Commit Gate。
- EC-005: Alignment check finds broad template / prompt drift
  - 条件: authoring docs / templates / prompt に重大だが大きい drift が見つかる。
  - 期待: この issue 内で小さく修正できるものだけ扱い、全面 rewrite や empirical harness は follow-up / deferred として記録する。
  - 観測点: report Evidence Adoption Ledger、Spec Interpretation / Decision Ledger。

## 用語

- First-read workflow spine:
  - Agent が linked docs を読む前に守るべき mandatory next actions、stop conditions、reviewer gates、handoff boundaries。
- Detail semantics:
  - Docs が所有する lifecycle policy、field meanings、hard cases、completion policy。
- Step Result Approval:
  - 次 step へ進むために、現在 step の closure、required verification、fresh reviewer pass、commit/no-op gate、post-commit clean が閉じている状態。
- Parent Implementation Exception:
  - 親 agent が例外的に直接 file mutation するために、delegation 不可理由、user approval、allowed files、allowed operation、rollback plan、post-change verification、reviewer gate を事前記録する例外手続き。
- Catch-up final commit:
  - 過去 implementation step の未 commit diff を final commit にまとめる誤った運用。本 issue では禁止境界として扱う。

## 未確定事項

- Blocking question:
  - なし。Option B 採用により、scope / non-scope / acceptance criteria は design review へ渡せる粒度で確定している。
- Non-blocking design questions:
  - Alignment check で見つかった authoring docs / templates / prompt の drift を小修正するか、follow-up にするか。
  - `approved-local-execution` / `degraded mode` の語彙を維持して補足するか、最小限の言い換えを行うか。
