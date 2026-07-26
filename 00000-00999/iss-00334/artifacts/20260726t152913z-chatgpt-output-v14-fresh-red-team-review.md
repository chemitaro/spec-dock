# Fresh Red Team 仕様レビュー — **FAIL**

Candidate ZIP自体のidentity、archive safety、inventory、checksum、source bindingには異常を認めませんでした。一方、閉じたbaselineとsource HEADに照らし、Issue-localかつmaterialなP1候補を3件認定します。主因は、①三文書生成からimmutable Issue Candidate ZIPへの変換責務が閉じていないこと、②Semantic Revisionのsame-thread Blue continuityが契約化されていないこと、③既存archive primitive再利用方針とPlanの変更path allowlistが両立しないことです。

## 1. Review identity

| 項目                | 確認値                                                                                                                                                            |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Logical filename  | `20260726t142121z-iss-00334-issue-planning-candidate-v14.zip`                                                                                                  |
| External SHA-256  | `cb7a0a9755d7d172c0bf469d47086f4f090f3bcd117ebd9341cd0a96073c17c8`                                                                                             |
| Candidate ID      | `iss-00334-v14-20260726t142121z`                                                                                                                               |
| Version           | `14`                                                                                                                                                           |
| Internal root     | `20260726t142121z-iss-00334-issue-planning-candidate-v14/`                                                                                                     |
| Repository        | `chemitaro/spec-dock`                                                                                                                                          |
| Branch            | `iss-00334-implement-chatgpt-issue-planning-workflow`                                                                                                          |
| Source HEAD       | `feefb9e8e96015e48cdb1f837e8f775da8b3d8aa`                                                                                                                     |
| Review thread     | Candidate v14専用のfresh independent Red Team review。v13および旧Reviewを仕様根拠として使用していない                                                                                 |
| Revision metadata | v13 `iss-00334-v13-20260726t125220z`、SHA `f5897ae4b1eeb81172e47625053beac609df5108b94a8148fc5592f3affa6349`、disposition `held_unadopted` と一致。履歴metadataとしてのみ確認 |

## 2. Repository and attachment verification

### 2.1 Repository verification

2026年7月27日（JST）にGitHub connectorで対象repositoryを開き、対象branchをexact SHAと比較しました。

* `head=iss-00334-implement-chatgpt-issue-planning-workflow`
* `base=feefb9e8e96015e48cdb1f837e8f775da8b3d8aa`
* 結果: `status=identical`
* `ahead_by=0`
* `behind_by=0`
* `total_commits=0`

したがって、対象branchのHEADは指定されたsource HEADと完全一致しています。default branchへのfallbackは使用していません。exact commitも取得でき、commit identityを確認しました。

暫定Review Charter、親Initiative／Epic、ADR 02／03／08／20／21／22、walking-skeleton ADR、provider runtime、CLI、installer、focused testsに直接関係するsourceを、このexact HEADから参照しました。暫定Charterが定める「閉じたbaseline」「scope ownerを先に判定する」「過去Reviewをauthorityにしない」という順序を適用しています。

### 2.2 Attachment verification

ZIPを一時的なread-only review領域へ実際に展開し、次を独立確認しました。

| 検査                            | 結果                                                                                    |
| ----------------------------- | ------------------------------------------------------------------------------------- |
| 実測SHA-256                     | 指定値と完全一致                                                                              |
| ZIP外形サイズ                      | `38,325` bytes                                                                        |
| Entries                       | `10` regular files                                                                    |
| Single root                   | 指定internal rootだけ                                                                     |
| File modes                    | 全件 `100644`、実行bitなし                                                                   |
| Special entries               | symlink、hardlink相当、device、FIFO、socketを認めず                                             |
| Path safety                   | traversal、absolute path、backslash、NUL、duplicate、casefold collision、NFC collisionなし    |
| Encryption／nested archive     | なし                                                                                    |
| UTF-8                         | 全payloadをUTF-8 textとして読取可能                                                            |
| CRC                           | `ZipFile.testzip()`異常なし                                                               |
| Expanded total                | `132,651` bytes                                                                       |
| Largest file                  | `68,899` bytes                                                                        |
| Longest UTF-8 path            | `129` bytes                                                                           |
| Maximum compression ratio     | 約`5.78`                                                                               |
| `CHECKSUMS.sha256`            | self-exempt以外の9 fileを過不足なく列挙し、全hash一致                                                 |
| `MANIFEST.json`               | declared inventory、payload size、payload SHA、identity、source、revision metadataが実体と一致   |
| `SOURCE-BASELINE.json`        | JSONとして読取可能。source repository／branch／HEADが一致し、直接影響sourceのGit blob SHAをconnector取得値と照合 |
| `PLACEHOLDER-ORACLE-MAP.json` | Candidate/source identity一致。dynamic file／tokenなし。static exact-hash contract           |
| 正式文書                          | `requirement.md`、`design.md`、`plan.md`を全文確認                                           |
| 宣言artifact                    | decision snapshot、implementation/test impact map、scope-reset authority traceを全文確認     |

