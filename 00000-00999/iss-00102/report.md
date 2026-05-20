---
種別: 実装報告書（Issue）
ID: "iss-00102"
タイトル: "Agentic TDD plan step contract"
関連GitHub: ["#102"]
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-05-20"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00102 Agentic TDD plan step contract — 実装報告（LOG）

## 実装サマリー (任意)
- 実装開始。`plan.md` に従い、S01 から provider-side shipped docs を更新する。
- 親 Codex は orchestration / report / review gate を担当し、shipped docs/templates/skills/workflow text は `doc-writer`、tests は `dev-coder` へ委任する。

## 実装記録（セッションログ） (必須)

### 2026-05-20 S01 start

#### 対象
- Step: S01
- AC/EC: AC-001, AC-002, AC-003, AC-005, EC-002, EC-003, EC-004

#### 実施内容
- active issue と clean worktree を確認した。
- S01 の docs-only implementation を `doc-writer` に委任するため、Implementation Delegation Gate を記録した。

#### 実行コマンド / 結果
```bash
git status --short --branch
## iss-00102-agentic-tdd-plan-step-contract

./spec-dock/scripts/spec-dock active show
initiative: init-local-00003
epic: epic-00067
issue: iss-00102
```

#### Step Contract Closure
| step | closure ids | close condition | evidence | result | notes |
|---|---|---|---|---|---|
| S01 | tc-001, tc-002 | Provider docs encode source-of-truth separation and risk-calibrated obligation guidance; hard cutover optional pattern is no longer embedded as standard issue workflow. | doc-writer changed 4 provider docs; targeted `rg` and `git diff --check`; spec-reviewer pass | pass | S01 docs-only closure |

#### Test Contract Closure
| closure id / test id | step | required | evidence level | pre-implementation evidence | verification command | result | notes |
|---|---|---|---|---|---|---|---|
| tc-001 | S01 | yes | inspect-only | current docs contained overlapping ownership language | targeted doc inspection + spec-reviewer S01 pass | pass | workflow / phase / authoring ownership clarified |
| tc-002 | S01 | yes | inspect-only | current docs contained normative count guidance in issue plan playbook | `rg -n "1〜3|1〜3 件|1〜3件" <target4>` -> no matches; spec-reviewer S01 pass | pass | risk-calibrated obligation guidance added |

- `closure id / test id` は Central index の `id` を指す。別 alias を使う場合は `Closure Delta` で対応を記録する。

#### Closure Coverage
| closure id | step | verification evidence | result | notes |
|---|---|---|---|---|
| tc-001 | S01 | spec-reviewer S01 review_status pass | pass | no findings |
| tc-002 | S01 | target docs no longer match `1〜3` count pattern; spec-reviewer pass | pass | count guidance removed from S01 target docs |

#### Closure Delta
| change | closure id | test id alias | resolves to closure id | reason | re-review required |
|---|---|---|---|---|---|
| added | tc-001 | N/A | tc-001 | `reference_hard_cutover.md` added as optional pattern destination | yes, completed by S01 spec-reviewer |
| changed | tc-002 | N/A | tc-002 | raw count guidance removed from target docs | yes, completed by S01 spec-reviewer |

#### Implementation Delegation Gate
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records evidence only.

| step | decision | required reason | delegated role | delegated scope | source of truth | allowed changes | forbidden changes | required verification | stop conditions | output required | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | delegated | shipped workflow / authoring docs update | doc-writer | provider-side docs: workflow, phase plan issue, authoring issue-plan, hard cutover reference | `requirement.md`, `design.md`, `plan.md`, provider docs | `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`, `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`, `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`, `src/spec_dock/assets/spec_dock/docs/reference_hard_cutover.md` | runtime code, tests, dogfooding mirror direct edits, accepted requirement changes | targeted `rg` inspection for `1〜3`, hard cutover, planned contract, observed evidence ledger | requirement conflict, need to rename `具体テストケース一覧`, need to remove `phase_plan_issue.md` | changed files, ownership summary, inspection results, unresolved risks | pass |

