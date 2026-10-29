---
種別: レポート（Issue）
ID: "iss-00455"
タイトル: "Flatten Canonical Catalog And Drop Slugs"
関連GitHub: ["#455"]
最終更新: "2026-10-29"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00424", "init-00423"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

マージ済みの canonical モードのコード（I-1、I-2、I-4）を、平らな置き場（カタログの直下の `<ID>/`）と `<種類>-<番号5桁>` の ID に直した。slug と Issue の本文を読む処理をなくし、GitHub の種類のラベルの付け替えを `SCOPE_KIND_CHANGED` として見つけ、止め、警告する部品を置いた。I-5、I-11、I-15 が使う公開の形は `design.md` の「責務・Interface」のとおりである。

### 実装したこと

- **ID（C1）**：`domain/ids.py` に `CANONICAL_ID_RE`（`^(init|epic|iss)-(?:[0-9]{5}|[1-9][0-9]{5,})$`）を足した（従来の名前は変えていない）。`parse_scope_id` がこれを使う。ID は種類のラベルと番号だけで決まり、本文の印の異常（`SLUG_MARKER_*`）はなくなった。
- **スナップショット（C10）**：`ScopeNode.slug` と `IssueFacts.body` を外した。全体を読む GraphQL の問い合わせと REST の読み取りは本文を読まない。`version` は1のままで、`slug` を持つ古いファイルや `id` と `kind` の合わないファイルは取り直す。`create_issue` は本文を送らない（`title` と `labels` だけ）。
- **付け替えの判定（C1）**：`SCOPE_KIND_CHANGED`、`KindChange`、`kind_changes`（カタログの名前とスナップショットの比較）、`renamed_scope`（古い ID の解決）、`branch_names_scope`（`<ID>` か `<ID>-…` を受け付ける）を `domain/canonical_structure.py` に置いた。
- **カタログ（C3）**：`CatalogTree` を、直下の、名前が ID とちょうど同じ実際のディレクトリだけを見る形に書き直した（`find` は直接 `<catalog>/<ID>` を見る。大文字と小文字を区別しないファイルシステムでも `ISS-00454/` を Scope にしない）。`misplaced()` が、ID の形で始まるのに ID でない名前と、`<ID>/` のすぐ下の `epics/`・`issues/` を返す。入れ子の探索と重複の扱い（`ScopeDirectoryAmbiguous`）を消した。
- **読む側の共通の部品**：`canonical_scopes.py` から入れ子の組み立て（`SCOPE_NESTING`）を消し、場所をいつも `spec-dock/initiatives/<ID>` にした。組み立ての1か所 `build_canonical_scopes`、`lineage`、`require_kind_unchanged`、`kind_change_warnings`、`snapshot_warnings`、`kind_change_error`、`refuse_old_ids`、`resolve_canonical_scope`、`check_canonical_scope_expectations` を置いた。古い ID は、従来と共有の選択子の正規化の後（`iss-454` も）に、スナップショットだけで `SCOPE_KIND_CHANGED` にする。
- **検査**：`workspace validate` と `canonical status --structure` が、`SCOPE_DIRECTORY_MISSING`、`SCOPE_ISSUE_MISSING`、`SCOPE_KIND_CHANGED`（番号ごとに1件、同じ番号の MISSING と ISSUE_MISSING を重ねない）、`SCOPE_DIRECTORY_MISPLACED`（警告）を出す（`directory_anomalies`）。`SCOPE_DIRECTORY_SLUG_MISMATCH` と `SCOPE_DIRECTORY_DUPLICATE` を消した。`structure` の項目は `misplaced` の代わりに `anomalies` を持ち、error を先に並べ、最初の次の1手を示す。
- **コマンド**：`branch` の既定の名前は `<ID>`。`branch create/switch`（`--dry-run` も）、`active set`（対象と GitHub の親をたどった祖先）、`worktree create --expect-current` は付け替えで終了コード3で止まる。読むコマンド（`scope show/list`、`dependency list/check`、`artifact list/show`、`active show`、`branch show`、`worktree list/show`、`workspace sync`）は警告を出す。`worktree list/show` は、`--expect-current` がなくても、構造を読めたときだけ警告を足す（読めなければ今のまま）。

### Epic の文書で決まっていなかったこと（この Issue の判断。`requirement.md` と `design.md` に理由を書いた）

- 古い ID の指定は、読むコマンドでも終了コード3の失敗にした（Epic の2章が `SCOPE_NOT_FOUND` の失敗を置き換えると決めているため）。今の ID の指定は、読むコマンドでは警告。
- `active set` は、対象に加えて祖先の付け替えでも止まる（祖先にもリンクを置くため）。
- 読むコマンドの警告には、カタログで見つけたすべての付け替えを入れる。
- 種類のラベルが2つの Issue の `<ID>/` は `KIND_LABEL_MULTIPLE` だけで、`SCOPE_ISSUE_MISSING` と `SCOPE_KIND_CHANGED` にしない。
- `SCOPE_DIRECTORY_MISSING` と `SCOPE_ISSUE_MISSING` の次の1手の文（Epic と I-4 に文がなかった）。

