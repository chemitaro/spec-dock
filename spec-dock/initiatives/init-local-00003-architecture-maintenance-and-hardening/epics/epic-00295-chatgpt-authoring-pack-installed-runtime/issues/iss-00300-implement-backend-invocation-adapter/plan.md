---
種別: 実装計画書（Issue）
ID: "iss-00300"
タイトル: "Backend Invocation Adapter"
関連GitHub: ["#300"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
依存: ["requirement.md", "design.md"]
親: ["epic-00295", "init-local-00003"]
Issue Grade: "standard"
---

# iss-00300 Backend Invocation Adapter — Issue 実装計画書

## 1. Plan Readiness

必須入力:

- `requirement.md`: `authoring backend invoke` の scope / non-scope / AC-001..AC-017 を定義済み。
- `design.md`: backend command resolver、prompt pack validation、dry-run、subprocess adapter、redaction、presentation、compatibility script 境界を定義済み。
- `report.md`: planning evidence / implementation evidence / reviewer gate / PR defer evidence の記録先。
- Issue-local draft artifacts: requirement/design/plan seeds。
- ChatGPT Use planning evidence summary: `artifacts/20260708-chatgpt-use-planning-evidence-summary.md`。

実装開始前 gate:

- `spec-reviewer` が `requirement.md` / `design.md` / `plan.md` / `report.md` に対して fresh `pass` を返す。
- `./spec-dock/scripts/spec-dock assurance verify` が pass する。
- `./spec-dock/scripts/spec-dock guidance issue-execution` が `may_execute_approved_plan: true` を返す。

## 2. Change Surface

許可変更面:

| 種別 | パス | 許可する変更 |
| --- | --- | --- |
| runtime command | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/authoring.py` | `authoring backend invoke` registration / dispatch |
| application | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/backend_invoke.py` | backend invocation service |
| domain | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/*` | command resolution / invocation contract / redaction helpers |
| presentation | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/authoring_pack/*` | text/json rendering for backend invoke |
| compatibility script | `src/spec_dock/assets/spec_dock/scripts/authoring-pack/invoke_chatgpt_backend.py` | delegate to runtime contract or maintain parity |
| dogfood mirror | `spec-dock/scripts/spec_dock_runtime/**`, `spec-dock/scripts/authoring-pack/**` | provider-side changes copied for dogfood verification |
| tests | `tests/cli_runtime/test_authoring.py`, related fixtures under `tests/fixtures/authoring_pack/**` | focused regression coverage |
| issue docs | active issue `report.md` | observed evidence only |

禁止変更:

- ZIP review / stage / extraction implementation。
- candidate validation / draft adoption validation / approval stop gate implementation。
- `.assurance.json` を manual edit で reviewer pass / execution-ready に見せる変更。
- hardcoded personal backend path。
- PR creation / PR readiness claim。
- broad `--force` bypass。

## 3. Spec-Locked Closure Index

| Closure ID | Requirement | Design | 閉じる内容 | Verification |
| --- | --- | --- | --- | --- |
| CL-001 | AC-001 | DES-CLI-001 | help exposes implemented backend command and no `--force` | `test_authoring_backend_invoke_help_exposes_contract_without_force` |
| CL-002 | AC-002 | DES-DOM-001 | unset backend blocks without process execution | `test_authoring_backend_invoke_unset_backend_blocks` |
| CL-003 | AC-003 | DES-DOM-001 | CLI backend command overrides env vars | `test_authoring_backend_invoke_cli_backend_command_overrides_env` |
| CL-004 | AC-004 | DES-DOM-001 | `SPECDOCK_CHATGPT_COMMAND` precedes fallback | `test_authoring_backend_invoke_primary_env_takes_precedence_over_fallback` |
| CL-005 | AC-005 | DES-DOM-001 | `ORACLE_CHATGPT_COMMAND` fallback works only when primary is empty | `test_authoring_backend_invoke_oracle_fallback_when_primary_empty` |
| CL-006 | AC-006 / AC-010 | DES-DOM-002 | malformed command blocks and backend argv is list without shell and with fixed ABI suffix | `test_authoring_backend_invoke_malformed_command_blocks_without_shell`; `test_authoring_backend_invoke_passes_argv_without_shell`; `test_authoring_backend_invoke_appends_fixed_backend_argv_abi` |
| CL-007 | AC-007 | DES-APP-001 | dry-run does not invoke backend | `test_authoring_backend_invoke_dry_run_does_not_execute_backend` |
| CL-008 | AC-008 | DES-APP-002 | missing / malformed prompt pack fail-closed | `test_authoring_backend_invoke_missing_prompt_pack_blocks`; `test_authoring_backend_invoke_missing_metadata_fails` |
| CL-009 | AC-009 | DES-APP-003 | unsafe output target rejected | `test_authoring_backend_invoke_rejects_canonical_output_target`; `test_authoring_backend_invoke_rejects_symlinked_summary` |
| CL-010 | AC-011 | DES-APP-004 | backend non-zero blocks without adoption claim | `test_authoring_backend_invoke_backend_non_zero_blocks_without_adoption_claim` |
| CL-011 | AC-012 | DES-APP-004 | timeout maps to blocked diagnostics | `test_authoring_backend_invoke_timeout_blocks` |
| CL-012 | AC-013 | DES-PRES-001 | secret-like data and host-local paths are redacted | `test_authoring_backend_invoke_redacts_secret_like_output_and_host_paths` |
| CL-013 | AC-014 | DES-DOM-003 | local-context summary preserves lower authority | `test_authoring_backend_invoke_local_context_summary_requires_eal_disposition` |
| CL-014 | AC-015 | DES-COMPAT-001 | provider and dogfood runtime smoke pass | `./spec-dock/scripts/spec-dock authoring backend invoke --help`; focused pytest |
| CL-015 | AC-016 | DES-COMPAT-001 | compatibility script contract retained or delegated | focused script test / inspection |
| CL-016 | AC-017 | DES-WF-001 | no PR delivery; `iss-00307` defer evidence recorded | `report.md` evidence |

## 4. 実装ステップ（Implementation Steps）

### S01 — Domain contract and fixtures

成果:

- backend invocation result/status contract を定義する。
- minimal valid / invalid prompt pack fixture を用意または既存 fixture を再利用する。

主な closure:

- CL-002, CL-008, CL-010, CL-011

検証:

- focused unit/CLI tests added as Red first where feasible。

### S02 — Backend command resolution

成果:

- CLI/env/fallback priority を実装する。
- empty env を unset として扱う。

主な closure:

- CL-002, CL-003, CL-004, CL-005

検証:

- resolver / CLI JSON tests。

### S03 — Prompt pack and output safety validation

成果:

- prompt pack root / manifest / required metadata を検証する。
- canonical output target と symlinked target を拒否する。

主な closure:

- CL-008, CL-009

検証:

- missing pack / missing metadata / unsafe target tests。

### S04 — Argv build and dry-run

成果:

- `shlex.split` による argv build。
- backend argv ABI suffix を固定する。具体的には resolved backend argv に `--slug <slug>`, `-p <prompt>`, repeated `--file <prompt-pack>/<file>` を追加し、prompt pack の `chatgpt-use-prompt.md`, `expected-output-contract.md`, `manifest.json`, `provenance.json`, `source-manifest.json`, `stale-if.json`, `safe-output-constraints.md` を渡す。
- `--output-dir` は backend argv に渡さず、SpecDock adapter の invocation summary / diagnostics 出力先として扱う。
- dry-run non-execution summary。
- shell metacharacter が prompt / args に含まれても shell 実行しないことを確認する。

主な closure:

- CL-006, CL-007

検証:

- sentinel backend / captured argv tests。

### S05 — Subprocess adapter and status mapping

成果:

- backend process execution。
- non-zero / timeout / OSError を deterministic diagnostics に map する。

主な closure:

- CL-010, CL-011

検証:

- fake backend scripts / timeout tests。

### S06 — Redaction and presentation

成果:

- text/json renderer を追加または拡張する。
- stdout/stderr summary redaction。
- invocation-local pass と authority boundary の明示。

主な closure:

- CL-012, CL-013

検証:

- redaction / local-context tests。

### S07 — CLI integration and compatibility script

成果:

- parser / command handler から service を呼ぶ。
- provider-side compatibility script を runtime service へ委譲、または parity を維持する。
- dogfood mirror を同期する。

主な closure:

- CL-001, CL-014, CL-015

検証:

- `uv run pytest tests/cli_runtime/test_authoring.py -q`
- `./spec-dock/scripts/spec-dock authoring backend invoke --help`

### S90 — Report and workflow evidence

成果:

- `report.md` に planning adoption、implementation evidence、reviewer gates、PR defer evidence を記録する。

主な closure:

- CL-016

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
| B-001 | S01/S02 | backend command 未設定時に process を起動せず blocked を返す | CL-002 |
| B-002 | S02 | CLI/env/fallback priority が deterministic に解決される | CL-003..CL-005 |
| B-003 | S03 | prompt pack / output target が安全でない場合に fail-closed する | CL-008..CL-009 |
| B-004 | S04 | argv build が shell injection を避け、dry-run は process を起動しない | CL-006..CL-007 |
| B-005 | S05 | backend non-zero / timeout を blocked diagnostics に map する | CL-010..CL-011 |
| B-006 | S06 | stdout/stderr summary を redact し、local-context lower authority を保持する | CL-012..CL-013 |
| B-007 | S07 | installed runtime command と compatibility script contract が使える | CL-001, CL-014, CL-015 |
| B-008 | S90/S99 | no-per-Issue-PR relay evidence を残す | CL-016 |

## 6. 具体テストケース（Concrete Test Cases）

| Test ID | 目的 | 期待 |
| --- | --- | --- |
| TC-001 | help contract | `backend invoke` options が表示され、`--force` が表示されない |
| TC-002 | unset backend | status `blocked`; sentinel file not created |
| TC-003 | CLI override | backend source `cli` |
| TC-004 | primary env priority | backend source `env:SPECDOCK_CHATGPT_COMMAND` |
| TC-005 | fallback env | backend source `env:ORACLE_CHATGPT_COMMAND`, compatibility fallback true |
| TC-006 | malformed command | parse failure; shell executionなし |
| TC-007 | argv without shell | captured argv に shell metacharacter が literal として残る |
| TC-008 | backend argv ABI | captured argv が `--slug`, `-p`, repeated `--file` の固定 suffix を含み、`--output-dir` を backend に渡さない |
| TC-009 | dry-run | backend process not executed |
| TC-010 | missing prompt pack | blocked / rejected |
| TC-011 | missing metadata | prompt pack required files / JSON fields / authority boundary 欠落で blocked / rejected |
| TC-012 | unsafe output target | rejected |
| TC-013 | backend non-zero | blocked; no adoption claims |
| TC-014 | timeout | blocked; timeout diagnostics |
| TC-015 | redaction | secret-like data and host paths redacted |
| TC-016 | local-context | lower authority and explicit EAL requirement preserved |
| TC-017 | compatibility script | no hardcoded personal default; contract parity |

## 7. Delegation Contract

実装は `dev-coder` へ委任可能だが、親 orchestrator は次を保持する。

- Canonical docs の採用判断。
- `report.md` evidence integration。
- reviewer gate の依頼と結果記録。
- `issue finish` 判断。

Parent direct implementation exception を使う場合は `report.md` に理由、許可範囲、検証、reviewer gate を記録する。

## 8. Stop Conditions

- `authoring backend invoke` が ZIP review/stage や adoption へ scope 拡張しそうになった場合。
- backend command を hardcoded local path に固定する必要が出た場合。
- shell execution が必要になる設計になった場合。
- raw secret / local absolute path を durable docs に保存する必要が出た場合。
- `.assurance.json`、reviewer pass、execution-ready、PR-ready を command が自己主張しそうになった場合。
- focused tests が既存挙動を広く壊す場合。
- provider source と dogfood mirror の同期方針が不明な場合。

## 9. Verification Queue

最低限の完了検証:

```bash
uv run pytest tests/cli_runtime/test_authoring.py -q
./spec-dock/scripts/spec-dock authoring backend invoke --help
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

`iss-00300` finish 前には、`report.md` に次を記録する。

- local verification result。
- reviewer gate result。
- no-per-Issue-PR rationale。
- PR delivery deferred to `iss-00307`。
- no merge-prepared claim before final PR delivery。
