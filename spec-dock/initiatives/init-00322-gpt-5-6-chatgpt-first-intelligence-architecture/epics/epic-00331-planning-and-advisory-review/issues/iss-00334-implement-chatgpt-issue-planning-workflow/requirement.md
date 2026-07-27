---
種別: 要件定義書（Issue）
ID: "iss-00334"
タイトル: "Implement ChatGPT Issue Planning Workflow"
状態: "approved"
作成者: "Blue Team"
最終更新: "2026-07-27"
親: ["epic-00331", "init-00322"]
planning_profile_guidance: "strict"
planning_profile_guidance_source: "Main-supplied current guidance; assurance classification remains external"
---

# iss-00334 Implement ChatGPT Issue Planning Workflow — Issue 要件定義

## 0. 文書の位置づけ

本書は、既存Issue NodeまたはSeedから完全なIssue Planning BundleをJIT生成し、独立Review、Human Gate、採用、検証、Planning publicationを経て実装引き渡し可能な状態を導出する製品能力の **WHAT** を定義する。実装方法とTDD順序は `design.md` と `plan.md` が所有する。

本書はHumanが正式配置を指示したCandidate v15を基礎に、fresh canonical `spec-reviewer` の指摘をMainが反映したcanonical Requirementである。planning repairのsource baselineは `chemitaro/spec-dock` / `iss-00334-implement-chatgpt-issue-planning-workflow` / `eadbfa544ad972c799162552f5684482d26e89b5`。このHEADは修正前のimplementation surfaceを識別するbaselineであり、Review／apply／implementation entryではcurrent branch HEADとrelevant source manifestを再取得し、implementation-relevant driftがあればfresh Reviewを要求する。本書の存在だけではfresh reviewer pass、Human implementation-start authorization、execution readiness、PR readiness、merge readiness、Issue finish、Epic completionのいずれも成立しない。Candidate provenanceと過去の非権限状態は`report.md`だけが保持する。

既存assurance runtimeが分類する`authorized_profile=standard`を置き換えず、本Issueはpublic command、archive security、multi-file recovery、credentialed live dogfoodを含むためMainがIssue-localな`strict`強化を適用する。差分はspecialist evidence、全negative matrix、step reviewer、S90／S99を省略しないことであり、これらの高リスク契約がRequirementから除かれfresh spec reviewを通過した場合だけstandardへ戻せる。classification／compositionはMainがCandidate workflow外で既存assurance手順に従って実行する。

## 1. Product Outcome

Humanがofficial `spec-dock-issue-planning` Skillを起点に、MainとSpecDockが次を一つのIssue Planning walking skeletonとして完了できる。

1. exact repository／branch／HEADへbindしたIssue Planningを開始する。
2. `spec-dock-chatgpt planning create`でChatGPT Plannerからcomplete `requirement.md`／`design.md`／`plan.md` responseを受け取り、Core Runtimeがmandatory controlsを付与したimmutable Issue Candidate ZIPをfinal artifactとして生成する。
3. `spec-dock-chatgpt review planning`でread-only Reviewを行う。
4. 必要時は`spec-dock-chatgpt planning revise`でSemantic complete replacementまたはbounded Mechanical revisionを行う。
5. exact reviewed identityへbindされたHuman Issue Plan Adoption and Implementation-Start Authorization後にだけ、`spec-dock-chatgpt planning apply`でmode固有の採用／parity、validation、Planning publicationを実行する。
6. 上記の論理積からだけ実装引き渡し可能状態を導出する。

## 2. Actors and Authority

| Actor | Authority |
|---|---|
| Human | Issue Plan adoption、implementation start、mergeの最終判断 |
| `spec-dock-issue-planning` Skill | Human entrypoint、Review transport／Revision lane／Human Gateのsemantic selection |
| Codex Main | context収集、deterministic filesystem／Git操作、canonical placement、commit／push、evidence統合 |
| `spec-dock-chatgpt` | target解決、Git preflight、Prompt合成、Oracle/backend起動、result retrieval、およびHuman-supplied evidenceをCore Runtimeへ渡すpublic apply adapter |
| Core Runtime | three-document response validation、immutable Issue Candidate packaging、safe archive、identity、transactional adoption、parity、validation、publication、derived readinessの決定的処理 |
| ChatGPT Planner | complete三文書responseの生成。outputはRuntime packaging前かつadoption前のEvidence |
| ChatGPT Reviewer | read-only findings／verdictの生成。repository／Candidateを変更しない |

