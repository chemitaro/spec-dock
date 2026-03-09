---
種別: research
ID: "research-00003"
タイトル: "Anthropic 公式情報に基づく skills / subagents ベストプラクティス調査"
状態: "draft"
作成者: "codex"
最終更新: "2026-03-09"
関連: ["iss-00016"]
---

# 調査目的

spec-dock の skill 情報設計を考えるにあたり、Anthropic 公式情報に基づいて以下を整理する。

- skill は何のために作るものか
- どの粒度が望ましいか
- `SKILL.md` / references / assets / scripts の責務分離
- skill と subagents の境界
- 今回の「scope × phase まで skill を増やすべきか」という論点への示唆

## 一次情報

- Claude Code docs: skills  
  https://code.claude.com/docs/en/skills
- Claude docs: skills overview  
  https://claude.com/docs/skills/overview
- Anthropic platform docs: agent skills overview  
  https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- Claude Code docs: sub-agents  
  https://code.claude.com/docs/en/sub-agents
- Claude Code docs: output styles  
  https://code.claude.com/docs/en/output-styles
- Anthropic 公式 guide PDF: The Complete Guide to Building Skill for Claude  
  https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf

## 事実整理

### 1. skill は task-specific な再利用手順である

- skills は `SKILL.md` を中心にした再利用可能な workflow / knowledge package である
- 常時読み込む巨大 instruction ではなく、「必要になった時だけロードされる task-specific guidance」という位置づけで説明されている
- したがって、skill は「いつ使うか」が明確である必要がある

## 2. skills は progressive disclosure 前提で設計する

- 起動時にまず参照されるのは主に `name` と `description`
- 実際にマッチした時に `SKILL.md`
- さらに必要なら `references/`, `assets/`, `scripts/` を読む
- つまり、`SKILL.md` 自体にすべてを書き込むのは推奨されない

### 3. 広すぎる skill は避けるべき

- 公式 guide は、broad すぎる skill は誤発火しやすいと示している
- description は「何をするか」だけでなく「いつ使うか」を含める必要がある
- 必要なら negative trigger（使わない条件）も書くべきとされている

### 4. description は trigger quality を左右する

- description は自然言語で、ユーザーや agent が実際に言いそうな語彙を含めるのが重要
- 抽象的すぎる説明、内部実装寄りの説明、呼び出し条件が曖昧な説明は bad pattern

### 5. 詳細は `references/` や `assets/` に逃がす

- `SKILL.md` は薄く保ち、重い説明や詳細仕様は `references/`
- 使い回すテンプレートやサンプルは `assets/`
- 確定的な処理は `scripts/`
- という分離が推奨されている

### 6. `SKILL.md` は小さく保つ

- 公式 guide では `SKILL.md` を 5,000 words 未満に保つ方針が示されている
- これは単なる可読性ではなく、発火後に読むべき内容を最小にして model の効率を維持するためでもある

### 7. skill はテストと反復が前提である

- trigger test（発火/非発火）
- functional test（出力の妥当性）
- 必要に応じて比較テスト
- まず 1 つの難しいタスクで有効性を確認し、その後横展開する

### 8. subagents は skill と別物である

- skills は再利用可能な workflow / prompt package
- subagents は隔離された context / 権限 / ツールで自己完結タスクを処理する実行主体
- 公式には、再利用 guidance には skills、並列処理や隔離された委譲には subagents、という役割分担が示されている

### 9. output styles とも混同しない

- output styles は「どのように話すか」
- skills は「どの仕事にどの再利用手順を使うか」
- subagents は「誰に処理を委譲するか」

## 今回の論点への示唆

### A. `scope × phase` をそのまま top-level skill に増やすのは慎重であるべき

Anthropic の公式 guidance と照らすと、次のリスクが高い。

- trigger 条件が近すぎる skill が大量に並ぶ
- description が似通い、誤発火・未発火が増える
- `SKILL.md` に interview / template / review gate を書き込みすぎて肥大化する
- docs / templates / skills の drift が増える

### B. 再利用したいものは skill ではなく playbook かもしれない

今回ユーザーが本当に再利用したいのは、

- 要件定義書の作り方
- 設計書の作り方
- 実装計画書の作り方

であり、これは「独立した入口」よりも「共通の作法」に近い。

Anthropic 公式の構造に沿うなら、これは skill を増やすより、

- skill は concise router
- docs / playbook は detailed guidance
- template は execution form

と分けた方が自然である。

### C. skill を増やすなら、明確な job boundary が必要

公式情報から導ける追加基準は次の通り。

1. その skill には独立した trigger がある
2. 固有の入力と出力がある
3. 他 skill と混同しにくい
4. `SKILL.md` を薄く保ったまま成立する
5. 追加することで trigger quality または失敗率が実際に改善する

## 暫定結論

Anthropic 公式 guidance と整合する構成は、

- **top-level skill は job boundary ベースで少数に保つ**
- **細かい作法や interview / review gate / UML guidance は docs / playbook / template に置く**
- **skills は concise な routing と reminder に徹する**
- **重い分析や並列調査は subagents に委譲する**

である。

この観点では、spec-dock が次に強化すべきは `scope × phase` の top-level skill 量産ではなく、**shared phase playbook の整備**である可能性が高い。
