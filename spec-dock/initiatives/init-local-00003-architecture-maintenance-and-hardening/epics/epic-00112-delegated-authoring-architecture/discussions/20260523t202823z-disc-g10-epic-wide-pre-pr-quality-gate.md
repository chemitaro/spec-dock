---
種別: ディスカッション
ID: "20260523t202823z-disc-g10-epic-wide-pre-pr-quality-gate"
タイトル: "G10 Epic-wide pre-PR quality gate evidence"
状態: "draft"
作成者: "Codex"
作成日: "2026-05-23"
関連: ["epic-00112", "#119", "#120", "#121", "#122", "#123", "#124", "#125"]
---

# G10 Epic-wide pre-PR quality gate evidence

## 目的

この記録は、Epic PR #119 を更新する前に、v1 追加 Issue `iss-00120`〜`iss-00125` の実装完了後の全差分を一つの品質ゲートとしてレビューするための共有証跡である。

## PR / diff endpoints

- PR:
  - `#119`
  - URL: `https://github.com/chemitaro/spec-dock/pull/119`
  - title: `Delegated Authoring Architectureを導入`
  - state: `OPEN`
  - draft: `false`
  - mergeable: `MERGEABLE`
- base endpoint:
  - base_ref_name: `main`
  - base_ref_oid: `421fd4c02fd2649b8c29ec9549a961b7824b9149`
- current PR head before update:
  - head_ref_name: `iss-00118-delegated-authoring-dogfooding-pilot`
  - head_ref_oid: `e7741fec10d9548354becb8040913680abd5aa40`
- final local endpoint before PR update:
  - local_branch: `iss-00125-authority-aware-delegated-authoring-dogfooding-pilot`
  - final_pr_update_head: clean `HEAD` at reviewer handoff; this intentionally avoids self-referential evidence hashes.
  - review_scope_note: reviewers must treat `421fd4c02fd2649b8c29ec9549a961b7824b9149...HEAD` as the authoritative PR-bound G10 diff scope.

## Completed v1 issue closure check

| Issue | title | state | closedAt |
| --- | --- | --- | --- |
| `#120` | `Authority Metadata and Promotion Record Schema` | `CLOSED` | `2026-05-23T17:22:37Z` |
| `#121` | `Authority Aware Context Pack and Lifecycle Gates` | `CLOSED` | `2026-05-23T18:20:38Z` |
| `#122` | `Evidence Adoption Ledger and Bounded Depth2 Delegation` | `CLOSED` | `2026-05-23T18:48:42Z` |
| `#123` | `Role Scoped Permission Profiles and Task Manifest Probes` | `CLOSED` | `2026-05-23T19:20:43Z` |
| `#124` | `Canonical Draft Authoring Role Rewrite` | `CLOSED` | `2026-05-23T19:53:38Z` |
| `#125` | `Authority Aware Delegated Authoring Dogfooding Pilot` | `CLOSED` | `2026-05-23T20:25:37Z` |

## Local validation before reviewer handoff

- `git status --short`: clean.
- `./spec-dock/scripts/spec-dock active show`: active not set; fallback points to `spec-dock/system/active-none/{initiative,epic,issue}`.
- `./spec-dock/scripts/spec-dock validate`: `spec-dock: ok (validate) nodes=63`.
- `git diff --check`: pass.
- `python -m unittest discover -v`: `Ran 847 tests in 400.478s` / `OK`.
- `./spec-dock/scripts/spec-dock issue finish` for `iss-00125`: succeeded and ran `issue finish auto-sync`.

Manual `sync` is intentionally not re-run in this G10 evidence step because issue finish already ran auto-sync and active is currently cleared. This avoids reintroducing branch-derived active state during final PR gating.

## Diff scope summary

Command:

```bash
git diff --stat 421fd4c02fd2649b8c29ec9549a961b7824b9149...HEAD
```

Summary:

- `270 files changed`
- `23075 insertions(+)`
- `898 deletions(-)`

High-level changed surfaces:

- Provider install-root assets:
  - `.agents/skills/spec-dock-epic-planning/SKILL.md`
  - new `.agents/skills/spec-dock-system-architect/SKILL.md`
  - new `.agents/skills/spec-dock-implementation-planner/SKILL.md`
  - `.codex/AGENTS.md`
  - new `.codex/agents/system-architect.toml`
  - new `.codex/agents/implementation-planner.toml`
  - `.codex/agents/spec-reviewer.toml`
- Provider docs / templates / active-none scaffolds:
  - `src/spec_dock/assets/spec_dock/docs/**`
  - `src/spec_dock/assets/spec_dock/templates/**`
  - `src/spec_dock/assets/spec_dock/system/active-none/**`
