---
artifact_type: s07-chatgpt-execution-work-packet
created_at: 2026-07-28T10:05:24Z
created_by_role: chatgpt-pro
intended_issue: iss-00334
intended_step: S07
adoption_status: execution-input
review_required: false
source_repository: chemitaro/spec-dock
source_branch: iss-00334-implement-chatgpt-issue-planning-workflow
source_head: 3bc0b8bada9b07ebc85f8cf29e15e361bd204f12
initial_session: iss00334-s07-implementa-brief
model_requested: Pro
model_resolved: Pro
model_selection_verified: true
disposition: STOP_AT_HUMAN_GATE
---

# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a687a72-f0ec-83e8-b6cf-59c018dc0cdc

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

Use the attached prompt as the complete task brief. Inspect the required GitHub branch and return only the bounded S07 execution packet.

## Answer

# S07 Execution Packet — JIT Dogfood and Delivery

## 1. Disposition

**Disposition: `STOP_AT_HUMAN_GATE`**

S07 cannot safely begin its live planning run yet.

The repository branch is available at the required remote HEAD, and read-only preflight/help inspection is safe. Live ChatGPT/GitHub use, pushes on the current Issue branch, and Delivery PR creation are authorized in principle. However, the six S07 run bindings are not complete: the Human has not explicitly fixed `iss-00334` as the live dogfood target, the exact dedicated worktree path, the planning mode, the external evidence destination, or the exact repository mutation scope. Separately, no exact `PlanningHumanDecisionV1` bound to a fresh reviewed identity and exact Review bytes exists. The supplied task expressly withholds authorization to infer canonical Requirement/Design/Plan replacement from implementation or PR authority. 

Proceed now only through the read-only preflight/help block in §6. Do not run `planning create`, `review planning`, `planning revise`, or `planning apply` until the initial S07 live-run authorization record in §4.2 is supplied. After that record is supplied, run create and fresh review, then stop again at the exact Human decision gate before apply.

---

## 2. Verified repository, branch, HEAD, Issue, and PR evidence

| Item                                              | Verified value                                                                 |
| ------------------------------------------------- | ------------------------------------------------------------------------------ |
| Repository                                        | `chemitaro/spec-dock`                                                          |
| Default branch                                    | `main`                                                                         |
| Required branch                                   | `iss-00334-implement-chatgpt-issue-planning-workflow`                          |
| Required pushed HEAD                              | `3bc0b8bada9b07ebc85f8cf29e15e361bd204f12`                                     |
| Branch versus required HEAD                       | `identical`; ahead `0`, behind `0`                                             |
| Branch versus `main`                              | ahead `55`, behind `0`                                                         |
| GitHub Issue                                      | `#334 — Implement ChatGPT Issue Planning Workflow`                             |
| GitHub Issue state                                | `open`                                                                         |
| Existing PR for the branch                        | None found                                                                     |
| Combined legacy status contexts at inspected HEAD | None returned; this is **not** CI-pass evidence                                |
| Current S07 state in canonical report             | S06 closed; S07, final QA, issue-wide code review, and PR delivery remain open |

The GitHub connector verifies remote repository state. It does not prove the executor’s local worktree path, local cleanliness, local-to-remote parity after a new fetch, installed tool versions, or current test results. Those must be re-proved immediately before every identity-sensitive operation.

The canonical S07 contract requires explicit authorization for target, worktree/branch, mode, live use, mutation scope, and evidence destination before live dogfood. It then requires create, fresh defect-only review, minimum P0/P1-only revision when necessary, exact Human decision, `ready` apply with parity, metrics, issue-wide review, and Delivery PR preparation.

---

## 3. Eligibility of `iss-00334` as the live dogfood target

### 3.1 Judgment

**`iss-00334` is conditionally eligible only through a `git-bound` live adoption run.**

It is a real, open Issue with an existing dedicated branch and a completed S01–S06 implementation. The installed public command boundary exists and the hermetic S06 suite already proved both archive and git-bound chains through `ready`, including FAIL → Semantic revision → fresh PASS.

### 3.2 Why archive adoption is not safe for this target now

A new archive Candidate for `iss-00334` would be generated after the Issue’s approved canonical plan has already driven six implementation milestones. Applying that Candidate would replace the three canonical planning documents after implementation, creating a circular and potentially stale self-replanning operation.

Archive approval is also more destructive than required: archive apply replaces `requirement.md`, `design.md`, and `plan.md`; git-bound apply reviews the exact existing canonical files at a bound HEAD and performs decision-only adoption without replacing those files.

Therefore:

* `planning create` may still be run to prove real Candidate creation, but its Candidate remains immutable external evidence and is **not** the adoption target.
* The fresh review and exact Human decision must use `--mode git-bound`.
* The git-bound apply must leave all three canonical documents byte-identical.
* Archive apply is prohibited in this packet unless a later Human instruction expressly supersedes the current no-rewrite boundary and approves one exact Candidate identity. No such authority currently exists.

### 3.3 Smallest product-contract-consistent live sequence

```text
real planning create
  → preserve Candidate externally as evidence-only
  → fresh git-bound defect-only review of the current canonical three documents
  → no revision for P2/P3-only observations
  → exact Human decision bound to the git-bound identity and exact Review bytes
  → git-bound planning apply
  → decision-only planning commit/push
  → ready/adoption_published and local/remote parity
```

This exact topology is not an invented workaround: S06’s git-bound E2E contract was `planning create → git-bound Review PASS → exact Human approval → planning apply → ready`, with canonical documents unchanged.

### 3.4 Conditional blocker

If the fresh git-bound review contains a real P0 or P1:

1. Do not use that Review for approval.
2. Do not run `planning revise`; the public revision flow is Candidate-bound, while the reviewed target in this lane is the canonical git-bound state.
3. Do not edit the canonical documents under this packet.
4. Stop and classify this target/run as unsuitable under the present mutation boundary.

A different target must not be invented or created. Selection of another already-existing eligible Issue would require a new explicit Human target decision outside this packet.

---

## 4. Authorization matrix

### 4.1 Current authority

