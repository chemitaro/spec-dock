---

kind: "tdd-ready-design-candidate"
issue: "iss-00395"
title: "Issue #395 TDD実装準備版Design"
generated_at: "2026-09-15"
repository: "chemitaro/spec-dock"
branch: "iss-00395-regression-baseline-terminalization-and-product-defect-repair"
verified_tip_sha: "25b33cfaf6214d8c78494f0e0520ef8738bc862f"
verified_tip_tree: "ad6c2fdc2434e514a4b23eb29dbabf33c33b8db8"
p392_entry_sha: "921bf7512c72bfa2887673cb7ec9bc512cec6ff3"
p392_entry_tree: "190bc566a18cd84813c4b7c043f8724e275cb55d"
implementation_allowed: false
owner_decisions_required: []
human_merge_only: true
authority: "advisory-canonical-replacement-candidate"
---

# Issue #395 TDD実装準備版Design

## 1. 設計判断

Issue #395の実装設計は、14 active rowsを四つのrepair unitと一つのterminal transitionへ分解します。

1. Rows 4–11: test doubleをcurrent descriptor-bound portへ追随させる
2. Rows 1・13・14・15: obsolete active observer argumentsをcurrent selection-only surfaceへ追随させる
3. Row 3: read-only identityとpublication policyの責務を分離する
4. Row 12: current thin-shell boundaryをno-editで保護する
5. 全behavior GREEN後: dogfood projectionを完了し、ledgerを最後にterminalizeする

この順序は、Productを古いtest前提へ戻さず、ledgerを先に書き換えて失敗を隠さず、candidate-changing provider sourceをdogfoodへ完全投影するために固定します。

## 2. Authority hierarchy

競合時のauthorityは次の順です。

1. Parent Epic Requirementとaccepted ADR
2. Post-#387 Regression Baseline Register
3. Provider Lifecycle Wire Contract
4. Epic Integration Branch ContractとRolling-Wave Contract
5. Issue Requirement
6. Issue Design
7. Issue Plan
8. LunaMax handoff
9. 実装時の補助evidence tool

Plan、handoff、補助toolは、上位contractを変更または拡張できません。Handoffの省略表現がPlanを弱める場合はPlanを採用し、PlanがDesignのboundaryを越える場合は実装を停止します。

## 3. System boundaries

### 3.1 Product source of truth

Provider-side runtime sourceは`src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`です。Checked-in `spec-dock/scripts/spec_dock_runtime/`はdogfood projectionです。

Provider behaviorを修正する場合はprovider sourceを先に変更し、focused GREEN後にcurrent lifecycle updateでdogfoodへ投影します。Generated dogfood filesを直接編集しません。

### 3.2 Layer boundary

* `commands`: CLI contractとrequest translation
* `application`: use-case contractとorchestration
* `domain`: catalogueとbusiness ruleのsource of truth
* `infra`: Git、filesystem、GitHub、persistence boundary
* `tests/cli_runtime`: shipped runtime behaviorとobserver contract

Row 3はinfra内のresponsibility splitです。Row 12はcommands/application/domainのdependency directionです。Rows 4–11はapplication portへ対するtest doubleのfidelityです。

### 3.3 Lifecycle boundary

Issue #395はProvider Lifecycle Wireのread-only consumerです。Lifecycle state、wire field、public code、serialization、migration、uninstall、recovery、coordinationを変更しません。Dogfood projectionはexisting lifecycle behaviorの利用であり、lifecycle設計変更ではありません。

### 3.4 Human authority boundary

LunaMaxはIssue branch candidateの作成と許可された場合のcommit/push・PR preparationまでを扱えます。Integration branchへのmerge、revert、Issue closure、#396 start、main merge、branch protection、required-context変更はhuman/Codex authorityです。

## 4. Write, generated, read-only surfaces

### 4.1 Hand-edited candidate surfaces

