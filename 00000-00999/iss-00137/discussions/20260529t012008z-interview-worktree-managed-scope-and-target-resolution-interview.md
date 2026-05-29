---
種別: interview
ID: "20260529t012008z-interview"
タイトル: "Worktree managed scope and target resolution interview"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-05-29"
親: ["iss-00137"]
関連: []
scope: "issue"
scope_id: "iss-00137"
created_at: "2026-05-29T01:20:08Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "spec-dock/active/issue/discussions/20260529t000036z-disc-worktree-list-show-delete-command-scope-memo.md"
  - "spec-dock/active/issue/discussions/20260529t002625z-research-worktree-list-show-delete-existing-contract-research.md"
  - "spec-dock/active/issue/discussions/20260529t002625z-01-interview-worktree-delete-scope-interview.md"
reflected_to:
  - "spec-dock/active/issue/requirement.md"
---

# 20260529t012008z-interview Worktree managed scope and target resolution interview

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - `worktree list` の表示対象、`show/delete <target>` の target 解決、central root 外 worktree の扱い、曖昧一致時の例外条件を決める。
  - `design.md`:
    - Git worktree record と `SPEC_DOCK_WORKTREE_ROOT/<repo-basename>/` namespace から managed / unmanaged を分類する責務を決める。
  - `plan.md`:
    - list/show/delete のテスト fixtures と edge case coverage を決める。
  - `ADR`:
    - 現時点では不要見込み。SpecDock-managed worktree の長期定義を central root 外へ拡大する場合のみ候補。
- chat 上の軽微な一問では足りない理由:
  - target 解決と managed scope は 3 command 全体のユーザー体験、安全性、テスト契約に影響するため。

## 質問の目的 (必須)
- 対象者:
  - iwasawayuuta
- 何を明確にする質問か:
  - `worktree list` の対象範囲と、`show/delete <target>` が受け付ける target 種別を明確にする。
- 回答が後続判断へ与える影響:
  - central root 外 worktree を表示・操作対象に含めるか、target として path / basename / branch をどこまで許可するかで、実装とエラー設計が変わる。

## 質問 (必須)
- 質問:
  - 初回実装では、SpecDock-managed worktree を `SPEC_DOCK_WORKTREE_ROOT/<repo-basename>/` 配下の Git linked worktree に限定し、`show/delete <target>` の target は `id` または directory basename を主対象にする、という方針でよいですか？
- 回答してほしいこと:
  - A / B / C のどれを採用するか。必要なら「list は unmanaged も表示するが delete は managed のみ」などの条件付きでもよい。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - 親 epic は作成先を `SPEC_DOCK_WORKTREE_ROOT/<repo-basename>/` namespace と定義している。
  - `worktree create` の `id` は path basename の suffix として保存されるが、SpecDock 側の永続 registry はない。
  - `git worktree list --porcelain` は全 linked worktree record を返せるため、central root 外の worktree も観測できる。
  - issue memo は「central root 外にある worktree を一覧や詳細でどう扱うか」と「path、directory basename、branch name、id のどれを target にするか」を未決論点としている。
- local context で解決できたこと:
  - central root namespace 内の worktree は existing create contract から SpecDock-managed と説明しやすい。
  - Git worktree record だけを source にすると、SpecDock が作っていない worktree も混じる。
  - branch name は `<current-branch>-<id>` なので slash を含むことがあり、target としては入力・曖昧一致の設計が少し重い。
- まだ人間判断が必要な理由:
  - 「SpecDock-managed」の意味を厳密に central root に限定するか、Git linked worktree 全体の viewer として広げるかはプロダクト方針で決める必要がある。

## 回答案 (必須)
- Option A:
  - managed scope は `SPEC_DOCK_WORKTREE_ROOT/<repo-basename>/` 配下に限定する。`list` は managed worktree を主表示し、`show/delete <target>` は managed worktree の `id` または directory basename を受け付ける。central root 外 worktree は初回操作対象外。
- Option B:
  - `list` / `show` は `git worktree list` に出る全 linked worktree を扱うが、`delete` は central root namespace 配下だけ許可する。
- Option C:
  - `list` / `show` / `delete` すべてで Git linked worktree 全体を扱い、path / basename / branch / id を幅広く target として受け付ける。

## Codex の分析 (必須)
- 判断軸:
  - 安全性、`worktree create` contract との一貫性、target 解決の分かりやすさ、central root 外の既存 worktree への可視性、初回実装の小ささ。
- tradeoff:
  - A は一番小さく安全だが、central root 外の worktree は見えない/操作できない。
  - B は可視性と安全性のバランスが良いが、managed/unmanaged 表示分類が必要。
  - C は万能だが、誤削除や曖昧一致の設計が重く、`worktree create` の central root contract から広がる。
- リスク:
  - 初回から C にすると、SpecDock が作っていない worktree の lifecycle まで所有しているように見え、削除事故の防止条件が膨らむ。
- 具体シナリオ / edge case:
  - `/tmp/worktrees/spec-dock/spec-dock-feature` と `/other/spec-dock-feature` が両方 Git worktree record にある。
  - branch `feature/foo-wt1` と directory basename `spec-dock-wt1` のどちらも target として指定できる場合。
  - central root env が未設定の状態で `list` / `show` を実行する場合。

## Codex の推奨案 (必須)
- 推奨:
  - Option B。
- 理由:
  - `list/show` は operator が現状把握に使うため、Git が認識している central root 外 worktree も `unmanaged` として見える方が便利。一方、`delete` は破壊的なので初回は managed worktree のみに限定するのが安全。
- 未回答時の影響:
  - `list` の表示対象、`show/delete` の target resolution、central root env 未設定時の振る舞いを要件定義書に確定できない。

## ユーザー回答 (回答後に必須)
- 回答:
  - Option B を採用する。`list` / `show` は Git が認識する全 linked worktree を扱い、central root namespace 配下を `managed`、それ以外を `unmanaged` と分類する。`delete` は初回実装では managed worktree のみに限定する。
- 回答日時:
  - 2026-05-29

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - `worktree delete` の dirty worktree / untracked files / force option の扱い。

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- 採用 / 棄却 / deferred の理由:
  - `list` / `show` は現状把握のため central root 外 worktree も見えるようにし、破壊的な `delete` は SpecDock が作成契約を持つ managed worktree に限定することで、安全性と運用上の可視性を両立するため。

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - `worktree list` / `worktree show <target>` は managed / unmanaged classification を表示する。
  - `worktree delete <target>` は managed worktree のみを対象にし、unmanaged worktree は拒否する。
  - `target` は全 linked worktree の中で解決するが、delete は解決後に managed guard を通す。
- `design.md`:
  - Git worktree records を central root namespace と照合し、managed / unmanaged を分類する application-level model を追加する。
  - delete use case では unmanaged rejection を safety guard として扱う。
- `plan.md`:
  - list/show の managed/unmanaged 表示テストと、delete が unmanaged target を拒否するテストを入れる。
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
