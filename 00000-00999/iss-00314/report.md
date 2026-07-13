---
種別: 実施報告書（Issue）
ID: "iss-00314"
タイトル: "Harden GitHub Sync Preflight Fetch And Receipt Contract"
関連GitHub: ["#314"]
状態: "planning"
作成者: "main orchestrator"
最終更新: "2026-07-13"
親: ["epic-00295", "init-local-00003"]
---

# iss-00314 実施報告書

## 現在の状態

- lifecycle: execution
- canonical requirement: authored and fresh-reviewed
- canonical design: authored and fresh-reviewed after one repair cycle
- canonical plan: authored; initial fresh review failed、repair後のfresh re-review passed
- authorized profile: standard
- implementation: started (M0 baseline complete)
- execution-ready: true (`guidance issue-execution`: `state=ready`, `may_execute_approved_plan=true`)
- PR-ready / merge-ready / complete: not claimed

## GitHub Issue移管

- 元インシデント: `chemitaro/taikyohiyou_project#2098`
- 後継: `chemitaro/spec-dock#314`
- #2098には#314への移管コメントを記録し、state reason `COMPLETED` でcloseした。
- 要件定義、設計、計画、実装、検証、deliveryは#314で管理する。

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger）

| ID | Status | Type | Decision | Rationale | Disposition | Evidence / follow-up |
|---|---|---|---|---|---|---|
| D-314-001 | resolved | scope / compatibility | output APIはoptional `--output-dir`と固定filenameのみ。first PRで`--report-path`を追加しない | 任意file path入力を増やさずincident workflowを満たす | applied | requirement/design |
| D-314-002 | resolved | implementation / test strategy | total attempts=2、timeout=60秒、delay=250ms、jitterなし、excerpt=1024 UTF-8 bytesをdesign constantsとする | boundedかつdeterministicで、callerへpolicy判断を漏らさない | applied | design/plan |
| D-314-003 | resolved | security / output | existing external directoryだけをreceipt rootとして許可し、repo-local/canonical/symlink/non-directory/non-owned targetを拒否する | receipt publicationが観測直後のrepoをdirtyにしない | applied | design/plan |
| D-314-004 | resolved | freshness | receipt integrity/bindingをMUST、pack current-state revalidationをfollow-up、backend final fetchをLATERとする | Issue-local修正とcross-command hardeningを分離する | applied | requirement/design/plan |
| D-314-005 | resolved | compatibility | observation sourceは`fetched_remote_tracking_ref`をtruthfully記録し、direct connector integrationをLATERにする | 現行runtimeを過大表現しない | applied | requirement/design |
| D-314-006 | resolved | delivery | standalone maintenance Issueとして通常のPR Delivery / Merge Preparation Gateを使う | 旧final Issueへ暗黙deferしない | applied | plan/final exit |
| D-314-007 | resolved | retry policy | timeout、transient transport、remote throttling、high-confidence ref lockだけをbudget内でretryし、auth/config/policy/spawn/cancel/unknownはretryしない | incident evidenceとconservative fail-closedを両立する | applied | design/plan |
| D-314-008 | resolved | planning grade | runtime分類はstandard。security/TOCTOU/CLI contractのためclosure indexとS90/S99を含む強化planを採用する | authorized profileを上書きせずmanual escalationを記録する | applied | plan |

## 証跡採用台帳（Evidence Adoption Ledger）

