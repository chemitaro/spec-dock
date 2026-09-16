---

kind: "corrected-plan"
issue: "iss-00395"
title: "Issue #395 LunaMax-ready Execution Plan"
artifact_path: "plan.md"
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
planning_level: "implementation-ready-after-adoption-review-and-dispatch"
implementation_allowed: true
owner_decisions_required: []
human_merge_only: true
authority: "advisory-corrected-plan"
---

# Issue #395 LunaMax-ready Execution Plan

## 1. 実行原則

本書はIssue #395の完全な実装順序、検証ゲート、証拠形式および停止条件を固定する。ユーザーの明示承認により、canonical statusの`implementation_allowed`はtrueである。ただし、実行者は最初のmutation前にPhase Eのexecution packet検証、exact identity、独立レビュー証跡、同時書き込みなしの確認を満たさなければならない。

GPT-5.6 LunaMaxは、両modeでPhase A〜Cのread-only preflightを実行できる。`initial-spec-freeze`ではD1の初回entry observationまで、`post-u05-checkpoint`ではD1Rのterminal-state entry proofまでがread-only preflightである。Issue #392 boundary witnessの文書SHA結合を除去する変更は、仕様レビュー前の同期ではなく、Strict仕様レビューpass後の通常の実装トラックで行う。次の操作は、Phase Eのexecution packet検証と同時書き込みなしの確認が成立するまで禁止する。

* Product sourceの編集
* regression testの編集
* `full-regression-ledger.json`の編集
* dogfood update
* tracked fileのstage
* commitまたはpush
* Pull Requestの作成または更新
* integration branchまたはmainへの変更
* Issue close、merge、revert、#396 start

すべてのcommandはrepository rootで、同じBash session内において実行する。一つでもassertionが失敗した場合は直ちに停止する。次によって失敗を回避してはならない。

* reset、force checkout、force push
* default branchまたは別branchへのfallback
* expected valueの現場合わせ
* assertionの削除または弱化
* skip、xfail、approved failureの追加
* node rename、signature rewrite、row削除
* obsolete APIまたはretired CLI flagの復活
* 推測による別設計の採用

### 1.1 Issue #392境界テストの独立性

`tests/integration/test_issue_392_acceptance.py`は、P392 entry SHA `921bf7512c72bfa2887673cb7ec9bc512cec6ff3`のimmutable `full-regression-ledger.json` blobと、Issue #392のbaseline、timing、required-fast、policy、workflow、boundary assertionを検証する独立したwitnessである。Issue #395/396のcanonical document SHAをProduct regression gateへ同期しない。

必要なtest-surface整理として、`_ISSUE_BOUNDARY_SHA256`からIssue #395/396文書の固定値照合を取り除くことは許可する。これは#392のassertionを削除・弱化・skip・xfail化せず、文書更新をIssue #392のProduct gateへ結合しないための最小変更である。Issue #395の15/0/15は、Issue #395のledger observerとfull verifierで検証する。

### 1.2 仕様訂正トラックとcheckpoint再開モード

最新のStrict仕様レビューがP0/P1を返した場合、まず`documentation-correction`として本Plan、Design、Requirement、および実装handoff/guide/manifestの契約だけを訂正する。このトラックではProduct、test、ledger、dogfood、evaluator、verifierを変更せず、実装許可済みの実装トラックへ進まない。訂正後のclean pushed SHAを同じ仕様レビューへ再投入し、`review_status=pass`、P0=0、P1=0になった後にだけ、以下の実装トラックを再開する。

実装トラックには二つのidentity modeがある。

* **`initial-spec-freeze`:** `SPEC_FREEZE_SHA/TREE`がcurrent local `HEAD`、configured upstream、Issue branchのremote tipであり、cleanであることを確認してから最初のmutationを行う。
* **`post-u05-checkpoint`:** `SPEC_FREEZE_SHA/TREE`をreviewed specificationのauthorityおよびcurrent local `HEAD`、configured upstream、Issue branchのremote tipの一致対象とする。実行packetが渡す`RESUME_CHECKPOINT_SHA/TREE`はU05後の既存clean実装candidateを表す祖先のresume基点として別に検証し、current tipの一致対象にはしない。U05が既に完了していること、current root ledgerがterminalizedであること、L1を再実行しないことを確認する。仕様訂正後のcurrent tipがcleanで必要な実装差分を既に含む場合は、空のcommitを作らず、そのcurrent tipを`IMPLEMENTATION_SHA/TREE`へadoptできる。新しい差分がある場合だけ、allowed implementation pathsの範囲でforward commitを作る。

`SPEC_FREEZE_SHA`をoriginal specification、resume checkpoint、pre-push current candidateの三つの意味で再利用してはならない。reset、rebase、stash、alternate index、force push、U05 transitionの再実行で古いidentityを作り直すことは禁止する。

## 2. 固定定数とnode集合

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
export PREVIOUS_SPEC_CANDIDATE_SHA="78d6406ba7df8bd4953f2c3f6db5610d635ff48c"

export RESUME_MODE="${RESUME_MODE:-initial-spec-freeze}"
case "$RESUME_MODE" in
  initial-spec-freeze) ;;
  post-u05-checkpoint)
    : "${RESUME_CHECKPOINT_SHA:?RESUME_CHECKPOINT_SHA is required}"
    : "${RESUME_CHECKPOINT_TREE:?RESUME_CHECKPOINT_TREE is required}"
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
ISSUE_392_BOUNDARY_TEST='tests/integration/test_issue_392_acceptance.py::test_t14_transitional_gates_baseline_and_issue_boundary_are_unchanged'

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

SPEC_PACK_PATHS=(
  spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/requirement.md
  spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/design.md
  spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/plan.md
  spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/artifacts/iss-00395-luna-max-implementation-handoff.md
  spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/artifacts/iss-00395-human-guide.html
  spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/artifacts/iss-00395-chatgpt-spec-pack-manifest.md
)

PRESERVED_SUPPORT_HISTORY_PATHS=(
  spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/artifacts/design-luna-max-ready.md
  spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/artifacts/iss-00395-design-tdd-ready.md
  spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/artifacts/iss-00395-lunamax-handoff-tdd-ready.md
  spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/artifacts/iss-00395-plan-review-analysis.md
  spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/artifacts/iss-00395-plan-tdd-ready.md
  spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/artifacts/iss-00395-requirement-tdd-ready.md
  spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/artifacts/iss-00395-spec-pack.zip
  spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/artifacts/iss-00395-tdd-ready-manifest.md
  spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/artifacts/iss-00395-tdd-ready-pack.receipt.md
  spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/artifacts/iss-00395-tdd-ready-pack.zip
  spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/artifacts/luna-max-implementation-handoff-ready.md
  spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/artifacts/luna-max-readiness-analysis.md
  spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/artifacts/luna-max-readiness-manifest.md
  spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/artifacts/luna-max-readiness-pack.receipt.md
  spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/artifacts/luna-max-readiness-pack.zip
  spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/artifacts/plan-lunamax-ready.md
)
```

## 3. Test lane契約

`tests/conftest.py`は、原則として次をfull-regression laneへ分類する。

* `tests/cli_runtime/`
* `tests/integration/`
* `tests/manual_tests/`
* `tests/unit/infra/test_init_update.py::`配下のheavy node

`--run-full-regression`なしでは、それらのtest bodyはpolicy skipされる。したがって、exit 0だけではGREENを意味しない。

本Planでは次を固定する。

1. Ordinary laneは次で実行する。

   ```bash
   uv run pytest
   ```

   このlaneのcurrent policy skipは意図した現行動作として保持する。

2. `tests/cli_runtime/`または`tests/integration/`のpath/nodeを直接選択するすべてのcommandに、次の両方を必ず付ける。

   ```text
   --run-full-regression --full-regression-shard
   ```

3. Heavy testの受入条件は、exit 0ではなく、observation JSONで対象nodeが次を満たすことである。

   * collected exactly once
   * executed exactly once
   * outcome `passed`
   * failure signatureなし
   * skip、xfail、xpass、errorなし

4. Current full verifierをmerge-blocking evidenceとして扱う場合は、clean committed candidateからprivate artifact rootを明示して実行する。共有された`spec-dock/.workbench/full-regression`から「最新run」を推測してはならず、working treeではfocused/manual diagnosticに限定する。

## 4. Phase A — private evidence workspace

予測可能な共有pathへlogやverifier artifactを書かない。Evidenceはrepository外へ置く。

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
test "$REPO_ROOT" = "$PWD"

BASE_TMP="${TMPDIR:-/tmp}"
test -d "$BASE_TMP"
test -w "$BASE_TMP"

export EVIDENCE_DIR="$(mktemp -d "${BASE_TMP%/}/iss-00395.XXXXXXXX")"
export TEST_TMPDIR="$EVIDENCE_DIR/tmp"
mkdir -p "$TEST_TMPDIR"

python - "$REPO_ROOT" "$EVIDENCE_DIR" <<'PY'
from pathlib import Path
import sys

repository = Path(sys.argv[1]).resolve()
evidence = Path(sys.argv[2]).resolve()

assert evidence != repository
assert repository not in evidence.parents

print(f"private-evidence-root={evidence}")
PY
```

以降のtest commandには原則として次を使用する。

```bash
env TMPDIR="$TEST_TMPDIR"
```

Raw log、absolute private path、credential-bearing outputは配布用evidenceへ転載しない。

## 5. Phase B — read-only repository / specification preflight

### B1. Specification and resume identity

Read-only preflightであっても、dispatchはadopt済みclean pushed identityを明示しなければならない。`SPEC_FREEZE_SHA/TREE`はreviewed specificationのauthorityであり、両modeでcurrent tip equalityの対象である。`post-u05-checkpoint`の`RESUME_CHECKPOINT_SHA/TREE`は、そのcurrent tipへ至る既存実装の祖先基点であり、別のidentityとして検証する。

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

### B2. Repository、branch、upstream、remote、ancestry、clean status

```bash
git fetch --prune origin

test "$(git rev-parse --show-toplevel)" = "$PWD"
test "$(git rev-parse --abbrev-ref HEAD)" = "$ISSUE_BRANCH"
test "$(git rev-parse HEAD)" = "$EXPECTED_CURRENT_SHA"
test "$(git rev-parse 'HEAD^{tree}')" = "$EXPECTED_CURRENT_TREE"

test "$(git rev-parse '@{upstream}')" = "$EXPECTED_CURRENT_SHA"
test "$(git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}')" = "origin/$ISSUE_BRANCH"

REMOTE_LINE="$(git ls-remote --heads origin "refs/heads/$ISSUE_BRANCH")"
test "$(printf '%s\n' "$REMOTE_LINE" | awk 'NF {count++} END {print count+0}')" -eq 1
test "$(printf '%s\n' "$REMOTE_LINE" | awk 'NF {print $1}')" = "$EXPECTED_CURRENT_SHA"

test -z "$(git status --porcelain=v1 --untracked-files=all)"

git merge-base --is-ancestor "$P392_SHA" "$ELABORATION_INPUT_SHA"
git merge-base --is-ancestor "$ELABORATION_INPUT_SHA" "$SPEC_FREEZE_SHA"
git merge-base --is-ancestor "$SPEC_FREEZE_SHA" "$EXPECTED_CURRENT_SHA"

if [ "$RESUME_MODE" = "post-u05-checkpoint" ]; then
  git merge-base --is-ancestor "$RESUME_CHECKPOINT_SHA" "$SPEC_FREEZE_SHA"
  test "$(git rev-parse "$RESUME_CHECKPOINT_SHA^{tree}")" = \
    "$RESUME_CHECKPOINT_TREE"
fi

test "$(git rev-parse "$P392_SHA^{tree}")" = "$P392_TREE"
test "$(git rev-parse "$ELABORATION_INPUT_SHA^{tree}")" = "$ELABORATION_INPUT_TREE"
```

`post-u05-checkpoint`では、U05の承認済み遷移が`RESUME_CHECKPOINT_SHA`の履歴に既に存在することを別途確認し、L1を再実行しない。current `HEAD`は`SPEC_FREEZE_SHA`に一致し、resume checkpointからcurrent spec-review targetまでの差分はB5でcanonical-document-onlyと検証する。`initial-spec-freeze`では、従来どおりspec freezeから実装を開始する。

一つでも失敗した場合、Product/test/ledger/dogfood変更0で停止する。

### B3. Origin repository identity

Production code is the single source of truth for repository parsing. The preflight calls the shipped fetch-only resolver and compares its normalized slug with `EXPECTED_REPOSITORY`; it does not contain a second `urlsplit`/regex parser. Publication strictness is exercised only by the existing publication endpoint and the create-boundary tests.

```bash
env PYTHONPATH=src/spec_dock/assets/spec_dock/scripts \
  uv run python - "$EXPECTED_REPOSITORY" <<'PY'
from pathlib import Path
import sys

from spec_dock_runtime.infra.git_cli import origin_github_repo_slug

repository = Path.cwd()
expected = sys.argv[1].lower()
actual = origin_github_repo_slug(repository)
assert actual == expected, {
    "expected": expected,
    "actual": actual or "unresolved",
}
print(f"repository-identity={actual}")
PY
```

### B4. P392からelaboration inputまでのexact差分