| Operation                                                                | Current status                                                          | Boundary                                                             |
| ------------------------------------------------------------------------ | ----------------------------------------------------------------------- | -------------------------------------------------------------------- |
| Inspect repository, Issue, branch, canonical docs, implementation, tests | Authorized and completed read-only                                      | No repository or GitHub mutation                                     |
| Run local Git/read-only preflight                                        | Authorized                                                              | No checkout, reset, commit, push, or file writes                     |
| Run `spec-dock-chatgpt` help commands                                    | Authorized                                                              | Parser/help only; backend call count must remain zero                |
| Live ChatGPT/GitHub transport                                            | Authorized in principle                                                 | Exact target, mode, worktree, and evidence destination still missing |
| `planning create`                                                        | Externally mutating only, but **not runnable yet**                      | Wait for §4.2 authorization; Candidate stays outside repository      |
| Fresh `review planning`                                                  | Externally mutating only, but **not runnable yet**                      | Wait for §4.2 authorization; use `git-bound`                         |
| `planning revise`                                                        | Not part of the selected git-bound lane                                 | Never revise for P2/P3; P0/P1 in git-bound causes stop               |
| Produce exact Human approval brief                                       | Authorized after fresh Review                                           | Read-only extraction from immutable evidence                         |
| Generate or infer Human decision JSON                                    | **Prohibited**                                                          | Human must supply exact bytes                                        |
| `planning apply`                                                         | **Not authorized now**                                                  | Requires exact approved decision bound to exact Review bytes         |
| Commit/push current Issue branch                                         | Authorized only within fixed post-approval scope                        | No force, amend, rebase, or unrelated files                          |
| Create/reuse one Delivery PR                                             | Authorized after final local gates                                      | Base `main`, head current Issue branch                               |
| Post deterministic `@codex review` trigger                               | Authorized only through repository observation script after PR creation | No manual trigger text or arbitrary GitHub API                       |
| Repair PR P0/P1 or required CI failures                                  | Conditional                                                             | Fresh triage/consultation and bounded repair unit required           |
| Merge, enable auto-merge, delete branch                                  | Prohibited; Human-only                                                  |                                                                      |
| Close Issue or run `issue finish`                                        | Prohibited; Human-only                                                  |                                                                      |

Candidate and Review are evidence only; neither authorizes adoption, implementation continuation, PR readiness, merge, or Issue finish. Only exact PASS Review evidence plus exact Human approval and a `ready/adoption_published` apply completes planning adoption.

### 4.2 Exact initial Human authorization record required

The Human must supply all fields below as one explicit record. No field may be inferred.

```yaml
authorization_type: S07LiveRunAuthorizationV1
repository: chemitaro/spec-dock
target_issue: iss-00334
worktree_absolute_path: "<dedicated absolute worktree path>"
branch: iss-00334-implement-chatgpt-issue-planning-workflow
expected_start_head: 3bc0b8bada9b07ebc85f8cf29e15e361bd204f12

planning_mode: git-bound
live_chatgpt_and_github_use: true
external_evidence_root_absolute_path: "<existing or explicitly creatable external directory>"

repository_mutation_scope:
  before_exact_planning_decision: []
  git_bound_apply:
    canonical_requirement_design_plan_must_remain_byte_identical: true
    deterministic_human_decision_artifact: allowed
    apply_owned_managed_sync_outputs: allowed_only_if_generated_and_diff_reviewed
    planning_commit_on_current_branch: allowed
    fast_forward_push_to_current_branch: allowed
  post_apply_s07:
    current_issue_report_update: allowed
    bounded_p0_p1_repairs_and_corresponding_tests: allowed_only_after_fresh_defect_evidence

delivery_pr:
  base: main
  head: iss-00334-implement-chatgpt-issue-planning-workflow
  create_or_reuse_exactly_one: true
  create_as_ready_only_after_local_final_gates: true
  deterministic_codex_review_trigger_via_repo_script: true

merge: false
auto_merge: false
branch_delete: false
issue_close: false
issue_finish: false
```

Approval of this record authorizes the live run through Candidate creation and fresh Review. It does **not** supply the later `PlanningHumanDecisionV1`.

---

## 5. External evidence destination and filenames

### 5.1 Required Human choice

Set:

```bash
S07_EVIDENCE_ROOT="<exact Human-approved absolute directory>"
```

The directory must be:

* outside the repository;
* not an ancestor or descendant of the repository;
* free of symlink components;
* dedicated to this run;
* writable only by the operator where the platform permits;
* free of secrets, credentials, browser profiles, raw host configuration, and private unrelated data.

The runtime requires existing external output directories and rejects repository-contained, unsafe, or symlinked paths.

### 5.2 Exact layout

```text
<S07_EVIDENCE_ROOT>/
├── candidates/
│   └── <candidate_identity.logical_filename>
├── reviews/
│   └── review-<UTC>-<reviewed_identity_sha256>/
│       ├── planning-review-result.json
│       └── planning-review-summary.md
├── operations/
├── pr-observation/
│   └── result.json
├── canonical-preapply-sha256.txt
├── canonical-postapply-sha256.txt
├── planning-create-command-result.json
├── planning-review-command-result.json
├── planning-human-decision.json
├── planning-apply-command-result.json
└── pr-observation-result.json
```

Runtime-resolved names must be consumed from command output; do not glob, scan for “latest,” or rename evidence:

* Candidate ZIP: exact `output.candidate_identity.logical_filename`.
* Review result: exact `output.review_result_file`.
* Review summary: exact `output.review_summary_file`.
* Review directory format: `review-<UTC timestamp>-<reviewed_identity_sha256>`.
* Human decision input: exactly `<S07_EVIDENCE_ROOT>/planning-human-decision.json`.
* Apply operation output directory: exactly `<S07_EVIDENCE_ROOT>/operations`.

Review publication writes exactly `planning-review-result.json` and `planning-review-summary.md` beneath its content-bound review directory.

Do not copy the Candidate, Review result, Review summary, command envelopes, operation state, or raw PR-observation JSON into the repository. Record only sanitized identities, hashes, results, metrics, and concise failure classes in `report.md`.

---

## 6. Exact execution sequence

## 6.A Read-only preflight and help — safe now

