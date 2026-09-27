---
種別: 実装計画書（Issue）
ID: "iss-00411"
タイトル: "Remove retired SpecDock CLI surfaces after scope active work cutover"
関連GitHub: ["#411"]
状態: "draft"
最終更新: "2026-09-27"
依存: ["requirement.md", "design.md"]
親: ["epic-00080", "init-00079"]
---

# iss-00411 Remove retired SpecDock CLI surfaces after scope active work cutover — 実装計画

詳細: [Issue Plan Guide](../../../../../../docs/authoring/issue-plan.md)

## Planning Level

**selected level: `strict`**

### 理由

- public CLI、fixed distribution、CI、installation、migration safety に接する。
- source file を削除して package data からも消すため、誤削除時の blast radius が単一 function 修正より大きい。
- old tests を多数削除するため、回帰を移植せずに進めると false-green になり得る。
- CI の source identity と read-only contract を誤ると、検証済みでない bytes を実行または workspace を変更する可能性がある。

### risk factors

- old CLI shell が shared application / infra を import しており、import 元だけを見て transitive module を削除すると current route を壊す。
- `installer.py` に retired behavior と current `ASSETS` が同居する。
- old harness が tests 全体の fixture と parity assertions に浸透している。
- historical / migration text と stale current guidance の文字列が似ている。

### 再評価条件

次のいずれかが判明したら同じ `plan.md` で `critical` への再評価を行う。

- cleanup に user specification data、active state、Git refs、GitHub state の migration / deletion が必要になる。
- current installation control または journal format の変更が必要になる。
- recovery が通常の source revert / forward fix ではなく incident response を必要とする。

現時点では data migration は `N/A`。schema 3 migration implementation と tests は保持し、cleanup の変更対象にしない。

## 目標

- package / shim / CI / tests を current fixed-engine route に統一する。
- retired CLI runtime と old directory installer を fixed distribution から除去する。
- old tests を assertion 単位で分類し、current invariant を適切な current test layer へ移植する。
- current docs と historical evidence を明確に分離する。
- provider を正本として、この repository の dogfood projection のみを同期する。
- AC-411-01〜08 をコマンド出力と inventory ledger で検証可能にする。

## 順序・依存

```text
Step 0  provenance / clean baseline
  -> Step 1  current safety net + deletion gate
  -> Step 2  neutral asset layout split
  -> Step 3  old test assertion migration + harness removal
  -> Step 4  retired runtime / installer source removal
  -> Step 5  CI caller cutover
  -> Step 6  current docs + provider/dogfood projection
  -> Step 7  config / links / inventory finalization
  -> Step 8  focused + full + clean-checkout verification
  -> Step 9  exit / handoff
```

### 並行可能性

- Step 1 の docs stale-scan test と runtime absence test は並行して作成できる。
- Step 3 の test assertion migration は command family ごとに並行できるが、old harness / conftest の削除は全 family の移植後に一回だけ行う。
- Step 6 の文書本文は runtime / CI target が確定した後なら並行できる。

### 並行禁止

- `installer.py` 削除と asset constant 移設を分けて実行しない。
- old test file 削除を current assertion 移植より先に行わない。
- provider docs を直さず dogfood mirror だけを手編集しない。
- CI workflow を旧 test 名のまま残して test file を削除しない。

## 実装step

## Step 0 — verified baseline と変更境界を固定する

### 目的

実装対象がこの仕様パックの調査基準と一致し、他 branch / default branch / unrelated dirty work を混ぜないことを確認する。

### 実行

```bash
set -euo pipefail
EXPECTED_BRANCH='iss-00411-retired-cli-surface-cleanup'
BASE_SHA='d7c816d11bee1a73cb87273b15e486c3b669206c'

test "$(git rev-parse --show-toplevel)" = "$PWD"
test "$(git branch --show-current)" = "$EXPECTED_BRANCH"
git merge-base --is-ancestor "$BASE_SHA" HEAD
test -z "$(git status --porcelain)"
git diff --name-status "$BASE_SHA" HEAD
```

### 判定

