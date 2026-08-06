# iss-00354 S09 Fresh Red Team v6 正式レビュー

**判定: PASS — P0=0 / P1=0 / P2=0 / P3=0**

## レビュー対象 identity

| 項目                      | 確認値                                                                   |
| ----------------------- | --------------------------------------------------------------------- |
| Repository              | `chemitaro/spec-dock`                                                 |
| Branch                  | `codex/iss-00354-chatgpt-context-contract`                            |
| Exact HEAD              | `b3e281af2c4380c9937bfcf862bd295d3d6be960`                            |
| Branch comparison       | expected HEAD と `identical` / ahead `0` / behind `0`                  |
| Default branch fallback | 使用していない                                                               |
| Candidate version       | `s09-blue-repair-v2`                                                  |
| Candidate ID            | `iss-00354-s09-blue-repair-v2-20260805T225843Z`                       |
| Implementation commit   | `470cacf5051272edfa71e9780f263d1f402a33a0`                            |
| Red v5 reviewed HEAD    | `d52f8ab1df0d34be36880d1be64f6b2605a63065`                            |
| Fresh review identity   | `iss-00354-s09-fresh-red-v6@b3e281af2c4380c9937bfcf862bd295d3d6be960` |
| Review mode             | fresh / read-only / defect-only                                       |
| Mutation                | なし                                                                    |

GitHub named branchのtipは指定されたexact HEADと一致した。HEAD commitは、`report.md`のEAL-080追加とcurrent-state 5行同期、およびBlue v5 briefの追加を内容とする。

## 参照ファイル一覧

添付bundleの37論理ファイルをGitHub exact HEAD上の対応ファイルと照合した。Red v5時点の34ファイルに、Red v5 canonical/rawとBlue v5 briefの3ファイルを加えた構成である。

**Canonical / identity:** `requirement.md`、`design.md`、`plan.md`、`report.md`、`decisions/ADR-ISS354-001-oracle-017-browser-compatibility.md`、`MANIFEST.json`、`CHECKSUMS.sha256`、`candidate-note.md`

**Supporting artifacts:** `context-and-attachment-contract.md`、`decision-and-migration-ledger.md`、`implementation-and-test-matrix.md`、`oracle-017-failure-classification.md`

**Characterization:** `s09-oracle-017-native-20260806.md`、`s09-oracle-017-native-inline-20260806.md`、`s09-oracle-017-native-rerun-20260806.md`

**Implementation briefs:** `s09-oracle-017-profile-20260806.md`、`s09-oracle-017-profile-inline-20260806.md`、`s09-red-v1-blue-repair-20260806.md`、`s09-red-v2-blue-repair-v2-20260806.md`、`s09-red-v3-blue-repair-v3-20260806.md`、`s09-red-v4-blue-repair-v4-20260806.md`、`s09-red-v5-blue-repair-v5-20260806.md`

**Formal reviews:** Red v1〜v5のcanonical/raw、計10ファイル

**Runtime / tests:** `issue_planning_chatgpt.py`、`issue_planning_oracle_artifact.py`、`zip_contract.py`、`test_issue_planning_chatgpt.py`、`test_issue_planning_oracle_artifact.py`

各添付ファイルを元のbyte列へ再構成してGit blob SHAを算出し、GitHub connectorがexact HEADについて返したfull-file blob SHAと比較した結果、**37/37ファイルが一致**した。代表的なruntime、reader、tests、canonical三文書についても一致している。

## Findings

| ID | severity | 対象                                                          | 事実と再現根拠                                                                         | 判定       |
| -- | -------- | ----------------------------------------------------------- | ------------------------------------------------------------------------------- | -------- |
| —  | —        | S09 Blue v5 report-only repairおよびbounded runtime/test scope | P0/P1に該当する欠陥、identity不整合、SHA不整合、current-state矛盾、report外semantic mutationを認めなかった | **PASS** |

## Red v5 findingの解消確認

Red v5の唯一のP1 `RT-354-S09-V5-001`は解消されている。

5つのS09 current-state surfaceは、それぞれ次の状態を一意に表している。

```text
Red v5 FAIL
→ Blue v5 report-only repairがcurrent review Candidate
→ fresh Red v6 pending
```

Implementation Delegation Gateは`review-failed / blue-v5-report-repair-active / red-v6-pending`を記録し、Blue v4同期が`d52f8ab1…`へcommit/push済みであることも明示している。

Delegated Worker Evidence、Parent Implementation Exception、Reviewer Gate Status、Milestone / Commit Candidate Gateも同じ状態へ同期されている。

5行を限定検索した結果、次のcurrent-state欠陥は0件だった。

* `blue-v4-report-repair-active`、Blue v4「実施中」「commit/push前」の旧表現
* Red v3をpendingとするcurrent assertion
* Blue v5 resulting HEADの自己参照
* Candidate version、Candidate ID、implementation commitの変更

