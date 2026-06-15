---
種別: 実装報告書（Issue）
ID: "iss-00187"
タイトル: "Use Actions Endpoint For PR Observation CI State"
関連GitHub: ["#187"]
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-16"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00187 Use Actions Endpoint For PR Observation CI State — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

> `report.md` は観測証跡台帳（observed evidence ledger）の scaffold です。planned requirements、evidence destination、closure 条件は `plan.md` が持ち、この文書は実際の Red / Green / Refactor evidence、発見された tests、closure delta、reviewer status、commit/no-op evidence を記録する evidence slot です。workflow / compliance authority は skills、docs、accepted ADRs、reviewer gates に置きます。

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger / 必須）

`report.md` は実装中・文書更新中に発生した material な仕様解釈、判断、plan 逸脱、tradeoff、open question、promotion / follow-up を記録する audit trail でもある。worker の raw note や作業 transcript を貼る場所ではなく、orchestrator が source docs、diff、tests、reviewer output と照合して issue-level の canonical entry に統合する。

Material な判断がない場合もこの section は残し、次を明示する。

- No material interpretation changes.
- No decision entries.

Ledger entry は次の契約値を使う。

- `Status`: `open` / `resolved` / `superseded`
- `Type`: `interpretation` / `scope` / `implementation` / `compatibility` / `test-strategy` / `operation` / `deviation` / `follow-up`
- `Disposition`: `applied` / `rejected` / `promoted_to_design` / `promoted_to_adr` / `promoted_to_plan` / `converted_to_followup` / `deferred` / `no_action` / `superseded`

完了時の意味論（completion semantics）:
- issue completion 前に `Status=open` の entry を残してはならない。
- `Status=resolved` は `Disposition`、evidence、必要な follow-up を持つ。
- `Status=superseded` または `Disposition=superseded` は置換先 entry ID を持つ。
- `Disposition=promoted_to_design` / `promoted_to_adr` / `promoted_to_plan` は昇格先 artifact と evidence を持つ。
- `Disposition=converted_to_followup` は follow-up issue / discussion / ADR candidate の参照を持つ。
- `Disposition=deferred` は scope 外である理由、blocking でない根拠、revisit 条件を持つ。
- `Disposition=no_action` は issue-local な判断で追加対応不要である理由を持つ。将来も効く durable decision を `report.md` だけに閉じ込めてはならない。

Disposition ごとの必須証跡:
- `applied`: 変更した artifact / 実装証跡と、issue-local 適用で十分な理由。
- `rejected`: 却下した選択肢、理由、blocking impact が残らない根拠。
- `promoted_to_design` / `promoted_to_adr` / `promoted_to_plan`: 昇格先 artifact 参照と証跡。
- `converted_to_followup`: follow-up issue / discussion / ADR candidate 参照と blocking / non-blocking の分類。
- `deferred`: scope-out 理由、non-blocking の根拠、revisit 条件。
- `no_action`: 判断が issue-local で durable ではない理由。
- `superseded`: 置換先 entry ID と置換理由。