```bash
set -euo pipefail

REPOSITORY='chemitaro/spec-dock'
ISSUE_ID='iss-00334'
GITHUB_ISSUE='334'
BRANCH='iss-00334-implement-chatgpt-issue-planning-workflow'
BASE='main'
REQUIRED_HEAD='3bc0b8bada9b07ebc85f8cf29e15e361bd204f12'
WORKTREE='<HUMAN_APPROVED_ABSOLUTE_WORKTREE>'

cd "$WORKTREE"
REPO_ROOT="$(git rev-parse --show-toplevel)"
test "$(cd "$REPO_ROOT" && pwd -P)" = "$(cd "$WORKTREE" && pwd -P)"
test "$(git branch --show-current)" = "$BRANCH"

git fetch --prune origin "$BRANCH" "$BASE"

test "$(git rev-parse HEAD)" = "$REQUIRED_HEAD"
test "$(git rev-parse "refs/remotes/origin/$BRANCH")" = "$REQUIRED_HEAD"
test "$(git rev-list --count "HEAD..refs/remotes/origin/$BRANCH")" = '0'
test "$(git rev-list --count "refs/remotes/origin/$BRANCH..HEAD")" = '0'
test "$(git rev-list --count "HEAD..refs/remotes/origin/$BASE")" = '0'

test "$(git config --get "branch.$BRANCH.remote")" = 'origin'
test "$(git config --get "branch.$BRANCH.merge")" = "refs/heads/$BRANCH"
test -z "$(git status --porcelain=v1 --untracked-files=all)"

test -x ./spec-dock/scripts/spec-dock-chatgpt
test -f ./spec-dock/scripts/spec_dock_runtime/chatgpt_app.py

./spec-dock/scripts/spec-dock-chatgpt --help
./spec-dock/scripts/spec-dock-chatgpt planning create --help
./spec-dock/scripts/spec-dock-chatgpt planning revise --help
./spec-dock/scripts/spec-dock-chatgpt review planning --help
./spec-dock/scripts/spec-dock-chatgpt planning apply --help

gh issue view "$GITHUB_ISSUE" \
  --repo "$REPOSITORY" \
  --json number,state,title,url

gh pr list \
  --repo "$REPOSITORY" \
  --head "$BRANCH" \
  --state all \
  --json number,url,state,isDraft,baseRefName,headRefName,headRefOid
```

Expected:

* exact branch and required HEAD;
* clean worktree and index;
* local/remote branch parity;
* branch not behind `main`;
* Issue #334 open;
* all five help invocations exit `0`;
* no backend/network planning invocation caused by help;
* no existing PR, or one existing open PR that must be reused rather than duplicated.

Stop immediately on any mismatch.

The installed parser exposes only `planning create`, `planning revise`, `review planning`, and `planning apply`; its mode options are closed and mutually exclusive.

## 6.B Initialize the Human-approved external evidence root

Run only after §4.2 is approved.

```bash
S07_EVIDENCE_ROOT='<HUMAN_APPROVED_ABSOLUTE_EXTERNAL_DIRECTORY>'

python3 - "$REPO_ROOT" "$S07_EVIDENCE_ROOT" <<'PY'
from pathlib import Path
import os
import sys

repo = Path(sys.argv[1]).resolve(strict=True)
root_lexical = Path(sys.argv[2]).absolute()

if not root_lexical.is_absolute():
    raise SystemExit("evidence root must be absolute")

for component in (root_lexical, *root_lexical.parents):
    if component.is_symlink():
        raise SystemExit(f"symlink component rejected: {component}")

root_lexical.mkdir(mode=0o700, parents=False, exist_ok=True)
root = root_lexical.resolve(strict=True)

if root == repo or root.is_relative_to(repo) or repo.is_relative_to(root):
    raise SystemExit("evidence root must be external and non-overlapping")

for name in ("candidates", "reviews", "operations", "pr-observation"):
    path = root / name
    path.mkdir(mode=0o700, exist_ok=True)
    if path.is_symlink() or not path.is_dir():
        raise SystemExit(f"unsafe evidence directory: {path}")

try:
    os.chmod(root, 0o700)
    for name in ("candidates", "reviews", "operations", "pr-observation"):
        os.chmod(root / name, 0o700)
except OSError:
    pass
PY

CANDIDATE_DIR="$S07_EVIDENCE_ROOT/candidates"
REVIEW_DIR="$S07_EVIDENCE_ROOT/reviews"
OPERATION_DIR="$S07_EVIDENCE_ROOT/operations"
HUMAN_DECISION="$S07_EVIDENCE_ROOT/planning-human-decision.json"

CREATE_RESULT="$S07_EVIDENCE_ROOT/planning-create-command-result.json"
REVIEW_COMMAND_RESULT="$S07_EVIDENCE_ROOT/planning-review-command-result.json"
APPLY_RESULT="$S07_EVIDENCE_ROOT/planning-apply-command-result.json"
```

Define a strict JSON field reader:

```bash
json_get() {
  python3 - "$1" "$2" <<'PY'
import json
import sys

value = json.loads(open(sys.argv[1], "rb").read())
for part in sys.argv[2].split("."):
    value = value[part]
if isinstance(value, (dict, list)):
    print(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
else:
    print(value)
PY
}
```

Record the initial canonical SHA-256 manifest using repository-relative paths only:

```bash
ISSUE_DIR='spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00334-implement-chatgpt-issue-planning-workflow'

python3 - "$ISSUE_DIR" > "$S07_EVIDENCE_ROOT/canonical-preapply-sha256.txt" <<'PY'
from pathlib import Path
import hashlib
import sys

root = Path(sys.argv[1])
for name in ("design.md", "plan.md", "requirement.md"):
    path = root / name
    print(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.as_posix()}")
PY

S07_STARTED_AT_UTC="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
S07_START_EPOCH="$(date '+%s')"
```

## 6.C Real `planning create`

Revalidate identity immediately before transport:

```bash
test "$(git rev-parse HEAD)" = "$REQUIRED_HEAD"
test "$(git rev-parse "refs/remotes/origin/$BRANCH")" = "$REQUIRED_HEAD"
test -z "$(git status --porcelain=v1 --untracked-files=all)"
```

Execute:

```bash
./spec-dock/scripts/spec-dock-chatgpt planning create \
  --issue "$ISSUE_ID" \
  --output "$CANDIDATE_DIR" \
  --format json |
  tee "$CREATE_RESULT"

test "$(json_get "$CREATE_RESULT" status)" = 'ok'
test "$(json_get "$CREATE_RESULT" reason)" = 'candidate_created'

CANDIDATE_LOGICAL_FILENAME="$(
  json_get "$CREATE_RESULT" output.candidate_identity.logical_filename
)"
CANDIDATE_PATH="$CANDIDATE_DIR/$CANDIDATE_LOGICAL_FILENAME"
CANDIDATE_REPORTED_SHA="$(
  json_get "$CREATE_RESULT" output.candidate_identity.zip_sha256
)"

test -f "$CANDIDATE_PATH"

CANDIDATE_OBSERVED_SHA="$(
  python3 - "$CANDIDATE_PATH" <<'PY'
from pathlib import Path
import hashlib
import sys
print(hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest())
PY
)"

test "$CANDIDATE_OBSERVED_SHA" = "$CANDIDATE_REPORTED_SHA"

test "$(git rev-parse HEAD)" = "$REQUIRED_HEAD"
test "$(git rev-parse "refs/remotes/origin/$BRANCH")" = "$REQUIRED_HEAD"
test -z "$(git status --porcelain=v1 --untracked-files=all)"
```

