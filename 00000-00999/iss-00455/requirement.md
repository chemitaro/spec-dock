---
種別: 要件定義書（Issue）
ID: "iss-00455"
タイトル: "Flatten Canonical Catalog And Drop Slugs"
関連GitHub: ["#455"]
状態: "draft"
最終更新: "2026-10-29"
親: ["epic-00424", "init-00423"]
---

# iss-00455 Flatten Canonical Catalog And Drop Slugs — 要件定義

詳細: [Requirement Guide](../../../docs/authoring/requirement.md)

表示名：canonical モードのカタログを平らにし、slug をやめ、ID・ディレクトリ名・ブランチ名を `<種類>-<番号5桁>` にそろえる（Epic の I-14）

## 目的

マージ済みの canonical モードのコード（I-1、I-2、I-4）が、平らな置き場（カタログの直下の `<ID>/`）と `<種類>-<番号5桁>` の ID で動く。止まっている I-5（`iss-00432`）と I-11（`iss-00438`）を再開でき、I-15（`iss-00456`）が写す ID の規則と種類の判定の定数がそろう。

- 材料：Epic の `plan.md` の「I-14 Flatten Canonical Catalog And Drop Slugs」の節（価値、担当する設計、作るものの表、テスト、受け入れ、注意）と、Epic の `design.md` の担当の章（2章の表し方の「番号・ID」、種類の決め方と付け替え、構造のスナップショットの `slug` と本文、内容の置き場。3章の `canonical status` の `structure`。6章の `branch` と `workspace validate` の行と検査。7章の ID とブランチ名。12章の `SCOPE_KIND_CHANGED` と、I-14 が直す `SCOPE_DIRECTORY_*` の行）。方針の理由は Epic の `design.md` の「設計の判断」の最後の行（2026-10-29 の利用者の決定）にある。
- 依存：なし（直す I-1、I-2、I-4 はマージ済み）。Planning Level：strict（理由は `plan.md`）。
- この Issue は、契約 C1（構造の表し方）、C3（置き場と `catalog_tree`）、C10（構造のスナップショット）の持ち主として、それらを新しい方針に合わせて直す。直した公開の形は、I-5、I-11、I-15 が使うので、`design.md` の「責務・Interface」に書く。

## 背景

- 2026-10-29 に、利用者が、カタログの置き場を平らにし（入れ子をやめる）、slug を廃止し、ID・ディレクトリ名・ブランチ名を `<種類>-<番号5桁>` にそろえ、題名は GitHub の題名だけを正とすると決めた。入れ子と slug は GitHub の親子と題名の写しで、写しを保つために、ずれの検査、本文の印、`SLUG_REQUIRED` などが要っていた。
- マージ済みのコードは、まだ前の方針で動く。
  - I-1：構造のスナップショットが、Issue の本文の slug の印（`<!-- spec-dock:slug=… -->`）を読み、印がない Scope の ID を null にし、`slug` を保存する。全体を読む GraphQL の問い合わせが本文を読む。
  - I-2：`CatalogTree` が、カタログを入れ子でたどり、`<ID>-<slug>` の名前で Scope のディレクトリを探し、同じ ID の重複を扱う。
  - I-4：読むコマンドが、ディレクトリのないときの場所を入れ子と slug で組み立て、`workspace validate` と `canonical status --structure` が slug の照合、重複、入れ子のずれを報告する。`branch create` の既定の名前が `<ID>-<slug>` である。
- 関係者：
  - 利用者とエージェント：canonical モードで、Scope の場所が `spec-dock/initiatives/<ID>/` に決まり、日本語の題名でもそのまま使えること。GitHub で種類のラベルを付け替えたときに、名前が黙ってずれず、止まって次の1手が示されること。
  - 止まっている I-5、I-11 と、後の I-15 の実装担当：平らな置き場と新しい ID の規則と、種類の付け替えの判定の部品を、この Issue の `design.md` だけで使えること。
  - 移行していないリポジトリ（版3）：今と同じに動くこと（AC-15）。

## 観測可能な要件

### R-455-01 ID は種類と番号だけで決まる（C1）

