---
種別: interview
ID: "20260529t014700z-interview"
タイトル: "Worktree delete remove naming interview"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-05-29"
親: ["iss-00137"]
関連: []
scope: "issue"
scope_id: "iss-00137"
created_at: "2026-05-29T01:47:00Z"
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

# 20260529t014700z-interview Worktree delete remove naming interview

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - user-facing command 名と alias の有無を決める。
  - `design.md`:
    - parser / command registry の leaf command 名を決める。
  - `plan.md`:
    - CLI help / command invocation tests を決める。
  - `ADR`:
    - 不要見込み。
- chat 上の軽微な一問では足りない理由:
  - command 名は公開 CLI contract であり、後から変えると docs / tests / agent prompt が揺れるため。

## 質問の目的 (必須)
- 対象者:
  - iwasawayuuta
- 何を明確にする質問か:
  - `spec-dock worktree delete <target>` を正式 command 名にするか、Git の `worktree remove` に合わせて `remove` にするか。
- 回答が後続判断へ与える影響:
  - CLI parser、help、docs、JSON result action name、tests が変わる。

## 質問 (必須)
- 質問:
  - user-facing command 名は、issue memo の通り `spec-dock worktree delete <target>` を正式名にしますか？それとも Git terminology に合わせて `remove` にしますか？
- 回答してほしいこと:
  - A / B / C のどれを採用するか。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - issue memo は追加 command として `spec-dock worktree delete <target>` を挙げている。
  - `reference_worktree.md` は future extension として `remove` を挙げている。
  - Git は `git worktree remove [-f] <worktree>` という terminology を使う。
  - SpecDock 既存の spec node 削除 command は top-level `delete`。
- local context で解決できたこと:
  - 実装内部は Git `worktree remove` に寄せる方針。
  - ユーザーの初期表現は `delete`。
  - agent-first の prompt/API としては、`delete` の方が既存 SpecDock の削除操作と揃う。
- まだ人間判断が必要な理由:
  - Git 用語との一致を優先するか、SpecDock command family の削除用語とユーザー入力を優先するかは product vocabulary の判断。

## 回答案 (必須)
- Option A:
  - 正式名は `worktree delete` にする。`remove` alias は初回では入れない。
- Option B:
  - 正式名は `worktree remove` にする。`delete` alias は初回では入れない。
- Option C:
  - 正式名は `worktree delete`、互換 alias として `worktree remove` も同時に入れる。

## Codex の分析 (必須)
- 判断軸:
  - SpecDock vocabulary との一貫性、Git terminology との一致、alias による実装・docs 増加、agent prompt の安定性。
- tradeoff:
  - A は既存 `delete` command と issue memo に揃う。Git との用語差は docs で説明できる。
  - B は Git に揃うが、ユーザーが求めた `delete` と SpecDock の top-level `delete` からずれる。
  - C は親切だが、初回から alias 2 系統の help/docs/tests が必要になる。
- リスク:
  - alias を増やすと agent がどちらを正規と扱うべきか曖昧になりやすい。
- 具体シナリオ / edge case:
  - agent が requirement に従い `worktree delete` を実行する。
  - Git に慣れた人が `worktree remove` を期待する。
  - docs に `delete` と `remove` が混在する。

## Codex の推奨案 (必須)
- 推奨:
  - Option A。
- 理由:
  - この issue のタイトルとメモ、既存 SpecDock の destructive operation 名に合わせて `delete` を正式名にするのが agent prompt と docs を安定させやすい。Git `remove` は内部実装・説明用語として扱えばよい。
- 未回答時の影響:
  - requirement の command surface と CLI tests を確定できない。

## ユーザー回答 (回答後に必須)
- 回答:
  - Option B を採用する。
  - user-facing command 名は Git の worktree interface に合わせて `spec-dock worktree remove <target>` とする。
  - `delete` alias は初回では入れない。
- 回答日時:
  - 2026-05-29

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - `SPEC_DOCK_WORKTREE_ROOT` が未設定・不正な場合の `list/show/remove` の挙動。

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- 採用 / 棄却 / deferred の理由:
  - Git linked worktree の操作面として、Git terminology と一致する `remove` を正式名にする。agent-first の安定性を保つため、`delete` alias は追加しない。

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - command surface は `spec-dock worktree list`、`spec-dock worktree show <target>`、`spec-dock worktree remove <target>` とする。
  - `worktree delete` は初回 scope 外とし、alias としても提供しない。
- `design.md`:
  - CLI parser / registry は `worktree_remove` leaf command を追加する。
  - application use case は `worktree_remove` とし、内部で Git `worktree remove` adapter を使う。
- `plan.md`:
  - CLI help / parser / runtime tests は `remove` を正規 command として検証し、`delete` alias は存在しないことを確認する。
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
