# GPT-5.5 Pro 分析結果: Codex review trigger / completion observation

## 位置づけ

この artifact は、Chrome 上の ChatGPT `for codex app` Project で GPT-5.5 Pro / `じっくり思考 Pro` に依頼した分析結果を、`iss-00176` の技術調査として整理したものである。

- ChatGPT thread: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a26875f-8498-83a5-9c09-82cec07d08d9
- input package: `20260608t085332z-research-chatgpt55-pro-analysis-request-package.md`
- ChatGPT generation time: 約14分20秒
- 注意: 本資料は ChatGPT 出力を Codex が整理した research artifact である。ChatGPT 内で Web 参照されたリンクは記録するが、Codex 側で各ドキュメント本文を独立検証したものではない。

## ChatGPT が参照した主な公開情報

ChatGPT 出力上で引用・参照された主な URL は次の通り。

- OpenAI Codex GitHub integration docs: https://developers.openai.com/codex/integrations/github
- GitHub issue comments REST API: https://docs.github.com/rest/issues/comments
- GitHub reactions REST API: https://docs.github.com/rest/reference/reactions
- GitHub pull request reviews REST API: https://docs.github.com/rest/pulls/reviews
- GitHub pull request review comments REST API: https://docs.github.com/rest/pulls/comments
- GitHub GraphQL pull request reference: https://docs.github.com/en/graphql/reference/pulls
- GitHub check runs REST API: https://docs.github.com/en/rest/checks/runs?apiVersion=2026-03-10

## 結論

`iss-00176` の自然な実装方針は、既存の read-only snapshot collector を維持しつつ、固定 write boundary を持つ `trigger_codex_review.sh` を追加し、`wait_pr_observation.sh` が trigger + polling の state machine を統括する形である。

重要な補正点は次の通り。

1. Codex review completion の primary signal は、`Codex-authored submitted PR review` に置くべきである。
2. `eyes` reaction は start / running signal としては有用だが、completion primary にしてはいけない。
3. timestamp window だけでは複数 trigger の切り分けに弱い。
4. CI quiet window は review completion の代替ではなく、bounded fallback に降格すべきである。

ChatGPT は、OpenAI の Codex GitHub integration docs が `@codex review` 後に Codex が PR に GitHub code review を投稿する前提を示しているため、GitHub REST / GraphQL 上の Pull Request Review が最も durable な完了候補だと判断した。

一方で、Codex review の bot login、reaction の消滅タイミング、response comment の定型文は公開仕様としては未確認であり、実運用観測または fixture 化された実例で確認すべき事項として扱う。

## 技術的に取得可能な signal

### Trigger comment

- Source: PR issue comment
- API: `POST /repos/{owner}/{repo}/issues/{issue_number}/comments`
- Return fields: `id`, `node_id`, `html_url`, `user`, `created_at`, `updated_at`, `body`
- 用途:
  - `@codex review` の投稿
  - trigger comment id / created_at の固定
  - trigger window の起点
- 信頼性:
  - GitHub REST API として安定
  - write permission が必要

### Start / running signal

候補は複数あるが、primary ではなく補助 signal として扱う。

- Trigger comment reaction:
  - REST: issue comment reactions endpoint
  - GraphQL: `Reactable.reactions(content: EYES)` または `reactionGroups`
  - `eyes` reaction が付いた場合、Codex が trigger を受け取った可能性がある。
  - ただし「reaction が消えたら完了」という公開仕様は確認できない。
- Codex-authored issue comment:
  - `@codex review` 後の bot response comment がある場合は start / activity signal になり得る。
  - ただし文面・author login の定型性は未確認。
- PR review object:
  - `state=pending` または submitted review が見えれば review lifecycle signal になる。
  - submitted review が見えた場合は completion primary に昇格できる。

### Completion signal

Primary completion signal は `Codex-authored submitted PR review` とする。

- API:
  - REST: `GET /repos/{owner}/{repo}/pulls/{pull_number}/reviews`
  - GraphQL: PR `reviews`
- Key fields:
  - `id`
  - `node_id`
  - `user.login`
  - `body`
  - `state`
  - `submitted_at`
  - `commit_id`
- 判定:
  - Codex-authored である。
  - `submitted_at` が存在する。
  - `commit_id` が expected head SHA と整合する。
  - `submitted_at >= trigger_created_at`。
  - review state が `COMMENTED`, `CHANGES_REQUESTED`, `APPROVED` など submitted な状態である。

`review_comment.pull_request_review_id` を用いることで、inline review comments を submitted PR review に紐付けられる。

### Thread state

- API:
  - GraphQL `reviewThreads`
