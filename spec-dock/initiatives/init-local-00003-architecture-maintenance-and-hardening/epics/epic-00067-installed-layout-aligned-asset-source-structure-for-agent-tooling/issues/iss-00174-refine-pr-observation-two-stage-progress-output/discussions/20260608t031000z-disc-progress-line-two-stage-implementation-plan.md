# Implementation Plan Draft: PR observation progress line 二段階表示

## 位置づけ

本資料は、progress line 二段階表示を実装するための具体的な実装計画案である。Canonical `plan.md` へ昇格する前の discussion artifact として扱う。

関連資料:

- `20260608t024500z-research-progress-line-two-stage-status-analysis.md`
- `20260608t025500z-interview-progress-review-comment-count.md`
- `20260608t030500z-disc-progress-line-two-stage-design-proposal.md`

## 実装対象

Provider source of truth:

- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`

Dogfooding mirror:

- `.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`

Tests:

- `tests/unit/infra/test_init_update.py`

## 変更方針

- 新しい GitHub API call は追加しない。
- `fetch_pr_observation_snapshot.sh` / checks / review collectors の schema を大きく変えない。
- wait wrapper の progress projection / semantic fingerprint / rendering を中心に変更する。
- stdout final JSON authority は維持する。

## Step 1: Red tests

担当: dev-coder

追加または更新する focused tests:

1. CI running progress detail
   - fake snapshot で `ci.check_runs.total=4`, `success=2`, `running=2` を返す。
   - stderr に `ci=running`, `checks=2/4`, `ok=2`, `run=2`, `pend=0`, `fail=0` が出る。
2. CI progress resets quiet
   - poll ごとに `checks=0/3 -> 1/3 -> 2/3 -> 3/3` と変化させる。
   - `latest_change_poll` が最後の count 変化 poll を指す。
   - progress line の quiet が count 変化後に reset される。
3. CI compact after passed
   - terminal success では `ci=passed` を出し、通常の detailed `checks=` は省略する。
4. Review observing comments count
   - trigger-window current Codex review comments / signals が `0 -> 1 -> 2` と増える。
   - stderr に `comments=0`, `comments=1`, `comments=2` が出る。
   - comment count 変化で `latest_change_poll` が更新される。
5. Review compact after stable
   - `observation_complete=true` 相当で compact status へ畳む。
   - `review=unresolved` の human gate では `comments=N` / `threads=N` / `unresolved=N` の最小 count が残る。
6. stdout / stderr boundary
   - stdout は final JSON のみ。
   - progress line に body、URL、reviewer name、workflow name、job name が出ない。
7. line bound and truncation
   - optional fields が多い payload でも 240 chars 程度に収まり、必要なら `limit=truncated`。
   - token途中の単純 slice ではなく optional fields drop を期待する。

Expected Red:

- 現行 `progress_line()` は coarse status しか出さないため、1 / 3 / 4 / 7 が fail する。
- 現行 semantic fingerprint は CI count progress を見ないため、2 が fail する可能性が高い。

## Step 2: Implement progress projection

担当: dev-coder

`wait_pr_observation.sh` 内 Python block に以下を追加する。

- `ci_progress_counts(payload) -> dict`
- `review_progress_counts(payload) -> dict`
- `progress_state(payload, phase, quiet_elapsed, quiet_required, same_count, same_required, observation_complete) -> dict`
- `render_progress_line(state) -> str`

Implementation notes:

- CI counts は `payload["ci"]["check_runs"]` を優先する。
- `done = success + failed + neutral + skipped + other_terminal` とする。ただし現行 aggregate に `skipped` がなければ `success + failed + neutral + other` から開始する。
- Review `comments` は user answer に従い、trigger-window current Codex review comments / review signals の count とする。
- Current payload で direct に count できない場合は、`review.codex_authored` から `omitted_reason != "trigger_unknown"` / stale / trigger-window metadata を使って projection する。難しければ first implementation では review collector が既に出す current fields に限定し、missing は `comments=0` とするのではなく tests で必要な minimal path を通す。

## Step 3: Update semantic fingerprint

担当: dev-coder

`semantic_fingerprint(payload)` に progress-significant counts を含める。

Add:

- `ci.check_runs.total`
- `ci.check_runs.success`
- `ci.check_runs.failed`
- `ci.check_runs.running`
- `ci.check_runs.pending`
- `ci.check_runs.other`
- required-check state compact summary
- review progress comments count
- review threads / unresolved counts
- limitation codes / count if not already included

Goal:

- `ci=running` の status が変わらなくても `checks=1/4 -> 2/4` で quiet reset する。
- review comment count が増えたら quiet reset する。
- no-change poll では quiet が伸び、same count が増える。

## Step 4: Render two-stage progress

担当: dev-coder

Rendering rules:

- Always include:
  - `pr_obs`
  - `poll`
  - `elapsed`
  - `remain`
  - `phase`
  - `ci`
  - `review`
  - `quiet`
  - `stable`
  - `limit`
  - `final=stdout_json`
- Include CI counters only when CI is not compact terminal.
- Include review counters while observing; for human gate compact status keep minimal `comments` / `threads` / `unresolved`.
- Use `limit=none` by default.
- If too long, drop optional fields in this order:
  - `other`
  - `threads`
  - `unresolved`
  - `stable`
  - `pend`
  - `run`
  - then set `limit=truncated`
- Avoid raw slicing except as final defensive fallback.

## Step 5: Provider / mirror parity

担当: dev-coder

- Apply provider change first.
- Copy or sync to dogfooding mirror.
- Verify provider and mirror `wait_pr_observation.sh` parity with `diff -u`.

## Step 6: Verification

担当: dev-coder + reviewers

Commands:

```sh
uv run pytest tests/unit/infra/test_init_update.py -k "pr_observation_wait" -q
uv run pytest tests/unit/infra/test_init_update.py -k "pr_review or pr_observation" -q
bash -n src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh
bash -n .agents/skills/github-pr-observation/scripts/wait_pr_observation.sh
diff -u src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh .agents/skills/github-pr-observation/scripts/wait_pr_observation.sh
git diff --check
```

Reviewer gates:

- code-reviewer:
  - progress projection correctness
  - quiet reset semantics
  - stdout/stderr boundary
  - regression risk around timeout / zero-check / stale head / human_gate
- spec-reviewer if canonical docs are updated:
  - requirement / design / plan alignment
  - interview adoption and `comments=N` definition

## Step 7: Canonical docs adoption

担当: main orchestrator

After implementation direction is accepted:

- Update `requirement.md` Progress 表示要件。
- Update `design.md` Progress line contract and semantic fingerprint design。
- Update `plan.md` with this follow-up implementation step.
- Update `report.md` with interview answer, design discussion adoption, tests, reviews, and commit evidence.

## Commit boundary

Recommended commit:

```text
fix(pr-observation): progress表示を二段階化
```

Commit should include:

- provider wait script
- dogfooding mirror wait script
- focused tests
- canonical docs/report updates if adopted in the same execution phase

Discussion-only artifacts may be committed separately if the workflow chooses to separate planning evidence from implementation.

## Done Criteria

- `comments=N` follows the answered definition.
- CI running progress shows `checks=done/total`.
- CI count progress resets quiet.
- Review comments progress resets quiet.
- Completed CI / stable review compact as designed.
- stdout final JSON remains parseable and authoritative.
- All focused tests and shell/parity checks pass.
- Review gates pass or findings are resolved.
