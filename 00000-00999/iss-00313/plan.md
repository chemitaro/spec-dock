---
種別: 実装計画書（Issue）
ID: "iss-00313"
タイトル: "PR Merge Preparer 修復継続ポリシー実装計画"
保証プロファイル: "standard"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
関連要件: ["requirement.md"]
関連設計: ["design.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00313 PR Merge Preparer 修復継続ポリシー — 実装計画

> この計画は、実装者が曖昧な設計判断を追加せずに進められる粒度の正規実行契約である。保証ランタイムが認可したプロファイルは`standard`。実装引き渡し適格性は、新鮮な計画レビュー、ADRの義務、ソースの結び付け、実行開始ゲートを満たした後にのみ判定する。

## 0. 計画の位置づけ

### 0.1 計画が定義すること

- 依存関係を解決した実装順序。
- 手順ごとの許可パスと禁止パス。
- Red、Green、リファクタリングに対する期待事項。
- 具体的なテストケースとコマンド。
- 委任契約とレポート証拠の記録先。
- 完了索引、S90の影響解消、新鮮なレビューゲート、S99の最終ゲート、最終終了契約。
- 停止、修正、エスカレーションの条件。

### 0.2 計画が定義しないこと

- 実際に観測された合格または不合格の結果。
- コミットSHA、プッシュ状態、PRの状態。
- ローカル統合の判断またはレビュー担当者の判定。
- `.assurance.json`の変更または認可プロファイルの決定。
- GitHubの変更またはプルリクエストの引き渡し。

実施結果は正規の`report.md`にある観測証拠台帳へ記録する。本計画は結果を先取りしない。

## 1. 計画の準備状況と実行前ゲート

### 1.1 現在の計画状態

| 入力 | 状態 | 証拠 | 実行への影響 |
|---|---|---|---|
| ローカルブランチ | 利用可能 | `iss-00313-remove-pr-merge-preparer-repair-attempt-limits` | ソースの基準として使用可能 |
| Issue #313 | オープン | GitHub Issue | 同一性を確認済み |
| ローカルのIssue文書と成果物 | 検証済み | EAL-001..007 | 正規の要件と設計を採用済み |
| プロファイル | standard / normal | 有効な`.assurance.json` | 認可済み |
| 要件と設計のレビュー | 合格 | レポートのフェーズ台帳 | 計画レビューが残っている |
| 実装とテスト | 未実行 | なし | 結果を主張しない |

### 1.2 S01実行前の必須ゲート

- [ ] 要求されたローカルブランチを開き、`git rev-parse HEAD`を記録している。
- [x] プロンプトパックのソースハッシュと変換済み証拠の来歴を判断済みである。
- [x] 一覧にあるローカル成果物の本文を読んでいる。
- [x] EAL項目に明示的なローカル判断を付けている。
- [x] 必須相談と手動フォールバックの範囲が採用済みの統合結果と一致している。
- [x] メインオーケストレーターが正規の要件、設計、計画を作成している。
- [x] 保証ワークフローが`standard`プロファイルを認可している。
- [x] 新鮮な仕様レビュー担当者が本計画を合格としている。
- [x] Issue実行前にADR進行支援の義務を解消している。
- [ ] 作業ツリーの所有権と許可パスを確認している。

いずれかの項目を満たさない場合、この計画を暗黙に実行してはならない。正規仕様を更新するか、パックを古いものとして記録する。

### 1.3 未解決のブロッキング質問がないとする境界

この計画には、Issue境界が安全でないことを示す未解決の質問はない。残る実行準備ゲートにEpicの修復は不要である。

## 2. 実装戦略

### 2.1 戦略

契約を先に定める垂直スライスを用いる。

1. 現在のソースを正確に結び付け、旧ポリシーの特性を記録する。
2. 対象契約と禁止する旧マーカーについて、失敗する回帰アサーションを追加する。
3. プロバイダーの `SKILL.md` にある主要ワークフロー契約を置き換え、`openai.yaml` を整合させる。
4. プロバイダーの3つの修復バッチテンプレートを一体で更新する。
5. 標準更新経路を通じて、インストール済み投影とドッグフーディング投影を更新する。
6. 焦点を絞った検査、静的検査、統合検査、同等性検査、validate/sync、スコープ外変更検査を実行する。
7. 新鮮で独立したレビューと最終完了監査を実施する。

### 2.2 TDDの解釈

このIssueは、主にMarkdown/YAMLの契約作業とPythonの回帰アサーションで構成される。

- プロバイダーの説明文やテンプレートを変更する前に、生成済みまたはインストール済みの契約を検証できる箇所ではRedを必須とする。
- 失敗テストは、旧来の固定制限契約が残っているか、新しい相談・継続契約が欠けていることを理由に失敗しなければならない。無効なフィクスチャや無関係な環境エラーを理由にしてはならない。
- 既存テストがすでに契約を検出し、実装前からGreenである場合は、特性記録または変更不要の根拠を記録し、欠けている反証感度だけを追加する。
- 実装手順では、Greenを得るためにテストを弱めてはならない。

### 2.3 最小の一貫した変更

一貫性を保てる最小実装には、次のすべてを含める。

- スキルポリシー。
- エージェントプロンプトの文言。
- スキルローカルのバッチテンプレート。
- 成果物バッチテンプレート。
- ディスカッションバッチテンプレート。
- 生成済み・インストール済み契約のテスト。
- プロバイダーとミラーの検証。

スキルだけ、またはテンプレート1つだけの変更は不完全であり、完了した振る舞いのスライスとしてコミットしてはならない。

## 3. 変更範囲

### 3.1 許可するプロバイダーパス

```text
src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md
src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/agents/openai.yaml
src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md
src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md
src/spec_dock/assets/spec_dock/templates/discussions/pr-repair-batch.md
tests/cli_runtime/test_new.py
tests/cli_runtime/test_runtime_new_doc_s09.py
tests/cli_runtime/test_wrappers.py
tests/unit/infra/test_init_update.py
```

### 3.2 標準更新後に許可する生成物とドッグフーディングの変更

```text
.agents/skills/github-pr-merge-preparer/SKILL.md
.agents/skills/github-pr-merge-preparer/agents/openai.yaml
.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md
spec-dock/templates/artifacts/pr-repair-batch.md
spec-dock/templates/discussions/pr-repair-batch.md
```

生成先のパス名は、実際の更新差分から確認しなければならない。ミラーだけを直接編集することは禁止する。

### 3.3 禁止するパス / 操作

```text
src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/**
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**
src/spec_dock/cli.py
.github/**
issue-local .assurance.json の手動変更（SpecDock標準`assurance classify`によるcanonical source_binding SHA refreshだけは許可）
unrelated Issue/Epic/Initiative canonical docs
```

禁止する操作:

- マージ、自動マージ、ブランチ削除。
- レビューコメントへの返信、スレッド解決、却下、管理者による上書き。
- GitHub Issueのクローズまたは`spec-dock issue finish`。
- シークレット、トークン、非公開データの送信。
- モデルとの会話の生記録の収録。
- ワーカー出力に基づくローカル統合判断またはプロファイル変更。

### 3.4 スコープ防護コマンド

各コミット候補の時点とS99で実行する。

```bash
git diff --name-only -- \
  src/spec_dock/assets/install_root/.agents/skills/github-pr-observation \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime \
  src/spec_dock/cli.py \
  .github
```

期待結果: 出力なし。何らかの出力があれば計画修正のトリガーとする。

## 4. マイルストーンと依存関係グラフ

### 4.1 マイルストーン

| マイルストーン | ステップ | 成果 | コミット候補 |
|---|---|---|---|
| M0 ソースの結び付け | S01 | 正確なローカル基準と旧ポリシー一覧 | コミットなし |
| M1 契約のRed | S02 | 意図した新契約の欠落を理由にテストが失敗する | `test(pr-repair): 継続契約の回帰テストを追加` |
| M2 ワークフローのGreen | S03 | スキルとプロンプトが証拠ゲート付き継続を表す | テスト上の不可分性が必要ならM3と統合する |
| M3 テンプレートのGreen | S04 | 3つのプロバイダーテンプレートが同じ契約を記録する | `feat(pr-repair): 証拠駆動の修復継続契約へ更新` |
| M4 統合 | S05 | 生成物とミラーの出力、および焦点テスト一式が合格する | 分ける場合は`test(pr-repair): 配布投影と互換性を固定` |
| M90 影響の解消 | S90 | 文書、テンプレート、スキル、ミラーへの影響をすべて解消する | 必要でない限り個別コミットなし |
| M95 独立レビュー | S95 | 新鮮な仕様、コード、QAレビューの所見を判断済みにする | 必要に応じて修正コミット |
| M99 最終品質 | S99 | 完了索引と終了証拠一式を収集する | 新たな意味変更なし |

コミットメッセージは候補にすぎず、実際のコミット境界はローカルの実行ワークフローに従わなければならない。

### 4.2 依存関係グラフ

```text
S01 baseline/source binding
  -> S02 Red contract tests
     -> S03 skill + prompt contract
        -> S04 template contract
           -> S05 generated/mirror integration
              -> S90 impact resolution
                 -> S95 fresh independent reviews
                    -> S99 final quality and exit
```

どの実装手順も先行手順を省略してはならない。S03とS04は1つの不可分なGreenコミットにしてもよいが、手順ごとの証拠は分けて保持しなければならない。

## 5. 受け入れ範囲

### 5.1 必須の契約マーカー

実装では同等の見出しを選択してもよいが、テストは安定した意味マーカーを基準にしなければならない。推奨マーカーは次のとおり。

- `Repair continuation and human-gate policy`
- `ChatGPT Consultation Gate`
- `Integrated Repair Strategy`
- `Repair Iteration Ledger`
- `strategy_delta`
- `consultation_status`
- `orchestrator disposition`
- `iteration count is telemetry` or equivalent
- `same root_cause_family recurrence` + `re-analysis` or equivalent
- `verbatim model conversation record` + prohibition

### 5.2 禁止する旧マーカー

少なくとも次を対象とする。

- `Default autonomous repair limit: 1 repair attempt for P0`
- `Default autonomous repair limit for the same failure family: 2 attempts for P1`
- `Default total autonomous repair limit: 4 repair attempts per invocation`
- `Loop limits for the same failure class or total repair attempts are reached`
- 同じ`root_cause_family`の再発だけで停止を要求する文言

句読点の完全一致だけでなく、意味上の条項を検出できる堅牢なアサーションを用いる。

### 5.3 維持するマーカー

- P0/P1をブロッキング、P2/P3を非ブロッキングとする定義。
- P2/P3のみを理由とするブランチ変更の禁止。
- 最新のHEADとトリガーの新鮮さ。
- 権限、認証、外部要因、不安定性、ベース競合、スコープ拡大、破壊的変更、移行、シークレット、デプロイ、曖昧な意図、プラットフォーム限定事項に対する人間ゲート。
- 禁止されるマージ、スレッド、Issue操作。
- レビュー指摘解消済みとマージ準備済みの区別。
- 必須CIと非必須CIの振る舞い。

## 6. 仕様固定の完了索引

| 完了ID | 要件 / AC | 設計 | 実装ステップ | 検証 | 証拠の記録先 | 完了条件 |
|---|---|---|---|---|---|---|
| CLOS-001 | BH-001, AC-001, CON-007 | DES-001 | S02-S04 | 禁止マーカーのテストと検査 | レポートS02/S03/S04 | どのプロバイダー面や生成面にも数値上限の決定権がない |
| CLOS-002 | BH-005, AC-002 | DES-002 | S02-S04 | 再発文言のアサーション | レポートS03/S04 | 再発だけでは停止せず、再分析と差分が必要である |
| CLOS-003 | BH-002/BH-003, AC-003 | DES-003 | S02-S04 | 順序とセクションのアサーション | レポートS03/S04 | ブロッキング修復の委任前に統合相談を行う |
| CLOS-004 | AC-004, CON-012 | DES-003 | S03-S04 | 新鮮さフィールドと無効化条件のアサーション | レポートS04 | 相談を現在の重要な状態に結び付ける |
| CLOS-005 | BH-004, AC-005, CON-001 | DES-004 | S03-S04 | 判断と決定権に関する否定アサーション | レポートS03/S04 | 自動採用または自動認可を示す文言がない |
| CLOS-006 | BH-006, AC-006 | DES-005/DES-006 | S03-S04 | 継続判断表と説明文の検査 | レポートS03/S04 | 継続には意味上のすべてのゲートが必要である |
| CLOS-007 | AC-007, EC-013, CON-006 | DES-006/DES-011 | S03-S04 | 失敗、フォールバック、古い状態の更新判断に関するアサーション | レポートS03/S04 | 非合格は既定で人間ゲートとなる。古い相談では先に更新を試み、更新が復旧不能な場合に限り、範囲設定・監査された1回の呼び出し限定ローカルフォールバックへ進む |
| CLOS-008 | BH-007, AC-008 | DES-006/DES-010 | S02-S05 | 維持マーカーの回帰検査 | レポートS05 | 強制ゲートを弱めていない |
| CLOS-009 | BH-008, AC-009 | DES-007 | S02/S04 | 生成テンプレートのフィールドアサーション | レポートS04/S05 | バッチに相談、判断、反復の証拠欄がある |
| CLOS-010 | AC-010 | DES-007 | S03-S05 | ファイル横断の意味マトリクス | レポートS05 | スキル、プロンプト、テンプレートが一致する |
| CLOS-011 | BH-009, AC-011/AC-012 | DES-008 | S02/S05 | 一時生成、更新、比較、validate/sync | レポートS05/S90 | プロバイダーと投影が一致し、メタデータに互換性がある |
| CLOS-012 | BH-010 | DES-009 | S02/S04/S05 | ランタイム非依存性と追記互換性のテストおよび検査 | レポートS05 | ランタイムスキーマや移行がなく、旧コンテンツを維持する |
| CLOS-013 | AC-013, CON-004/5/9/10 | DES-010 | S01/S05/S99 | 差分防護と焦点テスト一式 | レポートS99 | スコープ外の実装またはポリシー変更がない |
| CLOS-014 | AC-014 | 計画の各節 | 全手順/S90/S95/S99 | 計画監査と新鮮な仕様レビュー | レポートの計画およびレビューゲート | 完了、委任、テスト、終了契約が完全である |
| CLOS-015 | CON-011 | DESのセキュリティ | S03-S05/S99 | 安全でないトークンとパスの走査 | レポートS99 | 変更した内容にモデルとの会話の生記録、シークレット、ホストパスがない |
| CLOS-016 | Issue境界 | DESの境界 | S01/S90/S99 | 変更パスと設計影響半径の監査 | レポートS90/S99 | 一貫した1つのワークフロー契約スライスを維持する |

計画されたコマンドだけを根拠に完了行を完了済みにしてはならない。正規のレポートに記録された観測証拠だけが完了を確定する。

## 7. 振る舞いバックログ

| 振る舞いID | 説明 | 優先度 | ステップ | 計画作成時の状態 |
|---|---|---|---|---|
| B-001 | 固定数値制限を継続の決定根拠にしない | P0 | S02-S04 | 計画済み |
| B-002 | 同一系統の再発を再分析のトリガーにする | P0 | S02-S04 | 計画済み |
| B-003 | ブロッキング修復の変更前に統合ChatGPT相談を行う | P0 | S02-S04 | 計画済み |
| B-004 | 相談は証拠に限り、オーケストレーターが判断する | P0 | S02-S04 | 計画済み |
| B-005 | 意味に基づいて継続または人間ゲートを判断する | P0 | S03-S04 | 計画済み |
| B-006 | 強制ゲートとP2/P3ポリシーを維持する | P0 | S02-S05 | 計画済み |
| B-007 | バッチ監査台帳で相談と戦略差分を扱える | P1 | S02/S04 | 計画済み |
| B-008 | 生成物、プロバイダー、ミラーが同等である | P1 | S05/S90 | 計画済み |
| B-009 | 旧バッチとランタイムに互換性がある | P1 | S02/S05 | 計画済み |
| B-010 | 完了、レビュー、最終ゲートを備える | P1 | S90/S95/S99 | 計画済み |
| B-011 | 1回の呼び出しに限るローカル限定フォールバックを明示し、範囲と期限を定め、相談成功として扱わない | P0 | S02-S04 | 計画済み |

## 8. 対象の振る舞いとTDDサイクル

ゲート通過後に最初に有効化する振る舞い:

- 有効な振る舞い: 最初にテスト可能な契約スライスを`B-001 + B-003 + B-007`とする。
- Redの対象: 生成済みまたはインストール済みの修復バッチ内容に相談・戦略フィールドがなく、旧制限の意味が残っている状態。
- Greenの対象: プロバイダーのスキルとテンプレートが新契約を表し、生成出力とインストール済み投影がテストを満たす状態。
- リファクタリングの対象: Greenの後にだけ重複したアサーションヘルパーを削除する。スキル横断フレームワークへ一般化しない。

TDDサイクルの規則:

```text
one contract assertion set
  -> prove intended Red
  -> smallest provider change
  -> focused Green
  -> inspect semantic preservation
  -> record evidence
  -> next behavior
```

## 9. 詳細な実行手順

# S01 — ローカルソースの結び付けと特性記録

### S01 目標

この計画を実際のローカルブランチに結び付け、編集前に現在の固定制限条項と再発停止条項をすべて特定して記録する。

### 依存関係

- 依存先: 第1節の採用ゲートと実行前ゲート。
- 後続で可能になる手順: S02。

### 許可する操作

- リポジトリの読み取り専用検査。
- ソースハッシュの計算。
- 基準となる焦点テスト。
- レポート証拠項目の準備。

### 禁止する操作

- プロバイダーまたはミラーの編集。
- 委任ワーカーによる正規仕様の変更。
- `.assurance.json` の変更。

### 委任契約

| 項目 | 契約 |
|---|---|
| 委任する役割 | メインオーケストレーター。任意で読み取り専用の調査担当 |
| 目的 | 正確なソースを結び付け、旧来の意味を列挙する |
| 許可するパス | リポジトリ全体を読み取り専用で使用 |
| 禁止するパス | すべての書き込み |
| 必須入力 | 正規のローカルIssue文書、プロンプトパックのマニフェスト、プロバイダーとミラーのファイル |
| 必須出力 | ソース結び付け表、旧マーカー一覧、branch/head/status、不一致一覧 |
| 検証 | 下記コマンド、ハッシュ、パスの存在 |
| 停止条件 | 要求されたローカルブランチが存在しない、判断未記録のソースマニフェスト不一致、ローカル統合内容が正規スコープと矛盾する |
| 証拠の記録先 | 正規の`report.md`の計画・事前確認セクションとEAL |

### S01 コマンド

```bash
git status --short --branch
git rev-parse HEAD
git branch --show-current

python - <<'PY'
from hashlib import sha256
from pathlib import Path
paths = [
    Path("src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md"),
    Path("src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/agents/openai.yaml"),
    Path("src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md"),
    Path("src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md"),
    Path("src/spec_dock/assets/spec_dock/templates/discussions/pr-repair-batch.md"),
    Path("tests/cli_runtime/test_new.py"),
    Path("tests/cli_runtime/test_runtime_new_doc_s09.py"),
    Path("tests/cli_runtime/test_wrappers.py"),
]
for path in paths:
    data = path.read_bytes()
    print(sha256(data).hexdigest(), path.as_posix())
PY

rg -n \
  "Default autonomous repair limit|Default total autonomous repair limit|Fix loop limits|Loop limits|root_cause_family.*repair commit" \
  src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer \
  src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md \
  src/spec_dock/assets/spec_dock/templates/discussions/pr-repair-batch.md

uv run pytest -q \
  tests/cli_runtime/test_new.py::TestCliNew::test_new_artifact_full_direct_catalog_success \
  tests/cli_runtime/test_runtime_new_doc_s09.py::TestRuntimeNewDocS09::test_doc_type_parity_template_selection_regression \
  tests/cli_runtime/test_wrappers.py::TestCliRulesContract::test_scaffold_docs_point_to_runtime_commands_and_rules_docs
```

### 具体的なテストケース

#### TC-S01-001 ソースマニフェストの結び付け

- 目的: プロンプトパックのスナップショットからのローカルなずれを検出する。
- 前提条件: 対象のローカルブランチをチェックアウト済み。
- 操作: 計画対象の8つのソースファイルをハッシュ化する。
- アサーション:
  - すべてのファイルが存在し、通常ファイルである。
  - ハッシュの差異を、想定内のローカルコンテキスト、古いパック、またはブロッカーとして明示的に分類する。
- 反証感度: ファイルの欠落、名前変更、読み取り不能、説明のないハッシュ不一致で失敗する。
- 証拠の記録先: レポートのソース結び付け表。

#### TC-S01-002 旧ポリシー一覧

- 目的: 固定制限の条項を見落としていないことを確認する。
- 操作: `rg`でプロバイダーのスキルとテンプレートを検索する。
- アサーション: 既知の上限または再発停止箇所を、パス、行、置換対象手順とともに列挙する。
- 反証感度: 後のS99で別の旧マーカーが見つかった場合、一覧は不完全である。
- 証拠の記録先: レポートの判断台帳とS01の証拠。

#### TC-S01-003 基準動作

- 目的: 新しい契約テストの前に、現在の生成、種別、雛形テストがGreenであることを証明する。
- 操作: 既存の焦点テスト3件を実行する。
- 期待結果: 合格するか、既存の失敗として編集前に分類されている。
- 反証感度: いずれかの失敗があると、S02のRedを正しく解釈できない。

### S01 完了ゲート

- 正確なブランチ、HEAD、ステータスが記録されている。
- 実際のローカル成果物本文をレビューし、EALの判断を更新した。
- 対象パスとハッシュのマトリクスが完成している。
- 旧ポリシー一覧が完全である。
- 基準テストに失敗がないか、実装差分外で明示的に解消している。
- Issue境界が引き続き一貫している。

満たさない場合は停止して正規仕様を修正し、S02へ進んではならない。

---

# S02 — Red契約テスト

### S02 目標

現在の固定制限契約に対して意図した理由で失敗し、既存のパス、フロントマター、ランタイムの振る舞いを維持するテストを追加する。

### 依存関係

- 依存先: S01終了ゲート。
- 後続で可能になる手順: S03とS04。

### 許可するパス

```text
tests/cli_runtime/test_new.py
tests/cli_runtime/test_runtime_new_doc_s09.py
tests/cli_runtime/test_wrappers.py
```

### 禁止するパス

この手順では、プロバイダーの本番ファイルと成果物ファイルをすべて禁止する。

### 委任契約

| 項目 | 契約 |
|---|---|
| 委任する役割 | `dev-coder` |
| 目的 | プロバイダー成果物を変更せず、反証感度の高い契約テストを追加する |
| 許可するパス | 3つのテストファイルだけ |
| 禁止するパス | すべての`src/**`、`.agents/**`、`spec-dock/**`、仕様、assurance |
| 必須入力 | requirement AC-001..AC-013、design DES-001..DES-010、S01のマーカー一覧 |
| 必須出力 | 肯定、否定、維持、ランタイム非依存のアサーションを含む焦点テスト |
| テスト要件 | Greenの変更前に意図したRedを示す |
| 停止条件 | Redの原因がフィクスチャまたは環境エラー、ランタイム変更が必要と思われる、既存テストの名前または配置が実質的に異なる |
| レポート記録先 | S02のRed/Green証拠表。ワーカー出力は検証されるまで証拠にとどまる |

### 計画済みテスト

#### 1. `test_new.py`

専用テストを追加する。候補名:

```python
def test_new_artifact_pr_repair_batch_uses_evidence_gated_continuation_contract(self) -> None:
    ...
```

テストする振る舞い:

- 一時リポジトリを初期化し、関連付けたIssue階層を作成する。
- サポート対象のCLIパスを通じて `pr-repair-batch` 成果物を作成する。
- 既存のファイル名、フロントマター、種別、タイトル、親、日付の動作をアサートする。
- 肯定的な意味マーカー（相談ゲート、統合戦略、反復台帳、戦略差分、判断、テレメトリ専用の回数）をアサートする。
- 禁止された固定制限マーカーがないことをアサートする。
- モデルとの会話の生記録の収録が禁止されていることをアサートする。

#### 2. `test_runtime_new_doc_s09.py`

テストを追加または拡張する。候補名:

```python
def test_pr_repair_batch_continuation_fields_remain_markdown_only_and_runtime_opaque(self) -> None:
    ...
```

テストする振る舞い:

- 新しい相談・継続セクションを含むテンプレートを提供する。
- リクエストフィールドやパーサーオプションを追加せず、既存のディスカッション・成果物作成経路を使用する。
- 描画した内容がフィールドを維持することをアサートする。
- ID・パス・型の振る舞いが変わらないことをアサートする。
- これによりランタイムスキーマが不要であることを証明する。

#### 3. `test_wrappers.py`

プロバイダーからインストール済み投影までを検証するテストを追加する。候補名:

```python
def test_scaffolded_pr_merge_preparer_uses_evidence_gated_repair_continuation_policy(self) -> None:
    ...
```

テストする振る舞い:

- 現在のプロバイダーチェックアウトから一時対象を初期化する。
- インストール済みの `.agents/.../SKILL.md`、インストール済みのスキルローカルテンプレート、`spec-dock/templates/{artifacts,discussions}/pr-repair-batch.md` を読み取る。
- 肯定マーカーと禁止する旧マーカーをアサートする。
- 現在のプロバイダー不変条件である場合、成果物テンプレートとディスカッションテンプレートがバイト単位で同一であることをアサートする。
- 新しいランタイムオプションが公開されないことをアサートする。

### 具体的なテストケース

#### TC-S02-001 生成物の肯定契約

- 前提条件: 現在のプロバイダーがまだ旧状態である。
- 操作: 生成されたバッチ内容をアサートする。
- 期待するRed: 相談、戦略、テレメトリのマーカーが欠けている。
- 次の理由では失敗してはならない: CLIセットアップ、GitHubスタブ、タイムスタンプ、パスフィクスチャ。

#### TC-S02-002 生成物の否定契約

- 操作: 旧上限マーカーがないことをアサートする。
- 期待するRed: 生成テンプレートに少なくとも1つの旧マーカーがある。
- 反証感度: 各既知マーカーを個別に検査するか、禁止一覧へ正規化する。

#### TC-S02-003 維持

- 操作: ファイル名、ID、親、タイトル、日付、成果物種別をアサートする。
- 変更前後の期待結果: どちらの状態でもGreen。
- 目的: Green化の際に生じる意図しない公開契約のずれを検出する。

#### TC-S02-004 ランタイムの不透明性

- 操作: 既存のランタイムパスを通じて、新しいMarkdownフィールドを含むテンプレートをレンダリングする。
- 期待結果: 新しいコマンド、リクエスト、スキーマのフィールドなしで内容が維持される。
- Redポリシー: 特性記録としてGreenになる場合がある。すでにサポートされている場合は変更不要として記録する。

#### TC-S02-005 インストール済み投影

- 操作: 一時対象を初期化し、インストール済みのスキルとテンプレートを検査する。
- 期待するRed: 旧ポリシーがあるか、新しいフィールドが欠けている。
- 反証感度: 誤ってプロバイダーファイルを読むのではなく、実際の対象ファイルを読む。

#### TC-S02-006 維持する強制ゲート

- 操作: 権限と認証、外部要因と不安定性、スコープ拡張、破壊的変更と移行とシークレットとデプロイ、P2/P3での変更禁止、禁止されたGitHub操作をアサートする。
- 期待結果: 変更前後ともGreen。
- 目的: 過度に広範な書き換えを防ぐ。

### S02 コマンド

実装で名前を決定した後、完全なノードIDを指定して新しい焦点テストを実行する。

```bash
uv run pytest -q \
  tests/cli_runtime/test_new.py::<new_generated_contract_test> \
  tests/cli_runtime/test_runtime_new_doc_s09.py::<new_runtime_opaque_test> \
  tests/cli_runtime/test_wrappers.py::<new_installed_projection_test>
```

次を記録する:

- 失敗したアサーション、
- CLOS-001/003/009/011に対応する理由、
- 維持アサーションと強制ゲートアサーションが失敗原因ではないことの確認。

### S02 完了ゲート

- 新しい契約の欠落または旧固定制限マーカーについて、意図したRedを観測している。
- プロバイダー成果物を変更していない。
- 無関係な基準回帰がない。
- テストに明示的な肯定、否定、維持の感度がある。

---

# S03 — プロバイダースキルとエージェントプロンプトの契約

### S03 目標

主要ワークフローの規範にある回数ベースの修正ループポリシーを置き換え、エージェント呼び出しプロンプトを整合させる。

### 依存関係

- 依存先: S02で意図したRed。
- 1人のワーカーが重複しないファイルだけを担当し、両方の完了後に最終的なGreenを統合する場合に限り、S04と並行して進めてもよい。

### 許可するパス

```text
src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md
src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/agents/openai.yaml
```

### 禁止するパス

- この手順ではテンプレート、テスト、ミラーファイル。
- 観測スキル、ランタイム、GitHubワークフロー。

### 委任契約

| 項目 | 契約 |
|---|---|
| delegated role | `doc-writer` |
| 目的 | 権限やスコープを拡大せず、ワークフローの中核を書き換える |
| 許可するパス | 上記2つのプロバイダーファイル |
| 禁止するパス | その他すべてのパス |
| 必須入力 | DES-001..DES-006、強制ゲート一覧、S02テスト |
| 必須出力 | 簡潔な初読ポリシー、相談順序、再発と戦略の意味、整合したプロンプト |
| 必須の維持事項 | P2/P3ポリシー、強制ゲート、禁止する書き込みと操作、merge-preparedと人間によるマージの境界 |
| 停止条件 | 正確な相談範囲をローカル統合内容と整合できない、文言が自動採用を示唆する、ランタイム自動化が提案される |
| 証拠の記録先 | レポートのS03差分要約、テスト出力、判断台帳 |

### 実装契約

#### スキルの変更

- `Fix loop limits` セクションを改名または削除する。
- P0、P1、合計の数値上限条項を削除する。
- 反復のインデックスと回数はテレメトリ専用であると明記する。
- 修復委任前に、統合されたブロッキングバッチ相談の順序を追加する。
- 相談のステータスと鮮度について、非通過状態を定義する。
- ChatGPTは証拠提供のみとし、メインオーケストレーターを判断の所有者として定義する。
- 再発カテゴリまたは同等の分析要件を定義する。
- 実質的に異なる境界付き戦略の要件を定義する。
- 意味に基づく人間ゲート条件を定義する。
- 既存の強制ゲートと禁止操作の全カテゴリを維持する。
- 権限があると主張せずに相談、判断、継続の証拠を報告するよう、応答チェックリストを更新する。

#### `openai.yaml` の変更

- 曖昧な回数制限の文言を置き換える。
- プロンプトを簡潔に保ち、`SKILL.md` に従属させる。
- 統合バッチ、証拠をゲートとする修復、再観測、人間によるマージ判断に言及する。
- スキルのワークフローがホスト機能に依存する場合、ChatGPTの自動実行を主張しない。ランタイム実装ではなく、必要な相談結果を記述する。

### 具体的なテストケース

#### TC-S03-001 数値上限が存在しない

- アクション: 対象を絞ったスキル・プロンプトのアサーションと、禁止マーカーに対する`rg`を実行する。
- 期待結果: 回数に基づく決定権の文言がない。

#### TC-S03-002 相談順序が存在する

- アクション: ワークフローの順序を検査する。
- 期待する順序: 観測 -> トリアージ -> 統合相談 -> 対応判断 -> ワーカー -> プッシュ -> 再観測。

#### TC-S03-003 決定権の境界

- アクション: ChatGPT周辺の用語を検査する。
- 期待結果: 証拠・助言に限られ、承認・採用・通過・マージ準備完了の決定権がない。

#### TC-S03-004 再発の意味

- アクション: 同一系統に関する文言を検査する。
- 期待結果: 再分析と戦略差分があり、再発だけを理由に自動停止しない。

#### TC-S03-005 強制ゲートの維持

- アクション: 維持事項のテスト一覧を実行する。
- 期待結果: 既存の安全カテゴリと禁止操作がすべて維持される。

### S03 焦点コマンド

```bash
uv run pytest -q \
  tests/cli_runtime/test_wrappers.py::<new_installed_projection_test>

rg -n \
  "Repair continuation|ChatGPT|consultation|strategy|root_cause_family|human gate|telemetry" \
  src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md \
  src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/agents/openai.yaml

if rg -n \
  "Default autonomous repair limit|Default total autonomous repair limit|Loop limits.*repair attempts" \
  src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer; then
  echo "obsolete fixed-limit contract remains" >&2
  exit 1
fi
```

インストール済み投影のテストはS05の更新までRedのままでもよい。S03ではプロバイダー内容のアサーションをGreenにし、想定内のミラー側Redとプロバイダー側の失敗を証拠上で区別しなければならない。

### S03 完了ゲート

- 主要ワークフローの契約が完全で、初読で実行可能である。
- ポリシー全体を重複させずにプロンプトを整合させる。
- この2ファイルに旧来の数値による決定権が残っていない。
- 強制ゲートと禁止操作を維持している。
- 決定権を拡大する文言がない。

---

# S04 — 修復バッチテンプレートの契約

### S04 目標

数値制限を用いず、統合戦略、相談証拠、オーケストレーターの判断、再発分析、意味に基づく継続を記録するよう、プロバイダーの修復バッチテンプレートをすべて更新する。

### 依存関係

- Depends on: S02 Red and DES-007 fields。
- 完全なGreenにする前にS03と統合しなければならない。

### 許可するパス

```text
src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md
src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md
src/spec_dock/assets/spec_dock/templates/discussions/pr-repair-batch.md
```

### 禁止するパス

ミラーを含むその他すべてのパス。

### 委任契約

| 項目 | 契約 |
|---|---|
| 委任するロール | `doc-writer` |
| 目標 | ランタイムとフロントマターの意味を変更せずに証拠ワークシートを実装する |
| 許可するパス | 3つのプロバイダーテンプレート |
| 禁止するパス | スキル、プロンプト、テスト、ランタイム、ミラー |
| 必須入力 | DES-007、テンプレートの現在のセクション、S02の生成物テストの期待値 |
| 必須出力 | 新しいフィールドと意味上の停止条件を備えた同期済みテンプレート |
| 互換性 | プレースホルダー、フロントマター、種別、親、日付を維持する。既存のレンダラーがサポートしない限り、新しいランタイムプレースホルダーを要求しない |
| 停止条件 | テンプレートがパーサーまたはスキーマの変更を必要とする。成果物テンプレートとディスカッションテンプレートの互換性を維持できない。モデルとの会話の生記録フィールドを要求される |
| 証拠の記録先 | レポートのS04差分、テスト、互換性の表 |

### 実装契約

#### 必須セクションの意味

- メタデータ、目的、懸念事項カタログ、一覧、懸念事項ごとの分析、修復キューと単位計画、マージ準備完了ゲートを維持する。
- 次のセクションを追加または改名する:
  - 根本原因の系統と結合の分析、
  - 統合修復戦略、
  - ChatGPT相談ゲート、
  - オーケストレーターの判断、
  - 修復反復台帳、
  - 意味上の停止条件と人間ゲート条件。

#### 反復台帳

少なくとも次を含める。

- 反復インデックス（テレメトリ専用）、
- HEAD SHAと観測ステータス、
- 系統IDと再発分類、
- 以前の戦略IDと提案する戦略ID、
- 実質的な戦略差分、
- 相談ID、ステータス、鮮度、
- オーケストレーターの判断、
- 操作と修正コミット、
- 再観測結果、
- 継続判断と意味上の停止理由。

#### 相談セクション

次を含める。

- 必須か不要か、およびその理由、
- fresh、stale、failed、unavailable、denied、unsafeのステータス、
- 現在の証拠との結び付け、
- サニタイズ済み入力要約への参照、
- 推奨事項要約への参照、
- 未解決のリスク、
- 判断の要約、
- モデルとの会話の生記録、シークレット、絶対パスの禁止。

#### 停止条件

次を削除する。

- 数値制限への到達。
- 同一系統の再発だけを十分な停止理由とすること。

次を追加または維持する。

- 実質的に異なる境界付き戦略がない。
- 同じ無効な戦略を繰り返す。
- stale/incomplete observation。
- consultation non-pass state。
- 強制的な安全カテゴリ。
- scope/requirement expansion。
- unapproved trigger/resume metadata failure。

### テンプレート整合性の規則

- S01で文書化された意図的な差異が証明されない限り、成果物とディスカッションのプロバイダーテンプレートはバイト単位で同一のままにする。
- スキルローカルテンプレートにはより詳細な運用情報を含めてもよいが、配布される2つのテンプレートと矛盾してはならない。
- 正確な見出しを変更できるのは、テストと必須の意味フィールドがすべて安定している場合だけである。

### 具体的なテストケース

#### TC-S04-001 必須フィールド

- 操作: 生成テンプレートとプロバイダーのテキストをアサートする。
- 期待結果: 相談、戦略、台帳のすべてのフィールドが存在する。

#### TC-S04-002 旧停止セマンティクスがないこと

- 操作: 3つのテンプレートすべてで禁止マーカーを走査する。
- 期待結果: 数値または同一再発だけを根拠とする停止権限がない。

#### TC-S04-003 成果物とディスカッションの一致

- 操作: `cmp -s` でプロバイダーの成果物テンプレートとディスカッションテンプレートを比較する。
- 期待結果: レビュー済みの例外が文書化されていない限り一致する。

#### TC-S04-004 ランタイム互換性

- 操作: ランタイム不透明性の焦点テストを実行する。
- 期待結果: 既存のレンダラーが、パーサーやリクエストの変更なしで新しいMarkdown本文を処理する。

#### TC-S04-005 安全な出力

- 操作: モデルとの会話の生記録を求める指示、シークレットまたはトークンのプレースホルダー、ホストの絶対パス例を走査する。
- 期待結果: 禁止事項またはメタデータへの参照だけがあり、安全でないペイロード欄がない。

### S04 コマンド

```bash
uv run pytest -q \
  tests/cli_runtime/test_new.py::<new_generated_contract_test> \
  tests/cli_runtime/test_runtime_new_doc_s09.py::<new_runtime_opaque_test>

cmp -s \
  src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md \
  src/spec_dock/assets/spec_dock/templates/discussions/pr-repair-batch.md

rg -n \
  "ChatGPT Consultation|Integrated Repair Strategy|strategy_delta|consultation_status|orchestrator|iteration|human gate" \
  src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md \
  src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md \
  src/spec_dock/assets/spec_dock/templates/discussions/pr-repair-batch.md

if rg -n \
  "Default autonomous repair limit|Default total autonomous repair limit|Loop limits.*repair attempts" \
  src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md \
  src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md \
  src/spec_dock/assets/spec_dock/templates/discussions/pr-repair-batch.md; then
  echo "obsolete fixed-limit template contract remains" >&2
  exit 1
fi
```

### S04 完了ゲート

- 3つのプロバイダーテンプレートすべてが肯定テストと否定テストを満たす。
- 成果物テンプレートとディスカッションテンプレートの一致が解決済みである。
- ランタイムの不透明性とメタデータ互換性が維持されている。
- 安全でない出力欄がない。
- 統合したS03とS04の焦点契約テストがプロバイダーソースに対してGreenである。

---

# S05 — プロバイダーからドッグフーディングへの統合と互換性

### S05 目標

現在のチェックアウトを用いる標準更新経路で生成済み投影とインストール済み投影を更新し、プロバイダーとの同等性を検証し、焦点を絞った回帰検査と静的検査を実行し、スコープ外の面が変更されていないことを証明する。

### 依存関係

- Depends on: S03 and S04 exit gates。
- Unblocks: S90。

### 許可するパス

- 統合修正に限り、3つのテストファイル。
- テストで見つかった欠陥を修正するためのS03/S04のプロバイダーファイル。
- 標準更新コマンドによって生成される生成済み・ドッグフーディング投影パス。

### 禁止する操作

- テストを通すためにミラーを手作業で編集すること。
- ランタイムまたは観測の変更を導入すること。
- ユーザーが作成した`spec-dock/initiatives/**`の内容を上書きすること。

### 委任契約

| 項目 | 契約 |
|---|---|
| 委任するロール | `dev-coder` |
| 目標 | 更新、一致確認、テスト統合を実行し、契約を維持する修正だけを行う |
| 許可するパス | テストファイル、S03とS04のプロバイダーファイル、標準更新による生成済み投影 |
| 禁止するパス | ランタイム、観測、GitHubの変更、仕様権限 |
| 必須入力 | 先行する全手順の証拠、プロバイダー変更一覧、現在のチェックアウトで使う更新コマンド |
| 必須出力 | 更新ログ、投影差分、焦点テストと対象全体テスト、静的検査結果、一致マトリクス |
| 停止条件 | 更新が無関係なユーザー作成データに触れる。投影に手動編集が必要になる。ランタイム変更が必要になる。広範な無関係の失敗が発生する |
| 証拠の記録先 | レポートのS05統合台帳 |

### 標準更新

現在のチェックアウトをプロバイダーとして使用する。

```bash
uvx --from . spec-dock update .
```

リポジトリポリシーがインストール済みコマンドの使用を要求する場合は、理由と正確なコマンドを記録する。プロバイダーソースを暗黙に切り替えてはならない。

### 投影の同等性検査

```bash
cmp -s \
  src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md \
  .agents/skills/github-pr-merge-preparer/SKILL.md

cmp -s \
  src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/agents/openai.yaml \
  .agents/skills/github-pr-merge-preparer/agents/openai.yaml

cmp -s \
  src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md \
  .agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md

cmp -s \
  src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md \
  spec-dock/templates/artifacts/pr-repair-batch.md

cmp -s \
  src/spec_dock/assets/spec_dock/templates/discussions/pr-repair-batch.md \
  spec-dock/templates/discussions/pr-repair-batch.md
```

実際のインストール配置で対象パスが異なる場合は、リポジトリの証拠を記録してからパスを更新する。同等性検査を弱めてはならない。

### 焦点テスト

```bash
uv run pytest -q \
  tests/cli_runtime/test_new.py::<new_generated_contract_test> \
  tests/cli_runtime/test_runtime_new_doc_s09.py::<new_runtime_opaque_test> \
  tests/cli_runtime/test_wrappers.py::<new_installed_projection_test>

uv run pytest -q \
  tests/cli_runtime/test_new.py::TestCliNew::test_new_artifact_full_direct_catalog_success \
  tests/cli_runtime/test_runtime_new_doc_s09.py::TestRuntimeNewDocS09::test_doc_type_parity_template_selection_regression \
  tests/cli_runtime/test_wrappers.py::TestCliRulesContract::test_scaffold_docs_point_to_runtime_commands_and_rules_docs
```

### 対象ファイルのテストスイート

```bash
uv run pytest -q \
  tests/cli_runtime/test_new.py \
  tests/cli_runtime/test_runtime_new_doc_s09.py \
  tests/cli_runtime/test_wrappers.py
```

### 変更したPythonテストの静的検査

```bash
uv run ruff format --check \
  tests/cli_runtime/test_new.py \
  tests/cli_runtime/test_runtime_new_doc_s09.py \
  tests/cli_runtime/test_wrappers.py

uv run ruff check \
  tests/cli_runtime/test_new.py \
  tests/cli_runtime/test_runtime_new_doc_s09.py \
  tests/cli_runtime/test_wrappers.py

uv run mypy \
  tests/cli_runtime/test_new.py \
  tests/cli_runtime/test_runtime_new_doc_s09.py \
  tests/cli_runtime/test_wrappers.py
```

### 具体的なテストケース

#### TC-S05-001 更新時の維持

- 前提条件: 安全に実行できる範囲で、ユーザーが作成した進行中Issueのパスとハッシュのスナップショットを取得する。
- 操作: 現在のチェックアウトから更新を実行する。
- アサーション:
  - 意図したミラーが更新されている。
  - ユーザーが作成したIssueと成果物の内容が書き換えまたは削除されていない。
  - 予期しないパスの増加がない。
- 反証感度: 更新前後の一覧とgit差分を比較する。

#### TC-S05-002 プロバイダーとミラーの一致

- 操作: すべての `cmp -s` 検査を実行する。
- 期待結果: 終了ステータスが0である。
- 失敗時: 更新元とプロバイダー権限を検査し、ミラーだけをパッチしてはならない。

#### TC-S05-003 対象全体の回帰

- 操作: 3つのテストモジュール全体を実行する。
- 期待結果: 新たにスキップされる契約テストがなく、すべて合格する。

#### TC-S05-004 静的品質

- 操作: 変更したテストにruffのformat/checkとmypyを実行する。
- 期待結果: 合格する。列挙したファイルにPython差分がない場合は、リポジトリに基づく変更不要の理由を記録する。

#### TC-S05-005 スコープ外差分

- 操作: スコープガードと `git diff --stat`/`--name-only` を実行する。
- 期待結果: 許可されたプロバイダー、テスト、生成物のパスと、メインオーケストレーターが所有する正規Issue文書だけである。

#### TC-S05-006 安全なペイロード走査

- 操作: 変更したMarkdownとYAMLについて、ホストの絶対パス、認証情報の値の入力を促すプレースホルダー、モデルとの会話の生記録の収録、禁止された権限の主張を走査する。
- 期待結果: 明示的な禁止または説明を除き、該当がない。

推奨する走査:

```bash
python - <<'PY'
from pathlib import Path
import re
paths = [
    Path("src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md"),
    Path("src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/agents/openai.yaml"),
    Path("src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md"),
    Path("src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md"),
    Path("src/spec_dock/assets/spec_dock/templates/discussions/pr-repair-batch.md"),
]
unsafe = {
    "raw_transcript_slot": re.compile(r"(?i)(paste|attach|include).*verbatim model conversation record"),
    "authority_claim": re.compile(r"(?i)(chatgpt).*(authoriz|approve|fresh reviewer approval|merge-ready)"),
}
failures = []
for path in paths:
    text = path.read_text(encoding="utf-8")
    for code_span in re.findall(r"`([^`]+)`", text):
        if code_span.startswith("/") or re.match(r"^[A-Za-z]:[\\/]", code_span):
            failures.append((path.as_posix(), 0, "host_absolute_path", code_span))
    for name, pattern in unsafe.items():
        for match in pattern.finditer(text):
            # Explicit prohibition text must be manually dispositioned rather than blindly failed.
            line = text.count("\n", 0, match.start()) + 1
            failures.append((path.as_posix(), line, name, match.group(0)))
for row in failures:
    print(*row, sep=":")
PY
```

禁止文自体が一致する可能性があるため、手動での判断を必須とする。実際に安全でない例や値を残してはならない。

### S05 完了ゲート

- ユーザーデータを損なわずに標準更新が完了している。
- プロバイダーとミラーの一致検査に合格している。
- 焦点テストと対象テストモジュール全体が合格する。
- 静的検査に合格しているか、正当な変更不要の証拠がある。
- スコープ外の差分がない。
- CLOS-001..CLOS-013のすべてについて、レポート検証に使用できる実装とテストの証拠候補がある。

---

# S90 — 文書、スキル、テンプレート、ミラーへの影響解消

### S90 目標

最終レビュー前に、影響するすべての面を解消する。S90は一般的な文書整理ではない。永続的なポリシーが正しい所有元にあり、古い重複が残っていないことを証明する。

### 依存関係

- Depends on: S05 exit gate。
- Unblocks: S95。

### 委任契約

| 項目 | 契約 |
|---|---|
| 委任するロール | `docs-researcher` またはメインオーケストレーターによる読み取り専用監査 |
| 目標 | 旧制限へのすべての参照を一覧化し、所有元とミラーの配置を検証する |
| 許可するパス | リポジトリ全体を読み取り専用とする。確立済みのプロバイダー面を除き、編集には計画の修正が必要 |
| 禁止するパス | 無関係な文書の書き換え |
| 必須出力 | スキル、文書、テンプレート、テスト、ミラーの影響マトリクス、旧マーカー検索、変更しない面ごとの変更不要の根拠 |
| 停止条件 | 計画対象外のファイルに永続的な旧ポリシーがある。一般文書の権限を変更する必要がある。スキル横断ポリシーが見つかる |
| 証拠の記録先 | レポートのS90影響表 |

### S90 検査

```bash
rg -n \
  "Default autonomous repair limit|Default total autonomous repair limit|Fix loop limits|Loop limits.*repair attempts|root_cause_family.*repair commit" \
  src .agents spec-dock tests \
  --glob '!spec-dock/initiatives/**/artifacts/**' \
  --glob '!spec-dock/initiatives/**/discussions/**' \
  --glob '!spec-dock/initiatives/**/report.md'
```

履歴証拠には旧文言を正当に残せる。現在の規範ファイルや投影ファイルには残してはならない。

次を実行する。

```bash
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync
```

次を確認する:

- スキルが運用ポリシー全体を所有する。
- テンプレートに証拠欄があり、スキルと矛盾しない。
- 一般文書への重複記載が不要である。
- `openai.yaml` が簡潔なままである。
- プロバイダーとドッグフーディングのパスが現在も一致している。
- 実際の採用後、正規IssueレポートにEALと計画済み・観測済みの区別がある。

### S90 判断マトリクス

| 対象 | 期待する判断 |
|---|---|
| `github-pr-merge-preparer/SKILL.md` | 変更する。ワークフロー権限を持つ |
| `openai.yaml` | 変更する。簡潔なプロンプトに整合させる |
| スキルローカルテンプレート | 変更する。完全な運用ワークシートを持つ |
| 成果物テンプレートとディスカッションテンプレート | 変更する。生成される証拠欄を持つ |
| `github-pr-observation` | 変更しない。収集専用の性質を維持する |
| 一般ワークフロー文書 | S90で有効な矛盾する権限が見つからない限り変更しない |
| ランタイムCLIと文書 | 変更しない |
| 過去のIssue成果物 | 書き換えない |
| ドッグフーディングコピー | 生成によって更新し、一致させる |

### S90 で発見した回帰テストの計画修正

S90の旧マーカー監査で、`tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_105_pr_merge_preparer_content_regression_contract` が廃止対象のP0/P1/合計固定上限を肯定アサートしていることを発見した。このテストは履歴文書ではなく現在のprovider authorityを直接検証するため、旧文言を残す正当な履歴証拠ではない。

- 許可変更: `tests/unit/infra/test_init_update.py` の当該テストだけ。
- delegated role: `dev-coder`。
- 変更内容: 数値上限と再発だけの停止アサーションを、新しい相談ゲート、strategy delta、telemetry-only、再分析、既存hard gate維持のアサーションへ置換する。
- 禁止事項: 既存のpermission/auth、external/flaky、base conflict、scope/requirement expansion、migration、secret/deployment、ambiguous intent、platform-only、禁止GitHub操作のアサーションを弱めない。
- Red: 現在の旧アサーションが新providerに対して失敗することを確認する。
- Green: 当該node ID、`ruff format --check`、`ruff check`、`mypy`を実行する。
- 証拠の記録先: `report.md`のS90影響表とClosure Delta。

この追加は既存provider契約テストの追随であり、runtime、observation、GitHub、一般文書へスコープを拡大しない。

### S90 完了ゲート

- 有効な古い固定制限の権限が残っていない。
- 影響を受ける面と変更しない面のすべてに理由がある。
- validateとsyncの合格を観測している。
- IssueまたはEpicを横断する新しいポリシー要件が現れていない。
- 現れた場合は停止し、S95の前に計画を修正するかIssueを分割する。

---

# S95 — 独立レビューゲート

### S95 目標

仕様から実装までの全体について新鮮で独立したレビューを受け、通過を先取りせず、すべての所見を処理する。

### 依存関係

- Depends on: S90 exit gate。
- ブロック解除先: すべてのブロッキング所見が解決され、再レビューされた後に限りS99。

### レビュー契約

#### S95-A 新鮮な仕様レビュー

| 項目 | 契約 |
|---|---|
| ロール | `spec-reviewer` |
| モード | 読み取り専用、新鮮なコンテキスト |
| 入力 | 正規の要件・設計・計画・レポート、親Epic、実際の差分、テスト計画・証拠 |
| 焦点 | Issue境界、決定権、相談範囲、意味に基づく終了、AC・DES・完了追跡、計画の完全性 |
| 禁止事項 | ファイルを編集すること、またはこのパックを正規文書として扱うこと |
| 出力 | 判定、重大度別の所見、証拠参照 |
| ゲート | リポジトリのワークフローが求める新鮮な合格。非合格はブロッキング |

#### S95-B コードとテストのレビュー

| 項目 | 契約 |
|---|---|
| ロール | `code-reviewer` |
| モード | 読み取り専用 |
| 入力 | プロバイダー・テスト・生成済みの差分とテスト出力 |
| 焦点 | テスト感度、プロバイダー・ミラーの権限、ランタイムの逸脱がないこと、保守性、意図しない弱体化 |
| 出力 | 重大度別の所見と正確なパス・行 |
| ゲート | P0/P1を解決し、P2/P3をリポジトリポリシーに従って対応判断済みにする |

#### S95-C QAと契約のレビュー

| 項目 | 契約 |
|---|---|
| ロール | `qa-reviewer` |
| 焦点 | 生成済み成果物、旧来との互換性、否定マーカー、強制ゲートの維持、安全な出力 |
| 出力 | シナリオマトリクスと不足点 |
| ゲート | ブロッキングとなるシナリオの不足を解決する |

### 所見の取り扱い

- 生の所見を場当たり的に修復しない。
- 所見を一覧化し、根本原因ごとにまとめる。
- 変更がプルリクエスト引き渡し中にブランチを変更するブロッキング修復である場合、その段階では新たに定義したmerge-preparer相談ポリシーを適用する。
- 計画・仕様の所見は、正規の意思決定台帳・EALで対応判断する。
- 要件・設計を変更した場合は適切な段階に戻り、古い後続レビューを無効にする。

### S95 完了ゲート

- 新鮮な仕様レビュー状態がリポジトリの昇格規則を満たす。
- コード・QAのブロッキング所見が解決され、再レビューされている。
- 未解決の`needs-human`またはスコープ拡張の所見がない。
- レポートは過剰な主張をせずにレビュー証拠を記録する。

---

# S99 — 最終品質・完了監査

### S99 目標

最終差分に対して最終検証ラダーを実行し、完了、索引、証拠を整合させ、人間の判断に供する明示的な終了判断を作成する。

### 依存関係

- Depends on: S95 exit gate。

### S99 コマンド

#### 1. Focused contract tests

```bash
uv run pytest -q \
  tests/cli_runtime/test_new.py::<new_generated_contract_test> \
  tests/cli_runtime/test_runtime_new_doc_s09.py::<new_runtime_opaque_test> \
  tests/cli_runtime/test_wrappers.py::<new_installed_projection_test>
```

#### 2. Full target modules

```bash
uv run pytest -q \
  tests/cli_runtime/test_new.py \
  tests/cli_runtime/test_runtime_new_doc_s09.py \
  tests/cli_runtime/test_wrappers.py
```

#### 3. ランタイム回帰レーンまたは根拠を示したより広いベースライン

```bash
uv run pytest tests/cli_runtime
```

加えてS90で発見したprovider回帰契約を実行する。

```bash
uv run pytest -q \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_105_pr_merge_preparer_content_regression_contract
```

検証済みの無関係な既存障害により完全なランタイムレーンを実行できない場合は、正確な失敗、ソース証拠、対象を絞った完了判定がなお有効な理由を記録する。リポジトリで承認された判断なしにゲート通過と呼んではならない。

#### 4. Static checks

```bash
uv run ruff format --check \
  tests/cli_runtime/test_new.py \
  tests/cli_runtime/test_runtime_new_doc_s09.py \
  tests/cli_runtime/test_wrappers.py \
  tests/unit/infra/test_init_update.py

uv run ruff check \
  tests/cli_runtime/test_new.py \
  tests/cli_runtime/test_runtime_new_doc_s09.py \
  tests/cli_runtime/test_wrappers.py \
  tests/unit/infra/test_init_update.py

uv run mypy \
  tests/cli_runtime/test_new.py \
  tests/cli_runtime/test_runtime_new_doc_s09.py \
  tests/cli_runtime/test_wrappers.py \
  tests/unit/infra/test_init_update.py
```

#### 5. Dogfooding gates

```bash
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync
```

#### 6. Provider/mirror parity

最終修正後にS05の`cmp -s`検査をすべて再実行する。

#### 7. 禁止マーカー・維持マーカーの監査

```bash
if rg -n \
  "Default autonomous repair limit|Default total autonomous repair limit|Loop limits.*repair attempts" \
  src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer \
  src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md \
  src/spec_dock/assets/spec_dock/templates/discussions/pr-repair-batch.md \
  .agents/skills/github-pr-merge-preparer \
  spec-dock/templates/artifacts/pr-repair-batch.md \
  spec-dock/templates/discussions/pr-repair-batch.md; then
  echo "obsolete fixed-limit contract remains" >&2
  exit 1
fi

rg -n \
  "ChatGPT Consultation|Integrated Repair Strategy|strategy_delta|consultation_status|orchestrator|telemetry|human gate" \
  src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer \
  src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md \
  src/spec_dock/assets/spec_dock/templates/discussions/pr-repair-batch.md
```

#### 8. Diff hygiene and scope

```bash
git diff --check
git status --short --branch
git diff --stat
git diff --name-only
```

変更したすべてのパスを第3節と照合してレビューする。

### S99 完了監査

各`CLOS-*`行について:

- 計画されたテスト・検査が存在する。
- 観測結果がレポートにある。
- ソース・差分・テスト・レビュー担当者の証拠が一致する。
- 後続変更後に古いレビューが残っていない。
- 未解決のブロッカーや未レビューの計画修正がない。

### S99 変更不要時の規則

実装時に、現在のローカルブランチがこの設計の一部または全部をすでに満たしていると判明した場合:

- 意味のない差分を作らない。
- 欠けている回帰感度だけを強化する。
- 変更不要の証拠と正確な現在のソースを記録する。
- それでも互換性、決定権、ミラー、レビュー、最終の各ゲートを実行する。

### S99 完了ゲート

- 必須のテスト・静的検査・validate・sync・一致・差分検査のすべてに観測済みの対応結果がある。
- すべての完了項目が解決済みまたは明示的にブロックされており、暗黙に省略されたものがない。
- 最終レポートで計画証拠と観測証拠を分ける。
- 禁止された決定権の主張がない。
- ユーザーが承認した外部デリバリーワークフローを超えるGitHubの変更がない。

## 10. 検証段階

最も狭い範囲から広い範囲の順に実行する。下位段階の失敗がある場合、上位段階の成功を主張してはならない。

| 段階 | 範囲 | 例 | 目的 |
|---|---|---|---|
| V0 | ソースの紐付け | ハッシュ・パス・旧マーカーの棚卸し | 古いコンテキストの防止 |
| V1 | 単一テスト | 各新規テストノード | 迅速なRed/Green |
| V2 | 対象を絞った契約セット | 3つの新規テストと既存の近接テスト | 面をまたぐ振る舞い |
| V3 | 対象モジュール | 3つのファイル全体 | 影響を受けるレーンの回帰検査 |
| V4 | 静的検査 | ruff/mypy | テストコードの品質 |
| V5 | 投影 | 更新とcmp | プロバイダー・ミラーの一致 |
| V6 | ドッグフーディング | validate/sync | ワークスペースの一貫性 |
| V7 | より広いランタイムレーン | `pytest tests/cli_runtime` | 隣接領域の回帰検査 |
| V8 | レビュー | 仕様・コード・QA | 意味と実装の監査 |
| V9 | 最終差分・完了 | S99 | 全体の完結 |

## 11. 契約、互換性、復旧、ロールバックのゲート

### 11.1 契約ゲート

次をすべて満たす場合にのみ契約ゲートを通過させる。

- 現在有効なすべての面に数値試行の決定権がない。
- 相談・対応判断・戦略差分が存在し、整合している。
- 再発だけでは自動停止しない。
- 強制ゲートを維持する。
- ChatGPTの決定権は証拠の提示だけにとどまる。

### 11.2 互換性ゲート

- CLIオプション・パーサー・スキーマを変更しない。
- 生成されるファイル名・front matter・型を変更しない。
- 旧バッチを引き続き読み取れる。
- 新しいフィールドはMarkdownだけであり、追加に対する互換性がある。
- 更新によってユーザー作成の内容が上書きされない。

### 11.3 回復ゲート

スキルとテンプレートは次を明示的に処理しなければならない。

- 観測が古い場合 -> 再観測する。
- 相談が古い場合 -> 更新する。
- 相談が古い場合 -> まず更新する。回復不能な更新失敗の場合に限り、フォールバック承認へ進める。
- unavailable/failed/consultation_denied/unsafeの場合 -> デフォルトで人間ゲートとする。有効なDES-011のローカル限定フォールバックだけを例外とする。
- fallback_approval_denied/expired、スコープ不一致、再利用の場合 -> 絶対的な人間ゲートとする。
- 戦略差分がない場合 -> 人間ゲートとする。
- スコープ拡張の場合 -> 計画修正または人間ゲートとする。

### 11.4 ロールバックゲート

最終完了前に次を確認する。

- プロバイダーの変更を移行なしで戻せる。
- 更新によってプロバイダーからミラーを復元できる。
- 過去のバッチを削除・書き換える必要がない。
- 新しい永続状態が存在しない。

## 12. 委任ポリシー

### 12.1 一般規則

- メインオーケストレーターは、正規文書、EAL、スコープ判断、最終統合の所有権を保持する。
- ワーカーには、許可パスとテストを明示した境界付きの1手順を割り当てる。
- ワーカー出力は証拠であり、差分とテストを検査するまでは受け入れ済みの実装ではない。
- どのワーカーも`.assurance.json`、GitHubのレビュー状態、マージ状態、Issueライフサイクル、正規の決定権を独立して変更してはならない。
- 並列委任を許可するのは、S02のRed後にS03とS04の重複しないパスを扱う場合だけであり、統合は直列のままとする。

### 12.2 ワーカー引き渡しの最小項目

すべての委任タスクに次を含めなければならない。

- Issue、手順、完了のID。
- 目的と非目的。
- 正確な許可パスと禁止パス。
- ソース契約とID。
- 期待するRedとGreenの振る舞い。
- 正確なテストコマンド、または実行前に解決するプレースホルダー。
- 必須出力: 差分要約、テスト、不確実性、変更不要の証拠。
- 停止条件とエスカレーション条件。
- レポート証拠の記録先。

### 12.3 ワーカー受け入れチェックリスト

- [ ] 許可されたパスだけを変更した。
- [ ] スコープや要件を再解釈していない。
- [ ] 意図したテスト証拠を示した。
- [ ] アサーションを弱めていない。
- [ ] 不確実性、変更不要、制約を開示した。
- [ ] 決定権、GitHub、保証設定を変更していない。

## 13. レポート証拠の対応付け

ローカル統合判断後、`report.md`の次の欄に観測証拠を記録する。

| レポートのセクション | 必須の観測証拠 |
|---|---|
| ソースの結び付け | ブランチ、HEAD、状態、ファイルハッシュ、プロンプトパックの新鮮さ |
| 判断台帳 | ローカル統合結果の解釈、相談範囲、計画修正の有無 |
| EAL | 各調査、インタビュー、ChatGPT、統合結果への判断 |
| S01 | 基準テストと旧マーカー一覧 |
| S02 | 意図したRedと反証の説明 |
| S03 | スキルとプロンプトの差分、プロバイダーに焦点を絞ったGreen、維持された強制ゲート |
| S04 | テンプレート差分、生成物のGreen、同等性と安全な出力の証拠 |
| S05 | 更新ログ、プロバイダーとミラーの比較、対象テスト、静的検査、スコープ差分 |
| S90 | 影響マトリクス、validate/sync、古い決定権がないこと |
| S95 | レビュー担当者の判定、所見、修正、再レビュー |
| S99 | 最終コマンド、作業ツリー差分の範囲、完了マトリクス、残存リスク |
| ロールバック | テストまたは検査済みのロールバック経路と移行不要の証拠 |

ワーカーの生のメモ、モデルとの会話の生記録、機密情報、ホストローカルのパスをレポートへ貼り付けてはならない。

## 14. 計画修正と停止規則

### 14.1 必須の計画修正

次の場合は現在の手順を停止し、要件、設計、計画を更新する。

- ローカルで採用済みの統合結果が異なる必須相談境界を定義している。
- ランタイム、CLI、スキーマ、観測の変更が必要である。
- 公開テンプレート、フロントマター、ファイル名に新しい振る舞いが必要である。
- P2/P3または強制ゲートのポリシーを変更する必要がある。
- 計画外の永続的な面に有効な旧制限の決定権が存在する。
- 過去のバッチの移行が必要である。
- スキル横断ポリシーが必要である。
- セキュリティまたはプライバシーへの影響が、防護済みまたはなしから、ありまたは不明へ変わる。

### 14.2 即時の人間ゲート

- 相談にシークレット、認証情報、非公開データが必要である。
- ブロッキング変更が保留中で、相談が利用不能、失敗、拒否、または安全でない状態である。
- 要件またはレビュー意図が曖昧、もしくは競合している。
- 現在の権限外のGitHub変更である。
- 破壊的、または安全にロールバックできない変更である。
- 実質的な差分なしに同じ無効な戦略が提案されている。
- ワーカーが禁止パスまたは正規の決定権を変更した。

### 14.3 計画が古くなるトリガー

- 要求されたブランチまたはmainが、結び付けたHEADから実質的に変わる。
- ソースマニフェストのハッシュが変わる。
- この実行外で対象ファイルのハッシュが変わる。
- 親Epicまたはリポジトリの決定権ルールが変わる。
- ローカル成果物の本文によって前提が無効になる。
- 計画レビュー後にレビュー担当者が要件または設計を変更する。

## 15. 最終品質ゲート

最終品質ゲートはテストだけでは満たされない。次を必要とする。

1. 要件、設計、計画のトレーサビリティが完全である。
2. すべてのCLOS項目に観測証拠がある。
3. リポジトリワークフローに基づく新鮮なレビュー状態がある。
4. プロバイダー、ミラー、生成済み契約が同等である。
5. 旧来の固定制限に決定権がない。
6. 強制ゲートまたはP2/P3ポリシーを弱めていない。
7. ランタイム、観測、GitHub、保証のスコープを拡大していない。
8. 出力が安全であり、モデルとの会話の生記録、シークレット、ホストパスがない。
9. 互換性、ロールバック、移行不要の証拠がある。
10. 最終差分と変更のある作業ツリーの範囲を把握している。

## 16. 最終完了契約

### 16.1 成功時の結果

後続の実行とレビューを経て、人間またはオーケストレーターは、次のすべてが観測された場合にのみ実装完了と判断できる。

- 固定された数値試行上限が、現在の決定元と投影から除去されている。
- 再発は再分析のトリガーであり、自動停止ではない。
- 必須の統合相談、または1回の呼び出しに限る明示的なフォールバックと、証拠に限る判断が明記されている。
- 意味に基づく継続と人間ゲートのポリシーが完全かつ安全である。
- バッチテンプレートが監査可能で互換性を保っている。
- 対象、広範囲、静的、ドッグフーディング、同等性の各ゲートに受け入れ済みの結果がある。
- リポジトリワークフローに基づく新鮮なレビューに受け入れ済みの結果がある。
- 禁止操作や決定権の拡大が発生していない。
- レポートに完全な観測証拠と残存リスクが記載されている。

この結果だけでPRをマージしたりIssueを完了したりすることはない。それらは引き続き外部で認可される操作である。

### 16.2 ブロック時の結果

次のいずれかが残る場合は、正確な証拠を添えてブロックまたは人間ゲートの結果を返す。

- ソースまたはローカル統合結果が一致しない。
- 相談契約が曖昧である。
- ブロッキングレビューまたはテスト失敗が未解決である。
- プロバイダーとミラーにずれがある。
- スコープ外の差分がある。
- データの取り扱いが安全でない。
- レビュー、保証、採用に関する判断が欠けている。
- ブロッキング修復に実行可能で実質的に異なる戦略がない。

### 16.3 禁止する早すぎる終了ラベル

計画上の証拠に次のラベルを付けてはならない。

- 採用済み / 正規
- 実装引き渡し適格
- レビュー合格済み
- プルリクエスト引き渡し適格 / マージ準備済み
- 納品済み
- 認可済みプロファイル

## 17. 後続候補

| 後続候補 | トリガー | 関係 |
|---|---|---|
| ChatGPT相談アダプターまたはランタイム | ホストでの手動相談が運用上のボトルネックになる | 別のランタイムまたはネットワークIssue |
| 修復バッチの機械検証 | この契約後にもMarkdownのずれが再発する | 別の検証Issue |
| スキル横断の再試行または相談ADR | 複数の無関係なスキルにポリシーが必要になる | EpicまたはADR候補 |
| 観測スキーマの拡充 | 現在の証拠では新鮮さを安全に結び付けられない | 別の観測契約Issue |
| 旧バッチ移行ツール | 使用中の旧バッチを追記再開できない | 別の移行Issue |

現在の正規スコープでiss-00313の一貫性を保つために必須となる候補はない。

## 18. 計画承認チェックリスト

これらのチェックボックスは意図的に未チェックとしている。

### 採用

- [x] プロンプトパックのEAL判断を完了した。
- [x] ローカル統合結果の前提を確認した。
- [x] メインオーケストレーターが正規の要件、設計、計画を作成した。

### プロファイルとレビュー

- [x] 実際の保証およびプロファイルのワークフローを完了した（`standard`）。
- [x] 新鮮な要件レビューに合格した。
- [x] 新鮮な設計レビューに合格した。
- [x] 新鮮な計画レビューに合格した（記録管理だけに関する条件付き所見を解消済み）。

### このパック外の実行準備ゲート

- [x] ソースの結び付けが最新である（assurance classify / verify `valid`）。
- [x] 作業ツリーの所有権が明確である。
- [x] 手順のコマンドを実際のテストノード名に解決している。
- [x] レポートの証拠欄を用意している。
- [x] ブロッカーや古い入力がない。

追加要求はfresh named `spec-reviewer` passとassurance `valid`を得ており、S100-T以降を実行できる。

## 19. 追加実装ステップ: agent runtime profile固定値の除去

### S100 provider契約・投影

- 担当: `utility-worker`。`dev-coder`のHard ruleによりagent configは担当させない。
- 変更対象: 4ロールのprovider Codex/GitHub agent設定と対応するdogfooding投影。
- 代替証拠: 現行固定値の存在を`rg`でcharacterizationし、変更後は同じ走査が対象4ロールで0件になることを確認する。
- 完了条件: Codexの`model` / `model_reasoning_effort`、GitHubの`model` / `Reasoning profile` / `Target depth`が消え、provider↔dogfoodingがbyte-identicalになる。
- Closure: CLOS-017。
- Report destination: `追加要求の実行台帳`。

### S100-T 回帰テスト更新

- 担当: `dev-coder`。
- 実行時起動: `codex exec -m gpt-5.6-sol -c 'model_reasoning_effort="medium"' -s workspace-write -C <repo> <orchestrator-prompt>`で親sessionを起動し、親から`spawn_agent(agent_type="dev-coder")`を呼ぶ。
- 変更対象: `tests/unit/infra/test_init_update.py`だけ。
- Red: 対象4ロールを固定profile期待値から除外し、不在契約を追加する前に、変更済みproviderに対して旧期待値がfailすることを確認する。
- Green: `uv run pytest -q tests/unit/infra/test_init_update.py::TestInitUpdate::test_s04_codex_agent_permission_taxonomy_contract tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets`。
- 完了条件: 対象4ロールの固定値不在と非対象profile維持を同じtestで検証し、parity testがpassする。
- Closure: CLOS-017、CLOS-018（実行時profile証拠）。
- Report destination: `追加要求の実行台帳`。

### S101 追加変更のレビュー

- `code-reviewer`: 設定・テスト差分と回帰リスクを確認する。
- `spec-reviewer`: AC-015/016、設計、実装、投影の一致を確認する。
- `qa-reviewer`: absence assertion、非対象ロール保護、parity検証の十分性を確認する。
- 各reviewerは実行時に`gpt-5.6-sol`、`medium`を指定し、failなら修正後にfresh reviewを行う。
- reviewer起動は`codex exec -m gpt-5.6-sol -c 'model_reasoning_effort="medium"' -s read-only -C <repo> <orchestrator-prompt>`を使い、親sessionから`spawn_agent(agent_type="code-reviewer"|"spec-reviewer"|"qa-reviewer")`を呼ぶ。親起動ログ、spawnした`agent_type`、role固有JSON outputをCLOS-018の証拠とする。

### S102 再検証・送達

- focused test、関連module、lint、full test、validate/sync、parity、diff hygieneを再実行する。
- 結果を`report.md`へ記録し、コミット・push後にPR #320のchecksとCodex reviewを再観測する。

### 追加Closure

| ID | Requirements | Design | Steps | Verification | Report evidence |
|---|---|---|---|---|---|
| CLOS-017 | AC-015 | DES-012 | S100, S100-T, S102 | absence assertions、非対象profile期待値、provider/dogfooding parity | 追加要求の実行台帳 |
| CLOS-018 | AC-016 | DES-012 | planning review, S100-T, S101 | 親起動ログのmodel/reasoning、named `agent_type`、role固有child output | 追加要求の実行台帳 |

Amendment trigger: 対象4ロール以外の固定値削除、permission/prompt contract変更、named role spawnまたは親runtime overrideのchild再適用を確認できない事実、またはfocused node名の不一致を観測した場合は停止して本計画を更新する。
