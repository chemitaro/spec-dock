---
種別: 要件定義書（Epic）
ID: "epic-00112"
タイトル: "Delegated Authoring Architecture for Spec Workflow"
関連GitHub: ["#112"]
状態: "approved"
作成者: "Codex"
最終更新: "2026-05-23"
親: ["init-local-00003"]
---

# epic-00112 Delegated Authoring Architecture for Spec Workflow — 要件定義（WHAT / WHY）

## 改訂方針

この改訂は、既に実装・完了済みの `iss-00113`..`iss-00118` を書き換えない。これらは「draft-only evidence workflow」の v0 実装として保持する。

本 Epic は、ここまでの追加調査を踏まえて、次の v1 目標状態へ拡張する。

- `system-architect` は actual `design.md` を `status: draft` / `authority: proposed` として作成・更新できる。
- `implementation-planner` は actual `plan.md` を `status: draft` / `authority: proposed` として作成・更新できる。
- main orchestrator は final ownership、approval、promotion、user dialogue、requirement ownership、phase completion を保持する。
- 子 specialist は bounded depth=2 で evidence / report を作成できるが、canonical artifact を編集できない。
- `status: draft` だけを安全境界にせず、`authority`、`grants`、approved revision、promotion record、authority-aware context-pack / lifecycle gate で downstream 誤用を防ぐ。

## 目的（Initiative との紐づき）

- Initiative 目標 / 指標:
  - `init-local-00003 Architecture Maintenance and Hardening` の architecture concern として、spec-dock の仕様作成 workflow を、role delegation を含んでも source-of-truth / authority / phase gate / evidence が崩れない構造へ hardening する。
  - provider-side shipped assets と dogfooding consumer workspace の境界を守りながら、agent-native な spec authoring を継続運用できる baseline を作る。
- この Epic が提供する能力:
  - 専門 author が actual `design.md` / `plan.md` の draft を作成することで、main orchestrator と人間ユーザーの認知負荷を下げる。
  - canonical path に置かれた未承認 draft が実装根拠や完了根拠として誤用されない authority model を提供する。
  - 子 specialist による調査・分析・preflight review を evidence pipeline として扱い、採用 / 棄却 / 保留を audit 可能にする。
  - v0 の draft-only evidence workflow の上に、write-scoped draft authoring と authority-aware gate を追加する。

## 背景 / As-Is

- 現行の `workflow_spec_authoring.md` は `requirement -> spec-reviewer pass -> design -> spec-reviewer pass -> plan -> spec-reviewer pass -> downstream handoff` を正本契約としている。
- 現行 Epic 実装では、delegated authoring は `discussions/` に残る draft evidence として導入済みである。
- 追加調査では、`system-architect` / `implementation-planner` が助言だけを返すなら consultant と役割差が薄く、専門 authoring による認知負荷削減と品質向上が十分に得られないと整理された。
- 一方、actual `design.md` / `plan.md` を直接編集可能にすると、canonical path 自体が source-of-truth signal になるため、`status: draft` だけでは未承認 artifact の誤用を防げない。
- Deep Consultant と ChatGPT 5.5 Pro の追加分析は、`status` と `authority` と `grants` を分離し、implementation / issue ready / issue finish / phase completion が `authority: approved` の artifact だけを参照する設計を推奨した。

## ユースケース

- 正常系:
  - Epic / Issue authoring で requirement が `authority: approved` かつ approved revision 記録済みの場合、main orchestrator は `system-architect` に actual `design.md` の draft 更新を委譲する。
  - `system-architect` は `design.md` を `status: draft` / `authority: proposed` として更新し、参照した evidence と採用判断を記録する。
  - requirement と design が `authority: approved` かつ approved revision 記録済みの場合、main orchestrator は `implementation-planner` に actual `plan.md` の draft 更新を委譲する。
  - `implementation-planner` は `plan.md` を `status: draft` / `authority: proposed` として更新し、承認済み design revision への依存を記録する。
  - main orchestrator は draft を確認し、必要な修正と final review を行い、fresh `spec-reviewer` pass と promotion record をもって `authority: approved` へ昇格する。
  - review / planning context では proposed artifact を非権威として参照できるが、implementation / issue ready / issue finish / phase completion context では approved artifact だけを参照する。
