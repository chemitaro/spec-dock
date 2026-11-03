---
種別: レポート（Issue）
ID: "iss-00513"
関連GitHub: ["#513"]
最終更新: "2026-11-02"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

- R-01：`pyproject.toml`、`uv.lock`、版のファイル（提供側と dogfood）を 0.5.1 にした。
- R-02：`migration.md`（提供側と dogfood の写し）に「## 0.5.1 への更新」を足した。#506〜#511 と #520 の要点を、各 PR の report とコードで確かめて書いた。
- R-03：`static-inventory.json` の `migration.md` と版のファイルに今のハッシュを入れ、0.5.0 のバイトを既知の古い版に足した。#509・#520 がすでに足した `finalize-artifact.py`、`SKILL.md`、`cli-redesign-guide.html`、`reference_cli.md` の既知の古い版は、今の main で確かめ、重ねて足していない。
- 足した既知の古い版（0.5.0 のバイト）：`spec-dock/docs/migration.md` `75c97976…`、`spec-dock/system/spec-dock-version` `a0ad5064…`（先頭8桁）。
- 統合テスト `tests/integration/test_issue513_release_0_5_1.py`：版、節、inventory（6資産、重複なし）、0.5.0 の資産を持つリポジトリが `installation update` で上がること。旧 `test_issue440_release_0_5_0.py` の「版が 0.5.0」のテストは 0.5.1 のテストに移して外した。
- dogfood：`installation update --dry-run` で、変更なし（0.5.1 と一致）を確かめた。
- R-04・R-05 はマージの後に統括が行う。

## Verification

- 仕様のレビュー（spec-reviewer opus / medium）：pass、P0・P1 なし、P3 1件。固定した sha256：requirement `6a59cf70…`、design `7ddf2835…`、plan `cc01d0c8…`（その後は手順の status のみ更新）。
- コードのレビュー（code-reviewer sonnet / high）：pass、P0・P1 なし、P3 1件（`worktree remove` の記述）→ 修正済み（`413ce3e1a`）。
- 最終品質ゲート（quality-gate-reviewer opus / high）：`413ce3e1a831f0cef3745a316b2b620f7399ba95` で pass、coverage complete、P0・P1 なし、P3 1件（情報のみ）。
- テストレーン同コミット：`make lint` exit 0、`uv run pytest` exit 0（3288 passed, 7 skipped）。
- 新しく作った wheel を一時の venv に入れ、`spec-dock --version` が 0.5.1 を返すことを確かめた。

## Residual Risks / Follow-ups

- 配布の PR（R-04・R-05）と、タグ `v0.5.1`（マージで `release-tag.yml` が作る）は、この Issue の外。


## マージの後（統括、R-04・R-05）

2026-11-03 に統括が行った。

- PR #525 のマージ（`24f291f9c`）で、タグ `v0.5.1` ができた。`git archive v0.5.1` から作った wheel を `uv tool install --force` で利用者の環境に入れ、`spec-dock --version` が `spec-dock 0.5.1` を返した。
- 4つのリポジトリで、一時の worktree（`worktrees/spec-dock-051/<名前>`）を作り、`installation update --backup-dir worktrees/spec-dock-051/backups/<名前> --yes` で配布資産を上げ（変更 6）、`canonical check --json` が終了コード0で通った。PR：input-devices#23、company-os#5、housing-lifecycle#243、taikyohiyou_project#2231。CI は input-devices・company-os・taikyohiyou_project で成功。housing-lifecycle は CI が手で起動するときだけ動く決まりで、push の前の検査（同じ `canonical check`）が通った。利用者が4件をマージした。
- R-05：input-devices の `README.md`、company-os の `integrations/spec-dock/contract.md` と `README.md`、housing-lifecycle の `README.md` の、SpecDock を 0.2.4（`4d25a8b`）に固定する記述を、`spec-dock/system/spec-dock-version` の版のタグを入れる形に直した（同じ PR）。会議の記録や決定の記録の過去の記述は変えていない。
- マージの後、5つのリポジトリの `spec-dock/system/spec-dock-version` が 0.5.1 で、`canonical status` のリンク、同期、変更が ok。
- 一時の worktree とブランチは消した。控え `worktrees/spec-dock-051/backups/` は #514 の片付けの対象として残す。
- 0.5.1 を入れた後、`spec-dock scope close epic-00424 --reason completed --yes` で epic-00424 を閉じた（epic-00512 の R-09）。
