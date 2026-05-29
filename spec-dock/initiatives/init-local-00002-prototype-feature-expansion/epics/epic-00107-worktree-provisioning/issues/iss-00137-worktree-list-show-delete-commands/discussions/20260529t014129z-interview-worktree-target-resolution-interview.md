---
種別: interview
ID: "20260529t014129z-interview"
タイトル: "Worktree target resolution interview"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-05-29"
親: ["iss-00137"]
関連: []
scope: "issue"
scope_id: "iss-00137"
created_at: "2026-05-29T01:41:29Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "spec-dock/active/issue/discussions/20260529t000036z-disc-worktree-list-show-delete-command-scope-memo.md"
  - "spec-dock/active/issue/discussions/20260529t002625z-research-worktree-list-show-delete-existing-contract-research.md"
  - "spec-dock/active/issue/discussions/20260529t012008z-interview-worktree-managed-scope-and-target-resolution-interview.md"
  - "spec-dock/active/issue/discussions/20260529t013748z-interview-worktree-output-contract-interview.md"
reflected_to:
  - "spec-dock/active/issue/requirement.md"
---

# 20260529t014129z-interview Worktree target resolution interview

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - `worktree show <target>` / `worktree delete <target>` の target 種別、優先順位、曖昧一致時の failure contract を決める。
  - `design.md`:
    - target resolver と JSON payload の stable identifier を決める。
  - `plan.md`:
    - target resolution と ambiguity の tests を決める。
  - `ADR`:
    - 不要見込み。
- chat 上の軽微な一問では足りない理由:
  - agent-first の command では target が安定して解決できることが重要で、誤削除防止にも直結するため。

## 質問の目的 (必須)
- 対象者:
  - iwasawayuuta
- 何を明確にする質問か:
  - `show/delete <target>` が受け付ける target forms と、複数一致時にどう fail するか。
- 回答が後続判断へ与える影響:
  - JSON schema の `id` / `name` / `path` field、CLI help、delete safety tests が変わる。

## 質問 (必須)
- 質問:
  - agent-first の初回実装では、`worktree list --json` が返す stable `id` を `show/delete <target>` の主 target にし、補助的に absolute path と directory basename を受け付け、branch name target は future scope にする方針でよいですか？
- 回答してほしいこと:
  - A / B / C のどれを採用するか。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - `worktree create` の id は `wt1` または `<label>` / `<label>N` で、path basename は `<repo-basename>-<id>`。
  - `git worktree list --porcelain` records には path と branch があるが、SpecDock 永続 registry はない。
  - 先行回答により `list/show/delete` は `--json` を持ち、agent-first で使われる。
  - 先行回答により `list/show` は managed/unmanaged を扱い、delete は managed のみに限定される。
- local context で解決できたこと:
  - managed worktree の stable id は central root namespace と path basename から導出できる。
  - unmanaged worktree は create 由来 id がないため、path-derived id か path を stable identifier にする必要がある。
  - branch name は slash を含み得るうえ、複数 worktree / target forms と衝突しやすい。
- まだ人間判断が必要な理由:
  - agent がどの identifier を保存・再利用する前提にするかは UX / API contract として決める必要がある。

## 回答案 (必須)
- Option A:
  - `list --json` が返す stable `id` を主 target にする。補助的に absolute path と directory basename も受け付ける。branch name target は future scope。複数一致は候補一覧付き fatal error。
- Option B:
  - target は `list --json` の stable `id` のみに限定する。人間向けの basename / path shortcut は入れない。
- Option C:
  - stable `id`、absolute path、directory basename、branch name をすべて受け付ける。複数一致は候補一覧付き fatal error。

## Codex の分析 (必須)
- 判断軸:
  - agent の安定性、人間の手入力のしやすさ、誤削除防止、実装の小ささ、曖昧一致の少なさ。
- tradeoff:
  - A は agent-first の stable id を中心にしつつ、実用的な path/basename shortcut も残せる。branch ambiguity は避けられる。
  - B は最も厳密で agent 向けだが、CLI を手で試すときに少し不便。
  - C は便利だが、branch name は slash や suffix 由来の曖昧さがあり、削除 command では危険側。
- リスク:
  - branch name target を初回に入れると、branch lifecycle を削除しないという採用済み方針と mental model が混ざる。
- 具体シナリオ / edge case:
  - `list --json` の `id` を agent が保存して後続 `delete <id>` に渡す。
  - directory basename が unmanaged worktree と managed worktree で衝突する。
  - branch `feature/foo-wt1` を target として入力したくなるが、path basename と一致しない。

## Codex の推奨案 (必須)
- 推奨:
  - Option A。
- 理由:
  - agent-first なので stable `id` を主契約にしつつ、実運用で path/basename を指定できる余地を残すのが使いやすい。branch target は便利そうに見えて誤解と曖昧さが増えるため初回 scope 外がよい。
- 未回答時の影響:
  - JSON schema と target resolver の requirement / tests を確定できない。

## ユーザー回答 (回答後に必須)
- 回答:
  - Option A を採用する。
  - `worktree list --json` が返す stable `id` を `show/delete <target>` の主 target とする。
  - 補助的に absolute path と directory basename も受け付ける。
  - branch name target は初回 scope 外とする。
  - 複数一致した場合は候補一覧付き fatal error とする。
- 回答日時:
  - 2026-05-29

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - `list/show --json` に削除可否と拒否理由をどこまで含めるか。

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- 採用 / 棄却 / deferred の理由:
  - agent-first の主契約として stable `id` を使いつつ、debug / manual operation 用に path と directory basename を許可する。branch name は branch lifecycle と混同しやすいため初回 scope 外にする。

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - `worktree list --json` は後続 `show/delete` に渡せる stable `id` を各 record に含める。
  - `show/delete <target>` は stable `id`、absolute path、directory basename を受け付ける。
  - branch name target は対象外にする。
  - target が複数一致する場合は削除せず、候補一覧付き fatal error とする。
- `design.md`:
  - target resolver は accepted target forms と ambiguity detection を application layer に置く。
  - JSON payload は stable `id`、path、basename を含める。
- `plan.md`:
  - stable id / absolute path / basename target の成功テストと、branch target 不受理、複数一致 fatal error のテストを入れる。
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
