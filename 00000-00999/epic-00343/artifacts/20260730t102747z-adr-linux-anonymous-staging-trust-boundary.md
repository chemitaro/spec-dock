---
種別: ADR（Architecture Decision Record）
ID: "20260730t102747z-adr"
タイトル: "Linux generic import anonymous staging trust boundary"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-07-30"
親: ["epic-00343"]
authority: "accepted"
mirror_eligible: true
scope_id: epic-00343
source_paths:
  - "epic-00343/requirement.md"
  - "epic-00343/design.md"
  - "epic-00343/plan.md"
  - "epic-00343/issues/iss-00345-generic-single-file-artifact-import/report.md"
  - "epic-00343/artifacts/20260730t085831z-adr-macos-generic-import-staging-cleanup-trust-boundary.md"
intended_targets:
  - "epic-00343/requirement.md"
  - "epic-00343/design.md"
  - "epic-00343/plan.md"
adoption_status: adopted
derived_from:
  - "iss-00345 fresh code review finding: Linux named staging cleanup race"
reflected_to:
  - "epic-00343/requirement.md"
  - "epic-00343/design.md"
  - "epic-00343/plan.md"
diff_guard_result: pass
---

# 20260730t102747z-adr Linux generic import anonymous staging trust boundary

> 本ADRは、2026-07-30にユーザーが採用したOption AをEpic-level authorityとして固定する。Linuxのnamed staging cleanupにsame-UID waiverを導入せず、anonymous stagingを使用できないenvironmentではformal destination作成前にfail closedする。

## 1. Context and Requirement Coverage

`iss-00345`のfresh code reviewは、Linuxのdestination directory内に名前を持つstaging entryを作る実装では、最終identity確認後から`unlink`までにsame-UID actorがそのpathnameを置換できることを確認した。macOSについてはaccepted ADR `20260730t085831z-adr`が、その限定windowを明示した例外として受容している。しかし、そのADRはmacOS専用であり、Linuxへ拡張してはならない。

対象はEpic `E-RQ-013`, `E-RQ-017`, `E-AC-015`, `D-005`, `D-008`、Candidate 2 / 3のplatform capability、rollback、fresh review gateである。filename、privacy、source non-mutation、formal destination no-replace、macOS accepted ADRの契約は変更しない。

## 2. Decision

**Linuxでは`O_TMPFILE`によるanonymous stagingを必須とする。** source bytesをdestination filesystem上のanonymous inodeへstreamし、検証済みのheld staging FDを、現行のFD-bound no-replace publication primitiveへ渡す。formal nameへの`/proc/self/fd/<fd>` + `linkat(..., AT_SYMLINK_FOLLOW)` publicationを許すため、`O_EXCL`を伴わないlinkable anonymous inodeを使う。stagingにcleanup対象となるpathnameを作らないため、pre-commit abort/failureはFDをcloseするだけであり、pathname `unlink`を行わない。

filesystem、kernel、`/proc/self/fd`、またはdestination directory durabilityが利用できない場合は、formal destinationを作る前にcontent-freeな`publication_unsupported` / `not_committed` / `safe_after_remediation`でfail closedする。unsupportedを個別errnoへ公開契約化しない。preflightは`O_TMPFILE`作成、FD regularity、procfs reference、directory durabilityのnon-mutating確認だけを行う。`linkat`固有のcapability / policy failureはpreflightで推測・拒否せず、formal candidateへの最初のactual commitでのみ検出し、formal entryが未作成なら安定したpublic codeへ正規化する。original sourceはdestinationと別filesystemでもよく、destination-side anonymous stagingによりcross-filesystem source successを維持する。

この結果、Linuxのsupported filesystem laneは、anonymous stagingとheld-FD publicationを通常権限で満たすenvironmentへ縮小する。OS名だけではsupportを主張しない。

## 3. Contract Boundary

