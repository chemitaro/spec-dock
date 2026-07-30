---
種別: 実装計画書（Issue）
ID: "iss-00345"
タイトル: "Generic Single-File Artifact Import Implementation Plan"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-30"
親: ["epic-00343", "init-local-00002"]
planning_method: "Spec-Locked Micro-Batch TDD"
authorized_profile_observed: "standard"
parent_recommended_grade: "critical"
classification_status: "runtime_classified"
---

# iss-00345 Generic Single-File Artifact Import — 実装計画書（Standard / TDD）

## 0. 計画の位置づけ

本書はreview済みの `requirement.md` とcanonical `design.md` を、Codex と delegated workers が上から実行できる command queueへ変換するcanonical planned contract draftである。実行結果、Red/Green/Refactorの観測、test output、reviewer verdict、commit/no-op evidenceは `report.md` に記録する。本書へ実行結果を戻して二重正本にしない。

本書がcanonical pathに存在することだけではfresh reviewer pass、execution-ready、PR-ready、merge-ready、Issue finish、Epic completion、PR deliveryを意味しない。runtime classificationは`standard`であり、parent Candidate 2の`critical` recommendationはレビュー重点として保持する。以下のgateはhigher-risk recommendationに耐える厚さを維持する。

## 1. この計画で満たす要件ID

- Objectives: `I345-OBJ-001`〜`I345-OBJ-003`
- Requirements: `I345-RQ-001`〜`I345-RQ-015`
- Behaviors: `I345-BH-001`〜`I345-BH-008`
- Constraints: `I345-CON-001`〜`I345-CON-011`
- Edge cases: `I345-EC-001`〜`I345-EC-019`
- Acceptance criteria: `I345-AC-001`〜`I345-AC-019`
- Designs: `DES-345-001`〜`DES-345-007`

## 2. Execution policy

### 2.1 Spec-Locked Micro-Batch TDD

- `1 step = 1 observable behavior slice` を基本にする。
- 各stepはpublic interface / observable behaviorのfailing testから始め、最小Greenを縦に通す。
- private helperやlayer単位のhorizontal batchingを先行させない。
- 一つのtestをRed→最小実装→Greenにしてから次のtestへ進む。
- refactorは同stepのGreenを維持する範囲に限定する。
- closure indexのrequired row、locked expectation、spec linkを変更する必要が出たらimplementationを止め、plan amendmentとfresh reviewへ戻す。

### 2.2 Parent / delegated worker boundary

- parent Codexはsource selection、step ordering、worker handoff、diff integration、report ledger、review gateを所有する。
- runtime/CLI/domain/application/infra/testsは原則`dev-coder`へ委任する。
- shipped docs/rulesは`doc-writer`へ委任する。
- worker outputはaccepted decisionではなく、parentがdiff/test/evidenceを確認して採否する。
- workerはcanonical `requirement.md` / `design.md` / `plan.md` / `report.md`を直接書き換えない。実行時のreport転記はparent orchestratorが行う。

### 2.3 Grade handling

- authorized profileをimplementation workerが変更しない。
- `critical` recommendationを理由にsafety/fault/rollback evidenceを厚くすることはmanual escalationであり、profile mutationではない。
- specialist/reviewer availabilityがstrict/critical workflow obligationを満たさない場合は、skip reasonだけで進めず、workflowに従いblockedまたはexplicitly approved fallback evidenceとする。

## 3. 依存関係から導く実装順序

```text
S01 public tracer bullet
  CLI -> command -> application -> domain name -> explicit publisher -> presentation
  root / Issue の成功を最小縦切りで観測
        |
        v
S02 source/publication/privacy hardening
  external path, eligibility, descriptor identity, cross-FS, capability,
  pre/post commit states, fault injection
        |
        v
S03 shared identity and concurrency completion
  minimal normalization, typed/blank/generic ledger, suffix exhaustion,
  cooperative/non-cooperative races
        |
        v
S04 opaque lifecycle and legacy compatibility
  validate/sync/deps/context/ADR/authoring body isolation,
  chatgpt-output + typed/blank regression
        |
        v
S90 docs/rules/provider-dogfood projection
        |
        v
S99 final local quality, rollback evidence, Issue 346 handoff
```

この順序は、public tracerを最初に通し、そのinterfaceを変えずにsafety、identity、lifecycleを閉じる。S02より前に大量のdomain/infra helperだけを作らず、S01で実際のcommand successを観測する。

## 4. Milestones

| Milestone | Steps | Observable completion candidate | Commit candidate gate |
|---|---|---|---|
| `M1 Public vertical tracer` | `S01` | root/Issueへ一件のopaque fileをprivacy-safe resultでcommitできる | focused S01 tests Green後 |
| `M2 Safety and identity closure` | `S02`, `S03` | source/publication/privacy/concurrency/naming matrixが閉じる | 各step独立commit候補 |
| `M3 Semantic and compatibility closure` | `S04` | generic bodyがdefault lifecycleに入らずlegacy contractが維持される | S04 focused regression後 |
| `M4 Shipped surface and local gate` | `S90`, `S99` | provider docs/runtime、managed projection、focused/default local evidence、rollback/handoffが揃う | docs/evidence差分に応じたcommit候補 |

## 5. ステップ一覧

| Step | Behavior slice | Depends on | Unblocks | Primary role |
|---|---|---|---|---|
| `S01` | additive commandからroot/Issueへの最小generic import success | main workflowによるcanonical R/D/P adoption、fresh review、runtime-owned readiness evidence | S02, S03 | `dev-coder` |
| `S02` | arbitrary explicit sourceをdescriptor-boundで安全にpublishしprivacy-safe stateを返す | S01 | S03, S04 | `dev-coder` |
| `S03` | minimal basename + shared slot + no-overwrite concurrencyを完成 | S01, S02 | S04, S90 | `dev-coder` |
| `S04` | generic bodyをlifecycleから隔離しexisting contractsを固定 | S01〜S03 | S90, S99 | `dev-coder` |
| `S90` | docs/rulesとprovider→dogfood projectionを整合 | S01〜S04 | S99 | `doc-writer` + parent |
| `S99` | focused/default local quality、rollback、deferred handoffを判定 | all previous | Issue 346 handoff | parent + reviewers |

## 6. 要件 ↔ ステップ対応

| Requirement | Owner steps |
|---|---|
| `I345-RQ-001`, `I345-RQ-012` | S01, S90 |
| `I345-RQ-002`, `I345-RQ-003`, `I345-RQ-004` | S02 |
| `I345-RQ-005`, `I345-RQ-006`, `I345-RQ-007` | S01, S03 |
| `I345-RQ-008`, `I345-RQ-009`, `I345-RQ-010` | S02, S03 |
| `I345-RQ-011` | S04 |
| `I345-RQ-013` | S01, S04 |
| `I345-RQ-014` | S90, S99 |
| `I345-RQ-015` | all steps, S99 final assertion |

## 7. Spec-Locked Closure Index

`required=yes`のrowを削除または意味変更してはならない。`evidence level`はplanned minimumであり、実際のevidenceは`report.md`へ記録する。

### 7.1 Acceptance criteria closure

| Closure ID | Spec link | Locked expectation | Observable input/state | Bug class guarded | Required | Evidence level | Owner | Test seeds |
|---|---|---|---|---|---|---|---|---|
| `CL-AC-001` | `I345-AC-001` | exact command/options/one selector | CLI help + parse matrix | accidental legacy/general options | yes | unit + CLI | S01 | `tc-s01-001`, `002` |
| `CL-AC-002` | `I345-AC-002` | four targets; root non-node | root/initiative/epic/issue fixtures | fake graph root / wrong scope | yes | app + CLI | S01 | `tc-s01-003`, `004` |
| `CL-AC-003` | `I345-AC-003` | repo-root-relative + explicit external | nested cwd, abs, `..` | cwd dependence/path leak | yes | CLI + infra | S02 | `tc-s02-001` |
| `CL-AC-004` | `I345-AC-004` | regular only; leaf symlink reject; ancestor allow | source-kind matrix | unsafe file admission | yes | infra | S02 | `tc-s02-002`, `003` |
| `CL-AC-005` | `I345-AC-005` | opaque bytes/source unchanged | binary fixture matrix | decode/normalize/source mutation | yes | infra + CLI | S01, S02 | `tc-s01-005`, `tc-s02-004` |
| `CL-AC-006` | `I345-AC-006` | fixed generic grammar/full basename ID | deterministic clock | typed-token drift | yes | domain + CLI | S01, S03 | `tc-s01-004`, `tc-s03-001` |
| `CL-AC-007` | `I345-AC-007` | minimal/NAME_MAX-safe normalization | Unicode/space/ext/long names | destructive slugification/byte split | yes | domain | S03 | `tc-s03-002`, `003` |
| `CL-AC-008` | `I345-AC-008` | shared all-family slots/exhaustion | mixed directory inventory | cross-family overwrite | yes | domain + app | S03 | `tc-s03-004`, `005` |
| `CL-AC-009` | `I345-AC-009` | cooperative/noncooperative no overwrite | parallel import/barrier | race overwrite/duplicate identity | yes | app + infra | S03 | `tc-s03-006`, `007` |
| `CL-AC-010` | `I345-AC-010` | source races fail precommit | mutation/replace/unlink/retarget | TOCTOU acceptance | yes | infra | S02 | `tc-s02-005` |
| `CL-AC-011` | `I345-AC-011` | cross-FS succeeds; unsupported fails closed | device difference/capability stub | unsafe fallback | yes | infra + CLI | S02 | `tc-s02-006`, `007` |
| `CL-AC-012` | `I345-AC-012` | honest three-state/retry | fault injection matrix | duplicate retry after commit | yes | app + presentation + CLI | S02 | `tc-s02-008`, `009` |
| `CL-AC-013` | `I345-AC-013` | external basename-only/no derived data | secret path/body/hash sentinels | privacy disclosure | yes | presentation + CLI | S02 | `tc-s02-010` |
| `CL-AC-014` | `I345-AC-014` | body unopened by lifecycle | invalid UTF-8 ADR-like generic | semantic escalation/decode | yes | CLI/runtime | S04 | `tc-s04-001`, `002`, `003` |
| `CL-AC-015` | `I345-AC-015` | root setup/rules safe/provider-first | fresh/broken/wrong rules | graph pollution/setup overwrite | yes | app + CLI + docs | S01, S90 | `tc-s01-003`, `tc-s90-001` |
| `CL-AC-016` | `I345-AC-016` | chatgpt-output unchanged | existing focused suite | legacy contract regression | yes | regression | S04 | `tc-s04-004` |
| `CL-AC-017` | `I345-AC-017` | typed/blank unchanged/no migration | existing artifacts/new artifact | parser/allocation regression | yes | regression | S03, S04 | `tc-s03-004`, `tc-s04-005` |
| `CL-AC-018` | `I345-AC-018` | provider/docs/local gates; 346 defer | provider/projection diff + test lane | shipped drift/scope theft | yes | docs + default | S90, S99 | `tc-s90-002`, `tc-s99-001` |
| `CL-AC-019` | `I345-AC-019` | evidence-only/canonical=false/no assurance mutation | result/docs/report diff | authority escalation | yes | presentation + inspection | S01, S90, S99 | `tc-s01-005`, `tc-s90-003`, `tc-s99-004` |

