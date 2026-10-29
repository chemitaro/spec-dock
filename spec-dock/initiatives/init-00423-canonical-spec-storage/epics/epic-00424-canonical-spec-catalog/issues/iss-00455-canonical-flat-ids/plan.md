---
種別: 実装計画書（Issue）
ID: "iss-00455"
タイトル: "Flatten Canonical Catalog And Drop Slugs"
関連GitHub: ["#455"]
状態: "draft"
最終更新: "2026-10-29"
依存: ["requirement.md", "design.md"]
親: ["epic-00424", "init-00423"]
---

# iss-00455 Flatten Canonical Catalog And Drop Slugs — 実装計画

詳細: [Issue Plan Guide](../../../../../../docs/authoring/issue-plan.md)

## Planning Level

- **選んだ level**：strict（Epic の計画の指定と同じ）。
- **理由**：すべての canonical のコマンドが通る部品（ID の解析、構造のスナップショット、カタログの探し方、読む側の共通の部品）を変え、I-5、I-11、I-15 が使う公開の形（C1、C3、C10）を決め直すため。誤ると、後の3つの Issue と、I-10 の切り替えの後の全コマンドに当たる。
- **risk factor**：公開の形の変更（後の Issue の手戻り）、共有のテストの部品の変更、従来モードの回帰（AC-15）。
- **再評価の条件**：Epic の契約（C1〜C11）を変える必要が出たとき、従来モードのコードやテストを変える必要が出たときは、止まって統括に聞く。利用者のデータを書き換える処理が入ることになったら critical を検討する（今の範囲では、カタログにも GitHub にも書かない）。

## 目標

`requirement.md` の AC-455-01〜08 を満たす。マージ済みの canonical のコードが平らな置き場と `<種類>-<番号5桁>` の ID で動き、I-5 と I-11 を再開できる。

## 順序・依存

- 依存：なし（I-1、I-2、I-4 はマージ済み）。起点 `c8b1e338d`。
- 下の順に、内側（domain）から外側（application、CLI）へ進める。1〜3 は互いに独立だが、4 以降は 1〜3 に依る。
- 共有のファイル（`tests/support/*`）は I-5、I-11 のブランチも変えているが、この Issue が先にマージされ、そちらが取り込む（Epic の計画）。衝突したら `origin/main` をこのブランチにマージして解く（rebase しない）。

## 実装step

テスト駆動（Red → Green → Refactor）で、受け入れ条件ごとに進める。

