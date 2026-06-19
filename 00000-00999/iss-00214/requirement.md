---
種別: 要件定義書（Issue）
ID: "iss-00214"
タイトル: "PR Observation Review Target State"
関連GitHub: ["#214"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-19"
親: ["epic-00158", "init-local-00003"]
---

# iss-00214 PR Observation Review Target State — 要件定義

## 目的

`wait_pr_observation.sh` の progress line で、`review=` が観測者側の状態ではなく、監視対象である Codex review の状態を表示するようにする。
通常 wait flow の operator が Codex review 未起動と誤認して、手動で追加の `@codex review` trigger を投稿するリスクを下げる。

## 背景・現状

- 対象 workflow:
  - `.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
  - provider-side authority: `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/`
  - dogfooding mirror: `.agents/skills/github-pr-observation/`
- 現状の挙動:
  - wait 中かつ observation 未完了の progress line では、`review=` が `review=observing` と表示される。
  - 例: `pr_obs poll=3 ... phase=wait ci=running ... review=observing comments=0 threads=0 unresolved=0 ...`
- 現状の課題:
  - `review=observing` は監視対象の Codex review 状態ではなく、スクリプトが観測中であるという観測者側の状態を表している。
  - `review=observing comments=0 threads=0 unresolved=0` が続くと、operator は `@codex review` trigger が投稿されていない、または Codex review が起動していないと誤認しやすい。
  - 通常 wait flow では `wait_pr_observation.sh` が default `post-once` で fixed `@codex review` trigger を 1 回投稿するため、caller / agent は手動で `@codex review` を投稿してはならない。
- 観測点:
  - `stderr` progress line の `review=` field。
  - final `stdout` JSON の `decision` / `decision_fingerprint` / `recommended_next_action` contract。
  - `tests/unit/infra/test_init_update.py` の PR observation wait regression tests。
- 情報源:
  - GitHub issue `#214`
  - `spec-dock/active/issue/discussions/20260619t064501z-research-review-progress-target-state-source-analysis.md`
  - `spec-dock/active/issue/discussions/20260619t064502z-interview-review-pending-state-naming.md`

## 対象ユーザー / 利用シナリオ

- 主な利用者:
  - PR 作成後または push 後に、Codex review と CI を同じ trigger boundary で観測する agent / operator。
- 代表シナリオ:
  - Agent が `wait_pr_observation.sh` を通常 wait flow で実行する。
  - Script が fixed `@codex review` trigger を投稿し、CI と Codex review を poll する。
  - Progress line を読んだ operator が、手動で追加 trigger を投稿すべきか、待機すべきかを判断する。

## スコープ

- 必須:
  - `progress_line(...)` が wait 中の review status を無条件に `observing` へ上書きしない。
  - `review=` には、観測者側の状態ではなく、監視対象である Codex review の target state を表示する。
  - Trigger comment は投稿済みだが、Codex review の completion / comment signal がまだ観測できない待機中状態を `review=pending_signal` と表示する。
  - Unresolved review comments / threads がある場合は、`review=unresolved` と `comments` / `threads` / `unresolved` count が読める。
  - Codex review が major issues なしで完了した場合は、progress line または final output でその target state が分かる。
  - Provider-side source と dogfooding mirror の両方で変更内容を確認する。
  - Existing final JSON contract、`decision` / `decision_fingerprint` の authoritative semantics を維持する。
- 禁止:
  - `review=` を観測者側の状態で上書きすること。
  - `running` のように、GitHub / Codex 側の処理中シグナルがない状態を過剰に断定すること。
  - `wait_pr_observation.sh` の default `post-once` 仕様を変更すること。
  - Caller / agent が通常 wait flow で手動 `@codex review` を投稿する policy を弱めること。
  - `fetch_pr_observation_snapshot.sh` の read-only contract を変更すること。
  - PR repair triage / disposition logic、GitHub token 権限モデル、resume mode の semantics を変更すること。
- 対象外:
  - 自動 trigger reuse mode の追加。
  - Review body collection や selected review inventory の再設計。
  - Final readiness / merge-prepared decision の semantics 変更。
  - PR observation 以外の SpecDock workflow 表示改善。

## 境界

- 常に行う:
  - Progress line は bounded ASCII key/value summary として維持する。
  - `stdout` JSON を machine-readable authority、`stderr` progress を non-authoritative diagnostic として扱う。
  - `decision` と `decision_fingerprint` を current trigger boundary の final-status authoritative inputs として維持する。
  - `review_completion_unknown` は latency guards 後の human gate 状態として、通常 wait 中の `pending_signal` と区別する。
- 判断が必要:
  - `review=pending_signal` を導出する具体条件は design で固定する。
  - Progress line の length cap / optional field drop order への影響は design / plan で検証対象にする。
- 行わない:
  - Observer state 用の `observer=` / `wait=` field は今回追加しない。
  - `review=none` を trigger 済み signal 待ち状態の operator-facing 表示には使わない。

## 非交渉制約

- `review=pending_signal` は、ユーザー回答に基づく採用済み operator-facing 表示名である。
- `review=` は観測対象の状態を表示する。観測者側の状態を表示しない。
- Existing public script entrypoint は `.sh` wrapper のまま維持する。
- Provider-side source が shipped asset authority であり、dogfooding mirror は検証対象である。

## 受け入れ条件

- AC-001:
  - アクター: PR observation wait script を見る operator / agent。
  - 前提: `wait_pr_observation.sh` が wait phase にあり、trigger comment は投稿済みだが、Codex review の completion / comment signal はまだない。
  - 操作: Progress line を確認する。
  - 期待結果: `review=observing` ではなく `review=pending_signal` が表示される。
  - 観測点: `stderr` progress line。
- AC-002:
  - アクター: PR observation wait script を見る operator / agent。
  - 前提: Current trigger boundary に unresolved Codex review feedback がある。
  - 操作: Progress line を確認する。
  - 期待結果: `review=unresolved` と、`comments` / `threads` / `unresolved` count が読める。
  - 観測点: `stderr` progress line。
- AC-003:
  - アクター: Downstream orchestration / agent。
  - 前提: Wait result final JSON が生成される。
  - 操作: `stdout` JSON の `decision` / `decision_fingerprint` / `recommended_next_action` を確認する。
  - 期待結果: Existing authoritative final JSON contract は変更されていない。
  - 観測点: `stdout` JSON と existing regression tests。
- AC-004:
  - アクター: SpecDock maintainer。
  - 前提: Shipped PR observation asset を変更する。
  - 操作: Provider-side source と dogfooding mirror を確認する。
  - 期待結果: Provider-side source が変更され、dogfooding mirror も同等の behavior を持つ。
  - 観測点: `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/...`、`.agents/skills/github-pr-observation/...`、targeted tests。

## 例外・エッジケース

- EC-001:
  - 条件: CI は passed だが、Codex review completion signal は latency guard 未満でまだ観測されていない。
  - 期待: `review=pending_signal` として wait / resume path の状態が読める。`review_completion_unknown` へ早期昇格しない。
  - 観測点: Progress line と final JSON。
- EC-002:
  - 条件: Latency guards を満たした後も trusted Codex review completion signal がなく、actionable review inventory も空である。
  - 期待: Existing `review_completion_unknown` / `human_gate` semantics を維持し、通常 wait 中の `pending_signal` と区別できる。
  - 観測点: Existing no-completion regression tests。
- EC-003:
  - 条件: Codex review は fallback issue comment だけで観測される。
  - 期待: Existing fallback low-confidence human gate / wait_or_resume semantics を維持し、`review=` 表示変更が final decision を promote しない。
  - 観測点: Existing fallback regression tests。
- EC-004:
  - 条件: Progress line が length cap に近い。
  - 期待: `pending_signal` 表示により、既存の bounded summary / optional field dropping contract が破綻しない。
  - 観測点: Existing line budget regression tests。

## 入力→出力例

- EX-001:
  - 入力: `phase=wait`, trigger comment posted, `review.status=none`, no completion / comment signal.
  - 出力: `pr_obs ... phase=wait ... review=pending_signal comments=0 threads=0 unresolved=0 ...`
- EX-002:
  - 入力: `phase=wait`, current unresolved review feedback selected.
  - 出力: `pr_obs ... phase=wait ... review=unresolved comments=4 threads=3 unresolved=3 ...`
- EX-003:
  - 入力: `phase=terminal`, Codex review completion passed / approved and CI passed.
  - 出力: Progress line or final JSON shows the target review state without `review=observing`.

## 用語

- `review=`:
  - Progress line 上の key。監視対象である Codex review の target state を表示する。
- `pending_signal`:
  - Trigger comment は投稿済みだが、Codex review の completion / comment signal がまだ観測されていない wait 中の target state。
- `observing`:
  - 観測者側の状態を表すため、この issue の `review=` 表示では使わない。
- `review_completion_unknown`:
  - CI passed、head matched、actionable review inventory empty、trusted Codex review completion signal missing の状態が latency guards 後も続いた場合の non-pass human gate 状態。

## 未確定事項

- Blocking:
  - なし。
- Non-blocking:
  - `pending_signal` の exact derivation は design で固定する。
  - Progress line の length budget への影響は plan の verification で固定する。
