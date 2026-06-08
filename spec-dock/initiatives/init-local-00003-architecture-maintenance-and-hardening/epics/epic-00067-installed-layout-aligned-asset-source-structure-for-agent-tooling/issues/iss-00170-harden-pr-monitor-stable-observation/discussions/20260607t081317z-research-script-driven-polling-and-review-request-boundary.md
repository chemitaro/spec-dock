---
created_by_role: main-orchestrator
scope_id: iss-00170
artifact_type: research
source_paths:
  - /Users/iwasawayuuta/.codex/attachments/3b33d2f5-0c44-4685-9d52-14adccba51ce/pasted-text.txt
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/issue/discussions/20260607t063203z-research-gpt55-pr-monitor-stable-observation-discussion.md
  - spec-dock/active/issue/discussions/20260607t070628z-disc-system-architect-pr-monitor-stable-observation.md
  - spec-dock/active/issue/discussions/20260607t072057z-disc-implementation-plan-pr-monitor-stable-observation.md
intended_targets:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending
---

# リサーチ: スクリプト駆動 polling とレビュー依頼コメントの責務境界

この文書は、`iss-00170` の設計を見直すために共有されたサイドチャットの内容と、deep-consultant による分析結果を記録する research artifact である。
この文書自体は提案証跡であり、正式な `requirement.md`、`design.md`、`plan.md`、`report.md` への採用判断と反映は main orchestrator が行う。

## 1. サイドチャットで共有された問題提起

サイドチャットでは、現在の `iss-00170` の設計に対して、`pr-monitor` が polling loop を持つことへの懸念が提示された。

現在の設計は、概ね次の構造になっている。

```text
fetch_pr_stable_observation.sh
  - PR observation snapshot と fingerprint を1回分返す

pr-monitor agent
  - wrapper を複数回実行する
  - sleep / wait を行う
  - quiet window と same_fingerprint_count を評価する
  - timeout / stable / stale / unknown を判断する
```

この構造に対する懸念は、polling の継続判断が推論モデル側に残りすぎる点である。

- agent が毎回「待つか」「もう一度実行するか」「timeout とみなすか」「終了するか」を判断する。
- loop ごとに tool call と token budget を消費する。
- 待機間隔や終了条件が実行ごとに揺れる可能性がある。
- agent が早めに打ち切ったり、途中で方針を変えたり、安定前に要約してしまう可能性がある。
- 同じ入力でも、同じ待機条件・同じ判定になる保証が弱い。
- `pr-monitor` の責務が stable observation の要約ではなく polling orchestration に寄りすぎる。

サイドチャットで合意された方向性は、polling loop を script 側に寄せることである。

```text
snapshot helper
  - GitHub 状態を1回だけ取得する
  - checks / statuses / reviews / threads / review_requests を正規化する
  - fingerprint を出す

wait wrapper
  - snapshot helper を繰り返し呼ぶ
  - sleep / interval / timeout / quiet window / same fingerprint count を管理する
  - stable / timeout / stale_head / failed / review_state_unknown などの最終結果を返す

pr-monitor agent
  - wait wrapper を1回だけ実行する
  - final JSON を読む
  - caller へ要約・handoff する
```

サイドチャットで提示された望ましい command shape は次の通り。

```bash
wait_pr_stable_observation.sh --repo OWNER/REPO --pr 123 --head-sha abc123 --out /tmp/pr-monitor-123
```

推奨 default:

```text
--timeout-seconds        1800
--interval-seconds       30
--quiet-seconds          90
--same-fingerprint-count 2
--zero-check-grace-polls 2
```

重要な意味論:

- CI / check / status:
  - 観測された checks / statuses が terminal になるまで待つ。
- reviews / comments / threads:
  - 現在観測可能な review signals が quiet window の間変化しないことを待つ。
- review requests:
  - default では outstanding request として報告する。
  - 明示的な `--wait-review-requests` policy が指定された場合だけ待機対象にする。
- thread state unavailable:
  - default では success にしない。
  - `review_state_unknown` / human gate として返す。

