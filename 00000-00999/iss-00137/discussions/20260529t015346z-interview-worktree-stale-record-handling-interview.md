---
種別: interview
ID: "20260529t015346z-interview"
タイトル: "Worktree stale record handling interview"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-05-29"
親: ["iss-00137"]
関連: []
scope: "issue"
scope_id: "iss-00137"
created_at: "2026-05-29T01:53:46Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "spec-dock/active/issue/discussions/20260529t000036z-disc-worktree-list-show-delete-command-scope-memo.md"
  - "spec-dock/active/issue/discussions/20260529t002625z-research-worktree-list-show-delete-existing-contract-research.md"
  - "spec-dock/active/issue/discussions/20260529t014953z-interview-worktree-root-env-behavior-interview.md"
reflected_to:
  - "spec-dock/active/issue/requirement.md"
---

# 20260529t015346z-interview Worktree stale record handling interview

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - path missing / stale Git worktree record を `list/show/remove` でどう扱うかを決める。
  - `design.md`:
    - `git worktree prune` 相当の mutation を含めるか、read-only diagnostic に留めるかを決める。
  - `plan.md`:
    - stale record fixture と cleanup command のテスト要否を決める。
  - `ADR`:
    - 不要見込み。
- chat 上の軽微な一問では足りない理由:
  - stale record repair/prune は Git metadata mutation であり、`list/show/remove` の scope を超える可能性があるため。

## 質問の目的 (必須)
- 対象者:
  - iwasawayuuta
- 何を明確にする質問か:
  - Git worktree record はあるが path が存在しない、または central root に directory はあるが Git record がない状態を、この issue で修復・削除対象にするか。
- 回答が後続判断へ与える影響:
  - `prune` / `repair` / orphan directory cleanup を同じ issue に含めるか、JSON diagnostics のみで future scope にするかが変わる。

## 質問 (必須)
- 質問:
  - 初回実装では stale / missing worktree record の修復や `git worktree prune` 相当を scope 外にし、`list/show --json` で状態を診断表示するだけにしますか？
- 回答してほしいこと:
  - A / B / C のどれを採用するか。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - issue memo は stale worktree record の prune を同じ issue に入れるかを未決論点にしている。
  - 先行回答により、remove は managed individual worktree directory を削除する通常 cleanup command。
  - 先行回答により、`list/show --json` には `deletable` と `delete_blockers` を含める。
  - 親 epic の future extension には `prune` が含まれている。
- local context で解決できたこと:
  - stale record の検出は `git worktree list --porcelain` record と path existence の照合で可能。
  - orphan directory の検出は central root namespace scan が必要で、Git record だけを見るより scope が広がる。
  - prune / repair は read-only `list/show` や normal remove とは別の Git metadata mutation。
- まだ人間判断が必要な理由:
  - 大量短命 worktree 運用では stale cleanup が有用だが、初回 issue に含めると scope と destructive behavior が増えるため。

## 回答案 (必須)
- Option A:
  - stale / missing record の修復や prune は scope 外。`list/show --json` は `path_exists` / `record_exists` / `delete_blockers` などで診断表示し、`remove` は通常の Git remove が扱える範囲に限定する。
- Option B:
  - `worktree remove` に stale record cleanup も含める。path missing の managed record を target にした場合、Git metadata から pruning/removal する。
- Option C:
  - `worktree prune` command も同じ issue に追加し、stale record / orphan directory cleanup を扱う。

## Codex の分析 (必須)
- 判断軸:
  - issue scope の小ささ、短命 worktree 運用の実用性、Git metadata mutation の安全性、agent による診断可能性。
- tradeoff:
  - A は最小で安全。stale/orphan は見えるが直せない。
  - B は remove で一部 stale を直せるが、normal remove の意味が広がる。
  - C は運用価値が高いが、別 command / destructive cleanup / tests が増える。
- リスク:
  - prune / orphan cleanup を混ぜると、今回固めた managed remove の contract と別種の cleanup が混在する。
- 具体シナリオ / edge case:
  - Git record はあるが path が消えている。
  - central root namespace に directory はあるが Git record がない。
  - stale record が `list --json` に出るが `remove` できない。

## Codex の推奨案 (必須)
- 推奨:
  - Option A。
- 理由:
  - 今回は `list/show/remove` の基本 command surface を agent-first で固める issue。stale/prune は有用だが別 command として切った方が、削除 semantics と tests が混ざらない。
- 未回答時の影響:
  - stale / orphan state の JSON field と remove behavior を確定できない。

## ユーザー回答 (回答後に必須)
- 回答:
  - Option A を採用する。
  - stale / missing worktree record の修復や `git worktree prune` 相当は初回 scope 外にする。
  - `list/show --json` では診断表示だけ行う。
  - そこまで大量の worktree は想定しなくてよい。
- 回答日時:
  - 2026-05-29

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - no
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - なし。

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- 採用 / 棄却 / deferred の理由:
  - 初回 issue は `list/show/remove` の基本 command surface と agent-first JSON contract に集中し、stale/prune/repair は scope 外にするため。

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - stale record / orphan directory repair は対象外にする。
  - `list/show --json` は `path_exists` / `record_exists` / `delete_blockers` などで診断表示できるが、prune や repair は行わない。
- `design.md`:
  - prune / repair adapter は追加しない。
  - stale / orphan detection は read-only diagnostics に限定する。
- `plan.md`:
  - stale / missing record は JSON diagnostic のテスト対象に留め、cleanup command のテストは入れない。
- `ADR`:
  - 不要。
- reflected_to 更新方針:
  - `requirement.md` 作成時に採用する。

## 条件付き補足 (必要な場合だけ)
- PlantUML 図:
  ```plantuml
  @startuml
  ' TODO: 質問依存、意思決定フロー、before/after、責務境界が必要なら追加する
  @enduml
  ```
- 詳細 tradeoff:
  - ...
- 後続 reflection proposal:
  - ...
- 追加で作る discussion docs:
    - ...
