# PR observation progress line の二段階表示に関する分析

## 目的

本資料は、`wait_pr_observation.sh` のポーリング中 stderr progress 表示が、ユーザーの意図した「進行中は詳細、完了後は圧縮」という二段階表示になっていない問題を分析し、次に修正すべき契約を整理するための research / discussion artifact である。

対象は `iss-00170-harden-pr-monitor-stable-observation` の実施中に観測された PR observation loop の追加改善であり、`iss-00174-refine-pr-observation-two-stage-progress-output` の後続作業へ引き継ぐため、現状分析・目標状態・推奨修正・テスト観点を記録する。

## 背景

この issue では、PR monitoring を model-side polling ではなく deterministic script-driven polling に寄せた。長時間実行中に AI agent / human が不安定な待機状態にならないよう、poll ごとに stderr へ最大1行の progress を出し、stdout final JSON を唯一の authoritative result とする方針を採用している。

既存 design には、progress line の例として次のような richer current-state summary が記録されている。

```text
pr_obs poll=4 elapsed=06m00s remain=24m00s phase=waiting_checks ci=running checks=7/9 ok=6 fail=0 pend=2 other=1 review=requested quiet=00m30s limit=none
```

一方、現在の実装は `wait_pr_observation.sh` の `progress_line()` が次の情報だけを出す。

```text
poll=12 elapsed=396 remain=1403 phase=wait ci=passed review=unresolved quiet=0/60 limit=ok final=stdout_json
```

このため、CI / review が動いている間の「何がどれだけ進んでいるか」が見えず、quiet reset の理由も stderr progress からは読み取れない。

## 現状分析

### 実装の現状

`wait_pr_observation.sh` は poll ごとに snapshot JSON を取得し、`semantic_fingerprint(payload)` が変わった場合に `latest_change_monotonic` を更新する。つまり、内部的には payload の semantic change を quiet reset の根拠にしている。

ただし現行の wait wrapper 側 fingerprint は、CI については主に status / failures を見ており、`ci=running` のまま `checks=1/4 -> 2/4 -> 3/4` と進むような count 変化を quiet reset 対象にできていない可能性が高い。review については `review.fingerprint`、signals、summary、threads を見ているため CI より近いが、stderr に件数が出ないため進行が読めない。

ただし、stderr progress line は以下の粗い fields のみである。

- `poll`
- `elapsed`
- `remain`
- `phase`
- `ci`
- `review`
- `quiet`
- `limit`
- `final=stdout_json`

CI の `check_runs.success/running/pending/failed/total`、review の `summary` / `threads` / `signals` の件数、直近で semantic fingerprint が変化した理由は表示されない。

### ユーザー意図とのズレ

ユーザー意図は、完了後に情報を圧縮すること自体ではなく、状態に応じて粒度を変えることだった。

- CI 実行中:
  - 全体の job / check 数に対して完了数が何件かを `done/total` で見たい。
  - 成功・失敗・pending/running の内訳も短く見たい。
  - 何か進んだら quiet がリセットされたことが見えるべき。
- CI 完了後:
  - 大量の details は不要。
  - `ci=passed` または `ci=failed` の単一 status に圧縮してよい。
- Review 観測中:
  - trigger window / current observation で捕捉された review comment 件数が `0 -> 1 -> 2 -> 3` のように増えることを見たい。
  - review comment / thread activity が増えたら quiet がリセットされるべき。
- Review 完了または安定後:
  - `review=none` / `review=unresolved` / `review=changes_requested` などの単一 status に圧縮してよい。

現行実装は、初期から `ci=running` や `review=unresolved` の単一 status だけを出すため、「進行中だけ詳細」という段階が欠けている。

### quiet 表示の問題

quiet counter は内部的には semantic fingerprint change でリセットされる。だが progress line が `quiet=35/60` のような値しか出さないため、ユーザーには次が分からない。

- CI job が進んだから reset されたのか。
- review comment が増えたから reset されたのか。
- head / metadata / limitation / thread state が変わったから reset されたのか。
- snapshot collection のタイミング差でリセットされたのか。

したがって、quiet の機能は存在していても、progress 表示としては「なぜ待っているのか」「どれだけ進んだのか」を伝えきれていない。さらに CI については、表示不足だけでなく quiet reset の意味論自体も count-based progress に追従していない可能性がある。

