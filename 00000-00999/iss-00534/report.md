---
種別: レポート（Issue）
ID: "iss-00534"
関連GitHub: ["#534"]
最終更新: "2026-11-04"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

SpecDock 0.6.0 のリリース変更を作り、マージできる状態の PR にした。マージ、タグ、導入、5つのリポジトリへの配布は統括が行う。

## Outcome

- 版を 0.6.0 にした（`pyproject.toml`、`uv.lock`、`system/spec-dock-version` の提供側と dogfood の写し）。
- `migration.md`（提供側と dogfood の写しはバイト一致）に「## 0.6.0 への更新」を足した。
- `static-inventory.json` に、0.5.1 から変わった配布資産7つ（`.gitignore`、`docs/README.md`、`canonical.md`、`cli-redesign-guide.html`、`reference_cli.md`、`migration.md`、版のファイル）の今のハッシュと、0.5.1 のバイト（タグ v0.5.1）を既知の古い版として入れた。fixture は `tests/fixtures/issue534/`。
- 統合テスト `tests/integration/test_issue534_release_0_6_0.py`：版、migration の節、inventory、0.5.1 の配布資産を持つリポジトリが `installation update` で 0.6.0 に上がること。0.5.1 の版固定テストは 0.6.0 のテストに置き換えた。
- 機能のコードは変えていない。

## Verification

- 仕様のレビュー（spec-reviewer opus/medium）：指摘0件で合格（pin: requirement 9e97243d…、design 061d09f4…、plan は初版 ecdceaef…）。
- コードのレビュー（code-reviewer sonnet/high）：P0/P1 0、P3 1（新しいエラーのコードが一部だけ）。見出しを「主な新しいエラーのコード」に直した（b630ada4e）。
- 最終品質ゲート（quality-gate-reviewer opus/high、1人）：コミット b630ada4e4f55e355e331bf8a4f60834ed5f8299 で合格。P0/P1 0、P3 2。`make lint` 合格、`uv run pytest` 3514 passed, 7 skipped。
- fresh wheel：`/private/tmp/spec-dock-0.6.0-dist-20261104091943/spec_dock-0.6.0-py3-none-any.whl`、新しい venv `/private/tmp/spec-dock-0.6.0-venv-20261104091943`。`spec-dock --version` は 0.6.0、`help` と `dashboard --help` が動く。

## Residual Risks / Follow-ups

- P3（情報のみ、直していない）：(1) migration.md が `?focus=<ID>` を新しい契約として挙げるが、`reference_cli.md` の「ダッシュボードのサーバーの契約」には載っていない（統括の依頼文の記述に従った）。(2) migration.md は `dashboard/service.log` を launchd・systemd の両方で増えるように読めるが、実際は launchd だけで systemd は journal。必要なら後の版の migration で直す。
- マージの後：タグ、パッケージの導入、5つのリポジトリへの配布、利用者の PC での `dashboard serve` と iPhone からの確かめは統括が行う。
