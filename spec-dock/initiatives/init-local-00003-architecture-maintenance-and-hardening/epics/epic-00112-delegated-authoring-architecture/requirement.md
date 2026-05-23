---
種別: 要件定義書（Epic）
ID: "epic-00112"
タイトル: "Delegated Authoring Architecture for Spec Workflow"
関連GitHub: ["#112"]
状態: "draft"
作成者: "Codex"
最終更新: "2026-05-23"
親: ["init-local-00003"]
---

# epic-00112 Delegated Authoring Architecture for Spec Workflow — 要件定義（WHAT / WHY）

## 目的（Initiative との紐づき）
- Initiative 目標 / 指標:
  - `init-local-00003 Architecture Maintenance and Hardening` の architecture concern として、spec-dock の仕様作成 workflow を、role delegation を含んでも source-of-truth / phase gate / evidence が崩れない構造へ hardening する。
  - provider-side shipped assets と dogfooding consumer workspace の境界を守りながら、agent-native な spec authoring を継続運用できる baseline を作る。
- この epic が提供する能力:
  - `system-architect` が `design.md` の draft evidence を作成できる。
  - `implementation-planner` が `plan.md` の draft evidence を作成できる。
  - Main orchestrator が canonical artifact、user dialogue、integration、phase promotion、report evidence を所有し続ける。
  - delegated draft を `authority` ではなく `auditable draft evidence` として扱う契約を、workflow / phase docs / role skills / report evidence / dogfooding pilot に固定する。

## 背景 / As-Is
- 現行の `workflow_spec_authoring.md` は `requirement -> spec-reviewer pass -> design -> spec-reviewer pass -> plan -> spec-reviewer pass -> downstream handoff` を正本契約としている。
- 現行 delegation consent は reviewer / read-only specialist を前提にしており、spec authoring の design / plan draft を専門 role に委譲する契約は未定義である。
- 現行 issue execution workflow には implementation delegation gate があるが、authoring artifact の ownership、draft lifecycle、report evidence、reviewer criterion へそのまま流用できない。
- リサーチでは、要件定義は main orchestrator + human が所有し、設計 draft は `system-architect`、計画 draft は `implementation-planner` に委譲する方針が妥当と整理された。
- 追加 ChatGPT Pro 分析では、初期 Epic の核心は role 追加そのものではなく、`delegated authoring = authority ではなく auditable draft evidence` と固定することだと整理された。

## ユースケース
- 正常系:
  - Epic / Issue authoring で requirement が fresh `spec-reviewer` pass 済みの場合、main orchestrator は `system-architect` に design draft を依頼し、返却された draft artifact を `discussions/` に保存し、必要部分を canonical `design.md` に統合し、fresh `spec-reviewer` に通す。
  - requirement と design が fresh `spec-reviewer` pass 済みの場合、main orchestrator は `implementation-planner` に plan draft を依頼し、返却された draft artifact を `discussions/` に保存し、必要部分を canonical `plan.md` に統合し、fresh `spec-reviewer` に通す。
  - delegated draft を使わない軽微な authoring では、従来通り main orchestrator が直接 authoring し、通常の fresh `spec-reviewer` gate で promotion する。
- 例外 / 運用シナリオ:
  - `system-architect` が requirement gap を検出した場合、設計で補完せず `Requirement Clarification Request` を返す。
  - `implementation-planner` が design gap を検出した場合、計画で補完せず `Plan Blocked` を返す。
  - delegated draft が source artifact 変更により stale になった場合、reconcile または regenerate されるまで promotion evidence に使わない。
  - role / host adapter が利用できない場合、manual authoring path は継続可能だが、delegated authoring 使用済みとは記録しない。

## Epic 要件
- E-RQ-001 Canonical artifact ownership invariant:
  - Main orchestrator は canonical `requirement.md` / `design.md` / `plan.md`、user dialogue、canonical integration、phase promotion、report evidence を所有し続ける。
  - Delegated author は canonical artifact owner ではなく、draft evidence provider である。