| ID | adoption_status | source | target | rationale | evidence | next_action |
|---|---|---|---|---|---|---|
| EAL-314-001 | adopted | ChatGPT Pro research | `requirement.md` `design.md` `plan.md` | mandatory fixed fetch、same-capability retry、typed receipt、atomic publication、post-fetch snapshotをcurrent codeとincidentで裏付けた | `artifacts/20260713t014710z-research-chatgpt-pro-github-sync-preflight-reliability-analysis.md` | phase review complete |
| EAL-314-002 | partially_adopted | ChatGPT Pro planning candidate | `requirement.md` `design.md` `plan.md` | MUST/SHOULD/LATER、AC/EC、layering、closure、S01-S06/S90/S99を採用し、unsupported factsとauthority self-claimを除外した | `artifacts/20260713t024106z-research-chatgpt-pro-issue-planning-candidate-set.md` | plan review complete |
| EAL-314-003 | rejected | ChatGPT Pro | Issue facts | incident root cause、stderrからsandbox確定、connector observer実装済み、execution-ready claimはsource evidenceで確定不能 | `artifacts/20260713t024106z-research-chatgpt-pro-issue-planning-candidate-set.md` | none required |
| EAL-314-004 | deferred | ChatGPT Pro | follow-up | immutable launcher、Trace2、all-writer refactor、openat hardening、backend final fetchはcurrent Issue closureをblockしない | `artifacts/20260713t014710z-research-chatgpt-pro-github-sync-preflight-reliability-analysis.md` | 実測または別Issue化時に再訪 |
| EAL-314-005 | partially_adopted | system-architect | `design.md` `plan.md` | narrow layer split、single transaction、safe writer、truthful observation、compatibilityをrepository architectureと照合した | `artifacts/20260713t031029z-draft-design-system-architect-preflight-reliability-design-review.md` | design review complete |
| EAL-314-006 | adopted | first design spec-reviewer | `design.md` `report.md` | DES-008 normative marker、external receipt handoff、assurance refreshの具体findingを採用した | current-session fresh reviewer result | re-review passed |
| EAL-314-007 | partially_adopted | implementation-planner | `plan.md` `report.md` | C1-C6 slices、step test/delegation/report gates、S90/S99、scope-creep triggerをS01-S06へ統合した | `artifacts/20260713t031716z-draft-plan-implementation-planner-preflight-reliability-plan-review.md` | plan re-review passed |

## 目的整合台帳（Objective Alignment Ledger）

| ID | Primary objective | Secondary requirements | Inversion risk | Current verdict |
|---|---|---|---|---|
| OAL-314-001 | fetch failureを権限・shell shape変更なしで安全にretry/blockしdurable receiptへ残す | TOCTOU、pack binding、docs、projection parity | follow-up hardeningがcore fixを圧迫するriskをMUST/SHOULD/LATERで抑制 | pass for planning |

## ChatGPT-first evidence

- mode: github-synced
- branch: `iss-00314-harden-github-sync-preflight-fetch-and-receipt-contract`
- preflight HEAD: `48a26046c185c9563d073543e66404c8c8c4178f`
- source manifest hash: `f65cb99ce4d79bb1f3f600d1b579d0cb886036b5cfd1c67baf3a761e9dec1a87`
- preflight: status=pass, blockers=0, local/remote HEAD match
- analysis artifact: `artifacts/20260713t014710z-research-chatgpt-pro-github-sync-preflight-reliability-analysis.md`
- planning candidate artifact: `artifacts/20260713t024106z-research-chatgpt-pro-issue-planning-candidate-set.md`
- evidence authority: evidence-only
- raw candidate was not treated as reviewer pass or canonical authority

## 委任ドラフト証跡（Delegated Draft Evidence）

| created_by_role | scope_id | draft_path | source_paths | intended_targets | adoption_status | reflected_to | diff_guard_result | integration_result | rejected portions | blockers | reviewer result | promotion decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| system-architect | iss-00314 | `artifacts/20260713t031029z-draft-design-system-architect-preflight-reliability-design-review.md` | `requirement.md` `design.md` parent Epic and ChatGPT artifacts | `design.md` `plan.md` | partially_integrated | `design.md` `plan.md` | passed | main orchestrator integration via EAL-314-005 | timeout/ref-lock no-retry proposal | resolved | pass | promote |
| implementation-planner | iss-00314 | `artifacts/20260713t031716z-draft-plan-implementation-planner-preflight-reliability-plan-review.md` | `requirement.md` `design.md` `plan.md` `report.md` and candidate artifacts | `plan.md` | partially_integrated | `plan.md` `report.md` | passed | main orchestrator integration via EAL-314-007 | First PR wording normalized to Issue-local commit slices | resolved | pass | promote |

