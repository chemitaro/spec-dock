以下をそのままEpic文書へ追記できます。

---

## `requirement.md` 追記案

```markdown
## Agent Context Routing Requirements

- E-RQ-014: Tracked Agent Context Routing Policy
  - SpecDockは、サブエージェントへ渡すコンテキストの種類と範囲を、Git管理されたmachine-readableなpolicyとして管理しなければならない。
  - Context policyは、Assurance Profileやreasoning effortとは独立した設計軸として扱わなければならない。
  - Context policyは少なくとも次のmodeを表現できなければならない。
    - `recent_fork`
    - `bounded_packet`
    - `clean_room`
    - `minimal_packet`
  - Policyは、agent role、step kind、change kind、Assurance Profileに応じて、次を定義できなければならない。
    - context mode
    - fork対象となるturn数
    - includeするcontext category
    - excludeするcontext category
    - required canonical artifacts
    - required repository freshness checks
    - child agentからmain agentへ返却可能なoutput category
  - Runtimeは、tracked policyをcurrent Issue / current StepのAssurance Contractへ適用し、選択済みcontext contractをcurrent Runbookへ展開しなければならない。
  - Agent自身は、Runbookが指定したcontext modeを独自に弱めたり、reviewerのclean-room境界を解除したりしてはならない。

- E-RQ-015: Execution Context Affinity
  - Requirement、design、plan、approved decisionなど、現在の目的遂行に必要な文脈を共有すべき実行系agentには、`recent_fork`または`bounded_packet`を使用できなければならない。
  - 実行系agentは、親agentが既に確定した目的、制約、許可された変更範囲、禁止事項、verification obligationを再調査せず利用できなければならない。
  - Forkまたはpacketによるcontext継承は、current HEAD、worktree state、対象fileの現行内容を再確認する義務を免除してはならない。
  - 同一semantic batch内では、source revision、goal、scope、risk、allowed pathsが変化しない限り、同一worker threadを継続利用できなければならない。

- E-RQ-016: Independent Evaluation Context
  - `spec-reviewer`、`code-reviewer`、`qa-reviewer`は、authorまたはimplementerの会話履歴を継承しない`clean_room` contextを使用しなければならない。
  - Reviewerには、著者の推論過程ではなく、次のnormative evidenceだけを渡さなければならない。
    - approved requirement
    - approved design
    - approved planまたはstep contract
    - base SHA
    - head SHA
    - immutable diff
    - relevant changed files and symbols
    - verification evidence
    - known environment limitations
  - Reviewerへ次を渡してはならない。
    - authorの自己評価
    - implementation transcript
    - private reasoning
    - previous reviewer verdict
    - review結果を誘導する結論
    - rejected hypothesisの全履歴
  - Reviewerは必要な追加fileを独立して参照できるが、author narrativeをauthorityとして扱ってはならない。

- E-RQ-017: Independent Consultant Context
  - `consultant`および`deep-consultant`のfirst passは、main agentの推奨案または他agentの結論を含まない`clean_room`または`bounded_packet`で実行しなければならない。
  - First passには、decision question、objective、verified facts、constraints、evaluation criteria、unknownsだけを渡さなければならない。
  - 複数案の見解が衝突した場合に限り、second-stage arbitrationとして各案と反論を渡すことができる。
  - First passとarbitrationは別のcontext contractとして記録されなければならない。

- E-RQ-018: Context Minimization And Main Context Protection
  - Child agentからmain agentへ返却する情報は、原則として次に限定しなければならない。
    - outcome
    - changed files
    - verification result
    - evidence reference
    - material decision request
    - remaining risk
  - 次をmain agentのcontextへ自動転記してはならない。
    - raw shell transcript
    - full test log
    - stack trace全体
    - 読み込んだ全file一覧
    - failed hypothesisの全履歴
    - private reasoning
  - Raw evidenceは必要に応じてartifactまたはgenerated event storeへ保存し、main agentへはpath、hash、要約だけを返さなければならない。

- E-RQ-019: Context Freshness And Invalidation
  - Context packetは、canonical artifact hash、base SHA、head SHA、policy version、Assurance Contract hashへbindされなければならない。
  - 次のいずれかが発生した場合、既存context packetまたはworker continuationをstaleとして扱わなければならない。
    - requirementのsubstantive change
    - designのsubstantive change
    - planまたはstep contractのsubstantive change
    - branchまたはhead SHAの変更
    - allowed scopeの変更
    - new hard-riskの発見
    - Assurance escalation
  - Stale contextを使用してexecutionまたはreviewを続行してはならない。

- E-RQ-020: Context Policy Observability
  - 各agent invocationについて、次をmachine-readable evidenceとして記録しなければならない。
    - role
    - reasoning effort
    - context mode
    - context policy version
    - context packet hash
    - source artifact hashes
    - fork turn count
    - included category
    - excluded category
    - returned evidence references
  - Private reasoning、secret、credential、raw tokenを記録してはならない。
```

