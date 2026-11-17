---
種別: レポート（Issue）
ID: "iss-00663"
関連GitHub: ["#663"]
最終更新: "2026-11-18"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## レビュー記録

- 仕様のレビュー round-1（spec-reviewer opus / high、standard）：合格。P0 0、P1 0、P2 0、P3 1（片付けの候補の欄の段を描き直しで保つ直しを #659 の項に書いていた。正しくは #662（iss-00656 の R-09）。配るバイトの事実の誤りなので直した、6aba2177a）。結果 `.workbench/spec-review/iss-00663/round-1.json`、応答 `review-response.md`。
- 仕様のレビュー round-2（同じレビュアー）：**合格**。P0〜P3 0。結果 `.workbench/spec-review/iss-00663/round-2.json`、検査 `round-2.check.json`（valid、status pass）。固定したコミット 6aba2177a（S-01 の後、clean）。
- 合格した文書の sha256：requirement.cue `f1b231c2d8f078fc51b7c0903faeebd650ee3b4e9b65c409176f82cd06bd8895`、design.cue `1e0b825466159cd0c16bd71cd1562198eb0329272a0cda4940ddca8ec0fbb09d`、plan.cue `5b7e16202f1f20c1d87ebdfb7e24e187b4c4724346ff6d389b7509099a641354`（以後 plan.cue は手順の status だけを書き換える）。

## Outcome

SpecDock 0.9.8 のリリースの変更を作った（`git diff fa9824cb9 7b3c25650`、11ファイル）。機能のコードは変えていない。PR はまだ作っていない（統括の決定、下の「待ち」）。

- S-01（タスク担当）：`migration.md`（提供側と dogfood はバイト一致）の「## 0.9.7 への更新」の直後に「## 0.9.8 への更新」を足した（dcd52eaf6、仕様のレビューの P3 の直し 6aba2177a）。
- reference_cli.md は変えていない（契約と画面の道、書かれた操作が変わらない）。
- S-02（実装担当、3b094a06d）：版を 0.9.8 にし（`pyproject.toml`、`uv.lock`、版のファイルの提供側と dogfood）、`test_issue645_release_0_9_7.py` の版固定を外した。
- S-03（実装担当、7b3c25650）：`static-inventory.json` の2行の `sha256` を今のハッシュ（migration.md `ae9e47b6…`、版のファイル `ff35aa97…`）にし、v0.9.7 のバイトのハッシュ（`6ecfd102…`、`6c38d2d8…`）を `known_old_sha256` の末尾に足した。fixture `tests/fixtures/issue663/` の2つは v0.9.7 のタグのバイトと一致する（タスク担当が `cmp` で確かめた）。統合テスト `tests/integration/test_issue663_release_0_9_8.py`。
- S-04（タスク担当）：`git archive 7b3c25650` から作った wheel（sha256 `d7f02ec73e2d7f4829d8dbee9f763c9b0b71b3103669e49c80515032d039f346`）を隔離した venv（`/private/tmp/spec-dock-iss00663-1794943381/venv`）に入れ、`spec-dock --version` が `spec-dock 0.9.8` を返した。同じ venv で、この worktree（0.9.8）と orca-web（版のファイル 0.9.0）の `canonical check --dry-run --offline` が valid=true、failures なし。道具の環境は 0.9.7 のまま。

### 実装担当

- 最初に Codex GPT-6.1 Sol / medium（ctx_83bcb0a37734、launch.effective：codex・gpt-6.1-sol・medium）を起動した。chat-scratch の symlink の拒否で起動前に止まり、変更はなかった。計画の rationale（統括が了承済み）どおり停止し、Claude Opus 5.5 / medium（ctx_d36d406b2621、launch.effective：claude・claude-opus-5-5・medium）に切り替えた。
- 基準（6aba2177a）：リリースの統合テスト8ファイルで 16 failed / 9 passed（S-01 で migration.md のバイトが変わったことによる既知の失敗）。実装後：9ファイルで 28 passed。`uv lock --check`、`make lint` は合格。

### 待ち（統括の決定 2026-11-18）

最終品質ゲートの全テストで、範囲外の既存の不安定なテスト1件が落ちた（Verification）。統括は選択肢 C を選んだ。iss-00664 で見分けて直し、そのマージの後に origin/main を取り込んでゲートをやり直してから PR を作る。

## Verification

- 最終品質ゲート iss-00663-fqg-1 attempt 1（7b3c25650）：**閉じていない**。
  - レビュー（quality-gate-reviewer opus / medium）：合格。P0〜P3 0、coverage complete（`attempts/01/review.check.json`）。
  - `make lint`：exit 0。
  - `uv run pytest`：exit 1。1 failed / 4308 passed / 7 skipped（30分46秒）。落ちたのは `tests/unit/presentation/test_dashboard_allgraph_command_screen.py::test_the_motion_stills_and_watches_on_the_cross_repository_structure`（shots[1] の still が True）。この PR はダッシュボードの資産とテストを変えていない。開始のコミット fa9824cb9 のきれいな取り出しで単独に5回走らせると4回落ちた。HEAD では3回のうち2回落ちた（`attempts/01/baseline/note.md`）。
  - キャンペーン：`.workbench/final-quality-gate/iss-00663-fqg-1/`（worktree `/Volumes/990p2t/workspace/worktrees/orca/spec-dock/iss-00663`）。

## 逸脱と判断

## Residual Risks / Follow-ups
