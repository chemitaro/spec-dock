# iss-00354 S09 Fresh Red Team v5 正式レビュー

## レビュー対象

| 項目                      | 確認値                                             |
| ----------------------- | ----------------------------------------------- |
| Repository              | `chemitaro/spec-dock`                           |
| Named branch            | `codex/iss-00354-chatgpt-context-contract`      |
| GitHub exact HEAD       | `d52f8ab1df0d34be36880d1be64f6b2605a63065`      |
| Branch comparison       | `identical` / ahead `0` / behind `0`            |
| Default branch fallback | 使用していない                                         |
| Candidate version       | `s09-blue-repair-v2`                            |
| Candidate ID            | `iss-00354-s09-blue-repair-v2-20260805T225843Z` |
| Implementation commit   | `470cacf5051272edfa71e9780f263d1f402a33a0`      |
| Red v3 reviewed HEAD    | `26d40034507b60f76d06536fb7c5e552bdb49850`      |
| Red v4 reviewed HEAD    | `aa019e5d53af171b31845124e15482f78cd0fcb9`      |
| Review mode             | Fresh Red Team v5 / read-only / defect-only     |
| レビュー時刻                  | 2026-08-06 09:34 JST                            |
| 判定                      | **FAIL**                                        |
| 件数                      | P0=`0` / P1=`1` / P2=`0` / P3=`0`               |

GitHub の current commit は、Red v4 evidence と Blue v4 report 同期を行った `d52f8ab1df0d34be36880d1be64f6b2605a63065` であることを確認した。

## 参照したファイル一覧

添付入力は `attachments-bundle.txt` であり、そこから34論理ファイルを再構成した。

`ISSUE_DIR`:

```text
spec-dock/initiatives/
init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/
epics/epic-00331-planning-and-advisory-review/
issues/iss-00354-define-chatgpt-context-and-attachment-contract
```

### Canonical / identity / supporting artifacts

```text
ISSUE_DIR/requirement.md
ISSUE_DIR/design.md
ISSUE_DIR/plan.md
ISSUE_DIR/report.md
ISSUE_DIR/decisions/ADR-ISS354-001-oracle-017-browser-compatibility.md
ISSUE_DIR/MANIFEST.json
ISSUE_DIR/CHECKSUMS.sha256
ISSUE_DIR/candidate-note.md
ISSUE_DIR/artifacts/context-and-attachment-contract.md
ISSUE_DIR/artifacts/decision-and-migration-ledger.md
ISSUE_DIR/artifacts/implementation-and-test-matrix.md
ISSUE_DIR/artifacts/oracle-017-failure-classification.md
```

### S09 characterization

```text
ISSUE_DIR/artifacts/characterization/s09-oracle-017-native-20260806.md
ISSUE_DIR/artifacts/characterization/s09-oracle-017-native-inline-20260806.md
ISSUE_DIR/artifacts/characterization/s09-oracle-017-native-rerun-20260806.md
```

### S09 implementation / repair briefs

```text
ISSUE_DIR/artifacts/implementation-briefs/s09-oracle-017-profile-20260806.md
ISSUE_DIR/artifacts/implementation-briefs/s09-oracle-017-profile-inline-20260806.md
ISSUE_DIR/artifacts/implementation-briefs/s09-red-v1-blue-repair-20260806.md
ISSUE_DIR/artifacts/implementation-briefs/s09-red-v2-blue-repair-v2-20260806.md
ISSUE_DIR/artifacts/implementation-briefs/s09-red-v3-blue-repair-v3-20260806.md
ISSUE_DIR/artifacts/implementation-briefs/s09-red-v4-blue-repair-v4-20260806.md
```

### S09 formal reviews

```text
ISSUE_DIR/reviews/red-team-review-s09-v1.md
ISSUE_DIR/reviews/red-team-review-s09-v1-raw.md
ISSUE_DIR/reviews/red-team-review-s09-v2.md
ISSUE_DIR/reviews/red-team-review-s09-v2-raw.md
ISSUE_DIR/reviews/red-team-review-s09-v3.md
ISSUE_DIR/reviews/red-team-review-s09-v3-raw.md
ISSUE_DIR/reviews/red-team-review-s09-v4.md
ISSUE_DIR/reviews/red-team-review-s09-v4-raw.md
```

