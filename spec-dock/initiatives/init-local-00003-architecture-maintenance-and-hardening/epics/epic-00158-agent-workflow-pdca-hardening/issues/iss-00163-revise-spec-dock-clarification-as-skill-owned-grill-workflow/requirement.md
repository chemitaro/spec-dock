---
種別: 要件定義書（Issue）
ID: "iss-00163"
タイトル: "Revise Spec Dock Clarification As Skill Owned Grill Workflow"
関連GitHub: ["#163"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-06"
親: ["epic-00158", "init-local-00003"]
---

# iss-00163 Revise Spec Dock Clarification As Skill Owned Grill Workflow — 要件定義

## 目的

`spec-dock-clarification` を、既存 SpecDock artifact 作成を支援する source-grounded grill workflow として、skill first-read surface だけで実行可能にする。

この issue では、clarification workflow 自体を `SKILL.md` が所有する。詳細な意味、artifact lifecycle、採用証跡の考え方は既存 docs / templates へ接続するが、agent が最初に守る interaction loop は doc に隠さない。

## 背景・現状

- 現状の挙動:
  - `spec-dock-clarification/SKILL.md` は `workflow_clarification.md` を source of truth として参照する薄い skill になっている。
  - `workflow_clarification.md` は first-class workflow doc として、source-grounded read、一問一答、artifact selection、adoption rules まで持っている。
- 現状の課題:
  - Agent が workflow doc を読まない場合、source を読む、provisional understanding を作る、一つの pressure-test question を選ぶ、artifact に捕捉する、という loop を知らない。
  - Clarification が generic question answering に流れ、SpecDock artifact と `report.md` adoption に接続しにくい。
  - `interview` / `research` / `disc` templates は clarification を支える scaffold だが、source-grounded grill loop の minimum slots が弱い。
- 情報源:
  - Epic requirement / design / plan。
  - Epic ADR `20260605t080509z-01-adr-clarification-skill-owned-workflow.md`。
  - S01 inventory discussion `20260606t040013z-disc-context-surface-inventory.md`。
  - Draft requirement discussion `20260606t024142z-draft-requirement-revise-spec-dock-clarification-draft-requirement.md`。
  - Current provider files:
    - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md`
    - `src/spec_dock/assets/spec_dock/docs/workflow_clarification.md`
    - `src/spec_dock/assets/spec_dock/templates/discussions/interview.md`
    - `src/spec_dock/assets/spec_dock/templates/discussions/research.md`
    - `src/spec_dock/assets/spec_dock/templates/discussions/disc.md`

## 対象ユーザー / 利用シナリオ

- 主な利用者:
  - Requirement / design / plan authoring 前に曖昧さを潰す agent と maintainer。
- 代表シナリオ:
  - Agent が clarification skill を読み、local sources を確認してから一つの高価値な pressure-test question を選び、重要判断は unanswered `interview` artifact に捕捉する。
  - User が analysis-only clarification を求めた場合、agent は canonical docs 作成を強制せず、sources read / provisional understanding / unresolved questions / recommended next action を返す。

## スコープ

- 必須:
  - Provider `spec-dock-clarification/SKILL.md` に source-grounded grill loop を置く。
  - Dogfooding mirror `.agents/skills/spec-dock-clarification/SKILL.md` を provider と同じ内容に保つ。
  - `workflow_clarification.md` は bridge/reference として扱い、mandatory runbook authority と読ませない。
  - Provider / mirror `workflow_clarification.md` の wording を skill-owned workflow に整合させる。
  - `interview` / `research` / `disc` templates について、clarification-specific minimum slots を定義し、source grounding、question candidate、answer capture、adoption reflection を支える scaffold に寄せる。
  - Specialist agents は質問候補を orchestrator に返し、人間へ直接質問しない境界を明示する。
  - Analysis-only / draft-only / canonical authoring handoff の違いを skill 上で判断できるようにする。
- 禁止:
  - Matt Pocock 氏の original skill text を exact copy しない。
  - Generic coaching skill にしない。
  - Runtime gate / automated harness をこの issue で作らない。
  - `workflow_clarification.md` を link cleanup なしに削除しない。
  - Hub route table / broader leaf routing を変更しない。これは `iss-00164` が所有する。
- 対象外:
  - Issue planning / execution workflow の全面再設計。
  - ADR 作成条件そのものの大幅変更。
  - Templates 全体の global consistency / wording normalization。これは `iss-00166` が、upstream boundary settled 後に所有する。

## 境界

- 常に行う:
  - Read sources before asking。
  - Local context で答えられることをユーザーに聞かない。
  - Provisional understanding を作ってから、次の一つの pressure-test question を選ぶ。
  - 重要判断は unanswered `interview` を作ってから一問だけ聞く。
  - 回答後、同じ artifact を complete し、affected canonical docs / report adoption を明示する。
- 判断が必要:
  - `workflow_clarification.md` は first wave では bridge/reference とし、full retirement は link inventory 後に判断する。
  - Template に含める wording は clarification-specific minimum slots に留め、global style は `iss-00166` へ渡す。
- 行わない:
  - Human に複数質問 questionnaire を投げない。
  - Specialist agent が human に直接質問しない。
  - External analysis を ledger なしで canonical にしない。

## 非交渉制約

- `spec-dock-clarification` はこの issue では skill-owned workflow。
- `workflow_clarification.md` は first wave では bridge/reference が既定。
- Templates は scaffold / example であり compliance authority ではない。
- Provider source を正本、dogfooding mirror を verification target とする。

## 前提

- `iss-00159` の issue planning skill が first-read skill spine の specimen として存在する。
- `iss-00162` の inventory が clarification skill / workflow doc / discussion templates を `iss-00163` の handoff row として分類している。

## 受け入れ条件

- AC-001:
  - アクター: clarification を行う agent
  - 前提: `spec-dock-clarification/SKILL.md` を読む
  - 操作: 次に取るべき clarification action を判断する
  - 期待結果: read sources -> provisional understanding -> one pressure-test question -> artifact capture -> iterate/handoff の loop を理解できる
  - 観測点: skill first-read inspection
- AC-002:
  - アクター: maintainer
  - 前提: `workflow_clarification.md` を確認する
  - 操作: authority boundary を確認する
  - 期待結果: doc は bridge/reference であり、mandatory runbook authority と読めない
  - 観測点: docs diff
- AC-003:
  - アクター: agent
  - 前提: important human decision が必要
  - 操作: `interview` artifact を作成して質問する
  - 期待結果: unanswered before asking、answer capture、reflection/adoption needs が scaffold に沿って残る
  - 観測点: template inspection
- AC-004:
  - アクター: reviewer
  - 前提: `research` / `disc` templates を確認する
  - 操作: clarification workflow の補助 artifact として妥当か見る
  - 期待結果: research は facts / uncertainty / question candidates、disc は synthesis / ADR triage を担う
  - 観測点: templates diff
- AC-005:
  - アクター: maintainer
  - 前提: provider source を変更した
  - 操作: dogfooding mirror と generated projection を確認する
  - 期待結果: provider source と mirror の関係、`sync` / `validate` / parity check が report に記録される
  - 観測点: `cmp`, targeted parity unittest, `sync`, `validate`

## 例外・エッジケース

- EC-001:
  - 条件: Existing docs が `workflow_clarification.md` に link している
  - 期待: immediate delete ではなく bridge/reference で互換性を維持する
  - 観測点: link inventory / docs diff
- EC-002:
  - 条件: ユーザーが analysis-only clarification を求めている
  - 期待: canonical docs 作成を強制せず、sources read / unresolved questions / recommended next question を返す
  - 観測点: skill behavior text
- EC-003:
  - 条件: User intent clarification が本当に blocking になった
  - 期待: deep-consultant や専門 agent を user proxy にせず、作業をブロックしてユーザーへ直接一問で聞く
  - 観測点: skill behavior text / report evidence

## 用語

- Source-grounded grill loop:
  - local sources に根ざした仮説を作り、一つの重要質問で境界を pressure-test する interaction pattern。
- Pressure-test question:
  - scope / assumption / edge case / adoption impact を一つだけ検証する質問。
- Bridge/reference doc:
  - skill-owned workflow を隠さず、artifact semantics や link navigation を支える doc。

## 未確定事項

- Blocking question:
  - なし。
- Non-blocking default:
  - `workflow_clarification.md` は first wave では bridge/reference とする。
  - `iss-00163` は clarification-specific minimum template slots を所有し、`iss-00166` は upstream boundary settled 後に global template consistency / examples / cross-template wording を所有する。
