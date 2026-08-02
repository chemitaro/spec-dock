# Blue Team 修復ワークパケット — Planning Source Publication TOCTOU

## 1. Exact repository identity

**Repository binding: PASS**

| 項目                        | 確認結果                                                  |
| ------------------------- | ----------------------------------------------------- |
| Repository                | `chemitaro/spec-dock`                                 |
| Required branch           | `iss-00334-implement-chatgpt-issue-planning-workflow` |
| Source HEAD               | `bc7b160b0a710bf799214d0cc5f8d0a34e18672b`            |
| Pull request              | `#351`、open                                           |
| PR head branch            | required branch と完全一致                                 |
| PR head SHA               | required source HEAD と完全一致                            |
| Default-branch fallback   | 未使用                                                   |
| Provider application blob | `92e095827c35254e0ed7db4c5ec1dd13856076bc`            |
| Dogfood application blob  | `92e095827c35254e0ed7db4c5ec1dd13856076bc`            |
| Application test blob     | `bb1629ab880f24f2b57256aab727ea47c4acd0a1`            |

GitHub connectorでrequired branchを直接開き、PR #351のhead branchとhead SHAが指定値に一致することを確認した。 対象commitも同じexact SHAで取得できた。

本パケットは、添付Blue Team promptが指定する一件のP1だけを対象とする。

---

## 2. 結論 — P1はexact HEADに対して有効

**判定: VALID**

Exact HEADの`_review_publication_is_current()`は、現在次の順序である。

1. `_source_evidence_is_current(...)`
2. `candidate_loader(...)`
3. Candidate identityとZIP bytesの比較結果だけを返す

`_revision_publication_is_current()`も同じく、source evidenceを先に確認し、その後で`current_candidate_loader(...)`を呼び、最後はCandidate比較だけを返している。

したがって、次の実行が成立する。

### Review path

1. Publication guardがcanonical source manifestを確認し、`True`相当の状態を得る。
2. `candidate_loader()`がunchanged Candidateを読み取る。
3. Loader実行中、またはCandidate読取り後からloader returnまでの間にcanonical `requirement.md`、`design.md`、`plan.md`のいずれかが変更される。
4. Loaderは元と同じCandidate identity／ZIP bytesを返す。
5. GuardはCandidate比較だけを返すため`True`になる。
6. Review publicationは、既にsource evidenceと一致しないcanonical bytesに対して完了し得る。

### Semantic revision path

1. `_revision_publication_is_current()`がsource evidenceを先に確認する。
2. `current_candidate_loader()`がunchanged Candidateを読み取る間にcanonical sourceが変更される。
3. Candidate identity／ZIP bytesは一致する。
4. Guardは`True`になり、stale source evidenceを持つrevised Candidate publicationを許可し得る。

`run_issue_planning_review()`はこのhelperをpublication guardとしてpublisherへ渡しており、`PlanningPublicationSourceStale`を`stale/review_target_changed`、通常のpublication failureを`blocked/review_publication_failed`、publisher成功を`ok/review_completed`へ変換する。 Semantic revisionも`_revision_publication_is_current()`をpublisherへ渡し、source-staleを`stale/revision_source_stale`へ変換する。

RequirementはOracle output受領後、publication前に同じbranch／HEAD／source manifestを再検証し、driftを`stale`として拒否することを要求している。現行orderingはこのpublication-time保証を、Candidate loader中のsource mutationに対して満たしていない。

---

## 3. 単一のbounded repair objective

修復目的は、次の不変条件を両publication guardで成立させることだけである。

> Guardが`True`を返す場合、current Candidate identity／ZIP bytesがcaptured Candidateと一致し、かつ、そのCandidate読取り・比較が完了した後に実行したsource-state checkもcaptured source evidenceと一致している。

必要なorderingは次である。

1. Current Candidateをloaderから取得する。
2. Candidate identityを比較する。
3. Candidate ZIP bytesを比較する。
4. **その後で**source branch／HEAD／manifestを最終確認する。
5. 全条件成立時だけ`True`を返す。

これはlock、transaction、linearizable snapshotを導入するものではない。Candidate確認とsource確認は依然として逐次処理であり、最終source check後の変更まで原子的に排除したとは主張しない。

