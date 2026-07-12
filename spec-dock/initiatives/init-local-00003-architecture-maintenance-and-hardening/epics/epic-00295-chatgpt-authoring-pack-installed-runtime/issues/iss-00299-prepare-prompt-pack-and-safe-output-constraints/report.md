---
種別: 実装報告書（Issue）
ID: "iss-00299"
タイトル: "Prompt Pack Constraints"
関連GitHub: ["#299"]
状態: "planning-ready"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00295", "init-local-00003"]
---

# iss-00299 Prompt Pack Constraints — 実装報告

この文書は観測証跡台帳である。`requirement.md`、`design.md`、`plan.md` は planned contract を持ち、この文書は ChatGPT authoring evidence、draft adoption、reviewer gate、実装中の観測結果、verification、commit、Issue finish、PR defer evidence を記録する。

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger）

| ID | Status | Type | Raised By | Gap | Options | Decision | Rationale | Disposition | Evidence | Follow-up |
|---|---|---|---|---|---|---|---|---|---|---|
| D-001 | resolved | scope | orchestrator | `authoring pack prepare` が backend invocation / ZIP review / stage と接続しやすい | A: 後続 commands までまとめて実装; B: prompt pack prepare と safe output constraints に限定 | B を採用 | Epic plan は backend invocation を `iss-00300`、ZIP review/stage を `iss-00301` に分離しているため | applied | `requirement.md` §5.2, `design.md` §11, `plan.md` §1 | none |
| D-002 | resolved | operation | ChatGPT Use / orchestrator | ChatGPT connector は current branch を見つけられず default branch `main` を inspected base とした | A: ChatGPT 出力を棄却; B: GitHub connector access 成功と branch bundle attachment を補助証跡として採用 | B を採用 | current branch は実際に push 済みで、添付 bundle は active branch の source context を含むため。ただし ChatGPT 出力は evidence-only として採用する | applied | `artifacts/20260708-chatgpt-use-planning-evidence-summary.md` | none |
| D-003 | resolved | grade | ChatGPT Use / orchestrator | ChatGPT Use は strict を推奨したが、SpecDock assurance は `authorized_profile=standard` を返した | A: strict に昇格; B: workflow authority は standard とし、strict 相当リスクを reviewer focus として扱う | B を採用 | `authorized_profile` が obligation authority であり、ChatGPT 推奨は evidence-only の risk signal であるため | applied | `./spec-dock/scripts/spec-dock assurance classify --stage requirement`, `requirement.md` §10, `plan.md` §0 | none |
| D-004 | resolved | authority-boundary | spec-reviewer / orchestrator | working tree diff に `.assurance.json` source binding refresh が含まれており、AC-012 の runtime no-mutation guarantee と混同されうる | A: `.assurance.json` 差分を runtime change として扱う; B: planning workflow-owned `assurance classify` refresh と runtime behavior を明確に分離する | B を採用 | `.assurance.json` は Issue planning gate の workflow-owned refresh であり、`authoring pack prepare` runtime は `.assurance.json` を作成・更新しない。AC-012 は runtime behavior の no canonical write/no `.assurance.json` mutation として検証する | applied | `./spec-dock/scripts/spec-dock assurance verify`; pack prepare tests for canonical target / symlink target rejection | none |

## 証跡採用台帳（Evidence Adoption Ledger）

| ID | adoption_status | source | target | rationale | evidence | next_action |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | ChatGPT ZIP draft requirement | `requirement.md` | `authoring pack prepare` の目的、evidence-only、safe output constraints、PR defer が親 Epic と一致するため正式要件へ再記述して採用 | `artifacts/20260707t171246z-draft-requirement-prepare-prompt-pack-and-safe-output-constraints-draft-requirement.md` | fresh spec-reviewer |
| EAL-002 | adopted | ChatGPT ZIP draft design | `design.md` | provider-side paths、runtime/docs/skill impact、failure modes を採用し、後続 Issue 境界を明確化した | `artifacts/20260707t171247z-draft-design-prepare-prompt-pack-and-safe-output-constraints-draft-design.md` | fresh spec-reviewer |
| EAL-003 | adopted | ChatGPT ZIP draft plan | `plan.md` | step sequence と verification focus を採用し、Spec-Locked Closure Index と step-local concrete test cards へ拡張した | `artifacts/20260707t171247z-01-draft-plan-prepare-prompt-pack-and-safe-output-constraints-draft-plan.md` | fresh spec-reviewer |
| EAL-004 | adopted | ChatGPT Use planning response | requirement/design/plan/report | draft artifacts を formal planning package に具体化する high-depth analysis として採用。ただし branch access caveat は D-002 に記録 | `artifacts/20260708-chatgpt-use-planning-evidence-summary.md` | fresh spec-reviewer |

