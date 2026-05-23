---
type: synthesis
source: codex
created_at: 2026-05-23T11:52:03+09:00
epic: epic-00112
topic: subagent permission control and depth-2 authoring harness
status: current
inputs:
  - 20260523t115201z-research-deep-consultant-per-agent-permissions-depth2.md
  - 20260523t115202z-research-chatgpt-pro-per-agent-permissions-depth2.md
---

# Synthesis: Subagent Permission Control and Depth-2 Authoring Harness

## conclusion

今回の課題に対するベストプラクティスは、「authoring agent の自律性は広げるが、canonical source of truth の変更権限と final review ownership は狭く保つ」ことである。

採用すべき方向性:

1. `system-architect` / `implementation-planner` は、将来的に write-capable にしてよい。
2. ただし、最初の導入は `discussions/` への中間成果書き込みに限定する。
3. `design.md` / `plan.md` への直接編集は、Permission Profile probe、role-aware diff gate、final review policy が揃った後の段階導入にする。
4. depth=2 delegation は read-only specialist に限定して導入する。
5. write-capable child delegation は禁止する。
6. authoring agent による `spec-reviewer` 直接利用は preflight review として許可する。
7. final spec-reviewer pass、canonical promotion、review finding triage は main orchestrator が所有する。
8. `discussions/` は durable evidence layer として正式化するが、canonical source of truth ではない。

## why_this_matters

現行の `system-architect` / `implementation-planner` は read-only draft evidence を返す設計であり、安全だが、次の限界がある。

- 中間の調査・壁打ち・分析結果が main orchestrator の会話内に残りやすく、永続化されにくい。
- authoring agent 自身が specialist に調査やレビューを依頼できないため、main orchestrator が逐次仲介する必要がある。
- review loop の往復が重く、design / plan の品質を上げるまでの latency が大きい。
- ただし、いきなり canonical writer にすると、requirement / design / plan / implementation の責任境界が崩れやすい。

したがって、権限と責任を同時に広げるのではなく、まず情報収集・分析・pre-review の自律性を広げ、canonical mutation は後から狭く導入する。

## recommended_architecture

### authoring_modes

| Mode | 説明 | Canonical docs write | discussions write | 推奨タイミング |
| --- | --- | --- | --- | --- |
| `readonly-evidence` | 現行互換。draft evidence のみ返す | No | No | fallback / baseline |
| `discussion-authoring` | 中間分析・調査・pre-review を durable evidence として保存する | No | Yes | 最初に導入 |
| `canonical-authoring` | role-owned canonical artifact だけを限定編集する | Yes, exact artifact only | Yes | probe / gate 後 |

### role_write_scope

| Role | Discussion mode write | Canonical mode write | Always denied |
| --- | --- | --- | --- |
| system-architect | active target `discussions/**` | `design.md`, `discussions/**` | `requirement.md`, `plan.md`, implementation, tests, `.codex/**`, config, workflow files, secrets |
| implementation-planner | active target `discussions/**` | `plan.md`, `discussions/**` | `requirement.md`, `design.md`, implementation, tests, `.codex/**`, config, workflow files, secrets |
| spec-reviewer | none | none | all writes |
| repo-analyst | none | none | all writes |
| researcher | none | none | all writes |
| consultant / deep-consultant | none | none | all writes |
| dev-coder | none | approved implementation/test scope | `.codex/**`, agent config, workflow files, secrets unless explicitly approved |

### active_path_handling

Permission Profile や diff gate は `spec-dock/active/...` symlink を直接信頼しない。

Task start 時に次を行う。

1. active target を解決する。
2. canonical target の実体パスを task manifest に固定する。
3. allowed write paths を manifest に列挙する。
4. post-run diff gate は manifest の allowed paths に対して実行する。

## depth2_delegation_policy

depth=2 は「write-capable authoring agent が read-only specialist に調査・レビューを依頼できる」範囲に限定する。

Allowed:

- `system-architect -> repo-analyst`
- `system-architect -> researcher`
- `system-architect -> consultant`
- `system-architect -> deep-consultant`
- `system-architect -> spec-reviewer`
- `implementation-planner -> repo-analyst`
- `implementation-planner -> researcher`
- `implementation-planner -> consultant`
- `implementation-planner -> deep-consultant`
- `implementation-planner -> spec-reviewer`

