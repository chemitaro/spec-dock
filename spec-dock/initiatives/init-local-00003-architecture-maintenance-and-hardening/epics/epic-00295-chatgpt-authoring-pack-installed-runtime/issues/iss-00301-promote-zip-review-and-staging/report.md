---
種別: 実装報告書（Issue）
ID: "iss-00301"
タイトル: "Zip Review Staging"
関連GitHub: ["#301"]
状態: "in-progress"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00295", "init-local-00003"]
Issue Grade: "standard"
---

# iss-00301 Zip Review Staging — 実装報告

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger）

| ID | Status | Type | Raised By | Gap | Options | Decision | Rationale | Disposition | Evidence | Follow-up |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D-001 | resolved | scope | orchestrator | ZIP/tree review と stage が canonical adoption と混同されるリスク | A: review/stage のみ実装; B: adoption まで含める | A を採用 | Epic requirement/design は ChatGPT output を evidence-only とし、adoption / approval / reviewer pass は後続 Issue の責務に分けている | promoted_to_design | `requirement.md`, `design.md` | none |
| D-002 | resolved | operation | orchestrator | tree fallback を ZIP review pass と同格に扱うか | A: 同格; B: lower authority fallback | B を採用 | ZIP central directory evidence がないため、安全証跡が弱い | promoted_to_design | `design.md#treefallbackreview` | none |
| D-003 | resolved | compatibility | spec-reviewer | Issue docs が metadata missing / source hash mismatch を `rejected` としており、親 Epic の `fail` / `stale` taxonomy と矛盾した | A: Issue 独自 status; B: parent Epic taxonomy に合わせる | B を採用 | Epic design が status taxonomy authority であり、downstream automation が status を読む | applied | spec-reviewer finding P1; `requirement.md`, `design.md`, `plan.md` | none |
| D-004 | resolved | test-strategy | spec-reviewer | implementation steps が executable step schema を満たしていない | A: global plan のまま; B: S01-S07 に step-local contract を追加 | B を採用 | Standard Issue の worker/reviewer が fixture、Red/Green、report destination を判断せず実行できる必要がある | applied | spec-reviewer finding P1; `plan.md` | none |
| D-005 | resolved | test-strategy | spec-reviewer | unsafe stage target の期待 status が `rejected or blocked` と曖昧だった | A: 複数 status を許容; B: unsafe stage target は `rejected` に統一 | B を採用 | deterministic diagnostics を守り、requirement/design の stage target rejection と一致させる | applied | spec-reviewer P2; `plan.md` tc-s05-003 | none |

## 証跡採用台帳（Evidence Adoption Ledger）

| ID | adoption_status | source | target | rationale | evidence | next_action |
| --- | --- | --- | --- | --- | --- | --- |
| EAL-001 | adopted | draft-requirement | `requirement.md` | Scope、non-scope、acceptance seeds を正式要件へ統合した | `artifacts/20260707t171255z-draft-requirement-promote-zip-review-and-staging-draft-requirement.md` | spec-review |
| EAL-002 | adopted | draft-design | `design.md` | Target paths、failure modes、stage boundary を正式設計へ統合した | `artifacts/20260707t171255z-01-draft-design-promote-zip-review-and-staging-draft-design.md` | spec-review |
| EAL-003 | adopted | draft-plan | `plan.md` | Step sequence、verification seeds、relay policy を正式計画へ統合した | `artifacts/20260707t171256z-draft-plan-promote-zip-review-and-staging-draft-plan.md` | spec-review |
| EAL-004 | adopted | assurance-classify-compose | `.assurance.json` and docs | `assurance classify` で `standard` が確定し、`assurance compose` で設計・計画・report scaffold を生成した | `./spec-dock/scripts/spec-dock assurance classify --stage requirement`; `./spec-dock/scripts/spec-dock assurance compose --artifact all` | assurance verify |

## 目的整合台帳（Objective Alignment Ledger）

| 対象 | primary objective evidence | secondary requirement evidence | inversion risk | reviewer verdict |
| --- | --- | --- | --- | --- |
| OAL-001 | `authoring pack review/stage` を安全検査・staging command として実装する | canonical adoption / approval / PR delivery は non-scope として後続 Issue へ分離 | low | pass |

## 仕様 authoring ゲート（Spec Authoring Gate）

| phase | investigated facts | open questions / answers | adoption decision | reviewer verdict | blocking | promotion / next_action |
| --- | --- | --- | --- | --- | --- | --- |
| requirement | Epic requirement/design/plan、Issue draft requirement、existing authoring command/tests | none | adopted into `requirement.md` | pass | no | promote |
| design | Issue requirement、Issue draft design、existing command and prompt pack contract | none | adopted into `design.md` | pass | no | promote |
| plan | Issue requirement/design、Issue draft plan、verification queue | none | adopted into `plan.md` | pass | no | promote |

## 委任ドラフト証跡（Delegated Draft Evidence）