- branch が一致し、調査時の full SHA が現在の HEAD の祖先である。
- worktree が clean であり、基準 SHA から現在の HEAD までの差分が Issue #411 の仕様書・Artifact・レビュー修正だけである。source、CI、test に差分があれば Step 1 の前に inventory と設計を実装現物へ更新する。
- scaffold の Issue #411 R/D/P frontmatter が本 pack と一致する。

### drift / failure recovery

- 基準 SHA が祖先でない場合、または source / CI / test が先に変わった場合は、差分を current root / inventory に再反映するまで deletion を開始しない。default branch や別 branch へ切り替えて代用しない。
- unrelated dirty work がある場合は上書きしない。明示的に別 clean worktree を用意するか、作業を中止して path を報告する。
- この Step は schema migration や installation update を実行しない。

### 完了判定

`artifacts/20260927t131352z--cleanup-inventory.md` の provenance と実 checkout の関係を確認し、baseline test commands を記録した。

## Step 1 — current safety net と deletion gate を先に作る

### 目的

source / test 削除前に、current route と「retired path が distribution に残らない」ことを自動判定できるようにする。

### 1.1 新規 retired-surface integration test

`tests/integration/test_retired_cli_surface_cleanup.py` を追加し、次を実装する。

1. mandatory removal manifest の source paths が存在しないこと。
2. `spec_dock.cli` が `legacy_installer_main` を公開しないこと。
3. fixed bundle を temp directory に構築し、distribution 内に mandatory retired paths がないこと。
4. current root files に retired module import / exact module-name string がないこと。
5. `cli/legacy.py`、historical docs、migration docs、Issue specs は intentional allowlist であること。
6. representative retired roots が current entrypoint で fail closed すること。

実装前は absence assertion が赤になる。expected failure を確認したら、`xfail` や skip を残さず後続 Step で green にする。

### 1.2 provider distribution test の抽出

`tests/unit/infra/test_provider_distribution.py` を新設し、`test_init_update.py` から current な assertions を移す。

- provider scripts/docs/skills と checked-in dogfood projection の byte parity
- provider shipped shim と `src/spec_dock/shim_vnext.py` の byte equality
- managed skill catalog の exact match
- current docs / operator guidance の required current terms
- legacy fixture を dogfood mismatch の許容値にしない

### 1.3 docs stale-current test の拡張

`tests/integration/test_cli_docs_vnext.py` を更新する。

- current guidance set に provider `scripts/README.md`、root current docs、`AGENTS.md`、current dogfood copies、workflows を含める。
- historical / migration / tombstone / spec archive を理由付き allowlist にする。
- generic wordsではなく executable retired invocation pattern を検査する。

### 1.4 baseline focused tests

```bash
uv run pytest \
  tests/cli_runtime/test_cli_vnext_contract.py \
  tests/integration/test_cli_entrypoint_vnext.py \
  tests/integration/test_ci_fixed_validation.py \
  tests/integration/test_cli_docs_vnext.py \
  tests/integration/test_workspace_migration_vnext.py \
  tests/integration/test_workspace_migration_journal_vnext.py
```

新しい absence test だけが expected red、既存 current tests は green であることを確認する。

### 完了判定

- current public route、tombstone、CI validator、migration、docs を守る test が source deletion 前に存在する。
- inventory の test migration table に全 old test family と移植先が記載される。

### failure recovery

- current baseline test が既に失敗する場合は cleanup を進めず、baseline failure と Issue #411 差分を分離する。
- stale scan が historical content を誤検出する場合は broad skip を入れず、最小 path / pattern allowlist と理由を追加する。

## Step 2 — current asset layout を old installer から分離する

### 目的

current external engine が old installer module に依存する構造を先に解消し、後続で old installer を安全に削除できるようにする。

### 2.1 neutral module を追加

`src/spec_dock/asset_layout.py` を追加する。

- `ASSETS = Path(__file__).resolve().parent / "assets"` 相当の side-effect-free contract を置く。
- current reachability scan で必要と確認された layout constant だけを同じ module へ移す。
- install / update / uninstall、filesystem write、argument parse は置かない。

### 2.2 current caller を更新

