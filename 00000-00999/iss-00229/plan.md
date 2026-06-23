---
種別: 実装計画書（Issue）
ID: "iss-00229"
タイトル: "Compose Profile Aware Planning Artifacts"
関連GitHub: ["#229"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
依存: ["requirement.md", "design.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00229 Compose Profile Aware Planning Artifacts — 実装計画（実行契約 / Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001 profile-aware materialization
  - AC-002 idempotence
  - AC-003 no-overwrite
  - AC-004 stale source binding
  - AC-005 downgrade no deletion
  - AC-006 provider / mirror parity
- EC:
  - EC-001 missing assurance
  - EC-002 invalid assurance
  - EC-003 marker conflict
- 制約:
  - `authorized_profile` authority only
  - `lite_candidate` non-authority
  - monotonic additive escalation
  - provider source / dogfooding mirror parity
  - MyPy / Ruff clean

## 依存関係から導く実装順序
- S01:
  - 依存: I01 Assurance model / I02 workflow ready。
  - unblock: fragment manifest と pure composer の contract。
- S02:
  - 依存: S01。
  - unblock: CLI vertical slice と artifact write behavior。
- S03:
  - 依存: S02。
  - unblock: stale source binding integration for compose / verify / workflow block。
- S90:
  - 依存: S01-S03。
  - unblock: provider/mirror parity。
- S99:
  - 依存: S01-S90。
  - unblock: issue finish / Epic continuation。

## ステップ一覧
- S01:
  - 観測可能な振る舞い: profile manifest と domain composer が managed sections を決定し、idempotence / no-overwrite / no deletion を pure tests で保証する。
  - 対象ファイル: `domain/artifact_composer.py`, `templates/assurance/profile-sections.json`, unit tests。
  - 閉じる要件: AC-001, AC-002, AC-003, AC-005, EC-003。
  - レビューゲート: code-reviewer。
- S02:
  - 観測可能な振る舞い: `assurance compose --artifact ...` が active / explicit issue の planning artifacts を materialize し、missing / schema-invalid authority を fail-closed する。stale authority blocking は S03 が compose / verify / workflow へ統合する。
  - 対象ファイル: `application/assurance.py`, `commands/assurance.py`, `infra/artifact_store.py`, `presentation/assurance_text.py`, CLI tests。
  - 閉じる要件: AC-001, AC-002, AC-003, EC-001, EC-002, EC-003。
  - レビューゲート: code-reviewer。
- S03:
  - 観測可能な振る舞い: `assurance compose`、`assurance verify`、`workflow next issue-execution` が stale source binding を検出し、planning section generation と execution-ready を返さない。
  - 対象ファイル: `application/assurance.py`, `commands/assurance.py`, `infra/assurance_store.py`, `application/workflow.py`, `domain/workflow_state.py`, tests。
  - 閉じる要件: AC-004, EC-002。
  - レビューゲート: code-reviewer。
- S90:
  - 観測可能な振る舞い: provider asset から dogfooding mirror へ同期され、templates / runtime parity が確認される。
  - 対象ファイル: dogfooding mirror under `spec-dock/`。
  - 閉じる要件: AC-006。
  - レビューゲート: spec-reviewer。
- S99:
  - 観測可能な振る舞い: issue-wide tests / lint / reviewers が pass し、report が closure evidence を持つ。
  - 対象ファイル: report / final reviewer fixes if any。
  - 閉じる要件: all。
  - レビューゲート: qa-reviewer, code-reviewer, spec-reviewer。

## 要件 ↔ ステップ対応
- AC-001 -> S01, S02
- AC-002 -> S01, S02
- AC-003 -> S01, S02
- AC-004 -> S03
- AC-005 -> S01, S02
- AC-006 -> S90
- EC-001 -> S02
- EC-002 -> S02, S03
- EC-003 -> S01, S02

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| 識別子（ID） | ステップ（step） | スライス（slice） | 種別（type） | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル（evidence level） | クロージャ証跡（closure evidence） |
|---|---|---|---|---|---|---|---|---|---|---|
| tc-001 | S01 | profile-composer | acceptance | AC-001 | authorized profile から必要 section set が決まる | lite / standard / strict / critical profile fixtures | missing planning obligations / explicit Lite ambiguity | yes | red-required | report S01 closure |
| tc-002 | S01/S02 | idempotence | invariant | AC-002 | compose twice で diff が出ない | same contract + same artifacts | noisy tracked diff / unstable output | yes | red-required | report S01/S02 closure |
| tc-003 | S01/S02 | no-overwrite | invariant | AC-003/AC-005 | substantive body preserved; downgrade does not delete | existing manual section / stronger section | human content loss | yes | red-required | report S01/S02 closure |
| tc-004 | S02 | compose-cli | acceptance | AC-001/EC-001/EC-002 | compose command materializes or fails closed | valid / missing / invalid assurance | unsafe planning handoff | yes | red-required | report S02 closure |
| tc-005 | S01/S02 | marker-conflict | negative | EC-003 | broken markers stop without artifact mutation | duplicated / unclosed marker | corrupt markdown write | yes | red-required | report S01/S02 closure |
| tc-006 | S03 | stale-source-binding | negative | AC-004/EC-002 | stale contract blocks compose, verify, and workflow execution-ready | changed requirement/design/plan after classify | stale authority execution | yes | red-required | report S03 closure |
| tc-007 | S90 | provider-mirror-parity | integration | AC-006 | provider templates/runtime match dogfooding mirror | update after provider changes | dogfooding drift | yes | inspect-only | report S90 closure |
| tc-008 | S99 | issue-final-quality | final | all | unit/CLI/lint/reviewer gates pass | full issue diff | integrated regression | yes | manual-required | report S99 closure |

## レビュー / QA ゲート方針
- RG1 step review:
  - S01-S03 は code-reviewer。
  - S90 は spec-reviewer。
  - pass 条件: `review_status: pass`。
- QG1 final QA:
  - qa-reviewer が closure coverage と missing high-value tests を確認する。
- SG1 final spec review:
  - spec-reviewer が requirement / design / plan / report / implementation / tests / docs の整合を確認する。

## 実装ステップ

### 実装ステップ S01 — profile manifest / domain composer
- behavior goal:
  - profile preset から artifact kind ごとの managed section set を決定し、Markdown text へ additive に適用できる pure domain composer を追加する。
- allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/artifact_composer.py`
  - `src/spec_dock/assets/spec_dock/templates/assurance/profile-sections.json`
  - `tests/unit/domain/test_artifact_composer.py`
- forbidden changes:
  - CLI command wiring、workflow state、GitHub review。
- test obligation:
  - closure id: tc-001, tc-002, tc-003, tc-005。
  - red-required: Lite / Standard / Strict / Critical profile fixtures、idempotence、no-overwrite、downgrade no deletion、marker conflict。
- Green 検証:
  - `uv run pytest tests/unit/domain/test_artifact_composer.py`
- reviewer focus:
  - typed manifest boundary、marker safety、no-overwrite semantics。
- report evidence destination:
  - `report.md` S01 session log、TDD evidence、Step Contract Closure、Test Contract Closure、Closure Coverage、Reviewer Gate Status、Step Commit Gate。
- step commit / no-op gate:
  - S01 は code-reviewer pass 後に S01 scope のみで commit する。
  - no-op は、manifest / composer が既存実装で全 closure を満たす場合に限り、checked files、diff-clean command、reviewer pass を report に記録して approved-no-op とする。
- amendment trigger:
  - profile set、managed marker grammar、section deletion policy、or artifact list を変更する必要が出た場合は plan amendment と fresh spec-reviewer re-review を行う。

#### 委任契約（delegation contract）
- 委任ロール:
  - dev-coder。
- 入力 docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - accepted ADRs
  - existing Assurance runtime files。
- 許可 paths:
  - S01 allowed paths と同じ。
- 禁止 changes:
  - CLI command wiring、workflow state、GitHub review、dogfooding mirror direct edit。
- 受け入れ条件:
  - tc-001 / tc-002 / tc-003 / tc-005 が pass。
- 必須 tests または docs-only verification:
  - `uv run pytest tests/unit/domain/test_artifact_composer.py`
- reviewer focus:
  - code-reviewer: pure domain rules、typed manifest、marker conflict safety。
- 必須出力:
  - changed files、verification result、unresolved risks、Ledger Note または no material decision statement。
- 停止条件:
  - Markdown marker grammar が destructive になる、profile authority が ADR と衝突する、test が実行不能。

#### 具体テストケース一覧
- `tc-s01-001` acceptance: Lite / Standard / Strict / Critical profile fixtures
  - 前提: profile manifest に 4 profile の section fragments がある。
  - 操作: 各 `authorized_profile` で composer を実行する。
  - 期待結果: profile ごとの必要 section set が返る。`lite_candidate=true` だけでは Lite section set にならない。
  - 失敗検出: explicit Lite ambiguity、candidate authority 混入、profile mapping 欠落。
  - 検証方法: domain unit test。
  - 関連 closure id: tc-001
- `tc-s01-002` invariant: compose twice is idempotent
  - 前提: pristine Markdown に composer を一度適用済み。
  - 操作: 同じ manifest / profile / artifact kind で再実行する。
  - 期待結果: 2回目の output は1回目と同一。
  - 失敗検出: unstable marker / ordering / whitespace。
  - 検証方法: domain unit test。
  - 関連 closure id: tc-002
- `tc-s01-003` invariant: substantive body and downgrade are preserved
  - 前提: managed section 内に substantive body、または stronger profile section が存在する。
  - 操作: composer を実行する。
  - 期待結果: substantive body は上書きされず、stronger section は削除されない。
  - 失敗検出: human-authored content loss / automatic downgrade deletion。
  - 検証方法: domain unit test。
  - 関連 closure id: tc-003
- `tc-s01-004` negative: marker conflict stops composition
  - 前提: duplicated / unclosed / mismatched managed marker を持つ artifact text。
  - 操作: composer を実行する。
  - 期待結果: conflict error を返し、output text を生成しない。
  - 失敗検出: corrupt markdown write。
  - 検証方法: domain unit test。
  - 関連 closure id: tc-005

### 実装ステップ S02 — compose CLI vertical slice
- behavior goal:
  - `assurance compose --artifact {design,plan,report,all}` が active / explicit issue artifact を materialize し、result を text / JSON で返す。
- allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/assurance.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/assurance.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/artifact_store.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/assurance_text.py`
  - `tests/cli_runtime/test_assurance_compose.py`
- forbidden changes:
  - Step routing、GitHub review、automatic Lite default。
- test obligation:
  - closure id: tc-002, tc-003, tc-004, tc-005。
  - red-required: CLI apply / dry-run / missing assurance / invalid assurance / marker conflict / git clean on second compose。
- Green 検証:
  - `uv run pytest tests/cli_runtime/test_assurance_compose.py`
- reviewer focus:
  - CLI contract、target resolution、artifact write safety、output consistency。
- report evidence destination:
  - `report.md` S02 session log、TDD evidence、Discovered Tests、Closure Delta、Step Contract Closure、Reviewer Gate Status、Step Commit Gate。
- step commit / no-op gate:
  - S02 は code-reviewer pass 後に S02 scope のみで commit する。
  - no-op は、CLI vertical slice が既存 command で全 closure を満たす場合に限り、checked contracts と diff-clean evidence を report に記録して approved-no-op とする。
- amendment trigger:
  - CLI command name / arguments / exit semantics、artifact write safety、missing/invalid assurance policy を変更する必要が出た場合は plan amendment と fresh spec-reviewer re-review を行う。

#### 委任契約（delegation contract）
- 委任ロール:
  - dev-coder。
- 入力 docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - S01 implementation and tests
  - existing `assurance show/classify/verify` command patterns。
- 許可 paths:
  - S02 allowed paths と同じ。
- 禁止 changes:
  - step routing、GitHub review、automatic Lite default、S03 stale binding policy。
- 受け入れ条件:
  - tc-002 / tc-003 / tc-004 / tc-005 が pass。
- 必須 tests または docs-only verification:
  - `uv run pytest tests/cli_runtime/test_assurance_compose.py`
- reviewer focus:
  - code-reviewer: CLI contract、non-destructive writes、target resolution、missing/invalid authority。
- 必須出力:
  - changed files、verification result、unresolved risks、Ledger Note または no material decision statement。
- 停止条件:
  - compose command must overwrite user content、missing/invalid assurance cannot fail closed、CLI contract needs redesign。

#### 具体テストケース一覧
- `tc-s02-001` acceptance: compose all materializes planning sections
  - 前提: active Issue に valid `assurance.json` があり、design / plan / report が pristine scaffold。
  - 操作: `assurance compose --artifact all --format json` を実行する。
  - 期待結果: changed paths に design / plan / report が含まれ、managed sections が追加される。
  - 失敗検出: artifact omission / wrong profile / missing output contract。
  - 検証方法: CLI runtime test。
  - 関連 closure id: tc-004
- `tc-s02-002` invariant: second compose leaves git clean
  - 前提: compose result を commit または baseline 化済み。
  - 操作: 同じ input で compose を再実行し、`git status --short` を確認する。
  - 期待結果: tracked diff が出ない。
  - 失敗検出: noisy generated diff。
  - 検証方法: CLI runtime test。
  - 関連 closure id: tc-002
- `tc-s02-003` negative: missing / schema-invalid assurance fails closed
  - 前提: `assurance.json` がない、または invalid JSON / schema。
  - 操作: `assurance compose --artifact all --format json` を実行する。
  - 期待結果: non-zero または `ok=false` で classify / repair guidance を返し、artifact は変更されない。
  - 失敗検出: unsafe planning handoff without authority。
  - 検証方法: CLI runtime test。
  - 関連 closure id: tc-004
- `tc-s02-004` negative: marker conflict keeps artifact unchanged
  - 前提: target artifact に壊れた managed marker がある。
  - 操作: compose を実行する。
  - 期待結果: conflict error、artifact content unchanged。
  - 失敗検出: corrupt markdown write。
  - 検証方法: CLI runtime test。
  - 関連 closure id: tc-005

### 実装ステップ S03 — stale source binding blocks execution
- behavior goal:
  - `requirement.md` / `design.md` / `plan.md` source binding hash mismatch を `assurance compose`、`assurance verify`、`workflow next issue-execution` で検出し、compose output と execution-ready を返さない。
  - S02 の compose command に stale authority blocking を統合する責務は S03 が持つ。
- allowed paths:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/assurance.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/assurance.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/assurance_store.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/workflow_state.py`
  - `tests/unit/infra/test_assurance_store.py`
  - `tests/cli_runtime/test_assurance_compose.py`
  - `tests/cli_runtime/test_workflow.py`
- forbidden changes:
  - Compose section content rules、profile manifest shape、GitHub review。
- test obligation:
  - closure id: tc-006。
  - red-required: classify -> edit requirement/design/plan -> compose invalid / verify invalid / workflow blocked。
- Green 検証:
  - `uv run pytest tests/unit/infra/test_assurance_store.py tests/cli_runtime/test_assurance_compose.py tests/cli_runtime/test_workflow.py`
- reviewer focus:
  - fail-closed semantics、source hash details、legacy missing contract compatibility。
- report evidence destination:
  - `report.md` S03 session log、stale binding test evidence、workflow blocking evidence、Reviewer Gate Status、Step Commit Gate。
- step commit / no-op gate:
  - S03 は code-reviewer pass 後に S03 scope のみで commit する。
  - no-op は、`assurance compose`、`assurance verify`、`workflow next` が既に stale source binding を fail-closed にしている場合に限り、証跡と reviewer pass を report に記録して approved-no-op とする。
- amendment trigger:
  - `assurance verify` status taxonomy、workflow state kind、legacy missing-contract compatibility を変更する必要が出た場合は plan amendment と fresh spec-reviewer re-review を行う。

#### 委任契約（delegation contract）
- 委任ロール:
  - dev-coder。
- 入力 docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - existing Assurance source binding implementation
  - I02 workflow state implementation。
- 許可 paths:
  - S03 allowed paths と同じ。
- 禁止 changes:
  - compose section content rules、GitHub review、automatic Lite default、profile manifest shape。
- 受け入れ条件:
  - tc-006 が `requirement.md` / `design.md` / `plan.md` の stale cases すべてで pass し、legacy missing contract compatibility が維持される。
- 必須 tests または docs-only verification:
  - `uv run pytest tests/unit/infra/test_assurance_store.py tests/cli_runtime/test_assurance_compose.py tests/cli_runtime/test_workflow.py`
- reviewer focus:
  - code-reviewer: fail-closed semantics、stale details、missing contract backward compatibility。
- 必須出力:
  - changed files、verification result、unresolved risks、Ledger Note または no material decision statement。
- 停止条件:
  - stale binding cannot be detected without changing assurance schema incompatibly、workflow state requires new profile semantics。

#### 具体テストケース一覧
- `tc-s03-001` negative: verify detects stale planning source binding
  - 前提: `assurance classify --stage requirement` 後に `requirement.md` / `design.md` / `plan.md` のいずれかを substantive change する。
  - 操作: 各 changed artifact case で `assurance verify --format json` を実行する。
  - 期待結果: invalid / stale reason と artifact kind を含む source binding details が返る。
  - 失敗検出: stale authority accepted as valid。
  - 検証方法: unit / CLI runtime test。
  - 関連 closure id: tc-006
- `tc-s03-002` negative: compose blocks stale authority
  - 前提: `requirement.md` / `design.md` / `plan.md` のいずれかが stale source binding の active Issue。
  - 操作: `assurance compose --artifact all --format json` を実行する。
  - 期待結果: non-zero または `ok=false`、`reason=stale_source_binding`、stale artifact details、artifact content unchanged。
  - 失敗検出: stale planning sections generated from old authority。
  - 検証方法: CLI runtime test。
  - 関連 closure id: tc-006
- `tc-s03-003` negative: workflow next blocks stale execution
  - 前提: `requirement.md` / `design.md` / `plan.md` のいずれかが stale source binding の active Issue。
  - 操作: `workflow next issue-execution --format json` を実行する。
  - 期待結果: `state` は execution-ready ではなく、repair / reclassify guidance を含む。
  - 失敗検出: stale planning authority execution。
  - 検証方法: CLI runtime test。
  - 関連 closure id: tc-006
- `tc-s03-004` compatibility: missing assurance remains strict legacy / classification-required
  - 前提: active Issue に `assurance.json` がない。
  - 操作: `assurance verify` と `workflow next issue-execution` を実行する。
  - 期待結果: existing I01/I02 missing-contract behavior が維持される。
  - 失敗検出: legacy compatibility regression。
  - 検証方法: existing + targeted tests。
  - 関連 closure id: tc-006

### ドキュメント影響の解消ステップ S90
- 対象:
  - dogfooding mirror runtime / templates。
- 対応:
  - `uv run python -m spec_dock.cli update .`
  - provider runtime parity diff。
  - provider template / mirror template parity diff。
  - `./spec-dock/scripts/spec-dock validate`
- review:
  - spec-reviewer。
- report evidence destination:
  - `report.md` S90 docs impact resolution、provider/mirror parity、generated artifact tracking check、Reviewer Gate Status、Step Commit Gate。
- step commit / no-op gate:
  - S90 は spec-reviewer pass 後に dogfooding mirror / report scope で commit する。
  - no-op は、provider changes が dogfooding mirror に影響しないことを parity diff と checked paths で示した場合のみ approved-no-op とする。
- amendment trigger:
  - shipped template layout、mirror update behavior、generated/tracked boundary を変更する必要が出た場合は plan amendment と fresh spec-reviewer re-review を行う。

#### 委任契約（delegation contract）
- 委任ロール:
  - orchestrator verification; doc-writer only if shipped docs/templates beyond mirror sync require authoring.
- 入力 docs:
  - `plan.md` S90
  - provider asset diff
  - dogfooding update output。
- 許可 paths:
  - `spec-dock/scripts/spec_dock_runtime/**`
  - `spec-dock/templates/assurance/**`
  - `spec-dock/active/issue/report.md`
- 禁止 changes:
  - provider source changes except reviewer-approved S90 fixes。
- 受け入れ条件:
  - tc-007 pass。
- 必須 tests または docs-only verification:
  - update command、parity diff、validate。
- reviewer focus:
  - spec-reviewer: provider/mirror parity、generated/tracked boundary、docs impact closure。
- 必須出力:
  - command evidence、changed mirror files、unresolved risks。
- 停止条件:
  - update produces unexpected destructive diff、parity mismatch remains。

#### 具体テストケース一覧
- `tc-s90-001` inspect-only: provider / mirror parity
  - 前提: S01-S03 provider changes are committed or staged for S90.
  - 操作: `uv run python -m spec_dock.cli update .` and parity diff.
  - 期待結果: provider runtime/templates and dogfooding mirror match.
  - 失敗検出: dogfooding drift.
  - 検証方法: command inspection.
  - 関連 closure id: tc-007
- `tc-s90-002` inspect-only: generated artifacts stay ignored
  - 前提: compose / workflow commands may create generated outputs.
  - 操作: `git status --short --ignored` for generated paths.
  - 期待結果: generated outputs are ignored or absent, not tracked.
  - 失敗検出: generated artifact committed as authority.
  - 検証方法: command inspection.
  - 関連 closure id: tc-007

### 最終品質ゲートステップ S99
- 必須 validation:
  - `uv run pytest tests/unit`
  - `uv run pytest tests/cli_runtime`
  - `make lint`
  - `./spec-dock/scripts/spec-dock validate`
  - provider/mirror parity diff。
- final QA gate:
  - qa-reviewer pass。
- final code review gate:
  - code-reviewer pass。
- final spec review gate:
  - spec-reviewer pass。
- final commit:
  - S99 は issue-wide final gate であり、S01-S03/S90 の step commit を置き換えない。
  - final report / reviewer-fix if any を最後の commit として記録する。

#### 委任契約（delegation contract）
- 委任ロール:
  - qa-reviewer, code-reviewer, spec-reviewer are read-only final gates.
- 入力 docs:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md`
  - full issue diff。
- 許可 paths:
  - final report / reviewer-fix only after explicit finding.
- 禁止 changes:
  - new feature scope、unreviewed catch-up implementation。
- 受け入れ条件:
  - tc-008 pass and all final reviewers pass.
- 必須 tests または docs-only verification:
  - full validation commands listed above.
- reviewer focus:
  - QA coverage、code correctness、spec/report traceability。
- 必須出力:
  - final reviewer verdicts, unresolved risks or none, final report ledger status.
- 停止条件:
  - any final reviewer fail, validation fail, dirty unexpected diff.

#### 具体テストケース一覧
- `tc-s99-001` final: full validation suite
  - 前提: S01-S90 closed.
  - 操作: unit / CLI runtime / lint / validate / parity diff.
  - 期待結果: all pass.
  - 失敗検出: integrated regression.
  - 検証方法: command execution.
  - 関連 closure id: tc-008
- `tc-s99-002` final: three final reviewer gates
  - 前提: full validation pass.
  - 操作: qa-reviewer, code-reviewer, spec-reviewer read-only reviews.
  - 期待結果: all `review_status=pass`.
  - 失敗検出: missing tests, code bug, spec traceability gap.
  - 検証方法: reviewer output.
  - 関連 closure id: tc-008

## 未確定事項
- なし。
