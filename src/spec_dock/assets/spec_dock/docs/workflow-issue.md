# Workflow: Issue（要件 → 設計 → 計画 → 実装 → 報告）

このドキュメントは、**1つの Issue を単独の作業単位**として完結させるためのワークフローです。  
Codex CLI（コーディングエージェント）は、原則としてこのフローに従い、推測で進めません。

関連:
- ツリー運用（Initiative/Epic/Issue）: `workflow-tree.md`
- ADR運用: `workflow-adr.md`
- 共通原則/チェックリスト（正）: `spec-dock-guide.md`

---

## 0. 入口（active と context-pack）

### 0.1 active を確認/設定

```bash
./spec-dock/scripts/spec-dock active show
./spec-dock/scripts/spec-dock active set --issue 123   # iss-0123 / iss-local-0001 も可
```

`spec-dock/active/context-pack.md` が生成され、エージェントはそこから作業を開始できます。

### 0.2 読む順番（推奨）

1. `spec-dock/docs/README.md`
2. `spec-dock/active/context-pack.md`
3. 対象 Issue の仕様（active配下）
   - `spec-dock/active/issue/requirement.md`
   - `spec-dock/active/issue/design.md`
   - `spec-dock/active/issue/plan.md`
4. 親の仕様（必要に応じて。重複を書かないため）
   - `spec-dock/active/epic/requirement.md`
   - `spec-dock/active/epic/design.md`
   - `spec-dock/active/epic/plan.md`
   - `spec-dock/active/initiative/requirement.md`
   - `spec-dock/active/initiative/design.md`
   - `spec-dock/active/initiative/plan.md`
5. ADR（必要に応じて）
   - `spec-dock/active/**/adrs/*.md`

---

## 1. 計画フェーズ（Planning）

> ここでのゴールは「実装可能で、レビュー可能で、テストで証明できる」仕様にすること。

### 1.1 要件定義（Issue requirement）

対象: `spec-dock/active/issue/requirement.md`

- AC/EC を **観測可能（テスト可能）** に落とす
- スコープ境界（MUST/MUST NOT/OUT OF SCOPE / Always/Ask/Never）を固定する
- As-Is は「再現手順/観測点/実測結果/根拠」を残す
- 未確定事項（TBD）は「質問/選択肢/推奨案/影響範囲」で書く

承認ゲート:
- ユーザー/レビュアーの **明示的承認** を得るまで `状態: approved` にしない

### 1.2 設計（Issue design）

対象: `spec-dock/active/issue/design.md`

- 変更計画（ファイルパス単位）を具体化する
- 固定する IF 契約（API/関数/クラス境界）を明文化する
- 要件→設計→テストの対応（マッピング）を作る
- テスト戦略（AC/EC→テスト）と、非交渉制約の検証方法を書く

ADR（必要なとき）:
- トレードオフ/方針が割れるなら、**先に ADR を起こす**（`workflow-adr.md`）
- エージェントは ADR の Decision を勝手に確定しない（未決の叩き台でよい）

#### 1.2.1 意思決定ヒアリング（ADR を叩き台に挟む）

意思決定が必要な質問（トレードオフ/互換性/移行/運用影響など）をユーザーに投げる場合は、  
**質問 → 回答 → 設計/計画のアップデート → フィードバック**のサイクルの中に ADR を挟みます。

手順（推奨）:
1. ADR を作る（作成コマンド/置き場所は `workflow-adr.md`）
2. ADR を叩き台として埋める（Decision は未決/TBDのまま）
   - Context / Options / Consequences を優先して整理する
   - Options は複数提示し、Pros/Cons を書く（必要なら推奨案は書いてよいが、**結論にしない**）
3. ユーザーへ質問する
   - 「決めたいこと（質問）」「選択肢」「推奨案（あれば）」「影響範囲/リスク」を短く提示する
4. ユーザー回答後に更新する
   - ADR の Decision を穴埋めし、`状態: accepted` にする
   - Issue/Epic の `design.md` / `plan.md` に決定内容を反映し、`TBD` を解消する
   - ADR↔仕様（requirement/design/plan/report）の相互リンクを更新する

補足:
- 事実確認や不足情報の確認（再現手順/ログ/期待値の確認など）は、原則として ADR ではなく仕様の `TBD` と質問で扱う。

承認ゲート:
- ユーザー/レビュアーの明示的承認を得るまで `状態: approved` にしない

### 1.3 実装計画（Issue plan）

対象: `spec-dock/active/issue/plan.md`

- 1ステップ = 1つの観測可能な振る舞い
- 各ステップで Red/Green/Refactor が回せる粒度
- 要件 ↔ ステップ対応表で、対象AC/ECをすべてカバーする
- 各ステップに `update_plan` 登録 / テスト / report 記録のチェックを残す

承認ゲート:
- ユーザー/レビュアーの明示的承認を得るまで `状態: approved` にしない

詳細チェック: `spec-dock-guide.md` の `requirement.md` / `design.md` / `plan.md` チェックリスト

---

## 2. 実装フェーズ（Implementation: TDD）

対象: `spec-dock/active/issue/plan.md`

1. 着手ステップ（Sxx）を選ぶ
2. `update_plan` に作業ステップ（調査/Red/Green/Refactor/品質ゲート/報告）を登録
3. TDD（Red → Green → Refactor）で実装
4. ステップ末尾で必ず行う
   - テスト（必要なら lint/format/typecheck）
   - `spec-dock/active/issue/report.md` へ実行コマンド/結果/変更ファイルを記録
   - `update_plan` を更新

重要:
- 実装中に仕様変更が必要になったら、**コード着手前に** `requirement.md → design.md → plan.md` の順で差分を反映し、矛盾を残さない。
- 仕様変更が「意思決定」を伴う場合は、まず ADR を叩き台として起こし（Decisionは未決のまま）、質問→回答→Decision確定→仕様反映の順で進める。

---

## 3. クローズ/振り返り（Report と親への反映）

対象: `spec-dock/active/issue/report.md`

- セッション単位で事実を残す（コマンド/結果/変更ファイル/判断の経緯）
- 既知の問題とフォローアップ（別Issue化）を残す

必要に応じて:
- Epic/Initiative の `report.md` に「完了Issue/決定事項/差分/フォローアップ」を反映する
- `sync` を実行して `spec-dock/.agent/tree.json` を更新する（詳細: `sync.md`）
