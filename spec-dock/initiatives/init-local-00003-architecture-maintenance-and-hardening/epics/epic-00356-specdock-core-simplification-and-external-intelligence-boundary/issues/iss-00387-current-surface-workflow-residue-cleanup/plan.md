---
種別: 実装計画書（Issue）
ID: "iss-00387"
タイトル: "Current Surface Workflow Residue Cleanup"
関連GitHub: ["#387"]
状態: "approved"
最終更新: "2026-08-31"
依存: ["requirement.md", "design.md"]
親: ["epic-00356", "init-local-00003"]
---

# iss-00387 Current Surface Workflow Residue Cleanup — 実装計画

詳細: [Issue Plan Guide](../../../../../../docs/authoring/issue-plan.md)

## 1. Planning Level

**standard**を選択する。

理由:

- public CLIの追加・削除やdata migrationはない。
- 変更はCurrent docs、placeholder、内部request shape、package/test hygieneに限定される。
- ただしprovider/dogfood projection、`issue start` checkout ordering、package inventory、Historical/Epic #384境界を横断するためlightでは不足する。
- security、不可逆data、external API、release architectureを変更しないためstrict/criticalは不要である。

再評価条件:

- `checkout_active_target()`のbehavior変更が必要になる。
- distribution ownership、uninstall、journal、Full Regression policyの変更が必要になる。
- user-owned dataまたはHistorical evidenceのmigrationが必要になる。
- public CLI contractを変更する必要が判明する。

いずれかが成立した場合は実装を止め、本Issueのscope変更ではなくEpic #384または別Issueへのhandoffを優先する。

## 2. 目標と実施状態

### 2.1 目標

Current surfaceを親Epic #356の契約へ収束させ、Luna Max coderがTDDで最小実装を行い、human merge gateへ渡せるcandidateを作る。

### 2.2 現在の状態

- Issue作成、依存設定、`issue start`: 実施済み
- Requirement/Design/Planの具体化: 本計画作成時点で実施中
- production implementation: 未着手
- RED/GREEN test: 未着手
- quality verification、PR: 未着手

以後の実施結果は本欄を書き換えて捏造せず、`report.md`へ実測として記録する。

## 3. 依存と実装原則

- `iss-00357`〜`iss-00360`は完了済みで、本Issueのdependency readinessは成立している。
- production writerは一人とし、step/milestone単位で引き継ぐ。
- 各behavior stepは必ずRED → GREEN → REFACTORの順で行う。
- provider sourceを先に編集し、dogfood projectionを同期する。
- 既存test file/helperを優先し、新しいframeworkやglobal scannerを作らない。
- 実行していないtestをpassと記録しない。
- Epic #384所有fileに差分を作らない。

## 4. Milestone

| Milestone | 内容 | Exit |
|---|---|---|
| M0 | baseline/proof | exact SHA、target path、definition-only/phantom proofを記録 |
| M1 | Current text convergence | active-none、README、overviewのRED/GREENとparity |
| M2 | active request contraction | target-only request、selection-only、issue start非回帰 |
| M3 | package/test hygiene | stale config除去、conditional constants判定、clean build |
| M4 | integrated guard | Current inventory、Historical exclusion、focused/ordinary checks |
| M99 | final handoff | current verifier、fresh consumer、diff audit、Report、PR-ready candidate |

## 5. S00 — Baselineと削除proof（M0）

### 5.1 目的

実装開始点とscopeを固定し、条件付き削除を推測で行わない。

### 5.2 Read-only確認

```bash
git status --short
git rev-parse HEAD
git branch --show-current
git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}'
git rev-parse '@{upstream}'
./spec-dock/scripts/spec-dock active show
./spec-dock/scripts/spec-dock deps check --id iss-00387 --github --json
```

期待:

- branchは`iss-00387-current-surface-workflow-residue-cleanup`。
- worktreeはimplementation開始前にclean。
- local HEADとupstreamが一致。
- active Issueは`iss-00387`。
- dependency readinessは`true`。

### 5.3 Inventory

```bash
rg -n 'ActiveSetArgs|SetActiveRequest|checkout_active_target|active set .*--checkout|Evidence Adoption Ledger|Issue 359' \
  README.md src/spec_dock/assets/spec_dock spec-dock tests

rg -n 'tests.cli_runtime.test_delegated_authoring|assets/install_root/.codex/\*\*' \
  pyproject.toml

rg -n '_ISSUE_359_EXPECTED_CODEX_CONFIG|_REQUIRED_ISSUE_PROFILE_TEMPLATE_PATHS' \
  tests/unit/infra/test_init_update.py
```

### 5.4 Conditional deletion proof

definition-only候補ごとにASTの`Name(ctx=Load)`とrepository-wide referenceを確認する。dynamic lookupの可能性を否定できなければ保持する。判定と根拠を後でReportへ記録する。

