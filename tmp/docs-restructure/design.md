---
種別: 設計書（Docs）
ID: "docs-restructure-00001"
タイトル: "spec-dock 配布ドキュメント再構成（フラット化 + old/ 退避 + Guide/Workflow/Reference 分離）"
状態: "draft"
作成者: "<YOUR_NAME>"
最終更新: "2026-02-13"
依存: []
親: ["src/spec_dock/assets/spec_dock/docs"]
---

# docs-restructure-00001 spec-dock 配布ドキュメント再構成（フラット化 + old/ 退避 + Guide/Workflow/Reference 分離） — 設計

## 1. 背景（As-Is）

配布ドキュメント（`spec-dock init/update` が導入先へ配置する docs）は現状、以下のファイルで構成される:

```text
spec-dock/docs/
├── README.md                 # 入口
├── spec-dock-guide.md        # 共通原則 + 品質ゲート（全レイヤー）
├── workflow-tree.md          # ツリー運用
├── workflow-issue.md         # Issue 実装フロー
├── workflow-adr.md           # ADR 運用
├── github.md                 # gh 連携（new/active/import）
├── sync.md                   # sync の仕組み
└── spec-dock-guide-old.md    # 旧版（参考）
```

現状の主な問題:

1) **Guide が「総合情報」と「各レイヤーの品質ゲート」を同居**しており、読み手が「いま必要な情報」に辿り着きにくい  
   - `spec-dock-guide.md` が長大化し、Issue/Epic/Initiative の実作業中に参照しづらい
2) ワークフローが **Issue に偏っている**（Epic / Initiative の「単独の作業単位」としての運用が文章化されていない）  
   - `workflow-tree.md` はツリー運用の概観であり、Epic/Initiative を “単独で完結” させる運用の正になっていない
3) 入口（`README.md`）が “導線のハブ” として弱い  
   - 「Issueはこの workflow」「Epicはこの workflow」のような **役割ごとの参照先**が明確に提示されていない
4) 参照関係（リンク方針）が弱く、ドキュメント間の行き来が発生しやすい  
   - 「何をどこに書くべきか」が散らばり、運用でブレやすい

## 2. 目的（To-Be）

再構成後のドキュメント群は以下を満たす:

- Guide（総合）には **根本思想/SSOT/生成物/承認の意味/最短コマンド**などの“共通の正”だけを書く
- Workflows は **initiative / epic / issue / adr** をそれぞれ分離し、各レイヤーで “単独完結” できる正を置く
- 品質ゲート（チェックリスト）は **該当ワークフローに寄せる**
  - Initiative 品質ゲートは `workflow_initiative.md` に置く、等
- `README.md` は **入口（ハブ）**として、参照先を「目的別」に示す
- 既存ドキュメントは **`old/` に退避**し、そこから先は新ドキュメント群を“正”として運用する

## 3. 非目的（Non-Goals）

- テンプレート（`spec-dock/templates/**`）の全面改稿は本設計のスコープ外（必要なら別Issue化）
- 新しい概念（新レイヤー/新コマンド）の追加はしない（既存概念の説明整理が目的）
- クロスリポジトリ対応（URL の owner/repo 解釈など）は別ADR案件（現状は `gh` に委譲 + URL は番号抽出のみ）
- 旧ファイル名の互換 stub は作らない（旧版は `old/` に退避し、新版へ導線を張る）

## 4. 新しいドキュメント構成（To-Be）

### 4.1 ディレクトリ構成図（案）

配布 docs は **フラット（ネスト無し）**で並べ、ファイル名プレフィックスで用途を分ける。

- Workflow: `workflow_<type>.md`
- Reference: `reference_<topic>.md`
- 旧版退避: `old/`（旧ファイル名のまま格納）

`README.md` は入口、`guide.md` は総合（概念/生成物/ディレクトリ/導線）を担う。

```text
spec-dock/docs/
├── README.md                    # 入口（目的別リンク集）
├── guide.md                      # 総合（概念/生成物/ディレクトリ/導線）
├── workflow_initiative.md        # Initiative ワークフロー + 品質ゲート
├── workflow_epic.md              # Epic ワークフロー + 品質ゲート
├── workflow_issue.md             # Issue ワークフロー + 品質ゲート（TDD）
├── workflow_adr.md               # ADR ワークフロー + 品質ゲート
├── reference_github.md           # gh 連携（new/active/import）
├── reference_sync.md             # sync の仕組み
└── old/                          # 旧版ドキュメント退避（参考用）
    ├── README.md
    ├── spec-dock-guide.md
    ├── workflow-tree.md
    ├── workflow-issue.md
    ├── workflow-adr.md
    ├── github.md
    ├── sync.md
    ├── spec-dock-guide-old.md
    └── ...
```

