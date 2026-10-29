---
種別: レポート（Issue）
ID: "iss-00432"
タイトル: "Write Scopes To GitHub In Canonical Mode"
関連GitHub: ["#432"]
最終更新: "2026-10-30"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00424", "init-00423"]
---

# Result Summary

詳細: [Report Guide](../../../../../../docs/authoring/report.md)

## Outcome

canonical モード（宣言の版4）で、Scope を書くコマンドがすべて動くようにした。構造は GitHub に、内容はカタログの平らな `<区切り>/<ID>/` に書き、`.meta.json` と Issue の本文には何も書かない。版4のリポジトリで `CANONICAL_NOT_IMPLEMENTED` で止まるコマンドはなくなった（AC-432-15）。

- **書く側の共通の部品**（`application/canonical_writes.py`）：`--offline`、リンクと形式の版、`ensure_fresh(decision)`、読み直し、書き込みごとの効果の記録とスナップショットへの反映、`partial` の組み立て。結果が分からない書き込みは重ねない。
- **コマンド**：`scope create`（3つ）、`scope import github`（3つ）、`scope edit`、`scope move`（新設。GitHub の親だけ）、`scope close`、`scope reopen`、`scope delete`、`dependency add`、`dependency remove`、`artifact create`、`artifact import file`、`work start`、`work finish`。
- **題名の規則**（I-6 から移した）：空白を除いて空でない、制御文字を含まない、256文字以下。どの言語でもよい。`--slug` は `CANONICAL_NOT_APPLICABLE`。`scope import github` の `--title` は使わず `CANONICAL_TITLE_IGNORED` の警告（統括の判断 Q5）。
- **種類の付け替え**：書くコマンドと `work start`（対象と祖先）、`work finish`（対象と子孫）は `SCOPE_KIND_CHANGED` で書く前に止まる。`scope delete` は止まらず、古い種類のディレクトリも写して消す。
- **作成時のファイル**：前付けの `タイトル:` と `親:` を除き、「詳細:」のリンクを `../../../docs/…`、`artifacts/rules.md` と `discussions/rules.md` を `../../../../docs/rules/…` で置く。区切りはなければ作り、シンボリックリンクかファイルなら `CANONICAL_PATH_OCCUPIED`。
- **`work start`**：既定のブランチ名 `<ID>`、基点の `CANONICAL_BASE_HAS_SPECS`、`evaluate_readiness`（`DOING` は `SCOPE_IN_PROGRESS` の警告で進む）、`StartLock` の後の `link_after_command` と `spec-dock/active/`、作業中のラベルと担当者（失敗は警告だけ）。
- **`work finish`**：対象と子孫のそれぞれの `<区切り>/<ID>/` の未保存の変更を `origin: finish` の束にし、すぐの実行を頼み、`state.json` で保存と push を最大180秒待ってから、確かめ直して閉じる。保留は `CANONICAL_SAVE_HELD`、確かめられなければ `CANONICAL_SAVE_UNCONFIRMED`。
- **C1 と C10 の追加**：`update_issue` の読み直しが `state_reason` も比べる。反映できない変更は飛ばし、スナップショットを古いものとして扱う（`GITHUB_SNAPSHOT_STALE`）。
- **I-4 から引き継いだ直し**：ブランチの失敗の後の再観察を従来の形に、`worktree remove/bootstrap` は確かめた記録で従来の内側の処理を呼び、`worktree create` と `installation` は直前に読み直す。リンクだけが無視されたworktreeは `--discard-ignored` なしで消す。
- **`workspace sync` の題名**（AC-09）：canonical の `workspace sync` の `scopes` の各要素に GitHub の題名 `title` を足し、文字の出力は `title` があるときだけ示す（従来モードの出力は変わらない）。I-4 の出力に鍵を足しただけである。
- **配布資産**：`docs/reference_cli.md` に `scope move`（C53）を足し、`static-inventory.json` の digest を更新した（前の値を `known_old_sha256` に）。dogfooding の `spec-dock/docs/reference_cli.md` は、承認された installation update の手順で更新するため、この PR では変えていない。