Expected result:

```text
status=ok
reason=candidate_created
repository mutation=none
Candidate publication=one immutable external ZIP
```

The create result reports the exact Candidate identity and byte count; the ZIP filename must be taken from that identity rather than discovered by directory scanning.

## 6.D Fresh git-bound defect-only Review

Use the reviewed HEAD value captured after revalidation, not an assumed constant:

```bash
REVIEWED_HEAD="$(git rev-parse HEAD)"
test "$REVIEWED_HEAD" = "$REQUIRED_HEAD"
test "$(git rev-parse "refs/remotes/origin/$BRANCH")" = "$REVIEWED_HEAD"
test -z "$(git status --porcelain=v1 --untracked-files=all)"
```

Execute:

```bash
./spec-dock/scripts/spec-dock-chatgpt review planning \
  --issue "$ISSUE_ID" \
  --mode git-bound \
  --reviewed-head "$REVIEWED_HEAD" \
  --output "$REVIEW_DIR" \
  --format json |
  tee "$REVIEW_COMMAND_RESULT"

test "$(json_get "$REVIEW_COMMAND_RESULT" status)" = 'ok'
test "$(json_get "$REVIEW_COMMAND_RESULT" reason)" = 'review_completed'

REVIEW_RESULT_REL="$(
  json_get "$REVIEW_COMMAND_RESULT" output.review_result_file
)"
REVIEW_RESULT="$REVIEW_DIR/$REVIEW_RESULT_REL"
REVIEW_REPORTED_SHA="$(
  json_get "$REVIEW_COMMAND_RESULT" output.review_result_sha256
)"
REVIEWED_IDENTITY_SHA="$(
  json_get "$REVIEW_COMMAND_RESULT" output.reviewed_identity_sha256
)"

test -f "$REVIEW_RESULT"

REVIEW_OBSERVED_SHA="$(
  python3 - "$REVIEW_RESULT" <<'PY'
from pathlib import Path
import hashlib
import sys
print(hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest())
PY
)"
test "$REVIEW_OBSERVED_SHA" = "$REVIEW_REPORTED_SHA"
```

Classify the Review:

```bash
python3 - "$REVIEW_RESULT" <<'PY'
import json
import sys

review = json.loads(open(sys.argv[1], "rb").read())
findings = review["findings"]
blocking = [f for f in findings if f["severity"] in ("p0", "p1")]
nonblocking = [f for f in findings if f["severity"] in ("p2", "p3")]

expected = "fail" if blocking else "pass"
if review["verdict"] != expected:
    raise SystemExit("Review verdict contradicts P0/P1 findings")

print(f"verdict={review['verdict']}")
print(f"p0_p1_count={len(blocking)}")
print(f"p2_p3_count={len(nonblocking)}")

if blocking:
    for finding in blocking:
        print(
            f"BLOCKING {finding['id']} {finding['severity']} "
            f"{finding['exact_location']}"
        )
    raise SystemExit(20)
PY
```

Interpretation:

* Exit `0`, verdict `pass`: proceed to the exact Human decision gate.
* P2/P3-only: do not revise, do not mutate, and proceed; the Review contract treats these as non-blocking.
* Exit `20`: stop. The target cannot continue in the selected no-canonical-rewrite git-bound lane.
* Any malformed identity, changed HEAD, changed source bytes, publication failure, or non-fresh Review: stop and start a fresh Review only after the source is stable.

Review verdict is mechanically tied to P0/P1 presence: P0/P1 means `fail`; no P0/P1 means `pass`.

## 6.E Optional P0/P1 revision — archive-only contingency, not authorized here

Do **not** execute this block in the selected git-bound run.

It is included only to define the product’s exact P0/P1-only revision interface if a later Human explicitly changes the mode to archive-candidate and authorizes exact Candidate adoption.

Archive Review:

```bash
./spec-dock/scripts/spec-dock-chatgpt review planning \
  --issue "$ISSUE_ID" \
  --mode archive-candidate \
  --candidate "$CANDIDATE_PATH" \
  --output "$REVIEW_DIR" \
  --format json
```

For one actual P0/P1 finding, write exactly one minimum Semantic revision request beside that Review’s exact `planning-review-result.json`:

```json
{
  "schema_version": 1,
  "lane": "semantic",
  "candidate_identity": {
    "issue_id": "iss-00334",
    "candidate_id": "<exact candidate_id>",
    "version": 1,
    "logical_filename": "<exact logical_filename>",
    "observed_transport_filename": "<exact observed_transport_filename>",
    "internal_root": "<exact internal_root>",
    "source_repository": "chemitaro/spec-dock",
    "source_branch": "iss-00334-implement-chatgpt-issue-planning-workflow",
    "source_head": "3bc0b8bada9b07ebc85f8cf29e15e361bd204f12",
    "zip_sha256": "<exact Candidate ZIP SHA-256>"
  },
  "preserve_assumptions": [],
  "finding_ids": ["<one actual P0/P1 finding ID>"],
  "review_result_sha256": "<exact raw planning-review-result.json SHA-256>"
}
```

Then:

```bash
./spec-dock/scripts/spec-dock-chatgpt planning revise \
  --candidate "$CANDIDATE_PATH" \
  --request "<exact-review-directory>/planning-revision-request.json" \
  --output "$CANDIDATE_DIR" \
  --format json
```

Review the newly emitted Candidate in a fresh Review. Never reuse the prior Review, prior identity digest, or prior Human decision. Never create a revision request for a P2/P3-only Review. The revise command resolves only the fixed sibling `planning-review-result.json`.

## 6.F Exact Human decision preparation — mandatory stop

At this point, do not run apply.

Present the Human with the exact fields listed in §7, including the full Review result and all binding SHA-256 values. Candidate identity must be marked **evidence-only, not the git-bound adoption target**.

The Human—not a script, Codex, ChatGPT, or the worker—must supply the exact bytes of:

```text
<S07_EVIDENCE_ROOT>/planning-human-decision.json
```

For approval, the file must have exactly this closed shape, with `reviewed_identity` copied verbatim from the published Review:

```json
{
  "schema_version": 1,
  "issue_id": "iss-00334",
  "reviewed_identity": {
    "mode": "git-bound",
    "issue_id": "iss-00334",
    "repository": "chemitaro/spec-dock",
    "branch": "iss-00334-implement-chatgpt-issue-planning-workflow",
    "source_head": "3bc0b8bada9b07ebc85f8cf29e15e361bd204f12",
    "canonical_target_paths": [
      "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00334-implement-chatgpt-issue-planning-workflow/design.md",
      "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00334-implement-chatgpt-issue-planning-workflow/plan.md",
      "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00334-implement-chatgpt-issue-planning-workflow/requirement.md"
    ]
  },
  "reviewed_identity_sha256": "<exact reviewed_identity_sha256>",
  "review_result_sha256": "<exact raw Review file SHA-256>",
  "decision": "approved",
  "plan_adoption": true,
  "implementation_start": true,
  "decided_at": "<Human-supplied ISO-8601 timestamp with timezone>"
}
```

