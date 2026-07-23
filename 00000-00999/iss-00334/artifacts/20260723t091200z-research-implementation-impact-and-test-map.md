---
種別: research
ID: "20260723t091200z-research-implementation-impact-and-test-map"
タイトル: "iss-00334 実装影響面・module配置・test接続点調査"
状態: "completed"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-23"
親: ["iss-00334", "epic-00331", "init-00322"]
scope: "issue"
scope_id: "iss-00334"
authority: "source-grounded-evidence"
canonical_status: "non-authoritative"
source_repository: "chemitaro/spec-dock"
source_branch: "iss-00334-implement-chatgpt-issue-planning-workflow"
source_commit: "347c2f79086730ccd7af99ba836d0c1b758f4a95"
derived_from:
  - "src/spec_dock/assets/spec_dock/scripts/spec-dock"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/authoring.py"
  - "src/spec_dock/cli.py"
  - "pyproject.toml"
  - "AGENTS.md"
reflected_to: []
---

# 20260723t091200z-research-implementation-impact-and-test-map

## 位置づけ

- このArtifactは、`iss-00334`の正式Candidateを作成する前に、現行repositoryのCLI構造、配布境界、layered runtime、authoring-pack、testsを調査し、実装時の変更面をsource-groundedに整理する。
- 本文はcanonical Requirement／Design／Planやaccepted ADRを上書きしない。
- exact class名やprivate helper名は実装中に最小差分で調整できるが、責務境界とprovider／installed／dogfood投影は本調査を基準とする。

## 調査結果サマリー

1. day-to-day operationはglobal `spec-dock` installer CLIではなく、repo-local `spec-dock/scripts/spec-dock`が担う。
2. repo-local entrypointはstdlib-onlyのthin shimで、`spec_dock_runtime.app`を起動する。
3. current Core runtime parserには`authoring ...` command群が直接登録され、command handlerは`commands/authoring.py`からapplication／domain／infra／presentationへ委譲する。
4. package dataは`assets/**/*`を配布するため、新しいrepo-local executable、Python module、Prompt Markdown resourceはprovider assetsへ置けばwheel／sdistへ含められる。
5. installerは`docs`、`templates`、`scripts`、`system`をmanaged treeとして同期するため、`spec-dock-chatgpt`を`spec-dock/scripts/`へ投影できる。
6. 現在のproject console scriptはinstaller用`spec-dock = spec_dock.cli:main`だけであり、vNextのday-to-day ChatGPT commandをglobal installer CLIへ混在させる必要はない。
7. 新しいChatGPT-facing CLIは、repo-local sibling executableとして分離し、underlying deterministic primitiveは既存`spec_dock_runtime` layerから再利用するのが最小変更である。

## 推奨される実装配置

### Provider authority

```text
src/spec_dock/assets/spec_dock/scripts/
├── spec-dock
├── spec-dock-chatgpt                         # new independent repo-local CLI entrypoint
└── spec_dock_runtime/
    ├── chatgpt_app.py                        # new ChatGPT CLI bootstrap
    ├── cli/
    │   ├── chatgpt_parser.py                 # planning create/revise, review planning
    │   ├── chatgpt_registry.py
    │   └── chatgpt_dispatch.py               # existing contracts reuse where practical
    ├── commands/
    │   ├── chatgpt_planning.py               # ChatGPT-facing operations
    │   └── planning_adoption.py              # Core deterministic adoption operations
    ├── application/
    │   ├── issue_planning/
    │   │   ├── create_candidate.py
    │   │   ├── revise_candidate.py
    │   │   ├── review_planning.py
    │   │   ├── approval_capture_validation.py
    │   │   ├── adopt_candidate.py
    │   │   ├── verify_parity.py
    │   │   ├── verify_publication.py
    │   │   └── verify_readiness.py
    │   └── authoring_pack/                   # reusable existing primitives remain
    ├── domain/
    │   └── issue_planning/
    │       ├── candidate_contract.py
    │       ├── review_identity.py
    │       ├── authorization_contract.py
    │       ├── parity_contract.py
    │       ├── publication_contract.py
    │       └── readiness.py
    ├── infra/
    │   └── issue_planning/
    │       ├── git_binding.py
    │       ├── oracle_backend.py
    │       ├── prompt_resources.py
    │       ├── candidate_archive.py
    │       ├── atomic_adoption.py
    │       └── publication.py
    ├── presentation/
    │   └── issue_planning/
    │       ├── json_renderer.py
    │       └── text_renderer.py
    └── resources/
        └── chatgpt_prompts/
            ├── prompt-set.json
            ├── operations/
            │   ├── issue-planning-create.md
            │   ├── issue-planning-revise.md
            │   └── issue-planning-review.md
            └── fragments/
                ├── repository-source.md
                ├── target-navigation.md
                ├── task-contract.md
                ├── operator-context.md
                ├── explicit-attachments.md
                ├── sensitive-data-boundary.md
                ├── information-insufficient.md
                ├── issue-bundle-output-contract.md
                └── planning-review-output-contract.md
```

