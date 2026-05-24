---
種別: レポート（Epic）
ID: "epic-00112"
タイトル: "Delegated Authoring Architecture for Spec Workflow"
状態: "approved"
作成者: "Codex"
最終更新: "2026-05-24"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["init-local-00003"]
---

# epic-00112 Delegated Authoring Architecture for Spec Workflow — レポート（進捗 / 決定 / 結果）

## 進捗サマリー (必須)
- 現在地（何が完了し、何が未完か）:
  - v0 delegated authoring implementation is complete as historical work.
  - Requirement phase completed with fresh `spec-reviewer` pass.
  - Design phase completed with fresh `spec-reviewer` pass.
  - Plan phase completed with fresh `spec-reviewer` pass.
  - Child Issues #113..#118 are implemented, committed, and closed.
  - Delegated authoring is shipped as draft-only workflow evidence, role skills, phase gates, Codex thin adapters, and dogfooding pilot evidence.
  - v1 amendment requirement/design/plan authoring is review-passed, and additive Issues `iss-00120`〜`iss-00125` / #120〜#125 are created with approved specs.
  - Additive v1 Issues `iss-00120`〜`iss-00125` / #120〜#125 are historical completed work.
  - Corrective Issue `iss-00126` / #126 is now the active v1 correction for write-capable delegated draft authoring because user review found the prior fallback/read-only implementation did not satisfy the Epic's intended write-capable design/plan draft authoring requirement.
  - `iss-00126` has passed post-promotion `validate` and full-suite verification after its main-orchestrator promotion metadata was recorded. Fresh QA/spec/code findings were then fixed or dispositioned, targeted matrices passed, and post-P1 full-suite rerun passed. The latest code P1 added positive-probe fail-closed enforcement and its focused matrix passed. G10 Epic-wide pre-PR quality gate has deep-consultant, QA, fresh code-reviewer, and fresh spec-reviewer pass results after the latest G10 evidence repair. Final post-report verification also passed: `uv run python -m unittest discover -v` (`Ran 895 tests in 432.904s OK`), `./spec-dock/scripts/spec-dock validate` (`nodes=64`), and `git diff --check`.
- 次のマイルストーン:
  - Update Epic PR #119 and verify post-push PR checks/status.
- ブロッカー:
  - None for the corrective implementation gate. PR #119 update / push and post-push checks remain as delivery steps.

## 決定事項（ADRリンク） (必須)
- No ADR was created in this Epic.
- Durable decisions are reflected in child Issue reports:
  - Delegated author output is draft evidence, not canonical authority.
  - Manual authoring remains valid.
  - Fresh `spec-reviewer` remains required for phase promotion and final closure.
  - `.codex/agents` support is a thin Codex adapter contract.
  - `.github/agents` / Copilot support and role registry expansion remain deferred; write-capable delegated draft authoring is now in-scope through corrective Issue `iss-00126`.
  - `iss-00117` closed as `adapter_contract_only`; live Codex host callability is not claimed.

## Spec Interpretation / Decision Ledger

- v1 amendment status model:
  - decision: Separate `status`, `authority`, normative `grants`, and lifecycle handoff readiness.
  - disposition: accepted.
  - evidence: Requirement / Design Amendment Gate passed by Deep Consultant `Ptolemy` and Spec Reviewer `Meitner`.
- v1 delegated canonical draft authoring:
  - decision: `system-architect` and `implementation-planner` may author draft `design.md` / `plan.md`, but final authority and promotion remain with the main orchestrator plus reviewer gates.
  - disposition: accepted.
  - evidence: Requirement / Design Amendment Gate promotion scope.
- v1 additive planning:
  - decision: Preserve v0 Issue 001〜006 / #113..#118 as historical work and add v1 Issue 007〜012 for authority-aware delegated authoring.
  - disposition: accepted.
  - evidence: Plan Amendment Gate passed by Spec Reviewer `Beauvoir`; historical contract note added to `plan.md`.
