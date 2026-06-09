---
種別: 実装計画書（Issue）
ID: "iss-00176"
タイトル: "GitHub PR observation should trigger and wait for Codex review completion"
関連GitHub: ["#176"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-09"
依存: ["requirement.md", "design.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00176 GitHub PR observation should trigger and wait for Codex review completion — 実装計画（実行契約 / Execution Contract）

## この計画で満たす要件ID

- AC:
  - AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, AC-007, AC-008
- EC:
  - EC-001, EC-002, EC-003, EC-004, EC-005, EC-006, EC-007
- 制約:
  - fixed `@codex review` write boundary
  - default `post-once` / explicit `resume`
  - final stdout JSON authority
  - selected review body full text in stdout
  - selected body is independent from `body-mode`
  - no arbitrary GitHub write / raw `gh` / GraphQL / jq / body / header / endpoint inputs
  - no retired `pr-monitor` or retired review-comments skill revival
  - provider-side source authority under `src/spec_dock/assets/install_root/`

## 依存関係から導く実装順序

- 依存関係の参照元:
  - `design.md` の依存関係分析、Module Dependency Diagram、ディレクトリ / ファイル変更計画。
  - `discussions/20260609t143000z-disc-implementation-plan-draft-pr-observation-codex-review.md` の implementation-planner draft。
- 順序ルール:
  - fixed write boundary を先に固定する。
  - public wait mode orchestration は write helper の contract 固定後に実装する。
  - read-only snapshot / review collector は wait から明示 trigger metadata が渡る前提で更新する。
  - final wait status / timeout / output authority は helper、mode、collector の contract が揃ってから統合する。
  - user-facing skill docs と package/install regression は behavior が安定してから更新する。
- step 依存サマリー:
  - S01:
    - 依存: reviewed `requirement.md` / `design.md`
    - unblock: S02, S04
    - 対象ファイル: `trigger_codex_review.sh`, `tests/unit/infra/test_init_update.py`
  - S02:
    - 依存: S01
    - unblock: S03, S04
    - 対象ファイル: `wait_pr_observation.sh`, `tests/unit/infra/test_init_update.py`
  - S03:
    - 依存: S02
    - unblock: S04
    - 対象ファイル: `fetch_pr_observation_snapshot.sh`, `lib/fetch_pr_review_snapshot.sh`, tests
  - S04:
    - 依存: S01, S02, S03
    - unblock: S05a, S05b, S90, S99
    - 対象ファイル: `wait_pr_observation.sh`, `fetch_pr_observation_snapshot.sh`, tests
  - S05a:
    - 依存: S01-S04
    - unblock: S90
    - 対象ファイル: `SKILL.md`
  - S05b:
    - 依存: S01-S04
    - unblock: S90, S99
    - 対象ファイル: package/install assertions in `tests/unit/infra/test_init_update.py`

## ステップ一覧

- S01:
  - 観測可能な振る舞い: fixed helper が head match 後に固定 `@codex review` comment を1回だけ投稿し、safe JSON を返す。
  - 依存: reviewed design
  - unblock: S02 / S04
  - 対象ファイル: helper script / tests
  - 閉じる要件: AC-001, AC-002, AC-006, AC-007, EC-001, EC-005
  - レビューゲート: code-reviewer
- S02:
  - 観測可能な振る舞い: wait default `post-once` / explicit `resume` が trigger metadata を決定的に扱う。
  - 依存: S01
  - unblock: S03 / S04
  - 対象ファイル: wait script / tests
  - 閉じる要件: AC-001, AC-003, AC-008, EC-005, EC-007
  - レビューゲート: code-reviewer
- S03:
  - 観測可能な振る舞い: read-only collector が submitted PR review primary、selected body full text、collection summary を返す。
  - 依存: S02
  - unblock: S04
  - 対象ファイル: snapshot/review collector / tests
  - 閉じる要件: AC-003, AC-004, AC-008, EC-002, EC-006, EC-007
  - レビューゲート: code-reviewer
- S04:
  - 観測可能な振る舞い: wait final JSON が CI/review/head/timeout/output authority を統合する。
  - 依存: S01-S03
  - unblock: S05a / S05b / S90 / S99
  - 対象ファイル: wait/snapshot integration / tests
  - 閉じる要件: AC-003, AC-005, AC-006, AC-008, EC-003, EC-004, EC-006, EC-007
  - レビューゲート: code-reviewer
- S05a:
  - 観測可能な振る舞い: skill docs が fixed trigger write + read-only observation contract を説明する。
  - 依存: S01-S04
  - unblock: S90
  - 対象ファイル: `SKILL.md`
  - 閉じる要件: docs / retired workflow constraints
  - レビューゲート: spec-reviewer
- S05b:
  - 観測可能な振る舞い: new helper が shipped install-root / install/update / package inventory に含まれる。
  - 依存: S01-S04
  - unblock: S90 / S99
  - 対象ファイル: package/install tests
  - 閉じる要件: provider-side asset / package constraints
  - レビューゲート: code-reviewer
- S90:
  - 観測可能な振る舞い: docs impact が解消または no-op evidence で閉じる。
  - レビューゲート: spec-reviewer
- S99:
  - 観測可能な振る舞い: issue-wide QA / code / spec gate が closure coverage を確認する。
  - レビューゲート: qa-reviewer, code-reviewer, spec-reviewer

## 要件 ↔ ステップ対応

- AC-001 -> S01, S02
- AC-002 -> S01
- AC-003 -> S02, S03, S04
- AC-004 -> S03
- AC-005 -> S04
- AC-006 -> S01, S04
- AC-007 -> S01
- AC-008 -> S02, S03, S04
- EC-001 -> S01
- EC-002 -> S03
- EC-003 -> S04
- EC-004 -> S04
- EC-005 -> S01, S02
- EC-006 -> S03, S04
- EC-007 -> S02, S03, S04
- fixed write / no arbitrary GitHub API constraints -> S01, S02, S03, S04
- provider-side asset authority -> S05b
- retired workflow constraints -> S05a, S90

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| 識別子（ID） | ステップ（step） | スライス（slice） | 種別（type） | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル（evidence level） | クロージャ証跡（closure evidence） |
|---|---|---|---|---|---|---|---|---|---|---|
| cl-001 | S01 | fixed trigger write | acceptance | AC-001, AC-002, EC-005 | helper は pre-head match 後に `@codex review` issue comment を1回だけ投稿し、comment metadata JSON を返す | fake `gh` call log / helper stdout JSON | trigger 不発、誤 endpoint、既存 trigger reuse | yes | red-required | S01 Step/Test Closure |
| cl-002 | S01 | pre-trigger stale | negative | AC-006 | pre-trigger head mismatch では POST せず stale/non-success JSON を返す | fake PR head mismatch | stale PR で review を起動する回帰 | yes | red-required | S01 Step/Test Closure |
| cl-003 | S01 | POST failure recovery | negative | AC-007, EC-001 | POST failure は blind retry せず、exact one-comment recovery だけ採用する | fake POST failure / before-after comments | 二重投稿、曖昧 recovery | yes | red-required | S01 Step/Test Closure |
| cl-004 | S02 | trigger mode | acceptance | AC-001, AC-008, EC-005, EC-007 | wait default は `post-once`、`resume` は explicit metadata 必須で trigger helper を呼ばない | wait invocation / fake call log | implicit no-post、auto reuse、double trigger | yes | red-required | S02 Step/Test Closure |
| cl-005 | S02 | stdout capture | invariant | AC-003 | helper stdout は内部捕捉され、user-facing stdout は final JSON 1個だけ | helper JSON + snapshot JSON | stdout に複数 JSON が混ざる回帰 | yes | red-required | S02 Step/Test Closure |
| cl-006 | S03 | review completion primary | acceptance | AC-004, EC-002 | Codex-authored submitted PR review が primary completion signal であり fallback は区別される | fake reviews/comments after trigger | issue comment / quiet window primary 誤判定 | yes | red-required | S03 Step/Test Closure |
| cl-007 | S03 | selected body stdout | invariant | AC-003, AC-004, EC-006 | selected review/comment body は `body-mode` に関係なく stdout JSON に全文で含まれる | `--body-mode none|out-only|trigger-window-truncated` | body が `--out` のみに退避 / truncate される回帰 | yes | red-required | S03 Step/Test Closure |
| cl-008 | S03 | resume collection summary | acceptance | AC-008, EC-007 | reviews / review_comments / review_threads が fetched IDs、selected IDs、boundary-before exclusion、unresolved thread IDs/counts を返す | trigger 前後の fake artifacts | timeout/resume の取りこぼし | yes | red-required | S03 Step/Test Closure |
| cl-009 | S04 | CI/review mixed status | acceptance | AC-005, EC-003, EC-004 | CI と review lifecycle は独立し、mixed state を final status / next action で区別する | CI failed + review completed / CI passed + review pending | 片方完了だけで success になる回帰 | yes | red-required | S04 Step/Test Closure |
| cl-010 | S04 | stale after trigger/poll | negative | AC-006 | post-trigger / polling head mismatch は trigger metadata を保持し stale/non-success を返す | fake head drift | stale success、trigger metadata loss、delete mutation | yes | red-required | S04 Step/Test Closure |
| cl-011 | S04 | output authority | invariant | AC-003, EC-006 | stdout は authority final JSON、stderr は bounded progress、`--out/result.json` は stdout copy、`summary.md` は無し | wait with `--out` / progress modes | authority split、summary artifact 復活 | yes | red-required | S04 Step/Test Closure |
| cl-012 | S04 | timeout resume metadata | acceptance | AC-008, EC-007 | timeout/limit JSON は同一 boundary の resume metadata と command hint を含む | pending CI/review timeout | unresumable timeout | yes | red-required | S04 Step/Test Closure |
| cl-013 | S05b | shipped asset/package | scaffold/package | scope, constraints, epic design | `trigger_codex_review.sh` は source install-root、init/update layout、package inventory に含まれる | package/install regression tests | source / install / package drift | yes | red-required | S05b Step/Test Closure |
| cl-014 | S05a | skill contract docs | docs/spec | scope, non-scope, constraints | `SKILL.md` は fixed trigger write + read-only observation、default/resume、stdout body、retired workflow prohibition を説明する | docs inspection | old workflow revival、user discretion trigger | yes | inspect-only | S05a Step/Test Closure |
| cl-015 | S90 | docs impact | docs/spec | docs impact | docs/templates/README/workflow/skill/migration notes の影響が更新または no-op evidence で閉じる | docs diff / inspection | undocumented breaking contract | yes | inspect-only | S90 evidence |
| cl-016 | S99 | final gate | quality | workflow issue final gate | QA、issue-wide code review、final spec review、validation、diff/report gates が記録される | full issue diff / report evidence | step-local pass が統合失敗を隠す回帰 | yes | manual-required | S99 evidence |

## レビュー / QA ゲート方針

- RG1 step review:
  - 実施タイミング: 各 implementation step の report evidence 更新後、step commit 前。
  - reviewer:
    - code / runtime / tests / scaffold behavior: `code-reviewer`
    - docs-only / skill-text-only: `spec-reviewer`
  - pass 条件: fresh `review_status: pass`
  - fail 時: bounded follow-up を同じ step 範囲で修正し、fresh pass まで再実行する。
- QG1 final QA:
  - reviewer: `qa-reviewer`
  - 範囲: AC/EC/closure coverage、missing high-value tests、integration test 要否、`body-mode` selected-body obligation。
- CRG1 final code review:
  - reviewer: issue-wide `code-reviewer`
  - 範囲: integrated script/test/package diff、fixed write boundary、read-only collector boundary、failure modes、maintainability。
- SG1 final spec review:
  - reviewer: `spec-reviewer`
  - 範囲: requirement / design / plan / report / docs / implementation / tests 整合。

## 実行ルール（全ステップ共通）

- 各 implementation step は原則 `1 behavior slice / 1 review scope / 1 commit boundary` とする。
- `plan.md` には planned contract だけを書く。observed result は `report.md` に記録する。
- implementation 中に新しい仕様、bug class、外部 contract risk、未計画 closure が見つかった場合は、report 記録だけで足りるか plan amendment と re-review が必要かを判断する。
- delegated worker output は reviewer gate の代替ではない。
- fixed GitHub write boundary を広げる必要が出た場合は、実装を止めて requirement / design amendment に戻す。
- `tests/unit/infra/test_init_update.py` が肥大化しすぎて step-local review が困難になる場合は、既存 local pattern を確認した上でテスト分割の design/plan amendment 要否を判断する。

## 実装ステップ

### 実装ステップ S01 — fixed trigger write helper

- 振る舞いの目標（behavior goal）:
  - `trigger_codex_review.sh` を追加し、expected head SHA が一致する場合だけ固定本文 `@codex review` を PR issue comment として1回投稿し、trigger metadata JSON を返す。
- design 参照:
  - `design.md` `trigger_codex_review.sh`
- 依存:
  - reviewed `requirement.md` / `design.md`
- unblock:
  - S02, S04
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh`
  - `tests/unit/infra/test_init_update.py`
- 計画済み契約（planned contract）:
  - scope:
    - fixed endpoint、fixed body、strict validation、pre/post head checks、POST failure、exact one-comment recovery を実装・検証する。
  - テスト義務（test obligation）:
    - closure id: cl-001, cl-002, cl-003
    - coverage rationale: write boundary は安全上の中心であり、positive / stale / failure / recovery の negative path を red-required で固定する。
  - Red / 代替証跡の要件:
    - red-required: helper script 不在または未実装の状態で fake `gh` tests が失敗することを確認する。
  - 実装範囲（implementation scope）:
    - allowed paths:
      - `trigger_codex_review.sh`
      - S01-focused tests in `tests/unit/infra/test_init_update.py`
    - forbidden changes:
      - wait orchestration
      - snapshot/review collector behavior
      - skill docs
      - GitHub state / secrets
  - Green 検証:
    - focused pytest selection for S01 tests
    - fake `gh` write call log inspection
  - Refactor / cleanup ガードレール:
    - 目的: helper 内の JSON assembly / validation を読みやすく保つ。
    - 禁止する広がり: 汎用 GitHub write helper 化、caller-provided body/endpoint 追加。
  - report 証跡の記録先:
    - Implementation Delegation Gate
    - TDD evidence
    - Step Contract Closure
    - Test Contract Closure
    - Closure Coverage
  - amendment trigger:
    - fixed `@codex review` POST 以外の write が必要になる。
    - exact one-comment recovery では POST response loss を扱えない。

#### 委任契約（delegation contract）

- 委任ロール（delegated role）:
  - `dev-coder`
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`
  - current target scripts/tests
- 許可 paths:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh`
  - `tests/unit/infra/test_init_update.py`
- 禁止 changes:
  - S02-S05 target behavior
  - arbitrary GitHub write surface
  - docs/config/workflow/GitHub state/secrets
- 受け入れ条件:
  - cl-001, cl-002, cl-003
- 必須 tests または docs-only verification:
  - focused fake `gh` pytest
  - call log showing one fixed POST or no POST for stale/failure
- reviewer focus:
  - `code-reviewer`: fixed write boundary, validation, recovery ambiguity, executable permission, tests
- 必須出力（output required）:
  - changed files
  - verification result
  - fake `gh` call summary
  - Ledger Note or `No material implementation decisions beyond the approved plan.`
- 停止条件（stop conditions）:
  - caller-provided body/endpoint が必要
  - non-fixed GitHub mutation が必要
  - recovery ambiguity を fail closed にできない

#### 具体テストケース一覧

#### behavior slice execution

- Red / characterization:
  - cl-001, cl-002, cl-003 を対象に fake `gh` tests を先に追加し、helper 未実装または既存状態では失敗することを確認する。
- Implementation:
  - fixed endpoint / fixed body / strict validation / head match / POST failure recovery を helper 内に閉じる。
- Green:
  - S01-focused pytest と fake `gh` call log で one fixed POST、no stale POST、no blind retry を確認する。
- Report:
  - TDD evidence、Step/Test Closure、Closure Coverage、step reviewer result を `report.md` に記録する。

- `tc-s01-001` acceptance: helper posts fixed issue comment
  - 前提: fake `gh pr view` returns matching `headRefOid`.
  - 操作: `trigger_codex_review.sh --repo owner/repo --pr 13 --head-sha abc1234`.
  - 期待結果: one fixed POST to `repos/owner/repo/issues/13/comments` with body `@codex review`, and JSON with comment id / created_at / body evidence.
  - 失敗検出: wrong endpoint、missing POST、caller-controlled body、multiple POST。
  - 検証方法: fake `gh` call log assertion in `tests/unit/infra/test_init_update.py`.
  - 関連 closure id: cl-001

- `tc-s01-002` negative: pre-trigger stale head does not post
  - 前提: fake initial PR head differs from `--head-sha`.
  - 操作: helper invocation with old SHA.
  - 期待結果: no POST call; stdout JSON reports stale/non-success with current head evidence.
  - 失敗検出: stale PR triggers Codex review.
  - 検証方法: fake `gh` call log and stdout JSON assertion.
  - 関連 closure id: cl-002

- `tc-s01-003` negative: POST failure fail-closed
  - 前提: fake POST returns timeout/error and after snapshot yields zero or multiple exact-body candidates.
  - 操作: helper invocation.
  - 期待結果: no blind retry; final JSON carries blocking limitation.
  - 失敗検出: second POST or ambiguous recovery accepted.
  - 検証方法: fake call-count and JSON limitation assertions.
  - 関連 closure id: cl-003

- `tc-s01-004` recovery: exactly one new comment can be recovered
  - 前提: fake POST response is lost but before/after issue comments show exactly one new exact `@codex review` comment.
  - 操作: helper invocation.
  - 期待結果: JSON action is recovered, with recovered comment metadata and no second POST.
  - 失敗検出: recovery ignored or recovered without exact-one proof.
  - 検証方法: fake before/after comments fixture.
  - 関連 closure id: cl-003

#### ステップ完了契約（step closure contract）

- closure id:
  - cl-001, cl-002, cl-003
- close 条件:
  - S01 tests pass.
  - helper has executable permission.
  - no non-fixed write surface is exposed.
- 検証 evidence:
  - focused pytest command
  - fake `gh` call log
- report evidence:
  - Step Contract Closure
  - Test Contract Closure
  - Closure Coverage
  - Step Commit Gate
- 残リスク:
  - live GitHub response field variations are handled as limitation evidence in implementation.

#### ステップゲート（step gate）

- step reviewer gate:
  - reviewer: `code-reviewer`
  - review 範囲: helper script, tests, write boundary, recovery failure modes
  - pass 条件: `review_status: pass`
  - re-review rule: 指摘を修正し pass まで再実行
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S01 target files only
  - no-op: not allowed unless helper already exists and satisfies cl-001..cl-003 with evidence

### 実装ステップ S02 — wait trigger mode orchestration

- 振る舞いの目標（behavior goal）:
  - `wait_pr_observation.sh` に default `post-once` と explicit `resume` を追加し、trigger helper stdout を内部捕捉しながら snapshot に trigger metadata を渡す。
- design 参照:
  - `design.md` `wait_pr_observation.sh`, Mode Contract
- 依存:
  - S01
- unblock:
  - S03, S04
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
  - `tests/unit/infra/test_init_update.py`
- 計画済み契約（planned contract）:
  - scope:
    - `--trigger-mode post-once|resume` を追加する。
    - mode 未指定は `post-once`。
    - `post-once` + trigger metadata は usage error。
    - `resume` は `--trigger-comment-id` と `--trigger-created-at` の両方を必須にする。
    - `post-once` は helper を1回だけ呼び、`resume` は helper を呼ばない。
  - テスト義務:
    - closure id: cl-004, cl-005
    - coverage rationale: mode ambiguity と stdout JSON 混在は agent の誤判断へ直結するため red-required。
  - Red / 代替証跡の要件:
    - red-required: 現行 wait は mode option を持たず、default trigger 投稿もしないため mode/call-flow tests が失敗する。
  - 実装範囲:
    - allowed paths:
      - `wait_pr_observation.sh`
      - S02-focused tests
    - forbidden changes:
      - review selection JSON implementation beyond forwarding explicit metadata
      - skill docs
      - package inventory
  - Green 検証:
    - usage validation tests
    - fake helper/snapshot call-flow tests
    - stdout parse tests
  - Refactor / cleanup ガードレール:
    - 目的: wait orchestration の mode branch を明確にする。
    - 禁止する広がり: inferred trigger reuse を normal wait path に戻す。
  - report 証跡の記録先:
    - Implementation Delegation Gate
    - TDD evidence
    - Step/Test Closure
    - Closure Coverage
  - amendment trigger:
    - `post-once` と `resume` 以外の mode が必要になる。
    - helper stdout を final stdout から分離できない。

#### 委任契約（delegation contract）

- 委任ロール:
  - `dev-coder`
- 入力 docs:
  - requirement, design, plan, S01 result, current wait script/tests
- 許可 paths:
  - `wait_pr_observation.sh`
  - `tests/unit/infra/test_init_update.py`
- 禁止 changes:
  - S03 collector semantics
  - docs/package-only changes
  - GitHub state/secrets
- 受け入れ条件:
  - cl-004, cl-005
- 必須 tests:
  - mode usage tests
  - fake helper/snapshot call log tests
  - stdout single JSON test
- reviewer focus:
  - `code-reviewer`
- 必須出力:
  - changed files
  - verification result
  - call flow evidence
  - Ledger Note or no material decision note
- 停止条件:
  - implicit trigger reuse が必要
  - `resume` が no-post を保証できない
  - usage error が command 前に止まらない

#### 具体テストケース一覧

#### behavior slice execution

- Red / characterization:
  - cl-004, cl-005 を対象に mode usage、helper/snapshot call-flow、stdout single JSON tests を先に追加し、現行 wait では失敗することを確認する。
- Implementation:
  - default `post-once` と explicit `resume` の分岐、usage validation、helper stdout の内部捕捉、snapshot への trigger metadata forwarding を実装する。
- Green:
  - fake helper/snapshot call log と stdout parse assertion で default post-once / resume no-post / one final JSON を確認する。
- Report:
  - mode contract、call-flow、stdout boundary の証跡を `report.md` に記録する。

- `tc-s02-001` acceptance: default wait posts once before polling
  - 前提: fake helper succeeds and fake snapshot reaches terminal status.
  - 操作: `wait_pr_observation.sh --repo owner/repo --pr 13 --head-sha abc1234`.
  - 期待結果: helper is called once before snapshot; snapshot receives helper `comment_id` and `created_at`.
  - 失敗検出: no helper call, repeated helper call, or inferred trigger used.
  - 検証方法: fake helper/snapshot call log.
  - 関連 closure id: cl-004

- `tc-s02-002` negative: resume does not post
  - 前提: explicit trigger id/time are supplied.
  - 操作: wait with `--trigger-mode resume --trigger-comment-id 456 --trigger-created-at 2026-06-09T10:00:00Z`.
  - 期待結果: no helper/POST call; snapshot receives explicit metadata.
  - 失敗検出: resume posts a new trigger or drops boundary metadata.
  - 検証方法: fake call log.
  - 関連 closure id: cl-004

- `tc-s02-003` negative: invalid mode/metadata combinations fail usage
  - 前提: `post-once` with trigger metadata, or `resume` missing one metadata field.
  - 操作: invalid wait invocation.
  - 期待結果: usage error before any `gh`, helper, or snapshot command.
  - 失敗検出: ambiguous mode accepted.
  - 検証方法: exit code and empty fake call log.
  - 関連 closure id: cl-004

- `tc-s02-004` invariant: helper stdout does not leak
  - 前提: helper returns JSON and snapshot returns terminal JSON.
  - 操作: default wait invocation.
  - 期待結果: stdout parses as one JSON final result only; helper JSON is integrated, not emitted separately.
  - 失敗検出: two JSON documents on stdout.
  - 検証方法: stdout parse and document-count assertion.
  - 関連 closure id: cl-005

#### ステップ完了契約（step closure contract）

- closure id:
  - cl-004, cl-005
- close 条件:
  - mode validation, helper orchestration, explicit boundary forwarding, stdout capture are covered.
- 検証 evidence:
  - focused pytest command
  - fake helper/snapshot call log
  - stdout JSON parse result
- report evidence:
  - Step Contract Closure
  - Test Contract Closure
  - Closure Coverage
- 残リスク:
  - long-running live wait behavior remains covered by deterministic fake polling, not live GitHub.

#### ステップゲート（step gate）

- step reviewer gate:
  - reviewer: `code-reviewer`
  - review 範囲: wait CLI contract, usage validation, helper integration, stdout boundary
  - pass 条件: `review_status: pass`
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S02 target files only

### 実装ステップ S03 — snapshot and review JSON contract

- 振る舞いの目標:
  - read-only snapshot/review collectors が explicit trigger boundary、submitted PR review primary、selected full bodies、collection summaries を返す。
- design 参照:
  - `design.md` `fetch_pr_observation_snapshot.sh`, `fetch_pr_review_snapshot.sh`, `body-mode` 適用範囲
- 依存:
  - S02
- unblock:
  - S04
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_review_snapshot.sh`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh` only if minimal CI integration requires it
  - `tests/unit/infra/test_init_update.py`
- 計画済み契約:
  - scope:
    - explicit trigger metadata を最優先する。
    - normal wait/resume path では inferred trigger に依存しない。
    - direct snapshot diagnosis の inferred trigger は limitation 付きにする。
    - `codex_review.lifecycle`、selected reviews/comments body full text、collection summary、unresolved thread IDs/counts を返す。
  - テスト義務:
    - closure id: cl-006, cl-007, cl-008
    - coverage rationale: review completion と body output はこの issue の主要価値であり、fallback primary 誤判定、body-mode 誤適用、resume collection gap を red-required で固定する。
  - Red / 代替証跡:
    - red-required: 現行 collector の body-mode / inferred trigger / existing review payload では selected body non-application と collection summary が不足するため tests が失敗する。
  - 実装範囲:
    - allowed paths:
      - snapshot/review collector scripts
      - focused tests
    - forbidden changes:
      - write helper behavior
      - wait mode parser
      - skill docs
  - Green 検証:
    - fake issue comments / PR reviews / PR review comments / reviewThreads GraphQL fixtures
    - stdout JSON assertions
  - Refactor / cleanup ガードレール:
    - 目的: review JSON contract を明示的にする。
    - 禁止する広がり: arbitrary GitHub API / unsafe body fetching / selected body `--out` only。
  - report 証跡:
    - TDD evidence
    - Step/Test Closure
    - Closure Coverage
    - material heuristic decision があれば Decision Ledger
  - amendment trigger:
    - selected body full text が fixed read APIs だけで取得できない。
    - Codex author heuristic が design-level decision を必要とする。

#### 委任契約（delegation contract）

- 委任ロール:
  - `dev-coder`
- 入力 docs:
  - requirement, design, plan, S02 result, collector scripts/tests
- 許可 paths:
  - `fetch_pr_observation_snapshot.sh`
  - `lib/fetch_pr_review_snapshot.sh`
  - `lib/fetch_pr_checks_snapshot.sh` only if needed
  - `tests/unit/infra/test_init_update.py`
- 禁止 changes:
  - GitHub write helper
  - wait mode parser
  - docs/config/GitHub state/secrets
- 受け入れ条件:
  - cl-006, cl-007, cl-008
- 必須 tests:
  - submitted PR review primary tests
  - fallback-not-primary tests
  - selected body full text with body-mode variants
  - collection summary tests
- reviewer focus:
  - `code-reviewer`
- 必須出力:
  - changed files
  - verification result
  - representative JSON excerpt
  - Ledger Note or no material decision note
- 停止条件:
  - selected body requires unsafe follow-up API
  - body-mode cannot be scoped away from selected body
  - review thread collection cannot expose IDs/counts/reasons

#### 具体テストケース一覧

#### behavior slice execution

- Red / characterization:
  - cl-006, cl-007, cl-008 を対象に submitted PR review primary、fallback non-primary、selected body full text、collection summary tests を先に追加する。
- Implementation:
  - explicit trigger boundary、Codex review selection、selected body stdout inclusion、collection summary / limitations を read-only collectors に閉じる。
- Green:
  - fake issue comments / PR reviews / review comments / reviewThreads fixtures で primary completion、body-mode 非依存 body、resume auditability を確認する。
- Report:
  - representative JSON excerpt、heuristic limitation、Step/Test Closure、Closure Coverage を `report.md` に記録する。

- `tc-s03-001` acceptance: submitted PR review is primary completion
  - 前提: trigger boundary exists and fake Codex-authored submitted PR review is after boundary.
  - 操作: snapshot/review collector invocation with explicit trigger metadata.
  - 期待結果: `codex_review.lifecycle.completion_signal=submitted_pull_request_review`, high confidence, selected review id present.
  - 失敗検出: issue comment, reaction, or quiet window marked primary.
  - 検証方法: fake GitHub JSON fixture test.
  - 関連 closure id: cl-006

- `tc-s03-002` negative: fallback activity is not primary
  - 前提: only Codex issue comment/reaction/quiet window signal exists.
  - 操作: collector invocation.
  - 期待結果: fallback/timeout/human_gate with limitation or lower confidence, not primary submitted review completion.
  - 失敗検出: non-review object selected as primary completion.
  - 検証方法: fake fixture assertion.
  - 関連 closure id: cl-006

- `tc-s03-003` invariant: selected bodies ignore body-mode
  - 前提: selected Codex PR review and selected review comment have long body text.
  - 操作: collector or wait path with `--body-mode none`, `out-only`, and `trigger-window-truncated`.
  - 期待結果: `codex_review.selected_reviews[].body` and `codex_review.selected_review_comments[].body` contain full selected text in stdout JSON for each mode.
  - 失敗検出: selected body omitted, truncated, or only written under `--out`.
  - 検証方法: parametrized fake fixture test.
  - 関連 closure id: cl-007

- `tc-s03-004` negative: selected body collection failure is non-success/human-gate
  - 前提: selected review metadata exists but body is unavailable.
  - 操作: collector invocation.
  - 期待結果: item has `body_collection_status` and limitation; success is not claimed.
  - 失敗検出: empty body with success.
  - 検証方法: fake malformed/partial fixture test.
  - 関連 closure id: cl-007

- `tc-s03-005` acceptance: resume collection summary covers all families
  - 前提: before-boundary and after-boundary reviews/comments/threads exist; one thread unresolved.
  - 操作: collector with explicit trigger metadata.
  - 期待結果: fetched IDs, selected IDs, boundary-before excluded IDs/reasons, unresolved IDs/counts are present.
  - 失敗検出: timeout/resume gap cannot be audited.
  - 検証方法: fake paginated REST and GraphQL fixture test.
  - 関連 closure id: cl-008

#### ステップ完了契約（step closure contract）

- closure id:
  - cl-006, cl-007, cl-008
- close 条件:
  - explicit boundary selection、primary completion、selected body full text、collection summary、fallback limitations are covered.
- 検証 evidence:
  - focused pytest command
  - representative stdout JSON excerpt
- report evidence:
  - Step Contract Closure
  - Test Contract Closure
  - Closure Coverage
  - Decision Ledger if heuristic decision is material
- 残リスク:
  - Codex author login variance must be represented through evidence / confidence / limitations.

#### ステップゲート（step gate）

- step reviewer gate:
  - reviewer: `code-reviewer`
  - review 範囲: read-only collector JSON contract and tests
  - pass 条件: `review_status: pass`
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S03 target files only

### 実装ステップ S04 — wait final JSON, mixed status, timeout/resume, and output authority

- 振る舞いの目標:
  - trigger、CI、review、head state、timeout/resume、stdout/stderr、`--out` を final wait JSON に統合する。
- design 参照:
  - `design.md` JSON 契約、状態判定ルール、`--out` 境界
- 依存:
  - S01, S02, S03
- unblock:
  - S05a, S05b, S90, S99
- 対象ファイル:
  - `wait_pr_observation.sh`
  - `fetch_pr_observation_snapshot.sh` if final status fields must be surfaced there
  - `tests/unit/infra/test_init_update.py`
- 計画済み契約:
  - scope:
    - CI と review lifecycle を独立 classification し、`overall_status` / `recommended_next_action` で合流させる。
    - post-trigger / polling stale head は trigger metadata を保持し stale/non-success にする。
    - timeout / limit では `resume` metadata と command hint を返す。
    - stdout/stderr/`--out` authority 境界を維持する。
  - テスト義務:
    - closure id: cl-009, cl-010, cl-011, cl-012
    - coverage rationale: long-running wait の最終判断は agent の行動に直結するため mixed state / stale / timeout / output boundary を red-required にする。
  - Red / 代替証跡:
    - red-required: 現行 wait は trigger creation/resume hint/selected full body integration が不足するため tests が失敗する。
  - 実装範囲:
    - allowed paths:
      - wait/snapshot final integration
      - focused tests
    - forbidden changes:
      - new GitHub write surfaces
      - docs/package-only changes
      - selected body contract relaxation
  - Green 検証:
    - mixed-state fixtures
    - stale head phases
    - timeout/resume payload
    - `--out/result.json` equality
    - no `summary.md`
  - Refactor / cleanup ガードレール:
    - 目的: final status classification を読みやすく保つ。
    - 禁止する広がり: new state taxonomy を requirement なしに追加する。
  - report 証跡:
    - TDD evidence
    - Step/Test Closure
    - Closure Coverage
    - Discovered Tests
  - amendment trigger:
    - final status に requirement/design 未定義の状態が必要。
    - CI / review precedence が AC/EC と衝突する。

#### 委任契約（delegation contract）

- 委任ロール:
  - `dev-coder`
- 入力 docs:
  - requirement, design, plan, S01-S03 results, wait/snapshot scripts/tests
- 許可 paths:
  - `wait_pr_observation.sh`
  - `fetch_pr_observation_snapshot.sh`
  - `tests/unit/infra/test_init_update.py`
- 禁止 changes:
  - new GitHub write surfaces
  - docs/package-only changes
  - selected body contract relaxation
- 受け入れ条件:
  - cl-009, cl-010, cl-011, cl-012
- 必須 tests:
  - mixed CI/review state
  - stale after trigger/poll
  - stdout/stderr/out
  - timeout resume metadata
- reviewer focus:
  - `code-reviewer`
- 必須出力:
  - changed files
  - verification result
  - representative final JSON excerpts
  - Ledger Note or no material decision note
- 停止条件:
  - new status taxonomy が必要
  - CI/review precedence conflict
  - final stdout JSON cannot include selected body or resume metadata

#### 具体テストケース一覧

#### behavior slice execution

- Red / characterization:
  - cl-009, cl-010, cl-011, cl-012 を対象に mixed CI/review、stale after trigger、stdout/stderr/out、timeout resume metadata tests を先に追加する。
- Implementation:
  - helper / collector 結果を wait final JSON に統合し、CI と review lifecycle を独立に分類した上で final status と next action を決める。
- Green:
  - fake polling tests と stream/filesystem assertions で mixed state、stale non-success、resume command hint、`--out` equality、`summary.md` absence を確認する。
- Report:
  - representative final JSON excerpts、output authority evidence、Step/Test Closure、Closure Coverage を `report.md` に記録する。

- `tc-s04-001` acceptance: CI failed with review completed is non-merge-ready
  - 前提: fake CI failed and Codex submitted review exists.
  - 操作: wait invocation.
  - 期待結果: review completion is recorded but `overall_status` / next action is failed or human-gate, not merge-ready success.
  - 失敗検出: review completion masks CI failure.
  - 検証方法: wait final JSON assertion.
  - 関連 closure id: cl-009

- `tc-s04-002` acceptance: CI passed with review pending waits or times out as review pending
  - 前提: fake CI passed and no submitted Codex review exists before deadline.
  - 操作: wait invocation with short timeout.
  - 期待結果: timeout or pending review status with resume metadata; not passed.
  - 失敗検出: CI terminal alone marks success.
  - 検証方法: fake polling test.
  - 関連 closure id: cl-009, cl-012

- `tc-s04-003` negative: post-trigger head drift is stale with trigger metadata
  - 前提: helper posts successfully, then current head differs.
  - 操作: wait invocation.
  - 期待結果: final JSON includes trigger id/time and stale/non-success head phase; no delete mutation occurs.
  - 失敗検出: stale head marked success or trigger metadata lost.
  - 検証方法: fake call log and final JSON assertion.
  - 関連 closure id: cl-010

- `tc-s04-004` invariant: stdout/stderr/out authority
  - 前提: wait runs with `--out`.
  - 操作: wait invocation with progress mode variants.
  - 期待結果: stdout parses as one final JSON; stderr has bounded progress/diagnostics only; `--out/result.json` equals stdout; `summary.md` absent.
  - 失敗検出: authority split or generated summary.md.
  - 検証方法: filesystem and stream assertions.
  - 関連 closure id: cl-011

- `tc-s04-005` acceptance: timeout exposes resume command hint
  - 前提: CI or review remains pending until timeout and trigger metadata exists.
  - 操作: default wait with short timeout.
  - 期待結果: `resume.available=true`, trigger id/time/head SHA present, command hint uses `--trigger-mode resume`.
  - 失敗検出: timeout cannot be resumed without external API exploration.
  - 検証方法: final JSON assertion.
  - 関連 closure id: cl-012

#### ステップ完了契約（step closure contract）

- closure id:
  - cl-009, cl-010, cl-011, cl-012
- close 条件:
  - final wait JSON satisfies mixed status, stale, timeout/resume, stdout/stderr/out authority.
- 検証 evidence:
  - focused pytest command
  - representative final JSON excerpt
  - `--out/result.json` equality evidence
- report evidence:
  - Step Contract Closure
  - Test Contract Closure
  - Closure Coverage
- 残リスク:
  - live PR duration variance remains bounded by deterministic fake polling plus optional later PR observation evidence.

#### ステップゲート（step gate）

- step reviewer gate:
  - reviewer: `code-reviewer`
  - review 範囲: integrated wait behavior and tests
  - pass 条件: `review_status: pass`
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S04 target files only

### 実装ステップ S05a — skill docs contract

- 振る舞いの目標:
  - `github-pr-observation` skill docs が fixed trigger write + read-only observation contract を説明する。
- design 参照:
  - `design.md` `SKILL.md`, `--out` 境界, retired workflow constraints
- 依存:
  - S01-S04
- unblock:
  - S90
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
- 計画済み契約:
  - scope:
    - default `post-once`、explicit `resume`、fixed `@codex review` write、stdout/stderr/out authority、selected body stdout、retired workflow prohibition を文書化する。
  - テスト義務:
    - closure id: cl-014
    - coverage rationale: docs は user-facing public contract であり、skill が agent の実行判断を規定するため inspect-only + spec review で固定する。
  - Red / 代替証跡:
    - inspect-only: current `SKILL.md` still says read-only only; docs diff inspection is sufficient.
  - 実装範囲:
    - allowed paths:
      - `SKILL.md`
    - forbidden changes:
      - scripts/tests/config/workflow/canonical issue docs/GitHub state
  - Green 検証:
    - docs diff inspection
    - spec-reviewer docs/spec alignment
  - report 証跡:
    - Delegated Worker Evidence
    - Step/Test Closure
    - Closure Coverage
  - amendment trigger:
    - docs require behavior not implemented by S01-S04.

#### 委任契約（delegation contract）

- 委任ロール:
  - `doc-writer`
- 入力 docs:
  - requirement, design, plan, implemented behavior evidence
- 許可 paths:
  - `SKILL.md`
- 禁止 changes:
  - implementation scripts/tests/config/workflow/GitHub state/secrets
- 受け入れ条件:
  - cl-014
- 必須 verification:
  - docs diff inspection
  - spec-reviewer pass
- reviewer focus:
  - `spec-reviewer`
- 必須出力:
  - changed files
  - docs diff summary
  - unresolved docs risks
  - Ledger Note or no material decision note
- 停止条件:
  - docs update reveals missing behavior or broader workflow policy change

#### 具体テストケース一覧

#### behavior slice execution

- Inspect / characterization:
  - current `SKILL.md` が read-only only / external manual trigger 前提を残している箇所を確認する。
- Implementation:
  - default `post-once`、explicit `resume`、fixed `@codex review` write、stdout/stderr/out authority、selected body stdout、retired workflow prohibition を user-facing skill contract として更新する。
- Green:
  - docs diff inspection と spec-reviewer gate で requirement/design/implementation behavior と一致することを確認する。
- Report:
  - docs diff summary、Step/Test Closure、Closure Coverage、S90 入力を `report.md` に記録する。

- `tc-s05a-001` inspect-only: skill docs state new contract
  - 前提: S01-S04 の behavior contract と `design.md` の docs impact が確定している。
  - 操作: `SKILL.md` diff を inspect する。
  - 期待結果: docs match requirement/design and do not claim arbitrary write automation.
  - 失敗検出: default `post-once`、explicit `resume`、fixed `@codex review` write、stdout/stderr/out authority、selected body stdout、retired workflow prohibition のいずれかが欠ける、または arbitrary write automation を許可している。
  - 検証方法: docs inspection; spec-reviewer docs/spec alignment.
  - テスト不要理由: docs wording is a public contract artifact.
  - 記録先: report Delegated Worker Evidence / S90 docs impact evidence.
  - 関連 closure id: cl-014

#### ステップ完了契約（step closure contract）

- closure id:
  - cl-014
- close 条件:
  - `SKILL.md` aligns with implemented contract and retired workflows remain prohibited.
- 検証 evidence:
  - docs diff inspection
  - spec-reviewer result
- report evidence:
  - Step Contract Closure
  - Test Contract Closure
  - Closure Coverage

#### ステップゲート（step gate）

- step reviewer gate:
  - reviewer: `spec-reviewer`
  - review 範囲: skill docs/spec alignment
  - pass 条件: `review_status: pass`
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S05a target file only

### 実装ステップ S05b — shipped asset and package regression coverage

- 振る舞いの目標:
  - new helper が shipped source install-root、init/update layout、package inventory に含まれることを regression tests で固定する。
- design 参照:
  - `design.md` ディレクトリ / ファイル変更計画
- 依存:
  - S01-S04
- unblock:
  - S90, S99
- 対象ファイル:
  - `tests/unit/infra/test_init_update.py`
  - package/install inventory expectations
- 計画済み契約:
  - scope:
    - `trigger_codex_review.sh` の install/package inclusion を既存 install-root managed asset pattern で検証する。
  - テスト義務:
    - closure id: cl-013
    - coverage rationale: provider-side asset source と installed layout/package drift は shipped tool の回帰になるため red-required。
  - Red / 代替証跡:
    - red-required: helper script を package/install inventory に含める前に test が失敗する。
  - 実装範囲:
    - allowed paths:
      - package/install assertions in `tests/unit/infra/test_init_update.py`
    - forbidden changes:
      - implementation behavior scripts except test fixture stubs
      - docs/workflow/config/GitHub state/secrets
  - Green 検証:
    - focused package/install pytest selection
  - report 証跡:
    - TDD evidence
    - Step/Test Closure
    - Closure Coverage
  - amendment trigger:
    - install-root source authority is insufficient and installer/package behavior needs design change.

#### 委任契約（delegation contract）

- 委任ロール:
  - `dev-coder`
- 入力 docs:
  - requirement, design, plan, current package/install tests
- 許可 paths:
  - `tests/unit/infra/test_init_update.py`
- 禁止 changes:
  - implementation scripts/docs/config/workflow/GitHub state/secrets
- 受け入れ条件:
  - cl-013
- 必須 tests:
  - focused install/package pytest selection
- reviewer focus:
  - `code-reviewer`
- 必須出力:
  - changed files
  - verification result
  - package/install assertion summary
  - Ledger Note or no material decision note
- 停止条件:
  - package inclusion requires installer source authority change outside design

#### 具体テストケース一覧

#### behavior slice execution

- Red / characterization:
  - cl-013 を対象に helper script が source install-root / installed layout / package inventory から漏れた場合に失敗する test を先に追加する。
- Implementation:
  - package/install assertions を既存 install-root managed asset pattern に合わせて更新する。
- Green:
  - focused package/install pytest selection で source、installed layout、package inventory の inclusion を確認する。
- Report:
  - package/install assertion summary、Step/Test Closure、Closure Coverage を `report.md` に記録する。

- `tc-s05b-001` acceptance: helper script is installed and packaged
  - 前提: source install-root asset tree includes `trigger_codex_review.sh`.
  - 操作: existing init/update/package inventory tests run.
  - 期待結果: source, installed layout, wheel/sdist/package inventories include the helper.
  - 失敗検出: hidden asset added in source but absent from install/package.
  - 検証方法: focused pytest around install-root managed skill inventory.
  - 関連 closure id: cl-013

#### ステップ完了契約（step closure contract）

- closure id:
  - cl-013
- close 条件:
  - install/package tests cover new helper.
- 検証 evidence:
  - focused pytest command
- report evidence:
  - Step Contract Closure
  - Test Contract Closure
  - Closure Coverage

#### ステップゲート（step gate）

- step reviewer gate:
  - reviewer: `code-reviewer`
  - review 範囲: package/install test diff and source authority
  - pass 条件: `review_status: pass`
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S05b target tests only

### ドキュメント影響の解消ステップ S90（docs impact resolution / docs refresh）

- 対象:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - docs / templates / README / workflow / migration notes if implementation or review identifies direct impact
- 対応:
  - S05a の `SKILL.md` update を docs impact として確認する。
  - 追加 docs impact がない場合は no-op evidence を report に残す。
  - 追加 impact がある場合は doc-writer step と plan amendment / re-review 要否を判断する。
- doc update owner:
  - `doc-writer` when updates are required
- spec/doc review:
  - reviewer: `spec-reviewer`
  - pass 条件: docs が requirement / design / plan と整合し、未解決の必須 docs 影響が残っていない
- closure id:
  - cl-015

#### 委任契約（delegation contract）

- 委任ロール:
  - `doc-writer` if additional docs updates are required; otherwise N/A with inspect-only evidence.
- 入力 docs:
  - requirement, design, plan, implemented behavior evidence, S05a docs diff
- 許可 paths:
  - impacted docs only
- 禁止 changes:
  - implementation scripts/tests/config/GitHub state/secrets
- 受け入れ条件:
  - cl-015
- 必須 verification:
  - docs diff inspection
  - spec-reviewer docs/spec alignment
- 必須出力:
  - changed files or approved no-op rationale
  - checked docs surfaces
  - verification result
  - unresolved docs risks
  - report update inputs for Docs Impact Resolution and Closure Coverage
  - Ledger Note or no material decision note
- 停止条件:
  - docs impact requires new requirement/design decision or wider workflow policy change

#### 具体テストケース一覧

#### behavior slice execution

- Inspect / characterization:
  - S01-S05b の diff と docs surface を見て、追加 docs/templates/README/workflow/migration notes への直接影響があるか確認する。
- Implementation:
  - 追加 docs impact があれば doc-writer step として更新し、no-op の場合は根拠を `report.md` に残す。
- Green:
  - docs inspection と spec-reviewer gate で未記録の docs impact がないことを確認する。
- Report:
  - Docs Impact Resolution、Closure Coverage、Final Spec Review Gate input を `report.md` に記録する。

- `tc-s90-001` inspect-only: docs impact is resolved
  - 前提: S01-S05b の実装差分と `SKILL.md` docs diff が存在する。
  - 操作: docs / templates / README / workflow / skill / migration notes の直接影響を点検する。
  - 期待結果: no required docs impact remains unrecorded; skill docs align with implemented contract.
  - 失敗検出: user-facing contract に影響する docs surface が未更新または no-op evidence 未記録のまま残る。
  - 検証方法: docs surface inspection; spec-reviewer docs/spec alignment.
  - テスト不要理由: docs impact is a review/inspection gate.
  - 記録先: report S90 docs impact evidence and Final Spec Review Gate input.
  - 関連 closure id: cl-015

#### ステップ完了契約（step closure contract）

- closure id:
  - cl-015
- close 条件:
  - docs impact is updated or explicitly no-op with evidence and spec-reviewer pass.
- 検証 evidence:
  - docs inspection / spec-reviewer result
- report evidence:
  - Docs Impact Resolution
  - Closure Coverage

#### ステップゲート（step gate）

- step reviewer gate:
  - reviewer: `spec-reviewer`
  - review 範囲: docs impact and spec alignment
  - pass 条件: `review_status: pass`
- commit / no-op gate:
  - closure 状態: committed or approved-no-op
  - commit 範囲: S90 docs-only diff or no-op evidence

### 最終品質ゲートステップ S99（final quality gate）

- branch diff 範囲:
  - S01-S05b and S90 issue-wide diff plus report evidence.
- 必須 validation:
  - focused pytest selections for helper, wait mode, snapshot/review contract, output boundaries, install/package inventory.
  - broader relevant lane if focused tests indicate shared regression risk, likely `uv run pytest tests/unit/infra/test_init_update.py`.
  - `./spec-dock/scripts/spec-dock validate`
  - `git diff --check`
  - `git status --short`
- final QA gate:
  - reviewer: `qa-reviewer`
  - 範囲: Issue 全体の obligation coverage と integration test 要否。`body-mode` selected-body obligation を重点確認する。
  - pass 条件: reviewer pass
- final code review ゲート:
  - reviewer: issue-wide `code-reviewer`
  - 範囲: integrated script/test/package diff、fixed write boundary、read-only collector boundary、failure modes、保守性
  - pass 条件: `review_status: pass`
- final spec review ゲート:
  - reviewer: `spec-reviewer`
  - 範囲: requirement / design / plan / report / implementation / tests / docs 整合
  - pass 条件: reviewer pass
- final commit gate:
  - commit 範囲: final report ledger / cleanup after final gates
  - final report ledger: closure coverage、reviewer gates、validation results、commit/no-op evidence
  - post-commit external evidence destination: final response / PR body / issue comment as applicable

#### 委任契約（delegation contract）

- 委任ロール:
  - `qa-reviewer`
  - issue-wide `code-reviewer`
  - final `spec-reviewer`
- 入力 docs:
  - requirement, design, plan, report
  - S01-S05b and S90 implementation diff
  - validation command output
- 許可 paths:
  - reviewer は read-only review を原則とする。
  - reviewer finding に対する bounded follow-up は該当 step の allowed paths または final report ledger に限定する。
- 禁止 changes:
  - new scope behavior
  - GitHub state/secrets
  - reviewer pass なしの issue completion claim
- 受け入れ条件:
  - cl-016
- 必須 verification:
  - final validation commands
  - closure coverage inspection
  - fresh reviewer pass for QA, code, and spec gates
- 必須出力:
  - validation command results
  - QA / code / spec reviewer verdict summaries and JSON paths when available
  - closure coverage gaps or explicit no-gap statement
  - unresolved risks
  - final report ledger update inputs
  - Ledger Note or no material decision note
- 停止条件:
  - required closure evidence missing
  - final reviewer non-pass
  - validation failure not fixed or explicitly classified

#### 具体テストケース一覧

#### behavior slice execution

- Manual / validation:
  - S01-S05b and S90 の closure evidence、focused tests、`spec-dock validate`、`git diff --check`、`git status --short` を集約する。
- Review:
  - qa-reviewer、issue-wide code-reviewer、final spec-reviewer を fresh pass まで実行する。
- Report:
  - Final QA Gate、Final Code Review Gate、Final Spec Review Gate、Final Quality Gate、Closure Coverage、commit/no-op evidence を `report.md` に記録する。

- `tc-s99-001` manual-required: final integrated gate
  - 前提: S01-S05b and S90 closure evidence exists.
  - 操作: run final validation and delegated final reviews.
  - 期待結果: QA, code, and spec reviews are all fresh passed in report evidence before completion claims.
  - 失敗検出: step-local pass hides missing integrated behavior or docs/test mismatch.
  - 検証方法: report gate evidence plus commands above.
  - 関連 closure id: cl-016

#### ステップ完了契約（step closure contract）

- closure id:
  - cl-016
- close 条件:
  - final QA / code / spec gates pass.
  - all required closure IDs have report evidence.
  - validation commands pass or failures are fixed / explicitly classified.
- report evidence:
  - Final QA Gate
  - Final Code Review Gate
  - Final Spec Review Gate
  - Final Quality Gate
  - Closure Coverage

#### ステップゲート（step gate）

- step reviewer gate:
  - reviewer: `qa-reviewer`, issue-wide `code-reviewer`, final `spec-reviewer`
  - pass 条件: all fresh pass
  - re-review rule: 指摘を修正し、該当 reviewer を pass まで再実行
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: final report/cleanup after final gates

## 未確定事項

- なし。
  - Codex author login variance and GitHub response field variance are implementation verification risks handled through `confidence`, `limitations`, and fake `gh` fixtures unless they force requirement/design amendment.

## 最終完了条件

- AC/EC 達成:
  - cl-001 through cl-016 are recorded in report Step/Test Closure and Closure Coverage.
- docs 影響解決:
  - S05a and S90 pass with docs/spec alignment evidence.
- 全 implementation step 完了:
  - S01, S02, S03, S04, S05a, S05b, S90, S99 are committed or justified approved-no-op.
- final quality gate pass:
  - qa-reviewer: pass
  - issue-wide code-reviewer: pass
  - final spec-reviewer: pass
- validation:
  - focused tests pass
  - required broader lane pass or justified by reviewer
  - `./spec-dock/scripts/spec-dock validate` pass
  - `git diff --check` pass
- delivery:
  - report ledger records reviewer gates, validation, closure coverage, and commit/no-op evidence before issue finish.
