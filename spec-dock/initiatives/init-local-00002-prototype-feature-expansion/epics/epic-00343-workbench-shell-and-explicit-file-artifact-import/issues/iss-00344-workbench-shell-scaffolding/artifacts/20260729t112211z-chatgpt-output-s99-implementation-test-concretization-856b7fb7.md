# S99 実行ブリーフ（Advisory）

**結論:** S99 を開始できる。ただし、現時点で確認できる具体的な未完了は実装・テストではなく `report.md` の整合性である。まず report-only の review-target commit で既存の矛盾を正し、その新しい HEAD に aggregate verification と三者レビューを固定する。現時点で新しい実装または新規テストを追加する根拠はない。

GitHub connector で `chemitaro/spec-dock` の `iss-00344-workbench-shell-scaffolding` と requested HEAD `856b7fb7493b30fa1f703de77aac03d583e932d1` の一致を確認した。この commit は S95 の `committed / approved` と S99 admission を report に反映する report-only commit である。

## Preconditions

### 1. Source identity

```bash
set -euo pipefail

BRANCH='iss-00344-workbench-shell-scaffolding'
SOURCE_HEAD='856b7fb7493b30fa1f703de77aac03d583e932d1'
ISSUE_DIR='spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00343-workbench-shell-and-explicit-file-artifact-import/issues/iss-00344-workbench-shell-scaffolding'
REPORT="${ISSUE_DIR}/report.md"

git fetch --no-tags origin \
  "refs/heads/${BRANCH}:refs/remotes/origin/${BRANCH}" \
  "refs/heads/main:refs/remotes/origin/main"

test "$(git branch --show-current)" = "$BRANCH"
test "$(git rev-parse HEAD)" = "$SOURCE_HEAD"
test "$(git rev-parse "refs/remotes/origin/${BRANCH}")" = "$SOURCE_HEAD"

git diff --quiet
git diff --cached --quiet
test -z "$(git status --porcelain=v1 --untracked-files=all)"
git merge-base --is-ancestor origin/main HEAD
```

Mismatch、dirty state、remote-head drift、または `origin/main` と明らかに分岐している状態では進めない。reset、rebase、merge で自動補正しない。

S01、S02、S03、S90、S95 は report 上すべて `committed`、clean/pushed evidence 付き、Result Approval `approved` で、S99 が admitted されている。

### 2. Pre-review report normalization

三者レビュー前に、次の**既存 report-only gap**を修正する。

* `Step Contract Closure` 表に S90 行がない。S90 test/docs lane、closure head、EAL-043/EAL-045、Result Approval への参照を一行に正規化する。現在の表は S01、S02、S03、S95 のみである。
* `Implementation Delegation Gate` の S90 docs lane と S95 に残る旧 `fresh ... review pending` / `fresh review待ち` を、後段の確定済み PASS と整合させる。
* Final QA、Code、Spec、Final Commit の `...` / `pass / fail / blocked` は、事前段階では虚偽の PASS にせず、明示的な `pending S99` と必要フィールドに置換する。実測値はレビュー後の final evidence commit で入れる。

この修正は `report.md` だけに限定する。

```bash
# report.md を上記の範囲だけ修正した後
test "$(git diff --name-only)" = "$REPORT"
git diff --check

git add -- "$REPORT"
test "$(git diff --cached --name-only)" = "$REPORT"

git commit -m 'docs(workbench): S99レビュー対象のclosureを正規化'
git push origin "HEAD:${BRANCH}"

REVIEW_HEAD="$(git rev-parse HEAD)"
test "$(git rev-parse "refs/remotes/origin/${BRANCH}")" = "$REVIEW_HEAD"
test -z "$(git status --porcelain=v1 --untracked-files=all)"
```

以後、aggregate verification と三者レビューはすべて `REVIEW_HEAD` に固定する。`856b7f…` は inspected source baseline であり、report normalization 後の review target ではない。

### 3. Assurance binding

`.assurance.json` は `authorized_profile: standard` だが、ファイル上の `status` は `provisional` である。したがって文字列だけで final assurance を推定せず、approved docs への hash binding を実測する。

