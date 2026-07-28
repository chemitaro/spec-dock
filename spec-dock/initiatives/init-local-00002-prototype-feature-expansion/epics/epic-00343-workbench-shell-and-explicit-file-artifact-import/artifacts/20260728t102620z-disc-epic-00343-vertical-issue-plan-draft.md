---
created_by_role: implementation-planner
scope_id: epic-00343
source_paths:
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/report.md
  - spec-dock/active/epic/artifacts/20260728t100038z-adr-generic-imported-file-identity-and-privacy-boundary.md
  - spec-dock/active/initiative/requirement.md
  - spec-dock/active/initiative/design.md
  - spec-dock/active/initiative/plan.md
  - spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00312-experimental-local-workbench-and-worktree-handoff/artifacts/20260728t080013z-research-chatgpt-pro-epic-replanning-zip-evidence.md
  - src/spec_dock/cli.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_artifact.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/artifacts.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/binary_artifact_publisher.py
  - tests/unit/infra/test_init_update.py
  - tests/unit/infra/test_binary_artifact_publisher.py
  - tests/cli_runtime/test_artifact_import_chatgpt_output.py
  - tests/cli_runtime/test_workbench.py
intended_targets:
  - spec-dock/active/epic/plan.md
  - spec-dock/active/epic/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: passed
fallback_decision: not_applicable_delegated_authoring_available
report_evidence_destination: spec-dock/active/epic/report.md
adoption_ledger_note: Main orchestrator must disposition this evidence before canonical plan adoption.
source_snapshot:
  head: 7e867893c1d2fda48db7efee9aac7d69433046ac
  requirement_sha256: 068eda6ba36aadc93884ca8791a40c4f31998bcb47050014f07d0e623391e20c
  design_sha256: 8966f5e035c6427e48e193d336646b8d0152a31bfd89e21691cf7acdacd1dcd9
  accepted_adr_sha256: 9e22b35727f410e06b994cf5fc7631a1b2025f4e962b6168ec82e999171434bb
  design_review: ninth fresh spec-reviewer pass, confidence 0.96
---

# Epic 00343 Vertical Issue Plan Draft

## 1. Plan Summary

### 計画の目的

`epic-00343`を、利用者が観測できる価値を各Issue内で端から端まで閉じる、必要最小限の3 Issueへ分割する。

1. **Workbench Shell Scaffolding**
   - fresh repositoryと今後作成するInitiative / Epic / Issueで、Git追跡可能なshell markerを持つoptional Workbenchを直ちに利用可能にする。
2. **Generic Single-File Artifact Import**
   - Workbench内外、repository内外の明示single file一件を、root / Initiative / Epic / IssueのArtifactへ安全にimportできるCLI capabilityを提供する。
3. **Integration Distribution And Final Quality**
   - 上記二能力をcandidate wheel、fresh / updated consumer、dogfood、full regression、Epic-wide review、mergeable PR deliveryまで統合する。

この3分割より細かいlayer別Issueは作らない。Candidate 1と2はそれぞれCLI / application / domain / infra / tests / docsの必要部分を含むvertical sliceとし、Candidate 3は単なるreview-only Issueではなく、利用者へ配布可能な統合状態と最終送達を所有する必須のfinal quality Issueとする。

### Epic classification

- classification: `multi-issue implementation`
- final quality Issue: `required`
- Issue candidate count: `exactly 3`
- Issue node status: `not_created_pending_human_approval`
- canonical Issue docs status: `not_created_pending_human_approval`
- PR strategy:
  - Candidate 1 / 2はreview済みのlocal milestone commitまで閉じ、per-Issue PRを作成しない。
  - Candidate 3がCandidate 1 / 2へ依存し、Epic全差分のquality gate、push、PR Delivery Gate、Merge Preparation Gateを所有する。
  - mergeはhuman-only boundaryとし、本計画の完了条件はmergeable PR preparationまでとする。

### Scope