### 受け入れ条件の追記

```markdown
- E-AC-015: Role-specific context compilation
  - 前提:
    - 同一Issue内に、implementation step、code review、consultant decisionの各taskがある。
  - 操作:
    - 各taskのRunbookをcompileする。
  - 期待結果:
    - implementation workerには`recent_fork`または`bounded_packet`が選択される。
    - code reviewerには`clean_room`が選択される。
    - consultant first passにはmainの推奨案を含まない独立contextが選択される。
  - 観測点:
    - compiled Runbook JSON
    - context policy unit tests
    - golden context packet tests

- E-AC-016: Reviewer independence
  - 前提:
    - Main agentとdev-coderが実装を完了している。
  - 操作:
    - code-reviewer用context packetをcompileする。
  - 期待結果:
    - approved specification、immutable diff、verification evidenceは含まれる。
    - author self-assessment、implementation transcript、previous reviewer verdictは含まれない。
  - 観測点:
    - generated packet
    - inclusion / exclusion assertions

- E-AC-017: Worker context reuse
  - 前提:
    - 同一semantic batch内でgoal、scope、source revisions、riskが変更されていない。
  - 操作:
    - 次のworker actionを開始する。
  - 期待結果:
    - 既存worker threadを継続利用できる。
    - full repository reorientationを要求しない。
    - current HEADとworktree stateのbounded revalidationは実行される。
  - 観測点:
    - invocation history
    - repository freshness evidence
    - reorientation metrics

- E-AC-018: Context invalidation
  - 前提:
    - Context packet生成後にdesignまたはallowed scopeがsubstantive変更された。
  - 操作:
    - 既存packetを用いてexecutionを開始する。
  - 期待結果:
    - packetがstaleとして拒否され、再compileがnext actionになる。
  - 観測点:
    - hash mismatch test
    - workflow state transition

- E-AC-019: Main context minimization
  - 前提:
    - Child agentが複数fileの調査、test execution、失敗した仮説の検討を行った。
  - 操作:
    - Child agent resultをmain agentへ返す。
  - 期待結果:
    - mainへ返るのはoutcome、evidence refs、material decisions、remaining risksに限定される。
    - raw logsとprivate reasoningは含まれない。
  - 観測点:
    - return contract tests
    - generated event artifacts
```

---

## `design.md` 追記案

````markdown
## Agent Context Routing Architecture

### 目的

Agent Context Routingは、次の三つを同時に達成する。

1. Main orchestratorのcontextを目的、制約、意思決定、進行管理に集中させる。
2. 実行系agentへ既知の文脈を再利用可能な形で渡し、再調査とtoken消費を削減する。
3. Reviewerおよびconsultantの認知的独立性を維持する。

Context routingは、Assurance Profileおよびreasoning effortとは独立した設計軸とする。

```text
Role
  = 責任と権限

Reasoning effort
  = 推論の深さ

Context policy
  = 何を継承し、何から独立するか

Assurance profile
  = 必須verification / review / human gateの深さ
````

### Canonical Policy Files

```text
spec-dock/system/assurance/
├── context-routing-policy.json
└── schemas/
    └── context-routing-policy.schema.json
```

`context-routing-policy.json`はprovider-owned tracked policyとする。

Issueごとのcontext選択結果は`assurance.json`およびcompiled Runbookへ展開する。

Generated context packetはGit管理しない。

```text
spec-dock/.agent/context-packets/
└── <issue-id>/
    └── <contract-hash>/
        ├── architect.json
        ├── planner.json
        ├── worker-S01.json
        ├── code-reviewer-S01.json
        └── consultant-first-pass.json
