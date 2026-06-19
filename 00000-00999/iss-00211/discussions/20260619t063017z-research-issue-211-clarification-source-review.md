---
種別: research
ID: "20260619t063017z-research"
タイトル: "Issue 211 Clarification Source Review"
状態: "draft | completed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-19"
親: ["iss-00211"]
関連: []
authority: "synthesized"
derived_from: []
reflected_to: []
---

# 20260619t063017z-research Issue 211 Clarification Source Review

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約、用語衝突、edge case など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は source-grounded research evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、用語衝突、edge case、判断への含意を混ぜない。
- local context で解ける疑問は人間に聞かず、この artifact に source-grounding を残す。

## 調査目的 (必須)
- Issue 211 の requirement / design / plan authoring 前に、`spec-dock-epic-execution` が何を coordinator として所有し、何を既存 workflow / skills に委譲すべきかを source-grounded に整理する。
- ユーザーに聞くべき論点を、local sources で解決できない owner-intent / scope tradeoff に絞る。

## sources / 調査方法 (必須)
- 参照先:
  - User request in current session: Issue 211 の作業開始、要件分析、インタビュー、途中経過 artifact 記録。
  - GitHub issue #211 body: Epic execution skill should coordinate issue planning, execution, finish, and merge-ready PR preparation.
  - Active Issue docs: `spec-dock/active/issue/{requirement.md,design.md,plan.md,report.md}`.
  - Parent docs: `spec-dock/active/epic/requirement.md`, `spec-dock/active/initiative/requirement.md`.
  - Clarification workflow: `spec-dock/docs/workflow_clarification.md`, `spec-dock/docs/authoring/decision-routing.md`.
  - Existing operational skills: `spec-dock-issue-planning`, `spec-dock-issue-execution`, `github-pr-merge-preparer`.
  - Issue 210 output / handoff contract: `spec-dock/docs/workflow_epic.md` Planning Completion / Handoff section.
  - Existing skill layout under `src/spec_dock/assets/install_root/.agents/skills/` and dogfooding mirror `.agents/skills/`.
- 検証手順:
  - `active show` で active Issue が `iss-00211` であることを確認。
  - GitHub #211 body を `gh issue view 211 --json ...` で取得。
  - `rg` / `find` で既存 `spec-dock-epic-execution` skill が存在しないこと、関連 workflow references の有無を確認。
- 実験条件:
  - 実装・canonical docs 更新前の clarification phase。
  - Active issue docs は template scaffold 状態で、まだ Issue 211 固有の requirement / design / plan にはなっていない。

## facts / 観測できた事実 (必須)
- Issue 211 は GitHub #211 として OPEN で、local SpecDock node `iss-00211-epic-execution-coordinator-skill` に import 済み。
- Active Issue は `iss-00211`。`requirement.md` / `design.md` / `plan.md` / `report.md` は template scaffold で、Issue 固有内容は未具体化。
- Provider-side installed skill authority は `src/spec_dock/assets/install_root/.agents/skills/`。dogfooding mirror は `.agents/skills/`。
- Existing provider-side skills に `spec-dock-epic-execution` は存在しない。
- GitHub #211 は、新 skill path として `.agents/skills/spec-dock-epic-execution/SKILL.md` を想定している。provider-side authority に照らすと実装対象は `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md` と dogfooding mirror `.agents/skills/spec-dock-epic-execution/SKILL.md` になる可能性が高い。
- GitHub #211 は、必要なら `workflow_epic.md` / `workflow_issue.md` / `workflow_spec_authoring.md` / `authoring/decision-routing.md` / `reference_github.md` の追加・更新を許容している。
- Issue 210 の成果として `workflow_epic.md` は Epic planning completion / handoff package を定義している。Downstream Issue は Epic planning outputs と handoff contract を参照できるが、execution coordinator behavior / issue start-finish cycle / PR merge-ready preparation は later Issue 側の責務として残されている。
- `spec-dock-issue-planning` は Issue canonical `requirement.md` / `design.md` / `plan.md` の authoring order、delegated draft、fresh `spec-reviewer` gate、Evidence Adoption Ledger を所有する。
- `spec-dock-issue-execution` は approved / reviewer-pass 済み issue plan を前提に、1 step at a time、delegated implementation、review / commit / PR delivery / issue finish prerequisites を所有する。
- `github-pr-merge-preparer` は PR creation / observation / repair loop / merge-prepared evidence を所有し、PR merge や `issue finish` は禁止している。
- `workflow_issue.md` は `issue finish` が lifecycle-only command であり、delivery completion / PR merge readiness は別証跡として `issue finish` 前に report へ記録する必要があると定義している。
- `workflow_epic.md` は Epic-wide pre-PR gate として、全 Issue 完了後の Epic-level evidence、fresh `deep-consultant` / `spec-reviewer` review、指摘 disposition を要求している。

## inference / 推測 (必須)
- 事実から推測したこと:
  - Issue 211 の主成果は、新しい first-read operational skill `spec-dock-epic-execution` の追加である可能性が高い。
  - この skill は heavy implementation engine ではなく、既存 Issue planning / Issue execution / PR merge preparation skills を順に呼ぶ coordinator spine として設計すべき。
  - Docs 更新は、skill だけで十分か、Epic workflow docs に Epic execution lifecycle の reference semantics を足すかが主要 tradeoff になる。
  - Runtime CLI の新 command は GitHub #211 の本文には必須として書かれていない。`deps check`, `issue start`, `issue finish`, `validate`, `sync`, `gh pr...` など既存 command を使う workflow skill の追加で足りる可能性が高い。
  - Test obligation は docs/skill/scaffold behavior になるため、provider installed skill inclusion / mirror parity / Japanese-primary docs policy / provider tests snapshot などの既存 test style を確認して plan 化する必要がある。
