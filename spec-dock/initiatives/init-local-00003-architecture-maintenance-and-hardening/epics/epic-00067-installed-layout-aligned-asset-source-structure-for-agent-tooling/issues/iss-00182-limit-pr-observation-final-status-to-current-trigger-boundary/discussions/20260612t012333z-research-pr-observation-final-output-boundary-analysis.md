---
種別: research
ID: "20260612t012333z-research"
タイトル: "PR observation final output boundary analysis"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-12"
親: ["iss-00182"]
関連: ["PR #181", "Issue #182", "iss-00180"]
authority: "synthesized"
derived_from:
  - "/private/tmp/iss-00180-pr181-observation-3/result.json"
  - "/private/tmp/iss-00180-pr181-observation-3/events.ndjson"
reflected_to: []
---

# 20260612t012333z-research PR observation final output boundary analysis

## 調査目的

PR #181 の監視ログで見つかった、`github-pr-observation` の final output / final status と trigger boundary の関係を整理する。

特に、直近の `@codex review` trigger または resume boundary を起点にした review だけを final decision に使いたい一方で、final JSON に古い review / thread が混在して見える問題について、事実・推測・未検証事項・実装影響を分けて残す。

## sources / 調査方法

- Evidence:
  - `/private/tmp/iss-00180-pr181-observation-3/result.json`
  - `/private/tmp/iss-00180-pr181-observation-3/events.ndjson`
- 実装確認対象:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
- 調査方式:
  - deep-consultant に read-only analysis を依頼した。
  - コード編集、ファイル作成、git 操作は deep-consultant 側では実施していない。

## facts / 観測できた事実

- `result.json` の top-level `status` / `overall_status` / `normalized_status` は `human_gate`。
- `recommended_next_action` は `wait_or_resume`。
- `observation_complete` は `false`。
- `limitations` は空。
- `current_head_sha` は `expected_head_sha` と一致している。
- CI は `passed`。
  - check runs は `success=4`, `failed=0`, `pending=0`, `running=0`。
- trigger は explicit。
  - `comment_id`: `4683116317`
  - `created_at`: `2026-06-11T17:16:48Z`
- `codex_review.lifecycle` は fallback 扱い。
  - `status`: `fallback`
  - `completion_signal`: `fallback_issue_comment`
  - `confidence`: `low`
  - `selected_review_ids`: `[]`
  - `selected_review_comment_ids`: `[]`
  - `selected_review_thread_ids`: `[]`
- `codex_review.collection_summary.review_threads` は current boundary の selected thread を 0 件として扱っている。
  - `selected_ids`: `[]`
  - `unresolved_count`: `0`
  - `unresolved_ids`: `[]`
  - 古い 3 thread は `boundary_before_or_equal_trigger` で除外されている。
- `review.signals` の current signal は、Codex による issue comment 1 件。
- `review.threads.items` には古い thread が 3 件残っている。
  - states は `outdated`, `unresolved`, `outdated`。
  - `review.threads.unresolved` は `1`。
- `review.codex_authored` は 6 件で、current boundary の selected artifacts だけではなく historical Codex-authored items も含む。
- `events.ndjson` には 20 件の poll event がある。
  - poll 1-19 は `normalized_status=running`。
  - poll 20 は `ci=passed`, `review=commented`, `normalized_status=human_gate`。
  - events だけでは detailed provenance が不足し、final decision の理由は `result.json` と実装側を見ないと追えない。
- 実装上、`fetch_pr_review_snapshot.sh` は trigger boundary 判定自体を持っている。
  - signal body は trigger 後でなければ `outside_trigger_window` になる。
  - `thread_after_trigger()` と `summarize_thread_collection()` により、`codex_review.collection_summary.review_threads.unresolved_count` は current boundary の thread だけを対象にする。
  - `selected_review_ids` / `selected_review_comment_ids` / `selected_review_thread_ids` は current status signal から作られる。
- 一方で、同じ payload の `review` 配下には all-fetched context も残る。
  - `review.signals` は historical signal を含む。
  - `review.codex_authored` は all signals と review requests から Codex-authored を集める。
  - `review.threads` は all GraphQL review threads の `total`, `unresolved`, `items` を持つ。
  - review collector の fingerprint も all signals / all codex_authored / all threads を含む。