| Stage | Linux contract |
|---|---|
| preflight | visible probe pathnameを一切作らず、linkable `O_TMPFILE` anonymous inodeの作成、FD regularity、`/proc/self/fd/<fd>` reference availability、directory durability primitiveだけをnon-mutatingに確認する。anonymous FDをprobe nameへlinkして削除しない |
| staging | destination filesystem上のanonymous inodeだけを使い、visible staging pathnameを作らない |
| commit | verified held FDとopened destination-parent FDをcurrent FD-bound no-replace publicationへ渡す。formal candidateへのこのcommit syscallが最初のlinkability確認である。`EEXIST`はexisting destination collisionとして既存allocation retryへ委ね、formal entry未作成のcapability / policy failureは`publication_unsupported` / `not_committed`へ正規化する |
| pre-commit abort/failure | formal destinationなし。staging FDをcloseするだけでpathname cleanupをしない |
| capability不足 | `publication_unsupported`, `not_committed`, `safe_after_remediation`。formal destinationなし |
| post-commit | formal destinationのcommit/durability stateを既存contractで返す。anonymous stagingにpathname cleanup warningを持ち込まない |

Linuxに「最終check後のsame-UID replacementを保証対象外とする」例外はない。macOSのnamed-staging final-window exclusionは、`20260730t085831z-adr-macos-generic-import-staging-cleanup-trust-boundary.md`だけに留める。

## 4. Alternatives Considered

### A. anonymous staging capabilityを必須にし、不足時はfail closedする

- 利点: Linux same-UID cleanup waiverなしで、対応filesystemではcross-filesystem source successを保つ。変更範囲はgeneric publisherとcapability/test matrixに限定できる。
- 欠点: supported Linux filesystem laneが縮小する。
- 状態: **accepted**。ユーザー採用済みのOption Aである。

### B. Linux named staging cleanupへmacOSと同じwaiverを拡張する

- 利点: `O_TMPFILE`を持たないLinux filesystemでも現行のnamed staging success laneを維持できる。
- 不採用理由: macOS固有として受容した例外をLinuxへ暗黙拡張し、same-UID cleanup riskを広げる。ユーザーのOption Aはこれを採用しない。

### C. Linuxをunsupportedとする

- 利点: cleanup raceを完全に避けられる。
- 不採用理由: anonymous stagingを提供するLinux filesystemまで利用不能にし、利用者価値を過度に縮小する。

### D. trusted helper / distinct security principalを導入する

- 利点: named stagingを使う場合にもより強いownership境界を設けられる可能性がある。
- 不採用理由: daemon、権限、FD transfer、packaging、運用・recoveryを新設する別Epic級の変更である。

## 5. Rollback and Revisit

- rollbackはunsafe named stagingへ暗黙に回帰しない。anonymous capabilityが利用できない環境はfail closedを維持する。
- 実装をrevertする必要がある場合も、committed Artifactを削除・renameしない。
- supported laneを再拡張するには、FD-conditional cleanup等の同等primitive、または新しいaccepted ADRとfresh reviewを必要とする。
- trusted helperを採用する場合はcurrent Issueへ混在させず、別Epicでsecurity / packaging / operational modelを設計する。

## 6. Test and Review Gates

最低限、通常権限Linux supported filesystemでvisible probe pathnameを作らずanonymous stagingからFD-bound no-replace commitへ進めること、cross-filesystem original sourceが成功すること、`O_TMPFILE` / procfs / directory durability preflight不足ではformal destinationなしの`publication_unsupported`となること、formal candidateへの最初のcommitで`EEXIST`がallocation retryとなること、formal entry未作成のcapability / policy failureが個別errnoを漏らさず`publication_unsupported` / `not_committed`となること、pre-commit failureがpathname unlinkを試行しないことを固定する。macOSのaccepted ADR契約は別laneとして不変である。

このADRを反映したEpic requirement / design / planはfresh `spec-reviewer`へ提出し、Issue 345は継承amendmentとfresh reviewを完了するまで実行再開しない。実装完了時はfresh code reviewでLinux named-temp cleanupへのfallbackがないことを確認する。