- 推測の根拠:
  - GitHub #211 の非目標が、Issue planning / Issue execution / GitHub PR merge preparation の置換を明示的に否定している。
  - `github-pr-merge-preparer` は merge-prepared までを所有し、merge は人間 action とする設計になっている。
  - Existing skill set は leaf operational skills を provider-side install_root から shipping する構造になっている。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - `spec-dock-epic-execution` を skill-only で閉じるか、`workflow_epic.md` に Epic execution section を追加するか。
  - Epic execution coordinator が small Epic の skip / no-op をどの程度 first-read に含めるべきか。
  - Epic-wide review gate に `deep-consultant` を必須として skill first-read に残すか、既存 `workflow_epic.md` の reference に委譲するか。
  - PR merge preparation を Epic completion gate の後に必須とするか、Epic execution skill は merge-ready PR preparation への handoff までを定義し、実際の PR requirement は caller / Epic plan に依存させるか。
  - Provider-side docs/tests の正確な変更範囲。
- 確認できない理由:
  - 上記は local source だけでは一意に決まらない owner-intent / scope tradeoff。特に shipped skill の first-read 密度と docs 更新の広がりを変える。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - Q1: Issue 211 は skill-only 最小追加に寄せるか、`workflow_epic.md` に Epic execution lifecycle reference も追加するか。
  - Q2: `spec-dock-epic-execution` は Epic-level final review / PR merge preparation を「必須 gate」として書くか、「Epic plan が要求する場合の handoff」として書くか。
  - Q3: small Epic の skip/no-op を first-read にどこまで明記するか。
- pressure-test question として切り出すべき候補:
  - Q1。変更対象ファイル、acceptance criteria、test obligation、docs impact、Issue 210 handoff の消費方法を大きく変える。
- 質問せずに解決できた候補:
  - Runtime CLI 新 command は必須ではない。既存 Issue / deps / PR skills を順序制御する skill が GitHub #211 の主眼。
  - Issue planning / execution / PR merge-preparer は置き換えない。これは GitHub #211 と既存 skill docs の双方で確定。
  - PR merge はしない。`github-pr-merge-preparer` が明示的に human merge decision までの preparation を所有する。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - "Epic execution" と "Issue execution"。
  - "merge-ready / merge preparation" と "merge"。
  - "finish" と "delivery completion"。
- 既存 docs / code / tests / discussions での使われ方:
  - Issue execution は `spec-dock-issue-execution` と `workflow_issue.md` が所有する approved issue plan の実装 loop。
  - Epic execution は GitHub #211 では Epic planning 後の複数 Issue lifecycle coordination を指す。
  - `github-pr-merge-preparer` は merge-prepared evidence までで、merge は forbidden / human action。
  - `issue finish` は lifecycle-only close / active clear であり、PR readiness や delivery completion ではない。
- 判断が必要な理由:
  - Skill 名が `spec-dock-epic-execution` でも、実装内容は Issue execution の再実装ではなく coordinator であることを明確にしないと、既存 workflow と責務衝突する。

## edge cases / 具体シナリオ (必須)
- edge case:
  - Active issue が残っている状態で Epic execution を始める。
  - 複数 ready Issue がある。
  - 依存関係が未解決 / GitHub live state が stale。
  - Issue planning 中に requirement gap が出る。
  - Issue execution 中に plan gap が出る。
  - Issue finish 後に manual `sync` が branch-derived active を復元し得る caveat。
  - 全 Issue 完了後に Epic-level review が fail する。
  - PR observation が timeout / unresolved thread limitation / check failure で止まる。
  - 小規模 Epic で heavyweight Epic execution が過剰な場合。
- その edge case が requirement / design / plan に与える影響:
  - Bootstrap / stop condition / human gate / report evidence / no-op skip reason を acceptance criteria と design contract に含める必要がある。
  - plan では skill追加、docs更新、mirror検証、tests更新を分けた step にする可能性が高い。

## implications / 判断への含意 (必須)
- Requirement には、`spec-dock-epic-execution` の責務を "coordinator, not replacement" として明記する必要がある。
- Requirement には、active state / dependency state / git state bootstrap、ready issue selection、one issue at a time default、issue planning handoff、issue execution handoff、issue finish / next issue loop、Epic completion gate、PR merge-preparer handoff、blocked/follow-up evidence を acceptance criteria として置ける。
- Design には、provider-side installed skill、dogfooding mirror、必要 docs更新、test strategy、non-goals の境界を置く必要がある。
- Plan には、S01 skill追加、S02 docs更新が必要な場合、S03 mirror / provider test / snapshot update、S90/S99 gate などを分けて設計する可能性が高い。
- ADR は現時点では不要に見える。既存 workflow family への leaf skill 追加であり、長期 architecture choice というより Issue-local coordinator surface の追加。

## リスク/制約 (任意)
- Skill に詳細を詰め込みすぎると、Epic / Issue / PR workflow docs と重複し drift する。
- Skill を薄くしすぎると、Issue 210 と同じ failure mode、つまり first-read surface だけでは agent が正しい順序を判断できない状態が残る。
- Docs 更新範囲を広げすぎると Issue 211 が workflow docs 横断 cleanup に膨らむ。
- Existing provider tests は shipped docs の Japanese-primary prose や dogfooding snapshot drift に敏感。docs更新時は targeted provider tests を plan に入れる必要がある。

## 反映先 (任意)
- reflected_to:
  - Pending: `requirement.md`, later `design.md`, `plan.md`, and `report.md` Evidence Adoption Ledger.

## 参考（References） (任意)
- `spec-dock/docs/workflow_epic.md`
- `spec-dock/docs/workflow_issue.md`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`
- GitHub issue #211