```bash
python - "$P392_SHA" "$ELABORATION_INPUT_SHA" <<'PY'
from pathlib import Path
import subprocess
import sys

base, head = sys.argv[1:]

epic = Path(
    "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/"
    "epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction"
)

expected = {
    str(epic / "plan.md"),
    str(
        epic
        / "issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/report.md"
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

Product、test、ledger、timing、policy、workflowがこの差分へ含まれていた場合は停止する。

### B5. Elaboration inputからspec freezeまでのspecification admission history

```bash
python - "$RESUME_MODE" "${RESUME_CHECKPOINT_SHA:-}" \
  "${RESUME_CHECKPOINT_TREE:-}" "$SUPPORT_HISTORY_SHA" "$SPEC_FREEZE_SHA" \
  "$PREVIOUS_SPEC_CANDIDATE_SHA" "${SPEC_PACK_PATHS[@]}" -- \
  "${PRESERVED_SUPPORT_HISTORY_PATHS[@]}" <<'PY'
from pathlib import Path
import subprocess
import sys

mode, resume_checkpoint, resume_tree, support_history, spec_freeze, previous_candidate, *paths = sys.argv[1:]
separator = paths.index("--")
primary_paths = set(paths[:separator])
support_paths = set(paths[separator + 1:])

issue = Path(
    "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/"
    "epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/"
    "issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair"
)

def changed_paths(base, head):
    return set(
        subprocess.check_output(
            ["git", "diff", "--name-only", "--no-renames", base, head, "--"],
            text=True,
        ).splitlines()
    )

assert subprocess.check_output(
    ["git", "merge-base", "--is-ancestor", support_history, spec_freeze],
    text=True,
    stderr=subprocess.DEVNULL,
) == ""

assert primary_paths == {
    str(issue / "requirement.md"),
    str(issue / "design.md"),
    str(issue / "plan.md"),
    str(issue / "artifacts/iss-00395-luna-max-implementation-handoff.md"),
    str(issue / "artifacts/iss-00395-human-guide.html"),
    str(issue / "artifacts/iss-00395-chatgpt-spec-pack-manifest.md"),
}

if mode == "initial-spec-freeze":
    assert changed_paths(support_history, spec_freeze) == primary_paths, {
        "stage": "support-history-checkpoint-to-spec-freeze",
        "expected": sorted(primary_paths),
        "actual": sorted(changed_paths(support_history, spec_freeze)),
    }
    assert changed_paths(previous_candidate, spec_freeze) == primary_paths
elif mode == "post-u05-checkpoint":
    assert resume_checkpoint and len(resume_checkpoint) == 40
    assert len(resume_tree) == 40
    subprocess.run(
        ["git", "merge-base", "--is-ancestor", resume_checkpoint, spec_freeze],
        check=True,
    )
    assert subprocess.check_output(
        ["git", "rev-parse", f"{resume_checkpoint}^{{tree}}"],
        text=True,
    ).strip() == resume_tree
    assert changed_paths(resume_checkpoint, spec_freeze) <= primary_paths, {
        "stage": "resume-checkpoint-to-reviewed-specification",
        "allowed": sorted(primary_paths),
        "actual": sorted(changed_paths(resume_checkpoint, spec_freeze)),
    }
else:
    raise AssertionError(f"unsupported resume mode: {mode}")

support_changes = changed_paths(support_history, spec_freeze) & support_paths
assert not support_changes, {
    "stage": "support-history-no-diff",
    "changed": sorted(support_changes),
}

for path in sorted(primary_paths):
    candidate = Path(path)
    assert candidate.is_file(), path
    assert candidate.stat().st_size > 0, path

print(f"canonical-spec-admission-ok mode={mode}; support-history-nonblocking=true")
PY
```

`SPEC_PACK_PATHS`はhuman guideを含む6件のcurrent canonical specification packである。`IMPLEMENTATION_PATHS`は実装candidateのfocused path setであり、`PRESERVED_SUPPORT_HISTORY_PATHS`は履歴として参照できるがcurrent authorityではない。B5はcurrent canonical packの差分とsupport historyのno-diffだけを確認し、support historyのmode、object type、Git object ID一致や、22/19-path累積allowlistを実装開始の条件にしない。support historyのedit、delete、rename、copy substitution、regenerate、recompress、新規追加がcurrent candidateに含まれる場合だけ、no-diff違反として停止する。

### B6. Active state、managed metadata、SpecDock validation

```bash
./spec-dock/scripts/spec-dock active show \
  | tee "$EVIDENCE_DIR/active-show.txt"

grep -F 'iss-00395' "$EVIDENCE_DIR/active-show.txt"

python - <<'PY'
from pathlib import Path
import json

