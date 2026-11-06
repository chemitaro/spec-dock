---
種別: レポート（Issue）
ID: "iss-00580"
関連GitHub: ["#580"]
最終更新: "2026-11-06"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

SpecDock 0.9.0 のリリース変更を作り、マージできる状態の PR にした。マージ、タグ、導入、配布は統括が行う。

- 版を 0.9.0 にした（`pyproject.toml`、`uv.lock`、`system/spec-dock-version` の提供側と dogfood の写し）。
- `migration.md`（提供側と dogfood の写しはバイト一致）に「## 0.9.0 への更新」を足した。`git log v0.8.0..origin/main`（21コミット、PR #572 #574 #575 #578 の分）でマージ済みの #574（状態の色と形、`progress`・`revision`）、#575（Initiative の横並び）、#578（隙間の直し、`frameExits`）、#572（`/favicon.ico`、`/assets/favicon.svg` ほか）と、常駐の自動の起動し直し、戻し方を書いた。#572 の時間のテストの測り方は利用者に影響しないので書いていない。
- 0.8.0 の節の訂正：0.9.0 の節に「0.8.0 の節の訂正」を足し、#568 の意味の変更（構造の古さは `max(スナップショットの fetched_at, 確かめた checked_at)`。probe 失敗・欠落・未来の時刻では `fetched_at` だけ）を、欄の名前と型は同じことと合わせて書いた。**0.8.0 の節の本文は直していない**。理由：0.8.0 のバイトは配布済みで `known_old_sha256` に入れて受け入れる版であり、履歴としてそのまま残す。訂正は直後の節にあり、読み手は続けて読める。
- `static-inventory.json`：`migration.md` と版のファイルの2行だけ、今のハッシュにし、v0.8.0 のバイトを `known_old_sha256` に足した（ほかの行は変えていない）。fixture は `tests/fixtures/issue580/`（v0.8.0 のタグから取った）。
- 統合テスト `tests/integration/test_issue580_release_0_9_0.py`：版、節と写しの一致、inventory、0.8.0 の配布資産を持つ consumer が `installation update` で 0.9.0 に上がること。0.8.0 のテストの版固定は外した。機能のコードは変えていない。

### 次の版の移行の注記に要る契約の変更

なし（この PR は 0.9.0 の注記そのものを書いた）。

## Verification

- 仕様のレビュー（spec-reviewer opus/medium、round-1b。round-1 は私が作業ツリーを変えたため binding 失敗で、指摘ではない）：合格（P0・P1・P2 なし、P3 1件＝R-02・R-03 の受入の一部に対応するテストが plan にない。情報のみ）。requirement 0fe240b5…、design bb1c32af…、plan c049f7f9…（その後 plan は status だけ done に更新、最終 07b9c3f1…）。
- コードのレビュー（code-reviewer sonnet/high、66175daa3）：合格。P3 1件（訂正の文に probe の除外条件がない）を fe38c06e1 で直した。
- 最終品質ゲート（quality-gate-reviewer opus/high、1人、fe38c06e19c103616b33b8d35875fa53e258dcc2）：P0〜P3 すべて 0、coverage 完全。`make lint` 合格、`uv run pytest` 3759 passed、7 skipped、失敗 0（32分）。記録は `.workbench/final-quality-gate/iss-00580-g1/`（closure.md）。ChatGPT のレーンは使っていない（無効）。
- `spec-dock scope check iss-00580`：誤り0、警告0。

## Residual Risks / Follow-ups

- `work finish iss-00580` は実行していない（マージの後に統括が行う）。
- マージの後：タグ v0.9.0、パッケージの導入、配布、画面の確かめは統括が行う。
- PR の作成の直前に `origin/main` を確かめた時点で、取り込む差分はなかった。