- v1 reviewer findings:
  - decision: Per-issue rollout / fallback contracts and concrete Issue 011 provider docs paths are required.
  - disposition: resolved.
  - evidence: `plan.md` v1 Issue 007〜012 include provider source, dogfooding validation surface, test surface, rollback / fallback, and closes mapping.
- v1 execution state:
  - decision: v1 amendment Issues `iss-00120`〜`iss-00125` are historical completed work, but they did not close the user-accepted write-capable delegated draft authoring intent.
  - disposition: superseded for final Epic closure by corrective Issue `iss-00126`.
  - evidence: `iss-00126` requirement/design/plan/report and user follow-up on 2026-05-24.
- v1 Epic-wide pre-PR quality gate:
  - decision: After corrective Issue `iss-00126` completes raw implementation and before Epic PR #119 is updated, run fresh `deep-consultant` and `spec-reviewer` gates over the full development-baseline-to-final-implementation delta.
  - disposition: passed; fresh deep-consultant, QA, code-reviewer, and spec-reviewer gates passed after latest G10 evidence repair.
  - evidence: `iss-00126` plan G10; G10 shared diff artifact; Aristotle deep-consultant approve; Poincare QA pass; Chandrasekhar code-review pass; James spec-review pass; Schrodinger/Gauss/Carson findings dispositioned in `iss-00126` report.

## 完了した Issue / PR / Release (必須)
- #113 Delegated Authoring Policy Foundation: CLOSED.
- #114 Delegated Draft Evidence Schema: CLOSED.
- #115 Delegated Author Role Skills: CLOSED.
- #116 Delegated Authoring Phase Gates: CLOSED.
- #117 Codex Delegated Author Adapters: CLOSED.
- #118 Delegated Authoring Dogfooding Pilot: CLOSED.
- #126 Write Capable Delegated Draft Authoring Correction: OPEN / active correction.
- Epic PR #119 Delegated Authoring Architectureを導入: OPEN, non-draft, mergeable at creation-time audit.

## v0 受け入れ条件（E-AC）の履歴達成状況 (必須)

この節は、完了済み Issue #113..#118 / plan Issue 001〜006 に対する historical v0 evidence です。v1 amendment 後の E-AC 達成状況は次節を正とし、v1 Issue 007〜012 の実装証跡が揃うまで pass 扱いにしません。

- E-AC-001: pass
  - Evidence: #113 added delegated-authoring policy foundation and completed review/finish.
- E-AC-002: pass
  - Evidence: #117 added Codex delegated author adapter contract and dogfooding mirror parity, closed as `adapter_contract_only`.
- E-AC-003: pass
  - Evidence: #115 added system architect and implementation planner role skills and routing coverage.
- E-AC-004: pass
  - Evidence: #118 saved delegated design draft artifact under `discussions/` and recorded canonical integration evidence.
- E-AC-005: pass
  - Evidence: #118 saved delegated plan draft artifact under `discussions/` and recorded canonical integration evidence.
- E-AC-006: pass
  - Evidence: #116 added delegated design/plan authoring gates to phase docs and reviewer criteria.
- E-AC-007: pass
  - Evidence: #118 recorded provider/consumer parity evidence, `validate`, `sync`, and `git diff --check`.
- E-AC-008: pass
  - Evidence: #118 recorded pilot metrics for the historical fallback contract. This v0 evidence is superseded for write-capable acceptance by `iss-00126`.
- E-AC-009: pass
  - Evidence: #118 exercised the real `adapter_contract_only` fallback as negative/blocked-case evidence with `host_invocation_verified=false`.

## v1 Amendment 受け入れ条件（E-AC）の現在状況

- E-AC-001: pass
  - Evidence: `iss-00120` / #120 authority metadata and promotion record schema implementation.
- E-AC-002: pass
  - Evidence: `iss-00121` / #121 proposed-artifact blocking in context-pack and lifecycle gates.
- E-AC-003: pass
  - Evidence: `iss-00126` implemented and dogfooded the actual write-capable `system-architect` draft `design.md` authoring path. The delegated session used the generated issue-cwd Permission Profile, produced substantive non-metadata `design.md` body delta, preserved delegated draft/proposed authority until main promotion, denied requirement/peer/report/source/tests/config/secrets boundaries, and post-promotion `validate` / targeted / full-suite checks passed.
