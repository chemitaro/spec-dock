---
種別: 実装報告書（Issue）
ID: "iss-00088"
タイトル: "Issue lifecycle start and finish commands"
関連GitHub: ["#88"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-05-06"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00054", "init-local-00002"]
---

# iss-00088 Issue lifecycle start and finish commands — 実装報告（LOG）

## 実装サマリー
- 実装完了。`issue start` / `issue finish` の guided lifecycle command、provider/docs/skill/mirror 更新、targeted tests、full regression、`validate`、`sync --github` を完了した。
- `issue start -f` は unfinished active issue guard のみを bypass し、dependency/readiness checks は bypass しない契約として実装・テストした。
- `active set` / `active set --checkout` は manual / recovery command として既存 contract を維持した。

## 実装記録（セッションログ）

### 2026-05-05 spec authoring

#### 対象
- Step: S00
- AC/EC:
  - SG1 baseline

#### 実施内容
- `spec-dock/active/issue/requirement.md` を確認し、`issue start` / `issue finish` Phase 1 の目的、scope、acceptance criteria、edge cases を確認した。
- `spec-dock/active/issue/design.md` を scaffold から issue 固有の設計へ更新した。
- `spec-dock/active/issue/plan.md` を scaffold から Spec-Locked Closure Index 付きの execution contract へ更新した。
- `spec-dock/active/issue/report.md` を本 issue 固有の execution log として初期化した。

#### 実行コマンド / 結果
```bash
pwd && git branch --show-current && git status --short && ./spec-dock/scripts/spec-dock active show

/Users/iwasawayuuta/workspace/tools/spec-dock
iss-00088-issue-lifecycle-start-and-finish-commands
initiative: init-local-00002 (spec-dock/initiatives/init-local-00002-prototype-feature-expansion)
epic: epic-00054 (spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00054-github-lifecycle-command-expansion)
issue: iss-00088 (spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00054-github-lifecycle-command-expansion/issues/iss-00088-issue-lifecycle-start-and-finish-commands)
```

#### Step Contract Closure
| step | closure ids | close condition | evidence | result | notes |
|---|---|---|---|---|---|
| S00 | SG1 baseline | issue docs are implementation-ready after spec review | spec-reviewer pass after P1 fixes | pass | ready for implementation |

#### Test Contract Closure
| closure id / test id | step | required | evidence level | pre-implementation evidence | verification command | result | notes |
|---|---|---|---|---|---|---|---|
| SG1 baseline | S00 | yes | inspect-only | N/A | spec-reviewer pass | pass | docs/skill implementation still pending |

#### Closure Coverage
| closure id | step | verification evidence | result | notes |
|---|---|---|---|---|
| SG1 baseline | S00 | design/plan/report authored and re-reviewed | pass | implementation handoff approved |

#### Closure Delta
| change | closure id | test id alias | resolves to closure id | reason | re-review required |
|---|---|---|---|---|---|
| none | lc-007 | lc-007 | lc-007 | initial contract | yes |

#### 変更したファイル
- `spec-dock/active/issue/design.md` - issue-specific design
- `spec-dock/active/issue/plan.md` - issue-specific execution contract
- `spec-dock/active/issue/report.md` - initial report evidence

#### コミット
- 未実施

#### メモ
- Implementation must not begin until SG1 spec review passes.

### 2026-05-05 implementation and verification

#### 対象
- Steps:
  - S01 application lifecycle contract and guard
  - S02 CLI `issue start`
  - S03 CLI `issue finish`
  - S90 docs impact resolution / docs refresh
  - S99 final diff review quality gate
- AC/EC:
  - AC-001
  - AC-002
  - AC-003
  - AC-004
  - AC-005
  - AC-006
  - AC-007
  - EC-001
  - EC-002
  - EC-003
  - EC-004
  - EC-005

