---
種別: 要件定義書（Issue）
ID: "iss-00159"
タイトル: "Make Issue Planning Skill Expose Mandatory Authoring Gates"
関連GitHub: ["#159"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-05"
親: ["epic-00158", "init-local-00003"]
---

# iss-00159 Make Issue Planning Skill Expose Mandatory Authoring Gates — 要件定義（何を、なぜ行うか）

## 目的

`spec-dock-issue-planning` skill を、Issue の requirement / design / plan authoring で agent が守るべき必須手順を読み飛ばしにくい instruction surface へ改善する。

## 背景・現状

- 現状の挙動:
  - `spec-dock-issue-planning` は主要 docs への参照と一部の reviewer gate reminder を持つ。
  - しかし、実際の step-by-step workflow spine は主に `workflow_spec_authoring.md`、`workflow_issue.md`、`phase_plan_issue.md`、`authoring/issue-plan.md` に分散している。
- 現状の課題:
  - agent が linked docs を開かない、または一部だけ読む場合、requirement -> review -> design -> review -> plan -> review -> execution handoff の順序や stop conditions を十分に認識できない。
  - その結果、review gate の省略、requirement/design/plan の同時作成、未解決 gap の execution への持ち越し、report evidence の不足が起きやすい。
- 観測点:
  - Skill surface: `.agents/skills/spec-dock-issue-planning/SKILL.md`
  - Shipped asset source: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
  - Workflow docs: `spec-dock/docs/workflow_spec_authoring.md`, `spec-dock/docs/workflow_issue.md`
- 情報源:
  - `spec-dock/active/epic/discussions/20260605t040338z-disc-skill-docs-workflow-spine-synthesis.md`
  - `spec-dock/active/epic/discussions/20260605t035200z-research-chatgpt-skill-docs-information-architecture-report.md`
  - `spec-dock/active/epic/discussions/20260605t040000z-research-chatgpt-skill-rewrite-targets-report.md`
  - `spec-dock/active/epic/issues/iss-00159-make-issue-planning-skill-expose-mandatory-authoring-gates/discussions/20260605t040646z-disc-issue-planning-skill-spine-handoff.md`

## 対象ユーザー / 利用シナリオ

- 主な利用者:
  - SpecDock issue planning を行う Codex / sub-agent / human operator.
- 代表シナリオ:
  - agent が `spec-dock-issue-planning` skill を読んだ時点で、Issue authoring の phase order、必須 reviewer gate、stop conditions、report evidence obligation を理解し、docs を読む前に誤った phase promotion をしない。

## スコープ

- 必須:
  - `spec-dock-issue-planning` skill に、agent が守るべき mandatory workflow spine を明示する。
  - Skill 先頭側に、短い named section `Mandatory Issue Authoring Workflow` または同等の section を置く。
  - requirement -> fresh `spec-reviewer` pass -> design -> fresh `spec-reviewer` pass -> plan -> fresh `spec-reviewer` pass -> execution handoff の順序を skill 本文で可視化する。
  - reviewer の missing / stale / failed / unavailable / denied / waived / provisional、またはその他の non-pass state が pass ではないことを skill 本文で明示する。
  - `fresh` は、対象 phase の current artifact candidate に対して latest substantive change 後に実行された `review_status: pass` を意味することを skill 本文で最小限明示する。
  - canonical `requirement.md` / `design.md` / `plan.md` / `report.md` は main orchestrator owned であり、delegated drafts は main orchestrator が canonical artifact に採用し `report.md` に証跡化するまで evidence であることを明示する。
  - unresolved requirement / design / plan gap は clarification または prior authoring phase へ戻すことを明示する。
  - Issue `plan.md` が issue-plan docs に照らして executable でなければ execution handoff は blocked であることを明示する。
  - Skill は詳細 schema を複製せず、詳細の owner docs へ誘導する。
  - Skill は lifecycle / spec authoring / clarification / issue plan phase / issue-plan field semantics の各 activity がどの docs を読むべきかを短く対応づける。
- 禁止:
  - runtime gate、CLI command、validation logic をこの issue で追加しない。
  - workflow policy の意味を変えない。
  - issue-plan field schema を skill に長くコピーしない。
  - template を compliance authority にしない。
- 対象外:
  - hub skill (`spec-driven-tdd-workflow`) の再構成。
  - `spec-dock-issue-execution` skill の再構成。
  - epic / initiative planning skill への横展開。
  - manual compliance harness の実装。
  - `gate status --json` などの runtime enforcement。

## 境界

- 常に行う:
  - Provider-side source of truth を確認してから対象 skill を変更する。
  - Provider-side source と dogfooding mirror を同一 issue で更新し、rewritten instruction content の semantic identity を保つ。
  - Skill には mandatory procedure / stop condition / evidence obligation を書く。
  - 詳細 schema、field semantics、例、edge case は docs に残す。
- 判断が必要:
  - skill に置く section 名と順序。
  - exact wording が docs と重複しすぎていないか。
- 行わない:
  - issue execution や implementation gate の policy をこの issue で再設計しない。
  - model compliance を runtime enforcement だけで解決したことにしない。

## 非交渉制約

- `src/spec_dock/assets/install_root/.agents/skills/` が installed agent-tooling assets の source of truth である。
- Shipped docs / templates / skills / workflow text の変更は issue execution では `doc-writer` 対象だが、この requirement phase では変更方針だけを固定する。
- Completion や phase promotion は fresh `spec-reviewer` pass なしに主張しない。
- この issue の first change は小さく、`spec-dock-issue-planning` skill に限定する。

## 前提

- `epic-00158` の ChatGPT `じっくり思考 Pro` research は、`今すぐ回答` を使わずに取得された clean research を採用候補とする。
- `gate status --json` は後続候補として残すが、この issue の初手ではない。
- この issue は PDCA の最初の実装 issue であり、後続で hub / issue execution / evaluation harness へ展開する。

## Instruction boundary

- この issue は `spec-dock-issue-planning` の instruction surface を変更する。
- この issue は workflow policy、runtime enforcement、reviewer behavior、validation logic を変更しない。
- Skill には、agent が詳細 docs を開く前に守るべき mandatory operational gates を置く。
- Docs は、conceptual meaning、field semantics、schemas、detailed authoring guidance の source of truth として残す。
- Skill は、該当 artifact / activity を作成・修正する前に読むべき docs へ短く誘導する。

## 受け入れ条件

- AC-001:
  - アクター: Issue planning を行う agent
  - 前提: agent が `spec-dock-issue-planning` skill を読む
  - 操作: Issue requirement/design/plan authoring の次アクションを判断する
  - 期待結果: linked docs を開かなくても、skill 本文だけで requirement -> fresh `spec-reviewer` pass -> design -> fresh `spec-reviewer` pass -> plan -> fresh `spec-reviewer` pass -> execution handoff の mandatory sequence を識別できる
  - 観測点: `spec-dock-issue-planning/SKILL.md`
- AC-002:
  - アクター: Issue planning を行う agent
  - 前提: reviewer result が missing / stale / failed / unavailable / denied / waived / provisional のいずれかである
  - 操作: 次 phase または execution handoff へ進めるか判断する
  - 期待結果: explicit fresh `review_status: pass` だけが promotion / handoff gate を満たし、その他の non-pass state は blocked / incomplete または re-review required と判断できる wording が skill にある
  - 観測点: `spec-dock-issue-planning/SKILL.md`
- AC-003:
  - アクター: Issue planning を行う agent
  - 前提: requirement / design / plan に unresolved gap がある
  - 操作: plan または execution へ進めるか判断する
  - 期待結果: gap を execution assumption にせず、clarification または該当 authoring phase へ戻す wording が skill にある
  - 観測点: `spec-dock-issue-planning/SKILL.md`
- AC-004:
  - アクター: Issue planning を行う agent
  - 前提: delegated draft / discussion / research が存在する
  - 操作: canonical artifact として扱えるか判断する
  - 期待結果: main orchestrator が canonical artifact に採用し `report.md` に証跡化するまで canonical authority にならないことが skill にある
  - 観測点: `spec-dock-issue-planning/SKILL.md`
- AC-005:
  - アクター: Reviewer / maintainer
  - 前提: skill rewrite diff を確認する
  - 操作: skill が詳細 docs を過剰コピーしていないか確認する
  - 期待結果: field schema や長い policy は docs への参照に留まり、skill は runbook / stop condition / evidence obligation に集中している
  - 観測点: diff, `workflow_spec_authoring.md`, `workflow_issue.md`, `phase_plan_issue.md`, `authoring/issue-plan.md`
- AC-006:
  - アクター: Issue planning を行う agent
  - 前提: execution handoff を判断する
  - 操作: `plan.md` が executable か確認する
  - 期待結果: `plan.md` が issue-plan docs に照らして executable でなければ execution handoff は blocked であり、詳細 executable-step schema は docs を読む必要があることが skill にある
  - 観測点: `spec-dock-issue-planning/SKILL.md`, `phase_plan_issue.md`, `authoring/issue-plan.md`
- AC-007:
  - アクター: Issue planning を行う agent
  - 前提: requirement / design / plan の phase promotion を記録する
  - 操作: report evidence を残す
  - 期待結果: 各 Spec Authoring Gate の reviewer verdict / fixes / promotion decision / execution handoff readiness を issue `report.md` に記録することが skill にある
  - 観測点: `spec-dock-issue-planning/SKILL.md`
- AC-008:
  - アクター: Maintainer
  - 前提: provider-side skill と dogfooding mirror がある
  - 操作: 対象 skill の source-of-truth と mirror の整合を確認する
  - 期待結果: installed asset source と dogfooding mirror の rewritten instruction content が semantically identical である、または exact divergence と理由が `report.md` に記録されている
  - 観測点: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`, `.agents/skills/spec-dock-issue-planning/SKILL.md`, `report.md`
- AC-009:
  - アクター: Issue planning を行う agent
  - 前提: activity ごとに詳細 docs を読む必要がある
  - 操作: skill の doc routing を確認する
  - 期待結果: lifecycle / spec authoring / clarification / issue plan phase / issue-plan field semantics の docs references が維持または改善されている
  - 観測点: `spec-dock-issue-planning/SKILL.md`

## 例外・エッジケース

- EC-001:
  - 条件: root `.agents/skills/` mirror と provider-side source が既に差分を持つ
  - 期待: 差分を無批判に上書きせず、source-of-truth と dogfooding update 方針を design/report に記録する
  - 観測点: diff, `report.md`
- EC-002:
  - 条件: skill wording を追加すると長すぎて読みにくくなる
  - 期待: section headings と checklist で構造化し、詳細 schema は docs に残す
  - 観測点: skill file diff
- EC-003:
  - 条件: compliance improvement を確認する automated harness がまだない
  - 期待: この issue では smoke probe または inspection を最小検証にし、full harness は follow-up とする
  - 観測点: `plan.md`, `report.md`

## 入力→出力例

- EX-001:
  - 入力: agent が issue planning のため `spec-dock-issue-planning` skill を読む
  - 出力: agent は requirement/design/plan を同時に並行作成せず、requirement gate から順に進める
- EX-002:
  - 入力: plan authoring 中に requirement gap が見つかる
  - 出力: agent は gap を plan に押し込まず、requirement/clarification へ戻す

## 用語（ドメイン語彙）

- TERM-001:
  - workflow spine: agent が最初に読む skill 上に置く、必須手順・停止条件・証跡義務の最小 runbook。
- TERM-002:
  - non-pass reviewer state: missing / stale / failed / unavailable / denied / waived / provisional など、fresh passed reviewer として扱えない状態。
- TERM-003:
  - executable handoff: Issue `plan.md` が実行者に追加の workflow 判断を発明させず、step-local scope / obligation / verification / evidence destination を示せる状態。

## 未確定事項

- Q-001:
  - 質問: root `.agents/skills/spec-dock-issue-planning/SKILL.md` は provider-side source と同一 issue で更新するか。
  - 回答:
    - provider-side source と dogfooding mirror を同時更新する。
  - 理由:
    - dogfooding repo では実際に読む root `.agents/skills/` との乖離を避けるため。
  - 影響範囲:
    - design / plan の allowed paths と verification。
