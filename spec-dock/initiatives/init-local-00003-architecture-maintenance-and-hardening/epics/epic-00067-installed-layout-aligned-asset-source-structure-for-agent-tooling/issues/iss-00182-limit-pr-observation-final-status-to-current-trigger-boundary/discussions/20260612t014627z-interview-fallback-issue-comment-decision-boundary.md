---
種別: interview
ID: "20260612t014627z-interview"
タイトル: "Fallback issue comment decision boundary"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-06-12"
親: ["iss-00182"]
関連: ["20260612t012333z-research", "PR #181", "Issue #182"]
scope: "issue"
scope_id: "iss-00182"
created_at: "2026-06-12T01:46:27Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "20260612t012333z-research-pr-observation-final-output-boundary-analysis.md"
reflected_to:
  - "requirement.md"
---

# 20260612t014627z-interview Fallback issue comment decision boundary

## 正式質問として扱う理由

- 影響する artifact:
  - `requirement.md`:
    - final status / `overall_status` / `recommended_next_action` の受け入れ条件が変わる。
    - `fallback_issue_comment` を success 相当にするか、human gate として残すかで必須要件が変わる。
  - `design.md`:
    - `classify_snapshot()` / `classify()` の decision rule と、`review.decision` などの出力 contract が変わる。
    - `status_reason` / `decision_fingerprint` の扱いが変わる。
  - `plan.md`:
    - red test / characterization test の期待値が変わる。
    - fallback issue comment のケースを pass 系にするか wait_or_resume 系にするかで実装ステップが変わる。
  - `ADR`:
    - 現時点では必須ではないが、PR review と issue comment の信頼境界を長期 contract として固定するなら ADR 候補になる。
- chat 上の軽微な一問では足りない理由:
  - これは表面的な表示文言ではなく、PR observation が自動的に merge-ready 判断へ進めるかどうかに関わる運用境界である。
  - 一度要件化すると、後続の script output、workflow gate、reviewer handoff の解釈に影響する。

## 質問の目的

- 対象者:
  - `github-pr-observation` を運用する maintainer / user。
- 何を明確にする質問か:
  - current trigger / resume boundary に含まれる Codex の issue comment を、submitted PR review がない場合でも final decision の成功根拠として採用してよいか。
- 回答が後続判断へ与える影響:
  - `fallback_issue_comment` の final status を `human_gate` / `wait_or_resume` として維持するか、条件付きで pass / observation complete 相当に近づけるかが決まる。

## 質問

- pressure-test question:
  - `@codex review` 後に submitted PR review は作られず、Codex の issue comment だけが current boundary に現れ、その本文が「大きな問題なし」を示している場合、PR observation はそれを merge-ready に近い成功信号として扱うべきか。
- 質問:
  - `fallback_issue_comment` は、final decision でどの扱いにしますか。
- 回答してほしいこと:
  - 下記 Option A / B / C から、要件として採用したい方針を一つ選んでください。
  - 必要なら条件を追加してください。

## source-grounded context

- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/issue/design.md`
  - `spec-dock/active/issue/plan.md`
  - `spec-dock/active/issue/discussions/20260612t012333z-research-pr-observation-final-output-boundary-analysis.md`
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/design.md`
  - `spec-dock/active/initiative/requirement.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
- local context で解決できたこと:
  - historical review threads は `codex_review.collection_summary.review_threads` では current boundary から除外されている。
  - PR #181 の `human_gate` は historical unresolved thread が直接作ったというより、`completion_signal == "fallback_issue_comment"` の低信頼扱いが直接原因と見られる。
  - final JSON は decision-scoped artifacts と all-fetched history を同じ `review` 配下に混在させており、これは改善対象にすべき。
- まだ人間判断が必要な理由:
  - issue comment を PR review と同等または準同等に扱うかは、実装事実だけでは決まらない運用ポリシーである。
  - 安全側に倒すほど手動 resume / human gate が増え、信頼側に倒すほど自動完了判定のリスクが上がる。

## 回答案

- Option A: 現状維持寄り
  - `fallback_issue_comment` は submitted PR review ではないため、常に `human_gate` / `wait_or_resume` とする。
  - 今回の issue では、history と decision の分離、`status_reason` の明示、fingerprint 分離だけを行う。
- Option B: 条件付き成功信号
  - current boundary の Codex issue comment が明確な no-major-issues / pass 相当本文で、CI passed、head matched、blocking limitations なし、selected unresolved thread なしの場合は pass / observation complete 相当にする。
  - 曖昧な本文や pending 風の本文は `human_gate` / `wait_or_resume` のままにする。
- Option C: 中間案
  - top-level status は `human_gate` / `wait_or_resume` のまま維持する。
  - ただし `fallback_issue_comment` が current boundary 由来で、本文が問題なしを示す場合は、`review.decision` または `codex_review.lifecycle` に `fallback_pass_candidate` のような明示的な準成功信号を出す。
  - 最終 merge-ready 判定には使わないが、ユーザーと後続 agent が「古い thread 由来の human gate ではない」と判断できるようにする。

## Codex の分析

- 判断軸:
  - submitted PR review を primary completion とする既存方針を守るか。
  - issue comment の本文解釈を script が安全に自動判定できるか。
  - 自動 merge-ready 判定に近い surface へ進めるか、human gate を残すか。
  - 今回の主目的を output boundary 分離に限定するか、fallback completion policy まで踏み込むか。
- tradeoff:
  - Option A は最も安全だが、PR #181 のような「実質問題なし」コメントでも毎回 `wait_or_resume` になり、利便性は低い。
  - Option B は利便性が高いが、本文分類の誤判定や GitHub/Codex 側の出力揺れに弱い。
  - Option C は安全側を維持しつつ、なぜ `human_gate` なのかを明確にできる。将来 Option B に進める余地も残る。
- リスク:
  - Option B は merge readiness の過信につながる可能性がある。
  - Option A はこの issue の改善後も「なぜ gate なのか」が分かりにくいまま残る可能性がある。
  - Option C は出力 field が増えるため、contract naming を丁寧に固定する必要がある。
- 具体シナリオ / edge case:
  - PR #181 では CI passed / head matched / limitations empty / selected unresolved count 0 だが、`fallback_issue_comment` により `human_gate` になった。
  - このとき historical unresolved thread は final decision に混ぜない一方、fallback comment の信頼度をどう扱うかが別論点として残る。

## Codex の推奨案

- 推奨:
  - Option C。
- 理由:
  - 今回の issue の主目的は、current trigger / resume boundary の selected artifacts と historical context を分離し、final decision の根拠を誤読できないようにすること。
  - submitted PR review ではない issue comment を即 pass にするのは、この issue のスコープを「本文分類と成功判定ポリシー」へ広げる。
  - 一方で、`fallback_issue_comment` が current boundary 由来であり、古い thread 由来ではないことは出力で明確にする必要がある。
- 未回答時の影響:
  - 要件定義で `fallback_issue_comment` の受け入れ条件を固定できず、テスト期待値も決められない。

## ユーザー回答

- answer capture:
  - ユーザーは Option C を採用する、と回答した。
- 回答:
  - Option C: top-level は `human_gate` / `wait_or_resume` のまま維持する。
  - current boundary 由来の Codex issue comment が問題なしを示す場合は、`fallback_pass_candidate` のような準成功信号を出す。
  - この準成功信号は最終 merge-ready 判定には使わず、ユーザーと後続 agent が「古い thread 由来の human gate ではない」と判断できるようにする。
- 回答日時:
  - 2026-06-12

## 追加確認の要否

- 追加確認が必要か:
  - no
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - なし

## 採用判断

- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - Option C は、今回の issue の主目的である current trigger / resume boundary と historical context の分離を維持しつつ、`fallback_issue_comment` が current boundary 由来であることを出力上で説明できる。
  - submitted PR review ではない issue comment を即 pass 扱いにしないため、merge-ready 判定の信頼境界を急に広げない。
  - 将来 `fallback_issue_comment` を pass 相当に扱う場合にも、準成功信号を観測点として段階的に拡張できる。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意

- `requirement.md`:
  - `fallback_issue_comment` は top-level final status を pass / complete にしない。
  - current boundary 由来かつ問題なしを示す fallback comment は、準成功信号として観測可能にする。
  - historical unresolved thread 由来の gate と fallback confidence 由来の gate を区別できることを受け入れ条件に含める。
- `design.md`:
  - decision surface、history surface、status reason、fingerprint の設計へ反映する。
  - `fallback_pass_candidate` 相当の field 名と placement を設計で固定する。
  - top-level classification は `fallback_issue_comment` を `human_gate` / `wait_or_resume` として扱う。
- `plan.md`:
  - fallback issue comment のテスト期待値へ反映する。
  - CI passed / head matched / limitations empty / selected unresolved thread 0 / current fallback no-major-issues comment のケースで、top-level は `human_gate` のまま、準成功信号が出ることを固定する。
- `ADR`:
  - 現時点では不要。submitted PR review と issue comment の信頼境界を長期 contract として拡張する場合のみ検討する。
- reflected_to 更新方針:
  - `requirement.md` には反映済み。
  - 後続の issue planning で `design.md` / `plan.md` に反映した時点で `reflected_to` を追加更新する。
- adoption reflection:
  - Option C adopted. `requirement.md` の scope、受け入れ条件、用語、入力→出力例へ反映済み。
