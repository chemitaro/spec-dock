---
種別: draft-requirement
ID: "20260606t024142z-draft-requirement"
タイトル: "Revise Spec Dock Clarification Draft Requirement"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-06"
親: ["iss-00163", "epic-00158", "init-local-00003"]
authority: "proposed"
source_paths:
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - spec-dock/active/epic/discussions/20260605t080509z-01-adr-clarification-skill-owned-workflow.md
  - spec-dock/active/epic/discussions/20260605t053300z-research-chatgpt-clarification-grill-alignment-report.md
intended_targets:
  - spec-dock/active/epic/issues/iss-00163-revise-spec-dock-clarification-as-skill-owned-grill-workflow/requirement.md
adoption_status: unreviewed
reflected_to: []
---

# iss-00163 Revise Spec Dock Clarification As Skill Owned Grill Workflow — 要件定義ドラフト

## 目的

`spec-dock-clarification` を、SpecDock の既存 artifact 作成を支援する source-grounded grill workflow として、skill first-read surface だけで実行可能にする。

この issue は `spec-dock-clarification` 固有の例外 lane であり、一般的な skill/docs/templates boundary を踏まえつつ、clarification workflow 自体は `SKILL.md` が所有する。

## 背景・現状

- 現状の挙動:
  - `spec-dock-clarification/SKILL.md` は `workflow_clarification.md` を source of truth として参照する薄い skill になっている。
  - `workflow_clarification.md` は full workflow doc として振る舞っている。
- 現状の課題:
  - Agent が workflow doc を読まない場合、source を読む、provisional understanding を作る、一つの essential question を選ぶ、artifact に捕捉する、という loop を知らない。
  - Clarification が generic question answering に流れ、SpecDock artifact と report adoption に接続しにくい。
  - `interview` / `research` / `disc` templates が source-grounded grill loop の良いお手本として十分に揃っていない。
- 観測点:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_clarification.md`
  - `src/spec_dock/assets/spec_dock/templates/discussions/interview.md`
  - `src/spec_dock/assets/spec_dock/templates/discussions/research.md`
  - `src/spec_dock/assets/spec_dock/templates/discussions/disc.md`
- 情報源:
  - ADR `20260605t080509z-01-adr`
  - ChatGPT `じっくり思考 Pro` clarification report
  - Epic design / plan

## 対象ユーザー / 利用シナリオ

- 主な利用者:
  - Requirement / design / plan authoring 前に曖昧さを潰す agent と maintainer。
- 代表シナリオ:
  - Agent が clarification skill を読み、local sources を確認してから一つの高価値な pressure-test question を選び、重要判断は `interview` artifact に捕捉する。

## スコープ

- 必須:
  - `spec-dock-clarification/SKILL.md` に source-grounded grill loop を置く。
  - `workflow_clarification.md` は bridge/reference として扱い、mandatory runbook authority にしない。
  - `interview` / `research` / `disc` templates について、clarification-specific minimum slots を定義し、source grounding、question candidate、answer capture、adoption reflection を支える scaffold に寄せる。
  - Specialist agents は質問候補を orchestrator に返し、人間へ直接質問しない境界を明示する。
  - Analysis-only / draft-only / canonical authoring handoff の違いを skill 上で判断できるようにする。
- 禁止:
  - Matt Pocock 氏の original skill text を exact copy しない。
  - Generic coaching skill にしない。
  - Runtime gate / automated harness をこの issue で作らない。
  - `workflow_clarification.md` を link cleanup なしに削除しない。
- 対象外:
  - Issue planning / execution workflow の全面再設計。
  - ADR 作成条件そのものの大幅変更。
  - Hub routing の更新。
  - Templates 全体の global consistency / wording normalization。これは `iss-00166` が、upstream boundary settled 後に所有する。

## 境界

- 常に行う:
  - Read sources before asking。
  - Local context で答えられることをユーザーに聞かない。
  - 重要判断は unanswered `interview` を作ってから一問だけ聞く。
  - 回答後、同じ artifact を complete し、affected canonical docs / report adoption を明示する。
- 判断が必要:
  - `workflow_clarification.md` を bridge に留めるか、link cleanup と合わせて retirement へ進むか。
  - Template にどこまで example wording を含めるか。
- 行わない:
  - Human に複数質問 questionnaire を投げない。
  - Specialist agent が human に直接質問しない。
  - External analysis を ledger なしで canonical にしない。

## 非交渉制約

- `spec-dock-clarification` はこの issue では skill-owned workflow。
- `workflow_clarification.md` は first wave では bridge/reference が既定。
- Templates は scaffold / example であり compliance authority ではない。

## 前提

- `Align Skill Docs Template Context Surfaces` で ownership inventory が始まっている、またはその結果を参照できる。
- `iss-00159` の specimen で first-read skill spine の語彙が得られている。

## 受け入れ条件

- AC-001:
  - アクター: clarification を行う agent
  - 前提: `spec-dock-clarification/SKILL.md` を読む
  - 操作: 次に取るべき clarification action を判断する
  - 期待結果: read sources -> provisional understanding -> one pressure-test question -> artifact capture -> iterate/handoff の loop を理解できる
  - 観測点: skill first-read smoke
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
  - 観測点: template / manual smoke
- AC-004:
  - アクター: reviewer
  - 前提: `research` / `disc` templates を確認する
  - 操作: clarification workflow の補助 artifact として妥当か見る
  - 期待結果: research は facts / uncertainty / candidates、disc は synthesis / ADR triage を担う
  - 観測点: templates diff
- AC-005:
  - アクター: maintainer
  - 前提: provider source を変更した
  - 操作: dogfooding mirror を確認する
  - 期待結果: provider source と mirror の関係が report に記録される
  - 観測点: `validate`, `sync`, targeted inspection

## 例外・エッジケース

- EC-001:
  - 条件: Existing docs が `workflow_clarification.md` に link している
  - 期待: immediate delete ではなく bridge/reference で互換性を維持する
  - 観測点: link inventory
- EC-002:
  - 条件: ユーザーが analysis-only clarification を求めている
  - 期待: canonical docs 作成を強制せず、sources read / unresolved questions / recommended next question を返す
  - 観測点: skill behavior text

## 用語（ドメイン語彙）

- TERM-001:
  - Source-grounded grill loop: local sources に根ざした仮説を作り、一つの重要質問で境界を圧力テストする interaction pattern。
- TERM-002:
  - Pressure-test question: scope / assumption / edge case / adoption impact を一つだけ検証する質問。
- TERM-003:
  - Bridge/reference doc: skill-owned workflow を隠さず、artifact semantics や link navigation を支える doc。

## 未確定事項

- Blocking question:
  - なし。
- Non-blocking default:
  - `workflow_clarification.md` は first wave では bridge/reference とし、full retirement は link inventory 後に判断する。
  - `iss-00163` は clarification-specific minimum template slots を所有し、`iss-00166` は upstream boundary settled 後に global template consistency / examples / cross-template wording を所有する。
