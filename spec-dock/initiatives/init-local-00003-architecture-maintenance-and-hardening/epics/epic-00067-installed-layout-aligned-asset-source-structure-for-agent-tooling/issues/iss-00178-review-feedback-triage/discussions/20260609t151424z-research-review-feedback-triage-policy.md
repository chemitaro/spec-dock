---
種別: research
ID: "20260609t151424z-research"
タイトル: "Review Feedback Triage Policy"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-10"
親: ["iss-00178"]
関連: ["PR #177", "iss-00176"]
authority: "synthesized"
derived_from:
  - "gh pr view 177 --json number,title,state,mergedAt,baseRefName,headRefName,headRefOid,comments,reviews,url"
  - "gh api -X GET repos/chemitaro/spec-dock/pulls/177/comments --paginate"
  - "gh api -X GET repos/chemitaro/spec-dock/issues/177/comments --paginate"
  - "Deep Consultant: quality gate / workflow correctness analysis"
  - "Deep Consultant: development economics / review budget analysis"
reflected_to: []
---

# 20260609t151424z-research Review Feedback Triage Policy

## 調査目的

PR observation / PR merge preparation が Codex Review を最後まで捕捉できるようになったことで、P2 / P3 レビュー指摘の修正、再 push、CI/CD、再レビューのループが長期化しやすくなった。

このリサーチでは、直近の PR #177 の実レビューを根拠に、P0 / P1 以外のレビューをどのように扱うべきかを整理する。目的は、品質を落とさず、かつ「すべての P2 / P3 が消えるまで回す」運用を避けるための、実務的な triage policy を次 issue の要件定義・設計に渡すことである。

## sources / 調査方法

参照した実データ:

- PR #177: `feat(github-pr-observation): Codexレビューの起動と完了待機を統合`
- GitHub PR comments: `gh api -X GET repos/chemitaro/spec-dock/pulls/177/comments --paginate`
- GitHub issue comments: `gh api -X GET repos/chemitaro/spec-dock/issues/177/comments --paginate`
- GitHub PR reviews: `gh api -X GET repos/chemitaro/spec-dock/pulls/177/reviews --paginate`
- PR metadata: `gh pr view 177 --json number,title,state,mergedAt,baseRefName,headRefName,headRefOid,comments,reviews,url`

相談した Deep Consultant:

- Deep Consultant A: 品質ゲート、workflow correctness、safety、repeatability の観点で分析。
- Deep Consultant B: 開発速度、トークンコスト、再レビュー予算、停止条件の観点で分析。

## facts / 観測できた事実

PR #177 は 2026-06-09 に merge 済みであり、`github-pr-observation` に Codex review の deterministic trigger と completion wait を統合する PR だった。

PR #177 では、短時間に複数回の `@codex review` が実行された。

- `2026-06-09T10:06:15Z`: `@codex review`
- `2026-06-09T10:29:48Z`: `@codex review`
- `2026-06-09T10:52:49Z`: `@codex review`
- `2026-06-09T11:19:58Z`: `@codex review`
- `2026-06-09T11:40:52Z`: `@codex review`

PR review としては、少なくとも以下の review が観測された。

- `4457610911` on commit `3bddb903c5...`, submitted `2026-06-09T10:13:27Z`
- `4457778916` on commit `d736fc3038...`, submitted `2026-06-09T10:39:34Z`
- `4457920842` on commit `41ea375a62...`, submitted `2026-06-09T11:00:10Z`
- `4458117179` on commit `746ee12c1b...`, submitted `2026-06-09T11:32:06Z`

最後には Codex fallback issue comment として `Codex Review: Didn't find any major issues.` が投稿されていた。ただし、この最終状態に到達するまでに複数回の P2 / P3 指摘と修正ループが発生していた。

PR #177 の P2 / P3 指摘は、単なる style / polish よりも、PR observation workflow の決定性、冪等性、timeout、安全な外部副作用、review boundary の正しさに関わるものが多かった。

## PR #177 の review finding 分類

