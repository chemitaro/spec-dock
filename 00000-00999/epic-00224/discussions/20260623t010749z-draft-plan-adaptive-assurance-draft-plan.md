---
種別: 計画書（Epic）
ID: "<EPIC_ID>"
タイトル: "Adaptive Assurance And Compiled Agent Workflow"
関連GitHub: ["<GITHUB_EPIC_NUMBER_OR_URL>"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-22"
依存: ["requirement.md", "design.md"]
親: ["init-local-00003"]
---

# <EPIC_ID> Adaptive Assurance And Compiled Agent Workflow — 計画（Issue と実施順序）

## この計画で閉じる E-RQ / E-AC

| Requirement / AC | 閉じ方 | 主な完了証跡 |
|---|---|---|
| E-RQ-001〜005 | Assurance core、workflow state、fixed Skill kernel、Runbook compiler | CLI contract tests、golden Runbook、clean Git evidence |
| E-RQ-006〜008 | Planning composer、Step Assurance、agent context routing | artifact golden tests、step matrix、clean-room review evidence |
| E-RQ-009 | trusted base-SHA review policy compiler | trigger JSON、base/head tests、doctor |
| E-RQ-010〜011 | blocker-centric repair / re-review / stagnation | finding matrix、repair loop tests、merge predicate |
| E-RQ-012〜013 | legacy rollout、metrics、provider/mirror | migration fixtures、benchmark、validate / sync |
| E-AC-001〜004 | Issue 1〜2 | state / classification / clean Git tests |
| E-AC-005〜007 | Issue 3〜4 | composer / routing / stale invalidation tests |
| E-AC-008〜009 | Issue 5 | trusted trigger integration tests |
| E-AC-010〜012 | Issue 6 | PR blocker policy tests |
| E-AC-013〜014 | Issue 7 | legacy / rollout / efficiency report |

## 課題分割方針（Issue slicing policy）

- 分割原則:
  - 各Issueは、利用者またはagentから観測可能な一つのend-to-end capabilityを提供する。
  - domainだけ、docsだけ、testsだけのhorizontal sliceを原則作らない。
  - Provider source、dogfooding mirror、tests、docsを各Issue内で閉じる。
  - Issue間のtemporary incompatible stateを避け、feature flag / compatibility adapterを用いる。
  - 一つのIssueのPRは、GitHub Codex reviewが全diffとdirect callersを現実的に追える大きさに保つ。
  - Canonical artifact migrationとruntime enforcementを同じIssueで無制限に広げない。
- 例外:
  - Shared JSON schema / domain modelは最初のvertical capabilityに同梱する。
  - Real GitHub review evaluationはnetwork / external latencyを含むため、final rollout Issueのacceptanceに置く。
  - Codex Action migrationは本Epic外のfollow-upとする。

## 課題一覧（Issue list / 順序 / tranche 付き）

### I01 — Introduce Assurance Contract And Classification Runtime

- provisional slug:
  - `introduce-assurance-contract-and-classification-runtime`
- 目的:
  - Active Issueにtracked `assurance.json`を作成し、risk factsからProfile / Complexityを分類・表示・検証できる最小end-to-end capabilityを提供する。
- 成果物:
  - Assurance domain model / schema / preset。
  - `assurance show / classify / verify`。
  - Standard default、Lite predicates、hard trigger、monotonic escalation foundation。
  - `strict-legacy` detection。
  - Provider / mirror / tests / docs。
- Assurance:
  - strict / deep
- closes:
  - E-RQ-002, E-RQ-003, E-RQ-012
  - E-AC-002, E-AC-003, E-AC-013
- 依存:
  - `epic-00158`のcontext-surface境界。
- 非対象:
  - Skill kernel切替。
  - artifact composition。
  - GitHub review policy。

### I02 — Compile State-Aware Workflow Runbooks And Fixed Skill Kernels

- provisional slug:
  - `compile-state-aware-workflow-runbooks-and-fixed-skill-kernels`
- 目的:
  - `workflow status / next`を導入し、no-active / requirement-capture / classification-requiredのcurrent Runbookを生成し、Planning / Execution Skillをfixed kernelにする。
- 成果物:
  - Workflow State Resolver。
  - Runbook schema / compiler / atomic store。
  - `active/current-runbook`とcontext pack projection。
  - no-active時の`issue start` guidance。
  - fixed Planning / Execution Skill kernel。
  - generated stateでtracked diffが出ないtests。
- Assurance:
  - strict / deep
- closes:
  - E-RQ-001, E-RQ-004, E-RQ-005
  - E-AC-001, E-AC-004
- 依存:
  - I01
- 非対象:
  - Profile別artifact sections。
  - Step execution routing。
  - PR review。

### I03 — Compose Profile-Aware Planning Artifacts

- provisional slug:
  - `compose-profile-aware-planning-artifacts`
- 目的:
  - Provisional / approved Assuranceに応じてdesign / plan / report sectionsを安全に合成し、planning handoffまでをend-to-endで動かす。
- 成果物:
  - Fragment source / preset manifests。
  - design / plan / report composer。
  - stable section markers。
  - pristine/full materialization、substantive/no-overwrite。
  - requirement-stage provisional、design-stage approved、source binding。
  - escalation section追加とdownstream invalidation。
- Assurance:
  - strict / deep
- closes:
  - E-RQ-006
  - E-AC-005, E-AC-007
- 依存:
  - I01
  - I02
- 非対象:
  - Step worker routing。
  - GitHub review。

### I04 — Compile Step Assurance And Agent Routing

- provisional slug:
  - `compile-step-assurance-and-agent-routing`
- 目的:
  - plan step factsからeffective obligationsを計算し、worker、reasoning、context、verification、reviewerを含むcurrent execution Runbookを生成する。
- 成果物:
  - Step Assurance schema / compiler。
  - issue global ∪ step local ∪ discovered risk。
  - semantic batch closure。
  - recent-fork / packet / clean-room routing。
  - worker continuation / reviewer fresh policy。
  - execution escalation。
- Assurance:
  - strict / deep
- closes:
  - E-RQ-007, E-RQ-008
  - E-AC-006, E-AC-007
- 依存:
  - I03
- 非対象:
  - GitHub PR review trigger。
  - review finding policy。

### I05 — Inject Trusted Base-Branch Codex Review Policy

- provisional slug:
  - `inject-trusted-base-branch-codex-review-policy`
- 目的:
  - Project-owned review policyをPR base SHAから取得し、head SHA / policy hashへbindしたdeterministic multiline `@codex review`を安全に投稿する。
- 成果物:
  - `.github/codex/review-policy.md` bootstrap-only asset。
  - Policy schema / validator / max size。
  - Base SHA fixed-path fetch。
  - Trigger compiler / evidence。
  - Arbitrary body禁止。
  - Multiline trigger observation compatibility。
  - doctor capability。
- Assurance:
  - strict / complex
- closes:
  - E-RQ-009
  - E-AC-008, E-AC-009
- 依存:
  - I01
  - Existing `github-pr-observation`
- 並列:
  - I02と並列開始可能。
- 非対象:
  - Finding blocker policy。
  - Codex Action migration。

### I06 — Enforce Blocker-Centric PR Repair And Re-Review

- provisional slug:
  - `enforce-blocker-centric-pr-repair-and-rereview`
- 目的:
  - P0 / P1とmachine-validated blockerだけをrepair loopへ入れ、P2 / P3 noiseでpush / re-reviewを反復しないmerge-prepared semanticsを提供する。
- 成果物:
  - reported / validated priority。
  - protected domain / machine evidence promotion。
  - P2 default no-action / follow-up。
  - fresh re-review condition。
  - review-exempt / opportunistic observation。
  - finding fingerprint / stagnation / automation-stalled。
  - updated repair batch / merge predicate。
- Assurance:
  - strict / deep
- closes:
  - E-RQ-010, E-RQ-011
  - E-AC-010, E-AC-011, E-AC-012
- 依存:
  - I04
  - I05
- 非対象:
  - Automatic merge。
  - Human risk acceptance automation。

### I07 — Roll Out Adaptive Workflow With Legacy Compatibility And Telemetry

- provisional slug:
  - `roll-out-adaptive-workflow-with-legacy-compatibility-and-telemetry`
- 目的:
  - Shadow、opt-in、Standard defaultへ段階移行し、legacy compatibility、metrics、golden scenarios、provider/mirror parityを閉じる。
- 成果物:
  - shadow classification。
  - adaptive opt-in config。
  - new Issue Standard default。
  - Lite manual / evidence-gated activation。
  - strict-legacy adapter。
  - event / metrics projection。
  - benchmark / review-quality corpus。
  - installer migration / docs / validate / sync。
  - rollback runbook。
- Assurance:
  - strict / complex
- closes:
  - E-RQ-012, E-RQ-013
  - E-AC-013, E-AC-014
- 依存:
  - I02, I03, I04, I05, I06
- 非対象:
  - Codex Action production migration。
  - Existing Issue全量backfill。

## Tranche / 依存順

```text
T0 Epic authoring / ADR
  |
T1 I01 Assurance core
  |
  +--> T2A I02 Workflow kernel
  |
  +--> T2B I05 Trusted review policy
          |
T3 I03 Planning artifact composer
  |
T4 I04 Step assurance / routing
  |
  +------+
         |
T5 I06 PR blocker closure
         |
T6 I07 Rollout / telemetry / default switch
```

## Dependency commands（Issue作成後）

```bash
# I02 -> I01
./spec-dock/scripts/spec-dock deps add --from <I02_ID> --to <I01_ID>

# I03 -> I01, I02
./spec-dock/scripts/spec-dock deps add --from <I03_ID> --to <I01_ID>
./spec-dock/scripts/spec-dock deps add --from <I03_ID> --to <I02_ID>

# I04 -> I03
./spec-dock/scripts/spec-dock deps add --from <I04_ID> --to <I03_ID>

# I05 -> I01
./spec-dock/scripts/spec-dock deps add --from <I05_ID> --to <I01_ID>

# I06 -> I04, I05
./spec-dock/scripts/spec-dock deps add --from <I06_ID> --to <I04_ID>
./spec-dock/scripts/spec-dock deps add --from <I06_ID> --to <I05_ID>

# I07 -> I02..I06
./spec-dock/scripts/spec-dock deps add --from <I07_ID> --to <I02_ID>
./spec-dock/scripts/spec-dock deps add --from <I07_ID> --to <I03_ID>
./spec-dock/scripts/spec-dock deps add --from <I07_ID> --to <I04_ID>
./spec-dock/scripts/spec-dock deps add --from <I07_ID> --to <I05_ID>
./spec-dock/scripts/spec-dock deps add --from <I07_ID> --to <I06_ID>
```

## 統合チェックポイント

- G0 Architecture / ADR:
  - Fixed Skill Kernel / Compiled Runbook。
  - Assurance Contract / monotonic escalation。
  - Trusted base-SHA review policy。
  - Blocker-centric risk closure。
  - Fresh `spec-reviewer`と`deep-consultant`でEpic designを確認する。

- G1 Core contract:
  - I01後、classification truth table、legacy detection、schema/versioningを固定する。
  - I02 / I05が依存できるpublic application contractを確認する。

- G2 Workflow entrypoint:
  - I02後、no-activeからrequirement captureまでをmanual first-read smokeする。
  - Skill本文だけで`workflow next`起動とstop conditionが分かること。
  - Git statusがcleanであること。

- G3 Planning compiler:
  - I03後、Lite / Standard / Strict / Critical fixtureをgolden比較する。
  - substantive content no-overwriteを確認する。

- G4 Execution routing:
  - I04後、docs-only、runtime、migration、security fixtureでrouting matrixを確認する。
  - worker context inheritanceとreviewer clean-roomを区別する。

- G5 Review governance:
  - I05後、base/head policy trust boundary、multiline trigger、stale headを実PRまたはfake GitHubで確認する。
  - I06後、P0/P1、P2 only、promoted P2、stagnationを確認する。

- G9 Rollout:
  - I07後、shadow / opt-in / Standard default、legacy rollback、metricsを確認する。
  - Epic-wide diffをfresh `deep-consultant`、`spec-reviewer`、code / QA観点でレビューする。

## 品質ゲート

- Domain:
  - policy truth table。
  - state transition completeness。
  - invariant tests。
- Compiler:
  - golden output。
  - idempotence。
  - atomic write。
  - no-overwrite。
  - no unused profile text。
- CLI:
  - stdout JSON contract。
  - exit code。
  - error guidance。
- Git:
  - generated state ignored。
  - Skill switchでtracked diffなし。
- Provider / mirror:
  - provider source authority。
  - dogfooding semantic parity。
  - installer init / update。
- PR:
  - trusted policy source。
  - head freshness。
  - P2 suppression。
  - blocker repair。
  - no merge on automation-stalled。
- Docs:
  - workflow / reference / migration / rollback。
- Final:
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync`
  - targeted and full relevant test suites。

## ロールアウト / ドキュメント影響

- Rollout:
  - shadow only。
  - explicit opt-in。
  - selected dogfooding Issues。
  - Standard default for new Issues。
  - Lite enablement。
- Compatibility:
  - Existing Issues are strict-legacy。
  - No automatic canonical artifact rewrite。
- Docs:
  - workflow issue / epic。
  - authoring issue plan。
  - GitHub reference。
  - installer / update ownership。
  - troubleshooting / doctor。
- Review policy:
  - `.github/codex/review-policy.md`はproject-owned。
  - `AGENTS.md`から参照しない。
  - bootstrap-only ownershipをdocumentする。
- Follow-up:
  - Codex Action + structured output migration。
  - Cross-provider review ensemble。
  - Automatic Lite activation tuning。

## 課題準備完了条件（Issue readiness criteria）

各Issueは最低限次を持つ。

- Parent Epic E-RQ / E-AC trace。
- Observable end-to-end capability。
- Scope / non-scope。
- Provider source / dogfooding mirror paths。
- Public CLI / schema compatibility。
- Migration / rollback。
- Exact targeted tests。
- Assurance Profile / Complexity Tier。
- Context policy / reviewer independence。
- PR external review policy。
- Downstream dependency and unblock output。
- No unresolved requirement / design gap。

## 最終完了条件

- E-AC-001〜014にevidenceがある。
- 7 Issueが完了または明示的にsuperseded / deferredされている。
- New IssueのStandard default pathがdogfoodingで成功している。
- Existing Issueのstrict-legacy pathが壊れていない。
- No-active / planning / execution / PR / finish stateがcurrent Runbookとして動作する。
- Profile / Complexity / Step Assuranceがmachine-readable。
- Generated stateがGit差分を生まない。
- Trusted base-SHA policyでreview triggerが動作する。
- P2-only reviewでrepair / re-review loopが開始されない。
- P0 / P1 / promoted blockerが閉じるまでmerge-preparedにならない。
- Automation-stalledがrisk acceptanceにならない。
- Provider / mirror / installer / docs / testsが同期している。
- Benchmarkでagent invocation、P2 repair push、review generationの改善を確認する。
- Epic-wide fresh reviewとhuman merge judgmentが完了する。

## 依存 / ブロッカー

- D-001:
  - `epic-00158`のfirst-read skill / docs / template boundaryを前提とする。
- D-002:
  - Codex GitHub reviewの長文instruction遵守はhard guaranteeではないため、Blocker Engineを残す。
- D-003:
  - GitHub policy base-SHA fetch capabilityが必要。
- D-004:
  - Existing PR observation JSON contractのversion migrationが必要。
- D-005:
  - Token metricはhost/runtimeによって取得可能範囲が異なるため、missingをexplicitに表現する。

## 未確定事項

- Blocking question:
  - なし。
- Default:
  - EpicはStrict / Deep。
  - New IssueはStandard provisional。
  - Liteは最初はmanual / evidence-gated。
  - Review policy size limitは初期16 KiBを候補とし、実装Issueでfixture評価後に確定する。
  - Workflow event retentionはgenerated stateで30日相当を候補とし、repository policyでoverride可能にする。