- specialist 活用:
  - `system-architect` / `implementation-planner` は必要に応じて `repo-analyst`、`researcher`、`consultant`、`deep-consultant`、advisory `spec-reviewer` を呼び、evidence / report を収集する。
  - 子 specialist の output は `discussions/` または evidence path に保存し、親 authoring agent が evidence adoption ledger で採用 / 部分採用 / 棄却 / 保留を明示する。
- 例外 / 運用シナリオ:
  - `system-architect` が requirement gap を検出した場合、設計で補完せず Requirement Clarification Request を返し、requirement phase へ戻す。
  - `implementation-planner` が design gap を検出した場合、計画で補完せず Plan Blocked を返し、design phase へ戻す。
  - artifact が `authority: proposed` のままなら、実装開始、issue ready、issue finish、phase completion は block される。
  - Permission Profile や host behavior が期待どおり enforce できない場合、write-scoped draft authoring は解禁せず、v0 の discussions/proposal path に戻す。

## Epic 要件

- E-RQ-001 Main ownership invariant:
  - Main orchestrator は canonical `requirement.md` / final approval / phase promotion / user dialogue / report evidence を所有し続ける。
  - `requirement.md` は専門 author へ委譲しない。
- E-RQ-002 Draft canonical authoring:
  - `system-architect` は actual `design.md` の draft author になれる。
  - `implementation-planner` は actual `plan.md` の draft author になれる。
  - 両者が作成・更新できる artifact は `status: draft` / `authority: proposed` の範囲に限る。
- E-RQ-003 Authority separation:
  - `status` は lifecycle state、`authority` は downstream decision force、`grants` は許可された downstream action として分離する。
  - normative grants key set は `review_input`、`planning_input`、`design_baseline`、`implementation_start`、`issue_ready`、`issue_finish`、`phase_completion` とする。
  - `status: draft` / `authority: proposed` は review input / planning input にはできるが、implementation baseline / issue ready / issue finish / phase completion にはできない。
  - implementation / issue ready / issue finish / phase completion は `authority: approved` だけでなく、該当する `grants.*: true` も必須にする。
- E-RQ-004 Promotion gate:
  - `authority: approved` への昇格は main orchestrator の promotion と fresh final `spec-reviewer` pass を必須にする。
  - promotion は approved revision / artifact hash / approver / timestamp / promotion record を残す。
- E-RQ-005 Authority-aware context-pack and lifecycle:
  - context-pack は purpose-aware に proposed と approved を分離する。
  - implementation / issue ready / issue finish / phase completion purpose では `authority: approved` の `design.md` / `plan.md` だけを authoritative input にする。
- E-RQ-006 Evidence adoption ledger:
  - 子 specialist や外部分析の output は evidence adoption ledger を経由して draft artifact へ反映する。
  - ledger は source、contributor role、claim、disposition、target artifact / section、rationale、evidence strength、adopter、reviewer、blocking を持つ。
  - 採用だけでなく、部分採用、棄却、保留、置換を記録する。
- E-RQ-007 Bounded depth=2 delegation:
  - `system-architect` / `implementation-planner` は depth=2 で child specialist を呼べる。
  - child specialist は leaf-only evidence producer とし、canonical artifact edit、promotion、final review authority を持たない。
  - depth=3、implementation agent の authoring child 化、peer authoring role の child 化は禁止する。
- E-RQ-008 Permission and path boundary:
  - 将来の write-scoped delegation は Permission Profile などの path-level guard を使い、role ごとに許可 artifact と evidence path を分ける。
  - `system-architect` は design draft と evidence ledger 以外を編集しない。
  - `implementation-planner` は plan draft と evidence ledger 以外を編集しない。`design.md` は本文・metadata・approval fields を含めて read-only とする。
  - Permission Profile が host / platform 上で検証できない場合は、write-capable draft authoring を有効化しない。
  - Write-scoped delegation invocation は、resolved canonical target、input revision/hash、allowed write paths、forbidden paths、probe result、fallback を持つ task manifest を必須にする。
- E-RQ-009 Reviewer independence:
  - authoring agent が呼ぶ `spec-reviewer` は advisory preflight に限定する。
  - final `spec-reviewer` は main orchestrator が起動する blocking gate として独立させる。
