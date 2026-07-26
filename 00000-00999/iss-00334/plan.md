---
種別: 実装計画書（Issue）
ID: "iss-00334"
タイトル: "Implement ChatGPT Issue Planning Workflow"
Issue Grade: "strict"
状態: "draft"
作成者: "Blue Team"
最終更新: "2026-07-27"
関連Requirement: ["requirement.md"]
関連Design: ["design.md"]
関連Report: ["report.md"]
親: ["epic-00331", "init-00322"]
planning_profile_guidance_source: "Main-supplied current guidance; no assurance mutation by Candidate"
---

# iss-00334 Implement ChatGPT Issue Planning Workflow — Issue 実装計画書（Strict / Spec-Locked TDD）

## 0. 文書の位置づけ

本書はplanned executable workflow contractである。実績、逸脱、Review結果、commit evidenceはcanonical `report.md`へMainが記録する。Candidate packageはunreviewed／non-authoritativeであり、このPlanの存在だけではimplementation startを許可しない。

Mainは実装開始前に既存assurance workflowをCandidate外で実行する。Candidateは`.assurance.json`を変更しない。本Planは供給済み`strict` guidanceのsemantic obligationsを満たすが、assurance authorityを自己付与しない。

## 1. この計画で満たす要件ID

`REQ-001`〜`REQ-024`および`AC-001`〜`AC-017`。ID数自体はproduct acceptanceではなく、Requirement本文のmeaningとobservable behaviorがauthorityである。

## 2. Plan Readiness and Stop Gate

Implementationは次がすべて成立するまで開始しない。

- exact current Candidate identityへbindされたfuture fresh Planning Review result。
- exact reviewed identityへbindされたHuman Issue Plan Adoption and Implementation-Start Authorization。
- Mainによるcanonical adoption／source refresh／assurance classification and composition。
- adopted `requirement.md`／`design.md`／`plan.md`とfresh spec review evidence。
- clean named branch、upstream、local HEAD == remote HEAD、no unresolved ledger entry。

不足時は`blocked`または`未完了`としてMainがreason／next actionをCandidate外reportへ記録する。

## 3. Implementation Strategy

- one observable behavior per implementation step。
- provider-first。root dogfood projectionを直接編集しない。
- Mainはinspect／plan／delegate／verify／integrate／reportを所有し、product code／tests／shipped docsを通常は直接実装しない。
- code/runtime/testsは`dev-coder`、shipped docs／Skill／Prompt textは`doc-writer`へ委任する。
- each step: closure contract → delegation → bounded batch → verification → tidy → Main report integration → fresh reviewer → Result Approval → commit candidate → clean check。
- unknown failure、new authority、shared policy change、scope expansionは実装で吸収せずamendment／owning scopeへ戻す。

## 4. Scope and Change Surface

### Allowed provider surfaces

- `src/spec_dock/cli.py`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
- `src/spec_dock/assets/spec_dock/docs/**`の本Planで列挙したPlanning docs
- `src/spec_dock/assets/spec_dock/system/prompts/issue-planning/**`
- `src/spec_dock/assets/spec_dock/scripts/spec-dock-chatgpt`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**`の本Planで列挙したPlanning modules
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/zip_contract.py`のS05 bounded additive extension
- focused `tests/**` paths listed per step
- `pyproject.toml` only if packaging declaration is required by S07

### Forbidden changes

- current Portfolio boundary／dependency。
- downstream Issue Requirement／Design／Plan。
- `.assurance.json`。
- shared Issue delivery／merge／finish／lifecycle authority。
- root generated `spec-dock/` direct implementation edits。
- arbitrary legacy removal owned by E1-I3。
- new workflow database、receipt registry、custom Git ref、または新しいpersistent coordination subsystem。

## 5. Dependency-derived Order

```text
S01 CLI shell
 → S02 official Skill / closed Prompt authority
 → S03 Planner response / Git preflight
 → S04 revise response
 → S05 Runtime Candidate packaging / Review / archive integrity
 → S06 Human gate / adoption / publication / readiness
 → S07 installer / projection
 → S08 integrated compatibility
 → S09 JIT dogfood
 → S90 docs impact resolution
 → S99 final quality gate
 → Final Exit via current shared delivery workflow
```

## 6. Step Summary

| Step | Outcome | Depends on | Unblocks | Related AC |
|---|---|---|---|---|
| S01 | Independent CLI walking skeleton | future exact Candidate Review／Human adoption and implementation-start authorization | S02 | AC-002 |
| S02 | Official Skill and closed Prompt resources | S01 | S03 | AC-001, AC-011 |
| S03 | Git-bound Planner response flow | S02 | S04 | AC-003, AC-011 |
| S04 | Semantic and mechanical revision response | S03 | S05 | AC-004 (revision-lane behavior) |
| S05 | Runtime Issue Candidate packaging, read-only Planning Review, and archive integrity | S04 | S06 | AC-001, AC-004, AC-005, AC-006, AC-007, AC-017 |
| S06 | Human gate, adoption, publication, and derived readiness | S05 | S07 | AC-008, AC-009, AC-010, AC-013 |
| S07 | Installer and provider projection | S06 | S08 | AC-012, AC-015 |
| S08 | Integration, compatibility, and adoption negatives | S07 | S09 | AC-003, AC-004, AC-005, AC-006, AC-007, AC-008, AC-009, AC-010, AC-011, AC-015 |
| S09 | Human-selected JIT dogfood | S08 | S90 | AC-014 |
| S90 | docs／Skill／reference impact resolved | S09 | S99 | AC-001, AC-012, AC-015 |
| S99 | final QA/code/spec quality evidence | S90 | Final Exit | all |

## 7. 要件 ↔ ステップ対応

| Requirement group | Owning implementation step(s) |
|---|---|
| Official Skill／CLI／Prompt | S01, S02 |
| Planner response／revision lane | S03, S04 |
| Runtime final Candidate packaging／Dual Review／archive safety | S05 |
| Human Gate／adoption／publication／readiness | S06 |
| Provider/install/update parity | S07 |
| Integrated regression／PA-NF | S08 |
| Human-selected real-use validation／metrics | S09 |
| Docs/Skill reference alignment | S90 |
| Final test sufficiency／integrated diff／spec conformance | S99 |
| PR delivery／Human merge | Final Exit, external shared workflow |

## 8. Spec-Locked Closure Index

この索引はmaterial obligationsのbounded coverage ledgerであり、全test itemやglobal proof registryではない。

| Closure ID | Spec link | Closure owner | Locked expectation | Evidence destination |
|---|---|---|---|---|
| `CLOS-CLI` | REQ-002 | S01 | independent CLI command family contract | `report.md#Step-Contract-Closure` |
| `CLOS-CREATE` | REQ-003–REQ-005, REQ-019 | S05 | exact three-document Planner response is packaged into an immutable Issue Candidate and handed directly to archive Review | `report.md#Step-Contract-Closure` |
| `CLOS-GIT` | REQ-003 | S03 | fail-closed Git preflight | `report.md#Step-Contract-Closure` |
| `CLOS-SEC` | REQ-021 | S03 | direct argv and redaction | `report.md#Step-Contract-Closure` |
| `CLOS-REVISION` | REQ-007 | S04 | dual revision lanes | `report.md#Step-Contract-Closure` |
| `CLOS-REVIEW` | REQ-006, REQ-008 | S05 | dual transport read-only Review | `report.md#Step-Contract-Closure` |
| `CLOS-ARCHIVE` | REQ-010, REQ-022 | S05 | safe Candidate archive | `report.md#Step-Contract-Closure` |
| `CLOS-ADOPTION` | REQ-009–REQ-012 | S06 | Human-gated adoption/parity/publication | `report.md#Step-Contract-Closure` |
| `CLOS-READINESS` | REQ-013, REQ-014 | S06 | derived readiness and PA-NF | `report.md#Step-Contract-Closure` |
| `CLOS-SKILL` | REQ-001, REQ-005 | S02 | official Skill and closed Prompts | `report.md#Step-Contract-Closure` |
| `CLOS-PROJECTION` | REQ-017, REQ-023 | S07 | wheel/sdist/init/update parity | `report.md#Step-Contract-Closure` |
| `CLOS-INTEGRATION` | REQ-019 | S08 | E1-I1 integrated compatibility | `report.md#Step-Contract-Closure` |
| `CLOS-DOGFOOD` | REQ-018, REQ-024 | S09 | Human-selected real-use chain | `report.md#Step-Contract-Closure` |
| `CLOS-DOCS` | REQ-020 | S90 | docs/Skill/reference consistency | `report.md#Step-Contract-Closure` |
| `CLOS-QUALITY` | all | S99 | final QA/code/spec evidence | `report.md#Step-Contract-Closure` |

## 9. Implementation Steps

