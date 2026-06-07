---
created_by_role: main-orchestrator
scope_id: iss-00170
artifact_type: research
source_paths:
  - spec-dock/active/issue/discussions/20260607t081317z-research-script-driven-polling-and-review-request-boundary.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
intended_targets:
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: pending
---

# リサーチ v2: 長時間 wait 中の progress delta と最終判定の分離

この文書は、`iss-00170` の script-driven polling 設計に対する追加分析を記録する。
v1 research では、`pr-monitor` が polling loop を持つのではなく、`wait_pr_stable_observation.sh` が deterministic な bounded polling loop を持つ方針を推奨した。
v2 では、長時間 foreground wait 中に agent / 人間が進捗を把握できるよう、poll ごとの経過時間と差分サマリーをどう出すべきかを検討する。

## 1. 追加の問題提起

`wait_pr_stable_observation.sh` は、30分程度の timeout と 20〜30秒程度の poll interval を持つ可能性がある。
この foreground wait が長く続くと、agent や人間には「何も起きていない」「止まっている」「どれくらい進んでいるのかわからない」と見える可能性がある。

特に agent は、人間のような自然な時間感覚を持たない。
そのため、最終 JSON だけを最後に受け取る設計は parse 契約としては堅い一方で、待機中の安心材料や進捗説明としては弱い。

追加したい観測性:

- poll 開始からの経過時間。
- timeout までの残り時間。
- 次の poll までの秒数。
- 今回の poll で捕捉した material な変化。
- 完了した workflow / check 名。
- pending -> success / failure などへ変化した check/status。
- review comment / review / thread / review request の増減。
- 新たに出た limitation、解消した limitation。
- 現時点の `normalized_status`。

ただし、全 raw data を live output に流すと context bloat を起こす。
そのため、live output は bounded summary にし、詳細は artifact に残すべきである。

## 2. Deep-Consultant の結論

結論:

- 採用すべき。
- `stdout final JSON only` は維持する。
- 進捗は `stderr` の bounded progress summary と、artifact の machine-readable delta に分離する。
- `pr-monitor` は progress を待機中の状況説明として扱うが、最終判断には使わない。
- 最終判断は command 終了後の stdout final JSON / `result.json` のみで行う。

推奨 command:

```bash
wait_pr_stable_observation.sh \
  --repo OWNER/REPO \
  --pr 123 \
  --head-sha abc123 \
  --out /tmp/spec-dock-pr-monitor-123 \
  --progress stderr-summary
```

推奨 option:

```text
--progress stderr-summary|stderr-jsonl|none
default: stderr-summary

--progress-max-items 5
--progress-max-line-bytes 800
```

`pr-monitor` は明示的に `--progress stderr-summary` を渡してよい。
ただし、progress line から success / failure / timeout を確定してはならない。

## 3. 出力契約

### 3.1 stdout

`stdout` は引き続き final JSON only とする。

```text
stdout:
  final JSON only
```

理由:

- `pr-monitor` が parse する authoritative な最終結果を1つに固定できる。
- 途中経過 JSON と final JSON が混ざらない。
- caller や tests が deterministic に扱える。

### 3.2 stderr

default の `stderr` は、人間と agent runtime 向けの bounded progress summary とする。

例:

```text
[pr-stable-observation] iter=4 elapsed=90s remaining=1710s next=30s status=pending stable=1/2 quiet=30/90 head=abc123 checks=7s/2p/0f/0u changed="CI / test pending->success; lint pending->failure" reviews="+1 comment +0 reviews threads 0 state_changes" limitations="+0 -0"
```

意味:

- `iter=4`: 4回目の poll。
- `elapsed=90s`: wait 開始から90秒経過。
- `remaining=1710s`: timeout まで残り1710秒。
- `next=30s`: 次の poll まで30秒。
- `status=pending`: 現時点の中間 status。
- `stable=1/2`: fingerprint が同じだった連続回数。
- `quiet=30/90`: quiet window の進捗。
- `checks=7s/2p/0f/0u`: checks/statuses の success / pending / failure / unknown count。
- `changed=...`: 今回 poll で material に変化した check/status 名と遷移。
- `reviews=...`: review signals の増減。
- `limitations=...`: limitation の新規発生 / 解消数。

