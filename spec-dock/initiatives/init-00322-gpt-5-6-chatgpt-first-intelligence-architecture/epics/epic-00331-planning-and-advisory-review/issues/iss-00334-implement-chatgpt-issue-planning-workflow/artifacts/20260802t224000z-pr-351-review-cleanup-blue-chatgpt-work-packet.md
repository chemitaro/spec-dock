# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a6e6108-f37c-83e8-a123-7a14de41509b

## Prompt

Required repository connector context:
- @GitHub chemitaro/spec-dock
- Current branch: iss-00334-implement-chatgpt-issue-planning-workflow
- Default branch: main
- MUST inspect this GitHub repository with the GitHub connector before answering.
- First inspect the current branch. If the current branch does not exist or cannot be opened, inspect the default branch instead.
- Hard failure condition: if the GitHub connector/app is unavailable, or if the repository, current branch, and default branch cannot be accessed, return immediately with exactly: repository access failed.
- Do not continue from attached files, prompt context, memory, or general knowledge when repository access fails.
- Attached files and prompt-provided context are supplementary only after repository access succeeds.

Use the attached Blue Team brief as the task contract. Produce the bounded repair work packet only after exact GitHub branch/HEAD verification.

## Answer

# Blue Team 修復ワークパケット — `REVIEW-CLEANUP-OWNERSHIP-TOCTOU`

## 1. Exact identity confirmation

**Repository binding: PASS**

| 項目                      | 確認結果                                                  |
| ----------------------- | ----------------------------------------------------- |
| Repository              | `chemitaro/spec-dock`                                 |
| Required branch         | `iss-00334-implement-chatgpt-issue-planning-workflow` |
| Source HEAD             | `d3c72b6b58f301b5609566d7cdb9e94f4d08aa2c`            |
| Pull request            | `#351`、open、head branch一致                             |
| Default-branch fallback | 未使用                                                   |
| Review provider blob    | `e271b6332d9a2794654e4ae4bb1283e6657702c5`            |
| Dogfood projection blob | `e271b6332d9a2794654e4ae4bb1283e6657702c5`            |

PR #351 は対象 feature branch を head とし、PR head SHA は指定された source HEAD と完全一致している。 対象 SHA の commit も GitHub 上で取得できた。

provider authority と dogfood projection の `issue_planning_review.py` は、現 HEAD で同じ blob SHA である。

本パケットは read-only の実装計画であり、repository、添付 artifact、patch、ZIP の変更は行っていない。添付 brief が指定する exact branch／HEAD だけを使用した。

---

## 2. One bounded P1 repair objective

修復対象は、formal Red Team verdict の **P1 1件だけ**である。

> `REVIEW-CLEANUP-OWNERSHIP-TOCTOU`

目的は、Review evidence の stale／failure cleanup において、**captured directory と captured child identities の削除が完了したことを証明できた場合だけ cleanup success とみなす**ことである。名前空間が競合した場合、未知 entry を削除せず、structured stale ではなく既存の content-free publication failure へ閉じる。Red Team は他の spec、QA、P0/P1 finding を報告していない。

要求する結果判定は次のとおり。

| Publication outcome             | Cleanup outcome                             | 既存 result contract                           |
| ------------------------------- | ------------------------------------------- | -------------------------------------------- |
| `publication_guard()` が `True`  | cleanup 不要                                  | `ok/review_completed`                        |
| `publication_guard()` が `False` | exact owned directory の削除を証明                | `stale/review_target_changed`                |
| `publication_guard()` が `False` | rename、identity、unlink、rmdir、fsync のいずれかが曖昧 | `blocked/review_publication_failed`          |
| `publication_guard()` が例外       | cleanup 成否によらず                              | `blocked/review_publication_failed`          |
| その他の publication failure        | cleanup を証明                                 | 既存の collision／publication failure mappingを維持 |
| その他の publication failure        | cleanup が曖昧                                 | `blocked/review_publication_failed`          |

特に、`ReviewSourceStale` は「source が stale だった」という条件だけでは発生させない。**今回作成した exact Review directory の削除完了まで証明できた場合にだけ**発生させる。

---

## 3. Current behavior and reachable race sequence

現行 `publish_planning_review_evidence()` は、final directory の publication と source guard の後、guard が `False` の場合に `_remove_evidence_directory_at()` を呼ぶ。cleanup が `True` を返すと `ReviewSourceStale` を送出し、失敗すると generic `OSError` を送出する。また、未成功のすべての経路で `finally` から同じ cleanup helper を再度呼ぶ。

