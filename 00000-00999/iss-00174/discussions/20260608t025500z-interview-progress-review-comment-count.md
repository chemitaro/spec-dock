# Interview: progress line の review comment count 定義

## Status

answered

## Context

`wait_pr_observation.sh` の stderr progress 表示について、ユーザーは「レビューの最中であれば、レビューとしてついたコメントの数が 0, 1, 2, 3 と増えていくべき」と指摘した。

既存 research では `comments=N` の候補として次が残っている。

- PR 全体の review comments 件数。
- Codex authored comments 件数。
- trigger window 後に捕捉した body included comments 件数。
- current / trigger-window に入った actionable review comments 件数。
- unresolved / non-outdated inline review comments 件数。

## Source-grounded classification

- `checks=done/total`:
  - source-grounded / low-impact assumption として、まず GitHub check runs の terminal count / total を採用できる。
  - commit statuses / required-check rollup は CI status 判定と limitations に使い、progress denominator へ混ぜない方がシンプル。
- Review compact timing:
  - low-impact assumption として、`observation_complete=true` を compact 表示切り替え基準にできる。
- Phase naming:
  - implementation detail として既存 `wait|terminal|timeout` を維持し、必要なら後続で `waiting_ci|waiting_review|stabilizing` へ拡張できる。
- Final JSON progress-only fields:
  - low-impact assumption として、stdout final JSON の authority は既存 `ci.*` / `review.*` を維持し、progress 専用 projection は stderr と optional events に留める。

## User-intent blocker

`comments=N` の定義は、ユーザーが見たい「レビューとしてついたコメントの数」がどの範囲かに依存する。

ここを誤ると、progress line がユーザー期待より少なく見える、または古い / 無関係な review comments を数えてノイズになる。

## Recommended question

progress line の `comments=N` は、`@codex review` trigger 以後に今回の観測窓で新しく捕捉した Codex review comments / review signals の件数として定義してよいですか。

推奨は yes。理由は、古い PR 全体コメントや過去の unresolved thread を毎回積み上げると「今回のレビューが進んでいる」ことが読みにくくなるため。

## Answer

Yes.

`comments=N` は、`@codex review` trigger 以後に今回の観測窓で新しく捕捉した Codex review comments / review signals の件数として定義する。

古い PR 全体コメントや過去の unresolved thread を毎回数えるのではなく、「今回のレビューが 0 -> 1 -> 2 と進んでいる」ことを読める progress count とする。

## Adoption target

回答を次に反映する。

- `discussions/20260608t024500z-research-progress-line-two-stage-status-analysis.md`
- 必要に応じて `requirement.md`
- 必要に応じて `design.md`
- `report.md` の Decision / Evidence Adoption Ledger

## Adoption status

- `discussions/20260608t024500z-research-progress-line-two-stage-status-analysis.md` に反映済み。
- Canonical requirement / design への反映は、次の仕様更新フェーズで行う。
