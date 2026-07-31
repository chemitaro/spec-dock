# Bounded Blue Team work packet

## 1. Repository verification

* **Repository:** `chemitaro/spec-dock`
* **Branch:** `iss-00334-implement-chatgpt-issue-planning-workflow`
* **Exact HEAD:** `2ff5c4bda05d80d68f56510b56500c88a4ce3302`
* GitHub identifies that exact branch and SHA as the PR head. The default branch is `main`; it was **not opened, inspected, or used as a fallback**.
* The provider and packaged projection of `issue_planning_apply.py` both resolve to blob `bd6171534c937f36180a6e54ab93e8d1d7b35c8f`; both copies must remain byte-identical after implementation.
* Scope is limited to the task contract and its three formal P1 findings.  

---

## 2. `FINAL-P1-001` — Atomically bind checked-out branch and local ref

### Exact functions and seams

Change both provider and packaged projection:

* `spec_dock_runtime.infra.issue_planning_apply._install_operation_commit_cas`
* `_execute_planning_apply_transaction`, at the install call and `committed` transition
* `_resume_publication`
* `_push_operation_commit_cas`
* Add one shared private guard, such as `_operation_branch_commit_is_proven`
* Add one private prepared-ref-transaction validator used only by the dedicated install seam

Do **not** reorder the application-layer resume shortcut. The authority check belongs in the infra resume/publication proof.

The current installer samples `HEAD` and its symbolic target, separately updates `refs/heads/<operation.branch>`, and then performs fallible post-checks inside the same helper.  The caller does not mark the commit installed until that helper returns.  Resume currently proves only the resolved `HEAD` commit, not the exact symbolic branch and branch ref.

### Minimal invariant

A local commit is installed only when one ref transaction proves all of the following while the refs are locked:

1. `HEAD` is a symbolic checkout of exactly `refs/heads/<operation.branch>`.
2. That branch’s old value is exactly `operation.expected_head`.
3. That same branch is changed to exactly `local_commit`.

After installation, all resume, push, and terminal-ready paths require:

```text
symbolic-ref HEAD == refs/heads/<operation.branch>
refs/heads/<operation.branch> == local_commit
HEAD == local_commit
```

A mismatch must prevent push, publication evidence, and `ready`.

### Implementation sequence

1. Retain the existing immutable commit/tree/path/trailer proof before installation.

2. Replace the sampled branch check plus direct branch update with one dedicated ref transaction:

   * Run `git update-ref HEAD <local_commit> <expected_head>` so Git updates the actual checked-out referent.

   * Execute it with a private `reference-transaction` prepared-state validator.

   * The validator accepts only a prepared update inventory containing the exact branch update:

     ```text
     <expected_head> <local_commit> refs/heads/<operation.branch>
     ```

     It must reject an alternate branch, detached `HEAD`, another old value, another new value, duplicate branch entries, or unexpected branch refs.

   * Preserve the repository’s effective native `reference-transaction` hook by delegating to it exactly once with the original phase and stdin; do not replace or suppress it.

   * A nonzero prepared hook aborts the locked transaction, while `update-ref HEAD <new> <old>` provides the old-value CAS. ([Git SCM][1])

3. Make `_install_operation_commit_cas` return immediately after a successful transaction exit. It must not perform a fallible symbolic-ref or rev-parse post-read before returning.

4. Set `committed = True` immediately after that return, before hooks, evidence writes, status probes, or any other fallible post-install operation. Once the ref transaction succeeds, the rollback lane must not treat the operation as pre-commit.

5. Add `_operation_branch_commit_is_proven(operation, repo_root, local_commit)` and use it:

   * at `_resume_publication` entry;
   * inside `_push_operation_commit_cas`, immediately before spawning `git push`;
   * after remote parity and immediately before `_record_publication` and a terminal `ready`/`plan_rejected` result.

