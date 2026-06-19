---
種別: 実装計画書（Issue）
ID: "iss-00207"
タイトル: "Fix dependency projections for node level blockers"
関連GitHub: ["#207"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-18"
依存: ["requirement.md", "design.md"]
親: ["epic-00059", "init-local-00003"]
---

# iss-00207 Fix dependency projections for node level blockers — 実装計画（実行契約）

## この計画で満たす要件ID
- AC: AC-001, AC-002, AC-003, AC-004, AC-005, AC-006
- EC: EC-001, EC-002, EC-003, EC-004
- 制約:
  - `.meta.json.depends_on` storage format は変更しない。
  - provider-side source of truth は `src/spec_dock/assets/spec_dock/...`。
  - legacy monolithic `app.py` は実装 source of truth として扱わない。
  - `deps-raw.puml` は state color を持っても readiness authority ではない。
  - 各 implementation step は one-step / one-review / one-commit boundary とする。

## 依存関係から導く実装順序
- S01 Contract / Topology:
  - 依存: reviewed requirement/design
  - unblock: S02
  - 対象: `infra/contracts.py`, `infra/deps_reader.py`, `domain/models.py`
- S02 Domain Evaluation:
  - 依存: S01 commit
  - unblock: S03, S04
  - 対象: `domain/models.py`, `domain/deps.py`
- S03 Command Guards:
  - 依存: S02 commit
  - unblock: S04 command parity
  - 対象: `application/check_deps.py`, `application/set_active.py`, `application/issue_lifecycle.py`
  - status context owner: application layer で GitHub snapshot / local cache / descendant status を集め、domain evaluation へ渡す。
- S04 Sync / Presentation:
  - 依存: S02/S03 commits
  - unblock: S90
  - 対象: `application/sync_state.py`, `application/contracts.py`, `presentation/json_state.py`, `presentation/puml.py`
  - status context owner: S03 と同じ high-level status context builder を sync state に通し、presentation は渡された state だけを描画する。
- S90 Docs / Dogfooding Mirror:
  - 依存: S04 commit
  - unblock: S99
  - 対象: provider docs and intentional dogfooding mirror inspection/update
- S99 Final Quality Gate:
  - 依存: S01-S90 complete
  - 対象: verification, reviewer gates, report closure evidence

## ステップ一覧
- S01: topology loader が raw node dependency context と compiled issue dependency を両方保持する。
- S02: domain evaluation が issue blockers / node blockers / satisfied dependencies / unknown fail-closed を算出する。
- S03: `deps check` / `active set` / `issue start` が同じ readiness evaluation で node-blocked issue を止める。
- S04: `sync` が `deps-issues` v2 と high-level state 付き `deps-raw` を生成する。
- S90: docs と dogfooding mirror の authority 境界を揃える。
- S99: 全 closure evidence、tests、reviewer gate、diff guard を閉じる。

## 要件 ↔ ステップ対応
- AC-001 -> S02, S03
- AC-002 -> S02, S04
- AC-003 -> S01, S02
- AC-004 -> S04
- AC-005 -> S04
- AC-006 -> S90, S99
- EC-001 -> S02, S03, S04
- EC-002 -> S02, S04
- EC-003 -> S01, S04, S99
- EC-004 -> S90, S99

## 仕様固定クロージャ索引（Spec-Locked Closure Index）
| ID | Step | Type | Spec link | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル | クロージャ証跡 |
|---|---|---|---|---|---|---|---|---|---|
| cl-ac-001 | S02/S03 | acceptance | AC-001 | empty open initiative/epic dependency blocks readiness and start guards | `deps check`, `active set`, `issue start` on issue depending on empty open high-level node | false-ready active/start | yes | red-required | domain + CLI tests |
| cl-ac-002 | S02/S04 | acceptance | AC-002 | empty done/closed high-level dependency is satisfied, not blocking | domain/CLI/sync fixture with closed empty high-level node | over-blocking satisfied target | yes | red-required | domain + sync tests |
| cl-ac-003 | S01/S02 | regression | AC-003 | non-empty high-level dependency still expands to child issue blockers | issue depends on epic with open/done child issues | shorthand expansion regression | yes | covered-existing + red-required if field changes | topology/domain tests |
| cl-ac-004 | S04 | acceptance | AC-004 | `deps-issues` preserves blocker/satisfied context beyond todo issue set | sync-generated `.agent/deps-issues.json` and `deps-issues.puml` | lossy projection | yes | red-required | sync/presentation tests |
| cl-ac-005 | S04 | acceptance | AC-005 | `deps-raw.puml` shows high-level participant state from payload | raw direct edge involving initiative/epic | ambiguous raw participants | yes | red-required | presentation tests |
| cl-ac-006 | S90/S99 | docs | AC-006 | docs and tests fix the new contract | provider docs, mirror docs, regression suite | undocumented contract drift | yes | inspect-only + command | docs diff + final review |
| cl-ec-001 | S02/S03/S04 | edge | EC-001 | unknown empty high-level target blocks with unknown reason | high-level target with no authoritative state | fail-open unknown | yes | red-required | domain/CLI/sync tests |
| cl-ec-002 | S02/S04 | edge | EC-002 | done child-only dependency does not block but remains visible | high-level target with all child issues done | done blocker resurrection / invisible context | yes | red-required | domain/sync tests |
| cl-ec-003 | S01/S04/S99 | edge | EC-003 | raw node-level cycles fail before readiness projection and do not render stale authority | raw graph cycle fixture | cycle hidden by projection | yes | covered-existing + red-required if touched | cycle + disabled artifact tests |
| cl-ec-004 | S90/S99 | docs | EC-004 | docs/labels keep `deps-raw` as visual/debug, not readiness authority | provider docs and artifact wording | authority confusion | yes | inspect-only | docs/spec review |

## 実行ルール（全ステップ共通）
- Main orchestrator は implementation source/test/docs を直接変更せず、step ごとに `dev-coder` または `doc-writer` へ委任する。
- Worker は allowed paths だけを変更し、changed files / verification / unresolved risks / report evidence を返す。
- 各 step は reviewer pass 後に commit する。P1/P0 は修正して fresh re-review、P2 は blocking かを main orchestrator が判定して記録する。
- 新しい仕様解釈、未計画 path、closure 追加、schema 変更が必要になった場合は report だけで吸収せず、plan amendment と fresh review に戻す。
- 各 step の共通 required output:
  - changed files
  - implemented behavior summary
  - red / characterization evidence
  - green verification command and result
  - unresolved risks
  - report ledger note for Step Contract Closure / Test Contract Closure / Closure Coverage / Delegated Worker Evidence / Reviewer Gate Status / Step Commit Gate
- 各 step の共通 step gate:
  - worker returns required output
  - main orchestrator reviews diff against allowed paths
  - assigned reviewer returns `review_status: pass`
  - step is committed or explicitly recorded as approved no-op

## 実装ステップ

### S01 — Contract / Topology Facts
- 振る舞いの目標:
  - `load_issue_depends_on_map()` が issue-level expansion と lossless raw node dependency context を返す。
- allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/contracts.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/deps_reader.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/models.py`
  - `tests/unit/infra/**`, `tests/unit/domain/test_runtime_domain_s03.py`
- forbidden changes:
  - storage format change, empty high-level validation error, legacy `app.py`, command/presentation behavior.
- delegation contract:
  - role: `dev-coder`
  - inputs: `requirement.md`, `design.md`, `plan.md`, target files above.
  - acceptance criteria: `cl-ac-003` and partial `cl-ec-003` close; raw node context exists for S02; existing child expansion remains intact.
  - required verification: `uv run pytest tests/unit/domain/test_runtime_domain_s03.py tests/cli_runtime/test_sync.py -k "empty or expands or effective_deps or cycle"`
  - output required: common required output plus exact topology fields added and any compatibility notes for existing callers.
  - reviewer focus: `code-reviewer` checks compatibility, deterministic ordering, raw-vs-compiled separation, no readiness decision in infra.
  - stop: `DepsTopologyLoadResult.issue_depends_on_map` compatibility cannot be preserved, or storage change appears required.
- 具体テストケース一覧:
  - `tc-s01-001` characterization: empty epic dependency retains topology context
    - 前提: `iss-00301` depends on empty `epic-00202`.
    - 操作: call reader/topology public path.
    - 期待結果: compiled map for `iss-00301` is empty, warning includes `deps_ref_expanded_to_empty`, and new context records `iss-00301 -> epic-00202`.
    - 失敗検出: context absent, so S02 cannot distinguish empty open from empty done.
    - 検証方法: focused unit test, red before implementation.
    - 関連 closure id: `cl-ac-001`, `cl-ec-001`
  - `tc-s01-002` regression: non-empty epic keeps child expansion
    - 前提: `iss-00301` depends on `epic-00202` with child issues `iss-00401`, `iss-00402`.
    - 操作: load topology.
    - 期待結果: compiled map contains both child issue ids and raw context records the epic edge.
    - 失敗検出: child expansion disappears or duplicates.
    - 検証方法: unit/CLI characterization.
    - 関連 closure id: `cl-ac-003`
  - `tc-s01-003` regression: raw node cycle remains fail-closed
    - 前提: raw direct dependencies create a cycle.
    - 操作: run raw dependency graph validation through existing path.
    - 期待結果: failure occurs before readiness projection.
    - 失敗検出: cycle is warning-only or renders as ready graph.
    - 検証方法: existing cycle test plus assertion if map shape changes.
    - 関連 closure id: `cl-ec-003`
- report evidence destination:
  - Step Contract Closure, Test Contract Closure, Closure Coverage, Delegated Worker Evidence, Reviewer Gate Status, Step Commit Gate.
- step closure contract:
  - close condition: S01 tests pass, reader exposes raw context without changing storage semantics, and reviewer pass is recorded.
  - commit gate: commit only S01 allowed paths after reviewer pass.

### S02 — Domain Readiness Evaluation
- 振る舞いの目標:
  - `domain/deps.py` が issue blockers、node blockers、satisfied dependencies、unknown fail-closed を算出する。
- allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/models.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py`
  - `tests/unit/domain/test_runtime_domain_s03.py`, `tests/unit/domain/test_deps.py`
- forbidden changes:
  - GitHub I/O in domain, renderer-side readiness computation, removal of existing `DepsEvaluation` fields.
- delegation contract:
  - role: `dev-coder`
  - inputs: `requirement.md`, `design.md`, `plan.md`, S01 changed contracts, target files above.
  - acceptance criteria: `cl-ac-001`, `cl-ac-002`, `cl-ac-003`, `cl-ec-001`, `cl-ec-002` close at domain level.
  - required verification: `uv run pytest tests/unit/domain/test_runtime_domain_s03.py tests/unit/domain/test_deps.py`
  - output required: common required output plus model field list and status-context input shape expected from S03/S04.
  - reviewer focus: `code-reviewer` checks fail-closed unknown, typed fields, `blockers` compatibility, no GitHub I/O in domain.
  - stop: high-level status priority cannot be represented with explicit status context, or `blockers` compatibility must change beyond design.
- status fixture/source contract:
  - S02 tests inject explicit high-level status context directly into domain evaluation.
  - Domain does not fetch GitHub/cache itself.
  - Fixtures must cover `state=open/source=github`, `state=closed/source=github`, `state=unknown/source=none`, and descendant-derived done/open.
- 具体テストケース一覧:
  - `tc-s02-001` acceptance: empty open epic blocks
    - 前提: open `iss-00301` directly depends on empty `epic-00202`; injected high-level status is `state=open`, `source=github`.
    - 操作: evaluate readiness with topology context.
    - 期待結果: `ready=false`, `guard_reason="blocked"`, `blockers` includes `epic-00202`, `node_blockers.reason=="empty_open"`, `issue_blockers==[]`.
    - 失敗検出: target remains ready or blocker is warning-only.
    - 検証方法: red-first domain test.
    - 関連 closure id: `cl-ac-001`
  - `tc-s02-002` acceptance: empty closed epic is satisfied
    - 前提: `iss-00301` depends on empty `epic-00202`; injected high-level status is `state=closed`, `source=github`.
    - 操作: evaluate readiness.
    - 期待結果: `ready=true`, no blocker for `epic-00202`, `satisfied_dependencies` records raw direct dependency.
    - 失敗検出: closed high-level target blocks or disappears.
    - 検証方法: red-first domain test.
    - 関連 closure id: `cl-ac-002`
  - `tc-s02-003` edge: empty unknown epic fails closed
    - 前提: high-level target has no GitHub/cache/descendant state; injected high-level status is `state=unknown`, `source=none`.
    - 操作: evaluate readiness.
    - 期待結果: `ready=false`, `guard_reason="unknown"`, `node_blockers.reason=="empty_unknown"`.
    - 失敗検出: unknown target becomes ready.
    - 検証方法: domain test.
    - 関連 closure id: `cl-ec-001`
  - `tc-s02-004` regression: done child-only dependency stays non-blocking
    - 前提: high-level target has child issues and all are done; injected high-level status is `state=done`, `source=descendant_aggregate`.
    - 操作: evaluate readiness.
    - 期待結果: no issue blocker, ready remains true, satisfied context remains available.
    - 失敗検出: done child issue returns to `blockers`.
    - 検証方法: domain test.
    - 関連 closure id: `cl-ec-002`
- report evidence destination:
  - Step Contract Closure, Test Contract Closure, Closure Coverage, Delegated Worker Evidence, Reviewer Gate Status, Step Commit Gate.
- step closure contract:
  - close condition: S02 domain tests pass for open/closed/unknown/descendant-derived status context and reviewer pass is recorded.
  - commit gate: commit only S02 allowed paths after reviewer pass.

### S03 — Command Guards And CLI Output
- 振る舞いの目標:
  - `deps check`, `active set`, `issue start` が同じ evaluation を使い、node-blocked issue を開始させない。
- allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/check_deps.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_lifecycle.py`
  - CLI text / JSON renderer only if required by this step
  - `tests/cli_runtime/test_deps.py`, `tests/cli_runtime/test_issue_lifecycle.py`, `tests/unit/application/test_check_deps.py`, `tests/unit/application/test_set_active.py`
- forbidden changes:
  - dependency guard bypass via `--force`, GitHub mutation, unrelated branch lifecycle change, storage/presentation artifact behavior outside command output.
- delegation contract:
  - role: `dev-coder`
  - inputs: `requirement.md`, `design.md`, `plan.md`, S02 domain contract, target files above.
  - acceptance criteria: `cl-ac-001`, `cl-ac-002`, `cl-ec-001`, `cl-ec-002` close at command guard level.
  - required verification: `uv run pytest tests/cli_runtime/test_deps.py tests/cli_runtime/test_issue_lifecycle.py tests/unit/application/test_check_deps.py tests/unit/application/test_set_active.py -k "deps_check or active or issue_start or node"`
  - output required: common required output plus command JSON/text examples and status source path evidence.
  - reviewer focus: `code-reviewer` checks exit code, typed JSON fields, guard parity, force semantics, status source construction.
  - stop: `issue start` requires lifecycle redesign, or JSON schema strategy must change beyond design.
- status enrichment contract:
  - S03 owns the command-time high-level status context builder.
  - Priority is GitHub snapshot/enrichment when available, then local metadata / cached generated state, then descendant aggregate, then `unknown`.
  - `check_deps.py` and `set_active.py` must pass the same status context shape into domain evaluation.
  - `issue_lifecycle.py` should continue to reach dependency guard through `set_active` unless implementation proves a direct shared helper is smaller; either path must keep force from bypassing dependency guard.
- 具体テストケース一覧:
  - `tc-s03-001` acceptance: `deps check --json` fails on empty open epic
    - 前提: open `iss-00301` depends on empty `epic-00202`; command fixture/stub resolves high-level status as `state=open`, `source=github`.
    - 操作: `spec-dock deps check --id iss-00301 --json`.
    - 期待結果: non-zero exit, `schema_version==2`, `ready=false`, `blockers` includes `epic-00202`, typed `node_blockers` includes reason/state/source.
    - 失敗検出: exit 0 or warning-only output.
    - 検証方法: CLI runtime test.
    - 関連 closure id: `cl-ac-001`
  - `tc-s03-002` acceptance: `active set` rejects node-blocked issue
    - 前提: same node-blocked fixture.
    - 操作: `spec-dock active set iss-00301`.
    - 期待結果: command fails, active pointer unchanged, stderr names `epic-00202`.
    - 失敗検出: active issue becomes blocked issue.
    - 検証方法: CLI/application test.
    - 関連 closure id: `cl-ac-001`
  - `tc-s03-003` acceptance: `issue start --force` does not bypass dependency guard
    - 前提: node-blocked target and no unrelated lifecycle blocker.
    - 操作: `spec-dock issue start iss-00301 --force`.
    - 期待結果: command fails because dependency guard remains blocking; no checkout/active mutation occurs.
    - 失敗検出: force starts blocked issue.
    - 検証方法: `tests/cli_runtime/test_issue_lifecycle.py`.
    - 関連 closure id: `cl-ac-001`
  - `tc-s03-004` edge: warning-only satisfied context exits zero
    - 前提: target depends on empty closed epic from GitHub/cache source or done child-only epic from descendant aggregate source.
    - 操作: `spec-dock deps check --id iss-00301 --json`.
    - 期待結果: exit 0, `ready=true`, no `node_blockers`, satisfied dependency context present.
    - 失敗検出: satisfied-only context causes non-zero exit.
    - 検証方法: CLI runtime test.
    - 関連 closure id: `cl-ac-002`, `cl-ec-002`
- report evidence destination:
  - Step Contract Closure, Test Contract Closure, Closure Coverage, Delegated Worker Evidence, Reviewer Gate Status, Step Commit Gate.
- step closure contract:
  - close condition: S03 command tests pass, node-blocked issues fail consistently across `deps check`, `active set`, and `issue start`, and reviewer pass is recorded.
  - commit gate: commit only S03 allowed paths after reviewer pass.

### S04 — Sync State And Presentation Artifacts
- 振る舞いの目標:
  - `sync` が lossless readiness context を `.agent/deps-issues.json`, `deps-issues.puml`, `deps-raw.puml` に出す。
- allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/puml.py`
  - `tests/cli_runtime/test_sync.py`, `tests/unit/presentation/test_runtime_sync_s07.py`, `tests/unit/presentation/test_deps_raw_puml.py`
- forbidden changes:
  - renderer-side readiness inference, `index.json` reparse as `deps-issues` source, all-history graph dump, `deps-raw` authority claim.
- delegation contract:
  - role: `dev-coder`
  - inputs: `requirement.md`, `design.md`, `plan.md`, S02/S03 contracts, target files above.
  - acceptance criteria: `cl-ac-004`, `cl-ac-005`, plus sync/presentation parts of `cl-ac-002`, `cl-ec-001`, `cl-ec-002`, `cl-ec-003`.
  - required verification: `uv run pytest tests/cli_runtime/test_sync.py tests/unit/presentation/test_runtime_sync_s07.py tests/unit/presentation/test_deps_raw_puml.py`
  - output required: common required output plus example `deps-issues.json` v2 snippet and `deps-raw.puml` state-rendering evidence.
  - reviewer focus: `code-reviewer` checks schema v2, context node inclusion boundary, deterministic sorting, payload/rendering separation.
  - stop: `SyncStateResult` cannot carry required typed contexts without duplicating readiness rules, or payload size becomes unbounded.
- status enrichment contract:
  - S04 reuses or shares S03 high-level status context construction for sync.
  - `sync_state.py` owns carrying this context through `SyncStateResult`.
  - `json_state.py` and `puml.py` may only serialize/render the supplied state; they must not recompute GitHub/local/descendant status priority.
- 具体テストケース一覧:
  - `tc-s04-001` acceptance: `deps-issues` v2 includes high-level blocker context
    - 前提: open issue depends on empty epic; sync fixture resolves high-level status as `state=open`, `source=github` or cache.
    - 操作: run `spec-dock sync`.
    - 期待結果: `.agent/deps-issues.json` has `schema_version==2`, projection `issue-readiness-with-dependency-context`, node/edge for epic blocker.
    - 失敗検出: `deps-issues` nodes match todo issues only and omit epic blocker.
    - 検証方法: CLI runtime test.
    - 関連 closure id: `cl-ac-004`
  - `tc-s04-002` acceptance: satisfied dependencies remain visible without blocking
    - 前提: open target depends on empty closed epic from GitHub/cache source and/or done issue prerequisite.
    - 操作: run sync.
    - 期待結果: target remains ready; satisfied dependency nodes/edges are visible and not labeled `blocks`.
    - 失敗検出: satisfied context disappears or renders as blocking.
    - 検証方法: CLI runtime and presentation assertions.
    - 関連 closure id: `cl-ac-002`, `cl-ec-002`
  - `tc-s04-003` acceptance: `deps-raw.puml` colors high-level participants from payload
    - 前提: raw direct edges include initiative/epic endpoints and sync payload includes state/source from S04 context.
    - 操作: render `deps-raw.puml`.
    - 期待結果: initiative/epic package style or label reflects state/source; legend distinguishes raw state from readiness authority.
    - 失敗検出: packages remain unqualified white while only issue rectangles have state.
    - 検証方法: unit presentation test.
    - 関連 closure id: `cl-ac-005`
  - `tc-s04-004` regression: deps disabled path is preserved
    - 前提: raw cycle preflight fails and sync runs with forced artifact generation path.
    - 操作: render deps artifacts.
    - 期待結果: disabled artifact note remains; no misleading partial graph.
    - 失敗検出: stale or partial dependency graph appears.
    - 検証方法: existing disabled raw dependency view test plus deps-issues assertion if needed.
    - 関連 closure id: `cl-ec-003`
- report evidence destination:
  - Step Contract Closure, Test Contract Closure, Closure Coverage, Delegated Worker Evidence, Reviewer Gate Status, Step Commit Gate.
- step closure contract:
  - close condition: S04 sync/presentation tests pass, `deps-issues` no longer derives from todo-only `index.json`, `deps-raw` renders supplied high-level state, and reviewer pass is recorded.
  - commit gate: commit only S04 allowed paths after reviewer pass.

### S90 — Docs Impact Resolution And Dogfooding Mirror
- 振る舞いの目標:
  - provider docs が storage/readiness/raw visual の authority 境界を説明し、dogfooding mirror を refresh または意図的に記録する。
- allowed paths:
  - `src/spec_dock/assets/spec_dock/docs/reference_deps.md`
  - `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
  - generated mirror paths under `spec-dock/docs/` only if refresh is intentionally run and reviewed.
- forbidden changes:
  - workflow policy expansion, implementation source/test changes, broad scaffold output churn.
- delegation contract:
  - role: `doc-writer`
  - inputs: `requirement.md`, `design.md`, `plan.md`, S01-S04 implemented contract, target docs above.
  - acceptance criteria: `cl-ac-006`, `cl-ec-004`.
  - required verification: docs diff inspection; if scaffold refresh runs, inspect provider/mirror diffs.
  - output required: common required output plus provider/mirror doc alignment note.
  - reviewer focus: `spec-reviewer` checks docs/spec alignment, raw/debug authority wording, provider source-of-truth clarity.
  - stop: docs require workflow semantics beyond dependency reference, or scaffold refresh touches broad unrelated files.
- 具体テストケース一覧:
  - `tc-s90-001` inspect-only: provider docs define readiness authority
    - 前提: implementation has node blockers, satisfied dependencies, and `deps-issues` v2.
    - 操作: inspect `reference_deps.md` and `reference_sync.md`.
    - 期待結果: docs state `.meta.json.depends_on` is raw storage, `deps-issues` is readiness/blocker authority, `deps-raw` is raw visual/debug only.
    - 失敗検出: docs still describe empty expansion as warning-only ready behavior.
    - 検証方法: docs diff inspection and `spec-reviewer`.
    - 関連 closure id: `cl-ac-006`, `cl-ec-004`
  - `tc-s90-002` inspect-only: dogfooding mirror is intentionally aligned or deferred
    - 前提: provider docs changed.
    - 操作: run scaffold refresh or record a non-refresh rationale.
    - 期待結果: mirror docs align, or `report.md` records non-blocking deferral with revisit condition.
    - 失敗検出: provider and dogfooding docs silently diverge.
    - 検証方法: diff inspection and report evidence.
    - 関連 closure id: `cl-ac-006`
- report evidence destination:
  - Step Contract Closure, Test Contract Closure, Closure Coverage, Delegated Worker Evidence, Reviewer Gate Status, Step Commit Gate, Docs Impact Resolution.
- step closure contract:
  - close condition: provider docs explain node blockers/satisfied dependencies/authority boundary, mirror status is recorded, and spec-reviewer pass is recorded.
  - commit gate: commit only S90 allowed paths after reviewer pass.

### S99 — Final Quality Gate
- 振る舞いの目標:
  - all closure evidence, tests, reviews, and diff guard are complete before execution closeout.
- allowed paths:
  - no implementation edits except reviewer-directed fixes through the relevant prior step; main orchestrator may update `report.md` evidence.
- delegation contract:
  - roles: `qa-reviewer`, issue-wide `code-reviewer`, final `spec-reviewer`
  - inputs: final implementation diff, `requirement.md`, `design.md`, `plan.md`, completed `report.md`, test outputs.
  - acceptance criteria: all `cl-*` closure rows complete.
  - required verification: `uv run pytest tests/unit tests/cli_runtime`; broaden to `uv run pytest` if shared scaffold/update behavior is touched.
  - output required: reviewer verdicts, final verification output, final diff guard, unresolved risks.
  - reviewer focus: QA coverage, integrated code risk, spec/report/docs alignment.
  - stop: any required closure lacks evidence; out-of-scope files appear; dogfooding mirror status is unexplained.
- 具体テストケース一覧:
  - `tc-s99-001` final regression lane
    - 前提: S01-S90 reviewed and committed.
    - 操作: run final verification command.
    - 期待結果: targeted lanes pass; broader failures, if any, are classified with evidence.
    - 失敗検出: dependency contract regression outside targeted slices.
    - 検証方法: command output recorded in `report.md`.
    - 関連 closure id: all required closure ids
  - `tc-s99-002` final diff guard
    - 前提: implementation steps complete.
    - 操作: inspect `git status --short` and `git diff --name-only`.
    - 期待結果: only planned provider runtime/docs/tests and intentional dogfooding mirror files changed; no legacy `app.py`, secrets, unrelated workflow/config.
    - 失敗検出: unplanned paths appear.
    - 検証方法: final diff guard evidence in `report.md`.
    - 関連 closure id: `cl-ac-006`, `cl-ec-004`

## レビュー / QA ゲート方針
- S01-S04:
  - worker: `dev-coder`
  - reviewer: `code-reviewer`
  - commit: reviewer pass 後、step-local commit
- S90:
  - worker: `doc-writer`
  - reviewer: `spec-reviewer`
  - commit: reviewer pass 後、step-local commit
- S99:
  - reviewers: `qa-reviewer`, `code-reviewer`, `spec-reviewer`
  - pass 条件: closure coverage, final test evidence, final diff guard, report ledger completeness.

## report evidence destination
- Step Contract Closure:
  - each S01-S04/S90/S99 close condition.
- Test Contract Closure:
  - all `cl-*` rows and concrete test ids.
- Closure Delta:
  - any alias, added/removed/changed closure id.
- Delegated Worker Evidence:
  - worker summary, changed files, tests, risks, integration decision.
- Reviewer Gate Status:
  - each fresh reviewer pass/fail.
- Step Commit Gate:
  - commit hash, post-commit clean check, approved no-op rationale if applicable.

## ロールバック / 互換性
- storage migration はないため、rollback は issue diff revert で扱う。
- `DepsEvaluation.blockers`, `blockers_top`, `closure`, `ready`, `guard_reason` は維持する。
- typed `issue_blockers` / `node_blockers` / `satisfied_dependencies` を追加して consumer ambiguity を減らす。
- `deps check --json` と `deps-issues.json` は `schema_version: 2` として docs/tests に固定する。
- node id を `blockers` に含めることが承認済み consumer contract を壊すと判明した場合は、warning-only に逃がさず design amendment に戻す。

## 最終出口契約（Final Exit Contract）
- All `cl-*` have observed evidence in `report.md`.
- S01-S04 and S90 are each reviewed and committed or explicitly approved as no-op.
- `uv run pytest tests/unit tests/cli_runtime` passes, or unrelated failures are evidenced.
- `qa-reviewer`, issue-wide `code-reviewer`, and final `spec-reviewer` pass.
- Final diff guard confirms no legacy `app.py`, secrets, GitHub state, unrelated workflow/config, or unplanned canonical docs changes.
- Human blocking questions: none at planning time.

## 計画ドラフト採用
- 採用元:
  - `discussions/20260618t152507z-draft-plan-node-level-dependency-projection.md`
- 採用内容:
  - S01-S04/S90/S99 の step order。
  - closure index と concrete test seeds。
  - per-step delegation/review/commit gate。
  - legacy `app.py` を source of truth にしない制約。
- 採用しない内容:
  - draft は implementation readiness や reviewer pass を claim していない。canonical plan integration 後の fresh `spec-reviewer` pass を正本 gate とする。
