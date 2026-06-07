---
kind: research
created_by_role: consultant
scope_id: iss-00170
source_paths:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - src/spec_dock/assets/install_root/.agents/skills/github-codex-pr-review-comments/SKILL.md
  - src/spec_dock/assets/install_root/.agents/skills/github-codex-pr-review-comments/scripts/fetch_codex_pr_review_comments.sh
intended_targets:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/report.md
adoption_status: adopted
reflected_to:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/report.md
---

# Trigger Window Review Body And CI Detail Research

## 結論

最終 stdout JSON に review 本文と CI 失敗詳細を含めることは技術的に可能であり、むしろ `github-pr-observation` の安全な fixed wrapper を使う価値を高める。

ただし、PR の全コメントを毎回本文込みで出すと、古い review がノイズになり、stdout JSON が大きくなり、secret / internal URL / log 断片が保存されやすくなる。
そのため、`@codex review` trigger を観測 window の基準点として first-class に扱い、その trigger 後に付いた review/comment/thread/comment body だけを final JSON に含める設計がよい。

## 技術的に可能な取得方法

- PR metadata:
  - fixed REST GET で PR current head SHA、PR node id、PR metadata を取得する。
- PR conversation comments:
  - GitHub では Pull Request は Issue としても扱われるため、Issue comments API で PR conversation comments を取得できる。
  - `since` query は使えるが、最終的な window 判定は script 内で `created_at` / `updated_at` / comment id を見て行う。
- Pull request reviews:
  - Pull request reviews API で review state、submitted_at、commit_id、body を取得できる。
  - review body は raw markdown `body` として取得できる。
- Inline review comments:
  - Pull request review comments API で diff 上の inline comments を取得できる。
  - issue comments とは別 endpoint であり、raw markdown `body` を取得できる。
- Review thread state:
  - REST だけでは resolved / unresolved / outdated thread state の取得が弱い。
  - fixed GraphQL query を script 内部に閉じ込め、`reviewThreads` と thread の resolved/outdated state を取得するのが妥当。
  - caller から arbitrary GraphQL query は受け付けない。
- CI / check detail:
  - check runs は head SHA に対して取得でき、check run name、status、conclusion、details_url、html_url、check_suite などを出せる。
  - GitHub Actions run / jobs API を固定 GET で使うと、workflow run、job、failed steps まで出せる。

## Trigger window の推奨

推奨 input:

- `--trigger-comment-id`
- `--trigger-created-at`
- `--head-sha`

理由:

- `trigger_comment_id`:
  - trigger 自身を除外できる。
  - PR conversation comments の同一 timestamp tie-break に使える。
- `trigger_created_at`:
  - review、inline comments、review thread comments、workflow runs など、ID 空間が違う対象を横断する cutoff として使える。
- `head_sha`:
  - stale review / stale check を除外または分離する別軸。
  - trigger の代替ではなく、review / check が expected head に紐づくかを見る。
- `observation_start`:
  - fallback には使えるが、trigger 直後から script 起動までの comment を落としうるため primary にはしない。
- author classification:
  - Codex subset 判定には使うが、window boundary には使わない。

trigger が渡されない場合は、script が fixed logic で PR issue comments から最新の `@codex review` comment を探してよい。
この場合は `trigger.source=inferred` とし、`limitations` に `trigger_inferred` を出す。

## Body inclusion mode

推奨 default は `--body-mode trigger-window-truncated`。

- `none`:
  - metadata と `body_hash` のみ。
- `trigger-window-truncated`:
  - default。
  - trigger 後の review/comment body を stdout final JSON に含める。
  - item cap、per-item body char cap、total body char cap を適用する。
- `trigger-window-full`:
  - 明示 opt-in。
  - trigger window 内の body を可能な限り全文出力する。
  - stdout 肥大化リスクを final JSON の `limitations` / `body_policy` に明示する。
- `out-only`:
  - stdout は metadata + body hash。
  - `--out` 指定時だけ raw body artifact に出す。

推奨 cap:

- `max_items=50`
- `max_body_chars_per_item=12000`
- `max_total_body_chars=120000`

cap 超過時は、JSON validity を保ったまま、各 item に次を出す。