現行 `_remove_evidence_directory_at()` は次の順序で動く。

1. `evidence.descriptor` と親 directory 上の `evidence.name` が captured device／inode に一致することを確認する。
2. descriptor 上の inventory が captured child names と一致することを確認する。
3. 各 child の device／inode と regular-file 性を確認する。
4. child を captured directory descriptor 相対で unlink する。
5. 親 descriptor 上の `evidence.name` を pathname 指定して `rmdir` する。

最後の `rmdir` の直前には、`evidence.name` の identity revalidation がない。

### Reachable race

1. Review directory `review-…` は directory descriptor、device／inode、二つの child identities とともに captured されている。
2. cleanup helper が `review-…` と二つの child identities を正常に検証する。
3. 競合 actor が captured directory を `review-….owned` などへ rename する。
4. 同じ actor が元の `review-…` に、今回の publication に属さない空の replacement directory を作る。
5. helper は開いた descriptor を使うため、`review-….owned` 側にある captured directory の二つの child を unlink する。
6. `os.rmdir(evidence.name, dir_fd=parent_descriptor)` は、元の名前に置かれた unknown replacement を削除する。
7. helper は `True` を返すが、captured directory 自体は別名で残る。

その結果、guard-false 経路は `stale/review_target_changed` を返し得る一方、実際には unknown replacement が削除され、owned directory が残存する。guard-exception 経路は generic failure になるものの、同じ caller-owned entry の削除が起こり得る。

現行 test suite は、publication 前の staging pathname replacement、captured child replacement、競合のない guard-false cleanup を扱っているが、**identity 検証後から final `rmdir` までの namespace replacement**は注入していない。

---

## 4. Exact provider files/functions and matching dogfood projection

### 変更対象

