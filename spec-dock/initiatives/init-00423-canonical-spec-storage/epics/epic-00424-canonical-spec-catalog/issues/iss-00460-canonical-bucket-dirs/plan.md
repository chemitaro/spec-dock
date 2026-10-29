---
種別: 実装計画書（Issue）
ID: "iss-00460"
タイトル: "Bucket Canonical Catalog By Thousand"
関連GitHub: ["#460"]
状態: "draft"
最終更新: "2026-10-29"
依存: ["requirement.md", "design.md"]
親: ["epic-00424", "init-00423"]
---

# iss-00460 Bucket Canonical Catalog By Thousand — 実装計画

詳細: [Issue Plan Guide](../../../../../../docs/authoring/issue-plan.md)

## Planning Level

- **選んだ level**：standard（統括の指示と Epic の計画の I-16 の節）。
- **理由**：仕様が確定した、テストで確かめられる狭い直しである。変えるのは、場所を作る部品（純粋な関数1つと、それを呼ぶ3か所）と検査の判定で、カタログにも GitHub にも書かない。公開の形（C3）を変えるが、使う側（I-5、I-11、I-15）はまだマージされておらず、まだ作られたカタログもない。
- **risk factor**：I-15 の写しとの食い違い、場所を別々に作る箇所の取り残し、0埋めしない入力が通らない入口、従来モードの回帰（AC-15）。
- **再評価の条件**：Epic の契約（C1〜C11）の持ち主や使う側を変える必要が出たとき、従来モードのコードやテスト（`domain/selectors.py` を含む）を変える必要が出たときは、止まって統括に聞く。カタログのデータを書き換える処理（平らな置き場からの自動の移しなど）が要ることになったら strict に上げる。

## 目標

`requirement.md` の AC-460-01〜08 を満たす。canonical のカタログの Scope が `<カタログ>/<区切り>/<ID>/` に置かれ、0埋めしない ID の入力が通り、I-5 と I-11 が再開でき、I-15 が区切りの計算を写せる。

## 順序・依存

- 依存：なし（I-14 はマージ済み）。起点 `95bbb7a1c`、統括の雛形のコミット `fb61ca061`。
- 下の順に、内側（domain）から外側（application、CLI、文書）へ進める。1 の公開の形は、I-15 が読めるように、この計画書と同じコミットで `design.md` に書いてある。
- 並行：I-15（`iss-00456`）が同じ決まりで並べて進む。I-5、I-11 はこの Issue のマージを待つ。共有のファイル（`tests/support/*`、`cli/catalog.py` など）で衝突したら、`origin/main` をこのブランチにマージして解く（rebase しない）。

## 実装step

テスト駆動（Red → Green → Refactor）で、受け入れ条件ごとに進める。

1. **区切りの計算（AC-460-01、AC-460-05 の定数、AC-460-07）**：`tests/unit/domain/test_canonical_layout_buckets.py` を先に書き、`domain/canonical_layout.py` に `BUCKET_SIZE`、`BUCKET_NAME_SHAPE`、`SCOPE_TO_SPEC_DOCK`、`scope_bucket`、`scope_relative`、`is_bucket_name` を足す。
2. **カタログの区切り（AC-460-02、AC-460-03 の部品）**：`tests/unit/infra/test_catalog_tree.py` を区切りの形に書き直し（Red）、`CatalogTree` の `directories`、`find`、`misplaced` と `MisplacedDirectory.expected` を直す。
3. **読む側と検査（AC-460-02、AC-460-03）**：テストの部品 `CanonicalWorld.relative` を `<区切り>/<ID>` にし、`canonical_scopes.build_views` と `canonical_workspace` の `path`、メッセージ、次の1手を直す。置き場のパスを直書きしている canonical のテストを検索して直す。`tests/cli_runtime/test_issue460_bucket_dirs.py` に、区切りの置き場の CLI の確かめ（`scope show/list`、`active set`、`artifact list`、平らな残り、4つの外れ、付け替え）を足す。
4. **0埋めしない入力（AC-460-04）**：`test_issue460_bucket_dirs.py` に、入口ごとの0埋めしない入力のテストを足す。通らない入口があれば、`parse_scope_selector` を通すように直す。
5. **深さ（AC-460-05）**：一時のリポジトリの mainのチェックアウトと作業用のworktreeで、`<カタログ>/<区切り>/<ID>/` に置いた `../../../docs/…` と `artifacts/` の `../../../../docs/…` のシンボリックリンクが開くことを確かめるテストを足す。
6. **Epic の文書（AC-460-06）**：`requirement.md`、`design.md`、`plan.md` の置き場の記述を区切りの形に直し、`plan.md` に I-16 の節、一覧の行、順序の図の位置を足す。「直下の `<ID>/`」の検索で残りがないことを確かめる。
7. **掃除と全体（AC-460-07、AC-460-08）**：`src/spec_dock/runtime/` で `<ID>` を直接つないで場所を作る箇所が残っていないことを検索で確かめる。`make lint`、`uv run pytest`。変えたテストの一覧を `report.md` に書き、版3の振る舞いのテストを変えていないことを確かめる。

