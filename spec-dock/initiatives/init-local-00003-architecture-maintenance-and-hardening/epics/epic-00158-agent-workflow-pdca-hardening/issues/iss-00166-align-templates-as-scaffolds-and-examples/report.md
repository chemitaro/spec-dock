---
種別: 実装報告書（Issue）
ID: "iss-00166"
タイトル: "Align Templates As Scaffolds And Examples"
関連GitHub: ["#166"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-06"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00166 Align Templates As Scaffolds And Examples — 実装報告

`report.md` は観測証跡台帳（observed evidence ledger）である。`plan.md` が planned contract を所有し、この文書は実際の review result、verification、closure、commit evidence を記録する。

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger）

| 識別子（ID） | 状態（Status） | 種別（Type） | 起票元（Raised By） | 契機 / 差分（Gap） | 検討した選択肢 | 判断 / 解釈 | 根拠（Rationale） | 処置（Disposition） | 証跡（Evidence） | フォローアップ（Follow-up） |
|---|---|---|---|---|---|---|---|---|---|---|
| D-001 | resolved | scope | orchestrator | GitHub #167 is open but absent from current `epic-00158` tree | Option A: absorb #167; Option B: keep this issue to current Epic tree and templates lane | Treat #167 as outside current `epic-00158` issue tree for this issue; do not absorb tests migration | `tree.json` and local epic issue directories list only `iss-00166` as open child; #167 has no local node under this epic | applied | `spec-dock/.agent/tree.json`; `find .../epic-00158.../issues`; `gh issue view 167` | none |

## 証跡採用台帳（Evidence Adoption Ledger）

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | draft requirement discussion | `requirement.md` | Draft captured template scaffold / evidence slot / good example boundary and clarification-supporting discussion template needs | `discussions/20260606t024154z-draft-requirement-align-templates-scaffolds-examples-draft-requirement.md` | fresh requirement spec review |
| EAL-002 | adopted | `iss-00162` context surface inventory | `requirement.md` | Inventory explicitly hands template README, issue plan/report templates, and discussion templates to `iss-00166` | `iss-00162` discussion `20260606t040013z-disc-context-surface-inventory.md` | design/plan authoring |
| EAL-003 | adopted | completed prior issues | `requirement.md` | `iss-00163`, `iss-00164`, and `iss-00165` completed the skill-owned clarification, hub routing, and docs boundary prerequisites for T4 templates lane | GitHub #163/#164/#165 close evidence; local final gate commits `8d9d62c`, `925095f4`, `602c39aa` | execution prerequisite check |

## 目的整合台帳（Objective Alignment Ledger）

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | Primary objective is template scaffold/example consistency after skill/docs boundary cleanup | Secondary requirements cover provider/mirror validation and report/discussion evidence slots | low if runtime/tests/skills/docs changes stay forbidden | requirement/design/plan passed |

## 仕様 authoring ゲート（Spec Authoring Gate）

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | Epic requirement/design/plan; draft requirement; accepted ADRs; `iss-00162` inventory; current provider templates; completed `iss-00163`/`iss-00164`/`iss-00165`; GitHub #166/#167 state | none | adopted EAL-001..EAL-003 into canonical requirement | initial fail by spec-reviewer `019e9bd8-6cb4-74c0-87ed-59b38fed08dd`; follow-up pass after Initiative / Epic / Issue report templates were added to AC-003 | no | promoted to design |
| design | approved requirement; Epic design; provider template reads; authority-wording search; current dogfooding mirror template list | none | manual design authoring based on approved requirement and template family inspection | fresh pass by spec-reviewer `019e9bdc-d8dd-7b00-a467-f1dea73d8531` | no | promoted to plan |
| plan | approved design; issue plan workflow; template-only execution constraints; plan reviewer findings on executable case schema and delegation handoff fields | none | manual plan authoring with S01/S02/S90/S99 and cl-001..cl-007; updated plan to add required concrete-case fields, delegation handoff fields, reviewer focus, acceptance criteria, and per-step report evidence destinations | initial fail by spec-reviewer `019e9bdf-9f9e-7d83-8ce3-672c6231b5f4`; follow-up pass after executable-case, delegation, and report-destination fixes | no | promoted to issue execution |

## 委任ドラフト証跡（Delegated Draft Evidence）

| ロール（created_by_role） | 範囲（scope_id） | ドラフトパス（discussion draft path） | 参照元（source_paths） | 予定反映先（intended_targets） | 採用状態（adoption_status） | 反映先（reflected_to） | 差分ガード結果（diff_guard_result） | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果（reviewer result） | 昇格判断（promotion decision） |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| N/A | iss-00166 | N/A | N/A | N/A | not used | [] | not_run | manual authoring | N/A | none | N/A | no delegated draft promoted |

## 実装サマリー

- Planning / spec authoring is complete and committed at `f7413abf`.
- S01 template boundary / evidence-slot alignment is implemented and committed at `54e8ea40`.
- S02 discussion template evidence-flow alignment is implemented in provider and dogfooding mirror templates; S02 review and commit are pending.

## 実装記録（セッションログ）

### セッションログ（2026-06-06）

#### 対象
- Phase: issue planning / requirement authoring.
- AC/EC: all planned AC/EC in `requirement.md`.

#### 実施内容
- Started `iss-00166` with `./spec-dock/scripts/spec-dock issue start iss-00166`.
- Confirmed current Epic tree lists `iss-00166` as the only open child under `epic-00158`.
- Confirmed GitHub #166 is OPEN and #167 is OPEN but not in current Epic tree.
- Read draft requirement, Epic docs, `iss-00162` inventory, and current provider templates.
- Authored canonical `requirement.md` from local evidence without a user interview blocker.

#### 実行コマンド / 結果

```bash
./spec-dock/scripts/spec-dock active show
./spec-dock/scripts/spec-dock deps check epic-00158
gh issue view 166 --json number,title,state,body,labels,url
gh issue view 167 --json number,title,state,body,labels,url
find spec-dock/initiatives/.../epic-00158-agent-workflow-pdca-hardening/issues -maxdepth 1 -type d -name 'iss-*' -print
find src/spec_dock/assets/spec_dock/templates spec-dock/templates -maxdepth 3 -type f -print
git status --short

result:
- active issue is `iss-00166`.
- deps check for `epic-00158` returned ready=true blockers=0.
- GitHub #166 is OPEN.
- GitHub #167 is OPEN but has no local node under current `epic-00158` tree.
- local working tree was clean before requirement/report authoring.
```

### セッションログ（2026-06-06 / S01）

#### 対象
- Step: S01 Canonical Template Boundary And Evidence Slots.
- AC/EC: AC-001, AC-003, AC-004, AC-006, EC-001, EC-002, EC-003.
- Closure ids: cl-001, cl-002, cl-003, cl-005.

#### 実施内容
- Delegated S01 template wording update to `doc-writer` sub-agent `019e9be9-7282-7291-8f3b-56a27c952661`.
- Updated canonical template README, Initiative / Epic / Issue report templates, Epic design template, and Issue plan template as scaffold / evidence slot / good example surfaces.
- Preserved Initiative / Epic / Issue report evidence ledger slots.
- Kept S01 scope to provider templates and exact dogfooding mirror equivalents.

#### 実行コマンド / 結果

```bash
git diff --name-only
git diff --check
diff -q src/spec_dock/assets/spec_dock/templates/README.md spec-dock/templates/README.md
diff -q src/spec_dock/assets/spec_dock/templates/initiative/report.md spec-dock/templates/initiative/report.md
diff -q src/spec_dock/assets/spec_dock/templates/epic/design.md spec-dock/templates/epic/design.md
diff -q src/spec_dock/assets/spec_dock/templates/epic/report.md spec-dock/templates/epic/report.md
diff -q src/spec_dock/assets/spec_dock/templates/issue/plan.md spec-dock/templates/issue/plan.md
diff -q src/spec_dock/assets/spec_dock/templates/issue/report.md spec-dock/templates/issue/report.md
rg -n "scaffold|evidence slot|good example|detail-reference|workflow authority|compliance authority|observed evidence ledger|starting shape|詳細参照|参照元" <S01 changed templates>
rg -n "テンプレート.*正本|template.*source of truth|workflow/compliance source of truth|作成/運用ルールの正本|Issue 計画の書き方は .*正本|依存関係の正本" <S01 changed templates>
rg -n "Evidence Adoption Ledger|Delegated Draft Evidence|Spec Authoring Gate|Reviewer Gate Status|Step Contract Closure|Test Contract Closure|Closure Coverage|Closure Delta|blocking|next_action|フォローアップ" <report templates>

result:
- changed paths are limited to 12 S01 provider/mirror template files plus this issue report evidence.
- `git diff --check` passed.
- all 6 provider/mirror template pairs matched.
- positive scaffold / evidence-slot / reference wording was present.
- stale template authority wording was not found; `docs/rules/**` remains only as a detail-reference path and exists in current docs.
- Initiative / Epic / Issue report evidence slots remain present.
```

### セッションログ（2026-06-06 / S02）

#### 対象
- Step: S02 Discussion Template Evidence Flow.
- AC/EC: AC-002, AC-006, EC-002.
- Closure ids: cl-004, cl-005.

#### 実施内容
- Delegated S02 discussion template update to `doc-writer` sub-agent `019e9bf1-f818-7001-a0d2-5e0ca5db6a54`.
- Updated `interview`, `research`, and `disc` discussion templates as non-canonical evidence surfaces.
- Preserved `interview` one-question flow, answer capture, adoption target, and reflection fields.
- Preserved `research` facts / inference / unverified / question-candidate separation.
- Preserved `disc` synthesis, reflection proposal, adoption target, and ADR triage support.
- Kept S02 scope to provider discussion templates and exact dogfooding mirror equivalents.

#### 実行コマンド / 結果

```bash
git diff --name-only
git diff --check
diff -q src/spec_dock/assets/spec_dock/templates/discussions/interview.md spec-dock/templates/discussions/interview.md
diff -q src/spec_dock/assets/spec_dock/templates/discussions/research.md spec-dock/templates/discussions/research.md
diff -q src/spec_dock/assets/spec_dock/templates/discussions/disc.md spec-dock/templates/discussions/disc.md
rg -n "one essential question|answer capture|source-grounded context|adoption target|reflection|facts /|inference /|unverified /|question candidates|synthesis|ADR triage|ADR candidate triage|non-canonical evidence surface|evidence surface" <S02 changed templates>
rg -n "canonical source of truth|accepted authority|compliance authority|phase promotion|正本|採用済み|確定証跡|確定する|決定する" <S02 changed templates>

result:
- changed paths are limited to 6 S02 provider/mirror discussion template files before report evidence.
- `git diff --check` passed.
- all 3 provider/mirror discussion template pairs matched.
- positive source-grounded / answer-capture / facts-inference / synthesis / ADR-triage wording was present.
- accepted/canonical authority claim wording was not found.
```

## 実装委任ゲート（Implementation Delegation Gate）

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | delegated | shipped templates / persistent workflow text changes are docs/template worker work | doc-writer `019e9be9-7282-7291-8f3b-56a27c952661` | canonical template README, report templates, Epic design template, Issue plan template | approved requirement/design/plan; S01 target templates | S01 provider templates and exact dogfooding mirror equivalents | skills, docs, runtime, tests, GitHub state, issue metadata, S02 discussion templates | scope guard, positive/negative `rg`, provider/mirror parity, `git diff --check` | need for skill/doc/runtime/test change; user intent clarification; verification cannot run | changed files, verification result, unresolved risks, ledger note | pass; worker changed only S01 allowed templates and returned no material decision |
| S02 | delegated | shipped discussion template text changes are docs/template worker work | doc-writer `019e9bf1-f818-7001-a0d2-5e0ca5db6a54` | interview / research / disc discussion templates | approved requirement/design/plan; S02 target discussion templates | S02 provider discussion templates and exact dogfooding mirror equivalents | skills, docs, runtime, tests, GitHub state, issue metadata, S01 canonical templates | scope guard, positive/negative `rg`, provider/mirror parity, `git diff --check` | need for clarification skill/workflow/runtime change; user intent clarification; verification cannot run | changed files, verification result, unresolved risks, ledger note | pass; worker changed only S02 allowed templates and returned no material decision |

## 委任 worker 証跡（Delegated Worker Evidence）

| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01 | doc-writer `019e9be9-7282-7291-8f3b-56a27c952661` | Added scaffold / evidence slot / good example boundary wording; preserved report evidence ledgers; routed workflow authority to skills/docs/reviewer gates | 12 S01 provider/mirror template files | worker reported positive/negative `rg`, report-slot `rg`, 6 provider/mirror `diff -q`, scope guard, `git diff --check` all pass | pending step spec-reviewer | none | accepted after parent re-ran scope, parity, `rg`, and whitespace checks |
| S02 | doc-writer `019e9bf1-f818-7001-a0d2-5e0ca5db6a54` | Added non-canonical evidence-surface wording to interview/research/disc templates and preserved source-grounded evidence fields | 6 S02 provider/mirror discussion template files | worker reported positive/negative `rg`, 3 provider/mirror `diff -q`, scope guard, `git diff --check` all pass | pending step spec-reviewer | none | accepted after parent re-ran scope, parity, `rg`, and whitespace checks |

## ステップ契約の完了証跡（Step Contract Closure）

| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| planning-requirement | N/A | canonical requirement authored from local evidence and reviewed before design | requirement authored; reviewer pending | pending | implementation not started |
| planning-requirement | reviewer-finding-001 | Parent Epic plan T4 deliverable `Epic / Issue report evidence slots` must be observable in issue acceptance | AC-003 updated to cover Initiative / Epic / Issue report templates; scope text updated accordingly | pass | fixes P1 requirement reviewer finding |
| planning-design | N/A | design authored after requirement reviewer pass | design maps template families to S01/S02/S90/S99; no implementation started | pass | reviewer passed with no findings |
| planning-plan | N/A | plan authored after design reviewer pass | plan defines S01/S02/S90/S99, cl-001..cl-007, delegation contracts, and inspect-only checks | pass | reviewer passed after executable-case fix |
| planning-plan | reviewer-finding-002 | concrete cases must include premise, operation, expected result, failure detection, verification method, and evidence destination | expanded tc-s01/tc-s02/tc-s90/tc-s99 into executable cards with required fields and report destinations | pass | fixes P1 concrete-case field finding |
| planning-plan | reviewer-finding-003 | doc-writer handoff must include step scope, acceptance criteria, and reviewer focus | S01/S02 delegation contracts now include step scope, acceptance criteria, reviewer focus, and explicit closure IDs | pass | fixes P1 delegation handoff finding |
| planning-plan | reviewer-finding-004 | report evidence destinations must be explicit per step | S01/S02/S90/S99 now list report destinations for delegation, closure, reviewer, commit, and final-gate evidence | pass | fixes P2 report evidence destination finding |
| S01 | cl-001, cl-002, cl-003, cl-005 | S01 templates identify scaffold / evidence / example boundaries, preserve report slots, route plan detail to skills/docs, and stay in S01 scope | worker output; parent `git diff --name-only`; positive/negative `rg`; report-slot `rg`; 6 provider/mirror `diff -q`; `git diff --check`; spec-reviewer `019e9bef-59aa-78b0-8aed-959c201a3630` | pass | reviewer passed with one P3 wording correction, applied |
| S02 | cl-004, cl-005 | Discussion templates support source-grounded question, facts/inference separation, synthesis, adoption target, reflection, ADR triage, and stay in S02 scope | worker output; parent `git diff --name-only`; positive/negative `rg`; 3 provider/mirror `diff -q`; `git diff --check`; spec-reviewer `019e9bf5-628e-7771-85fb-98eea5a92640` | pass | reviewer passed with no findings |

## テスト契約の完了証跡（Test Contract Closure）

| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| cl-001 / tc-s01-001 | S01 | yes | inspect-only | old templates contained stale authority-style wording such as `正本` and plan template source-of-truth phrasing | positive/negative `rg` and human diff inspection of changed S01 templates | pass | changed templates now say scaffold / evidence slot / good example / detail-reference and avoid workflow authority claims |
| cl-002 / tc-s01-002 | S01 | yes | inspect-only | report templates contained required evidence ledger slots before S01 | `rg` for Evidence Adoption Ledger, Delegated Draft Evidence, Spec Authoring Gate, Reviewer Gate Status, closure/follow-up terms | pass | Initiative / Epic / Issue report slots remain present |
| cl-003 / tc-s01-003 | S01 | yes | inspect-only | Issue plan template previously used source-of-truth wording for writing policy | `rg` and diff inspection of `templates/issue/plan.md` provider/mirror pair | pass | Issue plan template is an executable scaffold and routes authority / field semantics to skills/docs |
| cl-005 / tc-s01-004 | S01 | yes | inspect-only | clean worktree after planning commit `f7413abf` | `git diff --name-only` and path comparison against S01 allowed paths | pass | only S01 provider/mirror templates plus issue report evidence changed |
| cl-004 / tc-s02-001 | S02 | yes | inspect-only | `interview.md` already had source-grounded context and answer fields before S02 | `rg` for one essential question, source-grounded context, answer capture, adoption target, reflection; diff inspection | pass | interview template is a non-canonical evidence surface for one-question user interviews |
| cl-004 / tc-s02-002 | S02 | yes | inspect-only | `research.md` and `disc.md` already separated research and synthesis fields before S02 | `rg` for facts / inference / unverified / question candidates / synthesis / adoption target / ADR triage; diff inspection | pass | research and disc templates preserve evidence separation and adoption routing |
| cl-005 / tc-s02-003 | S02 | yes | inspect-only | clean worktree after S01 commit `54e8ea40` | `git diff --name-only` and path comparison against S02 allowed paths | pass | only S02 provider/mirror discussion templates changed before report evidence |

## クロージャ網羅（Closure Coverage）

| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| cl-001 | S01 | positive/negative `rg`; diff inspection | pass | scaffold / evidence / example boundary wording present |
| cl-002 | S01 | report-slot `rg` across Initiative / Epic / Issue report templates | pass | evidence slots preserved |
| cl-003 | S01 | issue plan template `rg` and diff inspection | pass | policy/detail routing points to skills/docs |
| cl-005 | S01 | `git diff --name-only`; `git diff --check`; provider/mirror `diff -q` | pass | S01 scope contained |
| cl-004 | S02 | positive/negative `rg`; diff inspection; provider/mirror `diff -q` | pass | discussion templates support source-grounded evidence flow |
| cl-005 | S02 | `git diff --name-only`; `git diff --check`; provider/mirror `diff -q` | pass | S02 scope contained |

## レビューゲート状態（Reviewer Gate Status）

| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| requirement | phase reviewer | spec-reviewer `019e9bd8-6cb4-74c0-87ed-59b38fed08dd` | fresh | pass | no | promoted to design | initial P1 fixed; re-review had no findings |
| design | phase reviewer | spec-reviewer `019e9bdc-d8dd-7b00-a467-f1dea73d8531` | fresh | pass | no | promoted to plan | no findings |
| plan | phase reviewer | spec-reviewer `019e9bdf-9f9e-7d83-8ce3-672c6231b5f4` | fresh after fix | pass | no | promoted to issue execution | no findings; plan ready for execution handoff |
| S01 | step reviewer | spec-reviewer `019e9bef-59aa-78b0-8aed-959c201a3630` | fresh | pass | no | commit S01 | one P3 report wording correction applied |
| S02 | step reviewer | spec-reviewer `019e9bf5-628e-7771-85fb-98eea5a92640` | fresh | pass | no | commit S02 | no findings |

## ステップ commit ゲート（Step Commit Gate）

| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） |
|---|---|---|---|---|
| planning-requirement/design/plan | committed | requirement/design/plan/report authoring evidence | `f7413abf` | clean before S01 delegation |
| S01 | committed | S01 provider/mirror template changes + report evidence | `54e8ea40` | clean before S02 delegation |
| S02 | pending commit | S02 provider/mirror discussion template changes + report evidence | pending | pending |

## 最終品質ゲート（Final Quality Gate）

- Not started. Final QA/code/spec gates run after implementation and docs impact are committed.

## 省略/例外メモ

- User interview blocker: none.
- Deep-consultant/user-proxy path: not used; current user correction requires asking the user directly if a true blocker appears.
