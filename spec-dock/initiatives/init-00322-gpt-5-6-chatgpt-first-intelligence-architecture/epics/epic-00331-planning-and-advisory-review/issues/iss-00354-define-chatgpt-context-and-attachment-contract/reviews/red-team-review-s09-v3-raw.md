# SpecDock Issue `iss-00354` — S09 Fresh Red Team 正式レビュー v3

## 1. レビュー結果

| 項目                                           | 結果                                              |
| -------------------------------------------- | ----------------------------------------------- |
| Logical filename                             | `red-team-review-s09-v3.md`                     |
| Candidate version                            | `s09-blue-repair-v2`                            |
| Candidate ID                                 | `iss-00354-s09-blue-repair-v2-20260805T225843Z` |
| Source baseline                              | `ec179c301c045f94d54abea308c47e79d16c5979`      |
| Implementation commit                        | `470cacf5051272edfa71e9780f263d1f402a33a0`      |
| Current report evidence commit / source HEAD | `26d40034507b60f76d06536fb7c5e552bdb49850`      |
| Reviewed repository                          | `chemitaro/spec-dock`                           |
| Reviewed branch                              | `codex/iss-00354-chatgpt-context-contract`      |
| Review mode                                  | Fresh Red Team / read-only / defect-only        |
| Review verdict                               | **FAIL**                                        |
| P0                                           | **0**                                           |
| P1                                           | **1**                                           |
| P2                                           | **0**                                           |
| P3                                           | **0**                                           |

**結論:** `RT-354-S09-V2-001` のコード修正は解消済みである。一方、`RT-354-S09-V2-002` のreport修正は、Red v2正式レビューを採用した必須EAL行 `EAL-074` がcurrent `report.md`から欠落しているため、完全には解消されていない。

---

## 2. GitHub exact identity

確認したexact identityは次のとおりである。

```text
chemitaro/spec-dock
@ codex/iss-00354-chatgpt-context-contract
@ 26d40034507b60f76d06536fb7c5e552bdb49850
```

GitHub Connectorでnamed branch tipと要求source HEADを比較し、次を確認した。

```text
branch_tip = 26d40034507b60f76d06536fb7c5e552bdb49850
requested_head = 26d40034507b60f76d06536fb7c5e552bdb49850
relation = identical
ahead = 0
behind = 0
default_branch_fallback = not used
```

実装・証跡commit chainは次のとおりである。

```text
ec179c301c045f94d54abea308c47e79d16c5979
  └─ 470cacf5051272edfa71e9780f263d1f402a33a0
       S09 Blue repair v2 implementation / tests / evidence

470cacf5051272edfa71e9780f263d1f402a33a0
  └─ 26d40034507b60f76d06536fb7c5e552bdb49850
       report.md-only current-state synchronization
```

`470cacf…` はmixed inventory guardと対応テストを含む実装commitであり、`26d400…` はRed v3待ちのcurrent stateへreportを同期するdocs commitである。

---

## 3. レビュー範囲

### 対象

1. `RT-354-S09-V2-001`

   * 0.17.0 direct authoring ZIP readerの全inventory `kind=file` guard。
   * 共通ZIP helper委譲前のfail-closed。
   * file-only positive。
   * transcript、repository-failure、kind欠落とのmixed inventory全順序。
   * `oracle_artifact_rejected`。
   * helper委譲なし、staging生成なし。
   * 0.16.1 reader、共通helper、追加field、completed-only decoder、profile-owned builders、Reviewer pre-submit blockの回帰確認。

2. `RT-354-S09-V2-002`

   * EAL-073。
   * Delegated Worker Evidence。
   * Reviewer Gate Status。
   * Milestone / Commit Candidate Gate。
   * `ec179c…`、`470cacf…`、`26d400…`のcommit/push済み状態。
   * Red v2 FAIL履歴。
   * fresh Red v3だけを次ゲートとするcurrent state。

### 対象外

S10以降、generic recovery、fallback、retry、artifact-pending、独立capture option、wrapper/API、default branch、アーキテクチャ再設計はレビュー対象外とした。P2/P3の改善提案は行っていない。

---

## 4. 実際に確認した添付ファイル

物理添付 `attachments-bundle.txt` に含まれる次の18論理ファイルを全て読み、GitHub exact HEAD `26d400…` の対応blobと照合した。全18ファイルがbyte-equivalentなGit blob identityで一致した。