## 3. Scope

### 3.1 In Scope

- official `spec-dock-issue-planning` SkillからのIssue Planning起動。
- independent repo-local `spec-dock-chatgpt` command family: `planning create`、`planning revise`、`review planning`、`planning apply`。
- exact target、parent、dependency、relevant paths、repository／branch／HEADの解決。
- GitHub-visible named branch、clean tree、upstream、local HEADとremote HEADの一致を確認するpreflight。
- provider-managed closed Markdown Prompt resources。
- complete Requirement／Design／Plan authoringと、mandatory controlsを含むimmutable Issue Candidate ZIP packaging。
- `archive-candidate` defaultと、material reasonがある場合の`git-bound` fallback。silent fallbackなし。
- Semantic complete replacementとbounded Mechanical revision。
- read-only Review outputのCandidate外保存と基本的なpre／post mutation guard。
- Human Gate、deterministic adoption、parity、validation、Planning publication、derived readiness。
- provider-first source、wheel／sdist、fresh init、update、dogfood parity。
- feature-complete直前にHumanが選ぶeligible IssueでのJIT dogfood。
- Issue-local tests、docs、Skill、Prompt、provider／installed projection。

### 3.2 Mandatory Non-goals

1. **Current Portfolio replanning禁止:** 現在のHuman-approved Initiative／Epic Portfolioを再設計・再分割しない。
2. **Downstream Issue pre-authoring禁止:** 後続IssueのRequirement／Design／Planを先行作成せず、他IssueのPlanningを本Issueの成果物として代行しない。
3. **Human authority bypass禁止:** Human Portfolio Approval、Issue-local Human Gate、merge判断を自動化・代行・迂回しない。
4. **Planning-only completion禁止:** Planning文書またはPlanning runだけをIssue完了とせず、Workflow implementation、tests、docs、projectionを完了する。

### 3.3 Routed Outside This Issue

shared Issue delivery／report／HEAD cycle、PR merge semantics、Issue finish、lifecycle recovery、Epic completion、他Initiativeへ適用する一般Review frameworkは既存ownerの外部制約として参照するだけであり、本Issueで再設計または実装しない。

## 4. Functional Requirements

### REQ-001 Official Skill Entry
Human向けofficial interfaceは`spec-dock-issue-planning` Skillであり、Skillはbounded contextを組み立ててrepo-local `spec-dock-chatgpt`へ委譲する。

### REQ-002 Independent CLI
`spec-dock-chatgpt`はCore lifecycle CLIから独立したrepo-local executableとして提供し、`planning create`、`planning revise`、`review planning`、`planning apply`を公開する。`planning apply`だけがHuman-supplied decisionを検証して採用後半を呼び出せるsupported public routeであり、internal moduleのad-hoc Python呼出しを製品経路にしない。

### REQ-003 Exact Git Binding
正式runはrepository、named branch、expected HEAD、upstream、clean tree、local／remote equalityを検証し、GitHub exact HEADを確認できない場合はfail closedとする。default branch、添付tracked file、記憶へ暗黙fallbackしない。

### REQ-004 Complete Bundle and Runtime Candidate Package
`planning create`は二層のoutput contractを持つ。ChatGPT Planner responseは一つのfresh sessionから得たcomplete `requirement.md`、`design.md`、`plan.md`だけであり、Main／Runtimeはその意味内容を再構成しない。成功時のpublic final artifactはCore Runtimeが生成するimmutable Issue Candidate ZIPであり、三文書に加えて`SOURCE-BASELINE.json`、`MANIFEST.json`、`CHECKSUMS.sha256`、`PLACEHOLDER-ORACLE-MAP.json`を必須とする。Runtimeはversion、logical filename、Candidate ID、internal root、source repository／branch／HEADを一回のrun identityから決定し、archive close後のexternal ZIP SHA-256を返す。partial bundle、mandatory control欠落、identity不整合、既存final target衝突ではfinal ZIPを残さない。

### REQ-005 Closed Prompt Resources
Planning／Review Promptはprovider-managed closed Markdown resourcesから構成し、public raw Prompt overrideまたはarbitrary custom templateを受け付けない。

