---
種別: 要件定義書（Issue）
ID: "iss-00334"
タイトル: "Implement ChatGPT Issue Planning Workflow"
状態: "approved"
作成者: "Blue Team / Codex Main"
最終更新: "2026-07-29"
親: ["epic-00331", "init-00322"]
---

# iss-00334 Implement ChatGPT Issue Planning Workflow — Issue 要件定義

## 0. 文書の目的

本書は、既存のIssueを対象に、ChatGPTを用いて`requirement.md`、`design.md`、`plan.md`をJIT作成・修正・レビューし、Human承認後に正本へ採用できるSpecDockの製品能力を定義する。

本IssueはWorkflowの実装Issueである。iss-00334自身のPlanning完了だけではIssue完了にならず、実装、テスト、ドキュメント、dogfood、Delivery PRまでを完了対象とする。

## 1. Outcome

Humanがofficial `spec-dock-issue-planning` Skillを起点として、次の一連の操作を実行できる。

1. 既存Issueとcurrent GitHub branch／HEADを特定する。
2. ChatGPT Plannerから完全な三文書を取得し、immutableなIssue Candidate ZIPを生成する。
3. CandidateまたはGitHub上の正本三文書をfresh ChatGPT Reviewerへ渡す。
4. 指摘が実在する場合だけCandidateをrevisionする。
5. exact reviewed identityへbindしたHuman承認後に正本へ採用し、validate、commit、pushを行う。
6. 全条件成立時だけIssueを実装開始可能として引き渡す。

## 2. Actors and Authority

| Actor | Responsibility |
|---|---|
| Human | Plan採用、実装開始、mergeの最終判断 |
| `spec-dock-issue-planning` Skill | Human向け入口、mode／revision laneの選択、必要な文脈の収集 |
| Codex Main | repository確認、外部出力の検証、正本反映、証跡統合 |
| `spec-dock-chatgpt` | Git preflight、ChatGPT起動、result取得、Candidate／Review／apply処理のCLI |
| ChatGPT Planner | 三文書の新規作成または完全置換 |
| ChatGPT Reviewer | read-only review。Candidate、正本、repositoryを変更しない |
| Core Runtime | Candidate検証、identity、採用transaction、validation、publicationの決定的処理 |

ChatGPTの出力はadvisory evidenceであり、Humanの採用権限を代替しない。

## 3. Scope

### 3.1 In Scope

- official Skillからrepo-local `spec-dock-chatgpt`を呼ぶ経路。
- `planning create`、`planning revise`、`review planning`、`planning apply`。
- existing Issue、親Epic／Initiative、依存、関連source、repository／branch／HEADの解決。
- provider-managed Promptとprovider-owned Oracle adapterによるPlanner／Reviewer起動。
- complete三文書とcontrol filesを含むIssue Candidate ZIP。
- `archive-candidate`をdefault、`git-bound`を明示的fallbackとするReview。
- Semantic revisionとMechanical revision。
- exact identityへbindしたReview resultとHuman decision。
- transactional canonical adoption、validate、Planning commit、push、remote parity。
- provider／installed／dogfood projection、tests、docs、JIT dogfood。

### 3.2 Non-goals

- 現在承認済みのInitiative／Epic Portfolioの再設計。
- 後続Issueの三文書の先行作成。
- Human approval、merge、Issue finishの自動化。
- Initiative／Epic Planningや汎用Review frameworkの実装。
- arbitrary Prompt、任意backend、永続的なPlanning database／authority registryの追加。
- 本Issueでshared delivery／lifecycle policyを変更すること。

### 3.3 Seedの扱い

v1のCLIはexisting Issueだけを対象とする。GoalやSeedから開始する場合、official Skillが既存の親Planning／node materialization経路へ案内し、Issue node作成後に新しい`planning create --issue <id>`を開始する。SeedをCLIが暗黙materializeしてはならない。

## 4. Functional Requirements

### REQ-001 Official Entry