Neither delegated artifact claims canonical authority, reviewer pass, or implementation readiness.

## 仕様authoringゲート（Spec Authoring Gate）

| Phase | Investigated facts | Open questions / answers | Adoption decision | Fresh reviewer verdict | Blocking | Promotion decision |
|---|---|---|---|---|---|---|
| requirement | parent Epic、Issue #298、runtime/tests、incident、ChatGPT artifacts | none | adopted via EAL-314-001 through EAL-314-004 | pass | no | promote |
| design | canonical requirement、system-architect、current layers、assurance verify | none; O-001 through O-008 resolved | adopted via EAL-314-005 and EAL-314-006 | pass | no | promote |
| plan | canonical requirement/design、implementation-planner、CLOS-001 through CLOS-021 | none; implementation authorization is a later execution gate | adopted via EAL-314-007 | pass | no | promote |

## Grade Specialist Evidence Gate

| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |
|---|---|---|---|---|---|
| standard | system-architect / implementation-planner | used | delegated artifacts plus EAL-314-005 and EAL-314-007 | pass | ready |

## Reviewer Gate Status

| Scope | Reviewer | Freshness | Result | Notes |
|---|---|---|---|---|
| requirement | spec-reviewer | current planning diff | passed | parent trace、AC/EC、security、scopeを確認 |
| design initial | spec-reviewer | superseded | failed | marker/handoff/assurance findings |
| design re-review | spec-reviewer | current after repair | passed | O-001〜O-008、layering、TOCTOU、compatibility確認 |
| plan initial | spec-reviewer | superseded by repair | failed | new file明示、stale requirement context、blocking EAL定義、assurance refreshを要求 |
| plan re-review | spec-reviewer | current repaired canonical set | passed | CLOS-001〜021、S01〜S06/S90/S99、delegation/test/report gatesを確認 |
| implementation steps | code-reviewer/spec-reviewer | not started | pending | execution phase |
| final QA/code/spec | qa-reviewer/code-reviewer/spec-reviewer | not started | pending | S99 |

| scope | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| planning | planning spec-review | spec-reviewer | fresh | pass | no | promote | canonical requirement/design/plan phase reviews complete; implementation remains separately authorized |

## Assurance evidence

- `assurance classify --stage requirement --issue iss-00314`: ok
- authorized profile: standard
- complexity tier: normal
- `assurance classify --stage requirement --issue iss-00314`: ok、authorized profile=standard、complexity tier=normal
- `assurance verify --issue iss-00314`: ok（latest canonical requirement/design/plan）

## Workflow-Scoped Authorization

The user explicitly requested implementation through PR merge preparation after the reviewed Issue planning. This authorizes the SpecDock-defined execution roles and reviewers within this active Issue/worktree/session and PR creation/push/observation required for delivery. It does not authorize PR merge, branch deletion, or completion claims without evidence.

## Execution ledgers

Implementation has not started. The following ledgers are intentionally initialized rather than filled with template placeholders.

### Implementation Delegation Gate

