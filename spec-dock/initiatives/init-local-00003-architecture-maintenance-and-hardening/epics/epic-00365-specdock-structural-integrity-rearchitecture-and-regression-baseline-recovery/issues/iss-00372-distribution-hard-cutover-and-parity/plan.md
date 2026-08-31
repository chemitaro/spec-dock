---
種別: 実装計画書（Issue）
ID: "iss-00372"
タイトル: "Distribution Hard Cutover And Parity"
関連GitHub: ["#372"]
状態: "planned"
最終更新: "2026-08-30"
依存: ["requirement.md", "design.md"]
親: ["epic-00365", "init-local-00003"]
---

# iss-00372 Distribution Hard Cutover And Parity — 実装計画

詳細: [Issue Plan Guide](../../../../../../docs/authoring/issue-plan.md)

## Planning Level

**selected level: `strict`**

理由:

- D5は D1〜D4 の destructive/recovery semanticsを変更せずに final authority cutoverを固定する必要がある。
- package artifact、fresh consumer、Linux/macOS filesystem behavior、Full Regression verifierを同一 candidateへ束縛する。
- dead seam cleanupが hidden callerを壊す可能性と、schema 1 legacy payload / schema 2 current guardを取り違える危険がある。

`critical` への再評価は、Plan内の stop/interview gateで accepted destructive authority変更が必要と判明した場合だけ行う。通常の dead-code cleanup、CI matrix追加、docs parityは `strict` のまま実施する。

## Baseline と実装原則

この Plan の authoring baselineは `e8b885fcb98e63e6c2e5f32245f8d65345157d1f`。

実装開始時の branch HEADを `B`、最終 candidate SHAを `C` とする。`C` は PR head branchの full commit SHAであり、`pull_request` eventでは `github.event.pull_request.head.sha` を authorityとする。default checkoutの merge ref SHAである `github.sha` は `C` ではない。`B` がこの baselineより進んでいる場合、各 Stepの「先に検査すること」を再実行し、すでに満たされている変更を重複実装しない。accepted D1〜D4 semanticsと本 Requirement/Designに矛盾する差分がある場合は停止する。

原則:

1. inspect first
2. red characterization / structural proof
3. smallest authority-preserving change
4. focused green
5. package/platform integration
6. ordinary fast/lint
7. final current Full Regression verifier
8. same-SHA Strict review
9. human merge
10. issue lifecycle closure

## Artifact ownership

- production authority: `src/spec_dock/managed_distribution.py`
- CLI adapter / dead seam cleanup: `src/spec_dock/cli.py`
- structural + filesystem regression: `tests/unit/infra/test_managed_distribution.py`, `tests/cli_runtime/test_distribution_cutover.py`
- public CLI/package harness: `tests/unit/infra/test_init_update.py`, `tests/integration/test_epic_00343_distribution.py`
- package rules: `pyproject.toml`, `setup.py`（変更は current testsで必要性が証明された場合だけ）
- provider CI: `.github/workflows/provider-ci.yml`
- post-merge Full Regression: `.github/workflows/provider-full-regression.yml`（current verifier routeを維持。D5で不用意にmatrix化しない）
- docs: `README.md`, `spec-dock/docs/README.md`, `spec-dock/docs/migration.md`, provider mirrors under `src/spec_dock/assets/spec_dock/docs/`
- tracked issue report: existing `.../iss-00372-distribution-hard-cutover-and-parity/report.md`。candidate freeze前に実装要約とverification contractまで完成させる
- post-freeze final evidence receipt: candidateを変更しないPR本文、GitHub check summary、CI artifact

## Step 1 — Freeze current route/authority inventory

**Ownership:** analysis only。production変更なし。

### 先に検査する

- `git rev-parse HEAD` と `git status --short`
- `src/spec_dock/cli.py`
- `src/spec_dock/managed_distribution.py`
- `tests/unit/infra/test_managed_distribution.py`
- `tests/cli_runtime/test_distribution_cutover.py`
- `tests/unit/infra/test_init_update.py`
- completed `iss-00368`〜`iss-00371` reports

current public routeから次 entrypointまでを semantic call graphとして再確認する。

- `execute_fresh_distribution`
- `execute_recognized_distribution`
- `execute_deprovision_distribution`
- `execute_explicit_spec_history_purge_distribution`

次に `cli.py` の baseline residual symbols/importsの referencesを確認する。

