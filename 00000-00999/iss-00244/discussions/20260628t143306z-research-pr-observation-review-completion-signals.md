---
種別: research
ID: "20260628t143306z-research"
タイトル: "PR Observation Review Completion Signals"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-28"
親: ["iss-00244"]
関連: ["PR #245", "github-pr-observation", "wait_pr_observation.sh", "pr_observation_wait.py"]
authority: "synthesized"
derived_from:
  - ".agents/skills/github-pr-observation/SKILL.md"
  - "src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py"
  - "src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py"
  - "/private/tmp/spec-dock-iss-00244-pr245-observation-6fc80e8a/result.json"
  - "/private/tmp/spec-dock-pr245-fresh-snapshot-6fc80e8a/result.json"
  - "Oracle session: spec-dock-pr-observatio-review"
  - "Oracle session: spec-dock-pr-observatio-review-2"
  - "Oracle session: spec-dock-codex-review-completion"
  - "OpenAI Developers: Code review in GitHub"
reflected_to:
  - "../../discussions/20260628t154553z-adr-pr-observation-explicit-review-completion.md"
  - "requirement.md AC-020..AC-023"
  - "design.md 方針 F"
  - "plan.md S300..S399"
  - "report.md D-008 / EAL-009"
---

# 20260628t143306z-research PR Observation Review Completion Signals

## 調査目的

PR #245 の dogfooding で、`wait_pr_observation.sh` が `review_completion_unknown` を terminal-like な `human_gate` として返した後、約 14 分後に Codex review が投稿され、5 件の P1 review thread が発生した。

この artifact は、GitHub / Codex review の観測状態を整理し、`github-pr-observation` の wait loop が何を「レビュー完了シグナル」とみなすべきか、何を「監視継続」とみなすべきか、何を `timeout` / `wait_or_resume` として扱うべきかを明確にする。

## sources / 調査方法

参照先:

- `/.agents/skills/github-pr-observation/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh`
- `/private/tmp/spec-dock-iss-00244-pr245-observation-6fc80e8a/result.json`
- `/private/tmp/spec-dock-pr245-fresh-snapshot-6fc80e8a/result.json`
- Oracle / ChatGPT GPT-5.5 Pro Extended sessions:
  - `spec-dock-pr-observatio-review`
  - `spec-dock-pr-observatio-review-2`
  - `spec-dock-codex-review-completion`
- OpenAI Developers: `https://developers.openai.com/codex/integrations/github`

検証手順:

- PR #245 の latest head `6fc80e8aa1df5a46570179933d3e0e1b0db0ff44` に対して fresh snapshot を取得した。
- 旧 wait 結果と fresh snapshot を比較し、レビュー投稿前後の `completion_signal`、selected review、selected comments、selected threads、status reason を確認した。
- Oracle に 3 回相談し、初回は time-based completion の危険性、2 回目は実装最小差分、3 回目はユーザー補足を織り込んだ GitHub / Codex artifact 状態別の完了シグナルを分析した。
- OpenAI 公式 docs で `@codex review` の高レベル挙動を確認した。

## facts / 観測できた事実

### 公式 docs で確認できること

- OpenAI Developers の Codex GitHub review docs は、PR comment で `@codex review` を mention すると Codex が反応し、GitHub の通常 review として投稿する、という高レベル動作を説明している。
- 同 docs は、GitHub 上の Codex review は P0 / P1 の重大な issue に集中する、という意図を説明している。
- 同 docs は、GitHub API 上でどの object / field を review completion signal とすべきかまでは定義していない。

### PR #245 で観測したこと

- latest head: `6fc80e8aa1df5a46570179933d3e0e1b0db0ff44`
- 旧 wait 結果:
  - CI: passed
  - `completion_signal`: none
  - selected review comments: 0
  - selected review threads: 0
  - `status_reason`: `review_completion_unknown`
  - `post_unknown_fresh_audit_required`: true
