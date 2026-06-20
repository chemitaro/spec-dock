---
種別: research
ID: "20260620t140307z-research"
タイトル: "Checks API Forbidden Surface Research"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-20"
親: ["iss-00222"]
関連: []
authority: "synthesized"
derived_from: []
reflected_to: []
---

# 20260620t140307z-research Checks API Forbidden Surface Research

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約、用語衝突、edge case など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は source-grounded research evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、用語衝突、edge case、判断への含意を混ぜない。
- local context で解ける疑問は人間に聞かず、この artifact に source-grounding を残す。

## 調査目的 (必須)
- GitHub issue `#222` の要求を、SpecDock 本体の現在実装、provider-side shipped assets、dogfooding mirror、既存テスト、doctor capability probe と突き合わせる。
- Checks API / `statusCheckRollup` / `gh pr checks` 相当の利用箇所を洗い出し、要件定義書・設計書へ採用すべき scope、non-scope、edge case、質問候補を整理する。

## sources / 調査方法 (必須)
- 参照先:
  - GitHub issue `#222`: `GitHub PR観測でChecks APIを完全に使用禁止にする`
  - Active issue docs: `spec-dock/active/issue/{requirement,design,plan,report}.md`
  - Parent docs: `spec-dock/active/initiative/{requirement,design,plan}.md`, `spec-dock/active/epic/{requirement,design,plan}.md`
  - Clarification workflow references: `spec-dock/docs/workflow_clarification.md`, `spec-dock/docs/authoring/decision-routing.md`
  - Provider-side PR observation skill: `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - Provider-side PR observation scripts:
    - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`
    - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py`
    - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh`
    - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_snapshot.py`
  - Dogfooding mirror equivalents under `.agents/skills/github-pr-observation/`
  - Doctor capability probe: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/github_capability_cli.py`
  - Doctor application fallback diagnostics: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/doctor.py`
  - Runtime capability contracts: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
  - Tests:
    - `tests/cli_runtime/test_runtime_doctor_s04.py`
    - `tests/unit/infra/test_init_update.py`
  - Related PR observation issue discussions:
    - `iss-00218` fallback signal discussions
    - `iss-00219` carryover observation discussions
    - `iss-00180` GitHub token capability preflight discussions
- 検証手順:
  - `gh issue view 222 --json number,title,body,state,url,labels,comments`
  - `./spec-dock/scripts/spec-dock active set --id iss-00222 --no-checkout --github`
  - `rg -n "statusCheckRollup|check-runs|check-suites|gh pr checks|pr checks|Checks API|checks api|ci_coverage_limited_to_github_actions|mergeStateStatus" ...`
  - Targeted `sed` reads for active docs, parent docs, PR observation scripts, skill text, doctor capability probe, and focused test ranges.
- 実験条件:
  - Read-only investigation only. No implementation code was changed.
  - One research artifact was created in this issue's `discussions/`.

## facts / 観測できた事実 (必須)
- GitHub issue `#222` states that Checks API / `statusCheckRollup` must be completely forbidden, not merely treated as supplemental or fallback. It explicitly forbids:
  - `GET /repos/{owner}/{repo}/commits/{ref}/check-runs`
  - GraphQL / `gh pr view --json statusCheckRollup`
  - `gh pr checks` equivalent API surface
  - fallback to Checks API when Actions cannot decide CI state
