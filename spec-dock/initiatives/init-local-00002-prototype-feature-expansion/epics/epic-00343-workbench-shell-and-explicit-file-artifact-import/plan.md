---
種別: 計画書（Epic）
ID: "epic-00343"
タイトル: "Workbench Shell And Explicit File Artifact Import"
関連GitHub: ["#343"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-28"
依存: ["requirement.md", "design.md", "artifacts/20260728t100038z-adr-generic-imported-file-identity-and-privacy-boundary.md"]
親: ["init-local-00002"]
---

# epic-00343 Workbench Shell And Explicit File Artifact Import — 計画

## 1. 目的と分割方針

本Epicを、利用者が観測できる価値を各Issue内で端から端まで閉じる必要最小限の3 Issueへ分割する。

1. **Workbench Shell Scaffolding**
   - fresh repositoryと今後作成するInitiative / Epic / Issueで、利用方法をその場で説明するtracked `.workbench/README.md`を持つoptional Workbenchを直ちに利用可能にする。
2. **Generic Single-File Artifact Import**
   - Workbench内外、repository内外の明示single file一件を、root / Initiative / Epic / IssueのArtifactへ安全にimportできるCLI capabilityを提供する。
3. **Integration Distribution And Final Quality**
   - 上記二能力をcandidate wheel、fresh / updated consumer、dogfood、full regression、Epic-wide review、mergeable PR deliveryまで統合する。

layer別Issueへは分割しない。Candidate 1と2は各々CLI / installer / application / domain / infra / presentation / tests / docsの必要部分を含むvertical sliceとする。Candidate 3はreview-onlyではなく、配布された利用者環境で両能力が成立することと、Epic全体の最終品質・PR送達を所有する必須final-quality Issueとする。

- Epic classification: `multi-issue implementation`
- Issue candidate count: exactly 3
- final quality Issue: required
- Issue node: `not_created_pending_human_approval`
- canonical Issue docs: `not_created_pending_human_approval`
- merge: human-only。計画上の最終到達点はmergeable PR preparationであり、mergeは行わない。

## 2. Scope / Non-scope

### Scope

- fresh init rootとfuture Initiative / Epic / Issueの`.workbench/README.md`。
- READMEだけをGit追跡可能にし、Workbenchのその他contentsを深さに関係なくignoreするcontract。
- READMEがpurpose、worktree-local / disposable / noncanonical、explicit Artifact import、manual-only copy、Git ignore非security boundary、evidence-only authorityをmodel / humanへ説明するcontract。
- optional presence、existing root / node no-backfill、semantic opacity、worktree-local / disposable contract。
- existing manual one-shot `workbench copy`の互換維持。
- `artifact import file --file <path>`とexactly one root / node selector。
- repository内外のreadable regular leaf file、ancestor symlink許容、leaf symlink拒否。
- opaque byte identity、source survival、minimal basename normalization、全Artifact family共有slot、no-overwrite、FD-bound publication、privacy-safe output。
- binary / archive / invalid UTF-8をdecodeしないvalidate / sync / dependency / context lifecycle。
- provider、package、installed consumer、dogfood、docs、testのparity。

### Non-scope

- existing root / nodeへのWorkbench backfill。
- Workbench presenceのvalidity要件化。
- `.workbench/README.md`以外のWorkbench contentのGit tracking、automatic copy、watch、sync、copy-back。
- directory / glob / bulk / recursive import。
- source parse、MIME分類、format変換、archive展開。
- typed `file` token、title / slug要求、persistent provenance catalog。
- source delete / move / overwrite。
- importによるcanonical docs、ADR、report、assuranceの自動変更。
- unrelated architecture cleanup、dependency subsystem再設計、rootのgraph node化。
- Issue nodeの事前作成、pre-start canonical Issue `design.md` / `plan.md`の本文化。

## 3. Requirement / Design / ADR ownership

### Requirement ownership

`primary`はfocused implementationとevidenceの所有者、`integration`は配布・dogfood環境での最終再検証所有者である。

| Requirement | Candidate 1 | Candidate 2 | Candidate 3 |
|---|---|---|---|
| E-RQ-001〜007 Workbench shell / optional / no-backfill / opacity / manual copy | primary | compatibility observer | integration |
| E-RQ-008〜012 command / target / source / authorization | — | primary | integration |
| E-RQ-013〜018 bytes / naming / collision / publication / privacy | — | primary | integration |
| E-RQ-019〜020 authority isolation / opaque lifecycle | opacity compatibility | primary | integration |
| E-RQ-021 `chatgpt-output` compatibility | regression observer | primary compatibility | final regression |
| E-RQ-022 existing Artifact compatibility | — | primary compatibility | final regression |
| E-RQ-023 `workbench copy` compatibility | primary compatibility | — | final regression |
| E-RQ-024 provider / consumer parity | focused shell evidence | focused import evidence | primary final distribution |
| E-RQ-025 documentation | shell / copy docs | import / naming / privacy docs | integrated parity |

### Acceptance ownership

| Acceptance criteria | Primary closure owner | Final verification owner |
|---|---|---|
| E-AC-001〜007 Workbench matrix | Candidate 1 | Candidate 3 |
| E-AC-008〜016 import target/source/file/naming/publication/privacy | Candidate 2 | Candidate 3 |
| E-AC-017 opaque lifecycle | Candidate 2 | Candidate 3 |
| E-AC-018 existing command compatibility | Candidate 1: `workbench copy`; Candidate 2: `chatgpt-output` / `new artifact` | Candidate 3 |
| E-AC-019 distribution | Candidate 3 | Candidate 3 |
| E-AC-020 final closure | Candidate 3 | Candidate 3 |

### Design / ADR trace

| Design / decision | Owner |
|---|---|
| D-001〜002 fresh-only shell、tracked guidance README / ignored contents | Candidate 1 |
| D-003〜004 additive import use case、root target | Candidate 2 |
| D-005 explicit source guard / FD-bound publication | Candidate 2 |
| D-006〜007 generic filename / global slot / minimal normalization | Candidate 2 |
| D-008 publication state / privacy result | Candidate 2 |
| D-009 opaque lifecycle | Candidate 2、Candidate 3 final integration |
| accepted ADR `20260728t100038z-adr` | Candidate 2 implementation contract、Candidate 3 non-regression gate |

Candidate 2 / 3はaccepted ADRを再判断しない。`--` family、full destination basename identity、external basename-only visibility、content-derived metadata非公開、FD-bound commit point、postcommit retry不要を変更する必要が出た場合は、Issue内で仮定せずEpic design / ADR amendmentへ戻す。

## 4. Issue一覧と実施順序

### Candidate 1 — Workbench Shell Scaffolding

- candidate key: `candidate-epic-00343-01-workbench-shell`
- recommended grade: `standard`
- tranche: A
- dependencies: none
- user-visible value:
  - fresh init直後とfuture node作成直後にWorkbench shellが存在し、READMEを読めば利用方法とauthority boundaryを理解でき、scratch contentsをGitへ出さず利用できる。
- vertical scope:
  - `src/spec_dock/cli.py`のfresh root判定。
  - provider `.gitignore`。
  - root / Initiative / Epic / Issue templatesのbyte-identicalな`.workbench/README.md`。
  - provider `.gitignore`のREADME-only tracking contract。
  - hidden-directory README package-dataと、既存broad nested README exclusionの削除またはexact legacy pathへの限定。
  - new-node planned / result / filesystem path parity。
  - optional / no-backfill / opacity / manual-only copy compatibility。
  - shell / manual copy public docs。
- deliverables:
  - installer → provider assets/templates → runtime node creation → Git observation → focused tests → docs。
  - README本文にpurpose、temporary/worktree-local/noncanonical、README-only tracking、explicit import、manual copy、secret注意、evidence-only authorityを含むguidance。
  - source / wheel / sdist / installed resourcesのexact README allowlistと4 asset byte parity evidence。
- focused verification:

```bash
uv run pytest tests/unit/infra/test_init_update.py
uv run pytest tests/unit/infra/test_runtime_fs_repo_workbench_opacity.py
uv run pytest tests/cli_runtime/test_runtime_new_doc_s09.py tests/cli_runtime/test_workbench.py
```

- scenario matrix:
  - fresh rootとfuture 3 node kindsのREADME content / byte parity / `git add -n` / planned-result parity。
  - root + 3 node kindsのnested ignore / near-name。
  - `templates/README.md`と4 Workbench README以外のnested template READMEがsource / wheel / sdist / installed resourcesに存在しない。
  - existing init/update/sync/validate/active/artifact/ADRのno-backfill。
  - fake metadata、binary、invalid UTF-8、broken subtreeのsemantic opacity。
  - linked worktree creation時に自動copyせず、明示`workbench copy`だけが現行behaviorを維持。
- rollback:
  - provider template / ignore / installer deltaをIssue commit単位でrevertする。
  - user Workbench contentsや生成済みREADMEを自動削除しない。
  - ignore rollbackではscratch露出を防ぐ旧ruleを先に復元する。
- forbidden boundary:
  - backfill、required Workbench、automatic copy/sync、README以外のWorkbench content tracking。

### Candidate 2 — Generic Single-File Artifact Import

- candidate key: `candidate-epic-00343-02-generic-file-import`
- recommended grade: `critical`
- tranche: A
- dependencies: none
- user-visible value:
  - `artifact import file --file <path>`で、明示single fileをroot / Initiative / Epic / Issueへ、bytesとsourceを保持したままprivacy-safeに保存できる。
- vertical scope:
  - additive CLI / request / result / error / use case / bootstrap。
  - explicit root / node target resolverとroot Artifact setup。
  - source guard、ancestor symlink許容、leaf symlink拒否。
  - stream staging、source revalidation、FD-bound no-replace publication、capability probe。
  - generic `--` filename parser、minimal normalizer、全family共有slot ledger。
  - content-free success/error/warning text / JSON。
  - bodyを読まないvalidate / sync / ADR mirror / deps / context。
  - existing `chatgpt-output` / `new artifact`互換。
  - import / naming / privacy / authority public docs。
- deliverables:
  - CLI → application target/allocation → domain naming → infra publication → presentation → lifecycle consumers → tests → docs。
- focused verification:

```bash
uv run pytest tests/unit/domain/test_artifacts.py
uv run pytest tests/unit/application/test_import_file_artifact.py tests/unit/commands/test_artifact_import_file.py
uv run pytest tests/unit/infra/test_binary_artifact_publisher.py
uv run pytest tests/unit/presentation/test_artifact_import_file.py
uv run pytest tests/cli_runtime/test_artifact_import_file.py
uv run pytest tests/cli_runtime/test_artifact_import_chatgpt_output.py tests/cli_runtime/test_artifact_import_s04.py
```

- scenario matrix:
  - root / Initiative / Epic / Issue、zero / multiple selector。
  - scoped Workbench、repo内non-Workbench、external absolute / relative、nested cwd、cross-filesystem original source。
  - regular、ancestor symlink、missing、directory、leaf symlink、FIFO/socket/device、unreadable、source mutation。
  - Markdown / `.MD` / PDF / image / ZIP / multi-suffix / no-extension / empty / invalid UTF-8 / NUL / large stream。
  - Unicode / space / case / NAME_MAX、typed / blank / generic shared slot、concurrency、01..99 exhaustion。
  - Linux通常権限 / macOS clone-capable success、unsupported capability fail closed。
  - precommit failure、postcommit warning、retry disposition、external sentinel非漏洩。
  - body-open spyによるvalidate / sync / deps / context / ADR mirror isolation。
- rollback:
  - command / use case / parser / explicit publisher pathをIssue commit単位でrevertする。
  - import済みArtifactはuser evidenceとして保持し、削除・renameしない。
  - existing typed / blank / `chatgpt-output` dataをmigrationしない。
- forbidden boundary:
  - typed `file` token、content classification、external absolute path漏洩、source mutation、fallback overwrite、mutable-path commit。
- escalation:
  - accepted ADR変更、supported platform guarantee縮小、新しいdata-loss / overwrite riskはEpic design / ADRへ戻す。

### Candidate 3 — Integration Distribution And Final Quality

- candidate key: `candidate-epic-00343-03-final-quality`
- recommended grade: `strict`
- tranche: B
- dependencies:
  - Candidate 1
  - Candidate 2
- user-visible value:
  - shellとgeneric importを配布wheel、fresh / existing consumer、dogfoodで一貫して利用でき、blocking findingのないmergeable PRとして受け取れる。
- vertical scope:
  - Candidate 1 / 2のcross-feature integration repair。
  - wheel inventory / candidate wheel。
  - fresh consumer、pre-feature existing consumer update/no-backfill、post-update future node。
  - dogfood provider-first projection。
  - manual external-file root/node scenario。
  - full regression、docs parity、Epic report trace。
  - final QA / code / spec review、Epic-wide pre-PR review、push、PR preparation。
- verification:

```bash
uv build
uv run pytest
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync --no-github
```

  - candidate wheelをtemporary Git repositoryへinstallし、fresh root / future node shellとroot / node generic importを通常権限で実測する。
  - READMEなしpre-feature consumerをupdateし、existing root / nodeをbackfillせず、その後のnew nodeだけREADMEを得る。
  - destinationと別filesystemのexternal sourceを成功importし、external path/body/hash/count sentinelがoutput / provenanceへ漏れない。
  - unsupported filesystem capabilityはformal destination作成前にfail closedとなる。
  - dogfood update後もexisting `epic-00343`へREADMEをbackfillせず、validate / sync / deps / contextがpassする。
- repair boundary:
  - integration failureの最小修正は許可する。
  - major feature未実装をCandidate 3へ先送りしない。
  - requirement / design / ADR変更が必要ならEpic planning repairへ戻す。
- rollback:
  - integrated provider deltaをreviewable commit単位でrevertする。
  - generic Artifact / Workbench user contentは削除しない。
  - ignore rollbackはscratch露出防止順序を守る。
- final delivery:
  - fresh `qa-reviewer`をintegration / distribution test evidenceへ、fresh `code-reviewer`をCandidate 1 / 2 / 3を含むEpic base/head aggregate diff全体へ、fresh `spec-reviewer`をEpic closure evidenceへ通し、passまで回す。
  - 同じEpic base/head endpointと全差分証跡をfresh Epic-wide decision review / code review / spec reviewへ渡す。
  - final commit、push、PR Delivery Gate、Merge Preparation Gateを閉じ、human merge前で停止する。

## 5. Dependency / tranche

```text
Candidate 1 Workbench Shell ─────┐
                                 ├─> Candidate 3 Integration / Distribution / Final Quality
Candidate 2 Generic Import ──────┘
```

- Candidate 1と2のproduct dependencyはなく、論理上parallelizableである。
- 同一Epic branch / worktreeと`pyproject.toml` / provider docs / regression surfaceの衝突を避けるため、executionは原則Candidate 1 → Candidate 2 → Candidate 3の順で1 Issueずつ行う。
- Candidate 3は1 / 2の両方へdirect dependencyを持つ。
- 実Issue ID採番後だけ、metadata直編集ではなく次を実行する。

```bash
./spec-dock/scripts/spec-dock deps add --from <candidate-3-issue-id> --to <candidate-1-issue-id>
./spec-dock/scripts/spec-dock deps add --from <candidate-3-issue-id> --to <candidate-2-issue-id>
./spec-dock/scripts/spec-dock deps check <candidate-3-issue-id>
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync
```

Candidate 1 / 2はreview済みlocal milestone commitまで閉じ、per-Issue PRを作らない。各reportはdeferred PR deliveryとしてCandidate 3の実ID、dependency edge、no-per-Issue-PR理由、未完のPR Delivery / Merge Preparation Gateを記録する。Candidate 3はdeferred PR deliveryを使用しない。

## 6. Integration checkpoints / quality gates

### G0 Plan / human approval gate

- implementation-planner evidenceをEALでdispositionし、main orchestratorが本planへ再記述する。
- fresh `spec-reviewer` pass。
- ユーザーがexactly 3 slicesとIssue作成を承認する。
- 完了前のIssue node作成は禁止。

### G1 Per-Issue planning gate

- Issueを1つずつactiveにし、ChatGPT-first Issue planningをjust-in-timeで行う。
- current repository、prior completed Issues、dependency state、Epic reportを再確認する。
- Issue-local requirement → design → planを各fresh `spec-reviewer` passでpromoteする。
- draft-only / handoff-readyとexecution-readyを分離する。

### G2 Per-Issue implementation / review gate

- runtime / CLI / infra / tests / scaffoldは`dev-coder`、shipped docsは`doc-writer`へ委任する。
- code/runtime/test変更はfresh `code-reviewer`、test qualityは必要に応じ`qa-reviewer`、docs/spec alignmentはfresh `spec-reviewer`を通す。
- 各Issueはfocused test、compatibility evidence、commit candidate、post-commit clean checkを持つ。

### G3 Distribution / dogfood gate

- provider source、wheel inventory、candidate wheel fresh consumer、updated consumer、dogfoodを同じcandidate revisionで検証する。
- docs / CLI help / examples / naming / worktree referenceのparityを閉じる。
- Workbench no-backfillとgeneric Artifact opaque lifecycleを配布環境で再確認する。

### G4 Final Epic / PR gate

- E-RQ-001〜025 / E-AC-001〜020のclosure mapをEpic reportへ記録する。
- unresolved `blocked` / `stale` EAL、open decision、blocking findingを残さない。
- full `uv run pytest`、manual scenario、fresh QA review、Epic base/head aggregate diff全体のfresh code review、fresh spec review、Epic-wide decision reviewをpassさせる。
- final commit / clean check / push / PR Delivery Gate / Merge Preparation Gateを閉じる。
- mergeable PRを作成し、人間merge前で停止する。

## 7. Issue handoff / readiness

### Path index

| Candidate | Issue node | draft-requirement | draft-design | draft-plan |
|---|---|---|---|---|
| Candidate 1 | `not_created_pending_human_approval` | `not_created_pending_human_approval` | `not_created_pending_human_approval` | `not_created_pending_human_approval` |
| Candidate 2 | `not_created_pending_human_approval` | `not_created_pending_human_approval` | `not_created_pending_human_approval` | `not_created_pending_human_approval` |
| Candidate 3 | `not_created_pending_human_approval` | `not_created_pending_human_approval` | `not_created_pending_human_approval` | `not_created_pending_human_approval` |

### Handoff-ready

- canonical Epic requirement / design / plan / accepted ADRとCandidate固有のscope、forbidden boundary、acceptance owner、dependencies、verification seedが参照できる。
- Issue nodeとdraft pathは人間承認後にruntime-owned commandで作成する。
- Issue-local draft requirement / design / planはcurrent stateを反映するjust-in-time Issue planning evidenceであり、Epic planning中にexecution-readyを主張しない。

### Execution-ready

各Issueが次を満たした後だけ成立する。

- current repositoryとprior Issue成果を取り込んだcanonical Issue requirement / design / plan。
- phaseごとのfresh `spec-reviewer` pass。
- gradeに応じたspecialist / reviewer / report evidence。
- dependency readinessとactive branch / worktreeの確認。
- unresolved blocking EAL / decisionがない。

### Drift repair

- Issue planningでEpic契約の不足が見つかった場合は該当Epic phaseへ戻り、修正後にfresh reviewする。
- Candidate 1 / 2完了後のactual source driftは、後続Issue planningでhandoff seedを更新する。
- Issue内でparent requirement / accepted ADRを再解釈しない。

## 8. Rollout / docs / rollback

### Docs impact

- Candidate 1:
  - `docs/README.md`、`guide.md`、`reference_worktree.md`へREADME shell auto-generation、optional/no-backfill、README-only tracking、ignored/disposable、evidence-only authority、manual-only copyを反映する。
- Candidate 2:
  - `docs/README.md`、`guide.md`、`reference_naming.md`へroot / node target、source policy、generic `--` family、privacy-safe state、evidence-only authorityを反映する。
  - `docs/rules/root/artifacts.md`を追加する。
- Candidate 3:
  - provider docsとinstalled / dogfood projection、CLI help / examplesのparityを確認する。

### Rollout

1. Candidate 1 / 2を各focused gateまで完了する。
2. Candidate 3でcandidate wheelをbuildし、fresh / existing consumerへ適用する。
3. existing consumerはno-backfillを確認し、その後のnew nodeからshellを得る。
4. dogfoodはprovider-first update経路でprojectionする。
5. full quality / PR gate後にmergeable PRを引き渡す。

### Rollback invariants

1. Workbench ignoreを戻す場合、scratchが`git status`へ露出しないruleを先に復元する。
2. runtime / template / package deltaをreviewable commit単位でrevertする。
3. generic imported Artifact、生成済みWorkbench README、Workbench user contentを削除・renameしない。
4. existing typed / blank Artifact、`chatgpt-output`、`workbench copy` dataをmigrationしない。
5. rollback後にfocused compatibility、validate、syncを再実行する。

## 9. Final exit contract

次をすべて満たしたときだけEpic実装完了候補とする。

1. Candidate 1 / 2がcompleted、またはfresh-reviewed plan amendmentで明示的に不要化されている。
2. Candidate 3から1 / 2へのdirect dependencyがSpecDock commandで登録・検証されている。
3. provider source、wheel inventory、candidate wheel fresh consumer、updated consumer、dogfoodの実測が揃う。
4. `uv run pytest` full regressionとmanual external-file / no-backfill scenarioがpassする。
5. E-RQ-001〜025 / E-AC-001〜020のevidence mapがEpic reportへ記録される。
6. unresolved `blocked` / `stale` EAL、open decision、blocking review findingがない。
7. fresh QA review、Candidate 1 / 2 / 3を含むEpic base/head aggregate diff全体のfresh code review、fresh spec review、Epic-wide decision reviewがpassする。
8. final commit / clean check / push / PR Delivery Gate / Merge Preparation Gateが閉じる。
9. mergeable PR preparationで停止し、人間mergeを実行しない。

## 10. Current blockers / approval gate

- requirement amendment blocker: none。second fresh README requirement review `pass`、confidence 0.99。
- design amendment blocker: none。third fresh README design review `pass`、confidence 0.92。
- plan amendment blocker: none。second fresh README plan review `pass`、confidence 0.99。
- Issue creation blocker:
  - exactly 3 slicesに対する人間承認が未取得。
- Issue nodes:
  - 0。レビューと人間承認前には作成しない。
