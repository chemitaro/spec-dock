Review identity:
  repository: `chemitaro/spec-dock`
  branch: `codex/iss-00354-chatgpt-context-contract`
  source_head: `a93d38bc07a11a62a63ebdab19f9d26a0cb39938`
  candidate_or_step: `S06`
  fresh_red_thread: `true`

GitHub connector comparison confirmed that the named branch tip is identical to the specified HEAD, with ahead `0` / behind `0`; the default branch was not inspected as a substitute. The fetched commit identity is also `a93d38bc07a11a62a63ebdab19f9d26a0cb39938`.

Verdict: **FAIL**
Counts: **P0=0 P1=3 P2=1 P3=0**

Findings:

* ID: `RT-354-S06-001`
  severity: `p1`
  location: `application/ports.py::BlueThreadBinding`, `BlueBindingResolution`; `application/issue_planning.py::run_issue_planning_revise`; `tests/unit/application/test_issue_planning.py::_FakeThreadPort.resolve_blue`
  violated_contract: `ISS354-REQ-011`, `ISS354-REQ-013`; S06 brief §4.2 exact-lineage resolution; `tc-s06-001`
  concrete_impact: A binding belonging to another Candidate/source lineage can be classified as `exact` and passed to `invoke_continuation()`. An invalid resolution status can also fall through as `unavailable`, silently starting a new Blue execution. This permits cross-Candidate context contamination or an unintended new conversation instead of a Human block.
  minimal_evidence: `BlueThreadBinding` carries `lineage_sha256`, but neither its format nor its equality with the requested `GitBoundOperationBindingV1.binding_sha256` is validated. `run_issue_planning_revise()` trusts `resolution.status == "exact"` without correlating the returned binding to `prior_lineage`; every status other than `exact` or `ambiguous` is effectively treated as `unavailable`. The test fake discards the requested lineage and returns a constant binding, so the positive test cannot detect the mismatch.    The canonical requirement permits continuation only for a verified matching repository/branch/HEAD/Issue/Candidate lineage.
  required_action: Close and validate the resolution contract at runtime; require a lowercase SHA-256 lineage digest and compare an `exact` binding to the requested `prior_lineage.binding_sha256` before invocation. Unknown status or digest mismatch must block without backend invocation. Add negative cross-lineage and unknown-status tests.

* ID: `RT-354-S06-002`
  severity: `p1`
  location: `application/ports.py::ThreadInvocationReceipt`; `application/issue_planning.py::_thread_backend_invoker`, `_commit_published_blue`, `run_issue_planning_create`, `run_issue_planning_review`, `run_issue_planning_revise`
  violated_contract: `ISS354-REQ-031`; Design §12.2 binding transaction; S06 brief §5 and required “送信前失敗” tests
  concrete_impact: Submission state is not an authoritative publication gate. The receipt contract accepts `successful` without a Blue binding and accepts inconsistent `not_submitted`/`unknown` plus pass-result combinations. Create/review/revise consume only `receipt.result`; Candidate or Review publication can therefore occur without a verified successful submission. In the successful-without-binding path, Candidate publication completes first and the command then returns `blocked`, leaving an orphaned Candidate with no committed Blue lineage and creating collision risk on retry.
  minimal_evidence: `ThreadInvocationReceipt.blue_binding` is optional with no cross-field invariant. `_thread_backend_invoker()` returns `receipt.result` without validating `submission_state`. In create, `publisher()` runs before `_commit_published_blue()`; only after publication does that helper discover a missing binding and return `planning_context_rejected`.    The brief requires `not_submitted` to produce Candidate/Review publication count `0`, and the design binds private thread evidence before validation while committing Candidate lineage only after valid publication.
  required_action: Validate a mode-specific receipt before processing or publishing its result. A successful Blue invocation must carry a valid matching Blue binding; `not_submitted` and `unknown` must not authorize Candidate or Review publication. Preserve `commit_blue()` after valid publication, but prevent any missing/invalid-binding path from reaching publication.

