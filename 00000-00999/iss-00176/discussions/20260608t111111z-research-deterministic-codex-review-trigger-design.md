# 決定的な `@codex review` trigger 投稿設計の追加分析

- 作成日: 2026-06-08
- 対象 Issue: `iss-00176 GitHub PR observation should trigger and wait for Codex review completion`
- 対象領域: `github-pr-observation` skill / `wait_pr_observation.sh` / `fetch_pr_observation_snapshot.sh`
- 分析依頼元: ユーザー追加懸念
- 分析者:
  - ChatGPT / GPT-5.5 Pro 相当の追加分析
  - Deep Consultant / Codex sub-agent analysis

## 目的

前回までの提案では、`github-pr-observation` skill に `@codex review` の固定投稿を許可し、PR observation の一部として Codex review を扱う方向が示された。

しかし、「スキルが投稿を許可する」だけでは、実際に投稿するかどうかが実行エージェントの判断やオプション選択に戻り、非決定的になる。今回の追加分析では、`wait_pr_observation.sh` を実行したときに、開始時点で機械的に1回だけ `@codex review` を投稿し、その `comment_id` / `created_at` を observation boundary として使うべきかを検討した。

## ユーザー懸念

- `@codex review` の固定投稿を skill に「許可」するだけでは不十分。
- 利用エージェントが投稿するかどうか、どのコメントを trigger とみなすかを判断する運用は非決定的。
- 決定的にするには、`wait_pr_observation.sh` の通常実行 path が、最初の1回だけ自動的・機械的に `@codex review` を投稿する必要がある。
- 投稿位置をどの script に置くか、どの責務境界にするかは分析が必要。

## 現行前提

