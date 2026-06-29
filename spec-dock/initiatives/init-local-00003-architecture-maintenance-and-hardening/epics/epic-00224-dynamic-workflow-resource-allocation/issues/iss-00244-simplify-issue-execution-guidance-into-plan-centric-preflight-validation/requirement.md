---
種別: 要件定義書（Issue）
ID: "iss-00244"
タイトル: "Simplify Issue Execution Guidance Into Plan Centric Preflight Validation"
関連GitHub: ["#244"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-29"
親: ["epic-00224", "init-local-00003"]
---

# iss-00244 Simplify Issue Execution Guidance Into Plan Centric Preflight Validation — 要件定義（何を、なぜ行うか）

## 目的

`guidance issue-execution` を、実行時に次 step / worker / reviewer / context を動的に選ぶ仕組みから、承認済み `plan.md` を実行してよいか確認する preflight / consistency validator へ単純化する。

これにより、agent が `plan.md`、skill、runtime guidance、`report.md`、generated projection の複数 authority を同時に追う状態を解消し、実装時の判断と品質ゲートを `plan.md` に一本化する。

## 背景・現状

- Epic 初期設計では、runtime が current step、worker、reasoning effort、context policy、verification、reviewer を compile し、`guidance issue-execution` に返す方向だった。
- Dogfooding 中、`report.md` に S01-S99 の完了証跡があるにもかかわらず、`guidance issue-execution` が `selected_step: S01` を返し続ける問題が発生した。
- 直接原因は report parser が一部 ledger 形式を読めないことだったが、追加分析では、`report.md` を実行制御 state として parse する model 自体が不安定であると判断した。
- `spec-dock/docs/phase_plan_issue.md` と `spec-dock/docs/authoring/issue-plan.md` は、すでに `plan.md` を planned executable workflow contract / command queue、`report.md` を observed evidence ledger と位置づけている。
- 現行 runtime / tests / skill 文面には、まだ `selected_step`、`step_assurance`、`context_packets`、runtime worker/reviewer/verification inference が残っている。
- ユーザー回答により、この Issue では `hard cutover` を採用する。不要な interface / field は互換期間なしで削除する。
- PR #245 の dogfooding 中、GitHub Codex review trigger が base branch 上の `.github/codex/review-policy.md` だけを読みに行き、base 側に policy がないため `human_gate` となり、`@codex review` comment が投稿されない問題が確認された。
- 追加分析と ADR 差し替えにより、trusted base-SHA review policy はこの個人開発 / dogfooding repo の運用に合わないと判断した。Review instruction は GitHub base branch ではなく、`github-pr-observation` の comment posting script 近傍に置く script-local Markdown から読む。
- Script-local instruction が missing の場合は review 自体を止めず、instruction なしの deterministic `@codex review` comment を投稿する。Present だが invalid / oversized / unreadable の場合は設定不備として human gate にする。
- `assurance.json` は Issue の quality profile / source binding / stale detection を保持する machine-readable contract であり、agent が直接編集・読解する一次文書ではない。`requirement.md` / `design.md` / `plan.md` / `report.md` と同列に見える現在の file name は誤誘導になり得るため、metadata 的な扱いとして `.assurance.json` へ改名する。
- PR #245 の dogfooding 中、`wait_pr_observation.sh` / `pr_observation_wait.py` が CI passed、selected review comments 0、selected review threads 0、`completion_signal=none` の状態を `review_completion_unknown` として terminal-like `human_gate` に昇格し、監視を終了した。その約 14 分後に Codex が同じ head SHA に対する submitted PR review と 5 件の P1 unresolved review threads を投稿した。
- 追加リサーチと ChatGPT GPT-5.5 Pro Extended / deep consultant の分析により、time / quiet window / same fingerprint / selected comments 0 は review completion の証拠ではなく、明示的な Codex-authored completion artifact がない限り監視を継続し、deadline 到達時は retryable `timeout` / `wait_or_resume` とする必要があると判断した。

## 情報源

- `discussions/20260627t130116z-research-plan-centric-execution-guidance-handoff.md`
- `discussions/20260627t131746z-research-plan-centric-guidance-requirement-preparation.md`
- `discussions/20260627t132248z-disc-plan-centric-guidance-requirement-scope-synthesis.md`
- `discussions/20260627t132404z-interview-default-guidance-dynamic-fields-cutover.md`
- `discussions/20260628t043053z-research-script-local-codex-review-instruction-source.md`
- `discussions/20260628t052300z-research-hidden-assurance-contract-path.md`
- `../../discussions/20260623t074444z-adr-trusted-base-sha-github-review-policy.md`
- `spec-dock/docs/workflow_issue.md`
- `spec-dock/docs/workflow_spec_authoring.md`
- `spec-dock/docs/phase_plan_issue.md`
- `spec-dock/docs/authoring/issue-plan.md`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/context_packets.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/context_routing.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/runbook.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/workflow.py`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh`
- `tests/cli_runtime/test_workflow.py`
- `tests/cli_runtime/test_workflow_context_routing.py`
- `tests/cli_runtime/test_assurance_compose.py`
- `tests/unit/infra/test_init_update.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/assurance_store.py`
- `tests/unit/infra/test_assurance_store.py`
- `tests/cli_runtime/test_assurance.py`
- `discussions/20260628t143306z-research-pr-observation-review-completion-signals.md`
- `discussions/20260628t150332z-disc-pr-observation-completion-wait-repair-draft.md`
- `../../discussions/20260628t154553z-adr-pr-observation-explicit-review-completion.md`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`
- `.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
- `.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`

## スコープ

### 必須

- `guidance issue-execution` の default Markdown / JSON / runbook projection から、authoritative dynamic execution fields を削除する。
- 削除対象には少なくとも `selected_step`、`step_assurance`、`context_packets`、runtime による worker / reviewer / verification / reasoning effort / context mode 推定を含める。
- `guidance issue-execution` は、ready / blocked / planning-required の preflight result、canonical artifact path、commands、stop conditions、contract source、evidence ledger を返す。
- `report.md` の completion evidence は audit evidence として扱い、runtime が次 step を選ぶ control plane には使わない。
- `plan.md` authoring / assurance compose / issue planning docs は、Issue-level Quality Profile と Step-level Obligation Pattern を計画時に作り込める guidance / scaffold を持つ。
- `spec-dock-issue-planning` と `spec-dock-issue-execution` の skill 文面から、runtime-selected step を task checklist / execution authority として扱う記述を削除する。
- 旧 dynamic model を期待する tests を、plan-centric preflight / plan contract lint / hard cutover を検証する tests に置き換える。
- provider source を正本として変更し、必要な dogfooding workspace 確認を行う。
- この Issue planning 作業自体を manual test として扱い、`guidance issue-planning` / `assurance classify` / `assurance compose` / `validate` の観測結果を `report.md` または discussion artifact に残す。
- PR #245 dogfooding failure の修正として、GitHub PR observation の review trigger instruction source を script-local Markdown に差し替える。
- `trigger_codex_review.sh` は GitHub contents API で base branch / PR head の `.github/codex/review-policy.md` を読まない。
- Review trigger instruction は `github-pr-observation` skill の script 近傍に置く Markdown から読み、valid な場合は `@codex review` comment に metadata と instruction text を含める。
- Script-local instruction が missing の場合は、instruction text なしの deterministic `@codex review` comment を投稿し、fallback metadata を残す。
- Script-local instruction が present だが invalid / oversized / unreadable の場合は human gate とし、comment を投稿しない。
- `.github/codex/review-policy.md` bootstrap asset は provider / dogfooding workspace から削除する。
- Issue-local Assurance Contract の canonical file name を `assurance.json` から `.assurance.json` に変更する。
- Runtime は `.assurance.json` を read/write/verify の authority とし、新規に `assurance.json` を作成しない。
- Existing dogfooding Issue-local `assurance.json` artifacts は `.assurance.json` に rename する。
- `.assurance.json` がなく旧 `assurance.json` だけが存在する場合は、current authority として silently accept せず、migration-required diagnostics を返す。
- CLI help / current docs / tests / guidance output は `.assurance.json` を canonical contract path として扱う。
- PR observation wait logic は、`completion_signal=none` / `missing_current_completion_signal` を time / quiet window / same fingerprint / selected comments 0 によって terminal-like completion または human gate に昇格しない。
- Trusted review completion は、current trigger boundary と expected head SHA に bind された Codex-authored submitted PR review、または strict no-findings issue comment に限定する。
- Overall deadline まで trusted review completion artifact がない場合、`wait_pr_observation.sh` は `timeout` / `wait_or_resume` / `observation_complete=false` と same-boundary resume metadata を返す。
- `review_completion_unknown` は新規 active wait result として返さない。過去 artifact 互換の legacy vocabulary としてのみ扱い、no-review-work proof または merge-prepared proof にしない。
- quiet window / same fingerprint は、trusted completion artifact が見えた後の review comments / review threads / body hydration stability にのみ使う。
- PR #245 型の delayed review sequence は regression test として固定し、CI passed + no completion + stable fingerprint の後に submitted PR review が遅れて出た場合、wait loop が早期終了せず review feedback を拾うことを検証する。

### 禁止

- `selected_step`、`step_assurance`、`context_packets` を deprecated field として default output に残さない。
- `report.md` parser を改善して dynamic step selector を延命しない。
- runtime が `plan.md` の free text から task kind を推定し、worker / reviewer / verification を決める仕組みを default issue execution に残さない。
- generated projection files を agent handoff authority にしない。
- `lite_candidate` を obligation reduction authority として扱わない。
- plan 不備を execution 中の暗黙判断で補わない。
- GitHub base branch / PR head の `.github/codex/review-policy.md` を review trigger instruction source として使用しない。
- Missing instruction を理由に Codex review trigger comment の投稿を止めない。
- Script-local instruction を読み込むために caller-provided body、任意 path、任意 endpoint、raw `gh` args を受け付けない。
- 新規または current authority として `assurance.json` を write しない。
- 旧 `assurance.json` を `.assurance.json` と同等の current authority として silently read しない。
- `review_completion_unknown` を active terminal status / active `decision.status_reason` として新規出力しない。
- CI passed、quiet window、same fingerprint、selected comments 0、reaction only、old trigger artifact、old head artifact を review completion proof として扱わない。
- Timeout result を no-review-work proof、merge-prepared proof、または human が review 不要と判断した証拠として扱わない。

### 対象外

- Issue lifecycle completion、`issue finish`、PR delivery / merge preparation workflow の再設計。
- 自動 Lite default の有効化。
- 新しい external agent invocation framework の導入。
- 既存完了 Issue の requirement / design / plan / report / discussions を歴史的記録として意味変更する retroactive migration。
  - 例外: runtime-managed current contract file である Issue-local `assurance.json` の `.assurance.json` への rename は、dogfooding workspace の current artifact migration として本 Issue の対象内に含める。
- 将来の明示的な context packet utility（必要なら別 Issue で扱う）。
- Team / adversarial repository 向けの strict base-branch governance mode の導入。
- `github-pr-observation` 全体の全面 state-machine refactor。
  - 例外: 今回の delayed review 見逃しを止めるため、explicit completion artifact model / hydration semantics / timeout semantics に必要な最小限の state整理は対象内に含める。
- Codex no-findings wording の全バリエーション調査。
  - 例外: 現行 strict no-findings wording と head binding に基づく regression coverage は対象内に含める。

## 境界

- 常に行う:
  - `plan.md` を execution contract、`report.md` を observed evidence ledger として扱う。
  - `guidance issue-execution` は execution readiness と consistency を確認し、`may_execute_approved_plan` で実行可否を明示する。実行順や step obligations は `plan.md` を参照するよう促す。
  - `.assurance.json` の `authorized_profile` を obligation authority とし、`lite_candidate` は telemetry として扱う。
  - non-executable / scaffold / stale / unresolved な `requirement.md`、`design.md`、`plan.md` は execution-ready にしない。
  - invalid / stale assurance contract は fail-closed とし、`strict` fallback を current authority として偽装しない。
  - hard cutover のため、不要 interface / field は削除対象にする。
  - Review trigger は local script-local instruction を authority とし、GitHub remote policy fetch を authority としない。
  - Assurance Contract は `.assurance.json` を canonical metadata contract とする。
  - PR observation wait は explicit Codex completion artifact または timeout まで責任を持って監視し、completion 不明を downstream fresh audit に丸投げしない。
  - `no_completion_evidence` は diagnostics として扱い、completion / no-review-work proof にはしない。
- 判断が必要:
  - `context_routing.py` / `context_packets.py` / related store の削除範囲は、残存利用を調査したうえで design で確定する。
  - `NoReview-ReadOnly` を正式 pattern として扱うか、`inspect-only` / `approved-no-op` の rationale として扱うかは design で整理する。
  - S90 / S99 の waiver syntax は、既存 `workflow_issue.md` / `phase_plan_issue.md` と矛盾しない範囲で design / plan へ落とす。
- 行わない:
  - runtime が次 step を選ぶ。
  - runtime が worker / reviewer / verification を計画書の代わりに決める。
  - generated context packet を default execution path で作成・参照させる。
  - GitHub base branch の policy を読んで review trigger 可否を決める。
  - `assurance.json` を agent-facing canonical artifact として扱う。
  - `review_completion_unknown` を新規 active output として返す。
  - time / quiet / same fingerprint を no-completion 状態の terminal 化に使う。

## 非交渉制約

- Provider-side source under `src/spec_dock/assets/` を正本として変更する。
- `spec-dock/` は dogfooding / validation surface として確認する。
- Backward compatibility よりも hard cutover と authority simplification を優先する。
- CLI / Markdown / JSON output の新 contract は tests で固定する。
- `guidance issue-planning` / `guidance issue-execution` の projection は human/debug-only であり、agent authority ではない。
- `report.md` に残す planning workflow manual test 証跡は、raw transcript ではなく観測結果・判断・不具合有無に限定する。
- GitHub PR observation の normal write surface は fixed issue comment POST のままとし、review instruction source の差し替えによって arbitrary GitHub write surface を広げない。
- GitHub PR observation は GitHub Actions workflow runs/jobs のみを CI authority とし、GitHub Checks API、legacy commit statuses、PR status rollup、`gh pr checks`、または等価な check-rollup surface を追加しない。
- Review completion 判定は current trigger boundary と expected head SHA に bind されなければならない。false timeout / resume は許容するが、delayed P1 finding の見逃しは許容しない。

## 受け入れ条件

- AC-001: Ready guidance is plan-centric
  - アクター: issue execution agent
  - 前提: active issue の `requirement.md` / `design.md` / `plan.md` / `.assurance.json` が execution-ready である。
  - 操作: `./spec-dock/scripts/spec-dock guidance issue-execution` を実行する。
  - 期待結果: output は `plan.md` を contract source、`report.md` を evidence ledger として示し、approved plan を実行する next action と stop conditions を返す。
  - 観測点: CLI Markdown / JSON、projected runbook JSON / Markdown。

- AC-002: Dynamic execution fields are removed by hard cutover
  - アクター: issue execution agent / test suite
  - 前提: active issue が execution-ready である。
  - 操作: `guidance issue-execution` の Markdown / JSON / runbook projection を確認する。
  - 期待結果: `selected_step`、`step_assurance`、`context_packets` は default output に存在しない。
  - 観測点: CLI tests、projection JSON tests、Markdown assertions。

- AC-003: Report evidence is not a control plane
  - アクター: issue execution agent
  - 前提: `report.md` に S01-S99 の完了 / 未完了 / misleading rows がある。
  - 操作: `guidance issue-execution` を実行する。
  - 期待結果: runtime は `report.md` completion evidence から next step を算出せず、guidance output は report row の内容で変化しない。
  - 観測点: regression tests replacing old S01/S02 selection tests。

- AC-004: Non-executable plan blocks execution
  - アクター: issue execution agent
  - 前提: active issue の `plan.md` が scaffold、placeholder、構造化不足、未解決 marker、必須 gate 欠落のいずれかを含む。
  - 操作: `guidance issue-execution` を実行する。
  - 期待結果: execution-ready にならず、planning-required / blocked として `plan.md` 修正を促す。`There are no implementation steps yet` のような否定文や、strict-legacy path の symlinked `requirement.md` / `design.md` / `plan.md` を execution-ready として扱わない。
  - 観測点: CLI tests、reason_code、stop conditions。

- AC-005: Plan contract captures execution obligations
  - アクター: issue planner
  - 前提: `assurance compose` 後に plan authoring を行う。
  - 操作: `plan.md` を作成する。
  - 期待結果: 各 implementation step は step pattern / worker allocation / allowed paths / forbidden changes / verification evidence / reviewer or no-review rationale / report evidence destination / commit-no-op gate / amendment trigger を持つ。
  - 観測点: plan authoring docs、compose fragments、plan lint / inspection tests。

- AC-006: Planning-time taxonomy prevents under-review
  - アクター: issue planner / spec reviewer
  - 前提: step が docs-only、runtime/tests、mixed code+docs、migration/rollback、auth/security/privacy、read-only/no-op のいずれかである。
  - 操作: plan contract を作成または lint する。
  - 期待結果: step obligation が risk と change type に応じて適切に表現され、canonical artifact mutation を no-review として扱わない。
  - 観測点: authoring docs / template / lint tests。

- AC-007: Skill kernels stop registering runtime-selected step
  - アクター: planning / execution agent
  - 前提: updated installed skill assets がある。
  - 操作: `spec-dock-issue-planning` / `spec-dock-issue-execution` skill を読む。
  - 期待結果: runtime-selected step を task checklist / execution authority として登録する記述がなく、state / next_action / commands / stop conditions / contract source / evidence ledger を扱う記述になっている。
  - 観測点: provider asset text assertions。

- AC-008: Obsolete dynamic tests are replaced
  - アクター: test suite
  - 前提: old context routing tests exist.
  - 操作: CLI runtime tests を実行する。
  - 期待結果: `selected_step` / worker inference / context packet generation を期待する tests は削除または置換され、plan-centric preflight behavior を検証する tests が pass する。
  - 観測点: `uv run pytest tests/cli_runtime/...`。

- AC-009: Issue planning guidance dogfood evidence is recorded
  - アクター: issue planner
  - 前提: この Issue の requirement / design / plan authoring を行う。
  - 操作: authoring 中に `guidance issue-planning`、`assurance classify`、`assurance compose`、`validate` を実行し、観測結果を記録する。
  - 期待結果: guidance が期待通りなら `report.md` に pass evidence を残し、不具合があれば `discussions/` に bug / research artifact を残す。Draft discussion artifact は frontmatter と本文が正しく区切られ、`---# Heading` のような malformed artifact を生成しない。
  - 観測点: `report.md` Spec Authoring Gate / Evidence Adoption Ledger、必要時の discussion artifact。

- AC-010: Provider and dogfooding surfaces stay consistent
  - アクター: maintainer
  - 前提: provider assets / runtime / tests を変更した。
  - 操作: relevant tests と `./spec-dock/scripts/spec-dock validate` を実行する。
  - 期待結果: provider source と dogfooding workspace の意図した差分が説明でき、validation が pass する。`guidance` が表示する `authorized_profile` / authority は current `assurance classify` source binding と矛盾しない。`workflow-plan-unselectable` のような旧 step selector 由来の block reason は issue-execution default path に残らない。Generated projection path が directory の場合、refresh cleanup は再帰削除せず fail-closed する。
  - 観測点: test output、report evidence、git diff。

- AC-011: Review trigger uses script-local instruction
  - アクター: PR observation agent
  - 前提: `github-pr-observation` skill の script 近傍に valid な `codex-review-instructions.md` がある。
  - 操作: `wait_pr_observation.sh --trigger-mode post-once` 経由で `trigger_codex_review.sh` を実行する。
  - 期待結果: comment body は `@codex review` で始まり、script-local instruction text、instruction path、instruction hash、reviewed head SHA を含む。
  - 観測点: unit test、fake `gh` fixture、PR #245 manual dogfooding。

- AC-012: Review trigger does not fetch GitHub review policy
  - アクター: test suite / maintainer
  - 前提: PR metadata に base SHA がある、または base SHA がない。
  - 操作: review trigger helper を実行する。
  - 期待結果: GitHub contents API で `.github/codex/review-policy.md` を取得しない。Base branch / PR head 上の `.github/codex/review-policy.md` の有無は trigger instruction source に影響しない。
  - 観測点: fake `gh` command log、script assertions、grep inspection。

- AC-013: Missing script-local instruction falls back to plain review
  - アクター: PR observation agent
  - 前提: script-local instruction file が存在しない。
  - 操作: review trigger helper を実行する。
  - 期待結果: comment body は deterministic な `@codex review` comment として投稿され、instruction text は含まれず、metadata に `instruction_status: missing_plain_fallback` が記録される。
  - 観測点: unit test、payload JSON、posted comment body。

- AC-014: Invalid script-local instruction fails closed
  - アクター: PR observation agent
  - 前提: script-local instruction file が present だが empty / non-UTF-8 / oversized / unreadable のいずれかである。
  - 操作: review trigger helper を実行する。
  - 期待結果: `human_gate` になり、comment は投稿されない。
  - 観測点: unit tests、payload limitations。

- AC-015: GitHub/Codex repository policy asset is removed
  - アクター: maintainer
  - 前提: provider assets and dogfooding workspace are inspected.
  - 操作: repository file list and installer/update tests を確認する。
  - 期待結果: `.github/codex/review-policy.md` bootstrap asset は provider / dogfooding workspace から削除され、代わりに script-local instruction asset が存在する。
  - 観測点: `rg --files --hidden`、unit tests、git diff。

- AC-016: Assurance contract canonical path is hidden-style
  - アクター: runtime / maintainer
  - 前提: active issue または明示 issue path がある。
  - 操作: `assurance classify --stage requirement`、`assurance show`、`assurance verify` を実行する。
  - 期待結果: runtime は `.assurance.json` を read/write/verify の canonical path とし、`assurance.json` を新規作成しない。`.assurance.json` 内の unsupported non-empty metadata（例: `obligations.notes`）を silently discard しない。
  - 観測点: unit tests、CLI runtime tests、file list inspection。

- AC-017: Legacy assurance.json is migration-required, not silent authority
  - アクター: runtime / maintainer
  - 前提: `.assurance.json` がなく、旧 `assurance.json` だけが存在する issue がある。
  - 操作: `assurance show` または `assurance verify` を実行する。
  - 期待結果: 旧 path は silently current authority にならず、rename / migration が必要であることを示す diagnostics が返る。Stale source binding を検出した `assurance compose` は source-bound artifact read より前に structured invalid result を返し、missing artifact を unstructured exception として漏らさない。
  - 観測点: unit tests、CLI runtime tests。

- AC-018: Dogfooding assurance artifacts are renamed
  - アクター: maintainer
  - 前提: dogfooding workspace に既存 Issue-local `assurance.json` がある。
  - 操作: relevant dogfooding artifacts を inspect する。
  - 期待結果: current dogfooding Issue-local assurance artifacts は `.assurance.json` に rename され、旧 `assurance.json` は残らない。
  - 観測点: `rg --files --hidden spec-dock | rg '(^|/)assurance\\.json$|(^|/)\\.assurance\\.json$'`、git diff。

- AC-019: Current docs and CLI help use .assurance.json
  - アクター: maintainer / test suite
  - 前提: provider docs / runtime help / tests are updated.
  - 操作: current authority docs and CLI help text を inspect する。
  - 期待結果: current runtime / help / active workflow docs は `.assurance.json` を canonical path として説明する。
  - 観測点: grep inspection、unit / CLI runtime tests。

- AC-020: Review completion is explicit artifact based
  - アクター: PR observation agent
  - 前提: current trigger boundary と expected head SHA が確定している。
  - 操作: `wait_pr_observation.sh` または `fetch_pr_observation_snapshot.sh` が PR reviews / review comments / issue comments / review threads を観測する。
  - 期待結果: trusted review completion は current trigger 後かつ expected head SHA に bind された Codex-authored submitted PR review、または strict no-findings issue comment のみである。`completion_signal=none`、CI passed、quiet window、same fingerprint、selected comments 0 は completion proof にならない。
  - 観測点: wait unit tests、snapshot unit tests、skill text inspection。

- AC-021: Missing review completion times out retryably
  - アクター: PR observation agent
  - 前提: CI passed / head matched だが current trigger boundary に対する trusted Codex completion artifact がない。
  - 操作: `wait_pr_observation.sh` を overall deadline まで実行する。
  - 期待結果: result は `timeout` / `wait_or_resume` / `observation_complete=false` となり、same-boundary resume metadata を含む。`review_completion_unknown` を active terminal status / active `decision.status_reason` として返さない。
  - 観測点: fake snapshot wait tests、stdout JSON、resume metadata assertions。

- AC-022: Hydration only follows explicit completion
  - アクター: PR observation agent
  - 前提: current trigger boundary に対する trusted completion artifact が観測されている。
  - 操作: wait loop が quiet window / same fingerprint を評価する。
  - 期待結果: quiet window / same fingerprint は review object / review comments / review threads / body の hydration stability にのみ使われ、no-completion evidence を completion に昇格しない。
  - 観測点: partial visibility tests、delayed review tests、skill text inspection。

- AC-023: PR #245 delayed review regression is covered
  - アクター: test suite / maintainer
  - 前提: fake snapshots が PR #245 型の sequence を表現する。前半は CI passed + `completion_signal=none` + selected comments 0 + stable fingerprint、後半は same head の submitted Codex PR review + unresolved review threads。
  - 操作: `wait_pr_observation.sh` fake snapshot wait test を実行する。
  - 期待結果: wait loop は no-completion stable phase で早期 terminal にならず、後続 submitted PR review を拾って `human_gate` / `address_review_feedback` を返す。
  - 観測点: regression unit test、PR #245 manual/dogfooding evidence。

- AC-024: Pull request review body is blocker policy input
  - アクター: PR observation agent / test suite
  - 前提: current trigger boundary と expected head SHA に bind された Codex-authored submitted PR review があり、inline review comment / review thread は 0 件だが review body に P0 / P1 finding が含まれる。
  - 操作: `fetch_pr_observation_snapshot.sh` または `wait_pr_observation.sh` が blocker policy を評価する。
  - 期待結果: selected pull request review body を blocker evidence source として扱い、`human_gate` / `address_review_feedback` を返す。Selected review comments / threads 0 を blocker zero / no-finding proof にしない。
  - 観測点: snapshot unit test、stdout JSON の selected review signal、ADR `20260628t185812z-adr`。

## 例外・エッジケース

- EC-001: Legacy issue without `.assurance.json`
  - 条件: substantive requirement はあるが `.assurance.json` がない。
  - 期待: strict legacy authority として readiness を扱う場合でも、dynamic selected step / context packet は返さない。
  - 観測点: CLI tests。

- EC-002: Stale source binding
  - 条件: `.assurance.json` の source binding 後に requirement / design / plan が変わった。
  - 期待: execution-ready にせず、classification / planning repair を促す。
  - 観測点: existing stale binding tests。

- EC-003: Context policy missing or invalid
  - 条件: `context-routing-policy.json` が missing / invalid。
  - 期待: default `guidance issue-execution` は context packet generation に依存しないため、context policy の問題だけで ready issue を block しない。ただし残存機能がある場合は対象機能で fail-closed する。
  - 観測点: updated tests。

- EC-004: Docs-only but canonical workflow change
  - 条件: docs / templates / skill / workflow text の変更 step。
  - 期待: no-review ではなく `SpecOnly` 相当の spec-reviewer / docs inspection obligation を plan に持つ。
  - 観測点: plan lint / spec review。

- EC-005: Mixed code and docs step
  - 条件: runtime code と shipped docs / skill text を同じ step で変更する。
  - 期待: split-first、または `CodePlusSpec` 相当として both reviewer focus を plan に明記する。
  - 観測点: plan lint / reviewer checklist。

- EC-006: Generated projection stale
  - 条件: `.agent/runbooks/current-runbook.*` や `active/current-runbook.*` が古い。
  - 期待: agent は projection を authority として読まず、fresh stdout guidance と canonical docs を使う。projection refresh 後に `Step Assurance` / `Context Packets` / `selected_step` が残らない。
  - 観測点: skill text / tests。

- EC-007: Script-local review instruction missing
  - 条件: `codex-review-instructions.md` が存在しない。
  - 期待: `@codex review` comment は投稿され、instruction missing fallback が metadata に残る。
  - 観測点: review trigger unit test。

- EC-008: Script-local review instruction invalid
  - 条件: `codex-review-instructions.md` が empty / non-UTF-8 / oversized / unreadable。
  - 期待: `human_gate` になり、comment を投稿しない。
  - 観測点: review trigger unit test。

- EC-009: Legacy assurance.json remains after cutover
  - 条件: `.assurance.json` がなく `assurance.json` だけがある。
  - 期待: runtime は current authority として silently accept せず、migration-required diagnostics を返す。
  - 観測点: assurance store / CLI runtime tests。

- EC-010: Generated projection path is a directory
  - 条件: `spec-dock/active/current-runbook.json`、`current-runbook.md`、または `context-pack.md` の位置に directory が存在する。
  - 期待: active pointer refresh は directory を削除せず、異常状態として停止する。
  - 観測点: active store unit test。

- EC-011: Unsupported obligation notes
  - 条件: `.assurance.json` の `obligations.notes` が non-empty である。
  - 期待: 現行 domain model が preserve しない metadata は invalid schema として拒否し、読み捨てない。
  - 観測点: assurance store unit test。

- EC-012: Deleted source-bound artifact after classify
  - 条件: `.assurance.json` の source binding 後に `design.md` / `plan.md` / `report.md` が削除された。
  - 期待: `assurance compose` は stale source binding の structured JSON を返し、FileNotFoundError を top-level に漏らさない。
  - 観測点: CLI runtime compose test。

## 用語

- Plan-centric execution:
  - `plan.md` を実行順と品質ゲートの authority とし、runtime guidance は readiness を確認するだけの execution model。
- Preflight validator:
  - 実行を始めてよい条件、足りない artifact、stop conditions を確認する runtime guidance の役割。
- Dynamic execution fields:
  - `selected_step`、`step_assurance`、`context_packets` など、runtime が実行時に step / worker / reviewer / context を選ぶための output fields。
- Script-local review instruction:
  - `github-pr-observation` の comment posting script 近傍に置く Markdown instruction。GitHub base branch / PR head の `.github/codex/review-policy.md` ではなく、local checkout の script asset として `@codex review` comment に添える。
- Hidden-style assurance contract:
  - Issue-local `.assurance.json`。Quality profile / source binding / stale detection を保持する runtime-managed metadata contract。Agent-facing primary docs と同列の編集対象ではない。
- Hard cutover:
  - 旧 dynamic execution fields / interface を deprecated として残さず、default contract から削除する移行方針。
- Step-level Obligation Pattern:
  - step の change type / risk / evidence level に応じて、worker、verification、reviewer、no-review rationale、commit/no-op gate を計画時に固定する分類。

## 未確定事項

- Q-001:
  - 質問: `selected_step` / `step_assurance` / `context_packets` を互換期間なしで削除してよいか。
  - 回答: hard cutover を採用する。不要な interface / field は削除する。
  - 証跡: `discussions/20260627t132404z-interview-default-guidance-dynamic-fields-cutover.md`
  - 状態: 解決済み。

- Q-002:
  - 質問: `context_routing.py` / `context_packets.py` の削除範囲をどこまでにするか。
  - 推奨案: default issue-execution の旧 interface としては削除対象にし、残存利用がある場合だけ design で根拠付きに限定する。
  - 影響範囲: design / tests。
  - 状態: design で解決する。

- Q-003:
  - 質問: `NoReview-ReadOnly` を正式 pattern として採用するか。
  - 推奨案: canonical artifact mutation を no-review にしない制約を優先し、pattern 名は design / plan authoring の中で整理する。
  - 影響範囲: plan schema / lint / tests。
  - 状態: design で解決する。
