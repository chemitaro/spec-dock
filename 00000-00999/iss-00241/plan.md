---
種別: 実装計画書（Issue）
ID: "iss-00241"
タイトル: "Resolve Epic Traceability And Review Policy Gate Gaps"
関連GitHub: ["#241"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-27"
依存: ["requirement.md", "design.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00241 Resolve Epic Traceability And Review Policy Gate Gaps — 実装計画

## この計画で満たす要件ID
- AC:
  - AC-001 Trusted review policy failure は human gate になる。
  - AC-002 Valid base policy の deterministic multiline trigger は維持される。
  - AC-003 Skill public contract が runtime behavior と一致する。
  - AC-004 Epic 正本は `guidance <target>` stdout handoff を現在仕様として示す。
  - AC-005 Generated projection は human/debug-only として扱われる。
  - AC-006 Issue 作成直後の design / plan は assurance compose 待ち blocker になる。
  - AC-007 Assurance compose は placeholder を安全に materialize する。
  - AC-008 `iss-00239` は `iss-00241` に supersede される。
  - AC-009 Epic report は current close readiness を一貫して示す。
  - AC-010 Epic traceability quality gate が追加される。
- EC:
  - EC-001 PR head policy only。
  - EC-002 Oversized base policy。
  - EC-003 Non-UTF-8 / unreadable base policy。
  - EC-004 Placeholder direct edit。
  - EC-005 Projection write failure。
- 制約:
  - Head policy fallback 禁止。
  - Bare `@codex review` fallback 禁止。
  - Provider / dogfooding / tests / docs contract parity。
  - `workflow next` は current entrypoint として残さない。

## 依存関係から導く実装順序
- 順序ルール:
  - Accepted ADR と逆の P0 runtime behavior を最初に修正する。
  - Public skill wording は runtime behavior の後に合わせる。
  - `iss-00239` 吸収 scope は issue artifact lifecycle と compose behavior をまとめて閉じる。
  - Epic docs/report reconciliation は、実装 contract が確定してから最後に行う。
- step 依存サマリー:
  - S01 Trusted review trigger fail-closed:
    - 依存: requirement / ADR trusted base policy。
    - unblock: S02, S90, S99。
    - 対象ファイル: trigger scripts, `tests/unit/infra/test_init_update.py`。
  - S02 PR observation skill contract parity:
    - 依存: S01。
    - unblock: S90。
    - 対象ファイル: provider / dogfooding `github-pr-observation/SKILL.md`, text assertions。
  - S03 Assurance compose placeholder scaffold:
    - 依存: requirement / design, `iss-00239` research。
    - unblock: S04, S90。
    - 対象ファイル: issue templates, lifecycle/composer/guidance if needed, CLI tests。
  - S04 `iss-00239` supersession evidence:
    - 依存: S03 scope fixed。
    - unblock: S90 / S99。
    - 対象ファイル: `iss-00239` report / metadata via SpecDock commands, GitHub issue if command path is available。
  - S90 Docs / Epic traceability reconciliation:
    - 依存: S01-S04。
    - unblock: S99。
    - 対象ファイル: Epic requirement/design/plan/report, issue report。
  - S99 Final quality gate:
    - 依存: S01-S90。
    - 対象: tests, sync/validate, reviewer gates, final report evidence。

## ステップ一覧
- S01: Trusted base policy failure path を POST なし human gate にする。
- S02: `github-pr-observation` skill の public write contract を deterministic body / human gate に更新する。
- S03: Issue 作成直後の design / plan を assurance compose 待ち placeholder にし、compose で安全に materialize する。
- S04: `iss-00239` を `iss-00241` に supersede し、unresolved corrective scaffold として残さない。
- S90: Epic 正本・Issue report・traceability ledger を current contract へ更新する。
- S99: Focused tests、sync/validate、qa/code/spec review で Issue 全体を閉じる。

## 要件 ↔ ステップ対応
- AC-001, EC-001, EC-002, EC-003 -> S01
- AC-002 -> S01
- AC-003 -> S02
- AC-004, AC-005, EC-005 -> S90
- AC-006, AC-007, EC-004 -> S03
- AC-008 -> S04
- AC-009, AC-010 -> S90 / S99

## 仕様固定クロージャ索引

| ID | ステップ | スライス | 種別 | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル | クロージャ証跡 |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01 | review-trigger-fail-closed | negative | AC-001, EC-001〜003 | base policy failure は POST なし human gate | missing / invalid / oversized / unreadable base policy fixture | untrusted bare review trigger | yes | red-required | trigger tests + report |
| tc-002 | S01 | review-trigger-success | regression | AC-002 | valid base policy は multiline deterministic body を投稿 | valid base policy fixture | valid path regression | yes | covered-existing | focused test result |
| tc-003 | S02 | skill-contract | docs/spec | AC-003 | skill text は deterministic body / human gate を説明 | provider/dogfooding SKILL.md | stale public contract | yes | inspect-only | docs diff + text assertion |
| tc-004 | S03 | placeholder-new-issue | acceptance | AC-006 | new issue の design / plan は awaiting-assurance-compose placeholder | `spec-dock new issue` fixture | assurance compose bypass | yes | red-required | CLI test |
| tc-005 | S03 | compose-placeholder | acceptance/negative | AC-007, EC-004 | compose は placeholder を materialize し、substantive content は上書きしない | placeholder / edited content fixture | destructive overwrite / skipped compose | yes | red-required | compose tests |
| tc-009 | S03 | marker-preserved-direct-edit | negative | EC-004 | marker が残ったまま追記された user content は conflict / fail-closed になり、通常 placeholder として上書きされない | placeholder marker plus appended substantive content | marker-only detection destructive overwrite | yes | red-required | compose/validate/guidance test |
| tc-006 | S04 | issue-239-supersession | docs/lifecycle | AC-008 | `iss-00239` は superseded / closed evidence を持つ | SpecDock/GitHub issue state | open corrective scaffold | yes | inspect-only | report + command evidence |
| tc-007 | S90 | guidance-epic-reflection | docs/spec | AC-004, AC-005, EC-005 | Epic 正本は guidance stdout authority / projection human-only を示す | Epic docs | stale `workflow next` authority | yes | inspect-only | docs diff + spec review |
| tc-008 | S90 | epic-closure-ledger | docs/spec | AC-009, AC-010 | Epic report は corrective issues と gate status を矛盾なく示す | Epic report | false completion / missing trace | yes | inspect-only | traceability table + spec review |

## レビュー / QA ゲート方針
- RG1 step review:
  - S01 / S03 は runtime / tests / scaffold behavior を含むため `code-reviewer` pass。
  - S02 / S04 / S90 は docs / skill / report / lifecycle evidence を含むため `spec-reviewer` pass。ただし code/test を含む場合は `code-reviewer` も対象。
- QG1 final QA:
  - `qa-reviewer` が AC/EC と closure ids の coverage、manual test 要否、integration test 要否を確認する。
- SG1 final spec review:
  - `spec-reviewer` が requirement / design / plan / report / Epic docs / implementation / tests / corrective issue disposition の整合を確認する。

## 実行ルール
- 1 implementation step = 1 review scope = 1 commit を標準にする。
- S01 と S03 は必ず red / negative characterization を先に固定する。
- S02 / S90 は docs-only でも inspection target と expected wording を明示する。
- 実装中に新しい Epic-level decision が見つかった場合は report の decision ledger に記録し、必要なら plan amendment と re-review を行う。
- `iss-00239` を close / supersede する際は command-first を優先し、metadata 直編集を避ける。

## 実装ステップ

### 実装ステップ S01 — Trusted review trigger failure を human gate にする
- 振る舞いの目標:
  - base SHA policy が利用不能な場合、review trigger comment を投稿せず human gate JSON を返す。
- design 参照:
  - `インターフェース契約` / `Trusted review trigger failure path`
- 依存:
  - requirement AC-001 / ADR trusted base policy。
- unblock:
  - S02, S90, S99。
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh`
  - `.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh`
  - `tests/unit/infra/test_init_update.py`
- 計画済み契約:
  - scope:
    - base SHA missing / policy missing / invalid / non-UTF-8 / oversized / unreadable を POST なし human gate に反転する。
    - valid base policy success path は維持する。
  - テスト義務:
    - closure id: `tc-001`, `tc-002`
    - coverage rationale: accepted ADR と逆の failure path を防ぐため negative tests が必須。
  - Red / 代替証跡:
    - `tests/unit/infra/test_init_update.py` の既存 fallback-success 期待を fail-closed 期待へ変更し、実装修正前に失敗することを確認する。
  - 実装範囲:
    - allowed paths: 上記 trigger scripts と focused tests。
    - forbidden changes: head policy fallback 追加、caller-provided body 追加、PR blocker engine 全体の再設計。
  - Green 検証:
    - `uv run pytest tests/unit/infra/test_init_update.py -k "codex_review or review_policy or github_pr_observation"`、必要に応じて narrower `-k`。
  - report 証跡:
    - Step Contract Closure、Test Contract Closure、Closure Coverage、Reviewer Gate Status。
  - amendment trigger:
    - Existing helper JSON schema と大きく衝突し、downstream observation scripts の設計変更が必要になる場合。

#### 委任契約
- delegated role:
  - dev-coder
- input docs:
  - `requirement.md`, `design.md`, `plan.md`, ADR trusted base policy, audit report。
- allowed paths:
  - S01 対象ファイルのみ。
- forbidden changes:
  - `.github/codex/review-policy.md` policy content の変更。
  - PR observation wait / blocker repair の unrelated refactor。
- acceptance criteria:
  - `tc-001`, `tc-002`。
- required tests:
  - Focused pytest result。
- reviewer focus:
  - code-reviewer: failure-path semantics, shell safety, fake gh tests, no fallback POST。
- stop conditions:
  - POST なし判定を fake gh test で観測できない。
  - JSON contract の既存 consumers への影響が不明。
- output required:
  - changed files、test result、human gate JSON fields、unresolved risks、report ledger note。

#### 具体テストケース一覧
- `tc-s01-001` negative: base policy missing は POST なし human gate
  - 前提: fake GitHub base SHA policy fetch が 404 / missing を返す。
  - 操作: trigger helper を実行する。
  - 期待結果: issue comment POST は呼ばれず、payload は `success=false` / `overall_status=human_gate` / blocking limitation を含む。
  - 失敗検出: bare `@codex review` fallback が投稿される回帰を検出する。
  - 検証方法: `tests/unit/infra/test_init_update.py` の focused test。
  - 関連 closure id: `tc-001`
- `tc-s01-002` negative: base SHA missing は POST なし human gate
  - 前提: fake GitHub PR metadata から base SHA を取得できない、または base SHA が空になる。
  - 操作: trigger helper を実行する。
  - 期待結果: issue comment POST は呼ばれず、payload は `review_policy.status=base_sha_missing` と human gate / blocking limitation を含む。
  - 失敗検出: base SHA 不明のまま fixed default body を投稿する回帰を検出する。
  - 検証方法: `tests/unit/infra/test_init_update.py` の focused test。
  - 関連 closure id: `tc-001`
- `tc-s01-003` negative: invalid / oversized / non-UTF-8 policy は POST なし human gate
  - 前提: fake GitHub policy fetch が invalid content、32 KiB 超過、non-UTF-8 を返す。
  - 操作: trigger helper を実行する。
  - 期待結果: すべて POST なし human gate になり、reason code が payload に残る。
  - 失敗検出: warning limitation だけで success になる回帰を検出する。
  - 検証方法: parameterized focused test。
  - 関連 closure id: `tc-001`
- `tc-s01-004` negative: unreadable / permission failure は POST なし human gate
  - 前提: fake GitHub policy fetch が permission denied、API error、または unreadable response を返す。
  - 操作: trigger helper を実行する。
  - 期待結果: issue comment POST は呼ばれず、payload は unreadable / fetch failure reason と human gate / blocking limitation を含む。
  - 失敗検出: policy unreadable を warning limitation として bare trigger 投稿に進む回帰を検出する。
  - 検証方法: `tests/unit/infra/test_init_update.py` の fake gh failure-path test。
  - 関連 closure id: `tc-001`
- `tc-s01-005` regression: valid base policy は deterministic multiline body
  - 前提: base SHA 上に valid policy があり、expected head SHA が一致する。
  - 操作: trigger helper を実行する。
  - 期待結果: policy base SHA / policy hash / reviewed head SHA を含む multiline body が 1 件 POST される。
  - 失敗検出: human gate 化に巻き込まれて valid path が投稿されなくなる回帰を検出する。
  - 検証方法: existing happy-path test または focused assertion。
  - 関連 closure id: `tc-002`

#### ステップ完了契約
- close 条件:
  - `tc-001` と `tc-002` が pass。
  - provider / dogfooding trigger script が同じ behavior。
  - code-reviewer pass。
- commit gate:
  - S01 scope のみ commit。

### 実装ステップ S02 — PR observation skill contract を更新する
- 振る舞いの目標:
  - skill が fixed endpoint + deterministic runtime-composed body + human gate を正しく説明する。
- 依存:
  - S01。
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - `.agents/skills/github-pr-observation/SKILL.md`
  - `tests/unit/infra/test_init_update.py`
- 計画済み契約:
  - scope:
    - fixed bare body wording を削除または historical でない形で使わない。
    - manual trigger 禁止と caller-provided body 禁止は維持する。
  - テスト義務:
    - closure id: `tc-003`
  - Red / 代替証跡:
    - text assertion で stale wording を検出する。
  - Green 検証:
    - skill text assertion / docs inspection。
  - report 証跡:
    - Evidence Adoption Ledger、Step Contract Closure、Reviewer Gate Status。

#### 委任契約
- delegated role:
  - doc-writer
- input docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - ADR `Trusted Base SHA GitHub Review Policy`
  - S01 implementation diff / tests
  - provider / dogfooding current `github-pr-observation/SKILL.md`
- allowed paths:
  - S02 対象ファイルのみ。
- forbidden changes:
  - PR trigger runtime behavior の追加変更。
- acceptance criteria:
  - `tc-003`
- required tests or docs-only verification:
  - text assertion in `tests/unit/infra/test_init_update.py` or equivalent `rg` inspection proving stale fixed-bare-body wording is gone.
  - docs diff inspection for provider and dogfooding skill parity.
- reviewer focus:
  - spec-reviewer: skill wording が accepted ADR / S01 behavior と一致すること。
- stop conditions:
  - S01 behavior と skill wording が一致しない。
- output required:
  - docs diff、inspection result、text assertion result。

#### 具体テストケース一覧
- `tc-s02-001` inspect-only: skill write contract wording
  - 前提: provider / dogfooding `github-pr-observation/SKILL.md` が存在する。
  - 操作: skill text を読む。
  - 期待結果: deterministic runtime-composed body、policy/hash/head evidence、base policy failure human gate が説明され、fixed bare body が唯一の write として説明されない。
  - 失敗検出: downstream agent が bare `@codex review` model を採用する stale wording を検出する。
  - 検証方法: text assertion と spec-reviewer inspection。
  - 関連 closure id: `tc-003`

#### ステップ完了契約
- close 条件:
  - skill text assertion pass。
  - spec-reviewer docs/spec alignment pass。
- commit gate:
  - S02 scope のみ commit。

### 実装ステップ S03 — Issue planning artifacts を assurance compose 待ち placeholder にする
- 振る舞いの目標:
  - New Issue の design / plan が通常 scaffold ではなく compose 待ち blocker になり、compose が安全に materialize する。
- 依存:
  - `iss-00239` research / user-approved absorption。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/templates/issue/design.md`
  - `src/spec_dock/assets/spec_dock/templates/issue/plan.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_lifecycle.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/artifact_composer.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/runbook.py` if guidance needs placeholder detection
  - `tests/cli_runtime/test_new.py`
  - `tests/cli_runtime/test_assurance_compose.py`
  - `tests/cli_runtime/test_workflow.py` if guidance is changed
- 計画済み契約:
  - scope:
    - design / plan placeholder marker and body。
    - compose replacement for marker。
    - substantive non-placeholder conflict / no-overwrite。
    - guidance recognition if needed。
  - テスト義務:
    - closure id: `tc-004`, `tc-005`, `tc-009`
  - Red / 代替証跡:
    - new issue test currently sees normal scaffold; update to expect placeholder.
    - compose placeholder test fails before implementation.
  - Green 検証:
    - `uv run pytest tests/cli_runtime/test_new.py tests/cli_runtime/test_assurance_compose.py tests/cli_runtime/test_workflow.py -k "issue or compose or guidance"`
  - report 証跡:
    - Step Contract Closure、Test Contract Closure、Closure Coverage。
  - amendment trigger:
    - File existence assumptions require broader validate / active store migration beyond placeholder marker support。

#### 委任契約
- delegated role:
  - dev-coder
- input docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `../iss-00239-compose-issue-planning-templates-after-assurance-classification/discussions/20260624t113051z-research-assurance-compose-scaffold-analysis.md`
  - `src/spec_dock/assets/spec_dock/templates/issue/design.md`
  - `src/spec_dock/assets/spec_dock/templates/issue/plan.md`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/artifact_composer.py`
- allowed paths:
  - S03 対象ファイルのみ。
- forbidden changes:
  - removing design / plan files from new issue output。
  - broad validator rewrite unrelated to placeholder state。
- acceptance criteria:
  - `tc-004`, `tc-005`。
- required tests or docs-only verification:
  - `uv run pytest tests/cli_runtime/test_new.py tests/cli_runtime/test_assurance_compose.py tests/cli_runtime/test_workflow.py -k "issue or compose or guidance"` or narrower focused equivalents that cover `tc-004` and `tc-005`。
- reviewer focus:
  - code-reviewer: scaffold compatibility, no-overwrite safety, tests.
- stop conditions:
  - Existing active / sync / validate contracts require design / plan normal scaffold in a way that placeholder cannot satisfy without bigger migration。
- output required:
  - changed files、test result、placeholder marker contract、unresolved risks。

#### 具体テストケース一覧
- `tc-s03-001` acceptance: new issue creates placeholder design / plan
  - 前提: temp repo で `spec-dock new issue` を実行する。
  - 操作: 作成された `design.md` / `plan.md` を読む。
  - 期待結果: `artifact_state: awaiting-assurance-compose` などの marker と、requirement capture / assurance classify / assurance compose を促す本文がある。
  - 失敗検出: agent が通常 scaffold と誤認して design / plan を書き始める状態を検出する。
  - 検証方法: `tests/cli_runtime/test_new.py`。
  - 関連 closure id: `tc-004`
- `tc-s03-002` acceptance: assurance compose materializes placeholder
  - 前提: requirement と assurance contract があり、design / plan は placeholder 状態。
  - 操作: `assurance compose --artifact all` を実行する。
  - 期待結果: profile-aware sections が design / plan に生成され、placeholder marker は残らない。
  - 失敗検出: compose が placeholder を認識せず変更しない回帰を検出する。
  - 検証方法: `tests/cli_runtime/test_assurance_compose.py`。
  - 関連 closure id: `tc-005`
- `tc-s03-003` negative: substantive content は上書きしない
  - 前提: design / plan に placeholder marker ではない substantive content がある。
  - 操作: `assurance compose --artifact all` を実行する。
  - 期待結果: content は自動上書きされず、conflict / unchanged / fail-closed として観測できる。
  - 失敗検出: user-authored content を compose が破壊する回帰を検出する。
  - 検証方法: `tests/cli_runtime/test_assurance_compose.py`。
  - 関連 closure id: `tc-005`
- `tc-s03-004` negative: marker が残った direct edit は上書きしない
  - 前提: design / plan に `artifact_state: awaiting-assurance-compose` marker が残ったまま、ユーザーまたは agent が substantive content を追記している。
  - 操作: `assurance compose --artifact all`、または placeholder state を判定する validate / guidance 経路を実行する。
  - 期待結果: 通常 placeholder として無条件置換せず、conflict / fail-closed / planning incomplete として観測できる。
  - 失敗検出: marker だけを根拠に user-added content を上書きする回帰を検出する。
  - 検証方法: `tests/cli_runtime/test_assurance_compose.py`、必要なら `tests/cli_runtime/test_workflow.py` または validate test。
  - 関連 closure id: `tc-009`

#### ステップ完了契約
- close 条件:
  - `tc-004`, `tc-005`, `tc-009` pass。
  - code-reviewer pass。
- commit gate:
  - S03 scope のみ commit。

### 実装ステップ S04 — `iss-00239` を superseded として閉じる
- 振る舞いの目標:
  - `iss-00239` を unresolved corrective scaffold として残さず、`iss-00241` への吸収を記録する。
- 依存:
  - S03 の plan scope。
- 対象ファイル / commands:
  - `./spec-dock/scripts/spec-dock close iss-00239` または available lifecycle command。
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00224-dynamic-workflow-resource-allocation/issues/iss-00239-compose-issue-planning-templates-after-assurance-classification/report.md`
  - GitHub issue `#239` comment/close if command path handles it。
- 計画済み契約:
  - scope:
    - Superseded reason、replacement issue `iss-00241`、absorbed scope、non-blocking rationale を記録する。
  - テスト義務:
    - closure id: `tc-006`
  - 代替証跡:
    - docs/lifecycle inspection。
  - Green 検証:
    - `./spec-dock/scripts/spec-dock sync`
    - `./spec-dock/scripts/spec-dock active show`
    - GitHub close result if command emits it。
  - report 証跡:
    - Decision Ledger、Evidence Adoption Ledger、Step Contract Closure。

#### 委任契約
- delegated role:
  - doc-writer / SpecDock operator
- input docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md`
  - `../iss-00239-compose-issue-planning-templates-after-assurance-classification/requirement.md`
  - `../iss-00239-compose-issue-planning-templates-after-assurance-classification/discussions/20260624t113051z-research-assurance-compose-scaffold-analysis.md`
  - `discussions/20260627t031736z-interview-corrective-issue-scope-confirmation.md`
- allowed paths:
  - `iss-00239` report / metadata touched by SpecDock command, `iss-00241` report。
- forbidden changes:
  - deleting `iss-00239` artifact directory。
  - editing metadata by hand if command path is available。
- acceptance criteria:
  - `tc-006`
- required tests or docs-only verification:
  - `./spec-dock/scripts/spec-dock sync`
  - `./spec-dock/scripts/spec-dock active show`
  - report / metadata / GitHub issue status inspection proving `iss-00239` is superseded by `iss-00241`.
- reviewer focus:
  - spec-reviewer: supersession evidence removes close blocker。
- stop conditions:
  - close command would close wrong GitHub issue or mutate unrelated issue。
- output required:
  - command output、changed files、supersession evidence。

#### 具体テストケース一覧
- `tc-s04-001` inspect-only: `iss-00239` superseded by `iss-00241`
  - 前提: `iss-00239` exists and is scaffold-only.
  - 操作: Supersession evidence and close status を確認する。
  - 期待結果: `iss-00239` は `iss-00241` に吸収されたことが report / command evidence に残り、Epic final gate の unresolved list に残らない。
  - 失敗検出: open scaffold corrective Issue が Epic close readiness を再度 block する状態を検出する。
  - 検証方法: SpecDock sync / report inspection / GitHub issue status if available。
  - 関連 closure id: `tc-006`

#### ステップ完了契約
- close 条件:
  - Supersession evidence present。
  - spec-reviewer pass。
- commit gate:
  - S04 scope のみ commit。

### ドキュメント影響の解消ステップ S90
- 対象:
  - Epic `requirement.md`
  - Epic `design.md`
  - Epic `plan.md`
  - Epic `report.md`
  - `iss-00241` `report.md`
  - Possibly docs/templates if S03 changes require operator-facing wording。
- 対応:
  - `workflow next` current-entrypoint wording を `guidance <target>` stdout handoff に置換する。
  - Generated projection は human/debug-only / non-canonical と明記する。
  - `iss-00237` / `iss-00238` / `iss-00239` / `iss-00241` を corrective issue inclusion gate に含める。
  - E-RQ / E-AC / accepted ADR / discussion decision -> implementation / tests / docs / report evidence の traceability ledger を追加する。
  - Epic `report.md` の completed / blocked / next action を current state に再構成する。
- doc update owner:
  - doc-writer
- spec/doc review:
  - reviewer: spec-reviewer
  - pass 条件: docs が S01-S04 の runtime behavior、accepted ADR、user-approved scope decision と一致する。

#### 委任契約
- delegated role:
  - doc-writer
- input docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md`
  - Epic `requirement.md`
  - Epic `design.md`
  - Epic `plan.md`
  - Epic `report.md`
  - Epic audit `discussions/20260627t025746z-research-epic-quality-gate-traceability-audit.md`
  - Spec reviewer report `discussions/20260627t030737z-disc-spec-reviewer-epic-traceability-gate.md`
  - Accepted ADRs referenced by this issue
  - S01-S04 implementation / command evidence
- allowed paths:
  - Epic `requirement.md`
  - Epic `design.md`
  - Epic `plan.md`
  - Epic `report.md`
  - `iss-00241` `report.md`
  - docs/templates only if S03 implementation proves operator-facing wording must change
- forbidden changes:
  - Changing runtime behavior during docs refresh.
  - Editing historical ADR decisions to hide the original wording; use current docs/report reflection instead.
  - Marking Epic complete while failed / partial / needs-verification entries remain unresolved.
- acceptance criteria:
  - `tc-007`, `tc-008`
- required tests or docs-only verification:
  - `rg "workflow next" spec-dock/active/epic/{requirement.md,design.md,plan.md,report.md}` inspection with only historical/superseded usage allowed.
  - Traceability table inspection covering E-RQ / E-AC / ADR / corrective issues.
  - Fresh `spec-reviewer` docs/spec alignment pass.
- reviewer focus:
  - spec-reviewer: Epic正本が current runtime/skill/test contract と矛盾せず、corrective issue status を矛盾なく示すこと。
- stop conditions:
  - S01-S04 の implementation evidence が未完了で current behavior を文書化できない。
  - Epic docs update would require a new architecture decision outside accepted ADR/current issue scope。
- output required:
  - changed docs、inspection results、traceability table summary、unresolved risks、report ledger entries。

#### 具体テストケース一覧
- `tc-s90-001` inspect-only: Epic docs no longer advertise `workflow next`
  - 前提: Epic canonical docs exist.
  - 操作: `rg "workflow next" spec-dock/active/epic/{requirement.md,design.md,plan.md,report.md}` を確認する。
  - 期待結果: current entrypoint としての `workflow next` は残らず、必要なら historical/superseded context としてのみ出る。
  - 失敗検出: future agent が stale command を実行する docs drift を検出する。
  - 検証方法: docs inspection / `rg` / spec-reviewer。
  - 関連 closure id: `tc-007`
- `tc-s90-002` inspect-only: Epic closure ledger includes corrective issues and gates
  - 前提: Epic report exists.
  - 操作: corrective issue dispositions、trusted policy gate、guidance gate、placeholder scaffold gate、reviewer verdict を読む。
  - 期待結果: completed / blocked / superseded / remaining next action が矛盾なく示される。
  - 失敗検出: report が pass と blocked を同時に示す回帰を検出する。
  - 検証方法: docs inspection / spec-reviewer。
  - 関連 closure id: `tc-008`

#### ステップ完了契約
- close 条件:
  - `tc-007`, `tc-008` pass。
  - spec-reviewer docs/spec alignment pass。
- commit gate:
  - S90 scope のみ commit。

### 最終品質ゲートステップ S99
- branch diff 範囲:
  - `iss-00241` branch diff from previous clean state / relevant base。
- 必須 validation:
  - `uv run pytest` focused lanes:
    - `tests/unit/infra/test_init_update.py`
    - `tests/cli_runtime/test_new.py`
    - `tests/cli_runtime/test_assurance_compose.py`
    - `tests/cli_runtime/test_workflow.py`
  - `./spec-dock/scripts/spec-dock sync`
  - `./spec-dock/scripts/spec-dock validate` if available and within current repo constraints。
  - `rg` inspections for stale `workflow next` current-entrypoint wording and fixed bare-body skill wording。
- final QA gate:
  - reviewer: qa-reviewer
  - 範囲: AC/EC coverage、negative tests、docs-only evidence、manual test要否。
  - pass 条件: missing high-value tests なし。
- final code review:
  - reviewer: code-reviewer
  - 範囲: S01/S03 runtime and tests, provider/dogfooding parity。
  - pass 条件: review_status pass。
- final spec review:
  - reviewer: spec-reviewer
  - 範囲: requirement / design / plan / report / Epic docs / corrective issue disposition / implementation / tests。
  - pass 条件: reviewer pass。
- final commit gate:
  - 各 step commit 完了後、final report ledger のみを閉じる final commit を作る。

## 未確定事項
- なし。

## 最終完了条件
- AC/EC 達成:
  - AC-001〜AC-010、EC-001〜EC-005 が closure evidence に紐付く。
- docs 影響解決:
  - Epic docs / report / skill text / issue reports が current contract と一致する。
- 全 implementation step 完了:
  - S01〜S04、S90、S99 が committed または正当な approved-no-op。
- final quality gate pass:
  - qa-reviewer pass。
  - issue-wide code-reviewer pass。
  - spec-reviewer pass。
- final clean state:
  - `git status --short` に意図しない staged / unstaged changes がない。
