---
種別: research
ID: "20260706t114128z-research"
タイトル: "ChatGPT Spec Authoring Automation Best Practices"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-07-06"
親: ["epic-00283"]
関連:
  - "20260706t103820z-disc"
  - "20260706t111806z-research"
authority: "synthesized"
created_by_role: "main-orchestrator"
oracle_provider: "chatgpt-use"
oracle_model: "gpt-5.5-pro"
oracle_thinking: "Pro Extended"
oracle_session_slug: "specdock-spec-authoring-automation"
inspected_repo: "chemitaro/spec-dock"
inspected_default_branch: "main"
local_head_sha: "918e624b8a97a4c67bd5ac1ac4ff552999b64bbb"
local_branch_state: "detached-head"
adoption_status: "unreviewed"
derived_from:
  - "/private/tmp/codex-agent-work/501/session-20260706t112634z-specdock-chatgpt-spec-authoring-automation-35da9863/spec-authoring-automation-brief.md"
  - "/private/tmp/codex-agent-work/501/session-20260706t112634z-specdock-chatgpt-spec-authoring-automation-35da9863/spec-authoring-automation-output.md"
reflected_to: []
---

# 20260706t114128z-research ChatGPT Spec Authoring Automation Best Practices

## 調査目的

reviewer gate 置換ではなく、GPT-5.5 Pro Extended を SpecDock の authoring automation backend として使う具体策を整理する。

対象は以下の 3 workflow。

1. Initiative requirement / strategic intent から Initiative design / plan を作り、複数 Epic へ slice する。
2. Epic requirement から Epic design / plan を作り、複数 Issue へ slice する。
3. Issue context から Issue requirement / design / plan を bundle draft として作る。

## sources / 調査方法

実行:

- `chatgpt-use` wrapper を直接実行。
- dry-run: `gpt-5.5-pro`, browser mode, prompt only 約 `182,965` tokens, 57 files bundled。
- live run: `12m06s`, `gpt-5.5-pro[browser]`, input 約 `182.97k`, output 約 `10.56k`, total 約 `193.53k` tokens。
- Model selection evidence: `requested=Pro; resolved=Pro Extended; status=already-selected; verified=yes`。
- 出力保存先: `/private/tmp/codex-agent-work/501/session-20260706t112634z-specdock-chatgpt-spec-authoring-automation-35da9863/spec-authoring-automation-output.md`

主な添付:

- `AGENTS.md`, `README.md`, `pyproject.toml`
- `chatgpt-use/SKILL.md`
- 先行 ChatGPT artifact:
  - `20260706t103820z-disc-chatgpt-spec-authoring-batch-workflow-redesign.md`
  - `20260706t111806z-research-chatgpt-reviewer-gate-script-analysis.md`
- `init-local-00003-architecture-maintenance-and-hardening` docs
- `epic-00158-agent-workflow-pdca-hardening` docs
- `iss-00159` / `iss-00210` requirement
- `.codex/agents/{spec-reviewer,system-architect,implementation-planner,consultant,deep-consultant}.toml`
- `spec-dock-{initiative,epic,issue}-planning` / execution skills
- workflow / phase / authoring / dependency / GitHub docs
- initiative / epic / issue templates

補足:

- ChatGPT 出力の末尾には「この回答自体は GPT-5.5 Pro Extended を実行していない」という自己言及があるが、wrapper 実行ログでは GPT-5.5 Pro Extended が確認済み。artifact では local execution evidence を優先する。
- local checkout は detached HEAD であるため、branch-sensitive な実行例としては扱わない。

## facts / 観測できた事実

- SpecDock の canonical docs は repository source of truth。delegated / external output は adoption まで evidence。
- 既存 workflow は requirement -> design -> plan の段階的 promotion と fresh `spec-reviewer` gate を要求する。
- Initiative / Epic / Issue planning skill は、draft / research / generated runbook を scope-local artifact evidence とし、canonical docs への直接書き込みを禁止している。
- 現行 CLI は node creation, artifact creation, validate, sync, deps mutation を runtime command として扱える。
- branch-sensitive な ChatGPT 実行には、GitHub repo/ref provenance と local clean/pushed preflight が必要。

## inference / 推測

- GPT-5.5 Pro Extended は、単一の reviewer gate 置換よりも、複数 artifact を横断して design / plan / decomposition / reviewer focus / adoption map を一括生成する authoring backend として先に使うべき。
- Issue は Epic handoff が十分具体的なら requirement/design/plan を bundle draft として生成できる。ただし canonical adoption は requirement -> design -> plan の順に staged で行うのが安全。
- 実装の最初は shipped runtime ではなく `manual-tests/oracle-spec-authoring/` の dogfood-only script 群でよい。

## ChatGPT GPT-5.5 Pro Extended analysis

### 結論