stderr progress は non-authoritative signal である。
モデルや人間に「いま動いている」「何が変わったか」を見せるためのものであり、最終判定の source of truth ではない。

### 3.3 artifacts

`--out` 配下には、最終結果・全履歴・最新状態・最新差分を分けて保存する。

```text
--out/result.json          stdout と同じ final JSON
--out/events.ndjson        poll/event の durable JSONL audit
--out/latest.json          最新 snapshot + intermediate status
--out/latest_delta.json    最新 poll delta summary の machine-readable 版
--out/snapshots/           raw/normalized snapshots
```

`latest_delta.json` は追加する価値が高い。
stderr が runtime で表示されない場合やログが切れた場合でも、最新 poll の軽量な差分だけを確認できる。

役割分担:

- `result.json`:
  - final JSON。
  - stdout と同じ authoritative result。
- `events.ndjson`:
  - durable な全履歴。
  - debug / audit / postmortem 用。
- `latest.json`:
  - 最新 snapshot と中間 status。
  - 現在地確認用。
- `latest_delta.json`:
  - 最新 poll で何が変わったかの軽量 machine-readable summary。
  - agent / tooling が途中状態を低コストで確認するための artifact。
- `snapshots/`:
  - 必要に応じた poll ごとの raw / normalized snapshot。
  - live context に流さない詳細情報。

## 4. 形式比較

### 4.1 `stderr` human-readable progress

採用。

利点:

- stdout final JSON と衝突しない。
- transcript 上で人間にも agent にも読みやすい。
- 長時間 wait 中の安心材料になる。
- context bloat を `1 poll 1 line` で抑えられる。

注意:

- 最終判断には使わない。
- parse 必須の contract にしない。

### 4.2 `stderr` JSON lines

条件付き。

利点:

- programmatic live progress consumer には扱いやすい。

懸念:

- transcript 上では JSON が多くなりやすい。
- final JSON と心理的に混同しやすい。
- v1 の default としては重い。

推奨:

- option として `--progress stderr-jsonl` を用意してよい。
- default は `stderr-summary` とする。

### 4.3 `events.ndjson` only

不十分。

理由:

- 実行中の live output として見えない可能性がある。
- 今回の「長時間何も起きていないように見える」問題を解決しない。

採用位置:

- durable audit としては必須。
- live progress の代替にはしない。

### 4.4 `latest_delta.json`

採用。

利点:

- 最新差分だけを軽く確認できる。
- stderr が見えない runtime でも現在地を読める。
- retry/debug に効く。
- `events.ndjson` 全体を読む必要がない。

### 4.5 `--emit-progress`

`--progress` の方がよい。

理由:

- 短く、`none` も自然に表せる。
- 後から互換 alias として `--emit-progress` を足すことは可能。

## 5. `latest_delta.json` の推奨 schema

最小 schema:

```json
{
  "schema_version": "pr-stable-observation.delta.v1",
  "kind": "poll_delta",
  "iteration": 4,
  "elapsed_seconds": 90,
  "remaining_seconds": 1710,
  "next_poll_seconds": 30,
  "normalized_status": "pending",
  "head": {
    "expected_sha": "abc123",
    "current_sha": "abc123",
    "changed": false
  },
  "stability": {
    "same_fingerprint_count": 1,
    "required": 2,
    "quiet_seconds": 30,
    "quiet_required": 90
  },
  "checks": {
    "counts": {
      "success": 7,
      "pending": 2,
      "failure": 0,
      "unknown": 0
    },
    "changed": [
      {
        "name": "CI / test",
        "from": "pending",
        "to": "success"
      }
    ],
    "truncated": 0
  },
  "reviews": {
    "issue_comments_delta": 1,
    "review_comments_delta": 0,
    "reviews_delta": 0,
    "thread_state_changes": 0,
    "review_requests_delta": 0
  },
  "limitations": {
    "new": [],
    "resolved": []
  }
}
```

