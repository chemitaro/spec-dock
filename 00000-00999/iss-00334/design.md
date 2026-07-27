---
種別: 設計書（Issue）
ID: "iss-00334"
タイトル: "Implement ChatGPT Issue Planning Workflow"
状態: "approved"
作成者: "Blue Team"
最終更新: "2026-07-27"
依存: ["requirement.md"]
親: ["epic-00331", "init-00322"]
planning_profile_guidance: "strict"
---

# iss-00334 Implement ChatGPT Issue Planning Workflow — 設計

## 0. Design Position

本設計はE1-I1のwalking skeletonを一つのvertical implementation sliceとして実装するcanonical Designである。Candidate由来のprovenanceは`report.md`へ分離し、本書はcurrent implementation contractだけを所有する。Mainがassurance classification／composition、fresh Review、Human implementation-start gateを完了するまでimplementation authorityは成立しない。

## 1. Responsibility Model

| Component / Actor | Responsibility | Must not do |
|---|---|---|
| Human | Issue Plan adoption、implementation start、merge decision | automated approvalを委任しない |
| Planning Skill | active scope確認、context framing、mode／lane／Human Gate選択、Main handoff | raw outputをauthority化しない |
| Codex Main | source inspection、deterministic placement、Git transaction、evidence integration | semantic reviewを代行しない |
| `spec-dock-chatgpt` | target/Git preflight、closed Prompt、Oracle/backend invocation、artifact retrieval、Human-supplied apply evidenceのpublic受付 | Human decision生成、unbound lifecycle mutation、semantic adoption、mergeを行わない |
| Core Runtime | three-document response validation、immutable Issue Candidate packaging、archive validation、identity、adoption/parity、validation/publication/readiness evaluation | Human decisionを生成しない |
| Oracle/backend | browser/session/transport and downloadable artifact retrieval | SpecDock authorityを付与しない |
| ChatGPT Planner | complete三文書response生成 | control-file生成、canonical write、assurance writeを行わない |
| ChatGPT Reviewer | read-only Review result生成 | Candidate、patch、repositoryを変更しない |

## 2. System Context

```text
Human
  → spec-dock-issue-planning Skill
      → Codex Main context framing
          → spec-dock-chatgpt
              → Git preflight
              → closed Prompt resources
              → Oracle/backend
                  → ChatGPT Planner / Reviewer
          ← downloaded Candidate / Review result
      → Main deterministic adoption and publication
      → Core Runtime parity / validation / readiness evaluation
  → existing shared delivery workflow after S99
```

`spec-dock-chatgpt`はindependent repo-local entrypointだが、安全性実装を複製しない。existing `authoring_pack` Git preflight、direct-argv backend、archive review、digest、approval validationをthin application façadeから再利用する。

## 3. Public Command Design

```text
./spec-dock/scripts/spec-dock-chatgpt planning create --issue <id> --output <external-dir>
./spec-dock/scripts/spec-dock-chatgpt planning revise --candidate <zip-or-tree> --lane <semantic|mechanical> --output <external-dir>
./spec-dock/scripts/spec-dock-chatgpt review planning --mode archive-candidate --candidate <zip> --logical-filename <name> --zip-sha256 <sha256> --output <external-dir>
./spec-dock/scripts/spec-dock-chatgpt review planning --mode git-bound --reviewed-head <sha> --target <repo-relative-path> --output <external-dir>
./spec-dock/scripts/spec-dock-chatgpt planning apply --issue <id> --mode <archive-candidate|git-bound> --review-result <external-json> --human-decision <external-json> --decision-artifact <issue-artifacts-relative-json> --expected-head <sha> [mode identity] --output <external-dir>
```

