---

kind: "implementation-handoff"
issue: "iss-00395"
title: "Issue #395 LunaMax Implementation Handoff — Ready Contract"
artifact_path: "artifacts/iss-00395-luna-max-implementation-handoff.md"
generated_at: "2026-09-16"
repository: "chemitaro/spec-dock"
branch: "iss-00395-regression-baseline-terminalization-and-product-defect-repair"
integration_branch: "codex/epic-00384-provider-test-strategy-planning"
elaboration_input_sha: "fe9ac410a23ca4ccce2de440ef0ddb6c76c48af9"
elaboration_input_tree: "4ee7cf0911ed6e4e51f8d50a09e2b34c71eae599"
p392_entry_sha: "921bf7512c72bfa2887673cb7ec9bc512cec6ff3"
p392_entry_tree: "190bc566a18cd84813c4b7c043f8724e275cb55d"
support_history_sha: "c0736434503117d5d468d1438fb18da16d382a56"
support_history_tree: "cec02ce70fbcbbbac811a04106dcc15540ad4d09"
implementation_allowed: true
owner_decisions_required: []
human_merge_only: true
authority: "advisory-execution-handoff"
derived_from:

  - "requirement.md"
  - "design.md"
  - "plan.md"

---

# Issue #395 LunaMax Implementation Handoff

## 1. この文書の効力

この文書は、Codex GPT-5.6 LunaMax実装エージェントへIssue #395の実装候補作成を委任する際のexecution contractである。

現在の実装許可は次のとおりである。

```text
implementation_allowed = true
owner_decisions_required = []
human_merge_only = true
```

`implementation_allowed=true`はユーザーの明示dispatchを記録する。しかし、本書、Design、Plan、formal Issue start、active pointer、dependency state、`owner_decisions_required=[]`のいずれも単独ではProduct、test、ledger、dogfood projectionの変更を許可しない。fresh Strict specification reviewのpass、P0/P1=0、Phase E execution packet、concurrent-writer absenceが揃うまで、実効的なmutation gateは閉じている。

LunaMaxは、次の状態を分離して扱う。

1. Read-only preflight
2. 独立specification review
3. Explicit implementation dispatch
4. Product/test candidate作成
5. Working-tree provisional verification
6. Commit/push
7. Independent implementation reviews
8. PR preparation
9. Human merge
10. Post-merge same-tip B1/B2
11. Issue closureと#396 start

前段の完了を、後段の許可として解釈してはならない。

## 2. 固定identity

| Role                       | Value                                                                     |
| -------------------------- | ------------------------------------------------------------------------- |
| Repository                 | `chemitaro/spec-dock`                                                     |
| Issue branch               | `iss-00395-regression-baseline-terminalization-and-product-defect-repair` |
| Integration branch         | `codex/epic-00384-provider-test-strategy-planning`                        |
| P392 Product entry SHA     | `921bf7512c72bfa2887673cb7ec9bc512cec6ff3`                                |
| P392 Product entry tree    | `190bc566a18cd84813c4b7c043f8724e275cb55d`                                |
| Elaboration input SHA      | `fe9ac410a23ca4ccce2de440ef0ddb6c76c48af9`                                |
| Elaboration input tree     | `4ee7cf0911ed6e4e51f8d50a09e2b34c71eae599`                                |
| Entry ledger               | 15 total / 14 active / 1 resolved                                         |
| Entry timing               | 243 node weights                                                          |
| Required-fast              | Exact 4 nodeids                                                           |
| Target ledger              | 15 total / 0 active / 15 resolved                                         |
| Target resolution modes    | 14 fixed-in-place / 1 superseded                                          |
| Target approved failures   | 0                                                                         |
| Target unexpected failures | 0                                                                         |

P392はIssue #395のProduct/test/ledger entry pointである。P392はB1、Issue #392 acceptance、Issue #392 closure、Issue #395 implementation permission、Issue #396 start permissionではない。

Elaboration inputはP392後のreceipt文書を含む仕様作成sourceである。P392からelaboration inputまでの変更は、Epic PlanとIssue #392 Reportの二文書に限定される。Product source、tests、ledger、timing、policy、workflowはP392と同一である。

## 3. Execution packet v3

Codexは、少なくとも次のpacketをactual valuesで発行する。

```yaml
packet_schema: 3
issue: iss-00395
repository: chemitaro/spec-dock
branch: iss-00395-regression-baseline-terminalization-and-product-defect-repair
integration_branch: codex/epic-00384-provider-test-strategy-planning

p392_sha: 921bf7512c72bfa2887673cb7ec9bc512cec6ff3
p392_tree: 190bc566a18cd84813c4b7c043f8724e275cb55d

elaboration_input_sha: fe9ac410a23ca4ccce2de440ef0ddb6c76c48af9
elaboration_input_tree: 4ee7cf0911ed6e4e51f8d50a09e2b34c71eae599

spec_freeze_sha: "<actual clean pushed 40-hex SHA>"
spec_freeze_tree: "<actual clean pushed 40-hex tree>"
resume_mode: "initial-spec-freeze | post-u05-checkpoint"
resume_checkpoint_sha: "<required only for post-u05-checkpoint>"
resume_checkpoint_tree: "<required only for post-u05-checkpoint>"
initial_red_evidence:
  root: "<repository-external immutable directory; required only for post-u05-checkpoint>"
  identity_sha256: "<64 lowercase hex; required only for post-u05-checkpoint>"
  summary_sha256: "<64 lowercase hex; required only for post-u05-checkpoint>"

spec_review:
  reviewer: chatgpt-spec-review-strict
  target_sha: "<same as spec_freeze_sha>"
  target_tree: "<same as spec_freeze_tree>"
  status: pass
  p0: 0
  p1: 0
  receipt_identity: "<non-empty immutable identity>"
  receipt_path: "<repository-external immutable JSON path>"
  receipt_sha256: "<64 lowercase hex>"

implementation_authorized: true

concurrent_writer:
  absent: true
  assertion_id: "<non-empty identity>"
  assertion_path: "<repository-external immutable JSON path>"
  assertion_sha256: "<64 lowercase hex>"
  issued_at_utc: "<ISO-8601>"
  expires_at_utc: "<ISO-8601>"
  scope_paths:
    - full-regression-ledger.json
    - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py
    - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/repo_context.py
    - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py
    - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py
    - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py
    - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/github_cli.py
    - spec-dock/scripts/spec_dock_runtime/infra/git_cli.py
    - spec-dock/scripts/spec_dock_runtime/application/repo_context.py
    - spec-dock/scripts/spec_dock_runtime/application/ports.py
    - spec-dock/scripts/spec_dock_runtime/application/create_node.py
    - spec-dock/scripts/spec_dock_runtime/cli/bootstrap.py
    - spec-dock/scripts/spec_dock_runtime/infra/github_cli.py
    - spec-dock/spec-dock.version
    - .agents/skills/spec-dock/.spec-dock-provider-slot.json
    - .agents/skills/spec-dock-grill-with-docs/.spec-dock-provider-slot.json
    - tests/cli_runtime/test_delete.py
    - tests/cli_runtime/test_import.py
    - tests/cli_runtime/test_runtime_import_s10.py
    - tests/cli_runtime/test_sync.py
    - tests/cli_runtime/test_workbench.py
    - tests/cli_runtime/test_new.py
    - tests/unit/commands/test_runtime_new_s08.py
    - tests/unit/infra/test_init_update.py
    - tests/unit/test_provider_test_lanes.py
    - tests/integration/test_issue_392_acceptance.py
    - refs/heads/iss-00395-regression-baseline-terminalization-and-product-defect-repair

commit_push_authorized: false
pr_prepare_authorized: false
human_merge_only: true
```

`initial-spec-freeze`では`initial_red_evidence`を省略する。`post-u05-checkpoint`ではその3 fieldを必須とし、既存の初回RED証拠をSHA-256でpacketへ束縛する。

### 3.1 Environment mapping

| Packet field                         | Environment variable                 |
| ------------------------------------ | ------------------------------------ |
| `spec_freeze_sha`                    | `SPEC_FREEZE_SHA`                    |
| `spec_freeze_tree`                   | `SPEC_FREEZE_TREE`                   |
| `resume_mode`                        | `RESUME_MODE`                        |
| `resume_checkpoint_sha`              | `RESUME_CHECKPOINT_SHA`              |
| `resume_checkpoint_tree`             | `RESUME_CHECKPOINT_TREE`             |
| `initial_red_evidence.root`          | `INITIAL_RED_EVIDENCE_ROOT`          |
| `initial_red_evidence.identity_sha256` | `INITIAL_RED_IDENTITY_SHA256`       |
| `initial_red_evidence.summary_sha256`  | `INITIAL_RED_SUMMARY_SHA256`        |
| `spec_review.receipt_path`           | `SPEC_REVIEW_RECEIPT_PATH`           |
| `spec_review.receipt_sha256`         | `SPEC_REVIEW_RECEIPT_SHA256`         |
| `implementation_authorized`          | `IMPLEMENTATION_AUTHORIZED`          |
| `concurrent_writer.assertion_path`   | `CONCURRENT_WRITER_ASSERTION_PATH`   |
| `concurrent_writer.assertion_sha256` | `CONCURRENT_WRITER_ASSERTION_SHA256` |
| `commit_push_authorized`             | `COMMIT_PUSH_AUTHORIZED`             |
| `pr_prepare_authorized`              | `PR_PREPARE_AUTHORIZED`              |
| `human_merge_only`                   | `HUMAN_MERGE_ONLY`                   |

### 3.2 Permission semantics

* `IMPLEMENTATION_AUTHORIZED=false`または未設定:

  * Read-only preflightだけを実行できる。
  * Product、test、ledger、dogfoodを変更しない。
* `IMPLEMENTATION_AUTHORIZED=true`:

  * Mutation gateが成立した後だけ実装候補を作成できる。
* `COMMIT_PUSH_AUTHORIZED=false`:

  * Working-tree candidateとprovisional evidenceを返して停止する。
  * `merge_ready=false`とする。
* `COMMIT_PUSH_AUTHORIZED=true`:

  * 全gateがGREENの場合だけ、`initial-spec-freeze`ではfocused 26 paths、`post-u05-checkpoint`では事前検証済みnon-empty incremental subsetをIssue branchへcommit/pushできる。累積implementation surfaceのfocused 26 pathsは別のpath gateで維持する。
* `PR_PREPARE_AUTHORIZED=false`:

  * PRを作成・更新しない。
* `PR_PREPARE_AUTHORIZED=true`:

  * Reviewed clean pushed candidateに対してだけPRを作成・更新できる。
* `HUMAN_MERGE_ONLY=true`:

  * LunaMaxはPRをmergeしない。

### 3.3 Specification-review remediation track

最新のStrict仕様レビューがP0/P1を返した場合は、実装trackを開始せず、`documentation-correction`としてcanonical Requirement/Design/Planとこのadvisory handoffの契約だけを修正する。このtrackではProduct、test、ledger、dogfood、evaluator、verifierを変更せず、clean pushed specification candidateを作成して同じ仕様レビューをfresh rerunする。`review_status=pass`、P0=0、P1=0になった後にだけ、以下の実装mutation gateとfocused candidate gateを適用する。

### 3.4 Identity modes

`SPEC_FREEZE_SHA/TREE`はreviewed specificationのauthority identityであり、両modeでcurrent local `HEAD`、configured upstream、remote branch tipの一致対象である。U05後のresumeでは、実行packetが渡す`RESUME_CHECKPOINT_SHA/TREE`をU05後の既存clean実装candidateを表す祖先のresume基点として別に検査し、current equalityの対象にはしない。U05のledger transitionが既に完了している場合は、current rootのterminal stateを確認してL1を再実行せず、仕様レビュー対象を実装開始点とする。resume中の未commit差分は、旧identityへ戻す操作や空commitで隠さず、allowed pathとして束縛してcommitする。

