---
種別: 実装計画書（Issue）
ID: "iss-00068"
タイトル: "Install root tree and asset classification"
関連GitHub: ["#68"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-13"
依存: ["requirement.md", "design.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00068 Install root tree and asset classification — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC:
  - `AC-001`
  - `AC-002`
  - `AC-003`
- EC:
  - `EC-001`
  - `EC-002`
  - `EC-003`
- 制約:
  - `install_root` を authoritative source として導入するが、`src/spec_dock/cli.py` の source discovery 切替は行わない
  - `codex_skills` は current installer compatibility mirror として維持する
  - package data inclusion、managed cleanup、packaged-install verification は扱わない
  - uppercase path は原則禁止だが、shared skill asset の既存 filename convention である `SKILL.md` は user-approved 例外として扱う
  - 各 step 完了ごとに code review を通し、stage 単位でコミットする
  - `S99` で最終品質ゲートとして spec review を実施し、`pass` まで回す

## マイルストーン一覧
- M1:
  - 対象:
    - `install_root` authoritative tree の新設
    - in-scope 11 assets の authoritative placement
    - compatibility mirror 維持
  - exit:
    - `src/spec_dock/assets/install_root/` に `.agents` / `.codex` / `.github` / `.github/workflows` が揃い、in-scope inventory 全件が配置されている
- M2:
  - 対象:
    - issue-68 向け parity / duplicate boundary verification 追加
  - exit:
    - `tests/test_init_update.py` で inventory 外 duplicate 不在、compatibility mirror parity、既存回帰 subset を観測できる
- M3:
  - 対象:
    - final validation
    - report 更新
    - final diff / final spec gate
  - exit:
    - required validation、step-level code review、final spec review、report 証跡、最終コミットが揃っている

## 実装順序の根拠
- 依存関係の正本:
  - `design.md` の `依存関係分析` と `インターフェース契約`
- sequencing rule:
  - source tree foundation を先に確定し、その上で verification を足す
  - installer / packaging / cleanup は downstream issue のため、この issue では read only に留める
- step ordering notes:
  - `S01` が authoritative tree と compatibility mirror の基盤を作る
  - `S02` は `S01` の配置結果を観測する verification を追加する
  - `S99` は step で積んだ review/validation を横断確認し、final spec gate を閉じる

## ステップ一覧
- S01:
  - 観測可能な振る舞い:
    - `install_root` に install-shaped authoritative tree と in-scope assets が追加される
  - closes:
    - `AC-001`
    - `AC-002`
    - `EC-001`
    - `EC-002`
    - `EC-003`
  - review gate:
    - code review `pass`
    - targeted validation `pass`
    - stage commit
- S02:
  - 観測可能な振る舞い:
    - issue-68 専用 verification により authoritative placement / duplicate boundary / mirror parity が検証できる
  - closes:
    - `AC-003`
  - review gate:
    - code review `pass`
    - targeted validation `pass`
    - stage commit
- S90:
  - 観測可能な振る舞い:
    - docs/report impact が整理され、issue report に step evidence が記録される
  - closes:
    - report evidence contract
  - review gate:
    - no-op 可。ただし `report.md` は更新必須
- S99:
  - 観測可能な振る舞い:
    - branch 全体が final validation と final spec gate を通過し、close-ready な diff になる
  - closes:
    - final exit contract
  - review gate:
    - final code review `pass`
    - final spec review `pass`
    - final validation `pass`
    - final commit

## 要件 ↔ ステップ対応
- `AC-001` -> `S01`
- `AC-002` -> `S01`
- `AC-003` -> `S02`
- `EC-001` -> `S01`
- `EC-002` -> `S01`
- `EC-003` -> `S01`

## レビュー / QA ゲート方針
- RG1 step review:
  - timing:
    - `S01` 完了後
    - `S02` 完了後
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
    - issue-68 の requirement / design / plan / report と branch diff の整合
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
- no-op を選ぶ場合でも理由を `report.md` に残す

## 実装ステップ

### S01 — authoritative install_root tree を追加する
- target:
  - `src/spec_dock/assets/install_root/` を新設し、in-scope 11 assets を authoritative path へ配置する
- design refs:
  - `インターフェース契約 > Directory contract`
  - `インターフェース契約 > Temporary coexistence contract`
  - `変更計画 > Add`
- step boundary:
  - provider-side assets の追加と compatibility mirror の整合まで
  - `cli.py` / package data / installer cutover には触れない

#### B1 — authoritative subtree seed
- purpose:
  - install-shaped top-level subtree を固定する
- files:
  - `src/spec_dock/assets/install_root/.agents/**`
  - `src/spec_dock/assets/install_root/.codex/**`
  - `src/spec_dock/assets/install_root/.github/**`

##### I1 — Red/Green/Refactor
- slice goal:
  - `install_root` の top-level と in-scope asset placements を追加する

###### Red
- failing test:
  - `tests/test_init_update.py` に issue-68 向け authoritative placement テストを先に追加し、`install_root` 不在で fail させる
- expected failure:
  - `src/spec_dock/assets/install_root/...` が存在せず fail

###### Green
- minimum implementation:
  - skill 7 件、meta 1 件、native shim 2 件、workflow 1 件を `install_root` へ追加する
  - workflow seed は repo root `.github/workflows/ci.yml` の current content を provider-side authoritative asset としてコピーする
  - legacy `codex_skills` assets は削除せず維持する
- pass condition:
  - existence test が通る
  - `SKILL.md` を除き、repo 上に uppercase 新規 path が追加されない

###### Refactor
- 目的:
  - mirror parity を崩さず file placement を整理する
- guardrail:
  - asset content を不用意に書き換えない
  - `codex_skills` mirror を installer compatibility のために維持する

#### step gate
- review:
  - code reviewer に authoritative tree / compatibility mirror / workflow seed 方針をレビューさせる
- expected tests:
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_68_install_root_tree_exists`
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_68_authoritative_inventory_paths_are_classified_under_install_root`
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_68_workflow_seed_matches_repo_root_ci_workflow`
  - `find src/spec_dock/assets/install_root -print | rg '[A-Z]' | rg -v '/SKILL\\.md$'` が no match
- report update:
  - asset 追加内容、review verdict、test 結果、workflow seed 根拠を `report.md` に追記する
- commit:
  - `feat(spec): install_root正本ツリーを追加` 相当の Conventional Commit を作る

### S02 — authority inventory verification を追加する
- target:
  - issue-68 向け verification を `tests/test_init_update.py` に追加し、authoritative path / compatibility mirror / duplicate boundary を観測可能にする
- design refs:
  - `要件 / 例外 -> verification mapping`
  - `Temporary coexistence contract`
- step boundary:
  - issue-68 専用テスト追加に閉じる
  - installer behavior expectation の切替はしない

#### B1 — issue-local verification
- purpose:
  - `install_root` authority を downstream cutover前でも検証できるようにする
- files:
  - `tests/test_init_update.py`

##### I1 — Red/Green/Refactor
- slice goal:
  - declared mirror parity と inventory 外 duplicate 不在を確認する

###### Red
- failing test:
  - declared compatibility mirror pair の parity assertion
  - repo-wide duplicate boundary assertion
  - authority inventory に未記載の provider-side duplicate 不在 assertion
- expected failure:
  - mirror parity / duplicate boundary が未検証のため fail

###### Green
- minimum implementation:
  - issue-68 専用テスト群を追加し、declared mirror parity、inventory 外 duplicate 不在、repo-wide verification rule を確認する
  - 既存 `codex_skills` 前提テストは downstream issue のため温存する
- pass condition:
  - issue-68 新規テストが通る
  - 既存関連テストも壊さない

###### Refactor
- 目的:
  - テスト helper や inventory 定義の重複を最小化する
- guardrail:
  - 既存 installer contract テストの意味を変えない

#### step gate
- review:
  - code reviewer に verification scope が issue-68 に閉じているか確認させる
- expected tests:
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_68_declared_legacy_pairs_remain_byte_equivalent`
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_68_authority_inventory_disallows_unlisted_provider_duplicates`
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_bundled_skill_assets_cover_managed_manifest`
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_bundled_native_shim_assets_satisfy_static_delegation_only_contract`
- report update:
  - 新規 verification の対象、duplicate boundary、mirror parity 証跡、review verdict を `report.md` に追記する
- commit:
  - `test(spec): install_root分類検証を追加` 相当の Conventional Commit を作る

### S90 — report / docs impact resolution
- 対象:
  - `report.md`
- 対応:
  - `S01` / `S02` / validation / review / commit 証跡を issue report に集約する
  - requirement/design/plan の追加修正が不要なら no-op とし、その判断を report に記録する

### S99 — final diff review quality gate
- branch diff scope:
  - `iss-00068-install-root-tree-and-asset-classification` branch の全差分
- required validation:
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_68_install_root_tree_exists`
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_68_authoritative_inventory_paths_are_classified_under_install_root`
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_68_workflow_seed_matches_repo_root_ci_workflow`
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_68_declared_legacy_pairs_remain_byte_equivalent`
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_issue_68_authority_inventory_disallows_unlisted_provider_duplicates`
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_bundled_skill_assets_cover_managed_manifest`
  - `python -m unittest tests.test_init_update.TestInitUpdate.test_bundled_native_shim_assets_satisfy_static_delegation_only_contract`
  - `python -m unittest discover -v` が現実的であれば informational sweep として実施する
  - full suite が issue-68 scope 外の既存 failure を返した場合、targeted scope、`validate`、`sync --github` が通っており、report に failing tests と out-of-scope 理由が記録されていれば `final validation pass` を阻害しない
  - `./spec-dock/scripts/spec-dock validate`
  - `find src/spec_dock/assets/install_root -print | rg '[A-Z]' | rg -v '/SKILL\\.md$'` が no match
- workflow closeout evidence:
  - `./spec-dock/scripts/spec-dock sync --github`
  - これは issue acceptance を直接検証するコマンドではなく、`workflow_issue.md` が要求する完了証跡として final closeout で実行する
  - issue-local validations が通っていても、この closeout evidence が失敗した場合は `blocked` または `未完了` として report に理由を残す
- reviewer approvals:
  - final code review `pass`
  - final spec review `pass`
- report update:
  - final diff review verdict、validation summary、spec review verdict、close-ready 判断を `report.md` に残す
- commit expectation:
  - report 更新後に closeout commit expectation を満たす
  - product diff が S01 / S02 の既存 implementation commits で閉じており、S99 が closeout-evidence-only 更新に留まる場合は、追加の product commit を必須にしない
  - report-only closeout commit を作成する場合は、その hash を report に残す

## 未確定事項
- なし:
  - workflow seed は同一 branch / worktree 上の repo root `.github/workflows/ci.yml` を唯一のコピー元 artifact として扱い、`S01` で byte equality を確認する
  - `install_root` 側 `meta.json` の `source_of_truth_asset` は issue-68 では current compatibility を維持する

## final exit contract
- AC/EC 達成:
  - `install_root` tree、in-scope inventory、duplicate boundary、mirror parity が code と tests で確認できる
- docs impact resolved:
  - issue report に required evidence が記録されている
- final diff approved:
  - final code review `pass`
  - final spec review `pass`
  - required validation 完了
