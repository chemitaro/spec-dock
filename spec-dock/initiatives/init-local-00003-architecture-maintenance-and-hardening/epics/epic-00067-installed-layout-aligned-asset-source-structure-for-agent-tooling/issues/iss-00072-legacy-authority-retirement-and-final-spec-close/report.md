---
種別: 実装報告書（Issue）
ID: "iss-00072"
タイトル: "Legacy authority retirement and final spec close"
関連GitHub: ["#72"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-14"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00072 Legacy authority retirement and final spec close — 実装報告（LOG）

## 実装サマリー
- issue-72 は `install_root` authority 一本化の最終 closeout tranche として、current tests / repo guidance / current closeout docs の residual legacy authority assumptions を retire する。
- prep phase では requirement / design / plan を現 repo 状態に合わせて更新し、spec review pass まで fix した。

## failing-tests analysis (必須)
- full-suite execution:
  - `python -m unittest discover -v`
- analysis source of truth:
  - `discussions/20260414t012350z-research-runtime-shell-structural-regression-analysis.md`
- failing tests:
  - `tests.cli_runtime.test_runtime_shell_s11.RuntimeShellS11Tests.test_final_api_call_site_and_structural_regression`
    - failure:
      - `forbidden import in .../commands/deps.py: domain.ids`
    - observed cause:
      - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/deps.py` が `from ..domain.ids import format_id, parse_id` を行っており、S11 structural regression contract の「commands 層は `domain` / `infra` / `app` を直接 import しない」に違反している
    - options:
      - Option A:
        - S11 test を緩めて `commands/deps.py` の `domain.ids` import を許容する
      - Option B:
        - commands-safe helper へ id normalization を移し、`commands/deps.py` から `domain.ids` 直 import を除去する
      - Option C:
        - mutation request に raw string を渡し、application 層で canonicalization する
    - evaluation:
      - Option A は architecture contract を弱めるため不採用
      - Option C は request/error contract の変更範囲が広く、closeout tranche の修正として過大
      - Option B は振る舞いを保ったまま layering violation を局所除去できるため最適
    - chosen action:
      - Option B を採用し、commands layer 内の safe helper へ寄せる
- known residual handling:
  - 上記 failing test は issue-71 / epic report では scope-out residual として記録されていたが、今回ユーザー指示により full-suite green まで解消対象へ昇格した
- current status:
  - 上記 failing test は commands 層の局所修正後に targeted rerun / deps 周辺 targeted tests / full suite rerun のすべてで pass した

## 実装記録（セッションログ） (必須)

### 2026-04-13 00:00 - 00:00

#### 対象
- Step: prep
- AC/EC: implementation readiness

#### 実施内容
- issue-69/70/71 完了後の repo reality を調査し、production code の authority はすでに `install_root` に切替済みで、主な残課題が `tests/test_init_update.py`、`AGENTS.md`、issue-72 / epic closeout docs であることを確認した。
- issue-72 requirement / design を、当初の「legacy `codex_skills` を historical artifact として残す」前提から、後段の user 方針に合わせて physical tree 削除前提へ契約補正する準備として整理した。
- issue-72 plan をテンプレートから具体化し、S01 = tests/guidance cleanup、S02 = closeout docs reconciliation、S90/S99 = convergence / final gates として固定した。
- epic current report は prep phase では placeholder のままでよいが、S02/S99 で evidence-bearing content に更新する implementation target であることを明文化した。

#### 実行コマンド / 結果
```bash
spec_reviewer issue-72 requirement/design/plan review cycle

review_status: pass
```

#### 変更したファイル
- `requirement.md`
- `design.md`
- `plan.md`
- `report.md`

#### コミット
- `2933f3e` `docs(issue): iss-00072の実装準備を確定`

#### メモ
- issue-72 prep docs は implementation-ready。次の step は S01 current authority assumptions retirement。

---

### 2026-04-13 00:00 - 00:00

#### 対象
- Step: S01
- AC/EC: AC-001, EC-001

#### 実施内容
- `tests/test_init_update.py` の current authority assertions を `install_root` 基準へ整理し、dogfooding mirror map と bundled asset assertions が `codex_skills` を current source/path として扱わないようにした。
- issue-68 / issue-70 / issue-71 由来の historical regression coverage や legacy duplicate / inert artifact 検証は維持し、current authority assertion だけを retire した。
- `AGENTS.md` の provider-side directory map と repo guidance を更新し、`src/spec_dock/assets/install_root/` を current authority、`src/spec_dock/assets/codex_skills/` を historical artifact として明示した。
- scoped search により、`AGENTS.md` の `codex_skills` hit は historical artifact 説明だけになり、`tests/test_init_update.py` の残存 hit も prior-issue coverage / legacy duplicate classification に閉じていることを確認した。

#### 実行コマンド / 結果
```bash
python -m unittest -v \
  tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_mirror_docs_match_provider_assets \
  tests.test_init_update.TestInitUpdate.test_bundled_skill_assets_cover_managed_manifest \
  tests.test_init_update.TestInitUpdate.test_bundled_native_shim_assets_satisfy_static_delegation_only_contract \
  tests.test_init_update.TestInitUpdate.test_bundled_skill_routing_contract

Ran 4 tests ... OK
```

```bash
python -m unittest -v tests.test_init_update.TestInitUpdate.test_issue_68_authority_inventory_disallows_unlisted_provider_duplicates

Ran 1 test ... OK
```

```bash
rg -n "codex_skills" AGENTS.md tests/test_init_update.py tests/test_cli.py tests/cli_runtime tests/domain_runtime tests/presentation_runtime

AGENTS.md: historical artifact explanation only
tests/test_init_update.py: historical regression coverage / legacy duplicate classification only
tests/test_cli.py, tests/cli_runtime, tests/domain_runtime, tests/presentation_runtime: no hits
```

#### 変更したファイル
- `/srv/mount/spec-dock/tests/test_init_update.py`
  - dogfooding mirror map と bundled asset assertions を `install_root` current authority 基準へ更新
- `/srv/mount/spec-dock/AGENTS.md`
  - provider-side directory map / guidance を current authority model に更新

#### コミット
- `68f2a08` `test(authority): issue-72のcurrent authority前提を整理`

#### メモ
- S01 code review:
  - verdict:
    - `pass`
  - reviewer:
    - code_reviewer `019d86fd-0ea2-7021-b0a0-74c83bc3d657`
  - note:
    - P0/P1 findings はなし
    - `requirement.md` の forbidden residual list indentation は P2 として修正した

---

### 2026-04-13 00:00 - 00:00

#### 対象
- Step: S02
- AC/EC: AC-002, AC-003, AC-004, EC-002

#### 実施内容
- template 状態だった epic-00067 current report を evidence-bearing な closeout report へ更新し、`iss-00068` から `iss-00071` の完了状況、E-AC 達成状況、残件、follow-up を current committed state に合わせて整理した。
- issue-70 current report に残っていた final evidence commit pending 記述を、実際の commit `4007144` へ更新した。
- issue-72 closeout chain に必要な current docs として、epic current report と issue-70 current report が placeholder / pending に依存しない状態になったことを確認した。

#### 実行コマンド / 結果
```bash
rg -n "\\.\\.\\.|iss-xxxx|Pass / Fail|pending_until_execution|draft \\| approved|<YOUR_NAME>" \
  spec-dock/active/epic/report.md \
  spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00070-installer-source-discovery-and-managed-ownership/report.md \
  spec-dock/active/issue/report.md

epic current report / issue-70 current report:
- template placeholders は解消済み
issue-72 report:
- final closeout sections は pending_until_execution のまま（意図どおり）
```

#### 変更したファイル
- `/srv/mount/spec-dock/spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/report.md`
  - epic current report を evidence-bearing な closeout report に更新
- `/srv/mount/spec-dock/spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00070-installer-source-discovery-and-managed-ownership/report.md`
  - final evidence commit pending を実 commit へ更新

#### コミット
- `3968323` `docs(closeout): issue-72のcurrent close chainを整備`

#### メモ
- S02 code review:
  - verdict:
    - `pass`
  - reviewer:
    - code_reviewer `019d8712-f1f7-7303-b5a8-9f8981fa1efa`
  - note:
    - P0/P1 findings はなし
    - epic current report と issue-70 current report は current committed state と整合

---

### 2026-04-14 00:00 - 00:00

#### 対象
- Step: S99 re-review loop
- AC/EC: AC-001, AC-002, AC-003, AC-004

#### 実施内容
- fresh spec review で発見された closeout metadata drift に対応し、epic-00067 `requirement.md` / `design.md` / `plan.md` の front matter を `approved` へ揃え、`iss-00068` current docs も `approved` へ更新した。
- `epic-00067` report の進捗記述と `iss-00072` report の `upstream-prerequisites` を同期し、current evidence chain が「未更新の draft を前提に close 済みと見なしている」状態を解消した。
- fresh code review で発見された managed exact file path sync の symlink 境界逸脱リスクに対応し、`src/spec_dock/cli.py` の preflight で symlink 親 / symlink exact file path を fail-closed にした。
- `tests/test_init_update.py` に init/update の symlink parent conflict / symlink exact-file conflict を追加し、managed path sync が symlink 越しに書き込まないことを regression として固定した。
- informational full-suite sweep を開始し、既知 residual として issue-71 / epic report で scope-out 済みの `tests.cli_runtime.test_runtime_shell_s11.RuntimeShellS11Tests.test_final_api_call_site_and_structural_regression` を再現した。epic acceptance blocker ではなく、current review cycle では residual risk の再確認として扱った。

#### 実行コマンド / 結果
```bash
python -m unittest -v \
  tests.test_init_update.TestInitUpdate.test_issue_70_init_rejects_current_managed_directory_conflict_before_writes \
  tests.test_init_update.TestInitUpdate.test_issue_70_init_rejects_current_managed_container_file_conflict_before_writes \
  tests.test_init_update.TestInitUpdate.test_issue_70_init_rejects_current_managed_symlink_parent_conflict_before_writes \
  tests.test_init_update.TestInitUpdate.test_issue_70_init_rejects_current_managed_symlink_exact_file_conflict_before_writes \
  tests.test_init_update.TestInitUpdate.test_issue_70_update_rejects_current_managed_directory_conflict_before_writes \
  tests.test_init_update.TestInitUpdate.test_issue_70_update_rejects_current_managed_symlink_parent_conflict_before_writes \
  tests.test_init_update.TestInitUpdate.test_issue_70_update_rejects_current_managed_symlink_exact_file_conflict_before_writes \
  tests.test_init_update.TestInitUpdate.test_issue_70_update_rejects_obsolete_managed_directory_conflict_before_writes

Ran 8 tests ... OK
```

```bash
./spec-dock/scripts/spec-dock validate
spec-dock: ok (validate) nodes=29
```

```bash
./spec-dock/scripts/spec-dock sync --github
spec-dock: ok (sync)
spec-dock: sync: active unchanged (matched id in branch: iss-00072)
```

```bash
python -m unittest discover -v
informational sweep:
- known residual reproduced:
  - tests.cli_runtime.test_runtime_shell_s11.RuntimeShellS11Tests.test_final_api_call_site_and_structural_regression
- issue-71 / epic report の scope-out 記録と一致
```

#### 変更したファイル
- `/srv/mount/spec-dock/spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/requirement.md`
  - epic current spec state を `approved` へ同期
- `/srv/mount/spec-dock/spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/design.md`
  - epic current spec state を `approved` へ同期
- `/srv/mount/spec-dock/spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/plan.md`
  - epic current spec state を `approved` へ同期
- `/srv/mount/spec-dock/spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/report.md`
  - current progress summary を approved chain に同期
- `/srv/mount/spec-dock/spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00068-install-root-tree-and-asset-classification/requirement.md`
  - issue-68 current spec state を `approved` へ同期
- `/srv/mount/spec-dock/spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00068-install-root-tree-and-asset-classification/design.md`
  - issue-68 current spec state を `approved` へ同期
- `/srv/mount/spec-dock/spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00068-install-root-tree-and-asset-classification/report.md`
  - issue-68 report state を `approved` へ同期
- `/srv/mount/spec-dock/src/spec_dock/cli.py`
  - managed path preflight で symlink container / exact-file conflict を fail-closed
- `/srv/mount/spec-dock/tests/test_init_update.py`
  - symlink parent / exact-file conflict regression tests を追加
- `/srv/mount/spec-dock/spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00072-legacy-authority-retirement-and-final-spec-close/report.md`
  - upstream prerequisite status と final close gate evidence を更新

#### コミット
- 未実施

#### メモ
- fresh spec review:
  - initial verdict:
    - `fail`
  - finding:
    - epic current spec と issue-68 current docs の state drift
  - corrective action:
    - `draft` -> `approved` の同期と prerequisite record 更新
  - final re-review:
    - `pass`
- fresh code review:
  - initial verdict:
    - `fail`
  - finding:
    - managed path sync が symlink parent / exact-file を preflight で拒否しない
  - corrective action:
    - CLI preflight hardening、obsolete managed symlink prune 補正、symlink / guidance regression tests を追加
  - final re-review:
    - `pass`

---

### 2026-04-14 00:00 - 00:00

#### 対象
- Step: S03 PR review remediation follow-up
- AC/EC: AC-001, AC-004

#### 実施内容
- PR #73 の残レビューを精査し、`tomli` 指摘は既存 remediation 済みの stale comment と判断した。
- `src/spec_dock/cli.py` の obsolete exact path cleanup を補正し、`is_dir()` より先に `is_symlink()` を扱うことで symlink -> directory の obsolete managed path も prune できるようにした。
- current managed path 側の exact symlink fail-closed guard は維持し、obsolete exact path のみ prune 許可となるよう preflight / apply の分岐を揃えた。
- `tests/test_init_update.py` に symlink -> directory の obsolete exact path regression test を追加し、参照先 directory を保持したまま symlink だけが削除されることを固定した。
- full suite と fresh code review を再実行し、PR 再監視へ進められる state を確認した。

#### 実行コマンド / 結果
```bash
python -m unittest -v \
  tests.test_init_update.TestInitUpdate.test_issue_70_update_prunes_obsolete_managed_symlink_exact_file_path \
  tests.test_init_update.TestInitUpdate.test_issue_70_update_prunes_obsolete_managed_symlink_to_directory_exact_file_path \
  tests.test_init_update.TestInitUpdate.test_issue_70_update_rejects_obsolete_managed_directory_conflict_before_writes

Ran 3 tests ... OK
```

```bash
python -m unittest -v tests.test_init_update

Ran 151 tests ... OK
```

```bash
python -m unittest discover -v

Ran 727 tests in 139.190s ... OK
```

```bash
./spec-dock/scripts/spec-dock validate
spec-dock: ok (validate) nodes=29
```

#### 変更したファイル
- `/srv/mount/spec-dock/src/spec_dock/cli.py`
  - obsolete exact path cleanup で symlink -> directory を prune できるよう順序を補正
- `/srv/mount/spec-dock/tests/test_init_update.py`
  - obsolete managed symlink -> directory regression test を追加

#### コミット
- `78b60a6` `fix(cli): obsolete symlink dir の prune 回帰を修正`

#### メモ
- fresh code review:
  - verdict:
    - `pass`
  - reviewer:
    - code_reviewer `019d8aae-7f2d-7d11-8268-95f075f598dc`
  - note:
    - current managed path の symlink guard 維持と obsolete exact symlink prune の両立を確認

---

## 遭遇した問題と解決 (任意)
- 問題:
  - issue-72 prep docs で epic current report と CLI/runtime test targeting の契約が揺れやすかった。
  - 解決:
    - epic current report を current evidence corpus と final gate に明示的に組み込み、CLI/runtime tests は scoped search hit 時のみ targeted 実行する条件付きルールに統一した。

## 学んだこと (任意)
- closeout issue では、実装コードよりも current docs / tests / evidence chain の契約整合が先に崩れやすい。
- epic current report のような上位 closeout artifact は、prep phase と final close phase の期待値を分けて明示すると review が安定する。

## 今後の推奨事項 (任意)
- issue-72 実装では、historical artifact の physical existence と current authority assertion の禁止を混同しないこと。

### 2026-04-14 00:00 - 00:00

#### 対象
- Step: S03
- AC/EC: AC-001, AC-004

#### 実施内容
- PR review analyses A-D に基づく remediation を実装した。
- `tests/presentation_runtime/test_runtime_sync_s07.py` では、test-to-test call を private helper へ抽出し、public test 名と issue traceability を維持したまま `A` を解消した。
- `src/spec_dock/assets/install_root/.github/workflows/ci.yml` では、provider repo 固有の `pip install .` / `tests/test_cli.py` 前提を除去し、managed repo 一般で自己完結する runtime command ベースの local validation へ置換した。さらに code review で指摘された execute-bit 依存も外し、`python3 ./spec-dock/scripts/spec-dock ...` 形式へ修正した。
- dogfooding mirror `.github/workflows/ci.yml` を provider source と同期し、byte parity を維持した。
- provider repo 側の CI coverage regression を避けるため、shipped workflow と分離した root-only workflow `.github/workflows/provider-ci.yml` を追加した。
- `src/spec_dock/cli.py` では `_ManagedSkillInstallPlan` から apply path で未使用の field を除去し、builder 内 local validation data と plan shape を分離して `C` を解消した。
- `tests/test_init_update.py` と wheelhouse fixtures では、issue-69 hermetic backend contract に `tomli==2.2.1` と `tomli-2.2.1-py3-none-any.whl` を追加し、Python 3.10 fresh venv + `--no-index` backend install を成立させて `D` を解消した。
- review analysis discussion filename は命名規約に従う `*-research-*` 形式へ正規化し、`spec-dock validate` が通る状態へ収束させた。

#### 実行コマンド / 結果
```bash
python -m unittest -v \
  tests.presentation_runtime.test_runtime_sync_s07.TestRuntimeSyncS07.test_sync_force_placeholder_and_deps_error_regression \
  tests.presentation_runtime.test_runtime_sync_s07.TestRuntimeSyncS07.test_issue_71_runtime_bundle_sync_force_degraded_path

Ran 2 tests ... OK
```

```bash
python -m unittest -v \
  tests.test_init_update.TestInitUpdate.test_issue_68_workflow_seed_matches_repo_root_ci_workflow \
  tests.test_init_update.TestInitUpdate.test_issue_68_provider_only_workflow_is_not_shipped_via_install_root \
  tests.test_init_update.TestInitUpdate.test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets \
  tests.test_init_update.TestInitUpdate.test_issue_68_authoritative_inventory_paths_are_classified_under_install_root \
  tests.test_init_update.TestInitUpdate.test_issue_68_authority_inventory_disallows_unlisted_provider_duplicates \
  tests.test_init_update.TestInitUpdate.test_issue_70_build_plan_uses_install_root_recursive_inventory_including_workflow \
  tests.test_init_update.TestInitUpdate.test_issue_70_update_syncs_workflow_and_prunes_obsolete_exact_workflow_only \
  tests.test_init_update.TestInitUpdate.test_issue_69_isolated_wheel_install_runs_init_update_without_checkout_fallback

Ran 8 tests ... OK
```

```bash
uv venv --python 3.10 --seed <tmp>/py310
<tmp>/py310/bin/python -m pip install --no-index --no-cache-dir --find-links tests/fixtures/wheelhouse \
  build==1.2.2 packaging==24.2 pyproject_hooks==1.2.0 setuptools==75.8.0 tomli==2.2.1 wheel==0.45.1

Python 3.10 fresh venv + --no-index backend install: OK
```

```bash
python -m unittest discover -v
Ran 726 tests in 138.572s
OK
```

```bash
./spec-dock/scripts/spec-dock validate
spec-dock: ok (validate) nodes=29
```

#### 変更したファイル
- `/srv/mount/spec-dock/tests/presentation_runtime/test_runtime_sync_s07.py`
- `/srv/mount/spec-dock/src/spec_dock/assets/install_root/.github/workflows/ci.yml`
- `/srv/mount/spec-dock/.github/workflows/ci.yml`
- `/srv/mount/spec-dock/.github/workflows/provider-ci.yml`
- `/srv/mount/spec-dock/src/spec_dock/cli.py`
- `/srv/mount/spec-dock/tests/test_init_update.py`
- `/srv/mount/spec-dock/tests/fixtures/wheelhouse/tomli-2.2.1-py3-none-any.whl`
- `/srv/mount/spec-dock/spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00072-legacy-authority-retirement-and-final-spec-close/design.md`
- `/srv/mount/spec-dock/spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00072-legacy-authority-retirement-and-final-spec-close/discussions/*`

#### コミット
- docs commit:
  - `76bd2853e3772bc89ff57f61578498673d07d7d1`
  - `docs(issue-72): review 指摘を仕様書へ反映`
- implementation commit:
  - 未実施

#### メモ
- S03 code review:
  - initial verdict:
    - `fail`
  - corrective action:
    - managed workflow を `python3` invocation へ変更
    - provider-only workflow を root `.github/workflows/provider-ci.yml` として追加
  - fresh verdict:
    - `pass`
- fresh spec review:
  - verdict:
    - `pass`
  - note:
    - S03 sequencing と residual scope-gate の blocking 指摘解消後、実装可能な spec として承認された

## authority-uniqueness (必須)
- provider_authority_artifacts:
  - `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json` を provider-side authoritative manifest として確認した。
  - `src/spec_dock/assets/codex_skills/` は current repo から削除済みであり、provider-side authority を表す checked-in asset tree は `install_root` だけになっていることを確認した。
- retired_legacy_surfaces:
  - `AGENTS.md` は `install_root` を single current authority として記述し、`codex_skills` は retired / removed legacy tree としてだけ説明している。
  - `tests/test_init_update.py` の current authority assertions は `install_root` 基準へ揃っており、残存する `codex_skills` hit は legacy tree 退役確認テスト、synthetic duplicate 注入、legacy fallback 非使用の否定 assertions に限定される。
  - `tests/test_cli.py`、`tests/cli_runtime`、`tests/domain_runtime`、`tests/presentation_runtime` に current authority assertion としての `codex_skills` hit はない。
- dogfooding_convergence_evidence:
  - `uv run python -m spec_dock.cli update .` -> `spec-dock: ok (update) -> /srv/mount/spec-dock`
  - `./spec-dock/scripts/spec-dock validate` -> `spec-dock: ok (validate) nodes=29`
  - `./spec-dock/scripts/spec-dock sync --github` -> `spec-dock: ok (sync)` / active unchanged
  - `git status --short` は空で、issue-72 closeout evidence 取得後の dogfooding mirror / tracked files に drift が残っていない。
- result:
  - `install_root` が唯一の current authority であり、legacy `codex_skills` physical tree は repo から削除済み、残存するのは historical records と negative/synthetic test context だけであることを issue-72 current surfaces で再確認した。

## historical-boundary (必須)
- current_docs_corpus:
  - current docs corpus は issue-72 requirement/design/plan/report、epic-00067 requirement/design/plan/report、`AGENTS.md`、provider-side/dogfooding-side current docs の契約に従って確認した。
  - issue-72 S02 で epic current report を template から evidence-bearing closeout report へ更新し、issue-70 current report の pending commit 記述も解消した。
- out_of_scope_historical_records:
  - `spec-dock/initiatives/init-local-00002-*` 配下の closed issue/discussion、issue-68/69 requirement 上の historical `codex_skills` 文脈は historical record として scope 外に据え置いた。
  - current surface search で検出される historical mention は、authority source-of-truth ではなく legacy reference と明示された説明に限定される。
- result:
  - current docs だけを authority-close 対象に絞り、historical records は rewrite せず boundary を明示する closeout contract が維持されている。

## future-host-extension (必須)
- current_model_statement:
  - current host model は `.agents` shared + sibling host roots であり、現行実装では `.codex/` と `.github/` を `src/spec_dock/assets/install_root/` 配下に並置して管理する。
  - host adapter manifest (`install_root/.agents/host-adapters/meta.json`) もこの sibling-root model を前提に current source_of_truth_asset を指している。
- claude_code_scope_statement:
  - Claude Code は本 issue / epic では未導入で out-of-scope のままとする。
  - ただし future host extension point は legacy root 再利用ではなく、`.agents` shared surface を保ったまま新しい sibling host root を `install_root` 配下へ追加する設計として固定済みである。
- result:
  - `E-RQ-008` / `E-AC-005` に対して、現行 host model と将来拡張の境界が current docs と manifest evidence の両方で説明可能になった。

## upstream-prerequisites (必須)
- epic_requirement_refs:
  - `../requirement.md`
  - 特に `E-RQ-006`、`E-RQ-008`、`E-AC-004`、`E-AC-005`、`E-AC-007`
- epic_design_refs:
  - `../design.md`
  - 特に `Directory contract`、`Installer contract`、`Packaging contract`、`Legacy authority retirement`、`Flow-D future host extension`
- epic_plan_refs:
  - `../plan.md`
  - issue-68 から issue-72 の sequencing と epic close gate
- epic_report_refs:
  - `../report.md`
  - issue-72 S02/S99 により current evidence sink / final closeout report として整備
- epic_report_status:
  - `approved`
- issue68_refs:
  - `../issues/iss-00068-install-root-tree-and-asset-classification/{requirement.md,design.md,report.md}`
- issue68_evidence_status:
  - `approved`
- issue69_refs:
  - `../issues/iss-00069-package-data-and-installed-artifact-parity/{requirement.md,design.md,report.md}`
- issue69_evidence_status:
  - `approved`
- issue70_refs:
  - `../issues/iss-00070-installer-source-discovery-and-managed-ownership/{requirement.md,design.md,report.md}`
- issue70_evidence_status:
  - `approved`
  - issue-72 S02 で final evidence commit `4007144` まで current report に反映済み
- issue71_refs:
  - `../issues/iss-00071-verification-dogfooding-and-update-parity/{requirement.md,design.md,report.md}`
- issue71_evidence_status:
  - `approved`
  - full-suite residual 1 件は issue-71 report で scope-out 済み
- issue72_requirement_refs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
- issue72_design_refs:
  - `design.md` の `既存実装 / 規約の理解`、`legacy reference verification contract`、`Closeout evidence model`
- contradiction_summary:
  - issue-70 までに authority cutover は完了していた一方、current tests / AGENTS / closeout docs に residual legacy authority assumption が残っていた。
  - issue-72 S01 で current authority assertion を整理し、S02 で current closeout docs を evidence-bearing に更新し、S90/S99 で fresh convergence evidence と final reviews を接続する。
- result:
  - issue-68 から issue-71 までの upstream evidence chain は issue-72 closeout report から再現可能に参照できる。

## final-close-gate (必須)
- gate_checks:
  - targeted current-authority tests:
    - `python -m unittest -v tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_mirror_docs_match_provider_assets tests.test_init_update.TestInitUpdate.test_bundled_skill_assets_cover_managed_manifest tests.test_init_update.TestInitUpdate.test_bundled_native_shim_assets_satisfy_static_delegation_only_contract tests.test_init_update.TestInitUpdate.test_bundled_skill_routing_contract tests.test_init_update.TestInitUpdate.test_issue_68_authority_inventory_disallows_unlisted_provider_duplicates`
    - `Ran 5 tests in 0.048s` / `OK`
- targeted symlink-safety regression tests:
    - `python -m unittest -v tests.test_init_update.TestInitUpdate.test_issue_70_init_rejects_current_managed_directory_conflict_before_writes tests.test_init_update.TestInitUpdate.test_issue_70_init_rejects_current_managed_container_file_conflict_before_writes tests.test_init_update.TestInitUpdate.test_issue_70_init_rejects_current_managed_symlink_parent_conflict_before_writes tests.test_init_update.TestInitUpdate.test_issue_70_init_rejects_current_managed_symlink_exact_file_conflict_before_writes tests.test_init_update.TestInitUpdate.test_issue_70_update_rejects_current_managed_directory_conflict_before_writes tests.test_init_update.TestInitUpdate.test_issue_70_update_rejects_current_managed_symlink_parent_conflict_before_writes tests.test_init_update.TestInitUpdate.test_issue_70_update_rejects_current_managed_symlink_exact_file_conflict_before_writes tests.test_init_update.TestInitUpdate.test_issue_70_update_rejects_obsolete_managed_directory_conflict_before_writes`
    - `Ran 8 tests ... OK`
  - targeted obsolete-symlink / guidance regression tests:
    - `python -m unittest -v tests.test_init_update.TestInitUpdate.test_issue_70_update_prunes_obsolete_managed_symlink_exact_file_path tests.test_init_update.TestInitUpdate.test_issue_70_update_rejects_current_managed_symlink_exact_file_conflict_before_writes tests.test_init_update.TestInitUpdate.test_issue_70_update_rejects_obsolete_managed_directory_conflict_before_writes tests.test_init_update.TestInitUpdate.test_current_guidance_documents_match_discussion_numbering_contract`
    - `Ran 4 tests ... OK`
  - current-surface scoped search:
    - `rg -n "codex_skills" AGENTS.md tests/test_init_update.py tests/test_cli.py tests/cli_runtime tests/domain_runtime tests/presentation_runtime`
    - classification は authority-uniqueness 節のとおり
  - provider-side manifest review:
    - `install_root/.agents/host-adapters/meta.json` を authoritative manifest として確認
    - `src/spec_dock/assets/codex_skills/` deleted confirmation を current inventory search と file tree listing で確認
  - dogfooding convergence:
    - `uv run python -m spec_dock.cli update .` -> `ok`
    - `./spec-dock/scripts/spec-dock validate` -> `ok`
    - `./spec-dock/scripts/spec-dock sync --github` -> `ok`
  - final reviews:
    - prior final code review cycle:
      - initial review: `fail`
      - finding: unresolved `pending_until_review` placeholders and premature epic approval while issue report was still `draft`
      - corrective action: S99 report update resolved the final gate placeholders and aligned issue report status with the epic closeout verdict
      - second review: `fail`
      - finding: managed path sync did not reject symlink parent / exact-file conflicts before writes
      - corrective action: preflight hardening in `src/spec_dock/cli.py`、obsolete managed symlink prune 補正、guidance authority path cleanup、symlink / guidance regression testsを反映
      - prior re-review: `pass`
    - fresh final reviews after full-suite repair:
      - code review:
        - `pass`
        - note:
          - `deps.py` は commands-safe helper `node_id_normalizer.py` を参照し、duplicate normalization logic は除去済み
      - spec review:
        - `pass`
        - note:
          - review gate の循環解消、metadata drift 解消、analysis report 正本化の整合を確認済み
  - informational full-suite sweep:
    - `python -m unittest discover -v`
    - known residual reproduced:
      - `tests.cli_runtime.test_runtime_shell_s11.RuntimeShellS11Tests.test_final_api_call_site_and_structural_regression`
    - issue-71 / epic report の scope-out 記録と一致し、epic acceptance blocker ではないことを再確認した
  - full-suite repair rerun:
    - `python -m unittest -v tests.cli_runtime.test_runtime_shell_s11.RuntimeShellS11Tests.test_final_api_call_site_and_structural_regression`
    - `Ran 1 test in 0.161s` / `OK`
    - `python -m unittest -v tests.cli_runtime.test_deps tests.cli_runtime.test_runtime_deps_s04`
    - `Ran 106 tests in 32.476s` / `OK`
    - `python -m unittest discover -v`
    - `Ran 726 tests in 138.572s` / `OK`
    - `./spec-dock/scripts/spec-dock validate`
    - `spec-dock: ok (validate) nodes=29`
  - PR review remediation follow-up:
    - `python -m unittest -v tests.test_init_update.TestInitUpdate.test_issue_70_update_prunes_obsolete_managed_symlink_exact_file_path tests.test_init_update.TestInitUpdate.test_issue_70_update_prunes_obsolete_managed_symlink_to_directory_exact_file_path tests.test_init_update.TestInitUpdate.test_issue_70_update_rejects_obsolete_managed_directory_conflict_before_writes`
    - `Ran 3 tests ... OK`
    - `python -m unittest -v tests.test_init_update`
    - `Ran 151 tests ... OK`
    - `python -m unittest discover -v`
    - `Ran 727 tests in 139.190s` / `OK`
    - `./spec-dock/scripts/spec-dock validate`
    - `spec-dock: ok (validate) nodes=29`
- result:
  - final close gate evidence は current metadata drift 修正、current / obsolete managed symlink safety fix、obsolete symlink-to-directory prune 補正、guidance authority cleanup、full-suite residual repair、full suite green 確認、fresh final code review / spec review pass まで更新済みであり、issue-72 は close-ready である。

## post-review-audit (任意)
- spec_review_reference:
  - issue-72 prep review pass recorded in prep session
- final_code_review_reference:
  - initial final code review identified unresolved closeout placeholders and issue/epic status mismatch.
  - S99 corrective revision resolved the closeout placeholder / state drift finding.
  - follow-up fresh code review identified symlink preflight gap and required CLI/test fix.
  - prior focused code review pass confirmed current/obsolete symlink handlingと guidance authority test が current contract と整合している。
  - fresh final code review after full-suite repair passed after duplicate normalization removal and helper unification.
  - PR review remediation follow-up code review passed after obsolete symlink-to-directory prune regression fix.
- final_spec_review_reference:
  - prep / prior closeout cycles の spec review pass に加え、full-suite repair と独立 analysis report 追加後の fresh final spec review も pass.

## 省略/例外メモ (必須)
- 該当なし
