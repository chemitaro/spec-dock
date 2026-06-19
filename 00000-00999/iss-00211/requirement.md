---
種別: 要件定義書（Issue）
ID: "iss-00211"
タイトル: "Epic Execution Coordinator Skill"
関連GitHub: ["#211"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-19"
親: ["epic-00158", "init-local-00003"]
---

# iss-00211 Epic Execution Coordinator Skill — 要件定義（何を、なぜ行うか）

## 目的
- Epic planning 後に複数 Issue の planning / execution / finish / PR merge-ready preparation を順序立てて扱う first-read operational skill `spec-dock-epic-execution` を追加する。
- Issue 210 で定義した Epic planning handoff の後段として、Epic execution lifecycle を `workflow_epic.md` に最小限接続する。

## 背景・現状
- 現状の挙動:
  - `spec-dock-epic-planning` は Epic requirement / design / plan authoring を扱う。
  - `spec-dock-issue-planning` は Issue requirement / design / plan authoring を扱う。
  - `spec-dock-issue-execution` は approved / reviewer-pass 済み Issue plan の実装 loop を扱う。
  - `github-pr-merge-preparer` は PR creation / observation / repair loop / merge-prepared evidence を扱う。
- 現状の課題:
  - Epic planning 完了後、複数 Issue をどの順で start / planning / execution / finish し、いつ Epic-level completion gate と PR merge-ready preparation へ進むかを読む first-read coordinator がない。
  - `workflow_epic.md` は Planning Completion / Handoff を定義しているが、execution coordinator behavior、issue start / finish cycle、PR merge-ready preparation は later Issue に残されている。
- 情報源:
  - GitHub issue #211。
  - `discussions/20260619t063017z-research-issue-211-clarification-source-review.md`
  - `discussions/20260619t063303z-disc-issue-211-clarification-synthesis.md`
  - `discussions/20260619t063309z-interview-issue-211-scope-pressure-test.md`
  - `spec-dock/docs/workflow_epic.md`
  - `spec-dock/docs/workflow_issue.md`
  - Existing skills under `src/spec_dock/assets/install_root/.agents/skills/`

## 対象ユーザー / 利用シナリオ
- 主な利用者:
  - SpecDock を使って Epic planning 完了後の複数 Issue 実行を進める orchestrator agent。
- 代表シナリオ:
  - Active Epic の planning outputs を確認し、dependency / ready state に従って次の Issue を選び、Issue planning、Issue execution、Issue finish、次 Issue、Epic completion gate、PR merge-ready preparation へ進める。

## スコープ
- 必須:
  - Provider-side installed skill として `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md` を追加する。
  - Dogfooding mirror として `.agents/skills/spec-dock-epic-execution/SKILL.md` を追加する。
  - `spec-dock-epic-execution` は Epic execution coordinator として、既存 SpecDock commands / skills の順序、停止条件、委譲先、証跡記録を案内する。
  - `workflow_epic.md` に Epic planning handoff 後の Epic execution lifecycle、Epic completion gate、PR merge-preparer handoff を短い reference section として追加する。
  - 新 managed skill が installer / update / dogfooding asset parity の既存 tests に含まれるよう、必要な provider tests / expected asset lists を更新する。
  - 必要に応じて `spec-dock-hub` や wrapper / docs references へ最小 cross-reference を追加し、new skill が discoverable になるようにする。
- 禁止:
  - `spec-dock-issue-planning`、`spec-dock-issue-execution`、`github-pr-merge-preparer` の責務を新 skill に吸収しない。
  - PR merge 自体を自動化・指示しない。
  - Runtime CLI command を新規追加しない。
  - GitHub issue / PR state を直接変更する新しい code path を追加しない。
  - GitHub #211 に列挙された docs を理由なく横断更新する broad docs cleanup は行わない。
- 対象外:
  - Epic / Issue dependency algorithm の runtime 実装変更。
  - `spec-dock issue start` / `issue finish` / `deps check` の command behavior 変更。
  - 新しい agent role / host adapter の追加。
  - Existing skills の大規模 rewrite。

## 境界
- 常に行う:
  - Active Epic / active Issue / git / dependency / GitHub freshness の bootstrap check を first-read flow に含める。
  - Ready Issue selection は existing dependency state と `deps check` を参照する前提にする。
  - Issue planning は `spec-dock-issue-planning`、Issue execution は `spec-dock-issue-execution`、PR merge-ready preparation は `github-pr-merge-preparer` へ委譲する。
  - All Issues complete 後に Epic-level completion evidence / review disposition / PR handoff を確認する。
- 判断が必要:
  - 複数 ready Issue がある場合の選択は、Epic plan の dependency / priority / risk と current active state に基づく。
  - `workflow_issue.md`、`workflow_spec_authoring.md`、`decision-routing.md`、`reference_github.md` の更新は、実装設計中に明確な参照欠落が見つかった場合のみ最小追加する。
- 行わない:
  - New skill は detailed implementation steps を実行しない。
  - New skill は reviewer pass、Issue finish、PR merge-prepared state を自己主張しない。

## 非交渉制約
- Repo docs が source of truth。provider-side shipped assets は `src/spec_dock/assets/install_root/` と `src/spec_dock/assets/spec_dock/` を source of truth として更新する。
- Dogfooding mirror under `.agents/` / `spec-dock/` は provider-side changes と整合させる。
- Skill prose は first-read として短く、重い lifecycle semantics は `workflow_epic.md` に置く。
- Existing workflow authority と矛盾しない。特に `issue finish` は lifecycle-only、PR merge は human action、reviewer pass は fresh reviewer gate である。
- New tests / assertions は managed asset inclusion と discoverability regression を検出できる必要がある。

## 前提
- Issue 210 は完了済みで、Epic planning completion / handoff contract は `workflow_epic.md` に反映済み。
- Issue 211 は Issue 210 と独立した Issue として実行するが、Issue 210 の handoff context は参照してよい。
- ユーザーは Option B を採用済み: skill 追加に加えて `workflow_epic.md` の最小 reference を含める。

## 受け入れ条件
- AC-001: New skill availability
  - アクター: orchestrator agent。
  - 前提: repo checkout に provider-side installed assets と dogfooding mirror がある。
  - 操作: skill list / filesystem から `spec-dock-epic-execution` を確認する。
  - 期待結果: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md` と `.agents/skills/spec-dock-epic-execution/SKILL.md` が存在し、同じ first-read coordinator contract を提供する。
  - 観測点: file inspection、managed asset tests。
- AC-002: Coordinator responsibility boundary
  - アクター: orchestrator agent。
  - 前提: Epic planning 完了後に Epic execution を始める。
  - 操作: `spec-dock-epic-execution` skill を first-read する。
  - 期待結果: active Epic / dependencies / ready Issue / issue start / issue planning / issue execution / issue finish / Epic completion / PR merge-ready handoff の順序と停止条件がわかり、既存 skills の置換ではなく委譲先が明示される。
  - 観測点: skill prose inspection、spec-reviewer review。
- AC-003: Epic workflow reference
  - アクター: future agent。
  - 前提: `workflow_epic.md` の Planning Completion / Handoff を読んだ後。
  - 操作: Epic execution lifecycle の reference を探す。
  - 期待結果: `workflow_epic.md` に Epic execution lifecycle、completion gate、PR merge-preparer handoff の短い section があり、Issue 210 handoff と Issue 211 coordinator の関係がわかる。
  - 観測点: docs inspection、provider / dogfooding docs parity。
- AC-004: Discoverability and routing
  - アクター: orchestrator agent。
  - 前提: user asks to execute an Epic rather than only plan it.
  - 操作: hub / wrapper / README / tests など existing discovery surfaces を確認する。
  - 期待結果: relevant first-read surface can route Epic execution work to `spec-dock-epic-execution` without confusing it with `spec-dock-epic-planning` or `spec-dock-issue-execution`.
  - 観測点: minimal cross-reference inspection、targeted tests。
- AC-005: Installer / update regression coverage
  - アクター: maintainer。
  - 前提: provider-side new skill is added。
  - 操作: relevant unit / CLI runtime tests を実行する。
  - 期待結果: init / update / managed asset parity / Japanese-primary / installed skill list tests が new skill を含めて pass する。
  - 観測点: `uv run pytest ...` の targeted result。

## 例外・エッジケース
- EC-001: Active Issue already exists
  - 条件: Epic execution start 時点で active Issue が残っている。
  - 期待: skill は active Issue を無視して次 Issue を start せず、current state の確認、継続 / finish / human decision の必要性を示す。
  - 観測点: skill prose inspection。
- EC-002: No ready Issue
  - 条件: Epic に未完了 Issue はあるが dependency / blockers により ready Issue がない。
  - 期待: skill は implementation を進めず、deps evidence / blocked reason / report or discussion record / user escalation を案内する。
  - 観測点: skill prose inspection。
- EC-003: Multiple ready Issues
  - 条件: 複数 Issue が ready。
  - 期待: skill は Epic plan の dependency / priority / risk を参照して一つずつ選び、parallel execution を default にしない。
  - 観測点: skill prose inspection。
- EC-004: Small Epic / no-op Epic
  - 条件: Epic に実行すべき Issue がない、または all Issues already complete。
  - 期待: skill は no-op / completion evidence / Epic-level gate / PR handoff を案内し、不要な Issue planning / execution を作らない。
  - 観測点: skill prose inspection。
- EC-005: PR preparation blocked
  - 条件: PR checks、review threads、observation limitation、or merge-preparer result が blocked。
  - 期待: skill は PR merge-ready を自己主張せず、`github-pr-merge-preparer` の result と unresolved risk を evidence として扱う。
  - 観測点: skill prose inspection。

## 用語（ドメイン語彙）
- TERM-001: Epic execution
  - Epic planning 後に、複数 Issue の start / planning / execution / finish / completion / PR handoff を coordinator として進める workflow。
- TERM-002: Issue execution
  - `spec-dock-issue-execution` が所有する、approved / reviewer-pass 済み Issue plan の one-step-at-a-time implementation loop。
- TERM-003: Merge-ready preparation
  - `github-pr-merge-preparer` が所有する PR creation / observation / repair loop / merge-prepared evidence。PR merge そのものではない。

## 未確定事項
- なし。Option B は `discussions/20260619t063309z-interview-issue-211-scope-pressure-test.md` でユーザー承認済み。