6. Keep `update-ref` confined to the dedicated installer. Do not widen `_run_git` or `validate_planning_git_argv` to permit arbitrary ref updates.

### Deterministic Red tests and Green expectations

In `tests/integration/test_issue_planning_apply.py`:

1. **Branch switch at the install transaction boundary**

   * Create `alternate` at `expected_head`.
   * Switch from the operation branch to `alternate` immediately before the ref transaction.
   * **Green:** `recovery_required/restore_mismatch`; both local branches remain at `expected_head`; remote remains at `expected_head`; no `commit.json`, `publication.json`, or `ready`.

2. **Resume from another branch at the same proved commit**

   * Produce `publication_pending/push_failed`.
   * Create and check out `alternate` at `local_commit`.
   * Retry while making any remote observation or push a test failure.
   * **Green:** `recovery_required/restore_mismatch` before remote access; operation branch and remote unchanged; no publication evidence.

3. **Branch switch immediately before initial push**

   * At `before_push`, switch to `alternate` at `local_commit`.
   * **Green:** `publication_pending/remote_parity_unconfirmed`; push is not invoked; remote remains `expected_head`; no publication evidence or `ready`.

4. **Branch switch after push but before ready**

   * At `after_push`, switch to `alternate` at `local_commit`.
   * **Green:** the reviewed remote may contain `local_commit`, but the result remains `publication_pending/remote_parity_unconfirmed`; no `publication.json` and no terminal `ready`.

In `tests/unit/infra/test_issue_planning_apply.py`:

* Prove the prepared transaction validator accepts only the exact operation branch old→new update.
* Cover alternate branch, detached `HEAD`, wrong old SHA, wrong new SHA, duplicate branch updates, and native-hook rejection.
* Prove the native `reference-transaction` hook is delegated exactly once per received phase.

### Compatibility constraints

* No new public status, reason, result field, or evidence schema.
* Preserve commit signing and existing `pre-commit`, `prepare-commit-msg`, `commit-msg`, and `post-commit` behavior.
* Do not add a generic ref-mutation API.
* Do not move normal resume through the full application preflight.
* Keep provider/projection bytes identical.

---

## 3. `FINAL-P1-002` — One strict operation-trailer parser

### Exact functions and seams

Change:

* Add one private parser/proof helper, such as `_operation_trailer_is_proven`
* `_create_verified_operation_commit`
* `_operation_commit_is_proven`
* `_resume_publication`

Current pre-install, immutable-commit, and resume proofs all use substring membership.    The focused integration test covers only complete trailer removal.

### Minimal invariant

The parsed terminal Git trailer block must contain:

* exactly one trailer key equal, case-sensitively, to `SpecDock-Planning-Operation`;
* its complete unfolded value equal exactly to `operation.operation_id`;
* no second occurrence of that key, whether its value is equal or different.

An identical-looking line outside the Git trailer block is not proof. Unrelated valid trailers remain allowed.

### Implementation sequence

1. Implement the single parser with:

   ```text
   git interpret-trailers --parse --no-divider
   ```

   Feed it the raw message bytes on stdin. Fail closed on a nonzero exit, undecodable/malformed output, folded or ambiguous target values, or an invalid inventory. `--parse` emits only parsed input trailers, and `--no-divider` is appropriate when the input is the commit message rather than a patch. ([Git SCM][2])

2. Parse each returned trailer at the canonical separator and compare the target key and value exactly. Do not use `in`, `startswith`, `endswith`, case-folding, or regex substring acceptance.

3. Invoke the same helper:

   * after `commit-msg` has completed and before `commit-tree`;
   * from `_operation_commit_is_proven` against the immutable commit message;
   * during resume by calling `_operation_commit_is_proven` instead of maintaining a second message/path/trailer implementation.

4. Remove all direct substring checks for this trailer.

### Deterministic Red tests and Green expectations

In `tests/unit/infra/test_issue_planning_apply.py`, parameterize the parser with:

* exact key and exact value — accepted;
* exact trailer plus an unrelated trailer — accepted;
* `Not-SpecDock-Planning-Operation` — rejected;
* `SpecDock-Planning-Operation-Extra` — rejected;
* value prefixed with extra bytes — rejected;
* value suffixed with extra bytes — rejected;
* two exact target trailers — rejected;
* one correct and one wrong target-key occurrence — rejected;
* exact-looking line in an earlier body paragraph, followed by a non-trailer final paragraph — rejected.

In `tests/integration/test_issue_planning_apply.py`:

1. Expand the existing `commit-msg` rewrite test into the same invalid-form matrix.

   * **Green:** `rolled_back/planning_commit_failed`; local branch and remote remain `expected_head`; no commit or publication evidence.

2. Construct resume evidence around a commit with the correct parent/tree/path set but a duplicate or body-only operation line.

   * **Green:** `recovery_required/restore_mismatch` before remote observation or push.

3. Retain a positive hook test that appends an unrelated valid trailer.

   * **Green:** normal publication succeeds, hook order remains unchanged, and the resulting commit has exactly one operation trailer.

### Compatibility constraints

* Keep the existing subject and operation ID unchanged.
* Preserve other project/user trailers.
* Preserve hook order, signing intent, parent, tree, and changed-path proofs.
* Do not change `commit.json`, operation identity, or public result contracts.
* Do not normalize near-match keys or values into acceptance.

---

## 4. `FINAL-P1-003` — Bind publication to the reviewed repository endpoint

### Exact functions and seams

Change both provider and packaged projection:

* `infra.git_cli`

  * add a narrow immutable publication-endpoint result, or extend the existing GitHub remote parser so it returns both normalized repository slug and the captured push URL;
  * retain `origin_github_repo_slug` behavior for existing callers.
* `issue_planning_apply`

  * add frozen private `_PublicationAuthority`
  * add `_capture_publication_authority`
  * change `_remote_head_observation`
  * change `_remote_head`
  * change `_push_operation_commit_cas`
  * change `_cas_failure_result`
  * thread the authority through initial publication and `_resume_publication`

The current observation and push seams use the literal alias `origin`.  Initial publication and parity reuse those seams.  Resume does the same.  Existing `git_cli` already recognizes GitHub HTTPS/SSH URLs and validates fetch/push slug equality; extend that seam rather than introducing a second URL grammar.

### Minimal invariant

Every remote observation, lease decision, push, and parity proof for an operation uses one immutable endpoint whose normalized GitHub repository is exactly `operation.repository`.

After capture, changing `remote.origin.url` or `remote.origin.pushurl` cannot alter the publication destination or parity source.

### Implementation sequence

1. Add a frozen private authority value:

   ```text
   repository: normalized owner/repo
   push_endpoint: captured exact URL
   ```

2. For a new transaction, capture it before mutation and before commit hooks can alter repository configuration. For resume, capture it before the first remote observation.

3. Resolve the configured origin fetch and push endpoints once and require:

   * both are valid supported GitHub endpoint forms;
   * both normalize to the same repository;
   * that repository equals `operation.repository`.

4. Retain only the captured push endpoint as the in-memory publication authority. Do not persist or expose the endpoint because it may contain user or credential material.

5. Pass the authority explicitly through every remote seam:

   * `ls-remote --heads <authority.push_endpoint> ...`
   * `push <lease> <authority.push_endpoint> <refspec>`
   * CAS-failure re-observation
   * post-push parity observation
   * resume observation and push

   No publication command may contain the remote name `origin`.

6. Failure mapping:

   * authority mismatch before a new mutation: existing `stale/apply_target_changed`;
   * authority mismatch while resuming committed evidence: existing `recovery_required/restore_mismatch`;
   * no new status or reason values.

7. Re-run the P1-001 local branch/ref guard immediately before push and before recording parity, independently of endpoint authority.

### Deterministic Red tests and Green expectations