- Issue `iss-00222` canonical docs currently contain only generated scaffolds; the GitHub issue body is the substantive source for initial requirements.
- Parent Epic `epic-00158` is about agent workflow hardening and context surface authority. It requires provider-side shipped assets to be the authority and dogfooding mirror to be validation target.
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md` currently says Checks, commit statuses, and PR status rollup are supplemental observation surfaces. That conflicts with issue `#222`.
- The same skill text says zero Actions workflow runs may pass when readable green external check-runs or commit statuses exist. That conflicts with an Actions-only interpretation unless commit statuses are explicitly retained as allowed.
- `pr_observation_checks.py` currently maps `gh_pr_view.statusCheckRollup`, `/check-runs`, and `/status` into capability names and treats their failures as limitations.
- `pr_observation_checks.py` currently calls:
  - `gh pr view <pr> --repo <repo> --json mergeStateStatus,statusCheckRollup`
  - `gh api repos/<repo>/commits/<sha>/check-runs --paginate`
  - `gh api repos/<repo>/commits/<sha>/status --paginate`
  - `gh api repos/<repo>/actions/runs?head_sha=<sha> --paginate`
  - `gh api repos/<repo>/actions/runs/<run_id>/jobs --paginate`
- `pr_observation_checks.py` currently downgrades unavailable supplemental Checks/status/rollup coverage to an informational `ci_coverage_limited_to_github_actions` limitation when Actions evidence is decisive.
- `pr_observation_checks.py` currently uses `statusCheckRollup` and `mergeStateStatus` to compute:
  - `required_check_state`
  - `required_checks_missing_or_pending`
  - `pr_merge_state_blocking`
  - required check pending/running/failed decisions
- `pr_observation_checks.py` currently permits pass based on external green check-runs or commit statuses when Actions has zero runs in some cases.
- `fetch_pr_checks_snapshot.sh` usage text currently says it collects "check runs, commit statuses, and fixed GitHub Actions failure detail".
- `fetch_pr_observation_snapshot.sh` itself delegates CI collection to `fetch_pr_checks_snapshot.sh`; the aggregate snapshot inherits the forbidden surface behavior through that collector.
- Provider-side and dogfooding mirror `github-pr-observation` scripts are duplicated. A shipped asset change must update provider source and verify mirror parity or intentionally refresh dogfooding mirror.
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/github_capability_cli.py` currently includes core probes for:
  - `check_runs_read`: `GET /repos/{repo}/commits/{sha}/check-runs`
  - `commit_statuses_read`: `GET /repos/{repo}/commits/{sha}/status`
  - `status_check_rollup_read`: `gh pr view --json statusCheckRollup`
  - `actions_read` only as an extended probe
- `doctor.py` currently creates target-unavailable and gateway-unavailable diagnostics with `capability="check_runs_read"`. That conflicts with making Checks read a forbidden/non-required surface.
- `tests/cli_runtime/test_runtime_doctor_s04.py` asserts check-runs and status rollup diagnostics, including unknown `statusCheckRollup` schema handling.
- `tests/unit/infra/test_init_update.py` contains many fixtures expecting calls to check-runs and `statusCheckRollup`, and many tests intentionally asserting supplemental behavior:
  - `test_issue_187_actions_only_green_passes_with_coverage_limitation`
  - `test_issue_187_status_rollup_failure_blocks_actions_green`
  - `test_issue_187_status_rollup_running_blocks_actions_green`
  - `test_issue_180_s02_checks_collector_maps_integration_permission_denied`
  - `test_issue_180_s02_checks_collector_maps_status_check_rollup_permission_denied`
  - `test_issue_187_s202_zero_actions_runs_with_green_check_runs_can_pass`
  - `test_issue_187_s202_zero_actions_runs_with_green_commit_status_can_pass`
  - `test_issue_187_snapshot_propagates_actions_pass_with_informational_supplemental_permission`
  - `test_issue_187_wait_preserves_actions_pending_with_informational_supplemental_permission`
- Existing historical discussions for `iss-00218`, `iss-00219`, and `iss-00180` contain manual observation evidence using `gh pr checks`, `statusCheckRollup`, or check-runs. Those are historical evidence and should not be rewritten, but future instructions/docs should not recommend those surfaces.

## inference / 推測 (必須)
- 事実から推測したこと:
  - This issue is a contract inversion, not a small permission handling tweak. Existing tests that protected supplemental Checks/status/rollup behavior must be rewritten or replaced.
  - The implementation should make GitHub Actions workflow runs/jobs the sole CI collection source for PR observation. If Actions cannot decide, output should report Actions observation unavailable/unknown rather than falling back to check-runs or status rollup.
  - `ci_coverage_limited_to_github_actions` should disappear from normal output because Actions-only coverage is no longer a limitation; it is the designed scope.
  - Doctor capability probing should move `actions_read` into the normal/core expectation and remove Checks/status rollup probes from the required/default profile.
  - A guard test should fail if any PR observation script invokes `/check-runs`, `statusCheckRollup`, or `gh pr checks` equivalent commands.
  - Existing `commit_statuses_read` is adjacent to the forbidden surface. GitHub issue `#222` forbids Checks API and `statusCheckRollup` explicitly, and mentions `gh pr checks` equivalent API surface. It does not explicitly forbid commit status `/status`, but the purpose says CI state should use Actions workflow runs/jobs as the source of truth. The safest design is to remove commit status fallback from PR observation CI decisions as well, unless the user intentionally wants legacy commit statuses retained.