- `fetch_pr_observation_snapshot.sh` の top-level classification は、CI passed 後に `completion_signal == "fallback_issue_comment"` を `human_gate` / `wait_or_resume` にする。
- `wait_pr_observation.sh` も同様に、`completion_signal == "fallback_issue_comment"` を `human_gate` / `wait_or_resume` にする。

## inference / 推測

- この evidence に限れば、top-level `human_gate` の直接原因は historical unresolved thread ではなく、current boundary の Codex issue comment を `fallback_issue_comment` として低信頼扱いしていることだと見るのが妥当。
- ただし、final JSON の `review.threads.items` と `review.threads.unresolved=1` が all-history で出ているため、利用者や後続ツールは historical unresolved thread が final decision に混ざったと誤解しやすい。
- fingerprint に all-history thread / signals が含まれるため、final decision には混ぜていなくても、wait の安定判定や resume 境界の揺れに historical context が影響する可能性がある。
- 現状の主要な設計問題は、decision-scoped artifacts と historical / all-fetched context が同じ `review` 配下に混在していること。

## unverified / 未検証事項

- fallback issue comment の本文、例えば "Didn't find any major issues" を pass 扱いしてよいかは未決定。
- 現行 `SKILL.md` は issue comments を fallback / supporting evidence としており、submitted PR review を primary completion としている。この方針を変えるかは仕様判断が必要。
- external consumer が `review.threads.items` や `review.codex_authored` を all-history として依存しているかは未確認。
- current boundary の human / unrelated unresolved thread を final decision に含めるべきか、Codex-selected artifacts のみに限定すべきかは未確定。

## question candidates / 質問候補

- fallback issue comment が "問題なし" を示している場合、submitted PR review がなくても final status を pass 相当にしてよいか。
- `review.threads` / `review.codex_authored` の既存 all-history 形状を互換性のため維持するか、別枠へ移すか。
- final decision の対象にする unresolved thread は Codex-selected artifacts に紐づくものだけでよいか。
- progress output に historical counts を表示する場合、どのラベルで audit context と分かるようにするか。

## terminology conflicts / 用語衝突

- `review`
  - 現状は decision-facing な status と all-fetched historical context の両方を含む。
  - requirement / design では `review.decision`, `review.current`, `review.history` のように役割を分ける必要がある。
- `unresolved`
  - `codex_review.collection_summary.review_threads.unresolved_count` は selected / current boundary scope。
  - `review.threads.unresolved` は all-fetched scope。
  - 同じ `unresolved` でも scope が異なるため、final output では明示が必要。
- `fingerprint`
  - 現状は audit context を含む可能性がある。
  - wait stability に使う fingerprint と debug / audit 用 fingerprint を分ける必要がある。

## edge cases / 具体シナリオ

- 最新 trigger 後に selected review / comment / thread が 0 件で、historical unresolved thread が 1 件ある。
  - final decision は historical thread を理由に `address_review_feedback` へ進まないこと。
  - selected unresolved count は 0 のままになること。
- fallback issue comment が current boundary にある。
  - 既存方針を維持するなら `recommended_next_action=wait_or_resume` とし、`status_reason=fallback_issue_comment` のように理由を明示すること。
- current selected Codex PR review comment に unresolved thread がある。
  - top-level は `human_gate` / `address_review_feedback` になり、selected thread id と unresolved id が一致すること。
- historical thread が解決または更新される。
  - decision に関係しない場合は `decision_fingerprint` が変わらないこと。
- all-fetched context を debug 用に残す。
  - `review.history` / `review.audit` などとして確認でき、final decision には混ぜないこと。

## implications / 判断への含意

