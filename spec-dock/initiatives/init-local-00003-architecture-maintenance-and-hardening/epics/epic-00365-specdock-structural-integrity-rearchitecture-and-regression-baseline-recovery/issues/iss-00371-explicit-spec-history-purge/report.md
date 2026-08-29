---
種別: レポート（Issue）
ID: "iss-00371"
タイトル: "Explicit Spec History Purge"
関連GitHub: ["#371"]
最終更新: "2026-08-29"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00365", "init-local-00003"]
---

# Result Summary

詳細: [Report Guide](../../../../../../docs/authoring/report.md)

## Outcome

Issue 371 の受理済み contract に従い、`uninstall --remove-specs` を
`intent=purge` / `authority=explicit-spec-history-purge` の typed common
assessment/action/kernel/journal/result flow へ切り替えた。dry-run は write 0、
apply は `spec-dock/initiatives` だけを exact history root として purge し、
`.workbench` を保持する。component deprovision と history purge は同一 action
plan と forward-only journal recovery を共有する。

旧 remove-specs compatibility writer/mutator/marker-writer の production
executable path は削除した。legacy `.uninstall-retry.json` は reader のみを
残し、自動変換・新規 marker/journal は行わない。public `spec_history` action は
root-level 1 行へ集約し、public command/flag/schema/status/exit contract は
変更していない。

実装 candidate の base SHA は
`94546a138bd34b253c87ca8749f3c5678d172f2a`。受理済みの requirement/design/plan
は実装中に変更していない。

### Final Quality Gate P1 remediation

レビューで検出された二点を同じ accepted contract 内で修正した。

- purge tree capture が contract、history actions、target snapshots、directory
  evidence を一つの descriptor-bound capture record から提供するようにし、
  assessment 中の history subtree 再捕捉と leaf の独立 `_observe_target()` を
  廃止した。capture 間に二度目の root observation で内容を変える決定的テストで、
  contract/action snapshot の identity と SHA-256 が一致し blocker-free plan が
  分裂しないことを確認した。
- capture 済みの全 history directory を augmentation の managed directory closure
  と exact directory evidence に登録し、leaf および nested empty directory を
  deepest-first の `remove-empty-directory` action として生成するようにした。
  `.workbench` と repository root 外 sentinel は保持される。

### Final Quality Gate P1 remediation: cross-intent recovery

Strict review で検出された cross-intent recovery mismatch の retry policy 欠陥を
修正した。`_distribution_process_result_from_state` に型付き
`recovery_mismatch_kind` を追加し、同一 intent の package/plan/evidence mismatch
は従来どおり `same-keep-command`（purge は既存の manual policy）を維持する一方、
journal の intent/authority、または guard の operation/purpose が要求 intent と
異なる場合だけ `manual-recovery` を返すようにした。これにより purge journal に
対する keep/deprovision request、および deprovision journal に対する purge request
は、retry command を公開せず、target と journal checkpoint を変更しない。

### Final Quality Gate P1 remediation: parser/read boundary and dry-run projection

Strict re-review の P1-A/P1-B を accepted contract 内で修正した。operation journal
parser と retry guard reader は、supported canonical intent/authority または
purpose/operation pair が認識できた時点で `intent-authority` metadata を typed
exception に付加する。destructive recovery の journal 初回 read は descriptor-bound
な no-follow capture を先に行い、root/parent/package の後段検証で cross-intent の
分類を失わない。same-intent の malformed/package/plan mismatch は従来の
`same-keep-command`（purge は `same-remove-command`/manual contract）を維持し、
unsupported/malformed discriminator は authority を推測しない。guard-only の
cross-intent は manual recovery とし、guard 不変・journal 未生成・checkpoint 0 を
保つ。

purge の dry-run は `same-remove-command` による apply guidance を維持しながら、
public `retry_command` は `apply=True` の場合だけ生成する。apply 結果の exact
`spec-dock uninstall --apply --remove-specs` command と deprovision keep の既存
dry-run/retry projection、public schema/JSON/text/exit contract は変更していない。

## Verification

### Red to green

実装前の I371 selector は未成立で、次の characterization では新規 purge
acceptance が skip された。

