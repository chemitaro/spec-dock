---
種別: ADR（Architecture Decision Record）
ID: "20260913t144152z-adr"
タイトル: "Issue #392 provisional merge and deferred B1 acceptance"
状態: "accepted"
決定日: "2026-09-13"
作成者: "iwasawayuuta"
最終更新: "2026-09-13"
親: ["epic-00384"]
authority: "accepted"
accepted_authority: "accepted ADR"
accepted_at: "2026-09-13"
accepted_by: "user"
mirror_eligible: true
derived_from: []
reflected_to:
  - "../requirement.md"
  - "../design.md"
  - "../plan.md"
  - "epic-integration-branch-contract.md"
  - "rolling-wave-issue-elaboration-contract.md"
  - "active-failure-disposition-register.md"
  - "../issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/requirement.md"
  - "../issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/design.md"
  - "../issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/plan.md"
  - "../issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/artifacts/20260908t011846z-luna-max-implementation-handoff.md"
  - "../issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/artifacts/20260908t011846z-01-lifecycle-test-ownership-and-migration.md"
  - "../issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/requirement.md"
  - "../issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/design.md"
  - "../issues/iss-00395-regression-baseline-terminalization-and-product-defect-repair/plan.md"
---

# 20260913t144152z-adr Issue #392 provisional merge and deferred B1 acceptance

## Context

- Epicは各Issue merge後のGREENを要求しているが、#392は#395が所有する14件の既知baseline不整合を変更せず保持する。現行候補ではfull verifierが`ledger-mismatch` 10件を報告しており、#392中にこれらを修正・抑止することは責務境界違反となる。
- ユーザーは#392のcandidateを先に人間がEpic branchへmergeし、そのexact tipを#395のread-only lifecycle inputとしてbaseline修復を行い、修復後にB1/B2を判定する順序を承認した。
- B1のfull-current-gate GREENを#392 merge直後にも要求すると、#395を開始する前提と循環する。受入順を変えずに、この中間状態と唯一の例外を明確にする必要がある。

## Decision

- Issue実装・human mergeの順序は#392 → #395 → #396のまま維持する。#392のmergeは暫定統合状態`P392`であり、GREEN受入状態B1とは呼ばない。
- #392 PRは、#392所有のfocused/platform/package/dogfood/ordinary CIと全required checksがGREENで、15/14/1 baseline、243 timing、required-fast、policyが不変の場合に限りhuman mergeできる。current full verifierはmerge前にexact candidateで実行し、そのviolationがすべてregister §6.1の#395所有active rowに対応すると確認できる場合だけP392へ進める。unexpected failure、#392所有行の差分、証拠不一致、required check failureが一つでもあればmergeを停止する。
- P392では、full verifierの結果、exact SHA、各violationと#395 register rowの対応を記録する。ledger、test identity/signature、policy、skip/xfailを変更してこの状態をGREENに見せない。P392は#392の完了・closure、B1、#396開始を意味しない。
- #395は、#392が人間によりEpic branchへmergeされたP392のexact tipからだけ開始する。#392のIssue closureを#395開始条件にせず、#395の要件・計画でmerge SHAと許容される#395-owned failure集合を再確認する。実装開始前のR/D/P詳細化と独立Strict reviewは引き続き必須とする。
- #395 merge後の同一exact tipでB1（#392 lifecycle/integration契約と現行required/full gatesがGREEN）を先に、B2（15 rows、active 0、resolved 15、approved 0、unexpected 0）を続けて判定する。B1/B2はいずれもその同じtipを証拠にする。#392はB1成立後、#395はB2成立後にだけ完了・closureでき、#396はB2後にだけ開始できる。
- #395のSpecDock metadataから#392へのclose-based dependency edgeだけを削除し、上記P392 exact-tip entry gateで順序を強制する。#396から#395へのdependency、Issue IDs、human merge順、rollback単位は維持する。
- P392以外に非GREENを許す例外はない。必要なPR review、人間だけのmerge/revert、mainへの単一Epic merge、Issue数およびproduction責務境界は変更しない。

## Options

- #392 merge前に#395の修復を取り込む: PR/branch統合順を崩し、未受入の#392 lifecycleを別作業へ混ぜるため採用しない。
- #392をB1 GREEN扱いにする、またはknown failureをsuppressする: full verifier結果とbaselineを偽るため採用しない。
- #392をP392として一度mergeし、#395で修復後にB1/B2を同一tipで評価する: Issue所有、human merge、受入順を保ったまま循環を解消するため採用する。

## Consequences

- Integration pathはB0 → P392 → #395 → B1/B2（同一tip） → #396 → B3の一方向となる。P392は記録された#395-owned mismatchだけを含む限定的な中間状態で、一般的なGREEN waiverではない。
- #392 closureは#395の統合後まで遅れる。#395のmetadata readiness表示はP392 mergeの代替証拠にならないため、正式start時にexact upstream tipを確認する。
- P392で許容集合外のfailureが見つかる、または#395 merge後にB1/B2のいずれかが失敗する場合は次Issueを開始せず、humanがwhole-merge回復を判断する。

## References

- 根拠: ユーザーが承認した#392 provisional merge → #395修復 → 同一tipのB1/B2評価。
- 反映先: Epic Requirement/Design/Plan、Integration Branch Contract、Rolling-Wave Contract、Baseline Register、#392と#395のR/D/Pおよび#392 handoff/test artifact。
