---
種別: disc
ID: "20260714t195338z-disc"
タイトル: "PR Repair Unit U3 Workbench Descriptor Copy"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-07-15"
親: ["iss-00319"]
関連: []
authority: "proposed"
derived_from: ["20260714t195256z-chatgpt-output-pr-323-symlink-race-repair-design"]
reflected_to: []
---

# 20260714t195338z-disc PR Repair Unit U3 Workbench Descriptor Copy

## Repair Unit Identity

- source_batch: `20260714t154712z-pr-repair-batch`
- unit_id: `U3`
- root_cause_family: `workbench_copy.destination_symlink_race`
- covered_ids: `R8`
- source_links: PR #323 / latest Codex P1 / consultation `pr323-symlink-race-repair-design`
- evidence_ref: `artifacts/20260714t195256z-chatgpt-output-pr-323-symlink-race-repair-design.md`
- evidence_integrity: SHA-256 `92726c3966e78dfa3bdd5236093493966271f3a552fbc08b44de938c213799a1` / 40156 bytes / evidence-only
- bound_head_sha: `90a7adf3`
- failure_class: `review_feedback:workbench_destination_symlink_race`
- decided_priority: `P1`
- merge_blocking: `yes`
- disposition: `fix-now`
- status: `committed-and-pushed-awaiting-combined-re-observation`
- execution_order: `U3 before U4`; both units are required before PR re-observation

## Delegation Gate

- 本Artifactはworker delegation前に作成する。
- Workerは`gpt-5.6-sol` / reasoning `medium`を使う。
- allowed mutation files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_cli.py`
  - `spec-dock/scripts/spec_dock_runtime/infra/fs_cli.py`（providerのexact dogfood mirror）
  - `tests/unit/infra/test_runtime_fs_cli_workbench.py`
- forbidden mutation: 上記以外の全tracked file。特にapplication/CLI tests、public contracts、recursive directory traversalの全面fd rewrite、共通filesystem abstractionを含む。
- stop condition: Allowed boundaryだけで外部writeを防止できない、platform primitive不足でunsafe pathname fallbackが必要、public behavior変更が必要、U4 scopeとの結合が必要、またはsymlink-branch REDが現れた場合は実装せずorchestratorへ戻す。Symlink-branchはunit amendとfresh spec gateがpassするまで変更禁止。

## Validity / Need-To-Fix

- Current regular-file branchは`_assert_path_missing(destination)`後にpathname `shutil.copy2(source, destination, follow_symlinks=False)`を実行する。
- Missing check成功後にdestination leaf symlinkを挿入でき、`copy2`のdestination openがそのtargetをtruncate/writeし得る。
- Existing testsはmissing assertion前のleaf insertionを覆うが、check成功後からactual create/open直前のwindowを覆わない。
- Latest CI 4/4 passは当該windowを感知しないためP1 findingの反証にならない。
- need_to_fix: `yes`。Outside-repository write可能性が残るため、PRはU3完了までmerge-preparedではない。

## Adopted Design

1. Regular-file sourceを`O_RDONLY | O_NOFOLLOW`（availableなら`O_CLOEXEC`）でopenし、`fstat` identityを既存source identityへ照合する。
2. Destination parentを`O_RDONLY | O_DIRECTORY | O_NOFOLLOW`（availableなら`O_CLOEXEC`）でopenし、`fstat` identityを既存destination parent identityへ照合する。
3. Existing destination file/symlinkはparent fd + basenameで`stat(..., follow_symlinks=False)`してexpected identityを確認し、`unlink(..., dir_fd=parent_fd)`する。
4. Destination regular fileをparent fd + basenameで`O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW`、initial mode `0o600`としてexclusive createする。
5. Source fdからdestination fdへbytesをdescriptor copyし、short writeを完了まで処理する。
6. Required metadataはbytes、regular-file type、permission mode、mtime。`fchmod`とfd-safe timestamp operationを使う。
7. Pathname `shutil.copystat` fallbackは禁止する。xattrs、ACL、BSD flagsは今回のrequired contractに含めない。
8. `mutation_started`はexisting leafのsuccessful unlinkまたはdestination fdのsuccessful create後にtrue。Create後のcopy/metadata failureは従来のno-rollback contractを維持する。
9. Unsafe primitiveが利用できないplatformではfail closedとし、pathname copyへfallbackしない。

## Symlink-Branch Stop Boundary

- U3のauthorized implementation scopeはregular-file branchだけである。
- Symlink-branch REDが現れた場合、workerは直ちに停止してorchestratorへ報告する。
- Orchestratorが本unitをamendし、fresh spec-reviewer gateがpassするまでsymlink branchへ実装してはならない。
- Existing parameterized test hookを新しいprivate helperへ付け替える必要があるだけでは、symlink-branch scope expansionの根拠にならない。
- Recursive directory fd rewrite、root creation、source symlink leaf behaviorは現行U3のout of scopeを維持する。

## Deterministic Test Contract

- W-RACE-1: Missing leaf check成功後、exclusive create直前にexternal sentinelを指すsymlinkを挿入する。External sentinel bytes不変、outside新規fileなし、safe failure、source bytes不変をassertする。
- W-RACE-2: Existing destinationのsuccessful unlink後、exclusive create直前にexternal sentinel symlinkを挿入する。External sentinel bytes不変、safe failure、`mutation_started=True`をassertする。
- W-RACE-3: Destination parent pathnameを検証後に外部directoryへのsymlinkへ差し替える。Held original parent descriptor外へwriteせず、external sentinel/inventory不変をassertする。
- W-META-1: Safe regular-file copyでbytes、mode（例`0o640`）、fixed mtimeが一致する。
- Existing fault tests: `shutil.copy2` monkeypatchがdead boundaryになる場合だけ、新しいmodule-private descriptor copy/write boundaryへ最小更新する。
- Test fixtureはsafe synthetic bytesだけを使い、body、absolute host path、secret-like valueをevidenceへ出力しない。

## Validation Plan

```bash
uv run pytest tests/unit/infra/test_runtime_fs_cli_workbench.py
uv run pytest tests/unit/application/test_workbench.py tests/cli_runtime/test_workbench.py
cmp src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_cli.py spec-dock/scripts/spec_dock_runtime/infra/fs_cli.py
make lint
uv run pytest
git diff --check
```

- Current macOS hostで少なくとも`tests/unit/infra/test_runtime_fs_cli_workbench.py`をactual focused executionする。
- Actual Python 3.10 interpreterで`python3.10 -m pytest tests/unit/infra/test_runtime_fs_cli_workbench.py`をpre-push実行し、exact infra fileのpassを要求する。Python 3.10 interpreter unavailableはpassではなく、explicit gate/human conditionとして停止・報告する。
- U3差分に対するfresh code reviewer、QA reviewer、spec/pre-commit reviewerは完了し、blocking finding 0でPASS。
- Focused Python 3.10、related regression、new-node repetition、lint、parity、diff、fresh code/QA reviewsはPASS。Required full `uv run --python 3.12 pytest`もPASS（2600 passed / 75 skipped / 2 warnings, 1666.78s）。Commit/pushはhead `3dd94928d6d4b8a3810b9170b9fcb027572c64f2`で完了。
- Exploratory/non-requiredのPython 3.10 full-suite attemptはU3 gateではない。Test execution前のcollectionでpre-existing `scripts/authoring-pack/prepare_chatgpt_authoring_pack.py`の`datetime.UTC` importにより失敗したため、U3 regression/gate failureとは扱わない。Actual Python 3.10のU3 required focused gateは34 passedでPASS済み。
- U3 commit後もPR re-observationは行わず、U4完了後のlatest headで一度実行する。

## Out of Scope

- Recursive directory traversal全体のfd-relative rewrite。
- WorkbenchとArtifactの共通filesystem abstraction。
- xattrs、ACL、BSD flagsの`copy2` parity。
- Pathname `copystat`またはfull-path `open("xb")` fallback。
- Root Workbench bulk copy、sync/copy-back、classifier、public CLI/JSON変更。
- U4 Artifact publisher lifecycle。
- PR merge。

## Consultation Disposition

- use: Verified source/destination-parent descriptors、exclusive/no-follow leaf create、descriptor byte copy、deterministic external-sentinel tests。
- partial-use: Metadataはbytes/mode/mtimeだけrequired。これはuser simplicity-first constraintsとcanonical requirementsに整合するorchestrator bounded decisionであり、explicit human selectionとは主張しない。
- reject: Current U3でのsymlink-branch implementation。RED時はstop/report、unit amend、fresh spec gateが必要。
- reject: Common filesystem abstraction、pathname recheck/copy2/copystat fallback、recursive fd rewrite。
- Evidence Artifactはcanonical authorityではなく、本unitが採用境界を明示する。

## Commit / Re-observation Evidence

- implementation: `complete-locally`
- exact changed code/test files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_cli.py`
  - `spec-dock/scripts/spec_dock_runtime/infra/fs_cli.py`
  - `tests/unit/infra/test_runtime_fs_cli_workbench.py`
