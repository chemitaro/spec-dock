---
種別: research
ID: "20260613t082454z-research"
タイトル: "Issue Execution Step Gate Analysis"
状態: "draft | completed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-13"
親: ["iss-00186"]
関連: []
authority: "synthesized"
derived_from: []
reflected_to: []
---

# 20260613t082454z-research Issue Execution Step Gate Analysis

## 調査目的 (必須)
- `spec-dock-issue-execution` skill を使った Issue 実行で、実装 step の並行実装、per-step review / commit の欠落、親 Codex による直接実装が起きる理由を整理する。
- 先行 deep-consultant 3 名の分析と main orchestrator の分析を、`iss-00186` の後続 requirement / design / plan authoring に使える research evidence として残す。
- この artifact は canonical authority ではない。採用する場合は canonical docs または `report.md` Evidence Adoption Ledger へ反映判断を残す。

## sources / 調査方法 (必須)
- 参照先:
  - `.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `.agents/skills/spec-dock-hub/SKILL.md`
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/authoring/issue-plan.md`
  - `spec-dock/templates/issue/report.md`
  - `spec-dock/templates/issue/plan.md`
  - `.codex/prompts/execute-issue.md`
  - Prior deep-consultant outputs in the originating chat for `iss-00186` creation.
- 検証手順:
  - `spec-dock-issue-execution` skill の mandatory reminder と、`workflow_issue.md` の execution contract を比較した。
  - `workflow_issue.md` の step order、delegation、reviewer gate、commit gate、completion gate の記述を確認した。
  - `authoring/issue-plan.md` の executable step schema と reviewer fail conditions を確認した。
  - report / plan templates が複数 step 一括記録や `N/A` delegated role を許す見え方になっていないか確認した。
- 実験条件:
  - 実装や canonical docs の編集は行っていない。
  - 先行分析は read-only consultant analysis と main orchestrator analysis の synthesis である。

## facts / 観測できた事実 (必須)
- `spec-dock-issue-execution` skill は `workflow_issue.md` を source of truth とし、自身を concise reminder と位置づけている。
- skill は `plan.md` を executable workflow contract / command queue として扱うよう指示しているが、`current step only -> review pass -> commit -> clean -> next step unlock` の loop を入口で明示していない。
- skill は runtime / tests / scaffold behavior を `dev-coder`、shipped docs / templates / skills / workflow text を `doc-writer` へ route すると書いている。
- skill は review fail 時に bounded delegated follow-up と rerun review を求め、親 direct fix には documented `Parent Implementation Exception` が必要だとしている。
- `workflow_issue.md` は parent Codex を orchestration owner と定義し、code / runtime / tests / scaffold behavior / templates / shipped docs / skills / workflow text の直接実装者ではないと定義している。
- `workflow_issue.md` は各 implementation step を `step closure contract -> implementation delegation decision -> bounded implementation batch -> verification -> refactor/tidy -> report draft update -> step reviewer gate -> fix -> re-review -> commit -> clean確認` の順で進めるとしている。
- `workflow_issue.md` は `1 implementation step = 1 review scope = 1 commit` を標準とし、複数 step の変更を 1 commit に混ぜてはならないとしている。
- `workflow_issue.md` は step commit 後に `git status --short` などで次 step へ持ち越す意図しない変更がないことを確認するとしている。
- `workflow_issue.md` は `complete` 条件に、全 implementation step の `committed` または正当な `approved-no-op`、final QA / code / spec reviews、PR Delivery Gate、Merge Preparation Gate、final commit / clean evidence を含めている。
- `authoring/issue-plan.md` は plan authoring が reviewer-pass 済み requirement / design を、実装可能な step、検証、review gate、commit gate、final quality gate へ変換する責務を持つとしている。
- `authoring/issue-plan.md` は each implementation step の `delegation contract`、`具体テストケース一覧`、`step closure contract`、`behavior slice execution`、`step gate` を必須項目としている。
- `authoring/issue-plan.md` は `workflow_issue.md` の delegated-by-default policy を再定義せず、step-local `delegation contract` として worker が追加判断なしに作業できる項目へ具体化するとしている。

## inference / 推測 (必須)
- 事実から推測したこと:
  - 問題の中心は `workflow_issue.md` に規約がないことではなく、実行入口の skill / prompt / template が agent の最初の行動を十分に固定していないことにある。
  - `spec-dock-issue-execution` skill が concise reminder として詳細を参照先へ逃がしすぎると、agent は長い workflow doc 内の hard gate を見落とし、複数 step をまとめて進める。
  - `approved-local-execution` や `degraded mode` が completion evidence の並びに見えると、例外経路が通常経路に見え、親 Codex direct implementation を誘発する。
  - final commit が明示されている一方で「final commit は過去 step の未 commit implementation diff をまとめる場所ではない」と明示されていないため、per-step commit の代替として誤読される余地がある。
  - `step result approval` は存在するが、`closure pass / approved-no-op + fresh reviewer pass + Step Commit Gate + post-commit clean + no open decision/blocker` のような exact gate として定義すると、次 step unlock が明確になる。
  - plan / report templates 側にも、mutating implementation step の `delegated role: N/A` や `Step: S01, S02, ...` のような一括記録を誘う表現が残る場合、skill だけを直しても運用追随性は十分に上がらない。