- E-RQ-002 Draft-only delegated authoring mode:
  - 初期導入では delegated authoring role に canonical docs の直接編集、実装コード編集、GitHub issue mutation、destructive command を許可しない。
  - Delegated output は main orchestrator が統合して初めて canonical artifact に反映される。
- E-RQ-003 Delegation consent and scope contract:
  - Delegated authoring invocation は `node + phase + role + artifact` 単位で、scope、source artifacts、allowed actions、forbidden actions、output expectation を記録する。
  - workflow-wide blanket consent は draft-only authoring delegation の根拠にしない。
- E-RQ-004 Delegated design authoring contract:
  - `system-architect` は fresh reviewer-pass 済み `requirement.md` を前提に、design draft を作成できる。
  - Requirement gap は設計判断として補完せず、`Requirement Clarification Request` として返す。
  - Design draft は requirement coverage、context findings、design decisions、alternatives、boundary/contract、dependency analysis、SoR、file/module change plan、migration/compatibility、observability、test strategy、ADR candidates、risks を含む。
- E-RQ-005 Delegated plan authoring contract:
  - `implementation-planner` は fresh reviewer-pass 済み `requirement.md` / `design.md` を前提に、plan draft を作成できる。
  - Design gap は implementation step で補完せず、`Plan Blocked` として返す。
  - Plan draft は requirement/design traceability、milestones、dependency-derived execution order、issue/step slicing、test/review gates、rollback/compatibility、docs impact、final quality gate を含む。
- E-RQ-006 Delegated draft artifact lifecycle:
  - Delegated draft artifact は `requested` / `produced` / `integrated` / `partially_integrated` / `rejected` / `superseded` / `blocked` / `stale` の lifecycle を持つ。
  - `stale` / `rejected` / `superseded` / `blocked` の draft は promotion evidence として扱わない。
- E-RQ-007 Report evidence integration:
  - Delegated authoring を使った場合、`report.md` は role、phase、scope、consent、source artifacts、draft artifact path、status、integration result、rejected portions、blockers、reviewer result、promotion decision を記録する。
- E-RQ-008 Independent spec-reviewer treatment:
  - `spec-reviewer` は delegated draft 自体を pass するのではなく、canonical artifact が delegated draft を安全に統合したかを review する。
  - Delegated draft は fresh reviewer pass の代替にならない。
- E-RQ-009 Provider-first and dogfooding parity:
  - Shipped workflow docs / role skills / host adapter assets は provider-side source of truth から変更し、dogfooding workspace で parity を確認する。
  - Dogfooding pilot は ad hoc local prompt ではなく shipped asset / documented workflow を使う。
- E-RQ-010 Host adapter boundary:
  - `.codex/agents` は初期 Epic に含める。ただし role skill を正本にした thin adapter とし、長文 instruction を重複させない。
  - `.codex/agents` の path / syntax が実装時に確認できない場合でも、初期 Epic の scope は変えず、host adapter issue の成果物を adapter contract と documented uncertainty に縮退する。
  - `.github/agents` / Copilot agent は初期 Epic の非スコープとして確定する。
- E-RQ-011 Failure mode handling:
  - missing consent、missing/stale reviewer pass、requirement gap、design gap、role unavailable、forbidden action attempt、stale draft の扱いを明示する。
- E-RQ-012 Dogfooding pilot and future write-capable readiness:
  - 初期導入後、少なくとも design draft と plan draft を dogfooding し、traceability defect、scope creep、forbidden action、reviewer findings、integration cost、provider/consumer drift を観測する。
  - この Epic の pilot success は write-capable delegation の承認ではなく、draft-only workflow の evidence collection と go/no-go 判断材料の記録で閉じる。
  - Write-capable delegation は pilot 結果に関わらず初期 Epic では明示的に defer し、進める場合は後続 Epic / Issue の承認を必要とする。

