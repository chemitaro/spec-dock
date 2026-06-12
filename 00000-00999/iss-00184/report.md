---
種別: 実装報告書（Issue）
ID: "iss-00184"
タイトル: "Rename Spec Dock Hub Skill"
関連GitHub: ["#184"]
状態: "executed; final reviewers passed"
作成者: "iwasawayuuta"
最終更新: "2026-06-12"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00184 Rename Spec Dock Hub Skill — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

> `report.md` は観測証跡台帳（observed evidence ledger）の scaffold です。planned requirements、evidence destination、closure 条件は `plan.md` が持ち、この文書は実際の Red / Green / Refactor evidence、発見された tests、closure delta、reviewer status、commit/no-op evidence を記録する evidence slot です。workflow / compliance authority は skills、docs、accepted ADRs、reviewer gates に置きます。

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger / 必須）

`report.md` は実装中・文書更新中に発生した material な仕様解釈、判断、plan 逸脱、tradeoff、open question、promotion / follow-up を記録する audit trail でもある。worker の raw note や作業 transcript を貼る場所ではなく、orchestrator が source docs、diff、tests、reviewer output と照合して issue-level の canonical entry に統合する。

Material な判断がない場合もこの section は残し、次を明示する。

- No material interpretation changes.
- No decision entries.

Ledger entry は次の契約値を使う。

- `Status`: `open` / `resolved` / `superseded`
- `Type`: `interpretation` / `scope` / `implementation` / `compatibility` / `test-strategy` / `operation` / `deviation` / `follow-up`
- `Disposition`: `applied` / `rejected` / `promoted_to_design` / `promoted_to_adr` / `promoted_to_plan` / `converted_to_followup` / `deferred` / `no_action` / `superseded`

完了時の意味論（completion semantics）:
- issue completion 前に `Status=open` の entry を残してはならない。
- `Status=resolved` は `Disposition`、evidence、必要な follow-up を持つ。
- `Status=superseded` または `Disposition=superseded` は置換先 entry ID を持つ。
- `Disposition=promoted_to_design` / `promoted_to_adr` / `promoted_to_plan` は昇格先 artifact と evidence を持つ。
- `Disposition=converted_to_followup` は follow-up issue / discussion / ADR candidate の参照を持つ。
- `Disposition=deferred` は scope 外である理由、blocking でない根拠、revisit 条件を持つ。
- `Disposition=no_action` は issue-local な判断で追加対応不要である理由を持つ。将来も効く durable decision を `report.md` だけに閉じ込めてはならない。

Disposition ごとの必須証跡:
- `applied`: 変更した artifact / 実装証跡と、issue-local 適用で十分な理由。
- `rejected`: 却下した選択肢、理由、blocking impact が残らない根拠。
- `promoted_to_design` / `promoted_to_adr` / `promoted_to_plan`: 昇格先 artifact 参照と証跡。
- `converted_to_followup`: follow-up issue / discussion / ADR candidate 参照と blocking / non-blocking の分類。
- `deferred`: scope-out 理由、non-blocking の根拠、revisit 条件。
- `no_action`: 判断が issue-local で durable ではない理由。
- `superseded`: 置換先 entry ID と置換理由。

| 識別子（ID） | 状態（Status） | 種別（Type） | 起票元（Raised By） | 契機 / 差分（Gap） | 検討した選択肢 | 判断 / 解釈 | 根拠（Rationale） | 処置（Disposition） | 証跡（Evidence） | フォローアップ（Follow-up） |
|---|---|---|---|---|---|---|---|---|---|---|
| D-001 | resolved | scope | orchestrator | User request targets the hub skill name, while existing `iss-00164` already completed hub/leaf routing wording | Option A: reopen/reuse `iss-00164`; Option B: create a follow-up issue under the same Epic; Option C: edit implementation directly without a new issue | Create a new follow-up issue for naming / compatibility / reference cleanup | `iss-00164` is `done` and covers hub/leaf responsibility boundary, not canonical skill naming and migration | applied | `./spec-dock/scripts/spec-dock deps check --id iss-00164`; `iss-00164/requirement.md`; user request 2026-06-12 | Continue requirement/design/plan authoring for `iss-00184` |
| D-002 | resolved | scope | user | Clarification asked whether to preserve old `spec-driven-tdd-workflow` as compatibility surface or migrate fully | Option A: full canonical rename with no compatibility alias; Option B: staged compatibility; Option C: metadata-only clarification | Migrate fully to a new integrated hub name and do not leave compatibility surfaces | User explicitly said compatibility is unnecessary and the tool should not leave contradictions or broken mixed naming for users | applied | `discussions/20260612t070646z-interview-hub-skill-naming-compatibility-direction.md`; user answer 2026-06-12 | Adopt into requirement; carry into design / plan as full migration and negative inspection |
| D-003 | resolved | scope | user | Full migration requires a durable new canonical skill name | Option A: `spec-dock-hub`; Option B: `spec-dock-workflow-hub`; Option C: `spec-dock-governance-hub` | Use `spec-dock-hub` as the canonical skill name | User accepted `spec-dock-hub` as simple and easy to understand; it matches the original goal of making the hub role obvious | applied | `discussions/20260612t071326z-interview-canonical-hub-skill-name.md`; user answer 2026-06-12 | Adopt into requirement; carry into design / plan rename targets |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | user interview | `requirement.md` scope / constraints / AC | User answer resolves the blocker about compatibility and directly changes the issue success criteria | `discussions/20260612t070646z-interview-hub-skill-naming-compatibility-direction.md` | Author design / plan with full migration, no compatibility alias, and negative inspection for old current-surface references |
| EAL-002 | adopted | user interview | `requirement.md` canonical name | User answer fixes the full migration target name, allowing design / plan to pin paths and test expectations | `discussions/20260612t071326z-interview-canonical-hub-skill-name.md` | Author design / plan around `spec-dock-hub` |
| EAL-003 | adopted | repository research | `requirement.md` current surface / test / update acceptance | Research identifies current surfaces and distinguishes historical evidence from current runtime/discovery references | `discussions/20260612t072453z-research-spec-dock-hub-rename-surface-inventory.md`; `rg` inventory over README, cli.py, docs, tests, provider and mirror skills | Use as design / plan source for file map, negative inspection, and test obligations |
| EAL-004 | adopted | system-architect draft | `design.md` architecture and migration design | Draft cleanly maps approved requirement decisions to provider source, dogfooding mirror, installer/update lists, docs, tests, and historical evidence boundaries without editing forbidden files | `discussions/20260612t073146z-draft-design-spec-dock-hub-full-migration.md`; diff guard by `git diff --name-status` showed only canonical docs already edited by orchestrator and discussion drafts, with system-architect reporting it created only the new draft | Adopt into canonical `design.md`; preserve main-orchestrator ownership and run fresh design spec-reviewer |
| EAL-005 | adopted | design spec-reviewer finding | `design.md` install/update cleanup contract | Reviewer identified that `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json` drives obsolete exact file deletion for existing consumers and was missing from the design; this is required for AC-006 and no-compatibility migration | Ptolemy `019ebac2-471b-7592-8896-f9691a9a22d7` design review `review_status=fail`; `rg` and manifest inspection of `managed_assets.obsolete_exact_file_paths` | Design updated to include `host-adapters/meta.json`, old hub exact path cleanup contract, related tests, and negative inspection exceptions; rerun fresh design spec-reviewer |
| EAL-006 | adopted | implementation-planner draft | `plan.md` executable step structure and closure index | Draft provides a concrete dependency order, step slicing, delegation contracts, closure index candidates, focused tests, current-surface inspections, docs impact step, final quality gates, and amendment triggers aligned with the reviewed design | `discussions/20260612t-plan-draft-spec-dock-hub-full-migration.md`; diff guard by `git status --short` showed the delegated role created only the requested discussion draft beyond pre-existing canonical docs and earlier discussion drafts; Volta reported no forbidden files edited | Adopt into canonical `plan.md`; preserve main-orchestrator ownership and run fresh plan spec-reviewer |
| EAL-007 | adopted | plan spec-reviewer findings | `plan.md` closure precision and step gate clarity | Plan reviewer passed the canonical plan but found non-blocking precision issues: cl-ac-004 could be read as fully closeable before S05 sync/validate, and S01 commit/no-op gate should be explicit | Gauss `019ebad0-c01f-7ff2-bcfb-9f1f2688b3c5` plan review `review_status=pass` with P2/P3 findings | Plan updated to mark S01/S04 as partial cl-ac-004 evidence, S05/S99 as final closure, and S01 no-op gate expectations; rerun fresh plan spec-reviewer after fix |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | Primary objective is a clear, integrated SpecDock hub skill name with no contradictory compatibility surface | Secondary requirements cover reference inventory, provider/mirror verification, tests, and historical evidence handling | low | requirement/design/plan/final reviewer gates found no objective inversion after fixes |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | active issue/epic docs; hub skill source; README/docs/tests/CLI references; `iss-00164` done state; interview artifacts; surface inventory research | User answered compatibility policy: full migration, no compatibility alias. User also accepted `spec-dock-hub` as the canonical name. | Adopt full migration, `spec-dock-hub`, and current-surface inventory into requirement | fresh `spec-reviewer` pass by Darwin (`019ebaba-245a-7811-8e33-97ddb0423b71`), no findings, confidence 0.88 | no | promoted to design |
| design | reviewed requirement; report ledgers; research; system-architect draft; current source/test/docs surfaces; install-root manifest | Design reviewer found missing `host-adapters/meta.json` obsolete exact path cleanup contract; answered by adding manifest contract to design | Adopt system-architect draft plus reviewer correction into canonical design | first fresh `spec-reviewer` by Ptolemy (`019ebac2-471b-7592-8896-f9691a9a22d7`) failed with P1; fix applied; fresh `spec-reviewer` pass by Peirce (`019ebac6-5111-7222-9e74-706e45f2285e`), no findings, confidence 0.88 | no | promoted to plan |
| plan | reviewed requirement; reviewed design; implementation-planner draft; issue-plan authoring docs; workflow_issue; current source/test/docs surfaces | Plan reviewer passed with non-blocking precision findings about cl-ac-004 final closure timing and S01 no-op gate clarity; both were addressed in canonical plan | Adopt delegated draft plus reviewer precision fixes into canonical plan | first fresh `spec-reviewer` by Gauss (`019ebad0-c01f-7ff2-bcfb-9f1f2688b3c5`) passed with P2/P3 non-blocking findings; fixes applied; fresh `spec-reviewer` pass by Hypatia (`019ebad6-580b-7db3-b89c-ec5dcf3e4280`), no findings, confidence 0.90 | no | promoted to execution handoff readiness |

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）
- 委任 authoring の使用:
  - used / not used