- E-RQ-010 Provider-first and dogfooding parity:
  - Shipped workflow docs / role skills / host adapter assets / runtime gates は provider-side source of truth から変更し、dogfooding workspace で parity を確認する。
- E-RQ-011 Backward-compatible amendment:
  - 既存の `iss-00113`..`iss-00118` は v0 実装として保持し、書き換えない。
  - v1 への移行は追加 issue による amendment として積み上げる。
- E-RQ-012 Failure mode handling:
  - missing authority metadata、invalid state combination、missing ledger、unapproved dependency revision、Permission Profile enforcement failure、child artifact edit attempt、depth violation、stale proposed artifact を block / fail / fallback として扱う。

## Epic 受け入れ条件

- E-AC-001 Authority metadata:
  - 前提: `design.md` / `plan.md` を delegated draft author が更新する。
  - 操作: artifact metadata を確認する。
  - 期待結果: `status`、`authority`、`grants`、`owner_role`、`draft_author_role`、`approval`、source revision が記録される。
- E-AC-002 Proposed is not implementation authority:
  - 前提: artifact が `authority: proposed` である。
  - 操作: implementation / issue ready / issue finish / phase completion context を生成または検証する。
  - 期待結果: proposed artifact は authoritative input にならず、approved artifact がない場合は block / incomplete になる。
- E-AC-003 Draft canonical authoring:
  - 前提: requirement が承認済みである。
  - 操作: `system-architect` が `design.md` draft を更新する。
  - 期待結果: `design.md` は `authority: proposed` のまま更新され、promotion は行われない。
- E-AC-004 Delegated plan authoring:
  - 前提: requirement / design が承認済みである。
  - 操作: `implementation-planner` が `plan.md` draft を更新する。
  - 期待結果: `plan.md` は approved design revision を参照し、`authority: proposed` のまま更新され、promotion は行われない。
- E-AC-005 Promotion integrity:
  - 前提: proposed artifact が final review ready である。
  - 操作: main orchestrator が final `spec-reviewer` pass 後に promotion する。
  - 期待結果: `authority: approved`、downstream 用 `grants.*: true`、approved revision、promotion record が記録される。
- E-AC-006 Evidence adoption traceability:
  - 前提: child specialist output が存在する。
  - 操作: draft artifact と ledger を確認する。
  - 期待結果: 各 evidence の disposition と反映先 / 棄却理由が追跡できる。
- E-AC-007 Bounded depth=2:
  - 前提: authoring agent が specialist を使う。
  - 操作: delegation graph と output path を確認する。
  - 期待結果: child は leaf-only evidence producer であり、canonical artifact edit / promotion / final review を行わない。
- E-AC-008 Permission profile readiness:
  - 前提: Codex CLI / Desktop の Permission Profile で role-specific write scope を設定する。
  - 操作: 許可 path と禁止 path の write probe を実行または documented fallback を確認する。
  - 期待結果: task manifest の resolved path allowlist に含まれる artifact / evidence path だけが書き込み可能であり、失敗時は write-scoped draft authoring を無効化する。
- E-AC-009 Reviewer independence:
  - 前提: preflight review が行われている。
  - 操作: final review evidence を確認する。
  - 期待結果: preflight pass は final pass の代替にならず、main orchestrator 起動の fresh final reviewer が blocking verdict を返す。
- E-AC-010 Backward-compatible rollout:
  - 前提: `iss-00113`..`iss-00118` が完了済みである。
  - 操作: v1 amendment issue plan を確認する。
  - 期待結果: 完了済み issue の計画・報告を改ざんせず、追加 issue が v1 requirements を閉じる。
- E-AC-011 Provider-first rollout closure:
  - 前提: v1 amendment issue plan を作成する。
  - 操作: 各追加 issue の provider source、dogfooding validation surface、test surface、rollback / fallback を確認する。
  - 期待結果: workflow docs、role skills、host adapter assets、runtime gates、templates / report scaffolds の変更が provider-side source of truth から計画され、dogfooding workspace は validation / parity surface として扱われる。
