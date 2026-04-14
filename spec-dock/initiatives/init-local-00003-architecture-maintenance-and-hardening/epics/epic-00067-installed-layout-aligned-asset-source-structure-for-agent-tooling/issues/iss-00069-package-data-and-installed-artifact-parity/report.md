---
種別: 実装報告書（Issue）
ID: "iss-00069"
タイトル: "Package data and installed artifact parity"
関連GitHub: ["#69"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-13"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00069 Package data and installed artifact parity — 実装報告（LOG）

## 実装サマリー
- S01 では `install_root` hidden subtree を package-data 正本へ明示追加し、source / wheel / sdist / installed package の full inventory parity を actual build semantics で検証できるようにした。
- hermetic build/install のために repo 管理の test wheelhouse を追加し、temp venv から `python -m build --wheel --sdist --no-isolation` を `--no-index --find-links` だけで実行する経路へ固定した。

## 実装記録（セッションログ）

### 2026-04-13 00:00 - 00:00

#### 対象
- Step: S01
- AC/EC: AC-001, AC-003, EC-001

#### 実施内容
- `pyproject.toml` の `tool.setuptools.package-data.spec_dock` に `assets/install_root/.agents/**`、`assets/install_root/.codex/**`、`assets/install_root/.github/**` を追加し、hidden `install_root` subtree inclusion の正本を固定した。
- `tests/test_init_update.py` に issue-69 向けの artifact helper と parity regression を追加した。
  - source inventory
  - actual build backend で生成した wheel inventory
  - actual build backend で生成した sdist inventory
  - isolated non-editable installed package inventory
- requirement の representative 7 paths を全 artifact surface で exact-path assertion するテストを追加した。
- repo 管理の hermetic backend input として `tests/fixtures/wheelhouse/` を追加し、以下の pinned wheels を配置した。
  - `build-1.2.2-py3-none-any.whl`
  - `packaging-24.2-py3-none-any.whl`
  - `pyproject_hooks-1.2.0-py3-none-any.whl`
  - `setuptools-75.8.0-py3-none-any.whl`
  - `wheel-0.45.1-py3-none-any.whl`
- temp venv から `python -m build --wheel --sdist --no-isolation` を実行し、wheel install も `pip install --no-index --no-deps --find-links ... --target` で固定した。
- 途中で network / ambient cache 依存を含む helper 実装が code review `fail` になったため、manual artifact fabrication と cached-wheel fallback を捨て、repo 管理 wheelhouse を使う actual build semantics に切り替えた。

#### 実行コマンド / 結果
```bash
python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_package_data_includes_hidden_install_root_subtrees
.
----------------------------------------------------------------------
Ran 1 test in 0.000s

OK

python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_representative_install_root_assets_are_packaged_in_all_artifact_surfaces
.
----------------------------------------------------------------------
Ran 1 test in 2.963s

OK

python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_full_install_root_inventory_is_packaged_in_wheel_sdist_and_installed_resources
.
----------------------------------------------------------------------
Ran 1 test in 2.975s

OK

find tests/fixtures/wheelhouse -maxdepth 1 -type f | sort
tests/fixtures/wheelhouse/build-1.2.2-py3-none-any.whl
tests/fixtures/wheelhouse/packaging-24.2-py3-none-any.whl
tests/fixtures/wheelhouse/pyproject_hooks-1.2.0-py3-none-any.whl
tests/fixtures/wheelhouse/setuptools-75.8.0-py3-none-any.whl
tests/fixtures/wheelhouse/wheel-0.45.1-py3-none-any.whl
```

#### 変更したファイル
- `pyproject.toml` - hidden `install_root` subtree package-data inclusion を追加
- `tests/test_init_update.py` - hermetic build helper、inventory normalization、representative/full parity regression を追加
- `tests/fixtures/wheelhouse/build-1.2.2-py3-none-any.whl` - hermetic build backend input
- `tests/fixtures/wheelhouse/packaging-24.2-py3-none-any.whl` - hermetic build backend input
- `tests/fixtures/wheelhouse/pyproject_hooks-1.2.0-py3-none-any.whl` - hermetic build backend input
- `tests/fixtures/wheelhouse/setuptools-75.8.0-py3-none-any.whl` - hermetic build backend input
- `tests/fixtures/wheelhouse/wheel-0.45.1-py3-none-any.whl` - hermetic build backend input
- `spec-dock/active/issue/requirement.md` - issue-70 handoff surface / stale-fixture precondition を fix
- `spec-dock/active/issue/design.md` - package-data / sdist exclusion / repo-managed wheelhouse 前提を反映
- `spec-dock/active/issue/plan.md` - hermetic wheelhouse 前提の execution contract を反映
- `spec-dock/active/issue/report.md` - S01 証跡を記録

#### レビュー
- spec review:
  - requirement:
    - `pass`
  - design:
    - `pass`
  - plan:
    - `pass`
- code review:
  - 初回 verdict:
    - `fail`
  - fail reason:
    - network-bound bootstrap install / ambient cache 依存
  - 最終 verdict:
    - `pass`
  - note:
    - repo 管理 wheelhouse + actual build semantics に切り替えた後、P0/P1 指摘なし

#### コミット
- `2fe79aa` `feat(packaging): install_root配布面の収録契約を固定`

#### メモ
- `src/spec_dock/cli.py` と `src/spec_dock/assets/codex_skills/**` は S01 の範囲外として未変更。
- `setup.py` stale prune と `exclude-package-data` を使う S02 は未着手。

---

### 2026-04-13 00:00 - 00:00

#### 対象
- Step: S02
- AC/EC: AC-004, EC-002

#### 実施内容
- `setup.py` に S02 専用の観測フックを追加し、`build_py.run` の `super().run()` 後から prune 前までの build staging area に exact stale fixture set を seed / snapshot できるようにした。
- 上記フックは環境変数指定時のみ有効にし、通常 build semantics は変えないようにした。
- `tests/test_init_update.py` に次の S02 回帰を追加した。
  - wheel build staging area で fixture 14 件の pre-prune presence と wheel artifact absence を同時に検証
  - sdist temp source context で fixture 14 件の pre-build presence と sdist archive absence を同時に検証
  - `pyproject.toml` と `setup.py` の stale exclusion pattern set が approved exact set と一致することを検証

#### 実行コマンド / 結果
```bash
python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_wheel_build_prunes_seeded_stale_wrapper_era_outputs
.
----------------------------------------------------------------------
Ran 1 test in 2.932s

OK

python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_sdist_build_excludes_seeded_stale_wrapper_era_outputs
.
----------------------------------------------------------------------
Ran 1 test in 2.890s

OK

python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_stale_exclusion_patterns_are_aligned_between_pyproject_and_setup
.
----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

#### 変更したファイル
- `setup.py` - env-gated stale fixture seed / pre-prune snapshot hook を追加
- `tests/test_init_update.py` - wheel/sdist stale exclusion regression と pattern alignment regression を追加
- `spec-dock/active/issue/report.md` - S02 証跡を記録

#### レビュー
- code review:
  - verdict:
    - `pass`
  - note:
    - env 未指定時の通常 build semantics を変えずに、approved exact stale fixture/pattern set を検証できている

#### コミット
- `b6c2ba0` `test(packaging): stale除外回帰を追加`

#### メモ
- S02 は stale exclusion contract のみを扱い、isolated install smoke と handoff surface discovery は S03 へ残している。

---

### 2026-04-13 00:00 - 00:00

#### 対象
- Step: S03
- AC/EC: AC-002, EC-003

#### 実施内容
- `tests/test_init_update.py` に S03 向けの isolated installed-package helper を追加し、S01 で導入した hermetic wheelhouse + temp venv build 経路を再利用できるようにした。
- 追加した S03 回帰:
  - isolated installed package が approved handoff surface 3 paths をちょうど公開していること
  - isolated cwd + `PYTHONPATH` 除去 env で `spec-dock init` / `spec-dock update` が missing-asset diagnostics なしで通ること
  - local と installed の handoff surface inventory が一致すること
- 途中で full `install_root` equality を見る 3 本目テストは scope 逸脱として code review `fail` になったため、approved handoff surface 3 件だけを比較する形へ縮小し、テスト名も `...handoff_surface_inventories_match` に揃えた。

#### 実行コマンド / 結果
```bash
python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_isolated_wheel_install_exposes_install_root_handoff_surface
.
----------------------------------------------------------------------
Ran 1 test in 4.036s

OK

python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_isolated_wheel_install_runs_init_update_without_checkout_fallback
.
----------------------------------------------------------------------
Ran 1 test in 3.911s

OK

python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_local_and_installed_handoff_surface_inventories_match
.
----------------------------------------------------------------------
Ran 1 test in 4.025s

OK
```

#### 変更したファイル
- `tests/test_init_update.py` - isolated installed runtime snapshot helper、harness surface assertion、S03 regression を追加
- `spec-dock/active/issue/plan.md` - S03 3 本目テスト名を handoff-surface scope に合わせて更新
- `spec-dock/active/issue/report.md` - S03 証跡を記録

#### レビュー
- code review:
  - 初回 verdict:
    - `fail`
  - fail reason:
    - full `install_root` inventory equality を見る 3 本目テストが approved S03 scope を超えていた
  - 最終 verdict:
    - `pass`
  - note:
    - handoff surface 3 件だけを見る形へ絞った後、P0/P1 指摘なし

#### コミット
- `be2e813` `test(packaging): install済み配布面の検証を追加`

#### メモ
- checkout fallback 未使用の判定は、isolated runtime snapshot で `spec_dock.__file__` / `assets_dir` が `site-packages` 配下にあり、repo root が `sys.path` に含まれていないことを根拠にした。

## 遭遇した問題と解決
- 問題:
  - `setuptools` が実行環境に標準導入されておらず、`pip wheel` / cached-wheel bootstrap に頼った helper は network / ambient cache 依存になって code review `fail` となった。
  - 解決:
    - ユーザー判断で repo 管理 wheelhouse を採用し、actual build backend を temp venv + `--no-index --find-links` だけで実行するように切り替えた。

## package-parity-evidence
- full inventory parity:
  - test_or_command:
    - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_full_install_root_inventory_is_packaged_in_wheel_sdist_and_installed_resources`
  - assertion_summary:
    - source / wheel / sdist / installed package の canonical artifact-relative full inventory が一致する
  - result:
    - pass
- representative asset set:
  - test_or_command:
    - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_representative_install_root_assets_are_packaged_in_all_artifact_surfaces`
  - assertion_summary:
    - requirement の representative 7 paths が source / wheel / sdist / installed package の全 surface に存在する
  - result:
    - pass
- stale exclusion guard:
  - test_or_command:
    - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_wheel_build_prunes_seeded_stale_wrapper_era_outputs`
    - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_sdist_build_excludes_seeded_stale_wrapper_era_outputs`
    - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_stale_exclusion_patterns_are_aligned_between_pyproject_and_setup`
  - assertion_summary:
    - wheel build staging area と sdist temp source context に seeded stale fixture set が事前存在し、wheel / sdist artifact には approved stale paths が 0 件である
    - `pyproject.toml` と `setup.py` の stale exclusion pattern set が approved exact set と一致する
  - result:
    - pass
- isolated install smoke:
  - test_or_command:
    - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_isolated_wheel_install_exposes_install_root_handoff_surface`
    - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_isolated_wheel_install_runs_init_update_without_checkout_fallback`
    - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_local_and_installed_handoff_surface_inventories_match`
  - assertion_summary:
    - isolated installed package が approved handoff surface 3 paths を site-packages 由来で公開する
    - isolated cwd + `PYTHONPATH` 除去 env で `spec-dock init` / `update` が missing-asset diagnostics なしで通る
    - local と installed の handoff surface inventory が一致する
  - result:
    - pass

## 省略/例外メモ
- S01 では `python -m unittest discover -v` は未実行。plan 上の informational sweep は S99 で実施する。

---

### 2026-04-13 00:00 - 00:00

#### 対象
- Step: S99
- AC/EC: final quality gate

#### 実施内容
- issue-69 の targeted 9 tests を一括再実行し、S01-S03 の package parity / stale exclusion / isolated install smoke が branch 全体で再現することを確認した。
- `./spec-dock/scripts/spec-dock validate` を実行し、spec-dock graph / docs workspace の整合性が維持されていることを確認した。
- `python -m unittest discover -v` を informational sweep として実行し、issue-69 由来ではない既知 failure 3 件だけが残っていることを確認した。
- final code review は回収済みで、final spec review はこの更新後の report を対象に確定させる。

#### 実行コマンド / 結果
```bash
python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_package_data_includes_hidden_install_root_subtrees tests.test_init_update.TestInitUpdate.test_issue_69_representative_install_root_assets_are_packaged_in_all_artifact_surfaces tests.test_init_update.TestInitUpdate.test_issue_69_full_install_root_inventory_is_packaged_in_wheel_sdist_and_installed_resources tests.test_init_update.TestInitUpdate.test_issue_69_wheel_build_prunes_seeded_stale_wrapper_era_outputs tests.test_init_update.TestInitUpdate.test_issue_69_sdist_build_excludes_seeded_stale_wrapper_era_outputs tests.test_init_update.TestInitUpdate.test_issue_69_stale_exclusion_patterns_are_aligned_between_pyproject_and_setup tests.test_init_update.TestInitUpdate.test_issue_69_isolated_wheel_install_exposes_install_root_handoff_surface tests.test_init_update.TestInitUpdate.test_issue_69_isolated_wheel_install_runs_init_update_without_checkout_fallback tests.test_init_update.TestInitUpdate.test_issue_69_local_and_installed_handoff_surface_inventories_match
.........
----------------------------------------------------------------------
Ran 9 tests in 17.818s

OK

./spec-dock/scripts/spec-dock validate
spec-dock: ok (validate) nodes=29

python -m unittest discover -v
...
FAILED (failures=3)
```

#### informational sweep failures（scope外）
- `tests.cli_runtime.test_runtime_shell_s11.RuntimeShellS11Tests.test_final_api_call_site_and_structural_regression`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/deps.py` にある `domain.ids` import が既存 architecture rule に抵触している
- `tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json`
  - checked-in dogfooding `.meta.json` snapshot が current cutover snapshot とずれている
- `tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_subprocess_validate_and_sync_on_cutover_snapshot`
  - current dogfooding dependency graph が issue-68..72 の新規 deps を含み、cutover snapshot と一致しない

#### レビュー
- code review:
  - verdict:
    - `pass`
  - note:
    - branch diff（`c1782040cb88ce437a4ef6a14759789c6203670a..be2e813084046be3ba83a2208735a8af17b60b81`）と current working tree を確認し、issue-69 scope では P0/P1 指摘なし
- spec review:
  - verdict:
    - `pass`
  - note:
    - requirement / design / plan / report の整合、S99 証跡、scope外 failure の扱い、remaining gate 記述が workflow contract と一致していることを確認

#### close-ready judgment
- status:
  - `approved`
- rationale:
  - targeted 9 tests と `./spec-dock/scripts/spec-dock validate` が通過し、informational full-suite failure 3 件は issue-69 scope 外として report に明示済みで、final code review / final spec review ともに `pass`

#### コミット
- no-op rationale:
  - `S99` は closeout-evidence-only の品質ゲートであり、product diff は `S01`-`S03` の stage commits（`2fe79aa`, `b6c2ba0`, `be2e813`）で閉じている
  - この report 更新自体は監査証跡の確定のみを目的とし、追加の product-surface implementation commit は不要