## 検証

| AC | 確かめ方 |
|---|---|
| AC-460-01 | 単体（`test_canonical_layout_buckets.py`）：`scope_bucket` の9つの例、0と負の数の `ValueError`、`scope_relative` の例と `iss-454`・`iss-000454`・`ISS-00454` の `ValueError`、種類によらないこと |
| AC-460-02 | CLI（`test_issue460_bucket_dirs.py`、直した `test_issue431_*`）：`path`、リンクの先、Artifact のパス。直下の平らな `<ID>/` だけの Scope の `path` が null |
| AC-460-03 | 単体（`test_catalog_tree.py`）と CLI（`workspace validate`、`canonical status --structure`）：4つの理由の外れ、`expected`、`MISSING` の `path`、付け替えが1件、正しく置いた Scope に異常がないこと、隠し・リンク・ファイルの無視 |
| AC-460-04 | CLI：入口ごとに `iss-454`（と `iss-000454`）を渡し、0埋めの ID とパスとブランチの名前が出ること。単体：名前の照合（`CatalogTree`、`branch_names_scope`）が `iss-454` を受け付けないこと（I-14 のテストのまま） |
| AC-460-05 | 単体：`SCOPE_TO_SPEC_DOCK` の正規化。CLI の部品（一時のリポジトリ）：mainのチェックアウトと作業用のworktreeで、相対リンクとシンボリックリンクが `spec-dock/docs/…` を開く。テンプレートの配布資産の差分がないこと（`git diff --stat`） |
| AC-460-06 | Epic の3つの文書の検索（「直下の `<ID>/`」「`<カタログ>/<ID>/`」「`initiatives/<ID>`」が置き場の記述として残らない）と、`plan.md` の I-16 の節。文書のレビュー（手順4） |
| AC-460-07 | 単体のテストが `design.md` の公開の形を直接使う |
| AC-460-08 | `make lint`、`uv run pytest` の全体。変えたテストがすべて canonical モードのもの（`report.md` の一覧） |

- negative test：区切りの境（999/1000、99999/100000）、区切りの名前の誤り、区切りの違う ID、I-14 の平らな残り、`ID` でない値の `ValueError`。`requirement.md` の「失敗・境界条件」の各項目は AC-460-01（境、0以下）、AC-460-02（平らな残り）、AC-460-03（区切りの違う ID、名前の誤り、付け替え、隠し・リンク・ファイル）で確かめる。
- 読むだけのコマンドが書かないこと：I-4 の `test_issue431_read_only.py` を区切りの置き場で通す。
- 変えずに通すテスト：版3の振る舞いのテストのすべてと、I-8 の移行のテスト（`tests/integration/migration/`）。

## rollback

- **revert の条件**：マージの後に、この Issue の変更が原因で canonical のテストか版3のテストが落ち、I-5、I-11、I-15 のどれもまだこの Issue を取り込んでいないとき。PR を `git revert` すれば戻る。利用者の運用への影響はない（canonical モードはまだ使われていない）。
- **forward recovery**：取り込んだ Issue があれば、revert せず、直す PR を出す（担当は統括が決める）。
- migration：N/A（作られたカタログがない）。

## security / privacy / operability

- security / privacy：N/A。新しい外部への送信も、書き込みもない。テストは外のネットワークを使わない。
- operability：置き場の外れは、理由と正しい場所（`expected`）と次の1手を示す。`iss-454` のような入力がそのまま通る。

## exit / handoff

- **完了の条件**：AC-460-01〜08 を満たし、最終品質ゲート（同じ SHA で `make lint` と `uv run pytest` の全体、独立した2つのレビュー）に合格し、PR の CI が通り、マージできる状態の PR がある。マージは人が行い、`work finish` は統括の指示の後。
- **引き渡し**：
  - I-5：`scope_relative`（作成、削除、`work finish` の保存の確認、`holds_under` に渡す接頭辞）、`SCOPE_TO_SPEC_DOCK`（作成時の相対リンクとシンボリックリンクの深さ）、`CatalogTree.find`、新しい ID の入口は `parse_scope_selector` を通すこと。`KindChange.directories` は名前のままで、場所は `scope_relative(名前)`。
  - I-11：場所を使わないので、変えるものはない（テストの部品の取り込みだけ）。
  - I-15：`scope_bucket` の本体を写し、マージの後にパッケージの関数と比べるテストを足す。平らにする写しの写し先は `<区切り>/<ID>/`、深さは `SCOPE_TO_SPEC_DOCK`。
- **残るリスク**：`report.md` に書く。
