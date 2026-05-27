---
種別: research
ID: "20260526t081259z-research"
タイトル: "Existing Worktree Contract Research"
状態: "draft | completed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-05-26"
親: ["iss-00130"]
関連: []
authority: "synthesized"
derived_from: []
reflected_to: []
---

# 20260526t081259z-research Existing Worktree Contract Research

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、判断への含意を混ぜない。

## 調査目的 (必須)
- 現行 `spec-dock worktree create` の placement / naming / bootstrap / failure contract を確認し、central worktree root 化でどの契約を変更する必要があるかを明らかにする。
- この PC の directory layout と shell environment を確認し、`/Users/iwasawayuuta/workspace/worktrees` を default operational root とする妥当性と未設定 env var の扱いを整理する。

## 調査方法 (必須)
- Active context:
  - `./spec-dock/scripts/spec-dock active show`
  - `spec-dock/active/context-pack.md`
  - `spec-dock/active/epic/{requirement.md,design.md,plan.md}`
  - `spec-dock/active/issue/{requirement.md,design.md,plan.md}`
- Current implementation / tests / docs:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/worktree.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
  - `tests/cli_runtime/test_worktree.py`
  - `src/spec_dock/assets/spec_dock/docs/reference_worktree.md`
- Local environment / filesystem:
  - `git worktree list --porcelain`
  - `find /Users/iwasawayuuta/workspace -maxdepth 2 -type d`
  - `printenv | sort | rg 'WORKTREE|SPEC_DOCK|CODEX_HOME|WORKSPACE'`
  - `rg -n 'WORKTREE|SPEC_DOCK|workspace|worktrees' ~/.zshrc ~/.zprofile ~/.zshenv`

## 調査結果 (必須)
- Active issue:
  - Current active tuple is `init-local-00002` / `epic-00107` / `iss-00130`.
  - `iss-00130` docs are still template-level draft at the start of this research.
- Existing Epic contract:
  - `epic-00107` is approved and currently states sibling placement as the required contract:
    - container: main checkout parent / `<repo-basename>-worktrees`
    - worktree path: `<repo-basename>-worktrees/<repo-basename>-<id>`
    - branch: `<current-branch>-<id>`
    - linked worktree execution normalizes placement to Git's main worktree path.
  - Therefore `iss-00130` is a contract-changing issue, not just an implementation cleanup.
- Current implementation:
  - `application/worktree.py` computes:
    - `main_worktree = records[0].path`
    - `repo_basename = main_worktree.name`
    - `container = main_worktree.parent / f"{repo_basename}-worktrees"`
    - `worktree_path = container / f"{repo_basename}-{worktree_id}"`
  - `WorktreeCreateRequest` currently only carries `label`; there is no env-derived root, explicit root, or namespace field.
  - `WorktreeCreateResult` exposes `container_path` and `worktree_path`, so output and tests can observe the new root.
  - `GitGateway` and `BootstrapGateway` do not currently expose environment lookup. Env lookup likely needs a new port/protocol or runtime configuration gateway rather than being embedded in CLI/parser code.
- Current tests:
  - `test_worktree_create_uses_sibling_container_auto_id_and_branch` asserts sibling path `target.parent / "sample-repo-worktrees" / "sample-repo-wt1"`.
  - invalid labels currently assert that sibling container is not created.
  - bootstrap success/failure tests assume sibling container when checking `.init-ran` and worktree existence.
  - linked-worktree normalization test asserts that a nested call from an existing linked worktree creates another worktree in the same sibling container.
  - Several unit-style fake gateway tests hard-code `Path(tmp) / "repo-worktrees" / "repo-wt1"` as the known record path.
  - These tests will need to change from sibling placement to env-root placement and add missing-env failure coverage.
- Current docs:
  - `reference_worktree.md` explicitly states that the command creates `<repo-basename>-worktrees/` next to the main checkout and does not use nested `.worktrees/`.
  - The docs explicitly separate spec-dock managed long-lived worktrees from Codex app `$CODEX_HOME/worktrees`.