### 7.2 Edge-case closure

| Closure ID | Spec link | Locked expectation | Observable input/state | Bug class guarded | Required | Evidence level | Owner | Test seeds |
|---|---|---|---|---|---|---|---|---|
| `CL-EC-001` | `I345-EC-001` | zero/multiple reject before mutation | argv matrix | ambiguous target side effect | yes | unit | S01 | `tc-s01-002` |
| `CL-EC-002` | `I345-EC-002` | nested cwd still repo-root-relative | nested subprocess cwd | cwd-relative misread | yes | CLI | S02 | `tc-s02-001` |
| `CL-EC-003` | `I345-EC-003` | `..` external allowed/basename-only | parent temp source | external rejection/leak | yes | CLI | S02 | `tc-s02-001`, `010` |
| `CL-EC-004` | `I345-EC-004` | leaf symlink reject; ancestor stable allow | symlink fixtures | policy inversion | yes | infra | S02 | `tc-s02-002`, `003`, `005` |
| `CL-EC-005` | `I345-EC-005` | special/unreadable reject | missing/dir/FIFO/socket/device/denied | unsafe source open | yes | infra | S02 | `tc-s02-002` |
| `CL-EC-006` | `I345-EC-006` | empty/binary/invalid UTF-8 preserved | payload matrix | text-only copy | yes | infra + CLI | S01, S02 | `tc-s01-005`, `tc-s02-004` |
| `CL-EC-007` | `I345-EC-007` | basename variants preserved | ext/no-ext/dot/case/CJK/emoji | classifier/slugification | yes | domain | S03 | `tc-s03-002` |
| `CL-EC-008` | `I345-EC-008` | unsafe/reserved deterministic minimal mapping | control/reserved/trailing | path escape/empty name | yes | domain | S03 | `tc-s03-003` |
| `CL-EC-009` | `I345-EC-009` | max suffix also NAME_MAX safe | mocked/pathconf limit | ENAMETOOLONG/codepoint split | yes | domain + infra | S03 | `tc-s03-003` |
| `CL-EC-010` | `I345-EC-010` | typed/blank/generic share slots | fixed timestamp mixed names | family-local allocator | yes | domain + CLI | S03 | `tc-s03-004` |
| `CL-EC-011` | `I345-EC-011` | 01..99 exhaustion no mutation | prefilled slots | unbounded/overwrite fallback | yes | app | S03 | `tc-s03-005` |
| `CL-EC-012` | `I345-EC-012` | cooperative/noncooperative race safe | threads/process barrier | overwrite/duplicate result | yes | app + infra | S03 | `tc-s03-006`, `007` |
| `CL-EC-013` | `I345-EC-013` | source mutation precommit failure | stage barrier mutations | stale FD/path acceptance | yes | infra | S02 | `tc-s02-005` |
| `CL-EC-014` | `I345-EC-014` | cross-FS source support | different device fixture/seam | EXDEV false failure | yes | infra | S02 | `tc-s02-006` |
| `CL-EC-015` | `I345-EC-015` | unsupported capability no formal dest | primitive/probe injection | unsafe fallback | yes | infra | S02 | `tc-s02-007` |
| `CL-EC-016` | `I345-EC-016` | postcommit warnings success/no retry | fsync/cleanup/lock faults | misleading failure/retry | yes | app + CLI | S02 | `tc-s02-009` |
| `CL-EC-017` | `I345-EC-017` | ADR-looking generic remains opaque | `.md` with accepted-like frontmatter | authority/mirror escalation | yes | sync/authoring | S04 | `tc-s04-002`, `003` |
| `CL-EC-018` | `I345-EC-018` | fresh root setup; unsafe existing entry fail | rules fixtures | overwrite/broken setup | yes | app + CLI | S01, S90 | `tc-s01-003`, `tc-s90-001` |
| `CL-EC-019` | `I345-EC-019` | legacy chatgpt-output exact contract | current suite | accidental genericization | yes | regression | S04 | `tc-s04-004` |

### 7.3 Constraint closure

| Closure ID | Spec link | Locked expectation | Observable input/state | Bug class guarded | Required | Evidence level | Owner | Test seeds |
|---|---|---|---|---|---|---|---|---|
| `CL-CON-001` | `I345-CON-001` | exact leaf read only/no parent listing | filesystem spy | overbroad authorization | yes | infra | S02 | `tc-s02-001`, `002` |
| `CL-CON-002` | `I345-CON-002` | external parent never public/tracked | sentinel path | privacy leak | yes | CLI + diff | S02, S99 | `tc-s02-010`, `tc-s99-004` |
| `CL-CON-003` | `I345-CON-003` | no body/hash/count/MIME/encoding public | payload and exact JSON keys | content-derived leak | yes | presentation | S02 | `tc-s02-010` |
| `CL-CON-004` | `I345-CON-004` | formal entry never replaced | preexisting file/symlink/dir/race | evidence loss | yes | infra | S03 | `tc-s03-006`, `007` |
| `CL-CON-005` | `I345-CON-005` | bounded chunk memory | large/read-size spy | whole-file memory load | yes | infra | S02 | `tc-s02-004` |
| `CL-CON-006` | `I345-CON-006` | FD/path/source/destination identity guards | mutation/retarget/race | TOCTOU | yes | infra | S02, S03 | `tc-s02-005`, `tc-s03-007` |
| `CL-CON-007` | `I345-CON-007` | unsupported platform fails closed | capability injection | unsafe fallback | yes | infra | S02 | `tc-s02-007` |
| `CL-CON-008` | `I345-CON-008` | no semantic body read | open/read spy | semantic escalation | yes | runtime | S04 | `tc-s04-001`〜`003` |
| `CL-CON-009` | `I345-CON-009` | provider-first/projection checked | changed-path parity | dogfood as authority | yes | inspection | S90 | `tc-s90-002` |
| `CL-CON-010` | `I345-CON-010` | 346 obligations remain deferred | report handoff checklist | scope expansion | yes | inspection | S99 | `tc-s99-003` |
| `CL-CON-011` | `I345-CON-011` | evidence-only/no authority claim | docs/output string scan | implicit adoption/readiness | yes | inspection + presentation | S01, S90, S99 | `tc-s90-003`, `tc-s99-004` |

## 8. S01 — Public vertical tracer: commandからroot/Issueへ一件をcommitする

### 8.1 Behavior goal

利用者が`artifact import file --file <path>`とvalid `--root`または`--issue`を指定すると、opaque source一件がfixed generic nameでtarget `artifacts/`へcommitされ、privacy-safe resultが返る。existing `chatgpt-output` code pathは変わらない。

### 8.2 Trace

- Requirements: `I345-RQ-001`, `I345-RQ-004`〜`I345-RQ-006`, `I345-RQ-012`, `I345-RQ-013`, `I345-RQ-015`
- Designs: `DES-345-001`〜`DES-345-005`
- Acceptance: `I345-AC-001`, `002`, `005`, `006`, `015`, `019`
- Closures: `CL-AC-001`, `002`, `005`, `006`, `015`, `019`; `CL-EC-001`, `006`, `018`; `CL-CON-011`

### 8.3 Depends on / unblocks

- Depends on: main workflowが本候補をcanonical `requirement.md` / `design.md` / `plan.md`へ採用し、fresh reviewとruntime-owned assurance/readiness evidenceを記録していること。本ZIP自体はその条件を満たさない。
- Unblocks: S02 safety hardening、S03 identity/concurrency、S04 lifecycle tests。

### 8.4 Target files and symbols

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`: `artifact import file` leaf。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/artifact_import.py`: `ArtifactImportFileArgs`, `_add_file_arguments`, `_file_args_factory`, `_run_file`。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`: file import DTOs, publish DTOs, `UseCases.import_file_artifact`。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py`: `ExplicitFileSourceGuard`, `ExplicitFileArtifactPublisher`, Ports fields。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_file_artifact.py` (new): `import_file_artifact`, target descriptor/resolver。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_artifact_doc.py`: target-neutral setup extraction only as needed。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/artifacts.py`: first generic parser/formatter/normalizer and slot API sufficient for standard slot。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/binary_artifact_publisher.py`: `guard_explicit_file_source` lease entryと、leaseをborrowする`publish_explicit_file` entry。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py`: four generic renderers。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py`: wiring。
- tests: new command/application/presentation/CLI files plus narrow port test。

