---
種別: 実装報告書（Issue）
ID: "iss-00300"
タイトル: "Backend Invocation Adapter"
関連GitHub: ["#300"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00295", "init-local-00003"]
Issue Grade: "standard"
---

# iss-00300 Backend Invocation Adapter — 実装報告

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger）

| ID | Status | Type | Raised By | Gap | Options | Decision | Rationale | Disposition | Evidence | Follow-up |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D-PLN-001 | resolved | scope | ChatGPT planning evidence | `authoring backend invoke` が未実装で、prompt pack と backend command の接続面がない | A: helper のみ維持; B: installed runtime command に昇格 | B を採用。ただし backend invocation のみ。 | Epic 00295 の runtime plane に backend invocation が含まれるため。 | promoted_to_design | `design.md` Target Design Delta | none |
| D-PLN-002 | resolved | operation | ChatGPT planning evidence | backend command source の優先順位 | A: env only; B: CLI override first; C: hardcoded wrapper | B。`--backend-command` -> `SPECDOCK_CHATGPT_COMMAND` -> optional `ORACLE_CHATGPT_COMMAND`。 | task brief と installed runtime portability requirement に一致。 | promoted_to_requirement | `requirement.md` RQ-002..RQ-005 | `ORACLE_CHATGPT_COMMAND` deprecation schedule は Epic open question |
| D-PLN-003 | resolved | security | ChatGPT planning evidence | shell injection / secret exposure / host-local path leakage risk | A: shell execution; B: argv + redacted summary | B。`shlex.split` + no shell execution + redacted durable summary。 | external process を扱うため fail-closed と redaction が必要。 | promoted_to_design | `design.md` Domain / Redaction Design | none |
| D-PLN-004 | resolved | scope | User / Epic policy | 中間 Issue の PR delivery | A: iss-00300 で PR; B: final quality Issue に defer | B。`iss-00307` に defer。 | Epic は Issue relay 方式で最後に 1 PR を作る。 | promoted_to_plan | `plan.md` PR Delivery Policy | none |
| D-PLN-005 | resolved | interpretation | ChatGPT planning evidence | backend success と adoption success の混同 | A: backend exit 0 を adoption success と扱う; B: invocation-local success に限定 | B。backend exit 0 は invocation success のみ。 | authority boundary を維持するため。 | promoted_to_requirement | `requirement.md` RQ-012 / AC-011 | none |
| D-REV-001 | resolved | contract | spec-reviewer | backend invocation argv ABI が曖昧 | A: stdin/envで任意; B: `--slug` / `-p` / repeated `--file` ABI を固定 | B を採用。`--output-dir` は backend に渡さず adapter summary 用に限定。 | 実装者とテストが同じ backend interface を検証できるようにするため。 | promoted_to_design | `design.md` Backend argv ABI; `plan.md` S04 / TC-008 | none |
| D-REV-002 | resolved | contract | spec-reviewer | prompt pack required metadata が曖昧 | A: readable filesだけ; B: required files / JSON fields / authority boundary を明記 | B を採用。既存 prompt pack contract の必須ファイルと fields を design に明記。 | AC-008 / CL-008 / TC-011 の fail-closed 条件を実装可能にするため。 | promoted_to_design | `design.md` PromptPackInput | none |

## 証跡採用台帳（Evidence Adoption Ledger）

| ID | adoption_status | source | target | rationale | evidence | next_action |
| --- | --- | --- | --- | --- | --- | --- |
| EAL-PLN-001 | partially_adopted | ChatGPT Use prompt / task brief | requirement.md / design.md / plan.md / report.md | iss-00300 の目的、制約、output 要求を採用。ただし reviewer pass / execution-ready / PR-ready claim は除外。 | `artifacts/20260708-chatgpt-use-planning-evidence-summary.md` | spec-reviewer review |
| EAL-PLN-002 | adopted | draft requirement artifact | requirement.md | purpose、scope、non-scope、acceptance criteria を正式要件へ再記述した。 | `artifacts/20260707t171251z-draft-requirement-implement-backend-invocation-adapter-draft-requirement.md` | none |
| EAL-PLN-003 | adopted | draft design artifact | design.md | target paths、runtime/docs/skill impact、failure modes を正式設計へ統合した。 | `artifacts/20260707t171251z-01-draft-design-implement-backend-invocation-adapter-draft-design.md` | none |
| EAL-PLN-004 | adopted | draft plan artifact | plan.md | step sequence と verification seeds を closure index / milestone plan へ拡張した。 | `artifacts/20260707t171252z-draft-plan-implement-backend-invocation-adapter-draft-plan.md` | none |
| EAL-PLN-005 | partially_adopted | ChatGPT planning response | requirement.md / design.md / plan.md / report.md | command priority、dry-run、redaction、local-context authority、PR defer policy を採用。raw transcript、reviewer pass、execution-ready claim は採用しない。 | `artifacts/20260708-chatgpt-use-planning-evidence-summary.md` | spec-reviewer review |
| EAL-REV-001 | adopted | spec-reviewer finding | requirement.md / design.md / plan.md / report.md | P1 backend argv ABI gap と P2 prompt-pack metadata gap を採用して planning docs に反映した。 | spec-reviewer review result `review_status: fail` | re-review |
| EAL-REV-002 | adopted | spec-reviewer re-review | report.md | backend argv ABI と prompt pack metadata の修正後に fresh pass を確認した。 | spec-reviewer review result `review_status: pass` | none |
| EAL-REV-003 | adopted | qa-reviewer finding | tests/cli_runtime/test_authoring.py | timeout、malformed command、prompt-pack/output safety、compatibility script smoke の不足を採用して regression を追加した。 | qa-reviewer review result `review_status: fail` | re-review |
| EAL-REV-004 | adopted | code-reviewer finding | backend_invoke.py / backend_invoke_contract.py / tests | durable summary argv/path redaction、symlink parent canonical output rejection、backend OSError mapping を採用して修正した。 | code-reviewer review result `review_status: fail` | re-review |
| EAL-REV-005 | adopted | spec-reviewer finding | invoke_chatgpt_backend.py / report.md / tests | compatibility script を runtime service 委譲へ変更し、closure-level evidence を report に追加した。 | spec-reviewer review result `review_status: fail` | re-review |
| EAL-REV-006 | adopted | code-reviewer re-review finding | backend_invoke.py / backend_invoke_contract.py / tests | unsafe manifest blocker に host-local absolute path を残さないよう classified blocker へ変更し、summary blockers / remediation も redaction 対象にした。 | code-reviewer review result `review_status: pass` with P2 finding | re-review |
| EAL-REV-007 | adopted | qa-reviewer re-review finding | backend_invoke.py / tests/cli_runtime/test_authoring.py | non-canonical parent symlink output rejection と password/key/GitHub/Slack/AWS token family redaction の P1 を採用して修正した。 | qa-reviewer review result `review_status: fail` | re-review |
| EAL-REV-008 | adopted | qa-reviewer final finding | backend_invoke.py / backend_invoke_contract.py / tests/cli_runtime/test_authoring.py | env-style secret names (`DATABASE_PASSWORD=`, `MY_API_KEY=`, `SERVICE_TOKEN=`, `CUSTOM_SECRET=`) の P1 redaction gap を採用して修正した。 | qa-reviewer review result `review_status: fail` | re-review |
| EAL-REV-009 | adopted | code-reviewer re-review findings | backend_invoke.py / tests/cli_runtime/test_authoring.py | file-valued output dir と non-UTF-8 backend streams の P2 robustness gap を採用し、deterministic JSON diagnostics と replacement decode を追加した。 | code-reviewer review result `review_status: pass` with P2 findings | re-review |
| EAL-REV-010 | adopted | qa-reviewer re-review finding | backend_invoke.py / tests/cli_runtime/test_authoring.py | relative symlinked output parent の P1 bypass を採用し、relative path でも user-controlled parent symlink を拒否するようにした。 | qa-reviewer review result `review_status: fail` | re-review |
| EAL-REV-011 | adopted | code-reviewer final findings | backend_invoke_contract.py / invoke_chatgpt_backend.py / tests | separated secret option values (`--token abc123`) の P1 leak と legacy wrapper prompt-only 互換性 P2 を採用して修正した。 | code-reviewer review result `review_status: fail` | re-review |
| EAL-REV-012 | adopted | qa-reviewer final finding | backend_invoke.py / tests/cli_runtime/test_authoring.py | stdout/stderr stream redaction でも separated secret option values (`--token abc123`) を redaction 対象に追加した。 | qa-reviewer review result `review_status: fail` | re-review |
| EAL-REV-013 | adopted | code-reviewer final re-review | report.md | latest diff に対する code review pass を確認した。 | code-reviewer review result `review_status: pass` | none |
| EAL-REV-014 | adopted | qa-reviewer final re-review | report.md | latest diff に対する QA review pass を確認した。 | qa-reviewer review result `review_status: pass` | none |
| EAL-ISSUE-PLACEMENT-001 | adopted | Epic artifact placement manifest | `iss-00296`..`iss-00307` issue artifacts | Epic 配下 12 Issue が作成済みで、各 Issue-local `artifacts/` に draft requirement / draft design / draft plan が配置済みであることを実装前提として採用した。 | `spec-dock/active/epic/artifacts/20260707t204133z-research-issue-creation-and-draft-artifact-placement-manifest.md` | none |

## 目的整合台帳（Objective Alignment Ledger）

| 対象 | primary objective evidence | secondary requirement evidence | inversion risk | reviewer verdict |
| --- | --- | --- | --- | --- |
| OAL-PLN-001 | `authoring backend invoke` を explicit backend command で fail-closed に実装する planning package | redaction、local-context lower authority、no PR delivery | low | spec-reviewer pass |
| OAL-PLN-002 | backend invocation only; no ZIP/stage/adoption expansion | compatibility script / docs updates | medium | spec-reviewer pass |

## 仕様 authoring ゲート（Spec Authoring Gate）

| phase | investigated facts | open questions / answers | adoption decision | reviewer verdict | blocking | promotion / next_action |
| --- | --- | --- | --- | --- | --- | --- |
| requirement | Epic docs、Issue draft artifacts、ChatGPT Use planning evidence、existing `authoring` command surface | `ORACLE_CHATGPT_COMMAND` deprecation schedule はこの Issue では決めない | adopted into `requirement.md` | pass | no | promote |
| design | existing `pack_prepare` contract、prompt pack authority boundary、draft design、ChatGPT design proposal | provider registry は non-scope | adopted into `design.md` | pass | no | promote |
| plan | draft plan、ChatGPT closure index、relay PR delivery policy | final PR delivery は `iss-00307` | adopted into `plan.md` | pass | no | promote |

## 委任ドラフト証跡（Delegated Draft Evidence）

| created_by_role | scope_id | artifact draft path | source_paths | intended_targets | adoption_status | reflected_to | diff_guard_result | integration result | rejected portions | blockers | reviewer result | promotion decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ChatGPT Use / GPT-5.5 Pro Extended | iss-00300 | `artifacts/20260708-chatgpt-use-planning-evidence-summary.md` | Epic docs、Issue draft artifacts、runtime command files、tests | `requirement.md`, `design.md`, `plan.md`, `report.md` | partially_adopted | `requirement.md`, `design.md`, `plan.md`, `report.md` | pass | integrated by orchestrator | reviewer pass and execution-ready claims were not adopted without local review | none | pass | promote |

## ワークフロー単位の named role 許可（Workflow-Scoped Authorization）

| authorization source | repo/worktree | active issue | session | named roles | boundary | expires / invalidation | denied / unavailable / host conflict reason | next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| user request to execute Epic through SpecDock workflow | `chemitaro/spec-dock` / current worktree | iss-00300 | current session | spec-reviewer / code-reviewer / qa-reviewer / dev-coder / doc-writer | active repo/worktree、active SpecDock scope、current session、SpecDock-defined named roles、documented role responsibility | issue complete / scope change / user revocation / host policy conflict | none | continue |

## グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）

| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |
| --- | --- | --- | --- | --- | --- |
| `standard` | manual fallback | used | manual evidence from ChatGPT Use planning package plus orchestrator adoption in `artifacts/20260708-chatgpt-use-planning-evidence-summary.md`, `requirement.md`, `design.md`, and `plan.md` | pass | ready |

## レビューゲート状態（Reviewer Gate Status）

| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| planning | spec planning review | spec-reviewer | fresh | pass | no | promote | Re-review passed after backend argv ABI and prompt pack metadata contract were clarified. |
| implementation | code review | code-reviewer | fresh | pass | no | promote | Latest code-reviewer re-review returned no findings. |
| implementation | QA review | qa-reviewer | fresh | pass | no | promote | Latest QA re-review returned no findings. |
| final-local | final spec review | spec-reviewer | fresh | pass | no | promote | Planning spec-reviewer pass plus implementation code/QA pass and closure evidence are recorded. |

## 実装委任ゲート（Implementation Delegation Gate）

| step | decision | required reason | delegated role | delegated scope | source of truth | allowed changes | forbidden changes | required verification | stop conditions | output required | observed result |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S01-S07 | delegated ok | runtime command / shipped scaffold / tests | dev-coder | approved plan implementation | `requirement.md`, `design.md`, `plan.md` | allowed change surface in `plan.md` | non-scope commands, hardcoded local path, PR delivery | focused pytest, validate, assurance, diff check | scope expansion, unsafe authority claim | worker summary / changed files / verification / risks | pass: implementation completed; focused CLI suite, installer inventory test, validate, assurance, py_compile, diff check executed |
| S90 | delegated ok | report/docs evidence | doc-writer or orchestrator | report evidence updates | `plan.md`, observed verification | `report.md` only unless docs impact discovered | new requirements / reviewer pass self-claim | docs inspection / validate | unresolved doc impact | updated evidence rows | pass: report updated with reviewer findings, closure coverage, and issue/draft placement evidence |

## 実装記録（セッションログ）

### セッションログ（2026-07-08 planning）

#### 対象

- Phase: Issue planning
- AC: AC-001..AC-017

#### 実施内容

- `iss-00300` の scaffold requirement を正式要件へ置き換えた。
- `assurance classify --stage requirement` を実行し、`authorized_profile=standard` を確認した。
- `assurance compose --artifact all` を実行し、Standard 用の design / plan / report surface を生成した。
- ChatGPT Use planning evidence と Issue-local draft artifacts を採用し、`design.md` / `plan.md` / `report.md` を具体化した。

#### 実行コマンド / 結果

```bash
./spec-dock/scripts/spec-dock assurance classify --stage requirement

assurance classify: ok
issue: iss-00300
mode: adaptive
has_contract: true
authorized_profile: standard
complexity_tier: normal
lite_candidate: false
lite_authorized: false
reason: ok
```

```bash
./spec-dock/scripts/spec-dock assurance compose --artifact all

assurance compose: ok
issue: iss-00300
authorized_profile: standard
```

### セッションログ（2026-07-08 implementation）

#### 対象

- Phase: Issue execution
- AC: AC-001..AC-017

#### 実施内容

- `authoring backend invoke` を deferred skeleton から実装済み command に切り替えた。
- backend command を `--backend-command`、`SPECDOCK_CHATGPT_COMMAND`、`ORACLE_CHATGPT_COMMAND` の順に解決する adapter を追加した。
- prompt pack の必須ファイル / metadata / authority boundary を invocation 前に検証するようにした。
- resolved backend argv に `--slug`、`-p`、repeated `--file` を追加する固定 ABI を実装し、`--output-dir` は backend に渡さないようにした。
- dry-run、backend non-zero、timeout、unsafe output、redaction、local-context lower authority の diagnostics を追加した。
- provider-side runtime と dogfood runtime mirror の両方へ実装を反映した。
- dogfood runtime で使える compatibility script として `spec-dock/scripts/authoring-pack/invoke_chatgpt_backend.py` を配置した。

#### 実行コマンド / 結果

```bash
uv run pytest tests/cli_runtime/test_authoring.py -q

75 passed in 43.15s
```

```bash
./spec-dock/scripts/spec-dock authoring backend invoke --help

exit: 0
help exposes --prompt-pack, --output-dir, --backend-command, --evidence-mode, --timeout-seconds, --dry-run
```

```bash
uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_init_installs_authoring_pack_helper_inventory -q

1 passed in 0.11s
```

```bash
python -m py_compile src/spec_dock/assets/spec_dock/scripts/authoring-pack/invoke_chatgpt_backend.py

exit: 0
```

```bash
./spec-dock/scripts/spec-dock validate

spec-dock: ok (validate) nodes=202
```

```bash
./spec-dock/scripts/spec-dock assurance verify

assurance verify: ok
issue: iss-00300
mode: adaptive
has_contract: true
authorized_profile: standard
complexity_tier: normal
lite_candidate: false
lite_authorized: false
reason: ok
```

```bash
git diff --check

exit: 0
```

## Closure Coverage（CL / AC 対応証跡）

| Closure | Requirement / AC | Evidence | Result |
| --- | --- | --- | --- |
| CL-001 | AC-001 | `test_authoring_backend_invoke_help_exposes_contract_without_force`; `./spec-dock/scripts/spec-dock authoring backend invoke --help` | pass |
| CL-002 | AC-002 | `test_authoring_backend_invoke_unset_backend_blocks` | pass |
| CL-003 | AC-003 | `test_authoring_backend_invoke_cli_backend_command_overrides_env_and_dry_run_skips_execution` | pass |
| CL-004 | AC-004 | `test_authoring_backend_invoke_primary_env_precedes_oracle_fallback` | pass |
| CL-005 | AC-005 | `test_authoring_backend_invoke_oracle_fallback_when_primary_empty` | pass |
| CL-006 | AC-006 / AC-010 | `test_authoring_backend_invoke_malformed_command_blocks_without_shell`; `test_authoring_backend_invoke_passes_argv_without_shell`; `test_authoring_backend_invoke_redacts_summary_argv_and_paths` | pass |
| CL-007 | AC-007 | `test_authoring_backend_invoke_cli_backend_command_overrides_env_and_dry_run_skips_execution` | pass |
| CL-008 | AC-008 | `test_authoring_backend_invoke_missing_metadata_and_unsafe_output_fail_closed`; `test_authoring_backend_invoke_blocks_missing_prompt_pack_and_prompt_file_symlink` | pass |
| CL-009 | AC-009 | `test_authoring_backend_invoke_rejects_unsafe_output_target_with_valid_pack`; `test_authoring_backend_invoke_rejects_symlinked_output_parent`; `test_authoring_backend_invoke_rejects_noncanonical_symlinked_output_parent`; `test_authoring_backend_invoke_rejects_relative_symlinked_output_parent`; `test_authoring_backend_invoke_rejects_file_output_dir`; `test_authoring_backend_invoke_rejects_symlinked_summary` | pass |
| CL-010 | AC-011 | `test_authoring_backend_invoke_backend_non_zero_timeout_redaction_and_local_context` | pass |
| CL-011 | AC-012 | `test_authoring_backend_invoke_timeout_blocks` | pass |
| CL-012 | AC-013 | `test_authoring_backend_invoke_backend_non_zero_timeout_redaction_and_local_context`; `test_authoring_backend_invoke_redacts_summary_argv_and_paths`; secret family coverage includes `password=`, `key=`, `DATABASE_PASSWORD=`, `MY_API_KEY=`, `SERVICE_TOKEN=`, `CUSTOM_SECRET=`, separated stream values like `--token abc123`, `ghp_`, `xoxb-`, and `AKIA...` values in payload and durable summary | pass |
| CL-012b | AC-013 | `test_authoring_backend_invoke_redacts_separate_secret_option_values` | pass |
| CL-013 | AC-014 | `test_authoring_backend_invoke_backend_non_zero_timeout_redaction_and_local_context` | pass |
| CL-013b | AC-011 / AC-012 / AC-013 | `test_authoring_backend_invoke_decodes_non_utf8_backend_streams` | pass |
| CL-014 | AC-015 | `test_authoring_backend_invoke_dogfood_runtime_path_smoke`; `./spec-dock/scripts/spec-dock authoring backend invoke --help` | pass |
| CL-015 | AC-016 | `test_authoring_backend_invoke_compatibility_script_smoke`; `test_authoring_backend_invoke_compatibility_script_legacy_file_mode`; `test_authoring_backend_invoke_compatibility_script_legacy_prompt_only_mode`; compatibility script delegates to `invoke_backend` runtime service | pass |
| CL-016 | AC-017 | PR Delivery Defer Evidence section; no PR created in `iss-00300` | pass |

## 最終品質ゲート（Final Quality Gate）

| Gate | Status | Evidence |
| --- | --- | --- |
| Planning docs authored | pass | `requirement.md`, `design.md`, `plan.md` updated |
| Spec review | pass | planning spec-reviewer re-review returned `review_status: pass` |
| Implementation tests | pass | `uv run pytest tests/cli_runtime/test_authoring.py -q` -> `75 passed in 43.15s`; `uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_init_installs_authoring_pack_helper_inventory -q` -> `1 passed in 0.11s`; `./spec-dock/scripts/spec-dock authoring backend invoke --help`; `python -m py_compile src/spec_dock/assets/spec_dock/scripts/authoring-pack/invoke_chatgpt_backend.py`; `./spec-dock/scripts/spec-dock validate`; `./spec-dock/scripts/spec-dock assurance verify`; `git diff --check` |
| Code review | pass | code-reviewer final re-review returned `review_status: pass` with no findings |
| QA review | pass | qa-reviewer final re-review returned `review_status: pass` with no findings |
| PR delivery | deferred | final quality gate Issue `iss-00307` |

## PR Delivery Defer Evidence

| Item | Evidence |
| --- | --- |
| final quality Issue | `iss-00307` |
| rationale | Epic 00295 requires no per-Issue PR. Intermediate Issues are finished one by one, and a single mergeable PR is delivered at the final quality gate. |
| current Issue behavior | `iss-00300` may finish after local quality gates and reviewer passes, but must not create a PR. |
| merge-prepared claim | not claimed |