| 識別子（ID） | 状態（Status） | 種別（Type） | 起票元（Raised By） | 契機 / 差分（Gap） | 検討した選択肢 | 判断 / 解釈 | 根拠（Rationale） | 処置（Disposition） | 証跡（Evidence） | フォローアップ（Follow-up） |
|---|---|---|---|---|---|---|---|---|---|---|
| D-001 | resolved | scope | orchestrator + user interview | Actions-only green evidence を `passed` と扱えるかが requirement / design / plan を左右する | Option A: Actions-only green を pass 許可し limitation を残す; Option B: full rollup なしでは unknown | Option A を採用する | #187 の目的は Fine-grained PAT で付与可能な Actions read surface へ通常観測を寄せること。未証明 surface は limitation として残せば false-pass risk を可視化できる | applied | `discussions/20260615t154753z-01-research-actions-ci-observation-scope.md`; `discussions/20260615t154753z-02-interview-actions-only-pass-contract.md`; `requirement.md` | design / plan で collector contract と test obligation に展開する |
| D-002 | resolved | deviation | orchestrator | `system-architect` / `implementation-planner` delegated authoring は diff-guard 付き discussion draft を標準とするが、既存の requirement evidence discussions が未コミットで target `discussions/` baseline を dirty にしている | Option A: 現在の dirty discussions を前提に手動 authoring fallback; Option B: 途中 commit/stage して delegated draft precondition を作る | Option A を採用する | ユーザーは仕様書作成を要求しており、途中 commit は要求されていない。dirty baseline 上で delegated draft を昇格証跡にすると diff-guard 契約が弱くなるため、canonical design/plan は orchestrator が直接作成し、fresh spec-reviewer gate で品質保証する | applied | `git status --short`; `design.md`; `plan.md`; Delegated Draft Evidence | 実装開始前に design / plan spec-reviewer gate を通す |
| D-003 | resolved | compatibility | dev-coder Ledger Note / orchestrator | S02 で zero Actions runs を blocking limitation にすると既存 zero-check grace が wrapper で早期停止した | Option A: `zero_actions_runs_non_success` を blocking にする; Option B: `zero_actions_runs_non_success` は informational にし、`ci.status` を non-pass に保ち、check/status も 0 件のとき既存 `zero_checks_s03_non_success` blocking を維持する | Option B を採用する | S02 の非交渉点は zero Actions runs を `passed` にしないこと。`ci.status` は `none`/`unknown` の non-pass で保持され、既存 zero-check grace も壊さない | applied | S02 dev-coder Ledger Note; `test_issue_187_zero_actions_runs_is_never_passed`; `test_issue_75_pr_observation_wait_applies_zero_check_grace_before_human_gate` | S03 で wrapper semantics を触る場合は再確認する |
| D-004 | resolved | compatibility | dev-coder Ledger Note / orchestrator | reviewer P1 対応で generic `github_api_collection_failed` fallback に metadata を足す範囲 | Option A: Actions primary の default failure だけ special-case; Option B: shared default branch に sanitized `capability`/`api`/`token_source`/`secret_redacted`/`stderr_sha256` を足す | Option B を採用する | 既存 classified branches と limitation shape が揃い、raw stderr は出さない。非 Actions generic failures への追加 field は additive JSON metadata で互換リスクが低い | applied | S02 follow-up dev-coder Ledger Note; focused issue_187 actions failure tests | 互換問題が出たら Actions-only special-case へ狭める |
| D-005 | resolved | compatibility | Codex review / dev-coder Ledger Note / orchestrator | Codex P2 found the implementation emitted job detail entries under undocumented `ci.actions.jobs_detail` while `design.md` documented `ci.actions.jobs[]`; tests had started using `ci.actions.jobs` as the summary object | Option A: keep `ci.actions.jobs` as summary and document `jobs_detail`; Option B: align with design by making `ci.actions.jobs[]` the sanitized detail list, move counts/collection to `ci.actions.jobs_summary`, and keep `jobs_detail` as a legacy alias | Option B を採用する | `design.md` explicitly documents `jobs[]` as sanitized job entries. Keeping `jobs_detail` preserves existing detail-list consumers, while `jobs_summary` keeps counts/collection machine-readable without contradicting the documented key | applied | Codex P2 `PRRT_kwDOQ99OK86JszfO`; `test_issue_187_actions_job_details_are_documented_and_fingerprinted`; repo search for remaining `ci.actions.jobs.total/counts` consumers | If external consumers depended on the undocumented summary-at-`jobs` shape, they should switch to `jobs_summary` |
| D-006 | resolved | compatibility | Codex review / dev-coder Ledger Note / orchestrator | Codex P2 found accepted abbreviated `--head-sha` values were sent directly to Actions `head_sha` filters, and successful jobs API JSON missing `jobs` could be counted as successful collection | Option A: reject abbreviated SHA inputs; Option B: preserve compatibility by resolving abbreviated SHA to current full `headRefOid`; Option C: keep empty jobs list semantics | Option B for SHA compatibility; reject Option C by treating missing/non-list `jobs` as blocking jobs unavailable | Existing issue_75 tests establish abbreviated SHA acceptance. False-pass constraints require observed Actions job evidence before `passed`; successful JSON without a `jobs` list is ambiguous/unobserved evidence | applied | Codex P2 threads `PRRT_kwDOQ99OK86JtnyR`, `PRRT_kwDOQ99OK86JtnyU`; `test_issue_187_actions_jobs_missing_field_prevents_actions_only_pass`; abbreviated SHA tests updated to assert full-SHA API queries | None |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | research | `requirement.md` | Current implementation, existing tests, and GitHub permission surfaces define the concrete requirement boundary for #187 | `discussions/20260615t154753z-01-research-actions-ci-observation-scope.md` | Continue to design authoring |
| EAL-002 | adopted | discussion / user answer | `requirement.md` | User explicitly allowed Actions-only green evidence to produce `ci.status="passed"` when limitation semantics remain visible | `discussions/20260615t154753z-02-interview-actions-only-pass-contract.md` | Continue to design authoring |
| EAL-003 | adopted | reviewer | `requirement.md` | Requirement reviewer identified non-blocking ambiguity between workflow-run stale conclusion and stale head freshness failure; requirement now separates CI failure from rerun-needed freshness failure | Initial `spec-reviewer` pass with P2 cleanup; `requirement.md` | Fresh requirement re-review completed |
| EAL-004 | adopted | reviewer | `requirement.md` | Fresh requirement re-review found no findings and confirmed requirement is ready for design promotion | Fresh `spec-reviewer` pass result; `requirement.md`; `report.md` | Promote to design authoring |
| EAL-005 | adopted | orchestrator analysis | `design.md` | Existing provider scripts and tests define the lowest-risk implementation boundary: keep public collector CLI, move CI primary source to Actions, retain supplemental signals as compatibility evidence | `rg` / source inspection of PR observation scripts and tests; `design.md` | Run design spec review |
| EAL-006 | adopted | orchestrator analysis | `plan.md` | Implementation order follows dependency graph: collector contract first, taxonomy second, wrappers third, docs/mirror fourth, final gates last | `design.md`; `plan.md` closure index | Run plan spec review |
| EAL-007 | adopted | reviewer | `design.md`, `plan.md` | Design reviewer passed the gate with P2 improvements: wrapper permission handling must be mandatory, and Actions-derived `ci.failures[]` shape must be explicit | `spec-reviewer` design review result; `design.md`; `plan.md` | Run fresh design re-review |
| EAL-008 | adopted | reviewer | `design.md` | Fresh design re-review found no findings and confirmed P2 cleanup was reflected into design and plan obligations | Fresh `spec-reviewer` design re-review result; `design.md`; `plan.md`; `report.md` | Promote to plan review |
| EAL-009 | adopted | reviewer | `plan.md`, `report.md` | Plan reviewer failed the first plan gate on missing delegation-contract fields, S90 delegation contract, concrete report evidence destinations, and stale design gate state; plan/report were updated accordingly | `spec-reviewer` plan review result; `plan.md`; `report.md` | Run fresh plan re-review |
| EAL-010 | adopted | reviewer | `plan.md` | Fresh plan re-review failed on incomplete concrete test cards and S90 role mismatch; plan now adds full card fields for S01/S02/S03/S90 and assigns doc-writer to skill-text wording with dev-coder/utility for mechanical sync | Fresh `spec-reviewer` plan re-review result; `plan.md` | Run second fresh plan re-review |
| EAL-011 | adopted | reviewer | `plan.md`, `report.md` | Second fresh plan re-review found no findings and confirmed implementation handoff readiness | Fresh `spec-reviewer` plan re-review result; `plan.md`; `report.md` | Ready for implementation handoff |
| EAL-012 | adopted | dev-coder | `fetch_pr_checks_snapshot.sh`, `tests/unit/infra/test_init_update.py`, `report.md` | S01 delegated implementation and follow-up fixed Actions-only green and supplemental permission behavior; code-reviewer re-review passed | S01 dev-coder outputs; parent test reruns; S01 code-reviewer results; commit `0cb15bfd` | Continue to S02 |
| EAL-013 | adopted | dev-coder | `fetch_pr_checks_snapshot.sh`, `tests/unit/infra/test_init_update.py`, `report.md` | S02 delegated implementation added Actions taxonomy/failure/zero/API failure behavior. P1 reviewer findings were fixed by bounded dev-coder follow-ups; fresh code-reviewer re-review passed with no findings | S02 dev-coder outputs; parent test reruns; code-reviewer fail results; final code-reviewer pass; focused pytest `33 passed` | Commit S02 and continue to S03 |
| EAL-014 | adopted | dev-coder | `fetch_pr_observation_snapshot.sh`, `wait_pr_observation.sh`, `tests/unit/infra/test_init_update.py`, `report.md` | S03 delegated implementation made wrapper permission remediation depend on blocking limitations and refreshed wrapper fake-gh tests for Actions-primary output | S03 dev-coder output; parent focused pytest `49 passed`; `git diff --check` pass; fresh code-reviewer pass | Commit S03 and continue to S90 |
| EAL-015 | adopted | doc-writer / utility-worker | provider/mirror `SKILL.md`, mirror scripts, `report.md` | S90 delegated docs update names Actions read as normal CI observation permission and mirror sync copied S01-S03 provider scripts into dogfooding `.agents` | doc-writer output; utility-worker output; parent `cmp` provider/mirror checks all exit 0; `git diff --check` pass; fresh S90 spec-reviewer/code-reviewer pass | Commit S90 and continue to S99 |
| EAL-016 | adopted | dev-coder | `tests/unit/infra/test_init_update.py`, `report.md` | S99 integration verification exposed older pr_observation fake-gh fixtures that lacked Actions runs/jobs endpoints after the collector became Actions-primary; bounded dev-coder fixture alignment preserved exact assertions and parent rerun passed the intended S99 lane | Initial parent S99 focused pytest failed `14 failed, 67 passed`; dev-coder fixture alignment; parent rerun `uv run pytest tests/unit/infra/test_init_update.py -k "pr_observation or issue_187"` -> `81 passed, 287 deselected`; `git diff --check` pass; `spec-dock validate` pass | Run S99 code/QA/spec review and commit final verification evidence |
| EAL-017 | adopted | PR observation / dev-coder / reviewers | `fetch_pr_checks_snapshot.sh`, `tests/unit/infra/test_init_update.py`, `report.md` | PR #190 observation on head `fe9daa5955c156216071763246107e9908f6eef1` exposed provider-tests failures and two current Codex P2 false-pass risks. Bounded dev-coder follow-up fixed jobs-collection failure and statusCheckRollup non-green handling, refreshed old fixtures, and updated dogfooding meta snapshot expectations | `wait_pr_observation.sh` failed with `ci_failed`; Codex P2 threads for jobs collection failure and status rollup; focused pytest `18 passed`; full `test_init_update.py` `371 passed`; code-reviewer PASS; qa-reviewer PASS | Commit post-observation follow-up and re-push PR #190 |
| EAL-018 | adopted | PR observation / dev-coder / reviewers | `fetch_pr_checks_snapshot.sh`, `tests/unit/infra/test_init_update.py`, `report.md` | PR #190 observation on head `8456d3528d78b64fba96a28f5f3cfc0facca6fb0` passed CI but exposed a current Codex P1: Actions running/pending plus supplemental permission denial could remain a blocking permission limitation and drive wrappers to `fix_github_token_permissions` instead of continuing to wait. Bounded dev-coder follow-up now downgrades supplemental limitations when Actions primary is decisive for running/pending, without weakening jobs-unavailable or readable rollup non-green guards. QA P2 requested direct pending/queued coverage; bounded test-only follow-up parametrized the regression for running, queued, and pending | `wait_pr_observation.sh` returned `human_gate`; current Codex P1 thread `PRRT_kwDOQ99OK86Jrv1v`; parent parametrized regression rerun `3 passed, 371 deselected`; `issue_187` focused `19 passed`; full `test_init_update.py` `374 passed`; code-reviewer PASS; qa-reviewer PASS; spec-reviewer PASS | Commit post-observation P1/P2 follow-up and re-push PR #190 |
| EAL-019 | adopted | PR observation / dev-coder / reviewers | `fetch_pr_checks_snapshot.sh`, `tests/unit/infra/test_init_update.py`, `report.md` | PR #190 observation on head `ad6bada6537ac0a960865396152ed5e8023599b0` exposed a current Codex P2: Actions failed evidence plus supplemental permission denial could leave blocking token-permission limitations beside `ci.status="failed"`, misrouting downstream triage away from fixing CI. Bounded dev-coder follow-up now treats Actions failed as another decisive Actions state for supplemental limitation downgrade while preserving failed status and failure details | `wait_pr_observation.sh` returned `ci_failed` with current thread `PRRT_kwDOQ99OK86JsXBm`; dev-coder Red targeted regression failed then green; parent targeted regression `1 passed, 374 deselected`; `issue_187` focused `20 passed`; full `test_init_update.py` `375 passed`; `spec-dock validate` pass; provider/mirror `cmp` pass; code-reviewer PASS; qa-reviewer PASS; spec-reviewer PASS | Commit failed-Actions P2 follow-up and re-push PR #190 |
| EAL-020 | adopted | PR observation / dev-coder | `fetch_pr_checks_snapshot.sh`, `tests/unit/infra/test_init_update.py`, `design.md`, `report.md` | PR #190 observation on head `2734987cedb865d6192ceb5ed984977f0dd50137` passed CI but exposed three current Codex findings: P1 claimed the advertised `pr_observation or issue_187` lane could timeout under short waits, P2 required Actions evidence in the collector fingerprint, and P2 required job details under documented `ci.actions.jobs[]`. The P1 was not reproduced locally before or after the change; the follow-up keeps timeout values unchanged, adds Actions evidence and failed-step evidence to fingerprint, aligns `jobs[]` with design, and preserves summary as `jobs_summary` plus legacy `jobs_detail` alias | `wait_pr_observation.sh` returned `human_gate`; Codex threads `PRRT_kwDOQ99OK86JszfI`, `PRRT_kwDOQ99OK86JszfM`, `PRRT_kwDOQ99OK86JszfO`; parent targeted fingerprint tests `2 passed`; parent required lane `90 passed`; full `test_init_update.py` `377 passed`; provider/mirror `cmp` pass; `git diff --check` pass; `spec-dock validate` pass | Run fresh code/QA/spec review before commit and re-push |
| EAL-021 | adopted | PR observation / dev-coder | `fetch_pr_checks_snapshot.sh`, `tests/unit/infra/test_init_update.py`, `design.md`, `report.md` | PR #190 observation on head `66c6a3be199a30ea0104816361822de5ddda80a5` passed CI but exposed two current Codex P2 findings: successful Actions jobs JSON missing/non-list `jobs` could be counted as successful collection and allow false-pass, and accepted abbreviated `--head-sha` values were sent directly to Actions queries. Bounded dev-coder follow-up now treats missing/non-list `jobs` as blocking `github_actions_jobs_unavailable`, preserves abbreviated SHA compatibility by resolving to current full `headRefOid`, and records full-SHA query expectations in tests. QA P2 asked for explicit non-list jobs payload coverage and unresolved abbreviation coverage; bounded test-only follow-ups parametrized missing/object/null jobs payloads and added a non-matching `headRefOid` negative path | `wait_pr_observation.sh` returned `human_gate`; Codex threads `PRRT_kwDOQ99OK86JtnyR`, `PRRT_kwDOQ99OK86JtnyU`; dev-coder Red `3 failed`; parent focused before QA P2 `25 passed`; parent required before QA P2 `91 passed`; parent focused after jobs non-list QA P2 `25 passed`; parent required after jobs non-list QA P2 `93 passed`; parent focused after SHA resolution QA P2 `28 passed`; parent required after SHA resolution QA P2 `94 passed`; provider/mirror `cmp` pass; `git diff --check` pass; `spec-dock validate` pass | Run fresh code/QA/spec review before commit and re-push |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | #187 と `requirement.md` は Fine-grained PAT で付与可能な Actions read surface を通常 CI 観測に使うことを主要目的にしている | False-pass safety は limitation と unknown/pending/failed classification で保持する | low | requirement/design/plan spec-reviewer pass |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | GitHub issue #187; active issue scaffold; parent epic requirement/design; current PR observation scripts; fake `gh` tests; GitHub REST docs; research discussion | Answered: Actions-only green pass is allowed with explicit limitation; reviewer P2 clarified stale conclusion vs stale head freshness failure | adopted into `requirement.md` | initial pass with P2 cleanup; fresh re-review pass with no findings | no | promoted to design |
| design | `requirement.md`; provider PR observation scripts; wrapper classification; fake `gh` tests; parent dogfooding/provider rules | None blocking; delegated architecture draft not used due dirty discussion baseline and no mid-authoring commit; P2 reviewer findings applied | adopted into `design.md` | fresh re-review pass with no findings | no | promoted to plan review |
| plan | `design.md`; `docs/authoring/issue-plan.md`; closure requirements; affected test harness | None blocking; delegated implementation-planner draft not used due same diff-guard precondition; updated to reflect mandatory wrapper change, failure detail closure, required delegation fields, S90 contract, report evidence destinations, complete concrete test cards, and skill-text doc-writer ownership | adopted into `plan.md` | second fresh re-review pass with no findings | no | ready for implementation handoff |

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）
- 委任 authoring の使用:
  - used / not used