## 目標状態

### 基本方針

progress line は stdout final JSON の代替ではない。詳細本文、個別 URL、review body、P1/P2 text interpretation は出さない。一方で、長時間待機中の liveness と進捗理解に必要な counts は stderr の1行に出す。

目標は、1 poll 最大1行を維持しつつ、CI / review それぞれについて次の二段階表示を行うことである。

1. 進行中は count-based detail を出す。
2. 完了後または stable human gate 後は compact status へ圧縮する。

### CI の二段階表示

CI が `running` / `pending` / `none` / required check wait 中の場合は、次のような counters を出す。

```text
ci=running checks=2/4 ok=2 run=2 pend=0 fail=0 other=0
```

ここで `checks=done/total` は「terminal check run/status 数 / 全 check run/status 数」を意味する。`done` は success / skipped / neutral / failed / cancelled / timed_out / action_required など、GitHub 上で terminal と見なせるものを含む。

CI が完了したら compact にする。

```text
ci=passed
```

または:

```text
ci=failed fail=1
```

失敗時だけ `fail=1` など最小 count を残すのは有用だが、workflow name / job name / URL / failed step は final JSON の `ci.failures[]` に委ねる。

### Review の二段階表示

Review がまだ安定していない、または trigger-window feedback が増え得る状態では、count-based detail を出す。

```text
review=observing comments=2 threads=1 unresolved=1 reviews=1 requested=0
```

または、より短く:

```text
review=observing comments=2 threads=1 unresolved=1
```

最重要なのは `comments=N` である。ユーザーの意図では、review comment が 0, 1, 2, 3 と増える様子が progress に見える必要がある。

Review が stable に到達した後は compact にする。

```text
review=none
```

または:

```text
review=unresolved comments=15
```

unresolved の場合は human gate の理由として count があると有用であるため、完了後も `comments` / `unresolved` の最小 count を残す案が妥当である。ただし本文や reviewer 名は出さない。

### quiet reset と表示の整合

quiet reset の根拠は、現在の `semantic_fingerprint(payload)` を維持しつつ、progress line 上にも「reset の理由に対応する observable counters」を出すべきである。

望ましい reset signal は次の通り。

- CI:
  - total checks が増えた。
  - terminal count が増えた。
  - running / pending / failed / success count が変わった。
  - required-check rollup state が変わった。
  - merge state が CI 判定に影響する形で変わった。
- Review:
  - trigger-window / current signal count が増えた。
  - review comment count が増えた。
  - unresolved thread count が変わった。
  - reviewDecision / requested reviewers / review state が変わった。
  - thread activity timestamp / latest comment timestamp が変わった。
- Common:
  - expected head SHA との一致状態が変わった。
  - limitation が増減した。
  - normalized status / recommended next action が変わった。

progress line は、これらすべての delta を event log として出す必要はない。しかし、少なくとも count が動いたことが見える fields を出すべきである。

## 推奨 progress line contract

### 例: CI running / review 未着手

```text
pr_obs poll=4 elapsed=02m00s remain=28m00s phase=wait ci=running checks=2/4 ok=2 run=2 pend=0 fail=0 review=observing comments=0 threads=0 quiet=00m30s stable=1/2 final=stdout_json
```

### 例: CI running / review comments 増加中

```text
pr_obs poll=8 elapsed=04m00s remain=26m00s phase=wait ci=running checks=3/4 ok=3 run=1 pend=0 fail=0 review=observing comments=2 threads=2 unresolved=2 quiet=00m00s stable=1/2 final=stdout_json
```

### 例: CI passed / review なし

```text
pr_obs poll=12 elapsed=08m00s remain=22m00s phase=terminal ci=passed review=none quiet=01m10s stable=3/2 final=stdout_json
```

### 例: CI passed / unresolved review gate

```text
pr_obs poll=14 elapsed=09m00s remain=21m00s phase=terminal ci=passed review=unresolved comments=15 threads=15 quiet=01m10s stable=3/2 final=stdout_json
```

### 表示ルール

