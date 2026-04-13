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
- pending:
  - S02 runtime bundle tests commit

#### メモ
- S02 の薄い bundle tests は詳細回帰の代替ではなく、issue-71 report へ runtime-command-verification evidence を束ねる入口として追加した。

---

## 遭遇した問題と解決 (任意)
- 問題:
  - full-suite に `commands/deps.py` shell layering structural regression が残るが、issue-71 の closure surface と混同される余地があった。
  - 解決:
    - requirement/design/plan で scope-out 条件を限定し、final report に residual risk として記録する運用へ整理した。

## 学んだこと (任意)
- ...
- ...

## 今後の推奨事項 (任意)
- ...
- ...

## checkout-verification (必須)
- suite_or_command:
  - pending_until_execution
- target_surface:
  - pending_until_execution
- result:
  - pending_until_execution

## runtime-command-verification (必須)
- command_family:
  - pending_until_execution
- fixture_or_test:
  - pending_until_execution
- result:
  - pending_until_execution

## installed-package-verification (必須)
- isolated_env_contract:
  - pending_until_execution
- no_fallback_confirmation:
  - pending_until_execution
- result:
  - pending_until_execution

## dogfooding-parity (必須)
- surface:
  - pending_until_execution
- before_after_summary:
  - pending_until_execution
- result:
  - pending_until_execution

## upstream-handoff-consumed (必須)
- issue69_refs:
  - pending_until_execution
- issue70_refs:
  - pending_until_execution
- consumed_subchecks:
  - pending_until_execution
- reverified_in_issue71:
  - pending_until_execution

## 省略/例外メモ (必須)
- 該当なし