### S01 Independent CLI walking skeleton

#### behavior goal

`spec-dock-chatgpt`が独立entrypointとして三command familyを公開し、exact Issue targetを解決する。

#### depends on / unblocks

- depends on: future exact Candidate Review／Human adoption and implementation-start authorization
- unblocks: S02

#### exact target files

- `src/spec_dock/assets/spec_dock/scripts/spec-dock-chatgpt`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/chatgpt_app.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/chatgpt_parser.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/planning.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/issue_planning.py`
- `tests/cli_runtime/test_chatgpt_planning.py`
- `tests/unit/domain/test_issue_planning_contracts.py`
- `tests/unit/presentation/test_issue_planning.py`

#### behavior slice execution

1. Mainがbaseline、clean tree、current source identityを確認する。
2. MainがImplementation Delegation Gateを記録し、bounded workerへexact target subsetを渡す。
3. Workerがpre-implementation evidenceを取得し、one-test／minimal implementation単位で変更する。
4. Workerがtargeted verificationとdiff summaryを返す。
5. Mainがdiff、tests、scopeを検証し、`report.md`へevidenceを統合する。
6. fresh code-reviewerがstep diffを確認し、必要なfixはbounded follow-upとして再委任する。
7. Step Result Approval後にcommit候補とclean checkを閉じる。

#### planned contract

- scope: 上記exact target filesだけ。
- test obligation: public observable behavior、negative／failure path、source contract、regressionをrisk-calibratedに検証する。
- red or alternative evidence requirement: red-required: current source has no `spec-dock-chatgpt` entrypoint or public command family.
- green verification: `uv run pytest tests/cli_runtime/test_chatgpt_planning.py tests/unit/domain/test_issue_planning_contracts.py tests/unit/presentation/test_issue_planning.py -q`
- refactor guardrail: Green後のbounded tidyだけ。新しいpublic contract、shared policy、unrelated cleanupを追加しない。
- amendment trigger: target追加、parent boundary変更、new persistent state、existing public behavior破壊、Human Gate semantics変更が必要なら停止し、plan amendment／fresh reviewへ戻る。

#### delegation contract

- delegated role: `dev-coder`
- input docs: `requirement.md`、`design.md`、`plan.md`、current workflow／authoring docs、exact target source。
- allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec-dock-chatgpt`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/chatgpt_app.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/chatgpt_parser.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/planning.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/issue_planning.py`
  - `tests/cli_runtime/test_chatgpt_planning.py`
  - `tests/unit/domain/test_issue_planning_contracts.py`
  - `tests/unit/presentation/test_issue_planning.py`
- forbidden changes:
  - canonical `report.md` worker write（Main only）
  - `.assurance.json`
  - current Portfolio／sibling or downstream Issue canonical docs
  - root generated `spec-dock/` projection direct edit
  - shared delivery／merge／finish／lifecycle policy surfaces
  - any path not explicitly listed in this step
- acceptance criteria: `AC-002`
- required tests or docs-only verification: `uv run pytest tests/cli_runtime/test_chatgpt_planning.py tests/unit/domain/test_issue_planning_contracts.py tests/unit/presentation/test_issue_planning.py -q`
- reviewer focus: `code-reviewer` verifies scope、observable behavior、compatibility、security、no unauthorized authority claim。
- stop conditions: source drift、input contradiction、allowlist外変更、required tool unavailable、unknown Red、acceptance未達、unresolved material decision。
- output required: changed files、worker summary、verification results、unresolved risks、`Ledger Note`または`No material implementation decisions beyond the approved plan.`

#### 具体テストケース一覧

- `tc-s01-001` acceptance: 独立CLIが三command familyを公開する
  - 前提: provider treeにnew entrypointがなく、temp managed repoを使う。
  - 操作: entrypointの`--help`と各subcommand helpを直接実行する。
  - 期待結果: planning create／planning revise／review planningが表示され、Core lifecycle commandは混入しない。
  - 失敗検出: entrypoint混線またはcommand欠落を検出する。
  - 検証方法: `tests/cli_runtime/test_chatgpt_planning.py`
  - 関連 closure id: `CLOS-CLI`

- `tc-s01-002` negative: unknown targetをfail closedにする
  - 前提: Issue registryに存在しないIDを指定する。
  - 操作: planning createを実行する。
  - 期待結果: backend起動前にstable nonzeroとなり、filesystem mutationは0。
  - 失敗検出: target誤解決とbackendへの不正context送信を防ぐ。
  - 検証方法: `tests/unit/domain/test_issue_planning_contracts.py`
  - 関連 closure id: `CLOS-CLI`

#### report evidence destination

Mainだけが`report.md`の`Implementation Delegation Gate`、`Step Contract Closure`、`Test Contract Closure`、`Closure Coverage`、`Spec Interpretation / Decision Ledger`へevidenceを統合する。Workerはstructured evidenceを返し、canonical reportを変更しない。

#### step closure contract

`CLOS-CLI`は、targeted Green、required reviewer passed、commit候補または正当なapproved-no-op、post-commit clean checkが揃った場合だけcloseする。

#### step gate

`uv run pytest tests/cli_runtime/test_chatgpt_planning.py tests/unit/domain/test_issue_planning_contracts.py tests/unit/presentation/test_issue_planning.py -q`を成功させ、scope外diff 0、fresh `code-reviewer` passed、Main Step Result Approvalを確認する。失敗、skip、unavailable、denied、provisionalをpassとして扱わない。

### S02 Official Skill and closed Prompt resources

#### behavior goal

official Skillがnew CLIをHuman entrypointとして使い、closed provider Prompt inventoryとHuman Gateを正しく案内する。

#### depends on / unblocks

- depends on: S01
- unblocks: S03

#### exact target files

- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
- `src/spec_dock/assets/spec_dock/system/prompts/issue-planning/create.md`
- `src/spec_dock/assets/spec_dock/system/prompts/issue-planning/revise.md`
- `src/spec_dock/assets/spec_dock/system/prompts/issue-planning/review.md`

#### behavior slice execution

1. Mainがbaseline、clean tree、current source identityを確認する。
2. MainがImplementation Delegation Gateを記録し、bounded workerへexact target subsetを渡す。
3. Workerがpre-implementation evidenceを取得し、one-test／minimal implementation単位で変更する。
4. Workerがtargeted verificationとdiff summaryを返す。
5. Mainがdiff、tests、scopeを検証し、`report.md`へevidenceを統合する。
6. fresh spec-reviewerがstep diffを確認し、必要なfixはbounded follow-upとして再委任する。
7. Step Result Approval後にcommit候補とclean checkを閉じる。

#### planned contract

- scope: 上記exact target filesだけ。
- test obligation: public observable behavior、negative／failure path、source contract、regressionをrisk-calibratedに検証する。
- red or alternative evidence requirement: inspect-only: current Skill routes through the legacy evidence/rewrite lane and must be replaced by the approved integrated bundle route.
- green verification: `uv run pytest tests/cli_runtime/test_chatgpt_planning.py -q && git diff --check`
- refactor guardrail: Green後のbounded tidyだけ。新しいpublic contract、shared policy、unrelated cleanupを追加しない。
- amendment trigger: target追加、parent boundary変更、new persistent state、existing public behavior破壊、Human Gate semantics変更が必要なら停止し、plan amendment／fresh reviewへ戻る。

#### delegation contract

- delegated role: `doc-writer`
- input docs: `requirement.md`、`design.md`、`plan.md`、current workflow／authoring docs、exact target source。
- allowed paths:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
  - `src/spec_dock/assets/spec_dock/system/prompts/issue-planning/create.md`
  - `src/spec_dock/assets/spec_dock/system/prompts/issue-planning/revise.md`
  - `src/spec_dock/assets/spec_dock/system/prompts/issue-planning/review.md`
- forbidden changes:
  - canonical `report.md` worker write（Main only）
  - `.assurance.json`
  - current Portfolio／sibling or downstream Issue canonical docs
  - root generated `spec-dock/` projection direct edit
  - shared delivery／merge／finish／lifecycle policy surfaces
  - any path not explicitly listed in this step
- acceptance criteria: `AC-001`, `AC-011`
- required tests or docs-only verification: `uv run pytest tests/cli_runtime/test_chatgpt_planning.py -q && git diff --check`
- reviewer focus: `spec-reviewer` verifies scope、observable behavior、compatibility、security、no unauthorized authority claim。
- stop conditions: source drift、input contradiction、allowlist外変更、required tool unavailable、unknown Red、acceptance未達、unresolved material decision。
- output required: changed files、worker summary、verification results、unresolved risks、`Ledger Note`または`No material implementation decisions beyond the approved plan.`

#### 具体テストケース一覧

- `tc-s02-001` docs: Skillからnew CLIへ到達する
  - 前提: provider Skillとthree Prompt resourcesをinspectする。
  - 操作: Skillのoperating spineとcommandsを解析する。
  - 期待結果: official entrypoint、three command family、dual mode/lane、Human Gateが一致する。
  - 失敗検出: 旧evidence laneやmanual fallbackの通常経路復活を防ぐ。
  - 検証方法: `tests/cli_runtime/test_chatgpt_planning.py`
  - 関連 closure id: `CLOS-SKILL`

- `tc-s02-002` security: Prompt inventoryをclosedにする
  - 前提: undeclared Prompt fileまたはraw overrideを指定するfixtureを用意する。
  - 操作: planning commandを実行する。
  - 期待結果: backend起動前に拒否し、allowed provider Promptだけが使用される。
  - 失敗検出: prompt injection surfaceの拡張を防ぐ。
  - 検証方法: `tests/cli_runtime/test_chatgpt_planning.py`
  - 関連 closure id: `CLOS-SKILL`

#### report evidence destination

Mainだけが`report.md`の`Implementation Delegation Gate`、`Step Contract Closure`、`Test Contract Closure`、`Closure Coverage`、`Spec Interpretation / Decision Ledger`へevidenceを統合する。Workerはstructured evidenceを返し、canonical reportを変更しない。

#### step closure contract

`CLOS-SKILL`は、targeted Green、required reviewer passed、commit候補または正当なapproved-no-op、post-commit clean checkが揃った場合だけcloseする。

#### step gate

`uv run pytest tests/cli_runtime/test_chatgpt_planning.py -q && git diff --check`を成功させ、scope外diff 0、fresh `spec-reviewer` passed、Main Step Result Approvalを確認する。失敗、skip、unavailable、denied、provisionalをpassとして扱わない。

### S03 Git-bound Planner response flow

#### behavior goal

exact Git preflight、pre-produced closed Prompt、direct-argv backendを通してcomplete三文書Planner responseを取得・検証する。final immutable Candidate ZIPの構築とidentity確定はS05だけが所有する。

#### depends on / unblocks

- depends on: S02
- unblocks: S04

#### exact target files

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_io.py`
- `tests/unit/application/test_issue_planning.py`
- `tests/integration/test_chatgpt_planning_fake_oracle.py`