```bash
uv run python - <<'PY'
from __future__ import annotations

import hashlib
import json
from pathlib import Path

issue_dir = Path(
    "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/"
    "epics/epic-00343-workbench-shell-and-explicit-file-artifact-import/"
    "issues/iss-00344-workbench-shell-scaffolding"
)
contract = json.loads((issue_dir / ".assurance.json").read_text(encoding="utf-8"))

assert contract["classification"]["authorized_profile"] == "standard"

for artifact in contract["source_binding"]["artifacts"]:
    path = Path(artifact["path"])
    observed = hashlib.sha256(path.read_bytes()).hexdigest()
    assert observed == artifact["sha256"], (
        f"stale assurance binding: {path}: "
        f"expected={artifact['sha256']} observed={observed}"
    )

print("assurance binding: pass")
PY
```

## Aggregate verification commands

`tests/cli_runtime/**` と `test_init_update.py` の多くは既定で policy-skip される。したがって、下記の**明示した node/file に限った** `--run-full-regression` は必要である。禁止するのは Issue 346 所有の無指定全 suite、すなわち bare `uv run pytest --run-full-regression` である。

### 1. Fast focused nodes

```bash
uv run pytest -q -ra \
  tests/unit/infra/test_runtime_template_scaffolder.py \
  tests/unit/infra/test_runtime_fs_repo_workbench_opacity.py \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_mirror_docs_match_provider_assets \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_mirror_templates_match_provider_assets
```

### 2. Heavy exact Issue-local nodes

```bash
uv run pytest -q -ra --run-full-regression \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_workbench_readme_assets_are_byte_identical_and_complete \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_fresh_init_creates_only_tracked_root_workbench_readme \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_and_force_init_do_not_backfill_workbench_readme \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_workbench_gitignore_tracks_only_top_level_readme \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_workbench_readme_build_prune_preserves_allowlist_and_removes_stale_nested_readme \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_workbench_readme_distribution_inventory_and_bytes_match_all_surfaces \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_shipped_docs_describe_workbench_readme_boundary \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_mirror_match_provider_assets \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_preserves_opaque_workbenches_while_refreshing_managed_assets \
  tests/cli_runtime/test_new.py::TestCliNew::test_new_nodes_generate_only_workbench_readmes \
  tests/cli_runtime/test_new.py::TestCliNew::test_workbench_no_backfill_preserves_existing_scopes_across_all_triggers
```

### 3. Node lifecycle and Workbench-copy suites

```bash
uv run pytest -q -ra --run-full-regression \
  tests/cli_runtime/test_runtime_new_doc_s09.py \
  tests/cli_runtime/test_workbench.py
```

この scoped invocation は TC-344-001〜010 の fresh/existing root、future node、byte-stable exact-copy、ignore、no-backfill、opacity、checkout/copy、distribution、docs を閉じる。S03 の二つの distribution node は repository 外 temporary build、wheel/sdist extraction、temporary install を行うが、Issue 346 の candidate-wheel consumer E2E ではない。

### 4. Exact ten-pair projection parity

既存 pytest map は `spec-dock/docs/README.md` を完全には所有しないため、十組の direct byte parity も再実行する。

