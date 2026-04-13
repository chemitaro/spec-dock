---
種別: 実装計画書（Issue）
ID: "iss-00069"
タイトル: "Package data and installed artifact parity"
関連GitHub: ["#69"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-13"
依存: ["requirement.md", "design.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00069 Package data and installed artifact parity — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC:
  - `AC-001`
  - `AC-002`
  - `AC-003`
  - `AC-004`
- EC:
  - `EC-001`
  - `EC-002`
  - `EC-003`
- 制約:
  - installer canonical source discovery は切り替えない
  - `src/spec_dock/cli.py` は read only とし、`codex_skills` runtime authority は issue-70 まで維持する
  - package parity 比較は canonical artifact-relative strings で行う
  - `local package install` は isolated non-editable wheel install に限定する
- hidden `install_root` subtree inclusion の正本は `pyproject.toml` の `tool.setuptools.package-data.spec_dock` に固定する
- wheel stale prune の正本は `setup.py build_py`、sdist stale exclusion の正本は `pyproject.toml` の `tool.setuptools.exclude-package-data.spec_dock` に固定する
- hermetic build/install に必要な `build` / `setuptools` / `wheel` / `packaging` / `pyproject_hooks` は repo 管理の test wheelhouse から供給する
- 各 step 完了ごとに code review を通し、stage 単位でコミットする
  - `S99` で最終品質ゲートとして final code review と final spec review を実施し、`pass` まで回す

## マイルストーン一覧
- M1:
  - 対象:
    - canonical inventory / normalization helper と parity regression の土台
    - hidden `install_root` subtree package-data inclusion
  - exit:
    - source / wheel / sdist / installed package の full inventory parity を観測できる
- M2:
  - 対象:
    - wheel stale prune と sdist stale exclusion の fixture 回帰
  - exit:
    - requirement の exact stale fixture set で staging-presence / artifact-absence を wheel / sdist 両方で証明できる
- M3:
  - 対象:
    - isolated installed smoke
    - handoff evidence / final validation / final review
  - exit:
    - `install_root` handoff surface installed discovery、report evidence、final gate、最終コミットが揃っている

## 実装順序の根拠
- 依存関係の正本:
  - `design.md` の `依存関係分析`
  - `design.md` の `インターフェース契約`
- sequencing rule:
  - 先に inventory 比較と package inclusion を固定し、artifact parity の基盤を作る
  - 次に stale exclusion を wheel / sdist で閉じる
  - 最後に isolated installed smoke と handoff evidence を足して issue-70 前提を揃える
- step ordering notes:
  - `S01` は package inclusion と parity instrumentation を確定する前提 step
  - `S02` は `S01` の artifact generation が通ることを前提に stale exclusion を追加する
  - `S03` は `S01`/`S02` の build contract を使って isolated install smoke を閉じる
  - `S99` は branch 全体の close-ready 判断を行う

## ステップ一覧
- S01:
  - 観測可能な振る舞い:
    - hidden `install_root` subtree を含む full inventory が source / wheel / sdist / installed package で一致する
  - closes:
    - `AC-001`
    - `AC-003`
    - `EC-001`
  - review gate:
    - code review `pass`
    - targeted validation `pass`
    - stage commit
- S02:
  - 観測可能な振る舞い:
    - wrapper-era stale fixture set に対する wheel prune / sdist exclusion が同じ regression suite で観測できる
  - closes:
    - `AC-004`
    - `EC-002`
  - review gate:
    - code review `pass`
    - targeted validation `pass`
    - stage commit
- S03:
  - 観測可能な振る舞い:
    - isolated non-editable wheel install で `install_root` handoff surface の installed discovery が確認できる
  - closes:
    - `AC-002`
    - `EC-003`
  - review gate:
    - code review `pass`
    - targeted validation `pass`
    - stage commit
- S90:
  - 観測可能な振る舞い:
    - report / docs impact が整理され、handoff-validation-evidence の元になる証跡が issue report に記録される
  - closes:
    - report evidence contract
  - review gate:
    - no-op 可。ただし `report.md` 更新は必須
- S99:
  - 観測可能な振る舞い:
    - branch 全体が final validation と final review を通過し、issue-70 handoff-ready になる
  - closes:
    - final exit contract
  - review gate:
    - final code review `pass`
    - final spec review `pass`
    - final validation `pass`
    - final commit

## 要件 ↔ ステップ対応
- `AC-001` -> `S01`
- `AC-002` -> `S03`
- `AC-003` -> `S01`
- `AC-004` -> `S02`
- `EC-001` -> `S01`
- `EC-002` -> `S02`
- `EC-003` -> `S03`

## レビュー / QA ゲート方針
- RG1 step review:
  - timing:
    - `S01` 完了後
    - `S02` 完了後
    - `S03` 完了後
  - scope:
    - 当該 step の diff のみ
  - commit gate:
    - `pass` まで review loop を回し、`report.md` 更新後に step 単位でコミットする
- QG1 execution validation:
  - timing:
    - 各 step 完了時
    - `S99` で全体再確認
  - scope:
    - step 対応の targeted tests / commands
  - commit gate:
    - validation 成功を `report.md` に記録してからコミットする
- SG1 final spec review:
  - timing:
    - `S99`
  - scope:
    - issue-69 の requirement / design / plan / report と branch diff の整合
  - commit gate:
    - `pass` まで review loop を回し、必要な doc/report 反映後に最終コミットする

## 実行ルール（全ステップ共通）
- plan はこの issue の実装着手前に spec review を通して固定する
- cadence / approval policy は `workflow_issue.md` を正本とする
- 実装は `Red → Green → Refactor → code review → fix → re-review → report → commit/no-op` の順で進める
- 各 step は 1 つの観測可能な振る舞いに閉じる
- failing test は issue scope に必要な最小本数から始める
- `Refactor` は green 維持を前提とした bounded cleanup に限る
- `report.md` には command evidence、review verdict、修正内容、commit hash を残す
- 各 step の review / validation / commit 証跡は当該 step 完了時点で `report.md` に追記する
- build invocation は repo 管理の test wheelhouse を入力にした temp venv から `python -m build --wheel --sdist --no-isolation` を使う
- isolated install smoke は temp dir に build した wheel を使い、repo 管理の test wheelhouse を入力に `pip install --no-index --find-links` で bootstrap した env から site-packages inventory を checkout fallback なしで観測する
- `python -m unittest discover -v` は informational sweep とし、issue scope 外の既存 failure がある場合は report に failing tests と理由を記録する
- no-op を選ぶ場合でも理由を `report.md` に残す

## 実装ステップ

### S01 — package-data inclusion と full inventory parity を固定する
- target:
  - `install_root` hidden subtree の package-data inclusion、repo 管理の test wheelhouse、canonical artifact-relative inventory parity を実装する
- design refs:
  - `インターフェース契約 > Packaging inclusion contract`
  - `インターフェース契約 > Artifact comparison contract`
  - `変更計画 > Modify`
- step boundary:
  - `pyproject.toml`、repo 管理の test wheelhouse、`tests/test_init_update.py` の parity foundation に閉じる
  - stale exclusion fixture と isolated install smoke は後続 step に回す

#### B1 — parity foundation
- purpose:
  - source / wheel / sdist / installed package を同じ canonical basis で比較できるようにする
- files:
  - `pyproject.toml`
  - `tests/fixtures/wheelhouse/**`
  - `tests/test_init_update.py`

##### I1 — Red/Green/Refactor
- slice goal:
  - hidden `install_root` subtree が現在は artifact に乗らないことを failing regression で固定し、その後 inclusion と parity を通す

###### Red
- failing test:
  - full install_root inventory を source / wheel / sdist / installed package の 4 面で比較する regression を追加する
  - representative artifact set の exact 7 paths を wheel / sdist / installed package で明示 assertion する
- expected failure:
  - hidden `install_root` subtree が wheel / sdist / installed package に欠落して fail する

###### Green
- minimum implementation:
  - `tool.setuptools.package-data.spec_dock` に hidden `install_root` subtree inclusion pattern を追加する
  - repo 管理の test wheelhouse を追加し、temp venv から `python -m build --wheel --sdist --no-isolation` を hermetic に実行できるようにする
  - test helper に canonical artifact-relative normalization と recursive inventory collection を実装する
- pass condition:
  - full inventory parity regression と representative set assertion が通る
  - `codex_skills` 既存 package surface を壊さない

###### Refactor
- 目的:
  - inventory helper / artifact listing helper / temp build helper の重複を整理する
- guardrail:
  - installer behavior を変えない
  - `src/spec_dock/cli.py` と `src/spec_dock/assets/codex_skills/**` は変更しない

#### step gate
- review:
  - code reviewer に package-data inclusion rule と parity helper の妥当性をレビューさせる
- expected tests:
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_full_install_root_inventory_is_packaged_in_wheel_sdist_and_installed_resources`
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_representative_install_root_assets_are_packaged_in_all_artifact_surfaces`
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_package_data_includes_hidden_install_root_subtrees`
  - `find tests/fixtures/wheelhouse -maxdepth 1 -type f | sort` で expected backend wheels が揃っている
- report update:
  - inclusion rule、artifact parity、review verdict、test 結果を `report.md` に追記する
- commit:
  - `feat(packaging): install_root配布面の収録契約を固定` 相当の Conventional Commit を作る

### S02 — stale exclusion guard を wheel / sdist で実証する
- target:
  - requirement の exact stale fixture set に対する wheel prune / sdist exclusion を同じ regression suite で検証する
- design refs:
  - `インターフェース契約 > Stale exclusion contract`
  - `要件 / 例外 -> verification mapping`
- step boundary:
  - `setup.py` と `tests/test_init_update.py` の stale exclusion contract に閉じる
  - package inclusion の source-of-truth は再変更しない

#### B1 — wheel and sdist stale fixtures
- purpose:
  - vacuous pass を防ぎ、fixture が存在したうえで artifact から除外されることを示す
- files:
  - `setup.py`
  - `tests/test_init_update.py`

##### I1 — Red/Green/Refactor
- slice goal:
  - wheel build staging area と sdist temp source context で stale fixture set を seeded し、artifact absence を観測する

###### Red
- failing test:
  - wheel build staging area で fixture presence と wheel listing 0 件を同時に要求する regression
  - sdist temp source context で fixture presence と sdist listing 0 件を同時に要求する regression
  - `pyproject.toml` と `setup.py` の stale pattern set 整合 guard
- expected failure:
  - fixture precondition または artifact exclusion のどちらかが満たせず fail する

###### Green
- minimum implementation:
  - `setup.py build_py` の stale prune contract を requirement の exact pattern set と同期させる
  - test harness に wheel build staging area 注入と sdist temp source context 注入を追加する
  - `tool.setuptools.exclude-package-data.spec_dock` の exact pattern set を guard する
- pass condition:
  - seeded stale fixture regression が wheel / sdist の両方で通る
  - representative install_root assets inclusion regression と両立する

###### Refactor
- 目的:
  - stale pattern inventory と build harness の重複を整理する
- guardrail:
  - stale exclusion の exact pattern set を broaden しない
  - positive parity inventory を exclusion logic に巻き込まない

#### step gate
- review:
  - code reviewer に wheel/sdist stale exclusion mechanism と test harness の妥当性をレビューさせる
- expected tests:
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_wheel_build_prunes_seeded_stale_wrapper_era_outputs`
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_sdist_build_excludes_seeded_stale_wrapper_era_outputs`
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_stale_exclusion_patterns_are_aligned_between_pyproject_and_setup`
- report update:
  - seeded stale fixture set、wheel/sdist precondition、review verdict、test 結果を `report.md` に追記する
- commit:
  - `test(packaging): stale除外回帰を追加` 相当の Conventional Commit を作る

### S03 — isolated installed smoke と handoff-surface discovery を閉じる
- target:
  - isolated non-editable wheel install で `install_root` handoff surface の installed discovery と package-installed smoke を確認する
- design refs:
  - `インターフェース契約 > Installed smoke contract`
  - `要件 -> 設計マッピング`
- step boundary:
  - `tests/test_init_update.py` と issue report の evidence に閉じる
  - installer cutover や consumer repo reflection 判定には踏み込まない

#### B1 — installed package evidence
- purpose:
  - issue-70 へ渡す installed discovery evidence を isolated env で収集する
- files:
  - `tests/test_init_update.py`

##### I1 — Red/Green/Refactor
- slice goal:
  - package-installed `init/update` smoke を補助観測としつつ、`spec_dock/assets/install_root/.agents/host-adapters/meta.json`、`spec_dock/assets/install_root/.codex/agents/spec-dock.toml`、`spec_dock/assets/install_root/.github/agents/spec-dock.agent.md` の 3 件を主 assertion にする

###### Red
- failing test:
  - isolated wheel install から installed package resources を走査し、`meta.json` / `.codex/agents/spec-dock.toml` / `.github/agents/spec-dock.agent.md` の 3 件が見えることを要求する regression
  - 同じ isolated env で `spec-dock init` / `update` を実行し、checkout fallback なしの site-packages-only execution を要求する regression
- expected failure:
  - installed inventory または smoke assertion が不足して fail する

###### Green
- minimum implementation:
  - temp wheel build / isolated venv install helper を追加または拡張する
  - site-packages 内 package data inventory と command execution evidence を test から収集する
- pass condition:
  - handoff surface discovery 3 件と representative set parity が isolated env で通る
  - `init/update` smoke は missing asset error なしで通る

###### Refactor
- 目的:
  - temp env helper と inventory helper を整理し、report 用 evidence を取りやすくする
- guardrail:
  - smoke 成功だけで pass にしない
  - consumer repo reflection 成否を assertion に含めない

#### step gate
- review:
  - code reviewer に isolated install helper と handoff-surface assertion の十分性をレビューさせる
- expected tests:
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_isolated_wheel_install_exposes_install_root_handoff_surface`
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_isolated_wheel_install_runs_init_update_without_checkout_fallback`
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_local_and_installed_install_root_inventories_match`
- report update:
  - installed smoke、site-packages inventory、handoff surface evidence、review verdict を `report.md` に追記する
- commit:
  - `test(packaging): install済み配布面の検証を追加` 相当の Conventional Commit を作る

### S90 — report / docs impact resolution
- 対象:
  - `report.md`
- 対応:
  - `S01` / `S02` / `S03` で逐次追記した validation / review / commit 証跡の不足分だけを issue report で補完する
  - `package-parity-evidence` の各欄を実測値で埋める
  - requirement / design / plan の追加修正が不要なら no-op とし、その判断を report に記録する

### S99 — final diff review quality gate
- branch diff scope:
  - `iss-00069-package-data-and-installed-artifact-parity` branch の全差分
- required validation:
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_full_install_root_inventory_is_packaged_in_wheel_sdist_and_installed_resources`
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_representative_install_root_assets_are_packaged_in_all_artifact_surfaces`
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_package_data_includes_hidden_install_root_subtrees`
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_wheel_build_prunes_seeded_stale_wrapper_era_outputs`
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_sdist_build_excludes_seeded_stale_wrapper_era_outputs`
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_stale_exclusion_patterns_are_aligned_between_pyproject_and_setup`
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_isolated_wheel_install_exposes_install_root_handoff_surface`
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_isolated_wheel_install_runs_init_update_without_checkout_fallback`
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_69_local_and_installed_install_root_inventories_match`
  - `./spec-dock/scripts/spec-dock validate`
  - `python -m unittest discover -v` は informational sweep として実施する
  - full suite が issue-69 scope 外の既存 failure を返した場合、targeted scope と `validate` が通っており、report に failing tests と out-of-scope 理由が記録されていれば `final validation pass` を阻害しない
- reviewer approvals:
  - final code review `pass`
  - final spec review `pass`
- report update:
  - final diff review verdict、validation summary、handoff evidence、spec review verdict、close-ready 判断を `report.md` に残す
- commit expectation:
  - `report.md` 更新後に差分確認し、必要なら closeout commit を作成する
  - product diff が各 step の implementation commits で閉じており、`S99` が closeout-evidence-only 更新に留まる場合は report-only commit でもよい

## 未確定事項
- なし:
  - hidden `install_root` subtree inclusion は `pyproject.toml` package-data の explicit pattern 列挙で閉じる
  - wheel stale prune と sdist stale exclusion は別メカニズムとして検証し、issue-70 まで installer runtime authority は切り替えない

## final exit contract
- AC/EC 達成:
  - full inventory parity、harness-proven stale exclusion、isolated installed handoff-surface discovery が code と tests で確認できる
- docs impact resolved:
  - issue report に `package-parity-evidence` と review / validation / commit 証跡が記録されている
- final diff approved:
  - final code review `pass`
  - final spec review `pass`
  - required validation 完了
