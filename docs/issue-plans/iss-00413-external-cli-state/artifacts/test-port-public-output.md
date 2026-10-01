# 公開v2出力と維持する試験の型整合

基準は `e139745939a104a89cde4a44df0d6773632b485b`。productionを変更せず、旧v1の出力fixtureを公開v2へ更新した。既存test名を保持し、型チェックを緩和しない。

| test関数 | 維持・更新する保証 |
|---|---|
| test_empty_active_json_is_one_complete_envelope | 改行一件のv2 envelope、exit_code、直接selectionと動的ancestors。旧三role・revision・operation_id/targetを出力正本にしない |
| test_partial_result_keeps_unknown_effect_and_recovery_boundary | unknown effectと日本語診断を保ち、観測を促すinstructionsだけを返す。resume/rollback=false、旧operation IDやresume命令を含めない |
| test_result_rejects_success_exit_with_partial_effect | partial効果をexit0で成功扱いしない |
| test_top_level_result_cannot_hide_effect_state | succeeded/unchanged/planned/failedが不適切なeffectを隠せない。statusは実ResultStatus型を使う |
| test_text_renderer_reports_same_effect_and_error_codes | text/stderrに確認済み成功・clear失敗・診断codeを保持する |
| test_completion_script_contains_catalog_driven_scope_children | bash/zsh/fishの補完は現行cli/optionsの入口を使用 |
| test_json_renderer_redacts_secret_bearing_details | v2にもsecret-bearing message/detailが漏れない |

`tests/unit/domain/test_cli_lifecycle_vnext.py` のlocal metadata codec試験は維持し、decode後に `isinstance(..., LocalBackend)` を検証して型を確定した。新規offline作成を許可する変更ではない。

`tests/integration/test_atomic_json_publication.py` の別process交換直後kill・racing destination・post-effect error・symlink/hardlink拒否を維持した。直接代入するcallbackの引数名を実APIの `source` / `target` と一致させる型修正だけで、試験動作は変えない。

## 検証

- 通常make lint at clean e1397459: Ruff成功、mypy 41 errors/16 files、240 source files、make exit2。
- 対象三testの限定mypyは `MYPYPATH=src` なしだとimport解決が不十分で0を表示した。明示した同チェックでは3 errors/3 files、exit1を再現し、修正後は0、exit0。限定チェックの成功を通常full gateの成功とは扱わない。
- 関連三suite: 43 passed、0.13秒、exit0。Ruff check/formatとdiff check成功。production変更0、test削除0、skip追加0。
- 初回collection error（future annotations不足、0.09秒）はharness誤りとして訂正。製品Redに数えない。

元logは既存Epic Workbenchの `iss-00413-implementation/lint-p12-e1397459.log` と `pytest-retained-output-type{,-2}.log`。未修正の旧source/helpers、native OS、別Python、fresh Strict、全体gate・手動確認は別途継続する。