#### Delegated Worker Evidence
| step | delegated role | delegated worker summary | changed files | tests run or docs-only verification | reviewer verdict | unresolved risks | parent integration decision |
|---|---|---|---|---|---|---|---|
| S01 | doc-writer | Updated workflow / phase / authoring docs so `plan.md` is planned executable workflow contract and `report.md` is observed evidence ledger; moved hard cutover optional pattern to reference doc; removed raw count guidance from target docs. | `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`, `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`, `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`, `src/spec_dock/assets/spec_dock/docs/reference_hard_cutover.md` | `rg -n "1〜3|1〜3 件|1〜3件" <target4>` -> no matches; `git diff --check -- <target4>` -> pass | pending spec-reviewer | `reference_deps.md` / `reference_sync.md` still contain hard cutover references but were outside S01 scope. | accepted for S01 review |

#### Parent Implementation Exception
| step | delegation unavailable/impossible reason | user approval / risk acceptance | allowed files | allowed operation | rollback plan | post-change verification | reviewer gate | unavailable / denied / host conflict / waiver handling |
|---|---|---|---|---|---|---|---|---|
| S01 | unavailable / denied / host conflict / impossible because ... | approval source / risk accepted: yes / no | `path/to/file` | ... | ... | `command` -> pass / docs-only inspection -> pass | reviewer role + passed / failed / unavailable / denied / waived / provisional | blocked / incomplete / waived with explicit risk acceptance / next action |

#### Workflow Delegation Consent
This table is for reviewer / read-only specialist workflow-scoped consent. Write-capable delegation such as `dev-coder` or `doc-writer` is recorded in `Implementation Delegation Gate` and `Delegated Worker Evidence`, not as generic workflow-scoped consent.

| consent source | repo / worktree | active issue | session | named roles | boundary | expires / invalidation condition | denied / unavailable reason | next action |
|---|---|---|---|---|---|---|---|---|
| user message requesting workflow execution | `/Users/iwasawayuuta/workspace/tools/spec-dock` | iss-00102 | current session | spec-reviewer / code-reviewer / qa-reviewer / doc-writer / dev-coder | active issue scope only; destructive / external publishing excluded | issue completion or user redirect | none | proceed with S01 delegation |

#### Reviewer Gate Status
| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| S01 | step reviewer | spec-reviewer | fresh | passed | N/A | proceed to S01 commit gate | review_status pass; no findings |

#### Code Review Gate
| step | reviewer | review scope | review_status | findings / fixes | re-review count | result |
|---|---|---|---|---|---|---|
| S01 | spec-reviewer | provider docs and report evidence | pass | none | 0 | pass |

#### Step Commit Gate
| step | closure state | commit scope | commit hash / final ledger | post-commit clean check | no-op rationale | no-op checked contracts / files | no-op diff-clean command | no-op read-only confirmation |
|---|---|---|---|---|---|---|---|---|
| S01 | committed | provider docs and S01 report evidence | `7e0018a` | `git status --short --branch` -> clean | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `path/to/file1` - ...
- `path/to/file2` - ...

#### コミット
- `7e0018a docs(spec): Issue計画の正本境界を整理`

#### メモ
- ...

---

### 2026-05-20 S02 templates update

#### 対象
- Step: S02
- AC/EC: AC-001, AC-002, AC-003, AC-007, EC-001, EC-002, EC-004

#### 実施内容
- S02 の template-only implementation を `doc-writer` に委任した。
- `plan.md` template を planned contract / command queue として整理し、`report.md` template を observed evidence ledger として整理した。
- `具体テストケース一覧` 見出しは維持しつつ、full test inventory ではなく step-local obligation / concrete seeds の欄だと明記した。
- S02 対象の `plan.md` / `report.md` から `1〜3件程度` の規範的 guidance が残っていないことを確認した。

