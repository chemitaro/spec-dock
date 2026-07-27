---
種別: "fresh canonical planning review"
Issue: "iss-00334"
reviewer_role: "spec-reviewer"
review_status: "fail"
source_repository: "chemitaro/spec-dock"
source_branch: "iss-00334-implement-chatgpt-issue-planning-workflow"
source_head: "2984c696b4c7e94cbed6fd63697a563f55fd3631"
review_transport: "chatgpt-use browser-only with GitHub connector"
chatgpt_session: "iss00334-chatgpt-first-fresh-review"
model_selection: "requested=Pro; resolved=Pro; verified=yes"
created_at_utc: "2026-07-27T00:46:53Z"
authority: "read-only reviewer verdict"
---

# iss-00334 ChatGPT-first fresh canonical planning review — FAIL

## Verdict

- `review_status: fail`
- `S01_admission: blocked`
- P0: 0
- P1: 2
- P2: 2

前回のP1-02〜P1-09は実質的に閉鎖された。一方、authority-bearing evidence JSON contractとmode-neutralなplanning review identityが未確定であり、S01を開始すると実装者がmaterial contractを発明するためFAILとする。

このreviewはread-onlyであり、patch、replacement document、revised ZIP、repository mutationを生成していない。

## Repository access evidence

ChatGPT reviewerはGitHub connectorで次を確認した。

| Field | Observed value |
|---|---|
| Repository | `chemitaro/spec-dock` |
| Branch | `iss-00334-implement-chatgpt-issue-planning-workflow` |
| Default branch | `main` |
| Exact HEAD | `2984c696b4c7e94cbed6fd63697a563f55fd3631` |
| Branch/HEAD parity | current branchとexact HEADはidentical、ahead/behind 0 |
| Baseline delta | `eadbfa544ad972c799162552f5684482d26e89b5`から1 planning-only commit。implementation source変更なし |

Representative GitHub paths:

- canonical Issue `requirement.md`、`design.md`、`plan.md`、`report.md`、`.assurance.json`
- previous formal FAIL artifact
- parent `epic-00331` Requirement／Design／Plan
- parent `init-00322` Requirement／Plan
- Issue workflow／authoring docs
- authoring-pack approval、candidate、archive、workflow state、runbook transactionのsourceとtests

## Attachment identity

| Artifact | SHA-256 | GitHub exact HEAD parity |
|---|---|---|
| `requirement.md` | `ad6a7ddea25f459d7692d2746e6061b1d692bb6f543aaaa27d28c78e2794d501` | exact |
| `design.md` | `a16f2d612633eec0d2ab77dca593ffbcf889539f4d1be0d8288f6d22724fe84f` | exact |
| `plan.md` | `898a12afa984651a27905fb4d200e8aa6a8fd114f14df76806d6f28cf5f5b5ff` | exact |
| `report.md` | `3babd1fd8f0e993ca8321d0b05a3bacf01d5546c6d598ea7b713f666814b2f92` | exact |
| `.assurance.json` | `adb6be58f1530d3e463851497feb86123485b434230a99a0c505a4a779e42729` | exact |
| previous formal FAIL | `0bf6266c7340dece890809ceaed09ce8d0c5d20f3545b55207fc417654ab6f43` | exact |

## Previous P1 closure matrix

| Previous finding | Verdict | Evidence |
|---|---|---|
| P1-01 Public apply route | open | public routeは追加済みだが、Review result／Human decision JSONのclosed versioned schemaがない |
| P1-02 Crash-safe transaction | closed | Design §5.1とS06がrollback、recovery、post-commit resume、divergenceを固定 |
| P1-03 REQ-022 archive closure | closed | 25 classとinclusive boundary、partial-output zeroを個別追跡 |
| P1-04 Closure Index schema | closed | required fieldsとREQ／EC／PA-NF／archive／riskのindividual rowsが存在 |
| P1-05 S02 ownership | closed | S02A docs／S02B testへ分離 |
| P1-06 S09 boundary | closed | S09A hermetic／S09B Main-Human live gateへ分離 |
| P1-07 source binding | closed | implementation-surface baselineとcurrent planning-only HEADを区別し、Assuranceをcurrent三文書SHAへbind |
| P1-08 canonical authority | closed | 三文書はapproved/currentで、Candidate provenanceはReportへ分離 |
| P1-09 Assurance／Report | closed | standard authority、strict相当overlay、specialist evidence、observed commands、previous failを実値化 |