## 4. 共通shell constants

以降のcommandはrepository rootの同じBash sessionで実行する。

```bash
set -euo pipefail
umask 077

export EXPECTED_REPOSITORY="chemitaro/spec-dock"
export ISSUE_BRANCH="iss-00395-regression-baseline-terminalization-and-product-defect-repair"
export INTEGRATION_BRANCH="codex/epic-00384-provider-test-strategy-planning"

export P392_SHA="921bf7512c72bfa2887673cb7ec9bc512cec6ff3"
export P392_TREE="190bc566a18cd84813c4b7c043f8724e275cb55d"

export ELABORATION_INPUT_SHA="fe9ac410a23ca4ccce2de440ef0ddb6c76c48af9"
export ELABORATION_INPUT_TREE="4ee7cf0911ed6e4e51f8d50a09e2b34c71eae599"

export SUPPORT_HISTORY_SHA="c0736434503117d5d468d1438fb18da16d382a56"

export RESUME_MODE="${RESUME_MODE:-initial-spec-freeze}"
case "$RESUME_MODE" in
  initial-spec-freeze) ;;
  post-u05-checkpoint)
    : "${RESUME_CHECKPOINT_SHA:?RESUME_CHECKPOINT_SHA is required}"
    : "${RESUME_CHECKPOINT_TREE:?RESUME_CHECKPOINT_TREE is required}"
    : "${INITIAL_RED_EVIDENCE_ROOT:?INITIAL_RED_EVIDENCE_ROOT is required}"
    : "${INITIAL_RED_IDENTITY_SHA256:?INITIAL_RED_IDENTITY_SHA256 is required}"
    : "${INITIAL_RED_SUMMARY_SHA256:?INITIAL_RED_SUMMARY_SHA256 is required}"
    ;;
  *) exit 1 ;;
esac

ROW_1='tests/cli_runtime/test_delete.py::TestCliDelete::test_delete_scrubbed_meta_is_not_reobserved_by_validate_sync_active'
ROW_2_HISTORICAL='tests/cli_runtime/test_distribution_cutover.py::test_s40b_retained_skill_identity_matches_issue359_final_source'
ROW_2_SUCCESSOR='tests/cli_runtime/test_distribution_cutover.py::test_s40b_retained_skill_identity_matches_current_provider_and_dogfood'
ROW_3='tests/cli_runtime/test_import.py::TestCliImport::test_import_accepts_canonical_url_when_origin_is_credentialed_https_remote'
ROW_4='tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_parent_fallback_regression'
ROW_5='tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_load_active_manifest_chain_regression'
ROW_6='tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_parent_fallback_re_resolves_inside_lock_when_parent_drifts_regression'
ROW_7='tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_numeric_target_uses_resolved_current_repo_slug_for_github_read'
ROW_8='tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_issue_uses_target_repo_slug_for_same_repo_url_when_present'
ROW_9='tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_import_then_sync_artifact_path_name_content_regression'
ROW_10='tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_post_import_sync_negative_path_regression'
ROW_11='tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::test_execute_create_plan_reuse_seam'
ROW_12='tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::test_final_api_call_site_and_structural_regression'
ROW_13='tests/cli_runtime/test_sync.py::TestCliSync::test_new_and_active_and_sync'
ROW_14='tests/cli_runtime/test_sync.py::TestCliSync::test_sync_emits_tree_puml_ready_board_at_spec_dock_root'
ROW_15='tests/cli_runtime/test_workbench.py::TestCliWorkbench::test_copied_workbench_readme_and_payloads_remain_opaque_to_runtime_commands'

REPAIR_ROWS=(
  "$ROW_1"
  "$ROW_3"
  "$ROW_4"
  "$ROW_5"
  "$ROW_6"
  "$ROW_7"
  "$ROW_8"
  "$ROW_9"
  "$ROW_10"
  "$ROW_11"
  "$ROW_13"
  "$ROW_14"
  "$ROW_15"
)

ACTIVE_ROWS=(
  "$ROW_1"
  "$ROW_3"
  "$ROW_4"
  "$ROW_5"
  "$ROW_6"
  "$ROW_7"
  "$ROW_8"
  "$ROW_9"
  "$ROW_10"
  "$ROW_11"
  "$ROW_12"
  "$ROW_13"
  "$ROW_14"
  "$ROW_15"
)

ALL_OBSERVED_ROWS=(
  "${ACTIVE_ROWS[@]}"
  "$ROW_2_SUCCESSOR"
)

S10_ROWS=(
  "$ROW_4"
  "$ROW_5"
  "$ROW_6"
  "$ROW_7"
  "$ROW_8"
  "$ROW_9"
  "$ROW_10"
  "$ROW_11"
)

SELECTION_ROWS=(
  "$ROW_1"
  "$ROW_13"
  "$ROW_14"
  "$ROW_15"
)

IMPLEMENTATION_PATHS=(
  full-regression-ledger.json
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/repo_context.py
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/github_cli.py
  spec-dock/scripts/spec_dock_runtime/infra/git_cli.py
  spec-dock/scripts/spec_dock_runtime/application/repo_context.py
  spec-dock/scripts/spec_dock_runtime/application/ports.py
  spec-dock/scripts/spec_dock_runtime/application/create_node.py
  spec-dock/scripts/spec_dock_runtime/cli/bootstrap.py
  spec-dock/scripts/spec_dock_runtime/infra/github_cli.py
  spec-dock/spec-dock.version
  .agents/skills/spec-dock/.spec-dock-provider-slot.json
  .agents/skills/spec-dock-grill-with-docs/.spec-dock-provider-slot.json
  tests/cli_runtime/test_delete.py
  tests/cli_runtime/test_import.py
  tests/cli_runtime/test_runtime_import_s10.py
  tests/cli_runtime/test_sync.py
  tests/cli_runtime/test_workbench.py
  tests/cli_runtime/test_new.py
  tests/unit/commands/test_runtime_new_s08.py
  tests/unit/infra/test_init_update.py
  tests/unit/test_provider_test_lanes.py
  tests/integration/test_issue_392_acceptance.py
)
```

## 5. Private evidence workspace

Evidence、raw logs、verifier artifactsはrepository外のprivate directoryへ保存する。

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
test "$REPO_ROOT" = "$PWD"

BASE_TMP="${TMPDIR:-/tmp}"
test -d "$BASE_TMP"
test -w "$BASE_TMP"

export EVIDENCE_DIR="$(
  mktemp -d "${BASE_TMP%/}/iss-00395.XXXXXXXX"
)"
export TEST_TMPDIR="$EVIDENCE_DIR/tmp"

mkdir -p "$TEST_TMPDIR"

python - "$REPO_ROOT" "$EVIDENCE_DIR" <<'PY'
from pathlib import Path
import sys

repository = Path(sys.argv[1]).resolve()
evidence = Path(sys.argv[2]).resolve()

assert evidence != repository
assert repository not in evidence.parents

print(f"evidence-root={evidence}")
PY
```

禁止事項:

* Predictableな`/tmp/iss-00395-*.log`への書込み
* 共有`spec-dock/.workbench/full-regression`から最新runを推測すること
* Raw credentialを含むlogの配布
* Evidence、cache、`.pyc`、`.workbench` raw artifactのcommit

## 6. Read-only preflight

Read-only preflightは`implementation_allowed=true`の記録後も実行できる。これはeffective mutation gateが開いたことを意味しない。

### 6.1 Specification and resume identity

`SPEC_FREEZE_SHA/TREE`はreviewed specificationのauthority identityであり、両modeでcurrent tip equalityに使用する。U05後のresumeでは、execution packetが渡す`RESUME_CHECKPOINT_SHA/TREE`を既存実装の祖先基点として別に検証し、current tip equalityには使用しない。

```bash
: "${SPEC_FREEZE_SHA:?SPEC_FREEZE_SHA is required}"
: "${SPEC_FREEZE_TREE:?SPEC_FREEZE_TREE is required}"

test "${#SPEC_FREEZE_SHA}" -eq 40
test "${#SPEC_FREEZE_TREE}" -eq 40

case "$RESUME_MODE" in
  initial-spec-freeze)
    EXPECTED_CURRENT_SHA="$SPEC_FREEZE_SHA"
    EXPECTED_CURRENT_TREE="$SPEC_FREEZE_TREE"
    ;;
  post-u05-checkpoint)
    : "${RESUME_CHECKPOINT_SHA:?RESUME_CHECKPOINT_SHA is required}"
    : "${RESUME_CHECKPOINT_TREE:?RESUME_CHECKPOINT_TREE is required}"
    test "${#RESUME_CHECKPOINT_SHA}" -eq 40
    test "${#RESUME_CHECKPOINT_TREE}" -eq 40
    EXPECTED_CURRENT_SHA="$SPEC_FREEZE_SHA"
    EXPECTED_CURRENT_TREE="$SPEC_FREEZE_TREE"
    ;;
  *) exit 1 ;;
esac
```

### 6.2 Repository、branch、upstream、remote、clean status

```bash
git fetch --prune origin

test "$(git rev-parse --show-toplevel)" = "$PWD"
test "$(git rev-parse --abbrev-ref HEAD)" = "$ISSUE_BRANCH"

test "$(git rev-parse HEAD)" = "$EXPECTED_CURRENT_SHA"
test "$(git rev-parse 'HEAD^{tree}')" = "$EXPECTED_CURRENT_TREE"

test "$(git rev-parse '@{upstream}')" = "$EXPECTED_CURRENT_SHA"
test "$(
  git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}'
)" = "origin/$ISSUE_BRANCH"

REMOTE_LINE="$(
  git ls-remote --heads origin "refs/heads/$ISSUE_BRANCH"
)"

test "$(
  printf '%s\n' "$REMOTE_LINE" \
    | awk 'NF {count++} END {print count+0}'
)" -eq 1

test "$(
  printf '%s\n' "$REMOTE_LINE" \
    | awk 'NF {print $1}'
)" = "$EXPECTED_CURRENT_SHA"

test -z "$(
  git status --porcelain=v1 --untracked-files=all
)"

git merge-base --is-ancestor \
  "$P392_SHA" \
  "$ELABORATION_INPUT_SHA"

git merge-base --is-ancestor \
  "$ELABORATION_INPUT_SHA" \
  "$SPEC_FREEZE_SHA"

git merge-base --is-ancestor \
  "$SPEC_FREEZE_SHA" \
  "$EXPECTED_CURRENT_SHA"

if [ "$RESUME_MODE" = "post-u05-checkpoint" ]; then
  git merge-base --is-ancestor \
    "$RESUME_CHECKPOINT_SHA" \
    "$SPEC_FREEZE_SHA"
  test "$(git rev-parse "$RESUME_CHECKPOINT_SHA^{tree}")" = \
    "$RESUME_CHECKPOINT_TREE"
fi

