---
種別: 実装計画書（Issue）
ID: "iss-00299"
タイトル: "Prompt Pack Constraints"
関連GitHub: ["#299"]
状態: "planning-ready"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
依存: ["requirement.md", "design.md"]
親: ["epic-00295", "init-local-00003"]
Issue Grade: "standard"
---

# iss-00299 Prompt Pack Constraints — 実装計画

## 0. 結論

Issue Grade の workflow authority は `assurance classify --stage requirement` により `standard` とする。ChatGPT Use は `strict` を推奨したが、これは safe output constraints、privacy / authority boundary、provider/mirror asset consistency に関する reviewer focus として扱い、`authorized_profile=standard` の義務を下げる根拠にはしない。

この Issue は中間 Issue であり、PR delivery は行わない。finish evidence には no-per-Issue-PR rationale、local verification、final quality Issue `iss-00307` への dependency edge を記録する。

## 1. Scope / Non-scope

### Scope

- `authoring pack prepare` command を deferred から implemented behavior へ変更する。
- preflight/source evidence を読み、deterministic prompt pack tree を生成する。
- `manifest.json`、`provenance.json`、`source-manifest.json`、`stale-if.json`、`safe-output-constraints.md`、`chatgpt-use-prompt.md` を生成する。
- `github-synced` / `local-context` provenance を保持する。
- forbidden authority claims と expected ZIP/tree contract を prompt guidance に含める。
- provider-side assets と dogfood mirror を更新する。
- deterministic / negative / local-context / forbidden claim / cache exclusion tests を追加する。
- report evidence と EAL proposal を更新対象として準備する。

### Non-scope

- backend invocation。
- ZIP review。
- ZIP extraction。
- stage / dry-run diff。
- candidate validators。
- issue draft adoption validators。
- approval check。
- automatic canonical adoption。
- Issue creation。
- `.assurance.json` mutation。
- `authorized_profile` 決定。
- reviewer pass / execution-ready / PR-ready marking。
- PR delivery。
- broad `--force` bypass。

## 2. Dependencies

| dependency | required before | reason |
|---|---|---|
| iss-00298 preflight implementation | S01 | preflight result schema / source manifest / evidence mode を入力契約として使う |
| provider-side runtime command skeleton | S02 | `authoring pack prepare` dispatch を差し替える |
| source manifest cache exclusion | S03 | prompt pack source evidence に generated cache を入れない |
| Epic relay policy | S90/S99 | PR delivery defer evidence を finish に残す |

## 3. 実装ステップ（Implementation steps）

### S01: 既存 contract と preflight evidence schema を固定する

作業:

- `authoring preflight github-sync` の output schema を確認する。
- `github-synced` / `local-context` の required fields を確認する。
- current deferred behavior を確認し、`authoring pack prepare` だけを implementation target にする。
- 他 deferred commands は維持する。

依存:

- なし。ただし iss-00298 成果の確認が必要。

成果:

- prompt pack prepare input contract memo。
- required / optional field list。
- non-scope guardrail list。

### S02: CLI dispatch を実装対象へ切り替える

作業:

- `commands/authoring.py` の `authoring_pack_prepare` spec を deferred runner から pack prepare runner へ変更する。
- CLI args を追加する。
  - `--preflight`
  - `--output-dir`
  - `--format text|json`
  - optional `--mode`
  - optional `--source-manifest`
  - optional `--stale-if`
- `--force` は追加しない。
- unsupported commands の deferred behavior は維持する。

依存:

- S01。

成果:

- CLI help。
- dispatch path。
- stable exit code mapping。

### S03: domain contract を実装する

作業:

- `PromptPackPrepareRequest` / `PromptPackPrepareResult` を定義する。
- `AuthorityBoundary` を固定する。
- `SafeOutputConstraints` を定義する。
- expected ZIP root / required metadata / forbidden payload categories を定義する。
- forbidden achieved authority claim の guard を入れる。
- source manifest cache exclusion を reuse / verify する。

依存:

- S01。

成果:

- domain contract。
- schema validation。
- safety guard。

### S04: application use case を実装する

作業:

