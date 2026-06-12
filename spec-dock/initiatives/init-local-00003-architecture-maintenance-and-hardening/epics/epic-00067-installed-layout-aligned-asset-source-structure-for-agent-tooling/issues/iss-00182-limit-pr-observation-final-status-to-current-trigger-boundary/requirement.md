---
種別: 要件定義書（Issue）
ID: "iss-00182"
タイトル: "Limit PR observation final status to current trigger boundary"
関連GitHub: ["#182"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-12"
親: ["epic-00067", "init-local-00003"]
---

# iss-00182 Limit PR observation final status to current trigger boundary — 要件定義

## 目的

`github-pr-observation` の最終出力と最終判定を、直近の `@codex review` trigger または resume boundary に紐づく current decision artifacts に限定する。

古い review / thread は debug / audit context として保持できるが、final status、recommended action、wait stability、progress 表示の判定根拠に混ざらないようにする。

## 背景・現状

PR #181 の監視では、GitHub token の権限不足はなく、CI は成功し、head SHA も一致していた。一方で final output は `human_gate` / `wait_or_resume` になり、出力内に古い review thread が残っていた。

調査では、historical unresolved thread は `codex_review.collection_summary.review_threads` では current boundary から除外されていた。PR #181 の top-level `human_gate` の直接原因は、current boundary の Codex issue comment を `fallback_issue_comment` として低信頼扱いしたことと見るのが妥当である。

ただし final JSON は、decision-scoped artifacts と all-fetched historical context を同じ `review` 配下に混在させている。利用者や後続 agent は、古い unresolved thread が final decision に混ざったように誤読しやすい。

## 情報源

- `discussions/20260612t012333z-research-pr-observation-final-output-boundary-analysis.md`
- `discussions/20260612t014627z-interview-fallback-issue-comment-decision-boundary.md`
- `/private/tmp/iss-00180-pr181-observation-3/result.json`
- `/private/tmp/iss-00180-pr181-observation-3/events.ndjson`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`

## 対象ユーザー / 利用シナリオ

- 主な利用者:
  - `github-pr-observation` skill を使って PR review / CI / thread 状態を監視する maintainer。
  - PR observation の final JSON をもとに resume、修正委任、merge preparation を判断する後続 agent。
- 代表シナリオ:
  - PR に過去の Codex review thread が残っている状態で、直近の `@codex review` をトリガーして observation を実行する。
  - current trigger 以降に selected unresolved thread がない場合、古い thread は final decision に影響しないことを final JSON から判断する。
  - submitted PR review ではなく Codex issue comment だけが current boundary に現れた場合、top-level は `human_gate` のまま維持しつつ、古い thread 由来ではないことを出力から判断する。

## スコープ

### 必須

- final decision を current trigger / resume boundary の decision artifacts に限定する。
- decision artifacts と historical / all-fetched context を出力上で分離する。
- historical unresolved thread が selected current-boundary thread ではない場合、top-level status、recommended action、progress、wait stability の blocker として扱わない。
- `fallback_issue_comment` は top-level final status を pass / complete にしない。
- current boundary 由来で、かつ問題なしを示す fallback issue comment は、`fallback_pass_candidate` 相当の準成功信号として観測可能にする。
- `human_gate` の理由を区別できるようにする。
  - selected current-boundary unresolved thread 由来。
  - selected current-boundary changes requested 由来。
  - fallback issue comment の confidence 由来。
  - blocking limitation / stale head / CI failure 由来。
- wait / resume の安定判定に使う fingerprint は final decision に影響する current-boundary artifacts を基準にする。
- debug / audit 用に historical context を残す場合は、scope が all-fetched / historical であることを明示する。
- shipped skill の利用者向け docs / output semantics を更新する。

### 禁止

- 古い review thread を current selected thread として扱うこと。
- historical context の unresolved count を、scope 明示なしに final decision-facing count として出すこと。
- submitted PR review ではない issue comment を、今回の issue で即 merge-ready / pass 相当の top-level completion に昇格すること。
- `review.threads.items` や `review.codex_authored` の既存情報を削除して、debug 不能にすること。
- provider-side authority である `src/spec_dock/assets/install_root/` 以外を主要実装 source-of-truth として扱うこと。

### 対象外

- GitHub token permission / doctor capability の追加改善。
- Codex の review 本文分類を汎用自然言語判定として高度化すること。
- GitHub API から取得できない review thread の完全復元。
- PR merge / issue finish の workflow 全体の再設計。
- `fallback_issue_comment` を top-level pass / complete にするポリシー変更。

## 境界

- 常に行う:
  - final decision と historical context の scope を分ける。
  - selected ids / selected unresolved count を final decision-facing source とする。
  - all-fetched context を残す場合は audit / history として表現する。
- 判断が必要:
  - 既存 field をどこまで additive に残し、どの新 field を authoritative とするか。
  - `fallback_pass_candidate` 相当の field 名と配置。
- 行わない:
  - issue comment を submitted PR review と同等の primary completion source として扱うこと。

## 非交渉制約

- agent-tooling assets の provider-side source-of-truth は `src/spec_dock/assets/install_root/` とする。
- canonical `spec-dock/` dogfooding workspace は確認対象であり、実装 source-of-truth ではない。
- final status の意味は後続 agent が誤読しない形で明示する。
- 既存の debug / audit 情報を消す場合は互換性リスクとして扱い、原則 additive migration を優先する。

## 受け入れ条件

- AC-001: historical thread は final decision に混ざらない
  - アクター: PR observation を実行する maintainer / agent。
  - 前提: latest trigger より前の Codex review thread が unresolved のまま残っている。
  - 操作: expected head SHA を指定して PR observation snapshot / wait を実行する。
  - 期待結果: historical unresolved thread は audit / history context として観測できるが、current decision の selected unresolved count、top-level status reason、recommended action、decision fingerprint には混ざらない。
  - 観測点: final JSON、wait event、unit / CLI runtime test。

- AC-002: current selected unresolved thread は final decision に反映される
  - アクター: PR observation を実行する maintainer / agent。
  - 前提: latest trigger / resume boundary 以降の Codex-selected review thread が unresolved である。
  - 操作: PR observation snapshot / wait を実行する。
  - 期待結果: top-level status は human gate 系になり、recommended action は review feedback 対応を示し、selected thread id と unresolved id が追跡できる。
  - 観測点: final JSON、selected ids、status reason、unit / CLI runtime test。

- AC-003: fallback issue comment は top-level pass にしない
  - アクター: PR observation を実行する maintainer / agent。
  - 前提: CI passed、head matched、limitations empty、selected unresolved thread 0、current boundary に Codex issue comment の no-major-issues 相当本文だけがある。
  - 操作: PR observation snapshot / wait を実行する。
  - 期待結果: top-level status は `human_gate` / `wait_or_resume` のままで、observation complete / pass 相当にはならない。
  - 観測点: final JSON、recommended action、unit / CLI runtime test。

- AC-004: fallback no-major-issues comment は準成功信号として観測できる
  - アクター: PR observation を読む maintainer / agent。
  - 前提: AC-003 と同じ。
  - 操作: final JSON を確認する。
  - 期待結果: current boundary 由来の fallback comment が問題なしを示す場合、`fallback_pass_candidate` 相当の準成功信号、理由、source artifact を確認できる。
  - 観測点: final JSON の decision / lifecycle surface。

- AC-005: fingerprint は decision と audit で分離される
  - アクター: wait script を実行する maintainer / agent。
  - 前提: current decision artifacts は変わらず、historical thread だけが更新される。
  - 操作: wait / snapshot を複数回実行する。
  - 期待結果: final decision に使う fingerprint は historical-only change で変化しない。debug / audit fingerprint を出す場合は別名で観測できる。
  - 観測点: wait JSON、snapshot JSON、unit / CLI runtime test。

- AC-006: output semantics が docs に固定される
  - アクター: shipped `github-pr-observation` skill を読む maintainer / agent。
  - 前提: issue 実装後の shipped skill docs を確認する。
  - 操作: output status / decision / history / fallback の説明を読む。
  - 期待結果: final decision が current trigger / resume boundary に基づくこと、historical context が audit 用であること、`fallback_issue_comment` が top-level pass ではないことが分かる。
  - 観測点: `SKILL.md`、docs/spec review。

## 例外・エッジケース

- EC-001: trigger が推定である場合
  - 条件: explicit trigger comment を特定できず、trigger boundary が inferred になる。
  - 期待: inferred boundary である limitation / confidence を明示し、historical context と current decision を混同しない。
  - 観測点: limitations、status reason、decision source。

- EC-002: selected ids が空で fallback comment もない場合
  - 条件: CI passed / head matched だが、current boundary の review completion signal がない。
  - 期待: pass ではなく unknown / wait / human gate 系の安全側 status になり、理由が観測できる。
  - 観測点: final JSON、recommended action。

- EC-003: current selected review thread と historical thread が同時に存在する場合
  - 条件: current selected unresolved thread と historical unresolved thread の両方がある。
  - 期待: final decision は current selected thread を理由に human gate になる。historical thread は audit context として分離される。
  - 観測点: selected ids、history ids、status reason。

- EC-004: existing consumer が legacy `review.threads` を読んでいる場合
  - 条件: 既存 output の `review.threads` / `review.codex_authored` に依存する debug tooling がある。
  - 期待: 互換性のため既存 field を残す場合は `scope: all_fetched` 等で明示し、新 authoritative field を別に提供する。
  - 観測点: output schema、docs。

## 入力→出力例

- EX-001: historical unresolved thread と fallback issue comment があるケース
  - 入力:
    - expected head SHA は current PR head と一致。
    - CI は passed。
    - current trigger 以前の unresolved thread が 1 件。
    - current trigger 以降の selected unresolved thread は 0 件。
    - current trigger 以降に Codex issue comment が no-major-issues 相当本文を投稿。
  - 出力:
    - top-level status: `human_gate`
    - recommended action: `wait_or_resume`
    - decision selected unresolved count: `0`
    - fallback decision: `fallback_pass_candidate` 相当の準成功信号あり
    - historical thread: audit / history context に分離

## 用語

- TERM-001: current trigger / resume boundary
  - 直近の `@codex review` trigger または resume 実行が final decision の対象にする時間・artifact 境界。
- TERM-002: decision artifacts
  - final status、recommended action、observation complete、wait stability を決めるために使う current-boundary artifacts。
- TERM-003: historical / audit context
  - debug や経緯説明のために残す all-fetched artifacts。final decision の根拠ではない。
- TERM-004: selected artifacts
  - current boundary に基づいて collector が選択した review / comment / thread ids。
- TERM-005: fallback issue comment
  - submitted PR review ではなく、Codex の issue comment で review 結果らしき情報が得られる状態。
- TERM-006: fallback pass candidate
  - fallback issue comment が問題なしを示すことを表す準成功信号。top-level pass / complete ではない。

## 未確定事項

- なし。
  - `fallback_issue_comment` の扱いは interview で Option C を採用済み。
