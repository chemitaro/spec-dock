---
種別: 実装報告書（Issue）
ID: "<ISS_ID>"
タイトル: "<ISS_TITLE>"
関連GitHub: ["<GITHUB_ISSUE_NUMBER_OR_URL>"]
状態: "draft | approved"
作成者: "<YOUR_NAME>"
最終更新: "YYYY-MM-DD"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["<EPIC_ID>", "<INIT_ID>"]
---

# <ISS_ID> <ISS_TITLE> — 実装報告（Observed Evidence Ledger）

> `report.md` は observed evidence ledger です。planned requirements、evidence destination、closure 条件は `plan.md` が所有し、この文書は実際の Red / Green / Refactor evidence、discovered tests、closure delta、reviewer status、commit/no-op evidence を記録する。

## 実装サマリー (任意)
- [実装した内容の概要を2-3文で記載]

## 実装記録（セッションログ） (必須)

### YYYY-MM-DD HH:MM - HH:MM

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
| user instruction / explicit approval / none | ... | <ISS_ID> | current session / ... | spec-reviewer / code-reviewer / qa-reviewer / read-only specialist | same repo, active issue, session, named role; no destructive action / publishing / credentialed access / scope expansion / write-capable delegation / private external system use | issue complete / session end / scope change / host policy conflict / user revocation | none / denied / unavailable / host conflict | proceed / ask user / block gate / record waiver request |

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

### YYYY-MM-DD HH:MM - HH:MM

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
