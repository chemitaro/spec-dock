# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

- 重複メンバーを含む workspace 宣言（例 `{"schema_version":99,"schema_version":4}`）は版4として受け付けず、`ValueError` → `PRECONDITION_FAILED`（終了コード3）で止まる。`workspace doctor --raw` は宣言を解釈しない経路なので、0.5.0 と同じく観測（`invalid_json`、終了コード7）を返す（AC-440-01 の形を保つ）。
- `resolve_observed_context` は、版3の再読み取りで宣言が消えても `assert` ではなく `ValueError` を出し、既存の呼び出し元（`workspace sync`、`work start`）が `unavailable` の行にする。
- 変更：`src/spec_dock/runtime/application/project_context.py`（`_read_declaration_object`、`_unique_members`）。`read_guarded_json` は他の JSON のために変えていない。
- 最終の SHA：`984abc40bd496529463f32102a35bce6383346be`。
- requirement.cue は変更していない。

## Verification

- 仕様のレビュー（`spec-review`、spec-reviewer opus / medium）：合格（P0・P1 なし、P2 1件＝`declares_schema_4` 経由の挙動変化の記述漏れ。互換性の記述は `design.cue` の `compatibility` にある）。固定した `sha256`：requirement `537a25a6…`、design `bd8f17da…`、plan `75eabb48…`（その後 plan の手順の status とテスト文言だけ更新）。
- テスト：`tests/unit/application/test_project_context_mode.py`（重複キー3種、再読み取りで消えた宣言）、`tests/cli_runtime/test_issue510_ambiguous_declaration.py`（`scope list`・`workspace validate`・`active show` が `PRECONDITION_FAILED`＝終了コード3、`doctor --raw` が観測）。Red（修正前に4件失敗）→ Green を確認。
- コードのレビュー（`code-review`、code-reviewer sonnet / high、`809a9c67f..984abc40b`）：合格、指摘なし。
- 最終品質ゲート（`final-quality-gate`、campaign `iss-00510-fqg-1`、ChatGPT は無効）：commit `984abc40bd496529463f32102a35bce6383346be` で合格。quality-gate-reviewer（opus / high）pass・coverage complete・P0/P1 なし・P3 1件。`make lint` 終了コード0、`uv run pytest` 終了コード0（3239 passed、7 skipped、1627秒）。記録：`.workbench/final-quality-gate/iss-00510-fqg-1/closure.md`。

## Residual Risks / Follow-ups

- FQG-1（P3）：`canonical_check.py` の `_declaration_failure` は重複キーを拒まない。重複キーの宣言をコミットしても CI の `canonical check` は通るが、手元の業務コマンドは止まる。この Issue の範囲外なので直していない（後続の候補）。
- 契約の変更（#513 が 0.5.1 の `migration.md` に載せる）：重複メンバーの宣言を持つ版4のリポジトリは、0.5.0 では受け付けられたが、0.5.1 では業務コマンドが `PRECONDITION_FAILED`（終了コード3）で止まる。`doctor --raw` の JSON と、その他のコマンド・エラーコードは変わらない。
