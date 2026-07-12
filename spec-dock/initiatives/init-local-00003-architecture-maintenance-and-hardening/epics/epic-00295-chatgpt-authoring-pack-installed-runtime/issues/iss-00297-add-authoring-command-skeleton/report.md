---
種別: 実装報告書（Issue）
ID: "iss-00297"
タイトル: "Authoring Command Skeleton"
関連GitHub: ["#297"]
状態: "in_progress"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00295", "init-local-00003"]
---

# iss-00297 Authoring Command Skeleton — 実装報告

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger）

| ID | Status | Type | Raised By | Gap | Options Considered | Decision | Rationale | Disposition | Evidence | Follow-up |
|---|---|---|---|---|---|---|---|---|---|---|
| D-001 | resolved | scope | orchestrator | command group skeleton が後続 Issue の実質ロジックへ拡大しやすい | skeleton only; implement preflight/pack/backend now | skeleton only とし deferred commands は fail-closed にする | Epic plan は C02 を command group skeleton、C03 以降を実質ロジックとして分けている | applied | `requirement.md`; `design.md`; `plan.md` | 後続 Issue で各 deferred command を実装する |
| D-002 | resolved | planning-review | spec-reviewer | 初回 plan は `phase_plan_issue.md` が求める Spec-Locked Closure Index、step-local obligation、全 deferred mapping 検証が不足していた | minimal step table only; executable Issue plan contract | executable Issue plan contract へ拡張する | skeleton scope 自体は妥当だが、実装者と reviewer が全 command mapping / authority boundary を追跡できる必要がある | applied | `plan.md` | spec-reviewer re-review を実施する |
| D-003 | resolved | planning-review | spec-reviewer | 修正後 plan の forbidden authority coverage が `.assurance.json` と authorized profile / `set-authorized-profile` claim を含んでいなかった | ready-style claims only; all requirement-listed authority claims | all requirement-listed authority claims を forbidden phrase coverage に含める | deferred command は evidence-only skeleton であり、assurance / profile authority の自称も禁止する必要がある | applied | `plan.md` | spec-reviewer re-review を実施する |
| D-004 | resolved | final-review | spec-reviewer / code-reviewer | `authoring --help` が leaf command surface まで表示せず、中間 group help が実装済みのように読めた | nested help only; top-level epilog with all leaf commands | top-level help に deferred skeleton command 一覧を追加し、中間 group help を deferred skeleton wording にする | `authoring --help` が skeleton surface と deferred boundary を一箇所で確認できる必要がある | applied | `src/.../cli/parser.py`; `spec-dock/scripts/.../cli/parser.py`; `tests/cli_runtime/test_authoring.py` | reviewer re-review を実施する |
| D-005 | resolved | final-review | spec-reviewer | forbidden authority claim test が `success` / adoption claim を十分に固定していなかった | literal `adoption`; claim-oriented phrases | `success`、`adoption_status`、`adopted` を forbidden phrase coverage に追加する | `issue-draft-adoption` command 名自体は合法なので、adoption claim を表す語に絞って検査する | applied | `tests/cli_runtime/test_authoring.py` | reviewer re-review を実施する |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | partially_adopted | ChatGPT ZIP Issue draft pack delegated_draft | `requirement.md`; `design.md`; `plan.md` | command group skeleton、parser / registry registration、deferred command boundary、CommandOutcome compatibility、status taxonomy、PR defer 方針を採用した | `artifacts/20260707t171238z-draft-requirement-add-authoring-command-skeleton-draft-requirement.md`; `artifacts/20260707t171239z-draft-design-add-authoring-command-skeleton-draft-design.md`; `artifacts/20260707t171239z-01-draft-plan-add-authoring-command-skeleton-draft-plan.md` | spec-reviewer pass 後に approved plan を実行する |

## 目的整合台帳（Objective Alignment Ledger）

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | `authoring` command group skeleton を runtime parser / registry に追加する要件 | deferred command fail-closed と PR delivery defer | low | review pending |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | Epic `epic-00295` 正本、Issue draft requirement、既存 runtime parser surface を照合した | なし | draft requirement を部分採用し正本 requirement へ再記述した | pass | no | promote |
| design | 正本 requirement、Issue draft design、既存 `CommandSpec` / parser / registry pattern を照合した | なし | draft design を部分採用し正本 design へ再記述した | pass | no | promote |
| plan | 正本 requirement/design、Issue draft plan、`standard` profile を照合した | なし | draft plan を部分採用し、Spec-Locked Closure Index、step-local contracts、全 deferred mapping / forbidden authority coverage を持つ正本 plan へ再記述した | pass | no | execute approved plan |

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）