- fresh-init-only root `.workbench/.gitkeep`。
- future Initiative / Epic / Issue `.workbench/.gitkeep`。
- markerを追跡可能にし、Workbenchのその他contentsを無制限の深さでignoreするcontract。
- optional presence、no-backfill、semantic opacity、worktree-local / disposable contract。
- existing manual one-shot `workbench copy`互換。
- `artifact import file --file <path>`とexactly one root / node selector。
- repository内外のreadable regular leaf file、ancestor symlink許容、leaf symlink拒否。
- byte identity、source survival、minimal basename normalization、global slot uniqueness、no-overwrite、FD-bound publication、privacy-safe output。
- binary / archive / invalid UTF-8のopaque lifecycle。
- provider/package/installed consumer/dogfood/docs/test parity。

### Non-scope

- existing root / nodeへのWorkbench backfill。
- Workbench presenceのvalidity要件化。
- Workbench contentのGit tracking、automatic copy、watch、sync、copy-back。
- directory / glob / bulk / recursive import。
- source parse、MIME分類、format変換、archive展開。
- typed `file` token、title / slug要求、persistent provenance catalog。
- source delete / move / overwrite。
- importによるcanonical docs、ADR、report、assuranceの自動変更。
- unrelated architecture cleanup、dependency subsystem再設計、rootのgraph node化。
- Issue nodeの事前作成、pre-start canonical Issue `design.md` / `plan.md`の本文化。

## 2. Requirement / Design Traceability

### Requirement ownership matrix

`primary`は当該contractを実装してfocused evidenceを作る所有者、`integration`は他Issueの成果を変更せず統合環境で再検証する所有者を表す。

| Requirement | Candidate 1 | Candidate 2 | Candidate 3 |
|---|---|---|---|
| E-RQ-001〜007 Workbench shell / optional / no-backfill / opacity / manual copy | primary | compatibility observer | integration |
| E-RQ-008〜012 command / target / source location / eligibility / authorization | — | primary | integration |
| E-RQ-013〜018 bytes / naming / collision / publication / privacy | — | primary | integration |
| E-RQ-019〜020 authority isolation / opaque lifecycle | opacity compatibility | primary | integration |
| E-RQ-021 `chatgpt-output` compatibility | regression observer | primary compatibility | final regression |
| E-RQ-022 existing Artifact compatibility | — | primary compatibility | final regression |
| E-RQ-023 `workbench copy` compatibility | primary compatibility | — | final regression |
| E-RQ-024 provider / consumer parity | focused shell evidence | focused import evidence | primary final distribution |
| E-RQ-025 documentation | shell/copy docs | import/naming/privacy docs | integrated parity and omissions |

### Acceptance ownership matrix

| Acceptance criteria | Primary closure owner | Final verification owner |
|---|---|---|
| E-AC-001〜007 Workbench matrix | Candidate 1 | Candidate 3 |
| E-AC-008〜016 import target/source/file/naming/publication/privacy matrix | Candidate 2 | Candidate 3 |
| E-AC-017 opaque lifecycle compatibility | Candidate 2 | Candidate 3 |
| E-AC-018 existing command compatibility | Candidate 1: `workbench copy`; Candidate 2: `chatgpt-output` / `new artifact` | Candidate 3 |
| E-AC-019 distribution | Candidate 3 | Candidate 3 |
| E-AC-020 final closure | Candidate 3 | Candidate 3 |

### Design / ADR trace

| Design / decision | Issue ownership |
|---|---|
| D-001 fresh-only shell generation | Candidate 1 |
| D-002 tracked marker / ignored contents | Candidate 1 |
| D-003 additive generic import use case | Candidate 2 |
| D-004 root outside node graph | Candidate 2 |
| D-005 explicit source guard / publication reuse | Candidate 2 |
| D-006 generic filename family / shared slot ledger | Candidate 2 |
| D-007 minimal basename normalization | Candidate 2 |
| D-008 publication state / privacy result | Candidate 2 |
| D-009 opaque lifecycle | Candidate 2、Candidate 3でinstalled/dogfood再検証 |
| accepted ADR `20260728t100038z-adr` | Candidate 2のimplementation contract、Candidate 3のnon-regression gate |