Main Agent申告のdeterministic preflight `121/121 PASS`は外部Evidenceとして認識しましたが、本レビューはそれだけに依存せず、上記archive検査を独立実施しています。

また、generic authoring prompt-packの固定root／metadata schemaを、このIssue Planning Candidate ZIPの受入schemaとして誤適用していません。現在sourceのgeneric schemaは、後述する実装primitive再利用可能性の確認にだけ使用しました。

## 3. Perspective-by-perspective assessment

### RP-01 Requirement correctness — **FAIL**

親境界、mandatory four non-goals、D-001〜D-024、Human／Main／Planner／Reviewer／Runtimeのauthority、single lifecycle、assurance非変更は概ね正しく保持されています。

ただし、親E1-I1は`Issue Candidate package`をend-to-end責務とし、archive modeのcomplete chainまでを要求しています。 InitiativeおよびADR 20では、Issue Candidate packageに三文書だけでなくsource baseline、manifest、checksumsを含めることが明示されています。

これに対しCandidateの`REQ-004`、`AC-001`、`AC-004`は主に「三文書を返す」ことを要求し、final immutable ZIPへの変換責務を閉じていません。加えてSemantic Revisionのsame-thread Blue continuityがRequirementに存在しません。RT-001、RT-002を認定します。

### RP-02 Design implementability — **FAIL**

thin adapter、provider-first authority、Core Runtime側のdeterministic authority、Oracle側のsession／transport ownershipというlayeringはbaselineと整合しています。ADR 03も、SpecDock側をthin adapterに限定し、Oracle側へsession／reattach／artifact retrievalを委ねています。

一方で、次が実装可能な契約として閉じていません。

* `design.md:240`はcreate outputを「exactly three complete Markdown files plus optional package-only artifacts」とするが、mandatory package controlsを誰が生成するか不明。
* `PlanningRequest`にSemantic Revisionのcontinuation locatorがない。
* 既存safe archive primitiveをextension／reuseするとしながら、Planはそのprimitiveの変更を許可しない。

RT-001〜RT-003を認定します。

### RP-03 Plan executability — **FAIL**

S01→S09→S90→S99の依存順、step gate、focused verification、provider／installer／dogfoodの順序は明確です。

しかし、以下の既知の実装義務にowner stepがありません。

* S03はfake backendから三文書を取得するところでclosureし、archive defaultへ渡せるimmutable ZIPの生成をテストしない。
* S04はcomplete replacementをテストするが、同一Blue thread／Oracle session継続を検査しない。
* S05はarchive safetyを所有するものの、exact sourceで必要となる既存primitive extension pathをallowlistから除外している。

これらは実装中に初めて判明するhypothetical hardeningではなく、exact source HEADから現在確認できる制約です。

### RP-04 Boundary and authority integrity — **PASS**

別findingはありません。

Candidateは次を一貫して保持しています。

* HumanだけがPlan adoption、implementation start、mergeを判断する。
* Mainだけがcanonical placement、Git transaction、evidence integrationを所有する。
* Planner outputはadoption前Evidenceである。
* Reviewerはread-onlyであり、patch、replacement、revised ZIPを生成しない。
* Review、Human decision、parity、validation、publicationを単一authorityへ統合しない。
* `.assurance.json`、shared delivery／merge／finish policy、current Portfolio、downstream Issueへ権限を拡張しない。

clarification、review、execution、assuranceのauthority横取りは認めませんでした。

### RP-05 State and lifecycle correctness — **FAIL**

single adoption/publication lifecycle、Candidate immutability、変更後のnew identity、fresh Review、Red read-onlyは整合しています。

ただし暫定Charterは、Blue Teamがcomplete Candidate revisionを**同一の専用ChatGPT thread**で継続し、Red TeamはCandidate versionごとにfresh threadを用いると明示しています。

