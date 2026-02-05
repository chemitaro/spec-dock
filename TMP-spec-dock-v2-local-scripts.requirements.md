# 要件定義書: v2 ローカルスクリプト運用への再設計（追加対応）

## 背景 / 問題
- `spec-dock` は `uvx spec-dock init` / `uvx spec-dock update` でテンプレート・ドキュメント・スクリプトを取得し、以降は **リポジトリ内のスクリプト**で日常運用する前提だった。
- 現在の v2 実装では、initiative/epic/issue/adr の作成、active の切り替え、sync/validate などの操作を **都度 `uvx spec-dock ...`** で実行する導線になっている。
- これは「毎回ネットワーク越しに取得したツールを起動する」ように見え、運用として望ましくない。
  - オフライン時の操作性が下がる
  - “導入後にローカルで完結する” という体験と乖離する
  - スクリプトが空になり、v1 の運用思想と不整合

## 目的（達成したいこと）
1. `uvx spec-dock` の役割を **導入（init）と更新（update）に限定**する  
   - `uvx spec-dock init` … `.spec-dock/` の scaffold を配置する
   - `uvx spec-dock update` … `.spec-dock/{docs,templates,scripts}` と skill を更新する
2. 日常の操作（仕様ツリー操作）は **ローカルスクリプト**で実行できるようにする  
   - initiative/epic/issue/adr 作成
   - active（今作業中）セット/表示/解除
   - sync（state 生成、任意で GitHub enrich）
   - validate（整合性チェック）
3. v2 仕様（階層ツリー常置・移動なし・小文字 ID）を維持する

## スコープ
### In scope
- `.spec-dock/scripts/` に “運用 CLI” を配置し、導入後はローカルで操作できるようにする
- `spec-dock init/update` が scripts を適切に配置・更新する
- ドキュメント（README / guide / skill）を「ローカルスクリプトを入口」に更新する
- テストを「init/update は uvx（=パッケージ CLI）」「運用はローカルスクリプト」に合わせて更新する

### Out of scope（今回やらない）
- GitHub Projects 連携（フィールド/進捗の書き込み等）
- GitHub Issue の作成・編集（読み取り enrich は optional）
- 既存 v1 レイアウト互換（ユーザー指定により **捨てる**）

## ユーザーストーリー
- 開発者として、`uvx spec-dock init` の後、ネットワークに依存せずに `.spec-dock/scripts/spec-dock` で仕様ツリーを操作したい
- コーディングエージェントとして、常に固定パス `.spec-dock/active/context-pack.md` から始められるようにしたい
- メタ情報（進捗集計）は手で更新したくない。`sync` で生成される状態を参照したい

## 受け入れ条件（Acceptance Criteria）
1. `uvx spec-dock init` 実行後、以下が成立する
   - `.spec-dock/scripts/spec-dock`（または同等のエントリ）が存在し、`python` で実行できる
   - `.spec-dock/initiatives/` が作成される
   - `.spec-dock/active/` と `.spec-dock/.work/` が作成される（git 管理外）
2. ローカルスクリプトで以下が動作する
   - `new initiative/epic/issue/adr` がテンプレートから作成できる
   - `active set/show/clear` が `.spec-dock/.work/current.json` と `.spec-dock/active/*` を更新する
   - `sync` が `.spec-dock/.work/state.json` を生成する（`--github` は `gh` があれば enrich）
   - `validate` が構造不整合を検出できる
3. README / guide / skill が “運用はローカルスクリプト” を前提に記述されている
4. 自動テストがパスする

## 制約 / 既定値（本タスクの前提）
- 仕様ツリー本体ルート: `.spec-dock/initiatives/`（Option A）
- 命名規則: `init-0001-<slug>` 等、**全て小文字**
- v1 互換: **なし（legacy を捨てる）**

