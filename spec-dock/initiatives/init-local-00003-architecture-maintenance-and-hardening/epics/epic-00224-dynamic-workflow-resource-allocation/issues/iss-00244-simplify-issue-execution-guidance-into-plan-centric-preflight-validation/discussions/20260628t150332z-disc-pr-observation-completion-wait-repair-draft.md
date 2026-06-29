---
種別: disc
ID: "20260628t150332z-disc"
タイトル: "PR Observation Completion Wait Repair Draft"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-28"
親: ["iss-00244"]
関連:
  - "PR #245"
  - "20260628t143306z-research-pr-observation-review-completion-signals.md"
  - "github-pr-observation"
  - "wait_pr_observation.sh"
  - "pr_observation_wait.py"
authority: "synthesized"
derived_from:
  - "20260628t143306z-research-pr-observation-review-completion-signals.md"
  - "Oracle session: spec-dock-pr-observatio-completion"
  - "Deep consultant: 019f0eb7-63ee-7a61-b186-32e2422bd5cd"
  - "/private/tmp/spec-dock-iss-00244-pr245-observation-6fc80e8a/result.json"
  - "/private/tmp/spec-dock-pr245-fresh-snapshot-6fc80e8a/result.json"
reflected_to:
  - "../../discussions/20260628t154553z-adr-pr-observation-explicit-review-completion.md"
  - "requirement.md AC-020..AC-023"
  - "design.md 方針 F"
  - "plan.md S300..S399"
  - "report.md D-008 / EAL-009"
---

# 20260628t150332z-disc PR Observation Completion Wait Repair Draft

## 位置づけ

この artifact は、`github-pr-observation` の review completion wait logic を修正するための設計変更ドラフトである。

作成時点では `requirement.md` / `design.md` / `plan.md` へ反映する前の discussion artifact として、現状、理想形、差分、修正案、採用案、作業計画案をまとめた。2026-06-29 時点で採用案は `../../discussions/20260628t154553z-adr-pr-observation-explicit-review-completion.md` へ ADR 昇格済みであり、`requirement.md` AC-020..AC-023、`design.md` 方針 F、`plan.md` S300..S399、`report.md` D-008 / EAL-009 へ反映済みである。

## 背景

PR #245 の dogfooding 中、`wait_pr_observation.sh` / `pr_observation_wait.py` は次の状態で監視を終了した。

- CI: passed
- `completion_signal`: none
- selected review comments: 0
- selected review threads: 0
- `status_reason`: `review_completion_unknown`
- `post_unknown_fresh_audit_required`: true

その後、約 14 分後に Codex が同じ head に対する PR review を投稿し、5 件の P1 review thread が発生した。fresh snapshot では次が確認された。

- `overall_status`: `human_gate`
- `recommended_next_action`: `address_review_feedback`
- `decision.completion_signal`: `submitted_pull_request_review`
- selected review id: `4587513154`
- selected review comment ids:
  - `3487855613`
  - `3487855614`
  - `3487855616`
  - `3487855617`
  - `3487855619`
- current selected unresolved count: 5

これは、time / quiet window / same fingerprint / selected comments 0 を review completion の代替証拠として扱うと、delayed P1 finding を見逃すことを示している。

## 外部分析の要約

### ChatGPT GPT-5.5 Pro Extended

ChatGPT は、`review_completion_unknown` を active terminal-like state から外すべきだと結論した。

推奨案は Option C:

- `review_completion_unknown` terminal path は廃止する。
- `no_completion_evidence` は diagnostics として残す。
- `completion_signal=none` は explicit completion artifact が見えるまで pending / wait として扱う。
- deadline では `timeout` / `wait_or_resume` / `observation_complete=false` を返す。
- quiet window / same fingerprint は completion の代替ではなく、explicit completion artifact が見えた後の hydration stability に限定する。
- `review_completion_unknown` は新規 output contract からは削除し、過去 artifact 互換の legacy vocabulary としてのみ扱う。

### Deep consultant

Deep consultant も同じ方向で、次を指摘した。

