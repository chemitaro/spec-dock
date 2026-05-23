---
種別: 実装報告書（Issue）
ID: "iss-00117"
タイトル: "Codex Delegated Author Adapters"
関連GitHub: ["#117"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-05-23"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00112", "init-local-00003"]
---

# iss-00117 Codex Delegated Author Adapters — 実装報告（Observed Evidence Ledger）

> `report.md` は observed evidence ledger。planned requirements、evidence destination、closure 条件は `plan.md` が所有し、この文書は実際の Red / Green / Refactor evidence、discovered tests、closure delta、reviewer status、commit/no-op evidence を記録する。

## Spec Interpretation / Decision Ledger (必須)

| ID | Status | Type | Raised By | Trigger / Gap | Options Considered | Decision / Interpretation | Rationale | Disposition | Evidence | Follow-up |
|---|---|---|---|---|---|---|---|---|---|---|
| D-001 | resolved | implementation | orchestrator | Existing untracked adapter draft content represented role behavior directly but did not assert the Issue's thin adapter / role-skill authority boundary. | keep direct role instructions; replace with thin wrappers that point to role skills | Use thin Codex adapter files whose durable role authority is `.agents/skills/spec-dock-system-architect/SKILL.md` / `.agents/skills/spec-dock-implementation-planner/SKILL.md`. | This satisfies AC-001 and avoids duplicating role behavior in host-specific TOML. | applied | `src/spec_dock/assets/install_root/.codex/agents/system-architect.toml`; `src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml`; targeted test -> pass | none |
| D-002 | resolved | implementation | qa-reviewer | QA flagged that `verified_host_adapter` was stronger than the recorded evidence because no live Codex host invocation/schema acceptance check was available. | keep `verified_host_adapter`; downgrade to `adapter_contract_only` | Classify this issue closure as `adapter_contract_only`: static `.codex/agents` files exist, match existing Codex agent asset shape, and are covered by provider/mirror content tests, but live host callability is not claimed. | This avoids false verified-callability while still shipping the requested thin adapter contract. | applied | QA finding `[P1] Back verified_host_adapter with host-schema evidence`; updated tc-004/S90 closure rows | Follow-up host invocation/schema verification if Codex exposes a stable local validation command. |

## 実装サマリー (任意)
- Provider source に Codex delegated author adapters for `system-architect` / `implementation-planner` を追加し、dogfooding mirror と byte parity を揃えた。
- 各 adapter は read-only / approval never / draft-only とし、role skill を source of truth とする thin wrapper contract を明示した。
- `tests/test_init_update.py` に managed asset inventory と thin adapter boundary の assertion を追加した。

## 実装記録（セッションログ） (必須)

### 2026-05-23 23:20 - 23:48

#### 対象
- Step: S01, S02, S90, S99
- AC/EC: AC-001, AC-002, AC-003, EC-001, EC-002
- Planned source:
  - `plan.md`: S01 Provider source update; S02 Dogfooding parity and verification; S90 docs impact; S99 final quality gate
  - closure ids: tc-001, tc-002, tc-003, tc-004, tc-005

#### 実施内容
- Added provider Codex adapters:
  - `src/spec_dock/assets/install_root/.codex/agents/system-architect.toml`
  - `src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml`
- Added dogfooding mirror adapters:
  - `.codex/agents/system-architect.toml`
  - `.codex/agents/implementation-planner.toml`
- Updated static managed install_root inventories and added `test_issue_117_codex_delegated_author_adapters_are_thin_skill_wrappers`.
- Kept `.github/agents` / Copilot support, runtime validation, write-capable delegation, and role registry expansion out of scope.

#### 実行コマンド / 結果
```bash
uv run python -m unittest tests.test_init_update.TestInitUpdate.test_issue_117_codex_delegated_author_adapters_are_thin_skill_wrappers -v
# OK
# Asserts provider/dogfooding adapter content and parity without undeclared parser dependencies:
# name, model, reasoning effort, web_search, approval_policy, sandbox_mode,
# features.shell_tool, and developer_instructions.

uv run python -m unittest tests.test_init_update.TestInitUpdate.test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets -v
# OK

uv run python -m unittest tests.test_init_update.TestInitUpdate.test_issue_68_authoritative_inventory_paths_are_classified_under_install_root -v
# OK

uv run python -m unittest tests.test_init_update.TestInitUpdate.test_bundled_native_shim_assets_satisfy_static_delegation_only_contract -v
# OK

uv run python -m unittest tests.test_init_update.TestInitUpdate.test_issue_68_install_root_tree_exists -v
# OK

uv run python -m unittest tests.test_init_update.TestInitUpdate.test_init_creates_expected_structure -v
# OK

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=57

./spec-dock/scripts/spec-dock sync
# spec-dock: ok (sync) wrote=spec-dock/.agent/index-all.json,...

git diff --check
# pass
```