#### 実施内容
- `spec-dock issue start` / `spec-dock issue finish` command group を追加した。
- `issue start` は issue node のみを対象にし、active set と checkout を一操作で行う。
- unfinished active issue branch から別 issue を start する場合、GitHub state が `CLOSED` でない、または確認不能で、`-f` がないときは active mutation / checkout の前に block する。
- `-f` / `--force` は lifecycle guard だけを bypass し、dependency/readiness check は `set_active(force=False)` として維持した。
- `main` / `master` / `develop` / `staging` / non-issue branch からの start と same issue restart は block しない。
- `issue finish` は active issue の linked GitHub issue を close し、already-closed を success として扱い、その成功後だけ active state を clear する。
- `issue finish` の no active / no GitHub linkage / stale active node / GitHub state or close failure は active state を保持し、recovery guidance と raw reason を表示する。
- `issue finish` は lifecycle closure のみであり、commit / push / PR / merge / validate / test / review completion を保証しないことを docs/skill に明記した。
- provider runtime と dogfooding runtime mirror、provider docs と dogfooding docs、provider skill と checked-in skill mirror を同期した。
- checked-in dogfooding `iss-00088` の `.meta.json` 追加に合わせ、cutover snapshot test constants を更新した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.cli_runtime.test_issue_lifecycle
# Ran 14 tests in 15.322s
# OK

python -m unittest tests.cli_runtime.test_close tests.cli_runtime.test_active
# Ran 40 tests in 24.645s
# OK

python -m unittest tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_subprocess_validate_and_sync_on_cutover_snapshot tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_subprocess_deps_mutation_on_cutover_snapshot
# Ran 3 tests in 1.043s
# OK

python -m unittest tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_mirror_match_provider_assets tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_surface_includes_doctor_and_explicit_target_hint
# Ran 2 tests in 0.158s
# OK

python -m unittest tests.test_init_update.TestInitUpdate.test_workflow_issue_doc_matches_bundled_asset tests.test_init_update.TestInitUpdate.test_current_guidance_documents_match_discussion_numbering_contract tests.cli_runtime.test_wrappers.TestCliRulesContract.test_scaffold_docs_point_to_runtime_commands_and_rules_docs
# Ran 3 tests in 0.090s
# OK

python -m compileall -q src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime spec-dock/scripts/spec_dock_runtime tests/cli_runtime/test_issue_lifecycle.py
# exit 0

python -m unittest discover -v
# Ran 762 tests in 222.915s
# OK

./spec-dock/scripts/spec-dock issue --help
# exposes issue start / issue finish

./spec-dock/scripts/spec-dock issue start --help
# exposes --id, --github-issue, -f/--force, --gh-limit
# -f help states dependency readiness checks still apply

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=37

./spec-dock/scripts/spec-dock sync --github
# spec-dock: sync: active unchanged (matched id in branch: iss-00088)
# spec-dock: ok (sync) wrote=spec-dock/.agent/index-all.json,...

git diff --check
# no output

diff -ru -x __pycache__ src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime spec-dock/scripts/spec_dock_runtime
# no output

