# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a6e6b0e-c388-83ee-b934-721e931e0db3

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

Use the attached Blue Team brief as the task contract. Produce a bounded repair work packet after exact GitHub branch/HEAD verification.

## Answer

# Blue Team 修復ワークパケット — `REVIEW-QUARANTINE-DESTRUCTIVE-TOCTOU`

## 1. Exact repository identity

**Repository binding: PASS**

| 項目                      | 確認結果                                                  |
| ----------------------- | ----------------------------------------------------- |
| Repository              | `chemitaro/spec-dock`                                 |
| Required branch         | `iss-00334-implement-chatgpt-issue-planning-workflow` |
| Source HEAD             | `7ed51a133ab551ed22fd41c5856315256fcaace2`            |
| Pull request            | `chemitaro/spec-dock#351`                             |
| PR state                | open                                                  |
| PR head branch          | required branch と一致                                   |
| PR head SHA             | source HEAD と完全一致                                     |
| Default-branch fallback | 未使用                                                   |
| Provider blob           | `4b13cd2751aa28aacf36c97995f5dd22e9e70d46`            |
| Dogfood projection blob | `4b13cd2751aa28aacf36c97995f5dd22e9e70d46`            |

GitHub connector で repository、required feature branch、PR #351、exact source HEAD の存在と一致を確認した。PR #351 は required branch を head とし、head SHA は `7ed51a...` である。 対象 commit 自体も同 SHA で取得できた。

provider authority と dogfood projection の対象 `issue_planning_review.py` は同一 blob SHA である。

本パケットの task contract は、source HEAD `7ed51a...` を指定した fresh Blue Team brief である。default branch への fallback は認めない。

---

## 2. 単一の bounded P1 objective

修復対象は次の **P1 一件だけ**である。

> `REVIEW-QUARANTINE-DESTRUCTIVE-TOCTOU`

目的は、Review evidence cleanup の各 destructive operation を、操作時点の captured ownership に結合することである。

成立させるべき結果契約は次のとおり。

| Guard outcome                  | Cleanup proof                                          | Result                                                                             |
| ------------------------------ | ------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| `publication_guard() == True`  | cleanup 不要                                             | 従来どおり `ok/review_completed`                                                        |
| `publication_guard() == False` | exact owned children と directory の削除をすべて証明             | `ReviewSourceStale` → `stale/review_target_changed`                                |
| `publication_guard() == False` | identity mismatch、primitive unsupported、削除失敗、fsync失敗など | fixed `OSError("review publication failed")` → `blocked/review_publication_failed` |
| `publication_guard()` が例外      | cleanup 成否にかかわらず                                       | `blocked/review_publication_failed`                                                |
| 任意の cleanup ambiguity          | —                                                      | `ReviewSourceStale` と `review_completed` は禁止                                       |

現行 application は `PlanningPublicationSourceStale` を `stale/review_target_changed` に、通常の `OSError` 等を `blocked/review_publication_failed` に変換する。production application mapping は変更対象にしない。

Fresh Red transcript が報告する blocker はこの destructive-operation race 一件であり、spec／QA の追加 P0/P1 はない。 前回 packet の quarantine-first 方針は、公開名での最終削除 race を移動しただけで、各 `unlink`／`rmdir` 自体を ownership-bound にできていなかった。

---

## 3. 到達可能な race sequence

### 3.1 Child identity-check → unlink

現行 `_remove_evidence_directory_at()` は、quarantine directory の inventory を確認し、両 child を `os.stat()` した後、別ループで同じ pathname を `os.unlink()` する。

具体的な race は次のとおり。