- その後、Codex review が投稿された。
- fresh snapshot:
  - `overall_status`: `human_gate`
  - `recommended_next_action`: `address_review_feedback`
  - `observation_complete`: true
  - `decision.completion_signal`: `submitted_pull_request_review`
  - selected review id: `4587513154`
  - selected review comment ids:
    - `3487855613`
    - `3487855614`
    - `3487855616`
    - `3487855617`
    - `3487855619`
  - current selected unresolved count: 5
  - carryover unresolved count: 9
- Codex review object:
  - author: `chatgpt-codex-connector[bot]`
  - state: `commented`
  - commit_id: `6fc80e8aa1df5a46570179933d3e0e1b0db0ff44`
  - submitted_at: `2026-06-28T12:19:38Z`
  - body includes `Codex Review` and `Reviewed commit: 6fc80e8aa1`
- 5 件の current selected review comments はすべて:
  - author: `chatgpt-codex-connector[bot]`
  - `commit_id` / `original_commit_id`: `6fc80e8aa1df5a46570179933d3e0e1b0db0ff44`
  - `thread_state`: `unresolved`
  - created_at: `2026-06-28T12:19:38Z`

### 5 件の current selected P1 findings

| ID | Thread | File | Line | Finding |
|---|---|---|---:|---|
| `3487855613` | `PRRT_kwDOQ99OK86MzDvy` | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py` | 130 | strict-legacy missing-assurance path が plan readiness を bypass し得る |
| `3487855614` | `PRRT_kwDOQ99OK86MzDvz` | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py` | 210 | negated text 内の `implementation step` substring で execution-ready になり得る |
| `3487855616` | `PRRT_kwDOQ99OK86MzDv1` | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py` | 1257 | `draft-design` / `draft-plan` の frontmatter closing marker が壊れ得る |
| `3487855617` | `PRRT_kwDOQ99OK86MzDv2` | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/assurance_store.py` | 99 | symlinked `requirement.md` が source-binding 前に読まれ得る |
| `3487855619` | `PRRT_kwDOQ99OK86MzDv4` | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/assurance.py` | 137 | non-empty `obligations.notes` が rewrite で失われ得る |

## inference / 推測

### 結論

`review_completion_unknown` を terminal completion として扱う設計は廃止するべきである。

レビュー完了は、時間経過、quiet window、same fingerprint、CI passed、selected comments = 0 では判断できない。これらは「GitHub の観測値がしばらく静かだった」ことを示すだけで、非同期の Codex review worker が完了した証拠ではない。

### レビュー完了として信頼できるシグナル

信頼できる completion signal は、current trigger boundary と expected head SHA に bind された Codex-authored artifact に限定する。

1. Findings completion:
   - Codex-authored submitted PR review object が存在する。
   - author は Codex actor allowlist に含まれる。
   - review は current trigger の後に作成 / submitted されている。
   - API 上の `commit_id` / GraphQL `commit.oid` が expected full head SHA に一致する。
   - body に Codex review marker と `Reviewed commit` がある場合は補助 evidence として扱う。
   - review comments / review threads は hydration barrier 後に収集する。

2. No-findings completion:
   - Codex-authored issue comment が存在する。
   - current trigger 後に作成されている。
   - no-findings wording が strict allowlist に一致する。
   - `Reviewed commit` の prefix が expected head SHA と一致する。
   - same-boundary PR review / review comments / pending partial evidence がない。
   - CI / PR metadata / head freshness / unresolved current and carryover threads / changes-requested / blocking limitations を統合した後でのみ `passed` / `merge_prepared` にできる。

3. Explicit failure / limitation:
   - Codex が error / setup / permission / unable-to-review などの明示コメントを返す場合は、completion ではなく `human_gate` または `unknown` の terminal evidence として分類する余地がある。
   - PR #245 の観測だけでは、この種別の exact wording / artifact shape は未確認である。

### 完了として扱ってはいけないシグナル

- trigger comment が存在する。
- Codex が reaction した。
- CI が passed になった。
- `quiet_seconds` が満たされた。
- `same_fingerprint_count` が満たされた。
- selected current comments / threads が 0 件である。
- old trigger / old head に対する review または no-findings comment が存在する。
- latest PR head と artifact の head binding が不一致である。

### hydration barrier の必要性

GitHub API では、PR review object、review comments、review thread state、issue comments が完全に同時に見える保証はない。したがって、明示的な completion artifact を見つけた直後に即 final にするのではなく、短い hydration / stability barrier を置くべきである。

hydration barrier は completion の代替ではない。あくまで「明示 artifact が見えた後に、関連する comments / thread state / body が揃うのを待つ」ためのものとして使う。

## 状態別の判断表

| 状態 | GitHub observable evidence | 監視判断 | terminal status | next action |
|---|---|---|---|---|
| Review has findings | current trigger 後の Codex-authored submitted PR review が expected head に bind され、review comments / threads が見える | hydration 後に終了 | unresolved があれば `human_gate` | `address_review_feedback` |
| Review has no findings | current trigger 後の strict no-findings issue comment が expected head に bind され、same-boundary blocker がない | hydration 後に終了 | integrated gates が全て pass なら `passed` | `merge_prepared` |
| Review not completed yet | trigger はあるが Codex review / no-findings / explicit failure artifact がない | 継続 | deadline 到達時だけ `timeout` | `wait_or_resume` |
| Partial visibility | review object のみ、review comments のみ、thread state 欠落、body missing / truncated など | hydration 継続 | deadline で `timeout`、actionable body がある場合のみ `human_gate` | `wait_or_resume` または `address_review_feedback` |
| Stale artifact | artifact が trigger 前、または old head に bind されている | current completion として無視 | head 自体が変わった場合は `stale_head` | `rerun_for_current_head` |
| Ambiguous Codex output | Codex-authored issue comment だが no-findings allowlist でも review object でもない | merge-ready にはしない | `human_gate` | `manual_review_required_non_retryable` |
| CI failed | Actions CI failure | review 完了待ちとは独立して terminal | `failed` | `fix_ci` |
| GitHub read limitation | PR review/comment/thread read が権限や schema で不完全 | 安全に判断できない | `unknown` または `human_gate` | `fix_github_token_permissions` など |

## 状態機械案

```text
TRIGGER_POSTED_OR_RESUMED
  -> WAITING_FOR_CODEX_OUTPUT

