---
種別: interview
ID: "20260529t014953z-interview"
タイトル: "Worktree root env behavior interview"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-05-29"
親: ["iss-00137"]
関連: []
scope: "issue"
scope_id: "iss-00137"
created_at: "2026-05-29T01:49:53Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "spec-dock/active/epic/requirement.md"
  - "spec-dock/active/issue/discussions/20260529t002625z-research-worktree-list-show-delete-existing-contract-research.md"
  - "spec-dock/active/issue/discussions/20260529t012008z-interview-worktree-managed-scope-and-target-resolution-interview.md"
  - "spec-dock/active/issue/discussions/20260529t014506z-interview-worktree-deletable-status-json-interview.md"
  - "spec-dock/active/issue/discussions/20260529t014700z-interview-worktree-delete-remove-naming-interview.md"
reflected_to:
  - "spec-dock/active/issue/requirement.md"
---

# 20260529t014953z-interview Worktree root env behavior interview

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - `SPEC_DOCK_WORKTREE_ROOT` が未設定・不正な場合の `list` / `show` / `remove` の failure contract を決める。
  - `design.md`:
    - managed/unmanaged classification と deletable diagnostics が central root に依存するかどうかを決める。
  - `plan.md`:
    - env missing / invalid root の tests をどの command に入れるか決める。
  - `ADR`:
    - 不要見込み。
- chat 上の軽微な一問では足りない理由:
  - agent-first JSON contract で `managed` / `deletable` を安定して出すには central root contract の扱いを固定する必要があるため。

## 質問の目的 (必須)
- 対象者:
  - iwasawayuuta
- 何を明確にする質問か:
  - `SPEC_DOCK_WORKTREE_ROOT` が未設定、空、不正 path の場合に、read-only な `list/show` も fail-fast するか、部分情報を返すか。
- 回答が後続判断へ与える影響:
  - `list/show --json` の `managed` / `deletable` の意味、`remove` の safety guard、env validation の実装範囲が変わる。

## 質問 (必須)
- 質問:
  - `worktree list` / `show` / `remove` は、`worktree create` と同じく `SPEC_DOCK_WORKTREE_ROOT` を必須にして、未設定・不正な場合はすべて fail-fast にしますか？
- 回答してほしいこと:
  - A / B / C のどれを採用するか。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - 親 epic は `worktree create` で `SPEC_DOCK_WORKTREE_ROOT` を必須としている。
  - 先行回答により、`list/show` は全 linked worktree を表示し、central root 配下を `managed`、外を `unmanaged` と分類する。
  - 先行回答により、`remove` は managed worktree のみ許可する。
  - 先行回答により、`list/show --json` は `deletable` / `delete_blockers` を含む。
- local context で解決できたこと:
  - Git worktree records の列挙自体は central root env がなくても可能。
  - しかし `managed` / `unmanaged` classification と `remove` の managed-only guard は central root env に依存する。
  - env がない状態で partial JSON を返すと、agent が `managed=false` と `unknown` を取り違えるリスクがある。
- まだ人間判断が必要な理由:
  - read-only inventory を partial success にするか、agent-first の contract 安定性を優先して fail-fast にするかは product behavior の判断。

## 回答案 (必須)
- Option A:
  - `list` / `show` / `remove` すべてで `SPEC_DOCK_WORKTREE_ROOT` を必須にし、missing / blank / invalid root は fail-fast にする。
- Option B:
  - `list` / `show` は env missing でも全 Git worktree を表示するが、`managed` は `unknown` にする。`remove` は env 必須。
- Option C:
  - `list` は env missing でも表示、`show` / `remove` は env 必須にする。

## Codex の分析 (必須)
- 判断軸:
  - agent-first JSON の安定性、read-only inventory の便利さ、failure contract の単純さ、managed-only delete safety。
- tradeoff:
  - A は一貫して安全で、`managed` / `deletable` の意味が常に明確。ただし env 未設定時に read-only list も使えない。
  - B は観測だけはできるが、JSON に `unknown` state が入り、agent の分岐が増える。
  - C は折衷だが、`list` と `show` の contract がずれる。
- リスク:
  - env missing で partial data を返すと、agent が unmanaged 判定や deletable 判定を誤解する可能性がある。
- 具体シナリオ / edge case:
  - CI / agent session で `SPEC_DOCK_WORKTREE_ROOT` が未設定のまま `worktree list --json` を実行する。
  - central root path が file や relative path。
  - `remove` 前に `list --json` の `deletable` を信頼して対象を選ぶ。

## Codex の推奨案 (必須)
- 推奨:
  - Option A。
- 理由:
  - この command 群は agent-first で、`managed` / `deletable` を安定した JSON contract として使う。partial success より fail-fast の方が agent にとって扱いやすく、`worktree create` の central root contract とも揃う。
- 未回答時の影響:
  - env validation requirement と list/show/remove の failure tests を確定できない。

## ユーザー回答 (回答後に必須)
- 回答:
  - Option A を採用する。
  - `worktree list` / `worktree show` / `worktree remove` は、`worktree create` と同じく `SPEC_DOCK_WORKTREE_ROOT` を必須にする。
  - SpecDock が control する worktree は、すべて SpecDock の central root rule に従っている必要がある。
  - `SPEC_DOCK_WORKTREE_ROOT` が未設定、blank、または不正な場合は fail-fast とし、command を実行できないようにする。
- 回答日時:
  - 2026-05-29

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - stale / missing worktree record の扱いをこの issue に含めるか。

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- 採用 / 棄却 / deferred の理由:
  - SpecDock-managed worktree の判断と removal safety は central root rule に依存する。agent-first JSON contract を安定させるため、partial inventory ではなく fail-fast を採用する。

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - `worktree list` / `worktree show` / `worktree remove` は `SPEC_DOCK_WORKTREE_ROOT` を必須とする。
  - missing / blank / relative / file / broken symlink 等の invalid root は fail-fast し、Git worktree listing や removal を行わない。
  - root validation は `worktree create` と同じ contract に揃える。
- `design.md`:
  - worktree command group 共通の root resolution / validation helper を使う。
  - `list/show/remove` は root validation 後に Git worktree records を読む。
- `plan.md`:
  - env missing / blank / invalid root で `list/show/remove` が fail-fast し、side effect がないことをテストする。
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
