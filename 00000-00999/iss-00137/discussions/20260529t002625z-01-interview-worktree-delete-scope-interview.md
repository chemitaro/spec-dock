---
種別: interview
ID: "20260529t002625z-01-interview"
タイトル: "Worktree delete scope interview"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-05-29"
親: ["iss-00137"]
関連: []
scope: "issue"
scope_id: "iss-00137"
created_at: "2026-05-29T00:26:25Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "spec-dock/active/issue/discussions/20260529t000036z-disc-worktree-list-show-delete-command-scope-memo.md"
  - "spec-dock/active/issue/discussions/20260529t002625z-research-worktree-list-show-delete-existing-contract-research.md"
reflected_to:
  - "spec-dock/active/issue/requirement.md"
---

# 20260529t002625z-01-interview Worktree delete scope interview

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - `worktree delete <target>` の必須範囲、禁止事項、対象外、受け入れ条件、例外・エッジケースを決める。
  - `design.md`:
    - Git adapter、safety guard、target resolution、branch handling の責務境界を決める。
  - `plan.md`:
    - destructive command の Red/Green、review gate、test isolation、branch deletion を別 step に分けるかを決める。
  - `ADR`:
    - 現時点では不要見込み。branch lifecycle を command contract に含める durable policy へ拡大する場合のみ候補。
- chat 上の軽微な一問では足りない理由:
  - 回答によって delete command の破壊範囲と safety guard が変わり、複数 artifact とテスト計画へ反映する必要があるため。

## 質問の目的 (必須)
- 対象者:
  - iwasawayuuta
- 何を明確にする質問か:
  - `worktree delete <target>` が削除する対象を「Git linked worktree の checkout / Git worktree record」までに限定するか、関連 branch の削除まで含めるかを明確にする。
- 回答が後続判断へ与える影響:
  - branch deletion を含める場合、未 push / upstream ahead / current branch / active issue branch などの guard が要件に入る。含めない場合、delete は `git worktree remove` 相当を中心に小さく設計できる。

## 質問 (必須)
- 質問:
  - `spec-dock worktree delete <target>` の初回実装では、関連 branch の削除も command scope に含めますか？
- 回答してほしいこと:
  - A / B / C のどれを採用するか。必要なら「デフォルトは A だが `--delete-branch` を将来検討」などの条件付きでもよい。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - `20260529t000036z-disc-worktree-list-show-delete-command-scope-memo.md` は「関連 branch の削除も command scope に含めるのか」を未決論点としている。
  - 親 epic / `reference_worktree.md` は existing `worktree create` を Git linked worktree 作成に限定し、SpecDock active pointer や Codex-managed worktree cleanup を scope 外にしている。
  - `application/worktree.py` / `infra/git_cli.py` は create と `git worktree list --porcelain` の adapter は持つが、remove/delete/prune や branch deletion adapter はまだない。
  - `tests/cli_runtime/test_worktree.py` は temp repo / temp central root で Git worktree 作成を検証する先例を持つ。
- local context で解決できたこと:
  - `list/show` は Git worktree record と central root namespace から read-only に要件化できる。
  - `delete` は main checkout/current checkout/dirty worktree を削除しない safety guard が必要。
  - branch deletion は既存実装からは導けない product decision。
- まだ人間判断が必要な理由:
  - branch を消すかどうかは「操作後に何を残したいか」という運用方針であり、ローカルコードだけでは正解を決められないため。

## 回答案 (必須)
- Option A:
  - 初回実装では関連 branch を削除しない。`worktree delete` は safety guard を通過した linked worktree checkout / Git worktree record の削除に限定する。
- Option B:
  - `--delete-branch` のような明示 option を同じ issue に含め、指定時だけ関連 local branch も削除する。
- Option C:
  - default で関連 local branch も削除する。ただし未 push / upstream ahead / current branch / protected branch 相当の guard を入れる。

## Codex の分析 (必須)
- 判断軸:
  - 安全性、issue scope の小ささ、運用時の手間、branch lifecycle の誤削除リスク、テスト容易性。
- tradeoff:
  - A は最も安全で小さいが、worktree 削除後に branch が残るため cleanup は別途必要。
  - B は実用性が上がるが、branch safety guard の設計とテストが増える。
  - C は cleanup は楽だが、誤削除リスクが最も高く、SpecDock が branch lifecycle policy を強く所有することになる。
- リスク:
  - branch deletion を急いで入れると、未 push 作業や issue branch を消す事故を避けるための条件が膨らみ、`list/show/delete` の初回価値が遅れる。
- 具体シナリオ / edge case:
  - `spec-dock worktree delete spec-dock-iss-00137` が linked worktree を削除した後、branch `main-iss-00137` を残すかどうか。
  - branch が remote に存在しない local-only branch の場合。
  - branch が upstream より ahead の場合。
  - branch が別 worktree で checkout されている場合。

## Codex の推奨案 (必須)
- 推奨:
  - Option A。
- 理由:
  - 今回の主目的は `list/show/delete` の command surface と safety guard を first-class にすること。関連 branch deletion は別の destructive lifecycle なので、初回は scope 外にして `delete` を小さく安全に固めるのがよい。
- 未回答時の影響:
  - `requirement.md` の削除範囲と受け入れ条件を確定できないため、要件定義書の正式作成に進めない。

## ユーザー回答 (回答後に必須)
- 回答:
  - Option A を採用する。初回実装では関連 branch の削除を command scope に含めない。
- 回答日時:
  - 2026-05-29

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - `worktree list` / `show` / `delete` の target / managed scope をどう扱うか。

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- 採用 / 棄却 / deferred の理由:
  - 削除 command の初回 scope を小さく安全に保ち、branch lifecycle policy をこの issue に混ぜないため。

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - `worktree delete <target>` は related local branch を削除しないことを対象外または禁止事項として明記する。
  - 受け入れ条件は linked worktree checkout / Git worktree record の削除と、branch が残ることの観測を含める。
- `design.md`:
  - Git branch deletion adapter はこの issue の実装対象外とする。
  - delete use case は `git worktree remove` 相当の操作と safety guard に集中する。
- `plan.md`:
  - branch deletion test は追加しない。ただし branch が削除されないことを destructive scope guard として確認する。
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
