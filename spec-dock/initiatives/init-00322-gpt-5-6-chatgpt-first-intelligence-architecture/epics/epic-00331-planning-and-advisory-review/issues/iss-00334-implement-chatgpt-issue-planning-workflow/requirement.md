---
種別: 要件定義書（Issue）
ID: "iss-00334"
タイトル: "Implement ChatGPT Issue Planning Workflow"
状態: "draft"
作成者: "Blue Team"
最終更新: "2026-07-27"
親: ["epic-00331", "init-00322"]
planning_profile_guidance: "strict"
planning_profile_guidance_source: "Main-supplied current guidance; assurance classification remains external"
---

# iss-00334 Implement ChatGPT Issue Planning Workflow — Issue 要件定義

## 0. 文書の位置づけ

本書は、既存Issue NodeまたはSeedから完全なIssue Planning BundleをJIT生成し、独立Review、Human Gate、採用、検証、Planning publicationを経て実装引き渡し可能な状態を導出する製品能力の **WHAT** を定義する。実装方法とTDD順序は `design.md` と `plan.md` が所有する。

このCandidate packageは `authority=candidate`、`adoption_status=unreviewed` の非正本Evidenceである。現在のsource bindingは `chemitaro/spec-dock` / `iss-00334-implement-chatgpt-issue-planning-workflow` / `2e86ec64289ec8102470df75329025d46bbfa51a`。本書の存在だけではReview結果、Human authorization、canonical adoption、assurance mutation、execution readiness、PR readiness、merge readiness、Issue finish、Epic completionのいずれも成立しない。

現在のplanning profileはMainから `strict` として供給されたguidanceである。Candidateは `.assurance.json` を変更せず、classification／compositionはMainがCandidate外で既存Workflowに従って実行する。

## 1. Product Outcome

Humanがofficial `spec-dock-issue-planning` Skillを起点に、MainとSpecDockが次を一つのIssue Planning walking skeletonとして完了できる。

1. exact repository／branch／HEADへbindしたIssue Planningを開始する。
2. `spec-dock-chatgpt planning create`でChatGPT Plannerからcomplete `requirement.md`／`design.md`／`plan.md` responseを受け取り、Core Runtimeがmandatory controlsを付与したimmutable Issue Candidate ZIPをfinal artifactとして生成する。
3. `spec-dock-chatgpt review planning`でread-only Reviewを行う。
4. 必要時は`spec-dock-chatgpt planning revise`でSemantic complete replacementまたはbounded Mechanical revisionを行う。
5. exact reviewed identityへbindされたHuman Issue Plan Adoption and Implementation-Start Authorization後にだけ、mode固有の採用／parity、validation、Planning publicationを実行する。
6. 上記の論理積からだけ実装引き渡し可能状態を導出する。

## 2. Actors and Authority

| Actor | Authority |
|---|---|
| Human | Issue Plan adoption、implementation start、mergeの最終判断 |
| `spec-dock-issue-planning` Skill | Human entrypoint、Review transport／Revision lane／Human Gateのsemantic selection |
| Codex Main | context収集、deterministic filesystem／Git操作、canonical placement、commit／push、evidence統合 |
| `spec-dock-chatgpt` | target解決、Git preflight、Prompt合成、Oracle/backend起動、result retrievalのthin adapter |
| Core Runtime | three-document response validation、immutable Issue Candidate packaging、safe archive、identity、adoption、parity、validation、publication、derived readinessの決定的処理 |
| ChatGPT Planner | complete三文書responseの生成。outputはRuntime packaging前かつadoption前のEvidence |
| ChatGPT Reviewer | read-only findings／verdictの生成。repository／Candidateを変更しない |

## 3. Scope

### 3.1 In Scope

- official `spec-dock-issue-planning` SkillからのIssue Planning起動。
- independent repo-local `spec-dock-chatgpt` command family: `planning create`、`planning revise`、`review planning`。
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
`spec-dock-chatgpt`はCore lifecycle CLIから独立したrepo-local executableとして提供し、`planning create`、`planning revise`、`review planning`を公開する。

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

### REQ-010 Archive Adoption
archive pathではexact logical filename、ZIP SHA、internal root、MANIFEST identity、source bindingを照合し、fixed-order atomic replacement後にCandidate-to-canonical byte／declared-placeholder parityとCandidate外差分0を証明する。