- preflight JSON を load する。
- required field を validate する。
- preflight status を pack prepare status に mapping する。
- `github-synced` / `local-context` provenance を normalize する。
- stale / blocked / fail / rejected は fail-closed にする。
- valid input のみ prompt pack payload を生成する。

依存:

- S03。

成果:

- `pack_prepare.py`。
- status mapping。
- provenance model。

### S05: renderer / file writer を実装する

作業:

- deterministic JSON writer を実装する。
- fixed file ordering で prompt pack tree を生成する。
- `manifest.json` を生成する。
- `provenance.json` を生成する。
- `source-manifest.json` を生成する。
- `stale-if.json` を生成する。
- `safe-output-constraints.md` を生成する。
- `chatgpt-use-prompt.md` を生成する。
- unsafe output directory を reject する。

依存:

- S04。

成果:

- output tree。
- text/json diagnostics。
- no canonical write guard。

### S06: fixtures と tests を追加する

作業:

- valid `github-synced` fixture。
- valid `local-context` fixture。
- stale preflight fixture。
- blocked preflight fixture。
- missing required metadata fixture。
- forbidden authority claim fixture。
- cache exclusion fixture。
- deterministic double-run test。
- CLI help / no `--force` test。
- dogfood mirror smoke test。

依存:

- S02〜S05。

成果:

- pytest coverage。
- positive / negative evidence。

### S90: report evidence / EAL proposal を更新する

作業:

- report additions を作成する。
- Evidence Adoption Ledger proposal を記録する。
- deferred PR delivery evidence を記録する。
- residual risks と reviewer focus を記録する。

依存:

- S06。

成果:

- `report.md` 追記案。
- Closure Evidence Ledger。
- PR delivery defer note to `iss-00307`。

### S99: final issue-local verification を実行する

作業:

- exact verification commands を実行する。
- reviewer handoff package を作る。
- P0/P1 blocker が残る場合は status と next action を記録する。
- PR は作らず `iss-00307` へ delivery defer を記録する。

依存:

- S90。

成果:

- command output summary。
- reviewer handoff。
- finish evidence。

## 4. Spec-Locked Closure Index

| closure id | step | purpose | maps to AC | required evidence | close condition | report destination |
|---|---|---|---|---|---|---|
| tc-001 | S01 | preflight / evidence mode input contract を固定する | AC-002, AC-007, AC-008 | schema memo、fixture source | required fields と non-scope が説明できる | Closure Evidence Ledger |
| tc-002 | S02 | `authoring pack prepare` を deferred から実装 command に切り替える | AC-001, AC-010 | CLI help、deferred command comparison | pack prepare が deferred を返さず、他 commands は deferred 維持 | Closure Evidence Ledger |
| tc-003 | S03 | authority / safe output constraints を domain contract 化する | AC-004, AC-005, AC-006 | domain tests、snapshot | evidence-only fields と forbidden claims が固定される | EAL / Closure Evidence Ledger |
| tc-004 | S04 | status mapping と provenance normalize を実装する | AC-002, AC-007, AC-008 | application tests | valid は pass、stale/blocked は non-zero | Closure Evidence Ledger |
| tc-005 | S05 | deterministic prompt pack tree を生成する | AC-002, AC-003, AC-004, AC-006 | generated tree、digest comparison | same input の normalized digest が一致 | Closure Evidence Ledger |
| tc-006 | S06 | positive / negative fixtures を揃える | AC-003〜AC-010 | pytest output | valid/local-context/negative/cache tests が pass | Test Evidence |
| tc-007 | S06 | source cache exclusion を検証する | AC-009 | source manifest assertion | `__pycache__` / `.pyc` / `.pyo` が含まれない | Test Evidence |
| tc-008 | S90 | report / EAL / PR defer evidence を整える | AC-012 | report diff | no-per-Issue-PR と iss-00307 defer が明記される | Report |
| tc-009 | S99 | exact verification commands を完了する | all AC | command output | P0/P1 blocker がない、または明確に記録 | Final Gate |
| tc-010 | S99 | reviewer handoff を作る | all AC / reviewer focus | reviewer checklist | dev/code/qa/spec reviewer boundaries が明確 | Reviewer Gate Status |