## 目的整合台帳（Objective Alignment Ledger）

| 対象 | primary objective evidence | secondary requirement evidence | inversion risk | reviewer verdict |
|---|---|---|---|---|
| Prompt pack prepare | `requirement.md` §0-§7 が deterministic prompt pack と safe output constraints を主目的としている | local-context、source manifest cache exclusion、PR defer は主目的を補助する境界として記載 | low | pending |

## 仕様 authoring ゲート（Spec Authoring Gate）

| phase | investigated facts | open questions / answers | adoption decision | reviewer verdict | blocking | promotion / next_action |
|---|---|---|---|---|---|---|
| requirement | 親 Epic requirement/design/plan、Issue draft requirement、ChatGPT Use planning response、iss-00298 実装済み preflight contract | ChatGPT connector は current branch 未検出。D-002 として補助証跡扱いにした | draft requirement と ChatGPT Use response を正式 requirement へ採用 | pass | no | execute approved plan |
| design | parent Epic design、iss-00298 authoring runtime files、draft design、ChatGPT Use response | backend invocation / ZIP review / validators は後続 Issue として除外 | draft design と ChatGPT Use response を正式 design へ採用 | pass | no | execute approved plan |
| plan | parent Epic relay policy、draft plan、ChatGPT Use step-local cards | `authorized_profile=standard`。strict 推奨は reviewer focus として採用 | draft plan と ChatGPT Use response を executable plan へ採用 | pass | no | execute approved plan |

## 委任ドラフト証跡（Delegated Draft Evidence）

| created_by_role | scope_id | artifact draft path | source_paths | intended_targets | adoption_status | reflected_to | diff_guard_result | integration result | rejected portions | blockers | reviewer result | promotion decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ChatGPT ZIP authoring | iss-00299 | `artifacts/20260707t171246z-draft-requirement-prepare-prompt-pack-and-safe-output-constraints-draft-requirement.md` | `epic-00295/requirement.md`, `epic-00295/plan.md` | `requirement.md` | adopted | [`requirement.md`] | manual diff inspection pass | integrated | none | none | pass | execute approved plan |
| ChatGPT ZIP authoring | iss-00299 | `artifacts/20260707t171247z-draft-design-prepare-prompt-pack-and-safe-output-constraints-draft-design.md` | `requirement.md`, `epic-00295/design.md` | `design.md` | adopted | [`design.md`] | manual diff inspection pass | integrated with later-issue boundaries | backend / ZIP review / validators | none | pass | execute approved plan |
| ChatGPT ZIP authoring | iss-00299 | `artifacts/20260707t171247z-01-draft-plan-prepare-prompt-pack-and-safe-output-constraints-draft-plan.md` | `requirement.md`, `design.md` | `plan.md` | adopted | [`plan.md`] | manual diff inspection pass | integrated with standard authorized profile and strict-risk reviewer focus | none | none | pass | execute approved plan |
| ChatGPT Use GPT-5.5 Pro Extended | iss-00299 | `artifacts/20260708-chatgpt-use-planning-evidence-summary.md` | attached active Epic/Issue/docs/runtime files | `requirement.md`, `design.md`, `plan.md`, `report.md` | adopted | [`requirement.md`, `design.md`, `plan.md`, `report.md`] | manual section extraction pass | integrated | branch access caveat recorded in D-002 | none | pass | execute approved plan |

## ワークフロー単位の named role 許可（Workflow-Scoped Authorization）