- 推測の根拠:
  - GitHub issue `#222` says "CI 状態の取得は GitHub Actions の workflow runs / jobs を正とする" and "Actions で判定できない場合は、Checks API へ fallback せず、Actions 観測不能として明示する".
  - Current code has explicit supplemental paths and pass logic based on external check/status evidence.
  - Current doctor core probe treats Checks/status rollup as mandatory capability, which is incompatible with "Checks を読まないこと自体が正常系".

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - Whether commit statuses endpoint `GET /repos/{repo}/commits/{sha}/status` should also be removed from PR observation CI decisions, or whether only Checks API / `statusCheckRollup` are forbidden.
  - Whether `mergeStateStatus` alone is allowed if requested without `statusCheckRollup`, and whether PR observation should still use it for mergeability/human-gate hints.
  - Whether historical docs/discussions that mention `gh pr checks` should remain as immutable evidence or receive non-authoritative caveats in a new canonical doc.
  - The exact final naming for the Actions-only non-success limitation when Actions is unavailable, zero, or inconclusive.
- 確認できない理由:
  - The GitHub issue body establishes the high-level direction but does not explicitly classify commit statuses or `mergeStateStatus` without `statusCheckRollup`.
  - Historical issue discussions are evidence records; rewriting them would be a separate policy choice and is not implied by the issue body.

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - Should PR observation also stop reading legacy commit statuses (`GET /repos/{repo}/commits/{sha}/status`), treating Actions workflow runs/jobs as the only CI source?
  - Should PR observation still read `mergeStateStatus` if it does not request `statusCheckRollup`, or should merge-state hints be excluded from this issue's scope?
- pressure-test question として切り出すべき候補:
  - Commit statuses are the highest-impact ambiguity because they affect pass/fail semantics for zero Actions runs and the shape of existing tests. Ask this first.
- 質問せずに解決できた候補:
  - Checks API `/check-runs` must not be called.
  - `statusCheckRollup` must not be requested through `gh pr view` or GraphQL.
  - `gh pr checks` should not be used in PR observation/merge-preparer normal flow.
  - `ci_coverage_limited_to_github_actions` should not remain as a normal limitation code for missing Checks coverage.

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - "Checks API" vs "commit statuses" vs "PR status rollup" vs "CI checks".
- 既存 docs / code / tests / discussions での使われ方:
  - Current `github-pr-observation` skill groups Checks, commit statuses, and PR status rollup as supplemental observation surfaces.
  - Current `pr_observation_checks.py` exposes separate capability names: `check_runs_read`, `commit_statuses_read`, `status_check_rollup_read`, and `actions_read`.
  - GitHub issue `#222` explicitly forbids Checks API and `statusCheckRollup`, while the purpose text promotes Actions workflow runs/jobs as the CI source of truth.