### REQ-006 Dual Review Transport
`archive-candidate`をpre-canonical semantic iterationのdefaultとし、actual path／CI／GitHub inline review等のmaterial reasonがある場合だけ`git-bound`を選択できる。mode間のReview結果を流用せず、silent fallbackしない。

### REQ-007 Dual Revision Lanes
Semantic RevisionはChatGPT Blue Teamによるcomplete Candidate replacement、Mechanical Revisionは事前にpath／field／old-new literal／meaning invariant／diff budgetを閉じられる変更だけとする。どちらも変更後identityとfresh Reviewを必要とする。

### REQ-008 Read-only Review Isolation
ReviewerはCandidate、canonical file、patch、replacement document、revised ZIPを生成・変更しない。Review outputはCandidate／canonical pathから分離した明示destinationへ書き、Review前後でtracked treeとCandidate bytesが不変であることを確認する。

### REQ-009 Single Adoption and Publication Lifecycle
Issue Planningは次の一つのlifecycleだけを持つ。

```text
exact reviewed identity
→ future fresh Planning Review result
→ exact identity-bound Human Plan adoption and implementation-start decision
→ archive: deterministic canonical adoption + candidate-to-canonical parity
   or git-bound: exact reviewed-content canonical/commit parity
→ required validation
→ dedicated Planning commit/push and remote parity
→ readiness derived from the complete conjunction
```

Review、Human Gate、parity、validation、publicationのいずれか単独では実装引き渡し可能状態にならない。

後半lifecycleの公開入口は`planning apply`だけとする。CLIはHuman decisionを生成または推測せず、exact reviewed identity、review result、Human decision source、mode-specific identity、expected source HEAD、canonical decision-artifact destinationを明示入力として要求する。入力欠落、不一致、stale、または未許可destinationではrepository mutation前に非成功とする。

### REQ-010 Archive Adoption
archive pathではexact logical filename、ZIP SHA、internal root、MANIFEST identity、source bindingを照合する。全入力をrepository外のoperation staging areaで先に検証し、canonical Human decision artifactをnew-fileとして固定したうえで`requirement.md`→`design.md`→`plan.md`の順にtransactional replacementする。commit前の失敗はpre-operation bytes／modeへreverse-order restoreしてclean baselineを再証明し、rollback自体が失敗した場合は`recovery_required`として自動続行しない。成功時はCandidate-to-canonical byte／declared-placeholder parity、明示されたHuman decision artifact以外のunexpected Candidate-external diff 0を証明する。

### REQ-011 Git-bound Adoption
Git-bound pathではexact reviewed HEAD／target pathsへHuman decisionをbindし、reviewed target blobsの不変性、approval-only adoption diff、publication commit tree parityを証明する。

### REQ-012 Planning Publication
Mainは`planning apply`を明示的に起動し、RuntimeにPlanning専用commitを作成・pushさせ、local publication HEAD、remote branch HEAD、commit treeが一致することを確認する。commit前の失敗はrollbackする。commit成功後のpush失敗はlocal commitを破棄・rewriteせず`publication_pending`を返し、same operation identityでだけretryできる。remote divergenceまたはoperation identity不一致は`blocked_remote_diverged`とし、force push、automatic reset、別Candidateへのfallbackを行わない。publication failureではreadinessを導出しない。

### REQ-013 Derived Readiness
RuntimeはReview、Human decision、mode-specific parity、validation、publicationの論理積を評価し、全条件成立時だけ`ready`を返す。非成立時のstable statusは`blocked`、`stale`、`rejected`、`rolled_back`、`publication_pending`、`blocked_remote_diverged`、`recovery_required`のいずれかとし、CLI exit codeは`ready=0`、それ以外=`1`とする。operation-local staging／recovery manifestとexternal result JSONは許可するが、専用state database、receipt registry、custom Git refを新設しない。

### REQ-014 Negative Adoption Fixtures
以下を独立fixtureとして拒否し、どれか一件でも成立する場合はExecutor startを禁止する。

| ID | Rejected condition |
|---|---|
| PA-NF-01 | archive Review resultだけ |
| PA-NF-02 | git-bound Review resultだけ |
| PA-NF-03 | Human Gateだけ |
| PA-NF-04 | parityだけ |
| PA-NF-05 | wrong logical Candidate filenameまたはZIP SHA |
| PA-NF-06 | wrong reviewed HEADまたはtarget paths |
| PA-NF-07 | source drift後のstale identity |
| PA-NF-08 | adoption中のsemantic mutation |
| PA-NF-09 | parity failure |
| PA-NF-10 | validationまたはPlanning publication failure |

