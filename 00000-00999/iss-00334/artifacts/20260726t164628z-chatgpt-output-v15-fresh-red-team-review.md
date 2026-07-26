# Candidate v15 Fresh Red Team 仕様レビュー — **PASS**

## 1. Review identity と fresh-thread 宣言

| 項目                   | 確認値                                                                                   |
| -------------------- | ------------------------------------------------------------------------------------- |
| 対象Issue              | `init-00322 / epic-00331 / iss-00334`                                                 |
| Logical filename     | `20260726t154840z-iss-00334-issue-planning-candidate-v15.zip`                         |
| External SHA-256     | `07a2c240c9d2edee5faa58f0ad4ab09b05b542dba2e1a8d61234d479c0355fbd`                    |
| Candidate ID         | `iss-00334-v15-20260726t154840z`                                                      |
| Version              | `15`                                                                                  |
| Internal root        | `20260726t154840z-iss-00334-issue-planning-candidate-v15/`                            |
| Repository           | `chemitaro/spec-dock`                                                                 |
| Branch               | `iss-00334-implement-chatgpt-issue-planning-workflow`                                 |
| Source HEAD          | `2e86ec64289ec8102470df75329025d46bbfa51a`                                            |
| Review mode          | Candidate v15専用、fresh independent Red Team、read-only                                  |
| Revision predecessor | `iss-00334-v14-20260726t142121z`, version `14`, disposition `review_failed_unadopted` |

本ReviewはCandidate v15だけを対象とするfresh independent reviewである。v14、旧Candidate、旧Red Team Reviewは、`revision_of` identityおよびMain Admissionのdisposition確認以外の仕様根拠として使用していない。

## 2. Repository／attachment verification

### 2.1 Repository verification

GitHub connectorで次を確認した。

| 検査                      | 結果                                                         |
| ----------------------- | ---------------------------------------------------------- |
| Repository access       | `chemitaro/spec-dock`を取得可能                                 |
| Current branch access   | `iss-00334-implement-chatgpt-issue-planning-workflow`を取得可能 |
| Exact commit access     | `2e86ec64289ec8102470df75329025d46bbfa51a`を取得可能            |
| Branch comparison       | branch HEADと指定exact SHAは`identical`                        |
| Default-branch fallback | 未使用                                                        |
| Exact commit内容          | v14 ReviewとMain Admissionを記録したcommitであることを確認               |

exact HEADから、親Initiative／Epic三文書、ADR 02／03／08／20／21／22、walking-skeleton ADR、Issue decision source、provisional Charter、Main Admission、`report.md` ledger、archive implementationおよび関連testsを確認した。

Main Admissionは、RT-001とRT-003だけを修正対象として採用し、RT-002の恒久same-thread locator／session registry化を明示的に棄却している。 修正境界も、三文書responseからmandatory controls付きimmutable ZIPへのRuntime packaging、create→archive Review direct handoff、および既存archive primitiveの後方互換なbounded extensionに限定されている。

`report.md`では、RT-001／RT-003がv15修正後のfresh Review待ち、RT-002が`resolved/rejected`として記録され、EALでも同じ採否になっている。

`SOURCE-BASELINE.json`については、exact HEADに対して次を追加照合した。

* `git_blob_ledger`の49件すべてについて、pathとGit blob SHAが一致した。
* `planned_new_path_absence_at_source_head`の20件すべてについて、exact HEADで不存在を確認した。
* ledgerは固定件数の完全性主張ではなく、closed authorityと直接影響sourceに限定されている。

### 2.2 Attachment verification

添付ZIPを実際に読み取り、全entryと全payloadを独立検査した。

