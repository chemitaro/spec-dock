# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a544481-51b0-83ee-9a85-22e2f2b2b1d2

## Prompt

Required repository connector context:
- @GitHub chemitaro/spec-dock
- Current branch: iss-00313-remove-pr-merge-preparer-repair-attempt-limits
- Default branch: main
- MUST inspect this GitHub repository with the GitHub connector before answering.
- First inspect the current branch. If the current branch does not exist or cannot be opened, inspect the default branch instead.
- Hard failure condition: if the GitHub connector/app is unavailable, or if the repository, current branch, and default branch cannot be accessed, return immediately with exactly: repository access failed.
- Do not continue from attached files, prompt context, memory, or general knowledge when repository access fails.
- Attached files and prompt-provided context are supplementary only after repository access succeeds.

Use the attached SpecDock prompt pack as the evidence-only task brief. Produce a complete Japanese-first Issue requirement, design, and executable strict-profile plan candidate for iss-00313. Treat the input as context-heavy. First determine whether the adopted scope remains one coherent Issue inside epic-00158; return information_insufficient or recommend Epic repair only if repository evidence proves the Issue boundary is unsafe. Preserve all forbidden-authority constraints.

### File: ../../../../../../../../../private/tmp/codex-agent-work/501/session-20260713t014845z-issue-313-chatgpt56-planning-dcdef228/prompt-pack/chatgpt-use-prompt.md
Lines: 1-34
```md
 1 | # ChatGPT Use Prompt Pack
 2 | 
 3 | Use the attached repository context and this prompt pack to produce a ZIP or tree rooted at `specdock-authoring-pack/`.
 4 | Treat every generated file as evidence only. Do not claim canonical adoption, `.assurance.json` mutation, `authorized_profile` decision, reviewer pass, execution-ready, PR-ready, or PR delivery.
 5 | 
 6 | - mode: `issue`
 7 | - evidence_mode: `local-context`
 8 | - sync_state: `local_context`
 9 | - github_sync: `not_verified`
10 | - source_manifest_hash: `5a10d9f35e84419daf6e8bd37b2886a2bea7d4ee723693e7de1b59abe7af530d`
11 | - adoption_requires: `explicit_eal_disposition`
12 | - provided_context_paths: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/.meta.json, spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/requirement.md, spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/design.md, spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/plan.md, spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/report.md, spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/artifacts/20260713t005118z-research-pr-merge-preparer-repair-limit-clarification-baseline.md, spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/artifacts/20260713t005207z-interview-same-family-repair-recurrence-continuation-policy.md, spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/artifacts/20260713t005848z-user-proposal-chatgpt-assisted-integrated-pr-repair-batch.md, spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/artifacts/20260713t011949z-research-chatgpt-consultation-integrated-pr-repair-workflow.md, spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/artifacts/20260713t012046z-interview-mandatory-chatgpt-consultation-scope.md, spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/artifacts/20260713t012618z-chatgpt-raw-integrated-pr-repair-workflow-consultation.md, spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/artifacts/20260713t013418z-disc-adopted-integrated-pr-repair-workflow-synthesis.md, spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/requirement.md, spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/design.md, spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/plan.md, src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md, src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/agents/openai.yaml, src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md, src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md, src/spec_dock/assets/spec_dock/templates/discussions/pr-repair-batch.md, tests/cli_runtime/test_new.py, tests/cli_runtime/test_runtime_new_doc_s09.py, tests/cli_runtime/test_wrappers.py`
13 | - diff_summary: `Issue #313 adds clarification artifacts only. Planning target is a strict single-Issue workflow-contract change; no implementation files have been changed yet.`
14 | - unsynced_reason: `The active Issue branch and planning artifacts are local and not pushed; the operator explicitly requested ChatGPT 5.6 Pro planning from current local context.`
15 | - authority: `evidence_only`
16 | - adoption_status: `unreviewed`
17 | 
18 | ## Forbidden Authority Claims
19 | 
20 | - canonical adoption
21 | - `.assurance.json` mutation
22 | - `authorized_profile` decision
23 | - reviewer pass
24 | - execution-ready
25 | - PR-ready
26 | - PR delivery
27 | 
28 | ## Expected Output
29 | 
30 | - Return a ZIP when possible.
31 | - The ZIP root must be `specdock-authoring-pack/`.
32 | - Include all required metadata named in `safe-output-constraints.md`.
33 | - Keep adoption candidates explicit and unreviewed.
34 | - Do not include raw transcripts, secrets, credentials, host-local absolute paths, nested archives, binaries, executables, symlinks, or path traversal entries.
```

### File: ../../../../../../../../../private/tmp/codex-agent-work/501/session-20260713t014845z-issue-313-chatgpt56-planning-dcdef228/prompt-pack/expected-output-contract.md
Lines: 1-27
````md
 1 | # Expected Output Contract
 2 | 
 3 | ChatGPT output must use this root:
 4 | 
 5 | ```text
 6 | specdock-authoring-pack/
 7 |   manifest.json
 8 |   provenance.json
 9 |   source-manifest.json
