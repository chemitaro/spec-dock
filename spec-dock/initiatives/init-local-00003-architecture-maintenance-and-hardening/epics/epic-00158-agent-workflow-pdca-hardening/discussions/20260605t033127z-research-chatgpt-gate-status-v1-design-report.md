---
type: research
status: completed
source: chatgpt-use
created_at: "2026-06-05T03:31:27Z"
epic_id: "epic-00158"
title: "ChatGPT gate status v1 design report"
chatgpt_project: "for codex app"
chatgpt_thread_url: "https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a223f31-5e1c-83a9-9fd2-dcf40fb20090"
visible_model: "じっくり思考 Pro"
answer_now_used: false
---

# ChatGPT Gate Status v1 Design Report

## Retrieval Note

- Prompt source: `20260605t031241z-research-chatgpt-gate-status-v1-design-task-package.md`
- `今すぐ回答` appeared during generation, but was not selected.
- The response completed normally after long-running reasoning and was retrieved from the completed ChatGPT thread.

## ChatGPT Output

Conclusion

Build one read-only runtime command:

```bash
./spec-dock/scripts/spec-dock gate status --json
./spec-dock/scripts/spec-dock gate status <target> --json
./spec-dock/scripts/spec-dock gate status --id <node-id> --json
./spec-dock/scripts/spec-dock gate status --github-issue <n> --json
```

v1 should only pass when all three spec-authoring promotion gates are machine-verifiable, fresh, and spec-reviewer passed:

```text
requirement.spec_review -> design.spec_review -> plan.spec_review
```

It should not infer pass from legacy prose or Markdown tables. Legacy/no structured evidence is a blocked result, not an error that bypasses JSON.

I inspected the public repo through GitHub. The current runtime is under `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/` with the expected `application`, `cli`, `commands`, `domain`, `infra`, and `presentation` folders; the parser and registry currently list many subcommands but no gate command. The docs already define the sequential authoring contract and the report template already contains human-readable “Spec Authoring Gate” and reviewer-gate tables. GitHub+4GitHub+4GitHub+4

Repository inspection is incomplete because I used public GitHub web/raw views rather than a local clone. Several raw Python files are emitted as single-line source by GitHub’s text view, so line-granular source inspection was limited.

## 1. Recommended v1 scope and non-scope

### v1 scope

Implement a local, read-only status command for spec-authoring gates only:

```text
Gate 1: requirement.spec_review
Gate 2: design.spec_review
Gate 3: plan.spec_review
```

A gate passes only when:

```text
reviewer_role == "spec-reviewer"
reviewer_status == "passed"
freshness == "fresh"
all required artifacts exist
all required artifact hashes match current workspace bytes
all earlier gates pass
```

The command should read:

```text
<target-scope>/requirement.md
<target-scope>/design.md
<target-scope>/plan.md
<target-scope>/report.md
<target-scope>/.meta.json
spec-dock/.agent/active.json, only when no target is provided
```

It should not write `active.json`, derived state, reports, lock files, indexes, or any migration artifacts.

The docs already say phase promotion requires `requirement -> spec-reviewer pass -> design -> spec-reviewer pass -> plan -> spec-reviewer pass`, and that missing/stale/failed/unavailable/denied/waived/provisional reviewer states block promotion. The current report template has a “Spec Authoring Gate” section with reviewer verdict values, but it is a human table rather than a reliable machine contract. GitHub+1

### v1 non-scope

Do not implement enforcement in:

```text
issue start
issue finish
active set
deps check
sync
validate
```

Do not auto-run spec-reviewer.

Do not call `gh`, GitHub APIs, OpenAI APIs, or external agents.

Do not mutate `report.md` to add evidence.

Do not parse legacy prose/table rows as pass.

Do not implement waiver approval semantics beyond reporting waived as non-pass.

Do not validate final implementation gates such as code-reviewer, qa-reviewer, final spec review, step gates, or commit gates.

Do not create a migration tool for old reports.

## 2. Command UX

### Exact CLI shape

Add a top-level command group:

```bash
./spec-dock/scripts/spec-dock gate status [<target>] --json
./spec-dock/scripts/spec-dock gate status [<target>]
./spec-dock/scripts/spec-dock gate status --id <node-id> --json
./spec-dock/scripts/spec-dock gate status --github-issue <n> --json
```

Examples:

