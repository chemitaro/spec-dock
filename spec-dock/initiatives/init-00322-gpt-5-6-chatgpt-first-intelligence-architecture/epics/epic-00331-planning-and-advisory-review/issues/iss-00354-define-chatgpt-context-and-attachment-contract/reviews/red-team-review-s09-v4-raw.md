# SpecDock Issue `iss-00354` — S09 Fresh Red Team 正式レビュー v4

## 1. レビュー結果

| 項目                             | 結果                                                                 |
| ------------------------------ | ------------------------------------------------------------------ |
| Logical filename               | `red-team-review-s09-v4.md`                                        |
| Candidate version              | `s09-blue-repair-v2`                                               |
| Candidate ID                   | `iss-00354-s09-blue-repair-v2-20260805T225843Z`                    |
| Repository                     | `chemitaro/spec-dock`                                              |
| Named branch                   | `codex/iss-00354-chatgpt-context-contract`                         |
| Source HEAD / current commit   | `aa019e5d53af171b31845124e15482f78cd0fcb9`                         |
| Implementation commit          | `470cacf5051272edfa71e9780f263d1f402a33a0`                         |
| Previous reviewed HEAD（Red v3） | `26d40034507b60f76d06536fb7c5e552bdb49850`                         |
| Red v3 review SHA-256          | `aaf20c7288288f84197b02e6265cd2aaa3acb85235b1fd6f71c8f5217415b6f2` |
| Current commit subject         | `docs(iss-00354): S09 red v3のreport-only同期を追加`                     |
| Review mode                    | Fresh Red Team v4 / read-only / defect-only                        |
| Red v1〜v3との関係                  | Red v1、Red v2、Red v3とは別のfresh thread                               |
| Verdict                        | **FAIL**                                                           |
| P0                             | **0**                                                              |
| P1                             | **1**                                                              |
| P2                             | **0**                                                              |
| P3                             | **0**                                                              |

**結論:** Red v3の唯一のfinding `RT-354-S09-V3-001` は解消されている。`EAL-074` は所定位置へ正しい内容で復元され、実装commit以後にruntime、tests、canonical requirement/design/plan、既存Red v1/v2 evidenceの変更もない。

一方、current `report.md` の複数のS09 current-state行が、同じcurrent HEADにRed v3 canonical/raw reviewとBlue repair v3 briefが存在するにもかかわらず、Red v3を「pending」「未実施」「唯一の残ゲート」と記録したままである。このcurrent-state／evidence identity不整合をP1一件と判定する。

---

## 2. GitHub exact identity確認

GitHub Connectorではdefault branchを参照せず、named branchを先に取得した。

```text
repository = chemitaro/spec-dock
named_branch = codex/iss-00354-chatgpt-context-contract
locally_detected/source_head = aa019e5d53af171b31845124e15482f78cd0fcb9
github_named_branch_tip = aa019e5d53af171b31845124e15482f78cd0fcb9
relation = identical
ahead = 0
behind = 0
default_branch_fallback = not used
```

current commitのSHAとsubjectはGitHub上でも一致した。commit本文は、既存runtime/test/reviewを変更せず、S09 Red v3のreport-only証跡を4ファイルで追加したものと説明している。

Red v3 reviewed HEAD `26d40034507b60f76d06536fb7c5e552bdb49850` からcurrent HEADまでの差分は1 commitで、次の4ファイルだけである。

1. `ISSUE_DIR/report.md` — 一行追加
2. `ISSUE_DIR/artifacts/implementation-briefs/s09-red-v3-blue-repair-v3-20260806.md` — 新規
3. `ISSUE_DIR/reviews/red-team-review-s09-v3.md` — 新規
4. `ISSUE_DIR/reviews/red-team-review-s09-v3-raw.md` — 新規

`470cacf5051272edfa71e9780f263d1f402a33a0` からcurrent HEADまでに、provider runtime、tests、`requirement.md`、`design.md`、`plan.md`、Red v1/v2 canonical/rawへの変更はない。

---

## 3. 実際に展開・確認した添付ファイル

物理添付 `attachments-bundle.txt` を展開し、含まれる21論理ファイルを全て確認した。各ファイルについて、添付から再構成したbytesのSHA-256とGit blob SHA-1を計算し、GitHub current HEAD `aa019e5d53af171b31845124e15482f78cd0fcb9` の対応blobと照合した。全21ファイルが一致した。

