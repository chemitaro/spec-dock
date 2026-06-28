---
種別: リサーチ
ID: "20260628t043053z-research"
タイトル: "Codex review trigger instruction source を script-local に差し替える分析"
状態: "draft"
作成者: "codex"
作成日: "2026-06-28"
親: ["iss-00244", "epic-00224"]
参照:
  - "../../../discussions/20260623t074444z-adr-trusted-base-sha-github-review-policy.md"
  - "../requirement.md"
  - "../design.md"
  - "../plan.md"
---

# Codex review trigger instruction source を script-local に差し替える分析

## 要約

PR #245 の dogfooding で、現行の trusted base-SHA review policy 設計が運用上の blocker になることが確認された。

現行実装は、GitHub PR の `baseRefOid` から `.github/codex/review-policy.md` を取得し、valid な場合だけ multiline `@codex review` comment を投稿する。Base branch に policy がない場合は `human_gate` とし、comment を投稿しない。

この設計は team / adversarial repo の security boundary としては理解できるが、この repository は個人開発 / dogfooding repo であり、review instruction を main merge 前に調整・検証できないことの損失が大きい。したがって、この Issue では base branch policy fetch を廃止し、comment posting script 近傍の local Markdown instruction を使用する方針へ切り替える。

## 現状

### 実装

- `.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh`
  - `policy_path = ".github/codex/review-policy.md"` を固定している。
  - `gh pr view --json headRefOid,baseRefOid,...` で base SHA を取得している。
  - `repos/{owner}/{repo}/contents/.github/codex/review-policy.md?ref={base_sha}` を GitHub API で読み込む。
  - policy が valid な場合だけ comment body に policy を含める。
  - missing / invalid / oversized / unreadable / base_sha_missing は `block_review_policy_gate()` で `human_gate` にし、comment を投稿しない。
- provider mirror:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh` に同じ実装がある。
- skill text:
  - `.agents/skills/github-pr-observation/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - いずれも trusted base policy を valid にできない場合は comment を投稿しない、と説明している。
- policy file:
  - `.github/codex/review-policy.md`
  - `src/spec_dock/assets/install_root/.github/codex/review-policy.md`
  - review trigger 用 instruction として使われているが、置き場所は GitHub/Codex の repository policy に見える。

### 文書

- Epic requirement / design / plan は trusted base-SHA policy を正としている。
- ADR `20260623t074444z-adr-trusted-base-sha-github-review-policy.md` は旧方針を accepted としていたが、本分析に合わせて script-local instruction 方針へ差し替えた。
- Issue 244 の requirement は当初 `PR review policy / GitHub Codex review trigger の再設計` を対象外としていた。ただし PR #245 の dogfooding で、この対象外領域が Issue 244 の完了判定を妨げる実害になった。

## 問題

### P1: main merge 前に review instruction を検証できない

旧方針では、review instruction を変更しても、その instruction は base branch に merge されるまで当該 PR の review trigger に使われない。

この repository では review instruction をしばらく調整する局面であり、モデルや review 運用の変化に合わせて prompt を改善する必要がある。Main merge 前に動作確認できない設計は、dogfooding と prompt iteration の速度を大きく落とす。

### P1: policy missing が no-review になる

Base branch に `.github/codex/review-policy.md` がない場合、現行 script は `human_gate` として comment を投稿しない。

しかし instruction がない場合でも Codex review 自体には価値がある。Missing policy を理由に review trigger を止めるより、instruction なしの deterministic `@codex review` comment を投稿し、review の実行機会を確保する方がこの repo の運用に合う。

### P2: `.github/codex/review-policy.md` の責務が曖昧

`.github/codex/review-policy.md` は GitHub / Codex 側の repository policy に見える。しかし実際には `trigger_codex_review.sh` が PR comment に埋め込む instruction body である。

この用途なら、`.github/codex` に置くよりも `github-pr-observation` skill の comment posting script 近傍に置く方が責務境界が明確である。

### P2: GitHub remote state と local dogfooding state が分離する

現行 script は GitHub API で base branch 上の file を読むため、local checkout の現在の変更を反映しない。

今回必要なのは「現在この branch / checkout で review trigger がどの instruction を投稿するか」であり、過去に main に入った情報ではない。

## 理想形

### Instruction source