- `tests/unit/infra/test_init_update.py`: `31 skipped, 163 deselected`
- `tests/cli_runtime/test_distribution_cutover.py`: `50 skipped, 119 deselected`

実装後は次の focused suites が green になった。

- `uv run pytest --run-full-regression --full-regression-shard tests/unit/infra/test_managed_distribution.py -k 'i371_purge_assessment_is_typed_and_write_free or i371_purge_apply_removes_history_and_preserves_workbench' -q`: `2 passed`
- `uv run pytest --run-full-regression --full-regression-shard tests/unit/infra/test_managed_distribution.py -k 'i371_purge_forward_recovers_same_plan_after_history_checkpoint_failure' -q`: `1 passed`
- `uv run pytest --run-full-regression --full-regression-shard tests/unit/infra/test_managed_distribution.py -k 'i371_purge_assessment_reuses_one_coherent_history_capture or i371_purge_assessment_registers_nested_empty_history_directories' -q`: `2 passed`
- `uv run pytest --run-full-regression --full-regression-shard tests/unit/infra/test_managed_distribution.py -q`: `491 passed`
- `uv run pytest --run-full-regression --full-regression-shard tests/unit/infra/test_init_update.py -k 'uninstall or remove_specs or i371' -q`: `31 passed`
- `uv run pytest --run-full-regression --full-regression-shard tests/cli_runtime/test_distribution_cutover.py -k 'uninstall or remove_specs or i371' -q`: `49 passed`
- `uv run pytest --run-full-regression --full-regression-shard tests/cli_runtime/test_distribution_cutover.py -k 'i371' -q`: `3 passed`

通常の quality gates は次のとおり。

- `uv run pytest`: exit 0
- `make lint`: ruff check/format、mypy ともに pass
- `./spec-dock/scripts/spec-dock validate`: `spec-dock: ok (validate) nodes=227`
- `python -m py_compile src/spec_dock/cli.py`: pass
- `python -m py_compile src/spec_dock/managed_distribution.py`: pass
- `git diff --check`: pass（whitespace error 0）

P1 remediation 後の init/update selector は既存の重い keep-specs case を含むため
`534.58s` 時点で `9 passed, 163 deselected` の後に Ctrl-C で中断した（exit 130、
assertion failure なし）。修正前の同 selector `31 passed` と、P1修正後の managed
全体 `491 passed` および CLI I371 `3 passed` を合わせて確認した。

fast selector は既存の visible-parent rebind race が 1 件だけ単発 failure
となったが、同じ 4 parameter の再実行は `4 passed` だった。既存 race のための
緩和や変更は行っていない。

### Full Regression

次の fresh artifact directory で verifier を実行した。

```text
uv run python spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00365-specdock-structural-integrity-rearchitecture-and-regression-baseline-recovery/issues/iss-00368-recognized-workspace-reconciliation/artifacts/verify-full-regression.py --shards 4 --artifact-dir .artifacts/iss-00371-full-regression
```

artifact: `.artifacts/iss-00371-full-regression/20260828T092613.495723Z/`

結果は exit 1、`status=ledger-mismatch` であり、Full Regression が verified
になったとは扱わない。`unexpected_errors=0`、`missing_failures=0`、
`signature_mismatches=0`。unexpected failure は次の 2 件だった。

1. `tests/integration/test_epic_00343_distribution.py::test_tc_346_s01_001_candidate_wheel_receipt`
   - commit 前の dirty candidate（受理済み Issue 371 docs と実装差分、fresh
     artifact）が wheel receipt の clean-status 前提に該当した。
2. `tests/unit/infra/test_init_update.py::test_i370_legacy_marker_and_deprovision_journal_never_cross_authority_routes`
   - purge authority への hard cutover 後も旧 Issue 370 期待値を固定していたため
     failure。期待値を current contract の purge conflict
     (`exit=1`, `status=partial_failure`) へ同期し、単体 `1 passed` を確認した。

ledger、verifier、Issue 370 evidence は変更していない。この結果は pre-commit
candidate の historical evidence であり、final candidate の成否には使用しない。

