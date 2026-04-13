---
種別: 実装報告書（Issue）
ID: "iss-00072"
タイトル: "Legacy authority retirement and final spec close"
関連GitHub: ["#72"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-04-13"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00072 Legacy authority retirement and final spec close — 実装報告（LOG）

## 実装サマリー
- issue-72 は `install_root` authority 一本化の最終 closeout tranche として、current tests / repo guidance / current closeout docs の residual legacy authority assumptions を retire する。
- prep phase では requirement / design / plan を現 repo 状態に合わせて更新し、spec review pass まで fix した。

## 実装記録（セッションログ） (必須)

### 2026-04-13 00:00 - 00:00

#### 対象
- Step: prep
- AC/EC: implementation readiness

#### 実施内容
- issue-69/70/71 完了後の repo reality を調査し、production code の authority はすでに `install_root` に切替済みで、主な残課題が `tests/test_init_update.py`、`AGENTS.md`、issue-72 / epic closeout docs であることを確認した。
- issue-72 requirement / design を、legacy `codex_skills` を historical artifact として残しつつ current authority assertion だけを retire する契約へ補正した。
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
- pending:
  - S01 cleanup commit

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

## authority-uniqueness (必須)
- provider_authority_artifacts:
  - pending_until_execution
- retired_legacy_surfaces:
  - pending_until_execution
- dogfooding_convergence_evidence:
  - pending_until_execution
- result:
  - pending_until_execution

## historical-boundary (必須)
- current_docs_corpus:
  - pending_until_execution
- out_of_scope_historical_records:
  - pending_until_execution
- result:
  - pending_until_execution

## future-host-extension (必須)
- current_model_statement:
  - pending_until_execution
- claude_code_scope_statement:
  - pending_until_execution
- result:
  - pending_until_execution

## upstream-prerequisites (必須)
- epic_requirement_refs:
  - pending_until_execution
- epic_design_refs:
  - pending_until_execution
- epic_plan_refs:
  - pending_until_execution
- epic_report_refs:
  - pending_until_execution
- epic_report_status:
  - pending_until_execution
- issue68_refs:
  - pending_until_execution
- issue68_evidence_status:
  - pending_until_execution
- issue69_refs:
  - pending_until_execution
- issue69_evidence_status:
  - pending_until_execution
- issue70_refs:
  - pending_until_execution
- issue70_evidence_status:
  - pending_until_execution
- issue71_refs:
  - pending_until_execution
- issue71_evidence_status:
  - pending_until_execution
- issue72_requirement_refs:
  - pending_until_execution
- issue72_design_refs:
  - pending_until_execution
- contradiction_summary:
  - pending_until_execution
- result:
  - pending_until_execution

## final-close-gate (必須)
- gate_checks:
  - pending_until_execution
- result:
  - pending_until_execution

## post-review-audit (任意)
- spec_review_reference:
  - issue-72 prep review pass recorded in prep session

## 省略/例外メモ (必須)
- 該当なし