#### Red/Green/Refactor Evidence
| step | phase | planned evidence requirement | observed evidence | command / inspection / manual record | result | notes |
|---|---|---|---|---|---|---|
| S01 | Red / alternative | inspect-only | Initial targeted adapter test failed because provider adapter content lacked explicit `intentionally thin` / role-skill authority boundary. | `uv run python -m unittest tests.test_init_update.TestInitUpdate.test_issue_117_codex_delegated_author_adapters_are_thin_skill_wrappers -v` | pass | Red reproduced missing thin-wrapper contract before final edit. |
| S01 | Green | provider source update | Provider TOML files exist and assert read-only, draft-only, role skill source of truth, no reviewer substitution, and non-scope boundaries. | targeted test + provider file inspection | pass | AC-001 closed. |
| S01 | Refactor | guardrail satisfied | No broad refactor; adapter text is small and host-specific duplication is limited to boundary/loader text. | `git diff --check` | pass | Runtime/code behavior untouched. |
| S02 | Red / alternative | test-required parity | Existing parity test would fail if dogfooding mirrors diverged from provider inventory. | `test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets` | pass | Existing parity guard covers new files once added to both surfaces. |
| S02 | Green | managed asset parity | Dogfooding adapter bytes match provider assets; static inventory includes both new Codex adapters. | targeted issue117 test; issue71 parity; issue68 classification | pass | AC-002 / EC-002 closed. |
| S02 | Refactor | no unrelated refactor | `.github/agents` untouched; only Codex adapters and tests changed. | diff inspection | pass | Parent non-scope preserved. |
| S99 | Green | final validation | validate/sync/diff hygiene passed; code-reviewer, qa-reviewer, and spec-reviewer passed. | `./spec-dock/scripts/spec-dock validate`; `./spec-dock/scripts/spec-dock sync`; `git diff --check`; reviewer outputs | pass | S99 closed after fresh final reviewers passed. |

#### Discovered Tests
| step | discovered test / risk | source | action taken | closure id / new id | plan amendment required | evidence |
|---|---|---|---|---|---|---|
| S02 | Dedicated adapter contract assertion needed for role-skill authority and non-scope boundaries. | implementation / QA finding | added test | tc-002 | no | `test_issue_117_codex_delegated_author_adapters_are_thin_skill_wrappers` asserts content/provider-dogfooding parity -> pass |
| S99 | Full package inventory test could not run in this environment because `.venv/bin/python3` has no `pip` module. | verification | recorded as environment-blocked supplemental test, not required closure evidence because targeted install_root/static/parity tests passed. | tc-002 | no | `test_issue_69_full_install_root_inventory_is_packaged_in_wheel_sdist_and_installed_resources` -> fail: `No module named pip` |

#### Step Contract Closure
| step | closure ids | close condition from plan | observed evidence | result | notes |
|---|---|---|---|---|---|
| S01 | tc-001 | target provider source is updated and inspected | provider `.codex/agents/system-architect.toml` and `implementation-planner.toml` added as read-only thin wrappers | pass | No runtime or GitHub agent expansion. |
| S02 | tc-002, tc-005 | parity/verification evidence is recorded | targeted issue117 content/parity test, issue71 parity test, issue68 classification test, init structure test | pass | No provider/consumer drift. |
| S90 | tc-004 | uncertainty or no-op path recorded if needed | Static Codex adapter files exist and are covered by content/parity tests; live Codex host callability/schema acceptance was not verified. | pass | Closure classification: `adapter_contract_only`; no verified host-callability claim. |
| S99 | tc-003 | final validation/review pass and clean closure evidence | validate/sync/diff hygiene passed; code-reviewer, qa-reviewer, and spec-reviewer passed. | pass | Ready for commit. |