### 8.5 Planned contract

- Scope: root/Issue happy path、exact CLI grammar、public DTO field allowlist、full-basename identity、source unchanged。
- Test obligation: public command first; root non-node; binary/invalid UTF-8 one tracer; no hash/count/authority claim。
- Red evidence requirement: `red-required`。new command parseとCLI successがmissing command/use caseでfailすることを保存。
- Green verification: focused S01 commandsがpassし、legacy chatgpt command smokeもpass。
- Refactor guardrail: legacy request/result/renderer/Workbench guardをrename/generalizeしない。shared private core extractionはnew and legacy tests Greenの範囲だけ。
- Amendment trigger: fixed command/options、root semantics、result allowlist、full-basename IDを変える必要がある場合。

### 8.6 Red → Green → Refactor

1. **Red 1**: command help/parser exact-key testsを追加し、`file` leaf不在でfailを確認。
2. **Green 1**: parser/registry/args factoryだけを追加してparser testsをpass。
3. **Red 2**: `FileArtifactImportRequest`→root/Issue→generic resultのapplication/CLI tracer testsを追加。
4. **Green 2**: minimal target resolver、standard-slot formatter、explicit source guard/publish ports、renderer、bootstrapを縦に通す。source guardはsetup mutation前に呼ぶ。
5. **Red 3**: binary/invalid UTF-8とsource survival、exact JSON key、`canonical=false`を追加。
6. **Green 3**: bounded staging coreをreuseし、generic public DTOからhash/countを除外。
7. **Refactor**: Workbench-specific guardとshared staging coreをprivate boundaryへ分け、legacy testsを再実行。

### 8.7 Step-local verification commands

```bash
uv run pytest tests/unit/commands/test_artifact_import_file.py
uv run pytest tests/unit/application/test_import_file_artifact.py
uv run pytest tests/unit/application/test_binary_artifact_import_ports.py
uv run pytest tests/unit/presentation/test_artifact_import_file.py
uv run pytest tests/cli_runtime/test_artifact_import_file.py -k 'help or root or issue or opaque'
uv run pytest tests/unit/commands/test_artifact_import_chatgpt_output.py
```

### 8.8 Delegation contract

- **delegated role**: `dev-coder`。parent Codexがintegrationとreport転記を所有。
- **input docs**: main workflowで採用・fresh reviewされたcanonical `requirement.md`, `design.md`, `plan.md`; parent Epic R/D/P; accepted ADR; `AGENTS.md`; current command/application/contracts/ports/publisher/presentation/domain/bootstrap files; nearest legacy tests。
- **allowed paths**: §8.4に列挙したprovider runtime filesとS01 test filesのみ。`spec-dock/` projectionはS90まで変更しない。
- **forbidden changes**: existing `ArtifactImportChatGptOutputArgs`, `ArtifactImportRequest/Result/Error`, legacy renderers/fields、Workbench eligibility、typed/blank grammar、assurance/docs/canonical specs、Issue 346 surfaces。
- **acceptance criteria**: S01 trace rowsがobservable testsでGreen、source unchanged、root non-node、generic result exact allowlist、legacy smoke Green。
- **required tests**: §8.7の全commands。new file不存在を理由にtestを省略せず作成する。
- **reviewer focus**: vertical pathが実際にCLIからFSまで通ること、legacy conditional分岐の肥大化がないこと、public DTOにraw/internal fieldsがないこと。
- **stop conditions**: rootをgraphへ追加する必要、legacy contract変更、unsafe publication fallback、accepted filename/result boundary変更、allowed path外の大規模lifecycle変更が必要。
- **output required**: changed files、Red/Green/Refactor evidence、test output、unresolved risks、`Ledger Note`または`No material implementation decisions beyond the approved plan.`、reportへ転記するstep closure summary。

### 8.9 具体テストケース一覧

- `tc-s01-001` acceptance: additive command helpはgeneric最小optionだけを示す
  - 前提: provider registryからruntime parserをbuildする。
  - 操作: `artifact import file --help`をparseし、help textとoption setを取得する。
  - 期待結果: `--file`, `--root`, `--initiative`, `--epic`, `--issue`, `--json`があり、`--title`, `--slug`, MIME/encoding/move/overwrite系がない。
  - 失敗検出: legacy `chatgpt-output` argumentsをgeneric commandへ流用する回帰を検出する。
  - 検証方法: `tests/unit/commands/test_artifact_import_file.py`のred-first parser test。
  - 関連 closure id: `CL-AC-001`

- `tc-s01-002` negative: selector zero/multipleはuse case前に拒否される
  - 前提: command use case spyとfresh temp repositoryを用意する。
  - 操作: targetなし、root+issue、initiative+epic等のargvをparseする。
  - 期待結果: exit 2、spy call 0、source open 0、`artifacts/`作成なし。
  - 失敗検出: ambiguous targetでsource/destination mutationが始まる回帰を検出する。
  - 検証方法: parser unit testとCLI temp-tree assertion。
  - 関連 closure id: `CL-AC-001`, `CL-EC-001`

- `tc-s01-003` acceptance: root importはrootをgraph nodeにせずrules setupする
  - 前提: initialized temp repoにroot `artifacts/`がなく、valid regular sourceがある。
  - 操作: fixed clockで`artifact import file --root --file <repo-relative>`を実行する。
  - 期待結果: `spec-dock/artifacts/<timestamp>--<basename>`とcorrect `rules.md` symlinkが作られ、`.meta.json`/graph node count/depsは不変。
  - 失敗検出: fake root node、wrong rules source、source eligibility前setupを検出する。
  - 検証方法: application test + CLI runtime filesystem/graph snapshot。
  - 関連 closure id: `CL-AC-002`, `CL-AC-015`, `CL-EC-018`

- `tc-s01-004` acceptance: Issue successはfull destination basenameをidentityにする
  - 前提: Issue `iss-00345`相当fixture、fixed UTC clock、source `Report FINAL.PDF`がある。
  - 操作: `artifact import file --issue 345 --file "fixtures/Report FINAL.PDF" --json`を実行する。
  - 期待結果: destinationは`<timestamp>--Report FINAL.PDF`、`artifact_id`はそのfull basename、target kind/idはissue/canonical id。
  - 失敗検出: typed `file` token、slugification、extension/case/space loss、stem-only identityを検出する。
  - 検証方法: application + CLI exact JSON assertion。
  - 関連 closure id: `CL-AC-002`, `CL-AC-006`

- `tc-s01-005` acceptance: opaque tracerはsourceを保持しpublic metadataを限定する
  - 前提: invalid UTF-8/NULを含むsmall sourceとcontent sentinelを用意する。
  - 操作: Issue targetへimportし、source/destination bytesとtext/JSONを読む。
  - 期待結果: bytes一致、source unchanged、resultにhash/byte_count/MIME/encoding/body/authority claimがなく`canonical=false`。
  - 失敗検出: text decode、source mutation、legacy result DTO再利用、implicit adoption claimを検出する。
  - 検証方法: CLI runtime byte comparison + presentation exact-key test。
  - 関連 closure id: `CL-AC-005`, `CL-AC-019`, `CL-EC-006`, `CL-CON-011`

### 8.10 Step closure contract

- 全S01 closureがGreen。
- legacy command unit smoke Green。
- public result exact-key snapshotがreviewed diffに含まれる。
- worker decision ledgerにplan外decisionなし、またはmaterial decisionを明示。
- parentがprovider diffだけをintegrateし、reportへevidenceを転記する。

### 8.11 Report evidence destination

- `report.md / Step Contract Closure / S01`
- `report.md / Test Contract Closure / S01`
- `report.md / Delegated Worker Evidence / S01`
- `report.md / Spec Interpretation / Decision Ledger`

### 8.12 Commit candidate

```text
feat(artifact): 汎用単一ファイル import の縦切りを追加
```

commitはS01 review/test gate後の候補であり、本計画は作成済みを主張しない。

## 9. S02 — Explicit source / publication / privacy hardening

### 9.1 Behavior goal

repository内外の明示regular file一件を、leaf symlink reject / ancestor symlink allow、descriptor-bound identity、destination-side staging、cross-filesystem対応、capability fail-closedでpublishし、pre/post commit stateとexternal privacyを正確に返す。

### 9.2 Trace

- Requirements: `I345-RQ-002`〜`I345-RQ-004`, `I345-RQ-008`〜`I345-RQ-010`
- Designs: `DES-345-004`, `DES-345-005`
- Acceptance: `I345-AC-003`〜`005`, `010`〜`013`
- Closures: `CL-AC-003`, `004`, `005`, `010`〜`013`; `CL-EC-002`〜`006`, `013`〜`016`; `CL-CON-001`〜`003`, `005`〜`007`

### 9.3 Target files and symbols

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`: explicit publish result/error vocabulary。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py`: narrow explicit source guard / publisher Protocols。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_file_artifact.py`: source lease ownership、setup preflight/apply ordering、attempt cleanup aggregation、state mapping、lock warning merge。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/binary_artifact_publisher.py`: nonblocking regular-file guard、borrowed lease、no-throw descriptor finalization、shared staging core、capability probe、source visibility classifier。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/artifact_import.py`: unknown error redaction only if S01 incomplete。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py`: exact state/retry/privacy rendering。
- `tests/unit/infra/test_binary_artifact_publisher.py` and generic app/presentation/CLI tests。

### 9.4 Planned contract

