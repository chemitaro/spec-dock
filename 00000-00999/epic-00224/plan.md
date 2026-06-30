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
- Issue 実体は作成済み。実装対象は `I01`〜`I07` の `iss-00227`〜`iss-00233` に対応する。
- `iss-00226 / #226` は decision-only Issue として作成されたが、ADR-level decisions はこの Epic planning/design で固定すべきだったため closed / superseded historical evidence とする。
- 初期 rollout では automatic Lite default を有効化しない。Lite は shadow / explicit opt-in / evidence-gated に限定し、future automatic Lite default は別 accepted ADR、policy version bump、rollout Issue、telemetry gate が揃った場合だけ扱う。
- 実装開始前の workflow authority decision は、当初 Epic-scope accepted ADR 5 件として作成済みだった。その後の dogfooding修正により、script-local review instruction と explicit review completion を含む current ADR baseline へ変更済み。
- dogfooding修正により、issue execution authority は `20260629t003131z-adr` の plan-centric preflight、Assurance Contract path は `20260629t003132z-adr` の `.assurance.json` へ変更済み。
- `iss-00247 / #247` で profile Markdown templates は導入済みだが、manual test / follow-up analysis により、問題は `new doc draft-design` / `draft-plan` の source routing だけではなく、artifact readiness preflight、grade-aware Issue authoring guidance、delegated specialist routing、fresh review / report evidence gate、grade-aware smoke tests まで広がると整理した。
- そのため、以前の `I08` 単独案は採用せず、追加 corrective tranche を `R0 + G1〜G4` として計画する。既存 I01〜I07 と完了済み corrective work はそのまま保持する。
- `iss-00250` はこの corrective tranche の一部を検討するために一時的に作成したデータ置き場であり、正式な implementation Issue としては採用しない。正式 Issue は `iss-00251`〜`iss-00255` として作成済みであり、R0 / G1 / G2 / G3 / G4 に対応付ける。

## この計画で閉じる E-RQ / E-AC

| Requirement / AC | 閉じ方 | 主な完了証跡 |
|---|---|---|
| E-RQ-001〜005 | Assurance core、workflow state、fixed Skill kernel、plan-centric preflight guidance | CLI contract tests、guidance/runbook projection evidence、clean Git evidence |
| E-RQ-006 | I03 の initial planning composer と R0 の fail-closed artifact readiness preflight | profile template golden tests、readiness classifier regression、workflow/guidance fail-closed tests |
| E-RQ-007〜008, E-RQ-015〜021 | Step Assurance、agent context routing | step matrix、clean-room review evidence、context packet golden tests、return contract tests |
| E-RQ-009 | review trigger instruction compiler | 変更済み: trusted base-SHA policy は script-local instruction source へ置換。trigger JSON、local instruction tests、runtime validation、I07 doctor defer |
| E-RQ-010〜011 | blocker-centric repair / re-review / stagnation | finding matrix、repair loop tests、merge predicate |
| E-RQ-012〜014 | legacy rollout、metrics、provider/mirror、Auto-Lite readiness | migration fixtures、benchmark、auto-lite-readiness report、validate / sync |
| E-RQ-022 | G1〜G3 の grade-aware authoring guidance、delegated specialist / draft routing、fresh review / evidence gate | guidance tests、`new doc` CLI tests、report evidence tests、provider / dogfooding docs inspection |
| E-AC-001〜003 | I01〜I02 | state / classification tests |
| E-AC-004〜005 | I02 | Runbook candidate/authorized separation、fixed Skill / clean Git tests |
| E-AC-006 | I03 + R0 | profile-specific planning、fail-closed readiness、placeholder / executable plan classifier tests |
| E-AC-008 | I03 | stale source binding / invalidation tests |
| E-AC-007 | I04 | step routing matrix tests |
| E-AC-009〜010 | I05 / iss-00244 corrective scope | 変更済み: script-local trigger integration tests and explicit review completion observation tests |
| E-AC-011〜012 | I06 | PR blocker policy tests |
| E-AC-013 | I07 | automation-stalled rollout / telemetry tests |
| E-AC-014〜016 | I07 | legacy / rollout / auto-lite-readiness / efficiency report |
| E-AC-017〜021 | I04 | context routing / reviewer independence / reuse / invalidation / return contract tests |
| E-AC-022 | G1〜G4 | grade-aware Issue authoring workflow、profile-aware draft routing、delegated specialist evidence、fresh review gate、smoke tests |