WAITING_FOR_CODEX_OUTPUT
  -> FINDINGS_COMPLETION_VISIBLE
       when current-boundary submitted Codex PR review is observed
  -> NO_FINDINGS_COMPLETION_VISIBLE
       when strict current-boundary no-findings issue comment is observed
  -> AMBIGUOUS_CODEX_OUTPUT
       when Codex output exists but cannot be classified safely
  -> TIMEOUT_RETRYABLE
       when overall deadline expires without explicit completion artifact

FINDINGS_COMPLETION_VISIBLE
  -> HYDRATING_REVIEW_OUTPUT
  -> COMPLETED_HYDRATED

NO_FINDINGS_COMPLETION_VISIBLE
  -> HYDRATING_REVIEW_OUTPUT
  -> COMPLETED_HYDRATED

HYDRATING_REVIEW_OUTPUT
  -> COMPLETED_HYDRATED
       when selected review/comment/thread/body set stabilizes
  -> PARTIAL_VISIBILITY_TIMEOUT
       when deadline expires before hydration completes

COMPLETED_HYDRATED
  -> human_gate / address_review_feedback
       when current or carryover actionable unresolved feedback exists
  -> passed / merge_prepared
       when no-findings or no blockers and all integrated gates pass
```

## Head / boundary matching rules

優先順位:

1. PR head:
   - current PR `headRefOid` must equal expected full head SHA.
   - 不一致なら `stale_head`。
2. Trigger boundary:
   - deterministic trigger body の `reviewed_head_sha` must equal expected full head SHA。
   - `trigger_comment_id` と `trigger_created_at` を current boundary とする。
   - artifact の `created_at` / `submitted_at` が trigger 以前なら current completion として除外する。
3. PR review object:
   - API `commit_id` / GraphQL `commit.oid` must equal expected full head SHA。
   - body の `Reviewed commit` prefix は補助 evidence。API full SHA より弱い。
4. Review comments:
   - `original_commit_id` must equal expected full head SHA。
   - `commit_id` だけでは古い comment が current head に見えることがあるため、current selection の主根拠にしない。
5. Body commit prefix:
   - `Reviewed commit: <prefix>` は `expected_head_sha.startswith(prefix)` を満たす場合のみ fallback evidence として使う。
   - prefix-only binding を decisive に使う場合は limitation を残す。

## 実装への含意

### 最小修正方針

- `review_completion_unknown` を normal wait loop の terminal completion / terminal-like `human_gate` として使わない。
- no-completion evidence は diagnostics として残してよいが、deadline 前は `pending` / `wait_or_resume` として監視を継続する。
- deadline 到達時に explicit completion artifact がなければ、`timeout`、`observation_complete=false`、`recommended_next_action=wait_or_resume` を返す。
- `review_completion_unknown_latency_satisfied` のような time-based terminal reason は削除または non-terminal diagnostics へ降格する。
- quiet window / same fingerprint は、explicit completion artifact が見えた後の hydration 判定に限定する。
- skill 文面から `review_completion_unknown` を human gate として downstream fresh audit に委ねる記述を削除し、wait loop 自体が completion artifact または timeout まで待つ contract に更新する。

### 追加すべき test

- delayed review regression:
  - CI passed、trigger age guard satisfied、quiet window satisfied、same fingerprint satisfied、selected comments 0 の snapshot が続いても terminal にしない。
  - 後続 snapshot で submitted PR review が出たら `human_gate` / `address_review_feedback` になる。
- missing completion timeout:
  - overall timeout まで explicit completion signal がない場合、`timeout` / `wait_or_resume` / resume metadata を返す。
- findings completion:
  - submitted PR review + review comments + unresolved threads を current selected として選び、`human_gate` / `address_review_feedback` を返す。
- no-findings completion:
  - strict no-findings issue comment + matching head + no blockers + CI passed のときのみ `passed` / `merge_prepared`。
  - no-findings が trigger 前、wrong head、generic wording、same-boundary pending review evidence ありの場合は pass にしない。
- partial visibility:
  - comments before review object、review object before comments、thread state missing、body missing / truncated を hydrating / timeout / partial human gate として扱う。
- stale / boundary:
  - artifact が old trigger / old head / `created_at == trigger_created_at` の場合は current completion として除外する。
- carryover unresolved:
  - current no-findings completion があっても non-outdated carryover unresolved threads があれば `merge_prepared` にしない。

## unverified / 未検証事項

- Codex no-findings の exact wording が将来も `Codex Review: Didn't find any major issues. Keep it up!` で固定されるか。
- no-findings 時に必ず issue comment が投稿されるか、それとも reaction のみで完了する設定 / バージョンがあるか。
- Codex actor 名が `chatgpt-codex-connector[bot]` から変わる可能性。
- Codex が review 不能 / permission / setup error を返す場合の exact artifact shape。
- GitHub API 上で PR review object、review comments、GraphQL thread state が見える順序の全パターン。
- OpenAI docs は高レベル挙動を説明するが、API-level completion contract は明示していないため、実装では PR #245 の観測と保守的な fail-closed / wait-or-resume 方針を採用する。