- `_write_atomic_regular_file`
- `_write_active_pathfile`
- `_write_spec_dock_version`
- `_write_distribution_retry_marker`
- `_remove_distribution_retry_marker`
- `_install_repo_root_shortcut`
- `_rename_distribution_no_replace`
- `_swap_regular_distribution_target_if_bound`
- `_remove_distribution_target_if_bound`
- `DistributionStageOwnership`

### 変更不要条件

branch `B` で上記 dead subgraph/private importsがすでに除去され、current public routesが managed distribution authorityへだけ到達し、対応 absence testも存在する場合、Step 2の production cleanupは skipして Step 3で test adequacyだけ確認する。

### 最小変更条件

上記 helperが定義されるが public `main` / init/update/uninstall routeから到達不能で、referencesが dead helper/test seamに限定される場合は D5-owned cleanupとして Step 2へ進む。

### Stop condition

一つでも public executable routeから CLI-owned managed-file writerへ到達する場合は変更を始めない。D1/D2 predecessor exit defectとして owner decisionへ戻す。名前が違っても semantic roleが同じなら同じ判定にする。

### Red acceptance

baseline `e8b885…` では少なくとも CLI private kernel import/dead writer seamが存在するため、これを拒否する structural assertionを一時的に入れれば redになること。

### Focused command

```bash
uv run pytest tests/unit/infra/test_managed_distribution.py
```

この commandは current fast classificationで実行できる。Step 1では既存 suite greenを baselineとして記録し、new structural assertionのredは Step 2直前に確認する。

**Trace:** R01, R02, R03 / Design §3.1–§3.5, §4.1–§4.2

## Step 2 — Remove only the dead CLI distribution writer subgraph

**Ownership:** `src/spec_dock/cli.py` と direct private test seam。

### 先に検査する

Step 1の reference inventoryを確定し、各 helperの callersが dead subgraph/test onlyであることを再確認する。`managed_distribution.py` の同名/関連 filesystem kernel callersを削除対象へ混ぜない。

### 変更不要条件

Step 1で dead subgraphがすでに不存在なら production sourceは変更しない。

### 最小変更

public behaviorを変えず、到達不能な old CLI writer/helper definitionsと、それだけが必要とする imports/typesを削除する。baselineでは少なくとも次の direct dependencyが cleanup対象候補である。

- CLI direct `_rename_distribution_no_replace`
- CLI direct `_swap_regular_distribution_target_if_bound`
- CLI direct `_remove_distribution_target_if_bound`
- dead marker helper用 `DistributionStageOwnership`

`apply_distribution_plan` のように source comment上「test seam compatibility」とされる importも、actual repository callerを検索して reference 0なら同じ D5 cleanup候補に含めてよい。ただし current live CLI behaviorで使われる symbolを「名前が古い」だけで削除しない。

`tests/cli_runtime/test_distribution_cutover.py` の `cli._write_atomic_regular_file` / `cli._rename_distribution_no_replace` 直接 testは、CLI private writerの removal後は削除または managed_distribution kernel testへ置換する。race safety coverage自体は `managed_distribution.py` の current kernel testsに残す。

### Red / Green

- Red: CLI private filesystem-kernel importまたはdead writer definitionを禁止する new structural assertionが baselineでfail。
- Green: cleanup後に assertion pass、current service route characterization pass、`managed_distribution` kernel safety tests pass。

### Stop condition

cleanupで public output、fresh asset preflight、root operation lock/admission、typed service dispatchを変更する必要が出た場合は、その helperが本当に deadか再判定する。public executable dependencyが見つかれば Step 1 blockerとして停止。

### Focused commands

```bash
uv run pytest tests/unit/infra/test_managed_distribution.py
uv run pytest --run-full-regression --full-regression-shard tests/cli_runtime/test_distribution_cutover.py
```

**Trace:** R02, R03 / AC02 / Design §3.4, §4.1–§4.2, §7

## Step 3 — Lock the structural authority boundary with tests

**Ownership:** existing test files only。新 frameworkは作らない。

### 先に検査する

- `tests/cli_runtime/test_distribution_cutover.py::test_i371_distribution_cutover_has_single_purge_writer` の existing AST approach
- `tests/unit/infra/test_managed_distribution.py` の current imports and marker/guard tests
- `tests/conftest.py` の fast/full classification

### 変更不要条件

