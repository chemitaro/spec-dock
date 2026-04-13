---
種別: 実装報告書（Issue）
ID: "iss-00071"
タイトル: "Verification dogfooding and update parity"
関連GitHub: ["#71"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-04-13"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00071 Verification dogfooding and update parity — 実装報告（LOG）

## 実装サマリー
- 実装準備として requirement / design / plan を現行 issue-69 / issue-70 完了状態に合わせて更新し、spec review を pass した。
- 本 issue は checkout / runtime command / installed package / dogfooding parity の verification evidence を集約して `E-AC-002` / `E-AC-003` を閉じる。

## 実装記録（セッションログ） (必須)

### 2026-04-13 00:00 - 00:00

#### 対象
- Step: prep
- AC/EC: requirement/design/plan readiness

#### 実施内容
- `iss-00070` final sweep で残った `commands/deps.py: domain.ids` forbidden import failure の扱いを requirement / design に明記した。
- `validate` / `sync` / `sync --github`、checked-in dogfooding parity、installed package smoke に影響しない限り、deps command shell layering regression は issue-71 closure blocker ではなく full-suite residual risk として report に記録する契約へ整理した。
- backward compatibility layer / staged migration を追加せず、一括 cutover 後の現行 contract を検証する issue であることを requirement に追記した。
- `E-AC-002` / `E-AC-003`、runtime command surface、installed package surface、scope-out structural failure の closure matrix を design に追加した。
- implementation plan をテンプレートから具体化し、S01 / S02 / S03 / S90 / S99 の step、review gate、commit gate、validation 方針を固定した。

#### 実行コマンド / 結果
```bash
spec_reviewer requirement/design pre-review

review_status: fail
findings:
- P1: commands/deps.py structural regression の scope handling が requirement/design で未定義
- P2: backward compatibility / staged migration 不要方針と closure matrix の明確化が必要
```

```bash
spec_reviewer requirement/design re-review

review_status: pass
findings: []
```

#### 変更したファイル
- `requirement.md` - scope-out structural failure、no staged migration constraint を追加
- `design.md` - failure handling と closure matrix を追加
- `plan.md` - issue-71 execution contract を具体化
- `report.md` - 実装準備 evidence を初期化

#### コミット
- `c076d43` `docs(issue): iss-00071の実装準備を確定`

#### メモ
- plan review は `pass`。plan front matter を `approved` に更新済み。

---

### 2026-04-13 00:00 - 00:00

#### 対象
- Step: S01
- AC/EC: AC-001, AC-002, EC-001

#### 実施内容
- checked-in `.agents/.codex/.github/.github/workflows` と provider-side `install_root` authoritative assets の parity を issue-71 名前空間の test で固定した。
- issue-69 report の `package-parity-evidence` と issue-70 report の `handoff-validation-evidence` が evidence-bearing content を持ち、issue-71 final verification input として消費可能であることを test で確認した。
- production code は変更せず、`tests/test_init_update.py` の verification surface 追加に閉じた。

#### 実行コマンド / 結果
```bash
python -m unittest -v tests.test_init_update.TestInitUpdate.test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets tests.test_init_update.TestInitUpdate.test_issue_71_upstream_handoff_reports_expose_evidence_bearing_sections tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_mirror_docs_match_provider_assets tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_mirror_match_provider_assets tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json

----------------------------------------------------------------------
Ran 5 tests in 0.027s

OK
```

#### 変更したファイル
- `tests/test_init_update.py`
  - issue-71 checked-in agent-tooling parity test を追加
  - issue-69 / issue-70 handoff evidence consumption test を追加
  - markdown heading section extraction helper を test-local に追加

#### レビュー
- code review:
  - verdict:
    - `pass`
  - reviewer:
    - code_reviewer `019d867a-e4b8-7d30-b14f-1fbd8e3441d7`
  - note:
    - P0/P1 findings はなし
    - residual risk として、report wording 依存の phrase/count assertion と heading prefix extraction の軽微な brittleness を記録

#### コミット
- `9a225d2` `test(verification): dogfooding parityとhandoff消費を固定`

#### メモ
- issue-71 の `upstream-handoff-consumed` は issue-69 / issue-70 report の placeholder 不在と `result/pass` presence を confirmation source にしている。

---

### 2026-04-13 00:00 - 00:00

#### 対象
- Step: S02
- AC/EC: AC-003, AC-004, EC-002

#### 実施内容
- `validate` / `sync --no-update-active` / `sync --github --no-update-active` を issue-71 観点で束ねる薄い runtime bundle test を追加した。
- required artifact 欠落時の `validate` / `sync` fail-fast を issue-71 名前空間で固定した。
- `sync --force` degraded path は既存 detailed regression を issue-71 bundle test から再利用する形で closure evidence に接続した。
- production code は変更せず、runtime test files のみを更新した。

#### 実行コマンド / 結果
```bash
python -m unittest -v tests.cli_runtime.test_sync.TestCliSync.test_issue_71_runtime_bundle_validate_sync_and_sync_github_surface tests.cli_runtime.test_validate.TestCliValidate.test_issue_71_runtime_bundle_missing_required_artifact_fail_fast tests.presentation_runtime.test_runtime_sync_s07.TestRuntimeSyncS07.test_issue_71_runtime_bundle_sync_force_degraded_path

----------------------------------------------------------------------
Ran 3 tests in 0.943s

OK
```

#### 変更したファイル
- `tests/cli_runtime/test_sync.py`
  - issue-71 runtime bundle test を追加
- `tests/cli_runtime/test_validate.py`
  - issue-71 missing required artifact fail-fast test を追加
- `tests/presentation_runtime/test_runtime_sync_s07.py`
  - issue-71 sync-force degraded bundle test を追加

#### レビュー
- code review:
  - verdict:
    - `pass`
  - reviewer:
    - code_reviewer `019d8680-99ec-78c1-9555-9d5031a29ae9`
  - note:
    - P0/P1 findings はなし
    - residual risk として、presentation runtime 側 bundle test は既存 test method 直接呼び出しに依存するため、参照先 rename 時の追随修正が必要

#### コミット
- `dab7519` `test(runtime): issue-71のcommand bundleを追加`

#### メモ
- S02 の薄い bundle tests は詳細回帰の代替ではなく、issue-71 report へ runtime-command-verification evidence を束ねる入口として追加した。

---

### 2026-04-13 00:00 - 00:00

#### 対象
- Step: S03
- AC/EC: AC-005

#### 実施内容
- issue-69 / issue-70 の isolated installed package helper を再利用し、issue-71 名前空間の installed package final smoke を追加した。
- non-editable isolated install、no `PYTHONPATH` / no `PYTHONHOME`、repo-root fallback 非使用、`install_root` current managed reflection、obsolete managed prune、custom unmanaged path preservation を 1 本の smoke test で確認した。
- production code は変更せず、`tests/test_init_update.py` のみ更新した。

#### 実行コマンド / 結果
```bash
python -m unittest -v tests.test_init_update.TestInitUpdate.test_issue_71_isolated_wheel_install_final_smoke_closure_surface_without_fallback tests.test_init_update.TestInitUpdate.test_issue_70_isolated_wheel_install_reflects_cutover_contract_without_legacy_fallback tests.test_init_update.TestInitUpdate.test_issue_69_isolated_wheel_install_runs_init_update_without_checkout_fallback

----------------------------------------------------------------------
Ran 3 tests in 9.449s

OK
```

#### 変更したファイル
- `tests/test_init_update.py`
  - issue-71 installed package final smoke test を追加

#### レビュー
- code review:
  - verdict:
    - `pass`
  - reviewer:
    - code_reviewer `019d8685-c916-7702-90b4-a07abcb30d3f`
  - note:
    - P0/P1 findings はなし
    - residual risk として、managed inventory 全件網羅は S01/S02 parity evidence に依存し、issue-69/70 helper 契約変更時の追随が必要

#### コミット
- `7324dd4` `test(installer): issue-71のinstalled smokeを追加`

#### メモ
- S03 は closure matrix 上の installed-package-verification を閉じる代表 smoke であり、detailed package parity は issue-69 / issue-70 handoff evidence を前提にする。

---

### 2026-04-13 00:00 - 00:00

#### 対象
- Step: S90/S99
- AC/EC: AC-001, AC-002, AC-003, AC-004, AC-005, EC-001, EC-002

#### 実施内容
- issue-71 targeted verification suite 6 件を通し、checkout parity / runtime bundle / installed package smoke を一括で再確認した。
- checked-in dogfooding runtime に対して `validate` / `sync` / `sync --github` を手動実行し、runtime command surface が install-shaped layout と矛盾しないことを確認した。
- `uv run python -m spec_dock.cli update .` を実行し、checked-in dogfooding workspace の収束差分を観測した。
- full-suite informational sweep を走らせ、既知の `commands/deps.py: domain.ids` forbidden import failure 1 件のみが残ることを確認した。
- final code review を再実施し、closure evidence / convergence accounting / residual risk handling が issue-71 の境界条件と整合することを確認した。

#### 実行コマンド / 結果
```bash
python -m unittest -v tests.test_init_update.TestInitUpdate.test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets tests.test_init_update.TestInitUpdate.test_issue_71_upstream_handoff_reports_expose_evidence_bearing_sections tests.test_init_update.TestInitUpdate.test_issue_71_isolated_wheel_install_final_smoke_closure_surface_without_fallback tests.cli_runtime.test_sync.TestCliSync.test_issue_71_runtime_bundle_validate_sync_and_sync_github_surface tests.cli_runtime.test_validate.TestCliValidate.test_issue_71_runtime_bundle_missing_required_artifact_fail_fast tests.presentation_runtime.test_runtime_sync_s07.TestRuntimeSyncS07.test_issue_71_runtime_bundle_sync_force_degraded_path

----------------------------------------------------------------------
Ran 6 tests in 4.279s

OK
```

```bash
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync
./spec-dock/scripts/spec-dock sync --github

spec-dock: ok (validate) nodes=29
spec-dock: ok (sync)
spec-dock: ok (sync)
```

```bash
uv run python -m spec_dock.cli update .
git diff --name-status HEAD -- spec-dock/docs

spec-dock: ok (update) -> /srv/mount/spec-dock
D  spec-dock/docs/spec-dock-guide-old.md
D  spec-dock/docs/spec-dock-guide.md
D  spec-dock/docs/sync.md
D  spec-dock/docs/workflow-adr.md
D  spec-dock/docs/workflow-issue.md
```

```bash
python -m unittest discover -v

----------------------------------------------------------------------
Ran 720 tests in 164.914s

FAILED (failures=1)

only failure:
tests.cli_runtime.test_runtime_shell_s11.RuntimeShellS11Tests.test_final_api_call_site_and_structural_regression
-> forbidden import in src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/deps.py: domain.ids
```

#### 変更したファイル
- `requirement.md`
  - scope-out residual risk boundary を明文化
- `design.md`
  - `commands/deps.py` structural regression の扱いを risk / mitigation として固定
- `report.md`
  - final verification evidence、update convergence before/after、residual risk、review gate 記録を追加
- `spec-dock/docs/spec-dock-guide-old.md`
- `spec-dock/docs/spec-dock-guide.md`
- `spec-dock/docs/sync.md`
- `spec-dock/docs/workflow-adr.md`
- `spec-dock/docs/workflow-issue.md`
  - `spec-dock update .` により deprecated / historical alias docs が checked-in dogfooding workspace から prune された

#### レビュー
- final code review:
  - verdict:
    - `pass`
  - reviewer:
    - code_reviewer `019d86a9-5e54-79d2-b40e-ee0120126e89`
  - note:
    - P0/P1 findings はなし
    - issue-71 closure evidence、convergence accounting、residual risk handling は current requirement/design boundary と整合

#### コミット
- pending:
  - final evidence / convergence commit

#### メモ
- final spec review はこの S99 gate で継続中。pass 後に report front matter と final gate verdict を確定する。

---

## 遭遇した問題と解決 (任意)
- 問題:
  - full-suite に `commands/deps.py` shell layering structural regression が残るが、issue-71 の closure surface と混同される余地があった。
  - 解決:
    - requirement/design/plan で scope-out 条件を限定し、final report に residual risk として記録する運用へ整理した。

## 学んだこと (任意)
- closure issue を verification 専用に切り分けることで、production code を増やさずに contract closure と残存リスクの分離を明確にできた。
- installed package / checked-in dogfooding / runtime command の 3 面をそれぞれ独立した evidence として残すと、full-suite 側の非対象 failure が混ざっても close 判定を安定化できる。

## 今後の推奨事項 (任意)
- full-suite を green に揃える次の work item では、`commands/deps.py` の `domain.ids` import を commands/application boundary に戻す structural repair を別 issue で扱うとよい。
- issue 連鎖で handoff evidence を使う場合は、今回のような evidence-bearing section contract を継続し、placeholder を残さない運用を維持すると downstream issue が閉じやすい。

## checkout-verification (必須)
- suite_or_command:
  - `python -m unittest -v tests.test_init_update.TestInitUpdate.test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets tests.test_init_update.TestInitUpdate.test_issue_71_upstream_handoff_reports_expose_evidence_bearing_sections`
- target_surface:
  - checked-in `.agents/`, `.codex/`, `.github/`, `.github/workflows/` と provider-side `src/spec_dock/assets/install_root/` authoritative asset parity
  - issue-69 / issue-70 report の handoff evidence-bearing sections 消費可能性
- result:
  - pass

## runtime-command-verification (必須)
- command_family:
  - `validate`
  - `sync`
  - `sync --github`
  - required artifact 欠落時 fail-fast
  - `sync --force` degraded path
- fixture_or_test:
  - `python -m unittest -v tests.cli_runtime.test_sync.TestCliSync.test_issue_71_runtime_bundle_validate_sync_and_sync_github_surface tests.cli_runtime.test_validate.TestCliValidate.test_issue_71_runtime_bundle_missing_required_artifact_fail_fast tests.presentation_runtime.test_runtime_sync_s07.TestRuntimeSyncS07.test_issue_71_runtime_bundle_sync_force_degraded_path`
  - `./spec-dock/scripts/spec-dock validate`
  - `./spec-dock/scripts/spec-dock sync`
  - `./spec-dock/scripts/spec-dock sync --github`
- result:
  - pass

## installed-package-verification (必須)
- isolated_env_contract:
  - `python -m unittest -v tests.test_init_update.TestInitUpdate.test_issue_71_isolated_wheel_install_final_smoke_closure_surface_without_fallback`
  - non-editable isolated install
  - `PYTHONPATH` / `PYTHONHOME` なし
- no_fallback_confirmation:
  - `sys_path_has_repo_root == False`
  - current sources は `install_root/` 配下のみ
  - `codex_skills/` fallback 不使用
  - current managed reflection / obsolete managed prune / custom unmanaged path preservation を確認
- result:
  - pass

## dogfooding-parity (必須)
- surface:
  - parity-managed surface:
    - checked-in `.agents/`
    - checked-in `.codex/`
    - checked-in `.github/`
    - checked-in `.github/workflows/`
  - fixture surface:
    - checked-in `spec-dock/`
- before_after_summary:
  - before: issue-71 docs 更新後の `git status --short -- .agents .codex .github .github/workflows spec-dock` では issue docs 3 files 以外の tracked drift は観測されなかった
  - command: `uv run python -m spec_dock.cli update .`
  - after: `spec-dock: ok (update) -> /srv/mount/spec-dock`
  - after parity-managed surface: `git diff --name-status HEAD -- .agents .codex .github .github/workflows` は空で、agent-tooling / workflow managed surface に tracked drift は残らなかった
  - after fixture surface: `git diff --name-status HEAD -- spec-dock` では issue docs 3 files 更新に加えて `spec-dock/docs/` の deprecated / historical alias files 5 件の `D` のみが観測された
  - after: `git diff --name-status HEAD -- spec-dock/docs` では次の 5 files の `D` のみが観測され、tracked managed additions は発生しなかった
  - after: checked-in `spec-dock/docs/` の deprecated / historical alias files だけが prune され、current provider-side authoritative assets に存在しない stale managed docs が収束した
  - converged removals:
    - `spec-dock/docs/spec-dock-guide-old.md`
    - `spec-dock/docs/spec-dock-guide.md`
    - `spec-dock/docs/sync.md`
    - `spec-dock/docs/workflow-adr.md`
    - `spec-dock/docs/workflow-issue.md`
- result:
  - pass

## upstream-handoff-consumed (必須)
- issue69_refs:
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00069-package-data-and-installed-artifact-parity/report.md`
  - section: `package-parity-evidence`
- issue70_refs:
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00070-installer-source-discovery-and-managed-ownership/report.md`
  - section: `handoff-validation-evidence`
- consumed_subchecks:
  - issue-69 installed artifact parity evidence
  - issue-69 isolated package smoke evidence
  - issue-70 install_root discovery / managed ownership evidence
  - issue-70 cutover / obsolete cleanup evidence
- reverified_in_issue71:
  - S01 で handoff reports が evidence-bearing sections を持つことを再検証
  - S02 で runtime command surface を current bundle と manual command で再検証
  - S03 で installed package final smoke を isolated wheel install で再検証

## 省略/例外メモ (必須)
- `python -m unittest discover -v` は `Ran 720 tests in 164.914s` のうち 1 件失敗した
- 失敗: `tests.cli_runtime.test_runtime_shell_s11.RuntimeShellS11Tests.test_final_api_call_site_and_structural_regression`
- 原因: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/deps.py` の `domain.ids` forbidden import
- requirement / design / plan の契約どおり、この failure は `validate` / `sync` / `sync --github`、checked-in dogfooding parity、installed package smoke を壊さない限り issue-71 closure blocker ではなく、full-suite residual risk として scope-out する

## 最終検証 (必須)
- targeted issue-71 verification suite:
  - `python -m unittest -v tests.test_init_update.TestInitUpdate.test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets tests.test_init_update.TestInitUpdate.test_issue_71_upstream_handoff_reports_expose_evidence_bearing_sections tests.test_init_update.TestInitUpdate.test_issue_71_isolated_wheel_install_final_smoke_closure_surface_without_fallback tests.cli_runtime.test_sync.TestCliSync.test_issue_71_runtime_bundle_validate_sync_and_sync_github_surface tests.cli_runtime.test_validate.TestCliValidate.test_issue_71_runtime_bundle_missing_required_artifact_fail_fast tests.presentation_runtime.test_runtime_sync_s07.TestRuntimeSyncS07.test_issue_71_runtime_bundle_sync_force_degraded_path`
  - result: `Ran 6 tests in 4.279s` / `OK`
- manual runtime verification:
  - `./spec-dock/scripts/spec-dock validate` -> `spec-dock: ok (validate) nodes=29`
  - `./spec-dock/scripts/spec-dock sync` -> `spec-dock: ok (sync)`
  - `./spec-dock/scripts/spec-dock sync --github` -> `spec-dock: ok (sync)`
- dogfooding update convergence:
  - `uv run python -m spec_dock.cli update .` -> `spec-dock: ok (update) -> /srv/mount/spec-dock`
  - `git diff --name-status HEAD -- .agents .codex .github .github/workflows` -> empty
  - parity-managed surfaces には tracked drift が残らなかった
  - `git diff --name-status HEAD -- spec-dock` -> issue docs 3 files update + `spec-dock/docs` 5 deletions
  - `git diff --name-status HEAD -- spec-dock/docs` -> 5 deletions only
  - stale checked-in deprecated docs only were pruned; no tracked managed drift was introduced outside that convergence set
- full-suite informational sweep:
  - `python -m unittest discover -v`
  - result: `Ran 720 tests in 164.914s` / `FAILED (failures=1)`
  - only failure: `tests.cli_runtime.test_runtime_shell_s11.RuntimeShellS11Tests.test_final_api_call_site_and_structural_regression`
