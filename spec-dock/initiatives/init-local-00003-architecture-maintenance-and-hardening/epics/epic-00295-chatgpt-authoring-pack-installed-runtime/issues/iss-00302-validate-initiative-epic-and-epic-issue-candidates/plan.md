---
種別: 実装計画書（Issue）
ID: "iss-00302"
タイトル: "Initiative Epic Validation"
関連GitHub: ["#302"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
依存: ["requirement.md", "design.md"]
親: ["epic-00295", "init-local-00003"]
Issue Grade: "standard"
PR方針: "no-per-Issue-PR; defer to iss-00307"
---

# iss-00302 Initiative Epic Validation — Issue 実装計画書

## 1. Plan Readiness

実装開始前 gate:

- `requirement.md` / `design.md` / `plan.md` が具体化されている。
- `assurance classify --stage requirement` が `authorized_profile=standard` を返す。
- `assurance compose --artifact all` 済みで、Standard profile の report scaffold が存在する。
- Fresh `spec-reviewer` が canonical docs と report を `pass` する。
- `./spec-dock/scripts/spec-dock assurance verify` が pass する。
- `./spec-dock/scripts/spec-dock guidance issue-execution` が `may_execute_approved_plan: true` を返す。

## 2. Change Surface

許可変更面:

| 種別 | パス | 変更 |
| --- | --- | --- |
| commands | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/authoring.py` | validate command dispatch / args |
| cli parser | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py` | promoted command help |
| application | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/candidate_validation.py` | candidate validation orchestration |
| domain | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/candidate_contract.py` | candidate schema / status / safety contract |
| presentation | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/authoring_pack/candidate_validation_renderer.py` | text/json renderer |
| compatibility | `src/spec_dock/assets/spec_dock/scripts/authoring-pack/validate_issue_candidates.py` | runtime wrapper / parity |
| compatibility | `src/spec_dock/assets/spec_dock/scripts/authoring-pack/validate_initiative_epic_candidates.py` | runtime wrapper |
| dogfood mirror | `spec-dock/scripts/**` | provider-side changes copied |
| tests | `tests/cli_runtime/test_authoring.py` and fixtures if needed | positive/negative coverage |
| issue docs | `report.md` | evidence ledger |

禁止変更:

- node creation。
- canonical docs adoption。
- `.assurance.json` mutation。
- `authorized_profile` 決定。
- reviewer pass / execution-ready / PR-ready / mergeable PR claim。
- `authoring validate issue-draft-adoption` / `selected-skeleton-fill` / `approval check` 実装。
- per-Issue PR creation。

## 3. Spec-Locked Closure Index

| Closure ID | Requirement | Design | 閉じる内容 | Verification |
| --- | --- | --- | --- | --- |
| CL-001 | AC-001 | DES-CLI-001 | Initiative -> Epic validate command implemented help/output | CLI help / JSON test |
| CL-002 | AC-002 | DES-CLI-001 | Epic -> Issue validate command implemented help/output | CLI help / JSON test |
| CL-003 | AC-003 | DES-CLI-001 | remaining deferred commands still fail closed | deferred command tests |
| CL-004 | AC-004 | DES-SCHEMA-INIT-001 | valid Initiative -> Epic fixture passes evidence-only | positive fixture |
| CL-005 | AC-005 | DES-SCHEMA-ISSUE-001 | valid Epic -> Issue fixture passes advisory-only profile | positive fixture |
| CL-006 | AC-006 | DES-VAL-001 | malformed / missing schema maps to fail | negative fixture |
| CL-007 | AC-007 | DES-VAL-002 | duplicate / overlap diagnostics deterministic | negative fixture |
| CL-008 | AC-008 | DES-SAFE-001 | unsafe paths / file categories rejected | negative fixture |
| CL-009 | AC-009 | DES-SAFE-001 | secret/raw transcript rejected and redacted | negative fixture |
| CL-010 | AC-010 | DES-SAFE-001 | forbidden authority claims rejected | negative fixture |
| CL-011 | AC-011 | DES-SCHEMA-ISSUE-001 | non-null authorized_profile / non-advisory profile rejected | negative fixture |
| CL-012 | AC-012 | DES-IN-001 | source/parent/review mismatch stale | negative fixture |
| CL-013 | AC-013 | DES-OUT-001 | unsafe report path rejected and not written | filesystem test |
| CL-014 | AC-014 | DES-AUTH-001 | output separates validation from authority | text/json tests |
| CL-015 | AC-015 | DES-MIRROR-001 | provider and dogfood runtime smoke pass | subprocess tests |
| CL-016 | AC-016 | DES-MIRROR-001 | pytest / validate / diff check pass | local verification |
| CL-017 | AC-017 | DES-RELAY-001 | no PR delivery; defer to `iss-00307` | report finish evidence |

## 4. 実装ステップ

### Per-step evidence contract

S01-S06 はそれぞれ次の evidence contract を満たしてから step closure とする。

- Red / alternative evidence:
  - New behavior の場合は失敗する focused test を先に追加する。
  - 既存 test が Red 代替になる場合は、対象 test 名と期待する failure / deferred behavior を `report.md` の TDD table に記録する。
  - inspect-only の場合は、なぜ Red test が不適切か、どの artifact / command output が代替証跡かを記録する。
- Green verification:
  - 各 step の Tests に列挙した focused test または同等の command を実行し、stdout / exit status を `report.md` に記録する。
  - Green のあとに authority / no-mutation flags が崩れていないことを確認する。
- Refactor guardrail:
  - Provider-side source of truth と dogfood mirror の差分意図を確認する。
  - Unrelated runtime / template / canonical docs の変更を混ぜない。
  - Refactor が不要な場合も `approved-no-op` と根拠を `report.md` に残す。
- Report evidence destination:
  - TDD evidence は `report.md` の `テスト駆動開発証跡`。
  - Discovered tests / risks は `発見されたテスト / リスク`。
  - Closure evidence は `ステップ契約の完了証跡` と `クロージャ網羅`。
  - Test aliases or changed closure ids は `クロージャ差分`。
- Amendment trigger:
  - Requirement / design / plan contract と異なる behavior、status mapping、schema field、authority boundary、report path safety を発見した場合は implementation を止め、該当 artifact を修正して fresh spec-review を通す。
- Delegation / reviewer handoff:
  - S01-S06 の実装中は parent orchestrator が report evidence を維持する。
  - 実装後、`code-reviewer` と `qa-reviewer` は S07 の gate として実行し、findings は `report.md` に記録する。

### S01 — Command promotion tests and fixture builders

Goal:

- `initiative-epic-candidates` / `epic-issue-candidates` を `_DEFERRED_COMMANDS` から外す前提の Red tests を追加する。
- Candidate stage / pack fixture helpers を追加する。

Tasks:

1. `_DEFERRED_COMMANDS` から promoted command を分離する。
2. help exposes implemented contract tests を追加する。
3. candidate stage dir / review report / candidate index / candidate payload / draft docs fixture helper を追加する。

Tests:

- `test_authoring_validate_initiative_epic_candidates_help_exposes_implemented_contract`
- `test_authoring_validate_epic_issue_candidates_help_exposes_implemented_contract`

Closure: CL-001, CL-002, CL-003 input.

### S02 — Domain candidate contract

Goal:

- candidate validation status、result、finding、safe loader、schema validator、comparison validator を domain contract として定義する。

Tasks:

1. `candidate_contract.py` を追加する。
2. authority constants は `prompt_pack_contract.py` / existing authoring contract と整合させる。
3. safe relative path / JSON object loader / Markdown loader / status precedence を実装する。
4. duplicate ID/title/slug、scope signature、scope/non-scope overlap を sorted deterministic に検査する。

Tests:

- malformed index JSON -> `fail`
- missing required fields -> `fail`
- duplicate IDs/titles/slugs -> `fail`
- overlap -> `fail`
- unsafe paths -> `rejected`

Closure: CL-006, CL-007, CL-008.

### S03 — Authority and sensitivity validation

Goal:

- candidate JSON / Markdown で forbidden authority claim、secret/raw transcript、non-null `authorized_profile`、non-advisory profile を reject する。

Tasks:

1. Existing `authority_boundary.py` scanner を reuse/align する。
2. `authorized_profile` non-null を `rejected` にする。
3. `profile_recommendation.advisory_only != true` / `ignored_for_authority != true` を reject する。
4. raw secret value を result/report に含めない。

Tests:

- secret text -> `rejected`, raw value absent
- raw transcript -> `rejected`
- forbidden claim -> `rejected`
- non-null `authorized_profile` -> `rejected`
- profile recommendation missing advisory-only -> `rejected`
- unsupported `grade_recommendation.grade` -> `fail`
- unsupported `profile_recommendation.profile` -> `fail`

Closure: CL-009, CL-010, CL-011, CL-014.

### S04 — Application orchestration

Goal:

- staged evidence input、review report gate、source/parent/digest stale gate、safe report path を application use case として実装する。

Tasks:

1. `candidate_validation.py` を追加する。
2. `<input>/specdock-authoring-pack` or `<input>` root discovery を実装する。
3. `--review-report` / `<input>/review-report.json` / `<input>/../review-report.json` discovery を実装する。
4. review report status / authority boundary を検査する。
5. expected parent Initiative/Epic と candidate parent trace を照合する。
6. expected source manifest hash と observed source manifest hash を照合する。
7. optional report path guard を review/stage と同等に実装する。

Tests:

- missing review report -> `blocked`
- malformed review report -> `fail`
- review report status rejected -> `rejected` and `review_gate_passed=false`
- review report status stale -> `stale` and `review_gate_passed=false`
- review report status fail -> `fail` and `review_gate_passed=false`
- review report status blocked -> `blocked` and `review_gate_passed=false`
- unsupported review report status -> `blocked` and `review_gate_passed=false`
- expected source hash differs -> `stale`
- parent Initiative/Epic differs -> `stale`
- observed versus expected review digest differs -> `stale`
- unsafe report path -> `rejected`, no file written

Closure: CL-012, CL-013.

### S05 — Presentation renderer

Goal:

- JSON/text output を stable にし、validation pass と authority decision を明確に分離する。

Tasks:

1. `candidate_validation_renderer.py` を追加する。
2. JSON renderer は stable/sorted にする。
3. Text renderer は evidence-only / no-mutation flags を必ず出す。
4. Text output が readiness / PR / adoption 成功表現に見えないことを tests で固定する。

Tests:

- text output preserves authority boundary
- JSON output contains no-mutation flags

Closure: CL-014.

### S06 — CLI wiring and compatibility wrappers

Goal:

- CLI command と compatibility scripts を runtime contract に接続する。

Tasks:

1. `commands/authoring.py` に args dataclass、argument builder、run function、CommandSpec を追加する。
2. `cli/parser.py` help を更新する。
3. `validate_issue_candidates.py` を runtime use case wrapper にする。
4. `validate_initiative_epic_candidates.py` を追加する。
5. Provider-side scripts を dogfood mirror に反映する。

Tests:

- compatibility wrapper smoke
- dogfood runtime path smoke
- hardcoded personal path absence inspection

Closure: CL-001, CL-002, CL-015.

### S07 — Full verification and report closeout

Goal:

- Candidate validator implementation を Issue completion-ready にする。

Commands:

```bash
uv run pytest tests/cli_runtime/test_authoring.py -q -k "validate_initiative_epic or validate_epic_issue or candidate or deferred_commands or dogfood"
uv run pytest tests/cli_runtime/test_authoring.py -q
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock assurance verify
git diff --check
```

Report evidence:

- scope summary
- files changed
- tests run
- protected canonical docs unchanged
- no secret/raw transcript payload evidence
- reviewer results
- no-per-Issue-PR rationale
- `iss-00307` defer

Closure: CL-016, CL-017.

## 5. Concrete Test Cases

| Test | Input | Expected |
| --- | --- | --- |
| Initiative/Epic valid | 2 valid Epic candidates | `pass`, 2 candidates, no mutation flags false |
| Epic/Issue valid | 3 valid Issue candidates | `pass`, dependencies indexed, profile advisory-only |
| missing review report | stage without report | `blocked` |
| review rejected | review report status rejected | `rejected`, no candidate validation, `review_gate_passed=false` |
| review failed | review report status fail | `fail`, no candidate validation, `review_gate_passed=false` |
| review blocked | review report status blocked | `blocked`, no candidate validation, `review_gate_passed=false` |
| unsupported review status | review report status needs-human | `blocked`, no candidate validation, `review_gate_passed=false`, unsupported status finding |
| malformed index | `{bad json` | `fail` |
| non-object index | `[]` | `fail` |
| duplicate id | same `candidate_id` twice | `fail` |
| duplicate title | same title twice | `fail` |
| duplicate slug | same slug twice | `fail` |
| overlapping boundary | scope/non_scope overlap | `fail` |
| parent mismatch | expected parent differs | `stale` |
| source hash mismatch | expected hash differs | `stale` |
| review digest mismatch | observed staged pack digest differs from review report digest | `stale` |
| path traversal | `../requirement.md` | `rejected` |
| host local path | `/Users/example/file.md` | `rejected` |
| hidden path | `.env` or `.hidden.md` | `rejected` |
| unsupported suffix | `notes.txt` draft file | `rejected` |
| symlink draft | candidate draft path is symlink | `rejected` |
| executable draft | executable Markdown draft file | `rejected` |
| binary draft | binary draft payload | `rejected` |
| oversized draft | draft exceeds size limit | `rejected` |
| secret text | `token=abc123` | `rejected`, raw token absent |
| raw transcript | `raw transcript` marker | `rejected` |
| forbidden claim | `PR-ready` | `rejected` |
| authorized profile | non-null `authorized_profile` | `rejected` |
| unsupported grade | `grade_recommendation.grade=advanced` | `fail`, allowed values listed |
| unsupported profile | `profile_recommendation.profile=advanced` | `fail`, allowed values listed |
| unsafe report path | canonical active issue artifact path | `rejected`, no file written |
| dogfood smoke | `spec-dock/scripts/spec-dock ... validate ...` | same JSON contract as provider |

## 6. Delegation / Reviewer Obligations

- Runtime command, domain/application/presentation, tests, and dogfood mirror changes are implementation work.
- Parent orchestrator remains responsible for report evidence and canonical doc adoption.
- `spec-reviewer` must verify requirement/design/plan/report alignment and no authority confusion.
- `code-reviewer` must verify path/report safety, scanner reuse, deterministic ordering, and provider/dogfood parity.
- `qa-reviewer` must verify positive/negative fixtures, stale/rejected/blocked semantics, redaction, and no-mutation evidence.

## 7. Final Gates

Required before `issue finish`:

- Focused candidate validation tests pass.
- Existing authoring review/stage tests remain green or failures are explained.
- `./spec-dock/scripts/spec-dock validate` passes.
- `./spec-dock/scripts/spec-dock assurance verify` passes.
- `git diff --check` passes.
- Provider-side and dogfood mirror paths are in sync.
- No changed output claims reviewer pass, execution-ready, PR-ready, mergeable PR, canonical adoption, or `.assurance.json` mutation as achieved.
- No raw secret or transcript body is introduced into durable fixtures/reports.
- `report.md` records no-per-Issue-PR relay and `iss-00307` handoff.

## 8. No-per-Issue-PR Relay

This is an intermediate Epic `epic-00295` Issue. It must not create a PR.

Finish handoff must state:

- local verification completed
- no per-Issue PR created
- final quality gate / PR delivery deferred to `iss-00307`
- next Issue starts after this Issue is finished