- 対象 source of truth:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/`
- 現行 `SKILL.md` は read-only observation skill として説明されている。
- 現行 `wait_pr_observation.sh` は polling orchestrator であり、`--trigger-comment-id` / `--trigger-created-at` を受け取る器はあるが、自身では trigger comment を作成しない。
- 現行 `fetch_pr_observation_snapshot.sh` は read-only snapshot aggregator として、PR metadata / checks / review snapshot を統合する。
- 現行 `fetch_pr_review_snapshot.sh` には trigger command の推定や trigger window による filtering があるが、推定は決定的 trigger boundary の代替にはならない。

## ChatGPT 追加分析の要約

ChatGPT は、`trigger_codex_review.sh` を別 script として追加し、`wait_pr_observation.sh` の通常 path から必ず1回だけ内部呼び出しする案を推奨した。

主な理由:

- `wait_pr_observation.sh` に直書きすると実装は短いが、read / write / polling が混ざり、固定 write boundary が曖昧になる。
- 別 script にすると、許可される write が「固定 endpoint / 固定 body / 固定 JSON contract」に閉じる。
- ただし、利用者に `trigger_codex_review.sh` の任意実行を求める運用は避ける。通常 path では `wait_pr_observation.sh` が必ず内部呼び出しする。
- 通常 path は `always post once` に固定し、例外 path は resume / test / manual diagnosis のみに限定する。
- 同一 head SHA の既存 trigger 自動 reuse は避ける。古い run、手動投稿、別 automation、遅延 review output と混ざり、今回 run の因果関係が壊れる。
- `POST` 失敗時の blind retry は避ける。投稿済みなのに応答だけ失われた場合、二重投稿になる。
- `POST` 前後 snapshot 差分で recovery できる場合だけ採用し、曖昧なら fail closed にする。
- `stdout` は final JSON のみ、`stderr` は bounded progress のみにする。

ChatGPT が挙げた重要な注意:

- 実装本文は `@codex review` の固定本文に寄せるのがよい。
- 公式挙動の詳細、Codex author login、reaction の扱い、PR review object との対応は未確認として扱う。
- completion primary は `Codex-authored submitted PR review` とし、quiet window は fallback / low confidence とする。

## Deep Consultant 分析の要約

Deep Consultant も、`wait_pr_observation.sh` を通常入口として開始時に必ず1回だけ `@codex review` を投稿し、その返却 `comment_id` / `created_at` を observation boundary にする設計を推奨した。

ただし、投稿処理は `wait_pr_observation.sh` に直書きせず、固定 write boundary の `scripts/trigger_codex_review.sh` として分離するべきだとした。

Deep Consultant が現行実装から確認した点:

- `SKILL.md` は read-only contract を掲げており、ここへ write を入れるなら「任意 write ではなく固定投稿だけ」と明示する必要がある。
- `wait_pr_observation.sh` はすでに polling state machine が大きく、validation / POST / head revalidation / polling / final classification / artifact 管理を全部抱えさせると境界が読みにくくなる。
- `fetch_pr_observation_snapshot.sh` はすでに trigger metadata を受け取り、review collector に渡せる構造なので、`wait` が trigger を作って metadata を渡す設計と噛み合う。
- 現行 `fetch_pr_review_snapshot.sh` には trigger 推定や trigger window の logic があるが、通常 path の決定性を担保するものではない。

Deep Consultant の主な提案:

- 通常 path は `post-once` 固定。
- 例外として `observe-existing` や `no-trigger` 相当を明示指定した場合のみ、既存 `trigger-comment-id` / `trigger-created-at` を使う。
- default mode で `--trigger-comment-id` が渡された場合は usage error か明示 mode 要求にする。
- idempotency は「同一 wait process 内で投稿を1回だけ」に限定する。
- 同一 head SHA の既存 trigger reuse は避ける。
- head SHA は投稿前 / 投稿直後 / 観測中の3段階で stale を検知する。
- `wait` が内部で呼んだ trigger script の stdout は外へ流さず、final JSON の `trigger` に統合する。

## 比較

| 論点 | 選択肢 | 決定性 | 副作用制御 | 評価 |
|---|---|---:|---:|---|
| trigger 実装位置 | `wait_pr_observation.sh` に直書き | 高 | 中 | 最小差分だが、write boundary が読みにくくなる |
| trigger 実装位置 | `trigger_codex_review.sh` を別 script にし、`wait` が必ず1回内部呼び出し | 高 | 高 | 採用。固定 write boundary と通常 path の決定性を両立できる |
| trigger 実装位置 | 利用者が `trigger_codex_review.sh` を任意実行してから `wait` | 低 | 中 | 非採用。エージェント判断に戻る |
| public contract | trigger mode を通常利用者に選ばせる | 低〜中 | 中 | 非採用。通常 path が非決定的になる |
| public contract | 通常 path は `post-once` 固定、例外だけ明示 option | 高 | 高 | 採用 |
| idempotency | 同一 head SHA の既存 trigger を自動 reuse | 中 | 一見高いが危険 | 非採用。run boundary が混ざる |
| idempotency | run ごとに新規 trigger を1件投稿 | 高 | 中 | 採用。今回 run の observation boundary が明確 |
| retry | `POST` 失敗時に blind retry | 低 | 低 | 非採用。二重投稿リスク |
| retry | `POST` 前後 snapshot 差分で recovery、曖昧なら fail closed | 高 | 高 | 採用候補 |

## 採用する統合案

### 1. 通常 path は `post-once` 固定

`wait_pr_observation.sh --repo OWNER/REPO --pr NUMBER --head-sha SHA ...` の通常実行は、実行開始時に `@codex review` を新規投稿する。利用者やエージェントは、通常 path で trigger 投稿有無を選ばない。

この投稿で返った `comment_id` / `created_at` が、その run の唯一の observation boundary になる。

### 2. 投稿処理は `trigger_codex_review.sh` に分離

`trigger_codex_review.sh` を追加し、固定 write boundary とする。

責務:

- `--repo` / `--pr` / `--head-sha` の validation。
- 投稿前 current head SHA 確認。
- 固定本文 `@codex review` の PR issue comment 投稿。
- 投稿後 current head SHA 再確認。
- stdout に trigger JSON を1個だけ返す。
- progress / diagnostics は stderr。

禁止:

- caller-provided body。
- body file。
- arbitrary endpoint。
- raw `gh` args。
- caller-provided GraphQL / jq / header / method。
- 通常 path での既存 trigger 自動 reuse。

### 3. `wait_pr_observation.sh` は trigger stdout を内部 capture する

`wait_pr_observation.sh` は通常 path で `trigger_codex_review.sh` を必ず1回だけ呼ぶ。

- trigger script の stdout は user-facing stdout へ流さない。
- trigger JSON を parse し、`comment_id` / `created_at` を `fetch_pr_observation_snapshot.sh` に渡す。
- final stdout JSON の `trigger` section に trigger metadata を統合する。
- `stderr` progress に `phase=trigger_posting` / `phase=trigger_posted` / `phase=waiting_review` / `phase=finalizing` などを出す。

### 4. 例外 path は明示する

既存 trigger を観測し直す必要がある場合は、通常 path とは別の明示 option にする。

候補:

- `--trigger-mode observe-existing`
- または `--observe-existing-trigger`

この例外 path では、`--trigger-comment-id` / `--trigger-created-at` の両方を必須にする。

default mode で `--trigger-comment-id` / `--trigger-created-at` が渡された場合は、暗黙 no-post にせず usage error とする。

### 5. 既存 trigger 自動 reuse はしない

同じ head SHA に既存の `@codex review` comment があっても、通常 path はそれを reuse しない。

理由:

- 前回 run の timeout 後に遅れて review が付いた可能性がある。
- 手動投稿や別 automation の trigger と混ざる可能性がある。
- 複数 trigger がある場合、review output と今回 run の対応が曖昧になる。
- 「今回 `wait_pr_observation.sh` を実行したことにより review が発生した」という因果関係を証明できない。

### 6. `POST` 失敗時は blind retry しない

GitHub comment POST は、client から失敗に見えても server 側では作成済みの可能性がある。

推奨:

- 投稿前 comments snapshot を取る。
- `POST` する。
- 成功したら返却 id / created_at を採用。
- `POST` が失敗した場合は、投稿後 comments snapshot を取る。
- 投稿前には存在せず、現在の actor による exact body `@codex review` comment が1件だけ増えていれば recovery として採用。
- 0件なら `trigger_failed_no_comment_observed`。
- 2件以上なら `trigger_failed_ambiguous_duplicate`。
- 曖昧な場合、2回目の POST はしない。

### 7. head SHA は3段階で検証する

| タイミング | 条件 | 挙動 |
|---|---|---|
| 投稿前 | current head が expected head と不一致 | 投稿せず `stale_head` / non-success |
| 投稿直後 | 投稿済みだが current head が変化 | trigger metadata を残し、`stale_head_after_trigger` / human gate |
| 観測中 | polling snapshot で head が変化 | `stale_head_during_observation` terminal |

投稿後に head が変わった場合、trigger comment を削除しない。削除は追加 write side effect であり、audit trail を壊す。

### 8. completion primary は submitted PR review

review completion の primary signal は、Codex-authored submitted PR review とする。

補助 signal:

- trigger comment への reaction。
- Codex-authored issue comment。
- Codex review comment activity。

fallback:

- bounded quiet window。

fallback は成功と同等に扱わず、`completion_signal=bounded_quiet_window` / `confidence=low` などを final JSON に明示する。

## stdout final JSON 案

`stdout` は最終的に1つの JSON text のみ。

追加 / 拡張候補:

```json
{
  "script": "wait_pr_observation.sh",
  "status": "passed",
  "overall_status": "passed",
  "expected_head_sha": "abc123...",
  "trigger": {
    "mode": "post-once",
    "action": "posted",
    "body": "@codex review",
    "comment_id": 1234567890,
    "created_at": "2026-06-08T00:00:00Z",
    "html_url": "https://github.com/OWNER/REPO/pull/123#issuecomment-1234567890",
    "head_sha_before_post": "abc123...",
    "head_sha_after_post": "abc123...",
    "recovered_after_post_error": false
  },
  "codex_review": {
    "lifecycle": {
      "status": "completed",
      "completion_signal": "submitted_pull_request_review",
      "confidence": "high",
      "selected_review_ids": [987654321],
      "selected_review_comment_ids": []
    }
  }
}
```

trigger failure / stale の場合も、可能な限り JSON で返す。

## stderr progress 案

`stderr` は bounded key/value summary とし、JSON authority にはしない。

例:

```text
pr_obs phase=trigger_posting repo=OWNER/REPO pr=123 expected_head=abc123
pr_obs phase=trigger_posted trigger=posted comment_id=1234567890 created_at=2026-06-08T00:00:00Z
pr_obs poll=1 elapsed=00m30s phase=waiting_review trigger=posted ci=running review=waiting quiet=00m00s
pr_obs poll=8 elapsed=04m00s phase=finalizing trigger=posted ci=passed review=completed completion=submitted_review
```

## 実装ステップ案

1. `SKILL.md` を read-only skill から「fixed trigger write + read-only observation」skill として更新する。
2. `scripts/trigger_codex_review.sh` を追加する。
3. `wait_pr_observation.sh` に default `post-once` orchestration を追加する。
4. `--trigger-comment-id` / `--trigger-created-at` の扱いを明示 mode 必須にする。
5. `fetch_pr_observation_snapshot.sh` は read-only aggregator のまま維持し、trigger metadata を受け取って review snapshot に渡す。
6. `fetch_pr_review_snapshot.sh` は trigger boundary / Codex-authored submitted review / selected review comments / fallback lifecycle を明確化する。
7. final JSON に `trigger` と `codex_review.lifecycle` を追加する。
8. `--out` 指定時は `trigger.json` などの debug artifact を残してよい。ただし authority は stdout final JSON。

## テスト観点

必須:

- default path で `trigger_codex_review.sh` が exactly once 呼ばれる。
- `POST` body が exactly `@codex review`。
- default path に `--trigger-comment-id` を渡すと usage error。
- observe-existing mode では trigger script が呼ばれない。
- observe-existing mode で trigger metadata が欠けると usage error。
- 投稿前 head mismatch では POST されない。
- 投稿直後 head mismatch では trigger metadata を残しつつ stale / non-success。
- polling 中 head mismatch では stale terminal。
- `POST` success 時に final JSON の `trigger` に `comment_id` / `created_at` が含まれる。
- `POST` failure 時に blind retry しない。
- `POST` failure 後、投稿前 snapshot になかった exact-body comment が1件だけ見つかる場合は recovery。
- `POST` failure 後、0件または複数件の場合は fail closed。
- trigger metadata が `fetch_pr_observation_snapshot.sh` に渡される。
- trigger window より前の review/comment は今回 run の output として採用されない。
- Codex-authored submitted PR review が completion primary になる。
- quiet window fallback は `confidence=low` として表現される。
- stdout は常に最終 JSON 1個だけ。
- stderr に trigger JSON が漏れない。
- `--out` artifact は stdout final JSON の authority を置き換えない。

## 採用判断

採用する。

最終的な設計方針:

> `github-pr-observation` の通常 workflow は、`wait_pr_observation.sh` 実行時に `@codex review` を決定的に1回投稿し、その返却 metadata を observation boundary として PR checks / Codex review lifecycle を観測する。投稿処理は `trigger_codex_review.sh` に閉じ込めるが、通常利用者に任意実行を求めず、`wait_pr_observation.sh` が必ず内部呼び出しする。

この方針により、以下を両立できる。

- エージェント判断に依存しない決定的 trigger。
- 固定 write boundary による安全性。
- run ごとの observation boundary の明確化。
- 既存 read-only snapshot collector の再利用。
- stdout final JSON / stderr progress contract の維持。

## 残る不確実性

- Codex の GitHub author login の正確な値。
- `@codex review` 投稿後の response issue comment の有無。
- `eyes` reaction の付与先と消滅タイミング。
- Codex review が常に GitHub PR review object として投稿されるか。
- private repo / permission / rate limit 時の API failure details。

ただし、これらは review lifecycle collector の詳細に影響する不確実性であり、trigger 投稿責務の配置判断は変えない。

