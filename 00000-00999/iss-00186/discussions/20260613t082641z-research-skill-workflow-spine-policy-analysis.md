---
種別: research
ID: "20260613t082641z-research"
タイトル: "Skill Workflow Spine Policy Analysis"
状態: "draft | completed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-13"
親: ["iss-00186"]
関連: []
authority: "synthesized"
derived_from: []
reflected_to: []
---

# 20260613t082641z-research Skill Workflow Spine Policy Analysis

## 調査目的 (必須)
- SpecDock の skill / workflow docs / templates の責務分担に関する既存運用を確認する。
- その運用方針に照らして、`spec-dock-issue-execution` skill をどのように更新すべきかを整理する。
- この research は後続 requirement / design / plan authoring の input であり、canonical authority ではない。

## sources / 調査方法 (必須)
- 参照先:
  - `.agents/skills/spec-dock-hub/SKILL.md`
  - `.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/authoring/issue-plan.md`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00165-align-workflow-docs-with-skill-spine-boundary/design.md`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/discussions/20260605t035200z-research-chatgpt-skill-docs-information-architecture-report.md`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/discussions/20260605t035201z-research-chatgpt-empirical-skill-compliance-tests-report.md`
  - `.codex/prompts/execute-issue.md`
  - `src/spec_dock/assets/install_root/.codex/prompts/execute-issue.md`
  - `spec-dock/templates/issue/plan.md`
  - `spec-dock/templates/issue/report.md`
- 検証手順:
  - `rg` で skill / workflow / thin / first-read / context-surface 関連の既存 records を探索した。
  - `iss-00165` の design と epic-level discussions から、skill/docs/templates の責務分担を抽出した。
  - `spec-dock-hub` skill、`workflow_issue.md`、`authoring/issue-plan.md`、templates、execute prompt を比較した。
- 実験条件:
  - 実装変更は行っていない。
  - 追加 deep-consultant analysis は別途待機中であり、この artifact は現時点の local source-grounded analysis を先に記録する。

## facts / 観測できた事実 (必須)
- `spec-dock-hub` skill は、自身を entry / route selector / global invariant surface と定義している。
- `spec-dock-hub` skill は、leaf skills が task-specific workflow spines を所有するとしている。
- `spec-dock-hub` skill は、skills が first-read workflow spine として mandatory next actions、stop conditions、reviewer gates、handoff boundaries を持つと定義している。
- `spec-dock-hub` skill は、`spec-dock/docs/` が detailed semantics、field meanings、lifecycle policy、hard cases、reference material を持つとしている。
- `spec-dock-hub` skill は、templates が minimum authoring scaffolds、evidence slots、examples であり compliance authorities ではないとしている。
- `iss-00165` design は、workflow / phase / authoring / entry docs を skill-owned first-read workflow spine の detail / reference layer として読める状態にすることを目的にしている。
- `iss-00165` design は、docs に lifecycle policy、field semantics、hard cases、report evidence semantics を残しつつ、mandatory first action が docs-only に隠れる authority wording を避けるとしている。
- `iss-00165` design は、Docs は thin にはせず detailed semantics / policy / hard cases を持つが、skill が first-read workflow spine を所有し docs は detail / reference を所有する関係を明示すると決定している。
- `iss-00165` design の Boundary Wording Contract は、workflow docs を detail authority とし、skills を operational entrypoints とする責務分担を明示している。
- epic-level research `20260605t035200z` は、`spec-dock-issue-execution` を top-loaded runbook へ reorganize し、excessive schema detail は docs に戻す案を提示している。
- 同 research は `spec-dock-issue-execution` について、Must read、Entry preflight、Execution loop を skill 上部に出し、詳細は docs pointers に残す案を提示している。
- epic-level research `20260605t035201z` は、docs を同じに保ったまま skill text だけを変えて agent behavior を比較する empirical PDCA harness を提案している。
- 同 research は、revised skill は concise mandatory procedure reminders を持つが、detailed semantics は docs に残す条件を置いている。
- 同 research の Prompt 4 は、approved plan step が `.agents/skills/spec-dock-issue-execution/SKILL.md` と `workflow_issue.md` を更新する場合、親 agent が直接編集せず `doc-writer` に委任する expected behavior を定義している。

## inference / 推測 (必須)
- 事実から推測したこと:
  - SpecDock の既存運用は「skill は薄い」だけではなく、「skill は first-read runbook と hard gate を持つが、詳細 semantics は docs に置く」という二層構造である。
  - `spec-dock-issue-execution` の現状問題は、skill が薄すぎることではなく、first-read runbook として必要な loop / stop condition / next-step unlock が top-loaded されていないことである。
  - 今回の修正は、workflow docs の detail authority を維持しながら、skill に agent が最初に守るべき mandatory action sequence を短く追加するのが既存方針と整合する。
  - `workflow_issue.md` 側には exact policy name と completion semantics を置き、skill 側はそれをチェックする短い preflight / per-step / completion loop にするのがよい。
  - `authoring/issue-plan.md` は field semantics / schema の detail authority なので、reviewer fail conditions や plan step schema の整備はここに置くのが自然である。
  - templates は compliance authority ではないが、agent が具体的に記入するときの誘導面なので、`N/A` や multi-step batch を誘う scaffold 表現は修正対象になり得る。
  - `execute-issue` prompt は operational entrypoint の一つであり、skill と矛盾しない範囲で file mutation 前の worker handoff を明示する価値がある。
- 推測の根拠:
  - hub skill と `iss-00165` design の責務分担が一致している。
  - epic-level research はすでに `spec-dock-issue-execution` の top-loaded runbook 化を提案している。
  - empirical research は skill-level mandatory reminders が agent behavior を改善するかを検証対象にしており、今回の問題と一致する。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - 追加 deep-consultant が同じ結論に到達するか。
  - provider-side template / prompt / workflow docs と dogfooding mirror の全差分。
  - `spec-dock update` による dogfooding mirror refresh strategy。
  - どこまでを `iss-00186` の scope に含め、どこを follow-up に分離するべきか。
- 確認できない理由:
  - 現時点は research artifact 作成 phase であり、canonical requirement / design / plan はまだ authored されていない。
  - additional consultant analysis は非同期で実行中である。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - `iss-00186` の scope に templates / prompts / empirical harness まで含めるか、skill + workflow docs に絞るか。
  - 親 direct implementation exception を語彙変更まで行うか、既存語彙を残して条件を強化するか。
- pressure-test question として切り出すべき候補:
  - `iss-00186` は skill / workflow / authoring docs / templates / prompt の横断 issue として扱うべきか、それとも skill + workflow の最小修正 issue にすべきか。
- 質問せずに解決できた候補:
  - skill と docs の責務分担は existing repo evidence から確認できた。
  - skill を long schema の置き場にしない方針は existing repo evidence から確認できた。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - `thin skill`
  - `first-read workflow spine`
  - `detail authority`
  - `source of truth`
  - `compliance authority`
- 既存 docs / code / tests / discussions での使われ方:
  - `thin skill` は「何も書かず docs に丸投げ」ではなく、mandatory next actions / stop conditions / reviewer gates / handoff boundaries を持つ first-read surface を意味する。
  - `detail authority` は workflow docs / authoring docs が lifecycle policy、field semantics、hard cases を持つことを意味する。
  - `source of truth` は `spec-dock-issue-execution` skill 上では `workflow_issue.md` を指すが、hub / `iss-00165` の運用では skill が operational first action を持つ。
  - templates は scaffold / evidence slots / examples であり compliance authority ではない。
- 判断が必要な理由:
  - `source of truth` を docs-only first action と誤読すると、skill が必要な stop condition を露出せず、今回の追随性問題を再発させる。

## edge cases / 具体シナリオ (必須)
- edge case:
  - Skill に詳細 policy を入れすぎて、workflow docs と二重正本になる。
  - Skill を薄くしすぎて、agent が workflow docs を読まずに実装へ進む。
  - Workflow docs にだけ強い規約を追加し、実行入口である skill / prompt は変わらない。
  - Template は compliance authority ではないとして放置した結果、plan authoring 時に `N/A` や multi-step log が再生産される。
  - Empirical harness を scope に入れすぎて、まず必要な skill/workflow wording hardening が大きくなりすぎる。
- その edge case が requirement / design / plan に与える影響:
  - Requirement では、skill / docs / template の責務分担を非交渉制約に入れる必要がある。
  - Design では、どの surface にどの種類の rule を置くかを table 化する必要がある。
  - Plan では、skill top-loaded runbook、workflow exact semantics、authoring fail conditions、template/prompt alignment、verification を別 step にする必要がある。

## implications / 判断への含意 (必須)
- Skill update:
  - `spec-dock-issue-execution` の上部に `Must read before execution`、`Entry preflight`、`Single-step execution loop`、`Completion claim stop conditions` を短く置く。
  - Field schema、report table schema、long completion matrix は skill に移さず docs へ残す。
  - `Parent direct implementation` は normal path ではなく pre-recorded exception だけであることを skill の first-read surface に出す。
- Workflow docs update:
  - `Execution Readiness Gate`、`Step Result Approval`、`Final commit is not a catch-up implementation commit`、`mutating implementation step delegation` の exact semantics を `workflow_issue.md` に置く。
  - `approved-local-execution` / `degraded mode` の扱いを completion success と誤読されないよう整理する。
- Authoring docs / templates update:
  - `authoring/issue-plan.md` の reviewer fail conditions に missing step reviewer gate、missing commit/no-op gate、missing next-step unlock condition、mutating step with `N/A` delegated role を追加する。
  - `templates/issue/plan.md` の `delegated role` から mutating implementation step 用の `N/A` を外すか、approved-no-op / read-only only と明記する。
  - `templates/issue/report.md` の `Step: S01, S02, ...` を single-step cursor / repair-only multi-step note へ変える。
- Prompt update:
  - `/execute-issue` prompt に、file mutation 前に worker handoff を作り `dev-coder` / `doc-writer` へ委任することを明示する。
- Verification:
  - Provider source と dogfooding mirror の parity を確認する。
  - `rg` / tests / snapshot で forbidden wording と required gate wording を検査する。
  - 可能なら empirical prompt harness を follow-up または S99 evidence として扱う。

## リスク/制約 (任意)
- Skill を厚くしすぎると `iss-00165` の information architecture と矛盾する。
- Workflow docs だけを更新すると agent の first action が変わらない。
- Template / prompt まで同一 issue に入れると scope が大きくなりすぎる可能性がある。
- Runtime enforcement は将来有効だが、今回の主問題は agent action selection なので先に wording / workflow contract を固めるのがよい。

## 反映先 (任意)
- reflected_to:
  - candidate: `requirement.md`
  - candidate: `design.md`
  - candidate: `plan.md`
  - candidate: `report.md` Evidence Adoption Ledger
  - candidate: `workflow_issue.md`
  - candidate: `authoring/issue-plan.md`
  - candidate: `spec-dock-issue-execution` skill
  - candidate: `templates/issue/plan.md`
  - candidate: `templates/issue/report.md`
  - candidate: `.codex/prompts/execute-issue.md`

## 参考（References） (任意)
- `.agents/skills/spec-dock-hub/SKILL.md`
- `.agents/skills/spec-dock-issue-execution/SKILL.md`
- `spec-dock/docs/workflow_issue.md`
- `spec-dock/docs/authoring/issue-plan.md`
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00165-align-workflow-docs-with-skill-spine-boundary/design.md`
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/discussions/20260605t035200z-research-chatgpt-skill-docs-information-architecture-report.md`
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/discussions/20260605t035201z-research-chatgpt-empirical-skill-compliance-tests-report.md`
- `.codex/prompts/execute-issue.md`
- `src/spec_dock/assets/install_root/.codex/prompts/execute-issue.md`
- `spec-dock/templates/issue/plan.md`
- `spec-dock/templates/issue/report.md`