`ISSUE_DIR`:

```text
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/
epics/epic-00331-planning-and-advisory-review/issues/
iss-00354-define-chatgpt-context-and-attachment-contract
```

|  # | 確認ファイル                                                                                             | Git blob SHA-1                             |
| -: | -------------------------------------------------------------------------------------------------- | ------------------------------------------ |
|  1 | `ISSUE_DIR/requirement.md`                                                                         | `76ebf016b12abb06f2b5daa544ea7a1421c7471e` |
|  2 | `ISSUE_DIR/design.md`                                                                              | `118e46f905b86883aac9df0f34ebca9e7be2fe91` |
|  3 | `ISSUE_DIR/plan.md`                                                                                | `c553db3d222f5c346c1d15c21f0242cebdee0de4` |
|  4 | `ISSUE_DIR/report.md`                                                                              | `02271f4e2873a0e484f8c470d3d02afaae86953e` |
|  5 | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py` | `5bc79738937e2bf1a2df2e1326852bd1c6b1110d` |
|  6 | `tests/unit/infra/test_issue_planning_oracle_artifact.py`                                          | `0fef26e1965bcc0e19f01111493538f011978a5b` |
|  7 | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py`         | `26819c74d8eaee323cb31ec7241434f42eaf1e65` |
|  8 | `tests/unit/infra/test_issue_planning_chatgpt.py`                                                  | `042d8b2e14016062359c7a674db27e73f1e0c3be` |
|  9 | `ISSUE_DIR/artifacts/characterization/s09-oracle-017-native-rerun-20260806.md`                     | `0bde20e51a9423339a629e876027d02c12c46071` |
| 10 | `ISSUE_DIR/artifacts/characterization/s09-oracle-017-native-inline-20260806.md`                    | `6db586f6d7f0b1e52b8131eb687d529324c8c12f` |
| 11 | `ISSUE_DIR/artifacts/implementation-briefs/s09-oracle-017-profile-20260806.md`                     | `c0f9fb8e06e845177d0ed2aa9ab29809c67c02ee` |
| 12 | `ISSUE_DIR/artifacts/implementation-briefs/s09-oracle-017-profile-inline-20260806.md`              | `f3a6dc1f67b981eabf4c03a6185fa31f94cab534` |
| 13 | `ISSUE_DIR/artifacts/implementation-briefs/s09-red-v1-blue-repair-20260806.md`                     | `08fc236c993985515f329af18ee00eea7a1ed237` |
| 14 | `ISSUE_DIR/artifacts/implementation-briefs/s09-red-v2-blue-repair-v2-20260806.md`                  | `173ad8c749c9f6609b799b1a55450d5a2d0844ba` |
| 15 | `ISSUE_DIR/reviews/red-team-review-s09-v1.md`                                                      | `f339d79c7e9f772b141c7a70af46fad2aa0bbc36` |
| 16 | `ISSUE_DIR/reviews/red-team-review-s09-v1-raw.md`                                                  | `f339d79c7e9f772b141c7a70af46fad2aa0bbc36` |
| 17 | `ISSUE_DIR/reviews/red-team-review-s09-v2.md`                                                      | `3eb9e9416f045530ef45cec3232c67be968218e4` |
| 18 | `ISSUE_DIR/reviews/red-team-review-s09-v2-raw.md`                                                  | `3eb9e9416f045530ef45cec3232c67be968218e4` |

Red v1およびRed v2のcanonical/raw pairは、それぞれ同一blobであり、レビューbytesの変更は確認されなかった。

---

## 5. Red v2 finding再判定

| Red v2 finding      | 再判定                    | 根拠                                                                                                                               |
| ------------------- | ---------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `RT-354-S09-V2-001` | **RESOLVED**           | 0.17 entry pointに全inventory `kind=file` guardが追加され、共通helperより前に実行される。6 mixedケースがdirect reader、両順序、helper非委譲、staging非生成まで固定されている。 |
| `RT-354-S09-V2-002` | **NOT FULLY RESOLVED** | current-state wordingは概ね同期されたが、Red v2正式レビューを採用する必須行 `EAL-074` がcurrent EAL tableから欠落し、Reviewer Gateだけが存在しない`EAL-074`を参照している。     |

---

## 6. Finding

### RT-354-S09-V3-001 — P1: Red v2正式レビューの必須EAL行 `EAL-074` がcurrent reportから欠落している

**Severity:** P1