```

### Context Modes

#### `recent_fork`

用途:

* system-architect
* implementation-planner
* dev-coder
* 同一semantic batch内の継続worker

特徴:

* 親agentの直近の必要な会話文脈を継承する。
* 過去全履歴ではなく、policyで指定したbounded turn数を使用する。
* Canonical artifactとcurrent step contractを追加で付与する。
* Child agentが新たに取得したraw contextはmainへ自動返却しない。

#### `bounded_packet`

用途:

* repo-analyst
* researcher
* doc-writer
* task scopeが明確なworker
* fork機能が利用できないruntime

特徴:

* Objective、constraints、approved decisions、relevant paths、source hashes、verification obligationsを構造化packetとして渡す。
* Main agentの会話履歴を直接渡さない。
* Taskに不要なcanonical artifactや過去の議論を含めない。

#### `clean_room`

用途:

* spec-reviewer
* code-reviewer
* qa-reviewer
* consultant first pass
* deep-consultant first pass

特徴:

* Authorまたはimplementerの会話履歴を継承しない。
* Normative contractとimmutable evidenceだけを渡す。
* Previous reviewer verdictやauthor conclusionを渡さない。
* Independent evaluationを目的とする。

#### `minimal_packet`

用途:

* utility-worker
* spec-manager
* bounded command execution
* deterministic state check

特徴:

* Target、command、working directory、allowed side effect、expected outputだけを渡す。
* Requirement、design、planの全文を渡さない。

### Default Role Routing

| Role                       | Default context |  Reasoning | 補足                                   |
| -------------------------- | --------------- | ---------: | ------------------------------------ |
| main orchestrator          | root thread     |     medium | 目的、判断、統合を保持                          |
| system-architect           | recent_fork     |       high | high-risk designではxhigh              |
| implementation-planner     | recent_fork     |       high | approved requirement/designを付与       |
| dev-coder                  | recent_fork     |     medium | 同一semantic batchでは継続可能               |
| repo-analyst               | bounded_packet  |     medium | Mainの仮説を結論として渡さない                    |
| researcher                 | bounded_packet  | low/medium | 外部調査目的とsource criteriaだけ             |
| doc-writer                 | bounded_packet  | low/medium | 対象artifactと同期契約を付与                   |
| utility-worker             | minimal_packet  |        low | bounded commandのみ                    |
| spec-reviewer              | clean_room      |       high | approved artifactsとevidenceのみ        |
| code-reviewer              | clean_room      |       high | immutable diffとverification evidence |
| qa-reviewer                | clean_room      |       high | behavior obligationsとtest evidence   |
| consultant first pass      | clean_room      |       high | mainの推奨案を渡さない                        |
| deep-consultant first pass | clean_room      |      xhigh | 不可逆判断の独立意見                           |
| consultant arbitration     | bounded_packet  | high/xhigh | 独立意見取得後だけ各案を提示                       |

### Context Routing Policy Example

```json
{
  "schema_version": 1,
  "policy_version": "context-routing-v1",
  "defaults": {
    "repository_revalidation": [
      "git_head",
      "worktree_status"
    ],
    "return_contract": [
      "outcome",
      "changed_files",
      "verification",
      "evidence_refs",
      "decision_requests",
      "remaining_risks"
    ],
    "excluded_return_categories": [
      "private_reasoning",
      "raw_shell_transcript",
      "full_test_log",
      "failed_hypothesis_history"
    ]
  },
  "roles": {
    "system-architect": {
      "mode": "recent_fork",
      "fork_turns": 4,
      "include": [
        "current_objective",
        "approved_requirement",
        "user_approved_decisions",
        "repository_context",
        "design_constraints",
        "unresolved_questions"
      ],
      "exclude": [
        "main_recommended_solution",
        "previous_reviewer_verdicts",
        "raw_tool_logs"
      ]
    },
    "implementation-planner": {
      "mode": "recent_fork",
      "fork_turns": 3,
      "include": [
        "approved_requirement",
        "approved_design",
        "acceptance_criteria",
        "repository_context",
        "verification_constraints"
      ],
      "exclude": [
        "raw_tool_logs",
        "previous_reviewer_verdicts"
      ]
    },
    "dev-coder": {
      "mode": "recent_fork",
      "fork_turns": 3,
      "include": [
        "current_objective",
        "approved_decisions",
        "current_step_contract",
        "affected_paths",
        "affected_symbols",
        "allowed_changes",
        "forbidden_changes",
        "verification_obligations"
      ],
      "exclude": [
        "previous_reviewer_verdicts",
        "unrelated_issue_history",
        "raw_external_research"
      ],
      "continuation": {
        "enabled": true,
        "require_same": [
          "goal",
          "source_binding",
          "scope",
          "risk",
          "allowed_paths"
        ]
      }
    },
    "code-reviewer": {
      "mode": "clean_room",
      "include": [
        "approved_requirement",
        "approved_design",
        "approved_step_contract",
        "base_sha",
        "head_sha",
        "immutable_diff",
        "changed_files",
        "verification_evidence",
        "known_environment_limitations"
      ],
      "exclude": [
        "author_self_assessment",
        "implementation_transcript",
        "private_reasoning",
        "previous_reviewer_verdicts",
        "author_recommended_outcome"
      ]
    },
    "consultant": {
      "mode": "clean_room",
      "include": [
        "decision_question",
        "objective",
        "verified_facts",
        "constraints",
        "evaluation_criteria",
        "unknowns"
      ],
      "exclude": [
        "main_recommended_option",
        "architect_recommended_option",
        "previous_consultant_verdicts"
      ]
    },
    "utility-worker": {
      "mode": "minimal_packet",
      "include": [
        "target",
        "command",
        "working_directory",
        "allowed_side_effects",
        "expected_output"
      ]
    }
  }
}
```

### Context Packet Contract

```json
{
  "schema_version": 1,
  "policy_version": "context-routing-v1",
  "issue_id": "iss-xxxxx",
  "step_id": "S02",
  "role": "dev-coder",
  "reasoning_effort": "medium",
  "context_mode": "recent_fork",
  "fork_turns": 3,
  "source_binding": {
    "assurance_contract_sha256": "sha256:...",
    "requirement_sha256": "sha256:...",
    "design_sha256": "sha256:...",
    "plan_sha256": "sha256:...",
    "base_sha": "...",
    "head_sha": "..."
  },
  "objective": "...",
  "approved_decisions": [],
  "scope": {
    "affected_paths": [],
    "affected_symbols": [],
    "allowed_changes": [],
    "forbidden_changes": []
  },
  "verification_obligations": [],
  "stop_conditions": [],
  "return_contract": [
    "outcome",
    "changed_files",
    "verification",
    "evidence_refs",
    "decision_requests",
    "remaining_risks"
  ]
}
```

### Reviewer Evidence Packet

```json
{
  "schema_version": 1,
  "role": "code-reviewer",
  "context_mode": "clean_room",
  "review_target": {
    "base_sha": "...",
    "head_sha": "...",
    "diff_sha256": "sha256:..."
  },
  "normative_sources": {
    "requirement_sha256": "sha256:...",
    "design_sha256": "sha256:...",
    "step_contract_sha256": "sha256:..."
  },
  "verification_evidence": [],
  "known_limitations": [],
  "excluded_categories": [
    "author_self_assessment",
    "implementation_transcript",
    "private_reasoning",
    "previous_reviewer_verdicts"
  ]
}
```

### Compilation Flow

```text
Assurance Contract
  +
