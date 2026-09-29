---
種別: 設計書（Issue）
ID: "iss-00411"
タイトル: "Remove retired SpecDock CLI surfaces after scope active work cutover"
関連GitHub: ["#411"]
状態: "draft"
最終更新: "2026-09-27"
依存: ["requirement.md"]
親: ["epic-00080", "init-00079"]
---

# iss-00411 Remove retired SpecDock CLI surfaces after scope active work cutover — 設計

詳細: [Design Guide](../../../../../../docs/authoring/design.md)

## 設計目標

1. public execution graph を current fixed-engine route へ一意化する。
2. retired runtime、old installer、old test launcher を、共有責務を壊さずに除去する。
3. CI を fixed full-SHA / distribution-digest / read-only validation へ統一する。
4. current docs、historical evidence、migration guidance、tombstone diagnostics の責務を分離する。
5. source deletion の判断を「名前」ではなく「current root からの到達性」と「移植済み regression」で機械的に行えるようにする。

Requirement の AC-411-01〜08 を設計の正本とし、本書では構造、境界、失敗契約、testability を定める。

## Current / Target

### Current: 二つの runtime と二つの installer 意味が同居

#### current public route

```text
pyproject.toml: spec-dock = spec_dock.cli:main
    -> src/spec_dock/cli.py::main
    -> src/spec_dock/external_cli.py::main
    -> fixed distribution / verified engine
    -> spec_dock_runtime.cli.options
    -> spec_dock_runtime.cli.vnext_runtime
    -> commands/*_vnext.py
    -> current application / domain / infra / presentation
```

repository-local shim も engine pin と distribution digest を検証して同じ fixed engine を `exec` する。

```text
spec-dock/scripts/spec-dock
    -> verified engine pin
    -> fixed-engine/bin/spec-dock
    -> 同じ current public route
```

#### retired runtime route

production の通常入口ではないが、test fixture が明示的に復活させている。

```text
tests/fixtures/legacy_spec_dock.script
    -> spec_dock_runtime.app.run
    -> cli.parser + cli.registry + cli.dispatch + cli.bootstrap
    -> commands/{new,import_cmd,active,delete,close,update,uninstall,
                 issue,worktree,workbench,sync,deps,validate,doctor,...}
    -> application.contracts::UseCases
```

`tests/cli_runtime/harness.py` は旧 directory installer で fixture workspace を作成した後、配布 shim を `legacy_spec_dock.script` へ差し替える。したがって old CLI test lane は production route を検証していない。

#### old installer と current shared asset root

```text
src/spec_dock/cli.py::legacy_installer_main
    -> src/spec_dock/installer.py::{install,uninstall}

src/spec_dock/external_cli.py
    -> src/spec_dock/installer.py::ASSETS  # current route も使用
```

このため `installer.py` は old behavior と current shared constant を同居させている。

#### CI caller の不整合

```text
.github/workflows/ci.yml
    -> python3 ./spec-dock/scripts/spec-dock sync
    -> python3 ./spec-dock/scripts/spec-dock validate
```

current shim / parser では `sync` と `validate` は retired root であり、意図した CI contract ではない。一方、次の fixed validator は存在する。

```text
.github/scripts/specdock-ci-validate.sh
    -> exact source HEAD comparison
    -> clean source check
    -> fixed bundle build in scratch
    -> distribution digest validation
    -> fixed-engine --project TARGET workspace validate --ci --json
```

`provider-ci.yml` も focused parity lane で `test_directory_installation.py` と old harness 依存の `test_cli_smoke.py` を呼び、削除対象 test を CI caller として固定している。

### Target: current roots と intentional exceptions だけを配布

```text
public package / shim / CI
    -> fixed engine
    -> options + catalog + vnext_runtime + admission + legacy tombstones
    -> current commands / shared use cases

retired executable implementation
    -> source から除去
    -> package data から除去
    -> fixed distribution から除去
    -> test fixture から除去

intentional retained evidence
    -> cli/legacy.py: current fail-closed tombstone
    -> docs/historical/**: historical evidence
    -> migration implementation/tests/docs: current migration contract
```