#### behavior slice execution

1. Mainがbaseline、clean tree、current source identityを確認する。
2. MainがImplementation Delegation Gateを記録し、bounded workerへexact target subsetを渡す。
3. Workerがpre-implementation evidenceを取得し、one-test／minimal implementation単位で変更する。
4. Workerがtargeted verificationとdiff summaryを返す。
5. Mainがdiff、tests、scopeを検証し、`report.md`へevidenceを統合する。
6. fresh code-reviewerがstep diffを確認し、必要なfixはbounded follow-upとして再委任する。
7. Step Result Approval後にcommit候補とclean checkを閉じる。

#### planned contract

- scope: 上記exact target filesだけ。
- test obligation: exact Git preflight、backend non-invocation on source mismatch、complete three-document response validation、direct argv、redaction、no repository mutation。
- red or alternative evidence requirement: red-required: fake backend create first fails before Git/source/response validation exists。
- green verification: `uv run pytest tests/unit/application/test_issue_planning.py tests/integration/test_chatgpt_planning_fake_oracle.py tests/unit/authoring_pack/test_github_fetch_policy.py -q`
- refactor guardrail: Green後のbounded tidyだけ。Candidate packaging、archive identity、new persistent state、shared policy、unrelated cleanupをこのstepへ追加しない。
- amendment trigger: target追加、parent boundary変更、new persistent state、existing public behavior破壊、Human Gate semantics変更が必要なら停止し、plan amendment／fresh reviewへ戻る。

#### delegation contract

- delegated role: `dev-coder`
- input docs: `requirement.md`、`design.md`、`plan.md`、current workflow／authoring docs、exact target source。
- allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_io.py`
  - `tests/unit/application/test_issue_planning.py`
  - `tests/integration/test_chatgpt_planning_fake_oracle.py`
- forbidden changes:
  - Candidate ZIP packaging or identity finalization owned by S05
  - canonical `report.md` worker write（Main only）
  - `.assurance.json`
  - current Portfolio／sibling or downstream Issue canonical docs
  - root generated `spec-dock/` projection direct edit
  - shared delivery／merge／finish／lifecycle policy surfaces
  - any path not explicitly listed in this step
- acceptance criteria: `AC-003`, `AC-011`
- required tests or docs-only verification: `uv run pytest tests/unit/application/test_issue_planning.py tests/integration/test_chatgpt_planning_fake_oracle.py tests/unit/authoring_pack/test_github_fetch_policy.py -q`
- reviewer focus: `code-reviewer` verifies source fail-closed behavior、exact three-document response、direct argv、redaction、no hidden mutation、no premature packaging authority。
- stop conditions: source drift、input contradiction、allowlist外変更、required tool unavailable、unknown Red、acceptance未達、unresolved material decision。
- output required: changed files、worker summary、verification results、unresolved risks、`Ledger Note`または`No material implementation decisions beyond the approved plan.`

#### 具体テストケース一覧

- `tc-s03-001` acceptance: fake backendからcomplete three-document responseを取得する
  - 前提: clean named branch、upstream、local=remote、fake backend responseにexact `requirement.md`／`design.md`／`plan.md`がある。
  - 操作: planning createのbackend-response phaseを実行する。
  - 期待結果: safe external work areaへ三文書responseがbyte-preservingに取得され、repositoryとfinal Candidate targetは不変。
  - 失敗検出: partial response、unexpected file、hidden repository write、S05前のfinal identity確定を検出する。
  - 検証方法: `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - 関連 closure id: `CLOS-GIT`, `CLOS-SEC`

- `tc-s03-002` negative: source mismatchでbackendを起動しない
  - 前提: expected HEADとremote-visible HEADを不一致にする。
  - 操作: planning createを実行する。
  - 期待結果: stale/blockedとなりfake backend call countは0。
  - 失敗検出: stale sourceでのPlanningを防ぐ。
  - 検証方法: `tests/unit/application/test_issue_planning.py`
  - 関連 closure id: `CLOS-GIT`, `CLOS-SEC`

- `tc-s03-003` security: Prompt/pathをdirect argvで扱う
  - 前提: shell metacharacterを含むoperator contextとpathを用意する。
  - 操作: dry-run backend invocationを行う。
  - 期待結果: argv要素として保持され、shell executionとsecret-like outputがない。
  - 失敗検出: command injectionとdiagnostic leakageを防ぐ。
  - 検証方法: `tests/unit/authoring_pack/test_github_fetch_policy.py`
  - 関連 closure id: `CLOS-GIT`, `CLOS-SEC`

#### report evidence destination

Mainだけが`report.md`の`Implementation Delegation Gate`、`Step Contract Closure`、`Test Contract Closure`、`Closure Coverage`、`Spec Interpretation / Decision Ledger`へevidenceを統合する。Workerはstructured evidenceを返し、canonical reportを変更しない。

#### step closure contract

`CLOS-GIT`, `CLOS-SEC`は、targeted Green、required reviewer passed、commit候補または正当なapproved-no-op、post-commit clean checkが揃った場合だけcloseする。`CLOS-CREATE`はS05までopenのままにする。

#### step gate

`uv run pytest tests/unit/application/test_issue_planning.py tests/integration/test_chatgpt_planning_fake_oracle.py tests/unit/authoring_pack/test_github_fetch_policy.py -q`を成功させ、scope外diff 0、fresh `code-reviewer` passed、Main Step Result Approvalを確認する。失敗、skip、unavailable、denied、provisionalをpassとして扱わない。

### S04 Semantic and mechanical revision

#### behavior goal

Skill-selected laneを維持し、Semantic complete replacementとbounded Mechanical revisionを決定的に生成する。

#### depends on / unblocks

- depends on: S03
- unblocks: S05