## 課題分割方針（Issue slicing policy）

- 分割原則:
  - 各 Issue は、利用者または agent から観測可能な一つの end-to-end capability を提供する。
  - domain だけ、docs だけ、tests だけの horizontal slice を原則作らない。
  - Provider source、dogfooding mirror、tests、docs を各 Issue 内で閉じる。
  - Issue 間の temporary incompatible state を避け、feature flag / compatibility adapter を用いる。
  - 個別 Issue はレビュー可能な commit / checkpoint 単位に保つ。R0 + G1〜G4 corrective tranche は Issue ごとに PR を作らず、最終的に Epic 単位の 1 PR として GitHub Codex review が追える差分・証跡に整える。
  - Canonical artifact migration と runtime enforcement を同じ Issue で無制限に広げない。
- 例外:
  - Shared JSON schema / domain model は最初の vertical capability に同梱する。
  - Real GitHub review evaluation は network / external latency を含むため、final rollout Issue の acceptance に置く。
  - Codex Action migration は本 Epic 外の follow-up とする。
  - ADR 作成 / 承認は execution capability ではないため、Issue slice へ切り出さず Epic-scope `IC0` gate として扱う。
  - Cross-issue authoring source authority の判断は Epic requirement / design / plan に置き、Issue slice は runtime / tests / docs の実装だけを担う。

## 課題一覧（Issue list / 順序 / tranche 付き）

### I01 — Introduce Assurance Contract And Classification Runtime（iss-00227 / #227）

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
  - IC0 Epic Decision Baseline。
  - `epic-00158` の context-surface 境界。
- 非対象:
  - Skill kernel 切替。
  - artifact composition。
  - GitHub review policy。

### I02 — Compile State-Aware Workflow Runbooks And Fixed Skill Kernels（iss-00228 / #228）

- provisional slug:
  - `compile-state-aware-workflow-runbooks-and-fixed-skill-kernels`
- 目的:
  - `guidance <target>` を current agent handoff entrypoint とし、no-active / requirement-capture / classification-required の stdout guidance を生成し、Planning / Execution Skill を fixed kernel にする。
  - Historical implementation notes may refer to `workflow status / next`; current operational contract supersedes `workflow next` with `guidance <target>`.
- 成果物:
  - Workflow State Resolver。
  - Runbook schema / compiler / atomic store。
  - `active/current-runbook` と context pack projection。ただし projection は human/debug-only non-canonical output であり、agent handoff authority ではない。
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

### I03 — Compose Profile-Aware Planning Artifacts（iss-00229 / #229）

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
  - E-RQ-006 の initial artifact composition / profile template materialization subset
  - E-AC-006 の profile-specific planning subset
  - E-AC-008
- amended closure:
  - fail-closed readiness preflight、shared placeholder detector、executable plan predicate、stale reviewer / missing adoption evidence block は R0 で閉じる。
- 依存:
  - I01
  - I02
- 非対象:
  - Step worker routing。
  - GitHub review。

### I04 — Compile Step Assurance, Agent Routing, And Context Policy（iss-00230 / #230）

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

### I05 — Inject Trusted Base-Branch Codex Review Policy（iss-00231 / #231）

> 変更済み: この slice の旧 trusted base-SHA review policy 方針は、PR #245 dogfooding failure 後に `20260623t074444z-adr` / `iss-00244` により script-local Codex review instruction source へ置換済み。さらに review completion 終了条件は `20260628t154553z-adr` により explicit Codex artifact model へ変更済み。

- provisional slug:
  - `inject-trusted-base-branch-codex-review-policy`
- 目的:
  - Historical objective: Project-owned review policy を PR base SHA から取得し、head SHA / policy hash へ bind した deterministic multiline `@codex review` を安全に投稿する。
  - Current objective: script-local review instruction を読み、head SHA / instruction hash へ bind した deterministic multiline `@codex review` を安全に投稿する。
