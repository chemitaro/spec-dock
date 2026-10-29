---
種別: 実装計画書（Issue）
ID: "iss-00456"
タイトル: "Flatten Specs In Canonical Migration Script"
関連GitHub: ["#456"]
状態: "draft"
最終更新: "2026-10-29"
依存: ["requirement.md", "design.md"]
親: ["epic-00424", "init-00423"]
---

# iss-00456 Flatten Specs In Canonical Migration Script — 実装計画

詳細: [Issue Plan Guide](../../../docs/authoring/issue-plan.md)

## Planning Level

- **strict**（Epic の `plan.md` の Issue の一覧のとおり）。
- 理由：このスクリプトは、I-10 と I-12 で、5つのリポジトリの仕様のすべてを写し、GitHub に大量に書く。写しの誤り（リンクの切れ、履歴の不一致、入れ子に戻せない）は、切り替えの後に気づくと戻しにくい。
- risk factor：リンクの書き換えの誤り、履歴の作り直しの不一致（`adopt-worktree` の C が見つからない）、`export-legacy` が従来モードの検査を通らない、見つけ直しの重複。
- 再評価の条件：本物のリポジトリか本物の GitHub に書く必要が出たら、止まって統括に聞く（この Issue の範囲の外。`critical` の扱い）。

## 統括の判断（2026-10-29、Orca の `ask` の答え）

- **Q1 work start**：I-14（`iss-00455`）の `work finish` がまだで `READINESS_NOT_SATISFIED` になった。統括が I-14 の担当に頼み、#455 が閉じた後に `work start` した。
- **Q2 履歴の写し**：spec-dock の古いコミットには、平らにできないもの（`idmap.json` にないローカルの ID `init-local-00001`、`epic-local-00001`、`iss-local-00001`、1つのコミットで重なる `iss-00209`、`.meta.json` のない `epics/new-epic` などの仮置き。のべ727ファイル）がある。今の既定のブランチの木は、4つのリポジトリとも平らにできる。答えは A：履歴のコミットでは、平らにできる Scope だけを写し、できないパスはそのコミットからだけ落とし、落とした件数とパスの種類を出力に出す。先端と `adopt-worktree` の作業の状態に平らにできないものがあれば、一覧にして止める。理由：元のリポジトリの履歴は書き換えないので、落としたものは既定のブランチの履歴に残る。
- **Q3 HTML のリンク**（文書のレビューの指摘 P1-3 を受けて）：Epic の11章は書き換えるリンクを Markdown とシンボリックリンクに限るが、spec-dock の仕様のツリーには `.html` が34個あり、解決できる相対の `href`・`src` が77個、そのうち Scope をまたぐ9個は平らにすると切れる。答えは A：`.html` と `.htm` の `href` と `src` の相対のパスも、Markdown と同じ規則で書き換え、書き換えられないものは同じ一覧に入れる。予行演習の0件にも HTML を含める。理由：Epic の AC-04（移行の前に開けた仕様の中の相対のリンクが、移行の後も開ける）を満たすため。Epic の11章の文は、統括が次の Epic の文書の直しで書き足す。
- **区切りの計算**：幅 = max(5, 番号の桁数)、下端 = 番号 − 番号 mod 1000、上端 = 下端 + 999 は正しい。I-16 の `design.md`（`chemitaro/canonical-bucket-dirs` の `60ea01ccb`）の `scope_bucket`、`scope_relative`、`BUCKET_SIZE` と同じ値にし、I-16 のマージの後のテストで比べる。

## 文書のレビューの指摘の対応（独立のレビュー、2026-10-29）

