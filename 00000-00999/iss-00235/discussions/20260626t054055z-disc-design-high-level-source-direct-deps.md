---
種別: disc
ID: "20260626t054055z-disc"
タイトル: "Design: High Level Source Direct Deps"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-26"
親: ["iss-00235"]
関連: []
authority: "proposed"
created_by_role: system-architect
scope_id: iss-00235
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/discussions/20260623t162536z-research-high-level-source-dependency-projection-root-cause.md
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/models.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/contracts.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/deps_reader.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/check_deps.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py
  - tests/unit/application/test_check_deps.py
  - tests/unit/presentation/test_runtime_sync_s07.py
  - tests/unit/presentation/test_deps_raw_puml.py
  - tests/cli_runtime/test_runtime_deps_s04.py
intended_targets:
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pass
derived_from:
  - "iss-00235 requirement.md, 最終更新 2026-06-26"
  - "20260623t162536z-research root-cause discussion"
---

# 20260626t054055z-disc Design: High Level Source Direct Deps

This is delegated draft architecture evidence only. It proposes a design for `iss-00235` and does not claim canonical authority, implementation readiness, reviewer pass, or adoption.

## 1. Requirement Coverage
- Covers AC-001 and AC-002 by adding a first-class `deps check --id <initiative|epic>` contract for direct high-level source dependencies, including unresolved non-ready status.
- Covers AC-003 by adding complete raw direct edge audit data to `.agent/index-all.json`, including source and target node kinds.
- Preserves AC-004 by keeping issue-source readiness behavior and `effective_depends_on` semantics issue-centered.
- Respects prohibitions: no synthetic issue nodes, no `.meta.json.depends_on` storage change, no conversion of `deps-issues.json` into a complete raw graph dump, no `deps-raw.puml` contract expansion in this issue.

## 2. Existing Context Findings
- `deps_reader.load_node_dependency_resolutions()` and `load_issue_depends_on_map()` can read raw direct node dependencies from `.meta.json.depends_on`.
- `load_issue_depends_on_map()` stores `raw_node_depends_on_map[src_id]`, then projects source nodes to issue ids using `_issue_ids_for_dep_node()`.
- When a source `initiative` or `epic` has no descendant issues, `src_issue_ids` is empty and dependency context creation is skipped. The raw edge remains in memory but does not reach readiness evaluation.
- `domain.deps.evaluate_readiness()` and `inspect_target_deps()` are keyed around target issue ids and `DepsDependencyContext.source_issue_id`, so high-level source nodes are not first-class readiness sources.
- `presentation.json_state.render_deps_check_json()` exposes `effective_depends_on`, blockers, node blockers, satisfied dependencies, and dependency contexts, but there is no field for direct node-source dependencies.
- `.agent/index-all.json` currently reports issue readiness data and issue edges under `deps.issue_edges`; it does not include complete raw direct edges with node kinds.
- `deps-raw.puml` is an active visual/debug projection. Tests intentionally omit done/satisfied edges in several cases, so it should not become the complete raw audit surface for this issue.

## 3. Design Decisions
- Treat raw direct dependencies and issue readiness dependencies as separate projections from the same stored metadata.
- Introduce a domain-level raw edge shape, conceptually `RawDirectDependencyEdge`, with at least `source_node_id`, `source_node_kind`, `target_node_id`, `target_node_kind`, and `relation: "raw_direct"`.
- Introduce a domain-level high-level source inspection shape, conceptually `DirectNodeDependencyStatus`, for `deps check --id <initiative|epic>` when the target node itself has direct raw dependencies.
- Keep `effective_depends_on` as issue readiness closure only. Do not put high-level source direct dependencies into it unless they compile to issue blockers through the existing issue projection.
- For direct high-level source dependencies, `deps check` should set top-level `ready: false` when any direct dependency has `dependency_disposition` of `blocking` or `indeterminate`.
- For compatibility with simple consumers, top-level `blockers` should include unresolved direct dependency target ids. The detailed shape should live in a new additive field, not by overloading `dependency_contexts`.
- Add complete raw direct edges to `.agent/index-all.json` under `deps.raw_direct_edges`. Do not rely on per-node `depends_on`, because `depends_on` is already used elsewhere as readiness-oriented dependency output.
- Leave `.agent/index.json` unchanged unless the main design chooses to expose active raw edges there later. The requirement names `.agent/index-all.json` as the full-history audit surface.

## 4. Alternatives Considered
- Synthetic/fake issue for each high-level source: rejected because it violates the requirement and would leak fake nodes into readiness, artifacts, and user workflows.
- Blindly reuse the issue-source projection by forcing `source_issue_id` for high-level sources: rejected because the current failure is caused by issue-keyed projection assumptions, and a placeholder source issue would make ownership and readiness semantics ambiguous.
- Expand high-level source direct dependencies to all descendant issues: rejected as the primary contract because it hides the parent node's direct edge and creates duplicate or misleading blockers for non-empty sources.
- Put raw high-level dependencies into `effective_depends_on`: rejected because `effective_depends_on` currently means issue-level readiness blockers/closure and would become ambiguous.
- Convert `deps-issues.json` into a complete raw node graph: rejected because it is the issue readiness artifact and downstream tooling expects issue-centric nodes, edges, and dependency contexts.
- Make `deps-raw.puml` the complete audit artifact: rejected for this issue because current tests and behavior treat it as active visual output that can omit satisfied/done raw edges.