Current Workflow State
  +
Current Step Facts
  +
Agent Role
  +
Context Routing Policy
        |
        v
Context Policy Resolver
        |
        v
Compiled Context Contract
        |
        +--> Current Runbook
        |
        +--> Context Packet
        |
        +--> Invocation Evidence
```

1. Workflow State Resolverがcurrent actionを決定する。
2. Step Assurance Compilerがrole、reasoning effort、required reviewを決定する。
3. Context Policy Resolverがroleとtask typeからcontext modeを選択する。
4. Assurance Profileまたはhard-risk ruleが必要ならmodeを強化する。
5. Context packetをcanonical source hashへbindする。
6. Current Runbookへcontext contractを埋め込む。
7. Agent invocation後、return contractに従って結果を圧縮する。
8. Source bindingが変化した場合、packetをstaleにする。

### Precedence

Context policyの優先順位は次とする。

```text
hard safety rule
  >
issue global obligation
  >
step local obligation
  >
role default
```

例:

* Reviewerは常に`clean_room`。
* Security-sensitive stepがworkerの追加evidenceを必要としても、reviewerへauthor transcriptを渡してはならない。
* Main agentまたはchild agentは、token削減を理由にrequired canonical sourceを省略してはならない。
* Model confidenceだけで`clean_room`を`recent_fork`へ変更してはならない。

### Freshness And Revalidation

Forkまたはpacketはrepository stateの再確認を省略する仕組みではない。

Execution agentは最低限次を確認する。

```text
- current branch
- current HEAD
- worktree status
- target filesの現行revision
```

Reviewerは次を確認する。

```text
- reviewed head SHA
- immutable diff hash
- normative artifact hashes
```

次の場合にcontextをinvalidateする。

```text
- requirement / design / planのsubstantive change
- Assurance escalation
- current step contract change
- branch / head change
- allowed scope change
- protected risk discovery
```

### Context Return Boundary

Child agentは次だけをmainへ返す。

```text
- outcome
- changed files
- verification result
- evidence references
- material decision requests
- remaining risks
```

Raw evidenceが必要な場合は、generated artifactへ保存する。

```text
spec-dock/.agent/events/
spec-dock/.agent/evidence/
```

Mainへraw logを直接返さない。

### Failure Design

| Failure                                   | 判定                | 動作                              |
| ----------------------------------------- | ----------------- | ------------------------------- |
| context policy missing                    | blocked           | policy restore / doctor         |
| invalid policy schema                     | blocked           | validation error                |
| unknown role                              | fail-closed       | explicit routing required       |
| source hash mismatch                      | stale             | context recompile               |
| required clean-room unavailable           | blocked           | fresh agent capability required |
| fork unsupported                          | fallback          | bounded_packetへ明示fallback       |
| packet too large                          | blocked / compact | mandatory categoryを保持して再compile |
| excluded category detected                | blocked           | packet generation defect        |
| worker continuation binding mismatch      | reset             | new worker invocation           |
| reviewer packet includes author narrative | blocked           | clean-room packet rebuild       |

### Observability

各invocation eventに次を記録する。

```json
{
  "event": "AgentInvoked",
  "role": "code-reviewer",
  "reasoning_effort": "high",
  "context_mode": "clean_room",
  "context_policy_version": "context-routing-v1",
  "context_packet_sha256": "sha256:...",
  "source_binding": {},
  "included_categories": [],
  "excluded_categories": [],
  "fork_turns": null
}
```

記録しないもの:

```text
- private reasoning
- raw credential
- secret
- complete prompt body
- full raw logs
```

### Testing Strategy

* Role routing matrix:

  * architect
  * planner
  * coder
  * reviewer
  * consultant
  * utility worker
* Inclusion / exclusion tests:

  * Reviewer packetへauthor narrativeが混入しない。
  * Worker packetへprevious reviewer verdictが混入しない。
* Freshness tests:

  * source hash変更でstale。
  * HEAD変更でreview packet stale。
* Continuation tests:

  * same semantic batchではreuse。
  * scope変更時はreset。
* Fallback tests:

  * recent fork unavailable時にbounded packet。
  * clean-room unavailable時はfail-closed。
* Token-efficiency tests:

  * full canonical document再送との差分。
  * mainへ返るresult payload size。
  * repeated worker reorientationの減少。

````

---

## `plan.md` のI04差し替え案

```markdown
### I04 — Compile Step Assurance, Agent Routing, And Context Policy