The approved truth table requires `decision=approved`, `plan_adoption=true`, and `implementation_start=true`. A rejection requires `decision=rejected` and both booleans `false`. The raw Review bytes digest and reviewed identity must match exactly.

If the Human rejects, stop. Do not run apply.

## 6.G Apply — only after exact approval

Revalidate all identities without changing the repository:

```bash
test -f "$HUMAN_DECISION"
test "$(git branch --show-current)" = "$BRANCH"
test "$(git rev-parse HEAD)" = "$REVIEWED_HEAD"
git fetch --prune origin "$BRANCH"
test "$(git rev-parse "refs/remotes/origin/$BRANCH")" = "$REVIEWED_HEAD"
test -z "$(git status --porcelain=v1 --untracked-files=all)"

HUMAN_DECISION_SHA="$(
  python3 - "$HUMAN_DECISION" <<'PY'
from pathlib import Path
import hashlib
import sys
print(hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest())
PY
)"
printf 'human_decision_sha256=%s\n' "$HUMAN_DECISION_SHA"
```

Execute only through the installed public boundary:

```bash
./spec-dock/scripts/spec-dock-chatgpt planning apply \
  --issue "$ISSUE_ID" \
  --mode git-bound \
  --review-result "$REVIEW_RESULT" \
  --human-decision "$HUMAN_DECISION" \
  --expected-head "$REVIEWED_HEAD" \
  --reviewed-head "$REVIEWED_HEAD" \
  --output "$OPERATION_DIR" \
  --format json |
  tee "$APPLY_RESULT"

test "$(json_get "$APPLY_RESULT" status)" = 'ready'
test "$(json_get "$APPLY_RESULT" reason)" = 'adoption_published'
```

Extract and verify publication:

```bash
APPLY_OPERATION_ID="$(json_get "$APPLY_RESULT" output.operation_id)"
DECISION_ARTIFACT_PATH="$(json_get "$APPLY_RESULT" output.decision_artifact_path)"
LOCAL_COMMIT="$(json_get "$APPLY_RESULT" output.local_commit)"
REMOTE_COMMIT="$(json_get "$APPLY_RESULT" output.remote_commit)"

test -n "$APPLY_OPERATION_ID"
test -n "$DECISION_ARTIFACT_PATH"
test "$LOCAL_COMMIT" = "$REMOTE_COMMIT"

git fetch --prune origin "$BRANCH"

test "$(git rev-parse HEAD)" = "$LOCAL_COMMIT"
test "$(git rev-parse "refs/remotes/origin/$BRANCH")" = "$LOCAL_COMMIT"
test -z "$(git status --porcelain=v1 --untracked-files=all)"
test -f "$DECISION_ARTIFACT_PATH"
```

Verify that git-bound apply did not rewrite the canonical documents:

```bash
python3 - "$ISSUE_DIR" > "$S07_EVIDENCE_ROOT/canonical-postapply-sha256.txt" <<'PY'
from pathlib import Path
import hashlib
import sys

root = Path(sys.argv[1])
for name in ("design.md", "plan.md", "requirement.md"):
    path = root / name
    print(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.as_posix()}")
PY

cmp \
  "$S07_EVIDENCE_ROOT/canonical-preapply-sha256.txt" \
  "$S07_EVIDENCE_ROOT/canonical-postapply-sha256.txt"
```

Inspect the apply commit:

```bash
git show --stat --oneline --decorate "$LOCAL_COMMIT"
git show --name-status --format= "$LOCAL_COMMIT"
git show --check "$LOCAL_COMMIT"
```

Expected:

* `ready/adoption_published`;
* `local_commit == remote_commit == current HEAD == origin/current-branch`;
* canonical three-document SHA-256 manifest unchanged;
* deterministic Human decision artifact present;
* no unrelated file mutation;
* clean worktree.

The apply result exposes `operation_id`, decision artifact path, local commit/tree, and remote commit.

## 6.H S07 metrics and report evidence

Record in the existing Issue `report.md` only after successful apply. Do not record absolute host paths, raw model conversations, credentials, browser state, or raw PR observation payloads.

Required fields:

```text
target_issue
planning_mode
initial_head
reviewed_head
candidate_id
candidate_version
candidate_zip_sha256
reviewed_identity_sha256
review_result_sha256
human_decision_sha256
apply_operation_id
apply_local_commit
apply_remote_commit
canonical_docs_unchanged
intervention_count
handoff_count
handoff_items
started_at_utc
ended_at_utc
wall_clock_seconds
failure_modes
baseline_failures
s07_product_regressions
issue_wide_code_review
qa_review
delivery_pr
```

Measurement rules:

* `intervention_count`: count explicit Human decisions requested after S07 execution begins. Count the initial six-field authorization and the exact planning decision separately. Count additional Human blocker dispositions separately. Do not count automated commands or model calls.
* `handoff_count`: count distinct worker/role handoffs, not messages. Record each handoff’s source role, destination role, and bounded subject.
* `handoff_items`: count the identity/evidence objects transferred at each handoff, such as Candidate identity, Review result, decision, apply result, code-review packet, and QA packet.
* `wall_clock_seconds`: `ended_epoch - S07_START_EPOCH`, including Human-gate elapsed time; also record start/end UTC.
* `failure_modes`: record every blocked, stale, rejected, retry, timeout, CI failure, Review failure, identity mismatch, and recovery outcome. Use `none` only when none occurred.
* `baseline_failures`: failures reproduced unchanged at the required start HEAD.
* `s07_product_regressions`: new failures introduced after the live run or S07 report/repair commits.

Finish the timing values:

```bash
S07_ENDED_AT_UTC="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
S07_END_EPOCH="$(date '+%s')"
S07_WALL_CLOCK_SECONDS="$((S07_END_EPOCH - S07_START_EPOCH))"

printf '%s\n' \
  "started_at_utc=$S07_STARTED_AT_UTC" \
  "ended_at_utc=$S07_ENDED_AT_UTC" \
  "wall_clock_seconds=$S07_WALL_CLOCK_SECONDS"
```

After updating `report.md`, run the normal sync/validation path, inspect every generated diff, commit, and push. Do not modify Requirement, Design, or Plan.