上記は責務配置を示す。実装時に小さなmoduleを統合することは可能だが、ChatGPT transport、domain contract、filesystem／Git、renderingを再びmonolithic commandへ戻してはならない。

### Installed／dogfood projection

```text
spec-dock/scripts/spec-dock-chatgpt
spec-dock/scripts/spec_dock_runtime/**
```

- provider assetから`spec-dock update`で投影する。
- dogfood側をimplementation source of truthとして直接編集しない。
- installerは既存`spec-dock`と新規`spec-dock-chatgpt`の双方へexecutable bitを設定する。

### Skill／docs

```text
src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md
src/spec_dock/assets/spec_dock/docs/workflow_planning.md
src/spec_dock/assets/spec_dock/docs/workflow_issue.md
src/spec_dock/assets/spec_dock/docs/reference_chatgpt_cli.md
```

- E1-I1ではIssue Planning Skillのofficial pathをvNextへ更新する。
- planning-specific legacy Skill／docsの物理削除はE1-I3へ残す。
- `workflow_planning.md`がまだ存在しない場合は、Issue Planningで必要な共通mechanicsを最小限作成し、Portfolio Planningで共通化を拡張する。

## CLI boundary

### ChatGPT-facing CLI

Canonical invocation:

```text
./spec-dock/scripts/spec-dock-chatgpt planning create <target>
./spec-dock/scripts/spec-dock-chatgpt planning revise <target>
./spec-dock/scripts/spec-dock-chatgpt review planning <target>
```

Logical CLI nameは`spec-dock-chatgpt`とする。

所有するもの:

- target／parent／dependency／relevant path resolution
- named branch／clean tree／upstream／local HEAD == remote HEAD preflight
- provider-managed Prompt resource合成
- direct-argv Oracle invocation
- Oracle session／artifact retrieval
- ChatGPT-facing result identity

所有しないもの:

- Review modeのsemantic選択
- Semantic／Mechanical Revision判定
- Human approval判断
- canonical mutation
- commit／push／merge
- `execution-ready`自己宣言

### Core deterministic runtime

既存Core CLIまたはSkillから呼び出すdeterministic operationは、Candidate検査、approval検証、adoption、parity、validation、publication verification、readiness derivationを所有する。

これらを`spec-dock-chatgpt`へ入れない理由:

- accepted thin-adapter境界を維持する。
- ChatGPT transport失敗とrepository mutation失敗を分離する。
- Human Gate前に外部CLIがcanonical mutationする経路を作らない。

## 既存primitiveの再利用map

| Existing surface | Disposition | vNext usage |
|---|---|---|
| `github_sync_preflight` | reuse／harden | exact branch／HEAD、source manifest、typed failure |
| `git_fetch` policy | reuse | fixed argv、noninteractive env、bounded retry |
| `backend_invoke` | refactor／reuse | direct argv Oracle adapter。shell command stringは廃止方向 |
| prompt pack source manifest | reuse concept | structured source baseline／hash |
| ZIP central directory inspection | reuse／extend | exact Candidate safety contract |
| safe extraction | reuse／extend | collision、resource limit、path safety |
| pack digest | reuse | Candidate／Review identity binding |
| staging ownership guard | reuse pattern | canonical adoption staging／non-owned target protection |
| approval check | replace semantic contract／reuse validators | Issue authorization exact identity validation |
| candidate validation | extend | new `issue-planning` Candidate kind |
| preflight receipt writer | reuse atomic writer pattern | Workbench／evidence output publication where needed |
| diagnostics redaction | reuse | Prompt／Git／Oracle failure evidence |
| old Evidence Adoption Ledger | legacy only | vNext authorityには使わない |
| old `spec-dock-chatgpt-authoring` Skill | coexist until E1-I3 | vNext official Issue Planningからは呼ばない |

## Candidate／Review／authorization data contracts

### Candidate

```text
(single root)
requirement.md
design.md
plan.md
SOURCE-BASELINE.json
MANIFEST.json
CHECKSUMS.sha256
```

- `report.md`、`.meta.json`、`.assurance.json`、raw transcriptを含めない。
- Candidate version、logical filename、internal root、Candidate ID、external ZIP SHA、source bindingでidentityを構成する。

### Review

```text
review-result.json
review-result.md
```

- JSONはprotocol-specific structured result。
- MarkdownはHuman-readable rendering。
- Runtimeはfindingのsemantic verdictをparseしない。
- wrapperはschema、identity、hash、session referenceだけを検証する。

### Human authorization

```text
scope Workbench:
  human-issue-plan-authorization-source.json

Issue artifacts:
  <timestamp>-disc-human-issue-plan-authorization.md
```