#### Test Contract Closure
| closure id / test id | step | required | evidence level | pre-implementation evidence | verification command or alternative path | observed result | notes |
|---|---|---|---|---|---|---|---|
| tc-001 | S01 | yes | inspect-only | targeted test initially failed on missing thin-wrapper fragments | `test_issue_117_codex_delegated_author_adapters_are_thin_skill_wrappers` | pass | Provider contract asserted. |
| tc-002 | S02 | yes | test-required | existing parity guard plus new targeted adapter assertion | issue117 targeted content/parity test; issue71 parity; issue68 classification; init structure | pass | Package inventory supplemental test blocked by missing pip. |
| tc-003 | S99 | yes | manual-required | reviewer pending | final spec-reviewer re-review | pass | Final spec gate passed after stale evidence cleanup. |
| tc-004 | S90 | yes | inspect-only | live host callability verification unavailable in this issue | file inspection + targeted content/parity test | pass | Static adapter contract recorded; closed as `adapter_contract_only`; no live host-callability claim. |
| tc-005 | S02 | yes | inspect-only | provider/consumer mirror included in targeted test | issue117 targeted test + issue71 parity | pass | No drift. |

#### Closure Coverage
| closure id | step | verification evidence | observed result | notes |
|---|---|---|---|---|
| tc-001 | S01 | provider files + targeted adapter assertion | pass | AC-001 |
| tc-002 | S02 | targeted issue117 content/parity test + parity/classification/init tests + validate/sync | pass | AC-002 |
| tc-003 | S99 | final reviewer gate | pass | AC-003 |
| tc-004 | S90 | uncertainty path recorded; static path/content verified but live host callability not claimed | pass | EC-001; closure classification `adapter_contract_only` |
| tc-005 | S02 | provider/dogfooding byte parity | pass | EC-002 |

#### Closure Delta
| change | closure id | test id alias | resolves to closure id | reason | plan amendment required | re-review required |
|---|---|---|---|---|---|---|
| added | tc-002 | `test_issue_117_codex_delegated_author_adapters_are_thin_skill_wrappers` | tc-002 | targeted managed adapter contract assertion | no | yes |

#### Workflow Delegation Consent
| consent source | repo/worktree | active issue | session | named roles | boundary | expires / invalidation condition | denied / unavailable reason | next action |
|---|---|---|---|---|---|---|---|---|
| user instruction | `/Users/iwasawayuuta/workspace/tools/spec-dock-worktrees/spec-dock-delegated-authoring-architecture` | iss-00117 | current session | code-reviewer / qa-reviewer / spec-reviewer | same repo, active issue, session, named role; no destructive action / publishing / credentialed access / scope expansion / write-capable delegation / private external system use | issue complete / session end / scope change / host policy conflict / user revocation | none | proceed to reviewer gates |

#### Implementation Delegation Gate
| step | decision | required reason | delegated role | delegated scope | source of truth | allowed changes | forbidden changes | required verification | stop conditions | output required | observed result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01/S02 | approved-local-execution with parent exception | small shipped asset/test change with explicit issue plan and no disjoint worker needed | N/A | Codex adapter files and tests | issue requirement/design/plan | provider Codex adapters, dogfooding mirrors, managed asset tests, report | `.github/agents`, runtime validation, write-capable delegation, role registry | targeted tests, parity, validate/sync, review gates | reviewer fail or validation fail | report evidence and final reviewers | pass |

#### Delegated Worker Evidence
| step | delegated role | delegated worker summary | changed files | tests run or docs-only verification | reviewer verdict | unresolved risks | parent integration decision |
|---|---|---|---|---|---|---|---|
| S01/S02 | N/A | Parent implemented locally under the parent exception because the change was narrow, single-surface, and bounded by the active Issue plan. | provider adapters, dogfooding adapters, `tests/test_init_update.py`, report | targeted tests + validate/sync -> pass | passed | package inventory supplemental test blocked by missing pip, not issue-specific | accepted |

#### Parent Implementation Exception
| step | delegation unavailable/impossible reason | user approval / risk acceptance | allowed files | allowed operation | rollback plan | post-change verification | reviewer gate | unavailable / denied / host conflict / waiver handling |
|---|---|---|---|---|---|---|---|---|
| S01/S02 | No separate delegated worker was needed: write set was small, tightly coupled to report evidence, and already bounded by the active Issue's provider-first plan. | User authorized this Epic workflow and local implementation in this session; risk accepted only inside listed files and non-scope boundaries. | `src/spec_dock/assets/install_root/.codex/agents/system-architect.toml`; `src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml`; `.codex/agents/system-architect.toml`; `.codex/agents/implementation-planner.toml`; `tests/test_init_update.py`; active issue `report.md` | add/update Codex adapter assets, dogfooding mirrors, targeted tests, and report evidence | revert issue commit or restore the listed files to prior state | targeted issue117 content/parity test, issue71 parity, issue68 classification/tree, init structure, validate/sync, diff check | code-reviewer / qa-reviewer / spec-reviewer passed | parent exception recorded; no delegation denial or host conflict |