本P1が要求するclosureは、**source確認後、Candidate loader中に発生するcanonical mutationを見逃さないこと**である。全namespace／filesystem／Git状態をpublicationまで共通lock下へ置く設計には拡張しない。

---

## 4. 最小の安全な実装変更

### 4.1 `_review_publication_is_current()`

現在先頭にあるsource-state checkを、Candidate validationの後へ移す。

要求する制御順序は次のとおり。

* `candidate`と`candidate_path`の両方が存在する場合:

  1. `candidate_loader(candidate_path, repo_root)`を呼ぶ。
  2. Loader例外は従来どおり`False`。
  3. Identity mismatchは`False`。
  4. ZIP bytes mismatchは`False`。
  5. Candidate一致後に `_source_evidence_is_current(...)` を呼び、その結果を返す。
* Candidate情報が存在しない既存optional branchでは、Candidate checkを省略し、source-state checkを実行してその結果を返す。

Signature、例外allowlist、Candidate比較対象は変更しない。

### 4.2 `_revision_publication_is_current()`

次の順序へ変更する。

1. `current_candidate_loader(candidate_path, repo_root)`
2. Loader例外なら`False`
3. Identity mismatchなら`False`
4. ZIP bytes mismatchなら`False`
5. Candidate一致後に `_source_evidence_is_current(...)`
6. 最終source-state checkの結果を返す

`candidate.source_baseline["relevant_paths"]`からsource pathsを導出する既存契約は維持する。

### 4.3 変更しないもの

* `_source_evidence_is_current()`の入力、preflight request、比較field
* `run_issue_planning_review()`のpost-transport checks
* `run_issue_planning_revise()`のmaterial構築とpre-publication checks
* Publisher interfaceと`publication_guard` signature
* Review evidence cleanup
* Candidate publisher／Review publisherのfilesystem処理
* Public exception、status、reason、schema
* Candidate equalityのfield集合

特にCandidate equalityを`files`、`source_baseline`、`onboarding_companion`まで拡張しない。現行publication guardのauthorityはidentityとexact ZIP bytesであり、本P1はその契約変更を要求していない。

---

## 5. Exact change surface

### Production authority