## question candidates / 質問候補

source-grounded に解けず、人間判断が必要な候補:

- total timeout の標準値をどれくらいにするか。
  - ただし設計方針としては「timeout は completion の代替ではなく、resume を促す retryable outcome」で確定できる。
- no-findings が reaction-only の場合を completion として扱うか。
  - 現時点では扱わない方が安全。Codex-authored issue comment または submitted review のどちらかを completion artifact とする。

pressure-test question として切り出すべき候補:

- `@codex review` 後に Codex が thumbs-up reaction のみを返す実環境があるか。
- no-findings comment の body pattern は repo / organization / model version で変わるか。
- Codex error / setup limitation comment は current scripts の fixed read surfaces で検出できるか。

質問せずに解決できた候補:

- quiet window / same fingerprint を completion 判定に使うべきか。
  - 使うべきではない。hydration 補助に限定する。
- `review_completion_unknown` を `human_gate` として terminal に残すべきか。
  - 残すべきではない。PR #245 の実害により不適切と判断できる。

## terminology conflicts / 用語衝突

- `review_completion_unknown`
  - 旧 skill 文面では non-pass terminal-like human gate とされていた。
  - 実態としては「レビュー完了が確認できない」状態であり、terminal にすると delayed P1 findings を見逃す。
  - 新 contract では `no_completion_evidence` diagnostics または timeout reason へ降格する。
