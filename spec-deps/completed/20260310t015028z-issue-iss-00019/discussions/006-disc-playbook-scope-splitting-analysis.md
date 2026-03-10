---
種別: disc
ID: "006-disc-playbook-scope-splitting-analysis"
タイトル: "shared phase playbook を scope 別に分割すべきかの分析"
状態: "proposed"
作成者: "Codex"
最終更新: "2026-03-10"
親: ["iss-00019"]
関連: ["005-disc-phase-playbook-compression-refactor"]
---

# 006-disc shared phase playbook を scope 別に分割すべきかの分析

## 議題 (必須)
- `phase_requirement.md`, `phase_design.md`, `phase_plan.md` を、initiative / epic / issue ごとに分割すべきかを判断する。
- あるいは、shared phase playbook を維持しつつ、scope ごとの差分を別レイヤへ逃がすべきかを整理する。

## 背景 (必須)
- 現状は `workflow_<scope>.md` が scope 固有、`phase_*.md` が shared、`templates/<scope>/*` が出力の型、という構造である。
- しかし template を見ると、initiative / epic / issue では関心事が大きく異なる。
  - Initiative requirement は `成功指標`, `ステークホルダー`, `Definition of Ready/Done`
  - Epic requirement は `E2E 要求`, `受け入れ条件`, `非機能`
  - Issue requirement は `観測点`, `AC/EC`, `例外・エッジケース`, `用語`
- そのため、「差分を template だけで吸収してよいのか」「playbook 自体も scope 別に分けるべきではないか」という疑問がある。

## 現状分析（As-Is） (必須)

### docs / skills / templates の接続
- skills:
  - hub skill は scope を判定して leaf skill へ route する
  - leaf skills は `workflow_<scope>.md` と shared `phase_*.md` を参照する
- docs:
  - `workflow_initiative.md`, `workflow_epic.md`, `workflow_issue.md` が scope 固有の governance を持つ
  - `phase_requirement.md`, `phase_design.md`, `phase_plan.md` が共通の書き方 contract を持つ
- templates:
  - `templates/initiative/*`, `templates/epic/*`, `templates/issue/*` が scope 固有の項目差分を吸収する

### 現状の利点
- `skills -> docs -> templates` の責務分離が明快
- shared playbook により、調査 → docs 化 → ヒアリング → reviewer loop → handoff の共通原則を 3 文書で一貫して持てる
- template は生成フォームなので、scope ごとの出力差分を持つ場所として自然

### 現状の欠点
- scope 差分が大きい箇所まで shared playbook に書き始めると、`phase_*.md` が長くなりやすい
- issue は TDD / review loop / docs impact など温度が違うため、initiative / epic と同じ密度で shared に載せると重くなる
- agents が template を見ないと scope 差分を十分に掴めない場面があると、docs 側のルール正本としては弱い

## 第三者視点の要約 (必須)

### 視点A: 圧縮レビュー
- 3つの `phase_*.md` は 70〜80% 共通化可能
- 冗長の主因は、shared playbook に同じ骨格を重ねていること
- 完全分割より、shared 部分を contract 化して軽くするほうが効率がよい

### 視点B: phase 固有差分の分析
- requirement / design / plan の phase 内標準順は共通化できる
- ただし、phase 固有で残すべき核は明確に違う
  - requirement: WHAT / WHY / scope / success
  - design: HOW / guardrails / 契約 / 境界 / 移行 / 観測性
  - plan: 分解 / 順序 / 停止点 / quality gate
- つまり、phase 差分と scope 差分の両方がある

### 視点C: 構造設計レビュー
- 完全分割（initiative/epic/issue × requirement/design/plan）の 9 文書化は、正本が増えすぎる
- `skills` の参照先が増え、drift しやすい
- ベストプラクティスは、shared phase playbook を正本にしつつ、scope 固有差分は `workflow_<scope>.md` か薄い overlay に寄せるハイブリッド

## 選択肢 (必須)