- Scope: path resolution、source-kind matrix、opaque large copy、source TOCTOU、cross-FS、capability、fault states、privacy sentinels。
- Test obligation: all exits and warning paths; exact field allowlist; no external parent/content-derived data。
- Red evidence: `red-required` per fault class; existing publisher tests are `covered-existing` only forlegacy core, notgeneric policy。
- Green verification: S02 focused commands。
- Refactor guardrail: internal hash/count verificationを削除しないがpublic DTOへ出さない。ancestor symlink acceptanceをlegacy Workbench guardへ適用しない。
- Amendment trigger: public privacy relax、commit point変更、unsafe platform fallback、postcommit retry requirement。

### 9.5 Red → Green → Refactor

1. path/source-kind/privacy matrix testsをRedにする。
2. explicit guardをlegacy guardから分離し、repo-root-relative/absolute/`..`、ancestor symlink、FIFO direct/race nonblocking rejectionをGreenにする。
3. mutation/cross-FS/capability testsをRedにする。
4. shared staging coreへFD/source identity/capability probeを完成しGreenにする。
5. precommit fault、三つのpostcommit warning、descriptor close no-throw、race retry cleanup aggregation、public renderingをRedにする。
6. phase-aware state mapper、attempt cleanup merge、allowlist rendererをGreenにする。
7. fault injector namingとprivate helpersをtidyし、legacy publisher testsを再実行する。

### 9.6 Step-local verification commands

```bash
uv run pytest tests/unit/infra/test_binary_artifact_publisher.py -k 'explicit or generic or source or publication or fault or cross_filesystem'
uv run pytest tests/unit/application/test_import_file_artifact.py -k 'source or publication or warning or privacy'
uv run pytest tests/unit/presentation/test_artifact_import_file.py
uv run pytest tests/cli_runtime/test_artifact_import_file.py -k 'external or relative or source or fault or warning or privacy or cross_filesystem'
uv run pytest tests/cli_runtime/test_artifact_import_s04.py
```

### 9.7 Delegation contract

- **delegated role**: `dev-coder` with filesystem/security focus。
- **input docs**: main workflowで採用・fresh reviewされたcanonical R/D/P、accepted ADR Decision 5/6/8、current publisher source/tests、S01 diff/evidence、AGENTS testing/security rules。
- **allowed paths**: §9.3 provider files and tests only。
- **forbidden changes**: public hash/count addition、external path logging/provenance、source move/delete、legacy Workbench ancestry policy、rename/copy overwrite fallback、Issue 346 tests。
- **acceptance criteria**: S02 closure rows Green; cross-FS supported; unsupported capability no formal dest; warning retry not_needed; sentinel absent across text/JSON/stderr/warnings/diff。
- **required tests**: §9.6 plus existing full `tests/unit/infra/test_binary_artifact_publisher.py` after focused subset。
- **reviewer focus**: FD binding、identity comparisons、exception redaction、commit point、cleanup ownership、platform branches、no whole-file reads。
- **stop conditions**: safe primitive unavailable on intended supported platform without parent amendment、postcommit integrity uncertainty、raw path required in public error、source-side link/move required。
- **output required**: changed files、fault matrix、platform notes、Red/Green evidence、privacy sentinel result、unresolved capability risks、Ledger Note、report summary。

### 9.8 具体テストケース一覧

- `tc-s02-001` acceptance: all path forms resolve from repository root
  - 前提: nested current directory、repo-internal source、absolute external source、`../external/report.PDF` sourceを用意する。
  - 操作:各path formでsame targetへimportする。
  - 期待結果: internal relativeはrepo root基準、external absolute/relativeは成功し、parent directory enumerationは行わない。
  - 失敗検出: process cwd基準、external allow flag要求、parent directory scanを検出する。
  - 検証方法: CLI runtime nested-cwd tests + filesystem spy。
  - 関連 closure id: `CL-AC-003`, `CL-EC-002`, `CL-EC-003`, `CL-CON-001`

- `tc-s02-002` negative: ineligible source types are rejected before destination mutation
  - 前提: missing、directory、leaf symlink、FIFO、socket、device、unreadable regular fixturesとfresh targetを用意し、regular `lstat`後からopen前にFIFOへ置換するbarrier fixtureも用意する。
  - 操作:各sourceをgeneric source guard/use caseへ渡し、FIFO direct/race caseにはtimeout guardを置く。
  - 期待結果: `source_ineligible`, `not_committed`, formal destinationなし、fresh root setupなし、source/sentinel不変。
  - 失敗検出: symlink follow、special file blocking open、permission bypass、failure後setupを検出する。
  - 検証方法: infra parametrized test + deterministic lstat/open barrier; privileged runnerではopen denialをfault seamで固定する。
  - 関連 closure id: `CL-AC-004`, `CL-EC-004`, `CL-EC-005`, `CL-CON-001`

- `tc-s02-003` acceptance: stable ancestor symlink is allowed but leaf symlink is not
  - 前提: ancestor directory symlink下のregular leafと、そのleaf自体のsymlinkを別fixtureにする。
  - 操作:両sourceをimportする。
  - 期待結果: stable ancestor caseはbyte-identical success、leaf symlink caseはprecommit failure。
  - 失敗検出: legacy Workbench ancestry policyの誤流用、leaf symlink followを検出する。
  - 検証方法: infra unit + CLI runtime symlink-capability guarded test。
  - 関連 closure id: `CL-AC-004`, `CL-EC-004`

- `tc-s02-004` acceptance: opaque bounded streaming preserves payload matrix
  - 前提: empty、NUL、invalid UTF-8、PDF header、PNG-like bytes、ZIP-like bytes、multi-chunk large payloadを用意する。
  - 操作:small chunk sizeでpublishし、read call sizesをspyする。
  - 期待結果:source/destination bytes一致、source不変、read sizeはconfigured bound以下、text decodeなし。
  - 失敗検出: whole-file load、newline/encoding変換、content classifierを検出する。
  - 検証方法: infra parametrized byte/hash internal equality test + CLI subset。
  - 関連 closure id: `CL-AC-005`, `CL-EC-006`, `CL-CON-003`, `CL-CON-005`

- `tc-s02-005` negative: source mutation and ancestor retarget fail before commit
  - 前提: stage barrierでsame-size rewrite、replace、unlink、ancestor symlink retargetをinjectする。
  - 操作:publisherをbarrier付きで実行する。
  - 期待結果: `source_changed`, `not_committed`, formal destinationなし、owned tempはremovedまたはreported retained。
  - 失敗検出: stale FD/path metadataだけでmutationを見逃すTOCTOU回帰を検出する。
  - 検証方法: infra barrier testsでFD/path/hash/metadata branchesをassert。
  - 関連 closure id: `CL-AC-010`, `CL-EC-013`, `CL-CON-006`

- `tc-s02-006` acceptance: cross-filesystem original source remains supported
  - 前提: test environmentで異なる`st_dev`を持つsource/destinationを利用するか、adapter seamでsource device差を再現する。
  - 操作:generic importを実行する。
  - 期待結果:destination-side tempへstreamし成功、sourceをlink/renameせず不変。
  - 失敗検出:source-side hard link/renameによる`EXDEV` failureを検出する。
  - 検証方法: platform-capable integration fixture、不可時はhermetic syscall spy + skip reasonをreportへ記録。
  - 関連 closure id: `CL-AC-011`, `CL-EC-014`

- `tc-s02-007` negative: unsupported no-replace capability fails closed
  - 前提: `/proc/self/fd` unavailable、macOS symbol unavailable、probe unsupported、probe cleanup uncertaintyをfault-injectする。
  - 操作:formal destinationがない状態でpublishを試みる。
  - 期待結果: `publication_unsupported`, `not_committed`, formal destinationなし、overwrite/rename fallback callなし。
  - 失敗検出:unsafe fallbackまたはcapability probe省略を検出する。
  - 検証方法: syscall spies + fault-injection unit tests。
  - 関連 closure id: `CL-AC-011`, `CL-EC-015`, `CL-CON-007`

- `tc-s02-008` negative: every precommit fault maps to not_committed
  - 前提: temp create、copy、file fsync、hash、hash mismatch、destination parent identity、publication failureを個別injectする。
  - 操作:各faultでuse case/rendererを実行する。
  - 期待結果:exit failure、`committed=false`, `publication_state=not_committed`, retry `safe_after_remediation`, no formal destination。
  - 失敗検出:commit前faultをwarning/successにする誤分類を検出する。
  - 検証方法: infra + application + presentation parametrized tests。
  - 関連 closure id: `CL-AC-012`

- `tc-s02-009` acceptance: postcommit durability/cleanup faults remain committed
  - 前提: successful no-replace commit後にdirectory fsync、temp cleanup、create-lock releaseを個別injectする。別matrixでsource lease、staged-temp FD、destination-parent FDのclose failureをinjectする。
  - 操作:commandをtext/JSON両modeで実行する。
  - 期待結果:三つのpublic fault seamはexit success、formal file存在、`committed_with_warning`, `committed=true`, retry `not_needed`, exact stable warning code。descriptor close failureはno-throwでcommitted resultを保ち、新しいpublic warningを追加しない。
  - 失敗検出:warning/close後failureまたはretryによるduplicate import、汎用post-commit warning追加を検出する。
  - 検証方法: application/CLI fault tests + destination byte assertion。
  - 関連 closure id: `CL-AC-012`, `CL-EC-016`

- `tc-s02-010` security: external source outputs are basename-only and content-free
  - 前提: external parent/body/raw exception/hash sentinelを用意する。
  - 操作:success、source failure、allocation failure、publication failure、postcommit warning、unexpected exceptionをtext/JSONで実行する。
  - 期待結果:success sourceはbasenameのみ、failureはsource/destinationなし、全output/provenance diffにparent/body/hash/count/MIME/encoding/raw errorなし。
  - 失敗検出:DTO/renderer/logger/error chainingからのprivacy leakを検出する。
  - 検証方法: exact-key payload assertions、combined stdout/stderr/warnings scan、tracked diff scan。
  - 関連 closure id: `CL-AC-013`, `CL-EC-003`, `CL-CON-002`, `CL-CON-003`

