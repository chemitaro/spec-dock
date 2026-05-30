---
種別: research
ID: "20260530t100431z-research"
タイトル: "External worktree requirement analysis"
状態: "draft"
作成者: "Codex"
最終更新: "2026-05-30"
親: ["iss-00143"]
関連:
  - "iss-00137"
  - "epic-00107"
scope: "issue"
scope_id: "iss-00143"
created_at: "2026-05-30T10:04:31Z"
created_by_role: "orchestrator"
adoption_status: "unreviewed"
reflected_to: []
source_paths:
  - "spec-dock/active/issue/discussions/20260530t000000z-scratch-external-worktree-management.md"
  - "spec-dock/active/issue/requirement.md"
  - "spec-dock/active/epic/requirement.md"
  - "spec-dock/active/epic/design.md"
  - "spec-dock/active/epic/plan.md"
  - "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00107-worktree-provisioning/issues/iss-00137-worktree-list-show-delete-commands/discussions/20260529t012008z-interview-worktree-managed-scope-and-target-resolution-interview.md"
  - "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00107-worktree-provisioning/issues/iss-00137-worktree-list-show-delete-commands/discussions/20260529t012346z-interview-worktree-delete-dirty-guard-interview.md"
  - "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00107-worktree-provisioning/issues/iss-00137-worktree-list-show-delete-commands/discussions/20260529t014129z-interview-worktree-target-resolution-interview.md"
  - "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00107-worktree-provisioning/issues/iss-00137-worktree-list-show-delete-commands/discussions/20260529t014506z-interview-worktree-deletable-status-json-interview.md"
  - "src/spec_dock/assets/spec_dock/docs/reference_worktree.md"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py"
  - "tests/cli_runtime/test_worktree.py"
intended_targets:
  - "spec-dock/active/issue/requirement.md"
  - "spec-dock/active/issue/report.md"
---

# 20260530t100431z-research External worktree requirement analysis

## 調査目的

`iss-00143 Manage External Git Worktrees` の要件定義に入る前に、既存の `worktree list/show/remove` contract、先行 issue の user-approved 判断、今回の intake との差分を整理する。

## 確定事実

- active issue は `iss-00143 Manage External Git Worktrees`。
- issue-local `requirement.md` / `design.md` / `plan.md` は scaffold のままで、まだ implementation-ready ではない。
- intake memo は、Codex Desktop など spec-dock 以外が作成した Git worktree も、同一 repository に属するなら `list` / `show` / `remove` で扱いたい、としている。
- 現行 provider docs は、`worktree list` / `show` / `remove` を持つが、`remove` は SpecDock managed namespace 配下の linked worktree だけを対象にすると説明している。
- 現行 implementation は Git worktree records から inventory を作り、central root namespace 配下を `managed=true`、それ以外を `managed=false` と分類する。
- 現行 implementation は `unmanaged` を non-bypassable remove blocker として扱うため、`--force` でも unmanaged worktree を削除しない。
- 現行 tests は unmanaged worktree が `list --json` に出ることを検証しつつ、`remove --force` は unmanaged target を拒否することを検証している。
- 先行 `iss-00137` の interview では、user-approved な判断として「`list/show` は全 linked worktree を扱うが、`delete/remove` は managed worktree のみに限定する」が採用されていた。

## 今回の intake との衝突点

- intake は「remove any repository worktree」と述べており、先行判断の「unmanaged は remove しない」と衝突する。
- 親 epic の `E-RQ-011` / `E-AC-013` も managed remove を前提にしているため、今回の issue は親 epic の一部 contract を更新する変更になる可能性が高い。
- `list/show` はすでに概ね全 linked worktree を扱う方向にあるため、主な requirement gap は remove safety boundary と docs / tests の更新範囲。

## 要件に落とすべき論点

- `remove` の対象をどこまで広げるか:
  - 全 linked worktree を対象にするのか。
  - main checkout / current checkout / bare / path missing / record missing は引き続き拒否するのか。
  - unmanaged という分類は残すが blocker ではなく diagnostic にするのか。
- Codex Desktop が作る worktree の扱い:
  - `Git worktree record に存在する同一 repository の linked worktree` という一般条件で扱うのか。
  - `$CODEX_HOME/worktrees` を特別扱いするのか。
  - Codex Desktop 固有の cleanup / Handoff / env setup は scope 外にするのか。
- `SPEC_DOCK_WORKTREE_ROOT` の扱い:
  - 現行 `list/show/remove` は managed classification と target diagnostics のため必須にしている。
  - 全 linked worktree remove へ広げる場合も、central root env を必須のままにするか、classification optional にするかを決める必要がある。
- 削除後 cleanup:
  - managed worktree では Git remove 成功後に individual worktree directory が残れば filesystem cleanup する。
  - unmanaged worktree でも同じ cleanup をする場合、削除対象 path の containment guard をどう定義するかが要件になる。

## 推奨する最初のヒアリング

最初に確認すべき質問は、`remove` の対象範囲を「同一 repo の全 linked worktree」まで広げるかどうか。

理由:

- この回答で requirement の目的、スコープ、非スコープ、受け入れ条件、例外条件が大きく変わる。
- 先行 user-approved 判断を変更するかどうかに直結する。
- `SPEC_DOCK_WORKTREE_ROOT` や cleanup containment の詳細は、この回答後に切り分けて聞ける。

## 現時点の仮説

推奨案は、`remove` も Git が認識する同一 repo の linked worktree 全体へ広げること。ただし main checkout / current checkout / bare / missing path / missing record は引き続き拒否し、branch deletion、prune / repair、Codex Handoff / env setup は scope 外にする。

この場合、`managed` は削除可否の blocker ではなく、origin / placement diagnostic として残すのが自然。

## 未確定事項

- Q-001:
  - `remove` の対象範囲を全 linked worktree に広げるか、managed-only を維持するか。
- Q-002:
  - 全 linked worktree に広げる場合、`SPEC_DOCK_WORKTREE_ROOT` を `list/show/remove` で引き続き必須にするか。
- Q-003:
  - unmanaged worktree の Git remove 成功後に path が残る場合、filesystem cleanup まで実施するか。
- Q-004:
  - Codex Desktop generated worktree を `$CODEX_HOME/worktrees` で特別扱いするか、Git linked worktree として一般化するか。