#### exact target files

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`
- `tests/unit/application/test_issue_planning.py`
- `tests/integration/test_chatgpt_planning_fake_oracle.py`

#### behavior slice execution

1. Mainがbaseline、clean tree、current source identityを確認する。
2. MainがImplementation Delegation Gateを記録し、bounded workerへexact target subsetを渡す。
3. Workerがpre-implementation evidenceを取得し、one-test／minimal implementation単位で変更する。
4. Workerがtargeted verificationとdiff summaryを返す。
5. Mainがdiff、tests、scopeを検証し、`report.md`へevidenceを統合する。
6. fresh code-reviewerがstep diffを確認し、必要なfixはbounded follow-upとして再委任する。
7. Step Result Approval後にcommit候補とclean checkを閉じる。

#### planned contract

- scope: 上記exact target filesだけ。
- test obligation: public observable behavior、negative／failure path、source contract、regressionをrisk-calibratedに検証する。
- red or alternative evidence requirement: red-required: current authoring primitives do not expose the approved revision-lane contract.
- green verification: `uv run pytest tests/unit/application/test_issue_planning.py tests/integration/test_chatgpt_planning_fake_oracle.py -q`
- refactor guardrail: Green後のbounded tidyだけ。新しいpublic contract、shared policy、unrelated cleanupを追加しない。
- amendment trigger: target追加、parent boundary変更、new persistent state、existing public behavior破壊、Human Gate semantics変更が必要なら停止し、plan amendment／fresh reviewへ戻る。

#### delegation contract

- delegated role: `dev-coder`
- input docs: `requirement.md`、`design.md`、`plan.md`、current workflow／authoring docs、exact target source。
- allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`
  - `tests/unit/application/test_issue_planning.py`
  - `tests/integration/test_chatgpt_planning_fake_oracle.py`
- forbidden changes:
  - canonical `report.md` worker write（Main only）
  - `.assurance.json`
  - current Portfolio／sibling or downstream Issue canonical docs
  - root generated `spec-dock/` projection direct edit
  - shared delivery／merge／finish／lifecycle policy surfaces
  - any path not explicitly listed in this step
- acceptance criteria: `AC-004`
- required tests or docs-only verification: `uv run pytest tests/unit/application/test_issue_planning.py tests/integration/test_chatgpt_planning_fake_oracle.py -q`
- reviewer focus: `code-reviewer` verifies scope、observable behavior、compatibility、security、no unauthorized authority claim。
- stop conditions: source drift、input contradiction、allowlist外変更、required tool unavailable、unknown Red、acceptance未達、unresolved material decision。
- output required: changed files、worker summary、verification results、unresolved risks、`Ledger Note`または`No material implementation decisions beyond the approved plan.`

#### 具体テストケース一覧

- `tc-s04-001` acceptance: Semantic revisionはcomplete replacementを返す
  - 前提: valid prior Candidateとsemantic lane、fake backend complete responseを用意する。
  - 操作: planning reviseを実行する。
  - 期待結果: complete三文書replacement responseを返し、旧Candidateは不変。new Candidate identityとfinal ZIPはS05の共通packaging pathだけが確定する。
  - 失敗検出: 部分patchや旧version上書きを防ぐ。
  - 検証方法: `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - 関連 closure id: `CLOS-REVISION`

- `tc-s04-002` negative: Mechanical revisionのscope拡張を拒否する
  - 前提: allowed path/field外を変更するfake resultを用意する。
  - 操作: mechanical laneでreviseを実行する。
  - 期待結果: 非成功となりfinal Candidate outputは生成されない。
  - 失敗検出: bounded correctionをsemantic changeへ悪用する回帰を防ぐ。
  - 検証方法: `tests/unit/application/test_issue_planning.py`
  - 関連 closure id: `CLOS-REVISION`

#### report evidence destination

Mainだけが`report.md`の`Implementation Delegation Gate`、`Step Contract Closure`、`Test Contract Closure`、`Closure Coverage`、`Spec Interpretation / Decision Ledger`へevidenceを統合する。Workerはstructured evidenceを返し、canonical reportを変更しない。

#### step closure contract

`CLOS-REVISION`は、targeted Green、required reviewer passed、commit候補または正当なapproved-no-op、post-commit clean checkが揃った場合だけcloseする。

#### step gate

`uv run pytest tests/unit/application/test_issue_planning.py tests/integration/test_chatgpt_planning_fake_oracle.py -q`を成功させ、scope外diff 0、fresh `code-reviewer` passed、Main Step Result Approvalを確認する。失敗、skip、unavailable、denied、provisionalをpassとして扱わない。

### S05 Runtime Issue Candidate packaging, read-only Planning Review, and archive integrity

#### behavior goal

S03／S04のcomplete three-document responseからmandatory controlsを含むimmutable Issue Candidate ZIPを一意に構築し、そのfinal ZIPまたはexact git-bound identityをread-only Planning Reviewへ渡す。S05だけがlogical filename、version、Candidate ID、internal root、source binding、external ZIP SHAをfinalizeする。

#### depends on / unblocks

- depends on: S04
- unblocks: S06

#### exact target files

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/zip_contract.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_io.py`
- `tests/cli_runtime/test_authoring.py`
- `tests/manual_tests/test_review_chatgpt_authoring_pack.py`
- `tests/unit/infra/test_issue_planning_archive.py`
- `tests/integration/test_chatgpt_planning_fake_oracle.py`

#### behavior slice execution

1. Mainがbaseline、clean tree、current source identityを確認する。
2. MainがImplementation Delegation Gateを記録し、bounded workerへexact target subsetを渡す。
3. Workerがexisting generic authoring-pack defaultのcharacterizationを先に実行する。
4. Workerがshared `zip_contract.py`へdata-only named contractをbounded追加し、one-test／minimal implementationでIssue Candidate packagingとReviewを通す。
5. Workerがtargeted verificationとdiff summaryを返す。
6. Mainがdiff、tests、scope、generic default compatibilityを検証し、`report.md`へevidenceを統合する。
7. fresh code-reviewerがstep diffを確認し、必要なfixはbounded follow-upとして再委任する。
8. Step Result Approval後にcommit候補とclean checkを閉じる。

#### planned contract

- scope: 上記exact target filesだけ。
- packaging owner: S05のみ。ChatGPT responseはexact三文書、Runtime final artifactは三文書＋`SOURCE-BASELINE.json`＋`MANIFEST.json`＋`CHECKSUMS.sha256`＋`PLACEHOLDER-ORACLE-MAP.json`のimmutable ZIP。
- identity rule: initial createはversion 1、revisionはpredecessor version + 1。complete response検証後にrun-scoped UTC timestampを一度取得し、logical filename／Candidate ID／internal rootをpure derivationする。source bindingはS03 preflight resultを使用し、external SHAはarchive close後に計算する。
- publication rule: owned temporary fileからsafe external output directoryのnew final filenameへatomic publishし、existing final targetを上書きしない。failure時はtemporary fileをcleanupし、final ZIP、final extraction tree、Review resultを残さない。
- shared primitive rule: `zip_contract.py`にclosed data-only `ArchiveReviewContract`を追加し、引数省略時のexisting authoring-pack root／required metadata／limits／status taxonomyを完全に保持する。Issue Candidate contractはexpected root、mandatory paths、current ceilings、closed identity modeだけを追加する。registry、callback/plugin、parallel validator、allocator、general archive framework、all-resource matrixは作らない。
- test obligation: create→final ZIP→archive Review direct handoff、generic default regression、Issue Candidate positive identity/inventory、unsafe/missing-control negative、git-bound exact target、read-only mutation guard。
- red or alternative evidence requirement: red-required for direct create→archive Review and Issue-specific root/control validation; covered-existing for generic authoring-pack default characterization。
- green verification: `uv run pytest tests/cli_runtime/test_authoring.py tests/manual_tests/test_review_chatgpt_authoring_pack.py tests/unit/infra/test_issue_planning_archive.py tests/integration/test_chatgpt_planning_fake_oracle.py -q`
- refactor guardrail: Green後のbounded tidyだけ。generic defaultの意味変更、new public framework、shared policy、unrelated cleanupを追加しない。
- amendment trigger: existing generic behaviorを保てない、target追加、parent boundary変更、new persistent state、Human Gate semantics変更が必要なら停止し、plan amendment／fresh reviewへ戻る。

#### delegation contract