path = Path(
    "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/"
    "epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/"
    "issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/"
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

grep -F 'spec-dock: ok (validate) nodes=236' \
  "$EVIDENCE_DIR/spec-freeze-validate.txt"
```

Preflightを通すために次を行ってはならない。

* `active set`
* `issue start`
* `.meta.json`の手編集
* active pointerの手編集
* dependency storageの手編集
* generated index/tree/diagramの手編集

## 6. Phase C — exact source、baseline、policy guard

### C1. Exact source blob guard

`initial-spec-freeze`では、`SPEC_FREEZE_SHA`において、次のProduct/test/ledger/policy/workflow blobsがelaboration inputと一致しなければならない。`post-u05-checkpoint`では、同じno-touch面が`RESUME_CHECKPOINT_SHA`と`SPEC_FREEZE_SHA`の間で一致し、仕様訂正が実装candidateを変更していないことを検証する。post-U05でP392前のledger blobをcurrent spec freezeへ再適用してはならない。

```bash
if [ "$RESUME_MODE" = "initial-spec-freeze" ]; then
python - "$SPEC_FREEZE_SHA" <<'PY'
import subprocess
import sys

sha = sys.argv[1]

expected = {
    "full-regression-ledger.json":
        "f181fd3098ef0cba8d0d17e47d00ea12fbbeb8b5",
    "full-regression-timing-weights.json":
        "bdeeb6238609c38085aaed8023b78319a3dd0c6d",
    "tests/conftest.py":
        "d574c3a3e7a09c34f708c576a3b41a3b35772072",
    "scripts/quality/verify_full_regression.py":
        "d01045add90b6e98b58fd210d2ade0d340f7b576",
    "tests/cli_runtime/test_delete.py":
        "3d694fdba352abea454b536b8d108e55e659aa49",
    "tests/cli_runtime/test_import.py":
        "79c6a1eb25c928b447516213833e28e6af506a1b",
    "tests/cli_runtime/test_runtime_import_s10.py":
        "6a68212573cdbecea8496e74fd5be8fcd67400c1",
    "tests/cli_runtime/test_runtime_shell_s11.py":
        "0960800ec3eb183fd2cabcf2a90a9fd220c0a62d",
    "tests/cli_runtime/test_sync.py":
        "1f99b54b9edf2edde150ea64a9d3d6bdc6958397",
    "tests/cli_runtime/test_workbench.py":
        "d86c3a8dc62014c9607f9474f076300b0fe3d8c9",
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py":
        "b0e34dffb3650e7cb3d202e1db243e4c75fea341",
    "spec-dock/scripts/spec_dock_runtime/infra/git_cli.py":
        "b0e34dffb3650e7cb3d202e1db243e4c75fea341",
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py":
        "c967fcd279d628bf3c98b1795ebd090eda5fb959",
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py":
        "bc64a84f15b1176cb077c320c5fd5e7cb924589d",
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/artifacts.py":
        "9f62ddf799f22910efeda5eebb4ba41e775241ac",
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py":
        "129380b6a0b24e111650b264afe78596a26c8a8a",
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py":
        "ef8900a71f10df4559f2290c730f032b6d306d73",
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/template_scaffolder.py":
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
    "full-regression-ledger.json",
    "full-regression-timing-weights.json",
    "tests/conftest.py",
    "scripts/quality/full_regression_baseline.py",
    "scripts/quality/verify_full_regression.py",
    "tests/unit/test_full_regression_baseline.py",
    ".github/workflows/provider-ci.yml",
    ".github/workflows/provider-full-regression.yml",
    "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py",
    "spec-dock/scripts/spec_dock_runtime/infra/git_cli.py",
    "spec-dock/spec-dock.version",
    ".agents/skills/spec-dock/.spec-dock-provider-slot.json",
    ".agents/skills/spec-dock-grill-with-docs/.spec-dock-provider-slot.json",
    "tests/cli_runtime/test_delete.py",
    "tests/cli_runtime/test_import.py",
    "tests/cli_runtime/test_runtime_import_s10.py",
    "tests/cli_runtime/test_sync.py",
    "tests/cli_runtime/test_workbench.py",
    "tests/unit/test_provider_test_lanes.py",
    "tests/integration/test_issue_392_acceptance.py",
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

Blob driftがある場合は、仕様入力と実装対象が一致していないため変更0で停止する。

### C2. Immutable pre-transition ledger evidence

`ledger-before.json`は作業ツリーの現行rootをコピーして作らない。P392 entryのimmutable Git blobをhistorical beforeとして再構築し、U05遷移前のcurrent rootまたはU05後のcurrent rootを、実行フェーズに応じたafterとして別に検証する。U05後のcheckpointから再開する場合、ledger transition writeを再実行せず、P392 beforeとcurrent root afterの保存証明だけを実施する。

```bash
git show \
  "$P392_SHA:full-regression-ledger.json" \
  > "$EVIDENCE_DIR/ledger-before.json"

python - "$EVIDENCE_DIR/ledger-before.json" <<'PY'
from pathlib import Path
import hashlib
import json
import sys

path = Path(sys.argv[1])
raw = path.read_bytes()
ledger = json.loads(raw)
rows = ledger["failure_paths"]

expected = [
    (
        "tests/cli_runtime/test_delete.py::TestCliDelete::"
        "test_delete_scrubbed_meta_is_not_reobserved_by_validate_sync_active",
        "0d6c418e8c531ed77662b5bb0f166c6370f1b4d995a1ec6ac23452382c34869f",
        "active",
    ),
    (
        "tests/cli_runtime/test_distribution_cutover.py::"
        "test_s40b_retained_skill_identity_matches_issue359_final_source",
        "8742959a307d18594743f6bec12a056268baab34024279dbeb4e57458b3a7637",
        "resolved",
    ),
    (
        "tests/cli_runtime/test_import.py::TestCliImport::"
        "test_import_accepts_canonical_url_when_origin_is_credentialed_https_remote",
        "f149be56ae07e7b774137b1f8f5912076a82838250be9750c886aca7a8392a5f",
        "active",
    ),
    (
        "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::"
        "test_parent_fallback_regression",
        "3f7d32388f2d60f77ec1740aac53fd6d6481f7cb04ef3f3ae7ef09463a29a980",
        "active",
    ),
    (
        "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::"
        "test_load_active_manifest_chain_regression",
        "55f2d59d2e1ce7b337462feefbde5c5a84423d07f039ff5fb5dd7bc8b10762ce",
        "active",
    ),
    (
        "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::"
        "test_parent_fallback_re_resolves_inside_lock_when_parent_drifts_regression",
        "ab1f703094ed3335d43ff943cb9194266ee2c162758b3c732b47c1c1cee9256a",
        "active",
    ),
    (
        "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::"
        "test_import_numeric_target_uses_resolved_current_repo_slug_for_github_read",
        "ea4df2e82010c5a2058e5bfd5b31bb7ada7f4776f8cff44a2457fb50b8a1df70",
        "active",
    ),
    (
        "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::"
        "test_import_issue_uses_target_repo_slug_for_same_repo_url_when_present",
        "22d80f8db459620d13f14e34c9a7fc2ee60b73f4080ac7d181b3a7c69ab1d4f3",
        "active",
    ),
    (
        "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::"
        "test_import_then_sync_artifact_path_name_content_regression",
        "0dbf9314fa763929461775d43ae3e56c51bddcb742e2e329317736f5b1194ef7",
        "active",
    ),
    (
        "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::"
        "test_post_import_sync_negative_path_regression",
        "541c15d4ba9564d9256cb2651fe180c2e230760c2fa56ecb389f145fb8723d00",
        "active",
    ),
    (
        "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::"
        "test_execute_create_plan_reuse_seam",
        "44894dc46328aad1a9352cb69a93975a99701b9a9e14f8d5c9dc25470dcf6efd",
        "active",
    ),
    (
        "tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::"
        "test_final_api_call_site_and_structural_regression",
        "0c1088f1a15dd18d672fe5707d9add3ffe1593b6ead070d90ba553019c498790",
        "active",
    ),
    (
        "tests/cli_runtime/test_sync.py::TestCliSync::"
        "test_new_and_active_and_sync",
        "f9b206f85a7c0ee352b4019eaed232ee02dcf896c150659fa7e8191f125951a6",
        "active",
    ),
    (
        "tests/cli_runtime/test_sync.py::TestCliSync::"
        "test_sync_emits_tree_puml_ready_board_at_spec_dock_root",
        "3d1b673b92516964bd29b91cf29c8e03c553988dc9e0df7f0a9aee16dc545619",
        "active",
    ),
    (
        "tests/cli_runtime/test_workbench.py::TestCliWorkbench::"
        "test_copied_workbench_readme_and_payloads_remain_opaque_to_runtime_commands",
        "20d53420c38ab501c64346e6e22a0b309b2358191fe74a54ed9c20717ddb09b9",
        "active",
    ),
]

actual = [
    (
        row["nodeid"],
        row["fixed_point_signature_sha256"],
        row["lifecycle"],
    )
    for row in rows
]

assert actual == expected
assert rows[1]["resolution_mode"] == "superseded"
assert rows[1]["successor_nodeid"] == (
    "tests/cli_runtime/test_distribution_cutover.py::"
    "test_s40b_retained_skill_identity_matches_current_provider_and_dogfood"
)

git_blob = hashlib.sha1(
    f"blob {len(raw)}\0".encode("ascii") + raw
).hexdigest()

assert git_blob == "f181fd3098ef0cba8d0d17e47d00ea12fbbeb8b5"

print(
    "ledger-before-sha256="
    f"{hashlib.sha256(raw).hexdigest()} baseline=15/14/1"
)
PY
```

### C3. Required-fast、timing count

```bash
python - <<'PY'
from pathlib import Path
import ast
import json

source = Path("tests/conftest.py").read_text(encoding="utf-8")
tree = ast.parse(source)

required = None

for node in tree.body:
    if not isinstance(node, ast.Assign):
        continue

    if not any(
        isinstance(target, ast.Name)
        and target.id == "REQUIRED_FAST_NODE_IDS"
        for target in node.targets
    ):
        continue

    required = (
        ast.literal_eval(node.value.args[0])
        if isinstance(node.value, ast.Call)
        else ast.literal_eval(node.value)
    )
    break

assert set(required) == {
    "tests/unit/cli/test_cli_smoke.py::TestCliSmoke::"
    "test_active_set_by_id_succeeds_through_runtime_subprocess",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::"
    "test_checked_in_dogfooding_mirror_docs_match_provider_assets",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::"
    "test_issue_68_workflow_seed_matches_repo_root_ci_workflow",
    "tests/unit/infra/test_init_update.py::TestInitUpdate::"
    "test_issue_68_provider_only_workflow_is_not_shipped_via_install_root",
}

timing = json.loads(
    Path("full-regression-timing-weights.json").read_text(encoding="utf-8")
)

assert len(timing["node_seconds"]) == 243

print("required-fast=4 timing=243")
PY
```

## 7. Phase D — entry verifierと最初のRED

### D1. Current full verifier entry observation (`initial-spec-freeze` only)

このD1は、修復前の15 total / 14 active / 1 resolved状態を観測する初回route専用である。`post-u05-checkpoint`ではこのfull verifierを実行せず、初回の11 violations、`active_verified=4`、row 2だけの`resolved_verified`を要求してはならない。post-U05のentryは、次のD1Rでcurrent rootのterminal stateを確認した後、Phase Eへ進む。

Verifier artifact rootは、このrun専用の空directoryとする。

```bash
ENTRY_ARTIFACT_ROOT="$EVIDENCE_DIR/full-entry"
mkdir -p "$ENTRY_ARTIFACT_ROOT"
test -z "$(find "$ENTRY_ARTIFACT_ROOT" -mindepth 1 -print -quit)"

set +e

env TMPDIR="$TEST_TMPDIR" \
  uv run python -m scripts.quality.verify_full_regression \
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

python - "$ENTRY_RESULT" "$SPEC_FREEZE_SHA" <<'PY'
from pathlib import Path
import json
import sys

result = json.loads(
    Path(sys.argv[1]).read_text(encoding="utf-8")
)

assert result["candidate_sha"] == sys.argv[2]
assert result["status"] == "ledger-mismatch"
assert result["evaluation"]["verified"] is False

violations = {
    (item["code"], item["nodeid"])
    for item in result["evaluation"]["violations"]
}

expected = {
    (
        "signature_mismatch",
        "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::"
        "test_parent_fallback_regression",
    ),
    (
        "signature_mismatch",
        "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::"
        "test_load_active_manifest_chain_regression",
    ),
    (
        "signature_mismatch",
        "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::"
        "test_parent_fallback_re_resolves_inside_lock_when_parent_drifts_regression",
    ),
    (
        "signature_mismatch",
        "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::"
        "test_import_numeric_target_uses_resolved_current_repo_slug_for_github_read",
    ),
    (
        "signature_mismatch",
        "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::"
        "test_import_issue_uses_target_repo_slug_for_same_repo_url_when_present",
    ),
    (
        "signature_mismatch",
        "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::"
        "test_import_then_sync_artifact_path_name_content_regression",
    ),
    (
        "signature_mismatch",
        "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::"
        "test_post_import_sync_negative_path_regression",
    ),
    (
        "signature_mismatch",
        "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::"
        "test_execute_create_plan_reuse_seam",
    ),
    (
        "coverage_mismatch",
        "tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::"
        "test_final_api_call_site_and_structural_regression",
    ),
    (
        "signature_mismatch",
        "tests/cli_runtime/test_workbench.py::TestCliWorkbench::"
        "test_copied_workbench_readme_and_payloads_remain_opaque_to_runtime_commands",
    ),
    (
        "unexpected_failure",
        "tests/integration/test_issue_392_acceptance.py::"
        "test_t14_transitional_gates_baseline_and_issue_boundary_are_unchanged",
    ),
}

assert violations == expected
assert len(violations) == 11
assert sum(code == "unexpected_failure" for code, _ in violations) == 1

assert set(result["evaluation"]["active_verified"]) == {
    "tests/cli_runtime/test_delete.py::TestCliDelete::"
    "test_delete_scrubbed_meta_is_not_reobserved_by_validate_sync_active",
    "tests/cli_runtime/test_import.py::TestCliImport::"
    "test_import_accepts_canonical_url_when_origin_is_credentialed_https_remote",
    "tests/cli_runtime/test_sync.py::TestCliSync::"
    "test_new_and_active_and_sync",
    "tests/cli_runtime/test_sync.py::TestCliSync::"
    "test_sync_emits_tree_puml_ready_board_at_spec_dock_root",
}

assert result["evaluation"]["resolved_verified"] == [
    "tests/cli_runtime/test_distribution_cutover.py::"
    "test_s40b_retained_skill_identity_matches_issue359_final_source"
]

assert result["evaluation"]["retired_verified"] == []

print("entry-full-verifier-exact-allowance-ok")
PY
```

`RESUME_MODE=initial-spec-freeze`の受入条件は、現行baselineの診断として計画済みexact 10 violationsと、文書SHA結合を持つIssue #392 boundary witnessの既知の`unexpected_failure` 1件を記録することである。これはまだGREENではなく、boundary witnessの期待値を仕様レビュー前に同期してはならない。Strict仕様レビューpass後の実装トラックで不要な文書SHA結合を除去し、修復後に再実行するEntry verifierの受入条件はexact 10 violations、Extra violation 0、missing violation 0、#392-owned failure 0、unexpected failure 0である。`post-u05-checkpoint`では、このD1の受入条件を適用しない。

### D1R. Post-U05 terminalized entry observation (`post-u05-checkpoint` only)

`RESUME_MODE=post-u05-checkpoint`では、U05後のcurrent rootが既にterminalizedであるため、D1の初回full verifierを実行しない。Phase Eへ進む前に、current ledgerの15/0/15 invariantとmigration observerをread-onlyで確認し、U05 transitionを再実行しない。

```bash
POST_U05_ENTRY_OBS="$EVIDENCE_DIR/post-u05-terminal-entry-observation.json"

python - "$POST_U05_ENTRY_OBS" <<'PY'
from pathlib import Path
import json
import sys

ledger = json.loads(
    Path("full-regression-ledger.json").read_text(encoding="utf-8")
)
rows = ledger["failure_paths"]

assert len(rows) == 15
assert all(row["lifecycle"] == "resolved" for row in rows)
assert sum(
    row.get("resolution_mode") == "fixed-in-place"
    for row in rows
) == 14
assert sum(
    row.get("resolution_mode") == "superseded"
    for row in rows
) == 1
assert not any(row.get("lifecycle") == "active" for row in rows)

Path(sys.argv[1]).write_text(
    json.dumps(
        {
            "schema_version": 1,
            "entry_mode": "post-u05-checkpoint",
            "total": len(rows),
            "active": sum(row["lifecycle"] == "active" for row in rows),
            "resolved": sum(row["lifecycle"] == "resolved" for row in rows),
            "fixed_in_place": sum(
                row.get("resolution_mode") == "fixed-in-place"
                for row in rows
            ),
            "superseded": sum(
                row.get("resolution_mode") == "superseded"
                for row in rows
            ),
        },
        indent=2,
        ensure_ascii=False,
    )
    + "\n",
    encoding="utf-8",
)
print("post-u05-terminal-entry=15/0/15 fixed=14 superseded=1")
PY

env TMPDIR="$TEST_TMPDIR" \
  uv run pytest \
    -q \
    --tb=short \
    tests/unit/test_provider_test_lanes.py::test_full_regression_ledger_migration_preserves_schema1_history
```

このD1Rは、初回D1の11 violationsやfull-verifier `ledger-mismatch` receiptの代替ではない。D1Rとmigration observerがGREENでなければ、E1/E2、N1へ進まず、Product/test/ledger/dogfoodを変更しない。

### D1.1 — Issue #392境界witnessの独立性 (`initial-spec-freeze` only)

前回のspec freeze候補で観測した`ISSUE_392_BOUNDARY_TEST`のSHA不一致は、今回の仕様修正を反映する前の診断証拠として保持する。この節ではtracked fileを編集しない。Strict仕様レビューpass後の実装トラックで、`tests/integration/test_issue_392_acceptance.py`からIssue #395/#396文書の固定SHA照合だけを除去し、P392のimmutable ledger blob、baseline、timing、required-fast、policy、workflow、boundary assertionsは保持する。

この整理は仕様書SHAを更新する同期処理ではなく、Issue #392のProduct gateとIssue #395のcanonical documentを分離するための最小test-surface変更である。変更後は境界テストを`--run-full-regression --full-regression-shard`付きで一度実行し、normal passを記録する。固定SHAの追加更新、baseline assertionの削除・弱化・skip・xfail化、別のProduct gateの追加は行わない。

### D2. Rows 1、3–11、13–15の個別RED (`initial-spec-freeze` only)

この節とD3のnode実行は、Phase Eのmutation authorization後にboundary witness整理を含む実装変更を行い、focused testとEntry verifierの再検証が完了した後に行う。初回D1の後に直ちに実行してはならない。

13 rowsを一件ずつ実行し、各rowの最初の失敗層を独立に確認する。

```bash
python - "$EVIDENCE_DIR" "$TEST_TMPDIR" \
  "$ROW_1" \
  "$ROW_3" \
  "$ROW_4" \
  "$ROW_5" \
  "$ROW_6" \
  "$ROW_7" \
  "$ROW_8" \
  "$ROW_9" \
  "$ROW_10" \
  "$ROW_11" \
  "$ROW_13" \
  "$ROW_14" \
  "$ROW_15" <<'PY'
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

for ordinal, nodeid in zip(ordinals, rows, strict=True):
    observation = evidence / f"row-{ordinal:02d}-red-observation.json"
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

    log.write_text(completed.stdout, encoding="utf-8")

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
    assert value["outcomes"] == {nodeid: "failed"}
    assert nodeid in value["failure_signatures"]

    assert re.search(
        patterns[ordinal],
        completed.stdout,
    ), {
        "row": ordinal,
        "pattern": patterns[ordinal],
    }

    if ordinal == 3:
        assert "token@" not in completed.stdout
        assert "https://token@github.com" not in completed.stdout

    summary.append(
        {
            "ordinal": ordinal,
            "nodeid": nodeid,
            "returncode": completed.returncode,
            "failure_signature": value["failure_signatures"][nodeid],
            "raw_log_sha256": hashlib.sha256(
                log.read_bytes()
            ).hexdigest(),
            "observation_sha256": hashlib.sha256(
                observation.read_bytes()
            ).hexdigest(),
        }
    )

(evidence / "individual-red-summary.json").write_text(
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

次は停止条件である。

* 対象rowがpassする
* skip、xfail、xpassになる
* setup/teardown errorになる
* observationが生成されない
* expected patternと異なる失敗になる
* 対象外nodeが実行される
* credential-bearing URLがlogへ露出する

### D3. Row 12のfirst REDとcurrent node GREEN (`initial-spec-freeze` only)

Row 12のfirst REDは初回D1の`coverage_mismatch`である。Product-boundary node自身は既にnormal passしなければならない。`post-u05-checkpoint`ではD1およびこのinitial RED acquisitionを実行せず、D1Rのterminal-state proofを使用する。

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

python - "$ROW12_ENTRY_OBS" "$ROW_12" <<'PY'
from pathlib import Path
import json
import sys

value = json.loads(
    Path(sys.argv[1]).read_text(encoding="utf-8")
)

nodeid = sys.argv[2]

assert value["collected"] == [nodeid]
assert value["executed"] == [nodeid]
assert value["outcomes"] == {nodeid: "passed"}
assert value["failure_signatures"] == {}

print("row-12-node-pass-active-ledger-red")
PY
```

Nodeが失敗する場合はsource driftとして停止する。Row 12を推測修正してはならない。

## 8. Phase E — mutation authorization gate

`initial-spec-freeze`では、このPhaseを初回D1のread-only観測後、D2/D3のRED確認と最初のfile editに先立って実行する。`post-u05-checkpoint`では、D1Rのterminal-state entry proof後にこのPhaseへ入り、D1、D1.1、D2、D3のinitial routeを実行しない。いずれのmodeでもE1/E2の完了前にtracked file editを行ってはならない。

### E1. 必須environment values

```bash
: "${SPEC_REVIEW_RECEIPT_PATH:?SPEC_REVIEW_RECEIPT_PATH is required}"
: "${SPEC_REVIEW_RECEIPT_SHA256:?SPEC_REVIEW_RECEIPT_SHA256 is required}"

: "${CONCURRENT_WRITER_ASSERTION_PATH:?CONCURRENT_WRITER_ASSERTION_PATH is required}"
: "${CONCURRENT_WRITER_ASSERTION_SHA256:?CONCURRENT_WRITER_ASSERTION_SHA256 is required}"

: "${IMPLEMENTATION_AUTHORIZED:?IMPLEMENTATION_AUTHORIZED is required}"
: "${COMMIT_PUSH_AUTHORIZED:?COMMIT_PUSH_AUTHORIZED is required}"
: "${PR_PREPARE_AUTHORIZED:?PR_PREPARE_AUTHORIZED is required}"
: "${HUMAN_MERGE_ONLY:?HUMAN_MERGE_ONLY is required}"

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

### E2. Review receiptとconcurrent-writer assertion

両receiptはrepository外のimmutable evidence fileである。

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

def load(path: Path, expected_hash: str) -> dict[str, object]:
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == expected_hash
    value = json.loads(raw)
    assert isinstance(value, dict)
    return value

review = load(
    review_path,
    review_hash,
)

assert review == {
    "schema_version": 2,
    "reviewer": "chatgpt-spec-review-strict",
    "repository": repository,
    "branch": branch,
    "target_sha": sha,
    "target_tree": tree,
    "review_status": "pass",
    "p0": 0,
    "p1": 0,
    "receipt_identity": review["receipt_identity"],
}

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

assert isinstance(
    writer["issued_at_utc"],
    str,
)
assert isinstance(
    writer["expires_at_utc"],
    str,
)

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

assert set(writer["scope_paths"]) == implementation_paths

print(
    "mutation-authorized "
    f"review={review['receipt_identity']} "
    f"writer={writer['assertion_id']}"
)
PY

test -z "$(git status --porcelain=v1 --untracked-files=all)"
test "$(git rev-parse HEAD)" = "$EXPECTED_CURRENT_SHA"
test "$(git rev-parse 'HEAD^{tree}')" = "$EXPECTED_CURRENT_TREE"
```

次の場合は変更0で停止する。

* review receiptがない
* receipt hashが一致しない
* review target SHA/treeがspec freezeと異なる
* reviewがpassでない
* P0またはP1がnonzero
* writer assertionがない
* writer assertionがspec freezeに束縛されていない
* writer assertionが期限切れ
* writer scopeが不足
* `IMPLEMENTATION_AUTHORIZED`がtrueでない
* worktreeがdirty
* `initial-spec-freeze`でHEADがspec freezeから動いた
* `post-u05-checkpoint`でHEADがreviewed specification freezeから動いた

Writer assertionは最初のedit直前に再検証する。期限切れのassertionを再利用しない。

### E3. Issue #392境界witness整理の実装境界

Strict仕様レビューpass後、E1/E2がpassし、worktreeがcleanであり、`SPEC_FREEZE_SHA`／`SPEC_FREEZE_TREE`がレビュー対象と一致した後に、通常の実装トラックを開始する。`tests/integration/test_issue_392_acceptance.py`の変更は、Issue #395/#396 canonical documentの固定SHA比較を除去することだけに限定する。P392 entryのimmutable `full-regression-ledger.json` blob、Issue #392のbaseline、timing、required-fast、policy、workflow、boundary assertionsはそのまま保持する。

この整理は仕様書SHAを計算して同期するゲートではない。`initial-spec-freeze`でも`post-u05-checkpoint`でも、同じtest pathを実装candidateのfocused testとして一度だけ実行し、normal passを記録する。仕様レビュー後の作業は、Product修正、必要なtest修正、ledger transition、dogfood projectionを一つの実装計画に従って進める。U05後に既存のledger transitionを再実行しない。

### E4. Post-implementation Entry recheck

Issue #392境界witness整理とProduct/testのfocused修正を行った後、D1のcurrent full verifier commandを新しいprivate artifact rootで再実行する。`candidate_sha`は実装candidate、statusは`ledger-mismatch`、violation setは計画済みexact 10件でなければならない。`active_verified` 4件、row 2の`resolved_verified` 1件、`retired_verified=[]`、`#392-owned failure=0`、`unexpected_failure=0`も確認する。ここを通過して初めて全14 rowsのGREEN観測とledger transitionへ進む。`post-u05-checkpoint`では、既存checkpointのterminal-state/migration evidenceを確認したうえで、U05 transitionを再実行せずに同じentry recheckを適用する。

## 9. Phase F — Rows 4–11 test fixture修正

### F1. Edit boundary

変更対象は次だけである。

```text
tests/cli_runtime/test_runtime_import_s10.py::_StubTemplateScaffolder
```

次を変更してはならない。

* `application/ports.py`
* `application/create_node.py`
* `infra/template_scaffolder.py`
* production `execute_create_plan`
* production descriptor-bound writer

### F2. Required method

`_StubTemplateScaffolder`へ、current portと同じcall shapeのmethodを追加する。

```python
def copy_scaffolded_tree_at(
    self,
    src_dir: Path,
    dest_dir: Path,
    dest_dir_fd: int,
    replacements: dict[str, str],
) -> list[Path]:
    self.events.append("copy_scaffolded_tree_at")
    from spec_dock_runtime.infra import template_scaffolder

    return template_scaffolder.copy_scaffolded_tree_at(
        src_dir,
        dest_dir,
        dest_dir_fd,
        replacements,
    )
```

次を保持する。

* existing `copy_scaffolded_tree`
* existing event assertions
* parent fallback assertions
* active manifest chain assertions
* lock-side parent re-resolution
* numeric target repo slug propagation
* explicit target repo slug propagation
* artifact path/name/content assertions
* post-import sync negative path
* `execute_create_plan` exactly-once seam
* rules symlink assertions
* retired output absence assertions

Verified symbol signatureと上記methodが一致しない場合は停止する。別adapterを推測しない。

### F3. Individual GREEN

```bash
python - "$EVIDENCE_DIR" "$TEST_TMPDIR" \
  "$ROW_4" \
  "$ROW_5" \
  "$ROW_6" \
  "$ROW_7" \
  "$ROW_8" \
  "$ROW_9" \
  "$ROW_10" \
  "$ROW_11" <<'PY'
from pathlib import Path
import json
import os
import subprocess
import sys

evidence = Path(sys.argv[1])
tmpdir = sys.argv[2]
rows = sys.argv[3:]

for ordinal, nodeid in zip(
    range(4, 12),
    rows,
    strict=True,
):
    observation = evidence / (
        f"row-{ordinal:02d}-green-observation.json"
    )

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

    environment = dict(
        os.environ,
        TMPDIR=tmpdir,
    )

    completed = subprocess.run(
        command,
        env=environment,
        check=False,
    )

    assert completed.returncode == 0, {
        "row": ordinal,
        "returncode": completed.returncode,
    }

    value = json.loads(
        observation.read_text(encoding="utf-8")
    )

    assert value["collected"] == [nodeid]
    assert value["executed"] == [nodeid]
    assert value["outcomes"] == {
        nodeid: "passed",
    }
    assert value["failure_signatures"] == {}

print("rows-4-11-green=8/8")
PY
```

受入条件は8件の独立したnormal passである。

## 10. Phase G — Rows 1、13、14、15 selection-only observer修正

### G1. Exact replacements

Product CLIは変更しない。Test observerだけを次のように変更する。

| Row | Path                                  | Before                                 | After                       |
| --: | ------------------------------------- | -------------------------------------- | --------------------------- |
|   1 | `tests/cli_runtime/test_delete.py`    | `active set --id iss-00058 --force`    | `active set --id iss-00058` |
|  13 | `tests/cli_runtime/test_sync.py`      | `active set iss-00003 --force`         | `active set iss-00003`      |
|  14 | `tests/cli_runtime/test_sync.py`      | `active set 305 --force --no-checkout` | `active set 305`            |
|  15 | `tests/cli_runtime/test_workbench.py` | `active set --id scope_id --force`     | `active set --id scope_id`  |

Row 15は`active.json`を読む前にactive commandのreturn code 0をassertする。

次を削除・弱化しない。

* row 1のdeleted metadata非再観測
* row 13のnew/active/sync収束
* row 14のtree、PUML、ready-board content
* row 15のWorkbench README/payload byte opacity
* validate、sync、deps、active前後比較

### G2. Individual GREEN

```bash
python - "$EVIDENCE_DIR" "$TEST_TMPDIR" \
  "$ROW_1" \
  "$ROW_13" \
  "$ROW_14" \
  "$ROW_15" <<'PY'
from pathlib import Path
import json
import os
import subprocess
import sys

evidence = Path(sys.argv[1])
tmpdir = sys.argv[2]
rows = sys.argv[3:]
ordinals = [1, 13, 14, 15]

for ordinal, nodeid in zip(
    ordinals,
    rows,
    strict=True,
):
    observation = evidence / (
        f"row-{ordinal:02d}-green-observation.json"
    )

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

    environment = dict(
        os.environ,
        TMPDIR=tmpdir,
    )

    completed = subprocess.run(
        command,
        env=environment,
        check=False,
    )

    assert completed.returncode == 0, {
        "row": ordinal,
        "returncode": completed.returncode,
    }

    value = json.loads(
        observation.read_text(encoding="utf-8")
    )

    assert value["collected"] == [nodeid]
    assert value["executed"] == [nodeid]
    assert value["outcomes"] == {
        nodeid: "passed",
    }
    assert value["failure_signatures"] == {}

print("selection-rows-green=4/4")
PY
```

## 11. Phase H — Row 3 observerとProduct boundary修正

### H1. Observerを先に強化する

Existing row 3 nodeをrenameせず、success assertionを保持したまま次を追加する。

```python
combined = p.stdout + p.stderr
assert "token" not in combined
assert "https://token@github.com/example/repo.git" not in combined
```

New test nodeやnew ledger rowを追加しない。

### H2. Product edit前のRED再確認

```bash
ROW3_TESTFIRST_OBS="$EVIDENCE_DIR/row-03-test-first-red-observation.json"

set +e

env TMPDIR="$TEST_TMPDIR" \
  uv run pytest \
    --run-full-regression \
    --full-regression-shard \
    --full-regression-observation "$ROW3_TESTFIRST_OBS" \
    -q \
    --tb=short \
    "$ROW_3" \
    >"$EVIDENCE_DIR/row-03-test-first-red.log" \
    2>&1

ROW3_TESTFIRST_RC=$?

set -e

test "$ROW3_TESTFIRST_RC" -eq 1

grep -F \
  'Current GitHub repo scope could not be resolved from origin' \
  "$EVIDENCE_DIR/row-03-test-first-red.log"

! grep -F \
  'token@' \
  "$EVIDENCE_DIR/row-03-test-first-red.log"

! grep -F \
  'https://token@github.com' \
  "$EVIDENCE_DIR/row-03-test-first-red.log"
```

### H3. Product source edit

変更対象はprovider-side sourceの次のexisting symbolsだけである。

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py
```

1. `_parse_github_repo_slug`

   * `_remote_has_userinfo`によるpublication-policy rejectionをidentity parserから除去する。
   * GitHub host/path parsingを維持する。
   * owner/repositoryのnon-empty条件を維持する。
   * lowercase normalized slugだけを返す。
   * raw URLまたはcredentialを返さない。

2. `origin_github_repo_slug`

   * `origin_github_publication_endpoint`を呼ばない。
   * `_remote_get_url(repo_root, push=False)`だけを読む。
   * `_parse_github_repo_slug`の結果をread-only identityとして返す。

3. `origin_github_publication_endpoint`

   * fetch URLとpush URLを読む。
   * parseより前に、fetchまたはpushのuserinfoを明示的に拒否する。
   * diagnosticには必ず`_redact_remote_url`を使用する。
   * fetch/pushの両方がGitHub repository identityへparseできることを要求する。
   * normalized fetch slugとpush slugのexact equalityを要求する。
   * accepted時だけslugとpush URLを返す。

4. 次を変更しない。

   * `_remote_get_url` signature
   * `_remote_has_userinfo` signature
   * `_redact_remote_url` signature
   * `GitGateway.origin_github_repo_slug` signature
   * bootstrap adapter signature
   * application same-repository validation
   * numeric target current-scope requirement
   * foreign repository rejection
   * unrelated Git coordination code

New public function、new port、new request/result type、new CLI flagを追加しない。

### H4. Row 3 GREEN

```bash
ROW3_GREEN_OBS="$EVIDENCE_DIR/row-03-green-observation.json"

env TMPDIR="$TEST_TMPDIR" \
  uv run pytest \
    --run-full-regression \
    --full-regression-shard \
    --full-regression-observation "$ROW3_GREEN_OBS" \
    -q \
    --tb=short \
    "$ROW_3"

python - "$ROW3_GREEN_OBS" "$ROW_3" <<'PY'
from pathlib import Path
import json
import sys

value = json.loads(
    Path(sys.argv[1]).read_text(encoding="utf-8")
)

nodeid = sys.argv[2]

assert value["collected"] == [nodeid]
assert value["executed"] == [nodeid]
assert value["outcomes"] == {
    nodeid: "passed",
}
assert value["failure_signatures"] == {}

print("row-3-green")
PY
```

### H5. Publication security matrix

このdiagnosticは次の三時点で実行する。

1. dogfood projection前
2. exact clean implementation SHA
3. post-merge B1 SHA

```bash
env TMPDIR="$TEST_TMPDIR" \
  PYTHONPATH=src/spec_dock/assets/spec_dock/scripts \
  uv run python - <<'PY'
from pathlib import Path
import subprocess
import tempfile

from spec_dock_runtime.infra.git_cli import (
    origin_github_publication_endpoint,
    origin_github_repo_slug,
)

def run_git(
    repository: Path,
    *arguments: str,
) -> None:
    subprocess.run(
        ["git", *arguments],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    )

def reject_without_secret(
    repository: Path,
    forbidden: tuple[str, ...],
) -> str:
    try:
        origin_github_publication_endpoint(repository)
    except RuntimeError as error:
        text = str(error)
        for fragment in forbidden:
            assert fragment not in text
        return text

    raise AssertionError(
        "publication endpoint unexpectedly accepted"
    )

with tempfile.TemporaryDirectory() as temporary:
    repository = Path(temporary)

    run_git(
        repository,
        "init",
        "-q",
    )

    # Case 1:
    # Credential-bearing fetch URL is accepted for read-only identity,
    # but rejected for publication without credential exposure.
    run_git(
        repository,
        "remote",
        "add",
        "origin",
        "https://token@github.com/Example/Repo.git",
    )

    assert origin_github_repo_slug(
        repository
    ) == "example/repo"

    text = reject_without_secret(
        repository,
        (
            "token@",
            "https://token@github.com",
        ),
    )

    assert "<credential-bearing remote>" in text

    # Case 2:
    # Clean fetch plus credential-bearing push is rejected.
    run_git(
        repository,
        "remote",
        "set-url",
        "origin",
        "https://github.com/Example/Repo.git",
    )

    run_git(
        repository,
        "remote",
        "set-url",
        "--push",
        "origin",
        "https://push-token@github.com/Example/Repo.git",
    )

    text = reject_without_secret(
        repository,
        (
            "push-token@",
            "https://push-token@github.com",
        ),
    )

    assert "<credential-bearing remote>" in text

    # Case 3:
    # Clean fetch/push with different repository identities is rejected.
    run_git(
        repository,
        "remote",
        "set-url",
        "--push",
        "origin",
        "https://github.com/Other/Repo.git",
    )

    text = reject_without_secret(
        repository,
        (),
    )

    assert "fetch/push mismatch" in text
    assert "example/repo" in text
    assert "other/repo" in text

    # Case 4:
    # Clean matching fetch/push succeeds.
    run_git(
        repository,
        "remote",
        "set-url",
        "--push",
        "origin",
        "git@github.com:Example/Repo.git",
    )

    assert origin_github_repo_slug(
        repository
    ) == "example/repo"

    slug, push_url = origin_github_publication_endpoint(
        repository
    )

    assert slug == "example/repo"
    assert push_url == "git@github.com:Example/Repo.git"

print("identity-publication-security-matrix-ok")
PY
```

## 12. Phase I — Row 12 exact no-edit guard

Row 12のProduct/test sourceは変更しない。次を実装前、working-tree verification時、exact clean candidate時、post-merge B1時に実行する。

```bash
python - "$SPEC_FREEZE_SHA" <<'PY'
from pathlib import Path
import ast
import subprocess
import sys

freeze = sys.argv[1]

paths = {
    "new": Path(
        "src/spec_dock/assets/spec_dock/scripts/"
        "spec_dock_runtime/commands/new.py"
    ),
    "contracts": Path(
        "src/spec_dock/assets/spec_dock/scripts/"
        "spec_dock_runtime/application/contracts.py"
    ),
    "domain": Path(
        "src/spec_dock/assets/spec_dock/scripts/"
        "spec_dock_runtime/domain/artifacts.py"
    ),
    "test": Path(
        "tests/cli_runtime/test_runtime_shell_s11.py"
    ),
}

expected_blobs = {
    "new":
        "c967fcd279d628bf3c98b1795ebd090eda5fb959",
    "contracts":
        "bc64a84f15b1176cb077c320c5fd5e7cb924589d",
    "domain":
        "9f62ddf799f22910efeda5eebb4ba41e775241ac",
    "test":
        "0960800ec3eb183fd2cabcf2a90a9fd220c0a62d",
}

for key, path in paths.items():
    current_blob = subprocess.check_output(
        ["git", "hash-object", str(path)],
        text=True,
    ).strip()

    assert current_blob == expected_blobs[key], {
        "path": str(path),
        "actual": current_blob,
    }

    freeze_blob = subprocess.check_output(
        ["git", "rev-parse", f"{freeze}:{path}"],
        text=True,
    ).strip()

    assert freeze_blob == expected_blobs[key]

def imports(path: Path) -> set[tuple[str, str]]:
    tree = ast.parse(
        path.read_text(encoding="utf-8")
    )

    found: set[tuple[str, str]] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            found.update(
                (
                    node.module or "",
                    alias.name,
                )
                for alias in node.names
            )
        elif isinstance(node, ast.Import):
            found.update(
                (
                    alias.name,
                    "",
                )
                for alias in node.names
            )

    return found

new_imports = imports(paths["new"])
contract_imports = imports(paths["contracts"])

assert (
    "spec_dock_runtime.application.contracts",
    "CURRENT_CREATABLE_ARTIFACT_TYPES",
) in new_imports

assert not any(
    module.startswith("spec_dock_runtime.domain")
    for module, _ in new_imports
)

assert not any(
    module.startswith("spec_dock_runtime.infra")
    for module, _ in new_imports
)

assert (
    "spec_dock_runtime.domain.artifacts",
    "CURRENT_CREATABLE_ARTIFACT_TYPES",
) in contract_imports

print("row-12-blob-and-ast-guard-ok")
PY

ROW12_GREEN_OBS="$EVIDENCE_DIR/row-12-green-observation.json"

env TMPDIR="$TEST_TMPDIR" \
  uv run pytest \
    --run-full-regression \
    --full-regression-shard \
    --full-regression-observation "$ROW12_GREEN_OBS" \
    -q \
    --tb=short \
    "$ROW_12"
```

受入条件は次である。

* exact blobs unchanged
* `commands/new.py -> application.contracts -> domain.artifacts`
* commandsからdomain/infraへのdirect importなし
* row 12 normal pass
* Product/test edit 0

## 13. Phase J — ledger変更前の15 node normal pass

14 active historical nodesとrow 2 successorを、global ledger completeness checkを適用しないshard modeで実行する。

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

python - "$PRE_LEDGER_OBS" "${ALL_OBSERVED_ROWS[@]}" <<'PY'
from pathlib import Path
import json
import sys

value = json.loads(
    Path(sys.argv[1]).read_text(encoding="utf-8")
)

expected = list(sys.argv[2:])

assert value["collected"] == expected
assert value["executed"] == expected
assert value["outcomes"] == {
    nodeid: "passed"
    for nodeid in expected
}
assert value["failure_signatures"] == {}

print("pre-ledger-normal-pass=15/15")
PY
```

このproofが通る前にledgerを変更しない。

## 14. Phase K — provider-first dogfood projection

### K1. Source-focused heavy tests

Directly selected heavy testsにはfull-regression permissionを付ける。

```bash
SOURCE_FOCUSED_OBS="$EVIDENCE_DIR/source-focused-observation.json"

env TMPDIR="$TEST_TMPDIR" \
  uv run pytest \
    --run-full-regression \
    --full-regression-shard \
    --full-regression-observation "$SOURCE_FOCUSED_OBS" \
    -q \
    --tb=short \
    tests/cli_runtime/test_import.py \
    tests/cli_runtime/test_runtime_import_s10.py \
    tests/cli_runtime/test_runtime_shell_s11.py

python - "$SOURCE_FOCUSED_OBS" <<'PY'
from pathlib import Path
import json
import sys

value = json.loads(
    Path(sys.argv[1]).read_text(encoding="utf-8")
)

assert value["collected"]
assert value["executed"] == value["collected"]
assert set(value["outcomes"].values()) == {
    "passed",
}
assert value["failure_signatures"] == {}

print(
    f"source-focused-passed={len(value['executed'])}"
)
PY

env TMPDIR="$TEST_TMPDIR" \
  make lint
```

### K2. Protected-data snapshot helper

Helperはprivate evidence directory内だけに作成する。

```bash
cat > "$EVIDENCE_DIR/snapshot_protected.py" <<'PY'
from pathlib import Path
import hashlib
import json
import os
import stat
import sys

root = Path.cwd().resolve()
output = Path(sys.argv[1])

protected = [
    Path("spec-dock/initiatives"),
    Path("spec-dock/Artifacts"),
    Path("Artifacts"),
    Path("spec-dock/.workbench"),
    Path(".workbench"),
    Path(".agents/skills/spec-dock/SKILL.md"),
    Path(
        ".agents/skills/"
        "spec-dock-grill-with-docs/SKILL.md"
    ),
]

def item(path: Path) -> dict[str, object]:
    relative = path.relative_to(root).as_posix()

    try:
        value = os.lstat(path)
    except FileNotFoundError:
        return {
            "path": relative,
            "kind": "absent",
        }

    mode = stat.S_IMODE(value.st_mode)

    if stat.S_ISLNK(value.st_mode):
        return {
            "path": relative,
            "kind": "symlink",
            "mode": mode,
            "target": os.readlink(path),
        }

    if stat.S_ISDIR(value.st_mode):
        return {
            "path": relative,
            "kind": "directory",
            "mode": mode,
        }

    if stat.S_ISREG(value.st_mode):
        raw = path.read_bytes()

        return {
            "path": relative,
            "kind": "file",
            "mode": mode,
            "size": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
        }

    return {
        "path": relative,
        "kind": "other",
        "mode": mode,
        "type": stat.S_IFMT(value.st_mode),
    }

records: list[dict[str, object]] = []

for relative in protected:
    absolute = root / relative

    if not absolute.exists() and not absolute.is_symlink():
        records.append(
            {
                "path": relative.as_posix(),
                "kind": "absent",
            }
        )
        continue

    if absolute.is_dir() and not absolute.is_symlink():
        records.append(item(absolute))

        for current, directories, files in os.walk(
            absolute,
            topdown=True,
            followlinks=False,
        ):
            directories.sort()
            files.sort()
            current_path = Path(current)

            for name in directories + files:
                records.append(
                    item(current_path / name)
                )
    else:
        records.append(item(absolute))

output.write_text(
    json.dumps(
        records,
        indent=2,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)
PY

python "$EVIDENCE_DIR/snapshot_protected.py" \
  "$EVIDENCE_DIR/protected-before.json"

cp spec-dock/spec-dock.version \
  "$EVIDENCE_DIR/record-before.json"
```

### K3. Complete lifecycle update

Generated filesは手編集しない。

```bash
env TMPDIR="$TEST_TMPDIR" \
  uv run spec-dock update . --json \
  > "$EVIDENCE_DIR/dogfood-update.json"
```

Expected:

* exit 0
* canonical JSON object
* status `completed`
* operation `update`
* errors 0
* failed paths 0
* pending paths 0

`completed_with_warnings`は受入れない。

### K4. Projection、digest、protected-data proof

```bash
python "$EVIDENCE_DIR/snapshot_protected.py" \
  "$EVIDENCE_DIR/protected-after.json"

cmp -s \
  "$EVIDENCE_DIR/protected-before.json" \
  "$EVIDENCE_DIR/protected-after.json"

cmp -s \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py \
  spec-dock/scripts/spec_dock_runtime/infra/git_cli.py

python - \
  "$EVIDENCE_DIR/record-before.json" \
  "$EVIDENCE_DIR/dogfood-update.json" <<'PY'
from pathlib import Path
import json
import re
import sys

before = json.loads(
    Path(sys.argv[1]).read_text(encoding="utf-8")
)

result = json.loads(
    Path(sys.argv[2]).read_text(encoding="utf-8")
)

record = json.loads(
    Path(
        "spec-dock/spec-dock.version"
    ).read_text(encoding="utf-8")
)

markers = [
    json.loads(
        Path(
            ".agents/skills/spec-dock/"
            ".spec-dock-provider-slot.json"
        ).read_text(encoding="utf-8")
    ),
    json.loads(
        Path(
            ".agents/skills/"
            "spec-dock-grill-with-docs/"
            ".spec-dock-provider-slot.json"
        ).read_text(encoding="utf-8")
    ),
]

assert result["status"] == "completed"
assert result["operation"] == "update"
assert result["seed_policy"] == "preserve-only"
assert result["errors"] == []
assert result["failed_paths"] == []
assert result["pending_paths"] == []

assert record == {
    "schema_version": 1,
    "state": "ready",
    "operation": None,
    "version": "0.2.4",
    "candidate_digest": record["candidate_digest"],
    "seed_policy": "preserve-only",
    "skill_slots": {
        "spec-dock": "0.2.4",
        "spec-dock-grill-with-docs": "0.2.4",
    },
}

new_digest = record["candidate_digest"]

assert re.fullmatch(
    r"[0-9a-f]{64}",
    new_digest,
)

assert new_digest != before["candidate_digest"]
assert result["candidate_digest"] == new_digest

assert markers == [
    {
        "schema_version": 1,
        "slot": ".agents/skills/spec-dock",
        "version": "0.2.4",
        "candidate_digest": new_digest,
    },
    {
        "schema_version": 1,
        "slot":
            ".agents/skills/spec-dock-grill-with-docs",
        "version": "0.2.4",
        "candidate_digest": new_digest,
    },
]

print(f"dogfood-candidate={new_digest}")
PY
```

### K5. Dogfood parity node — clean candidateでのみ実行

K5はcandidate-wheel、source、sdist、installed、dogfoodの最終parity receiptを生成するため、Phase Kのworking treeでは実行しない。Phase KではK4までのprojection/protected-data proofと、必要なfocused/manual確認だけを行う。K5の次のcommandはPhase N1でclean pushed candidateを確定した後、N2のcurrent full verifierへ一度だけ含める。Phase Kのdirty状態から得た結果をfinal receiptへ転用してはならない。

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

python - "$DOGFOOD_PARITY_OBS" <<'PY'
from pathlib import Path
import json
import sys

value = json.loads(
    Path(sys.argv[1]).read_text(encoding="utf-8")
)

assert len(value["collected"]) == 1
assert value["executed"] == value["collected"]
assert list(value["outcomes"].values()) == [
    "passed",
]
assert value["failure_signatures"] == {}

print("dogfood-parity=passed")
PY
```

次が発生した場合、projection candidateを採用せず停止する。

* `pyproject.toml` version変更
* lifecycle source/schema/wire変更
* two skill `SKILL.md` bytes変更
* initiatives変更
* Workbench変更
* Artifacts変更
* consumer-owned data変更
* active state変更
* ledger変更
* timing変更
* policy変更
* workflow変更
* row 3 runtime mirror以外の意図しないprovider-root変更
* candidate digest不一致
* old digestとnew digestが同一

## 15. Phase L — atomic ledger transition

Phase JとPhase KがGREENになった後だけ実行する。

### L1. Write transition

```bash
python - "$EVIDENCE_DIR/ledger-before.json" <<'PY'
from pathlib import Path
import json
import sys

before_path = Path(sys.argv[1])
ledger_path = Path("full-regression-ledger.json")

before_raw = before_path.read_bytes()
current_raw = ledger_path.read_bytes()

assert current_raw == before_raw, (
    "ledger changed before authorized transition"
)

before = json.loads(before_raw)
expected = json.loads(before_raw)

fixed_in_place = {
    "tests/cli_runtime/test_delete.py::TestCliDelete::"
    "test_delete_scrubbed_meta_is_not_reobserved_by_validate_sync_active",
    "tests/cli_runtime/test_import.py::TestCliImport::"
    "test_import_accepts_canonical_url_when_origin_is_credentialed_https_remote",
    "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::"
    "test_parent_fallback_regression",
    "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::"
    "test_load_active_manifest_chain_regression",
    "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::"
    "test_parent_fallback_re_resolves_inside_lock_when_parent_drifts_regression",
    "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::"
    "test_import_numeric_target_uses_resolved_current_repo_slug_for_github_read",
    "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::"
    "test_import_issue_uses_target_repo_slug_for_same_repo_url_when_present",
    "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::"
    "test_import_then_sync_artifact_path_name_content_regression",
    "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::"
    "test_post_import_sync_negative_path_regression",
    "tests/cli_runtime/test_runtime_import_s10.py::TestRuntimeImportS10::"
    "test_execute_create_plan_reuse_seam",
    "tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::"
    "test_final_api_call_site_and_structural_regression",
    "tests/cli_runtime/test_sync.py::TestCliSync::"
    "test_new_and_active_and_sync",
    "tests/cli_runtime/test_sync.py::TestCliSync::"
    "test_sync_emits_tree_puml_ready_board_at_spec_dock_root",
    "tests/cli_runtime/test_workbench.py::TestCliWorkbench::"
    "test_copied_workbench_readme_and_payloads_remain_opaque_to_runtime_commands",
}

rows = expected["failure_paths"]

assert len(rows) == 15

assert {
    row["nodeid"]
    for row in rows
    if row["lifecycle"] == "active"
} == fixed_in_place

for row in rows:
    if row["nodeid"] not in fixed_in_place:
        continue

    assert row["lifecycle"] == "active"
    assert "resolution_mode" not in row
    assert "successor_nodeid" not in row

    row["lifecycle"] = "resolved"
    row["resolution_mode"] = "fixed-in-place"

ledger_path.write_text(
    json.dumps(
        expected,
        indent=2,
        ensure_ascii=False,
    )
    + "\n",
    encoding="utf-8",
)

print("ledger-transition-written")
PY
```

### L2. Full historical preservation proof

```bash
python - "$EVIDENCE_DIR/ledger-before.json" <<'PY'
from pathlib import Path
import copy
import json
import sys

before = json.loads(
    Path(sys.argv[1]).read_text(encoding="utf-8")
)

after = json.loads(
    Path(
        "full-regression-ledger.json"
    ).read_text(encoding="utf-8")
)

assert set(before) == set(after)

assert {
    key: value
    for key, value in before.items()
    if key != "failure_paths"
} == {
    key: value
    for key, value in after.items()
    if key != "failure_paths"
}

assert len(before["failure_paths"]) == 15
assert len(after["failure_paths"]) == 15

for index, (old, new) in enumerate(
    zip(
        before["failure_paths"],
        after["failure_paths"],
        strict=True,
    ),
    1,
):
    assert old["nodeid"] == new["nodeid"], index

    if index == 2:
        assert old == new
        continue

    expected = copy.deepcopy(old)
    expected["lifecycle"] = "resolved"
    expected["resolution_mode"] = "fixed-in-place"

    assert new == expected, {
        "row": index,
        "expected": expected,
        "actual": new,
    }

rows = after["failure_paths"]

assert sum(
    row["lifecycle"] == "active"
    for row in rows
) == 0

assert sum(
    row["lifecycle"] == "resolved"
    for row in rows
) == 15

assert sum(
    row.get("resolution_mode") == "fixed-in-place"
    for row in rows
) == 14

assert sum(
    row.get("resolution_mode") == "superseded"
    for row in rows
) == 1

print(
    "ledger-invariant="
    "15/0/15 fixed=14 superseded=1"
)
PY
```

Verifier GREENだけでは、このhistorical preservation proofを代替できない。

## 16. Phase M — working-tree verification

### M1. Evaluator unit testと15 node GREEN

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

python - "$POST_LEDGER_OBS" "${ALL_OBSERVED_ROWS[@]}" <<'PY'
from pathlib import Path
import json
import sys

value = json.loads(
    Path(sys.argv[1]).read_text(encoding="utf-8")
)

expected = list(sys.argv[2:])

assert value["collected"] == expected
assert value["executed"] == expected
assert value["outcomes"] == {
    nodeid: "passed"
    for nodeid in expected
}
assert value["failure_signatures"] == {}

print("post-ledger-normal-pass=15/15")
PY
```

### M2. Clean candidate full verifier

候補wheelを含むfull verifierは、意図的なtracked変更が残るworking treeでは実行しない。working-tree上の確認はfocused testとmanual invariantに限り、candidate verifierはcommit済みでcleanなcheckout/worktreeから実行する。stash、reset、force checkout、alternate indexなどでdirty stateを隠してはならない。

M2のfull verifier実行は、Phase N1で候補をcommit・pushした後のN2へ委譲する。N2ではclean状態を先に確認し、private artifact rootへ結果を書き込み、`candidate_sha`を実際のimplementation SHAへ束縛する。これにより候補wheel receiptとfull verifierが同じclean candidateを検査する。

### M3. Pre-candidate ordinary laneとsource checks

Phase Mのworking treeでは、candidate-wheel、distribution、installed、dogfood、またはfull-verifierのfinal receiptを生成しない。ここで実行できるのは、ordinary lane、Provider lifecycle unit、lint、SpecDock validation、およびfocused/manual invariantだけである。

```bash
# Ordinary lane。Current policy skipは意図した現行動作。
env TMPDIR="$TEST_TMPDIR" \
  uv run pytest \
    -q \
    --tb=short

# Provider lifecycle unit lane。
env TMPDIR="$TEST_TMPDIR" \
  uv run pytest \
    -q \
    --tb=short \
    tests/unit/provider_lifecycle

env TMPDIR="$TEST_TMPDIR" \
  make lint

./spec-dock/scripts/spec-dock validate \
  | tee "$EVIDENCE_DIR/post-change-validate.txt"

grep -F \
  'spec-dock: ok (validate) nodes=236' \
  "$EVIDENCE_DIR/post-change-validate.txt"
```

このpre-candidate subsetはexit 0でなければならない。Distribution、packaged parity、dogfood、およびfull verifierはN2のclean candidate gateで一度だけ実行し、N3では再実行しない。

### M4. No-touch surfaces

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

Parent、#392、#396 no-touch:

```bash
git diff --exit-code "$SPEC_FREEZE_SHA" -- \
  spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/requirement.md \
  spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/design.md \
  spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/plan.md \
  spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/artifacts \
  spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover \
  spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/issues/iss-00396-build-once-provider-gate-and-regression-policy-cutover
```

### M5. Exact implementation file set

初回実装ではreviewed specification freezeからのworking-tree diffを、`IMPLEMENTATION_PATHS`で定義したfocused 26-path setと比較する。U05後のresumeでは、support-history checkpointからcurrent reviewed specification targetまでの累積差分を、canonical 6 pathsとfocused implementation 26 pathsの和として実測し、さらにcurrent working-tree差分がimplementation paths内に限定されることを確認する。`RESUME_CHECKPOINT_SHA/TREE`はcurrent identityではなく、既存実装の祖先基点として検証する。support historyのmode、object type、Git object ID一致を追加のblocking gateにせず、resumeで空のcommitを作ってpath countを満たしてはならない。

```bash
if [ "$RESUME_MODE" = "initial-spec-freeze" ]; then
python - "$SPEC_FREEZE_SHA" "${IMPLEMENTATION_PATHS[@]}" <<'PY'
import subprocess
import sys

expected = set(sys.argv[2:])

actual = set(
    subprocess.check_output(
        [
            "git",
            "diff",
            "--name-only",
            sys.argv[1],
            "--",
        ],
        text=True,
    ).splitlines()
)

assert actual == expected, {
    "expected": sorted(expected),
    "actual": sorted(actual),
}

print(f"implementation-file-set={len(actual)}/{len(expected)}")
PY
else
python - "$SUPPORT_HISTORY_SHA" "$SPEC_FREEZE_SHA" \
  "${SPEC_PACK_PATHS[@]}" -- \
  "${IMPLEMENTATION_PATHS[@]}" <<'PY'
import subprocess
import sys

support_history, spec_freeze, *paths = sys.argv[1:]
separator = paths.index("--")
primary_paths = set(paths[:separator])
implementation_paths = set(paths[separator + 1:])

def changed_paths(base, head):
    return set(
        subprocess.check_output(
            ["git", "diff", "--name-only", "--no-renames", base, head, "--"],
            text=True,
        ).splitlines()
    )

committed_paths = changed_paths(support_history, spec_freeze)
assert committed_paths == primary_paths | implementation_paths, {
    "stage": "post-u05-cumulative-committed-scope",
    "expected": sorted(primary_paths | implementation_paths),
    "actual": sorted(committed_paths),
}

working_tree_paths = set(
    subprocess.check_output(
        ["git", "diff", "--name-only", "--no-renames", spec_freeze, "--"],
        text=True,
    ).splitlines()
)
assert working_tree_paths <= implementation_paths, {
    "stage": "post-u05-working-tree-scope",
    "allowed": sorted(implementation_paths),
    "actual": sorted(working_tree_paths),
}

print(
    f"implementation-file-set={len(implementation_paths)}/{len(implementation_paths)} "
    f"cumulative-committed={len(committed_paths)} "
    f"working-tree={len(working_tree_paths)}"
)
PY
fi

git diff --check
test -z "$(git ls-files --others --exclude-standard)"
```

Missing expected pathとextra pathのどちらもblockingである。

### M6. Working-tree manual invariants再実行

Commit gateへ進む前に次を再実行する。

1. Phase H5 publication security matrix
2. Phase I row 12 blob/AST guard
3. Phase K4 protected-data equality
4. Phase L2 ledger historical preservation
5. Required-fast 4 / timing 243
6. Exact focused 26-file set
7. no-touch checks

一つでも失敗した場合はcommit許可を使用しない。

## 17. Phase N — optional exact candidate freeze

### N1. Commit/push authorization boundary

`COMMIT_PUSH_AUTHORIZED=false`の場合はここで停止し、working-tree provisional receiptを返す。

```text
candidate_state = working-tree-provisional
merge_ready = false
implementation_sha = null
implementation_tree = null
```

`COMMIT_PUSH_AUTHORIZED=true`の場合だけ以下を実行する。

`RESUME_MODE=post-u05-checkpoint`で、current reviewed specification targetがcleanで必要な実装差分をすでに含む場合は、commit/pushを再実行せず、`SPEC_FREEZE_SHA/TREE`を検証してそのcurrent HEADを`IMPLEMENTATION_SHA/TREE`としてadoptする。`RESUME_CHECKPOINT_SHA/TREE`は、その実装が由来する祖先基点の証明にだけ使う。仕様レビュー後にboundary witnessの不要な文書SHA比較除去などのallowed implementation差分が残る場合は、旧candidateへ戻す操作をせず、以下のfocused path stage・commit・pushブロックで一つのforward commitへ束縛する。

初回のforward commitでは、実装candidateのstaged path set全体を`IMPLEMENTATION_PATHS`のfocused 26件と照合する。`post-u05-checkpoint`では、累積scopeと今回のcommitでstageするincremental setを混同しない。resumeで残るapproved pending setは、stage前に`SPEC_FREEZE_SHA`から実測し、non-emptyで`IMPLEMENTATION_PATHS`のsubsetであることを確認したうえで、そのpending setだけをstageする。既にcommit済みのpathを空の差分として再出現させたり、空commitでpath数を満たしたりしてはならない。

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

if [ "$RESUME_MODE" = "post-u05-checkpoint" ] && \
   [ -z "$(git status --porcelain=v1 --untracked-files=all)" ]; then
  test -z "$(git status --porcelain=v1 --untracked-files=all)"
  test "$(git rev-parse HEAD)" = "$SPEC_FREEZE_SHA"
  test "$(git rev-parse 'HEAD^{tree}')" = "$SPEC_FREEZE_TREE"
  export IMPLEMENTATION_SHA="$(git rev-parse HEAD)"
  export IMPLEMENTATION_TREE="$(git rev-parse 'HEAD^{tree}')"
else

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
POST_U05_INCREMENTAL_PATHS=(
  tests/integration/test_issue_392_acceptance.py
)

python - "$SPEC_FREEZE_SHA" "${IMPLEMENTATION_PATHS[@]}" -- \
  "${POST_U05_INCREMENTAL_PATHS[@]}" <<'PY'
import subprocess
import sys

base, *paths = sys.argv[1:]
separator = paths.index("--")
allowed = set(paths[:separator])
expected = set(paths[separator + 1:])
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
assert actual == expected, {
    "stage": "post-u05-incremental-before-stage",
    "expected": sorted(expected),
    "actual": sorted(actual),
}
assert actual <= allowed, {
    "stage": "post-u05-incremental-allowlist",
    "allowed": sorted(allowed),
    "actual": sorted(actual),
}

print("post-u05-incremental-file-set=1/1")
PY

git add -- "${POST_U05_INCREMENTAL_PATHS[@]}"

python - "${POST_U05_INCREMENTAL_PATHS[@]}" <<'PY'
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
    "stage": "post-u05-incremental-cached",
    "expected": sorted(expected),
    "actual": sorted(actual),
}

print("staged-incremental-file-set=1/1")
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
export IMPLEMENTATION_TREE="$(git rev-parse 'HEAD^{tree}')"

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

test -z "$(git status --porcelain=v1 --untracked-files=all)"
fi
```

禁止事項:

* amend
* force push
* unrelated pathのstage
* evidence/log/cacheのstage
* remoteが動いた状態でexpected SHAを更新して継続
* integration branchへのdirect push

### N2. Exact clean full verifier

```bash
EXACT_ARTIFACT_ROOT="$EVIDENCE_DIR/full-exact"
mkdir -p "$EXACT_ARTIFACT_ROOT"
test -z "$(find "$EXACT_ARTIFACT_ROOT" -mindepth 1 -print -quit)"

env TMPDIR="$TEST_TMPDIR" \
  uv run python -m scripts.quality.verify_full_regression \
    --shards 4 \
    --artifact-dir "$EXACT_ARTIFACT_ROOT"

test "$(
  find "$EXACT_ARTIFACT_ROOT" \
    -type f \
    -name result.json \
    | wc -l \
    | tr -d ' '
)" -eq 1