| 指摘 | 判断 | 対応 |
|---|---|---|
| P1-1 読むだけの `plan` が本物の `.git` にオブジェクトを書くおそれ | 正しい（今の `plan` は対象のリポジトリを直接読む） | D6 を足し、`TreeFlattener` の `scratch=None` で書かずに oid をメモリーで求める。`plan` の前後で `count-objects` が変わらないテスト（AC-456-11） |
| P1-2 登録の前の `plan` がローカルの Scope を平らにできないと扱う | 正しい | `plan` は置き換えの予定で写し、新しく作る予定のものは仮の場所 `pending/<ローカルの ID>` に写して `data.flatten.pending` に示す（R-456-05、AC-456-11） |
| P1-3 HTML の相対リンク | 正しい。Epic の範囲の外なので統括に聞いた | Q3 のとおり書き換える（R-456-04、AC-456-04、05） |
| P2-1 見つけ直しの時計のずれと最後の予定 | 正しい | 基準を、結果のない予定のうち最も古いものの時刻の5分前にする（R-456-03） |
| P2-2 往復で戻らないリンクの種類 | 正しい | 3種類を R-456-08 と design に書き、AC-456-07 で確かめる |
| P2-3 `export-legacy` のリンクの一覧 | 正しい | `data.links` を出す（R-456-08） |
| P2-4 ID の決め方の食い違い | 正しい | 読む項目を `type`、`id`、`github.issue_number` に決め、要件と設計をそろえた |
| P2-5 `move-local` の Scope の出所 | 正しい | 切り替え前のコミットと、そのチェックアウトのブランチの記録だけ。食い違えば止まる（R-456-07） |
| P2-6 AC-456-06 が R-456-07 の一部だけ | 正しい | 3点を AC-456-06 に足した |
| P2-7 予行演習の手順の抜けと、0件でないときの進め方 | 正しい | design の testability に `cut`、取り込み、偽の `gh` の見せ方、開けるかの判定を足し、0件でなければ止まって聞く（AC-456-05） |
| P2-8 AC-15 の測り方、`fake_github.py` の影響 | 正しい | `git diff --name-only` の記録（AC-456-10）と、全体のテストでの確かめを足した |
| P2-9 `verify` の追跡の参照が古い | 正しい | origin の canonical を使い捨てのクローンに取って読む（R-456-09） |
| P3 コードの範囲（2つの `）、4つの空白のコード | 一部 | ` の個数によらない範囲を除く。4つの空白のコードは見分けない（理由を要件に書いた） |
| P3 `build.json` の `layout_ids` | 正しい（読む側がない） | 足さない |
| P3 `undo` の「開いている Issue だけ」 | 正しい | 残すと書いた |
| P3 消す前の一致の2つの oid | 正しい | 両方を持つと書いた |
| P3 `_scope_directories` の扱い | 正しい | `nest_plan` に置き換えると書いた |
| P3 AC-456-07 と I-8 の判断の食い違い | 正しい | AC を R-456-08 にそろえた |
| P3 カタログを確かめる場所 | 正しい | AC-456-04 に、`spec-dock/initiatives` のリンクを通して開くと書いた |
| P3 仕様のツリーの外から中へのリンク | 正しい（範囲の外） | design の risk に書き、I-10 に引き渡す |
| P3 GitHub App の作成者の名前 | 正しい | README に書く（R-456-10） |
| P3 AC-456-08 が I-16 のマージに依存 | 正しい | exit に書いた（I-16 がマージされないまま PR を出すときは統括に聞く） |

## 目標

`requirement.md` の AC-456-01〜AC-456-11 を満たす。具体的には、移行のスクリプトが、印を使わずに登録し、入れ子の仕様を `<区切り>/<ID>/` に写してリンクを書き換え、履歴を平らに作り直し、チェックアウトの取り込みも平らにし、戻すときは入れ子を作り直す。本物の spec-dock の写しの予行演習で、書き換えられないリンクが0件であることを確かめる。

## 順序・依存

- 依存：I-14（マージ済み）。I-16 は並べて進む。区切りの写しは I-16 の設計の値で先に作り、I-16 のマージの後に `origin/main` をこのブランチにマージして（rebase しない）、パッケージと比べるテストを足す。
- 順：S1（写した値と区切り）→ S2（印の撤去と見つけ直し）→ S3（写しとリンクの書き換えの部品）→ S4（`plan` と `build-canonical`）→ S5（`move-local` と `adopt-worktree`）→ S6（`export-legacy`）→ S7（`verify` と README）→ S8（予行演習）→ S9（I-16 の取り込み）。S2 と S3 は独立。S4 以降は S3 を使う。
- 並行の作業：I-16 が `src/spec_dock/` と Epic の文書を変える。この Issue は `scripts/` と `tests/` とこの Issue の Scope だけを変えるので、衝突は `tests/support/` に限られる見込み。衝突したら `origin/main` をマージして解消する。