## Coverage verdicts

| Surface | Verdict |
|---|---|
| Requirement | pass |
| Design | fail |
| Plan | fail |
| Closure Index | pass — structural |
| Assurance | pass — source binding |
| Report | pass — current-state ledger |
| S01 admission | blocked |

## Blocking findings

### P1-01 — `planning apply` evidence JSON contracts are not closed

Owner: `design.md` §§3, 4.3, 4.4, 4.6。Affected Plan: S01、S06、`CLOS-REQ-009`、`CLOS-REQ-015`、PA-NF-01〜07。

`--review-result`と`--human-decision`はpath／digestと概念項目だけを持ち、次が未確定である。

- schema versionとevidence kind
- 必須keyとunknown-key policy
- Review verdictの許可値、reviewer role、freshness、read-only authority
- archive／git-boundのmode-specific identity
- Review result自身のdigest binding
- Human decisionの許可値
- Plan adoptionとimplementation startの両方を承認する表現
- approver identityとtimestamp形式
- rejected／revoked decision
- wrong mode／wrong identity／stale evidenceのstatus mapping

既存approval validatorはCandidate decomposition／node creation用の別contractである。新subsystemを追加せず、二つのversioned named closed data contract、または既存contractの明示的named extensionとして定義し、S06 testsへ接続する必要がある。

### P1-10 — Plan start gate excludes the approved git-bound mode

Owner: `plan.md` §2、S01 `depends on / unblocks`。

Requirement／Designはarchive-candidateとgit-boundを正式modeとして許可するが、Planは`exact current Candidate identity`と`future exact Candidate Review`だけを開始条件にしている。今回のcanonical GitHub HEAD reviewをS01 gateへ接続するには、Candidate identityへの再解釈またはwaiverが必要になる。

Planをmode-neutralな`exact reviewed planning identity`へ変更し、archiveはCandidate identity、git-boundはrepository／branch／reviewed HEAD／exact target pathsを使用する。Human adoption／implementation-start authorizationは同一identityへbindし、省略してはならない。

## Nonblocking findings

### P2-01 — S01 positive target-resolution oracle

S01 behavior goalはexact Issue target解決を含むが、testsはhelpとunknown target rejectionだけである。known-valid IssueについてIssue path、parent、dependency、repo root、fallback absenceを観測するpositive testを追加するか、target resolutionと`CLOS-EC-001`をS03へ移す必要がある。

### P2-02 — S03 test ownership

S03 allowed test filesはplanning application／integration testだけだが、`tc-s03-003`はallowlist外の`tests/unit/authoring_pack/test_github_fetch_policy.py`をverification methodにしている。planning-specific argv／redaction fixtureをS03 allowed testへ置き、既存Git fetch testはcovered-existing regressionとして分離する必要がある。

## Assumptions and uncertainty

- GitHub repository／branch／HEAD／blob identityはconnectorで直接確認した。
- local worktree cleanはreview brief supplied factであり、GitHubからは再確認できない。
- `spec-dock validate`、assurance classify／verify、compose dry-runはReport記録を確認したが、reviewer自身は再実行していない。
- `.assurance.json`のbytesとcurrent三文書SHA bindingは直接確認した。
- current `failed` rowsはprevious verdictの正直な履歴として扱い、今回 verdict の未記録をfindingにしていない。
- 本reviewはHuman adoption、implementation-start、merge authorityを生成しない。

## Required next action

別のChatGPT Blue Team threadでP1-01、P1-10、P2-01、P2-02のbounded correctionを具体化し、Mainがowner文書へ反映する。Assuranceを新しいDesign／Plan SHAへ再bindし、Reportへ本reviewとadoption decisionを記録してremoteへpushする。その後、別のfresh ChatGPT review threadで再審査する。