CandidateはRed fresh reviewを保持していますが、Semantic Revisionについては「ChatGPT Blue Teamによるcomplete replacement」としか規定せず、同一thread継続を保証するrequest field、continuation contract、fail-closed条件、testがありません。RT-002を認定します。

### RP-06 Test and evidence sufficiency — **FAIL**

CLI、Git preflight、direct argv、Review isolation、Human Gate、PA-NF、installer、provider／installed／dogfood、JIT dogfood、full regressionのテスト面は広く、Issue scopeに対して概ね比例しています。

不足は次の限定された2点です。

1. `planning create`の結果が、そのままarchive Review inputとなるcomplete immutable Candidate ZIPであることを確認するE2Eがない。
2. exact sourceのgeneric archive validatorをIssue Candidate contractへ安全に拡張する実装pathと、それに対応するfocused regressionが閉じていない。

巨大なproof matrix、固定件数ledger、全resource matrix、保証layerの新設は要求していません。

### RP-07 Human comprehensibility — **FAIL**

全体としてauthority、non-goals、failure handling、Human Gateは理解しやすく記述されています。

ただし、人間の実装判断をmaterialに分岐させる以下の点が一意に読めません。

* `planning create`のpublic final artifactは三文書treeなのか、external SHAを持つimmutable ZIPなのか。
* Semantic Revisionはoriginal Blue threadを継続するのか、fresh backend invocationでもよいのか。
* safe ZIP再利用は既存primitiveの変更、private helper利用、新規重複実装のどれを想定するのか。

RT-001〜RT-003の最小修正で解消可能です。

## 4. Findings table

| ID         | Severity | Category                        | Stage     | Authority / violated obligation                                                                                                                                                      | Candidate evidence                                                                                                                                                                                                                                                                     | Material impact                                                                                                                                                                                               | Scope owner                                              | Minimal correction / route / question                                                                                                                                                                                                                                                                                                                                                                     |
| ---------- | -------- | ------------------------------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **RT-001** | **P1**   | **AMBIGUITY**                   | A → B → C | 親E1-I1の`Issue Candidate package`責務、およびInitiative REQ-006／ADR 20の「Issue Candidate = 三文書＋source baseline＋manifest/checksums、archive identity」義務。                                       | `requirement.md:86–87,179–189`は三文書返却を定義。`design.md:81–93`はZIP identityを定義する一方、`design.md:240`はpackage-only artifactsをoptionalとする。`plan.md:332–399`のS03はexternal outputの三文書だけを受入し、MANIFEST／CHECKSUMS／SOURCE-BASELINE／external SHA生成のownerとtestがない。                                      | archive-candidateがdefaultであるにもかかわらず、create outputからReview可能なimmutable archiveへのdeterministic pathが未定義。実装者はraw tree、手動packaging、別command等を任意選択でき、create→Review→Human Gateのproduct chainが分断される。                 | `iss-00334` — `planning create`／Core Runtime packaging   | **必要な質問:** `planning create`のpublic final artifactはcomplete immutable ZIPか、それとも三文書responseを別のdeterministic Runtime stepがpackagingするのか。後者なら、そのstep、control files、identity計算、failure atomicityを誰が所有するか。<br>**最小修正:** ChatGPT responseはexact三文書、Runtime final outputはmandatory controlsを含むimmutable ZIP、と二層を明記し、S03またはS05へpackaging ownerを割り当てる。create結果を直接archive Reviewへ渡してPASSする1本のintegration testを追加する。 |
| **RT-002** | **P1**   | **MISSING_REQUIRED_OBLIGATION** | A → B → C | 暫定CharterのBlue Team same dedicated ChatGPT thread continuity。Redだけをfresh version-specific threadにする役割分離。 ADR 03上、session／reattachはOracle transportの責務であり、SpecDockはそのcontractを薄く利用する。 | `requirement.md:95–96`、`design.md:170–177`はSemantic complete replacementだけを規定。`PlanningRequest`（`design.md:67–79`）にcontinuation locatorがない。`plan.md:488–493`は任意のfake backend complete responseで成功し、original Blue thread reuseを検査しない。`design.md:259`のsame-session記述はtimeout recoveryだけ。 | 実装がSemantic Revisionを新規sessionで開始しても全Candidate testを通過し得る。これにより、admitted findings、Human-approved decision context、Blue revision historyが失われ、同一Blue continuityを前提とするrevision lifecycleを満たせない。                  | `iss-00334` — Planning Skill／`planning revise` transport | `REQ-007`、Revision Request、S04へ「Semantic Revisionはoriginal dedicated Blue sessionをcontinue／reattachする」を追加する。既存Oracle session locatorまたは明示slugを入力として渡し、continuation不能時は新sessionへsilent fallbackせずblocked／Human Relayとする。raw transcript、新DB、session registryは追加しない。fake backend testでoriginal continuation identityの再利用を確認する。                                                                               |
| **RT-003** | **P1**   | **INTERNAL_CONTRADICTION**      | B → C     | D-018、`REQ-019`、`design.md:49,235`はexisting safe ZIP／digest／archive review primitiveのextension／reuseを要求し、同じ安全機能の別subsystem化を禁止する。                                                    | S05のexact target／allowed paths（`plan.md:527–570`）は新規`issue_planning_*` filesとtestsだけで、既存`domain/authoring_pack/zip_contract.py`等の変更を禁止する。exact sourceではvalidator rootが固定`specdock-authoring-pack/`、metadataもgeneric prompt-pack用に固定されている。 ZIP review pathもその固定root／metadataを直接参照する。    | 現Planのallowlistを守ると、実装者はIssue Candidate archive validatorを新fileへ複製するか、generic private implementationへ依存する必要がある。前者はREQ-019違反、後者は脆弱かつCandidate固有root／MANIFEST／CHECKSUMS契約を安全に満たす保証がない。既知のsource制約に対してPlanが実行不能。 | `iss-00334` — S05 archive integrity                      | S05 exact target／allowlistへ、既存`authoring_pack` archive primitiveとfocused regression testの**bounded additive extension**を明示的に追加する。既存default behaviorを保持したままroot、required metadata、limits、Candidate-specific identity validatorをparameter化し、新規並行subsystemを作らない。REQ-022で既に列挙されたmandatory classのfocused negative coverageを同stepで閉じる。                                                                          |