test "$(git rev-parse "$P392_SHA^{tree}")" = "$P392_TREE"
test "$(
  git rev-parse "$ELABORATION_INPUT_SHA^{tree}"
)" = "$ELABORATION_INPUT_TREE"
```

`post-u05-checkpoint`では、U05の承認済み遷移が`RESUME_CHECKPOINT_SHA`の履歴に存在することとcurrent rootがterminalizedであることを確認し、L1を再実行しない。current tipは`SPEC_FREEZE_SHA`に一致し、resume checkpointからcurrent reviewed specification targetまでの差分はcanonical-document-onlyとして後続のadmission gateで検査する。

一つでも失敗した場合、変更0でstop-and-returnする。Reset、force checkout、別branch、default branchへのfallbackで修復しない。

### 6.3 Origin repository identity

Raw remote URLを表示せず、production resolverが返すorigin identityだけを検証する。ここに別の`urlsplit`、regex、remote parserを作らない。

```bash
env PYTHONPATH=src/spec_dock/assets/spec_dock/scripts \
  uv run python - "$EXPECTED_REPOSITORY" <<'PY'
from pathlib import Path
import sys

from spec_dock_runtime.infra.git_cli import origin_github_repo_slug

expected = sys.argv[1].lower()
actual = origin_github_repo_slug(Path.cwd())
assert actual == expected, {
    "expected": expected,
    "actual": actual or "unresolved",
}
print(f"repository-identity={actual}")
PY
```

### 6.4 P392からelaboration inputまでのdoc-only差分

```bash
python - "$P392_SHA" "$ELABORATION_INPUT_SHA" <<'PY'
from pathlib import Path
import subprocess
import sys

base, head = sys.argv[1:]

epic = Path(
    "spec-dock/initiatives/"
    "init-local-00003-architecture-maintenance-and-hardening/"
    "epics/"
    "epic-00384-provider-test-strategy-simplification-"
    "and-execution-cost-reduction"
)

expected = {
    str(epic / "plan.md"),
    str(
        epic
        / "issues/"
        "iss-00392-provider-lifecycle-and-regression-"
        "gate-hard-cutover/"
        "report.md"
    ),
}

actual = set(
    subprocess.check_output(
        ["git", "diff", "--name-only", base, head, "--"],
        text=True,
    ).splitlines()
)

assert actual == expected, {
    "stage": "p392-to-elaboration",
    "expected": sorted(expected),
    "actual": sorted(actual),
}

print("p392-to-elaboration-doc-only-ok")
PY
```

### 6.5 Specification admission history

```bash
python - "$RESUME_MODE" "${RESUME_CHECKPOINT_SHA:-}" \
  "${RESUME_CHECKPOINT_TREE:-}" "$SUPPORT_HISTORY_SHA" \
  "$SPEC_FREEZE_SHA" <<'PY'
from pathlib import Path
import subprocess
import sys

(
    mode,
    resume_checkpoint,
    resume_tree,
    support_history,
    spec_freeze,
) = sys.argv[1:]

issue = Path(
    "spec-dock/initiatives/"
    "init-local-00003-architecture-maintenance-and-hardening/"
    "epics/"
    "epic-00384-provider-test-strategy-simplification-"
    "and-execution-cost-reduction/"
    "issues/"
    "iss-00395-regression-baseline-terminalization-"
    "and-product-defect-repair"
)

primary = {
    str(issue / "requirement.md"),
    str(issue / "design.md"),
    str(issue / "plan.md"),
    str(
        issue
        / "artifacts/"
        "iss-00395-luna-max-implementation-handoff.md"
    ),
    str(
        issue
        / "artifacts/"
        "iss-00395-human-guide.html"
    ),
    str(
        issue
        / "artifacts/"
        "iss-00395-chatgpt-spec-pack-manifest.md"
    ),
}

support = {
    str(issue / "artifacts/design-luna-max-ready.md"),
    str(issue / "artifacts/iss-00395-design-tdd-ready.md"),
    str(issue / "artifacts/iss-00395-lunamax-handoff-tdd-ready.md"),
    str(issue / "artifacts/iss-00395-plan-review-analysis.md"),
    str(issue / "artifacts/iss-00395-plan-tdd-ready.md"),
    str(issue / "artifacts/iss-00395-requirement-tdd-ready.md"),
    str(issue / "artifacts/iss-00395-spec-pack.zip"),
    str(issue / "artifacts/iss-00395-tdd-ready-manifest.md"),
    str(issue / "artifacts/iss-00395-tdd-ready-pack.receipt.md"),
    str(issue / "artifacts/iss-00395-tdd-ready-pack.zip"),
    str(issue / "artifacts/luna-max-implementation-handoff-ready.md"),
    str(issue / "artifacts/luna-max-readiness-analysis.md"),
    str(issue / "artifacts/luna-max-readiness-manifest.md"),
    str(issue / "artifacts/luna-max-readiness-pack.receipt.md"),
    str(issue / "artifacts/luna-max-readiness-pack.zip"),
    str(issue / "artifacts/plan-lunamax-ready.md"),
}

def changed_paths(base, head):
    return set(
        subprocess.check_output(
            ["git", "diff", "--name-only", "--no-renames", base, head, "--"],
            text=True,
        ).splitlines()
    )

subprocess.run(
    ["git", "merge-base", "--is-ancestor", support_history, spec_freeze],
    check=True,
)
if mode == "initial-spec-freeze":
    assert changed_paths(support_history, spec_freeze) == primary
elif mode == "post-u05-checkpoint":
    assert resume_checkpoint
    assert len(resume_checkpoint) == 40
    assert len(resume_tree) == 40
    subprocess.run(
        ["git", "merge-base", "--is-ancestor", resume_checkpoint, spec_freeze],
        check=True,
    )
    assert subprocess.check_output(
        ["git", "rev-parse", f"{resume_checkpoint}^{{tree}}"],
        text=True,
    ).strip() == resume_tree

    resume_to_spec_paths = changed_paths(resume_checkpoint, spec_freeze)
    assert resume_to_spec_paths <= primary, {
        "stage": "resume-checkpoint-to-reviewed-specification",
        "allowed": sorted(primary),
        "actual": sorted(resume_to_spec_paths),
    }
else:
    raise AssertionError(f"unsupported resume mode: {mode}")

support_changes = changed_paths(support_history, spec_freeze) & support
assert not support_changes, {
    "stage": "support-history-no-diff",
    "changed": sorted(support_changes),
}

for path in sorted(primary):
    candidate = Path(path)
    assert candidate.is_file(), path
    assert candidate.stat().st_size > 0, path

print(f"specification-admission-ok mode={mode}; support-history-nonblocking=true")
PY
```

The six primary paths are the only current specification surface. The sixteen support paths are preserved history; a simple no-diff check prevents accidental mutation, but their mode, object type, and Git object ID are not a second implementation gate. In `post-u05-checkpoint`, the handoff requires only that the resume-to-target correction diff stays within the six primary paths. The execution handoff must not use a 22-path current-spec allowlist, a directory-prefix or glob allowlist, a Manifest self-declaration, or working-tree existence as a substitute for the current canonical path check. Support-history edits, deletion, rename, regeneration, recompression, reclassification, and new support artifacts are forbidden.

### 6.6 Active state、metadata、validation

```bash
./spec-dock/scripts/spec-dock active show \
  | tee "$EVIDENCE_DIR/active-show.txt"

grep -F \
  'iss-00395' \
  "$EVIDENCE_DIR/active-show.txt"

python - <<'PY'
from pathlib import Path
import json

path = Path(
    "spec-dock/initiatives/"
    "init-local-00003-architecture-maintenance-and-hardening/"
    "epics/"
    "epic-00384-provider-test-strategy-simplification-"
    "and-execution-cost-reduction/"
    "issues/"
    "iss-00395-regression-baseline-terminalization-"
    "and-product-defect-repair/"
    ".meta.json"
)

value = json.loads(path.read_text(encoding="utf-8"))

assert value["id"] == "iss-00395"
assert value["type"] == "issue"
assert value["github"]["repo_owner"] == "chemitaro"
assert value["github"]["repo_name"] == "spec-dock"
assert value["github"]["issue_number"] == 395
assert value.get("depends_on", []) == []

print("issue-metadata-ok")
PY

./spec-dock/scripts/spec-dock validate \
  | tee "$EVIDENCE_DIR/spec-freeze-validate.txt"

grep -F \
  'spec-dock: ok (validate) nodes=236' \
  "$EVIDENCE_DIR/spec-freeze-validate.txt"
```

Preflightを通すために次を行ってはならない。

* `active set`
* `issue start`
* `.meta.json`の手編集
* active pointerの手編集
* dependency storageの手編集
* generated index/tree/diagramの手編集

## 7. Source and baseline drift guard

### 7.1 Verified source blobs

`initial-spec-freeze`では、`SPEC_FREEZE_SHA`のblobsがelaboration inputと一致しなければならない。`post-u05-checkpoint`では、P392前のledger blobをcurrent specへ再適用せず、次のno-touch面が`RESUME_CHECKPOINT_SHA`と`SPEC_FREEZE_SHA`の間で一致することを検証する。

```bash
if [ "$RESUME_MODE" = "initial-spec-freeze" ]; then
python - "$SPEC_FREEZE_SHA" <<'PY'
import subprocess
import sys

sha = sys.argv[1]

expected = {
    "full-regression-timing-weights.json":
        "bdeeb6238609c38085aaed8023b78319a3dd0c6d",
    "tests/conftest.py":
        "d574c3a3e7a09c34f708c576a3b41a3b35772072",
    "scripts/quality/verify_full_regression.py":
        "d01045add90b6e98b58fd210d2ade0d340f7b576",
    "tests/cli_runtime/test_runtime_shell_s11.py":
        "0960800ec3eb183fd2cabcf2a90a9fd220c0a62d",
    "src/spec_dock/assets/spec_dock/scripts/"
    "spec_dock_runtime/commands/new.py":
        "c967fcd279d628bf3c98b1795ebd090eda5fb959",
    "src/spec_dock/assets/spec_dock/scripts/"
    "spec_dock_runtime/application/contracts.py":
        "bc64a84f15b1176cb077c320c5fd5e7cb924589d",
    "src/spec_dock/assets/spec_dock/scripts/"
    "spec_dock_runtime/domain/artifacts.py":
        "9f62ddf799f22910efeda5eebb4ba41e775241ac",
    "src/spec_dock/assets/spec_dock/scripts/"
    "spec_dock_runtime/infra/template_scaffolder.py":
        "86489fdf323d0e70e52bec9d049bbd9b086c76b3",
    ".github/workflows/provider-ci.yml":
        "db1adceda41e7927a9dd7e5f7934d3f88152bf06",
    ".github/workflows/provider-full-regression.yml":
        "259c7988f3cf13ed4484be60bc200e01680b95f2",
}

actual = {
    path: subprocess.check_output(
        ["git", "rev-parse", f"{sha}:{path}"],
        text=True,
    ).strip()
    for path in expected
}

mismatch = {
    path: {
        "expected": expected[path],
        "actual": actual[path],
    }
    for path in expected
    if actual[path] != expected[path]
}

assert not mismatch, mismatch
print("source-blob-guard-ok")
PY
else
python - "$RESUME_CHECKPOINT_SHA" "$SPEC_FREEZE_SHA" <<'PY'
import subprocess
import sys

base, head = sys.argv[1:]
paths = {
    "full-regression-timing-weights.json",
    "tests/conftest.py",
    "scripts/quality/full_regression_baseline.py",
    "scripts/quality/verify_full_regression.py",
    "tests/unit/test_full_regression_baseline.py",
    ".github/workflows/provider-ci.yml",
    ".github/workflows/provider-full-regression.yml",
}

def blob(revision, path):
    return subprocess.check_output(
        ["git", "rev-parse", f"{revision}:{path}"],
        text=True,
    ).strip()

mismatch = {
    path: {"resume": blob(base, path), "spec": blob(head, path)}
    for path in sorted(paths)
    if blob(base, path) != blob(head, path)
}