## 5. Boundary / Contract Model
- Storage contract remains `.meta.json.depends_on`: direct refs are stored per source node and resolved by `deps_reader`.
- Raw audit contract is node-keyed and complete: every resolved direct edge from `.meta.json.depends_on` is inspectable regardless of blocker/satisfied status.
- Readiness contract remains status-aware: readiness can suppress satisfied dependencies, block on unresolved dependencies, or mark indeterminate dependencies without deleting raw audit evidence.
- `deps check --id <initiative|epic>` contract:
  - If the high-level target node itself has direct raw dependencies, include them in `direct_node_dependencies`.
  - Each entry should include source id/kind, target id/kind, lifecycle state/source, disposition, basis, and expansion information for target descendants when applicable.
  - Top-level `ready` is `false` if any direct node dependency is `blocking` or `indeterminate`.
  - Top-level `blockers` includes unresolved direct target node ids.
  - `effective_depends_on` continues to report only issue-level effective blockers for descendant issue readiness.
- `.agent/index-all.json` contract:
  - Add `deps.raw_direct_edges`.
  - Shape: `{ "from": "...", "from_kind": "initiative|epic|issue", "to": "...", "to_kind": "initiative|epic|issue", "relation": "raw_direct" }`.
  - Include satisfied/done/closed dependencies and edges whose source or target is high-level.

## 6. Dependency Analysis
- `infra.deps_reader` is the source of raw resolved dependencies and should remain responsible for resolving refs and validating storage-level refs.
- `application.check_deps` needs both projections: issue topology for existing readiness and raw direct edges/statuses for target node source inspection.
- `application.sync_state` already carries `raw_node_depends_on_map`; it can derive complete raw edge payloads without changing storage.
- `domain.deps` should own disposition rules for direct node dependencies so CLI and sync output agree on blocking/satisfied/indeterminate semantics.
- `presentation.json_state` should render the new additive JSON fields while keeping existing fields stable.

## 7. Source of Record
- Canonical requirement source: `spec-dock/active/issue/requirement.md`, `iss-00235`, last updated `2026-06-26`.
- Root-cause evidence source: `spec-dock/active/issue/discussions/20260623t162536z-research-high-level-source-dependency-projection-root-cause.md`.
- Runtime source of truth remains provider-side code under `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/...`.
- This discussion draft is not a source of record until the main orchestrator adopts it into canonical docs.

## 8. Data Flow / Domain Model / Interface Contract
Current flow:
- `.meta.json.depends_on` is loaded by `deps_reader`.
- `load_issue_depends_on_map()` resolves raw node dependencies and compiles them into issue-source maps plus issue-keyed dependency contexts.
- Empty high-level sources cannot produce issue-keyed contexts, so readiness evaluation sees no dependency.
- Sync presentation consumes issue readiness evaluations and omits high-level raw `depends_on` from `index-all`.

Proposed flow:
- `deps_reader` continues returning `raw_node_depends_on_map` and/or raw direct edge resolutions.
- Domain builds two views:
  - `issue_depends_on_map` and `dependency_contexts_by_issue_id` for issue readiness.
  - `raw_direct_edges` and `direct_node_dependency_statuses_by_source_id` for raw audit and direct high-level source readiness.
- `deps check --id init-00001 --json` for `init-00001 -> epic-00002` unresolved open target should return a result equivalent to:

```json
{
  "target": "init-00001",
  "ready": false,
  "effective_depends_on": [],
  "blockers": ["epic-00002"],
  "direct_node_dependencies": [
    {
      "source_node_id": "init-00001",
      "source_node_kind": "initiative",
      "target_node_id": "epic-00002",
      "target_node_kind": "epic",
      "target_issue_ids": [],
      "expansion": "empty",
      "lifecycle_state": "open",
      "lifecycle_source": "local",
      "dependency_disposition": "blocking",
      "disposition_basis": "empty_open_container"
    }
  ]
}
```

- `.agent/index-all.json` should include complete raw edge audit data equivalent to:

```json
{
  "deps": {
    "valid": true,
    "error": null,
    "issue_edges": [],
    "raw_direct_edges": [
      {
        "from": "init-00001",
        "from_kind": "initiative",
        "to": "epic-00002",
        "to_kind": "epic",
        "relation": "raw_direct"
      }
    ],
    "edge_direction": "depends_on (dependent -> prerequisite)"
  }
}
```

What stays out:
- `deps-issues.json` should not include complete raw direct edges for high-level sources unless those edges participate in issue readiness contexts.
- `deps-raw.puml` should not be promoted to complete audit for this issue. It may continue to show active visual raw dependencies and omit satisfied/done edges.