- 未使用の場合:
  - manual authoring path / 委任ドラフトを昇格証跡として使っていない理由。
- lifecycle state（契約値）:
  - `requested`, `produced`, `integrated`, `partially_integrated`, `rejected`, `superseded`, `blocked`, `stale`
- 昇格不可 state:
  - `stale`, `rejected`, `superseded`, `blocked`
- 標準出力先:
  - 対象 scope の `discussions/` direct child にある flat Markdown
  - filename: `<ts>-<kind>-<slug>.md` または same-second collision 用 `<ts>-<nn>-<kind>-<slug>.md`
- 軽量 provenance:
  - `created_by_role`, `scope_id`, `source_paths`, `intended_targets`, `adoption_status: unreviewed`, `reflected_to: []`, `diff_guard_result`, fallback decision, report evidence destination, adoption ledger note
  - 互換 label: source artifacts, draft artifact path, status, integration result, rejected portions, blockers, reviewer result, promotion decision
- 禁止 self-claim:
  - `authority: accepted`, `adoption_status: adopted`, non-empty `reflected_to`, reviewer pass, phase completion, implementation readiness
- 禁止 wildcard token:
  - `*`, `grants.*`, `all`
- 標準必須にしない field:
  - task manifest hash, Permission Profile hash, session invocation hash, probe run id, session hash
- historical note:
  - 既存 `iss-00126` などの manifest/Profile/probe/session artifacts は grandfathered evidence として残し、削除・rename・validation failure 化しない。

| ロール（created_by_role） | 範囲（scope_id） | ドラフトパス（discussion draft path） | 参照元（source_paths） | 予定反映先（intended_targets） | 採用状態（adoption_status） | 反映先（reflected_to） | 差分ガード結果（diff_guard_result） | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果（reviewer result） | 昇格判断（promotion decision） |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| system-architect | iss-00187 | 該当なし | `requirement.md`; research/interview discussions; PR observation scripts/tests | `design.md` | not used | [] | not_run; target `discussions/` baseline dirty from uncommitted requirement evidence | 手動 authoring fallback | 該当なし | diff-guard precondition unavailable without mid-authoring commit/stage | pending spec-reviewer | delegated draft 昇格なし。canonical design は fresh spec-reviewer gate で昇格判断 |
| implementation-planner | iss-00187 | 該当なし | `requirement.md`; `design.md`; authoring docs | `plan.md` | not used | [] | not_run; same target `discussions/` baseline dirty | 手動 authoring fallback | 該当なし | diff-guard precondition unavailable without mid-authoring commit/stage | pending spec-reviewer | delegated draft 昇格なし。canonical plan は fresh spec-reviewer gate で昇格判断 |

### 委任ドラフトの失敗モード（Delegated Draft Failure Modes）
| 失敗モード | 期待される判定 | 許可される次アクション | レポート証跡の記録先（report evidence destination） | 昇格可否 |
|---|---|---|---|---|
| 同意なし（missing consent） | blocked / incomplete | 範囲付き同意を取得する、または手動 authoring に戻す | この section | ineligible |
| 前段 reviewer pass 不足 / stale（missing/stale previous reviewer pass） | blocked / incomplete | レビューゲートを再実行する（rerun reviewer gate） | レビューゲート証跡（Reviewer Gate Status / Final Spec Review Gate） | ineligible |
| 設計中の要件 gap（requirement gap during design） | blocked / incomplete | requirement phase へ戻す | 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger） | ineligible |
| 計画中の設計 gap（design gap during plan） | blocked / incomplete | design phase へ戻す | 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger） | ineligible |
| ロール利用不可（role unavailable） | blocked / manual path | 利用不可を記録し、妥当なら手動で続行する | この section | ineligible |
| 禁止行為の試行（forbidden action attempt） | rejected | ドラフトを破棄し incident を記録する | この section / decision ledger | ineligible |
| 古いドラフト（stale draft） | stale | 再生成または差分調整する | この section | ineligible |
| 置換済みドラフト（superseded draft） | superseded | 置換先ドラフトを参照する | この section | ineligible |
| 委任使用主張に対する証跡不足（missing draft evidence when delegated use is claimed） | incomplete | 証跡を追加する、または委任使用 claim を外す | この section | ineligible |
| reviewer 利用不可 / 拒否 / waiver / provisional（reviewer unavailable/denied/waived/provisional） | blocked / incomplete | fresh な passed reviewer を取得する、または昇格なしの risk acceptance を記録する | レビューゲート証跡（Reviewer Gate Status / Final Spec Review Gate） | ineligible |

## 実装サマリー (任意)
- `github-pr-observation` の CI 観測は Actions workflow runs/jobs を primary source とし、Checks/statuses/status rollup は supplemental evidence として扱う実装へ更新された。
- S01-S03 で collector と wrappers を段階実装し、S90 で provider/mirror docs と mirror scripts を同期した。S99 では最終統合検証で露出した旧 fake-gh fixture drift を修正し、親セッションで正しい focused pytest lane を再実行して green を確認した。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-06-16）

#### 対象
- Step: S01, S02, S03, S90, S99
- AC/EC: AC-001..AC-005, EC-001..EC-004
- 計画上の出典（Planned source）:
  - `plan.md` Spec-Locked Closure Index
  - closure ids: `tc-s01-001`, `tc-s01-002`, `tc-s02-001`..`tc-s02-005`, `tc-s03-001`..`tc-s03-003`, `tc-s90-001`, `tc-s90-002`, `tc-s99-001`

#### 実施内容
- S01: Actions-only green and supplemental permission behavior.
- S02: Actions failure/running/pending/zero/API-failure taxonomy and sanitized failure details.
- S03: snapshot/wait wrapper permission severity and stale-head preservation.
- S90: skill docs and dogfooding mirror synchronization.
- S99: final integrated verification, legacy fake-gh fixture alignment, and final reviewer gates.