- provisional slug:
  - `compile-step-assurance-agent-routing-and-context-policy`

- 目的:
  - Plan step facts、Issue-wide Assurance、agent role、task kindから、worker、reasoning effort、context mode、verification、reviewerを含むcurrent execution Runbookを生成する。
  - 実行系agentへの必要なcontext継承と、reviewer / consultantのclean-room independenceを同時に実現する。
  - Main orchestratorへ返るcontextを圧縮し、subagentの再調査とmain context pollutionを削減する。

- 成果物:
  - Step Assurance schema / compiler。
  - `context-routing-policy.json`。
  - `context-routing-policy.schema.json`。
  - Context Policy Resolver。
  - `recent_fork / bounded_packet / clean_room / minimal_packet`。
  - Role別default context policy。
  - Step kind / risk別override。
  - Context Packet compiler。
  - Reviewer Evidence Packet compiler。
  - Consultant first-pass / arbitration context contract。
  - Worker continuation policy。
  - Context source bindingとstale invalidation。
  - Mainへのbounded return contract。
  - Current Runbookへのcontext contract展開。
  - Invocation evidenceとtoken / payload observability。
  - Provider source / dogfooding mirror / tests / docs。

- Assurance:
  - strict / deep

- closes:
  - E-RQ-007
  - E-RQ-008
  - E-RQ-014
  - E-RQ-015
  - E-RQ-016
  - E-RQ-017
  - E-RQ-018
  - E-RQ-019
  - E-RQ-020
  - E-AC-006
  - E-AC-007
  - E-AC-015
  - E-AC-016
  - E-AC-017
  - E-AC-018
  - E-AC-019