1. Quarantine 内に captured child `planning-review-result.json` があり、device／inode の検証が成功する。
2. 検証後、`os.unlink()` より前に、競合 actor が captured child を quarantine 外の sibling name、例えば `.owned-result` へ移す。
3. 同じ actor が元の `planning-review-result.json` に caller-owned replacement file を作成する。
4. Helper は検証時の情報を保持したまま pathname 指定で `os.unlink("planning-review-result.json")` を呼ぶ。
5. 実際に削除されるのは caller-owned replacement である。
6. 残るもう一方の captured child も削除されると quarantine inventory は空になる。
7. Captured result file は quarantine 外に残っているにもかかわらず、helper は後続の directory removal まで成功して `True` を返し得る。

Guard-false なら、外部証跡を破壊したうえで `ReviewSourceStale` が送出され得る。Guard-exception では最終結果は generic failure でも、caller-owned replacement の削除自体は発生する。

### 3.2 Final directory identity-check → rmdir

1. Captured children の削除後、quarantine directory は空である。
2. `_owned_review_directory_matches()` が、descriptor と quarantine pathname が captured device／inode に一致すると判定する。
3. 判定後、`os.rmdir()` より前に、競合 actor が captured empty quarantine directory を `.owned-directory` へ移す。
4. 元の quarantine name に caller-owned empty replacement directory を作成する。
5. Helper が `os.rmdir(quarantine_name)` を呼び、caller-owned replacement を削除する。
6. Captured empty directory は別名に残るが、helper は親 fsync 後に `True` を返し得る。

現行 regression test は quarantine `fsync` 中、最終 identity verification より前に swap し、replacement を非空にしている。このため、上記 child window と、empty replacement を使う final directory window のどちらも直接再現しない。

---

## 4. Exact change surface

### 4.1 Production provider

