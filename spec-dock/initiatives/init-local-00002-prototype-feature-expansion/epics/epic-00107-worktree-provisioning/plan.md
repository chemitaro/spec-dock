---
種別: 計画書（Epic）
ID: "epic-00107"
タイトル: "Worktree Provisioning"
関連GitHub: ["#107"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-05-22"
依存: ["requirement.md", "design.md"]
親: ["init-local-00002"]
---

# epic-00107 Worktree Provisioning — 計画（Issues / Order）

## この計画で閉じる E-RQ / E-AC
- E-RQ:
  - E-RQ-001: runtime worktree creation command
  - E-RQ-002: sibling `<repo-basename>-worktrees/` placement and linked-worktree normalization
  - E-RQ-003: id / directory / branch naming
  - E-RQ-004: label validation
  - E-RQ-005: collision detection and retry
  - E-RQ-006: optional / non-fatal `make init` bootstrap
  - E-RQ-007: output contract
  - E-RQ-008: Codex-managed worktree non-reimplementation
  - E-RQ-009: parallel development support without banning main checkout work
  - E-RQ-010: provider-side source of truth and layered runtime architecture
- E-AC:
  - E-AC-001: basic create
  - E-AC-002: repeated create / collision
  - E-AC-003: label naming
  - E-AC-004: invalid label
  - E-AC-005: `make init` success
  - E-AC-006: bootstrap skipped
  - E-AC-007: bootstrap detection/execution failure warning + exit `0`
  - E-AC-008: linked-worktree normalization
  - E-AC-009: non-retryable Git/path failure
  - E-AC-010: detached/outside repo failure
  - E-AC-011: provider / dogfooding / docs parity

## Issue 分割方針
- 分割原則:
  - Issue 1 は pure contract / adapter foundation を閉じる。
  - Issue 2 は CLI integration と user-visible output/docs を閉じる。
  - Issue 3 は dogfooding refresh、parity、final epic verification を閉じる。
  - SpecDock tree mutation と worktree creation は混ぜない。
  - `worktree remove` / `status` / `prune` は future extension として扱い、この epic の issue に入れない。
- 例外:
  - Issue 1 の実装中に `domain/worktree.py` 抽出が不要と判断できる場合は、application-local helper に留めてよい。
  - Issue 2 の docs 更新で provider docs と dogfooding docs の両方が同時に必要な場合は、provider-side 更新を先に行い、dogfooding parity は Issue 3 で確認する。

## Issue 一覧（順序 / tranche 付き）
- iss-00110-worktree-create-core-use-case:
  - 目的:
    - `worktree create` の application contract、GitGateway / BootstrapGateway、candidate generation、collision retry、main worktree normalization、bootstrap result aggregation を実装する。
  - 成果物:
    - `application.contracts` の `WorktreeCreateRequest` / `WorktreeCreateResult`
    - `application.ports` の worktree / bootstrap protocols
    - `application/worktree.py`
    - `infra/git_cli.py` worktree list / main worktree / add worktree helpers
    - `infra/make_cli.py`
    - core unit/runtime tests for naming, retry, linked-worktree normalization, bootstrap statuses, fatal failures
  - tranche:
    - T1 core contract
  - closes:
    - E-RQ-002, E-RQ-003, E-RQ-004, E-RQ-005, E-RQ-006
    - E-AC-002, E-AC-003, E-AC-004, E-AC-006, E-AC-007, E-AC-008, E-AC-009, E-AC-010
  - 依存:
    - approved requirement / design
- iss-00108-worktree-create-cli-and-output:
  - 目的:
    - `spec-dock worktree create [LABEL]` を CLI command として公開し、absolute path primary output と warnings を実装する。
  - 成果物:
    - `commands/worktree.py`
    - `cli/parser.py` / `cli/registry.py` / `cli/bootstrap.py` wiring
    - `presentation/cli_text.py` の `render_worktree_create_text`
    - CLI help
    - runtime tests for command success/failure exit codes and output text
  - tranche:
    - T2 command surface
  - closes:
    - E-RQ-001, E-RQ-007, E-RQ-010
    - E-AC-001, E-AC-005, E-AC-007, E-AC-009, E-AC-010
  - 依存:
    - iss-00110
- iss-00109-worktree-docs-dogfooding-and-final-verification:
  - 目的:
    - shipped docs / dogfooding workspace / final validation を整え、Codex-managed worktree との境界と future extension を明文化する。
  - 成果物:
    - provider-side docs under `src/spec_dock/assets/spec_dock/docs/`
    - dogfooding workspace parity inspection
    - final runtime command smoke in temp repo
    - final `validate` / `sync` / `python -m unittest` or targeted runtime test evidence
    - epic `report.md` final E-AC status
  - tranche:
    - T3 rollout / close-out
  - closes:
    - E-RQ-008, E-RQ-009, E-RQ-010
    - E-AC-011
  - 依存:
    - iss-00108

## 統合チェックポイント
- G1 分解レビュー:
  - `iss-00110` plan が requirement / design の failure contract を全て testable に落としている。
  - `worktree create` が spec tree mutation と混ざっていない。
- G2 統合準備確認:
  - `iss-00110` 完了後、application result と port protocols が CLI output に十分な情報を持っている。
  - `bootstrap_status` の `skipped` / `succeeded` / `failed` / `detection_failed` が tests で区別されている。
- G3 ロールアウト / docs 影響:
  - `iss-00108` 完了後、CLI help と docs の command shape が `spec-dock worktree create [LABEL]` で一致している。
  - absolute path primary output が docs / tests に反映されている。
- G9 最終 Epic spec review:
  - `iss-00109` で E-AC-001..E-AC-011 の evidence を report に集約する。
  - provider-side source and dogfooding workspace parity を確認する。

## 品質ゲート
- test:
  - `python -m unittest discover -v` または runtime affected tests。
  - worktree creation tests は temp directory / temp Git repo を使い、live checkout へ worktree を作らない。
  - `make init` tests は stub `make` または controlled Makefile を使い、real project bootstrap を実行しない。
- observability:
  - CLI output contains id, branch, absolute worktree path, bootstrap status.
  - warnings use existing `CliText.warnings` path.
- migration:
  - No persisted SpecDock state migration.
  - Existing commands keep backward-compatible behavior.
- docs:
  - command help / shipped docs / dogfooding docs agree on scope and non-scope.
  - Codex-managed worktree is explicitly out of scope.

## ロールアウト / docs impact
- ロールアウト順序:
  1. Core use case and adapters.
  2. CLI command and output.
  3. Docs / dogfooding parity / final verification.
- 契約 / docs 更新:
  - Add a worktree command section to shipped workflow/reference docs.
  - Mention sibling container placement and no nested `.worktrees/`.
  - Mention optional / non-fatal `make init`.
  - Mention future extensions: list/status/remove/prune are out of scope.

## Issue 準備完了条件
- Issue に要求する最低条件:
  - Requirement / design references are linked in issue docs.
  - Each issue has concrete tests mapped to E-AC subset.
  - Each issue states whether it may create Git worktrees and how tests isolate them.
  - Each issue states cleanup expectations for temp repos/worktrees.
  - Each issue keeps provider-side source of truth first.

## 最終完了条件
- E-AC 完了:
  - E-AC-001..E-AC-011 have pass evidence in `report.md`.
- 統合 / ロールアウト完了:
  - Runtime command exists and passes targeted / full relevant tests.
  - Shipped assets and dogfooding workspace are inspected.
  - `./spec-dock/scripts/spec-dock validate` and `./spec-dock/scripts/spec-dock sync` pass.
- docs 影響解決:
  - Provider docs and dogfooding docs show the same command contract.
  - No stale wording suggests nested `.worktrees/` or Codex-managed worktree replacement.

## 依存 / ブロッカー
- D-001:
  - Existing runtime layered architecture must remain intact.
- D-002:
  - Git CLI must be available for runtime command behavior.
- D-003:
  - `make` availability is optional; missing or failed bootstrap must not block worktree creation.
- D-004:
  - `epic-00054` and other runtime command work may touch parser / registry / presentation files; avoid overlapping edits in concurrent implementation worktrees.

## 未確定事項
- なし。