GPT-5.5 Pro Extended は reviewer gate replacement ではなく、`Oracle Spec Authoring Batch Engine` として evidence-only に導入する。対象は以下。

- Initiative -> Epic decomposition
- Epic -> Issue decomposition
- Issue requirement/design/plan bundle draft generation

生成物は canonical docs ではなく、まず `artifacts/` 配下の構造化 evidence とする。main orchestrator が claim 単位で採否を判断し、canonical `requirement.md` / `design.md` / `plan.md` / `report.md` に再記述する。

### 推奨 architecture

| Batch | 入力 | 出力 | canonical への反映 |
| --- | --- | --- | --- |
| `initiative-planning-batch` | Initiative requirement / strategic intent、既存 Initiative/Epic、関連 docs/source | Initiative design/plan draft、Epic candidate set、sequencing、dependency map、acceptance rationale | Initiative `design.md` / `plan.md` に main orchestrator が再記述し、Epic 作成は明示採択後 |
| `epic-planning-batch` | reviewer-pass 済み Epic requirement、親 Initiative docs、関連 source | Epic design/plan draft、Issue candidate set、cross-issue handoff package、dependency graph | Epic `design.md` / `plan.md` に再記述し、Issue 作成は reviewer-gated Epic plan 後 |
| `issue-planning-bundle` | Issue context、Epic handoff、Issue draft artifacts、grade/profile | Issue requirement/design/plan draft bundle、test expectations、reviewer focus、bundle/staged recommendation | Issue canonical docs へ段階採用。必要なら `draft-*` artifact として materialize |

最初の実装は shipped runtime command ではなく、dogfood-only の `manual-tests/oracle-spec-authoring/` script 群にする。その後、効果が測定できたら provider-side docs / optional adapter / runtime command へ昇格する。

### Layered workflow model

| Layer | 目的 | 主な成果物 | Authority |
| --- | --- | --- | --- |
| L0. Source / branch preflight | repo/ref/source_paths/秘密情報/clean branch を固定 | `preflight.json`, source manifest, `stale_if` | script evidence only |
| L1. Requirement lock / critique | requirement の不足・曖昧さを batch 前に検出 | `requirement_critique`, blocking questions | evidence only |
| L2. Authoring batch | design draft、plan draft、decomposition を一括生成 | batch JSON + markdown artifact | evidence only |
| L3. Candidate decision | Epic/Issue candidate を採択・分割・棄却 | accepted candidate list, creation commands | human/orchestrator decision |
| L4. Quarantine / schema validation | output の安全性・schema・source grounding を検査 | validation result, unsafe claim list | no canonical authority |
| L5. Canonical adoption | 採用 claim だけ canonical docs に再記述 | updated `design.md`, `plan.md`, `report.md` EAL | main orchestrator |
| L6. Fresh review gate | canonical artifact を reviewer が検査 | `spec-reviewer` JSON / gate record | downstream safety gate |
| L7. Handoff / execution | approved plan から downstream workflow へ渡す | handoff package, issue artifacts | workflow-owned |

### Initiative -> Epic workflow

1. 入力を固定する。
   - Initiative `requirement.md`
   - existing Initiative/Epic inventory
   - relevant ADR / artifacts / source files
   - success metrics / non-scope / strategic constraints
2. GPT-5.5 Pro Extended に一括生成させる。
   - requirement critique
   - Initiative design draft
   - Initiative plan draft
   - Epic candidate list
   - dependency / sequencing / parallelization map
   - adoption map
   - reviewer focus
3. human/orchestrator が Epic candidate を採択する。
4. 採択済み candidate だけ runtime command で Epic 化する。
5. Initiative canonical docs を再記述し、fresh `spec-reviewer` gate を通す。

### Epic -> Issue workflow

1. 入力を固定する。
   - reviewer-pass 済み Epic requirement
   - parent Initiative docs
   - existing sibling Epics / Issues
   - source paths
   - accepted ADRs / relevant artifacts
2. GPT batch で次を生成する。
   - Epic design draft
   - Epic plan draft
   - Issue candidates
   - Issue responsibility boundaries
   - dependency edges
   - cross-issue draft package
   - Issue-local draft materialization plan
3. main orchestrator が Epic canonical docs へ採用する。
4. fresh `spec-reviewer` gate 後、Issue 作成に進む。
5. 採択済み Issue candidate だけ runtime command で作成する。

### Issue requirement/design/plan bundle workflow

Epic handoff が十分に具体的な場合、Issue では requirement/design/plan の draft bundle を 1 回で生成してよい。ただし canonical adoption は staged にする。

```text
Issue context + Epic handoff
  -> oracle issue planning bundle
  -> schema / provenance / safety validation
  -> requirement 採用候補を canonical requirement.md へ再記述
  -> fresh spec-reviewer
  -> design 採用候補を canonical design.md へ再記述
  -> fresh spec-reviewer
  -> plan 採用候補を canonical plan.md へ再記述
  -> fresh spec-reviewer
  -> execution-ready 判定
```