- skill contract が `review_completion_unknown` を non-pass terminal-like human gate として正当化している。
- wait 実装は 300 秒 guard と stability により no-completion evidence を completion 代替にしている。
- snapshot 側は `completion_signal=none` を `missing_current_completion_signal` / `wait_or_resume` として表現できているが、wait 側がそれを終端化している。
- tests には missing completion を pending / timeout として扱うものと、`review_completion_unknown` を期待するものが混在している。
- 採用すべき修正は、Option B に近い明示 artifact state machine だが、実装順はまず `review_completion_unknown` 昇格停止から入るのが現実的である。

## 現状

### Skill contract

対象:

- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
- `.agents/skills/github-pr-observation/SKILL.md`

現在の skill は、次のように `review_completion_unknown` を active state として定義している。

- Observation statuses に `review_completion_unknown` が含まれる。
- `review_completion_unknown` は non-pass terminal-like review state とされる。
- CI passed、head matched、current blocker なし、trusted Codex review completion signal なし、trigger-age / CI-passed-age guard 充足で human gate にする。
- stable no-completion evidence は generic timeout に collapse せず、top-level `human_gate` とする。
- `post_unknown_fresh_audit_required` を downstream orchestration に要求する。
- resume metadata は delayed `review_completion_unknown` evaluation を継続できるようにすると書かれている。

この contract は「スクリプト自身が completion artifact まで待つ」のではなく、「completion が不明なまま停止し、後続 fresh audit に委ねる」設計になっている。

### Wait implementation

対象:

- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
- `.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`

主な現状:

- `REVIEW_COMPLETION_UNKNOWN_MIN_TRIGGER_AGE_SECONDS = 300`
- `REVIEW_COMPLETION_UNKNOWN_MIN_CI_PASSED_AGE_SECONDS = 300`
- `mark_decision_review_completion_unknown(payload)` が decision を次へ書き換える。
  - `status="unknown"`
  - `status_reason="review_completion_unknown"`
  - `recommended_next_action="human_gate"`
  - `observation_complete=True`
- `is_review_completion_unknown_candidate(payload)` が no-completion evidence を terminal candidate に変換する。
- `classify()` は `decision_reason == "missing_current_completion_signal"` かつ unknown candidate の場合、`can_complete_when_stable=True` 相当の tuple を返す。
- wait loop は `can_complete_when_stable`、quiet、same fingerprint、unknown latency guard を組み合わせ、`observation_complete=True` にする。
- `observation_complete and review_completion_unknown_candidate` の場合、top-level を `human_gate` にし、`mark_decision_review_completion_unknown()` を呼ぶ。
- wait metadata に `review_completion_unknown_min_*` と `review_completion_unknown_latency_satisfied`、条件付きで `post_unknown_fresh_audit_required` を出す。

### Snapshot implementation

対象:

- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`
- `.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`

snapshot 側はすでに比較的良い分離を持っている。

- `submitted_pull_request_review`
- `codex_no_findings_issue_comment`
- `blocker_policy_no_action`
- `fallback_issue_comment`
- `none`

`completion_signal == "none"` の場合、decision は概ね次を返す。

- `status_reason="missing_current_completion_signal"`
- `recommended_next_action="wait_or_resume"`
- `no_completion_evidence`

つまり、危険な終端化は主に wait 側で起きている。

### Tests

対象:

- `tests/unit/infra/test_init_update.py`

現状の tests には、新方針に近いものと旧方針を固定しているものが混在する。

更新対象の例:

- `test_issue_219_s01_wait_carryover_only_missing_completion_reaches_unknown_after_latency`
- `test_issue_187_s420_wait_stable_no_completion_remains_possible_with_empty_inventory`
- `test_issue_187_s430_short_timeout_still_attempts_confirmation_poll`
- `test_issue_187_s430_ci_passed_age_below_300_does_not_promote_unknown`
- `test_issue_187_s430_post_unknown_fresh_audit_metadata_is_emitted`

これらは、stable no-completion が `review_completion_unknown` / `human_gate` へ昇格することを期待しているため、timeout / wait-or-resume 期待へ反転する必要がある。

## 理想形

### 基本原則

レビュー完了は、current trigger boundary と expected head SHA に bind された Codex-authored artifact でのみ判断する。

次は completion proof ではない。

- trigger comment が存在する。
- Codex が reaction した。
- CI が passed になった。
- selected current comments / threads が 0 件である。
- quiet window が満たされた。
- same fingerprint が満たされた。
- old trigger / old head の review artifact が存在する。

### Findings completion

trusted findings completion は次である。

- Codex-authored submitted PR review object が存在する。
- current trigger より後に作成 / submitted されている。
- expected head SHA に bind されている。
- API 上の `commit_id` / GraphQL `commit.oid` が expected full head SHA に一致することを最優先にする。
- body の `Reviewed commit` prefix は補助 evidence とする。
- review comments / review threads / body は hydration barrier 後に inventory として確定する。

### No-findings completion

trusted no-findings completion は次である。

- Codex-authored issue comment が存在する。
- current trigger 後に作成されている。
- strict no-findings wording に一致する。
- `Reviewed commit` prefix が expected head SHA と一致する。
- pending Codex review evidence、same-boundary blocker、selected unresolved、changes-requested、blocking limitations がない。
- CI / PR metadata / head freshness / draft / open state / carryover unresolved を統合した後でのみ top-level `passed` / `merge_prepared` にできる。

### Pending / wait

次は monitoring 継続である。

- `completion_signal == "none"`
- `decision.status_reason == "missing_current_completion_signal"`
- Codex output がまだない。
- current review object / comments / thread state が partial visibility。
- current completion がないが carryover unresolved がある。
- old trigger / old head の artifact しかない。

### Timeout / resume

overall deadline まで explicit completion artifact がない場合:

- `normalized_status="timeout"`
- `overall_status="timeout"`
- `recommended_next_action="wait_or_resume"`
- `observation_complete=false`
- same-boundary resume metadata を返す。

timeout は no-review-work proof ではない。単に「この wait window では completion artifact を得られなかった」という retryable outcome である。

### Hydration barrier

quiet window / same fingerprint は、explicit completion artifact が見えた後の hydration stability にのみ使う。

例:

- PR review object が見えたが review comments / thread state がまだ不完全。
- review comments が見えたが PR review object がまだ見えない。
- strict no-findings comment が見えたが、same-boundary blocker が遅れて見える可能性がある。

この場合、completion の代替ではなく、artifact inventory を揃えるために短く待つ。

## 差分

| 観点 | 現在 | 理想 |
|---|---|---|
| no completion evidence | time / quiet / fingerprint で `review_completion_unknown` へ昇格 | pending / wait。deadline で timeout / resume |
| `review_completion_unknown` | active terminal-like human gate | 新規 output から廃止。legacy vocabulary のみ |
| `observation_complete` | completion signal なしでも true になり得る | explicit completion または hard terminal failure 以外では false |
| quiet / same fingerprint | no-completion を終端化する材料 | explicit artifact 後の hydration 補助 |
| post-unknown audit | wait 側が停止し downstream fresh audit に委ねる | wait 側が completion artifact または timeout まで責任を持つ |
| delayed review | 見逃し得る | timeout window 内なら拾う。window 外なら retryable resume |

## 修正案

### Option A: 最小修正

内容:

- `review_completion_unknown` 昇格だけを止める。
- `classify()` の `missing_current_completion_signal` は常に `pending` / `wait_or_resume` / `can_complete_when_stable=False` とする。
- `mark_decision_review_completion_unknown()` 呼び出しを止める。
- `post_unknown_fresh_audit_required` を出さない。
- deadline では `timeout` / `wait_or_resume` とする。

メリット:

- PR #245 型の delayed P1 見逃しを最短で止められる。
- 実装コストが低い。

リスク:

- hydration / head binding の弱さは残る。
- state machine の整理が不十分で、将来の仕様理解が難しいまま残る。

### Option B: full state-machine refactor

内容:

- wait lifecycle を明示状態へ再設計する。
  - `WAITING_FOR_CODEX_OUTPUT`
  - `FINDINGS_COMPLETION_VISIBLE`
  - `NO_FINDINGS_COMPLETION_VISIBLE`
  - `HYDRATING_REVIEW_OUTPUT`
  - `COMPLETED_HYDRATED`
  - `TIMEOUT_RETRYABLE`
- partial visibility / hydration / terminal action を整理する。
- snapshot 側の head binding も full SHA exact match を強化する。

メリット:

- 長期的に最も明快。
- completion / hydration / timeout の責務境界が明確。

リスク:

- 実装範囲が広い。
- 現在の PR repair scope としては手戻りが大きく、既存 tests への影響が大きい。

### Option C: hybrid

内容:

- Option A の直接修正を必ず実施する。
- ただし docs / tests / metadata では明示 artifact model と hydration 専用の quiet/fingerprint を固定する。
- `review_completion_unknown` は active output から外し、legacy vocabulary としてのみ残す。
- snapshot 側の completion taxonomy は大きく壊さず、必要な head-binding / partial visibility test を追加する。
- full state-machine refactor は将来拡張可能な形にとどめる。

メリット:

- PR #245 の実害を確実に止める。
- 実装範囲が現実的。
- canonical docs に反映しやすい。
- 将来の state-machine refactor への道筋も残る。

リスク:

- Option B ほど完全な構造整理ではない。
- `no_completion_evidence` や legacy unknown wording の残し方を慎重に定義する必要がある。

### Option D: latency guard 延長

内容:

- 300 秒 guard を 30 分などに伸ばす。

メリット:

- 変更が最小。

リスク:

- completion の代替証拠という設計誤りは残る。
- worker latency が guard を超えれば同じ失敗が再発する。
- 不採用。

### Option E: post-unknown fresh audit 強制

内容:

- 既存 `review_completion_unknown` を維持し、downstream に必ず fresh audit をさせる。

メリット:

- 現行 contract に近い。

リスク:

- 親エージェントや merge-preparer が fresh audit を忘れると再発する。
- wait script 自体が責任を持って待ち切らない。
- 今回の失敗そのものを workflow discipline で覆い隠すだけなので不採用。

## 採用案

採用案は Option C とする。

理由:

- PR #245 の根本原因である `review_completion_unknown` terminal path を確実に除去できる。
- full state-machine refactor ほど大きな差分にせず、現在の issue / PR repair scope に収められる。
- `pr_review_snapshot.py` の既存 completion taxonomy を活かせる。
- false timeout / resume を許容し、delayed P1 findings 見逃し不可という制約に最も合う。
- skill contract と tests を同時に修正でき、agent が再び `review_completion_unknown` を merge-prepared の代替にしないよう固定できる。

## 設計変更ドラフト

### Public contract

- `review_completion_unknown` は active observation status ではない。
- 新規 `wait_pr_observation.sh` result は `review_completion_unknown` を出さない。
- 過去 artifact に `review_completion_unknown` が含まれる可能性は legacy として扱う。
- legacy `review_completion_unknown` を受け取った downstream は、no-review-work proof として扱ってはならない。
- no-completion by deadline は `timeout` / `wait_or_resume` / `observation_complete=false`。
- `timeout` は review absence proof ではない。
- `selected_unresolved_count == 0` は no-review-work proof ではない。

### Wait semantics

- `completion_signal=none` は常に monitoring continuation または retryable timeout。
- `missing_current_completion_signal` は terminal reason ではない。
- `can_complete_when_stable=True` は explicit completion artifact がある場合に限定する。
- quiet / same fingerprint は hydration stability のみに使う。
- CI passed は review completion proof ではない。
- carryover unresolved は current completion proof ではない。

### Completion semantics

trusted completion signal:

- `submitted_pull_request_review`
- `codex_no_findings_issue_comment`
- 必要に応じて `blocker_policy_no_action`

completion として扱わないもの:

- `fallback_issue_comment`
- `none`
- current trigger 前の artifact
- wrong head artifact
- generic Codex issue comment
- reaction only

### Timeout semantics

- overall deadline 到達時に explicit completion artifact がない場合、`mark_decision_timeout()` に寄せる。
- timeout result は resume metadata を持つ。
- same-boundary resume は新しい trigger を投稿しない。

## 作業計画ドラフト

### S300 PR observation completion wait contract update

Pattern: `CodePlusSpec`

目的:

- skill contract と runtime wait contract を、explicit completion artifact model に変更する。

変更対象:

- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
- `.agents/skills/github-pr-observation/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
- `.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`

