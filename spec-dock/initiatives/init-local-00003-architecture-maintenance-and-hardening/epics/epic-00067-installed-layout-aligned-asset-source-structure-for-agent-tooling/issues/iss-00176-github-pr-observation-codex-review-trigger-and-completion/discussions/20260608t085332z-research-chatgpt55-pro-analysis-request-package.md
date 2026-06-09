# GPT-5.5 Pro 分析依頼パッケージ: Codex review trigger / completion observation

## 位置づけ

この artifact は、`iss-00176` で実施する予定の技術調査を ChatGPT GPT-5.5 Pro に依頼するための入力パッケージである。

現時点では、Codex 側から Chrome の ChatGPT Web を開こうとしたが、環境ポリシーにより `chatgpt.com` の利用がブロックされた。そのため、本資料は「GPT-5.5 Pro に渡すべき文脈と質問」を先に固定するために作成する。GPT-5.5 Pro からの回答そのものではない。

## 共有する公開リポジトリ

- GitHub repository: https://github.com/chemitaro/spec-dock
- active issue: `iss-00176`
- GitHub issue: https://github.com/chemitaro/spec-dock/issues/176

## 調査したい問題

`github-pr-observation` skill の PR observation script は、PR の CI / review / comments / review threads を観測し、最終的な JSON を stdout に返す。

しかし、現在の実装は主に read-only observation であり、Codex review を発生させる `@codex review` コメント投稿を script 自身が行わない。そのため、レビューが自動的に発生しないケースがある。

また、現在の wait logic は「CI 完了後に一定時間 quiet なら完了」といった安定窓に依存しており、Codex review が本当に完了したことを示すシグナルで停止しているわけではない。ユーザーはこれを不十分と判断している。

必要な最終状態は次である。

1. script が必要に応じて PR に `@codex review` コメントを投稿し、Codex review を開始させる。
2. 投稿した trigger comment を識別し、その trigger に紐づく Codex review の出力だけを収集する。
3. Codex review が進行中か完了済みかを、GitHub から取得できる技術的に実在するシグナルで判定する。
4. Codex review 完了時点で polling を終了する。
5. CI / review の最終結果、review body、inline review comments、thread state、失敗 CI details などは stdout final JSON に含める。
6. stderr progress は長時間待機中の liveness を示す補助情報として維持する。

## 現行実装の要点

実装の source of truth は provider-side asset である。

- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`

consumer-side mirror は `.agents/skills/github-pr-observation/` にあるが、通常は provider-side asset を先に修正する。

### 現行 skill contract

`github-pr-observation` skill は、現在 read-only PR observation skill として定義されている。

- public entrypoints:
  - `scripts/wait_pr_observation.sh`
  - `scripts/fetch_pr_observation_snapshot.sh`
- stdout:
  - exactly one machine-readable JSON text result
- stderr:
  - progress / diagnostics only
- `summary.md` は生成しない
- `--out` は optional debug / audit artifacts
- 現在の安全境界:
  - arbitrary GitHub endpoint / method / GraphQL / body / raw `gh` arguments を受け取らない
  - fixed API contract のみ

今回の issue では、この read-only 境界をどう扱うべきかも検討対象になる。完全 read-only のままでは `@codex review` を投稿できないため、少なくとも trigger command posting 用の固定 write API を許可する設計が必要になる可能性が高い。

### `wait_pr_observation.sh`

現在の wait script は次の options を受け取る。

- `--repo OWNER/REPO`
- `--pr NUMBER`
- `--head-sha SHA`
- `--timeout-seconds`
- `--poll-interval-seconds`
- `--quiet-seconds`
- `--same-fingerprint-count`
- `--zero-check-grace-polls`
- `--trigger-comment-id`
- `--trigger-created-at`
- `--body-mode none|trigger-window-truncated|trigger-window-full|out-only`
- `--progress stderr-summary|none`
- `--out DIR`

poll ごとに `fetch_pr_observation_snapshot.sh` を実行し、snapshot JSON を semantic fingerprint 化する。fingerprint が変化した場合は quiet window を reset する。

CI progress は `ci_progress_counts(payload)` で、success / skipped / neutral を ok、failed、running、pending、other、stale、total として数える。

Review progress は `review_progress_counts(payload)` で、trigger-window / current signal の Codex-authored review signal 件数、threads、unresolved、requested などを数える。

ただし、現在の完了判定は「Codex review の明確な完了シグナル」ではなく、snapshot の normalized status、quiet window、same fingerprint count、timeout などに依存する。

### `fetch_pr_observation_snapshot.sh`

現在の snapshot script は概ね次を行う。

1. `gh pr view "$pr" --repo "$repo" --json headRefOid,url,state,isDraft,number` で PR metadata を取得する。
2. head SHA が期待値と一致する場合、checks collector と review collector を呼ぶ。
3. review collector には `--trigger-comment-id` / `--trigger-created-at` / `--body-mode` / `--out` を渡せる。
4. 最後に再度 PR metadata を取得し、collection 中の head 変更などを検知する。

### `fetch_pr_review_snapshot.sh`

review collector は、すでに trigger-window scoped collection の基盤を持つ。

取得している主な GitHub API:

- `repos/{repo}/issues/{pr}/comments`
- `repos/{repo}/pulls/{pr}/reviews`
- `repos/{repo}/pulls/{pr}/comments`
- `repos/{repo}/pulls/{pr}`
- GraphQL review threads

trigger 判定:

- `--trigger-comment-id` があれば明示 trigger として扱う。
- `--trigger-created-at` があれば明示 trigger timestamp として扱う。
- 明示 trigger がなければ、issue comments から最新の `@codex review` コメントを inferred trigger として扱う。
- trigger が不明な場合は `trigger_unknown` limitation を返す。

body collection:

- `body-mode=trigger-window-full` なら trigger 以後の body を stdout JSON に含める。
- `trigger-window-truncated` なら bounded cap 付きで body を含める。
- `out-only` なら body は optional artifact に逃がす。
- `none` なら body は含めない。

status signals:

- issue comments
- pull reviews
- pull review comments
- review requests
- review decision
- review threads / resolved / outdated / unresolved

current status signal:

- trigger command 自体は除外する。
- stale commit の signal は除外する。
- explicit / inferred trigger がある場合は trigger 以後の signal のみ current とする。
- trigger がない場合は expected head SHA に紐づく pull review / pull review comment を fallback current とする。

現在は、Codex review の「開始中」「完了」を表す専用シグナルはまだ実装されていない。

## ユーザーが観測している実運用上の仮説

ユーザーは GitHub PR 上の Codex review 挙動について、次のようなシグナルがある可能性を示している。

- PR に `@codex review` コメントを投稿すると、Codex から何らかの応答コメントが投稿される。
- review 中は trigger comment あるいは関連 comment に目の emoji reaction が付く可能性がある。
- review が終わると、その emoji reaction が消える可能性がある。
- review output は、trigger comment に時間的または thread 的に紐づく形で発生する可能性がある。

ただし、これらが GitHub API で安定して取得できる正式シグナルなのか、UI 上の一時表現なのか、仕様として信頼できるのかは未確定である。GPT-5.5 Pro には、技術的に可能な取得方法と信頼性を分析してほしい。

## GPT-5.5 Pro への質問

以下の技術課題について、GitHub API / GitHub CLI / GraphQL / Codex review の実際の挙動を前提に、実装可能な候補を徹底的に列挙し、ベストプラクティス案を提案してください。

### 1. `@codex review` trigger comment の投稿

- `gh api` または `gh pr comment` のどちらを使うのがよいか。
- 投稿後に comment id / node id / created_at / author / URL を確実に取得する方法。
- duplicate trigger を避けるべきか、常に新規 trigger を投稿すべきか。
- head SHA と trigger comment をどう関連付けるべきか。
- script の安全境界として、固定文面 `@codex review` の投稿だけを許可する設計で十分か。
- dry-run / no-trigger / reuse-existing-trigger のような option は必要か。

### 2. Codex review 開始シグナル

- `@codex review` 投稿後、GitHub API から取得できる「review が開始した」シグナルは何か。
- issue comment reaction、Codex bot の response comment、review request、pending review、check run、status、timeline event など、候補ごとの取得 API と信頼性を比較してほしい。
- 目の emoji reaction が使える場合、どの API で取得できるか。
  - REST issue comment reactions
  - GraphQL reactions
  - timeline events
- reaction がない環境や UI-only の場合、fallback はどうするべきか。

### 3. Codex review 完了シグナル

- Codex review が完了したことを GitHub API から安定して判定する方法は何か。
- 「reaction が消えた」「Codex bot が final comment を出した」「PR review / review comments が増え終わった」「pending review が submitted になった」など候補を比較してほしい。
- 完了判定は単一 signal に依存すべきか、複数 signal の state machine にすべきか。
- どうしても正式完了シグナルがない場合、どのような bounded fallback を設計すべきか。
- 現行の「CI 完了後 quiet 90 秒」はなぜ不十分で、どう置き換えるべきか。

### 4. trigger に紐づく review output の収集

- trigger comment id / created_at 以後の comments / reviews / review comments を収集する現行方式は妥当か。
- 複数回 `@codex review` が投稿された PR で、今回の trigger に紐づく出力だけを切り分ける方法。
- timestamp window だけで十分か。
- Codex bot response comment との relation / reply / thread / timeline を使えるか。
- review comments の本文を stdout final JSON に含める場合の cap / truncation / full mode の方針。
- API rate limit と large PR の pagination をどう扱うべきか。

### 5. polling state machine

望ましい state machine を提案してほしい。

候補 state:

- `trigger_posting`
- `trigger_posted`
- `waiting_review_start`
- `review_running`
- `review_completed`
- `ci_running`
- `ci_completed`
- `finalizing`
- `timeout`
- `human_gate`

CI と review を並列に観測する場合、どのような終了条件にするべきか。

期待する最終終了条件の例:

- expected head SHA が変わっていない。
- CI が terminal に到達している。
- Codex review trigger が既知である。
- Codex review が完了シグナルを出している。
- trigger 以後の Codex-authored review output を最終 snapshot として収集済み。

### 6. stdout / stderr contract

現在の方針は次の通り。

- stdout: final authoritative JSON only
- stderr: polling progress only

この方針を維持したまま、trigger posting と review completion tracking を追加するには、JSON schema にどのような fields を追加すべきか。

例:

- `trigger.action`
- `trigger.comment_id`
- `trigger.created_at`
- `trigger.reused`
- `trigger.posted_by`
- `codex_review.lifecycle.status`
- `codex_review.lifecycle.start_signal`
- `codex_review.lifecycle.completion_signal`
- `codex_review.lifecycle.last_activity_at`
- `codex_review.lifecycle.limitations`
- `review.output_scope`
- `review.trigger_window`

stderr progress はどのような key/value line がよいか。

### 7. testing strategy

この機能を hermetic tests でどう検証するべきか。

- `gh` stub の設計
- REST API response fixtures
- GraphQL response fixtures
- reaction present / reaction absent
- start signal delayed
- completion signal delayed
- multiple triggers
- stale head
- CI completes before review
- review completes before CI
- no Codex response
- timeout
- permission failure

## GPT-5.5 Pro に期待するアウトプット

次の形式で回答してください。

1. 技術的に取得可能な signal 一覧
   - source
   - API
   - schema field
   - reliability
   - limitations
2. 推奨 state machine
3. 推奨 GitHub API / CLI calls
4. trigger posting の安全境界
5. review output collection の scope 定義
6. completion condition の best practice
7. fallback / timeout policy
8. stdout JSON schema 追加案
9. stderr progress 追加案
10. 実装ステップ案
11. テストケース案

回答は、抽象論ではなく、`spec-dock` の現行実装に対してどのファイル / どの責務をどう変えるべきかが分かる具体性でお願いします。

## 現時点の Codex 側メモ

Codex 側の暫定見立てでは、最小の自然な拡張は次の方向である。

- `wait_pr_observation.sh` を read-only wait から `trigger + wait` orchestration に拡張するか、write boundary を分けた `trigger_codex_review.sh` を追加して wait から固定呼び出しする。
- trigger posting は arbitrary `gh` を許さず、固定 REST endpoint に固定 body を送る。
- trigger comment id / created_at を得たら、既存の `--trigger-comment-id` / `--trigger-created-at` を使って collection window を固定する。
- review lifecycle は、reaction / bot response / review activity / quiet fallback の複合 state machine にする必要がある可能性が高い。
- 「CI 完了後 quiet 90 秒」は review completion の主判定から外し、completion signal が取れない場合の bounded fallback に下げるべきである。
- 最終 JSON には、completion が reliable signal で確定したのか、fallback timeout / quiet で推定したのかを明示する。

この暫定見立ての妥当性も、GPT-5.5 Pro に批判的に検討してもらいたい。
