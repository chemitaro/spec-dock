---
種別: 実装報告書（Issue）
ID: "iss-00257"
タイトル: "Severity Aware Codex PR Review Policy And Non Blocking Repair Loop Hardening"
関連GitHub: ["#257"]
状態: "reviewed"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00257 Severity Aware Codex PR Review Policy And Non Blocking Repair Loop Hardening — 実装報告

この report は、Issue Planning / clarification / implementation / verification の観測証跡台帳である。現時点では要件定義書、設計書、実装計画書の段階的 authoring と spec-reviewer gate までを記録する。

## Spec Interpretation / Decision Ledger

| ID | Status | Type | Raised By | Gap | Options | Decision | Rationale | Disposition | Evidence | Follow-up |
|---|---|---|---|---|---|---|---|---|---|---|
| D-001 | resolved | scope | user | 親 Epic には旧 P2 promotion 方針があるが、この Issue では新方針を採用する必要がある | 親 docs も更新 / Issue 内限定 override | Issue 内限定で `P2 + protected_domain + machine_evidence` promotion を廃止し、親 Epic docs は編集しない | 親 Epic は別 worktree で作業中というユーザー制約がある | applied | `discussions/20260701t022257z-interview-parent-epic-p2-promotion-policy.md`, `requirement.md` | none |
| D-002 | resolved | implementation | user | bundle は `root_cause_family` を強く示すが現行 runtime は `blocker_fingerprint` contract | runtime first-class / docs-only / optional metadata | Option B: docs / LLM judgement / operational triage vocabulary に限定する | runtime parser と stalled semantics を広げず、主目的の P2/P3 non-blocking 化に集中する | applied | `discussions/20260701t023858z-interview-root-cause-family-runtime-scope.md`, `design.md` | none |
| D-003 | resolved | operation | orchestrator | Issue Planning 導入初回運用で、workflow の違和感を残す必要がある | product requirement に混ぜる / discussion と report に分離 | Dogfooding note を discussion artifact に分離し、採用分だけ report に反映する | 本筋の PR review policy 要件と workflow 改善観察を混ぜない | applied | `discussions/20260701t025116z-research-issue-planning-dogfooding-notes.md` | Possible future workflow polish, non-blocking |
| D-004 | resolved | operation | orchestrator | 誤って no-op spec-reviewer を起動した | 採用 / 不採用 | no-op reviewer は workflow evidence として不採用 | 対象 artifact をレビューしていないため | rejected | subagent `019f1ba9-9921-7212-83a5-e26b782610c3` | none |
| D-005 | resolved | test-strategy | spec-reviewer | Plan の CLOS-004 が terminal P2/P3-only no-mutation 境界を具体的に閉じていなかった | そのまま / CLOS と step を追加 | `CLOS-004A` と `S40` を追加し、batch persistence / commit-push / re-review / repair loop の証跡を要求 | Plan phase review P1 finding | applied | plan review `019f1baf-8f38-7833-bca6-21c4a48fe275`, `plan.md` | none |
| D-006 | resolved | test-strategy | spec-reviewer | Parent Epic 非編集 evidence が symlink path だけだと弱い | symlink path / real parent docs path | 実体 parent Epic docs path を plan の検証コマンドと report evidence requirement に明示 | Plan re-review P2 finding | applied | plan re-review `019f1bb1-e3c3-7b70-a79a-94be1be82475`, `plan.md` | none |
| D-007 | resolved | operation | user | SpecDock workflow が必要とする named sub-agent / reviewer を追加許可待ちで省略する判断が発生した | 現状維持 / runtime consent schema / instruction hardening | SpecDock workflow invocation を workflow-scoped named role authorization として instruction / docs / skill に明文化する | SpecDock は workflow-defined named roles を orchestrator が自律的に使い分ける前提であり、複雑な runtime consent schema は不要 | applied | supplemental user instruction, `requirement.md`, `design.md`, `plan.md` | none |

## Evidence Adoption Ledger