その後、clean exact SHA `6bd80c78a4b4ba4762eacaaea4e16af5ca3845f6`
に対して外部 fresh artifact directory で verifier を再実行し、
`status=verified`、`approved_failure_count=27`、candidate SHA exact match、
total elapsed `1420.6s` を確認した。この SHA 後に parser/read boundary と purge
dry-run projection の remediation を追加しているため、final frozen SHAでは同じ
verifierをもう一度実行し、その外部 `result.json` を Final Quality Gate evidence
とする。report-only commitによるSHA更新は行わない。

### Static/source contract evidence

次の old route/helper symbols の `src`/`tests` source scan は no output だった。

```text
_run_uninstall_remove_specs_compatibility
_UninstallAction
_UninstallTargetIdentity
_build_uninstall_plan
_apply_uninstall_plan
_remove_uninstall_path
_remove_uninstall_tree_fd
_write_uninstall_retry_marker
_finalize_uninstall_retry_marker
_restore_uninstall_retry_marker_action
_ensure_uninstall_retry_marker_action
_verify_uninstall_postcondition
_cleanup_empty_uninstall_dirs
_uninstall_apply_blockers
_uninstall_payload
_emit_uninstall_preflight_error
_iter_existing_files_or_symlinks
_capture_uninstall_target_identity
```

I371 CLI seam test で deprovision/purge の typed service が各 1 回だけ選択され、
purge adapter が journal を直接解釈しないこと、purge/keep の mapper mismatch
が typed error になることを確認した。history の symlink/hardlink/special/
rebind、unknown nested component、cross-intent/authority/root/plan、legacy
marker ambiguity、same-plan forward recovery の negative cases は focused
suite で確認した。

### Current cross-intent remediation checks

新しい回帰を先に red で確認し、purge journal + keep request の旧実装が
`same-keep-command` を返すことを検出した後、次の checks を green で確認した。

- `uv run pytest tests/unit/infra/test_managed_distribution.py::test_i371_cross_intent_recovery_mismatch_is_manual_and_write_free`: `2 passed`
- `uv run pytest --run-full-regression tests/cli_runtime/test_distribution_cutover.py -k i371`: `3 passed`（既存 ledger mismatch 診断を出力したが exit 0）
- `uv run pytest --run-full-regression tests/unit/infra/test_init_update.py -k i371`: `2 passed`、exit 3（full-regression wrapper の既存 ledger missing-node mismatch。テスト assertion failure なし）
- `uv run pytest tests/unit/infra/test_managed_distribution.py`: `493 passed`
- `uv run pytest`: `1444 passed, 1138 skipped`
- `make lint`: ruff check/format、mypy ともに pass
- `./spec-dock/scripts/spec-dock validate`: `spec-dock: ok (validate) nodes=227`
- `git diff --check`: pass（whitespace error 0）

managed regression は両 cross-intent 順序で target tree、journal bytes、guard bytes を
不変とし、pending checkpoint 0 と `manual-recovery` を確認した。CLI route regression
は purge journal + keep request で `retry_command=null` と manual guidance を確認した。
この修正は未commitのため、clean exact-SHA Full Regression verified evidence は
primary の最終 gate で取得する。

### Current parser and dry-run remediation checks

- `uv run pytest tests/unit/infra/test_managed_distribution.py -k i371`: `13 passed`
- `uv run pytest tests/unit/infra/test_managed_distribution.py`: `499 passed`
- `uv run pytest --run-full-regression --full-regression-shard tests/unit/infra/test_init_update.py -k i371`: `2 passed`
- `uv run pytest --run-full-regression --full-regression-shard tests/cli_runtime/test_distribution_cutover.py -k i371`: `3 passed`
- `uv run pytest`: `1449 passed, 1138 skipped`
- `make lint`: ruff check/format、mypy ともに pass
- `./spec-dock/scripts/spec-dock validate`: `spec-dock: ok (validate) nodes=227`
- `python3 -m py_compile src/spec_dock/managed_distribution.py src/spec_dock/cli.py`: pass
- `git diff --check`: pass（whitespace error 0）