### 9.9 Step closure contract

- source-kind/path/fault/privacy matrixがGreen。
- legacy publisher full unit fileもGreen。
- platform-specific skipはcapabilityと理由をreportへ残し、contract未検証をpassと表現しない。
- committed/warning retry semanticsのreviewer focusが解消。

### 9.10 Report evidence destination

- `report.md / Step Contract Closure / S02`
- `report.md / Test Contract Closure / S02`
- `report.md / Privacy and Fault Injection Matrix`
- `report.md / Platform Capability Evidence`
- `report.md / Delegated Worker Evidence / S02`

### 9.11 Commit candidate

```text
fix(artifact): 明示ファイル publish と privacy 境界を固定
```

## 10. S03 — Minimal naming, shared slot ledger, and concurrency closure

### 10.1 Behavior goal

original basenameのcase/spaces/Unicode/extension chainを可能な限り保ち、`NAME_MAX`内でdeterministicに正規化し、typed/blank/generic全familyのslotを共有してcooperative/non-cooperative concurrencyでもoverwriteしない。

### 10.2 Trace

- Requirements: `I345-RQ-005`〜`I345-RQ-007`, `I345-RQ-008`
- Designs: `DES-345-003`, `DES-345-004`
- Acceptance: `I345-AC-006`〜`I345-AC-009`, `I345-AC-017`
- Closures: `CL-AC-006`〜`009`, `017`; `CL-EC-007`〜`012`; `CL-CON-004`, `006`

### 10.3 Target files and symbols

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/artifacts.py`: `GenericImportedArtifactFilename`, `parse_generic_imported_artifact_filename`, normalizer, `ArtifactSlot`, shared scanner/allocator。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_artifact_doc.py`: existing allocator integration only if shared ledger requires; legacy output unchanged。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_artifact.py`: existing chatgpt-output allocation compatibility if shared ledger extraction changes call site。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_file_artifact.py`: read-only setup preflight→slot allocation→setup apply ordering、fresh-target `PC_NAME_MAX` verification、bounded race retry、monotonic cleanup aggregation/exhaustion mapping。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/binary_artifact_publisher.py`: parent/artifacts FD limit lookup、no-replace race result contract。
- domain/application/CLI concurrency tests and existing new/chatgpt tests。

### 10.4 Planned contract

- Scope: parser/formatter、normalization matrix、direct-child ledger、cross-family collision、exhaustion、concurrency。
- Red evidence: `red-required` for each public grammar/budget/race behavior; existing typed/blank tests as characterization。
- Green verification: S03 commands and legacy/new artifact regressions。
- Refactor guardrail: do not alter existing `ArtifactFilename` result or filenames; scan names/types only; no body read。
- Amendment trigger: suffix range/delimiter/public ID change、content/title-derived naming、existing file migration、lock/no-replace semantic change。

### 10.5 Red → Green → Refactor

1. generic parser/roundtrip、platform-aware basename、fresh/existing target `PC_NAME_MAX` matrixをRedにする。
2. separate parser/formatter/normalizerをGreenにする。
3. shared ledger mixed-family/exhaustion testsをRedにする。
4. direct-child name/type scannerとallocatorをGreenにし、existing allocatorsをprojectionとしてadaptする。
5. cooperative/non-cooperative race、attempt cleanup aggregation、fresh setup exhaustion mutation-free testsをRedにする。
6. create lock + read-only setup preflight + destination_exists rescan bounded retry + monotonic cleanup mergeをGreenにする。
7. scanner/normalizer private helpersをtidyし、typed/blank/new/chatgpt regressionsを再実行する。

### 10.6 Step-local verification commands

```bash
uv run pytest tests/unit/domain/test_artifacts.py
uv run pytest tests/unit/application/test_import_file_artifact.py -k 'name or slot or collision or exhaustion or concurrent'
uv run pytest tests/cli_runtime/test_artifact_import_file.py -k 'name or collision or concurrent or exhaustion'
uv run pytest tests/cli_runtime/test_artifact_import_chatgpt_output.py -k 'coexist or collision'
uv run pytest tests/cli_runtime/test_runtime_new_doc_s09.py
```

`tests/cli_runtime/test_runtime_new_doc_s09.py`が指定 HEADで別名/不存在なら、current new-artifact focused surfaceをrepository searchで特定し、置換理由をreportに記録する。test omissionにはしない。

### 10.7 Delegation contract

- **delegated role**: `dev-coder` with domain/concurrency focus。
- **input docs**: main workflowで採用・fresh reviewされたcanonical R/D/P、ADR filename decisions、current `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/artifacts.py`, create/import use cases、current allocator tests、S01/S02 evidence。
- **allowed paths**: §10.3 provider files and focused tests。
- **forbidden changes**: typed/blank grammar/result変更、existing Artifact rename/migration、body read、suffix >99、random/hash-based filename、overwrite fallback。
- **acceptance criteria**: all normalization/slot/race closures Green; direct child name-only scan; existing families unchanged。
- **required tests**: §10.6 and full touched domain/application test files。
- **reviewer focus**: UTF-8 byte boundary、extension preservation、reserved names、symlink/type inventory、lock scope、no-replace retry、bounded attempts。
- **stop conditions**: `NAME_MAX`取得不能をunsafe defaultで隠す必要、existing grammar change、generic identityにcontent hash/titleが必要、slot sharingがparent contractと矛盾。
- **output required**: algorithm summary、test matrix、race evidence、changed symbols、Red/Green/Refactor、Ledger Note、report summary。

### 10.8 具体テストケース一覧

- `tc-s03-001` acceptance: generic parser/formatter round-trip is separate from typed/blank
  - 前提: standard/suffix generic names、typed/blank names、malformed `--` namesを用意する。
  - 操作:three parsersへ各nameを渡す。
  - 期待結果:valid genericだけnew parserにmatchしfull basename IDを返す。typed/blank returnはunchanged。
  - 失敗検出:typed `file` token化、generic Markdownのtyped昇格、parser ambiguityを検出する。
  - 検証方法:domain parametrized unit test。
  - 関連 closure id: `CL-AC-006`

- `tc-s03-002` acceptance: safe basename preserves case, spaces, Unicode, and extension chain
  - 前提: `Report FINAL.PDF`, `archive.tar.gz`, extensionless, `.env`, CJK, combining mark, emoji, case variants、POSIXでbackslashを含むbasenameを用意する。
  - 操作:normalizerを十分なbyte budgetで実行する。
  - 期待結果:path safety変更が不要なinputはbyte-for-byte basenameを保持し、Linux/macOSではbackslashも保持し、content/title/slugを参照しない。
  - 失敗検出:lowercase、slugify、space collapse、Unicode normalization、extension lossを検出する。
  - 検証方法:domain exact-string tests。
  - 関連 closure id: `CL-AC-007`, `CL-EC-007`

- `tc-s03-003` boundary: unsafe and overlong names normalize deterministically within NAME_MAX
  - 前提: control/実platform separator/reserved/trailing dot-space、multi-byte overlong stem/extension、mocked small `PC_NAME_MAX`を用意する。fresh targetではparent FD limitと作成後artifacts FD limitの一致/取得不能/不一致seamを用意する。
  - 操作:max `-99--` prefix budgetでnormalize/formatする。
  - 期待結果:deterministic platform-aware minimal replacement、nonempty/non-dot result、code point intact、formatted component bytes <= limit、extension chain最大保持。fresh targetはlimit再確認後だけpublishする。
  - 失敗検出:ENAMETOOLONG、broken UTF-8、empty/dot path、aggressive slugificationを検出する。
  - 検証方法:domain byte-length/property matrix; exact expected examplesも固定。
  - 関連 closure id: `CL-AC-007`, `CL-EC-008`, `CL-EC-009`

- `tc-s03-004` acceptance: typed, blank, generic share one timestamp/suffix ledger
  - 前提:fixed timestampでtyped standard、blank `-01`、generic `-02`をdirect childrenとして用意する。
  - 操作:new generic、new typed、chatgpt-output allocationを順に実行する。
  - 期待結果:各familyがnext free shared slotを得て、existing entries/contentは不変。
  - 失敗検出:extension-only scan、family-local slot、legacy parser/result changeを検出する。
  - 検証方法:domain ledger unit + CLI coexist regression。
  - 関連 closure id: `CL-AC-008`, `CL-AC-017`, `CL-EC-010`

- `tc-s03-005` negative: suffix exhaustion is bounded and mutation-free
  - 前提:standardと`01..99`全slotをmixed familiesで占有しsource sentinelを用意する。
  - 操作:同timestampでgeneric importする。
  - 期待結果:`artifact_slot_exhausted`, `not_committed`, source/entries unchanged, no temp/formal destination、fresh targetでは`artifacts/`/rules setupも未作成。
  - 失敗検出:`100`以上のsuffix、overwrite、infinite retry、partial setupを検出する。
  - 検証方法:application/CLI fixed-clock test with timeout guard。
  - 関連 closure id: `CL-AC-008`, `CL-EC-011`

- `tc-s03-006` concurrency: cooperative imports receive distinct identities
  - 前提:same target/timestampへ複数threads/processes、shared create lock、different payloadsを用意する。
  - 操作:barrierから同時にgeneric importを開始する。
  - 期待結果:all successful results have distinct slots、each destination matches corresponding source、overwriteなし。
  - 失敗検出:lock scope不足、duplicate slot、payload cross-writeを検出する。
  - 検証方法:application/CLI concurrency test; platform flakesを避けるdeterministic barrier。
  - 関連 closure id: `CL-AC-009`, `CL-EC-012`, `CL-CON-004`

- `tc-s03-007` concurrency: non-cooperative destination race is handled by no-replace and rescan
  - 前提:applicationがcandidate選択後、publication直前にexternal actorがsame basenameをsentinel contentで作る。先行attemptのowned-temp cleanupを`removed`/`retained`へ分岐できるfault seamを用意する。
  - 操作:publisher barrierをreleaseし、同じapplication-owned source lease/FDでimportを続ける。retained後successとretained後retry exhaustionを別caseで実行する。
  - 期待結果:sentinelは不変、first attemptは`destination_exists`、use caseはnext slotへretryし一回だけcommitする。leaseは全体で一度だけclose。全attempt cleanupは`retained > removed > not_created`でmergeし、successは`temp_cleanup_retained / committed_with_warning`、exhaustionは`cleanup_state=retained`を保持する。
  - 失敗検出:precheck-then-overwrite、formal destination置換、retry without rescan、source reopen/double-close、先行retained state喪失を検出する。
  - 検証方法:infra/app barrier test with exact destination set/content assertion。
  - 関連 closure id: `CL-AC-009`, `CL-EC-012`, `CL-CON-004`, `CL-CON-006`

### 10.9 Step closure contract

- parser/normalizer/ledger/concurrency closures Green。
- existing typed/blank/chatgpt allocation characterization Green。
- race tests deterministic and repeatable。
- no current Artifact migration/diff。

### 10.10 Report evidence destination

- `report.md / Step Contract Closure / S03`
- `report.md / Test Contract Closure / S03`
- `report.md / Naming and Slot Ledger Matrix`
- `report.md / Concurrency Evidence`
- `report.md / Delegated Worker Evidence / S03`

### 10.11 Commit candidate

```text
feat(artifact): generic naming と shared slot を完成
```

## 11. S04 — Opaque lifecycle and compatibility closure

### 11.1 Behavior goal

generic Artifactのnameはinventory/slot目的で認識してもbodyはdefault lifecycleでopen/decodeせず、ADR/spec/delegated draftへ昇格しない。同時にexisting `chatgpt-output`, typed, blank behaviorを固定する。

### 11.2 Trace

- Requirements: `I345-RQ-011`, `I345-RQ-013`
- Designs: `DES-345-006`
- Acceptance: `I345-AC-014`, `I345-AC-016`, `I345-AC-017`
- Closures: `CL-AC-014`, `016`, `017`; `CL-EC-017`, `019`; `CL-CON-008`

### 11.3 Target files and symbols

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/artifacts.py`: valid genericをmalformed typed候補から除外、name-only inventory。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py` / `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/validate_tree.py`: actual failing test が示す最小 change のみ。
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`: `_collect_adr_mirror_sources` name gate。
- dependency/context/authoring modules: body-read spyが actual call を示した場合だけ変更。
- tests: new generic lifecycle tests + existing chatgpt-output/new artifact/sync/ADR/deps/context/authoring tests。