- source JSONはHuman回答をMainが構造化captureした一次record。
- canonical Markdownはsource record SHA、exact reviewed identity、approver、timestamp、Plan adoption、implementation-start authorizationをclosed renderする。

## Readiness integration

現行`workflow status`はassurance、Design／Plan readiness、legacy `report.md` gateから`ready`を導出する。

E1-I1では既存stateを破壊的に置換せず、vNext Planning Adoption verifierを追加する。

```text
ready
blocked
stale
insufficient-evidence
```

検証入力:

- Review identity
- Human authorization evidence
- archive／git-bound parity
- required validation result
- Planning publication local／remote identity

E1-I3 cutoverでofficial guidanceをvNext readinessへ切り替え、legacy report-based planning gateをplanning-specific routeから除去する。

## Test impact map

### CLI runtime

```text
tests/cli_runtime/test_chatgpt_planning.py
tests/cli_runtime/test_planning_adoption.py
tests/cli_runtime/test_planning_readiness.py
```

検証:

- create／revise／review command grammar
- target resolution
- output format
- no one-shot Human Gate bypass
- exit code taxonomy

### Unit — domain

```text
tests/unit/domain/issue_planning/
```

検証:

- Candidate identity
- closed transport alias
- source drift
- Review identity
- authorization exact binding
- parity state
- publication state
- `PA-NF-01`〜`PA-NF-10`

### Unit — application

```text
tests/unit/application/issue_planning/
```

検証:

- archive positive path
- git-bound positive path
- Semantic／Mechanical new identity
- Human rejection
- partial adoption／resume
- publication parent／blob parity
- readiness derivation

### Unit — infra

```text
tests/unit/infra/issue_planning/
```

検証:

- Prompt resource inventory／hash
- direct argv／shell injection
- sensitive-data rejection／redaction
- safe ZIP extraction
- symlink／TOCTOU／non-owned target
- atomic replace／rollback
- fake remote push／remote HEAD verification
- Oracle timeout／reattach／artifact retrieval

### Integration

```text
tests/integration/test_chatgpt_planning_oracle_smoke.py
```

- fake backend contractを既定にし、real Oracleはmanual／opt-in smokeとする。
- provider wheel、fresh init、update、dogfood parityを検証する。

### Installer／package

```text
tests/unit/infra/test_init_update.py
tests/test_cli.py
```

検証:

- `spec-dock-chatgpt` entrypointがfresh init／updateで配置され実行可能。
- Prompt resourcesがwheel／sdistへ含まれる。
- generated Python cacheが混入しない。
- provider／installed／dogfood inventoryが一致する。

## Completion test matrix

1. archive happy path。
2. git-bound happy path。
3. `PA-NF-01`〜`PA-NF-10`個別fixture。
4. Prompt resource欠落／未知fragment／未解決placeholder。
5. exact branch／HEAD確認不能。
6. Oracle timeout／permanent access denial／artifact missing。
7. Candidate ZIP全unsafe class。
8. Human authorization field／SHA／identity mismatch。
9. Candidate payload semantic mutation。
10. publication HEAD parent／blob／remote mismatch。
11. provider／installed／dogfood parity。
12. current Portfolio／downstream Issue unauthorized mutation 0。
13. one Issue／one branch／one Delivery PR boundary。
14. representative real Issue dogfood。

## 調査からの結論

- 新CLIはglobal installer CLIへ混在させず、repo-local sibling executableとして実装するのが現行architectureと最も整合する。
- underlying moduleは既存`spec_dock_runtime`のlayered architectureへ配置し、authoring-packの安全primitiveを再利用する。
- Prompt MarkdownはRuntime resourceとして配布し、docsから実行時に読む設計にはしない。
- E1-I1はreplacement capabilityを実装するが、旧planning-specific surfaceの物理削除はE1-I3まで延期する。
- RuntimeはReview内容の意味をparseせず、exact identityと決定的gateだけを検証する。
- 追加のHuman意思決定を必要とするmaterialなgapは見つからなかった。

## Candidate文書への含意

- Requirement:
  - 独立repo-local CLI、closed Prompt resource、dual transport、Human authorization、publication、readiness、parityを必須化する。
- Design:
  - 上記layer／module配置、data contract、sequence、failure／rollback、projectionを具体化する。
- Plan:
  - walking skeletonをhorizontal foundationへ分割せず、TDDでvertical tranchesとして実装する。
  - provider実装、projection、tests、docs、dogfoodを同一Issueで完了する。

## 未検証事項

- real Oracle browser modeのlive behaviorは実装後のopt-in smokeで確認する。
- exact dogfood Issueはfeature-complete直前に最新repository状態からHumanが選定する。
- E1-I3によるlegacy physical removalのexact inventoryは同IssueのJIT Planningで再調査する。
