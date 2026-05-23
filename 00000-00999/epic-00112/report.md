---
種別: レポート（Epic）
ID: "epic-00112"
タイトル: "Delegated Authoring Architecture for Spec Workflow"
状態: "approved"
作成者: "Codex"
最終更新: "2026-05-23"
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
  - Additive v1 Issues `iss-00120`〜`iss-00125` / #120〜#125 are implemented, issue-finished, and closed.
  - G10 Epic-wide pre-PR quality gate is now running against the full `main` baseline to fixed implementation endpoint delta before PR #119 is updated.
- 次のマイルストーン:
  - Complete fresh `deep-consultant` and `spec-reviewer` review for G10, resolve all findings, re-review as needed, then update Epic PR #119.
- ブロッカー:
  - None for v0 historical implementation closure.
  - PR #119 update is blocked until G10 has no unresolved `deep-consultant` / `spec-reviewer` findings.

## 決定事項（ADRリンク） (必須)
- No ADR was created in this Epic.
- Durable decisions are reflected in child Issue reports:
  - Delegated author output is draft evidence, not canonical authority.
  - Manual authoring remains valid.
  - Fresh `spec-reviewer` remains required for phase promotion and final closure.
  - `.codex/agents` support is a thin Codex adapter contract.
  - `.github/agents` / Copilot support, write-capable delegation, runtime validation, and role registry expansion remain deferred.
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
  - decision: v1 amendment Issues are created, approved, implemented, issue-finished, and closed.
  - disposition: accepted.
  - evidence: `iss-00120`〜`iss-00125` / #120〜#125 closure plus issue-local reports and implementation commits through `fc80c94bb97995e1c9e963bcb7886f53f43fa47d`.
- v1 Epic-wide pre-PR quality gate:
  - decision: After all v1 Issues complete raw implementation and before Epic PR #119 is updated, run fresh `deep-consultant` and `spec-reviewer` gates over the full development-baseline-to-final-implementation delta.
  - disposition: accepted.
  - evidence: user follow-up on 2026-05-24; `plan.md` now defines G10 Epic-wide pre-PR quality gate and final exit contract.

## 完了した Issue / PR / Release (必須)
- #113 Delegated Authoring Policy Foundation: CLOSED.
- #114 Delegated Draft Evidence Schema: CLOSED.
- #115 Delegated Author Role Skills: CLOSED.
- #116 Delegated Authoring Phase Gates: CLOSED.
- #117 Codex Delegated Author Adapters: CLOSED.
- #118 Delegated Authoring Dogfooding Pilot: CLOSED.
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
  - Evidence: #118 recorded pilot metrics and `write-capable delegation remains deferred`.
- E-AC-009: pass
  - Evidence: #118 exercised the real `adapter_contract_only` fallback as negative/blocked-case evidence with `host_invocation_verified=false`.

## v1 Amendment 受け入れ条件（E-AC）の現在状況

- E-AC-001: pass
  - Evidence: `iss-00120` / #120 authority metadata and promotion record schema implementation.
- E-AC-002: pass
  - Evidence: `iss-00121` / #121 proposed-artifact blocking in context-pack and lifecycle gates.
- E-AC-003: pass
  - Evidence: `iss-00124` / #124 `system-architect` draft `design.md` authoring contract with `authority: proposed` and no promotion authority.
- E-AC-004: pass
  - Evidence: `iss-00124` / #124 `implementation-planner` draft `plan.md` authoring contract with approved design revision reference, `authority: proposed`, and no promotion authority.
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
- phase: pre-PR update / final amendment rollout
- amendment reviewer:
  - Fermat (`019e55c0-c71f-7302-bcd1-97a3097b1f20`) `review_status: fail`.
    - findings: baseline/final endpoints were not pinned; non-blocking findings could remain unresolved; report evidence fields were incomplete.
    - disposition: fixed by pinning PR #119 `baseRefOid...HEAD`, requiring disposition for every finding, and adding G10 evidence fields.
  - Huygens (`019e55c4-4735-7540-a831-936cc9f47d50`) `review_status: pass`.
    - finding: none.
    - reason: G10 now defines shared diff endpoints/evidence and blocks PR update until all findings have accepted dispositions.