## Epic 受け入れ条件
- E-AC-001 Ownership contract:
  - 前提: `workflow_spec_authoring.md` と phase docs が現行 phase gate を保持している。
  - 操作: delegated authoring policy を追加する。
  - 期待結果: Main orchestrator ownership、delegated draft evidence、fresh `spec-reviewer` pass requirement が矛盾なく明記される。
  - 観測点: workflow docs / report evidence / reviewer criteria。
- E-AC-002 Draft-only safety:
  - 前提: `system-architect` / `implementation-planner` role を追加する。
  - 操作: role skill と host adapter を確認する。
  - 期待結果: 両 role が canonical docs / code / GitHub issue / destructive action を変更しないことを明示する。
  - 観測点: role skill docs、host adapter docs、dogfooding invocation record。
- E-AC-003 Delegated draft lifecycle:
  - 前提: delegated draft が生成される。
  - 操作: draft artifact を `discussions/` に保存し、integration result を記録する。
  - 期待結果: draft status と source artifacts が追跡でき、stale / rejected / blocked draft が promotion evidence にならない。
  - 観測点: draft artifact metadata、`report.md` evidence。
- E-AC-004 Delegated design gate:
  - 前提: `requirement.md` が fresh `spec-reviewer` pass 済みである。
  - 操作: `system-architect` を draft-only mode で利用する。
  - 期待結果: Design draft が requirement に traceable で、requirement gap は RCR として返る。
  - 観測点: delegated design draft、canonical `design.md`、reviewer result。
- E-AC-005 Delegated plan gate:
  - 前提: `requirement.md` / `design.md` が fresh `spec-reviewer` pass 済みである。
  - 操作: `implementation-planner` を draft-only mode で利用する。
  - 期待結果: Plan draft が requirement/design に traceable で、design gap は Plan Blocked として返る。
  - 観測点: delegated plan draft、canonical `plan.md`、reviewer result。
- E-AC-006 Reviewer independence:
  - 前提: delegated draft が canonical artifact に統合されている。
  - 操作: fresh `spec-reviewer` が canonical artifact と delegated evidence を review する。
  - 期待結果: reviewer は draft を authority とせず、scope creep / stale draft / untraceable decision / phase gate bypass を fail または incomplete にできる。
  - 観測点: reviewer verdict、report gate。
- E-AC-007 Provider/consumer parity:
  - 前提: provider-side docs / role skills / adapter assets を変更する。
  - 操作: init/update または dogfooding workspace refresh 相当の確認を行う。
  - 期待結果: provider source と dogfooding consumer の意図した差分または parity evidence が残る。
  - 観測点: tests、`spec-dock validate`、`spec-dock sync`、diff evidence。
- E-AC-008 Dogfooding pilot:
  - 前提: role skill / gate / evidence contract が導入済みである。
  - 操作: dogfooding workspace で design draft と plan draft を少なくとも1回ずつ使う。
  - 期待結果: pilot metrics、draft-only workflow の成功 / 失敗 / 制約、write-capable delegation を後続 scope に defer する判断が `report.md` または discussion に残る。
  - 観測点: pilot report、reviewer results、metrics summary、defer decision。
- E-AC-009 Failure mode evidence:
  - 前提: delegated authoring gate / role skill / report evidence contract が導入済みである。
  - 操作: failure mode table または equivalent contract で、missing consent、missing/stale reviewer pass、requirement gap、design gap、role unavailable、forbidden action attempt、stale draft の期待処理を確認する。
  - 期待結果: 各 failure mode について、expected verdict、allowed next action、report evidence path、promotion eligibility が明示される。
  - 観測点: workflow docs、phase gate docs、role skill output contract、report evidence template、reviewer criteria。