- `src/spec_dock/external_cli.py` の `installer.ASSETS` import を `asset_layout.ASSETS` へ変更する。
- current tests / helpers が asset root のためだけに `installer.py` を import している場合は `asset_layout.py` へ変更する。
- fixed bundle、runtime loader、shim security boundary は無関係に変更しない。

### 2.3 current import scan

```bash
rg -n --hidden \
  'from spec_dock\.installer import|import spec_dock\.installer|spec_dock\.installer\.' \
  src tests .github pyproject.toml || true
```

結果を次に分類する。

- old installer tests / `legacy_installer_main`: Step 3 で削除。
- current asset-root caller: `asset_layout` へ移設。
- old behavior caller: old test migration ledger へ追加。

### 検証

```bash
uv run pytest \
  tests/integration/test_cli_entrypoint_vnext.py \
  tests/unit/infra/test_provider_distribution.py
```

### 完了判定

- current production source に `spec_dock.installer` import がない。
- old installer module は old tests / `legacy_installer_main` だけから到達する。
- fixed engine help と provider parity が green。

### failure recovery

current caller が additional installer constant を必要とする場合は、その constant の意味と caller を inventory に記録し、neutral module へ移す。old installer behavior を current module へコピーしない。

## Step 3 — old test assertions を移植し、legacy harness を除去する

### 目的

旧 test 数を減らすことではなく、current contract に必要な assertions を current test layer へ移し、旧 launcher を test setup から排除する。

### 3.1 assertion-level classification

`artifacts/20260927t131352z--cleanup-inventory.md` の mapping に従い、各 old test function を次の一つに記録する。

- `delete-retired-syntax`
- `port-current-cli`
- `port-shared-unit`
- `retain-migration-safety`
- `delete-historical-inventory`

各 port entry には移植先 test path と test function 名を記録する。file 単位の「全部 old」判断は禁止する。

### 3.2 command family ごとの移植

順序は次に固定する。

1. Active / Scope create/import / Artifact
2. Scope close/delete / Work start/finish / Dependency
3. Workspace sync/validate/doctor
4. Worktree / Workbench
5. Installation update/uninstall
6. shared application/domain/infra/presentation tests

各 family で次を繰り返す。

```text
old assertion を読む
-> current behavior なら current *_vnext / integration test へ追加
-> shared invariant なら unit test へ追加
-> 移植先だけを実行して green
-> old test function を削除
-> family focused tests を再実行
```

### 3.3 special files

#### `tests/cli_runtime/test_cli_vnext_contract.py`

- old `parser.py` / `registry.py` import を削除する。
- `test_legacy_28_leaf_inventory_is_frozen_before_cutover` を削除する。
- 44 leaf、help、JSON envelope、recovery、tombstone tests を保持する。

#### `tests/unit/infra/test_init_update.py`

- current provider/docs/skills parity assertionsを `test_provider_distribution.py` へ移す。
- legacy fixture を parity の許容値にする branch を削除する。
- old init/update wire assertions は current installation integration へ移植するか、old-only なら削除する。
- file に current-only assertions が残らなければ file を削除する。

#### `tests/unit/infra/test_directory_installation.py`

- old nontransactional replacement semantics は削除する。
- still-current data preservation、symlink / hard-link safety、managed-directory boundary が current installation tests に不足する場合のみ、current `installation_*_vnext` integration test へ移す。
- 移植後 file を削除する。

#### `tests/unit/cli/test_cli.py`

- old test module inventory / grouping assertion を削除する。
- generic pytest discovery invariant が独立価値を持つ場合のみ neutral test に移す。

#### `tests/unit/cli/test_cli_smoke.py`

- old `active set --id` smoke を削除する。
- current fixed-engine active smoke が current test に存在することを確認する。

#### `tests/cli_runtime/test_distribution_cutover.py`

- `tests.cli_runtime.harness.main` を直接 import しているため、conftest の一覧とは別に全 test function を Step 3.1 の台帳へ記録する。
- provider/install-root catalog、provider/dogfood skill parity、実行可能ファイル境界は current provider distribution test へ移植する。
- unmanaged content、consumer workflow、foreign fixed root の保持は current installation init/update contract と照合し、有効な invariant を current installation integration test へ移植する。
- old `init` の置換動作だけを固定する assertion は current contract と一致しない限り移植しない。移植先が green になるまで、この file と共有 harness を削除しない。