## Recommended script commands

以下は提案コマンドであり、現行 runtime availability の主張ではない。dogfood-only では `manual-tests/oracle-spec-authoring/` 配下に置き、将来 shipped runtime 化する場合だけ `./spec-dock/scripts/spec-dock oracle ...` へ移す。

### `oracle-authoring-preflight`

目的: branch/ref/source/provenance/secret/reviewer state を fail-closed で固定する。

```bash
manual-tests/oracle-spec-authoring/oracle-authoring-preflight \
  --repo chemitaro/spec-dock \
  --requested-ref unavailable \
  --fallback-ref main \
  --scope initiative|epic|issue \
  --scope-id <init-id|epic-id|iss-id> \
  --mode default-ref|pushed-branch|pr \
  --source-paths-file manual-tests/oracle-spec-authoring/source-paths.txt \
  --require-clean-worktree true|false \
  --require-pushed-head true|false \
  --require-reviewer-pass requirement|design|none \
  --deny-path ".env*" \
  --deny-path "**/cookies*" \
  --deny-path "**/*token*" \
  --json-out /tmp/specdock-oracle/<scope-id>/preflight.json
```

Preflight checks:

| Check | `default-ref` mode | `pushed-branch` / `pr` mode |
| --- | --- | --- |
| GitHub connector repo access | required | required |
| default branch resolved | required | required |
| current branch resolved | optional | required |
| detached HEAD | allowed with `branch_sensitive=false` | hard fail |
| `git status --porcelain=v1` clean | recommended | required |
| local HEAD == upstream HEAD | not applicable | required |
| PR head SHA == local HEAD | not applicable | required in PR mode |
| source paths explicit | required | required |
| denylist / secret scan | required | required |
| previous phase reviewer pass | required when adopting | required |
| output path under `artifacts/` | required | required |

Failure behavior:

| Failure | Exit | Behavior |
| --- | ---: | --- |
| GitHub connector/repo unavailable | 10 | no ChatGPT run, no repo artifact |
| requested branch unavailable but fallback allowed | 0 with warning | inspect `main`, set `branch_sensitive=false`, add `stale_if` |
| detached/dirty/unpushed in branch-sensitive mode | 20 | no ChatGPT run |
| missing required reviewer pass | 30 | no ChatGPT run |
| source path outside allowlist | 40 | no ChatGPT run |
| denylisted/secret-like path | 50 | no ChatGPT run |
| artifact output path not under target `artifacts/` | 60 | hard fail |
| schema invalid after model run | 70 | save only blocked diagnostic outside canonical path |
| unsafe authority claim in output | 71 | mark adoption-ineligible; no canonical write |

### `oracle-initiative-planning-batch`

```bash
manual-tests/oracle-spec-authoring/oracle-initiative-planning-batch \
  --preflight-json /tmp/specdock-oracle/init-local-00002/preflight.json \
  --scope-id init-local-00002 \
  --requirement spec-dock/initiatives/init-local-00002-*/requirement.md \
  --include-existing-epics true \
  --source-paths-file manual-tests/oracle-spec-authoring/source-paths.txt \
  --oracle-provider chatgpt-use \
  --oracle-model gpt-5.5-pro \
  --thinking extended \
  --output-artifact spec-dock/initiatives/init-local-00002-*/artifacts/<ts>-disc-oracle-initiative-planning-batch.md \
  --json-out /tmp/specdock-oracle/init-local-00002/initiative-planning-batch.json \
  --mode evidence-only
```

Canonical write behavior: prohibited. The artifact starts with `adoption_status: unreviewed` and `reflected_to: []`.

### `oracle-epic-planning-batch`

```bash
manual-tests/oracle-spec-authoring/oracle-epic-planning-batch \
  --preflight-json /tmp/specdock-oracle/epic-00158/preflight.json \
  --scope-id epic-00158 \
  --parent-initiative init-local-00003 \
  --requirement spec-dock/initiatives/.../epics/epic-00158-*/requirement.md \
  --requirement-review-report spec-dock/initiatives/.../epics/epic-00158-*/report.md \
  --source-paths-file manual-tests/oracle-spec-authoring/source-paths.txt \
  --candidate-count-min 3 \
  --candidate-count-max 8 \
  --emit-issue-creation-plan true \
  --output-artifact spec-dock/initiatives/.../epics/epic-00158-*/artifacts/<ts>-disc-oracle-epic-planning-batch.md \
  --json-out /tmp/specdock-oracle/epic-00158/epic-planning-batch.json \
  --mode evidence-only
```

After human adoption and fresh Epic plan review, create accepted Issues using runtime commands:

```bash
./spec-dock/scripts/spec-dock new issue \
  --epic epic-00158 \
  --title "Ascii Issue Title"
```

Dependencies must be command-first:

```bash
./spec-dock/scripts/spec-dock deps add \
  --from iss-00234 \
  --to iss-00233
```

### `oracle-issue-planning-bundle`

```bash
manual-tests/oracle-spec-authoring/oracle-issue-planning-bundle \
  --preflight-json /tmp/specdock-oracle/iss-00234/preflight.json \
  --scope-id iss-00234 \
  --parent-epic epic-00158 \
  --profile lite|standard|strict|critical|auto \
  --bundle-policy auto|force-bundle|force-staged \
  --requirement-input spec-dock/.../issues/iss-00234-*/requirement.md \
  --epic-handoff-artifact spec-dock/.../epics/epic-00158-*/artifacts/<handoff>.md \
  --source-paths-file manual-tests/oracle-spec-authoring/source-paths.txt \
  --output-artifact spec-dock/.../issues/iss-00234-*/artifacts/<ts>-disc-oracle-issue-planning-bundle.md \
  --json-out /tmp/specdock-oracle/iss-00234/issue-planning-bundle.json \
  --materialize-draft-artifacts none|selected|all \
  --mode evidence-only
```

If `--materialize-draft-artifacts all` is selected:

```bash
./spec-dock/scripts/spec-dock new artifact draft-requirement --issue iss-00234 --title "Oracle Draft Requirement"
./spec-dock/scripts/spec-dock new artifact draft-design --issue iss-00234 --title "Oracle Draft Design"
./spec-dock/scripts/spec-dock new artifact draft-plan --issue iss-00234 --title "Oracle Draft Plan"
```

### `oracle-authoring-validate-output`

```bash
manual-tests/oracle-spec-authoring/oracle-authoring-validate-output \
  --kind initiative-planning-batch|epic-planning-batch|issue-planning-bundle \
  --json-in /tmp/specdock-oracle/<scope-id>/<batch>.json \
  --schema manual-tests/oracle-spec-authoring/schemas/<kind>.schema.json \
  --source-manifest /tmp/specdock-oracle/<scope-id>/preflight.json \
  --fail-on-unsafe-authority-claim true \
  --fail-on-unlisted-source true \
  --fail-on-missing-stale-if true \
  --report-out /tmp/specdock-oracle/<scope-id>/validation.json
```

### `oracle-authoring-render-artifact`

```bash
manual-tests/oracle-spec-authoring/oracle-authoring-render-artifact \
  --json-in /tmp/specdock-oracle/<scope-id>/<batch>.json \
  --validation-json /tmp/specdock-oracle/<scope-id>/validation.json \
  --artifact-out spec-dock/.../artifacts/<ts>-disc-oracle-<kind>.md \
  --frontmatter-adoption-status unreviewed \
  --frontmatter-reflected-to-empty true \
  --exclude-raw-transcript true
```

## Output schemas

### Common envelope

```json
{
  "schema_version": "oracle_spec_authoring_batch_v1",
  "kind": "initiative_planning_batch|epic_planning_batch|issue_planning_bundle",
  "authority": "evidence_only",
  "adoption_status": "unreviewed",
  "reflected_to": [],
  "oracle": {
    "provider": "chatgpt-use",
    "model": "gpt-5.5-pro",
    "thinking": "extended",
    "session_slug": "string",
    "repository_access": "confirmed|failed|unknown"
  },
  "target": {
    "repo": "chemitaro/spec-dock",
    "requested_ref": "unavailable|branch|pr|sha",
    "inspected_ref": "main|branch|sha",
    "head_sha": "string|null",
    "scope_type": "initiative|epic|issue",
    "scope_id": "string",
    "parent_scope_ids": ["string"]
  },
  "source_manifest": {
    "source_paths": ["path"],
    "source_hashes": [
      {"path": "path", "sha256": "string", "git_sha": "string|null"}
    ],
    "attached_files": [
      {"name": "string", "purpose": "brief|supplemental", "hash": "string"}
    ],
    "denylist_checked": true,
    "raw_transcript_excluded": true
  },
  "preflight": {
    "ok": true,
    "mode": "default-ref|pushed-branch|pr",
    "branch_sensitive": false,
    "clean_worktree_required": false,
    "pushed_head_required": false,
    "reviewer_pass_required": "requirement|design|none",
    "reviewer_pass_observed": true,
    "blocking_failures": []
  },
  "stale_if": [
    "inspected ref changes",
    "source path content changes",
    "requirement changes",
    "required reviewer target hash changes",
    "scope decision changes"
  ],
  "unsafe_claims": [],
  "self_review": {
    "findings": [],
    "limitations": [],
    "known_weak_evidence": []
  },
  "reviewer_focus": {
    "spec_reviewer": [],
    "code_reviewer": [],
    "qa_reviewer": []
  },
  "adoption_map": []
}
```

### Initiative planning batch