- GitHub base branch / head branch の `.github/codex/review-policy.md` は読まない。
- Local checkout の script-local Markdown を読む。
- 採用予定 path:
  - provider authority:
    - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/codex-review-instructions.md`
  - dogfooding installed copy:
    - `.agents/skills/github-pr-observation/scripts/codex-review-instructions.md`

### Trigger behavior

- Script-local Markdown が valid:
  - comment body は `@codex review` で始まる。
  - metadata と instruction text を含める。
  - JSON payload に instruction path / hash / bytes / status / reviewed head SHA / generated body hash を記録する。
- Script-local Markdown が missing:
  - comment body は `@codex review` で始まる。
  - instruction text は含めない。
  - metadata に `instruction_status: missing_plain_fallback` を記録する。
  - `human_gate` にはしない。
- Script-local Markdown が present だが invalid / oversized / unreadable:
  - 設定ミスとして `human_gate` にする。
  - comment は投稿しない。

### Security / safety boundary

- 任意 body は引き続き禁止する。
- 任意 endpoint / method / path / raw `gh` args は引き続き禁止する。
- Write surface は `POST repos/{owner}/{repo}/issues/{pr}/comments` に限定する。
- Stale head guard は維持する。
  - comment 投稿前後に PR head SHA が expected head SHA と一致することを確認する。
- Instruction は trusted base policy ではなく、script-local review instruction と呼ぶ。

## 現実と理想の差分

| 項目 | 現状 | 理想 | 修正方針 |
|---|---|---|---|
| instruction source | GitHub base SHA の `.github/codex/review-policy.md` | local script-local Markdown | GitHub contents API fetch を削除し、script-relative file read に変更 |
| missing behavior | `human_gate` / no comment | plain deterministic `@codex review` fallback | missing を non-blocking fallback として扱う |
| invalid behavior | `human_gate` | `human_gate` | invalid / oversized / unreadable は維持 |
| terminology | trusted base review policy | script-local review instruction | skill/docs/tests/JSON keys を更新 |
| file location | `.github/codex/review-policy.md` | `.agents/.../scripts/codex-review-instructions.md` | `.github/codex/review-policy.md` を廃止 |
| metadata | base SHA / policy hash | local instruction path / hash / status / head SHA | payload schema と comment metadata を更新 |
| test fixture | GitHub contents API base fetch | local file present/missing/invalid | unit tests を置換 |

## 実装差分の具体化

### Provider / installed assets

- Add:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/codex-review-instructions.md`
  - `.agents/skills/github-pr-observation/scripts/codex-review-instructions.md`
- Remove:
  - `src/spec_dock/assets/install_root/.github/codex/review-policy.md`
  - `.github/codex/review-policy.md`

### Script

- Modify:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh`
  - `.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh`
- Remove behavior:
  - GitHub contents API read for `.github/codex/review-policy.md?ref={base_sha}`
  - base policy missing / base_sha_missing blocking gate
  - `trusted base review policy` terminology
- Add behavior:
  - script-relative `codex-review-instructions.md` read
  - missing fallback body
  - instruction metadata / hash
  - `instruction_status` JSON field or updated `review_policy.status` semantics

### Skill text

- Modify:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - `.agents/skills/github-pr-observation/SKILL.md`
- Replace:
  - trusted base policy explanation
  - no comment on missing base policy
- With:
  - script-local instruction explanation
  - missing instruction fallback
  - invalid instruction human gate

### Tests

- Modify:
  - `tests/unit/infra/test_init_update.py`
- Replace base-SHA policy fetch fixtures with:
  - local instruction present: comment includes instruction hash / path / reviewed head SHA
  - local instruction missing: deterministic `@codex review` fallback comment is posted
  - local instruction oversized: human gate / no comment
  - local instruction invalid or unreadable: human gate / no comment
  - no arbitrary body / fixed endpoint contract remains enforced

### Epic / Issue docs

- Update:
  - Epic requirement / design / plan lines that mention trusted base-SHA policy.
  - Issue 244 requirement / design / plan to include this added scope and remove the previous target-out statement.
  - Report evidence to record PR #245 review trigger regression and fix verification.

## 受け入れ条件案

- AC-RP-001: `trigger_codex_review.sh` は GitHub contents API で `.github/codex/review-policy.md` を読まない。
- AC-RP-002: script-local `codex-review-instructions.md` が valid な場合、comment body に instruction と metadata が含まれる。
- AC-RP-003: script-local instruction が missing の場合、instruction なしの deterministic `@codex review` comment が投稿される。
- AC-RP-004: script-local instruction が invalid / oversized / unreadable の場合、`human_gate` になり comment は投稿されない。
- AC-RP-005: `.github/codex/review-policy.md` bootstrap asset は provider / dogfooding workspace から削除される。
- AC-RP-006: skill text は script-local instruction を正とし、trusted base-SHA policy を正としない。
- AC-RP-007: PR #245 上で `wait_pr_observation.sh --trigger-mode post-once` が Codex review trigger comment を投稿できる。

## リスクと緩和

- リスク: Team / adversarial repo で PR author が review instruction を弱める可能性。
  - 緩和: この Issue の default は個人 dogfooding repo 向けであることを明記する。Future strict/team mode は別 Issue とする。
- リスク: local file missing でも review が走るため、instruction が適用されていないことに気づきにくい。
  - 緩和: comment metadata と JSON payload に `missing_plain_fallback` を明記する。
- リスク: script-local instruction の installed copy と provider asset が drift する。
  - 緩和: installer / asset parity tests を追加する。
- リスク: `.github/codex/review-policy.md` 削除により過去文書との整合が崩れる。
  - 緩和: ADR を差し替え、Epic / Issue docs を更新する。

## 結論

この Issue では、trusted base-SHA review policy 設計を廃止し、`github-pr-observation` script-local review instruction 設計へ切り替える。

Missing instruction は no-review gate にせず、instruction なしの deterministic `@codex review` fallback を投稿する。Invalid / oversized / unreadable instruction は設定不備として human gate にする。

この修正は PR #245 の dogfooding failure を解消するため、この Issue の追加スコープとして扱う。