10 |   stale-if.json
11 |   safe-output-constraints.md
12 |   adoption/adoption-map.json
13 |   adoption/eal-candidates.json
14 |   summaries/
15 |   candidates/
16 |   drafts/
17 |   selected-skeleton-fill/section-fills.json
18 | ```
19 | 
20 | Required metadata:
21 | - `manifest.json`
22 | - `provenance.json`
23 | - `source-manifest.json`
24 | - `stale-if.json`
25 | - `safe-output-constraints.md`
26 | - `adoption/adoption-map.json`
27 | - `adoption/eal-candidates.json`
````

### File: ../../../../../../../../../private/tmp/codex-agent-work/501/session-20260713t014845z-issue-313-chatgpt56-planning-dcdef228/prompt-pack/manifest.json
Lines: 1-27
```json
 1 | {
 2 |   "adoption_status": "unreviewed",
 3 |   "authority": "evidence_only",
 4 |   "bundle_generation_not_promotion": true,
 5 |   "expected_output_root": "specdock-authoring-pack/",
 6 |   "files": [
 7 |     "manifest.json",
 8 |     "provenance.json",
 9 |     "source-manifest.json",
10 |     "stale-if.json",
11 |     "safe-output-constraints.md",
12 |     "chatgpt-use-prompt.md",
13 |     "expected-output-contract.md"
14 |   ],
15 |   "generated_by": "spec-dock authoring pack prepare",
16 |   "mode": "issue",
17 |   "required_metadata": [
18 |     "manifest.json",
19 |     "provenance.json",
20 |     "source-manifest.json",
21 |     "stale-if.json",
22 |     "safe-output-constraints.md",
23 |     "adoption/adoption-map.json",
24 |     "adoption/eal-candidates.json"
25 |   ],
26 |   "schema_version": 1
27 | }
```

### File: ../../../../../../../../../private/tmp/codex-agent-work/501/session-20260713t014845z-issue-313-chatgpt56-planning-dcdef228/prompt-pack/provenance.json
Lines: 1-41
```json
 1 | {
 2 |   "adoption_requires": "explicit_eal_disposition",
 3 |   "adoption_status": "unreviewed",
 4 |   "authority": "evidence_only",
 5 |   "bundle_generation_not_promotion": true,
 6 |   "diff_summary": "Issue #313 adds clarification artifacts only. Planning target is a strict single-Issue workflow-contract change; no implementation files have been changed yet.",
 7 |   "effective_ref": null,
 8 |   "evidence_mode": "local-context",
 9 |   "github_sync": "not_verified",
10 |   "local_head": null,
11 |   "provided_context_paths": [
12 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/.meta.json",
13 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/requirement.md",
14 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/design.md",
15 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/plan.md",
16 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/report.md",
17 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/artifacts/20260713t005118z-research-pr-merge-preparer-repair-limit-clarification-baseline.md",
18 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/artifacts/20260713t005207z-interview-same-family-repair-recurrence-continuation-policy.md",
19 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/artifacts/20260713t005848z-user-proposal-chatgpt-assisted-integrated-pr-repair-batch.md",
20 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/artifacts/20260713t011949z-research-chatgpt-consultation-integrated-pr-repair-workflow.md",
21 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/artifacts/20260713t012046z-interview-mandatory-chatgpt-consultation-scope.md",
22 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/artifacts/20260713t012618z-chatgpt-raw-integrated-pr-repair-workflow-consultation.md",
23 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/artifacts/20260713t013418z-disc-adopted-integrated-pr-repair-workflow-synthesis.md",
24 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/requirement.md",
25 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/design.md",
26 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/plan.md",
27 |     "src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md",
28 |     "src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/agents/openai.yaml",
29 |     "src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md",
30 |     "src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md",
31 |     "src/spec_dock/assets/spec_dock/templates/discussions/pr-repair-batch.md",
32 |     "tests/cli_runtime/test_new.py",
33 |     "tests/cli_runtime/test_runtime_new_doc_s09.py",
34 |     "tests/cli_runtime/test_wrappers.py"
35 |   ],
36 |   "remote_head": null,
37 |   "requested_ref": null,
38 |   "source_manifest_hash": "5a10d9f35e84419daf6e8bd37b2886a2bea7d4ee723693e7de1b59abe7af530d",
39 |   "sync_state": "local_context",
40 |   "unsynced_reason": "The active Issue branch and planning artifacts are local and not pushed; the operator explicitly requested ChatGPT 5.6 Pro planning from current local context."
41 | }
```

### File: ../../../../../../../../../private/tmp/codex-agent-work/501/session-20260713t014845z-issue-313-chatgpt56-planning-dcdef228/prompt-pack/source-manifest.json
Lines: 1-53
```json
 1 | {
 2 |   "source_hashes": {
 3 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/design.md": "89587a3f91d079c9907d943334d4708dc924682887c32139f8e16e9ccc00cdba",
 4 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/.meta.json": "3cc776509b7deedc436e57b47b33d96142aa353e34c9183b3c1308772bb88bcd",
 5 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/artifacts/20260713t005118z-research-pr-merge-preparer-repair-limit-clarification-baseline.md": "92f91072ac5590827599d1cac5461bd064be8f77ed54296294eabd776debda70",
 6 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/artifacts/20260713t005207z-interview-same-family-repair-recurrence-continuation-policy.md": "2e6e41360e43cbcd8ae5287cdb79c9972a3dc7ca5dd1defdb6f507520b6daa19",
 7 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/artifacts/20260713t005848z-user-proposal-chatgpt-assisted-integrated-pr-repair-batch.md": "8caaf0bd97460ad9f2a1dce95e32bd2f28cc5e2a74924791643d0544fbdcaaad",
 8 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/artifacts/20260713t011949z-research-chatgpt-consultation-integrated-pr-repair-workflow.md": "b76ec8b23ed4e70d9fdbcba65708227a2c99c1f76d87bce5c9914fcc9878ec7b",
 9 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/artifacts/20260713t012046z-interview-mandatory-chatgpt-consultation-scope.md": "5457d9ddc8ec06ca19908cb03396f68cf97bfb842a5cc2e61a081bf01d1d0e03",
10 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/artifacts/20260713t012618z-chatgpt-raw-integrated-pr-repair-workflow-consultation.md": "4d696e0d0adda87a11c7f3c4998f51fb217cf3c368f440e6eefcebe9a833a057",
11 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/artifacts/20260713t013418z-disc-adopted-integrated-pr-repair-workflow-synthesis.md": "357d493d6b7d0dfc2d29f7e7f1e9f75de63eeaae254327d938b577f541f5a00e",
12 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/design.md": "bc602be3fd40d313a16f822c7f1639c29bf73aedbf5f9fb47272789ec774f2e3",
13 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/plan.md": "f9c0e7e937f1475fcf6de4249ca006c5696ee785aefa7a9e35830ec7278c8bc4",
14 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/report.md": "4f4ee8372e6d38aa9f67860c906ca16d46a6875f21a6b247f1c2f8359b83f557",
15 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/requirement.md": "1f5e8559f7ccfc0071bcc33589ecb93dbe2b2a96aecf95d54acb2409d203890e",
16 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/plan.md": "4ff424d97dae1e55aa24c5313572898f6f41ef2349d7528fa7b79286e5d9bb81",
17 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/requirement.md": "e660f4c8fb285247f7b8963640d8ffe013349bf75bbce18ee86c2d3a49694c7c",
18 |     "src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md": "7a630fcc1e44ba78220abc12c17cf0acbf797fd1f5e863c945fa41337c9d1f0a",
19 |     "src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/agents/openai.yaml": "098d65f17c2db28da883c2ef24da592ff7bdb386696d270488cdd0cf06fa4c67",
20 |     "src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md": "d324ad20b7dc22f0ac0c271d16f48e346706ed3b11d97b88c13adefcf7f98020",
21 |     "src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md": "26563debf685efc3f68eeca8e5ab24dae3ef626ce0ede80fe1144ea69f42b255",
22 |     "src/spec_dock/assets/spec_dock/templates/discussions/pr-repair-batch.md": "26563debf685efc3f68eeca8e5ab24dae3ef626ce0ede80fe1144ea69f42b255",
23 |     "tests/cli_runtime/test_new.py": "dc3fa88c73f47a01852ed3c277a14b8fa482f132db6dd3a7ba8067770f489a0d",
24 |     "tests/cli_runtime/test_runtime_new_doc_s09.py": "bf5db094911212ce71e822de2cf60e2f6785626a8e2185d82da448f01b5dc519",
25 |     "tests/cli_runtime/test_wrappers.py": "6d3788d7dd9c326ebbc451b44b64a81b8d6cfd0117ea0073d8954000f3eebf17"
26 |   },
27 |   "source_manifest_hash": "5a10d9f35e84419daf6e8bd37b2886a2bea7d4ee723693e7de1b59abe7af530d",
28 |   "source_paths": [
29 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/.meta.json",
30 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/requirement.md",
31 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/design.md",
32 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/plan.md",
33 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/report.md",
34 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/artifacts/20260713t005118z-research-pr-merge-preparer-repair-limit-clarification-baseline.md",
35 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/artifacts/20260713t005207z-interview-same-family-repair-recurrence-continuation-policy.md",
36 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/artifacts/20260713t005848z-user-proposal-chatgpt-assisted-integrated-pr-repair-batch.md",
37 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/artifacts/20260713t011949z-research-chatgpt-consultation-integrated-pr-repair-workflow.md",
38 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/artifacts/20260713t012046z-interview-mandatory-chatgpt-consultation-scope.md",
39 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/artifacts/20260713t012618z-chatgpt-raw-integrated-pr-repair-workflow-consultation.md",
40 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00313-remove-pr-merge-preparer-repair-attempt-limits/artifacts/20260713t013418z-disc-adopted-integrated-pr-repair-workflow-synthesis.md",
41 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/requirement.md",
42 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/design.md",
43 |     "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/plan.md",
44 |     "src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md",
45 |     "src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/agents/openai.yaml",
46 |     "src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md",
47 |     "src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md",
48 |     "src/spec_dock/assets/spec_dock/templates/discussions/pr-repair-batch.md",
49 |     "tests/cli_runtime/test_new.py",
50 |     "tests/cli_runtime/test_runtime_new_doc_s09.py",
51 |     "tests/cli_runtime/test_wrappers.py"
52 |   ]
53 | }
```

### File: ../../../../../../../../../private/tmp/codex-agent-work/501/session-20260713t014845z-issue-313-chatgpt56-planning-dcdef228/prompt-pack/stale-if.json
Lines: 1-7
```json
1 | {
2 |   "evidence_mode_changes": "local-context",
3 |   "github_sync_changes": "not_verified",
4 |   "local_head_changes": null,
5 |   "remote_head_changes": null,
6 |   "source_manifest_hash_changes": "5a10d9f35e84419daf6e8bd37b2886a2bea7d4ee723693e7de1b59abe7af530d"
7 | }
```

### File: ../../../../../../../../../private/tmp/codex-agent-work/501/session-20260713t014845z-issue-313-chatgpt56-planning-dcdef228/prompt-pack/safe-output-constraints.md
Lines: 1-37
```md
 1 | # Safe Output Constraints
 2 | 
 3 | - expected_zip_root: `specdock-authoring-pack/`
 4 | - authority: `evidence_only`
 5 | - adoption_status: `unreviewed`
 6 | - bundle_generation_not_promotion: `true`
 7 | 
 8 | ## Required Metadata
 9 | - `manifest.json`
