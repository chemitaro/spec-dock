# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a699fd0-fb58-83ee-9cd8-4789115f855c

## Prompt

Required repository connector context:
- @GitHub chemitaro/spec-dock
- Current branch: iss-00334-implement-chatgpt-issue-planning-workflow
- Default branch: main
- MUST inspect this GitHub repository with the GitHub connector before answering.
- First inspect the current branch. If the current branch does not exist or cannot be opened, inspect the default branch instead.
- Hard failure condition: if the GitHub connector/app is unavailable, or if the repository, current branch, and default branch cannot be accessed, return immediately with exactly: repository access failed.
- Do not continue from attached files, prompt context, memory, or general knowledge when repository access fails.
- Attached files and prompt-provided context are supplementary only after repository access succeeds.

Fresh read-only defect review. MUST use @GitHub chemitaro/spec-dock and inspect only branch iss-00334-implement-chatgpt-issue-planning-workflow at exact HEAD cdfb47171d921ff9f5e28c675de75b2ae52921da. This exact-branch rule overrides generic default-branch fallback; if exact HEAD cannot be verified return exactly repository access failed. Review diff ff5264689c192781d82ed05b4f02909042f3f47a..cdfb47171d921ff9f5e28c675de75b2ae52921da plus surrounding source/tests and the two committed artifacts whose names contain s08-chatgpt-implementation-work-packet and s08-chatgpt-compatibility-decision. Report only concrete P0/P1 correctness, security, integrity, fail-closed, compatibility, or required-test defects. No P2/P3, improvements, redesign, style, future flexibility, or patches. Do not report the known tests/integration/test_issue_planning_chatgpt_transport.py classify_transport_frame collection failure; S11 owns that migration. Do not object to temporary transient_payload compatibility itself; S10 owns removal. Check direct PATH Oracle 0.16.1 only, capability preflight, one submit, same-session harvest, allowlisted env, executable identity recheck, bounded contained regular no-symlink hash-validated private artifact snapshot, single-root Planner ZIP, strict Reviewer JSON object, exact typed-or-temporary-legacy result invariants, no bytes serialization/repr/equality leakage, production typed-only, and pre-S10 application fail-closed Candidate publication zero. Return exactly one JSON object: review_status pass|fail; source_repository; source_branch; source_head; findings array with id priority path line problem impact required_fix required_test; verified_checks; known_deferred; confidence. FAIL iff findings contains P0/P1. Do not modify repository.

## Answer