Candidate 2 / 3はaccepted ADRを再判断しない。`--` family、full destination basename identity、external basename-only visibility、content-derived metadata非公開、FD-bound commit point、`committed_with_warning`のretry不要contractを変更する必要が出た場合は、Issue内で仮定せずEpic design / ADR amendmentへ戻す。

## 3. Milestones

### M0 Canonical plan / human slice gate

- deliverable:
  - main orchestratorが本draftを採否し、canonical `plan.md`へ再記述する。
  - fresh `spec-reviewer`がcanonical planをrequirement / design / ADRと照合する。
  - ユーザーがexactly 3 slicesとIssue作成を承認する。
- exit:
  - canonical plan reviewer `pass`。
  - human approval。
  - それまではIssue nodeを作成しない。
- annotation: `HITL`

### M1 Workbench shell capability

- owner: Candidate 1。
- deliverable:
  - fresh root / future node shell、ignore、no-backfill、opacity、manual-copy互換をprovider-firstで実装し、focused source / packaged-asset evidenceを閉じる。
- exit:
  - E-AC-001〜007とCandidate 1担当分のE-AC-018 / 019 evidence。
  - required per-step review、docs alignment、milestone commit、clean check。
- annotation: `AFK between required review gates`

### M2 Generic explicit-file import capability

- owner: Candidate 2。
- deliverable:
  - CLIからprivacy-safe outputまでのgeneric single-file importを、root / node、internal / external source、binary / invalid UTF-8、fault laneを含めて閉じる。
- exit:
  - E-AC-008〜018のfocused evidence。
  - accepted ADR non-regression。
  - required per-step review、docs alignment、milestone commit、clean check。
- annotation: `AFK between required review gates`

### M3 Integrated distribution and mergeable delivery

- owner: Candidate 3。
- deliverable:
  - Candidate 1 / 2の成果をcandidate wheel、fresh / updated consumer、dogfood、manual scenario、full regression、Epic-wide review、PRへ統合する。
- exit:
  - E-AC-019〜020、全E-RQ / E-ACのreport trace、blocking findingなし。
  - final QA / code / spec review pass。
  - Epic-wide pre-PR review、push、PR Delivery Gate、Merge Preparation Gate pass。
  - mergeable PR prepared。mergeは行わない。
- annotation: `AFK until PR gate; HITL for merge`

## 4. Dependency-Derived Execution Order

### Logical dependency graph

```text
Candidate 1 Workbench Shell ─────┐
                                 ├─> Candidate 3 Integration / Distribution / Final Quality
Candidate 2 Generic Import ──────┘
```

- Candidate 1と2のproduct dependencyはない。
- Candidate 3はCandidate 1と2の両方へdirect dependencyを持つ。
- Candidate 1と2は理論上parallelizableだが、同一Epic branch / worktree、`pyproject.toml`、provider docs、Artifact regression surfaceの衝突を避けるため、Epic executionは原則Candidate 1 → Candidate 2 → Candidate 3の順で1 Issueずつ進める。
- 実際のIssue ID採番後だけ、metadata直編集ではなく次を実行する。

```bash
./spec-dock/scripts/spec-dock deps add --from <candidate-3-issue-id> --to <candidate-1-issue-id>
./spec-dock/scripts/spec-dock deps add --from <candidate-3-issue-id> --to <candidate-2-issue-id>
./spec-dock/scripts/spec-dock deps check <candidate-3-issue-id>
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync
```

### Tranches

- Tranche A:
  - Candidate 1、Candidate 2。
  - logical parallelismは許容するが、current execution policyはserial。
