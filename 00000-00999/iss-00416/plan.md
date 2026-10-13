---
種別: 実装計画書（Issue）
ID: "iss-00416"
タイトル: "Restore Active Scope Links For Human Navigation"
関連GitHub: ["#416"]
状態: "draft"
最終更新: "2026-10-13"
依存: ["requirement.md", "design.md"]
親: ["epic-00080", "init-00079"]
---

# iss-00416 Restore Active Scope Links For Human Navigation — 実装計画

詳細: [Issue Plan Guide](../../../docs/authoring/issue-plan.md)

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