- 種類のラベルがちょうど1つの Issue は、本文によらず、その種類と番号から ID を持つ。ID は種類の接頭辞（`init-`、`epic-`、`iss-`）と番号をつないだもので、番号は5桁未満なら0で埋め、5桁以上ならそのまま（`iss-100000`）である。
- ID の形は、Epic の2章の正規表現 `^(init|epic|iss)-(?:[0-9]{5}|[1-9][0-9]{5,})$` に合うものだけである（番号が0のものを除く）。この規則は、名前を ID として読むところ（カタログのディレクトリ名、ブランチ名の照合、ID の解析の部品 `parse_scope_id`）に当てる。`iss-000454`、`iss-454`、`iss-00454-foo`、`ISS-00454` は、ディレクトリ名やブランチ名としては ID ではない。
- コマンドの引数（選択子）は、従来モードと共有の今の解析（`domain/selectors.py`。変えない）を通る。今と同じく、前後の空白を除いて小文字にし、番号を5桁に正規化する（`iss-454` は `iss-00454` を指す）。付け替えの判定も、この正規化の後の ID で行う（R-455-06）。
- 種類のラベルが2つ以上の Issue は、今と同じく `KIND_LABEL_MULTIPLE` の異常にし、ID を決めない。本文の印に関する異常（`SLUG_MARKER_MISSING`、`SLUG_MARKER_MULTIPLE`、`SLUG_MARKER_INVALID`）はなくなる。

### R-455-02 スナップショットは本文と slug を持たない（C10）

- 全体を読む GraphQL の問い合わせと、REST の Issue の読み取りは、本文を使わない。GraphQL の問い合わせに `body` の項目がない。
- 構造のスナップショット（`snapshot.json`）の Issue の要素は `slug` の項目を持たない。`version` は1のままである。
- `slug` を持つ古い `snapshot.json` は、壊れたファイルと同じく読まずに、全体を取り直す。
- SpecDock が作る Issue に本文を送らない（Epic の2章「書く」の表。作成は `title` と `labels` だけ）。

### R-455-03 Scope のディレクトリはカタログの直下の `<ID>/`（C3）

- canonical モードのコマンドは、Scope のディレクトリを `<カタログ>/<ID>/` で直接求める。入れ子をたどって探さず、入れ子のパスを組み立てない。名前は ID と完全に一致しなければならない（大文字と小文字を区別しないファイルシステムでも、`ISS-00454/` は `iss-00454` のディレクトリではない）。
- `scope show`、`scope list`、`active set`、`artifact list`、`artifact show` は、`spec-dock/initiatives/<ID>/` を示し、開く。`active set` が置くリンクの先は `../initiatives/<ID>` である。
- `scope show --json` と `scope list --json` は、各 Scope の ID、GitHub の題名、親の ID、Scope のディレクトリのパス（`spec-dock/initiatives/<ID>`）を返す。ディレクトリがなければ、I-4 のとおりパスは null、`directory_found` は偽である（入れ子の場所を推測して示さない）。

### R-455-04 ディレクトリと GitHub の対応の異常（`workspace validate`、`canonical status --structure`）

- 次の4つの異常を報告する。`SCOPE_DIRECTORY_SLUG_MISMATCH` と `SCOPE_DIRECTORY_DUPLICATE` は出さない。
  - `SCOPE_DIRECTORY_MISSING`（error）：スナップショットにある Scope の `<ID>/` が、カタログの直下にない。
  - `SCOPE_ISSUE_MISSING`（error）：カタログの直下の `<ID>/` に当たる Scope の Issue が、スナップショットにない。
  - `SCOPE_KIND_CHANGED`（error）：カタログの直下の `<ID>/` の番号の Scope が、GitHub では別の種類である。同じ番号で `SCOPE_DIRECTORY_MISSING` と `SCOPE_ISSUE_MISSING` を重ねて出さず、その番号について1件だけ出す。
  - `SCOPE_DIRECTORY_MISPLACED`（warning）：カタログの直下の、ID の形で始まる名前（`init-`、`epic-`、`iss-` と数字）なのに名前が ID そのものでないディレクトリ（`iss-00454-foo` など）と、直下の `<ID>/` のすぐ下にある `epics/` か `issues/`。Scope の中の `artifacts/`、`discussions/` などの下は調べない。次の1手は「中身を `<カタログ>/<ID>/` に移し、空になったディレクトリを消す」。