- delegated role: `dev-coder`
- input docs: `requirement.md`、`design.md`、`plan.md`、current workflow／authoring docs、exact `zip_contract.py`、generic compatibility tests、S03／S04 response contracts。
- allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/zip_contract.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_io.py`
  - `tests/cli_runtime/test_authoring.py`
  - `tests/manual_tests/test_review_chatgpt_authoring_pack.py`
  - `tests/unit/infra/test_issue_planning_archive.py`
  - `tests/integration/test_chatgpt_planning_fake_oracle.py`
- forbidden changes:
  - existing generic authoring-pack default root、metadata、limits、status taxonomy
  - parallel archive validator、allocator、plugin/callback registry、general archive framework
  - canonical `report.md` worker write（Main only）
  - `.assurance.json`
  - current Portfolio／sibling or downstream Issue canonical docs
  - root generated `spec-dock/` projection direct edit
  - shared delivery／merge／finish／lifecycle policy surfaces
  - any path not explicitly listed in this step
- acceptance criteria: `AC-001`, `AC-004`, `AC-005`, `AC-006`, `AC-007`, `AC-017`
- required tests or docs-only verification: `uv run pytest tests/cli_runtime/test_authoring.py tests/manual_tests/test_review_chatgpt_authoring_pack.py tests/unit/infra/test_issue_planning_archive.py tests/integration/test_chatgpt_planning_fake_oracle.py -q`
- reviewer focus: `code-reviewer` verifies sole packaging ownership、direct create→Review handoff、generic default compatibility、scope、identity/inventory/checksum correctness、read-only Review、no duplicated subsystem。
- stop conditions: generic default regression、source drift、input contradiction、allowlist外変更、required tool unavailable、unknown Red、acceptance未達、unresolved material decision。
- output required: changed files、worker summary、verification results、generic compatibility result、unresolved risks、`Ledger Note`または`No material implementation decisions beyond the approved plan.`

#### 具体テストケース一覧

- `tc-s05-001` acceptance: planning create final ZIPをそのままarchive Reviewへ渡す
  - 前提: fake Plannerがexact三文書を返し、safe external output directoryとsource preflightがある。
  - 操作: `planning create`を実行し、そのresultのZIP pathを変更・再packagingせず`review planning --mode archive-candidate`へ渡す。
  - 期待結果: final ZIPはmandatory seven files、single root、new identity、source binding、external SHAを持ち、Review resultはそのexact identityへbindする。repositoryとCandidate bytesはReview前後で不変。
  - 失敗検出: raw three-file tree、manual repack、missing controls、identity取り違え、hidden repository writeを防ぐ。
  - 検証方法: `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - 関連 closure id: `CLOS-CREATE`, `CLOS-REVIEW`, `CLOS-ARCHIVE`

- `tc-s05-002` regression: existing generic authoring-pack defaultを変えない
  - 前提: current `specdock-authoring-pack/` root、required metadata、status taxonomyのpositive/negative fixturesがある。
  - 操作: contract引数なしのexisting `authoring pack review`とmanual compatibility suiteを実行する。
  - 期待結果: current generic valid packは従来どおりpassし、wrong root／metadata missing／source mismatch／unsafe entryは従来のstatusとfindingを維持する。
  - 失敗検出: Issue Candidate追加がgeneric root、metadata、limits、statusを破壊する回帰を防ぐ。
  - 検証方法: `tests/cli_runtime/test_authoring.py`, `tests/manual_tests/test_review_chatgpt_authoring_pack.py`
  - 関連 closure id: `CLOS-ARCHIVE`, `CLOS-INTEGRATION`

- `tc-s05-003` acceptance: Issue Candidate named contractがidentityとinventoryを検証する
  - 前提: expected root、version、logical filename、Candidate ID、source binding、三文書と四control filesを持つsafe Candidateを用意する。
  - 操作: Issue Candidate contractでarchive validationを実行する。
  - 期待結果: MANIFEST inventory、CHECKSUMS、source baseline、placeholder map、Candidate identityが一致し、external SHAがresultへ返る。
  - 失敗検出: mandatory control omission、cross-Candidate substitution、stale source、checksum mismatchを防ぐ。
  - 検証方法: `tests/unit/infra/test_issue_planning_archive.py`
  - 関連 closure id: `CLOS-CREATE`, `CLOS-ARCHIVE`

- `tc-s05-004` negative: unsafeまたはincomplete Issue Candidateをpartial outputなしで拒否する
  - 前提: wrong root、missing mandatory control、traversal、symlink、duplicate、CRC、oversizeの代表fixturesを用意する。
  - 操作: archive packagingまたはReviewを各fixtureで実行する。
  - 期待結果: stable non-successとなりfinal ZIP、final extraction tree、Review resultは存在しない。
  - 失敗検出: ZIP slip、resource exhaustion、incomplete Candidate publication、partial evidenceを防ぐ。
  - 検証方法: `tests/unit/infra/test_issue_planning_archive.py`
  - 関連 closure id: `CLOS-CREATE`, `CLOS-REVIEW`, `CLOS-ARCHIVE`

- `tc-s05-005` negative: git-bound modeはexact target setを要求する
  - 前提: reviewed HEADまたはtarget pathsを欠落／不一致にする。
  - 操作: review planning --mode git-boundを実行する。
  - 期待結果: backend起動前にinsufficient evidenceとなりarchiveへ切り替わらない。
  - 失敗検出: mode混同とsilent fallbackを防ぐ。
  - 検証方法: `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - 関連 closure id: `CLOS-REVIEW`, `CLOS-ARCHIVE`

#### report evidence destination

Mainだけが`report.md`の`Implementation Delegation Gate`、`Step Contract Closure`、`Test Contract Closure`、`Closure Coverage`、`Spec Interpretation / Decision Ledger`へevidenceを統合する。Workerはstructured evidenceを返し、canonical reportを変更しない。

#### step closure contract

`CLOS-CREATE`, `CLOS-REVIEW`, `CLOS-ARCHIVE`は、direct create→Review Green、generic default regression、Issue positive/negative archive tests、required reviewer passed、commit候補または正当なapproved-no-op、post-commit clean checkが揃った場合だけcloseする。

#### step gate

`uv run pytest tests/cli_runtime/test_authoring.py tests/manual_tests/test_review_chatgpt_authoring_pack.py tests/unit/infra/test_issue_planning_archive.py tests/integration/test_chatgpt_planning_fake_oracle.py -q`を成功させ、scope外diff 0、existing generic default unchanged、fresh `code-reviewer` passed、Main Step Result Approvalを確認する。失敗、skip、unavailable、denied、provisionalをpassとして扱わない。

### S06 Human gate, adoption, publication, and derived readiness

#### behavior goal

exact reviewed identityへbindしたHuman decisionとmode-specific parity、validation、publicationの論理積だけからreadinessを導出する。

#### depends on / unblocks

- depends on: S05
- unblocks: S07

#### exact target files

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_io.py`
- `tests/unit/application/test_issue_planning.py`
- `tests/unit/domain/test_issue_planning_contracts.py`
- `tests/integration/test_chatgpt_planning_fake_oracle.py`

#### behavior slice execution

1. Mainがbaseline、clean tree、current source identityを確認する。
2. MainがImplementation Delegation Gateを記録し、bounded workerへexact target subsetを渡す。
3. Workerがpre-implementation evidenceを取得し、one-test／minimal implementation単位で変更する。
4. Workerがtargeted verificationとdiff summaryを返す。
5. Mainがdiff、tests、scopeを検証し、`report.md`へevidenceを統合する。
6. fresh code-reviewerがstep diffを確認し、必要なfixはbounded follow-upとして再委任する。
7. Step Result Approval後にcommit候補とclean checkを閉じる。

#### planned contract

- scope: 上記exact target filesだけ。
- test obligation: public observable behavior、negative／failure path、source contract、regressionをrisk-calibratedに検証する。
- red or alternative evidence requirement: red-required: current approval check is evidence-only and does not implement the complete E1-I1 readiness conjunction.
- green verification: `uv run pytest tests/unit/application/test_issue_planning.py tests/unit/domain/test_issue_planning_contracts.py tests/integration/test_chatgpt_planning_fake_oracle.py -q`
- refactor guardrail: Green後のbounded tidyだけ。新しいpublic contract、shared policy、unrelated cleanupを追加しない。
- amendment trigger: target追加、parent boundary変更、new persistent state、existing public behavior破壊、Human Gate semantics変更が必要なら停止し、plan amendment／fresh reviewへ戻る。

#### delegation contract

- delegated role: `dev-coder`
- input docs: `requirement.md`、`design.md`、`plan.md`、current workflow／authoring docs、exact target source。
- allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_io.py`
  - `tests/unit/application/test_issue_planning.py`
  - `tests/unit/domain/test_issue_planning_contracts.py`
  - `tests/integration/test_chatgpt_planning_fake_oracle.py`
- forbidden changes:
  - canonical `report.md` worker write（Main only）
  - `.assurance.json`
  - current Portfolio／sibling or downstream Issue canonical docs
  - root generated `spec-dock/` projection direct edit
  - shared delivery／merge／finish／lifecycle policy surfaces
  - any path not explicitly listed in this step
- acceptance criteria: `AC-008`, `AC-009`, `AC-010`, `AC-013`
- required tests or docs-only verification: `uv run pytest tests/unit/application/test_issue_planning.py tests/unit/domain/test_issue_planning_contracts.py tests/integration/test_chatgpt_planning_fake_oracle.py -q`
- reviewer focus: `code-reviewer` verifies scope、observable behavior、compatibility、security、no unauthorized authority claim。
- stop conditions: source drift、input contradiction、allowlist外変更、required tool unavailable、unknown Red、acceptance未達、unresolved material decision。
- output required: changed files、worker summary、verification results、unresolved risks、`Ledger Note`または`No material implementation decisions beyond the approved plan.`

#### 具体テストケース一覧

- `tc-s06-001` acceptance: archive full conjunctionだけがreadinessを導出する
  - 前提: exact review evidence、Human decision、atomic adoption parity、validation、remote-equal publicationを用意する。
  - 操作: readiness evaluationを実行する。
  - 期待結果: ready resultを返し、各evidence locatorを参照する。
  - 失敗検出: Review-onlyまたはHuman-only startを防ぐ。
  - 検証方法: `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - 関連 closure id: `CLOS-ADOPTION`, `CLOS-READINESS`