- 未使用の場合:
  - manual authoring path / 委任ドラフトを昇格証跡として使っていない理由。
- lifecycle state（契約値）:
  - `requested`, `produced`, `integrated`, `partially_integrated`, `rejected`, `superseded`, `blocked`, `stale`
- 昇格不可 state:
  - `stale`, `rejected`, `superseded`, `blocked`
- 標準出力先:
  - 対象 scope の `discussions/` direct child にある flat Markdown
  - filename: `<ts>-<kind>-<slug>.md` または same-second collision 用 `<ts>-<nn>-<kind>-<slug>.md`
- 軽量 provenance:
  - `created_by_role`, `scope_id`, `source_paths`, `intended_targets`, `adoption_status: unreviewed`, `reflected_to: []`, `diff_guard_result`, fallback decision, report evidence destination, adoption ledger note
  - 互換 label: source artifacts, draft artifact path, status, integration result, rejected portions, blockers, reviewer result, promotion decision
- 禁止 self-claim:
  - `authority: accepted`, `adoption_status: adopted`, non-empty `reflected_to`, reviewer pass, phase completion, implementation readiness
- 禁止 wildcard token:
  - `*`, `grants.*`, `all`
- 標準必須にしない field:
  - task manifest hash, Permission Profile hash, session invocation hash, probe run id, session hash
- historical note:
  - 既存 `iss-00126` などの manifest/Profile/probe/session artifacts は grandfathered evidence として残し、削除・rename・validation failure 化しない。

| ロール（created_by_role） | 範囲（scope_id） | ドラフトパス（discussion draft path） | 参照元（source_paths） | 予定反映先（intended_targets） | 採用状態（adoption_status） | 反映先（reflected_to） | 差分ガード結果（diff_guard_result） | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果（reviewer result） | 昇格判断（promotion decision） |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| system-architect | iss-00184 | `discussions/20260612t073146z-draft-design-spec-dock-hub-full-migration.md` | `requirement.md`; report; interviews; research; parent epic; AGENTS; cli.py; provider/mirror hub skill; README/docs/tests surfaces | `design.md` | adopted | `design.md` | pass: only one scope-local discussion draft was created by the delegated role; no canonical/implementation/test/config edits by the delegated role | integrated into canonical design by main orchestrator | none | none | first design review failed on missing manifest cleanup contract; canonical design fixed; fresh re-review passed | promoted to plan after reviewer pass |
| implementation-planner | iss-00184 | `discussions/20260612t-plan-draft-spec-dock-hub-full-migration.md` | `requirement.md`; `design.md`; report; research; issue plan authoring docs; workflow_issue; cli.py; host-adapters meta; tests/harness surfaces | `plan.md` | adopted | `plan.md` | pass: only the requested scope-local discussion draft was newly created by the delegated role; no canonical/implementation/test/config edits by the delegated role | integrated into canonical plan by main orchestrator | none | none | first plan review passed with non-blocking precision findings; canonical plan fixed; fresh re-review passed with no findings | promoted to execution handoff readiness |