出力は、最終的に parse する結果と途中経過を分けるべきである。

```text
stdout:
  final JSON only

--out/result.json または --out/final.json:
  stdout と同じ final JSON

--out/events.ndjson:
  poll ごとの重要イベントを1行1JSONで追記

--out/latest.json:
  最新 snapshot / 最新の中間判定

--out/snapshots/<timestamp>.json:
  必要に応じた poll ごとの snapshot

stderr:
  人間向けの軽い進捗ログのみ
```

サイドチャットの推奨は、まず bounded foreground wait を採用することだった。
foreground wait が実運用でつらくなった場合にだけ、background / job mode を follow-up として検討する。

## 2. Deep-Consultant の分析要約

deep-consultant の結論は明確だった。

- script-driven polling を採用する。
- `pr-monitor` に sleep / quiet window / fingerprint / timeout の判断を持たせない。
- `pr-monitor` は wait wrapper を1回実行し、final JSON を読み、要約と handoff だけを行う。

推奨 topology:

```text
.agents/skills/github-pr-stable-observation/scripts/
  wait_pr_stable_observation.sh          # pr-monitor が1回だけ呼ぶ公開 entrypoint
  fetch_pr_observation_snapshot.sh       # 単発 snapshot helper
  lib/fetch_pr_checks_snapshot.sh        # CI/check/status collector
  lib/fetch_pr_review_snapshot.sh        # review/comment/thread/request collector
```

重要なニュアンス:

- CI/CD と review の collection は、内部 collector として分ける方がシンプルで testable である。
- ただし、`pr-monitor` が呼ぶ公開 entrypoint は combined wait wrapper 1つにする。
- combined wait wrapper が統合結果を作ることで、CI と review の安定判定が同じ PR head SHA・同じ observation window に基づくことを保証しやすくなる。

`pr-monitor` が実行する推奨コマンド:

```bash
./.agents/skills/github-pr-stable-observation/scripts/wait_pr_stable_observation.sh \
  --repo OWNER/REPO \
  --pr 123 \
  --head-sha abc123 \
  --timeout-seconds 1800 \
  --poll-interval-seconds 20 \
  --quiet-seconds 90 \
  --same-fingerprint-count 2 \
  --out /tmp/spec-dock-pr-monitor-123
```

final JSON の主要 field:

```json
{
  "schema_version": "pr-stable-observation.wait.v1",
  "repo": "OWNER/REPO",
  "pr": 123,
  "head": {
    "expected_sha": "abc123",
    "current_sha": "abc123",
    "matches_expected": true,
    "changed_during_wait": false
  },
  "poll": {
    "iteration_count": 5,
    "quiet_seconds": 90,
    "same_fingerprint_required": 2,
    "same_fingerprint_count": 3,
    "snapshot_stable": true,
    "exit_reason": "stable"
  },
  "overall_status": "success",
  "normalized_status": "success",
  "observation_complete": true,
  "checks": {
    "normalized_status": "success",
    "counts": {}
  },
  "reviews": {
    "normalized_status": "success",
    "thread_state_available": true,
    "counts": {}
  },
  "limitations": [],
  "artifacts": {
    "events": ".../events.ndjson",
    "latest": ".../latest.json",
    "snapshots_dir": ".../snapshots",
    "final": ".../result.json"
  },
  "recommended_next_action": "human may evaluate merge readiness"
}
```

## 3. 推奨判断

### 3.1 Polling loop は script 側へ移す

採用する方針:

- `wait_pr_stable_observation.sh` が次を担当する。
  - loop
  - sleep interval
  - timeout
  - quiet window
  - same fingerprint count
  - zero-check grace
  - head-change detection
  - event writing
  - final status classification

`pr-monitor` が担当するのは次だけにする。

- wait wrapper を1回実行する。
- final JSON を parse する。
- `normalized_status` を要約する。
- artifact paths を handoff に含める。
- repair / human gate / merge-readiness evidence を caller へ返す。

却下寄りの案:

- `pr-monitor` が snapshot wrapper を繰り返し呼び、継続判断をする案。