### コミットと再開

- 前の担当（2026-10-26）：`1490d3834`（文書）、`d44047b78`（S1）。未コミットの変更（S2〜S5）は再開のときに `370fa63d5` で残した。
- 再開（2026-10-29〜30）：`origin/main` を merge（`34ef6426d`。自動のメッセージの件名が merge の内容を表していない。履歴は書き換えていない）、文書の直し（`e658ca378`、`9edd17a0e`）、新しい方針への適合（`4ace8b2b0`）、以後の実装（`47c2e0702`〜）。

## Verification

### 自動のテスト

- 偽の `gh`、一時の bare とクローン、一時の `XDG_STATE_HOME` だけを使う（`tests/conftest.py` の2段の防ぎの中）。新しいテスト：`tests/cli_runtime/test_issue432_{scope_create,scope_change,dependency_write,artifact_write,work_start,work_finish,branch_followups,titles_and_kinds}.py`、`tests/unit/{domain,infra}/test_canonical_scaffold.py`、`tests/unit/commands/test_canonical_dispatch.py` の版3の `scope move`。
- 受け入れ条件との対応：AC-432-01、03、04、05、18 は `test_issue432_scope_create.py` と `test_issue432_titles_and_kinds.py`、02 は各 CLI テストの要求の記録（読み直しの `GET`、つながらないとき、`--offline`、GitHub だけの変更）、06 と 07 は単体（`test_canonical_structure.py`、`test_github_snapshot.py`、`test_github_structure.py`）、08 は `test_issue432_dependency_write.py`、09 と 10 は `test_issue432_scope_change.py`、11 は `test_issue432_artifact_write.py`、12 は `test_issue432_work_start.py`、13 は `test_issue432_work_finish.py`（偽のスケジューラーの `on_kick` で `canonical sync` の1周期、注入した時計で時間切れ）、14 は `test_issue432_branch_followups.py`、15 は `test_issue431_read_only.py` と `test_cli_vnext_contract.py`、16 は下の表と `git diff --name-only origin/main -- src/`（設計の「置き場」の表のファイルだけ）、19 は `test_issue432_titles_and_kinds.py`、`test_issue432_work_start.py`、`test_issue432_work_finish.py`、`test_issue432_scope_change.py`。
- ゲートの前の全体の実行（`f5047b09b` の時点）：`uv run pytest` は 3178 passed、8 skipped（終了コード0）。

### 実機の確かめ（2026-10-29）

- wheel（`uv build --wheel`）を一時の venv に入れ、外の console で、一時の bare とクローン、偽の `gh`、一時の `XDG_STATE_HOME` と `HOME` で動かした（`canonical link --no-schedule`。利用者の GitHub、状態の置き場、定期の実行に触れない）。`scope create`（日本語の題名だけで initiative、epic、issue。置き場は `spec-dock/initiatives/00000-00999/iss-00003`）、`--slug` の `CANONICAL_NOT_APPLICABLE`、`scope move --parent`、`--parent` なしの使い方の誤り（2）、`scope edit`（日本語）、`dependency add` の後の `work start` の `READINESS_NOT_SATISFIED`、`dependency remove`、`artifact create`、`work start`（ブランチ `iss-00003`、`spec-dock/active/issue` が `../initiatives/00000-00999/iss-00003`）、`workspace sync` が、期待どおりに動いた。この確かめで `workspace sync` に題名が出ないことが分かり、上のとおり足した（足した後は CLI のテストで確かめ、外の console では再確認していない）。
- **未確認**：外の console での `work finish`（構造のリポジトリを決める `origin` を GitHub の URL にすると、同期の push が本物の GitHub に向かうため、外では行わなかった。CLI のテストで、bare のリモートへの push と1周期で確かめた）。Linux の実機、Codex のサンドボックスの中からの書くコマンド（Epic の計画は I-9、I-10 に置く）。本物の GitHub での書き込み（I-10）。