- 成果物:
  - script-local `github-pr-observation` review instruction asset。
  - instruction path / instruction SHA-256 / reviewed head SHA binding。
  - instruction runtime validator:
    - non-empty UTF-8。
    - max size。
    - invalid / unreadable / oversized / non-UTF-8 の no PR comment + human gate / fail-closed。
    - missing instruction の plain deterministic fallback。
  - Trigger compiler / evidence。
  - Arbitrary body 禁止。
  - Multiline trigger observation compatibility。
  - Dedicated script-local instruction doctor capability は I07 rollout / operationalization へ defer。
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

### I06 — Enforce Blocker-Centric PR Repair And Re-Review（iss-00232 / #232）

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
  - finding fingerprint / stagnation evidence。
  - Dedicated automation-stalled operator surfacing は I07 rollout / telemetry へ defer。
  - updated repair batch / merge predicate。
- Assurance:
  - strict / deep
- closes:
  - E-RQ-010, E-RQ-011
  - E-AC-011, E-AC-012
- provides to I07:
  - E-AC-013 prerequisite: blocker fingerprint evidence for stagnation detection。
- 依存:
  - I04
  - I05
- 非対象:
  - Automatic merge。
  - Human risk acceptance automation。

### I07 — Roll Out Adaptive Workflow With Legacy Compatibility And Telemetry（iss-00233 / #233）

- provisional slug:
  - `roll-out-adaptive-workflow-with-legacy-compatibility-and-telemetry`
- 目的:
  - 初期 rollout では automatic Lite default を有効化せず、strict-legacy compatibility、Auto-Lite readiness、automation-stalled operator surface、efficiency evidence、provider/mirror parity を閉じる。
- 成果物:
  - `auto-lite-readiness report` with `automatic_lite_default_enabled=false`。
  - future automatic Lite adoption gates: accepted ADR、policy version bump、rollout Issue、telemetry gate。
  - required metrics list: false positive candidates / escalation rate / P0/P1 escape / post-review blocker / wall-clock-token delta / missing metrics summary。
  - efficiency baseline fixture comparing Lite / Standard / Strict expected workflow cost。
  - substantive requirement + missing assurance strict-legacy workflow compatibility。
  - repeated blocker fingerprint `automation_stalled` / human gate operator surface。
  - provider / dogfooding mirror parity and validation evidence。
  - rollback mode recorded as `strict-legacy`。
- Assurance:
  - strict / complex
- closes:
  - E-RQ-012, E-RQ-013, E-RQ-014
  - E-AC-013
  - E-AC-014, E-AC-015, E-AC-016
- 依存:
  - I02, I03, I04, I05, I06
- 非対象:
  - Codex Action production migration。
  - Existing Issue 全量 backfill。
  - Automatic Lite default の有効化。

### R0 — Enforce Fail-Closed Issue Artifact Readiness Preflight（iss-00251 / #251）

- provisional slug:
  - `enforce-fail-closed-issue-artifact-readiness-preflight`
- 位置づけ:
  - `iss-00247 / #247` 後の manual test で確認した F-001〜F-004 を直接閉じる最優先 corrective slice。
  - `assurance compose` 成功と execution readiness を分離し、未完成 artifact が `ready` になる false positive を止める。
- 目的:
  - `workflow status` / `guidance issue-execution` が requirement / design / plan / report evidence を fail-closed に判定し、placeholder / heading-only / stale evidence を execution-ready にしない。
- 成果物:
  - shared placeholder detector。
  - requirement の `REQ-XXX` / `CON-...` / placeholder sentinel 検出。
  - plan の executable marker と quality marker の分離。
  - design の scaffold marker 判定 narrow 化。
  - stale reviewer / missing adoption evidence の readiness block。
  - `tests/unit/domain/test_workflow_state.py` と `tests/cli_runtime/test_workflow.py` の F-001〜F-004 regression。
- Assurance:
  - strict / normal
  - execution readiness に関わるため、runtime classification が Standard 相当でも manual escalation として strict review gate を使う。
- closes:
  - E-RQ-006
  - E-AC-006
- 依存:
  - `iss-00247 / #247`
  - existing workflow state / guidance contract
- 非対象:
  - Issue planning guidance の全文再構成。
  - delegated specialist role routing。
  - profile template 本文の全面改訂。

