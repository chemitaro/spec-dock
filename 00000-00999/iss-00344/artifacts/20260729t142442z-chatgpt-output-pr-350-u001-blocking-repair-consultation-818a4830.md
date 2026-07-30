{
"consultation_status": "fresh",
"bound_head_sha": "818a48303f7a59b625d10681e6a2182767828279",
"bound_family_ids": [
"F001"
],
"validity": "partially-valid",
"recommendations": [
{
"id": "REC-001",
"disposition_candidate": "partial-use",
"summary": "Adopt the exact-path uninstall inventory repair for spec-dock/.workbench/README.md, but do not delete or reorder the existing uninstall retry marker as part of F001.",
"rationale": "The core P1 root cause is valid: fresh init copies templates/root/.workbench/README.md to spec-dock/.workbench/README.md, while _build_scaffold_uninstall_sources() does not register that target path. The unknown-boundary scan therefore preserves the unchanged generated file as unmanaged, and bounded empty-directory cleanup cannot remove .workbench. The existing exact-match helper is already the correct ownership seam and preserves modified, symlinked, non-regular, or unreadable targets. The marker portion of the finding is not caused by this omission: _run_uninstall writes the retry marker before planning, _add_uninstall_retry_marker_action intentionally preserves it, and the existing remove-specs rerun regression depends on that marker. Treating marker persistence as part of this repair would change the established idempotent-retry contract rather than repair F001.",
"implementation_scope": [
"src/spec_dock/cli.py: add one exact target/source mapping in _build_scaffold_uninstall_sources() from spec_dock/templates/root/.workbench/README.md bytes to spec-dock/.workbench/README.md",
"tests/unit/infra/test_init_update.py: add focused classification, removal, modification-preservation, and arbitrary-payload-preservation regressions",
"Issue 344 repair evidence only: record partial adoption, the retained retry-marker contract, executed commands, and the new exact repair head"
],
"test_cases": [
{
"name": "test_uninstall_dry_run_classifies_fresh_root_workbench_readme_as_scaffold_managed_exact_match",
"precondition": "Run fresh init; leave spec-dock/.workbench/README.md byte-identical to the shipped root Workbench README.",
"expected": "Dry-run contains exactly one action for spec-dock/.workbench/README.md with category scaffold_managed, status would_remove, and an exact-match reason; no unmanaged action exists for that path."
},
{
"name": "test_uninstall_apply_remove_specs_removes_unchanged_root_workbench_readme_and_empty_workbench_dir",
"precondition": "Run fresh init; keep .workbench limited to the unchanged generated README; execute uninstall --apply --remove-specs.",
"expected": "The README action is removed, spec-dock/.workbench no longer exists after bounded empty-directory cleanup, status is completed, the valid retry marker remains, and a second remove-specs invocation succeeds with already_removed evidence."
},
{
"name": "test_uninstall_apply_remove_specs_preserves_modified_root_workbench_readme",
"precondition": "Run fresh init, change the README bytes, then execute uninstall --apply --remove-specs.",
"expected": "The exact path is classified scaffold_managed but preserved for content mismatch; its bytes are unchanged, .workbench remains, and no recursive deletion occurs."
},
{
"name": "test_uninstall_apply_remove_specs_removes_only_managed_readme_and_preserves_arbitrary_workbench_payload",
"precondition": "Run fresh init, leave the README unchanged, add a nested arbitrary Workbench payload, then execute uninstall --apply --remove-specs.",
"expected": "Only the unchanged README is removed; the payload is reported as unmanaged/preserved with identical bytes, and the non-empty .workbench directory remains."
}
]
}
],
"minimal_design": {
"code_seam": "In _build_scaffold_uninstall_sources(), append the exact target alias Path('spec-dock/.workbench/README.md') with expected bytes read from src_spec_dock / 'templates' / 'root' / '.workbench' / 'README.md'. Reuse _add_exact_match_uninstall_action through the existing _build_uninstall_plan loop; no new removal helper or Workbench-specific traversal is needed.",
"preservation_contract": "Ownership is exact-path plus current shipped bytes. Exact bytes are removable; modified, symlinked, non-regular, or unreadable README targets are preserved for manual review; every other Workbench entry remains unmanaged and preserved; a missing README is never created and may report already_removed during apply; empty-directory cleanup runs only after file actions; the retry marker remains preserved for installer-CLI reruns.",
"avoid": [
"Recursive ownership or shutil.rmtree of spec-dock/.workbench",
"Deleting arbitrary Workbench payload or a modified README",
"Special-case unlink logic that bypasses _compare_uninstall_bytes and _add_exact_match_uninstall_action",
"Changing retry-marker creation, preservation, validation, or cleanup ordering in F001",
"Existing-root or existing-node README backfill",
"Issue 345 generic import or Issue 346 candidate-wheel/integrated-regression implementation",
"A new manifest, deletion framework, provenance database, or manual-first dogfood edit"
]
},
"validation_commands": [
"uv run pytest -q -ra --run-full-regression tests/unit/infra/test_init_update.py::TestInitUpdate::test_uninstall_dry_run_classifies_fresh_root_workbench_readme_as_scaffold_managed_exact_match tests/unit/infra/test_init_update.py::TestInitUpdate::test_uninstall_apply_remove_specs_removes_unchanged_root_workbench_readme_and_empty_workbench_dir tests/unit/infra/test_init_update.py::TestInitUpdate::test_uninstall_apply_remove_specs_preserves_modified_root_workbench_readme tests/unit/infra/test_init_update.py::TestInitUpdate::test_uninstall_apply_remove_specs_removes_only_managed_readme_and_preserves_arbitrary_workbench_payload",
"uv run pytest -q -ra --run-full-regression tests/unit/infra/test_init_update.py::TestInitUpdate::test_uninstall_apply_remove_specs_rerun_reports_already_removed_and_succeeds tests/unit/infra/test_init_update.py::TestInitUpdate::test_uninstall_apply_bounded_cleanup_respects_preserved_files_and_roots tests/unit/infra/test_init_update.py::TestInitUpdate::test_uninstall_apply_rejects_symlinked_retry_marker_without_external_mutation",
"uv run pytest -q -ra --run-full-regression tests/unit/infra/test_init_update.py::TestInitUpdate::test_workbench_readme_assets_are_byte_identical_and_complete tests/unit/infra/test_init_update.py::TestInitUpdate::test_fresh_init_creates_only_tracked_root_workbench_readme tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_and_force_init_do_not_backfill_workbench_readme tests/unit/infra/test_init_update.py::TestInitUpdate::test_workbench_gitignore_tracks_only_top_level_readme",
"uv run pytest -q -ra --run-full-regression tests/unit/infra/test_init_update.py -k 'uninstall or workbench or readme'",
"uv run pytest -q -ra tests/cli_runtime/test_uninstall.py",
"git diff --check -- src/spec_dock/cli.py tests/unit/infra/test_init_update.py",
"make lint",
"uv run pytest -q -ra"
],
"open_risks": [
"U001 currently states that the retry marker should disappear, but current production code and the established remove-specs rerun test require it to persist. A zero-residue uninstall would need a separate human-gated contract change and replacement retry-evidence design.",
"Exact-match ownership is provenance-blind: a manually created byte-identical file at the exact path is indistinguishable from installer output during an explicit uninstall.",
"Comparison uses current shipped bytes, so a root README generated by an older version may be conservatively preserved after the shipped README changes; this is consistent with the existing scaffold mismatch policy but remains an under-delete case.",
"The repair must retain existing symlink/non-regular/read-error preservation; a direct unlink special case would reopen external-deletion and data-loss risks.",
"Current exact-head CI and Provider CI passed, but they do not cover this omitted target alias; the proposed Red tests must fail before the code change and pass afterward.",
"The unresolved review thread was raised on an earlier PR head, while the current exact head retains the same cli.py blob and adds repair evidence. Any repair commit invalidates this consultation binding and requires new exact-head CI and PR re-observation."
],
"strategy_delta": "Narrow S350-001 to generation/uninstall inventory symmetry only: register the generated root README target, remove it only on exact byte match, and let existing post-action bounded cleanup remove an empty .workbench directory. Replace the U001 expectation that the retry marker is removed with an assertion that the marker remains valid and the second remove-specs run succeeds. Marker elimination, if desired, is a separate contract decision rather than part of F001.",
"next_action": "bounded_repair"
}
