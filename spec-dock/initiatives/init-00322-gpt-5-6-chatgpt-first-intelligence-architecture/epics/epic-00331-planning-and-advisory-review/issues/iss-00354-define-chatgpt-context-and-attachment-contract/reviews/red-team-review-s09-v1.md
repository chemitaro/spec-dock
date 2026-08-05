# SpecDock Issue `iss-00354` — S09 Fresh Red Team 正式レビュー

## レビュー対象

| 項目                      | 確認結果                                                     |
| ----------------------- | -------------------------------------------------------- |
| Candidate               | S09 Oracle `0.17.0` compatibility profile implementation |
| Repository              | `chemitaro/spec-dock`                                    |
| Branch                  | `codex/iss-00354-chatgpt-context-contract`               |
| Review source HEAD      | `ac84de312072028ad864d06ae018b3ccf196051d`               |
| GitHub branch tip       | 指定 HEAD と一致                                              |
| Default branch fallback | 使用していない                                                  |
| Review mode             | read-only / defect-only / S09限定                          |
| Verdict                 | **FAIL**                                                 |
| P0                      | **0件**                                                   |
| P1                      | **2件**                                                   |

GitHub Connectorで指定branchのtipが `ac84de312072028ad864d06ae018b3ccf196051d` であることを確認した。別HEADやdefault branchはレビューしていない。

添付から再構成した4つのsource/testのGit blob SHAは、GitHub上の同一HEADのblob SHAと全件一致した。    レビューの添付根拠全体は、canonical文書、ADR、S09 briefs、characterization receipts、matrix、4つのsource/testを含むbundleである。

### Oracle観測モデル証拠

このレビュー実行について、Oracle wrapperのmodel-selection receiptは提示されていない。このため、現在のレビュアー実行に関するrequested model、target、resolved label、strategy、verified値はいずれも**未確認**であり、モデルの成功claimは行わない。

添付内のdirect PATH Oracleおよび過去のChatGPT-Use wrapper記録はCandidate側の観測証拠としてのみ使用し、現在のレビュアーwrapper証拠とは扱っていない。

---

## Findings

### RT-354-S09-001 — P1: 0.17 readerが未characterizeの0.16.1 transcript／repository sentinel形式を受理する

**対象ファイル・行**

* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py:178-224`
* 同 `:243-289`
* 同 `:720-734`
* `tests/unit/infra/test_issue_planning_oracle_artifact.py:16-135`
* 同 `:139-217`
* `artifacts/characterization/s09-oracle-017-native-rerun-20260806.md:48-76`
* `artifacts/characterization/s09-oracle-017-native-inline-20260806.md:45-53`
* `artifacts/implementation-briefs/s09-oracle-017-profile-20260806.md:205-238`
* 同 `:328-345`

**欠陥**

`snapshot_review_json_0170()` は0.17 metadataを読むだけで、その後は0.16.1と共通の `_snapshot_review_json_from_metadata()` に処理を渡している。この共通処理は、artifact `kind="transcript"` と固定の `\n## Answer\n` markerを前提にReview JSONを抽出する。

同様に、`has_exact_repository_access_failure_0170()` は `_has_exact_repository_access_failure_from_metadata()` に処理を渡し、同じtranscript markerと `repository access failed` sentinelを0.17でも受理する。0.17 profile registryは、これらのentry pointを有効な0.17 readerとして登録している。

一方、S09の0.17 characterization receiptsが確認しているartifact schemaは `kind="file"` のZIP artifactであり、0.17のtranscript artifact、`## Answer` marker、Review JSON抽出形式、repository-access-failure sentinelは観測されていない。native receiptも、確認済みcore shapeとしてfile artifactだけを示している。

S09 original briefは、0.17 sanitized schemaが完全にcharacterizeされた場合だけdecoderを追加し、status、repository sentinel、ZIP、Review JSONの各entry pointをselected readerへbindすることを要求している。現在の実装は、未characterize部分をrejectするのではなく、0.16.1形式を暗黙に受理している。

**再現根拠**

添付されたexact sourceをread-onlyのPython harnessへ読み込み、次の0.17 completed metadataを構成した。

```text
version = 0.17.0
status = completed
artifact.kind = transcript
transcript = 0.16.1形式の "\n## Answer\n{\"verdict\":\"pass\"}"
```

