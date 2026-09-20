---
種別: artifact
ID: "20260920t055027z"
タイトル: "Luna Max Implementation Handoff"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-09-20"
親: ["iss-00405"]
template: "blank"
authority: "evidence"
derived_from: []
reflected_to: []
---

# Luna Max Implementation Handoff — iss-00405

## 0. Authority and state

- task: Issue #405 Directory Replacement Final Cleanup implementation
- repository: `chemitaro/spec-dock`
- authoring branch: `iss-00405-directory-replacement-final-cleanup`
- specification source SHA: `457faf31df8840d1f2fc87417d297dc318903fbe`
- canonical Issue path: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00405-directory-replacement-final-cleanup`
- state: specification draft; implementation/review/qualification未実行
- parent merge history is context only; Issue #405 remains OPEN

Start only after Codex has placed and reviewed the canonical `requirement.md`, `design.md`, and `plan.md`. Re-read the actual repository HEAD and `AGENTS.md`; do not assume this handoff SHA is still HEAD after specification adoption commits.

## 1. Non-negotiable design decisions

1. Delete provider repository shared lease, generation witness/global state, broad capability gate, and generation-drift reauthentication.
2. Keep Git clean check, fixed target commit, and branch/HEAD postcondition.
3. Keep worktree target no-follow, EX lock, device/inode binding, same-filesystem preflight, safe materializer, entrypoint-last, and consumer hook bound cwd.
4. Keep node create/import locks, explicit artifact source/publication guards, active rollback, and secret/credential redaction.
5. Keep `git_helper.py`, but rewrite it to a single target-bound cwd executor. It must not open/lock repository root and must not expose `lease-fd` vocabulary.
6. Use an unlocked source directory FD only for same-filesystem probing; close it before Git child execution and never pass it to a child.
7. Ordinary issue checkout and worktree add/remove use direct native Git with fixed commit/path. Only materializer `read-tree` uses the target-bound cwd helper.
8. Do not add compatibility aliases for deleted internal types/ports/functions.
9. Do not change installer semantics unless the new mid-copy test demonstrates a real contract defect.
10. Do not reintroduce ledger, sharder, performance qualification, policy skip, provider marker, journal, rollback, or resume token.

## 2. Exact implementation delta

### 2.1 contracts

Path:
`src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`

Delete:

- `GitCapabilityAssessment`
- `PinnedCheckout`

Keep:

- `GitWorktreeRecord`
- `WorktreeCreateResult.bound_cwd_fd/bound_device/bound_inode`
- `GuardedExplicitFileSource`
- Artifact/publication failure types

Do not globally rename the word `lease`; explicit file source lifetime is a different safety boundary.

### 2.2 ports and adapter

Paths:

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py`

Delete GitGateway methods:

- `checkout_branch`
- `create_and_checkout_branch`
- `assess_capabilities`
- `pinned_checkout`
- `verify_pinned_checkout`

Add/replace exactly as canonical Design:

- `checkout_fixed_ref`
- `add_worktree_at_commit`
- `materialize_worktree(repo_root, path=worktree_path, target_commit=target_commit, target_fd=target_fd)`
- `remove_worktree(repo_root, path=worktree_path, force=force, target_fd=target_fd)`

Remove `source_fd` from worktree Git adapter interfaces.

### 2.3 git_cli

Path:
`src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py`

Delete:

- `_WRITING_GIT_COMMANDS`
- `_run_git_write`
- `assess_capabilities`
- `pinned_checkout`
- `verify_pinned_checkout`
- provider shared-flock error mapping

Retain direct read helpers and remote redaction.

Implement `checkout_fixed_ref` with CAS no-op for existing ref, native switch/create, and exact branch/HEAD postcondition. Implement `_run_git_in_bound_cwd` only for target `read-tree`.

Rename:

- `add_worktree_pinned` → `add_worktree_at_commit`
- `pinned_commit` → `target_commit` in worktree interfaces/errors

Do not remove `_validate_link_target`, `_materialize_tree_entry` submodule rejection, no-replace entrypoint publication, directory witnesses, or content/mode verification.

### 2.4 git_helper

Path:
`src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_helper.py`

Target parser:

```text
--cwd-fd (required)
--expected-device (required)
--expected-inode (required)
argv remainder
```

Algorithm:

1. parse child argv and require non-empty;
2. `fstat(cwd_fd)`;
3. require directory and expected device/inode;
4. `fchdir(cwd_fd)`;
5. execute child and wait;
6. return child status;
7. content-free error on validation/OS failure.

