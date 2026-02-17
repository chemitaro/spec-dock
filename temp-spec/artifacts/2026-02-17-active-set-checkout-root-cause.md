# active set の checkout 結合問題（`init-00002` 事象）分析レポート

## 1. 背景と目的
- 目的は、`./spec active set init-00002` 実行時に **ブランチだけ切り替わって active 設定が失敗**する事象の根本原因を特定し、設計改善方針（ベストプラクティス）を提示すること。
- あわせて、要望（デフォルトは checkout しない、ローカルノード優先、数値指定で未リンク時は副作用なしで失敗）に対して、既存実装との差分を整理する。

## 2. 入力情報
- ユーザー報告:
  - 実行前ブランチ: `main`
  - 実行コマンド: `./spec active set init-00002`
  - 実行後ブランチ: `2-codex-team-mcp`
  - エラー: `No node found for github.issue_number=2. Create/link the node first.`
- 対象ノード `meta.json`（要点）:
  - `type: initiative`
  - `id: init-00002`
  - `github.issue_number: 2`
- 合意済み希望仕様（ヒアリング結果）:
  - デフォルトは **checkout しない**（質問3: b）
  - 数値指定でローカルノード未解決なら **checkoutしない / activeも更新しない / エラー**
  - 解決優先順位は **ローカルノード優先**
  - GitHub からの自動 import はしない

## 3. 事実（観測結果）

### 3.1 実装上の事実（コード）
- `active set` の target 解釈:
  - 数値/`#123`/URL は `github_issue` 扱い（`src/spec_dock/assets/spec_dock/scripts/spec-dock:1304`）。
  - `init-xxxx` / `epic-xxxx` / `iss-xxxx` は `node_id` 扱い。
- `node_id` 指定でも、対象ノードが `github.issue_number` を持つと **自動 checkout 分岐**に入る（`src/spec_dock/assets/spec_dock/scripts/spec-dock:1803`）。
- checkout 後は target が `node_id` でも、再解決は `github.issue_number` 基準で行う（`src/spec_dock/assets/spec_dock/scripts/spec-dock:1818`, `1851`, `1863`）。
- `No node found for github.issue_number=...` は `_find_node_by_github_issue_number` の標準エラー（`src/spec_dock/assets/spec_dock/scripts/spec-dock:1278`）。
- `initiative` / `epic` / `issue` の active 設定自体は既に実装済み（`_select_active_from_node`、`src/spec_dock/assets/spec_dock/scripts/spec-dock:1253`）。

### 3.2 現行仕様（ドキュメント/テスト）
- 現行ドキュメントは「GitHubリンク対象の active set は checkout を伴う」と明記（`src/spec_dock/assets/spec_dock/docs/reference_github.md:46`、`src/spec_dock/assets/spec_dock/docs/guide.md:105`、`README.md:95`）。
- 既存テストでも「数値指定で未リンクでも checkout が先に走る」挙動を期待している（`tests/test_cli.py:1849`）。

### 3.3 事象の再構成（`init-00002`）
1. `target=init-00002` は `node_id` として解決。
2. ノードに `github.issue_number=2` があるため checkout 分岐へ。
3. `gh issue checkout 2` によりブランチ移動（報告では `2-codex-team-mcp`）。
4. checkout 後に再走査し、`github.issue_number=2` ノードを探索。
5. checkout 先ブランチに当該ローカルノードが無い/見えない場合、`No node found...` で失敗。
6. 失敗時も checkout 副作用は残る（元ブランチへ自動復帰しない）。

## 4. 仮説・検討メモ

### 4.1 根本原因（設計レベル）
1. **責務の結合**  
   `active set` が「active選択」と「ブランチ操作」を同時に担い、ユースケース（要件検討 vs 実装作業）の差を表現できない。
2. **副作用順序の問題**  
   特に数値指定で、ローカルノード確定前に checkout が走り得るため、失敗時に「中途半端な状態（ブランチだけ変更）」が残る。
3. **再解決キーの不整合**  
   `node_id` 指定後も checkout 後は `github.issue_number` で再解決しており、branch間差分に脆い。
4. **運用ポリシー不一致**  
   現行は「GitHubリンク=常にcheckout」寄り。要望は「initiative/epic の要件定義は main で進める（GitHub Flow）」。

### 4.2 ベストプラクティス方針（推奨）
- **方針A: ローカルSSOT先行・副作用後置（Fail-fast）**
  - まずローカルノード解決を完了し、未解決なら即エラー。
  - checkout は解決後にのみ実行（必要時のみ）。
- **方針B: active設定とcheckoutを分離可能にする**
  - `active set` はデフォルト `--no-checkout`。
  - 明示時のみ `--checkout` を実行。
- **方針C: 解決優先順位を固定**
  - 常にローカルノード優先（要望どおり）。
  - 数値指定で未リンクなら副作用なしで失敗。
- **方針D: ノード種別ごとの意図を尊重**
  - `initiative`/`epic`: 仕様整理フェーズを想定し、デフォルト非checkout。
  - `issue`: 実装フェーズで checkout を選べる（ただし明示的）。

### 4.3 推奨仕様（具体）
- CLI:
  - `./spec active set <target>` → デフォルト非checkout
  - `./spec active set <target> --checkout` → 明示的にcheckout
- 挙動:
  - `<target>` が数値系:
    - ローカルで `github.issue_number` 一意解決できなければ **即エラー**（checkoutしない）
  - `<target>` が node_id:
    - 指定 node を基準に active 決定
    - `--checkout` 指定時のみ checkout 実施
- 失敗時原則:
  - active manifest は未更新のまま
  - checkout 未実行ケースではブランチ無変更
  - （要検討）checkout後検証失敗時の元ブランチ自動復帰

### 4.4 実装影響箇所（見積り）
- 主変更:
  - `src/spec_dock/assets/spec_dock/scripts/spec-dock`（`_active_set`, 引数定義）
- テスト更新:
  - `tests/test_cli.py`
    - `test_active_set_github_issue_number_requires_linked_node` は期待値変更（checkout回数 1 → 0）
    - `--checkout` 明示時の新規テスト追加
    - `initiative` / `epic` の GitHubリンクノードを非checkoutで active 可能な回帰テスト追加
- ドキュメント更新:
  - `README.md`
  - `src/spec_dock/assets/spec_dock/docs/reference_github.md`
  - `src/spec_dock/assets/spec_dock/docs/guide.md`
  - 必要に応じて workflow 系 docs

## 5. 次アクション
- [ ] 設計決定: `active set` の正式CLIを `--checkout` opt-in にする（デフォルト非checkout）
- [ ] 実装: `_active_set` を「解決→（任意）checkout→active反映」の2段階に分離
- [ ] 実装: 数値指定未解決時は fail-fast（副作用ゼロ）
- [ ] テスト: 現行期待（checkout先行）を新仕様へ更新 + 追加テスト
- [ ] ドキュメント: checkout規約を新運用に合わせて改訂

## 確認したい事項（実装前）
- Q1. `--checkout` というフラグ名で確定してよいか（代替: `--with-checkout`）。
- Q2. `--checkout` 指定時に対象が `initiative` / `epic` でも checkout を許可するか（issue のみ許可に絞るか）。
- Q3. checkout 後に再検証で失敗した場合、元ブランチへ自動復帰する要件を入れるか。

## 運用メモ
- 本レポートは discussion 用の分析資料。実装着手時は本内容を `requirement/design/plan` に分解し、変更を段階適用する。