package-data globは次を確認する。

- `src/spec_dock/assets/install_root/.codex`が存在しない。
- current `.agents`と`.github`が存在する。
- clean baseline buildのarchiveに`.codex` entryがない。

### 5.5 Exit

- implementation baseline SHAを記録。
- exact対象pathとno-touch pathを確定。
- 条件付き候補ごとに`delete`または`retain`を証拠付きで決定。

## 6. S01 — TDD: Current text drift guard（M1 RED）

### 6.1 Test ownership

主に`tests/unit/infra/test_authoring_kit_assets.py`を使う。package projectionに既存assertionがある場合だけ`tests/unit/infra/test_init_update.py`を補助的に使う。

### 6.2 先に追加する失敗test

1. active-none三scopeのprovider contentがminimal placeholderと一致する。
2. provider/dogfood pairがbyte一致する。
3. root READMEに`active set --checkout`のCurrent案内とEAL必須説明がない。
4. root READMEにselection-only、`issue start`、canonical rewrite説明がある。
5. Authoring overviewが二skillを現在形で案内し、Issue #359未来形を含まない。
6. Current vocabulary inventoryにHistorical path/fixtureと`docs/migration.md`が含まれない。
7. `docs/migration.md`はCurrent vocabulary scanから外れても、既存のlink/parity検証対象には残る。
8. synthetic旧phraseをCurrent detectorへ渡すと違反になり、migration-only sampleはCurrent detectorへ渡されない。

Test名はIssue番号だけでなくdurable contractを表す。例:

```text
test_active_none_reports_are_minimal_current_placeholders
test_root_readme_describes_selection_only_active_contract
test_current_authoring_surfaces_exclude_historical_evidence
```

### 6.3 RED確認

```bash
uv run pytest tests/unit/infra/test_authoring_kit_assets.py -q
```

追加testが現行残滓を理由に失敗することを確認する。test setup errorやpath typoによる失敗はREDとして採用しない。

## 7. S02 — GREEN: Current docs/placeholder（M1 GREEN/REFACTOR）

### 7.1 Provider-first実装

1. provider active-none report三件をDesign §3.3のminimal contentへ縮小する。
2. root READMEから`active set --checkout`のexample/recovery/normalization案内を除き、`issue start`へ置換する。
3. root READMEのEAL必須説明をevidence review + canonical rewriteへ置換する。
4. provider Authoring overviewを二skillの現在形へ更新する。
5. provider変更を対応dogfood pathへ同期する。

### 7.2 変更禁止

- Historical guide/fixture/initiative history
- installed skill本文
- consumer/provider workflow
- migration-only説明
- active-none directory/file構造

### 7.3 GREEN

```bash
uv run pytest tests/unit/infra/test_authoring_kit_assets.py -q
```

```bash
cmp src/spec_dock/assets/spec_dock/docs/authoring/overview.md \
  spec-dock/docs/authoring/overview.md

for scope in initiative epic issue; do
  cmp \
    "src/spec_dock/assets/spec_dock/system/active-none/$scope/report.md" \
    "spec-dock/system/active-none/$scope/report.md"
done
```

### 7.4 REFACTOR/Exit

- exact placeholder mappingをtest内で一か所にまとめる。
- repository-wide raw word banやproduction validatorを作らない。
- M1の全Current text assertionとparityがgreen。

## 8. S03 — TDD: active selection contract（M2 RED）

### 8.1 Test ownership

- `tests/unit/application/test_set_active.py`
- `tests/cli_runtime/test_storage_core_cli.py`
- 必要なordering非回帰だけ`tests/cli_runtime/test_issue_lifecycle.py`

### 8.2 先に追加/更新する失敗test

1. `dataclasses.fields(ActiveSetArgs)`が`target_ref`, `target_display`だけ。
2. `dataclasses.fields(SetActiveRequest)`が`target`だけ。
3. fail-fast fake Git/GitHub/dependency portを渡しても`set_active()`が呼ばない。
4. `set_active()`のresultは`branch is None`。
5. CLI `active set`のpositional/`--id`/`--github-issue`は従来どおり成功する。
6. CLI helpに`--checkout`、`--force`、network flagが現れない。
7. `issue start`はdependency check後にcheckoutし、checkout後にactive writeする。

### 8.3 RED

```bash
uv run pytest tests/unit/application/test_set_active.py -q
uv run pytest --run-full-regression --full-regression-shard \
  tests/cli_runtime/test_storage_core_cli.py -q
uv run pytest --run-full-regression --full-regression-shard \
  tests/cli_runtime/test_issue_lifecycle.py -q
```

field shape testが旧fieldを理由に失敗することを確認する。既存full-regression testはpermission flagを明示して実行する。