### G1 — Compile Grade-Aware Issue Planning Guidance（iss-00252 / #252）

- provisional slug:
  - `compile-grade-aware-issue-planning-guidance`
- 位置づけ:
  - `20260630t111316z-adr` の grade-aware Issue authoring rules を runtime / docs / guidance へ反映する slice。
- 目的:
  - Issue planning guidance が `lite / standard / strict / critical` ごとに requirement / design / plan / review / report evidence の作業ルールを示し、agent が旧 step-centric / one-size-fits-all planning に戻らないようにする。
- 成果物:
  - `guidance issue-planning` または関連 docs の grade-aware authoring matrix。
  - `authorized_profile` と manual escalation の分離説明。
  - Lite automatic default 禁止、unknown / ambiguous は Standard 以上の guidance。
  - `standard` の specialist 推奨 / 未使用理由、`strict` / `critical` の原則必須 / fallback evidence。
  - provider docs と dogfooding docs parity。
- Assurance:
  - strict / normal
- closes:
  - E-RQ-022 の grade-aware planning guidance subset
  - E-AC-022 の guidance subset
- 依存:
  - `iss-00251 / #251`
  - `20260630t111316z-adr`
- 非対象:
  - `new doc draft-design` / `draft-plan` routing 実装。
  - smoke test matrix の全量。

### G2 — Connect Delegated Specialist Role Routing And Draft Artifact Sources（iss-00253 / #253）

- provisional slug:
  - `connect-delegated-specialist-routing-and-draft-artifact-sources`
- 位置づけ:
  - grade-aware authoring guidance を、`system-architect` / `implementation-planner` 相当の delegated specialist routing と discussion draft generation に接続する slice。
- 目的:
  - classified Issue の `draft-design` / `draft-plan` が `authorized_profile` に対応する profile template から生成され、delegated specialist draft が canonical docs ではなく evidence として扱われることを runtime / docs / tests で固定する。
- 成果物:
  - Issue `new doc draft-design` / `draft-plan` の profile-aware routing。
  - `.assurance.json` missing / invalid / stale 時の no-write fail-closed。
  - `draft-requirement` と Initiative / Epic draft の既存挙動維持。
  - delegated specialist draft provenance / self-claim 禁止 guidance。
  - `tests/cli_runtime/test_new.py` と profile template validation regression。
- Assurance:
  - strict / normal
- closes:
  - E-RQ-022 の delegated draft / profile-aware draft routing subset
  - E-AC-022 の draft routing subset
- 依存:
  - `iss-00252 / #252`
  - profile Markdown templates
- 非対象:
  - `system-architect` / `implementation-planner` role skill の新規 shipped asset 化。
  - canonical design / plan の直接 rewrite。

### G3 — Add Grade-Aware Spec Review And Evidence Gates（iss-00254 / #254）

- provisional slug:
  - `add-grade-aware-spec-review-and-evidence-gates`
- 位置づけ:
  - grade-aware authoring guidance を phase promotion / issue readiness の証跡 gate へ接続する slice。
- 目的:
  - Fresh `spec-reviewer`、Evidence Adoption Ledger、delegated specialist adoption、report evidence が grade に応じて揃わない限り、canonical phase promotion / issue readiness を主張できないようにする。
- 成果物:
  - grade 別 report evidence / Spec Authoring Gate guidance。
  - `standard` の specialist 未使用理由、`strict` / `critical` の unavailable / manual fallback evidence contract。
  - delegated draft adoption ledger と stale draft rejection rule。
  - stale reviewer evidence / missing adoption evidence の readiness block と R0 連携。
  - relevant docs / tests。
- Assurance:
  - strict / normal
- closes:
  - E-RQ-022 の review / evidence gate subset
  - E-AC-022 の review / evidence subset
- 依存:
  - `iss-00252 / #252`
  - `iss-00251 / #251`
- 非対象:
  - code-review / PR observation policy の再設計。
  - automatic Lite default 有効化。

### G4 — Add Grade-Aware Issue Authoring Smoke Tests（iss-00255 / #255）

- provisional slug:
  - `add-grade-aware-issue-authoring-smoke-tests`