| File                                                                                     | 対象                                                                                 |
| ---------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py` | `_review_publication_is_current()`と`_revision_publication_is_current()`のorderingのみ |

### Tests

| File                                            | 対象                                                                              |
| ----------------------------------------------- | ------------------------------------------------------------------------------- |
| `tests/unit/application/test_issue_planning.py` | Review／semantic revisionのpublication-guard TOCTOU testsとno-drift positive tests |

### Dogfood projection

| File                                                                | 作業                                                           |
| ------------------------------------------------------------------- | ------------------------------------------------------------ |
| `spec-dock/scripts/spec_dock_runtime/application/issue_planning.py` | Provider修正完了後にwhole-file projectionし、byte-for-byte parityを回復 |

Providerとdogfoodはexact HEADで同一blobである。

Current application test authorityは`tests/unit/application/test_issue_planning.py`であり、exact HEADのblobは`bb1629...`である。

### Production変更を要求しないfiles

* `application/ports.py`
* `domain/issue_planning_contracts.py`
* `domain/issue_planning_candidate.py`
* `infra/issue_planning_candidate.py`
* `infra/issue_planning_review.py`
* Oracle adapter／Prompt resources
* CLI／presentation
* Requirement／Design／Plan／report
* Candidate ZIP／Review evidence／onboarding companion

前回のcleanup修復は再度変更対象にしない。

---

## 6. Deterministic regression tests

Production test hookは追加しない。既存のdependency-injection seamである`candidate_loader`、`current_candidate_loader`、`preflight_runner`、`publisher`だけを使用する。

### 6.1 共通instrumentation

各testはpublication guardが実行される直前に`guard_phase`をarmし、それ以前の初期Candidate loadやpost-transport preflightをevent logから除外する。

Guard phase中は次を記録する。

1. `candidate_loader_enter`
2. `candidate_identity_read`
3. `candidate_zip_bytes_read`
4. `source_preflight`

Loaderが返すcurrent Candidateには、`identity`と`zip_bytes`のproperty accessだけを記録するapplication-owned observing wrapperを使用できる。これにより、単にloaderが呼ばれたことだけでなく、Candidate evidence比較が完了してからsource preflightが実行されたことを証明する。

期待順序は厳密に次とする。

```text
candidate_loader_enter
candidate_identity_read
candidate_zip_bytes_read
source_preflight
```

Old orderingでは`source_preflight`が先頭になるため、deterministicにRedとなる。

### 6.2 Review negative — loader中のcanonical mutation

推奨test名:

`test_review_publication_guard_rechecks_source_after_candidate_loader`

#### Setup

* `git-bound` Reviewを使用する。
* Initial canonical三文書からsource manifestを生成する。
* Valid immutable Candidateとvalid Review JSONを用意する。
* Transport evidenceの`source_manifest_hash`をinitial manifestへbindする。
* Publisher doubleはpublication guardを呼ぶまでfileを書かない。

#### Injection

Guard phaseの`candidate_loader`は次を行う。

1. Real loaderからunchanged Candidateを取得。
2. Candidate取得後、return前にcanonical `plan.md`へ固定bytesを追加する。
3. Candidate observing wrapperを返す。

`preflight_runner`は呼出し時点のcanonical三文書からsource manifestを再構築する。Mutation後のmanifestはtransport evidenceと不一致になる。

#### Expected result

* Publication guardは`False`。
* Publisher doubleはwriteを一度も行わない。
* Current fail-closed Review publication mappingを模擬し、fixed `OSError`を送出する。
* Application result:

  * `status == "blocked"`
  * `reason == "review_publication_failed"`
  * `output == {}`
  * `details == ()`
* Review output directoryは空、またはtest開始時のsentinelだけ。
* `review_completed`は成立しない。
* Event orderはCandidate identity／bytes確認後にsource preflight。
* Old HEAD相当orderingではguardが`True`となるためtestは失敗する。

### 6.3 Review no-drift positive

推奨test名:

`test_review_publication_guard_no_drift_validates_candidate_then_source_and_publishes`

#### Setup

Negative testと同じだが、loaderはcanonical sourceを変更しない。

#### Expected result

* Event orderはloader → identity → ZIP bytes → source preflight。
* Guardは`True`。
* Publisherのpublication side effectはexactly one。
* Resultは`ok/review_completed`。
* Result／summaryのoutput evidenceが存在する。
* Candidate、canonical三文書、source manifestは不変。

このtestにより、修復がsuccessful publicationを常時stale／blockedへ変えていないことを証明する。

### 6.4 Semantic revision negative — current loader中のcanonical mutation

推奨test名:

`test_semantic_revision_publication_guard_rechecks_source_after_current_candidate_loader`

#### Setup

* Existing semantic revision fixtureを使用する。
* P1 findingにbindしたvalid Review evidenceとsemantic revision requestを用意する。
* Valid authoring ZIPからrevision materialを構築する。
* Source evidenceをmutation前manifestへbindする。
* Revised Candidate publisher doubleはguard結果を得るまでfinal ZIPを書かない。

#### Injection

`current_candidate_loader`は次を行う。

1. Unchanged current Candidateを取得。
2. Return前にcanonical `design.md`または`plan.md`を変更する。
3. Candidate observing wrapperを返す。

Final source preflightはmutation後manifestを返す。

#### Expected result

* Publication guardは`False`。
* Publisherは`PlanningPublicationSourceStale`を送出し、final Candidateを書かない。
* Application result:

  * `status == "stale"`
  * `reason == "revision_source_stale"`
  * `output == {}`
  * `details == ()`
* Revised output directoryにnew ZIPはない。
* Old Candidate bytesは不変。
* Event orderはloader → identity → ZIP bytes → source preflight。
* Old orderingではsource checkがmutation前に完了し、guardが`True`になり得るためRedとなる。

### 6.5 Semantic revision no-drift positive

推奨test名:

`test_semantic_revision_publication_guard_no_drift_validates_candidate_then_source_and_publishes`

#### Expected result

* Candidate loader後にCandidate identity／ZIP bytes、最後にsource evidenceを確認する。
* Guardは`True`。
* Publisherはexactly one new Candidateを生成する。
* Resultは`ok/candidate_revised`。
* New Candidate version／identity／ZIP SHA contractは既存どおり。
* Old Candidateは不変。

### 6.6 Review mapping compatibility

小さいmapping-only assertionを追加または既存fixtureへ統合する。

Publisher doubleがpublication side effectなしで`PlanningPublicationSourceStale`を送出した場合:

* `status == "stale"`
* `reason == "review_target_changed"`
* `output == {}`
* `details == ()`

これにより、ordering repairがcurrent fail-closed `blocked/review_publication_failed` mappingだけを残し、既存のproven-stale mappingを誤って削除することを防ぐ。

---

## 7. Result-contract preservation

| Path              | Publisher／guard outcome         | 維持するresult                          |
| ----------------- | ------------------------------- | ----------------------------------- |
| Review            | Guard true、publication成功        | `ok/review_completed`               |
| Review            | Proven source-stale exception   | `stale/review_target_changed`       |
| Review            | Fail-closed publication failure | `blocked/review_publication_failed` |
| Semantic revision | Guard true、publication成功        | `ok/candidate_revised`              |
| Semantic revision | Source-stale exception          | `stale/revision_source_stale`       |

新しいstatus、reason、details codeを追加しない。既存catch orderingも変更しない。

---

## 8. Verification plan

以下はimplementation後にCodexが実行するverification laneであり、本Blue Team turnでは未実行である。

### 8.1 Focused

```bash
uv run pytest -q tests/unit/application/test_issue_planning.py \
  -k 'publication_guard and (review or semantic_revision)'