In `tests/unit/infra/test_issue_planning_apply.py`:

* HTTPS and SSH endpoints for the exact operation repository are accepted.
* Fetch/push repository mismatch, wrong owner/repository, missing endpoint, non-GitHub endpoint, and malformed endpoint are rejected.
* Push and `ls-remote` argv contain the captured endpoint and never the string `origin`.
* `_cas_failure_result` reuses the same authority object.

In `tests/integration/test_issue_planning_apply.py`:

1. **Initial publication retarget**

   * Create reviewed primary and unreviewed secondary bare repositories, both at `expected_head`.
   * Capture primary authority.
   * At `before_push`, retarget `origin` to secondary.
   * Make the reviewed primary reject the push so an accidental push to secondary would be observable as a false success.
   * **Green:** `publication_pending/push_failed`; secondary remains at `expected_head`; no publication evidence and no `ready`.

2. **Post-push parity retarget**

   * Push successfully through captured primary authority.
   * At `after_push`, retarget `origin` to secondary.
   * **Green:** parity is still read from primary; secondary remains unchanged. A terminal result is permitted only from primary parity.

3. **Resume after origin retarget**

   * First produce committed `publication_pending` evidence against primary.
   * Before retry, retarget `origin` to secondary.
   * **Green:** authority validation fails before any observation or push; `recovery_required/restore_mismatch`; neither remote changes; no publication evidence or `ready`.

For local-bare integration fixtures, monkeypatch only the private authority-capture seam to map the primary and secondary paths to distinct repository identities. Do not weaken the production GitHub URL validation to accommodate test paths.

### Compatibility constraints

* Preserve HTTPS versus SSH endpoint choice and normal Git credential/SSH handling.
* Do not persist, log, or return the captured URL.
* Keep `operation.repository`, operation ID bytes, and evidence schemas unchanged.
* Do not add a default-branch fallback or derive a publication branch from the remote.
* `origin` may be consulted only during authority capture; it is not publication authority afterward.

---

## 5. Cross-finding ordering and focused verification

### Implementation order

1. Implement the strict trailer parser and route all commit proofs through it.
2. Replace local installation with the atomic checked-out-ref transaction and add the shared branch/ref guard.
3. Add immutable publication authority and thread it through all remote seams.
4. Mirror every runtime change into `src/spec_dock/assets/...`.
5. Run focused tests, then parity and static checks.

### Verification commands

```bash
uv run pytest -q \
  tests/unit/infra/test_issue_planning_apply.py \
  -k 'trailer or branch or install or push or remote or publication'
```

```bash
uv run pytest -q \
  tests/integration/test_issue_planning_apply.py \
  -k 'trailer or branch or commit_install or alternate or origin or publication or resume'
```

```bash
uv run pytest -q \
  tests/unit/infra/test_issue_planning_apply.py \
  tests/integration/test_issue_planning_apply.py \
  tests/unit/application/test_issue_planning_apply.py
```

```bash
cmp -s \
  spec-dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py

cmp -s \
  spec-dock/scripts/spec_dock_runtime/infra/git_cli.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py

git diff --check
make lint
```

---

## 6. Explicit non-goals

* No hostile same-UID tampering protection inside private `0700` workspaces.
* No post-replacement stale-file-descriptor retention.
* No continuous-latest canonical semantics during repeated contention.
* No redesign of public status/reason/output schemas or Human-decision binding.
* No change to canonical three-document semantics, companion bytes, or Candidate ZIP bytes.
* No personal `chatgpt-use` wrapper dependency, API fallback, default-branch fallback, or alternate browser profile.
* No P2/P3 findings, broad Git abstraction, or replacement architecture.

[1]: https://git-scm.com/docs/git-update-ref.html?utm_source=chatgpt.com "Git - git-update-ref Documentation"
[2]: https://git-scm.com/docs/git-interpret-trailers?utm_source=chatgpt.com "Git - git-interpret-trailers Documentation"