```bash
# Default: most-specific active scope, issue > epic > initiative.
./spec-dock/scripts/spec-dock gate status --json

# Explicit node.
./spec-dock/scripts/spec-dock gate status --id iss-00123 --json
./spec-dock/scripts/spec-dock gate status epic-00120 --json

# Explicit GitHub issue number linked by .meta.json.
./spec-dock/scripts/spec-dock gate status --github-issue 123 --json
./spec-dock/scripts/spec-dock gate status 123 --json
./spec-dock/scripts/spec-dock gate status '#123' --json
./spec-dock/scripts/spec-dock gate status https://github.com/owner/repo/issues/123 --json
```

The existing runtime already has target parsing helpers for positional targets, `--id`, and `--github-issue`, including canonical GitHub issue URLs. Reuse that parsing behavior instead of adding a new target grammar. GitHub

### Target resolution behavior

Resolution order:

1. If exactly one explicit target is provided, resolve it.
2. If no target is provided, load the active manifest without migration and select the most-specific active scope:
   - issue if present, else epic if present, else initiative if present
3. If no explicit target and no active scope exists, emit JSON with:

```json
"ok": false,
"status": "blocked",
"reason": "target_missing"
```

4. If multiple selector forms are provided, treat it as CLI usage error:

```text
choose exactly one of <target>, --id, --github-issue
```

5. If a GitHub issue number maps to multiple nodes, fail closed with:

```json
"reason": "target_ambiguous"
```

6. If the target maps to no node, fail closed with:

```json
"reason": "target_not_found"
```

Important read-only detail: do not use active-manifest loading paths that migrate legacy `.work` state into `.agent`. The existing runtime has no-migration active loading in the active-state port surface, so v1 should use that path for default active resolution. GitHub+1

### Exit code policy

For a syntactically valid invocation:

```text
0 = all required gates pass
1 = any gate is non-pass, evidence is missing/malformed/stale, target cannot be resolved, or runtime evidence is unavailable
```

Argparse usage errors may retain normal parser behavior, but the command implementation should avoid raising `RuntimeError` for expected status failures in `--json` mode. Status failures should return a JSON payload and exit 1.

This follows the existing fail-closed precedent from `delegated-authoring diff-guard`, which has command args, application requests, domain result objects with `ok/status/reason/details`, and exit code 0 or 1. GitHub+2GitHub+2

### Text vs JSON output behavior

`--json` is the stable v1 contract.

JSON mode:

```text
stdout: exactly one JSON object, pretty-printed, trailing newline
stderr: empty for normal blocked/pass results
exit: 0 or 1
```

Text mode is intentionally non-stable and human-oriented:

```text
spec-dock: ok (gate status)
target=iss-00123
status=pass
gate=requirement.spec_review status=pass freshness=fresh
gate=design.spec_review status=pass freshness=fresh
gate=plan.spec_review status=pass freshness=fresh
```

Blocked text mode:

```text
spec-dock: blocked (gate status)
target=iss-00123
status=blocked
reason=gate_blocked
gate=requirement.spec_review status=missing reason=missing_structured_evidence
```

Text mode must use the same exit code as JSON mode.

## 3. Domain model

Create:

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/gate_status.py
```

### Enums

```python
from enum import Enum

class GateId(str, Enum):
    REQUIREMENT_SPEC_REVIEW = "requirement.spec_review"
    DESIGN_SPEC_REVIEW = "design.spec_review"
    PLAN_SPEC_REVIEW = "plan.spec_review"

class AuthoringPhase(str, Enum):
    REQUIREMENT = "requirement"
    DESIGN = "design"
    PLAN = "plan"

class ReviewerStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    UNAVAILABLE = "unavailable"
    DENIED = "denied"
    WAIVED = "waived"
    PROVISIONAL = "provisional"
    MISSING = "missing"
    MALFORMED = "malformed"
    UNKNOWN = "unknown"

class FreshnessStatus(str, Enum):
    FRESH = "fresh"
    STALE = "stale"
    MISSING = "missing"
    UNKNOWN = "unknown"

class GateStatus(str, Enum):
    PASS = "pass"
    MISSING = "missing"
    STALE = "stale"
    FAILED = "failed"
    UNAVAILABLE = "unavailable"
    DENIED = "denied"
    WAIVED = "waived"
    PROVISIONAL = "provisional"
    MALFORMED = "malformed"
    BLOCKED = "blocked"
