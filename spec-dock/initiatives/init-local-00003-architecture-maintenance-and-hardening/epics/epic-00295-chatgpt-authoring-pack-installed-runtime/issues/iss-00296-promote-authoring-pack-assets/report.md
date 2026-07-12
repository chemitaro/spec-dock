---
種別: 実装報告書（Issue）
ID: "iss-00296"
タイトル: "Authoring Pack Assets"
関連GitHub: ["#296"]
状態: "in_progress"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00295", "init-local-00003"]
---

# iss-00296 Authoring Pack Assets — 実装報告

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger）

| ID | Status | Type | Raised By | Gap | Options Considered | Decision | Rationale | Disposition | Evidence | Follow-up |
|---|---|---|---|---|---|---|---|---|---|---|
| D-001 | resolved | scope | orchestrator | root `scripts/authoring-pack/` は consumer repository へ配布される provider-side asset ではない | root helper を正式面にする; provider asset へ昇格する | provider asset へ昇格し root は compatibility / dogfood surface として残す | repo guidance は `src/spec_dock/assets/spec_dock/...` を shipped scaffold source of truth としている | applied | `requirement.md`; `design.md`; `plan.md` | 後続 Issue で command group と adapter を実装する |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | partially_adopted | ChatGPT ZIP Issue draft pack delegated_draft | `requirement.md`; `design.md`; `plan.md` | provider-side asset promotion、source-of-truth boundary、scope、verification、relay PR defer 方針を採用した。tests/fixtures path updates、thin-wrapper choice、command implementation claim は後続 Issue の責務として除外した | `artifacts/20260707t171106z-draft-requirement-promote-authoring-pack-assets-draft-requirement.md`; `artifacts/20260707t171234z-draft-design-promote-authoring-pack-assets-draft-design.md`; `artifacts/20260707t171235z-draft-plan-promote-authoring-pack-assets-draft-plan.md` | spec-reviewer pass 後に approved plan を実行する |

## 目的整合台帳（Objective Alignment Ledger）

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | `src/spec_dock/assets/spec_dock/scripts/authoring-pack/` を provider-side source of truth とする要件 | root helper README に compatibility / dogfood surface を残す設計 | low | pass |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | Epic `epic-00295` 正本と Issue draft requirement を照合した | なし | draft requirement を部分採用し正本 requirement へ再記述した | pass | no | promote |
| design | 正本 requirement と Issue draft design と provider asset layout を照合した | なし | draft design を部分採用し正本 design へ再記述した | pass | no | promote |
| plan | 正本 requirement/design と Issue draft plan と `standard` profile を照合した | なし | draft plan を部分採用し実装ステップと検証契約を正本 plan へ再記述した | pass | no | execute approved plan |

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）

| ロール（created_by_role） | 範囲（scope_id） | ドラフトパス（artifact draft path） | 参照元（source_paths） | 予定反映先（intended_targets） | 採用状態（adoption_status） | 反映先（reflected_to） | 差分ガード結果（diff_guard_result） | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果（reviewer result） | 昇格判断（promotion decision） |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ChatGPT ZIP authoring pack | iss-00296 | `artifacts/20260707t171106z-draft-requirement-promote-authoring-pack-assets-draft-requirement.md`; `artifacts/20260707t171234z-draft-design-promote-authoring-pack-assets-draft-design.md`; `artifacts/20260707t171235z-draft-plan-promote-authoring-pack-assets-draft-plan.md` | Epic `epic-00295` final authoring pack | `requirement.md`; `design.md`; `plan.md` | partially_adopted | `requirement.md`; `design.md`; `plan.md` | clean | 部分採用して canonical docs へ再記述した | draft heading、authority self-claim、branch wording、tests/fixtures path updates、thin-wrapper choice、command implementation claim | none | pass | execute approved plan |

## ワークフロー単位の named role 許可

| 許可元（authorization source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可 / host conflict 理由（denied / unavailable / host conflict reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user request to use SpecDock workflow | `/Users/iwasawayuuta/.codex/worktrees/aa9c/spec-dock` | iss-00296 | current session | spec-reviewer | active repo/worktree、active SpecDock scope、current session、SpecDock-defined named roles | issue complete or scope change | none | spec-reviewer gate を実行する |

## グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）

| グレード（Grade） | 必要な専門家 / 代替（required specialist / fallback） | 使用状況（usage） | 証跡（evidence） | 鮮度 spec-reviewer 判定（fresh spec-reviewer verdict） | 実行可否（execution readiness） |
|---|---|---|---|---|---|
| standard | manual fallback | used | manual-authored canonical docs in `requirement.md`; `design.md`; `plan.md` based on delegated draft evidence EAL-001 | pass | ready |

## レビューゲート状態（Reviewer Gate Status）

| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| planning | spec authoring review | spec-reviewer | stale | review pending | no | blocked until pass | 初回レビュー前の待機行。r1 実施後に stale history として保持 |
| planning-r1 | spec authoring review | spec-reviewer | stale | failed | no | blocked | provider README を root dogfood README のコピーとして扱う曖昧さ、init/update 到達性検証不足、未採用 draft claim 記録不足を指摘された |
| planning-r2 | spec authoring review | spec-reviewer | fresh | pass | no | execute approved plan | provider README と root README の責務分離、TC-005、未採用 draft claim 記録を確認し、実装前の blocking ambiguity なし |

## 実装サマリー

Root `scripts/authoring-pack/` の Python helper inventory を provider-side installed asset tree `src/spec_dock/assets/spec_dock/scripts/authoring-pack/` へ配置した。Provider README は installed asset / source-of-truth 文言で新規作成し、root README は compatibility / dogfood developer surface として明記した。`spec-dock/scripts/spec_dock_runtime/.../authoring_pack/` は dogfooding runtime mirror として追加し、provider-side package boundary の consumer-side validation artifact として扱う。

## 実装記録（セッションログ）

### セッションログ（2026-07-08 進行中）

#### 対象
- Step: planning gate
- Closure: pre-implementation readiness

#### 実施内容
- ChatGPT ZIP 由来の Issue draft artifacts を確認し、`requirement.md`、`design.md`、`plan.md` へ部分採用した。
- 中間 Issue では PR delivery を行わず、final quality gate Issue `iss-00307` に defer する計画を維持した。
- spec-reviewer r1 failed findings を受け、provider README は新規 provider-side wording とし、root README は compatibility / dogfood wording とする計画へ修正した。
- `spec-dock init` smoke による consumer delivery verification を TC-005 として追加した。
- 採用しなかった draft claim に tests/fixtures path updates、thin-wrapper choice、command implementation claim を追加した。
- Provider-side `authoring-pack` helper inventory、application/domain `authoring_pack` package boundary、provider README、root README boundary note を実装した。
- Dogfooding runtime mirror に `spec-dock/scripts/spec_dock_runtime/application/authoring_pack/__init__.py` と `spec-dock/scripts/spec_dock_runtime/domain/authoring_pack/__init__.py` を追加した。これは provider boundary の mirror / validation artifact であり、implementation source of truth は provider-side asset tree に置く。
- TC-001 through TC-005 と `git diff --check` を実行し、すべて pass した。

#### 実行コマンド / 結果
```bash
./spec-dock/scripts/spec-dock guidance issue-planning
# blocked: report-evidence-scaffold

./spec-dock/scripts/spec-dock guidance issue-execution
# ready: execute-approved-plan

find src/spec_dock/assets/spec_dock/scripts/authoring-pack -maxdepth 1 -type f | sort
# pass: README.md and 10 Python helper files observed

python -m py_compile src/spec_dock/assets/spec_dock/scripts/authoring-pack/*.py
# pass

rg -n "source of truth|compatibility|provider-side|installed asset" scripts/authoring-pack/README.md src/spec_dock/assets/spec_dock/scripts/authoring-pack/README.md
# pass: root and provider README boundary wording observed

./spec-dock/scripts/spec-dock validate
# pass: spec-dock: ok (validate) nodes=202

uvx --from . spec-dock init /private/tmp/specdock-authoring-pack-init-smoke
# pass: spec-dock: ok (init) -> /private/tmp/specdock-authoring-pack-init-smoke

test -f /private/tmp/specdock-authoring-pack-init-smoke/spec-dock/scripts/authoring-pack/README.md
# pass

find /private/tmp/specdock-authoring-pack-init-smoke/spec-dock/scripts/authoring-pack -maxdepth 1 -type f | sort
# pass: README.md and 10 Python helper files observed in consumer smoke workspace

git diff --check
# pass

uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_subprocess_validate_and_sync_on_cutover_snapshot tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_mirror_match_provider_assets
# pass: 3 passed in 7.54s

uv run pytest tests/unit/infra/test_init_update.py
# pass: 545 passed in 348.35s

uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_init_installs_authoring_pack_helper_inventory
# pass

uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_init_creates_expected_structure tests/unit/infra/test_init_update.py::TestInitUpdate::test_init_installs_authoring_pack_helper_inventory
# pass: 2 passed in 1.68s
```

