---
種別: 実装報告書（Issue）
ID: "iss-00246"
タイトル: "Dogfooding Update Runtime Mirror Sync"
関連GitHub: ["#246"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-30"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00246 Dogfooding Update Runtime Mirror Sync — 実装報告

この report は、Issue #246 の planning phase と execution phase で確認した証跡を記録する。実装は test hardening が中心であり、production code と package metadata は no-op とした。spec authoring review はユーザー指示により fresh spec-reviewer で実施済みである。

## 1. 仕様解釈・判断台帳

| ID | 状態 | 種別 | 起票元 | 判断 / 解釈 | 根拠 | 処置 | フォローアップ |
|---|---|---|---|---|---|---|---|
| D-001 | resolved | scope | orchestrator | Issue #246 は manual sync 手順化ではなく、`spec-dock update` と dogfooding parity が runtime mirror drift を検出または解消する契約として扱う | GitHub #246 の観測、Issue #244 research、`requirement.md` RQ-001/RQ-002 | promoted_to_requirement | none |
| D-002 | resolved | test-strategy | orchestrator | 現行 code が既に stale runtime を更新できる場合でも、subset parity の穴を閉じる test hardening を成果に含める | `design.md` DES-002、`plan.md` S02 | promoted_to_design | none |
| D-003 | resolved | operation | orchestrator | 現時点でユーザー interview は不要。残る不確実性は実装時の root-cause technical split である | `requirement.md` 8、`plan.md` 8 | no_action | none |
| D-004 | resolved | test-strategy | spec-reviewer | 初回 spec-review は plan の step-local delegation、closure index、具体テストケース schema 不足を P1 blocker とした | fresh spec-reviewer review_status=fail | promoted_to_plan | `plan.md` 5-7 を拡張し再レビュー |
| D-005 | resolved | implementation | orchestrator | S01/S03 で installer/package update は stale runtime file を provider bytes へ戻せることが確認されたため、production code と `pyproject.toml` は no-op とする | S01 focused pytest 2 passed; S03 isolated wheel smoke 1 passed | applied | none |
| D-006 | resolved | test-strategy | orchestrator | Issue #246 の再発防止上の主 defect は、checked-in dogfooding runtime parity が手書き subset で provider runtime 95 files 中 26 files しか比較していなかった coverage gap と判断する | S02 worker inspection and inventory-driven parity test | applied | none |
| D-007 | resolved | operation | spec-reviewer | S99 final gate requires dirty-tree scope evidence. `.assurance.json` is an intended PR artifact because `assurance classify/verify` binds the approved requirement/design/plan to the active issue authority. | final spec-reviewer P1 finding; `git status --short --branch` | applied | none |
| D-008 | resolved | test-strategy | code-reviewer | Runtime inventory parity should fail if both provider and mirror roots disappear. Add explicit root directory assertions before comparing inventories. | issue-wide code-reviewer P2 finding; focused parity pytest 1 passed after fix | applied | none |

## 2. 証跡採用台帳

| ID | 採用状態 | 出所 | 対象 | 判断理由 | 証跡 | 次アクション |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | GitHub issue | `requirement.md` / `design.md` / `plan.md` | Issue #246 の観測が runtime mirror drift 契約の中心根拠であるため | GitHub Issue #246 imported metadata in `.meta.json` | implementation |
| EAL-002 | adopted | research | `requirement.md` / `design.md` | Issue #244 検証で provider/dogfooding `workflow.py` drift と manual sync recovery が記録されているため | `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/discussions/20260627t154455z-research-dogfooding-runtime-update-drift-finding.md` | implementation |
| EAL-003 | adopted | command | `design.md` / `plan.md` | 現在の local tree では provider/dogfood runtime 通常 file 差分がなく、実装時は regression hardening と package/local smoke が主眼になりうるため | `diff -qr src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime spec-dock/scripts/spec_dock_runtime` showed only `__pycache__` differences | implementation |
| EAL-004 | adopted | command | `plan.md` | 現在の active Issue と dependency readiness を確認済み | `spec-dock active show`; `spec-dock deps check --id iss-00246 --github --json` ready=true | implementation |
| EAL-005 | adopted | reviewer | `plan.md` | Fresh spec-reviewer findings identify mandatory issue-plan workflow gaps; all findings were plan-contract fixes, not requirement/design changes | spec-reviewer review_status=fail with P1 findings on step-local delegation, closure index fields, concrete test schema | re-review |
| EAL-006 | adopted | command | `report.md` | S01/S03 verification demonstrates update runtime refresh works in checkout and installed wheel paths; production fix is not required | S01 focused pytest 2 passed; S03 focused pytest 1 passed | S04 closure |
| EAL-007 | adopted | command | `report.md` | S02 verification demonstrates full dogfooding runtime inventory parity and cache exclusion; old subset map coverage gap is closed | S02 focused pytest 3 passed; provider/mirror inventory 95/95 | S04 closure |
| EAL-008 | adopted | reviewer | `tests/unit/infra/test_init_update.py` | Issue-wide code review found a non-blocking parity guard weakness; adding root directory assertions improves sensitivity without changing production behavior | code-reviewer P2; `test_checked_in_dogfooding_runtime_mirror_match_provider_assets -q` -> 1 passed | final review |
| EAL-009 | adopted | command | `report.md` | Final dirty-tree scope is now explicit and contains only intended issue docs, assurance authority artifact, and test changes | `git status --short --branch` output recorded in S99 final verification | final review |

## 3. 目的整合台帳

| 対象 | 主要目的の証跡 | 副次要件の証跡 | 逆転リスク | レビュアー判定 |
|---|---|---|---|---|
| OAL-001 | `requirement.md` RQ-001/RQ-002 と `design.md` DES-001/DES-002 が runtime mirror update/parity を中心に置く | preservation/cache/package smoke は AC-003 から AC-005 に限定 | low | pass |

## 4. 仕様 authoring ゲート

| フェーズ | 調査証跡 | 未確定事項 / 回答 | 採用判断 | レビュアー判定 | ブロック有無 | 昇格 / 次アクション |
|---|---|---|---|---|---|---|
| requirement | GitHub #246、Issue #244 research、active context、existing code/test surface | ユーザー確認が必要な open question なし | adopted | pass | no | fresh spec-reviewer pass recorded |
| design | `src/spec_dock/cli.py` update structure、`pyproject.toml` package data、`tests/unit/infra/test_init_update.py` existing parity/update tests | root cause は S01-S04 で切り分け | adopted | pass | no | fresh spec-reviewer pass recorded |
| plan | `phase_plan_issue.md` / `authoring/issue-plan.md` の closure/test/delegation 契約を反映 | 初回 fail 指摘は `plan.md` に反映し、P2 report traceability nit も修正済み | adopted | pass | no | final fresh spec-reviewer pass; findings none |

## 5. 委任ドラフト証跡

| ロール | 範囲 | ドラフトパス | 参照元 | 採用状態 | ブロッカー | レビュー結果 | 昇格判断 |
|---|---|---|---|---|---|---|---|
| N/A | N/A | N/A | N/A | not_used | none | not_run | manual issue-doc authoring only |

## 6. ワークフロー委任同意の証跡

| 同意元 | repo/worktree | active issue | 指名ロール | 境界 | 拒否 / 利用不可理由 | 次アクション |
|---|---|---|---|---|---|---|
| user instruction | `/Users/iwasawayuuta/.codex/worktrees/55b2/spec-dock` | iss-00246 | spec-reviewer | read-only fresh review of requirement/design/plan; findings must be fixed and re-reviewed until pass | none | record pass/fail in this report before implementation |

## 6.1 Spec Review Gate Evidence

| Review pass | 対象 | reviewer status | findings | 修正内容 | residual risks | evidence |
|---|---|---|---|---|---|---|
| initial | `requirement.md`, `design.md`, `plan.md`, `report.md` | fail | P1: step-local delegation contracts missing; P1: closure index fields incomplete; P1: concrete test case schema incomplete | `plan.md` の closure index、S01/S02/S03/S04/S90/S99 contracts、具体テストケース、step gates を拡張 | N/A | spec-reviewer output |
| second | `requirement.md`, `design.md`, `plan.md`, `report.md` | pass | P2: report closure references used old `TC-*` labels | `report.md` Closure Coverage を `tc-s01-001` 等の現行 test IDs へ更新 | implementation-phase only | spec-reviewer output |
| final | `requirement.md`, `design.md`, `plan.md`, `report.md` | pass | none | no further changes required | S03 may need justified package-like smoke alternative; final QA/code/spec gates still need post-implementation evidence | spec-reviewer output; assurance/guidance/validate/diff-check commands pass |

## 7. 実装記録

### セッションログ（2026-06-30 planning）

#### 対象

- Step: Planning only
- AC/EC: AC-001 から AC-006 の契約化

#### 実施内容

- `issue start iss-00246` 済みの active issue context を確認した。
- `spec-dock-issue-planning` workflow と planning/authoring docs に従い、placeholder requirement/design/plan を issue-specific docs へ更新した。
- `assurance classify --stage requirement --issue iss-00246` を実行し、`authorized_profile=standard` を確認した。
- `assurance compose --artifact all --issue iss-00246` を実行し、standard skeleton を生成した。
- 生成 skeleton を Issue #246 固有の requirement/design/plan/report へ統合した。

#### 実行コマンド / 結果

```bash
./spec-dock/scripts/spec-dock assurance classify --stage requirement --issue iss-00246
# assurance classify: ok
# authorized_profile: standard

./spec-dock/scripts/spec-dock assurance compose --artifact all --issue iss-00246
# assurance compose: ok
# changed_paths: design.md, plan.md, report.md
```

#### TDD / 実装証跡

実装はまだ開始していない。Red/Green/Refactor evidence は S01 以降で記録する。

### セッションログ（2026-06-30 S01）

#### 対象

- Step: S01 stale runtime mirror refresh characterization
- AC/EC: AC-001, AC-003
- Closure: CLOS-001, CLOS-003

#### 実施内容

- `dev-coder` に S01 の bounded task を委任し、`tests/unit/infra/test_init_update.py` に focused regression test を追加した。
- temp target の `spec-dock/scripts/spec_dock_runtime/application/workflow.py` を stale bytes にして `update` を実行し、provider bytes へ戻ることを確認する。
- 同じ test で `spec-dock/initiatives/**` の user-authored issue data と root unmanaged marker が保持されることを確認する。
- Red が production defect を示さなかったため、production code は no-op とした。

#### 実行コマンド / 結果

```bash
uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_refreshes_stale_runtime_mirror_and_preserves_user_data tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_keeps_initiatives_by_default
# 2 passed
```

#### TDD / Red / Green / Refactor Evidence

| step | phase | planned evidence requirement | observed evidence | method | result | notes |
|---|---|---|---|---|---|---|
| S01 | Red alternative / characterization | red-required; existing Green acceptable with stale fixture sensitivity | new test asserts `stale_bytes != provider_bytes` and fails if stale bytes remain after update | focused pytest | pass | production defect not reproduced |
| S01 | Green | stale runtime file refreshed to provider bytes; user-authored data preserved | `test_update_refreshes_stale_runtime_mirror_and_preserves_user_data` | focused pytest | pass | CLOS-001/CLOS-003 closed |
| S01 | Refactor | no unrelated refactor | no production code change; test-only diff | diff inspection | pass | no helper refactor |

#### Step Contract Closure

| step | closure ids | close condition from plan | observed evidence | result | notes |
|---|---|---|---|---|---|
| S01 | CLOS-001, CLOS-003 | `tc-s01-001` and `tc-s01-002` pass; production code change/no-op recorded | focused pytest 2 passed; production no-op | pass | code-reviewer pass |

#### Test Contract Closure

| closure id / test id | step | required | evidence level | pre-implementation evidence | verification command | observed result | notes |
|---|---|---|---|---|---|---|---|
| CLOS-001 / `tc-s01-001` | S01 | yes | focused pytest / CLI-like unit | stale fixture sensitivity | `uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_refreshes_stale_runtime_mirror_and_preserves_user_data` | pass | target runtime bytes match provider bytes |
| CLOS-003 / `tc-s01-002` | S01 | yes | focused pytest plus existing preservation regression | user-authored issue data and unmanaged marker fixture | same focused pytest plus `test_update_keeps_initiatives_by_default` | pass | preservation guard retained |

#### Delegated Worker Evidence

| step | delegated role | delegated worker summary | changed files | tests run | reviewer verdict | unresolved risks | parent integration decision |
|---|---|---|---|---|---|---|---|
| S01 | dev-coder | Added stale runtime refresh + preservation focused test. Production code no-op. No material implementation decisions beyond the approved plan. | `tests/unit/infra/test_init_update.py` | focused pytest 1 passed; combined focused pytest 2 passed; `git diff --check -- tests/unit/infra/test_init_update.py` pass | code-reviewer pass | S02/S03 remain open by plan | accepted |

#### Reviewer Gate Status

| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| S01 | step reviewer | code-reviewer | fresh | passed | N/A | proceed | no findings; reviewer relied on parent pytest evidence |

#### 変更したファイル

- `tests/unit/infra/test_init_update.py` - stale runtime mirror refresh and preservation regression test

### セッションログ（2026-06-30 S02）

#### 対象

- Step: S02 checked-in dogfooding runtime parity inventory
- AC/EC: AC-002, AC-004
- Closure: CLOS-002, CLOS-004

#### 実施内容

- `dev-coder` に S02 の bounded task を委任し、手書き subset map を provider/dogfooding runtime inventory 由来の比較へ置換した。
- `_runtime_inventory` を追加し、`__pycache__`、`.pyc`、`.pyo` を generated cache として除外する。
- provider runtime inventory と checked-in dogfooding mirror inventory の relative path set equality と byte equality を検証する。
- 現在の checked-in dogfooding mirror は provider と一致していたため、runtime mirror file は変更しなかった。

#### 実行コマンド / 結果

```bash
uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_mirror_match_provider_assets tests/unit/infra/test_init_update.py::TestInitUpdate::test_dogfooding_runtime_inventory_excludes_generated_python_caches tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_does_not_copy_generated_python_caches_from_provider_assets
# 3 passed
```

#### TDD / Red / Green / Refactor Evidence

| step | phase | planned evidence requirement | observed evidence | method | result | notes |
|---|---|---|---|---|---|---|
| S02 | Characterization | old subset map leak should be made visible | old handwritten map covered 26 of 95 provider runtime files; old parity test still passed | worker inspection | pass | 69 files were not covered by old map |
| S02 | Green | provider/dogfood runtime path set and bytes match with cache exclusion | inventory-driven parity test and cache helper test | focused pytest | pass | provider inventory 95, mirror inventory 95, no drift |
| S02 | Refactor | avoid stale handwritten map | `_DOGFOODING_RUNTIME_MIRROR_PROVIDER_ASSET_MAP` removed; `_runtime_inventory` added | diff inspection | pass | test-only change |

#### Step Contract Closure

| step | closure ids | close condition from plan | observed evidence | result | notes |
|---|---|---|---|---|---|
| S02 | CLOS-002, CLOS-004 | `tc-s02-001` and `tc-s02-002` pass; generated cache exclusion recorded | focused pytest 3 passed; code-reviewer pass | pass | no dogfooding mirror file changes |

#### Test Contract Closure

| closure id / test id | step | required | evidence level | pre-implementation evidence | verification command | observed result | notes |
|---|---|---|---|---|---|---|---|
| CLOS-002 / `tc-s02-001` | S02 | yes | focused pytest / inspection | old map covered 26/95 runtime files | `uv run pytest ...test_checked_in_dogfooding_runtime_mirror_match_provider_assets` | pass | path set and bytes parity from inventory |
| CLOS-004 / `tc-s02-002` | S02 | yes | focused pytest / structural inspection | generated cache exclusion required by plan | `uv run pytest ...test_dogfooding_runtime_inventory_excludes_generated_python_caches ...test_update_does_not_copy_generated_python_caches_from_provider_assets` | pass | `__pycache__`, `.pyc`, `.pyo` excluded |

#### Delegated Worker Evidence

| step | delegated role | delegated worker summary | changed files | tests run | reviewer verdict | unresolved risks | parent integration decision |
|---|---|---|---|---|---|---|---|
| S02 | dev-coder | Replaced handwritten runtime subset parity with inventory-driven parity and generated cache exclusion. No material implementation decisions beyond the approved plan. | `tests/unit/infra/test_init_update.py` | focused pytest 2 passed; generated-cache update pytest 1 passed | code-reviewer pass | S03 package/local smoke remains open | accepted |

#### Reviewer Gate Status

| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| S02 | step reviewer | code-reviewer | fresh | passed | N/A | proceed | no findings; reviewer relied on parent pytest evidence |

#### 変更したファイル

- `tests/unit/infra/test_init_update.py` - inventory-driven runtime mirror parity and generated cache exclusion test

### セッションログ（2026-06-30 S03）

#### 対象

- Step: S03 local checkout/package update smoke
- AC/EC: AC-005
- Closure: CLOS-005

#### 実施内容

- `dev-coder` に S03 の bounded task を委任し、既存 Issue 69 系の hermetic wheel/install helper を再利用した package-like smoke を追加した。
- isolated wheel install された `spec-dock` command で target repo を `init` し、target runtime file を stale bytes に変更した。
- 同じ installed/package-like command の `update` で `workflow.py` が provider bytes に戻ることを byte-level で確認した。
- installed package snapshot assertion により checkout fallback を使っていないことを確認した。
- 追加 test が Green だったため、`pyproject.toml` / package metadata は no-op とした。

#### 実行コマンド / 結果

```bash
uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_246_isolated_wheel_update_refreshes_stale_runtime_file
# 1 passed
```

#### TDD / Red / Green / Refactor Evidence

| step | phase | planned evidence requirement | observed evidence | method | result | notes |
|---|---|---|---|---|---|---|
| S03 | Characterization | package-like path should prove stale runtime refresh; existing S01/Issue69 tests did not combine both assertions | new test uses local wheel build + isolated installed command + stale runtime file | focused pytest | pass | full package-like smoke chosen; no alternative needed |
| S03 | Green | installed/package-like update refreshes stale runtime file to provider bytes | `test_issue_246_isolated_wheel_update_refreshes_stale_runtime_file` | focused pytest | pass | checkout fallback excluded by snapshot assertion |
| S03 | Refactor | no package metadata change unless defect observed | `pyproject.toml` unchanged | diff inspection | pass | package data defect not observed |

#### Step Contract Closure

| step | closure ids | close condition from plan | observed evidence | result | notes |
|---|---|---|---|---|---|
| S03 | CLOS-005 | `tc-s03-001` or approved equivalent pass; selected evidence path recorded | focused package-like isolated wheel smoke 1 passed | pass | full package-like smoke, no alternative path |

#### Test Contract Closure

| closure id / test id | step | required | evidence level | pre-implementation evidence | verification command | observed result | notes |
|---|---|---|---|---|---|---|---|
| CLOS-005 / `tc-s03-001` | S03 | yes | package-like smoke | existing S01 covered checkout update and Issue69 covered isolated init/update, but stale runtime byte refresh in package-like path was missing | `uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_246_isolated_wheel_update_refreshes_stale_runtime_file` | pass | installed wheel update restores stale `workflow.py` to provider bytes |

#### Delegated Worker Evidence

| step | delegated role | delegated worker summary | changed files | tests run | reviewer verdict | unresolved risks | parent integration decision |
|---|---|---|---|---|---|---|---|
| S03 | dev-coder | Added isolated wheel/package-like stale runtime refresh test. `pyproject.toml` no-op. No material implementation decisions beyond the approved plan. | `tests/unit/infra/test_init_update.py` | focused S03 pytest 1 passed; supporting 3-test selection 3 passed | code-reviewer pass after report evidence update | test path uses one representative runtime file by design | accepted |

#### Reviewer Gate Status

| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| S03 | step reviewer | code-reviewer | fresh | passed | N/A | proceed | initial fail was report-evidence-only; re-review passed after CLOS-005 evidence update |

#### 変更したファイル

- `tests/unit/infra/test_init_update.py` - isolated wheel/package-like stale runtime refresh smoke

### セッションログ（2026-06-30 S04）

#### 対象

- Step: S04 production defect / no-op root-cause closure
- AC/EC: AC-006
- Closure: CLOS-006 implementation-decision portion

#### 実施内容

- S01/S03 の結果により、direct checkout update と installed wheel/package-like update の両方で stale runtime file が provider bytes へ戻ることを確認した。
- `src/spec_dock/cli.py` と `pyproject.toml` の production/package metadata defect は観測されなかったため no-op とした。
- S02 の結果により、checked-in dogfooding runtime parity の旧手書き map が provider runtime 95 files 中 26 files のみを比較していたことを確認し、inventory-driven parity へ置換した。
- root cause classification を `test coverage gap / parity subset gap` として記録した。

#### 実行コマンド / 結果

```bash
uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_refreshes_stale_runtime_mirror_and_preserves_user_data tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_mirror_match_provider_assets tests/unit/infra/test_init_update.py::TestInitUpdate::test_dogfooding_runtime_inventory_excludes_generated_python_caches tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_246_isolated_wheel_update_refreshes_stale_runtime_file
# 4 passed
```

#### Step Contract Closure

| step | closure ids | close condition from plan | observed evidence | result | notes |
|---|---|---|---|---|---|
| S04 | CLOS-006 | root cause classification and code/no-op decision recorded | production/package metadata no-op; parity subset gap fixed in tests | pass | no plan amendment required |

#### Test Contract Closure

| closure id / test id | step | required | evidence level | pre-implementation evidence | verification command or alternative path | observed result | notes |
|---|---|---|---|---|---|---|---|
| CLOS-006 / `tc-s04-001` | S04 | yes | docs inspection / focused pytest evidence | S01-S03 pass evidence | report decision ledger inspection | pass | root cause and no-op rationale recorded |

#### Reviewer Gate Status

| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| S04 | step reviewer | spec-reviewer | pending | not_run | N/A | run at S99 | S04 changes are report/closure evidence; final spec-reviewer checks issue-wide closure |

### セッションログ（2026-06-30 S90）

#### 対象

- Step: S90 docs / workflow impact resolution
- AC/EC: AC-006
- Closure: CLOS-006 docs impact portion

#### 実施内容

- S01-S03 の実装差分を確認し、public CLI command / argument / workspace layout / operator-visible diagnostic は変更していないことを確認した。
- production code と `pyproject.toml` は no-op で、変更は `tests/unit/infra/test_init_update.py` と issue docs/report の証跡更新に閉じている。
- したがって persistent docs/templates/skills/workflow text の更新は不要と判断した。

#### 代替検証 / 結果

| step | phase | planned evidence requirement | observed evidence | method | result | notes |
|---|---|---|---|---|---|---|
| S90 | inspect-only | docs impact resolved by no-op rationale or docs diff | no public CLI/docs contract change; no operator-visible diagnostic added | diff inspection | pass | doc-writer delegation not required |

#### Step Contract Closure

| step | closure ids | close condition from plan | observed evidence | result | notes |
|---|---|---|---|---|---|
| S90 | CLOS-006 | docs no-op or docs update evidence recorded | docs no-op rationale recorded | pass | final spec-reviewer to check at S99 |

#### Reviewer Gate Status

| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| S90 | docs/spec alignment | spec-reviewer | pending | not_run | N/A | run at S99 | no persistent docs update required |

### セッションログ（2026-06-30 S99 discovered repair）

#### 対象

- Step: S99 final gate discovered test repair
- Test: `test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json`
- Closure: CLOS-006 final evidence hygiene

#### 発見事項

`uv run pytest tests/unit/infra/test_init_update.py -q` の初回実行で `test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json` が失敗した。原因は、Issue #246 import により checked-in dogfooding initiatives tree に `iss-00246` の `.meta.json` が追加された一方、test snapshot `_CHECKED_IN_DOGFOODING_META_JSON_PATHS` と `_CHECKED_IN_DOGFOODING_DEPENDS_ON_BY_META_PATH` が未更新だったことである。

#### 実施内容

- `dev-coder` に discovered repair を委任した。
- `tests/unit/infra/test_init_update.py` の checked-in dogfooding `.meta.json` snapshot に `iss-00246` の `.meta.json` path を追加した。
- 同じ path を `depends_on=[]` として depends-on baseline に追加した。
- runtime/source behavior は変更していない。

#### 実行コマンド / 結果

```bash
uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json -q
# 1 passed
```

#### Delegated Worker Evidence

| step | delegated role | delegated worker summary | changed files | tests run | reviewer verdict | unresolved risks | parent integration decision |
|---|---|---|---|---|---|---|---|
| S99 repair | dev-coder | Updated checked-in dogfooding meta snapshot and depends_on baseline for imported iss-00246. | `tests/unit/infra/test_init_update.py` | focused failing test 1 passed | pending final review | snapshot could mask unintended import; mitigated by confirming actual iss-00246 `.meta.json` | accepted |

### セッションログ（2026-06-30 S99 final verification）

#### 対象

- Step: S99 final quality gate
- Closure: CLOS-001 through CLOS-006

#### 実行コマンド / 結果

```bash
uv run pytest tests/unit/infra/test_init_update.py -q
# 530 passed in 322.38s

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=156

./spec-dock/scripts/spec-dock sync
# spec-dock: ok (sync)

./spec-dock/scripts/spec-dock assurance verify --issue iss-00246
# assurance verify: ok

git diff --check
# pass

git status --short --branch
# ## iss-00246-dogfooding-update-runtime-mirror-sync
#  M spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00246-dogfooding-update-runtime-mirror-sync/design.md
#  M spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00246-dogfooding-update-runtime-mirror-sync/plan.md
#  M spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00246-dogfooding-update-runtime-mirror-sync/report.md
#  M spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00246-dogfooding-update-runtime-mirror-sync/requirement.md
#  M tests/unit/infra/test_init_update.py
# ?? spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00246-dogfooding-update-runtime-mirror-sync/.assurance.json
```

#### Dirty-tree scope decision

| path | scope decision | rationale |
|---|---|---|
| `spec-dock/active/issue/requirement.md` | intended | Issue #246 requirement authored and reviewed |
| `spec-dock/active/issue/design.md` | intended | Issue #246 design authored and reviewed |
| `spec-dock/active/issue/plan.md` | intended | Issue #246 execution plan authored, reviewed, and amended for reviewer findings |
| `spec-dock/active/issue/report.md` | intended | Observed evidence ledger for S01-S99 |
| `spec-dock/active/issue/.assurance.json` | intended | Generated assurance authority binding for approved issue artifacts; required by `assurance verify` / guidance |
| `tests/unit/infra/test_init_update.py` | intended | Regression tests and checked-in dogfooding snapshot updates for Issue #246 |

#### Reviewer follow-up fixes

| reviewer | finding | fix | verification |
|---|---|---|---|
| code-reviewer | P2: runtime parity could pass if both roots disappeared | added explicit `provider_root.is_dir()` and `mirror_root.is_dir()` assertions | `uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_mirror_match_provider_assets -q` -> 1 passed |
| spec-reviewer | P1: final gate lacked `git status --short` evidence and `.assurance.json` scope decision | recorded dirty-tree status and marked `.assurance.json` as intended assurance artifact | pending re-review |
| spec-reviewer | final re-review | no further changes required | pass |

#### Step Contract Closure

| step | closure ids | close condition from plan | observed evidence | result | notes |
|---|---|---|---|---|---|
| S99 | CLOS-001, CLOS-002, CLOS-003, CLOS-004, CLOS-005, CLOS-006 | required commands pass; report has closure coverage and final quality evidence | `test_init_update.py` full file 530 passed; validate/sync/assurance/diff-check pass | pass | reviewer gates pending |

### セッションログ（2026-06-30 PR repair U001）

#### 対象

- PR: https://github.com/chemitaro/spec-dock/pull/249
- Step: PR merge-preparer repair loop
- Repair batch: `discussions/20260630t083605z-pr-repair-batch-pr-repair-batch.md`
- Repair unit: `discussions/20260630t083631z-disc-pr-repair-unit-u001-check-failure-provider-tests.md`

#### 発見事項

PR observation が latest head `6d9d8aa243e3323141046c58f14292c1b1b6e961` に対して `overall_status=failed` / `recommended_next_action=fix_ci` を返した。GitHub Actions `Provider CI / provider-tests` の `Run provider static analysis` で `ruff format check` が失敗し、`tests/unit/infra/test_init_update.py` が `1 file would be reformatted` と報告された。

#### 実施内容

- `dev-coder` に formatting-only repair を委任した。
- `uv run ruff format tests/unit/infra/test_init_update.py` 相当の単一ファイル整形のみを適用した。
- production code、issue canonical docs、PR body は変更していない。
- PR repair batch と repair unit を生成し、`check_failure:provider-tests` として triage した。

#### 実行コマンド / 結果

```bash
uv run ruff format --check tests/unit/infra/test_init_update.py
# 1 file already formatted

uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_refreshes_stale_runtime_mirror_and_preserves_user_data tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_246_isolated_wheel_update_refreshes_stale_runtime_file tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_mirror_match_provider_assets -q
# 3 passed in 3.94s

git diff --check
# pass
```

#### Delegated Worker Evidence

| step | delegated role | delegated worker summary | changed files | tests run | reviewer verdict | unresolved risks | parent integration decision |
|---|---|---|---|---|---|---|---|
| PR repair U001 | dev-coder | Applied formatting-only repair for CI `ruff format check` failure. | `tests/unit/infra/test_init_update.py` | `ruff format --check` pass; focused Issue 246 tests 3 passed; `git diff --check` pass | pending latest-head PR observation | latest-head CI/review re-observation still required | accepted |

## 8. Closure Coverage

| Closure ID | 状態 | 現在の証跡 | 次アクション |
|---|---|---|---|
| CLOS-001 | closed | S01 focused pytest / `tc-s01-001` | update stale runtime refresh covered |
| CLOS-002 | closed | S02 focused pytest / `tc-s02-001` | inventory-driven runtime parity covered |
| CLOS-003 | closed | S01 focused pytest / `tc-s01-002` | user-authored data and unmanaged marker preservation covered |
| CLOS-004 | closed | S02 focused pytest / `tc-s02-002` | generated cache exclusion covered |
| CLOS-005 | closed | S03 focused pytest / `tc-s03-001` | package-like isolated wheel update smoke covered |
| CLOS-006 | closed | S04 decision ledger / `tc-s04-001`; S90 docs no-op; S99 commands and reviewer gates pass | root cause/no-op, docs impact, final command evidence, and final reviewer evidence recorded |

## 9. Final Quality Gate

| Gate | 状態 | 証跡 | 次アクション |
|---|---|---|---|
| spec authoring | pass | `requirement.md`, `design.md`, `plan.md`, `report.md`; final spec-reviewer findings none | implementation phase may start subject to issue execution workflow gates |
| QA | pass | `uv run pytest tests/unit/infra/test_init_update.py -q` -> 530 passed in 322.38s; qa-reviewer findings none | residual risk limited to implementation-phase smoke representativeness |
| code review | pass | issue-wide code-reviewer findings none after P2 root assertion fix | no remaining code-review findings |
| spec review | pass | final spec-reviewer findings none after dirty-tree scope evidence fix | no unresolved spec gaps |
| validation | pass | `spec-dock validate`, `spec-dock sync`, `assurance verify`, `git diff --check` passed | none |

## 10. 変更したファイル

- `spec-dock/active/issue/requirement.md` - Issue #246 の要件・受け入れ条件を定義
- `spec-dock/active/issue/design.md` - runtime mirror update/parity の設計差分を定義
- `spec-dock/active/issue/plan.md` - TDD/closure/test/delegation plan を定義
- `spec-dock/active/issue/report.md` - planning phase の evidence ledger を定義
