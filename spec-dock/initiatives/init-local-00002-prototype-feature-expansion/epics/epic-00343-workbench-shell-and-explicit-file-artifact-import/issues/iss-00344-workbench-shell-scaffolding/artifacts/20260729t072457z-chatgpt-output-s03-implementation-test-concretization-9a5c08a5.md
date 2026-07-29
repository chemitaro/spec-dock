## Recommendation

**S03 は GO。** `9a5c08a5e33c0458cbdb0db9eb103e7f35513b39` と branch `iss-00344-workbench-shell-scaffolding` は、GitHub connector 上で exact revision として確認した。以下はこの exact revision を基準にした、`pyproject.toml`、`setup.py`、`tests/unit/infra/test_init_update.py` の3ファイルだけの実装・テスト戦略である。

推奨する最小方針は次のとおり。

1. `pyproject.toml` で4つの hidden `.workbench/README.md` を個別に package-data へ追加する。
2. 現在の broad nested README exclusion は削除する。
3. `setup.py` に、template-root-relative の exact five-path allowlist を1つだけ定義する。
4. `build_py` はその allowlist 外の `README.md` を再帰的に削除し、5件を保存する。
5. broad exclusion を外した後も sdist の stale README 防御を維持するため、既存 `sdist.make_release_tree()` にも同じ allowlist predicate を適用する。
6. 既存 Issue 69 build frameworkをそのまま再利用し、指定された2 test nodeで source / wheel / normalized sdist / installed resources の exact inventory と raw bytes を検証する。

これは `TC-344-008` と `EVD-007/010/011` に限定され、runtime Workbench、generic import、docs、dogfood projection、consumer E2Eには触れない。

## Current-state findings

現在の4つの Workbench README は byte-identical である。installer 側の `_prune_legacy_scaffold()` はすでに、次の exact five-path を保存し、それ以外の nested `README.md` を削除する実装になっている。

```text
README.md
root/.workbench/README.md
initiative/.workbench/README.md
epic/.workbench/README.md
issue/.workbench/README.md
```

したがって `src/spec_dock/cli.py` は S03 で変更不要かつ read-only である。

### `pyproject.toml` の packaging gap

現在の package-data は `assets/**/*` と一部 hidden subtree だけを明示しており、template の `.workbench` subtree は明示されていない。一方、exclude-package-data には `"assets/spec_dock/templates/*/**/README.md"` が残っている。

この broad exclusion を残したまま4つの exact pathを package-data に加える方法は不可である。Setuptools では `exclude-package-data` が `package-data` や `include-package-data` より優先し、matching file を最終的に除外する。

### `setup.py` の build-prune gap

現在の `_STALE_BUILD_OUTPUT_PATTERNS` にも同じ broad pattern があり、`_prune_stale_build_outputs()` は matching path を無条件に削除する。そのため `build_py` staging に4 READMEが到達しても、現状の prune は保存できない。

既存の seed fixture には要求どおり `spec_dock/assets/spec_dock/templates/issue/legacy/README.md` が含まれる。build hook は seed、pre-prune snapshot、prune の順に実行される。

ただし現在の snapshot は seeded fixture の存在だけを記録し、allowlisted README の pre-prune inventory は記録しない。また、custom `sdist` は Python cache だけを filter しており、broad pyproject exclusionを外した後の stale nested README を除外する処理はない。

### 再利用可能な Issue 69 seam

既存テストには以下がすでにある。

- pinned local wheelhouse と backend requirements
- repository 外の temporary build context
- exact `python -m build --wheel --sdist --no-isolation --outdir <temp-dist>`
- wheel / sdist artifact 数の assertion
- wheel ZIP inventory
- sdist TAR の top-level prefix / `src/` normalization
- temporary installed package
- checkout fallback を排除した subprocess
- installed package が site-packages から import されたことの assertion
- pyproject / setup stale-pattern alignment test

build helper の exact invocation と artifact relocationは既存のまま利用できる。新しい build framework は不要である。

## Minimal production delta

### `pyproject.toml`

`[tool.setuptools.package-data].spec_dock` に、以下の4行を個別に追加する。