- Tranche B:
  - Candidate 3。
  - Tranche A両Issueのlocal completion、review、commit、deferred PR delivery evidenceをentry条件とする。

## 5. Issue / Step Slicing

### Candidate 1: Workbench Shell Scaffolding

- candidate key: `candidate-epic-00343-01-workbench-shell`
- title: `Workbench Shell Scaffolding`
- recommended grade: `standard`
- user-visible value:
  - fresh init直後とfuture node作成直後にWorkbench shellが存在し、markerだけをtrackingしつつscratch contentsをGitへ出さず利用できる。
- in scope:
  - `src/spec_dock/cli.py`のfresh root判定とfallback ignore。
  - provider `.gitignore`。
  - Initiative / Epic / Issue templatesの`.workbench/.gitkeep`。
  - hidden marker package-data。
  - new-node planned/result/filesystem path parity。
  - optional/no-backfill/opacity/manual-only copy compatibility。
  - shell / manual copy public docs。
- vertical deliverables:
  - installer → provider assets/templates → runtime node creation → Git observation → focused tests → docs。
  - source treeとcandidate package inventoryでhidden markerを観測できること。
- verification seeds:
  - fresh init root markerと`git add -n`。
  - future 3 node kindsのplanned/result/filesystem一致。
  - root + 3 node kindsのnested ignore / near-name matrix。
  - existing init/update/sync/validate/active/artifact/ADR mutationのno-backfill matrix。
  - missing/manual Workbench validity、fake metadata / binary / broken subtree opacity。
  - linked worktree creationでは自動copyなし、明示`workbench copy`のみcurrent behavior。
  - focused commands:

```bash
uv run pytest tests/unit/infra/test_init_update.py
uv run pytest tests/unit/infra/test_runtime_fs_repo_workbench_opacity.py
uv run pytest tests/cli_runtime/test_runtime_new_doc_s09.py tests/cli_runtime/test_workbench.py
```

- rollback:
  - provider template / ignore / installer deltaをIssue commit単位でrevertする。
  - user Workbench contentsや既に作成されたmarkerを自動削除しない。
  - rollback時は旧`.workbench/` ignore ruleを先に復元してscratch露出を防ぐ。
- handoff seed:
  - parent trace: E-RQ-001〜007、023〜025; E-AC-001〜007、018〜019; D-001〜002。
  - allowed local delta: exact fixture / symbol placement、package inventory assertion。
  - forbidden boundary: backfill、required Workbench、automatic copy/sync、Workbench content tracking。
  - expected evidence: changed files、focused tests、package inventory、docs/spec review、deferred PR delivery gate。

### Candidate 2: Generic Single-File Artifact Import

- candidate key: `candidate-epic-00343-02-generic-file-import`
- title: `Generic Single-File Artifact Import`
- recommended grade: `critical`
- user-visible value:
  - `artifact import file --file <path>`で、明示single fileをroot / Initiative / Epic / Issueへ、bytesとsourceを保持したままprivacy-safeに保存できる。
- in scope:
  - additive CLI / request / result / error / use case / bootstrap。
  - explicit root / node target resolverとroot Artifact setup。
  - explicit source guard、ancestor symlink、leaf symlink拒否。
  - stream staging、source revalidation、FD-bound no-replace publication、capability probe。
  - generic `--` filename parser、minimal normalizer、all-family shared slot ledger。
  - content-free success/error/warning text / JSON。
  - bodyを読まないvalidate / sync / ADR mirror / deps / context。
  - existing `chatgpt-output` / `new artifact`互換。
  - import / naming / privacy / authority public docs。
- vertical deliverables:
  - CLI → application target/allocation → domain naming → infra publication → presentation → lifecycle consumers → focused tests → docs。
