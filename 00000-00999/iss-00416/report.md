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
- リンクの結果は `active.link` の effect と `ACTIVE_LINK_NOT_UPDATED` の warning で報告する。失敗は warning だけで、選択の status / exit は変わらない（Q1）。
- 書くのは3つのリンク名だけ。実体の同名ファイル・ディレクトリ、`active` 自体の symlink、Git に無視されない `active/` には書かない。旧 writer の既知生成物（`context-pack.md`、`current-runbook.{json,md}`、`{initiative,epic,issue}.path`）を含め、役割名以外は変更・削除しない（Q4、FQG-416-007 を受けて削除から変更）。
- provider 資産（`system/README.md`、`system/active-none/README.md`、`docs/reference_cli.md`、`docs/cli-redesign-guide.html`、installed skill `spec-dock`）と catalog の説明を更新し、`static-inventory.json` の sha256 と `known_old_sha256` を更新した。
- 未使用の旧 active テキスト renderer（`cli_text.render_active_{show,set,clear}_text`）を除去した。
- Issue 413 設計 D-01 の「第二の閲覧状態を増やさない」のうち、人間の閲覧手段を廃止した部分を本 Issue で上書きした。リンクは選択判定に読まれないため、選択状態は増えていない。AC-413-36 の保全は維持した。

## Verification

- TDD（Red → Green）: domain 2件、infra 11件、CLI 10件の新規テスト（`tests/unit/{domain,infra}/test_active_links.py`、`tests/cli_runtime/test_issue416_active_links.py`）。
- `make lint`: ruff check / format / mypy が成功。
- `uv run pytest tests/unit tests/cli_runtime`: 1686 passed、1 skipped（実装途中の snapshot。最終 candidate の全体結果は PR に記録する）。
- fresh wheel（`spec_dock-0.2.4`）の外部 console を、`gh` stub を使う hermetic consumer で実行: `work start` で3リンク作成と `git status` clean、`workspace validate` 成功、`active set @current` で欠けたリンクの修復と `context-pack.md` の削除、2回目は `unchanged`、`active clear --all` で fallback へ戻ることを確認した。
- dogfood: 候補 console の `active set @current` をこの worktree で実行し、`spec-dock/active/issue` が本 Issue を指すこと、`workspace validate` が成功し追跡ファイルが変わらないことを確認した。
- 既存のリンクを置いた状態で、インストール済み console の `workspace validate`、`workspace doctor`（`--raw` 含む）、`workspace sync`、`scope list`、`installation show` が成功し、Scope の重複が無いことを確認した。

## Final Quality Gate

- 1回目（`e7400e66`、GPT-6 Pro）: fail。P1 が3件、P2 が2件。
  - FQG-416-001（検査後の root 差し替えで外部へ書込・削除）: fd 起点の操作に変更して修正。
  - FQG-416-002（リンク先の観測エラーが選択の status / exit を変える）: 役割ごとの例外処理に入れ、application 層でも OSError を warning に変換して修正。
  - FQG-416-003（ignore 規則に一致する追跡ファイルを変更）: `git ls-files` による追跡確認を加えて修正。
  - FQG-416-004（P2、空選択の `clear --from` が修復しない）: AC-416-03 の未達なので修正。
  - FQG-416-005（P2、Start dry-run が checkout 前の path を使う）: 残余リスクとして記録（下記）。
- 2回目（`a9e2ec78`、同じ会話）: fail。前回の P1 3件は closed。新しい P1 が1件。
  - FQG-416-006（役割名の確認後に並行 Start が置いた実体をリンクで置換）: 書込が必要なときだけ Start lock を待たずに取り、その中で観測し直して書くように変更。古いリンクの置換は退避して確かめる方式にし、lock を取らない並行 writer の実体も置換・削除しないようにした。
- 3回目（`5f4a6515`、同じ会話）: fail。FQG-416-006 は closed。新しい P1 が1件。
  - FQG-416-007（旧生成物の削除が、Start lock を取らない並行 `branch switch` の置いた追跡ファイルを消し得る）: 名前と種類では区別できず、Git はファイルを書いてから index を更新するため確認の窓を閉じられない。利用者判断（2026-10-13）で Q4 を「旧生成物は削除しない」に変更し、削除処理を取り除いた。

## Residual Risks / Follow-ups

- `work start --dry-run` のリンク計画は、checkout 前の Scope path で評価する。候補 tip で Scope ディレクトリが移動している場合だけ、計画と本実行のリンク先がずれ得る（FQG-416-005）。本実行は候補 tip の path を使う。

- 同じ worktree での並行操作や branch 切替の後、リンクが古くなる・dangling になることがある。`active set @current` または `active clear --all` で揃え直す。
- 旧 consumer には、旧 writer の古い `context-pack.md` などが残る。README で案内するが、利用者が不要なら手で消す。
- この worktree と他の dogfood worktree の静的投影（`spec-dock/system/`、`.agents/skills/`）は未更新。インストール済み package の更新（利用者判断）の後、`installation update` で反映する。
