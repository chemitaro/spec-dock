# Blue Team 実装ワークパケット — PR #351 current-head P1 repair batch

## 1. Exact GitHub identity と model-selection evidence

**Repository binding: PASS**

| 項目                       | 確認結果                                                                                                        |
| ------------------------ | ----------------------------------------------------------------------------------------------------------- |
| Repository               | `chemitaro/spec-dock`                                                                                       |
| Required branch          | `iss-00334-implement-chatgpt-issue-planning-workflow`                                                       |
| Exact source HEAD        | `c8e1ac2c75502d94d47d097d4a6ee8e63b698a9f`                                                                  |
| Pull request             | `#351`、open                                                                                                 |
| PR head branch           | required branch と完全一致                                                                                       |
| PR head SHA              | exact source HEAD と完全一致                                                                                     |
| Branch comparison        | exact SHA とrequired branchは`identical`、ahead `0`、behind `0`                                                 |
| Default-branch fallback  | 未使用                                                                                                         |
| Observation              | CI成功、Provider CI成功、current decisionは`human_gate`                                                            |
| Review mode              | Blue Team、read-only                                                                                         |
| Active model             | GPT-5.6 Pro                                                                                                 |
| Model-selection evidence | 現在のruntime model identity。Oracle／wrapper model selectorは起動しておらず、別の`requested/resolved/verified` tupleは主張しない |

GitHub connectorでPR #351がopenであり、head branchとhead SHAが上記required identityに一致することを確認した。 Exact commit自体もGitHubから取得できた。

添付current-head observationは、このSHAについてGitHub ActionsのCI／Provider CI成功と`human_gate`を記録し、今回のrepair scopeをP1三件に限定している。P2は明示的にnon-blockingである。 本パケットは添付Blue Team contractのread-only、no-patch、no-ZIP、no-repository-mutation境界に従う。

---

## 2. Scope verdict

| Finding                                             | Exact-head validity | Blue disposition                                               |
| --------------------------------------------------- | ------------------- | -------------------------------------------------------------- |
| P1-A `planning-source-publication-toctou`           | **VALID**           | Review／semantic revisionのCandidate→source→Candidate guardへ限定修正 |
| P1-B `planning-prompt-source-ancestor-symlink-race` | **VALID**           | Prompt sourceだけをrepository descriptor相対で読む                     |
| P1-C `artifact-rules-link-rollback-cas`             | **VALID**           | Atomically証明不能なrollback unlinkを廃止し、replacementを保持              |
| P2 `archive-stale-blocker-vocabulary`               | **OUT OF SCOPE**    | code、test、docsを変更しない                                           |

P2に関係する`dirty_index`、`dirty_untracked`、`staged_changes`、`untracked_files`のclassifierは、本repair batchでは一切触らない。

---

# 3. P1-A — Planning source publication opposite-side TOCTOU

## 3.1 Validity assessment

Exact HEADの両helperは現在、次の順で動作する。

1. Candidateを一度loadする。
2. Candidate identityとexact ZIP bytesを比較する。
3. `_source_evidence_is_current()`を実行する。
4. Source preflightの結果をそのまま返す。

`_review_publication_is_current()`と`_revision_publication_is_current()`の双方がこのorderingである。 添付current sourceも同じ実装を示している。

したがって、source preflightがpassing snapshotを取得した後、return前にCandidate pathを別Candidateへ置換すると、guardは置換後Candidateを再確認せず`True`を返す。Review／revisionは旧Candidate identityに基づく成功を返し得る一方、後続Applyはcurrent pathを再loadしてstaleまたはbinding mismatchとして拒否する。

既存testは逆方向、すなわちCandidate loader中のsource mutationだけを扱い、event orderを`candidate_loader → source_preflight`として固定している。source preflight中のCandidate mutationは未検証である。

**P1-Aはexact HEADに対して有効。**

## 3.2 Smallest bounded repair

