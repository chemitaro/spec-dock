---
種別: 計画書（Epic）
ID: "epic-00295"
タイトル: "ChatGPT Authoring Pack Installed Runtime"
関連GitHub: ["#295"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
依存: ["requirement.md", "design.md"]
親: ["init-local-00003"]
---

# epic-00295 ChatGPT Authoring Pack Installed Runtime — 計画

## この計画で閉じる範囲

- Installed skill taxonomy、skill naming、mode / stop gate。
- Installed runtime command group と backend command contract。
- GitHub sync preflight と explicit `local-context` evidence mode。
- ZIP / tree artifact contract と safe review / staging。
- Candidate validation、Issue draft adoption validation、approval check。
- Fail-closed、deterministic validation、provider-side source of truth。
- No-per-Issue-PR relay policy と final quality gate / PR delivery Issue。

## Issue slicing policy

1. Provider-side source-of-truth migration と consumer installed runtime behavior を分ける。
2. CLI command group skeleton を先に作り、その後に preflight / pack / validate を接続する。
3. GitHub sync preflight は backend invocation より前に置く。
4. 同期できない事情がある場合の ChatGPT authoring は `local-context` evidence mode として明示的に分ける。
5. ZIP safety / authority claim validation は high-risk slice として独立させる。
6. Skill taxonomy / naming / installed skill list は runtime implementation と並行可能だが、final gate 前に統合確認する。
7. Issue draft adoption は runtime `authoring adopt` ではなく、`spec-dock-issue-planning draft-adoption` mode と validator contract で扱う。
8. Human approval before node creation は `approval check` と planning skill stop gate で扱い、initial runtime は node creation をしない。
9. Epic に属する中間 Issue ごとに PR を作成しない。
10. Issue を一つずつ start / planning / execution / finish でリレーし、次の Issue へ進む。
11. 最後には final quality gate / PR delivery Issue を必ず置き、Epic 単位の品質ゲート、修正、mergeable PR delivery をまとめて行う。
12. Final quality gate で installed repo simulation、dogfood scenario、docs consistency、deferred command absence、mergeable PR readiness を確認する。

## Suggested Issue sequence

### C01: authoring pack assets を provider-side installed layout へ昇格する

目的: dogfood helper として存在してきた authoring-pack assets を provider-side source of truth へ移し、consumer repository へ `spec-dock init/update` で配布できる配置へ整理する。

主な対象:

- src/spec_dock/assets/spec_dock/scripts/authoring-pack/*
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/*
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/*
- tests / fixtures referencing provider asset paths

Handoff package:

- scope / non-scope decision
- verification evidence
- finish evidence
- relay policy: no PR delivery; defer to Issue 12

Depends on: none.
### C02: runtime `authoring` command group skeleton を追加する

目的: installed runtime の primary entrypoint として `./spec-dock/scripts/spec-dock authoring ...` を追加し、help / dispatch / status output の土台を作る。

主な対象:

- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/authoring.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/* parser / registry
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/*

Handoff package:

- scope / non-scope decision
- verification evidence
- finish evidence
- relay policy: no PR delivery; defer to Issue 12

Depends on: 01-promote-authoring-pack-assets.
### C03: block-first GitHub sync preflight を実装する

目的: repo-aware ChatGPT invocation 前に local branch / GitHub connector-visible branch / HEAD / source hash が一致していることを fail-closed に確認する。

主な対象:

- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/github_sync_preflight.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/preflight_contract.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/source_manifest.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/authoring_pack/diagnostics.py

Handoff package:

- scope / non-scope decision
- verification evidence
- finish evidence
- relay policy: no PR delivery; defer to Issue 12

Depends on: 02-add-authoring-command-skeleton.
### C04: prompt pack prepare と safe output constraints を実装する

目的: preflight evidence から ChatGPT に渡す prompt pack を deterministic に生成し、禁止 claim と ZIP output contract を明示する。

主な対象:

- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/pack_prepare.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/source_manifest.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/zip_contract.py
- src/spec_dock/assets/spec_dock/scripts/authoring-pack/prepare_chatgpt_authoring_pack.py

Handoff package:

- scope / non-scope decision
- verification evidence
- finish evidence
- relay policy: no PR delivery; defer to Issue 12

Depends on: 03-implement-github-sync-preflight.
### C05: backend invocation adapter を実装する

目的: ChatGPT backend command を明示設定された場合だけ fail-closed に呼び出し、prompt pack と invocation summary を接続する。

主な対象:

- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/backend_invoke.py
- src/spec_dock/assets/spec_dock/scripts/authoring-pack/invoke_chatgpt_backend.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/authoring_pack/cli_json.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/authoring_pack/cli_text.py

Handoff package:

- scope / non-scope decision
- verification evidence
- finish evidence
- relay policy: no PR delivery; defer to Issue 12

Depends on: 04-prepare-prompt-pack-and-safe-output-constraints.
### C06: ZIP/tree review と staging を runtime command へ昇格する

目的: ChatGPT output ZIP/tree を canonical docs に触れずに安全検査し、staged evidence と EAL candidate を生成する runtime command として提供する。

主な対象:

- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/pack_review.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/pack_stage.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/zip_contract.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/authority_boundary.py
- src/spec_dock/assets/spec_dock/scripts/authoring-pack/review_chatgpt_authoring_pack.py
- src/spec_dock/assets/spec_dock/scripts/authoring-pack/stage_chatgpt_authoring_pack.py

Handoff package:

- scope / non-scope decision
- verification evidence
- finish evidence
- relay policy: no PR delivery; defer to Issue 12

Depends on: 04-prepare-prompt-pack-and-safe-output-constraints.
### C07: Initiative/Epic と Epic/Issue 候補 validators を実装する

目的: ChatGPT batch planning output を node creation 前の candidate-only evidence として検証し、重複・境界・権限 claim の誤りを検出する。

主な対象:

- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/candidate_validation.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/candidate_contract.py
- src/spec_dock/assets/spec_dock/scripts/authoring-pack/validate_issue_candidates.py
- src/spec_dock/assets/spec_dock/scripts/authoring-pack/validate_initiative_epic_candidates.py

Handoff package:

- scope / non-scope decision
- verification evidence
- finish evidence
- relay policy: no PR delivery; defer to Issue 12

Depends on: 06-promote-zip-review-and-staging.
### C08: Issue draft adoption と selected skeleton validation contracts を実装する

目的: Issue node 作成後に、ChatGPT draft pack を canonical Issue docs へ採否判断するための input integrity を検証する。

主な対象:

- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/candidate_validation.py
- src/spec_dock/assets/spec_dock/scripts/authoring-pack/validate_issue_draft_adoption.py
- src/spec_dock/assets/spec_dock/scripts/authoring-pack/validate_selected_skeleton_fill.py
- Issue-local artifacts/draft-requirement.md
- Issue-local artifacts/draft-design.md
- Issue-local artifacts/draft-plan.md

Handoff package:

- scope / non-scope decision
- verification evidence
- finish evidence
- relay policy: no PR delivery; defer to Issue 12

Depends on: 06-promote-zip-review-and-staging.
### C09: `spec-dock-chatgpt-authoring` skill を追加し既存 planning skills を更新する

目的: human-facing skill taxonomy、names、ordering、modes、stop gates を installed skill docs と managed skill list に反映する。

主な対象:

- src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md
- src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md
- src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md
- src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md
- src/spec_dock/cli.py or managed skill list equivalent

Handoff package:

- scope / non-scope decision
- verification evidence
- finish evidence
- relay policy: no PR delivery; defer to Issue 12

Depends on: 02-add-authoring-command-skeleton.
### C10: approval check と stop-gate evidence reports を実装する

目的: Epic/Issue node creation 前の explicit human approval を machine-checkable evidence として扱い、自動 node creation を初期 scope から除外する。

主な対象:

- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/approval_check.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/candidate_contract.py
- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/authoring_pack/diagnostics.py

Handoff package:

- scope / non-scope decision
- verification evidence
- finish evidence
- relay policy: no PR delivery; defer to Issue 12

Depends on: 07-validate-initiative-epic-and-epic-issue-candidates.
### C11: runtime docs / reference docs / workflow guidance を更新する

目的: installed runtime command、skill taxonomy、evidence modes、deferred command boundary、relay PR delivery policy を user-facing docs に反映する。

主な対象:

- src/spec_dock/assets/spec_dock/docs/workflow_chatgpt_authoring_pack.md
- src/spec_dock/assets/spec_dock/docs/reference_authoring_pack_backend.md
- src/spec_dock/assets/spec_dock/docs/authoring/chatgpt-pack.md
- src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md
- src/spec_dock/assets/spec_dock/docs/workflow_initiative.md
- src/spec_dock/assets/spec_dock/docs/workflow_epic.md
- src/spec_dock/assets/spec_dock/docs/workflow_issue.md

Handoff package:

- scope / non-scope decision
- verification evidence
- finish evidence
- relay policy: no PR delivery; defer to Issue 12

Depends on: 03-implement-github-sync-preflight, 07-validate-initiative-epic-and-epic-issue-candidates, 08-validate-issue-draft-adoption-and-selected-skeleton, 09-add-chatgpt-authoring-skill-and-update-planning-skills, 10-implement-approval-check-and-stop-gate-reports.
### C12: final quality gate と mergeable PR delivery を実施する

目的: Epic 00295 全体を installed runtime / installed skills として dogfood し、final quality gate、manual tests、reviewer / CI / PR review repair loop を通して一つの mergeable PR を作る。

主な対象:

- all Epic 00295 changed provider-side assets
- all installed skill/docs paths touched by C01-C11
- spec-dock/initiatives/.../epic-00295.../report.md
- PR body / final quality gate evidence

Handoff package:

- scope / non-scope decision
- verification evidence
- finish evidence
- relay policy: final Issue only PR delivery

Depends on: 01-promote-authoring-pack-assets, 02-add-authoring-command-skeleton, 03-implement-github-sync-preflight, 04-prepare-prompt-pack-and-safe-output-constraints, 05-implement-backend-invocation-adapter, 06-promote-zip-review-and-staging, 07-validate-initiative-epic-and-epic-issue-candidates, 08-validate-issue-draft-adoption-and-selected-skeleton, 09-add-chatgpt-authoring-skill-and-update-planning-skills, 10-implement-approval-check-and-stop-gate-reports, 11-update-runtime-docs-and-workflow-guidance.


## Dependency graph

```text
C01 -> C02 -> C03 -> C04 -> C05
C04 -> C06 -> C07 -> C10
C06 -> C08
C02 -> C09
C03 -> C11
C07 -> C11
C08 -> C11
C09 -> C11
C10 -> C11
C11 -> C12
all preceding Issues -> C12
```

## Quality gates

- G1 Provider Asset Gate: implementation source is under `src/spec_dock/assets/...`; dogfood workspace is not source of truth.
- G2 Runtime Surface Gate: `authoring` help and supported command list are installed.
- G3 GitHub Sync Gate: repo-aware invocation is impossible without preflight pass.
- G4 Local Context Gate: unsynced execution is explicit `local-context` evidence and requires EAL disposition before canonical adoption.
- G5 Backend Gate: backend unset fails closed; configured command is explicit.
- G6 ZIP Safety Gate: unsafe ZIPs are rejected before extraction.
- G7 Authority Gate: no ChatGPT output claims canonical adoption / reviewer pass / authorized profile / execution-ready / PR-ready.
- G8 Approval Gate: Epic/Issue node creation remains blocked without explicit human approval.
- G9 Draft Adoption Gate: Issue draft adoption is validated after node creation and before execution handoff.
- G10 Skill Install Gate: installed skills exist in managed skill list and preserve user-facing names.
- G11 Relay Completion Gate: all preceding Issues are finished with deferred PR delivery evidence and no per-Issue PR claim.
- G12 Final Quality Gate: tests、docs、installed asset simulation、dogfood scenario、fresh reviewer evidence pass.
- G13 PR Delivery Gate: final quality gate Issue creates a mergeable PR and repairs reviewer / CI / manual test findings.

## Deferred items

- `authoring adopt`
- `authoring create-issues-from-zip`
- `authoring mark-reviewer-pass`
- `authoring set-authorized-profile`
- `authoring issue-execution-ready`
- `authoring pr-ready`
- automatic GitHub Issue creation from ChatGPT candidates
- automatic `.assurance.json` mutation from ChatGPT recommendation
- automatic reviewer pass or PR readiness claim
- raw ZIP durable repository storage contract
- generic external AI provider registry beyond configurable backend command
- per-Issue PR delivery for intermediate Issues
- broad `--force` bypass for ChatGPT authoring preflight

## Relay policy

All non-final implementation Issues in this Epic are intermediate Issues. They finish with local verification evidence, no-per-Issue-PR rationale, and dependency coverage into the final quality gate Issue. `iss-00307` is mandatory and is the only Issue that performs Epic-wide final quality gate, manual tests, reviewer / CI / PR review repair loop, and mergeable PR delivery. Newly inserted implementation Issues, including `iss-00309`, must be linked before `iss-00307` rather than creating their own per-Issue PR delivery.

## Final quality gate checks

C12 must verify:

- `./spec-dock/scripts/spec-dock validate`
- `git diff --check`
- related unit / cli_runtime tests
- installed asset simulation with `spec-dock init/update`
- `./spec-dock/scripts/spec-dock authoring --help`
- backend unset fail-closed
- GitHub sync preflight positive / negative fixtures
- `local-context` evidence mode provenance and adoption limitation
- unsafe ZIP rejection
- forbidden authority claim rejection
- candidate validation without node creation
- Issue draft adoption validation without execution-ready self-claim
- approval check without node creation
- docs / skills / runtime command consistency
- deferred command absence or fail-closed behavior
- all intermediate Issues finished without per-Issue PR delivery
- mergeable pull request created from final quality gate / PR delivery Issue

## Open questions

- `authoring preflight github-sync` の default branch fallback flag 名。
- `spec-dock-chatgpt-authoring` の managed skill list insertion position。
- `ORACLE_CHATGPT_COMMAND` fallback の deprecation schedule。
- `authoring validate initiative-epic-candidates` の exact schema。
- `approval check` が読む approval evidence の保存場所と署名強度。
- `local-context` mode の exact flag 名。現時点候補は `--evidence-mode local-context`。
