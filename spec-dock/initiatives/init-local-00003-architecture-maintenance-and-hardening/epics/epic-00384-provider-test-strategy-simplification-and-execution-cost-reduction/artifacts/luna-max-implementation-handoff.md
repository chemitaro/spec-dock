---
種別: Implementation Handoff
対象: "GPT-5.6 Luna / reasoning Max"
Issue: "iss-00392"
最終更新: "2026-09-01"
正本:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "d18ca60b2a6ff11571ee366f71c4528dcd668d99"
---

# Luna Max Implementation Handoff

## 1. Instruction priority

1. Entry pointはIssue `plan.md`。
2. Behavior contractはIssue `requirement.md`。
3. Component/state/filesystem contractはIssue `design.md`。
4. Epic R/D/Pとaccepted ADRはboundary/governance。
5. Repository root `AGENTS.md`に従い、`src/spec_dock/`をsource of truth、`spec-dock/`をdogfoodとする。
6. Materialな追加設計判断をしない。stop matrixに該当したら実装を止め、exact evidenceをownerへ渡す。
7. PR merge、required-context変更、Issue closeはhuman-only。

## 2. Path ownership matrix

### Production — create

| Path | Owner step | Contract |
|---|---|---|
| `src/spec_dock/provider_lifecycle/__init__.py` | S10 | public exports only |
| `src/spec_dock/provider_lifecycle/model.py` | S10 | paths、states、record/marker/result |
| `src/spec_dock/provider_lifecycle/candidate.py` | S10 | source capture、digest、stage validation |
| `src/spec_dock/provider_lifecycle/filesystem.py` | S20 | lock、binding、native rename、record/root/slot/seed writes |
| `src/spec_dock/provider_lifecycle/legacy_023.py` | S10/S50 | exact single-version read-only recognizer |
| `src/spec_dock/provider_lifecycle/service.py` | S20-S50 | install/update/uninstall/resume/dispatch |
| `src/spec_dock/provider_lifecycle/public_result.py` | S40 | text/JSON/exit mapping |
| `src/spec_dock/context_pack.py` | S60 | surviving non-lifecycle extraction only |
| `src/spec_dock/assets/legacy_0_2_3.json` | S10 | whole-tree digests only |
| `scripts/provider_gate.py` | S70/S80 | build/artifact/node/budget evidence |

### Production — modify

| Path | Owner step | Allowed change |
|---|---|---|
| `src/spec_dock/cli.py` | S40/S60 | new service dispatch、old imports/helpers removal |
| `pyproject.toml` | S40/S60 | version 0.2.4、old marker/mypy cleanup |
| `scripts/static_analysis/run.sh` | S70 | include `scripts/provider_gate.py` |
| `Makefile` | S70 | thin `provider-test`/`provider-qualify` targets |
| `.github/workflows/provider-ci.yml` | S70 | final build-once topology |
| `README.md` | S40/S80 | final CLI/lifecycle guidance |
| provider/dogfood runtime uninstall wrapper pair | S40/S80 | default apply/aliases/trap help/forwarding |

### Delete only after successor proof

| Path | Earliest step | Successor authority |
|---|---|---|
| `src/spec_dock/managed_distribution.py` | S60 | provider_lifecycle package + context_pack extraction |
| `src/spec_dock/assets/managed_distribution.json` | S60 | fixed constants + legacy_0_2_3.json |
| `tests/unit/infra/test_managed_distribution.py` | S60 | new model/candidate/filesystem/service tests |
| `tests/unit/infra/test_init_update.py` | S60 | provider_assets + lifecycle tests |
| `tests/cli_runtime/test_distribution_cutover.py` | S60 | test_provider_lifecycle.py + artifact tests |
| `tests/integration/test_epic_00343_distribution.py` | S60 | test_provider_lifecycle_artifacts.py |
| `full-regression-ledger.json` | S60 | all failures pass/retired; no successor ledger |
| `tests/conftest.py` | S60 | ordinary pytest; no lane policy |
| `full-regression-timing-weights.json` | S70 | no sharding |
| `scripts/quality/full_regression_baseline.py` | S70 | no approved failure evaluator |
| `scripts/quality/verify_full_regression.py` | S70 | provider_gate canonical/qualify |
| `.github/workflows/provider-full-regression.yml` | S70 | PR provider-gate only |

### Tests — create/replace