#### 対象

* `ISSUE_DIR/report.md:55-65`
* `ISSUE_DIR/report.md:140-146`
* `ISSUE_DIR/report.md:394`
* `ISSUE_DIR/artifacts/implementation-briefs/s09-red-v2-blue-repair-v2-20260806.md:480-517`

#### 欠陥

`report.md`自身は、delegated reviewer evidenceを採用する場合、Evidence Adoption Ledgerへの採用記録を必須とし、EALなしでdelegated evidenceの採用を主張してはならないと定めている。

しかしcurrent exact HEADのEAL tableは次の順序になっている。

```text
EAL-073
EAL-075
EAL-076
```

`EAL-074` は存在しない。

一方、Reviewer Gate Statusは次の履歴を存在するものとして参照している。

```text
EAL-073 repair v1
EAL-074 Red v2
EAL-075 Blue v2 brief
EAL-076 implementation evidence
```

したがってReviewer Gateは存在しないEAL recordを参照している。

さらにBlue repair v2 briefは、`EAL-074`を既存のRed v2正式review evidenceとして変更せず保持し、`EAL-075`と`EAL-076`を後続IDとして使用することを明示している。

Red v2 canonical/raw review files自体はGitHubに存在し、Delegated Worker Evidence、Reviewer Gate Status、Milestone GateにもRed v2の`FAIL / P0=0 / P1=2`は記載されている。しかし、必須Evidence Adoption Ledger上の正式な採用行だけが欠落している。

#### 再現経路

1. GitHubで次を取得する。

```text
chemitaro/spec-dock
branch = codex/iss-00354-chatgpt-context-contract
ref = 26d40034507b60f76d06536fb7c5e552bdb49850
path = ISSUE_DIR/report.md
```

2. EAL tableで次を検索する。

```text
| EAL-073 |
| EAL-074 |
| EAL-075 |
| EAL-076 |
```

3. 観測結果:

```text
EAL-073 = present
EAL-074 = absent
EAL-075 = present
EAL-076 = present
```

4. 同じreportのReviewer Gate Statusで次を確認する。

```text
EAL-074 Red v2
```

5. Blue repair v2 briefのAppend-only EAL契約で次を確認する。

```text
既存EAL-074はRed v2正式review evidenceとして変更しない
EAL-075 = Blue repair v2 brief
EAL-076 = Blue repair v2 implementation evidence
```

これらは同時には成立しない。

#### 影響

* Red v2 review bytesは存在するが、report自身が必須とするformal adoption recordがない。
* Reviewer Gate Statusが存在しないEAL IDを参照するため、Red v2 findingの採用・修正・次ゲートへのtraceが閉じない。
* 「Red v2 FAILを歴史として保持し、fresh Red v3だけを残ゲートとする」というV2-002の完了条件を、mandatory ledger semantics上は満たしていない。
* この状態ではfresh Red v3をS09の唯一の残ゲートとしてPASS扱いできない。

#### 最小修正境界

修正対象は **`report.md`のみ** とする。

* EAL tableの`EAL-073`と`EAL-075`の間に、既存Red v2正式レビューを採用する`EAL-074`を復元する。
* 次のidentityを保持する。

  * source: `reviews/red-team-review-s09-v2.md`
  * reviewed HEAD: `ec179c301c045f94d54abea308c47e79d16c5979`
  * verdict: `FAIL`
  * P0=`0`
  * P1=`2`
  * findings: `RT-354-S09-V2-001` / `RT-354-S09-V2-002`
  * canonical/raw evidence identity
  * Blue repair v2へのhandoff
* `EAL-073`、`EAL-075`、`EAL-076`の意味を変更しない。
* Red v1/v2 canonical/raw bytes、runtime、tests、characterization receipts、briefsを変更しない。
* S10以降、generic recovery、capture、fallbackへ変更を広げない。

---

## 7. `RT-354-S09-V2-001` 解消確認

### 7.1 Guard位置

0.16.1 entry pointは従来どおりmetadataを共通helperへ渡す。一方、0.17 entry pointは次の順序になっている。

```text
_read_metadata_0170
→ _require_oracle_0170_file_only_inventory
→ _snapshot_authoring_zip_from_metadata
```

全entryの`kind`が`file`でなければ`oracle_artifact_rejected`となり、共通ZIP helperには進まない。

### 7.2 Mixed inventory test

直接0.17 readerを呼ぶparameterized testは次のcross-productを持つ。