- parser／dispatchは上記四つのChatGPT planning commandだけを公開する。
- `planning create`はscope、parent、dependencies、source HEADを解決し、closed Promptからcomplete三文書responseを要求する。response検証後、Core Runtimeがmandatory controlsを生成してimmutable Issue Candidate ZIPをfinal public artifactとして返す。
- `planning revise`はSkillが選択済みlaneを受ける。CLIはlaneを推測しない。
- `review planning`はmodeを推測せず、archive identityまたはgit identityを検証してread-only reviewerを起動する。
- `planning apply`は後半lifecycleの唯一のsupported public entrypointである。archive modeでは`--candidate <zip>`、`--logical-filename <name>`、`--zip-sha256 <sha256>`を、git-bound modeでは`--reviewed-head <sha>`とrepeatable `--target <repo-relative-path>`を追加必須とする。両modeでreview result、Human decision、decision artifact destination、expected HEAD、external output directoryを要求し、欠落またはmode混在をparser／domain validationでrepository mutation前に拒否する。
- `--decision-artifact`はactive Issueの`artifacts/` direct childにある新規lowercase JSON pathだけを受け付け、既存file、symlink parent、scope外pathを拒否する。Runtimeは`--human-decision` bytesとSHAを検証し、そのexact bytesだけをcanonical artifactへ追加する。
- text／JSONは同じstable `status`を返す。`ready`だけexit `0`、`blocked`、`stale`、`rejected`、`rolled_back`、`publication_pending`、`blocked_remote_diverged`、`recovery_required`はexit `1`。resultはoperation ID、source/review/Human identity digest、mutation phase、local/remote HEAD、evidence locators、bounded remediationを含み、Human approvalやreviewer passを生成しない。
- output directoryはrepository／canonical tree外のexisting non-symlink directoryに限定する。

## 4. Core Contracts

### 4.1 Planning Request

```text
PlanningRequest
- scope_id = iss-00334形式のexisting Issueまたはapproved Seed
- repository / branch / expected_head
- parent_epic / parent_initiative
- dependency_state
- relevant_paths
- operator_context (redacted free-form)
- prompt_resource_id
- output_directory
```

### 4.2 Planner Response, Runtime Package, and Candidate Identity

```text
ChatGPTPlannerResponse
- requirement.md
- design.md
- plan.md

RuntimeIssueCandidatePackage
- requirement.md
- design.md
- plan.md
- SOURCE-BASELINE.json
- MANIFEST.json
- CHECKSUMS.sha256
- PLACEHOLDER-ORACLE-MAP.json
- optional package-only artifacts only when explicitly declared

CandidateIdentity
- version = 1 for initial create, predecessor version + 1 for revision
- one run-scoped UTC timestamp captured once after complete-response validation
- logical_filename = <timestamp>-<scope>-issue-planning-candidate-v<version>.zip
- candidate_id = <scope>-v<version>-<timestamp>
- internal_root = logical filename stem + "/"
- source_repository / source_branch / source_head from exact Git preflight
- external_zip_sha256 computed after immutable archive close (outside the ZIP)
```

S05 is the sole implementation owner for final package construction and Candidate identity finalization. Packaging writes to an owned temporary path in the safe external output directory and publishes the final ZIP atomically; existing final targets are never overwritten. ChatGPT response files remain semantic source bytes and are not rewritten during control-file generation. Transport filenameはlogical identityではない。closed `(N)` aliasだけをnormalizeし、normalized logical filename、ZIP SHA、root、MANIFEST identityが一致しない場合はinsufficient evidenceとする。

### 4.3 Review Identity

```text
archive-candidate:
- logical filename / observed transport filename / ZIP SHA
- internal root / candidate ID
- source repository / branch / HEAD

git-bound:
- repository / branch / reviewed HEAD
- exact target paths
- semantic base or merge base when required
```

### 4.4 Human Authorization Evidence

Human decisionはexact reviewed identity、decision owner、timestamp、scope、decisionを持つcanonical Issue Artifactへ記録する。Workbench source JSONとそのSHAをprovenanceとして保持し、raw transcriptを保存しない。

### 4.5 Readiness Result

```text
ReadinessResult = conjunction(
  exact future Review result,
  exact Human decision,
  mode-specific parity,
  validation,
  Planning publication remote parity
)
```

専用state storeへ永続化せず、current Git／GitHub／canonical artifactsから再構成する。

### 4.6 Apply Request and Operation Identity

```text
PlanningApplyRequest
- issue_id / repository / branch / expected_head
- mode = archive-candidate | git-bound
- review_result_path + review_result_sha256
- human_decision_path + human_decision_sha256
- decision_artifact_repo_path
- archive identity:
    candidate_path / logical_filename / external_zip_sha256
  or git identity:
    reviewed_head / exact_target_paths
- output_directory

PlanningApplyOperation
- operation_id = sha256(canonical JSON of all identity-bearing request fields)
- phase = preflight | staged | replaced | validated | committed | pushed | verified
- planning_commit trailer = SpecDock-Planning-Operation: <operation_id>
```

operation IDはtimestampやhost pathを含めず、same reviewed identity／Human decision／mode identity／source bindingからpureに導出する。external output directory配下のoperation-local directoryはstage、backup、recovery manifestだけを保持し、global registryとして列挙・検索する機能を持たない。

## 5. One Adoption and Publication Lifecycle