作業:

- Observation statuses から active `review_completion_unknown` を削除する。
- `review_completion_unknown` terminal-like human gate の説明を削除する。
- `post_unknown_fresh_audit_required` contract を削除する。
- `completion_signal=none` は timeout / resume まで wait する contract にする。
- `classify()` の `missing_current_completion_signal` branch を non-completable pending にする。
- `mark_decision_review_completion_unknown()` の呼び出しを削除する。
- `REVIEW_COMPLETION_UNKNOWN_MIN_*` を active logic から削除する。
- wait metadata から `review_completion_unknown_*` を削除、または legacy/debug-only に降格する。

### S310 PR observation wait regression tests

Pattern: `CodeReview`

変更対象:

- `tests/unit/infra/test_init_update.py`

作業:

- stable no-completion が `review_completion_unknown` になる既存期待を反転する。
- timeout / wait_or_resume / observation_complete=false を期待する。
- delayed review regression を追加する。
- missing completion timeout を追加または既存 test を更新する。
- post-unknown fresh audit metadata test を削除または「出ない」期待に変更する。
- age guard tests を削除または「age に依存せず unknown へ昇格しない」期待に変更する。

必須テスト観点:

- CI passed + completion none + stable fingerprint が続いても terminal にならない。
- その後 submitted PR review が出たら `human_gate` / `address_review_feedback` になる。
- deadline まで completion none なら `timeout` / `wait_or_resume`。
- submitted review あり + unresolved threads ありなら `human_gate`。
- strict no-findings は integrated gates 通過後のみ `passed`。
- carryover unresolved は merge-prepared を blocker するが、current completion proof ではない。
- stale head / wrong trigger artifact は current completion としない。

