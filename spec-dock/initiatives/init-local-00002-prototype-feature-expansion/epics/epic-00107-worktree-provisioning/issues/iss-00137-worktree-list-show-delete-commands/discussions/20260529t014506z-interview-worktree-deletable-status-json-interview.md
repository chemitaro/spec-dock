---
種別: interview
ID: "20260529t014506z-interview"
タイトル: "Worktree deletable status json interview"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-05-29"
親: ["iss-00137"]
関連: []
scope: "issue"
scope_id: "iss-00137"
created_at: "2026-05-29T01:45:06Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "spec-dock/active/issue/discussions/20260529t002625z-research-worktree-list-show-delete-existing-contract-research.md"
  - "spec-dock/active/issue/discussions/20260529t012008z-interview-worktree-managed-scope-and-target-resolution-interview.md"
  - "spec-dock/active/issue/discussions/20260529t012346z-interview-worktree-delete-dirty-guard-interview.md"
  - "spec-dock/active/issue/discussions/20260529t013748z-interview-worktree-output-contract-interview.md"
  - "spec-dock/active/issue/discussions/20260529t014129z-interview-worktree-target-resolution-interview.md"
reflected_to:
  - "spec-dock/active/issue/requirement.md"
---

# 20260529t014506z-interview Worktree deletable status json interview

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - JSON output に `deletable` / `delete_blockers` を含めるか、削除可否は `delete` 実行時だけ判定するかを決める。
  - `design.md`:
    - `list/show` が filesystem / Git status をどこまで読むか、軽量 inventory に留めるかを決める。
  - `plan.md`:
    - JSON output tests と delete guard tests の責務分担を決める。
  - `ADR`:
    - 不要見込み。
- chat 上の軽微な一問では足りない理由:
  - agent が `list --json` だけで安全に削除候補を選べるか、削除直前にだけ確定判定するかで command contract が変わるため。

## 質問の目的 (必須)
- 対象者:
  - iwasawayuuta
- 何を明確にする質問か:
  - `list/show --json` に削除可否と拒否理由を事前表示するかどうか。
- 回答が後続判断へ与える影響:
  - JSON schema、Git status / current path checks、locked / dirty detection の実装タイミングが変わる。

## 質問 (必須)
- 質問:
  - `worktree list --json` / `show --json` には、各 worktree の `deletable` と `delete_blockers` を含めますか？それとも削除可否は `delete` 実行時だけ判定しますか？
- 回答してほしいこと:
  - A / B / C のどれを採用するか。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - 先行回答により、`delete` は managed のみ、main/current/unmanaged は拒否する。
  - 先行回答により、通常削除は Git `worktree remove` に寄せ、dirty / locked は Git error を表示し、必要なら `--force`。
  - 先行回答により、`list/show/delete` は agent-first で `--json` を持つ。
  - `git worktree remove -h` は `--force` を dirty / locked 用として説明している。
- local context で解決できたこと:
  - managed/unmanaged、main checkout、current checkout は `list/show` 時点でも判定しやすい。
  - dirty / locked は削除直前の状態変化があり得るため、`list/show` の事前表示だけでは最終保証にならない。
- まだ人間判断が必要な理由:
  - agent-first で事前 planning しやすくするか、JSON schema を軽く保つかの判断が必要。

## 回答案 (必須)
- Option A:
  - `list/show --json` に `deletable` と `delete_blockers` を含める。ただしこれは事前診断であり、`delete` 実行時に必ず再検証する。
- Option B:
  - `show --json` にだけ `deletable` と `delete_blockers` を含める。`list --json` は inventory に留める。
- Option C:
  - `list/show --json` には削除可否を含めない。削除可否は `delete` 実行時だけ判定する。

## Codex の分析 (必須)
- 判断軸:
  - agent の計画しやすさ、JSON schema の重さ、状態の鮮度、実装の小ささ、誤削除防止。
- tradeoff:
  - A は agent が一覧から削除候補を選びやすい。ただし stale になり得るため、delete 時の再検証が必須。
  - B は詳細確認時だけ重い判定を行うため、list が軽い。ただし agent は N 件 show する必要がある。
  - C は最小だが、agent-first の `list --json` としては削除候補選定がしづらい。
- リスク:
  - `deletable=true` を最終保証のように扱うと危険。JSON field には事前診断であることを docs に明記する必要がある。
- 具体シナリオ / edge case:
  - agent が `list --json` で `managed=true` かつ `deletable=true` の worktree を選ぶ。
  - `list --json` 後に別プロセスが worktree を dirty にする。
  - current checkout を `delete` target にしてしまう。

## Codex の推奨案 (必須)
- 推奨:
  - Option A。
- 理由:
  - agent-first なら `list --json` の時点で削除候補を絞れることが重要。ただし最終判定は必ず `delete` で再実行し、`deletable` は planning hint として扱うのが安全。
- 未回答時の影響:
  - JSON schema と `list/show` が実行する診断範囲を確定できない。

## ユーザー回答 (回答後に必須)
- 回答:
  - Option A を採用する。
  - `worktree list --json` / `worktree show --json` の両方に、各 worktree の `deletable` と `delete_blockers` を含める。
  - ただし `deletable` は planning hint とし、`worktree delete` 実行時には必ず削除可否を再検証する。
- 回答日時:
  - 2026-05-29

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - user-facing command 名を `delete` にするか、Git terminology に合わせて `remove` にするか。

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- 採用 / 棄却 / deferred の理由:
  - agent-first の JSON output として、一覧時点で削除候補を絞れることを重視する。ただし状態は変化し得るため、`delete` 実行時の再検証を必須にする。

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - `worktree list --json` / `worktree show --json` は `deletable` と `delete_blockers` を含める。
  - `deletable` は planning hint であり、`worktree delete` は実行時に managed / main / current / dirty / locked 等を再検証する。
- `design.md`:
  - list/show result contract は deletion diagnostics を持つ。
  - delete use case は list/show の診断結果を信用せず、削除直前に同じ guard を再評価する。
- `plan.md`:
  - `list --json` / `show --json` の `deletable` / `delete_blockers` assertion と、delete 時再検証の test を追加する。
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