- Provider runtime:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_lifecycle.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`
  - new `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authority.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/active_store.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/contracts.py`
  - `src/spec_dock/cli.py`
- Dogfooding workspace parity:
  - `.agents/**`
  - `.codex/**`
  - `spec-dock/docs/**`
  - `spec-dock/templates/**`
  - `spec-dock/system/active-none/**`
  - `spec-dock/scripts/spec_dock_runtime/**`
- Epic / Issue evidence:
  - new `epic-00112` requirement / design / plan / report / discussions.
  - v0 Issue docs for `iss-00113`〜`iss-00118`.
  - v1 additive Issue docs for `iss-00120`〜`iss-00125`.
- Tests:
  - `tests/test_init_update.py`
  - `tests/cli_runtime/test_issue_lifecycle.py`
  - `tests/cli_runtime/test_runtime_active_s05.py`
  - new `tests/domain_runtime/test_authority.py`
  - `tests/cli_runtime/harness.py`

Name-status command:

```bash
git diff --name-status 421fd4c02fd2649b8c29ec9549a961b7824b9149...HEAD
```

The full name-status output is captured in sibling evidence artifact:

- `discussions/20260523t204806z-disc-g10-full-name-status.md`
- endpoint: `421fd4c02fd2649b8c29ec9549a961b7824b9149...HEAD`
- entry count: `270`

Reviewers must treat that full name-status artifact as the authoritative file-level scope list for the G10 review.

## Required G10 reviews

- Fresh `deep-consultant`:
  - first reviewer: `Euclid the 2nd` (`019e5689-c524-7633-a5ea-4180af5d4986`)
  - consultant_status: fail.
  - initial findings:
    - P1: `spec-dock close <issue>` bypassed the authority gate that `issue finish` enforced.
    - P1: shared G10 evidence omitted the full `git diff --name-status` output.
  - disposition:
    - close bypass: superseded by the explicit close-vs-finish responsibility split. `spec-dock close <target>` is restored as an explicit GitHub issue maintenance close / already-closed check that does not claim lifecycle completion, active clear, or `issue_finish` authority. `spec-dock issue finish` remains the authority-gated lifecycle closure path, with regression coverage in `tests/cli_runtime/test_issue_lifecycle.py`, `tests/domain_runtime/test_authority.py`, `tests/cli_runtime/test_close.py`, and `tests/cli_runtime/test_runtime_close_s12.py`.
    - missing full name-status: fixed by adding `20260523t204806z-disc-g10-full-name-status.md`.
  - first re-reviewer: `Planck the 2nd` (`019e56b2-ddb6-7233-bc48-164a3a485696`)
  - first_re_review_status: pass; previous findings resolved under the final `base...HEAD` scope.
  - final re-reviewer: `Nash the 2nd` (`019e56b9-f3cd-7ca2-b721-0a9022957699`)
  - final_re_review_status: pass; no blocking finding remains in the deep-consultant lane.
  - scope: architecture/workflow risk, hidden coupling, fallback adequacy, rollout quality, and product-quality gaps across the full diff.
- Fresh `spec-reviewer`:
  - first reviewer: `Euler the 2nd` (`019e5689-fa44-71f3-8414-e8d1eab3a5a5`)
  - review_status: fail.
  - initial findings:
    - P1: G10 endpoint was pinned to `2a7dbec...` while the working tree still had uncommitted quality-gate fixes.
    - P1: `iss-00124` / `iss-00125` reports still contained stale pending wording that contradicted Epic E-AC pass claims.
  - disposition:
    - endpoint mismatch: superseded by regenerating this artifact and the full name-status artifact against the PR-bound `base...HEAD` scope.
    - stale issue reports: fixed by additive final closure addenda in the issue-local reports.
  - first re-reviewer: `Galileo the 2nd` (`019e56b3-39e3-7ca2-9af5-8523229256bb`)
  - first_re_review_status: fail.
  - first re-review findings:
    - P1: G10 scope still pointed at `fc80c94...` while the PR-bound clean HEAD also included G10 evidence and executable test-alignment changes.
    - P1: PR remains blocked until deep-consultant re-review pass is recorded.
  - second disposition:
    - final scope alignment: fixed by using `421fd4c02fd2649b8c29ec9549a961b7824b9149...HEAD` as the authoritative PR-bound G10 diff scope and regenerating the full name-status artifact to 270 entries.
    - deep-consultant pass recording: fixed by recording Planck the 2nd's pass above.
  - second re-reviewer: `Boyle the 2nd` (`019e56b9-f454-7e82-a3d7-737fb5ee9821`)
  - second_re_review_status: pass; no specification finding remains and PR #119 is not blocked from the spec-reviewer lane.
  - scope: requirement/design/plan/report alignment, issue closure evidence, additive v1 preservation of v0 history, and whether PR update is blocked by unresolved findings.

## Finding disposition rule

PR update / push remains blocked until every finding from both reviewers has one of:

- `fixed`
- `superseded`
- `explicitly_deferred_with_user_acceptance`

Findings with disposition `open`, `pending`, or `unresolved` block PR update. Fixed or superseded findings require revalidation and fresh re-review against the same G10 scope before PR update.

## Final G10 verdict

- `deep-consultant`: pass.
- `spec-reviewer`: pass.
- unresolved findings: none.
- PR #119 update gate: unblocked.

## Post-PR automated review disposition

- `Codex-P2-tomli-python310`: fixed by declaring `tomli>=2.0.1` for Python `<3.11` and updating `uv.lock`.
- `Codex-P1-close-active-coupling`: fixed by restoring explicit `spec-dock close <target>` as a GitHub issue maintenance command independent of active issue lifecycle state, while preserving `issue finish` as the authority-gated lifecycle closure path.
- targeted verification:
  - `python -m unittest tests.cli_runtime.test_close tests.cli_runtime.test_runtime_close_s12 tests.cli_runtime.test_issue_lifecycle tests.domain_runtime.test_authority -v` -> `Ran 55 tests` / `OK`.
  - `git diff --check` -> pass.