```text
assets/spec_dock/templates/root/.workbench/README.md
assets/spec_dock/templates/initiative/.workbench/README.md
assets/spec_dock/templates/epic/.workbench/README.md
assets/spec_dock/templates/issue/.workbench/README.md
```

同時に `[tool.setuptools.exclude-package-data].spec_dock` から次を削除する。

```text
assets/spec_dock/templates/*/**/README.md
```

`templates/README.md` は既存の `assets/**/*` で収録されるため、重複して explicit include する必要はない。その他の stale exclusion と Python cache exclusion は変更しない。

### `setup.py`

template-root-relative の正本表現を1つ導入する。

```text
README.md
root/.workbench/README.md
initiative/.workbench/README.md
epic/.workbench/README.md
issue/.workbench/README.md
```

実装上の責務は以下の3点に限定する。

1. `_STALE_BUILD_OUTPUT_PATTERNS` から broad README patternを削除する。代わりに build tree の `spec_dock/assets/spec_dock/templates/` を `rglob("README.md")` し、template rootからの normalized relative pathが allowlist にないものだけを stale setへ加える。これにより4つの `.workbench/README.md` と `templates/README.md` は保存し、`issue/legacy/README.md` や他の nested README は削除する。
2. 既存 `_write_pre_prune_snapshot()` に、観測値 `template_readmes_before_prune` として normalized template-root-relative README inventoryを追加する。test側の expected allowlistを `setup.py` から読み返してはならない。
3. 既存 `sdist.make_release_tree()` の `distributable_files` filter に、source path `src/spec_dock/assets/spec_dock/templates/` からの normalized relative README predicateを追加する。allowlist外 README を `files` から除外し、既存 Python cache filter と併用する。

### `tests/unit/infra/test_init_update.py`

追加・変更は次に限定する。

- exact five-path expected constant
- four Workbench path constant
- archive memberを template-root-relative に正規化する小さな helper
- isolated installed resource snapshot helper
- 指定された2 test methods
- 既存 stale-pattern alignment constant/test の README 部分だけを exact-allowlist contractへ更新

既存 `_ISSUE_69_STALE_EXCLUSION_ARTIFACT_RELATIVE_PATTERNS` から broad README patternを外す。pyproject/setup の非README stale patternsの equality は維持する。READMEについては別 assertionとして以下を固定する。

- pyproject broad README exclusion が存在しない。
- pyproject package-data に4 exact hidden asset pathがある。
- setup allowlist が exact five-path である。
- setup build/sdist predicate が同じ allowlistを使う。

### 技術的に修正が必要な plan 解釈

1. broad exclusion を残して explicit include で4件を復活させることはできない。`exclude-package-data` が最終優先なので、broad exclusion自体を削除する必要がある。
2. broad exclusionだけを削除し、現在の `sdist` を変更しない案も不十分。既存 `test_issue_69_sdist_build_excludes_seeded_stale_wrapper_era_outputs` が `issue/legacy/README.md` の除外を要求しており、full `test_init_update.py` gateを通せない。
3. plan の installed-resource 指示は、pytest host process で直接 `importlib.resources.files("spec_dock")` を呼ぶ解釈では誤りである。その場合 checkout側 packageを観測して偽陽性になり得る。既存 `venv_python` の isolated subprocess 内で実行する必要がある。
4. 上記は locked five-path contract の変更ではなく、その契約を setuptools の実際の優先順位と既存 sdist regression に整合させる実装具体化であるため、normative plan amendment は不要と判断する。

## Exact test design

共通 expected inventory は次の exact setとする。

```text
README.md
root/.workbench/README.md
initiative/.workbench/README.md
epic/.workbench/README.md
issue/.workbench/README.md
```

byte parity 対象は後半4件だけであり、`templates/README.md` と Workbench README の本文一致は要求しない。

### `test_workbench_readme_build_prune_preserves_allowlist_and_removes_stale_nested_readme`

Fixtures / preconditions:

- `TemporaryDirectory()` 下に `build-context`、`wheelhouse`、`sdist`、snapshot JSON を置く。
- `_issue_69_prepare_build_context()` で build context を作る。
- `SPEC_DOCK_BUILD_PY_SEED_STALE_FIXTURES=1` と `SPEC_DOCK_BUILD_PY_PRE_PRUNE_SNAPSHOT=<temporary-json>` を設定する。
- expected pre-prune README setは five-path allowlist + `issue/legacy/README.md` の6件。

