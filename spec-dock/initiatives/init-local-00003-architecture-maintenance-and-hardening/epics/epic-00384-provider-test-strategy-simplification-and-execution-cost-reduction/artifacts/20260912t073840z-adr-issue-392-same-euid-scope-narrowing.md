---
種別: ADR（Architecture Decision Record）
ID: "20260912t073840z-adr"
タイトル: "Issue 392 Same-EUID Threat Scope Narrowing"
状態: "accepted"
決定日: "2026-09-12"
作成者: "iwasawayuuta"
最終更新: "2026-09-12"
親: ["epic-00384"]
authority: "accepted"
accepted_authority: "accepted ADR"
accepted_at: "2026-09-12"
accepted_by: "user"
mirror_eligible: true
derived_from:
  - "20260912t053507z-adr-issue-392-same-uid-threat-safe-stop.md"
supersedes: "20260912t053507z-adr-issue-392-same-uid-threat-safe-stop.md"
reflected_to:
  - "../requirement.md"
  - "../design.md"
  - "../plan.md"
  - "../report.md"
  - "../artifacts/provider-lifecycle-wire-contract.md"
  - "../issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/requirement.md"
  - "../issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/design.md"
  - "../issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/plan.md"
  - "../issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/report.md"
---

# 20260912t073840z-adr Issue 392 Same-EUID Threat Scope Narrowing

本ADRはユーザーが選択したOption 1を記録するaccepted authorityです。前ADRはその時点の脅威モデルに対して妥当な安全停止記録として保持し、本ADRが脅威範囲と再開条件だけを置き換えます。

## Context

- 2026-09-12 accepted safe-stop ADRは、同一EUIDの非協調filesystem actorを脅威に残す判断を前提としていた。その前提では通常ユーザー権限CLIが作成者provenanceを保証できないため、実装停止が必要だった。
- ユーザーはOption 1を明示的に選択し、同一EUIDの非協調actorを保証対象から外して、複雑な特権broker、常駐daemon、OS policy subsystemを追加しない軽量なCLI設計を採用した。
- 親Wire WIR-COORD-003は、参加するSpecDock command間のlease協調と、任意のmanual Git/filesystem edit・external writer・nonparticipating commandを既に区別している。Issue詳細化をこの契約へ整合させる。

## Decision

1. 同一EUIDを共有する非協調processによる意図的なfilesystem/Git変更、実行中processへの介入、またはpath replacementは脅威モデル外とする。owner/mode、lock、inode witness、descriptor-relative operation、atomic renameはそのactorに対するsecurity boundaryまたはcreator-provenance証明とは主張しない。
2. サポート対象の同時実行は、repository-root leaseおよび定義済みworktree leaseを守るSpecDock commandに限定する。shared/exclusive admission、helper lifetime、crash後のwire-defined recoveryは維持する。
3. 通常のI/O error、process interruption、durability/fault recovery、symlink/special-type rejection、protected-data preservationおよびOS permission errorは現行Wireの範囲で維持する。これは悪意ある同一EUID actorに対する耐性を意味しない。
4. 異なるcredentialを持つprocessについて、OSが書込み権限を拒む状況を前提とする。ACL、権限昇格、共有可能な書込み権限などにより対象を書き換えられるactorに対する保証は本Issueで追加しない。
5. 前safe-stop ADRは履歴として保持する。本ADRが同ADRの脅威範囲および実装停止判断をsupersedeする。他のaccepted Wire、Issue ownership、baseline、human merge gateは変更しない。
6. 同一EUID actorからのcreator-provenanceを保証するための特権service、daemon、OS固有policy、追加独自security layerは導入しない。
7. Product/test変更は、親とIssueのRequirement/Design/Planが本決定と既存Wireへ整合し、Plan G0の独立review・clean pushed freeze/projectionを完了するまで行わない。既存candidateではCP1–CP4は実施済みだが未受入であるため、G0後はIssue Plan §2.1の再開位置から続け、完了済みcheckpointを理由なくやり直さない。

## Options

- 採用: 同一EUIDの非協調actorを保証対象外にし、通常OS権限とSpecDockの協調leaseを境界として、現行の軽量CLIを継続する。
- 不採用: 同一EUID actorを脅威に残し、特権broker、常駐daemon、OS policy等を追加する。文書管理CLIに対して複雑さと運用負担が大きい。
- 不採用: threat modelを文書へ書かず、owner/mode/lock/path rebindだけでcreator provenanceを証明したと扱う。First REDが反証している。

## Consequences

- `test_t06_bootstrap_creation_replacement_is_not_populated`が表す同一EUIDの非協調actor guaranteeは削除対象となり、Product test suiteから撤去する。単にout-of-scopeであることをassertする後継testは作らない。
- 同じraceだけを根拠にしたReport上のfailure判定はhistorical evidenceとして残すが、現行acceptance criterionではない。既存testのKEEP/REMOVE判断はPlanで根拠を付け、協調競合・通常I/O failure・crash recoveryの証拠を維持する。
- E384-RQ-006のoperation/crash/data-preservation責務とE384-RQ-019のSpecDock runtime/lifecycle coordinationは維持する。Wire v12 inventory/goldenの追加・変更は本ADRだけでは承認しない。
- 親およびIssueの仕様更新、独立内容review、clean pushed freeze/projection後に実装を再開する。実装、Product GREEN、Code Review、Final Quality Gate、Issue finishはそれぞれ後続証拠で判定する。

## References

- [2026-09-12 safe-stop ADR（superseded）](20260912t053507z-adr-issue-392-same-uid-threat-safe-stop.md)
- [Provider Lifecycle Wire Contract §16 WIR-COORD-003](provider-lifecycle-wire-contract.md)
- [Issue #392 Report §28–29](../issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/report.md)