EXACT_RESULT="$(
  find "$EXACT_ARTIFACT_ROOT" \
    -type f \
    -name result.json \
    -print
)"

python - "$EXACT_RESULT" "$IMPLEMENTATION_SHA" <<'PY'
from pathlib import Path
import json
import sys

result = json.loads(
    Path(sys.argv[1]).read_text(encoding="utf-8")
)

assert result["candidate_sha"] == sys.argv[2]
assert result["status"] == "verified"
assert result["evaluation"]["verified"] is True
assert result["evaluation"]["active_verified"] == []
assert len(
    result["evaluation"]["resolved_verified"]
) == 15
assert result["evaluation"]["retired_verified"] == []
assert result["evaluation"]["violations"] == []

print("exact-candidate-full-verifier=verified")
PY
```

### N3. Exact clean non-overlapping gate

N2のcurrent full verifierが収集・実行したfull-regression nodeと、その結果に含まれるdistribution、lifecycle、packaged parity、dogfood、M1相当の全nodeを再実行しない。N2の一つのresult receiptを、それらのテスト証拠の正本として再利用する。N3は同じclean `IMPLEMENTATION_SHA/TREE`に対する、N2が収集しない非重複のlint、SpecDock validation、手動no-touch/protected-data証明だけを確認する。これにより同一candidateの重複実行と追加のflake/costを避ける。

```bash
env TMPDIR="$TEST_TMPDIR" \
  make lint