- verification seeds:
  - root / 3 node target、zero/multiple selector。
  - root/scoped Workbench、repo内non-Workbench、external absolute / relative、nested cwd。
  - regular、ancestor symlink、missing、directory、leaf symlink、FIFO/socket/device、unreadable、source mutation。
  - Markdown / uppercase extension / PDF / image / ZIP / multi-suffix / no-extension / empty / invalid UTF-8 / NUL / large stream。
  - basename preservation、path safety、Unicode/space/case、NAME_MAX。
  - typed / blank / generic shared slot、concurrency、01..99 exhaustion、no-overwrite。
  - precommit failure、postcommit warning、retry disposition、external sentinel非漏洩。
  - body-open spyを用いたvalidate / sync / deps / context / ADR mirror isolation。
  - focused commands:

```bash
uv run pytest tests/unit/domain/test_artifacts.py
uv run pytest tests/unit/application/test_import_file_artifact.py tests/unit/commands/test_artifact_import_file.py
uv run pytest tests/unit/infra/test_binary_artifact_publisher.py
uv run pytest tests/unit/presentation/test_artifact_import_file.py
uv run pytest tests/cli_runtime/test_artifact_import_file.py
uv run pytest tests/cli_runtime/test_artifact_import_chatgpt_output.py tests/cli_runtime/test_artifact_import_s04.py
```

- rollback:
  - command / use case / generic parser / explicit publisher pathをIssue commit単位でrevertする。
  - import済みArtifactはuser evidenceとして保持し、削除・renameしない。
  - existing typed / blank / `chatgpt-output` dataをmigrationしない。
- handoff seed:
  - parent trace: E-RQ-008〜025; E-AC-008〜019; D-003〜009; accepted ADR。
  - allowed local delta: exact error class、test fixture、supported filesystem probeの実装詳細。
  - forbidden boundary: typed `file` token、content classification、external absolute path漏洩、source mutation、fallback overwrite、mutable-path commit。
  - expected evidence: state/privacy snapshots、fault injection、byte/hash internal assertions、opaque lifecycle spy、docs/spec review、deferred PR delivery gate。
- escalation triggers:
  - accepted ADRのpublic identity/privacy/retry contract変更。
  - supported platform guaranteeの縮小。
  - requirement threat-model境界外の新しいdata-loss / overwrite risk。
  - 上記はIssue-local判断で吸収せずEpic design / ADR amendmentへ戻す。

### Candidate 3: Integration Distribution And Final Quality

- candidate key: `candidate-epic-00343-03-final-quality`
- title: `Integration Distribution And Final Quality`
- recommended grade: `strict`
- user-visible value:
  - shellとgeneric importを、source checkoutだけでなく配布wheel、fresh / existing consumer、dogfoodで一貫して利用でき、blocking findingのないmergeable PRとして受け取れる。
- depends on:
  - Candidate 1。
  - Candidate 2。
- in scope:
  - Candidate 1 / 2のcross-feature integration repair。
  - wheel inventory / candidate wheel。
  - fresh consumer、pre-feature existing consumer update/no-backfill、post-update future node。
  - dogfood provider-first projection。
  - manual external-file root/node scenario。
  - full regression、docs parity、Epic report trace。
  - final QA / code / spec review、Epic-wide pre-PR review、push、PR preparation。
- vertical deliverables:
  - provider source → built distribution → installed consumer → updated consumer → dogfood → full quality evidence → mergeable PR。
- verification seeds:

```bash
uv build
uv run pytest
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync --no-github
```

  - candidate wheelをtemp Git repositoryへinstallし、fresh root/future node shellとroot/node generic importを通常権限で実測する。
  - markerなしpre-feature consumerをupdateし、existing root/nodeへbackfillせず、その後作成するnew nodeだけmarkerを得る。
  - external sourceはdestinationと別filesystemでも成功し、external path/body/hash/count sentinelがoutput/provenanceへ漏れない。
  - unsupported filesystem capabilityはformal destination前にfail closedとなる。
  - dogfood更新後もexisting `epic-00343`へmarkerをbackfillせず、validate/sync/deps/contextがpassする。