#### テスト契約の完了証跡（Test Contract Closure）

| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| TC-001 | S02 | yes | inspection | provider directory absent before implementation | `find src/spec_dock/assets/spec_dock/scripts/authoring-pack -maxdepth 1 -type f | sort` | pass | README.md and 10 Python helper files observed |
| TC-002 | S05 | yes | command | provider scripts absent before implementation | `python -m py_compile src/spec_dock/assets/spec_dock/scripts/authoring-pack/*.py` | pass | `__pycache__` generated by compile was removed from source tree |
| TC-003 | S05 | yes | command | validation required after scaffold doc updates | `./spec-dock/scripts/spec-dock validate` | pass | `spec-dock: ok (validate) nodes=202` |
| TC-004 | S04 | yes | inspection | README boundary wording absent before implementation | `rg -n "source of truth|compatibility|provider-side|installed asset" scripts/authoring-pack/README.md src/spec_dock/assets/spec_dock/scripts/authoring-pack/README.md` | pass | root and provider README wording observed |
| TC-005 | S06 | yes | command | consumer delivery unproven before implementation | `uvx --from . spec-dock init /private/tmp/specdock-authoring-pack-init-smoke` and `test -f /private/tmp/specdock-authoring-pack-init-smoke/spec-dock/scripts/authoring-pack/README.md` | pass | init smoke delivered authoring-pack README and helper inventory |
| TC-006 | S05 | yes | command | scaffold snapshot required update after provider asset and dogfooding epic changes | `uv run pytest tests/unit/infra/test_init_update.py` | pass | `545 passed in 348.35s` |
| TC-007 | S06 | yes | command | reviewer requested durable init coverage for authoring-pack delivery | `uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_init_installs_authoring_pack_helper_inventory` | pass | focused test added after QA P2 finding |

## PR delivery defer evidence

| 対象 Issue | final quality gate Issue | dependency edge | no-per-Issue-PR rationale | merge-prepared claim |
|---|---|---|---|---|
| iss-00296 | iss-00307 | iss-00307 depends on iss-00306 and relay chain includes iss-00296 | Epic は複数 Issue をリレー方式で完了し、PR は final quality gate Issue に集約する | none |

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）

| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| README source-of-truth note and dogfooding mirror evidence | yes | orchestrator | `scripts/authoring-pack/README.md`; `src/spec_dock/assets/spec_dock/scripts/authoring-pack/README.md`; `spec-dock/scripts/spec_dock_runtime/application/authoring_pack/__init__.py`; `spec-dock/scripts/spec_dock_runtime/domain/authoring_pack/__init__.py` | pass |

### 最終 QA ゲート（Final QA Gate）

| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer | whole issue obligation coverage | run after implementation | pass with P2 durable init coverage and final spec gate clarity findings addressed locally | pass |

### 最終コードレビューゲート（Final Code Review Gate）

| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer | issue-wide integrated diff | no findings | 0 | pass |

### 最終 spec review ゲート（Final Spec Review Gate）

| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report / implementation diff alignment | no findings after final report ledger correction | 2 | pass |

### 最終 commit（Final Commit）

| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| final local reviewers passed | provider asset inventory, package boundaries, README wording, Issue docs, report evidence, focused init coverage | final quality gate Issue `iss-00307` | ready for commit and issue finish |

## 省略/例外メモ

- 中間 Issue のため PR delivery は実施しない。