./spec-dock/scripts/spec-dock validate \
  | tee "$EVIDENCE_DIR/exact-candidate-validate.txt"

grep -F \
  'spec-dock: ok (validate) nodes=236' \
  "$EVIDENCE_DIR/exact-candidate-validate.txt"
```

その後、identityを確認する。

```bash
test "$(git rev-parse HEAD)" = \
  "$IMPLEMENTATION_SHA"

test "$(git rev-parse 'HEAD^{tree}')" = \
  "$IMPLEMENTATION_TREE"

test "$(git rev-parse '@{upstream}')" = \
  "$IMPLEMENTATION_SHA"

test "$(
  git ls-remote \
    --heads \
    origin \
    "refs/heads/$ISSUE_BRANCH" \
    | awk 'NF {print $1}'
)" = "$IMPLEMENTATION_SHA"

test -z "$(git status --porcelain=v1 --untracked-files=all)"
```

Working-tree evidenceを再利用しない。N2のfull-verifier receiptとN3の非重複gateを、exact clean SHA/treeへ束縛する。Phase H5、I、M1、K5、distribution、lifecycle、package parity、dogfoodのfull-regression結果はN2から再実行せずに参照する。

### N4. Sanitized full-verifier summary

```bash
python - \
  "$EXACT_RESULT" \
  "$EVIDENCE_DIR/exact-result-summary.json" <<'PY'
