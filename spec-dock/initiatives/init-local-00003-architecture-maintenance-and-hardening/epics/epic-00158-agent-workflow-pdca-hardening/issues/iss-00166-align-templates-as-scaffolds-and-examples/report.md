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

- Implementation has not started.
- Current work is issue planning / spec authoring for requirement/design/plan readiness.

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

## レビューゲート状態（Reviewer Gate Status）

| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| requirement | phase reviewer | spec-reviewer `019e9bd8-6cb4-74c0-87ed-59b38fed08dd` | fresh | pass | no | promoted to design | initial P1 fixed; re-review had no findings |
| design | phase reviewer | spec-reviewer `019e9bdc-d8dd-7b00-a467-f1dea73d8531` | fresh | pass | no | promoted to plan | no findings |
| plan | phase reviewer | spec-reviewer `019e9bdf-9f9e-7d83-8ce3-672c6231b5f4` | fresh after fix | pass | no | promoted to issue execution | no findings; plan ready for execution handoff |

## ステップ commit ゲート（Step Commit Gate）

| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） |
|---|---|---|---|---|
| planning-requirement | pending reviewer | requirement/report authoring evidence | pending | pending |
| planning-design | pending reviewer | design/report authoring evidence | pending | pending |
| planning-plan | pending reviewer | plan/report authoring evidence | pending | pending |

## 最終品質ゲート（Final Quality Gate）

- Not started. Final QA/code/spec gates run after implementation and docs impact are committed.

## 省略/例外メモ

- User interview blocker: none.
- Deep-consultant/user-proxy path: not used; current user correction requires asking the user directly if a true blocker appears.