diff -u src/spec_dock/assets/spec_dock/docs/workflow_issue.md spec-dock/docs/workflow_issue.md
diff -u src/spec_dock/assets/spec_dock/docs/workflow-tree.md spec-dock/docs/workflow-tree.md
diff -u src/spec_dock/assets/spec_dock/docs/reference_github.md spec-dock/docs/reference_github.md
diff -u src/spec_dock/assets/spec_dock/docs/reference_naming.md spec-dock/docs/reference_naming.md
diff -u src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md .agents/skills/spec-dock-issue-execution/SKILL.md
# no output
```

#### Step Contract Closure
| step | closure ids | close condition | evidence | result | notes |
|---|---|---|---|---|---|
| S01 | lc-001, lc-002, lc-003, lc-004, lc-008 | application lifecycle guard and force scope implemented | `tests.cli_runtime.test_issue_lifecycle` pass | pass | `-f` does not bypass dependency guard |
| S02 | lc-001, lc-002, lc-003, lc-004 | CLI `issue start` parser/output/action paths implemented | CLI help + lifecycle tests pass | pass | block message includes recovery commands |
| S03 | lc-005, lc-006 | CLI `issue finish` close/clear ordering implemented | finish tests pass | pass | failure paths leave active unchanged |
| S90 | lc-007 | docs/skill primary path updated and mirrored | docs/skill grep + mirror diffs clean | pass | `active set` documented as manual/recovery |
| S99 | lc-001..lc-008 | final validation, sync, parity, and regression pass | full suite, validate, sync, parity checks, spec/code/QA review pass | pass | final review gate closed; QA P2 workflow-tree follow-up resolved |

#### Test Contract Closure
| closure id / test id | step | required | evidence level | pre-implementation evidence | verification command | result | notes |
|---|---|---|---|---|---|---|---|
| lc-001 | S01/S02 | yes | red-required | command/use case absent before implementation | `python -m unittest tests.cli_runtime.test_issue_lifecycle` | pass | start sets active and checks out issue branch |
| lc-002 | S01/S02 | yes | red-required | command/use case absent before implementation | `python -m unittest tests.cli_runtime.test_issue_lifecycle` | pass | open/unknown unfinished guard blocks before mutation |
| lc-003 | S01/S02 | yes | red-required | command/use case absent before implementation | `python -m unittest tests.cli_runtime.test_issue_lifecycle` | pass | force bypasses lifecycle guard only, dependency guard still blocks |
| lc-004 | S01/S02 | yes | red-required | command/use case absent before implementation | `python -m unittest tests.cli_runtime.test_issue_lifecycle` | pass | main branch and same issue restart do not block |
| lc-005 | S03 | yes | red-required | command/use case absent before implementation | `python -m unittest tests.cli_runtime.test_issue_lifecycle` | pass | close/already-closed success clears active |
| lc-006 | S03 | yes | red-required | command/use case absent before implementation | `python -m unittest tests.cli_runtime.test_issue_lifecycle` | pass | no active/no link/close failure leave active unchanged |
| lc-007 | S90 | yes | inspect-only | docs/skill did not name lifecycle commands as primary path | docs grep + provider/mirror diffs | pass | workflow/reference/skill updated |
| lc-008 | S99 | yes | covered-existing | active set regression suite existed | `python -m unittest tests.cli_runtime.test_close tests.cli_runtime.test_active` and full suite | pass | direct active set contract unchanged |

#### Closure Coverage
| closure id | step | verification evidence | result | notes |
|---|---|---|---|---|
| lc-001 | S01/S02 | lifecycle tests, CLI help, full suite | pass | issue-only target and checkout covered |
| lc-002 | S01/S02 | lifecycle block test | pass | no active file / branch mutation on block |
| lc-003 | S01/S02 | force + dependency-not-ready test | pass | force scope constrained |
| lc-004 | S01/S02 | main branch / same issue restart test | pass | emergency/non-issue branch work remains possible |
| lc-005 | S03 | finish open/already-closed tests | pass | active clear after success |
| lc-006 | S03 | finish failure tests | pass | active unchanged on failures; recovery guidance asserted for missing link, stale node, state failure, and close failure |
| lc-007 | S90 | docs/skill/README/workflow update and mirror diff | pass | primary path wording and delivery non-guarantee present; delivery completion is before `issue finish` |
| lc-008 | S99 | active/close/lifecycle regression and full suite | pass | direct active set bypass test confirms guard did not leak into `active set` |

#### 変更したファイル
- `.agents/skills/spec-dock-issue-execution/SKILL.md`
- `README.md`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
- `src/spec_dock/assets/spec_dock/docs/README.md`
- `src/spec_dock/assets/spec_dock/docs/guide.md`
- `src/spec_dock/assets/spec_dock/docs/github.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
- `src/spec_dock/assets/spec_dock/docs/workflow-tree.md`
- `src/spec_dock/assets/spec_dock/docs/reference_github.md`
- `src/spec_dock/assets/spec_dock/docs/reference_naming.md`
- `spec-dock/docs/README.md`
- `spec-dock/docs/guide.md`
- `spec-dock/docs/github.md`
- `spec-dock/docs/workflow_issue.md`
- `spec-dock/docs/workflow-tree.md`
- `spec-dock/docs/reference_github.md`
- `spec-dock/docs/reference_naming.md`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_lifecycle.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/issue.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py`
- `spec-dock/scripts/spec_dock_runtime/application/contracts.py`
- `spec-dock/scripts/spec_dock_runtime/application/issue_lifecycle.py`
- `spec-dock/scripts/spec_dock_runtime/commands/issue.py`
- `spec-dock/scripts/spec_dock_runtime/cli/bootstrap.py`
- `spec-dock/scripts/spec_dock_runtime/cli/parser.py`
- `spec-dock/scripts/spec_dock_runtime/cli/registry.py`
- `spec-dock/scripts/spec_dock_runtime/presentation/cli_text.py`
- `tests/cli_runtime/test_issue_lifecycle.py`
- `tests/test_init_update.py`
- `spec-dock/active/issue/design.md`
- `spec-dock/active/issue/plan.md`
- `spec-dock/active/issue/report.md`

#### コミット
- 未実施

#### メモ
- `compileall` 実行により `__pycache__` が生成されたが、git status には出ない ignored artifact である。runtime mirror parity は `-x __pycache__` を付けて source file 同士で確認した。
- `sync --github` は generated state を更新したが、tracked diff は発生しなかった。
- QA/spec/code review findings after implementation passes were resolved:
  - report final closure evidence was added.
  - finish failure recovery guidance was added and tested.
  - UNKNOWN GitHub state blocking and arbitrary non-issue branch start were added to lifecycle tests.
  - docs/skill now state that `issue finish` does not guarantee delivery completion.
  - entry docs (`README.md`, `guide.md`, `github.md`) now point normal issue execution at `issue start` / `issue finish`.
  - `issue start` allows switching from a completed active issue branch when GitHub state is `CLOSED`.
  - `issue finish` clear-active failure now includes recovery guidance after remote close success.
  - design/report/reference naming ambiguity around `issue start --github` was removed; `issue start` remains issue-only and has no Phase 1 `--github` opt-in.
  - QA P2/P3 coverage findings were resolved by adding `test_direct_active_set_checkout_bypasses_issue_lifecycle_guard` and asserting no-active finish recovery guidance.
  - code-review P2 mirror-parity finding was resolved by adding lifecycle runtime files to the checked-in provider/mirror parity test map.
  - spec-review P1 docs findings were resolved by documenting `issue start` / `issue finish` in root `README.md`, removing the skill contradiction that required active state after finish, and aligning `workflow_issue.md` completion wording with active clear.
  - final QA P2 stale `workflow-tree.md` guidance was resolved by making `issue start` / `issue finish` the primary lifecycle path and demoting `active set` to manual/recovery/no-checkout guidance in provider and dogfooding docs.
- Final review gate:
  - spec-reviewer pass: no P0/P1 specification blockers or material cross-artifact contradictions.
  - code-reviewer pass: no findings; guarded start, direct active set separation, force scope, unknown-state fail-closed handling, finish recovery paths, and mirror parity coverage reviewed.
  - QA-reviewer pass: no P0/P1; P2 stale `workflow-tree.md` guidance was addressed after review.
  - final spec re-review pass: S99 `pending-review` contradiction resolved; no P0/P1 blockers remain.
  - spec-review P1 docs findings were resolved by documenting `issue start` / `issue finish` in root `README.md`, removing the skill contradiction that required active state after finish, and aligning `workflow_issue.md` completion wording with active clear.
- Manual test:
  - report directory: `manual-tests/reports/2026-05-05-iss-00088-issue-lifecycle/`
  - workspace: `manual-tests/workspaces/2026-05-05-iss-00088-issue-lifecycle/repo`
  - GitHub repo: `chemitaro/spec-dock-manual-iss-00088-lifecycle`
  - verdict: pass
  - covered real GitHub-backed `issue start`, unfinished branch guard, `-f` dependency readiness preservation, direct `active set --checkout` manual/recovery boundary, non-issue branch start, `issue finish` close+active clear, already-closed finish, and recovery guidance with active preservation.
  - final health: `validate` ok (`nodes=7`), `sync --github` ok, `doctor` ok (`findings=0`), and all temporary GitHub issues were closed.
  - operational observation: after `issue finish`, the current Git branch remains on the issue branch; running `sync --github` there can restore active from the branch name, so final cleanup should switch to `main` or another non-issue branch before sync when active should remain clear.

## 遭遇した問題と解決
- 2026-05-07 skill external review and remediation:
  - consultant verdict: conditional_pass.
    - finding: skill reminder should state that `issue start -f` / `--force` does not bypass dependency readiness, target validation, or checkout safety.
    - finding: workflow command block should visually separate primary lifecycle and manual / recovery commands.
    - finding: `issue finish` naming can be misread as delivery completion; skill already mitigates this but should keep the warning prominent.
  - QA-reviewer verdict: pass with P2 findings.
    - finding: skill did not yet warn that `sync --github` on a just-finished issue branch can restore active from branch-derived context.
    - finding: automated regression did not yet cover the primary CLI path `issue start` -> `issue finish` in one scenario.
  - spec-reviewer verdict: fail with P1.
    - finding: shipped provider skill at `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md` still documented old `issue start -F` while dogfooding mirror used `-f`.
  - remediation:
    - provider skill and dogfooding mirror skill now both document `issue start -f` / `--force`.
    - skill now states that `-f` / `--force` bypasses only the unfinished active issue guard and does not bypass dependency readiness, target validation, or checkout safety.
    - skill and workflow now warn that post-finish `sync --github` on the issue branch can restore active; final sync should move to `main` or another non-issue branch first, or be skipped after finish.
    - workflow command block now separates `# primary lifecycle` from `# manual / recovery only`.
    - added `test_issue_start_then_finish_closes_open_issue_and_clears_active` to cover the skill's primary lifecycle path.
  - verification:
    - provider skill / dogfooding mirror skill: `cmp -s` pass.
    - provider workflow / dogfooding workflow: `cmp -s` pass.
    - targeted grep found no stale `issue start -F` or accidental `issue start -t` guidance outside historical/report context.
    - `python -m unittest tests.cli_runtime.test_issue_lifecycle -v`: pass (`Ran 16 tests ... OK`).