- prefix は `pr_obs` を付けると他 stderr と区別しやすい。
- elapsed / remain / quiet は秒数でもよいが、`MMmSSs` 形式の方が人間には読みやすい。
- `stable=current/required` を出すと、quiet だけでなく same fingerprint gate の進捗も分かる。
- 1行上限は維持する。目安は 200-240 chars。
- 文字数超過時は optional fields を削り、`limit=truncated` を出す。
- review body / individual URL / reviewer name / workflow name / job name / P1/P2 は出さない。
- stdout final JSON が唯一の authoritative result であることを `final=stdout_json` で維持する。

## 推奨修正

### 1. progress summary 用の projection を追加する

`progress_line()` が raw payload を直接読むのではなく、`progress_projection(payload)` のような小さな projection を作る。

候補 fields:

- `ci_status`
- `ci_done`
- `ci_total`
- `ci_success`
- `ci_running`
- `ci_pending`
- `ci_failed`
- `ci_other`
- `review_status`
- `review_comments`
- `review_threads`
- `review_unresolved_threads`
- `review_requests`
- `review_reviews`
- `limitations_count`
- `same_count`
- `same_required`

この projection は stderr 表示だけでなく、テストしやすい pure function として扱う。`progress_line()` に直接複雑な分岐を詰め込むより、`progress_state(payload, phase, quiet, stable)` のような内部表現を作り、そこから bounded key/value line を render する方がよい。

### 2. CI の compact / detailed 切り替えを明示する

`ci.status in {"running", "pending", "none", "unknown"}` または required check wait 中は detailed 表示にする。

`ci.status in {"passed", "failed"}` で terminal と判断できる場合は compact 表示にする。ただし failed の場合は `fail=N` を残してもよい。

### 3. Review の compact / detailed 切り替えを明示する

review は CI より難しい。GitHub / Codex review の完了は厳密には「レビューがもう来ない」ことを API で確定できないため、wait loop の安定条件と status で表示を切り替えるのがよい。

推奨:

- `observation_complete=false` の間は `review=observing` または current `review.status` + counters を表示する。
- `observation_complete=true` になったら current `review.status` を compact 表示する。
- `review.status in {"unresolved", "changes_requested", "commented"}` の場合は、human gate 理由として `comments=N` / `threads=N` / `unresolved=N` の最小 count を残す。

### 4. quiet reset の根拠を semantic fingerprint と progress counters の両方で説明可能にする

内部 reset は引き続き semantic fingerprint でよい。ただし projection に出ない field だけで fingerprint が変わると、quiet がリセットされた理由が progress line から分からなくなる。

そのため、semantic fingerprint に含める主要カテゴリは progress projection にも count / status として反映するのが望ましい。

例:

- review body hash だけが変わる場合、body text は出さないが `comments=N` と `review=commented/unresolved` は維持し、必要なら `body_meta=changed` のような boolean を検討する。
- limitation が変わる場合、`limits=N` を出す。
- head mismatch が起きた場合、`head=stale` を出す。

CI については、現行の wait wrapper fingerprint に `payload["fingerprint"]` または CI collector fingerprint 相当を含める、もしくは `check_runs` count / required-check state count を wait wrapper fingerprint に明示的に追加する必要がある。新しい GitHub API call を増やす必要はなく、既存 snapshot JSON から投影すればよい。

### 5. stdout final JSON contract は維持する

progress line はあくまで liveness / progress summary であり、final decision authority にしない。詳細な review 本文、CI failure detail、thread item は final JSON に残す。

## Deep-consultant 分析の要約

deep-consultant は、問題の本質を「GitHub 取得処理不足」ではなく「既存 snapshot JSON の progress projection 不足」と整理した。

- 現行 `stderr` progress は liveness を示す粗い status 表示であり、CI / review の進捗が増えていることを読める表示ではない。
- CI collector は `ci.check_runs` / `ci.commit_statuses` の count を既に持っているため、新しい GitHub API call を増やさずに `checks=done/total ok=n fail=n pend=n other=n` を出せる。
- wait wrapper の `semantic_fingerprint()` は CI 側を `status` / `failures` 中心で見ており、`running` のまま count が進む変化を quiet reset 対象にできていない可能性が高い。
- review collector は `review.summary` / `signals` / `threads` / `fingerprint` を持つため、review semantic change の quiet reset は CI より近い状態にある。ただし stderr に件数が出ないため、進行が読めない。
- `limit=ok` は design の `limit=none` とズレているため、通常は `limit=none`、optional fields を落とした場合だけ `limit=truncated` にするのがよい。
- `events.ndjson` に compact progress state を残すと監査性が上がる。ただし stdout final JSON の authority は変えない。