### Option A: 現状維持（shared phase playbook + template 差分吸収）
- Pros:
  - 正本数が少ない
  - `skills -> docs -> templates` の構造が単純
- Cons:
  - scope 差分が docs 側で見えにくい
  - template を読まないと関心事の違いが十分に伝わらない場面がある

### Option B: 完全分割（initiative/epic/issue × requirement/design/plan）
- Pros:
  - 読むべき playbook が最初から具体的
  - scope ごとの差分を playbook 本体に直接書ける
- Cons:
  - 正本が 9 文書へ増え、drift しやすい
  - skill の参照先も増え、保守コストが大きい
  - shared 原則の修正が多点更新になる

### Option C: ハイブリッド強化
- 形:
  - `phase_*.md` は shared contract のみに絞る
  - `workflow_<scope>.md` に scope 固有の関心事、問い、品質ゲート、読み解き方を寄せる
  - templates は引き続き出力フォームとして scope 差分を持つ
- Pros:
  - shared 原則を一箇所に残せる
  - scope 差分は docs 側で読めるようになる
  - 既存の構造を大きく壊さない
- Cons:
  - workflow 側の書き方を少し厚くする必要がある
  - 境界を意識して設計しないと再び重複する

## 推奨案 (必須)
- 推奨は Option C。
- 結論:
  - **全面分割はしない**
  - **template に差分を押し込み続けるだけにもしない**
  - **shared phase playbook = 共通 contract、workflow = scope 固有 governance / 関心事、template = 出力の型** に整理する

## なぜ全面分割しないのか (必須)
- `requirement/design/plan` の共通原則そのものは scope をまたいで再利用価値が高い
- これを 9 文書へ分散すると、修正時に drift しやすい
- 今の主問題は「shared playbook の存在」ではなく、「shared に何を書き、scope 固有をどこへ逃がすかの境界が甘いこと」である

## なぜ template だけに任せないのか (必須)
- template は生成フォームであり、読む側の主資料ではない
- LLM / coding agents が scope 差分を template から読み解く前提は弱い
- よって、scope 固有の関心事は template のみに閉じず、`workflow_<scope>.md` でも見えるようにする必要がある

## To-Be（どうあるべきか） (必須)

### shared phase playbook に残すもの
- phase の責務
- 前提入力
- 調査 → docs 化 → ヒアリング → reviewer loop → handoff の共通 contract
- shared minimum gate

### workflow_<scope>.md に寄せるもの
- その scope 固有の問い
- その scope で重視する品質ゲート
- その scope の文書を読む / 書くときに着目すべき項目
- shared gate に上乗せする additive gate

### templates に残すもの
- 実際の文書の型
- 項目レベルの必須 / 任意
- frontmatter
- scope 固有の具体フィールド

## 実務的な改善提案 (必須)
- 1. `phase_*.md` は今のまま shared contract に保つ
- 2. `workflow_initiative.md` に initiative 特有の関心事を追加する
  - 例: success metrics、stakeholder、投資判断、DoR/DoD
- 3. `workflow_epic.md` に epic 特有の関心事を追加する
  - 例: E2E 要求、E-AC、NFR、契約 / 移行 / 観測性
- 4. `workflow_issue.md` に issue 特有の関心事を追加する
  - 例: AC/EC、観測点、既存実装調査、TDD、step review
- 5. skills は新設せず、参照先 docs をこの整理に沿って調整する

## 判断 (必須)
- 現状:
  - template が scope 差分を吸収している
  - shared playbook も scope 差分を少し背負ってしまっている
- To-Be:
  - template はフォーム
  - shared playbook は共通 contract
  - workflow は scope 固有 governance
- 推奨:
  - shared playbook の全面分割ではなく、workflow 側の scope 固有説明を強めるハイブリッドへ寄せる

## 次アクション (必須)
- まず `workflow_initiative.md` / `workflow_epic.md` / `workflow_issue.md` に、各 scope 特有の関心事を短く明示する改修案を作る
- skills はその docs 参照先を調整する
- template はフォームとして維持し、運用ルールの正本にしない