```

### Gate IDs and required artifacts

```python
REQUIRED_ARTIFACTS_BY_GATE = {
    GateId.REQUIREMENT_SPEC_REVIEW: ("requirement.md",),
    GateId.DESIGN_SPEC_REVIEW: ("requirement.md", "design.md"),
    GateId.PLAN_SPEC_REVIEW: ("requirement.md", "design.md", "plan.md"),
}
```

Do not include `report.md` in freshness hashes for v1. `report.md` is the evidence source. Including it would make a freshly inserted evidence block stale immediately unless the reviewer had reviewed the report after the evidence block was written.

### Dataclasses

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

@dataclass(frozen=True)
class ArtifactHash:
    path: str
    exists: bool
    sha256: str | None
    expected_sha256: str | None
    freshness: FreshnessStatus
    git_status: str = "unknown"

@dataclass(frozen=True)
class ReviewerEvidence:
    reviewer_role: str | None
    reviewer_status: ReviewerStatus
    reviewed_at: str | None
    evidence_id: str | None
    source: str | None
    risk_acceptance: dict[str, Any] | None = None

@dataclass(frozen=True)
class GateBlocker:
    code: str
    message: str
    gate_id: GateId | None = None
    path: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class GateWarning:
    code: str
    message: str
    gate_id: GateId | None = None
    path: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class GateEvaluation:
    gate_id: GateId
    phase: AuthoringPhase
    required: bool
    ok: bool
    status: GateStatus
    reason: str
    reviewer: ReviewerEvidence
    artifacts: tuple[ArtifactHash, ...]
    blockers: tuple[GateBlocker, ...]
    warnings: tuple[GateWarning, ...]

@dataclass(frozen=True)
class GateStatusDomainResult:
    ok: bool
    status: str
    reason: str
    target_id: str | None
    target_kind: str | None
    target_path: str | None
    gates: tuple[GateEvaluation, ...]
    blockers: tuple[GateBlocker, ...]
    warnings: tuple[GateWarning, ...]
    details: tuple[str, ...]
```

### Pass / non-pass truth table

| Evidence condition | Freshness | Gate status | ok | Blocker code |
|---|---|---|---:|---|
| spec-reviewer + passed + all required hashes match + upstream gates pass | fresh | pass | true | none |
| No structured evidence record for gate | missing | missing | false | missing_structured_evidence |
| Report has only legacy prose/table | missing | missing | false | legacy_no_structured_evidence |
| Evidence JSON invalid | unknown | malformed | false | malformed_evidence |
| Duplicate evidence block or duplicate gate ID | unknown | malformed | false | ambiguous_evidence |
| Reviewer role is not spec-reviewer | any | malformed | false | wrong_reviewer_role |
| Reviewer status is failed | any | failed | false | reviewer_failed |
| Reviewer status is unavailable | any | unavailable | false | reviewer_unavailable |
| Reviewer status is denied | any | denied | false | reviewer_denied |
| Reviewer status is waived | any | waived | false | reviewer_waived_not_pass |
| Reviewer status is provisional | any | provisional | false | provisional_not_reviewer_pass |
| Reviewer status is passed, but any required artifact is missing | stale | stale | false | required_artifact_missing |
| Reviewer status is passed, but any required artifact hash differs | stale | stale | false | artifact_hash_mismatch |
| Reviewer status is passed, but expected hash is absent | unknown | stale | false | missing_target_hash |
| Downstream gate has pass evidence, but upstream gate is non-pass | gate’s own freshness | blocked | false | upstream_gate_not_passed |

## 4. Evidence input strategy

### v1 should require a new structured block

Do not accept current report prose/table rows as pass evidence. The report template already has a human “Spec Authoring Gate” table and reviewer-state tables; those are useful for humans but ambiguous for a runtime gate. GitHub

Use a strict fenced JSON block in `report.md`:

```markdown
```spec-dock-gates-v1
{
  "schema_version": 1,
  "scope_id": "iss-00123",
  "gates": [
    {
      "gate_id": "requirement.spec_review",
      "phase": "requirement",
      "reviewer_role": "spec-reviewer",
      "reviewer_status": "passed",
      "reviewed_at": "2026-06-05T12:00:00Z",
      "evidence_id": "review-req-20260605-120000",
      "source": "report.md#spec-authoring-gate",
      "target_hashes": {
        "requirement.md": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
      }
    }
  ]
}
```
```

Parsing rules:

- scan `report.md` for fenced blocks whose opening line is exactly ```` ```spec-dock-gates-v1 ````;
- require exactly one block;
- parse as JSON with stdlib `json`;
- require `schema_version == 1`;
- require `scope_id == target node id`;
- require all `gate_id` values to be known;
- require no duplicate `gate_id`;
- require no unknown `reviewer_status`;
- require `reviewer_role == "spec-reviewer"` for pass eligibility.

This keeps runtime dependency-free. The runtime script already states a minimal-dependency design goal, so JSON is preferable to YAML for v1. GitHub

### What v1 can parse safely from `report.md`

Safe:

- the exact fenced JSON block;
- JSON scalar fields;
- JSON object `target_hashes`;
- optional `risk_acceptance` object.

Unsafe for pass:

- prose saying “passed”;
- Markdown tables;
- raw reviewer transcript pasted into report;
- bilingual table labels;
- unchecked `review_status: pass` outside the structured block.

### Legacy/no-evidence classification

If no structured block exists:

```json
{
  "ok": false,
  "status": "blocked",
  "reason": "legacy_no_structured_evidence"
}
```

If the report contains the human “Spec Authoring Gate” heading/table but no structured block, add warning:

```json
{
  "code": "legacy_table_present",
  "message": "Human-readable Spec Authoring Gate table is present, but v1 requires spec-dock-gates-v1 structured evidence."
}
```

No legacy form may produce pass in v1.

## 5. Artifact freshness

### Hash strategy

Use SHA-256 over raw bytes:

```text
sha256:<64 lowercase hex characters>
```

No newline normalization. No Markdown normalization. No YAML parsing. No frontmatter extraction.

Rules:

- regular file required;
- missing file => blocked;
- directory => blocked;
- symlink artifact => blocked;
- unreadable file => blocked;
- non-UTF-8 `report.md` => blocked for evidence parsing.

Canonical doc hashes should use scope-relative names in evidence:

```json
"target_hashes": {
  "requirement.md": "sha256:...",
  "design.md": "sha256:...",
  "plan.md": "sha256:..."
}
```

The output should expand them to repo-relative paths.

### Required hashes by gate

```text
requirement.spec_review:
  requirement.md

design.spec_review:
  requirement.md
  design.md

plan.spec_review:
  requirement.md
  design.md
  plan.md
```

### Upstream artifact changes

Upstream changes stale downstream gates.

Examples:

```text
requirement.md changes:
  requirement.spec_review => stale
  design.spec_review      => stale
  plan.spec_review        => stale

design.md changes:
  requirement.spec_review => unaffected
  design.spec_review      => stale
  plan.spec_review        => stale

plan.md changes:
  requirement.spec_review => unaffected
  design.spec_review      => unaffected
  plan.spec_review        => stale
```

### Uncommitted changes

Content hash is the authoritative freshness check.

Git status should be diagnostic, not the primary freshness mechanism:

- if a required artifact has uncommitted changes but its current bytes match the recorded hash, gate may still pass;
- if uncommitted changes alter bytes after reviewer evidence was recorded, the hash mismatch makes the gate stale;
- if git is unavailable, still compute hashes; emit warning `git_status_unavailable`;
- if `report.md` itself is uncommitted, emit warning `report_uncommitted`, but do not block solely for that.

Do not require a clean entire working tree in v1. That would make the command harder to dogfood and unrelated implementation dirtiness should not invalidate authoring-gate freshness.

## 6. Application / command / presentation layering

### Proposed files

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/gate_status.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/gate_status.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/gate.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/gate_status_json.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/gate_status_text.py
```

Optional infra helper:

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/file_hash.py
```

Or keep hashing private in `application/gate_status.py` for v1.

### Registry/parser integration

In `cli/parser.py`, add:

```python
p_gate = sub.add_parser("gate", help="Inspect workflow gates")
gate_sub = p_gate.add_subparsers(dest="gate_cmd", required=True)
_bind_leaf(gate_sub.add_parser("status", help="Show spec-authoring gate status"), registry, "gate_status")
```

In `cli/registry.py`, import and register:

```python
from ..commands import gate as gate_commands
...
items.update(gate_commands.command_specs())
```

The current parser and registry already follow this command-spec pattern, so v1 should fit the existing shape. GitHub+1

### Request/result dataclasses

Add to `application/contracts.py` or keep in `application/gate_status.py`. Recommended: add to `application/contracts.py` because this is a core runtime use case, unlike delegated-authoring’s special direct-call style.

```python
@dataclass(frozen=True)
class GateStatusRequest:
    target: TargetRef | None
    resolved_from: str
    json_output: bool = False