| ID | adoption_status | source | target | rationale | evidence | next_action |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | research | `requirement.md`, `design.md`, `plan.md` | 添付 bundle と現行 repo 差分、tests、edge cases を突き合わせ済み | `discussions/20260701t023648z-research-pr-review-policy-clarification-research.md` | none |
| EAL-002 | adopted | discussion / user answer | `requirement.md`, `design.md`, `plan.md` | Issue-local P2 promotion 廃止と親 Epic docs 非編集が明確化された | `discussions/20260701t022257z-interview-parent-epic-p2-promotion-policy.md` | none |
| EAL-003 | adopted | discussion / user answer | `requirement.md`, `design.md`, `plan.md` | `root_cause_family` を runtime contract にしない範囲が確定した | `discussions/20260701t023858z-interview-root-cause-family-runtime-scope.md` | none |
| EAL-004 | adopted | command evidence | design.md and plan.md and report.md | assurance classify and compose produced standard profile planning artifacts | command evidence recorded in Implementation Session Log | none |
| EAL-005 | adopted | research / dogfooding | this report | Issue Planning workflow の初回運用観察を正本 report に反映した | `discussions/20260701t025116z-research-issue-planning-dogfooding-notes.md` | Track future polish outside this Issue if needed |
| EAL-006 | adopted | reviewer | `requirement.md` | Requirement phase pass により design phase へ進める | spec-reviewer `019f1ba9-6a28-7890-8dcc-6e17cca335b2` | none |
| EAL-007 | adopted | reviewer | `design.md` | Design phase pass により plan phase へ進める | spec-reviewer `019f1bac-2f1c-7720-bf8b-4e95f443562b` | none |
| EAL-008 | partially_adopted | reviewer | `plan.md` | Initial plan review failed with one P1 finding; finding was fixed and re-reviewed | spec-reviewer `019f1baf-8f38-7833-bca6-21c4a48fe275` | none |
| EAL-009 | adopted | reviewer | `plan.md` | Re-review passed; P2 evidence-path correction was incorporated | spec-reviewer `019f1bb1-e3c3-7b70-a79a-94be1be82475` | none |
| EAL-010 | rejected | reviewer | none | Accidental no-op reviewer reviewed no artifacts and is not valid workflow evidence | spec-reviewer `019f1ba9-9921-7212-83a5-e26b782610c3` | none |
| EAL-011 | adopted | user instruction | requirement.md and design.md and plan.md | SpecDock workflow invocation authorization hardening was added to planning scope | supplemental user instruction in current session | fresh spec-reviewer after scope update |
| EAL-012 | adopted | reviewer | requirement.md and design.md and plan.md and report.md | Supplemental authorization scope re-review passed after P1/P2 fixes | spec-reviewer `019f1bc3-0837-73c2-841d-6c935120e3a7` | none |

## Objective Alignment Ledger

| Target | Primary objective evidence | Secondary requirement evidence | Inversion risk | Reviewer verdict |
|---|---|---|---|---|
| Severity-aware PR review policy | `requirement.md` defines P0/P1 blocking, P2/P3 reportable non-blocking, and no P2 promotion | Dogfooding notes and `root_cause_family` docs-only vocabulary are captured but scoped | low | pass |

## Spec Authoring Gate

| Phase | Investigated facts | Open questions / answers | Adoption decision | Reviewer verdict | Blocking | Promotion / next_action |
|---|---|---|---|---|---|---|
| requirement | ZIP bundle, current code/tests/assets, parent Epic constraint, discussions, supplemental authorization scope | Parent docs do not edit; root_cause_family Option B docs-only; workflow-scoped named role authorization | adopted into requirement artifact | passed | no | promote |
| design | Requirement pass, current runtime and asset structure, mirror parity tests, authorization docs surfaces | none | adopted into design artifact | passed | no | promote |
| plan | Design pass, closure IDs, target files, focused tests, forbidden changes, authorization hardening step | Initial no-mutation verification gap fixed via CLOS-004A and S40; CLOS-010 added | adopted into plan artifact | passed | no | promote |

## Delegated Draft Evidence

| Role | Scope | Draft path | Source paths | Intended targets | Adoption status | Reflected to | Diff guard result | Integration result | Rejected portions | Blockers | Reviewer result | Promotion decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| N/A | iss-00257 | N/A | N/A | N/A | not used | [] | not_run | manual authoring by main orchestrator | N/A | none | passed | promote |

## Grade Specialist Evidence Gate

| Profile | Required or fallback | Usage | Evidence | Reviewer verdict | Readiness |
|---|---|---|---|---|---|
| standard | manual authoring fallback | not used | manual-authored canonical docs reviewed by fresh spec-reviewer passes | passed | ready |

## Reviewer Gate Status

| Step | Gate | Reviewer role | Freshness | State | Risk acceptance | Completion decision | Notes |
|---|---|---|---|---|---|---|---|
| requirement | requirement authoring review | spec-reviewer | fresh | passed | no | promote | `019f1ba9-6a28-7890-8dcc-6e17cca335b2` |
| design | design authoring review | spec-reviewer | fresh | passed | no | promote | `019f1bac-2f1c-7720-bf8b-4e95f443562b` |
| plan | plan authoring review | spec-reviewer | fresh | passed | no | promote | P1 fixed via `CLOS-004A` and `S40`; pass from `019f1bb1-e3c3-7b70-a79a-94be1be82475` |
| ignored | accidental no-op review | spec-reviewer | stale | rejected | no | no_action | `019f1ba9-9921-7212-83a5-e26b782610c3`; no artifacts reviewed |