### REQ-015 Workbench and Durable Evidence

Workbenchはprompt、explicit external files、downloaded Candidate、Review result、Human decision source、operation-local staging／backup／recovery manifest、diagnosticsのtemporary surfaceに限定する。raw transcriptを保存せず、`report.md`をPlanning receipt、Review authority、Human authorization authority、readiness state storeにしない。

`PlanningHumanDecisionV1`のv1許可decisionは`approved`と`rejected`だけである。

- `approved`はexact Review-result bytesとexact reviewed identityへbindし、`plan_adoption=true`かつ`implementation_start=true`を要求する。`planning apply`はvalidated Human decision sourceのexact bytesを明示されたIssue `artifacts/` direct-child JSONへ記録し、mode固有のcanonical adoption、validation、Planning publicationを一つのtransactionとして実行する。
- `rejected`はexact Review-result bytesとexact reviewed identityへbindし、`plan_adoption=false`かつ`implementation_start=false`を要求する。`planning apply`はdecision artifactだけを追加するbounded decision-record transactionを実行し、`requirement.md`、`design.md`、`plan.md`を変更しない。dedicated Planning decision commitのpushとremote parityが成立した後もresultは`blocked`、exit `1`であり、readinessを導出しない。
- published rejectionはrepository HEADを変更するため、rejection前のHEADへbindされたReview result、Human approval、Candidate identity、git-bound identityを`stale`にする。その後のapprovalはnew HEADへbindしたfresh Reviewとnew Human decisionを必要とする。
- `revoked`は`PlanningHumanDecisionV1` v1に含めない。approved publication後のHuman withdrawal、implementation stop、または履歴取消しはcurrent shared Human／Main stop-or-revert workflowのowner境界で扱い、`planning apply`は`decision=revoked`を`rejected`としてrepository mutation前に拒否する。source-changing stop／revert evidenceがない口頭またはWorkbench上のrevocation claimを、既存approvalを失効させるproduct authorityとして扱わない。

decision artifactは`planning apply --decision-artifact`で明示された新規Issue `artifacts/` direct-child JSONだけへbyte-exactに記録する。operation完了後はbackupを削除し、external result JSONは観測Evidenceとしてだけ保持する。専用authority registry、revocation registry、state database、custom Git refを新設しない。

### REQ-016 Assurance Boundary
Candidate generation、adoption、publication、readinessは`.assurance.json`を変更しない。Mainは既存assurance workflowをCandidate外で実行する。

### REQ-017 Provider-first Projection
実装authorityは`src/spec_dock/` provider surfaceに置き、installed／dogfood copiesは`init`／`update`で生成する。同一Issueでwheel、sdist、fresh init、update、provider／installed／dogfood parityを検証する。

### REQ-018 JIT Dogfood
feature-complete直前に、まずhermetic fake-remote testでselection／abort／recovery contractを検証する。その後Humanが、open real Issue、E1 dependency chain外、Portfolio replanning不要、genuine refresh need、dedicated clean worktree／branch、bounded pre-commit rollback、他作業非干渉、Human Gate実行可能という条件を満たすtargetを一件選び、credentialed mutation範囲とevidence destinationを明示承認した場合だけMainが選択modeのfull positive chainを完走する。target選択または承認がない限りlive backend／canonical write／pushを開始しない。

### REQ-019 Existing Primitive Reuse
Git preflight、direct argv、redaction、safe ZIP、digest、atomic file replacement／publication、current validation primitivesを再利用し、同じ安全機能を別subsystemとして複製しない。multi-file adoptionではcurrent `runbook_store.py`のstage／backup／restore patternをshared scoped transaction primitiveへ抽出し、runbook projectionとIssue Planning双方から使用する。private helperへのcross-module couplingまたは同等処理の複製は禁止する。

### REQ-020 Delivery Boundary
本Issueはone Issue／one branch／one Delivery PR／required review／Human mergeに従う。S99後のPR delivery、merge、finishはcurrent shared workflowへhandoffし、そのowner contractを本Issueで変更しない。

## 5. Non-functional and Security Requirements