| Surface                 | 対象                                                                                        | 作業                                                                           |
| ----------------------- | ----------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| Provider authority      | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_review.py` | cleanup ownership protocol の修正                                               |
| Provider functions      | `publish_planning_review_evidence()`                                                      | cleanup outcome と exception classification の一元化、double-cleanup 防止            |
| Provider functions      | `_remove_evidence_directory_at()`                                                         | public name への pathname-only `rmdir` を廃止し、quarantine-first cleanup へ置換       |
| Provider functions      | `_owned_review_directory_matches()`                                                       | pre-move／post-move identity revalidation に継続利用                               |
| Provider functions      | `_verify_review_directory_contents()`                                                     | captured child identities の authority を維持                                    |
| Provider private helper | no-replace rename primitive                                                               | `_atomic_publish_no_replace_at()` と同じ Linux／Darwin syscall boundary を局所的に再利用 |
| Dogfood projection      | `spec-dock/scripts/spec_dock_runtime/infra/issue_planning_review.py`                      | provider 完了後に whole-file projection。byte-for-byte parity 必須                  |
| Infra tests             | `tests/unit/infra/test_issue_planning_review.py`                                          | cleanup-time namespace race の deterministic Red／Green tests                  |
| Application tests       | `tests/unit/application/test_issue_planning.py`                                           | stale と generic publication failure の既存 mapping を直接固定する test のみ              |

### Production editを要求しない surfaces

次の production files は現状の contract をそのまま使用し、今回の修復では変更しない。

* `application/issue_planning.py`
* `application/ports.py`
* `domain/issue_planning_contracts.py`
* `cli/bootstrap.py`
* `infra/issue_planning_candidate.py`
* Oracle adapter、Prompt resources、Candidate／apply code

現在の application mapping は、`PlanningPublicationSourceStale` を `stale/review_target_changed` にし、それより後で `OSError`／`ValueError` を `blocked/review_publication_failed` にしている。この catch order は今回必要な結果 contract と一致している。

新しい public exception、status、reason、gateway method、CLI option は不要である。

---

## 5. Implementation state machine and invariants

### 5.1 Cleanup state machine

| State                   | 意味                                                                                | 許される次状態                                       |
| ----------------------- | --------------------------------------------------------------------------------- | --------------------------------------------- |
| `OWNED_AT_CURRENT_NAME` | descriptor、directory device／inode、二つの child identities を保持                        | `MOVE_ATTEMPTED` または `AMBIGUOUS`              |
| `MOVE_ATTEMPTED`        | 同じ親 descriptor 上で private quarantine name への no-replace atomic move を実行           | `QUARANTINED_VERIFIED` または `AMBIGUOUS`        |
| `QUARANTINED_VERIFIED`  | quarantine name、既存 descriptor、新規 quarantine descriptor が同じ captured directory を指す | `CHILDREN_REMOVED` または `AMBIGUOUS`            |
| `CHILDREN_REMOVED`      | captured 二 child だけを削除し、directory inventory が空                                    | `DIRECTORY_REMOVED` または `AMBIGUOUS`           |
| `DIRECTORY_REMOVED`     | quarantine name の captured directory を削除し、親 directory を fsync                     | `CLEANUP_PROVEN`                              |
| `CLEANUP_PROVEN`        | exact owned object の削除完了を証明                                                       | guard false時だけ `ReviewSourceStale`            |
| `AMBIGUOUS`             | rename、identity、inventory、unlink、rmdir、fsync のどれかを証明不能                            | unknown entryを保持し generic publication failure |

### 5.2 Required sequence

1. **Pre-move revalidation**

   `fstat(evidence.descriptor)`、親 descriptor 上の `stat(evidence.name, follow_symlinks=False)`、captured device／inode、exact inventory、二つの captured child identities を再確認する。

2. **Private quarantine name**

   同じ親 directory 内で、外部へ公開しない高エントロピー名を生成する。既存 staging naming と同程度の entropy を使う。quarantine 名衝突時は、新しい名前を生成して source identity から再検証する。

3. **Atomic parent-relative move**

   `evidence.name` から quarantine name へ、親 descriptor 相対の no-replace rename を行う。

   * Linux: 現在使用している `renameat2(..., RENAME_NOREPLACE)`
   * Darwin: 現在使用している `renameatx_np(..., RENAME_EXCL)`
   * `os.rename()` への overwrite-capable fallbackは禁止
   * syscall／capability が利用不能なら cleanup は未証明として扱う

4. **Post-move directory revalidation**

   quarantine name を `O_DIRECTORY | O_NOFOLLOW` で独立に開き、次の三者が captured device／inode と一致することを確認する。

   * original captured descriptor の `fstat`
   * quarantine descriptor の `fstat`
   * 親 descriptor 上の quarantine name の `stat`

   atomic move が unknown replacement を移動していた場合は、この比較で不一致になる。その entry は unlink／rmdir せず、quarantine name 側に保持して `False` を返す。元 pathname への復元は P1 closure の必須条件ではなく、安全な no-replace identity-checked restore を既存 primitive だけで証明できない限り追加しない。

5. **Post-move child revalidation**

   quarantine descriptor 上で inventory が exact two files だけであることを確認する。

   * `planning-review-result.json`
   * `planning-review-summary.md`

   両方の device／inode、regular-file 性を、`evidence.file_identities` と照合する。全 child の検証を終える前に unlink を開始しない。

6. **Exact child deletion**

   `os.listdir()` の結果をそのまま削除対象にしてはならない。削除するのは captured map にある上記二つの exact names だけとする。各 unlink 直前にも quarantine descriptor 相対で identity を再確認する。

7. **Directory deletion**

   child deletion 後に quarantine directory を fsyncし、inventory が空であることと quarantine directory identity を再確認する。`rmdir` の対象は **quarantine nameだけ**とし、元の public `evidence.name` を再利用しない。成功後に親 descriptor を fsyncする。

8. **Cleanup result**

   helper が `True` を返してよいのは、atomic move、post-move identity、child identity、exact child unlink、quarantine `rmdir`、親 fsync がすべて成功した場合だけとする。それ以外は `False`。

9. **Single cleanup attempt**

   `publish_planning_review_evidence()` は explicit stale cleanup と `finally` cleanup の二重実行を避ける。少なくとも `cleanup_attempted` と `cleanup_proven` に相当する private state を保持し、一つの failure outcomeにつき destructive cleanup attempt は一回だけにする。

10. **Failure precedence**

    staging 作成後の通常 exception が存在していても、cleanup が曖昧なら、その曖昧さを優先して fixed-message `OSError` にする。cleanup を証明できた場合だけ元の collision／validation exception を維持する。

### 5.3 Safety invariants

1. 元の public evidence name を pathname-only で `rmdir` しない。
2. quarantine 移動後に captured identity が一致しない object は一切 unlink／rmdir しない。
3. arbitrary directory inventory を反復して削除しない。
4. `ReviewSourceStale` は exact owned cleanup の完了証明を含意する。
5. cleanup ambiguity は常に `review_publication_failed` を含意する。
6. unknown replacement の bytes／inode は保持する。必要なら private quarantine name に残す。
7. `review_completed` は final identity／content verificationと guard `True` の後だけ成立する。
8. quarantine name、raw exception text、private pathを public resultへ出さない。
9. provider と dogfood は whole-file byte parity を維持する。
10. callback invocation count、normal collision、normal successful publication、result SHA contractは変更しない。

---

## 6. Deterministic Red/Green tests

### 6.1 Infra race tests

対象: `tests/unit/infra/test_issue_planning_review.py`

#### A. `test_review_guard_false_cleanup_namespace_swap_preserves_unknown_entry`

**Injection**

* `publication_guard` が呼ばれた時点で `cleanup_armed=True` にし、`False` を返す。
* `_owned_review_directory_matches()` を monkeypatch する。
* cleanup 中に original helper が初めて `True` を返した直後、wrapper 内で以下を実施する。

  1. captured `evidence.name` を `<name>.owned` へ parent-fd-relative rename。
  2. 元の `evidence.name` に空の unknown replacement directory を作成。
  3. replacement の device／inode を記録。
  4. caller へ元の `True` を返す。

これにより「identity check 完了後、cleanup operation 開始直前」の race を deterministic に再現する。production test hookは追加しない。

**Red expectation on `d3c72b6…`**

* `ReviewSourceStale` が発生する。
* replacement device／inode が消える。
* displaced owned directory は残るが、二つの child が削除される。

**Green assertions**

* `ReviewSourceStale` ではなく fixed-message `OSError`。
* replacement の device／inode が output directory 内のいずれかの entryとして残る。元名でも quarantine 名でもよい。
* `<name>.owned` は残り、二つの exact child と元 bytes が保持される。
* cleanup helper は cleanup success を返していない。
* `PublishedPlanningReview` は返らない。
* `review_completed` を示す成功 evidence は生成されない。

#### B. `test_review_guard_exception_cleanup_namespace_swap_preserves_unknown_entry`

同じ race injectionを使用し、`publication_guard` は distinct `RuntimeError` を送出する。

**Green assertions**

* public-facing classification は generic publication failure。
* direct infra exception は固定された `OSError` であり、`ReviewSourceStale` ではない。
* replacement device／inode が残る。
* displaced owned directory と二 child bytes が残る。
* guard例外の内容を result output／detailsへコピーしない。

### 6.2 Quarantine protocol test

#### C. `test_review_cleanup_removes_only_quarantined_captured_directory`

競合なしの guard-false publicationを instrument し、次を確認する。

* final public nameから private quarantine nameへの no-replace move が、child unlinkより先に行われる。
* `rmdir` の対象は private quarantine nameだけ。
* 元の final public nameを `rmdir` しない。
* unlink対象は captured two namesだけ。
* cleanup後に final name、quarantine name、staging nameが残らない。
* unrelated sentinel entryは不変。
* resultは従来どおり `ReviewSourceStale`。

既存 `test_review_publication_guard_false_removes_only_new_directory` は残し、private quarantine residue 0 の assertion を追加してよい。

### 6.3 Application mapping tests

対象: `tests/unit/application/test_issue_planning.py`

#### D. `test_review_cleanup_ambiguity_maps_to_review_publication_failed`

application-owned publisher double が cleanup ambiguity相当の `OSError` を送出する。

Assertions:

* `status == "blocked"`
* `reason == "review_publication_failed"`
* `output == {}`
* `details == ()`
* `review_completed`、review file paths、digest fieldがない

#### E. `test_review_proven_cleanup_source_stale_mapping_is_unchanged`

publisher double が `PlanningPublicationSourceStale` を送出する。

Assertions:

* `status == "stale"`
* `reason == "review_target_changed"`
* `output == {}`
* `details == ()`

これにより、infra race testが「ambiguity → `OSError`」を証明し、application testが「`OSError` → content-free blocked result」を証明する。

### 6.4 Existing tests that must remain Green

* atomic no-replace successful publication
* staging directory name replacement rejection
* staging child identity replacement rejection
* output-directory identity swap rejection
* normal guard-false owned cleanup
* external Review result bounded／symlink／parent-swap safety

現行 tests の staging-name replacement と child replacementは、今回の final-cleanup race testの代替にはならないため、削除・置換しない。

---

## 7. Non-goals and compatibility constraints

本修復では次を変更しない。

* public status／reason set
* `PlanningCommandResult` schema
* `ReviewSourceStale`／`PlanningPublicationSourceStale` public behavior
* `publication_guard` signatureと invocation timing
* Candidate ZIP、canonical三文書、onboarding companion bytes
* Candidate identity、reviewed identity、Human decision binding
* exact repository／branch／HEAD gate
* default-branch fallback禁止
* Oracle configuration／adapter boundary
* provider-first authorityとdogfood whole-file projection
* successful Review publication filenames、digest、inventory
* output collisionの通常挙動
* create／revise／apply publication logic

次の前回 blockers は再度変更対象にしない。

* apply origin resolution の content-free `github_upstream_required`
* recursive JSON failure の `invalid JSON` 正規化
* Create／Review／Revise publication-completion source guard
* Review successful publication の staging／final identity binding

Requirement は exact Git binding、closed result vocabulary、repository外 evidence、provider-first projectionを要求している。 Design は既存 publication／Human authority／Oracle boundaryの維持と、局所的な infra repairを要求している。 Plan上も、shared lifecycleやpublic contractの変更は amendment triggerであり、今回の一件には含めない。

daemon、registry、database、新public API、generic filesystem framework、cleanup service、P2/P3 hardening、添付 artifactの編集は行わない。

---

## 8. Acceptance checklist for the next fresh Red Team review

### Repository binding

* [ ] Review対象は `chemitaro/spec-dock`。
* [ ] Branchは `iss-00334-implement-chatgpt-issue-planning-workflow`。
* [ ] Implementation HEADは `d3c72b6…` の descendant。
* [ ] PR #351 head SHAとreviewed SHAが一致。
* [ ] default branch fallbackなし。

### Diff boundary

* [ ] Production変更は provider `infra/issue_planning_review.py` とその dogfood projectionに限定。
* [ ] application production contract、ports、domain schema、Oracle、Candidate、applyに不要な変更なし。
* [ ] test変更は focused infra／application mappingに限定。
* [ ] source code、tests、projection以外の attached evidenceを編集していない。

### Ownership and cleanup proof

* [ ] captured directoryは削除前に private quarantine nameへatomic no-replace moveされる。
* [ ] moveは親 descriptor 相対である。
* [ ] post-move directory identityを captured descriptor、新規 quarantine descriptor、quarantine pathnameの三者で確認する。
* [ ] post-move child inventoryと二つの child identitiesを再確認する。
* [ ] arbitrary child deletionがない。
* [ ] `rmdir` は quarantine nameだけを対象にする。
* [ ] 元の public nameに現れた replacementを削除しない。
* [ ] cleanup ambiguity時に unknown entryを保持する。
* [ ] cleanup ambiguity時に `ReviewSourceStale` を送出しない。
* [ ] cleanup ambiguity時に `review_completed` を返さない。
* [ ] explicit cleanupと`finally` cleanupの二重 destructive attemptがない。
* [ ] directory／parent fsync failureは cleanup successにしない。

### Result mappings

* [ ] raceなし guard false → `stale/review_target_changed`。
* [ ] raceあり guard false → `blocked/review_publication_failed`。
* [ ] guard exception → `blocked/review_publication_failed`。
* [ ] guard true →従来どおり `ok/review_completed`。
* [ ] cleanup ambiguity resultの `output == {}`、`details == ()`。
* [ ] fixed public resultにraw exception、quarantine name、absolute pathがない。

### Regression evidence

* [ ] guard-false race testが旧 HEADでRed、新 HEADでGreen。
* [ ] guard-exception race testが旧 HEADでRed、新 HEADでGreen。
* [ ] replacementの device／inodeが削除されていない。
* [ ] displaced captured directoryの二 child bytesが、ambiguous cleanup時に保持されている。
* [ ] normal stale cleanup後に staging／final／quarantine residue 0。
* [ ] provider／dogfood `cmp` が一致。
* [ ] Linux `renameat2(RENAME_NOREPLACE)` pathを実行。
* [ ] Darwin `renameatx_np(RENAME_EXCL)` pathを実行。
* [ ] `tests/unit/infra/test_issue_planning_review.py` Green。
* [ ] focused application mapping tests Green。
* [ ] `git diff --check`、lint、関連full regression Green。

### 根拠・仮定・未検証点

本パケットの根拠は、exact PR headのGitHub source、formal Red Team transcript、添付 Blue Team brief、canonical Requirement／Design／Planである。Linux／Darwinのno-replace syscallを引き続きsupported boundaryとすることを仮定している。

この planning passではrepositoryの実行、test実行、syscall fault injection、CI確認は行っていない。したがって、両OSでの syscall behavior、focused／full regression、修復後 provider→dogfood byte parityは、implementation agentと次のfresh Red Teamが exact pushed SHAで独立検証する必要がある。