| 検査                            | 結果                                                                                  |
| ----------------------------- | ----------------------------------------------------------------------------------- |
| 実測external SHA-256            | 指定値と完全一致                                                                            |
| ZIP外形サイズ                      | `42,703` bytes                                                                      |
| Entry数                        | `10` regular files                                                                  |
| Root                          | 指定internal rootだけのsingle root                                                       |
| File mode                     | 全件`100644`、実行bitなし                                                                  |
| Entry type                    | symlink、device、FIFO、socketその他special entryなし                                        |
| Path safety                   | absolute、`..`、backslash、NULなし                                                       |
| Collision                     | duplicate、case-fold collision、NFC collisionなし                                       |
| Encryption／nested archive     | なし                                                                                  |
| Text contract                 | 全payloadがUTF-8 text                                                                 |
| CRC                           | `ZipFile.testzip()`異常なし                                                             |
| Expanded total                | `146,004` bytes                                                                     |
| Largest entry                 | `plan.md`, `74,873` bytes                                                           |
| 最大compression ratio           | 約`5.43`                                                                             |
| 最長UTF-8 path                  | `129` bytes                                                                         |
| Archive limits                | MANIFESTの全ceiling内                                                                  |
| `CHECKSUMS.sha256`            | self-exemptの同fileを除く9件を過不足なく列挙し、全hash一致                                             |
| `MANIFEST.json`               | 10 declared paths、8 payload files、2 control filesが実entryと一致。payload size／SHAも一致     |
| `SOURCE-BASELINE.json`        | repository／branch／HEAD、49件blob ledger、20件planned-absent path、revision metadataを確認   |
| `PLACEHOLDER-ORACLE-MAP.json` | Candidate ID／source HEAD一致。`static-exact-bytes`、dynamic files 0、token definitions 0 |
| 正式文書                          | `requirement.md`、`design.md`、`plan.md`を全文確認                                         |
| 宣言artifact                    | decision snapshot、implementation/test impact map、scope-reset authority traceを全文確認   |
| `revision_of`                 | v14のID、version、filename、SHA、source HEAD、dispositionが提示identityと一致                   |

generic authoring prompt-packの固定root／metadata schemaは、このIssue Candidate ZIPの受入schemaとして使用していない。generic schemaは既存primitiveの後方互換性を評価するためだけに参照した。

Main申告のdeterministic preflight `127/127 PASS`と、上記の独立検査結果に不一致はない。

## 3. RP-01〜RP-07 assessment

### RP-01 — Requirement correctness: **PASS**

親E1-I1は、Issue Planningを単なる三文書生成ではなく、Candidate、Review、Human Gate、採用、検証、publicationを含むwalking skeletonとして要求している。  Candidate v15はこの境界を保持している。

特に`requirement.md`は次を一意に規定している。

* `requirement.md:28, 42–44`: Plannerは三文書responseだけを所有し、Core Runtimeがpackaging／identityを所有する。
* `requirement.md:87`: public final artifactは、三文書と`SOURCE-BASELINE.json`、`MANIFEST.json`、`CHECKSUMS.sha256`、`PLACEHOLDER-ORACLE-MAP.json`を持つimmutable ZIP。
* `requirement.md:87`: version、logical filename、Candidate ID、internal root、source binding、external SHAのfinalizationをRuntimeへ割り当てる。
* `requirement.md:180`: `planning create`のfinal ZIPを変更・再packagingせずarchive Reviewへ渡す。
* `requirement.md:66–69`: mandatory four non-goalsを維持する。
* `requirement.md:95–96`: Semantic complete replacement／Mechanical bounded revisionとnew identity／fresh Reviewを維持する。
* `requirement.md:127, 216`:新しいPlanning DB、receipt registry、custom Git refを禁止する。

Candidate内D-001〜D-024は、exact-head decision synthesis、親文書、accepted ADRと意味上のmaterialな差異を認めなかった。exact-head sourceも、Issue Candidate package、安全検査、dual revision、Human Gate、single lifecycle、derived readiness、assurance／report境界を要求している。

RT-001はRequirementレベルで閉じている。RT-001／RT-003以外のscope ratchetは認めない。

### RP-02 — Design implementability: **PASS**

`design.md:81–109`は二層outputを次のように分離している。

```text
ChatGPTPlannerResponse
- requirement.md
- design.md
- plan.md

RuntimeIssueCandidatePackage
- 上記三文書
- SOURCE-BASELINE.json
- MANIFEST.json
- CHECKSUMS.sha256
- PLACEHOLDER-ORACLE-MAP.json
```

さらに、`design.md:109`でS05をfinal package constructionとCandidate identity finalizationのsole ownerとし、external SHAをarchive close後のZIP外identityとして扱っている。Core RuntimeとS05のownershipは重複していない。

現行`zip_contract.py`はgeneric authoring-packのroot、required metadata、limitsをhard-codeし、`review_pack_input(input_path)`にcontract parameterを持たない。  generic metadataも現在のprompt-pack contractへ固定されている。

これに対し`design.md:254`は、次の最小extensionを明記している。

