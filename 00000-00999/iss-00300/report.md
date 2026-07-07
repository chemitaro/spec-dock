---
種別: 実装報告書（Issue）
ID: "iss-00300"
タイトル: "Backend Invocation Adapter"
関連GitHub: ["#300"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00295", "init-local-00003"]
Issue Grade: "standard"
---

# iss-00300 Backend Invocation Adapter — 実装報告

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger）

| ID | Status | Type | Raised By | Gap | Options | Decision | Rationale | Disposition | Evidence | Follow-up |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D-PLN-001 | resolved | scope | ChatGPT planning evidence | `authoring backend invoke` が未実装で、prompt pack と backend command の接続面がない | A: helper のみ維持; B: installed runtime command に昇格 | B を採用。ただし backend invocation のみ。 | Epic 00295 の runtime plane に backend invocation が含まれるため。 | promoted_to_design | `design.md` Target Design Delta | none |
| D-PLN-002 | resolved | operation | ChatGPT planning evidence | backend command source の優先順位 | A: env only; B: CLI override first; C: hardcoded wrapper | B。`--backend-command` -> `SPECDOCK_CHATGPT_COMMAND` -> optional `ORACLE_CHATGPT_COMMAND`。 | task brief と installed runtime portability requirement に一致。 | promoted_to_requirement | `requirement.md` RQ-002..RQ-005 | `ORACLE_CHATGPT_COMMAND` deprecation schedule は Epic open question |
| D-PLN-003 | resolved | security | ChatGPT planning evidence | shell injection / secret exposure / host-local path leakage risk | A: shell execution; B: argv + redacted summary | B。`shlex.split` + no shell execution + redacted durable summary。 | external process を扱うため fail-closed と redaction が必要。 | promoted_to_design | `design.md` Domain / Redaction Design | none |
| D-PLN-004 | resolved | scope | User / Epic policy | 中間 Issue の PR delivery | A: iss-00300 で PR; B: final quality Issue に defer | B。`iss-00307` に defer。 | Epic は Issue relay 方式で最後に 1 PR を作る。 | promoted_to_plan | `plan.md` PR Delivery Policy | none |
| D-PLN-005 | resolved | interpretation | ChatGPT planning evidence | backend success と adoption success の混同 | A: backend exit 0 を adoption success と扱う; B: invocation-local success に限定 | B。backend exit 0 は invocation success のみ。 | authority boundary を維持するため。 | promoted_to_requirement | `requirement.md` RQ-012 / AC-011 | none |
| D-REV-001 | resolved | contract | spec-reviewer | backend invocation argv ABI が曖昧 | A: stdin/envで任意; B: `--slug` / `-p` / repeated `--file` ABI を固定 | B を採用。`--output-dir` は backend に渡さず adapter summary 用に限定。 | 実装者とテストが同じ backend interface を検証できるようにするため。 | promoted_to_design | `design.md` Backend argv ABI; `plan.md` S04 / TC-008 | none |
| D-REV-002 | resolved | contract | spec-reviewer | prompt pack required metadata が曖昧 | A: readable filesだけ; B: required files / JSON fields / authority boundary を明記 | B を採用。既存 prompt pack contract の必須ファイルと fields を design に明記。 | AC-008 / CL-008 / TC-011 の fail-closed 条件を実装可能にするため。 | promoted_to_design | `design.md` PromptPackInput | none |

## 証跡採用台帳（Evidence Adoption Ledger）

| ID | adoption_status | source | target | rationale | evidence | next_action |
| --- | --- | --- | --- | --- | --- | --- |
| EAL-PLN-001 | partially_adopted | ChatGPT Use prompt / task brief | requirement.md / design.md / plan.md / report.md | iss-00300 の目的、制約、output 要求を採用。ただし reviewer pass / execution-ready / PR-ready claim は除外。 | `artifacts/20260708-chatgpt-use-planning-evidence-summary.md` | spec-reviewer review |
| EAL-PLN-002 | adopted | draft requirement artifact | requirement.md | purpose、scope、non-scope、acceptance criteria を正式要件へ再記述した。 | `artifacts/20260707t171251z-draft-requirement-implement-backend-invocation-adapter-draft-requirement.md` | none |
| EAL-PLN-003 | adopted | draft design artifact | design.md | target paths、runtime/docs/skill impact、failure modes を正式設計へ統合した。 | `artifacts/20260707t171251z-01-draft-design-implement-backend-invocation-adapter-draft-design.md` | none |
| EAL-PLN-004 | adopted | draft plan artifact | plan.md | step sequence と verification seeds を closure index / milestone plan へ拡張した。 | `artifacts/20260707t171252z-draft-plan-implement-backend-invocation-adapter-draft-plan.md` | none |
| EAL-PLN-005 | partially_adopted | ChatGPT planning response | requirement.md / design.md / plan.md / report.md | command priority、dry-run、redaction、local-context authority、PR defer policy を採用。raw transcript、reviewer pass、execution-ready claim は採用しない。 | `artifacts/20260708-chatgpt-use-planning-evidence-summary.md` | spec-reviewer review |
| EAL-REV-001 | adopted | spec-reviewer finding | requirement.md / design.md / plan.md / report.md | P1 backend argv ABI gap と P2 prompt-pack metadata gap を採用して planning docs に反映した。 | spec-reviewer review result `review_status: fail` | re-review |
| EAL-REV-002 | adopted | spec-reviewer re-review | report.md | backend argv ABI と prompt pack metadata の修正後に fresh pass を確認した。 | spec-reviewer review result `review_status: pass` | none |

## 目的整合台帳（Objective Alignment Ledger）

| 対象 | primary objective evidence | secondary requirement evidence | inversion risk | reviewer verdict |
| --- | --- | --- | --- | --- |
| OAL-PLN-001 | `authoring backend invoke` を explicit backend command で fail-closed に実装する planning package | redaction、local-context lower authority、no PR delivery | low | spec-reviewer pass |
| OAL-PLN-002 | backend invocation only; no ZIP/stage/adoption expansion | compatibility script / docs updates | medium | spec-reviewer pass |

## 仕様 authoring ゲート（Spec Authoring Gate）

| phase | investigated facts | open questions / answers | adoption decision | reviewer verdict | blocking | promotion / next_action |
| --- | --- | --- | --- | --- | --- | --- |
| requirement | Epic docs、Issue draft artifacts、ChatGPT Use planning evidence、existing `authoring` command surface | `ORACLE_CHATGPT_COMMAND` deprecation schedule はこの Issue では決めない | adopted into `requirement.md` | pass | no | promote |
| design | existing `pack_prepare` contract、prompt pack authority boundary、draft design、ChatGPT design proposal | provider registry は non-scope | adopted into `design.md` | pass | no | promote |
| plan | draft plan、ChatGPT closure index、relay PR delivery policy | final PR delivery は `iss-00307` | adopted into `plan.md` | pass | no | promote |

## 委任ドラフト証跡（Delegated Draft Evidence）

| created_by_role | scope_id | artifact draft path | source_paths | intended_targets | adoption_status | reflected_to | diff_guard_result | integration result | rejected portions | blockers | reviewer result | promotion decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ChatGPT Use / GPT-5.5 Pro Extended | iss-00300 | `artifacts/20260708-chatgpt-use-planning-evidence-summary.md` | Epic docs、Issue draft artifacts、runtime command files、tests | `requirement.md`, `design.md`, `plan.md`, `report.md` | partially_adopted | `requirement.md`, `design.md`, `plan.md`, `report.md` | pass | integrated by orchestrator | reviewer pass and execution-ready claims were not adopted without local review | none | pass | promote |

## ワークフロー単位の named role 許可（Workflow-Scoped Authorization）

| authorization source | repo/worktree | active issue | session | named roles | boundary | expires / invalidation | denied / unavailable / host conflict reason | next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| user request to execute Epic through SpecDock workflow | `chemitaro/spec-dock` / current worktree | iss-00300 | current session | spec-reviewer / code-reviewer / qa-reviewer / dev-coder / doc-writer | active repo/worktree、active SpecDock scope、current session、SpecDock-defined named roles、documented role responsibility | issue complete / scope change / user revocation / host policy conflict | none | continue |

## グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）

| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |
| --- | --- | --- | --- | --- | --- |
| `standard` | manual fallback | used | manual evidence from ChatGPT Use planning package plus orchestrator adoption in `artifacts/20260708-chatgpt-use-planning-evidence-summary.md`, `requirement.md`, `design.md`, and `plan.md` | pass | ready |

## レビューゲート状態（Reviewer Gate Status）

| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| planning | spec planning review | spec-reviewer | fresh | pass | no | promote | Re-review passed after backend argv ABI and prompt pack metadata contract were clarified. |
| implementation | code review | code-reviewer | pending | pending | no | blocked | Required after implementation. |
| implementation | QA review | qa-reviewer | pending | pending | no | blocked | Required after implementation. |
| final-local | final spec review | spec-reviewer | pending | pending | no | blocked | Required after implementation evidence. |

## 実装委任ゲート（Implementation Delegation Gate）

| step | decision | required reason | delegated role | delegated scope | source of truth | allowed changes | forbidden changes | required verification | stop conditions | output required | observed result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S01-S07 | delegated ok | runtime command / shipped scaffold / tests | dev-coder | approved plan implementation | `requirement.md`, `design.md`, `plan.md` | allowed change surface in `plan.md` | non-scope commands, hardcoded local path, PR delivery | focused pytest, validate, assurance, diff check | scope expansion, unsafe authority claim | worker summary / changed files / verification / risks | pending |
| S90 | delegated ok | report/docs evidence | doc-writer or orchestrator | report evidence updates | `plan.md`, observed verification | `report.md` only unless docs impact discovered | new requirements / reviewer pass self-claim | docs inspection / validate | unresolved doc impact | updated evidence rows | pending |

## 実装記録（セッションログ）

### セッションログ（2026-07-08 planning）

#### 対象

- Phase: Issue planning
- AC: AC-001..AC-017

#### 実施内容

- `iss-00300` の scaffold requirement を正式要件へ置き換えた。
- `assurance classify --stage requirement` を実行し、`authorized_profile=standard` を確認した。
- `assurance compose --artifact all` を実行し、Standard 用の design / plan / report surface を生成した。
- ChatGPT Use planning evidence と Issue-local draft artifacts を採用し、`design.md` / `plan.md` / `report.md` を具体化した。

#### 実行コマンド / 結果

```bash
./spec-dock/scripts/spec-dock assurance classify --stage requirement

assurance classify: ok
issue: iss-00300
mode: adaptive
has_contract: true
authorized_profile: standard
complexity_tier: normal
lite_candidate: false
lite_authorized: false
reason: ok
```

```bash
./spec-dock/scripts/spec-dock assurance compose --artifact all

assurance compose: ok
issue: iss-00300
authorized_profile: standard
```

## 最終品質ゲート（Final Quality Gate）

| Gate | Status | Evidence |
| --- | --- | --- |
| Planning docs authored | pass | `requirement.md`, `design.md`, `plan.md` updated |
| Spec review | pending | Must run before implementation |
| Implementation tests | pending | To be recorded after implementation |
| Code review | pending | To be recorded after implementation |
| QA review | pending | To be recorded after implementation |
| PR delivery | deferred | final quality gate Issue `iss-00307` |

## PR Delivery Defer Evidence

| Item | Evidence |
| --- | --- |
| final quality Issue | `iss-00307` |
| rationale | Epic 00295 requires no per-Issue PR. Intermediate Issues are finished one by one, and a single mergeable PR is delivered at the final quality gate. |
| current Issue behavior | `iss-00300` may finish after local quality gates and reviewer passes, but must not create a PR. |
| merge-prepared claim | not claimed |