| # | Priority | 指摘 | 主なリスク分類 | 推奨 disposition | 理由 |
|---|---|---|---|---|---|
| 1 | P2 | Parse all paginated comment pages | runtime correctness / recovery correctness | `must_fix` | `gh api --paginate` が複数 JSON document を出す場合に before/after snapshot を信頼できず、POST 失敗 recovery が誤判定され得る。duplicate trigger や missed state に直結する。 |
| 2 | P2 | Bound the trigger helper with the wait timeout | hang / runaway risk | `must_fix` | trigger step が `--timeout-seconds` の外側にあると、bounded wait script が無期限に止まり得る。agent workflow の停止性に直撃する。 |
| 3 | P2 | Wait for Codex completion before human-gating comments | completion boundary / false human gate | `must_fix` | Codex review 完了前に generic feedback で early human_gate になると、「最後まで捕捉する」という PR 目的を壊す。 |
| 4 | P3 | Write --out artifacts on trigger failures | observability / auditability | `fix_if_low_cost` または `defer_followup` | trigger failure / stale head の診断 artifact が残らない問題。主要成功 path は壊さないため、低コストなら直し、高コストなら follow-up 化でよい。 |
| 5 | P2 | Preserve trigger metadata in final wait JSON | auditability / resume evidence | `fix_if_low_cost` または `must_fix` | `trigger.mode/action` が最終 JSON から落ちる問題。単なる監査性なら low-cost fix、resume 判断や duplicate 防止に使うなら must-fix。 |
| 6 | P2 | Filter unresolved thread ids to the trigger boundary | boundary correctness | `must_fix` | trigger 前の unresolved thread が boundary 内 unresolved として混入すると、agent が stale feedback を処理対象にしてしまう。 |
| 7 | P2 | Gate trigger posts on PR state | external side effect safety | `must_fix` | draft / non-open PR に不要な `@codex review` を投稿し得る。外部副作用があるため blocker 扱いが妥当。 |
| 8 | P2 | Kill trigger descendants on timeout | external side effect safety / timeout correctness | `must_fix` | timeout 後も descendant `gh` が生き残ると、script が `trigger_timeout` を返した後にコメント投稿され得る。fail-closed contract に反する。 |
| 9 | P2 | Do not hide review feedback while Codex is pending | human gate correctness | `must_fix` | 既存の actionable feedback を pending として隠すと、false pending / missed feedback が発生する。 |
| 10 | P2 | Preserve posted trigger after final metadata read fails | retry safety / duplicate trigger | `must_fix` | 投稿済み trigger を read-side failure で失敗扱いにすると、retry で duplicate trigger が起こり得る。 |
| 11 | P2 | Include resume metadata for fallback review waits | resume safety / duplicate trigger | `must_fix` | `wait_or_resume` なのに resume metadata がないと、caller が default `post-once` で再実行し duplicate trigger を作り得る。 |

この分類から、PR #177 における P2 の多くは「モデルの好み」や「より良い書き方」ではなく、deterministic automation の correctness に関わる実害ある指摘だったと判断できる。したがって、この PR で多くの P2 を修正した判断は妥当だった。

一方で、この事例は「P2 だから全部直すべき」という一般則を支持しない。PR #177 は PR review observation 自体が主機能だったため、P2 の多くが主機能の失敗モードに当たっただけである。別種の PR では、P2 / P3 の中に non-blocking な polish、operator clarity、rare edge、将来の保守改善が多く含まれ得る。

## Deep Consultant A: 品質ゲート観点の要約

品質ゲート観点では、severity label は入口情報に過ぎず、merge blocker かどうかは以下で判断するべきである。

- PR の主目的・受け入れ条件を直接壊すか。
- false pass / false fail / false human gate / missed feedback を生むか。
- GitHub コメント投稿、review trigger、branch state 変更などの外部副作用を重複・stale・不要に実行するか。
- retry / resume / rerun で duplicate trigger や状態喪失が起きるか。
- 無期限ハング、descendant process 残存、timeout 無効化があるか。
- 後続 agent / human が判断する artifact が欠けるか。
- 修正が局所的か、設計変更・PR scope 拡大を伴うか。