Build:

- 既存 `_issue_69_build_artifacts_with_local_wheelhouse()` を `build_env` 付きで1回呼ぶ。

Pre-prune assertions:

- `expected_seeded_stale_fixture_paths` が既存 seed fixture setと一致。
- `present_before_prune` が同じ seed fixture setと一致。
- `template_readmes_before_prune` が five allowlist + `issue/legacy/README.md` の6件と一致。

Post-prune assertions:

- wheel memberから exact package prefix `spec_dock/assets/spec_dock/templates/` だけを選び、`README.md` basenameを持つ regular entriesを正規化。
- normalized wheel README inventory == exact five-path。
- `issue/legacy/README.md` は存在しない。
- selected archive entry countとnormalized unique path countが一致し、duplicateを拒否する。

この test は hidden README package-data 欠落、broad prune残存、stale prune無効、seed hook不動作、unexpected nested README、duplicate ZIP entryを区別して検出する。

### `test_workbench_readme_distribution_inventory_and_bytes_match_all_surfaces`

Build preconditions:

- normal source treeを temporary build contextへcopy。
- seed environment variablesは設定しない。
- `_issue_69_build_artifacts_with_local_wheelhouse()` を1回だけ実行。
- 同一 build の wheel と sdistを観測し、その wheelを isolated environmentへinstall。

Source observation:

- `src/spec_dock/assets/spec_dock/templates/` の `rglob("README.md")` regular filesを正規化。
- source inventory == exact five-path。
- four Workbench payloadsは raw bytesで同一。

Wheel observation:

- exact package subtreeだけを選ぶ。
- directory entriesは除外。
- `wheel_zip.read()` で raw bytes取得。
- normalized inventory == exact five-path。
- duplicate memberを拒否。

Sdist observation:

- regular filesだけを対象にする。
- archive root名/versionをhard-codeせず、最初のpath componentを1つ除去。
- 残りが exact prefix `src/spec_dock/assets/spec_dock/templates/` で始まるものだけを対象にする。
- `extractfile(member).read()` で raw bytesを読み、`extractall()` は使わない。
- archive root componentが1種類だけであること、normalized inventory == exact five-path、duplicate pathがないことを確認。

Installed package resource observation:

- 同じ wheelを、build helperが返した `venv_python` のsite-packagesへinstall。
- `_issue_69_install_target_packages()` を再利用し、`wheelhouse=` を渡して `--no-index --find-links` を維持。
- cwdは repository 外、environmentは `_issue_69_runtime_env_without_checkout_fallback()`。
- subprocess内で `importlib.resources.files("spec_dock")` を呼ぶ。
- Python 3.10 compatible に `Traversable.iterdir()` を再帰利用。
- 既存 `_issue_69_assert_runtime_snapshot_uses_installed_package()` で site-packages配下かつcheckout外を検証。
- installed inventoryは resources rootからのrelative pathとして exact five-path。

Cross-surface assertions:

- `source == wheel == sdist == installed == expected five-path`。
- 4 Workbench pathごとに `source_bytes == wheel_bytes == sdist_bytes == installed_bytes`。
- SHA-256 は diagnostic と report evidenceに使うが、testは raw bytes equalityで判定。
- source内4 pathの bytesも相互に同一。

False-positive / false-negative prevention:

- exact set equalityでextra/missingを検出。
- set化前後の件数を比較してduplicateを検出。
- raw bytes比較でdecode/newline normalizationを防止。
- installed observationをisolated subprocessで行いcheckout importを拒否。
- wheelとsdistを同じ build invocationのartifactとして比較。
- expected setはproduction constantからimportしない。
- archive pathは `endswith()` ではなく exact subtree prefixで選ぶ。

## Reuse map