Denied:

- authoring agent -> `dev-coder`
- authoring agent -> write-capable authoring agent
- child specialist -> any child
- recursive same-role delegation
- generic unrestricted subagent delegation

Caps:

- child agents per parent turn: maximum 3
- `deep-consultant`: maximum 1
- pre-review loops: maximum 2
- child output must be summarized as structured evidence
- adopted / rejected / unresolved evidence must be recorded

## review_ownership

Review ownership must be explicit.

| Stage | Owner | Purpose | Pass meaning |
| --- | --- | --- | --- |
| Draft pre-review | authoring agent | early finding discovery | advisory only |
| Final independent review | main orchestrator | canonical promotion / completion | required gate |

Rules:

- `spec-reviewer` remains read-only.
- `spec-reviewer` called by an authoring agent cannot grant final pass.
- main orchestrator must run or commission final review against actual canonical docs and diff.
- final review can use `discussions/` evidence, but must not rely on it blindly.
- finding disposition must be recorded before promotion.

## discussion_artifact_policy

`discussions/` should become an official evidence layer.

Required metadata:

- `type`
- `source`
- `created_at`
- `epic` or active target id
- `topic`
- `status`
- `inputs`
- `canonical_targets` when relevant
- `supersedes` / `superseded_by` when relevant
- `promotion_decision` when promoted or rejected

Recommended statuses:

- `draft`
- `current`
- `promoted`
- `superseded`
- `rejected`

Promotion criteria:

- traceability to canonical docs.
- evidence and assumptions separated.
- unresolved questions identified.
- review findings disposed.
- main orchestrator approves promotion.
- role-aware diff gate passes.

## permission_profile_adoption

Permission Profiles should be introduced as defense-in-depth, not sole enforcement.

Design constraints:

- Do not mix `default_permissions` / `[permissions]` with old `sandbox_mode` / `sandbox_workspace_write` in the same effective role config.
- Treat `sandbox_workspace_write.writable_roots` as unsuitable for workspace-internal narrowing.
- Probe CLI first.
- Probe Desktop separately before relying on it.
- Probe parent-runtime override behavior.
- Keep read-only evidence mode as fallback.

Minimum probes:

- architect can write `design.md` and `discussions/**`.
- architect cannot write `requirement.md`, `plan.md`, implementation, tests, `.codex/**`, `.env*`.
- planner can write `plan.md` and `discussions/**`.
- planner cannot write `requirement.md`, `design.md`, implementation, tests, `.codex/**`, `.env*`.
- read-only child remains read-only when spawned from write-capable parent.
- max depth and no-grandchild policy are effective.
- Desktop behavior is recorded and not assumed from CLI behavior.

## required_spec_updates

The current epic should be extended with requirements covering:

- role-owned write scope.
- discussion-authoring mode.
- canonical-authoring mode.
- Permission Profile probe and fallback.
- depth=2 allowlist.
- no write-capable child delegation.
- draft pre-review versus final independent review.
- discussion artifact lifecycle.
- task manifest / resolved active path allowlist.
- role-aware diff gate.

Design should add sections for:

- Role Permission Model.
- Permission Profile Threat Model.
- Delegation Graph.
- Review Ownership.
- Discussion Artifact Lifecycle.
- Promotion Flow.
- Probe and Fallback Strategy.

Implementation plan should add staged issues or tasks for:

1. discussion artifact schema and templates.
2. role permission matrix and docs.
3. Permission Profile prototype/probe harness.
4. role-aware diff gate.
5. depth=2 read-only specialist allowlist.
6. preflight review loop protocol.
7. canonical authoring trial for `design.md` / `plan.md`.
8. dogfooding pilot and final review validation.

## final_decision

The best next step is not to immediately rewrite `system-architect` and `implementation-planner` into fully write-capable canonical authors.

Instead, update the epic design and plan toward this phased target:

- Phase 1: discussion-authoring mode.
- Phase 2: limited depth=2 read-only specialist delegation.
- Phase 3: Permission Profile probe and role-aware diff gate.
- Phase 4: canonical authoring trial for `design.md` and `plan.md`.
- Phase 5: dogfooding and reviewer pass before considering this default behavior.

This preserves spec-dock's source-of-truth discipline while enabling higher-quality autonomous research, consultation, pre-review, and context engineering.