### 11.4 Planned contract

- Scope: validate/sync/deps/context/ADR/authoring no-read、projection equivalence、legacy regressions。
- Red/alternative evidence: `red-required` body-open spy and invalid UTF-8 tests; unchanged consumers may be `covered-existing` only after spy proves no read。
- Green verification: S04 commands。
- Refactor guardrail: generic bodyのschema/frontmatter validationを追加しない。root genericをgraph scopeに追加しない。
- Amendment trigger: default consumerがgeneric contentを必要とする、generic MarkdownをADR/typed扱いする、legacy result/grammar changeが必要。

### 11.5 Red → Green → Refactor

1. invalid UTF-8/ADR-looking generic bodyを用いたbody-open denial testsをRedにする。
2. generic parserをmalformed/typed discoveryの前に適用し、name-only ignoreをGreenにする。
3. projection/deps/context/mirror before/after equivalenceをGreenにする。
4. existing chatgpt-output/typed/blank suitesをfull focusedで実行し、regressionがあればgeneric pathだけを修正する。
5. duplicated name filtersをshared predicateへtidyするが、consumer-specific semanticsは統合しすぎない。

### 11.6 Step-local verification commands

```bash
uv run pytest tests/unit/domain/test_artifacts.py -k 'generic or malformed or opaque'
uv run pytest tests/cli_runtime/test_artifact_import_file.py -k 'validate or sync or deps or context or adr or authoring or opaque'
uv run pytest tests/cli_runtime/test_artifact_import_chatgpt_output.py
uv run pytest tests/cli_runtime/test_artifact_import_s04.py
uv run pytest tests/unit/commands/test_artifact_import_chatgpt_output.py
uv run pytest tests/unit/presentation/test_artifact_import_chatgpt_output.py
```

Nearest dedicated sync/deps/context/authoring tests discovered at execution must be added to this command set and recorded in report。

### 11.7 Delegation contract

- **delegated role**: `dev-coder` with lifecycle/regression focus。
- **input docs**: main workflowで採用・fresh reviewされたcanonical R/D/P、ADR Decision 7、current validation/sync/deps/context/authoring source、S01-S03 diff/evidence、legacy test suites。
- **allowed paths**: §11.3のactual affected provider modulesとfocused tests。body-open testがpassするunaffected moduleは変更しない。
- **forbidden changes**: generic body parser、frontmatter/MIME decode、default projection inclusion、root graph node、legacy command/result変更、broad lifecycle rewrite。
- **acceptance criteria**: all no-read/equivalence/legacy closures Green; invalid UTF-8 generic causes no decode failure; ADR mirror unchanged。
- **required tests**: §11.6 + discovered nearest focused tests。
- **reviewer focus**: filter-before-read ordering、generic `.md` malformed interaction、authority isolation、absence of unnecessary changes。
- **stop conditions**: consumer requirement needs body read、accepted ADR conflict、generic file must become typed/ADR、large unrelated lifecycle refactor required。
- **output required**: body-open call graph/evidence、changed paths、before/after projection digest/equivalence summary、legacy test output、Ledger Note、report summary。

### 11.8 具体テストケース一覧

- `tc-s04-001` security: default lifecycle never opens generic body
  - 前提:all target kindsにgeneric filesを置き、`Path.open/read_text/read_bytes` spyがそのpathsだけでfailするようにする。
  - 操作:`validate`, `sync --no-github`, deps/context, ADR collection, authoring discoveryのunit/application entryを実行する。
  - 期待結果:generic path へのbody-open call 0、operationsはname-only policyに従う。
  - 失敗検出:extension/frontmatter probingやgeneric default discoveryを検出する。
  - 検証方法:monkeypatch spy tests in nearest unit surfaces。
  - 関連 closure id: `CL-AC-014`, `CL-CON-008`

- `tc-s04-002` acceptance: invalid UTF-8 generic Markdown does not affect validate/sync projections
  - 前提:typed projection/ADR baselineとinvalid UTF-8 generic `.md`を用意する。
  - 操作:generic追加前後で`validate`と`sync --no-github`を実行しgenerated outputsをnormalize比較する。
  - 期待結果:decode errorなし、node/index/tree/dashboard/deps outputsとtyped ADR mirror setがbaseline同等。
  - 失敗検出:generic body decode、default projection inclusion、mirror contaminationを検出する。
  - 検証方法:CLI runtime before/after artifact comparison。
  - 関連 closure id: `CL-AC-014`, `CL-EC-017`

- `tc-s04-003` authority: ADR-looking generic file is not mirrored or discovered
  - 前提:generic basename/bodyにaccepted ADR風frontmatterとauthority sentinelを入れる。
  - 操作:sync/ADR mirror/authoring discoveryを実行する。
  - 期待結果:mirror symlink/candidate/provenance増加なし、body未読、authority state不変。
  - 失敗検出:generic Markdownのtyped ADR/delegated draft昇格を検出する。
  - 検証方法:mirror directory/candidate list/open spy exact assertions。
  - 関連 closure id: `CL-AC-014`, `CL-EC-017`, `CL-CON-008`

- `tc-s04-004` regression: chatgpt-output public contract is unchanged
  - 前提:current legacy test fixturesとexisting expected payloadsを維持する。
  - 操作:unit/presentation/CLI/S04 legacy suitesを実行する。
  - 期待結果:Workbench-only lowercase `.md`, title/slug, blank naming, source/hash/count result, warning tokensがcurrent contractどおり。
  - 失敗検出:generic guard/DTO/parser/rendererのlegacy混入を検出する。
  - 検証方法:existing focused test filesを変更理由レビュー付きで実行。
  - 関連 closure id: `CL-AC-016`, `CL-EC-019`

- `tc-s04-005` regression: typed/blank new artifact and existing files require no migration
  - 前提:existing typed/blank/legacy artifactsとfixed-clock new artifact fixtureを用意する。
  - 操作:generic code導入後にnew typed/blank作成、validate/syncを実行する。
  - 期待結果:existing filenames/content不変、new identitiesはlegacy grammar、shared slotsだけがcollision時に反映。
  - 失敗検出:parser return change、existing rename、generic delimiter混入を検出する。
  - 検証方法:current new artifact focused tests + filesystem before/after snapshot。
  - 関連 closure id: `CL-AC-017`

### 11.9 Step closure contract

- no-read spy、invalid UTF-8、ADR-looking、projection equivalence Green。
- complete legacy focused suites Green。
- changed lifecycle files are only those justified by failing tests。
- authority state/provenance diffなし。

### 11.10 Report evidence destination

- `report.md / Step Contract Closure / S04`
- `report.md / Test Contract Closure / S04`
- `report.md / Opaque Lifecycle Matrix`
- `report.md / Compatibility Regression Evidence`
- `report.md / Delegated Worker Evidence / S04`

### 11.11 Commit candidate

```text
fix(artifact): generic Artifact を lifecycle から隔離
```