assert not mismatch, mismatch
print("post-u05-source-and-implementation-no-touch-ok")
PY
fi
```

Blob driftがある場合、変更0でstop-and-returnする。

### 7.2 Entry ledger evidence

初回のtransitionでは、P392 entryのimmutable Git blobをhistorical beforeとしてprivate evidenceへ保存する。作業ツリーのcurrent rootをbeforeとしてコピーしてはならない。U05後のresumeではこのbeforeを再構築し、current rootのterminalized afterを検証するだけで、ledger transition writeを再実行しない。

```bash
git show \
  "$P392_SHA:full-regression-ledger.json" \
  > "$EVIDENCE_DIR/ledger-before.json"
```

Entry stateは次でなければならない。

* 15 rows
* Rows 1、3–15が`active`
* Row 2が`resolved/superseded`
* Row order unchanged
* Historical signatures unchanged
* Row 2 successor unchanged
* Timing 243
* Required-fast 4

`post-u05-checkpoint`では、上記はP392 historical beforeの期待値であり、current rootの検査値ではない。current afterは15 rows、0 active、15 resolved、14 `fixed-in-place`、1 `superseded`であることを別のafter assertionで確認する。

## 8. Test lane contract

### 8.1 Ordinary lane

```bash
env TMPDIR="$TEST_TMPDIR" \
  uv run pytest
```

Ordinary laneは現行policy skipを保持する。Skipされたheavy nodeをGREENとして扱わない。

### 8.2 Selected heavy lane

`tests/cli_runtime/`または`tests/integration/`のpath/nodeを直接選ぶcommandは、必ず次を含む。

```text
--run-full-regression --full-regression-shard
```

例:

```bash
env TMPDIR="$TEST_TMPDIR" \
  uv run pytest \
    --run-full-regression \
    --full-regression-shard \
    -q \
    --tb=short \
    "$ROW_3"
```

Heavy nodeの受入条件:

* collected exactly once
* executed exactly once
* outcome `passed`
* skip 0
* xfailed 0
* xpassed 0
* error 0
* failure signatureなし

### 8.3 Full verifier（clean candidate only）

各runへprivateな空directoryを渡す。このコマンドは説明用の形だけを示し、merge-blockingのfull verifier receiptとして受け入れるのは、N1後のclean pushed `IMPLEMENTATION_SHA/TREE`に対する§28の実行だけである。意図的なtracked変更が残るworking treeでは、focused/manual diagnosticを超えて実行・受入してはならない。

```bash
ARTIFACT_ROOT="$EVIDENCE_DIR/full-example"
mkdir -p "$ARTIFACT_ROOT"

test -z "$(
  find "$ARTIFACT_ROOT" -mindepth 1 -print -quit
)"

env TMPDIR="$TEST_TMPDIR" \
  uv run python \
    -m scripts.quality.verify_full_regression \
    --shards 4 \
    --artifact-dir "$ARTIFACT_ROOT"
```

`result.json`は、そのprivate root内でexactly oneでなければならない。

## 9. 変更許可ファイル（focused 26 paths）

Mutation authorization後に変更できるtracked pathsは、§4の`IMPLEMENTATION_PATHS`にある26件だけである。以降のgateは同じ配列を再利用し、別のallowlistを定義しない。

`tests/unit/test_provider_test_lanes.py`は、P392 entryのimmutable `full-regression-ledger.json` blobをbefore、current root ledgerをafterとして比較するmigration observerである。`tests/integration/test_issue_392_acceptance.py`は、Issue #392の独立したboundary witnessとして、不要なIssue #395/#396文書SHA比較だけを除去する。P392 entry SHA `921bf7512c72bfa2887673cb7ec9bc512cec6ff3`のimmutable baseline source binding、Issue #392のledger、timing、required-fast、policy、workflow、その他のassertionは変更しない。assertionの削除・弱化・skip・xfail化、仕様書SHAの同期gate追加は許可しない。

### 9.1 Hand-edit可能なpaths

§4の`IMPLEMENTATION_PATHS`にあるprovider source、test、ledgerだけを直接編集する。`full-regression-ledger.json`は全14 active nodesのnormal-pass proof後に限り編集する。

### 9.2 Generated paths

`IMPLEMENTATION_PATHS`内の六つのruntime mirror、`spec-dock.version`、二つのslot marker（計9件）は手編集しない。Provider source GREEN後にcurrent lifecycle commandで一つのcandidateとして生成する。

## 10. Read-only / no-touch surfaces

次は本Issueで変更しない。

```text
full-regression-timing-weights.json
tests/conftest.py
scripts/quality/full_regression_baseline.py
scripts/quality/verify_full_regression.py
tests/unit/test_full_regression_baseline.py
.github/workflows/provider-ci.yml
.github/workflows/provider-full-regression.yml
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_node.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/template_scaffolder.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/artifacts.py
tests/cli_runtime/test_runtime_shell_s11.py
```

次もno-touchである。

* Parent Epic R/D/P
* Accepted ADR
* Active failure disposition register
* Provider Lifecycle Wire Contract
* Epic Integration Branch Contract
* Rolling-Wave Contract
* Issue #392 lifecycle sourceとArtifacts
* Issue #396 Requirement、Design、Plan、Product
* `E384-QUAL-001`
* Required contexts
* Branch protection
* Main branch
* Managed `.meta.json`
* Active pointer
* Dependency storage
* Generated index/tree/diagram

The exact sixteen support-history artifacts recorded at `SUPPORT_HISTORY_SHA` are also no-touch paths. They are preserved evidence, not current authority or implementation input; do not edit, delete, rename, regenerate, recompress, or reclassify them.

## 11. 13個の修正対象

14 active rowsのうち、実際にsource/test editを行う対象は13 rowsである。Row 12はcurrent Product boundaryが既に正しいためno-editである。

| Row | Node                                                                          | Repair surface     | Required correction                                                            |
| --: | ----------------------------------------------------------------------------- | ------------------ | ------------------------------------------------------------------------------ |
|   1 | `test_delete_scrubbed_meta_is_not_reobserved_by_validate_sync_active`         | Test observer      | `active set --id iss-00058 --force`を`active set --id iss-00058`へ変更             |
|   3 | `test_import_accepts_canonical_url_when_origin_is_credentialed_https_remote`  | Product + observer | Read-only identityとpublication policyを分離し、credential non-exposure assertionを追加 |
|   4 | `test_parent_fallback_regression`                                             | Test double        | `_StubTemplateScaffolder.copy_scaffolded_tree_at`を追加                           |
|   5 | `test_load_active_manifest_chain_regression`                                  | Test double        | 同じcurrent descriptor-bound portへ追随                                             |
|   6 | `test_parent_fallback_re_resolves_inside_lock_when_parent_drifts_regression`  | Test double        | 同じcurrent descriptor-bound portへ追随                                             |
|   7 | `test_import_numeric_target_uses_resolved_current_repo_slug_for_github_read`  | Test double        | 同じcurrent descriptor-bound portへ追随                                             |
|   8 | `test_import_issue_uses_target_repo_slug_for_same_repo_url_when_present`      | Test double        | 同じcurrent descriptor-bound portへ追随                                             |
|   9 | `test_import_then_sync_artifact_path_name_content_regression`                 | Test double        | 同じcurrent descriptor-bound portへ追随                                             |
|  10 | `test_post_import_sync_negative_path_regression`                              | Test double        | 同じcurrent descriptor-bound portへ追随                                             |
|  11 | `test_execute_create_plan_reuse_seam`                                         | Test double        | 同じcurrent descriptor-bound portへ追随                                             |
|  13 | `test_new_and_active_and_sync`                                                | Test observer      | `active set iss-00003 --force`を`active set iss-00003`へ変更                       |
|  14 | `test_sync_emits_tree_puml_ready_board_at_spec_dock_root`                     | Test observer      | `active set 305 --force --no-checkout`を`active set 305`へ変更                     |
|  15 | `test_copied_workbench_readme_and_payloads_remain_opaque_to_runtime_commands` | Test observer      | `--force`を除去し、`active.json` read前にreturn code 0をassert                         |

既存assertionを削除・弱化してはならない。

## 12. Row 2の特別扱い

Row 2は本Issueのactive repair scopeではない。

Historical node:

```text
tests/cli_runtime/test_distribution_cutover.py::test_s40b_retained_skill_identity_matches_issue359_final_source
```

Successor:

```text
tests/cli_runtime/test_distribution_cutover.py::test_s40b_retained_skill_identity_matches_current_provider_and_dogfood
```

Row 2は次の状態を保持する。

```json
{
  "lifecycle": "resolved",
  "resolution_mode": "superseded",
  "successor_nodeid": "tests/cli_runtime/test_distribution_cutover.py::test_s40b_retained_skill_identity_matches_current_provider_and_dogfood"
}
```

禁止事項:

* Row 2 objectの変更
* Successorの置換
* Fixed-in-placeへの変更
* Historical nodeのrename
* Row orderの変更
* Row 2をactiveへ戻すこと

Row 2 successorは、14 active rowsと同じpre-ledger normal-pass commandで実行する。

## 13. Row 12の特別扱い

Row 12 node:

```text
tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::test_final_api_call_site_and_structural_regression
```

Current accepted dependency direction:

```text
commands/new.py
  -> application/contracts.py::CURRENT_CREATABLE_ARTIFACT_TYPES
     -> domain/artifacts.py::CURRENT_CREATABLE_ARTIFACT_TYPES
```

Row 12は次の扱いとする。

1. Entry full verifierでは、active ledgerに対してnormal passしているため`coverage_mismatch`になる。
2. Node単体は最初からnormal passしなければならない。
3. Product sourceとtest sourceは変更しない。
4. Exact blobsとAST import edgeをguardする。
5. 14-row ledger transitionで`resolved/fixed-in-place`へ移す。
6. Nodeが失敗、blob drift、AST driftした場合は、推測修正せずstop-and-returnする。

Row 12に対して次を行ってはならない。

* `commands/new.py`からdomainへdirect importを追加
* Catalogueの複製
* New wrapper typeの発明
* Structural test assertionの削除・弱化
* Row rename
* Successor追加
* Silent retirement

## 14. Entry verifierとindividual RED

### 14.1 Entry full verifier (`initial-spec-freeze` only)

```bash
ENTRY_ARTIFACT_ROOT="$EVIDENCE_DIR/full-entry"
mkdir -p "$ENTRY_ARTIFACT_ROOT"

set +e

env TMPDIR="$TEST_TMPDIR" \
  uv run python \
    -m scripts.quality.verify_full_regression \
    --shards 4 \
    --artifact-dir "$ENTRY_ARTIFACT_ROOT"

ENTRY_RC=$?

set -e

test "$ENTRY_RC" -eq 1

test "$(
  find "$ENTRY_ARTIFACT_ROOT" \
    -type f \
    -name result.json \
    | wc -l \
    | tr -d ' '
)" -eq 1

