---
種別: 実装計画書（Issue）
ID: "iss-00100"
タイトル: "Discussion template hearing sheet and flexible note expansion"
関連GitHub: ["#100"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-05-17"
依存: ["requirement.md", "design.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00100 Discussion template taxonomy and elicitation/capture expansion — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC: AC-001〜AC-010
- EC: EC-001〜EC-007
- 制約:
  - 新規 type は lowercase。
  - `interview` は質問ごとの分析ブロックを必須にする。
  - `scratch` は低摩擦 raw capture。
  - `note` は新規作成不可、既存 artifact は grandfathered。
  - 文書そのものの昇格 type / command は作らない。

## マイルストーン一覧
- M1: Shipped docs/templates catalog
  - 完了条件: provider-side docs/templates が新 catalog、authority、reflection、retired `note` と一致し、docs-only review を pass する。
- M2: Runtime and tests
  - 完了条件: `new doc scratch/interview` が作成でき、`new doc note` は retired error、validation は grandfathered `note` を許容し、targeted tests が pass する。
- M3: Dogfooding mirror and stale guidance closure
  - 完了条件: local dogfooding `spec-dock/` mirror が provider asset と整合し、stale `new doc note` / old catalog examples が required scan で検出されない。
- M4: Final gates
  - 完了条件: docs impact、qa-reviewer、issue-wide code-reviewer、final spec-reviewer が pass し、final report ledger と commit が完了する。

## 依存関係から導く実装順序
- S01 docs/templates は runtime が読む target catalog を固定するため最初に置く。
- S02 runtime/tests は S01 の template names/placeholders を前提に CLI behavior と validation behavior を実装する。
- S03 dogfooding/stale scan は S01/S02 の結果を local mirror と shipped docs 全体に反映し、old catalog drift を閉じる。
- S90/S99 は implementation step 後に必ず独立実施する。

## ステップ一覧
- S01: provider-side docs/templates を新 catalog に更新する。
  - 依存: requirement/design pass
  - unblock: S02 runtime template lookup and docs contract
  - reviewer: spec-reviewer
  - commit: docs/templates scope
- S02: runtime allowlist/parser/validation/tests を実装する。
  - 依存: S01
  - unblock: S03 dogfooding verification
  - reviewer: code-reviewer
  - commit: runtime/tests scope
- S03: dogfooding mirror、stale-doc scan、report evidence を閉じる。
  - 依存: S01/S02
  - unblock: S90/S99
  - reviewer: spec-reviewer
  - commit: dogfooding/docs/report scope
- S90: docs impact resolution / docs refresh
- S99: final quality gate

## 要件 ↔ ステップ対応
- AC-001 -> S01, S03
- AC-002 -> S01, S02
- AC-003 -> S01, S03
- AC-004 -> S01, S02
- AC-005 -> S01, S03
- AC-006 -> S02, S03
- AC-007 -> S02
- AC-008 -> S01, S03
- AC-009 -> S01, S03, S90
- AC-010 -> S01, S03
- EC-001〜EC-007 -> S01, S02, S03

## Spec-Locked Closure Index（仕様固定クロージャ索引）

| id | phase / step | slice | type | spec link | locked expectation | observable input/state | bug class guarded | required | evidence level | closure evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| cl-001 | S01 | docs/templates catalog | acceptance | AC-001, AC-003, AC-005, AC-008, AC-009, AC-010, EC-001, EC-006 | shipped docs/templates describe `scratch` / `interview` / `research` / `disc` / `adr`, authority defaults, reflection rules, simple confirmation guidance, oversized `disc` split guidance, and retired `note` consistently | provider docs/templates diff | stale taxonomy / misleading agent guidance | yes | inspect-only | spec-reviewer step pass + stale scan |
| cl-002 | S01 | interview template | acceptance | AC-002, EC-001, EC-002, EC-003 | `interview.md` has repeatable question block with all required analysis labels and answer/follow-up fields, and explains when trivial yes/no can stay outside `interview` | provider `interview.md` content | weak user question sheet / missing decision support | yes | red-required | automated content assertion + spec-reviewer pass |
| cl-003 | S01 | scratch template | acceptance | AC-004, EC-004, EC-005 | `scratch.md` keeps required body minimal and marks raw capture as non-authoritative | provider `scratch.md` content | raw capture becoming pseudo-authoritative | yes | inspect-only | spec-reviewer pass |
| cl-004 | S02 | creatable doc types | acceptance | AC-006, AC-007 | `new doc scratch/interview` succeeds; `adr/disc/research` regressions do not occur | CLI command / runtime use case | new types unusable | yes | red-required | targeted runtime tests |
| cl-005 | S02 | retired note creation | negative | AC-006, EC-007 | `new doc note` reaches retired guidance, not argparse generic invalid choice | CLI command | confusing or silently supported retired type | yes | red-required | targeted negative test |
| cl-006 | S02 | validation grandfathering | regression | AC-006, EC-007 | validation accepts timestamp and legacy `note` artifacts while accepting `scratch/interview` filenames | validate fixtures | breaking existing discussion history | yes | red-required | targeted validation tests |
| cl-007 | S02 | installer/update scaffold | acceptance | AC-006 | init/update scaffold places `interview.md` / `scratch.md` and prunes managed `note.md` while preserving existing discussion artifacts | installer/update temp workspace or tests | shipped scaffold drift | yes | red-required | installer/update test or equivalent command evidence |
| cl-008 | S03 | dogfooding mirror / prune | acceptance | AC-006, AC-009 | dogfooding mirror has new docs/templates and no managed `note.md`; existing issue discussion `note` artifacts remain valid | `spec-dock/` mirror and validate | provider/dogfooding drift | yes | manual-required | sync/update evidence + validate |
| cl-009 | S03 | stale shipped docs scan | regression | AC-001, AC-005, AC-009, AC-010, EC-006 | shipped docs do not advertise `new doc note` or `adr|disc|research|note` as current catalog; grandfathering explanations are allowed | `rg` scan over provider and dogfooding docs | stale command contract | yes | inspect-only | stale scan output + spec-reviewer pass |
| cl-010 | S90/S99 | final integrated quality | acceptance | all AC/EC | tests, docs, report, implementation, and reviews agree; no required closure remains open | full diff/report/reviews | issue-level incomplete delivery | yes | manual-required | qa/code/spec final pass |

## レビュー / QA ゲート方針
- S01/S03/S90 docs/template-only changes: `spec-reviewer` docs/spec alignment pass.
- S02 runtime/tests/scaffold behavior changes: `code-reviewer` step pass.
- S99 final:
  - `qa-reviewer`: test sufficiency and integration test decision.
  - issue-wide `code-reviewer`: integrated diff.
  - `spec-reviewer`: requirement/design/plan/report/implementation/docs alignment.

## 実行ルール（全ステップ共通）
- `workflow_issue.md` を実行 policy の正本にする。
- 各 implementation step は delegation gate、reviewer gate、commit gate を持つ。
- `1 implementation step = 1 review scope = 1 commit` を守る。
- report は step reviewer gate 前に更新し、step diff として review される。
- required closure row の locked expectation / required / spec link を変更する場合は plan amendment と re-review を先に行う。

## 実装ステップ

### S01 — provider docs/templates catalog
- 観測可能な振る舞い:
  - provider-side shipped docs/templates を読めば、新 catalog、authority、reflection、retired `note` が分かる。
- design 参照:
  - `ディレクトリ / ファイル変更計画`, `採用方針 / トレードオフ`, `インターフェース契約`
- 依存: requirement/design pass
- unblock: S02
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/templates/discussions/{adr,disc,research,interview,scratch}.md`
  - `src/spec_dock/assets/spec_dock/templates/discussions/note.md`
  - `src/spec_dock/assets/spec_dock/docs/{guide,reference_naming,workflow_initiative,workflow_epic,workflow_issue,workflow_spec_authoring,phase_requirement,phase_design}.md`
  - `src/spec_dock/assets/spec_dock/docs/rules/{initiative,epic,issue}/discussions.md`
  - `src/spec_dock/assets/spec_dock/templates/README.md`
  - `src/spec_dock/assets/spec_dock/scripts/README.md`
- test bundle:
  - closure ids: cl-001, cl-002, cl-003
  - evidence level: inspect-only / red-required for cl-002 content assertion
  - negative: old `new doc note` examples are removed from current catalog docs.
- pre-implementation evidence:
  - characterization pass: current docs/templates still contain `note` catalog and no `interview.md` / `scratch.md`.

#### delegation contract
- delegated role: doc-writer
- input docs:
  - active issue `requirement.md`, `design.md`, `plan.md`
  - `spec-dock/docs/phase_design.md`, `spec-dock/docs/workflow_issue.md`
  - current target files above
- allowed paths:
  - S01 target files only.
- forbidden changes:
  - runtime code/tests, dogfooding mirror, unrelated docs, migration of existing discussion artifacts.
- acceptance criteria:
  - cl-001, cl-002, cl-003 close.
- required tests or docs-only verification:
  - `git diff --check`
  - automated content assertion for required `interview.md` labels.
- reviewer focus:
  - `spec-reviewer` docs/spec alignment.
- stop conditions:
  - target docs contradict design, required label set cannot fit template, stale command contract found outside allowed paths.
- output required:
  - changed files, summary, verification output, unresolved risks.

#### 具体テストケース一覧
- `tc-s01-001` acceptance: provider docs/templates advertise the new catalog.
  - 前提: S01 target files are changed only in provider-side assets.
  - 操作: inspect docs/templates and run stale scan over S01 target files.
  - 期待結果: current catalog is `scratch/interview/research/disc/adr`; `note` appears only as retired/grandfathered.
  - 失敗検出: `new doc note` or `adr|disc|research|note` is still presented as current catalog.
  - 検証方法: `rg` stale scan + spec-reviewer.
  - 関連 closure id: cl-001
- `tc-s01-002` acceptance: `interview.md` contains required per-question labels.
  - 前提: provider `interview.md` exists.
  - 操作: run a label assertion command against `interview.md`.
  - 期待結果: every required label in cl-002 exists in the repeatable question block.
  - 失敗検出: any required label is missing or only global.
  - 検証方法: targeted assertion command.
  - 関連 closure id: cl-002
- `tc-s01-003` acceptance: `scratch.md` remains low friction.
  - 前提: provider `scratch.md` exists.
  - 操作: inspect required sections.
  - 期待結果: required body is centered on `メモ`; other organization fields are optional guidance.
  - 失敗検出: `scratch` requires research/discussion/decision fields.
  - 検証方法: spec-reviewer inspection.
  - 関連 closure id: cl-003

#### step closure contract
- closure ids: cl-001, cl-002, cl-003
- close 条件: S01 files changed, verification passes, report updated, spec-reviewer pass, commit created.
- 検証 evidence: `git diff --check`, content assertion, stale scan, reviewer pass.
- report evidence: Step Contract Closure / Test Contract Closure / Closure Coverage.
- 残リスク: exact wording may be refined in S03 dogfooding docs pass.

#### behavior slice execution
- 実装 batch:
  - 許可範囲: S01 target files.
  - 禁止範囲: runtime/tests/dogfooding mirror.
- 検証:
  - `git diff --check`
  - targeted content assertion.
- refactor / tidy:
  - 目的: duplicated docs wording may be normalized only within S01 target files.
  - ガードレール: do not redesign workflow policy.

#### step gate
- delegation 判断: delegated to doc-writer.
- step reviewer gate: `spec-reviewer`, S01 diff only, pass required.
- commit gate:
  - closure 状態: committed
  - commit 範囲: S01 docs/templates/report evidence only
  - commit message 意図: `docs(discussions): ディスカッションテンプレートカタログを整理`
- no-op gate: not allowed unless no target docs are stale, which current characterization disproves.

### S02 — runtime allowlist, parser, validation, tests
- 観測可能な振る舞い:
  - CLI creates `scratch` / `interview`, rejects `note` with retired guidance, and validates existing `note`.
- 依存: S01
- unblock: S03
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py`
  - `tests/cli_runtime/test_new.py`
  - `tests/cli_runtime/test_runtime_new_doc_s09.py`
  - `tests/cli_runtime/test_validate.py`
  - `tests/test_init_update.py`
- test bundle:
  - closure ids: cl-004, cl-005, cl-006, cl-007
  - evidence level: red-required
- pre-implementation evidence:
  - expected red: current parser choices reject `scratch/interview`, current use case allows `note`.

#### delegation contract
- delegated role: dev-coder
- input docs:
  - active issue `requirement.md`, `design.md`, `plan.md`
  - S01 committed docs/templates
  - current runtime/test files
- allowed paths:
  - S02 target files only.
- forbidden changes:
  - shipped docs/templates except test fixtures, dogfooding mirror, existing discussion artifact migration.
- acceptance criteria:
  - cl-004, cl-005, cl-006, cl-007 close.
- required tests or docs-only verification:
  - targeted `python -m unittest` for changed runtime tests.
  - `./spec-dock/scripts/spec-dock validate`
  - `git diff --check`
- reviewer focus:
  - `code-reviewer` for runtime/tests behavior and compatibility.
- stop conditions:
  - type policy requires design change, parser cannot route retired error, tests require broad unrelated rewrite.
- output required:
  - changed files, tests run, summary, risks.

#### 具体テストケース一覧
- `tc-s02-001` acceptance: `new doc scratch/interview` creates timestamped files.
  - 前提: initialized temp spec-dock workspace with templates.
  - 操作: run runtime new doc for `scratch` and `interview`.
  - 期待結果: files match `<ts>-scratch-*.md` and `<ts>-interview-*.md`; placeholders are replaced.
  - 失敗検出: parser rejects type or template lookup fails.
  - 検証方法: unittest.
  - 関連 closure id: cl-004
- `tc-s02-002` negative: `new doc note` is retired.
  - 前提: CLI parser receives raw `note`.
  - 操作: run `new doc note`.
  - 期待結果: command exits non-zero with retired `note` guidance and suggests `scratch`; it is not argparse invalid choice.
  - 失敗検出: generic invalid choice, silent creation, or alias creation.
  - 検証方法: unittest.
  - 関連 closure id: cl-005
- `tc-s02-003` regression: validation accepts grandfathered `note` and new types.
  - 前提: discussions dir contains timestamp/legacy `note`, plus `scratch/interview`.
  - 操作: run validation fixtures.
  - 期待結果: valid filenames pass; malformed new/old type candidates fail.
  - 失敗検出: existing `note` rejected or new type malformed detection missed.
  - 検証方法: unittest.
  - 関連 closure id: cl-006
- `tc-s02-004` acceptance: init/update scaffold carries new templates and prunes managed `note.md`.
  - 前提: temp consumer workspace initialized or updated from provider assets.
  - 操作: run installer/update test or equivalent command that inspects `spec-dock/templates/discussions`.
  - 期待結果: `interview.md` and `scratch.md` exist; managed `note.md` does not; existing discussion artifacts are not deleted.
  - 失敗検出: new templates missing, stale managed `note.md` remains, or discussion artifacts are pruned.
  - 検証方法: `tests/test_init_update.py` targeted test or equivalent installer/update command evidence.
  - 関連 closure id: cl-007

#### step closure contract
- closure ids: cl-004, cl-005, cl-006, cl-007
- close 条件: targeted tests pass, validate pass, report updated, code-reviewer pass, commit created.
- 検証 evidence: unittest commands, `validate`, `git diff --check`.
- report evidence: Step Contract Closure / Test Contract Closure / Closure Coverage.
- 残リスク: installer/update scaffold behavior is fully closed in S02; S03 only closes dogfooding mirror application and stale-doc scan evidence.

#### behavior slice execution
- 実装 batch:
  - 許可範囲: S02 target files.
  - 禁止範囲: docs/templates wording changes outside tests.
- 検証:
  - targeted unittest commands.
- refactor / tidy:
  - 目的: keep type constants readable; avoid sweeping runtime refactor.
  - ガードレール: layered architecture remains intact.

#### step gate
- delegation 判断: delegated to dev-coder.
- step reviewer gate: `code-reviewer`, S02 diff only, pass required.
- commit gate:
  - closure 状態: committed
  - commit 範囲: S02 runtime/tests/report evidence only
  - commit message 意図: `feat(runtime): discussion doc type catalogを更新`
- no-op gate: not allowed.

### S03 — dogfooding mirror, stale scan, report closure
- 観測可能な振る舞い:
  - local `spec-dock/` mirror and report reflect implemented catalog, and stale current-catalog docs are closed.
- 依存: S01, S02
- unblock: S90, S99
- 対象ファイル:
  - `spec-dock/templates/`
  - `spec-dock/docs/`
  - `spec-dock/active/issue/report.md`
  - optional test fixtures generated by allowed commands under `/private/tmp` or temp dirs
- test bundle:
  - closure ids: cl-008, cl-009
  - evidence level: manual-required / inspect-only
- pre-implementation evidence:
  - characterization pass: current dogfooding mirror still has old catalog until refreshed.

#### delegation contract
- delegated role: doc-writer
- input docs:
  - active issue requirement/design/plan
  - S01/S02 commit summaries
  - provider asset paths and dogfooding mirror paths
- allowed paths:
  - S03 target files only.
- forbidden changes:
  - provider runtime code/tests, existing issue discussion artifact rename/delete, unrelated dogfooding data.
- acceptance criteria:
  - cl-008, cl-009 close.
- required tests or docs-only verification:
  - `./spec-dock/scripts/spec-dock validate`
  - stale scan command for old current-catalog expressions
  - `git diff --check`
- reviewer focus:
  - `spec-reviewer` docs/spec alignment and stale guidance closure.
- stop conditions:
  - dogfooding mirror cannot be updated without deleting issue data, stale scan reveals provider files outside design scope, validate fails.
- output required:
  - changed files, scan output, validate output, risks.

#### 具体テストケース一覧
- `tc-s03-001` acceptance: dogfooding mirror matches shipped catalog.
  - 前提: S01/S02 committed.
  - 操作: refresh or manually mirror shipped docs/templates according to repo dogfooding rule.
  - 期待結果: dogfooding templates include `interview.md` / `scratch.md`, managed `note.md` removed, docs show new catalog.
  - 失敗検出: provider/dogfooding drift.
  - 検証方法: file inventory + `validate`.
  - 関連 closure id: cl-008
- `tc-s03-002` regression: stale current-catalog docs are absent.
  - 前提: provider and dogfooding docs updated.
  - 操作: run stale scan for `new doc note` and `adr|disc|research|note`.
  - 期待結果: no current catalog examples remain; grandfathered compatibility text is reviewed as intentional.
  - 失敗検出: stale docs still instruct agents to create `note`.
  - 検証方法: `rg` scan + spec-reviewer.
  - 関連 closure id: cl-009

#### step closure contract
- closure ids: cl-008, cl-009
- close 条件: dogfooding mirror updated, scans/validate pass, report updated, spec-reviewer pass, commit created.
- 検証 evidence: validate, stale scan, inventory diff.
- report evidence: Step Contract Closure / Test Contract Closure / Closure Coverage.
- 残リスク: final gates may request additional docs polish.

#### behavior slice execution
- 実装 batch:
  - 許可範囲: S03 target files.
  - 禁止範囲: provider runtime/tests.
- 検証:
  - `./spec-dock/scripts/spec-dock validate`
  - stale scan command.
- refactor / tidy:
  - 目的: report evidence consistency.
  - ガードレール: do not rewrite earlier specs except evidence corrections.

#### step gate
- delegation 判断: delegated to doc-writer.
- step reviewer gate: `spec-reviewer`, S03 diff only, pass required.
- commit gate:
  - closure 状態: committed
  - commit 範囲: S03 dogfooding/report evidence only
  - commit message 意図: `docs(dogfooding): discussion template catalog mirrorを同期`
- no-op gate: only if dogfooding update command produces no diff and stale scan proves no drift.

### S90 — docs impact resolution / docs refresh
- 対象:
  - docs / templates / README / workflow / migration notes affected by S01〜S03.
- test bundle:
  - closure ids: cl-009
  - evidence level: inspect-only
- 対応:
  - S01/S03 が docs impact を解決済みであることを確認する。
  - 追加 stale docs が見つかった場合は doc-writer に bounded follow-up を委任し、spec-reviewer pass を再取得する。
- delegation contract:
  - delegated role: doc-writer when additional docs changes are required; N/A for approved-no-op.
  - input docs: requirement/design/plan/report, S01〜S03 summaries, stale scan output.
  - allowed paths: docs/templates/README/workflow/skill/migration notes identified by stale scan.
  - forbidden changes: runtime/tests behavior, unrelated docs, existing discussion artifact migration.
  - required verification: stale scan, `git diff --check`, `./spec-dock/scripts/spec-dock validate` when files change.
  - stop conditions: stale scan finds files outside design scope, docs impact cannot be resolved without plan amendment.
  - output required: update/no-op rationale, changed files if any, verification result, spec-reviewer evidence.
- 具体テストケース一覧:
  - `tc-s90-001` docs-impact: no unresolved docs impact remains.
    - 前提: S01〜S03 are complete.
    - 操作: inspect docs/templates/README/workflow/skill/migration notes impact and rerun stale scan.
    - 期待結果: either no additional docs change is required with rationale, or doc-writer follow-up is committed/reviewed.
    - 失敗検出: docs impact marked none without checked paths/spec-reviewer evidence, or stale current-catalog guidance remains.
    - 検証方法: stale scan + spec-reviewer.
    - 関連 closure id: cl-009
- step closure contract:
  - closure ids: cl-009
  - close 条件: docs impact resolved by committed follow-up or approved-no-op, report updated, spec-reviewer pass.
  - 検証 evidence: stale scan, validate if changed, spec-reviewer pass.
  - report evidence: S90 Docs Impact Resolution, Closure Coverage, Step Commit Gate or approved-no-op evidence.
- step gate:
  - step reviewer gate: `spec-reviewer`, S90 docs impact scope, pass required.
  - commit gate: committed if S90 changes files; approved-no-op only when scan/inspection proves no changes required.
  - no-op gate: requires checked path list, no-update rationale, stale scan output, spec-reviewer pass.
- spec/doc review:
  - reviewer: spec-reviewer
  - pass 条件: docs/templates/report が requirement/design/plan と整合し、未解決 docs impact がない。

### S99 — final quality gate
- branch diff 範囲:
  - iss-00100 branch full diff from base.
- test bundle:
  - closure ids: cl-010
  - evidence level: manual-required
- 必須 validation:
  - `git diff --check`
  - `./spec-dock/scripts/spec-dock validate`
  - targeted unittest commands from S02
- final QA gate:
  - reviewer: qa-reviewer
  - 範囲: issue 全体の test 十分性と integration test 要否
  - pass 条件: reviewer pass。必要なら先に integration test を追加する。
- final code review ゲート:
  - reviewer: code-reviewer
  - 範囲: issue-wide integrated diff、構造、責務境界、回帰リスク、保守性
  - pass 条件: review_status: pass。
- final spec review ゲート:
  - reviewer: spec-reviewer
  - 範囲: requirement / design / plan / report / implementation / tests / docs alignment
  - pass 条件: review_status: pass。
- final commit gate:
  - final report ledger を更新して commit する。
  - post-commit clean check を final response / PR / issue comment に残す。
- step closure contract:
  - closure ids: cl-010
  - close 条件: required validation commands pass, S90 is closed, qa-reviewer pass, issue-wide code-reviewer pass, final spec-reviewer pass, final report ledger updated, final commit created.
  - 検証 evidence: command outputs, reviewer pass summaries, final report ledger, post-commit clean check.
  - report evidence: Final QA Gate, Final Code Review Gate, Final Spec Review Gate, Final Commit, Closure Coverage for cl-010.
- 具体テストケース一覧:
  - `tc-s99-001` final: integrated issue quality is closed.
    - 前提: S01〜S03 and S90 are closed.
    - 操作: run final validations and three final reviewers.
    - 期待結果: qa/code/spec final reviewers pass and no closure id remains open.
    - 失敗検出: missing tests, unresolved docs impact, report/spec mismatch, dirty final state.
    - 検証方法: command evidence + reviewer pass + final clean check.
    - 関連 closure id: cl-010

## 未確定事項
- なし。

## 最終完了条件
- requirement/design/plan gate: all pass.
- S01〜S03: committed or approved-no-op with valid report evidence.
- S90: docs impact resolved with spec-reviewer pass.
- S99: qa-reviewer, issue-wide code-reviewer, final spec-reviewer all pass.
- required closure ids cl-001〜cl-010: closed in report.
- final commit completed and no unintended staged / unstaged changes remain.
