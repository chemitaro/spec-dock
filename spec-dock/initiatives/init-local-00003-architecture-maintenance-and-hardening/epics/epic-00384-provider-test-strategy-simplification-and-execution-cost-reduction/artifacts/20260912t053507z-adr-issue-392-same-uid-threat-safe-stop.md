---
種別: ADR（Architecture Decision Record）
ID: "20260912t053507z-adr"
タイトル: "Issue 392: same-UID 脅威下の実装停止"
状態: "superseded"
作成者: "Codex"
最終更新: "2026-09-12"
親: ["epic-00384"]
authority: "accepted"
accepted_authority: "accepted ADR"
accepted_at: "2026-09-12"
accepted_by: "ユーザー承認に基づくCodex"
mirror_eligible: true
superseded_by: "20260912t073840z-adr-issue-392-same-euid-scope-narrowing.md"
superseded_at: "2026-09-12"
derived_from:
  - "../issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/report.md"
reflected_to:
  - "../requirement.md"
  - "../design.md"
  - "../plan.md"
  - "../report.md"
  - "provider-lifecycle-wire-contract.md"
  - "../issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/requirement.md"
  - "../issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/design.md"
  - "../issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/plan.md"
  - "../issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/report.md"
---

# Issue 392: same-UID 脅威下の実装停止

## Status

本ADRは[2026-09-12 Same-EUID Threat Scope Narrowing ADR](20260912t073840z-adr-issue-392-same-euid-scope-narrowing.md)により、同一EUIDの非協調actorを脅威モデルから除外する判断と実装再開条件についてsupersedeされた。以下は当時の脅威モデルに基づく履歴であり、現行の実装停止authorityではない。

## Context

Issue #392は、SpecDockの文書・管理対象ファイルを更新する通常ユーザー権限のCLIです。現行仕様は、同一EUIDの非協調プロセスも脅威に含めたまま、作成者が信頼できるprivate namespaceとConsumer更新境界を要求しています。

2026-09-12のFirst REDでは、作成したdirectoryを最初のpath open前に同一owner・同一modeのdirectoryへ置換すると、現行engineが置換先へConsumer内容を書き込むことを確認しました。既存の`EEXIST` race testは別のscheduleを検証します。詳細は[Issue #392 Report §28](../issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/report.md)を参照してください。

## Decision

1. 同一EUIDの非協調プロセスは脅威モデルに残す。これを暗黙に除外して既存要件を満たしたことにはしない。
2. owner/modeの確認、flock、path再bind、inode witness、atomic renameは協調操作や通常の障害回復には使えるが、同じ資格情報を持つactorに対する作成者provenanceの証明にはならない。現行の通常ユーザー権限CLIには、要求されたtrusted mutation boundaryがない。
3. SpecDockは文書管理の仕組みとして単純・軽量に保つ。#392へprivileged broker、常駐daemon、OS policy subsystem、追加の独自security layerを導入しない。
4. #392のProduct実装を安全停止する。新しい実装回避策、テストのskip/xfail、仕様上の脅威除外は追加しない。B1は未達で、#395/#396は開始しない。
5. 既にある`test_t06_bootstrap_creation_replacement_is_not_populated`のREDと、別scheduleを扱う`test_t06_bootstrap_planned_create_race_does_not_adopt_foreign_directory`は保持する。これは機能削除確認テストではなく、現在のforeign-write故障と別の競合条件を示す既存証拠である。安全停止そのものを確認する新しいProduct testは作らない。
6. 2026-09-08 accepted ADR、Wire v12およびIssue #392の詳細R/D/Pは、実装候補の履歴として保持するが、本ADRと矛盾する実装指示は停止する。既存worktree/candidateをこの決定だけを理由にrevertまたは削除しない。
7. 再開には、Product ownerが脅威条件を明示的に変更するか、同じ脅威条件を保てる単純で実効性のある保護境界を別途承認したうえで、親仕様と実装計画を再承認する必要がある。

## Options

- 採用: 実装停止。現行の簡素なCLI範囲を維持し、未達のsecurity guaranteeを主張しない。
- 不採用: owner/mode、lock、再検査、temporary directoryだけを組み合わせ、作成者provenanceが解決したと扱う。First REDが反証している。
- 不採用: 同一EUID actorを黙ってout-of-scopeにする。明示された脅威条件を変える判断になる。
- 不採用: #392の範囲へ特権serviceやOS固有の強制機構を追加する。文書管理製品に対して複雑さと運用負担が大きく、採用権限もない。

## Consequences

- Issue #392の既存candidateはこの故障条件についてGREENではない。Product、test、packaging、dogfood、CIの新規変更をこの決定では承認しない。
- E384-RQ-006とE384-RQ-019の保護境界は未達のまま残る。参加するSpecDock command同士の協調は、同一EUIDの非協調filesystem actorへの防御を意味しない。
- 14 active regression identity、timing、required-fast、#395/#396の責務、PR human-merge gateは変更しない。
- 仕様のみを更新する。コードレビュー、Final Quality Gate、Product GREEN、Issue finishを通過したとは主張しない。

## References

- [Issue #392 Report §28 — Same-EUID creation replacement first-RED](../issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/report.md)
- [Provider Lifecycle Wire Contract](provider-lifecycle-wire-contract.md)
- [準備と初期レコード公開の失敗契約を閉じる ADR](20260908t011139z-adr-lifecycle-preparation-and-initial-record-failure-contract.md) — 実装候補の履歴として保持
