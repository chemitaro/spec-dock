# Design Proposal: PR observation progress line の二段階表示

## 位置づけ

本資料は、`wait_pr_observation.sh` の stderr progress 表示を「進行中は詳細、完了後は圧縮」の二段階表示へ修正するための設計案である。Canonical `design.md` へ昇格する前の discussion artifact として扱う。

入力資料:

- `20260608t024500z-research-progress-line-two-stage-status-analysis.md`
- `20260608t025500z-interview-progress-review-comment-count.md`
- `requirement.md` の Progress 表示要件
- `design.md` の Progress line contract
- 現行 `wait_pr_observation.sh`

## 設計目標

- stderr progress は 1 poll 最大1行の bounded key/value current-state summary とする。
- stdout final JSON は唯一の authoritative result として維持する。
- CI / review が進行中の間だけ count-based detail を出す。
- CI / review が完了または observation stable になった後は compact status へ畳む。
- quiet reset と progress line の visible counters を揃え、quiet がリセットされた理由を推測できるようにする。
- 新しい GitHub API call は増やさず、既存 snapshot JSON から projection する。

## 非目標

- review body、URL、reviewer name、workflow name、job name、P1/P2 text interpretation を progress に出さない。
- stdout JSON の schema authority を progress 表示へ移さない。
- GitHub review の「今後もうコメントが来ない」ことを API 的に確定しようとしない。
- progress のためだけに arbitrary GitHub query / jq / raw gh args を追加しない。

## 現行からの変更点

現行:

```text
poll=12 elapsed=396 remain=1403 phase=wait ci=passed review=unresolved quiet=0/60 limit=ok final=stdout_json
```

変更後の代表例:

```text
pr_obs poll=4 elapsed=120s remain=1680s phase=wait ci=running checks=2/4 ok=2 run=2 pend=0 fail=0 review=observing comments=0 threads=0 quiet=30/90 stable=1/2 limit=none final=stdout_json
```

CI 完了後:

```text
pr_obs poll=12 elapsed=480s remain=1320s phase=terminal ci=passed review=none quiet=70/90 stable=3/2 limit=none final=stdout_json
```

Review human gate:

```text
pr_obs poll=14 elapsed=540s remain=1260s phase=terminal ci=passed review=unresolved comments=3 threads=2 unresolved=2 quiet=70/90 stable=3/2 limit=none final=stdout_json
```

## Core Design

### 1. `progress_state(payload, ...)` projection を追加する

`progress_line()` に raw payload parsing を直接詰め込まず、まず progress 専用の内部 projection を作る。

候補:

```python
{
    "ci_status": "running|pending|passed|failed|none|unknown",
    "ci_done": 2,
    "ci_total": 4,
    "ci_success": 2,
    "ci_running": 2,
    "ci_pending": 0,
    "ci_failed": 0,
    "ci_other": 0,
    "review_status": "observing|none|approved|commented|changes_requested|unresolved|requested|unknown",
    "review_comments": 0,
    "review_threads": 0,
    "review_unresolved": 0,
    "limits": 0,
    "same_count": 1,
    "same_required": 2,
    "limit": "none|truncated",
}
```

この projection は stderr rendering と tests の共通入力にする。

### 2. CI counters

CI progress の主 denominator は `ci.check_runs.total` とする。

- `checks=done/total`
- `done = success + failed + skipped + neutral + other terminal`
- `ok = success + skipped + neutral`
- `run = running`
- `pend = pending`
- `fail = failed`
- `other = other`

commit statuses / required-check rollup は CI status 判定と limitations のために使い、初期実装では `checks=done/total` に混ぜない。必要が出たら `status_ctx=done/total` を別 field として拡張する。

CI status が `running|pending|none|unknown` の間は counters を表示する。`passed` では counters を省略する。`failed` では `fail=N` だけ残してよい。

### 3. Review counters

`comments=N` はユーザー回答により次で確定済み。

> `@codex review` trigger 以後に今回の観測窓で新しく捕捉した Codex review comments / review signals の件数。

古い PR 全体コメントや過去の unresolved thread は progress count に積み上げない。

実装上は既存 `review.signals` / `review.codex_authored` / `trigger` / `body_mode` から progress 用 projection を作る。body text は参照しても表示しない。

推奨 count:

- `comments`: trigger-window current Codex review comment / review signal count
- `threads`: current trigger-window thread count、または current unresolved thread count
- `unresolved`: current trigger-window unresolved thread count

Review が `observation_complete=false` の間は `review=observing` または current `review.status` + counters を表示する。`observation_complete=true` 後は compact status に畳む。ただし `unresolved|changes_requested|commented` は human gate 理由として `comments` / `threads` / `unresolved` の最小 count を残してよい。

### 4. quiet reset semantics

quiet reset は semantic fingerprint で行う現行方針を維持する。ただし CI count progress を fingerprint へ入れる。

追加すべき fingerprint source:

- CI check total
- CI terminal / success / running / pending / failed / other counts
- required-check state summary
- review progress comments / threads / unresolved counts
- limitations count / codes

これにより `ci=running` のまま `checks=1/4 -> 2/4 -> 3/4` と進んだ場合も quiet が reset される。

### 5. line rendering

Rendering rule:

- prefix: `pr_obs`
- always: `poll`, `elapsed`, `remain`, `phase`, `ci`, `review`, `quiet`, `stable`, `limit`, `final=stdout_json`
- CI detailed only while not terminal compact.
- Review detailed while observing or human gate count helps.
- target max: 200-240 chars.
- truncation: string slice ではなく optional fields drop。
- default `limit=none`; optional fields drop 時のみ `limit=truncated`。

### 6. provider / dogfooding mirror

Source of truth は provider side:

- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`

Dogfooding mirror:

- `.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`

両者の parity を維持する。

## Interface Impact

- `wait_pr_observation.sh --progress stderr-summary` の stderr line content が richer になる。
- stdout final JSON は現行 authority を維持する。
- `--progress none` は挙動維持。
- `events.ndjson` が有効な `--out` 使用時は、任意で compact progress state を poll event に追加してよい。ただし必須 schema にはしない。

## Acceptance Criteria Draft

- CI running 中の progress line に `checks=done/total ok=N run=N pend=N fail=N` が出る。
- CI passed 後は `ci=passed` の compact 表示になり、通常は CI counters を出さない。
- Review observing 中は `comments=N` が trigger-window current Codex review comments / review signals count として増える。
- `comments=N` 増加、CI checks count 変化、limitations 変化で quiet が reset される。
- stdout は final JSON のみで、stderr progress と混ざらない。
- `--progress none` では stderr progress が出ない。
- progress line は body / URL / reviewer name / job name / workflow name を含まない。
- provider / mirror scripts は一致する。

## Risks

- progress line が長くなりすぎる。
  - optional field drop と `limit=truncated` で抑える。
- review count 定義が実装上ぶれる。
  - `@codex review` trigger 以後の current Codex review comments / review signals count として固定する。
- quiet fingerprint と progress projection が再び乖離する。
  - projection fields を fingerprint source に含める tests を追加する。

## Canonical Adoption Target

次に canonical docs へ反映する場合:

- `requirement.md`: Progress 表示要件、quiet reset 要件、`comments=N` 定義。
- `design.md`: Progress line contract、projection / fingerprint 設計。
- `plan.md`: S05 follow-up step または新 step として tests / implementation / review を追加。
- `report.md`: interview 回答と discussion adoption を記録。