- E-AC-004: pass
  - Evidence: `iss-00126` implemented and dogfooded the actual write-capable `implementation-planner` draft `plan.md` authoring path with approved requirement/design inputs. The delegated session used the generated issue-cwd Permission Profile, produced substantive non-metadata `plan.md` body delta, preserved delegated draft/proposed authority until main promotion, denied requirement/peer/report/source/tests/config/secrets boundaries, and post-promotion `validate` / targeted / full-suite checks passed.
- E-AC-005: pass
  - Evidence: `iss-00120`, `iss-00121`, and `iss-00125` promotion record / lifecycle handoff evidence.
- E-AC-006: pass
  - Evidence: `iss-00122` / #122 evidence adoption ledger with disposition, reflected target, rejected reason, or pending state.
- E-AC-007: pass
  - Evidence: `iss-00122` / #122 bounded depth=2 graph proving child specialists remain leaf-only evidence producers.
- E-AC-008: pass
  - Evidence: `iss-00123` / #123 role-scoped Permission Profile / task manifest probe contract and fallback evidence.
- E-AC-009: pass
  - Evidence: `iss-00122`, `iss-00124`, and `iss-00125` final fresh reviewer evidence proving preflight review is not treated as final pass.
- E-AC-010: pass
  - Evidence: `iss-00125` / #125 rollout evidence showing completed Issue 001〜006 / #113〜#118 plans and reports were not rewritten, and v1 requirements are closed by additive Issues.
- E-AC-011: pass
  - Evidence: `iss-00123` and `iss-00125` provider-first rollout and parity evidence for docs, role skills, host adapter assets, runtime gates, templates, and report scaffolds.
- E-AC-012: pass
  - Evidence: `iss-00120`, `iss-00121`, and `iss-00125` requirement authority prerequisite and lifecycle gate evidence.

## Spec Authoring Gate

### Requirement Gate
- phase: requirement
- reviewer:
  - First fresh `spec-reviewer`: fail.
  - Second fresh `spec-reviewer`: pass with P2.
  - Third fresh `spec-reviewer`: pass, no findings.
- verdict: passed
- promotion:
  - Requirement promoted to design.

### Design Gate
- phase: design
- reviewer:
  - First fresh `spec-reviewer`: fail.
  - Second fresh `spec-reviewer`: fail.
  - Third fresh `spec-reviewer`: pass with P2.
  - P2 was incorporated into the design/domain model before planning.
- verdict: passed
- promotion:
  - Design promoted to plan.

### Plan Gate
- phase: plan
- reviewer:
  - First fresh `spec-reviewer`: fail.
  - Second fresh `spec-reviewer`: pass, no findings.
- verdict: passed
- promotion:
  - Epic proceeded to Issue decomposition and implementation.

## v1 Amendment Spec Authoring Gate（2026-05-23）

この節は、完了済み Issue #113..#118 / plan Issue 001〜006 を上書きしない追加修正ゲート記録です。v1 amendment は、既存実装の履歴を保持したまま、追加 Issue として authority-aware delegated authoring を具体化します。

### Requirement / Design Amendment Gate
- phase: requirement / design amendment
- reviewer / consultant:
  - Deep Consultant `Ptolemy` (`019e551d-b9d8-7411-ad67-313c0961af7b`): `consultant_status: approve`
  - Spec Reviewer `Meitner` (`019e5526-a89f-76b3-b4fb-5a7d74244630`): `review_status: pass`
- verdict: passed
- promotion:
  - v1 requirement / design amendment promoted to additive plan amendment.
- promotion scope:
  - `status` / `authority` / `grants` を分離する。
  - `system-architect` と `implementation-planner` は canonical draft author になれるが、final authority / promotion authority は持たない。
  - implementation / issue ready / issue finish / phase completion は `authority: approved` と対応 grant を必要とする。
  - Permission Profile / task manifest / provider-first rollout / requirement authority prerequisite を gate として扱う。