`ISSUE_DIR` は次を表す。

```text
spec-dock/initiatives/
init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/
epics/epic-00331-planning-and-advisory-review/
issues/iss-00354-define-chatgpt-context-and-attachment-contract
```

|  # | 論理ファイル                                                                                             | SHA-256                                                            | Git blob SHA-1                             |
| -: | -------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ | ------------------------------------------ |
|  1 | `ISSUE_DIR/requirement.md`                                                                         | `f87e59aaa54dcf1cdf6637bb9ead34647d5fc33091f3e1abc94c8d883d0aca71` | `76ebf016b12abb06f2b5daa544ea7a1421c7471e` |
|  2 | `ISSUE_DIR/design.md`                                                                              | `ffd88599b265509711c122cd682c00e02c3159435010420e4887f568b4ec727b` | `118e46f905b86883aac9df0f34ebca9e7be2fe91` |
|  3 | `ISSUE_DIR/plan.md`                                                                                | `6e5b8418b7ef98c15a895de90d2b4d49a209fc1e52b9b61cba010b769fec3b0e` | `c553db3d222f5c346c1d15c21f0242cebdee0de4` |
|  4 | `ISSUE_DIR/report.md`                                                                              | `32c6cb5f6e0db2e215cb35af197f8e2b2dfc5be920b5227b8a4d5fc4f6eae8e8` | `c93086e20ac6e4721a172ced0a5498a99695e774` |
|  5 | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py` | `fdcd476f56946094f18410c95b75f2e5d3935177ac0704f82a1643c22caa0a4d` | `5bc79738937e2bf1a2df2e1326852bd1c6b1110d` |
|  6 | `tests/unit/infra/test_issue_planning_oracle_artifact.py`                                          | `f2264f0e0e14b0f8f39add5749abbef18c5458bb3726ea3c68720306ae1b6ed8` | `0fef26e1965bcc0e19f01111493538f011978a5b` |
|  7 | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py`         | `3b0510e61148bd9354b45307d6a69b85e02a0a22c873c84ba83a3df1cfd97b69` | `26819c74d8eaee323cb31ec7241434f42eaf1e65` |
|  8 | `tests/unit/infra/test_issue_planning_chatgpt.py`                                                  | `429fc697f9cb16ebc3e2ef7013b240b439a133be98ac44e617289f34e0765a9d` | `042d8b2e14016062359c7a674db27e73f1e0c3be` |
|  9 | `ISSUE_DIR/artifacts/characterization/s09-oracle-017-native-rerun-20260806.md`                     | `3822d755564c0768063fc57101d7e7019b51ee9f3de69af80323c9573116389a` | `0bde20e51a9423339a629e876027d02c12c46071` |
| 10 | `ISSUE_DIR/artifacts/characterization/s09-oracle-017-native-inline-20260806.md`                    | `60f8a83fe78152264a83656c9ad7f84d27f8bec2bafdb27179b304c5094544a8` | `6db586f6d7f0b1e52b8131eb687d529324c8c12f` |
| 11 | `ISSUE_DIR/artifacts/implementation-briefs/s09-oracle-017-profile-20260806.md`                     | `533ee896a9ff81d21829022db995f1f882553149fb492489932a6f7852669fb2` | `c0f9fb8e06e845177d0ed2aa9ab29809c67c02ee` |
| 12 | `ISSUE_DIR/artifacts/implementation-briefs/s09-oracle-017-profile-inline-20260806.md`              | `26055d6bad240cd5a85efc10b50939ffabd8d1951069413cab32d3f3be897964` | `f3a6dc1f67b981eabf4c03a6185fa31f94cab534` |
| 13 | `ISSUE_DIR/artifacts/implementation-briefs/s09-red-v1-blue-repair-20260806.md`                     | `d544a0a3bf3cad99f0f5396bed092fbd9934c2721ed057e4c390bd0288d71812` | `08fc236c993985515f329af18ee00eea7a1ed237` |
| 14 | `ISSUE_DIR/artifacts/implementation-briefs/s09-red-v2-blue-repair-v2-20260806.md`                  | `df79713c4b65fe19cb9ea2d5925616f030bdca3b6ad2972cd7d4b168f28db083` | `173ad8c749c9f6609b799b1a55450d5a2d0844ba` |
| 15 | `ISSUE_DIR/artifacts/implementation-briefs/s09-red-v3-blue-repair-v3-20260806.md`                  | `cd95bb0a1bc21198631d29b80395a9799ebea1910fb0d5c9bf2f637e02e22a93` | `1103a2155e3aec53c2d55a84a471a2df07dd6f0e` |
| 16 | `ISSUE_DIR/reviews/red-team-review-s09-v1.md`                                                      | `61963c422460437462e6d2dbe0e0e229a5832c37764cc85c7cdd093b86a72c74` | `f339d79c7e9f772b141c7a70af46fad2aa0bbc36` |
| 17 | `ISSUE_DIR/reviews/red-team-review-s09-v1-raw.md`                                                  | `61963c422460437462e6d2dbe0e0e229a5832c37764cc85c7cdd093b86a72c74` | `f339d79c7e9f772b141c7a70af46fad2aa0bbc36` |
| 18 | `ISSUE_DIR/reviews/red-team-review-s09-v2.md`                                                      | `90354aaed36d59e9b11fdc7ed514d282715ec5950b89a7fc95d1d52852c43c4b` | `3eb9e9416f045530ef45cec3232c67be968218e4` |
| 19 | `ISSUE_DIR/reviews/red-team-review-s09-v2-raw.md`                                                  | `90354aaed36d59e9b11fdc7ed514d282715ec5950b89a7fc95d1d52852c43c4b` | `3eb9e9416f045530ef45cec3232c67be968218e4` |
| 20 | `ISSUE_DIR/reviews/red-team-review-s09-v3.md`                                                      | `aaf20c7288288f84197b02e6265cd2aaa3acb85235b1fd6f71c8f5217415b6f2` | `067d1cca7d8bcb973cc8a1d9144e32276dab870a` |
| 21 | `ISSUE_DIR/reviews/red-team-review-s09-v3-raw.md`                                                  | `aaf20c7288288f84197b02e6265cd2aaa3acb85235b1fd6f71c8f5217415b6f2` | `067d1cca7d8bcb973cc8a1d9144e32276dab870a` |

