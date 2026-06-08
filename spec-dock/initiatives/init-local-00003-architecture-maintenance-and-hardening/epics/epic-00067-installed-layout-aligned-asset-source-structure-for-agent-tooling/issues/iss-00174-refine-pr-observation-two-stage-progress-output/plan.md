---
種別: 実装計画書（Issue）
ID: "iss-00174"
タイトル: "Refine PR Observation Two Stage Progress Output"
関連GitHub: ["#174"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-08"
依存: ["requirement.md", "design.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00174 Refine PR Observation Two Stage Progress Output — 実装計画（実行契約 / Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001: CI running 中の detailed progress。
  - AC-002: CI check count progress による quiet reset。
  - AC-003: CI passed 後の compact progress。
  - AC-004: Review observing 中の trigger-window `comments=N` progress。
  - AC-005: Review count / thread progress による quiet reset。
  - AC-006: Review human gate compact progress の最小 count。
  - AC-007: `--progress none` の stderr 抑止と stdout JSON 維持。
  - AC-008: stdout/stderr boundary と forbidden detail leakage 防止。
  - AC-009: optional field drop と `limit=none|truncated`。
  - AC-010: provider / dogfooding mirror parity。
- EC:
  - EC-001: zero-check / metadata 未出揃い。
  - EC-002: skipped / neutral check runs。
  - EC-003: failed check run compact hint。
  - EC-004: old unresolved thread と current `comments=N` の分離。
  - EC-005: trigger unknown / timestamp unavailable。
  - EC-006: timeout / fallback payload。
  - EC-007: raw review body text only の安定性。
  - EC-008: progress line length budget。
- 制約:
  - stdout final JSON authority 維持。
  - progress 専用 GitHub API call 追加なし。
  - review body、URL、reviewer name、workflow name、job name、failed step detail、P1/P2 text interpretation を progress line に出さない。
  - 旧 `pr-monitor` sub-agent や旧 Codex-only review skill を復活させない。

## 依存関係から導く実装順序
- 依存関係の参照元:
  - `design.md` の「依存関係分析」「インターフェース契約」「要件 → 設計マッピング」「テスト戦略」。
  - `discussions/20260608t044318z-disc-implementation-planner-progress-line-two-stage-plan.md`。
- 順序ルール:
  - tests で期待 behavior を固定してから provider 実装を行う。
  - provider source を先に green にし、dogfooding mirror は provider 結果の exact parity として同期する。
  - docs impact / final quality gate は runtime 実装完了後に独立して閉じる。
- step 依存サマリー:
  - S01:
    - 依存: approved `requirement.md` / `design.md`。
    - unblock: S02 / S03 の Red contract。
    - 対象ファイル: `tests/unit/infra/test_init_update.py`。
  - S02:
    - 依存: S01 の Red / characterization。
    - unblock: S03 / S04。
    - 対象ファイル: provider `wait_pr_observation.sh`。
  - S03:
    - 依存: S01 の quiet reset tests、S02 の progress helper。
    - unblock: stable wait semantics。
    - 対象ファイル: provider `wait_pr_observation.sh`。
  - S04:
    - 依存: provider behavior green。
    - unblock: shipped asset parity。
    - 対象ファイル: mirror `wait_pr_observation.sh`。
  - S90:
    - 依存: runtime diff 確定。
    - unblock: final spec review。
    - 対象ファイル: docs / templates / README / workflow / skill text if needed。
  - S99:
    - 依存: S01-S04 / S90 closure。
    - unblock: PR delivery / merge preparation / issue finish。

## ステップ一覧
- S01:
  - 観測可能な振る舞い: current implementation に対して progress / quiet reset / boundary / truncation の Red または characterization が固定される。
  - 依存: approved requirement/design。
  - unblock: S02, S03。
  - 対象ファイル: `tests/unit/infra/test_init_update.py`。
  - 閉じる要件: AC-001..AC-009, EC-001..EC-008 の test obligations。
  - レビューゲート: code-reviewer。
- S02:
  - 観測可能な振る舞い: provider wait script が two-stage progress line を render する。
  - 依存: S01。
  - unblock: S03, S04。
  - 対象ファイル: `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`。
  - 閉じる要件: AC-001, AC-003, AC-004, AC-006, AC-007, AC-008, AC-009, EC-001..EC-006, EC-008。
  - レビューゲート: code-reviewer。
- S03:
  - 観測可能な振る舞い: CI / review count progress が semantic fingerprint と quiet reset に反映される。
  - 依存: S01, S02。
  - unblock: S04。
  - 対象ファイル: provider `wait_pr_observation.sh`。
  - 閉じる要件: AC-002, AC-005, EC-007。
  - レビューゲート: code-reviewer。
- S04:
  - 観測可能な振る舞い: provider / mirror scripts が一致し、shell syntax / parity が通る。
  - 依存: S02, S03。
  - unblock: S90, S99。
  - 対象ファイル: `.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`。
  - 閉じる要件: AC-010。
  - レビューゲート: code-reviewer。
- S90:
  - 観測可能な振る舞い: docs impact が更新済みまたは approved-no-op として閉じる。
  - レビューゲート: spec-reviewer。
- S99:
  - 観測可能な振る舞い: issue-wide quality gates が pass し、report closure が実装証跡を持つ。
  - レビューゲート: qa-reviewer, code-reviewer, spec-reviewer。

## 要件 ↔ ステップ対応
- AC-001 -> S01, S02
- AC-002 -> S01, S03
- AC-003 -> S01, S02
- AC-004 -> S01, S02
- AC-005 -> S01, S03
- AC-006 -> S01, S02
- AC-007 -> S01, S02
- AC-008 -> S01, S02
- AC-009 -> S01, S02
- AC-010 -> S04
- EC-001 -> S01, S02
- EC-002 -> S01, S02
- EC-003 -> S01, S02
- EC-004 -> S01, S02
- EC-005 -> S01, S02
- EC-006 -> S01, S02
- EC-007 -> S01, S03
- EC-008 -> S01, S02

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| 識別子（ID） | ステップ（step） | スライス（slice） | 種別（type） | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル（evidence level） | クロージャ証跡（closure evidence） |
|---|---|---|---|---|---|---|---|---|---|---|
| cl-ci-detail | S01/S02 | CI detailed progress | acceptance | AC-001 | stderr に `pr_obs ci=running checks=2/4 ok=2 run=2 pend=0 fail=0` が出る | total=4, success=2, running=2 | coarse status only regression | yes | red-required | report Step/Test Closure |
| cl-ci-quiet | S01/S03 | CI quiet reset | acceptance | AC-002 | `checks=0/3 -> 1/3 -> 2/3 -> 3/3` で `latest_change_poll` と `quiet` が更新される | same coarse `ci=running` | quiet reset drift | yes | red-required | report Step/Test Closure |
| cl-ci-compact | S01/S02 | CI compact | acceptance | AC-003 | terminal success は `ci=passed` を出し通常 `checks=` を省略 | passed CI payload | noisy completed progress | yes | red-required | report Step/Test Closure |
| cl-review-detail | S01/S02 | Review detailed progress | acceptance | AC-004 | `comments=0 -> 1 -> 2` が trigger-window count として出る | current Codex review signals | historical comments noise | yes | red-required | report Step/Test Closure |
| cl-review-quiet | S01/S03 | Review quiet reset | acceptance | AC-005 | comments / threads / unresolved count 変化で `latest_change_poll` が更新される | review progress count change | review progress ignored | yes | red-required | report Step/Test Closure |
| cl-review-human-gate | S01/S02 | Review human gate compact | acceptance | AC-006 | human gate compact で `comments=N`、thread gate なら `threads=N unresolved=N` を残す | unresolved / changes_requested stable payload | opaque human gate | yes | red-required | report Step/Test Closure |
| cl-progress-none | S01/S02 | Progress disabled | acceptance | AC-007 | `--progress none` は stderr empty、stdout parseable final JSON | progress none invocation | stdout/stderr mixing | yes | red-required | report Step/Test Closure |
| cl-boundary | S01/S02 | Output boundary / leakage | negative | AC-008 | stdout は final JSON のみ、stderr に body / URL / name / workflow / job / failed step detail / P1/P2 が出ない | payload with forbidden details | sensitive/noisy progress leakage | yes | red-required | report Step/Test Closure |
| cl-truncation | S01/S02 | Line budget | acceptance | AC-009, EC-008 | normal `limit=none`; optional drop 時だけ `limit=truncated`; token途中 slice を通常経路にしない | many optional fields | broken key/value progress | yes | red-required | report Step/Test Closure |
| cl-zero-check | S01/S02 | Zero check / metadata not ready | edge | EC-001 | zero-check grace / pending / limitation semantics を壊さず false passed にしない | check runs 0 件または metadata 未出揃い | premature passed regression | yes | red-required | report Step/Test Closure |
| cl-skipped-neutral | S01/S02 | Skipped / neutral checks | edge | EC-002 | skipped / neutral は merge を妨げない terminal outcome として `done` / `ok` に含める | skipped / neutral check runs | skipped treated as failed/unknown | yes | red-required | report Step/Test Closure |
| cl-failed-compact | S01/S02 | Failed CI compact hint | edge | EC-003 | compact 後は `ci=failed fail=N` を出し、workflow / job / step detail は stderr に出さない | failed check run payload | noisy or under-informative failure progress | yes | red-required | report Step/Test Closure |
| cl-old-thread-isolation | S01/S02 | Old unresolved thread isolation | edge | EC-004 | old unresolved thread だけでは `comments=N` を増やさないが final review status / human gate は維持する | old unresolved thread, no new trigger-window comment | historical thread counted as new progress | yes | red-required | report Step/Test Closure |
| cl-trigger-unknown | S01/S02 | Trigger unknown safety | edge | EC-005 | trigger timestamp 不明時は古い comments を新規 progress として数えず limitation を保持する | trigger unknown / timestamp unavailable | unsafe progress count inflation | yes | red-required | report Step/Test Closure |
| cl-timeout-rendering | S01/S02 | Timeout / fallback rendering | edge | EC-006 | timeout / fallback payload でも stderr rendering が stdout final JSON を壊さない | snapshot timeout near deadline | broken final JSON on timeout | yes | red-required | report Step/Test Closure |
| cl-raw-body-stability | S01/S03 | Raw body only stability | edge | EC-007 | raw review body text だけを semantic fingerprint / progress reset の主因にしない | same semantic review, changed raw body text only | body text churn resets quiet | yes | red-required | report Step/Test Closure |
| cl-provider-mirror-parity | S04 | Shipped asset parity | acceptance | AC-010 | provider / mirror `wait_pr_observation.sh` が exact match | both script paths | dogfooding drift | yes | inspect-only | `diff -u` evidence |
| cl-bash-compat | S04 | Shell syntax | compatibility | design compatibility | provider / mirror とも `bash -n` pass、Bash 3.2 非互換を入れない | both script paths | macOS shell regression | yes | inspect-only | `bash -n` evidence |
| cl-docs-impact | S90 | Docs impact | docs-impact | constraints | docs impact が更新済みまたは approved-no-op | docs/templates/README/workflow/skill scan | stale public contract | yes | inspect-only | report docs gate |
| cl-final-quality | S99 | Final gates | quality | all AC/EC | final QA / code / spec reviewer が pass | whole issue diff | incomplete closure | yes | manual-required | final report gates |

## レビュー / QA ゲート方針
- RG1 step review:
  - 実施タイミング: S01-S04 の実装差分が green になった後。
  - reviewer: code-reviewer。
  - pass 条件: review_status: pass。
  - focus: progress projection correctness、quiet reset semantics、stdout/stderr boundary、forbidden leakage、timeout / zero-check / stale review regression、provider/mirror parity。
- SG90 docs review:
  - reviewer: spec-reviewer。
  - pass 条件: docs impact updated または approved-no-op が requirement/design/plan と整合する。
- QG1 final QA:
  - reviewer: qa-reviewer。
  - 範囲: issue 全体の obligation coverage、missing high-value tests、integration test 要否。
- CR99 final code review:
  - reviewer: code-reviewer。
  - 範囲: issue-wide integrated diff。
- SG99 final spec review:
  - reviewer: spec-reviewer。
  - 範囲: requirement / design / plan / report / implementation / tests / docs alignment。

## 実行ルール（全ステップ共通）
- S01-S04 は runtime script、tests、shipped asset に触れるため dev-coder に委任する。
- main orchestrator は source / test を直接編集しない。
- worker は provider source first で作業し、mirror は provider green 後に同期する。
- 新しい GitHub API call、raw `gh` args、stdout final JSON authority 変更が必要になった場合は stop し、report に blocker / plan amendment trigger として記録する。
- implementation 中に closure id の追加 / 削除 / 意味変更が必要になった場合は plan amendment と fresh spec-reviewer を先に行う。
- observed results、worker note、reviewer verdict、closure evidence は `report.md` に記録する。

## 実装ステップ

### 実装ステップ S01 — Progress test harness and Red obligations
- 振る舞いの目標（behavior goal）:
  - two-stage progress、quiet reset、boundary、truncation、parity の期待を focused tests で固定する。
- design 参照:
  - `design.md` の「テスト戦略」「要件 / 例外 -> 検証マッピング」。
- 依存:
  - approved requirement/design。
- unblock:
  - S02, S03。
- 対象ファイル:
  - `tests/unit/infra/test_init_update.py`
- 計画済み契約（planned contract）:
  - scope:
    - 既存 PR observation wait / review test 近傍に focused tests または fixture helper を追加する。
  - テスト義務（test obligation）:
    - closure id:
      - cl-ci-detail
      - cl-ci-quiet
      - cl-ci-compact
      - cl-review-detail
      - cl-review-quiet
      - cl-review-human-gate
      - cl-progress-none
      - cl-boundary
      - cl-truncation
      - cl-zero-check
      - cl-skipped-neutral
      - cl-failed-compact
      - cl-old-thread-isolation
      - cl-trigger-unknown
      - cl-timeout-rendering
      - cl-raw-body-stability
  - Red / 代替証跡の要件:
    - red-required:
      - current coarse `progress_line()` に対して新規 progress fields / quiet reset tests が失敗することを確認する。
    - covered-existing:
      - trigger-window collector behavior が既存 test で十分に検出できる場合は、その既存 test と理由を report に記録する。
    - inspect-only:
      - test placement が既存 harness に沿っていることを diff inspection で確認する。
  - 実装範囲（implementation scope）:
    - allowed paths:
      - `tests/unit/infra/test_init_update.py`
    - forbidden changes:
      - runtime script、docs、templates、agent config、GitHub workflow。
  - Green 検証:
    - command / inspection:
      - `uv run pytest tests/unit/infra/test_init_update.py -k "pr_observation_wait or pr_review or pr_observation" -q`
  - Refactor / cleanup ガードレール:
    - helper extraction は fixture duplication を減らす場合のみ。
    - unrelated test rewrites は禁止。
  - closure 証跡要件:
    - report の Step Contract Closure、Test Contract Closure、Closure Coverage に Red / characterization を記録する。
  - amendment trigger:
    - Existing harness で trigger-window review count を表現できない。
    - closure id の意味を変える必要がある。

#### 委任契約（delegation contract）
- 委任ロール（delegated role）:
  - dev-coder
- 入力 docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - current test file
- 許可 paths:
  - `tests/unit/infra/test_init_update.py`
- 禁止 changes:
  - implementation files / docs / workflow / agent config。
- 受け入れ条件:
  - S01 closure ids の Red / characterization evidence が report に記録可能。
- 必須 tests:
  - focused pytest command above。
- reviewer focus:
  - code-reviewer: test sensitivity、fixture clarity、overfit risk。
- 必須出力:
  - changed files、Red/characterization result、unresolved risks、report evidence note。
- 停止条件:
  - test harness が必要 behavior を表現できない。

#### 具体テストケース一覧
- `tc-s01-001` acceptance: CI detailed progress fields
  - 前提: fake snapshot または fake `gh` harness が total=4 / success=2 / running=2 の CI snapshot を返す。
  - 操作: `wait_pr_observation.sh --progress stderr-summary` を実行する。
  - 期待結果: `pr_obs`, `ci=running`, `checks=2/4`, `ok=2`, `run=2`, `pend=0`, `fail=0`。
  - 失敗検出: coarse `ci=running` だけを出す現行 progress line では失敗する。
  - 検証方法: `tests/unit/infra/test_init_update.py` の focused pytest。
  - 関連 closure id: cl-ci-detail
- `tc-s01-002` acceptance: CI count quiet reset
  - 前提: 複数 poll の fake snapshots が `checks=0/3 -> 1/3 -> 2/3 -> 3/3` と進む。
  - 操作: wait loop を same coarse `ci=running` のまま実行する。
  - 期待結果: `wait.latest_change_poll` と stderr `quiet` が最後の count 変化を反映。
  - 失敗検出: CI status だけを fingerprint する実装では quiet が伸び続ける。
  - 検証方法: focused pytest で final JSON と stderr progress を assert する。
  - 関連 closure id: cl-ci-quiet
- `tc-s01-003` acceptance: review comments progress
  - 前提: `@codex review` trigger 後の current review signals が `0 -> 1 -> 2` と増える。
  - 操作: review observing 中に複数 poll する。
  - 期待結果: stderr に `comments=0`, `comments=1`, `comments=2`。
  - 失敗検出: review status だけを出す progress line や historical comments を数える実装を検出する。
  - 検証方法: trigger-window fixture を使う focused pytest。
  - 関連 closure id: cl-review-detail
- `tc-s01-004` negative: forbidden stderr leakage
  - 前提: payload に body / URL / names / workflow / job / failed step detail がある。
  - 操作: `--progress stderr-summary` で progress line を出す。
  - 期待結果: progress line に出ない。
  - 失敗検出: renderer が raw payload detail をそのまま流す回帰を検出する。
  - 検証方法: stderr forbidden-token assertion。
  - 関連 closure id: cl-boundary
- `tc-s01-005` edge: CI edge outcomes
  - 前提: zero-check、skipped / neutral、failed check run の fixtures を用意する。
  - 操作: 各 fixture で wait script を実行する。
  - 期待結果: zero-check は false passed にならず、skipped / neutral は `done` / `ok` に含まれ、failed compact は `ci=failed fail=N` に留まる。
  - 失敗検出: skipped を失敗扱いする、zero-check を即 passed にする、failed detail を stderr に漏らす回帰を検出する。
  - 検証方法: focused pytest。
  - 関連 closure id: cl-zero-check, cl-skipped-neutral, cl-failed-compact
- `tc-s01-006` edge: review trigger and historical thread isolation
  - 前提: old unresolved thread があるが、trigger-window 後の新規 Codex review comment はない fixture と、trigger timestamp 不明 fixture を用意する。
  - 操作: review observing / human gate の wait loop を実行する。
  - 期待結果: old thread だけでは `comments=N` は増えず、trigger unknown では古い comments を新規 progress として数えない。
  - 失敗検出: historical thread / old PR-wide comments を current progress に混入する回帰を検出する。
  - 検証方法: focused pytest。
  - 関連 closure id: cl-old-thread-isolation, cl-trigger-unknown
- `tc-s01-007` edge: timeout and raw-body-only stability
  - 前提: snapshot timeout / fallback payload fixture と、raw review body text だけが変わる fixture を用意する。
  - 操作: wait script を deadline 近傍または repeated poll で実行する。
  - 期待結果: timeout / fallback でも stdout final JSON は parseable で、raw body text only change は progress reset authority にならない。
  - 失敗検出: timeout rendering が stdout を壊す、body text churn が quiet reset を誘発する回帰を検出する。
  - 検証方法: focused pytest または既存 raw-body stability test の characterization。
  - 関連 closure id: cl-timeout-rendering, cl-raw-body-stability

#### ステップ完了契約（step closure contract）
- closure id:
  - cl-ci-detail, cl-ci-quiet, cl-ci-compact, cl-review-detail, cl-review-quiet, cl-review-human-gate, cl-progress-none, cl-boundary, cl-truncation, cl-zero-check, cl-skipped-neutral, cl-failed-compact, cl-old-thread-isolation, cl-trigger-unknown, cl-timeout-rendering, cl-raw-body-stability
- close 条件:
  - Red / characterization evidence と focused pytest result が report に記録される。
- 検証 evidence:
  - focused pytest result。
- report evidence:
  - TDD / Red / Refactor Evidence、Step Contract Closure、Test Contract Closure、Closure Coverage。
- 残リスク:
  - Red tests の追加だけでは issue complete ではない。

#### ステップゲート（step gate）
- step reviewer gate:
  - reviewer: code-reviewer
  - review 範囲: S01 test diff
  - pass 条件: review_status: pass
  - re-review rule: fail findings を dev-coder に戻して pass まで再実行
- commit / no-op gate:
  - closure 状態: committed
  - commit 範囲: S01 test diff または後続実装と同一 commit でもよいが、report で scope を明記する。

### 実装ステップ S02 — Provider progress projection and two-stage rendering
- 振る舞いの目標（behavior goal）:
  - provider wait script が `progress_state` / renderer により detailed / compact progress line を出す。
- design 参照:
  - `design.md` の「インターフェース契約」「シーケンス差分」。
- 依存:
  - S01。
- unblock:
  - S03, S04。
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
- 計画済み契約（planned contract）:
  - scope:
    - `ci_progress_counts`, `review_progress_counts`, `progress_state`, `render_progress_line` を provider Python block に追加または相当の小 helper として実装する。
    - `progress_line()` の coarse rendering と `limit=ok` を置き換える。
  - テスト義務:
    - closure id:
      - cl-ci-detail
      - cl-ci-compact
      - cl-review-detail
      - cl-review-human-gate
      - cl-progress-none
      - cl-boundary
      - cl-truncation
      - cl-zero-check
      - cl-skipped-neutral
      - cl-failed-compact
      - cl-old-thread-isolation
      - cl-trigger-unknown
      - cl-timeout-rendering
  - Red / 代替証跡の要件:
    - S01 の Red tests を Green にする。
  - 実装範囲:
    - allowed paths:
      - provider `wait_pr_observation.sh`
    - forbidden changes:
      - collectors、mirror、tests 以外の docs/config。
      - new GitHub API call / raw `gh` args / stdout JSON authority change。
  - Green 検証:
    - `uv run pytest tests/unit/infra/test_init_update.py -k "pr_observation_wait or pr_review or pr_observation" -q`
    - `bash -n src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
  - Refactor / cleanup ガードレール:
    - helper の責務分離のみ。collector への premature abstraction は禁止。
  - amendment trigger:
    - existing payload から `comments=N` を導出できない。
    - line budget のため必須 field を落とす必要がある。

#### 委任契約（delegation contract）
- 委任ロール:
  - dev-coder
- 入力 docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `discussions/20260608t043253z-disc-system-architect-progress-line-two-stage-design.md`
  - provider `wait_pr_observation.sh`
  - `tests/unit/infra/test_init_update.py`
- 許可 paths:
  - provider `wait_pr_observation.sh`
- 禁止 changes:
  - mirror direct redesign、collector expansion without stop/report decision、docs/config/workflow。
- 受け入れ条件:
  - cl-ci-detail, cl-ci-compact, cl-review-detail, cl-review-human-gate, cl-progress-none, cl-boundary, cl-truncation, cl-zero-check, cl-skipped-neutral, cl-failed-compact, cl-old-thread-isolation, cl-trigger-unknown, cl-timeout-rendering が pass する。
- 必須 tests:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "pr_observation_wait or pr_review or pr_observation" -q`
  - `bash -n src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
- reviewer focus:
  - code-reviewer: projection correctness、forbidden leakage、stdout/stderr boundary、truncation。
- 必須出力:
  - changed files
  - verification result
  - closure ids satisfied / not satisfied
  - report evidence note
  - Ledger Note or `No material implementation decisions beyond the approved plan.`
  - unresolved risks
- 停止条件:
  - design contradiction
  - required external API expansion
  - required stdout final JSON schema authority change
  - progress line must include forbidden detail to satisfy tests
  - allowed path outside provider script becomes necessary

#### 具体テストケース一覧
- `tc-s02-001` Green: detailed and compact rendering passes
  - 前提: S01 の CI / review detailed fixtures と terminal passed / human-gate fixtures が存在する。
  - 操作: provider `wait_pr_observation.sh` の実装後に focused pytest を実行する。
  - 期待結果: running / observing 中は detailed counters、terminal / stable 後は compact status が出る。
  - 失敗検出: renderer が二段階表示へ切り替わらない、または required count を落とす回帰を検出する。
  - 検証方法: `uv run pytest tests/unit/infra/test_init_update.py -k "pr_observation_wait or pr_review or pr_observation" -q`。
  - 関連 closure id: cl-ci-detail, cl-ci-compact, cl-review-detail, cl-review-human-gate
- `tc-s02-002` Green: progress disabled and boundary remain intact
  - 前提: `--progress none` fixture と forbidden detail を含む payload fixture がある。
  - 操作: provider script を `--progress none` と `--progress stderr-summary` の両方で実行する。
  - 期待結果: `--progress none` は stderr empty、stderr-summary は forbidden detail を含まず stdout は final JSON のみ。
  - 失敗検出: stdout/stderr mixing、stderr leakage、progress disabled regression を検出する。
  - 検証方法: focused pytest stdout/stderr assertions。
  - 関連 closure id: cl-progress-none, cl-boundary
- `tc-s02-003` Green: limit and edge rendering pass
  - 前提: optional fields が多い payload と zero-check / skipped-neutral / failed / timeout fixtures がある。
  - 操作: provider script の progress rendering を各 fixture で実行する。
  - 期待結果: normal `limit=none`、optional drop 時だけ `limit=truncated`、EC fixtures はそれぞれの locked expectation を満たす。
  - 失敗検出: token途中 slice、false passed、skipped misclassification、failed detail leakage、timeout stdout breakage を検出する。
  - 検証方法: focused pytest と provider `bash -n`。
  - 関連 closure id: cl-truncation, cl-zero-check, cl-skipped-neutral, cl-failed-compact, cl-timeout-rendering

#### ステップ完了契約（step closure contract）
- closure id:
  - cl-ci-detail, cl-ci-compact, cl-review-detail, cl-review-human-gate, cl-progress-none, cl-boundary, cl-truncation, cl-zero-check, cl-skipped-neutral, cl-failed-compact, cl-old-thread-isolation, cl-trigger-unknown, cl-timeout-rendering
- close 条件:
  - targeted tests and provider shell syntax pass。
- report evidence:
  - TDD Green、Step/Test Closure、code-reviewer verdict。

#### ステップゲート（step gate）
- step reviewer gate:
  - reviewer: code-reviewer
  - pass 条件: review_status: pass
- commit / no-op gate:
  - closure 状態: committed

### 実装ステップ S03 — Semantic fingerprint alignment
- 振る舞いの目標（behavior goal）:
  - visible progress counters と quiet reset の semantic fingerprint を揃える。
- design 参照:
  - `design.md` の「採用方針 / トレードオフ」「クラス / インターフェース詳細設計」。
- 依存:
  - S01, S02。
- unblock:
  - S04。
- 対象ファイル:
  - provider `wait_pr_observation.sh`
- 計画済み契約:
  - scope:
    - `semantic_fingerprint(payload)` に CI check counts と review progress counts / threads / unresolved / limitations を含める。
    - raw body text そのものを progress reset の主因にしない。
  - テスト義務:
    - closure id:
      - cl-ci-quiet
      - cl-review-quiet
      - cl-raw-body-stability
  - Green 検証:
    - focused pytest
    - existing timeout / raw body / review collector regressions が壊れていないことを targeted `-k` で確認する。
  - amendment trigger:
    - fingerprint alignment が existing stability tests と矛盾する。

#### 委任契約（delegation contract）
- 委任ロール:
  - dev-coder
- 入力 docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - provider `wait_pr_observation.sh`
  - S01/S02 test evidence in `report.md`
- 許可 paths:
  - provider `wait_pr_observation.sh`
- 禁止 changes:
  - raw body text leakage、collector broad rewrite、new API。
- 受け入れ条件:
  - cl-ci-quiet, cl-review-quiet, cl-raw-body-stability が pass する。
- 必須 tests または docs-only verification:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "pr_observation_wait or pr_review or pr_observation" -q`
  - targeted raw-body / timeout / review collector regression command if test names are narrower after implementation
- reviewer focus:
  - code-reviewer: quiet reset semantics、raw-body-only stability、timeout / stale-head regressions。
- 必須出力:
  - changed files
  - verification result
  - closure ids satisfied / not satisfied
  - report evidence note
  - Ledger Note or `No material implementation decisions beyond the approved plan.`
  - unresolved risks
- 停止条件:
  - fingerprint alignment conflicts with approved design
  - raw body text must be fingerprinted as reset authority
  - collector broad rewrite or new API becomes necessary
  - existing stability regression cannot be preserved

#### 具体テストケース一覧
- `tc-s03-001` acceptance: CI count changes reset quiet
  - 前提: same coarse `ci=running` のまま check counts だけが進む poll sequence がある。
  - 操作: provider wait loop を複数 poll 実行する。
  - 期待結果: count 変化 poll が `wait.latest_change_poll` に反映され、stderr `quiet` が reset される。
  - 失敗検出: CI status / failures だけを fingerprint して count progress を無視する回帰を検出する。
  - 検証方法: focused pytest final JSON / stderr assertion。
  - 関連 closure id: cl-ci-quiet
- `tc-s03-002` acceptance: review count and thread changes reset quiet
  - 前提: comments / threads / unresolved counts が変化する review poll sequence がある。
  - 操作: provider wait loop を複数 poll 実行する。
  - 期待結果: review progress count 変化が `latest_change_poll` と stderr `quiet` に反映される。
  - 失敗検出: review status だけを fingerprint して count / thread progress を無視する回帰を検出する。
  - 検証方法: focused pytest final JSON / stderr assertion。
  - 関連 closure id: cl-review-quiet
- `tc-s03-003` regression: raw body text only stability
  - 前提: semantic review status / counts は同じで raw body text だけが変わる payload sequence がある。
  - 操作: provider wait loop を複数 poll 実行する。
  - 期待結果: raw body text のみの変化は progress reset authority にならず、既存 raw-body stability expectation が維持される。
  - 失敗検出: body text churn が quiet reset を誘発する回帰を検出する。
  - 検証方法: existing focused regression または新規 characterization pytest。
  - 関連 closure id: cl-raw-body-stability

#### ステップ完了契約（step closure contract）
- closure id:
  - cl-ci-quiet, cl-review-quiet, cl-raw-body-stability
- close 条件:
  - targeted tests pass and report evidence is recorded。

#### ステップゲート（step gate）
- step reviewer gate:
  - reviewer: code-reviewer
  - pass 条件: review_status: pass
- commit / no-op gate:
  - closure 状態: committed

### 実装ステップ S04 — Mirror sync and shipped asset parity
- 振る舞いの目標（behavior goal）:
  - dogfooding mirror の wait script が provider と一致する。
- design 参照:
  - `design.md` の「ディレクトリ / ファイル変更計画」「AC-010」。
- 依存:
  - S02, S03。
- unblock:
  - S90, S99。
- 対象ファイル:
  - `.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
- 計画済み契約:
  - scope:
    - provider script を mirror へ同期する。
    - mirror で独自 redesign しない。
  - テスト義務:
    - closure id:
      - cl-provider-mirror-parity
      - cl-bash-compat
  - Green 検証:
    - `bash -n src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
    - `bash -n .agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
    - `diff -u src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh .agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
  - amendment trigger:
    - provider / mirror exact parity が維持できない。

#### 委任契約（delegation contract）
- 委任ロール:
  - dev-coder
- 入力 docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - provider `wait_pr_observation.sh`
  - mirror `wait_pr_observation.sh`
- 許可 paths:
  - mirror `wait_pr_observation.sh`
- 禁止 changes:
  - provider から乖離した mirror-only behavior。
- 受け入れ条件:
  - cl-provider-mirror-parity and cl-bash-compat が pass する。
- 必須 tests または docs-only verification:
  - `bash -n src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
  - `bash -n .agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
  - `diff -u src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh .agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
- reviewer focus:
  - code-reviewer: exact parity、Bash syntax、dogfooding asset impact。
- 必須出力:
  - changed files
  - verification result
  - exact parity evidence
  - report evidence note
  - Ledger Note or `No material implementation decisions beyond the approved plan.`
  - unresolved risks
- 停止条件:
  - provider / mirror exact parity cannot be maintained
  - mirror requires behavior not present in provider
  - Bash syntax check fails after sync

#### 具体テストケース一覧
- `tc-s04-001` inspect-only: provider / mirror exact diff is empty
  - 前提: provider script が S02/S03 の tests を pass している。
  - 操作: provider script を mirror path へ同期し、`diff -u` を実行する。
  - 期待結果: provider / mirror の差分が空。
  - 失敗検出: dogfooding mirror が provider source と乖離する回帰を検出する。
  - 検証方法: `diff -u src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh .agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`。
  - 関連 closure id: cl-provider-mirror-parity
- `tc-s04-002` inspect-only: both scripts pass `bash -n`
  - 前提: provider / mirror scripts が存在する。
  - 操作: 両方に `bash -n` を実行する。
  - 期待結果: どちらも syntax check が pass する。
  - 失敗検出: mirror sync または provider implementation による Bash syntax / macOS compatibility regression を検出する。
  - 検証方法: `bash -n <provider>` と `bash -n <mirror>`。
  - 関連 closure id: cl-bash-compat

#### ステップ完了契約（step closure contract）
- closure id:
  - cl-provider-mirror-parity, cl-bash-compat
- close 条件:
  - `diff -u` empty and `bash -n` pass。

#### ステップゲート（step gate）
- step reviewer gate:
  - reviewer: code-reviewer
  - pass 条件: review_status: pass
- commit / no-op gate:
  - closure 状態: committed

### ドキュメント影響の解消ステップ S90（docs impact resolution / docs refresh）
- 対象:
  - docs / templates / README / workflow / skill / migration notes。
- 対応:
  - `limit=ok`、coarse progress example、`stderr-summary` の説明、stdout authority に矛盾する記述を検索する。
  - public docs 変更不要なら approved-no-op として根拠を report に残す。
  - 更新が必要なら doc-writer に委任し、runtime step と混ぜない。
- doc update owner:
  - updates required: doc-writer
  - no update: N/A with approved-no-op evidence
- spec/doc review:
  - reviewer: spec-reviewer
  - pass 条件: docs impact decision が requirement / design / plan と整合。

### 最終品質ゲートステップ S99（final quality gate）
- branch diff 範囲:
  - issue-wide diff: plan/report/discussions plus runtime script/tests/docs if implemented。
- 必須 validation:
  - `uv run pytest tests/unit/infra/test_init_update.py -k "pr_observation_wait or pr_review or pr_observation" -q`
  - `bash -n src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
  - `bash -n .agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
  - `diff -u src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh .agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`
  - `git diff --check`
  - `./spec-dock/scripts/spec-dock validate`
- final QA gate:
  - reviewer: qa-reviewer
  - 範囲: Issue 全体の obligation coverage と integration test 要否
  - pass 条件: reviewer pass
- final code review ゲート:
  - reviewer: code-reviewer
  - 範囲: issue-wide integrated diff、構造、責務境界、回帰リスク、保守性
  - pass 条件: review_status: pass
- final spec review ゲート:
  - reviewer: spec-reviewer
  - 範囲: requirement / design / plan / report / implementation / tests / docs 整合
  - pass 条件: reviewer pass
- final commit gate:
  - commit 範囲:
    - docs/planning artifacts、runtime script、tests、report closure。
  - final report ledger:
    - closure coverage、reviewer verdict、commit/no-op evidence、PR delivery / merge-preparation evidence。
  - post-commit external evidence destination:
    - final response / PR body / issue comment。

## 未確定事項
- なし。
  - `comments=N` の定義は回答済み。
  - 設計 reviewer は no findings で pass 済み。
  - 実装中に発生する collector 追加要否や line budget 逸脱は amendment trigger として扱う。

## 最終完了条件
- AC/EC 達成:
  - Spec-Locked Closure Index の required closure ids が pass または正当な approved-no-op で report に記録される。
- docs 影響解決:
  - S90 が update または approved-no-op で閉じ、spec-reviewer が pass する。
- 全 implementation step 完了:
  - S01-S04 が delegated / committed または正当な approved-no-op として report に記録される。
- final quality gate pass:
  - qa-reviewer: pass
  - issue-wide code-reviewer: pass
  - final spec-reviewer: pass
  - required validation commands: pass
  - PR delivery / merge-preparation gate: pass
  - issue finish 前に report に completion evidence が記録済み。
