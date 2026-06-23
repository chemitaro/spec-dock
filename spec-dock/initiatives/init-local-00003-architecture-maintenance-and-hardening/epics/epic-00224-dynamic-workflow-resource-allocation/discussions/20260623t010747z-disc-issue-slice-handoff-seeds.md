# Issue Slice Handoff Seeds

この文書は Epic planning から各 Issue planning へ渡す seed であり、各 Issue の canonical requirement / design / plan ではない。Issue作成後、runtime-owned `draft-requirement` / `draft-design` discussionへ必要部分を移し、個別 Issue workflowで正式化する。

---

## I01 Introduce Assurance Contract And Classification Runtime

### Requirement seed

- 目的:
  - Active IssueについてAssurance Contractを作成、分類、表示、検証できる。
- 必須:
  - Standard default。
  - Lite all-positive eligibility。
  - Strict / Critical hard trigger。
  - Complexity Tier分離。
  - strict-legacy detection。
- AC:
  - `assurance classify --stage requirement`がvalid JSONを作る。
  - same inputsでsame classification。
  - unknown protected factでLiteにならない。
  - existing issue without contractはlegacy判定。
- 非対象:
  - Skill kernel、artifact compiler、PR review。

### Design seed

- Domain-first。
- JSON schema version 1。
- Issue-local tracked file。
- Classification pure function + evidence refs。
- Provider/mirror parity。
- Rollbackはcontract ignored + legacy。

---

## I02 Compile State-Aware Workflow Runbooks And Fixed Skill Kernels

### Requirement seed

- 目的:
  - Agentが現在状態を推測せず、`workflow next`から一つのRunbookを受け取る。
- 必須:
  - no-active、requirement-capture、classification-required。
  - Markdown / JSON output。
  - atomic generated files。
  - Planning / Execution fixed kernel。
- AC:
  - no-activeでissue start以外を返さない。
  - Issue切替でtracked Skill差分が出ない。
  - Runbookは未選択Profile本文を含まない。

### Design seed

- State Resolver + Runbook Compiler。
- `.agent/runbooks` / `active/current-runbook`。
- symlink不要。
- stdout authority、file projection。
- fixed kernelは8項目以下のbootstrap flowを目標。

---

## I03 Compose Profile-Aware Planning Artifacts

### Requirement seed

- 目的:
  - Assuranceに応じて必要なdesign / plan / report sectionを安全に合成する。
- 必須:
  - fragment manifest。
  - no-overwrite。
  - idempotence。
  - provisional / approved source binding。
  - escalation additive。
- AC:
  - Profile fixtureごとに期待section。
  - same compile twiceでdiffなし。
  - substantive body保持。
  - source changeでstale。

### Design seed

- Stable section markers。
- Pristine/full vs additive mode。
- Fragment IDs / policy version。
- Design approval後plan compile。
- downgrade deletes nothing。

---

## I04 Compile Step Assurance And Agent Routing

### Requirement seed

- 目的:
  - Step内容に応じたworker / reasoning / context / verification / reviewをcompileする。
- 必須:
  - semantic batch。
  - global + local + discovered obligations。
  - worker context affinity。
  - reviewer clean-room。
  - escalation。
- AC:
  - docs-only / code / migration / security fixtureのroutingが異なる。
  - current stepだけがRunbookに出る。
  - new riskでnext stepへ進まずreapprovalを要求。

### Design seed

- Step facts schema。
- Obligation lattice。
- ContextPolicy VO。
- Review invalidation matrix。
- worker thread reuse条件。

---

## I05 Inject Trusted Base-Branch Codex Review Policy

### Requirement seed

- 目的:
  - Base SHA上のreview policyをreview時だけCodexへ渡す。
- 必須:
  - `.github/codex/review-policy.md`。
  - bootstrap-only ownership。
  - fixed path / base SHA。
  - deterministic multiline body。
  - head / policy hash evidence。
  - arbitrary body禁止。
- AC:
  - head側policy changeが当該reviewに効かない。
  - missing policyでhuman gate。
  - existing trigger boundary / parserと互換。

### Design seed

- ReviewPolicyStore。
- Trigger compiler。
- UTF-8 / NUL / size / schema validation。
- fixed GitHub write endpoint。
- multiline first line `@codex review`。

---

## I06 Enforce Blocker-Centric PR Repair And Re-Review

### Requirement seed

- 目的:
  - Verified blockerだけをrepairし、P2 noiseによるloopを止める。
- 必須:
  - P0/P1 blocker。
  - P2 default no-action。
  - protected + machine evidence promotion。
  - stale SHA exclusion。
  - re-review matrix。
  - automation-stalled。
- AC:
  - P2-onlyでpush / triggerなし。
  - P1 fixでfresh review。
  - promoted P2 fixでfresh review。
  - same fingerprintでhuman gate。
  - blocker残存でmerge-preparedにならない。

### Design seed

- Finding normalization。
- Protected domain registry。
- Machine evidence types。
- ReviewCoverage。
- Required / opportunistic modes。
- Attempt limit is stagnation only。

---

## I07 Roll Out Adaptive Workflow With Legacy Compatibility And Telemetry

### Requirement seed

- 目的:
  - Adaptive workflowを安全にdefault化し、改善効果を測定する。
- 必須:
  - shadow、opt-in、Standard default。
  - legacy strict。
  - metrics。
  - rollback。
  - provider/mirror/installer/docs。
- AC:
  - existing fixtures unchanged。
  - new fixture Standard。
  - generated state clean。
  - benchmarkでinvocation / review loop低下。
  - rollbackでlegacy execution可能。

### Design seed

- Repository mode config。
- Event schema / retention。
- Metrics missing semantics。
- Golden workflow corpus。
- Review quality corpus。
- Default switch gate。
