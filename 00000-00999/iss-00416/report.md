---
種別: レポート（Issue）
ID: "iss-00416"
タイトル: "Restore Active Scope Links For Human Navigation"
関連GitHub: ["#416"]
最終更新: "2026-10-13"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00080", "init-00079"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

- `work start` の成功後、`active clear`（選択が空になったとき）、選択を解除した `work finish` の後、`active set @current` で、Git 無視の相対リンク `spec-dock/active/{initiative,epic,issue}` を直接対象の連鎖、または `system/active-none/<role>` に揃えるようにした。
- リンクの結果は `active.link` / `active.legacy.remove` の effect と、`ACTIVE_LINK_NOT_UPDATED` / `ACTIVE_LEGACY_NOT_REMOVED` の warning で報告する。失敗は warning だけで、選択の status / exit は変わらない（Q1）。
- 書くのは3つのリンク名だけ。実体の同名ファイル・ディレクトリ、`active` 自体の symlink、Git に無視されない `active/` には書かない。旧 writer の既知生成物6件（`context-pack.md`、`current-runbook.{json,md}`、`{initiative,epic,issue}.path`）は file / symlink のときだけ削除する（Q4）。
- provider 資産（`system/README.md`、`system/active-none/README.md`、`docs/reference_cli.md`、`docs/cli-redesign-guide.html`、installed skill `spec-dock`）と catalog の説明を更新し、`static-inventory.json` の sha256 と `known_old_sha256` を更新した。
- 未使用の旧 active テキスト renderer（`cli_text.render_active_{show,set,clear}_text`）を除去した。
- Issue 413 設計 D-01 の「第二の閲覧状態を増やさない」のうち、人間の閲覧手段を廃止した部分を本 Issue で上書きした。リンクは選択判定に読まれないため、選択状態は増えていない。AC-413-36 の保全範囲は「既知の旧生成物6件を除く」に狭まった（利用者決定 Q4、2026-10-13）。

## Verification

- TDD（Red → Green）: domain 2件、infra 11件、CLI 10件の新規テスト（`tests/unit/{domain,infra}/test_active_links.py`、`tests/cli_runtime/test_issue416_active_links.py`）。
- `make lint`: ruff check / format / mypy が成功。
- `uv run pytest tests/unit tests/cli_runtime`: 1686 passed、1 skipped（実装途中の snapshot。最終 candidate の全体結果は PR に記録する）。
- fresh wheel（`spec_dock-0.2.4`）の外部 console を、`gh` stub を使う hermetic consumer で実行: `work start` で3リンク作成と `git status` clean、`workspace validate` 成功、`active set @current` で欠けたリンクの修復と `context-pack.md` の削除、2回目は `unchanged`、`active clear --all` で fallback へ戻ることを確認した。
- dogfood: 候補 console の `active set @current` をこの worktree で実行し、`spec-dock/active/issue` が本 Issue を指すこと、`workspace validate` が成功し追跡ファイルが変わらないことを確認した。
- 既存のリンクを置いた状態で、インストール済み console の `workspace validate`、`workspace doctor`（`--raw` 含む）、`workspace sync`、`scope list`、`installation show` が成功し、Scope の重複が無いことを確認した。

## Residual Risks / Follow-ups

- 同じ worktree での並行操作や branch 切替の後、リンクが古くなる・dangling になることがある。`active set @current` または `active clear --all` で揃え直す。
- 削除した旧生成物は復元しない。
- この worktree と他の dogfood worktree の静的投影（`spec-dock/system/`、`.agents/skills/`）は未更新。インストール済み package の更新（利用者判断）の後、`installation update` で反映する。