- Key fields:
  - `isResolved`
  - `isOutdated`
  - `isCollapsed`
  - `comments`
  - comment `databaseId`
  - comment author / createdAt / updatedAt
- 用途:
  - review comments の unresolved / resolved / outdated 判定
  - final JSON に human gate の理由を残す

### CI signal

- API:
  - check runs / statuses / statusCheckRollup
- 用途:
  - CI terminal 判定
  - review lifecycle とは独立して扱う
- 注意:
  - CI terminal と Codex review completion は別系統の GitHub object であり、CI quiet window は review completion の primary signal にならない。

## 推奨 state machine

ChatGPT は、CI と review を並列に観測しつつ、review lifecycle を trigger 中心で管理する state machine を提案した。

```text
init
  -> trigger_posting
  -> trigger_posted
  -> waiting_review_start
  -> review_running
  -> review_completed
  -> final_snapshot
  -> completed | human_gate | timeout | stale_head
```

CI 側は並列 sub-state とする。

```text
ci_unknown | ci_pending | ci_running | ci_passed | ci_failed | ci_stale
```

Review 側は次のように分ける。

```text
trigger_absent
trigger_posting
trigger_posted
waiting_start_signal
running_by_reaction
running_by_codex_activity
completed_by_submitted_review
fallback_waiting_quiet
fallback_completed
timeout
permission_denied
```

### 終了条件

正常終了の基本条件:

1. expected head SHA が変わっていない。
2. CI が terminal に到達している。
3. trigger comment が既知である。
4. Codex-authored submitted PR review が観測されている。
5. trigger 以後の selected review output を final snapshot として収集済みである。

Fallback 終了の条件:

1. trigger は既知である。
2. Codex activity が一定時間変化していない。
3. reaction / issue comment / review comment / review thread / PR review の activity が bounded quiet window で安定している。
4. ただし final JSON では `completion_signal=fallback_quiet_window` のように、primary completion ではないことを明示する。

## 推奨 GitHub API / CLI calls

### Trigger posting

`gh pr comment` よりも、`gh api` で REST endpoint を固定して呼ぶ方がよい。

理由:

- response JSON から `id`, `node_id`, `created_at`, `html_url` を確実に取得しやすい。
- endpoint と body を script 側で固定でき、安全境界を作りやすい。
- arbitrary `gh` arguments を受け付けない方針と相性がよい。

推奨 call:

```sh
gh api \
  --method POST \
  "repos/${owner}/${repo}/issues/${pr}/comments" \
  -f body='@codex review'
```

ただし、実装では raw `owner`, `repo`, `pr`, `body` を自由入力にせず、既存の strict validation と同等の validation を行う。

### Snapshot / review collection

既存 collector の REST / GraphQL 呼び出しは維持しつつ、次を追加する。

- trigger issue comment reactions
- trigger 後 issue comments
- Codex-authored PR reviews
- PR review comments
- GraphQL review threads
- pagination
- author / commit / timestamp / review id による selection

## Trigger posting の安全境界

推奨は、arbitrary GitHub write を一切許可せず、固定 endpoint + 固定 body のみ許可することである。

### 新規 script

`src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/trigger_codex_review.sh`

または public entrypoint として:

`src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh`

どちらにするかは、ユーザーが単体で trigger だけ使う必要があるかで決める。ChatGPT の提案では、public entrypoint として追加してもよいが、arbitrary write を許さない contract を明記すべきとされた。

### Options

```text
--repo OWNER/REPO
--pr NUMBER
--head-sha SHA
--mode post|never|reuse-explicit|reuse-latest
--dry-run
```

最小実装では `post|never` から始め、`reuse-latest` は ambiguity が大きいため慎重に扱う。

### 出力

stdout は exactly one JSON。

```json
{
  "script": "trigger_codex_review.sh",
  "status": "posted",
  "repo": "owner/repo",
  "pr": 123,
  "expected_head_sha": "...",
  "trigger": {
    "action": "posted",
    "body": "@codex review",
    "comment_id": 123,
    "node_id": "...",
    "html_url": "...",
    "created_at": "...",
    "author": "..."
  },
  "limitations": []
}
```

## Review output collection の scope

timestamp window だけではなく、複合 scope にする。

推奨 scope:

1. `trigger_comment_id`
2. `trigger_created_at`
3. `expected_head_sha`
4. Codex author filter
5. submitted PR review id
6. `pull_request_review_id`
7. GraphQL review thread join

### 選択ルール

`selected_reviews`:

- `codex_authored=true`
- `submitted_at >= trigger_created_at`
- `commit_id` が expected head SHA と整合
- `state != DISMISSED`