```json
{
  "schema_version": "oracle_spec_authoring_batch_v1",
  "kind": "initiative_planning_batch",
  "initiative": {
    "initiative_id": "init-local-00002",
    "strategic_intent_summary": "string",
    "requirement_critique": {
      "blocking_gaps": [],
      "non_blocking_gaps": [],
      "clarification_questions": [],
      "assumptions": []
    },
    "design_draft": {
      "operating_model": "string",
      "scope_boundaries": [],
      "decision_routing": [],
      "architecture_or_product_principles": [],
      "risks": [],
      "adr_candidates": []
    },
    "plan_draft": {
      "milestones": [],
      "epic_portfolio_strategy": [],
      "sequencing_rationale": [],
      "parallelization_policy": [],
      "success_metrics": [],
      "deferred_work": []
    },
    "epic_candidates": [
      {"$ref": "#/definitions/decomposition_candidate"}
    ]
  }
}
```

### Epic planning batch

```json
{
  "schema_version": "oracle_spec_authoring_batch_v1",
  "kind": "epic_planning_batch",
  "epic": {
    "epic_id": "epic-00158",
    "requirement_critique": {
      "blocking_gaps": [],
      "non_blocking_gaps": [],
      "clarification_questions": [],
      "assumptions": []
    },
    "design_draft": {
      "responsibility_model": [],
      "contract_boundaries": [],
      "data_or_artifact_flow": [],
      "migration_and_rollback": [],
      "failure_modes": [],
      "observability": [],
      "adr_candidates": []
    },
    "plan_draft": {
      "milestones": [],
      "issue_slicing_policy": [],
      "dependency_order": [],
      "test_strategy": [],
      "review_gates": [],
      "handoff_package": {
        "shared_vocabulary": [],
        "responsibility_boundaries": [],
        "dependency_edges": [],
        "draft_artifact_path_index_plan": [],
        "skip_or_fallback_policy": []
      }
    },
    "issue_candidates": [
      {"$ref": "#/definitions/decomposition_candidate"}
    ]
  }
}
```

### Issue planning bundle

```json
{
  "schema_version": "oracle_spec_authoring_batch_v1",
  "kind": "issue_planning_bundle",
  "issue": {
    "issue_id": "iss-00234",
    "parent_epic_id": "epic-00158",
    "profile_recommendation": {
      "recommended_profile": "lite|standard|strict|critical",
      "rationale": "string",
      "escalation_triggers": []
    },
    "bundle_policy_recommendation": {
      "mode": "bundle|staged",
      "rationale": "string",
      "staged_required_reasons": []
    },
    "requirement_draft": {
      "objective": "string",
      "background": [],
      "scope": [],
      "non_scope": [],
      "constraints": [],
      "acceptance_criteria": [],
      "edge_cases": [],
      "open_questions": []
    },
    "design_draft": {
      "design_summary": "string",
      "responsibility_boundary": [],
      "interfaces_or_artifact_contracts": [],
      "data_flow": [],
      "risks": [],
      "rollback": [],
      "test_surfaces": []
    },
    "plan_draft": {
      "milestones": [],
      "implementation_steps": [],
      "verification_commands": [],
      "test_expectations": [],
      "review_gates": [],
      "report_evidence_destinations": [],
      "completion_criteria": []
    },
    "draft_materialization": {
      "recommended": "none|selected|all",
      "commands": [
        "./spec-dock/scripts/spec-dock new artifact draft-requirement --issue iss-00234 --title \"...\""
      ]
    }
  }
}
```

### Decomposition candidate object

```json
{
  "candidate_id": "CAND-EPIC-001|CAND-ISSUE-001",
  "candidate_type": "epic|issue",
  "parent_id": "init-local-00002|epic-00158",
  "title_ascii": "Ascii Title Required By Runtime",
  "slug": "kebab-case-slug",
  "summary": "string",
  "rationale": "why this child exists",
  "boundary": {
    "owns": [],
    "does_not_own": [],
    "upstream_decisions_kept_at_parent": [],
    "downstream_decisions_allowed": []
  },
  "acceptance_criteria": [
    {
      "id": "AC-001",
      "actor": "string",
      "precondition": "string",
      "action": "string",
      "expected_result": "string",
      "observation_point": "path|command|review"
    }
  ],
  "dependencies": [
    {
      "depends_on_candidate_id": "CAND-ISSUE-000",
      "depends_on_existing_id": "iss-00000",
      "reason": "string",
      "dependency_command": "./spec-dock/scripts/spec-dock deps add --from iss-new --to iss-prereq"
    }
  ],
  "parallelization": {
    "parallel_group": "G1",
    "can_parallelize": true,
    "conflict_risks": []
  },
  "test_expectations": [],
  "review_expectations": {
    "spec_reviewer_focus": [],
    "code_reviewer_focus": [],
    "qa_reviewer_focus": []
  },
  "rollback_or_migration_risk": {
    "risk_level": "low|medium|high",
    "migration_required": false,
    "rollback_strategy": []
  },
  "creation": {
    "recommended": true,
    "creation_command": "./spec-dock/scripts/spec-dock new issue --epic epic-00158 --title \"Ascii Title\"",
    "draft_artifact_commands": []
  },
  "confidence": {
    "score": 0.0,
    "evidence_strength": "high|medium|low",
    "blocking_questions": []
  },
  "adoption_recommendation": "adopt|partial|reject|defer"
}
```

