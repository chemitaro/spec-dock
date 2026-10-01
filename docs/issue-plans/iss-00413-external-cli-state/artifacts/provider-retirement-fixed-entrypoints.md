# 旧fixed bundle入口の製品コード退役

D-02/D-11に従い、`src/spec_dock/external_cli.py` と `src/spec_dock/fixed_bundle.py` を削除した。公開consoleは既に `spec_dock.cli:main` であり、44 leafは新runtime_dispatchへ委譲している。通常配布から二つの旧入口を除き、互換main・deprecated実行alias・fallbackを追加しない。

対象全文とsource/tests/setup/pyproject/CI/scriptsの参照を確認した。製品のinboundは旧fixed launcher文字列からexternal_cliへの一件だけで、二ファイルを同時に退役する。残るtestの名前文字列はwheel収録禁止またはCIで旧builderが実行されないことを検査するsentinelであり、旧製品moduleの呼出しではない。

## src/spec_dock/external_cli.py

| 旧関数 | 移行・退役判断 |
|---|---|
| `_json_requested` | 公開parserが--jsonを解釈する。旧fixed preflightだけの判定を残さない。 |
| `_preflight_failure` | 公開front doorのv2 render_diagnostic_jsonへ統合済み。旧v1/operation IDのengine preflightを廃止。 |
| `_git_root` | 新project_contextのnative Git context解決へ置換済み。旧入口からの二重preflightを廃止。 |
| `_project_candidate` | 新project_context/installation_contextの明示root解決へ置換済み。fixed engineの候補解決を廃止。 |
| `_executing_engine` | fixed distribution layoutとdigest照合を廃止。通常packageのconsole/version/resourcesを使用。 |
| `run_external` | 公開cli.main→runtime_dispatchへ統合済み。control/locator/handoverを実行条件にしない。 |
| `main` | 公開consoleはspec_dock.cli:mainに一意化。旧moduleの別main/fallbackを残さない。 |

## src/spec_dock/fixed_bundle.py

| 旧関数 | 移行・退役判断 |
|---|---|
| `_python_binary` | fixed copy用Pythonパス制約を廃止。通常venv/console配布のPython要件で扱う。 |
| `_source_checkout` | 固定copyのためのcheckout探索を廃止。普通のwheel/sdist buildを使用。 |
| `build_fixed_engine` | 追加package copy/lib/bin/digest bundle生成を廃止。通常wheel一つだけを配布。 |
| `main` | 公開consoleはspec_dock.cli:mainに一意化。旧moduleの別main/fallbackを残さない。 |

## Red → Greenと公開境界の確認

先に実wheel inventoryへ二つの旧入口の収録禁止を追加した。同じwheel試験は実build成功後に二moduleを検出して1 failed（0.80秒）。runner/collectionの問題ではなく、今回の配布退役条件のRedである。

二ファイルを削除した後、同じ公開wheel試験は1 passed（14.34秒）。fresh wheel、sdist→derived wheel、checkout外の非editable venv、実consoleの44 leaf help/version/completion、Scope validate、CI HEAD validation、shim、static installationのinit/show/update/uninstall、resources hashとデータ保全まで確認した。削除は既存build_pyの新鮮なpackage再構築で反映され、古いbuild/libを配布へ残さない。build手順の新たなfallback/除外は加えていない。

公開entrypoint/CI/provider distributionの関連24 tests（13.03秒）も成功。全source/tests Ruff check/format（418 files）、変更wheel test限定mypy --follow-imports=silent、diff checkが成功した。

## 残作業

`runtime_loader.py`、旧vnext dispatcher/commands/application、control/registry/journalの製品sourceはまだ残る。module名やASTの到達不能だけを削除根拠にせず、public/packaging/codec/shared helperの各参照と旧testsを確認して続ける。package初期化の暗黙importとsetupのasset_layout参照も保持する。必要な三階層/既存ID・metadata codecは廃止対象ではない。

通常全体type/pytest、native Windows/Python3.10、fresh Strict、説明HTMLの最終更新・手動製品確認は別の未完了条件。実consumer・旧.git独自領域・live GitHubへの適用は行っていない。README/AGENTSの旧fixed build記述もP-12/P-14で新配布へ合わせる。