## 9. File / Module Change Plan
- `domain.models`: add explicit raw direct edge and direct node dependency status models, or equivalent typed structures.
- `domain.deps`: add disposition evaluation for direct node dependencies using existing high-level lifecycle/status rules; keep issue readiness evaluation paths stable.
- `infra.contracts` and `infra.deps_reader`: expose enough raw edge information for source/target kind-aware audit, without changing `.meta.json`.
- `application.check_deps`: combine target issue readiness inspection with direct node source inspection for high-level target ids.
- `application.sync_state`: carry complete raw direct edge data to presentation, preferably derived once from `raw_node_depends_on_map` plus `graph`.
- `presentation.json_state`: add `direct_node_dependencies` to `deps check` JSON and `deps.raw_direct_edges` to `index-all`.
- Tests should be contract tests around the new behavior rather than broad rewrites of dependency internals.

## 10. Migration / Compatibility / Rollback
- Migration is additive. Existing `.meta.json.depends_on` files remain valid.
- Existing `deps check` consumers that only read `ready`, `blockers`, or `effective_depends_on` keep working. They additionally see `ready: false` and blockers for unresolved high-level source direct deps.
- Existing `index-all` consumers should tolerate unknown fields under `deps`; if any consumer rejects unknown fields, this change needs a schema-version note or consumer update.
- Rollback can remove the additive JSON fields and direct node readiness path without data migration because raw storage is unchanged.
- `deps-issues.json` and `deps-raw.puml` contracts remain stable, reducing rollback surface.

## 11. Observability
- `deps check --json` becomes the primary user-facing readiness observation for high-level source direct dependencies.
- `.agent/index-all.json` becomes the machine-readable complete raw audit observation.
- Existing `warnings` should not be used to compensate for missing contract data. A warning such as `deps_ref_expanded_to_empty` may remain useful for target expansion, but raw edge visibility and non-ready status must be represented structurally.
- If a direct dependency target has unknown lifecycle state, the structural status should be `dependency_disposition: "indeterminate"` with top-level `ready: false`.

## 12. Test Strategy
- Application contract: `deps check --id <initiative>` with empty source and unresolved high-level target returns `ready: false`, `blockers` containing the target node, and `direct_node_dependencies` containing source/target ids and kinds.
- Application contract: non-empty high-level source retains separate direct node dependency status while descendant issue readiness still uses `effective_depends_on`.
- Presentation contract: `render_deps_check_json()` includes the new additive direct node dependency payload and keeps `effective_depends_on` issue-only.
- Sync/index contract: `.agent/index-all.json` includes `deps.raw_direct_edges` for all raw direct edges, including high-level source edges and satisfied/done/closed dependencies.
- Regression contract: existing issue-source to high-level-target tests continue to pass, including empty high-level target blockers and satisfied high-level target contexts.
- Negative contract: `deps-issues.json` does not become a complete raw graph dump, and `deps-raw.puml` tests that omit satisfied/done edges remain valid.
- All regression cases should use `--no-github` or stubbed gateways so the issue remains reproducible without live GitHub state.

## 13. ADR Candidates
- Candidate: "Separate complete raw dependency audit from issue readiness projection."
- ADR is useful if the team wants a long-lived rule that raw storage/audit and readiness projection must stay separate across future dependency features.
- ADR can be deferred if the canonical design clearly records this boundary and tests enforce it.

## 14. Risks
- Adding `blockers` entries for high-level target ids may surprise consumers that assumed blockers were issue ids only. The risk is acceptable because the existing `node_blockers` path already introduced node-level blockers; document the contract clearly.
- A new `direct_node_dependencies` field can drift from issue readiness evaluation unless disposition rules are centralized in domain code.
- `index-all` unknown-field tolerance is assumed but should be verified by focused tests or downstream review.
- Non-empty high-level source dependencies can appear in both direct node status and descendant issue readiness; presentation must label them separately to avoid double-counting.

## 15. Requirement Clarification Requests
- None blocking. The approved requirement already decides the key boundary: raw dependency audit and issue readiness projection must remain separate.
- Non-blocking clarification for main orchestrator: whether `deps check` should also expose `guard_reason` in JSON as an additive field. This draft does not require it because `ready: false`, `blockers`, and `direct_node_dependencies.dependency_disposition` are sufficient for AC-002.

## 16. Integration Notes for Main Orchestrator
- Recommended adoption target is `design.md`, with `plan.md` only receiving implementation ordering after reviewer acceptance.
- Keep the discarded approach out: do not repair the bug by inventing source issues or pushing high-level source edges through `source_issue_id`.
- The core recommendation is:
  - use `direct_node_dependencies` in `deps check` for high-level source direct dependency readiness;
  - use `deps.raw_direct_edges` in `.agent/index-all.json` for complete raw audit;
  - keep `deps-issues.json` and `deps-raw.puml` scoped to their existing projections for this issue.
- Leaf evidence used: active issue requirement, root-cause research discussion, runtime/domain/presentation source inspection, and existing unit/CLI regression tests.
- Forbidden actions avoided: no canonical edits, no source/test edits, no report update, no phase promotion, no reviewer-pass claim, no user-dialogue ownership.

No canonical edit, final authority, promotion, reviewer-pass, or user-dialogue ownership is claimed.