## 12. S90 — Docs impact resolution, root rules, and provider/managed-file parity

### 12.1 Behavior goal

shipped docs/rules/helpがimplemented contractを説明し、provider filesをauthorityとしてmanaged dogfood projectionへ反映する。evidence-only/authority/Issue 346 boundaryを明記する。

### 12.2 Trace

- Requirements: `I345-RQ-012`, `I345-RQ-014`, `I345-RQ-015`
- Designs: `DES-345-002`, `DES-345-007`
- Acceptance: `I345-AC-015`, `I345-AC-018`, `I345-AC-019`
- Closures: `CL-AC-015`, `018`, `019`; `CL-EC-018`; `CL-CON-009`, `010`, `011`

### 12.3 Target files

Provider first:

- `src/spec_dock/assets/spec_dock/docs/rules/root/artifacts.md` (new)
- `src/spec_dock/assets/spec_dock/docs/README.md`
- `src/spec_dock/assets/spec_dock/docs/guide.md`
- `src/spec_dock/assets/spec_dock/docs/reference_naming.md`
- related provider rules/reference files only when links require。
- CLI help source already changed inS01。

Managed projection after provider review:

- corresponding managed files under `spec-dock/docs/`
- corresponding managed files under `spec-dock/scripts/spec_dock_runtime/`

### 12.4 Planned contract

- docs-only verification: command examples、target/source/naming/privacy/state/opaque/compatibility/authority/346 defer。
- root rules: generic body authorityなし、rules symlink behavior、no body parsing。
- projection: provider-first via repository-approved update flow; exact changed paths parity。
- no candidate-wheel consumer E2E/integrated dogfood/full regression。
- amendment trigger:docs require product choice absent from R/D/P or update flow changes unmanaged files materially。

### 12.5 Red → Green → Refactor / alternative evidence

1. **Inspect-first**: current docs searchでmissing command/root/generic privacy termsをrecordする。
2. **Red structural**: doc link/required heading/root rules source existence assertionsを追加またはscripted grepでfailを保存する。
3. **Green**: provider docs/rulesを更新。
4. **Projection**: `spec-dock update .`等repository-approved flowでmanaged dogfood filesをrefreshし、changed-path parityを確認。
5. **Refactor**: duplicated proseをreferenceへ集約し、help/example/token spellingをcodeと一致させる。

### 12.6 Step-local verification commands

```bash
uv run pytest tests/cli_runtime/test_artifact_import_file.py -k 'help or root'
test -f src/spec_dock/assets/spec_dock/docs/rules/root/artifacts.md
rg -n 'artifact import file|canonical=false|committed_with_warning|retry.*not_needed' \
  src/spec_dock/assets/spec_dock/docs
spec-dock update .
git diff --check
git diff -- src/spec_dock/assets/spec_dock spec-dock
```

`test`、`rg`、update、diff のいずれかが失敗した場合は、その失敗を無視せず step blocker として `report.md` に記録する。既存の `tests/unit/infra/test_init_update.py` suiteへroot rulesのinit/update parity assertionを追加し、focused testとして実行する。存在だけを根拠にdocs/install verificationを通過扱いせず、追加したexact test nodeと結果を`report.md`のTest Contract Closureに記録する。

### 12.7 Delegation contract

- **delegated role**: `doc-writer` for provider docs/rules。parent Codexがprojection commandとdiff integrationを所有。
- **input docs**: main workflowで採用・fresh reviewされたcanonical R/D/P、accepted ADR、implemented CLI/result tokens、AGENTS provider-first rule、S01-S04 evidence。
- **allowed paths**: §12.3 provider docs/rules; projectionでは対応managed filesだけ。
- **forbidden changes**: product behavior/code、canonical Issue/Epic docs/report authority、assurance files、unrelated consumer data、Issue 346 execution、full regression/PR claims。
- **acceptance criteria**: docs complete/link-valid/token-consistent; root rules exists; provider/projection parity; evidence-only and scope defer explicit。
- **required verification**: §12.6をactual test pathsへ確定、doc link/check commands、changed-path byte comparison where expected。
- **reviewer focus**: docs/code consistency、external privacy wording、warning retry wording、generic vs Workbench distinction、provider-first diff。
- **stop conditions**: docs reveal unresolved product choice、update rewrites active/canonical data unexpectedly、projection cannot be attributed to provider changes、authority wording conflict。
- **output required**: changed docs、source-to-projection map、verification output、unresolved link risks、Ledger Note、report summary。

### 12.8 具体テストケース一覧

- `tc-s90-001` docs/rules: root Artifact rules are shipped and safely referenced
  - 前提:provider asset treeとfresh initialized consumer fixtureを用意する。
  - 操作:provider update/init後にroot importを行い`docs/rules/root/artifacts.md`と`artifacts/rules.md`を検査する。
  - 期待結果:rules sourceはregular shipped file、root rules symlinkはcorrect relative target、generic evidence-only/opaque policyを説明する。
  - 失敗検出:missing source、wrong/broken symlink、node rule流用、authority昇格文言を検出する。
  - 検証方法:installer/update fixture + root CLI test + link inspection。
  - 関連 closure id: `CL-AC-015`, `CL-EC-018`

- `tc-s90-002` projection: provider and managed dogfood files remain in parity
  - 前提:S01-S04 provider changesがGreenでworktree diffが把握されている。
  - 操作:repository-approved update flowを実行し、corresponding runtime/docs filesを比較する。
  - 期待結果:managed projectionはprovider contentと一致し、unrelated active specs/customer dataを変更しない。
  - 失敗検出:consumer-first edits、projection drift、broad update side effectsを検出する。
  - 検証方法:changed-path manifest + byte/hash comparison + `git diff --check`。
  - 関連 closure id: `CL-AC-018`, `CL-CON-009`

- `tc-s90-003` authority: docs make evidence-only and retry semantics explicit
  - 前提:all changed docs/help/output samplesを収集する。
  - 操作:required termsとforbidden authority claimsをstructural scanしhuman-readable reviewする。
  - 期待結果:`canonical=false`, evidence-only, `committed_with_warning` retry not needed, Issue 346 deferが明示され、adopted/reviewed/ready/merge claimsがない。
  - 失敗検出:import receiptをadoption/readinessと誤認させる文言を検出する。
  - 検証方法:grep/scripted assertions + spec-reviewer docs alignment focus。
  - 関連 closure id: `CL-AC-019`, `CL-CON-010`, `CL-CON-011`

- `tc-s90-004` documentation: newcomer can distinguish file import from chatgpt-output
  - 前提:README/guide/naming referenceのrendered Markdownを用意する。
  - 操作:command examples、source policy、result fields、compatibility tableをinspection checklistで読む。
  - 期待結果:generic arbitrary fileとWorkbench Markdown flowの違いが、未定義略語なしで説明される。
  - 失敗検出:title/slug、external policy、hash/count resultの混同を検出する。
  - 検証方法:doc-writer self-check + independent spec-reviewer focus。
  - 関連 closure id: `CL-AC-016`, `CL-AC-018`

### 12.9 Step closure contract

- provider docs/rules complete。
- root rules、docs token、update/projection checks passし、failureを無視する shell guard は存在しない。
- managed projection diff is scoped and attributable。
- docs/spec alignment review evidence recorded。

### 12.10 Report evidence destination

- `report.md / S90 Docs Impact Resolution`
- `report.md / Provider-Dogfood Projection Evidence`
- `report.md / Delegated Worker Evidence / S90`
- `report.md / Authority Wording Self-Check`

### 12.11 Commit candidate

```text
docs(artifact): 汎用 file import と root rules を反映
```

## 13. S99 — Final local quality gate, rollback, and Issue 346 handoff

### 13.1 Goal

Issue 345 ownership内のfocused/default local evidenceを統合し、closure delta、rollback、review findings、deferred delivery boundaryをreportへ残す。Issue 346のworkを実行または完了扱いしない。

### 13.2 Entry criteria

- S01〜S04, S90 step gatesがreport evidence付きでclosed candidate。
- no unresolved required closure row。
- provider assetと対応するmanaged fileのscoped parity diffを分類する。
- material design deviationなし、またはapproved amendmentがある。
- assurance/reviewer obligationsがruntime workflowに従って満たされるまでexecution-readyを主張しない。

### 13.3 Local verification queue

Focused commands:

```bash
uv run pytest tests/unit/domain/test_artifacts.py
uv run pytest tests/unit/application/test_import_file_artifact.py tests/unit/commands/test_artifact_import_file.py
uv run pytest tests/unit/infra/test_binary_artifact_publisher.py
uv run pytest tests/unit/presentation/test_artifact_import_file.py
uv run pytest tests/cli_runtime/test_artifact_import_file.py
uv run pytest tests/cli_runtime/test_artifact_import_chatgpt_output.py tests/cli_runtime/test_artifact_import_s04.py
```

Default/local gates:

```bash
make lint
uv run pytest
git diff --check
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync --no-github
```

- ordinary `uv run pytest`はdefault policy laneであり、`--run-full-regression`を付けない。
- `uv run pytest -m full_regression`だけをpermissionとして使わない。
- opt-in full regressionはIssue 346へdeferする。
- active/canonical authoring gate未完で`validate`がblockする場合、block reasonを正確にreportし、feature test passへ読み替えない。

### 13.4 Review / QA gate policy

Issue 345 local gate候補:

- step-local `code-reviewer` after each code slice。
- security/privacy/concurrency focus review after S02/S03。
- docs/spec alignment review after S90。
- issue-wide code review against exact HEAD after integration。
- local QA review of focused/default evidence、rollback、known platform limitations。
- fresh spec review of canonical docsはChatGPT evidence adoption後のmain workflowが所有。

Epic-wide final review、consumer-wheel E2E、integrated dogfood、full regression、PR deliveryはIssue 346。