ENTRY_RESULT="$(
  find "$ENTRY_ARTIFACT_ROOT" \
    -type f \
    -name result.json \
    -print
)"
```

Expected evaluation:

* `status=ledger-mismatch`
* 10 violations exactly
* Rows 4–11: `signature_mismatch`
* Row 12: `coverage_mismatch`
* Row 15: `signature_mismatch`
* Rows 1、3、13、14: `active_verified`
* Row 2: `resolved_verified`
* Unexpected failure 0
* #392-owned failure 0

Extra violation、missing violation、別row failureがあれば停止する。

### 14.1R Post-U05 terminalized entry (`post-u05-checkpoint` only)

13-row initial RED evidenceはPlan §7 D1Rに従い、packet指定rootのidentity・summary・各raw log/observation hash、repository/branch/P392 identity、node集合、初回spec SHAの祖先関係を検証して再利用する。欠落・不一致時はE1/E2前に停止し、修復済みnodeを再実行しない。

post-U05では、U05後に既に確定したcurrent ledgerの15 total / 0 active / 15 resolved / 14 `fixed-in-place` / 1 `superseded`をread-onlyで確認する。D1相当の`ledger-mismatch`、exact 10 active-row violationsまたはU05のledger transitionを再実行しない。migration observerがP392 beforeとcurrent root afterの契約を確認し、Issue #392 boundary witnessと今回のfocused Product/test変更はE4R相当のfocused recheckで検証する。

### 14.2 13修正対象のindividual RED (`initial-spec-freeze` only)

Grouped commandだけでREDを証明してはならない。13 rowsを一件ずつ実行する。

```bash
python - \
  "$EVIDENCE_DIR" \
  "$TEST_TMPDIR" \
  "${REPAIR_ROWS[@]}" <<'PY'
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import sys

evidence = Path(sys.argv[1])
tmpdir = sys.argv[2]
rows = sys.argv[3:]

ordinals = [
    1,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    13,
    14,
    15,
]

patterns = {
    1: r"--force",
    3: r"Current GitHub repo scope could not be resolved from origin",
    4: r"copy_scaffolded_tree_at",
    5: r"copy_scaffolded_tree_at",
    6: r"copy_scaffolded_tree_at",
    7: r"copy_scaffolded_tree_at",
    8: r"copy_scaffolded_tree_at",
    9: r"copy_scaffolded_tree_at",
    10: r"copy_scaffolded_tree_at",
    11: r"copy_scaffolded_tree_at",
    13: r"--force",
    14: r"--force|--no-checkout",
    15: r"--force|active\.json",
}

assert len(rows) == len(ordinals)

summary = []

for ordinal, nodeid in zip(
    ordinals,
    rows,
    strict=True,
):
    observation = (
        evidence
        / f"row-{ordinal:02d}-red-observation.json"
    )
    log = evidence / f"row-{ordinal:02d}-red.log"

    command = [
        "uv",
        "run",
        "pytest",
        "--run-full-regression",
        "--full-regression-shard",
        "--full-regression-observation",
        str(observation),
        "-q",
        "--tb=short",
        nodeid,
    ]

    environment = dict(os.environ)
    environment["TMPDIR"] = tmpdir

    completed = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=environment,
        check=False,
    )

    log.write_text(
        completed.stdout,
        encoding="utf-8",
    )

    assert completed.returncode == 1, {
        "row": ordinal,
        "nodeid": nodeid,
        "returncode": completed.returncode,
    }

    value = json.loads(
        observation.read_text(encoding="utf-8")
    )

    assert value["collected"] == [nodeid]
    assert value["executed"] == [nodeid]
    assert value["outcomes"] == {
        nodeid: "failed",
    }
    assert nodeid in value["failure_signatures"]

    assert re.search(
        patterns[ordinal],
        completed.stdout,
    ), {
        "row": ordinal,
        "expected_pattern": patterns[ordinal],
    }

    if ordinal == 3:
        assert "token@" not in completed.stdout
        assert (
            "https://token@github.com"
            not in completed.stdout
        )

    summary.append(
        {
            "ordinal": ordinal,
            "nodeid": nodeid,
            "returncode": completed.returncode,
            "failure_signature":
                value["failure_signatures"][nodeid],
            "raw_log_sha256": hashlib.sha256(
                log.read_bytes()
            ).hexdigest(),
            "observation_sha256": hashlib.sha256(
                observation.read_bytes()
            ).hexdigest(),
        }
    )

(
    evidence / "individual-red-summary.json"
).write_text(
    json.dumps(
        summary,
        indent=2,
        ensure_ascii=False,
    )
    + "\n",
    encoding="utf-8",
)

print("individual-red=13/13")
PY
```

停止条件:

* 対象rowがpass
* Skip、xfail、xpass
* Setup/teardown error
* Expected failure layerと異なる失敗
* 別nodeの実行
* Observation未生成
* Credential exposure

### 14.3 Row 12 node observation

```bash
ROW12_ENTRY_OBS="$EVIDENCE_DIR/row-12-entry-observation.json"

env TMPDIR="$TEST_TMPDIR" \
  uv run pytest \
    --run-full-regression \
    --full-regression-shard \
    --full-regression-observation "$ROW12_ENTRY_OBS" \
    -q \
    --tb=short \
    "$ROW_12"
```

Expected:

```text
collected = [ROW_12]
executed = [ROW_12]
outcome = passed
failure_signatures = {}
```

## 15. Mutation authorization gate

最初のfile edit直前に実行する。

```bash
: "${SPEC_REVIEW_RECEIPT_PATH:?required}"
: "${SPEC_REVIEW_RECEIPT_SHA256:?required}"

: "${CONCURRENT_WRITER_ASSERTION_PATH:?required}"
: "${CONCURRENT_WRITER_ASSERTION_SHA256:?required}"

: "${IMPLEMENTATION_AUTHORIZED:?required}"
: "${COMMIT_PUSH_AUTHORIZED:?required}"
: "${PR_PREPARE_AUTHORIZED:?required}"
: "${HUMAN_MERGE_ONLY:?required}"

test "$IMPLEMENTATION_AUTHORIZED" = "true"
test "$HUMAN_MERGE_ONLY" = "true"

case "$COMMIT_PUSH_AUTHORIZED" in
  true|false) ;;
  *) exit 1 ;;
esac

case "$PR_PREPARE_AUTHORIZED" in
  true|false) ;;
  *) exit 1 ;;
esac
```

Receipt validation:

```bash
python - \
  "$SPEC_REVIEW_RECEIPT_PATH" \
  "$SPEC_REVIEW_RECEIPT_SHA256" \
  "$CONCURRENT_WRITER_ASSERTION_PATH" \
  "$CONCURRENT_WRITER_ASSERTION_SHA256" \
  "$EXPECTED_REPOSITORY" \
  "$ISSUE_BRANCH" \
  "$SPEC_FREEZE_SHA" \
  "$SPEC_FREEZE_TREE" \
  "${IMPLEMENTATION_PATHS[@]}" <<'PY'
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import sys

review_path = Path(sys.argv[1])
review_hash = sys.argv[2]
writer_path = Path(sys.argv[3])
writer_hash = sys.argv[4]

repository = sys.argv[5]
branch = sys.argv[6]
sha = sys.argv[7]
tree = sys.argv[8]
implementation_paths = set(sys.argv[9:])

def load(
    path: Path,
    expected_hash: str,
) -> dict[str, object]:
    raw = path.read_bytes()

    assert hashlib.sha256(
        raw
    ).hexdigest() == expected_hash

    value = json.loads(raw)
    assert isinstance(value, dict)

    return value

review = load(
    review_path,
    review_hash,
)

assert review["schema_version"] == 2
assert review["reviewer"] == "chatgpt-spec-review-strict"
assert review["repository"] == repository
assert review["branch"] == branch
assert review["target_sha"] == sha
assert review["target_tree"] == tree
assert review["review_status"] == "pass"
assert review["p0"] == 0
assert review["p1"] == 0
assert isinstance(
    review["receipt_identity"],
    str,
)
assert review["receipt_identity"]

writer = load(
    writer_path,
    writer_hash,
)

assert writer["schema_version"] == 2
assert writer["repository"] == repository
assert writer["branch"] == branch
assert writer["target_sha"] == sha
assert writer["target_tree"] == tree
assert writer["absent"] is True
assert isinstance(
    writer["assertion_id"],
    str,
)
assert writer["assertion_id"]

issued = datetime.fromisoformat(
    writer["issued_at_utc"].replace("Z", "+00:00")
)
expires = datetime.fromisoformat(
    writer["expires_at_utc"].replace("Z", "+00:00")
)
now = datetime.now(timezone.utc)

assert issued.tzinfo is not None
assert expires.tzinfo is not None
assert issued <= now <= expires

expected_scope = implementation_paths | {
    f"refs/heads/{branch}",
}

assert set(writer["scope_paths"]) == expected_scope

print(
    "mutation-authorized "
    f"review={review['receipt_identity']} "
    f"writer={writer['assertion_id']}"
)
PY

test -z "$(
  git status --porcelain=v1 --untracked-files=all
)"

test "$(git rev-parse HEAD)" = "$EXPECTED_CURRENT_SHA"
test "$(git rev-parse 'HEAD^{tree}')" = "$EXPECTED_CURRENT_TREE"
```

Writer assertionが期限切れになった場合は再取得する。期限切れ、scope不足、SHA/tree mismatchを無視して継続しない。

## 16. 実装順序

実装順序は変更しない。

```text
Rows 4–11 test double
  -> Rows 1/13/14/15 observers
  -> Row 3 observer
  -> Row 3 Product
  -> Row 12 guard
  -> 15-node pre-ledger GREEN
  -> dogfood projection and protection proof
  -> atomic ledger transition (initial route only)
  -> focused GREEN
  -> post-U05 resume verification without transition rerun
  -> exact clean candidate freeze
  -> full verifier and complete gates on the clean candidate
  -> independent reviews
  -> optional PR preparation
  -> human merge
  -> same-tip B1
  -> same-tip B2
```

初回modeではentry verifier、individual RED、15-node pre-ledger GREENおよびatomic ledger transitionを実行する。post-U05 modeではterminalized entryとmigration observerを確認した後、focused Product/test recheckとdogfood projectionへ進み、entry verifier、individual REDおよびledger transitionを再実行しない。

## 17. Rows 4–11 test double

変更対象:

```text
tests/cli_runtime/test_runtime_import_s10.py::_StubTemplateScaffolder
```

追加するmethod:

```python
def copy_scaffolded_tree_at(
    self,
    src_dir: Path,
    dest_dir: Path,
    dest_dir_fd: int,
    replacements: dict[str, str],
) -> list[Path]:
    self.events.append("copy_scaffolded_tree_at")

    from spec_dock_runtime.infra import (
        template_scaffolder,
    )

    return template_scaffolder.copy_scaffolded_tree_at(
        src_dir,
        dest_dir,
        dest_dir_fd,
        replacements,
    )
```

保持するもの:

* Existing `copy_scaffolded_tree`
* Parent fallback assertions
* Active manifest chain assertions
* Lock-side parent re-resolution
* Repo slug propagation
* Stored owner/name
* Artifact path/name/content
* Negative post-sync behavior
* `execute_create_plan` exactly once
* Rules symlinks
* Retired output absence
* Production held-descriptor path

変更禁止:

* `application/ports.py`
* `application/create_node.py`
* `infra/template_scaffolder.py`
* Production `execute_create_plan`
* Obsolete pathname writerへのfallback

GREENは8件をindividualまたはexact observation付きで確認する。

## 18. Rows 1、13、14、15 observers

Exact replacements:

```text
Row 1
before: active set --id iss-00058 --force
after:  active set --id iss-00058

Row 13
before: active set iss-00003 --force
after:  active set iss-00003

Row 14
before: active set 305 --force --no-checkout
after:  active set 305

Row 15
before: active set --id scope_id --force
after:  active set --id scope_id
```

Row 15は`active.json`を読む前にactive commandのreturn code 0をassertする。

保持するもの:

* Row 1: delete後のmetadata非再観測
* Row 13: new/active/sync収束
* Row 14: tree、PUML、ready-board
* Row 15: Workbench README/payload bytes、active fields、index、validate、sync、deps、active observation

## 19. Row 3 observer and Product

### 19.1 Observer strengthening

Existing nodeをrenameしない。Success assertionを保持し、次を追加する。

```python
combined = p.stdout + p.stderr