- 推測の根拠:
  - deep-consultant 3 名の分析はいずれも、既存 workflow は強いが skill / entrypoint / template が hard gate を top-level に出していない点を主因としていた。
  - main orchestrator の一次分析でも、`workflow_issue.md` の規約は強い一方で `SKILL.md` の bullet は loop / next-step unlock / exception invalidation を十分に露出していないと確認した。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - 実際の `doc-writer` / `dev-coder` がこの workflow に沿って file mutation できるかどうかの runtime behavior。
  - `execute-issue` prompt の provider-side source と installed mirror が完全に同期しているか。
  - issue execution skill の変更だけで empirical compliance が改善するか。
  - report / plan templates の `N/A` や multi-step notation が現行最新版でも同じ問題を持つかの全量確認。
- 確認できない理由:
  - この作業は research capture であり、まだ requirement / design / plan authoring や implementation phase に入っていない。
  - empirical harness 実行や subagent runtime validation は別 step の検証対象になる。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - 親 Codex direct implementation を完全禁止に近づけるか、`Parent Implementation Exception` を明確化したうえで限定的に残すか。
  - `approved-local-execution` という語を維持するか、`approved-parent-implementation-exception` のように例外性が見える名称へ変えるか。
  - `degraded mode` を implementation step closure の値から外すか、availability evidence のみとして残すか。
- pressure-test question として切り出すべき候補:
  - 「通常の mutating implementation step は常に delegated とし、親実装は事前承認済み例外だけにする」方針を採用してよいか。
- 質問せずに解決できた候補:
  - skill / workflow / templates の責務分担は既存 docs と discussions から確認できるため、現時点ではユーザー質問なしで research を進められる。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - `approved-local-execution`
  - `degraded mode`
  - `step result approval`
  - `final commit`
- 既存 docs / code / tests / discussions での使われ方:
  - `approved-local-execution` は `Parent Implementation Exception` を満たす場合のみ使える例外として説明される一方、completion evidence の候補として並ぶため通常値に見える。
  - `degraded mode` は unavailable / denied / host conflict を success にしないという制約を持つ一方、Implementation Delegation Gate closure の候補に見える。
  - `step result approval` は次 step へ進む条件として出るが、何を満たせば approval なのかの compact definition が弱い。
  - `final commit` は final report ledger の commit として必要だが、未 commit implementation diff のまとめ commit と誤読される余地がある。
- 判断が必要な理由:
  - これらの用語が曖昧なままだと、agent は failure / exception / availability evidence を completion evidence と誤読し、今回の問題を再発させる。

## edge cases / 具体シナリオ (必須)
- edge case:
  - S01 と S02 が同じファイルを触るため、agent がまとめて実装し、最後に一括 review / commit してしまう。
  - S01 の reviewer fail に対して、親 Codex が「小さい修正」として直接直し、delegated follow-up と re-review evidence を省略する。
  - doc-only / skill-text-only step で code test がないため、review 不要と誤認し、`spec-reviewer` docs/spec alignment を省略する。
  - subagent unavailable のため、親が degraded mode として直接実装し、blocked / incomplete としない。
  - S99 final quality gate 時に未 commit implementation diff が見つかり、final commit に混ぜてしまう。
- その edge case が requirement / design / plan に与える影響:
  - Requirement では、逐次実行、委任、review、commit、clean check の非交渉制約を観測可能にする必要がある。
  - Design では、skill / workflow / authoring docs / templates / prompts のどこに hard gate を置くかを責務分担として決める必要がある。
  - Plan では、skill text change、workflow definition change、template / prompt change、verification / empirical harness を step 分割する必要がある。

## implications / 判断への含意 (必須)
- `spec-dock-issue-execution` skill には、長い schema ではなく、top-loaded mandatory runbook を追加するのが妥当である。
- `workflow_issue.md` には、`Step Result Approval`、`Execution Readiness Gate`、`Final commit is not a catch-up commit`、`mutating implementation step delegation` の exact policy を置くのが妥当である。
- `authoring/issue-plan.md` には、plan reviewer fail conditions として missing step reviewer gate、missing commit/no-op gate、missing next-step unlock condition、mutating step with `N/A` delegated role、final review substituting per-step review を追加する余地がある。
- `templates/issue/plan.md` / `templates/issue/report.md` には、mutating step の `N/A` 禁止、single-step cursor / next-step unlock evidence、multi-step bundled log の禁止または repair-only 化を検討する余地がある。
- `.codex/prompts/execute-issue.md` には、親が file mutation 前に worker handoff を作ること、worker unavailable は blocked / incomplete であって direct implementation approval ではないことを明示する余地がある。
- スキルを厚くしすぎると既存の information architecture と衝突するため、field semantics や long completion matrix は docs に残し、skill には first actions / stop conditions / route map / exit gate のみを置くのがよい。

## リスク/制約 (任意)
- Skill へ詳細 policy を移しすぎると、docs と skill の二重正本になり drift が増える。
- Workflow docs だけを変更すると、agent の first action が変わらず追随性が上がらない。
- Runtime enforcement だけに寄せると、agent が invalid workflow action を試した後に失敗するだけになり、ユーザー体験が改善しにくい。
- テンプレートだけを変えると、既存 authored plans には効かない。

## 反映先 (任意)
- reflected_to:
  - candidate: `requirement.md`
  - candidate: `design.md`
  - candidate: `plan.md`
  - candidate: `report.md` Evidence Adoption Ledger
  - candidate: `spec-dock-issue-execution` skill update scope

## 参考（References） (任意)
- `.agents/skills/spec-dock-issue-execution/SKILL.md`
- `.agents/skills/spec-dock-hub/SKILL.md`
- `spec-dock/docs/workflow_issue.md`
- `spec-dock/docs/authoring/issue-plan.md`
- `spec-dock/templates/issue/plan.md`
- `spec-dock/templates/issue/report.md`
- `.codex/prompts/execute-issue.md`