Human向け入口は`spec-dock-issue-planning` Skillとする。Skillはactive stateを推測だけで決定せず、対象IssueとGit identityを表示してからrepo-local CLIへ委譲する。

### REQ-002 Public Command Family

repo-local `spec-dock-chatgpt`は次の四commandだけを公開する。

- `planning create`
- `planning revise`
- `review planning`
- `planning apply`

Core `spec-dock` lifecycle commandとは分離する。

### REQ-003 Exact Git Binding

ChatGPTを使用する正式runはcurrent repository、named branch、HEAD、upstreamを取得し、local HEADとremote branch HEADの一致を確認する。不一致、detached HEAD、upstream欠落、dirty treeではChatGPT起動またはrepository mutation前に停止する。

### REQ-004 Complete Issue Candidate

`planning create`と`planning revise`の成功結果は、次を含むimmutable ZIPとする。

- `requirement.md`
- `design.md`
- `plan.md`
- `SOURCE-BASELINE.json`
- `MANIFEST.json`
- `CHECKSUMS.sha256`
- `PLACEHOLDER-ORACLE-MAP.json`

CandidateはIssue ID、Candidate ID、version、logical filename、observed transport filename、internal root、source repository／branch／HEAD、ZIP SHA-256で識別する。closed`(N)`transport suffixだけをlogical filenameへ正規化でき、それ以外のrenameは拒否する。Human decision evidenceはlogical／transport filenameとSHAを保持する。不完全な三文書、control file不整合、既存output衝突時はfinal ZIPを残さない。

placeholder verificationは`PLACEHOLDER-ORACLE-MAP.json`がdynamicとして宣言したfile／tokenだけを対象とする。static exact-hash document内のliteral exampleを未解決placeholderとして拒否しない。

### REQ-005 Review Modes

- `archive-candidate`: pre-canonical iterationのdefault。exact Candidate ZIPをReviewする。
- `git-bound`: actual canonical path、CI、GitHub inline参照が必要な場合のfallback。exact reviewed HEADと対象Issueのcanonical三文書をReviewする。

git-bound Issue Planning Reviewのtargetは対象Issueの`requirement.md`、`design.md`、`plan.md`のexact 3 pathsとする。親文書、source code、関連artifactはread-only contextとして参照できるがreviewed target identityには含めない。

modeはSkillまたはHumanが明示し、silent fallback、別modeのPASS流用を禁止する。

### REQ-006 Read-only Fresh Review

ReviewはCandidateまたはtracked treeを変更せず、resultを明示されたrepository外outputへ保存する。Candidate versionまたはgit-bound reviewed HEADごとにfresh reviewer conversationを使用する。

Reviewは現在の設計を前提として、実在する欠落、矛盾、重複、path／identity／ownerのずれ、具体的な実装不能、安全性またはHuman authority違反だけをfindingとする。改善提案や再設計案だけでFAILにしない。

P0／P1だけをblocking findingとする。P2／P3はnon-blocking observationであり、P2／P3だけのReviewではCandidateを変更せずPASSとしてHuman Gateへ進める。

### REQ-007 Revision Request

`planning revise`は`--request <json>`を必須とし、Skillが選んだlaneと修正対象を明示する。

- Semantic: 対象Candidate identity、採用するP0／P1 review finding IDs、維持すべき設計前提を渡し、完全な三文書replacementを要求する。
- Mechanical: 対象Candidate identity、target file、old text、new text、meaning invariant、diff budgetを渡し、指定箇所以外のsemantic changeを禁止する。一意に適用できないrequestはSemantic laneへ暗黙fallbackせず拒否する。

Revision request validatorはP2／P3 finding IDを修正triggerとして受理しない。旧Candidateは上書きせず、P0／P1 revision成功後は新version／Candidate ID／ZIP SHAを持つcomplete Candidateを生成し、fresh Reviewへ戻す。

### REQ-008 Human Decision

`planning apply`はexact reviewed identity、Review result file、Human decision fileを必須とする。Human decisionはReview result bytesとreviewed identityへbindし、`approved`または`rejected`だけを許可する。