## 責務・Interface

### 1. Current root set

削除判定の root は次に固定する。

| Root ID | Root | 責務 |
|---|---|---|
| ROOT-PACKAGE | `pyproject.toml -> spec_dock.cli:main` | installed command の public entry |
| ROOT-FIXED | `spec_dock.fixed_bundle` が生成する `bin/spec-dock` | checkout 外 immutable distribution |
| ROOT-SHIM | `src/spec_dock/assets/spec_dock/scripts/spec-dock` | repository pin を検証し fixed engine へ委譲 |
| ROOT-CI | `.github/scripts/specdock-ci-validate.sh` | full-SHA 固定、digest 検証、read-only validation |
| ROOT-TEST-CURRENT | `*_vnext.py`、current integration / unit tests | current contract の回帰 |
| ROOT-TOMBSTONE | `spec_dock_runtime.cli.legacy` | retired root の fail-closed rejection |

`spec_dock_runtime.app`、old parser / registry / dispatch / bootstrap、legacy installer fixture は root に含めない。

### 2. Source classification model

`artifacts/20260927t131352z--cleanup-inventory.md` の各項目は次の一つに分類する。

| Class | 意味 | 実装規則 |
|---|---|---|
| `REMOVE-CONFIRMED` | current root から到達せず、役割が retired executable / test wire に限定される | regression 移植後に削除 |
| `UPDATE-CURRENT` | current caller / guidance だが旧 route を参照する | current contract へ更新 |
| `RETAIN-CURRENT` | current public route、safety、migration、shared invariant に必要 | 保持し回帰を強化 |
| `RETAIN-HISTORICAL` | 実行されず、明示的 historical evidence として必要 | historical label / location を維持 |
| `VERIFY-THEN-REMOVE` | old stack から主に使われるが current transitive caller の可能性がある | deletion gate を満たした場合のみ削除 |

分類は filename suffix、`legacy` token、`vnext` token、単純な `rg` 件数だけで決めない。

### 3. Deletion gate

`VERIFY-THEN-REMOVE` を `REMOVE-CONFIRMED` に昇格するため、次を全て満たす。

1. **Static import**: ROOT-PACKAGE / ROOT-FIXED / ROOT-SHIM / ROOT-CI / ROOT-TEST-CURRENT からの import graph に対象がない。
2. **Dynamic reference**: `importlib`、module-name string、resource path、subprocess path、shell script、package-data test に対象名がない。
3. **Shared symbol**: current caller が対象 module の定数・type・helper を使っていない。使う場合は neutral current module へ先に移す。
4. **Test migration**: 対象を直接・間接に起動する old test の current invariant が移植済みである。
5. **Distribution absence**: fixed bundle build 後、対象 path が distribution に存在しない。
6. **Runtime smoke**: current help、representative current command、tombstone rejection、CI validation が green である。

一つでも未達なら削除を中止し、inventory を `VERIFY-THEN-REMOVE` のまま残す。これは product 判断ではなく証拠不足として扱う。

### 4. Package entry / asset layout

#### Target interface

- `src/spec_dock/cli.py` は public `main(argv)` だけを保持し、`external_cli.main` へ委譲する。
- `legacy_installer_main` は削除する。
- `src/spec_dock/installer.py` の current caller が必要とする asset root は、新しい neutral module `src/spec_dock/asset_layout.py` へ移す。
- `asset_layout.py` は副作用を持たず、最低限 `ASSETS: Path` を提供する。
- reachability scan で current caller が他の installer constant を利用していることが判明した場合のみ、同じ module へその constant を移す。old install / uninstall behavior は移さない。
- `external_cli.py` と current distribution / parity tests は `asset_layout.ASSETS` を参照する。
- current import がゼロになった後に `installer.py` を削除する。

これにより「current package asset location」と「retired directory installer behavior」を別責務にする。

### 5. Runtime source boundary

#### 除去する shell