## 6.I Local tests, issue-wide reviews, and final gates

Run from the latest pushed S07 head.

Focused S06/S07 regression set:

```bash
uv run pytest \
  tests/cli_runtime/test_chatgpt_cli.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/unit/commands/test_issue_planning.py \
  tests/unit/infra/test_init_update.py \
  tests/integration/test_issue_planning_e2e.py
```

Static analysis:

```bash
make lint
```

`make lint` runs `ruff check`, `ruff format --check`, and `mypy` over `src/spec_dock` and `tests`.

Workspace checks:

```bash
./spec-dock/scripts/spec-dock sync --no-github --no-update-active
./spec-dock/scripts/spec-dock validate
git diff --check
git status --short
```

Full Provider CI parity:

```bash
uv run pytest
```

Expected GitHub workflows after PR creation:

* `CI / validate`: checkout, local sync, workspace validation.
* `Provider CI / provider-tests`: package environment, `make lint`, full `uv run pytest`.

Existing starting-HEAD failures must be classified separately from S07 regressions, but a required GitHub Actions failure still blocks `merge-prepared`. Baseline classification is not a waiver.

Run two fresh defect-only reviews against the complete latest branch diff:

```text
issue-wide code review:
  target: main...latest pushed HEAD
  authority: current Requirement/Design/Plan plus accepted S07 mutation boundary
  blocking scope: actual P0/P1 defects, required-CI defects, security/integrity defects
  non-blocking scope: P2/P3 observations; no branch mutation solely for them
  expected result: PASS or P2/P3-only

QA review:
  target: acceptance criteria, live dogfood evidence, identity/parity proof,
          tests, baseline separation, report evidence, and PR gate readiness
  blocking scope: missing/contradictory proof, untested required behavior,
                  failed required checks, unauthorized mutation
  expected result: PASS
```

No improvement proposal, speculative architecture work, workflow expansion, or planning regrowth may block S07.

## 6.J Delivery PR creation or reuse

Revalidate the latest final head:

```bash
git fetch --prune origin "$BRANCH" "$BASE"
FINAL_HEAD="$(git rev-parse HEAD)"

test "$(git rev-parse "refs/remotes/origin/$BRANCH")" = "$FINAL_HEAD"
test -z "$(git status --porcelain=v1 --untracked-files=all)"
test "$(git rev-list --count "HEAD..refs/remotes/origin/$BASE")" = '0'

git diff --stat "origin/$BASE...HEAD"
git diff --name-only "origin/$BASE...HEAD"
```

Check for an existing PR:

```bash
gh pr list \
  --repo "$REPOSITORY" \
  --head "$BRANCH" \
  --state open \
  --json number,url,state,isDraft,baseRefName,headRefName,headRefOid
```

If one open PR exists, reuse it. If more than one exists, stop. At inspection time no PR existed.

If none exists, create a ready PR only after every local final gate above passes:

```bash
PR_BODY="$(mktemp)"

cat > "$PR_BODY" <<EOF
## 概要

- ChatGPT-first Issue Planning Workflow の公開コマンド境界を実装しました。
- Candidate、fresh defect-only Review、exact Human decision、transactional apply の identity/authority boundary を実装しました。
- provider、installed runtime、dogfood projection、Skill、docs、tests を同期しました。
- S07 の実 Issue dogfood は git-bound mode で実施し、canonical Requirement/Design/Plan が不変であることを確認しました。

## S07 live dogfood

- Target: \`iss-00334\`
- Mode: \`git-bound\`
- Reviewed HEAD: \`$REVIEWED_HEAD\`
- Candidate ZIP SHA-256: \`$CANDIDATE_REPORTED_SHA\` (evidence-only)
- Reviewed identity SHA-256: \`$REVIEWED_IDENTITY_SHA\`
- Review result SHA-256: \`$REVIEW_REPORTED_SHA\`
- Apply operation: \`$APPLY_OPERATION_ID\`
- Apply commit: \`$LOCAL_COMMIT\`
- Canonical documents unchanged: yes
- Local/remote parity: yes

## 検証

- \`make lint\`
- focused Issue Planning regression suite
- \`uv run pytest\`
- \`spec-dock sync --no-github --no-update-active\`
- \`spec-dock validate\`
- issue-wide defect-only code review
- QA review

Closes #334
EOF

git push -u origin "$BRANCH"

PR_URL="$(
  gh pr create \
    --repo "$REPOSITORY" \
    --base "$BASE" \
    --head "$BRANCH" \
    --title 'feat: ChatGPT Issue Planning Workflow を実装' \
    --body-file "$PR_BODY"
)"

rm -f "$PR_BODY"
printf '%s\n' "$PR_URL"
```

Base selection is `main` because it is the verified repository default, no stronger base exists, and the branch is currently not behind it. PR creation must reuse an existing PR when present and must not create duplicates.

## 6.K Delivery PR observation

Read the PR identity:

```bash
PR_JSON="$(
  gh pr view "$PR_URL" \
    --repo "$REPOSITORY" \
    --json number,url,state,isDraft,baseRefName,headRefName,headRefOid,mergeStateStatus
)"

printf '%s\n' "$PR_JSON"

PR_NUMBER="$(
  python3 -c 'import json,sys; print(json.load(sys.stdin)["number"])' <<<"$PR_JSON"
)"
PR_HEAD="$(
  python3 -c 'import json,sys; print(json.load(sys.stdin)["headRefOid"])' <<<"$PR_JSON"
)"

test "$PR_HEAD" = "$(git rev-parse HEAD)"
```

Invoke only the fixed repository observation script. Its default mode posts one deterministic `@codex review` trigger and then observes GitHub Actions and Review state:

```bash
./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh \
  --repo "$REPOSITORY" \
  --pr "$PR_NUMBER" \
  --head-sha "$PR_HEAD" \
  --out "$S07_EVIDENCE_ROOT/pr-observation" \
  > "$S07_EVIDENCE_ROOT/pr-observation-result.json"
```

Do not use `gh pr checks` as authoritative CI evidence, do not manually post `@codex review`, and do not post arbitrary comments. The observation script’s stdout JSON is authoritative; stderr progress is not.

A `merge-prepared: yes` conclusion requires:

* PR open and non-draft;
* observation bound to the latest head;
* required Actions workflows terminal-green;
* no unresolved P0/P1;
* no visible merge conflict;
* no unresolved Human blocker;
* P2/P3, if any, recorded as non-blocking without a record-only repair push;
* conversation-resolution limitations disclosed;
* latest head re-observed after every repair push.

`merge-prepared` must remain separate from `github-mergeable`; platform branch-protection requirements must be independently confirmed before claiming the latter.

