---
種別: interview
ID: "20260530t112038z-interview"
タイトル: "External worktree post remove cleanup interview"
状態: "answered"
作成者: "Codex"
最終更新: "2026-05-30"
親: ["iss-00143"]
関連:
  - "iss-00137"
scope: "issue"
scope_id: "iss-00143"
created_at: "2026-05-30T11:20:38Z"
created_by_role: "orchestrator"
status: "answered"
adoption_status: "adopted"
reflected_to: []
derived_from:
  - "spec-dock/active/issue/discussions/20260530t000000z-scratch-external-worktree-management.md"
  - "spec-dock/active/issue/discussions/20260530t100431z-research-external-worktree-requirement-analysis.md"
  - "spec-dock/active/issue/discussions/20260530t100431z-01-interview-external-worktree-remove-scope.md"
  - "spec-dock/active/issue/discussions/20260530t111421z-interview-worktree-root-requirement-for-external-management.md"
  - "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00107-worktree-provisioning/issues/iss-00137-worktree-list-show-delete-commands/discussions/20260529t012346z-interview-worktree-delete-dirty-guard-interview.md"
intended_targets:
  - "spec-dock/active/issue/requirement.md"
  - "spec-dock/active/issue/report.md"
---

# 20260530t112038z-interview External worktree post remove cleanup interview

## 正式質問として扱う理由

- 影響する artifact:
  - `requirement.md`:
    - `worktree remove` 成功後に Git 管理外 file / cache / directory を削除対象に含めるかを決める。
  - `design.md`:
    - Git-first removal 後の filesystem cleanup と containment guard を決める。
  - `plan.md`:
    - post-remove directory cleanup tests と destructive safety tests を決める。
  - `report.md`:
    - destructive cleanup の user-approved evidence を記録する。
- chat 上の軽微な一問では足りない理由:
  - Git worktree record の削除だけでなく filesystem tree の削除まで行うかは、破壊的 command の範囲そのものに関わる。

## 質問の目的

- 対象者:
  - iwasawayuuta
- 何を明確にする質問か:
  - unmanaged / external worktree でも、Git remove 成功後に残った directory を spec-dock が削除するか。
- 回答が後続判断へ与える影響:
  - cleanup の受け入れ条件、safety guard、JSON result の `removed_directory`、tests が決まる。

## 質問

外部ツールが作成した unmanaged worktree についても、`git worktree remove` が成功した後に worktree path が残っている場合、spec-dock がその directory を削除してよいですか？

回答は、次のどちらを採用するかでお願いします。

- Option A:
  - managed / unmanaged を問わず、対象が main/current/bare/stale ではなく、Git remove が成功した worktree path なら、残った directory を filesystem cleanup する。
  - cleanup は resolved target path のみを対象にし、parent directory や root namespace は削除しない。
  - `removed_directory` は cleanup の実績を JSON で返す。
- Option B:
  - unmanaged / external worktree では Git record removal だけを行い、残った directory は削除しない。
  - managed worktree のみ現行どおり残 directory cleanup を行う。

## source-grounded context

- 先行 `iss-00137` では、managed worktree について Git remove 成功後に individual worktree directory が残る場合は cleanup する user-approved 判断だった。
- 今回 Option A により remove 対象は all linked worktrees へ広がった。
- `SPEC_DOCK_WORKTREE_ROOT` は `list/show/remove` で不要になったため、external worktree の containment guard は central root ではなく resolved target / main/current guards を中心に再設計する必要がある。
- 現行 JSON result は `removed_record`、`removed_directory`、`branch_deleted=false` を返す。

## Codex の分析

- Option A の利点:
  - cleanup command として一貫し、Codex Desktop generated worktree に残った cache / generated files も片付けられる。
  - managed / unmanaged で削除後の期待結果が分かれない。
- Option A のリスク:
  - central root 外の path を削除するため、resolved target が本当に Git worktree record 由来で main/current ではないことを厳密に守る必要がある。
  - symlink や unexpected path の扱いを design で明確にする必要がある。
- Option B の利点:
  - spec-dock が作っていない filesystem tree を削除しないため安全側。
- Option B のリスク:
  - issue の cleanup 目的が半分しか満たせず、operator が手動で残 directory を消す必要が残る。

## Codex の推奨案

- 推奨:
  - Option A。
- 理由:
  - この issue の目的が external worktree cleanup であるなら、Git record だけ消して directory / cache が残る状態は実用上の片付けとして不十分。Git worktree record に基づいて target を解決し、main/current/bare/stale を拒否し、resolved target path のみに限定すれば破壊範囲は requirement と design で制御できる。
- 未回答時の影響:
  - remove 成功時の期待結果と JSON result を確定できない。

## ユーザー回答

- 回答:
  - Option A を採用する。
  - managed / unmanaged を問わず、対象が main checkout、current checkout、bare worktree、stale record ではなく、Git remove が成功した worktree path なら、残った directory を filesystem cleanup する。
  - cleanup は resolved target path のみを対象にし、parent directory や root namespace は削除しない。
  - `removed_directory` は cleanup の実績を JSON で返す。
- 回答日時:
  - 2026-05-30

## 追加確認の要否

- 追加確認が必要か:
  - yes
  - symlink / path containment の詳細は design で固定する。

## 採用判断

- adoption_status:
  - adopted
- 採用 / 棄却 / deferred の理由:
  - external worktree cleanup を目的とする issue では、Git record removal だけで directory / cache が残ると利用者の cleanup 目的を満たしにくい。Git worktree record から解決した target path に限定し、main/current/bare/stale を拒否することで破壊範囲を制御する。

## requirement / design / plan / ADR への含意

- `requirement.md`:
  - `worktree remove` は managed / unmanaged を問わず、Git remove 成功後に resolved target path が残る場合は filesystem cleanup する。
  - cleanup は target worktree path のみを対象にし、parent directory、central root、namespace directory は削除しない。
  - JSON result は `removed_record` と `removed_directory` を返す。
- `design.md`:
  - Git-first remove の成功後だけ filesystem cleanup を実行する。
  - containment guard は resolved target path に限定し、main/current/bare/stale を拒否した後に cleanup する。
- `plan.md`:
  - unmanaged worktree の Git remove 成功後に remaining directory / cache を削除する test を追加する。
  - parent directory が残ることを検証する test を追加または既存 cleanup test に含める。
- `ADR`:
  - 現時点では不要見込み。