### S320 Hydration and head-binding hardening

Pattern: `StrictGate`

変更対象:

- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`
- `.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`
- `tests/unit/infra/test_init_update.py`

作業:

- completion 用 head-binding helper を明示する。
- PR review object は full SHA exact match を優先する。
- review comments は `original_commit_id` を current selection の主要根拠にする。
- body `Reviewed commit` prefix は fallback evidence とし、decisive に使う場合は limitation / weaker confidence とする。
- partial visibility の代表ケースを tests で固定する。

注意:

- ここは Option C の中でもリスクが少し高いため、S300/S310 で delayed P1 見逃しを先に止める。
- full state-machine refactor までは行わない。

### S330 Dogfooding / manual validation

Pattern: `StrictGate`

作業:

- 旧 result `/private/tmp/spec-dock-iss-00244-pr245-observation-6fc80e8a/result.json` を bad artifact として report に記録する。
- fresh snapshot `/private/tmp/spec-dock-pr245-fresh-snapshot-6fc80e8a/result.json` を expected current finding artifact として記録する。
- 修正後、同 PR/head/trigger boundary で `--trigger-mode resume` を試す。
- 期待:
  - 既に submitted PR review が存在するため、`human_gate` / `address_review_feedback` / `submitted_pull_request_review` になる。
  - `review_completion_unknown` に戻らない。
- fake gh / unit test で delayed review regression を確認する。

### S399 Final gate

Pattern: `StrictGate`

必須検証:

- `uv run pytest tests/unit/infra/test_init_update.py`
- focused grep:
  - active skill contract に `review_completion_unknown` terminal-like human gate 記述が残っていない。
  - wait output contract が `timeout` / `wait_or_resume` を明示している。
  - forbidden CI surfaces (`gh pr checks`, status rollup, commit statuses, Checks API) を追加していない。
- `./spec-dock/scripts/spec-dock validate`
- PR #245 live observation または saved/fake snapshots による manual validation。

## Requirement 反映案

追加する AC:

- AC-020: Review completion is explicit artifact based
  - `wait_pr_observation.sh` は `completion_signal=none` を time / quiet / fingerprint で review completion とみなさない。
  - trusted completion は current trigger boundary と expected head SHA に bind された Codex-authored submitted PR review または strict no-findings issue comment のみである。

- AC-021: Missing completion times out retryably
  - overall deadline まで trusted completion artifact がない場合、result は `timeout` / `wait_or_resume` / `observation_complete=false` になる。
  - `review_completion_unknown` を active terminal status として返さない。

- AC-022: Hydration only follows explicit completion
  - quiet window / same fingerprint は explicit completion artifact が見えた後の hydration stability にのみ使う。
  - no-completion evidence を completion に昇格しない。

- AC-023: PR #245 delayed review regression is covered
  - CI passed + no completion + stable fingerprint の後に Codex submitted review が遅れて出る fake snapshot sequence で、wait loop が早期終了せず review feedback を拾う。

## Design 反映案

設計書に追加する内容:

- `Review Completion State Machine` セクション。
- `Trusted Completion Signals` セクション。
- `Timeout / Resume Semantics` セクション。
- `Hydration Barrier` セクション。
- `Legacy review_completion_unknown` セクション。

状態機械:

```text
TRIGGER_BOUNDARY_READY
  -> WAITING_FOR_CI_AND_CODEX_OUTPUT