existing testsが次の全条件を already enforceする場合は重複 testを追加しない。

1. `cli.py` に managed-file writer helperがない
2. CLI が filesystem kernel private helperを direct importしない
3. old uninstall/purge writer denylistが再導入されない
4. public intentsが typed serviceへ routeする

### 最小変更

既存 AST/runtime spy styleを拡張する。

- fast laneで CLI source boundaryを検査する軽量 assertionを `tests/unit/infra/test_managed_distribution.py` に置くか、同等の既存 fast nodeへ統合する。
- heavy `test_distribution_cutover.py` では end-to-end public routeとnegative regenerationを維持する。
- testは line countではなく AST import/definition/reference roleを検査する。
- `managed_distribution._rename_distribution_no_replace` の存在は denyしない。

### Green

- dead CLI writer/private-kernel edgeを再導入すると testがfailする。
- current schema-2 guard writerや current kernel primitiveを誤ってlegacy扱いしてfailしない。

### Focused commands

```bash
uv run pytest tests/unit/infra/test_managed_distribution.py
uv run pytest --run-full-regression --full-regression-shard tests/cli_runtime/test_distribution_cutover.py
```

**Trace:** R02, R03 / AC01, AC02 / Design §4.2, §7

## Step 4 — Freeze recovery metadata role classification

**Ownership:** tests first。`managed_distribution.py` は accepted behavior gapが証明された場合だけ最小修正。

### 先に検査する

- `_DISTRIBUTION_RETRY_SCHEMA_VERSION`
- `_DISTRIBUTION_JOURNAL_GUARD_SCHEMA_VERSION`
- `_DISTRIBUTION_RETRY_PURPOSE`
- current forward-only purpose constants
- `_UNINSTALL_RETRY_MARKER_REL`
- `OperationJournalStore.prepare_legacy_guard()` live callers
- cross-intent tests from Issue 371

### 変更不要条件

current sourceが次を維持していれば production logicは変更しない。

- schema 2 `.distribution-retry.json` を current guardとして書く
- schema 1 same-path payloadだけを legacy migration inputとして扱う
- `.uninstall-retry.json` を writeしない、自動変換しない
- cross-intent/current-vs-legacy conflictで write 0/manual/fail-closed

### 最小変更

D5 structural/doc testsが filenameだけで writer absenceを要求しないよう修正する。必要なら recovery-role classification testを追加し、writer authorityを payload schema/purposeで固定する。

### Stop condition

`.uninstall-retry.json` current writerが発見される、または current schema-2 guardを削除しないと testをgreenにできない場合は仕様理解が誤っているため停止。D3/D4 owner semanticsを再確認する。

### Focused commands

```bash
uv run pytest tests/unit/infra/test_managed_distribution.py -k 'guard or journal or recovery or legacy'
uv run pytest --run-full-regression --full-regression-shard tests/cli_runtime/test_distribution_cutover.py -k 'retry or recovery or journal or uninstall'
```

`-k` は current collected namesに対する broad selectorとして使う。final gateでは file-level runも必須とする。

**Trace:** R04, R05 / AC03, AC04 / Design §3.3, §4.3–§4.4

## Step 5 — Complete public semantic and preservation matrix

**Ownership:** characterization tests。production変更は regressionが current accepted contractから逸脱している場合だけ。

### 先に検査する

`tests/unit/infra/test_init_update.py` と `tests/cli_runtime/test_distribution_cutover.py` の existing D1〜D4 tests。特に Issue 371 の typed deprovision/purge service route、JSON schema 1、retry command、cross-intent manual behaviorを再利用する。

matrix:

| flow | minimum cases |
|---|---|
| fresh | absent / empty / preserved workspace |
| recognized | no-op / managed refresh / blocker / recovery |
| deprovision | dry-run / apply / preserve specs+Workbench+unknown contract / recovery |
| purge | dry-run / explicit apply / preserve Workbench / cross-intent mismatch |

### 変更不要条件

existing testsが public command/flag/text/JSON/exit/sanitization/preservationを全て current contractどおり固定していれば new duplicate golden testを増やさない。

### 最小変更

D5で CLI dead seam cleanupによって testが private helperへ依存している箇所だけ public/typed service characterizationへ置換する。public schemaや wordingを新しく設計しない。

### Green

- no new command/flag/schema
- one JSON object
- existing exit mappings
- retry authority mismatchは manual/no guessed command
- unknown/modified/user-owned preservationが intent contractどおり

