---
kind: research
scope_id: iss-00174
created_at: 2026-06-08T07:31:19Z
source_pr: https://github.com/chemitaro/spec-dock/pull/175
reviewed_commit: 6490dfd0b1bb2c6d89c8a14539fbcf1656f18621
reviewer: chatgpt-codex-connector
---

# Codex review 指摘の個別分析

## 前提

PR #175 に対して、ユーザーが `@codex review` を投稿した結果、Codex review が inline comment 3件を返した。

対象はいずれも `wait_pr_observation.sh` の review progress projection と wait fingerprint の整合に関する P2 指摘である。

今回の issue の重要な意図は次の通り。

- review progress line の `comments=N` は、今回の観測窓で捕捉した current Codex review signal の進捗を表す。
- body 出力 mode は stdout JSON に本文を含めるかどうかの制御であり、progress count そのものを消してはならない。
- quiet reset は progress 表示の意味論と揃える。progress に出ない古い/非current/noise signal で不安定化してはならない。
- final stdout JSON が権威であり、stderr progress は bounded summary に留める。

## R-001: Exclude filtered review noise from the wait fingerprint

- GitHub comment: https://github.com/chemitaro/spec-dock/pull/175#discussion_r3371426079
- 対象: `semantic_fingerprint()` の `review.fingerprint`
- 指摘要旨:
  - `signals` は `review_progress_signal_items(payload)` に置き換えられている。
  - しかし直前で `payload.review.fingerprint` を fingerprint source に含めている。
  - collector 側の `review.fingerprint` は全 review signals、`omitted_reason`、non-Codex、stale なども含む。
  - そのため `comments=N` が変化しない noise でも wait fingerprint が変わり、quiet が reset される。

### 妥当性

妥当。

`fetch_pr_review_snapshot.sh` の `fingerprint_source` は `signals: [fingerprint_signal(item) for item in signals]` と `codex_authored` を含み、status 判定から除外される signal も fingerprint に含めている。`wait_pr_observation.sh` の `semantic_fingerprint()` がこの collector fingerprint をそのまま含めると、wait loop の安定判定は progress projection より広い signal 集合へ反応する。

これは issue の設計意図である「progress 表示と quiet reset は同じ projection を共有する」に反する。

### 修正要否

修正必要。

### 修正設計

- `semantic_fingerprint()` から raw `review.fingerprint` を除外する。
- wait fingerprint は `review.status`、`review_progress_signal_items(payload)`、`review_requests`、`threads`、`body_mode`、`review_progress_counts(payload)` など、wait loop が本当に反応すべき要素から構成する。
- raw body / omitted noise / non-current signal 由来の collector fingerprint には依存しない。

### 検証計画

- review collector fingerprint だけが変化し、progress count が変わらない2 pollで `quiet` が reset されない test を追加する。

## R-002: Count current signals when bodies are omitted by mode

- GitHub comment: https://github.com/chemitaro/spec-dock/pull/175#discussion_r3371426094
- 対象: `review_progress_signal_items()` の `and not item.get("omitted_reason")`
- 指摘要旨:
  - `--body-mode none` / `out-only` では collector が全 signal に `omitted_reason=body_mode_none` / `body_mode_out_only` を付ける。
  - 現在の predicate は `omitted_reason` がある signal をすべて除外する。
  - その結果、current Codex review feedback が来ていても `comments=N` が 0 のままになる。

### 妥当性

妥当。実際に PR #175 の observation でも `--body-mode none` で Codex authored issue comment が存在したが、progress line は `comments=0` のままだった。

`body_mode_none` / `body_mode_out_only` は「本文を stdout に含めない」という出力境界の理由であり、「current signal ではない」という意味ではない。progress count が body 出力 mode に依存すると、プライバシー/本文出力抑制 mode でレビュー進捗が見えなくなる。

### 修正要否

修正必要。

### 修正設計

- `review_progress_signal_items()` の `omitted_reason` 判定を allowlist 化する。
- 除外すべき `omitted_reason`:
  - `outside_trigger_window`
  - `trigger_unknown`
  - `timestamp-unavailable`
- count 対象として許可すべき `omitted_reason`:
  - `None`
  - `body_mode_none`
  - `body_mode_out_only`
  - `item_count_cap`
  - `total_body_char_cap`