### 実装のレビュー（独立レビュー②、`f5047b09b`）

- 規約と仕様を、この作業に関わっていない新しいサブエージェント2つ（opus/high、`code-review`）で見た。どちらも P0/P1 なし。規約は P2 3件・P3 1件、仕様は P3 5件。`analyze-review-findings` で6つのまとまりに分け、すべて根拠を確かめて直した：`work finish` の書いた後の Git の失敗と閉じた後の選択の失敗を `partial` に、`scope create` のラベル作成の失敗を Issue 作成の失敗として案内しない、`reread_parent` が Scope でない親を「Scope の親なし」として反映する、案内の `--title` を `shlex.quote` で引用、区切りの場所の退避の手順を案内の先頭に、`scope edit/close/reopen` の題名・付け替え・古い ID のテスト（`test_issue432_titles_and_kinds.py`）。

### 最終品質ゲート

- **Gate 1**（`dfb86e1f9b763db5d022f8ce3889fed103c5c4e6`、push 済み）：`make lint` は合格（ruff check、ruff format check、mypy。終了コード0）。`uv run pytest` は 3229 passed、8 skipped（終了コード0、17分07秒）。全差分（`origin/main...dfb86e1f9`）のレビュー：この作業に関わっていない新しいサブエージェント2つ（opus/high）。規約は P0/P1 なし、P2 1件（`work finish` の後、作業中のラベルを外した反映が閉じる前の Issue の値を使い、スナップショットで対象が open に戻る）、P3 1件（読み直しでだけ見える種類の付け替えが `SCOPE_NOT_FOUND` になる）。仕様は P0/P1 なし、P2 2件（AC-432-06 の CLI の証拠、AC-432-14 の `worktree bootstrap` の証拠）、P3 1件（R-432-12 の文が `finished_at` のまま）。ゲートの決まりでは合格だが、規約の P2 は完了した Scope を `scope show` が open と示す実際の不具合なので、5件とも直して Gate 2 を行った。
- **Gate 2**（`e86f003a1f7c5fdc2b7ab4b382443f035dadac46`、push 済み。直しの `015aa07c8` と、`origin/main`（PR #464、移行のスクリプト）の merge を含む）：`make lint` は合格（終了コード0）。`uv run pytest` は 3276 passed、8 skipped（終了コード0、17分18秒）。レビューは、新しいサブエージェント2つ（opus/high）に、Gate 1 の SHA からの差分と前の指摘の確かめに絞って頼んだ（全差分は Gate 1 で2つのレビューを通っているため）。規約、仕様とも指摘なし。前の5件がすべて直ったことを確かめた。**合格**。
- Gate 2 の後に、`origin/main` の PR #465（Epic の文書だけ）を merge した。コードに触れないので、ゲートはやり直していない（依頼文の決まりと統括の連絡）。Epic の文書と、この Issue の文書・実装に食い違いがないことを確かめた。

### 変えた既存のテスト（AC-432-16）

| テスト | 変えたこと | 区分 |
|---|---|---|
| `tests/cli_runtime/test_cli_vnext_contract.py` | コマンドの数 52→53 と一覧に `scope move` | コマンドの数と一覧 |
| `tests/cli_runtime/test_help_completion_vnext.py` | コマンドの数 52→53 | コマンドの数と一覧 |
| `tests/cli_runtime/test_issue413_contract.py` | コマンドの数 52→53 | コマンドの数と一覧 |
| `tests/integration/test_cli_docs_vnext.py` | コマンドの数 52→53 | コマンドの数と一覧 |
| `tests/cli_runtime/test_issue428_canonical_mode.py` | 未実装のコマンドの表に `scope move` の引数。文字の出力のテストは、登録を外したコマンドで確かめる | canonical モードのテスト（I-1） |
| `tests/cli_runtime/test_issue431_read_only.py` | 「I-5 の書くコマンドだけ処理がない」を「処理のないコマンドがない」に | canonical モードのテスト（I-4） |
| `tests/unit/commands/test_canonical_dispatch.py` | 未実装の経路を、登録を外したコマンドで確かめる。版3の `scope move` のテストを足す | canonical モードのテスト（I-1） |
| `tests/unit/domain/test_canonical_structure.py`、`tests/unit/infra/test_github_snapshot.py`、`tests/unit/infra/test_github_structure.py` | C1 と C10 の追加のテスト（S1）。`body` のテストを外した | canonical モードのテスト（I-1） |