```bash
uv run python - <<'PY'
from __future__ import annotations

import hashlib
from pathlib import Path

pairs = (
    ("spec-dock/.gitignore", "src/spec_dock/assets/spec_dock/.gitignore"),
    ("spec-dock/docs/README.md", "src/spec_dock/assets/spec_dock/docs/README.md"),
    ("spec-dock/docs/guide.md", "src/spec_dock/assets/spec_dock/docs/guide.md"),
    (
        "spec-dock/docs/reference_worktree.md",
        "src/spec_dock/assets/spec_dock/docs/reference_worktree.md",
    ),
    (
        "spec-dock/scripts/spec_dock_runtime/infra/template_scaffolder.py",
        "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/template_scaffolder.py",
    ),
    (
        "spec-dock/templates/README.md",
        "src/spec_dock/assets/spec_dock/templates/README.md",
    ),
    (
        "spec-dock/templates/root/.workbench/README.md",
        "src/spec_dock/assets/spec_dock/templates/root/.workbench/README.md",
    ),
    (
        "spec-dock/templates/initiative/.workbench/README.md",
        "src/spec_dock/assets/spec_dock/templates/initiative/.workbench/README.md",
    ),
    (
        "spec-dock/templates/epic/.workbench/README.md",
        "src/spec_dock/assets/spec_dock/templates/epic/.workbench/README.md",
    ),
    (
        "spec-dock/templates/issue/.workbench/README.md",
        "src/spec_dock/assets/spec_dock/templates/issue/.workbench/README.md",
    ),
)

for mirror_name, provider_name in pairs:
    mirror = Path(mirror_name)
    provider = Path(provider_name)
    assert mirror.is_file(), f"missing mirror: {mirror}"
    assert provider.is_file(), f"missing provider: {provider}"

    mirror_bytes = mirror.read_bytes()
    provider_bytes = provider.read_bytes()
    assert mirror_bytes == provider_bytes, (
        f"provider/mirror divergence: {mirror} != {provider}"
    )
    print(hashlib.sha256(mirror_bytes).hexdigest(), mirror)

print(f"provider/mirror pairs: {len(pairs)} passed")
PY
```

### 5. Exact static contract

```bash
uv run ruff check \
  src/spec_dock/cli.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/template_scaffolder.py \
  setup.py \
  tests/unit/infra/test_init_update.py \
  tests/unit/infra/test_runtime_template_scaffolder.py \
  tests/unit/infra/test_runtime_fs_repo_workbench_opacity.py \
  tests/cli_runtime/test_runtime_new_doc_s09.py \
  tests/cli_runtime/test_new.py \
  tests/cli_runtime/test_workbench.py

uv run ruff format --check \
  src/spec_dock/cli.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/template_scaffolder.py \
  setup.py \
  tests/unit/infra/test_init_update.py \
  tests/unit/infra/test_runtime_template_scaffolder.py \
  tests/unit/infra/test_runtime_fs_repo_workbench_opacity.py \
  tests/cli_runtime/test_runtime_new_doc_s09.py \
  tests/cli_runtime/test_new.py \
  tests/cli_runtime/test_workbench.py

uv run mypy \
  src/spec_dock/cli.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/template_scaffolder.py

git diff --check
```

これが EVD-011 の計画上の exact path list である。

### 6. Default PR lane

```bash
make lint
uv run pytest
```

ここでは bare default suite を使い、`--run-full-regression` を付けない。S95 の既存結果値をコピーせず、S99 の `REVIEW_HEAD` で観測した実際の pass/skip count と exit code を記録する。S95 でも focused five nodes、`make lint`、bare default suite が gate とされていた。

### 7. Same-revision proof

```bash
test "$(git rev-parse HEAD)" = "$REVIEW_HEAD"
test "$(git rev-parse "refs/remotes/origin/${BRANCH}")" = "$REVIEW_HEAD"

git diff --quiet
git diff --cached --quiet
test -z "$(git status --porcelain=v1 --untracked-files=all)"
```

## Closure inspection

次を report と branch diff で確認する。

1. TC-344-001〜011 がすべて closed。`002A/B` と `007A/B/C` は、それぞれ normative `002` / `007` の分解であることを明記する。
2. EVD-001〜013 が欠落なく、EVD-009=三者 review、EVD-010=Issue 346 handoff、EVD-012=S95 projection/default lane、EVD-013=PR delivery に対応する。
3. DES-344-001〜010 と `origin/main...REVIEW_HEAD` の差分に deviation がない。
4. S01/S02/S03/S90/S95 の close state、closure head、clean/pushed、fresh review、Result Approval が一貫する。
5. EAL に unresolved current finding、未採否 recommendation、current-state の `pending` / `blocked` がない。過去の FAIL は削除せず、後続 closure/re-review への参照を保持する。
6. Issue 345 は generic one-file import、Issue 346 は candidate-wheel consumer E2E、integrated dogfood、bare opt-in full regression、Epic-wide review の owner のまま変更しない。

