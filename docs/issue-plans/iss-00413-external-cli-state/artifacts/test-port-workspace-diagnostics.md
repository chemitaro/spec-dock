# Workspace診断のテスト移行

変更前は `ccce5d51e1ffcc4017377348bcace8649dbead45`。旧二ファイル・九関数を全文確認し、RQ-413-16、D-11/D-12、CLI v2へ照合した。私的doctor/validate use case、run_vnext、中央controlとengine admission、新規local発行をfixture/入口から外し、公開mainと現物の不変を検査する。

| 旧test | 後継・判断 |
|---|---|
| diagnostics `test_workspace_diagnostics_cli_reports_valid_and_required_nodes` | 公開validate/require-nodes/doctorの一連の操作で空workspaceを検査。NODES_REQUIRED/exit7、通常validationとdoctorのexit0、effects空・全tree不変・control/state作成0を確認 |
| doctor `test_empty_workspace_is_valid_unless_nodes_required` | 上の後継と既存 `test_issue413_workspace_validate.py::test_empty_workspace_is_valid_unless_nodes_are_required`（通常/CI×require-nodes）へ。退役したgeneration cacheがないことをfindingsにしない |
| doctor `test_ci_validation_reads_fresh_checkout_without_control_or_active_state` | committed snapshotの公開--ciでcontrol/state作成0・全tree不変・HEAD sourceを確認。snapshot固定と取得body範囲は既存workspace validate suiteで保護 |
| doctor `test_ci_validation_reports_invalid_committed_schema_without_installing` | schema2をfixtureのHEADへcommitした後の--ciでWORKSPACE_DECLARATION_INVALID/exit7、install/write0を維持。working copyだけの変更でCIのHEAD読取を代替しない |
| doctor `test_corrupt_control_and_generation_are_findings_without_exposing_content` | 通常doctorは旧control/generationをauthorityにせずexit0。--legacyを明示した時だけ旧controlのinvalid_jsonを報告し、両bodyを秘匿・bytes保持。旧generationは現行生成台帳として検証しない |
| doctor `test_doctor_github_probe_arguments_are_all_or_none` | 既存 `test_doctor_refuses_incomplete_or_invalid_fixed_github_probe_before_any_probe` の公開main・raw有無・無効repo/PR/head/offlineケースへ。旧private use caseを直接呼ばない |
| doctor `test_engine_mismatch_is_diagnosed_without_mutating_control` | engine_digest照合による全体admissionはD-11で撤去。通常diagnosisは旧controlを起動条件にせず、実配布entrypoint suiteのopaque旧locator検査と現行legacy Doctorの未実行/秘匿/保全検査で旧資産を隔離 |
| doctor `test_complete_github_probe_arguments_delegate_once` | 既存 `test_doctor_native_github_probe_binds_repository_pr_and_head_and_redacts_output` の公開main→external gh七requests（repo/PR/head一致、拒否、malformed、timeout等）へ。内部FakeProbe一回のassertを実際の公開通信と結果で代替 |
| doctor `test_dependency_and_artifact_faults_are_read_only_findings` | 同時にdangling dependencyと外部artifact directory symlinkを置き、validate/doctor双方が二findingを返す後継へ。effects空・全tree/外部body不変・秘匿を検査。単独faultのparametrizationだけで複合faultを代替しない |

後継二ファイルは五cases。既存doctor/validate suiteの公開保証を再利用して旧private APIの重複試験を除き、通常test実行のskip・selector除外は追加しない。限定portのGreenをfull suite、live GitHub、Windows、Strict合格とは扱わない。