- final decision の authoritative surface を明確に分離するべき。
- 推奨仕様:
  1. top-level `status` / `overall_status` / `normalized_status` は current trigger / resume boundary の decision artifacts だけから決める。
  2. decision artifacts は、少なくとも次に限定する。
     - head match / stale head
     - CI status
     - blocking limitations
     - `codex_review.lifecycle`
     - `selected_review_ids`
     - `selected_review_comment_ids`
     - `selected_review_thread_ids`
     - selected artifacts に紐づく unresolved thread
  3. historical / all-fetched context は別枠に出す。
     - 例: `review.history`, `review.audit`, `review.raw`, `review.context`
     - 既存互換のため当面 `review.threads` を残す場合も、`scope: "all_fetched"` を明示する。
  4. `review.codex_authored` は current と historical を分ける。
     - 例: `review.current.codex_authored`
     - 例: `review.history.codex_authored`
  5. `summary.review` は mixed / all-history status ではなく decision-facing status にする。
  6. fallback issue comment は selected PR review ではないため、当面は `human_gate` / `wait_or_resume` を維持してよい。ただし、その理由を `status_reason: "fallback_issue_comment"` のように明示する。
  7. fingerprint も分離する。
     - `decision_fingerprint`: final decision に影響する current boundary artifacts のみ。
     - `audit_fingerprint`: historical / all-fetched context を含む。
     - wait の quiet / stability 判定は原則 `decision_fingerprint` を使う。

## 実装影響範囲

- `fetch_pr_review_snapshot.sh`
  - `review` payload を decision / current / history に分離する。
  - `review.status` を decision scope に寄せるか、新規 `review.decision.status` を追加する。
  - `review.threads` の scope を明示し、current selected thread counts を別に出す。
  - fingerprint source を decision と audit に分ける。
- `fetch_pr_observation_snapshot.sh`
  - `classify_snapshot()` が mixed `review.status` ではなく decision surface を読むようにする。
  - top-level `summary.review` の意味を decision-facing に固定する。
- `wait_pr_observation.sh`
  - `classify()` と `review_progress_counts()` を decision scoped counts に寄せる。
  - progress line で historical thread count を出す場合は audit context として明示する。
- `SKILL.md`
  - Output Boundary / Observation Semantics に、final decision と historical context の境界を追記する。

## テスト観点

- 最新 trigger 後に selected review / comment / thread が 0 件、historical unresolved thread が 1 件あるケース。
  - top-level は historical thread を理由に `address_review_feedback` にならない。
  - `status_reason` は fallback など current reason になる。
  - selected unresolved count は 0。
- fallback issue comment が current boundary にあるケース。
  - `recommended_next_action=wait_or_resume`。
  - historical thread は decision に混ざらない。
- current selected Codex PR review comment に unresolved thread があるケース。
  - top-level は `human_gate` / `address_review_feedback`。
  - selected thread id と unresolved id が一致する。
- historical thread が解決または更新されても `decision_fingerprint` は変わらない。
- all-fetched context は `review.history` / `review.audit` で引き続き確認できる。
- progress stderr は historical counts を decision counts として表示しない。
- 既存の `fallback_issue_comment` 関連テストは、status の理由と action を明示する形に更新する。

## リスク/制約

- `review.threads.items` を all-fetched として読んでいる既存利用者がいる場合、移動・削除は breaking change になる。
- `review.codex_authored` が all-history であることに依存する debug tooling がある可能性がある。
- `summary.review` の意味を変えると、既存テストやログ比較が壊れる可能性がある。
- fallback issue comment を pass 扱いへ変える場合は、primary completion source を submitted PR review とする既存方針と衝突する。
- 互換性を優先するなら、まず additive migration がよい。
  - 新規 `decision` / `review.current` / `review.history` を追加する。
  - 既存 `review.threads` / `review.codex_authored` は残し、`scope: "all_fetched"` と deprecation note を付ける。
  - top-level decision は新規 decision surface から算出する。

## 結論

この evidence では、`human_gate` は historical unresolved thread が直接作ったものではなく、current boundary の `fallback_issue_comment` を低信頼 completion として扱った結果と判断するのが妥当。

ただし final JSON は、decision-scoped artifacts と historical / all-fetched context を同じ `review` 配下に混在させているため、status boundary と output boundary の設計問題は実在する。

iss-00182 では「final decision は current trigger / resume boundary の selected artifacts のみに基づく」「historical context は別枠に出しても final decision / fingerprint / progress には混ぜない」を中心仕様に据えるのがよい。

## 反映先

- まだ canonical `requirement.md` / `design.md` / `plan.md` には反映していない。
- 次工程で clarification または issue planning を行う際の source-grounded research として採用候補にする。