```text
tests/unit/infra/test_provider_lifecycle_model.py
tests/unit/infra/test_provider_lifecycle_candidate.py
tests/unit/infra/test_provider_lifecycle_filesystem.py
tests/unit/infra/test_provider_lifecycle_service.py
tests/unit/infra/test_provider_lifecycle_public_result.py
tests/unit/infra/test_provider_lifecycle_faults.py
tests/unit/infra/test_provider_assets.py
tests/unit/infra/test_provider_gate.py
tests/cli_runtime/test_provider_lifecycle.py
tests/cli_runtime/test_uninstall.py
tests/cli_runtime/test_update.py
tests/integration/test_provider_lifecycle_artifacts.py
tests/integration/test_provider_lifecycle_tripwire.py
tests/platform/macos/test_provider_lifecycle_macos.py
tests/support/provider_lifecycle_tripwire/sitecustomize.py
tests/support/provider_lifecycle_tripwire/native_positive_control.py
tests/provider_test_ownership.json
```

### No-touch

```text
spec-dock/initiatives/**                       # except #392 report/generated lifecycle metadata
spec-dock/.gitignore                           # dogfood consumer seed
.github/workflows/ci.yml                       # dogfood consumer seed
src/spec_dock/assets/install_root/.github/workflows/ci.yml
.agents/skills/*                               # except exact two fixed slots
Issue #372 canonical/evidence
human review/merge settings                    # agent no write
release/tag/publication
```

## 3. Step graph and PR grouping

```text
S00
 |
 +-- PR-A: S10 -> S20 -> S30
 |          dormant successor, old public behavior
 |
 +-- PR-B: S40 -> S50 -> S60
 |          combined public cutover + old engine terminalization
 |
 +-- PR-C: S70 -> S80
            provider gate cutover + qualification/handoff
```

PR count is not mandatory。Do not split S40 public contract into bridge generations。

## 4. Fixed contract cheat sheet

### Paths

```text
Roots:
  spec-dock/docs
  spec-dock/templates
  spec-dock/system
  spec-dock/scripts

Slots:
  .agents/skills/spec-dock
  .agents/skills/spec-dock-grill-with-docs

Record:
  spec-dock/spec-dock.version

Slot marker:
  <slot>/.spec-dock-provider-slot.json

Fresh-only seeds:
  spec-dock/.gitignore
  .github/workflows/ci.yml
```

### Versions

- exact legacy: `0.2.3`
- final: `0.2.4`
- legacy marker bytes: `0.2.3\n`
- final marker: strict JSON record

### Order

```text
candidate validate
-> incomplete record
-> docs
-> templates
-> system
-> scripts
-> spec-dock skill
-> grill skill
-> fresh-only seed creation
-> ready record
-> cleanup
```

Uninstall uses same target order and publishes tooling-absent record last。

### Result/exit

```text
planned                    0
completed                  0
completed_with_warnings    0
blocked                    1
partial_failure            1
error                      2
```

### Permanent compatibility

- `init --force`: state-based install/update alias
- `--keep-specs`: default uninstall alias
- `--remove-specs`: code `spec-history-purge-removed`, mutation 0, exit 2
- uninstall default dry-run; `--apply` confirmation
- human merge only

## 5. Trace matrix

| Issue requirement | Primary design | Primary step |
|---|---|---|
| I392-RQ-001 | I392-D-018 / Epic D-019 | S00 |
| I392-RQ-002〜007 | I392-D-002〜010 | S10/S20 |
| I392-RQ-008 | I392-D-011〜012 | S20/S40 |
| I392-RQ-009〜010 | I392-D-009、012 | S30 |
| I392-RQ-011〜012 | I392-D-013 | S40 |
| I392-RQ-013 | I392-D-010〜013 | S30/S40 |
| I392-RQ-014 | I392-D-014 | S10/S50 |
| I392-RQ-015 | I392-D-017 | S50 |
| I392-RQ-016〜018 | I392-D-011、015 | S40 |
| I392-RQ-019 | I392-D-016〜017 | S60 |
| I392-RQ-020 | I392-D-018 | S70/S80 |

## 6. Command matrix

| Purpose | Before S60 policy removal | Final |
|---|---|---|
| model/service focused | `uv run pytest -q tests/unit/infra/test_provider_lifecycle_*.py` | same |
| CLI runtime focused | `uv run pytest --run-full-regression --full-regression-shard -q tests/cli_runtime/...` | `uv run pytest -q tests/cli_runtime/...` |
| integration focused | current full-regression flags | ordinary explicit file |
| static analysis | `make lint` | `make lint` |
| current full baseline | `uv run python -m scripts.quality.verify_full_regression --shards 4` | removed |
| final build | N/A | `uv run python scripts/provider_gate.py build ...` |
| final canonical | N/A | `uv run python scripts/provider_gate.py canonical ...` |
| macOS delta | N/A | `uv run python scripts/provider_gate.py macos-delta ...` |
| node ownership | N/A | `uv run python scripts/provider_gate.py verify-node-ownership ...` |
| qualification | N/A | `uv run python scripts/provider_gate.py qualify --runs 20 --budget-runs 5 ...` |
| dogfood | `python3 ./spec-dock/scripts/spec-dock validate` | sync then validate |