### REQ-021 Sensitive Data and Process Safety
Prompt、Operator Context、explicit files、Workbench、Candidate、Review outputへsecret、token、cookie、credential、private key、`.env`、production dump、private customer dataを含めない。process launchはdirect argvをdefaultとし、untrusted valueをshell stringへ補間しない。不可避なshell例外はHuman-approved Design、fixed template、安全なinput handling、injection regression、rollback mechanism／trigger／tested rollback evidenceを必要とする。

### REQ-022 Candidate Archive Safety
archive interfaceはregular UTF-8 text only、single safe root、no traversal／absolute／backslash ambiguity／NUL、no symlink／hardlink／device／FIFO／socket、no duplicate／casefold／Unicode-normalization collision、no encryption／nested archive／executable／unexpected binary、CRC／MANIFEST／CHECKSUMS一致をfail closedで検証する。Prospective implementation limits are: outer ZIP `<= 10,000,000` bytes、entries `<= 64`、each expanded file `<= 2,000,000` bytes、aggregate expanded `<= 10,000,000` bytes、UTF-8 path `<= 240` bytes、per-entry compression ratio `<= 100`。境界はinclusiveとし、超過時はfinal extraction／adoption outputを残さない。

### REQ-023 Compatibility
existing Core CLI、existing authoring-pack safety primitives、existing Issue lifecycle、provider／consumer directory ownershipを壊さず、new CLIをadditiveに導入する。physical legacy route removalはE1-I3へ残す。

### REQ-024 Observability
representative Planning／Review runごとにplanned／unplanned Human intervention、handoff byte／character count、Agent／Skill invocation、Review result、wall-clock、failure modeをCandidate外evidenceへ記録する。

## 6. Acceptance Criteria

### AC-001 Official Entry and Complete Output
Humanがofficial Skillを起動すると、Skillがrepo-local `spec-dock-chatgpt planning create`へ到達する。Plannerがcomplete三文書を返した場合、commandはmandatory controlsを含むimmutable Issue Candidate ZIPとexternal SHA-256を返し、そのZIPを変更・再packagingせず`review planning --mode archive-candidate`のinputにできる。情報不足時はfinal ZIPを作らず明示的`information_insufficient`を返す。

### AC-002 Command Family
`spec-dock-chatgpt --help`と各subcommand helpが`planning create`、`planning revise`、`review planning`、`planning apply`を示し、Core `spec-dock` lifecycle commandと混在しない。`planning apply --help`はHuman decision、review identity、mode identity、source HEAD、decision artifact、output directoryを必須契約として示す。

### AC-003 Git Fail-closed
clean／upstream／local-remote／exact HEADの各negative fixtureがbackend起動前に非成功となり、tracked file attachmentやdefault fallbackを行わない。

### AC-004 Create and Revision
fake backendでcreate／Semantic revisionがcomplete三文書responseを返すと、Runtimeは旧identityを上書きせずmandatory controlsを含むcomplete immutable ZIPを生成する。Mechanical revisionはclosed change setだけを許可し、変更後は同じpackaging pathでnew identityを生成する。不完全bundle、mandatory control欠落、scope追加、undeclared targetはfinal ZIPなしで拒否する。

### AC-005 Dual Review
archiveとgit-boundのpositive fixtureがそれぞれexact identityへbindされ、mode mismatch、silent fallback、stale sourceを拒否する。

### AC-006 Archive Integrity
安全なCandidateは受理され、path/type/collision/encryption/nested archive/binary/CRC/inventory/checksum/resource-limitの代表negative fixtureはpartial outputなしで拒否される。

### AC-007 Review Isolation
Review commandの前後でCandidate bytesとtracked treeが不変であり、resultは明示されたCandidate外destinationにだけ生成される。

### AC-008 Archive Positive Chain
archive modeのrepresentative fixtureを`planning apply`へ与え、future fresh Review result、exact identity-bound Human decision、transactional adoption、Candidate parity、validation、Planning publicationの全条件を満たしたときだけ`ready`を導出する。commit前faultはbaselineへrollbackし、commit後push faultは`publication_pending`からsame-operation retryで収束する。

### AC-009 Git-bound Positive Chain
git-bound fixtureを`planning apply`へ与え、future fresh Review result、exact HEAD／paths-bound Human decision、target blob不変、approval-only diff、validation、Planning publicationの全条件を満たしたときだけ`ready`を導出する。

### AC-010 Adoption Negative Set