### Focused commands

```bash
uv run pytest --run-full-regression --full-regression-shard tests/unit/infra/test_init_update.py -k 'init or update or uninstall or i368 or i369 or i370 or i371'
uv run pytest --run-full-regression --full-regression-shard tests/cli_runtime/test_distribution_cutover.py
```

**Trace:** R01, R05 / AC01, AC04 / Design §4.4, §7

## Step 6 — Close provider/dogfood/wheel/sdist/installed/fresh parity

**Ownership:** package tests first。`pyproject.toml` / `setup.py` は red evidenceがある場合だけ変更。

### 先に検査する

- `pyproject.toml` package-data / exclude-package-data
- `setup.py` `_prune_stale_build_outputs()` / custom `sdist`
- `src/spec_dock/assets/install_root`
- `src/spec_dock/assets/spec_dock`
- `src/spec_dock/assets/managed_distribution.json`
- checked-in `spec-dock/` mapped dogfood files
- `tests/unit/infra/test_init_update.py` Issue 69 build helpers and dogfood mirror tests
- `tests/integration/test_epic_00343_distribution.py` candidate wheel/sdist tests

### 変更不要条件

current candidateで existing source→wheel/sdist byte/mode equality、installed/fresh consumer parity、dogfood mirror parity、stale negative testsが greenなら package configurationを触らない。

### 最小変更

1. D5 cleanupで package inventoryに影響する source fileがある場合、wheel/sdistに不要 legacy artifactが残らないことを testで固定する。
2. existing `test_tc_360_s80_wheel_and_sdist_*` harnessを拡張し、isolated candidate artifactから deprovision/purge public routeの representative packaged behaviorを確認する。
3. fresh/recognized/deprovision/purgeの deep race matrixを package testへ重複させない。
4. stale-build regressionが出た場合のみ `pyproject.toml` / `setup.py` の existing prune/exclude mechanismへ最小追記する。

### Red / Green

- Red: deliberately seeded stale output、source/package byte drift、checkout fallback、provider/dogfood driftのいずれかを fixtureで検出できる。
- Green: provider/dogfood/wheel/sdist/installed/fresh surfaceが expected identityに一致し、isolated packaged routeが current service authorityを使用する。

### Focused commands

```bash
uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_mirror_docs_match_provider_assets
uv run pytest --run-full-regression --full-regression-shard tests/integration/test_epic_00343_distribution.py
```

必要に応じて existing exact nodesを先に速く回す。

```bash
uv run pytest --run-full-regression --full-regression-shard \
  tests/integration/test_epic_00343_distribution.py::test_tc_360_s80_wheel_and_sdist_catalog_bytes_and_modes_match_provider \
  tests/integration/test_epic_00343_distribution.py::test_tc_360_s80_wheel_and_sdist_fresh_and_updated_consumers_match_provider
```

D5で packaged deprovision/purge coverageを追加した後の final package gateは file-level commandを使い、新規 test名をこの Planから先取りして固定しない。

**Trace:** R06 / AC05, AC06 / Design §3.6–§3.7, §5

## Step 7 — Add required Linux/macOS provider parity gate

**Ownership:** `.github/workflows/provider-ci.yml`。consumer `.github/workflows/ci.yml` とは分離。

### 先に検査する

- `.github/workflows/provider-ci.yml`
- `.github/workflows/provider-full-regression.yml`
- `tests/conftest.py` lane policy
- current provider-only workflow not-shipped fast test
- current host behavior of `_resolve_distribution_no_replace_rename()`

### 変更不要条件

branch `B` で既に provider-only required jobが `ubuntu-latest` / `macos-latest` の両方で `github.event.pull_request.head.sha` を明示 checkoutし、各 runnerの `git rev-parse HEAD` と一致する同一 `C` に対して D5 focused suiteを実行し、best-effortでない場合は workflow変更不要。

### 最小変更

baselineでは macOS jobがないため、`provider-ci.yml` に最小の provider-only OS matrix/focused jobを追加する。

- runner: `ubuntu-latest`, `macos-latest`
- Python: current provider CIと同じ 3.11 unless repository-wide supported version policyが branch `B` で変更済み
- installation: current provider CIと同じ pip/uv setup
- candidate identity: `C = github.event.pull_request.head.sha`
- checkout: `actions/checkout` の `ref` に `C` を明示し、test前に `git rev-parse HEAD == C` を検証
- same focused command set on both OS
- `continue-on-error` 不可
- consumer install_rootへ provider workflowを copyしない

