---
種別: discussion
ID: "20260616t072719z-10"
タイトル: "PR observation snapshot/wait Python extraction architecture draft"
状態: "draft"
作成日: "2026-06-16"
作成者: "system-architect draft via orchestrator"
対象Issue: "iss-00187"
created_by_role: "system-architect"
scope_id: "iss-00187"
source_paths:
  - "spec-dock/active/issue/design.md"
  - "spec-dock/active/issue/plan.md"
  - "src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh"
  - "src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh"
intended_targets:
  - "spec-dock/active/issue/design.md"
  - "spec-dock/active/issue/plan.md"
  - "spec-dock/active/issue/report.md"
adoption_status: "unreviewed"
reflected_to: []
diff_guard_result: "passed by orchestrator diff review against current canonical docs"
adoption_ledger_note: "Adoption authority is recorded in report.md EAL-030, Spec Authoring Gate S300+ addendum, Delegated Draft Evidence, and D-015."
---

# PR observation snapshot/wait Python extraction architecture draft

## 目的

このドラフトは、`iss-00187` の追加 follow-up として、PR observation scripts に残る大きな Python heredoc を standalone Python entrypoint へ抽出するための設計案である。

今回の直接対象は次の 2 つに限定する。

- `fetch_pr_observation_snapshot.sh`
- `wait_pr_observation.sh`

`fetch_pr_review_snapshot.sh` と `trigger_codex_review.sh` にも Python heredoc は残っているが、前者は review lifecycle collector、後者は review trigger initiation であり、snapshot/wait extraction とは責務が異なる。そのため、このドラフトでは follow-up target として扱う。

## 現状分析

`fetch_pr_checks_snapshot.sh` はすでに薄い shell wrapper になっており、検証済みの `OBS_*` 環境変数を渡して `lib/pr_observation_checks.py` を実行する構造になっている。この形を snapshot/wait に広げる。

`fetch_pr_observation_snapshot.sh` に残る Python heredoc の責務は次の通り。

- `gh pr view` の JSON から `headRefOid` を抽出する小さな metadata parsing
- collection head / final head の freshness 判定
- checks collector と review collector の stdout JSON merge
- `limitations`、`summary`、`normalized_status`、`decision`、`recommended_next_action`、`artifacts` の final JSON 生成

`wait_pr_observation.sh` に残る Python heredoc の責務は次の通り。

- trigger handling 後の snapshot polling
- semantic fingerprint の算出
- quiet / same-fingerprint stability 判定
- zero-check grace handling
- `review_completion_unknown` の trigger age / CI-passed age guard
- timeout / fallback JSON
- `out_dir` artifacts、resume metadata、stderr progress rendering

現状は shell file が CLI wrapper と Python application logic の両方を持っており、レビュー粒度、テスト粒度、保守性が悪い。

## 採用する責務分離

### Shell wrapper

Shell は公開 CLI 互換レイヤーとして残す。

- usage/help を維持する
- 既存引数と validation を維持する
- invalid usage は `64` のままにする
- caller-provided arbitrary endpoint / query / raw `gh` args は受け付けない
- provider-local Python entrypoint を `script_dir` から解決して実行する
- stdout は Python entrypoint の final JSON をそのまま流す
- progress / diagnostics は stderr のみとする

### Python snapshot entrypoint

推奨ファイル:

- `scripts/lib/pr_observation_snapshot.py`

責務:

- fixed `gh pr view --json headRefOid,url,state,isDraft,number` の metadata collection
- expected/current/final head freshness 判定
- `lib/fetch_pr_checks_snapshot.sh` と `lib/fetch_pr_review_snapshot.sh` の fixed subprocess invocation
- checks/review JSON の merge
- top-level `normalized_status`、`recommended_next_action`、`decision`、`fingerprint`、`artifacts` の生成
- `--out` 指定時の snapshot artifacts を現行互換で書く

### Python wait entrypoint

推奨ファイル:

- `scripts/lib/pr_observation_wait.py`

責務:

- `post-once` の場合に fixed `trigger_codex_review.sh` を呼ぶ
- `resume` の場合は shell validation 済みの trigger metadata を前提にする
- fixed snapshot command を poll する
- semantic fingerprint / quiet / same-fingerprint / zero-check grace / latency guard を管理する
- `review_completion_unknown` を non-pass `human_gate` としてのみ確定する
- `result.json`、`latest.json`、`latest_delta.json`、`events.ndjson`、`snapshots/`、`raw/` を現行互換で書く
- stderr progress line の内容と頻度を維持する

### Optional common module

共通 helper は最初から大きく作らない。抽出後に実際の重複が問題になる場合だけ、次のような最小 helper を検討する。

- `scripts/lib/pr_observation_common.py`
- 候補: `classify_github_stderr`、`token_source`、`sha256_json`、`parse_utc_timestamp`、`sha_prefix_matches`、safe JSON load/dump

## 依存方向

```text
fetch_pr_observation_snapshot.sh
  -> lib/pr_observation_snapshot.py
       -> lib/fetch_pr_checks_snapshot.sh
       -> lib/fetch_pr_review_snapshot.sh
       -> gh pr view fixed metadata

wait_pr_observation.sh
  -> lib/pr_observation_wait.py
       -> fetch_pr_observation_snapshot.sh
       -> trigger_codex_review.sh

lib/pr_observation_checks.py
lib/pr_observation_snapshot.py
lib/pr_observation_wait.py
  -> optional lib/pr_observation_common.py
```

