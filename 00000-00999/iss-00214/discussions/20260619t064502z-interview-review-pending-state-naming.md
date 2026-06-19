---
種別: interview
ID: "20260619t064502z-interview"
タイトル: "Review Pending State Naming"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-06-19"
親: ["iss-00214"]
関連: []
scope: "<initiative | epic | issue | local-topic>"
scope_id: "iss-00214"
created_at: "2026-06-19T06:45:02Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "GitHub issue #214"
  - "20260619t064501z-research-review-progress-target-state-source-analysis.md"
reflected_to:
  - "requirement.md"
  - "design.md"
  - "plan.md"
  - "report.md"
---

# 20260619t064502z-interview Review Pending State Naming

## 位置づけ
- 用途: 重要判断に関わる一つの質問を、回答前の source-grounded 正式質問シートとして作成し、回答後に同じ artifact を完成 record にする。
- authority default: `proposed`。ユーザー回答と採用判断を反映した後は、必要に応じて `user-approved` または `synthesized` に更新する。
- この artifact は answer capture / adoption target / reflection の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 技術的に調べられることは先に docs / code / tests / ADR / discussions / primary source を確認する。
- 一つの `interview` artifact には one essential question / 一つの本質的な質問だけを書く。回答によって新しい高影響な曖昧さが見つかった場合は、追加質問をこの file に増やさず、次の unanswered `interview` を作成する。
- trivial な yes/no は、重要な判断、後続反映、回答証跡が必要なら `interview` を使い、そうでなければ issue comment や `scratch` で足りる。
- 回答から複数質問の synthesis が必要になったら `disc`、追加調査が必要になったら `research`、長期判断が固まったら `adr` を新規作成する。

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - progress line の `review=` に表示する target state 名を受け入れ条件へ入れるかが変わる。
  - `design.md`:
    - `progress_line(...)` の状態名 derivation と、`observer=` / `wait=` の別フィールド化要否が変わる。
  - `plan.md`:
    - failing test の期待文字列と、待機中 signal ゼロケースの test obligation が変わる。
  - `ADR`:
    - 不要見込み。Issue-local display contract decision として扱う。
- chat 上の軽微な一問では足りない理由:
  - 状態名は user-facing progress line に出るため、operator の次行動と誤操作リスクに影響する。回答は canonical docs と tests に反映される。

## 質問の目的 (必須)
- 対象者:
  - この PR observation workflow を dogfooding している operator / product owner。
- 何を明確にする質問か:
  - `@codex review` trigger 済みだが、Codex review の completion / comment signal がまだない状態を、progress line の `review=` で何と表示するか。
- 回答が後続判断へ与える影響:
  - `review=observing` 廃止後の primary display value、必要なら observer/wait state の別フィールド化、テスト期待値が決まる。

## 質問 (必須)
- pressure-test question:
  - `review=` は「監視対象の Codex review 状態」だけを表示し、観測者側の状態は必要なら別 key に逃がす、という方針でよいか。
- 質問:
  - Trigger comment は投稿済みだが、Codex review の completion / comment signal がまだ観測できない待機中状態を、progress line ではどの表記にしたいですか？
