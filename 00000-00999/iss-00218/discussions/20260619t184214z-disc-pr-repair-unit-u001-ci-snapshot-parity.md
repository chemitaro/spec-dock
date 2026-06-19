---
種別: disc
ID: "20260619t184214z-disc"
タイトル: "PR Repair Unit U001 CI snapshot parity"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-19"
親: ["iss-00218"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260619t184214z-disc PR Repair Unit U001 CI snapshot parity

## 位置づけ
- 用途: 集まった質問回答や調査をもとに、意思決定前の synthesis、選択肢、tradeoff、reflection proposal、ADR candidate triage、推奨反映先を整理する。
- authority default: `proposed`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は synthesis / reflection proposal / adoption target / ADR triage の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 人間から回答を引き出し、回答欄や未回答事項を管理する場合は `interview` を使う。
- 生ログや未整理の思考は `scratch`、事実確認や外部根拠は `research`、長期判断の固定は `adr` に分ける。
- この doc は proposal / synthesis であり、issue `report.md` の observed evidence ledger ではない。採否の最終証跡は canonical docs / ADR / `report.md` Evidence Adoption Ledger に昇格する。
- doc が大きくなりすぎたら、質問回答は `interview`、事実調査は `research`、raw capture は `scratch`、長期決定は `adr` へ分割する。

## 対象論点 (必須)
- 今回整理する論点:
  - U001: PR #220 Provider CI の snapshot/parity failure 5件を、実装意図を変えずに checked-in dogfooding / provider fixture expectation へ反映する。
- この synthesis が必要な理由:
  - merge-preparer workflow では raw CI failure から直接修正せず、repair unit に妥当性・root cause・実装計画・検証計画を記録してから bounded fix を行う必要がある。

## derived question sheets / research (必須)
- `interview`:
  - N/A
- `research`:
  - N/A
- その他の根拠:
  - PR #220 observation result: `/private/tmp/spec-dock-pr220-observation/result.json`
  - Provider CI failed run: https://github.com/chemitaro/spec-dock/actions/runs/27842323053
  - Source batch: `20260619t184139z-pr-repair-batch-pr-repair-batch.md`

## synthesis (必須)
- 合意済みのこと:
  - Issue #218 の implementation / final reviewer gates は local で pass 済み。
  - Provider CI failure は branch の intended files と checked-in snapshot/parity expectations の不一致であり、runtime behavior の新たな仕様拡張ではない。
- 未合意 / 未確定のこと:
  - Codex review usage-limit comment は repo 内修正では解消できない。CI repair 後も review-clean は別途人間判断または再観測が必要。
- source-grounded に解決できたこと:
  - `iss-00218` の `.meta.json` 追加により dogfooding meta snapshot が1件不足している。
  - S90 の provider skill update により `.agents/skills/github-pr-observation/SKILL.md` mirror が stale。
  - S99 の fallback action update により wait/snapshot expectation の一部が stale。
  - `pr_review_snapshot.py` 変更により provider wrapper fixture snapshot が stale。

## 選択肢 / tradeoff (必須)
- Option A:
  - Pros:
    - Checked-in snapshot/parity expectations を現在の intended branch state に更新する。
    - CI failure と実装意図が一致する。
  - Cons:
    - snapshot 更新の diff がやや大きくなる可能性がある。
- Option B:
  - Pros:
    - Provider CI を waiver にする。
  - Cons:
    - merge-prepared predicate に反し、checked-in parity drift を残す。

## reflection proposal (必須)
- canonical docs / workflow / template / skill guidance へ反映すべき候補:
  - なし。これは PR repair の実装証跡であり、canonical requirement/design/plan の変更は不要。
- まだ proposal に留める理由:
  - repair unit は batch に従う作業単位で、最終採否は `report.md` / PR re-observation へ昇格する。

## adoption target / 採用先候補 (必須)
- `requirement.md`:
  - なし
- `design.md`:
  - なし
- `plan.md`:
  - なし
- `ADR`:
  - なし
- `report.md` Evidence Adoption Ledger:
  - Provider CI repair / re-observation evidence として採用する。

## ADR triage / ADR candidate triage (必須)
- ADR candidate か:
  - no
- hard to reverse:
  - no
- surprising without context:
  - no
- real tradeoff:
  - no
- ADR 化しない場合の反映先:
  - `report.md`

## 推奨案 (必須)
- Option A を採用する。Provider CI の5 failure は branch の intended changes に対する snapshot/parity 更新漏れであり、CI を waiver せず checked-in expectations を更新するのが最小かつ正しい。

## Repair Unit Fields

- source_batch: `20260619t184139z-pr-repair-batch`
- unit_id: U001
- covered_ids: I001, I002, I003, I004, I005
- source_links:
  - PR: https://github.com/chemitaro/spec-dock/pull/220
  - Provider CI run: https://github.com/chemitaro/spec-dock/actions/runs/27842323053
  - Observation result: `/private/tmp/spec-dock-pr220-observation/result.json`
- failure_class: `check_failure:provider-tests`
- risk_class: blocking
- disposition: fix-now

### Validity Analysis

- I001: valid. The branch intentionally adds `iss-00218` dogfooding metadata; snapshot list must include it.
- I002/I003: valid/duplicate. Provider skill docs changed and dogfooding `.agents` mirror must match install_root assets for checked-in parity tests.
- I004: valid. `fallback_issue_comment` now maps to `manual_review_required_non_retryable`; an old wait progress expectation still asserted `wait_or_resume`.
- I005: valid. Provider wrapper/entrypoint fixture snapshot is stale after `pr_review_snapshot.py` output shape changed.

### Need-To-Fix Decision

- Fix now. All five failures are deterministic required Provider CI failures.

### Root Cause

- S90/S99 changed shipped observation assets and semantics, and issue execution added dogfooding docs, but CI-enforced checked-in snapshots/mirrors were not updated in the final S99 commit.

### Options Considered

- Update snapshots/parity fixtures now.
- Waive Provider CI.
- Remove dogfooding issue scaffold from the branch.

### Recommended Design

- Update the smallest checked-in parity surfaces required by CI:
  - add the `iss-00218` `.meta.json` path to dogfooding metadata snapshot;
  - sync `.agents/skills/github-pr-observation/SKILL.md` from provider install_root asset;
  - update stale fallback action expectation to `manual_review_required_non_retryable`;
  - refresh the provider wrapper fixture snapshot expected by `test_issue_197_pr_review_snapshot_provider_wrapper_invokes_python_entrypoint`.

### Implementation Plan

1. Inspect failing tests locally with targeted pytest selectors.
2. Update only snapshot/parity expectations and dogfooding mirror files needed for the five failures.
3. Run the five failing tests directly.
4. Run the S99 broad selector and `spec-dock validate` / `git diff --check`.
5. Commit and push the repair, then re-observe PR #220 latest head.

### Validation Plan

- `uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_75_pr_monitor_assets_retired_and_observation_scaffold_present tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_182_s03_wait_progress_uses_decision_current_counts_not_audit_threads tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_197_pr_review_snapshot_provider_wrapper_invokes_python_entrypoint -vv`
- `uv run pytest tests/unit/infra/test_init_update.py -k "github_pr_observation or pr_observation or fallback_issue_comment or no_findings" --maxfail=1`
- `./spec-dock/scripts/spec-dock validate`
- `git diff --check`

### Implementation Result

- Implemented locally.
- Added `iss-00218` `.meta.json` to the checked-in dogfooding metadata snapshot and empty dependency snapshot.
- Synced checked-in `.agents/skills/github-pr-observation/` dogfooding mirror from `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/`.
- Updated the remaining stale fallback expectation from `wait_or_resume` to `manual_review_required_non_retryable`.
- Verified the original five Provider CI failures locally:

```bash
uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_75_pr_monitor_assets_retired_and_observation_scaffold_present tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_182_s03_wait_progress_uses_decision_current_counts_not_audit_threads tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_197_pr_review_snapshot_provider_wrapper_invokes_python_entrypoint -vv

5 passed
```

```bash
uv run pytest tests/unit/infra/test_init_update.py -k "github_pr_observation or pr_observation or fallback_issue_comment or no_findings" --maxfail=1

87 passed, 369 deselected
```

```bash
./spec-dock/scripts/spec-dock validate

spec-dock: ok (validate) nodes=135
```

```bash
git diff --check

pass
```

### Commit Evidence

- pending until repair commit is created

### Re-observation Result

- pending latest-head push and PR #220 re-observation

### Residual Risk / Follow-up

- Provider CI latest-head result is pending until the repair commit is pushed and checks complete.
- Codex review usage limit remains external/human-gate unless a later observation can complete review after quota is available or the user explicitly waives the limitation.

## 推奨反映先 (必須)
- `requirement.md`:
  - なし
- `design.md`:
  - なし
- `plan.md`:
  - なし
- `ADR`:
  - なし
- `report.md` Evidence Adoption Ledger:
  - U001 repair result and re-observation result

## 未採用 / deferred 理由 (必須)
- 未採用:
  - Provider CI waiver: required check failure remains blocking and should not be waived.
- deferred:
  - Codex review usage-limit handling: repo-local repair cannot add usage credits; keep as human-gate / residual risk.

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - なし
- 追加で作る discussion docs:
  - なし
