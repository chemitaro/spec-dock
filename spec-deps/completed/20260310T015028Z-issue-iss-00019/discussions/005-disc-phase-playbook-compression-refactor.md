---
種別: disc
ID: "005-disc-phase-playbook-compression-refactor"
タイトル: "phase playbook を LLM 向けに圧縮するリファクタリング案"
状態: "proposed"
作成者: "Codex"
最終更新: "2026-03-10"
親: ["iss-00019"]
関連: ["002-disc-phase-playbook-authoring-workflow-revision", "003-disc-phase-playbook-concrete-edit-blueprint", "004-disc-phase-playbook-wording-replacement-draft"]
---

# 005-disc phase playbook を LLM 向けに圧縮するリファクタリング案

## 議題 (必須)
- `phase_requirement.md`, `phase_design.md`, `phase_plan.md` を、意味と判断材料を維持したまま LLM / coding agents 向けに圧縮する。
- あわせて `guide.md`, `README.md`, `workflow_*.md` の冗長な再説明を減らし、参照導線だけを残す。

## 背景 (必須)
- 現行 docs は全体 workflow を明示できるようになったが、そのぶん文量が増えた。
- この docs の主読者は日常的には人間よりも LLM / coding agents であり、コンテキスト効率が重要である。
- 問題は情報不足ではなく、同じ概念の言い換え、同じ型の箇条書き、同じ導線の再説明が複数箇所に散っていることにある。

## 現状分析 (必須)
- 現行行数:
  - `phase_requirement.md`: 218 行
  - `phase_design.md`: 210 行
  - `phase_plan.md`: 206 行
  - `guide.md`: 179 行
  - `README.md`: 124 行
  - `workflow_initiative.md`: 116 行
  - `workflow_epic.md`: 118 行
  - `workflow_issue.md`: 156 行
- 冗長の主因:
  - 3つの `phase_*.md` の冒頭骨格がほぼ同型
  - `標準順`、`subagent`、`迷ったとき` が 3 文書でほぼ同内容
  - `guide.md` / `README.md` / `workflow_*.md` に導線説明が繰り返し出る
  - discussion docs の作成コマンド、命名補足、`validate/sync` が複数箇所に再掲される

## 選択肢 (必須)

### Option A: 文量はそのままに wording だけ少し短くする
- Pros:
  - 変更差分が小さい
  - リスクが低い
- Cons:
  - 圧縮効果が弱い
  - 構造的な重複が残る

### Option B: 章構成は維持しつつ、contract / checklist / reference へ畳み込む
- Pros:
  - 情報量を維持しつつ文量を大きく減らせる
  - phase docs の読み方が速くなる
  - 既存の layering を維持できる
- Cons:
  - 節の再編が必要
  - wording の再設計が要る

### Option C: さらに共通 playbook を別ファイル化し、phase docs は薄くする
- Pros:
  - 3 文書の共通部分を大きく削れる
  - 将来的な保守は楽になる
- Cons:
  - 新しい正本が増える
  - 読み始めの導線が増え、かえって迷いやすい

## 推奨案 (必須)
- 推奨は Option B。
- 理由:
  - 新しい正本を増やさずに済む
  - 今の構造のまま、重複だけを整理できる
  - LLM が最初に読むべき情報を `phase contract` と `checklist` に圧縮できる

## 圧縮の設計方針 (必須)
- 方針 1:
  - 冒頭は `phase contract` に統合する
  - 含めるのは `責務 / 前提入力 / 固定すること / 出力 / 非ゴール / 正本参照`
- 方針 2:
  - `標準順` は 8 行の詳細列挙ではなく、1 行または短い 5〜6 項目へ圧縮する
- 方針 3:
  - `開始前確認` と `template 参照先` は `entry checklist` としてまとめる
- 方針 4:
  - `ヒアリング条件`、`discussion/docs 化`、`ADR 条件` は `論点の逃がし先ルール` に寄せる
- 方針 5:
  - `exit criteria` と `次 phase へ進める条件` は `review / handoff gate` に寄せる
- 方針 6:
  - `subagent` と `迷ったとき` は 1〜3 行の短い規則へ縮める
- 方針 7:
  - `workflow_*.md` はその scope 固有でない文を持ち込まない

## 具体的な圧縮ルール (必須)
- 各節の導入文は 1 文まで
- 同じ意味の語は固定する
  - 例: `docs 化`, `discussion`, `handoff`, `phase contract`
- 既出の共通ルールは再説明せず参照に寄せる
- `補足:` の多用をやめ、例外だけ残す
- checklist は checklist のまま、説明文に戻さない
- コマンド例は代表 1 例だけにし、派生は reference へ寄せる
- phase docs では `共通 7割 + phase 固有 3割` の比率を目指す

## phase docs の再編案 (必須)

### requirement
- 残すべき核:
  - WHAT / WHY / scope / success
  - As-Is の一次情報と観測点
  - MUST / MUST NOT / OUT OF SCOPE
  - TBD の仕分け
- 圧縮案:
  - 冒頭の `位置づけ / 前提 / 固定すること / 完了条件 / 目的 / 出力 / 非ゴール / 注意` を `phase contract` に統合
  - `ユーザーヒアリング` と `discussion/docs 化` を `論点の逃がし先` に統合
  - `exit criteria` と `次 phase 条件` を `review / handoff gate` に統合

### design
- 残すべき核:
  - HOW / guardrails
  - 既存パターン優先
  - 境界 / 契約 / SoR / 移行 / 観測性 / テスト戦略
  - 採用理由と非採用理由の所在
- 圧縮案:
  - 冒頭の `標準順` と `注意` を contract へ畳む
  - `4.1` と `4.2` を `design input / design rule` に寄せる
  - `ヒアリング / discussion / ADR` を `設計論点のエスカレーション` に統合
  - `exit criteria` と `次 phase 条件` を `review / handoff gate` に統合

### plan
- 残すべき核:
  - 分解単位 / 順序 / 停止点 / 完了判定 / 品質ゲート
  - requirement / design の再議論をしないこと
  - 依存とブロッカーの可視化
  - Issue では `1 step = 1 観測可能な振る舞い`
- 圧縮案:
  - 冒頭は `plan contract`
  - `4.1` と `4.2` を `planning checklist` に統合
  - `ヒアリング / discussion / ADR` を `順序決定のエスカレーション` に統合
  - `Issue 固有実行ルール` は `workflow_issue.md` 参照を強める

## 周辺 docs の圧縮案 (必須)
- `guide.md`:
  - 入口と全体像に徹し、繰り返しのコマンドや補足を削る
- `README.md`:
  - docs 入口とショートカットに徹し、guide と重なる説明を削る
- `workflow_initiative.md` / `workflow_epic.md`:
  - 共通の注意事項は削り、固有の再利用判定 / 作成 / 品質ゲートだけ残す
- `workflow_issue.md`:
  - 前半の共通説明は削り、TDD / step review / docs impact / final gate に集中させる

## 圧縮後も絶対に落とさない要素 (必須)
- 各 phase が全体 workflow のどこか
- その phase で固定するもの
- 共通ルールと scope 固有ルールの正本分離
- ヒアリング前に docs に残す前提
- reviewer 判定と handoff の条件

## 次アクション (必須)
- この案に沿って `phase_*.md` を contract/checklist 中心に再編する
- `guide.md`, `README.md`, `workflow_*.md` の冗長を削る
- その後 `spec_reviewer` で layering と情報欠落がないかを確認する