```text
Candidate or reviewed git target at H0
→ future read-only Review bound to H0
→ Human decision bound to H0
→ archive atomic adoption + candidate parity
   OR git-bound reviewed-blob-preserving adoption
→ validate
→ dedicated Planning commit H1
→ push / fetch / remote == H1 / tree parity
→ readiness derived from all evidence
```

- archive publicationのsource parentはreviewed source `H0`。
- git-bound target blobsはreviewed `H0`のbytesを維持する。
- closed authorized adoptionは同じreviewed planning identityを消費する。source／target／Prompt inventory／profile／authorityのunauthorized driftだけが再Planningを要求する。
- Review output、Human decision、adoption、publicationは異なるauthorityであり、一つのresultへ統合しない。

### 5.1 Apply State Machine and Transaction Boundary

```text
preflight
  → validate all immutable inputs
  → stage decision artifact + canonical replacement set outside repository
  → validate staged set
  → backup existing canonical bytes/modes
  → add decision artifact
  → replace requirement → design → plan
  → validate canonical bytes, parity, and exact diff
  → create one Planning commit with operation trailer
  → push
  → fetch and verify remote HEAD/tree
  → ready
```

- `ScopedFileTransaction`を`infra/scoped_file_transaction.py`へ置き、`runbook_store.py`のcurrent stage／backup／restore behaviorを同primitiveへ移してcharacterization testsを維持する。Issue Planningは同primitiveを使用し、private helperをimportせず、同等実装を複製しない。
- mutation前にCandidate／git identity、review result、Human decision、decision destination、clean branch、upstream、local==remote==expected HEAD、operation directory safetyをすべて検証する。失敗時はfilesystem／index／HEADを変更しない。
- stage完了後からcommit成功前までの例外、validation failure、commit failure、process interruptはreverse-order restoreを試み、decision artifactを除去し、original bytes／mode／index／HEAD／`git status --porcelain=v1`を照合する。成功は`rolled_back`、一点でも不一致なら`recovery_required`で停止する。
- recovery manifestは各targetのbefore digest、staged digest、backup locator、completed phaseをatomic updateする。crash後のsame-operation invocationだけがmanifestを読み、commitが存在しなければrollbackを完了してclean baselineから再開する。異なるoperationは既存manifestを上書きしない。
- commit成功後はautomatic rollback、reset、amend、force pushを行わない。push失敗またはresponse lossではlocal H1を保持して`publication_pending`を返す。same-operation retryはcommit trailer、exact tree、parent H0を照合してpushから再開する。
- retry時にremote==H1ならpush済みとしてremote/tree verificationへ進む。remoteがH0でもlocal H1がexactならpushをretryする。それ以外は`blocked_remote_diverged`とし、Human／Mainへreconcileを返す。
- success時はbackupを削除する。external result JSONは観測Evidenceであり、readiness authorityはreview、Human decision、canonical parity、validation、local/remote commit/treeから再構成する。

## 6. Review Transport and Isolation

### 6.1 archive-candidate

- default for pre-canonical semantic iteration。
- single root、regular UTF-8 text、MANIFEST／CHECKSUMS、source bindingを検証する。
- outer ZIP 10,000,000 bytes、64 entries、per-entry 2,000,000 bytes、expanded total 10,000,000 bytes、path 240 UTF-8 bytes、compression ratio 100をinclusive ceilingとする。
- rejected inputからfinal extraction tree、review result、adoption outputを残さない。

### 6.2 git-bound

- actual repository path、CI、inline review、merge-base等が必要なときだけ選択する。
- exact reviewed HEAD、target paths、BASEを固定する。
- archiveへsilent fallbackせず、別modeへ切り替える場合はnew Review identityとする。

### 6.3 Read-only guard

1. Review前にCandidate SHAと`git status --porcelain=v1`を記録する。
2. Reviewerへread-only sourceとseparate output directoryだけを渡す。
3. Review後にCandidate SHAとtracked/untracked inventoryを再取得する。
4. Candidateまたはrepository mutationがあればReview resultをinvalidとする。

forensic database、custom refs、generalized mutation inventoryは作らない。

## 7. Revision Lanes

| Lane | Allowed | Executor | Result |
|---|---|---|---|
| Semantic | Requirement、Architecture、scope、AC、Gate、Workflow meaning | ChatGPT Blue Team | complete replacement Candidate |
| Mechanical | closed path／field／literal、meaning invariant、bounded diff | Main／deterministic script | complete new Candidate identity or bounded git correction |