### 変えたテスト（すべて canonical モードのもの。AC-455-08、Epic の AC-15）

版3の振る舞いを確かめるテストは1つも変えていない。変えたのは次の19ファイルで、どれも canonical モード（I-1、I-2、I-3、I-4、I-8 の契約の写し）のテストか、その部品である。

- テストの部品：`tests/support/fake_github.py`（`scope()` から `slug` を外し、本文に印を付けない。`POST …/issues` の本文の扱いは変えない）、`tests/support/canonical_scopes.py`（`CanonicalWorld.scope/directory/relative` を平らな `<ID>` にし、`_NESTING` を消した）。
- 単体：`tests/unit/domain/test_canonical_structure.py`、`tests/unit/domain/test_canonical_readiness.py`、`tests/unit/infra/test_github_structure.py`、`tests/unit/infra/test_github_snapshot.py`、`tests/unit/infra/test_catalog_tree.py`、`tests/unit/application/test_canonical_catalog.py`、`tests/unit/infra/test_migration_contract_copies.py`（slug の印の読み書きの比べ合わせ2つだけを外した。`migrate.py` の写しは I-15 が消す）。
- 結合と CLI：`tests/integration/github/test_fake_github.py`、`tests/cli_runtime/test_issue430_canonical_status.py`、`test_issue430_canonical_sync.py`（`fake.scope` の引数だけ）、`test_issue431_branch.py`、`test_issue431_dependency_active.py`、`test_issue431_read_only.py`、`test_issue431_scope_read.py`、`test_issue431_workspace.py`、`test_issue431_worktree.py`。
- 足したテスト：`tests/cli_runtime/test_issue455_flat_ids.py`（付け替えのシナリオ、古い ID、停止と警告、公開の形）。
- Epic の計画が挙げた `tests/cli_runtime/test_issue429_canonical_link.py` は、slug と入れ子を使っていなかったので変えていない。I-8 の移行のテスト（`tests/integration/migration/`）は変えずに通る。

## Verification

### 受け入れ条件

| AC | 確かめたテスト | 結果 |
|---|---|---|
| AC-455-01 | `test_canonical_structure.py`（印のない Issue の ID、`slug` と `body` の項目がない、古い形の拒否）、`test_github_structure.py`（GraphQL の問い合わせに `body` がない、`create_issue` の本文、移行前の印が残っても同じ ID）、`test_github_snapshot.py::test_a_version_one_snapshot_that_still_carries_slug_is_refetched` | 通過 |
| AC-455-02 | `test_canonical_structure.py`（ID の境界11通り）、`test_catalog_tree.py`（ID でない名前、大文字、隠し、リンク、ファイル、`misplaced`） | 通過 |
| AC-455-03 | `test_issue431_scope_read.py`、`test_issue431_dependency_active.py`（`path`、`active set` のリンク、Artifact） | 通過 |
| AC-455-04 | `test_issue431_workspace.py`、`test_issue455_flat_ids.py`（4つの異常、1件だけの付け替え、古い名前が2つ、種類が決まらない番号、並びと次の1手） | 通過 |
| AC-455-05 | `test_issue431_branch.py`（既定の名前 `<ID>`、移行前の `<ID>-<名前>` の `--name`）、`test_canonical_structure.py`（`branch_names_scope` の9通り） | 通過 |
| AC-455-06 | `test_issue455_flat_ids.py`（止める4つのコマンドと `--dry-run`、読むコマンド12通りの警告、古い ID の3つの綴りと `--expect-current`、カタログが見えないとき） | 通過 |
| AC-455-07 | `test_issue455_flat_ids.py::test_the_reading_side_public_shapes_used_by_later_issues` ほか単体のテスト。消す名前の一覧の検索が `src/spec_dock/runtime/` で0件（下）。`CANONICAL_FORMAT == 1` | 通過 |
| AC-455-08 | `make lint` と `uv run pytest` の全体を同じ SHA `147b9c8d4` で実行（下の「最終品質ゲート」）。変えたテストはすべて canonical モードのもの（上の一覧） | 通過 |

- 消す名前の検索：`grep -rnE 'SLUG_MARKER|SlugMarker|read_slug_marker|format_slug_marker|append_slug_marker|_MARKER_LINE|_MARKER_MESSAGES|SCOPE_DIRECTORY_NAME|ScopeDirectoryAmbiguous|duplicates\(|SCOPE_NESTING|misplaced_scopes|SLUG_MISMATCH|DIRECTORY_DUPLICATE|\.ambiguous' src/spec_dock/runtime/` は0件。
- 実装の途中の確かめ：`5e6b50371` で `uv run pytest` が 2986 passed、8 skipped（終了コード0）。