#### その他の direct harness caller

- `test_generation_checkout.py`、`test_runtime_handoff.py`、`test_worktree_lifecycle_coordination.py` は `CliRuntimeHarness` を継承する。各 assertion を current safety invariant と旧 CLI wire に分け、current 側を現行 fixture/test に移す。
- `test_scope_github_vnext.py` と `test_scope_local_vnext.py` は名前が current でも `harness.main(["init", ...])` を setup に使う。現行 installation setup へ替え、scope の current assertion を保持する。
- `tests/unit/infra/test_fake_gh_harness.py` の fake-gh helper と GitHub status invariant は neutral test support と current unit test に移し、旧 harness 継承をなくす。
- inventory §8.3 の全 direct caller と conftest 経由の利用を照合し、`rg -n 'tests\.cli_runtime\.harness|from \.harness|import harness' tests` で取りこぼしを確認してから共有 harness を削除する。

### 3.4 legacy setup を削除

移植先が全て green になった後に、同一 coherent change で次を削除する。

```text
tests/cli_runtime/harness.py
tests/cli_runtime/conftest.py の old template/harness logic
tests/fixtures/legacy_spec_dock.script
tests/fixtures/cli_redesign/legacy_manifest.json
```

`tests/cli_runtime/conftest.py` に current fixtures が必要なら current-only fixture だけを残し、`legacy_installer_main`、old shim replacement、old command syntax を参照しない。

### 3.5 old installer entry を削除

old test caller がゼロになった時点で次を行う。

- `src/spec_dock/cli.py` から `legacy_installer_main`、old argparse/json/path/shutil/version helper、`installer` imports を削除する。
- `src/spec_dock/installer.py` の current import がゼロであることを再確認し、module を削除する。

### focused verification

実際の current test namesを inventory に反映した上で、少なくとも次を実行する。

```bash
uv run pytest \
  tests/cli_runtime/test_cli_vnext_contract.py \
  tests/cli_runtime/test_active_vnext.py \
  tests/cli_runtime/test_artifact_commands_vnext.py \
  tests/cli_runtime/test_artifact_vnext.py \
  tests/integration/test_cli_entrypoint_vnext.py \
  tests/integration/test_cli_recovery_vnext.py \
  tests/integration/test_installation_group_init_vnext.py \
  tests/integration/test_installation_group_update_vnext.py \
  tests/integration/test_installation_journal_vnext.py \
  tests/unit/infra/test_provider_distribution.py
```

### 完了判定

- test collection に old harness import error がない。
- `rg -n 'legacy_installer_main|legacy_spec_dock\.script|legacy_manifest\.json|tests\.cli_runtime\.harness' tests src pyproject.toml` は intentional spec/history 以外ゼロ。
- assertion migration ledger が全 old test family で完了している。
- current installation / migration / safety tests が green。

### failure recovery

- 移植先 test が current implementation の bug を示した場合は source deletion より前に current behavior を修正し、Requirement / Design を変える必要があれば仕様へ戻す。
- unique invariant の移植先が決まらない場合は old test file を残すのではなく、その assertion が public behavior / shared invariant / history のどれかを inventory rule で分類する。証拠不足なら削除しない。

## Step 4 — retired runtime source と proven orphan を削除する

### 目的

production package data と fixed distribution から old executable stack を除去する。

### 4.1 confirmed shell を削除

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/dispatch.py
```

### 4.2 old registry command modules を削除

inventory §5.2 の non-vNext command modules を削除する。削除直前に exact import/reference scan を実行する。

```bash
rg -n --hidden \
  'spec_dock_runtime\.commands\.(active|artifact_import|close|delete|deps|doctor|import_cmd|issue|new|sync|uninstall|update|validate|workbench|worktree)\b' \
  src tests .github || true