## 実装step

各 step は `tdd` の Red → Green → Refactor で進め、区切りのよいところでコミットする。

- **S1 写した値**（AC-456-08）：`CANONICAL_ID_RE`、`BUCKET_SIZE`、`scope_bucket`、`scope_relative`、`LEGACY_TITLE_RE`、`legacy_slug`、`LEGACY_CHILD_RULES` を足し、`SLUG_RE` と印の写しを消す。`test_migration_contract_copies.py` で、`domain/ids.CANONICAL_ID_RE`、`INPUT_TITLE_RE`、`derive_input_slug_from_title`、`application/scope_scaffold._rules_source_paths` と比べ、区切りは R-456-01 の値の例で確かめる。
- **S2 印の撤去と見つけ直し**（AC-456-01、02）：`analyze` の `SLUG_MARKER_CONFLICT`、`registration_plan` と `Registrar` の `issue.marker`、`verify` の印の照合、`undo` の `issue.marker` と `_remove_marker` を消す。作成の本文をやめる。`Facts` に `author` と `created_at`、`_ISSUE_FIELDS` に `author { login } createdAt` を足し、`body` を消す。`_find_created` と `_created_without_record` を R-456-03 の条件にする。偽の `gh` に作成者と作成の時刻を足す。テスト：本文が変わらない、予定だけの記録からの再実行で拾う、2件で止まる、ほかの利用者と古い Issue を拾わない、`undo` の見つけ直し。
- **S3 写しの部品**（AC-456-03、04 の単位）：`nested_layout`、`FlatMap`、`rewrite_links`、`link_report`、`TreeFlattener` を作る。`test_migrate_flatten.py` で、パスの対応（`discussions/` の下の ID の形の名前、捨てる `rules.md`、(a)〜(d)）、リンクの書き換え（R-456-04 のすべての種類、コードの中、`#` と末尾の `/`、変えないリンク、切れたリンク）を確かめる。
- **S4 `plan` と `build-canonical`**（AC-456-03、04、11）：`plan` に `data.flatten`（`pending` を含む）と `FLATTEN_*` の異常を足し、書かずに写す。`build-canonical` を、先端の厳しい写し、履歴の作り直し、先端の照らし合わせ、管理ファイルのコミット、`data.history` と `data.links` にする。テスト：すべてのコミットが平らで `.meta.json` がない、先端の中身の一致、リンクの多いリポジトリで canonical のどのリンクも開ける、書き換えられないリンクの一覧、履歴の落とし、先端の (a) で止まる、もう一度の実行で同じコミット。
- **S5 `move-local` と `adopt-worktree`**（AC-456-06）：`move-local` の Scope の候補（切り替え前のコミットと `adopt/*.json`）、写した位置とリンクの書き換え、位置を決められないときの停止。`adopt-worktree` の C（M の写し）、X（作業の状態の厳しい写し）、消す前の一致（写した後の中身）。テスト：今の `test_migrate_checkouts.py` を平らな位置に直し、作業の状態に (a) があると止まることを足す。
- **S6 `export-legacy`**（AC-456-07）：`nest_plan`、止まる条件、`NestMap` による写しとリンクの逆の書き換え、`rules.md` の置き直し、slug の規則。テスト：日本語の題名の新しい Scope が `untitled`、英数字の題名の新しい Scope が題名から、リンクが元の文字列に戻る、従来モードの `workspace validate` と `scope show` が通る、親のない Epic、Issue のない `<ID>/`、種類の付け替えで、`--apply` なしでも止まり何も書かない。
- **S7 `verify` と README**（AC-456-09、R-456-10）：`_canonical_layout` を足し、README を直す。テスト：canonical に置き場の外れや `.meta.json` があると不一致になる。README のテストに、平らにする写しと区切りの説明を足す。
- **S8 予行演習**（AC-456-05）：`design.md` の testability の「予行演習」の手順で、本物の spec-dock の写しで行う（本物のリポジトリと GitHub には書かない）。手順と結果（書き換えたリンクの数、書き換えられないリンク0件、履歴の数と落とした数、時間、往復で字面が戻らないリンク、`canonical check` と従来モードの `workspace validate` の結果）を `report.md` に書き、一時ディレクトリを消す。手順の助けのスクリプトは、この Issue の `.workbench/`（Git では無視）に置く。
- **S9 I-16 の取り込み**（AC-456-08）：I-16 のマージの後に `origin/main` をマージし、`test_migration_contract_copies.py` で、`scope_bucket`（1、999、1000、99999、100000、1000000）、`BUCKET_SIZE`、`scope_relative` をパッケージの関数と比べる。I-16 がマージされないうちに PR を出すときは、統括に聞く。