`pr_observation_wait.py` は `pr_observation_snapshot.py` を import して内部関数を直接呼ばない。wait は public snapshot script contract を poll することで、既存 shell CLI / stdout JSON contract を integration surface として維持する。

## 互換性方針

維持するもの:

- shell script names
- existing CLI flags
- invalid usage exit `64`
- stdout single final JSON authority
- stderr progress / diagnostics
- `out_dir` artifact names and shape
- trigger resume metadata
- semantic fingerprint behavior
- `review_completion_unknown` timing and non-pass semantics

`review_completion_unknown` は引き続き次の意味を持つ。

- `normalized_status="human_gate"`
- `decision.status="unknown"`
- `decision.status_reason="review_completion_unknown"`
- `recommended_next_action="human_gate"`
- `passed` ではない
- `merge_prepared` ではない

## 段階移行方針

1. Characterization first
   - 現在の heredoc inventory と既存テスト coverage を記録する。
   - 既存 behavior tests を抽出前後の equivalence evidence として使う。

2. Snapshot extraction
   - `fetch_pr_observation_snapshot.sh` の Python logic を `pr_observation_snapshot.py` へ移す。
   - metadata parsing heredoc も最終的には shell から消す。
   - JSON shape / status taxonomy / artifacts / exit behavior は変えない。

3. Wait extraction
   - `wait_pr_observation.sh` の Python logic を `pr_observation_wait.py` へ移す。
   - S204 で導入した timing guard と resume behavior を変えない。

4. Mirror / docs / scaffold sync
   - provider source を正本として、repo root `.agents/...` mirror を同期する。
   - new Python assets が init/update で install されることをテストする。

5. Final validation
   - focused tests、broad tests、`git diff --check`、`spec-dock validate`、provider/mirror cmp、PR latest-head observation を行う。

## テスト方針

抽出は behavior-preserving なので、テストは「新しい behavior」より「既存 contract の保持」を中心にする。

必要な観点:

- snapshot invalid args are rejected before `gh`
- wait invalid args are rejected before trigger/snapshot/`gh`
- snapshot metadata failure returns JSON with redacted stderr hash
- initial/final head mismatch remains `stale_head`
- checks/review collector failures remain explicit limitations
- missing review completion remains pending before wait stability
- wait preserves pending/running CI as wait/resume
- quiet / same-fingerprint behavior is preserved
- `review_completion_unknown` is delayed by trigger age and CI-passed age
- late submitted/unresolved review overrides unknown candidate
- timeout preserves latest payload
- stdout/stderr/progress/out_dir artifacts remain compatible
- `pr_observation_snapshot.py` and `pr_observation_wait.py` are installed by init/update
- provider/mirror changed files match

推奨 focused commands:

```sh
uv run pytest tests/unit/infra/test_init_update.py -k "pr_observation_snapshot or pr_observation_wait or review_completion_unknown or issue_187"
uv run pytest tests/unit/infra/test_init_update.py -k "installed_by_init_and_update or python_asset"
git diff --check
./spec-dock/scripts/spec-dock validate
```

## リスク

- Behavior drift:
  - 現行 heredoc は nested JSON を in-place mutation しており、順序変更が fingerprint / decision_fingerprint / timeout classification に影響する可能性がある。
  - 対策: characterization tests と exact JSON field assertions。

- Missing installed asset:
  - shell wrapper が新しい `.py` を呼ぶが init/update で配布されない可能性がある。
  - 対策: installed asset test。

- Mirror drift:
  - provider は修正済みでも dogfooding `.agents/...` が stale になる可能性がある。
  - 対策: S390 で provider/mirror `cmp -s`。

- Over-abstraction:
  - common helper を早く作りすぎると mini-framework 化する。
  - 対策: shared helper は必要になった場合だけ最小化する。

- Self-referential PR observation:
  - 変更対象が PR observation 自体なので、final doc/report commit 後に最新 head で PR observation を再実行する必要がある。

## canonical docs への採用案

`design.md` へ採用する場合の追記ポイント:

- `Script Boundary / Python Entrypoint Extraction` subsection を追加する。
- `fetch_pr_checks_snapshot.sh -> pr_observation_checks.py` を先行例として明記する。
- `pr_observation_snapshot.py` と `pr_observation_wait.py` を module dependency diagram に追加する。
- direct target と follow-up target を分ける。
  - direct: snapshot / wait
  - follow-up: review collector / trigger
- shell wrapper が public CLI / validation / stdout JSON / stderr progress / exit code / fixed command surface を保持することを明記する。

## 未確定事項

Blocking clarification はない。

推奨 default:

- common helper は S301/S303 の抽出後、必要性が具体化するまで defer する。
- metadata `gh pr view` 実行は、テストが十分に lock できるなら `pr_observation_snapshot.py` に寄せる。
- `fetch_pr_review_snapshot.sh` / `trigger_codex_review.sh` の heredoc extraction は別 follow-up にする。

No canonical edit, final authority, promotion, reviewer-pass, or implementation-readiness is claimed by this draft.
