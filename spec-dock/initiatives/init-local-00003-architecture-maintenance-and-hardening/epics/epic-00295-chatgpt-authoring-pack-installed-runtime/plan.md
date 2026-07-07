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

## この計画で閉じる E-RQ / E-AC

- E-RQ-ST: installed skill taxonomy、skill naming、mode / stop gate。
- E-RQ-RT: installed runtime command group と backend command contract。
- E-RQ-GH: GitHub sync preflight。
- E-RQ-ZIP: ZIP / tree artifact contract。
- E-RQ-NF: fail-closed、deterministic validation、provider-side source of truth。
- E-AC-001〜E-AC-022: installed skill / runtime / preflight / local-context mode / ZIP / candidate validation / dogfood / relay delivery / final quality gate。

## Issue slicing policy

1. Provider-side source-of-truth migration と consumer installed runtime behavior を分ける。
2. CLI command group skeleton を先に作り、その後に preflight / pack / validate を接続する。
3. GitHub sync preflight は backend invocation より前に置く。
4. 同期できない事情がある場合の ChatGPT authoring は `local-context` evidence mode として明示的に分ける。
5. ZIP safety / authority claim validation は high-risk slice として独立させる。
6. Skill taxonomy / naming / installed skill list は runtime implementation と並行可能だが、final gate 前に統合確認する。
7. Issue draft adoption は runtime `authoring adopt` ではなく、`spec-dock-issue-planning draft-adoption` mode と validator contract で扱う。
8. Human approval before node creation は `approval check` と planning skill stop gate で扱い、initial runtime は node creation をしない。
9. Epic に属する中間 Issue ごとに PR を作成しない。Issue を一つずつ start / planning / execution / finish し、次の Issue へリレーする。
10. Issue list の最後には final quality gate / PR delivery Issue を必ず置き、Epic 単位の品質ゲート、修正、mergeable PR delivery をまとめて行う。
11. Final quality gate で installed repo simulation、dogfood scenario、docs consistency、deferred command absence、mergeable PR readiness をまとめて確認する。

## Suggested Issue sequence

### C01: Promote authoring pack assets into provider-side installed layout

目的:

- dogfood helper を provider-side source of truth へ移し、consumer repo に配布できる layout を作る。

主な対象:

- `src/spec_dock/assets/spec_dock/scripts/authoring-pack/*`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/*`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/*`
- fixtures / manual tests の provider-side 参照整理

Handoff package:

- migrated file inventory
- dogfood helper compatibility note
- source-of-truth boundary note
- no canonical mutation evidence
- existing authoring pack helper tests adapted to provider asset path

Depends on: none.

### C02: Add runtime `authoring` command group skeleton

目的:

- existing runtime parser / registry pattern に `authoring` group を追加し、help / dispatch / status output の土台を作る。

主な対象:

- `commands/authoring.py`
- parser subcommand registration
- command registry registration
- `CommandOutcome` presenter

Commands introduced as stubs or thin use-case calls:

- `authoring preflight github-sync`
- `authoring pack prepare`
- `authoring backend invoke`
- `authoring pack review`
- `authoring pack stage`
- `authoring validate ...`
- `authoring approval check`

Handoff package:

- help output snapshot
- unsupported/deferred command list
- no mutation guarantee
- parser / dispatch tests

Depends on: C01.

### C03: Implement block-first GitHub sync preflight

目的:

- repo-aware ChatGPT invocation 前に local branch と GitHub connector-visible state の同期を保証する。

主な対象:

- git observation
- origin normalization
- branch / HEAD comparison
- dirty/staged/untracked detection
- ahead/behind/diverged detection
- default branch fallback contract
- source hash manifest

Handoff package:

- preflight JSON schema
- positive fixture
- dirty/staged/untracked/behind/diverged/missing branch/origin mismatch negative fixtures
- default fallback evidence with requested/effective ref
- `github-synced` / `local-context` evidence mode taxonomy
- `local-context` provenance sample with unsynced reason and provided context paths
- docs for block conditions

Depends on: C02.

Gate:

- backend invocation cannot start without C03 pass.
- `local-context` invocation cannot pretend to be `github-synced` evidence.

### C04: Implement prompt pack prepare and safe output constraints

目的:

- GitHub sync preflight pass から ChatGPT prompt pack を deterministic に生成する。

主な対象:

- `authoring pack prepare`
- source manifest
- stale-if
- safe-output-constraints
- forbidden authority claims
- ZIP root / schema instructions
- use-case mode selection: initiative-epic, epic-issue, issue-draft-adoption, selected-skeleton-fill

Handoff package:

- prompt pack tree sample
- `manifest.json` / `source-manifest.json` / `stale-if.json` examples
- safe-output-constraints sample
- local-context prompt pack sample with diff / file bundle manifest
- no raw transcript / secret policy evidence

Depends on: C03.

### C05: Implement backend invocation adapter

目的:

- ChatGPT backend command を configurable / fail-closed に呼び出す。

主な対象:

- `authoring backend invoke`
- `--backend-command`
- `SPECDOCK_CHATGPT_COMMAND`
- optional `ORACLE_CHATGPT_COMMAND`
- `shlex.split` argv interpretation
- dry-run support
- invocation summary
- stdout/stderr redaction policy

Handoff package:

- unset backend negative test
- env var resolution test
- CLI override test
- dry-run output
- explicit `--evidence-mode local-context` invocation summary
- rejection test for broad `--force` bypass behavior
- no personal absolute path in canonical docs

Depends on: C04.

Gate:

- no backend inference if unset.

### C06: Promote ZIP/tree review and staging into runtime commands

目的:

- dogfood review/stage helpers を installed runtime command として利用可能にする。

主な対象:

- `authoring pack review`
- `authoring pack stage`
- central directory inspection
- safe extraction
- mandatory metadata
- forbidden authority claim scanner
- staged evidence output
- EAL candidate rendering
- ownership marker and cleanup safety

Handoff package:

- valid ZIP fixture
- unsafe ZIP fixtures
- tree fallback fixture
- staging report
- EAL candidate sample
- canonical docs unchanged evidence

Depends on: C04.

### C07: Implement candidate validators for Initiative/Epic and Epic/Issue slicing

目的:

- ChatGPT batch planning output を node creation 前の candidate-only evidence として検証する。

主な対象:

- `authoring validate initiative-epic-candidates`
- `authoring validate epic-issue-candidates`
- parent trace
- scope/non-scope
- dependencies
- duplicate / overlap diagnostics
- per-candidate draft requirement/design/plan
- advisory-only profile recommendation
- no `authorized_profile` claim

Handoff package:

- Initiative -> Epic candidate fixture
- Epic -> Issue candidate fixture
- duplicate/overlap negative fixture
- profile authority negative fixture
- candidate comparison summary

Depends on: C06.

Gate:

- human approval before node creation remains outside validator.

### C08: Implement Issue draft adoption and selected skeleton validation contracts

目的:

- Issue node 作成後の draft adoption / canonicalization input を検証可能にする。

主な対象:

- `authoring validate issue-draft-adoption`
- `authoring validate selected-skeleton-fill`
- `.assurance.json` snapshot observation-only
- selected profile / template hash / section inventory
- draft-to-canonical target mapping
- missing / extra section diagnostics
- no execution-ready claim

Handoff package:

- issue draft adoption fixture
- selected skeleton fill fixture
- `.assurance.json` mutation negative fixture
- stale template hash negative fixture
- handoff note for `spec-dock-issue-planning draft-adoption`

Depends on: C06.

### C09: Add `spec-dock-chatgpt-authoring` installed skill and update planning skills

目的:

- human-facing taxonomy、names、ordering、modes、stop gates を installed skill docs に反映する。

主な対象:

- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md`
- `spec-dock-initiative-planning/SKILL.md`
- `spec-dock-epic-planning/SKILL.md`
- `spec-dock-issue-planning/SKILL.md`
- installer managed skill list update
- host-adapter metadata if required

Handoff package:

- skill inventory diff
- user-facing name table
- stop gate matrix
- installed skill presence test
- update/init install simulation

Depends on: C02.

### C10: Implement approval check and stop-gate evidence reports

目的:

- node creation 前の explicit human approval を machine-checkable evidence として扱う。

主な対象:

- `authoring approval check`
- approval evidence schema
- requested scope and effective scope
- candidate pack digest
- approver / timestamp / statement
- unsupported auto-creation diagnostics

Handoff package:

- approval pass fixture
- missing approval blocked fixture
- stale candidate digest fixture
- report wording for Issue Decomposition Approval Gate

Depends on: C07.

Gate:

- no Issue / Epic node creation command is introduced.

### C11: Update runtime docs, reference docs, and workflow guidance

目的:

- installed runtime command と skill taxonomy を user-facing docs に反映し、deferred command を誤って利用可能に見せない。

主な対象:

- `src/spec_dock/assets/spec_dock/docs/workflow_chatgpt_authoring_pack.md`
- `src/spec_dock/assets/spec_dock/docs/reference_authoring_pack_backend.md`
- `src/spec_dock/assets/spec_dock/docs/authoring/chatgpt-pack.md`
- `workflow_spec_authoring.md`
- `workflow_initiative.md`
- `workflow_epic.md`
- `workflow_issue.md`
- status taxonomy docs
- failure mode docs
- manual fallback docs

Handoff package:

- docs trace matrix
- command examples
- deferred command warning
- migration note from dogfood helper to installed runtime
- `git diff --check`

Depends on: C03, C07, C08, C09, C10.

### C12: Final quality gate and mergeable PR delivery

目的:

- Epic 00295 の installed runtime と installed skills を dogfood し、Epic 単位の final quality gate を通した上で、mergeable pull request を作成する。

主な対象:

- all preceding Issues completion evidence
- installed repo simulation
- `spec-dock init/update` asset verification
- `authoring preflight github-sync`
- `authoring preflight github-sync --evidence-mode local-context` or equivalent local-context fixture
- `authoring pack prepare`
- `authoring backend invoke --dry-run`
- `authoring pack review`
- `authoring pack stage`
- candidate validation
- approval check
- deferred command absence
- final docs consistency
- manual test summary
- full test / lint / validation evidence
- reviewer / CI / PR review repair loop
- mergeable PR creation

Handoff package:

- command transcript summary
- test output
- manual scenario matrix
- fresh `spec-reviewer` evidence for canonical docs
- final Evidence Adoption Ledger
- final open risk / deferred list
- PR URL
- PR readiness / mergeability evidence
- review finding repair evidence

Depends on: all prior Issues.

PR delivery policy:

- C01〜C11 の中間 Issue では PR を作成しない。
- 各中間 Issue は local completion、verification、deferred PR delivery evidence を記録して finish し、次の Issue にリレーする。
- C12 だけが Epic branch 全体の PR delivery を担う。
- C12 ではレビュー指摘、CI failure、manual test failure、merge conflict などを修正し、mergeable PR を作成する。

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
- G4 Backend Gate: backend unset fails closed; configured command is explicit.
- G5 ZIP Safety Gate: unsafe ZIPs are rejected before extraction.
- G6 Authority Gate: no ChatGPT output claims canonical adoption / reviewer pass / authorized profile / execution-ready.
- G7 Approval Gate: Epic/Issue node creation remains blocked without explicit human approval.
- G8 Draft Adoption Gate: Issue draft adoption is validated after node creation and before execution handoff.
- G9 Skill Install Gate: installed skills exist in managed skill list and preserve user-facing names.
- G10 Relay Completion Gate: all preceding Issues are finished with deferred PR delivery evidence and no per-Issue PR claim.
- G11 Final Quality Gate: tests, docs, installed asset simulation, dogfood scenario, fresh reviewer evidence pass.
- G12 PR Delivery Gate: final quality gate Issue creates a mergeable PR and repairs reviewer / CI / manual test findings.

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

## Final quality gate

最終 Issue では次を確認する。

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
- `local-context` mode の exact flag 名。現時点の候補は `--evidence-mode local-context`。