PA-NF-01〜PA-NF-10を各独立named fixtureとして実行し、各fixtureがDesign／Planで固定された一つのexact stable status、exit `1`、readinessなし、許可されたmutation contractだけを返すことを確認する。genericな「reject」または複数statusの許容を代替証拠にせず、10／10でexpected status一致、violations 0を得る。

### AC-011 Security
secret/path/shell metacharacter fixturesがPrompt、diagnostic、Candidate、Review outputへ漏れず、backendはdirect argvで起動される。

### AC-012 Provider and Distribution Parity
`uv build`でwheel／sdistを作成し、fresh initとupdate後に`spec-dock-chatgpt`がregular executableとして直接起動し、provider／installed／dogfoodのmanaged bytesとSkill／Prompt inventoryが一致する。

### AC-013 State Boundary
Candidate workflowによる`.assurance.json` mutation、new Planning database、Review receipt registry、raw transcript保存、`report.md` authority化が0である。

### AC-014 JIT Dogfood
hermetic testでlive-operation selection／abort／recovery contractを先にGreenにする。その後、Humanがtarget、worktree／branch、credentialed mutation、evidence destinationを明示承認したeligible Issue一件だけで、Mainがselected modeのcreate→Review→Human Gate→`planning apply`→readiness handoffを完走し、current Portfolio／downstream Issueへのunauthorized mutationが0である。live runをpytest workerへ委任しない。

### AC-015 Existing Compatibility
existing authoring-pack focused tests、Core CLI tests、validate／sync regressionが維持され、new public routeはprovider-firstでinstall/update可能である。

### AC-016 Delivery Handoff
全product steps、S90、S99完了後、current shared delivery workflowへone branch／one Delivery PRとしてhandoffし、required review後のmergeはHumanだけが実行する。

### AC-017 Source Identity
Review identityはcurrent repository／branch／HEADと直接関係するsource setへbindし、いずれかが変化した場合は再Reviewまたはnew Candidateを要求する。任意のtransitive完全性や固定件数はauthorityとしない。

## 7. Error Conditions

| ID | Observable failure | Required result |
|---|---|---|
| EC-001 | unknown Issue、dirty tree、upstream欠落、local／remote／expected HEAD不一致 | backend／repository mutation前に`blocked`または`stale` |
| EC-002 | Planner response不完全、unexpected file、non-UTF-8、authority claim、secret-like payload | final Candidateなしで`rejected` |
| EC-003 | Review mode／identity不一致、Review mutation、silent fallback要求 | Review evidenceをinvalid化して`rejected` |
| EC-004 | REQ-022のarchive safety classまたはinclusive ceiling違反 | extraction／Review／adoption outputなしで`rejected` |
| EC-005 | Review／Human gate evidenceまたはdecision destinationの不成立 | required Review-result sourceまたはHuman-decision sourceの欠落／不存在は`blocked`、mutation 0。malformed JSON、wrong schema version／kind、missing／unknown／duplicate key、invalid enum／timestamp／digest、partial authorization、Review／Human／CLI mode・Issue・identity・digest mismatch、unsafe／existing／scope外destination、unsupported `decision=revoked`は`rejected`、mutation 0。validated identityに対するcurrent source／Candidate／target driftは`stale`、mutation 0。valid Review `fail`とHuman `approved`の組合せは`blocked`、mutation 0。valid Human `rejected`はdecision-record transactionへ進み、verified remote publication後に`blocked`、exit `1`、canonical三文書mutation 0 |
| EC-006 | canonical replacementまたはpre-commit validation failure | baseline復元成功なら`rolled_back`、復元失敗なら`recovery_required` |
| EC-007 | commit作成失敗 | worktree/indexをbaselineへ戻し`rolled_back`、復元不能なら`recovery_required` |
| EC-008 | commit成功後のpush失敗またはresponse loss | local commitを保持して`publication_pending`、same-operation retryだけ許可 |
| EC-009 | retry時のremote divergence、operation identity／tree mismatch | `blocked_remote_diverged`、force push／automatic resetなし |
| EC-010 | JIT dogfood target不適格またはHumanのcredentialed mutation承認なし | live backend／canonical mutation／push前に`blocked` |

## 8. Completion Boundary

本Issueのproduct work完了候補は、implementation、focused tests、docs／Skill／Prompt、provider／installed／dogfood parity、JIT dogfood、S99、current shared delivery handoffが揃った状態である。Candidate package単体はその状態を成立させない。