```text
kind:
  transcript
  repository-failure
  missing kind

order:
  unknown entry first
  valid ZIP first
```

合計6ケースすべてで次をassertしている。

```text
error.code == oracle_artifact_rejected
common helper delegation == 0
staging directory does not exist
```

valid file-only ZIPのpositive caseと、`transfer` / `origin`追加fieldの無視も同じtest moduleで固定されている。

### 7.3 回帰確認

| 契約                                | 判定   | 確認内容                                                                                                                       |
| --------------------------------- | ---- | -------------------------------------------------------------------------------------------------------------------------- |
| 0.16.1 reader                     | PASS | 0.16.1 entry pointには0.17専用guardを適用していない。                                                                                   |
| Common ZIP helper                 | PASS | `_snapshot_authoring_zip_from_metadata`の選択・snapshot・ZIP validation処理は維持されている。                                              |
| 追加field無視                         | PASS | valid core schemaに`transfer` / `origin`を追加しても成功する。                                                                         |
| Core field優先                      | PASS | `path`、`sizeBytes`、`sha256`、`validation`の欠陥を追加fieldで上書きできない。                                                               |
| 0.17 completed-only metadata      | PASS | `_read_metadata_0170`は`status == "completed"`以外をrejectする。                                                                  |
| 0.17 completed-only stage decoder | PASS | `"completed"`だけがterminalで、その他はinvalidである。                                                                                  |
| Profile-owned builders            | PASS | 0.16.1と0.17.0は各profileがbrowser、harvest、capture builderを所有し、0.17 harvest/captureはcharacterized builderへ明示bindされている。         |
| Reviewer pre-submit block         | PASS | `review_output_characterized=False`の0.17 reviewerはmanaged Chrome/browser invocation前に`oracle_capability_unsupported`で停止する。 |
| 0.17 review reader                | PASS | registryは0.17 `review_output_characterized=False`を維持している。                                                                  |

`RT-354-S09-V2-001`について新規P0/P1は確認されなかった。

---

## 8. `RT-354-S09-V2-002` の解消済み部分

次のcurrent-state修正自体は確認できた。

* EAL-073は`ec179c…`をcommit/push済みとして記録する。
* Delegated Worker EvidenceはBlue v2 commit `470cacf…`をcommit/push済みとする。
* Reviewer Gate StatusはRed v1、Red v2をそれぞれFAIL履歴として保持し、Blue v2適用後のfresh Red v3を要求する。
* Milestone / Commit Candidate Gateは`ec179c…`と`470cacf…`を実装・証跡commitとして保持し、closure claimを行っていない。
* GitHub current tipはreport-only commit `26d400…`であり、named branchと一致する。

Delegated Worker EvidenceとMilestone Gateのcurrent wordingは、Blue v2が実装・push済みでfresh Red v3待ちであることを正しく表している。

ただし、前記`EAL-074`欠落によりformal evidence historyは閉じていないため、V2-002全体は未解消と判定した。

---

## 9. 仮定・不確実性・未検証主張

### 仮定

判定に影響するmaterialな仮定はない。

### 未検証主張

* 本レビューではpytest、Ruff、Mypy、SpecDock validate、native Oracle/browser smokeを再実行していない。
* reportに記録されたテスト件数とコマンドexitは、current source/testとcommit scopeへ照合したが、独立再実行はしていない。
* ただし`RT-354-S09-V3-001`はcurrent GitHub `report.md`の静的な行欠落と内部参照不整合だけで再現できるため、この未実行事項はfindingまたはverdictへ影響しない。
* `RT-354-S09-V2-001`の解消判定は、exact source、direct-reader tests、baseline/current diffにより確認した。

---

## 10. レビュー後の状態

```text
review_verdict = FAIL
P0 = 0
P1 = 1
P2 = 0
P3 = 0

RT-354-S09-V2-001 = resolved
RT-354-S09-V2-002 = not fully resolved
closure_claim = none
```

* Candidate ZIP、repository、canonical documents、source、tests、review evidenceは変更していない。
* 修正版、パッチ、新規ZIP、設計提案は生成していない。
* S09 closureは未成立のままである。
* `RT-354-S09-V3-001`のreport-only修正を反映した新しいpushed exact HEADには、v3とは別のfresh Red reviewが必要である。
* S10以降、PR、merge、Issue close、Issue finishは引き続き保留対象である。
