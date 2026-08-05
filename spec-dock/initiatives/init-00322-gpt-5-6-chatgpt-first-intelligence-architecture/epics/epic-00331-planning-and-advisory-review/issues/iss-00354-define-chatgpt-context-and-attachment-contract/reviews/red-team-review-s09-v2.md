# SpecDock Issue `iss-00354` — S09 Fresh Red Team 正式再レビュー

## レビュー識別

| 項目                       | 確認結果                                                                                                                                                                                                     |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Repository               | `chemitaro/spec-dock`                                                                                                                                                                                    |
| Named branch             | `codex/iss-00354-chatgpt-context-contract`                                                                                                                                                               |
| Review source HEAD       | `ec179c301c045f94d54abea308c47e79d16c5979`                                                                                                                                                               |
| GitHub parity            | named branch tip と review HEAD は **identical**、ahead `0`、behind `0`                                                                                                                                      |
| Red v1 HEADとの差分          | `ac84de312072028ad864d06ae018b3ccf196051d` から ahead `1`。変更は4 source/test、`report.md`、Blue repair brief、Red v1 canonical/rawの計8ファイル                                                                       |
| Default branch fallback  | **未使用**                                                                                                                                                                                                  |
| Review mode              | fresh thread / read-only / defect-only                                                                                                                                                                   |
| Model-selection evidence | 現在の再レビュー実行に関するwrapper telemetryは本インターフェースへ提示されていない。添付済みRed v1／Blue repair証跡で確認できる値は requested `gpt-5.6`、target/resolved `GPT-5.6 Sol`、strategy `select`、verified `yes`。`Luna`／Reasoning Effort `Max`は未確認 |
| Verdict                  | **FAIL**                                                                                                                                                                                                 |
| P0                       | **0件**                                                                                                                                                                                                   |
| P1                       | **2件**                                                                                                                                                                                                   |

添付bundleの15論理ファイルを読み、GitHubの同一HEADにある各blobと照合した。canonical requirement/design/plan/report、ADR、S09 initial/inline/Blue-repair briefs、inline receipt、Red v1 canonical/raw、4 source/testはすべて添付再構成blobとGitHub blobが一致した。

---

## 結論

Red v1の修正は大部分が成立している。

* `0.16.1`／`0.17.0` reader capability bindingは明示された。
* `0.17.0` Review transcriptとrepository sentinelの直接reader経路は拒否される。
* `0.17.0` Reviewerはversion/help capability gate後、managed Chrome接続・browser argv・prompt・recovery・session directory作成前にblockされる。
* EAL-068のreceipt SHAはcanonical実値`60f8...4544a8`へ訂正され、Red v1 canonical/rawも不変である。
* exact-version registry、unknown/malformed version fail-closed、0.16.1 parser、0.17 file-only ZIP、managed Chrome、通常attachment `always`、completed-only decoder、profile-owned recovery builderは維持されている。

ただし、**0.17 authoring ZIP readerの直接呼出しがmixed/uncharacterized inventoryを受理する欠陥**と、**修正commitが既にpush済みである事実にcanonical reportのcurrent stateが追随していない欠陥**が残る。したがってP0/P1=0のPASS条件を満たさない。

---

## Findings

### RT-354-S09-V2-001 — P1: 0.17 authoring ZIPの直接reader経路がmixed／unknown artifact inventoryを受理する

**Severity:** P1

**対象ファイル・行**

* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py:106-118`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py:121-139`
* `tests/unit/infra/test_issue_planning_oracle_artifact.py:173-194`
* `artifacts/implementation-briefs/s09-red-v1-blue-repair-20260806.md:290-301`

**欠陥**

`has_exact_repository_access_failure_0170()`はinventory中に`kind != "file"`が一件でもあれば拒否する。一方、`snapshot_authoring_zip_0170()`は0.17 metadataを読んだ後、0.16.1と共通の`_snapshot_authoring_zip_from_metadata()`へそのまま委譲する。

共通処理は、inventory全体を検証せず、`kind == "file"`かつZIP名に一致するentryだけを抽出する。このため、valid ZIP fileと未characterize artifactが混在していても、未characterize entryを無視してZIP snapshotを成功させる。

