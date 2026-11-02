---
種別: レポート（Issue）
ID: "iss-00496"
関連GitHub: ["#496"]
最終更新: "2026-11-02"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

- `installation update`（`--dry-run` の `planned`、適用の `succeeded`、途中で止まった `partial`）が、`.claude/skills/spec-dock*` の古い写しを外す（外す予定の）枠ごとに、外枠の `warnings` に `CLAUDE_SKILL_LINK_MISSING` を1件出すようにした（`src/spec_dock/runtime/application/direct_static_update.py`）。
  - `details`：`slot`（例 `.claude/skills/spec-dock`）、`link_target`（`../../.agents/skills/<name>`）、`command`（`cd <根> && find <slot> -mindepth 1 -depth -type d -empty -delete && rmdir <slot> && ln -s <link_target> <slot>` の1行）。`message` は `sync-project-skills` とこのコマンドを含む。
  - 枠がリンク（壊れたリンクを含む）なら今までどおり枠を飛ばすので出さない。写しがない、2回目の更新、`installation uninstall` でも出さない。SpecDock はリンクを作らない。
- 葉の help（`installation update --help` の Writes）に1文を足した（`src/spec_dock/runtime/cli/catalog.py`）。
- `requirement.cue` は変えていない。仕様のレビューの P2（コマンドの安全の前提、partial のテスト）を取り入れ、`design.cue` の `details.commands`（列）を `details.command`（`&&` でつないだ1行）に変え、`plan.cue` に T-05 を足した。

### 0.5.0 の「更新」の節に書く契約の変更

- `installation update`（と `--dry-run`、`partial`）の結果に、新しい警告 `CLAUDE_SKILL_LINK_MISSING` が出ることがある（JSON の `warnings[]`、テキストの標準エラーの `warning [CLAUDE_SKILL_LINK_MISSING] …`）。終了コード、`status`、`effects`、`data.result` は変わらない。`warnings` を空と決めつけて読む利用者は、新しい要素を受け入れる。
- 警告が出たら、Claude Code で `sync-project-skills` を使うか、`details.command` を実行してリンクを置く。

## Verification

- 新しいテスト `tests/integration/test_issue496_claude_skill_link_warning.py`（8件。T-01〜T-05）を Red → Green で書いた。関連（issue496、issue421、issue413_assets）106件が合格。
- `scope check iss-00496`：誤り0、警告0。
- 仕様のレビュー（spec-reviewer opus/high）：round-1 合格（P0=0、P1=0、P2=2、P3=1。P2 と P3 は取り入れた）。
- コードのレビュー（code-reviewer opus/high、axis both、`9c11174f8..602575f18`）：合格、指摘0。
- 最終品質ゲート（quality-gate-reviewer opus/high、1人、campaign `iss-00496-g1`、commit `602575f18`）：レビューは合格（P0=0、P1=0、P3=1、範囲は完全）。テストのレーン：`make lint` exit 0、`uv run pytest` exit 0（4100 passed、8 skipped、24分14秒）。記録は作業ツリーの `.workbench/final-quality-gate/iss-00496-g1/closure.md`（Git の外）。

## Residual Risks / Follow-ups

- P3（ゲート FQG-001）：作業ツリーの根の道筋に単引用符やバックスラッシュがあると、テキストの標準エラーの文はエスケープされ、写してもそのままでは動かない（`cd` が失敗して `&&` で止まるので、ファイルは壊れない）。JSON の `details.command` は正しい。対応は不要とした。
- 壊れたリンクの診断は、この Issue の範囲外（リンクは Claude Code の側のもの）。