* ID: `RT-354-S06-003`
  severity: `p1`
  location: `tests/unit/application/test_issue_planning.py` S06 tests; `tests/unit/domain/test_issue_planning_contracts.py`
  violated_contract: S06 brief §6 required tests; Plan `cl-s06-blue-red` / `tc-s06-001` required transaction, privacy, unavailable, source-drift, and publication evidence
  concrete_impact: The test suite can remain green while both blocking defects above are present. It does not establish the required Planning → committed Blue → same-binding Revision → distinct fresh Red transaction, nor the prescribed pre-submit, unknown, publication-failure, and privacy matrix. S06 closure therefore lacks the required executable evidence.
  minimal_evidence: The create, revision, and review tests use separate fake ports rather than one stateful lineage store. The semantic-revision setup creates its Candidate without a thread port, then injects an unrelated constant binding. The review test uses another new port and never compares its Red binding or provider handle with the committed Blue binding. No S06 test covers `not_submitted`, `continuation_unavailable_before_submission`, unknown-state fallback counts, publication collision/failure commit counts, successful-but-unpublished reuse, or the full private sentinel scan required by the brief. The domain test blob was unchanged in the S06 commit.   The omitted matrix is explicitly mandatory.
  required_action: Add one stateful `tc-s06-001` transaction using the same port/store across Planning, Revision, and Review; assert committed lineage and provider-handle identity for Blue, distinct Red identity, and no reusable Red state. Add the complete not-submitted/unknown/unavailable/publication/source-drift/privacy matrix specified by the brief.

* ID: `RT-354-S06-004`
  severity: `p2`
  location: source-HEAD-to-target diff; `artifacts/implementation-briefs/s06-blue-continuity-fresh-red-20260805.md`
  violated_contract: S06 brief §3.2 changed-file allowlist, §3.3 `artifacts/**` read-only boundary, and its exact allowlist-audit command
  concrete_impact: The implementation Candidate is not scope-clean against its declared source HEAD, and the brief’s own allowlist audit would return nonzero. Runtime behavior is unaffected, but the implementation provenance and mandatory diff-consistency evidence are invalid.
  minimal_evidence: GitHub comparison from brief source HEAD `382e49b5b3d93ff26c4672e633cb33481ca61991` to target HEAD shows the implementation brief itself added under `artifacts/**`, in addition to the three allowed runtime/test files. The contract permits only the four listed application/test paths and explicitly marks `artifacts/**` read-only.   The brief is present in the exact target commit.
  required_action: Rebind the implementation source baseline to a commit where the approved brief already exists, or remove the brief addition from the implementation delta, then rerun the exact allowlist and diff-consistency checks.

Verification evidence:

* GitHub repository access succeeded. The named branch was inspected directly and matched the requested HEAD exactly; no default-branch fallback was used.
* GitHub comparison of `382e49b5b3d93ff26c4672e633cb33481ca61991...a93d38bc07a11a62a63ebdab19f9d26a0cb39938` showed one commit and four changed paths: the S06 brief, `application/ports.py`, `application/issue_planning.py`, and `tests/unit/application/test_issue_planning.py`.
* Exact-head Git blob SHAs matched all attached copies reviewed: canonical requirement/design/plan, S06 brief, both source files, and both test files.
* A supplemental local `python -m py_compile` of the four exact attached Python blobs completed successfully.
* A supplemental runtime/static probe confirmed that `ThreadInvocationReceipt(submission_state="successful", blue_binding=None)` and an unrecognized `BlueBindingResolution.status` are accepted, that semantic revision does not read `BlueThreadBinding.lineage_sha256`, and that Candidate publication precedes `_commit_published_blue()`.
* Focused pytest, the complete application/domain suites, Ruff, mypy, `spec-dock validate`, and repository `git diff --check` were **not observed**. The review container had no repository checkout and could not resolve GitHub for a read-only clone; the exact commit also had no connector-visible workflow runs or combined status checks.
* Exact-head `report.md` still records S06–S13 as pending with no S06 execution evidence. It therefore does not falsely claim live Oracle/provider continuation is complete.

Review conclusion:
  no patch or repaired Candidate was generated by Red Team: `true`
