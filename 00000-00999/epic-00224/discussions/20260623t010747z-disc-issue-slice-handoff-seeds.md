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

## I04 Compile Step Assurance, Agent Routing, And Context Policy

### Requirement seed

- 目的:
  - Plan step facts、Issue-wide Assurance、agent role、task kindから、worker、reasoning effort、context mode、verification、reviewerを含むcurrent execution Runbookを生成する。
  - 実行系agentへの必要なcontext継承と、reviewer / consultantのclean-room independenceを同時に実現する。
  - Main orchestratorへ返るcontextを圧縮し、subagentの再調査とmain context pollutionを削減する。
- 必須:
  - semantic batch。
  - global + local + discovered obligations。
  - tracked `context-routing-policy.json`。
  - `recent_fork / bounded_packet / clean_room / minimal_packet`。
  - role別default context policy。
  - worker context affinity / continuation。
  - reviewer clean-room / consultant first-pass independence。
  - context source binding / stale invalidation。
  - bounded child return contract。
  - invocation evidence and context observability。
  - escalation。
- AC:
  - docs-only / code / migration / security fixtureのroutingが異なる。
  - current stepだけがRunbookに出る。
  - `dev-coder`は同一semantic batch内で`recent_fork`または`bounded_packet`を利用できる。
  - `code-reviewer`、`qa-reviewer`、`spec-reviewer`は常に`clean_room` packetを使用する。
  - Reviewer packetへauthor self-assessment、implementation transcript、previous reviewer verdictが含まれない。
  - Consultant first passへmain / architectの推奨案が含まれない。
  - Same source bindingとscopeではworker threadを継続できる。
  - Source binding、scope、riskの変更後はworker continuationを拒否する。
  - Fork機能が利用できない場合、workerは`bounded_packet`へfallbackできる。
  - Clean-roomを提供できない場合、reviewを実行せずfail-closedになる。
  - Raw shell transcript、full test log、private reasoningがmain agentのreturn payloadへ混入しない。
  - new riskでnext stepへ進まずreapprovalを要求。

### Design seed

- Step facts schema。
- Obligation lattice。
- ContextPolicy VO。
- Context Routing Policy schema。
- Context Policy Resolver。
- Context Packet / Reviewer Evidence Packet compiler。
- Consultant first-pass / arbitration context contract。
- Context source binding and packet stale invalidation。
- bounded return contract。
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
  - `auto-lite-readiness report`。
  - future automatic Lite default の adoption / rollback 条件。
  - metrics。
  - rollback。
  - provider/mirror/installer/docs。
- AC:
  - existing fixtures unchanged。
  - new fixture Standard。
  - automatic Lite default は有効化されない。
  - auto-lite-readiness report に false positive candidates、escalation rate、P0/P1 escape、post-review blocker、wall-clock/token delta、missing metrics が出る。
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