### Plan Amendment Gate
- phase: plan amendment
- reviewer:
  - Spec Reviewer `Rawls` (`019e552a-3779-71a0-b4d9-a6a5df7986d4`): `review_status: fail`
    - finding: per-issue rollout and fallback contracts were missing.
  - Spec Reviewer `Beauvoir` (`019e552f-f20f-7bf2-96d9-983e3165e4bd`): `review_status: pass`
    - finding: P2 path precision gap for v1 Issue 011 provider docs.
    - resolution: v1 Issue 011 provider source now names the concrete provider doc paths under `src/spec_dock/assets/spec_dock/docs/`.
  - Spec Reviewer `Hilbert` (`019e55ae-7729-7871-af30-7be1cfc03d05`): `review_status: pass`
    - finding: none.
    - reason: v0 Issue 001〜006 / #113〜#118 are preserved as historical work, v1 Issue 007〜012 are mapped to `iss-00120`〜`iss-00125` / #120〜#125 as additive amendment work, and preliminary `iss-00120` work is excluded from Epic plan closure evidence.
- verdict: passed
- promotion:
  - v1 plan amendment is ready for additive Issue execution after the refreshed Epic plan review gate.
- promotion scope:
  - Original plan Issue 001〜006 remains historical v0 work and is not rewritten.
  - v1 Issue 007〜012 correspond to `iss-00120`〜`iss-00125` / #120〜#125 and are additive update / fix Issues.
  - Each v1 Issue records provider source, dogfooding validation surface, test surface, rollback / fallback, and closes mapping.

### Epic-wide Pre-PR Quality Gate
- phase: corrective pre-PR update / final amendment rollout
- amendment reviewer:
  - Historical G10 reviewer passes remain recorded for the pre-`iss-00126` delta only.
  - Current corrective G10 has fresh `deep-consultant`, QA, code-reviewer, and spec-reviewer pass results after the latest G10 evidence repair.
- timing:
  - Run only after `iss-00126` completes raw implementation and issue-local closure evidence.
  - Run before updating, pushing, or refreshing Epic PR #119.
- reviewers:
  - Fresh `deep-consultant`: pass / approve (Aristotle), findings none.
  - Fresh QA: pass (Poincare), findings none.
  - Fresh `code-reviewer`: pass (Chandrasekhar), findings none.
  - Fresh `spec-reviewer`: pass (James), findings none after Carson P2 fixes.
- review scope:
  - Full delta from the captured development baseline to the clean local `HEAD` that includes `iss-00126` and will update PR #119.
  - Provider source, dogfooding workspace parity, runtime/test/docs/templates/skills/agent assets, active reports, validation/sync evidence, and PR rollout evidence.
- pass condition:
  - Every finding from either reviewer receives disposition `fixed`, `superseded`, or `explicitly_deferred_with_user_acceptance`.
  - Fixed or superseded findings are revalidated and re-reviewed until the shared G10 evidence has no unresolved findings.
  - PR update / push is blocked while any finding has disposition `open`, `pending`, or `unresolved`.
