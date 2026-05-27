---
種別: research
ID: "20260526t082342z-research"
タイトル: "Shell Environment Setup Research"
状態: "draft | completed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-05-26"
親: ["iss-00130"]
関連: []
authority: "synthesized"
derived_from: []
reflected_to: []
---

# 20260526t082342z-research Shell Environment Setup Research

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、判断への含意を混ぜない。

## 調査目的 (必須)
- `SPEC_DOCK_WORKTREE_ROOT` をこの開発環境のどの zsh startup file に置くべきかを、既存 local configuration の役割から確認する。
- Workspace 外編集が必要な場合に、要件・計画へどのように approval と evidence を組み込むべきかを整理する。

## 調査方法 (必須)
- Read-only inspection:
  - `/Users/iwasawayuuta/.zshenv`
  - `/Users/iwasawayuuta/.zprofile`
  - `/Users/iwasawayuuta/.zshrc`
- Secret hygiene:
  - `.zshrc` contains secret-looking exports, so this research records only structural facts relevant to startup-file placement and does not copy secret values.

## 調査結果 (必須)
- `.zshenv`:
  - Contains a small set of environment variables that should be available broadly to zsh sessions.
  - Existing examples include cache/root path variables and `WORKSPACE_SECRETS_HOME`.
  - This makes `.zshenv` a good fit for `SPEC_DOCK_WORKTREE_ROOT`, because `spec-dock worktree create` may be run from non-login shells or tool-launched shells where `.zprofile` is not sourced.
- `.zprofile`:
  - Contains login-shell setup such as PATH additions, Java path, Homebrew preference, and OrbStack shell integration.
  - It is less suitable for a required env var that should be visible to CLI invocations independent of login shell behavior.
- `.zshrc`:
  - Contains interactive shell configuration and many user-specific exports.
  - It is not the preferred target for this issue because `spec-dock worktree create` can be run from scripts or non-interactive contexts.
- Current state:
  - `SPEC_DOCK_WORKTREE_ROOT` is not yet defined.
  - `/Users/iwasawayuuta/workspace/worktrees` was not observed in the workspace directory listing before setup.
- User-confirmed setup scope:
  - This issue should include local machine setup.
  - The setup target should be `.zshenv`.
  - Editing `.zshenv` is outside the repository workspace and requires user approval at execution time.

## 推測 / 未検証事項 (必須)
- 推測:
  - Adding `export SPEC_DOCK_WORKTREE_ROOT="${SPEC_DOCK_WORKTREE_ROOT:-$HOME/workspace/worktrees}"` to `.zshenv` is preferable to a hard-coded absolute home path because it preserves the user's existing override and remains readable.
  - Creating `/Users/iwasawayuuta/workspace/worktrees` can be treated as local setup evidence, not as a repository artifact.
- 未検証:
  - Whether Codex Desktop sessions launched before `.zshenv` change will inherit the new env var without restart.
  - Whether the user wants a literal absolute path export or `$HOME/workspace/worktrees` expression in `.zshenv`.

## 判断への含意 (必須)
- Requirement should state that this issue includes local setup for the current development machine:
  - create `/Users/iwasawayuuta/workspace/worktrees`
  - add `SPEC_DOCK_WORKTREE_ROOT` export to `.zshenv`
  - request approval before editing outside workspace
- Design should separate:
  - runtime behavior: read required env var and derive central path
  - local setup evidence: directory/profile update for this machine
- Plan should include a manual/local setup step with approval and verification:
  - inspect existing `.zshenv`
  - update it after approval
  - verify a new shell sees `SPEC_DOCK_WORKTREE_ROOT`
  - verify directory exists
- This local setup should not be treated as a checked-in repo file change.

## リスク/制約 (任意)
- Editing user shell startup files is outside the repo and can affect future shells. It must be explicit, narrow, and approval-gated.
- `.zshenv` is sourced by many zsh invocations; the added line must be simple, fast, and side-effect free.
- Do not place commands that create directories inside `.zshenv`; directory creation should be a one-time setup action, not a shell startup side effect.

## 反映先 (任意)
- reflected_to:
  - `requirement.md` local setup scope / approval requirement.
  - `design.md` environment and setup boundary.
  - `plan.md` local setup step.

## 参考（References） (任意)
- `/Users/iwasawayuuta/.zshenv`
- `/Users/iwasawayuuta/.zprofile`
- `/Users/iwasawayuuta/.zshrc` structural inspection only; no secret values copied.