- 位置づけ:
  - R0 / G1 / G2 / G3 の統合動作を provider-side と dogfooding-side で確認する closure slice。
- 目的:
  - grade-aware Issue authoring workflow が、template materialization、readiness preflight、draft routing、delegated evidence、fresh review / report gate まで end-to-end で崩れていないことを固定する。
- 成果物:
  - Lite に途中 commit / full static analysis 必須が混入しない smoke。
  - Standard / Strict / Critical に M99 static analysis / lint / tests / report / commit gate がある smoke。
  - classified Standard / Strict / Critical Issue の `draft-design` / `draft-plan` profile template routing smoke。
  - missing / invalid / stale `.assurance.json` の draft no-write smoke。
  - readiness false-positive regression smoke。
  - provider / dogfooding docs parity inspection。
- Assurance:
  - strict / normal
- closes:
  - E-AC-006 の readiness regression subset
  - E-AC-022 の end-to-end smoke subset
- 依存:
  - `iss-00251 / #251`
  - `iss-00252 / #252`
  - `iss-00253 / #253`
  - `iss-00254 / #254`
- 非対象:
  - live GitHub repository を必要とする external integration。
  - production telemetry backend。

## Tranche / 依存順

```text
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

Post-I07 corrective:

iss-00247 Profile Markdown templates
  |
  +--> R0 iss-00251 Fail-closed artifact readiness preflight
        |
        +--> G1 iss-00252 Grade-aware issue planning guidance
              |
              +--> G2 iss-00253 Delegated specialist + draft artifact routing
              |
              +--> G3 iss-00254 Spec review + evidence gates
                    |
                    +--> G4 iss-00255 Grade-aware authoring smoke tests
```

## Dependency commands（登録済み）

> この節の dependency edge は登録済み。再実行する場合は duplicate/no-op になることを確認する。
> `iss-00227 -> iss-00226` は decision-only Issue routing correction により削除済み。

```bash
# I02 -> I01
./spec-dock/scripts/spec-dock deps add --from iss-00228 --to iss-00227

# I03 -> I01, I02
./spec-dock/scripts/spec-dock deps add --from iss-00229 --to iss-00227
./spec-dock/scripts/spec-dock deps add --from iss-00229 --to iss-00228

# I04 -> I03
./spec-dock/scripts/spec-dock deps add --from iss-00230 --to iss-00229

# I05 -> I01
./spec-dock/scripts/spec-dock deps add --from iss-00231 --to iss-00227

# I06 -> I04, I05
./spec-dock/scripts/spec-dock deps add --from iss-00232 --to iss-00230
./spec-dock/scripts/spec-dock deps add --from iss-00232 --to iss-00231

# I07 -> I02..I06
./spec-dock/scripts/spec-dock deps add --from iss-00233 --to iss-00228
./spec-dock/scripts/spec-dock deps add --from iss-00233 --to iss-00229
./spec-dock/scripts/spec-dock deps add --from iss-00233 --to iss-00230
./spec-dock/scripts/spec-dock deps add --from iss-00233 --to iss-00231
./spec-dock/scripts/spec-dock deps add --from iss-00233 --to iss-00232

# R0 -> iss-00247
./spec-dock/scripts/spec-dock deps add --from iss-00251 --to iss-00247

# G1 -> R0
./spec-dock/scripts/spec-dock deps add --from iss-00252 --to iss-00251

# G2 -> G1
./spec-dock/scripts/spec-dock deps add --from iss-00253 --to iss-00252

# G3 -> G1, R0
./spec-dock/scripts/spec-dock deps add --from iss-00254 --to iss-00252
./spec-dock/scripts/spec-dock deps add --from iss-00254 --to iss-00251

# G4 -> R0, G1, G2, G3
./spec-dock/scripts/spec-dock deps add --from iss-00255 --to iss-00251
./spec-dock/scripts/spec-dock deps add --from iss-00255 --to iss-00252
./spec-dock/scripts/spec-dock deps add --from iss-00255 --to iss-00253
./spec-dock/scripts/spec-dock deps add --from iss-00255 --to iss-00254
```

## Epic PR 実行モデル（R0 + G1〜G4）