### 委任ドラフトの失敗モード（Delegated Draft Failure Modes）
| 失敗モード | 期待される判定 | 許可される次アクション | レポート証跡の記録先（report evidence destination） | 昇格可否 |
|---|---|---|---|---|
| 同意なし（missing consent） | blocked / incomplete | 範囲付き同意を取得する、または手動 authoring に戻す | この section | ineligible |
| 前段 reviewer pass 不足 / stale（missing/stale previous reviewer pass） | blocked / incomplete | レビューゲートを再実行する（rerun reviewer gate） | レビューゲート証跡（Reviewer Gate Status / Final Spec Review Gate） | ineligible |
| 設計中の要件 gap（requirement gap during design） | blocked / incomplete | requirement phase へ戻す | 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger） | ineligible |
| 計画中の設計 gap（design gap during plan） | blocked / incomplete | design phase へ戻す | 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger） | ineligible |
| ロール利用不可（role unavailable） | blocked / manual path | 利用不可を記録し、妥当なら手動で続行する | この section | ineligible |
| 禁止行為の試行（forbidden action attempt） | rejected | ドラフトを破棄し incident を記録する | この section / decision ledger | ineligible |
| 古いドラフト（stale draft） | stale | 再生成または差分調整する | この section | ineligible |
| 置換済みドラフト（superseded draft） | superseded | 置換先ドラフトを参照する | この section | ineligible |
| 委任使用主張に対する証跡不足（missing draft evidence when delegated use is claimed） | incomplete | 証跡を追加する、または委任使用 claim を外す | この section | ineligible |
| reviewer 利用不可 / 拒否 / waiver / provisional（reviewer unavailable/denied/waived/provisional） | blocked / incomplete | fresh な passed reviewer を取得する、または昇格なしの risk acceptance を記録する | レビューゲート証跡（Reviewer Gate Status / Final Spec Review Gate） | ineligible |

## 実装サマリー (任意)
- Hub skill の current name/path を `spec-driven-tdd-workflow` から `spec-dock-hub` へ移行し、provider asset、dogfooding mirror、installer/update cleanup metadata、current docs、tests/harness expectations を統合的に更新した。
- 旧名は compatibility surface として残さず、obsolete cleanup metadata、prune/legacy cleanup fixtures、historical evidence に限定した。
- Final validation は focused / fallback pytest、sync、validate、diff-check、provider/mirror parity、scoped current-surface inspections で pass した。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-06-12 execution）

#### 対象
- Step: S01-S05, S90, S99
- AC/EC: AC-001 through AC-006, EC-001 through EC-003
- 計画上の出典（Planned source）:
  - `plan.md` steps S01-S05, S90, S99
  - closure ids: all AC / EC closure ids

#### 実施内容
- Executed the approved full migration plan from old hub skill name to `spec-dock-hub`.