- E-AC-012 Requirement authority prerequisite:
  - 前提: `system-architect` または `implementation-planner` へ actual draft canonical authoring を委譲する。
  - 操作: requirement authority source と approved revision を確認する。
  - 期待結果: requirement approval は `report.md` の Spec Authoring Gate requirement promotion entry、または v0/v1 移行中の fresh reviewer pass + main promotion evidence から検証でき、hash / revision mismatch がある場合は canonical draft write が block される。

## スコープ

- 必須:
  - artifact frontmatter / metadata に `status`、`authority`、`grants`、`approval`、source revision を導入する。
  - authority-aware context-pack / lifecycle gate を設計・実装する。
  - evidence adoption ledger を導入する。
  - `system-architect` / `implementation-planner` を draft canonical author として再定義する。
  - bounded depth=2 specialist delegation の許可 graph / cap / output path を定義する。
  - Permission Profile による role-specific write scope を検証し、失敗時の fallback を定義する。
  - final reviewer / preflight reviewer の責務分離を明文化する。
  - v0 完了済み issue の後に v1 amendment issue を追加する。
- 禁止:
  - `status: draft` だけで safety を主張すること。
  - `authority: proposed` の artifact を implementation baseline / issue ready / issue finish / phase completion に使うこと。
  - child specialist に canonical artifact edit / promotion / final review authority を与えること。
  - Permission Profile 未検証のまま write-scoped draft authoring を本番運用すること。
  - 既に完了した `iss-00113`..`iss-00118` の計画・報告を v1 に合わせて改ざんすること。
- 対象外:
  - `.github/agents` / Copilot agent support。
  - external publishing automation。
  - model selection enforcement。
  - OS sandbox だけを信頼した security boundary の保証。
  - depth=3 以上の multi-agent hierarchy。

## 境界

- 常に行う:
  - Requirement は main orchestrator / human owned として扱う。
  - Draft canonical artifact と approved authority を分離する。
  - Proposed artifact を downstream に渡すときは非権威として明示する。
  - Specialist output は evidence adoption ledger で採否を記録する。
  - Manual authoring path は維持する。
- 判断が必要:
  - Permission Profile が Desktop App で期待どおり enforce できない場合、CLI 限定運用にするか v0 fallback を使うか。
  - 単一ファイル write と専用ディレクトリ write のどちらを採用するか。
  - Proposed artifact を canonical path に置く前に、authority-aware tooling gate をどこまで必須にするか。
- 行わない:
  - Requirement ownership を専門 author へ移さない。
  - Final approval を専門 author や child reviewer へ移さない。
  - v0 issue の observed evidence を後から書き換えない。

## 非機能要件

- 信頼性 / 一貫性:
  - 未承認 draft が canonical path にあっても、implementation / issue ready / issue finish / phase completion の根拠にならない。
  - Approved revision と promotion record により、後続 agent がどの版を根拠にしたか追跡できる。
- セキュリティ:
  - Role-specific write scope は instruction だけに依存せず、Permission Profile / diff gate / lifecycle validation で補強する。
  - `.env*`、credential、GitHub mutation、destructive command は delegated authoring role の非許可対象とする。
- 運用:
  - Permission Profile または host adapter が不安定な場合は、write-scoped draft authoring を無効化し、manual / discussions proposal path へ戻せる。
  - depth=2 は常時起動ではなく、複雑度・不確実性・影響範囲に応じて使う。

## 依存 / 影響範囲

- 影響する component:
  - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_design.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_epic.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/` の context-pack / lifecycle / validation surfaces
  - `src/spec_dock/assets/install_root/.agents/skills/`
  - `src/spec_dock/assets/install_root/.codex/agents/`
  - provider / dogfooding report templates
  - `tests/`
- 外部依存:
  - Codex CLI / Desktop の Permission Profile 挙動。
  - `spec-reviewer` role availability。
- 互換性:
  - v0 draft-only evidence workflow は backward-compatible fallback として維持する。
  - Existing manual authoring workflow は維持する。

## 未確定事項

- なし:
  - この改訂では、draft canonical authoring を最終目標として採用する。
  - ただし、authority-aware gate と Permission Profile 検証が揃うまで write-scoped draft authoring を運用解禁しない。
  - 既存完了 issue は変更せず、追加 amendment issue で v1 へ進める。