```bash
BASE="$(git merge-base origin/main "$REVIEW_HEAD")"
git diff --name-status "$BASE" "$REVIEW_HEAD"
git diff --check "$BASE" "$REVIEW_HEAD"

for number in $(seq 1 13); do
  evidence_id="$(printf 'EVD-%03d' "$number")"
  grep -Fq "$evidence_id" "$REPORT" || {
    printf 'missing report evidence: %s\n' "$evidence_id" >&2
    exit 1
  }
done

# Final Gate 内に未正規化 placeholder が残っていないこと
sed -n '/## 最終品質ゲート/,$p' "$REPORT" |
  grep -nE 'pass / fail / blocked|\| \.\.\. \|' &&
  {
    echo 'unresolved Final Gate placeholder' >&2
    exit 1
  } || true

# 旧 pending 表現は current-state table に残さない
grep -nE 'fresh review待ち|fresh spec review pending|fresh review pending' "$REPORT" &&
  {
    echo 'stale review state remains in report' >&2
    exit 1
  } || true
```

S95 の protected-state before/after 証拠は歴史的 evidence として report の row count、hash、equality、exact ten-path allowlist を照合する。S99 時点の再 snapshot は「S99 が新たに壊していない」ことは示せるが、S95 projection 前の状態を再構成するものではない。

## Reviewer contracts

三者は**別の fresh context**で、同一の pushed `REVIEW_HEAD`、同じ specs/report/diff/command outputs を読む。他 reviewer の最終 verdict は、三者すべてが返るまで入力しない。全 reviewer は read-only。`pass` 条件は `blocking=0`、`major=0`、required scope の未確認なし。minor は report に採否・理由・残余リスクを記録した場合だけ PASS と両立できる。S99 の役割分担は QA=test sufficiency、code=aggregate implementation、spec=spec/report alignment と固定されている。

### qa-reviewer

```json
{
  "reviewer": "qa-reviewer",
  "review_status": "pass|fail",
  "reviewed_commit": "<REVIEW_HEAD>",
  "review_scope": "TC-344-001..011, EVD-001..013, exact commands, policy skips, test sufficiency",
  "findings": [
    {
      "id": "QA-S99-001",
      "severity": "blocking|major|minor",
      "location": "<path/section/command>",
      "summary": "<finding>",
      "evidence": "<observable evidence>",
      "recommended_action": "<bounded action>"
    }
  ],
  "coverage": {
    "required": ["TC-344-001..011", "EVD-001..013"],
    "unverified": []
  },
  "independence": {
    "fresh_context": true,
    "other_final_verdicts_received": false
  },
  "residual_risks": [],
  "next_action": "proceed|bounded_fix_and_rereview|return_to_planning"
}
```

### code-reviewer

```json
{
  "reviewer": "code-reviewer",
  "review_status": "pass|fail",
  "reviewed_commit": "<REVIEW_HEAD>",
  "review_scope": "origin/main...REVIEW_HEAD implementation, installer, exact-copy, opacity/copy, prune/package, projection",
  "findings": [
    {
      "id": "CR-S99-001",
      "severity": "blocking|major|minor",
      "location": "<path:line>",
      "summary": "<finding>",
      "evidence": "<observable evidence>",
      "recommended_action": "<owner-step bounded action>"
    }
  ],
  "coverage": {
    "required": ["freshness/no-backfill", "README-only tracking", "semantic opacity", "exact five-path distribution", "provider-first parity"],
    "unverified": []
  },
  "independence": {
    "fresh_context": true,
    "other_final_verdicts_received": false
  },
  "residual_risks": [],
  "next_action": "proceed|bounded_fix_and_rereview|return_to_planning"
}
```

### spec-reviewer

```json
{
  "reviewer": "spec-reviewer",
  "review_status": "pass|fail",
  "reviewed_commit": "<REVIEW_HEAD>",
  "review_scope": "requirement/design/plan/report/code/tests/docs traceability, ownership, handoff, human-only boundary",
  "findings": [
    {
      "id": "SR-S99-001",
      "severity": "blocking|major|minor",
      "location": "<artifact/section>",
      "summary": "<finding>",
      "evidence": "<observable evidence>",
      "recommended_action": "<report-only or planning action>"
    }
  ],
  "coverage": {
    "required": ["RQ/TC/DES closure", "S01-S95 admission", "Issue 345/346 boundary", "PR/merge/finish claims"],
    "unverified": []
  },
  "independence": {
    "fresh_context": true,
    "other_final_verdicts_received": false
  },
  "residual_risks": [],
  "next_action": "proceed|bounded_fix_and_rereview|return_to_planning"
}
```