@dataclass(frozen=True)
class GateStatusResult:
    ok: bool
    status: str
    reason: str
    target: GateStatusTarget | None
    required_gate_ids: list[str]
    gates: list[GateEvaluation]
    blockers: list[GateBlocker]
    warnings: list[GateWarning]
    details: list[str]
```

Target view:

```python
@dataclass(frozen=True)
class GateStatusTarget:
    kind: str
    id: str
    title: str
    path: str
    resolved_from: str
    github_issue_number: int | None = None
```

### UseCases integration

Add:

```python
gate_status: Callable[[GateStatusRequest], GateStatusResult] = lambda _req: ...
```

Wire it in `cli/bootstrap.py`:

```python
from ..application.gate_status import gate_status as application_gate_status
...
gate_status=lambda req: application_gate_status(req, ports)
```

Reason: gate status needs existing ports and should avoid direct filesystem ad hoc behavior where possible. `delegated-authoring diff-guard` is a precedent for fail-closed classification, but gate status is a first-class runtime read model and should be integrated into `UseCases`.

## 7. JSON schema v1 and example payloads

Output schema v1, condensed

```json
{
  "schema_version": 1,
  "command": "gate status",
  "ok": "boolean",
  "status": "pass | blocked",
  "reason": "string",
  "target": {
    "kind": "initiative | epic | issue",
    "id": "string",
    "title": "string",
    "path": "repo-relative path",
    "resolved_from": "active | positional | --id | --github-issue",
    "github_issue_number": "integer|null"
  },
  "required_gate_ids": [
    "requirement.spec_review",
    "design.spec_review",
    "plan.spec_review"
  ],
  "gates": [
    {
      "gate_id": "requirement.spec_review | design.spec_review | plan.spec_review",
      "phase": "requirement | design | plan",
      "required": true,
      "ok": "boolean",
      "status": "pass | missing | stale | failed | unavailable | denied | waived | provisional | malformed | blocked",
      "reason": "string",
      "reviewer": {
        "role": "spec-reviewer|null",
        "status": "passed | failed | unavailable | denied | waived | provisional | missing | malformed | unknown",
        "freshness": "fresh | stale | missing | unknown",
        "reviewed_at": "string|null",
        "evidence_id": "string|null",
        "source": "string|null",
        "risk_acceptance": "object|null"
      },
      "artifacts": [
        {
          "path": "repo-relative path",
          "exists": "boolean",
          "sha256": "sha256:<hex>|null",
          "expected_sha256": "sha256:<hex>|null",
          "freshness": "fresh | stale | missing | unknown",
          "git_status": "clean | modified | staged | untracked | unknown"
        }
      ],
      "blockers": [
        {
          "code": "string",
          "message": "string",
          "gate_id": "string|null",
          "path": "string|null",
          "details": {}
        }
      ],
      "warnings": []
    }
  ],
  "blockers": [],
  "warnings": [],
  "details": []
}
```

### Example: all pass

The ChatGPT output included a full all-pass JSON example with all three gates:

- `requirement.spec_review`
- `design.spec_review`
- `plan.spec_review`

Each gate had:

- `ok: true`
- `status: "pass"`
- `reason: "fresh_reviewer_pass"`
- `reviewer.role: "spec-reviewer"`
- `reviewer.status: "passed"`
- `reviewer.freshness: "fresh"`
- matching `sha256` / `expected_sha256` for required artifacts
- no blockers or warnings

### Example: requirement missing review

The missing-review example had:

- top-level `ok: false`
- top-level `status: "blocked"`
- top-level `reason: "gate_blocked"`
- gate `requirement.spec_review`
- gate `status: "missing"`
- gate `reason: "missing_structured_evidence"`
- reviewer fields all missing/null
- artifact current hash present but expected hash null
- blocker `missing_structured_evidence`

### Example: design stale review

The stale-review example had:

- top-level `ok: false`
- gate `design.spec_review`
- gate `status: "stale"`
- gate `reason: "artifact_hash_mismatch"`
- reviewer status `passed` but freshness `stale`
- requirement hash mismatch causing design review to be stale
- warning `artifact_uncommitted` when Git status shows modified

### Example: waived reviewer result

The waived example had:

- top-level `ok: false`
- gate `requirement.spec_review`
- gate `status: "waived"`
- gate `reason: "reviewer_waived_not_pass"`
- reviewer status `waived`
- optional `risk_acceptance`
- blocker `reviewer_waived_not_pass`
- detail that fresh spec-reviewer passed evidence is still required for automatic promotion

### Example: legacy no evidence

The legacy example had:

- top-level `ok: false`
- top-level `reason: "legacy_no_structured_evidence"`
- gate `requirement.spec_review`
- gate `status: "missing"`
- blocker `legacy_no_structured_evidence`
- warning `legacy_table_present` if a human-readable table exists
- no legacy form producing pass

## 8. Tests

The repo already has runtime test directories for CLI, domain, and presentation, which fit this change. GitHub+2GitHub+2

### Domain tests

Add:

```text
tests/domain_runtime/test_gate_status.py
```

Test cases:

```text
test_all_pass_truth_table
test_missing_evidence_blocks_gate
test_legacy_table_never_passes
test_invalid_json_block_is_malformed
test_multiple_evidence_blocks_are_ambiguous
test_duplicate_gate_ids_are_malformed
test_wrong_scope_id_blocks
test_unknown_gate_id_blocks
test_unknown_reviewer_status_blocks
test_wrong_reviewer_role_blocks
test_failed_unavailable_denied_waived_provisional_are_non_pass
test_pass_with_missing_hash_is_unknown_and_non_pass
test_pass_with_hash_mismatch_is_stale
test_design_stale_when_requirement_hash_changes
test_plan_stale_when_requirement_or_design_hash_changes
test_downstream_gate_blocked_by_upstream_non_pass
```

### Application tests

Add:

```text
tests/domain_runtime/test_gate_status_application.py
```

or keep in `tests/domain_runtime/test_gate_status.py` if project convention favors fewer files.

Test cases:

```text
test_resolves_explicit_node_id
test_resolves_github_issue_number_to_node
test_resolves_active_issue_without_migration
test_no_active_target_returns_json_status_not_exception
test_missing_report_returns_blocked_json
test_missing_requirement_file_blocks
test_symlink_canonical_artifact_blocks
test_git_unavailable_does_not_prevent_hash_evaluation
test_uncommitted_matching_hash_warns_not_blocks
test_uncommitted_hash_mismatch_blocks_stale
```

### CLI runtime fixtures

Add:

```text
tests/cli_runtime/test_gate_status.py
```

Fixture builder:

```text
tmp repo/
  spec-dock/
    .agent/active.json
    initiatives/init-00100-alpha/.meta.json
    initiatives/init-00100-alpha/requirement.md
    initiatives/init-00100-alpha/design.md
    initiatives/init-00100-alpha/plan.md
    initiatives/init-00100-alpha/report.md
    initiatives/init-00100-alpha/epics/epic-00110-runtime/.meta.json
    initiatives/init-00100-alpha/epics/epic-00110-runtime/issues/iss-00123-gate-status/.meta.json
    initiatives/.../issues/iss-00123-gate-status/requirement.md
    initiatives/.../issues/iss-00123-gate-status/design.md
    initiatives/.../issues/iss-00123-gate-status/plan.md
    initiatives/.../issues/iss-00123-gate-status/report.md
