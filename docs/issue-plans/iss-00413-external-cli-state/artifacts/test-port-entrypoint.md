# 公開入口テストの移行根拠

対象は `tests/integration/test_cli_entrypoint_vnext.py`。変更前の本文はcommit `f9edf1928d3fe4a5c9c3aa37951a1ca574c770c3`で全件読取した。この資料は本Issueの仕様差分と検証対応を説明するもので、通常pytestの失敗を除外する台帳ではない。

根拠はRQ-413-01/02/03/16、D-02/D-12、P-02/P-12/P-13および計画の「既存テストの維持・更新・削除理由」。旧fixed配布、digest pin、control locator、コピーruntimeは新しい業務実行の前提ではない。復活させて旧testを通す変更は行わない。

| 変更前のtest | 判断と後継 |
|---|---|
| `test_fixed_distribution_builder_isolation_and_digest` | fixed builder/digest APIの保証を撤去。非editableの通常wheelをcheckout外のvenvへ導入し、import元がそのsite-packages内であること、実consoleのhelpと業務実行を確認する |
| `test_fixed_engine_ci_validate_requires_no_repository_control_and_writes_nothing` | controlなしCI検証と書込0を維持。通常検証もcontrolなしで成功する契約へ拡張し、Gitを含むtree digestの不変を比較する |
| `test_package_version_ignores_retired_fixed_distribution_version_file` | 維持。version.txtを9.9.9としても通常package metadataのversionを使う |
| `test_fixed_distribution_builder_rejects_checkout_destination` | 撤去するbuilderの配置拒否を撤去。fixtureは外部venvを明示しimport先も検証する。ユーザーが自由に配置した別programの信頼性をCLIがdigestで保証する契約には置き換えない |
| `test_wheel_layout_is_not_a_fixed_mutating_engine` | wheel拒否を撤回。実wheelのStart、Sync、Finishが成功する後継へ |
| `test_public_entrypoints_use_fixed_engine` | consoleの`spec_dock.cli:main`宣言、旧installer入口不在、static shim/source bytes一致を維持し、名称を新契約へ変更 |
| `test_package_entrypoint_exposes_read_only_help_without_repository_pin` | 強化。source内mainの呼出しを実consoleへ移し、GitのないPATHと欠けたprojectでもv2 utility/効果0/書込0を確認 |
| `test_public_entrypoint_rejects_retired_installer_before_write` | 実consoleへ移して維持。旧root initはexit2/v2診断で、新規fileを作らない |
| `test_external_engine_pin_uses_absolute_package_and_digest` | 退役pinの絶対配置/digest APIの保証を撤去。不正・相対・欠損・digest不一致の旧locatorが通常Scope読取を阻害せず、その旧fileも変更しない後継へ |
| `test_checkout_runtime_and_symlinked_engine_are_rejected` | consumer Pythonを実行しない保証を維持。外部consoleへの正当なsymlinkの一律拒否は撤回し、PATH shimで実行できることを確認。shim自身/旧shimへの再帰拒否は既存`test_issue413_shim.py`で維持 |
| `test_executable_tamper_and_relative_pin_are_rejected` | 旧pinによるprogram改変検出を撤去。実行先は標準PATH/package管理の責任であり、独自digest検証を再導入しない。旧相対/改変locatorが実行権限を持たない後継を確認 |
| `test_engine_locator_matches_control_and_verifies_full_distribution` | locator/controlの一致保証を撤去。それらを新しい実行判断に使わず、通常readerが旧fileのbytesを保持する後継へ |
| `test_engine_locator_does_not_replace_an_existing_pin` | pin writerを撤去するためAPIの冪等書込保証を撤去。新CLIによる旧locator/controlの書換え0を後継で確認 |
| `test_external_package_cli_runs_without_checkout_runtime_import` | fake bin/libとsys.path注入を通常wheelへ置換。consumerのsitecustomize/local package/runtimeを実行しない、GIT_DIR/GIT_WORK_TREEで別repoへ誤誘導しない保証を実配布shimで維持。PATHを無視してpinを実行する期待、digest不一致で別installed packageを拒否する期待はD-02に基づき撤去。単WT installationの実console検証は`test_issue413_wheel.py`も参照 |
| `test_two_consumers_share_one_fixed_engine_without_shared_control` | 通常packageを二つの独立cloneで使う形へ移行。各Scope、Syncの観測先、書込0を確認。shimの出身repoに拘束する制限を撤去し、現在CWD/明示projectへ正確に解決する。明示subdirectoryは拒否。第三repoへの明示installationは禁じず、target一致/誤target/他WT不変は`test_issue413_assets.py`で確認。新規local Scopeと各Git内engine.json生成の期待は撤去 |

実consoleのIssue lifecycle試験は、GitHub-backed三階層fixtureと外部のstateful `gh` executableを使う。Gitは実programでbranch作成・checkoutを行い、Syncは記録を保全し、FinishはIssue #3を一度だけcompletedへ変更して捕捉記録を解除する。祖先のGitHub状態、Scope metadata bytes、branchは保持され、独自`.git/spec-dock`は作らない。

このportは既存実装のGreen回帰であり、新しい製品不具合のRedではない。macOS上の実processの証拠に限定する。POSIX shim/symlink二casesのplatform指定をWindows native成功と扱わず、full-suite、最低Python、Windows、fresh Strict、Final Quality Gate、手動製品確認は別途閉じる。
