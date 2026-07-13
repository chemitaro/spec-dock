---
種別: 設計書（Issue）
ID: "iss-00313"
タイトル: "PR Merge Preparer の証拠駆動型修復継続ポリシー"
保証プロファイル: "standard"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
関連要件: ["requirement.md"]
関連計画: ["plan.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00313 PR Merge Preparer の証拠駆動型修復継続ポリシー — Issue 設計

> この文書内の `[N]` は規範的契約、`[P]` は実装上調整可能な提案を表す。保証ランタイムが認可したプロファイルは `standard` であり、実行準備状況は計画と最新のレビュアーゲートで別途判定する。

## 0. 文書の位置づけ

この設計は、現行の固定試行回数上限と同一 `root_cause_family` 再発時の停止を、統合バッチ分析、必須のChatGPT相談、オーケストレーターの判断、実質的な戦略差分に基づく意味的継続ゲートへ置換する。

実装順、Red/Green、委任、具体的なコマンド、レポート証拠の格納先は`plan.md`で定義する。

## 1. 保証プロファイルとIssue境界確認

### 1.1 認可済みプロファイル

- ランタイム認可: `standard / normal`
- 文書作成証拠上の推奨: `strict`（非権威。追加品質観点としてのみ利用）
- 理由:
  - 配布済みエージェントワークフロー契約を変更する。
  - プロバイダーのスキル、プロンプト、テンプレート契約とドッグフーディング互換性へ影響する。
  - 継続、失敗・復旧、人間ゲート、証拠の権限を明示する必要がある。
- Criticalではない理由:
  - ランタイム、永続スキーマ、破壊的移行、GitHubの状態変更を追加しない。
  - シークレットや認証情報を扱わず、むしろ送信禁止を固定する。
  - プロバイダーの文章とテンプレートを元に戻すことでロールバックできる。

### 1.2 Issue境界の判定

- 判断: `single_issue_coherent`
- Epic修復: いいえ
- 分割: いいえ。ただし、エスカレーショントリガーが発生した場合を除く

[N] 本Issueの判断範囲は、`github-pr-merge-preparer` がブロッキング修復を継続または人間ゲートへ分岐するワークフロー契約と、それを記録・配布・検証する従属面に限定する。

[N] ランタイムでの相談自動化、観測スキーマ、GitHub会話の変更、スキル横断の再試行フレームワークは別の判断範囲であり、本Issueへ取り込まない。

### 1.3 Criticalへのエスカレーション防止策

| 条件 | 候補判定 | 対応 |
|---|---|---|
| シークレットまたは認証情報の送信 | いいえ | 判明したら停止しCritical評価 |
| 破壊的な成果物移行 | いいえ | 判明したら分割 |
| GitHubの状態変更追加 | いいえ | 判明したらCriticalまたは別Issue |
| 永続的な再試行状態スキーマ | いいえ | 移行設計へ分割 |
| 高リスク戦略の自動実行 | いいえ | 人間ゲートを維持 |
| ロールバック不能 | いいえ | 計画を修正 |

## 2. 設計概要

### 2.1 変わること

1. `Fix loop limits` を `Repair continuation and human-gate policy` に置換する。
2. P0は1回、同一ファミリーのP1は2回、合計4回という既定上限を削除する。
3. 同一ファミリーの再発を自動停止から再発分析の契機へ変更する。
4. ブランチ変更を伴うブロッキング修復の委任前に、統合バッチ全体を対象とするChatGPT相談を必須にする。
5. 証拠、グループ化、戦略に実質的な変更がある場合は相談の鮮度を再評価する。
6. ChatGPTの出力は証拠専用であり、メインオーケストレーターの判断後にのみ修復戦略へ変換できる。
7. バッチテンプレートへ相談ゲート、統合戦略、反復台帳、意味的停止フィールドを追加する。
8. 反復番号はテレメトリーとして維持するが、上限を決める権限から切り離す。

### 2.2 変えないこと

- P0/P1をブロッキング、P2/P3を非ブロッキングとするポリシー。
- P2/P3だけを理由にブランチを変更しない規則。
- 最新ヘッドの観測要件。
- `github-pr-observation` の収集専用境界。
- 必須・任意チェックの扱い。
- マージ準備済みとレビュー指摘解消済みの区別。
- マージ、自動マージ、ブランチ削除、Issue完了、レビュー会話変更の禁止。
- 権限・認証、外部・不安定要因、ベースブランチ競合、スコープ拡大、破壊的変更・移行・シークレット・デプロイなどの強制ゲート。
- フロントマター、成果物ファイル名、ランタイムCLI、JSONスキーマ。

### 2.3 確定した設計契約

- `[N] DES-001`: 修復回数はテレメトリーであり、継続・停止を決める権限ではない。
- `[N] DES-002`: 同一ファミリーの再発は自動停止ではなく、必須の再分析を開始する契機である。
- `[N] DES-003`: ブランチを変更するブロッキング修復には、現在の統合バッチへ結び付けた最新のChatGPT相談、またはDES-011を満たす明示的な一回限りの手動フォールバックが必要である。
- `[N] DES-004`: ChatGPTの出力は証拠専用であり、オーケストレーターの判断なしに作業者への引き渡しへ入らない。
- `[N] DES-005`: 継続には最新の証拠、完全なトリアージ、強制停止がないこと、実質的に異なる有界な戦略、最新の相談またはDES-011のフォールバック、スコープ上安全な検証が必要である。
- `[N] DES-006`: 新たに実行可能な戦略がない場合、同じ効果のない戦略しかない場合、証拠が不十分・古い・安全でない場合は人間ゲートとする。
- `[N] DES-007`: スキルがワークフロー上の権限を持ち、テンプレートは証拠欄を提供し、テストは投影契約を検証する。
- `[N] DES-008`: プロバイダーソースを先に変更し、ミラーは標準の更新処理で生成・検証する。ミラーだけの直接編集は禁止する。
- `[N] DES-009`: 既存バッチは非破壊で再開でき、一括移行を要求しない。
- `[N] DES-010`: ランタイム、観測スキーマ、GitHubの状態、保証上の権限を変更しない。
- `[N] DES-011`: 相談失敗時は既定で安全側に閉じ、人間が対象の呼び出し、範囲、理由、失効条件を明示承認した一回限りの手動フォールバックだけを例外とする。フォールバックは相談成功または恒久的な免除ではない。

## 3. 規範的な情報源と優先順位

| 種別 | パス / ID | 意味 |
|---|---|---|
| 親要件 | `epic-00158/requirement.md` | スキルの所有権、証拠の権限、プロバイダー/ミラー境界 |
| 親設計 | `epic-00158/design.md` | プロバイダーソース優先、メインオーケストレーターの採用境界 |
| 親計画 | `epic-00158/plan.md` | Issue分割、準備状況、ミラー検証、EAL |
| 現行スキル | `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md` | 現行ワークフローと試行回数制限 |
| 現行プロンプト | `.../github-pr-merge-preparer/agents/openai.yaml` | エージェント呼び出しの文言 |
| 現行テンプレート | スキルローカル + 成果物 + 議論用 `pr-repair-batch.md` | バッチ証拠契約 |
| 過去の設計 | `iss-00178` | トリアージバッチ / 修復単位 / 根本原因ファミリー / 人間ゲートの基準 |
| 厳格な計画規則 | `phase_plan_issue.md`, `authoring/issue-plan.md`, 厳格計画テンプレート | 完了/委譲/テスト/S90/S99契約 |
| プロンプトパック | 記載されたローカルパス + ソースマニフェスト | ローカルコンテキストの作成証拠。採用時に成果物本文を検証済み |

正規情報源の優先順位:

```text
repository-wide accepted rules / parent contracts
  > current shipped behavior
  > canonical Issue requirement
  > canonical Issue design
  > canonical Issue plan
  > local research / interview / ChatGPT evidence
```

ローカル成果物のファイル名に`adopted`が含まれていても、その権限を自動継承しない。実際の本文とEAL判断の検証が必要である。

## 4. 要件から設計へのトレーサビリティ

| 要件 | 設計 | 扱い |
|---|---|---|
| BH-001 / AC-001 | DES-001 | 数値上限の削除、反復回数のテレメトリー化 |
| BH-002 / AC-003 | DES-003, DES-007 | 統合バッチ -> 相談 -> 判断 -> 委任 |
| BH-003 / AC-004 / AC-007 / EC-013 | DES-003, DES-006, DES-011 | 相談の鮮度 / 失敗時の処理 / 一回限りのフォールバック |
| BH-004 / AC-005 | DES-004 | 証拠専用の出力とオーケストレーターの判断 |
| BH-005 / AC-002 | DES-002 | 再発分類 |
| BH-006 / AC-006 | DES-005, DES-006 | 意味的継続アルゴリズム |
| BH-007 / AC-008 | DES-006, DES-010 | 強制停止を維持 |
| BH-008 / AC-009 | DES-007 | テンプレートの証拠スキーマ |
| BH-009 / AC-010..AC-012 | DES-007, DES-008 | プロバイダー / プロンプト / テンプレート / テスト / ミラー |
| BH-010 / AC-011 | DES-009 | 旧バッチの再開互換性 |
| AC-013 | DES-010 | スコープ外差分の防止 |
| AC-014 | 計画契約 | 完了 / 委任 / テスト / S90 / S99 |
| CON-001 / CON-002 | DES-004, DES-010 | 権限を昇格しない |
| CON-003 | DES-008 | プロバイダーソースを先に変更 |
| CON-004 / CON-005 | DES-010 | 観測とGitHubの境界を変更しない |
| CON-006..CON-008 | DES-001..DES-006, DES-011 | 必須相談 + 明示的フォールバック + 意味的終了 |
| CON-009..CON-012 | DES-007..DES-010 | ランタイム変更なし、安全な出力、鮮度 |

## 5. 判断範囲 / エスカレーション

| ID | 判断 | 扱い | 理由 |
|---|---|---|---|
| DEC-001 | 固定試行回数上限を削除する | 本Issueで決定 | Issue名と現在の欠陥の中心 |
| DEC-002 | 再発を分析開始の契機へ変更 | 本Issueで決定 | 回数制限削除後の中核的な振る舞い |
| DEC-003 | 必須の統合ChatGPT相談 + 明示的な一回限りのフォールバック | 本Issueで決定 | 採用済みの聞き取り・統合結果と要件に整合 |
| DEC-004 | ChatGPT出力に対する判断語彙 | 本Issueで決定 | 権限境界に必要 |
| DEC-005 | 意味的な継続・人間ゲートアルゴリズム | 本Issueで決定 | 盲目的な再試行の防止に必要 |
| DEC-006 | バッチテンプレートの証拠フィールド | 本Issueで決定 | 監査可能性に必要 |
| DEL-001 | 正確な文言 / 見出し / 補助テスト構造 | 実装へ委任 | 意味を維持すれば局所選択可 |
| ESC-001 | ランタイムでのChatGPT自動化 | 別Issue / アーキテクチャレビュー | ネットワーク・ホスト境界を跨ぐ |
| ESC-002 | 観測JSONの変更 | 別Issue | 収集契約を跨ぐ |
| ESC-003 | スキル横断の再試行フレームワーク | Epic/ADR候補 | 永続的で広範なポリシー |
| ESC-004 | GitHubの状態変更追加 | Critical / 別Issue | 安全境界 |

ADR候補:

- 固定回数から証拠駆動の継続判定へ authority を移す判断は、Issue-local ADR `artifacts/20260713t040923z-adr-evidence-gated-pr-repair-continuation.md` として採用する。
- 3つ以上の無関係なスキルへ証拠ゲート付き再試行を展開する場合、スキル横断ADRを検討する。

## 6. 現在の状態と目標状態

### 6.1 現在の状態

```text
observe latest head
  -> triage batch
  -> if blocking:
       apply severity + fixed attempt caps
       if same family reappears after repair: stop
       else delegate bounded fix
  -> push
  -> re-observe
```

問題は、`attempt_count` と `same_family recurrence` が終了を決める権限になっており、新しい証拠や戦略を評価する前に停止し得ることである。

### 6.2 目標状態

```text
observe latest head
  -> verify freshness / trigger boundary
  -> create or update integrated blocking batch
  -> complete triage and family/coupling analysis
  -> hard-stop check
  -> obtain fresh sanitized ChatGPT consultation for current batch
     OR verify explicit one-invocation local-only fallback approval
  -> main orchestrator dispositions recommendations
  -> require bounded strategy + material delta + validation plan
  -> delegate repair
  -> confirm commit/push
  -> re-observe latest head
  -> classify recurrence/new blockers
  -> repeat semantic gate or human gate
```

[N] この判断経路には、数値による反復回数の上限を設けない。

[N] この経路は無条件に無限ではない。ブランチを変更するたびに、新しい現行証拠、最新かつ有効な相談または明示的な一回限りのフォールバック、明示的な判断、証拠に裏付けられた有界な戦略が必要である。これらがない場合、経路は人間ゲートで終了する。

## 7. 責務アーキテクチャ

### 7.1 コンポーネント

| コンポーネント | 所有する責務 | 所有してはならない責務 |
|---|---|---|
| `github-pr-observation` | トリガーと証拠の収集、最新ヘッドの観測結果 | リスク判断、相談、継続判断 |
| `github-pr-merge-preparer/SKILL.md` | 運用手順、ゲート、停止条件、権限境界 | 生のテンプレート重複、ランタイムパーサー |
| `openai.yaml` | 簡潔な呼び出し意図 | ポリシーの詳細または独立した権限 |
| スキルローカルテンプレート | 詳細な運用バッチワークシート | スキルから独立したワークフロー権限 |
| 配布済みの成果物・議論用テンプレート | 生成される証拠欄と互換構造 | スキルローカルテンプレートと異なるポリシー |
| ChatGPT | 選択肢、診断仮説、トレードオフ、リスク/戦略の提案 | 承認、ローカル統合判断、マージ判断 |
| メインオーケストレーター | 証拠検証、判断、作業者への引き渡し、継続・人間ゲート判断 | ChatGPTへの暗黙的な権限委譲 |
| 修復作業者 | スコープ内の実装と検証 | 要件・スコープまたは相談判断の再定義 |
| 人間 | 曖昧、高リスク、未対応の判断とマージ | 該当なし |

### 7.2 依存方向

```plantuml
@startuml
actor Human
participant "github-pr-observation\ncollection only" as Obs
participant "github-pr-merge-preparer\njudgment owner" as Prep
collections "Integrated Repair Batch\nevidence control sheet" as Batch
participant "ChatGPT\nevidence-only consultant" as GPT
participant "Main Orchestrator\ndisposition owner" as Orch
participant "Repair Worker" as Worker

Obs --> Prep : latest-head evidence
Prep --> Batch : inventory / family analysis
Batch --> GPT : sanitized current batch context
GPT --> Orch : recommendations / risks / options
Orch --> Batch : disposition + strategy delta
alt safe bounded strategy exists
  Orch --> Worker : scoped handoff
  Worker --> Orch : commit + validation evidence
  Orch --> Obs : re-observe current head
else hard stop / no strategy / unavailable evidence
  Orch --> Human : human gate evidence
end
@enduml
```

[N] 権限モデル上、ChatGPTは作業者を直接呼び出さない。メインオーケストレーターは、明示的に判断した内容だけを作業者契約へ変換しなければならない。

## 8. ドメイン用語 / データ契約

これらはワークフロー文書の用語であり、新しいランタイムスキーマではない。

### 8.1 `RepairBatchSnapshot`

概念上のフィールド:

- `pr_number`
- `head_sha`
- `observation_status`
- `trigger_state`
- `blocking_item_ids`
- `blocking_family_ids`
- `nonblocking_context_ids`
- `allowed_paths`
- `forbidden_paths`
- `requirement_constraints`
- `compatibility_constraints`
- `validation_obligations`
- `snapshot_fingerprint`（人間が読める証拠の結び付け。必ずしも機械的なハッシュではない）

### 8.2 `RecurrenceClass`

[N] 規範的な語彙:

- `not_recurrent`
- `same_family_new_evidence`
- `same_family_incomplete_implementation`
- `same_family_strategy_failed`
- `same_family_misclassified`
- `same_family_stale_observation`
- `same_family_unknown`

[N] `same_family_*` 自体は停止判断ではない。必要な分析と鮮度への対応を選択するための値である。

### 8.3 `RepairStrategy`

概念上のフィールド:

- `strategy_id`
- `root_cause_hypothesis`
- `covered_item_ids`
- `covered_family_ids`
- `allowed_paths`
- `behavior_change`
- `compatibility_effect`
- `validation_plan`
- `rollback_plan`
- `delta_from_prior_strategy`
- `bounded_reason`

### 8.4 `ConsultationEvidence`

概念上のフィールド:

- `consultation_id`
- `consultation_status`: `fresh` / `stale` / `failed` / `unavailable` / `consultation_denied` / `unsafe`
- `fallback_approval_status`: `not_requested` / `approved_for_invocation` / `fallback_approval_denied` / `expired`
- `consulted_at`
- `bound_head_sha`
- `bound_observation_status`
- `bound_family_ids`
- `bound_strategy_context`
- `input_summary_ref`
- `recommendation_summary_ref`
- `open_risks`
- `freshness_invalidators`

[N] モデルとの会話を逐語的に記録したものは、必須または許可されたバッチフィールドではない。リポジトリ相対の証拠参照はサニタイズ済みの要約成果物を指してよいが、認証情報、ホストパス、未レビューの逐語的なモデル会話記録を指してはならない。

### 8.5 `OrchestratorDisposition`

[N] 規範的な値:

- `use`
- `partial-use`
- `reject`
- `defer`
- `human-gate`

必須フィールド:

- 推奨事項または選択肢のID
- 判断
- 根拠
- 使用した証拠
- スコープへの影響
- 残存リスク
- 結果として採用する戦略ID（該当する場合）

### 8.6 `ContinuationDecision`

[N] 規範的な値:

- `continue-repair`
- `reobserve-first`
- `refresh-consultation`
- `human-gate`
- `merge-prepared-evaluation`

[N] `attempt-limit-reached` という値は存在しない。

## 9. ChatGPT相談契約

### 9.1 トリガー

[N] ブランチを変更するブロッキング修復の委譲には、最新の相談または有効なDES-011の一回限りのローカル限定フォールバックのいずれかが常に必要である。

対象には次を含む:

- 最初のブロッキングバッチ修復。
- 前回の修復後にブロッキング項目が残っている状態での再観測。
- 修復によって新たに生じたブロッキングファミリー。
- ファミリーのグループ化、根本原因、許可スコープ、検証計画の実質的な変更。
- 現在の証拠が直近の相談との結び付きと異なる場合における、旧形式または一時停止中のバッチの再開。

P2/P3または任意対応・対応不要の項目だけが残り、修復による変更を予定していない場合、それだけを理由に相談を要求しない。

### 9.2 相談の範囲

[N] ブロッキング項目が厳密に1件で関連する義務もない場合を除き、相談の入力は孤立した単一コメントではなく、統合された現在のブロッキングバッチ全体を対象とする。

必須入力の概要:

1. PRと最新ヘッドのメタデータ。
2. 観測の完全性とトリガー状態。
3. すべてのブロッキング項目と証拠参照。
4. ファミリーと結合関係の分析。
5. 以前の戦略、コミット、検証、再観測の結果。
6. 現在の再発分類。
7. 許可するパス・操作と禁止するパス・操作。
8. 要件、設計、互換性、セキュリティの制約。
9. 提案する質問: 根本原因、選択肢、戦略差分、テスト、リスク、停止条件。

### 9.3 サニタイズ

[N] オーケストレーターは次を削除またはマスキングしなければならない:

- シークレット、トークン、認証情報、非対称署名素材。
- 診断に不要な個人情報または非公開情報。
- ホストローカルの絶対パス。
- 未加工の環境ダンプ。
- 無関係なリポジトリ内容。
- 実行可能形式またはバイナリのペイロード。

サニタイズによって安全な外部相談に不可欠な証拠が失われる場合、相談状態は `unsafe` となり、外部送信を常に禁止する。ワークフローは既定で人間ゲートへ進む。有効なDES-011承認がある場合に限り、安全でない素材を送信しないローカル限定分析を認可できる。

### 9.4 保持する出力

保持するのは次に限る:

- 相談の来歴、状態、鮮度の結び付け。
- 簡潔な診断、選択肢、リスクの要約。
- 提案する戦略差分。
- 未解決の質問。
- オーケストレーターの判断と根拠。

モデルとの会話の逐語記録を正本文書または修復バッチへ貼り付けてはならない。

### 9.5 権限

[N] 相談は助言としての証拠である。

相談には次の権限がない:

- ブランチ変更を認可する。
- 要件または許可スコープを変更する。
- プロファイルまたは保証状態を承認する。
- 最新のレビュアー承認を与える。
- マージ準備済みまたはプルリクエスト引き渡し可能と宣言する。
- レビュー会話を解決する。
- ローカル統合判断を行う。

### 9.6 鮮度の失効

実質的な結び付けが一つでも変わった場合、相談は `stale` となる:

- `head_sha`
- 観測トリガーの状態または完全性
- ブロッキング項目・ファミリー
- 根本原因のグループ化
- 以前の戦略の結果
- 許可・禁止パス
- 要件・設計・互換性・セキュリティ制約
- 検証計画またはロールバック計画

意味を変えないメタデータコミットだけによるヘッドSHAの変更であっても、オーケストレーターによる明示的な鮮度判断が必要であり、暗黙には引き継がない。

## 10. 再発分析と継続アルゴリズム

### 10.1 アルゴリズム

```text
入力: 最新の観測、現在のバッチ、以前の台帳

1. 最新ヘッドとトリガーの鮮度を検証する。
   - stale/incomplete -> reobserve-first または human-gate。

2. 統合ブロッキング一覧とファミリー／結合分析を再構築する。
   - ブロッカーなし -> merge-prepared-evaluation。

3. ハード人間ゲートを評価する。
   - ハードゲートが一つでもある -> human-gate。

4. 各ブロッキングファミリーの再発を分類する。
   - 古い観測 -> reobserve-first。
   - 誤分類 -> 再グループ化。実質的な変更。
   - 不完全な実装 -> 欠けている有界な作業を記述する。
   - 戦略の失敗／新しい証拠 -> 新しい仮説と戦略差分を必須とする。
   - 不明 -> 証拠によって解決されない限り human-gate。

5. 現在のバッチについて、サニタイズ済みのChatGPT相談を取得／更新する。
   - stale -> 先に更新する。stale だけではフォールバックを有効化しない。
   - unavailable/failed/consultation_denied/unsafe -> 既定では human-gate。
   - 更新または復旧が復旧不能になった場合、明示的に人間が承認した一回の呼び出しに限る手動フォールバックによってのみローカル分析へ進める。承認範囲、理由、有効期限を記録し、相談成功とは決して表記しない。

6. メインオーケストレーターが推奨事項の扱いを決定する。
   - 採用または部分採用と判断された戦略がない -> human-gate。

7. 候補戦略を検証する。
   - 有界かつスコープ内で、必要な場合は実質的に異なり、
     テスト／ロールバック／再観測の経路を備え、ハード契約を維持していなければならない。
   - それ以外 -> human-gate または計画修正。

8. 一つの一貫した修復単位、または順序付けられた結合単位の集合を委任する。

9. コミット／プッシュの証拠を確認し、最新ヘッドを再観測する。

10. 台帳に追記し、ステップ1から繰り返す。
```

### 10.2 判断表

| 証拠の状態 | 再発 | 戦略の状態 | 相談 | 判断 |
|---|---|---|---|---|
| 古い / 不完全 | すべて | すべて | すべて | `reobserve-first` または人間ゲート |
| 最新、ブロッカーなし | なし | 該当なし | 該当なし | マージ準備済み評価 |
| 最新 | 初回発生 | 有界 / スコープ内 | 最新 + 判断済み | 修復を継続 |
| 最新 | 不完全な実装 | 有界な完了差分 | 最新 + 判断済み | 修復を継続 |
| 最新 | 以前の戦略が失敗 | 実質的に異なる戦略 | 最新 + 判断済み | 修復を継続 |
| 最新 | 以前の戦略が失敗 | 同じ戦略または名称変更のみ | すべて | 人間ゲート |
| 最新 | ファミリーの誤分類 | 再編成した証拠 | 更新済み | 新たな判断後にのみ継続 |
| 最新 | 不明な再発 | 解決可能な証拠なし | すべて | 人間ゲート |
| 最新 | すべて | スコープ拡大が必要 | すべて | 計画修正 / 人間ゲート |
| 最新 | すべて | 安全な戦略 | `unavailable` / `failed` / `consultation_denied` / `unsafe` | 既定では人間ゲート |
| 最新 | すべて | 安全な戦略 | 復旧不能な相談 + 明示的な一回限りのフォールバック | ローカル限定分析 + 判断。承認範囲内でのみ継続 |
| 最新 | すべて | すべて | `fallback_approval_denied` | 絶対的な人間ゲート。フォールバック禁止 |
| 最新 | すべて | すべて | `stale` | 修復前に相談を更新。更新が復旧不能になった場合のみフォールバック可 |
| 最新 | すべて | すべて | モデル会話の逐語記録のみ / 判断なし | 人間ゲート |

### 10.3 意味に基づく終了特性

ループは次の場合に終了するか、自律的に停止する:

- ブロッカーが残っていない。
- 最新ヘッドの新しい証拠がない。
- 強制ゲートが存在する。
- 実質的に異なる有界な戦略がない。
- 相談を安全かつ最新の状態で完了できず、有効なDES-011フォールバックもない。
- フォールバック承認が拒否、欠落、失効、または別の呼び出しに由来する。
- オーケストレーターが推奨事項を確信を持って判断できない。
- 必要なスコープまたは契約が拡大する。

したがって、数値上限の削除は無条件の無限再試行を意味しない。

## 11. 強制人間ゲート契約

[N] 次の分類は、反復回数にかかわらず即時または委譲前の人間ゲートとして維持する:

- 権限、認証、認可の失敗。
- リポジトリスコープ内で安全に修復できない外部サービス、プラットフォーム、不安定要因の失敗。
- ベースブランチの競合、またはリベース・マージ判断が必要な場合。
- 十分なソース証拠がない不明な失敗。
- 要件の拡大または設計契約の変更。
- 破壊的変更、移行、シークレット、認証情報、デプロイ、本番状態への影響。
- 曖昧なレビュー意図、または競合するレビュアー指示。
- プラットフォーム上でのみ行えるレビュー返信、スレッド解決、却下、管理者上書き。
- 未承認のレビュートリガー、古いトリガー、または再開メタデータの欠落。
- 有効なDES-011ローカル限定フォールバックがない、安全でない・利用不能・失敗した相談。
- フォールバック承認の拒否、失効、スコープ不一致、または別の呼び出しからの再利用。
- 実質的な差分がない、同じ効果のない戦略。
- ユーザー作成成果物の保護を保証できない場合。

[N] 既存の書き込み禁止対象および禁止操作は変更しない。

## 12. スキル / プロンプト / テンプレートの契約差分

### 12.1 `SKILL.md`

置換対象:

- 見出し `Fix loop limits`
- P0/P1/合計の既定数値
- 同一ファミリー再発時の強制停止規則

置換後:

- `Repair continuation and human-gate policy`
- 試行回数はテレメトリーであるという記述
- 統合バッチ相談ゲート
- 再発分類
- 相談の鮮度と権限
- 戦略差分に基づく継続条件
- 意味的停止・人間ゲート一覧
- 台帳要件

維持するもの:

- 観測、トリアージ、作業者、プッシュ、再観測を巡るワークフロー順序。
- 禁止される書き込みと操作。
- P2/P3ポリシー。
- マージ準備済みの判定条件と、人間によるマージ判断の境界。

### 12.2 `openai.yaml`

「範囲を限定した修正」を強調する現在の文言は、試行回数を制限する意味に解釈される可能性がある。候補文言では次を強調する。

- 統合ブロッキングバッチのトリアージ
- 証拠ゲート付き修復継続
- 最新のChatGPT相談
- 試行回数ではなく、有界なスコープと戦略
- 人間によるマージ判断は引き続き外部で行うこと

意図の例であり、文言の完全一致は必須ではない。

```yaml
default_prompt: >-
  Prepare the current PR for human merge judgment by observing the latest head,
  triaging the integrated repair batch, consulting ChatGPT as evidence before
  branch-mutating blocking repairs, delegating only dispositioned in-scope
  strategies, re-observing after each push, and stopping at semantic human gates.
```

### 12.3 バッチテンプレートのセクション

必須の対象セクション:

1. `PR / Observation Metadata`
2. `Batch Purpose`
3. `Concern Catalog`
4. `Inventory`
5. `Per-Concern Analysis`
6. `Root-Cause Family and Coupling Analysis`
7. `Integrated Repair Strategy`
8. `ChatGPT Consultation Gate`
9. `Orchestrator Disposition`
10. `Repair Queue / Unit Plan`
11. `Repair Iteration Ledger`
12. `Semantic Stop / Human-Gate Conditions`
13. `Merge-Prepared Gate`
14. `Final Summary`

### 12.4 相談ブロックのフィールド

```text
consultation_required
consultation_status
consultation_id
consulted_at
bound_head_sha
bound_observation_status
bound_family_ids
input_summary_ref
recommendation_summary_ref
freshness_invalidators
open_risks
orchestrator_disposition_summary
```

### 12.5 反復台帳のフィールド

| フィールド | 意味 |
|---|---|
| `iteration_index` | テレメトリー専用。上限なし |
| `head_sha` | 観測との結び付け |
| `observation_status` | `complete` / `limited` / `stale` など |
| `family_ids` | 現在影響を受けているファミリー |
| `recurrence_class` | 再発分析 |
| `prior_strategy_id` | 以前に試行した戦略 |
| `proposed_strategy_id` | 現在の候補戦略 |
| `strategy_delta` | 実質的な差分 |
| `consultation_id/status` | 証拠参照と鮮度 |
| `orchestrator_disposition` | `use` / `partial-use` / `reject` / `defer` / `human-gate` |
| `action_taken` | `delegated` / `none` / `reobserve` など |
| `fix_commit` | コミット証拠 |
| `re_observation_result` | 最新の結果 |
| `continuation_decision` | 継続 / 再観測 / 更新 / 人間 / マージ評価 |
| `stop_reason` | 回数閾値ではなく意味的な理由 |

### 12.6 削除するテンプレートの意味

- `Default autonomous repair limit`
- `Default total autonomous repair limit`
- `loop limits reached`
- 「同一ファミリーが再発した」ことを十分な停止条件とする意味

### 12.7 維持するテンプレートの意味

- 必須・任意CIの証拠。
- レビュー所見、スレッド状態、マージブロッカー。
- 有効性、リスク、修正要否、判断の一覧。
- 修復単位と検証証拠。
- レビュー指摘解消済みとマージ準備済みの区別。
- 禁止操作と残存リスク。

## 13. ファイル変更計画

### 13.1 プロバイダーファイル

| パス | 変更内容 |
|---|---|
| `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md` | 主要ワークフロー契約の置換 |
| `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/agents/openai.yaml` | 証拠ゲート付き統合修復の意図 |
| `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md` | スキルローカルの詳細ワークシート |
| `src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md` | 生成成果物の契約 |
| `src/spec_dock/assets/spec_dock/templates/discussions/pr-repair-batch.md` | 生成される議論用契約。成果物テンプレートと同期 |

### 13.2 テスト

| パス | 計画する対象範囲 |
|---|---|
| `tests/cli_runtime/test_new.py` | 生成されたpr-repair-batchが新マーカーを含み、旧制限を除外し、メタデータとパスを維持すること |
| `tests/cli_runtime/test_runtime_new_doc_s09.py` | 文書・成果物種別の選択とテンプレート同等性が引き続き機能し、内容契約が更新されること |
| `tests/cli_runtime/test_wrappers.py` | インストール済み・ドッグフーディング用スキルとテンプレートの投影がプロバイダーの意味と一致し、旧制限マーカーがないこと |
| `tests/unit/infra/test_init_update.py` | 既存のIssue 105回帰契約を数値上限から証拠駆動継続へ更新し、維持対象のhard gateと禁止操作を引き続き固定すること |

### 13.3 生成物 / ドッグフーディングの検証対象

- `.agents/skills/github-pr-merge-preparer/**`
- `spec-dock/templates/artifacts/pr-repair-batch.md`
- `spec-dock/templates/discussions/pr-repair-batch.md`

[N] まずプロバイダーを編集する。リポジトリ標準の`spec-dock update .`で更新する。生成変更が差分に現れることはあるが、ミラーだけを直接手作業で編集してはならない。

### 13.4 禁止パス

- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/**`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**`
- `src/spec_dock/cli.py`
- 成果物投影と無関係なGitHubワークフローまたはアクションのコード
- `.assurance.json`
- このパック後にメインオーケストレーターが明示的に採用する場合を除く、無関係なIssue・Epic・Initiativeの正本文書

`source_binding`例外: canonical requirement/design/plan変更後にSpecDock標準の`assurance classify`がissue-local `.assurance.json`のsource SHAだけを更新することは許可する。profile、authority、schema、classificationの手動変更は禁止する。

## 14. 互換性と移行

### 14.1 互換性戦略

[N] これは、廃止された停止の意味を削除し、内容を追加・言い換えるMarkdown契約変更である。ランタイムスキーマの新しいバージョンは導入しない。

- 既存の修復バッチファイルは、有効な履歴証拠として残る。
- 既存のフロントマター、ファイル名、ID、スコープの振る舞いは変更しない。
- 旧形式のバッチは、履歴内容を削除せずに現在の相談、戦略、反復のセクションを追記して再開できる。
- 旧来の`attempt limit reached`判断は履歴証拠として残し、暗黙に書き換えない。
- 再開後の新しい継続判断には、新しい意味ゲートを使用する。

### 14.2 移行

- 一括移行: なし
- 自動書き換え: なし
- 稼働中の旧形式バッチに必要な手動更新: 次の修復変更前に現在のスナップショット、相談、判断を追記
- 読み取り互換性: Markdownは引き続き読める
- 書き込み互換性: 新しいテンプレートは追加セクションを生成する

### 14.3 ロールバック

1. プロバイダーのスキル、プロンプト、テンプレート、テストを元に戻す。
2. リポジトリ標準の`spec-dock update .`を実行し、ドッグフーディング投影を復元する。
3. 対象テスト、検証、同期、同等性検査を実行する。
4. 履歴バッチは書き換えない。すでに作成済みの新セクションは無害な証拠として残す。

ロールバックにデータ移行は不要である。

## 15. 失敗 / 復旧設計

| 失敗 | 検出 | 復旧 | 自律修復を許可するか |
|---|---|---|---|
| 古い観測 | ヘッド・トリガーの不一致 | 最新ヘッドを再観測 | 最新の証拠を得るまでは不可 |
| 相談が利用不能・失敗 | 状態・結果の欠落または回復困難な失敗 | 再試行・復旧。復旧不能なら人間ゲートまたは明示的な一回限りのローカル限定フォールバック | 明示的なフォールバック範囲内のみ可 |
| `consultation_denied` | プロバイダー、アカウント、ポリシーが相談を拒否 | 可能なら復旧。復旧不能なら人間ゲートまたはDES-011承認を別途取得 | 明示的なフォールバック範囲内のみ可 |
| `fallback_approval_denied` | 人間がフォールバックを拒否 | 絶対的な人間ゲート | 不可 |
| 安全でない相談 | サニタイズ不能 | 送信しない。人間ゲート、または安全でない送信を除外する明示的なローカル限定フォールバック | 明示的なフォールバック範囲内のみ可 |
| 古い相談 | 実質的な結び付けの変更 | 相談を更新。更新が復旧不能になった場合は人間ゲートまたはDES-011承認へ進む | 更新前は不可。更新が復旧不能になった後のみフォールバック可 |
| モデル会話の逐語記録のみ | サニタイズ済み要約・判断なし | 安全に要約するか人間ゲート | 不可 |
| 推奨事項の競合 | 証拠に裏付けられた選択肢なし | 人間ゲート | 不可 |
| 同じ戦略の反復 | 戦略差分なし | 人間ゲート | 不可 |
| 新たに実行可能な戦略 | 証拠 + 差分 + 最新の相談または有効なDES-011フォールバック | 判断して委任 | 可。有界なスコープ内のみ |
| プロバイダー・ミラーのずれ | 同等性・テストの失敗 | 更新を再実行し、ソースの権限を検査 | 最終完了は不可 |
| 生成テンプレートの不一致 | 焦点テストの失敗 | プロバイダーテンプレート・テストを修復 | 最終完了は不可 |
| スコープ拡大の判明 | 差分・設計の不一致 | 停止して修正または分割 | 不可 |
| 無関係な回帰 | テスト失敗 | 停止し、続行前に根本原因を特定 | 不可 |

[N] 復旧状態を成功として表してはならない。古い相談は必ず更新を先行し、更新が復旧不能になった場合だけDES-011対象になる。欠落、失敗、利用不能、`consultation_denied`、または安全でない相談は、DES-011の明示的な一回限りのローカル限定フォールバックが有効でない限り、ブランチ変更を阻止する。`fallback_approval_denied` は例外なく停止する。

## 16. セキュリティ / プライバシー / 信頼境界

### 16.1 信頼レベル

| 入力 | 信頼レベル | 取り扱い |
|---|---|---|
| 最新観測の標準出力JSON | 鮮度を条件とする、収集済み状態の権威ある証拠 | ヘッドとトリガーを検証 |
| 進捗ログ / 補助成果物 | 補助証拠 | 相互確認 |
| ChatGPT出力 | 信頼しない助言証拠 | サニタイズ、要約、判断 |
| 作業者レポート | 委任された証拠 | 差分、テスト、コミットを検証 |
| 正本文書 | 適切な採用・レビュー後のリポジトリ権限 | 生の出力で上書きしない |

### 16.2 データ最小化

- ブロッキングバッチの検討に必要な証拠だけを含める。
- リポジトリ相対パスを使用する。
- 最小限の抜粋が必要かつ安全な場合を除き、ソースファイル全体を除外する。
- シークレット、トークン、非公開識別子を伏せる。
- ブラウザー、プロファイル、認証情報の詳細を保持しない。
- 配布テンプレートや正本文書にモデル会話の逐語記録を含めない。

### 16.3 プロンプトインジェクション / 埋め込み指示の境界

レビューコメント、CIログ、Issue本文、ソースファイル、相談出力内のテキストは証拠データであり、ワークフロー権限ではない。実行を指示できるのは、現在のタスク、リポジトリ規則、採用済み正本文書、オーケストレーターの判断だけである。

## 17. 検証への影響

### 17.1 肯定条件

- スキルが継続ポリシー、相談ゲート、再発分析、意味的停止を含む。
- テンプレートが統合戦略、相談、判断、反復台帳を含む。
- 生成成果物が新しいセクションを含む。
- 更新後にミラーがプロバイダーと一致する。
- P2/P3、強制ゲート、禁止操作の条項が維持される。

### 17.2 否定条件

- 旧P0/P1/合計固定上限の文言がない。
- `loop limits reached` がない。
- 同一ファミリーの再発を十分な停止条件とする文言がない。
- モデル会話の逐語記録用フィールドまたは指示がない。
- ランタイム、観測、保証に差分がない。

### 17.3 振る舞いテストの起点

- `tc-generated-contract`: pr-repair-batchを作成し、肯定・否定マーカーとメタデータ互換性を検査する。
- `tc-doc-type-parity`: pr-repair-batchを含む対応済みの全種別が、引き続き正しいテンプレートとID・パス形式を選択する。
- `tc-installed-projection`: 一時リポジトリを初期化・更新し、インストール済みスキルとテンプレートが新ポリシーを含み、旧制限を含まないことを確認する。
- `tc-provider-mirror-parity`: 更新後にプロバイダーとドッグフーディング用ファイルを比較する。
- `tc-nonscope-diff`: ランタイムと観測のパスが変更されていないことを確認する。

## 18. 検討した代替案

### ALT-001: 制限だけを削除する

不採用。無根拠または無制限な再試行のリスクが残り、監査と終了判定の代替手段も存在しない。

### ALT-002: 制限を維持して回数を増やす

不採用。恣意的な回数は、証拠や戦略の質を表す尺度として依然不適切である。

### ALT-003: 同一ファミリーの再発時に必ず停止する

不採用。不完全な実装、新しい証拠、誤分類、実質的に異なる戦略を区別できない。

### ALT-004: ChatGPTが修正を自動選択して認可する

不採用。証拠と正規の権限との境界に違反し、安全でない暗黙の委任を生む。

### ALT-005: N回失敗した後だけ相談する

不採用。数値による権限を再導入し、統合バッチレビューなしで初回修復を許してしまう。

### ALT-006: P2/P3だけの状態を含むすべての観測で相談する

不採用。不要な負荷となり、非ブロッキング所見では変更しないポリシーと衝突する。相談が必須なのは、ブランチを変更するブロッキング修復を検討するときである。

### ALT-007: ランタイムのカウンターまたは状態機械を実装する

スコープ外として不採用。現在の変更はスキルとテンプレートのワークフロー契約であり、ランタイム永続化なしでテストできる。

### ALT-008: スキル、テンプレート、テストを別々のIssueに分割する

不採用。これらは1つの垂直な契約スライスであり、分割すると一時的なずれとIssue間の不完全な振る舞いが生じる。

## 19. 未決事項と前提

### A-001 必須相談の範囲

採用した判断: ブランチを変更するすべてのブロッキング修復の委任には、新鮮な統合相談を必須とする。唯一の例外は、人間が対象の呼び出しに限定して明示承認した手動フォールバックである。

### A-002 相談内容の保存

採用した判断: 修復バッチにはサニタイズ済みの要約、来歴、判断を保存し、会話の逐語記録を埋め込まない。計画証拠としての生の成果物は別の面で保持できるが、安全性レビューとEAL採用なしに正規の権限を持たない。

### A-003 テンプレート見出しの完全一致

意味上の全フィールドとテストが維持されるなら、実装時に日本語または英語の見出し名が変わってもよい。これは`[P]`であり、契約変更ではない。

Issue境界が安全でないことを示す未解決項目はない。これらは採用確認項目であり、`information_insufficient`とする理由ではない。

## 20. 計画への引き渡し契約

認可された標準計画は、次を満たさなければならない（ChatGPTの厳格な候補が示した追加の品質観点も採用する）。

1. 編集前に現在の固定制限条項とテンプレートマーカーの特性を記録する。
2. 新契約を肯定的に検証し、旧マーカーを否定的に検証するRed表明を追加する。
3. ミラーを直接編集せず、テンプレートより先に、または一体でスキルとプロンプトを更新する。
4. 明示的な検査により、強制ゲートとスコープ外の振る舞いを維持する。
5. リポジトリ標準の更新、焦点テスト、静的検査、検証、同期、同等性検査を実行する。
6. すべてのAC/DESを対応付ける完了索引を含める。
7. 手順ごとの委任と具体的なテストケースを含める。
8. S90の影響解消、厳格なレビューゲート、S99の最終ゲート、最終終了契約を含める。
9. ソースのずれ、ローカル成果物との矛盾、スコープ拡大、回帰、権限の曖昧さがあれば停止する。
10. ローカル統合判断後に、観測したすべての証拠を`report.md`へ記録する。このパック自体はその証拠を主張できない。