If observation times out, resume against the same trigger boundary. Do not post another trigger:

```bash
./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh \
  --repo "$REPOSITORY" \
  --pr "$PR_NUMBER" \
  --head-sha "$PR_HEAD" \
  --trigger-mode resume \
  --trigger-comment-id "<id from prior result.json>" \
  --trigger-created-at "<created_at from prior result.json>" \
  --out "$S07_EVIDENCE_ROOT/pr-observation" \
  > "$S07_EVIDENCE_ROOT/pr-observation-result.json"
```

---

## 7. Exact identity and digest presentation before Human approval

Present the following as a single approval brief. Do not abbreviate hashes.

### 7.1 Repository binding

```text
repository
branch
expected/current source HEAD
fetched remote HEAD
upstream
target Issue
planning mode
canonical target paths
```

The HEAD values are Git SHA-1 identities and must be labeled as such, not as SHA-256.

### 7.2 Candidate evidence identity

Present all ten fields exactly:

```text
issue_id
candidate_id
version
logical_filename
observed_transport_filename
internal_root
source_repository
source_branch
source_head
zip_sha256
```

These are the closed `IssueCandidateIdentity` fields.

Also show:

```text
zip_byte_count
observed Candidate file SHA-256
reported and observed Candidate SHA-256 equality
Candidate status: evidence-only; not the git-bound adoption target
```

### 7.3 Reviewed identity

For the selected lane, show exactly:

```text
mode = git-bound
issue_id
repository
branch
source_head
canonical_target_paths, in byte-sorted order
reviewed_identity_sha256
```

The reviewed identity digest is SHA-256 over canonical compact JSON with sorted keys.

### 7.4 Exact Review bytes

Show:

```text
review_result_file
review_result_sha256 from command output
independently observed raw-file SHA-256
reported/observed equality
verdict
complete findings array
P0 count
P1 count
P2 count
P3 count
```

Approval is allowed only when:

```text
verdict = pass
P0 count = 0
P1 count = 0
repository/branch/HEAD still match
canonical source bytes have not changed
```

### 7.5 Supporting canonical-byte manifest

Show the full SHA-256 manifest from:

```text
canonical-preapply-sha256.txt
```

This is supporting source-integrity evidence. The formal git-bound decision remains bound through exact repository, branch, source HEAD, paths, reviewed identity digest, and Review result digest.

### 7.6 Before invoking apply

After the Human supplies the decision file, show:

```text
planning-human-decision.json raw SHA-256
decision
plan_adoption
implementation_start
decided_at
reviewed_identity_sha256 equality
review_result_sha256 equality
current local HEAD
current fetched remote HEAD
clean worktree status
```

Do not alter, normalize, reformat, or recreate the Human-supplied decision bytes.

---

## 8. Repository write boundaries

### 8.1 Before exact Human planning approval

Allowed repository writes:

```text
none
```

Specifically prohibited before approval:

* canonical Requirement/Design/Plan edits;
* `report.md` edits;
* generated state changes;
* staging;
* commits;
* pushes;
* decision artifacts;
* Candidate or Review copies;
* temporary prompt packs;
* raw ChatGPT output;
* credentials, browser data, or private host diagnostics.

All Candidate, Review, and command-result writes must remain under the approved external evidence root. Any repository write after Review makes the reviewed source stale and requires restoration plus a fresh Review.

### 8.2 During approved git-bound apply

Expected write:

```text
<iss-00334 issue directory>/artifacts/
  <UTC>-planning-human-decision-<operation-id-prefix>.json
```

The transaction also has a predeclared managed-sync allowlist:

```text
spec-dock/.agent/index-all.json
spec-dock/.agent/index.json
spec-dock/.agent/tree-all.json
spec-dock/.agent/tree.json
spec-dock/.agent/deps-issues.json
spec-dock/tree-all.puml
spec-dock/tree.puml
spec-dock/deps-issues.puml
spec-dock/deps-raw.puml
spec-dock/dashboard.md
spec-dock/.agent/deps.json
spec-dock/.agent/deps.puml
spec-dock/.agent/deps.todo.puml
spec-dock/.work/state.json
spec-dock/.work/index.json
spec-dock/.work/tree.json
spec-dock/adrs/**
```

For this synchronized branch, the expected live result is decision-artifact-only. Any managed-sync change must be explicitly diff-reviewed and explained. Any path outside the apply allowlist is a hard stop.

The following must remain byte-identical:

```text
<issue>/requirement.md
<issue>/design.md
<issue>/plan.md
.assurance.json
sibling Issues
downstream Issues
unrelated Initiative/Epic material
provider and dogfood implementation files
```

### 8.3 After successful apply

Allowed S07 writes:

* the current Issue’s `report.md`, limited to sanitized S07 execution, metrics, final-review, QA, PR, and merge-preparation evidence;
* generated sync outputs resulting from that report update, after exact diff review;
* bounded implementation/test repairs for actual P0/P1 or required-CI defects, only through the established repair workflow;
* commits and fast-forward pushes on the same Issue branch.

Prohibited throughout:

* Requirement/Design/Plan amendment;
* new target Issue;
* new delivery branch;
* second PR;
* force push;
* amend or rebase;
* merge or auto-merge;
* branch deletion;
* Issue close or `issue finish`;
* P2/P3-only repair commits;
* architecture or workflow expansion.

---

## 9. Tests, checks, reviews, and expected outcomes

| Gate                       | Required outcome                                                                       |
| -------------------------- | -------------------------------------------------------------------------------------- |
| Initial Git preflight      | Exact required HEAD, clean tree/index, fetched remote parity, branch not behind `main` |
| Help surface               | All public help commands exit `0`; no planning backend call                            |
| Real create                | `ok/candidate_created`; one immutable external ZIP; zero repository mutation           |
| Candidate integrity        | Reported ZIP SHA-256 equals independently calculated bytes digest                      |
| Fresh git-bound Review     | `ok/review_completed`; exact identity; exact raw Review SHA-256                        |
| Defect classification      | No P0/P1; P2/P3 do not trigger revision                                                |
| Human gate                 | Exact Human-supplied closed JSON; Review and identity digests match                    |
| Apply                      | `ready/adoption_published`                                                             |
| Git-bound source integrity | Canonical Requirement/Design/Plan pre/post SHA-256 manifests identical                 |
| Publication parity         | apply local commit = remote commit = local HEAD = fetched remote HEAD                  |
| Focused regression         | All selected Issue Planning CLI/application/command/init-update/E2E tests pass         |
| Static analysis            | `ruff check`, `ruff format --check`, and `mypy` pass                                   |
| Workspace                  | sync and validate pass; no unexplained diff                                            |
| Full Provider CI parity    | Full `uv run pytest` passes, or required check remains blocking                        |
| Issue-wide code review     | No unresolved P0/P1; no planning regrowth                                              |
| QA review                  | Acceptance, live evidence, parity, metrics, and baseline separation complete           |
| Delivery PR                | Exactly one open ready PR, base `main`, head current branch, correct issue linkage     |
| PR observation             | Latest-head Actions green; no P0/P1; no conflict; limitations known                    |
| Final delivery state       | `merge-prepared: yes`; merge remains Human-only                                        |

