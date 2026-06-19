---
種別: research
ID: "20260619t023116z-research"
タイトル: "Issue 210 Clarification Research"
状態: "draft | completed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-19"
親: ["iss-00210"]
関連: []
authority: "synthesized"
derived_from: []
reflected_to: []
---

# 20260619t023116z-research Issue 210 Clarification Research

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約、用語衝突、edge case など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は source-grounded research evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、用語衝突、edge case、判断への含意を混ぜない。
- local context で解ける疑問は人間に聞かず、この artifact に source-grounding を残す。

## 調査目的 (必須)
- Issue 210 の要件具体化前に、GitHub issue 本文、親 Epic、現行 skill/docs、後続 Issue 211 の関係を読み、local source で解ける範囲とユーザー判断が必要な scope boundary を切り分ける。

## sources / 調査方法 (必須)
- 参照先:
  - `gh issue view 210 --json number,title,body,url,state`
  - `gh issue view 211 --json number,title,body,url,state`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/requirement.md`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/plan.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`
  - `spec-dock/docs/workflow_clarification.md`
  - `spec-dock/docs/authoring/decision-routing.md`
  - Issue-local `requirement.md`, `design.md`, `plan.md`, `report.md`
- 検証手順:
  - `./spec-dock/scripts/spec-dock active show`
  - `./spec-dock/scripts/spec-dock deps check iss-00210`
  - `git status --short --branch`
- 実験条件:
  - worktree: `/Users/iwasawayuuta/.codex/worktrees/f376/spec-dock`
  - active: not set
  - git state: detached `HEAD (no branch)`, clean before discussion artifact creation

## facts / 観測できた事実 (必須)
- Issue 210 の local `requirement.md` / `design.md` / `plan.md` は scaffold のままで、現時点の具体要求は GitHub issue #210 body が主な source である。
- `deps check iss-00210` は `ready=true blockers=0` で、SpecDock 上の機械的 blocker はない。
- 親 Epic `epic-00158` は agent-facing workflow / governance / context surface の改善を目的とし、skills は first-read workflow spine、docs は詳細 semantics、templates は薄い scaffold を所有する方針を持つ。
- 親 Epic は runtime gate / automated regression / harness を first-wave blocker にしない方針を持つ。
- 現行 `spec-dock-epic-planning/SKILL.md` は routing と authoring gate を持つが、GitHub #210 が求める system-architect draft cycle、issue-local draft package、Issue 作成後の draft distribution はまだ明示していない。
- GitHub #210 は、Epic planning で system-architect discussion draft を先に作り、main orchestrator が Evidence Adoption Ledger を通して canonical docs へ統合する flow を求めている。
- GitHub #210 は、Issue 作成前に Epic design / plan を具体化し、Issue 作成後は全 issue 横断の draft requirement / draft design package を system-architect が作り、各 issue の `discussions/` に `draft-requirement` / `draft-design` を置く flow を求めている。
- GitHub #210 の非目標は、system-architect が canonical docs を直接編集すること、Issue 作成前に issue canonical docs を完成させること、すべての Epic に heavyweight delegation を強制することではない。
- GitHub #211 は #210 の後続で、Epic planning 完了後の execution coordinator skill を追加する issue である。#211 は #210 を Epic planning draft cycle の担当 issueとして明示している。

## inference / 推測 (必須)
- 事実から推測したこと:
  - Issue 210 は implementation 以前に、Issue 211 が消費する planning completion / handoff artifact boundary を明確にする必要がある。
  - Issue 210 の責務は Epic planning の品質ゲートと draft handoff を定義することであり、Issue execution cycle、issue start/finish、PR merge preparation は Issue 211 へ渡すのが自然である。
  - ただし #210 がどこまで #211 向けの handoff contract を具体化するかで、更新対象が `spec-dock-epic-planning/SKILL.md` だけに留まるか、`workflow_epic.md` / `workflow_spec_authoring.md` / authoring docs まで広がるかが変わる。