- repair boundary:
  - integration failureの最小修正は許可する。
  - major feature未実装をCandidate 3へ先送りしない。
  - parent requirement / design / ADR変更が必要ならEpic planning repairへ戻す。
- rollback:
  - integrated provider deltaをreviewable commit単位でrevertする。
  - generic Artifact / Workbench user contentは削除しない。
  - ignore rollbackはscratch露出防止順序を守る。
- final delivery:
  - `qa-reviewer`、issue-wide `code-reviewer`、`spec-reviewer`をfresh passまで回す。
  - Epic base/head endpointと全差分証跡を固定し、fresh Epic-wide decision reviewとfresh `spec-reviewer`を同じevidenceへ通す。
  - findingsを`fixed` / `superseded` / `explicitly_deferred_with_user_acceptance`へdispositionする。
  - final commit、push、PR Delivery Gate、Merge Preparation Gateを閉じる。
  - human merge前で停止する。

### Issue-local draft path index

Issue nodesはまだ作成しないため、存在しないpathやIDを捏造しない。

| Candidate | Issue node | draft-requirement | draft-design | draft-plan |
|---|---|---|---|---|
| Candidate 1 | `not_created_pending_human_approval` | `not_created_pending_human_approval` | `not_created_pending_human_approval` | `not_created_pending_human_approval` |
| Candidate 2 | `not_created_pending_human_approval` | `not_created_pending_human_approval` | `not_created_pending_human_approval` | `not_created_pending_human_approval` |
| Candidate 3 | `not_created_pending_human_approval` | `not_created_pending_human_approval` | `not_created_pending_human_approval` | `not_created_pending_human_approval` |

人間承認後はruntime-owned `new issue`で3 nodeを作成し、採番後のIDをcanonical plan / reportへ記録する。各Issueのdraft requirement / `draft-design` / `draft-plan`はIssue-local runtime commandで作成し、Issue planningがcurrent repository stateとprior completed Issuesを反映してjust-in-timeにcanonical化する。

## 6. Test Strategy Mapping

| Canonical design test lane | Candidate | Evidence level |
|---|---|---|
| T1 Workbench shell | Candidate 1 | unit + installer + CLI runtime + real Git observation |
| T2 Domain / allocation | Candidate 2 | pure unit + concurrency / exhaustion |
| T3 Source / publication | Candidate 2 | infra unit + fault injection + supported/unsupported capability |
| T4 Privacy / state | Candidate 2 | presentation snapshot + CLI runtime + secret sentinel |
| T5 Opaque lifecycle / compatibility | Candidate 2 | validate/sync/deps/context spy + focused compatibility |
| T6 Distribution / dogfood | Candidate 3 | candidate wheel + fresh/update consumer + dogfood + full regression |

Cross-Issue rule:

- Candidate 1 / 2は各vertical capabilityのRedまたはcharacterization、Green、focused compatibilityを自Issueで閉じる。
- Candidate 3は同じcontractをdistribution/dogfoodで再検証するが、Candidate 1 / 2の未完了test obligationを肩代わりしない。
- concrete test case cards、Spec-Locked Closure Index、delegation contractは各Issue planningで作成し、Epic planではfixture実装詳細を固定しない。

## 7. Review Gates

### G0 Epic plan adoption gate

- main orchestratorによるEAL disposition。
- canonical `plan.md`への再記述。
- fresh `spec-reviewer` pass。
- humanによる3-slice / Issue creation承認。
- G0完了前のIssue作成は禁止。

### G1 Issue planning gate

- Issueを1つずつactiveにし、ChatGPT-first Issue planningをjust-in-timeで行う。
- current repo、prior completed Issues、dependency state、Epic report ledgerを再確認する。
- Issue-local requirement → design → planを各fresh `spec-reviewer` passでpromoteする。
- `handoff-ready`と`execution-ready`を分離し、draft-only状態で実装しない。

### G2 Per-Issue implementation / review gate