| Existing seam | S03での利用 | 最小拡張 |
|---|---|---|
| `_issue_69_resolve_wheelhouse()` | backend wheelのoffline確認 | なし |
| `_issue_69_prepare_build_context()` | repository外build context作成 | なし |
| `_issue_69_build_artifacts_with_local_wheelhouse()` | wheel/sdistのsingle build | なし |
| `_issue_69_install_target_packages()` | built wheelのoffline temporary install | `wheelhouse=` を渡して利用 |
| `_issue_69_runtime_env_without_checkout_fallback()` | checkout import防止 | なし |
| `_issue_69_assert_runtime_snapshot_uses_installed_package()` | site-packages / repo外確認 | snapshot keyを同じ形にする |
| `_issue_69_collect_wheel_file_inventory()` | prune testのwheel全inventory | そのまま利用可 |
| `_issue_69_collect_sdist_source_file_inventory()` | sdist normalizationの参考 | bytes取得には局所helper追加 |
| stale exclusion extractors/alignment test | non-README pattern parity | README allowlist assertionを別軸で追加 |
| `test_workbench_readme_assets_are_byte_identical_and_complete` | source canonical bytesの既存証拠 | 変更不要 |

新規 helper は最大でも、wheel template README payload collector、sdist template README payload collector、isolated installed template README snapshot collectorの局所3種に留める。これらは buildを実行せず、既存 build成果物を読むだけにする。

## Red / Green / refactor

### Red

1. exact expected constantsと distribution testを先に追加する。
2. 現在の production で distribution testを実行する。
3. 期待する Red は、wheel / sdist / installed のいずれかで4 hidden READMEがmissingになること。
4. prune testを追加する。最初は既存 snapshot fieldsとpost-wheel exact inventoryをassertする。
5. snapshotに `template_readmes_before_prune` 観測だけを追加し、pre-pruneまたはpost-prune inventoryがsix/five contractを満たさないことを確認する。
6. malformed test、wrong prefix、host checkout importだけを理由とする failure は有効なRedとして採用しない。

production変更前から2 nodeともGreenの場合は停止し、build cache、unexpected manifest、testのsurface選択漏れを調査する。

### Green

1. `pyproject.toml` に4 exact package-data pathを追加する。
2. pyproject/setup双方から broad README stale patternを削除する。
3. `setup.py` に exact allowlist と build-tree README pruneを追加する。
4. pre-prune snapshotへobserved README inventoryを追加する。
5. existing custom sdistへ同じallowlist predicateを追加する。
6. 2 exact nodeを実行する。
7. full `tests/unit/infra/test_init_update.py` を実行する。

### Refactor

Green後に許可する整理は duplicate prefix literalを class constantへ寄せること、payload collectionの小さなdiagnostic整形、assertion messageへのmissing/unexpected/hashes追加だけ。

generic distribution test framework、setup helperの別module化、README生成機構、package backend変更、fixture cache、runtime import/copy変更、production allowlistをtest expected値としてimportすることは禁止。

## Verification order

1. 指定2 node。
2. full `tests/unit/infra/test_init_update.py`。
3. plan記載の scoped Ruff check。
4. plan記載の scoped Ruff format。
5. plan記載の scoped Mypy。
6. `git diff --check`。
7. base SHAからの exact allowed-path diff。
8. repository cleanliness。`build/`、`dist/`、`*.egg-info/`、temporary venv、wheel、sdist、snapshot JSON がrepository内に現れた場合は不合格。

plan指定Mypyは S03で変更する `setup.py` を対象にしない。これは planどおり実行し、`setup.py` は Ruffとruntime build testsで検証する。

## Risks and stop conditions

| Risk | Guard | Stop condition |
|---|---|---|
| broad excludeがhidden READMEを再除外 | broad pattern削除、explicit 4-path include | wheel/sdist pre-pruneに4件が到達しない |
| sdist stale defense消失 | existing custom sdistにexact predicate | existing Issue 69 sdist test failure |
| build pruneがallowlistも削除 | pre-prune six / post-prune five | missing allowlisted path |
| stale READMEが残留 | exact inventory equality | any extra normalized README |
| ZIP/TAR path normalization誤り | exact prefix、root count、duplicate count | archive layoutを一意に正規化できない |
| installed observationがcheckoutを読む | isolated cwd/envとsite-packages assertion | repo rootがsys.pathまたはresource pathに現れる |
| network利用 | pinned wheelhouse、no-index、no-isolation | index accessまたは不足wheel |
| testがproduction constantをexpectedに使用 | independent test constant | tautological comparison |
| static alignment testを弱める | non-README pattern equalityを維持 | 既存 stale guardの削除・緩和 |
| scope外変更 | exact three-path diff | runtime/docs/dogfood/dependency change |
| backend mechanism追加が必要 | existing build_py/sdistのみ利用 | MANIFEST.in、新backend、dependencyが必要 |
| exact five-path変更が必要 | implementation停止 | planning amendmentとfresh review |