**再現根拠**

次の0.17 metadataをread-only harnessで構成した。

```text
version = 0.17.0
status = completed
mode = browser
artifacts =
  - kind = file       / valid ZIP
  - kind = transcript / legacy 0.16.1 form
```

同じ`OracleArtifactReader`に対して直接呼び出した結果は次のとおりだった。

```text
reader.snapshot_authoring_zip(...)
  -> ACCEPT candidate.zip

reader.has_exact_repository_access_failure(...)
  -> REJECT oracle_artifact_rejected
```

`transcript`を`repository-failure`またはkind欠落entryへ置換しても、valid ZIPとのmixed inventoryでは`reader.snapshot_authoring_zip(...)`が成功した。

現在のrepository testは、単独の`transcript`、`repository-failure`、kind欠落を`has_exact_repository_access_failure(...)`へ渡すケースだけをparameterizeしている。Blue repair briefが必須とした`file + transcript`ケースと、`snapshot_authoring_zip(...)`の直接reader経路は検証されていない。

**影響**

* ユーザー指定の「0.17未characterize mixed kindを直接readerでもfail-closed」という最小条件を満たさない。
* 現在の`_collect_typed_result()`はsentinel判定を先に呼ぶため通常orchestrationでは拒否されるが、安全性が呼出し順序へ依存している。
* readerの別caller、直接利用、または将来の処理順序変更では、未characterize schemaをvalid 0.17 ZIPとして受理し得る。
* Red v1が問題にした「version-bound reader自身が未characterize schemaを受理する」根本境界が完全には閉じていない。

**最小修正方針**

`0.17.0`専用のinventory-kind guardを`OracleArtifactReader`内部へ置き、`snapshot_authoring_zip_0170()`もinventory中の全entryが`kind == "file"`である場合だけ共通ZIP処理へ進める。

少なくとも次の直接readerテストを追加する。

```text
valid file + transcript          -> oracle_artifact_rejected
valid file + repository-failure  -> oracle_artifact_rejected
valid file + missing kind        -> oracle_artifact_rejected
file-only valid ZIP              -> success
```

0.16.1 parser、0.17 file-only ZIP/core、generic orchestration、S10 taxonomy／fallback／captureには変更を広げない。

---

### RT-354-S09-V2-002 — P1: canonical reportがpush済みrepair HEADを未commit／未pushとして記録している

**Severity:** P1

**対象ファイル・行**

* `report.md:143` — EAL-073
* `report.md:357` — Delegated Worker Evidence
* `report.md:392` — Reviewer Gate Status
* `report.md:404` — Milestone / Commit Candidate Gate
* `artifacts/implementation-briefs/s09-red-v1-blue-repair-20260806.md:429-450`
* `artifacts/implementation-briefs/s09-red-v1-blue-repair-20260806.md:624-648`

**欠陥**

GitHub Connectorでは、named branch tipと`ec179c301c045f94d54abea308c47e79d16c5979`がidenticalである。Red v1 HEAD `ac84de3...`からは1 commit進んでおり、そのcommitに4 source/test、report、Blue repair brief、Red v1 canonical/rawが含まれている。

しかし、同じHEADのcanonical reportは次のように記録している。

* EAL-073: 「許可4ファイルとreport/evidenceをcommit/pushし…」
* Delegated Worker Evidence: 「commit/pushとfresh Red v2は未実施」
* Reviewer Gate Status: 「commit/push後のfresh Red v2が必要」
* Milestone Gate: 「pending commit for four provider/test files」「current worktree contains … pending commit」

EAL-073はsource baseline `ac84de3...`だけを記録し、実際のpushed repair HEAD `ec179c...`をimplementation identityへ束ねていない。

Blue repair briefは、完了条件として次を明示している。

```text
resulting commit is pushed
local/remote exact HEAD match
report state = repair_applied_pending_fresh_review
resulting pushed HEAD is recorded
next = fresh Red v2
```

**再現根拠**

```text
GitHub named branch tip
= ec179c301c045f94d54abea308c47e79d16c5979

compare(ec179c..., named branch)
= identical / ahead 0 / behind 0

compare(ac84de3..., ec179c...)
= ahead 1 / behind 0

report current state
= commit/push pending
```

