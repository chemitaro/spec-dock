---
種別: 要件定義書（Epic）
ID: "epic-00332"
タイトル: "Analysis Guided Issue Execution and Per Issue Delivery"
関連GitHub: ["chemitaro/spec-dock#332"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-23"
親: ["init-00322"]
candidate_semantic_key: "issue-execution-and-per-issue-delivery"
canonical_path: "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00332-issue-execution-and-per-issue-delivery/requirement.md"
---

# epic-00332 Analysis Guided Issue Execution and Per Issue Delivery — 要件定義（何を、なぜ行うか）

## 1. Epic Outcome

Main／Executor／Humanが、承認済みIssue PlanからArchitecture-Aware Execution Brief、bounded implementation、Checkpoint／Repair、Issue Delivery Review、dedicated PR、external gates、Human merge、reviewed HEAD確認、Issue finishまでを一つのActor Journeyとして完了できる。

## 2. Scope

- Architecture-Aware Execution BriefのPrompt、semantic Artifact retrieval、status、Workbench candidate、adoption、freeze、stale handling。
- 一つのcustom Executorによるbounded implementation／verification。
- limited read-only specialists、Issue Gradeとmodel／reasoning routingの分離。
- Execution Unit、Checkpoint Review、Repair Batch、Final Completion Summary、Issue Delivery Review。
- dedicated Issue PR、CI、ChatGPT Delivery Review、GitHub Codex Review、blocking repair、merge-prepared、Human merge、reviewed HEAD確認、Issue finish。
- tests、docs、provider／installed／dogfood projection、Representative Real-Use Validation。

## 3. Non-scope

- Multi-Issue Epic coordination、Epic Delivery Review、Epic finish。
- aggregate Epic PR。
- Planning Candidate authoring／Portfolio materialization。Issue execution consumes only an adopted Issue Plan。
- 自動merge、hidden Git transaction、複数write Agent。

## 4. Requirements

| ID | Requirement |
|---|---|
| E2-REQ-001 | Mainがapproved Issue PlanのExecution Unitを選び、exact GitHub HEADへbindしたArchitecture-Aware Execution BriefをChatGPTで生成できる。 |
| E2-REQ-002 | ChatGPTが関連Artifact、code、tests、configuration、repository conventionsを意味的に探索し、Applicable Concern、Evidence Used／Gaps、test／implementation strategy、stop conditionsを返す。 |
| E2-REQ-003 | Briefは`ready | planning-gap | insufficient-evidence`を返し、`ready`だけをIssue Artifactへcontent-preservingに配置・freezeする。 |
| E2-REQ-004 | maintained official pathのwrite roleを`executor`一つ、read-only closed setをbuilt-in `explorer`とcustom `researcher`,`consultant`,`deep-consultant`へ限定する。provider authority=`src/spec_dock/assets/install_root/.codex/agents/`、dogfood=`.codex/agents/`、installed=`<install-root>/.codex/agents/`とし、built-in `explorer`のoverride fileを禁止する。allowlist外roleを起動・維持しない。 |
| E2-REQ-005 | ExecutorはBrief／Repair内のbounded implementationとverificationを所有し、commit／push／stash／force／mergeを行わない。 |
| E2-REQ-006 | Issue Gradeをmodel／reasoningの自動routingへ使用せず、Mainが必要時だけ明示overrideする。 |
| E2-REQ-007 | MainがExecution Unit、明示semantic BASEからcurrent HEADまでのCheckpoint Review、P0／P1 Repair Batch、same-Executor repair loopを制御する。BASE ancestryを解決できなければ`insufficient-evidence`とする。 |
| E2-REQ-008 | 全Execution Unit完了後、Issue実装開始時の明示semantic BASEからcurrent HEADまでのFinal Completion SummaryとIssue Delivery Reviewを実行し、mutation frontierとIssue Contract全体の双方を評価する。 |
| E2-REQ-009 | Issue Delivery Review PASS後、同じIssueのdedicated PRを作成し、PR target baseとPR HEADのmerge-baseからPR HEADまでを対象にCI、ChatGPT Delivery Review、GitHub Codex Reviewを観測する。 |
| E2-REQ-010 | PR上のP0／P1またはrequired CI failureだけをRepair Batchで修復し、新HEADでfresh gatesを再観測する。 |
| E2-REQ-011 | merge-preparedでHumanへ停止し、Human merge後にreviewed HEAD一致を確認してIssue finishする。 |
| E2-REQ-012 | P2／P3だけではbranch mutation、再CI、再Reviewを行わない。 |
| E2-REQ-013 | Brief、implementation、tests、必要なdocs／configを同じcandidate commitへ含め、Briefだけの先行commitを標準にしない。 |
| E2-REQ-014 | provider／installed／dogfoodでAgent、Skill、Workflow、Prompt、Artifact lifecycleの責務parityを維持する。 |
| E2-REQ-015 | Execution Brief、Repair Batch、Executor Handoff、Operator Context、GitHub外file、Workbench、Artifact、report evidenceへsensitive dataを含めない。Executor／adapter／helper processはdirect argvをdefaultとし、shell例外はHuman-approved Design、固定template、input validation／encoding、injection regression evidence、明示的rollback mechanism／trigger、tested rollback evidenceをすべて必要とする。 |
| E2-REQ-016 | 各代表Issue run終了時にBrief finding、first Checkpoint result、failure cycle／手戻り、tool call／探索／handoff proxy、Human intervention、wall-clockを記録し、E3-I3の比較評価へhandoffする。 |
| E2-REQ-017 | Issue Executionはpositive Human Issue Plan Adoption Gateを通過したadopted canonical Issue Planだけを入力とする。archive modeではfresh Planning Review PASS、exact logical Candidate filename／ZIP SHAへbindされたHuman authorization、deterministic canonical adoption、candidate-to-canonical parity、required validation／planning publicationを、git-bound modeではfresh Planning Review PASS on exact reviewed HEAD／exact target paths、同identityへbindされたHuman authorization、exact reviewed-content canonical／commit parity、required validation／planning publicationをすべて満たさなければExecutorを開始しない。archive Candidate Review PASSまたはgit-bound Review PASSだけでexecution-readyを主張しない。 `PA-NF-01` archive Review PASS only、`PA-NF-02` git-bound Review PASS only、`PA-NF-03` Human Gate only、`PA-NF-04` parity only、`PA-NF-05` wrong logical Candidate filename／Candidate SHA、`PA-NF-06` wrong reviewed HEAD／exact target paths、`PA-NF-07` source drift、`PA-NF-08` semantic mutation during adoption、`PA-NF-09` parity failure、`PA-NF-10` validation／planning-publication failureを相互に独立した必須negative fixtureとして拒否し、どれか1件でも該当する場合は`execution-ready`／Executor startを禁止する。 E2-I1 consumerは10／10 PASS、violations 0を必要とする。 |
| E2-REQ-018 | Checkpoint、Issue Delivery、PR-style ReviewはGit-bound modeでsemantic BASE／merge-base、reviewed HEAD、CI、current Contract Ownerを評価し、Planning Candidate ZIPを代替Evidenceとして使用しない。 |
| E2-REQ-019 | canonical Issue Planning文書のsemantic correctionが必要な場合はnew Issue Planning Candidateへ戻し、mechanical correctionだけがclosed diffでlocal edit／commit／push／Git-bound Reviewを使用できる。 |

## 5. Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| E2-AC-001 | representative IssueをPlanからBrief、Executor、Checkpoint、Repair、Issue Delivery Review、dedicated PR、external gates、Human merge、reviewed HEAD確認、finishまで一つのIssue／PRで完走できる。 |
| E2-AC-002 | `ready` BriefだけがArtifactへ昇格し、`planning-gap`／`insufficient-evidence`ではExecutorを開始しない。 |
| E2-AC-003 | provider／installed／dogfoodのexact agent setがwrite=`executor`、read-only=`explorer`,`researcher`,`consultant`,`deep-consultant`と一致する。missing、extra、renamed、write-capable誤設定、built-in explorer override、allowlist外起動、Issue Grade routingをtestが拒否する。 |
| E2-AC-004 | Issue Gradeがmodel／reasoning自動routingへ影響しない。 |
| E2-AC-005 | Executor／adapterのhidden commit／push／stash／force／mergeが0。 |
| E2-AC-006 | Checkpoint／Issue Deliveryは明示semantic BASEからcurrent HEAD、PR-styleはmerge-baseからPR HEADを用い、P1をRepair Batchで解消して新HEADのfresh Review PASSへ進める。BASE／ancestry不明時はPASSしない。 |
| E2-AC-007 | P2／P3だけではbranch mutationが発生しない。 |
| E2-AC-008 | Human merge前にIssue finishせず、merge後に最終reviewed HEAD一致を確認する。 |
| E2-AC-009 | Briefと対応実装が同じcandidate commitに含まれる。 |
| E2-AC-010 | provider／installed／dogfood parityとrepresentative E2EがPASSする。 |
| E2-AC-011 | sensitive-data fixtureがBrief／Repair／Handoff／Artifact／reportへ残らず、Executor／adapter processがdirect argvで起動され、shell metacharacterを含むPrompt／pathがcommand injectionを起こさない。shell例外はrollback mechanism／trigger／tested evidenceを含み、欠落時はIssue Delivery ReviewをPASSしない。 |
| E2-AC-012 | Briefなし／generic／Architecture-Aware比較に必要なEvidence quality、Checkpoint PASS、failure cycle、tool call／探索／handoff、Human intervention、wall-clockがrun単位で記録される。 |
| E2-AC-013 | Human Issue Plan Adoption Gate欠落、Issue Candidate adoption／commit parity不成立、wrong logical filename／SHA／reviewed HEAD／target paths、source HEAD drift、semantic adoption mutation、validation／planning-publication failureを検出したfixtureでExecutor開始を拒否し、new Candidate／fresh Reviewへ戻る。 `PA-NF-01` archive Review PASS only、`PA-NF-02` git-bound Review PASS only、`PA-NF-03` Human Gate only、`PA-NF-04` parity only、`PA-NF-05` wrong logical Candidate filename／Candidate SHA、`PA-NF-06` wrong reviewed HEAD／exact target paths、`PA-NF-07` source drift、`PA-NF-08` semantic mutation during adoption、`PA-NF-09` parity failure、`PA-NF-10` validation／planning-publication failureを相互に独立した必須negative fixtureとして拒否し、どれか1件でも該当する場合は`execution-ready`／Executor startを禁止する。 E2-I1 consumerは10／10 PASS、violations 0を必要とする。 |
| E2-AC-014 | Checkpoint／Issue Delivery／PR ReviewがGit-bound identityとCI／BASE／merge-base Evidenceを必須とし、ZIP-only fixtureからPASSを生成しない。 |
| E2-AC-015 | canonical planning correction fixtureがsemantic changeをCandidate lane、closed mechanical changeをGit-bound laneへrouteし、両者を混同しない。 |