| Step | Worker | State | Reason / next action |
|---|---|---|---|
| M0 | main orchestrator | passed | runtime guidance ready、explicit execution authorization、focused baseline 49 passed |
| M1 / C1 | utility-worker | committed | `a7a35f311871dc05cd3d4038774fda3d387c6984`、focused `30 passed, 389 deselected`、post-commit clean |
| M2 / C2 | utility-worker | committed | `3b28c12badcbb74f4795d5e1b2e6610bbb762766`、writer/CLI/Ruff/mypy pass、post-commit clean |
| M3 / C3 | utility-worker | committed | `84ab6ca015ccaa0c4b473d06720437687e15a85f`、preflight/Ruff/mypy pass、post-commit clean |
| M4 / C4 | utility-worker | committed | `f5a24a8aebe16004e9aca3cca70b5bf08a3a19da`、pack/parity/Ruff/mypy pass、post-commit clean |
| S01 | dev-coder | passed | fresh code review failed once、bounded repair後のfresh re-review passed |
| S02 | dev-coder | passed | fresh code review failed once、HTTP5xx/TLS identity fixtures修正後のfresh re-review passed |
| S03 | dev-coder | passed | fresh code review failed once、symlink例外撤去とtarget境界test後のfresh re-review passed |
| S04 | dev-coder | passed | first fresh code review passed |
| S05 | dev-coder | passed | first fresh code review passed |
| S06 | dev-coder | passed | fresh code review failed on matrix evidence、expanded parity/install execution後fresh re-review passed |
| S90 | doc-writer | passed | first fresh spec-review passed |
| S90 | doc-writer | not_started | depends on stable implemented contract |
| S99 | reviewers | not_started | depends on all prior step closures |

### TDD / Red / Green / Refactor Evidence

- state: baseline_complete
- destination: this section, updated per plan step
- M0 baseline: `uv run pytest -q tests/cli_runtime/test_authoring.py -k 'preflight or pack_prepare'` -> `49 passed, 338 deselected in 39.26s`
- S01 Red: new adapter不在によりfocused testが`ModuleNotFoundError`で失敗。
- S01 Green: typed fixed fetch tracer、schema v1 skeleton、spawn/timeout/exited outcomeを実装。`uv run pytest -q tests/unit/authoring_pack/test_github_fetch_policy.py tests/cli_runtime/test_authoring.py -k 'authoring_preflight'` -> `29 passed, 364 deselected`。
- S01 review repair: `policy_id=origin-fetch-v1`、timeout sensitivity、application-level spawn failure、text additive assertionsを追加。
- S02 Red: policy module不在によりfocused collectionが`ModuleNotFoundError`。
- S02 Green: conservative classifier、same-shape bounded retry、safe diagnosticを実装。initial expanded lane `30 passed, 384 deselected`。
- S02 review repair: HTTP 5xxをbounded retry、TLS certificate/auth/publickeyをnon-retry分類へ固定。final focused unit `30 passed`、CLI `21 passed, 368 deselected`。
- S03 Red: receipt writer module / `--output-dir`不在を確認。
- S03 Green: external existing directory限定、fixed filename、atomic JSON publication、ownership/digest/publication evidenceを実装。focused writer/CLI `19 passed`、expanded authoring lane `436 passed, 1 skipped`。
- S03 review repair: system symlink例外を撤去し、target symlink/directory/unsupported schema/oversizeのunchanged rejectionを追加。final writer `18 passed`、CLI `5 passed, 389 deselected`、Ruff/mypy pass。
- S04 Red: mixed-order observationがconcurrent source/HEAD/remote-ref mutationをstableとして扱い得るfixtureを追加。
- S04 Green: mandatory fetch後のstable snapshot、intra-capture/final guard、immutable SHA comparison、`unverified_cache` dispositionを実装。focused preflight `40 passed, 359 deselected`、full authoring `398 passed, 1 skipped`、Ruff/mypy pass。
- S05 Red: v1 integrity/binding matrixがdigest・semantic inconsistencyを未検出。
- S05 Green: v1 kind/schema/digest/pass invariant、pack provenance/stale-if binding、legacy marker、`current_repository_revalidated=false`を実装。focused `10 passed`、authoring CLI `406 passed, 1 skipped`、Ruff/mypy pass。
- S06 Red: checked-in dogfood mirrorにprovider-only 3 modules欠落。
- S06 Green: provider projection、fresh wheel init/update、module inclusion/help/no-bytecodeを追加。reviewでblocked/stale/pack binding/installed execution matrix不足を検出後、provider/dogfood pass-blocked-staleとpack binding、init/update後pass-blocked publicationを追加。final focused matrix `13 passed, 944 deselected`、Ruff/diff/parity pass。
- S90 docs: provider skill/workflow/pack referenceとdogfood projectionを更新。direct argv/no-shell/no-escalation、SpecDock-owned retry、receipt/freshness/operator remediationを明文化。focused install/parity assertions `2 passed`、fresh spec-review pass。
- next action: M90 commit candidate C5 then S99