三文書とreportのGitHub blob identityは添付と一致した。

provider source/test 4件も全て一致した。

Red v1、Red v2、Red v3のcanonical/raw pairはそれぞれ同一blobかつ同一SHA-256であり、既存review bytesの変更は確認されなかった。Red v3 review自身もCandidate version、Candidate ID、implementation commit、reviewed HEAD、FAIL/P1=1を一致して記録している。

---

## 4. Red v3 finding再判定

| Red v3 finding                    | 再判定          | 根拠                                                                                                                                                                                                                                                                                                                                          |
| --------------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `RT-354-S09-V3-001` — `EAL-074`欠落 | **RESOLVED** | current `report.md` は `EAL-073` → `EAL-074` → `EAL-075` → `EAL-076` の連続順であり、`EAL-074`は一件だけ存在する。内容はRed v2 canonical/raw、reviewed HEAD `ec179c301c045f94d54abea308c47e79d16c5979`、FAIL、P0=0/P1=2、`RT-354-S09-V2-001`／`002`、Blue repair v2 handoffを保持している。current commitのreport差分はこの一行追加だけであり、`EAL-073`、`EAL-075`、`EAL-076`のbytesと意味は変更されていない。 |

current EALの実際の連続行は次のとおりである。

```text
EAL-073
EAL-074
EAL-075
EAL-076
```

Blue repair v3 briefが固定したCandidate identity、Red v3 reviewed HEAD、Red v3 SHA-256、唯一のfinding、および期待するEAL順序とも一致する。

---

## 5. S09実装契約の確認結果