- `workspace validate` は、error の3つを findings（終了コード7）に、`SCOPE_DIRECTORY_MISPLACED` を warnings に入れる。ほかの検査（スナップショットの異常、必要な文書、`.meta.json`、別名ファイル、Scope でない Issue への依存）は今と同じである。
- `canonical status --structure` の `structure` の項目は、上の4つの異常を、error を先に（`SCOPE_KIND_CHANGED`、`SCOPE_DIRECTORY_MISSING`、`SCOPE_ISSUE_MISSING`、`SCOPE_DIRECTORY_MISPLACED` の順に）示す。異常がなければ `ok`、あれば `problem` とし、最初の異常の次の1手を示す。4つの異常は、どれも `details.next_step` に次の1手を持つ（`MISSING` と `ISSUE_MISSING` の文は I-4 の設計にないので、この Issue で決める）。

### R-455-05 ブランチ名（`branch show`、`branch create`、`branch switch`）

- 既定のブランチ名は `<ID>` である（例 `iss-00454`）。`--name` で明示した名前は今と同じく使える。
- ブランチ名と ID を照らす部品は、最後の `/` の後の部分が `<ID>` か `<ID>-` で始まるものを、その ID のブランチとして受け付ける。`iss-00454`、`iss-00454-foo`、`<所有者>/iss-00454-foo` は `iss-00454` のブランチで、`iss-004541` はそうでない。

### R-455-06 種類の付け替え（`SCOPE_KIND_CHANGED`）

- GitHub で種類のラベルを付け替えると ID が変わる（例 `iss-00454` から `epic-00454`）。SpecDock は、ディレクトリとブランチの名前を自動で変えない。カタログの直下に、同じ番号で GitHub と違う種類の `<ID>/` があることで、付け替えを見つける。
- 指定の解決：古い ID（`iss-00454`、正規化して同じになる `iss-454` も）で指定すると、スナップショットにその ID はないが同じ番号の Scope があるので、`SCOPE_NOT_FOUND` ではなく `SCOPE_KIND_CHANGED` で止まり、`details.current_id` に今の ID（`epic-00454`）を示す。Epic の2章の「指定の解決」は、`SCOPE_NOT_FOUND` の失敗を `SCOPE_KIND_CHANGED` に置き換えると決めているので、どのコマンドでも（読むコマンドでも）失敗で、終了コードは Epic の12章の `SCOPE_KIND_CHANGED` の行の3とする。古い ID は、スナップショットのどの Scope の ID でもないので、読むコマンドでも示す対象を決められないためである。今の ID（`epic-00454`）での指定は、対象を決められるので、読むコマンドは警告にし、止めるコマンドは止まる。`--expect-current` に渡した古い ID も同じに扱う。古い ID の判定は、スナップショットだけで行う（カタログが見えなくても判定できる）。
- 止めるもの（終了コード3。書く前に止まる）：この Issue の範囲では、付け替えの異常のある Scope を対象にする `branch create`、`branch switch`、`active set`、`worktree create --expect-current`。`--dry-run` でも止まる。`active set` は、対象に加えて、GitHub の親をたどった祖先の付け替えでも止まる（この Issue の判断。`active set` は祖先のディレクトリにもリンクを置くため。Epic の「対象か祖先」の `work start` と同じ範囲にそろえる）。
- 警告にするもの：この Issue の範囲の読むコマンド（`scope show`、`scope list`、`dependency list`、`dependency check`、`artifact list`、`artifact show`、`active show`、`branch show`、`worktree list`、`worktree show`、`workspace sync`）は、付け替えの異常を `warnings` に入れ、結果（終了コードとデータ）を変えない。
  - 警告には、指定した Scope に関係なく、カタログで見つけたすべての付け替えを入れる（この Issue の判断。どの読むコマンドでも気付けるようにするため。付け替えは利用者が直すまで残る異常で、数は少ない）。
  - `worktree list` と `worktree show` は、今は `--expect-current` のときだけ構造を読む。Epic のとおり、`--expect-current` がなくても警告を出すために、構造（`display`）とリンクが正しいカタログを読む。読めないとき（GitHub につながらない、スナップショットがない、リンクがない）は、警告を足さず、結果を変えない（この2つのコマンドは、構造もカタログも要らないため）。
  - 警告にするコマンドでも、今の ID のディレクトリがないために、ディレクトリを要るコマンドは今のとおり失敗する（`artifact list --scope epic-00454` は、`epic-00454/` がなければ `LOCAL_TARGET_NOT_FOUND`、終了コード4）。止める理由は付け替えではなく、ディレクトリがないことである。
  - `workspace validate`、`workspace doctor`、`canonical status --structure` は、付け替えを findings か `structure` の異常として示し、同じものを警告に重ねない。