{
"review_status": "fail",
"source_repository": "chemitaro/spec-dock",
"source_branch": "iss-00334-implement-chatgpt-issue-planning-workflow",
"source_head": "cdfb47171d921ff9f5e28c675de75b2ae52921da",
"findings": [
{
"id": "P1-001",
"priority": "P1",
"path": "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py",
"line": "252-281",
"problem": "The prompt-bearing Oracle executable is re-resolved and identity-checked immediately before submission, but _recover_same_session later executes the previously stored path without re-resolving it or comparing its identity with the preflighted 0.16.1 executable. A timeout can therefore be followed by a harvest invocation of a replaced or upgraded binary that never passed the version and capability preflight.",
"impact": "The long-running recovery path does not preserve the direct-PATH-Oracle-0.16.1-only invariant. A different executable can process the session after submission, causing incompatible session interpretation or unintended code execution from the repository working directory.",
"required_fix": "Carry the preflighted resolved path and executable identity into recovery. Immediately before every recovery Oracle subprocess, re-resolve PATH oracle, require the same resolved path and identity, and start no process on mismatch. Return a closed blocked result without attempting a new submission.",
"required_test": "Force the prompt call to time out, change the resolved executable identity before recovery, and assert exactly one prompt submission, zero harvest subprocesses after the change, no typed or legacy payload, and the selected closed blocked reason."
},
{
"id": "P1-002",
"priority": "P1",
"path": "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py",
"line": "284-293",
"problem": "_session_is_terminal converts every OracleArtifactError into False. Wrong session identity, unsupported mode, malformed metadata, and other deterministic metadata-integrity failures are consequently treated as an ordinary nonterminal session, followed by harvest and ultimately blocked/oracle_session_recovery_required instead of rejected/oracle_artifact_rejected.",
"impact": "Corrupt or identity-mismatched metadata is misclassified as recoverable transport uncertainty. This violates the closed reason contract, obscures evidence tampering or incompatible metadata, and can prompt repeated recovery attempts for an artifact that must be rejected.",
"required_fix": "Replace the boolean probe with a closed state that distinguishes missing or genuinely nonterminal metadata from invalid metadata. Only the former may enter same-session harvest. Propagate deterministic identity, mode, schema, or parse failures as rejected/oracle_artifact_rejected.",
"required_test": "Exercise invoke_issue_planning_chatgpt with completed metadata containing a wrong session id, wrong mode, and malformed JSON. Each case must submit the prompt once, perform no duplicate submission, return rejected/oracle_artifact_rejected rather than recovery_required, and expose no raw metadata or private path."
},
{
"id": "P1-003",
"priority": "P1",
"path": "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py",
"line": "185-267",
"problem": "_contained_regular_path lstat-checks each pathname component and then returns a pathname that _open_regular_nofollow reopens later. O_NOFOLLOW protects only the final component; an ancestor directory can be replaced with a symlink between the checks and os.open, causing the open to resolve outside the submitted session root.",
"impact": "The adapter can snapshot bytes from outside the Oracle session despite the stated containment and no-symlink boundary. Metadata-controlled size and SHA checks do not restore containment when the substituted outside file and metadata agree.",
"required_fix": "Use descriptor-rooted traversal. Open and retain a verified session-root directory descriptor, open every ancestor relative to its parent with directory and no-follow flags, and open the leaf relative to the retained parent descriptor. Perform fstat, bounded read, and copy from that descriptor without reopening a reconstructed pathname. Apply the same model to meta.json.",
"required_test": "Introduce a deterministic race hook that replaces a previously checked artifact parent directory with a symlink to an outside directory immediately before the leaf open. Assert rejection, no outside bytes in the returned snapshot, and no private path in the result or exception."
},
{
"id": "P1-004",
"priority": "P1",
"path": "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py",
"line": "119-129,298-314",
"problem": "Not all validation failures from untrusted Oracle output are normalized to OracleArtifactError. Reviewer JSON is first parsed permissively and then passed to OracleReviewJsonPayload, whose strict duplicate-key and nonstandard-number validation raises ValueError outside the helper's catch boundary. ZIP validation can likewise raise RuntimeError or other zipfile exceptions, for example for encrypted or unsupported entries. _collect_typed_result catches only OracleArtifactError.",
"impact": "Malformed Reviewer JSON or Planner ZIP data can escape invoke_issue_planning_chatgpt as an exception instead of producing the required content-free rejected/oracle_artifact_rejected result. This breaks the fail-closed result contract and can surface dynamic parser diagnostics.",
"required_fix": "Perform strict JSON-object parsing inside the artifact boundary and translate all expected parse and typed-constructor validation failures into content-free OracleArtifactError. Normalize expected zipfile validation exceptions, including encrypted and unsupported-compression cases, at the same boundary while allowing genuine programmer faults to remain visible.",
"required_test": "Drive the public adapter with Reviewer answers containing duplicate keys and NaN, and with encrypted or unsupported-compression Planner ZIPs. Every case must return rejected/oracle_artifact_rejected without raising, with no transient payload, raw answer, entry name, session path, or private diagnostic leakage."
},
{
"id": "P1-005",
"priority": "P1",
"path": "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py",
"line": "298-303",
"problem": "_zip_internal_root calls ZipFile.testzip before imposing any entry-count, per-entry uncompressed-size, total-uncompressed-size, or compression-ratio bound. MAX_ARTIFACT_BYTES limits only the compressed snapshot and therefore does not bound the decompression work performed by testzip.",
"impact": "A compressed artifact within the 64 MiB snapshot limit can expand to an extremely large stream and consume unbounded CPU and wall-clock time inside the transport adapter before S10 application validation can reject it.",
"required_fix": "Do not fully decompress entries merely to discover the S08 internal root, or reject archives from bounded central-directory metadata before any entry read using closed entry-count and uncompressed-size limits. Full CRC and Candidate inventory validation may remain owned by S10, but S08 must not perform unbounded decompression.",
"required_test": "Provide an archive whose declared total uncompressed size exceeds the closed limit while its compressed bytes remain below MAX_ARTIFACT_BYTES. Assert rejection before testzip or any entry read; include an entry-count overflow case and verify the public result remains rejected/oracle_artifact_rejected."
}
],
"verified_checks": [
{
"check": "exact_source_identity",
"status": "pass",
"evidence": "GitHub comparison showed the required branch identical to cdfb47171d921ff9f5e28c675de75b2ae52921da. No default-branch fallback was used."
},
{
"check": "reviewed_diff",
"status": "pass",
"evidence": "The one-commit diff ff5264689c192781d82ed05b4f02909042f3f47a..cdfb47171d921ff9f5e28c675de75b2ae52921da, all changed runtime and unit-test files, surrounding application and Candidate paths, report.md, the S08 implementation work packet, and the S08 compatibility decision were inspected."
},
{
"check": "direct_path_oracle_0_16_1",
"status": "pass_with_finding",
"evidence": "The initial path resolves through shutil.which, the final target must be a regular executable, version output must equal 0.16.1, and the identity is rechecked before prompt submission. Recovery lacks the same identity guarantee; see P1-001."
},
{
"check": "capability_preflight",
"status": "pass",
"evidence": "Version, root help, and session help are checked before submission for engine, file, slug, wait, prompt, browser-attachment, harvest, and no-recover capabilities; unsupported profiles submit no prompt."
},
{
"check": "single_submit_and_same_session_recovery",
"status": "pass_with_finding",
"evidence": "Only the initial argv contains --prompt; recovery uses the same session id with session --harvest --no-recover and never submits a second prompt. Recovery executable identity is not revalidated; see P1-001."
},
{
"check": "child_environment",
"status": "pass",
"evidence": "The child receives the closed base-key set plus locale-prefixed variables. Standard OpenAI and Azure API keys and backend selectors exercised by the tests are excluded."
},
{
"check": "artifact_snapshot_integrity",
"status": "fail",
"evidence": "Size and SHA are verified before and after a private 0600 staging copy, source mutation is checked with fstat, and static symlink cases are rejected. The pathname reopen remains vulnerable to ancestor replacement; see P1-003."
},
{
"check": "planner_zip_root",
"status": "pass_with_finding",
"evidence": "The reader requires all ZIP entries to share one safe first path component. Its use of unbounded testzip is unsafe before S10 validation; see P1-005."
},
{
"check": "reviewer_json_object",
"status": "fail",
"evidence": "OracleReviewJsonPayload enforces a strict JSON object and rejects duplicate keys, nonstandard numbers, and non-object roots, but those strict validation errors are not normalized by the adapter; see P1-004."
},
{
"check": "typed_or_temporary_legacy_result_invariants",
"status": "pass",
"evidence": "A pass result requires exactly one typed authority or one explicit legacy-only payload; both typed outputs, typed plus legacy, no-output pass, failure plus payload, and byte-count or SHA mismatch are rejected."
},
{
"check": "byte_non_leakage",
"status": "pass",
"evidence": "ZIP, JSON, and compatibility bytes are repr=False and compare=False and are omitted from PlanningInvocationResult.to_dict. Focused tests assert repr and serialization non-leakage."
},
{
"check": "production_typed_only",
"status": "pass",
"evidence": "The production adapter constructs successful results only through authoring_zip or review_json. The test spy verifies that production does not pass transient_payload to PlanningInvocationResult."
},
{
"check": "pre_s10_candidate_publication",
"status": "pass",
"evidence": "The typed Planner ZIP is exposed only through the temporary compatibility view, fails the legacy marker parser, returns rejected/planner_response_rejected, calls the Candidate publisher zero times, and leaves the output directory empty."
},
{
"check": "test_execution_evidence",
"status": "repository_recorded_only",
"evidence": "The committed report records focused S08 tests, the unchanged 66 application tests, and CLI smoke tests as passing. No GitHub Actions workflow run or combined status was present for the exact commit, and tests were not independently executed in this review."
}
],
"known_deferred": [
{
"item": "tests/integration/test_issue_planning_chatgpt_transport.py collection failure caused by its classify_transport_frame import",
"owner": "S11",
"disposition": "Explicitly excluded from findings by the review brief."
},
{
"item": "Temporary nonserialized transient_payload constructor and compatibility view",
"owner": "S10",
"disposition": "Accepted temporary compatibility boundary; its existence is not a finding."
},
{
"item": "Direct typed consumption by create, Semantic Revision, and Review; final removal of the legacy constructor lane; full authoring ZIP inventory, extraction, and Candidate connection",
"owner": "S10",
"disposition": "Deferred as designed. Findings above concern defects already active inside the S08 adapter rather than the deferred S10 migration."
}
],
"confidence": {
"level": "high",
"basis": "The exact branch and HEAD were verified through the GitHub connector, and the complete changed implementation surfaces, focused tests, surrounding consumers, and both required S08 artifacts were inspected.",
"limitations": [
"No GitHub Actions runs or commit statuses were available for the exact HEAD.",
"Repository-recorded test results were not independently rerun."
]
}
}
