---
種別: 実装計画書（Issue）
ID: "iss-00416"
タイトル: "Restore Active Scope Links For Human Navigation"
関連GitHub: ["#416"]
状態: "draft"
最終更新: "2026-10-14"
依存: ["requirement.md", "design.md"]
親: ["epic-00080", "init-00079"]
---

# iss-00416 Restore Active Scope Links For Human Navigation — 実装計画

詳細: [Issue Plan Guide](../../../../../../docs/authoring/issue-plan.md)

## Planning Level

- selected: `standard`
- 理由: 変更は Git 無視の派生リンクと、3コマンドの後段に限られる。リンクは正本ではなく、コードの revert だけで戻せる。
- risk factor: 公開 JSON の effects / warnings に `active.link` と `ACTIVE_LINK_NOT_UPDATED` が加わる。`active set` の説明と結果が変わる（Q3）。旧 consumer の `active/` の役割名 symlink に書込が戻る。旧生成物は触れない（Q4）。
- 再評価条件: 新しい CLI leaf を追加する、Start の排他時間を延ばす、役割名以外のファイルを変更・削除する、のいずれかになった場合は `strict` に上げる。

## 目標

AC-416-01〜08 を満たし、fresh wheel の外部 console で `work start` → `spec-dock/active/issue/requirement.md` を開ける状態を確認する。

## 順序・依存

1. 利用者決定 Q1〜Q4（2026-10-13 確定済み）を前提にする。
2. domain → infra → application → 呼び出し点 → 文書 → 旧 renderer 除去、の順。domain と infra は並行可能。
3. 既存テストの契約変更（旧 `active/` 保全テスト、`active set` の digest テスト）は、呼び出し点の実装と同じ step で更新する。

## 実装step

`tdd` スキルで各 step を Red → Green → Refactor で進める。

1. **domain `plan_links`**: Initiative / Epic / Issue 直接、未選択の4ケースのテストを先に書き、実装する。
2. **infra `sync_active_links`**: tmp dir のテストで、作成、一致、置換、実体 occupied、`active` が symlink、target_missing、dry-run 無書込、書込失敗時に一時リンクが残らないこと、検査後の root 差し替え・役割名への並行配置で実体が保全されること、未知名・旧生成物の不変を確認する。
3. **application `active_links`**: chain の導出と、outcome → effect / warning の変換をテストする。
4. **`work start`**: Issue 直接・Epic 直接で3リンクを確認する cli_runtime テスト、dry-run の `planned`、選択 publish 失敗時と `unchanged` 時にリンク処理が無いこと。
5. **`active clear` / `work finish`**: fallback リンクへの切替、選択が残る `unchanged` 時の不変、選択が空の `active clear` による修復、両者の dry-run。`active/` を無視させた fixture で、既知旧生成物の削除と他の旧状態の保全を確認する（Issue 413 の保全テストは無視されない `active/` の不変として残す）。
6. **`active set @current`（Q3）**: 欠けたリンクの修復で `succeeded`、一致時は `unchanged` と tree 不変、dry-run は `planned` で無書込。既存 `test_active_set_existing_direct_resolves_exact_selectors_without_acquisition_or_remote_calls` は `active/` を無視しない fixture なので変更不要。catalog の説明を更新する。
7. **warning 経路**: 実体ディレクトリ occupied で exit 0 と `ACTIVE_LINK_NOT_UPDATED` を確認する。
8. **読み取り無書込**: `active show` がリンクの有無に関係なく同じ結果で、書込しないこと。
9. **provider 資産の文書**: `system/README.md`、`system/active-none/README.md`、installed skill `install_root/.agents/skills/spec-dock/SKILL.md` を更新し、`static-inventory.json` の hash を更新する。この worktree の静的投影（`spec-dock/system/`、`.agents/skills/`）は、この Issue では更新しない。`installation update` は利用者環境にインストール済みの package の資産を使うため、ソースの変更は package 更新（利用者判断）の後でないと反映できない。fresh consumer で新しい資産を確認する。
10. **旧 renderer 除去**: `cli_text.render_active_show_text` / `render_active_set_text` と未使用の `ActiveViewResult` 系を、参照が無いことを確認して除去する。

## 検証

- `make lint`
- `uv run pytest`
- fresh wheel:
  ```bash
  uv build --wheel --out-dir /private/tmp/spec-dock-416-dist
  uv venv /private/tmp/spec-dock-416
  uv pip install --python /private/tmp/spec-dock-416/bin/python /private/tmp/spec-dock-416-dist/spec_dock-*.whl
  ```
  hermetic な一時 consumer で `work start` → `ls -l spec-dock/active` → `active clear` → `ls -l spec-dock/active` を確認する。
