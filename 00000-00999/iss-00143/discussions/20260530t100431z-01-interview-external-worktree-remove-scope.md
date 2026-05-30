---
種別: interview
ID: "20260530t100431z-interview"
タイトル: "External worktree remove scope interview"
状態: "answered"
作成者: "Codex"
最終更新: "2026-05-30"
親: ["iss-00143"]
関連:
  - "iss-00137"
scope: "issue"
scope_id: "iss-00143"
created_at: "2026-05-30T10:04:31Z"
created_by_role: "orchestrator"
status: "answered"
adoption_status: "adopted"
reflected_to: []
derived_from:
  - "spec-dock/active/issue/discussions/20260530t000000z-scratch-external-worktree-management.md"
  - "spec-dock/active/issue/discussions/20260530t100431z-research-external-worktree-requirement-analysis.md"
  - "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00107-worktree-provisioning/issues/iss-00137-worktree-list-show-delete-commands/discussions/20260529t012008z-interview-worktree-managed-scope-and-target-resolution-interview.md"
intended_targets:
  - "spec-dock/active/issue/requirement.md"
  - "spec-dock/active/issue/report.md"
---

# 20260530t100431z-interview External worktree remove scope interview

## 正式質問として扱う理由

- 影響する artifact:
  - `requirement.md`:
    - `worktree remove <target>` の対象範囲、禁止対象、受け入れ条件、例外条件を決める。
  - `design.md`:
    - `managed` / `unmanaged` の意味、remove guard、filesystem cleanup containment、JSON diagnostics を決める。
  - `plan.md`:
    - unmanaged / Codex Desktop generated worktree の remove tests と safety tests を決める。
  - `report.md`:
    - 先行 `iss-00137` の user-approved 判断を変更する場合の adoption / decision evidence を記録する。
- chat 上の軽微な一問では足りない理由:
  - 先行 issue では「remove は managed のみ」が user-approved だったが、今回の intake は「remove any repository worktree」を求めている。破壊的 command の scope と安全境界を再確定する必要がある。

## 質問の目的

- 対象者:
  - iwasawayuuta
- 何を明確にする質問か:
  - `worktree remove` を、SpecDock managed namespace 配下だけでなく、Codex Desktop など外部ツールが作成した同一 repo の linked worktree まで広げるかどうか。
- 回答が後続判断へ与える影響:
  - requirement の目的、必須 scope、禁止 scope、AC / EC、既存 docs/tests の変更方針が決まる。

## 質問

今回の `iss-00143` では、`spec-dock worktree remove <target>` の対象を **Git が認識する同一 repository の linked worktree 全体** に広げますか？

回答は、次のどちらを採用するかでお願いします。

- Option A:
  - `list/show/remove` すべてを同一 repo の全 linked worktreeへ広げる。
  - `managed` / `unmanaged` は diagnostic として残すが、`unmanaged` は remove blocker ではなくする。
  - main checkout、current checkout、bare worktree、path missing / record missing は引き続き拒否する。
  - branch deletion、`prune` / `repair`、Codex Desktop Handoff / env setup は scope 外にする。
- Option B:
  - 先行 `iss-00137` の判断を維持し、`list/show` は全 linked worktreeを扱うが、`remove` は managed worktree のみに限定する。
  - Codex Desktop など外部作成 worktree は visibility 対象だが cleanup 対象にはしない。

## source-grounded context

- 確認済みの docs / code / tests:
  - `iss-00143` intake memo は、Codex Desktop が spec-dock とは独立に Git worktree を作成するため、同一 repo の worktree を一つの command surface で inspect / cleanup したいとしている。
  - 現行 `reference_worktree.md` は、`remove` を SpecDock managed namespace 配下に限定している。
  - 現行 `application/worktree.py` は `unmanaged` を non-bypassable remove blocker として扱う。
  - 現行 `tests/cli_runtime/test_worktree.py` は unmanaged worktree の `remove --force` が拒否されることを期待している。
  - 先行 `iss-00137` interview では Option B 相当が user-approved だった。