| 確認項目                                                        | 結果          | 観測事実                                                                                                                                                                                                                                 |
| ----------------------------------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Oracle `0.17.0` exact profile / reader / decoder / builders | **確認済み**    | registryは`0.16.1`と`0.17.0`のexact versionだけを持つ。0.17.0 profileは専用browser argv、completed-only decoder、versioned reader、profile-owned harvest/capture builder、characterized inline declarationを所有する。unknown patchはprofile lookupで受理されない。 |
| Oracle `0.16.1`回帰                                           | **確認済み**    | 0.16.1 readerは独立登録され、review output characterizedを維持する。0.16.1 browser/session exact argvを固定するtestが存在し、0.17.0 pathとは分離されている。                                                                                                           |
| `0.17.0` mixed inventory fail-closed                        | **確認済み**    | `snapshot_authoring_zip_0170()`は共通ZIP helperへの委譲前に全inventoryの`kind=file`を要求する。transcript、repository-failure、kind欠落をvalid ZIPと混在させた両順序6ケースについて、`oracle_artifact_rejected`、helper委譲0、staging生成0を直接固定している。                              |
| Reviewer pre-submit block                                   | **確認済み**    | 0.17.0 readerの`review_output_characterized=False`をpreflight後に検査し、Reviewerはmanaged Chrome、browser argv builder、prompt、recovery、session生成へ到達する前に`blocked / oracle_capability_unsupported`となる。                                          |
| Characterization／brief identity                             | **確認済み**    | native rerun、inline characterization、profile brief、inline追補、Blue repair v1/v2/v3 briefのlogical filename、SHA-256、GitHub blobが添付と一致した。                                                                                                 |
| Test／static結果                                               | **記録証跡を確認** | `report.md`に記録されたfocused、infra subset、Ruff、Mypy、validate、diff-check結果と対応test codeを確認した。本Red v4ではtest commandの再実行は行っていない。                                                                                                             |

---

## 6. Current commitのscope監査

| 監査項目                                             | 結果                  |
| ------------------------------------------------ | ------------------- |
| `report.md`のsemantic変更                           | `EAL-074`一行追加のみ     |
| Red v3 canonical/raw                             | 新規追加、byte-identical |
| Blue repair v3 brief                             | 新規追加                |
| Provider runtime                                 | 変更なし                |
| Tests                                            | 変更なし                |
| `requirement.md`                                 | 変更なし                |
| `design.md`                                      | 変更なし                |
| `plan.md`                                        | 変更なし                |
| Red v1 canonical/raw                             | 変更なし                |
| Red v2 canonical/raw                             | 変更なし                |
| Characterization receipts                        | 変更なし                |
| Existing S09 briefs                              | 変更なし                |
| Default branch / alternate backend / wrapper/API | 使用・変更なし             |

current commitはreport/evidence-onlyであり、implementation commit `470cacf5051272edfa71e9780f263d1f402a33a0` のruntime/test実装を変更していない。このscope自体にはP0/P1欠陥を認めない。

---

## 7. Finding

### `RT-354-S09-V4-001` — P1: 実行済みRed v3とBlue repair v3がS09 current-stateへ反映されず、Red v3がpending／未実施のまま記録されている

**Severity:** P1

#### 対象

* `ISSUE_DIR/report.md:347`
* `ISSUE_DIR/report.md:360`
* `ISSUE_DIR/report.md:373`
* `ISSUE_DIR/report.md:395`
* `ISSUE_DIR/report.md:407`
* `ISSUE_DIR/report.md:55-64`
* `ISSUE_DIR/report.md:143-148`
* `ISSUE_DIR/reviews/red-team-review-s09-v3.md`
* `ISSUE_DIR/reviews/red-team-review-s09-v3-raw.md`
* `ISSUE_DIR/artifacts/implementation-briefs/s09-red-v3-blue-repair-v3-20260806.md`

#### 観測事実

current HEADには、次のRed v3正式結果がcanonical/rawの同一bytesで存在する。

```text
reviewed HEAD = 26d40034507b60f76d06536fb7c5e552bdb49850
Candidate version = s09-blue-repair-v2
Candidate ID = iss-00354-s09-blue-repair-v2-20260805T225843Z
implementation commit = 470cacf5051272edfa71e9780f263d1f402a33a0
verdict = FAIL
P0/P1/P2/P3 = 0/1/0/0
finding = RT-354-S09-V3-001
SHA-256 = aaf20c7288288f84197b02e6265cd2aaa3acb85235b1fd6f71c8f5217415b6f2
```

Red v3 canonical reviewは、Blue repair v2のruntime修正を解消済みとし、唯一のP1を`EAL-074`欠落へ限定している。

同じcurrent HEADには、そのP1を`report.md`一行だけで修正し、次ゲートをfresh Red v4とするBlue repair v3 briefも存在する。

しかしcurrent `report.md`は、S09について次の相互に整合しない記録を保持している。