assert "token" not in combined
assert (
    "https://token@github.com/example/repo.git"
    not in combined
)
```

Product edit前の再実行では、current repo scope unresolvedでREDのままでなければならない。

### 19.2 Product write surface

Test-firstとGREENはPlan §2のROW3_CREATE_BOUNDARY_NODESに列挙された既存4 nodeを同じ順序で実行する。必須assertionはPlan §H1を正とし、重複説明や追加node/ledger rowを作らない。H5は既存publication endpointの4-case policy matrixに限定する。

変更対象は次の6つのprovider fileである。generated mirrorは§9.2のとおり更新コマンドで投影し、手編集しない。

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/repo_context.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/github_cli.py
```

Required correction:

1. `infra/git_cli.py`の既存`origin_github_publication_endpoint`を唯一のpublication policyとして維持し、薄い`origin_github_publication_repo_slug(repo_root)` adapterだけを追加する。adapterはendpointを一度呼び、accepted slugを返す。fetch-only `origin_github_repo_slug`とimport経路は変更しない。
2. `application/repo_context.py`でcreate/link_existing向けpublication slugをrequireする。preflight failureは`IssueGateway`またはlocal writerより前に返す。
3. `application/ports.py`で新しいGitGateway methodを公開し、`IssueGateway.issue_create`に既に解決済みのnormalized `repo_slug`を必須化する。
4. `application/create_node.py`でpublication preflightを既存same-repository validationの前段へ接続し、create時だけslugをIssueGatewayへ渡す。link_existingも作成境界のrepository contractを満たすため同じpreflightを通す。
5. `cli/bootstrap.py`でapplication portをprovider adapterへ束縛する。command-layerへpolicyを追加しない。
6. `infra/github_cli.py`で`gh issue create --repo <repo_slug>`を実行する。repo slugのtarget bindingだけを行い、raw stderr/stdoutやcredential-bearing URLをexception/diagnosticへ転載しない。

維持する境界:

* `_remote_get_url` signature
* `_remote_has_userinfo` signature
* `_redact_remote_url` signature
* `GitGateway.origin_github_repo_slug` signature
* read-only importのfetch-only identity path
* Numeric-target current-repository requirement
* Foreign repository rejection
* Git coordination behavior
* 既存publication endpointのuserinfo拒否とfetch/push slug equality
* retry、cache、feature flag、background verifier、new CLI flag、duplicate parser

### 19.3 Publication security matrix

次の4 caseを検証する。

1. Credential-bearing fetch:

   * Read-only identity succeeds
   * Publication rejects
   * Credential exposure 0
2. Clean fetch + credential-bearing push:

   * Publication rejects
   * Credential exposure 0
3. Clean fetch/push + different repository:

   * Publication rejects mismatch
4. Clean matching fetch/push:

   * Publication succeeds

Working-treeではfocused確認をprovisionalに記録できるが、同じmatrixを文書・gateごとに重複実行しない。merge-blockingの正式なsecurity receiptはclean implementation SHAで一度、post-merge B1 SHAで一度だけ取得し、同じraw observationを該当receiptへ再利用する。

このmatrixは既存publication endpointのpolicyだけを検証する。create前のapplication preflightと`gh issue create --repo`へのbindingは、Row 3のfocused create-boundary testで別に検証する。

## 20. Row 12 guard

Row 12のProduct/test sourceを編集しない。

Guard対象:

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/artifacts.py
tests/cli_runtime/test_runtime_shell_s11.py
```

Required result:

* Exact verified blobs unchanged
* `commands/new.py` imports catalogue from `application.contracts`
* `application.contracts` imports catalogue from `domain.artifacts`
* Commands layerからdomain/infraへのdirect importなし
* Structural node normal pass
* Product/test edit 0

Guard failure時はstop-and-returnする。

## 21. Pre-ledger normal-pass gate

Ledgerを変更する前に、14 active historical nodesとrow 2 successorを一度に実行する。

```bash
PRE_LEDGER_OBS="$EVIDENCE_DIR/pre-ledger-all-15-observation.json"

env TMPDIR="$TEST_TMPDIR" \
  uv run pytest \
    --run-full-regression \
    --full-regression-shard \
    --full-regression-observation "$PRE_LEDGER_OBS" \
    -q \
    --tb=short \
    "${ALL_OBSERVED_ROWS[@]}"
```

Acceptance:

```text
collected = exact 15 nodeids
executed = exact 15 nodeids
all outcomes = passed
failure_signatures = {}
skip = 0
xfail = 0
xpass = 0
error = 0
```

一件でもnon-passならledgerを変更しない。

## 22. Dogfood projection

### 22.1 Projection前

記録する。

* Pre-projection candidate digest
* Both skill `SKILL.md` hashes
* `spec-dock/initiatives`
* Workbench roots
* Artifacts roots
* Current tracked diff

Protected snapshotはtype、mode、symlink target、file SHA-256を含む。

### 22.2 Projection command

```bash
env TMPDIR="$TEST_TMPDIR" \
  uv run spec-dock update . --json \
  > "$EVIDENCE_DIR/dogfood-update.json"
```

Expected:

* Exit 0
* `status=completed`
* `operation=update`
* `seed_policy=preserve-only`
* `errors=[]`
* `failed_paths=[]`
* `pending_paths=[]`

`completed_with_warnings`は受け入れない。

### 22.3 Generated identity

Require:

* Provider/dogfood runtime byte equality
* New digest is lowercase 64-hex
* New digest differs from old digest
* Update result、ready record、both markersが同じdigest
* Version `0.2.4`
* Record state `ready`
* Operation `null`
* Seed policy `preserve-only`
* Exact slot names
* Both `SKILL.md` unchanged
* Protected snapshot unchanged

### 22.4 Dogfood parity lane（clean candidate only）

このfull-regression parity nodeは、projection直後やledger transition前のworking treeでは実行・受入しない。生成identity、protected-data、pre-ledger 15-node GREENの確認後も、ここではfocused/manual diagnosticだけを記録する。次のcommandはN1で一つのclean pushed `IMPLEMENTATION_SHA/TREE`を作成し、ledger transitionを含むcandidateを確定した後の§28でのみ実行する。

```bash
DOGFOOD_PARITY_OBS="$EVIDENCE_DIR/dogfood-parity-observation.json"

env TMPDIR="$TEST_TMPDIR" \
  uv run pytest \
    --run-full-regression \
    --full-regression-shard \
    --full-regression-observation "$DOGFOOD_PARITY_OBS" \
    -q \
    --tb=short \
    tests/integration/test_provider_lifecycle_dogfood.py::test_t13_source_wheel_sdist_installed_and_dogfood_candidate_are_identical
```

§28での受入条件は、対象nodeが`--run-full-regression --full-regression-shard`で一回だけ収集・実行され、normal passすることである。Heavy flagなしのexit 0は受け入れない。working-tree実行結果はfinal dogfood receiptへ転用しない。

## 23. Atomic ledger transition

Dogfood projectionとpre-ledger 15-node GREENの後だけ実行する。

### 23.1 Allowed semantic changes

Rows 1、3–15について、次だけを変更する。

Before:

```json
{
  "lifecycle": "active"
}
```

After:

```json
{
  "lifecycle": "resolved",
  "resolution_mode": "fixed-in-place"
}
```

変更禁止:

* `nodeid`
* `fixed_point_signature_sha256`
* `current_signature_sha256`
* Historical statuses
* Historical disposition
* Row order
* Row 2
* Top-level historical fields
* New rows
* Deleted rows
* Renamed rows
* `successor_nodeid`
* Retirement metadata

### 23.2 Preservation proof

Transition前の`ledger-before.json`からexpected payloadを構築し、transition後のactual payloadと比較する。

Accepted difference:

```text
Rows 1、3–15:
  lifecycle active -> resolved
  resolution_mode absent -> fixed-in-place

All other values:
  exact equality
```

Verifier GREENはこのpreservation proofを代替しない。

## 24. Working-tree verification

### 24.1 Focused verification

```bash
env TMPDIR="$TEST_TMPDIR" \
  uv run pytest \
    -q \
    --tb=short \
    tests/unit/test_full_regression_baseline.py

POST_LEDGER_OBS="$EVIDENCE_DIR/post-ledger-all-15-observation.json"

env TMPDIR="$TEST_TMPDIR" \
  uv run pytest \
    --run-full-regression \
    --full-regression-shard \
    --full-regression-observation "$POST_LEDGER_OBS" \
    -q \
    --tb=short \
    "${ALL_OBSERVED_ROWS[@]}"
```

### 24.2 Working-tree provisional boundary

Working treeではfocused test、manual invariant、no-touch、protected-data、および必要な診断だけを実行する。candidate-wheel、distribution、installed、dogfood parity、full verifierのfinal receiptはここで生成しない。

```text
candidate_state = working-tree-provisional
merge_ready = false
full_verifier_receipt = absent
candidate_wheel_receipt = absent
```

Full verifierとcandidate-wheelを含む完全なgateは、N1でclean candidateをcommit/pushした後、N2で一度だけ実行する。Working-treeのdiagnostic結果をclean candidate receiptへ転用してはならない。

### 24.3 Working-tree ordinary/source checks

```bash
# Ordinary lane
env TMPDIR="$TEST_TMPDIR" \
  uv run pytest \
    -q \
    --tb=short

# Provider lifecycle unit
env TMPDIR="$TEST_TMPDIR" \
  uv run pytest \
    -q \
    --tb=short \
    tests/unit/provider_lifecycle

# Static analysis
env TMPDIR="$TEST_TMPDIR" \
  make lint

# SpecDock validation
./spec-dock/scripts/spec-dock validate \
  | tee "$EVIDENCE_DIR/post-change-validate.txt"

grep -F \
  'spec-dock: ok (validate) nodes=236' \
  "$EVIDENCE_DIR/post-change-validate.txt"
```

Distribution cutover、platform/coordination、packaged parity、complete dogfood suite、およびcandidate-wheelを含むfull verifierは、N1後のclean candidate gateとして28章のN2で一度だけ実行する。Working-treeで実行したfocused/ordinary結果はprovisionalで、final receiptへ転用しない。

## 25. Exact changed-file gate

このgateの唯一の実行定義はcanonical Plan §M5である。実装候補のpath completenessを確認するときは同gateを一度だけ実行する。post-U05ではP392からcandidateまでの累積implementation setが、Planに既存定義された26-path setと完全一致しなければならない。N1では通過後のnon-empty incremental差分だけをstageし、累積gateを重複実行しない。

## 26. No-touch gate

次のdiffは空でなければならない。

```bash
git diff --exit-code "$SPEC_FREEZE_SHA" -- \
  full-regression-timing-weights.json \
  tests/conftest.py \
  scripts/quality/full_regression_baseline.py \
  scripts/quality/verify_full_regression.py \
  tests/unit/test_full_regression_baseline.py \
  .github/workflows/provider-ci.yml \
  .github/workflows/provider-full-regression.yml \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_node.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/template_scaffolder.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/artifacts.py \
  tests/cli_runtime/test_runtime_shell_s11.py