repository stateとcanonical evidence ledgerが同時に成立しない。

**影響**

* Blue repair実装を今回のreview HEADへ暗号学的・履歴的にbindできない。
* reportを読む後続workerは、既にpush済みのmutationを再度要求される。
* fresh Red v2の入力identity、S09の現在状態、次ゲートが一意にならない。
* Blue repair briefの明示的なhandoff完了条件を満たさず、S09 reviewer gateを正しく進められない。

**最小修正方針**

`report.md`だけを修正し、current S09 surfacesを次へ同期する。

* repair implementation commit／review sourceとして`ec179c301c045f94d54abea308c47e79d16c5979`を記録する。
* named branchとのidentical／ahead 0／behind 0を記録する。
* 「commit/push予定」「pending commit」「current worktree pending」の表現を除去する。
* Red v1 FAIL、finding IDs、canonical/raw SHA、inline receipt bytesを変更しない。
* S09 closureは`none`のまま維持する。
* 本v2 FAILをappend-only evidenceとして記録し、次ゲートを新しいpushed HEADに対するfresh Red v3とする。

production code、tests、receipt、Red v1、S10以降へ変更を広げない。

---

## Red v1 findingsの再判定

| Red v1 finding   | 再判定                                                                                                                                                                                           |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `RT-354-S09-001` | **部分解消**。0.17 Review transcript、repository sentinel、unknown単独kind、Reviewer pre-submit blockは修正済み。ただしvalid ZIPとのmixed inventoryを`reader.snapshot_authoring_zip()`が直接受理するため完全解消ではない             |
| `RT-354-S09-002` | **解消済み**。canonical receipt SHAとEAL-068は`60f8a83f...4544a8`で一致。artifact SHA identityは`9566748c...827a2`のまま。Red v1 canonical/rawはbyte-identical。ただしrepair commitのreport current-state不整合は別の新規P1 |

---

## Findingなしと確認したS09契約

| 確認項目                       | 結果                                                                                                                                                          |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Exact profile registry     | `0.16.1`と`0.17.0`だけを登録。`0.17.1`等は未登録                                                                                                                        |
| Reader capability binding  | 0.16.1=`review_output_characterized=True`、0.17.0=`False`                                                                                                    |
| 0.17 Review JSON           | `snapshot_review_json_0170()`はmetadata検証後に常に`oracle_artifact_rejected`                                                                                      |
| 0.17 repository sentinel   | transcript、unknown kind、kind欠落を直接readerで拒否                                                                                                                  |
| 0.17 Reviewer gate         | version/root help/session help後、managed Chrome network preflight・browser builder・prompt・recovery・session directory前に`blocked/oracle_capability_unsupported` |
| 0.16.1 compatibility       | existing Review JSON parser、exact sentinel、browser argv、session argvを維持                                                                                     |
| 0.17 browser policy        | `gpt-5.6`、`select`、managed Chrome、cookie sync無効、通常attachment `always`、one prompt                                                                            |
| Stage decoder              | `completed`のみterminal。他値はinvalid                                                                                                                            |
| Recovery ownership         | generic recoveryはselected profileの`harvest_argv_builder`のみを使用。generic helper内にhardcoded `session`／`--harvest`／`--no-recover` assemblyなし                     |
| Harvest/capture binding    | 0.17のharvest／capture fieldsは同一characterized builder objectへbind                                                                                             |
| Unknown/malformed versions | help、prompt、recovery、session directoryへ進まずfail-closed                                                                                                       |
| S10 scope                  | failure taxonomy、inline fallback execution、new-execution loop、artifact-pending／independent captureは未実装                                                      |
| Change scope               | Red v1 HEADからの8ファイル差分はBlue repair allowlist／evidence boundary内                                                                                              |

---

## Evidence identity確認