#### Reviewer Gate Status
| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| S01/S02 | final code review | code-reviewer | fresh | passed | N/A | proceed | No findings; no scope expansion into `.github/agents`, runtime validation, role registry, or write-capable delegation. |
| S99 | final QA | qa-reviewer | fresh | passed | N/A | proceed | Re-review passed; targeted test asserts content/parity and closure is `adapter_contract_only`. |
| S99 | final spec review | spec-reviewer | fresh | passed | N/A | proceed | Re-review passed after stale TOML parse evidence was removed and content/parity evidence matched the diff. |

#### Step Commit Gate
| step | closure state | commit scope | commit hash / final ledger | post-commit clean check | no-op rationale | no-op checked contracts / files | no-op diff-clean command | no-op read-only confirmation |
|---|---|---|---|---|---|---|---|---|
| S01/S02/S90/S99 | ready to commit | Codex delegated author adapters + tests + report | pending | pending | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `src/spec_dock/assets/install_root/.codex/agents/system-architect.toml` - provider Codex system architect adapter
- `src/spec_dock/assets/install_root/.codex/agents/implementation-planner.toml` - provider Codex implementation planner adapter
- `.codex/agents/system-architect.toml` - dogfooding mirror
- `.codex/agents/implementation-planner.toml` - dogfooding mirror
- `tests/test_init_update.py` - managed inventory and thin adapter boundary assertions
- `spec-dock/active/issue/report.md` - observed evidence ledger

#### コミット
- pending

#### メモ
- `rg --files | rg '[A-Z]'` returned only established uppercase paths such as `README.md`, `AGENTS.md`, `LICENSE`, and `SKILL.md`; no new uppercase path family was introduced beyond established Codex/skill conventions.

---

## Final Quality Gate (必須)

### S90 Docs Impact Resolution
| target | update required | owner | evidence | spec-reviewer result |
|---|---|---|---|---|
| provider Codex adapters / dogfooding mirrors / managed asset tests / report | yes | orchestrator | target files and tests updated; spec-reviewer P1 findings fixed | pass |

### Final QA Gate
| reviewer | scope | integration test decision | evidence | result |
|---|---|---|---|---|
| qa-reviewer | whole issue obligation coverage | added | issue117 targeted content/parity test, issue71 parity, issue68 inventory/classification, init structure, validate/sync, diff check | pass |

### Final Code Review Gate
| reviewer | scope | findings / fixes | re-review count | result |
|---|---|---|---|---|
| code-reviewer | issue-wide integrated diff | no findings | 0 | pass |

### Final Spec Review Gate
| reviewer | scope | findings / fixes | re-review count | result |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report / implementation / tests / docs alignment | prior P1 fixed: stale TOML parse evidence removed; content/parity evidence recorded | 3 | pass |

### Final Commit
| final report ledger | final commit scope | post-commit external evidence destination | result |
|---|---|---|---|
| current report | Codex delegated author adapters + tests + report | final response / eventual Epic PR | ready |

## 遭遇した問題と解決 (任意)
- 問題: `test_issue_69_full_install_root_inventory_is_packaged_in_wheel_sdist_and_installed_resources` が package assertion 前に失敗した。
  - 解決: `.venv/bin/python3` に `pip` が無い環境問題として report に記録し、必須 closure は targeted parity / init / validate evidence で閉じた。

## 学んだこと (任意)
- Codex adapter は role behavior を複製せず、role skill への thin wrapper として固定するほうが後続 issue の drift risk を小さくできる。

## 今後の推奨事項 (任意)
- 後続 issue で host adapter registry や Copilot parity を扱う場合も、この Issue の non-scope 境界を明示的に scope amendment してから進める。

## 省略/例外メモ (必須)
- Supplemental package inventory test `test_issue_69_full_install_root_inventory_is_packaged_in_wheel_sdist_and_installed_resources` was attempted and failed before package assertions because `.venv/bin/python3` has no `pip` module in this worktree environment. Required targeted parity and init/update-adjacent tests passed.
- Live Codex host invocation was not performed in this Issue. Closure classification is `adapter_contract_only`: the files are present, byte-mirrored, and covered by static content assertions, but downstream work must not infer verified live Codex host callability.