- 判断が必要な理由:
  - If commit statuses remain allowed, zero Actions runs may still pass via legacy statuses, preserving part of the old supplemental model. If commit statuses are removed, zero Actions runs become non-pass unless Actions data appears.

## edge cases / 具体シナリオ (必須)
- edge case:
  - Actions runs are available and all jobs are green; check-runs permission would fail if queried.
  - Actions runs are unavailable because token lacks Actions read.
  - Actions returns zero workflow runs for the head SHA.
  - Actions runs are green but required checks are pending only in `statusCheckRollup`.
  - Actions jobs API is unavailable for one or more workflow runs.
  - A legacy commit status exists but no Actions run exists.
  - Existing historical discussion references `gh pr checks` or `statusCheckRollup`.
- その edge case が requirement / design / plan に与える影響:
  - Green Actions should pass without checking forbidden surfaces and without supplemental limitation.
  - Missing Actions read should produce non-success/unknown with an Actions-specific limitation.
  - Zero Actions runs should likely remain non-pass in Actions-only mode.
  - Required-check state visible only via status rollup should not be consulted; requirement/design must state this is an accepted limitation of the forbidden-surface policy.
  - Historical evidence should remain readable but not become future operator guidance.

## implications / 判断への含意 (必須)
- Requirement implications:
  - Add explicit forbidden surfaces: `/check-runs`, `statusCheckRollup`, `gh pr checks`, and caller/agent instructions that produce equivalent reads.
  - Add explicit allowed CI source: Actions workflow runs and jobs.
  - Add non-success behavior for Actions unavailable/inconclusive, with no fallback to forbidden surfaces.
  - Clarify commit statuses policy through interview before finalizing ACs.
- Design implications:
  - Remove `gh_pr_view()` status rollup collection from `pr_observation_checks.py`.
  - Remove `/check-runs` collection and check-run based failure/pass logic from `pr_observation_checks.py`.
  - Remove `ci_coverage_limited_to_github_actions` emission path.
  - Rework `required_check_state` and merge-state-related blocking semantics so they do not depend on status rollup.
  - Update `fetch_pr_checks_snapshot.sh` usage text to Actions-only CI collection.
  - Update provider-side skill text and dogfooding mirror text.
  - Update doctor capability probe to stop requiring Checks/status rollup and to make Actions read the normal CI capability.
  - Update tests so forbidden `gh` calls are unexpected and fail the fake-gh scripts.
- Plan implications:
  - Start with red tests that assert forbidden calls are not made.
  - Then remove forbidden collectors and update output schema/limitations.
  - Then update doctor probes and docs/skill wording.
  - Then verify provider/mirror parity, focused PR observation tests, doctor tests, `validate`, and `sync`.

## リスク/制約 (任意)
- Removing status rollup means PR observation may no longer know about required checks that are not represented by Actions workflow runs/jobs. This is an intentional product tradeoff if Actions-only is the accepted source of truth.
- If commit statuses remain allowed, the policy may still feel like fallback beyond Actions. If they are removed, some repos using legacy non-Actions status contexts will no longer be merge-prepared by SpecDock PR observation.
- Tests are dense and many fixtures currently bake in forbidden calls. The implementation plan should keep changes narrow and avoid unrelated review-observation behavior changes.
- Provider-side source and dogfooding mirror duplication must be handled intentionally; editing only `.agents/` would not update shipped assets.

## 反映先 (任意)
- reflected_to:
  - Pending: `requirement.md`
  - Pending: `design.md`
  - Pending: `plan.md`
  - Pending: `report.md` Evidence Adoption Ledger / Spec Authoring Gate

## 参考（References） (任意)
- GitHub issue `#222`: https://github.com/chemitaro/spec-dock/issues/222
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/github_capability_cli.py`
- `tests/unit/infra/test_init_update.py`
- `tests/cli_runtime/test_runtime_doctor_s04.py`