### 独立したレビュー

- 文書（手順4）：新しいサブエージェント1つが、3つの文書を Epic と照らした。P0/P1 は0件、P2 が10件、P3 が6件。すべて根拠があり、文書の訂正（古い ID の扱いの理由、選択子の正規化、`--expect-current` の経路、次の1手、大文字と小文字、`CanonicalScopes` の組み立て、観測の欄と前提、失敗・境界条件の検証、偽の `gh` の範囲、根拠の章、`details` の鍵、Issue の判断の明記、消す名前の一覧、rollback の条件）と、実装への反映（`build_canonical_scopes`、`refuse_old_ids`、`check_canonical_scope_expectations`、`find` の完全一致、`worktree list/show` の警告）で直した。統括に聞く判断はなかった。
- 実装（手順6、`c8b1e338d..5e6b50371`）：Standards と Spec の新しいサブエージェント2つ（`code-review`）。どちらも pass、P0/P1 は0件、P2 が計3件：`canonical status --structure` で読めない Scope のディレクトリの `OSError` が項目の外に漏れる、`workspace validate/doctor --expect-current` の古い ID が `PRECONDITION_FAILED` になる、application 層の公開の形を直接使うテストがない。3件とも直し、テストを足した（`d4c2f3715`）。

### 最終品質ゲート（Claude だけのゲート。ChatGPT のゲートは利用者の設定で無効）

- **対象**：通常の push で GitHub に送った `147b9c8d45d9cc649128649bfe46b98c222ab628`（`origin/main` = `c8b1e338d` からの全差分 `origin/main...HEAD`）。作業ツリーはきれいな状態で固定した。
- **静的解析**：`make lint`（ruff check、ruff format --check、mypy）→ 終了コード0（3つとも pass）。
- **全体のテスト**：`uv run pytest` → 終了コード0、2990 passed、8 skipped（846秒）。
- **独立したレビュー**：この作業に関わっていない新しいサブエージェント2つ（`code-review` の Standards と Spec。範囲 `c8b1e338d..147b9c8d4`）。結果は契約の検証（`validate-review.py`）で有効、どちらも `pass`、P0/P1/P2 は0件。
  - Standards：P3 が1件（`report.md` が修正のコミットを存在しない短い SHA `d4c2f3714` で書いていた）。
  - Spec：P3 が1件（同じ SHA の誤記と、AC-455-08 の行が、まだなかったこの節を参照していた）。
  - 対応：止める指摘ではない（P3）。この節を足し、SHA を `d4c2f3715` に直した。直したのは `report.md` だけで、ゲートの対象のコードとテストは変えていない。
- **結果**：合格。止める指摘がなく、lint と全体のテストが同じ SHA で通った。この節を書いたコミットは、ゲートの対象の上の、`report.md` だけの変更である。

### 未確認

- 実機の確かめ（Codex のサンドボックス、Linux の実機）：この Issue は読み取りの部品と名前の規則だけを変え、定期の実行や OS の仕組みに触れないので、行っていない（未確認）。CI の `ubuntu-latest` の結果は PR の検査で確かめる。
- 本物の GitHub での付け替えの観測：偽の `gh` だけで確かめた（未確認）。

## Residual Risks / Follow-ups

- **I-5、I-11 の取り込み**：テストの部品の形（`fake.scope` と `CanonicalWorld.scope` から `slug` がなくなり、`CanonicalWorld.directory/relative` が平らになった）と、消した名前（`read_slug_marker`、`append_slug_marker`、`ScopeNode.slug`、`IssueFacts.body`、`create_issue(body=…)`、`ScopeDirectoryAmbiguous`、`SCOPE_NESTING`、`CanonicalScopes.ambiguous`、`misplaced_scopes`）を使う未マージのコードは、`origin/main` の取り込みで合わせ直す必要がある。
- **Epic の文書のずれ**：Epic の `design.md` の3章の「項目の担当」は、`structure` と `--structure` を I-4 としたままである（I-14 の計画の「担当する設計」と食い違う）。また、`structure` の項目の形は I-4 の `misplaced` から `anomalies` に変わった。I-9 で文書をそろえるときに直すよう提案する。
- **`worktree list/show` の GitHub への問い合わせ**：警告のために、`--expect-current` がなくても構造（`display` の新しさ）を読むようになった。60秒以内は問い合わせず、変化の確かめは 304 で済むが、ネットワークのないときは読めないので警告を足さないだけである。
- **I-15 への引き渡し**：`migrate.py` の slug の印の写しと `SLUG_RE` の比べ合わせは残している（I-15 が消す）。ID の正規表現の写しは `CANONICAL_ID_RE.pattern` と比べる。