#### 実行コマンド / 結果
```bash
rg -n "planned contract|observed evidence ledger|amendment trigger|report evidence destination|1〜3|具体テストケース一覧" src/spec_dock/assets/spec_dock/templates/issue
# required markers present in plan/report templates
# 1〜3 only matched src/spec_dock/assets/spec_dock/templates/issue/requirement.md:15, outside S02 target scope

rg -n "Discovered Tests|Red/Green|observed evidence|Closure Delta" src/spec_dock/assets/spec_dock/templates/issue/report.md
# Observed Evidence Ledger / Red-Green-Refactor Evidence / Discovered Tests / Closure Delta markers present

git diff --check -- src/spec_dock/assets/spec_dock/templates/issue/plan.md src/spec_dock/assets/spec_dock/templates/issue/report.md
# pass
```

#### Red/Green/Refactor Evidence
| step | phase | planned evidence requirement | observed evidence | command / inspection / manual record | result | notes |
|---|---|---|---|---|---|---|
| S02 | Red / alternative | inspect-only template contract | prior template carried ambiguous plan/report ownership and count-based guidance; S02 diff replaces it with planned/observed contract language | template diff inspection | pass | docs/template-only step |
| S02 | Green | target templates contain planned contract, evidence destination, amendment trigger, observed evidence ledger, discovered tests, closure delta | `rg -n "planned contract|observed evidence ledger|amendment trigger|report evidence destination|1〜3|具体テストケース一覧" src/spec_dock/assets/spec_dock/templates/issue` | pass | `1〜3` remains only in `requirement.md` placeholder outside S02 scope |
| S02 | Refactor | no extra cleanup beyond template contract simplification | `git diff --check -- <S02 target templates>` | pass | no unrelated template files changed |

#### Discovered Tests
| step | discovered test / risk | source | action taken | closure id / new id | plan amendment required | evidence |
|---|---|---|---|---|---|---|
| S02 | none | implementation inspection | no action | N/A | no | target template markers and diff hygiene verified |

#### Step Contract Closure
| step | closure ids | close condition | evidence | result | notes |
|---|---|---|---|---|---|
| S02 | tc-003, tc-004 | Issue plan/report templates encode planned step contract, alternative evidence path, observed ledger, closure delta, discovered tests, reviewer/commit evidence. | doc-writer changed 2 provider templates; targeted `rg`; `git diff --check`; spec-reviewer pass after traceability corrections | pass | S02 template-only closure |

#### Test Contract Closure
| closure id / test id | step | required | evidence level | pre-implementation evidence | verification command | result | notes |
|---|---|---|---|---|---|---|---|
| tc-003 | S02 | yes | inspect-only | existing issue plan template did not make planned contract / report evidence destination explicit enough | targeted template inspection + spec-reviewer pass | pass | plan template now has planned contract scaffold |
| tc-004 | S02 | yes | inspect-only | existing report template did not clearly own observed evidence ledger / discovered tests | targeted template inspection + spec-reviewer pass | pass | report template now has evidence ledger scaffold |

#### Closure Coverage
| closure id | step | verification evidence | result | notes |
|---|---|---|---|---|
| tc-003 | S02 | `planned contract`, `report evidence destination`, `amendment trigger`, `具体テストケース一覧` markers in plan template | pass | planned workflow expression added |
| tc-004 | S02 | `Observed Evidence Ledger`, `Red/Green/Refactor Evidence`, `Discovered Tests`, `Closure Delta` markers in report template; S02 target templates have no `1〜3` count guidance | pass | observed evidence structure added; count-guidance check is evidence for S02 template scope, not a separate S02 closure id |

#### Closure Delta
| change | closure id | test id alias | resolves to closure id | reason | re-review required |
|---|---|---|---|---|---|
| changed | tc-003 | N/A | tc-003 | plan template now provides copyable planned contract skeleton | yes, completed by S02 spec-reviewer |
| changed | tc-004 | N/A | tc-004 | report template now provides observed evidence ledger skeleton and S02 target templates remove normative test-count guidance | yes, completed by S02 spec-reviewer |

#### Implementation Delegation Gate
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records evidence only.