- Current local worktree state:
  - `git worktree list --porcelain` currently shows main checkout at `/Users/iwasawayuuta/workspace/tools/spec-dock` and one linked worktree at `/Users/iwasawayuuta/workspace/tools/spec-dock-worktrees/spec-dock-delegated-authoring-architecture`.
  - This is the exact sibling-container shape that causes Codex sandbox writable-root friction.
- Local directory structure:
  - Development checkouts are broadly under `/Users/iwasawayuuta/workspace/` with category directories such as `product`, `tools`, `project`, `python`, `rails`, `mcp`, `learning`, `javascript`.
  - There is currently no `/Users/iwasawayuuta/workspace/worktrees` in the observed max-depth listing.
  - `/Users/iwasawayuuta/.codex/worktrees` exists and contains Codex-managed short names like `79f3` and `c2d5`.
- Current shell environment:
  - No `WORKTREE`, `SPEC_DOCK`, `CODEX_HOME`, or `WORKSPACE` worktree-root env var was present in the current process environment.
  - `~/.zshrc`, `~/.zprofile`, and `~/.zshenv` did not contain a worktree-root variable. `~/.zshrc` contains a workspace-related PATH entry only.

## 推測 / 未検証事項 (必須)
- 推測:
  - Env lookup belongs in an application port or runtime config abstraction so tests can exercise missing/present/malformed env without mutating process-global environment in core unit tests.
  - The user likely wants the new env var to be required only for `spec-dock worktree create`, not for unrelated spec-dock commands.
  - `SPEC_DOCK_WORKTREE_ROOT` is safer than a generic `WORKTREE_ROOT` because it avoids colliding with other tools, but the user's phrase "worktree root" may imply a generic name. This needs interview confirmation.
- 未検証:
  - Whether the implementation should automatically create the env root directory when the env var is set but missing.
  - Whether namespace should always be exactly `main_worktree.name`, or be configurable for repos whose directory basename is not the product name.
  - Whether existing sibling worktrees should be migrated, left untouched, or only documented as legacy.
  - Whether `spec-dock update .` should install or suggest shell profile configuration. Current user wording suggests local environment setup, but packaging cross-shell setup is not yet confirmed.

## 判断への含意 (必須)
- Requirements must explicitly supersede Epic E-RQ-002 for this issue: placement becomes env-root based rather than sibling container based.
- Missing env var must be a fatal precondition failure for `worktree create`. It should not silently fallback to sibling placement, because fallback would recreate the sandbox-permission problem.
- The central root should not be `$CODEX_HOME/worktrees` because current docs reserve that for Codex app managed short-lived worktrees and mixing lifecycles would blur ownership.
- `/Users/iwasawayuuta/workspace/worktrees` is the best local operational value for this PC because it keeps development assets under the visible `workspace` tree while isolating temporary linked worktrees from normal product checkout lifecycles.
- Namespace contract must be settled before canonical requirement promotion. Using only repo basename is simple and matches user preference for `spec-dock`, but can collide if multiple products share the same basename in different category directories.
- Existing individual worktree id / branch naming can mostly remain unchanged; the main change is container path:
  - before: `<main-parent>/<repo>-worktrees/<repo>-<id>`
  - proposed: `$<env>/<namespace>/<repo>-<id>`

## リスク/制約 (任意)
- Changing the default placement breaks existing tests and docs by design.
- Env-var-required behavior may be surprising for existing users unless docs and error text give a concrete setup example.
- Generic env var naming may collide with other development tools; tool-specific naming reduces ambiguity.
- Automatic directory creation is convenient but can hide typoed env var paths unless output clearly reports the root and created namespace.

## 反映先 (任意)
- reflected_to:
  - `requirement.md` after interview answers.
  - `design.md` for env gateway / namespace / path derivation.
  - `plan.md` for test slices covering missing env, present env, namespace path, collision behavior, docs update.

## 参考（References） (任意)
- `spec-dock/active/context-pack.md`
- `spec-dock/active/epic/requirement.md`
- `spec-dock/active/epic/design.md`
- `spec-dock/active/epic/plan.md`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/worktree.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
- `tests/cli_runtime/test_worktree.py`
- `src/spec_dock/assets/spec_dock/docs/reference_worktree.md`