| created_by_role | scope_id | artifact draft path | source_paths | intended_targets | adoption_status | reflected_to | diff_guard_result | integration result | rejected portions | blockers | reviewer result | promotion decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ChatGPT authoring pack | iss-00301 | `artifacts/20260707t171255z-draft-requirement-promote-zip-review-and-staging-draft-requirement.md` | `spec-dock/active/epic/requirement.md`; `spec-dock/active/epic/design.md`; `spec-dock/active/epic/plan.md`; draft requirement path | `requirement.md` | adopted | [`requirement.md`] | pass: manual diff guard confirmed no unsupported adoption/reviewer/PR-ready self-claim was promoted | integrated | none | none | pass | promote |
| ChatGPT authoring pack | iss-00301 | `artifacts/20260707t171255z-01-draft-design-promote-zip-review-and-staging-draft-design.md` | `spec-dock/active/epic/requirement.md`; `spec-dock/active/epic/design.md`; `spec-dock/active/epic/plan.md`; draft design path | `design.md` | adopted | [`design.md`] | pass: manual diff guard confirmed design boundaries remain evidence-only and non-scope commands are not promoted | integrated | none | none | pass | promote |
| ChatGPT authoring pack | iss-00301 | `artifacts/20260707t171256z-draft-plan-promote-zip-review-and-staging-draft-plan.md` | `spec-dock/active/epic/requirement.md`; `spec-dock/active/epic/design.md`; `spec-dock/active/epic/plan.md`; draft plan path | `plan.md` | adopted | [`plan.md`] | pass: manual diff guard confirmed relay/no-per-Issue-PR policy remains deferred to `iss-00307` | integrated | none | none | pass | promote |

## 実装記録（セッションログ）

### セッションログ（2026-07-08 planning）

#### 対象

- Step: Planning adoption
- AC/EC: AC-001..AC-015

#### 実施内容

- Active issue `iss-00301` の scaffold requirement / placeholder design / placeholder plan を確認した。
- Issue-local draft requirement/design/plan を読み、Epic requirement/design/plan と照合した。
- `requirement.md` を正式要件として作成した。
- `assurance classify --stage requirement` を実行し、`authorized_profile=standard` を確認した。
- `assurance compose --artifact all` を実行し、Standard profile の設計・計画・report scaffold を生成した。
- `design.md` と `plan.md` を正式版へ置き換えた。

#### 実行コマンド / 結果

```bash
./spec-dock/scripts/spec-dock guidance issue-planning
# state: requirement-capture; reason_code: requirement-scaffold

./spec-dock/scripts/spec-dock assurance classify --stage requirement
# assurance classify: ok
# authorized_profile: standard

./spec-dock/scripts/spec-dock assurance compose --artifact all
# assurance compose: ok
# changed_paths: design.md, plan.md, report.md
```

#### ワークフロー単位の named role 許可（Workflow-Scoped Authorization）

| authorization source | repo/worktree | active issue | session | named roles | boundary | expires / invalidation condition | denied / unavailable / host conflict reason | next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| user request to continue SpecDock workflow | `/Users/iwasawayuuta/.codex/worktrees/aa9c/spec-dock` | iss-00301 | current session | spec-reviewer / code-reviewer / qa-reviewer | active repo/worktree、active SpecDock scope、current session、SpecDock-defined named roles、documented role responsibility | issue complete / session end / scope change / user revocation | none | continue |

## 実装委任ゲート（Implementation Delegation Gate）

| step | decision | required reason | delegated role | delegated scope | source of truth | allowed changes | forbidden changes | required verification | stop conditions | output required | observed result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S01-S07 | pending | runtime command / shipped scaffold / tests | dev-coder or parent exception | authoring pack review/stage implementation | `requirement.md`, `design.md`, `plan.md` | plan change surface | non-scope adoption / PR / `.assurance.json` mutation | focused pytest, CLI smoke, validate, assurance verify | unresolved spec-review finding | worker summary / changed files / verification | pending |

## レビューゲート状態（Reviewer Gate Status）

| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| planning | spec authoring review | spec-reviewer | fresh | pass | no | promote | re-review resolved P1 blockers; P2 unsafe stage target status made deterministic |
| planning | spec authoring review | spec-reviewer | fresh first review | failed | no | re-review required | P1 executable step contract and status taxonomy findings fixed in docs; P2 draft provenance tightened |
| implementation | final code review | code-reviewer | not started | pending | no | pending | after implementation |
| implementation | final QA review | qa-reviewer | not started | pending | no | pending | after verification |

## グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）

| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |
| --- | --- | --- | --- | --- | --- |
| `standard` | manual fallback | manual fallback | manual authoring fallback evidence: Epic docs、Issue draft artifacts、existing runtime/tests を orchestrator が照合して正式 docs へ採用 | pass | ready |

## 最終品質ゲート（Final Quality Gate）

### ドキュメント影響の解消ステップ S90

| 対象 | 更新要否 | owner | evidence | spec-reviewer result |
| --- | --- | --- | --- | --- |
| runtime command docs / compatibility scripts | yes if implementation changes help or shipped scripts | orchestrator / doc-writer if needed | pending | pending |

### 最終 QA ゲート

| reviewer | 範囲 | integration test decision | evidence | result |
| --- | --- | --- | --- | --- |
| qa-reviewer | issue-wide obligation coverage | pending | pending | pending |

### 最終コードレビューゲート

| reviewer | 範囲 | findings / fixes | re-review count | result |
| --- | --- | --- | --- | --- |
| code-reviewer | issue-wide integrated diff | pending | 0 | pending |

### 最終 spec review ゲート

| reviewer | 範囲 | findings / fixes | re-review count | result |
| --- | --- | --- | --- | --- |
| spec-reviewer | requirement / design / plan / report / implementation / tests / docs alignment | pending | 0 | pending |

### 最終 commit

| final report ledger | final commit scope | post-commit external evidence destination | result |
| --- | --- | --- | --- |
| pending | pending | final response / later `iss-00307` PR | pending |

## 省略/例外メモ

- この Issue では PR を作成しない。Epic 単位の PR は final quality gate Issue `iss-00307` で作成する。