S06’s current evidence includes strong focused and integration coverage, but it does not substitute for S07’s current-head local gates or PR-triggered workflows. The canonical report explicitly records that real ChatGPT/GitHub use and real planning apply had not yet been run at S06 closure.

---

## 10. Stop conditions and cleanup

### 10.1 Immediate stop conditions

Stop without create/review if any of the following is true:

* §4.2 authorization is incomplete;
* worktree path is not the exact approved path;
* branch or Issue differs;
* local or remote HEAD differs from the required start HEAD;
* tree, index, or untracked state is dirty;
* upstream is not `origin/<current-branch>`;
* evidence destination is absent, overlapping, symlinked, unsafe, or ambiguous;
* another live process may mutate the worktree;
* an unexpected existing PR or conflicting PR base is found.

Stop before approval if:

* Candidate identity or ZIP digest is inconsistent;
* Review is malformed, stale, not fresh, or identity-mismatched;
* Review asks only for improvements and attempts to block on P2/P3;
* git-bound Review contains an actual P0/P1;
* source HEAD or canonical bytes change;
* evidence contains unsafe or private material.

Stop before or during apply if:

* Human decision bytes were generated, inferred, completed, or edited by a worker;
* decision is rejected;
* Review is not PASS;
* decision/Review/identity digests differ;
* mode differs;
* current/fetched HEAD differs from reviewed HEAD;
* repository mutation occurred after Review;
* apply returns anything other than `ready/adoption_published`.

Stop after apply if:

* canonical planning documents changed;
* local commit and remote commit differ;
* worktree is dirty;
* an unexpected path changed;
* operation reports rollback, recovery required, publication pending, or remote divergence;
* tests, validation, required CI, code review, or QA fail;
* PR head differs from the observed head;
* required Actions fail;
* unresolved P0/P1, merge conflict, or Human blocker remains.

### 10.2 Cleanup and recovery

* Never overwrite or reuse an existing Candidate or Review publication path.
* Preserve immutable external Candidate, Review, Human decision, and operation evidence until PR delivery and Human disposition are complete.
* On pre-apply failure, leave the repository unchanged and record only the sanitized failure class.
* On `rolled_back`, verify exact restoration and stop.
* On `recovery_required`, `publication_pending`, or `blocked_remote_diverged`, preserve the operation directory and operation ID; do not use reset, amend, rebase, force push, or manual file reconstruction.
* After a PR observation timeout, use the exact resume trigger metadata; do not post another trigger.
* Delete only disposable local files such as the temporary PR body after successful PR creation.
* Do not delete the branch, merge the PR, close Issue #334, or run `issue finish`.

The PR merge-preparer explicitly forbids merge, auto-merge, branch deletion, Issue close, and `issue finish`.

---

## 11. Copy-ready bounded instruction for the next worker

```text
Execute S07 only for chemitaro/spec-dock.

Repository:
- target Issue: iss-00334
- branch: iss-00334-implement-chatgpt-issue-planning-workflow
- required starting HEAD: 3bc0b8bada9b07ebc85f8cf29e15e361bd204f12
- default/PR base: main
- do not create another Issue, branch, or PR

Current disposition is STOP_AT_HUMAN_GATE.

First perform only the read-only preflight/help sequence from the S07 packet.
Re-prove the exact dedicated worktree, clean tree/index, branch, upstream,
fetched local/remote HEAD parity, Issue #334 open state, and existing-PR state.
Do not rely on prior local-state claims.

Do not run any live planning command until the Human supplies every field of
S07LiveRunAuthorizationV1:
target Issue, absolute worktree, branch, start HEAD, git-bound mode, live
ChatGPT/GitHub authorization, exact external evidence root, pre/post-decision
mutation scope, current-branch commit/push authority, one ready Delivery PR,
and explicit no-merge/no-finish boundaries.

After that initial authorization:
1. Create the exact external evidence subdirectories.
2. Record the canonical pre-apply SHA-256 manifest.
3. Run the installed repo-local public boundary:
   ./spec-dock/scripts/spec-dock-chatgpt planning create
4. Verify the exact Candidate identity and ZIP SHA-256; keep it external and
   label it evidence-only.
5. Run a fresh defect-only git-bound Review at the exact synchronized HEAD:
   ./spec-dock/scripts/spec-dock-chatgpt review planning
6. Do not revise for P2/P3-only findings.
7. If git-bound Review reports a P0/P1, stop. Do not edit canonical documents,
   do not switch modes silently, and do not invent another target.
8. If Review passes, prepare the complete Human approval brief with the exact
   repository/branch/HEAD, Candidate identity, Candidate ZIP SHA-256,
   reviewed identity, reviewed_identity_sha256, exact raw Review SHA-256,
   verdict, all findings, and canonical file SHA-256 manifest.
9. STOP_AT_HUMAN_GATE. Do not generate, infer, complete, normalize, or edit
   planning-human-decision.json.

Only after the Human supplies exact approved PlanningHumanDecisionV1 bytes:
10. Re-prove clean exact HEAD and fetched remote parity.
11. Run git-bound planning apply through the installed public command.
12. Require ready/adoption_published, canonical three-document byte identity,
    operation evidence, clean tree, and local/remote commit parity.
13. Record sanitized S07 metrics and evidence in the existing report.md only.
14. Run focused regression tests, make lint, full uv run pytest, sync, validate,
    issue-wide defect-only code review, and QA review. Separate starting-HEAD
    baselines from S07 regressions, but do not waive required CI.
15. Commit and push only allowed S07 evidence/repairs on the same branch.
16. Create or reuse exactly one ready PR to main, linked to #334.
17. Observe the exact latest PR head through the repository
    wait_pr_observation.sh script. Repair only actual P0/P1 or required-CI
    defects through the bounded repair workflow. Do not mutate for P2/P3 only.
18. Return merge-prepared evidence or a precise Human gate.

Never amend canonical Requirement/Design/Plan in this packet.
Never merge, enable auto-merge, delete the branch, close Issue #334, or run
issue finish.
```