10 | - `provenance.json`
11 | - `source-manifest.json`
12 | - `stale-if.json`
13 | - `safe-output-constraints.md`
14 | - `adoption/adoption-map.json`
15 | - `adoption/eal-candidates.json`
16 | 
17 | ## Forbidden Authority Claims
18 | - canonical adoption
19 | - .assurance.json mutation
20 | - authorized_profile decision
21 | - reviewer pass
22 | - execution-ready
23 | - PR-ready
24 | - PR delivery
25 | 
26 | ## Forbidden Payloads
27 | - raw transcript
28 | - secret
29 | - credential
30 | - private key
31 | - host-local absolute path
32 | - path traversal
33 | - hidden path
34 | - nested archive
35 | - binary
36 | - executable
37 | - symlink
```

## Answer

# 結論

**`iss-00313` は `epic-00158` 内の一つの coherent Issue として維持可能です。** `information_insufficient` でも Epic repair 推奨でもありません。

GitHub コネクタでは指定ブランチ `iss-00313-remove-pr-merge-preparer-repair-attempt-limits` を確認できなかったため、指示どおり `main` を検査しました。検査時の `main` HEAD は `081ba64823f66d4efb051fb88e2a160915efdfa0` で、GitHub Issue #313 は open でした。

Issue 境界が安全である理由は、変更を次の一つの workflow invariant に閉じられるためです。

> **blocking repair を、固定試行回数ではなく、最新 evidence、再分析、materially distinct な bounded strategy、明示的な hard gate によって継続または停止する。**

現行の repair-batch contract は、同じ `root_cause_family` の再出現と総試行回数上限を停止条件にしています。
今回の候補は、このうち**固定回数と再出現そのものを停止権限から外す**一方、scope expansion、権限・認証、外部／flaky 要因、曖昧な review intent、古い observation、未承認 trigger などの既存 hard gate は保持します。

親 Epic は、skill が operational workflow spine を所有すること、ChatGPT 等の出力は採用判断まで evidence に留めること、provider-side source を authority として dogfooding mirror を検証することを要求しています。今回の範囲はこれらに整合しています。

# 成果物

[specdock-authoring-pack-iss-00313.zip](sandbox:/mnt/data/specdock-authoring-pack-iss-00313.zip)

* ZIP ルート: `specdock-authoring-pack/`
* SHA-256: `695976a477cdf5b42a36d62511355f2af7825eecf1036464613a346239e47442`
* サイズ: 81,389 bytes
* Authority: `evidence_only`
* Adoption status: `unreviewed`
* Bundle file 数: 17

主要候補は次の場所にあります。

```text
specdock-authoring-pack/
├── manifest.json
├── provenance.json
├── source-manifest.json
├── stale-if.json
├── safe-output-constraints.md
├── adoption/
│   ├── adoption-map.json
│   └── eal-candidates.json
├── candidates/
│   ├── requirement.md
│   ├── design.md
│   └── plan.md
├── drafts/
│   ├── implementation-diff-outline.md
│   └── reviewer-checklist.md
├── selected-skeleton-fill/
│   └── section-fills.json
└── summaries/
    ├── executive-summary.md
    ├── scope-boundary-assessment.md
    ├── evidence-and-assumptions.md
    └── bundle-validation.md