```

各new testをnode ID指定でも個別実行し、old orderingでRed、新orderingでGreenになることを確認する。

### 8.2 Complete Issue Planning regression

```bash
uv run pytest -q \
  tests/unit/application/test_issue_planning.py \
  tests/unit/application/test_issue_planning_apply.py \
  tests/unit/application/test_issue_planning_prompt.py \
  tests/unit/commands/test_issue_planning.py \
  tests/unit/domain/test_issue_planning_candidate.py \
  tests/unit/domain/test_issue_planning_contracts.py \
  tests/unit/infra/test_issue_planning_apply.py \
  tests/unit/infra/test_issue_planning_candidate.py \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/unit/infra/test_issue_planning_oracle_artifact.py \
  tests/unit/infra/test_issue_planning_review.py \
  tests/unit/presentation/test_issue_planning.py \
  tests/cli_runtime/test_chatgpt_cli.py \
  tests/integration/test_issue_planning_apply.py \
  tests/integration/test_issue_planning_chatgpt_transport.py \
  tests/integration/test_issue_planning_e2e.py
```

### 8.3 Ordinary suite

```bash
uv run pytest -q
```

### 8.4 Lint／type checks

```bash
make lint
```

### 8.5 SpecDock validation

```bash
./spec-dock/scripts/spec-dock validate
```

### 8.6 Diff integrity

```bash
git diff --check
git status --short
```

### 8.7 Provider／dogfood parity

```bash
cmp -s \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \
  spec-dock/scripts/spec_dock_runtime/application/issue_planning.py