| File／function                                                                             | Bounded responsibility                                                           |
| ----------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_review.py` | 唯一の production authority                                                         |
| `publish_planning_review_evidence()`                                                      | single-cleanup-attempt、failure precedence、`ReviewSourceStale` 発生条件を維持            |
| `_remove_evidence_directory_at()`                                                         | check-then-`unlink`／`rmdir` を廃止し、ownership-proof state machine の coordinator に限定 |
| `_rename_no_replace_at()`                                                                 | unknown entry を破壊せず namespace entry を capture する既存 Linux／Darwin primitive として再利用 |
| `_owned_review_directory_matches()`                                                       | observation／revalidation にのみ利用し、後続 pathname deletion の authorization としては使用禁止    |
| `_verify_review_directory_contents()`                                                     | captured child identities の authority を維持                                        |
| New private helper、必要な場合のみ                                                                | atomic conditional removal capability を局所化。public API にはしない                      |

`_remove_evidence_directory_at()` から直接 `os.unlink()`／`os.rmdir()` を呼ぶ構成は廃止する。条件付き削除を実装する private helper が存在する場合も、単なる `stat` と `unlink` の二 syscall wrapper では不適合である。

### 4.2 Tests

| File                                             | Work                                                                                  |
| ------------------------------------------------ | ------------------------------------------------------------------------------------- |
| `tests/unit/infra/test_issue_planning_review.py` | 二つの destructive window × guard-false／guard-exception の deterministic Red/Green tests  |
| `tests/unit/application/test_issue_planning.py`  | cleanup ambiguity と proven stale の既存 result mapping を固定。production application は変更しない |

### 4.3 Dogfood projection

Provider 完了後、次を whole-file projection する。

`spec-dock/scripts/spec_dock_runtime/infra/issue_planning_review.py`

Provider と projection は byte-for-byte 一致を必須とする。projection の先行直接編集は禁止する。

### 4.4 変更しない production surface

次は本 P1 の production change target にしない。

* `application/issue_planning.py`
* `application/ports.py`
* `domain/issue_planning_contracts.py`
* Candidate／apply／Oracle adapter
* Prompt resources
* CLI option／public exception／status／reason／schema
* canonical `requirement.md`、`design.md`、`plan.md`
* onboarding companion bytes

---

## 5. Ownership-bound cleanup state machine

### 5.1 重要な設計判断

**No-replace rename は、安全な「削除」primitive ではなく、安全な「非破壊 capture」primitive としてのみ扱う。**

高エントロピー名は collision 回避には使えるが、ownership proof には使えない。`stat`、`fstat`、directory descriptor、private-looking name のいずれも、その後の別 syscall による pathname deletion を原子的には拘束しない。

削除成功を認めてよい primitive は、次の契約を持つものだけである。

1. 一つの atomic operation として、現在の directory entry identity と expected device／inode／type を比較する。
2. Identity が一致した場合だけ、その exact entry を削除する。
3. Identity mismatch、unsupported、error の場合は、unknown entry を削除しない。
4. 成功／不一致を曖昧に返さない。
5. Advisory lock、秘密名、`stat`＋`unlink` の user-space sequence を atomic proof と称しない。

### 5.2 State machine

| State                       | 意味                                                                                              | 次の許可状態                                                |
| --------------------------- | ----------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| `OWNED_VISIBLE`             | directory descriptor、directory identity、exact child identities を保持                              | `DIRECTORY_CAPTURED` / `PRESERVED_FAILURE`            |
| `DIRECTORY_CAPTURED`        | current name を fresh quarantine name へ no-replace moveし、post-move identity を確認                  | `CHILD_SET_CAPTURED` / `PRESERVED_FAILURE`            |
| `CHILD_SET_CAPTURED`        | 全 child をそれぞれ fresh deletion-candidate name へ no-replace moveし、各 identity を再確認。まだ削除しない          | `CHILD_REMOVAL` / `PRESERVED_FAILURE`                 |
| `CHILD_REMOVAL`             | atomic conditional-remove primitive だけを使用                                                       | `EMPTY_DIRECTORY` / `PRESERVED_FAILURE`               |
| `EMPTY_DIRECTORY`           | 全 child removal success、inventory empty、directory identity、directory fsync を確認                  | `DIRECTORY_DELETE_CAPTURED` / `PRESERVED_FAILURE`     |
| `DIRECTORY_DELETE_CAPTURED` | empty directory の current name を fresh deletion-candidate name へ no-replace moveし、identity を再確認 | `DIRECTORY_REMOVAL` / `PRESERVED_FAILURE`             |
| `DIRECTORY_REMOVAL`         | atomic conditional-rmdir primitive だけを使用                                                        | `CLEANUP_PROVEN` / `PRESERVED_FAILURE`                |
| `CLEANUP_PROVEN`            | exact owned tree removal と parent fsync がすべて成立                                                  | guard-false 時のみ `ReviewSourceStale`                   |
| `PRESERVED_FAILURE`         | mismatch、unsupported、partial failure、fsync failure                                              | fixed publication failure。追加 destructive operation 禁止 |

### 5.3 Required sequence

1. **Initial directory proof**
   Original descriptor の `fstat`、親 descriptor 上の current name、captured device／inode、exact child inventory を再確認する。

2. **Directory capture**
   Existing `_rename_no_replace_at()` で fresh quarantine name へ moveする。Move は unknown entry を削除しない。Move 後に descriptor、pathname、新規 descriptor の identity を照合する。Mismatch なら移動された entry を保持して停止する。

3. **Capture all children before deletion**
   Captured map の exact names だけを対象とする。各 child を fresh deletion-candidate name へ no-replace moveし、移動後の identity を captured device／inode と照合する。
   競合により replacement が move された場合、それを削除せず保持して `PRESERVED_FAILURE` とする。

4. **Exact child destruction**
   Atomic conditional-remove capability が独立に証明されている場合だけ実行する。Capability がない、または対象 filesystem で unsupported なら、captured child も replacement も保持し cleanup failure とする。

5. **No partial-success claim**
   一部の exact child deletion が成功した後に別 child が ambiguous になっても、helper は `True` を返さない。既に安全に削除済みの owned entryについて rollback を主張しない。

6. **Final directory capture**
   Inventory empty と identity を確認した後、直ちに `rmdir` してはならない。Fresh directory-deletion candidate name へ no-replace moveし、post-move identity を再確認する。

7. **Exact directory destruction**
   Atomic conditional-rmdir capability がある場合だけ実行する。Unsupported／mismatch 時は empty directory を保持する。

8. **Durability**
   Exact child removals、exact directory removal、parent fsync の全成功後だけ `CLEANUP_PROVEN` とする。

9. **Single cleanup attempt**
   Existing `cleanup_attempted`／`cleanup_proven` semantics を維持し、guard-false branch と `finally` から二重に destructive cleanup しない。

10. **Failure precedence**
    Published final directory の cleanup が未証明なら、元の guard detailやprivate nameを出さず、外向きには固定された `OSError("review publication failed")` へ閉じる。

### 5.4 Platform limitation

2026年8月2日に確認した Linux man-pages では、`renameat2(RENAME_NOREPLACE)` は destination の非上書きを保証するため、安全な relocation／capture には利用できる。一方、`unlinkat()` は parent descriptor と pathname を受け、定義された flag は `AT_REMOVEDIR` だけであり、expected inodeを条件にした delete interfaceではない。([man7.org][1])

したがって、**Linux の標準 `unlinkat`／`rmdir` sequenceだけでは本 P1 の atomic ownership proof は成立しない**。Darwinについても、現行 source が使用する `renameatx_np(..., RENAME_EXCL)` は no-replace move primitiveであり、この planning passでは identity-conditional unlink／rmdir primitiveを独立確認できていない。

実装上の必須方針は次である。

* Codex が両 supported platformについて atomic conditional-remove primitive、または uncooperative writerを排除する強制的 namespace exclusivity を独立証明できた場合だけ `CLEANUP_PROVEN` branchを有効にする。
* 証明できない platform／filesystemでは、entryを保持し fixed publication failureへ閉じる。
* C／ctypes helper内で `stat` と `unlink` を順番に呼ぶだけでは proof にならない。
* Advisory lock、directory mode変更、秘密名、短い syscall間隔は proof として受理しない。

この制約下で normal guard-false を必ず `stale` に保つ必要があるなら、現在確認できる primitiveだけでは安全性と両立しない。その場合、unsafe deletionで互換性を優先せず、native primitiveの追加または仕様 amendmentを停止条件とする。`ReviewSourceStale` の型と application mapping自体は変更しない。

---

## 6. Deterministic Red／Green tests

### 6.1 Child destructive window

Test名の例:

`test_review_cleanup_child_post_identity_swap_is_fail_closed[false|exception]`

**Injection**

1. `publication_guard` 呼出後だけ race を armする。
2. Quarantine descriptor 上の first captured childに対する identity statを interceptする。
3. Real `stat_result` を取得した後、callerへ返す前に次を行う。

   * Captured childを quarantine外の `.owned-result` へ rename。
   * 元の child nameへ caller-owned replacement bytes を作成。
   * Replacement の device／inode、bytesを記録。
4. 元の captured `stat_result` を callerへ返す。これにより、identity verification完了後、destructive operation直前の状態を決定的に作る。

**Red expectation on `7ed51a...`**

* Unsafe `os.unlink()` が replacement を削除する。
* Guard-falseでは `ReviewSourceStale` が発生し得る。
* Guard-exceptionでは generic failureになるが replacement は失われる。

**Green assertions**

* Replacement inodeが output tree内に残る。Nameが capture用 private nameへ変わっていてもよい。
* Replacement bytesが完全一致する。
* `.owned-result` の captured bytesが残る。
* Race対象を最初の childに固定し、まだ削除していないもう一方の captured childも保持する。
* `_remove_evidence_directory_at()` は cleanup successを返さない。
* Direct infra outcomeは `ReviewSourceStale` ではなく fixed-message `OSError`。
* Guard callback invocation countは一回。
* 追加 destructive cleanup attemptはない。

### 6.2 Final directory destructive window

Test名の例:

`test_review_cleanup_empty_directory_post_identity_swap_is_fail_closed[false|exception]`

**Injection**

1. Guard後だけ raceを armする。
2. Final `_owned_review_directory_matches()` が `True` を返し、directory inventoryがemptyである時点を特定する。
3. Wrapper内で次を行ってから元の `True` を返す。

   * Captured empty quarantine directoryを `.owned-directory` へ rename。
   * 元の quarantine nameへ caller-owned empty replacement directoryを作成。
   * Replacement device／inodeを記録。

**Red expectation on `7ed51a...`**

* `os.rmdir()` が empty replacementを削除する。
* Guard-falseでは cleanup successとなり `ReviewSourceStale` が発生し得る。
* Captured empty directoryは別名で残る。

**Green assertions**

* Replacement directoryの device／inodeが保持される。Capture用 private nameへ移動されていてもよい。
* Captured `.owned-directory` が保持される。
* Cleanup successは返らない。
* Guard-false／guard-exceptionの双方で fixed publication failure。
* `ReviewSourceStale` は発生しない。

### 6.3 Application mapping tests

`tests/unit/application/test_issue_planning.py` では、application-owned publisher doubleを使用する。

**Cleanup ambiguity**

Publisherが `OSError("review publication failed")` を送出する。

Assertions:

* `status == "blocked"`
* `reason == "review_publication_failed"`
* `output == {}`
* `details == ()`
* `review_completed` に相当するpath／digestなし

**Proven stale mapping**

Publisherが `PlanningPublicationSourceStale` を送出する。

Assertions:

* `status == "stale"`
* `reason == "review_target_changed"`
* `output == {}`
* `details == ()`

これにより、`ReviewSourceStale` mappingを維持しつつ、cleanup ambiguityがstructured staleへ昇格しないことを固定する。

### 6.4 Existing regression

次は引き続き Green とする。

* Normal guard-true successful publication
* No-replace publication collision
* Staging directory identity replacement rejection
* Staging child identity replacement rejection
* Output directory identity swap rejection
* Existing quarantine pre-final-check replacement test
* Provider／dogfood whole-file parity

Existing fsync-time testは残してよいが、上記二つの post-identity testsの代替にはしない。

---

## 7. Non-goals and compatibility constraints

本修復では次を変更しない。

* Public status／reason vocabulary、result schema
* `ReviewSourceStale`／`PlanningPublicationSourceStale` の型と application mapping
* Guard-true successful Review publication
* Review result／summary filenames、digest contract
* Candidate ZIP、canonical三文書、onboarding companion bytes
* Exact repository／branch／HEAD binding
* Oracle adapter、fresh Reviewer、closed JSON boundary
* Human decision／apply lifecycle
* Provider-first authorityとdogfood whole-file projection
* Existing output collision behavior
* Prior origin resolution、recursive JSON、publication-completion guard blockers

次は追加しない。

* Daemon、cleanup service、registry、database
* New public API、CLI option、public exception
* Generic filesystem transaction framework
* Persistent tombstone inventory
* Background garbage collection
* Arbitrary directory inventory deletion
* P2／P3 speculative hardening
* Unrelated source、docs、artifacts、ZIPの変更

Requirement は external evidence、closed result、provider-first compatibility、pre-Human immutabilityを要求している。 Design は provider authority、security／privacy、focused verification、projection parityを維持する。 Plan上も、private helperとfocused testの追加は許容される一方、public lifecycleやpublication semanticsの全面再設計は amendment triggerである。

---

## 8. Fresh Red Team acceptance checklist

### Repository binding

* [ ] Repositoryは `chemitaro/spec-dock`。
* [ ] Branchは `iss-00334-implement-chatgpt-issue-planning-workflow`。
* [ ] Reviewed implementation SHAは `7ed51a...` の descendant。
* [ ] PR #351 head SHAとreviewed SHAが一致。
* [ ] Default branch fallbackなし。

### Diff boundary

* [ ] Production変更は provider `infra/issue_planning_review.py` とwhole-file dogfood projectionに限定。
* [ ] Application production、domain、CLI、Oracle、Candidate、applyに不要な変更なし。
* [ ] Testsはfocused infra race testsと必要最小限のapplication mapping testsだけ。
* [ ] 添付artifact、ZIP、canonical三文書を変更していない。

### Destructive-operation proof

* [ ] `_remove_evidence_directory_at()` に check-then-`os.unlink()` が残っていない。
* [ ] `_remove_evidence_directory_at()` に check-then-`os.rmdir()` が残っていない。
* [ ] No-replace renameはcaptureとしてのみ使用される。
* [ ] High-entropy nameをownership proofとして扱っていない。
* [ ] Child deletionの成功はatomic identity-conditional primitiveの成功を含意する。
* [ ] Directory deletionの成功も同じ条件を満たす。
* [ ] Primitive unsupported時にpathname fallbackしない。
* [ ] C／ctypes内の複数 syscall wrapperをatomicと称していない。
* [ ] 一度 ambiguityへ入った後に追加 destructive operationを行わない。
* [ ] Partial cleanupをcleanup successとして扱わない。
* [ ] Parent fsync failureをcleanup successにしない。

### Race evidence

* [ ] Child post-identity swapがold HEADでreplacement deletionを再現する。
* [ ] Empty-directory post-identity swapがold HEADでreplacement rmdirを再現する。
* [ ] 両testがguard-falseとguard-exceptionをそれぞれcoverする。
* [ ] Greenではreplacement inode／bytesが保持される。
* [ ] Child raceではcaptured child bytesと未処理child bytesが保持される。
* [ ] Directory raceではcaptured empty directoryが保持される。
* [ ] Cleanup successが返らない。
* [ ] Guard-false ambiguityで`ReviewSourceStale`が発生しない。
* [ ] Guard-exception detailがpublic resultへ漏れない。

### Result contract

* [ ] Guard true → `ok/review_completed`。
* [ ] Exact cleanup proven＋guard false → `stale/review_target_changed`。
* [ ] Cleanup ambiguity／unsupported＋guard false → `blocked/review_publication_failed`。
* [ ] Guard exception → `blocked/review_publication_failed`。
* [ ] Failure resultは `output == {}`、`details == ()`。
* [ ] Raw exception、absolute path、quarantine／deletion-candidate nameを公開しない。
* [ ] Cleanup attemptは一回だけ。

### Platform and projection

* [ ] Linux capabilityについて syscall-level proofまたはexplicit unsupported evidenceがある。
* [ ] Darwin capabilityについて同様のproofまたはexplicit unsupported evidenceがある。
* [ ] Filesystem-level unsupported resultでunsafe fallbackしない。
* [ ] Provider／dogfood blobまたはbyte comparisonが一致。
* [ ] Focused infra／application tests Green。
* [ ] Related regression、lint、`git diff --check` Green。
* [ ] Fresh Red Teamがexact pushed SHAを再確認する。

### 仮定・不確実性・未検証事項

* Namespace mutatorは、同一 UIDを含む uncooperative writerとして扱う。Advisory lockや秘密名に協力するとは仮定しない。
* Linuxの標準 pathname delete interfaceに、captured inodeを条件とする削除機能は確認できていない。
* Darwinのidentity-conditional unlink／rmdir primitiveは本 planning passでは未確認である。
* 本パケットではrepository、tests、projectionを変更しておらず、test実行も行っていない。
* Atomic conditional-remove capability、両OSでの実挙動、修復後のfull regressionはCodexとfresh Red Teamによる後続検証対象である。

[1]: https://man7.org/linux/man-pages/man2/renameat2.2.html?utm_source=chatgpt.com "rename(2) - Linux manual page"