- implementation stepごとにdelegation contract、step-local verification、reviewer focusを固定する。
- runtime / CLI / infra / tests / scaffold behaviorは`dev-coder`へ委任する。
- shipped docsは`doc-writer`へ委任する。
- code/runtime/testを含むstepはfresh `code-reviewer` pass。
- docs-only stepはfresh `spec-reviewer` docs/spec alignment pass。
- `standard` / `strict` / `critical` milestoneはcommit candidateとpost-commit clean checkを持つ。

### G3 Intermediate deferred PR delivery gate

- Candidate 1 / 2はCandidate 3へのdependency edgeとdefer先実IDをreportへ記録する。
- per-Issue PRを作らない理由、final PRまでmerge-preparedを主張しないこと、Candidate 3のPR Delivery / Merge Preparation Gateが残ることを明記する。
- local completion、review、commit、issue finish条件は省略しない。

### G4 Final quality / PR gate

- Candidate 3はdeferred PR deliveryを使用しない。
- S90 docs impact resolution後にS99 final quality gateを独立実行する。
- fresh `qa-reviewer`、issue-wide `code-reviewer`、`spec-reviewer`をpassまで回す。
- Epic-wide base/head evidenceをfresh decision reviewとfresh `spec-reviewer`へ渡す。
- PR Delivery Gate / Merge Preparation Gateを通し、人間merge前で停止する。

## 8. Rollback / Compatibility

### Compatibility invariants

- existing `artifact import chatgpt-output`のWorkbench-only lowercase `.md`、title/slug、blank identity、hash/count resultを維持する。
- existing `new artifact`のtyped / blank grammarとcatalogを維持する。
- existing `workbench copy`のexplicit one-shot、source-wins、destination-only preserve、symlink-object behaviorを維持する。
- existing root / nodeのmarker有無、Workbench bytes/names/mtimesをupdate/sync/validateで変更しない。
- rootをdependency/status/active graphへ追加しない。

### Rollback order

1. PR未mergeなら、Issue単位のreviewable commitをrevertする。
2. Workbench ignore変更を戻す場合はscratch contentsが`git status`へ露出しないruleを先に復元する。
3. runtime/template/package deltaを戻す。
4. imported generic Artifact、existing marker、Workbench user contentは削除・renameしない。
5. rollback後にfocused compatibility、validate、syncを再実行する。

## 9. Docs Impact

### Candidate 1

- `src/spec_dock/assets/spec_dock/docs/README.md`
- `src/spec_dock/assets/spec_dock/docs/guide.md`
- `src/spec_dock/assets/spec_dock/docs/reference_worktree.md`
- shell auto-generation、optional/no-backfill、ignored/disposable、manual-only copyを説明する。

### Candidate 2

- `src/spec_dock/assets/spec_dock/docs/README.md`
- `src/spec_dock/assets/spec_dock/docs/guide.md`
- `src/spec_dock/assets/spec_dock/docs/reference_naming.md`
- root / node target、source policy、generic `--` family、privacy-safe state、evidence-only authorityを説明する。
- `src/spec_dock/assets/spec_dock/docs/rules/root/artifacts.md`を追加する。

### Candidate 3

- provider docsとinstalled/dogfood projectionのparityを確認する。
- command help / examples / naming / worktree referenceが互いに矛盾しないことを確認する。
- docs impact `none`を使う場合でも、対象docs / templates / workflow / migration notesのinspection根拠とfresh spec reviewをreportへ残す。

## 10. Final Quality Gate

Candidate 3のexitには次をすべて要求する。