- `spec_dock_runtime/app.py`
- `spec_dock_runtime/cli/bootstrap.py`
- `spec_dock_runtime/cli/parser.py`
- `spec_dock_runtime/cli/registry.py`
- `spec_dock_runtime/cli/dispatch.py`
- old registry が列挙する non-vNext command modules と、old command registry contract

#### 保持する current shell

- `cli/options.py`
- `cli/catalog.py`
- `cli/vnext_runtime.py`
- `cli/admission.py`
- `cli/legacy.py`
- `commands/*_vnext.py` と current route が参照する result / helper module

#### application / infra / domain / presentation

この層は shared implementation を含むため、一括削除しない。特に current `vnext_runtime.py` は `application.active_selection`、`application.scope_query`、`application.installation_update_vnext` などを直接参照し、current command modules からも old-named shared use case へ到達し得る。

- `application/contracts.py`、`application/issue_lifecycle.py` など old shell 色が強い module は `VERIFY-THEN-REMOVE` とする。
- current command から到達する `check_deps.py`、`close_node.py`、`create_*`、`delete_node.py`、`sync_state.py`、`validate_tree.py` 等は、名称にかかわらず `RETAIN-CURRENT` とする。
- orphan cleanup は本 Issue に含めるが、無関係な rename / layering redesign は行わない。

### 6. Tombstone interface

`cli/legacy.py` は compatibility implementation ではなく current safety boundary である。

- representative retired root は `LEGACY_COMMAND_REMOVED` と replacement を返す。
- tombstone は old command を実行しない。
- `init` のように既存 tombstone mapping がない old installer root は、current parser の usage failure でもよい。ただし target write が起きないことを test する。
- message を変更する場合は current help / docs と同一 replacement を使う。

### 7. CI interface

#### `.github/workflows/ci.yml`

Target invocation は次の contract とする。

```yaml
- uses: actions/checkout@v4
- name: Validate dogfood workspace with fixed SpecDock source
  env:
    EXPECTED_SOURCE_SHA: ${{ github.sha }}
  run: |
    test "$(git rev-parse --verify 'HEAD^{commit}')" = "$EXPECTED_SOURCE_SHA"
    bash .github/scripts/specdock-ci-validate.sh \
      "$GITHUB_WORKSPACE" \
      "$GITHUB_WORKSPACE" \
      "$EXPECTED_SOURCE_SHA"
```

- branch 名や短縮 SHA を expected source identity にしない。
- PR event の merge checkout を使う場合は `${{ github.sha }}` と `HEAD` の一致を採用する。
- workflow 内で `workspace sync` を実行しない。
- hard-code された authoring baseline SHA `d7c...` を workflow に埋め込まない。各 run の checked-out full SHA が固定値である。

#### `.github/workflows/provider-ci.yml`

- full suite job は維持する。
- matrix parity job の focused test を current tests に差し替える。
- focused set は次を含む。
  - provider asset / dogfood parity test
  - fixed public entrypoint / distribution isolation test
  - current installation init regression
  - retired surface absence test
- `test_directory_installation.py` と old harness `test_cli_smoke.py` は参照しない。

#### `.github/scripts/specdock-ci-validate.sh`

既存 contract を保持する。変更は workflow wiring や error clarity に必要な最小限とし、次を弱めない。

- complete SHA only
- exact `HEAD^{commit}` comparison
- clean source checkout
- scratch build
- SHA-256 distribution digest format
- `workspace validate --ci --json`
- target write なし

### 8. Test architecture

#### current test strata

| Stratum | 守るもの |
|---|---|
| parser / contract | 44 leaf、help、JSON envelope、recovery option、tombstone |
| fixed entrypoint | checkout fallback 拒否、engine pin / digest、distribution isolation |
| current CLI runtime | Scope / Active / Work / Dependency / Artifact / Worktree / Workspace behavior |
| installation integration | init / update / uninstall、journal、resume / rollback、group behavior |
| CI integration | exact SHA、dirty / mismatch failure、read-only target |
| provider distribution | provider asset、dogfood projection、shipped path、retired path absence |
| migration integration | schema 3 plan / execute / journal / recovery |

#### old test migration rule