- `tc-s06-002` acceptance: git-bound target blobを維持する
  - 前提: reviewed HEAD/paths、Human decision、approval-only adoption diffを用意する。
  - 操作: git-bound adoptionとpublicationを実行する。
  - 期待結果: reviewed target blobsが不変でlocal/remote publication parityが成立する。
  - 失敗検出: Review後semantic mutationを防ぐ。
  - 検証方法: `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - 関連 closure id: `CLOS-ADOPTION`, `CLOS-READINESS`

- `tc-s06-003` negative: PA-NF setを独立拒否する
  - 前提: PA-NF-01〜PA-NF-10を一件ずつ満たすfixturesを用意する。
  - 操作: readiness evaluationを各fixtureで実行する。
  - 期待結果: 全件非ready、canonical partial output 0、violations 0。
  - 失敗検出: 複合gateの短絡を防ぐ。
  - 検証方法: `tests/unit/domain/test_issue_planning_contracts.py`
  - 関連 closure id: `CLOS-ADOPTION`, `CLOS-READINESS`

#### report evidence destination

Mainだけが`report.md`の`Implementation Delegation Gate`、`Step Contract Closure`、`Test Contract Closure`、`Closure Coverage`、`Spec Interpretation / Decision Ledger`へevidenceを統合する。Workerはstructured evidenceを返し、canonical reportを変更しない。

#### step closure contract

`CLOS-ADOPTION`, `CLOS-READINESS`は、targeted Green、required reviewer passed、commit候補または正当なapproved-no-op、post-commit clean checkが揃った場合だけcloseする。

#### step gate

`uv run pytest tests/unit/application/test_issue_planning.py tests/unit/domain/test_issue_planning_contracts.py tests/integration/test_chatgpt_planning_fake_oracle.py -q`を成功させ、scope外diff 0、fresh `code-reviewer` passed、Main Step Result Approvalを確認する。失敗、skip、unavailable、denied、provisionalをpassとして扱わない。

### S07 Installer and provider projection

#### behavior goal

wheel／sdist、fresh init、updateを通してnew CLI／Skill／Prompt／docsをregular executableなinstalled surfaceへ投影する。

#### depends on / unblocks

- depends on: S06
- unblocks: S08

#### exact target files

- `src/spec_dock/cli.py`
- `pyproject.toml`
- `tests/unit/infra/test_init_update.py`

#### behavior slice execution

1. Mainがbaseline、clean tree、current source identityを確認する。
2. MainがImplementation Delegation Gateを記録し、bounded workerへexact target subsetを渡す。
3. Workerがpre-implementation evidenceを取得し、one-test／minimal implementation単位で変更する。
4. Workerがtargeted verificationとdiff summaryを返す。
5. Mainがdiff、tests、scopeを検証し、`report.md`へevidenceを統合する。
6. fresh code-reviewerがstep diffを確認し、必要なfixはbounded follow-upとして再委任する。
7. Step Result Approval後にcommit候補とclean checkを閉じる。

#### planned contract

- scope: 上記exact target filesだけ。
- test obligation: public observable behavior、negative／failure path、source contract、regressionをrisk-calibratedに検証する。
- red or alternative evidence requirement: red-required: current installer only handles the existing repo-local runtime executable and lacks the new managed entrypoint contract.
- green verification: `uv build && uv run pytest tests/unit/infra/test_init_update.py -q`
- refactor guardrail: Green後のbounded tidyだけ。新しいpublic contract、shared policy、unrelated cleanupを追加しない。
- amendment trigger: target追加、parent boundary変更、new persistent state、existing public behavior破壊、Human Gate semantics変更が必要なら停止し、plan amendment／fresh reviewへ戻る。

#### delegation contract

- delegated role: `dev-coder`
- input docs: `requirement.md`、`design.md`、`plan.md`、current workflow／authoring docs、exact target source。
- allowed paths:
  - `src/spec_dock/cli.py`
  - `pyproject.toml`
  - `tests/unit/infra/test_init_update.py`
- forbidden changes:
  - canonical `report.md` worker write（Main only）
  - `.assurance.json`
  - current Portfolio／sibling or downstream Issue canonical docs
  - root generated `spec-dock/` projection direct edit
  - shared delivery／merge／finish／lifecycle policy surfaces
  - any path not explicitly listed in this step
- acceptance criteria: `AC-012`, `AC-015`
- required tests or docs-only verification: `uv build && uv run pytest tests/unit/infra/test_init_update.py -q`
- reviewer focus: `code-reviewer` verifies scope、observable behavior、compatibility、security、no unauthorized authority claim。
- stop conditions: source drift、input contradiction、allowlist外変更、required tool unavailable、unknown Red、acceptance未達、unresolved material decision。
- output required: changed files、worker summary、verification results、unresolved risks、`Ledger Note`または`No material implementation decisions beyond the approved plan.`

#### 具体テストケース一覧

- `tc-s07-001` compatibility: wheel／sdist fresh initでnew CLIを直接実行する
  - 前提: fresh temp reposとbuilt wheel/sdistを用意する。
  - 操作: 各artifactをinstallしspec-dock init後にboth repo-local entrypointsのmodeと--helpを確認する。
  - 期待結果: regular non-symlink、POSIX executable、direct invocation成功。
  - 失敗検出: bytesだけ存在して実行不能なinstallを防ぐ。
  - 検証方法: `tests/unit/infra/test_init_update.py`
  - 関連 closure id: `CLOS-PROJECTION`

- `tc-s07-002` compatibility: updateでmanaged inventoryを同期する
  - 前提: old managed repoへprovider changesを用意する。
  - 操作: spec-dock updateを実行する。
  - 期待結果: new CLI/Skill/Prompt/docsがprovider bytesと一致しuser specsを保持する。
  - 失敗検出: partial projectionとuser-authored spec損失を防ぐ。
  - 検証方法: `tests/unit/infra/test_init_update.py`
  - 関連 closure id: `CLOS-PROJECTION`

- `tc-s07-003` failure: representative mode failureを非成功にする
  - 前提: new entrypointのchmodまたはpostconditionを失敗させる。
  - 操作: init/updateを実行する。
  - 期待結果: nonzeroでsuccess表示なし、既存user specs保持。
  - 失敗検出: silent successful but unusable installを防ぐ。
  - 検証方法: `tests/unit/infra/test_init_update.py`
  - 関連 closure id: `CLOS-PROJECTION`

#### report evidence destination

Mainだけが`report.md`の`Implementation Delegation Gate`、`Step Contract Closure`、`Test Contract Closure`、`Closure Coverage`、`Spec Interpretation / Decision Ledger`へevidenceを統合する。Workerはstructured evidenceを返し、canonical reportを変更しない。

#### step closure contract

`CLOS-PROJECTION`は、targeted Green、required reviewer passed、commit候補または正当なapproved-no-op、post-commit clean checkが揃った場合だけcloseする。

#### step gate

`uv build && uv run pytest tests/unit/infra/test_init_update.py -q`を成功させ、scope外diff 0、fresh `code-reviewer` passed、Main Step Result Approvalを確認する。失敗、skip、unavailable、denied、provisionalをpassとして扱わない。

### S08 Integration, compatibility, and adoption negatives

#### behavior goal

fake remote end-to-end、PA-NF、legacy compatibility、provider／installed／dogfood parityを一つのintegration checkpointで検証する。

#### depends on / unblocks

- depends on: S07
- unblocks: S09

#### exact target files

- `tests/integration/test_chatgpt_planning_fake_oracle.py`
- `tests/cli_runtime/test_chatgpt_planning.py`
- `tests/unit/application/test_issue_planning.py`
- `tests/unit/domain/test_issue_planning_contracts.py`
- `tests/unit/infra/test_issue_planning_archive.py`
- `tests/unit/presentation/test_issue_planning.py`

#### behavior slice execution

1. Mainがbaseline、clean tree、current source identityを確認する。
2. MainがImplementation Delegation Gateを記録し、bounded workerへexact target subsetを渡す。
3. Workerがpre-implementation evidenceを取得し、one-test／minimal implementation単位で変更する。
4. Workerがtargeted verificationとdiff summaryを返す。
5. Mainがdiff、tests、scopeを検証し、`report.md`へevidenceを統合する。
6. fresh code-reviewerがstep diffを確認し、必要なfixはbounded follow-upとして再委任する。
7. Step Result Approval後にcommit候補とclean checkを閉じる。

#### planned contract

- scope: 上記exact target filesだけ。
- test obligation: public observable behavior、negative／failure path、source contract、regressionをrisk-calibratedに検証する。
- red or alternative evidence requirement: covered-existing plus red-required for the new E1-I1 chain; preserve existing authoring-pack tests while adding focused planning integration.
- green verification: `uv run pytest tests/cli_runtime/test_chatgpt_planning.py tests/unit/application/test_issue_planning.py tests/unit/domain/test_issue_planning_contracts.py tests/unit/infra/test_issue_planning_archive.py tests/unit/presentation/test_issue_planning.py tests/integration/test_chatgpt_planning_fake_oracle.py tests/unit/authoring_pack tests/manual_tests/test_invoke_chatgpt_backend.py tests/manual_tests/test_review_chatgpt_authoring_pack.py -q`
- refactor guardrail: Green後のbounded tidyだけ。新しいpublic contract、shared policy、unrelated cleanupを追加しない。
- amendment trigger: target追加、parent boundary変更、new persistent state、existing public behavior破壊、Human Gate semantics変更が必要なら停止し、plan amendment／fresh reviewへ戻る。

#### delegation contract

- delegated role: `dev-coder`
- input docs: `requirement.md`、`design.md`、`plan.md`、current workflow／authoring docs、exact target source。
- allowed paths:
  - `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - `tests/cli_runtime/test_chatgpt_planning.py`
  - `tests/unit/application/test_issue_planning.py`
  - `tests/unit/domain/test_issue_planning_contracts.py`
  - `tests/unit/infra/test_issue_planning_archive.py`
  - `tests/unit/presentation/test_issue_planning.py`