### REQ-011 Git-bound Adoption
Git-bound pathではexact reviewed HEAD／target pathsへHuman decisionをbindし、reviewed target blobsの不変性、approval-only adoption diff、publication commit tree parityを証明する。

### REQ-012 Planning Publication
MainはPlanning専用commitを作成しpushし、local publication HEAD、remote branch HEAD、commit treeが一致することを確認する。publication failureではreadinessを導出しない。

### REQ-013 Derived Readiness
RuntimeはReview、Human decision、mode-specific parity、validation、publicationの論理積を評価してreadiness結果を返す。専用state database、receipt registry、custom Git refを新設しない。

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
Workbenchはprompt、explicit external files、downloaded Candidate、Review result、diagnosticsのtemporary surfaceに限定する。Human decisionはWorkbench source JSON SHAとcanonical Issue Artifactへ記録し、raw transcriptを保存しない。`report.md`はPlanning receipt、Review authority、Human authorization authority、readiness state storeにしない。

### REQ-016 Assurance Boundary
Candidate generation、adoption、publication、readinessは`.assurance.json`を変更しない。Mainは既存assurance workflowをCandidate外で実行する。

### REQ-017 Provider-first Projection
実装authorityは`src/spec_dock/` provider surfaceに置き、installed／dogfood copiesは`init`／`update`で生成する。同一Issueでwheel、sdist、fresh init、update、provider／installed／dogfood parityを検証する。

### REQ-018 JIT Dogfood
feature-complete直前にHumanが、open real Issue、E1 dependency chain外、Portfolio replanning不要、genuine refresh need、bounded rollback、他作業非干渉、Human Gate実行可能という条件を満たすtargetを一件選び、選択modeのfull positive chainを完走する。

### REQ-019 Existing Primitive Reuse
Git preflight、direct argv、redaction、safe ZIP、digest、atomic file replacement／publication、current validation primitivesを再利用し、同じ安全機能を別subsystemとして複製しない。

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
`spec-dock-chatgpt --help`と各subcommand helpが三command familyを示し、Core `spec-dock` lifecycle commandと混在しない。

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
archive modeのrepresentative fixtureがfuture fresh Review result、exact identity-bound Human decision、atomic adoption、Candidate parity、validation、Planning publicationの全条件を満たしたときだけreadinessを導出する。

### AC-009 Git-bound Positive Chain
git-bound fixtureがfuture fresh Review result、exact HEAD／paths-bound Human decision、target blob不変、approval-only diff、validation、Planning publicationの全条件を満たしたときだけreadinessを導出する。

### AC-010 Adoption Negative Set
PA-NF-01〜PA-NF-10を各独立に実行し、10／10 reject、violations 0を得る。

### AC-011 Security
secret/path/shell metacharacter fixturesがPrompt、diagnostic、Candidate、Review outputへ漏れず、backendはdirect argvで起動される。

### AC-012 Provider and Distribution Parity
`uv build`でwheel／sdistを作成し、fresh initとupdate後に`spec-dock-chatgpt`がregular executableとして直接起動し、provider／installed／dogfoodのmanaged bytesとSkill／Prompt inventoryが一致する。

### AC-013 State Boundary
Candidate workflowによる`.assurance.json` mutation、new Planning database、Review receipt registry、raw transcript保存、`report.md` authority化が0である。

### AC-014 JIT Dogfood
Human-selected eligible Issue一件で、selected modeのcreate→Review→Human Gate→adoption/parity→validation/publication→readiness handoffを完走し、current Portfolio／downstream Issueへのunauthorized mutationが0である。

### AC-015 Existing Compatibility
existing authoring-pack focused tests、Core CLI tests、validate／sync regressionが維持され、new public routeはprovider-firstでinstall/update可能である。

### AC-016 Delivery Handoff
全product steps、S90、S99完了後、current shared delivery workflowへone branch／one Delivery PRとしてhandoffし、required review後のmergeはHumanだけが実行する。

### AC-017 Source Identity
Review identityはcurrent repository／branch／HEADと直接関係するsource setへbindし、いずれかが変化した場合は再Reviewまたはnew Candidateを要求する。任意のtransitive完全性や固定件数はauthorityとしない。

## 7. Completion Boundary

本Issueのproduct work完了候補は、implementation、focused tests、docs／Skill／Prompt、provider／installed／dogfood parity、JIT dogfood、S99、current shared delivery handoffが揃った状態である。Candidate package単体はその状態を成立させない。