- 推測の根拠:
  - #210 body は `spec-dock-epic-planning` skill を主対象にしつつ、必要なら workflow docs / delegated authoring docs の更新も候補にしている。
  - #211 body は #210 を非目標として分離し、Epic planning 完了後の coordinator を定義する。
  - 親 Epic は hidden mandatory workflow を docs 側だけに残さず、first-read skill surface に置く方針を持つ。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - `workflow_epic.md` と delegated authoring 関連 docs の具体的な現行記述。
  - `system-architect` role の現行 permission / expected output contract。
  - `new doc draft-requirement` / `draft-design` の template 具体内容。
- 確認できない理由:
  - requirement clarification の最初の pressure-test question 前は、scope boundary を決めるための必要最小限の source read に留めている。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - Issue 210 で、後続 Issue 211 が依存する Epic planning completion / handoff contract をどこまで固定するか。
  - system-architect draft cycle を「非自明な Epic では必須、軽微なら skip reason 可」として強めに書くか、「推奨」に留めるか。
  - Issue 作成後の cross-issue draft package を、Issue 210 の必須 deliverable として明記するか、後続 docs / execution issue へ委ねるか。
- pressure-test question として切り出すべき候補:
  - Issue 210 の要件は、`spec-dock-epic-planning` skill の first-read workflow に加えて、Issue 211 が利用する planning completion / handoff contract まで固定するべきか。
- 質問せずに解決できた候補:
  - Issue 210 と Issue 211 の基本順序: #210 が planning、#211 が planning 後の execution coordinator。
  - system-architect は canonical docs を直接編集しない。
  - Issue canonical docs は issue planning workflow で正式化し、Epic planning 後の draft は discussion evidence として扱う。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - `draft requirement / draft design`: canonical issue docs ではなく issue-local `discussions/` artifact を指す。
  - `Epic planning completion`: Epic canonical docs の reviewer pass だけなのか、Issue list / dependencies / issue-local draft package まで含むのかが未確定。
  - `system-architect draft cycle`: mandatory gate なのか conditional recommended gate なのかが未確定。
- 既存 docs / code / tests / discussions での使われ方:
  - 親 Epic は delegated / external output を Evidence として扱い、main orchestrator の adoption 記録なしに canonical artifact としない。
  - 現行 epic planning skill は authoring gate と bounded depth=2 delegation を記載しているが、draft package / issue draft distribution の語彙はまだ持たない。
- 判断が必要な理由:
  - 用語境界が曖昧なまま進めると、Issue 210 と 211 が同じ docs/skill surface に重複または矛盾した workflow を追加する。

## edge cases / 具体シナリオ (必須)
- edge case:
  - 軽微な Epic で system-architect draft cycle を必須化すると、workflow が重くなりすぎる。
  - 複数 Issue にまたがる大きい Epic で draft package を省略すると、Issue 間 vocabulary / dependency / handoff がばらける。
  - Issue 210 が execution coordinator の手順まで書きすぎると、Issue 211 の責務と重複する。
- その edge case が requirement / design / plan に与える影響:
  - Requirement では mandatory / conditional / recommended の適用条件を明記する必要がある。
  - Design では `spec-dock-epic-planning` と future `spec-dock-epic-execution` の境界、docs routing、handoff artifacts を分ける必要がある。
  - Plan では Issue 210 の step scope を planning skill/docs に限定し、Issue 211 用の execution cycle は依存先・後続として扱う必要がある。

## implications / 判断への含意 (必須)
- Issue 210 の最初の user interview は、planning completion / handoff contract の scope を決める質問にする。
- 回答は Issue 210 `requirement.md` の scope / non-scope / acceptance criteria、`design.md` の responsibility boundary、`plan.md` の implementation step と docs impact に反映する。
- 回答後、必要に応じて Issue 210 `report.md` の Evidence Adoption Ledger / Spec Authoring Gate に採用証跡を残す。

## リスク/制約 (任意)
- ...

## 反映先 (任意)
- reflected_to:
  - ...

## 参考（References） (任意)
- ...
