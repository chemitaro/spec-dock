---
種別: 実装報告書（Issue）
ID: "iss-00105"
タイトル: "PR Creation And Merge Ready Monitoring Skill"
関連GitHub: ["#105"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-05-21"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00105 PR Creation And Merge Ready Monitoring Skill — 実装報告（Observed Evidence Ledger）

> `report.md` は observed evidence ledger です。planned requirements、evidence destination、closure 条件は `plan.md` が所有し、この文書は実際の Red / Green / Refactor evidence、discovered tests、closure delta、reviewer status、commit/no-op evidence を記録する。

## Spec Interpretation / Decision Ledger (必須)

`report.md` は実装中・文書更新中に発生した material な仕様解釈、判断、plan 逸脱、tradeoff、open question、promotion / follow-up を記録する audit trail でもある。worker の raw note や作業 transcript を貼る場所ではなく、orchestrator が source docs、diff、tests、reviewer output と照合して issue-level の canonical entry に統合する。

Material な判断がない場合もこの section は残し、次を明示する。

- No material interpretation changes.
- No decision entries.

Ledger entry は次の値を使う。

- `Status`: `open` / `resolved` / `superseded`
- `Type`: `interpretation` / `scope` / `implementation` / `compatibility` / `test-strategy` / `operation` / `deviation` / `follow-up`
- `Disposition`: `applied` / `rejected` / `promoted_to_design` / `promoted_to_adr` / `promoted_to_plan` / `converted_to_followup` / `deferred` / `no_action` / `superseded`

Completion semantics:
- issue completion 前に `Status=open` の entry を残してはならない。
- `Status=resolved` は `Disposition`、evidence、必要な follow-up を持つ。
- `Status=superseded` または `Disposition=superseded` は置換先 entry ID を持つ。
- `Disposition=promoted_to_design` / `promoted_to_adr` / `promoted_to_plan` は昇格先 artifact と evidence を持つ。
- `Disposition=converted_to_followup` は follow-up issue / discussion / ADR candidate の参照を持つ。
- `Disposition=deferred` は scope 外である理由、blocking でない根拠、revisit 条件を持つ。
- `Disposition=no_action` は issue-local な判断で追加対応不要である理由を持つ。将来も効く durable decision を `report.md` だけに閉じ込めてはならない。

Disposition required evidence:
- `applied`: changed artifact / implementation evidence and why issue-local application is sufficient.
- `rejected`: rejected option, reason, and no remaining blocking impact.
- `promoted_to_design` / `promoted_to_adr` / `promoted_to_plan`: promoted artifact reference and evidence.
- `converted_to_followup`: follow-up issue / discussion / ADR candidate reference and blocking / non-blocking classification.
- `deferred`: scope-out reason, non-blocking rationale, and revisit condition.
- `no_action`: reason the decision is issue-local and not durable.
- `superseded`: replacement entry ID and reason for replacement.

| ID | Status | Type | Raised By | Trigger / Gap | Options Considered | Decision / Interpretation | Rationale | Disposition | Evidence | Follow-up |
|---|---|---|---|---|---|---|---|---|---|---|
| D-001 | resolved | scope | orchestrator + consultant | User requested `spec-dock-issue-execution` to use the PR merge-preparation skill as part of issue execution completion. | standalone PR skill only; extend issue execution final delivery gate; change `issue_finish()` runtime semantics | Extend issue execution's workflow completion boundary with PR Delivery Gate and Merge Preparation Gate, while keeping `issue_finish()` runtime semantics unchanged. | This satisfies the user's intent that issue execution prepares a mergeable PR without mixing PR readiness into the lifecycle command. | applied | `requirement.md` D-008/D-009; `discussions/20260521t004308z-disc-issue-execution-pr-delivery-scope.md`; spec-reviewer pass | Promote sequence/responsibility/evidence details into `design.md` |

## 実装サマリー (任意)
- [実装した内容の概要を2-3文で記載]

## 実装記録（セッションログ） (必須)

### 2026-05-21 HH:MM - HH:MM

#### 対象
- Step: S01, S02, ...
- AC/EC: AC-___, EC-___
- Planned source:
  - `plan.md` section:
  - closure ids:

#### 実施内容
- ...

#### 実行コマンド / 結果
```bash
<command>

<result>
```

#### Red/Green/Refactor Evidence
| step | phase | planned evidence requirement | observed evidence | command / inspection / manual record | result | notes |
|---|---|---|---|---|---|---|
| S01 | Red / alternative | red-required / covered-existing / inspect-only / manual-required | ... | `command` / docs inspection / manual record | pass / approved-no-op / fail / blocked | ... |
| S01 | Green | ... | ... | `command` / inspection / manual record | pass / fail / blocked | ... |
| S01 | Refactor | guardrail satisfied / no refactor needed | ... | diff inspection / command | pass / approved-no-op / fail / blocked | ... |

#### Discovered Tests
| step | discovered test / risk | source | action taken | closure id / new id | plan amendment required | evidence |
|---|---|---|---|---|---|---|
| S01 | none / ... | implementation / review / QA / user report | recorded / added test / deferred / amended plan | tc-001 / new | yes / no | ... |

#### Step Contract Closure
| step | closure ids | close condition from plan | observed evidence | result | notes |
|---|---|---|---|---|---|
| S01 | tc-001 | ... | ... | pass / approved-no-op / fail / blocked | ... |

#### Test Contract Closure
| closure id / test id | step | required | evidence level | pre-implementation evidence | verification command or alternative path | observed result | notes |
|---|---|---|---|---|---|---|---|
| tc-001 | S01 | yes | red-required / covered-existing / inspect-only / manual-required | ... | ... | pass / approved-no-op / fail / blocked | ... |

- `closure id / test id` は Spec-Locked Closure Index の `id` を指す。別 alias を使う場合は `Closure Delta` で対応を記録する。

#### Closure Coverage
| closure id | step | verification evidence | observed result | notes |
|---|---|---|---|---|
| tc-001 | S01 | ... | pass / approved-no-op / fail / blocked | ... |

#### Closure Delta
| change | closure id | test id alias | resolves to closure id | reason | plan amendment required | re-review required |
|---|---|---|---|---|---|---|
| none / added / removed / changed / alias-mapped | tc-001 | tc-001 / test-name | tc-001 | ... | yes / no | yes / no |

#### Workflow Delegation Consent
`workflow_issue.md` is the policy source for workflow-scoped delegation consent. This report records observed consent, boundary, expiry, and denied / unavailable handling only.

| consent source | repo/worktree | active issue | session | named roles | boundary | expires / invalidation condition | denied / unavailable reason | next action |
|---|---|---|---|---|---|---|---|---|
| user instruction / explicit approval / none | ... | iss-00105 | current session / ... | spec-reviewer / code-reviewer / qa-reviewer / read-only specialist | same repo, active issue, session, named role; no destructive action / publishing / credentialed access / scope expansion / write-capable delegation / private external system use | issue complete / session end / scope change / host policy conflict / user revocation | none / denied / unavailable / host conflict | proceed / ask user / block gate / record waiver request |

#### Implementation Delegation Gate
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| step | decision | required reason | delegated role | delegated scope | source of truth | allowed changes | forbidden changes | required verification | stop conditions | output required | observed result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | delegated / approved-local-execution / degraded mode | multi-layer / shipped scaffold / pattern analysis / integration / large worker scope / none | repo-analyst / dev-coder / doc-writer / N/A | ... | ... | ... | ... | ... | ... | worker summary / changed files / verification / risks / integration decision | pass / fail / blocked |

#### Delegated Worker Evidence
| step | delegated role | delegated worker summary | changed files | tests run or docs-only verification | reviewer verdict | unresolved risks | parent integration decision |
|---|---|---|---|---|---|---|---|
| S01 | dev-coder / doc-writer / repo-analyst | ... | `path/to/file` | `command` -> pass / docs-only inspection -> pass | pass / fail / unavailable / denied / waived / provisional | none / ... | accepted / rejected / needs follow-up |

#### Parent Implementation Exception
| step | delegation unavailable/impossible reason | user approval / risk acceptance | allowed files | allowed operation | rollback plan | post-change verification | reviewer gate | unavailable / denied / host conflict / waiver handling |
|---|---|---|---|---|---|---|---|---|
| S01 | unavailable / denied / host conflict / impossible because ... | approval source / risk accepted: yes / no | `path/to/file` | ... | ... | `command` -> pass / docs-only inspection -> pass | reviewer role + passed / failed / unavailable / denied / waived / provisional | blocked / incomplete / waived with explicit risk acceptance / next action |

#### Reviewer Gate Status
| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| S01 | step reviewer / final reviewer | code-reviewer / spec-reviewer / qa-reviewer | fresh / stale | passed / failed / unavailable / denied / waived / provisional | yes / no / N/A | proceed / blocked / incomplete / follow-up required | ... |

#### Step Commit Gate
| step | closure state | commit scope | commit hash / final ledger | post-commit clean check | no-op rationale | no-op checked contracts / files | no-op diff-clean command | no-op read-only confirmation |
|---|---|---|---|---|---|---|---|---|
| S01 | committed / approved-no-op | ... | <hash or final ledger reference> | `git status --short` -> clean | ... | ... | ... | ... |

#### 変更したファイル
- `path/to/file1` - ...
- `path/to/file2` - ...

#### コミット
- <hash> <message>

#### メモ
- ...

---

### 2026-05-21 09:55 JST - 09:55 JST

#### 対象
- Phase: requirement authoring gate
- AC/EC: AC-001..AC-010, EC-001..EC-007
- Planned source:
  - `workflow_spec_authoring.md` requirement gate
  - `workflow_issue.md` spec authoring section

#### 実施内容
- `requirement.md` をユーザー補足要求に合わせて更新し、`github-pr-merge-preparer` 単体追加だけでなく、`spec-dock-issue-execution` の final delivery gate として利用する要件を追加した。
- コンサルタント分析を `discussions/20260521t004308z-disc-issue-execution-pr-delivery-scope.md` に整理した。
- `issue_finish()` runtime command の意味は変更せず、PR readiness は workflow / skill evidence として扱う方針を要件に固定した。
- fresh `spec-reviewer` を起動し、更新後 requirement と discussion doc の整合を確認した。

#### 実行コマンド / 結果
```bash
./spec-dock/scripts/spec-dock validate

spec-dock: ok (validate) nodes=46
```

#### Spec Authoring Gate
| phase | investigated facts | open questions | delegation consent | reviewer | verdict | fixes | promotion |
|---|---|---|---|---|---|---|---|
| requirement | `requirement.md`; `workflow_spec_authoring.md`; `workflow_issue.md`; `spec-dock-issue-execution/SKILL.md`; existing `github-pr-creator` / `pr-monitor` boundaries; discussions under active issue | none blocking | User explicitly requested consultant / reviewer style analysis in this issue scope; named reviewer use limited to current repo, active issue, current session | fresh `spec-reviewer` Einstein reviewed updated `requirement.md` and `20260521t004308z-disc-issue-execution-pr-delivery-scope.md` | passed | none | proceed to design |

#### Reviewer Gate Status
| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| requirement | Spec Authoring Gate | spec-reviewer | fresh | passed | N/A | proceed to design | review_status `pass`; findings 0; confidence 0.94 |

#### 変更したファイル
- `requirement.md` - Requirement gate pass により front matter を `approved` に更新。
- `report.md` - Requirement Spec Authoring Gate evidence を記録。
- `discussions/20260521t004308z-disc-issue-execution-pr-delivery-scope.md` - issue execution 統合の分析を記録。

#### コミット
- 未実施。Requirement / discussion / report authoring changes are not committed yet.

#### メモ
- 次 phase は `design.md`。Sequence、responsibility split、state matrix、evidence model、affected files / tests を設計へ落とし込む。

---

### 2026-05-21 10:07 JST - 10:07 JST

#### 対象
- Phase: design authoring gate
- AC/EC: AC-001..AC-010, EC-001..EC-007
- Planned source:
  - `workflow_spec_authoring.md` design gate
  - `phase_design.md` Issue design checklist
  - reviewer-pass済み `requirement.md`

#### 実施内容
- `design.md` を作成し、`github-pr-merge-preparer`、`github-pr-creator`、`pr-monitor`、`spec-dock-issue-execution`、`workflow_issue.md`、`issue_finish()` の責務境界を整理した。
- Sequence、module dependency、directory / file change plan、interface contract、fix-loop stop contract、merge-prepared predicate evidence、test strategy を追加した。
- `spec-reviewer` で design review loop を実施し、P1/P2 指摘を修正した。

#### 実行コマンド / 結果
```bash
./spec-dock/scripts/spec-dock validate

spec-dock: ok (validate) nodes=46
```

#### Spec Authoring Gate
| phase | investigated facts | open questions | delegation consent | reviewer | verdict | fixes | promotion |
|---|---|---|---|---|---|---|---|
| design | `requirement.md`; `design.md`; `workflow_spec_authoring.md`; `phase_design.md`; `workflow_issue.md`; `github-pr-creator`; `pr-monitor`; `spec-dock-issue-execution`; `tests/test_init_update.py` asset/parity patterns | none blocking | User explicitly requested issue workflow analysis and reviewer use in this issue scope; named reviewer use limited to current repo, active issue, current session | fresh `spec-reviewer` Aquinas reviewed final `design.md` against `requirement.md` | passed | Added base-resolution precedence, existing PR conflict handling, non-required check waiver evidence, draft/ready rule, fix-loop stop contract, merge-prepared predicate fields, forbidden write boundaries, and dogfooding mirror file plan. | proceed to plan |

#### Reviewer Gate Status
| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| design | Spec Authoring Gate | spec-reviewer | fresh | passed | N/A | proceed to plan | review_status `pass`; findings 0; confidence 0.94 |

#### 変更したファイル
- `design.md` - Issue design を作成し、Spec Authoring Gate pass により front matter を `approved` に更新。
- `report.md` - Design Spec Authoring Gate evidence を記録。

#### コミット
- 未実施。Requirement / design / discussion / report authoring changes are not committed yet.

#### メモ
- 次 phase は `plan.md`。`phase_plan_issue.md` に従い、docs/skill text work は `doc-writer`、tests は `dev-coder` の delegated implementation step として切る。

---

### 2026-05-21 10:14 JST - 10:14 JST

#### 対象
- Phase: plan authoring gate
- AC/EC: AC-001..AC-010, EC-001..EC-007
- Planned source:
  - `workflow_spec_authoring.md` plan gate
  - `phase_plan_issue.md`
  - `docs/authoring/issue-plan.md`
  - reviewer-pass済み `requirement.md` / `design.md`

#### 実施内容
- `plan.md` を作成し、S01 `github-pr-merge-preparer` shared skill 追加、S02 `spec-dock-issue-execution` / `workflow_issue.md` 統合、S03 installer / parity / content regression tests の 3 implementation step に分解した。
- `Spec-Locked Closure Index`、各 step の delegation contract、具体テストケース一覧、step closure contract、S90 docs impact、S99 final quality gate、Final Exit Contract を追加した。
- `spec-reviewer` の指摘により、未解決 review-thread limitation human gate と `issue_finish()` runtime semantics evidence を closure / test contract に明示した。

#### 実行コマンド / 結果
```bash
./spec-dock/scripts/spec-dock validate

spec-dock: ok (validate) nodes=46
```

#### Spec Authoring Gate
| phase | investigated facts | open questions | delegation consent | reviewer | verdict | fixes | promotion |
|---|---|---|---|---|---|---|---|
| plan | `requirement.md`; `design.md`; `plan.md`; `phase_plan_issue.md`; `docs/authoring/issue-plan.md`; `workflow_issue.md`; existing test locations for managed asset / parity / issue lifecycle coverage | none blocking | User explicitly requested issue workflow analysis and reviewer use in this issue scope; named reviewer use limited to current repo, active issue, current session | fresh `spec-reviewer` Gibbs reviewed final `plan.md` against requirement/design | passed | Added unresolved review-thread limitation disclosure / human gate to tc-001, tc-005, S01/S03 concrete tests; added concrete `issue_finish()` runtime/no-runtime-diff evidence requirement. | proceed to implementation |

#### Reviewer Gate Status
| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| plan | Spec Authoring Gate | spec-reviewer | fresh | passed | N/A | proceed to implementation | review_status `pass`; findings 0; confidence 0.92 |

#### 変更したファイル
- `plan.md` - Issue execution-ready plan を作成し、Spec Authoring Gate pass により front matter を `approved` に更新。
- `report.md` - Plan Spec Authoring Gate evidence を記録。

#### コミット
- 未実施。Spec authoring changes are not committed yet.

#### メモ
- Requirement / design / plan の Spec Authoring Gate はすべて fresh `spec-reviewer` pass 済み。
- 次は `workflow_issue.md` の execution contract に従い、S01 から implementation step を開始できる。

---

### 2026-05-21 10:29 JST - 10:29 JST

#### 対象
- Step: S01
- AC/EC: AC-001..AC-006, EC-001..EC-005, EC-007
- Planned source:
  - `plan.md` section: `S01 — Add github-pr-merge-preparer shared skill`
  - closure ids: tc-001, tc-002

#### 実施内容
- `doc-writer` に S01 を委譲し、provider asset と dogfooding mirror に `github-pr-merge-preparer` shared skill を追加した。
- `spec-reviewer` の P2 指摘を受け、`Forbidden Writes` に `spec-dock issue finish` / active lifecycle closure の禁止を追記した。
- provider / dogfooding の `SKILL.md` と `agents/openai.yaml` が byte-identical であることを確認した。

#### 実行コマンド / 結果
```bash
cmp -s src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md .agents/skills/github-pr-merge-preparer/SKILL.md
cmp -s src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/agents/openai.yaml .agents/skills/github-pr-merge-preparer/agents/openai.yaml
git diff --check -- src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer .agents/skills/github-pr-merge-preparer

# all commands exited 0
```

#### Red/Green/Refactor Evidence
| step | phase | planned evidence requirement | observed evidence | command / inspection / manual record | result | notes |
|---|---|---|---|---|---|---|
| S01 | alternative | inspect-only | Code test is not meaningful for initial skill text creation; verified by file existence, content inspection, parity, and spec review. | docs inspection | pass | S03 will add installer/content regression tests. |
| S01 | Green | provider/dogfooding parity and skill contract inspection | `SKILL.md` and `openai.yaml` exist in provider and dogfooding mirror, match byte-for-byte, and include required coordinator boundaries. | `cmp -s ...`; `rg ...`; `git diff --check ...` | pass | Required wording includes `github-pr-creator`, `pr-monitor`, `failure_class`, non-required checks, unresolved review-thread limitation, and forbidden writes. |
| S01 | Refactor | keep text concise and avoid CI/review repair implementation | No refactor needed beyond P2 wording addition. | diff inspection | pass | Skill remains coordinator-only. |

#### Discovered Tests
| step | discovered test / risk | source | action taken | closure id / new id | plan amendment required | evidence |
|---|---|---|---|---|---|---|
| S01 | `spec-dock issue finish` needed explicit forbidden-write wording | spec-reviewer P2 | Added explicit forbidden write and re-reviewed | tc-001 | no | final S01 spec-reviewer pass |

#### Step Contract Closure
| step | closure ids | close condition from plan | observed evidence | result | notes |
|---|---|---|---|---|---|
| S01 | tc-001, tc-002 | Provider and dogfooding files exist, match, and satisfy the designed contract. | Provider/dogfooding parity; metadata exists; S01 spec-reviewer pass. | pass | Text semantics are inspect-only; S03 adds tests. |

#### Test Contract Closure
| closure id / test id | step | required | evidence level | pre-implementation evidence | verification command or alternative path | observed result | notes |
|---|---|---|---|---|---|---|---|
| tc-001 | S01 | yes | inspect-only | New skill text did not exist before S01. | content inspection + spec-reviewer pass | pass | New skill defines bounded PR preparation. |
| tc-002 | S01 | yes | inspect-only | New metadata did not exist before S01. | metadata inspection + provider/dogfooding `cmp -s` | pass | Metadata follows existing shared skill style. |

#### Closure Coverage
| closure id | step | verification evidence | observed result | notes |
|---|---|---|---|---|
| tc-001 | S01 | `spec-reviewer` final S01 pass; provider/dogfooding `SKILL.md` parity | pass | Includes unresolved review-thread limitation human gate and forbidden lifecycle closure. |
| tc-002 | S01 | provider/dogfooding `agents/openai.yaml` parity | pass | Installer inventory coverage deferred to S03. |

#### Closure Delta
| change | closure id | test id alias | resolves to closure id | reason | plan amendment required | re-review required |
|---|---|---|---|---|---|---|
| none | tc-001 | tc-s01-001 | tc-001 | Planned closure met. | no | no |
| none | tc-002 | tc-s01-002 | tc-002 | Planned closure met. | no | no |

#### Workflow Delegation Consent
| consent source | repo/worktree | active issue | session | named roles | boundary | expires / invalidation condition | denied / unavailable reason | next action |
|---|---|---|---|---|---|---|---|---|
| user instruction to execute workflow | `/Users/iwasawayuuta/workspace/tools/spec-dock` | iss-00105 | current session | doc-writer, spec-reviewer | same repo, active issue, session, named roles; no destructive action / publishing / credentialed access / scope expansion beyond S01 | issue complete / session end / scope change / user revocation | none | proceed |

#### Implementation Delegation Gate
| step | decision | required reason | delegated role | delegated scope | source of truth | allowed changes | forbidden changes | required verification | stop conditions | output required | observed result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | delegated | shipped skill text | doc-writer | Add `github-pr-merge-preparer` provider and dogfooding skill files | `requirement.md`, `design.md`, `plan.md`, existing `github-pr-creator` / `pr-monitor` assets | `src/.../github-pr-merge-preparer/**`, `.agents/skills/github-pr-merge-preparer/**` | runtime, tests, workflow docs, existing skills, `.codex/agents`, `.github/agents`, merge / issue close authority | provider/dogfooding byte parity, content inspection, `git diff --check` | need new API wrapper, monitor output, merge authority, or issue finish authority | changed files, verification, risks, ledger note | pass |

#### Delegated Worker Evidence
| step | delegated role | delegated worker summary | changed files | tests run or docs-only verification | reviewer verdict | unresolved risks | parent integration decision |
|---|---|---|---|---|---|---|---|
| S01 | doc-writer | Added merge-preparer skill and metadata, then added explicit `spec-dock issue finish` forbidden-write wording after review. | `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`; `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/agents/openai.yaml`; `.agents/skills/github-pr-merge-preparer/SKILL.md`; `.agents/skills/github-pr-merge-preparer/agents/openai.yaml` | docs-only inspection; provider/dogfooding `cmp -s`; `git diff --check` | pass | S03 still needs installer/content tests | accepted |

#### Reviewer Gate Status
| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| S01 | step reviewer | spec-reviewer | fresh after P2 fix | passed | N/A | proceed to S01 commit | final review_status `pass`; findings 0; confidence 0.94 |

#### Step Commit Gate
| step | closure state | commit scope | commit hash / final ledger | post-commit clean check | no-op rationale | no-op checked contracts / files | no-op diff-clean command | no-op read-only confirmation |
|---|---|---|---|---|---|---|---|---|
| S01 | pending commit | S01 skill files + S01 report evidence | pending | pending | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md` - New provider skill.
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/agents/openai.yaml` - New provider skill metadata.
- `.agents/skills/github-pr-merge-preparer/SKILL.md` - Dogfooding mirror.
- `.agents/skills/github-pr-merge-preparer/agents/openai.yaml` - Dogfooding mirror metadata.

#### コミット
- pending

#### メモ
- `Too many open files` occurred while some subagents were open; closing completed agents restored parent verification commands.

---

### 2026-05-21 HH:MM - HH:MM

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
| qa-reviewer | whole issue obligation coverage | added / already sufficient / not applicable | ... | pass / fail / blocked |

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

## 今後の推奨事項 (任意)
- ...

## 省略/例外メモ (必須)
- 該当なし