| ロール（created_by_role） | 範囲（scope_id） | ドラフトパス（artifact draft path） | 参照元（source_paths） | 予定反映先（intended_targets） | 採用状態（adoption_status） | 反映先（reflected_to） | 差分ガード結果（diff_guard_result） | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果（reviewer result） | 昇格判断（promotion decision） |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ChatGPT ZIP authoring pack | iss-00297 | `artifacts/20260707t171238z-draft-requirement-add-authoring-command-skeleton-draft-requirement.md`; `artifacts/20260707t171239z-draft-design-add-authoring-command-skeleton-draft-design.md`; `artifacts/20260707t171239z-01-draft-plan-add-authoring-command-skeleton-draft-plan.md` | Epic `epic-00295` final authoring pack | `requirement.md`; `design.md`; `plan.md` | partially_adopted | `requirement.md`; `design.md`; `plan.md` | clean | 部分採用して canonical docs へ再記述した | branch wording、authority self-claim、後続 Issue の実質ロジック | none | pass | execute approved plan |

## ワークフロー単位の named role 許可

| 許可元（authorization source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可 / host conflict 理由（denied / unavailable / host conflict reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user request to use SpecDock workflow | `/Users/iwasawayuuta/.codex/worktrees/aa9c/spec-dock` | iss-00297 | current session | spec-reviewer | active repo/worktree、active SpecDock scope、current session、SpecDock-defined named roles | issue complete or scope change | none | spec-reviewer gate を実行する |

## グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）

| グレード（Grade） | 必要な専門家 / 代替（required specialist / fallback） | 使用状況（usage） | 証跡（evidence） | 鮮度 spec-reviewer 判定（fresh spec-reviewer verdict） | 実行可否（execution readiness） |
|---|---|---|---|---|---|
| standard | manual fallback | used | manual-authored canonical docs in `requirement.md`; `design.md`; `plan.md` based on delegated draft evidence EAL-001 | pass | ready |

## レビューゲート状態（Reviewer Gate Status）

| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| planning-final | spec authoring review | spec-reviewer | fresh | pass | no | execute approved plan | 3回目 spec-reviewer は findings なし。実行可能 Issue plan、全 deferred mapping、authority boundary coverage、PR defer policy を確認済み。初回/2回目 fail と修正内容は Decision Ledger D-002/D-003 に記録済み。 |

## 実装サマリー

`authoring` command group skeleton を provider-side runtime と dogfooding mirror に追加した。全 leaf command は実質ロジックを持たず、`status=deferred` / `authority=evidence_only` / `next_issue=<issue-id>` を返して fail-closed する。

## 実装記録（セッションログ）

### セッションログ（2026-07-08 進行中）

#### 対象
- Step: planning gate
- Closure: pre-implementation readiness

#### 実施内容
- ChatGPT ZIP 由来の Issue draft artifacts を確認し、`requirement.md`、`design.md`、`plan.md` へ部分採用した。
- 中間 Issue では PR delivery を行わず、final quality gate Issue `iss-00307` に defer する計画を維持した。
- 初回 spec-reviewer の P1 指摘を受け、`plan.md` に `Spec-Locked Closure Index`、step-local `delegation contract`、step-local `具体テストケース一覧`、全 deferred command mapping table、S90/S99/Final Exit Contract を追加した。
- 2回目 spec-reviewer の P1 指摘を受け、forbidden authority coverage に canonical docs、`.assurance.json`、authorized profile / `set-authorized-profile`、reviewer pass、execution-ready、PR-ready、merge-ready を含めた。
- 3回目 spec-reviewer で planning gate が pass したため、approved plan を実行した。
- provider-side `commands/authoring.py` を追加し、全 deferred command mapping と shared deferred outcome helper を実装した。
- provider-side `cli/parser.py` / `cli/registry.py` に `authoring` group を登録した。
- dogfooding mirror の `spec-dock/scripts/spec_dock_runtime/` を provider-side 変更へ同期した。
- `tests/cli_runtime/test_authoring.py` を追加し、help と全 deferred command の diagnostics / forbidden authority claim absence を検証した。
- code-reviewer P2 と final spec-reviewer P1/P2 を受け、`authoring --help` に leaf command 一覧を追加し、help wording を deferred skeleton に統一した。
- forbidden authority claim coverage に `success`、`adoption_status`、`adopted` を追加した。