- 2026-05-06 force short option correction:
  - user feedback により、`issue start` の unfinished active issue guard bypass short option を uppercase `-F` ではなく lowercase `-f` に修正した。
  - long option `--force` は維持した。
  - `active set --force` / `sync --force` など他 command の force contract は変更していない。
  - block/recovery message、provider runtime、dogfooding runtime mirror、provider/dogfooding docs、root README、issue execution skill、tests、issue docs を `-f` に揃えた。
  - verification:
    - `./spec-dock/scripts/spec-dock issue start --help`: `-f, --force` を表示。
    - `python -m unittest tests.cli_runtime.test_issue_lifecycle -v`: pass (`Ran 15 tests ... OK`)。
    - `./spec-dock/scripts/spec-dock validate`: pass (`nodes=37`)。
    - provider/dogfooding runtime mirror for `commands/issue.py` and `application/issue_lifecycle.py`: `cmp -s` pass。
    - `git diff --check`: pass。
  - old short options `-F` and accidental `-t` are rejected by lifecycle CLI regression test.
- 2026-05-05 SG1 spec review は fail:
  - `-f` の scope が dependency/readiness bypass と読める設計記述になっていた。
  - S99 final gate に `sync --github` evidence が不足していた。
  - S01-S03 に step-local の bounded implementation batch / verification / report evidence が不足していた。
  - S00 が lc-007 docs closure を先取りしており、S90 の docs closure と混同しやすかった。