- body cap 系は body 本文の収録制限であり、signal 自体は current であるため count 対象にする。

### 検証計画

- `body_mode_none` / `body_mode_out_only` 付き current Codex signal が `comments=N` に加算される test を追加する。
- `outside_trigger_window` / `trigger_unknown` / `timestamp-unavailable` は引き続き除外されることを既存 test と追加 assert で確認する。

## R-003: Ignore stale review signals in progress counts

- GitHub comment: https://github.com/chemitaro/spec-dock/pull/175#discussion_r3371426097
- 対象: `review_progress_signal_items()` の stale 判定不足
- 指摘要旨:
  - collector の S04 status logic は `stale` signal を current review state から除外している。
  - しかし progress projection は Codex-authored かつ omitted なしなら stale signal も count する。
  - その結果、final review status は non-current と扱う feedback で `comments=N` と quiet reset が進む。

### 妥当性

妥当。

`fetch_pr_review_snapshot.sh` の `is_current_status_signal()` は `item.get("stale")` を明示的に除外する。progress count は current head の進捗を示すべきなので、stale feedback を `comments=N` に含めると status semantics とずれる。

### 修正要否

修正必要。

### 修正設計

- `review_progress_signal_items()` に `item.get("stale") is not True` を追加する。
- R-001 と合わせて wait fingerprint も stale signal に反応しないようにする。

### 検証計画

- stale Codex-authored review/comment がある poll でも `comments=N` が増えず、quiet が reset されない test を追加する。

## 統合修正方針

3件とも修正必要と判断する。修正は次の最小差分にまとめる。

1. `review_progress_signal_items()` を current progress signal predicate として明確化する。
2. body omission mode / body cap 由来の omission は count 対象に残す。
3. trigger/window/timestamp 不明と stale / non-Codex / trigger command は除外する。
4. wait `semantic_fingerprint()` から raw `review.fingerprint` を除外し、progress projection と同じ filtered signals で安定判定する。
5. provider script を修正後、dogfooding mirror script を exact match に同期する。
6. focused regression を追加し、`bash -n`、provider/mirror `diff -u`、`git diff --check`、focused pytest を実行する。

## 修正後の期待結果

- `--body-mode none` / `out-only` でも current Codex feedback の件数が `comments=N` に反映される。
- `outside_trigger_window` / `trigger_unknown` / `timestamp-unavailable` / stale / non-Codex / trigger command は `comments=N` と quiet reset に影響しない。
- review collector の raw fingerprint が noise で変わっても、wait loop の quiet は progress projection に関係する変化にだけ reset される。

## 追加レビュー R-004: Preserve trigger-window filtering when bodies are suppressed

- GitHub comment: https://github.com/chemitaro/spec-dock/pull/175#discussion_r3371528181
- 対象: `review_progress_signal_items()` の `body_mode_none` / `body_mode_out_only` allowlist
- Reviewed commit: `8e38b41043303362795d60425d998a194f29ed9f`
- 指摘要旨:
  - `fetch_pr_review_snapshot.sh` の `add_body_metadata()` は、`body_mode_none` / `body_mode_out_only` の場合、trigger-window 判定より前に `omitted_reason` を付けて return する。
  - そのため wait 側が `body_mode_none` / `body_mode_out_only` を単純に current signal として許可すると、今回の `@codex review` trigger より前の古い Codex-authored signal も `comments=N` に混入し得る。
  - これは「今回の観測窓で捕捉した Codex review signal 件数」という D-002 の定義に反する。

### 妥当性

妥当。

前回 R-002 の修正方針で「body 出力 mode は progress count を消してはならない」と判断したこと自体は正しい。一方で、collector の実装順序を見ると、`body_mode_none` / `body_mode_out_only` は current 性を示す omission reason ではない。

`add_body_metadata()` はまず `include_candidate = body_state["trigger_known"] and is_after_trigger(signal)` を計算するが、`body_mode == "none"` / `"out-only"` の branch では `include_candidate` を使わずに return する。したがって、wait 側で `omitted_reason` だけを見て current と推定するのは不十分である。

本来の current 判定は collector 側の `is_current_status_signal()` に集約されており、ここでは `trigger_command`、`stale`、explicit/inferred trigger 以後、または trigger 不在時の expected head review signal という条件が表現されている。progress count と quiet reset もこの判定に揃えるべきである。

