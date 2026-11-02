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