結論として、P2 / P3 は以下に分類するのが妥当である。

- `must_fix`: 主目的、冪等性、外部副作用、timeout、gate correctness、false pass / false escalation に関わる。
- `fix_if_low_cost`: 成功 path は壊さないが、artifact、診断性、小さな edge case を改善する。差分が小さいなら同 PR で直す。
- `defer_followup`: 正しい指摘だが、PR の主目的から外れる、設計判断が必要、修正が広がる、または別 issue にした方がレビューしやすい。
- `accept_risk_no_fix`: 既知リスクとして受け入れる。影響範囲、理由、再訪条件を artifact に残す場合だけ許可する。
- `false_positive` / `already_addressed`: 指摘の前提が誤り、既存コードで防げている、または reviewer が古い diff を見ている。根拠リンク、該当コード、テストで閉じる。

## Deep Consultant B: 開発速度・トークンコスト観点の要約

開発速度とトークンコストの観点では、Codex PR Review loop の成功条件を「no major issues になるまで回す」ことに置くべきではない。

より重要なのは、以下が人間に読める evidence として残っていることである。

- P0 / P1 がゼロである。
- P2 / P3 のうち merge-blocking risk に分類されたものがゼロである。
- 残存 P2 / P3 がすべて `fixed` / `follow-up issue` / `accepted no-fix` / `needs user decision` に分類されている。
- どの理由で自動ループを止めたかが明示されている。

推奨される予算・停止条件:

- Codex review request は原則最大 2 回。
- 自動修正 pass は原則最大 2 回。
- 監視時間は 1 PR あたり 30 分を目安にする。
- 自動修正差分が初回 PR 差分の 30% または 200 行を超えたら停止して人間判断へ渡す。
- 同種指摘が 2 回出たら、追加自動修正ではなく人間判断へ切り替える。
- 未分類 P2 / P3 が残っている状態では `merge-prepared` と言わない。
- 分類済み P2 / P3 が残っている状態では `review-clean` ではなく `merge-prepared` と表現してよい。

用語の区別:

- `review-clean`: Codex が no major issues / no actionable review を返した状態。
- `merge-prepared`: P0 / P1 がなく、残存 P2 / P3 が分類済みで、人間が最終 merge 判断できる状態。
- `human-decision-required`: 予算超過、設計判断、同種再発、PR scope 拡大などにより、agent が自動判断を止める状態。
- `blocked`: P0 / P1 または merge-blocking P2 / P3 が残っている状態。

## inference / 推奨方針

### 1. Severity だけで自動判断しない

P0 / P1 は原則 merge blocker でよい。一方、P2 / P3 は severity label だけでは不十分である。

P2 / P3 でも以下に該当する場合は `must_fix` とする。

- runtime correctness を壊す。
- deterministic automation を壊す。
- duplicate trigger / duplicate comment / stale trigger を起こす。
- retry / resume の冪等性を壊す。
- timeout / process lifecycle / bounded wait を壊す。
- review boundary / completion signal / human gate を誤らせる。
- false pass / false pending / missed feedback を生む。
- GitHub への外部副作用を誤って実行する。

逆に、P2 / P3 でも以下に該当する場合は同 PR 内で直さない選択肢を持つ。

- cosmetic / style / naming / refactor / polish に近い。
- operator clarity や report readability の改善だが、merge 判断に必要な情報は足りている。
- rare edge で実害が限定的、かつ回避策がある。
- 修正により PR scope が広がる。
- 新しい仕様判断や設計変更が必要。
- 差分が大きくなり、元 PR の reviewability を壊す。

### 2. Review finding disposition を必須化する

P2 / P3 を「直す / 直さない」の二択にせず、finding ごとに disposition を付ける。

推奨する disposition:

- `must_fix`: この PR の merge preparation 前に修正必須。
- `fix_if_low_cost`: 小さく安全に直せるなら直す。大きくなる場合は `defer_followup` へ変更。
- `defer_followup`: 正しい指摘だが、この PR では扱わず follow-up issue / future work にする。
- `accept_risk_no_fix`: 修正しない。理由、影響範囲、再訪条件を記録する。
- `false_positive`: 指摘の前提が誤り。
- `already_addressed`: 既に修正済み、または別の変更で解消済み。
- `needs_user_decision`: agent だけでは scope / risk / product priority を判断できない。

### 3. 自動修正条件を絞る

P2 / P3 の自動修正は、次をすべて満たす場合に限定する。

- 変更箇所が明確。
- 既存仕様と矛盾しない。
- 1-3 ファイル程度、50-100 行程度の局所差分で済む。
- テスト、snapshot、手動確認、または static inspection で閉じられる。
- 新しい設計判断を要求しない。
- 同種指摘が再発していない。

この条件を外れるものは、`needs_user_decision` または `defer_followup` とする。

### 4. Review loop budget を導入する

PR merge preparation は、無限に綺麗な状態を目指す工程ではなく、人間が merge 判断できる evidence を作る工程である。

推奨する初期 budget:

- Codex review request: 最大 2 回。
- 自動修正 pass: 最大 2 回。
- 累積 observation 時間: 30 分目安。
- 自動修正差分: 初回 PR 差分の 30% または 200 行を超えたら停止。
- 同種 risk class の再発: 2 回で停止し、人間判断へ渡す。

budget 超過時は失敗ではなく、状態を `human-decision-required` として、残存 finding と推奨判断を report に残す。

### 5. `review-clean` と `merge-prepared` を分ける

Codex Review が no major issues を返すことは望ましいが、merge preparation の必須条件にしない。

目標状態は以下のように分ける。

- `review-clean`: Codex Review が major issue を出していない。
- `merge-prepared`: blocker がなく、残存 finding が分類済みで、CI / required checks / review state / residual risk が報告され、人間が merge 判断できる。

`merge-prepared` は `review-clean` より現実的で、個人開発と agentic workflow のコストに合う。

## 推奨する次 issue のスコープ

この issue では、巨大な自動判定 AI を作るのではなく、最初に「review finding triage を人間と agent が同じ表で扱えるようにする」ことを狙うのがよい。

推奨スコープ:

1. `github-pr-merge-preparer` または該当する PR preparation workflow に Review Finding Triage Gate を追加する。
2. Codex Review から得られた finding を severity だけでなく risk class と disposition で整理する。
3. P0 / P1 は未解決なら blocker とする。
4. P2 は未分類なら merge-prepared 不可とする。
5. P2 / P3 の `must_fix` が残っている場合は blocked とする。
6. P2 / P3 の `defer_followup` / `accept_risk_no_fix` / `false_positive` / `already_addressed` は rationale と evidence がある場合だけ non-blocking とする。
7. review loop budget を report / PR body / final response に記録する。
8. budget 超過、同種再発、scope 拡大、設計判断が必要な場合は `human-decision-required` として止める。

## 推奨する出力 artifact

PR monitor / merge preparer / report には、少なくとも次の summary を残すべきである。

```md
## Review Loop Summary

- review requests: 3
- elapsed observation: 42m
- pushes after review: 2
- final state: merge-prepared
- blocking findings: 0
- residual P2/P3 findings: 3 classified
- stop reason: P0/P1 cleared and remaining P2/P3 classified

## Findings Disposition

| finding | priority | risk class | disposition | evidence |
|---|---:|---|---|---|
| timeout not bounded | P2 | hang/runaway | fixed | test: ... |
| duplicate trigger risk | P2 | automation safety | follow-up | issue: ... |
| report wording clarity | P3 | operator clarity | accepted no-fix | rationale: ... |

## Budget Gate

- review request budget: within budget
- automatic fix pass budget: exceeded
- human action needed: yes
```