**その他のfinding:** なし。`UPSTREAM_GAP`、`IMPROVEMENT`、`FEATURE_REQUEST`、`CLEANUP`として別途routeすべき項目は認定していません。

## 5. Finding counts

| Severity class | Count |
| -------------- | ----: |
| P0             | **0** |
| P1             | **3** |
| Nonblocking    | **0** |

各severityはRed Teamからの提案です。Finding Admission authorityはMain Agentにあります。

## 6. Verdict

# **FAIL**

Candidate-internalかつIssue-localなP1候補が3件あります。

Archive bytesおよびmetadataの健全性はPASSしていますが、formal verdictはpackage integrityだけでは決まりません。RT-001〜RT-003により、親が要求するarchive-candidate product chain、same-thread Semantic Revision lifecycle、exact sourceに対するshared archive primitive再利用計画がmaterialに閉じていないため、PASS条件を満たしません。

## 7. Read-only declaration

本レビューでは以下を行っていません。

* Candidate ZIPの変更
* GitHub repository／branch／fileの変更
* canonical fileの変更
* patch、修正版、replacement documentの生成
* revised ZIP／new Candidateの生成
* Review結果のdownloadable artifact化
* `.assurance.json`、`report.md`、Git stateの変更

ZIPは検査目的で一時領域へ展開しただけで、元のCandidate bytesは不変です。

## 8. Assumptions and uncertainties

1. 本レビューのP0／P1はRed Team severity proposalであり、Main AgentのFinding Admission前の評価です。
2. same-threadに関するRT-002は、「v14が実際に別threadで作られた」と主張するものではありません。raw transcriptを要求せず、製品契約とS04 testにcontinuity義務がない点だけをfindingとしています。
3. `SOURCE-BASELINE.json`の全entryを構造的に確認し、findingsに直接関係するauthority／runtime／provider filesはexact HEADから取得してblob identityと内容を確認しました。47 entryすべての本文を独立再取得したという主張はしません。
4. Main申告の`121/121 PASS`を同一runnerで再実行してはいません。外部SHA、archive safety、inventory、checksums、manifest payload、placeholder map、source identityは本レビューで独立確認しました。
5. Generic authoring prompt-pack schemaはCandidate v14の受入条件として使用していません。RT-003では、Candidate自身が要求する既存primitive再利用がexact source上で実装可能かを判断するためだけに参照しています。
6. v13 identityと`held_unadopted` dispositionはrevision metadataとしてのみ確認し、v13文書または旧Reviewの主張をbaselineへ混入していません。