## 7. Fault injection matrix

Minimum fault IDs:

```text
install.after-incomplete-record
install.after-docs
install.after-templates
install.after-system
install.after-scripts
install.after-slot-spec-dock
install.after-slot-grill
install.before-ready-record
install.after-ready-before-cleanup

update.after-incomplete-record
update.after-docs
update.after-templates
update.after-system
update.after-scripts
update.after-slot-spec-dock
update.after-slot-grill
update.before-ready-record
update.after-ready-before-cleanup

uninstall.after-incomplete-record
uninstall.after-docs
uninstall.after-templates
uninstall.after-system
uninstall.after-scripts
uninstall.after-slot-spec-dock
uninstall.after-slot-grill
uninstall.before-tooling-absent-record
uninstall.after-tooling-absent-before-cleanup
```

For every pre-final-record fault:

- first result `partial_failure`
- record state incomplete/operation exact
- protected digest unchanged
- same operation/same candidate rerun completes
- cross-intent/candidate blocks

For after-final-record cleanup fault:

- desired state valid
- result `completed_with_warnings`
- exit 0
- retry not required for product convergence

## 8. Active failure terminalization algorithm

Input is post-#387 active rows only。For each row:

1. Record exact node ID、failure signature、current requirement。
2. Run node alone against final code。
3. Choose mechanically:
   - **fix**: accepted current requirement remains; make node pass。
   - **successor**: new node has same requirement trace and representative failure; delete old duplicate。
   - **retirement**: #387 or accepted hard-cutover explicitly removes requirement; delete node and cite trace。
4. Any row not fitting one category is stop。
5. Final verifier requires ledger absent and all canonical nodes pass。

No `approved-no-op`、xfail、retry、policy skip。

## 9. Required-context human operation

The agent prepares, but does not execute:

1. before-state JSON/read output
2. new gate workflow run GREEN
3. intentional RED canary commit/instruction
4. proof merge blocked
5. canary removal and GREEN
6. exact new required context name
7. list of old provider-only contexts to remove
8. unrelated contexts/review requirement diff expected empty
9. restoration command/instruction
10. operator sign-off slot in report

Current authoring observation: repository rulesets collection was empty。Classic protection/effective required contexts must be read again at transition; unreadable state is hard stop, not owner decision delegation。

## 10. Stop / escalation matrix

| Condition | Immediate action | Owner |
|---|---|---|
| #387 drift outside allowlist | no code change | Product/repository owner |
| final version cannot be 0.2.4 | stop before cutover | Product owner |
| fixed paths insufficient | no allowlist expansion | Product owner |
| atomic native primitive missing | fail closed | filesystem safety reviewer |
| candidate needs symlink/special/hard link | reject candidate | Product owner |
| record needs progress/checkpoint/path list | stop; no schema expansion | Product owner |
| old package mutation event >0 | merge forbidden; adjust record/marker | Product + safety reviewer |
| positive control not intercepted | test infrastructure failure | safety reviewer |
| active failure not terminalizable | no ledger/skip | Product owner |
| duplicate owner remains | no merge | test architecture owner |
| build count !=1 / hash mismatch | no merge | CI owner |
| budget/CPU/fault/flake fail | forward-fix same Issue | implementation owner |
| required setting unreadable | no setting mutation | human repository admin |
| intentional RED does not block | restore before-state | human repository admin |
| seed/protected data changed | destructive stop | Product owner |
| PR head changes after evidence | discard evidence and rerun | implementation owner |

## 11. Report structure

`report.md` must contain:

1. Verified repository/branch/authoring SHA
2. #387 admission and POST_387_SHA
3. Step completion table S00〜S80
4. RED/GREEN evidence per step
5. Path ownership/mutation audit
6. State/command/result matrix
7. Fault/convergence matrix
8. Legacy migration matrix
9. Old-package tripwire/native controls
10. Active failure terminalization table
11. Test ownership/node inventory/duplicate result
12. Artifact manifest/build count
13. Linux/macOS lane evidence
14. Five-run/CPU/fault/rolling-20
15. Provider/dogfood/seed/fresh consumer evidence
16. Required contexts before/after and human operator
17. Final PR head/hashes/tree status
18. Stop events/cleanup
19. Post-merge tree equality
20. Remaining owner decisions: zero

## 12. Definition of done

Implementation is done only when all step invariants and I392-RQ-001〜020 are verified on one final PR head and one candidate manifest。It is not merged until human merge。Issue is not finished until post-merge tree equality and report completion。Epic is not closed until #392 finish。