focused command setは少なくとも current `tests/unit/infra/test_managed_distribution.py` と D5 cutover/package representative heavy nodesを含める。CI durationを理由に global Full Regressionを両OSで回す必要はない。

### Linux/macOS red acceptance

baseline workflow sourceには macOS runnerがなく、D5 platform gateは未成立。

### Green

- PR candidate `C` で Linux/macOS jobsが同じ `github.event.pull_request.head.sha` を使用し、各 checked-out HEADが `C` と一致
- real no-replace pathが両 hostで成功、または意図した capability-negative fixtureは target write 0で既存 diagnosticを返す
- root/parent rebind、guard/journal recovery、cross-intent write-zero、package representative parityが両OS green

### Stop condition

normal `macos-latest` で `renameatx_np(RENAME_EXCL)` 等 current required capabilityが実用上成立せず、fail-closedだけでは R07 の supported parityを満たせない場合、fallbackを勝手に実装しない。platform support semanticsの owner decisionへ戻す。

### Local configuration validation

```bash
uv run pytest tests/unit/infra/test_managed_distribution.py
uv run pytest --run-full-regression --full-regression-shard tests/cli_runtime/test_distribution_cutover.py
```

最終 Linux/macOS greenは GitHub Actions candidate SHA evidenceで確定する。

**Trace:** R07, R10 / AC07, AC11 / Design §6, §9

## Step 8 — Align recovery/documentation wording and provider projections

**Ownership:** docs/projection only。behaviorを docsに合わせて変えない。

### 先に検査する

- `README.md`
- `spec-dock/docs/README.md`
- `spec-dock/docs/migration.md`
- `src/spec_dock/assets/spec_dock/docs/README.md`
- `src/spec_dock/assets/spec_dock/docs/migration.md`
- current recovery constants/tests in `managed_distribution.py`

### 変更不要条件

schema 1 legacy distribution retry payload、schema 2 current forward guard、current journal、legacy uninstall markerの違いが既に誤解なく説明され、dogfood/provider bytesも一致している場合は docs変更不要。

### 最小変更

baseline wordingを次の semantic vocabularyへ統一する。

- `spec-dock/.distribution-retry.json` schema 1: legacy migration input
- same pathname schema 2: current forward guard
- `.distribution-journal.json`: current journal
- `.uninstall-retry.json`: legacy reader-only/manual evidence
- recovery: same root/intent/authority/contract/plan/protocolの forward recovery
- rollback: active current journal/guardを old installerへ戻して解決することを推奨しない
- completed Issue 368〜371: future/compatibility ownerとして説明せず、current fresh/reconciliation/deprovision/purge authorityとして記述する

checked-in `spec-dock/docs/*.md` を変更したら corresponding provider asset copyも同じ bytesへ更新し、mirror testを通す。

### Green

```bash
uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_mirror_docs_match_provider_assets
uv run pytest
```

**Trace:** R09 / AC10 / Design §8

## Step 9 — Run ordinary quality gates without mixing lanes

**Ownership:** verification only。

### 先に検査する

`tests/conftest.py` が branch `B/C` でも同じ lane policyを持つことを確認する。policy自体が別 Issueで変更済みなら current policyに従い、この Planの historical commandを盲目的に使わない。

### Required ordinary gates

```bash
make lint
uv run pytest
./spec-dock/scripts/spec-dock validate
```

`uv run pytest` の skipped heavy nodesを failure扱いしない一方、これを heavy/full-regression greenの代替にも使わない。

### Required focused heavy gates

```bash
uv run pytest --run-full-regression --full-regression-shard tests/cli_runtime/test_distribution_cutover.py
uv run pytest --run-full-regression --full-regression-shard tests/integration/test_epic_00343_distribution.py
```

D5で touched `tests/unit/infra/test_init_update.py` heavy casesがある場合は同じ shard modeで relevant selectorまたは file runを実行する。

### Green

- lint pass
- ordinary fast lane pass
- focused heavy files pass
- no lane classification conflict

**Trace:** R05, R08 / AC04, AC08 / Design §7

## Step 10 — Run current Full Regression verifier on final candidate

**Ownership:** verification/evidence。ledgerを書き換えて candidate failureを隠さない。

### 先に検査する