| step | decision | required reason | delegated role | delegated scope | source of truth | allowed changes | forbidden changes | required verification | stop conditions | output required | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S02 | delegated | shipped issue templates update | doc-writer | provider-side issue plan/report templates | `requirement.md`, `design.md`, `plan.md`, S01 docs | `src/spec_dock/assets/spec_dock/templates/issue/plan.md`, `src/spec_dock/assets/spec_dock/templates/issue/report.md` | runtime code, tests, installed agent assets, dogfooding mirror direct edits, accepted requirement changes | targeted marker inspection, `1〜3` target-scope check, `git diff --check` | requirement conflict, need to rename `具体テストケース一覧`, need to edit outside allowed paths | changed files, template summary, inspection results, unresolved risks | pass |

#### Delegated Worker Evidence
| step | delegated role | delegated worker summary | changed files | tests run or docs-only verification | reviewer verdict | unresolved risks | parent integration decision |
|---|---|---|---|---|---|---|---|
| S02 | doc-writer | Updated issue plan template as planned contract / command queue and report template as observed evidence ledger; kept `具体テストケース一覧` as step-local obligation / concrete seeds; removed `1〜3件程度` guidance from plan template; separated docs-only / inspect-only / manual-required alternative evidence path. | `src/spec_dock/assets/spec_dock/templates/issue/plan.md`, `src/spec_dock/assets/spec_dock/templates/issue/report.md` | marker `rg`; `1〜3` target-scope inspection; `git diff --check -- <S02 targets>` -> pass | spec-reviewer pass | `templates/issue/requirement.md` still contains unrelated `（1〜3行）` summary placeholder outside S02 scope. | accepted and closed for S02 commit |

#### Reviewer Gate Status
| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| S02 | step reviewer | spec-reviewer | fresh | pending | N/A | blocked until review pass | template-only scope |
| S02 | step reviewer | spec-reviewer | fresh | failed | N/A | follow-up completed; re-review required | initial review found S02 report incorrectly reused S03 `tc-005`; report evidence corrected to S02 `tc-003` / `tc-004` only |
| S02 | step reviewer | spec-reviewer | fresh | failed | N/A | follow-up completed; re-review required | second review found S02 AC/EC traceability overclaimed `AC-004` / `AC-005`; plan/report traceability corrected to S02-owned AC/EC only |
| S02 | step reviewer | spec-reviewer | fresh | passed | N/A | proceed to S02 commit gate | final review_status pass; no findings |

#### Step Commit Gate
| step | closure state | commit scope | commit hash / final ledger | post-commit clean check | no-op rationale | no-op checked contracts / files | no-op diff-clean command | no-op read-only confirmation |
|---|---|---|---|---|---|---|---|---|
| S02 | committed | provider issue plan/report templates plus S02 plan/report traceability evidence | `7d204aa` | `git status --short --branch` -> clean | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/templates/issue/plan.md` - planned contract / command queue scaffold に更新
- `src/spec_dock/assets/spec_dock/templates/issue/report.md` - observed evidence ledger scaffold に更新

#### コミット
- `7d204aa docs(spec): Issue計画テンプレートを実行契約へ更新`

#### メモ
- S02 は template-only step のため code test は置かず、inspection と spec-reviewer pass で閉じる。

---

### 2026-05-20 S03 agent routing assets update

#### 対象
- Step: S03
- AC/EC: AC-004, AC-005, AC-007

#### 実施内容
- S02 commit 後の clean worktree を確認した。
- S03 の installed agent asset / prompt / skill / role config 更新に向けて、対象ファイルの現状を inspection した。
- S03 の docs/text implementation を `doc-writer` に委任するため、Implementation Delegation Gate を記録した。

#### 実行コマンド / 結果
```bash
git status --short --branch
## iss-00102-agentic-tdd-plan-step-contract