## 5. 具体テストケース（Step-local concrete test-case cards）

### TC-S01-001: preflight schema inventory

- Step: S01
- Given: iss-00298 preflight output fixture。
- When: required field inventory を作る。
- Then: `status`、`evidence_mode`、`sync_state`、`github_sync`、`source_manifest_hash`、`authority` が識別される。
- Evidence: schema memo。
- Failure: schema が不足する場合は implementation 前に blocker とする。

### TC-S02-001: CLI help exposes implemented prepare command

- Step: S02
- Given: installed runtime。
- When:
  - `./spec-dock/scripts/spec-dock authoring pack prepare --help`
- Then:
  - `--preflight`、`--output-dir`、`--format` が表示される。
  - `--force` は表示されない。
- Evidence: pytest capture。

### TC-S02-002: other authoring commands stay deferred

- Step: S02
- Given: installed runtime。
- When:
  - `authoring backend invoke`
  - `authoring pack review`
  - `authoring pack stage`
- Then:
  - deferred/fail-closed diagnostics を維持する。
- Evidence: CLI runtime test。

### TC-S03-001: authority boundary cannot be changed

- Step: S03
- Given: generated metadata。
- When: metadata を inspect する。
- Then:
  - `authority=evidence_only`
  - `adoption_status=unreviewed`
  - `bundle_generation_not_promotion=true`
- Evidence: domain test。

### TC-S03-002: forbidden achieved claim is rejected

- Step: S03
- Given: input config or prompt metadata containing achieved reviewer/pass/readiness claim。
- When: domain validator を実行する。
- Then: status `rejected`。
- Evidence: negative fixture.

### TC-S04-001: github-synced pass maps to prompt pack pass

- Step: S04
- Given: valid preflight `status=pass`, `evidence_mode=github-synced`。
- When: use case を実行する。
- Then: pack prepare result `status=pass`。
- Evidence: application test。

### TC-S04-002: local-context pass preserves lower authority

- Step: S04
- Given: valid local-context preflight。
- When: use case を実行する。
- Then:
  - `github_sync=not_verified`
  - `sync_state=local_context`
  - `adoption_requires=explicit_eal_disposition`
- Evidence: application test。

### TC-S04-003: stale preflight stays stale

- Step: S04
- Given: preflight `status=stale`。
- When: use case を実行する。
- Then:
  - result `status=stale`
  - no invocation-ready prompt claim。
- Evidence: negative fixture。

### TC-S05-001: deterministic double run

- Step: S05
- Given: valid fixture。
- When: same input で 2 回 pack を生成する。
- Then: normalized output digest が一致する。
- Evidence: pytest digest assertion。

### TC-S05-002: output tree contains required files

- Step: S05
- Given: valid fixture。
- When: pack を生成する。
- Then:
  - `.specdock-authoring-pack`
  - `manifest.json`
  - `provenance.json`
  - `source-manifest.json`
  - `stale-if.json`
  - `safe-output-constraints.md`
  - `chatgpt-use-prompt.md`
- Evidence: filesystem assertion。

### TC-S05-003: canonical output target is rejected

- Step: S05
- Given: output-dir points into canonical Issue docs。
- When: pack prepare を実行する。
- Then: status `rejected`。
- Evidence: negative fixture.

### TC-S06-001: source manifest excludes cache files

- Step: S06
- Given: fixture containing `__pycache__/module.pyc` and source file。
- When: pack prepare を実行する。
- Then: manifest excludes cache files。
- Evidence: JSON assertion。

### TC-S06-002: prompt guidance contains ZIP contract

- Step: S06
- Given: valid generated prompt。
- When: `chatgpt-use-prompt.md` を inspect する。
- Then:
  - expected root `specdock-authoring-pack/`
  - required metadata
  - unsafe categories
  - no adoption/readiness claim
- Evidence: text fixture assertion。

### TC-S90-001: report records PR defer to iss-00307