- 依存:
  - I03

- implementation outline:
  1. Context routing schemaとrole defaultsを追加する。
  2. Context modeとprecedenceをdomain modelへ追加する。
  3. Step Assurance CompilerからContext Policy Resolverを呼び出す。
  4. Context Packet / Reviewer Evidence Packetを生成する。
  5. Source bindingとstale invalidationを実装する。
  6. Worker continuation eligibilityを実装する。
  7. Current Runbookへcontext contractを展開する。
  8. Child agent return contractを実装する。
  9. Role routing、include / exclude、freshness、fallbackのtestsを追加する。
  10. Provider / dogfooding mirrorとreference docsを同期する。

- 受け入れ条件:
  - docs-only、runtime behavior、migration、security-sensitiveの各Stepで、worker、reasoning、context、verification、reviewersがpolicyどおりに異なる。
  - `dev-coder`は同一semantic batch内で`recent_fork`または`bounded_packet`を利用できる。
  - `code-reviewer`、`qa-reviewer`、`spec-reviewer`は常にclean-room packetを使用する。
  - Reviewer packetへauthor self-assessment、implementation transcript、previous reviewer verdictが含まれない。
  - Consultant first passへmain / architectの推奨案が含まれない。
  - Consultant arbitrationは独立意見取得後に限り各案を受け取る。
  - Same source bindingとscopeではworker threadを継続できる。
  - Source binding、scope、riskの変更後はworker continuationを拒否する。
  - Fork機能が利用できない場合、workerはbounded packetへfallbackできる。
  - Clean-roomを提供できない場合、reviewを実行せずfail-closedになる。
  - Raw shell transcript、full test log、private reasoningがmain agentのreturn payloadへ混入しない。
  - Current Runbookには選択されたcontext contractだけが含まれ、他modeの完全な説明は含まれない。

- 主なテスト:
  - context policy schema tests
  - role routing table tests
  - context precedence tests
  - reviewer clean-room exclusion tests
  - consultant blind-first-pass tests
  - worker continuation tests
  - source binding invalidation tests
  - recent-fork fallback tests
  - bounded return contract tests
  - golden Runbook / context packet tests
  - provider / mirror parity tests

- 非対象:
  - GitHub PR review trigger。
  - GitHub review finding blocker policy。
  - Cross-provider agent context transfer。
  - Private reasoningの保存または転送。
````

---

## Epic要件の短い補足説明として使える文面

```markdown
### Context Routingに関する補足

本Epicにおけるsubagent利用は、単に作業を複数agentへ分割することを目的としない。

Subagentは次の二つの目的で使用する。

1. Taskに応じたreasoning effortと専門roleを選択する。
2. Main orchestratorのcontextを目的、制約、判断、進行管理に集中させ、詳細な調査、実装、test log、失敗した仮説をchild contextへ隔離する。

ただし、全subagentをfresh contextで開始すると、既知の目的、制約、repository context、approved decisionを再取得するtokenと時間が発生する。

そのため、実行系agentには必要なcontextを継承する`recent_fork`または`bounded_packet`を使用する。一方、reviewerとconsultant first passには著者の推論や結論を継承しない`clean_room`を使用する。

設計原則は次のとおりとする。

> Agents performing the same objective receive bounded inherited context.  
> Agents evaluating the result receive normative contracts and immutable evidence, not the author's narrative.

Context modeはmodelの都度判断に委ねず、tracked context routing policyとcurrent Assurance Contractからruntimeがcompileし、current Runbookへ展開する。
```