- forbidden changes:
  - canonical `report.md` worker write（Main only）
  - `.assurance.json`
  - current Portfolio／sibling or downstream Issue canonical docs
  - root generated `spec-dock/` projection direct edit
  - shared delivery／merge／finish／lifecycle policy surfaces
  - any path not explicitly listed in this step
- acceptance criteria: `AC-003`, `AC-004`, `AC-005`, `AC-006`, `AC-007`, `AC-008`, `AC-009`, `AC-010`, `AC-011`, `AC-015`
- required tests or docs-only verification: `uv run pytest tests/cli_runtime/test_chatgpt_planning.py tests/unit/application/test_issue_planning.py tests/unit/domain/test_issue_planning_contracts.py tests/unit/infra/test_issue_planning_archive.py tests/unit/presentation/test_issue_planning.py tests/integration/test_chatgpt_planning_fake_oracle.py tests/unit/authoring_pack tests/manual_tests/test_invoke_chatgpt_backend.py tests/manual_tests/test_review_chatgpt_authoring_pack.py -q`
- reviewer focus: `code-reviewer` verifies scope、observable behavior、compatibility、security、no unauthorized authority claim。
- stop conditions: source drift、input contradiction、allowlist外変更、required tool unavailable、unknown Red、acceptance未達、unresolved material decision。
- output required: changed files、worker summary、verification results、unresolved risks、`Ledger Note`または`No material implementation decisions beyond the approved plan.`

#### 具体テストケース一覧

- `tc-s08-001` integration: fake remoteでarchive／git positive chainを完走する
  - 前提: fake Git remote、fake Oracle、Human decision fixturesを用意する。
  - 操作: 両modeのfull chainを実行する。
  - 期待結果: 各modeで全conjunct後だけreadiness、remote publication parity成立。
  - 失敗検出: subsystem単体greenだがE2E不成立を検出する。
  - 検証方法: `tests/integration/test_chatgpt_planning_fake_oracle.py`
  - 関連 closure id: `CLOS-INTEGRATION`

- `tc-s08-002` regression: existing authoring-pack safetyを維持する
  - 前提: current focused suitesをbaselineとして用意する。
  - 操作: new planning suitesとexisting authoring-pack suitesを実行する。
  - 期待結果: existing public behaviorはgreenで、new routeだけadditive。
  - 失敗検出: walking skeletonが既存safe primitivesを壊す回帰を検出する。
  - 検証方法: `tests/unit/authoring_pack and tests/manual_tests`
  - 関連 closure id: `CLOS-INTEGRATION`

#### report evidence destination

Mainだけが`report.md`の`Implementation Delegation Gate`、`Step Contract Closure`、`Test Contract Closure`、`Closure Coverage`、`Spec Interpretation / Decision Ledger`へevidenceを統合する。Workerはstructured evidenceを返し、canonical reportを変更しない。

#### step closure contract

`CLOS-INTEGRATION`は、targeted Green、required reviewer passed、commit候補または正当なapproved-no-op、post-commit clean checkが揃った場合だけcloseする。

#### step gate

`uv run pytest tests/cli_runtime/test_chatgpt_planning.py tests/unit/application/test_issue_planning.py tests/unit/domain/test_issue_planning_contracts.py tests/unit/infra/test_issue_planning_archive.py tests/unit/presentation/test_issue_planning.py tests/integration/test_chatgpt_planning_fake_oracle.py tests/unit/authoring_pack tests/manual_tests/test_invoke_chatgpt_backend.py tests/manual_tests/test_review_chatgpt_authoring_pack.py -q`を成功させ、scope外diff 0、fresh `code-reviewer` passed、Main Step Result Approvalを確認する。失敗、skip、unavailable、denied、provisionalをpassとして扱わない。

### S09 Human-selected JIT dogfood

#### behavior goal

Human-selected eligible Issueでselected modeのfull positive chainを完走し、実運用Evidenceを取得する。

#### depends on / unblocks

- depends on: S08
- unblocks: S90

#### exact target files

- `tests/integration/test_chatgpt_planning_dogfood.py`

#### behavior slice execution

1. Mainがbaseline、clean tree、current source identityを確認する。
2. MainがImplementation Delegation Gateを記録し、bounded workerへexact target subsetを渡す。
3. Workerがpre-implementation evidenceを取得し、one-test／minimal implementation単位で変更する。
4. Workerがtargeted verificationとdiff summaryを返す。
5. Mainがdiff、tests、scopeを検証し、`report.md`へevidenceを統合する。
6. fresh code-reviewerがstep diffを確認し、必要なfixはbounded follow-upとして再委任する。
7. Step Result Approval後にcommit候補とclean checkを閉じる。

#### planned contract

- scope: 上記exact target filesだけ。
- test obligation: public observable behavior、negative／failure path、source contract、regressionをrisk-calibratedに検証する。
- red or alternative evidence requirement: manual-required: exact targetはfeature-complete直前にHumanが選択し、selection evidenceはCandidate外に記録する。
- green verification: `SPEC_DOCK_ORACLE_LIVE=1 uv run pytest tests/integration/test_chatgpt_planning_dogfood.py -q`
- refactor guardrail: Green後のbounded tidyだけ。新しいpublic contract、shared policy、unrelated cleanupを追加しない。
- amendment trigger: target追加、parent boundary変更、new persistent state、existing public behavior破壊、Human Gate semantics変更が必要なら停止し、plan amendment／fresh reviewへ戻る。

#### delegation contract

- delegated role: `dev-coder`
- input docs: `requirement.md`、`design.md`、`plan.md`、current workflow／authoring docs、exact target source。
- allowed paths:
  - `tests/integration/test_chatgpt_planning_dogfood.py`
- forbidden changes:
  - canonical `report.md` worker write（Main only）
  - `.assurance.json`
  - current Portfolio／sibling or downstream Issue canonical docs
  - root generated `spec-dock/` projection direct edit
  - shared delivery／merge／finish／lifecycle policy surfaces
  - any path not explicitly listed in this step
- acceptance criteria: `AC-014`
- required tests or docs-only verification: `SPEC_DOCK_ORACLE_LIVE=1 uv run pytest tests/integration/test_chatgpt_planning_dogfood.py -q`
- reviewer focus: `code-reviewer` verifies scope、observable behavior、compatibility、security、no unauthorized authority claim。
- stop conditions: source drift、input contradiction、allowlist外変更、required tool unavailable、unknown Red、acceptance未達、unresolved material decision。
- output required: changed files、worker summary、verification results、unresolved risks、`Ledger Note`または`No material implementation decisions beyond the approved plan.`

#### 具体テストケース一覧

- `tc-s09-001` manual: eligible targetでselected positive chainを完走する
  - 前提: Human-selected targetがeligibility条件を満たし、external approval/evidence destinationsが準備済み。
  - 操作: selected modeでcreate→Review→Human Gate→adoption/parity→validation/publication→readinessを実行する。
  - 期待結果: full chain完了、unauthorized Portfolio/downstream mutation 0、metrics記録。
  - 失敗検出: synthetic-only acceptanceまたはscope侵入を防ぐ。
  - 検証方法: `tests/integration/test_chatgpt_planning_dogfood.py`
  - 関連 closure id: `CLOS-DOGFOOD`