rg -n "executable|planned contract|observed evidence|obligation|code-reviewer scope|1〜3|具体テストケース一覧|plan.md|report.md" src/spec_dock/assets/install_root/.codex src/spec_dock/assets/install_root/.agents
# execute-issue prompt mentions plan/report and `具体テストケース一覧`, but does not yet use planned contract / observed evidence ledger boundary.
# issue execution skill is concise and workflow-routed, but does not yet remind implementers to execute step-local planned contract fields.
# role configs do not yet express obligation coverage / report ledger expectations for reviewer output.
```

#### Implementation Delegation Gate
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records evidence only.

| step | decision | required reason | delegated role | delegated scope | source of truth | allowed changes | forbidden changes | required verification | stop conditions | output required | result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S03 | delegated | installed agent prompt / skill / role config routing update | doc-writer | provider-side installed agent assets | `requirement.md`, `design.md`, `plan.md`, S01 docs, S02 templates | `src/spec_dock/assets/install_root/.codex/prompts/execute-issue.md`, `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`, `src/spec_dock/assets/install_root/.codex/agents/dev-coder.toml`, `src/spec_dock/assets/install_root/.codex/agents/code-reviewer.toml`, `src/spec_dock/assets/install_root/.codex/agents/qa-reviewer.toml`, `src/spec_dock/assets/install_root/.codex/agents/spec-reviewer.toml` | runtime code, tests, non-issue prompts/skills unless direct stale reference is found and reported, model/tool changes | targeted `rg` inspection for executable/planned/observed/obligation/stale wording; `git diff --check` | role config needs model/tool changes, prompt/skill would become a duplicate workflow manual, need to rename `具体テストケース一覧` | changed files, role contract summary, inspection evidence, unresolved risks | pass |

#### Delegated Worker Evidence
| step | delegated role | delegated worker summary | changed files | tests run or docs-only verification | reviewer verdict | unresolved risks | parent integration decision |
|---|---|---|---|---|---|---|---|
| S03 | doc-writer | Updated execute prompt, issue execution skill, dev-coder, code-reviewer, qa-reviewer, and spec-reviewer instructions so agents route through `plan.md` as planned executable workflow contract / command queue and `report.md` as observed evidence ledger. Kept workflow policy routed to `workflow_issue.md` and step field semantics to `authoring/issue-plan.md`; removed stale `code-reviewer scope` wording from execute prompt. | `src/spec_dock/assets/install_root/.codex/prompts/execute-issue.md`, `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`, `src/spec_dock/assets/install_root/.codex/agents/dev-coder.toml`, `src/spec_dock/assets/install_root/.codex/agents/code-reviewer.toml`, `src/spec_dock/assets/install_root/.codex/agents/qa-reviewer.toml`, `src/spec_dock/assets/install_root/.codex/agents/spec-reviewer.toml` | `rg -n "executable|planned contract|observed evidence|obligation|code-reviewer scope|1〜3|具体テストケース一覧" src/spec_dock/assets/install_root/.codex src/spec_dock/assets/install_root/.agents`; `git diff --check -- <S03 allowed files>` -> pass | spec-reviewer pass after P2 cleanup | none reported | accepted and closed for S03 commit |

#### Red/Green/Refactor Evidence
| step | phase | planned evidence requirement | observed evidence | command / inspection / manual record | result | notes |
|---|---|---|---|---|---|---|
| S03 | Red / alternative | inspect-only current assets lack full plan-as-command-queue and role output contracts | pre-change inspection showed execute prompt referenced plan/report and concrete cases but did not yet use planned/observed boundary; role configs lacked obligation/report-ledger review contracts | targeted asset inspection | pass | docs/text-only step |
| S03 | Green | installed agent assets contain executable/planned/observed/obligation markers and no stale `code-reviewer scope` / `1〜3` wording | marker `rg` found expected terms in updated prompt/skill/configs; no `code-reviewer scope` or `1〜3` matches in allowed files | `rg -n "executable|planned contract|observed evidence|obligation|code-reviewer scope|1〜3|具体テストケース一覧" src/spec_dock/assets/install_root/.codex src/spec_dock/assets/install_root/.agents` | pass | `具体テストケース一覧` intentionally remains in prompt/skill routing |
| S03 | Refactor | keep prompt/skill concise and avoid full workflow duplication | diff inspection confirms skill adds short reminders and routes policy/details to docs | `git diff --check -- <S03 allowed files>` | pass | no model/tool/sandbox/approval/notify settings changed |

#### Discovered Tests
| step | discovered test / risk | source | action taken | closure id / new id | plan amendment required | evidence |
|---|---|---|---|---|---|---|
| S03 | none | implementation inspection | no action | N/A | no | worker reported no unresolved risks; parent inspection found target-scope markers present |

#### Step Contract Closure
| step | closure ids | close condition | evidence | result | notes |
|---|---|---|---|---|---|
| S03 | tc-005 | installed agent assets route through the planned contract and observed evidence ledger. | doc-writer changed 6 provider installed agent assets; targeted `rg`; `git diff --check`; spec-reviewer pass after P2 cleanup | pass | S03 docs/text-only closure |

#### Test Contract Closure
| closure id / test id | step | required | evidence level | pre-implementation evidence | verification command | result | notes |
|---|---|---|---|---|---|---|---|
| tc-005 | S03 | yes | inspect-only | current assets lacked complete plan-as-command-queue and role output contracts | targeted asset inspection + spec-reviewer pass after P2 cleanup | pass | prompt/skill/config routing updated |

#### Closure Coverage
| closure id | step | verification evidence | result | notes |
|---|---|---|---|---|
| tc-005 | S03 | `planned executable workflow contract`, `observed evidence ledger`, `obligation coverage`, and `authoring/issue-plan.md` routing markers in S03 assets; no `1〜3` or `code-reviewer scope` matches | pass | installed agent routing updated |

#### Closure Delta
| change | closure id | test id alias | resolves to closure id | reason | re-review required |
|---|---|---|---|---|---|
| changed | tc-005 | N/A | tc-005 | installed agent prompt/skill/configs now consume plan contract and report ledger | yes, completed by S03 spec-reviewer |

#### Reviewer Gate Status
| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| S03 | step reviewer | spec-reviewer | fresh | passed | N/A | follow-up applied before commit | initial review_status pass with P2 findings |
| S03 | step reviewer | spec-reviewer | fresh | failed | N/A | follow-up completed; re-review required | re-review found mixed pending/pass ledger rows; report status normalized to pending re-review |
| S03 | step reviewer | spec-reviewer | fresh | passed | N/A | proceed to S03 commit gate | final re-review_status pass; no findings |

#### Step Commit Gate
| step | closure state | commit scope | commit hash / final ledger | post-commit clean check | no-op rationale | no-op checked contracts / files | no-op diff-clean command | no-op read-only confirmation |
|---|---|---|---|---|---|---|---|---|
| S03 | pending commit | installed agent prompt/skill/role configs plus S03 report evidence | pending | pending | N/A | N/A | N/A | N/A |

---

### 2026-05-20 HH:MM - HH:MM

#### 対象
- Step: ...
- AC/EC: ...

#### 実施内容
- ...

---

## Final Quality Gate (必須)

### S90 Docs Impact Resolution
| target | update required | owner | evidence | spec-reviewer result |
|---|---|---|---|---|
| docs / templates / README / workflow / skill / migration notes | yes / no | doc-writer / N/A | ... | pass / fail / blocked |

### Final QA Gate
| reviewer | scope | integration test decision | evidence | result |
|---|---|---|---|---|
| qa-reviewer | whole issue test adequacy | added / already sufficient / not applicable | ... | pass / fail / blocked |

### Final Code Review Gate
| reviewer | scope | findings / fixes | re-review count | result |
|---|---|---|---|---|
| code-reviewer | issue-wide integrated diff | ... | 0 | pass / fail / blocked |

### Final Spec Review Gate
| reviewer | scope | findings / fixes | re-review count | result |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report / implementation / tests / docs alignment | ... | 0 | pass / fail / blocked |

### Final Commit
| final report ledger | final commit scope | post-commit external evidence destination | result |
|---|---|---|---|
| ... | ... | final response / PR / issue comment / other external delivery evidence | ready / blocked |

## 遭遇した問題と解決 (任意)
- 問題: ...
  - 解決: ...

## 学んだこと (任意)
- ...
- ...

## 今後の推奨事項 (任意)
- ...
- ...

## 省略/例外メモ (必須)
- 該当なし