| authorization source | repo/worktree | active issue | session | named roles | boundary | expires / invalidation condition | denied / unavailable / host conflict reason | next action |
|---|---|---|---|---|---|---|---|---|
| ユーザーによる Epic 実装依頼 | `/Users/iwasawayuuta/.codex/worktrees/aa9c/spec-dock` | iss-00299 | current session | spec-reviewer / code-reviewer / qa-reviewer / dev-coder / ChatGPT Use | active repo/worktree、active SpecDock scope、current session、SpecDock-defined role responsibility に限定。外部公開、credentialed mutation、scope expansion は含まない | issue complete / scope change / user revocation | none | continue workflow |

## グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）

| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |
|---|---|---|---|---|---|
| standard | ChatGPT Use / manual fallback | used | ChatGPT Use planning evidence summary, `authorized_profile=standard`, and manual adoption into canonical docs | pass | ready |

## 実装記録（Session Log）

### Planning session 2026-07-08

#### 対象

- Phase: Issue planning
- AC/EC: requirement / design / plan formalization

#### 実施内容

- active issue が `iss-00299` であることを確認した。
- `iss-00298` を finish 後、`iss-00299` を start した。
- current branch `iss-00299-prepare-prompt-pack-and-safe-output-constraints` を GitHub に push した。
- ChatGPT Use GPT-5.5 Pro Extended に、current branch / parent Epic / issue drafts / authoring runtime filesを添付して planning package 作成を依頼した。
- ChatGPT output を evidence-only として扱い、正式 `requirement.md` / `design.md` / `plan.md` へ再記述・採用した。

#### 実行コマンド / 結果

```bash
git push -u origin iss-00299-prepare-prompt-pack-and-safe-output-constraints
# pushed and branch set to track origin/iss-00299-prepare-prompt-pack-and-safe-output-constraints

chatgpt-use session slug: iss-00299-planning
# completed; portable summary recorded at artifacts/20260708-chatgpt-use-planning-evidence-summary.md

./spec-dock/scripts/spec-dock guidance issue-planning
# state=requirement-capture, next_action=requirement-capture-required
```

## Verification Evidence