```

current source / test caller がある module は、caller の目的を確認し、shared helper を neutral current module へ移した後に削除する。

### 4.3 conditional old-stack modules

次を一件ずつ gate する。

- `commands/contracts.py`
- `application/contracts.py`
- `application/issue_lifecycle.py`
- old installer-delegation application module
- old shell 専用 adapter / renderer

確認コマンド例:

```bash
rg -n --hidden \
  'commands\.contracts|application\.contracts|application\.issue_lifecycle' \
  src tests .github pyproject.toml || true
```

判定:

- current root / current test caller あり: retain または shared part を移設。
- old test / deleted shell callerだけ: delete。
- dynamic/resource reference 未確認: inventory を pending のままにして削除しない。

### 4.4 package/distribution absence

```bash
uv run pytest tests/integration/test_retired_cli_surface_cleanup.py
```

追加の手動確認:

```bash
TMP_ENGINE="$(mktemp -d)/engine"
uv run python -m spec_dock.fixed_bundle "$TMP_ENGINE"
test ! -e "$TMP_ENGINE/lib/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py"
test ! -e "$TMP_ENGINE/lib/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py"
"$TMP_ENGINE/bin/spec-dock" --help --json
```

### 完了判定

- confirmed retired source が source tree / package data / fixed distribution にない。
- current 44 leaf、tombstone、installation、migration tests が green。
- conditional modules は削除証拠または retain 理由が inventory に記録される。

### failure recovery

- current import failure が出た場合、削除した shared module をそのまま old shell として復活させない。必要 symbol を current ownership へ forward-port し current tests を追加する。
- 広範な architecture redesign が必要になった場合は本 Issue の範囲を超えるため、module を retain し residual item として記録する。

## Step 5 — CI caller を fixed read-only route へ切り替える

### 目的

workflow が current CLI と同じ fixed source bytes を検証し、old root や write operation を呼ばないようにする。

### 5.1 `.github/workflows/ci.yml`

次の構造へ変更する。

```yaml
name: CI

on:
  push:
  pull_request:

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
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

- `sync` stepを削除する。
- repository-local `validate` stepを削除する。
- branch checkoutの追加 fetch / default branch fallback を入れない。
- fixed authoring SHAを literalにしない。

### 5.2 workflow wiring test

`tests/integration/test_ci_fixed_validation.py` に次を追加する。

- `ci.yml` が `specdock-ci-validate.sh` を一回呼ぶ。
- expected SHA source が `${{ github.sha }}` である。
- `git rev-parse HEAD` comparison がある。
- `spec-dock/scripts/spec-dock sync`、`... validate`、`workspace sync` がない。
- validator script の success / mismatch tests は保持する。read-only test は target root 全体の相対 path、file bytes、file mode、symlink target、directory set を実行前後で比較する。active、generated、installation control、`.git/spec-dock` も対象に含め、対象外の scratch engine は含めない。

### 5.3 `.github/workflows/provider-ci.yml`

matrix focused step を次の current test setへ変更する（実際の file 名は Step 1/3 で確定したものと一致させる）。

```bash
uv run pytest \
  tests/unit/infra/test_provider_distribution.py \
  tests/integration/test_cli_entrypoint_vnext.py \
  tests/integration/test_installation_group_init_vnext.py \
  tests/integration/test_retired_cli_surface_cleanup.py
```

full provider suite (`make lint`, `uv run pytest`) は維持する。

### 検証

```bash
uv run pytest \
  tests/integration/test_ci_fixed_validation.py \
  tests/integration/test_cli_entrypoint_vnext.py \
  tests/integration/test_retired_cli_surface_cleanup.py \
  tests/unit/infra/test_provider_distribution.py
```

### 完了判定

- workflow に old root invocation がない。
- exact SHA mismatch negative test が green。
- target workspace bytes / control state が変わらない。
- provider-ci が削除済み test path を参照しない。

### failure recovery

- `github.sha` と checkout HEAD が一致しない event では validation を別 ref へ fallback させず fail する。必要なら checkout configuration と event semantics を明示的に修正する。
- validator script の full-SHA / clean-source / digest checks を弱めない。

## Step 6 — current docs を provider-first で更新し dogfood を同期する

### 目的

実行可能な current guidance から retired command を除き、historical / migration evidence は意図的に残す。