- `body_truncated`
- `body_original_length`
- `body_sha256`
- `omitted_reason`

全体 overflow として次を出す。

- `item_count_omitted`
- `body_chars_omitted`

## Final JSON schema 更新案

`reviews` は status summary と trigger-window body payload を分ける。

```json
{
  "trigger": {
    "source": "explicit",
    "comment_id": 123456,
    "created_at": "2026-06-08T01:23:45Z",
    "body_match": "@codex review"
  },
  "reviews": {
    "body_mode": "trigger-window-truncated",
    "thread_state_available": true,
    "trigger_window": {
      "cutoff_created_at": "2026-06-08T01:23:45Z",
      "items": [
        {
          "kind": "pull_review",
          "id": 80,
          "state": "CHANGES_REQUESTED",
          "author_login": "codex",
          "submitted_at": "2026-06-08T01:30:00Z",
          "commit_id": "expected-head-sha",
          "html_url": "https://github.com/OWNER/REPO/pull/123#pullrequestreview-80",
          "body": "review body",
          "body_truncated": false,
          "body_original_length": 11,
          "body_sha256": "sha256:..."
        }
      ],
      "overflow": {
        "item_count_omitted": 0,
        "body_chars_omitted": 0
      }
    }
  }
}
```

CI は summary counts とは別に `failures[]` を出す。

```json
{
  "ci": {
    "progress_status": "failed",
    "failures": [
      {
        "kind": "github_actions_job",
        "workflow_name": "CI",
        "workflow_run_id": 123,
        "job_name": "test",
        "job_id": 456,
        "conclusion": "failure",
        "failed_steps": [
          {
            "number": 7,
            "name": "Run tests",
            "conclusion": "failure"
          }
        ],
        "html_url": "https://github.com/OWNER/REPO/actions/runs/123/job/456"
      }
    ]
  }
}
```

## 設計へ反映すべきこと

- `wait_pr_observation.sh` / `fetch_pr_observation_snapshot.sh` に trigger window input を追加する。
- `--body-mode` を追加し、default を `trigger-window-truncated` とする。
- final JSON の `reviews.trigger_window.items[].body` に trigger 後の本文を含める。
- progress には body、URL、reviewer 名、個別 job 名を出さない。
- fingerprint は raw body ではなく `body_sha256` を使う。
- CI final JSON に workflow / job / failed step detail を出す。
- fixed REST GET / fixed GraphQL query は script 内部に閉じ込める。
- caller-provided endpoint / method / query / jq / raw gh args は引き続き禁止する。

## 受け入れ条件 / テスト案

- explicit trigger 指定時、trigger 前の old review body は final JSON に出ない。
- trigger 後の PR conversation comment body、inline review comment body、review body が body mode に応じて出る。
- 同 timestamp の PR conversation comment は `id > trigger_comment_id` のものだけ含む。
- `submitted_at >= cutoff` かつ `commit_id == expected_head_sha` の review を current-window として扱う。
- expected head SHA と一致しない review / check は stale として分離される。
- GraphQL thread state 取得失敗時も REST body collection は継続し、`thread_state_available=false` と limitation を出す。
- failed Actions run から workflow / job / failed step が final JSON に出る。
- body cap 超過時も valid JSON を維持し、truncation / overflow metadata を出す。
- stdout は final JSON only。
- stderr progress に body、URL、reviewer 名、job 名を混ぜない。
- caller-provided endpoint / method / query / jq / raw gh args を拒否する。

## 参照した一次情報

- GitHub REST API: Issue comments
  - https://docs.github.com/en/rest/issues/comments
- GitHub REST API: Pull request review comments
  - https://docs.github.com/en/rest/pulls/comments
- GitHub REST API: Pull request reviews
  - https://docs.github.com/en/rest/pulls/reviews
- GitHub REST API: Check runs
  - https://docs.github.com/en/rest/checks/runs
- GitHub REST API: Workflow runs / jobs
  - https://docs.github.com/en/rest/actions/workflow-runs
  - https://docs.github.com/en/rest/actions/workflow-jobs
- GitHub GraphQL: Pull request review threads
  - https://docs.github.com/en/graphql/reference/objects
