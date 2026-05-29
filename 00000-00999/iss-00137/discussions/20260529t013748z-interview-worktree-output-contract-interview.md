---
種別: interview
ID: "20260529t013748z-interview"
タイトル: "Worktree output contract interview"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-05-29"
親: ["iss-00137"]
関連: []
scope: "issue"
scope_id: "iss-00137"
created_at: "2026-05-29T01:37:48Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "spec-dock/active/issue/discussions/20260529t000036z-disc-worktree-list-show-delete-command-scope-memo.md"
  - "spec-dock/active/issue/discussions/20260529t002625z-research-worktree-list-show-delete-existing-contract-research.md"
  - "spec-dock/active/issue/discussions/20260529t012008z-interview-worktree-managed-scope-and-target-resolution-interview.md"
  - "spec-dock/active/issue/discussions/20260529t013126z-interview-worktree-delete-confirmation-interview.md"
reflected_to:
  - "spec-dock/active/issue/requirement.md"
---

# 20260529t013748z-interview Worktree output contract interview

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - `list` / `show` / `delete` の観測可能な output field と JSON support の要否を決める。
  - `design.md`:
    - presentation contract と result dataclass の payload を決める。
  - `plan.md`:
    - output assertion tests の範囲を決める。
  - `ADR`:
    - 不要見込み。
- chat 上の軽微な一問では足りない理由:
  - JSON support を同時に含めるかで CLI contract、test matrix、将来互換性が変わるため。

## 質問の目的 (必須)
- 対象者:
  - iwasawayuuta
- 何を明確にする質問か:
  - 初回実装で human-readable text output のみを要求するか、`--json` machine-readable output も含めるか。
- 回答が後続判断へ与える影響:
  - `list` の列安定性、`show` の詳細 field、`delete` の result payload、presentation tests が変わる。

## 質問 (必須)
- 質問:
  - 初回実装の output contract は、human-readable text を主契約にして `--json` は future scope にしますか？それとも `list/show/delete` に `--json` も同時に入れますか？
- 回答してほしいこと:
  - A / B / C のどれを採用するか。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - issue memo は「text output のほか、将来的に JSON output が必要か」を未決論点としている。
  - 既存 `worktree create` output は human-readable text のみ。
  - 既存 spec node `delete` は `--json` を持つ。
  - 既存 `deps check` と spec node `delete` は `--json` を持つ。
  - 今回の `list` / `show` / `delete` は人間より agent が把握・操作する目的が強い。
- local context で解決できたこと:
  - human-readable text には少なくとも id/name、path、branch、managed/unmanaged、current/main/deletable を含める必要がある。
  - JSON を入れる場合、managed classification、deletable reason、Git record fields の key stability を初回から固定する必要がある。
- まだ人間判断が必要な理由:
  - machine-readable automation を今回の issue で使う予定があるかは運用方針で決まるため。

## 回答案 (必須)
- Option A:
  - 初回は human-readable text output のみ。`--json` は future scope にする。
- Option B:
  - `list` / `show` には `--json` を同時に入れる。`delete` は text のみ。
- Option C:
  - `list` / `show` / `delete` すべてに `--json` を同時に入れる。

## Codex の分析 (必須)
- 判断軸:
  - 初回 scope の小ささ、将来 automation、既存 create output との一貫性、presentation contract の安定性、テスト量。
- tradeoff:
  - A は最小で、まず人間向け運用に集中できる。ただし後で JSON を追加すると契約が増える。
  - B は inventory 系だけ machine-readable にでき、削除の destructive result は後回しにできる。
  - C は最も自動化しやすいが、初回から JSON schema を固定する負担が大きい。
- リスク:
  - JSON を急いで入れると、まだ固まっていない target resolution / deletable reason の schema を早期固定してしまう。
- 具体シナリオ / edge case:
  - agent が `worktree list --json` から削除候補を選びたい。
  - 人間が `worktree list` で managed/unmanaged と path をざっと確認したい。
  - `delete` の失敗理由を script が機械判定したい。

## Codex の推奨案 (必須)
- 推奨:
  - Option C。
- 理由:
  - ユーザー回答により、この command は agent-first の操作面として扱う。既存 runtime command にも `--json` 先例があるため、`list` / `show` / `delete` すべてに machine-readable output を持たせる方が目的に合う。
- 未回答時の影響:
  - output contract と tests の粒度を確定できない。

## ユーザー回答 (回答後に必須)
- 回答:
  - Option C を採用する。
  - `worktree list` / `worktree show` / `worktree delete` すべてに `--json` を追加する。
  - この command 群は人間が見るためではなく、agent が把握・操作する目的で設計する。
  - human-readable text はあってよいが、agent-first として JSON output を正規の観測面にする。
  - 既存 spec-dock command の `--json` 対応と同じ方向性に合わせる。
- 回答日時:
  - 2026-05-29

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - `show/delete <target>` が受け付ける target 種別と曖昧一致時の挙動。

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- 採用 / 棄却 / deferred の理由:
  - `worktree` command 群は agent-first の操作面であり、machine-readable output が要件上の中心になる。既存 command の `--json` 先例とも整合するため、初回から `list` / `show` / `delete` の JSON contract を要求する。

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - `worktree list --json` / `worktree show <target> --json` / `worktree delete <target> --json` を必須にする。
  - JSON output は agent が target selection、managed/unmanaged 判定、deletable 判定、delete result 判定を行える field を持つ。
  - text output は human-readable fallback として扱い、正規の自動化面は JSON とする。
- `design.md`:
  - presentation layer に worktree JSON payload builder を追加する。
  - result contract は JSON payload に必要な stable fields を保持する。
- `plan.md`:
  - `list` / `show` / `delete` の text assertion に加えて JSON payload assertion を入れる。
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
