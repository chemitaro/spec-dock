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
  - local_head_oid: `2a7dbec2fc7000d4e596d2080312a5c83322c13d`

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
- `./spec-dock/scripts/spec-dock issue finish` for `iss-00125`: succeeded and ran `issue finish auto-sync`.

Manual `sync` is intentionally not re-run in this G10 evidence step because issue finish already ran auto-sync and active is currently cleared. This avoids reintroducing branch-derived active state during final PR gating.

## Diff scope summary

Command:

```bash
git diff --stat 421fd4c02fd2649b8c29ec9549a961b7824b9149...HEAD
```

Summary:

- `262 files changed`
- `22239 insertions(+)`
- `887 deletions(-)`

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

The full name-status output is intentionally not pasted here because it contains 262 entries. Reviewers must use the command above as the authoritative scope list; this artifact records the endpoint and surface summary so both reviews share the same base.

## Required G10 reviews

- Fresh `deep-consultant`:
  - review_status: pending.
  - scope: architecture/workflow risk, hidden coupling, fallback adequacy, rollout quality, and product-quality gaps across the full diff.
- Fresh `spec-reviewer`:
  - review_status: pending.
  - scope: requirement/design/plan/report alignment, issue closure evidence, additive v1 preservation of v0 history, and whether PR update is blocked by unresolved findings.

## Finding disposition rule

PR update / push remains blocked until every finding from both reviewers has one of:

- `fixed`
- `superseded`
- `explicitly_deferred_with_user_acceptance`

Findings with disposition `open`, `pending`, or `unresolved` block PR update. Fixed or superseded findings require revalidation and fresh re-review against the same G10 scope before PR update.