from pathlib import Path
import hashlib
import json
import sys

raw_path = Path(sys.argv[1])
raw = raw_path.read_bytes()
value = json.loads(raw)

summary = {
    "raw_result_sha256":
        hashlib.sha256(raw).hexdigest(),
    "candidate_sha":
        value["candidate_sha"],
    "status":
        value["status"],
    "evaluation":
        value["evaluation"],
    "collection_seconds":
        value.get("collection_seconds"),
    "shard_elapsed_seconds":
        value.get("shard_elapsed_seconds"),
    "total_elapsed_seconds":
        value.get("total_elapsed_seconds"),
}

Path(sys.argv[2]).write_text(
    json.dumps(
        summary,
        indent=2,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)

print(summary["raw_result_sha256"])
PY
```

Raw private pathやraw logをdistribution evidenceへ含めない。

## 18. Phase O — independent implementation review

Exact clean pushed `IMPLEMENTATION_SHA`とtreeに対し、fresh independent sessionで次を別々に実行する。

### O1. Code Review Strict

Input:

* repository
* branch
* exact implementation SHA/tree
* adopted Requirement/Design/Plan/handoff
* exact diff
* 14 rowsのRED/GREEN
* row 2 successor
* row 3 security matrix
* row 12 no-edit guard
* dogfood/protected-data evidence
* ledger preservation
* exact full-verifier summary/hash
* no-touch proof
* exact focused 26-file set

Acceptance:

```text
review_status = pass
P0 = 0
P1 = 0
```

### O2. Final Quality Gate Strict v2

Acceptance:

```text
status = pass
coverage_complete = true
P0 = 0
P1 = 0
unreviewed_areas = []
unresolved_items = []
```

Findingの修正でcommitが変わった場合、そのcandidateは新しいidentityである。次をすべてnew SHAへ再束縛する。

* affected focused tests
* exact full verifier
* ordinary/lifecycle/platform/package/dogfood gates
* lint
* SpecDock validate
* row 3 security matrix
* row 12 guard
* ledger preservation
* protected-data proof
* no-touch proof
* Code Review Strict
* Final Quality Gate Strict

過去receiptをnew SHAへ流用しない。

## 19. Phase P — optional PR preparation / human merge boundary

### P1. PR authorization

`PR_PREPARE_AUTHORIZED=false`の場合、review済みcandidateを返して停止する。PRを作成・更新しない。

`PR_PREPARE_AUTHORIZED=true`の場合、packetは次も含む。

* `PR_MODE=create|update`
* updateの場合はexact `PR_NUMBER`
* `PR_BODY_PATH`

### P2. Create mode

```bash
test "$PR_PREPARE_AUTHORIZED" = "true"
test "${PR_MODE:?PR_MODE is required}" = "create"

gh pr create \
  --repo "$EXPECTED_REPOSITORY" \
  --head "$ISSUE_BRANCH" \
  --base "$INTEGRATION_BRANCH" \
  --title "fix(iss-00395): 回帰ベースラインを終端化" \
  --body-file "${PR_BODY_PATH:?PR_BODY_PATH is required}"
```

### P3. Update mode

既存PRのhead/base/SHAを先に確認する。

```bash
test "$PR_PREPARE_AUTHORIZED" = "true"
test "${PR_MODE:?PR_MODE is required}" = "update"
: "${PR_NUMBER:?PR_NUMBER is required}"

gh pr view \
  "$PR_NUMBER" \
  --repo "$EXPECTED_REPOSITORY" \
  --json headRefName,headRefOid,baseRefName \
  > "$EVIDENCE_DIR/pr-before.json"

python - \
  "$EVIDENCE_DIR/pr-before.json" \
  "$ISSUE_BRANCH" \
  "$IMPLEMENTATION_SHA" \
  "$INTEGRATION_BRANCH" <<'PY'
from pathlib import Path
import json
import sys

value = json.loads(
    Path(sys.argv[1]).read_text(encoding="utf-8")
)

assert value["headRefName"] == sys.argv[2]
assert value["headRefOid"] == sys.argv[3]
assert value["baseRefName"] == sys.argv[4]
PY

gh pr edit \
  "$PR_NUMBER" \
  --repo "$EXPECTED_REPOSITORY" \
  --title "fix(iss-00395): 回帰ベースラインを終端化" \
  --body-file "${PR_BODY_PATH:?PR_BODY_PATH is required}" \
  --base "$INTEGRATION_BRANCH"
```

### P4. Human merge boundary

LunaMaxは次を実行しない。

* PR merge
* integration branch direct push
* main push/merge
* revert
* required-context変更
* branch protection変更
* #392 close
* #395 close
* #396 start
* new Issue creation
* automatic rollback

Human merge前に、次を確認する。

* PR head SHA = final reviewed `IMPLEMENTATION_SHA`
* PR head tree = final reviewed `IMPLEMENTATION_TREE`
* Provider CI `provider-tests` SUCCESS
* Provider distribution parity Ubuntu SUCCESS
* Provider distribution parity macOS SUCCESS
* Code Review Strict pass
* Final Quality Gate pass
* exact full verifier GREEN
* unresolved findingなし

## 20. Phase Q — human-merged same-tip B1 then B2

このPhaseはLunaMax implementation taskに含まれない。Codex/human verificationへのoperational handoffである。

### Q1. Exact integration identity

Clean verification checkoutを使用する。

```bash
set -euo pipefail
umask 077

git fetch --prune origin

git checkout --detach \
  "origin/$INTEGRATION_BRANCH"

export POST_395_MERGE_SHA="$(git rev-parse HEAD)"
export POST_395_MERGE_TREE="$(git rev-parse 'HEAD^{tree}')"

test -z "$(git status --porcelain=v1 --untracked-files=all)"

test "$(
  git ls-remote \
    --heads \
    origin \
    "refs/heads/$INTEGRATION_BRANCH" \
    | awk 'NF {print $1}'
)" = "$POST_395_MERGE_SHA"
```

Immutable PR gate receiptへ次を記録する。

* PR number
* accepted PR head SHA/tree
* base branch
* human merge SHA/tree
* required Provider CI role names
* each conclusion
* PR head tree = `POST_395_MERGE_TREE`のproof

Tree equalityが成立しない場合、PR-head CIはmerged treeを証明しないためB1を停止する。

### Q2. Post-merge evidence workspace

```bash
BASE_TMP="${TMPDIR:-/tmp}"
export EVIDENCE_DIR="$(mktemp -d "${BASE_TMP%/}/iss-00395-post-merge.XXXXXXXX")"
export TEST_TMPDIR="$EVIDENCE_DIR/tmp"
mkdir -p "$TEST_TMPDIR"
```

P392 ledger baselineをverified Git objectから再構築する。

```bash
git show \
  "$P392_SHA:full-regression-ledger.json" \
  > "$EVIDENCE_DIR/post-merge-ledger-before.json"