### 修正要否

修正必要。

このままでは `--body-mode none` / `out-only` で古い Codex review comment が `comments=N` に混入し、今回の issue で確定した「0 -> 1 -> 2 の current review progress」を表せない。

### 修正設計

- collector 側で `is_current_status_signal(item)` の結果を `current_status_signal` として各 signal に付与する。
- `fingerprint_signal()` と wait 側の `sanitized_review_signals()` safe keys に `current_status_signal` を追加する。
- `review_progress_signal_items()` は `current_status_signal is True` を優先して current 判定する。
- `body_mode_none` / `body_mode_out_only` / body cap 系の omission は、`current_status_signal is True` の signal に限って count 対象にする。
- 古い snapshot / fake snapshot との互換のため、`current_status_signal` が存在しない場合だけ従来の `stale` / `outside_trigger_window` / `trigger_unknown` / `timestamp-unavailable` 除外に fallback する。

### 検証計画

- `current_status_signal=False` かつ `body_mode_none` / `body_mode_out_only` の signal が `comments=N` に加算されない test を追加する。
- `current_status_signal=True` の body-mode omitted signal は引き続き count されることを既存 R-002 test で確認する。
- `semantic_fingerprint()` は `review_progress_signal_items()` を使い続けるため、non-current body-mode omitted signal では quiet reset されないことを events fixture で確認する。

## 追加レビュー R-005: Preserve non-Codex review changes in wait fingerprint

- GitHub comment: https://github.com/chemitaro/spec-dock/pull/175#discussion_r3371654171
- 対象: `semantic_fingerprint()` の review signal projection
- Reviewed commit: `31595d48a66b2956289758193c8d0255986581bf`
- 指摘要旨:
  - R-001/R-004 対応後、`semantic_fingerprint()` が `review_progress_signal_items(payload)` を使っている。
  - `review_progress_signal_items()` は `comments=N` 用なので `codex_authored is True` に絞っている。
  - その結果、人間 reviewer など non-Codex の current review signal が変化しても wait fingerprint が変わらず、quiet / stability が reset されない。
  - 既存の `test_issue_170_pr_observation_wait_resets_stability_on_review_semantic_change` は同じ review status の body change を semantic change として扱う。

### 妥当性

妥当。

`comments=N` の定義は D-002 により「今回の観測窓で捕捉した Codex review comments / review signals 件数」である。一方で、wait loop の semantic fingerprint は `comments=N` と完全に同じ集計値ではなく、PR 観測としての安定判定に必要な current semantic state を表す必要がある。

R-001 の目的は raw collector `review.fingerprint` に含まれる non-current / outside-window / stale / trigger_unknown noise を quiet reset から外すことであり、current な non-Codex review feedback の変化まで無視することではない。

R-004 で追加した `current_status_signal` により、collector 側の current 判定を wait 側でも利用できる。したがって、progress count と semantic fingerprint を分離し、semantic fingerprint には current review semantic signals 全体を含めるのが適切である。

### 修正要否

修正必要。

このままでは、人間レビューコメントの body change や same-status review feedback の更新があっても、wait が古い fingerprint のまま stable と判断し得る。これは PR observation の安全側挙動として不十分である。

### 修正設計

- `review_progress_signal_items()` は現状どおり `codex_authored is True` を維持し、`comments=N` の意味を変えない。
- 新たに `review_semantic_signal_items()` を追加し、`trigger_command` ではなく、`review_progress_signal_is_current(item)` が true の review / review comment / issue comment を、Codex authored かどうかに関係なく返す。
- `semantic_fingerprint()` の `review.signals` は `review_semantic_signal_items(payload)` を使う。
- raw collector `review.fingerprint` には戻さない。current 判定済み signal projection を使うことで、R-001 の noise 除外と R-005 の semantic change 追跡を両立する。

### 検証計画

- non-Codex かつ `current_status_signal=True` の review signal の `body_sha256` が変わると `latest_change_poll` が進み、events が `[True, True, False]` になる test を追加する。
- `comments=N` は non-Codex signal では増えず `comments=0` のままであることを確認する。
- 既存 `test_issue_170_pr_observation_wait_resets_stability_on_review_semantic_change` も含めて focused pytest を実行する。