| Purpose             | Path                                                                        | Symbol / responsibility                                                                                                |
| ------------------- | --------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Row 3 Product       | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py` | `_parse_github_repo_slug`、`origin_github_repo_slug`、`origin_github_publication_endpoint`のexisting responsibility split |
| Row 1 observer      | `tests/cli_runtime/test_delete.py`                                          | Exact row 1 test methodのactive observation                                                                             |
| Row 3 observer      | `tests/cli_runtime/test_import.py`                                          | Exact row 3 test methodのcredential non-exposure observation                                                            |
| Rows 4–11 fixture   | `tests/cli_runtime/test_runtime_import_s10.py`                              | `_StubTemplateScaffolder`のcurrent port fidelity                                                                        |
| Rows 13–14 observer | `tests/cli_runtime/test_sync.py`                                            | Exact row 13・14 test methodsのactive observation                                                                        |
| Row 15 observer     | `tests/cli_runtime/test_workbench.py`                                       | Exact row 15 test methodのactive operation ordering                                                                     |
| Final ledger        | `full-regression-ledger.json`                                               | All behavior GREEN後の14-row lifecycle transition                                                                        |

### 4.2 Generated candidate surfaces

| Path                                                                     | Generation rule                                   |
| ------------------------------------------------------------------------ | ------------------------------------------------- |
| `spec-dock/scripts/spec_dock_runtime/infra/git_cli.py`                   | Provider sourceからcurrent lifecycle updateで投影する    |
| `spec-dock/spec-dock.version`                                            | Ready recordとしてcurrent lifecycle updateが生成する      |
| `.agents/skills/spec-dock/.spec-dock-provider-slot.json`                 | Fixed slot markerとしてcurrent lifecycle updateが生成する |
| `.agents/skills/spec-dock-grill-with-docs/.spec-dock-provider-slot.json` | Fixed slot markerとしてcurrent lifecycle updateが生成する |

Final tracked implementation diffのexpected setは上記11 pathsです。Expected generated pathが変化しない、またはextra pathが変化する場合は手編集で帳尻を合わせず、projection contract driftとして停止します。

### 4.3 Read-only verification surfaces

* `src/.../application/import_node.py`
* `src/.../application/repo_context.py`
* `src/.../application/ports.py`
* `src/.../cli/bootstrap.py`
* `src/.../application/create_node.py`
* `src/.../infra/template_scaffolder.py`
* `src/.../commands/new.py`
* `src/.../application/contracts.py`
* `src/.../domain/artifacts.py`
* `tests/cli_runtime/test_runtime_shell_s11.py`
* `scripts/quality/full_regression_baseline.py`
* `scripts/quality/verify_full_regression.py`
* `tests/unit/test_full_regression_baseline.py`
* `tests/conftest.py`
* `full-regression-timing-weights.json`
* Provider CIとProvider Full Regression workflows
* Issue #392 lifecycle sourceとwire-owned assets

これらにsemantic changeが必要ならIssue #395のboundaryを越えるため停止します。

## 5. Baseline state model

### 5.1 Entry state

* Ledger total: 15
* Active: rows 1、3–15の14件
* Resolved: row 2の1件
* Row 2 mode: `superseded`
* Timing: 243
* Required-fast: 4
* Allowed P392 verifier violations: rows 4–12、15だけ
* Rows 1、3、13、14: active historical signatureを観測
* Row 12 node: normal passだがactive ledgerに対してcoverage mismatch

### 5.2 Candidate state transitions

| State                   | Meaning                                         | Entry condition                                         | Exit condition                            |
| ----------------------- | ----------------------------------------------- | ------------------------------------------------------- | ----------------------------------------- |
| S0 Specification-only   | 現在の状態。Mutation禁止                                | `implementation_allowed=false`                          | Independent spec reviewとexplicit dispatch |
| S1 Authorized TDD       | Product/test mutation可能                         | Exact identity、review pass、authorization、writer absence | Repair-unit GREEN                         |
| S2 Behavior repaired    | 14 historical nodesとrow 2 successorがnormal pass | Four repair units完了                                     | Dogfood projection GREEN                  |
| S3 Candidate projected  | Provider sourceとdogfoodが一candidate              | Digest/protected-data/lifecycle proof                   | Ledger transition                         |
| S4 Ledger terminalized  | 15/0/15、14 fixed-in-place、1 superseded          | S2・S3 GREEN                                             | Complete verifier/gates                   |
| S5 Exact clean reviewed | One clean pushed SHA/treeへ全証拠を再束縛               | All gates + independent reviews                         | Human PR merge                            |
| S6 Human merged         | Integration tip固定                               | Human merge                                             | Same-tip B1                               |
| S7 B1                   | Current gates GREEN                             | S6 exact tip                                            | Same-tip B2                               |
| S8 B2                   | 15/0/15 terminal state                          | Same exact S7 tip                                       | Human closure decision / #396 eligibility |

Ledger transitionはS2とS3より前に起こせません。Human mergeはS5より前に起こせません。#396はS8より前に開始できません。

## 6. Test lane contract

* Ordinary laneはcurrent policy skipを保持するfast laneです。
* `tests/cli_runtime/`または`tests/integration/`のpath/nodeを直接選ぶ場合は、full-regression execution permissionとshard modeを明示します。
* Selected heavy testは、collected exactly once、executed exactly once、outcome passedであることを証拠にします。
* Exit 0でもskip、xfail、xpass、未実行ならGREENではありません。
* Full verifierはdedicated empty artifact rootを使い、one resultだけを採用します。
* Working-tree verifier resultはuncommitted bytesをSHAへ表現できないため、binary diff digest付きprovisional evidenceとして扱います。
* Merge-ready evidenceはclean pushed exact SHA/treeで再実行します。

## 7. Repair unit contracts

### 7.1 Rows 4–11 — Descriptor-bound test double

**Boundary:** production portとproduction adapterはread-only、test doubleだけを修正します。

**Responsibility:** `_StubTemplateScaffolder.copy_scaffolded_tree_at`がcurrent `TemplateScaffolder` protocolのdescriptor-bound call shapeを受け、production infra behaviorへ委譲できるようにします。

**Invariants:**

* Held destination descriptorを失わない
* Second pathname writerを作らない
* Production `execute_create_plan`を変更しない
* Old copy APIへproductionを戻さない
* Existing event、parent resolution、active manifest、repo identity、artifact、negative sync、exactly-once writer assertionsを保持する

**Testable contract:** rows 4–11がそれぞれnormal passし、failure layerがmissing current portから消えることです。

### 7.2 Rows 1、13、14、15 — Selection-only observers

**Boundary:** Product active commandはread-only、test observerだけを修正します。

**Responsibility:** Retired flagsを除去し、current positional/`--id`/`--github-issue` surfaceで同じbehaviorを観測します。

| Row | Current obsolete observation           | Accepted observation        |
| --: | -------------------------------------- | --------------------------- |
|   1 | `active set --id iss-00058 --force`    | `active set --id iss-00058` |
|  13 | `active set iss-00003 --force`         | `active set iss-00003`      |
|  14 | `active set 305 --force --no-checkout` | `active set 305`            |
|  15 | `active set --id scope_id --force`     | `active set --id scope_id`  |

**Invariants:**

* Row 1のdeleted metadata非再観測
* Row 13のnew/active/sync convergence
* Row 14のtree、PUML、ready-board content
* Row 15のREADME/payload byte opacity、active fields、index、validate/sync/deps observation
* Row 15はactive command successをstate readより先に確認する

**Testable contract:** four nodesが個別にnormal passし、Productにretired flagを復活させないことです。

### 7.3 Row 3 — Identity / publication separation

**Read-only identity responsibility:** fetch originからGitHub owner/repo identityを返します。Credential-bearing HTTPS originはidentity解析の入力として許容しますが、credential自体を返しません。

**Publication responsibility:** fetchとpushの両endpointを読み、userinfoをどちらでも拒否し、両slugのexact一致を要求し、accepted push URLだけを返します。

**Invariants:**

* Existing functionとport signaturesを維持する
* Same-repository validationを維持する
* Numeric targetのcurrent-scope requirementを維持する
* Foreign URL rejectionを維持する
* Raw credentialを出力しない
* Publication strictnessを弱めない

**Testable matrix:**

| Case                                  | Read-only identity | Publication     | Secret exposure |
| ------------------------------------- | ------------------ | --------------- | --------------- |
| Credential-bearing fetch              | success            | reject          | 0               |
| Clean fetch + credential-bearing push | success            | reject          | 0               |
| Clean fetch + foreign clean push      | success            | reject mismatch | 0               |
| Clean matching fetch/push             | success            | success         | 0               |

### 7.4 Row 12 — No-edit thin-shell guard

Accepted dependency directionは`commands/new.py`から`application/contracts.py`を経由し、`domain/artifacts.py`のsingle catalogueへ到達する形です。

**Invariants:**

* Row 12 Product/test blobsはverified inputから変更しない
* Commands layerからdomain/infraへのdirect importを追加しない
* Catalogueを複製しない
* Old typeを復活させない
* Structural test assertionsを保持する

**Testable contract:** nodeはentryからnormal passし、ledger evaluatorだけがactive coverage mismatchを報告します。SourceまたはAST boundaryがdriftしている場合は修復せず停止します。

## 8. Dogfood projection design

### 8.1 Preconditions

* Provider sourceのfocused behaviorがGREEN
* Row 3 security matrixがGREEN
* Ledgerはまだentry state
* Protected-data snapshotが取得済み

### 8.2 Projection responsibility

Current lifecycle updateを一回のcomplete candidate projectionとして使用します。Generated mirror、record、markersを手編集しません。

### 8.3 Postconditions

* Provider sourceとdogfood runtime mirrorがbyte-equal
* Old digestとnew digestが異なる
* Update result、record、two markersがnew digestで一致
* Recordはversion `0.2.4`、state `ready`、operation `null`、seed policy `preserve-only`
* Fixed slot namesを保持
* Two skill `SKILL.md` bytesを保持
* Four provider rootsとconsumer-owned dataを保持
* Dogfood/package parity nodeがnormal pass

## 9. Ledger transition design

Ledgerはbehavior truthを記録するconsumerであり、修復そのものではありません。

Transition直前に、saved entry payloadとcurrent payloadのbyte-semantic equalityを確認します。Rows 1、3–15へ許可するsemantic deltaは`lifecycle=resolved`と`resolution_mode=fixed-in-place`だけです。Row 2とtop-level historical payloadは完全一致させます。

Transition後のtargetは15 total / 0 active / 15 resolved / 14 fixed-in-place / 1 supersededです。Verifier GREENだけではhistorical preservation proofを代替できません。

## 10. Authorization and concurrency

Read-only preflightはS0で実行できます。File mutation、dogfood update、ledger update、stage、commit、push、PR operationはS1以前に実行できません。

Mutation gateは次を要求します。

* Exact specification SHA/tree
* Review targetが同じSHA/tree
* Independent review pass、P0=0、P1=0
* `implementation_authorized=true`
* Non-empty identityとscopeを持つconcurrent-writer absence
* Clean worktreeとunchanged HEAD
* `human_merge_only=true`

Commit/pushとPR preparationはmutation authorizationから独立したpermissionです。

## 11. Evidence model

### 11.1 Per-row evidence

各rowは、ordinal、nodeid、historical signature、first RED layer、changed path/symbol、protected assertions、GREEN outcome、ledger before/afterを持ちます。

Row 12は、entry evaluator coverage mismatchとindependent node passを別々に記録します。

### 11.2 Candidate evidence

Working-tree evidenceはHEAD、complete binary diff SHA-256、provisional verifier resultを束縛し、`merge_ready=false`とします。

Exact clean evidenceはimplementation SHA/tree、exact changed paths、full verifier、all gates、manual invariants、independent reviewsを同じidentityへ束縛します。

### 11.3 Secret handling

Raw credential、userinfo-bearing URL、private absolute path、secret-bearing raw logをdistributed evidenceへ含めません。Raw local evidenceとsanitized distribution evidenceを分離します。

## 12. Stop and recovery design

次の場合は新しい設計を選ばず停止します。

* Repository、branch、SHA/tree、upstream、remote、ancestry不一致
* Review/authorization/writer assertion不備
* Baseline row、signature、order、row 2、timing、required-fast drift
* Entry verifierに許容外violation
* First REDがexpected layerと異なる
* Heavy nodeがskip/xfail/error
* Row 3 security contractを両立できない
* Row 12 boundary drift
* Dogfood projectionがlifecycle、version、protected dataを変える
* Ledgerの許容差分を越える
* Policy、workflow、timing、wire、#396 scopeの変更が必要
* Unexpected failureまたはnew owner decision

Human merge前はcandidate全体を修正または破棄します。Human merge後かつ#396前はhumanがwhole-merge revertまたはowned forward-fixを選びます。Partial rollbackとautomatic rollbackは禁止します。

## 13. Requirement traceability

| Requirement | Design section |
| ----------- | -------------- |
| I395-RQ-001 | §§3、5、10       |
| I395-RQ-002 | §§4、7          |
| I395-RQ-003 | §7.3           |
| I395-RQ-004 | §7.1           |
| I395-RQ-005 | §7.2           |
| I395-RQ-006 | §7.4           |
| I395-RQ-007 | §8             |
| I395-RQ-008 | §9             |
| I395-RQ-009 | §§6、7、9        |
| I395-RQ-010 | §§3.3、4.3、12   |
| I395-RQ-011 | §5.2           |
| I395-RQ-012 | §§2、10         |
| I395-RQ-013 | §11            |
| I395-RQ-014 | §12            |

## 14. Decision state

New Product、security、lifecycle、policy decisionは不要です。`owner_decisions_required=[]`、`implementation_allowed=false`、`human_merge_only=true`を維持します。