- 回答してほしいこと:
  - 推奨の表示値を 1 つ選ぶか、別案を指定してください。
  - `observer=` または `wait=` のような別フィールドを追加したいかも合わせて教えてください。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - GitHub issue #214 body。
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
  - `.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - `tests/unit/infra/test_init_update.py`
  - `20260619t064501z-research-review-progress-target-state-source-analysis.md`
- local context で解決できたこと:
  - `review=observing` は避けるべき。
  - `review=` は observer state ではなく target review state を表示すべき。
  - final JSON の `decision` / `decision_fingerprint` は authoritative のまま維持する。
  - 手動 `@codex review` 投稿、default `post-once`、snapshot read-only contract は非スコープ。
- まだ人間判断が必要な理由:
  - issue body は `triggered` / `pending_signal` / `no_completion_signal` を例示しているが、標準名を一つに確定していない。
  - 状態名は operator-facing な言葉であり、実装だけから最適な語を決めると利用者の認知に合わない可能性がある。

## 回答案 (必須)
- Option A:
  - `review=pending_signal`
  - 意味: trigger 済み / wait 中だが、completion / comment signal はまだない。
  - 長所: 「まだ signal 待ち」が明確で、`running` より断定しない。
  - 短所: 既存の internal status ではなく、新しい operator-facing 表示名になる。
- Option B:
  - `review=triggered`
  - 意味: `@codex review` trigger は投稿済み。
  - 長所: 手動再投稿が不要であることを強く示せる。
  - 短所: trigger 済み後に何を待っているかは弱い。
- Option C:
  - `review=none`
  - 意味: payload 上の target review status をそのまま表示する。
  - 長所: 実装上の状態を最も素直に出す。
  - 短所: trigger 済みなのに未起動に見え、今回の誤認を十分に防げない可能性がある。
- Option D:
  - `review=no_completion_signal`
  - 意味: completion signal がまだない。
  - 長所: 後段の `review_completion_unknown` との意味的連続性がある。
  - 短所: 初期 wait 中から出すにはやや重く、terminal-like unknown と混同しうる。

## Codex の分析 (必須)
- 判断軸:
  - operator が手動 `@codex review` を再投稿しないで済むか。
  - GitHub / Codex 側の処理中を過剰に断定しないか。
  - final JSON authoritative contract と混同しないか。
  - progress line の bounded ASCII key/value summary に収まるか。
- tradeoff:
  - `triggered` は誤再投稿を防ぎやすいが、signal 待ちの状態説明が薄い。
  - `pending_signal` は実際の待ち状態をよく表すが、新しい表示語として requirement / tests へ固定する必要がある。
  - `none` は既存 payload への忠実度が高いが、operator-facing clarity は低い。
- リスク:
  - 表示名が曖昧だと、今回と同じく手動 trigger 追加や trigger boundary 混乱を再発させる。
  - `review_completion_unknown` と近すぎる名前にすると、latency guard 後の human gate と通常 wait 中の区別が曖昧になる。
- 具体シナリオ / edge case:
  - `phase=wait ci=running review=pending_signal comments=0 threads=0 unresolved=0`
  - `phase=wait ci=passed review=pending_signal comments=0 threads=0 unresolved=0`
  - `phase=terminal ci=passed review=unresolved comments=4 threads=3 unresolved=3`

## Codex の推奨案 (必須)
- 推奨:
  - Option A: `review=pending_signal`
  - observer 側の状態は、今回は追加しない。必要なら将来 `wait=active` を別 issue / design decision として扱う。
- 理由:
  - `pending_signal` は「trigger 済みだが Codex review completion / comment signal 待ち」という operator-facing 目的に近く、`running` のように処理中を断定しない。
  - `review=observing` の問題を直接解消しつつ、`review_completion_unknown` の terminal-like human gate とは区別しやすい。
  - progress line の既存 key set を増やさずに済むため、line budget と drop order への影響が小さい。
- 未回答時の影響:
  - requirement / design / plan の具体化で表示名を仮置きする必要があり、後から test expectation と docs の修正が発生する可能性がある。

## ユーザー回答 (回答後に必須)
- answer capture:
  - `review=pending_signal` を採用する。
  - `review=` は観測者側の状態ではなく、観測対象である Codex review の状態を表示する。
- 回答:
  - 「review=pending_signal これが良いと思います。観測する自分の状態を表示するのではなくて、観測対象の状態を表示するべきです。」
- 回答日時:
  - 2026-06-19

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - no
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - none

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md` Evidence Adoption Ledger / Spec Authoring Gate
- 採用 / 棄却 / deferred の理由:
  - ユーザーが operator-facing 表示値として `review=pending_signal` を承認し、`review=` は observer state ではなく target state を表示するべきだと明示したため。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - `review=observing` を廃止し、trigger 済みだが Codex review completion / comment signal がまだない状態を `review=pending_signal` と表示する acceptance criteria を追加する。
- `design.md`:
  - `progress_line(...)` の `review=` は target review state を表示し、observer state で上書きしない。signal 待ち状態は `pending_signal` として導出する。
- `plan.md`:
  - 既存 `review=observing` expectation を red / regression test として更新し、`review=pending_signal` を検出する step を置く。
- `ADR`:
  - 不要。Issue-local display contract decision として扱う。
- reflected_to 更新方針:
  - Canonical docs authoring 時に front matter `reflected_to` と `report.md` adoption evidence を更新する。
- adoption reflection:
  - `review=pending_signal` is user-approved for the no-completion/comment-signal wait state after a trigger.

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
