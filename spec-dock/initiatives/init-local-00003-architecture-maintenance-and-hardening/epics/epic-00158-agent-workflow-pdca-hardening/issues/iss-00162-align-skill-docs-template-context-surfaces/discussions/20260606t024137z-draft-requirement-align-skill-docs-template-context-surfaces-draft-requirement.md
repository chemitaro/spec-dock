---
種別: draft-requirement
ID: "20260606t024137z-draft-requirement"
タイトル: "Align Skill Docs Template Context Surfaces Draft Requirement"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-06"
親: ["iss-00162", "epic-00158", "init-local-00003"]
authority: "proposed"
source_paths:
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - spec-dock/active/epic/discussions/20260605t080509z-adr-skill-docs-template-context-surface-ownership.md
  - spec-dock/active/epic/discussions/20260605t080509z-02-adr-first-wave-issue-decomposition.md
intended_targets:
  - spec-dock/active/epic/issues/iss-00162-align-skill-docs-template-context-surfaces/requirement.md
adoption_status: unreviewed
reflected_to: []
---

# iss-00162 Align Skill Docs Template Context Surfaces — 要件定義ドラフト

## 目的

Provider-side の skills / docs / templates を横断 inventory し、`skill = operational workflow spine`、`docs = meaning/detail/hard cases`、`templates = scaffold/evidence slots/examples` という責務分担が、どの surface を読んでも矛盾なく見える状態にする。

この issue は first-wave cleanup の中核であり、後続の clarification / hub / workflow docs / templates issue が同じ境界で進められるようにする。

## 背景・現状

- 現状の挙動:
  - 一部 skill は docs source-of-truth を強く示し、mandatory workflow spine が docs 側に埋もれている。
  - `spec-dock-issue-planning` は先行 specimen として workflow spine を出し始めているが、全体の skills / docs / templates にはまだ同じ境界が行き渡っていない。
- 現状の課題:
  - Agent が読む surface によって、mandatory workflow が skill-owned なのか docs-owned なのかが揺れる。
  - Templates が scaffold ではなく compliance authority のように読まれるリスクが残る。
  - 後続 issue が局所修正に流れると、Epic 全体としての住み分けが統合されない。
- 観測点:
  - Provider skills: `src/spec_dock/assets/install_root/.agents/skills/`
  - Provider docs: `src/spec_dock/assets/spec_dock/docs/`
  - Provider templates: `src/spec_dock/assets/spec_dock/templates/`
  - Dogfooding mirror: `.agents/`, `spec-dock/docs/`, `spec-dock/templates/`
- 情報源:
  - Epic requirement/design/plan
  - ADR `20260605t080509z-adr`
  - ADR `20260605t080509z-02-adr`

## 対象ユーザー / 利用シナリオ

- 主な利用者:
  - SpecDock を使って planning / clarification / execution を行う coding agent と maintainer。
- 代表シナリオ:
  - Agent が任意の related skill/docs/templates を読んだとき、どの surface が workflow / detail / scaffold を所有するかを同じように判断できる。

## スコープ

- 必須:
  - Provider-side skills / docs / templates の inventory を作る。
  - Surface ごとに ownership claim と contradiction を整理する。
  - Priority surface の古い source-of-truth wording / hidden workflow wording / template authority wording を洗い出す。
  - 後続 issue に渡す cleanup boundary と trace matrix を作る。
  - Dogfooding mirror は verification target として確認する。
- 禁止:
  - Runtime gate / CLI enforcement / automated regression harness を実装しない。
  - すべての docs を skill にコピーしない。
  - Templates を compliance authority にしない。
  - `spec-dock-clarification` 固有の full rewrite をこの issue に吸収しない。
- 対象外:
  - Issue 内実装 step の詳細設計。
  - Runtime validation schema。
  - GitHub workflow / CI harness。

## 境界

- 常に行う:
  - Provider source を正本として確認する。
  - `iss-00159` の specimen wording を参照し、横断 vocabulary を揃える。
  - Contradiction は skill/docs/templates のどの責務境界に反するかで分類する。
- 判断が必要:
  - Inventory だけで終える surface と、この issue で first cleanup まで行う surface の線引き。
  - Scope が広すぎる場合の skill family / artifact family split。
- 行わない:
  - Clarification exception の workflow をここで全部書き換えない。
  - Hub routing の詳細をここで確定しない。
  - Deferred guard work を前倒ししない。

## 非交渉制約

- `src/spec_dock/assets/install_root/.agents/skills/` が installed skill source of truth。
- `src/spec_dock/assets/spec_dock/docs/` と `src/spec_dock/assets/spec_dock/templates/` が shipped docs/templates source of truth。
- Canonical adoption と phase gate は main orchestrator-owned。

## 前提

- `iss-00159` は T1 specimen として先行する。
- この issue は T2 inventory / consistency lane であり、後続 T2/T3/T4 issue の土台になる。

## 受け入れ条件

- AC-001:
  - アクター: maintainer / reviewer
  - 前提: Provider-side skills / docs / templates を確認する
  - 操作: ownership claim と contradiction を inventory する
  - 期待結果: surface ごとの `skill-owned spine`, `docs-owned detail`, `template-owned scaffold` への分類と矛盾が一覧化されている
  - 観測点: discussion / report evidence
- AC-002:
  - アクター: maintainer
  - 前提: priority contradiction がある
  - 操作: この issue で修正するか後続 issue に渡すか判断する
  - 期待結果: 後続 issue へ渡すものは trace と理由を持ち、この issue で直すものは provider source に反映される
  - 観測点: diff, report
- AC-003:
  - アクター: agent
  - 前提: cleaned priority surface を読む
  - 操作: workflow / detail / scaffold の所有者を判断する
  - 期待結果: Epic ADR と矛盾しない境界を読み取れる
  - 観測点: manual first-read inspection
- AC-004:
  - アクター: maintainer
  - 前提: shipped asset に変更がある
  - 操作: provider source と dogfooding mirror を確認する
  - 期待結果: provider source が authority、mirror が verification target として記録される
  - 観測点: `validate`, `sync`, targeted inspection

## 例外・エッジケース

- EC-001:
  - 条件: inventory の結果、scope が大きすぎる
  - 期待: skill family / docs / templates family へ split し、Epic plan と report に残す
  - 観測点: report follow-up
- EC-002:
  - 条件: docs に lifecycle policy と mandatory first action が混在している
  - 期待: policy detail は docs に残し、mandatory first action は対応 skill の first-read surface へ渡す
  - 観測点: inventory matrix

## 用語（ドメイン語彙）

- TERM-001:
  - Context surface: agent が作業前または作業中に読む skill/docs/templates/generated view。
- TERM-002:
  - Ownership claim: surface が何の source of truth / authority であるかを示す文言。
- TERM-003:
  - Contradiction: Epic ADR の責務分担と矛盾する wording / structure / example。

## 未確定事項

- Blocking question:
  - なし。
- Non-blocking default:
  - まず一つの inventory / first-cleanup issue として進め、review scope が広すぎる場合だけ split する。