- PR 方針:
  - `iss-00251`〜`iss-00255` は個別 PR を作成しない。
  - 各 Issue は実装、focused validation、issue-local report evidence、必要な commit までを checkpoint とする。
  - GitHub PR は G4 完了後の Epic 最終品質ゲートを通過してから、Epic #224 の corrective tranche 全体として 1 本だけ作成する。
- branch baton:
  - 基本順序は `iss-00251 -> iss-00252 -> iss-00253 -> iss-00254 -> iss-00255` とする。
  - 各 Issue 完了時点の HEAD を次 Issue branch の starting point にする。
  - 次 Issue branch は直前 Issue の commit を含む累積 branch として作成し、差分をバケツリレーで引き継ぐ。
  - 最終 PR head は `iss-00255` 完了後の累積 branch とし、R0〜G4 の全 commit を含める。
- Issue handoff gate:
  - 各 Issue の M99 は「PR 作成」ではなく「次 Issue へ渡せる local closure checkpoint」とする。
  - checkpoint では focused tests、`./spec-dock/scripts/spec-dock validate`、必要な docs / template parity、issue `report.md` の証跡、未実施理由を記録する。
  - 次 Issue の実装を始める前に、直前 Issue の未完了差分・失敗テスト・未記録の検証結果を残さない。
- 最終 PR gate:
  - G4 完了後、下記の Epic 最終品質ゲートを通過してから PR を作成する。
  - PR description には `iss-00251`〜`iss-00255`、Epic requirement / design trace、実行した test / review / QA、未実施理由、残リスクをまとめる。

## 統合チェックポイント

- IC0 Epic Decision Baseline:
  - `20260623t074441z-adr-fixed-skill-kernel-compiled-runbook-authority.md` accepted。
  - `20260623t074443z-adr-adaptive-assurance-lite-authorization-monotonic-escalation.md` accepted。
  - `20260623t074442z-adr-step-assurance-resource-allocation-agent-context-routing.md` accepted。
  - `20260623t074444z-adr-trusted-base-sha-github-review-policy.md` accepted。
  - `20260623t074447z-adr-blocker-centric-pr-risk-closure-rereview.md` accepted。
  - `iss-00226 / #226` は closed / superseded historical evidence であり、implementation readiness dependency ではない。
  - Fresh spec-reviewer pass 後に implementation Issue を downstream planning-ready にする。
- IC1 Core contract:
  - I01 後、classification truth table、legacy detection、schema/versioning を固定する。
  - I02 / I05 が依存できる public application contract を確認する。
- IC2 Workflow entrypoint:
  - I02 後、no-active から requirement capture までを manual first-read smoke する。
  - Skill 本文だけで `./spec-dock/scripts/spec-dock guidance <target>` 起動と stop condition が分かること。
  - Git status が clean であること。
- IC3 Planning compiler:
  - I03 後、Lite / Standard / Strict / Critical fixture を golden 比較する。
  - substantive content no-overwrite を確認する。
  - approved `assurance.json` 後の requirement / design / plan substantive change が stale source binding として block されることを確認する。
- IC4 Execution routing:
  - I04 後、docs-only、runtime、migration、security fixture で routing matrix を確認する。
  - worker context inheritance と reviewer clean-room を区別する。
  - returned evidence refs / missing reason が event に残ることを確認する。
- IC5 Review governance:
  - I05 後、script-local instruction validation、instruction hash / reviewed head SHA binding、missing fallback、invalid fail-closed、multiline trigger、stale head を実 PR または fake GitHub で確認する。
  - I06 後、P0/P1、P2 only、promoted P2、stagnation を確認する。
- IC9 Rollout:
  - I07 後、automatic Lite default が無効のまま、Auto-Lite adoption gates、strict-legacy fallback、required metrics / missing metrics summary、automation-stalled human gate、efficiency baseline を確認する。
  - Epic-wide diff を fresh `deep-consultant`、`spec-reviewer`、code / QA 観点でレビューする。