共通lockやlinearizable snapshotは現実装に存在しないため、新しいlockを主張しない。修正は既存publication guard内部の**Candidate sandwich revalidation**に限定する。

### Review guard

Candidateが存在する通常経路は次の順序にする。

1. First Candidate load。
2. Captured Candidateとのidentity比較。
3. Captured Candidateとのexact ZIP bytes比較。
4. Final source preflight。
5. Second Candidate load。
6. Candidate identity再比較。
7. Exact ZIP bytes再比較。
8. 全条件成立時だけ`True`。

Candidateまたはpathが`None`である既存branchは、現在どおりsource-state checkだけを行う。公開signatureやoptional semanticsを変更しない。

### Semantic revision guard

次の順序にする。

1. First `current_candidate_loader()`。
2. Identity／ZIP bytes比較。
3. Final source preflight。
4. Second `current_candidate_loader()`。
5. Identity／ZIP bytes再比較。
6. 全条件成立時だけ`True`。

### Private helper

重複を避ける場合だけ、同じmoduleにprivate helperを一つ置く。

責務は次だけとする。

* Candidate loaderを呼ぶ。
* `IssuePlanningCandidateArchiveRejected`、`OSError`、`ValueError`を`False`へ閉じる。
* `identity`と`zip_bytes`だけを比較する。

`files`、`source_baseline`、`onboarding_companion`を新たなequality authorityへ追加しない。

### 明示する限界

この順序は次を保証する。

* Candidate loader中のsource mutationはsource preflightで検出する。
* Source preflight中のCandidate mutationはsecond Candidate loadで検出する。

一方、second Candidate load完了後やguard return後の変更まで原子的に禁止するものではない。これはlockでもtransactionでもlinearizable joint snapshotでもない。

「Candidateとrepository sourceをpublication完了まで原子的に固定すること」が必要と判断された場合は、本P1のbounded ordering repairを停止し、別のcontract／architecture amendmentへ戻す。

## 3.3 Deterministic tests

対象:

* `tests/unit/application/test_issue_planning.py`

### A1. Candidate replacement during source preflight

推奨test:

`test_publication_guard_rechecks_candidate_after_source_preflight`

`revision=False／True`でparameterizeする。

Test fixture:

* First Candidate loadはcaptured identity／ZIPを返す。
* Source preflightはpassing resultを構築する。
* Passing resultをreturnする直前にCandidate stateをreplacementへ切り替える。
* Second Candidate loadはreplacementを返す。

少なくとも次の二variantを持たせる。

| Variant        | Replacement                |
| -------------- | -------------------------- |
| Identity drift | ZIP bytesは同じ、identityだけ異なる |
| ZIP drift      | Identityは同じ、ZIP bytesだけ異なる |

Assertions:

* Guard resultは`False`。
* Event orderは厳密に`candidate_loader → source_preflight → candidate_loader`。
* Source preflightは一回。
* Candidate loaderは二回。
* Guard callbackは例外detailを公開しない。

Old HEADではCandidate loaderが一回なのでRedになる。

### A2. Existing source-side mutation remains closed

現在のsource-mutation testを維持する。

* First Candidate loader中にsource manifestを変更。
* Source preflightが不一致を返す。
* Resultは`False`。
* Second Candidate loadは不要。
* Event orderは`candidate_loader → source_preflight`。

これにより、今回の反対側修正が前回閉じたwindowを再開しないことを固定する。

### A3. No-drift positive

推奨test:

`test_publication_guard_revalidates_candidate_around_source_without_drift`

Review／revision双方で次を確認する。

* First Candidate一致。
* Source evidence一致。
* Second Candidate一致。
* Resultは`True`。
* Event orderは`candidate_loader → source_preflight → candidate_loader`。

### A4. Application result and zero-authoritative-publication

既存application fixtureを使用し、publisher doubleがguardを呼ぶ。

#### Review

Candidate drift時:

* Guardは`False`。
* Publisher doubleは外部fileを書かない。
* Fixed `OSError`を返す。
* Result:

  * `status == "blocked"`
  * `reason == "review_publication_failed"`
  * `output == {}`
  * `details == ()`
* `review_completed`なし。

Exact cleanupを証明できない実publisherでは、Review evidenceがfail-closedに保持されることは許容する。「publication zero」は**successful／authoritative publication outcomeがゼロ**という意味であり、保持された非権威evidenceの物理的不存在を新たに要求しない。Reviewのexisting mappingは変更しない。

#### Semantic revision

Candidate drift時:

* Guardは`False`。
* Publisher doubleはnew Candidateを書かない。
* Existing `PlanningPublicationSourceStale` pathを使用する。
* Result:

  * `status == "stale"`
  * `reason == "revision_source_stale"`
  * `output == {}`
  * `details == ()`

Revision mappingとsuccessful `ok/candidate_revised` contractは維持する。

---

# 4. P1-B — Planning prompt source ancestor symlink race

## 4.1 Validity assessment

`issue_planning_prompt.py`は現在、各canonical／relevant pathについて次を行う。

1. `_safe_source_file(root, relative)`でsymlink／containment／file check。
2. Returned absolute `Path`に対して後続の`read_bytes()`。

この二操作は別のpathname lookupである。 `_safe_source_file()`自身もpath componentのsymlink checkと`resolve(strict=True)`を行った後、resolved `Path`を返している。 添付current sourceにも同じcheck-then-path-readがある。

検証後、`read_bytes()`前にIssue directoryなどのancestorをrenameし、元名へrepository外directoryを指すsymlinkを置くと、後続pathname readはsymlinkをfollowしてoutside bytesをattachmentへ取り込める。

**P1-Bはexact HEADに対して有効。**

## 4.2 Minimal platform-aware repair

変更対象は`synthesize_issue_planning_prompt()`がcanonical／relevant sourceを読む部分だけとする。

### Repository root descriptor

1. `repo_root.resolve(strict=True)`を従来どおり取得する。
2. Rootを次のflagsでopenする。

   * `O_RDONLY`
   * `O_DIRECTORY`
   * `O_NOFOLLOW`
   * `O_CLOEXEC`
3. Open前`lstat`、`fstat`、open後`lstat`のdevice／inode／directory modeを比較する。
4. Root identityが一貫しなければcontent-freeな`ValueError`へ閉じる。

### Descriptor-relative traversal

各relative pathについて、既存のlexical checksを維持する。

* absolute path禁止
* `""`、`.`、`..`禁止
* `.workbench`禁止
* backslash禁止
* credential-like path禁止

その後、root descriptorから各ancestorを順に開く。

Intermediate component:

* `os.open(part, O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC, dir_fd=current_fd)`

Final file:

* `os.open(name, O_RDONLY | O_NONBLOCK | O_NOFOLLOW | O_CLOEXEC, dir_fd=parent_fd)`
* `fstat`がregular fileであることを確認
* `os.read`でdescriptorからbytesを取得

すべてのdescriptorを`finally`で閉じる。

### Existing `_safe_source_file()` seam

最小のRed／Green testを可能にするため、`_safe_source_file()`の既存validationは残してよい。ただし、その返却`Path`をbytes取得のauthorityにしない。

推奨順序:

1. `_safe_source_file()`で既存validation／error compatibility。
2. 元の`relative`を用いてrepository descriptor相対で再open。
3. Bytesはverified final descriptorからだけ読む。

### Relevant byte limits

* Relevant sourceは既存のper-file／total byte limitsを維持する。
* Oversizeはdescriptor read中または直後に既存`ValueError`へ閉じる。
* Canonical三文書へ新しいsize contractを追加しない。
* UTF-8 decode、sensitive scan、private-path scanは現状維持。

### Platform rule

Supported Linux／macOSでは`openat`相当の`dir_fd`、`O_DIRECTORY`、`O_NOFOLLOW`を使う。

これらが利用不能なplatformでは:

* `Path.read_bytes()`へfallbackしない。
* `resolve()`後の再pathname readへfallbackしない。
* Prompt synthesisをfail closedにする。

Linux専用`O_PATH`、`/proc/self/fd`、macOS専用profileやprivate runtime dependencyは追加しない。

## 4.3 Deterministic tests

対象:

* `tests/unit/application/test_issue_planning_prompt.py`
* 必要最小限で`tests/unit/application/test_issue_planning.py`

### B1. Ancestor replacement after validation

推奨test:

`test_prompt_source_ancestor_swap_fails_closed_without_outside_bytes`

Fixture:

1. Repository内にcanonical Issue directoryと三文書を作る。
2. Repository外にmirror directoryを作り、同名`requirement.md`へoutside sentinel bytesを書く。
3. `_safe_source_file()`をwrapperする。
4. Final `requirement.md`のvalidation完了直後に:

   * Original Issue directoryを`.owned`へrename。
   * 元名へoutside mirrorを指すdirectory symlinkを置く。
5. Original `_safe_source_file()` resultを返す。

Old implementation:

* 後続`Path.read_bytes()`がoutside sentinelを読むためRed。

New implementation:

* Ancestorをまだopenしていなければ`O_NOFOLLOW`で拒否。
* Ancestor descriptorを既にopenしていればoriginal directoryから読む。
* Outside sentinelは絶対にattachmentへ入らない。

Assertions:

* Accepted outcomeは次のいずれかだけ:

  * content-free `ValueError`でfail closed。
  * Original repository bytesを読む。
* Outside sentinelがprompt、attachments、exception textにない。
* Attachment name／source labelの変更なし。

Transport-level assertionを加える場合:

* `status == "rejected"`
* `reason == "planning_context_rejected"`
* Backend／Oracle invocation count `0`
* Source evidenceをoutside bytesから生成しない。

### B2. Normal descriptor read

推奨test:

`test_prompt_source_descriptor_read_preserves_names_order_and_bytes`

Assertions:

* Attachment pathsは従来と同じUTF-8 byte sort。
* Canonical／relevant source setは完全一致。
* Attachment text bytesはsource file bytesと一致。
* Duplicate pathの扱いは従来どおりset deduplication。
* Prompt body／output expectationは不変。
* Source pathに対する`Path.read_bytes()`を使用しない。

Current prompt testsのdeterministic ordering／exact bytes expectationsは維持する。

---

# 5. P1-C — Rules link rollback CAS

## 5.1 Validity assessment

Exact HEADの`_rollback_bound_rules_link()`は次の処理である。

1. `rules.md`を`follow_symlinks=False`でstat。
2. `(st_dev, st_ino, st_mode, st_ctime_ns)`をcaptured tupleと比較。
3. 一致すればpathname指定で`os.unlink("rules.md", dir_fd=...)`。

Dogfood projectionも同一blobである。 添付current sourceも同じ実装を示す。

Original symlinkをunlinkした直後にfilesystemが同じinodeを再利用し、observable ctimeも同値となる場合、caller-owned replacementはcaptured tupleと区別できない。Helperはreplacementを自身のlinkと誤認して削除する。

Exact test suiteは`during_create／after_setup`と`wrong／broken／alternate`をparameterizeし、replacementが`rules.md`に残ることを要求している。加えて、ctimeが変わるinode-reuse caseしか直接固定していない。 Observationはordinary suiteで三つの`after_setup` variantが失敗したと報告しているが、本Blue turnでは再実行していない。

**P1-Cはexact HEADに対して有効。**

## 5.2 Smallest provably fail-closed repair

### 結論

Current Linux／Darwin pathname APIと現在のcaptured tupleだけでは、`unlink`対象が操作時点でもcreated symlinkであることをatomicに証明できない。

追加の:

* ctime再確認
* symlink target比較
* birth time
* random name
* extra `stat`
* advisory create lock

だけではownership proofにならない。

