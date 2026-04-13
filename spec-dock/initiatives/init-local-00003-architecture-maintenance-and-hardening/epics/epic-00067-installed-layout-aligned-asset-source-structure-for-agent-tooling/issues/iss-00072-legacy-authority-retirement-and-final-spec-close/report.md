---
種別: 実装報告書（Issue）
ID: "iss-00072"
タイトル: "Legacy authority retirement and final spec close"
関連GitHub: ["#72"]
状態: "approved"
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
  - `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json` を provider-side authoritative manifest として確認した。
  - historical artifact として残る `src/spec_dock/assets/codex_skills/host-adapters/meta.json` も確認し、`source_of_truth_asset` は legacy root ではなく `install_root/.codex/agents/spec-dock.toml` と `install_root/.github/agents/spec-dock.agent.md` を指していることを再確認した。
- retired_legacy_surfaces:
  - `AGENTS.md` は `install_root` を current authority、`codex_skills` を historical artifact としてだけ記述している。
  - `tests/test_init_update.py` の current authority assertions は `install_root` 基準へ揃っており、残存する `codex_skills` hit は historical regression coverage / legacy duplicate classification / inert duplicate path explanation に限定される。
  - `tests/test_cli.py`、`tests/cli_runtime`、`tests/domain_runtime`、`tests/presentation_runtime` に current authority assertion としての `codex_skills` hit はない。
- dogfooding_convergence_evidence:
  - `uv run python -m spec_dock.cli update .` -> `spec-dock: ok (update) -> /srv/mount/spec-dock`
  - `./spec-dock/scripts/spec-dock validate` -> `spec-dock: ok (validate) nodes=29`
  - `./spec-dock/scripts/spec-dock sync --github` -> `spec-dock: ok (sync)` / active unchanged
  - `git status --short` は空で、issue-72 closeout evidence 取得後の dogfooding mirror / tracked files に drift が残っていない。
- result:
  - `install_root` が唯一の current authority であり、legacy `codex_skills` は historical artifact としてのみ残る状態を issue-72 current surfaces で再確認した。

## historical-boundary (必須)
- current_docs_corpus:
  - current docs corpus は issue-72 requirement/design/plan/report、epic-00067 requirement/design/plan/report、`AGENTS.md`、provider-side/dogfooding-side current docs の契約に従って確認した。
  - issue-72 S02 で epic current report を template から evidence-bearing closeout report へ更新し、issue-70 current report の pending commit 記述も解消した。
- out_of_scope_historical_records:
  - `spec-dock/initiatives/init-local-00002-*` 配下の closed issue/discussion、issue-68/69 requirement 上の historical `codex_skills` 文脈、`src/spec_dock/assets/codex_skills/**` の physical tree は historical record / artifact として scope 外に据え置いた。
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
  - final closeout update 後に `approved` へ引き上げる対象
- issue68_refs:
  - `../issues/iss-00068-install-root-tree-and-asset-classification/{requirement.md,design.md,report.md}`
- issue68_evidence_status:
  - report front matter は `draft` のままだが、foundation tranche の evidence と representative commits は揃っている
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
  - current-surface scoped search:
    - `rg -n "codex_skills" AGENTS.md tests/test_init_update.py tests/test_cli.py tests/cli_runtime tests/domain_runtime tests/presentation_runtime`
    - classification は authority-uniqueness 節のとおり
  - provider-side manifest review:
    - `install_root/.agents/host-adapters/meta.json` と legacy `codex_skills/host-adapters/meta.json` を比較確認
  - dogfooding convergence:
    - `uv run python -m spec_dock.cli update .` -> `ok`
    - `./spec-dock/scripts/spec-dock validate` -> `ok`
    - `./spec-dock/scripts/spec-dock sync --github` -> `ok`
  - final reviews:
    - final code review cycle:
      - initial review: `fail`
      - finding: unresolved `pending_until_review` placeholders and premature epic approval while issue report was still `draft`
      - corrective action: S99 report update resolved the final gate placeholders and aligned issue report status with the epic closeout verdict
      - final re-review: `pass`
    - final spec review:
      - `pass`
- result:
  - final close gate evidence is complete after code re-review and final spec review pass.

## post-review-audit (任意)
- spec_review_reference:
  - issue-72 prep review pass recorded in prep session
- final_code_review_reference:
  - initial final code review identified unresolved closeout placeholders and issue/epic status mismatch.
  - S99 corrective revision resolved both findings before final re-review.
- final_spec_review_reference:
  - final spec review pass recorded for issue-72 requirement/design/plan/report and epic closeout report.

## 省略/例外メモ (必須)
- 該当なし