1. Candidate 1 / 2がcompletedまたはfresh-reviewed plan amendmentで明示的に不要化されている。
2. Candidate 3からCandidate 1 / 2へのdirect dependencyがSpecDock commandで登録・検証されている。
3. provider source、wheel inventory、candidate wheel fresh consumer、updated consumer、dogfoodの実測が揃う。
4. `uv run pytest` full regressionがpassする。
5. manual external-file root/node importとno-backfill scenarioがpassする。
6. E-RQ-001〜025 / E-AC-001〜020のevidence mapがEpic reportへ記録される。
7. unresolved `blocked` / `stale` EAL、open decision、blocking review findingがない。
8. final `qa-reviewer`、issue-wide `code-reviewer`、final `spec-reviewer`がfresh passする。
9. Epic-wide base/head evidenceのdecision reviewとspec reviewがpassする。
10. final commit / clean check / push / PR Delivery Gate / Merge Preparation Gateが閉じ、mergeable PRが作成される。
11. human-only merge boundaryを越えない。

## 11. Plan Blockers

### Current blockers

- `PB-001 canonical adoption`:
  - 本artifactはunreviewed evidenceであり、canonical `plan.md`へ未反映。
  - owner: main orchestrator。
  - next action: EAL disposition、canonical rewrite。
- `PB-002 fresh plan review`:
  - canonical planのfresh `spec-reviewer` passが未取得。
  - owner: main orchestrator。
  - next action: canonical rewrite後にfresh review。
- `PB-003 human Issue-creation approval`:
  - 3 slicesのIssue node作成は人間承認待ち。
  - owner: user / main orchestrator。
  - next action: plan pass後にexactly 3 candidatesを提示して承認を得る。

### Design blockers

- none observed。
- requirement hash、design hash、accepted ADR hash、ninth fresh design review passを入力として確認した。
- 実装中にADR / threat model / platform support / public result変更が必要になった場合は、Issue内で解釈せずEpic design phaseへ戻す。

## 12. Integration Notes for Main Orchestrator

### Canonical integration

- 本draftから採用する場合も、canonical `plan.md`をmain orchestratorが日本語で再記述する。
- Epic `report.md`へ次を追加する。
  - implementation-planner delegated draft path / SHA-256 / source snapshot。
  - diff guard result。
  - Evidence Adoption Ledger disposition。
  - Delegated Draft Evidence lifecycle。
  - plan gate review / fixes / promotion state。
- `adoption_status`、`reflected_to`、reviewer verdictは本artifactを直接変更して自己主張させず、canonical reportで管理する。

### Issue creation / handoff

- G0完了まではIssue nodeを作成しない。
- human approval後にexactly 3 Issueをruntime-owned commandで作成する。
- 実ID採番後にCandidate 3 → Candidate 1 / 2のdependency edgeをcommandで登録する。
- Issue-local draft path indexを実IDで作成し、各Issue planningでjust-in-time adoptionする。
- Candidate 1 / 2のreportにはCandidate 3実IDを持つdeferred PR delivery gateを記録する。

### Final exit contract

- exactly 3 Issuesの責務でE-RQ-001〜025 / E-AC-001〜020を閉じる。
- Candidate 3が配布、dogfood、full quality、Epic-wide review、PR preparationを閉じる。
- unresolved design gap、blocking EAL、blocking reviewer findingを残さない。
- user evidenceを削除・renameしない。
- mergeable PR preparationで完了し、人間mergeを実行しない。

### Provenance / leaf evidence

- delegated role: `implementation-planner`。
- leaf evidence producer: none used。
- source HEAD: `7e867893c1d2fda48db7efee9aac7d69433046ac`。
- ChatGPT advisory ZIP: SHA-256 `ecd4c65a608ee4474fd5e06b0230150ba56106a5eee7418811367c9cbadca371`、candidate validation pass、3 candidates、Issue creation false。
- forbidden actions avoided:
  - canonical docs edit。
  - existing artifact edit。
  - implementation / tests / package / config edit。
  - Issue creation。
  - GitHub mutation。
  - git stage / commit / push。
  - phase promotion / reviewer-pass / implementation-readiness claim。

No canonical edit, final authority, promotion, reviewer-pass, implementation-readiness, or user-dialogue ownership is claimed.