### Evidence Adoption Ledger entry

```json
{
  "id": "EAL-ORACLE-001",
  "adoption_status": "adopted|partially_adopted|rejected|deferred|stale|blocked",
  "source": "oracle_spec_authoring_batch",
  "source_role": "chatgpt-use:gpt-5.5-pro:extended",
  "source_artifact": "spec-dock/.../artifacts/<ts>-disc-oracle-epic-planning-batch.md",
  "source_claim_id": "CLAIM-001",
  "claim": "string",
  "target_artifact": "design.md|plan.md|report.md|child-node|artifact",
  "target_section": "string",
  "rationale": "why adopted/rejected",
  "evidence_strength": "high|medium|low",
  "source_paths": ["path"],
  "source_hashes": [{"path": "path", "sha256": "string"}],
  "adopter": "main-orchestrator",
  "reviewer": "spec-reviewer:<result-id>|pending|not_required_yet",
  "blocking": true,
  "next_action": "none|rewrite canonical docs|rerun reviewer|clarify|split candidate|reject output",
  "stale_if": []
}
```

## Canonical adoption procedure

1. Quarantine:
   - Store GPT output as scope-local artifact.
   - Frontmatter includes `adoption_status: unreviewed`, `reflected_to: []`, `authority: evidence_only`, model, repo/ref, source paths, stale conditions.
2. Validate:
   - JSON schema valid.
   - No canonical authority claim.
   - No reviewer pass claim.
   - No unlisted source path.
   - No denylisted file.
   - No raw transcript / secrets.
3. Map claims:
   - Convert each substantive design/plan/decomposition assertion into `adoption_map`.
   - Mark `adopt`, `partial`, `reject`, or `defer`.
4. Record EAL:
   - Add claim-level or grouped EAL entries to target scope `report.md`.
   - `blocked` / `stale` unresolved entries block downstream readiness.
5. Rewrite canonical docs:
   - Do not paste raw model output wholesale.
   - Main orchestrator rewrites adopted content into `requirement.md`, `design.md`, or `plan.md`.
6. Run fresh `spec-reviewer`:
   - Requirement after requirement adoption.
   - Design after design adoption.
   - Plan after plan adoption.
   - Self-review / reviewer focus from GPT is focus evidence, never gate result.
7. Create children only after parent canonical plan is reviewer-gated:
   - Epic creation after Initiative plan adoption and review.
   - Issue creation after Epic plan adoption and review.
   - Dependencies via `deps add`, not metadata edits.
8. Materialize issue drafts only when useful:
   - Use Issue-local `draft-requirement`, `draft-design`, `draft-plan` artifacts.

## Bundle vs staged Issue docs

| Condition | Bundle allowed | Staged required |
| --- | --- | --- |
| Scope clarity | Epic handoff has clear boundary, AC, dependencies | unresolved requirement/design gap |
| Grade/profile | Lite or Standard, low/medium risk | Strict/Critical or unknown risk |
| Architecture novelty | existing pattern reuse | new runtime/scaffold/API/persistence contract |
| Migration/rollback | no irreversible migration | migration, hard cutover, rollback complexity |
| Cross-issue coupling | dependencies already fixed | shared contract still unstable |
| User intent | no blocking user-intent question | scope/non-scope/priority unresolved |
| Test strategy | obvious verification surface | test adequacy unclear or QA-risk high |
| Adoption burden | claim map is small | output too broad to review safely |

Recommended default:

- Initiative: staged adoption. GPT can generate design+plan together, but canonical adoption remains staged.
- Epic: staged adoption for design/plan; child Issue candidates can be generated in same batch but not created until canonical Epic plan passes review.
- Issue: bundle generation is acceptable when the Issue is narrow and Epic handoff is concrete. Adoption still proceeds requirement -> design -> plan with fresh reviewer pass after each substantive canonical update.

## Best practices for child slicing