- `tc-s09-002` negative: ineligible targetを開始前に拒否する
  - 前提: dependency chain内、Portfolio change必要、rollback不明のいずれかのtargetを用意する。
  - 操作: dogfood selection preflightを実行する。
  - 期待結果: live backendとcanonical mutation前にblocked。
  - 失敗検出: dogfoodをPortfolio replanningへ拡張する事故を防ぐ。
  - 検証方法: `tests/integration/test_chatgpt_planning_dogfood.py`
  - 関連 closure id: `CLOS-DOGFOOD`

#### report evidence destination

Mainだけが`report.md`の`Implementation Delegation Gate`、`Step Contract Closure`、`Test Contract Closure`、`Closure Coverage`、`Spec Interpretation / Decision Ledger`へevidenceを統合する。Workerはstructured evidenceを返し、canonical reportを変更しない。

#### step closure contract

`CLOS-DOGFOOD`は、targeted Green、required reviewer passed、commit候補または正当なapproved-no-op、post-commit clean checkが揃った場合だけcloseする。

#### step gate

`SPEC_DOCK_ORACLE_LIVE=1 uv run pytest tests/integration/test_chatgpt_planning_dogfood.py -q`を成功させ、scope外diff 0、fresh `code-reviewer` passed、Main Step Result Approvalを確認する。失敗、skip、unavailable、denied、provisionalをpassとして扱わない。


### S90 docs impact resolution / docs refresh

#### behavior goal

Provider docs、Skill、Prompt reference、READMEをfinal public behaviorへ揃え、Issue／Epic／Initiative boundaryとcurrent shared delivery authorityを正しく説明する。

#### depends on / unblocks

- depends on: S09
- unblocks: S99

#### exact target files

- `src/spec_dock/assets/spec_dock/docs/README.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_planning.md`
- `src/spec_dock/assets/spec_dock/docs/reference_chatgpt_cli.md`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`

#### behavior slice execution

1. Mainがimplementation behaviorとdocs deltaを確定する。
2. `doc-writer`がexact filesだけを日本語ファーストで更新する。
3. commands、mode、lane、Human Gate、external delivery boundaryをsource behaviorと照合する。
4. Mainがdiffをreportへ統合し、fresh `spec-reviewer`へ渡す。

#### planned contract

- scope: exact four provider files。
- test obligation: commands／paths／authority／security／rollback wordingのsource alignment。
- red or alternative evidence: inspect-only plus CLI help snapshot。
- green verification: `uv run pytest tests/cli_runtime/test_chatgpt_planning.py tests/unit/infra/test_init_update.py -q && git diff --check`
- refactor guardrail: generic Review framework、shared delivery policy、sibling planning detailsを追加しない。
- amendment trigger: docsがnew product behaviorを必要とする場合はowning stepへ戻る。

#### delegation contract

- delegated role: `doc-writer`
- input docs: Requirement、Design、Plan、actual CLI help、parent Epic、accepted ADRs。
- allowed paths: exact target files only。
- forbidden changes: code、tests、canonical report、assurance、generated dogfood、shared delivery docs。
- acceptance criteria: `AC-001`, `AC-012`, `AC-015`
- required verification: targeted tests、docs diff、link/path inspection。
- reviewer focus: `spec-reviewer` docs/spec alignment。
- stop conditions: observed behaviorとdocs不一致、scope expansion、missing command evidence。
- output required: changed files、docs impact summary、verification、Ledger Note。

#### 具体テストケース一覧

- `tc-s90-001` docs: official routeとauthorityを一致させる
  - 前提: final CLI help、Skill、Prompt inventory、Requirement／Designが利用可能。
  - 操作: docs／Skillのcommands、mode、lane、Human Gate、external boundaryを照合する。
  - 期待結果: public routeが一意で、Review resultやPlanning runだけのauthority claimがない。
  - 失敗検出: stale legacy route、wrong command、Human bypass、shared policy absorptionを検出する。
  - 検証方法: `tests/cli_runtime/test_chatgpt_planning.py` and `git diff --check`
  - 関連 closure id: `CLOS-DOCS`

#### report evidence destination

Mainが`report.md#Docs-Impact`、`Step Contract Closure`、`Spec Interpretation / Decision Ledger`へ統合する。

#### step closure contract

`CLOS-DOCS`はdocs impact resolved、fresh `spec-reviewer` passed、commit候補、clean checkでcloseする。

#### step gate

`uv run pytest tests/cli_runtime/test_chatgpt_planning.py tests/unit/infra/test_init_update.py -q && git diff --check`、docs link inspection、fresh `spec-reviewer` passedを必要とする。

### S99 final quality gate

#### behavior goal

全stepのclosure、test sufficiency、integrated diff、Requirement／Design／Plan／implementation／tests／docsの整合を三者で確認する。S99はmissing product workを直接実装しない。

#### depends on / unblocks

- depends on: S90 and all material closures
- unblocks: Final Exit

#### exact verification surface

- full provider diff and generated projection diff
- `requirement.md`, `design.md`, `plan.md`, canonical `report.md`
- all focused and repository-wide tests
- package build and fresh install/update evidence
- dogfood evidence and open risk list

#### behavior slice execution

1. Mainがall closures、step reviewer evidence、commit candidates、clean statusを確認する。
2. `uv run pytest -q`、`make lint`、`uv build`、`./spec-dock/scripts/spec-dock validate`を実行する。
3. `qa-reviewer`がtest sufficiency、integration、failure pathsを確認する。
4. issue-wide `code-reviewer`がstructure、responsibility、security、regression riskを確認する。
5. `spec-reviewer`がall requirements、non-goals、authority、docs一致を確認する。
6. failはowning stepへ戻してbounded fix／re-reviewを行う。
7. 三者passed後、Mainがfinal report ledgerを更新しfinal commitを作成、clean checkを行う。

#### delegation contract

- delegated role: reviewer-only; product mutationはowning stepへ戻す。
- input docs: complete planning set、report、diff、test／build／dogfood evidence。
- allowed paths: none for reviewer; review outputs only in external/reviewer-approved destination。
- forbidden changes: repository／Candidate／patch／replacement ZIP／canonical docs。
- acceptance criteria: all ACs。
- required verification: repository-wide commands and three fresh reviewer passes。
- reviewer focus: QA、integrated code、spec conformance。
- stop conditions: any failed/unavailable/denied reviewer、open material ledger、dirty tree、missing closure。
- output required: reviewer results、Main disposition、final commit scope、remaining risks。

#### 具体テストケース一覧

- `tc-s99-001` quality: full suite and package verification
  - 前提: S01〜S90がclosedし、clean branchにfinal candidate diffがある。
  - 操作: full tests、lint、build、validateとthree reviewersを実行する。
  - 期待結果: commands成功、three fresh reviewers passed、open material blocker 0。
  - 失敗検出: focused-only green、docs drift、unreviewed integrated riskを検出する。
  - 検証方法: `uv run pytest -q && make lint && uv build && ./spec-dock/scripts/spec-dock validate`
  - 関連 closure id: `CLOS-QUALITY`

#### report evidence destination

Mainが`report.md#Final-Quality-Gate`、final closure coverage、three reviewer results、final commit scopeへ記録する。

#### step closure contract

`CLOS-QUALITY`はall required closures、full verification、three fresh reviewer passed、final report update、final commit、post-commit clean checkが揃った場合だけcloseする。

#### step gate

failed／unavailable／denied／waived／provisionalをpassedとして扱わない。全三者fresh passedとclean final commitを必要とする。

## 10. Final Exit Contract

### Entry conditions

- S01〜S09、S90、S99のrequired closures complete。
- final report ledger、final commit、post-commit clean check complete。
- current source branch remains the intended Issue branch。

### External delivery handoff

1. Mainはcurrent shared Issue delivery workflowを使用する。
2. one Issue／one branch／one Delivery PRを維持する。
3. PR Delivery／Merge Preparation evidence、required checks／reviews／blockersはshared workflow owner contractに従う。
4. Humanだけがmergeを決定・実行する。
5. merge後verificationとIssue lifecycle completionはcurrent shared workflowへ従い、本Planはそのsemanticsを再定義しない。

### Stop conditions

- required review/check未完了、unresolved blocker、dirty tree、wrong branch/base、source drift、Human decision欠落。
- Planning result、S99 result、PR readinessのいずれもHuman mergeまたはIssue completionを自己主張しない。

### Exit evidence

Final response／PR／Issue comment等のcurrent shared destinationsへfinal commit、PR URL、Human merge evidence、post-merge verification locatorを記録する。Candidate packageへ戻して書き込まない。
