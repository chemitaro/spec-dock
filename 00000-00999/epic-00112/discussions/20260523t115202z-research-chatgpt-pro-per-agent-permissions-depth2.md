---
type: research
source: chatgpt-pro
created_at: 2026-05-23T11:52:02+09:00
epic: epic-00112
topic: per-agent permissions and depth-2 delegated authoring
status: current
thread_url: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a1192b4-d6c4-83a2-9b56-5d930ec6b055
---

# ChatGPT Pro Research: Per-Agent Permissions and Depth-2 Delegated Authoring

## source_note

This report summarizes the ChatGPT Pro response obtained through Chrome in the Codex-only ChatGPT Project thread above. The response should be treated as external analytical input, not as independently verified repo truth.

## executive_recommendation

ChatGPT Pro recommended staged controlled delegated authoring, not unrestricted delegation.

Core conclusions:

- `system-architect` / `implementation-planner` may become write-capable, but not all at once.
- First rollout should allow `discussions/` writes only.
- Later rollout may allow `system-architect` to edit `design.md + discussions/` and `implementation-planner` to edit `plan.md + discussions/`.
- Permission Profiles should be used as least-privilege workflow guards, not as sole security boundaries.
- depth=2 delegation should be limited to read-only specialists.
- write-capable child delegation should be prohibited.
- authoring agents may run direct `spec-reviewer` draft pre-review loops, but final review remains main-orchestrator-owned.
- `discussions/` should be an evidence incubator with lifecycle metadata, not canonical source of truth.
- Permission Profile adoption must be probe-first, avoid old sandbox mixing, and be backed by CI / Git diff gates.
- Probe failure should fallback immediately to current read-only evidence mode.

## decision_matrix

| 論点 | 推奨判断 | 価値 | リスク | 必須ガード |
| --- | --- | --- | --- | --- |
| `system-architect` write-capable | Yes, staged | 設計往復削減 | requirement / implementation への誤編集 | discussions-only から開始、diff gate |
| `implementation-planner` write-capable | Yes, staged | plan 作成速度と精度向上 | design / code への越境 | discussions-only から開始、diff gate |
| Permission Profile | Yes, not sole boundary | least privilege の機械的表現 | beta / old sandbox conflict / parent override | probe、fallback、role-aware diff gate |
| depth=2 delegation | Limited Yes | specialist 調査を authoring agent 自身が依頼できる | recursive fan-out、責任境界不明 | read-only child only、cap、no recursion |
| authoring agent -> spec-reviewer | Draft loop only | canonical 反映前の欠陥検出 | review independence の形骸化 | final review は main-owned |
| discussions | Yes | durable evidence | stale / canonical 矛盾 | status / superseded / promotion metadata |
| write-capable child | No | 速度は出る | conflict、責任分散、権限境界破壊 | 禁止 |
| canonical promotion | Main-owned | source of truth の一貫性 | main bottleneck | checklist / evidence で軽量化 |

## recommended_role_permission_model

ChatGPT Pro は role permission を `role x mode x active spec path` 単位で設計することを推奨した。

| Mode | system-architect | implementation-planner | 用途 |
| --- | --- | --- | --- |
| `readonly-evidence` | read-only | read-only | 現行互換、probe 失敗時 fallback |
| `discussion-authoring` | `discussions/` のみ write | `discussions/` のみ write | 初期導入、中間成果の永続化 |
| `canonical-authoring` | `design.md + discussions/` のみ write | `plan.md + discussions/` のみ write | probe / CI gate / review policy 確立後 |

### system-architect

Write allowed:

- active spec の `design.md`
- active spec の `discussions/**`

Read allowed:

- active context
- `requirement.md`
- `design.md`
- `plan.md`
- parent docs
- relevant repo implementation files
- workflow / phase / reference docs

Write denied:

- `requirement.md`
- `plan.md`
- implementation files
- tests
- `.codex/**`
- workflow files
- config layers
- secrets / `.env*`

### implementation-planner

Write allowed:

- active spec の `plan.md`
- active spec の `discussions/**`

Read allowed:

- active context
- `requirement.md`
- `design.md`
- `plan.md`
- parent docs
- relevant implementation files
- issue / authoring / phase / dependency docs

Write denied:

- `requirement.md`
- `design.md`
- implementation files
- tests
- `.codex/**`
- workflow files
- config layers
- secrets / `.env*`

## permission_profile_granularity

Suggested profiles:

| Profile | Role | Write scope | Network |
| --- | --- | --- | --- |
| `specdock_architect_discussion_authoring` | system-architect initial | active spec `discussions/**` | disabled |
| `specdock_architect_canonical_authoring` | system-architect promoted | active spec `design.md`, `discussions/**` | disabled |
| `specdock_planner_discussion_authoring` | implementation-planner initial | active spec `discussions/**` | disabled |
| `specdock_planner_canonical_authoring` | implementation-planner promoted | active spec `plan.md`, `discussions/**` | disabled |
| `specdock_repo_analyst_readonly` | repo-analyst | none | disabled |
| `specdock_researcher_readonly_net` | researcher | none | allowlisted only |
| `specdock_reviewer_readonly` | spec-reviewer | none | disabled by default |
| `specdock_dev_coder_workspace` | dev-coder | approved implementation/test scope | disabled or task-specific |

ChatGPT Pro emphasized that Permission Profiles should not be described as a strong security boundary because they mainly constrain local sandboxed command execution and may not cover app connectors, browser, computer-use, MCP, or parent runtime overrides.

## depth2_delegation_policy

Recommended delegation graph:

| Parent | Allowed child | Purpose | Child write |
| --- | --- | --- | --- |
| system-architect | repo-analyst | repo structure / existing implementation constraints | No |
| system-architect | researcher | external / cross-source research | No |
| system-architect | consultant | architecture decision support | No |
| system-architect | deep-consultant | high-stakes tradeoff analysis | No |
| system-architect | spec-reviewer | draft design pre-review | No |
| implementation-planner | repo-analyst | implementation surface / dependency / test strategy | No |
| implementation-planner | researcher | external dependency / migration notes | No |
| implementation-planner | consultant | slicing / risk / rollout strategy | No |
| implementation-planner | deep-consultant | complex sequencing / safety tradeoff | No |
| implementation-planner | spec-reviewer | draft plan pre-review | No |

Forbidden graph:

- `system-architect -> dev-coder`
- `implementation-planner -> dev-coder`
- `system-architect -> write-capable planner`
- `implementation-planner -> write-capable architect`
- recursive same-role spawn
- child specialist spawning further child

Operational caps:

- Maximum 3 child agents per authoring parent turn.
- Maximum 1 `deep-consultant` call per authoring parent turn.
- `researcher` only when web/external confirmation is actually needed.
- child output must be structured evidence, not raw logs.
- parent must record adopted / rejected / unresolved child evidence in `discussions/`.
- parent must distill child evidence before canonical promotion.

## review_loop_ownership

ChatGPT Pro recommended splitting review into two types.

| Review type | Caller | Purpose | Canonical gate |
| --- | --- | --- | --- |
| Draft pre-review | system-architect / implementation-planner | early defect detection | No |
| Final independent review | main orchestrator | canonical promotion / task completion | Yes |

Final independent review conditions:

- reviewer reads canonical docs and diff directly.
- reviewer may consult discussion evidence but must not accept it blindly.
- unresolved P0/P1 findings block promotion.
- authoring-agent-reported pass is not a final pass.
- main orchestrator triages findings and re-delegates if needed.

## discussion_artifact_policy

ChatGPT Pro recommended treating `discussions/` as non-canonical durable evidence.

Canonical source of truth:

- `requirement.md`
- `design.md`
- `plan.md`
- parent docs
- workflow / phase / reference docs

Durable non-canonical evidence:

- `discussions/**`

Temporary / non-durable:

- raw command output
- exploratory scratch
- large logs
- failed prompt debris
- untriaged child output

Recommended frontmatter:

```yaml
---
kind: discussion
spec_id: <active-spec-or-epic-id>
phase: requirement|design|plan|implementation|review
owner_role: system-architect|implementation-planner|repo-analyst|researcher|consultant|deep-consultant|spec-reviewer|main-orchestrator
status: draft|current|promoted|superseded|rejected
canonical_targets:
  - design.md
  - plan.md
source_inputs:
  - requirement.md
  - design.md
  - plan.md
  - parent-docs
created_at: <ISO-8601>
updated_at: <ISO-8601>
supersedes: []
superseded_by: []
promotion_decision: pending|promoted|not-promoted
promoted_by: null
review_evidence: []
---
```

Promotion criteria:

- traceability to requirement / design / plan / parent docs.
- evidence quality and uncertainty separation.
- conflict check against existing canonical docs.
- review status / finding disposition.
- main promotion decision.
- role-aware diff hygiene.

## risk_assessment

Key risks identified:

- Permission Profiles are beta / active development.
- Permission Profiles should not be mixed with old `sandbox_mode` / `sandbox_workspace_write`.
- old `sandbox_workspace_write.writable_roots` adds writable roots and does not restrict workspace-internal write scope.
- subagents inherit or can receive reapplied parent sandbox / approval runtime state.
- permission enforcement surfaces differ across local commands, MCP, connectors, browser, and computer-use.
- Desktop and CLI behavior may differ and must be probed.
- OS-level enforcement can differ across macOS, Linux, WSL, and Windows.

Recommended defense-in-depth layers:

| Layer | Guarantees | Does not guarantee |
| --- | --- | --- |
| Permission Profile | local sandboxed command read/write/network constraints | intent, MCP, connectors, parent override, review correctness |
| Role instructions | responsibility and forbidden actions | hard enforcement |
| Discussion policy | evidence lifecycle | canonical correctness |
| Final spec-reviewer | defect detection | completeness |
| Git diff gate | actual changed path scope | external side effects |
| CI | repository invariants | authoring judgment correctness |

## phased_rollout

### phase_0_baseline_freeze

- snapshot current read-only role policy.
- define role writable path matrix.
- preserve fallback to read-only evidence mode.
- document final review ownership first.

### phase_1_discussions_only_authoring

- allow `system-architect` / `implementation-planner` to write only `discussions/**`.
- main orchestrator remains canonical integrator.
- validate discussion frontmatter and unauthorized canonical diffs.

### phase_2_limited_depth2_readonly_delegation

- enable authoring agents to call read-only specialists.
- enforce child allowlist, max child count, no recursive delegation.
- store child evidence summaries in `discussions/`.

### phase_3_canonical_authoring_for_design_plan

- allow `system-architect` to write `design.md + discussions/**`.
- allow `implementation-planner` to write `plan.md + discussions/**`.
- require Permission Profile probes, role-aware diff gates, and final orchestrator-owned spec-reviewer pass.

### phase_4_hardening_and_productization

- template role profiles.
- template discussion schema.
- add `spec-dock doctor` or equivalent probes.
- document Desktop / CLI differences and fallback modes.

## tests_and_acceptance_criteria

Required probes:

- architect allow/deny probe:
  - `design.md` write succeeds.
  - `discussions/test.md` write succeeds.
  - `requirement.md`, `plan.md`, source files, `.codex/config.toml`, `.env*` writes fail.
- planner allow/deny probe:
  - `plan.md` write succeeds.
  - `discussions/test.md` write succeeds.
  - `design.md`, implementation files writes fail.
- old sandbox conflict probe:
  - `default_permissions` and old sandbox settings do not silently coexist.
- subagent inheritance probe:
  - read-only child remains read-only under write-capable parent.
  - parent runtime override behavior is measured.
- Desktop vs CLI probe:
  - CLI explicit profile passes.
  - project-local profile passes.
  - Desktop behavior is recorded; failure triggers fallback.
- depth probes:
  - max depth and fan-out caps behave as expected.
  - child specialist cannot spawn grandchild.

Role-aware diff gate should fail when:

- role writes outside allowlist.
- canonical doc changes without promotion metadata.
- final spec-reviewer pass is missing.
- discussion frontmatter is invalid.
- Permission Profile config mixes beta profile and old sandbox settings.
- write-capable agent config enables unexpected network access.
- read-only specialist has write-capable permission.

## docs_templates_agents_skills_changes_needed

Requirements to add:

- role-specific authoring agents must not edit outside owned artifact and `discussions/`.
- Permission Profiles are workflow guards, not sole enforcement.
- depth=2 delegation is limited to read-only specialists.
- authoring agents may request draft review; final review is main-owned.
- discussions are durable non-canonical evidence with lifecycle metadata.
- canonical promotion requires traceability, review disposition, and main decision.
- fallback to read-only evidence mode is required.
- CLI/Desktop/OS permission behavior must be probed before canonical authoring.

Design sections to add:

- Delegated Authoring Architecture
- Role Permission Model
- Permission Profile Threat Model
- Depth=2 Delegation Graph
- Review Ownership and Independence
- Discussion Artifact Lifecycle
- Promotion Flow
- Fallback Modes
- CI / Diff Gate Enforcement

Agent / skill changes:

- `system-architect` should become mode-aware: readonly, discussion-authoring, canonical-authoring.
- `implementation-planner` should become mode-aware with plan-specific gates.
- `spec-reviewer` should distinguish draft pre-review from final independent review.
- `repo-analyst`, `researcher`, `consultant`, `deep-consultant` should stay read-only and return structured evidence.
- Add or update helper skills for discussion artifact management, permission probes, role diff gates, and review finding disposition.

## final_recommendation

ChatGPT Pro's final recommendation:

- Adopt Permission Profiles for role-specific delegated authoring.
- Treat them as least-privilege workflow guards plus review/diff enforcement, not hard security boundaries.
- Start with discussions-only authoring.
- Allow depth=2 only for read-only specialists.
- Prohibit write-capable child delegation.
- Let authoring agents run draft pre-review loops, but keep final review / promotion / review integration under the main orchestrator.
- Make `discussions/` an evidence incubator with frontmatter, promotion, and superseded policy.
- Run probes before enabling canonical authoring.
- Fall back to read-only evidence mode when probes fail.
