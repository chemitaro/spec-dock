---
種別: 実装計画書（Issue）
ID: "iss-00170"
タイトル: "Harden Pr Monitor Stable Observation"
関連GitHub: ["#170"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-08"
依存: ["requirement.md", "design.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00170 Harden Pr Monitor Stable Observation — 実装計画（実行契約 / Execution Contract）

## この計画で満たす要件ID

- AC:
  - AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, AC-007, AC-008, AC-009, AC-010, AC-011, AC-012, AC-013, AC-014
- EC:
  - EC-001, EC-002, EC-003, EC-004, EC-005, EC-006, EC-007, EC-008, EC-009
- 非交渉制約:
  - `pr-monitor` sub-agent は完全廃止する。
  - `github-codex-pr-review-comments` skill は削除し、compatibility shim は残さない。
  - 正規入口は `github-pr-observation` skill / scripts とする。
  - wait / snapshot / collector は read-only fixed GitHub calls だけを使う。
  - stdout final JSON text が唯一の primary result である。
  - stderr progress は default で出すが non-authoritative である。
  - latest / expected head SHA に束縛されない observation は merge-prepared evidence に使わない。
  - `summary.md` は生成しない。

## 実装順序

1. S01 Asset retirement and observation skill scaffold:
   - 旧 `pr-monitor` / `github-codex-pr-review-comments` の退役と、新 `github-pr-observation` skill の provider-side scaffold を固定する。
2. S02 Public script contract and stdout/stderr boundary:
   - `wait_pr_observation.sh` / `fetch_pr_observation_snapshot.sh` の CLI、入力検証、stdout final JSON、stderr progress、optional `--out` contract を実装する。
3. S03 CI/check/status collector:
   - CI status taxonomy、head SHA binding、zero-check grace、required pending、failure detail を実装する。
4. S04 Review/comment/thread collector:
   - review status taxonomy、Codex subset、trigger window、body modes/caps、fixed GraphQL thread state boundary を実装する。
5. S05 Wait loop integration and stable result:
   - snapshot fingerprint、quiet window、same fingerprint count、timeout、head-change reset、final normalized status を統合する。
6. S06 Workflow skill guidance and dogfooding parity:
   - `github-pr-merge-preparer` / `github-pr-creator` / host guidance から `pr-monitor` handoff を除き、dogfooding mirror と update cleanup を揃える。
7. S90 Docs impact resolution:
   - shipped skill docs / workflow guidance の整合性を確認し、必要な docs-only 更新を閉じる。
8. S99 Final quality gates:
   - closure evidence、tests、reviewer gates、report ledger を揃える。

## 要件 ↔ ステップ対応

| 要件 | 主ステップ | 補助ステップ | 検証方針 |
|---|---|---|---|
| AC-001 | S02 | S05, S06 | caller が loop 判断せず、stdout JSON だけで最終判断する contract test / skill text inspection |
| AC-002 | S03 | S05 | expected head SHA mismatch が non-success JSON になる fixture test |
| AC-003 | S05 | S03 | monitoring 中の head change が stale/reset として扱われる fixture test |
| AC-004 | S03 | S05 | failure 系 conclusion が1件でも CI failed になり、details が出る fixture test |
| AC-005 | S05 | S02, S03, S04 | quiet / fingerprint / same count まで complete しない wait fixture test |
| AC-006 | S04 | S05 | trigger-window review/comment body が body mode/cap 付きで出る fixture test |
| AC-007 | S03 | S05 | zero-check grace 中は success にしない fixture test |
| AC-008 | S04 | S05 | unresolved / changes requested / comments が review non-success または human action になる fixture test |
| AC-009 | S04 | S05 | thread state unavailable は limitation として machine-readable に出る fixture test |
| AC-010 | S02 | S05 | stderr progress が1 poll 最大1行、stdout に混ざらない test |
| AC-011 | S01 | S06 | provider/mirror inventory と stale cleanup test |
| AC-012 | S04 | S05 | explicit trigger id/time 後の本文だけを含む fixture test |
| AC-013 | S04 | S05 | inferred/unknown trigger の limitation と body suppression test |
| AC-014 | S03 | S05 | Actions job/step failure detail fallback test |
| EC-001 | S05 | S03, S04 | checks green 後も review stability を待つ fixture test |
| EC-002 | S03 | S05 | success + pending / required pending が pending になる fixture test |
| EC-003 | S03 | S05 | skipped / neutral terminal non-blocking が pending/failed 不在なら passed になる fixture test |
| EC-004 | S04 | S05 | resolved/outdated thread と unresolved thread を分離する fixture test |
| EC-005 | S04 | S02, S05 | thread-state wrapper の missing/auth/rate/schema failure は limitation + `review=unknown` / human gate になる fixture test |
| EC-006 | S02 | S05 | progress output が bounded stderr に留まり、詳細は final JSON / optional artifacts に残る fixture test |
| EC-007 | S05 | S03, S04 | draft / non-open PR が human_gate になり merge-prepared にならない fixture test |
| EC-008 | S05 | S02 | late snapshot poll / wait deadline timeout が latest payload を保持しつつ timeout limitation を付ける fixture test |
| EC-009 | S03 | S05 | required-check pending、non-CI merge state、required-check metadata failure を分ける fixture test |

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| ID | ステップ | 仕様リンク | 固定する期待値 | 防ぐ bug class | 必須 | 証跡レベル |
|---|---|---|---|---|---|---|
| CL-AC-001 | S02/S05 | AC-001 | caller は polling loop を持たず、stdout final JSON が primary result | agent-side loop regression | yes | red-required + inspection |
| CL-AC-002 | S03/S05 | AC-002 | head SHA mismatch は `stale_head` / non-success / `observation_complete=false` | stale green reuse | yes | red-required |
| CL-AC-003 | S05 | AC-003 | monitoring 中の head change は old snapshot を final success にしない | mixed-SHA final result | yes | red-required |
| CL-AC-004 | S03 | AC-004 | 1件でも failure 系なら CI status は `failed`、detail を保持 | mixed success/failure false pass | yes | red-required |
| CL-AC-005 | S05 | AC-005 | quiet / fingerprint / same count を満たすまで complete しない | early success | yes | red-required |
| CL-AC-006 | S04 | AC-006 | trigger-window body を default truncated mode で final JSON に含める | missing actionable review body | yes | red-required |
| CL-AC-007 | S03/S05 | AC-007 | zero-check grace 未満は success にしない | no-check false green | yes | red-required |
| CL-AC-008 | S04 | AC-008 | unresolved / changes requested / comments は review status に反映 | ignored blocker | yes | red-required |
| CL-AC-009 | S04 | AC-009 | thread state unavailable は limitation として出す | hidden unresolved thread | yes | red-required |
| CL-AC-010 | S02/S05 | AC-010 | progress は stderr、1 poll 最大1行、stdout JSON に混ざらない | unparsable stdout | yes | red-required |
| CL-AC-011 | S01/S06 | AC-011 | new skill added、old agent/skill removed、shim なし、stale cleanup あり | duplicate/conflicting assets | yes | red-required + parity |
| CL-AC-012 | S04 | AC-012 | explicit trigger 後の body だけを current payload に含める | old review noise | yes | red-required |
| CL-AC-013 | S04 | AC-013 | inferred は limitation、unknown は body full output しない | unsafe body overcollection | yes | red-required |
| CL-AC-014 | S03 | AC-014 | CI failure detail は workflow/run/job/step または check-run fallback で出す | insufficient fix context | yes | red-required |
| CL-EC-001 | S05 | EC-001 | CI green 後も review stability を待つ | late review miss | yes | red-required |
| CL-EC-002 | S03 | EC-002 | success + pending/status pending は pending | partial green | yes | red-required |
| CL-EC-003 | S03 | EC-003 | skipped / neutral terminal non-blocking は unknown ではなく passed に畳める | skipped-as-unknown false block | yes | red-required |
| CL-EC-004 | S04 | EC-004 | resolved/outdated と unresolved を分離 | stale comment blocker | yes | red-required |
| CL-EC-005 | S04/S05 | EC-005 | thread-state wrapper failure は limitation + `review=unknown` / human gate | hidden collection failure | yes | red-required |
| CL-EC-006 | S02/S05 | EC-006 | progress は bounded stderr、詳細は final JSON / optional artifacts | progress flood / stdout contamination | yes | red-required |
| CL-EC-007 | S05 | EC-007 | draft / non-open PR は human_gate | draft/closed false merge-prepared | yes | red-required |
| CL-EC-008 | S05 | EC-008 | late poll timeout / wait deadline timeout は latest payload を保持 | timeout synthetic unknown loss | yes | red-required |
| CL-EC-009 | S03/S05 | EC-009 | required-check pending は wait、non-CI merge state / metadata failure は false pass させない | merge-state false wait / false green | yes | red-required |

## 実装ステップ

### S01 Asset retirement and observation skill scaffold

- 目的:
  - provider-side source of truth で、旧 `pr-monitor` agent assets と旧 `github-codex-pr-review-comments` skill を削除し、新 `github-pr-observation` skill scaffold を追加する。
- 対象ファイル:
  - add: `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - add: `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
  - add: `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh`
  - add: `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`
  - add: `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`
  - remove: `src/spec_dock/assets/install_root/.codex/agents/pr-monitor.toml`
  - remove: `src/spec_dock/assets/install_root/.github/agents/pr-monitor.agent.md`
  - remove: `src/spec_dock/assets/install_root/.agents/skills/github-codex-pr-review-comments/`
  - update tests that assert installed asset inventory / stale cleanup.
- 委任:
  - role: dev-coder
  - allowed changes: listed provider asset files and focused inventory tests.
  - forbidden: canonical docs, source outside installed asset/update tests, compatibility shim.
- 必須検証:
  - asset inventory test fails before adding new skill / removing old assets and passes after.
  - update cleanup fixture proves stale `pr-monitor` / `github-codex-pr-review-comments` assets are removed.
  - `rg 'pr-monitor|github-codex-pr-review-comments' src/spec_dock/assets/install_root tests -n` only finds deliberate retirement assertions or historical text.
- reviewer gate:
  - code-reviewer for asset/test diff.
- closure:
  - CL-AC-011.

### S02 Public script contract and stdout/stderr boundary

- 目的:
  - public wait/snapshot scripts の fixed CLI、input validation、stdout/stderr separation、progress contract、optional `--out` behavior を実装する。
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh`
  - focused shell/script contract tests.
- 委任:
  - role: dev-coder
  - allowed changes: new skill scripts and tests.
  - forbidden: caller-provided endpoint/method/query/header/body/jq/raw gh args, write operations, `summary.md`.
- 必須検証:
  - invalid repo/pr/head/options fail before any fake `gh` call.
  - stdout contains valid JSON only; progress and diagnostics do not contaminate stdout.
  - stderr default emits bounded key/value progress; `--progress none` suppresses progress.
  - `--out` writes `result.json` only as stdout copy plus debug artifacts; no `summary.md`.
  - auth/rate/schema collection failure can be represented as limitation + non-success when JSON generation is possible.
- reviewer gate:
  - code-reviewer.
- closure:
  - CL-AC-001, CL-AC-010, CL-EC-006.

### S03 CI/check/status collector

- 目的:
  - expected head SHA に束縛した checks/statuses/Actions collection と CI taxonomy を実装する。
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`
  - public snapshot/wait scripts if integration fields are needed.
  - focused CI fixture tests.
- 委任:
  - role: dev-coder
  - allowed changes: CI collector, shared schema helpers inside new skill scripts, focused tests.
  - forbidden: logs full-text collection as default path, repository-specific policy engine, write operations.
  - 必須検証:
    - statuses: `unknown`, `none`, `pending`, `running`, `passed`, `failed`.
    - any failure/error/cancelled/timed_out/action_required/startup_failure/stale yields `failed`.
    - success + skipped + neutral can yield `passed` when no blocking pending/failure remains.
    - required pending / path-filter pending remains `pending`.
    - `mergeStateStatus=BLOCKED` plus pending / expected required check rollup becomes `required_checks_missing_or_pending` and `ci=pending`.
    - `DIRTY` / `BEHIND` and other non-CI merge states become `pr_merge_state_blocking` and `ci=unknown` / human gate instead of `ci=pending`.
    - `gh pr view --json mergeStateStatus,statusCheckRollup` failure is surfaced as `pr_required_check_state_unavailable` and does not allow observed green false pass when checks/statuses exist.
  - zero checks remain non-success until grace/deadline semantics allow a limitation result.
  - `ci.failures[]` includes workflow/run/job/failed steps when obtainable, otherwise check-run fallback.
- reviewer gate:
  - code-reviewer.
- closure:
  - CL-AC-002, CL-AC-004, CL-AC-007, CL-AC-014, CL-EC-002, CL-EC-003, CL-EC-009.

### S04 Review/comment/thread collector

- 目的:
  - review/comment/thread/review request collection、Codex subset、trigger window、body mode/cap、thread limitation を実装する。
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`
  - public snapshot/wait scripts if integration fields are needed.
  - focused review fixture tests.
- 委任:
  - role: dev-coder
  - allowed changes: review collector, shared schema helpers inside new skill scripts, focused tests.
  - forbidden: arbitrary GraphQL query/endpoint, P1/P2 text interpretation, old-trigger body mixing, reviewer identity in stderr progress.
  - 必須検証:
    - fixed REST GET reads issue comments, pull reviews, pull review comments.
    - fixed GraphQL query reads review thread state and `reviewDecision` when available; unavailable thread state becomes limitation.
    - review statuses are limited to `unknown`, `none`, `requested`, `commented`, `approved`, `changes_requested`, `unresolved`.
    - `reviewDecision=REVIEW_REQUIRED` maps to `requested` even without explicit review-request nodes.
    - current trigger-window issue comments override approval for aggregate status.
    - all review signals and Codex-authored subset are both represented.
    - explicit `--trigger-comment-id` / `--trigger-created-at` includes only trigger-window bodies.
    - explicit `--trigger-comment-id` without `--trigger-created-at` resolves timestamp from issue comments or records `trigger_timestamp_unresolved`.
  - inferred trigger emits `trigger_inferred` limitation.
  - unknown trigger does not dump all bodies.
  - `body-mode` cap/truncation metadata preserves valid JSON.
- reviewer gate:
  - code-reviewer.
- closure:
  - CL-AC-006, CL-AC-008, CL-AC-009, CL-AC-012, CL-AC-013, CL-EC-004, CL-EC-005.

### S05 Wait loop integration and stable result

- 目的:
  - snapshot collectors を bounded deterministic wait に統合し、stable fingerprint と final normalized result を返す。
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh`
  - focused wait-loop fixture tests.
- 委任:
  - role: dev-coder
  - allowed changes: new skill scripts and focused tests.
  - forbidden: infinite waits, model/agent-side polling fallback, progress-as-authority.
  - 必須検証:
    - default `timeout=1800`, `poll_interval=30`, `quiet=90`, `same_fingerprint_count=2` are exposed and overrideable.
    - quiet window and same fingerprint count are required before `observation_complete=true`.
    - head SHA changes reset or terminate as stale/non-success.
    - CI green followed by late review feedback waits for review stability.
    - draft and non-open PRs return `human_gate` with PR-state-specific recommended next action instead of merge-prepared success.
    - late snapshot poll timeout or wait deadline expiry with a prior valid payload preserves latest CI/review summary and appends `snapshot_poll_timeout`.
    - terminal stdout JSON includes `overall_status`, `normalized_status`, `observation_complete`, `summary`, `limitations`, `recommended_next_action`, `ci`, `review`, `trigger`, `artifacts`.
- reviewer gate:
  - code-reviewer.
- closure:
  - CL-AC-001, CL-AC-003, CL-AC-005, CL-AC-010, CL-EC-001, CL-EC-005, CL-EC-006, CL-EC-007, CL-EC-008, CL-EC-009.

### S06 Workflow skill guidance and dogfooding parity

- 目的:
  - PR workflow skills / host guidance から `pr-monitor` role handoff を除き、`github-pr-observation` direct invocation に置き換える。provider と dogfooding mirror を一致させる。
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-creator/SKILL.md`
  - provider host/role guidance files that mention `pr-monitor`
  - dogfooding mirror `.agents/skills/github-pr-observation/`
  - dogfooding removal targets `.codex/agents/pr-monitor.toml`, `.github/agents/pr-monitor.agent.md`, `.agents/skills/github-codex-pr-review-comments/`
  - parity / install / update tests.
- 委任:
  - role: dev-coder for tests and scaffold parity; doc-writer may be used for text-only skill guidance if no script/test edits are needed.
  - allowed changes: listed skill/guidance/mirror/test files.
  - forbidden: recreating `pr-monitor`, leaving deprecated aliases, changing PR merge responsibility.
- 必須検証:
  - provider/mirror new skill files match expected installed content.
  - old provider and mirror assets are absent.
  - `github-pr-merge-preparer` no longer delegates to `pr-monitor`; it invokes `wait_pr_observation.sh` and consumes stdout JSON.
  - `github-pr-creator` references snapshot/wait only as post-create observation support.
  - role guidance contains no active `pr-monitor` routing.
- reviewer gate:
  - code-reviewer for tests/assets, spec-reviewer focus if skill prose changes material workflow semantics.
- closure:
  - CL-AC-011 plus regression coverage for AC-001.

### S90 Docs impact resolution

- 目的:
  - shipped skill docs and workflow guidance changes are sufficient; unrelated docs/README are not changed unless they contain active `pr-monitor` routing.
- 委任:
  - role: doc-writer when non-issue permanent docs require updates.
  - otherwise orchestrator records no-op evidence in `report.md`.
- 必須検証:
  - `rg 'pr-monitor|github-codex-pr-review-comments|github-pr-observation' src/spec_dock/assets/install_root spec-dock/docs .agents .codex .github -n` inspected.
  - remaining old names are only historical issue docs, removal assertions, or intentionally quoted migration notes.
- reviewer gate:
  - spec-reviewer focus in final gate.

### S99 Final quality gates

- 目的:
  - implementation evidence and authoring evidence are complete enough for issue execution / PR preparation.
- 必須検証:
  - focused tests from S01〜S06.
  - `uv run pytest tests/unit/infra/test_init_update.py`
  - any new focused test file added for scripts.
  - `git diff --check`
  - `./spec-dock/scripts/spec-dock sync --no-github`
- reviewer gates:
  - qa-reviewer: closure/test sufficiency.
  - code-reviewer: issue-wide source/test diff.
  - spec-reviewer: requirement/design/plan/report/implementation evidence alignment.

## レビュー / QA ゲート方針

- Each implementation step that changes scripts/tests requires a fresh code-reviewer pass before integration.
- Material workflow prose changes require either code-reviewer inspection or spec-reviewer focus, depending on whether the risk is implementation or specification alignment.
- Plan/design/requirement gates must be fresh after the latest substantive authoring change.
- Waiver, unavailable, denied, or provisional reviewer states do not satisfy this plan unless the user explicitly accepts risk; the default is blocked/incomplete.

## 実行ルール（全ステップ共通）

- Main orchestrator records canonical issue evidence in `report.md`; source/test changes are delegated.
- Do not start implementation from a stale pre-ADR plan.
- Do not restore old `pr-monitor` or `github-codex-pr-review-comments` for compatibility.
- Do not add arbitrary GitHub API passthrough to make collection easier.
- If implementation discovers that fixed REST/GraphQL calls cannot technically provide a required field, stop and amend requirement/design before proceeding.
- If a step adds or removes closure obligations, update this plan and rerun fresh spec-reviewer before continuing.