各 old test assertion を次の順で分類する。

1. **retired syntax only**: 削除する。
2. **current public behavior**: current `*_vnext` / integration test へ移す。
3. **shared invariant**: application / domain / infra unit test へ移す。
4. **historical inventory only**: executable test から削除し、Git history / historical docs に委ねる。
5. **migration / safety**: current migration / tombstone test として保持する。

`tests/unit/infra/test_init_update.py` は old harness test と current provider/docs parity assertion を同居させるため分割する。current assertion は `tests/unit/infra/test_provider_distribution.py` に移し、legacy init / update wire に依存する部分を削除または installation integration へ移す。

`tests/unit/infra/test_directory_installation.py` の nontransactional old update contract は current journaled installation contract ではないため移植しない。tool data preservation、source symlink rejection 等の current invariant が現行 installation tests に不足する場合のみ current test へ移す。

`tests/cli_runtime/test_cli_vnext_contract.py` は current 44 leaf / help / JSON / recovery / tombstone test を保持し、old parser / registry import と 28-leaf manifest assertion を削除する。

### 9. Docs boundary

#### provider-first

1. `src/spec_dock/assets/spec_dock/scripts/README.md` を current guide に更新する。
2. current docs / templates / skills の stale guidance を更新する。
3. current repository の dogfood projection を provider から更新する。
4. byte parity test で確認する。

#### current root docs

- `docs/github-issue-integration.md`: `scope create/import`、GitHub/local backend authority、fixed engine、safe failure に全面更新する。
- `docs/sync-aggregation.md`: `workspace sync` と generation pointer / cache authority / read-only validation の現行設計へ更新する。
- `AGENTS.md`: runtime architecture map から retired parser / registry / dispatch / legacy installer fixture を除き、current CLI shell を記載する。
- root `README.md` と installed skills は current であることを検証し、stale token がある場合のみ更新する。

#### historical / migration

- provider `docs/historical/**` と dogfood mirrorを保持する。
- `docs/scope-lifecycle-start-finish-analysis.md` は historical decision input の banner と current reference link を保持・強化する。
- migration docs は old-to-current 手順を含み得るため current stale scan の一律対象外とし、historical / migration allowlist に理由を記録する。

## data / failure

### Data impact

本 Issue は source / tooling asset / docs / tests / workflows の cleanup であり、以下を変更しない。

- `spec-dock/initiatives/**` の user specification data
- active selection
- branch / worktree registry
- GitHub Issue state
- schema 3 data
- installation control / journal の live instance

current dogfood の managed docs / scripts は provider parity のため更新対象だが、user-authored spec data ではない。

### Failure contract

| Failure | Expected behavior | Recovery |
|---|---|---|
| shared caller が残る | deletion test が fail、対象 file を保持 | shared symbol を neutral module へ移し再実行 |
| old test に current invariant が残る | migration ledger が incomplete で gate fail | current test を先に追加し green を確認 |
| fixed source SHA mismatch | CI validator exit 3 | checkout / expected SHA wiring を修正し再実行 |
| dirty source | CI validator fail before build | clean commit checkout で実行 |
| distribution digest invalid | build/validator fail | fixed bundle sourceを復旧、digest contractを調査 |
| current docs に retired invocation | docs regression fail | provider sourceを更新し dogfood再同期 |
| dogfood parity mismatch | parity test fail | providerを正本として projectionを再生成 |
| current command regression | focused / full test fail | retired deletion commitを revertまたはforward fix |

## 変更対象

### 必須変更

- `src/spec_dock/cli.py`
- `src/spec_dock/installer.py` と新規 `src/spec_dock/asset_layout.py`
- retired runtime shell / old command modules
- `.github/workflows/ci.yml`
- `.github/workflows/provider-ci.yml`
- current CI / entrypoint / distribution tests
- old harness、legacy launcher fixture、legacy manifest、old wire tests
- `pyproject.toml` の stale mypy overrides
- provider / dogfood scripts README
- current root docs と `AGENTS.md`
- provider/dogfood parity test

### 原則変更しない