この summary は PR body には短く、`report.md` には詳細に置くのがよい。PR body は merge 判断用、`report.md` は監査・次 agent への引き継ぎ用に分ける。

## question candidates / 質問候補

現時点では、次の初期方針を仮定して要件定義に進める。

- P0 / P1 は常時 blocker。
- P2 は triage 必須。
- P3 は原則 non-blocking だが、`must_fix` と分類された場合は blocker。
- 自動修正 pass と Codex review request は原則 2 回まで。
- `review-clean` ではなく `merge-prepared` を標準完了語にする。

人間に確認した方がよい候補:

- 初期 budget の具体値を固定するか、skill / workflow の推奨値に留めるか。
- `P2 未分類なら merge-prepared 不可` を hard gate にするか、warning にするか。
- `accept_risk_no_fix` にユーザー明示承認を必須にするか、agent rationale で許可するか。

## terminology conflicts / 用語衝突

`review-clean` と `merge-prepared` を区別しないと、Codex Review が no major issues を返すまで回すことが暗黙の成功条件になりやすい。

推奨する用語:

- `review-clean`: review tool から新たな actionable finding が出ていない状態。
- `merge-prepared`: human merge decision に必要な CI / review / residual risk / disposition evidence が揃っている状態。
- `blocked`: blocking finding が残っている状態。
- `human-decision-required`: agent が自動修正・自動 no-fix を続けるべきではない状態。

## edge cases / 具体シナリオ

### P2 だが must-fix の例

`@codex review` の duplicate trigger、timeout 無効、review completion の false gate、trigger boundary 混入などは、P2 でも must-fix とする。これらは review loop の便利さではなく、PR preparation workflow の安全性と決定性を壊すため。

### P2 だが follow-up の例

診断 artifact の追加、report readability の改善、operator UX の改善などは、主要成功 path と merge 判断に必要な evidence が満たされているなら follow-up にできる。

### P3 だが低コスト修正の例

`--out` failure artifact のように、失敗時の監査性に効き、差分が局所的なら P3 でも同 PR 内で直してよい。ただし、修正により workflow 設計が広がるなら follow-up がよい。

### P2 / P3 が同種再発する例

同じ risk class の指摘が再レビューで繰り返し出る場合、agent が逐次修正を続けるより、設計見直しまたは人間判断へ切り替える。これは、局所修正では根の設計問題を閉じられていない可能性が高いため。

## implications / 判断への含意

次 issue の要件定義では、以下を acceptance criteria に含めるのが望ましい。

- PR review finding に severity だけでなく risk class と disposition を持たせる。
- P0 / P1、および merge-blocking と分類された P2 / P3 が残る場合、merge-prepared としない。
- P2 / P3 を no-fix / follow-up にする場合、rationale、risk、evidence、revisit condition を必須にする。
- review loop budget と stop reason を report / PR body / final response のいずれかに残す。
- Codex Review が no major issues を返すことを絶対条件にせず、`merge-prepared` を human merge decision のための状態として定義する。

## リスク / 制約

この方針は review 指摘を軽視するためのものではない。むしろ P2 / P3 のうち実害があるものを確実に must-fix へ昇格し、非本質なものを根拠付きで止めるための運用である。

`accept_risk_no_fix` は濫用されると品質低下につながるため、理由、影響範囲、再訪条件、必要に応じたユーザー承認を必須にする必要がある。

完全自動分類は初期スコープにしない方がよい。まずは agent が分類表を作り、人間が読める evidence として残す workflow / artifact contract を作るのが安全である。

## 反映先候補

- `iss-00178` の `requirement.md`
- `iss-00178` の `design.md`
- `iss-00178` の `plan.md`
- `.agents/skills/github-pr-merge-preparer/SKILL.md`
- `.agents/skills/github-pr-observation/SKILL.md`
- `spec-dock/docs/workflow_issue.md` の PR Delivery Gate / Merge Preparation Gate 周辺
- 必要であれば ADR: review-clean と merge-prepared の分離、および P2 / P3 triage gate