P1-A regression は、canonical cross discriminator と arbitrary/noncanonical authority、
後段 root/workspace malformed binding の順序、guard-only の journal 未生成、
unsupported intent の generic classification を確認した。P1-B regression は purge dry-run の
`retry_command=null`/apply guidance、apply 時の exact remove command、deprovision
keep projection の維持を確認した。Full Regression の clean candidate SHA 検証は
primary のプロセス gate として実施し、ledger/verifier は変更していない。

### Final Quality Gate P1 remediation: quarantine ownership and pathname unlink

Strict review で検出された recovery quarantine の pathname race を、accepted
R18/R19/R21/R22/R29 contract 内で修正した。canonical path から operation-owned
quarantine への no-replace rename 後は、後段 failure で canonical pathname や
quarantine pathname を identity 条件なしに unlink／rollback rename しない。
`_remove_distribution_stage_if_owned` の Issue 371 専用 `direct_unlink` escape と、
canonical/quarantine が同一 inode の hardlink である場合に quarantine name を
unlink する helper を削除した。

cleanup failure 後に exact canonical と exact quarantine が併存する場合、または
third-party canonical conflict がある場合は、operation-owned quarantine を bounded
recovery evidence として保持し、内部 `quarantine-preserved` state から public
`recovery_required` / `manual-recovery` へ写像する。これは genuine な
`dual-recovery-state` と区別し、既存 schema version、protocol version、guard
version、intent/authority、CLI JSON/text/exit contract は変更しない。Issue 370 から
継承した一般 GC cleanup seam の再設計はこの修正に含めていない。

pre-commit candidate では次を確認した。

- focused pathname/quarantine recovery regressions: `46 passed`
- `tests/unit/infra/test_managed_distribution.py`: `575 passed`
- ordinary fast lane `uv run pytest -q`: `1526 passed, 1142 skipped`
- CLI I371 focused selector: `3 passed`（部分 Full Regression selector のため
  ledger missing-node 診断は出るが assertion failure 0）
- `make lint`: ruff check/format、mypy ともに pass
- `./spec-dock/scripts/spec-dock validate`: `spec-dock: ok (validate) nodes=227`
- `python -m py_compile src/spec_dock/managed_distribution.py`: pass
- `git diff --check`: pass（whitespace error 0）

この pre-commit 証拠は fixed candidate SHA の Full Regression／Strict review の
代替には使用しない。最終 gate は commit/push 後の clean exact SHA に対して fresh
verifier と browser-only Strict review を実行し、外部 artifact と最終応答で記録する。

## Residual Risks / Follow-ups

- pathname/quarantine remediation と本 report を含む final frozen SHA で、clean
  Full Regression verifier と Strict review の再検証が必要。直前の clean SHA
  `fdcb26bb19aac8e5732b74489a23183975f2b811` は Full Regression `verified`
  （approved failure 27、unexpected/missing/signature mismatch 0）だった。ledger、
  verifier、approved failure signaturesは変更していない。
- fast lane の visible-parent rebind race は既存挙動として残る。再実行で green
  だったが、根本修正は Issue 371 の scope 外。
- init/update の再実行は重い既存ケースで中断したため、P1修正後の当該 selector
  全件 green とは主張しない。修正前の `31 passed` evidence と対象 managed/CLI
  suitesの修正後 greenを保全している。
- `.artifacts/iss-00371-full-regression/20260828T092613.495723Z/` は verifier
  evidence として生成したが、現在の working tree には保持していない。
- quarantine ownership remediation 前の commit
  `fdcb26bb19aac8e5732b74489a23183975f2b811` までは upstream へpush済みである。
  最新 remediation の pre-commit `git status --short` は次のとおり。

```text
 M spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00365-specdock-structural-integrity-rearchitecture-and-regression-baseline-recovery/issues/iss-00371-explicit-spec-history-purge/report.md
 M src/spec_dock/managed_distribution.py
 M tests/unit/infra/test_managed_distribution.py
```

この report は pre-commit 時点の事実だけを記録する。commit/push 後の fixed SHA、
fresh Full Regression artifact、Strict review 結果は Final Quality Gate の外部証拠と
最終応答で確定し、report-only commit による reviewed SHA の更新は行わない。
