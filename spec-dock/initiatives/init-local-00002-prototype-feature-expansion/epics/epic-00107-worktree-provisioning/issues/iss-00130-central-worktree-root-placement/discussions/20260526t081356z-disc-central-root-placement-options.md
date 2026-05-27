---
種別: disc
ID: "20260526t081356z-disc"
タイトル: "Central Root Placement Options"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-05-26"
親: ["iss-00130"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260526t081356z-disc Central Root Placement Options

## 位置づけ
- 用途: 集まった情報をもとに、論点、評価軸、選択肢、合意点/未合意点を整理する。
- authority default: `proposed`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- 人間から回答を引き出し、回答欄や未回答事項を管理する場合は `interview` を使う。
- 生ログや未整理の思考は `scratch`、事実確認や外部根拠は `research`、長期判断の固定は `adr` に分ける。
- doc が大きくなりすぎたら、質問回答は `interview`、事実調査は `research`、raw capture は `scratch`、長期決定は `adr` へ分割する。

## 議題 (必須)
- `spec-dock worktree create` の placement を、repo sibling container から environment-provided central root へ変える。
- Central root 配下で product namespace をどう決めるか。
- Missing env var をどう扱うか。
- Existing per-worktree naming logic を維持するか、調整するか。

## 背景 (必須)
- User goal:
  - Codex sandbox writable root を project ごとに手動追加する運用をなくす。
  - 通常 product checkout と短命 linked worktree の lifecycle を分離し、すべての product の worktree を一箇所で見えるようにする。
  - この PC では `/Users/iwasawayuuta/workspace/worktrees` を worktree root として用意し、zsh profile で shell environment variable に設定する。
- Current contract:
  - Existing placement is `<main-worktree-parent>/<repo-basename>-worktrees/<repo-basename>-<id>`.
  - Existing branch naming is `<current-branch>-<id>`.
  - Existing label/id logic is `wt1`, `wt2`, ... or `<label>`, `<label>2`, ...

## 選択肢 (必須)
- Option A: Tool-specific env var + central root
  - Pros:
    - Env var ownership is clear: `SPEC_DOCK_WORKTREE_ROOT`.
    - Missing env var can fail-fast with exact setup guidance.
    - Low risk of colliding with unrelated tools.
  - Cons:
    - Longer name; other tools will not automatically share it.
- Option B: Generic env var + central root
  - Pros:
    - Env var is short: `WORKTREE_ROOT`.
    - Could be shared by multiple local tools if the user wants one convention.
  - Cons:
    - Ownership and semantics are ambiguous.
    - Higher collision risk with unrelated scripts.
- Option C: Central root with fallback to sibling placement
  - Pros:
    - Backward-compatible for users who have not configured env vars.
  - Cons:
    - Missing env var recreates the exact sandbox-permission problem.
    - User explicitly asked for no worktree creation when env var is missing.
- Option D: Reuse `$CODEX_HOME/worktrees`
  - Pros:
    - Already exists on this machine.
  - Cons:
    - Current docs reserve it for Codex app managed short-lived worktrees.
    - Mixes spec-dock managed manual worktrees with Codex app lifecycle and cleanup expectations.

## 推奨案 (必須)
- Recommended option: A, `SPEC_DOCK_WORKTREE_ROOT`.
- Local setup example:
  - `export SPEC_DOCK_WORKTREE_ROOT=/Users/iwasawayuuta/workspace/worktrees`
- Proposed path shape:
  - `$SPEC_DOCK_WORKTREE_ROOT/<namespace>/<repo-basename>-<id>`
  - This repo:
    - `/Users/iwasawayuuta/workspace/worktrees/spec-dock/spec-dock-<id>`
  - Label example:
    - `/Users/iwasawayuuta/workspace/worktrees/spec-dock/spec-dock-central-root`
  - Branch remains:
    - `<current-branch>-<id>`
- Rationale:
  - Solves the Codex writable-root problem with one stable editable root.
  - Keeps spec-dock managed worktrees distinct from normal product checkouts and Codex app managed worktrees.
  - Keeps individual worktree names and branch names familiar.

## User-confirmed decisions
- 2026-05-26:
  - Env var name is `SPEC_DOCK_WORKTREE_ROOT`.
  - Missing env var is fatal for `worktree create`.
  - If env var is set but the root directory does not exist, the command may create the root and namespace directories.
  - Namespace is the Git main worktree basename. This repo uses `spec-dock`.
  - This issue includes local machine setup: create `/Users/iwasawayuuta/workspace/worktrees` and add the export to `.zshenv`, with user approval when editing outside workspace.
  - Existing sibling worktrees are left untouched.
  - Backward compatibility for future sibling placement is not required.

## Namespace analysis
- User preference:
  - Namespace is product name as-is.
  - For this repo, namespace is `spec-dock`.
- Simple rule:
  - Default namespace = Git main worktree basename.
  - This yields `spec-dock` for `/Users/iwasawayuuta/workspace/tools/spec-dock`.
- Collision risk:
  - If two different products share the same basename, both map to the same namespace.
  - Existing sibling placement avoided this by scoping the container to each repo parent; central root removes that implicit parent namespace.
- Possible mitigation:
  - Keep default namespace as repo basename for human readability.
  - Add override only later if a real collision or product-name mismatch appears.
  - Do not introduce `tools-spec-dock` now unless the user values collision avoidance more than product-name readability.

## Individual worktree naming analysis
- Keep existing id logic:
  - no label: `wt1`, `wt2`, ...
  - label: `<label>`, `<label>2`, ...
- Keep existing worktree directory basename:
  - `<repo-basename>-<id>`
- Keep existing branch:
  - `<current-branch>-<id>`
- Rationale:
  - Existing behavior is already covered by tests and docs.
  - Changing placement is enough to solve the sandbox and lifecycle problem.
  - Renaming individual worktrees beyond placement would increase migration and user relearning cost.

## 未決事項 (任意)
- Env var name:
  - Resolved: `SPEC_DOCK_WORKTREE_ROOT`.
- Root creation:
  - Resolved: command may create root / namespace when env var is set.
- Namespace:
  - Resolved: strictly repo basename for this issue.
- Legacy:
  - Resolved: leave untouched; no migration.
- Scope:
  - Resolved: include local setup; use `.zshenv`; request user approval for workspace-external edit.

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - After interview answers, promote accepted placement/env/namespace/failure requirements into `requirement.md`.
  - Then design env lookup / path derivation and plan targeted tests.
- 追加で作る discussion docs:
  - ADR only if central-root placement becomes a long-lived architecture decision that should supersede Epic E-RQ-002 beyond this issue.