```

Parent、#392、#396も変更しない。

## 27. Exact candidate freeze

### 27.1 Commit/push未許可

`COMMIT_PUSH_AUTHORIZED=false`の場合:

```text
candidate_state = working-tree-provisional
implementation_sha = null
implementation_tree = null
merge_ready = false
```

Working-tree diff、evidence、stop/return receiptを返して停止する。

### 27.2 Commit/push許可あり

`RESUME_MODE=post-u05-checkpoint`では、`RESUME_CHECKPOINT_SHA/TREE`を既存実装candidateの祖先基点として確認し、current reviewed specification target以後の実装差分が残っている場合だけ、そのnon-empty差分をstage・commit・pushする。current HEADがspec freezeと同じで差分がない場合は、空commitを作らず、実装candidate未作成として停止する。`SPEC_FREEZE_SHA/TREE`からcurrent HEADまでの実装差分がfocused pathsに限定されていることを確認してから`IMPLEMENTATION_SHA/TREE`へ束縛する。

初回のforward commitでは、実装candidateのstaged path set全体をfocused 26件と照合する。`post-u05-checkpoint`では、累積scopeと今回のcommitでstageするincremental setを混同しない。resumeで残るapproved pending setは、stage前に`SPEC_FREEZE_SHA`から実測し、non-emptyで`IMPLEMENTATION_PATHS`のsubsetであることを確認したうえで、そのpending setだけをstageする。既にcommit済みのpathを空の差分として再出現させたり、空commitでpath数を満たしたりしてはならない。

```bash
test "$COMMIT_PUSH_AUTHORIZED" = "true"

EXPECTED_REMOTE_SHA="$SPEC_FREEZE_SHA"
if [ "$RESUME_MODE" = "post-u05-checkpoint" ]; then
  : "${RESUME_CHECKPOINT_SHA:?RESUME_CHECKPOINT_SHA is required}"
  : "${RESUME_CHECKPOINT_TREE:?RESUME_CHECKPOINT_TREE is required}"
fi

test "$(
  git ls-remote \
    --heads \
    origin \
    "refs/heads/$ISSUE_BRANCH" \
    | awk 'NF {print $1}'
  )" = "$EXPECTED_REMOTE_SHA"

test "$(git rev-parse HEAD)" = "$SPEC_FREEZE_SHA"
test "$(git rev-parse 'HEAD^{tree}')" = "$SPEC_FREEZE_TREE"

if [ "$RESUME_MODE" = "initial-spec-freeze" ]; then
git add -- "${IMPLEMENTATION_PATHS[@]}"

python - "${IMPLEMENTATION_PATHS[@]}" <<'PY'
import subprocess
import sys

expected = set(sys.argv[1:])
actual = set(
    subprocess.check_output(
        [
            "git",
            "diff",
            "--cached",
            "--name-only",
            "--no-renames",
            "--",
        ],
        text=True,
    ).splitlines()
)

assert actual == expected, {
    "stage": "initial-focused-26",
    "expected": sorted(expected),
    "actual": sorted(actual),
}

print(f"staged-file-set={len(actual)}/{len(expected)}")
PY
else
python - "$SPEC_FREEZE_SHA" "${IMPLEMENTATION_PATHS[@]}" <<'PY'
import subprocess
import sys

base = sys.argv[1]
allowed = set(sys.argv[2:])
actual = set(
    subprocess.check_output(
        [
            "git",
            "diff",
            "--name-only",
            "--no-renames",
            base,
            "--",
        ],
        text=True,
    ).splitlines()
)

assert actual, "post-U05 incremental diff must be non-empty"
assert actual <= allowed, {
    "stage": "post-u05-incremental-before-stage",
    "allowed": sorted(allowed),
    "actual": sorted(actual),
}

print(f"post-u05-incremental-file-set={len(actual)}/{len(allowed)}")
PY

git add -- "${IMPLEMENTATION_PATHS[@]}"

python - "${IMPLEMENTATION_PATHS[@]}" <<'PY
import subprocess
import sys

allowed = set(sys.argv[1:])
actual = set(
    subprocess.check_output(
        [
            "git",
            "diff",
            "--cached",
            "--name-only",
            "--no-renames",
            "--",
        ],
        text=True,
    ).splitlines()
)

assert actual, "post-U05 incremental stage is empty"
assert actual <= allowed, {
    "stage": "post-u05-incremental-cached",
    "allowed": sorted(allowed),
    "actual": sorted(actual),
}

print(f"staged-incremental-file-set={len(actual)}/{len(allowed)}")
PY
fi

test -z "$(git diff --name-only)"
test -z "$(git ls-files --others --exclude-standard)"

git diff --cached --check

test "$(git config user.name)" = "chemitaro"
test "$(git config user.email)" = \
  "84865385+chemitaro@users.noreply.github.com"

git commit \
  -m "fix(iss-00395): 回帰ベースラインを終端化" \
  -m "- 14件のactive rowをnormal passへ修復" \
  -m "- dogfood候補とledgerを同一candidateへ束縛"

export IMPLEMENTATION_SHA="$(git rev-parse HEAD)"
export IMPLEMENTATION_TREE="$(
  git rev-parse 'HEAD^{tree}'
)"

git push origin \
  "HEAD:refs/heads/$ISSUE_BRANCH"

test "$(git rev-parse '@{upstream}')" = \
  "$IMPLEMENTATION_SHA"

test "$(
  git ls-remote \
    --heads \
    origin \
    "refs/heads/$ISSUE_BRANCH" \
    | awk 'NF {print $1}'
)" = "$IMPLEMENTATION_SHA"

test -z "$(
  git status --porcelain=v1 --untracked-files=all
)"
```

禁止事項:

* Amend
* Force push
* Integration branch direct push
* Evidence/log/cacheのstage
* Extra pathのstage
* Remote drift後のexpected SHA書換え

## 28. Exact clean rerun

Clean pushed `IMPLEMENTATION_SHA`へ、すべてのmerge-blocking proofを再束縛する。ここがcandidate-wheel、distribution、installed、dogfood parity、およびfull verifierの唯一の受入段階である。N1のcommit/push前に、これらのfinal receiptを生成・受入してはならない。

必須rerun:

* Exact clean full verifier（full-regressionの全node、15-node observation、distribution、lifecycle、platform/coordination、packaged parity、dogfood、candidate-wheelを一度に収集・実行）
* Ordinary pytest lane（full-regression opt-inを付けない現行policy lane）
* `make lint`
* SpecDock validate
* Row 3 security matrix
* Row 12 blob/AST guard
* Ledger historical preservation
* Protected-data proof
* Timing 243
* Required-fast 4
* Policy/workflow no-touch
* Exact focused 26-path set
* Clean local/upstream/remote equality

N2のfull verifierで収集済みのnodeやsuiteをN3相当の別commandで再実行しない。Ordinary laneはN2の`--run-full-regression`とは異なるpolicy laneなので、clean candidate上で一度だけ実行する。Row 3 security matrix、row 12 guard、protected-dataおよびno-touchはN2が収集しないmanual proofとしてN3相当で一度だけ実行する。Working-tree proofをexact clean proofとして流用しない。

## 29. Independent implementation reviews

Exact clean pushed candidateに対して、別々のfresh independent sessionで実施する。

### 29.1 Code Review Strict

Acceptance:

```text
review_status = pass
P0 = 0
P1 = 0
```

Input:

* Exact repository、branch、SHA/tree
* Requirement、Design、Plan、handoff
* Exact diff
* 13 rows individual RED
* Row 12 entry evaluator REDとnode GREEN
* 14 active rows GREEN
* Row 2 successor GREEN
* Dogfood/protected-data evidence
* Ledger preservation
* Exact full verifier
* No-touch proof

### 29.2 Final Quality Gate Strict v2

Acceptance:

```text
status = pass
coverage_complete = true
P0 = 0
P1 = 0
unreviewed_areas = []
unresolved_items = []
```

Finding修正でcommitが変わった場合、過去receiptを破棄し、すべてをnew SHA/treeへ再束縛する。

## 30. PR preparation boundary

### 30.1 PR未許可

`PR_PREPARE_AUTHORIZED=false`の場合、review済みcandidateを返して停止する。

### 30.2 PR許可あり

PRは次へ固定する。

```text
head = iss-00395-regression-baseline-terminalization-and-product-defect-repair
base = codex/epic-00384-provider-test-strategy-planning
```

PR作成または更新前に確認する。

* PR head SHA = final reviewed `IMPLEMENTATION_SHA`
* PR head tree = final reviewed `IMPLEMENTATION_TREE`
* Exact clean full verifier GREEN
* Code Review Strict pass
* Final Quality Gate pass
* Required Provider CI checks SUCCESS
* Unresolved finding 0

LunaMaxは次を行わない。

* PR merge
* Integration branch direct push
* Main push/merge
* Revert
* Branch protection変更
* Required contexts変更
* Issue #392 close
* Issue #395 close
* Issue #396 start
* New Issue creation
* Automatic rollback

## 31. Required evidence artifacts

`$EVIDENCE_DIR`または承認済みexternal evidence storeへ、次を作成する。

### 31.1 Identity

`identity.json`

Required fields:

```text
repository
branch
integration_branch
p392_sha
p392_tree
elaboration_input_sha
elaboration_input_tree
spec_freeze_sha
spec_freeze_tree
implementation_sha
implementation_tree
```

### 31.2 RED evidence

Initial-spec-freeze mode creates the RED files below. Post-U05 mode references the prior immutable evidence root and hashes supplied in packet v3; D1R verifies them and does not copy the files or rerun repaired nodes.

* `individual-red-summary.json`
* `row-01-red-observation.json`
* `row-03-red-observation.json`
* `row-04-red-observation.json`
* …
* `row-15-red-observation.json`
* Raw logs
* Raw log SHA-256
* Observation SHA-256

Raw logsはprivateに保持し、distribution evidenceにはsanitized summaryとhashだけを載せる。

### 31.3 GREEN evidence

* Row-specific GREEN observations
* `pre-ledger-all-15-observation.json`
* `post-ledger-all-15-observation.json`
* Dogfood parity observation

### 31.4 Ledger evidence

* `ledger-before.json`
* `ledger-after.json`
* `ledger-invariant.json`

`ledger-invariant.json`には次を記録する。

```text
total = 15
active = 0
resolved = 15
fixed_in_place = 14
superseded = 1
approved = 0
unexpected = 0
row_2_preserved = true
top_level_historical_fields_preserved = true
```

### 31.5 Protected-data evidence

* `protected-before.json`
* `protected-after.json`
* Equality result
* Both skill `SKILL.md` hashes

### 31.6 Dogfood evidence

* `dogfood-update.json`
* Old digest
* New digest
* Digest changed=true
* Provider/dogfood runtime equality
* Ready record
* Both slot markers
* Package parity result

### 31.7 Verifier evidence

各runへ専用rootを使う。

* Entry verifier result
* Working-tree focused/manual diagnostic summary (never a final verifier receipt)
* Exact clean verifier result
* Post-merge verifier result

Distribution summaryには次を記録する。

```text
raw_result_sha256
candidate_sha
status
evaluation
collection_seconds
shard_elapsed_seconds
total_elapsed_seconds
```

Raw private pathを配布用summaryへ含めない。

### 31.8 Command receipts

次のcommandごとに記録する。

```text
command
exit_code
observed_sha
result
artifact_sha256
```

対象:

* Ordinary
* Evaluator unit
* Pre-candidate provider lifecycle unit
* Clean-candidate / post-merge full verifier (single authoritative receipt for the remaining full-regression suites)
* Lint
* SpecDock validate
* Row 3 security matrix
* Row 12 guard
* No-touch checks

### 31.9 Review receipts

* Specification review
* Code Review Strict
* Final Quality Gate Strict

### 31.10 Completion receipt

Working-tree candidate:

```text
candidate_state = working-tree-provisional
merge_ready = false
```

Exact clean reviewed candidate:

```text
candidate_state = clean-pushed-exact
working_tree_clean = true
implementation_sha = non-null
implementation_tree = non-null
merge_ready = true
```

`merge_ready=true`はhuman merge permissionを意味しない。

## 32. Stop conditions

次のいずれかで直ちに停止する。

### 32.1 Identity / permission

* Repository mismatch
* Branch mismatch
* P392 SHA/tree mismatch
* Elaboration SHA/tree mismatch
* Spec freeze SHA/tree mismatch
* Local/upstream/remote mismatch
* Dirty worktree
* Specification receipt missing
* Specification review fail
* P0/P1 nonzero
* Implementation authorization missing
* Concurrent writer present
* Writer assertion expired
* Writer scope incomplete
* Human-merge-only false

### 32.2 Source / baseline drift

* 15 rowsでない
* 14 active / 1 resolvedでない
* Row order drift
* Nodeid drift
* Historical signature drift
* Row 2 drift
* Row 2 successor drift
* Timingが243でない
* Required-fastが4でない
* Verified source blob drift
* Row 12 AST/import boundary drift

### 32.3 RED / GREEN

* Individual REDがexpected first incorrect layerと異なる
* Selected heavy testがskip
* Selected heavy testがxfail/xpass
* Setup/teardown error
* Unexpected failure
* Assertion削除・弱化が必要
* Obsolete API/flag復活が必要
* Row 12 source editが必要
* 15-node normal pass前にledger editが必要

### 32.4 Security

* Credential-bearing read-only originを解決できない
* Publicationがuserinfoを受理する
* Push-only credentialを受理する
* Fetch/push mismatchを受理する
* Credential exposure
* Same-repository validation弱化が必要

### 32.5 Dogfood / lifecycle

* Generated fileの手編集が必要
* Candidate digestが変化しない
* Record/marker digest mismatch
* Version drift
* State/operation/seed-policy drift
* `SKILL.md` drift
* Protected data drift
* Lifecycle source/schema/wire drift
* Unrelated provider-root drift

### 32.6 Ledger / policy

* Historical fields drift
* Row 2 drift
* Top-level historical metadata drift
* Timing変更
* Sharder変更
* Policy hook変更
* Workflow変更
* Skip/xfail追加
* Approved failure追加
* Node rename
* Signature rewrite
* Row delete
* Successor substitution
* Silent retirement

### 32.7 Parent boundary

* #392 lifecycle redesignが必要
* `E384-QUAL-001`変更が必要
* #396 toolingが必要
* Policy retirementが必要
* Required-context transitionが必要
* Main mergeが必要
* New Product/security/policy decisionが必要
* `owner_decisions_required`がnon-emptyになる

## 33. Stop-and-return JSON Schema

停止時は、次のschemaに適合する一つのJSON objectを返す。

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Issue395StopAndReturnV2",
  "type": "object",
  "required": [
    "issue",
    "stage",
    "repository",
    "branch",
    "p392_sha",
    "spec_freeze_sha",
    "observed_head_sha",
    "contract_id",
    "row_ordinal",
    "nodeid",
    "expected",
    "actual",
    "changed_paths",
    "observed_operations",
    "secret_redacted",
    "owner_decision_required",
    "next_check"
  ],
  "properties": {
    "issue": {
      "const": "iss-00395"
    },
    "stage": {
      "enum": [
        "read-only-preflight",
        "entry-verifier",
        "individual-red",
        "mutation-authorization",
        "test-fixture-edit",
        "selection-observer-edit",
        "product-row-3-edit",
        "row-12-guard",
        "pre-ledger-green",
        "dogfood-projection",
        "ledger-transition",
        "working-tree-verification",
        "candidate-freeze",
        "exact-clean-verification",
        "strict-review",
        "pr-preparation",
        "post-merge-b1",
        "post-merge-b2",
        "rollback"
      ]
    },
    "repository": {
      "const": "chemitaro/spec-dock"
    },
    "branch": {
      "const": "iss-00395-regression-baseline-terminalization-and-product-defect-repair"
    },
    "p392_sha": {
      "const": "921bf7512c72bfa2887673cb7ec9bc512cec6ff3"
    },
    "spec_freeze_sha": {
      "type": "string",
      "pattern": "^[0-9a-f]{40}$"
    },
    "observed_head_sha": {
      "type": "string",
      "pattern": "^[0-9a-f]{40}$"
    },
    "contract_id": {
      "type": "string",
      "minLength": 1
    },
    "row_ordinal": {
      "anyOf": [
        {
          "type": "null"
        },
        {
          "type": "integer",
          "minimum": 1,
          "maximum": 15
        }
      ]
    },
    "nodeid": {
      "anyOf": [
        {
          "type": "null"
        },
        {
          "type": "string",
          "pattern": "^tests/.+::.+$"
        }
      ]
    },
    "expected": {
      "type": "string",
      "minLength": 1
    },
    "actual": {
      "type": "string",
      "minLength": 1
    },
    "changed_paths": {
      "type": "array",
      "items": {
        "type": "string",
        "minLength": 1
      },
      "uniqueItems": true
    },
    "observed_operations": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": [
          "operation",
          "result"
        ],
        "properties": {
          "operation": {
            "type": "string",
            "minLength": 1
          },
          "result": {
            "type": "string",
            "minLength": 1
          }
        },
        "additionalProperties": false
      }
    },
    "secret_redacted": {
      "const": true
    },
    "owner_decision_required": {
      "type": "boolean"
    },
    "next_check": {
      "type": "string",
      "minLength": 1
    }
  },
  "additionalProperties": false
}
```

