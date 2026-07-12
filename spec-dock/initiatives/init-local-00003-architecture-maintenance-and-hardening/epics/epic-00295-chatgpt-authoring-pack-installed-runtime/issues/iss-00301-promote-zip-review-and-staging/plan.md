---
種別: 実装計画書（Issue）
ID: "iss-00301"
タイトル: "Zip Review Staging"
関連GitHub: ["#301"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
依存: ["requirement.md", "design.md"]
親: ["epic-00295", "init-local-00003"]
Issue Grade: "standard"
---

# iss-00301 Zip Review Staging — Issue 実装計画書

## 1. Plan Readiness

必須入力:

- `requirement.md`: review / stage scope、non-scope、AC-001..AC-015 を定義済み。
- `design.md`: ZIP contract、authority scanner、tree fallback、stage output、presentation、compatibility boundary を定義済み。
- `report.md`: planning evidence / implementation evidence / reviewer gate / PR defer evidence の記録先。
- Issue-local draft artifacts: requirement/design/plan seeds。

実装開始前 gate:

- `spec-reviewer` が `requirement.md` / `design.md` / `plan.md` / `report.md` に対して fresh `pass` を返す。
- `./spec-dock/scripts/spec-dock assurance verify` が pass する。
- `./spec-dock/scripts/spec-dock guidance issue-execution` が `may_execute_approved_plan: true` を返す。

## 2. Change Surface

許可変更面:

| 種別 | パス | 許可する変更 |
| --- | --- | --- |
| runtime command | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/authoring.py` | `authoring pack review` / `stage` dispatch |
| CLI parser | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py` | deferred help から implemented help へ更新 |
| application | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/pack_review.py` | review orchestration |
| application | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/pack_stage.py` | stage orchestration |
| domain | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/zip_contract.py` | ZIP/tree safety contract |
| domain | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/authority_boundary.py` | forbidden claim / secret scanner |
| presentation | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/authoring_pack/*` | review/stage text/json rendering |
| compatibility script | `src/spec_dock/assets/spec_dock/scripts/authoring-pack/review_chatgpt_authoring_pack.py` | runtime contract delegation or parity |
| compatibility script | `src/spec_dock/assets/spec_dock/scripts/authoring-pack/stage_chatgpt_authoring_pack.py` | runtime contract delegation or parity |
| dogfood mirror | `spec-dock/scripts/spec_dock_runtime/**`, `spec-dock/scripts/authoring-pack/**` | provider-side changes copied for dogfood verification |
| tests | `tests/cli_runtime/test_authoring.py`, related fixtures under `tests/fixtures/authoring_pack/**` | focused regression coverage |
| issue docs | active issue `report.md` | observed evidence only |

禁止変更:

- ChatGPT backend invocation implementation。
- candidate validation / draft adoption validation / approval stop gate implementation。
- canonical docs への自動採用。
- `.assurance.json` manual mutation。
- hardcoded personal local wrapper path。
- reviewer pass / execution-ready / PR-ready / mergeable PR の自己主張。
- per-Issue PR creation。

## 3. Spec-Locked Closure Index

| Closure ID | Requirement | Design | 閉じる内容 | Verification |
| --- | --- | --- | --- | --- |
| CL-001 | AC-001 | DES-CLI-001 | `authoring pack review --help` implemented contract | `test_authoring_pack_review_help_exposes_implemented_contract` |
| CL-002 | AC-002 | DES-CLI-001 | `authoring pack stage --help` implemented contract | `test_authoring_pack_stage_help_exposes_implemented_contract` |
| CL-003 | AC-003 | DES-ZIP-001 | valid ZIP review pass and evidence-only authority retained | `test_authoring_pack_review_valid_zip_passes_with_evidence_only_authority` |
| CL-004 | AC-004 | DES-STAGE-001 | valid ZIP stage output includes report, dry-run diff, EAL candidate, owner marker | `test_authoring_pack_stage_valid_zip_writes_stage_outputs` |
| CL-005 | AC-005 | DES-ZIP-001 | unsafe ZIP is rejected before extraction | `test_authoring_pack_review_rejects_unsafe_zip_without_extracting` |
| CL-006 | AC-006 | DES-ZIP-002 | unsafe entry categories are rejected | parameterized unsafe fixture tests |
| CL-007 | AC-007 | DES-AUTH-001 | secret / raw transcript payloads are rejected | scanner tests |
| CL-008 | AC-008 | DES-AUTH-001 | forbidden authority claims are rejected, not warnings | scanner tests |
| CL-009 | AC-009 | DES-ZIP-002 | wrong root=`rejected`, metadata missing=`fail`, source hash mismatch=`stale` | negative fixture tests |
| CL-010 | AC-010 | DES-TREE-001 | tree fallback reports lower authority and missing central directory evidence | CLI JSON / test |
| CL-011 | AC-011 | DES-STAGE-001 | stage does not change canonical docs / active docs / `.assurance.json` | git diff / test |
| CL-012 | AC-012 | DES-PRES-001 | output distinguishes local validation from adoption/reviewer/ready claims | text/json output tests |
| CL-013 | AC-013 | DES-COMPAT-001 | provider and dogfood runtime smoke pass | focused pytest and CLI help |
| CL-014 | AC-014 | DES-COMPAT-001 | compatibility scripts have no hardcoded personal path and match runtime contract | inspection / script smoke |
| CL-015 | AC-015 | DES-WF-001 | no PR delivery; `iss-00307` defer evidence recorded | `report.md` evidence |

## 4. 実装ステップ

### S01 — Domain contract and fixtures

#### behavior goal

- ZIP / tree review result model、entry finding、stage result model を定義する。
- valid ZIP fixture と unsafe ZIP fixtures を用意する。
- required metadata と authority boundary fixture を用意する。

#### planned contract

- scope: domain result/status model、fixture builders、test helper utilities の追加。
- test obligation: valid ZIP、unsafe ZIP、mandatory metadata、authority boundary の最小 fixture を作り、後続 step の Red を支える。
- red or alternative evidence requirement: `covered-existing`。現時点では implemented command が deferred のため、fixture helper の sensitivity は S02 以降の Red で確認する。
- green verification: fixture builders が deterministic ZIP/tree を作り、後続 tests から利用できる。
- refactor guardrail: fixture utility は `tests/cli_runtime/test_authoring.py` または authoring fixture helper に限定し、production contract を先走って広げない。
- amendment trigger: fixture が parent Epic required metadata と一致しない、または status taxonomy を表現できない場合は plan amendment と spec re-review。

#### delegation contract

- delegated role: `dev-coder`
- input docs: `requirement.md`, `design.md`, `spec-dock/active/epic/design.md`, `tests/cli_runtime/test_authoring.py`
- allowed paths: `tests/cli_runtime/test_authoring.py`, `tests/fixtures/authoring_pack/**` if existing pattern requires it
- forbidden changes: runtime command implementation、canonical docs adoption、`.assurance.json` mutation
- acceptance criteria: CL-003, CL-005, CL-006, CL-009 の fixtures が後続 tests で参照できる
- required tests or docs-only verification: fixture construction inspection plus first failing CLI tests in S02
- reviewer focus: fixture が ZIP central directory / metadata / authority boundary を正しく表現しているか
- stop conditions: fixture が unsafe ZIP を extraction 前に検査できない形になっている場合
- output required: changed fixture/test helper paths and rationale

#### 具体テストケース一覧

- `tc-s01-001` alternative: valid ZIP fixture builder
  - 前提: required metadata と text payload を持つ `specdock-authoring-pack/` ZIP を生成する helper を追加する。
  - 操作: helper を呼び出す後続 test を追加できる状態にする。
  - 期待結果: generated ZIP は root と required metadata を含む。
  - 失敗検出: metadata / root が欠けると後続 S02 valid ZIP test が失敗する。
  - 検証方法: S02 の `test_authoring_pack_review_valid_zip_passes_with_evidence_only_authority` で観測する。
- `tc-s01-002` alternative: unsafe fixture seeds
  - 前提: path traversal、wrong root、metadata missing、source hash mismatch、forbidden authority claim の fixture を生成できる。
  - 操作: S02/S03 tests で各 fixture を review command に渡す。
  - 期待結果: expected status taxonomy を検査できる。
  - 失敗検出: fixture が不正に作られていると expected status と diagnostic が一致しない。
  - 検証方法: S02/S03 negative fixture tests。

#### step closure contract

- closures: CL-003, CL-005, CL-006, CL-009 の test input が準備される。
- report evidence destination: `report.md` の TDD evidence、Step Contract Closure、Test Contract Closure。
- step gate: fixture helper と後続 Red tests が commit candidate に含まれる。

### S02 — ZIP central directory and metadata review

#### behavior goal

- ZIP を extraction せず central directory だけで root / path / entry properties を検査する。
- required metadata / source hash / size / suffix / encryption / symlink / nested archive を親 Epic status taxonomy に従って map する。

#### planned contract

- scope: `zip_contract.py` と `pack_review.py` の ZIP review path。
- test obligation: valid ZIP pass、unsafe entry rejected before extraction、wrong root rejected、metadata missing fail、source hash mismatch stale。
- red or alternative evidence requirement: `red-required` for first CLI-visible valid ZIP / wrong-root test; remaining cases can be parameterized after first Red.
- green verification: CLI JSON result includes deterministic `status`, `findings`, `input_kind=zip`, and no extraction side effect.
- refactor guardrail: ZIP extraction must not occur inside review. Any extraction logic belongs to S05 stage only.
- amendment trigger: new status outside `pass/fail/stale/rejected/blocked` or extraction-before-review requires plan/design amendment.

#### delegation contract

- delegated role: `dev-coder`
- input docs: `requirement.md`, `design.md`, `plan.md`, parent Epic design status taxonomy
- allowed paths: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/zip_contract.py`, `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/pack_review.py`, focused tests
- forbidden changes: stage extraction, adoption, approval, GitHub mutation, PR delivery
- acceptance criteria: CL-003, CL-005, CL-006, CL-009
- required tests or docs-only verification: focused pytest for valid and negative ZIP fixtures
- reviewer focus: extraction-before-review absence and status taxonomy alignment
- stop conditions: central directory API cannot detect required unsafe property; return to design
- output required: implementation summary, changed files, test output

#### 具体テストケース一覧

- `tc-s02-001` acceptance: valid ZIP review passes
  - 前提: valid `specdock-authoring-pack/` ZIP fixture exists.
  - 操作: `spec-dock authoring pack review --input <valid.zip> --format json`
  - 期待結果: `status=pass`, `authority=evidence_only`, `adoption_status=unreviewed`.
  - 失敗検出: valid pack が rejected/fail/stale になる、または adoption/reviewer claim が出る。
  - 検証方法: `test_authoring_pack_review_valid_zip_passes_with_evidence_only_authority`.
- `tc-s02-002` negative: unsafe ZIP is not extracted
  - 前提: path traversal ZIP includes a sentinel path that would write outside stage if extracted.
  - 操作: review command を実行する。
  - 期待結果: `status=rejected`; sentinel file is absent.
  - 失敗検出: review 後に sentinel file が存在する。
  - 検証方法: `test_authoring_pack_review_rejects_unsafe_zip_without_extracting`.
- `tc-s02-003` negative: taxonomy-aligned metadata failures
  - 前提: wrong root、metadata missing、source hash mismatch fixtures。
  - 操作: each fixture を review command に渡す。
  - 期待結果: wrong root=`rejected`, metadata missing=`fail`, source hash mismatch=`stale`.
  - 失敗検出: Issue docs と Epic design の taxonomy が再びずれる。
  - 検証方法: parameterized negative fixture test。

#### step closure contract

- closures: CL-003, CL-005, CL-006, CL-009
- report evidence destination: TDD evidence、Closure Coverage、Discovered Tests。
- step gate: focused tests pass before S03.

### S03 — Authority boundary scanner

#### behavior goal

- secret-looking data、raw transcript、credential / token / private key、forbidden authority claim を reject する。
- warning downgrade せず `rejected` に map する。

#### planned contract

- scope: `authority_boundary.py` and review integration.
- test obligation: secret-looking content、raw transcript、forbidden adoption/reviewer/ready claims。
- red or alternative evidence requirement: `red-required` for forbidden authority claim; scanner-only unit can be added if CLI wiring is too broad.
- green verification: finding severity maps to `status=rejected` and renderer does not downgrade to warning.
- refactor guardrail: scanner must not store raw secret / raw transcript into durable report.
- amendment trigger: required scanner categories expand beyond Epic requirement; update requirement/design/plan and re-review.

#### delegation contract

- delegated role: `dev-coder`
- input docs: `requirement.md`, `design.md`, `prompt_pack_contract.py`
- allowed paths: `authority_boundary.py`, `pack_review.py`, renderer/tests as needed
- forbidden changes: redaction policy broadening unrelated to review/stage, adoption logic
- acceptance criteria: CL-007, CL-008, CL-012
- required tests or docs-only verification: scanner/CLI tests for each forbidden class
- reviewer focus: no forbidden authority claim can be warning-only
- stop conditions: detecting a claim requires ambiguous natural language classification beyond deterministic patterns
- output required: scanner categories and test coverage summary

#### 具体テストケース一覧

- `tc-s03-001` negative: forbidden authority claim
  - 前提: fixture text claims reviewer pass or canonical adoption.
  - 操作: review command を実行する。
  - 期待結果: `status=rejected`; finding category is forbidden authority claim.
  - 失敗検出: status が pass/fail/warning-only になる。
  - 検証方法: `test_authoring_pack_review_rejects_forbidden_authority_claim`.
- `tc-s03-002` negative: secret/raw transcript
  - 前提: fixture contains token/private-key-like text or raw ChatGPT transcript marker.
  - 操作: review command を実行する。
  - 期待結果: `status=rejected`; durable output does not persist raw secret body.
  - 失敗検出: secret body appears in report or status is not rejected.
  - 検証方法: scanner tests and CLI JSON output tests.

#### step closure contract

- closures: CL-007, CL-008, CL-012
- report evidence destination: TDD evidence、Test Contract Closure。
- step gate: scanner tests pass before S04/S05.

### S04 — Tree fallback review

#### behavior goal

- tree input を検査可能な範囲で review する。
- `fallback=true`、`authority_level=lower_than_zip_review`、`missing_evidence=["zip-central-directory"]` を diagnostics に含める。

#### planned contract

- scope: tree input branch in review service.
- test obligation: tree input valid-ish review, lower authority diagnostics, no ZIP-equivalent claim.
- red or alternative evidence requirement: `red-required` for lower authority diagnostic.
- green verification: JSON output contains `input_kind=tree`, `fallback=true`, `missing_evidence`.
- refactor guardrail: tree fallback must reuse safety scanner and metadata validation where possible.
- amendment trigger: tree fallback needs canonical adoption or approval logic; stop and re-scope.

#### delegation contract

- delegated role: `dev-coder`
- input docs: `requirement.md`, `design.md`
- allowed paths: `pack_review.py`, `zip_contract.py`, renderer/tests
- forbidden changes: treating tree fallback as ZIP review pass
- acceptance criteria: CL-010, CL-012
- required tests or docs-only verification: CLI JSON tree fallback test
- reviewer focus: lower authority is explicit and machine-readable
- stop conditions: tree input cannot be safely bounded without ZIP metadata
- output required: diagnostic fields and test output

#### 具体テストケース一覧

- `tc-s04-001` acceptance: tree fallback lower authority
  - 前提: a directory shaped like `specdock-authoring-pack/` exists.
  - 操作: review command に tree path を渡す。
  - 期待結果: `input_kind=tree`, `fallback=true`, `authority_level=lower_than_zip_review`, `missing_evidence=["zip-central-directory"]`.
  - 失敗検出: ZIP review pass と同格の diagnostics になる。
  - 検証方法: `test_authoring_pack_review_tree_fallback_reports_lower_authority`.

#### step closure contract

- closures: CL-010, CL-012
- report evidence destination: TDD evidence、Closure Coverage。
- step gate: tree fallback test pass before S05.

### S05 — Stage orchestration

#### behavior goal

- review pass 済み input だけを stage する。
- stage target safety を検査する。
- staged tree、review report、dry-run diff、EAL candidate、ownership marker を生成する。
- canonical docs / active docs / `.assurance.json` を変更しない。

#### planned contract

- scope: `pack_stage.py` stage path and stage renderer.
- test obligation: valid ZIP stage output, reject non-pass review input, reject canonical/active/assurance target, unchanged canonical docs.
- red or alternative evidence requirement: `red-required` for valid stage output; `covered-existing` for review failure reuse after S02/S03.
- green verification: stage directory contains required artifacts and owner marker; git diff for canonical docs unchanged.
- refactor guardrail: stage must not mutate source input, canonical docs, active docs, `.assurance.json`.
- amendment trigger: stage needs adoption-map interpretation beyond EAL candidate rendering; defer to later Issue and re-review if needed.

#### delegation contract

- delegated role: `dev-coder`
- input docs: `requirement.md`, `design.md`, S02/S03 review contract
- allowed paths: `pack_stage.py`, renderer/tests, compatibility script if needed
- forbidden changes: writing canonical docs, active docs, `.assurance.json`, issue/epic node creation
- acceptance criteria: CL-004, CL-011, CL-012
- required tests or docs-only verification: stage output and canonical unchanged tests
- reviewer focus: stage output cannot be mistaken for adoption
- stop conditions: cannot produce safe stage without extracting before review pass
- output required: stage output inventory and canonical unchanged evidence

#### 具体テストケース一覧

- `tc-s05-001` acceptance: valid ZIP stage writes evidence
  - 前提: valid ZIP review passes.
  - 操作: `spec-dock authoring pack stage --input <valid.zip> --stage-dir <tmp-stage> --format json`
  - 期待結果: staged tree、review report、dry-run diff、EAL candidate、owner marker が生成される。
  - 失敗検出: required stage artifact missing or status not pass.
  - 検証方法: `test_authoring_pack_stage_valid_zip_writes_stage_outputs`.
- `tc-s05-002` invariant: canonical unchanged
  - 前提: active issue/epic docs and `.assurance.json` hashes recorded before stage.
  - 操作: valid stage command を実行する。
  - 期待結果: recorded canonical hashes unchanged.
  - 失敗検出: canonical docs or assurance file changes.
  - 検証方法: `test_authoring_pack_stage_does_not_change_canonical_docs`.
- `tc-s05-003` negative: unsafe stage target
  - 前提: stage dir points to canonical docs, active docs, `.assurance.json`, symlink, or non-owned existing stage.
  - 操作: stage command を実行する。
  - 期待結果: `status=rejected`; no stage write.
  - 失敗検出: unsafe target is written.
  - 検証方法: parameterized stage target safety test.

#### step closure contract

- closures: CL-004, CL-011, CL-012
- report evidence destination: TDD evidence、Closure Coverage、changed files inventory。
- step gate: stage tests pass before S06.

### S06 — CLI integration and presentation

#### behavior goal

- `authoring pack review` / `stage` を parser / command handler に接続する。
- text/json renderer を実装する。
- deferred command registration を削除または対象 command から外す。

#### planned contract

- scope: parser, command dispatch, renderer.
- test obligation: help output, JSON/text output, no deferred diagnostic for implemented commands.
- red or alternative evidence requirement: `red-required` for help no longer deferred.
- green verification: `--help` outputs options and command invocation routes to services.
- refactor guardrail: unrelated deferred commands remain deferred.
- amendment trigger: command option names conflict with existing authoring CLI or Epic design; update docs and re-review.

#### delegation contract

- delegated role: `dev-coder`
- input docs: `requirement.md`, `design.md`, existing parser/command tests
- allowed paths: `commands/authoring.py`, `cli/parser.py`, renderer/tests
- forbidden changes: implementing out-of-scope authoring commands, changing backend invoke contract
- acceptance criteria: CL-001, CL-002, CL-012
- required tests or docs-only verification: help tests and focused CLI tests
- reviewer focus: command surface matches docs and no false authority claims
- stop conditions: parser architecture requires broad refactor beyond this Issue
- output required: help output snippets and test output

#### 具体テストケース一覧

- `tc-s06-001` acceptance: review help implemented
  - 前提: runtime command parser is loaded.
  - 操作: `spec-dock authoring pack review --help`
  - 期待結果: `--input`, `--format`, `--evidence-mode`, `--report-path` が表示され、deferred skeleton wording が出ない。
  - 失敗検出: deferred diagnostic or missing option.
  - 検証方法: `test_authoring_pack_review_help_exposes_implemented_contract`.
- `tc-s06-002` acceptance: stage help implemented
  - 前提: runtime command parser is loaded.
  - 操作: `spec-dock authoring pack stage --help`
  - 期待結果: `--input`, `--stage-dir`, `--dry-run`, `--format` が表示され、deferred skeleton wording が出ない。
  - 失敗検出: deferred diagnostic or missing option.
  - 検証方法: `test_authoring_pack_stage_help_exposes_implemented_contract`.

#### step closure contract

- closures: CL-001, CL-002, CL-012
- report evidence destination: TDD evidence、Test Contract Closure。
- step gate: help tests pass before S07.

### S07 — Compatibility scripts and dogfood mirror

#### behavior goal

- provider-side compatibility scripts を runtime service へ委譲、または parity を維持する。
- dogfood mirror を同期する。

#### planned contract

- scope: provider compatibility scripts and dogfood runtime mirror.
- test obligation: no hardcoded personal path, script command parity, provider/dogfood smoke.
- red or alternative evidence requirement: `inspect-only` for hardcoded path absence, `manual-required` smoke for dogfood mirror if direct import path differs.
- green verification: focused pytest and CLI help pass on dogfood runtime.
- refactor guardrail: mirror changes must correspond to provider source changes.
- amendment trigger: installed layout cannot expose scripts from provider source as planned; return to design.

#### delegation contract

- delegated role: `dev-coder`
- input docs: `requirement.md`, `design.md`, provider/dogfood source map from AGENTS.md
- allowed paths: `src/spec_dock/assets/spec_dock/scripts/authoring-pack/*`, `spec-dock/scripts/authoring-pack/*`, dogfood mirrored runtime files, tests
- forbidden changes: local absolute wrapper defaults, installation architecture redesign
- acceptance criteria: CL-013, CL-014
- required tests or docs-only verification: focused pytest, CLI smoke, `rg` for local absolute wrapper path
- reviewer focus: provider/dogfood parity and no personal local dependency
- stop conditions: compatibility scripts need a broader install-surface redesign
- output required: provider/dogfood changed file list and smoke output

#### 具体テストケース一覧

- `tc-s07-001` smoke: provider and dogfood help
  - 前提: provider source copied or mirrored to dogfood runtime.
  - 操作: `./spec-dock/scripts/spec-dock authoring pack review --help` and `./spec-dock/scripts/spec-dock authoring pack stage --help`
  - 期待結果: both commands display implemented help.
  - 失敗検出: dogfood runtime still shows deferred command.
  - 検証方法: CLI smoke plus focused pytest.
- `tc-s07-002` inspection: no personal wrapper path
  - 前提: compatibility scripts exist or are added.
  - 操作: `rg -n "/Users/.+oracle-chatgpt|\\.codex/skills/chatgpt-use" src/spec_dock/assets/spec_dock/scripts/authoring-pack spec-dock/scripts/authoring-pack`
  - 期待結果: no hardcoded personal backend path.
  - 失敗検出: local absolute wrapper dependency is committed.
  - 検証方法: inspection command output.

#### step closure contract

- closures: CL-013, CL-014
- report evidence destination: TDD evidence、changed files inventory、Final Quality Gate。
- step gate: focused pytest, CLI smoke, inspection pass before S90.

### S90 — Report and workflow evidence

成果:

- `report.md` に planning adoption、implementation evidence、reviewer gates、PR defer evidence を記録する。

主な closure:

- CL-015

検証:

- `./spec-dock/scripts/spec-dock validate`
- `./spec-dock/scripts/spec-dock assurance verify`
- `git diff --check`

### S99 — Final local quality gate

成果:

- code-reviewer、qa-reviewer、spec-reviewer の fresh pass。
- commit candidate を作る。
- PR delivery は行わず `iss-00307` へ defer する。

検証:

- `uv run pytest tests/cli_runtime/test_authoring.py -q`
- `./spec-dock/scripts/spec-dock validate`
- `./spec-dock/scripts/spec-dock assurance verify`
- `git diff --check`
- `./spec-dock/scripts/spec-dock guidance issue-execution`

## 5. Behavior Backlog

| Behavior | Milestone | 内容 | Closures |
| --- | --- | --- | --- |
| B-001 | S01/S02 | valid ZIP を evidence-only review pass にする | CL-003 |
| B-002 | S02 | unsafe ZIP entry を extraction 前に reject する | CL-005, CL-006 |
| B-003 | S02 | wrong root / missing metadata / hash mismatch を親 Epic status taxonomy に従って分類する | CL-009 |
| B-004 | S03 | secret/raw transcript/forbidden authority claim を reject する | CL-007, CL-008 |
| B-005 | S04 | tree fallback を lower authority evidence として分類する | CL-010 |
| B-006 | S05 | review pass 済み pack を staged evidence として配置する | CL-004 |
| B-007 | S05 | stage が canonical docs / `.assurance.json` を変更しない | CL-011 |
| B-008 | S06 | CLI help / text/json output が implemented contract を示す | CL-001, CL-002, CL-012 |
| B-009 | S07 | provider / dogfood / compatibility script が同じ contract を満たす | CL-013, CL-014 |
| B-010 | S90/S99 | no-per-Issue-PR relay evidence を残す | CL-015 |

## 6. 具体テストケース

| Test ID | 目的 | 期待 |
| --- | --- | --- |
| TC-001 | review help contract | `authoring pack review` options が表示され、deferred message が出ない |
| TC-002 | stage help contract | `authoring pack stage` options が表示され、deferred message が出ない |
| TC-003 | valid ZIP review | status `pass`; authority evidence-only; adoption unreviewed |
| TC-004 | valid ZIP stage | staged tree、review report、dry-run diff、EAL candidate、owner marker が生成される |
| TC-005 | no extraction before safe review | unsafe ZIP rejection 後に sentinel extracted file が存在しない |
| TC-006 | path traversal | rejected |
| TC-007 | absolute / host-local path | rejected |
| TC-008 | hidden path | rejected |
| TC-009 | unsupported suffix / executable | rejected |
| TC-010 | encrypted / symlink / nested archive | rejected |
| TC-011 | binary / oversized entry | rejected |
| TC-012 | missing metadata / wrong root | metadata missing=`fail`; wrong root=`rejected` |
| TC-013 | source hash mismatch | `stale` |
| TC-014 | secret-looking / private key / token | rejected |
| TC-015 | raw transcript | rejected |
| TC-016 | forbidden authority claim | rejected; warning ではない |
| TC-017 | tree fallback | fallback lower authority diagnostics |
| TC-018 | canonical unchanged | stage 後に canonical docs / `.assurance.json` が変わらない |
| TC-019 | compatibility scripts | hardcoded personal path なし、runtime contract parity |

## 7. Delegation Contract

実装は `dev-coder` へ委任可能だが、親 orchestrator は次を保持する。

- Canonical docs の採用判断。
- `report.md` evidence integration。
- reviewer gate の依頼と結果記録。
- `issue finish` 判断。

Parent direct implementation exception を使う場合は `report.md` に理由、許可範囲、検証、reviewer gate を記録する。

## 8. Stop Conditions

- review / stage が canonical docs adoption へ scope 拡張しそうになった場合。
- `.assurance.json`、reviewer pass、execution-ready、PR-ready を command が自己主張しそうになった場合。
- unsafe ZIP を extraction 後に検査する設計になった場合。
- raw secret / raw transcript を durable docs に保存する必要が出た場合。
- provider source と dogfood mirror の同期方針が不明な場合。
- focused tests が既存 authoring command behavior を広く壊す場合。

## 9. Verification Queue

最低限の完了検証:

```bash
uv run pytest tests/cli_runtime/test_authoring.py -q
./spec-dock/scripts/spec-dock authoring pack review --help
./spec-dock/scripts/spec-dock authoring pack stage --help
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock assurance verify
git diff --check
```

必要に応じて追加:

```bash
uv run pytest tests/unit/infra/test_init_update.py -q
```

## 10. PR Delivery Policy

この Issue では PR を作成しない。全中間 Issue を `issue start` -> planning -> execution -> local quality gate -> `issue finish` のリレーで進め、Epic 単位の mergeable PR は final quality gate Issue `iss-00307` で作成する。

`iss-00301` finish 前には、`report.md` に次を記録する。

- no-per-Issue-PR rationale。
- local verification summary。
- reviewer gate summary。
- `iss-00307` への PR delivery defer evidence。