- `approved`: Plan採用とimplementation startの双方を明示する。
- `rejected`: 正本三文書を変更せず、decision artifactだけを記録する。

CLIはHuman decisionを生成、推測、補完しない。

### REQ-009 Canonical Adoption

archive modeではCandidate内の三文書を正本へwhole-file replacementし、Candidate-to-canonical parityと明示されたdecision artifact以外のunexpected Candidate-external diff 0を確認する。git-bound modeではreviewed HEADのexact target blobsがapply時まで不変であることを確認する。

採用はoperation staging areaで検証してから開始する。commit前の失敗では三文書とindexを元へ戻す。restoreを確認できない場合は自動継続しない。

archive PASS後の二度目の完全Semantic Reviewは、source HEAD不変、exact Candidate／Human binding、unexpected Candidate-external diff 0、byte／semantic parity、validation／sync PASSをすべて証明できる場合だけ省略できる。証明できない場合はnew Candidateまたはfresh git-bound Reviewへ戻る。

### REQ-010 Validation and Publication

approved adoption後にrequired SpecDock validation／syncを実行し、Planning専用commitを作成してcurrent branchへpushする。local commit、remote branch HEAD、commit treeが一致した場合だけpublication成功とする。

commit後のpush失敗ではcommitをreset／amendせず、同じoperation identityによるretryを許可する。remote divergenceではforce pushしない。

### REQ-011 Command Result

全commandはtext／JSONで同じ結果意味を返す。

| Command outcome | status | reason |
|---|---|---|
| Candidate生成成功 | `ok` | `candidate_created` |
| Candidate revision成功 | `ok` | `candidate_revised` |
| Review完了 | `ok` | `review_completed` |
| approved applyとremote parity完了 | `ready` | `adoption_published` |
| 必須情報／Review／Human decision不足 | `blocked` | named reason |
| malformed input／unsafe archive／identity mismatch | `rejected` | named reason |
| sourceまたはCandidate drift | `stale` | named reason |
| commit前失敗からrestore成功 | `rolled_back` | named reason |
| restore未確認 | `recovery_required` | named reason |
| commit済みでpush／remote確認未完了 | `publication_pending` | named reason |
| retry時remote divergence | `blocked_remote_diverged` | named reason |

`ok`はcommand完了だけを示し、実装開始可能を意味しない。`ready`だけがapply lifecycle完了を示す。archive validatorの詳細findingはresult detailsへ保持し、public reasonは`archive_rejected`へ統一する。

親Epicのnegative adoption oracleは次の独立fixtureで確認する。

| Fixture | Condition | Expected status |
|---|---|---|
| PA-NF-01 | archive Reviewだけ | `blocked` |
| PA-NF-02 | git-bound Reviewだけ | `blocked` |
| PA-NF-03 | Human decisionだけ | `blocked` |
| PA-NF-04 | parityだけ | `blocked` |
| PA-NF-05 | wrong Candidate filename／SHA | `rejected` |
| PA-NF-06 | wrong reviewed HEAD／target paths | `rejected` |
| PA-NF-07 | source／Candidate／target drift | `stale` |
| PA-NF-08 | adoption中semantic mutation、restore成功 | `rolled_back` |
| PA-NF-09 | parity failure、restore成功 | `rolled_back` |
| PA-NF-10A | validation／sync failure、restore成功 | `rolled_back` |
| PA-NF-10B | commit後push／remote確認失敗 | `publication_pending` |

### REQ-012 Security and Data Handling

Prompt、operator context、Candidate、Review resultへsecret、token、cookie、credential、`.env`、private customer dataを含めない。process起動はdirect argvを使用し、untrusted inputをshell文字列へ補間しない。

ZIPは既存authoring-pack安全primitiveを再利用し、path traversal、absolute／ambiguous path、special file、collision、encryption、nested archive、executable／binary、CRC／inventory／checksum不整合、resource limit超過をfail closedで拒否する。

### REQ-013 Provider-first and Compatibility

