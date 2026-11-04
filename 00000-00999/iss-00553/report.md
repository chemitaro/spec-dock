---
種別: レポート（Issue）
ID: "iss-00553"
関連GitHub: ["#553"]
最終更新: "2026-11-04"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

SpecDock 0.7.0 のリリース変更を作り、マージできる状態の PR にした。マージ、タグ、導入、5つのリポジトリへの配布、dogfooding の確かめは統括が行う。

## Outcome

- 版を 0.7.0 にした（`pyproject.toml`、`uv.lock`、`system/spec-dock-version` の提供側と dogfood の写し）。
- `migration.md`（提供側と dogfood の写しはバイト一致）に「## 0.7.0 への更新」を足した。内容：`todo` の10のコマンド（61 → 71。#549）、集約と `todo show <REF>`、`dashboard summary` の `todos`（#550）、設定の3段、`todo check` と `cue`、`TODO_*`、スキルの規則と `docs/todo.md`（#551）、ダッシュボードの表示の設定と常駐の `service install` のやり直し（#552）、構造の図の既定の変更・保存のキー `v2`・`active_at`（#556）と配置の改め（#560）、最初の1手、戻し方。リリースの時点で main に入っていた #549・#550・#551・#552・#556・#560 を書いた（#535・#554 は入っていない）。
- `static-inventory.json`：`migration.md` と版のファイルの今のハッシュを入れ、0.6.0 のバイト（タグ v0.6.0）を既知の古い版に足した。ほかの変わった配布資産（スキル、README、guide、canonical、cli-redesign-guide、reference_cli）は前の Issue が入れていた。fixture は `tests/fixtures/issue553/`。
- 統合テスト `tests/integration/test_issue553_release_0_7_0.py`：版、migration の節（と写しの一致）、inventory、0.6.0 の配布資産を持つリポジトリが `installation update` で 0.7.0 に上がる（8つが変わり、`docs/todo.md` が補われる）こと。0.6.0 のテストの版固定は外した。
- 機能のコードは変えていない。

## Verification

- 仕様のレビュー（spec-reviewer opus/medium）：指摘0件で合格（コミット 845b455b0、requirement b18256d6…、design 20be37b8…、plan 7be8ff8f…）。その後 #552・#560 の取り込みに合わせて requirement と design の文言を直した。
- コードのレビュー（code-reviewer sonnet/high）：e3d7f8d0b で指摘0件。
- 最終品質ゲート（quality-gate-reviewer opus/high、1人、コミット ebb29c38f32f4e957f54db95a037c0ede624296a、base は merge-base 48e04934d）：
  - レビューの段：合格（P0〜P3 すべて 0、範囲は完全）。
  - テストの段：`make lint` 合格。`uv run pytest` は 3654 passed、7 skipped、1 failed（65分）。失敗は #560 の時間制限のテスト `tests/unit/presentation/test_dashboard_graph_js.py::test_the_250_scope_structure_routes_within_a_second`（1379ms > 1000ms）。このマシンの load が 40〜55 だったための環境の要因とみている（この Issue の変更はこのテストにもコードにも触れない）。負荷が高いまま単独で3回やり直しても失敗した。統括の了承（案 A）で、負荷が下がってからこの1件だけ再実行し、PR の CI でも確かめる。結果は下の「環境の要因の確認」に書く。閾値の見直しは統括が別に扱う。
  - 記録は `.workbench/final-quality-gate/iss-00553-g1/`。ChatGPT のレーンは使っていない（無効）。
- `spec-dock scope check iss-00553`：誤り0、警告0。

## 環境の要因の確認

- PR #565（head ebb29c38f）の CI：Provider CI の `provider-tests` が成功（`uv run pytest` 3637 passed、25 skipped、失敗0。時間制限のテストを含む）、`Provider distribution parity`（macOS・ubuntu）も成功。GitHub は OPEN／MERGEABLE／CLEAN（2026-11-04T09:36Z 付近の観測）。
- ローカルの単独の再実行：このマシンの load が下がらず（40〜133）、行えなかった。そのため時間制限のテストの失敗は、負荷による環境の要因とみなし、CI の合格で確かめた。統括の了承（案 A）に沿う。

## Residual Risks / Follow-ups

- 時間制限のテストの閾値は統括が別に扱う。
- マージの後：タグ、パッケージの導入、5つのリポジトリへの配布、dogfooding（別の worktree で登録したタスクが見えること R-01、2つのリポジトリの集約 R-10、統括と作業者がスキルの規則で登録・完了すること R-14）は統括が行う。