- 次の1手（`recovery`）は「GitHub の種類のラベルを元に戻す。種類を変えるのが意図なら、新しい種類で Issue を作り直し（`spec-dock scope create`）、古いディレクトリの内容を新しい `<ID>/` に移し、古い Scope を、今の ID で `spec-dock scope delete`」である。
- 書くコマンド（`scope …`、`dependency add/remove`、`artifact create/import`）、`work start`、`work finish` での停止と、`scope delete` の扱いは I-5 が行う。この Issue は、その判定の部品を1か所に置く（R-455-07）。

### R-455-07 後の Issue が使う公開の形

- I-5、I-11、I-15 が使う公開の形（ID の正規表現、ID の解析と生成、ブランチ名の照合、種類の付け替えの判定、カタログの直下の `<ID>/` を求める部品、`SCOPE_KIND_CHANGED` での停止と警告の部品）を、この Issue の `design.md` に、関数と型とエラーのコードとして書き、その形どおりに実装する。

## スコープ

### 対象

- `plan.md` の I-14 の表のファイルと関数（`src/spec_dock/runtime/` の `domain/canonical_structure.py`、`domain/ids.py`、`infra/github_structure.py`、`infra/catalog_tree.py`、`application/canonical_scopes.py`、`application/canonical_workspace.py`、`application/canonical_status.py`、`application/canonical_branches.py`）と、その結果として直す canonical の読む処理（`application/canonical_scope_read.py`、`application/canonical_worktrees.py`、`application/canonical_errors.py`）。
- `domain/canonical_content.py` の `CANONICAL_FORMAT` を1のままにすること（変えないことを確かめる）。
- I-14 の表のテストと、テストの部品（`tests/support/fake_github.py`、`tests/support/canonical_scopes.py`）。`tests/unit/infra/test_migration_contract_copies.py` から slug の印の写しの比べ合わせを外す。

### 対象外

- 書くコマンドの canonical の処理（`scope create`、`scope import github` の `--slug` の拒否を含む）、`work start`、`work finish`、書くコマンドでの `SCOPE_KIND_CHANGED` の停止、`scope delete` の古いディレクトリの扱い（I-5）。
- ダッシュボードと、スナップショットの `created_at`、`closed_at`（I-11）。
- 移行のスクリプト `scripts/migrate-to-canonical/migrate.py` の slug の印の写しの削除と、平らにする写し（I-15）。
- 定期の同期（I-3）と `canonical check`（I-7）の本体（読んで、直す必要がないことを確かめた）。
- 配布資産の文書とテンプレート（I-9。移行の間はテンプレートを変えない）。
- 従来モード（宣言の版3）の処理、`.meta.json` の読み書き、版3の振る舞いのテスト（AC-15）。

### 親の契約として守る境界

- Epic の目的、Issue の分け方、Issue をまたぐ契約（C1〜C11）は変えない。C1、C3、C10 は、Epic の `design.md` の2章と3章に書かれた新しい形にする。
- 読むだけのコマンドは、リポジトリ、カタログ、`.git`、GitHub に書かない（書いてよいのは状態の置き場の `snapshot.json` と `probe.json` だけ）。