### Assumptions and uncertainty

- 実際の wheel/sdist buildはこの分析では実行していない。Redの正確な最初のmissing surfaceは未検証であり、実装時のbuild outputが ground truth。
- project local wheelhouse は pinned backendを使用するため、最終判断は pinned backendでの2 exact testsに置く。
- `python -m build` がwheelをsourceから直接作るかsdist経由で作るかにtestを依存させない。
- branchが進んだ場合、このbriefは新HEADへ自動適用せず、baseからのdiffを再確認する。
- sdist `files` path形式が想定と異なる場合、局所normalizationは調整できるがfive-path contractは変更しない。

## Issue 346 handoff

| S03で閉じる evidence | Issue 346へ残すもの |
|---|---|
| source exact five-path inventory | candidate wheelによるconsumer product E2E |
| custom build_py pre/post prune | generic `artifact import file` |
| `issue/legacy/README.md` stale removal | generic importを含むintegrated dogfood |
| wheel exact inventory / bytes | opt-in full regression |
| normalized sdist exact inventory / bytes | cross-feature repair |
| isolated installed package resources inventory / bytes | Epic-wide QA / code / spec review |
| local wheelhouse / no-network evidence | 残余 Epic integration PR |
| scoped Ruff / format / Mypy / diff | merge、auto-merge、branch削除、Issue finish |

temporary wheel installationによる `importlib.resources` 検査は `TC-344-008` の focused package-resource evidence であり、Issue 346のconsumer workflow E2Eではない。

dev-coder は EVD-007向けに wheel/sdist filenames、four surface inventories、canonical Workbench SHA-256、per-surface byte equality、pre-prune six-path inventory、post-prune five-path inventory、stale path absenceを返す。EVD-011向けには exact static commandとexit statusを返す。EVD-010のdependency、deferred gates、delivery ownerのcanonical report記録はmain orchestratorが担当する。

## Dev-coder handoff checklist

- [ ] base revisionが `9a5c08a5e33c0458cbdb0db9eb103e7f35513b39` である。
- [ ] 変更pathを `pyproject.toml`、`setup.py`、`tests/unit/infra/test_init_update.py` の3件に限定する。
- [ ] `pyproject.toml` に4 exact hidden README pathを追加する。
- [ ] broad nested README exclusionをpyproject/setup双方から削除する。
- [ ] setupにtemplate-root-relative exact five-path allowlistを置く。
- [ ] `build_py` がallowlist外 READMEだけを削除する。
- [ ] pre-prune snapshotがobserved README inventoryを記録する。
- [ ] existing custom `sdist` が同じallowlist外 READMEを除外する。
- [ ] non-README stale patternsとPython cache patternsを変更しない。
- [ ] existing stale-pattern alignment testを弱めず、README部分だけbehavioral allowlist assertionへ移す。
- [ ] 指定された2 test methodをexact nameで追加する。
- [ ] source / wheel / sdist / installed inventoryをexact equalityで比較する。
- [ ] four Workbench payloadをraw bytesで比較し、SHA-256をdiagnosticとして記録する。
- [ ] installed resourceはisolated subprocessの `importlib.resources` で読む。
- [ ] wheel installもlocal wheelhouse / no-indexで完結させる。
- [ ] duplicate ZIP/TAR paths、extra paths、missing pathsを個別に検出する。
- [ ] repository内にbuild outputを生成しない。
- [ ] exact two nodes、full test file、Ruff check、Ruff format、Mypy、diff-checkを順に通す。
- [ ] base SHAからのchanged pathがexact three-pathであることを確認する。
- [ ] runtime Workbench、provider docs、dogfood、dependencies、generic importを変更しない。
- [ ] exact inventoryを成立させるためにfive-path変更や新backendが必要になった場合は実装を停止する。