## スコープ
- 必須:
  - `workflow_spec_authoring.md` に ownership / consent / draft-only delegation 契約を追加する。
  - delegated draft artifact lifecycle と `discussions/` 保存方針を追加する。
  - `spec-dock-system-architect` / `spec-dock-implementation-planner` role skill assets を provider-first で追加する。
  - `phase_design.md` / `phase_plan.md` / `phase_plan_issue.md` と report evidence に delegated authoring gate を追加する。
  - `.codex/agents` は thin host adapter として初期 Epic に含める。実際の path / schema を確認できない場合は、adapter 実装済みとせず、adapter contract と documented uncertainty を成果物にする。
  - dogfooding pilot と provider/consumer parity verification を行う。
- 禁止:
  - 初期 Epic で delegated author に canonical `requirement.md` / `design.md` / `plan.md` の直接編集を許可すること。
  - 初期 Epic で implementation code editing、GitHub issue close/update、destructive command を delegated authoring role に許可すること。
  - delegated draft を fresh `spec-reviewer` pass の代替として扱うこと。
  - host adapter に role skill と同等の長文 instruction を重複させること。
  - `.github/agents` / Copilot agent support を初期 Epic に含めること。
- 対象外:
  - scoped write-capable delegation の正式導入。
  - role registry / runtime validation / automated staleness detection。
  - `.github/agents` / Copilot agent support。
  - external publishing automation。
  - model selection enforcement。

## 境界
- 常に行う:
  - Previous-phase artifact を delegated author が変更しない前提で設計する。
  - Requirement gap は requirement phase へ戻し、design gap は design phase へ戻す。
  - Draft artifact と canonical artifact を分離する。
  - 長い draft / analysis は `discussions/` に保存し、`report.md` には判断に必要な evidence summary を残す。
- 判断が必要:
  - `.codex/agents` の実 path / schema が確認できない場合、host adapter issue を adapter contract + documented uncertainty として閉じるか、同 issue 内で確認作業を追加するか。
  - Pilot metrics から後続 write-capable delegation Epic を起票する価値があるか。
  - Docs-only / trivial issue で delegated authoring を省略する基準。
- 行わない:
  - Requirement を delegated author に所有させない。
  - `spec-reviewer` と authoring role を兼任させない。
  - Drift しやすい multi-host support を初期 Epic に含めない。

## 非機能要件
- 性能:
  - 初期導入は docs / skills / host adapter の軽量契約に留め、runtime validation を追加しない。
- 信頼性 / 一貫性:
  - Draft lifecycle、report evidence、reviewer criteria により、古い draft や未統合 draft が canonical authority と誤認されない。
  - Provider source と dogfooding consumer workspace の差分を検証可能にする。
- セキュリティ:
  - Delegated authoring role に credentialed access、external publishing、destructive command、GitHub mutation を許可しない。
- 運用:
  - Role unavailable の場合も manual authoring path は維持する。
  - Dogfooding pilot は write-capable delegation の go/no-go 判断材料を残す。

## 依存 / 影響範囲
- 影響する component:
  - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_design.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
  - `src/spec_dock/assets/install_root/.agents/skills/`
  - `src/spec_dock/assets/install_root/.codex/`
  - `spec-dock/` dogfooding workspace
  - `tests/test_init_update.py` and related scaffold parity tests
- 外部依存:
  - Codex host adapter の `.codex/agents` path / syntax。
  - `spec-reviewer` role availability。
- 互換性:
  - Existing manual authoring workflow は維持する。
  - Existing reviewer / read-only specialist consent contract を壊さず、draft-only authoring delegation を additive に導入する。

## 未確定事項
- なし:
  - `.codex/agents` は thin adapter として初期 Epic に含める。path / schema が確認できない場合も scope は変えず、adapter contract + documented uncertainty として扱う。
  - `.github/agents` / Copilot agent support は初期 Epic の非スコープとして確定する。
  - Dogfooding pilot は write-capable delegation の承認ではなく、draft-only workflow の evidence collection と後続判断材料の記録で閉じる。