## 失敗・境界条件

- 種類のラベルが2つの Issue：ID を決めず `KIND_LABEL_MULTIPLE` の異常にする。その番号の `<ID>/` がカタログにあっても、`SCOPE_ISSUE_MISSING` と `SCOPE_KIND_CHANGED` は出さない（この Issue の判断。Issue はスナップショットにあり、異常はすでに `KIND_LABEL_MULTIPLE` の error で示しているため）。
- 同じ番号で、古い種類と新しい種類の両方の `<ID>/` があるとき：古い種類のディレクトリを `SCOPE_KIND_CHANGED` として1件だけ示す（今の ID のディレクトリはあるので `SCOPE_DIRECTORY_MISSING` は出ない）。
- 同じ番号で、別の2つの種類の古いディレクトリがあるとき：その番号について1件だけ出し、古いディレクトリの一覧に両方を入れる。
- 番号が0の名前（`iss-00000`）、6桁以上で先頭が0の名前（`iss-000454`）、`iss-00454-foo` は ID ではない。カタログの直下にあれば `SCOPE_DIRECTORY_MISPLACED` にする。
- カタログの直下の、隠しディレクトリ（`.` で始まる名前）、シンボリックリンク、ファイルは、Scope のディレクトリではない。
- カタログが見えない（リンクを求めないコマンドで、リンクが正しくない）とき：ディレクトリによる付け替えの判定はできないので、今の ID での指定は付け替えなしとして進む。古い ID での指定はスナップショットだけで判定できるので、`SCOPE_KIND_CHANGED` で止まる（`details.directories` は空）。
- `slug` を持つ古い `snapshot.json`、`slug` も `id` も持たない形など、版1の今の形と鍵の集合が違うファイルは、取り直す。GitHub につながらず取り直せないときは、ファイルがないときと同じ失敗のコードで止まる（I-1 の今の扱い）。

## 受け入れ条件