### 6.1 provider scripts README

`src/spec_dock/assets/spec_dock/scripts/README.md` を全面更新する。

必須内容:

- daily entry は fixed external `spec-dock` または verified repository shim。
- current examples: `scope create/import`、`active`、`work start/finish`、`dependency`、`artifact`、`workspace sync/validate`、`installation`。
- shim は local implementation ではなく fixed engine delegator。
- CI は fixed full-SHA validator と `workspace validate --ci --json`。
- installation update / schema migration / recovery を別操作として説明。
- `uvx spec-dock init/update`、old `new`、`issue start`、top-level `sync/validate` を現行手順として記載しない。

### 6.2 root current docs

- `docs/github-issue-integration.md` を current Scope create/import、GitHub/local authority、explicit target、failure boundary へ書き換える。
- `docs/sync-aggregation.md` を `workspace sync` の current generation/cache contract と CI validation distinction へ書き換える。
- `AGENTS.md` の runtime architecture map を `options/catalog/vnext_runtime/admission/legacy tombstone` に更新する。
- root `README.md`、provider `docs/reference_cli.md`、installed skills は stale scanで必要な箇所だけ更新する。

### 6.3 historical boundary

- `docs/scope-lifecycle-start-finish-analysis.md` の冒頭に historical decision input と current reference link が明示されていることを確認する。不足時のみ追加する。
- provider / dogfood `docs/historical/**` は保持する。
- `migration.md` は old-to-current evidence を含むため一律置換しない。

### 6.4 dogfood projection

provider変更後、この repository の managed projectionだけを更新する。

- `src/spec_dock/assets/spec_dock/scripts/**` -> `spec-dock/scripts/**`
- `src/spec_dock/assets/spec_dock/docs/**` -> `spec-dock/docs/**`
- provider skills -> root `.agents/skills/**`

他 worktree / consumerを更新しない。

更新方法は current installation/projection contractに従う。手動 copy を使う場合も providerを正本とし、最終 byte parity testで検証する。

### docs verification

```bash
uv run pytest \
  tests/integration/test_cli_docs_vnext.py \
  tests/unit/infra/test_provider_distribution.py
```

補助 scan:

```bash
rg -n --hidden \
  '(\./spec-dock/scripts/spec-dock|python3 ./spec-dock/scripts/spec-dock)[[:space:]]+(new|issue|deps|sync|validate|update|uninstall|delete|close)|uvx spec-dock (init|update)' \
  README.md AGENTS.md docs src/spec_dock/assets/spec_dock src/spec_dock/assets/install_root spec-dock .agents .github/workflows \
  || true
```

scan結果は historical / migration / tombstone / spec archive allowlistと照合し、current guidance matchをゼロにする。

### 完了判定

- current guidanceの executable examplesが現行 leafのみ。
- provider / dogfood managed assetsが byte-equal。
- historical evidenceとmigration guidanceが残る。

### failure recovery

- parity failure時は dogfood側を正本にしてproviderを戻さない。provider変更を確定し、projectionを再作成する。
- historical docの旧語だけを理由に内容を削除しない。current-looking表現が問題ならhistorical banner/linkを強化する。

## Step 7 — configuration、links、inventory を cleanup 後の実体に合わせる

### 目的

削除済み module / test への metadata caller を残さない。

### 7.1 `pyproject.toml`

- deleted test modulesに対する mypy overrideを削除する。
- current testで実際に必要な overrideだけを残す。
- package-data設定は retained current assetsを引き続き含み、retired filesが物理的にないことを distribution testで確認する。

### 7.2 links / imports / workflow path scan

```bash
rg -n --hidden \
  'legacy_installer_main|legacy_spec_dock\.script|legacy_manifest\.json|spec_dock_runtime\.(app|cli\.(bootstrap|parser|registry|dispatch))' \
  . \
  -g '!spec-dock/initiatives/**' \
  -g '!src/spec_dock/assets/spec_dock/docs/historical/**' \
  || true
```

許容される match はIssue #411 specs / inventory の説明だけ。production source、tests、workflows、current docsにmatchを残さない。

### 7.3 inventory finalization

