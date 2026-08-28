---
種別: レポート（Issue）
ID: "iss-00371"
タイトル: "Explicit Spec History Purge"
関連GitHub: ["#371"]
最終更新: "2026-08-28"
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

## Verification

### Red to green

実装前の I371 selector は未成立で、次の characterization では新規 purge
acceptance が skip された。

- `tests/unit/infra/test_init_update.py`: `31 skipped, 163 deselected`
- `tests/cli_runtime/test_distribution_cutover.py`: `50 skipped, 119 deselected`

実装後は次の focused suites が green になった。

- `uv run pytest --run-full-regression --full-regression-shard tests/unit/infra/test_managed_distribution.py -k 'i371_purge_assessment_is_typed_and_write_free or i371_purge_apply_removes_history_and_preserves_workbench' -q`: `2 passed`
- `uv run pytest --run-full-regression --full-regression-shard tests/unit/infra/test_managed_distribution.py -k 'i371_purge_forward_recovers_same_plan_after_history_checkpoint_failure' -q`: `1 passed`
- `uv run pytest --run-full-regression --full-regression-shard tests/unit/infra/test_managed_distribution.py -q`: `489 passed`
- `uv run pytest --run-full-regression --full-regression-shard tests/unit/infra/test_init_update.py -k 'uninstall or remove_specs or i371' -q`: `31 passed`
- `uv run pytest --run-full-regression --full-regression-shard tests/cli_runtime/test_distribution_cutover.py -k 'uninstall or remove_specs or i371' -q`: `49 passed`

通常の quality gates は次のとおり。

- `uv run pytest`: exit 0
- `make lint`: ruff check/format、mypy ともに pass
- `./spec-dock/scripts/spec-dock validate`: `spec-dock: ok (validate) nodes=227`
- `python -m py_compile src/spec_dock/cli.py`: pass
- `git diff --check`: pass（whitespace error 0）

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

ledger、verifier、Issue 370 evidence は変更していない。candidate が未commitの
ため、wheel receipt failure を解消した、または Full Regression が成功したとは
主張しない。

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

## Residual Risks / Follow-ups

- Full Regression verifier は `ledger-mismatch` のため、clean candidate SHA での
  wheel receipt を含む再検証が必要。ledger の変更や failure の隠蔽は行っていない。
- fast lane の visible-parent rebind race は既存挙動として残る。再実行で green
  だったが、根本修正は Issue 371 の scope 外。
- `.artifacts/iss-00371-full-regression/20260828T092613.495723Z/` は verifier
  evidence として保持しているが、production diff の一部ではない。
- `git status --short` は次のとおりで、受理済み R/D/P の dirty state を含む。

```text
 M README.md
 M spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00365-specdock-structural-integrity-rearchitecture-and-regression-baseline-recovery/issues/iss-00371-explicit-spec-history-purge/design.md
 M spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00365-specdock-structural-integrity-rearchitecture-and-regression-baseline-recovery/issues/iss-00371-explicit-spec-history-purge/plan.md
 M spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00365-specdock-structural-integrity-rearchitecture-and-regression-baseline-recovery/issues/iss-00371-explicit-spec-history-purge/requirement.md
 M src/spec_dock/cli.py
 M src/spec_dock/managed_distribution.py
 M tests/cli_runtime/test_distribution_cutover.py
 M tests/unit/infra/test_init_update.py
 M tests/unit/infra/test_managed_distribution.py
?? .artifacts/
```

commit/push/PR publication は実施していない。