- **AC-455-01**（R-455-01、R-455-02）：偽の `gh` で、本文に印のない、種類のラベル付きの Issue が ID を持つ（移行前の印が本文に残っていても、ID は同じに決まる）。スナップショットに `slug` と本文がなく、偽の `gh` が記録した全体を読む GraphQL の問い合わせに `body` がない。`slug` を持つ古い `snapshot.json` は読まずに取り直す。`version` は1のまま。`create_issue` が送る本文に `body` がない。
- **AC-455-02**（R-455-01、R-455-03、失敗・境界条件）：番号が5桁未満なら0で埋まり、6桁以上ならそのまま（`iss-100000`）。2章の正規表現に合わない名前（`iss-000454`、`iss-454`、`iss-00454-foo`、`iss-00000`）は `parse_scope_id` で解析されず、カタログの Scope のディレクトリにもならず、カタログの直下にあれば `SCOPE_DIRECTORY_MISPLACED` になる。`ISS-00454/` も Scope のディレクトリにならず、`SCOPE_DIRECTORY_MISPLACED` になる。隠しディレクトリ、シンボリックリンク、ファイルは Scope のディレクトリにならない。
- **AC-455-03**（R-455-03）：一時のカタログで、`scope show --json`、`scope list --json` の `path` が `spec-dock/initiatives/<ID>`、`active set` のリンクの先が `../initiatives/<ID>`、`artifact list` が `<カタログ>/<ID>/artifacts` を読み `spec-dock/initiatives/<ID>/artifacts/…` を示す。ディレクトリのない Scope の `path` は null で、移行前の名前や入れ子に残ったディレクトリ（`iss-00004-old/`、`epic-00002/issues/iss-00004/`）を、その Scope の場所として使わない。`scope show --json` が ID、題名、親の ID、パスを返す。
- **AC-455-04**（R-455-04、失敗・境界条件）：`workspace validate` と `canonical status --structure` が、2章の4つの異常を見つけ、`SCOPE_DIRECTORY_SLUG_MISMATCH` と `SCOPE_DIRECTORY_DUPLICATE` を出さない。`iss-00454/` があり GitHub では epic のとき、`SCOPE_KIND_CHANGED` を1件だけ出し、同じ番号の `SCOPE_DIRECTORY_MISSING` と `SCOPE_ISSUE_MISSING` を出さない。古い種類のディレクトリが2つ（`iss-00454/` と `init-00454/`）あっても、新しい種類のディレクトリ（`epic-00454/`）もあっても、1件で、古い名前の一覧に両方が入る。種類のラベルが2つの Issue の `<ID>/` は、`KIND_LABEL_MULTIPLE` だけで、`SCOPE_ISSUE_MISSING` と `SCOPE_KIND_CHANGED` にならない。`structure` の項目は error を先に並べ、最初の異常の次の1手を示す。
- **AC-455-05**（R-455-05）：`branch create` の既定の名前が `<ID>`。ブランチ名の照合の部品が、`iss-00454` と `iss-00454-foo` と `<所有者>/iss-00454-foo` を `iss-00454` のブランチとして受け付け、`iss-004541` を受け付けない。
- **AC-455-06**（R-455-06）：#454 の種類のラベルを issue から epic に付け替え、カタログに `iss-00454/` だけがある一時のリポジトリで：
  - `branch create`、`branch switch`（`epic-00454` でも `iss-00454` でも、`--dry-run` でも）、`active set epic-00454`、祖先の付け替えのときの `active set`、`worktree create --expect-current epic-00454` が終了コード3の `SCOPE_KIND_CHANGED` で止まり、ブランチ、チェックアウト、リンク、worktree を作らない。
  - 付け替えのない Scope（`iss-00003`）か、今の ID（`epic-00454`）を対象にした R-455-06 の警告にするコマンドは、終了コード0で、`warnings` に `SCOPE_KIND_CHANGED`（`details.current_id` が `epic-00454`、`details.directories` が `["iss-00454"]`）を1件入れる。
  - 古い ID（`iss-00454`、`ISS-00454`、`iss-454`）での指定と、`--expect-current` の古い ID は、`SCOPE_NOT_FOUND` ではなく終了コード3の `SCOPE_KIND_CHANGED` になり、`details.current_id` に今の ID を示す。カタログが見えないときも、古い ID はこうなる。
- **AC-455-07**（R-455-07）：`design.md` の「責務・Interface」に書いた公開の形（名前と引数と戻り値とエラーのコード）が実装にあり、テストがその形を直接使う。`design.md` の「消す名前の一覧」の名前が、`src/spec_dock/runtime/` の検索で0件である。`CANONICAL_FORMAT` は1のまま。
- **AC-455-08**（Epic の AC-15）：版3の振る舞いを確かめるテストが変更なしで通る（この Issue で変えるテストは canonical モードのものだけで、`report.md` に一覧で書く）。`make lint` と `uv run pytest` が通る。

## 制約・前提

- 起点は `origin/main` の `c8b1e338d`（Epic の改訂の PR #457 のマージ後）。
- 従来モード（宣言の版3）の処理、`.meta.json` の読み書きのコード、版3の振る舞いのテストを変えない（AC-15）。`domain/ids.py` の今の関数と正規表現（`ID_RE`、`format_id`、`INPUT_SLUG_KEBAB_RE` など）は従来モードが使うので変えず、canonical の ID の正規表現は足すだけにする。
- テストは外のネットワークを使わない。GitHub は偽の `gh`、リモートは一時ディレクトリの bare のリポジトリ、状態の置き場は一時ディレクトリの `XDG_STATE_HOME` で置き換え、`tests/conftest.py` の2段の偽物（本物の launchd、systemd、`gh api` に届かないようにするもの）の中で書く。
- 止まっている I-5、I-11 の worktree（`iss-00432-canonical-scope-write`、`iss-00438-canonical-dashboard`）には触れない。それらは、この Issue のマージの後に `origin/main` を取り込んで、テストの部品の新しい形（`fake.scope` と `CanonicalWorld.scope` の引数から `slug` がなくなる）に合わせる。
- 本物の GitHub、本物の spec-dock のリポジトリの canonical、利用者の状態の置き場とツールの設定に書かない。