## 検証

| AC | 確かめ方 |
|---|---|
| AC-456-01 | `test_migrate_register.py`：偽の `gh` の記録に本文の `PATCH` がなく、`POST /issues` の本文に `body` がない。`plan` の `by_operation` に `issue.marker` がない。`verify` と `undo` の出力に印がない |
| AC-456-02 | `test_migrate_register.py`：予定だけの `undo.jsonl` と偽の Issue で、拾う、2件で止まる（番号の一覧、`POST /issues` なし）、ほかの利用者と古い Issue を拾わずに作る。`undo` の見つけ直しも同じ |
| AC-456-03 | `test_migrate_canonical.py`、`test_migrate_flatten.py`：`git rev-list` のすべてのコミットのツリーを調べる。先端の中身の比べ合わせ。履歴の落としの数。先端の (a) で `plan` が1、`build-canonical` が2で push なし |
| AC-456-04 | `test_migrate_flatten.py`：リンクの多いリポジトリの canonical を作業ツリーに取り出し、すべてのリンクを開く。書き換えられないリンクの一覧 |
| AC-456-05 | S8 の予行演習の記録（`report.md`） |
| AC-456-06 | `test_migrate_checkouts.py`：平らな位置、C の発見、作業の状態の (a) で止まる |
| AC-456-07 | `test_migrate_checkouts.py`、`test_migrate_flatten.py`：入れ子と slug、リンクの戻り、従来モードの `workspace validate`、止まる条件 |
| AC-456-08 | `test_migration_contract_copies.py` |
| AC-456-09 | `test_migrate_canonical.py`：`verify` の置き場の不一致 |
| AC-456-10 | `make lint` と `uv run pytest`（全体）。`git diff --name-only origin/main...HEAD` を `report.md` に記録 |
| AC-456-11 | `test_migrate_plan.py`：登録の前の `plan` の終了コード0と `pending`、前後の参照、作業ツリー、`count-objects -v` |

- negative test：(a)〜(d) の各異常、書き換えられないリンク、見つけ直しの2件、`move-local` の位置を決められないファイル、`adopt-worktree` の作業の状態の異常、`export-legacy` の各止まる条件。どれも、何も書かない（GitHub の書き込み、origin の参照、作業の記録が変わらない）ことを確かめる。
- 回帰：`uv run pytest` の全体で、従来モードのテストを変えずに通す（AC-15）。`tests/support/fake_github.py` の変更は足すだけで、ほかのテストの結果を変えない。
- security / privacy / operability：本物の GitHub には書かない。予行演習で本物の GitHub を読むのは `plan` だけ（`gh` の今の資格情報。書き込みの API を呼ばないことを、予行演習の前に `--apply` なしであることで確かめる）。資格情報を記録や報告書に写さない。新しい出力（`data.flatten`、`data.history`）は、パスと数だけで、仕様の中身を含まない。

## rollback

- この PR を `git revert` すれば、I-8 の版に戻る。スクリプトはまだ本物で使っていないので、データの移行は N/A。
- 予行演習で問題が見つかったら、本物では使わずに、この Issue の中で直す（forward recovery）。

## exit / handoff

- 完了：AC-456-01〜11 を満たし、最終品質ゲート（lint、全体のテスト、2つの独立のレビュー）が同じ SHA で通り、PR がマージできる状態になる。マージは人が行い、`work finish` は統括の指示の後に行う。
- 引き渡し：I-9（`README.md` と使い方の文書のつなぎ）、I-10（spec-dock の本番の予行演習と切り替え。予行演習の手順は、この Issue の `report.md` と `README.md`）、I-12。I-16 がマージされないまま PR を出す必要が出たら、統括に聞き、比べ合わせが残ることを残余のリスクとして渡す。