したがって、本repairでは `_rollback_bound_rules_link()` の**destructive unlinkをauthorizationしない**。

### Required behavior

`created_rules_identity is None`:

* 何も作成していないためno-op。

`rules.md`が既に存在しない:

* no-op。削除済み扱いを新たなpublic resultへ出さない。

`rules.md`が存在する:

* Captured tupleが一致しても`os.unlink()`しない。
* Current entryを元名のまま保持する。
* Current entryをprivate nameへ移動しない。
* Symlink targetがexpectedと同じでも削除しない。
* Caller-ownedかcreated-ownedかを推測しない。
* Operationは既存のsetup failureへ閉じる。

### Internal disposition

Helper signatureを維持するのが最小である。ただしcallerがcleanup stateを必要とする場合、private return dispositionを追加してよい。

許可する内部値は既存概念だけとする。

* `removed`または`not_created`: entryが既に存在しない場合
* `retained`: entryが存在し、非破壊で保持した場合

新しいpublic status／reason／schemaは追加しない。

Current failure mappingsは維持する。

* `code == "artifact_setup_failed"`
* `publication_state == "not_committed"`
* Publisher invocation `0`

既存error envelopeがcleanup stateを公開する場合、既存値`retained`を使う。新しいcleanup vocabularyを作らない。

### Existing safe rollback preservation

次は変更しない。

* `_rollback_fresh_artifacts_setup()`
* Explicit binary publisherのtemp cleanup
* Artifact directory rollback
* Destination collision handling
* Create lock release handling
* Committed artifact rollback／warning semantics

つまり、今回非破壊化するのは `_rollback_bound_rules_link()` のpathname unlinkだけである。

Exact owned `rules.md`をfailure時に必ず削除することがproduct contractとして必須なら、portable identity-conditioned unlink primitiveが必要になる。その要件が出た場合は本repairを停止し、別のdesign amendmentへ戻す。High-entropy quarantineとcheck-then-unlinkで代用しない。

## 5.3 Deterministic tests

対象:

* `tests/unit/application/test_import_file_artifact.py`

### C1. Existing parameterized replacement test

既存:

`test_fresh_rules_link_replacement_fails_closed_without_deleting_replacement`

を維持し、全六variantをGreenにする。

特に三つの`after_setup` variantで次を確認する。

* `artifact_setup_failed`
* `not_committed`
* Publisher call `0`
* Replacement `rules.md`が元名に残る
* Replacement targetが完全一致
* Artifact binary `0`
* Source bytes不変

### C2. Same identity／same ctime deterministic collision

推奨test:

`test_rules_link_rollback_preserves_same_identity_replacement_without_unlink`

Filesystemの実際のinode reuseに依存させない。

1. Caller-owned replacement symlinkを作る。
2. `created_rules_identity`にreplacementと完全同一のdevice／inode／mode／ctime tupleを渡す。
3. `module.os.unlink`をmonkeypatchし、呼ばれたらtest failureにする。
4. `_rollback_bound_rules_link()`を呼ぶ。

Assertions:

* `os.unlink` call `0`
* Replacement symlinkが同じpathnameに残る
* `readlink()` target完全一致
* Target bytes不変
* Private error detailなし

Current implementationではunlinkを呼ぶためRedになる。

### C3. ctime-difference test

既存:

`test_rules_link_rollback_preserves_reused_inode_replacement_with_new_ctime`

を維持する。

このtestとC2を組み合わせ、rollback safetyがctime precisionやfilesystem generation behaviorに依存しないことを固定する。

### C4. Normal import positive

既存root import positiveで次を再確認する。

* Successful importは従来どおりcommit。
* Expected `rules.md` linkが存在。
* Expected rules sourceへresolve。
* Artifact bytes不変。
* Public result keys／status不変。

### C5. Existing separate safe rollback

`test_fresh_target_name_max_failure_is_precommit_and_rolls_back_setup`など、`_rollback_fresh_artifacts_setup()`を使う既存safe rollback testを変更せずGreenにする。