観測結果:

```text
0.17-review-json-accepted = {"verdict":"pass"}
```

同じく0.16.1形式のsentinel transcriptを与えると:

```text
0.17-0161-sentinel-accepted = True
```

0.17固有テストはregistry、ZIP core schema、`transfer`／`origin`無視、cross-version call、invalid statusを検証しているが、0.17 Review JSONまたはrepository sentinelのpositive／negative fixtureは存在しない。0.16.1用fixtureだけが共有実装を通しているため、このfail-openを検出できない。

**影響**

* Formal Reviewの0.17 pathが、direct PATH Oracleで確認されていない0.16.1 transcript形式からclosed Review JSONを生成できる。
* 未characterize schemaをfail-closedにするREQ-021／REQ-022と、S09 exact reader契約を破る。
* 0.17 repository access failure判定も、未確認のsentinel形式によってbranch gateを決定できる。
* これはS12のdownload/capture taxonomyを先取りする問題ではない。S09で既に登録・実行可能になっている0.17 reader entry point自体の欠陥である。

**最小修正方針**

Direct PATH Oracle `0.17.0`でReview transcriptまたは0.17 equivalent closed JSON、およびrepository failure sentinelのexact schemaをcharacterizeし、0.17専用fixture・parser・positive／negative testsへbindする。

characterizationが得られるまでは、0.17 Review JSON／repository sentinel entry pointをfail-closedにし、少なくともReviewer operationをsubmission前にblockする。全operationに必要なreader contractを完成できない場合は、canonical stop gateに従って0.17 profile登録自体を保留する。

---

### RT-354-S09-002 — P1: inline characterization receiptのcanonical bytesとEAL-068 SHA-256が一致しない

**対象ファイル・行**

* `artifacts/characterization/s09-oracle-017-native-inline-20260806.md:1-59`
* `report.md:138`
* `artifacts/implementation-briefs/s09-oracle-017-profile-inline-20260806.md:269-284`

**欠陥**

GitHub exact HEADにあるcanonical inline receiptのbytesをSHA-256で計算すると、結果は次の値である。

```text
60f8a83fe78152264a83656c9ad7f84d27f8bec2bafdb27179b304c5094544a8
```

しかし、`report.md` のEAL-068はreceipt SHA-256を次の値として記録している。

```text
3fa59e69ad5b1f2345c62f9b5afabe394851ac4ad0c7be07773f55c5e53da370
```

GitHub上のreceipt Git blob SHAは添付から再構成したblobと一致しており、別HEADや添付変換を比較しているものではない。 EAL-068が異なるSHAを記録していることも、同一HEADのreportで確認した。

S09 follow-up briefは、closure条件として「Inline receiptとreport EALのpath、bytes、SHA-256が一致する」ことを明示している。現在はこの条件を満たさない。

**再現根拠**

```text
sha256(canonical s09-oracle-017-native-inline-20260806.md)
= 60f8a83fe78152264a83656c9ad7f84d27f8bec2bafdb27179b304c5094544a8

report EAL-068 receipt SHA-256
= 3fa59e69ad5b1f2345c62f9b5afabe394851ac4ad0c7be07773f55c5e53da370
```

**影響**

* `inline_mode_characterized=True` の唯一のtext-only positive evidenceが、canonical receipt bytesへ暗号学的にbindingされていない。
* EAL-068がどのreceipt revisionを採用したのか検証できない。
* S09明示closure条件を満たさず、text-only inline capability declarationの正式採用根拠が成立しない。

**最小修正方針**

権威あるinline receipt bytesを確定し、次のいずれか一方だけを行う。

1. 現在のcanonical receiptが正本なら、EAL-068を実SHA
   `60f8a83fe78152264a83656c9ad7f84d27f8bec2bafdb27179b304c5094544a8`
   へ訂正する。
2. EAL-068の既存SHAが正本なら、そのSHAに対応する正式receipt bytesを復元し、canonical artifactを置換する。

修正後、path、bytes、SHA-256の一致を同一pushed HEADで再検証する。

---

## Findingなしと確認したS09契約