* data-only `ArchiveReviewContract`
* 引数省略時のexisting generic defaultを完全維持
* generic defaultとIssue Candidate用の二つのnamed contract
* Issue contractはroot、mandatory paths、ceilings、identity fieldsだけを保持
* plugin registry、callback framework、parallel validator、allocator、new state storeを作らない

現行`pack_review.py`のone-argument default callを維持しつつ、新しいIssue Planning application pathからnamed contractを渡せるため、実装可能であり後方互換でもある。

RT-003はDesignレベルで閉じている。

### RP-03 — Plan executability: **PASS**

`plan.md`はS03／S04とS05のownershipを明確に分けている。

* S03: exact Git preflightとcomplete三文書response取得。
* S04: Semantic／Mechanical revision response。
* S05: sole Runtime packaging／identity finalization／Review handoff。
* S06: Human Gate、adoption、parity、publication、derived readiness。

S05のexact target／allowed pathsには、RT-003で必要となった既存pathとfocused compatibility pathsが含まれる。

```text
src/.../application/issue_planning.py
src/.../domain/issue_planning_contracts.py
src/.../domain/authoring_pack/zip_contract.py
src/.../infra/issue_planning_io.py
tests/cli_runtime/test_authoring.py
tests/manual_tests/test_review_chatgpt_authoring_pack.py
tests/unit/infra/test_issue_planning_archive.py
tests/integration/test_chatgpt_planning_fake_oracle.py
```

`plan.md:594–632`は次を独立テストとして閉じる。

* `tc-s05-001`: create final ZIPを無変更でarchive Reviewへ渡す。
* `tc-s05-002`: generic defaultのvalid／wrong-root／missing-metadata／source-mismatch／unsafe statusとfindingを維持する。
* `tc-s05-003`: Issue Candidate identity、inventory、MANIFEST、CHECKSUMS、source baseline、placeholder map、external SHA。
* `tc-s05-004`: unsafe／incomplete Candidateをpartial outputなしで拒否。
* `tc-s05-005`: git-bound exact HEAD／pathsとsilent fallback禁止。

現行generic testにもvalid ZIP、wrong root、path traversal、symlink、encryption、nested archive、binary／non-UTF-8、missing metadata、source mismatchの回帰fixtureが存在する。

依存順、exact allowlist、step gate、stop condition、closure ID、provider→distribution→dogfood順が実装可能な粒度で閉じている。

### RP-04 — Boundary and authority integrity: **PASS**

Candidateは次のauthority boundaryを保持している。

* HumanだけがPlan adoption、implementation start、mergeを決定する。
* Mainだけがcanonical placement、filesystem／Git mutation、commit／push、evidence integrationを所有する。
* Planner responseとRuntime Candidateはadoption前Evidenceである。
* Reviewerはread-onlyであり、patch、replacement document、revised ZIPを生成しない。
* Review PASS単独、Human decision単独、parity単独のいずれもreadinessを成立させない。
* `.assurance.json`、shared delivery／merge／finish policy、current Portfolio、downstream Issueを変更しない。

provisional Charterはnon-authoritativeかつ将来標準への自動適用禁止である。 Main Admissionもsame-thread locator、session registry、new persistent stateの製品要件化を禁止している。

Candidate内にsame-thread locator、session registry、恒久continuation fieldは存在しない。RT-002の再導入は認めない。

### RP-05 — State and lifecycle correctness: **PASS**

Candidateは次を一貫している。

* version `15`の新しいimmutable identity。
* v14を指す完全な`revision_of`。
* existing final targetを上書きしない。
* Candidate bytes変更後はnew identityとfresh Review。
* archive／git-boundのいずれも単一のadoption／publication lifecycleへ収束。
* readinessはEvidenceの論理積から都度導出。
* persistent Planning state、receipt registry、accepted HEAD registry、custom Git refなし。

ADR 08も、persistent stateの追加ではなくGit／canonical evidenceからの導出を要求する。 ADR 20／22のdual transport、revision、content-addressed identityとも整合する。

現在のBlue same-thread運用を恒久product contractと混同していない。

### RP-06 — Test and evidence sufficiency: **PASS**

Issue scopeに比例する必須検証が閉じている。

