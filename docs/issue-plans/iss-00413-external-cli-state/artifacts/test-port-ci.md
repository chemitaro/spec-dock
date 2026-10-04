# CI検証経路の移行根拠

対象は `.github/scripts/specdock-ci-validate.sh` と `tests/integration/test_ci_fixed_validation.py`。変更前commitは `61f00023d35e265a93c96acdc0591423e56fa5af`。旧test本文を末尾まで読取した。RQ-413-01/02/16/17、D-02/D-13、P-12/P-13に従い、fixed bundleによるCIだけの別入口を通常wheelへ置換する。

| 変更前のtest / 保証 | 判断と後継 |
|---|---|
| `test_ci_workflow_uses_fixed_read_only_validator` | workflowが確認対象SHAを一回渡し、Syncやconsumer shimを実行しない保証を維持。Python 3.11とuvを明示し、scriptのfixed builder/runtime loader依存を除去 |
| `test_ci_validator_checks_source_sha_and_keeps_target_unmodified` | full SHA照合、正常検証、SHA不一致を維持。新writerのcommit済み三階層metadataを通常wheelの実consoleでHEAD検証する。v2 JSON/効果0を確認し、元sourceとtargetの全entry type/mode/bytesを比較。旧builder用の不活性sentinelが実行されないことも確認 |
| `test_ci_validator_rejects_untrusted_source_before_build` の四cases | tracked/untracked dirty、短縮/不正SHAの副作用前拒否を維持。旧controlを持つtargetの保全も維持。wheel buildと退役builderの両sentinelが未実行であることを確認 |
| `test_ci_validator_rejects_invalid_distribution_digest` | 退役fixed bundleのdigest形式検査を撤去。通常wheelのbuild失敗で実consoleを実行せず、source/targetを保持する後継へ。wheel SHA256は配送結果の識別表示であり、Git内のpinや実行権を作らない |

scriptはcleanなsourceとfull commit OIDを確認してから、Git archiveでそのcommitのpackage/build入力を専用の一時領域へ取り出す。通常wheelをbuildし、外部fresh venvへ非editable installし、`workspace validate --ci --json`を実行する。consumerにはruntime、pin、control、cache、直接記録を追加せず、元sourceにもbuild directoryを作らない。scratchはこのCI toolの終了時に処理する。

対象fixtureは旧の未commit workspaceから現在のcommit済みfixtureへ変更した。最初の試行の不足build入力と旧fixtureに対する失敗は、新機能のRedに数えない。成立したfixtureで旧経路の`workspace_schema_mismatch`/exit7/v1を確認してから、通常wheel経路で同じtestがexit0/v2/HEAD/効果0になったことをRed→Greenとして記録する。

Provider CIの通常lint/全pytestを維持し、既存Ubuntu/macOS配布laneの旧group init選択を通常wheel/単WT static installationの検証へ移す。ローカルのnative Bash/macOS試験とGitHub Actionsの実ジョブ結果を混同しない。Windowsと最低Pythonの受入、全体gate、Strict/最終品質gateは別途残る。