Severity policy:

* `blocking`: wrong/stale HEAD、required command failure、dirty state、assurance invalid、security/no-backfill violation、missing mandatory closure、scope violation。
* `major`: approved behaviorまたは evidence の material gap。bounded repair が可能でも PASS を阻止する。
* `minor`:非実質的な wording/traceability。report disposition があれば PASS 可能。
* reviewer 自身は変更しない。修正は S01/S02/S03/S90/S95 の owner step に戻す。
* 新しい実装・テストは、既存 command failure または reviewer が示す具体的な未検証 approved contract がある場合だけ検討する。新 bug class、canonical behavior、sibling ownership の変更が必要なら planning amendment で停止する。

## Report evidence

Final evidence commit 前に `report.md` へ記録する内容:

* `REVIEW_HEAD`、branch/remote/clean identity。
* 全 aggregate command、exit code、pass/skip count、direct ten-pair parity、exact static results。
* TC-344-001〜011、DES-344-001〜010、EVD-001〜013 の closure mapping。
* S95 protected snapshot の既存 row count/hash/equality と、S99 では再構成不能な historical evidence である旨。
* 三 reviewer の exact JSON artifact、verdict、finding 採否、fix commit、re-review count。
* EVD-010: Issue 346 dependency/handoff、deferred gates、Issue 344 PR delivery owner。
* `No material implementation decisions beyond the approved plan.`、または具体的 Ledger Note。
* final commit に含める予定 path。
* post-commit external evidence destination。
* final evidence commit authorization は `ready`、S99 Result Approval はまだ `pending external PR observation`。

**同じ commit にその commit 自身の SHA を書かない。** 実際の final HEAD、clean、remote equality、PR URL/number、observation result は PR body/comment と Codex handoff の外部 evidence に置く。これは plan が明示した非循環境界である。

## Final commit and PR sequence

1. 三者すべて PASS、blocking/major 0 を確認する。
2. `report.md` と三つの S99 review artifact だけを stage する。source、tests、approved requirement/design/plan、Issue 345/346、raw logs、temporary build/snapshot は含めない。
3. staged diff を検査する。

```bash
git diff --cached --name-status
git diff --cached --check
```

4. mandatory final evidence commit を作る。S99 に approved-no-op はない。

```bash
git commit -m 'docs(workbench): S99最終証跡を確定'

FINAL_HEAD="$(git rev-parse HEAD)"
test "$FINAL_HEAD" != "$REVIEW_HEAD"
test -z "$(git status --porcelain=v1 --untracked-files=all)"

git diff --name-status "$REVIEW_HEAD" "$FINAL_HEAD"
```

`REVIEW_HEAD..FINAL_HEAD` は report/reviewer evidence のみでなければならない。実装・テスト・仕様変更が混在した場合は commit を final closure と扱わず、該当 owner step に戻す。

5. push 後、local/remote exact と clean を確認する。

```bash
git push origin "HEAD:${BRANCH}"

test "$(git rev-parse HEAD)" = "$FINAL_HEAD"
test "$(git rev-parse "refs/remotes/origin/${BRANCH}")" = "$FINAL_HEAD"
test -z "$(git status --porcelain=v1 --untracked-files=all)"
```

6. 実行時点で同 branch の open PR を再検索する。存在すれば再利用し、重複 PR を作らない。存在しなければ **ready、base `main`、head `$BRANCH`** で作成する。本文には次を独立行で含める。

```text
Closes #344
Refs #343

Deferred, non-closing follow-up: #345
Deferred, non-closing integration: #346
```

`Closes`、`Fixes`、`Resolves` を #345 または #346 に使用しない。

7. PR の実 head が `FINAL_HEAD` と一致することを確認し、canonical observation script を exact SHA 付きで実行する。

