---
種別: 実装計画書（Issue）
ID: "iss-00421"
タイトル: "Retire the Claude Code skill projection"
関連GitHub: ["#421"]
状態: "draft"
最終更新: "2026-10-22"
依存: ["requirement.md", "design.md"]
親: ["epic-00080", "init-00079"]
---

# iss-00421 Retire the Claude Code skill projection — 実装計画

詳細: [Issue Plan Guide](../../../../../../docs/authoring/issue-plan.md)

## Planning Level
- 選択: `standard`
- 理由: shipped asset API（インベントリと uninstall の件数）を変えるが、既存の retired の仕組みを使い、新しい分岐は1つだけである。
- risk factor: リンク経由で `.agents` 側の正本を消すこと、既存 consumer の update 経路。
- 再評価条件: `.claude` のリンクを spec-dock が作成・削除する必要が出たら、`strict` へ上げる。

## 目標
- Requirement の AC-421-01〜06 を、テスト先行の回帰テスト、fresh wheel の CLI、dogfood の実地確認で満たす。

## 順序・依存
1. P0: ADR `20261022t104008z-adr` の accepted（2026-10-22、product owner が coordinator 経由で承認済み）。
2. S01（Red）→ S02（Green）→ S03（文書）→ S04（検証）→ S05（dogfood）→ S06（記録と PR）。

## 実装step
- S01（Red）: 次のテストを先に書き、失敗を確認する。
  - fresh init で `.claude` がない。
  - 旧版のコピーの退役（dry-run・apply・再実行・バックアップ・利用者ファイル）。
  - リンクの4形（slot、`.claude/skills`、`.claude`、リンク先なし）での init / show / update / uninstall。
  - inventory の unit テスト、uninstall の件数、wheel の検査、文書の検査。
- S02（Green）: インベントリ、`static_assets.py`、`asset_layout.py`、`direct_static_update.py` を Design のとおり変える。
- S03（文書）: `spec-dock` SKILL.md、`overview.md`、`README.md`、`AGENTS.md` を直し、インベントリの sha256 と `known_old_sha256` を更新する。
- S04（検証）: `make lint`、`uv run pytest`、fresh wheel の隔離環境での init・update。
- S05（dogfood）:
  - 候補 wheel の CLI で、この worktree だけに `installation update --target <this worktree> --backup-dir <未使用の /private/tmp/...> --yes` を実行する。
  - 空になった `.claude/skills/<slot>` を削除し、`../../.agents/skills/<slot>` への相対リンクを作る。
  - 候補 CLI の `installation show`・`installation update`（dry-run）と `workspace validate` がエラーにならないことを確認してコミットする。
- S06: Report を書き、コミットし、PR を作る（Issue #421 を関連付け、自動クローズしない）。

## 検証
- AC-421-01〜04: 新しい統合テストと、更新した既存テスト。
- AC-421-05: `make lint`、`uv run pytest`。
- AC-421-06: S05 の実行結果。

## rollback
- マージ前: ブランチの revert。
- マージ後: provider の revert と再配布。dogfood は、リンクのコミットを revert して、旧 CLI で update する。

## exit / handoff
- 完了の条件: Report に証拠を残し、PR がマージ可能な状態であること。マージは人間が行う。
- `work finish` はマージ後の別操作とする。
- 残余リスク: 旧 CLI でのリンクの worktree の扱い、他の worktree が未更新であること。