- `external_cli.py`、`fixed_bundle.py`、`runtime_loader.py` の security boundary（import source の付替え以外）
- current 44 leaf contract
- `cli/legacy.py` の fail-closed 目的
- current installation / migration journal protocol
- provider `docs/historical/**`
- schema 3 migration code / tests / fixture helpers
- consumer specification data
- `.github/workflows/commit-identity.yml`

## 移行・互換性・rollback

### Compatibility

retired public CLI の executable compatibility は提供しない。残すのは error / replacement guidance だけである。current 44 leaf と JSON envelope / exit code / recovery contract は維持する。

### Migration

Data migration は `N/A`。理由は、本 Issue が executable / docs / tests / CI の cleanup であり、schema 3 data format を変更しないためである。既存 migration implementation と tests は regression として実行する。

### Rollback

変更は段階別に revert 可能にする。

1. test safety net / parity test 追加
2. asset constant 分離
3. old test fixture 切離
4. retired source 除去
5. CI caller 切替
6. docs / dogfood 更新
7. config cleanup

current regression が見つかった場合は、最後の green stage まで source commit を revert する。old runtime を一時復活させて production fallback にする rollback は認めない。必要な回復は current route の forward fix または source commit revert で行う。

## testability

### Positive observations

- `spec-dock --help --json` が fixed package entry から成功する。
- 44 leaf が catalog と docs に一致する。
- fixed validator success output に full source SHA と 64-hex distribution digest が含まれる。
- `workspace validate --ci --json` の `effects` が空で target bytes が変わらない。
- provider / dogfood managed trees が一致する。

### Negative observations

- source SHA mismatch、dirty source、invalid expected SHA を拒否する。
- checkout 内 engine、symlinked engine、tampered distribution を拒否する。
- `issue start` 等を old runtime で成功させず、current tombstone で拒否する。
- `init` old root が target directoryを書き換えない。
- fixed distribution 内に retired files がない。
- current docs allowlist 外に retired invocation がない。

### Distribution absence test

新規 `tests/integration/test_retired_cli_surface_cleanup.py` を設け、少なくとも次を検証する。

- source tree の mandatory-removed paths が存在しない。
- fixed bundle の `lib/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/` に同 paths が存在しない。
- `spec_dock.cli` に `legacy_installer_main` がない。
- current roots が retired module names を import / reference しない。
- historical allowlist と `cli/legacy.py` を誤検出しない。

## risk

| Risk | Impact | Mitigation |
|---|---|---|
| shared use case を old-only と誤認 | current command failure | deletion gate、current import graph、focused test |
| old tests を一括削除し invariant 消失 | latent regression | assertion-level migration ledger、移植先 green before delete |
| CI が event SHA と異なる checkout を検証 | source identity false assurance | `HEAD^{commit}` と expected SHA の明示比較 |
| provider / dogfood divergence | shipped behavior と self-hosted behavior の不一致 | provider-first、byte parity test |
| historical text の過剰削除 | migration / decision evidence 消失 | historical allowlist、current/historical boundary test |
| old runtime が package data に残る | accidental reactivation | fixed distribution absence test |
| cleanup が consumer rollout に波及 | 稼働中 worktree interruption | local provider + dogfood only、rollout out-of-scope |

## 要件トレーサビリティ

| Requirement | Design mechanism | Acceptance |
|---|---|---|
| RQ-411-01 | current root set、package entry simplification | AC-411-01 |
| RQ-411-02 | classification model、deletion gate、distribution absence test | AC-411-02 |
| RQ-411-03 | `cli/legacy.py` tombstone boundary | AC-411-03 |
| RQ-411-04 | CI full-SHA interface、provider-ci focused set | AC-411-04 |
| RQ-411-05 | provider-first docs boundary、historical allowlist | AC-411-05 |
| RQ-411-06 | test strata、assertion migration rule | AC-411-06 / 07 |
| RQ-411-07 | provider authority、bounded dogfood update | AC-411-08 |
| RQ-411-08 | data impact N/A、migration retention | AC-411-07 / 08 |