```text
canonical inline receipt SHA-256
= 60f8a83fe78152264a83656c9ad7f84d27f8bec2bafdb27179b304c5094544a8

EAL-068 receipt SHA-256
= 60f8a83fe78152264a83656c9ad7f84d27f8bec2bafdb27179b304c5094544a8

recorded ZIP artifact SHA-256
= 9566748c79c49e5369d36fff3c76d2cb65250dc281fdaca563c5c0be3bd827a2

Red v1 canonical SHA-256
= 61963c422460437462e6d2dbe0e0e229a5832c37764cc85c7cdd093b86a72c74

Red v1 raw SHA-256
= 61963c422460437462e6d2dbe0e0e229a5832c37764cc85c7cdd093b86a72c74

Red v1 canonical/raw
= byte-identical
```

EAL-068にはreceipt SHAとartifact SHAが別identityとして正しく記録されている。

---

## 確認ファイル

### Canonical／design authority

* `requirement.md`
* `design.md`
* `plan.md`
* `report.md`
* `decisions/ADR-ISS354-001-oracle-017-browser-compatibility.md`

### S09 characterization／brief／review evidence

* `artifacts/characterization/s09-oracle-017-native-20260806.md`
* `artifacts/characterization/s09-oracle-017-native-rerun-20260806.md`
* `artifacts/characterization/s09-oracle-017-native-inline-20260806.md`
* `artifacts/implementation-briefs/s09-oracle-017-profile-20260806.md`
* `artifacts/implementation-briefs/s09-oracle-017-profile-inline-20260806.md`
* `artifacts/implementation-briefs/s09-red-v1-blue-repair-20260806.md`
* `reviews/red-team-review-s09-v1.md`
* `reviews/red-team-review-s09-v1-raw.md`

### Current source／tests

* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py`
* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py`
* `tests/unit/infra/test_issue_planning_chatgpt.py`
* `tests/unit/infra/test_issue_planning_oracle_artifact.py`

---

## 確認コマンド／操作

```text
GitHub Connector:
  get_repo(chemitaro/spec-dock)
  search_branches(codex/iss-00354-chatgpt-context-contract)
  compare_commits(ec179c..., named branch)
  compare_commits(ac84de3..., ec179c...)
  fetch_commit(ec179c...)
  fetch_file(..., ref=ec179c...) for canonical/evidence/source/test files
```

```text
sha256sum:
  inline characterization receipt
  Red v1 canonical
  Red v1 raw

cmp:
  Red v1 canonical vs raw

Git blob reconstruction:
  attached 15 logical files vs GitHub exact-HEAD blob SHA

python -m py_compile:
  current 4 source/test files

read-only isolated harness:
  0.17 transcript direct rejection
  0.17 sentinel direct rejection
  0.17 unknown/missing/mixed inventory behavior
  0.17 file-only ZIP positive path
  0.16.1 Review/sentinel positive path
  unknown reader versions
  0.17 Reviewer call order and zero-call boundary
  generic recovery token/AST inspection
```

Candidate、repository、report、review evidence、receipt、ZIPは変更していない。patch、新規ZIP、修正版review artifactは生成していない。

---

## 仮定・不確実性・未確認事項

* Report記載のfocused `152 passed`、infra subset `45 passed / 1067 deselected`、infra全体`539 passed / 573 skipped`、Ruff、Mypy、SpecDock validate、`git diff --check`は独立再実行していない。今回はGitHub exact source/test、構文compile、限定read-only harnessで確認した。
* Direct PATH Oracle `0.17.0`、managed Chrome、model picker、attachment delivery、same-session harvest、ZIP downloadは再実行していない。characterization receiptsと実装の整合だけを確認した。
* ZIP artifact実体bytesは添付／repositoryに含まれないため、`9566748c...827a2`はreceipt／report上のidentity不変を確認したものであり、ZIP実体の独立再hashではない。
* 現在のfresh v2実行に関するwrapper model telemetryは提示されていない。モデル自己申告はreview evidenceへ採用していない。
* GitHub branch tipとのparityは確認したが、ローカルworktreeのclean状態はGitHub Connectorからは確認していない。

---

## 次アクション

Blue側で`RT-354-S09-V2-001`の0.17 mixed-inventory direct-reader fail-closedと、`RT-354-S09-V2-002`のreport-only current-state同期だけを修正する。新しいexact HEADをnamed branchへpushし、今回およびRed v1とは別のfresh Red Team threadで再レビューする。

P0/P1が0件になるまで、S09 closure、S10開始、PR、merge、Issue close、Issue finishは保留する。