### 4.2 既存ファイルとの互換（移行方針）

既存参照の多くは“ファイル名直指定”であり、互換 stub を維持すると **フラット化の意図（正の一本化）**が崩れる。

そのため以下の方針を採用する:

- 旧版は `spec-dock/docs/old/` に **一括退避**する（旧ファイル名のまま）
- 新版の正は `spec-dock/docs/*.md`（`workflow_*/reference_*`）とし、導線は `README.md`/`guide.md` に集約する
- コーディングエージェント参照（Codex skill）とテストは **新版へ更新**する

移行時の注意:
- 旧ファイルへ直接リンクしている外部記事/社内メモは、必要に応じて `old/` を参照するか、新版へ更新する

## 5. ファイル設計（何を書くか / 見出し案）

> 方針: “このファイルを読めば作業が進む” を第一にし、重複は Guide か Reference へ寄せる。

### 5.1 `spec-dock/docs/README.md`（入口 / ハブ）

目的:
- 最初に開く 1 枚
- 「今やりたいこと」から参照先へ最短で飛べる

章立て案:
1. まず読む（リンク）
2. 目的別ショートカット（表）
3. コマンド早見（new/import/active/sync/validate）
4. よくある失敗（最短の対処先リンク）

### 5.2 `spec-dock/docs/guide.md`（総合ガイド / 概念・生成物・ディレクトリ）

目的:
- “spec-dock とは何か/何が正か/何が生成物か/承認とは何か” を固定する
- ワークフローや品質ゲートの詳細は置かない（リンクで誘導）
- 人間/エージェントが「repo を開いた直後に迷わない」ための全体像を提供する（ディレクトリ構成図、生成物説明）

章立て案:
1. コア概念（SSOT / 生成物 / active / sync）
2. ディレクトリ構造（何をGit管理するか）
3. 99.9%理解ルール、推測禁止、DRY、承認の意味
4. 参照先一覧（Workflows / Reference）

### 5.3 `spec-dock/docs/workflow_initiative.md`

目的:
- Initiative を単独作業単位として運用できる
- Outcome/指標/投資範囲/ガードレールの固定ができる

章立て案:
1. 入口（いつ作るか/何のために）
2. 作業フロー（requirement → design → plan → report）
3. 品質ゲート（Initiative requirement/design/plan）
4. よくある失敗（例: KPIが曖昧、スコープが漏れる）

### 5.4 `spec-dock/docs/workflow_epic.md`

目的:
- Epic を “設計の背骨” として単独完結できる

章立て案:
1. 入口（いつ作るか/何のために）
2. 作業フロー（E-RQ/E-AC/NFR → 契約/移行/観測性 → Issue分割）
3. 品質ゲート（Epic requirement/design/plan）
4. よくある失敗（契約が無い、移行が無い、Issue分割が破綻）

### 5.5 `spec-dock/docs/workflow_issue.md`

目的:
- Issue を単独作業単位として TDD で完了できる

章立て案:
1. 入口（active/context-pack）
2. Planning（requirement/design/plan）
3. Implementation（TDD: Red→Green→Refactor）
4. Report（実行ログ）
5. 品質ゲート（Issue requirement/design/plan/report）

### 5.6 `spec-dock/docs/workflow_adr.md`

目的:
- 意思決定を ADR で分離し、議論→決定→accepted の運用を固定する

章立て案:
1. いつ ADR を起こすか
2. 叩き台 → 質問 → Decision → accepted の流れ
3. 品質ゲート（ADR）

### 5.7 `spec-dock/docs/reference_github.md`

目的:
- `gh` を使う挙動（new/active/import）を固定し、事故を減らす

含めるべき注意:
- URL target は番号抽出のみ（owner/repo 無視、別repo URL 事故）
- import は `gh issue view` のみ（読み取り）

### 5.8 `spec-dock/docs/reference_sync.md`

目的:
- `sync` の入力/出力/active更新/--force の意味を固定する

## 6. 参照更新（実装時に必要になる変更点）

以下はドキュメント再構成の実装フェーズで必須:
- `src/spec_dock/assets/codex_skills/spec-driven-tdd-workflow/SKILL.md` の参照先更新
- 旧ファイルの `old/` 退避
- テスト（`tests/test_cli.py`）の docs 構成アサート更新
- `spec-dock/docs/README.md` / `guide.md` の導線整理

## 7. 完了条件（Definition of Done）

- 入口 `README.md` から「目的別」に迷わず飛べる
- Guide が “総合” に徹し、品質ゲートは Workflows に移っている
- Initiative/Epic/Issue/ADR の各ワークフローが独立して読める
- 旧版は `old/` で参照できる（新版の正は 1 つ）