1. **ID の形（AC-455-02）**：`domain/ids.py` に `CANONICAL_ID_RE` を足す。`parse_scope_id` をそれに合わせる。単体のテスト（境界の値）を先に書く。
2. **スナップショットから本文と slug を外す（AC-455-01）**：`IssueFacts.body`、`ScopeNode.slug`、印の関数と異常のコードを消し、`_node_from_facts` と `_node_from_json` を直す。`FULL_READ_QUERY` と `_facts_from_rest`、`_fetched_from_graphql` から本文を外し、`create_issue` から `body` を外す。偽の `gh` の `scope()` を、印を付けない形にする。テスト：`test_canonical_structure.py`、`test_github_structure.py`、`test_github_snapshot.py`（古い形の取り直し）、`test_canonical_readiness.py`、`test_fake_github.py`。
3. **付け替えの判定とブランチ名の照合（AC-455-05、AC-455-06 の部品）**：`SCOPE_KIND_CHANGED`、`KindChange`、`kind_changes`、`renamed_scope`、`branch_names_scope` を `domain/canonical_structure.py` に足す。単体のテストを先に書く。
4. **カタログを平らに（AC-455-02、AC-455-03 の部品）**：`CatalogTree` を直下の `<ID>/` と `misplaced()` に書き直す。`test_catalog_tree.py` を書き直す。
5. **読む側の共通の部品（AC-455-03、AC-455-06）**：`canonical_scopes.py` から入れ子と重複を消し、`kind_changes`、`require_kind_unchanged`、`kind_change_warnings`、`snapshot_warnings`、`kind_change_error`、`resolve_canonical_scope`、`check_canonical_expectation` の新しい形を作る。`canonical_errors.py` に `SCOPE_KIND_CHANGED_RECOVERY` を足す。テストの部品 `tests/support/canonical_scopes.py` を平らな置き場にする。
6. **検査と状態（AC-455-04）**：`canonical_workspace.py` の `directory_anomalies` と `structure_item`、`canonical_status.py` の説明。`test_issue431_workspace.py`、`test_issue430_canonical_status.py` を直す。
7. **コマンド（AC-455-03、AC-455-05、AC-455-06）**：`canonical_branches.py`（既定の名前、停止）、`canonical_scope_read.py`（解決、`active set` の停止、Artifact のパス）、`canonical_worktrees.py`（`--expect-current` の停止と警告）。`test_issue431_branch.py` などを直し、`tests/cli_runtime/test_issue455_flat_ids.py` に付け替えのシナリオを足す。
8. **残りのテストの直し**：`test_issue430_canonical_sync.py`、`test_issue429_canonical_link.py`、`test_issue431_*` の残り、`test_migration_contract_copies.py`（印の比べ合わせを外す）。
9. **掃除**：消した名前が `src/spec_dock/runtime/` に残っていないことを検索で確かめる（AC-455-07）。`CANONICAL_FORMAT` が1のままであることをテストで確かめる。
10. **全体**：`make lint`、`uv run pytest`。変えたテストの一覧を `report.md` に書き、版3の振る舞いのテストを変えていないことを確かめる（AC-455-08）。

## 検証

| AC | 確かめ方 |
|---|---|
| AC-455-01 | 単体：印のない種類のラベル付きの Issue の要素が ID を持つ。スナップショットの JSON に `slug` がない。`slug` を持つ版1のファイルを置くと `ensure_fresh` が取り直す。偽の `gh` の記録で、GraphQL の問い合わせの文に `body` がなく、`POST …/issues` の本文が `title` と `labels` だけ |
| AC-455-02 | 単体（`test_canonical_structure.py`、`test_catalog_tree.py`）：`scope_id` と `parse_scope_id` の境界（`iss-00001`、`iss-99999`、`iss-100000`、`iss-000454`、`iss-454`、`iss-00000`、`iss-00454-foo`、`issue-00454`）。`CatalogTree` がそれらの名前と `ISS-00454`、隠し、リンク、ファイルを Scope にせず、ID の形の名前を `misplaced` にする |
| AC-455-03 | CLI（`test_issue431_scope_read.py`、`test_issue431_dependency_active.py`）：平らな一時のカタログで `scope show/list --json` の `path` が `spec-dock/initiatives/<ID>`、ディレクトリのない Scope は null で、`iss-00004-old/` や `epic-00002/issues/iss-00004/` を場所にしない。`active set` のリンクの先が `../initiatives/<ID>`、`artifact list/show` が `<ID>/artifacts` を読む |
| AC-455-04 | CLI（`test_issue431_workspace.py`、`test_issue455_flat_ids.py`）：4つの異常を置いたカタログで `workspace validate` と `canonical status --structure` の結果と並びと次の1手。`iss-00454/` と GitHub の epic で `SCOPE_KIND_CHANGED` がちょうど1件、同じ番号の MISSING と ISSUE_MISSING がない。古い名前が2つ、新しい名前もあるときも1件。種類のラベルが2つの Issue の `<ID>/` は `KIND_LABEL_MULTIPLE` だけ。SLUG_MISMATCH と DUPLICATE が出ない |
| AC-455-05 | CLI：`branch create` の既定の名前。単体：`branch_names_scope` の4つの例 |
| AC-455-06 | CLI（`test_issue455_flat_ids.py`）：付け替えのとき、`branch create`、`branch switch`（今の ID と古い ID、`--dry-run` でも）、`active set`（対象と祖先）、`worktree create --expect-current` が終了コード3（ブランチ、チェックアウト、リンク、worktree ができていない）。読むコマンド12通りが終了コード0で `warnings` に `SCOPE_KIND_CHANGED` を1件。古い ID（`iss-00454`、`ISS-00454`、`iss-454`）と `--expect-current` の古い ID が `SCOPE_KIND_CHANGED` と `details.current_id`。カタログが見えないときも古い ID は止まる |
| AC-455-07 | 単体のテストが `design.md` の公開の形を直接使う。消した名前の検索が0件。`CANONICAL_FORMAT == 1` |
| AC-455-08 | `make lint`、`uv run pytest` の全体。変えたテストがすべて canonical モードのものであること（`report.md` の一覧） |