1. Implementation Delegation Gateは、Red v3を`pending`とし、「fresh Red v3を実行する」と記録している。
2. Delegated Worker Evidenceは、Red v3を`未実施`とし、named branch tipをRed v3へ渡すことを次アクションとしている。
3. Parent Implementation Exceptionは、Red v3を唯一の残ゲートとし、「Run fresh Red v3」と記録している。
4. Reviewer Gate Statusは、freshnessを`fresh v1〜v2 / Blue v2 applied / Red v3 pending`と記録している。
5. Milestone / Commit Candidate Gateは、Red v3がcurrent exact tipで必要であると記録している。

これらは、同じGitHub HEADに存在するRed v3 formal review、Red v3のFAIL/P1=1、Blue repair v3 brief、復元済み`EAL-074`と同時には成立しない。

また、current EALは`EAL-076`で終了し、Red v3 reviewまたはBlue repair v3 briefを採用した行を持たない。 `report.md`自身は、delegated evidenceを実装判断またはcanonical artifactへ取り込む場合はEvidence Adoption Ledgerが必須であり、EALなしで採用を主張してはならないと定めている。

#### 再現手順

1. GitHubで次のrefを取得する。

```text
repository = chemitaro/spec-dock
branch = codex/iss-00354-chatgpt-context-contract
ref = aa019e5d53af171b31845124e15482f78cd0fcb9
```

2. `reviews/red-team-review-s09-v3.md`と`reviews/red-team-review-s09-v3-raw.md`が存在し、Red v3のFAIL/P1=1、reviewed HEAD、Candidate identityを記録していることを確認する。
3. `artifacts/implementation-briefs/s09-red-v3-blue-repair-v3-20260806.md`が存在し、Red v3 findingとfresh Red v4 handoffを記録していることを確認する。
4. `report.md`のEALで`EAL-073`〜`EAL-076`を確認し、`EAL-074`が復元済みであることを確認する。
5. 同じ`report.md`の347、360、373、395、407行を確認する。
6. Red v3が依然として`pending`、`未実施`、`唯一の残ゲート`として記録されていることを観測する。

#### 影響

* current reportが、実行済みformal reviewを未実施として扱っている。
* Red v3のFAIL、唯一のP1、Blue repair v3、current commitの関係がmandatory ledger／current-state上で閉じていない。
* next review identityがfresh Red v4ではなくfresh Red v3として残り、正式なreview lineageが一世代ずれる。
* current commitが主張する「S09 red v3のreport-only同期」と、実際のS09 current-stateが一致しない。
* S09 closureは引き続き成立せず、P0/P1=0のPASS判定はできない。

このfindingはreport/evidence recordの整合性欠陥であり、runtime、tests、profile architecture、S10以降の設計を問題としていない。

---

## 8. 件数・最終判定・未解決リスク

| Severity | 件数 |
| -------- | -: |
| P0       |  0 |
| P1       |  1 |
| P2       |  0 |
| P3       |  0 |

**最終判定: FAIL**

未解決リスクは`RT-354-S09-V4-001`のみである。Red v3 finding `RT-354-S09-V3-001`、0.17 mixed inventory fail-closed、0.17 Reviewer pre-submit block、0.16.1回帰、current commitのreport/evidence-only scopeについて、追加のP0/P1は確認されなかった。

artifact-pending、独立capture option、fallback、retry、generic recoveryのS10以降の事項は本レビューのfinding対象外であり、判定へ含めていない。

---

## 9. Read-only確認

本Red v4レビューでは、次を変更していない。

```text
repository
branch
Candidate
report.md
requirement.md
design.md
plan.md
provider runtime
tests
characterization receipts
implementation briefs
Red v1/v2/v3 canonical/raw reviews
review artifacts
```

添付は検査用に展開しただけであり、repositoryへの書込み、patch、修正版、ZIP、新しいCandidate、Blue向け修正artifactは生成していない。

---

## 10. Model / strategy / verified観測

本Red v4実行について、wrapper由来のmodel selection telemetryは観測できなかった。

```text
model = 未観測
strategy = 未観測
verified = 未観測
```

したがって、`GPT-5.6 Luna`、`Reasoning Effort Max`、その他のmodel／strategy／verified値を本Red v4の観測値として主張しない。
