---
種別: research
ID: "20260529t002625z-research"
タイトル: "Worktree list show delete existing contract research"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-05-29"
親: ["iss-00137"]
関連: []
authority: "synthesized"
derived_from:
  - "spec-dock/active/issue/discussions/20260529t000036z-disc-worktree-list-show-delete-command-scope-memo.md"
  - "spec-dock/active/epic/requirement.md"
  - "spec-dock/active/epic/design.md"
  - "spec-dock/active/epic/plan.md"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/worktree.py"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py"
  - "src/spec_dock/assets/spec_dock/docs/reference_worktree.md"
  - "tests/cli_runtime/test_worktree.py"
reflected_to:
  - "spec-dock/active/issue/requirement.md"
---

# 20260529t002625z-research Worktree list show delete existing contract research

## 調査目的 (必須)
- `iss-00137` の要件定義前に、既存 `worktree create` の contract、実装境界、テスト先例、docs 上の future extension 表現を確認し、`worktree list` / `show` / `delete` の要件へ採用できる事実と、人間判断が必要な論点を分離する。

## sources / 調査方法 (必須)
- 参照先:
  - `spec-dock/active/issue/discussions/20260529t000036z-disc-worktree-list-show-delete-command-scope-memo.md`
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/design.md`
  - `spec-dock/active/epic/plan.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/worktree.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py`
  - `src/spec_dock/assets/spec_dock/docs/reference_worktree.md`
  - `tests/cli_runtime/test_worktree.py`
- 検証手順:
  - `./spec-dock/scripts/spec-dock active show` で active issue が `iss-00137` であることを確認した。
  - `rg --files` / `rg -n "worktree"` で既存実装、docs、tests の配置を確認した。
  - 上記 source files を読み、既存 contract と今回の追加 command の境界を整理した。
- 実験条件:
  - 2026-05-29 JST、worktree `/Users/iwasawayuuta/workspace/worktrees/spec-dock/spec-dock-worktree-list-show-delete`。
  - この research では runtime command の実行テストは未実施。要件定義前の source-grounded read に限定した。

## facts / 観測できた事実 (必須)
- active issue は `iss-00137-worktree-list-show-delete-commands`。`requirement.md` はテンプレート状態で、正式要件は未作成。
- issue-local memo は `worktree list`、`worktree show <target>`、`worktree delete <target>` を追加候補にしている。未決論点は target 指定方法、managed scope、delete の意味、output contract、`delete` / `remove` naming。
- 親 epic の正本は `worktree create` を中心に、`SPEC_DOCK_WORKTREE_ROOT/<repo-basename>/` central root namespace、`<repo-basename>-<id>` path、`<current-branch>-<id>` branch、optional / non-fatal `make init` を定義している。
- `src/spec_dock/assets/spec_dock/docs/reference_worktree.md` は現時点で `worktree list`、`status`、`remove`、`prune`、Codex-managed worktree cleanup を future extension と明記している。
- `commands/worktree.py` は現在 `worktree_create` だけを登録し、CLI parser も `worktree create` だけを leaf command として bind している。
- `application/worktree.py` は `worktree_create` の use case を持ち、candidate id、central root validation、main worktree normalization、directory / branch / Git worktree record collision、`git worktree add -b`、bootstrap result aggregation を application 層で扱う。
- `infra/git_cli.py` には `git worktree list --porcelain` parser と `git worktree add -b` adapter がある。porcelain parser は path、HEAD、branch、detached、bare を `GitWorktreeRecord` として扱う。
- `application.ports.GitGateway` には `worktree_list` と `add_worktree_with_new_branch` があるが、worktree remove/delete/prune や dirty check、ahead/unpushed branch check はまだない。
- `WorktreeCreateResult` は `id`、`main_worktree_path`、`container_path`、`worktree_path`、`branch_name`、bootstrap 情報を持つ。list/show/delete 用の result contract はまだない。
- `presentation/cli_text.py` の create output は `spec-dock: ok (worktree create) id=... branch=... path=...` と bootstrap status の二行。
- `tests/cli_runtime/test_worktree.py` は temp Git repo と temp central root を使い、live checkout を破壊しない形で worktree behavior を検証している。

## inference / 推測 (必須)
- 事実から推測したこと:
  - `list` / `show` は既存 `GitWorktreeRecord` と central root namespace contract を拡張すれば、SpecDock 永続 state を追加せずに実装できる可能性が高い。
  - `delete` は `git worktree remove` だけでも破壊的操作であり、dirty worktree、current checkout、main checkout、untracked files、locked worktree、missing path/stale record などを要件で先に固定する必要がある。
  - branch deletion を同時に扱うと、Git worktree 削除と Git branch lifecycle の二つの責務を一つの command に混ぜるため、初回 issue の scope とテスト量が増える。
  - 既存 docs が future extension に `remove` と書いている一方、issue memo は `delete` を望んでいるため、user-facing command 名は正式要件で明示する必要がある。
- 推測の根拠:
  - 既存 create は SpecDock tree mutation や active pointer を触らず、Git metadata を source of truth にしている。
  - `git worktree list --porcelain` の adapter がすでにあるため、list/show の観測情報は追加 adapter なしでも一部取得できる。
  - 削除系 adapter と safety guard はまだ存在しないため、削除 contract を曖昧なまま実装すると危険側へ振れやすい。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - `git worktree list --porcelain` が locked / prunable / bare / detached などの状態を現行 parser でどこまで保持できるか。
  - `git worktree remove` の dirty / locked / missing path / stale record に対する stderr と exit code の実例。
  - branch が upstream より ahead か、未 push かをこの issue の delete guard に含めるべきか。
  - `worktree list` に JSON output を入れる必要があるか。
- 確認できない理由:
  - 要件定義前であり、削除 scope と output contract が未確定。実験は次の research または design 前調査で対象を絞って実施する。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - `delete` vs `remove`
  - `managed worktree` vs `Git linked worktree`
  - `id` vs directory basename vs branch name vs path
- 既存 docs / code / tests / discussions での使われ方:
  - `reference_worktree.md` は future extension として `remove` を挙げる。
  - issue memo は user-facing command として `delete` を挙げる。
  - create contract の `id` は `wt1` または `<label>` / `<label>N` で、path は `<repo-basename>-<id>`、branch は `<current-branch>-<id>`。
- 判断が必要な理由:
  - command 名と target resolution は CLI contract、help、docs、tests、ユーザーの mental model に直接影響する。

## edge cases / 具体シナリオ (必須)
- edge case:
  - main checkout が target になった。
  - command 実行中の current checkout が target になった。
  - central root namespace 内に directory はあるが Git worktree record がない。
  - Git worktree record はあるが path が存在しない。
  - target string が path / basename / branch の複数に一致する。
  - target worktree に uncommitted changes または untracked files がある。
  - target branch が local only、または upstream より ahead。
  - locked worktree が target になった。
- その edge case が requirement / design / plan に与える影響:
  - safety guard、fatal error message、disambiguation、`--force` / `--yes` の有無、branch deletion を scope に入れるかが受け入れ条件とテストケースになる。

## implications / 判断への含意 (必須)
- requirement では、少なくとも `managed scope`、`target resolution`、`delete safety guard`、`branch deletion non-scope or option`、`output minimum fields` を明文化する必要がある。
- design では、既存 `worktree_create` と同じ layered architecture に沿い、commands/application/infra/presentation/tests の責務を分ける必要がある。
- plan では、`list/show` の read-only behavior slice と `delete` の destructive behavior slice を分け、delete は Red/Green と safety guard review を厚めにする必要がある。
- ADR は現時点では不要。`delete` と `remove` の naming や branch deletion default は重要だが、issue-local requirement/design で十分に扱える見込み。

## リスク/制約 (任意)
- 削除 command は実ファイルシステムと Git metadata を変更するため、temp Git repo / temp worktree root での hermetic tests が必須。
- Codex-managed `$CODEX_HOME/worktrees` の cleanup は既存 epic の対象外であり、この issue で混ぜると scope creep になる。
- provider-side source of truth は `src/spec_dock/assets/spec_dock/...`。dogfooding `spec-dock/...` は確認・反映対象。

## 反映先 (任意)
- reflected_to:
  - `requirement.md` draft after interview answers
  - `design.md` / `plan.md` after requirement review

## 参考（References） (任意)
- `spec-dock/docs/workflow_clarification.md`
- `spec-dock/docs/workflow_issue.md`
