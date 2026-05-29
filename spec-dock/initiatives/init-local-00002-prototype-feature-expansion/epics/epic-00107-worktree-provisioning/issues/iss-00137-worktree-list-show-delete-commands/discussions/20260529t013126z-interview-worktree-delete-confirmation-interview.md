---
種別: interview
ID: "20260529t013126z-interview"
タイトル: "Worktree delete confirmation interview"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-05-29"
親: ["iss-00137"]
関連: []
scope: "issue"
scope_id: "iss-00137"
created_at: "2026-05-29T01:31:26Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "spec-dock/active/issue/discussions/20260529t000036z-disc-worktree-list-show-delete-command-scope-memo.md"
  - "spec-dock/active/issue/discussions/20260529t002625z-research-worktree-list-show-delete-existing-contract-research.md"
  - "spec-dock/active/issue/discussions/20260529t012346z-interview-worktree-delete-dirty-guard-interview.md"
reflected_to:
  - "spec-dock/active/issue/requirement.md"
---

# 20260529t013126z-interview Worktree delete confirmation interview

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - `worktree delete` が確認 flag なしで実行できるか、`--yes` を必須にするかを destructive operation の受け入れ条件へ反映する。
  - `design.md`:
    - CLI args、confirmation validation、error message を決める。
  - `plan.md`:
    - no-confirm rejection / confirmed delete / force delete の test case を決める。
  - `ADR`:
    - 不要見込み。
- chat 上の軽微な一問では足りない理由:
  - worktree directory を丸ごと削除する破壊的操作の UX と safety policy に直結するため。

## 質問の目的 (必須)
- 対象者:
  - iwasawayuuta
- 何を明確にする質問か:
  - `worktree delete <target>` に `--yes` confirmation を必須にするかどうか。
- 回答が後続判断へ与える影響:
  - CLI shape、help、tests、削除実行時の安全性が変わる。

## 質問 (必須)
- 質問:
  - `spec-dock worktree delete <target>` は、初回実装で `--yes` などの明示 confirmation を必須にしますか？
- 回答してほしいこと:
  - A / B / C のどれを採用するか。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - 既存の spec node `delete` command は destructive operation として `--yes` を持つ。
  - 先行回答により、worktree delete は managed individual worktree directory を Git 管理外 file / cache ごと削除し得る。
  - 先行回答により、関連 branch は削除しない。
  - `--force` は dirty / untracked guard の escape hatch として採用済み。
- local context で解決できたこと:
  - main/current/unmanaged guard は confirmation や force でも bypass しない方針。
  - destructive scope は individual worktree directory であり、namespace directory は残す方針。
- まだ人間判断が必要な理由:
  - daily cleanup を軽くするか、毎回明示 confirmation を要求するかは運用 UX の判断であり、コードからは決められない。

## 回答案 (必須)
- Option A:
  - `--yes` を必須にする。`worktree delete <target> --yes` が通常削除、dirty / untracked を含める場合は `--yes --force`。
- Option B:
  - `--yes` は不要にする。`delete <target>` だけで clean managed worktree は削除でき、dirty / untracked は `--force` で削除できる。
- Option C:
  - interactive TTY では確認 prompt を出し、非 interactive では `--yes` 必須にする。

## Codex の分析 (必須)
- 判断軸:
  - 大量 issue 運用での cleanup 速度、誤削除防止、CI / script での使いやすさ、既存 `delete --yes` との一貫性。
- tradeoff:
  - A は既存 destructive command と一貫し、安全だが、短命 worktree を大量に消す運用では毎回 flag が増える。
  - B は最も軽いが、directory 丸ごと削除としてはやや強い。
  - C は人間操作に優しいが、runtime tests と実装が少し複雑になり、non-interactive agent 実行では結局 `--yes` が必要。
- リスク:
  - `--yes` と `--force` の意味が混ざると危険。`--yes` は破壊的操作の確認、`--force` は dirty / untracked guard の bypass と分ける必要がある。
- 具体シナリオ / edge case:
  - `spec-dock worktree delete spec-dock-iss-00137` を誤って叩いた。
  - cleanup script で複数 worktree を削除したい。
  - agent が non-interactive に削除 command を実行する。

## Codex の推奨案 (必須)
- 推奨:
  - Option A。
- 理由:
  - この command は individual worktree directory を Git 管理外 file / cache ごと削除し得るため、既存 `delete --yes` と同じく明示 confirmation を必須にするのが安全。大量運用では alias/script 側で `--yes` を付ければよい。
- 未回答時の影響:
  - `delete` の CLI contract と destructive operation tests を確定できない。

## ユーザー回答 (回答後に必須)
- 回答:
  - Option B を採用する。
  - `--yes` は不要にする。
  - cache などの作業生成物を含む個別 worktree directory の削除は、短命 worktree lifecycle 上の通常作業として扱う。
  - Git が `git worktree remove` で削除可能と判断する状態では、`delete <target>` だけで削除できるようにする。
  - Git が dirty / locked 等で削除を拒否する状態では、Git interface に合わせて `--force` を必要とする。
- 回答日時:
  - 2026-05-29

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - `worktree list` / `show` の output contract と JSON support の要否。

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- 採用 / 棄却 / deferred の理由:
  - `worktree delete` は短命 worktree cleanup の通常操作であり、cache / generated artifact cleanup に毎回 confirmation を要求すると運用負荷が高い。安全性は managed-only、main/current rejection、Git の dirty / locked rejection、必要時の `--force` で担保する。

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - `worktree delete <target>` は `--yes` なしで実行できる。
  - clean managed worktree は `delete <target>` で削除でき、個別 worktree directory が残らない。
  - Git が dirty / locked 等で拒否する状態では失敗し、`--force` が必要であることを表示する。
- `design.md`:
  - confirmation validation は追加しない。
  - `--force` は Git worktree remove force option として扱う。
- `plan.md`:
  - no-confirm rejection test は不要。
  - normal delete / force delete / Git rejection path の test を追加する。
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
