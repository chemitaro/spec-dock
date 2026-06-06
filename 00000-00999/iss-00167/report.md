---
種別: 実装報告書（Issue）
ID: "iss-00167"
タイトル: "Migrate Tests To Pytest"
関連GitHub: ["#167"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-06"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00167 Migrate Tests To Pytest — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

> `report.md` は観測証跡台帳（observed evidence ledger）です。planned requirements、evidence destination、closure 条件は `plan.md` が所有し、この文書は調査、採用判断、reviewer status、実装中の Red / Green / Refactor evidence、closure delta、commit/no-op evidence を記録する。

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger / 必須）

| 識別子（ID） | 状態（Status） | 種別（Type） | 起票元（Raised By） | 契機 / 差分（Gap） | 検討した選択肢 | 判断 / 解釈 | 根拠（Rationale） | 処置（Disposition） | 証跡（Evidence） | フォローアップ（Follow-up） |
|---|---|---|---|---|---|---|---|---|---|---|
| D-001 | resolved | scope | user / orchestrator | `iss-00160` merge 前提が後から満たされ、旧前提の planning が無効になった | 旧 layout 前提で続行; 現行 main merge 後の layout で requirement から作り直す | 現行 branch の `iss-00160` merge 後状態を正として requirement から再作成する | `tests/unit` / `tests/integration` / `tests/cli_runtime` の現行配置、README / AGENTS / CI の unittest 契約を確認済み | applied | `git log --oneline --decorate --graph -12`; `git diff --name-status --find-renames 7ea10f7c..2a27a8eb -- tests`; `find tests -type f -name '*.py'` | none |
| D-002 | resolved | test-strategy | user | pytest 互換実行だけにするか、完全移行にするか | A: pytest runner のみ導入; B: unittest tests を pytest collection 互換で温存; C: unittest runner / API 依存を除去する完全移行 | C を採用し、`unittest.TestCase`、`self.assert*`、`unittest.main()`、`unittest.mock` 依存の除去を requirement に入れる | ユーザーが「オプションC」「完全に pytest に移行」を明示済み | applied | user instruction; `requirement.md` Scope / AC-006 | none |
| D-003 | resolved | scope | spec-reviewer | Requirement review で、pytest migration が親 Epic の first-wave context-surface scope へ trace できないと指摘された | A: 親 Epic first-wave issue として扱う; B: 親 Epic scope 外として re-parent / parent update を要求する; C: 親 Epic の deferred testing / regression infrastructure lane として位置づけ、first-wave を置き換えないことを requirement に明示する | C を採用。ユーザーがこの active issue で pytest migration を進める意図を示しており、親 Epic plan には regression / harness / runtime gate の deferred work が存在するため、この Issue は後段 testing infrastructure lane として固定する | 親 Epic first-wave closure を変更せず、pytest migration が後続の deterministic test evidence / regression lane の土台になることを明示すれば、親 Epic trace と scope control を両立できる | applied | requirement review finding REQ-001; `spec-dock/active/epic/plan.md` Deferred work; `spec-dock/active/epic/discussions/20260605t034636z-01-research-branch-d-codex-eval-ci-harness-patterns-deep-research-report.md`; `requirement.md` Parent Epic trace / AC-009 | none |
| D-004 | resolved | ci-scope | user | ユーザー確認により、GitHub Actions / provider CI は unit-only ではなく全テストを実行してほしいと明示された | A: previous plan の unit-only provider CI を維持; B: provider CI を `uv run pytest tests/unit` + 別 job で段階実行; C: provider CI / GitHub Actions の標準 test step を `uv run pytest` full suite にする | C を採用。GitHub Actions は pytest collection 対象の unit / integration / cli_runtime を含む full suite を実行する。個別 lane command は local / step-level verification として残す | ユーザーの最新指示が CI scope の source of truth であり、「すべてのテストを実行」が明確。unit-only 前提は requirement/design/plan ともに修正し、前回 pass は substantive change により stale と扱う | applied | user instruction 2026-06-06; `.github/workflows/provider-ci.yml` current state still `python -m unittest discover -s tests/unit`; updated `requirement.md`, `design.md`, `plan.md`; fresh requirement/design/plan reviews passed | none |
| D-005 | resolved | plan-scope | spec-reviewer | Plan re-review failed because `tests/unit/commands/test_runtime_new_s08.py` contains unittest dependencies but S04/S05/S08 did not provide an allowed migration step for `tests/unit/commands/**` | A: leave commands cleanup to S08; B: absorb commands into S05 infra step; C: add `tests/unit/commands/**` to S04 small / medium unit migration with focused verification | C を採用。commands package is a unit package outside the large infra file, so S04 owns its pytest migration and verification. S08 remains cleanup/consolidation only. | This keeps step ownership aligned with design's unit lane file plan and lets AC-006 / AC-008 close without expanding infra scope or overloading cleanup. | applied | plan review finding 2026-06-06; `tests/unit/commands/test_runtime_new_s08.py`; updated `plan.md` S04 / AC mapping / tc-006; fresh plan review passed | none |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | command / local inspection | `requirement.md` 背景・現状 / スコープ / AC | `iss-00160` 後の現行 test topology と stale docs / CI 契約を一次情報として採用 | `find tests -type f -name '*.py'`; `rg -n "unittest\|self\\.assert\|assertRaises\|subTest\|unittest\\.main\|from unittest\|import unittest" tests README.md AGENTS.md .github/workflows pyproject.toml`; `rg -n "pytest" uv.lock pyproject.toml tests README.md AGENTS.md .github/workflows src/spec_dock/assets/install_root/.github/workflows` | requirement review |
| EAL-002 | partially_adopted | repo-analyst | `requirement.md` 背景・現状 / 前提 / edge cases | Read-only analysis の事実部分を採用。推奨スコープのうち「unittest-style tests を温存する狭い migration」はユーザー意図と衝突するため不採用 | repo-analyst final summary 2026-06-06; `README.md`; `AGENTS.md`; `.github/workflows/provider-ci.yml`; `pyproject.toml` | requirement review |
| EAL-003 | adopted | user instruction | `requirement.md` 目的 / スコープ / 未確定事項 | ユーザーが完全移行を明示したため、追加 interview なしで scope / non-scope / AC を固定できる | user instruction: 「オプションC」「完全に pytest に移行」 | requirement review |
| EAL-004 | adopted | spec-reviewer finding / parent epic docs | `requirement.md` 親 Epic trace / 対象外 / AC-009; `report.md` D-003 | Requirement review の REQ-001 は親 Epic trace の実欠落だったため採用。親 Epic first-wave を置き換えず、deferred testing / regression infrastructure lane として位置づける修正を行った | requirement review JSON; `spec-dock/active/epic/plan.md`; `spec-dock/active/epic/discussions/20260605t034636z-01-research-branch-d-codex-eval-ci-harness-patterns-deep-research-report.md` | fresh requirement re-review |
| EAL-005 | partially_adopted | spec-dock-system-architect draft | `design.md` 採用方針 / 依存関係分析 / interface contract / file plan / risk | Draft の harness-first migration、test lane preservation、docs / CI contract、risk framing を採用。pytest dependency は orchestrator が `dependency-groups.dev` に固定。Draft / previous integration の provider CI unit-only 判断はユーザー補正により不採用へ変更し、full-suite CI contract に差し替えた。`unittest.mock` 温存案は不採用 | `spec-dock/active/issue/discussions/20260606t045218z-disc-pytest-complete-migration-design-proposal.md`; user correction D-004; updated `design.md`; fresh design review passed | none |
| EAL-006 | partially_adopted | spec-dock-implementation-planner draft | `plan.md` step order / closure index / delegation contract / test seeds / review gates; `report.md` delegated evidence | Draft の S00/S01/S02/S03/S04/S05/S06/S08/S90/S99 ordering、44 files unittest dependency finding、large infra file risk、review gate structure を採用。Canonical `plan.md` では issue-plan schema に合わせて再構成し、D-004 により S90 / AC-002 / final gates を full-suite GitHub Actions contract へ変更し、D-005 により `tests/unit/commands/**` を S04 に追加した | `spec-dock/active/issue/discussions/20260606t050446z-disc-pytest-migration-plan-proposal.md`; user correction D-004; plan review finding D-005; updated `plan.md`; fresh plan review passed | none |
| EAL-007 | adopted | user correction / local CI inspection | `requirement.md`, `design.md`, `plan.md`, `report.md` CI scope | 現行 spec は provider CI unit-only 前提だったが、ユーザーは GitHub Actions で全テストを実行することを要求したため、CI scope を full pytest suite に修正した | `.github/workflows/provider-ci.yml` currently runs `python -m unittest discover -s tests/unit`; user instruction; updated canonical docs; fresh requirement/design/plan reviews passed | none |
| EAL-008 | adopted | spec-reviewer plan review finding | `plan.md` S04 scope / closure index / step mapping | `tests/unit/commands/**` が実行計画から漏れており、完全移行の grep closure を閉じられないという指摘は現物に基づく blocking gap だったため採用 | plan review fail 2026-06-06; `plan.md` update; D-005; fresh plan review passed | none |

## 目的整合台帳（Objective Alignment Ledger / 必須）

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | pytest 完全移行を runner / dependency / tests / docs / CI まで固定 | `iss-00160` 後の test layout 維持、GitHub Actions full pytest suite、heavy runtime lane の pytest 実行可能性 | low: runtime 性能改善や layout 再編を scope 外に置いた | pass: fresh requirement re-review after D-004 |
| OAL-002 | 親 Epic first-wave を置き換えず、後段 testing / regression infrastructure lane として扱う | 親 Epic の deferred regression / harness / runtime gate 記述、deterministic test evidence research | medium before fix; low after Parent Epic trace / AC-009 added | pass: fresh requirement re-review |
| OAL-003 | Design keeps pytest complete migration as the primary objective and expresses it through dependency / runner / harness / test idiom / docs / CI contracts | Provider CI / GitHub Actions now runs full pytest suite; product runtime and parent Epic first-wave work remain unchanged | low: Python version matrix expansion and runtime optimization remain out of scope | pass: fresh design re-review after D-004 |
| OAL-004 | Plan turns complete pytest migration into ordered executable steps with closure evidence, delegation boundaries, S90 docs/CI cutover, and S99 final gates | Large unittest-dependent files are isolated into dedicated slices; parent Epic boundary is reserved for final spec review | low: plan forbids unittest exception, CI scope reduction below full suite, product source change, assertion weakening, and test deletion without amendment | pass: fresh plan re-review after D-005 |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | Active issue / parent epic / workflow docs / current branch status / `iss-00160` diff / current test topology / README / AGENTS / provider CI / pyproject / lock / repo-analyst read-only analysis / parent Epic plan deferred work / deterministic gate research / D-004 CI scope correction | Blocking question: none. ユーザーは完全移行と GitHub Actions full-suite execution を明示済み。Requirement review REQ-001 は親 Epic trace 欠落として採用し修正済み。 | adopted / partially_adopted per EAL-001..004, EAL-007 | pass: fresh re-review after D-004 | no known blocker | Promoted to design re-review |
| design | Approved requirement, system-architect draft, `pyproject.toml`, `README.md`, `AGENTS.md`, provider CI, representative tests / harness, phase_design / workflow_issue, D-004 CI scope correction | Blocking question: none. Dependency source is fixed to `dependency-groups.dev`; `unittest.mock` is forbidden with all other `unittest` imports; provider CI / GitHub Actions runs full pytest suite. | partially_adopted per EAL-005 and EAL-007; canonical design authored by orchestrator | pass: fresh re-review after D-004 | no known blocker | Promoted to plan re-review |
| plan | Approved requirement/design, implementation-planner draft, issue-plan authoring docs, phase_plan_issue, workflow_issue, current unittest dependency evidence, user CI correction D-004, plan-scope correction D-005 | Blocking question: none. Plan assumes hard pytest cutover, step commits, delegated implementation, per-step code/spec review, S90 docs/CI full-suite cutover, S04 commands package migration, and S99 final QA/code/spec gates. | partially_adopted per EAL-006..008; canonical plan authored by orchestrator | pass: fresh re-review after D-005 | no known blocker | Ready for execution handoff |

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）

| ロール（created_by_role） | 範囲（scope_id） | ドラフトパス（discussion draft path） | 参照元（source_paths） | 予定反映先（intended_targets） | 採用状態（adoption_status） | 反映先（reflected_to） | 差分ガード結果（diff_guard_result） | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果（reviewer result） | 昇格判断（promotion decision） |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| repo-analyst | iss-00167 | N/A（read-only analysis; discussion direct-write not used） | current repo files / active issue docs / test layout | `requirement.md`, `report.md` | partially_adopted | `requirement.md`, `report.md` | N/A | 事実部分を canonical docs へ統合 | unittest-style tests 温存を前提にした狭い推奨は不採用 | none | N/A | delegated draft ではなく read-only evidence として採用 |
| spec-dock-system-architect | iss-00167 | `spec-dock/active/issue/discussions/20260606t045218z-disc-pytest-complete-migration-design-proposal.md` | active issue docs, parent docs, workflow docs, `pyproject.toml`, README / AGENTS / provider CI, tests topology, representative tests / harness | `design.md`, `plan.md`, `report.md` | partially_adopted via EAL-005 | `design.md`, `report.md` | manual_guard_passed: formal baseline-status was not captured before delegation; post-run status showed only canonical issue docs plus one new issue discussion | Adopted after orchestrator rewrite into canonical design; D-004 later changed CI scope to full suite and fresh design review passed | optional extra / narrow mock retention uncertainty was resolved differently: `dependency-groups.dev`, no `unittest.mock`; unit-only provider CI now rejected | none | pass after D-004 design re-review | promoted to plan re-review |
| spec-dock-implementation-planner | iss-00167 | `spec-dock/active/issue/discussions/20260606t050446z-disc-pytest-migration-plan-proposal.md` | active issue docs, parent epic docs, workflow / phase / authoring docs, current pytest/unittest config, docs, CI, representative tests | `plan.md`, `report.md` | partially_adopted via EAL-006 and supplemented by EAL-008 | `plan.md`, `report.md` | manual_guard_passed: formal baseline had pre-existing dirty canonical docs and untracked design discussion; post-run added exactly the expected plan discussion | Adopted after orchestrator rewrite into canonical issue-plan schema; D-004 changed CI scope to full suite; D-005 added `tests/unit/commands/**` to S04; fresh plan review passed | Draft's caveat language and proposal authority were not copied as plan authority; unit-only CI assumption rejected; initial commands package omission fixed by D-005 | none | pass after D-005 plan re-review | ready for execution handoff |

### 委任ドラフトの失敗モード（Delegated Draft Failure Modes）

| 失敗モード | 期待される判定 | 許可される次アクション | レポート証跡の記録先（report evidence destination） | 昇格可否 |
|---|---|---|---|---|
| missing/stale previous reviewer pass | blocked / incomplete | 該当 phase の reviewer gate を再実行する | Spec Authoring Gate | ineligible |
| requirement gap during design | blocked / incomplete | requirement phase へ戻す | Spec Interpretation / Decision Ledger | ineligible |
| design gap during plan | blocked / incomplete | design phase へ戻す | Spec Interpretation / Decision Ledger | ineligible |
| reviewer unavailable/denied/waived/provisional | blocked / incomplete | fresh passed reviewer を取得する | Spec Authoring Gate / Reviewer Gate Status | ineligible |

## ワークフロー委任同意の証跡（Workflow Delegation Consent）

| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user instruction: 「適切なサブエージェントを利用」 | `/Users/iwasawayuuta/.codex/worktrees/cfd8/spec-dock` | iss-00167 | current session | repo-analyst, spec-reviewer, later code-reviewer / qa-reviewer / dev-coder / doc-writer as plan requires | same repo, active issue, current session, named role; no destructive action, publishing, credentialed access, scope expansion, or canonical doc write by sub-agent | issue complete / session end / scope change / host policy conflict / user revocation | none | proceed with required fresh reviewer gates |

## 実装サマリー
- Planning phase complete after D-004 CI scope correction and D-005 plan-scope correction. Implementation has not started.
- Requirement, design, and plan were recreated from the post-`iss-00160` test topology and the user-selected complete pytest migration scope.
- D-004 corrected the GitHub Actions / provider CI scope from unit-only pytest to `uv run pytest` full suite. Fresh requirement, design, and plan reviewer gates passed in phase order.
- D-005 corrected the plan execution scope so `tests/unit/commands/**` is owned by S04 and full migration closure can be reached.

## 実装記録（セッションログ）

### セッションログ（2026-06-06）

#### 対象
- Phase: requirement authoring
- AC/EC: requirement candidate only
- 計画上の出典（Planned source）:
  - `workflow_spec_authoring.md`
  - `workflow_clarification.md`
  - `phase_requirement.md`
  - `workflow_issue.md`

#### 実施内容
- Active issue と親 Epic を確認した。
- `iss-00160` merge 後の test topology、README / AGENTS / CI / pyproject / lock の current contract を確認した。
- ユーザーの完全移行指示と repo-analyst の read-only facts を統合し、要件定義書を再作成した。
- Blocking clarification question はなしと判断したため、formal interview artifact は作成していない。
- Requirement re-review pass 後、system-architect draft を委任して設計論点を作成し、採用 / 不採用を整理して設計書へ統合した。
- Design review pass 後、implementation-planner draft を委任して plan step ordering / closure / gate proposal を作成し、採用 / 不採用を整理して実装計画書へ統合した。
- ユーザー確認により GitHub Actions / provider CI は unit-only ではなく全テスト実行が必要と判明したため、D-004 として requirement / design / plan を `uv run pytest` full suite 契約へ修正し、requirement -> design -> plan の順で fresh re-review を通した。
- Plan re-review で `tests/unit/commands/**` の実行範囲漏れが見つかったため、D-005 として S04 に追加し、fresh plan re-review を通した。

#### 実行コマンド / 結果
```bash
./spec-dock/scripts/spec-dock active show
# initiative: init-local-00003
# epic: epic-00158
# issue: iss-00167

git status --short --branch
# ## iss-00167-migrate-tests-to-pytest

sed -n '1,140p' .github/workflows/provider-ci.yml
# current implementation still runs: python -m unittest discover -s tests/unit

git diff --check
# pass

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=86
```

#### レビューゲート状態（Reviewer Gate Status）

| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| requirement | requirement spec authoring gate | spec-reviewer | fresh after D-004 CI scope correction | pass | N/A | promoted to design re-review | Fresh re-review confirmed GitHub Actions / provider CI full pytest suite via `uv run pytest` |
| design | design spec authoring gate | spec-reviewer | fresh after D-004 CI scope correction | pass | N/A | promoted to plan re-review | Fresh re-review confirmed provider CI full pytest suite design contract |
| plan | plan spec authoring gate | spec-reviewer | fresh after D-005 plan-scope correction | pass | N/A | ready for execution handoff | Fresh re-review confirmed `tests/unit/commands/**` S04 ownership and provider CI full pytest suite contract |

#### ステップ契約の完了証跡（Step Contract Closure）

| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| planning-requirement | N/A | requirement candidate created from current facts and fresh reviewer pass | `requirement.md`, this report, fresh requirement re-review after D-004 | passed | promoted to design re-review |
| planning-design | N/A | design candidate created from approved requirement and fresh reviewer pass | `design.md`, this report, fresh design re-review after D-004 | passed | promoted to plan re-review |
| planning-plan | N/A | executable plan candidate created from approved design and fresh reviewer pass | `plan.md`, this report, fresh plan re-review after D-005 | passed | ready for execution handoff |

#### テスト契約の完了証跡（Test Contract Closure）

| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| N/A | planning-spec-authoring | no | inspect-only | current docs / test topology inspection | fresh `spec-reviewer` requirement/design/plan re-reviews after D-004/D-005 | passed | implementation tests are planned in `plan.md`; execution has not started |
| tc-000 | S00 preflight characterization | yes | inspect-only | clean tree before implementation; current pytest/unittest state | `uv run pytest --version`; `uv run pytest --collect-only`; baseline grep commands | passed / baseline recorded | `uv run pytest --version` unexpectedly succeeds in current environment with pytest 9.0.3, but `pyproject.toml` / `uv.lock` contain no pytest contract; collect-only finds 1065 tests as unittest-compatible collection; unittest dependencies remain across docs, CI, runtime, unit, and integration files |

### 実装ステップ S00 — Preflight characterization

#### 対象
- Step: S00
- Closure IDs: `tc-000`
- Scope: read-only baseline plus orchestrator report evidence.

#### 実施内容
- Current pytest availability / collection behavior を観測した。
- unittest runner / assertion / fixture API と docs / CI の旧契約が残っていることを baseline として記録した。
- 実装ファイル、テスト、docs、config は変更していない。

#### 実行コマンド / 結果
```bash
uv run pytest --version
# pytest 9.0.3

uv run pytest --collect-only
# collected 1065 items
# pytest currently collects existing unittest-style tests as UnitTestCase/TestCaseFunction.

rg -l 'unittest|self\.assert|assertRaises|subTest|unittest\.main|from unittest|import unittest' tests README.md AGENTS.md .github/workflows pyproject.toml
# matched 44 paths, including README.md, AGENTS.md, .github/workflows/provider-ci.yml,
# tests/cli_runtime/harness.py, tests/cli_runtime/test_*.py,
# tests/unit/{application,cli,commands,domain,infra,presentation}/..., and tests/integration/test_discovery.py

rg -n '^\[tool\.pytest|pytest' pyproject.toml uv.lock
# no output

rg -n 'UnitTestCase|python -m unittest discover|Framework: `unittest`' README.md AGENTS.md .github/workflows tests/cli_runtime tests/unit tests/integration
# README.md and AGENTS.md still document unittest commands/framework.
# .github/workflows/provider-ci.yml still runs python -m unittest discover -s tests/unit.
# tests/unit/infra/test_init_update.py still asserts the old provider CI command string.
```

#### レビュー / コミットゲート
- Step reviewer gate: N/A read-only.
- Commit gate: commit report evidence only.

#### 変更したファイル
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00167-migrate-tests-to-pytest/requirement.md` - post-`iss-00160` 前提の pytest 完全移行要件を作成。
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00167-migrate-tests-to-pytest/design.md` - pytest 完全移行の設計、依存順序、interface contract、test / docs / CI 変更境界を作成。
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00167-migrate-tests-to-pytest/plan.md` - pytest 完全移行の実行順序、closure index、delegation contract、step-local concrete tests、S90/S99 gate を作成。
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00167-migrate-tests-to-pytest/report.md` - 調査、採用判断、委任同意、requirement / design gate 証跡を記録。
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00167-migrate-tests-to-pytest/discussions/20260606t045218z-disc-pytest-complete-migration-design-proposal.md` - system-architect delegated design draft。
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00167-migrate-tests-to-pytest/discussions/20260606t050446z-disc-pytest-migration-plan-proposal.md` - implementation-planner delegated plan draft。

### 実装ステップ S01 — Pytest dependency and collection contract

#### 対象
- Step: S01
- Closure IDs: `tc-001`
- Scope: `pyproject.toml`, `uv.lock`

#### 実施内容
- `dependency-groups.dev` に `pytest>=8.0` を追加した。
- `uv.lock` に pytest 9.0.3 と通常の推移依存を記録した。
- pytest plugin は追加していない。

#### 実行コマンド / 結果
```bash
uv run pytest --version
# pytest 9.0.3

uv run pytest --collect-only
# collected 1065 items
# tests/cli_runtime, tests/integration, tests/unit are included in collection.

git diff --check
# pass
```

#### レビュー / コミットゲート
- Step reviewer gate: code-reviewer fresh pass.
- Reviewer verdict:
  - findings: none
  - review_status: pass
  - notes: scope verified as `pyproject.toml` and `uv.lock` only; pytest is in `dependency-groups.dev`; no pytest plugins; version and collect-only commands pass.
- Commit gate: pending at time of report update.

#### ステップ契約の完了証跡（Step Contract Closure）

| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S01 | `tc-001` | pytest is available through `uv run` and collects current lanes | `uv run pytest --version` -> pytest 9.0.3; `uv run pytest --collect-only` -> 1065 items; code-reviewer pass | passed | dependency contract only; no tests/docs/CI changed in this step |

#### テスト契約の完了証跡（Test Contract Closure）

| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| `tc-001` | S01 | yes | covered-existing | S00 では local environment の pytest は起動できたが dependency contract が repo に存在しなかった | `uv run pytest --version`; `uv run pytest --collect-only`; `git diff --check` | passed | `pyproject.toml` / `uv.lock` に pytest dependency contract を固定 |

#### 変更したファイル
- `pyproject.toml` - `dependency-groups.dev` に pytest を追加。
- `uv.lock` - pytest と通常の推移依存を lock。

### 実装ステップ S02 — Runtime harness pytest-native conversion

#### 対象
- Step: S02
- Closure IDs: `tc-002`
- Scope: `tests/cli_runtime/harness.py`

#### 実施内容
- `CliRuntimeHarness` から `unittest.TestCase` 継承を削除した。
- `harness.py` の `unittest` import と `self.assert*` / `skipTest` 依存を削除した。
- harness 内部の assertion helper を plain `AssertionError` / `assert` helper へ置換した。
- git が必要な helper の skip は `pytest.skip(...)` に移行した。
- Downstream runtime tests の `self.assert*` / `subTest` / `skipTest` 依存は S03 対象として残した。

#### 実行コマンド / 結果
```bash
rg -n 'unittest|TestCase|assertRaises|subTest|skipTest|assertTrue|assertFalse|assertEqual|assertNotEqual|assertIn|assertNotIn|assertIs|assertIsNone|assertIsNotNone|assertIsInstance|assertGreater|assertGreaterEqual|assertLess|assertRegex' tests/cli_runtime/harness.py
# no output

uv run pytest tests/cli_runtime --collect-only
# collected 628 items

python -m py_compile tests/cli_runtime/harness.py
# pass

git diff --check
# pass
```

#### レビュー / コミットゲート
- Initial step reviewer gate: code-reviewer fail.
  - Finding: harness 内の一時互換 shim が `assertRaises` / `subTest` / `assert*` API を残し、pytest-native helper boundary と AC-006 grep target に反していた。
- Follow-up:
  - `tests/cli_runtime/harness.py` から一時互換 shim を削除し、S03 で downstream tests を移行する責務境界へ戻した。
- Fresh step reviewer gate: code-reviewer pass.
  - findings: none
  - review_status: pass
  - notes: previous shim finding resolved; scope is harness-only; replacement assertions preserve checked conditions; downstream migration remains S03 risk.
- Commit gate: pending at time of report update.

#### 仕様解釈 / 判断記録

| ID | 状態 | 種別 | 判断者 | トピック | トリガー | 採用判断 | 根拠 | 影響ファイル | フォローアップ |
|---|---|---|---|---|---|---|---|---|---|
| D-006 | resolved | implementation | orchestrator + code-reviewer | S02 harness transition compatibility | 初回 dev-coder が downstream tests を通すために旧 API 互換 shim を harness に追加し、code-reviewer が P1 fail を返した | 旧 API 互換 shim は不採用。S02 は harness boundary の pytest-native 化に閉じ、downstream tests の旧 API 除去は S03 に残す | AC-006 は permanent `unittest` runner / assertion / fixture API dependency 除去を要求し、S02 は helper boundary から旧 API を外す段階。互換 shim は移行を隠すため不適合 | `tests/cli_runtime/harness.py` | S03 で `tests/cli_runtime/test_*.py` の `self.assert*` / `assertRaises` / `subTest` / `skipTest` を除去 |

#### ステップ契約の完了証跡（Step Contract Closure）

| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S02 | `tc-002` | runtime helper no longer requires `unittest.TestCase` inheritance and harness has no unittest-style helper dependency | scoped grep no output; `uv run pytest tests/cli_runtime --collect-only` -> 628 items; `python -m py_compile tests/cli_runtime/harness.py`; fresh code-reviewer pass | passed | downstream runtime tests intentionally remain for S03 |

#### テスト契約の完了証跡（Test Contract Closure）

| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| `tc-002` | S02 | yes | red-required | harness had `import unittest`, `CliRuntimeHarness(unittest.TestCase)`, `self.assert*`, and `self.skipTest` dependencies | scoped grep; `uv run pytest tests/cli_runtime --collect-only`; `python -m py_compile tests/cli_runtime/harness.py`; `git diff --check` | passed | `uv run pytest tests/cli_runtime/test_new.py -q` is not claimed as S02 closure after shim removal; full runtime pass belongs to S03 |

#### 変更したファイル
- `tests/cli_runtime/harness.py` - runtime harness を pytest-native plain helper に移行。

### 実装ステップ S03 — Runtime / CLI regression lane migration

#### 対象
- Step: S03
- Closure IDs: `tc-003`, `tc-004`, `tc-005`
- Scope: `tests/cli_runtime/test_*.py`

#### 実施内容
- `tests/cli_runtime/test_*.py` 25ファイルを pytest-native に移行した。
- `import unittest`, `from unittest`, `unittest.TestCase`, `unittest.skip`, `unittest.main`, `unittest.mock`, `self.assert*`, `self.fail(...)`, `assertRaises*`, `subTest`, `skipTest` を runtime lane から除去した。
- 既存 skip は `pytest.mark.skip` / `pytest.skip` として理由を維持した。
- `unittest.mock` は pytest-native local fake/context または direct monkeypatch-style helper に置換した。
- 旧 `subTest` 由来のケースは `pytest.mark.parametrize` または case label 付き assertion message へ移行し、ケース可視性を維持した。
- pytest lifecycle では呼ばれない `tearDown` を `teardown_method` に移行した。

#### 実行コマンド / 結果
```bash
rg -n 'self\.fail\(|def tearDown|super\(\)\.tearDown|import unittest|from unittest|unittest\.|self\.assert|assertRaises|subTest|skipTest|unittest\.main|mock\.' tests/cli_runtime
# no output

uv run pytest tests/cli_runtime --collect-only
# collected 651 items

uv run pytest tests/cli_runtime/test_new.py -q
# 38 passed, 5 skipped

uv run pytest tests/cli_runtime/test_runtime_doctor_s04.py -q
# 26 passed

uv run pytest tests/cli_runtime/test_import.py tests/cli_runtime/test_deps.py tests/cli_runtime/test_worktree.py -q
# 168 passed, 10 skipped

uv run pytest tests/cli_runtime
# 575 passed, 76 skipped in 359.74s

git diff --check
# pass
```

#### レビュー / コミットゲート
- Initial S03 code-reviewer gates returned pass with P2 findings.
- All P2 findings were fixed before commit:
  - locked worktree returncode assertion restored to success/failure equivalence check.
  - former `subTest` loops in `test_deps.py`, `test_import.py`, `test_worktree.py`, and `test_new.py` were parametrized or given explicit case labels.
  - `TestDelegatedAuthoringCli.tearDown` was converted to `teardown_method`.
  - leftover `self.fail(...)` calls in `test_runtime_doctor_s04.py` were replaced with `pytest.fail(...)`.
- Fresh final step reviewer gate: code-reviewer pass.
  - findings: none
  - review_status: pass
  - notes: no P0/P1/P2 finding; no old unittest API residue; no test function deletion; no out-of-scope diff; no new xfail; S03 step commit possible.
- Commit gate: pending at time of report update.

#### 仕様解釈 / 判断記録

| ID | 状態 | 種別 | 判断者 | トピック | トリガー | 採用判断 | 根拠 | 影響ファイル | フォローアップ |
|---|---|---|---|---|---|---|---|---|---|
| D-007 | resolved | implementation | orchestrator + code-reviewer | Former `subTest` case visibility | S03 review が plain loop 化により failure case identity / coverage が落ちる P2 を複数回指摘した | `pytest.mark.parametrize` が自然な箇所は parametrization、共有 fixture / side effect が大きい箇所は case label 付き assertion message で補強 | EC-002 は former `subTest` cases の visibility 維持を要求する。全て parametrize に寄せるより、副作用の大きい loop は case label で可視性を保つ方が最小安全 | `tests/cli_runtime/test_deps.py`, `test_import.py`, `test_worktree.py`, `test_new.py` | S99 QA で EC-002 closure を再確認 |
| D-008 | resolved | implementation | orchestrator + code-reviewer | Pytest lifecycle cleanup | `tearDown` は plain class 化後に pytest から呼ばれず、TemporaryDirectory cleanup が per-test lifecycle から外れる P2 が出た | `tearDown` を `teardown_method` へ移行し、`super().tearDown()` を削除 | S03 は runtime lane の pytest-native migration であり、cleanup lifecycle も pytest の実行規約に合わせる必要がある | `tests/cli_runtime/test_delegated_authoring.py` | なし |
| D-009 | resolved | implementation | orchestrator + code-reviewer | Residual `self.fail(...)` | `self.fail(...)` が grep baseline から漏れたが、plain class では `unittest.TestCase.fail` が存在しない P2 が出た | `self.fail(...)` を `pytest.fail(...)` に置換し、future grep に `self\.fail\(` を追加 | AC-006 は unittest assertion API dependency の除去を要求する。`self.fail` も assertion API とみなす | `tests/cli_runtime/test_runtime_doctor_s04.py` | S08/S99 grep へ `self\.fail\(` を含める |

#### ステップ契約の完了証跡（Step Contract Closure）

| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S03 | `tc-003`, `tc-004`, `tc-005` | runtime lane passes under pytest and has no unittest dependency; former subTest / exception expectations retain visibility and strength | scoped grep no output; collect-only 651 items; full `uv run pytest tests/cli_runtime` -> 575 passed, 76 skipped; final code-reviewer pass with no findings | passed | runtime lane duration 359.74s recorded for EC-005 |

#### テスト契約の完了証跡（Test Contract Closure）

| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| `tc-003` | S03 | yes | red-required | S02 後は runtime test bodies に `self.assert*` / `subTest` / `skipTest` / `unittest` API が残り、initial runtime run は多数 failure | `uv run pytest tests/cli_runtime`; scoped grep | passed: 575 passed, 76 skipped; grep no output | full runtime lane migrated |
| `tc-004` | S03 | yes | covered-existing | Former `subTest` cases existed across deps/import/worktree/new loops | parametrization / case label assertions; code-reviewer re-review | passed | P2 findings were fixed before final review |
| `tc-005` | S03 | yes | covered-existing | `assertRaises*` / exception message checks were unittest-style | pytest-native exception assertions; full runtime lane | passed | no `assertRaises` grep output remains |

#### 変更したファイル
- `tests/cli_runtime/test_active.py`
- `tests/cli_runtime/test_close.py`
- `tests/cli_runtime/test_delegated_authoring.py`
- `tests/cli_runtime/test_delete.py`
- `tests/cli_runtime/test_deps.py`
- `tests/cli_runtime/test_import.py`
- `tests/cli_runtime/test_issue_lifecycle.py`
- `tests/cli_runtime/test_new.py`
- `tests/cli_runtime/test_post_mutation_sync_s01.py`
- `tests/cli_runtime/test_runtime_active_s05.py`
- `tests/cli_runtime/test_runtime_active_s06.py`
- `tests/cli_runtime/test_runtime_close_s12.py`
- `tests/cli_runtime/test_runtime_delete_s13.py`
- `tests/cli_runtime/test_runtime_deps_s04.py`
- `tests/cli_runtime/test_runtime_doctor_s04.py`
- `tests/cli_runtime/test_runtime_import_s10.py`
- `tests/cli_runtime/test_runtime_new_doc_s09.py`
- `tests/cli_runtime/test_runtime_shell_s11.py`
- `tests/cli_runtime/test_runtime_validate_s02.py`
- `tests/cli_runtime/test_sync.py`
- `tests/cli_runtime/test_uninstall.py`
- `tests/cli_runtime/test_update.py`
- `tests/cli_runtime/test_validate.py`
- `tests/cli_runtime/test_worktree.py`
- `tests/cli_runtime/test_wrappers.py`

### 実装ステップ S04 — Small / medium unit package migration

#### 対象
- Step: S04
- Closure IDs: `tc-006`, with applicable `tc-004`, `tc-005`
- Scope: `tests/unit/application`, `tests/unit/cli`, `tests/unit/commands`, `tests/unit/domain`, `tests/unit/presentation`, `tests/unit/test_discovery.py`

#### 実施内容
- S04 対象 unit packages を pytest-native に移行した。
- `import unittest`, `from unittest`, `unittest.TestCase`, `unittest.main`, `unittest.mock`, `self.assert*`, `self.fail`, `assertRaises*`, `subTest`, `skipTest` を S04 対象範囲から除去した。
- 既存 skip は `pytest.skip(...)` として理由と条件を維持した。
- 例外期待は `pytest.raises(..., match=...)` へ移行した。
- 旧 `subTest` 由来の loop は parametrization または case label 付き assertion message で failure case visibility を維持した。
- `unittest.mock.patch` 由来の patching は file-local context manager / direct monkeypatch-style helper へ移行し、pytest plugin は追加していない。
- `tests/unit/cli/test_cli.py` の runtime shell inventory は、現行 runtime lane の class 名 `TestRuntimeShellS11` に合わせた。

#### 実行コマンド / 結果
```bash
rg -n 'self\.fail\(|def tearDown|super\(\)\.tearDown|import unittest|from unittest|unittest\.|self\.assert|assertRaises|subTest|skipTest|unittest\.main|mock\.' tests/unit/application tests/unit/cli tests/unit/commands tests/unit/domain tests/unit/presentation tests/unit/test_discovery.py
# no output

uv run pytest tests/unit/application tests/unit/cli tests/unit/commands tests/unit/domain tests/unit/presentation tests/unit/test_discovery.py
# 211 passed in 2.29s

git diff --check
# pass
```

#### レビュー / コミットゲート
- Initial S04 code-reviewer gate: fail.
  - P1: S04 completion evidence was not yet recorded in `report.md`.
  - P2: former `subTest` loops in `test_authority.py`, with similar direct loop conversions in `test_validate.py`, `test_delegated_authoring.py`, and `test_runtime_domain_s03.py`, needed case label visibility.
- Follow-up:
  - P2 was fixed in the allowed S04 files by adding case labels / assertion messages for former `subTest` loops.
  - Fresh S04 code-reviewer found P1 that `tests/unit/test_discovery.py` had become an uncollected plain class because the class name did not start with `Test`; fixed by renaming `UnitDiscoverySmokeTest` to `TestUnitDiscoverySmoke`.
  - Focused follow-up verification:
    - `rg -n 'subTest|self\.assert|assertRaises|skipTest|unittest|mock\.' tests/unit/application/test_validate.py tests/unit/domain/test_authority.py tests/unit/domain/test_delegated_authoring.py tests/unit/domain/test_runtime_domain_s03.py` -> no output
    - `uv run pytest tests/unit/application/test_validate.py tests/unit/domain/test_authority.py tests/unit/domain/test_delegated_authoring.py tests/unit/domain/test_runtime_domain_s03.py` -> 77 passed in 0.20s
    - `uv run pytest tests/unit/test_discovery.py -q` -> 1 passed in 0.01s
    - `uv run pytest tests/unit/application tests/unit/cli tests/unit/commands tests/unit/domain tests/unit/presentation tests/unit/test_discovery.py` -> 211 passed in 2.32s
    - `git diff --check` -> pass
- Later S04 code-reviewer gate: fail.
  - P1: `tests/unit/cli/test_cli_smoke.py` still had `setUp`, which pytest does not call for a plain class.
- Follow-up:
  - `setUp` was converted to `setup_method`, preserving the existing Windows / bash unavailable skip guard under pytest lifecycle.
  - Focused follow-up verification:
    - `rg -n 'def setUp|skipTest|unittest|self\.assert|assertRaises|subTest|mock\.' tests/unit/cli/test_cli_smoke.py` -> no output
    - `uv run pytest tests/unit/cli/test_cli_smoke.py` -> 2 passed in 1.21s
    - `git diff --check` -> pass
- Fresh step reviewer gate: code-reviewer pass after `setup_method` lifecycle follow-up.
  - reviewer: `019e9c1f-550b-7da3-bcea-e0f28059f2c4`
  - review_status: pass
  - summary: HEAD `30e4a4c6` plus the report-only working tree diff has no remaining actionable findings; `setup_method` resolves the CLI smoke lifecycle concern and the remaining diff is suitable as S04 gate evidence.
- Commit gate: implementation commit `30e4a4c6`; report-only gate evidence commit `751381b5`.

#### 仕様解釈 / 判断記録

| ID | 状態 | 種別 | 判断者 | トピック | トリガー | 採用判断 | 根拠 | 影響ファイル | フォローアップ |
|---|---|---|---|---|---|---|---|---|---|
| D-010 | resolved | implementation | dev-coder + orchestrator | Runtime shell inventory class name | `tests/unit/cli/test_cli.py` の inventory が旧 `RuntimeShellS11Tests` を参照したが、S03 後の runtime lane は `TestRuntimeShellS11` を公開していた | inventory 側を現行 class 名 `TestRuntimeShellS11` に更新 | inventory test の目的は runtime lane の重要 class / method が存在することの確認であり、現行 source の定義名へ追随するのが最小変更 | `tests/unit/cli/test_cli.py` | なし |
| D-011 | resolved | implementation | code-reviewer + dev-coder + orchestrator | Former `subTest` case visibility in S04 unit packages | 初回 S04 review が plain loop 化による failure case visibility 低下を P2 として指摘した | former `subTest` loop は parametrization または case label / assertion message で可視性を維持する | EC-002 は former `subTest` cases の visibility 維持を要求する。pytest-native 移行後も失敗ケース特定性を落とさない必要がある | `tests/unit/application/test_validate.py`, `tests/unit/domain/test_authority.py`, `tests/unit/domain/test_delegated_authoring.py`, `tests/unit/domain/test_runtime_domain_s03.py` | S04 fresh review で再確認 |
| D-012 | resolved | implementation | code-reviewer + orchestrator | Pytest class discovery for unit discovery smoke | S04 fresh review found that removing `unittest.TestCase` from `UnitDiscoverySmokeTest` made the class invisible to pytest default discovery | Rename the class to `TestUnitDiscoverySmoke` so pytest collects the existing package marker smoke test | AC-008 requires coverage intent preservation; a migrated class test must still be collected after dropping `unittest.TestCase` inheritance | `tests/unit/test_discovery.py` | S04 fresh review で再確認 |
| D-013 | resolved | implementation | code-reviewer + dev-coder + orchestrator | Pytest lifecycle for CLI smoke skip guard | S04 review found that plain-class `setUp` was not called by pytest, bypassing the existing Windows / bash unavailable skip guard | Convert `setUp` to `setup_method` and keep the existing skip conditions and reasons | AC-008 requires preserving existing test hermeticity and environment guards after dropping `unittest.TestCase` inheritance | `tests/unit/cli/test_cli_smoke.py` | S04 fresh review で再確認 |

#### ステップ契約の完了証跡（Step Contract Closure）

| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S04 | `tc-006`, `tc-004`, `tc-005` | small / medium unit packages pass under pytest idioms; former subTest and exception expectation visibility / strength are preserved | scoped grep no output; `uv run pytest tests/unit/test_discovery.py -q` -> 1 passed; `uv run pytest tests/unit/cli/test_cli_smoke.py` -> 2 passed; `uv run pytest tests/unit/application tests/unit/cli tests/unit/commands tests/unit/domain tests/unit/presentation tests/unit/test_discovery.py` -> 211 passed; `git diff --check` pass; fresh code-reviewer pass `019e9c1f-550b-7da3-bcea-e0f28059f2c4` | passed | initial reviewer P2 fixed; discovery P1 and setup lifecycle P1 fixed; final S04 reviewer gate passed; implementation commit `30e4a4c6` |

#### テスト契約の完了証跡（Test Contract Closure）

| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| `tc-006` | S04 | yes | red-required | S04 対象 files に `unittest.TestCase`, `self.assert*`, `subTest`, `skipTest`, `assertRaises*`, `unittest.mock.patch` が残存していた | scoped grep; focused discovery smoke; S04 package-group pytest; `git diff --check` | passed: 211 passed; focused discovery smoke collected; grep no output | S04 対象 packages migrated |
| `tc-004` | S04 | yes | covered-existing | former `subTest` loops existed in application/domain/commands/presentation unit tests | parametrization / case label assertions; focused follow-up pytest | passed | initial P2 finding fixed before fresh re-review |
| `tc-005` | S04 | yes | covered-existing | `assertRaises*` / exception message checks were unittest-style | pytest-native exception assertions; S04 package-group pytest | passed | no `assertRaises` grep output remains |

#### 変更したファイル
- `tests/unit/application/test_check_deps.py`
- `tests/unit/application/test_set_active.py`
- `tests/unit/application/test_validate.py`
- `tests/unit/cli/test_cli.py`
- `tests/unit/cli/test_cli_smoke.py`
- `tests/unit/commands/test_runtime_new_s08.py`
- `tests/unit/domain/test_active.py`
- `tests/unit/domain/test_authority.py`
- `tests/unit/domain/test_delegated_authoring.py`
- `tests/unit/domain/test_deps.py`
- `tests/unit/domain/test_runtime_domain_s01.py`
- `tests/unit/domain/test_runtime_domain_s03.py`
- `tests/unit/presentation/test_runtime_sync_s07.py`
- `tests/unit/test_discovery.py`

### 実装ステップ S05 — Large installer/update unit migration

#### 対象
- Step: S05
- Closure IDs: `tc-007`, with applicable `tc-004`, `tc-005`
- Scope: `tests/unit/infra/test_active_store.py`, `tests/unit/infra/test_fake_gh_harness.py`, `tests/unit/infra/test_init_update.py`

#### 実施内容
- `tests/unit/infra/**` を pytest-native に移行した。
- `unittest.TestCase`, `unittest.mock.patch`, `self.assert*`, `self.fail`, `self.subTest`, `self.skipTest`, `unittest.main()` を除去した。
- 旧 `subTest` 相当の case visibility は case label 付き assertion helper / assertion message で維持した。
- 例外期待は `pytest.raises` と plain assert へ移行した。
- `pytest.MonkeyPatch.context()`、plain assert、`pytest.skip` を使い、既存の isolation / skip guard を維持した。
- `uv run pytest` の `.venv` Python に pip が無い場合でも packaging helper が対象 Python へ依存を入れられるよう、test helper は `uv pip install --target ... --python <target>` fallback を使う。
- checked-in dogfooding snapshot fixtures を現行 `spec-dock/initiatives` に合わせ、`epic-00158` 配下の `iss-00159`, `iss-00162`..`iss-00167` の `.meta.json` と `depends_on` を固定値へ追加した。

#### 実行コマンド / 結果
```bash
rg -n 'self\.fail\(|def tearDown|def setUp|super\(\)\.tearDown|super\(\)\.setUp|import unittest|from unittest|unittest\.|self\.assert|assertRaises|subTest|skipTest|unittest\.main|mock\.' tests/unit/infra
# no output

uv run pytest tests/unit/infra
# 217 passed in 74.29s

uv run pytest tests/unit
# 428 passed in 79.29s

git diff --check
# pass
```

#### Red / 代替証跡
- Delegated dev-coder baseline:
  - `tests/unit/infra` に `import unittest`, `from unittest.mock`, `self.assert*`, `subTest`, `skipTest`, `unittest.main` が残存していた。
  - `uv run pytest tests/unit/infra -q` は `214 failed, 3 passed`。主因は plain pytest class では `self.assertEqual` 等が存在しないこと。
- Orchestrator follow-up after worker diff:
  - Initial local rerun failed with 14 failures.
  - Failure classes:
    - `.venv` Python had no pip, while packaging helper tried `sys.executable -m pip` instead of target venv / wrapper Python.
    - checked-in dogfooding fixture expected values did not include current `epic-00158` issue nodes and dependencies.
    - pytest API conversion around `pytest.raises` / `ExceptionInfo` needed focused verification.
  - Focused fixes were made in `tests/unit/infra/test_init_update.py`, then representative failing tests passed.

#### レビュー / コミットゲート
- Delegated implementation:
  - dev-coder `019e9c26-8832-7b70-b2bb-c766bd370435`
  - changed files: S05 target files only.
  - worker verification reported: scoped grep no output; `uv run pytest tests/unit/infra` -> 217 passed; `uv run pytest tests/unit` -> 428 passed; `git diff --check` -> pass.
- Orchestrator verification:
  - `uv run pytest tests/unit/infra` -> 217 passed in 74.29s.
  - `uv run pytest tests/unit` -> 428 passed in 79.29s.
  - `git diff --check` -> pass.
- Initial S05 code-reviewer gate: fail.
  - P1: S05 closure evidence was missing from `report.md`.
- Follow-up:
  - This S05 section records Step Contract Closure, Test Contract Closure, delegated worker evidence adoption, reviewer gate state, and commit gate status.
- Fresh S05 code-reviewer gate: pass.
  - reviewer: `019e9c31-7940-74d3-87d3-a037d28a7b0f`
  - review_status: pass
  - summary: no remaining actionable S05 correctness issues; report now records delegated adoption, D-015/D-016, Step/Test Contract Closure, and scoped grep plus infra/unit pytest evidence.
- Commit gate: pending at time of report update.

#### 仕様解釈 / 判断記録

| ID | 状態 | 種別 | 判断者 | トピック | トリガー | 採用判断 | 根拠 | 影響ファイル | フォローアップ |
|---|---|---|---|---|---|---|---|---|---|
| D-015 | resolved | implementation | dev-coder + orchestrator | Packaging helper target Python under pytest / uv | `uv run pytest` の `.venv` Python に pip がなく、issue-69 packaging helper が `sys.executable -m pip` へ依存して失敗した | `_issue_69_install_target_packages` に `python_executable` を渡し、対象 venv / wrapper Python に対して pip または `uv pip install --target ... --python <target>` を使う | test helper の目的は isolated wheel / sdist artifact surface を検証することであり、product code を変えずに test isolation を保つ必要がある | `tests/unit/infra/test_init_update.py` | none |
| D-016 | resolved | test-strategy | dev-coder + orchestrator | Dogfooding snapshot fixture refresh | 現行 branch の checked-in dogfooding tree に `epic-00158` issue nodes and dependencies が追加され、固定 snapshot が stale になった | `_CHECKED_IN_DOGFOODING_META_JSON_PATHS`, `_CHECKED_IN_DOGFOODING_DEPENDS_ON_BY_META_PATH`, `_CHECKED_IN_DOGFOODING_NON_EMPTY_ISSUE_DEPENDS_ON_MAP` を現行 tree に合わせて更新する | fixture は checked-in dogfooding state の drift 検出が目的であり、現行 issue set を固定値に反映しないと正しい drift test にならない | `tests/unit/infra/test_init_update.py` | future dogfooding node additions must update this snapshot intentionally |

#### 証跡採用台帳（S05 delegated evidence adoption）

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-S05-001 | adopted | dev-coder `019e9c26-8832-7b70-b2bb-c766bd370435` | S05 implementation and report evidence | Worker stayed within S05 target files, reported Red / Green evidence, and identified material helper / snapshot decisions. Orchestrator re-ran focused failing tests plus infra/unit lanes and adopted the implementation with D-015/D-016. | worker final summary; scoped grep no output; `uv run pytest tests/unit/infra` -> 217 passed; `uv run pytest tests/unit` -> 428 passed; `git diff --check` -> pass | fresh S05 code-reviewer re-review |

#### ステップ契約の完了証跡（Step Contract Closure）

| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S05 | `tc-007`, `tc-004`, `tc-005` | infra unit lane and all unit tests pass under pytest; unittest dependency is removed; former subTest / exception expectation strength is preserved | scoped grep no output; `uv run pytest tests/unit/infra` -> 217 passed; `uv run pytest tests/unit` -> 428 passed; `git diff --check` pass; fresh code-reviewer pass `019e9c31-7940-74d3-87d3-a037d28a7b0f` | passed | code-reviewer P1 report gap fixed; final S05 reviewer gate passed |

#### テスト契約の完了証跡（Test Contract Closure）

| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| `tc-007` | S05 | yes | red-required | infra tests used `unittest.TestCase`, `unittest.mock.patch`, `self.assert*`, `self.subTest`, `self.skipTest`, and `unittest.main`; pre-migration pytest failed broadly | scoped grep; `uv run pytest tests/unit/infra`; `uv run pytest tests/unit`; `git diff --check` | passed: infra 217 passed; unit 428 passed; grep no output | Large infra lane migrated |
| `tc-004` | S05 | yes | covered-existing | former `subTest` loops existed in infra tests | case labels / assertion messages; infra/unit pytest; code-reviewer focus | passed | Fresh review found no remaining actionable S05 correctness issues |
| `tc-005` | S05 | yes | covered-existing | `assertRaises*` / exception expectations were unittest-style | pytest-native exception assertions; scoped grep; infra/unit pytest | passed | no `assertRaises` grep output remains |

#### 変更したファイル
- `tests/unit/infra/test_active_store.py`
- `tests/unit/infra/test_fake_gh_harness.py`
- `tests/unit/infra/test_init_update.py`

### 実装ステップ S06 — Integration lane migration

#### 対象
- Step: S06
- Closure IDs: `tc-008`
- Scope: `tests/integration/test_discovery.py`

#### 実施内容
- integration discovery smoke を pytest-native function に移行した。
- `unittest.TestCase`, `unittest.main`, `self.subTest`, `self.assertTrue` を除去した。
- 旧 `subTest(path=...)` の case visibility は `pytest.mark.parametrize` により、3 つの package marker case として個別 collection される形で維持した。

#### 実行コマンド / 結果
```bash
rg -n 'self\.fail\(|def tearDown|def setUp|super\(\)\.tearDown|super\(\)\.setUp|import unittest|from unittest|unittest\.|self\.assert|assertRaises|subTest|skipTest|unittest\.main|mock\.' tests/integration
# no output

uv run pytest tests/integration -q
# 3 passed in 0.01s

uv run pytest tests/integration --collect-only -q
# tests/integration/test_discovery.py::test_integration_package_markers_exist[integration]
# tests/integration/test_discovery.py::test_integration_package_markers_exist[integration/git_remote]
# tests/integration/test_discovery.py::test_integration_package_markers_exist[integration/github]
# 3 tests collected in 0.00s

git diff --check
# pass
```

#### レビュー / コミットゲート
- Initial S06 code-reviewer gate: pass with P2.
  - P2: loop assertion preserved the first failure message but did not preserve former `subTest` case-level collection when multiple markers are missing.
- Follow-up:
  - Replaced the loop with `pytest.mark.parametrize`, making each integration marker path a separate pytest case.
- Fresh S06 code-reviewer gate: pass.
  - reviewer: `019e9c26-ee98-76d3-8761-c4d143472af9`
  - review_status: pass
  - summary: no findings remain; unittest usage is removed, pytest discovery naming is valid, and former subTest case visibility is preserved through parametrized collection.
- Commit gate: pending at time of report update.

#### 仕様解釈 / 判断記録

| ID | 状態 | 種別 | 判断者 | トピック | トリガー | 採用判断 | 根拠 | 影響ファイル | フォローアップ |
|---|---|---|---|---|---|---|---|---|---|
| D-014 | resolved | implementation | code-reviewer + orchestrator | Integration marker smoke case visibility | S06 review noted that a plain loop would stop at the first missing marker and reduce former `subTest` visibility | Use `pytest.mark.parametrize` for the three integration marker paths | EC-002 requires former multi-case visibility to remain observable after pytest migration; parametrization is the smallest pytest-native replacement for this side-effect-free smoke | `tests/integration/test_discovery.py` | none |

#### ステップ契約の完了証跡（Step Contract Closure）

| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S06 | `tc-008`, with applicable `tc-004` | integration lane is pytest-native, hermetic, collected, and free of unittest dependency | scoped grep no output; `uv run pytest tests/integration -q` -> 3 passed; `uv run pytest tests/integration --collect-only -q` -> 3 tests collected; `git diff --check` pass; fresh code-reviewer pass `019e9c26-ee98-76d3-8761-c4d143472af9` | passed | initial P2 fixed by parametrization |

#### テスト契約の完了証跡（Test Contract Closure）

| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| `tc-008` | S06 | yes | red-required | integration discovery smoke used `unittest.TestCase`, `self.subTest`, `self.assertTrue`, and `unittest.main` | scoped grep; integration pytest; collect-only; `git diff --check` | passed: 3 passed; 3 parametrized cases collected; grep no output | Integration lane migrated |
| `tc-004` | S06 | yes | covered-existing | former `subTest(path=...)` cases existed for three integration marker paths | `pytest.mark.parametrize`; collect-only evidence | passed | case-level visibility preserved |

#### 変更したファイル
- `tests/integration/test_discovery.py`