#### 実行コマンド / 結果
```bash
./spec-dock/scripts/spec-dock guidance issue-planning
# blocked: requirement-scaffold

spec-reviewer planning review
# failed: P1 missing executable Issue plan contract and full deferred mapping diagnostics

spec-reviewer planning re-review
# failed: P1 missing .assurance.json and authorized profile / set-authorized-profile forbidden authority claim coverage

spec-reviewer planning re-review 2
# pass: findings none; executable plan, all deferred mapping, forbidden authority coverage, and PR defer policy verified

./spec-dock/scripts/spec-dock authoring --help
# pass: help exits 0 and lists preflight/pack/backend/validate/approval

./spec-dock/scripts/spec-dock authoring preflight github-sync
# expected exit 1; output includes status=deferred, authority=evidence_only, next_issue=iss-00298

./spec-dock/scripts/spec-dock authoring pack prepare
# expected exit 1; output includes status=deferred, authority=evidence_only, next_issue=iss-00299

./spec-dock/scripts/spec-dock authoring validate issue-draft-adoption
# expected exit 1; output includes status=deferred, authority=evidence_only, next_issue=iss-00303

uv run pytest tests/cli_runtime/test_authoring.py
# 11 passed in 3.27s

uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_mirror_match_provider_assets
# 1 passed in 0.07s

uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_init_installs_authoring_pack_helper_inventory
# 1 passed in 0.11s

python -m py_compile src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/authoring.py src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py spec-dock/scripts/spec_dock_runtime/commands/authoring.py spec-dock/scripts/spec_dock_runtime/cli/parser.py spec-dock/scripts/spec_dock_runtime/cli/registry.py
# pass

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=202

git diff --check
# pass

uv run pytest tests/cli_runtime
# 741 passed, 74 skipped in 591.36s

final code-reviewer
# pass with P2 help wording finding; fixed in D-004

qa-reviewer
# pass with no findings

final spec-reviewer
# failed: P1 missing leaf commands in authoring --help, P2 missing success/adoption claim coverage; fixed in D-004/D-005

./spec-dock/scripts/spec-dock authoring --help
# pass: help exits 0 and lists every deferred leaf command

uv run pytest tests/cli_runtime/test_authoring.py
# 11 passed in 3.13s after D-004/D-005

uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_mirror_match_provider_assets
# 1 passed in 0.07s after D-004/D-005
```

#### テスト契約の完了証跡（Test Contract Closure）

| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| TC-001 | S03 | yes | command | pending | `./spec-dock/scripts/spec-dock authoring --help` | pass | help exits 0 and lists all command groups plus every deferred leaf command |
| TC-002 | S04 | yes | command | pending | `./spec-dock/scripts/spec-dock authoring preflight github-sync` | pass | expected exit 1; deferred diagnostics include `next_issue=iss-00298` |
| TC-003 | S04 | yes | command | pending | `./spec-dock/scripts/spec-dock authoring pack prepare` | pass | expected exit 1; deferred diagnostics include `next_issue=iss-00299` |
| TC-004 | S04 | yes | command | pending | `./spec-dock/scripts/spec-dock authoring validate issue-draft-adoption` | pass | expected exit 1; deferred diagnostics include `next_issue=iss-00303` |
| TC-005 | S05 | yes | command | pending | focused CLI runtime tests | pass | `uv run pytest tests/cli_runtime/test_authoring.py` -> 11 passed |
| TC-006 | S05 | yes | command | pending | `./spec-dock/scripts/spec-dock validate` | pass | `spec-dock: ok (validate) nodes=202` |
| cl-001..cl-008 | S01..S99 | yes | mixed | plan repaired | `plan.md` Spec-Locked Closure Index | pass | planning re-review passed; implementation evidence recorded |
| cl-005 | S05 | yes | focused test | plan repaired | forbidden authority phrase coverage | pass | focused test covers `.assurance.json` / authorized profile / `set-authorized-profile` / `success` / `adoption_status` / `adopted` claim absence |

## PR delivery defer evidence

| 対象 Issue | final quality gate Issue | dependency edge | no-per-Issue-PR rationale | merge-prepared claim |
|---|---|---|---|---|
| iss-00297 | iss-00307 | relay chain includes iss-00297 and final Issue `iss-00307` | Epic は複数 Issue をリレー方式で完了し、PR は final quality gate Issue に集約する | none |

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）

| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| authoring command help / deferred boundary | yes | orchestrator | `./spec-dock/scripts/spec-dock authoring --help`; `tests/cli_runtime/test_authoring.py` | pass |

### 最終 QA ゲート（Final QA Gate）

| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer | whole issue obligation coverage | focused CLI runtime tests, parity/init tests, validate, diff check, full `tests/cli_runtime` completed | pass: re-review findings none | pass |

### 最終コードレビューゲート（Final Code Review Gate）

| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer | issue-wide integrated diff | initial P2 help wording finding fixed in D-004; re-review findings none | 1 | pass |

### 最終 spec review ゲート（Final Spec Review Gate）

| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report / implementation diff alignment | initial P1/P2 findings fixed in D-004/D-005; re-review findings none | 1 | pass |

### 最終 commit（Final Commit）

| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| ready for commit | issue-scoped docs, provider runtime, dogfooding mirror, focused tests | final quality gate Issue `iss-00307` | ready |

## 省略/例外メモ

- 中間 Issue のため PR delivery は実施しない。