- local context で解決できたこと:
  - `list/show` はすでに Git worktree records 全体を扱える。
  - `remove` の破壊的 scope を広げるには、要件で安全境界を明確にする必要がある。
  - branch deletion は既存 contract でも `branch_deleted=false` であり、今回も scope 外にできる。
- まだ人間判断が必要な理由:
  - これは既存 user-approved safety contract の変更であり、誤削除リスクと運用効率のトレードオフをプロダクト方針として決める必要がある。

## Codex の分析

- Option A の利点:
  - intake の「remove any repository worktree」に素直に一致する。
  - Codex Desktop generated worktree も spec-dock command で cleanup できる。
  - `managed` は ownership ではなく placement/origin diagnostic として残せる。
- Option A のリスク:
  - 外部ツールが作った worktree の lifecycle まで spec-dock が触るため、remove guard と docs の言葉を慎重にする必要がある。
  - unmanaged path の filesystem cleanup を行う場合、containment guard の設計が追加で必要になる。
- Option B の利点:
  - 先行合意と現行実装に近く、安全。
  - provider docs / tests の変更が小さい。
- Option B のリスク:
  - 今回の intake の中心要求である、Codex Desktop generated worktree の cleanup が満たせない。

## Codex の推奨案

- 推奨:
  - Option A。
- 理由:
  - この issue は、先行 `iss-00137` の managed-only remove contract を見直すために作られていると読むのが自然。`main` / `current` / `bare` / stale record を拒否し、branch deletion や Codex-specific lifecycle を scope 外にすれば、同一 repo の external worktree cleanup という目的を満たしつつ破壊範囲を絞れる。
- 未回答時の影響:
  - requirement の必須 scope と受け入れ条件が確定できず、design / plan へ進めない。

## ユーザー回答

- 回答:
  - Option A を採用する。
  - `list/show/remove` すべてを同一 repository の全 linked worktree へ広げる。
  - `managed` / `unmanaged` は diagnostic として残すが、`unmanaged` は remove blocker ではなくする。
  - main checkout、current checkout、bare worktree、path missing / record missing は引き続き拒否する。
  - branch deletion、`prune` / `repair`、Codex Desktop Handoff / env setup は scope 外にする。
- 回答日時:
  - 2026-05-30

## 追加確認の要否

- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す候補:
  - 全 linked worktree remove を採用する場合、`SPEC_DOCK_WORKTREE_ROOT` を `list/show/remove` で引き続き必須にするか。
  - unmanaged worktree の Git remove 成功後に path が残る場合、filesystem cleanup まで行うか。

## 採用判断

- adoption_status:
  - adopted
- 採用 / 棄却 / deferred の理由:
  - 今回の issue は、Codex Desktop など spec-dock 外で作成された同一 repo の linked worktree を一つの command surface で inspect / cleanup することを目的にしている。先行 `iss-00137` の managed-only remove contract は安全だが、今回の intake の cleanup 要求を満たせないため、`unmanaged` を remove blocker から diagnostic へ変更する。

## requirement / design / plan / ADR への含意

- `requirement.md`:
  - `worktree list` / `show` / `remove` は Git が認識する同一 repo の linked worktree 全体を対象にする。
  - `managed` / `unmanaged` は表示・JSON diagnostic として残す。
  - `unmanaged` は remove blocker ではない。
  - main checkout、current checkout、bare worktree、path missing / record missing は remove blocker として残す。
  - branch deletion、`prune` / `repair`、Codex Desktop Handoff / env setup は scope 外にする。
- `design.md`:
  - remove guard から `unmanaged` blocker を外し、managed classification は diagnostic / placement classification として維持する。
  - target resolver は同一 repo の全 linked worktree inventory を対象にする。
- `plan.md`:
  - unmanaged linked worktree の remove 成功テストを追加する。
  - main/current/bare/stale record を拒否する safety tests を維持または更新する。
- `ADR`:
  - 現時点では不要見込み。