## Residual Risks / Follow-ups

- **結果の分からない書き込み**：同じ書き込みは重ねず、`partial` と次の1手で返す。利用者やエージェントは、GitHub の今の状態を確かめてから続ける必要がある。
- **読み直さない関係**：`work start` は対象と祖先の依存の一覧を読み直すが、前提の Scope の状態、閉じるときの子孫、依存の追加の循環の確かめに使うほかの辺は、`decision` の5分の新しさのスナップショットで判断する（Epic の決めたとおり）。
- **`work finish` の待ち**：最大180秒、端末を止める。定期の実行が動いていないと `CANONICAL_SAVE_UNCONFIRMED` になる。周期の新しさは `last_cycle.started_at`（秒の精度）で判断し、保存の保証は束の消費、未保存の変更がないこと、HEAD の一致、`remote_contains_head` が受け持つ。
- **`--expect-current` の残る窓**：`worktree create` と `installation` は、従来の処理の取り込みの直前に読み直すが、その後の従来の取り込みとの間の狭い窓が残る（統括の判断 Q3）。`worktree remove/bootstrap` にはこの窓はない。
- **`worktree remove` の窓**：無視されたものがリンクだけと確かめてから `git worktree remove` までに作られた無視されたファイルは消える（従来の `--discard-ignored` と同じ種類の窓。統括の判断 Q4）。
- **従来の部品の写し**：`work start`、`work finish`、Artifact の公開、`worktree remove/bootstrap` の外側は、従来の流れの写しや非公開の関数を使う（AC-15 のため）。I-13 の撤去で一本にする。
- **題名の長さ**：256文字をコードポイントで数える。GitHub が別の数え方をすると、絵文字の多い題名で GitHub が拒むことがある（そのときは Issue ができずに失敗する）。
- **merge の件名**：`34ef6426d`（`origin/main` の merge）の件名は、自動のメッセージの生成で merge の内容を表していない。履歴は書き換えていない。

### 統括に判断・対応してほしいこと

- Epic の文書の残り（PR #465 で `--title`、180秒、`SCOPE_IN_PROGRESS`、`CANONICAL_TITLE_IGNORED` は直った）：12章の `CANONICAL_SAVE_UNCONFIRMED` は終了コード6だけだが、束を書いていないときは `failed` の3になること。12章に `CANONICAL_PROGRESS_MARK_FAILED`（警告）がないこと。I-5 の「変わる」の「区切りの場所の確かめは書く前」に対し、`scope create` では作った後の失敗になること（Issue の番号は作るまで分からない。`partial` と「退避してから `scope import github`」の案内）。6章の「作成時のファイル」の `discussions/rules.md` は、配布資産の `docs/rules/<種類>/discussions.md` へのリンクとして置いた（従来の作成は置かない）。
- I-9 への申し送り：`scope move` の文書（GitHub の親だけ）、新しいコードの文書、`SCOPE_IN_PROGRESS` でエージェントが利用者に確かめる規則、`work finish` が最大180秒待つこと、`worktree remove` がリンクだけなら `--discard-ignored` なしで消すこと、`workspace sync` が題名を示すこと、dogfooding の `spec-dock/docs/reference_cli.md` の更新（配布資産は更新済み）。