- scope boundary: Exactly the three authorized files。Regular-file branch only; symlink branch unchanged。
- RED: Before implementation、3 failed / 33 passed。
- GREEN actual Python 3.10: uv-provided Python 3.10.15、exact `tests/unit/infra/test_runtime_fs_cli_workbench.py` 34 passed。
- reviewer PATH correction: Code-review PATH confusion is superseded by actual uv interpreter evidence。Python 3.10.15 version and focused execution are verified; PATH presentation alone is not treated as interpreter evidence。
- related gates: Workbench application + CLI 47 passed。Four new nodes repeated 40/40。`make lint` PASS。Provider/dogfood `cmp` PASS。`git diff --check` PASS。
- fresh reviews: Code review PASS P0-P3=0。QA review PASS P0-P3=0。Spec/pre-commit review PASS。
- full pytest: Required `uv run --python 3.12 pytest` PASS。2600 passed / 75 skipped / 2 warnings in 1666.78s。
- exploratory Python 3.10 full suite: U3 non-gate。Collection failed before test execution on pre-existing `datetime.UTC` import in `scripts/authoring-pack/prepare_chatgpt_authoring_pack.py`; not a U3 regression or U3 gate failure。
- commit/push: `complete` at head `3dd94928d6d4b8a3810b9170b9fcb027572c64f2`
- local closure: R8/F6 implementation/quality/code+QA reviews/commit/push complete。
- U4 dependency: Satisfied。U4 local implementation/test/staticは完了し、fresh code review PASS、QA conditional PASS。Final fresh spec/precommit、commit/push、Ubuntu CI/re-observationはpending。
- latest-head re-observation: `intentionally-pending-after-U4-final-gates-and-push`; U3単独headでは実施しない。