---

# 6. Exact change surface

## 6.1 Provider authority

| P1 | Provider file                                                                                   | Exact functions                                                                                         |
| -- | ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| A  | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`        | `_review_publication_is_current()`、`_revision_publication_is_current()`、任意のprivate Candidate comparator |
| B  | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py` | `synthesize_issue_planning_prompt()`、`_safe_source_file()`とのread boundary、private descriptor helpers    |
| C  | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_file_artifact.py`  | `_rollback_bound_rules_link()`、必要時だけそのprivate return dispositionと既存call sites                           |

Current provider blobs:

| File                       | Blob SHA                                   |
| -------------------------- | ------------------------------------------ |
| `issue_planning.py`        | `76e766dc1e5cb47adf759a3cab8533a15a4b1da2` |
| `issue_planning_prompt.py` | `63cb4c6f865a9f3d0c562afbb612ae712a2f074a` |
| `import_file_artifact.py`  | `6b39bb18a74cdad1e26754ec7612029725aad044` |

## 6.2 Tests

| Test file                                              | Work                                                                                                    |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| `tests/unit/application/test_issue_planning.py`        | Candidate→source→Candidate guard tests、Review／revision mapping／zero-successful-publication              |
| `tests/unit/application/test_issue_planning_prompt.py` | Ancestor symlink replacement、normal descriptor read、order／bytes parity                                  |
| `tests/unit/application/test_import_file_artifact.py`  | Same-identity rollback preservation、existing six race variants、normal positive／safe rollback regression |

Current test blobs:

* Issue Planning application tests: `b2983b9ae834897f8120445dcae566fe56d23dee`。
* Prompt tests: `aceca521041a0997234b2578c988fab61946fbe8`。
* Artifact import tests: `c51e9c73f2be15d5bc9102952a696723e0d75325`。

## 6.3 Dogfood whole-file projection

Provider完了後、次の三fileをwhole-file projectionする。

* `spec-dock/scripts/spec_dock_runtime/application/issue_planning.py`
* `spec-dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py`
* `spec-dock/scripts/spec_dock_runtime/application/import_file_artifact.py`

Current HEADでは三pairすべて同一blobである。

Rules:

1. Providerを先に編集。
2. Provider focused testsを実行。
3. Dogfoodをwhole-file projection。
4. `cmp`とblob hashでbyte parityを確認。
5. Dogfood側だけの手修正は禁止。

Repositoryのdevelopment rulesもprovider-first editとdogfood inspectionを要求している。

## 6.4 Production non-targets

次を変更しない。

* `application/ports.py`
* `domain/issue_planning_contracts.py`
* Candidate／Review publisher interfaces
* `infra/issue_planning_candidate.py`
* `infra/issue_planning_review.py`
* Oracle adapter
* Prompt resource markdown
* CLI parser／command family／presentation
* Apply transaction
* Review cleanup
* Candidate ZIP schema
* Canonical Requirement／Design／Plan
* Report、assurance、existing evidence artifacts
* P2 classifier

---

# 7. Preserved contracts

## Public behavior

変更しないstatus／reason:

* `ok/review_completed`
* `stale/review_target_changed`
* `blocked/review_publication_failed`
* `ok/candidate_revised`
* `stale/revision_source_stale`
* `blocked/candidate_publication_failed`
* `rejected/planning_context_rejected`
* `rejected/artifact_setup_failed`相当のexisting import envelope

新しいstatus、reason、CLI option、output key、exception type、schema fieldは追加しない。

## Candidate and source identity

維持する。

* Candidate identity
* Exact ZIP bytes
* Repository／branch／HEAD
* Source manifest
* Canonical three-document path set
* Relevant source path set
* Git-bound operation binding
* No default-branch fallback

REQ-003はOracle output後、publication前のsame branch／HEAD／source manifest再検証とdrift rejectionを要求している。

## Prompt protocol

維持する。

* Attachment names
* Attachment order
* Attachment source labels
* Canonical／relevant source set
* Prompt body
* Output expectation
* Exact GitHub connector gate
* Oracle transport boundary

Design上、Prompt本文とreference attachment manifestのownerは`application/issue_planning_prompt.py`であり、Oracle adapterやpublic protocolへ責務を移さない。

## Cleanup

維持する。

* Review cleanupの既存fail-closed behavior
* Unknown objectを削除しない
* Ambiguous cleanupをsuccessful staleへ昇格しない
* Rules replacementを削除しない
* Successful publication pathsは変更しない

---

# 8. Explicit non-goals

* Candidate／sourceのlinearizable joint snapshot
* Repository-wide lock
* New daemon、registry、database、lease service
* Generic filesystem transaction framework
* Prompt protocol redesign
* Oracle configuration変更
* New attachment source
* Canonical document set拡張
* Apply redesign
* Review cleanup再修正
* Rules link generic lifecycle redesign
* `_rollback_fresh_artifacts_setup()`の別race調査
* P2／P3修正
* Historical unresolved thread cleanup
* Merge、auto-merge、Issue close、branch delete、`issue finish`

---

# 9. Verification commands

## 9.1 Focused Red／Green

```bash
uv run pytest -q \
  tests/unit/application/test_issue_planning.py \
  -k 'publication_guard'
