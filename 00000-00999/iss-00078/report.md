---
種別: 実装報告書（Issue）
ID: "iss-00078"
タイトル: "Installer coexistence contract and migration flow"
関連GitHub: ["#78"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-04-15"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00077", "init-local-00003"]
---

# iss-00078 Installer coexistence contract and migration flow — 実装報告（LOG）

## 実装サマリー (任意)
- installer の legacy rename blocker を除去し、legacy `.spec-dock/` と current `spec-dock/` の共存インストールを許可した。
- runtime `doctor` に `legacy_only_workspace` finding と `legacy_cleanup_pending` warning を追加し、manual migration / manual delete を案内する current-only contract を固定した。
- dogfooding mirror、guide、issue-78 regression tests、review evidence を揃え、final reviewer verdict を `pass` まで収束させた。

## 実装記録（セッションログ） (必須)

### 2026-04-15 00:00 - 23:59

#### 対象
- Step: S02, S03, S04, S90, S99
- AC/EC: AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, EC-001, EC-002, EC-003

#### 実施内容
- `src/spec_dock/cli.py` の `_install_spec_dock()` から legacy rename blocker を除去し、`_require_specdock()` を no-rename / manual migration guidance に置き換えた。
- provider runtime に `legacy_only_workspace` finding、`legacy_cleanup_pending` warning、warning text rendering を追加した。
- dogfooding runtime mirror の `contracts.py` / `doctor.py` / `cli_text.py` を provider と同期した。
- `tests/test_init_update.py` に issue-78 installer regressions を追加し、`tests/cli_runtime/test_runtime_doctor_s04.py` / `test_validate.py` / `test_runtime_validate_s02.py` に current-only / no-fallback / cleanup-pending 契約を追加した。
- `src/spec_dock/assets/spec_dock/docs/guide.md` と `spec-dock/docs/guide.md` に `.spec-dock/` 非互換 / rename 禁止 / manual migration guidance を追記した。
- code review / QA review / final spec review を pass まで回し、close evidence を確定した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.test_init_update.TestInitUpdate.test_issue_78_init_allows_install_when_legacy_hidden_workspace_exists \
  tests.test_init_update.TestInitUpdate.test_issue_78_update_reports_manual_migration_guidance_without_rename \
  tests.test_init_update.TestInitUpdate.test_issue_78_update_keeps_legacy_hidden_workspace_untouched_during_coexistence \
  tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_mirror_match_provider_assets \
  tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json -v
python -m unittest tests.cli_runtime.test_runtime_doctor_s04 -v
python -m unittest tests.cli_runtime.test_validate -v
python -m unittest tests.cli_runtime.test_runtime_validate_s02 -v
python -m unittest tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_mirror_docs_match_provider_assets -v
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock doctor

all targeted issue-78 / runtime / mirror tests: PASS
./spec-dock/scripts/spec-dock validate: spec-dock: ok (validate) nodes=33
./spec-dock/scripts/spec-dock doctor: spec-dock: ok (doctor) findings=0

reviews:
- RG1/code review: pass
- QG1/QA review: pass
- SG1/final spec review: pass
```

#### 変更したファイル
- `src/spec_dock/cli.py` - installer coexistence / no-rename guidance
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py` - `legacy_only_workspace` code 追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/doctor.py` - legacy-only / cleanup-pending 診断追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py` - cleanup-pending warning 文言追加
- `spec-dock/scripts/spec_dock_runtime/application/contracts.py` - dogfooding mirror 同期
- `spec-dock/scripts/spec_dock_runtime/application/doctor.py` - dogfooding mirror 同期
- `spec-dock/scripts/spec_dock_runtime/presentation/cli_text.py` - dogfooding mirror 同期
- `src/spec_dock/assets/spec_dock/docs/guide.md` - static migration guidance 追加
- `spec-dock/docs/guide.md` - mirror docs 同期
- `tests/test_init_update.py` - issue-78 installer / mirror snapshot regressions
- `tests/cli_runtime/test_runtime_doctor_s04.py` - issue-78 doctor regressions
- `tests/cli_runtime/test_validate.py` - no-fallback validate regressions
- `tests/cli_runtime/test_runtime_validate_s02.py` - current-only validate seam regression

#### コミット
- 未実施（final review pass 後に実施）

#### メモ
- `tests.test_init_update` 全体は、この issue 差分外の network / venv / 既存 active pathfile 系 failure が残るため full green ではない。
- issue-78 で直接変更した contract と mirror parity に関する targeted validation はすべて pass した。

## 遭遇した問題と解決 (任意)
- 問題: 初回 review で update coexistence regression の不足、dogfooding runtime mirror の未同期、単体実行での import 順序依存が指摘された。
  - 解決: `tests/test_init_update.py` に coexistence update regression を追加し、mirror `contracts.py` / `doctor.py` / `cli_text.py` を provider と同期し、`tests/cli_runtime/test_runtime_validate_s02.py` を `_runtime_modules()` 系の import seam に揃えた。
- 問題: `tests.test_init_update` full run に network / ensurepip / 既存 active pathfile 系の unrelated failure が含まれていた。
  - 解決: issue-78 契約に直接対応する targeted validation を切り出して実施し、review でも non-blocking residual risk として扱った。

## 学んだこと (任意)
- checked-in dogfooding mirror を含む repo では、provider 側の runtime contract 変更だけでは不十分で、mirror parity まで同時に閉じないと review と dogfooding がずれる。
- legacy hidden workspace の移行契約は install permissive / runtime current-only / doctor observability の 3 点をセットで固定すると運用上の誤誘導が減る。

## 今後の推奨事項 (任意)
- `tests.test_init_update` の network / ensurepip / active pathfile 系 failure は別 issue で baseline 安定化すると、今後の full validation gate が扱いやすくなる。

## 省略/例外メモ (必須)
- `tests.test_init_update` full suite の unresolved failures は issue-78 の変更範囲外として今回の close criteria から除外し、targeted validation + reviewer pass を最終 gate とした。