| Command / check | Scope | Observed result | Evidence owner | Notes |
|---|---|---|---|---|
| ChatGPT Use `iss-00299-planning` | planning package draft | completed | orchestrator | GPT-5.5 Pro Extended; portable evidence summary recorded at `artifacts/20260708-chatgpt-use-planning-evidence-summary.md` |
| `git status --short` before adoption | local worktree before docs adoption | clean | orchestrator | issue start / push did not leave local diff |
| `./spec-dock/scripts/spec-dock guidance issue-execution` | execution readiness | `state=ready`, `may_execute_approved_plan=true`, `reason_code=assurance-valid` | orchestrator | `authorized_profile=standard` |
| `uv run pytest tests/cli_runtime/test_authoring.py -q` | authoring preflight and pack prepare CLI/runtime tests | pass: `46 passed` | dev-coder / orchestrator | covers implemented prepare, deferred remaining commands, deterministic output, local-context, stale/blocked/missing metadata fail-closed, unsafe source/context/text rejection, source-manifest cache exclusion/hash recomputation, symlink output and diagnostics rejection, complete prompt guidance, canonical target rejection, dogfood mirror smoke |
| `./spec-dock/scripts/spec-dock authoring pack prepare --help` | dogfood mirror CLI help | pass; `--preflight`, `--output-dir`, `--format`, `--mode`, `--source-manifest`, `--stale-if`; no `--force` | orchestrator | TC-S02-001 |
| `./spec-dock/scripts/spec-dock authoring pack prepare --preflight tests/fixtures/authoring_pack/prepare/valid-github-synced-preflight.json --output-dir /private/tmp/specdock-iss-00299-pack --format json` | valid github-synced fixture smoke | pass; status=`pass`, authority=`evidence_only`, github_sync=`verified` | orchestrator | generated required prompt pack files |
| `./spec-dock/scripts/spec-dock authoring pack prepare --preflight tests/fixtures/authoring_pack/prepare/valid-local-context-preflight.json --output-dir /private/tmp/specdock-iss-00299-local-context-pack --format json` | valid local-context fixture smoke | pass; status=`pass`, github_sync=`not_verified`, sync_state=`local_context` | orchestrator | preserves lower-authority provenance |
| `./spec-dock/scripts/spec-dock authoring pack prepare --preflight tests/fixtures/authoring_pack/prepare/blocked-preflight.json --output-dir /private/tmp/specdock-iss-00299-blocked-pack --format json` | blocked preflight fixture smoke | expected non-zero; status=`blocked`, output_files=`[]` | orchestrator | fail-closed; diagnostics-only |
| `./spec-dock/scripts/spec-dock authoring pack prepare --preflight tests/fixtures/authoring_pack/prepare/missing-required-metadata-preflight.json --output-dir /private/tmp/specdock-iss-00299-missing-pack --format json` | missing metadata fixture smoke | expected non-zero; status=`fail`, blockers include `missing_source_manifest_hash` and `missing_source_hashes` | orchestrator | fail-closed; diagnostics-only |
| `uv run pytest tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_pack_prepare_filters_cache_entries_from_explicit_source_manifest -q` | explicit source-manifest cache exclusion | covered in full focused suite | orchestrator | prevents `__pycache__`, `.pyc`, `.pyo` from durable pack manifest |
| `uv run pytest tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_pack_prepare_rejects_symlinked_output_entries -q` | symlink output target rejection | covered in full focused suite | orchestrator | prevents symlink-mediated canonical / `.assurance.json` mutation |
| `uv run pytest tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_pack_prepare_rejects_symlinked_diagnostics_output -q` | symlink diagnostics target rejection | covered in full focused suite | orchestrator | prevents non-pass diagnostics from following symlinks into canonical / `.assurance.json` targets |
| `uv run pytest tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_pack_prepare_rejects_unsafe_source_and_context_paths -q` | unsafe path / privacy guard | covered in full focused suite | orchestrator | rejects absolute, traversal, and secret-looking source/context paths |
| `uv run pytest tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_pack_prepare_rejects_unsafe_local_context_text -q` | unsafe durable local-context text guard | covered in full focused suite | orchestrator | rejects host-local / secret-looking `diff_summary` and `unsynced_reason` text before durable output |
| `uv run pytest tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_pack_prepare_filters_cache_entries_from_explicit_source_manifest -q` | explicit source-manifest hash recomputation | covered in full focused suite | orchestrator | generated `source_manifest_hash` is recomputed from filtered `source_hashes` |
| `uv run pytest tests/cli_runtime/test_authoring.py::TestAuthoringCli::test_authoring_pack_prepare_prompt_guidance_contains_lower_authority_contract -q` | prompt guidance contract | covered in full focused suite | orchestrator | includes local-context lower authority, `.assurance.json` mutation ban, and `authorized_profile` decision ban |
| `./spec-dock/scripts/spec-dock assurance verify` | Issue assurance contract | pass | orchestrator | `authorized_profile=standard`, `reason=ok` |
| `./spec-dock/scripts/spec-dock validate` | SpecDock tree | pass: `nodes=202` | orchestrator | structural validation |
| `git diff --check` | whitespace / patch health | pass | orchestrator | no output |

## Closure Evidence Ledger

| closure id | evidence | status | notes |
|---|---|---|---|
| tc-001 | iss-00298 `PreflightResult` and `SourceManifest` schema inspected and reused by `pack_prepare.py` | pass | required fields are validated before pack generation |
| tc-002 | `authoring pack prepare --help` exposes implemented args; remaining authoring commands still return deferred/fail-closed diagnostics | pass | `_DEFERRED_COMMANDS` no longer includes pack prepare |
| tc-003 | generated `manifest.json`, `provenance.json`, and `safe-output-constraints.md` fix `authority=evidence_only`, `adoption_status=unreviewed`, and forbidden authority claims | pass | achieved authority claim keys in input are rejected |
| tc-004 | github-synced pass maps to prompt pack pass; local-context pass preserves `github_sync=not_verified`; stale preflight returns non-zero stale diagnostics | pass | covered by `tests/cli_runtime/test_authoring.py` |
| tc-005 | deterministic double-run test compares normalized generated pack payloads | pass | generated tree includes `.specdock-authoring-pack`, metadata JSON, constraints, prompt, and output contract |
| tc-006 | positive / negative coverage added for github-synced, local-context, stale, blocked, missing metadata, canonical target rejection, forbidden achieved claim, unsafe source/context path/text, symlink output/diagnostics target, no `--force`, and dogfood mirror smoke | pass | focused pytest passed: `46 passed` |
| tc-007 | source manifest cache exclusion and hash recomputation covered for preflight and explicit `--source-manifest` pack prepare path | pass | `__pycache__` / `.pyc` / `.pyo` assertions and filtered hash assertion pass in focused pytest |
| tc-008 | PR delivery is explicitly deferred to `iss-00307` | pass | this Issue does not create a PR |
| tc-009 | exact verification command bundle completed | pass | see Verification Evidence |
| tc-010 | reviewer handoff package is ready | pass | code-reviewer / qa-reviewer / spec-reviewer final review_status pass |