- `quiet`
  - 旧 wait loop では terminal unknown の条件に使われていた。
  - 新 contract では explicit completion artifact 後の hydration stability にだけ使う。
- `observation_complete`
  - 旧 unknown path では completion signal なしでも final result として扱われ得た。
  - 新 contract では review completion がない deadline 到達時は `observation_complete=false` とし、resume を促す。

## edge cases / 具体シナリオ

- CI passed 後 90 秒 quiet:
  - PR #245 で実害が出た。レビュー完了の根拠ではない。
- submitted PR review が先に見え、comments / threads が後から見える:
  - completion artifact は見えたが inventory が未hydrated。短い hydration barrier が必要。
- review comments が先に見え、review object が後から見える:
  - blocker evidence として merge-ready は不可。ただし completion と断定せず hydration 継続。
- strict no-findings comment の直後に comments が遅れて見える:
  - no-findings completion でも hydration barrier を置き、same-boundary blocker がないことを確認する。
- old review comments の `commit_id` が current head に見える:
  - `original_commit_id` と trigger boundary を使わないと stale comment を current と誤認する。
- carryover unresolved がある:
  - current review が no-findings でも top-level merge-prepared にはしない。

## implications / 判断への含意

- この Issue の追加修正対象に `pr_observation_wait.py` の wait state machine 修正を含めるべきである。
- `github-pr-observation/SKILL.md` の Observation Semantics は、`review_completion_unknown` を terminal human gate とする記述から、explicit completion artifact または retryable timeout を待つ contract へ更新する必要がある。
- PR #245 の 5 件の P1 finding 修正とは別に、PR observation 自体の監視終了条件修正も同一 Issue の dogfooding failure repair として扱うのが妥当である。
- `github-pr-merge-preparer` は、`timeout` / `wait_or_resume` を「レビューなし」や「merge-ready」へ変換してはならない。

## リスク/制約

- 待機時間が長くなる可能性がある。ただし delayed P1 finding を見逃すリスクより小さい。
- no-findings comment の wording が変わると false timeout が増える可能性がある。allowlist は実観測に基づいて保守する。
- API hydration の全順序は未確認であるため、実装は partial visibility を pass にしない方向で保守的に設計する。

## 反映先

- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
- `.agents/skills/github-pr-observation/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
- `.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
- `tests/unit/infra/test_init_update.py`
- `spec-dock/active/issue/requirement.md`
- `spec-dock/active/issue/design.md`
- `spec-dock/active/issue/plan.md`

## 参考（References）

- OpenAI Developers, Code review in GitHub: `https://developers.openai.com/codex/integrations/github`
- Oracle session transcript: `/Users/iwasawayuuta/.oracle/sessions/spec-dock-codex-review-completion/artifacts/transcript.md`