```

```bash
uv run pytest -q \
  tests/unit/application/test_issue_planning_prompt.py \
  -k 'source and (ancestor or descriptor or order)'
```

```bash
uv run pytest -q \
  tests/unit/application/test_import_file_artifact.py::test_fresh_rules_link_replacement_fails_closed_without_deleting_replacement \
  tests/unit/application/test_import_file_artifact.py::test_rules_link_rollback_preserves_reused_inode_replacement_with_new_ctime
```

新規same-identity nodeも個別実行する。

```bash
uv run pytest -q \
  tests/unit/application/test_import_file_artifact.py \
  -k 'rules_link_rollback and same_identity'
```

## 9.2 Complete related lane

```bash
uv run pytest -q \
  tests/unit/application/test_issue_planning.py \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/unit/application/test_import_file_artifact.py \
  tests/unit/infra/test_issue_planning_candidate.py \
  tests/unit/infra/test_issue_planning_review.py \
  tests/integration/test_issue_planning_e2e.py
```

## 9.3 Ordinary suite

```bash
uv run pytest -q
```

## 9.4 Lint and type checks

```bash
make lint
```

## 9.5 SpecDock validation

```bash
./spec-dock/scripts/spec-dock validate
```

## 9.6 Diff integrity

```bash
git diff --check
git status --short
git diff --name-only
```

Expected implementation diffは次の九paths以内とする。

```text
src/.../application/issue_planning.py
src/.../application/issue_planning_prompt.py
src/.../application/import_file_artifact.py
spec-dock/.../application/issue_planning.py
spec-dock/.../application/issue_planning_prompt.py
spec-dock/.../application/import_file_artifact.py
tests/unit/application/test_issue_planning.py
tests/unit/application/test_issue_planning_prompt.py
tests/unit/application/test_import_file_artifact.py
```

## 9.7 Provider／dogfood parity

```bash
cmp -s \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \
  spec-dock/scripts/spec_dock_runtime/application/issue_planning.py

cmp -s \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py \
  spec-dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py

cmp -s \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_file_artifact.py \
  spec-dock/scripts/spec_dock_runtime/application/import_file_artifact.py