## Reviewer Gate Status

| Gate ID | Gate | Reviewer role | Freshness | State | Risk acceptance | Promotion decision | Evidence |
|---|---|---|---|---|---|---|---|
| RG-PLAN-001 | planning spec review | spec-reviewer | fresh | pass | no | execute approved plan | 019f3e23-de84-7f90-815c-5b98a58eeee0 review_status pass |
| RG-EXEC-001 | implementation code review | code-reviewer | fresh | pass | no | promote | 019f3e32-55da-71d0-aff4-36653a804550 final review_status pass |
| RG-EXEC-002 | implementation QA review | qa-reviewer | fresh | pass | no | promote | 019f3e32-71da-7092-b845-6fd92b114a00 final review_status pass |
| RG-EXEC-003 | implementation spec review | spec-reviewer | fresh | pass | no | promote | 019f3e32-858f-7d72-9fdf-7c52b7ccb85f final review_status pass |

## Reviewer Gate History

| Gate | Status | Evidence | Next action |
|---|---|---|---|
| planning ChatGPT Use | completed | `artifacts/20260708-chatgpt-use-planning-evidence-summary.md` | fresh spec-reviewer |
| planning spec-reviewer attempt 1 | fail | P1: missing step-local delegation contracts; P2: host-local transcript path in durable evidence ledgers | fixed and re-review requested |
| planning spec-reviewer attempt 2 | pass | no findings; step-local delegation contracts and scope-local evidence summary verified | execution handoff ready |
| implementation local verification | completed | focused pytest `46 passed`; validate pass; diff check pass; dogfood positive/negative fixture smoke pass | fresh code / QA / spec review |
| implementation code-reviewer attempt 2 | fail | P1 diagnostics symlink output could still mutate canonical files on non-pass paths | fixed; re-review required |
| implementation code-reviewer attempt 1 | fail | P1 symlinked output entries could mutate canonical files; P2 non-object JSON diagnostic stability | fixed; re-review required |
| implementation qa-reviewer attempt 1 | fail | P1 blocked/missing metadata fail-closed coverage and explicit source-manifest cache exclusion coverage; P2 exact negative evidence | fixed; re-review required |
| implementation spec-reviewer attempt 1 | fail | P1 unsafe source/context path persistence, incomplete prompt guidance contract, `.assurance.json` boundary ambiguity; P2 fixture evidence | fixed; re-review required |
| implementation spec-reviewer attempt 2 | fail | P1 filtered source manifest hash preserved original cache-inclusive hash; P1 unsafe local-context text could persist host-local/secret-looking paths | fixed; re-review required |
| implementation final code-reviewer | pass | no findings; provider/dogfood mirror reviewed for command dispatch, path safety, deterministic generation, JSON fail-closed behavior, authority-boundary handling | commit candidate |
| implementation final qa-reviewer | pass | no findings; 46-test suite and report evidence cover latest safety/cache/prompt guidance obligations | commit candidate |
| implementation final spec-reviewer | pass | no findings; safety/privacy/cache, prompt contract, `.assurance.json` boundary separation, and PR defer all satisfy reviewed scope | commit candidate |

## PR Delivery Defer Evidence

この Issue は中間 Issue のため PR delivery を行わない。Epic-level PR delivery、CI / review repair、mergeable PR 作成は final quality gate Issue `iss-00307` で実施する。
