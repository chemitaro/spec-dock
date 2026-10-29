---
種別: レポート（Issue）
ID: "iss-00456"
タイトル: "Flatten Specs In Canonical Migration Script"
関連GitHub: ["#456"]
最終更新: "2026-10-29"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00424", "init-00423"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

移行のスクリプト `scripts/migrate-to-canonical/migrate.py` を、平らなカタログ（`spec-dock/initiatives/<区切り>/<ID>/`）に合わせて直した。本物の spec-dock の写しの予行演習で、書き換えられないリンクは0件だった。

- **登録（R-456-02、03）**：本文の印の写し（`SLUG_RE`、`read_slug_marker` など）と、その登録、照合、取り消しを消した。`register` は本文を読まず、書かない。作る Issue には題名と種類のラベルだけを送る。作った Issue の見つけ直しは、種類のラベル、題名、作成者（`GET /user`）、作成の時刻（結果の記録のない最も古い予定の時刻の5分前より後）で行い、2件以上なら番号の一覧を付けて止まる。`undo` も同じ条件で探す。
- **写した値（R-456-01）**：`CANONICAL_ID_RE`、`BUCKET_SIZE`、`scope_bucket`、`scope_relative`（I-16 の `design.md` の公開の形と同じ計算）、従来の題名の規則 `LEGACY_TITLE_RE` と `legacy_slug`、従来の `rules.md` の先 `LEGACY_CHILD_RULES` を足した。
- **平らにする写し（R-456-04）**：`nested_layout`、`FlatMap`、`NestMap`、`rewrite_links`、`link_report`、`TreeFlattener` を足した。Scope は置き場と `.meta.json` の `type`、`id`、`github.issue_number` で決める。リンクは、シンボリックリンク、Markdown の `[…](…)` と `[…]: …`、HTML の `href` と `src`（統括の判断 Q3）を、新しい位置から同じ先を開くように書き換える。Markdown のコードの中は変えない。
- **`plan`（R-456-05）**：`data.flatten`（平らにできないもの、仮の場所 `pending`、リンクの一覧）を出す。対象のリポジトリには何も書かない（oid はメモリーの上で求める）。
- **`build-canonical`（R-456-06）**：先端を写して平らにできないものがあれば止まり、subtree split の各コミットを同じ写しで作り直す（作成者、日時、メッセージを保ち、署名のヘッダーを外す）。履歴で平らにできないパスは、そのコミットからだけ落とし、`data.history` に数と例を出す（統括の判断 Q2）。
- **`move-local`、`adopt-worktree`（R-456-07）**：平らにした位置へ移し、リンクを書き換える。`move-local` は切り替え前のコミットと、そのチェックアウトのブランチの `adopt/` の記録から Scope を決める。`adopt-worktree` は分岐点を写したツリーで C を見つけ、写した後の中身で消す前の一致を確かめる。
- **`export-legacy`（R-456-08）**：GitHub の親子で入れ子に戻し、slug を切り替え前の `.meta.json`、なければ題名（英数字の規則に合わなければ `untitled`）から決め、リンクを逆に書き換え、`epics/rules.md` と `issues/rules.md` を置き直す。戻せないもの（`PARENT_MISSING`、`KIND_RULE`、`PARENT_CONFLICT`、`KIND_LABEL_MULTIPLE`、`SCOPE_DIRECTORY_MISSING`、`SCOPE_ISSUE_MISSING`、`SCOPE_KIND_CHANGED`、`SCOPE_DIRECTORY_MISPLACED`、`CATALOG_PATH_OUTSIDE_SCOPE`）があれば、`--apply` の有無によらず、何も書かずに止まる。
- **`verify`（R-456-09）**：origin の canonical を使い捨てのクローンに取り、`.meta.json` と、`<区切り>/<ID>/` の外れと、ない `<区切り>/<新しい ID>/` を不一致にする。
- **README（R-456-10）**：印の説明を消し、「平らにする写し」と「入れ子への戻し方」の節を足した。
- **テストの助け**：偽の GitHub（`tests/support/fake_github.py`）に、Issue の作成者と作成の時刻を足した（足すだけ）。`tests/support/migration_repo.py` に、シンボリックリンクの書き込み、平らにした場所 `flat_path`、リンクの多い仕様のツリー `linked_specs`、切り替えまでの流れ `migrated` と `merge_cut` を足した。テスト用の bare の origin で `receive.autogc` と `gc.auto` を止めた（push の後の裏の gc と、ローカルの clone の写しがぶつかり、`git clone` が `failed to copy file` で落ちることがあった。直す前は4回のうち2回失敗し、直した後は5回とも通った）。

## Verification

### 自動のテスト