```

# 候補仕様の中心契約

## Requirement 候補

`candidates/requirement.md` は、日本語優先で次を固定しています。

* 固定数値制限は repair continuation／stop authority にしない。
* iteration count は telemetry と audit evidence に限定する。
* 同じ `root_cause_family` の再出現は、自動停止ではなく mandatory re-analysis を開始する。
* blocking repair の前に、current integrated batch を用いた ChatGPT consultation を必須にする。
* consultation は、最新 head SHA、observation、CI failure、review findings、過去の strategy／result、scope／禁止事項を入力に含める。
* ChatGPT 出力は evidence に限定し、orchestrator が `use`、`partial-use`、`reject`、`defer`、`human-gate` を明示的に disposition する。
* continuation には、最新 observation、triage 完了、fresh consultation、materially distinct strategy、bounded scope、検証・rollback・re-observation path を必要とする。
* materially distinct strategy が存在しない場合や、同じ ineffective strategy の反復になる場合は human gate にする。
* P2／P3 だけの terminal observation で record-only mutation や追加 review trigger を行わない。
* merge、auto-merge、branch deletion、thread resolution、review dismissal、admin override 等は引き続き禁止する。

## Design 候補

`candidates/design.md` は責任境界を次のように分離しています。

```text
github-pr-observation
    └─ latest-head observation evidence の収集のみ
           ↓