Skillがlaneを選択する。CLI／wrapperはmaterialityを推測しない。Review findingがparent boundaryやshared policyへ属する場合、本Issueへ取り込まずowning scopeへrouteする。

## 8. Provider-first Implementation

### 8.1 Module Dependency

```text
spec-dock-chatgpt entrypoint
  → chatgpt CLI parser / restricted registry
    → planning command handlers
      → issue planning application service
        → existing authoring_pack preflight / backend / review / approval primitives
        → planning domain contracts
        → filesystem / Git / Oracle adapter
      → planning presentation renderer
```

Provider `src/spec_dock/`がimplementation authorityであり、root `spec-dock/`はgenerated dogfood projectionである。workerはgenerated projectionを直接編集しない。

### 8.2 Directory / File Change Plan

```text
src/spec_dock/
├── cli.py                                           # install/update executable handling
└── assets/
    ├── install_root/.agents/skills/spec-dock-issue-planning/SKILL.md
    └── spec_dock/
        ├── docs/
        │   ├── README.md
        │   ├── workflow_planning.md                 # new shared planning reference
        │   └── reference_chatgpt_cli.md             # new CLI reference
        ├── system/prompts/issue-planning/
        │   ├── create.md
        │   ├── revise.md
        │   └── review.md
        └── scripts/
            ├── spec-dock-chatgpt                    # new independent executable
            └── spec_dock_runtime/
                ├── chatgpt_app.py
                ├── cli/chatgpt_parser.py
                ├── commands/planning.py
                ├── application/issue_planning.py
                ├── domain/issue_planning_contracts.py
                ├── domain/authoring_pack/zip_contract.py # bounded additive shared archive contract
                ├── infra/issue_planning_io.py
                ├── infra/scoped_file_transaction.py
                ├── infra/runbook_store.py               # shared transaction primitiveへ移行
                └── presentation/issue_planning.py

tests/
├── cli_runtime/test_authoring.py                  # existing generic archive default regression
├── cli_runtime/test_chatgpt_planning.py
├── manual_tests/test_review_chatgpt_authoring_pack.py # existing compatibility regression
├── unit/application/test_issue_planning.py
├── unit/domain/test_issue_planning_contracts.py
├── unit/infra/test_issue_planning_archive.py
├── unit/infra/test_scoped_file_transaction.py
├── unit/infra/test_runbook_store.py
├── unit/infra/test_init_update.py
├── unit/presentation/test_issue_planning.py
└── integration/
    ├── test_chatgpt_planning_fake_oracle.py
    └── test_chatgpt_planning_dogfood.py
```

既存`authoring_pack` archive primitiveはS05でだけbounded additive extensionする。`review_pack_input(input_path)`の既存default root、required metadata、limits、status taxonomyを変えず、closed data-only `ArchiveReviewContract` parameterへ既存defaultとIssue Candidate用の二つのnamed contractを与える。Issue contractはexpected root、mandatory paths、既存ceiling、Candidate identity fieldsを列挙するだけであり、plugin registry、callback framework、parallel validator、new state storeを導入しない。既存default behaviorを保てない場合はstopし、Design amendmentへ戻る。

## 9. Prompt and Output Design

- Prompt resourceはprovider-managed Markdownで、scope identity、parent context、exact source、closed output contract、security constraintsを含む。
- ChatGPT Planner responseはexactly three complete Markdown files (`requirement.md`, `design.md`, `plan.md`)であり、control filesやReview resultを含めない。
- Core Runtime final artifactは三文書と`SOURCE-BASELINE.json`、`MANIFEST.json`、`CHECKSUMS.sha256`、`PLACEHOLDER-ORACLE-MAP.json`を必須とするsingle-root immutable ZIPである。optional package-only artifactはMANIFESTへ明示された場合だけ含められる。
- incomplete／duplicate／unexpected response file、non-UTF-8、authority claim、raw transcript、secret-like payloadをpackaging前に拒否する。mandatory controls、inventory、checksum、identity、source bindingの不一致はfinal ZIPまたはReview outputを残さず拒否する。
- `planning create`の成功resultはfinal ZIP path、logical filename、Candidate ID、version、internal root、source binding、external ZIP SHAを返し、そのpathをそのまま`review planning --mode archive-candidate`へ渡せる。
- Placeholder verificationはdeclared dynamic files／tokensだけに適用し、map外static filesはexact hashで扱う。

## 10. Human Gate and Adoption

