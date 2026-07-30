---
種別: "実装計画書（Issue）"
ID: "iss-00346"
タイトル: "Integration, Distribution, and Final Quality Plan"
planning_method: "Spec-Locked Micro-Batch TDD"
関連GitHub: ["#346"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-31"
依存: ["requirement.md", "design.md", "epic-00343/plan.md"]
親: ["epic-00343", "init-local-00002"]
authorized_profile_observed: "standard"
classification_status: "runtime_classified"
---

# iss-00346 Integration, Distribution, and Final Quality — Issue 実装計画書（Standard）

## 0. 計画の位置づけ

本書は review 済みの canonical `requirement.md` と `design.md` を実行順の planned contract に変換する。fresh spec review と runtime readiness gate を満たした後にのみ implementation queue として使う。本書だけでは execution readiness、PR readiness、merge readiness、Issue/Epic completion を意味しない。

実行時は `plan.md` を planned contract、target Issue `report.md` を observed evidence ledger とする。Red/Green/Refactor、test output、discovered test、decision、reviewer verdict、commit/no-op、PR observation を本書へ書き戻さない。

## 1. 実行前の hard gate

次をすべて満たせない場合、S01 を開始しない。

1. canonical `requirement.md` / `design.md` / `plan.md` が本 candidate の採否を反映済みで、template-only ではない。
2. repository/branch/headを再確認し、planning baseline `2217889c31e1a8a83732c446264dec00dde77be6`とは別に、実行cycle開始時HEADをcandidate revisionとして記録する。
3. target report の Evidence Adoption Ledger に、candidate claim ごとの disposition がある。
4. fresh spec review、Spec Authoring Gate、runtime `guidance issue-execution` の report-evidence gate を確認する。
5. `deps check iss-00346` で Issue 344/345 dependency state を確認する。
6. named worker/reviewer、host/platform lane、temporary workspace、wheel build tool が利用可能である。
7. working tree の既存変更を inventory し、Issue 346 diff と混在させない。

実行中に requirement/design/ADR/cross-Issue ownership の変更が必要になった場合は、`I346-CON-002` / `I346-CON-003` に従い停止し、Epic planning repair へ戻る。

## 2. Execution policy

### 2.1 Spec-Locked Micro-Batch TDD

- `1 step = 1 observable vertical behavior slice` を基本とする。
- public interface / installed behavior / observable filesystem state から test を開始する。
- 既存 capability を統合検証する step では、`red-required` だけを形式的に要求せず、`covered-existing`、controlled negative control、mutation sensitivity、inspect-only を明示する。
- 一つの test case を Red または sensitivity confirmation → minimal Green → refactor guardrail の順で閉じる。
- production repair は failing closure を閉じる最小 path に限定する。
- step reviewer gate と commit-candidate/no-op gate を閉じるまで次 step の implementation を始めない。
- actual host evidence を hermetic simulation で代替しない。

### 2.2 Delegation boundary

- runtime/CLI/infra/tests/scaffold behavior: `dev-coder`。
- shipped docs/templates/skills/workflow text: `doc-writer`。
- Codex orchestrator: inspect、step handoff、diff integration、verification、report/EAL、review coordination、commit/push/PR preparation。
- `qa-reviewer`、`code-reviewer`、`spec-reviewer` は implementation worker と独立した fresh evidence を使う。
- worker は canonical requirement/design/plan/report を直接編集しない。worker は report 転記用 evidence と `Ledger Note` を返す。

### 2.3 Repair boundary

Allowed:

- wheel inventory/build defect の最小 package-data repair。
- installer/update no-backfill defect の最小 repair。
- Workbench + generic import の integration defect の最小 repair。
- accepted ADR 内での privacy/publication/lifecycle/compatibility defect の最小 repair。
- test harness 自身の誤りの test-only repair。

Forbidden:

- new major feature、広い architecture refactor、API redesign。
- missing Candidate 1/2 scope の吸収。
- parent requirement/design/ADR/ownership の Issue-local rewrite。
- Linux named-temp/visible-probe/pathname-cleanup fallback。
- macOS accepted trust boundary の拡張主張。
- human merge。

## 3. 依存関係から導く実装順序

```text
S01 Exact-source candidate wheel + fresh installed tracer
  -> wheel と public installed surface を固定
       |
       v
S02 Existing consumer update + no-backfill + future-only shell
  -> distribution update semantics を固定
       |
       v
S03 Four-target / external / cross-FS / Linux / macOS publication
  -> privacy と platform safety を installed surface で固定
       |
       v
S04 Opaque lifecycle + legacy compatibility + integrated dogfood
  -> two-feature integration と consumer isolation を固定
       |
       v
S90 Documentation impact / provider-dogfood parity / report trace
       |
       v
S99 Independent final quality / full regression / delivery gates
       |
       v
Human merge decision (agent stops before merge)
```

S01 の wheel は S02〜S04 の共通 input である。production/package repair により head が変わったら wheel を rebuild し、affected downstream evidence を再取得する。

## 4. Milestones

| Milestone | Steps | Observable closure candidate | Commit candidate |
|---|---|---|---|
| `M1 Distribution tracer` | S01 | exact wheel inventory と wheel-installed fresh shell/import が通る | test-only または package repair commit candidate |
| `M2 Update safety` | S02 | synthetic existing consumer が no-backfill、future node が shell を得る | installer/test repair commit candidate または reviewed no-op |
| `M3 Platform/privacy distribution` | S03 | 4 target、external/cross-FS privacy、Linux/macOS boundary が actual/ hermetic evidence で閉じる | infra/presentation/test repair candidate または reviewed no-op |
| `M4 Integrated consumer closure` | S04 | opaque lifecycle、legacy compatibility、dogfood no-backfill + import が閉じる | interaction/test repair candidate または reviewed no-op |
| `M5 Docs and final quality` | S90, S99 | docs/report parity、lint/fast/full/validate/sync、fresh reviews、delivery evidence | final commit/push candidate |

## 5. ステップ一覧

| Step | Behavior slice | Depends on | Primary role | Unblocks |
|---|---|---|---|---|
| `S01` | candidate revision から作った candidate wheel を isolated fresh consumer で実行する | execution hard gate | `dev-coder` | S02〜S04 |
| `S02` | valid existing consumer の update は no-backfill、future node は shell を得る | S01 | `dev-coder` | S04 |
| `S03` | installed generic import が target/privacy/platform boundary を守る | S01 | `dev-coder` + actual host evidence | S04, S99 |
| `S04` | opaque lifecycle、legacy compatibility、dogfood projection が一体で動く | S01〜S03 | `dev-coder` | S90, S99 |
| `S90` | docs impact、provider→dogfood parity、Issue/Epic report trace を解決する | S01〜S04 | `doc-writer` + orchestrator | S99 |
| `S99` | independent final quality、full regression、review、commit/push、PR gates | all | orchestrator + reviewers | human merge decision |

## 6. 要件 ↔ step 対応

| Requirement | Owner step |
|---|---|
| `I346-RQ-001`, `I346-RQ-002` | S01 |
| `I346-RQ-003` | S01 |
| `I346-RQ-004`, `I346-RQ-005` | S02 |
| `I346-RQ-006` | S04 |
| `I346-RQ-007`, `I346-RQ-008`, `I346-RQ-009` | S03 |
| `I346-RQ-010` | S04 |
| `I346-RQ-011`, `I346-RQ-012` | S03 |
| `I346-RQ-013` | S04 |
| `I346-RQ-014` | S90, S99 |
| `I346-RQ-015` | all step gates, final owner S99 |

## 7. Spec-Locked Closure Index

`Required=yes` の row を削除、意味変更、別 step へ黙って移動してはならない。spec change が必要なら plan amendment と fresh review を先に行う。Evidence level は planned minimum であり、actual evidence は `report.md` に記録する。

### 7.1 Acceptance closure

| Closure ID | Spec link | Observable locked expectation | Defect class guarded | Required | Evidence level | Owner |
|---|---|---|---|---|---|---|
| `CL-346-AC-001` | `I346-AC-001` | wheel/test receipt は exact observed head に束縛される | stale/mixed-revision evidence | yes | inspect + build receipt | S01, S99 |
| `CL-346-AC-002` | `I346-AC-002` | clean wheel の README allowlist 5件と denylist | missing shell / stale package contamination | yes | build + inventory automation | S01 |
| `CL-346-AC-003` | `I346-AC-003` | source checkout 非依存の fresh init/node/import | source-tree false positive / broken distribution | yes | isolated integration | S01 |
| `CL-346-AC-004` | `I346-AC-004` | existing 4 scope は update 後も README absent、data/payload 不変 | accidental backfill/data rewrite | yes | integration + snapshot | S02 |
| `CL-346-AC-005` | `I346-AC-005` | update 後 future Initiative/Epic/Issue に byte-identical README | feature unavailable after update | yes | integration | S02 |
| `CL-346-AC-006` | `I346-AC-006` | dogfood `epic-00343` は no-backfill、future shell + import は成功 | provider projection drift / hidden backfill | yes | disposable dogfood integration | S04 |
| `CL-346-AC-007` | `I346-AC-007` | root/init/epic/issue opaque import、source不変、no overwrite、canonical=false | target gap / overwrite / authority escalation | yes | CLI + installed integration | S03 |
| `CL-346-AC-008` | `I346-AC-008` | external/cross-FS は basename-only、path/body/digest/count/derived値なし | privacy disclosure / source-device coupling | yes | CLI + host + sentinel scan | S03 |
| `CL-346-AC-009` | `I346-AC-009` | binary/ZIP/invalid UTF-8/NUL を lifecycle が開かず projection 不変 | decode/semantic escalation/context contamination | yes | spy + lifecycle integration | S04 |
| `CL-346-AC-010` | `I346-AC-010` | actual Linux supported FS は anonymous stage + FD no-replace、visible stage 0 | unsafe named staging / race overwrite | yes | actual Linux host | S03 |
| `CL-346-AC-011` | `I346-AC-011` | Linux capability不足は formal destination前 fail closed、fallback/cleanup path 0 | unsafe fallback / false commit | yes | hermetic + actual where available | S03 |
| `CL-346-AC-012` | `I346-AC-012` | actual macOS clone success、cleanup uncertainty retain/no-unlink、accepted exclusion保持 | overclaimed safety / non-owned unlink | yes | actual macOS + hermetic | S03 |
| `CL-346-AC-013` | `I346-AC-013` | chatgpt-output/new artifact/workbench copy contracts unchanged | legacy regression | yes | focused regression | S04 |
| `CL-346-AC-014` | `I346-AC-014` | lint + ordinary pytest の結果と policy skip を独立記録 | fast lane regression / full claim inflation | yes | local final gate | S99 |
| `CL-346-AC-015` | `I346-AC-015` | final candidate revision で explicit full regression body を実行 | hidden heavy regression | yes | full suite | S99 |
| `CL-346-AC-016` | `I346-AC-016` | shipped docs/provider projection/Issue-Epic trace が一致 | docs drift / untraceable closure | yes | docs + diff + reports | S90, S99 |
| `CL-346-AC-017` | `I346-AC-017` | fresh QA/code/spec review、未解決 blocker 0 | self-review / stale review | yes | independent review | S99 |
| `CL-346-AC-018` | `I346-AC-018` | final commit/push、pull-request handoff/Merge Preparation records、human merge stop | unpushed/stale PR / agent merge | yes | git + PR observation | S99 |
| `CL-346-AC-019` | `I346-AC-019` | changed paths は strict repair boundary 内、spec/ADR gap は Epic repairへ | scope theft / decision smuggling | yes | diff + decision ledger | all, S99 |

### 7.2 Constraint and edge closure

| Closure ID | Spec link | Observable locked expectation | Defect class guarded | Required | Evidence level | Owner |
|---|---|---|---|---|---|---|
| `CL-346-CON-001` | `I346-CON-001` | source identity changes invalidate evidence | stale evidence | yes | pre/post checks | S01, S99 |
| `CL-346-CON-002` | `I346-CON-002` | parent Epic/accepted ADR contradiction stops implementation and returns to Epic planning repair | issue-local authority override | yes | decision ledger + amendment gate | all |
| `CL-346-CON-003` | `I346-CON-003` | only smallest integration/distribution repair | overimplementation | yes | changed-path review | all |
| `CL-346-CON-004` | `I346-CON-004` | provider-first; dogfood hand edits do not become source | projection divergence | yes | source-to-projection map | S04, S90 |
| `CL-346-CON-005` | `I346-CON-005` | external planning/test/import evidence changes authority only through explicit EAL disposition | evidence self-promotion | yes | EAL + spec review | S90, S99 |
| `CL-346-CON-006` | `I346-CON-006` | invalid existing fixture is rejected before update evidence | false no-backfill proof | yes | fixture preflight | S02 |
| `CL-346-CON-007` | `I346-CON-007` | Linux has no named-temp/visible-probe/pathname-cleanup fallback | trust-boundary regression | yes | syscall/path observer | S03 |
| `CL-346-CON-008` | `I346-CON-008` | macOS same-UID exclusion remains explicit | misleading assurance | yes | test wording + review | S03, S90 |
| `CL-346-CON-009` | `I346-CON-009` | fast and full evidence are separate | skipped suite counted as success | yes | two command records | S99 |
| `CL-346-CON-010` | `I346-CON-010` | agent stops before merge | unauthorized external mutation | yes | final handoff state | S99 |
| `CL-346-CON-011` | `I346-CON-011` | external public/provenance allowlist excludes content-derived values | privacy regression | yes | sentinel scan | S03 |
| `CL-346-CON-012` | `I346-CON-012` | plan remains planned; report owns observations | dual source of truth | yes | docs/report review | all, S90 |
| `CL-346-EC-001` | `I346-EC-001` | build/test中HEAD移動はstaleとなりnew candidate revisionで再実行 | mixed revision | yes | pre/post HEAD negative | S01, S99 |
| `CL-346-EC-002` | `I346-EC-002` | stale dist/buildを除去したclean wheelだけを候補にする | stale package contamination | yes | dirty-build negative + inventory | S01 |
| `CL-346-EC-003` | `I346-EC-003` | installed origin is not source checkout | false E2E | yes | module origin assertion | S01 |
| `CL-346-EC-004` | `I346-EC-004` | fixture with preexisting README/invalid state is rejected | contaminated update oracle | yes | negative fixture preflight | S02 |
| `CL-346-EC-005` | `I346-EC-005` | ignored Workbench payloadはupdate前後でbytes/path/ignored state不変 | payload deletion/tracking | yes | snapshot + git status | S02 |
| `CL-346-EC-006` | `I346-EC-006` | old managed assetだけがcandidate版へ更新されcanonical node dataは不変 | false no-op / data migration | yes | fixed fixture + managed manifest | S02 |
| `CL-346-EC-007` | `I346-EC-007` | path/hash/count風sentinelのbody/derived valueをpublic surfaceへ出さない | privacy false negative | yes | scoped sentinel scan | S03 |
| `CL-346-EC-008` | `I346-EC-008` | unavailable cross-FS host is not counted as actual success | platform inference | yes | host capability record | S03, S99 |
| `CL-346-EC-009` | `I346-EC-009` | Linux capability不足はformal destination前fail closedでfallbackなし | unsupported continuation | yes | named probe + fault matrix | S03 |
| `CL-346-EC-010` | `I346-EC-010` | Linux no-replace collisionはexisting fileを保ちshared next slotへ進む | overwrite/collision loss | yes | collision integration + publisher test | S03 |
| `CL-346-EC-011` | `I346-EC-011` | macOS clone capability不足はprecommit unsupportedでcopy/rename fallbackなし | unsafe platform fallback | yes | named probe + fault matrix | S03 |
| `CL-346-EC-012` | `I346-EC-012` | macOS cleanup uncertaintyはretain/no-unlink | non-owned unlink | yes | cleanup fault matrix | S03 |
| `CL-346-EC-013` | `I346-EC-013` | ADR-looking/invalid generic body is not parsed | authority/semantic escalation | yes | body-open spy | S04 |
| `CL-346-EC-014` | `I346-EC-014` | legacy/generic同秒slot競合でもshared allocation/no-overwriteを維持 | cross-command overwrite | yes | concurrent allocation regression | S04 |
| `CL-346-EC-015` | `I346-EC-015` | full failure blocks final quality even if fast passes | partial-quality release | yes | final gate | S99 |
| `CL-346-EC-016` | `I346-EC-016` | docs/review/PR observation bind latest pushed head | stale final evidence | yes | freshness checks | S90, S99 |

## 8. S01 — Exact-source candidate wheel and fresh installed tracer

### 8.1 Behavior goal

各実行cycle開始時のcandidate revisionから生成したcandidate wheelのinventoryを固定し、そのwheelだけをinstallしたfresh consumerでWorkbench shellとgeneric importの最小vertical tracerを通す。

### 8.2 Trace

- Requirements: `I346-RQ-001`〜`I346-RQ-003`
- Acceptance: `I346-AC-001`〜`I346-AC-003`
- Closures: `CL-346-AC-001`〜`003`, `CL-346-CON-001`, `CL-346-CON-004`, `CL-346-EC-003`
- Evidence: `I346-EVD-001`〜`I346-EVD-003`

### 8.3 Planned contract

#### Scope and allowed paths

Primary expected paths:

- `tests/integration/test_epic_00343_distribution.py`（new unless equivalent exists）
- `tests/unit/infra/test_init_update.py`
- small test helper under existing `tests/` only when shared fixture reuse is justified

Repair-only:

- `pyproject.toml`
- `setup.py`
- `src/spec_dock/cli.py`
- `src/spec_dock/assets/spec_dock/templates/README.md`
- `src/spec_dock/assets/spec_dock/templates/root/.workbench/README.md`
- `src/spec_dock/assets/spec_dock/templates/initiative/.workbench/README.md`
- `src/spec_dock/assets/spec_dock/templates/epic/.workbench/README.md`
- `src/spec_dock/assets/spec_dock/templates/issue/.workbench/README.md`

列挙外pathが必要ならworkerは変更せずAmendment triggerへ戻す。

#### Forbidden changes

- runtime/import behavior not exercised by the fresh tracer defect。
- Issue 344/345 public contract changes。
- package version bump、release publication、upload。
- dogfood consumer-first edits。
- historical fixture work（S02 owner）。

#### Red or alternative evidence

Evidence mode: `covered-existing + controlled-negative`。

1. Add wheel inventory assertion and run it against a synthesized inventory missing one required hidden README; it must fail.
2. Run installed-origin assertion with a negative control that places source checkout first; assertion must detect the source origin.
3. Run the actual current wheel. If it already passes, record it as covered-existing Green after sensitivity evidence rather than inventing a production failure.
4. If actual wheel fails, preserve the failing inventory/install output and apply only the smallest package repair.

#### Risk-calibrated test obligations

- exact HEAD and clean build receipt。
- wheel basename/digest/version/inventory。
- exact 5 template README set and denylist。
- isolated venv and console entrypoint/module origin。
- fresh root README and Initiative/Epic/Issue README byte equality。
- ignored payload remains untracked/unmodified。
- generic import from fresh Workbench to target Artifact through installed projected runtime。
- source bytes/source existence/result `canonical=false`。
- no absolute source path in output。

#### Green verification

```bash
rm -rf dist build
uv build
uv run pytest tests/unit/infra/test_init_update.py -k 'workbench or readme or package or wheel'
uv run pytest tests/integration/test_epic_00343_distribution.py \
  -k 'candidate_wheel or fresh_consumer' --run-full-regression
```

実装時に exact node IDs と wheel path selection command を report に記録する。shell wildcard で複数 wheel を曖昧選択しない。

#### Refactor guardrail

- inventory helper は test-only を優先する。
- build system に general-purpose manifest framework を追加しない。
- existing fixture/harness と重複する init/node creation logic を最小限にする。
- production repair は observed package defect の行だけに限定する。

#### Report evidence destination

- `report.md / Source Revision and Candidate Wheel Receipt`
- `report.md / Step Contract Closure / S01`
- `report.md / Test Contract Closure / S01`
- `report.md / Fresh Consumer Matrix`
- `report.md / Delegated Worker Evidence / S01`
- `report.md / Spec Interpretation / Decision Ledger`（material decision がある場合のみ）

#### Amendment trigger

- wheel inventory contract が parent/Issue344 docs と一致しない。
- required assets を入れるため package architecture 変更が必要。
- fresh consumer success に new public API/command が必要。
- source checkout independence を current packaging で検証不能。

いずれも implementation を止め、planning/ADR/Epic repair を判断する。

### 8.4 Delegation contract

- **delegated role**: `dev-coder`（packaging/integration-test focus）。
- **inputs**: adopted canonical R/D/P、Issue344 report/package inventory、`pyproject.toml`、`setup.py`、`src/spec_dock/cli.py`、installer tests、test-lane policy、candidate revision。
- **allowed paths**: §8.3 primary paths。repair は failing evidence に直接対応する repair-only path。
- **forbidden paths**: unrelated runtime/domain/docs/canonical reports、`.assurance.json`、provider workflow policy、release remote。
- **acceptance**: all S01 closures Green、wheel-only origin proven、changed paths bounded。
- **verification**: §8.3 commands、wheel listing、module origin boolean、`git diff --check`。
- **reviewer focus**: source-tree leakage、stale build artifacts、README exact set、hidden path package behavior、test sensitivity、scope creep。
- **stop conditions**: input docs conflict、head changes、wheel cannot be uniquely bound、production architecture change required、unrelated dirty tree prevents attribution。
- **required output**: changed files、negative-control result、actual wheel receipt summary、exact test nodes/results、unresolved risks、report-ready evidence、`Ledger Note` または `No material implementation decisions beyond the approved plan.`。

### 8.5 Concrete test-case cards

#### `tc-346-s01-001` — candidate revision and clean build receipt

- **前提**: current branch を checkout し、既存 user changes を inventory 済み。実行cycle開始時HEADをcandidate revisionとしてreportに記録している。
- **操作**: branch/head/status を取得し、clean build output を作り、build 後に head/status を再確認する。
- **期待結果**: pre/post head が同一、expected revision と一致。wheel が current build に一意に帰属する。
- **失敗検出**: mixed revision、dirty/unattributed output、build 中 head move、複数 candidate ambiguity。
- **検証方法**: git read-only checks + build receipt assertions。
- **関連 closure IDs**: `CL-346-AC-001`, `CL-346-CON-001`, `CL-346-EC-001`。

#### `tc-346-s01-002` — wheel inventory allow/deny contract

- **前提**: current-run candidate wheel と sorted entry list。
- **操作**: template README exact set と deny patterns を検査し、missing-entry negative inventory も検査する。
- **期待結果**: actual wheel は required 5 README を含み、forbidden stale/cache paths を含まない。negative inventory は失敗する。
- **失敗検出**: hidden README omission、non-allowlisted README、legacy/current/completed/cache/bytecode contamination。
- **検証方法**: Python `zipfile` based test-only inventory assertion。
- **関連 closure IDs**: `CL-346-AC-002`, `CL-346-EC-002`。

#### `tc-346-s01-003` — isolated wheel install and origin

- **前提**: empty isolated venv、source checkout を import path から外した subprocess environment。
- **操作**: candidate wheel を install し、console script と module origin を確認する。
- **期待結果**: command/module は isolated installed location から解決され、source checkout に fallback しない。
- **失敗検出**: cwd/PYTHONPATH leakage、editable/source install、wrong wheel/version。
- **検証方法**: subprocess output を boolean/path-class assertion に変換し、host absolute path を report に保存しない。
- **関連 closure IDs**: `CL-346-AC-003`, `CL-346-EC-003`。

#### `tc-346-s01-004` — fresh shell plus generic import tracer

- **前提**: wheel-installed CLI で init した fresh repository と public command/harness で作った Initiative/Epic/Issue。
- **操作**: root/node README、gitignore、ignored payload を検査し、one opaque file を generic import して validate する。
- **期待結果**: 4 scope の README は provider template と同一。payload は ignored/source unchanged。Artifact bytes一致、result `canonical=false`、path leakなし。
- **失敗検出**: missing shell、tracked payload、source mutation、source-tree runtime usage、import integration failure。
- **検証方法**: installed subprocess E2E + filesystem assertions。
- **関連 closure IDs**: `CL-346-AC-003`, `CL-346-CON-004`。

### 8.6 Step closure contract / reviewer gate / commit candidate

Close only when:

- four S01 test cards and controlled negatives are recorded。
- exact wheel receipt is complete。
- fresh installed tracer is Green。
- all changed paths are allowed/repair-only justified。
- fresh `code-reviewer` reviews packaging/test diff and reports no unresolved blocker。
- `git diff --check` succeeds。

Commit candidate:

```text
test(distribution): candidate wheel の fresh consumer 証跡を追加
```

Production repair が必要なら scope を明示した別 commit candidate にする。差分が test-only または no-op でも reviewer-approved closure evidence を report に残す。

## 9. S02 — Existing consumer update, no-backfill, and future-only shell

### 9.1 Behavior goal

README-absent の valid synthetic existing consumer を candidate wheel で update しても既存 root/node に backfill せず、update 後に作る future node だけが shell を受け取ることを証明する。

### 9.2 Trace

- Requirements: `I346-RQ-004`, `I346-RQ-005`
- Acceptance: `I346-AC-004`, `I346-AC-005`
- Closures: `CL-346-AC-004`, `CL-346-AC-005`, `CL-346-CON-006`, `CL-346-EC-004`
- Evidence: `I346-EVD-004`

### 9.3 Planned contract

#### Scope and allowed paths

- `tests/integration/test_epic_00343_distribution.py`
- `tests/unit/infra/test_init_update.py`
- existing fixture helper only when necessary

Repair-only:

- `src/spec_dock/cli.py`
- `src/spec_dock/assets/spec_dock/templates/root/.workbench/README.md`
- `src/spec_dock/assets/spec_dock/templates/initiative/.workbench/README.md`
- `src/spec_dock/assets/spec_dock/templates/epic/.workbench/README.md`
- `src/spec_dock/assets/spec_dock/templates/issue/.workbench/README.md`

列挙外pathが必要ならworkerは変更せずAmendment triggerへ戻す。

#### Forbidden changes

- automatic migration/backfill option。
- existing node schema or `.meta.json` rewrite。
- Initiative/Epic/Issue templates unrelated to README defect。
- historical revision dependency unless explicitly selected and evidenced。
- root Workbench copy expansion。

#### Red or alternative evidence

Evidence mode: `red-required for new no-backfill integration + controlled illegal-state negative`。

1. Create fixture that intentionally inserts a README after snapshot; no-backfill assertion must fail.
2. Add update test before any production change. If current installer passes, record current Green as expected existing implementation plus negative sensitivity.
3. If update backfills, preserve before/after path matrix and repair only installer path responsible.

#### Risk-calibrated test obligations

- fixture validity before update。
- four preexisting README paths absent。
- ignored Workbench payload present and untracked。
- `spec-dock/docs/guide.md` をtest sourceに固定した既知のpre-candidate valid bytesへ置換し、update前にもvalidate/graph loadが成功すること。
- pre-candidate `guide.md` のfixture digestがcandidate wheel内provider版と異なること。
- canonical docs/metadata/deps snapshot before/after。
- update後の`guide.md`がcandidate wheel内provider版とbyte-identicalになり、managed changed-path manifestがexpected managed pathsだけであること。
- future Initiative/Epic/Issue README byte-identical after update。
- existing scope remains absent even after future descendants are created。
- historical SHA/method/absence proof only if historical option is used。

#### Green verification

```bash
uv run pytest tests/unit/infra/test_init_update.py -k 'update and workbench'
uv run pytest tests/integration/test_epic_00343_distribution.py \
  -k 'existing_consumer or no_backfill or future_node' --run-full-regression
git diff --check
```

#### Refactor guardrail

- synthetic fixture recipe を integration test 内に閉じ、production “pre-feature mode” を作らない。
- snapshot normalization は nondeterministic managed fields だけに限定する。
- README absent は directory absent/empty/payload-present の違いを曖昧化しない。
- update implementation の broad copy algorithm rewrite を避ける。

#### Report evidence destination

- `report.md / Existing Consumer Fixture Receipt`
- `report.md / Fresh-Update-Dogfood Matrix / existing`
- `report.md / Step Contract Closure / S02`
- `report.md / Test Contract Closure / S02`
- `report.md / Delegated Worker Evidence / S02`

#### Amendment trigger

- README absent workspace が current validator で invalid と判明する。
- no-backfill を維持するには parent requirement/Issue344 contract 変更が必要。
- future node shell を作る command contract が欠落し、new feature が必要。
- installer が canonical initiatives tree を managed surface として扱う design change が必要。

### 9.4 Delegation contract

- **delegated role**: `dev-coder`（installer/update integration focus）。
- **inputs**: S01 wheel receipt、canonical R/D/P、Issue344 no-backfill contract/report、installer source/tests、fixture helper。
- **allowed paths**: §9.3。
- **forbidden paths**: generic import runtime、platform publisher、docs、canonical Issue/Epic docs、assurance、workflow policy。
- **acceptance**: fixture valid、4 scope no-backfill、future 3 node shell、snapshots bounded。
- **verification**: §9.3 commands、before/after manifest、payload bytes/source state。
- **reviewer focus**: fixture authenticity、no-op update false positive、unexpected node data mutation、template equality、historical option evidence。
- **stop conditions**: invalid fixture、update requires schema migration、path outside allowed scope、head/wheel changed without rebuild。
- **required output**: recipe、before/after content-free matrix、changed files、test results、repair rationale/no-op rationale、report-ready evidence、Ledger Note。

### 9.5 Concrete test-case cards

#### `tc-346-s02-001` — valid synthetic pre-feature fixture

- **前提**: wheel-installed consumer hierarchy exists。
- **操作**: four README filesを除去し、ignored payloadを残し、`spec-dock/docs/guide.md`だけをtest sourceで管理する既知のpre-candidate valid bytesへ置換してvalidate/graph loadを実行し、snapshotを取る。
- **期待結果**: fixture is valid、4 README absent、payload/canonical data readable、pre-candidate `guide.md` digestは固定値でcandidate provider版と異なる。
- **失敗検出**: hidden existing README、invalid hierarchy、payload accidentally tracked、candidateと同一のmanaged asset、snapshot incomplete。
- **検証方法**: filesystem matrix + validation + git status/snapshot assertions + fixed fixture/candidate bytes comparison。
- **関連 closure IDs**: `CL-346-CON-006`, `CL-346-EC-004`, `CL-346-EC-005`, `CL-346-EC-006`。

#### `tc-346-s02-002` — update does not backfill existing scopes

- **前提**: `tc-346-s02-001` fixture and S01 candidate wheel。
- **操作**: wheel-installed top-level `spec-dock update` を実行し、four README paths と snapshots を再取得する。
- **期待結果**: all existing README remain absent、canonical/metadata/payload unchanged、`guide.md`がcandidate provider版とbyte-identicalへ更新され、managed差分はexpected pathsだけ。
- **失敗検出**: any backfill、node rewrite/delete、payload deletion/track、no-op masquerading as update。
- **検証方法**: exact path assertions + normalized before/after manifest。
- **関連 closure IDs**: `CL-346-AC-004`, `CL-346-EC-005`, `CL-346-EC-006`。

#### `tc-346-s02-003` — future nodes receive shell after update

- **前提**: successfully updated existing fixture with preexisting scopes still README-absent。
- **操作**: future Initiative → Epic → Issue を existing public helper/command で作る。
- **期待結果**: each future node gets tracked README byte-identical to provider template; preexisting nodes remain absent。
- **失敗検出**: future README missing/wrong、preexisting backfill triggered by node creation、template drift。
- **検証方法**: path matrix + byte comparison + git status classification。
- **関連 closure IDs**: `CL-346-AC-005`。

#### `tc-346-s02-004` — illegal post-update state sensitivity

- **前提**: no-backfill assertion helper。
- **操作**: negative fixture に one preexisting README を不正に追加し、assertion を実行する。
- **期待結果**: test fails specifically on unexpected backfill path。
- **失敗検出**: over-normalized snapshot、existence-only aggregate that misses one path、false Green。
- **検証方法**: controlled negative test fixture。
- **関連 closure IDs**: `CL-346-AC-004`, `CL-346-EC-004`。

### 9.6 Step closure contract / reviewer gate / commit candidate

- S02 cards Green and negative sensitivity proven。
- historical option usage is explicitly yes/no; yesなら exact SHA/method/absence proof exists。
- no unexpected canonical node diff。
- fresh `code-reviewer` verifies installer/test scope and no-backfill semantics。
- step report rows complete。

Commit candidate:

```text
test(update): existing consumer の no-backfill 証跡を追加
```

Observed installer defect repair is a separately reviewable candidate:

```text
fix(update): existing scope の Workbench shell backfill を防止
```

## 10. S03 — Distributed target, privacy, cross-filesystem, and platform publication

### 10.1 Behavior goal

candidate-wheel-installed generic import が root/Initiative/Epic/Issue、external/cross-filesystem source、Linux/macOS accepted publication boundary を守り、external public/provenance privacy を維持することを証明する。

### 10.2 Trace

- Requirements: `I346-RQ-007`〜`I346-RQ-009`, `I346-RQ-011`, `I346-RQ-012`
- Acceptance: `I346-AC-007`, `008`, `010`, `011`, `012`
- Closures: corresponding AC rows, `CL-346-CON-007`, `008`, `011`, `CL-346-EC-008`
- Evidence: `I346-EVD-006`, `I346-EVD-007`

### 10.3 Planned contract

#### Scope and allowed paths

Primary:

- `tests/integration/test_epic_00343_distribution.py`
- `tests/integration/iss346_platform_probe.py`
- `tests/cli_runtime/test_artifact_import_file.py`
- `tests/unit/infra/test_binary_artifact_publisher.py`
- `tests/unit/application/test_import_file_artifact.py`
- `tests/unit/application/test_binary_artifact_import_ports.py`
- `tests/unit/commands/test_artifact_import_file.py`
- `tests/unit/presentation/test_artifact_import_file.py`

Repair-only:

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_file_artifact.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/binary_artifact_publisher.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/artifact_import.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/artifacts.py`

列挙外pathが必要ならworkerは変更せずAmendment triggerへ戻す。

#### Forbidden changes

- new import command or target type。
- public digest/count for generic import。
- Linux visible/named staging/probe/cleanup fallback。
- macOS trust model expansion or copy/rename fallback。
- platform support inferred solely from OS label。
- unrelated naming/lifecycle refactor。

#### Red or alternative evidence

Evidence mode: mixed `red-required`, `covered-existing`, and actual-host required。

- Add wheel-installed four-target and external privacy tests first; external sentinel leak must fail a controlled renderer/output negative.
- Existing publisher unit tests are `covered-existing`; demonstrate sensitivity by capability fault injection and visible-entry observer.
- Actual Linux and macOS host tests are `manual-required/host-required`; policy skip/unavailable is not Green.
- If current code passes all, no production change is needed; add only missing integration evidence.

#### Risk-calibrated test obligations

- target matrix and target binding。
- source bytes unchanged、destination bytes equal、no overwrite/shared slot behavior。
- repo-relative/absolute external/nested-CWD relative external。
- actual cross-device source where capability exists。
- text and JSON allowlist; no absolute/parent/body/digest/count/derived value。scan対象はcaptured stdout/stderr、parsed JSON、import自身が作成・変更したpublic provenance fileだけとし、generic body、canonical R/D/P/report、wheel receipt/distribution digestを除外する。
- Linux actual anonymous stage, procfs identity, no visible entry, no-replace commit。
- Linux capability failure classes and zero formal destination/fallback/path cleanup。
- macOS actual clone-capable success and actual cross-FS if available。
- macOS cleanup ambiguity/missing/replacement/type/stat/open retain/no-unlink matrix。
- accepted same-UID exclusion in docs/evidence wording。
- precommit vs postcommit state/retry semantics。
- actual hostごとにcandidate revision、OS/kernel/Python、execution kind、resolved container image digestまたはnot_applicable、filesystem type、device equality boolean、capability booleans、ordinary-user条件、repo-relative command、pytest node/named probe ID、result evidence refをcontent-free receiptへ記録する。

#### Green verification

Hermetic/focused:

```bash
uv run pytest tests/unit/infra/test_binary_artifact_publisher.py \
  -k 'explicit or privacy or cross or linux or macos or publication or cleanup'
uv run pytest tests/cli_runtime/test_artifact_import_file.py
uv run pytest tests/integration/test_epic_00343_distribution.py \
  -k 'target_matrix or external or cross_filesystem or linux or macos' \
  --run-full-regression
```

Host laneの変数契約:

- `ISS346_CANDIDATE_WHEEL`: S01 receiptで一意に確定したwheelのabsolute path。reportにはbasename/digestだけを保存する。
- `ISS346_VENV`: そのwheelだけをinstallしたisolated venv。reportにはabsolute pathを保存しない。
- `ISS346_LINUX_DEST`: ordinary userが書け、`O_TMPFILE` open/anonymous inode regularity、`/proc/self/fd` identity、directory fsyncをpreflightで確認したdestination。linkabilityはpreflight対象にせず、`linux-supported-publication`の最初のactual no-replace formal commitで確定する。
- `ISS346_MACOS_DEST`: ordinary userが書け、clone-capableであることをpreflightしたdestination。

Linux actual-host command queue:

```bash
ISS346_PLATFORM_DEST="$ISS346_LINUX_DEST" "$ISS346_VENV/bin/python" \
  tests/integration/iss346_platform_probe.py --probe linux-capability-preflight
ISS346_PLATFORM_DEST="$ISS346_LINUX_DEST" "$ISS346_VENV/bin/python" \
  tests/integration/iss346_platform_probe.py --probe linux-supported-publication
ISS346_PLATFORM_DEST="$ISS346_LINUX_DEST" "$ISS346_VENV/bin/python" \
  tests/integration/iss346_platform_probe.py --probe linux-capability-insufficient
```

Linux containerを使う場合は、resolved digestと通常権限を固定する。

```bash
ISS346_LINUX_IMAGE_DIGEST="$(docker image inspect python:3.12 --format '{{index .RepoDigests 0}}')"
docker run --rm --user "$(id -u):$(id -g)" \
  --mount type=bind,src="$PWD",dst=/repo,readonly \
  --mount type=bind,src="$ISS346_CANDIDATE_WHEEL",dst=/wheel/candidate.whl,readonly \
  --mount type=bind,src="$ISS346_LINUX_DEST",dst=/evidence \
  -w /repo "$ISS346_LINUX_IMAGE_DIGEST" sh -lc \
  'python -m venv /tmp/iss346-venv && /tmp/iss346-venv/bin/pip install --no-deps /wheel/candidate.whl && ISS346_PLATFORM_DEST=/evidence /tmp/iss346-venv/bin/python tests/integration/iss346_platform_probe.py --probe linux-supported-publication'
```

macOS actual-host command queue:

```bash
ISS346_PLATFORM_DEST="$ISS346_MACOS_DEST" "$ISS346_VENV/bin/python" \
  tests/integration/iss346_platform_probe.py --probe macos-capability-preflight
ISS346_PLATFORM_DEST="$ISS346_MACOS_DEST" "$ISS346_VENV/bin/python" \
  tests/integration/iss346_platform_probe.py --probe macos-clone-publication
```

各preflightはO_TMPFILE open/regularity、procfs identity、directory fsync等のpre-commit capability有りで0、不足で77、test defectで1を返す。preflightはvisible linkability probeを実行しない。`linux-supported-publication`は最初のactual formal candidateへのno-replace commitでlinkabilityを確定し、link固有のunsupported/policy failureは77、test/contract defectは1とする。77は`unavailable`としてreceiptへ記録するがrequired host successを閉じない。probe ID、repo-relative command、result linkageは`design.md` §10.1 schemaで保存し、host-local path/payload contentは保存しない。

#### Refactor guardrail

- do not introduce test-only branches in production。
- platform capability helper changes only if actual defect requires them。
- privacy allowlist remains command-specific; do not create broad “sanitize arbitrary object” abstraction。
- do not consolidate Linux/macOS algorithms beyond accepted shared contract。
- retain existing fault injection hooks; remove temporary instrumentation before closure。

#### Report evidence destination

- `report.md / Target and Source Matrix`
- `report.md / External Source Privacy Matrix`
- `report.md / Platform Capability Evidence / Linux`
- `report.md / Platform Capability Evidence / macOS`
- `report.md / Step Contract Closure / S03`
- `report.md / Test Contract Closure / S03`
- `report.md / Delegated Worker Evidence / S03`

#### Amendment trigger

- accepted ADR primitive unavailable on all required hosts。
- success requires named/visible fallback, stronger mac trust claim, or publication semantics change。
- privacy requirement conflicts with existing generic public contract。
- cross-FS behavior requires source-link/rename。
- new platform support decision is needed。

### 10.4 Delegation contract

- **delegated role**: `dev-coder`（security/platform integration focus）。
- **inputs**: S01 wheel、canonical R/D/P、three accepted ADRs、Issue345 report、publisher/application/presentation source/tests、host capability information。
- **allowed paths**: §10.3。
- **forbidden paths**: package/update docs/canonical reports/workflow/assurance/unrelated artifact lifecycle。
- **acceptance**: all target/privacy closures Green; actual Linux and macOS evidence present; no unsafe fallback; changed paths bounded。
- **verification**: focused + installed integration + actual host commands; source/destination internal equality; privacy scan; path observer。
- **reviewer focus**: FD binding、TOCTOU、formal commit point、no-replace、external path leak、digest/count leak、capability honesty、cleanup ownership、same-UID exclusion wording。
- **stop conditions**: required host unavailable、accepted ADR conflict、unsafe workaround needed、external privacy cannot be met、unexpected production architecture expansion。
- **required output**: changed files、test/fault/host matrix、content-free capability receipt、remaining platform limitations、report-ready evidence、Ledger Note。

### 10.5 Concrete test-case cards

#### `tc-346-s03-001` — wheel-installed four-target import

- **前提**: S01 fresh hierarchy and candidate-wheel-installed runtime; one opaque payload per target。
- **操作**: root/Initiative/Epic/Issue selectorsで generic import を実行する。
- **期待結果**: correct target artifacts、bytes equal、source unchanged、canonical=false、no existing overwrite。
- **失敗検出**: selector routing gap、root treated as graph node、wrong artifacts dir、source mutation、legacy grammar contamination。
- **検証方法**: installed subprocess matrix + filesystem assertions。
- **関連 closure IDs**: `CL-346-AC-007`。

#### `tc-346-s03-002` — external and nested-CWD privacy

- **前提**: harmless parent/body sentinels、absolute external source、nested CWD relative external source、text/JSON modes。
- **操作**: import を実行し、captured stdout/stderr、parsed JSON、importが作成・変更したpublic provenance fileだけをscanする。generic body、canonical planning/report、wheel receiptは対象外とし、import以外のtracked text差分はfixture scope違反として失敗させる。
- **期待結果**: basename-only source display; no parent/absolute path、body、digest、byte count、derived content field/value。
- **失敗検出**: raw exception/path、debug context、hash/count DTO reuse、provenance body duplication。
- **検証方法**: allowlist + negative sentinel scan。
- **関連 closure IDs**: `CL-346-AC-008`, `CL-346-CON-011`, `CL-346-EC-007`。

#### `tc-346-s03-003` — actual cross-filesystem source

- **前提**: source and destination `st_dev` differ; destination satisfies platform commit capability。
- **操作**: external source を import する。
- **期待結果**: destination-side staging、source unchanged、commit success、privacy contract maintained。
- **失敗検出**: source-device staging/link/rename、EXDEV failure、path disclosure。
- **検証方法**: actual host integration + `design.md` §10.1 platform receipt。reportにはdevice-different boolean、repo-relative command、test node/probe ID、result linkageを保存する。
- **関連 closure IDs**: `CL-346-AC-008`, `CL-346-EC-008`。

#### `tc-346-s03-004` — Linux supported anonymous publication

- **前提**: Linux、`O_TMPFILE` open/regularity・working procfs identity・directory fsyncのpreflight成功。linkabilityは未確定。
- **操作**: directory-entry observerを有効にし、最初のactual formal candidateへのno-replace commitとしてlink syscallを実行してlinkabilityを確定する。続けてcommit race/no-overwrite caseを実行する。
- **期待結果**: precommit visible stage/probe count 0、held anonymous FD から formal destination へ no-replace link、bytes equal。
- **失敗検出**: named temp、visible probe、path cleanup、non-FD-bound commit、overwrite。
- **検証方法**: actual Linux host + syscall/path event assertions + existing unit faults + candidate/image/OS/Python/filesystem/command/test-node receipt。
- **関連 closure IDs**: `CL-346-AC-010`, `CL-346-CON-007`, `CL-346-EC-010`。

#### `tc-346-s03-005` — Linux capability-insufficient fail-closed

- **前提**: preflight failure matrix（O_TMPFILE open/regularity、procfs identity、directory durability）と、formal commit failure matrix（link capability/policy）を分離する。
- **操作**: preflight failureはformal commit前に注入する。link capability/policy failureはvisible probeを行わず、最初のactual formal candidateへのno-replace commit syscallで注入またはactual unsupported FS上で観測する。
- **期待結果**: content-free unsupported result、committed=false、formal destination absent、visible stage/probe 0、pathname cleanup call 0。
- **失敗検出**: fallback success、partial destination、named cleanup、raw path/error disclosure。
- **検証方法**: hermetic fault injection + actual negative where available。
- **関連 closure IDs**: `CL-346-AC-011`, `CL-346-CON-007`, `CL-346-EC-009`。

#### `tc-346-s03-006` — macOS clone-capable success

- **前提**: macOS clone-capable destination、external source（cross-device if available）。
- **操作**: destination-side stage/copy/verify、`fclonefileat` no-replace commit、cleanup を実行する。
- **期待結果**: commit success、source unchanged、destination bytes equal、no overwrite、owned stage cleanup state honest。
- **失敗検出**: copy/rename fallback、source link、wrong-parent commit、capability overclaim。
- **検証方法**: actual macOS host + existing publisher tests + candidate/OS/Python/filesystem/command/test-node receipt。
- **関連 closure IDs**: `CL-346-AC-012`, `CL-346-EC-011`。

#### `tc-346-s03-007` — macOS cleanup trust boundary

- **前提**: missing/replaced/unexpected-type/stat/fstat/open uncertainty cases and accepted ADR wording。
- **操作**: cleanup boundary faults を注入し、unlink calls と result state を観測する。
- **期待結果**: uncertainty は retain/no-unlink; success unlink は final identity/type check 通過時のみ。same-UID final-check-to-unlink exclusion remains documented。
- **失敗検出**: non-owned unlink、missing treated removed、stronger-than-ADR assurance claim。
- **検証方法**: hermetic unit tests + spec/code reviewer inspection。
- **関連 closure IDs**: `CL-346-AC-012`, `CL-346-CON-008`, `CL-346-EC-012`。

### 10.6 Step closure contract / reviewer gate / commit candidate

- all hermetic tests Green。
- actual Linux supported lane evidence exists。
- actual macOS clone-capable lane evidence exists。
- cross-FS actual evidence exists on at least one required capable host; unavailable cases are explicitly non-success。
- privacy scan is content-free and leaks zero forbidden values。
- fresh security/platform-focused `code-reviewer` has no unresolved blocker。
- accepted ADR wording unchanged unless Epic repair occurred first。

Commit candidate:

```text
test(artifact): 配布後の platform と privacy 統合証跡を追加
```

Observed defect repairs are separate `fix(artifact): ...` candidates, one root-cause family per reviewable batch where practical。

## 11. S04 — Opaque lifecycle, compatibility, and integrated dogfood projection

### 11.1 Behavior goal

binary/ZIP/invalid UTF-8/NUL-bearing generic Artifacts が validate/sync/discovery/deps/context で body-open されず、legacy commands remain compatible、exact-revision dogfood projection で existing `epic-00343` を backfill せず future shell + generic import が一体で動くことを証明する。

### 11.2 Trace

- Requirements: `I346-RQ-006`, `I346-RQ-010`, `I346-RQ-013`
- Acceptance: `I346-AC-006`, `I346-AC-009`, `I346-AC-013`
- Closures: `CL-346-AC-006`, `009`, `013`, `CL-346-CON-004`, `CL-346-EC-013`
- Evidence: `I346-EVD-005`, `007`, `008`

### 11.3 Planned contract

#### Scope and allowed paths

Primary:

- `tests/integration/test_epic_00343_distribution.py`
- `tests/cli_runtime/test_artifact_import_s04.py`
- `tests/cli_runtime/test_artifact_import_chatgpt_output.py`（inspect/run; change only for missing characterization）
- `tests/cli_runtime/test_workbench.py`（inspect/run; change only for missing characterization）
- `tests/cli_runtime/test_artifact_import_file.py`
- `tests/unit/application/test_import_file_artifact.py`
- `tests/unit/presentation/test_artifact_import_file.py`

Repair-only:

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/artifacts.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_artifact.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_file_artifact.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_artifact_doc.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/active_store.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/binary_artifact_publisher.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/artifact_import.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py`

列挙外pathが必要ならworkerは変更せずAmendment triggerへ戻す。

#### Forbidden changes

- generic body parser/frontmatter/MIME/encoding logic。
- root graph node or generic default discovery inclusion。
- legacy result/filename/selector changes。
- direct canonical dogfood data edit in real working tree。
- backfill of current `epic-00343`。
- provider source replaced by dogfood copy。

#### Red or alternative evidence

Evidence mode: `red-required for dogfood/opaque integration + covered-existing compatibility`。

- body-open spy must raise if any lifecycle consumer opens a generic fixture; run before production change。
- illegal dogfood update negative that creates `epic-00343` README must be detected。
- existing compatibility suites are covered-existing and run unchanged; if additional characterization is needed, add expectation before repair。
- actual dogfood run uses a disposable exact checkout, not the real canonical worktree。

#### Risk-calibrated test obligations

- four opaque payload classes and ADR-looking generic names。
- `ValidateTreeRequest`, `SyncRequest`, discovery/ADR/authoring paths, `CheckDepsRequest`, `build_context_pack_text` or current equivalent。
- normalized `.agent/index*`, tree/deps PUML/JSON, dashboard, `active/context-pack.md` equivalence。
- zero generic body opens。
- chatgpt-output specific digest/count/source contract unchanged。
- new typed/blank Artifact naming/shared slots/no migration unchanged。
- workbench copy node scope/output/source-wins contract unchanged。
- disposable exact dogfood checkout before/after `epic-00343` README absence。
- provider update projection + future node shell + generic import through projected runtime。
- dogfood checkout validation/sync and clean/expected diff manifest。

#### Green verification

```bash
uv run pytest tests/cli_runtime/test_artifact_import_s04.py \
  -k 'opaque or lifecycle or projection or context or deps or validate or sync'
uv run pytest tests/cli_runtime/test_artifact_import_chatgpt_output.py
uv run pytest tests/cli_runtime/test_workbench.py
uv run pytest tests/cli_runtime/test_artifact_import_file.py
uv run pytest tests/integration/test_epic_00343_distribution.py \
  -k 'dogfood or opaque or compatibility' --run-full-regression
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync --no-github
```

Nearest new-artifact focused test path/node discovered at execution is added to command list and report before closure。

#### Refactor guardrail

- body-open spy/integration helpers remain test-only。
- do not generalize all projections into a new snapshot framework unless existing helper cannot serve。
- normalize only timestamps/known generated fields。
- dogfood disposable setup reuses provider update/public runtime; no bespoke production bypass。
- compatibility failure repair is interaction-local, not legacy redesign。

#### Report evidence destination

- `report.md / Opaque Lifecycle Matrix`
- `report.md / Compatibility Regression Evidence`
- `report.md / Fresh-Update-Dogfood Matrix / dogfood`
- `report.md / Provider-to-Dogfood Projection Manifest`
- `report.md / Step Contract Closure / S04`
- `report.md / Test Contract Closure / S04`
- `report.md / Delegated Worker Evidence / S04`

#### Amendment trigger

- default lifecycle consumer requires generic body content。
- generic Markdown must be treated as typed/ADR/canonical input。
- dogfood update requires backfilling current epic。
- legacy public contract must change。
- provider/dogfood ownership cannot be kept provider-first。

### 11.4 Delegation contract

- **delegated role**: `dev-coder`（lifecycle/compatibility/dogfood integration focus）。
- **inputs**: S01 wheel、S02 no-backfill evidence、S03 platform/privacy evidence、canonical R/D/P、Issue344/345 reports、current S04/legacy tests、provider/dogfood rules。
- **allowed paths**: §11.3。
- **forbidden paths**: real canonical dogfood data outside approved projection/report, docs (S90), workflow/assurance, broad lifecycle rewrite。
- **acceptance**: zero body opens、projection equivalence、legacy suites Green、dogfood existing epic absent/future shell+import success。
- **verification**: §11.3 commands、before/after manifest、body-open spy、disposable checkout receipt。
- **reviewer focus**: filter-before-read、generic name classification、projection normalization honesty、provider-first ownership、no-backfill、legacy expectation integrity。
- **stop conditions**: semantic read needed、real worktree mutation cannot be isolated、accepted contract conflict、broad repair required、platform evidence invalidated。
- **required output**: changed files、opaque/compat/dogfood matrices、disposable checkout cleanup result、test results、report-ready evidence、Ledger Note。

### 11.5 Concrete test-case cards

#### `tc-346-s04-001` — opaque body-open denial matrix

- **前提**: binary、ZIP、invalid UTF-8、NUL-bearing files imported as generic artifacts; readers spy on those exact paths。
- **操作**: validate、sync、discovery/ADR/authoring、deps、context generation entrypoints を実行する。
- **期待結果**: generic body-open count 0、decode error 0、operations succeed per name-only policy。
- **失敗検出**: extension/frontmatter probe、generic default discovery、body hash/read in lifecycle。
- **検証方法**: monkeypatch spy + current lifecycle requests/helpers。
- **関連 closure IDs**: `CL-346-AC-009`, `CL-346-EC-013`。

#### `tc-346-s04-002` — projection and context equivalence

- **前提**: baseline consumer projections and same consumer after opaque generic additions。
- **操作**: normalize known generated timestamp only; compare index/tree/deps/dashboard/context/ADR mirror outputs。
- **期待結果**: semantic output equivalent、generic path/body absent from projections、typed/ADR set unchanged。
- **失敗検出**: projection contamination、over-normalization、context body leak、ADR promotion。
- **検証方法**: existing `_PROJECTION_PATHS` style snapshot + exact diff assertions。
- **関連 closure IDs**: `CL-346-AC-009`。

#### `tc-346-s04-003` — legacy compatibility bundle

- **前提**: existing chatgpt-output、typed/blank new artifact、workbench copy fixtures/expectations。
- **操作**: all focused suites run after generic integration tests; shared-slot concurrency cases included。
- **期待結果**: public output/filename/source policy/copy semantics unchanged; existing files unmodified。
- **失敗検出**: generic DTO/filter/naming/lock behavior leaking into legacy contracts。
- **検証方法**: existing tests unchanged where possible + before/after filesystem snapshot。
- **関連 closure IDs**: `CL-346-AC-013`, `CL-346-EC-014`。

#### `tc-346-s04-004` — exact dogfood no-backfill

- **前提**: disposable checkout at candidate revision; current `epic-00343/.workbench/README.md` absent; S01 wheel installed。
- **操作**: candidate wheel top-level CLI で checkout update、pre/post path and provider-projection manifest を取る。
- **期待結果**: existing epic README remains absent; managed projection matches provider changes; unrelated canonical data unchanged。
- **失敗検出**: epic backfill、consumer-first drift、unexpected active/canonical rewrite、wrong wheel/source。
- **検証方法**: exact path assertions + changed-path manifest + byte/hash equality for provider/projection files (digest values not duplicated into user-file provenance)。
- **関連 closure IDs**: `CL-346-AC-006`, `CL-346-CON-004`。

#### `tc-346-s04-005` — future shell plus generic import in dogfood projection

- **前提**: updated disposable dogfood checkout with existing epic still absent; local GitHub stub/public node creation harness。
- **操作**: future node を作り、its ignored Workbench file を projected runtime で generic import、validate/sync を実行する。
- **期待結果**: future node README present/byte-identical、import succeeds/privacy-safe、existing epic remains absent、checkout diff is expected only。
- **失敗検出**: shell/import not coexisting、backfill side effect、provider/runtime drift、privacy leak。
- **検証方法**: installed top-level update + projected runtime subprocess E2E。
- **関連 closure IDs**: `CL-346-AC-006`。

### 11.6 Step closure contract / reviewer gate / commit candidate

- opaque lifecycle/body-open/projection closures Green。
- all legacy compatibility suites Green without unjustified expectation changes。
- disposable dogfood closure Green and real working tree remains attributable/clean except planned changes。
- fresh `code-reviewer` evaluates Issue/Epic interaction and no-backfill/provider-first boundary。
- S04 report sections complete。

Commit candidate:

```text
test(epic): Workbench と generic import の dogfood 統合証跡を追加
```

Interaction repair is a separate bounded `fix(...)` commit candidate if needed。

## 12. S90 — Documentation impact resolution, provider parity, and report trace

### 12.1 Behavior goal

implemented contract と shipped docs/help/rules を照合し、必要最小限の docs refresh を provider-first で行い、dogfood projection、Issue report、Epic report、EAL を最新 evidence に接続する。

### 12.2 Trace

- Requirement: `I346-RQ-014`, `I346-RQ-015`
- Acceptance: `I346-AC-016`, supporting `AC-019`
- Closures: `CL-346-AC-016`, `CL-346-CON-004`, `008`, `012`, `CL-346-EC-016`
- Evidence: `I346-EVD-009`, `I346-EVD-010`

### 12.3 Planned contract

#### Scope and allowed paths

Provider docs, only when inspect-first identifies a gap:

- `src/spec_dock/assets/spec_dock/docs/README.md`
- `src/spec_dock/assets/spec_dock/docs/guide.md`
- `src/spec_dock/assets/spec_dock/docs/reference_naming.md`
- `src/spec_dock/assets/spec_dock/docs/rules/root/artifacts.md`

Projection:

- `spec-dock/docs/README.md`
- `spec-dock/docs/guide.md`
- `spec-dock/docs/reference_naming.md`
- `spec-dock/docs/rules/root/artifacts.md`
- S01〜S04の列挙済みprovider runtime pathと同じrelative pathの`spec-dock/scripts/spec_dock_runtime/` mirror（該当stepでproduction repairがあった場合だけ）

Evidence targets controlled by orchestrator:

- target Issue `report.md`
- parent Epic `report.md`
- target report EAL/decision/reviewer/test/step/delivery sections

列挙外pathが必要ならworker/doc-writerは変更せずAmendment triggerへ戻す。

#### Forbidden changes

- product behavior in a docs step。
- consumer-first dogfood doc edits。
- broad workflow policy rewrite。
- canonical R/D/P changes without planning amendment/fresh review。
- `.assurance.json` mutation or profile selection。
- claiming completed gate before evidence exists。

#### Red or alternative evidence

Evidence mode: `inspect-only + structural negative`。

- search current provider docs for required concepts/tokens。
- link/heading/token structural checks fail when a required term/link is removed in a controlled fixture or when actual gap exists。
- if docs already complete, record approved-no-op candidate after spec review rather than prose churn。

#### Risk-calibrated verification obligations

- fresh-only shell/no-backfill wording。
- Workbench ignored/non-secret guidance。
- generic import target/source/privacy/opaque wording。
- Linux anonymous/no-fallback wording。
- macOS clone/cleanup/same-UID exclusion wording。
- fast vs explicit full regression wording。
- provider and projected docs byte/content parity where expected。
- Issue report has all S01〜S04 evidence/EAL/decision dispositions。
- Epic report traces Candidate 1/2 dependencies and Candidate 3 final evidence without raw duplication。
- no authoritative claims unsupported by reviews/delivery state。

#### Green verification

```bash
rg -n 'workbench|no-backfill|artifact import file|opaque|O_TMPFILE|fclonefileat|full-regression' \
  src/spec_dock/assets/spec_dock/docs
"$ISS346_VENV/bin/spec-dock" update "$ISS346_DOGFOOD_REPO"
git diff --check
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync --no-github
git diff -- src/spec_dock/assets/spec_dock spec-dock
```

`ISS346_VENV`はS01 candidate wheelだけをinstallしたvenv、`ISS346_DOGFOOD_REPO`は同じcandidate revisionのdisposable checkoutである。GitHub取得を行うrepository wrapper `./spec-dock/scripts/spec-dock update .`はcandidate revision証跡には使用しない。

Provider docs変更が不要なら、上記candidate-wheel-installed commandでdisposable projection parityを閉じる。Provider docs変更が必要な場合は、(1) provider docsだけをreview/commitし、(2) その新HEADをcandidate revisionとしてwheelを再buildしてS01 inventoryを再取得し、(3) 新wheelのvenvでdisposable checkoutをupdateし、(4) 必要なdogfood projection差分をreview/commitする。candidate revision変更で影響を受けたdocs/projection/review証跡は再取得する。real worktreeをupdateする場合もGitHub wrapperではなく同じcandidate-wheel-installed top-level CLIを使い、unrelated active/canonical dataを変更するなら停止する。

#### Refactor guardrail

- avoid duplicate policy prose; link to accepted reference where available。
- exact command/token spelling matches implementation。
- do not turn docs refresh into architecture redesign。
- report entries are concise evidence summaries, not verbatim interaction logs。

#### Report evidence destination

- `report.md / Documentation Impact Resolution`
- `report.md / Provider-to-Dogfood Projection Manifest`
- `report.md / Evidence Adoption Ledger`
- `report.md / Spec Interpretation / Decision Ledger`
- `report.md / Reviewer Gate Status / S90`
- parent Epic `report.md / Candidate 3 Trace`

#### Amendment trigger

- docs gap reveals unresolved product choice。
- current behavior contradicts accepted ADR。
- update flow rewrites unrelated canonical data。
- report requires durable decision absent from R/D/ADR。

### 12.4 Delegation contract

- **delegated role**: `doc-writer` for shipped provider docs; orchestrator owns report/EAL and projection command; `dev-coder` only if structural doc test code is required。
- **inputs**: final S01〜S04 behavior/evidence、canonical R/D/P、accepted ADRs、current provider docs/help、Issue/Epic reports、workflow reporting contract。
- **allowed paths**: §12.3 exact docs subset; projected counterparts via command; report paths by orchestrator only。
- **forbidden paths**: runtime/tests unless separately delegated、assurance/profile、unrelated docs、canonical requirements/design/plan without amendment。
- **acceptance**: docs/code/ADR parity、provider-first projection、Issue/Epic trace、no unsupported authority claim。
- **verification**: inspect/search/link/token checks、update/diff/validate/sync、fresh docs/spec review。
- **reviewer focus**: no-backfill clarity、privacy wording、Linux no fallback、macOS exclusion honesty、fast/full distinction、evidence-only language。
- **stop conditions**: unresolved product decision、provider/dogfood ownership conflict、unrelated update mutation、reviewer unavailable。
- **required output**: changed/no-op docs list、source-to-projection map、verification results、unresolved wording risks、report-ready summary、Ledger Note。

### 12.5 Concrete test-case cards

#### `tc-346-s90-001` — docs contract parity

- **前提**: final implemented public commands/tokens and current provider docs。
- **操作**: required concept/link/token inventory を inspect し、code/ADR と比較する。
- **期待結果**: shell/no-backfill/privacy/opaque/Linux/macOS/fast-full boundaries accurately described; no overclaim。
- **失敗検出**: stale command、missing safety boundary、named-temp implication、same-UID exclusion omission、full regression ambiguity。
- **検証方法**: structural search + human/spec review + link inspection。
- **関連 closure IDs**: `CL-346-AC-016`, `CL-346-CON-008`。

#### `tc-346-s90-002` — provider projection parity

- **前提**: provider docs/runtime changes reviewed; working tree diff inventory exists。
- **操作**: repository-approved update flow、source-to-projection comparison、unrelated diff scan。
- **期待結果**: corresponding managed files match provider; existing `epic-00343` remains no-backfill; unrelated canonical data unchanged。
- **失敗検出**: consumer-first edits、projection drift、broad update side effects。
- **検証方法**: changed-path manifest + byte/content comparison + diff check。
- **関連 closure IDs**: `CL-346-AC-016`, `CL-346-CON-004`。

#### `tc-346-s90-003` — Issue/Epic report trace and EAL

- **前提**: S01〜S04 observed evidence summaries and candidate adoption dispositions。
- **操作**: target report ledger と Epic Candidate 3 trace を更新し、open/stale/blocking entries を inspect する。
- **期待結果**: each closure has evidence path/result/head binding; EAL disposition complete; Epic report references Issue report without raw duplication。
- **失敗検出**: evidence-only candidate self-adoption、open decision、stale head、missing platform/full/review status、verbatim interaction log。
- **検証方法**: report schema/manual review + `spec-dock validate`。
- **関連 closure IDs**: `CL-346-AC-016`, `CL-346-CON-012`, `CL-346-EC-016`。

### 12.6 Step closure contract / reviewer gate / commit candidate

- docs impact resolved as bounded change or reviewed no-op。
- provider/projection parity verified without unrelated canonical mutation。
- Issue/Epic report/EAL/decision entries current through S04。
- fresh `spec-reviewer` reviews docs/spec/report alignment; code-facing doc tests receive `code-reviewer` if changed。
- diff check/validate/sync evidence recorded。

Commit candidate:

```text
docs(epic): 統合配布と final quality の証跡を同期
```

## 13. S99 — Independent final quality, full regression, review, and delivery gates

### 13.1 Behavior goal

all planned closures を final candidate revision で再検証し、ordinary/full lanes、fresh independent review、限定的なreview-evidence転記、final commit/push、pull-request handoff Gate、Merge Preparation Gate を順に実施し、human merge 前で停止する。

### 13.2 Trace

- Requirements: `I346-RQ-014`, `I346-RQ-015`
- Acceptance: `I346-AC-014`〜`I346-AC-019`
- Closures: corresponding AC rows, `CL-346-CON-003`, `009`, `010`, `012`, `CL-346-EC-015`, `016`
- Evidence: `I346-EVD-009`, `I346-EVD-010`

### 13.3 Planned contract

#### Scope and allowed paths

- tests and implementation already justified by closed steps
- target Issue `report.md`
- parent Epic `report.md`
- final bounded reviewer-finding repairs within `I346-CON-003`
- PR repair batch artifact only when blocking workflow requires it

#### Forbidden changes

- opportunistic feature/refactor during final gate。
- suppressing/marking expected a failing test without plan amendment/review。
- treating skipped full tests as success。
- changing required checks/workflow policy to make gate pass。
- self-approving reviewer roles。
- merge execution。

#### Red or alternative evidence

Evidence mode: `verification-required`。

S99 is not a production TDD slice. Its negative condition is any failed command, stale head, unresolved closure, reviewer blocker, dirty/unpushed diff, or PR observation mismatch. No failure may be converted to success by omission。

#### Risk-calibrated final obligations

- final candidate revision/status and wheel provenance consistency。
- all step-focused tests on final head。
- `make lint`。
- ordinary `uv run pytest` and policy skip summary。
- explicit `uv run pytest --run-full-regression` and actual body result。
- `spec-dock validate` and `sync --no-github`。
- provider/dogfood diff and no-backfill recheck。
- all required platform host evidence fresh enough for final head; rerun if affected code changed。
- all report decision/EAL rows resolved/non-blocking with rationale。
- reviewer evidence欄を空に正規化したIssue/Epic report ledgerを閉じ、sorted repo-relative path + bytesから`review_content_hash`を計算してcandidate content/diffをfreezeする。
- fresh `qa-reviewer` against acceptance/evidence matrix。
- fresh Issue/Epic-wide `code-reviewer` against final diff and prior Issues interaction。
- fresh `spec-reviewer` against parent/ADR/Issue docs/report。
- bounded repair/fix/re-review loop for P0/P1/required CI only。
- 三者pass後、外部review出力からrole、task/session id、status、findings count、scope、observed_at、機械的gate stateだけを転記し、同じ正規化で`review_content_hash`一致を確認する。それ以外の変更またはhash不一致はfreezeを無効化しfresh reviewへ戻す。
- final commit/push and remote head confirmation。
- pull-request handoff and Merge Preparation records for latest head。
- human merge stop。

#### Green verification command queue

```bash
git status --short
git rev-parse HEAD
git diff --check
make lint
uv run pytest
uv run pytest --run-full-regression
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync --no-github
git diff --check
git status --short
```

Focused step tests are rerun before or as part of full suite when their result may be obscured by aggregate output. Exact command summaries and test counts/duration are recorded in report, not verbatim interaction logs。

#### Refactor guardrail

- no refactor after final Green unless a fresh reviewer finding requires bounded repair。
- review前のbranch/content mutationはlater review/PR observationを無効化する。review後は許可されたreview-evidence転記だけを認め、その他の変更はaffected gatesをnew candidate revisionで再実行する。
- P2/P3 alone do not authorize branch mutation in PR preparation workflow。
- final report wording reflects actual states only。

#### Report evidence destination

- `report.md / Final Quality Gate`
- `report.md / Fast and Full Regression Evidence`
- `report.md / Reviewer Gate Status / S99`
- `report.md / Issue and Epic-wide Review`
- `report.md / Final Review Evidence Transcription`
- `report.md / Commit and Push Evidence`
- `report.md / pull-request handoff Gate`
- `report.md / Merge Preparation Gate`
- `report.md / Residual Risk and Human Handoff`
- parent Epic `report.md / Final Candidate 3 Delivery Trace`

#### Amendment trigger

- final failure reveals missing closure/new bug class outside existing steps。
- repair requires requirement/design/ADR/ownership change。
- required host/reviewer/check unavailable without approved workflow fallback。
- PR base/branch/issue linkage conflicts cannot be resolved from authoritative source。

### 13.4 Delegation and reviewer contract

#### QA review

- **role**: fresh `qa-reviewer`。
- **inputs**: final candidate revision、AC/closure index、test/host evidence、fresh/update/dogfood matrices、reviewer verdict欄以外を閉じたreport。
- **acceptance**: each required closure has valid current evidence; no skipped/unavailable requirement counted as success。
- **focus**: end-to-end distribution truth、failure semantics、test sensitivity、platform evidence、rollback/observability。
- **stop**: stale/missing evidence、unreproducible fixture、full suite not executed。
- **output**: verdict、findings severity/evidence/action、coverage gaps、confidence、report-ready summary。

#### Code review

- **role**: fresh Issue/Epic-wide `code-reviewer`。
- **inputs**: final diff against base、Issue344/345 interaction surfaces、accepted ADRs、all tests/reports。
- **acceptance**: no unresolved P0/P1; strict repair boundary; no unsafe fallback/privacy leak/no-backfill regression。
- **focus**: package/update/runtime/platform/lifecycle/compatibility、test validity、overimplementation。
- **stop**: head changes during review、missing diff context、required host evidence absent。
- **output**: exact findings and scope classification, report-ready summary。

#### Spec review

- **role**: fresh `spec-reviewer`。
- **inputs**: parent Epic R/D/P/report、accepted ADRs、canonical Issue346 R/D/P/report、Issue344/345 completion evidence、final implementation evidence。
- **acceptance**: no unresolved spec blocker; docs/report do not overclaim; delivery boundary correct。
- **focus**: parent boundary、no-backfill interpretation、platform trust boundaries、repair routing、human merge stop。
- **stop**: canonical docs stale/template/contradictory、durable decision stranded only in report。
- **output**: verdict/findings, required amendments, report-ready summary。

#### Blocking repair

- **role**: fresh bounded `dev-coder` or `doc-writer` according to finding root cause。
- **preconditions**: integrated finding batch、current-head observation、fresh consultation evidence when PR workflow requires it、orchestrator disposition、strategy delta、allowed paths。
- **forbidden**: P2/P3-only mutation、scope expansion、policy/check weakening、merge。
- **verification**: finding-specific tests + affected focused/full/validate/sync + re-review/re-observe。

### 13.5 Concrete test-case cards — final gates

#### `tc-346-s99-001` — ordinary fast lane

- **前提**: all steps closed on current local head。
- **操作**: `make lint`、ordinary `uv run pytest`。
- **期待結果**: lint and fast lane success; policy-skipped full tests identified; no claim that full ran。
- **失敗検出**: fast regression、unintended heavy execution、skip reason drift、full claim inflation。
- **検証方法**: command summary + test-lane policy assertion。
- **関連 closure IDs**: `CL-346-AC-014`, `CL-346-CON-009`。

#### `tc-346-s99-002` — explicit full regression

- **前提**: final candidate revision; sufficient time/platform resources; no branch mutation during run。
- **操作**: `uv run pytest --run-full-regression`。
- **期待結果**: full bodies execute; aggregate pass/fail/skip/duration recorded; required integration nodes included。
- **失敗検出**: flag omitted、marker-only run、policy skip counted as pass、selector omission、timeout hidden。
- **検証方法**: pytest output summary + known node collection/receipt。
- **関連 closure IDs**: `CL-346-AC-015`, `CL-346-EC-015`。

#### `tc-346-s99-003` — validate/sync/report freshness

- **前提**: final docs/report/dogfood projection updates staged or committed as appropriate。
- **操作**: validate、sync --no-github、diff check、closure/EAL/decision audit。
- **期待結果**: commands succeed; no unexpected diff; all blocking/open/stale rows resolved; latest head binding present。
- **失敗検出**: report schema gap、sync mutation drift、stale evidence、open decision、verbatim interaction log/authority overclaim。
- **検証方法**: commands + report manual/schema review。
- **関連 closure IDs**: `CL-346-AC-016`, `CL-346-CON-012`, `CL-346-EC-016`。

#### `tc-346-s99-004` — independent final reviews

- **前提**: final candidate revisionと、reviewer evidence欄を空に正規化したcomplete evidence packageの`review_content_hash`がfreeze済み。
- **操作**: fresh QA, Issue/Epic-wide code, spec review in independent contexts。
- **期待結果**: all required reviewers return frozen-content/hash-bound verdicts; no unresolved blockers; unavailable/skipped is not pass。pass後のreport追記は許可されたreview-evidence fieldsだけで、転記後の正規化hashが一致する。
- **失敗検出**: self-review、stale review、missing scope、waiver masquerading as verdict。
- **検証方法**: reviewer receipts/findings + head/diff binding。
- **関連 closure IDs**: `CL-346-AC-017`。

#### `tc-346-s99-005` — commit/push and pull-request handoff Gate

- **前提**: local final gates/reviews complete; 許可されたreview-evidence fieldsだけを外部出力から転記済み; 転記前後の正規化`review_content_hash`一致; branch/base resolution sources known。
- **操作**: review済みcontentと限定転記だけを含むbounded final commit、push、remote head confirmation、existing PR reuse or new PR creation。final commit SHA/clean checkはexternal delivery evidenceへ記録する。
- **期待結果**: PR URL/number/open state/base/head branch/latest SHA/issue linkage/draft-ready decision recorded for pushed head。
- **失敗検出**: uncommitted evidence、push mismatch、duplicate PR、wrong base、stale SHA、missing issue linkage。
- **検証方法**: git/remote/PR metadata receipt。
- **関連 closure IDs**: `CL-346-AC-018`, `CL-346-EC-016`。

#### `tc-346-s99-006` — Merge Preparation Gate and human stop

- **前提**: pull-request handoff Gate for latest pushed head。
- **操作**: observe required/non-required checks、reviews、conflicts、review threads/limitations、blocker history; bounded repair/re-push/re-observe if allowed。
- **期待結果**: latest head has complete merge-preparation record; unresolved blockers lead to human/block state; agent does not merge。
- **失敗検出**: stale observation、required failure ignored、P0/P1 unresolved、thread limitation hidden、agent merge action。
- **検証方法**: PR preparation workflow final JSON/summary + report gate fields + explicit stop state。
- **関連 closure IDs**: `CL-346-AC-018`, `CL-346-CON-010`。

#### `tc-346-s99-007` — repair-boundary audit

- **前提**: complete final diff, decision ledger, reviewer findings and repairs。
- **操作**: map every changed path/behavior to owner closure and classify repair/new feature/spec change。
- **期待結果**: all changes are test/evidence/docs or smallest integration/distribution repair; no hidden Candidate1/2/ADR/ownership change。
- **失敗検出**: orphan diff、broad refactor、requirement change smuggled as fix、unrecorded decision。
- **検証方法**: changed-path-to-closure matrix + code/spec review。
- **関連 closure IDs**: `CL-346-AC-019`, `CL-346-CON-003`。

### 13.6 Final step closure / commit / delivery gate

S99 can close only when:

- all required closure rows have current evidence。
- lint、fast、full、validate、sync、diff/clean requirements are met。
- required Linux/macOS evidence is current for affected code。
- fresh QA/code/spec review has no unresolved blocker。
- report/EAL/decision ledgers are complete and current。
- final commit and push are confirmed。
- pull-request handoff Gate and Merge Preparation Gate records bind latest head。
- final state explicitly says merge is a human action and no agent merge occurred。

Suggested final commit form:

```text
test(epic): Workbench と Artifact import の最終品質を閉じる

- candidate wheel と fresh/update/dogfood 証跡を追加
- platform/privacy/opaque/compatibility 回帰を固定
- Issue/Epic report と docs parity を更新
```

Actual message must describe actual diff; do not claim closure unsupported by evidence。

## 14. Final Exit Contract

### 14.1 Candidate success handoff

The orchestrator may hand off to human merge judgment only when S99 closure is documented. Final response/evidence should identify:

- repository/branch/latest head。
- PR URL/base/head and merge-preparation state。
- required check/review status。
- any remaining non-blocking P2/P3 or platform limitation for human judgment。
- explicit `merge_performed_by_agent=false`。

### 14.2 Blocked exit

Stop as `blocked` or `human gate` when any required closure, host lane, reviewer, full test, latest-head PR observation, or spec boundary is unresolved. Provide the exact blocker, evidence path, and next workflow action; do not use success language。

### 14.3 Epic planning repair exit

Return to Epic planning repair when:

- requirement/design/ADR must change。
- Candidate 1/2 ownership or dependency direction is wrong。
- accepted Linux/macOS primitive/boundary is infeasible。
- final integration requires a new major feature。

The Issue report records the discovery and disposition; durable decisions move to the appropriate canonical artifact before execution resumes。