`selected_review_comments`:

- `pull_request_review_id` が selected review id と一致するものを最優先
- fallback として `created_at >= trigger_created_at` かつ `codex_authored=true` かつ commit SHA 整合

`selected_issue_comments`:

- trigger command 自体は除外
- Codex-authored
- `created_at` または `updated_at >= trigger_created_at`
- response comment として扱うが、completion primary にはしない

`selected_threads`:

- selected review comments の comment id / thread id と GraphQL reviewThreads を join
- thread state を final JSON に含める

## Completion condition の best practice

Primary:

```text
completed_by_submitted_review
```

条件:

- Codex-authored PR review が存在
- submitted review である
- trigger 以後に submitted
- expected head SHA と整合
- final snapshot で review comments / threads を収集済み

Secondary:

```text
running_by_reaction
running_by_codex_issue_comment
running_by_codex_activity
```

Fallback:

```text
fallback_completed_by_quiet_window
```

Fallback は成功扱いにしすぎない。final JSON に confidence / completion signal / limitation を明示する。

```json
{
  "codex_review": {
    "lifecycle": {
      "status": "fallback_completed",
      "completion_signal": "bounded_quiet_window",
      "confidence": "low"
    }
  }
}
```

## Timeout policy

timeout は階層化する。

- `review-start-timeout-seconds`
  - trigger 後、reaction / Codex comment / PR review / review comment が何も出ない場合
- `review-completion-timeout-seconds`
  - start signal はあるが submitted PR review が出ない場合
- `quiet-seconds`
  - fallback completed に入るための activity quiet window
- `timeout-seconds`
  - script 全体 deadline

Timeout 時は、stdout JSON を返し、stderr diagnostics と混ぜない。

## stdout JSON schema 追加案

既存 snapshot の上に、次を追加する。

```json
{
  "trigger": {
    "action": "posted|reused_explicit|reused_latest|never|dry_run|failed",
    "comment_id": 123,
    "node_id": "...",
    "created_at": "...",
    "html_url": "...",
    "author": "...",
    "body_sha256": "...",
    "expected_head_sha": "..."
  },
  "codex_review": {
    "lifecycle": {
      "status": "not_started|waiting_start|running|completed|fallback_completed|timeout|permission_denied|unknown",
      "start_signal": "eyes_reaction|codex_issue_comment|codex_review_activity|submitted_review|none",
      "completion_signal": "submitted_pull_request_review|bounded_quiet_window|timeout|none",
      "confidence": "high|medium|low",
      "started_at": "...",
      "completed_at": "...",
      "last_activity_at": "...",
      "selected_review_ids": [],
      "selected_review_comment_ids": [],
      "limitations": []
    }
  },
  "review": {
    "output_scope": {
      "mode": "trigger_review",
      "trigger_comment_id": 123,
      "expected_head_sha": "...",
      "selection_rules": [
        "codex_authored",
        "submitted_review_after_trigger",
        "commit_matches_expected_head",
        "review_comment_joined_by_pull_request_review_id"
      ]
    }
  }
}
```

## stderr progress 追加案

stderr は machine-friendly key/value line とする。

例:

```text
pr_obs poll=6 elapsed=03m00s remain=27m00s phase=review_running trigger=posted review=running start=eyes completion=none activity=2 comments=1 reviews=0 ci=running checks=3/5 quiet=00m30s final=stdout_json
```

完了後:

```text
pr_obs poll=12 elapsed=06m00s phase=finalizing trigger=posted review=completed completion=submitted_review reviews=1 comments=4 ci=passed final=stdout_json
```

Fallback:

```text
pr_obs poll=20 elapsed=10m00s phase=finalizing trigger=posted review=fallback completion=quiet confidence=low activity=3 ci=passed final=stdout_json
```

## 実装ステップ案

### Step 1: `SKILL.md` の contract 更新

対象:

- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`

変更:

- read-only skill ではなく、fixed trigger write + read-only observation skill として再定義する。
- arbitrary GitHub write は許可しない。
- `@codex review` 固定投稿のみを許可する。
- stdout / stderr contract は維持する。

### Step 2: `trigger_codex_review.sh` 追加

対象候補:

- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh`
- または `scripts/lib/trigger_codex_review.sh`

責務:

- repo / pr / head-sha validation
- current PR head の確認
- fixed REST POST
- result JSON 出力
- permission / rate limit / validation failure の JSON 化

### Step 3: `wait_pr_observation.sh` を orchestrator 化

対象:

- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`

追加 option:

```text
--trigger-mode post|never|reuse-explicit|reuse-latest
--review-start-timeout-seconds NUMBER
--review-completion-timeout-seconds NUMBER
```

責務:

- trigger posting / reuse
- trigger metadata を `fetch_pr_observation_snapshot.sh` に渡す
- review lifecycle state の管理
- CI と review の並列 terminal 判定
- final snapshot の取得

### Step 4: `fetch_pr_observation_snapshot.sh` は read-only aggregator のまま拡張

対象:

- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh`

責務:

- trigger metadata を review collector に渡す
- checks collector / review collector の JSON を統合する
- final PR metadata で stale head を検知する

### Step 5: `fetch_pr_review_snapshot.sh` を lifecycle signal collector に拡張

対象:

- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`

追加責務:

- trigger issue comment reactions 取得
- trigger 後 issue comments を Codex author で filter
- PR reviews を submitted_at / commit_id / author で filter
- PR review comments を `pull_request_review_id` primary で filter
- GraphQL reviewThreads を selected comments に join
- `signals` と `selected_output` を分けて返す

内部構造案:

```json
{
  "trigger": {
    "known": true,
    "comment_id": 123,
    "created_at": "..."
  },
  "signals": {
    "start_candidates": [],
    "completion_candidates": [],
    "activity": [],
    "reaction": {}
  },
  "output": {
    "selected_reviews": [],
    "selected_review_comments": [],
    "selected_issue_comments": [],
    "selected_threads": []
  },
  "limitations": []
}
```

### Step 6: `fetch_pr_checks_snapshot.sh` の terminal classification を明示

対象:

- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`

追加案:

```json
{
  "ci": {
    "terminal": true,
    "status": "completed|running|pending|zero_checks|stale|failed",
    "conclusion": "success|failure|neutral|mixed|unknown",
    "last_activity_at": "..."
  }
}
```

## テストケース案

`gh` stub を中心に hermetic tests を作る。

Stub 要件:

- `gh pr view` と `gh api` を区別する。
- `POST /issues/{pr}/comments` の body が exactly `{"body":"@codex review"}` であることを assert する。
- pagination を fixture で再現する。
- poll number に応じて response を変える。
- stderr に diagnostics を出しても stdout JSON を汚さない。
- 403 / 404 / 410 / 422 / secondary rate limit を返せる。

必須テスト:

- trigger post success
- dry-run
- no-trigger backward compatibility
- explicit trigger reuse
- reuse latest trigger ambiguity
- reaction present then review submitted
- reaction absent but review submitted
- reaction present then disappears without review
- Codex issue comment only
- pending review then submitted
- multiple triggers with delayed old output
- stale head before trigger
- stale head after trigger
- CI completes before review
- review completes before CI
- CI failure while review running
- zero checks grace
- large PR pagination
- GraphQL thread pagination
- nested thread comments overflow
- permission failure posting
- rate limit
- body truncation
- stdout exactly one parseable JSON
- stderr progress contains phase / review / ci keys

## 受け入れるべき設計方針

この分析に基づき、今後の要件定義・設計では次を前提にするのがよい。

1. `github-pr-observation` は完全 read-only ではなく、固定 write boundary を持つ observation skill へ更新する。
2. `@codex review` 投稿は固定 endpoint / 固定 body の script に閉じ込める。
3. Review completion の primary は `Codex-authored submitted PR review` とする。
4. `eyes` reaction は start / running hint であり、completion primary ではない。
5. Review output scope は trigger timestamp だけではなく、trigger id / head SHA / Codex author / submitted review id / review comment id を組み合わせる。
6. CI terminal と review completion は別々に管理し、最終終了条件で合流させる。
7. quiet window は fallback として残してよいが、confidence low / inferred として JSON に明示する。

## 未確定事項

以下は ChatGPT も未確認として扱った事項であり、実装前または実装中に live PR / fixture で確認する必要がある。

- Codex review の GitHub author login の正確な値。
- `@codex review` 後の response comment の有無と文面。
- `eyes` reaction がどの comment に付くか。
- `eyes` reaction が消えるタイミング。
- OpenAI / Codex 側の review が PR review object として常に投稿されるか。
- private repo / permission 差による API 挙動。

## 次の planning への示唆

要件定義では、次を明確に分けて書く必要がある。

- confirmed completion:
  - Codex-authored submitted PR review が取得できた状態
- fallback completion:
  - submitted PR review は取れないが、bounded quiet window で activity が安定した状態
- human gate:
  - permission / rate limit / ambiguous trigger / stale head / no Codex response

また、既存の `fetch_pr_review_snapshot.sh` は trigger-window body collection の土台を持っているため、全面置換ではなく、lifecycle signal と selected output を追加する形がよい。