- Step: S90
- Given: Issue finish evidence。
- When: report additions を作る。
- Then:
  - no per-Issue PR rationale。
  - dependency edge to `iss-00307`。
- Evidence: report diff.

### TC-S99-001: final verification command bundle

- Step: S99
- Given: completed implementation。
- When: exact commands を実行する。
- Then: P0/P1 blocker がない、または blocker が report に記録される。
- Evidence: command output summary。

## 6. Delegation boundaries

### Step-local delegation contracts

#### S01: existing contract and preflight evidence schema

| Field | Contract |
|---|---|
| delegated role | parent-orchestrator direct inspection |
| input docs | `requirement.md`, `design.md`, `plan.md`, `src/.../github_sync_preflight.py`, `src/.../preflight_contract.py`, `src/.../source_manifest.py`, `tests/cli_runtime/test_authoring.py` |
| allowed paths | read-only inspection; report evidence rows may be updated in S90 only |
| forbidden changes | production code edits, test edits, backend invocation, ZIP review/stage, adoption automation |
| acceptance criteria | preflight result fields, evidence modes, deferred command boundary, and non-scope guardrails are recorded before implementation starts |
| required verification | direct inspection summary; no runtime tests required for S01 |
| reviewer focus | spec-reviewer confirms S01 does not expand implementation scope |
| stop conditions | iss-00298 contract is unavailable, contradictory, or insufficient to define prompt pack input |
| output required | schema inventory summary and implementation boundary for S02-S06 |

#### S02: CLI dispatch for `authoring pack prepare`

| Field | Contract |
|---|---|
| delegated role | dev-coder |
| input docs | `requirement.md` AC-001/AC-010, `design.md` §1/§8/§11, this plan tc-002 and TC-S02-* |
| allowed paths | provider and dogfood mirror `commands/authoring.py`; focused CLI tests |
| forbidden changes | backend invocation, ZIP review/stage, validators, canonical adoption automation, `.assurance.json` writes, PR creation, broad bypass flags |
| acceptance criteria | `authoring pack prepare --help` exposes implemented options and no `--force`; other authoring commands remain deferred/fail-closed |
| required verification | CLI help test, deferred command regression test, focused pytest |
| reviewer focus | code-reviewer verifies only `pack prepare` leaves deferred state |
| stop conditions | parser shape requires changing unrelated command groups or adding bypass flags |
| output required | changed files, CLI help behavior, deferred command evidence, unresolved risks |

#### S03: domain contract and safe output constraints

| Field | Contract |
|---|---|
| delegated role | dev-coder |
| input docs | `requirement.md` AC-004/AC-005/AC-006/AC-009, `design.md` §3/§4/§5/§6/§7/§12, this plan tc-003 and TC-S03-* |
| allowed paths | provider and mirror `domain/authoring_pack/*`; focused tests / fixtures |
| forbidden changes | backend command resolution, ZIP extraction/review, stage/dry-run diff, validators, automatic adoption |
| acceptance criteria | domain model fixes evidence-only metadata, forbidden claim prohibition list, expected ZIP/tree contract, and cache exclusion semantics |
| required verification | domain/application pytest for authority fields, forbidden achieved claim handling, source manifest cache exclusion |
| reviewer focus | code-reviewer checks deterministic serialization and no achieved authority claim |
| stop conditions | domain contract requires data owned by later backend/ZIP stages |
| output required | contract summary, schema fields, tests run, follow-up if later issue dependency is discovered |

#### S04: application use case and status mapping

| Field | Contract |
|---|---|
| delegated role | dev-coder |
| input docs | `requirement.md` AC-002/AC-007/AC-008, `design.md` §2/§10/§12, this plan tc-004 and TC-S04-* |
| allowed paths | provider and mirror `application/authoring_pack/pack_prepare.py`; command integration as needed; focused tests |
| forbidden changes | actual ChatGPT/backend invocation, ZIP review/stage, canonical docs write, `.assurance.json` write |
| acceptance criteria | valid github-synced/local-context inputs map to pass with correct provenance; stale/blocked/invalid inputs fail closed with non-zero status |
| required verification | application/CLI tests for github-synced pass, local-context lower authority, stale/blocked negative cases |
| reviewer focus | qa-reviewer checks exit codes, status taxonomy, provenance preservation |
| stop conditions | preflight schema ambiguity prevents deterministic status mapping |
| output required | status mapping table, test results, unresolved input-schema risks |