- timing:
  - Run only after `iss-00120`〜`iss-00125` complete raw implementation and issue-local closure evidence.
  - Run before updating, pushing, or refreshing Epic PR #119.
- reviewers:
  - Fresh `deep-consultant`: first review failed; findings fixed; re-review pending.
  - Fresh `spec-reviewer`: first review failed; findings fixed; re-review pending.
- review scope:
  - Full delta from captured Epic PR #119 `baseRefOid` to completed v1 implementation endpoint `fc80c94bb97995e1c9e963bcb7886f53f43fa47d`.
  - Provider source, dogfooding workspace parity, runtime/test/docs/templates/skills/agent assets, active reports, validation/sync evidence, and PR rollout evidence.
- pass condition:
  - Every finding from either reviewer receives disposition `fixed`, `superseded`, or `explicitly_deferred_with_user_acceptance`.
  - Fixed or superseded findings are revalidated and re-reviewed until the shared G10 evidence has no unresolved findings.
  - PR update / push is blocked while any finding has disposition `open`, `pending`, or `unresolved`.
- evidence fields to fill at G10:
  - base_ref_name: `main`.
  - base_ref_oid: `421fd4c02fd2649b8c29ec9549a961b7824b9149`.
  - head_ref_name: `iss-00125-authority-aware-delegated-authoring-dogfooding-pilot`.
  - implementation_head_oid_after_g10_fixes: `fc80c94bb97995e1c9e963bcb7886f53f43fa47d`.
  - evidence_artifact_commit_oid: use clean `git rev-parse HEAD` at reviewer handoff; this avoids self-referential evidence hashes.
  - shared_diff_artifact: `discussions/20260523t202823z-disc-g10-epic-wide-pre-pr-quality-gate.md`.
  - full_name_status_artifact: `discussions/20260523t204806z-disc-g10-full-name-status.md`.
  - diff_stat_command: `git diff --stat 421fd4c02fd2649b8c29ec9549a961b7824b9149...fc80c94bb97995e1c9e963bcb7886f53f43fa47d`
  - diff_name_status_command: `git diff --name-status 421fd4c02fd2649b8c29ec9549a961b7824b9149...fc80c94bb97995e1c9e963bcb7886f53f43fa47d`
  - validation_commands: `./spec-dock/scripts/spec-dock validate`, `git diff --check`, `git status --short`, `./spec-dock/scripts/spec-dock active show`, `python -m unittest discover -v`.
  - validation_results: `spec-dock: ok (validate) nodes=63`; `git diff --check` pass; active not set with active-none fallback; `python -m unittest discover -v` ran 847 tests in 415.583s and passed.
  - deep_consultant_reviewer: `Euclid the 2nd` (`019e5689-c524-7633-a5ea-4180af5d4986`) first review `fail`; fixed findings pending re-review.
  - spec_reviewer: `Euler the 2nd` (`019e5689-fa44-71f3-8414-e8d1eab3a5a5`) first review `fail`; fixed findings pending re-review.
  - findings_disposition_table:
    - `DC-P1-close-bypass`: fixed by `fc80c94bb97995e1c9e963bcb7886f53f43fa47d` (`close_node` issue-target authority gate plus regression tests).
    - `DC-P1-missing-full-name-status`: fixed by `20260523t204806z-disc-g10-full-name-status.md`.
    - `SR-P1-dirty-endpoint`: fixed by `fc80c94bb97995e1c9e963bcb7886f53f43fa47d` and refreshed G10 endpoint evidence.
    - `SR-P1-stale-issue-report-wording`: fixed by additive final closure addenda in `iss-00124` and `iss-00125` reports.
  - re_review_verdicts: pending.
  - pr_update_push_evidence: pending.
- current status:
  - Running; all v1 Issues are closed, first-round G10 findings are fixed in local evidence, and PR #119 update remains blocked until fresh re-review passes.

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
  - Separate Epic/Issue for write-capable delegation, runtime validation, role registry, or `.github/agents` / Copilot support.
- Current Epic does not require these follow-ups for closure because they are explicitly out of scope or deferred.

## 省略/例外メモ (必須)
- Live Codex host invocation is not verified by this Epic.
- `iss-00117` and `iss-00118` intentionally record `adapter_contract_only` / `host_invocation_verified=false`.
- No provider source changes were made during #118; #118 is dogfooding evidence only.