#### 実行コマンド / 結果
```bash
uv run pytest tests/unit/infra/test_init_update.py -k "pr_observation or issue_187"
# 81 passed, 287 deselected

git diff --check
# pass

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=96
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S01 | Red | `tc-s01-001`, `tc-s01-002` red-required | Added issue_187 tests failed before implementation: Actions-only green remained `unknown`; later added jobs-unavailable regression failed as `passed` vs expected `unknown` before follow-up fix | `uv run pytest tests/unit/infra/test_init_update.py -k issue_187`; `uv run pytest tests/unit/infra/test_init_update.py -k "issue_187_actions_jobs_unavailable or actions_only or checks_collector"` | pass | Red evidence observed by dev-coder before green fixes |
| S01 | Green | Actions-only green and supplemental permission non-blocking path | `23 passed, 335 deselected`; parent rerun confirmed same result | `uv run pytest tests/unit/infra/test_init_update.py -k "issue_187_actions_jobs_unavailable or actions_only or checks_collector"` | pass | Covers S01 tests and discovered jobs-unavailable regression |
| S01 | Refactor | guardrail satisfied / no broad refactor | `git diff --check` passed; no wrapper/docs/mirror edits in S01 | `git diff --check`; diff inspection | pass | Refactor/tidy limited to scoped collector/test changes |
| S02 | Red | `tc-s02-001`..`tc-s02-005` red-required | Initial S02 tests failed before implementation for failed/stale/running/API-failure paths; zero Actions runs was confirmed to pass incorrectly on S01 collector | `uv run pytest tests/unit/infra/test_init_update.py -k issue_187_actions`; S01 collector temporary check for zero Actions runs | pass | Red evidence observed by dev-coder |
| S02 | Green | Actions failure/running/pending/zero/API failure taxonomy | Parent rerun after schema-unavailable follow-up: `33 passed, 333 deselected` | `uv run pytest tests/unit/infra/test_init_update.py -k "issue_187 or actions or stale or zero"` | pass | Includes `actions_primary_non_json` schema-unavailable metadata regression |
| S02 | Refactor | guardrail satisfied / no wrapper/docs/mirror edits | `git diff --check` passed after all S02 follow-ups | `git diff --check`; diff inspection | pass | Report update is parent evidence-only |
| S03 | Red | `tc-s03-001`, `tc-s03-002` red-required; `tc-s03-003` covered-existing | New wrapper tests initially failed because informational supplemental permission limitation was treated as permission blocker; wait fixture also exposed missing resume boundary until corrected | `uv run pytest tests/unit/infra/test_init_update.py -k "issue_187_snapshot_propagates_actions_pass_with_informational_supplemental_permission or issue_187_wait_preserves_actions_pending_with_informational_supplemental_permission"` | pass | Red evidence observed by dev-coder before wrapper severity fix |
| S03 | Green | snapshot/wait wrappers ignore informational supplemental permission blockers and preserve stale-head behavior | Parent rerun: `49 passed, 319 deselected` | `uv run pytest tests/unit/infra/test_init_update.py -k "issue_187 or pr_observation_snapshot or pr_observation_wait or stale_head"` | pass | Includes stale-head regressions and wrapper fake-gh Actions-primary fixtures |
| S03 | Refactor | guardrail satisfied / only wrapper scripts and tests changed | `git diff --check` passed; diff limited to S03 allowed paths | `git diff --check`; `git diff --stat` | pass | No mirror/docs/report edits by dev-coder |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S01 | `test_issue_187_actions_jobs_unavailable_prevents_actions_only_pass` | code-reviewer P1 | added regression test and bounded dev-coder follow-up fix | `tc-s01-002` / discovered false-pass coverage | no | code-reviewer initial fail; follow-up green command `23 passed` |
| S02 | zero Actions runs limitation severity | implementation / broad verification | recorded decision D-003; kept status non-pass and limitation informational to preserve existing zero-check grace | `tc-s02-005` | no | `test_issue_187_zero_actions_runs_is_never_passed`; existing zero-check grace test |
| S02 | generic API failure metadata and check-run-derived Actions failure shape | code-reviewer P1 | bounded dev-coder follow-up added tests and fixes | `tc-s02-001`, `tc-s02-004` | no | code-reviewer fail; follow-up `32 passed` |
| S02 | schema-unavailable Actions metadata | code-reviewer P1 | bounded dev-coder follow-up added non-JSON response regression and metadata fix | `tc-s02-004` | no | `test_issue_187_actions_primary_non_json_response_is_actions_read_and_redacted`; follow-up `33 passed` |
| S03 | existing wrapper fake-gh tests lacked Actions endpoints after Actions-primary collector became required | focused pytest failure during S03 | added Actions success runs/jobs payloads to affected wrapper fake-gh tests | `tc-s03-001`, `tc-s03-003` | no | focused pytest `49 passed` |
| S99-post-observation | Actions running/pending plus supplemental permission denial could become a permission remediation blocker instead of wait continuation | PR #190 Codex P1 review thread `PRRT_kwDOQ99OK86Jrv1v`; QA reviewer P2 | added parametrized regression and collector predicate so decisive non-terminal Actions evidence downgrades supplemental limitations to informational coverage limitation for running, queued, and pending | `tc-s01-002`, `tc-s02-003`, `tc-s03-002` / discovered P1/P2 coverage | no | `test_issue_187_actions_non_terminal_downgrades_supplemental_permission_limitations`; parent rerun `3 passed, 371 deselected` |
| S99-post-observation | Actions failed plus supplemental permission denial could become a permission-remediation blocker beside actionable CI failure | PR #190 Codex P2 review thread `PRRT_kwDOQ99OK86JsXBm` | added failed-Actions regression and collector predicate so decisive failed Actions evidence downgrades supplemental limitations while preserving `ci.status="failed"` and failure details | `tc-s01-002`, `tc-s02-001` / discovered P2 coverage | no | `test_issue_187_actions_failed_job_downgrades_supplemental_permission_limitations`; parent rerun `1 passed, 374 deselected`; `issue_187` focused `20 passed` |
| S99-post-observation | Actions jobs API successful JSON missing/non-list `jobs` could be counted as successful collection and allow Actions-only false-pass | PR #190 Codex P2 review thread `PRRT_kwDOQ99OK86JtnyR` | added regression and collector guard so missing/non-list `jobs` is blocking `github_actions_jobs_unavailable`, increments failed job collection, and cannot produce `passed` | `tc-s01-002`, `tc-s02-004`, `tc-s99-001` / discovered P2 coverage | no | `test_issue_187_actions_jobs_missing_field_prevents_actions_only_pass`; dev-coder Red `3 failed`; parent focused `25 passed`; required lane `91 passed` |
| S99-post-observation | Accepted abbreviated `--head-sha` values could be sent directly to Actions queries and produce zero-runs false classification | PR #190 Codex P2 review thread `PRRT_kwDOQ99OK86JtnyU` | preserved abbreviated SHA compatibility by resolving the accepted prefix to current full `headRefOid` before Actions/check-runs/status queries; resolution failure is blocking `pr_head_sha_resolution_failed` and non-pass | `tc-s03-003`, `tc-s99-001` / discovered P2 coverage | no | existing abbreviated SHA prefix tests updated to assert full 40-char SHA API queries; parent focused `25 passed`; required lane `91 passed` |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S01 | `tc-s01-001`, `tc-s01-002` | Actions-only green passes with explicit coverage limitation; supplemental permission is not normal blocker; no raw token/stderr leak | dev-coder implementation; parent focused pytest rerun; code-reviewer re-review pass | pass | S01 committed after reviewer gate |
| S02 | `tc-s02-001`..`tc-s02-005` | Actions failures/running/pending/zero/API failures are non-pass and failure details follow design shape | dev-coder implementation and follow-ups; parent focused pytest rerun `33 passed`; `git diff --check` pass; fresh code-reviewer re-review pass with no findings | pass | Ready for S02 commit |
| S03 | `tc-s03-001`..`tc-s03-003` | wrapper tests and stale head regression pass; informational supplemental permission limitations do not become permission blockers | dev-coder implementation; parent focused pytest rerun `49 passed`; `git diff --check` pass; fresh code-reviewer pass | pass | Ready for S03 commit |
| S90 | `tc-s90-001`, `tc-s90-002` | skill docs reflect Actions-primary permission contract and provider/mirror changed files are aligned | doc-writer SKILL.md update; utility-worker mirror sync; parent `cmp` checks for provider/mirror SKILL.md and three scripts exit 0; `git diff --check` pass; fresh spec-reviewer/code-reviewer pass | pass | Ready for S90 commit |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| `tc-s01-001` | S01 | yes | red-required | issue_187 test failed before collector used Actions primary | `uv run pytest tests/unit/infra/test_init_update.py -k "issue_187_actions_jobs_unavailable or actions_only or checks_collector"` -> 23 passed | pass | `test_issue_187_actions_only_green_passes_with_coverage_limitation` |
| `tc-s01-002` | S01 | yes | red-required | supplemental permission / jobs-unavailable false-pass regressions failed before fixes | `uv run pytest tests/unit/infra/test_init_update.py -k "issue_187_actions_jobs_unavailable or actions_only or checks_collector"` -> 23 passed; `git diff --check` -> pass | pass | `test_issue_187_actions_only_green_redacts_supplemental_permission_stderr`; `test_issue_187_actions_jobs_unavailable_prevents_actions_only_pass` |
| `tc-s02-001` | S02 | yes | red-required | failed job/step initially returned non-failed/legacy shape; reviewer found check-run-derived shape gap | `uv run pytest tests/unit/infra/test_init_update.py -k "issue_187 or actions or stale or zero"` -> 33 passed | pass | `test_issue_187_actions_failed_job_surfaces_step_detail`; check-run-derived shape/dedupe regression added |
| `tc-s02-002` | S02 | yes | red-required | stale conclusion initially not classified as CI failure | `uv run pytest tests/unit/infra/test_init_update.py -k "issue_187 or actions or stale or zero"` -> 33 passed | pass | `test_issue_187_actions_stale_conclusion_is_ci_failure_not_stale_head` |
| `tc-s02-003` | S02 | yes | red-required | running/pending states initially not classified from Actions | `uv run pytest tests/unit/infra/test_init_update.py -k "issue_187 or actions or stale or zero"` -> 33 passed | pass | `test_issue_187_actions_running_and_pending_states_are_not_passed` |
| `tc-s02-004` | S02 | yes | red-required | Actions API failure initially could pass or lack required metadata; schema-unavailable non-JSON path lacked metadata before follow-up | `uv run pytest tests/unit/infra/test_init_update.py -k "issue_187 or actions or stale or zero"` -> 33 passed; `git diff --check` -> pass | pass | API failure/redaction tests plus `test_issue_187_actions_primary_non_json_response_is_actions_read_and_redacted` |
| `tc-s02-005` | S02 | yes | red-required | zero Actions runs on S01 collector could pass with supplemental green | `uv run pytest tests/unit/infra/test_init_update.py -k "issue_187 or actions or stale or zero"` -> 33 passed | pass | `test_issue_187_zero_actions_runs_is_never_passed` |
| `tc-s03-001` | S03 | yes | red-required | snapshot initially treated informational supplemental permission limitation as permission blocker | `uv run pytest tests/unit/infra/test_init_update.py -k "issue_187 or pr_observation_snapshot or pr_observation_wait or stale_head"` -> 49 passed | pass | `test_issue_187_snapshot_propagates_actions_pass_with_informational_supplemental_permission` |
| `tc-s03-002` | S03 | yes | red-required | wait wrapper initially needed fixture correction after Red; final behavior preserves running as wait/resume | `uv run pytest tests/unit/infra/test_init_update.py -k "issue_187 or pr_observation_snapshot or pr_observation_wait or stale_head"` -> 49 passed | pass | `test_issue_187_wait_preserves_actions_pending_with_informational_supplemental_permission` |
| `tc-s03-003` | S03 | yes | covered-existing | existing stale-head tests cover head mismatch / rerun action | `uv run pytest tests/unit/infra/test_init_update.py -k "issue_187 or pr_observation_snapshot or pr_observation_wait or stale_head"` -> 49 passed | pass | Existing stale-head regressions remained green |
| `tc-s90-001` | S90 | yes | inspect-only | old `SKILL.md` said checks/statuses/rollup read failures normally return unknown/fix-permissions | provider and mirror `SKILL.md` inspection; `rg` for Actions read / supplemental / informational limitation; `diff -u provider mirror` -> no diff | pass | Docs now name Actions read as normal CI observation permission and avoid Checks read as ordinary fix for Actions-decisive green |
| `tc-s90-002` | S90 | yes | inspect-only | mirror scripts differed from provider after S01-S03 provider-first commits | `cmp -s` provider/mirror for `SKILL.md`, `fetch_pr_checks_snapshot.sh`, `fetch_pr_observation_snapshot.sh`, `wait_pr_observation.sh` -> all exit 0; `git diff --check` -> pass | pass | Dogfooding mirror now matches provider for intended changed assets |

- `closure id / test id` は Spec-Locked Closure Index の `id` を指す。別 alias を使う場合は `Closure Delta` で対応を記録する。

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| `tc-s01-001` | S01 | Actions workflow runs/jobs success with supplemental permission denied returns `ci.status="passed"` and informational `ci_coverage_limited_to_github_actions` | pass | Parent rerun: 23 focused tests passed |
| `tc-s01-002` | S01 | token marker absent; blocking supplemental `github_token_permission_denied` absent; jobs API unavailable prevents `passed` | pass | Parent rerun: 23 focused tests passed; code-reviewer re-review pass |
| `tc-s02-001` | S02 | Actions failed job/step produces sanitized `ci.failures[]` with dedupe shape | pass | Focused tests and fresh code-reviewer pass |
| `tc-s02-002` | S02 | `stale` Actions conclusion is CI failure, not stale head | pass | Focused tests and fresh code-reviewer pass |
| `tc-s02-003` | S02 | running/pending Actions states are non-pass | pass | Focused tests and fresh code-reviewer pass |
| `tc-s02-004` | S02 | primary Actions API failures, including schema-unavailable, are blocking `actions_read` unknown with sanitized metadata | pass | Focused tests and fresh code-reviewer pass |
| `tc-s02-005` | S02 | zero Actions runs is never passed | pass | Focused tests and fresh code-reviewer pass |
| `tc-s03-001` | S03 | Snapshot propagates Actions-primary passed status and avoids permission remediation for informational supplemental limitation | pass | Parent rerun: 49 focused tests passed; fresh code-reviewer pass |
| `tc-s03-002` | S03 | Wait preserves Actions running/pending as wait/resume and ignores informational supplemental permission limitation | pass | Parent rerun: 49 focused tests passed; fresh code-reviewer pass |
| `tc-s03-003` | S03 | Stale head remains freshness failure with `rerun_for_current_head` | pass | Existing stale-head regressions included in focused suite; fresh code-reviewer pass |
| `tc-s90-001` | S90 | Provider and mirror `SKILL.md` describe Actions read as normal CI permission, supplemental Checks/statuses/rollup, and informational limitation semantics | pass | Docs inspection, provider/mirror `diff -u`, and fresh spec-reviewer passed |
| `tc-s90-002` | S90 | Provider and dogfooding mirror changed assets are byte-identical where intended | pass | Parent/reviewer `cmp` checks for SKILL.md and three scripts all exit 0; fresh code-reviewer passed |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| added | `tc-s01-002` | `test_issue_187_actions_jobs_unavailable_prevents_actions_only_pass` | `tc-s01-002` | code-reviewer found primary Actions jobs unavailable could false-pass; this is within AC-005/S01 false-pass safety | no | no; re-review pass obtained |
| added | `tc-s02-001` | check-run-derived Actions failure shape/dedupe regression | `tc-s02-001` | code-reviewer found legacy shape could appear from supplemental check-run path | no | no; fresh code-reviewer pass obtained |
| added | `tc-s02-004` | generic and schema-unavailable Actions API failure metadata regressions | `tc-s02-004` | code-reviewer found primary Actions failure metadata gaps | no | no; fresh code-reviewer pass obtained |
| added | `tc-s03-001`, `tc-s03-002` | informational supplemental permission wrapper regressions | `tc-s03-001`, `tc-s03-002` | S03 Red showed wrapper permission gating needed severity/blocking semantics | no | no; fresh code-reviewer pass obtained |
| added | `tc-s01-001`, `tc-s03-001`, `tc-s99-001` | `test_issue_187_actions_job_details_are_documented_and_fingerprinted` | `tc-s01-001`, `tc-s03-001`, `tc-s99-001` | Codex P2 found Actions primary evidence absent from fingerprint and documented job detail key absent from payload | no | fresh code/QA/spec review passed for prior contract follow-up |
| added | `tc-s02-001`, `tc-s99-001` | `test_issue_187_actions_failed_step_details_are_fingerprinted` | `tc-s02-001`, `tc-s99-001` | code-reviewer P2 found failed step details could change without fingerprint changes | no | fresh code/QA/spec review passed for prior contract follow-up |
| added | `tc-s01-002`, `tc-s02-004`, `tc-s99-001` | `test_issue_187_actions_jobs_missing_field_prevents_actions_only_pass` | `tc-s01-002`, `tc-s02-004`, `tc-s99-001` | Codex P2 found successful Actions jobs JSON without `jobs` could be counted as observed job evidence and false-pass; QA P2 asked to also cover non-list `jobs` values | no | fresh code/QA/spec review passed; test now covers missing/object/null jobs payloads |
| updated | `tc-s03-003`, `tc-s99-001` | abbreviated head SHA prefix tests assert full-SHA API queries | `tc-s03-003`, `tc-s99-001` | Codex P2 found accepted abbreviated SHA could be used as Actions `head_sha` filter and misclassify zero runs | no | fresh code/QA/spec review passed |
| added | `tc-s99-001` | `test_issue_187_abbreviated_head_sha_resolution_failure_blocks_green_ci` | `tc-s99-001` | QA P2 found the new abbreviated SHA resolution failure branch lacked an otherwise-green negative-path regression | no | fresh code/QA/spec review passed |

#### ワークフロー委任同意の証跡（Workflow Delegation Consent）
`workflow_issue.md` is the policy source for workflow-scoped delegation consent. This report records observed consent, boundary, expiry, and denied / unavailable handling only.

| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user instruction invoking `$spec-dock-issue-planning` and `$spec-dock-issue-execution` workflows | `/Users/iwasawayuuta/.codex/worktrees/1fe5/spec-dock` | iss-00187 | current session | spec-reviewer; system-architect; implementation-planner; dev-coder; doc-writer; code-reviewer; qa-reviewer as named in `plan.md` | same repo/worktree, active issue, issue-local docs and bounded implementation steps; no destructive action, publishing, credential expansion, or scope expansion without separate instruction | issue complete / session end / scope change / host policy conflict / user revocation | system-architect and implementation-planner discussion-draft authoring not used because target discussions baseline was dirty; reviewer and implementation roles available | proceed with step-by-step delegated implementation, review, and commit gates |

#### 実装委任ゲート（Implementation Delegation Gate）
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| authoring-requirement | delegated-review | workflow gate | spec-reviewer | requirement review | `requirement.md`; `report.md`; discussions | read-only review | file edits | reviewer findings and `review_status` | P0/P1 blocker | findings, status, rationale | fresh pass |
| authoring-design | approved-local-authoring | dirty delegated-draft baseline | N/A for draft; spec-reviewer for gate | canonical design authoring and review | `design.md`; `report.md` | issue-local docs | source code/test edits | fresh spec-reviewer | design blocker | findings, status, rationale | pass; promoted to plan review |
| authoring-plan | approved-local-authoring | dirty delegated-draft baseline | N/A for draft; spec-reviewer for gate | canonical plan authoring and review | `plan.md`; `report.md` | issue-local docs | source code/test edits | fresh spec-reviewer | plan blocker | findings, status, rationale | pass; ready for implementation handoff |
| S01 | delegated | runtime/test implementation step | dev-coder | Actions-only green and supplemental permission collector behavior | `plan.md` S01; `design.md`; `requirement.md` | provider collector and focused tests | wrappers, SKILL.md, mirror, Codex review collector, trigger script, merge automation | focused pytest and `git diff --check` | public CLI change; arbitrary endpoint input; secret leak; jobs unavailable false-pass | changed files, tests, closure evidence, ledger note | pass; code-reviewer re-review passed |
| S02 | delegated | runtime/test implementation step | dev-coder | Actions taxonomy, failure details, zero runs, primary API failures | `plan.md` S02; `design.md`; `requirement.md`; S01 evidence | provider collector and focused tests | wrappers, SKILL.md, mirror, docs, report edits by worker | focused pytest and `git diff --check` | inability to distinguish failure/running/pending; API failure metadata gaps | changed files, tests, closure evidence, ledger notes | pass; fresh code-reviewer re-review passed with no findings |
| S03 | delegated | runtime/test implementation step | dev-coder | snapshot/wait wrapper classification and stale-head regression | `plan.md` S03; `design.md`; `requirement.md`; S01/S02 evidence | wrapper scripts and focused tests | review lifecycle, trigger script, merge automation, SKILL.md, mirror files, report edits by worker | focused pytest and `git diff --check` | stale head and CI failure cannot remain distinct | changed files, tests, closure evidence, ledger note | pass for implementation and closure evidence; fresh code-reviewer pass obtained |
| S90-docs | delegated | docs impact resolution step | doc-writer | provider/mirror skill-text wording | `plan.md` S90; `design.md`; `requirement.md`; S01-S03 evidence | provider and mirror `SKILL.md` | scripts, tests, source behavior, issue docs by worker | docs inspection, provider/mirror diff, `git diff --check` | docs contradict Actions-primary contract | changed files, docs inspection, residual risks | pass for worker verification; reviewer pending |
| S90-mirror | delegated | mechanical mirror sync step | utility-worker | dogfooding mirror copies of changed provider scripts | `plan.md` S90; S01-S03 provider diffs | `.agents/skills/github-pr-observation/scripts/**` mirror copies only | provider source, tests, SKILL.md, issue docs | provider/mirror `cmp`, `git diff --check` | provider/mirror cannot align | changed files, comparison result, residual risks | pass for worker verification; reviewer pending |
| S99-fixture-alignment | delegated | final integrated verification remediation | dev-coder | old fake-gh fixture alignment for Actions-primary collector | `plan.md` S99; S01-S90 committed evidence; initial S99 pytest failure | `tests/unit/infra/test_init_update.py` only | provider scripts, mirror scripts, SKILL.md, issue docs by worker | parent rerun of `uv run pytest tests/unit/infra/test_init_update.py -k "pr_observation or issue_187"`; `git diff --check`; `spec-dock validate` | fixture changes mask behavior or alter provider/runtime behavior | changed files, exact assertion rationale, tests, residual risks | pass for worker verification; reviewer pending |
| S99-post-observation | delegated | PR observation remediation after first PR check | dev-coder | false-pass hardening and CI fixture drift after PR #190 observation | PR #190 observation result; Codex P2 findings; S99 final delivery gate | provider/mirror `fetch_pr_checks_snapshot.sh`; `tests/unit/infra/test_init_update.py` | issue docs/report by worker; unrelated source/docs; `spec-dock/initiatives/**/.meta.json` | focused pytest for issue_187/issue_176/issue_170/status_rollup/actions_jobs; full `tests/unit/infra/test_init_update.py`; `git diff --check`; provider/mirror `cmp` | inability to prevent Actions jobs failure false-pass or statusCheckRollup non-green false-pass | changed files, tests, reviewer evidence, residual risks | pass for worker verification; code-reviewer and qa-reviewer pass |
| S99-post-observation-p1 | delegated | PR observation remediation after second PR observation | dev-coder | Actions running/pending supplemental permission blocker after PR #190 observation | PR #190 observation result on head `8456d3528d78b64fba96a28f5f3cfc0facca6fb0`; Codex P1 thread `PRRT_kwDOQ99OK86Jrv1v`; S99 delivery gate | provider/mirror `fetch_pr_checks_snapshot.sh`; `tests/unit/infra/test_init_update.py` | issue docs/report by worker; unrelated source/docs | focused regression; issue_187 focused suite; full `tests/unit/infra/test_init_update.py`; `git diff --check`; provider/mirror `cmp` | permission-denied supplemental signals still force `fix_github_token_permissions` while Actions primary says running/pending | changed files, tests, reviewer evidence, residual risks | pass for worker verification; reviewer pending |
| S99-post-observation-contract | delegated | PR observation remediation after fourth PR observation | dev-coder | wait regression lane, Actions fingerprint evidence, documented job details key, and failed-step fingerprint evidence after PR #190 observation | PR #190 observation result on head `2734987cedb865d6192ceb5ed984977f0dd50137`; Codex threads `PRRT_kwDOQ99OK86JszfI`, `PRRT_kwDOQ99OK86JszfM`, `PRRT_kwDOQ99OK86JszfO`; design `ci.actions.jobs[]` contract; code-reviewer P2 | provider/mirror `fetch_pr_checks_snapshot.sh`; `tests/unit/infra/test_init_update.py`; `design.md` | issue docs/report by worker; unrelated source/docs | required `pr_observation or issue_187` lane; targeted fingerprint/jobs regressions; full `tests/unit/infra/test_init_update.py`; `git diff --check`; provider/mirror `cmp`; `spec-dock validate` | short-timeout waits time out, fingerprint omits primary Actions evidence or failed steps, or documented job detail key remains absent | changed files, tests, ledger note, residual risks | pass for worker verification; reviewer pending |
| S99-post-observation-contract-p2 | delegated | PR observation remediation after fifth PR observation | dev-coder | missing Actions jobs list false-pass and abbreviated SHA query resolution after PR #190 observation | PR #190 observation result on head `66c6a3be199a30ea0104816361822de5ddda80a5`; Codex threads `PRRT_kwDOQ99OK86JtnyR`, `PRRT_kwDOQ99OK86JtnyU`; design false-pass and CLI compatibility contract | provider/mirror `fetch_pr_checks_snapshot.sh`; `tests/unit/infra/test_init_update.py`; `design.md` | issue docs/report by worker; unrelated source/docs | targeted `abbreviated_head_sha or actions_jobs_missing or issue_187` lane; required `pr_observation or issue_187` lane; `git diff --check`; provider/mirror `cmp` | missing/non-list jobs can pass, abbreviated SHA accepted input can misclassify zero Actions runs, or resolution failure leaks secrets/raw stderr | changed files, tests, ledger note, residual risks | pass for worker verification; reviewer pending |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| requirement-review-1 | spec-reviewer | Initial requirement review returned pass with P2 cleanup findings for stale taxonomy and research metadata alignment | none | read-only spec review | pass | P2 cleanup applied before promotion | accepted |
| requirement-review-2 | spec-reviewer | Fresh requirement re-review returned no findings and confirmed design promotion readiness | none | read-only spec review | pass | none | accepted |
| design-review-1 | spec-reviewer | Initial design review returned pass with P2 cleanup findings for wrapper permission handling and Actions failure detail shape | none | read-only spec review | pass | P2 cleanup applied before re-review | accepted |
| design-review-2 | spec-reviewer | Fresh design re-review returned no findings and confirmed design promotion readiness | none | read-only spec review | pass | none | accepted |
| plan-review-1 | spec-reviewer | Initial plan review failed on missing delegation contract fields, missing S90 delegation contract, vague report evidence destinations, and stale design gate state | none | read-only spec review | fail | P1/P2 cleanup applied; re-review pending | accepted for remediation |
| plan-review-2 | spec-reviewer | Fresh plan re-review failed on incomplete concrete test cards and S90 skill-text role ownership | none | read-only spec review | fail | P1/P2 cleanup applied; second re-review pending | accepted for remediation |
| plan-review-3 | spec-reviewer | Second fresh plan re-review returned no findings and confirmed implementation handoff readiness | none | read-only spec review | pass | none | accepted |
| S01-dev | dev-coder | Implemented Actions workflow runs/jobs primary green path, supplemental permission non-blocking coverage limitation, `ci.actions` summary, and jobs-unavailable false-pass regression fix | `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`; `tests/unit/infra/test_init_update.py` | `uv run pytest tests/unit/infra/test_init_update.py -k "issue_187_actions_jobs_unavailable or actions_only or checks_collector"` -> 23 passed; `git diff --check` -> pass | pass after reviewer follow-up | S02/S03 remain for failure taxonomy and wrappers | accepted |
| S01-review-1 | code-reviewer | Initial S01 review found P1: jobs API unavailable could still pass | none | read-only code review | fail | dev-coder follow-up added regression/fix | accepted for remediation |
| S01-review-2 | code-reviewer | Fresh S01 re-review found no findings; previous P1 fixed | none | read-only code review | pass | none | accepted |
| S02-dev | dev-coder | Implemented Actions taxonomy, failure details, zero-runs non-pass, primary API failure handling, and follow-up fixes for metadata/shape/schema gaps | `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`; `tests/unit/infra/test_init_update.py` | `uv run pytest tests/unit/infra/test_init_update.py -k "issue_187 or actions or stale or zero"` -> 33 passed; `git diff --check` -> pass | pass | none after fresh code-reviewer pass | accepted |
| S02-review-1 | code-reviewer | Initial S02 review found P1: generic Actions API failure metadata missing and check-run-derived Actions failure shape inconsistent | none | read-only code review | fail | dev-coder follow-up fixed both and added tests | accepted for remediation |
| S02-review-2 | code-reviewer | Fresh S02 review found P1: schema-unavailable Actions primary path missing metadata; report closure evidence incomplete | none | read-only code review | fail | dev-coder schema follow-up completed; report evidence updated | accepted for remediation |
| S02-review-3 | code-reviewer | Third S02 review found no additional code P1, but report evidence was stale/pending | none | read-only code review | fail | report evidence updated to latest 33-pass result | accepted for remediation |
| S02-review-4 | code-reviewer | Fresh S02 re-review found no findings; confirmed taxonomy, failure shape, API failure metadata, zero-runs behavior, and report closure evidence | none | `uv run pytest tests/unit/infra/test_init_update.py -k 'issue_187 or actions or stale or zero'` -> 33 passed; `git diff --check` -> pass | pass | none | accepted |
| S03-dev | dev-coder | Implemented wrapper permission-blocker severity checks, added S03 wrapper regressions, and refreshed affected wrapper fake-gh fixtures for Actions-primary collector output | `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh`; `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`; `tests/unit/infra/test_init_update.py` | `uv run pytest tests/unit/infra/test_init_update.py -k "issue_187 or pr_observation_snapshot or pr_observation_wait or stale_head"` -> 49 passed; `git diff --check` -> pass | pass | none | accepted |
| S03-review-1 | code-reviewer | Reviewed uncommitted S03 wrapper/test/report changes after parent verification | same S03 files | `uv run pytest tests/unit/infra/test_init_update.py -k 'issue_187 or pr_observation_snapshot or pr_observation_wait or stale_head'` -> 49 passed; `git diff --check` -> pass | pass | none | accepted |
| S90-doc-writer | doc-writer | Updated provider and mirror `SKILL.md` permission/remediation wording for Actions-primary CI observation | `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`; `.agents/skills/github-pr-observation/SKILL.md` | `git diff --check -- ...` -> pass; `diff -u provider mirror` -> no diff; `rg`/`sed` inspection of permission section | pass | none | accepted |
| S90-mirror-sync | utility-worker | Copied changed provider PR observation scripts into dogfooding mirror and verified byte equality | `.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`; `.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh`; `.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh` | `cmp -s` for all three provider/mirror script pairs -> exit 0; `git diff --check` -> pass | pass | behavior tests remain S01-S03/S99 responsibility | accepted |
| S90-spec-review-1 | spec-reviewer | Reviewed S90 docs/report alignment against requirement/design/plan | none | provider/mirror SKILL.md inspection; `cmp -s` checks; `diff -u`; `git diff --check` | pass | none | accepted |
| S90-code-review-1 | code-reviewer | Reviewed S90 mechanical mirror sync and confirmed no provider script behavior edits in the uncommitted diff | none | provider/mirror `cmp -s` checks; provider script diff empty; `git diff --check` | pass | none | accepted |
| S99-dev | dev-coder | Added Actions runs/jobs fake-gh responses to older pr_observation tests and adjusted exact expected metadata to the current Actions-primary output shape without touching provider or mirror scripts | `tests/unit/infra/test_init_update.py` | dev-coder reported a non-authoritative selector with stale `issue_180_s02`; parent authoritative rerun used `uv run pytest tests/unit/infra/test_init_update.py -k "pr_observation or issue_187"` -> `81 passed, 287 deselected`; `git diff --check` -> pass; `./spec-dock/scripts/spec-dock validate` -> pass | code-reviewer pass; qa-reviewer pass; spec-reviewer initial fail remediated and fresh re-review pass | none | accepted |
| S99-code-review-1 | code-reviewer | Reviewed S99 test/report diff and found no masking of Actions-primary behavior or weakened exact assertions | none | `git diff --check` -> pass; `uv run pytest tests/unit/infra/test_init_update.py -k "pr_observation or issue_187"` -> 81 passed; `./spec-dock/scripts/spec-dock validate` -> pass | pass | none | accepted |
| S99-qa-review-1 | qa-reviewer | Confirmed AC/EC coverage and S99 fixture remediation are sufficient; live GitHub API test is not required by plan | none | focused pytest 81 passed; provider/mirror `cmp -s` checks; `git diff --check`; `spec-dock validate` | pass | fake-gh based coverage only, accepted by plan | accepted |
| S99-spec-review-1 | spec-reviewer | Initial final spec review failed on placeholder rows and stale S99 worker selector overclaim | none | read-only spec review | fail | remediated in report | accepted for remediation |
| S99-spec-review-2 | spec-reviewer | Fresh final spec re-review found no blocking findings after placeholder cleanup and parent-authoritative S99 verification wording | none | `git diff --check` -> pass; `uv run pytest tests/unit/infra/test_init_update.py -k "pr_observation or issue_187"` -> 81 passed; `./spec-dock/scripts/spec-dock validate` -> pass | pass | none | accepted |
| S99-post-observation-dev | dev-coder | Fixed PR #190 observation regressions: Actions jobs collection failures now force non-pass, statusCheckRollup failed/running/pending blocks Actions-only pass, older fixtures expose Actions endpoints, and dogfooding meta snapshot includes iss-00186/iss-00187 | `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`; `.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`; `tests/unit/infra/test_init_update.py` | focused pytest `18 passed`; target dogfooding meta test `1 passed`; full `uv run pytest tests/unit/infra/test_init_update.py` -> `371 passed`; `git diff --check` -> pass; provider/mirror `cmp_exit=0` | code-reviewer pass; qa-reviewer pass | external API unknown rollup values not exhaustively enumerated | accepted |
| S99-post-observation-code-review | code-reviewer | Reviewed post-observation false-pass and fixture drift diff; found no blocking findings | none | `git diff --check` -> pass; provider/mirror `cmp_exit=0`; diff inspection | pass | pending+CLEAN has existing behavior but no dedicated new test; not blocking | accepted |
| S99-post-observation-qa-review | qa-reviewer | Confirmed Codex P2 coverage and fixture drift remediation are sufficient for the changed blast radius | none | reviewed focused `18 passed`, dogfooding target pass, full `test_init_update.py` `371 passed`, diff check, provider/mirror cmp | pass | unknown external rollup states remain a low residual risk | accepted |
| S99-post-observation-spec-review | spec-reviewer | Reviewed post-observation report evidence against requirement/design/plan/report alignment and found no blocking findings | none | read-only spec review of `report.md` diff and issue docs | pass | did not rerun tests; relied on recorded verification evidence | accepted |
| S99-post-observation-p1-dev | dev-coder | Fixed PR #190 current P1: decisive running/pending Actions primary evidence now downgrades supplemental permission limitations to informational coverage limitation, preserving non-pass CI status and wait continuation | `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`; `.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`; `tests/unit/infra/test_init_update.py` | dev-coder full `uv run pytest tests/unit/infra/test_init_update.py` -> `372 passed`; parent focused regression rerun -> `1 passed, 371 deselected`; `git diff --check` pass; provider/mirror `cmp` exit 0 | code-reviewer pass; qa-reviewer pass with non-blocking P2 | existing broad supplemental-unavailability folding remains unchanged when Actions primary is decisive | accepted; P2 test coverage follow-up delegated |
| S99-post-observation-p1-p2-dev | dev-coder | Addressed QA P2 by parametrizing the non-terminal supplemental permission regression for running, queued, and pending without changing provider/mirror scripts | `tests/unit/infra/test_init_update.py` | parent targeted rerun `uv run pytest tests/unit/infra/test_init_update.py -k test_issue_187_actions_non_terminal_downgrades_supplemental_permission_limitations` -> `3 passed, 371 deselected`; `issue_187` focused -> `19 passed`; full `test_init_update.py` -> `374 passed`; `git diff --check` -> pass; `spec-dock validate` -> ok | code-reviewer pass; qa-reviewer pass; spec-reviewer pass | none known | accepted |
| S99-post-observation-p2-failed-dev | dev-coder | Fixed PR #190 current P2: decisive failed Actions evidence now downgrades supplemental permission limitations to informational coverage limitation while keeping `ci.status="failed"` and Actions failure details | `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`; `.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`; `tests/unit/infra/test_init_update.py` | dev-coder Red targeted regression `1 failed`; parent targeted regression -> `1 passed, 374 deselected`; parent `issue_187` focused -> `20 passed`; full `test_init_update.py` -> `375 passed`; `git diff --check` -> pass; provider/mirror `cmp` -> pass; `spec-dock validate` -> ok | code-reviewer pass; qa-reviewer pass; spec-reviewer pass | none known | accepted |
| S99-post-observation-contract-dev | dev-coder | Addressed latest Codex review set: local required lane did not reproduce the P1 timeout before or after; fingerprint now includes sanitized Actions runs/jobs, summary, and Actions failure evidence including failed steps; documented `ci.actions.jobs[]` now exposes job details, with counts/collection moved to `jobs_summary` and `jobs_detail` retained as alias | `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`; `.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`; `tests/unit/infra/test_init_update.py`; `design.md`; `report.md` | dev-coder required lane `89 passed`; dev-coder full `test_init_update.py` `376 passed`; Turing targeted `1 passed`; parent targeted `2 passed`; parent required lane `90 passed`; parent full `test_init_update.py` `377 passed`; `git diff --check` -> pass; provider/mirror `cmp` -> pass; `spec-dock validate` -> pass | pending | potential external consumers of old undocumented `ci.actions.jobs.total/counts` need `jobs_summary` | accepted for fresh review |
| S99-post-observation-contract-p2-dev | dev-coder | Addressed latest Codex P2 review set: missing/non-list Actions jobs JSON is now blocking jobs unavailable and abbreviated SHA inputs are resolved to current full PR head SHA before Actions/check-runs/status queries. After QA P2 findings, test-only follow-ups parametrized missing/object/null `jobs` payloads and added an abbreviated SHA resolution-failure negative path | `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`; `.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`; `tests/unit/infra/test_init_update.py`; `design.md`; `report.md` | dev-coder Red `3 failed`; dev-coder focused `25 passed`; dev-coder required lane `91 passed`; jobs non-list QA P2 focused `25 passed`; jobs non-list QA P2 required lane `93 passed`; SHA resolution QA P2 focused `28 passed`; SHA resolution QA P2 required lane `94 passed`; parent focused after final QA P2 `28 passed`; parent required lane after final QA P2 `94 passed`; `git diff --check` -> pass; provider/mirror `cmp` -> pass; `spec-dock validate` -> pass | pending | new `gh pr view --json headRefOid` call is only on abbreviated SHA inputs; full SHA path unchanged | accepted for fresh review |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| N/A | none | N/A | N/A | N/A | N/A | N/A | N/A | All implementation/test/docs changes were delegated to the planned roles; orchestrator direct edits were limited to issue-level `report.md` evidence. |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| requirement | spec authoring gate | spec-reviewer | fresh | passed | N/A | proceed to design | Fresh re-review had no findings |
| design | spec authoring gate | spec-reviewer | fresh | passed | N/A | proceed to plan review | Fresh re-review had no findings |
| plan | spec authoring gate | spec-reviewer | fresh | passed | N/A | ready for implementation handoff | Second fresh re-review had no findings |
| S01 | step code review gate | code-reviewer | fresh after follow-up | passed | N/A | proceed to S01 commit | No findings after jobs-unavailable P1 fix |
| S02 | step code review gate | code-reviewer | fresh after follow-ups and report update | passed | N/A | proceed to S02 commit | No findings; focused pytest 33 passed and diff check passed |
| S03 | step code review gate | code-reviewer | passed | pass | S03-review-1 | proceed to S03 commit | Dev-coder, parent focused pytest, reviewer focused pytest, and `git diff --check` passed |
| S90 | step docs/spec review gate | spec-reviewer | fresh | passed | N/A | proceed to S90 commit | No findings; docs/report align with Actions-primary contract |
| S90 | step mirror/code review gate | code-reviewer | fresh | passed | N/A | proceed to S90 commit | No findings; provider/mirror byte equality confirmed |
| S99 | final integrated verification remediation gate | code-reviewer / qa-reviewer / spec-reviewer | fresh | passed | N/A | proceed to S99 commit | code-reviewer pass, qa-reviewer pass, and fresh spec-reviewer re-review pass |
| S99-post-observation | PR observation remediation gate | code-reviewer / qa-reviewer | fresh | passed | N/A | proceed to follow-up commit and re-push PR #190 | code-reviewer PASS with no blocking findings; qa-reviewer PASS with no blocking findings |
| S99-post-observation | report evidence spec review gate | spec-reviewer | fresh | passed | N/A | include report evidence in follow-up commit | spec-reviewer PASS with no blocking findings; no overclaim or stale pending gate found |
| S99-post-observation-p1 | PR observation P1 remediation gate | code-reviewer / qa-reviewer | fresh before P2 follow-up | passed | N/A | P2 test-only follow-up applied before commit | code-reviewer PASS with no findings; qa-reviewer PASS with non-blocking P2 pending/queued direct coverage request |
| S99-post-observation-p1-p2 | PR observation P2 coverage remediation gate | code-reviewer / qa-reviewer / spec-reviewer | fresh | passed | N/A | proceed to follow-up commit and re-push PR #190 | code-reviewer PASS; qa-reviewer PASS; spec-reviewer PASS after pending/queued parametrized regression |
| S99-post-observation-p2-failed | PR observation failed-Actions remediation gate | code-reviewer / qa-reviewer / spec-reviewer | fresh | passed | N/A | proceed to follow-up commit and re-push PR #190 | code-reviewer PASS; qa-reviewer PASS after full-suite evidence update; spec-reviewer PASS |
| S99-post-observation-contract | PR observation contract remediation gate | code-reviewer / qa-reviewer | fresh | passed | N/A | ready for spec re-review before commit | code-reviewer PASS; qa-reviewer PASS; dev-coder fix and parent verification recorded |
| S99-post-observation-contract | report evidence spec review gate | spec-reviewer | fresh | passed | N/A | proceed to follow-up commit and re-push PR #190 | spec-reviewer PASS; prior P1 about stale pending code/QA/commit/final paths resolved |
| S99-post-observation-contract-p2 | PR observation contract P2 remediation gate | code-reviewer / qa-reviewer | fresh | passed | N/A | ready for spec re-review before commit | code-reviewer PASS; qa-reviewer PASS; dev-coder fixes and parent verification recorded |
| S99-post-observation-contract-p2 | report evidence spec review gate | spec-reviewer | fresh | passed | N/A | proceed to follow-up commit and re-push PR #190 | spec-reviewer PASS with P2 audit-ledger cleanup applied before commit |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S01 | committed | provider collector + focused tests + S01 report evidence | S01 commit hash recorded in external delivery evidence; row updated by amend | `git status --short` -> clean after commit | N/A | N/A | N/A | code-reviewer pass obtained before commit; amend used only to record post-commit gate state |
| S02 | committed | provider collector + focused tests + S02 report evidence | S02 commit hash recorded in external delivery evidence; row updated by amend | `git status --short` -> clean after commit | N/A | N/A | N/A | code-reviewer pass obtained before commit; amend used only to record post-commit gate state |
| S03 | committed | wrapper scripts + focused tests + S03 report evidence | committed | `git status --short` clean after commit | hash recorded in external delivery evidence; row updated by amend | N/A | N/A | fresh code-reviewer pass obtained before commit |
| S90 | committed | provider/mirror skill docs + dogfooding mirror scripts + S90 report evidence | committed | `git status --short` clean after commit | hash recorded in external delivery evidence; row updated by amend | N/A | N/A | fresh spec-reviewer and code-reviewer pass obtained before commit |
| S99 | committed | final fixture alignment + final report evidence | S99 commit hash recorded in external delivery evidence; row updated by amend | `git status --short` -> clean after commit | N/A | N/A | N/A | code-reviewer, qa-reviewer, and fresh spec-reviewer re-review passed before commit; amend used only to record post-commit gate state |
| S99-post-observation | ready | false-pass follow-up + fixture drift + report evidence | pending commit | pending post-commit check | N/A | N/A | N/A | code-reviewer and qa-reviewer passed before commit |
| S99-post-observation-p1 | ready | current Codex P1 follow-up + P2 coverage follow-up + report evidence | pending commit | pending post-commit check | N/A | N/A | N/A | fresh code-reviewer, qa-reviewer, and spec-reviewer passed before commit |
| S99-post-observation-p2-failed | ready | current Codex P2 failed-Actions follow-up + report evidence | pending commit | pending post-commit check | N/A | N/A | N/A | fresh code-reviewer, qa-reviewer, and spec-reviewer passed before commit |
| S99-post-observation-contract | ready | latest Codex P1/P2 contract follow-up + report evidence | pending commit | pending post-commit check | N/A | N/A | N/A | fresh code-reviewer, qa-reviewer, and spec-reviewer passed before commit |
| S99-post-observation-contract-p2 | ready | latest Codex P2 jobs-list/SHA-resolution follow-up + report evidence | pending commit | pending post-commit check | N/A | N/A | N/A | fresh code-reviewer, qa-reviewer, and spec-reviewer passed before commit |

#### 変更したファイル
- `tests/unit/infra/test_init_update.py` - S99 final integrated verification fixture alignment for Actions-primary fake GitHub responses.
- `spec-dock/active/issue/report.md` - S99 evidence ledger and final gate status.

#### コミット
- `62991a539582de9cbe852c319e37090090b0c99c` `docs(spec-dock): iss-00187の実装委任ハンドオフ証跡を更新`
- `0cb15bfd` `feat(github-pr-observation): Actions 証跡で CI green を判定`
- `2668c90a` `feat(github-pr-observation): Actions CI 状態分類を強化`
- `57cad25d` `feat(github-pr-observation): Actions wrapper の権限判定を整理`
- `e7377989` `docs(github-pr-observation): Actions primary 契約を文書と mirror に反映`
- S99 committed; exact hash recorded in external delivery evidence
- post-observation follow-up pending commit

#### メモ
- S99 initial parent verification failed because legacy fake-gh fixtures did not expose the new Actions-primary endpoint; no provider behavior change was required.
- First PR #190 observation failed on head `fe9daa5955c156216071763246107e9908f6eef1` with provider-tests failures and two Codex P2 findings. The post-observation follow-up fixes the observed false-pass risks before re-pushing.
- Second PR #190 observation passed CI on head `8456d3528d78b64fba96a28f5f3cfc0facca6fb0` but Codex review raised a P1 for running/pending Actions plus supplemental permission denial. The P1 follow-up keeps CI in running/pending and prevents permission-remediation false routing when Actions primary evidence is decisive.
- Third PR #190 observation on head `ad6bada6537ac0a960865396152ed5e8023599b0` exposed Codex P2 for failed Actions plus supplemental permission denial. The failed-Actions follow-up keeps CI failed and prevents token-permission false routing when Actions primary evidence is decisive.
- Fourth PR #190 observation on head `2734987cedb865d6192ceb5ed984977f0dd50137` passed CI but exposed Codex review findings around required regression lane stability, fingerprint evidence, and documented job detail key. The contract follow-up preserves short-timeout test values, adds Actions evidence to fingerprints, and aligns `ci.actions.jobs[]` with design.

---

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| `github-pr-observation` provider/mirror `SKILL.md` | yes | doc-writer | Actions read named as normal CI observation permission; Checks/statuses/status rollup documented as supplemental; provider/mirror `diff -u` no diff; `git diff --check` pass | pass |

### 最終 QA ゲート（Final QA Gate）
| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer | whole issue obligation coverage | already sufficient after S99 fixture alignment; live GitHub API test not required by plan | `uv run pytest tests/unit/infra/test_init_update.py -k "pr_observation or issue_187"` -> `81 passed, 287 deselected`; `git diff --check` -> pass; `./spec-dock/scripts/spec-dock validate` -> pass; provider/mirror `cmp -s` checks for `SKILL.md` and three scripts -> pass | pass |
| qa-reviewer | post-observation contract follow-up obligation coverage | fake-gh coverage is sufficient for `ci.actions.jobs[]`, `jobs_summary`, `jobs_detail`, job-detail fingerprint, and failed-step fingerprint contracts; live GitHub API test not required by plan | targeted fingerprint tests `2 passed`; required lane `90 passed`; full `tests/unit/infra/test_init_update.py` `377 passed`; `git diff --check` -> pass; provider/mirror `cmp` -> pass; `./spec-dock/scripts/spec-dock validate` -> pass | pass |
| qa-reviewer | post-observation contract P2 follow-up obligation coverage | no findings after test-only follow-ups; confirmed missing/object/null Actions jobs payloads and abbreviated SHA resolution negative path are directly covered; live GitHub API test/full suite not required for this blast radius | targeted after final follow-up `28 passed`; required lane after final follow-up `94 passed`; `git diff --check` -> pass; provider/mirror `cmp` -> pass; `spec-dock validate` -> pass | pass |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer | S99 uncommitted diff (`tests/unit/infra/test_init_update.py`, `report.md`) | no findings; confirmed fixture updates do not mask Actions-primary behavior, exact assertions remain strict, and no provider/mirror/source behavior files are touched | 0 | pass |
| code-reviewer | post-observation follow-up diff (`fetch_pr_checks_snapshot.sh`, mirror script, `tests/unit/infra/test_init_update.py`, `report.md`) | no findings; confirmed jobs API collection failure cannot pass, statusCheckRollup non-green blocks pass, and dogfooding meta snapshot update is fixture-only | 0 | pass |
| code-reviewer | post-observation P1 follow-up diff (`fetch_pr_checks_snapshot.sh`, mirror script, `tests/unit/infra/test_init_update.py`, `report.md`) | no findings; confirmed non-terminal Actions predicate excludes jobs failures, zero runs, failed/unknown states, and readable non-green supplemental evidence still wins | 1 | pass |
| code-reviewer | post-observation failed-Actions P2 follow-up diff (`fetch_pr_checks_snapshot.sh`, mirror script, `tests/unit/infra/test_init_update.py`, `report.md`) | no findings; confirmed decisive failed excludes jobs collection failure, unknown, and zero runs while preserving CI failure and failure details | 0 | pass |
| code-reviewer | post-observation contract follow-up diff (`fetch_pr_checks_snapshot.sh`, mirror script, `tests/unit/infra/test_init_update.py`, `design.md`, `report.md`) | no findings; confirmed failed-step detail enters the fingerprint and `ci.actions.jobs[]` / `jobs_summary` / `jobs_detail` contract aligns with implementation | 1 | pass |
| code-reviewer | post-observation contract P2 follow-up diff (`fetch_pr_checks_snapshot.sh`, mirror script, `tests/unit/infra/test_init_update.py`, `design.md`, `report.md`) | no findings; confirmed abbreviated SHA resolution and failure handling, missing/object/null jobs blocking behavior, provider/mirror parity, and design/report consistency | 1 | pass |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report / implementation / tests / docs alignment | initial fail: placeholder rows remained and S99 worker selector was stale; remediation applied; fresh re-review found no blocking findings | 1 | pass |
| spec-reviewer | post-observation P1/P2 follow-up scope and report alignment | no findings; confirmed follow-up is within AC-001/AC-004/AC-005 and report pending rows were valid before pass update | 0 | pass |
| spec-reviewer | post-observation failed-Actions P2 follow-up scope and report alignment | no findings; confirmed failed-Actions follow-up is within AC-001/AC-003/AC-005 and remaining updates were ledger-only | 0 | pass |
| spec-reviewer | post-observation contract follow-up scope and report alignment | no findings; confirmed `ci.actions.jobs[]` / `jobs_summary` / `jobs_detail` contract is reflected in design, implementation, mirror, tests, and report evidence; prior P1 stale pending path resolved | 1 | pass |
| spec-reviewer | post-observation contract P2 follow-up scope and report alignment | PASS with P2 audit-ledger cleanup; confirmed missing/non-list jobs and abbreviated SHA contracts align with requirement/design/plan, and commit gate evidence is sufficient | 1 | pass |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| S99 report ledger ready for commit | `tests/unit/infra/test_init_update.py`; `spec-dock/active/issue/report.md` | PR body / final response / issue closeout evidence | ready |
| post-observation follow-up ledger ready for commit | provider/mirror `fetch_pr_checks_snapshot.sh`; `tests/unit/infra/test_init_update.py`; `spec-dock/active/issue/report.md` | PR #190 re-push / PR observation rerun / final response | ready |
| post-observation P1 follow-up ledger ready for commit | provider/mirror `fetch_pr_checks_snapshot.sh`; `tests/unit/infra/test_init_update.py`; `spec-dock/active/issue/report.md` | PR #190 re-push / PR observation rerun / final response | ready |
| post-observation failed-Actions P2 follow-up ledger ready for commit | provider/mirror `fetch_pr_checks_snapshot.sh`; `tests/unit/infra/test_init_update.py`; `spec-dock/active/issue/report.md` | PR #190 re-push / PR observation rerun / final response | ready |
| post-observation contract follow-up ledger ready for commit | provider/mirror `fetch_pr_checks_snapshot.sh`; `tests/unit/infra/test_init_update.py`; `spec-dock/active/issue/design.md`; `spec-dock/active/issue/report.md` | PR #190 re-push / PR observation rerun / final response | ready |
| post-observation contract P2 follow-up ledger ready for commit | provider/mirror `fetch_pr_checks_snapshot.sh`; `tests/unit/infra/test_init_update.py`; `spec-dock/active/issue/design.md`; `spec-dock/active/issue/report.md` | PR #190 re-push / PR observation rerun / final response | ready |

## 遭遇した問題と解決 (任意)
- 問題: S99 の親 focused pytest で、旧 pr_observation fake-gh fixture が Actions-primary endpoint を返さず、`actions_read` unknown で 14 件失敗した。
  - 解決: dev-coder に `tests/unit/infra/test_init_update.py` のみを委任し、旧 fixture に Actions runs/jobs 応答を追加した。親セッションで正しい S99 lane を再実行し `81 passed, 287 deselected` を確認した。

## 学んだこと (任意)
- Actions-primary collector へ切り替えた後は、新規 issue_187 tests だけでなく、既存 pr_observation fake-gh tests にも primary endpoint の期待状態を明示する必要がある。

## 今後の推奨事項 (任意)
- Future PR observation tests should make the intended primary CI source explicit in each fake-gh fixture so fallback-path tests are not accidentally driven by missing Actions endpoints.

## 省略/例外メモ (必須)
- 該当なし