`artifacts/20260927t131352z--cleanup-inventory.md` に次を記録する。

- conditional application modulesのretain/delete結果
- old test function -> current test function mapping
- current-guidance scanのallowlistと理由
- focused/full test結果
- out-of-scope pathsに差分がないこと

### 完了判定

- deleted pathへの import/config/workflow/linkがない。
- inventoryにpending deletion evidenceがない。retainしたconditional itemには理由がある。

## Step 8 — verification

## 8.1 focused contract suite

```bash
uv run pytest \
  tests/cli_runtime/test_cli_vnext_contract.py \
  tests/integration/test_retired_cli_surface_cleanup.py \
  tests/integration/test_cli_entrypoint_vnext.py \
  tests/integration/test_cli_docs_vnext.py \
  tests/integration/test_ci_fixed_validation.py \
  tests/integration/test_cli_recovery_vnext.py \
  tests/integration/test_cli_writer_compatibility_vnext.py \
  tests/integration/test_installation_finalize_vnext.py \
  tests/integration/test_installation_group_init_vnext.py \
  tests/integration/test_installation_group_journal_vnext.py \
  tests/integration/test_installation_group_update_vnext.py \
  tests/integration/test_installation_journal_vnext.py \
  tests/integration/test_workspace_migration_vnext.py \
  tests/integration/test_workspace_migration_journal_vnext.py \
  tests/unit/infra/test_provider_distribution.py
```

## 8.2 full static / test suite

```bash
make lint
uv run pytest
git diff --check
```

policy skip、regression ledgerによる除外、old-test allowlistによるcollection回避を追加しない。

## 8.3 fixed bundle smoke

```bash
set -euo pipefail
TMP_ROOT="$(mktemp -d /private/tmp/specdock-bundle-XXXXXX)"
trap 'rm -rf -- "$TMP_ROOT"' EXIT
ENGINE="$TMP_ROOT/engine"
uv run python -m spec_dock.fixed_bundle "$ENGINE"
"$ENGINE/bin/spec-dock" --help --json
"$ENGINE/bin/spec-dock" help workspace validate
"$ENGINE/bin/spec-dock" --project "$PWD" workspace validate --ci --json

test ! -e "$ENGINE/lib/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py"
test ! -e "$ENGINE/lib/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py"
test ! -e "$ENGINE/lib/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py"
test ! -e "$ENGINE/lib/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/dispatch.py"
```

## 8.4 representative negative commands

実際の entrypoint helperに合わせて JSON/textを検証する。

```bash
# いずれも test-built fixed engine を使い、old behavior を成功させない。
set -euo pipefail
TMP_NEG="$(mktemp -d /private/tmp/specdock-negative-XXXXXX)"
trap 'rm -rf -- "$TMP_NEG"' EXIT
NEG_ENGINE="$TMP_NEG/engine"
NEG_TARGET="$TMP_NEG/retired-init-probe"
uv run python -m spec_dock.fixed_bundle "$NEG_ENGINE"
CLI="$NEG_ENGINE/bin/spec-dock"

set +e
"$CLI" issue start iss-00411
ISSUE_RC=$?
"$CLI" deps check iss-00411
DEPS_RC=$?
"$CLI" delete iss-00411
DELETE_RC=$?
"$CLI" init "$NEG_TARGET"
INIT_RC=$?
set -e

test "$ISSUE_RC" -ne 0
test "$DEPS_RC" -ne 0
test "$DELETE_RC" -ne 0
test "$INIT_RC" -ne 0
test ! -e "$NEG_TARGET"
```

外部に導入済みの `spec-dock` や別 consumer は使わず、この checkout から作った isolated fixed engine だけで確認する。

## 8.5 clean-checkout CI reproduction

`.github/scripts/specdock-ci-validate.sh` はsource cleanを要求するため、implementation candidateをcommitした後に独立した一時 clone で実行する。これにより開発 repo の worktree registry を変更しない。