python - "$EVIDENCE_DIR/post-merge-ledger-before.json" <<'PY'
from pathlib import Path
import hashlib
import sys

raw = Path(sys.argv[1]).read_bytes()

actual = hashlib.sha1(
    f"blob {len(raw)}\0".encode("ascii") + raw
).hexdigest()

assert actual == (
    "f181fd3098ef0cba8d0d17e47d00ea12fbbeb8b5"
)

print("post-merge-p392-ledger-baseline-ok")
PY
```

Implementation worktreeのprivate evidence pathへ依存しない。

### Q3. B1

同じ`POST_395_MERGE_SHA`/tree上で次を実行する。

```bash
env TMPDIR="$TEST_TMPDIR" \
  uv run pytest \
    -q \
    --tb=short

env TMPDIR="$TEST_TMPDIR" \
  uv run pytest \
    -q \
    --tb=short \
    tests/unit/provider_lifecycle

env TMPDIR="$TEST_TMPDIR" \
  uv run pytest \
    --run-full-regression \
    --full-regression-shard \
    -q \
    --tb=short \
    tests/cli_runtime/test_distribution_cutover.py

env TMPDIR="$TEST_TMPDIR" \
  uv run pytest \
    --run-full-regression \
    --full-regression-shard \
    -q \
    --tb=short \
    tests/cli_runtime/test_provider_lifecycle_bootstrap.py \
    tests/cli_runtime/test_provider_lifecycle_handoff.py \
    tests/cli_runtime/test_generation_checkout.py \
    tests/cli_runtime/test_worktree_lifecycle_coordination.py

env TMPDIR="$TEST_TMPDIR" \
  uv run pytest \
    --run-full-regression \
    --full-regression-shard \
    -q \
    --tb=short \
    tests/integration/test_epic_00343_distribution.py

