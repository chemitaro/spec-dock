---
種別: レポート（Issue）
ID: "iss-00421"
タイトル: "Retire the Claude Code skill projection"
関連GitHub: ["#421"]
最終更新: "2026-10-22"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00080", "init-00079"]
---

# Result Summary

詳細: [Report Guide](../../../../../../docs/authoring/report.md)

## Outcome

- accepted ADR `20261022t104008z-adr`（2026-10-22、product owner が coordinator 経由で承認）に従い、`.claude` へのスキル投影をやめた。ADR `20261014t072234z-adr` の Decision 2・3 を改訂する。
  - init / update は同梱スキルを `.agents/skills/<name>/` にだけ配置する。`.claude/` には何も作らない。
  - `.claude` 側の4エントリを current inventory から retired inventory へ移した。登録したハッシュは、git 履歴で `.claude` 側に記録されたことのある5つ（`spec-dock/SKILL.md` は `f8086263…` と `4d8befe3…`、grill の3ファイルは各1つ）。
  - `package_retired_assets()` の allowlist を、`.claude/skills/spec-dock/` と `.claude/skills/spec-dock-grill-with-docs/` に限って拡張した。
  - update / uninstall は、`.claude`・`.claude/skills`・`.claude/skills/<slot>` のいずれかがリンクなら、その slot の退役エントリを飛ばす（`_linked_host_slot`）。リンクをたどらず、リンクとリンク先を変更しない。通常ファイルの `.claude` や、実体 slot 内のファイル単位の symlink は、従来どおり停止する。
- `spec-dock` SKILL.md、`overview.md`、`README.md`、`AGENTS.md` を、`.agents/skills` だけの配置と Claude Code 側の相対リンク（`.claude/skills/<name>` → `../../.agents/skills/<name>`）の説明に直した。grill スキルは変更していない。
- dogfood:
  - 候補 wheel の CLI で、この worktree だけに `installation update` を実行した。`.claude/skills/spec-dock*` の4ファイルを除去し、`.agents/skills/spec-dock/SKILL.md` と `spec-dock/docs/authoring/overview.md` を更新した。
  - 空になった2つの slot ディレクトリを、`../../.agents/skills/<slot>` への相対リンクに置き換えた。
  - 範囲外の既存差分の追従（coordinator の承認済み、別コミット）: 同じ update で、provider 側だけが `21a53c54e` で更新され dogfood が未追従だった次の4ファイルも現行版になった。`spec-dock/docs/cli-redesign-guide.html`、`spec-dock/docs/reference_cli.md`、`spec-dock/system/README.md`、`spec-dock/system/active-none/README.md`。内容は CLI の結果だけで、手編集はしていない。

## Verification

- テスト先行（Red → Green）。新しいテストと更新したテスト（307件）で23件の失敗を確認してから実装した。
  - 新規: `tests/unit/infra/test_issue421_claude_skill_retirement.py`、`tests/integration/test_issue421_claude_skill_retirement.py`
  - 更新: issue418 の unit / integration、issue413 の assets / wheel、`test_provider_distribution.py`、`test_authoring_kit_assets.py`（uninstall の件数 88 → 84）
- 受け入れ条件:
  - AC-421-01: `test_init_creates_nothing_under_claude` ほか。
  - AC-421-02: `test_update_retires_only_known_claude_copies_and_keeps_user_files`、`test_update_accepts_the_earlier_distributed_spec_dock_skill`。
  - AC-421-03: issue413 の `test_static_changes_refuse_unknown_current_or_retired_files_before_preservation` と hard link の parametrize（`.claude/skills/spec-dock/SKILL.md`）。
  - AC-421-04: `test_linked_claude_slots_are_left_to_the_host`（slot のリンク、リンク先なし、`.claude/skills` のリンク、外部への `.claude` リンク）と `test_other_redirected_claude_shapes_still_stop_before_any_effect`。
- `uv run pytest`（実装コミット `df49f6ee1`）: 2067 passed, 8 skipped。dogfood 更新後に、dogfood を読むテスト（`test_authoring_kit_assets.py`、`test_artifact_templates.py`）と issue418 / 421 の unit テストを再実行し、244 passed。
- `make lint`: ruff check、ruff format、mypy とも pass。
- fresh wheel（`df49f6ee1` を `git archive` で展開してビルドし、`/private/tmp/spec-dock-iss421-venv` に非 editable で導入）:
  - 一時リポジトリへの init で `.claude` が作られない。`workspace validate` の findings は0件。
  - ユーザーの 0.2.4（`4d25a8b4` のビルド）で init した一時リポジトリ（`.claude/settings.json` を追加）に update を実行した。dry-run は `.agents/skills/spec-dock/SKILL.md`・`overview.md` の change と `.claude` 4ファイルの retire を予定し、無変更だった。適用で同じ効果になり、バックアップには6ファイルの旧版が入った。`.claude/settings.json` と空の slot ディレクトリは残った。再実行は `unchanged`。
- dogfood（AC-421-06）:
  - 候補 CLI の update（バックアップ `/private/tmp/spec-dock-iss421-dogfood-backup`）で、`.claude` の4ファイルを retire し、`.agents/skills/spec-dock/SKILL.md`・`overview.md` と範囲外の4ファイルを change した。各ファイルは provider とバイト一致する。
  - リンク置換後、候補 CLI で `installation show`（`.claude` の表示なし、`unknown` は init_only の `spec-dock/workspace.json` だけで既存の差異）、`installation update --dry-run`（効果なし）、`installation update --yes`（`unchanged`、バックアップを作らない）、`installation uninstall --dry-run`（84件、`.claude` なし）がすべて exit 0 だった。前後で `.agents` の全ファイルのハッシュは変わらなかった。
  - `workspace validate` の findings は0件（インストール済み CLI・候補 CLI の両方）。
- PR: https://github.com/chemitaro/spec-dock/pull/422（`Refs #421`、自動クローズなし）。head `1c1eca72` で、CI validate、Commit identity、Provider CI（provider-tests、distribution parity の ubuntu / macOS）がすべて成功し、GitHub の状態は MERGEABLE / CLEAN だった（2026-10-22T11:29Z の観測）。

## Residual Risks / Follow-ups

- **旧 CLI**: ユーザーのツール環境の 0.2.4（`4d25a8b4` のビルド）は `.claude` 投影を含む。この dogfood で、その CLI の `installation show` は `.claude` 側の4ファイルを `unsafe` と表示した。`installation update --dry-run` は、新しい `.agents/skills/spec-dock/SKILL.md` を未知の内容として `PRECONDITION_FAILED`（効果0）で停止した。`.agents` が旧版のままリンクだけ作った worktree では、親チェーンの symlink で停止する（コード上の判断で、未実行）。パッケージの更新は範囲外で、マージ後に行う。
- **他の worktree**: main checkout と他の linked worktree の `.claude` コピーは未処理である。パッケージ更新後に、各 worktree で `installation update --backup-dir ABS --yes` を実行する。
- **Claude Code 側**: リンクの作成・削除は Claude Code 側のフックとスキル（`~/.claude`、別作業）に依存する。それがない環境では、Claude Code から SpecDock のスキルは見えない。
- **残るゲート**: 人間による PR のマージ。マージ後の `work finish` は別の操作である。