## テスト観点

### Progress line unit / fixture tests

- CI running:
  - total 4、success 2、running 2 の payload から `checks=2/4 ok=2 run=2` が出る。
  - fake snapshot で `checks=0/3 -> 1/3 -> 2/3 -> ci=passed` を返し、stderr の count 増加と quiet reset / `latest_change_poll` 更新を確認する。
- CI passed:
  - success 4 / total 4 の payload から detailed counters が省略され、`ci=passed` になる。
- CI failed:
  - failed 1 を含む payload から `ci=failed fail=1` が出る。
- Review observing:
  - comments 0 -> 2 に増えた payload で `comments=0` / `comments=2` が出る。
- Review unresolved terminal:
  - `review.status=unresolved` の payload で `review=unresolved comments=N threads=M unresolved=K` が出る。
- Truncation:
  - optional fields が多い場合でも 240 chars 程度に収まり、必要なら `limit=truncated` が出る。

### Quiet reset tests

- CI check count が増えた場合、semantic fingerprint が変わり `quiet` が reset される。
- CI terminal count が増えた場合、semantic fingerprint が変わり `quiet` が reset される。
- Review comment count が増えた場合、semantic fingerprint が変わり `quiet` が reset される。
- Review thread unresolved count が変わった場合、semantic fingerprint が変わり `quiet` が reset される。
- No-change poll では `quiet` が増加し、same count も増える。
- slow snapshot collection time が quiet に混入しない既存 regression を維持する。

### stdout / stderr separation tests

- stderr progress は最大1行 / poll。
- stdout は final JSON だけ。
- `--progress none` では progress line が出ない。
- progress line は review body / URL / reviewer name / workflow name / job name を含まない。

## リスク

- counters を増やしすぎると1行 progress が読みにくくなる。
- review の「完了」を API で確定しようとすると過剰設計になる。wait loop の stable / observation_complete と組み合わせて表示粒度を切り替えるのが現実的。
- progress projection と semantic fingerprint が乖離すると、quiet reset の理由がまた見えなくなる。
- CI の done/total を check runs と commit statuses と required-check rollup のどこまで含めるかは定義が必要。まずは `ci.check_runs.total` と check-run counts を中心にし、commit statuses / required-check rollup は status 判定と limitations に使うのがシンプル。

## 確定事項

- `comments=N` は、`@codex review` trigger 以後に今回の観測窓で新しく捕捉した Codex review comments / review signals の件数として定義する。
  - 古い PR 全体コメントや過去の unresolved thread は毎回の progress count へ積み上げない。
  - 目的は「今回のレビューが 0 -> 1 -> 2 と進んでいる」ことを stderr progress から読めるようにすることである。
  - この定義は interview `20260608t025500z-interview-progress-review-comment-count.md` でユーザー回答により確定した。

## 残る低リスク未確定事項

- Review compact 表示へ切り替えるタイミングを `observation_complete=true` のみにするか、`review.status=none|approved` のような terminal-like status でも先に compact にするか。
  - 推奨は `observation_complete=true` を基準にすること。
- `checks=done/total` に commit statuses を含めるか。
  - 推奨はまず check runs の `done/total` とし、commit statuses は `status_ctx=done/total` を別 field にする必要が出た場合だけ拡張すること。

## 結論

現行の `wait_pr_observation.sh` は、stdout final JSON と stderr progress の分離、および semantic fingerprint による quiet reset という基盤は持っている。しかし stderr progress が coarse status のみで、設計例とユーザー意図にある「進行中の count-based detail」を実装していない。

次の修正では、progress line を二段階表示にするべきである。CI / review が進行中なら count-based detail を出し、完了後は compact status に畳む。quiet reset は semantic fingerprint のままでよいが、reset の理由が progress counters から推測できるよう、projection と fingerprint の対象カテゴリを揃える必要がある。