```

CLI test cases:

```text
test_gate_status_json_all_pass_exit_0
test_gate_status_json_missing_review_exit_1
test_gate_status_json_design_stale_exit_1
test_gate_status_json_waived_exit_1
test_gate_status_json_legacy_no_evidence_exit_1
test_gate_status_defaults_to_active_issue
test_gate_status_explicit_id
test_gate_status_positional_github_number
test_gate_status_ambiguous_target_exit_1_json
test_gate_status_json_stdout_only_on_blocked_result
test_gate_status_text_output_human_summary
```

### Presentation JSON snapshots

Add:

```text
tests/presentation_runtime/test_gate_status_json.py
```

Snapshot-like assertions:

```text
test_render_all_pass_schema_v1
test_render_requirement_missing_schema_v1
test_render_design_stale_schema_v1
test_render_waived_schema_v1
test_render_legacy_no_evidence_schema_v1
```

Assertions should verify:

- `schema_version == 1`
- `command == "gate status"`
- stable top-level key order if renderer uses dict insertion order
- `ok/status/reason` are present
- all blockers include `code/message/gate_id/path/details`
- no Python repr strings
- no `Path` objects leak into JSON
- no stderr warnings in `--json` normal blocked mode

### No-write / read-only verification

Add runtime tests that record before/after:

- sorted file list
- file contents hash for every file under `spec-dock/`
- mtimes for `active.json`, `report.md`, canonical docs
- `git status --porcelain`

Then run:

```bash
./spec-dock/scripts/spec-dock gate status --json
```

Assert:

- no files created
- no files modified
- no active manifest migration
- no `.agent/index.json` or `tree.json` written
- no `report.md` mutation
- no chmod / permission changes
- git status unchanged

Also monkeypatch or fake ports so accidental calls fail:

```text
json_store.write_json => AssertionError
active_state_store.write_active_manifest => AssertionError
artifact_writer.write => AssertionError
template_scaffolder.write_text => AssertionError
node_repo.write_meta => AssertionError
```

## 9. Acceptance criteria for the issue

- `gate status` is registered under the runtime parser/registry.
- These commands work:

```bash
./spec-dock/scripts/spec-dock gate status --json
./spec-dock/scripts/spec-dock gate status --id iss-00123 --json
./spec-dock/scripts/spec-dock gate status iss-00123 --json
./spec-dock/scripts/spec-dock gate status --github-issue 123 --json
```

- `--json` emits exactly one JSON object to stdout for both pass and blocked states.
- Exit code is 0 only when all three required gates pass.
- Exit code is 1 for missing, stale, failed, unavailable, denied, waived, provisional, malformed, ambiguous, or legacy-only evidence.
- v1 never classifies legacy prose/table evidence as pass.
- v1 requires a strict `spec-dock-gates-v1` fenced JSON block in `report.md`.
- v1 validates `scope_id`, `gate_id`, `reviewer_role`, `reviewer_status`, duplicate gate IDs, and required `target_hashes`.
- v1 computes SHA-256 over raw bytes of canonical artifacts and detects stale reviewer evidence through hash mismatch.
- v1 treats upstream artifact changes as stale for downstream gates.
- v1 does not include `report.md` in required freshness hashes.
- v1 reports uncommitted required artifacts as warnings when Git status is available.
- v1 performs no writes, no active migration, no sync artifact generation, no report updates, no chmod changes, no GitHub calls, and no `gh` calls.
- Unit, CLI runtime, presentation JSON, and read-only verification tests are added under the existing test directories.
- The implementation uses stdlib only.
- The JSON schema is documented either in a new runtime reference doc or in a concise section near the workflow/spec-authoring docs.

## 10. Risks and rollback

### Risks

The main risk is false negatives: old reports and human-only evidence will block until structured evidence is added. This is acceptable for v1 because the explicit goal is fail-closed hardening.

Hashing raw bytes may mark cosmetic edits stale. This is also acceptable because “fresh reviewer pass” should attach to exact reviewed content.

Multiple structured evidence blocks may feel inconvenient. Blocking on ambiguity is safer than choosing the wrong block.

Users may expect a waiver to pass. v1 must not do that; docs already distinguish waived/risk acceptance from reviewer pass.

### Rollback

Rollback is simple because v1 is read-only:

- remove parser binding for `gate status`;
- remove registry import/update;
- remove `UseCases` field and bootstrap wiring;
- remove new application/domain/presentation files;
- remove tests.

No user workspace migration is needed. No generated state format is modified.

## 11. Follow-up issues intentionally left open

1. Add a writer/helper command to append or refresh `spec-dock-gates-v1` evidence after a reviewer pass.
2. Update all report templates for initiative/epic/issue with a documented structured evidence example.
3. Add enforcement hooks to `issue start`, `issue finish`, or downstream handoff after the read-only command is dogfooded.
4. Add a migration assistant that reads legacy human tables and emits draft structured evidence as non-authoritative suggestions.
5. Add report-schema validation for Evidence Adoption Ledger and Delegated Draft Evidence.
6. Extend `gate status` to final implementation gates: code-reviewer, qa-reviewer, final spec review, docs impact, commit/no-op gates.
7. Add CI-friendly compact JSON mode.
8. Add JSON Schema file under docs/reference and use it in tests.
9. Record reviewer invocation metadata if SpecDock later owns reviewer execution.
10. Support explicit waiver policy validation, while still keeping waiver non-pass for automatic promotion.