#### S05: renderer and file writer

| Field | Contract |
|---|---|
| delegated role | dev-coder |
| input docs | `requirement.md` AC-002/AC-003/AC-004/AC-006/AC-012, `design.md` §6/§7/§9/§12, this plan tc-005 and TC-S05-* |
| allowed paths | provider and mirror `presentation/authoring_pack/*`, domain/application support files, focused tests / fixtures |
| forbidden changes | writing canonical Issue docs, writing `.assurance.json`, writing outside explicit output directory, ZIP extraction/review/stage |
| acceptance criteria | prompt pack tree contains required files, deterministic normalized digest is stable, unsafe canonical output targets are rejected |
| required verification | filesystem fixture tests, digest comparison, unsafe output path negative test, dogfood mirror smoke |
| reviewer focus | code-reviewer checks path safety; qa-reviewer checks determinism and file inventory |
| stop conditions | deterministic output requires timestamps or host-local paths that cannot be normalized |
| output required | generated file inventory, digest evidence, unsafe-path test evidence |

#### S06: fixtures and test coverage

| Field | Contract |
|---|---|
| delegated role | dev-coder |
| input docs | all AC/EC, this plan tc-006/tc-007 and TC-S06-* |
| allowed paths | `tests/cli_runtime/*`, fixture directories, provider/mirror runtime files needed to satisfy tests |
| forbidden changes | broadening runtime scope beyond `pack prepare`, weakening deferred command assertions |
| acceptance criteria | positive/negative fixtures cover github-synced, local-context, stale, blocked, missing metadata, forbidden claims, cache exclusion, no `--force`, and dogfood mirror |
| required verification | focused pytest command from §7 and `git diff --check` |
| reviewer focus | qa-reviewer checks negative tests fail closed and positive tests do not overclaim authority |
| stop conditions | fixture setup needs live network or credentials |
| output required | test list, commands, observed pass/fail, any uncovered AC |

#### S90: report evidence and relay policy

| Field | Contract |
|---|---|
| delegated role | parent-orchestrator |
| input docs | completed S01-S06 evidence, reviewer outputs, `plan.md` §8 |
| allowed paths | `report.md` only unless reviewer finding requires planned implementation fix |
| forbidden changes | new runtime behavior, PR creation, issue finish self-claim before gates |
| acceptance criteria | EAL, closure coverage, verification output, reviewer status, no-per-Issue-PR rationale, and `iss-00307` defer are recorded |
| required verification | report inspection and `./spec-dock/scripts/spec-dock guidance issue-execution` |
| reviewer focus | spec-reviewer verifies report evidence is current and not self-promoted |
| stop conditions | any closure id remains unproven or reviewer gate missing |
| output required | final report evidence rows and blocker/follow-up summary |

#### S99: final local gate

| Field | Contract |
|---|---|
| delegated role | parent-orchestrator with code-reviewer / qa-reviewer / spec-reviewer gates |
| input docs | all implementation evidence, `report.md`, §7 exact verification commands |
| allowed paths | reviewer-finding fixes within S02-S06 allowed paths, `report.md`, commit metadata |
| forbidden changes | new feature scope, PR creation, final quality gate work owned by `iss-00307` |
| acceptance criteria | required verification passes, fresh reviewers pass, commit created, post-commit clean check passes, issue finish allowed |
| required verification | §7 command bundle, reviewer gates, post-commit `git status --short` |
| reviewer focus | all reviewers check final integrated diff and evidence ledger |
| stop conditions | P0/P1 reviewer finding, failed verification, stale assurance, dirty unrelated worktree |
| output required | commit hash, verification summary, issue finish evidence, next issue readiness |

### dev-coder

May do:

- provider-side runtime implementation。
- dogfood mirror update。
- tests / fixtures。
- docs/report evidence draft。

Must not do:

- backend invocation implementation。
- ZIP review/stage implementation。
- validators。
- canonical adoption automation。
- `.assurance.json` mutation。
- PR creation。
- broad bypass flag introduction。

### code-reviewer

Focus:

- command dispatch が `pack prepare` のみ implemented になっているか。
- other commands remain deferred/fail-closed。
- domain/application/presentation layering が守られているか。
- deterministic writer。
- unsafe output path guard。
- provider/mirror consistency。
- no achieved authority claim。

### qa-reviewer

Focus:

- positive / negative fixture coverage。
- local-context provenance。
- stale / blocked / rejected status mapping。
- cache exclusion。
- CLI help / no `--force`。
- dogfood mirror smoke。
- exact command reproducibility。

### spec-reviewer

Focus:

- scope/non-scope。
- Epic trace。
- prompt pack contract。
- authority boundary。
- evidence-only output。
- PR delivery defer to `iss-00307`。
- future issue boundaries for iss-00300 / iss-00301 / validators。

## 7. Exact verification commands

Minimum commands:

```bash
git diff --check
```

```bash
./spec-dock/scripts/spec-dock validate
```

```bash
uv run pytest tests/cli_runtime/test_authoring.py
```

If implementation adds narrower tests, run them explicitly:

```bash
uv run pytest tests/cli_runtime/test_authoring_pack_prepare.py
```

or, if consolidated into existing file:

```bash
uv run pytest tests/cli_runtime/test_authoring.py -k "pack_prepare or source_manifest or local_context or forbidden"
```

Dogfood mirror smoke:

```bash
./spec-dock/scripts/spec-dock authoring pack prepare --help
```

Valid fixture smoke:

```bash
./spec-dock/scripts/spec-dock authoring pack prepare \
  --preflight tests/fixtures/authoring_pack/prepare/valid-github-synced-preflight.json \
  --output-dir "${TMPDIR:-/tmp}/specdock-iss-00299-pack" \
  --format json
```

Local-context fixture smoke:

```bash
./spec-dock/scripts/spec-dock authoring pack prepare \
  --preflight tests/fixtures/authoring_pack/prepare/valid-local-context-preflight.json \
  --output-dir "${TMPDIR:-/tmp}/specdock-iss-00299-local-context-pack" \
  --format json
```

Negative fixture smoke:

```bash
./spec-dock/scripts/spec-dock authoring pack prepare \
  --preflight tests/fixtures/authoring_pack/prepare/stale-preflight.json \
  --output-dir "${TMPDIR:-/tmp}/specdock-iss-00299-stale-pack" \
  --format json
```

Expected negative result: non-zero exit and `status=stale`.

Forbidden claim smoke:

```bash
./spec-dock/scripts/spec-dock authoring pack prepare \
  --preflight tests/fixtures/authoring_pack/prepare/forbidden-authority-claim.json \
  --output-dir "${TMPDIR:-/tmp}/specdock-iss-00299-forbidden-pack" \
  --format json
```

Expected negative result: non-zero exit and `status=rejected`.

## 8. PR delivery defer evidence

This Issue is intermediate in epic-00295 relay execution.

Finish evidence must include:

```md
### PR Delivery Defer Evidence

- Issue: `iss-00299`
- Reason: 中間 Issue のため、Epic-wide PR delivery は final quality Issue `iss-00307` に集約する。
- Local verification completed:
  - `git diff --check`
  - `./spec-dock/scripts/spec-dock validate`
  - relevant pytest commands
- No per-Issue PR created: yes
- Deferred to: `iss-00307`
- Dependency edge: `iss-00299` completion evidence is input to `iss-00307`
```

## 9. Completion conditions

Issue can be finished only when:

* all AC have pass/blocker evidence;
* `authoring pack prepare` no longer returns iss-00299 deferred status for valid usage;
* other commands remain deferred;
* prompt pack output is evidence-only;
* forbidden authority claims are only listed as prohibited, not achieved;
* no `.assurance.json` mutation;
* no canonical adoption;
* no PR delivery;
* report contains EAL proposal and PR defer evidence;
* reviewer handoff package is ready for fresh review.