- negative test：古い ID、付け替え、名前の外れ、壊れたスナップショット（`slug` の鍵、`id` と `kind` の食い違い）、カタログが見えないときの古い ID の解決、`--dry-run` での停止、種類が決まらない番号。`requirement.md` の「失敗・境界条件」の各項目は、AC-455-02（名前、隠し、リンク、ファイル）、AC-455-04（種類が決まらない番号、古い名前が2つ、新しい名前もある）、AC-455-06（カタログが見えないとき）で確かめる。
- 読むだけのコマンドが書かないこと：I-4 の `test_issue431_read_only.py` を平らな置き場で通す（`worktree list/show` が構造を読むようになっても、リポジトリ、カタログ、`.git`、GitHub に書かないこと）。
- 変えずに通すテスト：I-8 の移行のテスト（`tests/integration/migration/`）と、版3の振る舞いのテストのすべて。

## rollback

- **revert の条件**：マージの後に、この Issue の変更が原因で canonical のテストか版3のテストが落ち、I-5、I-11、I-15 のどれもまだこの Issue を取り込んでいないとき。PR を `git revert` すれば戻る。canonical モードはまだどのリポジトリでも使われていないので、利用者の運用への影響はない。
- **forward recovery**：I-5、I-11、I-15 のどれかが取り込んだ後は、revert すると、それらが使う公開の形が消えるので、revert せず、直す PR を出す。担当は統括が決める（この Issue の担当か、取り込んだ Issue の担当）。順序は、直す PR を先にマージし、取り込んだ側が `origin/main` を取り込み直す。
- migration：N/A（状態の置き場にもカタログにも、直す対象のデータがない。古い形のスナップショットは取り直しになる）。

## security / privacy / operability

- security / privacy：N/A。読む項目が減る（本文を読まない）だけで、新しい外部への送信はない。テストは外のネットワークを使わない。
- operability：付け替えのとき、止まる理由と次の1手（`SCOPE_KIND_CHANGED_RECOVERY`）を示す。`canonical status --structure` と `workspace validate` で見つけられる。

## exit / handoff

- **完了の条件**：AC-455-01〜08 を満たし、最終品質ゲート（同じ SHA で `make lint` と `uv run pytest` の全体、独立した2つのレビュー）に合格し、PR の CI が通り、マージできる状態の PR がある。マージは人が行い、`work finish` は統括の指示の後。
- **引き渡し**：
  - I-5：`resolve_canonical_scope`、`require_kind_unchanged`、`kind_changes`、`KindChange.directories`（`scope delete` で消す古いディレクトリ）、`branch_names_scope`、`create_issue(title, labels)`、`CatalogTree.find`。`scope create` と `scope import github` の `--slug` の拒否、書くコマンドと `work start`、`work finish` での停止は I-5。
  - I-11：`slug` のない `ScopeNode`、`branch_names_scope`。`created_at` と `closed_at` は I-11 が足す。
  - I-15：`CANONICAL_ID_RE.pattern`、`KIND_LABELS`、`ID_PREFIXES`。`migrate.py` の印の写しを消し、ID の正規表現の写しを比べるテストを足す。
  - テストの部品の新しい形（`design.md` の「変更対象」）。
- **残るリスク**：`report.md` に書く。