| AC | テスト |
|---|---|
| AC-456-01 | `test_migrate_register.py::test_register_adds_structure_maps_local_scopes_and_verify_matches`（本文の `PATCH` なし、作成の要求は題名とラベルだけ）、`test_migrate_plan.py`（`by_operation` に `issue.marker` なし） |
| AC-456-02 | `test_a_register_stopped_after_the_creation_picks_that_issue_up`（時計が3分進んでいても拾う）、`test_two_matching_issues_stop_register_with_their_numbers`（`register` と `undo` が番号の一覧で止まる）、`test_issues_by_someone_else_or_from_before_the_intent_are_not_picked_up`、`test_a_lost_create_answer_is_recovered_without_a_second_issue` |
| AC-456-03 | `test_migrate_canonical.py`：`test_build_canonical_pushes_the_flattened_history_with_format_one_files`（すべてのコミットが平らで `.meta.json` なし、先端の中身が一致）、`test_history_commits_drop_what_cannot_be_flattened_and_stay_flat`、`test_a_tip_that_cannot_be_flattened_stops_plan_and_build_canonical` |
| AC-456-04 | `test_migrate_flatten.py`：単位のテスト（パスの対応、R-456-04 の各種のリンク、コードの中、HTML、捨てる `rules.md`）と、`test_every_link_of_a_linked_tree_opens_through_the_flat_catalog`（`canonical link` の後に `spec-dock/initiatives` を通して、独立の確かめ方ですべてのリンクを開く）、`test_unrewritable_links_are_listed_by_plan_and_build_canonical` |
| AC-456-06 | `test_migrate_checkouts.py`（平らな位置への移動と取り込み）、`test_move_local_rewrites_moved_links_and_refuses_files_without_a_place`、`test_adopt_worktree_removes_files_whose_links_were_rewritten_and_refuses_unflattenable_specs` |
| AC-456-07 | `test_export_legacy_nests_back_with_the_original_links_and_new_scope_slugs`（`untitled` と題名からの slug、リンクの字面の往復、従来モードの `workspace validate`）、`test_export_legacy_stops_before_writing_when_the_catalog_cannot_nest_back`（3つの場合、`--apply` なしでも終了コード2）、`test_export_legacy_rebuilds_schema_three_metadata_that_legacy_commands_read` |
| AC-456-08 | `test_migration_contract_copies.py`（`CANONICAL_ID_RE`、区切りの値の例、従来の題名と slug、`rules.md` の先）。区切りをパッケージの `scope_bucket` と比べるテストは、I-16 のマージの後に足す（未確認） |
| AC-456-09 | `test_verify_checks_the_flat_layout_of_origins_canonical` |
| AC-456-11 | `test_plan_before_register_places_local_scopes_by_the_plan_and_writes_nothing`（参照、作業ツリー、`git count-objects -v` が変わらない） |

- `uv run pytest -q tests/integration/migration tests/unit/infra/test_migration_contract_copies.py`：94 passed（`77febaf25`）。
- 偽の GitHub の変更の影響：その変更の後に全体のテストを流し、3004 passed、8 skipped（`99a437adc` の作業中の状態。偽の GitHub を使うほかのテストの結果は変わらない）。
- AC-456-10 の変えたファイル（`git diff --name-only origin/main...HEAD`）：`scripts/migrate-to-canonical/{README.md,migrate.py}`、この Issue の `requirement.md`、`design.md`、`plan.md`、`report.md`、`tests/integration/migration/` の5つ、`tests/support/{fake_github.py,migration_repo.py}`、`tests/unit/infra/test_migration_contract_copies.py`。`src/` と従来モードのテストは変えていない。

### 本物の spec-dock での読むだけの `plan`（2026-10-29）

- 本物の main のチェックアウト（`/Volumes/990p2t/workspace/tools/spec-dock`、`origin/main` = `95bbb7a1c`）に、このブランチの `migrate.py plan`（`--apply` なし、作業の記録は一時ディレクトリ）を、本物の GitHub を読むだけで実行した。終了コード0、約10秒。
- 前後で、参照、`git count-objects -v`、`git status --porcelain --ignored` の要約が同じだった（本物のリポジトリに書いていない）。
- 結果：Scope 263（Initiative 4、Epic 27、Issue 232）、依存162。平らにできないもの0、仮の場所1（`init-local-00003-architecture-maintenance-and-hardening`。登録で新しく作る予定）。書き換えるリンク492、書き換えられないリンク0、移行の前から切れているリンク35。異常は `TITLE_MISMATCH` 35、`LOCAL_SCOPE` 2、`CLOSED_PARENT_OPEN_CHILD` 1（止めるものなし）。登録の予定は687回の書き込み（約82分）。

### 予行演習（AC-456-05、2026-10-29）