provider authorityを`src/spec_dock/assets/`に置き、installed／dogfood projectionを生成して同じcommand、Skill、Promptを利用できるようにする。existing Core CLI、authoring-pack、Issue lifecycleを破壊しない。

### REQ-014 JIT Dogfood

hermetic tests完了後、Humanが選んだeligible Issue一件でcreate→Review→Human Gate→applyを実行する。live mutation範囲、worktree／branch、evidence destinationをHumanが承認するまでcanonical writeやpushを開始しない。

### REQ-015 Oracle Product Dependency Boundary

Issue Planningの外部実行依存は、`PATH`で解決されたローカルOracle本体の`oracle` commandだけとする。RuntimeはSpecDockがprovider authorityとして配布するOracle adapter／wrapperからdirect argvでOracleを起動し、`chatgpt-use`等の個人Skill、個人wrapper、user-specific absolute path、個人ChatGPT Project URL、個人browser profile／host setupを製品依存として参照してはならない。

個人wrapperはOracle運用知見を得るためのread-only参考実装またはoperator-local toolに限定する。Oracle欠落、version／capability不一致、browser／account state不成立時に個人wrapper、任意backend、APIへsilent fallbackしない。

## 5. Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| AC-001 | official Skillからexisting Issueの`planning create`を起動し、complete immutable Candidate ZIPを生成できる |
| AC-002 | create／revise／review／applyのhelp、text／JSON result、invalid inputが一貫している |
| AC-003 | exact Git preflightのpositive／negative fixtureがChatGPT起動前に判定される |
| AC-004 | Semantic／Mechanical revisionが明示requestに従い、旧Candidateを保持してnew Candidateを生成する |
| AC-005 | archive Reviewとexact canonical 3 pathsのgit-bound Reviewが別identityとして動作し、repositoryを変更しない |
| AC-006 | unsafeまたは不整合なCandidateをpartial outputなしで拒否する |
| AC-007 | approved Human decisionだけがcanonical adoptionへ進み、wrong／missing／stale identityを拒否する |
| AC-008 | archive applyがwhole-file replacement、parity、validation、commit、pushを完了した場合だけ`ready`になる |
| AC-009 | git-bound applyがreviewed target不変、validation、commit、pushを完了した場合だけ`ready`になる |
| AC-010 | PA-NF-01〜09、10A、10Bを独立fixtureとして拒否し、commit前faultはrollback、commit後push faultは`publication_pending`から安全にretryできる |
| AC-011 | secret／shell injection／path traversal fixturesをfail closedで処理する |
| AC-012 | wheel／sdist、fresh init、update、dogfood projectionでcommand／Skill／Prompt parityが成立する |
| AC-013 | Human承認済みeligible Issue一件でJIT dogfoodを完走し、scope外mutationが0である |
| AC-014 | one Issue／one branch／one Delivery PRで実装し、mergeはHumanへhandoffする |
| AC-015 | provider／wheel／sdist／fresh init／update／dogfoodでprovider-owned adapterが`PATH`上のfake／real Oracleを同一contractで起動し、shipped product surfaceに個人home、`chatgpt-use` Skill、`oracle-chatgpt` wrapperへの必須依存が0件である |

## 6. Error and Stop Conditions

- Issue未存在、Seedの直接指定、dirty／detached／unpublished Git state。
- backend unavailable、timeout、nonzero、complete response欠落。
- Candidate identity、manifest、checksums、Review result、Human decisionの不一致。
- Review後のCandidate／HEAD／target drift。
- unsafe archive、unsafe destination、secret検出。
- rollback未確認、remote divergence、required validation failure。
- 実装中にInitiative／Epic境界またはshared lifecycle変更が必要になった場合。

これらはsilent fallbackせず、原因と次の安全なactionを返す。

## 7. Completion Boundary

本Issueの完了には、AC-001〜AC-014の実装証拠、focused tests、full relevant regression、JIT dogfood、provider／installed／dogfood parity、required code／QA review、Delivery PRのmerge-ready handoffが必要である。Planning文書の承認だけでは完了しない。