| Topic | Best practice | Anti-pattern |
| --- | --- | --- |
| Boundary sizing | Each child should close one externally reviewable capability, contract, or workflow slice. Prefer 3-8 children per parent batch before reassessing. | File-based slices, role-based slices, or misc cleanup buckets. |
| Parent/child authority | Parent owns cross-child decisions; child owns local implementation detail. | Passing unresolved parent decisions downstream as execution-ready work. |
| Dependency mapping | Generate explicit dependency edges with reason and command. Keep direct prerequisites only. | Implied ordering in prose or direct `.meta.json` edits. |
| Parallelization | Parallelize only when shared contracts are fixed and file/test conflict risk is low. | Parallel work that mutates the same runtime contract or migration boundary. |
| Acceptance criteria | AC must be actor/precondition/action/expected/observation-point. | Improve quality / make better without observable result. |
| Review/test gates | Candidate should include expected reviewer focus, but not claim pass. | GPT self-review laundered as reviewer gate. |
| Rollback/migration | Put migration risk at the parent if cross-child; child only gets local rollback. | Each child invents a different rollback story. |
| Draft handoff | For Epic -> Issue, include issue-local draft artifact commands or explicit skip evidence. | Pre-writing canonical Issue docs before Issue planning. |
| Decision-only work | Keep durable decisions at Initiative/Epic/ADR level. | Creating execution-ready Issues that only contain unresolved decisions. |

## Orchestrator cognitive load

Automate:

- Source manifest creation.
- Prompt pack construction.
- GitHub/ref/source-path provenance.
- Schema validation.
- Unsafe authority claim detection.
- Candidate table normalization.
- Adoption map generation.
- Reviewer focus list.
- Suggested runtime commands.
- `stale_if` generation.

Preserve human/orchestrator decisions:

- Whether the Initiative/Epic/Issue placement is correct.
- Whether child candidates are accepted, split, merged, or rejected.
- Whether Issue docs can be bundled or must be staged.
- Which claims are adopted into canonical docs.
- Whether a reviewer finding requires rewrite, clarification, ADR, or scope change.
- Whether unavailable GPT output falls back to manual authoring.

## First dogfood experiment

Recommended experiment:

**Dogfood Oracle Spec Authoring Batch For Epic Issue Decomposition**

Scope:

- dogfood-only
- no shipped runtime command yet
- location: `epic-00158 Agent Workflow PDCA Hardening` if framed as SpecDock workflow/governance hardening

Experiment arms:

| Arm | Method | Output |
| --- | --- | --- |
| Baseline | Existing staged authoring: `system-architect` draft -> adoption -> `implementation-planner` draft -> adoption | current workflow artifacts |
| Oracle batch | GPT-5.5 Pro Extended one-shot requirement critique + design draft + plan draft + child candidates | oracle batch artifact |
| Hybrid | Oracle batch first, then existing specialist roles use it as evidence | specialist artifacts + oracle evidence |

Minimum implementation:

```text
manual-tests/oracle-spec-authoring/
  oracle-authoring-preflight
  oracle-epic-planning-batch
  oracle-issue-planning-bundle
  oracle-authoring-validate-output
  oracle-authoring-render-artifact
  schemas/
    common-envelope.schema.json
    epic-planning-batch.schema.json
    issue-planning-bundle.schema.json
  README.md
```

Pass criteria:

- Artifact is created under target `artifacts/` with `adoption_status: unreviewed`.
- No canonical docs are written by script.
- Output schema validates.
- No reviewer pass / phase completion / implementation readiness self-claim.
- At least 60% of substantive claims are adoptable with minor rewrite.
- Fresh `spec-reviewer` passes adopted canonical design/plan in no more than one repair loop.
- Child Issue candidates require no major merge/split after review.
- Manual fallback remains available.

Fail criteria:

- Output claims canonical authority.
- Output relies on unlisted sources.
- Branch/ref provenance missing for branch-sensitive claims.
- Self-review is treated as `spec-reviewer` pass.
- Canonical docs are updated without EAL.
- First reviewer pass finds P0/P1 hallucination or scope creep caused by oracle adoption.

## Risks / anti-patterns / mitigations

| Risk / anti-pattern | Failure mode | Mitigation |
| --- | --- | --- |
| Reviewer laundering | GPT self-review becomes perceived gate | Name it `self_review` / `reviewer_focus`; never `review_status`. |
| Canonical copy-paste | Large generated prose becomes canonical without decision | Require claim-level EAL and orchestrator rewrite. |
| Stale branch | GPT reads `main` while task depends on unpushed branch | `pushed-branch` mode requires clean worktree and local HEAD == upstream. |
| Local diff invisibility | GitHub connector cannot see local uncommitted changes | Branch-sensitive mode hard fails on dirty/unpushed state. |
| Over-bundling | Issue docs look coherent but hide unresolved design gap | Bundle/staged decision gate; Strict/Critical staged by default. |
| Child scope hallucination | GPT invents children outside parent scope | Candidate must include parent trace, non-scope, adoption rationale. |
| Dependency hallucination | Edges based on assumed implementation order | Each edge needs reason and `deps add` command; reviewer checks. |
| Raw transcript leakage | Private reasoning/secrets enter artifact | Render summarized artifact only; exclude raw transcript. |
| Schema drift | GPT returns prose instead of contract | JSON schema validation; invalid output is adoption-ineligible. |
| Prompt injection from repo artifacts | Artifact text tries to change workflow | Treat repo artifacts as data; enforce outer schema and safety checks. |
| Availability dependency | ChatGPT/browser unavailable blocks normal work | Manual authoring fallback remains valid. |
| Cost/latency creep | Every small Issue gets Extended batch | Use grade/profile and bundle/staged policy; Lite skip allowed with reason. |