#### 実行コマンド / 結果
```bash
see TDD / Test Contract / Final Quality Gate tables below

pass unless explicitly recorded as fail-as-expected or fixed reviewer finding
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S01 | 赤フェーズ / 代替証跡（Red / alternative） | inspect-only: old provider/mirror `spec-driven-tdd-workflow/SKILL.md` exists and new `spec-dock-hub/SKILL.md` does not exist | old provider and mirror paths existed; new provider and mirror paths did not exist before S01 | `test -e src/.../spec-driven-tdd-workflow/SKILL.md`; `test -e .agents/.../spec-driven-tdd-workflow/SKILL.md`; `test ! -e src/.../spec-dock-hub/SKILL.md`; `test ! -e .agents/.../spec-dock-hub/SKILL.md` | pass | pre-change characterization matched S01 plan |
| S01 | 緑フェーズ（Green） | rename provider/mirror hub skill to `spec-dock-hub`, preserve byte parity, remove old current path, keep hub/leaf boundary | new provider/mirror `spec-dock-hub/SKILL.md` files exist and are byte-equivalent; old provider/mirror `spec-driven-tdd-workflow/SKILL.md` files do not exist; text contains `name: spec-dock-hub`, `SpecDock Hub`, `route selector`, and `global invariant` | `cmp -s src/spec_dock/assets/install_root/.agents/skills/spec-dock-hub/SKILL.md .agents/skills/spec-dock-hub/SKILL.md`; `rg -n "name: spec-dock-hub|SpecDock Hub|route selector|global invariant" ...`; old-path `test ! -e ...`; `git diff --check` | pass | doc-writer Erdos implemented S01; parent re-ran the planned checks |
| S01 | リファクタリング（Refactor） | guardrail satisfied / no refactor needed | no additional refactor performed; changes remained inside S01 allowed paths | `git status --short`; `git diff --name-status`; reviewer checks | pass | S02 docs/tests/runtime/manifest updates intentionally not mixed into S01 |
| S02 | 赤フェーズ / 代替証跡（Red / alternative） | covered-existing / red-required: focused installer/update tests should fail while current managed skill still points at the removed old asset | focused pytest failed because `_MANAGED_SKILL_NAMES` / tests still treated `spec-driven-tdd-workflow` as current and init/update looked for the missing provider asset | `uv run pytest tests/unit/infra/test_init_update.py -k "managed or obsolete or manifest or prunes or skill"` | fail-as-expected | failure class: `Missing asset file: .../spec-driven-tdd-workflow/SKILL.md` |
| S02 | 緑フェーズ（Green） | update current managed skill to `spec-dock-hub`; represent old hub as obsolete exact-file cleanup; focused tests pass | `_MANAGED_SKILL_NAMES` uses `spec-dock-hub`; old hub exact path is in `managed_assets.obsolete_exact_file_paths`; focused pytest passed `59 passed, 296 deselected`; current/obsolete overlap absent by inspection | `uv run pytest tests/unit/infra/test_init_update.py -k "managed or obsolete or manifest or prunes or skill"`; `rg` inspection; `git diff --check` | pass | dev-coder Sagan implemented S02; parent re-ran focused tests and inspection |
| S02 | リファクタリング（Refactor） | guardrail satisfied / no broad installer cleanup rewrite | no installer architecture rewrite; no compatibility alias / forwarding skill / symlink; S04 harness/test_wrappers and S03 docs left for later steps | `git diff --stat`; `git diff --check`; code-reviewer Lorentz | pass | S02 remained in allowed paths |
| S03 | 赤フェーズ / 代替証跡（Red / alternative） | inspect-only: current docs contain old hub name before change | `README.md`, provider docs README, and dogfooding docs README contained `spec-driven-tdd-workflow` as current hub entry/path | `rg -n "spec-driven-tdd-workflow|Spec-driven TDD Workflow|spec-dock-hub" README.md src/spec_dock/assets/spec_dock/docs/README.md spec-dock/docs/README.md` | pass | pre-change current docs matches were `README.md:173`, provider docs `README.md:13`, dogfooding docs `README.md:13` |
| S03 | 緑フェーズ（Green） | current docs point to `spec-dock-hub` and no current old-name docs entry remains | all 3 S03 docs contain `spec-dock-hub`; no S03 target docs contain `spec-driven-tdd-workflow` or `Spec-driven TDD Workflow` | positive `rg -n "spec-dock-hub" ...`; negative `rg -n "spec-driven-tdd-workflow|Spec-driven TDD Workflow" ...`; `git diff --check` | pass | doc-writer Singer implemented S03; parent re-ran inspection |
| S03 | リファクタリング（Refactor） | guardrail satisfied / no unrelated docs rewrite | changes are one-line current hub entry/path replacements in 3 allowed docs only | `git diff -- README.md src/spec_dock/assets/spec_dock/docs/README.md spec-dock/docs/README.md`; `spec-reviewer` Turing | pass | no compatibility wording added |
| S04 | 赤フェーズ / 代替証跡（Red / alternative） | covered-existing / red-required: tests and harness should expose old current-name assumptions before S04 | wrapper test failed because it read removed old hub path; focused unit lane failed because dogfooding mirror `meta.json` lagged provider obsolete cleanup manifest | `uv run pytest tests/cli_runtime/test_wrappers.py`; `uv run pytest tests/unit/infra/test_init_update.py -k "managed or skill or bundled or parity or routing or prunes or obsolete or manifest or README"` | fail-as-expected | failures: `FileNotFoundError` for `.agents/skills/spec-driven-tdd-workflow/SKILL.md`; parity mismatch for `.agents/host-adapters/meta.json` |
| S04 | 緑フェーズ（Green） | tests / harness treat `spec-dock-hub` as current expected hub and retain old path only as obsolete cleanup evidence | wrapper tests passed; focused unit lane passed; harness current skill tuple uses `spec-dock-hub`; wrapper reads installed `spec-dock-hub`; mirror `meta.json` matches provider obsolete cleanup entry | `uv run pytest tests/cli_runtime/test_wrappers.py`; `uv run pytest tests/unit/infra/test_init_update.py -k "managed or skill or bundled or parity or routing or prunes or obsolete or manifest or README"`; `git diff --check`; `./spec-dock/scripts/spec-dock validate` | pass | parent re-ran Goodall's checks: `6 passed`; `95 passed, 260 deselected`; validate pass |
| S04 | リファクタリング（Refactor） | guardrail satisfied / no compatibility alias or broad test rewrite | old-name references remain only in obsolete cleanup metadata and prune/legacy fixtures; runtime harness and wrapper current expectations have no old-name reference | `rg -n "spec-driven-tdd-workflow|Spec-driven TDD Workflow|spec-dock-hub|SpecDock Hub" tests/cli_runtime tests/unit/infra/test_init_update.py .agents/host-adapters/meta.json`; `git diff --check` | pass | test_init_update managed-skill expectation now reuses harness current tuple instead of local conversion |
| S05 | 赤フェーズ / 代替証跡（Red / alternative） | inspect-only: historical `rg` shows expected old-name past evidence, while current-surface old-name matches must be classified | historical `spec-dock/initiatives/**` contains many old-name references from completed specs/discussions; current-surface old-name matches are limited to cleanup metadata and prune fixtures | `rg -n "spec-driven-tdd-workflow|Spec-driven TDD Workflow" spec-dock/initiatives`; scoped current-surface old-name `rg` | pass | historical matches are non-current evidence; current matches were 6 cleanup/test entries only |
| S05 | 緑フェーズ（Green） | sync, validate, diff-check, `cmp`, and scoped inspections pass | `sync` passed and left worktree clean; `validate` passed; `cmp` provider/mirror hub skill passed; positive new-name `rg` found current docs/code/tests/skills; negative old-name current-surface `rg` found only allowed cleanup/test exceptions | `./spec-dock/scripts/spec-dock sync`; `./spec-dock/scripts/spec-dock validate`; `git diff --check`; `git status --short`; `cmp -s ...spec-dock-hub...`; positive/negative scoped `rg` | pass | `sync` wrote projection files but produced no tracked diff; cl-ac-004 can now close fully |
| S05 | リファクタリング（Refactor） | no manual historical rewrite or generated-data cleanup | no generated/runtime/docs diff remained after sync; no historical specs were rewritten | `git status --short`; `git diff --check` | pass | S05 implementation is report evidence only |
| S99 | 最終検証（Final validation） | final required validation and inspections pass | wrapper focused test passed; focused unit lane passed; fallback combined lane passed; sync/validate/diff-check/cmp passed; current-surface inspections passed with old-name matches limited to cleanup/test exceptions and historical evidence | `uv run pytest tests/cli_runtime/test_wrappers.py`; focused `tests/unit/infra/test_init_update.py -k ...`; fallback `uv run pytest tests/unit/infra/test_init_update.py tests/cli_runtime/test_wrappers.py`; `sync`; `validate`; `git diff --check`; `cmp`; scoped `rg` | pass | QA/code gates pass; final spec re-review pending after ledger fix |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S01 | docs/tests/runtime/manifest still reference old name | implementation / worker note | recorded as planned downstream work for S02+; not a S01 risk | cl-ac-001 / cl-ec-002 partial | no | worker note: old-name docs/tests/runtime references are S02+ scope |
| S02 | `tests/cli_runtime/harness.py` and wrapper tests still use old name | implementation / worker note | recorded as planned S04 work; S02 prohibited harness/test_wrappers edits | cl-ac-006 / cl-ec-001 partial | no | worker note and `rg` inspection show remaining harness references are downstream S04 scope |
| S03 | additional current docs surfaces may exist outside known 3 files | plan / worker note | defer to S05/S90 scoped current-surface inspection | cl-ac-005 / cl-ec-003 | no | S03 worker notes additional current docs/tests/runtime surfaces are S05/S90 scope |
| S04 | dogfooding mirror `meta.json` lagged provider obsolete cleanup manifest | focused pytest / parity test | synchronized mirror `.agents/host-adapters/meta.json` with provider obsolete exact path entry | cl-ac-004 / cl-ac-006 | no | parity failure was within S04 dogfooding/harness expectation scope; provider source was already updated in S02 |
| S05 | scoped current-surface old-name inspection still reports cleanup/test matches | current-surface `rg` | classified allowed exceptions: `_LEGACY_MANAGED_SKILL_NAMES`, provider/mirror obsolete exact path metadata, and prune/legacy cleanup fixtures | cl-ac-005 / cl-ec-003 | no | no README/docs/skills/harness wrapper current discovery match remains |
| S90 | no additional current docs impact after S05 | S05 scoped current-surface inspection | record approved no-op for docs impact resolution; no doc-writer edit required | cl-ac-005 / cl-ec-003 | no | S03 already updated known current docs; historical references remain excluded evidence |
| S99 | broader fallback pytest found two test harness expectation gaps | S99 fallback pytest | updated legacy obsolete hub fixture setup to create parent directory and added `iss-00184/.meta.json` to checked-in dogfooding snapshot with `depends_on=[]` | cl-ac-001 / cl-ac-004 / cl-ac-006 / cl-ec-001 | no | `uv run pytest tests/unit/infra/test_init_update.py tests/cli_runtime/test_wrappers.py` first failed with 2 failures, then passed `361 passed` after bounded test fix |
| S99 | final current-surface inspection still reports old name in cleanup/test exceptions | final scoped `rg` | classify as allowed exceptions and keep historical evidence unchanged | cl-ac-005 / cl-ec-003 | no | current-surface old-name matches: `_LEGACY_MANAGED_SKILL_NAMES`, provider/mirror obsolete exact path metadata, and obsolete prune fixtures only |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S01 | cl-ac-001, cl-ac-003, cl-ec-002; cl-ac-004 partial only | S01 verification commands pass and required reviewers pass; do not mark cl-ac-004 fully closed in this step | provider/mirror skill renamed to `spec-dock-hub`; old current path absent; `cmp`, `rg`, old-path `test ! -e`, `git diff --check` pass; `spec-reviewer` Franklin pass; `code-reviewer` Parfit pass with report-evidence P2 addressed here | pass | cl-ac-004 final closure waits for S05/S99 sync/validate evidence |
| S02 | cl-ac-006, cl-ec-001 | Focused tests pass and code-reviewer passes | `_MANAGED_SKILL_NAMES` current hub is `spec-dock-hub`; manifest obsolete exact path includes `.agents/skills/spec-driven-tdd-workflow/SKILL.md`; focused pytest passed; code-reviewer Lorentz pass | pass | S04 will update runtime harness/wrapper expectations; no compatibility alias added |
| S03 | cl-ac-002, cl-ac-005 | docs inspection passes and spec-reviewer passes | `README.md`, provider docs README, and dogfooding docs README now use `spec-dock-hub`; old current docs matches absent; spec-reviewer Turing pass | pass | additional current-surface inspection remains S05/S90 |
| S04 | cl-ac-001, cl-ac-004 partial, cl-ac-006, cl-ec-001 | focused harness/wrapper/unit tests pass and code-reviewer passes | runtime harness current tuple uses `spec-dock-hub`; wrapper reads installed `spec-dock-hub` and checks hub wording; focused unit lane verifies managed skill inventory, obsolete cleanup fixture, and provider/mirror parity; no compatibility alias added; code-reviewer Avicenna pass after report evidence fix | pass | cl-ac-004 final closure still waits for S05/S99 sync/validate evidence |
| S05 | cl-ac-002, cl-ac-004, cl-ac-005, cl-ec-003 | sync, validate, diff-check, `cmp`, and scoped inspections pass | dogfooding `sync` and `validate` passed; worktree stayed clean; provider/mirror `spec-dock-hub` skill byte parity passed; new-name current-surface inspection passed; old-name current-surface matches are only cleanup metadata/tests; historical `spec-dock/initiatives/**` matches preserved | pass | no generated/runtime/docs diff, so no step reviewer required by plan |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| cl-ac-001 | S01 | yes | inspect-only + pytest later | old provider/mirror path existed; new path absent | `rg -n "name: spec-dock-hub|SpecDock Hub|route selector|global invariant" src/.../spec-dock-hub/SKILL.md .agents/.../spec-dock-hub/SKILL.md` | pass | S04 and S99 added installed inventory test evidence |
| cl-ac-003 | S01 | yes | inspect-only + reviewer | existing hub text routed to leaf skills | `spec-reviewer` Franklin reviewed skill wording and hub/leaf boundary | pass | no leaf workflow spine absorbed |
| cl-ec-002 | S01 | yes | inspect-only + reviewer | old name was vague; new path absent | new skill text includes `SpecDock Hub`, `route selector`, and `global invariant`; `spec-reviewer` pass | pass | short name clarified by heading/description/first bullets |
| cl-ac-004 | S01 | yes | command partial | provider/mirror old paths existed before S01 | `cmp -s src/spec_dock/assets/install_root/.agents/skills/spec-dock-hub/SKILL.md .agents/skills/spec-dock-hub/SKILL.md` | pass | partial parity evidence only; final closure waits for S05/S99 sync/validate |
| cl-ac-006 | S02 | yes | pytest + inspect-only | focused pytest failed before S02 with missing old hub asset | `uv run pytest tests/unit/infra/test_init_update.py -k "managed or obsolete or manifest or prunes or skill"` | pass | `59 passed, 296 deselected`; old hub exact path is obsolete cleanup |
| cl-ec-001 | S02 | yes | pytest | old path dependency was still treated as current before S02 | focused pytest plus current/obsolete boundary inspection | pass | no compatibility alias / forwarding skill / symlink |
| cl-ac-002 | S03 | yes | inspect-only | S03 target docs had old current hub references before change | positive/negative `rg` over S03 target docs | pass | classification: S03 current docs updated; historical evidence untouched |
| cl-ac-005 | S03 | yes | inspect-only | current docs presented old hub entry/path before change | positive `rg "spec-dock-hub"` and negative `rg "spec-driven-tdd-workflow|Spec-driven TDD Workflow"` over S03 target docs | pass | current docs target set uses new name |
| cl-ac-001 | S04 | yes | pytest | wrapper test previously read removed old hub path | `uv run pytest tests/cli_runtime/test_wrappers.py` | pass | wrapper now reads installed `spec-dock-hub` and asserts `name: spec-dock-hub`, `SpecDock Hub`, `route selector`, `global invariant` |
| cl-ac-004 | S04 | yes | command partial | mirror `meta.json` lagged provider obsolete cleanup manifest | focused unit parity test plus `./spec-dock/scripts/spec-dock validate` | partial-pass | final closure waits for S05/S99 sync/validate evidence |
| cl-ac-006 | S04 | yes | pytest | harness and wrapper still had old current-name assumptions before S04 | wrapper and focused unit pytest lanes | pass | tests now encode new current hub and old exact-path cleanup |
| cl-ec-001 | S04 | yes | pytest + inspection | old path dependency caused wrapper FileNotFoundError before S04 | wrapper pytest and scoped `rg` over tests/harness | pass | no alias / forwarding skill / symlink added |
| cl-ac-002 | S05 | yes | inspect-only | historical old-name references exist by design | scoped current/historical `rg` | pass | current old-name matches classified as cleanup/test only; historical matches preserved |
| cl-ac-004 | S05 | yes | command | S01/S04 provided partial parity/test evidence only | `./spec-dock/scripts/spec-dock sync`; `./spec-dock/scripts/spec-dock validate`; `cmp -s ...spec-dock-hub...`; `git status --short` | pass | first full closure of cl-ac-004 |
| cl-ac-005 | S05 | yes | inspect-only | S03 left broader current-surface inspection for S05 | positive/negative scoped current-surface `rg` | pass | no old-name current docs/discovery references remain outside cleanup/test exceptions |
| cl-ec-003 | S05 | yes | inspect-only | historical old-name evidence remains under `spec-dock/initiatives/**` | historical `rg` plus current-surface exception list | pass | no destructive historical rewrite performed |

- `closure id / test id` は Spec-Locked Closure Index の `id` を指す。別 alias を使う場合は `Closure Delta` で対応を記録する。

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| cl-ac-001 | S01 | new skill path, frontmatter, heading, description inspection | pass | S04/S99 installed inventory evidence completed |
| cl-ac-003 | S01 | `spec-reviewer` Franklin pass | pass | hub/leaf boundary maintained |
| cl-ec-002 | S01 | wording inspection and `spec-reviewer` pass | pass | short name clarity satisfied for skill text |
| cl-ac-004 | S01 | provider/mirror `cmp` | partial-pass | final closure waits for S05/S99 |
| cl-ac-006 | S02 | focused update/install tests and manifest inspection | pass | old hub exact path is obsolete cleanup, not current managed target |
| cl-ec-001 | S02 | focused tests and current/obsolete inspection | pass | old path dependency fixed for installer/update cleanup without alias |
| cl-ac-002 | S03 | S03 docs positive/negative `rg` and spec-reviewer pass | pass | current docs updated; broader reference classification continues in S05/S90 |
| cl-ac-005 | S03 | S03 docs positive/negative `rg` and spec-reviewer pass | pass | old name not present in S03 current docs |
| cl-ac-001 | S04 | installed wrapper test reads `spec-dock-hub` and validates hub wording | pass | installed inventory evidence added |
| cl-ac-004 | S04 | focused provider/mirror parity lane and validate | partial-pass | final closure waits for S05/S99 |
| cl-ac-006 | S04 | wrapper and focused unit pytest lanes | pass | new current hub plus old exact cleanup detection covered |
| cl-ec-001 | S04 | scoped old-name inspection over tests/harness plus pytest | pass | old path dependency removed without compatibility surface |
| cl-ac-002 | S05 | current/historical reference classification by scoped `rg` | pass | current exceptions are cleanup/test only |
| cl-ac-004 | S05 | sync, validate, `cmp`, clean status | pass | full closure reached |
| cl-ac-005 | S05 | positive/negative current-surface `rg` | pass | current surfaces use `spec-dock-hub` |
| cl-ec-003 | S05 | historical exclusion `rg` and no manual historical rewrite | pass | historical references intentionally preserved |
| all AC/EC | S99 | focused tests, fallback tests, sync, validate, diff-check, `cmp`, scoped positive/negative `rg` | pass | QA/code gates pass; final spec re-review pending after ledger fix |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | S01 closure set | N/A | cl-ac-001, cl-ac-003, cl-ec-002, cl-ac-004 partial | S01 executed as planned | no | no |
| none | S02 closure set | N/A | cl-ac-006, cl-ec-001 | S02 executed as planned | no | no |
| none | S03 closure set | N/A | cl-ac-002, cl-ac-005 | S03 executed as planned | no | no |
| none | S04 closure set | N/A | cl-ac-001, cl-ac-004 partial, cl-ac-006, cl-ec-001 | S04 executed as planned; mirror meta sync was discovered by focused parity test and remains within S04 dogfooding/harness expectation scope | no | no |
| none | S05 closure set | N/A | cl-ac-002, cl-ac-004, cl-ac-005, cl-ec-003 | S05 executed as planned; sync produced no tracked diff and current-surface old-name matches are allowed cleanup/test exceptions only | no | no |

#### ワークフロー委任同意の証跡（Workflow Delegation Consent）
`workflow_issue.md` is the policy source for workflow-scoped delegation consent. This report records observed consent, boundary, expiry, and denied / unavailable handling only.

| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user instruction: "レビューにおいても取りこぼしのないように、しっかりとレビューをしてください" plus requested `spec-dock-issue-planning` workflow | `/Users/iwasawayuuta/.codex/worktrees/82dd/spec-dock` | iss-00184 | current session | spec-reviewer, system-architect, implementation-planner, qa-reviewer, code-reviewer | same repo/worktree, active issue, current session, named roles only; canonical docs remain main-orchestrator-owned; delegated authoring may only create one scope-local flat Markdown discussion draft when explicitly invoked; no destructive action, publishing, credentialed external access, scope expansion, or hidden writes | issue complete / session end / scope change / host policy conflict / user revocation | none | proceed with issue planning reviewer and specialist gates |

#### 実装委任ゲート（Implementation Delegation Gate）
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | delegated | shipped skill text and provider/mirror scaffold asset change; parent direct implementation prohibited by workflow | doc-writer | provider/mirror hub skill rename and skill wording only | `requirement.md`; `design.md`; `plan.md` S01 | `src/.../.agents/skills/spec-dock-hub/SKILL.md`; `src/.../spec-driven-tdd-workflow/SKILL.md` deletion only; `.agents/skills/spec-dock-hub/SKILL.md`; `.agents/.../spec-driven-tdd-workflow/SKILL.md` deletion only | runtime code; tests; README/docs; `src/spec_dock/cli.py`; `host-adapters/meta.json`; canonical issue docs; historical specs; compatibility alias / forwarding skill / symlink | `cmp`; `rg` wording; old-path `test ! -e`; `git diff --check`; step reviewers | allowed paths insufficient; compatibility alias needed; boundary conflict with `iss-00164` | changed files; deleted paths; verification; unresolved risks; no-material-decision note | pass |
| S02 | delegated | installer/update cleanup contract touches runtime installer, manifest, and focused tests | dev-coder | current managed skill name, obsolete exact cleanup manifest, and focused unit tests | `requirement.md`; `design.md`; `plan.md` S02; `src/spec_dock/cli.py`; `host-adapters/meta.json`; focused tests | `src/spec_dock/cli.py`; `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json`; focused assertions/fixtures in `tests/unit/infra/test_init_update.py` | skill text/files; README/docs; `tests/cli_runtime/harness.py`; `tests/cli_runtime/test_wrappers.py`; broad test rewrites; compatibility alias / forwarding skill / symlink | focused pytest; `git diff --check`; current/obsolete inspection; code-reviewer | compatibility alias required; manifest obsolete overlap; allowed paths insufficient | changed files; red/green evidence; inspection; unresolved risks; no-material-decision note | pass |
| S03 | delegated | current docs references require shipped/dogfooding docs updates; parent direct docs implementation prohibited by workflow | doc-writer | current docs hub entry/path references only | `requirement.md`; `design.md`; `plan.md` S03; target docs | `README.md`; `src/spec_dock/assets/spec_dock/docs/README.md`; `spec-dock/docs/README.md` | historical evidence; implementation code; tests; skill files; canonical issue docs; runtime/manifest files; compatibility alias wording | positive/negative docs `rg`; `git diff --check`; spec-reviewer | old-name current compatibility wording required; docs surface outside design scope | changed docs; inspection results; no-compatibility wording confirmation; no-material-decision note | pass |
| S04 | delegated | test and harness expectations touch test code; parent direct implementation prohibited by workflow | dev-coder | runtime harness current skill expectation, wrapper hub-path test, focused unit expectation cleanup, and dogfooding mirror meta parity | `requirement.md`; `design.md`; `plan.md` S04; tests/harness; provider/mirror meta | `tests/cli_runtime/harness.py`; `tests/cli_runtime/test_wrappers.py`; `tests/unit/infra/test_init_update.py`; mirror `.agents/host-adapters/meta.json` only for provider parity | source/runtime/skill/docs; canonical issue docs; compatibility alias / forwarding skill / symlink; provider meta rewrite beyond already approved S02 change | wrapper pytest; focused unit pytest; `git diff --check`; `spec-dock validate`; code-reviewer | compatibility alias required; old name remains in current harness/wrapper; mirror parity cannot be restored by scoped sync | changed files; red/green evidence; old-name exception list; no-material-decision note | pass |
| S05 | not delegated | operational sync/validate plus report evidence only; no generated/runtime/docs diff remained | N/A | dogfooding sync/validate and scoped inspections | `requirement.md`; `design.md`; `plan.md` S05 | report evidence only | manual historical rewrite; compatibility alias; generated data cleanup unrelated to sync | sync; validate; diff-check; `cmp`; scoped current/historical `rg` | sync modifies canonical specs unexpectedly; old-name current reference remains outside cleanup/test exceptions | command results; allowed old-name exception list; no-op reviewer rationale | approved-no-op implementation diff |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01 | doc-writer | Renamed provider/mirror hub skill to `spec-dock-hub`, updated frontmatter/heading/description/first bullets, removed old current path, preserved provider/mirror byte parity | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-hub/SKILL.md`; `.agents/skills/spec-dock-hub/SKILL.md`; deleted old provider/mirror `spec-driven-tdd-workflow/SKILL.md` | worker and parent verification: `cmp` pass; wording `rg` pass; old-path `test ! -e` pass; `git diff --check` pass | `spec-reviewer` pass; `code-reviewer` pass with report-evidence note addressed | none for S01; downstream old-name references remain planned S02+ work | accepted |
| S02 | dev-coder | Updated installer current managed hub to `spec-dock-hub`, added old hub exact file to obsolete cleanup manifest, and updated focused unit tests / prune fixture | `src/spec_dock/cli.py`; `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json`; `tests/unit/infra/test_init_update.py` | Red focused pytest failed before S02; Green focused pytest `59 passed, 296 deselected`; `git diff --check` pass; inspection confirmed current/obsolete boundary | `code-reviewer` pass | `tests/cli_runtime/harness.py` and wrapper tests remain S04 scope; docs remain S03 scope | accepted |
| S03 | doc-writer | Updated current hub entry/path references in allowed docs from old name to `spec-dock-hub` | `README.md`; `src/spec_dock/assets/spec_dock/docs/README.md`; `spec-dock/docs/README.md` | positive `rg "spec-dock-hub"` pass; negative old-name `rg` pass; `git diff --check` pass | `spec-reviewer` pass | additional current docs discovery remains S05/S90 scope | accepted |
| S04 | dev-coder | Updated harness current skill tuple and wrapper installed hub test to `spec-dock-hub`, simplified focused unit expected managed skills to reuse harness tuple, and synchronized mirror `meta.json` to provider cleanup manifest | `.agents/host-adapters/meta.json`; `tests/cli_runtime/harness.py`; `tests/cli_runtime/test_wrappers.py`; `tests/unit/infra/test_init_update.py` | Red wrapper pytest and focused unit lane failed as expected; Green wrapper pytest `6 passed`; focused unit lane `95 passed, 260 deselected`; `git diff --check` pass; `spec-dock validate` pass | `code-reviewer` pass after report evidence fix | none; old-name references remain only cleanup metadata / prune fixtures | accepted |
| S05 | N/A | No worker used; parent ran operational sync/validate and scoped inspections, with no generated/runtime/docs diff to delegate | report evidence only | `sync` pass; `validate` pass; `git diff --check` pass; `cmp` pass; scoped `rg` pass with allowed cleanup/test exceptions | reviewer not required by plan because no generated/runtime/docs diff remained | S90 still records docs impact no-op after this inspection | accepted no-op |
| S99 fallback fix | dev-coder | Fixed broader fallback test expectations: legacy obsolete hub fixture now creates its parent directory, and checked-in dogfooding snapshot includes `iss-00184/.meta.json` with empty depends_on baseline | `tests/unit/infra/test_init_update.py` | targeted 2-test lane `2 passed`; focused lane `95 passed, 260 deselected`; broader fallback `361 passed`; `git diff --check` pass; `spec-dock validate` pass | `code-reviewer` pass | none; old-name references remain cleanup fixture only | accepted |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| none | No parent implementation exception was used for implementation/test/shipped docs changes | N/A | N/A | N/A | N/A | N/A | N/A | delegated workers performed implementation/doc/test changes; parent edited issue-local report evidence only |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| requirement | requirement phase reviewer | spec-reviewer | fresh | passed | N/A | proceed to design | Darwin `019ebaba-245a-7811-8e33-97ddb0423b71`; no findings; reviewed requirement, parent epic, report, interviews, research, and current code/docs/tests surfaces |
| design | design phase reviewer | spec-reviewer | fresh after fix | passed | N/A | proceed to plan | Ptolemy `019ebac2-471b-7592-8896-f9691a9a22d7` failed first pass with P1 finding: add install-root `host-adapters/meta.json` obsolete exact path cleanup contract; design updated accordingly; Peirce `019ebac6-5111-7222-9e74-706e45f2285e` fresh re-review passed with no findings |
| plan | plan phase reviewer | spec-reviewer | fresh after precision fixes | passed | N/A | execution handoff ready | Gauss `019ebad0-c01f-7ff2-bcfb-9f1f2688b3c5`; `review_status=pass` with P2/P3 non-blocking findings; plan updated to clarify cl-ac-004 final closure and S01 no-op gate. Hypatia `019ebad6-580b-7db3-b89c-ec5dcf3e4280`; fresh re-review passed with no findings |
| S01 | skill wording / hub-leaf boundary | spec-reviewer | fresh | passed | N/A | S01 reviewer gate passed | Franklin `019ebaf1-0ddf-70f3-8817-6083fefc121d`; no findings; confirmed `spec-dock-hub` wording and boundary |
| S01 | shipped asset path behavior | code-reviewer | fresh | passed | N/A | S01 reviewer gate passed after report evidence update | Parfit `019ebaf1-0eaf-75e0-b44f-0e7f9aee1635`; implementation pass; P2 report evidence gap addressed in this report update |
| S02 | installer/update cleanup contract | code-reviewer | fresh | passed | N/A | S02 reviewer gate passed | Lorentz `019ebafd-b1ad-7512-bbce-df69b8ee0a95`; no findings; confirmed current managed hub, obsolete exact path cleanup, no compatibility alias |
| S03 | current docs alignment | spec-reviewer | fresh | passed | N/A | S03 reviewer gate passed | Turing `019ebb06-557c-7100-82a0-7951da8ff422`; no findings; confirmed surgical docs update and no old-name current docs target matches |
| S04 | tests / harness expectations | code-reviewer | fresh before report evidence fix | failed | N/A | report evidence fix required before S04 completion | Arendt `019ebb10-4e55-75f1-b417-49204f276619`; P1 finding: S04 report evidence absent; code/test changes otherwise aligned |
| S04 | tests / harness expectations re-review | code-reviewer | fresh after report evidence fix | passed | N/A | S04 reviewer gate passed | Avicenna `019ebb15-0672-7ec2-8aa4-3653217f28ef`; no findings; confirmed harness/wrapper expectations, old-name cleanup-only references, mirror parity, and sufficient report evidence |
| S05 | dogfooding sync / current-surface inspections | N/A | approved no-op | not required | N/A | proceed to S90 | No generated/runtime/docs diff remained after sync; plan requires reviewer only if generated/runtime/docs diff is non-trivial or docs/spec references change |
| S90 | docs impact no-op | spec-reviewer | fresh | passed | N/A | proceed to S99 | Aristotle `019ebb1a-f35e-7af3-8759-aa07553b860b`; no findings; confirmed S90 no-op is consistent with requirement/design/plan and current docs show `spec-dock-hub` |
| S99 fallback test fix | code-reviewer | fresh | passed | N/A | proceed to final QA/code/spec gates after final validation | Raman `019ebb28-3bbe-7170-a62d-7ba67e3d7800`; no findings; confirmed test-only bounded fix and old hub path remains obsolete fixture only |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S01 | committed | S01 skill rename plus S01 report evidence only | S01 commit hash is post-commit external evidence; report records closure state without self-referential hash | `git status --short` after S01 commit -> clean | N/A | N/A | N/A | N/A |
| S02 | committed | S02 installer/update cleanup plus S02 report evidence only | S02 commit hash is post-commit external evidence; report records closure state without self-referential hash | `git status --short` after S02 commit -> clean | N/A | N/A | N/A | N/A |
| S03 | committed | S03 current docs references plus S03 report evidence only | S03 commit hash is post-commit external evidence; report records closure state without self-referential hash | `git status --short` after S03 commit -> clean | N/A | N/A | N/A | N/A |
| S04 | committed | S04 tests/harness expectations plus S04 report evidence only | S04 commit hash is post-commit external evidence; report records closure state without self-referential hash | `git status --short` after S04 commit -> clean | N/A | N/A | N/A | N/A |
| S05 | committed | S05 report evidence only; sync generated no tracked diff | S05 commit hash is post-commit external evidence; report records closure state without self-referential hash | `git status --short` after S05 commit -> clean | sync/validate/current-surface inspection produced no implementation diff | generated dogfooding outputs; current-surface old-name exception list; historical exclusion | `git status --short`; `git diff --check` | reviewer not required because no generated/runtime/docs diff remained |

#### 変更したファイル
- Provider / mirror skill assets: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-hub/SKILL.md`, `.agents/skills/spec-dock-hub/SKILL.md`; old current hub skill paths deleted.
- Installer / manifest / mirror metadata: `src/spec_dock/cli.py`, `src/spec_dock/assets/install_root/.agents/host-adapters/meta.json`, `.agents/host-adapters/meta.json`.
- Current docs: `README.md`, `src/spec_dock/assets/spec_dock/docs/README.md`, `spec-dock/docs/README.md`.
- Tests / harness: `tests/cli_runtime/harness.py`, `tests/cli_runtime/test_wrappers.py`, `tests/unit/infra/test_init_update.py`.
- Issue evidence: `requirement.md`, `design.md`, `plan.md`, `report.md`, and scope-local `discussions/` drafts/research/interview artifacts.

### セッションログ（2026-06-12 issue bootstrap）

#### 対象
- Step: issue creation / requirement bootstrap
- AC/EC: requirement draft only
- 計画上の出典:
  - User request on 2026-06-12
  - Parent Epic `epic-00158 Agent Workflow PDCA Hardening`
  - Completed predecessor `iss-00164 Clarify Hub And Leaf Skill Routing Surface`

#### 実施内容
- `epic-00158` 配下に `iss-00184 Rename Spec Dock Hub Skill` を作成した。
- GitHub issue `#184` が作成され、local spec node とリンクされた。
- `iss-00164` が `done` であることを確認し、この issue を hub skill naming / compatibility / reference cleanup の後続 issue として位置付けた。
- `requirement.md` を scaffold から、今回のユーザー意図・scope・acceptance criteria・未確定の命名判断が復元できる draft に更新した。

#### 実行コマンド / 結果
```bash
./spec-dock/scripts/spec-dock sync --github

pass: active unchanged; agent index/tree/deps/dashboard projections were written.
```

```bash
./spec-dock/scripts/spec-dock deps check --id iss-00164

pass: target=iss-00164 authority=github effective_status=done ready=true blockers=0.
```

```bash
./spec-dock/scripts/spec-dock new issue --epic epic-00158 --title "Rename Spec Dock Hub Skill" --slug rename-spec-dock-hub-skill

pass: id=iss-00184 github=#184; new issue auto-sync passed.
```

#### 変更したファイル
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00184-rename-spec-dock-hub-skill/requirement.md` - Issue 要件 draft を作成。
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00184-rename-spec-dock-hub-skill/report.md` - issue bootstrap の観測証跡を記録。

#### コミット
- issue bootstrap / planning commits were completed before execution handoff; execution step commits are recorded in Step Commit Gate.

#### メモ
- bootstrap evidence retained for issue creation context; no open bootstrap blocker remains.

---

### セッションログ（2026-06-12 execution summary）

#### 対象
- Step: S01-S05, S90, S99
- AC/EC: all AC / EC

#### 実施内容
- S01-S04 implemented the hub rename, installer cleanup contract, current docs references, and tests/harness expectations through delegated workers and per-step reviewer gates.
- S05/S90 recorded dogfooding sync/current-surface inspections and docs impact no-op evidence.
- S99 fixed fallback test gaps, reran final validation, and collected final reviewer gates.

---

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| docs / templates / README / workflow / skill / migration notes | no | N/A | S03 updated known current docs; S05 scoped inspection found no additional current docs old-name references; remaining old-name matches are cleanup metadata, prune fixtures, or historical `spec-dock/initiatives/**` evidence | pass: Aristotle `019ebb1a-f35e-7af3-8759-aa07553b860b` |

### 最終 QA ゲート（Final QA Gate）
| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer Hegel `019ebb2f-4deb-7042-a268-2887ad9fbfb9` | whole issue obligation coverage | already sufficient / fallback gap fixed | wrapper focused `6 passed`; focused unit `95 passed, 260 deselected`; fallback combined `361 passed`; sync/validate/diff-check/cmp/scoped rg passed | pass |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer Schrodinger `019ebb2f-7eae-73b0-941e-d3e52d9afffe` | issue-wide integrated diff | no findings; confirmed no alias/forwarding/current old discovery, provider/mirror parity, cleanup-only old-name usage, and sufficient validation evidence | 0 | pass |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer Helmholtz `019ebb2f-c283-72b0-88d7-1647b09bb39b` | requirement / design / plan / report / implementation / tests / docs alignment | fail: final gate rows were still pending and placeholder evidence remained; this report update resolves those ledger issues before re-review | 0 | fail, re-review required |
| spec-reviewer Jason `019ebb34-2d66-7c42-8635-d1f0e0ad1174` | requirement / design / plan / report / implementation / tests / docs alignment | fail: Final Commit row remained pending and residual report placeholders remained; this report update resolved placeholders and clarified the final commit row is closed after final spec pass | 1 | fail, re-review required |
| spec-reviewer James `019ebb37-ea11-7db2-9c31-bee41393fe99` | requirement / design / plan / report / implementation / tests / docs alignment | no findings; confirmed AC/EC closure evidence, placeholder cleanup, and Final Commit row closure after final spec pass | 2 | pass |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| final validation, QA/code reviewer pass, and final spec re-review pass recorded | final report evidence only | final response / PR / issue comment / other external delivery evidence | ready |

## 遭遇した問題と解決 (任意)
- 問題: S04 code-reviewer failed because S04 report evidence was not yet recorded.
  - 解決: S04 TDD / closure / reviewer / commit evidenceを report に追記し、fresh re-review pass を取得した。
- 問題: S99 fallback test revealed legacy obsolete hub fixture parent directory and checked-in dogfooding `.meta.json` snapshot gaps.
  - 解決: bounded test fixを委任し、targeted / focused / fallback tests と code-reviewer pass で確認した。
- 問題: final spec-reviewer failed because final gate rows and scaffold placeholders remained.
  - 解決: final gate rowsを実 reviewer 結果へ更新し、unused placeholder rowsを factual no-op evidenceへ置換した。

## 学んだこと (任意)
- Current-surface negative inspection must classify cleanup/test exceptions separately from historical evidence.

## 今後の推奨事項 (任意)
- Dogfooding snapshot tests are sensitive to newly created checked-in issues; future issue creation work should update or regenerate those baselines as part of final fallback validation.

## 省略/例外メモ (必須)
- 該当なし