`owner_decision_required=true`の場合は実装を継続しない。

Payloadへ次を含めない。

* Raw credential
* Token
* Username/password
* Userinfoを含むremote URL
* Private absolute path
* Secret-bearing raw log

## 34. Human merge前の境界

LunaMaxのterminal pointは、次のいずれかである。

### 34.1 Working-tree return

```text
implementation_authorized = true
commit_push_authorized = false
candidate_state = working-tree-provisional
merge_ready = false
```

### 34.2 Clean pushed candidate return

```text
implementation_authorized = true
commit_push_authorized = true
candidate_state = clean-pushed-exact
implementation reviews = pass
merge_ready = true
human merge = not performed
```

`merge_ready=true`でも、LunaMaxはmergeしない。

Human merge前に必要なもの:

* Final PR head SHA/tree
* Exact full verifier GREEN
* Provider CI `provider-tests` SUCCESS
* Provider distribution parity Ubuntu SUCCESS
* Provider distribution parity macOS SUCCESS
* Code Review Strict pass
* Final Quality Gate pass
* Unresolved findings 0

## 35. Human merge後の境界

Post-merge verificationはLunaMax implementation taskには含めない。Codex/human gateへのhandoffとする。

### 35.1 Integration tip固定

```bash
set -euo pipefail
umask 077

git fetch --prune origin
git checkout --detach "origin/$INTEGRATION_BRANCH"

export POST_395_MERGE_SHA="$(git rev-parse HEAD)"
export POST_395_MERGE_TREE="$(
  git rev-parse 'HEAD^{tree}'
)"

test -z "$(
  git status --porcelain=v1 --untracked-files=all
)"

test "$(
  git ls-remote \
    --heads \
    origin \
    "refs/heads/$INTEGRATION_BRANCH" \
    | awk 'NF {print $1}'
)" = "$POST_395_MERGE_SHA"
```

PR head treeとpost-merge integration treeが一致しなければ、PR-head CIをB1 evidenceとして再利用しない。

### 35.2 B1

同じexact merged SHA/tree上で次を実行する。

* Ordinary lane (default policy behavior)
* Current full verifier (includes provider lifecycle, distribution, platform/coordination, packaged distribution, and dogfood pytest nodes)
* Row 3 security matrix
* Row 12 guard
* Protected-data proof
* Lint
* SpecDock validate

B1 acceptance:

```text
required PR gates = success
ordinary = green
full verifier = verified
full-regression categories = covered by the full verifier receipt
row 3 security matrix = green
row 12 guard = green
protected data = unchanged
lint and SpecDock validate = green
unexpected failure = 0
same merged SHA/tree = unchanged
```

### 35.3 B2

B1と同じSHA/treeで次を確認する。

```text
total = 15
active = 0
resolved = 15
fixed_in_place = 14
superseded = 1
approved = 0
unexpected = 0
timing = 243
row_2_preserved = true
historical_fields_preserved = true
```

B1とB2を別commitへ分割しない。

### 35.4 Closure boundary

B1後:

* Human/Codex operationとして#392 closureを判断できる。

B2後:

* Human/Codex operationとして#395 finishを判断できる。
* #396 startを判断できる。

LunaMaxはこれらを実行しない。

## 36. Rollback boundary

### 36.1 Human merge前

Issue branch candidateをabandonまたは修正する。Integration branchへ次を部分導入しない。

* Ledgerだけ
* Productだけ
* Testsだけ
* Generated mirrorだけ
* Record/markersだけ

### 36.2 Human merge後、#396開始前

B1またはB2が失敗した場合、Humanが次のどちらかを選ぶ。

1. Whole Issue #395 merge revertでP392へ戻す。
2. Issue #395 owned boundary内でforward-fixし、new exact tipでB1/B2を完全再実行する。

LunaMaxはrevertを実行・pushしない。

### 36.3 #396開始後

#396 workを停止・保存する。Humanがsuffix dispositionを決定するまで#395をrevertしない。Accepted suffixを戻す場合はreverse dependency orderで扱う。

### 36.4 禁止rollback

* Ledger-only rollback
* Product-only rollback
* Test-only rollback
* Generated-mirror-only rollback
* Automatic rollback
* Old API fallback
* Retired flag fallback
* Force push
* Human判断前のhistory rewrite

## 37. Terminal return checklist

LunaMaxはCodexへ次を返す。

1. Repository、branch
2. P392 SHA/tree
3. Elaboration SHA/tree
4. Spec freeze SHA/tree
5. Working-tree diff SHA-256
6. Commit/push許可時のimplementation SHA/tree
7. Exact changed files focused 26件（post-U05ではcanonical 6 pathsとimplementation scopeを実測）
8. Exact changed symbols
9. 13 rowsのindividual RED
10. 13 rowsのGREEN
11. Row 12 entry evaluator REDとnode GREEN
12. Row 2 successor GREEN
13. 14-row ledger before/after
14. Historical fields preservation proof
15. Row 3 credential secrecy
16. Publication security matrix
17. Row 12 blob/AST guard
18. Dogfood runtime/record/marker/digest evidence
19. Protected-data equality
20. Exact full-verifier result SHA-256
21. Ordinary/lifecycle/platform/package/dogfood results
22. Lint result
23. SpecDock validate result
24. Timing 243 / required-fast 4
25. Policy/workflow/lifecycle no-touch
26. Code Review Strict receipt
27. Final Quality Gate receipt
28. Unresolved findings
29. Stop conditionの有無
30. `merge_ready`
31. Rollback readiness

LunaMaxは、人間merge、Issue closure、#396 start、policy retirement、required-context transition、main mergeを行わない。

## 38. Completion state

本handoffの作成・採用自体は、実装許可を変更しない。現在の `implementation_allowed=true` は、ユーザーの明示dispatchをcanonical R/D/Pと整合させて記録した値である。

```text
implementation_allowed = true
owner_decisions_required = []
human_merge_only = true
```

実効的な実装開始は、修正後のexact clean spec freeze、independent fresh spec review pass、P0/P1=0、explicit implementation authorization、scoped concurrent-writer absenceがすべて成立した後だけである。support-history 16件はimmutable、non-authoritativeであり、current specification packはexact 6 pathsのまま維持する。