Historical EAL内には過去findingを説明する「Red v3 pending」という文字列が残るが、これは解消済みの旧状態を記録する履歴であり、current assertionではない。過去FAILをPASSへ書き換える変更もない。

## EAL / OAL / SHA確認

`EAL-073`〜`EAL-080`は欠番・重複なしで連続し、全8行が既存EAL schemaと同じ14 fieldsを持つ。`EAL-080`はRed v5のFAIL、P0=`0`、P1=`1`、finding `RT-354-S09-V5-001`、reviewed HEAD、Candidate identity、implementation commitを正しく保持している。

Red v5 reviewed HEAD `d52f8ab1…`とcurrent HEADを直接比較した結果、`EAL-073`〜`EAL-079`および`OAL-001`／`OAL-002`はbyte-equivalentである。

`OAL-002`自体はSHA fieldを持つ表ではなく、Blue v4 briefを副次証跡として参照するhistorical rowである。Blue v4 briefのexact SHA bindingはS09 Reviewer Gate Statusに記録されており、実artifactから算出した値と一致した。

| Evidence         | SHA-256確認                                                          |
| ---------------- | ------------------------------------------------------------------ |
| Red v5 canonical | `7bda038fdb085493d8d847ac1ac778c9968516b3a5d7e4c680e1b831585d882b` |
| Red v5 raw       | canonicalとbyte-identical、同じSHA-256                                 |
| Blue v4 brief    | `6d570858e2009b72868b5b95bb41dde3bfb3c0e58a81d0aa1bfc534e5cebffa4` |
| Blue v5 brief    | `b356e0884419b301e84413c418e993d901775809ad0ddee4a84d79745f63348f` |

Red v5 canonical/rawはGitHub上でも同じGit blobであり、Blue v4/v5 briefsも添付から算出したGit blob SHAとGitHub blob SHAが一致した。

## Semantic scope確認

Red v5 reviewed HEAD `d52f8ab1…`からcurrent HEAD `b3e281af…`までの差分は2 commits・4 filesである。

| ファイル                 | 性質                                                |
| -------------------- | ------------------------------------------------- |
| `report.md`          | 唯一のsemantic mutation。EAL-080追加とcurrent-state 5行置換 |
| Red v5 canonical/raw | immutable evidence import                         |
| Blue v5 brief        | immutable evidence import                         |

Implementation commit `470cacf…`からcurrent HEADまでにも、runtime、tests、canonical三文書、ADR、characterization receiptの変更はない。Candidate version、Candidate ID、implementation commitは維持されている。

## Runtime / reader / builder / testsのbounded確認

静的確認では新しいP0/P1を認めなかった。

* Registryはexact `0.16.1`と`0.17.0`だけを受理し、`0.17.1`等をfail-closedにする。
* `0.16.1` profileは旧browser argvと`session <id> --harvest --no-recover`を保持する。
* `0.17.0` profileはcharacterized model/strategy/attachment argvを所有し、同じcharacterized session builderをharvest/captureへ明示的にbindする。
* Generic adapterはprofile builderを経由してsame-session commandを取得する。
* `0.17.0` decoderはcharacterized済みの`completed`だけをterminalとして扱う。
* `0.17.0` authoring ZIP readerは共有snapshot helperへ委譲する前に、全artifact inventoryの`kind=file`を要求する。
* 未characterizeのtranscript、repository-failure、kind欠落を含むmixed inventoryは順序違いを含む6ケースで拒否される。
* `0.17.0` Review outputは未characterizeのため、Reviewer invocationはprompt送信前に`oracle_capability_unsupported`でblockされる。
* Testsはexact profile、0.16.1旧argv、0.17.0 characterized argv、unknown version rejection、cross-version reader rejection、file-only positive、mixed inventory rejectionを固定している。

S10で予定されるsubmission evidenceベースのbounded recoveryやstage-specific public mappingをS09完了として先取りする変更はない。

## 根拠

判定は、GitHub named branchとexact HEADの一致、37添付ファイルのGit blob identity、commit間差分、current `report.md`のEAL/OALおよび5 current-state行、runtime/reader/testsの静的確認に基づく。

## 仮定

なし。Repository、branch、HEAD、Candidate identity、各SHAは明示値とGitHub connector／添付byte列の照合結果を使用した。

## 不確実性・未検証主張

Oracle browser smoke、private session、pytest、Ruff、Mypy、SpecDock validateは本レビューでは再実行していない。既存のcommand resultはcommitted evidenceとして確認したが、独立再現済みとは扱わない。

この未再実行事項は、Blue v5差分がreport/evidence-onlyであり、runtime/test blobsがRed v5 reviewed stateおよびimplementation commit後から不変であるという今回のPASS根拠を変更しない。

**最終判定: PASS — P0=0 / P1=0 / P2=0 / P3=0**

Repository、Candidate、report、review artifacts、添付ファイルへの変更は行っていない。