```

三pairの`git hash-object`も一致させる。

---

# 10. Handoff gates

## Gate A — Implementation admission

実装開始前にCodex Mainが確認する。

* [ ] Current branchがrequired branch。
* [ ] `git rev-parse HEAD`が`c8e1ac2c75502d94d47d097d4a6ee8e63b698a9f`。
* [ ] Worktree／indexがclean。
* [ ] Allowed filesが上記exact change surfaceだけ。
* [ ] P2をrepair instructionsへ含めていない。
* [ ] Provider-first orderをworkerへ明示。
* [ ] Rules rollbackでpathname unlinkを再導入しない。
* [ ] Prompt readでpathname fallbackを追加しない。
* [ ] Publication guardをlockと説明しない。

HEADが変わっていた場合、このpacketをそのまま適用せず、三sourceとtestsを新HEADへ再bindする。

## Gate B — Commit／push admission

Commit前に次をすべて満たす。

* [ ] P1-A mutation／no-drift tests Green。
* [ ] P1-B ancestor swap／normal read tests Green。
* [ ] P1-C six replacement variants＋same-identity test Green。
* [ ] Complete related lane Green。
* [ ] Ordinary pytest Green。
* [ ] `make lint` Green。
* [ ] `spec-dock validate` Green。
* [ ] `git diff --check` Green。
* [ ] Provider／dogfood三pair byte-identical。
* [ ] DiffにP2、Oracle、CLI、domain、publisher、cleanup、canonical docs変更なし。
* [ ] No patch artifact／replacement ZIP／Candidateをrepositoryへ追加していない。

Push後:

* [ ] Remote branch HEADがnew commit SHAと一致。
* [ ] PR #351 headが同じnew SHA。
* [ ] CI／Provider CIをnew SHAへbindして確認。
* [ ] Merge、auto-merge、branch delete、Issue closeを実行しない。

## Gate C — Fresh Red Team

New pushed SHAに対し、新しいread-only Red Team conversationを使用する。

Mandatory review:

1. **P1-A**

   * Review／revision双方がCandidate→source→Candidate。
   * Source preflight中のidentity drift／ZIP driftを検出。
   * Existing source-during-loader testもGreen。
   * No `review_completed`／`candidate_revised` on false guard。
   * Lock／linearizabilityの誤主張なし。

2. **P1-B**

   * Ancestor symlink replacementでoutside bytesを読まない。
   * Source readsはguarded root descriptor相対。
   * Intermediate／final componentでno-follow。
   * Linux／macOS unsupported capabilityはfail closed。
   * Attachment names／order／source set不変。
   * Backend／Oracle call 0 on unsafe source.

3. **P1-C**

   * Same dev／ino／mode／ctimeでもreplacementをunlinkしない。
   * All three `after_setup` variants Green。
   * `os.unlink("rules.md")`によるambiguous destructive rollbackなし。
   * Public error contract不変。
   * Other safe rollback pathsにregressionなし。

4. **Projection**

   * Provider／dogfood三pair同一blob。

5. **Scope**

   * P2 vocabulary findingを本repair verdictへ混入しない。

Fresh Red Team acceptanceは`P0=0`、`P1=0`を必須とする。その後にcurrent-head PR observationを再実行し、new SHAのCIとreview stateを確認してHuman merge gateへ戻す。

---

# 11. Assumptions, uncertainty, and unverified claims

* Attached observationのCI成功、ordinary-suite failure、`human_gate`判定はsource evidenceとして使用したが、本Blue turnではtestを再実行していない。
* P1-A repairはbounded sequential revalidationであり、atomic joint snapshotではない。
* P1-BはPythonのLinux／macOS `dir_fd`＋`O_NOFOLLOW` semanticsを前提とする。Capability不在時はfail closedとする。
* P1-Cについて、current repositoryにはportable identity-conditioned unlink primitiveを確認できない。したがって、replacement preservationを安全側の結論とする。
* Exact owned rules linkのfailure-time removalが新たな必須contractと判明した場合は、推測的なCASを実装せずstop conditionとする。
* Current exact-head sourceと添付三sourceはGit blob SHA単位で一致することを確認したが、本パケットはimplementation correctnessを先取りして保証するものではない。

**Blue Teamはpatch、diff、repository change、branch update、PR update、artifact、ZIP、replacement Candidate、test変更を生成していない。**