| 必須検証                                               | Candidate closure                       |
| -------------------------------------------------- | --------------------------------------- |
| create→immutable ZIP→archive Review direct handoff | `tc-s05-001`                            |
| generic default backward compatibility             | `tc-s05-002`＋既存CLI/manual suites        |
| Issue Candidate positive identity／inventory        | `tc-s05-003`                            |
| Issue Candidate unsafe／missing-control negative    | `tc-s05-004`                            |
| git-bound exact identity／no silent fallback        | `tc-s05-005`                            |
| Review read-only                                   | S05 integration＋pre/post mutation guard |
| Human Gate／adoption／parity／publication             | S06                                     |
| PA-NF-01〜PA-NF-10                                  | S06、10/10 reject／violations 0           |
| provider／wheel／sdist／fresh init／update             | S07                                     |
| integrated compatibility                           | S08                                     |
| real Issue dogfood                                 | S09                                     |
| full regression／fresh reviews                      | S99                                     |

generic defaultの既存挙動を保持する検査、Issue固有のpositive／negative、create→Review focused integrationがそれぞれ別の責務として定義されている。巨大proof matrix、全resource matrix、allocator、assurance layer等は追加されていない。

### RP-07 — Human comprehensibility: **PASS**

実装者が次を一意に区別できる。

1. **Planner response:** 三文書だけ。
2. **Runtime final artifact:** mandatory controlsを含むimmutable ZIP。
3. **Review:** exact identityに対するread-only評価。
4. **Human decision:** Reviewとは別のidentity-bound authority。
5. **Adoption／publication:** MainとRuntimeのdeterministic処理。
6. **Readiness:**全gateの論理積から導出される結果。

v14で不明確だった「三文書responseとpublic final ZIPの違い」「packaging owner」「既存archive primitiveの変更path」は、v15では一意に読める。

## 4. Findings table

| ID   | Severity | Category | Authority／violated obligation | Candidate evidence | Material impact | Scope owner | Minimal correction |
| ---- | -------- | -------- | ----------------------------- | ------------------ | --------------- | ----------- | ------------------ |
| 該当なし | —        | —        | materialな未充足義務なし              | RP-01〜RP-07すべてPASS | なし              | —           | なし                 |

Issue-localかつmaterialな`NONCONFORMANCE`、`INTERNAL_CONTRADICTION`、`MISSING_REQUIRED_OBLIGATION`、`UPSTREAM_GAP`、`AMBIGUITY`は認めない。

`IMPROVEMENT`、`FEATURE_REQUEST`、`CLEANUP`として記録すべきnonblocking findingも認めない。

## 5. Finding counts

| Classification | Count |
| -------------- | ----: |
| P0             | **0** |
| P1             | **0** |
| Nonblocking    | **0** |

## 6. Verdict

# **PASS**

Candidate内かつIssue-localでmaterialなP0／P1候補は0件である。

RT-001は、三文書Planner response、S05 Runtime packaging、mandatory control files、identity finalization、create→archive Review direct handoffにより閉じている。

RT-003は、exact `zip_contract.py` path、後方互換なdata-only named contract、generic default regression、Issue-specific positive／negative testsにより閉じている。

RT-002はMain dispositionどおり製品要件へ再導入されていない。

このPASSはfresh Red Teamによる仕様適合判定であり、canonical adoption、Human authorization、implementation start、execution readiness、PR readiness、merge readiness、Issue finishを成立させない。Main Agentが後続のadmission／adoption authorityを保持する。

## 7. Read-only declaration

本Reviewでは、次を変更または生成していない。

* Candidate ZIP
* GitHub repositoryまたはbranch
* canonical Requirement／Design／Plan／report
* patch
* replacement document
* revised ZIP
* downloadable Review artifact

Review outputは本回答本文だけである。

## 8. Assumptions and uncertainties

1. D-001〜D-024の元となった外部v1 ZIPは今回のattachmentおよびexact HEAD上のtracked fileとしては提供されていないため、その外部ZIPとのbyte-for-byte比較は実施していない。Candidate内snapshotを、exact-head decision synthesis、親文書、accepted ADR、Main preflight結果と意味比較し、materialな意味変更がないことを確認した。この制約はVerdictを変更しない。
2. planned implementation filesはexact HEAD時点で20／20不存在であり、Candidateは将来実装の仕様である。したがって本PASSは仕様のcorrectness／implementability／executabilityに対する判定であり、未実装codeや未実行future testsの成功を主張しない。
3. 本Reviewはsource HEAD `2e86ec64289ec8102470df75329025d46bbfa51a`へ限定される。repository／branch／HEAD、親authority、Main disposition、またはCandidate bytesが変化した場合、このReviewはstaleとなりfresh Reviewを必要とする。
4. 上記以外にVerdictへ影響する未確認事項はない。
