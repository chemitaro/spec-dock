---
種別: interview
ID: "20260529t012346z-interview"
タイトル: "Worktree delete dirty guard interview"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-05-29"
親: ["iss-00137"]
関連: []
scope: "issue"
scope_id: "iss-00137"
created_at: "2026-05-29T01:23:46Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "spec-dock/active/issue/discussions/20260529t000036z-disc-worktree-list-show-delete-command-scope-memo.md"
  - "spec-dock/active/issue/discussions/20260529t002625z-research-worktree-list-show-delete-existing-contract-research.md"
  - "spec-dock/active/issue/discussions/20260529t002625z-01-interview-worktree-delete-scope-interview.md"
  - "spec-dock/active/issue/discussions/20260529t012008z-interview-worktree-managed-scope-and-target-resolution-interview.md"
reflected_to:
  - "spec-dock/active/issue/requirement.md"
---

# 20260529t012346z-interview Worktree delete dirty guard interview

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - `worktree delete <target>` が dirty worktree、untracked files、ignored files をどう扱うかを受け入れ条件と例外条件に落とす。
  - `design.md`:
    - Git status adapter、safety guard、`--force` の有無、force が bypass できる範囲を決める。
  - `plan.md`:
    - destructive command の Red/Green と hermetic fixture を決める。
  - `ADR`:
    - 不要見込み。削除安全性の issue-local contract として扱う。
- chat 上の軽微な一問では足りない理由:
  - `delete` の破壊範囲と事故防止条件に直結し、テストと CLI option の有無が変わるため。

## 質問の目的 (必須)
- 対象者:
  - iwasawayuuta
- 何を明確にする質問か:
  - dirty worktree / untracked files がある managed worktree を `delete` がデフォルトで拒否するか、明示 force で削除可能にするかを決める。
- 回答が後続判断へ与える影響:
  - `--force` / `--yes` の CLI shape、Git status adapter、テストケース、エラーメッセージが変わる。

## 質問 (必須)
- 質問:
  - `worktree delete <target>` は、dirty worktree や untracked files がある場合に、初回実装で `--force` による削除を許可しますか？
- 回答してほしいこと:
  - A / B / C のどれを採用するか。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - issue memo は「dirty worktree、未 push branch、branch 削除の扱いは実装前に方針を決める」としている。
  - 先行回答により、関連 branch deletion は初回 scope 外。
  - 先行回答により、delete は managed worktree のみに限定される。
  - 既存 `worktree create` tests は temp repo / temp central root で destructive side effect を隔離している。
- local context で解決できたこと:
  - main checkout / current checkout / unmanaged worktree は delete 対象外または拒否対象にできる。
  - branch deletion をしないため、未 push branch は deletion の直接対象ではない。
  - ただし worktree directory の削除は uncommitted file loss に直結する。
- まだ人間判断が必要な理由:
  - force を許可するかどうかは安全性と運用効率のトレードオフであり、プロダクトの destructive command 方針として決める必要がある。

## 回答案 (必須)
- Option A:
  - 初回実装では dirty / untracked がある worktree は常に拒否する。`--force` は入れない。
- Option B:
  - デフォルトでは拒否し、`--force` を指定した場合だけ dirty / untracked worktree の削除を許可する。ただし main/current/unmanaged guard は `--force` でも bypass できない。
- Option C:
  - dirty / untracked は Git の `git worktree remove` の挙動に任せ、SpecDock 独自の preflight guard は最小化する。

## Codex の分析 (必須)
- 判断軸:
  - 誤削除防止、CLI の実用性、実装の小ささ、Git 標準挙動との一貫性、テストの明確さ。
- tradeoff:
  - A は最も安全でシンプルだが、不要 worktree に untracked generated files が残っているだけでも削除できず、手動 cleanup が必要になる。
  - B は安全な default と明示的な escape hatch を両立できるが、`--force` が bypass できる guard とできない guard を明確にする必要がある。
  - C は Git に寄せられるが、SpecDock command としての事故防止メッセージや一貫した UX が弱くなる。
- リスク:
  - `--force` を広くしすぎると main/current/unmanaged まで削除できるように誤解される。force の対象は dirty / untracked guard に限定する必要がある。
- 具体シナリオ / edge case:
  - generated cache file だけが untracked で残っている managed worktree を削除したい。
  - 未コミットの source change がある managed worktree を誤って削除しようとした。
  - current checkout に対して `--force` 付きで delete を実行した。

## Codex の推奨案 (必須)
- 推奨:
  - Option B。
- 理由:
  - default は安全に拒否しつつ、長命 worktree の cleanup では untracked generated files が残ることがあり得るため、明示 `--force` の escape hatch が実用的。`--force` は dirty / untracked guard だけを bypass し、main/current/unmanaged は絶対に拒否するのがよい。
- 未回答時の影響:
  - `delete` の CLI option、safety guard、受け入れ条件、テスト設計を確定できない。

## ユーザー回答 (回答後に必須)
- 回答:
  - Interface としては Option B を採用する。
  - worktree は issue lifecycle とほぼ同じ短命な作業単位として扱う。
  - `SPEC_DOCK_WORKTREE_ROOT/<repo-basename>/` の namespace directory は残し、その内部の個別 worktree directory を削除対象にする。
  - cache などの作業生成物を個別 worktree directory ごと削除することは通常作業であり、追加の `--yes` や `--force` は要求しない。
  - 通常削除は Git 側の `git worktree remove` interface に合わせる。Git が dirty / locked 等で削除を拒否する場合は、その Git error を表示し、削除には `--force` を必要とする。
  - `--force` は Git 側の `git worktree remove --force` に寄せ、dirty / locked worktree の削除を明示的に許可するために使う。
  - Git remove 成功後または force remove 成功後は、Git 管理外 file / cache を含め、個別 worktree directory が残らないようにする。
- 回答日時:
  - 2026-05-29

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - destructive `delete` に `--yes` confirmation を必須にするかどうか。

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- 採用 / 棄却 / deferred の理由:
  - 初回 interface は Git の `worktree remove [-f] <worktree>` に寄せる。短命 worktree cleanup の運用に合わせて、通常削除でも Git が許可する clean worktree なら individual worktree directory を丸ごと消し、cache を残さない。Git が dirty / locked として拒否する場合のみ `--force` を必要とする。

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - `worktree delete <target>` は managed worktree の個別 directory を削除対象にし、namespace directory 自体は残す。
  - デフォルト削除は Git の `git worktree remove` の safety rejection を尊重し、Git が dirty / locked 等で拒否した場合は失敗として表示する。
  - Git が通常削除を許可する clean worktree では、cache など Git 管理外の作業生成物を理由に追加 confirmation を要求しない。
  - 通常削除または `--force` 削除が成功した場合、Git 管理外 file / cache を含め、個別 worktree directory が残らないことを受け入れ条件に含める。
  - `--force` でも main checkout / current checkout / unmanaged worktree は削除不可とする。
- `design.md`:
  - delete use case は Git worktree record removal と filesystem cleanup の順序・失敗時 state を明確化する。
  - `--force` は Git worktree remove の force option に対応させる。
  - cleanup は target が managed / not main / not current であることを確認した後に限定する。
- `plan.md`:
  - default delete が Git の dirty / locked rejection をそのまま失敗として表示するテストを入れる。
  - clean worktree の default delete が cache file を含む individual worktree directory を残さないテストを入れる。
  - `--force` が Git force remove に対応し、成功後に individual worktree directory を残さないテストを入れる。
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
