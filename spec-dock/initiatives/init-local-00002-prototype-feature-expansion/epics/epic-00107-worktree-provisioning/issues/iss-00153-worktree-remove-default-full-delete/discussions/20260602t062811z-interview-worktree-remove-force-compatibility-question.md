---
種別: interview
ID: "20260602t062811z-interview"
タイトル: "Worktree Remove Force Compatibility Question"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-06-02"
親: ["iss-00153"]
関連: []
scope: "<initiative | epic | issue | local-topic>"
scope_id: "iss-00153"
created_at: "2026-06-02THH:MM:SSZ"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/plan.md
  - spec-dock/docs/reference_worktree.md
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/worktree.py
  - src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py
  - tests/cli_runtime/test_worktree.py
reflected_to:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/report.md
---

# 20260602t062811z-interview Worktree Remove Force Compatibility Question

## 位置づけ
- 用途: 重要判断に関わる一つの質問を、回答前の正式質問シートとして作成し、回答後に同じ artifact を完成 record にする。
- authority default: `proposed`。ユーザー回答と採用判断を反映した後は、必要に応じて `user-approved` または `synthesized` に更新する。
- 技術的に調べられることは先に docs / code / tests / ADR / discussions / primary source を確認する。
- 一つの `interview` artifact には一つの本質的な質問だけを書く。回答によって新しい高影響な曖昧さが見つかった場合は、追加質問をこの file に増やさず、次の unanswered `interview` を作成する。
- trivial な yes/no は、重要な判断、後続反映、回答証跡が必要なら `interview` を使い、そうでなければ issue comment や `scratch` で足りる。
- 回答から複数質問の synthesis が必要になったら `disc`、追加調査が必要になったら `research`、長期判断が固まったら `adr` を新規作成する。

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - `worktree remove` の CLI 契約、後方互換性、受け入れ条件、非スコープを決める。
  - `design.md`:
    - parser から `--force` を消すか、受け付けるが default と同じ扱いにするかで設計が変わる。
  - `plan.md`:
    - CLI help / runtime tests / docs 更新の範囲が変わる。
  - `ADR`:
    - ADR は不要と見込む。単一 command の UX / compatibility 判断であり、後戻り困難な architecture decision ではない。
- chat 上の軽微な一問では足りない理由:
  - 親 Epic の品質ゲートには「Existing commands keep backward-compatible behavior」とあり、一方で今回の依頼は「force が存在しない完全削除をデフォルト」と表現されている。互換性を残すか削るかが requirement / design / tests に直接影響する。

## 質問の目的 (必須)
- 対象者:
  - spec-dock maintainer / user。
- 何を明確にする質問か:
  - `worktree remove` の `--force` option を今後 CLI surface に残すかどうか。
- 回答が後続判断へ与える影響:
  - 残す場合は backward-compatible alias / deprecated no-op として扱い、消す場合は `--force` 指定を invalid argument にする requirement として固定する。

## 質問 (必須)
- 質問:
  - `spec-dock worktree remove <target>` を完全削除デフォルトにした後、既存の `--force` option はどう扱いますか？
- 回答してほしいこと:
  - Option A / B のどちらを採用するか。必要なら別案も可。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - `spec-dock/active/epic/requirement.md`: `worktree remove` は同一 repository の linked worktree を対象にし、main/current/bare/stale は `--force` でも削除しない。branch は削除しない。
  - `spec-dock/active/epic/plan.md`: worktree command の docs / tests / command help を一致させる。既存コマンドは backward-compatible behavior を保つ品質ゲートがある。
  - `spec-dock/docs/reference_worktree.md`: 現行 docs は `worktree remove <target> [--force]` とし、通常 remove が dirty / untracked / locked を拒否した場合に `--force` が Git force removal を行うと説明している。
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/worktree.py`: parser が `--force` を `WorktreeRemoveRequest(force=...)` へ渡している。
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py`: `force=True` の場合は `git worktree remove --force --force <path>` を実行する。
  - `tests/cli_runtime/test_worktree.py`: dirty worktree は default で失敗し、`--force` で削除される現行テストがある。
- local context で解決できたこと:
  - 今回の変更は `worktree remove` の削除強度 default を変えるもの。main/current/bare/missing/stale/containment guard と branch retention は既存 Epic の境界として維持すべき。
- まだ人間判断が必要な理由:
  - `--force` を消すことは後方互換性を壊す。親 Epic の互換性方針と今回の UX 意図のどちらを優先するかは maintainer 判断が必要。

## 回答案 (必須)
- Option A:
  - `--force` は廃止し、指定された場合は invalid argument とする。CLI surface から「force mode」を完全になくす。
- Option B:
  - `--force` は互換のため受け付けるが、完全削除が default になったため default と同じ挙動にする。docs / help では deprecated compatibility option として扱う、または非推奨表示に留める。
- Option C:
  - `--force` は残し、locked worktree など Git がより強い force depth を要求するケースだけ追加強度として使う。ただし「force が存在しない」という UX とはズレる。

## Codex の分析 (必須)
- 判断軸:
  - UX の単純さ、既存 script 互換性、docs / tests の明確さ、Git の locked worktree 例外をどう扱うか。
- tradeoff:
  - Option A は新しい UX が明確だが、既存の `worktree remove ... --force` 呼び出しを壊す。Option B は互換性を守るが、「force が存在しない」を完全には満たさない。Option C は Git の概念には近いが、今回のユーザー意図から離れる。
- リスク:
  - Option A の場合、既存利用者や agent 手順が `--force` を付け続けると失敗する。Option B/C の場合、docs に `--force` が残ることで「完全削除 default」の UX が伝わりにくい。
- 具体シナリオ / edge case:
  - dirty / untracked file を含む linked worktree を `worktree remove <target>` だけで削除できる必要がある。
  - main checkout / current checkout / bare worktree / missing path / record missing / containment guard は完全削除 default でも削除してはならない。
  - successful remove 後も branch deletion は行わず、`branch_deleted=false` を維持する。

## Codex の推奨案 (必須)
- 推奨:
  - Option B。
- 理由:
  - 親 Epic の backward compatibility gate を守りながら、ユーザーが求める「引数なしで完全削除」を満たせる。`--force` は新しい挙動を選ぶための必須引数ではなくなるため、実用上の friction は解消される。
- 未回答時の影響:
  - requirement に `--force` の互換 / 廃止方針を固定できず、design / tests の範囲が曖昧なままになる。

## ユーザー回答 (回答後に必須)
- 回答:
  - Option B を採用する。
- 回答日時:
  - 2026-06-02

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - no
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - なし。

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- 採用 / 棄却 / deferred の理由:
  - ユーザーが Option B を明示採用した。親 Epic の backward compatibility gate を維持しながら、`worktree remove <target>` の引数なし実行で完全削除を実現する。

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - `--force` は互換入力として受け付けるが、完全削除 default と同じ削除強度を表す。新しい強度選択や必須 option として扱わない。
- `design.md`:
  - parser / request / Git adapter の扱いを、default remove が Git force removal 相当になる方向で設計する。`--force` 指定時も同じ contract を満たす。
- `plan.md`:
  - default remove と `--force` 指定 remove の互換テストを分けて確認する。
- `ADR`:
  - ADR 不要。issue-local command UX / compatibility 判断として扱う。
- reflected_to 更新方針:
  - `requirement.md` と `report.md` に採用済み evidence として反映済み。

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
