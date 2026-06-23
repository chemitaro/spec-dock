---
種別: 計画書（Epic）
ID: "epic-00224"
タイトル: "Dynamic Workflow Resource Allocation"
関連GitHub: ["#224"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
依存: ["requirement.md", "design.md"]
親: ["init-local-00003"]
---

# epic-00224 Dynamic Workflow Resource Allocation — 計画（Issue と実施順序）

## 計画サマリー

- この plan は reviewer-pass 済み `requirement.md` / `design.md` を、実行可能な Issue slice、依存順、統合 checkpoint、品質 gate、最終 exit contract へ変換する。
- 本 turn では Issue 実体は作成しない。`I01`〜`I07` は Epic plan 上の provisional slice であり、後続の Issue 作成時に `spec-dock new issue` と dependency command へ変換する。
- 初期 rollout では automatic Lite default を有効化しない。Lite は shadow / explicit opt-in / evidence-gated に限定し、future automatic Lite default は別 Issue、ADR、または policy version bump で扱う。
- 実装開始前に、workflow authority に関わる 5 件の ADR を作成 / 承認する Issue を先行させる。

## この計画で閉じる E-RQ / E-AC

| Requirement / AC | 閉じ方 | 主な完了証跡 |
|---|---|---|
| E-RQ-001〜005 | Assurance core、workflow state、fixed Skill kernel、Runbook compiler | CLI contract tests、golden Runbook、clean Git evidence |
| E-RQ-006〜008, E-RQ-015〜021 | Planning composer、Step Assurance、agent context routing | artifact golden tests、step matrix、clean-room review evidence、context packet golden tests、return contract tests |
| E-RQ-009 | trusted base-SHA review policy compiler | trigger JSON、base/head tests、doctor |
| E-RQ-010〜011 | blocker-centric repair / re-review / stagnation | finding matrix、repair loop tests、merge predicate |
| E-RQ-012〜014 | legacy rollout、metrics、provider/mirror、Auto-Lite readiness | migration fixtures、benchmark、auto-lite-readiness report、validate / sync |
| E-AC-001〜003 | I01〜I02 | state / classification tests |
| E-AC-004〜005 | I02 | Runbook candidate/authorized separation、fixed Skill / clean Git tests |
| E-AC-006, E-AC-008 | I03 | profile-specific planning、stale source binding / invalidation tests |
| E-AC-007 | I04 | step routing matrix tests |
| E-AC-009〜010 | I05 | trusted trigger integration tests |
| E-AC-011〜013 | I06 | PR blocker policy tests |
| E-AC-014〜016 | I07 | legacy / rollout / auto-lite-readiness / efficiency report |
| E-AC-017〜021 | I04 | context routing / reviewer independence / reuse / invalidation / return contract tests |

## 課題分割方針（Issue slicing policy）

- 分割原則:
  - 各 Issue は、利用者または agent から観測可能な一つの end-to-end capability を提供する。
  - domain だけ、docs だけ、tests だけの horizontal slice を原則作らない。
  - Provider source、dogfooding mirror、tests、docs を各 Issue 内で閉じる。
  - Issue 間の temporary incompatible state を避け、feature flag / compatibility adapter を用いる。
  - 一つの Issue / PR は、GitHub Codex review が全 diff と direct callers を現実的に追える大きさに保つ。
  - Canonical artifact migration と runtime enforcement を同じ Issue で無制限に広げない。
- 例外:
  - Shared JSON schema / domain model は最初の vertical capability に同梱する。
  - Real GitHub review evaluation は network / external latency を含むため、final rollout Issue の acceptance に置く。
  - Codex Action migration は本 Epic 外の follow-up とする。
  - ADR 作成 / 承認は execution capability ではないため、T0 の prerequisite slice として扱い、execution-ready Issue と混同しない。

## 課題一覧（Issue list / 順序 / tranche 付き）

### T0 — Architecture ADR Prerequisites

- provisional slug:
  - `record-adaptive-workflow-authority-adrs`
- 目的:
  - 後続 implementation Issue が依存する長期 workflow authority 決定を ADR として固定する。
- 成果物:
  - Fixed Skill Kernel And Compiled Runbook Authority ADR。
  - Adaptive Assurance Contract And Monotonic Escalation ADR。
  - Tracked Agent Context Routing Policy And Clean-Room Evaluation ADR。
  - Trusted Base-SHA GitHub Review Policy ADR。
  - Blocker-Centric PR Risk Closure ADR。
- closes:
  - Design の required ADR before implementation。
- 依存:
  - reviewer-pass 済み requirement / design。
- 非対象:
  - runtime implementation。
  - Issue execution readiness の claim。

### I01 — Introduce Assurance Contract And Classification Runtime

- provisional slug:
  - `introduce-assurance-contract-and-classification-runtime`
- 目的:
  - Active Issue に tracked `assurance.json` を作成し、risk facts から Profile / Complexity を分類・表示・検証できる最小 end-to-end capability を提供する。
- 成果物:
  - Assurance domain model / schema / preset。
  - `assurance show / classify / verify`。
  - Standard default、Lite predicates、hard trigger、monotonic escalation foundation。
  - `strict-legacy` detection。
  - Provider / mirror / tests / docs。
- Assurance:
  - strict / deep
- closes:
  - E-RQ-002, E-RQ-003
  - E-AC-002, E-AC-003
- contributes:
  - E-RQ-012 strict-legacy detection prerequisite。正式 close は rollout / compatibility owner の I07。
- 依存:
  - T0
  - `epic-00158` の context-surface 境界。
- 非対象:
  - Skill kernel 切替。
  - artifact composition。
  - GitHub review policy。

### I02 — Compile State-Aware Workflow Runbooks And Fixed Skill Kernels

- provisional slug:
  - `compile-state-aware-workflow-runbooks-and-fixed-skill-kernels`
- 目的:
  - `workflow status / next` を導入し、no-active / requirement-capture / classification-required の current Runbook を生成し、Planning / Execution Skill を fixed kernel にする。
- 成果物:
  - Workflow State Resolver。
  - Runbook schema / compiler / atomic store。
  - `active/current-runbook` と context pack projection。
  - no-active 時の `issue start` guidance。
  - fixed Planning / Execution Skill kernel。
  - generated state で tracked diff が出ない tests。
- Assurance:
  - strict / deep
- closes:
  - E-RQ-001, E-RQ-004, E-RQ-005
  - E-AC-001, E-AC-004, E-AC-005
- 依存:
  - I01
- 非対象:
  - Profile 別 artifact sections。
  - Step execution routing。
  - PR review。

### I03 — Compose Profile-Aware Planning Artifacts

- provisional slug:
  - `compose-profile-aware-planning-artifacts`
- 目的:
  - Provisional / approved Assurance に応じて design / plan / report sections を安全に合成し、planning handoff までを end-to-end で動かす。
- 成果物:
  - Fragment source / preset manifests。
  - design / plan / report composer。
  - stable section markers。
  - pristine/full materialization、substantive/no-overwrite。
  - requirement-stage provisional、design-stage approved、source binding。
  - escalation section 追加と downstream invalidation。
- Assurance:
  - strict / deep
- closes:
  - E-RQ-006
  - E-AC-006, E-AC-008
- 依存:
  - I01
  - I02
- 非対象:
  - Step worker routing。
  - GitHub review。

### I04 — Compile Step Assurance, Agent Routing, And Context Policy

- provisional slug:
  - `compile-step-assurance-agent-routing-and-context-policy`
- 目的:
  - Plan step facts、Issue-wide Assurance、agent role、task kind から、worker、reasoning effort、context mode、verification、reviewer を含む current execution Runbook を生成する。
  - 実行系 agent への必要な context 継承と、reviewer / consultant の clean-room independence を同時に実現する。
  - Main orchestrator へ返る context を圧縮し、sub-agent の再調査と main context pollution を削減する。
- 成果物:
  - Step Assurance schema / compiler。
  - issue global ∪ step local ∪ discovered risk。
  - semantic batch closure。
  - `context-routing-policy.json`。
  - `context-routing-policy.schema.json`。
  - Context Policy Resolver。
  - `recent_fork / bounded_packet / clean_room / minimal_packet`。
  - Role 別 default context policy。
  - Step kind / risk 別 override。
  - Context Packet compiler。
  - Reviewer Evidence Packet compiler。
  - Consultant first-pass / arbitration context contract。
  - worker continuation / reviewer clean-room policy。
  - context source binding と stale invalidation。
  - Main への bounded return contract。
  - Current Runbook への context contract 展開。
  - Invocation evidence と token / payload observability。
  - execution escalation。
- Assurance:
  - strict / deep
- closes:
  - E-RQ-007, E-RQ-008
  - E-RQ-015, E-RQ-016, E-RQ-017, E-RQ-018, E-RQ-019, E-RQ-020, E-RQ-021
  - E-AC-007
  - E-AC-017, E-AC-018, E-AC-019, E-AC-020, E-AC-021
- 依存:
  - I03
- 受け入れ条件:
  - docs-only、runtime behavior、migration、security-sensitive の各 Step で、worker、reasoning、context、verification、reviewers が policy どおりに異なる。
  - `dev-coder` は同一 semantic batch 内で `recent_fork` または `bounded_packet` を利用できる。
  - `code-reviewer`、`qa-reviewer`、`spec-reviewer` は常に clean-room packet を使用する。
  - Reviewer packet へ author self-assessment、implementation transcript、previous reviewer verdict が含まれない。
  - Consultant first pass へ main / architect の推奨案が含まれない。
  - Same source binding と scope では worker thread を継続できる。
  - Source binding、scope、risk の変更後は worker continuation を拒否する。
  - Fork 機能が利用できない場合、worker は bounded packet へ fallback できる。
  - Clean-room を提供できない場合、review を実行せず fail-closed になる。
  - Raw shell transcript、full test log、private reasoning が main agent の return payload へ混入しない。
  - Returned evidence refs の path / hash / missing reason が machine-readable event に残る。
- 主なテスト:
  - context policy schema tests。
  - role routing table tests。
  - context precedence tests。
  - reviewer clean-room exclusion tests。
  - consultant blind-first-pass tests。
  - worker continuation tests。
  - source binding invalidation tests。
  - recent-fork fallback tests。
  - bounded return contract tests。
  - golden Runbook / context packet tests。
  - provider / mirror parity tests。
- 非対象:
  - GitHub PR review trigger。
  - review finding policy。
  - Cross-provider agent context transfer。
  - Private reasoning の保存または転送。

### I05 — Inject Trusted Base-Branch Codex Review Policy

- provisional slug:
  - `inject-trusted-base-branch-codex-review-policy`
- 目的:
  - Project-owned review policy を PR base SHA から取得し、head SHA / policy hash へ bind した deterministic multiline `@codex review` を安全に投稿する。
- 成果物:
  - `.github/codex/review-policy.md` bootstrap-only asset。
  - Policy schema / validator / max size。
  - Base SHA fixed-path fetch。
  - Trigger compiler / evidence。
  - Arbitrary body 禁止。
  - Multiline trigger observation compatibility。
  - doctor capability。
- Assurance:
  - strict / complex
- closes:
  - E-RQ-009
  - E-AC-009, E-AC-010
- 依存:
  - I01
  - Existing `github-pr-observation`
- 並列:
  - I02 と並列開始可能。
- 非対象:
  - Finding blocker policy。
  - Codex Action migration。

### I06 — Enforce Blocker-Centric PR Repair And Re-Review

- provisional slug:
  - `enforce-blocker-centric-pr-repair-and-rereview`
- 目的:
  - P0 / P1 と machine-validated blocker だけを repair loop へ入れ、P2 / P3 noise で push / re-review を反復しない merge-prepared semantics を提供する。
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
  - E-AC-011, E-AC-012, E-AC-013
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
  - Shadow、opt-in、Standard default へ段階移行し、legacy compatibility、metrics、golden scenarios、provider/mirror parity を閉じる。
- 成果物:
  - shadow classification。
  - adaptive opt-in config。
  - new Issue Standard default。
  - Lite manual / evidence-gated activation。
  - `auto-lite-readiness report`。
  - false positive candidates / escalation rate / P0/P1 escape / post-review blocker / wall-clock-token delta / missing metrics summary。
  - strict-legacy adapter。
  - event / metrics projection。
  - benchmark / review-quality corpus。
  - installer migration / docs / validate / sync。
  - rollback runbook。
- Assurance:
  - strict / complex
- closes:
  - E-RQ-012, E-RQ-013, E-RQ-014
  - E-AC-014, E-AC-015, E-AC-016
- 依存:
  - I02, I03, I04, I05, I06
- 非対象:
  - Codex Action production migration。
  - Existing Issue 全量 backfill。
  - Automatic Lite default の有効化。

## Tranche / 依存順

```text
T0 Architecture ADR prerequisites
  |
T1 I01 Assurance core
  |
  +--> T2A I02 Workflow kernel
  |
  +--> T2B I05 Trusted review policy
          |
T3 I03 Planning artifact composer
  |
T4 I04 Step assurance / routing / context policy
  |
  +------+
         |
T5 I06 PR blocker closure
         |
T6 I07 Rollout / telemetry / default switch
```

## Dependency commands（Issue作成後）

> この節は Issue 作成後に実行する予定 command であり、この plan 作成時点では実行しない。

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
  - Tracked Agent Context Routing Policy / clean-room evaluation。
  - Trusted base-SHA review policy。
  - Blocker-centric risk closure。
  - ADR pass 後に implementation Issue を execution-ready にする。
- G1 Core contract:
  - I01 後、classification truth table、legacy detection、schema/versioning を固定する。
  - I02 / I05 が依存できる public application contract を確認する。
- G2 Workflow entrypoint:
  - I02 後、no-active から requirement capture までを manual first-read smoke する。
  - Skill 本文だけで `workflow next` 起動と stop condition が分かること。
  - Git status が clean であること。
- G3 Planning compiler:
  - I03 後、Lite / Standard / Strict / Critical fixture を golden 比較する。
  - substantive content no-overwrite を確認する。
  - approved `assurance.json` 後の requirement / design / plan substantive change が stale source binding として block されることを確認する。
- G4 Execution routing:
  - I04 後、docs-only、runtime、migration、security fixture で routing matrix を確認する。
  - worker context inheritance と reviewer clean-room を区別する。
  - returned evidence refs / missing reason が event に残ることを確認する。
- G5 Review governance:
  - I05 後、base/head policy trust boundary、multiline trigger、stale head を実 PR または fake GitHub で確認する。
  - I06 後、P0/P1、P2 only、promoted P2、stagnation を確認する。
- G9 Rollout:
  - I07 後、shadow / opt-in / Standard default、legacy rollback、metrics を確認する。
  - Epic-wide diff を fresh `deep-consultant`、`spec-reviewer`、code / QA 観点でレビューする。

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
- Context routing:
  - role routing table。
  - clean-room exclusion。
  - consultant blind-first-pass。
  - worker continuation / reset。
  - context packet stale invalidation。
  - bounded return contract。
- CLI:
  - stdout JSON contract。
  - exit code。
  - error guidance。
- Git:
  - generated state ignored。
  - Skill switch で tracked diff なし。
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
  - Lite manual / evidence-gated activation only。
  - automatic Lite default is out of initial rollout。
- Compatibility:
  - Existing Issues are strict-legacy。
  - No automatic canonical artifact rewrite。
- Docs:
  - workflow issue / epic。
  - authoring issue plan。
  - GitHub reference。
  - context routing reference。
  - installer / update ownership。
  - troubleshooting / doctor。
- Review policy:
  - `.github/codex/review-policy.md` は project-owned。
  - `AGENTS.md` から参照しない。
  - bootstrap-only ownership を document する。
- Follow-up:
  - Codex Action + structured output migration。
  - Cross-provider review ensemble。
  - Automatic Lite activation tuning。

## 課題準備完了条件（Issue readiness criteria）

各 Issue は最低限次を持つ。

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

- E-AC-001〜021 に evidence がある。
- 7 implementation Issue が完了または明示的に superseded / deferred されている。
- Required ADR が作成 / 承認され、implementation Issue より先に閉じている。
- New Issue の Standard default path が dogfooding で成功している。
- Existing Issue の strict-legacy path が壊れていない。
- No-active / planning / execution / PR / finish state が current Runbook として動作する。
- Profile / Complexity / Step Assurance が machine-readable。
- Generated state が Git 差分を生まない。
- Trusted base-SHA policy で review trigger が動作する。
- Auto-Lite readiness report が future automatic Lite default の adoption / rollback 条件を示し、初期 rollout では automatic Lite default が無効のままである。
- Context routing policy、context packet、clean-room reviewer packet、bounded return contract が evidence 付きで動作する。
- P2-only review で repair / re-review loop が開始されない。
- P0 / P1 / promoted blocker が閉じるまで merge-prepared にならない。
- Automation-stalled が risk acceptance にならない。
- Provider / mirror / installer / docs / tests が同期している。
- Benchmark で agent invocation、P2 repair push、review generation の改善を確認する。
- Epic-wide fresh review と human merge judgment が完了する。

## 依存 / ブロッカー

- D-001:
  - `epic-00158` の first-read skill / docs / template boundary を前提とする。
- D-002:
  - Codex GitHub review の長文 instruction 遵守は hard guarantee ではないため、Blocker Engine を残す。
- D-003:
  - GitHub policy base-SHA fetch capability が必要。
- D-004:
  - Existing PR observation JSON contract の version migration が必要。
- D-005:
  - Token metric は host/runtime によって取得可能範囲が異なるため、missing を explicit に表現する。

## 未確定事項

- Blocking question:
  - なし。
- Default:
  - Epic は Strict / Deep。
  - New Issue は Standard provisional。
  - Lite は最初は manual / evidence-gated。
  - Review policy size limit は初期 16 KiB を候補とし、実装 Issue で fixture 評価後に確定する。
  - Workflow event retention は generated state で 30 日相当を候補とし、repository policy で override 可能にする。