## 9. S04 — GREEN: target-only request（M2 GREEN/REFACTOR）

### 9.1 編集順

1. provider `commands/active.py`
   - `ActiveSetArgs`を二fieldへ縮小。
   - `_active_set_args()`のhidden default extractionを削除。
   - `_run_active_set()`は`SetActiveRequest(target=...)`だけを生成。
2. provider `application/contracts.py`
   - `SetActiveRequest`を`target`だけへ縮小。
3. provider `application/set_active.py`
   - conditional checkout blockを削除。
   - `branch=None`で既存result shapeを返す。
   - `checkout_active_target()`は無変更。
4. provider `application/issue_lifecycle.py`
   - checkout後のcall siteをtarget-only requestへ更新。
5. provider runtime変更をdogfood runtimeへ同期。
6. 全`SetActiveRequest(...)` call siteをrepository searchで更新。

### 9.2 GREEN

S03の三commandを同じpermission flag付きで再実行する。特にCLI testをpolicy skipでGREEN扱いしない。

```bash
uv run pytest tests/unit/application/test_set_active.py -q
uv run pytest --run-full-regression --full-regression-shard \
  tests/cli_runtime/test_storage_core_cli.py -q
uv run pytest --run-full-regression --full-regression-shard \
  tests/cli_runtime/test_issue_lifecycle.py -q
```

加えて:

```bash
rg -n 'SetActiveRequest\(' src/spec_dock/assets/spec_dock/scripts spec-dock/scripts tests

cmp \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py \
  spec-dock/scripts/spec_dock_runtime/application/set_active.py
```

### 9.3 No-change proof

implementation baselineと比較し、`checkout_active_target()`のsignature/body/docstringに差分がないことを確認する。functionを別helperへ移すことも禁止する。

### 9.4 REFACTOR/Exit

- unused imports/fieldsだけを除く。
- `ActiveSetResult`等のunrelated result shapeを整理しない。
- M2 test、provider/dogfood parity、helper no-diffがgreen。

## 10. S05 — TDD/GREEN: package/test hygiene（M3）

### 10.1 RED test

既存`tests/unit/infra/test_init_update.py`へ、次を確認するfocused assertionを追加する。

- stale mypy module entryがない。
- phantom `.codex/**` package-data globがない。
- current `.agents/**`と`.github/**` package-dataがある。
- source `install_root/.codex`が存在しない。

```bash
uv run pytest --run-full-regression --full-regression-shard \
  tests/unit/infra/test_init_update.py -k 'package_data or install_root' -q
```

現行stale entryにより追加assertionが失敗することを確認する。

### 10.2 GREEN

1. `pyproject.toml`から対象二entryだけを削除。
2. S00 proofが成立したdefinition-only constantだけを削除。
3. unrelated config、Historical path mapping、Full Regression selectorを変更しない。

### 10.3 Verification

```bash
uv run pytest --run-full-regression --full-regression-shard \
  tests/unit/infra/test_init_update.py -k 'package_data or install_root' -q
make lint
uv run pytest --collect-only -q
```

clean buildはrepository既存の安全なbuild commandを使う。既存`build/`/`dist/`を削除する必要がある場合は、対象pathを確認し、本Issueのbuild artifactだけであることを確認してから行う。

```bash
uv build
python -m zipfile -l dist/*.whl
tar -tf dist/*.tar.gz
```

archiveにcurrent二skillと`ci.yml`があり、`install_root/.codex`がないことを確認する。

### 10.4 Exit

- stale configがない。
- current package inventoryが維持される。
- definition-only候補のdelete/retain判断が証拠付きで確定。
- M3 focused test、lint、collection、buildがgreen。

## 11. S06 — Integrated guard refactor（M4）

### 11.1 Consolidation

- Current text inventoryを一つのexplicit tuple/mappingへ整理。
- Historical path/fixtureと`docs/migration.md`をCurrent vocabulary inventoryから除外するassertionを固定。
- migration文書の既存link/parity testは保持し、Current vocabulary scanだけを分離する。
- public CLI、application behavior、issue-start orderingの重複assertionを減らす。
- source substringだけでbehaviorを証明せずfail-fast port testを残す。
- Issue-specific temporary helperを増やさない。

### 11.2 Focused verification

```bash
uv run pytest \
  tests/unit/infra/test_authoring_kit_assets.py \
  tests/unit/application/test_set_active.py -q

uv run pytest --run-full-regression --full-regression-shard \
  tests/cli_runtime/test_issue_lifecycle.py \
  tests/cli_runtime/test_storage_core_cli.py -q

uv run pytest --run-full-regression --full-regression-shard \
  tests/unit/infra/test_init_update.py \
  -k 'active_none or package_data or install_root' -q
```