含めるべきもの:

- `iteration`
- `elapsed_seconds`
- `remaining_seconds`
- `next_poll_seconds`
- current `normalized_status`
- head expected/current/changed
- stability progress
- check/status counts
- material check/status changes
- review signal deltas
- limitation new/resolved

含めないもの:

- raw comment body
- full check payload
- full thread payload
- raw arrays
- 長い URL 群
- full logs

必要な詳細は `snapshots/` や `raw/` artifact に置く。

## 6. Context bloat を避ける制限

必須制限:

- stderr は poll ごとに1行だけ。
- default `--progress-max-items 5`。
- default `--progress-max-line-bytes 800`。
- check / review / thread 名は最大60 chars 程度で truncate。
- raw body、raw URL、raw arrays は stderr に出さない。
- `events.ndjson` は全 event を持ってよいが、stderr は poll summary + material changes + terminal summary に限定する。
- debug 相当の詳細は artifact のみに置く。

`progress-max-items` を超えた場合:

- stderr には代表的な changed items だけを出す。
- `latest_delta.json` の `truncated` に省略件数を入れる。
- full list は `latest.json` / `events.ndjson` / `snapshots/` に残す。

## 7. 要件・設計に採用すべき内容

この追加案は採用すべきである。
ただし、「progress から最終判断する」要件としてではなく、「長時間 foreground wait の観測性を確保する」要件として採用する。

採用すべき文言:

```text
wait_pr_stable_observation.sh は stdout に final JSON のみを出す。
長時間 foreground wait の観測性のため、bounded progress summary を stderr に出せる。
default は --progress stderr-summary とし、--progress none で抑止できる。
stderr progress は人間 / agent runtime 向けの non-authoritative signal であり、最終判断は stdout final JSON / result.json のみで行う。
poll delta は latest_delta.json と events.ndjson に machine-readable に保存する。
```

要件に追加すべき acceptance coverage:

- wait wrapper は progress mode を持つ。
- default は `--progress stderr-summary`。
- stdout は final JSON only を維持する。
- stderr progress は bounded で、poll ごとに最大1行。
- progress line には elapsed / remaining / next / status / stability / compact diff を含める。
- `latest_delta.json` を machine-readable に更新する。
- `events.ndjson` に durable events を残す。
- `pr-monitor` は progress を final decision に使わない。

## 8. `pr-monitor` best practice への反映

`pr-monitor` の振る舞いは次に固定する。

```text
1. wait_pr_stable_observation.sh を1回だけ実行する。
2. 実行中の stderr progress は待機中の状況説明として扱う。
3. progress line から success / failure / timeout を確定しない。
4. command exit 後、stdout final JSON を parse して final decision を作る。
5. 必要なら final JSON の artifact paths から events/latest/latest_delta/snapshots を参照する。
```

この境界により、progress は agent の安心材料・状況説明として機能しつつ、最終判断の authority は final JSON に保たれる。

## 9. リサーチ v2 結論

v1 の script-driven polling 方針は維持する。
そのうえで、長時間 foreground wait の UX と agent reliability のために progress delta を追加採用する。

最終的な推奨:

```text
stdout:
  final JSON only

stderr:
  defaultで bounded progress summary
  --progress none で抑止可能
  --progress stderr-jsonl は programmatic live consumer 用 option

artifacts:
  result.json
  events.ndjson
  latest.json
  latest_delta.json
  snapshots/

pr-monitor:
  progress は状況把握にだけ使う
  final decision は stdout final JSON のみ
```

この追加により、parse 契約の堅さを失わずに、長時間 wait 中の不安・停止誤認・進捗不明を軽減できる。