- IC10 Grade-aware authoring corrective tranche:
  - R0 後、manual test で見つかった F-001〜F-004 が runtime readiness classifier regression として閉じていることを確認する。
  - G1 後、Issue planning guidance が grade-aware authoring rules、Lite non-default、manual escalation / `authorized_profile` separation を返すことを確認する。
  - G2 後、classified Issue の `draft-design` / `draft-plan` が `authorized_profile` の profile template を source とし、missing / invalid / stale `.assurance.json` で no-write fail-closed することを確認する。
  - G3 後、fresh `spec-reviewer`、Evidence Adoption Ledger、delegated specialist evidence、report evidence gate が phase promotion / issue readiness と整合することを確認する。
  - G4 後、Lite / Standard / Strict / Critical の representative smoke tests と provider / dogfooding docs parity を確認する。
- IC99 Epic final PR readiness:
  - R0〜G4 の issue-local report evidence を横断し、E-RQ-006 / E-AC-006 / E-RQ-022 / E-AC-022 の実装証跡が揃っていることを確認する。
  - Epic requirement / design で定義した振る舞いが focused tests / smoke tests / docs parity / manual QA で支えられていることを確認する。
  - Fresh `spec-reviewer`、fresh code review、QA review を通過するまで Epic PR を作成しない。

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
  - script-local instruction source。
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

## Epic 最終品質ゲート（単一 PR 前）

G4 完了後、Epic #224 corrective tranche の最終 PR を作成する前にこの gate を通す。

- requirement / design trace:
  - `E-RQ-006` / `E-AC-006` / `E-RQ-022` / `E-AC-022` の各項目について、どの Issue、どの test、どの report evidence が closure を支えるかを確認する。
  - R0〜G4 の scope / non-scope が崩れ、同じ責務を複数 Issue が重複実装していないことを確認する。
  - `iss-00250` が temporary / superseded evidence のままで、正式 implementation evidence と誤認されていないことを確認する。
- tests:
  - artifact readiness regression: placeholder / heading-only / stale evidence / missing adoption evidence が ready にならないこと。
  - grade-aware guidance regression: Lite / Standard / Strict / Critical の authoring / specialist / review / report evidence rules が guidance に出ること。
  - draft routing regression: Issue `draft-design` / `draft-plan` が `authorized_profile` の profile template source を使い、missing / invalid / stale `.assurance.json` で no-write fail-closed すること。
  - evidence gate regression: fresh `spec-reviewer`、Evidence Adoption Ledger、delegated specialist evidence、report evidence gate が phase promotion / issue readiness と整合すること。
  - smoke / parity: Lite / Standard / Strict / Critical fixture、provider / dogfooding docs・template parity、installer/update 影響を確認すること。
- static analysis / lint / format:
  - repository で設定されている静的解析、lint、format check をローカルで実行する。
  - 実行できない検証は、未実施理由、代替確認、残リスクを Epic / Issue report に記録する。
- local test suite:
  - R0〜G4 の focused tests をすべて実行する。
  - 影響範囲に必要な unit / CLI runtime / integration / regression tests を実行する。
  - 現実的に full `uv run pytest` が必要かを判断し、実行した場合は結果、未実施の場合は理由と代替確認を記録する。
- Spec review:
  - Fresh `spec-reviewer` が Epic requirement / design / plan / report、R0〜G4 の requirement / design / plan / report、最終 diff、test evidence をレビューする。
  - `review_status: pass` になるまで Epic PR を作成しない。
- Code review:
  - Fresh code review が runtime / docs / tests / template changes をレビューする。
  - P0 / P1 / promoted blocker が残る場合は repair / re-review を行い、blocker zero まで PR 作成を保留する。
- QA review:
  - QA 観点で no-active / planning / execution guidance、draft generation、readiness preflight、report evidence、provider / dogfooding parity の代表フローを確認する。
  - QA で見つかった Epic requirement / design 不一致は、修正または明示 defer する。
- PR creation:
  - 上記 gate を pass した後、累積 branch から Epic #224 corrective tranche の単一 PR を作成する。
  - PR 作成後の GitHub Actions / Codex review は、ローカル検証後の最終確認として扱う。基礎的な lint / test failure を初めて発見する場所にしない。

## ロールアウト / ドキュメント影響

- Rollout:
  - automatic Lite default disabled。
  - future Auto-Lite adoption requires accepted ADR、policy version bump、rollout Issue、telemetry gate。
  - selected dogfooding Issues keep strict-legacy fallback when assurance is missing。
  - Lite manual / evidence-gated activation only。
  - automatic Lite default is out of initial rollout。
