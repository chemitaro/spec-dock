---
種別: 実装報告書（Issue）
ID: "iss-00069"
タイトル: "Package data and installed artifact parity"
関連GitHub: ["#69"]
状態: "draft"
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
- pending:
  - S02 stage commit を次に作成する

#### メモ
- S02 は stale exclusion contract のみを扱い、isolated install smoke と handoff surface discovery は S03 へ残している。

## 遭遇した問題と解決
- 問題:
  - `setuptools` が実行環境に標準導入されておらず、`pip wheel` / cached-wheel bootstrap に頼った helper は network / ambient cache 依存になって code review `fail` となった。
  - 解決:
    - ユーザー判断で repo 管理 wheelhouse を採用し、actual build backend を temp venv + `--no-index --find-links` だけで実行するように切り替えた。

## 今後の推奨事項
- S02 では requirement の exact stale fixture set を使い、wheel build staging area と sdist archive listing の両方で exclusion guard を閉じる。
- S03 ではこの wheelhouse を再利用し、isolated install smoke と 3 件の handoff surface discovery を閉じる。

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
    - pending_for_s03
  - assertion_summary:
    - pending_for_s03
  - result:
    - pending_for_s03

## 省略/例外メモ
- S01 では `python -m unittest discover -v` は未実行。plan 上の informational sweep は S99 で実施する。