- Review resultはHuman decisionの入力であり、start authorityではない。
- archive Human decisionはlogical filename／ZIP SHAへbindする。
- git-bound Human decisionはreviewed HEAD／target pathsへbindする。
- MainだけがHuman-supplied evidenceを確認して`planning apply`を起動する。CLI／Runtimeはそのevidenceを生成・推測しない。
- Runtimeはshared transaction primitiveでcanonical filesとnew decision artifactを処理し、Main authority下でGit commit／pushを行う。unexpected Candidate-external diffは0でなければならない。
- RuntimeはPA-NF-01〜PA-NF-10を独立に拒否する。
- Candidate adoptionやreadinessの副作用として`.assurance.json`を変更しない。

## 11. Security and Failure Handling

| Failure | Result | Recovery |
|---|---|---|
| GitHub access／HEAD mismatch | blocked／stale, backend not started | branch／remoteを修正してnew run |
| unsafe Prompt／attachment／output path | rejected | safe external pathを選択 |
| backend missing／timeout／nonzero | blocked, bounded redacted diagnostic | same session recovery／Human Relay under same contract |
| malformed／partial bundle | failed, no canonical mutation | Semantic revision or rerun |
| unsafe archive／integrity mismatch | rejected, no final extraction | new complete Candidate |
| Review mutation detected | invalid Review evidence | restore clean state and fresh Review |
| Human rejection | no adoption | feedback-bound new Candidate／git correction |
| replacement／pre-commit validation／commit failure | `rolled_back` or `recovery_required`, no readiness | reverse-order restoreを検証。restore不完全なら自動続行禁止 |
| push failure／response loss after commit | `publication_pending`, no readiness | same operation identityでcommit/treeを照合しpush／remote verificationからresume |
| retry時のremote divergence | `blocked_remote_diverged`, no readiness | force push／resetせずHuman／Main reconcile |

Sensitive diagnostics are bounded and redacted. Direct argv is default. Shell exception is unavailable without explicit Human-approved Design and rollback evidence.

## 12. Compatibility and Projection

- `uv build` produces wheel／sdist using repository provisioning.
- fresh environments install each artifact and run `spec-dock init` and `spec-dock update`.
- both repo-local entrypoints are regular non-symlink files with executable mode on POSIX and can run directly.
- provider managed file set equals installed and dogfood projections after init/update.
- existing Core CLI, authoring-pack tests, validate／sync behavior remain green.
- physical removal of old planning routes remains E1-I3 work; this Issue only adds and activates the replacement path needed for its acceptance.

## 13. JIT Dogfood

S09Aではfake backend／fake remote／temporary repositoryだけを使うhermetic testとして、eligible／ineligible selection、pre-mutation abort、transaction rollback、publication retryを検証する。S09Aのworkerはcredential、live backend、real canonical path、push authorityを持たない。

S09BはMain/Human operation gateであり、pytestではない。Humanがtarget Issue、dedicated clean worktree／branch、selected mode、許可するcanonical paths、push先、evidence destinationを明示承認した場合だけMainが実行する。Mainは開始前にtargetがREQ-018を満たすこと、他作業がないこと、pre-commit rollback pathがGreenであることを記録する。abort／failureは§5.1に従い、push済みcommitの取り消しは自動化せず別のHuman-authorized revertとして扱う。Dogfood evidenceはiss-00334 `artifacts/` direct childとtargetのauthorized decision artifactへ保存し、raw transcriptやcredentialを残さない。

## 14. Risk Register

| Risk ID | Risk | Design control | Verification owner |
|---|---|---|---|
| RISK-001 | multi-file partial adoptionでcanonical bytesが混在する | shared scoped transaction、reverse restore、recovery manifest、fault injection | S06 |
| RISK-002 | unsafe／ambiguous archiveがresource exhaustionまたはpath escapeを起こす | closed Issue archive contract、class-by-class fail-closed matrix、partial-output 0 | S05 |
| RISK-003 | live dogfoodが別Issue／remoteへ無許可変更する | S09A hermetic testとS09B Human/Main gateの分離 | S09A/S09B |
| RISK-004 | shared archive／runbook behaviorが新機能で退行する | default contractとrunbook characterizationを先に固定 | S05/S06/S08 |
| RISK-005 | commit済みpush失敗をrollbackして履歴／identityを曖昧にする | `publication_pending`、operation trailer、same-operation resume、no force/reset | S06 |

## 15. External Delivery Boundary

After S99, Main uses the current shared delivery workflow for PR delivery and merge preparation. The implementation remains one Issue／one branch／one Delivery PR; required review precedes Human-only merge. This design does not redefine report/HEAD ordering, merge strategy, `issue finish`, or lifecycle recovery.