- Compatibility:
  - Existing Issues are strict-legacy。
  - No automatic canonical artifact rewrite。
- Docs:
  - workflow issue / epic。
  - authoring issue plan。
  - issue discussions / draft authoring source authority。
  - GitHub reference。
  - context routing reference。
  - installer / update ownership。
  - troubleshooting / doctor。
- Review instruction:
  - `.github/codex/review-policy.md` は current authority ではなく historical / bootstrap-only evidence として扱う。
  - `github-pr-observation` script-local instruction asset を current authority とし、`AGENTS.md` から参照しない。
  - script-local instruction ownership、missing fallback、invalid fail-closed を document する。
- Follow-up:
  - Codex Action + structured output migration。
  - Cross-provider review ensemble。
  - Automatic Lite activation tuning。
  - `iss-00250` 一時検討置き場は、この amendment の採用証跡として、`iss-00251`〜`iss-00255` の正式 Issue 証跡へ置換されるまで temporary / superseded evidence として保持する。破棄する場合は、EAL-033 の参照先を正式 Issue evidence に置換してから行う。

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
- Temporary analysis artifacts are not treated as formal Issue IDs unless plan gate and creation command have promoted them.

## 最終完了条件

- E-AC-001〜022 に evidence がある。
- 7 initial implementation Issue と、追加 corrective tranche `R0 + G1〜G4` が完了または明示的に superseded / deferred されている。
- Required ADR が Epic-scope accepted ADR として作成 / 反映され、implementation Issue より先に reviewer-gated baseline になっている。
- New Issue / substantive Issue の strict-legacy compatibility path が dogfooding で成功している。
- Existing Issue の strict-legacy path が壊れていない。
- No-active / planning / execution / PR / finish state が `guidance <target>` stdout authority として動作し、generated projection files は human/debug-only non-canonical output として扱われる。
- Profile / Complexity / Step Assurance が machine-readable。
- Generated state が Git 差分を生まない。
- 変更済み: Valid script-local instruction で deterministic multiline `@codex review` trigger が動作する。missing instruction は plain deterministic fallback、invalid / oversized / unreadable は no PR comment の human gate / fail-closed になる。
- Review completion は explicit Codex artifact で判断し、completion artifact missing by deadline は retryable `timeout` / `wait_or_resume` / `observation_complete=false` とする。
- Auto-Lite readiness report が future automatic Lite default の adoption / rollback 条件を示し、初期 rollout では automatic Lite default が無効のままである。
- Context routing policy、context packet、clean-room reviewer packet、bounded return contract が evidence 付きで動作する。
- Artifact readiness preflight は未解決 placeholder、template-only artifact、heading-only plan、stale reviewer evidence、missing adoption evidence を ready にしない。
- Grade-aware Issue planning guidance は `lite / standard / strict / critical` ごとの authoring、delegated specialist、review、report evidence rules を返し、Lite automatic default を許可しない。
- Issue `draft-design` / `draft-plan` は profile template source authority と fail-closed contract に従って動作する。
- Fresh `spec-reviewer`、Evidence Adoption Ledger、delegated specialist evidence、report evidence gate が grade-aware authoring workflow に整合している。
- P2-only review で repair / re-review loop が開始されない。
- P0 / P1 / promoted blocker が閉じるまで merge-prepared にならない。
- Automation-stalled が risk acceptance にならない。
- Provider / mirror / installer / docs / tests が同期している。
- Efficiency baseline で Lite / Standard / Strict の agent invocation、review generation、workflow cost proxy の差分を確認し、live telemetry 不足は missing metrics summary として残る。
- Epic-wide fresh review と human merge judgment が完了する。

## 依存 / ブロッカー

- D-001:
  - `epic-00158` の first-read skill / docs / template boundary を前提とする。
- D-002:
  - Codex GitHub review の長文 instruction 遵守は hard guarantee ではないため、Blocker Engine を残す。
- D-003:
  - 変更済み: GitHub policy base-SHA fetch capability は不要。script-local instruction source と local file validation が current authority。
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