- 解決:
  - `-f` を unfinished active issue guard 専用とし、dependency/readiness check は bypass しない契約へ修正した。
  - S99 に `./spec-dock/scripts/spec-dock sync --github` と report evidence を追加した。
  - S00-S03/S90 に bounded implementation batch、verification command、report evidence、refactor guardrails を補足した。
  - S00 は SG1 baseline として扱い、lc-007 は S90/S99 の docs/skill closure に限定した。

## 学んだこと
- `issue finish` の completion source は local lifecycle flag ではなく GitHub `CLOSED` state として固定した。
- 実運用では `issue finish` 後も Git branch 自体は issue branch のままなので、その状態で `sync --github` を走らせると branch 名から active が復元されうる。active clear を保ちたい終了手順では、`main` など non-issue branch へ移動してから final sync するのが安全。

## 今後の推奨事項
- 追加の Phase 2 として force reason / audit schema、finish 前の delivery gate 連携、PR/merge automation を検討する場合は、別 issue で要件化してから実装する。

## 省略/例外メモ
- commit / push / PR / merge / GitHub issue close は本実装作業では未実施。`issue finish` は lifecycle closure command として実装済みだが、この issue 自体の完了処理としては実行していない。
- `issue finish` は delivery completion を保証しないため、delivery completion は本 report の tests / reviews / validate / sync evidence で閉じる。
