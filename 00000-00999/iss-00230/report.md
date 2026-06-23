---
種別: 実装報告書（Issue）
ID: "iss-00230"
タイトル: "Compile Step Assurance Agent Routing And Context Policy"
関連GitHub: ["#230"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00230 Compile Step Assurance Agent Routing And Context Policy — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

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
| D-230-P01 | resolved | test-strategy | orchestrator | `assurance classify` currently defaults unknown risk facts to `standard`, while Epic I04 records strict/deep assurance intent | manually edit `assurance.json`; expand classifier in planning; keep Issue-local plan gates strict | Keep the generated contract valid and enforce strict reviewer / validation obligations through `plan.md`; classifier semantic expansion is not part of this Issue's approved scope. | `assurance.json` is validated by runtime schema and source binding; changing classifier behavior belongs to assurance core, not context routing. | applied | `./spec-dock/scripts/spec-dock assurance classify --stage requirement --format json`; `./spec-dock/scripts/spec-dock assurance verify --format json`; `plan.md` S01/S02/S99 | none |
| D-230-P02 | resolved | scope | spec-reviewer | Planning docs omitted parent I04 invocation observability and full worker-continuation freshness criteria. | keep original narrower contract; adopt full parent I04 criteria | Adopt full parent criteria for invocation event observability and continuation freshness. | Parent Epic I04 explicitly closes E-RQ-016/E-RQ-021 and issue implementation would otherwise pass while missing those obligations. | applied | spec-reviewer finding P1; `requirement.md`; `design.md`; `plan.md` | none |
| D-230-P03 | resolved | scope | spec-reviewer | Issue docs used `system/policies/...` for context routing policy while parent Epic uses `system/assurance/...`. | supersede parent path; align issue path with parent path | Adopt parent Epic path: provider `src/spec_dock/assets/spec_dock/system/assurance/context-routing-policy.json` and schema `src/spec_dock/assets/spec_dock/system/assurance/schemas/context-routing-policy.schema.json`; mirror under `spec-dock/system/assurance/...`. | Policy file location is a shipped scaffold API surface and should not diverge from Epic design during Issue execution. | applied | spec-reviewer finding P1; `design.md`; `plan.md` | none |
| D-230-S01 | resolved | implementation | dev-coder | S01 policy needed concrete per-task defaults not fully enumerated in planning docs. | minimal distinct matrix; strict all-reviewer matrix; defer to S02 | Adopt minimal distinct matrix: docs-only/doc-writer/low/minimal/spec-reviewer; runtime/dev-coder/medium/recent_fork/code-reviewer; migration/dev-coder/high/bounded_packet/code+qa; security/dev-coder/max/bounded_packet/code+qa+spec. | Satisfies AC-001 with proportional obligations and keeps S02 projection deterministic. | applied | `context-routing-policy.json`; `test_context_routing.py` | none |
| D-230-S01-R01 | resolved | implementation | code-reviewer | Unsupported context routing policy versions were accepted despite schema `const` and EC-002 fail-closed requirement. | accept any non-empty version; reject versions other than `context-routing-policy-v1` | Reject unsupported policy versions in `context_routing_policy_from_dict` and cover it with a unit test. | Keeps runtime parser behavior aligned with shipped schema and fail-closed policy. | applied | code-reviewer P1; `uv run pytest tests/unit/domain/test_context_routing.py` -> 4 passed | none |
| D-230-S01-R02 | resolved | implementation | code-reviewer | Bounded return policy accepted supersets such as `raw_shell_transcript`, allowing policy JSON to broaden the return contract. | accept superset; reject any field outside the closed allowlist | Reject unsupported bounded return fields in parser and close the JSON schema allowlist with fixed size / enum / uniqueness. | Preserves S01 bounded return contract and EC-002 fail-closed behavior. | applied | code-reviewer P1; `uv run pytest tests/unit/domain/test_context_routing.py` -> 5 passed | none |
| D-230-S02 | resolved | implementation | dev-coder | S02 needed packet/policy stores connected to `workflow next issue-execution`. | edit bootstrap; inject stores through workflow use case; resolve stores inside `workflow_next` from `store.repo_root` | Inject `ContextPolicyStore` and `ContextPacketStore` from bootstrap through Protocol-shaped parameters on `workflow_next`. | Final structural regression requires application code to depend on contracts, not concrete infra. Bootstrap is the existing composition root for runtime stores. | applied | `application/workflow.py`; `cli/bootstrap.py`; `tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::test_final_api_call_site_and_structural_regression` -> pass | none |
| D-230-S02-R01 | resolved | implementation | orchestrator | Initial `ContextPacketStore` wrote multiple packet files without restoring prior projection set on partial replace failure. | leave as best-effort; add rollback backups like `RunbookStore` | Add backup/restore around packet projection replacement and test partial replace failure. | S02 requires atomic generated projection behavior and no tracked-state pollution. | applied | `tests/unit/infra/test_context_packet_store.py`; `uv run pytest ...` -> 17 passed | none |
| D-230-S02-R02 | resolved | implementation | code-reviewer | RunbookStore projection omitted `step_assurance` / `context_packets` even though CLI stdout included them. | keep stdout-only; persist optional fields in runbook projection | Persist optional context fields in `RunbookStore` JSON / Markdown and test generated `current-runbook` files. | AC-007 requires current Runbook projection to carry routing decision and packet refs. | applied | code-reviewer P1; `tests/cli_runtime/test_workflow_context_routing.py` | none |
| D-230-S02-R03 | resolved | implementation | code-reviewer | Stale role packet files remained after later projections omitted those roles. | leave stale files; remove stale role packet files with backup/restore | Delete role packet files not present in the new write set and preserve previous set on failure. | EC-002 fail-closed must not leave obsolete reviewer packet files available. | applied | code-reviewer P1; `tests/unit/infra/test_context_packet_store.py` | none |
| D-230-S02-R04 | resolved | implementation | code-reviewer | Unselectable step fell back to runtime implementation packet. | keep runtime default; return issue-wide non-invocation default | Return `issue-wide` with no worker/reviewers/invocation events when no uncompleted implementation step can be selected. | EC-003 requires indeterminate selection not to prompt implementation start. | applied | code-reviewer P2; `tests/cli_runtime/test_workflow_context_routing.py` | none |
| D-230-S02-R05 | resolved | implementation | code-reviewer | Packet assembly used default role context contracts instead of loaded valid policy exclusions. | leave default role contracts; pass loaded policy into role context contracts | Apply loaded policy to role packet / invocation event contracts and cover custom reviewer exclusion. | Keeps valid policy changes reflected in generated context packets. | applied | code-reviewer P2; `uv run pytest ...` -> 24 passed | none |
| D-230-S99-R01 | resolved | implementation | final gate | `tests/cli_runtime` failed structural regression because `application/workflow.py` imported concrete infra stores. | keep direct imports; move store construction to bootstrap composition root | Move context policy / packet store construction to `cli/bootstrap.py` and pass stores through application Protocol parameters. | Preserves layered architecture while keeping the same `workflow next` behavior and context packet projection. | applied | first `uv run pytest tests/cli_runtime` -> 1 failed; targeted structural regression -> pass; full rerun -> 669 passed, 76 skipped | none |
| D-230-S99-R02 | resolved | test-strategy | qa-reviewer | Workflow projection path did not pass `ContinuationFacts`, so dirty worktree / revalidation failure could still project `recent_fork`. | keep domain-only coverage; build current continuation facts in workflow path | Build continuation facts in `workflow_next` from source refs, current HEAD, worktree cleanliness, and file revalidation, and persist continuation state in context packet projection. | AC-002/AC-006/EC-004 are observable workflow obligations, not only domain-helper obligations. | applied | qa-reviewer P1; `tests/cli_runtime/test_workflow_context_routing.py::test_workflow_next_dirty_worktree_forces_bounded_continuation`; focused `uv run pytest ...` -> 34 passed; full `uv run pytest tests/cli_runtime` -> 672 passed, 76 skipped | none |
| D-230-S99-R03 | resolved | implementation | code-reviewer | Step selection skipped S01 when report still contained scaffold text or failed/blocked S01 logs. | continue broad regex; require completed session evidence | Replace broad `Step:` regex with session-block completion detection that requires pass / committed / approved-no-op evidence and excludes fail / blocked blocks. | Maintains ordered execution and avoids scaffold/example text driving worker routing. | applied | code-reviewer P1; `tests/cli_runtime/test_workflow_context_routing.py::test_workflow_next_does_not_skip_step_from_scaffold_report_text`; focused `uv run pytest ...` -> 34 passed; full `uv run pytest tests/cli_runtime` -> 672 passed, 76 skipped | none |
| D-230-S99-R04 | resolved | implementation | code-reviewer | Policy parser accepted worker roles in `reviewers`, letting malformed policy produce worker packets where clean-room reviewer context was required. | rely on schema only; enforce reviewer role set in parser | Reject non-reviewer roles in policy `reviewers` during runtime parsing. | Runtime parser must fail closed even when policy JSON bypasses schema validation. | applied | code-reviewer P1; `tests/unit/domain/test_context_routing.py::test_policy_parser_rejects_non_reviewer_roles_in_reviewers`; focused `uv run pytest ...` -> 34 passed; full `uv run pytest tests/unit` -> 818 passed | none |
| D-230-S99-R05 | resolved | test-strategy | qa-reviewer | Observable workflow tests covered runtime default only, while plan-derived docs/migration/security routing could regress. | keep domain matrix only; add workflow-level task-kind coverage | Add CLI coverage for docs-only, migration, and security-sensitive plan markers. | AC-001 requires observable Runbook routing, not only pure domain matrix behavior. | applied | qa-reviewer P2; `tests/cli_runtime/test_workflow_context_routing.py::test_workflow_next_routes_plan_derived_task_kinds`; focused `uv run pytest ...` -> 34 passed; full `uv run pytest tests/cli_runtime` -> 672 passed, 76 skipped | none |
| D-230-S99-R06 | resolved | implementation | code-reviewer re-review | Completion parser treated any incidental `fail` text in a session block as incomplete, including Red evidence and fail-closed wording. | block-level string exclusion; result-cell specific completion | Detect completed steps from table rows whose first cell is the step id and whose result cell is `pass` / `passed` / `committed` / `approved-no-op`, while explicit `fail` / `failed` / `blocked` result cells remain incomplete. | Step execution ordering must be based on closure evidence, not incidental wording. | applied | code-reviewer re-review P1; happy path report fixture includes `fail-closed` wording and still selects S02; failed result row still selects S01; focused `uv run pytest ...` -> 16 passed | none |
| D-230-S99-R07 | resolved | implementation | code-reviewer re-review | Continuation git probes called `git` directly from `application/workflow.py`. | keep direct subprocess; inject continuation probe from bootstrap | Move current HEAD / status probes behind a `ContinuationProbeLike` Protocol implemented at bootstrap through `infra/git_cli`. | Preserves application-layer dependency boundaries and keeps external process access in infra. | applied | code-reviewer re-review P2; `tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::test_final_api_call_site_and_structural_regression` -> pass; `make lint` -> pass | none |
| D-230-S99-R08 | resolved | implementation | code-reviewer second re-review | Completion parser still accepted Red-phase `pass` rows as step completion evidence. | accept any table pass row; restrict accepted rows to closure / commit sections | Only inspect step result rows inside `ステップ契約の完了証跡` / `Step Contract Closure` / step commit sections. | Red / Green / Refactor evidence is progress evidence, not step completion evidence. | applied | code-reviewer second re-review P1; `test_workflow_next_does_not_skip_step_from_red_phase_pass_only`; focused `uv run pytest tests/cli_runtime/test_workflow_context_routing.py tests/unit/domain/test_context_routing.py` -> 16 passed; `make lint` -> pass | none |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-230-P01 | adopted | parent Epic design/plan and ADR discussions | issue planning artifacts | Epic I04 already fixes the scope for step assurance, context routing, clean-room reviewer packets, and bounded return contracts; the issue docs adopt that scope without adding PR review semantics. | `spec-dock/active/epic/design.md`; `spec-dock/active/epic/plan.md`; `requirement.md`; `design.md`; `plan.md` | spec-review |
| EAL-230-S01 | adopted | dev-coder S01 implementation note | S01 runtime domain / policy / tests | Worker implemented only the approved S01 file set and returned material matrix defaults for orchestrator adoption. The matrix is the smallest distinct docs/runtime/migration/security routing set that satisfies AC-001 while preserving clean-room reviewer obligations. | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/context_routing.py`; `tests/unit/domain/test_context_routing.py`; `uv run pytest tests/unit/domain/test_context_routing.py` | code-review |
| EAL-230-S02 | adopted | dev-coder S02 implementation note | S02 workflow / packet projection / CLI tests | Worker connected S01 domain decisions to Runbook JSON/Markdown and ignored context packet projection, then orchestrator added atomic rollback coverage for projection writes. | `tests/cli_runtime/test_workflow_context_routing.py`; `tests/unit/infra/test_context_packet_store.py`; `uv run pytest tests/cli_runtime/test_workflow_context_routing.py tests/unit/infra/test_context_packet_store.py tests/cli_runtime/test_workflow.py` | code-review |
| EAL-230-S99 | adopted | final gate command evidence | final implementation / report ledger | Full lint and CLI runtime verification found and then cleared one application-layer structural violation; final evidence is adopted as issue closure evidence. | `make lint`; `uv run pytest tests/cli_runtime`; `uv run pytest tests/unit`; `./spec-dock/scripts/spec-dock validate`; parity diffs | final review |
| EAL-230-RR01 | adopted | qa-reviewer / code-reviewer / spec-reviewer final findings | final fixes / report ledger | Fresh final reviews identified workflow continuation, completed-step evidence, reviewer-role parser, task-kind coverage, and final ledger gaps; implementation findings were fixed and report findings are tracked for re-review. | D-230-S99-R02 through D-230-S99-R08; final gate rows | re-review |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-230-P01 | Step-level resource allocation and context routing are captured in AC-001 through AC-011 and S01/S02/S90/S99. | Classifier precision mismatch is recorded as Issue-local test-strategy decision, not implemented as extra scope; policy paths now match parent Epic. | low | spec-review pass with P2 traceability fixes applied locally |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement / design / plan | Inspected active issue scaffold, parent Epic I04 scope, current `assurance/workflow/runbook` runtime modules, generated planning Runbook, and spec-reviewer findings. | P1 findings resolved; spec-reviewer re-review passed with P2 traceability findings, then AC-011/S02 and tc-230-009 final closure references were corrected. | adopted | passed | no | promote to implementation-ready |

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
| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | 未使用（not used） | なし（[]） | 未実行（not_run） | 手動 authoring | 該当なし | なし（none） | 該当なし | 委任ドラフト昇格なし |

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
- Step-level task kind / risk / assurance authority に基づく worker routing policy、clean-room reviewer / consultant context contract、bounded return contract を provider runtime に追加した。
- `workflow next issue-execution` が routing decision、context packet refs、invocation event、continuation revalidation result を Runbook JSON / Markdown と ignored generated packet stateへ投影するようにした。
- Provider runtime / assurance policy source は dogfooding mirror へ同期し、final reviewer findings に基づく regression tests と full regression evidence を追加した。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-06-23 S01）

#### 対象
- Step: S01
- AC/EC: AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, EC-002, EC-004
- 計画上の出典:
  - `plan.md` 実装ステップ S01
  - closure ids: tc-230-001, tc-230-002, tc-230-003

#### 実施内容
- `dev-coder` に S01 implementation を委任し、context routing policy source、domain model、unit tests を追加した。
- Orchestrator が worker の matrix decision を採用し、targeted verification を再実行した。

#### 実行コマンド / 結果
```bash
uv run pytest tests/unit/domain/test_context_routing.py
# 3 passed in 0.01s

uv run ruff check src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/context_routing.py tests/unit/domain/test_context_routing.py
# All checks passed!
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ | フェーズ | 計画した証跡要件 | 観測した証跡 | 証跡手段 | 結果 | メモ |
|---|---|---|---|---|---|---|
| S01 | Red | red-required | 実装前は `tests/unit/domain/test_context_routing.py` が存在せず pytest exit 4 | worker evidence | pass | file missing による期待どおりの Red |
| S01 | Green | targeted unit tests | initial `3 passed`; after code-reviewer P1 fixes `5 passed in 0.02s` | `uv run pytest tests/unit/domain/test_context_routing.py` | pass | tc-230-001〜003 plus unsupported policy version / bounded return superset regressions |
| S01 | Refactor | targeted lint / domain boundary | ruff pass; imports are `__future__`, `dataclasses`, `enum`, `typing` only | `uv run ruff check ...`; AST import inspection | pass | filesystem / CLI import なし |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ | クロージャID | 計画上の close 条件 | 観測した証跡 | 結果 | メモ |
|---|---|---|---|---|---|
| S01 | tc-230-001 | routing matrix が task kind ごとに異なる | docs/runtime/migration/security expected tuple tests | pass | policy JSON と domain parser で検証 |
| S01 | tc-230-002 | continuation freshness / fallback | same context allowed、変更/revalidation failure は bounded_packet fallback | pass | source binding/revision/goal/scope/paths/risk/head/worktree/files |
| S01 | tc-230-003 | clean-room exclusions | reviewer/consultant clean_room、forbidden source exclusion、bounded return contract | pass | consultant first-pass exclusions も検証 |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ | ゲート名 | レビュアーロール | 鮮度 | 状態 | リスク受容 | 昇格 / 完了判断 | メモ |
|---|---|---|---|---|---|---|---|
| S01 | step reviewer | code-reviewer | fresh | passed | no | proceed to commit | P1 unsupported policy version and P1 bounded return superset fixed; no remaining P0/P1 findings |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ | 委任ロール | 委任 worker 要約 | 変更ファイル | 実行 tests または docs-only 検証 | レビュアー判定 | 未解決リスク | 親統合判断 |
|---|---|---|---|---|---|---|---|
| S01 | dev-coder | context routing matrix、continuation freshness、clean-room exclusions、bounded return contract を実装 | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/context_routing.py`; `src/spec_dock/assets/spec_dock/system/assurance/context-routing-policy.json`; `src/spec_dock/assets/spec_dock/system/assurance/schemas/context-routing-policy.schema.json`; `tests/unit/domain/test_context_routing.py` | `uv run pytest tests/unit/domain/test_context_routing.py` -> pass; `uv run ruff check ...` -> pass | passed; final reviewer findings resolved in D-230-S99-R04 | none; projection integration completed by S02 | accepted |

### セッションログ（2026-06-23 S02）

#### 対象
- Step: S02
- AC/EC: AC-007, AC-008, AC-009, AC-010, AC-011, EC-001, EC-002, EC-003
- 計画上の出典:
  - `plan.md` 実装ステップ S02
  - closure ids: tc-230-004, tc-230-005, tc-230-006, tc-230-007, tc-230-008

#### 実施内容
- `dev-coder` に S02 implementation を委任し、S01 の context routing decision を `workflow next issue-execution` の optional `step_assurance` / `context_packets` へ接続した。
- Context packet projection を `spec-dock/.agent/context-packets/` 配下の ignored generated state として書き出す store を追加した。
- Orchestrator が atomic projection requirement に合わせて packet store の backup / restore を補強した。

#### 実行コマンド / 結果
```bash
uv run pytest tests/cli_runtime/test_workflow_context_routing.py tests/unit/infra/test_context_packet_store.py tests/cli_runtime/test_workflow.py
# 17 passed in 15.54s

uv run ruff check src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/context_packets.py src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/runbook.py src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/context_policy_store.py src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/context_packet_store.py src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/workflow.py tests/cli_runtime/test_workflow_context_routing.py tests/unit/infra/test_context_packet_store.py
# All checks passed!
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ | フェーズ | 計画した証跡要件 | 観測した証跡 | 証跡手段 | 結果 | メモ |
|---|---|---|---|---|---|---|
| S02 | Red | red-required | 実装前は provider runtime Runbook に `step_assurance` / `context_packets` がなく、new CLI test file も存在しなかった | worker evidence | pass | pytest exit 4 / missing field 相当 |
| S02 | Green | targeted CLI / infra tests | initial `17 passed`; after code-reviewer fixes `24 passed in 17.78s` | `uv run pytest tests/cli_runtime/test_workflow_context_routing.py tests/unit/infra/test_context_packet_store.py tests/unit/infra/test_runbook_store.py tests/cli_runtime/test_workflow.py` | pass | tc-230-004〜008 plus projection persistence / stale packet / issue-wide default / loaded policy exclusion regressions |
| S02 | Refactor | targeted lint / atomicity guard | ruff pass; packet store partial replace rollback test added | `uv run ruff check ...`; unit test | pass | generated state remains ignored |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ | クロージャID | 計画上の close 条件 | 観測した証跡 | 結果 | メモ |
|---|---|---|---|---|---|
| S02 | tc-230-004 | Runbook JSON / Markdown が step assurance と packet refs を返す | CLI runtime JSON / Markdown tests | pass | existing top-level fields preserved |
| S02 | tc-230-005 | packet projection が ignored state に書かれ refs hash を持つ | CLI git-clean test; infra hash / symlink / rollback tests | pass | `.agent/context-packets/` |
| S02 | tc-230-006 | missing / invalid assurance precedence | missing assurance CLI test | pass | step fields omitted |
| S02 | tc-230-007 | invalid policy degrade / fail-closed | invalid JSON policy CLI test | pass | worker bounded_packet, reviewer missing_reason |
| S02 | tc-230-008 | invocation observability | role / effort / context / policy / packet hash / source hashes / fork turn / include-exclude / refs assertions | pass | machine-readable event |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ | ゲート名 | レビュアーロール | 鮮度 | 状態 | リスク受容 | 昇格 / 完了判断 | メモ |
|---|---|---|---|---|---|---|---|
| S02 | step reviewer | code-reviewer | fresh | passed | no | proceed to commit | P1 findings fixed; P2 loaded policy exclusion fixed locally after reviewer pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ | 委任ロール | 委任 worker 要約 | 変更ファイル | 実行 tests または docs-only 検証 | レビュアー判定 | 未解決リスク | 親統合判断 |
|---|---|---|---|---|---|---|---|
| S02 | dev-coder | workflow next に step assurance / context packet projection / invocation event を接続 | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/context_packets.py`; `application/workflow.py`; `domain/runbook.py`; `infra/context_policy_store.py`; `infra/context_packet_store.py`; `presentation/workflow.py`; `tests/cli_runtime/test_workflow_context_routing.py`; `tests/unit/infra/test_context_packet_store.py` | `uv run pytest ...` -> pass; `uv run ruff check ...` -> pass | passed; final reviewer findings resolved in D-230-S99-R02 / R03 / R05 | none; dogfooding mirror sync completed by S90 and re-synced after S99 fixes | accepted |

### セッションログ（2026-06-23 S90）

#### 対象
- Step: S90
- AC/EC: docs impact / mirror parity
- 計画上の出典:
  - `plan.md` ドキュメント影響の解消ステップ S90
  - closure id: tc-230-009

#### 実施内容
- Provider runtime / assurance policy source を dogfooding mirror へ同期した。
- Local dogfooding runtime で `workflow next issue-execution --format json` が `step_assurance` / `context_packets` を返すことを確認した。

#### 実行コマンド / 結果
```bash
diff -ru -x __pycache__ src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime spec-dock/scripts/spec_dock_runtime
# pass

diff -ru src/spec_dock/assets/spec_dock/system/assurance spec-dock/system/assurance
# pass

./spec-dock/scripts/spec-dock workflow next issue-execution --format json
# state=ready; step_assurance and context_packets present
```

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ | クロージャID | 計画上の close 条件 | 観測した証跡 | 結果 | メモ |
|---|---|---|---|---|---|
| S90 | tc-230-009 | provider source と dogfooding mirror が一致する | runtime parity diff pass; assurance policy parity diff pass | pass | local projection 出力も確認 |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ | ゲート名 | レビュアーロール | 鮮度 | 状態 | リスク受容 | 昇格 / 完了判断 | メモ |
|---|---|---|---|---|---|---|---|
| S90 | docs impact reviewer | spec-reviewer | fresh | passed | no | proceed to commit | P2 final gate placeholders deferred to S99 |

### セッションログ（2026-06-23 S99）

#### 対象
- Step: S99
- AC/EC: full issue closure / final verification / reviewer readiness

#### 実施内容
- `make lint` で formatter と mypy の最終ゲートを実行し、初回 failure を解消した。
- `tests/cli_runtime` の初回全体実行で structural regression failure を検出し、context policy / packet store の生成責務を bootstrap composition root へ移した。
- Provider runtime と dogfooding runtime mirror を再同期し、parity diff、targeted tests、full CLI runtime tests を再実行した。

#### 実行コマンド / 結果
```bash
make lint
# initial: ruff format check failed on 7 files; mypy failed in application/context_packets.py
# after fixes: ruff check pass; ruff format check pass; mypy pass

uv run pytest tests/unit
# after reviewer fixes: 818 passed in 308.99s

uv run pytest tests/cli_runtime
# initial: 1 failed, 668 passed, 76 skipped
# failure: application/workflow.py concrete infra imports violated S11 structural rule
# after DI and reviewer fixes: 672 passed, 76 skipped in 502.21s

uv run pytest tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::test_final_api_call_site_and_structural_regression tests/unit/infra/test_context_packet_store.py tests/unit/infra/test_runbook_store.py tests/cli_runtime/test_workflow_context_routing.py tests/cli_runtime/test_workflow.py
# after reviewer fixes: 34 passed in 25.57s

diff -ru -x __pycache__ src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime spec-dock/scripts/spec_dock_runtime
# pass

diff -ru src/spec_dock/assets/spec_dock/system/assurance spec-dock/system/assurance
# pass

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=148

./spec-dock/scripts/spec-dock workflow next issue-execution --format json
# state=ready; step_assurance and context_packets present
```

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ | 発見されたテスト / リスク | 起票元 | 実施した対応 | クロージャID / 新規ID | 計画修正要否 | 証跡 |
|---|---|---|---|---|---|---|
| S99 | application layer must not import concrete infra context stores | final CLI runtime suite | moved store construction to bootstrap and injected Protocol-shaped dependencies | D-230-S99-R01 | no | `tests/cli_runtime/test_runtime_shell_s11.py::TestRuntimeShellS11::test_final_api_call_site_and_structural_regression` -> pass |
| S99 | workflow path must revalidate continuation facts before `recent_fork` | qa-reviewer | added workflow-level continuation facts and dirty worktree CLI test | D-230-S99-R02 | no | `test_workflow_next_dirty_worktree_forces_bounded_continuation` -> pass |
| S99 | step selection must not treat scaffold or failed logs as completed | code-reviewer | changed completion detection to pass/commit evidence within session blocks | D-230-S99-R03 | no | `test_workflow_next_does_not_skip_step_from_scaffold_report_text` -> pass |
| S99 | malformed policy reviewers must fail closed when non-reviewer roles appear | code-reviewer | rejected non-reviewer roles in parser and added unit regression | D-230-S99-R04 | no | `test_policy_parser_rejects_non_reviewer_roles_in_reviewers` -> pass |
| S99 | plan-derived docs/migration/security routing needs observable workflow coverage | qa-reviewer | added parameterized CLI routing coverage | D-230-S99-R05 | no | `test_workflow_next_routes_plan_derived_task_kinds` -> pass |
| S99 | completed-step parser must ignore incidental `fail` text and use result-specific evidence | code-reviewer re-review | changed parser to inspect step table result cells | D-230-S99-R06 | no | focused `uv run pytest ...` -> 16 passed |
| S99 | continuation git probes must stay behind infra/bootstrap boundary | code-reviewer re-review | injected `ContinuationProbeLike` from bootstrap and moved subprocess access to `infra/git_cli` | D-230-S99-R07 | no | structural regression -> pass; `make lint` -> pass |
| S99 | completed-step parser must not accept Red-phase pass rows as closure | code-reviewer second re-review | limited completion parser to Step Contract Closure / Step Commit sections | D-230-S99-R08 | no | `test_workflow_next_does_not_skip_step_from_red_phase_pass_only` -> pass |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ | クロージャID | 計画上の close 条件 | 観測した証跡 | 結果 | メモ |
|---|---|---|---|---|---|
| S99 | final-gate | lint / unit / CLI runtime / validate / mirror parity | `make lint`; `uv run pytest tests/unit`; `uv run pytest tests/cli_runtime`; `./spec-dock/scripts/spec-dock validate`; parity diffs | pass | initial failures fixed and rerun green |

---

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| provider runtime mirror | yes | orchestrator | `diff -ru -x __pycache__ src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime spec-dock/scripts/spec_dock_runtime` -> pass | pass |
| assurance policy mirror | yes | orchestrator | `diff -ru src/spec_dock/assets/spec_dock/system/assurance spec-dock/system/assurance` -> pass | pass |
| README / workflow / skill / migration notes | no | N/A | S02 changes add runtime projection and shipped policy source without changing human-facing workflow text beyond existing issue docs; no separate persistent docs update required for this slice. | pass |

### 最終 QA ゲート（Final QA Gate）
| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer | whole issue obligation coverage | added workflow-level continuation and task-kind routing coverage | initial review failed on P1 continuation coverage and P2 task-kind coverage; fixes recorded in D-230-S99-R02 / R05; focused `uv run pytest ...` -> 34 passed; full `uv run pytest tests/unit` -> 818 passed; full `uv run pytest tests/cli_runtime` -> 672 passed, 76 skipped; re-review passed | pass |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer | issue-wide integrated diff | initial review failed on P1 completed-step evidence and P1 non-reviewer role policy parser; first re-review found result-specific completion P1 and continuation probe layering P2; second re-review found Red-phase pass completion P1; fixes recorded in D-230-S99-R03 / R04 / R06 / R07 / R08; focused `uv run pytest ...` -> 16 passed; `make lint` -> pass; third re-review passed | 3 | pass |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report / implementation / tests / docs alignment | initial review failed on final gate placeholders and stale delegated rows; placeholders replaced with concrete pending/pass evidence and delegated rows updated; re-review passed with P2 front matter status fix applied | 1 | pass |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| final reviewer pass recorded | S99 reviewer-finding fixes, mirror sync, tests, report ledger | final response / Epic PR body after issue finish | ready for final commit |

## 遭遇した問題と解決 (任意)
- 問題: final reviewer / full regression で application layer の infra 直参照、workflow continuation 未接続、step 完了判定の scaffold 誤検出、policy reviewer role の runtime parser 漏れが見つかった。
  - 解決: bootstrap DI、workflow-level continuation facts、session-block completion detection、reviewer role validation、追加 CLI / unit regression tests を適用した。

## 学んだこと (任意)
- Domain helper のみで満たしたように見える契約でも、Runbook / CLI projection の observable path で検証しないと agent routing contract の退行を見落とす。

## 今後の推奨事項 (任意)
- 後続 issue では workflow output に追加する agent-facing metadata について、domain unit と CLI runtime の両方で少なくとも 1 件ずつ regression を置く。

## 省略/例外メモ (必須)
- 該当なし