本物の spec-dock の `origin/main` を、内蔵のディスクの一時ディレクトリ（`/private/tmp/specdock-rehearsal-i15.*`）に `--no-local` で写した bare の origin とそのクローンで、偽の GitHub（本物の `.meta.json` から作った。本物の `register` はまだないため）と一時の `XDG_STATE_HOME` と作業の記録の置き場を使って行った。CLI はこのブランチの wheel を一時の venv に入れたもの。手順の助けは、この Issue の `.workbench/rehearsal.py`（Git では無視）。本物のリポジトリと GitHub には書いていない。終わった後に一時ディレクトリを消した。

1. 準備の代わりに、0.3.0 の配布資産（`spec-dock/.gitignore` の無視の3行と版のファイル）を写したコミットを、使い捨てのクローンの既定のブランチに足した（本番では `installation update` の PR。I-9）。最初の試行では、これがないので `cut` が設計どおり止まった。
2. `register --apply`（偽の GitHub、約1秒）、`verify`（不一致0）、`build-canonical --apply`（約215秒）、`cut --apply`、切り替えのブランチの早送りの取り込み、`move-local --apply`、`canonical link --no-schedule`（succeeded）、`canonical sync`（unchanged）。
3. `build-canonical`：2,818ファイル、書き換えたリンク492、**書き換えられないリンク0**、移行の前から切れているリンク35。履歴は2,403コミットを作り直し、725コミットから平らにできないパスを落とした（どの Scope にも入らないもの65,312、ID を決められない Scope 105、`epics/` の下の仮置き714、同じ ID 15）。どの Scope にも入らないものの例は `.gitignore`、`LICENSE`、`README.md`、`pyproject.toml`、`src/spec_dock/__init__.py` で、subtree split が、仕様のツリーのないブランチ側のコミットにリポジトリ全体を含めたものである（仕様ではないので、落とすのが正しい）。カタログの直下は `00000-00999/`（263の `<ID>/`）と管理ファイルだけだった。
4. 独立の確かめ（チェックアウトの `spec-dock/initiatives` のリンクを通して、シンボリックリンクは実際のファイルシステムで、Markdown と HTML は字面で開く）：移行の前は879個のうち32個が切れていて、移行の後は850個のうち32個が切れていた（29個の差は、捨てた `epics/rules.md` と `issues/rules.md`）。後で切れている3つの文字列（`../../../docs/authoring/chatgpt-pack.md` など）は、先のファイルがリポジトリになく、移行の前から切れていたリンクを、新しい深さで書き換えたものである。**移行の前に開けて後で開けなくなったリンクは0件**。
5. `canonical check`：最初は、写した配布資産が足りず（`spec-dock/docs/ci/spec-dock-check.yml`。準備の代わりのコミットに含めなかった）`STATIC_ASSET_INVALID` の1件で失敗した。その資産を一時のクローンに足すと通った（valid、失敗0）。本番の準備の `installation update` で入る資産である。
6. `export-legacy --apply`（約7秒）：異常0、書き換えて戻したリンク492、戻せないリンク0。戻したブランチで、従来モードの `workspace validate` が通った（findings なし）。移行の前の追跡されたファイルのすべてが戻り、`.meta.json` は `revision`、`lifecycle`、置き換えた ID、番号のほかは一致し、ほかのファイルは**すべてバイト列まで一致**した（往復で字面が戻らない3種類のリンクは、本物の spec-dock にはなかった）。戻した後のリンクの切れは32個で、移行の前と同じだった。

## Residual Risks / Follow-ups

- **I-16 との比べ合わせ（未確認）**：区切りの計算は I-16 の `design.md`（`60ea01ccb`）の値で写し、値の例でだけ確かめた。I-16 のマージの後に `origin/main` を取り込み、パッケージの `scope_bucket`、`scope_relative`、`BUCKET_SIZE` と比べるテストを足す（plan の S9）。
- **予行演習の GitHub は偽物**：本物の `register` は I-10 で行う。`plan` は本物の GitHub を読むだけで確かめた。本物の GitHub の上での `register`、`verify`、作った Issue の見つけ直し（作成者と作成の時刻の値の形）は未確認。
- **履歴で落ちるもの**：spec-dock の canonical の履歴では、725コミットから平らにできないパスが落ちる。元のリポジトリの既定のブランチの履歴に残る（統括の判断 Q2）。
- **`build-canonical` の時間**：spec-dock で約215秒。I-10 の凍結の時間の見積もりに入れる。
- **仕様のツリーの外から中を指すリンク**：`docs/issue-plans/iss-00413-external-cli-state/artifacts/source-basis.md` などは、`cut` の後に切れる。この Issue の範囲の外（写すのは仕様のツリーの中だけ）なので、I-10 に引き渡す。
- **Epic の文書**：Epic の `design.md` 11章の、書き換えるリンクの種類に HTML を足すこと（統括が次の Epic の文書の直しで行う）と、区切りの決まり（I-16）。
- **作成者の名前**：見つけ直しは `gh` の利用者の名前と Issue の作成者を比べるので、GitHub App のトークンでは使えない（README に書いた）。