理由:

- agent-driven loop は決定性が弱い。
- テストしにくい。
- 実行コストが高い。
- 途中打ち切りや方針 drift のリスクがある。

### 3.2 内部 collector は分け、公開 wait entrypoint は1つにする

採用する方針:

- 内部 collector を分ける。
  - `lib/fetch_pr_checks_snapshot.sh`
  - `lib/fetch_pr_review_snapshot.sh`
- combined snapshot を作る。
  - `fetch_pr_observation_snapshot.sh`
- combined wait を作る。
  - `wait_pr_stable_observation.sh`

却下寄りの案:

- 通常の `pr-monitor` path で、公開 `wait_pr_checks_stable.sh` と公開 `wait_pr_review_stable.sh` を別々に呼び、agent 側で統合する案。

理由:

- CI 側と review 側の stable window が同じ head SHA・同じ observation window に対するものだと保証しづらい。
- merge-prepared evidence としては combined wait result の方が強い。

条件付きであり得る案:

- checks-only / review-only の wait script は、debug 用または将来の専用 workflow 用なら有用。
- ただし merge-prepared evidence には、原則として combined wait wrapper の result を使う。

### 3.3 既存 Codex review wrapper は互換境界として維持する

採用する方針:

- `fetch_codex_pr_review_comments.sh` は既存の Codex-focused read-only comment/review retrieval として残す。
- これを all-purpose PR observation script へ変えない。

理由:

- 現在の名前と contract は、PR 全体の stable observation より狭い。
- 既存互換を保つ方が migration risk が低い。

### 3.4 `pr-monitor` と wait scripts は read-only のままにする

採用する方針:

- `pr-monitor` は read-only。
- `wait_pr_stable_observation.sh` は read-only。
- `fetch_pr_observation_snapshot.sh` と collector libs も read-only。

却下する案:

- `pr-monitor` から Codex review request comment を投稿する。
- wait / snapshot scripts から comment を投稿する。
- review collection failure 時に monitor が write operation へ fallback する。

理由:

- この issue の非交渉制約は read-only monitoring である。
- 初回 review request の write operation を monitor scripts に混ぜると、安全性、idempotency、retry、監査可能性が悪くなる。

### 3.5 初回レビュー依頼コメントは別の write-capable coordinator path に置く

この機能を今回または将来の scope に含める場合の推奨配置:

```text
.agents/skills/github-pr-review-requester/scripts/
  ensure_pr_codex_review_request_comment.sh
```

CLI 例:

```bash
ensure_pr_codex_review_request_comment.sh \
  --repo OWNER/REPO \
  --pr 123 \
  --head-sha abc123 \
  --request-key spec-dock:codex-review:abc123 \
  --execute \
  --out /tmp/spec-dock-pr-request-123
```

安全境界:

- default は dry-run。
- 実投稿には `--execute` を必須にする。
- comment body に idempotency marker を入れる。
- 同じ `repo/pr/head_sha/request-key` では二重投稿しない。
- output status を machine-readable に返す。
  - `posted`
  - `already_exists`
  - `skipped`
  - `failed`
- 失敗時は human gate にする。
- monitor 側では fallback 投稿しない。

最適な owner:

- `pr-monitor` ではなく `github-pr-merge-preparer`。

理由:

- `github-pr-merge-preparer` は PR creation / discovery、latest head SHA、repair loop、re-monitoring、human gate を既に調整する coordinator である。
- monitor 開始前に review request comment が必要か判断しやすい。
- write intent を処理した後に monitor を呼べる。

## 4. 要件・設計・計画への影響

### 4.1 要件定義書で必要な変更

現在の要件は概ね次の表現になっている。

```text
pr-monitor が複数 poll し、stable fingerprint を待つ。
```

これを次の表現へ変える必要がある。

```text
fixed wait wrapper が bounded stable observation を機械的に実行する。
pr-monitor は wait wrapper を1回だけ実行し、final JSON を要約する。
```

追加または修正すべき acceptance coverage:

- `wait_pr_stable_observation.sh` が機械的 loop owner であること。
- `fetch_pr_observation_snapshot.sh` が one-shot snapshot owner であること。
- stdout は final JSON only であること。
- `events.ndjson`、`latest.json`、`snapshots/`、`result.json` artifacts を出すこと。
- CI/check/status collector と review collector は script layer 内で分離されること。
- `pr-monitor` は no-loop / no-sleep / no-write / one-command usage に限定されること。
- 初回 review request comment は `pr-monitor` と wait scripts の外に置くこと。
- write-capable review request は follow-up または別の explicit opt-in scope とすること。

### 4.2 設計書で必要な変更

現在の D3 は次の意味になっている。

```text
stable 判定は wrapper 単発ではなく pr-monitor の複数 poll で行う。
```

これは次へ置き換える必要がある。

```text
stable 判定は wait_pr_stable_observation.sh が行う。
pr-monitor は wait wrapper を1回だけ呼ぶ。
```

script の名前と責務も分ける。

現在の案:

```text
fetch_pr_stable_observation.sh
```

推奨される新しい案:

```text
fetch_pr_observation_snapshot.sh
wait_pr_stable_observation.sh
```

もし旧名を残す場合は、互換 alias または deprecated path と明示する必要がある。

推奨 module map:

```text
github-pr-stable-observation/
  SKILL.md
  scripts/
    wait_pr_stable_observation.sh
    fetch_pr_observation_snapshot.sh
    lib/
      fetch_pr_checks_snapshot.sh
      fetch_pr_review_snapshot.sh
```

設計に追加すべき要素:

- event stream model
- final JSON schema version
- exit reasons
  - `stable`
  - `timeout`
  - `stale_head`
  - `check_failed`
  - `review_changes_requested`
  - `review_state_unknown`
  - `auth_failed`
  - `rate_limited`
  - `schema_mismatch`
  - `wrapper_error`
- final output に artifacts path を含めること。
- fake clock / fake snapshot による test strategy。

### 4.3 実装計画書で必要な変更

現在の S01/S02 は組み替える必要がある。

推奨される新しい順序:

- S01: snapshot helper と collector libs
  - one-shot JSON shape
  - checks/statuses collector
  - review/comment/thread/request collector
  - unsafe input tests
- S02: wait wrapper loop
  - fake clock / fake snapshot fixtures
  - timeout / interval / quiet window / same fingerprint count
  - stdout final JSON only
  - `events.ndjson`, `latest.json`, `snapshots/`
- S03: provider `pr-monitor` instructions
  - one wait command only
  - no direct polling
  - no direct API
  - no writes
  - final JSON parse / handoff
- S04: skill docs and dogfooding parity
- S05: final verification / report gates

## 5. 未確定事項

main user decision として残る論点:

- 初回 Codex review request comment 投稿をこの issue scope に含めるか。

推奨:

- ユーザーが明示的に scope を広げない限り、`iss-00170` には含めない。
- 含める場合でも、`pr-monitor` や wait scripts には入れない。
- `github-pr-merge-preparer` が所有する別の write-capable requester script として扱う。
- その script は `--execute` 必須、default dry-run、idempotency key 必須にする。

## 6. リサーチ結論

修正後の方向性は次の通りにすべきである。

```text
pr-monitor:
  read-only summarizer
  wait wrapper を1回だけ呼ぶ

wait_pr_stable_observation.sh:
  deterministic bounded loop owner
  stdout に final JSON のみを出す
  events/latest/snapshots/result artifacts を書く

fetch_pr_observation_snapshot.sh:
  one-shot normalized snapshot owner

lib/fetch_pr_checks_snapshot.sh:
  CI/check/status collector

lib/fetch_pr_review_snapshot.sh:
  review/comment/thread/request collector

初回 review request comment:
  pr-monitor と wait scripts の外側に置く
  github-pr-merge-preparer または follow-up の write-capable requester が所有する
```

この構造は、現在の agent-driven polling design よりも、決定性、テスト容易性、agent 実行コスト、途中打ち切りリスク、read-only monitoring boundary の面で優れている。