- evidence fields to fill at corrective G10:
  - base_ref_name: `main` (`develop` is not a valid local ref; `origin/HEAD -> origin/main`).
  - base_ref_oid: `421fd4c02fd2649b8c29ec9549a961b7824b9149`.
  - head_ref_name: `iss-00125-authority-aware-delegated-authoring-dogfooding-pilot`.
  - local_branch_at_handoff: `iss-00125-authority-aware-delegated-authoring-dogfooding-pilot`.
  - pr_head_ref_at_handoff: `iss-00118-delegated-authoring-dogfooding-pilot`.
  - final_pr_update_head: `4365d38f5d88ac4ace362837ce55fdf8e2d6e404` plus current working-tree changes included in the shared diff artifact before PR update.
  - shared_diff_artifact: `discussions/20260524t043441z-disc-g10-shared-diff-evidence.md`.
  - immutable_committed_diff_command: `git diff --stat 421fd4c02fd2649b8c29ec9549a961b7824b9149...HEAD`; result `270 files changed, 23075 insertions(+), 898 deletions(-)`.
  - immutable_committed_name_status_command: `git diff --name-status 421fd4c02fd2649b8c29ec9549a961b7824b9149...HEAD`; result recorded in `discussions/20260523t204806z-disc-g10-full-name-status.md` with `270` entries.
  - full_name_status_artifact: `discussions/20260523t204806z-disc-g10-full-name-status.md`.
  - working_tree_supplement_artifact: `discussions/20260524t043441z-disc-g10-shared-diff-evidence.md`.
  - validation_commands: `./spec-dock/scripts/spec-dock validate`, `git diff --check`, `git status --short`, `./spec-dock/scripts/spec-dock active show`, `uv run python -m unittest discover -v`.
  - validation_results:
    - `./spec-dock/scripts/spec-dock validate`: pass (`spec-dock: ok (validate) nodes=64`).
    - `git diff --check`: pass.
    - `./spec-dock/scripts/spec-dock active show`: active initiative `init-local-00003`, epic `epic-00112`, issue `iss-00126`.
    - `uv run python -m unittest discover -v`: pass after latest Curie/Ampere P1 repairs (`Ran 892 tests in 436.168s OK`).
    - post-P1 targeted matrix: `uv run python -m unittest tests.domain_runtime.test_authority tests.domain_runtime.test_delegated_authoring tests.cli_runtime.test_delegated_authoring tests.cli_runtime.test_validate tests.cli_runtime.test_runtime_active_s05 tests.cli_runtime.test_issue_lifecycle -v`: pass (`Ran 125 tests in 115.036s OK`).
    - post-Zeno positive-probe authority repair focused matrix: `uv run python -m unittest tests.domain_runtime.test_authority tests.cli_runtime.test_validate tests.cli_runtime.test_issue_lifecycle -v`: pass (`Ran 95 tests in 109.130s OK`).
    - `gh pr view 119 --json baseRefName,baseRefOid,headRefName,headRefOid,url,state,isDraft,mergeable`: pass; PR #119 open, non-draft, mergeable, base `main`, base OID `421fd4c02fd2649b8c29ec9549a961b7824b9149`, PR head OID `4365d38f5d88ac4ace362837ce55fdf8e2d6e404`.
  - deep_consultant_reviewer: Aristotle approve; findings none; residual risk accepted for PR update gate because depth policy is contract/test enforced rather than whole-agent-graph runtime monitoring.
  - spec_reviewer: James pass; findings none after Carson P2 fixes.
  - code_reviewer: Chandrasekhar pass; findings none.
  - findings_disposition_table: Schrodinger P1/P2 fixed; Gauss P1 fixed; Carson P2/P2 fixed and re-reviewed by James.
  - re_review_verdicts: fresh spec/code pass.
  - pr_update_push_evidence: unblocked by corrective G10; pending PR update / push.
- current status:
  - Corrective G10 evidence has been refreshed after `iss-00126` main promotion and full verification, then repaired for immutable base-OID diff evidence after Schrodinger review and exact working-tree scope evidence after Carson review.
  - PR #119 update gate is unblocked by fresh code/spec re-review; push/update and post-push checks remain.

## ロールアウト結果（必要なら） (任意)
- 段階公開の状況:
  - Local dogfooding implementation completed across #113..#118.
  - No external release has been cut yet.
- 監視値（エラー率/レイテンシなど）:
  - Not applicable for this documentation/scaffold workflow Epic.
- 障害/アラート:
  - None.

## フォローアップ（別Issue化） (必須)
- Optional future work:
  - Dedicated Codex host schema/callability verification if the product wants to promote `adapter_contract_only` to verified host invocation.
  - Separate Epic/Issue for `.github/agents` / Copilot support or broader role registry expansion.
- Write-capable delegated draft authoring and runtime validation are no longer follow-up-only items; they are handled by `iss-00126` before this Epic can close.

## 省略/例外メモ (必須)
- Live Codex host invocation is not verified by this Epic.
- `iss-00117` and `iss-00118` intentionally record `adapter_contract_only` / `host_invocation_verified=false`.
- No provider source changes were made during #118; #118 is dogfooding evidence only.