```

`cmp` successに加え、両fileのGit blob SHAが一致することを記録する。

---

## 9. Stop conditions／contract ambiguity

次のいずれかが必要になった場合、本P1へ暗黙に取り込まず停止する。

1. **新しいpublic status／reasonが必要になる場合**
   `review_target_changed`、`review_publication_failed`、`revision_source_stale`の既存分類で表現できないなら、仕様判断へ戻す。

2. **Candidateとsourceをpublicationまでatomicに固定する要求が追加された場合**
   現修復はordering correctionでありlockではない。Common lock、transaction、repository snapshot handle等が必要ならarchitecture／contract amendment対象とする。

3. **Candidate equality contractの拡張が必要な場合**
   `identity`／`zip_bytes`以外に`files`、`source_baseline`、companion等をpublication guard authorityへ追加するなら別契約変更である。

4. **Review cleanup semanticsの変更が必要な場合**
   前回のfail-closed cleanup repairを再度開かない。Guard false時のevidence deletion、stale昇格、filesystem primitive変更は本packet外である。

5. **Provider-first projectionが維持できない場合**
   Dogfood fileを先に直接修正せず停止する。

6. **Implementation時のGit HEADが変わった場合**
   Exact pushed HEADを再確認し、source orderingとtest blobを再bindしてから作業する。

---

## 10. Non-goals and compatibility constraints

本修復では次を行わない。

* New lock、mutex、filesystem transaction、Git transaction
* Publisher／cleanup protocolの再設計
* Oracle configuration、transport、Prompt変更
* Candidate ZIP、canonical三文書、companion bytesの変更
* New Candidate generation
* Review JSON／Human decision schema変更
* Public CLI option追加
* Generic source/Candidate snapshot framework
* Registry、database、daemon、persistent state
* Apply lifecycleの変更
* P2／P3 hardening
* Unrelated tests／docs／artifactsの編集

Designはapplicationをexact Git preflightとpublication orchestrationのowner、provider sourceをimplementation authority、root `spec-dock/`をdogfood projectionとしている。 Planも`application/issue_planning.py`とfocused application testsを既存owner surfaceとしている。

---

## 11. Fresh Red Team acceptance checklist

### Exact identity

* [ ] Repositoryは`chemitaro/spec-dock`。
* [ ] Branchは`iss-00334-implement-chatgpt-issue-planning-workflow`。
* [ ] Reviewed HEADは`bc7b160...`のdescendantで、PR #351 headと一致。
* [ ] Default-branch fallbackなし。

### Diff boundary

* [ ] Production変更はprovider application fileの二helperだけ。
* [ ] Dogfoodはprovider後のwhole-file projection。
* [ ] Test変更は`tests/unit/application/test_issue_planning.py`だけ。
* [ ] Infra cleanup、domain、ports、Oracle、CLIに変更なし。

### Guard ordering

* [ ] Review helperはCandidate load／identity／ZIP比較後にsource-state checkを行う。
* [ ] Revision helperも同じordering。
* [ ] Loader failure、identity mismatch、ZIP mismatchはfail closed。
* [ ] Source preflight exception／mismatchはfail closed。
* [ ] Final `True`はCandidate一致かつpost-loader source一致を含意する。
* [ ] Lockまたはatomic snapshotを保持すると主張していない。

### Regression evidence

* [ ] Review loader中source mutationでguard false。
* [ ] Review drift resultはstaleまたはcurrent fail-closed blocked contractに従い、publication 0。
* [ ] Semantic revision loader中source mutationで`stale/revision_source_stale`、new Candidate 0。
* [ ] Negative testsでevent orderがloader → Candidate evidence → source preflight。
* [ ] Review no-driftで`ok/review_completed`。
* [ ] Semantic revision no-driftで`ok/candidate_revised`。
* [ ] Old Candidate不変。
* [ ] Existing Review stale／publication-failed mappingsを維持。
* [ ] Provider／dogfood parity成立。

### Verification

* [ ] Focused tests Green。
* [ ] Complete Issue Planning regression Green。
* [ ] Ordinary pytest Green。
* [ ] `make lint` Green。
* [ ] SpecDock validation Green。
* [ ] `git diff --check` Green。
* [ ] Post-test worktree state確認済み。

---

## 12. 仮定・不確実性・未検証事項

* `candidate_loader`／`current_candidate_loader`の実行中にもcanonical sourceが変化し得る、というconcurrent mutation modelを採用している。
* 本修復はそのloader windowを閉じるが、最終source check後から実際のpublicationまでをatomicに固定しない。
* `/private/tmp/iss-00334-pr351-observation-final-correct/result.json`自体は本環境から確認していない。P1は添付promptの記述と、GitHub exact HEADのsource orderingから独立に有効性を確認した。
* Test、lint、validate、parity commandは本turnでは実行していない。

**Blue Teamはpatch、ZIP、repository change、branch update、PR update、test変更、replacement Candidateを生成していない。**