env TMPDIR="$TEST_TMPDIR" \
  uv run pytest \
    --run-full-regression \
    --full-regression-shard \
    -q \
    --tb=short \
    tests/integration/test_provider_lifecycle_dogfood.py

env TMPDIR="$TEST_TMPDIR" \
  make lint

./spec-dock/scripts/spec-dock validate
```

Row 3 security matrixとrow 12 guardを、merged sourceに対して再実行する。

Current full verifier:

```bash
POST_MERGE_ARTIFACT_ROOT="$EVIDENCE_DIR/full-post-merge"
mkdir -p "$POST_MERGE_ARTIFACT_ROOT"

env TMPDIR="$TEST_TMPDIR" \
  uv run python -m scripts.quality.verify_full_regression \
    --shards 4 \
    --artifact-dir "$POST_MERGE_ARTIFACT_ROOT"

test "$(
  find "$POST_MERGE_ARTIFACT_ROOT" \
    -type f \
    -name result.json \
    | wc -l \
    | tr -d ' '
)" -eq 1

POST_MERGE_RESULT="$(
  find "$POST_MERGE_ARTIFACT_ROOT" \
    -type f \
    -name result.json \
    -print
)"

python - \
  "$POST_MERGE_RESULT" \
  "$POST_395_MERGE_SHA" <<'PY'
from pathlib import Path
import json
import sys

result = json.loads(
    Path(sys.argv[1]).read_text(encoding="utf-8")
)

assert result["candidate_sha"] == sys.argv[2]
assert result["status"] == "verified"
assert result["evaluation"]["verified"] is True
assert result["evaluation"]["active_verified"] == []
assert len(
    result["evaluation"]["resolved_verified"]
) == 15
assert result["evaluation"]["retired_verified"] == []
assert result["evaluation"]["violations"] == []

print("post-merge-full-verifier=verified")
PY
```

各block後にidentityを確認する。

```bash
test "$(git rev-parse HEAD)" = \
  "$POST_395_MERGE_SHA"

test "$(git rev-parse 'HEAD^{tree}')" = \
  "$POST_395_MERGE_TREE"

test -z "$(git status --porcelain=v1 --untracked-files=all)"
```

B1受入条件:

* PR required Provider CI roles SUCCESS
* PR head tree = merged tree
* ordinary suite GREEN
* provider lifecycle unit GREEN
* distribution cutover GREEN
* platform/coordination GREEN
* packaged distribution parity GREEN
* dogfood parity GREEN
* row 3 security matrix GREEN
* row 12 no-edit guard GREEN
* lint GREEN
* SpecDock validate GREEN
* current full verifier GREEN
* unexpected failure 0
* lifecycle/protected-data invariants unchanged
* same exact merged SHA/tree維持

### Q4. B2

B1と同じ`POST_395_MERGE_SHA`/tree上で実行する。

```bash
python - \
  "$POST_395_MERGE_SHA" \
  "$POST_395_MERGE_TREE" \
  "$POST_MERGE_RESULT" \
  "$EVIDENCE_DIR/post-merge-ledger-before.json" <<'PY'
from pathlib import Path
import copy
import json
import subprocess
import sys

sha = sys.argv[1]
tree = sys.argv[2]
result_path = Path(sys.argv[3])
before_path = Path(sys.argv[4])

actual_sha = subprocess.check_output(
    ["git", "rev-parse", "HEAD"],
    text=True,
).strip()

actual_tree = subprocess.check_output(
    ["git", "rev-parse", "HEAD^{tree}"],
    text=True,
).strip()

assert actual_sha == sha
assert actual_tree == tree

before = json.loads(
    before_path.read_text(encoding="utf-8")
)

after = json.loads(
    Path(
        "full-regression-ledger.json"
    ).read_text(encoding="utf-8")
)

assert len(before["failure_paths"]) == 15
assert len(after["failure_paths"]) == 15

assert {
    key: value
    for key, value in before.items()
    if key != "failure_paths"
} == {
    key: value
    for key, value in after.items()
    if key != "failure_paths"
}

for index, (old, new) in enumerate(
    zip(
        before["failure_paths"],
        after["failure_paths"],
        strict=True,
    ),
    1,
):
    assert old["nodeid"] == new["nodeid"]

    if index == 2:
        assert old == new
        continue

    expected = copy.deepcopy(old)
    expected["lifecycle"] = "resolved"
    expected["resolution_mode"] = "fixed-in-place"

    assert new == expected

rows = after["failure_paths"]

assert sum(
    row["lifecycle"] == "active"
    for row in rows
) == 0

assert sum(
    row["lifecycle"] == "resolved"
    for row in rows
) == 15

assert sum(
    row.get("resolution_mode") == "fixed-in-place"
    for row in rows
) == 14

assert sum(
    row.get("resolution_mode") == "superseded"
    for row in rows
) == 1

timing = json.loads(
    Path(
        "full-regression-timing-weights.json"
    ).read_text(encoding="utf-8")
)

assert len(timing["node_seconds"]) == 243

result = json.loads(
    result_path.read_text(encoding="utf-8")
)

assert result["candidate_sha"] == sha
assert result["status"] == "verified"
assert result["evaluation"]["violations"] == []
assert result["evaluation"]["active_verified"] == []
assert len(
    result["evaluation"]["resolved_verified"]
) == 15

print(
    "B2=15/0/15 "
    "fixed=14 superseded=1 "
    "approved=0 unexpected=0"
)
PY
```

B1とB2のreceiptは同じfull SHA/treeを持たなければならない。LunaMaxはIssue closureまたは#396 startを行わない。

## 21. Required execution artifacts

Executorは、tracked Product filesではなく、private evidence rootまたは承認済みexternal evidence storeへ次を返す。

1. `identity.json`

   * repository
   * Issue branch
   * P392 SHA/tree
   * elaboration input SHA/tree
   * specification SHA/tree
   * authorized時のimplementation SHA/tree

2. `individual-red-summary.json`

   * 13 individually failing rows
   * expected failure layer
   * raw log SHA-256
   * observation SHA-256

3. Row GREEN observations

   * repaired 13 rows
   * row 12
   * row 2 successor

4. Ledger evidence

   * `ledger-before.json`
   * authorized fieldだけが変わった比較summary
   * row 2 exact preservation
   * top-level historical metadata preservation

5. Protected-data evidence

   * `protected-before.json`
   * `protected-after.json`
   * equality result

6. Dogfood evidence

   * `dogfood-update.json`
   * old/new digest
   * ready record fields
   * two slot markers
   * runtime mirror equality
   * parity result

7. Working-tree provisional evidence

   * binary diff SHA-256
   * focused/manual diagnostic results only; no full-verifier, wheel, distribution, or dogfood final receipt
   * `merge_ready=false`

8. Exact clean evidence

   * implementation SHA/tree
   * exact full-verifier hash
   * sanitized result summary

9. Command receipts

   * ordinary
   * lifecycle
   * distribution cutover
   * platform/coordination
   * packaged distribution
   * dogfood
   * lint
   * SpecDock validate

10. Manual invariant receipts

    * row 3 publication-security matrix
    * row 12 blob/AST guard
    * policy/workflow no-touch
    * exact focused 26-file set
    * timing 243
    * required-fast 4

11. Independent reviews

    * Code Review Strict
    * Final Quality Gate Strict

12. PR receipt

    * PR number
    * head/base
    * head SHA/tree
    * required checks

13. Human-merge operational receipts

    * post-merge SHA/tree
    * B1
    * B2

14. Stop-and-return object

    * any gate failure時

Raw credential、private absolute path、raw secret-bearing logをdistributed evidenceへ含めない。Evidence artifactをProduct pathへstageしない。

## 22. Stop-and-return schema

停止時は、新しい設計を選択せず、次のschemaに適合する一つのJSON objectを返す。

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

`owner_decision_required=true`の場合は実装を継続せずparent ownerへ返す。

Payloadへ次を含めない。

* raw credential
* token
* username/password
* userinfoを含むremote URL
* private absolute path
* secret-bearing raw log

## 23. Stop conditions

次のいずれかで直ちに停止する。

### Identity / permission

* repository不一致
* Issue branch不一致
* P392 SHA/tree不一致
* elaboration SHA/tree不一致
* spec freeze SHA/tree不一致
* local/upstream/remote不一致
* dirty worktree
* spec review receipt不在
* review target mismatch
* review fail
* P0/P1 nonzero
* implementation authorization不在
* writer assertion不在、期限切れ、scope不足
* concurrent writer存在

### Baseline / source drift

* 15 rowsでない
* P392 historical beforeが14 active / 1 resolvedでない
* U05後のcurrent root afterが15 resolved / 0 active / 14 `fixed-in-place` / 1 `superseded`でない
* row order drift
* nodeid drift
* historical signature drift
* row 2 successor drift
* timingが243でない
* required-fastが4でない
* verified source blob drift
* row 12 boundary drift

### RED / GREEN

* first REDがexpected layerと異なる
  -対象rowがskip、xfail、xpass、error
* heavy test bodyが未実行
* Product修復後もrowがnormal passしない
* unexpected failureが発生
* accepted assertionを削除しなければ通らない

### Security

* read-only identityとpublication strictnessを両立できない
* publicationがuserinfoを受理する
* fetch/push mismatchを受理する
* credential materialがstdout/stderr/exception/evidenceへ露出する
* same-repository validationを弱める必要がある

### Dogfood / lifecycle

* generated filesの手編集が必要
* candidate digestが変化しない
* record/markers digest不一致
* version/state/operation/seed policy drift
* skill `SKILL.md` drift
* protected data drift
* lifecycle source/schema/wire drift
* unintended provider-root drift

### Ledger / policy

* 15 nodesがnormal passする前にledger変更が必要
* historical fieldsが変わる
* row 2が変わる
* top-level historical metadataが変わる
* timing、sharder、policy hook、workflow変更が必要
* skip、xfail、approved failureが必要
* node rename、row削除、signature rewriteが必要

### Parent boundary

* #392 lifecycle redesignが必要
* `E384-QUAL-001`変更が必要
* #396 toolingが必要
* policy retirementが必要
* required-context変更が必要
* main mergeが必要
* new owner decisionが必要
* `owner_decisions_required`がnon-emptyになる

## 24. GREEN / merge-ready criteria

Candidateは、一つのclean pushed implementation SHA/treeに対し次がすべて成立した場合だけmerge-readyである。

* 13 failing rowsのindividual expected RED evidence
* row 12のentry evaluator RED
* row 12 node normal pass
* 14 historical active nodes normal pass
* row 2 successor normal pass
* row 3 security matrix pass
* push-only credential rejection pass
* fetch/push mismatch rejection pass
* credential non-exposure pass
* row 12 exact blob/AST boundary unchanged
* descriptor-bound test double
* retired active flags 0
* dogfood complete projection
* provider/dogfood runtime byte equality
* old/new candidate digest不一致
* record/markers digest一致
* protected-data equality
* ledger 15/0/15
* fixed-in-place 14
* superseded 1
* historical fields preservation
* approved failure 0
* unexpected failure 0
* full verifier `status=verified`
* `active_verified=[]`
* resolved count 15
* violations 0
* ordinary lane pass
* provider lifecycle unit pass
* distribution cutover pass
* platform/coordination pass
* packaged distribution parity pass
* full dogfood suite pass
* lint pass
* SpecDock validate pass
* timing 243 unchanged
* required-fast 4 unchanged
* policy/workflow unchanged
* exact changed-file set 26（post-U05はcanonical 6 pathsとfocused implementation 26 pathsのscopeを実測）
* no extra tracked/untracked implementation file
* Code Review Strict pass、P0/P1=0
* Final Quality Gate pass、coverage complete、P0/P1=0
* unreviewed/unresolved arrays empty
* agentがmergeしていない

Working-tree-only evidenceは常に次である。

```text
candidate_state = working-tree-provisional
merge_ready = false
```

## 25. Rollback boundary

### 25.1 Human merge前

Issue candidate全体をabandonまたは修正する。次をintegration branchへ部分導入しない。

* ledgerだけ
* Productだけ
* testsだけ
* generated mirrorだけ
* candidate record/markersだけ

### 25.2 Human merge後、#396開始前

B1またはB2が失敗した場合、humanが次のいずれかを選ぶ。

1. Whole Issue #395 merge revertでP392へ戻し、P392 invariantsを再検証する。
2. Issue #395 owned boundary内でforward-fixし、new exact tipでB1/B2を完全再実行する。

### 25.3 #396開始後

#396 workを停止・保存する。Humanがsuffix dispositionを決定するまで#395をrevertしない。Accepted suffixを戻す場合はreverse dependency orderで扱う。

### 25.4 禁止rollback

* ledger-only rollback
* Product-only rollback
* test-only rollback
* generated-mirror-only rollback
* automatic rollback
* old API fallback
* retired CLI flag fallback
* force-push history rewrite
* human判断前のrevert

## 26. Completion state

本Planの作成・保存自体はrepository state、commit permission、PR permissionまたはmerge permissionを変更しない。今回はユーザーの明示承認により、canonical implementation permissionをtrueとした。

```text
implementation_allowed = true
owner_decisions_required = []
human_merge_only = true
```

Product completionは次の順序でのみ成立する。

```text
adopted clean specification
  -> independent spec review pass
  -> explicit implementation dispatch
  -> Product/test GREEN
  -> dogfood projection
  -> ledger transition
  -> exact clean verification
  -> independent implementation reviews
  -> human PR merge
  -> same-tip B1
  -> same-tip B2
```

LunaMaxは人間merge前で停止し、#392/#395 closure、#396 start、policy retirement、required-context変更、main mergeを行わない。