WAITING_FOR_CI_AND_CODEX_OUTPUT
  -> CI_FAILED
  -> STALE_HEAD
  -> CODEX_REVIEW_VISIBLE
  -> CODEX_NO_FINDINGS_VISIBLE
  -> AMBIGUOUS_CODEX_OUTPUT
  -> TIMEOUT_RETRYABLE

CODEX_REVIEW_VISIBLE
  -> HYDRATING_REVIEW_OUTPUT
  -> COMPLETED_WITH_ACTIONABLE
  -> COMPLETED_NO_ACTIONABLE

CODEX_NO_FINDINGS_VISIBLE
  -> HYDRATING_REVIEW_OUTPUT
  -> COMPLETED_NO_ACTIONABLE

TIMEOUT_RETRYABLE
  -> wait_or_resume
```

## Plan 反映案

実装計画書末尾に追加する step:

- S300 PR observation completion wait contract update
- S310 PR observation wait regression tests
- S320 Hydration and head-binding hardening
- S330 Dogfooding / manual validation
- S399 Final gate

既存 S200-S299 までの実施済み step は残し、末尾に追加する。

## 採用しない案

- 300 秒 guard を延長する案:
  - worker latency が guard を超えると再発する。
  - completion の代替証拠という設計誤りを温存する。
- post-unknown fresh audit 強制案:
  - downstream agent が audit を忘れると再発する。
  - wait script 自体が安全に待ち切らない。
- full state-machine refactor をこの PR repair で一気に行う案:
  - 長期的には魅力的だが、現在の issue / PR repair としては差分が大きすぎる。

## 未検証事項

- Codex no-findings comment wording が将来も固定か。
- no-findings が reaction-only になる設定 / バージョンが存在するか。
- Codex setup / permission / unable-to-review error comment の exact artifact shape。
- GitHub API の partial visibility 順序の全パターン。

ただし、これらが未検証でも、今回の採用案は保守的に false timeout / resume へ倒すため、delayed P1 finding を見逃すより安全である。

## 結論

この issue では Option C を採用する。

実装の中心は、`review_completion_unknown` を active terminal-like state から外し、`completion_signal=none` を pending / wait または retryable timeout にすることである。

そのうえで、skill contract と tests に「completion は explicit Codex artifact のみ」「quiet / fingerprint は hydration 専用」「timeout は no-review-work proof ではない」を固定する。