### Runtime / tests

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/zip_contract.py
tests/unit/infra/test_issue_planning_chatgpt.py
tests/unit/infra/test_issue_planning_oracle_artifact.py
```

添付から再構成した34ファイルは、すべて GitHub exact HEAD の対応 Git blob と一致した。Canonical three documents、`report.md`、ADR、MANIFEST、CHECKSUMS についても版違いはない。

## Findings

| ID                  | severity | 対象                                                                                                                                                                                | 事実と再現根拠                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | 判定       |
| ------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------- |
| `RT-354-S09-V5-001` | **P1**   | `report.md` の S09 current-state — Implementation Delegation Gate、Delegated Worker Evidence、Parent Implementation Exception、Reviewer Gate Status、Milestone / Commit Candidate Gate | GitHub current HEAD `d52f8ab1…` は、Blue v4 の `report.md` 同期、Blue v4 brief、Red v4 canonical/raw の追加を既にcommitしたHEADであり、named branchへpush済みである。一方、current `report.md` は S09 を `review-failed / blue-v4-report-repair-active`、`Blue v4 report-only repairを実施中`、`Blue v4 report repair中`、`Blue v4 report-only同期をcommit/push後`、`Commit前…push後…` と記録している。すなわち、Blue v4 mutationが完了したcurrent HEAD上で、Blue v4を未完了・commit/push前のfuture actionとして扱っている。これは必須状態である「Red v4 FAIL → Blue v4修正済み → fresh Red v5 pending」ではなく、current-stateが再び一世代遅れている。Red v3 pendingという旧stale assertion自体は除去されたが、Red v4が指摘したcurrent-state/evidence同期欠陥の型は解消していない。 | **FAIL** |

## その他の必須確認結果

### Identity / attachment

* Named branch のtipは expected exact HEAD `d52f8ab1df0d34be36880d1be64f6b2605a63065` と一致した。
* Candidate version、Candidate ID、implementation commit は維持されている。
* 添付34論理ファイルと GitHub current HEAD は全件一致した。
* `470cacf…` から current HEAD までの変更は、`report.md` と Red v3/v4・Blue v3/v4 evidenceだけである。runtime、tests、`requirement.md`、`design.md`、`plan.md` にsemantic mutationはない。
* `aa019e…` から current HEAD までの変更も1 commit・4ファイルに限定され、semantic mutationは `report.md` のみである。

### EAL / OAL

* `EAL-073`〜`EAL-079` は連番で存在する。
* `EAL-074` は `EAL-073`直後かつ`EAL-075`直前に存在する。
* `EAL-073`〜`EAL-076` は Blue v4前の `aa019e…` と byte-equivalent であり、既存行の変更はない。
* `OAL-002` は `OAL-001` の直後に存在する。

### Review / brief evidence identity

| Evidence               | 確認結果                                                                    |
| ---------------------- | ----------------------------------------------------------------------- |
| Red v3 canonical / raw | byte-identical                                                          |
| Red v3 SHA-256         | `aaf20c7288288f84197b02e6265cd2aaa3acb85235b1fd6f71c8f5217415b6f2` — 一致 |
| Red v4 canonical / raw | byte-identical                                                          |
| Red v4 SHA-256         | `7e7fc0c39f6040b4134bd0eceb72654ff6e204c0f5c8252948cdd30a0b48b911` — 一致 |
| Blue v3 brief SHA-256  | `cd95bb0a1bc21198631d29b80395a9799ebea1910fb0d5c9bf2f637e02e22a93` — 一致 |
| Blue v4 brief SHA-256  | `6d5708e2009b72868b5b95bb41dde3bfb3c0e58a81d0aa1bfc534e5cebffa4` — 一致   |

Red v3 canonical/raw は同一 Git blob、Red v4 canonical/raw も同一 Git blobである。

### Runtime / reader / builder / fail-closed

静的確認の範囲では、新しいP0/P1は認めなかった。

* exact `0.16.1` / `0.17.0` profileが分離されている。
* 0.16.1と0.17.0のsame-session argv builderはprofileが所有し、harvest/captureへ明示的にbindされている。
* 0.17 decoderは`completed`だけをterminalとする。
* unknown versionを広いsemver rangeで受理していない。
* 0.17 authoring ZIP readerは共通snapshot helperへ委譲する前に全inventoryの`kind=file`を要求し、未characterize entryをfail-closedにする。
* Testsは0.16.1/0.17.0のexact reader binding、unknown version rejection、0.17 file-only positive、mixed transcript／repository-failure／missing-kind inventoryの6ケース拒否を固定している。

### Red v3 / Red v4 finding disposition

* `RT-354-S09-V3-001`：**解消済み**。`EAL-074` は復元され、既存行も維持されている。
* `RT-354-S09-V4-001`：**未完全解消**。Red v3 pending のstale assertionは除去されたが、current HEAD上でBlue v4 repairを未完了・commit/push前と扱う新たな一世代遅れが残る。

## 根拠

本判定は、GitHub named branchのexact HEAD、添付から再構成した34ファイルのbyte identity、commit間ファイル差分、current `report.md` の各S09 gate row、source/testの静的確認に基づく。

## 仮定

なし。Repository、branch、HEAD、Candidate identityはすべて明示値とGitHub connectorの確認結果を使用した。

## 不確実性・未検証主張

Oracle browser smoke、private session、pytest／Ruff／Mypy／SpecDock validateは本レビューでは再実行していない。既存command resultはcommitted evidenceとして照合したが、独立再現済みとは扱わない。今回のP1はcurrent HEADと`report.md`だけで再現可能であり、この未再実行事項には依存しない。

## 最終判定

**FAIL — P0=0 / P1=1 / P2=0 / P3=0**

Candidate、runtime、tests、review artifactsに変更は加えていない。