- dogfood: インストール済みの `spec-dock` には変更が入っていないため、fresh wheel の候補 console（`/private/tmp/spec-dock-416/bin/spec-dock --project <この worktree>`）で `active set @current --json` を実行し、`spec-dock/active/issue` が本 Issue を指すこと、`workspace validate` / `workspace sync` が成功し `git status` が clean のままであることを確認する（`active/` は Git 無視）。

## rollback

- コードの revert で戻す。リンクは Git 無視の派生物なので、残置しても選択や検証に影響しない。
- data migration: N/A（永続状態を追加しない）。

## security / privacy / operability

- リンクは worktree 内の相対パスだけを指す。`active` 自体が symlink の場合は書かないため、worktree 外への書込経路を作らない。
- 出力には役割名と理由だけを出し、旧ファイルの中身は読まない。

## exit / handoff

- AC-416-01〜08 の確認結果、lint / pytest / fresh wheel の結果、Issue 413 D-01 の閲覧側判断を上書きした旨を `report.md` に記録する。
- merge-ready の PR を作成し、merge は人間が行う。
- 残余リスク: 同じ worktree での並行操作によるリンクのずれ（Q3 で修復）、branch 切替後の dangling リンク。

## 追加作業（2026-10-14、利用者決定 Q5・FQG-416-008/009）

既存の step 1〜10 は書き換えず、以下を追加で行う。

- 背景: FQG 4回目（`7e37b754`）の P1 FQG-416-008。Start lock を取らない並行の `branch switch` が checkout で置いた追跡ファイルを、リンク同期が置き換え得る。利用者決定 Q5 で、`branch switch` も Start lock を取り、作業ツリーを書き換える SpecDock 操作とリンク同期を同じ lock で排他する。Git の環境には何も書かない。
- 再評価: Issue 413 の「排他は Start だけ」を広げるため、`branch switch` の公開挙動（`START_LOCK_BUSY`、`--lock-timeout`）が変わる。新しい CLI leaf は追加しない。Planning Level は `standard` のままとする。

11. **step 5 の記述の訂正（FQG-416-009）**: step 5 にある「既知旧生成物の削除」は、Q4 の変更（2026-10-13）で行わないことになった。実装とテストは「旧生成物を含め役割名以外は変更・削除しない」（`test_issue416_active_links.py` の保全テスト）で確定している。step 5 は当時の記録として残し、この step で置き換える。
12. **`--lock-timeout` の適用先（Red → Green）**: `branch switch` で `--lock-timeout` を受け付け、`work start` と `branch switch` 以外では exit 2 になるテストを先に書き、`cli/options.py` を変える。
13. **`branch switch` の Start lock（Red → Green）**: 別 process（または同じ process の別 fd）が同じ clone の Start lock を保持している間、`branch switch --lock-timeout 0` が `START_LOCK_BUSY`（exit 3、effects 空）で止まり、current branch・作業ツリー・直接記録が変わらないテストを先に書く。続けて `application/branch_operations.py` で、checkout の前に Start lock を取り、branch 占有・clean の再確認から checkout 後の確認まで lock の中で行う。lock が空いていれば従来どおり checkout する（既存の `test_issue413_branch.py` が通ること）。`--dry-run` は lock を取らない。
14. **リンク同期との排他（Red → Green）**: `branch switch` が Start lock を保持している間、リンク同期（`active set @current` など）が書かずに `ACTIVE_LINK_NOT_UPDATED(start_in_progress)` を出すことを確認する（既存の lock 経路の確認。必要ならテストを追加）。
15. **案内文書**: catalog の `branch switch` 説明、provider 資産の `docs/reference_cli.md`（C20 と「Start・Finishと排他」）、`docs/cli-redesign-guide.html`、installed skill `spec-dock` の `SKILL.md` に、`branch switch` も Start lock を取ること、同じノードの排他は SpecDock、同じブランチの排他は Git が担うこと、SpecDock を経由しない Git 操作と別 clone は範囲外であることを反映する。`static-inventory.json` の sha256 と `known_old_sha256` を更新する。
16. **検証**: `make lint`、`uv run pytest` 全体、fresh wheel の外部 console で、Start lock 保持中の `branch switch` が `START_LOCK_BUSY` で止まり、解放後は成功することを確認する。`.git` 配下にファイルが増えないことも確認する。
17. **記録と再レビュー**: `report.md` に Q5 と FQG 4回目の結果・対応を追記し、FQG の `review-response.md` を更新する。push 後、同じ会話で FQG 5回目を実行し、P0/P1 が無くなるまで繰り返す。合格後に PR を作成する（merge は人間）。