No repository root discovery, no flock, no repeated lease descriptors, no generation terminology. Retain `_runtime_scripts_root()` and `_helper_environment()` so `_run_git_in_bound_cwd` launches the provider module with provider `cwd`/`PYTHONPATH`; pass only `cwd_fd` to the helper, close it after `fchdir`, and do not pass it to the Git child.

### 2.5 set_active / issue_lifecycle

Paths:

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_lifecycle.py`

Delete global `_LAST_PINNED_CHECKOUT` and `last_pinned_checkout` import/use. `checkout_active_target` completes fixed-ref verification internally and returns `BranchDecision`. Preserve lifecycle order and existing partial-state guidance.

### 2.6 worktree

Path:
`src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py`

- `_pin_worktree_source`: current HEAD only; remove broad assessment.
- `_open_source_shared`: delete.
- add `_open_source_directory_for_filesystem_probe`: no-follow, no flock.
- compare source probe `st_dev` with target FD, then close source probe.
- keep target FD EX and inode witness through add/materialize/publication/hook.
- remove source FD from remove path; keep target FD through Git and cleanup.
- keep current same-filesystem rejection; do not add cross-filesystem implementation.

## 3. Test execution order

### First: change tests

Implement exact mappings in `artifacts/test-disposition.csv`. The following must become explicit successors before Product implementation:

- fixed-ref new/existing checkout
- dirty precondition
- positive hook/fsmonitor/diff/merge/sparse cases
- worktree submodule rejection before entrypoint publication
- target-bound `read-tree` without source lease
- target-bound helper provenance

Expected pre-implementation behavior:

- positive gate-removal cases: first runを保存する。current broad gateでRedになり得るが、Greenなら`covered-existing`
- dirty/target/hook safety: Green
- mid-copy successor later may already be Green

Never manufacture Red by changing Product behavior or weakening setup.

### Focused after implementation

```bash
uv run pytest \
  tests/cli_runtime/test_generation_checkout.py \
  tests/cli_runtime/test_worktree.py \
  tests/cli_runtime/test_runtime_handoff.py \
  tests/cli_runtime/test_worktree_lifecycle_coordination.py \
  tests/cli_runtime/test_issue_lifecycle.py \
  -q
```

### Harness/installer cleanup

Follow S4 exactly. The 4th-copy injection is a test seam, not a new Product constant. Verify version remains `old-version\n`, data remains unchanged, first three/partial/last two states are observable, then rerun to exact six-tree parity.

### Integrated

Follow canonical Plan S6. Do not replace ordinary pytest with any legacy evaluator.

## 4. Provider-first and dogfood

Edit only `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**` and the provider docs under `src/spec_dock/assets/spec_dock/docs` / `scripts` first. Do not hand-edit provider and dogfood in parallel. After provider tests are Green and checkpointed:

```bash
git diff --exit-code HEAD -- spec-dock/initiatives
uvx --no-cache --from . spec-dock update .
git diff --exit-code HEAD -- spec-dock/initiatives
```

Then verify runtime/docs/skills parity. If protected data changes, stop and preserve evidence; do not clean it automatically.

## 5. Parent docs and Report

At S5/S7:

- update parent Epic `plan.md` and `report.md` only with observed state;
- identify Issue #405 as final cleanup;
- move old shared coordination/qualification narrative to Historical appendix;
- do not change parent Requirement R1〜R10 or accepted ADR;
- write Issue `report.md` only after actual commands run;
- do not claim browser validation, full suite, platform jobs, review, or merge unless evidence exists.

## 6. Commit discipline

Before every commit:

```bash
git config user.name
git config user.email
git diff --check
```

Run each Git command in a separate tool call and compare the returned identity with `chemitaro` / `84865385+chemitaro@users.noreply.github.com`. Use the `git-commit` skill and `commit-codex -a`. Do not commit the Red-only S1 state; group S1 tests and S2 implementation after S3 verification is Green. Use Japanese Conventional Commits and the checkpoint boundaries in canonical Plan. Never merge the PR; stop at merge-ready handoff.

## 7. Hard stop conditions

Stop and return to Codex/user if any of the following is true:

- target-bound helper cannot be retained without a public contract change;
- worktree target safety requires path-only execution;
- data path mutation is observed;
- secret/private content appears in output;
- cross-filesystem support, same-EUID adversary guarantee, atomic installer, or new CLI option becomes necessary;
- old ledger/sharder/qualification must be restored;
- a test marked KEEP can only pass by deleting or weakening its contract.

No owner decision is currently outstanding. Pending tests/review are evidence obligations, not design choices.