## Implementation Session Log

### セッションログ（2026-07-01）

#### 対象

- Phase: issue planning authoring redo
- Closures: CLOS-009 authoring evidence

#### 実施内容

- User instruction に従い、先行して一括具体化した canonical docs を template 状態へ戻した。
- Requirement のみを具体化し、spec-reviewer pass を取得した。
- `assurance classify --stage requirement` と `assurance compose --artifact all` を実行した。
- Design のみを具体化し、spec-reviewer pass を取得した。
- Plan を具体化し、spec-reviewer review を実施した。
- Plan review P1 finding に従い、terminal P2/P3-only no-mutation 境界を `CLOS-004A` / `S40` として追加した。
- Plan re-review pass 後、P2 finding に従い parent Epic docs 実体 path の diff evidence を plan に明記した。
- User supplemental instruction に従い、SpecDock workflow-scoped named role authorization hardening を requirement/design/plan scope に追加した。

#### 実行コマンド / 結果

```bash
./spec-dock/scripts/spec-dock guidance issue-planning
# requirement-capture / requirement-scaffold を確認

./spec-dock/scripts/spec-dock assurance classify --stage requirement
# assurance classify: ok
# authorized_profile: standard

./spec-dock/scripts/spec-dock assurance compose --artifact all
# assurance compose: ok

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate)
```

#### Test / Review Evidence

| Step | Evidence | Result | Notes |
|---|---|---|---|
| requirement authoring | spec-reviewer `019f1ba9-6a28-7890-8dcc-6e17cca335b2` | pass | no findings |
| design authoring | spec-reviewer `019f1bac-2f1c-7720-bf8b-4e95f443562b` | pass | no findings |
| plan authoring | spec-reviewer `019f1baf-8f38-7833-bca6-21c4a48fe275` | fail | P1 no-mutation verification gap |
| plan re-review | spec-reviewer `019f1bb1-e3c3-7b70-a79a-94be1be82475` | pass | P1 fixed; P2 evidence path incorporated |
| final scope update review | pending fresh spec-reviewer | pending | authorization hardening scope added after previous pass |

#### 変更したファイル

- `spec-dock/active/issue/requirement.md` - Requirement concrete draft, reviewer-passed.
- `spec-dock/active/issue/design.md` - Design concrete draft, reviewer-passed.
- `spec-dock/active/issue/plan.md` - Plan concrete draft, reviewer-passed after one fix.
- `spec-dock/active/issue/report.md` - Authoring and reviewer evidence ledger.
- `spec-dock/active/issue/discussions/20260701t023858z-interview-root-cause-family-runtime-scope.md` - User answer captured.
- `spec-dock/active/issue/discussions/20260701t025116z-research-issue-planning-dogfooding-notes.md` - Dogfooding observations.

## Final Quality Gate

### Docs Impact Resolution

| Target | Update needed | Owner | Evidence | spec-reviewer result |
|---|---|---|---|---|
| Issue-local requirement/design/plan/report | yes | main orchestrator | this report | pass |
| Parent Epic docs | no | N/A | real parent doc path diff required by `plan.md` | N/A |
| Non-issue workflow docs / skill docs / orchestrator instructions | yes | dev-coder or doc-writer during implementation | CLOS-010 / S50 require provider and dogfooding updates for workflow-scoped named role authorization | pass |

### Final Spec Review Gate

| Reviewer | Scope | Findings / fixes | Re-review count | Result |
|---|---|---|---|---|
| spec-reviewer | requirement/design/plan/report alignment after supplemental authorization scope | Fresh review found report/docs-impact and skill-scope issues; fixes applied; re-review passed | 2 | pass |

### Final Commit

| Final report ledger | Final commit scope | Post-commit evidence destination | Result |
|---|---|---|---|
| this report | planning docs only for current turn | final response | ready for implementation workflow |

## 遭遇した問題と解決

- 誤って no-op spec-reviewer を一件起動したが、対象 artifact をレビューしていないため workflow evidence として不採用にした。
- Plan review で terminal P2/P3-only no-mutation の検証不足が見つかったため、`CLOS-004A` と `S40` を追加して再レビュー pass を得た。
- Supplemental authorization scope review で stale docs impact gate と epic/initiative skill path ambiguity が見つかったため、`report.md` と `plan.md` を更新した。

## 省略/例外メモ

- 実装変更、実装テスト、commit はまだ行っていない。
- Parent Epic docs は編集していない。