```bash
set -euo pipefail
TMP_ROOT="$(mktemp -d /private/tmp/specdock-ci-XXXXXX)"
SOURCE="$TMP_ROOT/source"
trap 'rm -rf -- "$TMP_ROOT"' EXIT
SOURCE_SHA="$(git rev-parse --verify 'HEAD^{commit}')"
git clone --quiet --no-hardlinks --single-branch \
  --branch "$(git branch --show-current)" "$PWD" "$SOURCE"
test "$(git -C "$SOURCE" rev-parse --verify 'HEAD^{commit}')" = "$SOURCE_SHA"
bash "$SOURCE/.github/scripts/specdock-ci-validate.sh" \
  "$SOURCE" \
  "$SOURCE" \
  "$SOURCE_SHA"
test -z "$(git -C "$SOURCE" status --porcelain)"
```

開発中のdirty checkoutではこの代わりに`test_ci_fixed_validation.py`を使う。validatorのdirty-source checkを無効化しない。一時 clone は成功・失敗のどちらでも trap で除去する。

## 8.6 side-effect / scope check

```bash
git status --short
git diff --name-only
```

確認:

- Issue #411 R/D/P、inventory/report、provider/tooling source、tests、workflows、current docs/dogfood managed assets以外に予期しない差分がない。
- `spec-dock/initiatives/**` の他Issue/Epic/Initiative dataに機械的migration差分がない。
- active pointers、Git refs、worktree registry、GitHub stateを変更していない。

### verification failure recovery

| Failure | Recovery |
|---|---|
| focused test failure | 最後のgreen stepへsource restore/revertし、current invariantをforward-fix |
| full suiteだけfailure | shared module/test migration漏れを特定し、old runtime fallbackを復活させずcurrent layerで修正 |
| fixed bundleにretired file | source/package-data/referenceの残存を除去、absence testを強化 |
| CI validator SHA mismatch | checkout/expected SHA wiring修正。別branch/default refへfallbackしない |
| dogfood parity mismatch | provider正本からprojection再作成 |
| migration regression | cleanup deletionを戻し、migration module/testをretain。schema migrationは実行しない |
| stale scan false positive | 最小intentional allowlistと理由を追加。current directory丸ごと除外は禁止 |

## Step 9 — exit / handoff

### 完了条件

- AC-411-01〜08が全てgreen。
- mandatory removal manifestがsourceとfixed distributionの両方で不在。
- mandatory retain manifestが存在し、current testsがgreen。
- inventoryのconditional itemsにdelete evidenceまたはretain reasonがある。
- current CI workflowsがdeleted tests / retired commandsを参照しない。
- provider/dogfood parityがgreen。
- schema migration、他worktree update、GitHub writeを実施していない。

### PR / reportに含めるもの

- 問題: cutover後もold executable/test/docs/CI callerが残っていたこと
- source baseline: `d7c816d11bee1a73cb87273b15e486c3b669206c`
- removed source/test paths
- retained safety/migration/history pathsと理由
- old assertion -> current test mapping
- CI source SHA / distribution digest validation result
- provider/dogfood parity result
- focused / full test output summary
- residual risks

### residual risk と後続

- 他 worktree / consumerはこのIssueでは更新しない。必要なrolloutは別Issueで明示targetを持って行う。
- historical docsに旧command textが残ることはexpectedであり、current guidanceへの再浮上をdocs testで防ぐ。
- current commandが将来shared moduleを使わなくなった場合の追加orphan cleanupは別Issueで扱える。本Issueで根拠なく先取り削除しない。

## 受け入れ条件とstepの対応

| Acceptance | Primary step | Verification |
|---|---|---|
| AC-411-01 | Step 2, 3 | entrypoint tests、no `legacy_installer_main` |
| AC-411-02 | Step 4 | retired-surface test、fixed bundle path check |
| AC-411-03 | Step 1, 4, 8 | tombstone / no-write negative tests |
| AC-411-04 | Step 5, 8 | CI integration、clean-checkout reproduction |
| AC-411-05 | Step 6 | docs test、provider/dogfood parity |
| AC-411-06 | Step 3, 7 | assertion migration ledger、old harness absence |
| AC-411-07 | Step 8 | focused/full/static/fixed bundle suite |
| AC-411-08 | Step 0, 6, 8, 9 | diff/scope check、no migration/rollout/GitHub write |