- current `tests/conftest.py`
- `.../iss-00368.../artifacts/full-regression-ledger.json`
- `.../iss-00368.../artifacts/verify-full-regression.py`
- `.github/workflows/provider-full-regression.yml`

### 変更不要条件

verifier/ledgerが current policyどおり candidate ancestor/signature contractを表現していれば変更しない。

### Required command

clean candidate `C` から実行する。

```bash
uv run python spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00365-specdock-structural-integrity-rearchitecture-and-regression-baseline-recovery/issues/iss-00368-recognized-workspace-reconciliation/artifacts/verify-full-regression.py --shards 4
```

### Green

verifierの current result contractが `verified`/exit 0相当を返し、unexpected failure/error、missing approved failure、signature mismatchがない。

### Failure classification

- D5 changeにより新規に生じた failure: D5で修正し、candidate SHAを更新して Step 6以降の relevant evidenceを再取得。
- current ledger contract自体と矛盾する unrelated historical failure: D5で ledgerを書き換えて隠さず、次candidate freeze前のreportまたはcandidateを変更しないPR/check evidenceへ記録する。D5 final completionは verifier greenなしに宣言しない。
- timingだけの増減: verifier completion/CI resource issueとして調査するが、過去600秒等を acceptance thresholdへ昇格しない。

### Stop condition

ledgerを変更しないと D5 unrelated failureを pass扱いできない場合は、Issue 372のscopeで勝手に baseline policyを再定義しない。

**Trace:** R08, R10 / AC09, AC11 / Design §7.3, §9

## Step 11 — Bind same-candidate evidence without mutating the candidate

**Ownership:** tracked reportのpre-freeze completionと、PR/check/CI artifact上のpost-freeze final receipt。

### 先に検査する

```bash
git rev-parse HEAD
git status --short
```

`C` を確定し、dirty working treeで package receiptやfinal Full Regression evidenceを取らない。

`report.md` はこの時点より前に実装要約、変更境界、verification contractまでcommit済みでなければならない。`C` 確定後にfinal resultをtracked reportへ追記しない。

### Evidence table to record without changing `C`

PR本文、GitHub check summary、CI artifactの組合せに次を記録する。

- candidate SHA `C`
- changed production/test/CI/docs paths
- wheel SHA-256
- sdist SHA-256
- isolated package/fresh consumer command/result
- Linux provider CI run/check + `github.event.pull_request.head.sha` + checked-out `git rev-parse HEAD`
- macOS provider CI run/check + `github.event.pull_request.head.sha` + checked-out `git rev-parse HEAD`
- ordinary `make lint`, `uv run pytest`, `validate`
- focused heavy commands/results
- Full Regression verifier command/result
- structural absence result
- docs/provider mirror parity result

tracked evidence fileを新設しない。PR本文はrepository guidelineどおりtest outputとchange impactを記録し、GitHub check summary/CI artifactの再検証可能なrun/check/artifact identityを参照する。これらの記録はcandidate commitを変更しない。

### Green

全 final evidenceが同じ `C` に結び付き、receipt記録後もbranch HEADが `C` のままである。Strict remediationまたはtracked report訂正で SHAが変わったら新candidateとしてfreezeし、stale evidenceを final欄から外して影響 gateを再実行する。

**Trace:** R06, R07, R08, R09, R10 / AC05–AC11 / Design §9

## Step 12 — Strict review, Human PR gate, Issue finish を分離する

**Ownership:** delivery process。

### Gate A — Implementation Completion

次が全て greenで初めて implementation complete とする。

- AC01〜AC11
- source clean candidate `C`
- same-SHA package/Linux/macOS/tests/docs/Full Regression evidence
- `C` に含まれるpre-freeze reportと、`C` を変更しないpost-freeze PR/check/CI artifact receipt

### Gate B — Strict Review Pass

exact `C` を対象に Strict reviewする。review findingを修正した場合、new SHA `C2` を作り、finding影響範囲に加えて package/platform/Full Regression/same-SHA bindingを再確認する。reviewed SHAとfinal SHAが違う状態を pass扱いしない。

### Gate C — Human PR Merge Gate

repositoryの human-operated merge policyに従う。agent/coderは tests passやStrict reviewを根拠に merge完了とみなさない。

### Gate D — `issue finish`

merge/delivery evidenceが成立した後の lifecycle closureとして実行する。`issue finish` 自体は commit、push、PR、merge、validate、test、review completionを保証しない。