| 確認項目                    | 判定                                                                                                     |
| ----------------------- | ------------------------------------------------------------------------------------------------------ |
| 0.16.1 browser argv     | `Pro`、`select`、managed Chrome、cookie sync無効、`always`、prompt、repeated `--file`の既存順序を保持                  |
| 0.16.1 session argv     | 旧exact `session <id> --harvest --no-recover` をprofile builderへ移管                                       |
| Exact registry          | `0.16.1` と `0.17.0` だけを登録                                                                              |
| 0.17 browser policy     | `gpt-5.6`、`select`、managed Chrome flags、通常attachment `always`                                          |
| Completed-only decoder  | `completed`だけterminal。その他はinvalid                                                                      |
| Inline declaration      | `inline_mode_characterized=True`。runtimeでinline fallbackはまだ選択しない                                       |
| Harvest／capture binding | 0.17の両fieldが同一builder objectを所有                                                                        |
| `transfer`／`origin`     | 存在を許容するが、path／size／SHA／validation authorityには使用しない                                                     |
| Unknown version         | `0.17.1`、`0.18.0`等をprofile lookup前提でfail-closed                                                        |
| Malformed version       | help、prompt、recoveryへ進まずfail-closed                                                                    |
| Generic recovery        | `_recover_same_session`はselected profileのbuilderだけを呼び、command tokenを再構築しない                             |
| S10以降の先取り               | failure taxonomy、submission evidence gate、inline retry loop、capture invocation、public reason追加は実装していない |

ただし、0.17 reader全体については `RT-354-S09-001`、inline evidence identityについては `RT-354-S09-002` が残るため、上表の個別成立だけではS09をPASSにできない。

---

## 検証したファイル

### Canonical／evidence

* `requirement.md`
* `design.md`
* `plan.md`
* `report.md`
* `decisions/ADR-ISS354-001-oracle-017-browser-compatibility.md`
* `artifacts/implementation-briefs/s09-oracle-017-profile-20260806.md`
* `artifacts/implementation-briefs/s09-oracle-017-profile-inline-20260806.md`
* `artifacts/characterization/s09-oracle-017-native-rerun-20260806.md`
* `artifacts/characterization/s09-oracle-017-native-inline-20260806.md`
* `artifacts/implementation-and-test-matrix.md`

### Source／tests

* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py`
* `tests/unit/infra/test_issue_planning_chatgpt.py`
* `tests/unit/infra/test_issue_planning_oracle_artifact.py`

---

## 実施した検証

* GitHub repository取得とnamed branch存在確認
* named branch tipと指定exact HEADの一致確認
* exact HEADから4 source/test blobを取得
* 添付版とGitHub版のGit blob SHA比較
* implementation commit `f8cfbc9f27febb50f310790bb8f63b76aa62cdcb` からreview HEADまでの比較

  * 差分は `report.md` の1 commitのみ
* canonical inline receiptのSHA-256再計算
* 4 source/testのPython syntax compile

  * 全件成功
* generic recovery helperとversion-specific buildersの静的監査
* 0.17 Review JSON／repository sentinelのread-only再現harness
* 0.17固有test matrixの検索と、Review JSON／sentinel fixture欠落の確認

---

## 仮定・不確実性・未確認事項

* Reportに記録されたfocused `144 passed`、infra subset `40 passed`、infra全体 `531 passed / 573 skipped`、Ruff、Mypy、validate、diff-checkは、このレビューでは独立再実行していない。GitHub Connectorから実行可能なrepository checkoutは得ていないため、記録済み証跡としてのみ扱った。
* Direct PATH Oracle `0.17.0` browser smoke、managed Chrome、model picker、attachment delivery、ZIP downloadは再実行していない。characterization receiptsの記述と実装の整合だけを確認した。
* 現在のレビューwrapperにmodel evidenceがないため、レビュアー実行のmodel identity／verified状態は未確認である。
* Candidate、branch、source、tests、report、receiptは変更していない。パッチ、ZIP、修正版artifactは生成していない。

---

## 次アクション

`RT-354-S09-001` と `RT-354-S09-002` をBlue側で最小修正し、新しいpushed exact HEADを別のfresh Red Team threadで再レビューする。P0/P1が0件になるまで、S09 closure、S10開始、PR、merge、Issue close、Issue finishは保留する。