`-k`使用時はcollection outputで必要testが選択されていることを確認する。

### 11.3 Exit

- Current violation mutation test、実file test、Historical exclusionがgreen。
- new production abstractionとtest lane config差分がない。

## 12. S90 — Package/fresh consumer integration

### 12.1 Fresh init

```bash
TMP_ROOT="$(mktemp -d)"
CONSUMER="$TMP_ROOT/consumer"
mkdir -p "$CONSUMER"
uvx --no-cache --from . spec-dock init "$CONSUMER"
```

### 12.2 Verification

- consumerのactive-none三件とoverviewがprovider sourceと一致する。
- `active set --help`はselection-onlyで、`--checkout`を受理しない。
- `issue start --help`が存在する。
- installed assetはcurrent二skillとconsumer `ci.yml`。
- retired `.codex` assetを生成しない。
- consumer `spec-dock validate`が成功する。

live GitHubを必要とするcommandはfresh consumer smokeで実行しない。

### 12.3 Exit

distribution implementationへ差分を作らず、built packageからCurrent contractを再現できる。

## 13. S99 — Final verificationとhandoff（M99）

### 13.1 Static/focused/ordinary

```bash
make lint
git diff --check
uv run pytest
```

ordinary laneのpass/skip/failure数とdurationを実測どおり記録する。policy skipをexecuted passと数えない。

### 13.2 SpecDock

```bash
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync --no-github
./spec-dock/scripts/spec-dock validate
```

sync後のtracked diffを確認し、本Issue外のgenerated changeをcommitしない。

### 13.3 Current Full Regression

現行policyを変更せず、repositoryが定めるcurrent verifierを実行する。

```bash
uv run python -m scripts.quality.verify_full_regression --shards 4
```

failure時は本Issue差分を修正し、ledger/timing/shard/provider workflowを変更しない。Epic #384の将来計画を理由にfailureを無視しない。

### 13.4 Diff audit

implementation baselineからのchanged pathを列挙する。次に差分がないことを確認する。

- `src/spec_dock/managed_distribution.py`
- `src/spec_dock/assets/managed_distribution.json`
- `src/spec_dock/cli.py`
- current二skillとconsumer CI
- provider CI/Full Regression workflow
- ledger/timing/scripts/quality/test lane config
- Historical guide/fixtureと他Issueの履歴

本Issue historyの許可deltaはR/D/P/Reportだけとする。

### 13.5 Report

`report.md`の薄い三sectionへ実測だけを記録する。

- Outcome: actual changed filesと残滓除去結果
- Verification: command、pass/skip/failure、package/fresh consumer。version管理Reportへfinal commit SHAは記録しない
- Residual Risks / Follow-ups: conditional candidate判断、Epic #384 handoff、未実施事項

長いlog、仕様、意思決定履歴をReportへ複製しない。

### 13.6 Delivery

1. commit identityをrepository contractと照合。
2. explicit pathだけをstage。
3. focused commitを作成しpush。
4. このcommit後に確定したfinal candidate SHAを、version管理ReportではなくPR本文またはhandoff evidenceへ記録する。SHA記録のための追加commitは作らない。
5. Issue #387を参照するPRを作成する。
6. independent ChatGPT code review/Final Quality Gateを固定SHAで実施し、指摘があればTDDで修正・再reviewする。修正commit後は新しいSHAをPR/handoff evidenceで更新する。
7. merge-ready状態で停止する。agentはmergeしない。
8. human merge前に`issue finish`を実行しない。

## 14. Rollback / forward recovery

- docs/placeholder、active request、package hygieneを小さいcommit境界に分け、各境界を独立revert可能にする。
- active request regressionはpublic `active set --checkout`を復活させず、call siteをforward-fixする。
- package inventory欠落は対象config変更だけを戻し、managed manifestへad hoc entryを追加しない。
- Historical false positiveはHistorical contentではなくCurrent inventoryを修正する。
- Epic #384 overlapは本Issueから除外し、old/new dual modeを作らない。

## 15. Exit / handoff

次をすべて満たしたとき、Luna Max coderからmain orchestratorへ返す。

- I387-AC01〜AC15のevidenceがある。
- REDを確認したbehavior testがGREENになっている。
- provider/dogfood parityと`checkout_active_target()` no-diffが確認済み。
- focused、lint、ordinary、current verifier、package/fresh consumer、validateの実結果がある。
- Historical、current二skill、consumer CI、Epic #384 surfaceに意図しない差分がない。
- commit後に確定したfinal candidate SHAがPR/handoff evidenceにあり、pushed branch、merge-ready PR、residual riskが明確。Reportへの自己参照SHA追記はない。
- 未実施checkをpass扱いしていない。
- human merge gateを維持している。
