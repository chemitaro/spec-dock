---
種別: 設計書（Issue）
ID: "iss-00334"
タイトル: "Implement ChatGPT Issue Planning Workflow"
状態: "draft"
作成者: "Blue Team"
最終更新: "2026-07-27"
依存: ["requirement.md"]
親: ["epic-00331", "init-00322"]
planning_profile_guidance: "strict"
---

# iss-00334 Implement ChatGPT Issue Planning Workflow — 設計

## 0. Design Position

本設計はE1-I1のwalking skeletonを一つのvertical implementation sliceとして実装する。Candidateはunreviewed Evidenceであり、MainがCandidate外でassurance classification／composition、fresh Review、Human Gateを完了するまでimplementation authorityを持たない。

## 1. Responsibility Model

| Component / Actor | Responsibility | Must not do |
|---|---|---|
| Human | Issue Plan adoption、implementation start、merge decision | automated approvalを委任しない |
| Planning Skill | active scope確認、context framing、mode／lane／Human Gate選択、Main handoff | raw outputをauthority化しない |
| Codex Main | source inspection、deterministic placement、Git transaction、evidence integration | semantic reviewを代行しない |
| `spec-dock-chatgpt` | target/Git preflight、closed Prompt、Oracle/backend invocation、artifact retrieval | lifecycle mutation、semantic adoption、mergeを行わない |
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
./spec-dock/scripts/spec-dock-chatgpt review planning --mode <archive-candidate|git-bound> ... --output <external-dir>
```

- parser／dispatchはChatGPT command familyだけを公開する。
- `planning create`はscope、parent、dependencies、source HEADを解決し、closed Promptからcomplete三文書responseを要求する。response検証後、Core Runtimeがmandatory controlsを生成してimmutable Issue Candidate ZIPをfinal public artifactとして返す。
- `planning revise`はSkillが選択済みlaneを受ける。CLIはlaneを推測しない。
- `review planning`はmodeを推測せず、archive identityまたはgit identityを検証してread-only reviewerを起動する。
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
                └── presentation/issue_planning.py

tests/
├── cli_runtime/test_authoring.py                  # existing generic archive default regression
├── cli_runtime/test_chatgpt_planning.py
├── manual_tests/test_review_chatgpt_authoring_pack.py # existing compatibility regression
├── unit/application/test_issue_planning.py
├── unit/domain/test_issue_planning_contracts.py
├── unit/infra/test_issue_planning_archive.py
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
- Mainだけがcanonical filesをatomic replaceし、Git commit／pushする。
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
| adoption parity／validation／publication failure | no readiness | rollback atomic replacement where applicable; reconcile and re-review if semantic |

Sensitive diagnostics are bounded and redacted. Direct argv is default. Shell exception is unavailable without explicit Human-approved Design and rollback evidence.

## 12. Compatibility and Projection

- `uv build` produces wheel／sdist using repository provisioning.
- fresh environments install each artifact and run `spec-dock init` and `spec-dock update`.
- both repo-local entrypoints are regular non-symlink files with executable mode on POSIX and can run directly.
- provider managed file set equals installed and dogfood projections after init/update.
- existing Core CLI, authoring-pack tests, validate／sync behavior remain green.
- physical removal of old planning routes remains E1-I3 work; this Issue only adds and activates the replacement path needed for its acceptance.

## 13. JIT Dogfood

Human selects one target near feature completion using the eligibility conditions in Requirement REQ-018. Main records selection externally, runs the selected archive or git-bound positive chain, captures metrics, and verifies no current Portfolio or downstream Issue planning mutation. Dogfood output is evidence, not the primary product artifact.

## 14. External Delivery Boundary

After S99, Main uses the current shared delivery workflow for PR delivery and merge preparation. The implementation remains one Issue／one branch／one Delivery PR; required review precedes Human-only merge. This design does not redefine report/HEAD ordering, merge strategy, `issue finish`, or lifecycle recovery.
