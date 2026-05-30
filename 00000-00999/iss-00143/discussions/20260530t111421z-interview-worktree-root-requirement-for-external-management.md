---
種別: interview
ID: "20260530t111421z-interview"
タイトル: "Worktree root requirement for external management interview"
状態: "answered"
作成者: "Codex"
最終更新: "2026-05-30"
親: ["iss-00143"]
関連:
  - "iss-00137"
scope: "issue"
scope_id: "iss-00143"
created_at: "2026-05-30T11:14:21Z"
created_by_role: "orchestrator"
status: "answered"
adoption_status: "adopted"
reflected_to: []
derived_from:
  - "spec-dock/active/issue/discussions/20260530t000000z-scratch-external-worktree-management.md"
  - "spec-dock/active/issue/discussions/20260530t100431z-research-external-worktree-requirement-analysis.md"
  - "spec-dock/active/issue/discussions/20260530t100431z-01-interview-external-worktree-remove-scope.md"
  - "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00107-worktree-provisioning/issues/iss-00137-worktree-list-show-delete-commands/discussions/20260529t014953z-interview-worktree-root-env-behavior-interview.md"
intended_targets:
  - "spec-dock/active/issue/requirement.md"
  - "spec-dock/active/issue/report.md"
---

# 20260530t111421z-interview Worktree root requirement for external management interview

## 正式質問として扱う理由

- 影響する artifact:
  - `requirement.md`:
    - `worktree list/show/remove` が `SPEC_DOCK_WORKTREE_ROOT` 未設定でも動くか、fatal error にするかを決める。
  - `design.md`:
    - managed classification の optional 化、JSON diagnostics、env validation timing を決める。
  - `plan.md`:
    - env missing / invalid root の tests と external worktree remove tests を決める。
  - `report.md`:
    - 先行 `iss-00137` の user-approved root-required 判断を変更する場合の evidence を記録する。
- chat 上の軽微な一問では足りない理由:
  - Option A により `remove` が all linked worktrees に広がったため、central root は削除可否の前提ではなく diagnostic の前提に変わる可能性がある。

## 質問の目的

- 対象者:
  - iwasawayuuta
- 何を明確にする質問か:
  - `list/show/remove` で `SPEC_DOCK_WORKTREE_ROOT` を必須のままにするか、外部 worktree management では optional にするか。
- 回答が後続判断へ与える影響:
  - CLI failure contract、JSON fields、managed/unmanaged classification、既存 invalid-root tests の期待値が変わる。

## 質問

Option A を採用した前提で、`worktree list/show/remove` は `SPEC_DOCK_WORKTREE_ROOT` が未設定または invalid でも動作できるようにしますか？

回答は、次のどちらを採用するかでお願いします。

- Option A:
  - `worktree create` は引き続き `SPEC_DOCK_WORKTREE_ROOT` 必須。
  - `worktree list/show/remove` は Git worktree records を正本にするため、`SPEC_DOCK_WORKTREE_ROOT` 未設定でも動く。
  - root が valid な場合だけ `managed=true/false` を分類し、root がない場合は `managed=null` 相当または `managed=false + classification_unavailable` のような diagnostic を返す。
- Option B:
  - `worktree list/show/remove` も引き続き `SPEC_DOCK_WORKTREE_ROOT` 必須。
  - root がない場合は現行どおり fail-fast する。
  - 全 linked worktree を remove できるが、managed/unmanaged diagnostic のため central root 設定は必須とする。

## source-grounded context

- 先行 `iss-00137` では、`list/show/remove` は managed/unmanaged classification と deletable diagnostics のため `SPEC_DOCK_WORKTREE_ROOT` 必須、という user-approved 判断だった。
- 今回 Option A により、`unmanaged` は remove blocker ではなく diagnostic へ変わる。
- 現行 implementation は `_resolve_worktree_root_for_command` を通して `list/show/remove` の前に root を検証する。
- current docs / tests は missing / invalid root で JSON error を返すことを期待している。

## Codex の分析

- Option A の利点:
  - 「同一 repo の all linked worktree を inspect / cleanup する」という今回の目的により合う。
  - Codex Desktop generated worktree を片付けたい場面で、central root env の未設定が余計な blocker にならない。
- Option A のリスク:
  - `managed` field の既存 boolean contract を変更するか、classification unavailable を別 field で表す必要がある。
  - invalid root を silently ignore すると設定ミスに気づきにくい。
- Option B の利点:
  - 現行 contract / tests からの変更が小さく、JSON schema も保てる。
  - managed/unmanaged diagnostic が常に計算できる。
- Option B のリスク:
  - 外部 worktree management が central root 設定に依存し、今回の「regardless of how they were created」という動機と少しずれる。

## Codex の推奨案

- 推奨:
  - Option A。ただし invalid root は warning / diagnostic として返し、missing root と invalid root の扱いを分ける余地がある。
- 理由:
  - `remove` が all linked worktrees に広がるなら、削除可否の正本は Git worktree record と safety guard になる。central root は placement diagnostic であり、command availability の必須条件から外す方が issue の目的に合う。
- 未回答時の影響:
  - requirement の failure contract と JSON schema を確定できない。

## ユーザー回答

- 回答:
  - Option A を採用する。
  - `worktree create` は引き続き `SPEC_DOCK_WORKTREE_ROOT` 環境変数を必須にする。
  - `worktree list` / `worktree show` / `worktree remove` は `SPEC_DOCK_WORKTREE_ROOT` を不要にする。
  - 一覧、参照、削除は Git worktree records を正本にして動作する。
- 回答日時:
  - 2026-05-30

## 追加確認の要否

- 追加確認が必要か:
  - yes
  - root がない場合の JSON diagnostic field と、root が invalid な場合に warning / diagnostic とするかは design で詰める余地がある。

## 採用判断

- adoption_status:
  - adopted
- 採用 / 棄却 / deferred の理由:
  - `remove` の対象を同一 repo の全 linked worktree へ広げたため、削除可否の前提は Git worktree record と safety guard になる。`SPEC_DOCK_WORKTREE_ROOT` は worktree 作成先と managed placement diagnostic のための設定に限定し、inspection / cleanup command の availability blocker から外す。

## requirement / design / plan / ADR への含意

- `requirement.md`:
  - `worktree create` は `SPEC_DOCK_WORKTREE_ROOT` を必須とする。
  - `worktree list` / `show` / `remove` は `SPEC_DOCK_WORKTREE_ROOT` 未設定でも動作する。
  - `list` / `show` / `remove` は Git worktree records を正本にする。
  - root が valid な場合は managed placement diagnostic を出し、root がない場合も inventory / detail / remove は実行できることを受け入れ条件に含める。
- `design.md`:
  - root resolution を create path と inventory/remove path で分ける。
  - `managed` classification は optional diagnostic とし、root absence を fatal error にしない。
- `plan.md`:
  - `SPEC_DOCK_WORKTREE_ROOT` なしで `list --json` / `show --json` / `remove --json` が動く tests を追加する。
  - `create` は root missing で引き続き fail-fast する regression test を維持する。
- `ADR`:
  - 現時点では不要見込み。