### 13.5 Delegation / reviewer contract

- **delegated roles**: `qa-reviewer` for local evidence sufficiency、`code-reviewer` for exact integrated diff、`spec-reviewer` forcanonical R/D/P only after adoption。parent Codex aggregates verdicts。
- **input docs**: adopted canonical R/D/P、all step report evidence、exact integrated HEAD/diff、Issue 346 scope。
- **allowed paths**: read-only review; fixes return to owner step and allowed paths。report updates are parent-owned。
- **forbidden changes**:reviewer self-fix without handoff、scope expansion、full regression execution、PR/merge/issue-finish claim、assurance mutation。
- **acceptance criteria**: all required closure rows haveevidence; no unresolved blocker; rollback andprivacy/fault matrices reviewed;defer list exact。
- **required tests**: §13.3; reviewer may request focused rerun but not silently waive failures。
- **reviewer focus**: observable contracts、no overwrite、privacy、postcommit retry、opaque lifecycle、legacy compatibility、provider parity、scope boundary。
- **stop conditions**: test failure、stale HEAD、unreviewed material change、missing platform evidence、closure gap、authority conflict、scope leakage。
- **output required**: structured verdict/findings with exact files/tests/closure IDs; parent records status without claiming unavailable gate passed。

### 13.6 具体テストケース一覧

- `tc-s99-001` quality: focused and ordinary default lanes are Green on exact integrated HEAD
  - 前提:all owner steps integrated、working tree/diff classified、exact HEAD recorded。
  - 操作:§13.3 focused commands、`make lint`, ordinary `uv run pytest`, diff checkを実行する。
  - 期待結果:all required commands pass, or an exact blocker is recorded; policy-skipped full regression is not reported as run。
  - 失敗検出:partial suite、stale HEAD result、full-regression permission誤用を検出する。
  - 検証方法:command/stdout/exit/HEAD evidenceをreport Test Contract Closureへ記録。
  - 関連 closure id: `CL-AC-018`

- `tc-s99-002` rollback: additive feature can be disabled without rewriting imported evidence
  - 前提:generic imported file、legacy chatgpt-output/typed/blank baseline、step commit candidatesを用意する。
  - 操作:additive generic changesをtest branch/worktreeでrevertまたはfeature removal diffとしてsimulateしlegacy focused testsを実行する。
  - 期待結果:legacy flows Green、existing generic evidence filesはrename/deleteされず、commandだけunavailableになる。
  - 失敗検出:rollback migration/data deletion、legacy core couplingを検出する。
  - 検証方法:disposable worktree/revert rehearsalまたはreviewed inverse-diff inspection;実行不可なら理由と残riskをreport。
  - 関連 closure id: `CL-AC-016`, `CL-AC-017`

- `tc-s99-003` handoff: Issue 346 obligations remain open and explicit
  - 前提:parent Candidate 3 scopeとIssue 345 reportを並べる。
  - 操作:candidate-wheel E2E、integrated dogfood、opt-in full regression、Epic reviews、residual PRのevidence statusをinspectする。
  - 期待結果:各項目は`deferred to iss-00346`であり、Issue 345 pass/complete evidenceとして数えられない。
  - 失敗検出:final-quality scopeの先取り、missing handoff、PR-ready/merge-ready誤主張を検出する。
  - 検証方法:report handoff checklist + reviewer scope audit。
  - 関連 closure id: `CL-CON-010`

- `tc-s99-004` authority/privacy: final diff contains no forbidden claims or leaked source data
  - 前提:integrated code/docs/tests/report diffとprivacy sentinelsを収集する。
  - 操作:forbidden authority phrases、absolute/parent path、body/hash/count/MIME/encoding provenanceをscanしreviewする。
  - 期待結果:public/tracked surfacesはevidence-only boundaryを守り、authorized profileは変更されない。
  - 失敗検出:implementation receiptからadoption/readiness/assuranceを暗黙推論する文言とprivacy leakを検出する。
  - 検証方法:structural grep、exact JSON tests、git diff inspection、spec/code reviewer focus。
  - 関連 closure id: `CL-AC-019`, `CL-CON-002`, `CL-CON-011`

### 13.7 Report evidence destination

- `report.md / Final Local Quality Gate`
- `report.md / Reviewer Gate Status`
- `report.md / Rollback Evidence`
- `report.md / Closure Delta`
- `report.md / Deferred PR Delivery Gate`
- `report.md / Issue 346 Handoff`
- `report.md / Final Authority and Privacy Self-Check`

### 13.8 Commit candidate

- test/reviewでcode fixが生じた場合はowner stepへ戻してそのcommit candidateを更新する。
- evidence/docsだけのfinal deltaがある場合の候補:

```text
test(artifact): Issue 345 の local closure evidence を固定
```

no-opの場合はcommitを捏造せず、approved-no-op evidenceをreportへ記録する。

## 14. Fault injection matrix

| Injection point | Expected public state | Formal destination | Retry | Owner step |
|---|---|---|---|---|
| source open / eligibility | `not_committed` | absent | safe after remediation | S02 |
| temp create | `not_committed` | absent | safe after remediation | S02 |
| copy/write | `not_committed` | absent | safe after remediation | S02 |
| file fsync | `not_committed` | absent | safe after remediation | S02 |
| staged hash/read | `not_committed` | absent | safe after remediation | S02 |
| source changed | `not_committed` | absent | safe after remediation | S02 |
| capability probe | `not_committed` | absent | safe after remediation | S02 |
| destination parent identity | `not_committed` | absent | safe after remediation | S02 |
| destination exists race | internal retry | existing entry unchanged | bounded retry | S03 |
| no-replace non-race fault | `not_committed` | absent | safe after remediation | S02 |
| directory fsync after commit | `committed_with_warning` | present | not needed | S02 |
| owned temp cleanup after commit | `committed_with_warning` | present | not needed | S02 |
| create lock release after commit | `committed_with_warning` | present | not needed | S02 |

## 15. Compatibility matrix

| Surface | Issue 345 expected | Evidence owner |
|---|---|---|
| `artifact import file` | new generic command | S01-S04 |
| `artifact import chatgpt-output` | unchanged Workbench Markdown contract | S01 smoke, S04 full focused |
| `new artifact` typed/blank | unchanged grammar/result; shared slot aware | S03/S04 |
| Workbench shell/copy | unchanged | S04 regression/inspection |
| validate/sync/deps/context/ADR/authoring | generic body ignored/unopened | S04 |
| root graph/deps | unchanged; no root node | S01/S04 |
| provider vs dogfood | managed parity | S90/S99 |

## 16. Provider / dogfood projection policy

1. edit the relevant provider files under `src/spec_dock/assets/spec_dock/` first。
2. run focused provider tests before projection。
3. use the repository-approved update flow for corresponding managed files under `spec-dock/`。
4. compare only expected managed counterparts and classify additional diff。
5. do not manually make dogfood code authoritative。
6. do not call this integrated dogfood; Issue 346 owns end-to-end consumer/dogfood final evidence。

## 17. Issue 346 handoff contract

Issue 345 report must leave the following explicitly open:

- candidate wheel built from exact integrated provider revision。
- fresh consumer repository initialized/updated from that wheel。
- consumer E2E for root/Initiative/Epic/Issue、external/cross-FS、privacy、warning states。
- integrated dogfood across Issue 344 Workbench shell + Issue 345 generic import。
- `uv run pytest --run-full-regression` or repository-authorized equivalent。
- Epic-wide spec/code/QA/decision review。
- residual Epic integration branch/PR、PR Delivery Gate、Merge Preparation Gate。
- human merge decision。

Handoff payload:

- exact Issue 345 integrated SHA。
- provider changed-path manifest。
- focused/default commands and results。
- known platform capability matrix/skips。
- unresolved risks/waivers (if any)。
- rollback notes。
- public tokens/CLI examples。
- explicit statement that no candidate-wheel/integrated/full/Epic final claim was made by Issue 345。

## 18. Plan amendment triggers

実装を止めてplan/design/ADRへ戻す条件:

- required closure expectationを変更/削除する必要。
- fixed ADR decision変更。
- new public field/tokenがprivacy/identity/retry contractへ影響。
- root graph node化。
- legacy command contract変更。
- generic body read/semantic inclusion。
- unsafe filesystem fallback。
- cross-family slotを共有できない。
- `NAME_MAX`を安全に取得/適用できない。
- Issue 346 scopeを前倒ししないとclosureできない。
- authorized profile mutationが必要。
- platform-specific behaviorがparent supported matrixと矛盾。

## 19. Final Exit Contract

Issue 345のlocal implementation candidateがhandoff可能と判断されるための必要条件。これはIssue finish、PR delivery、merge-ready、Epic completionを意味しない。

1. `I345-AC-001`〜`019`、`I345-EC-001`〜`019`、`I345-CON-001`〜`011`のrequired closure evidenceがreportにある。
2. S01〜S04、S90、S99のstep gatesがexact integrated HEADに対して記録される。
3. focused tests、ordinary default tests、lint/diff checksがpassし、未実行/skip/blockは正確に区別される。
4. privacy sentinel、fault injection、concurrency、opaque lifecycle、legacy compatibility evidenceがある。
5. provider assetと対応するmanaged fileだけがscoped/parity-checkedである。integrated dogfoodは主張しない。
6. rollback evidenceまたは明示した未検証riskがある。
7. no unresolved material design deviation。
8. authorized profileはruntime-owned stateのまま、本実装/ChatGPT outputが変更していない。
9. Issue 346 handoff obligationsがopen/deferredとして明記される。
10. main orchestratorによるEvidence Adoption Ledger、canonical rewrite、fresh reviewer gate等のauthoring authority workflowが別途完了するまでexecution/delivery claimをしない。