## Metrics

| Metric | Definition | Target signal |
| --- | --- | --- |
| Lead time | requirement locked -> plan reviewer pass | batch should reduce elapsed orchestration time |
| Tool/model calls | number of specialist/oracle/reviewer calls | batch should reduce authoring calls, not reviewer calls |
| Reviewer pass iterations | count of fresh `spec-reviewer` loops | equal or fewer than baseline |
| P0/P1 findings | severe findings caused by adopted output | zero tolerance for oracle-caused P0/P1 |
| Adoption ratio | adopted substantive claims / total substantive claims | target 60-80% in dogfood |
| Claim traceability | RQ/AC -> design decision -> plan step coverage | equal or better than baseline |
| Child churn | created child candidates later merged/split/rejected | lower is better |
| Dependency corrections | dependency edges changed after reviewer/execution | lower is better |
| Human edit burden | minor rewrite / major rewrite / reject | batch should shift toward minor rewrite |
| Schema validity rate | valid outputs / total runs | must be high before shipping |
| Provenance failure rate | stale/ref/source/secret failures | should trend down as scripts mature |
| Execution readiness defects | planning gaps found during execution | lower than baseline |
| QA missing-test findings | QA reviewer findings tied to weak plan | lower than baseline |
| Fallback success | manual path works when oracle unavailable | must remain 100% viable |

## question candidates / 質問候補

- source-grounded に解けず、人間判断が必要な候補:
  - 最初の dogfood を `epic-00158` の workflow hardening として扱うか、user-facing feature expansion として別 Epic/Issue 化するか。
  - machine-readable JSON sidecar を durable artifact として repo に保存するか、sanitized Markdown artifact のみ repo に残すか。
- 質問せずに解決できた候補:
  - reviewer gate replacement は今回の焦点から外す。
  - 初期実装は shipped runtime ではなく dogfood-only `manual-tests/oracle-spec-authoring/` に置く。
  - canonical docs への直接書き込みは禁止する。

## terminology conflicts / 用語衝突

- `batch`:
  - model call で design/plan/decomposition を一括生成する意味。
  - canonical docs を一括 promotion する意味ではない。
- `Issue planning bundle`:
  - Issue requirement/design/plan draft を一括生成する意味。
  - canonical Issue docs を review なしで完了させる意味ではない。
- `reviewer focus`:
  - reviewer に見てほしい観点。
  - reviewer pass ではない。

## edge cases / 具体シナリオ

- detached HEAD:
  - 今回の checkout の状態。default-ref analysis は可能だが、branch-sensitive adoption は不可。
- Epic handoff が曖昧:
  - Issue bundle generation は staged required。requirement clarification に戻す。
- Issue が Strict/Critical:
  - bundle draft は生成可能でも、canonical adoption は staged とし、stronger specialist evidence を要求する。
- GPT が child candidates を 12 個以上出す:
  - parent decomposition が荒い可能性が高い。3-8 children を目安に regroup を要求する。
- GPT が `deps add` ではなく `.meta.json` 編集を提案する:
  - adoption-ineligible。command-first dependency mutation に修正する。

## implications / 判断への含意

- 次に作るべき Issue は `Dogfood Oracle Spec Authoring Batch For Epic Issue Decomposition`。
- 初期範囲は `oracle-authoring-preflight`、`oracle-epic-planning-batch`、`oracle-issue-planning-bundle`、schema validation、artifact rendering。
- `initiative-planning-batch` は 2nd step でよい。まず Epic -> Issue decomposition が最も頻度・効果・検証容易性のバランスが良い。
- Issue-level bundle は default-on ではなく `bundle_policy=auto` とし、Strict/Critical や architecture novelty がある場合は staged に戻す。

## リスク/制約

- Browser / manual-login / local wrapper 依存があるため、初期 shipped runtime 化は避ける。
- GitHub connector の branch visibility と local worktree state がずれるため、branch-sensitive mode では pushed/clean preflight が必須。
- GPT output が良質でも canonical authority は持たない。

## 反映先

- まだ canonical docs へ反映していない。
- 反映する場合の候補:
  - `epic-00158` 配下に dogfood Issue を追加。
  - Issue title candidate: `Dogfood Oracle Spec Authoring Batch For Epic Issue Decomposition`
  - Follow-up Issue candidate: `Add Oracle Authoring Output Schemas And Validation Runbook`
  - Later Issue candidate: `Promote Oracle Authoring Batch From Manual Tests To Optional Adapter`