### Step Contract Closure

- S01: passed / Result Approval granted
- evidence: CLOS-001〜004とCLOS-008のS01部分、fresh code-reviewer re-review pass、`git diff --check` pass
- S02: passed / Result Approval granted
- evidence: CLOS-002、003、005、006、007、fresh code-reviewer re-review pass、same-shape 2 attempts/250ms、unknown fail-closed、redaction上限を確認
- S03: passed / Result Approval granted
- evidence: CLOS-009〜011、fresh code-reviewer re-review pass、external-only path policy、atomic replacement、old receipt preservation、publication failure separationを確認
- S04: passed / Result Approval granted
- evidence: CLOS-012〜014、CLOS-017 S04部分、first fresh code-reviewer pass、post-fetch snapshot/final guard/cache disposition/local-context regressionを確認
- S05: passed / Result Approval granted
- evidence: CLOS-015〜016、first fresh code-reviewer pass、tamper/downgrade/inconsistent pass fail-closed、legacy/additive compatibility、truthful freshness boundaryを確認
- S06: passed / Result Approval granted
- evidence: CLOS-018、CLOS-017統合、fresh code-reviewer re-review pass、provider/dogfood/fresh init/update三surface parity、package inclusion、no-bytecodeを確認
- S90: passed / Result Approval granted
- evidence: CLOS-019〜020、fresh spec-reviewer pass、provider/dogfood/install docs parity、live help/schema alignmentを確認
- required closure IDs: CLOS-001 through CLOS-021
- evidence source: plan step closure contracts and future execution results

### Test Contract Closure

- state: not_started
- baseline focused test passed: `49 passed, 338 deselected`
- planned commands and test cards are in `plan.md`

### Closure Coverage / Delta

- planned coverage: CLOS-001 through CLOS-021
- observed coverage: S01〜S06/S90 CLOS-001〜020
- delta: S99 CLOS-021 pending

### Commit Evidence

- planning scaffold commit: `fa98df44c28b0dc09e35d322c7186eacf904820e`
- research artifact commit: `48a26046c185c9563d073543e66404c8c8c4178f`
- canonical planning changes: `98b2454def27f404e4039ea1198574eb7959668b`
- implementation commits: C1 `a7a35f311871dc05cd3d4038774fda3d387c6984`; C2 `3b28c12badcbb74f4795d5e1b2e6610bbb762766`; C3 `84ab6ca015ccaa0c4b473d06720437687e15a85f`; C4 `f5a24a8aebe16004e9aca3cca70b5bf08a3a19da`

## Docs Impact

- required: yes
- planned owner: doc-writer
- planned paths: installed `spec-dock-chatgpt-authoring` skill and ChatGPT authoring workflow docs, with provider/dogfood/install parity
- actual updates: provider installed skill、workflow、pack referenceとdogfood projectionを更新。direct argv/no-shell/no-escalation、receipt、freshness boundaryを反映。

## Final Quality Gate

- QA reviewer: not started
- issue-wide code reviewer: not started
- final spec reviewer: not started
- PR Delivery Gate: not started
- Merge Preparation Gate: not started
- completion decision: incomplete by design

## Current blockers and next action

1. Blocking itemはない。S01をplanのdelegation contractに従って開始する。
2. 各stepはfresh reviewer pass、report evidence、commit/no-op gateを満たしてから次へ進む。

## Omitted / exception notes

- Manual planning fallback was not used.
- ChatGPT/browser delay was treated as retryable waiting, not fallback justification.
- Baseline test executionのみ完了。実装step、PR作成、merge preparation、Issue completionはまだclaimしない。