### Stop condition

Strict review pass前、Human merge前、または final candidate evidence不一致の状態で Issue 372完了を宣言しない。

**Trace:** R10 / AC12 / Design §10

## Final acceptance matrix

| Requirement | Primary Plan steps | Primary tests/evidence |
|---|---|---|
| I372-R01 | 1, 5 | public route characterization, D1〜D4 focused matrix |
| I372-R02 | 1, 2, 3 | AST/import boundary + runtime spy |
| I372-R03 | 1, 2, 3 | CLI dead seam absence, managed kernel retained |
| I372-R04 | 4 | guard/journal/legacy/cross-intent regression |
| I372-R05 | 5, 9 | init/update/uninstall public JSON/text/exit/preservation tests |
| I372-R06 | 6 | dogfood mirror + wheel/sdist + isolated installed/fresh consumer |
| I372-R07 | 7 | same-SHA Ubuntu/macOS provider checks |
| I372-R08 | 9, 10 | ordinary fast + focused shard + current Full Regression verifier |
| I372-R09 | 8 | README/migration/provider mirror parity |
| I372-R10 | 10, 11, 12 | same-candidate evidence + separated process gates |

## Final exit conditions

Issue 372 implementationは次を全て満たした場合にのみ coder handoff可能である。

1. predecessor executable-writer blockerがない。
2. CLI dead legacy writer/private-kernel seamが sourceから除去され、absence testがある。
3. current schema-2 forward guard / journal / schema-1 migration / legacy uninstall reader boundaryを壊していない。
4. public command/flag/text/JSON/exit/data-preservation contractが green。
5. provider/dogfood/wheel/sdist/installed/fresh consumer parityが green。
6. Ubuntu/macOS focused provider checksが同一 candidate SHAで green。
7. `make lint`、ordinary `uv run pytest`、focused heavy suitesが各 laneの正しい方法で green。
8. current Full Regression verifierが final candidateで green。
9. README/migration/provider projectionが current implementationと一致。
10. source/package/platform/test/docs evidenceが同じ candidate SHAへ束縛される。
11. Strict reviewは exact final candidateに対して pass。
12. Human PR mergeと `issue finish` は implementation/review completionとは別 gateとして処理される。

この exitを満たすために Windows、generic transaction framework、automatic rollback、automatic Issue creation、unrelated Full Regression remediation、新 public APIを追加しない。

## 2026-08-30 収束Addendum（実施済み計画を遡及変更しない）

既存Step 1〜9およびM1〜M5の実施記録・成果はそのまま保持する。Step 10で観測済みのredも書き換えず、次の追加workを順番に行う。

### Step 10A — external quality-governance dependency `iss-00382`

- accepted ADR、Issue 382 requirement/design/planをauthorityに、repository-level evaluatorを別IssueとしてTDD実装する。
- Issue 372固有exception、historical row削除、旧failure test復活、distribution production変更でgreen化しない。
- Issue 382はfocused/ordinary/Full Regression/Strictを通したmerge-ready PRまで整え、人間mergeを待つ。

### Step 10B — accepted canonical verifierでIssue 372を再判定する

- Issue 382がhuman mergeされdependencyがsatisfiedになったことを確認する。
- merged baseをIssue 372 branchへ通常のrepository workflowで取り込み、新candidate `C2`を形成する。
- `uv run python -m scripts.quality.verify_full_regression --shards 4`をclean `C2`で実行する。
- retained-skill successor、全active row、unexpected failure/errorがaccepted typed resultでgreenでなければStep 11へ進まない。

### Step 11A — new candidate evidenceを再束縛する

既存Step 11のevidence tableを`C2`で再取得する。旧candidateのpackage、Linux/macOS、Full Regression、Strict receiptを流用しない。M1〜M5 production diffに追加修正がない場合でもbase/candidate SHAが変わるためsame-SHA gateは再実行する。

### Step 12A — Final Quality Gateとdelivery closure

- exact pushed `C2`へStrict Final Quality Gateを行い、finding修正でSHAが変われば影響gateとreviewを繰り返す。
- P0/P1=0かつreview passのmerge-ready PRを人間へ渡す。
- human merge後にのみIssue 372の`issue finish`と最終status同期を行う。

**Trace:** I372-R11, I372-R12 / I372-AC13, I372-AC14 / Design §13