```bash
OBS_OUT="$(mktemp -d "${TMPDIR:-/tmp}/spec-dock-pr-observation.XXXXXXXX")"

./.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh \
  --repo chemitaro/spec-dock \
  --pr "$PR_NUMBER" \
  --head-sha "$FINAL_HEAD" \
  --out "$OBS_OUT"
```

この script の authoritative output は stdout の JSON であり、`stale_head`、`timeout`、`unknown`、`human_gate` は PASS ではない。

8. `merge-prepared: yes` は、少なくとも次が最新 head で成立した場合だけ宣言する。

* PR open、ready、base `main`、head branch/`FINAL_HEAD` 一致。
* latest head への observation 完了。
* required GitHub Actions failure なし。
* external/non-Actions required checks がある場合は別途確認。
* unresolved P0/P1 なし。
* P2/P3 は明示的に non-blocking disposition。
* visible conflict / semantic merge blocker なし。
* unresolved thread 状態と branch-protection conversation requirement を確認。
* blocker inventory、human gate、未完 repair unit なし。

9. `merge-prepared` の Result Approval を記録して停止する。merge、auto-merge、branch deletion、review thread resolve、Issue close、`issue finish` は実行しない。

## Stop conditions

即時停止または owner step へ戻す条件:

* branch、local HEAD、remote HEAD、clean state、assurance binding の不一致。
* aggregate command、direct parity、static/default lane の failure。
* required closure/evidence 欠落、report の current-state 矛盾。
* reviewer の blocking/major、未確認 required scope、stale reviewer SHA。
* implementation/spec/test 変更が必要だが具体的既存 gap が示されていない。
* Issue 345/346 の implementation、candidate-wheel consumer E2E、generic import、bare full-regression、Epic-wide work が必要。
* security/privacy、existing Workbench mutation、no-backfill violation。
* PR observation の stale head、required CI failure、P0/P1、conflict、unknown limitation、timeout、human gate。

### Stale-head rules

* **PR observation 後を含む branch-changing repair**は、それ以前の S99 aggregate、三者 review、final evidence commit、post-commit clean/head、PR observation をすべて stale にする。影響 owner step の local gate、S99 aggregate、三者 fresh review、新 evidence-only final commit、push、exact-head observation を新 HEAD で再実行する。
* repair が S01〜S95 の所有 path またはその contract を変更した場合、その step の既存 closure/reviewer evidence も stale とし、該当 step gate から戻す。
* 予定された `REVIEW_HEAD` 後の final evidence commit は、`REVIEW_HEAD..FINAL_HEAD` が report/review artifact のみである場合に限り、非循環 closure commit として三者 review を失効させない。
* PR body/comment の変更だけで branch SHA が変わらなければ aggregate/review は失効しない。ただし observation boundary は再確認する。
* rebase、merge-main、repair commit、report の追加 commit は branch mutation であり、旧 exact-head observation は無効。
* P2/P3 だけなら branch mutation を行わず、採否と残余リスクを記録する。P0/P1、required CI failure、visible conflict だけが自律的 repair scope である。

## Risks

**仮定**

* S01〜S95 の user-provided pass results は、connector で確認した report の確定値と一致している。
* Codex 実行環境に `git`、`uv`、`make`、`gh` と observation script の実行権限がある。
* report-only review-target commit を先行させ、その後の aggregate/reviews を新 SHA に固定できる。

**不確実性・後続検証対象**

* この回答では commands を実行していない。pass count、runtime、CI、PR platform state は未検証である。
* S95 の raw snapshot/log は repository 外 temporary path に置かれたと report に記録されている。現在も存在するかは未確認であり、失われている場合、S95 before/after no-mutation の独立再検証はできず、committed hashes/evidence summary に依存する。
* `.assurance.json` は Standard authorization を示す一方で `status: provisional` であるため、上記 hash binding と workflow 上の有効性確認が必要である。
* required external checks、branch protection、conversation-resolution requirement は PR 作成後の GitHub observation/UI でしか確定しない。zero Actions runs は CI success の証拠ではない。
* 添付された設計判断文書は別テーマであり、Issue 344 S99 の根拠または closure evidence には採用していない。
