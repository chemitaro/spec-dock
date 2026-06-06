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