github-pr-merge-preparer
    ├─ integrated batch の更新
    ├─ root-cause family の再分析
    ├─ ChatGPT consultation の実施・freshness 判定
    ├─ consultation disposition
    ├─ bounded repair strategy の選択
    └─ continue / human-gate 判定
           ↓
repair worker
    └─ 採用済み bounded strategy の実装・検証
           ↓
re-observation
```

変更対象候補は以下に限定しました。

```text
src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/
├── SKILL.md
├── agents/openai.yaml
└── templates/pr-repair-batch.md

src/spec_dock/assets/spec_dock/templates/
├── artifacts/pr-repair-batch.md
└── discussions/pr-repair-batch.md

tests/cli_runtime/
├── test_new.py
├── test_runtime_new_doc_s09.py
└── test_wrappers.py
```

`.agents/**` と `spec-dock/**` の類似ファイルは直接の設計正本ではなく、標準 update 後の parity／dogfooding 検証面として扱っています。リポジトリ規約も `src/spec_dock/` を provider-side source of truth、`spec-dock/` を consumer-side dogfooding workspace と定義しています。

次は対象外として明記しました。

* `github-pr-observation` JSON schema の変更
* GitHub API mutation の追加
* 自動 repair strategy classifier
* runtime／CLI contract の変更
* `.assurance.json` の変更
* 既存 batch の一括 migration
* merge authority の変更
* ChatGPT への adoption／approval authority 付与

## Strict-profile plan 候補

`candidates/plan.md` は strict template に合わせた command-queue 形式で、以下を含みます。

* `S01`: current contract characterization と fixed-limit regression の Red
* `S02`: skill／prompt の continuation policy と consultation boundary
* `S03`: 3 種の repair-batch template の parity
* `S04`: scaffold／runtime regression と既存 batch compatibility
* `S05`: provider → dogfooding update／parity／validate／sync
* `S90`: docs・template・skill impact resolution
* `S95`: strict review candidate gate
* `S99`: final quality candidate gate
* `CLOS-001` から `CLOS-016` の Spec-Locked Closure Index
* 各 implementation step の delegation contract
* 各 step の concrete test cards
* Red／Green／refactor guardrail
* report evidence destination
* amendment／stop conditions
* Final Exit Contract

リポジトリの Issue-plan 規則では、observable behavior 単位、Spec-Locked Closure Index、risk-calibrated test obligations、delegation contract を要求し、S90、S99、Final Exit Contract も必須としています。

# 権限境界

この pack は次を主張していません。

* canonical adoption
* `.assurance.json` mutation
* `authorized_profile` decision
* reviewer pass
* execution-ready
* PR-ready
* PR delivery

`strict` はリスクと変更面に基づく**候補上の推奨**であり、正式な profile authorization ではありません。PR #311 で導入された ChatGPT-first planning も、ChatGPT 生成物を evidence-only とし、canonical adoption と reviewer authority を SpecDock 側に残しています。

添付された `設計判断と提案.txt` は、例外 taxonomy／`FailureResult` 境界に関する別設計テーマであり、Issue #313 の PR-repair continuation contract と直接対応しないため、採用候補から除外しました。

# 検証状態

実施済み:

* ZIP root／entry path 検査
* path traversal、絶対パス、hidden entry、symlink、nested archive、binary／executable の不在確認
* 全 JSON の parse
* manifest の非自己参照 file hash／size 照合
* required metadata の存在確認
* forbidden-authority wording の検査
* source／candidate／closure／section-fill の内部整合検査
* 38 件の bundle-internal check: pass

未実施:

* repository checkout 上での `pytest`
* `ruff`／`mypy`
* `spec-dock update .`
* dogfooding mirror parity
* `spec-dock validate`／`sync`
* reviewer gate
* EAL disposition
* profile authorization
* canonical file への反映

したがって、ZIP は**検査可能な authoring evidence candidate**であり、後続の Codex ワークフローによる source hash 再確認、明示的 EAL disposition、正式な profile 判定、reviewer gate の対象です。

## Artifacts

- specdock-authoring-pack-iss-00313.zip: /Users/iwasawayuuta/.oracle/sessions/iss-00313-chatgpt56-issue-planning/artifacts/specdock-authoring-pack-iss-00313.zip sha256=695976a477cdf5b42a36d62511355f2af7825eecf1036464613a346239e47442 transfer=not-needed validation=ok
