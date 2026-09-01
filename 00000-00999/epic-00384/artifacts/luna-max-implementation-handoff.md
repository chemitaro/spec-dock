---
種別: Implementation Handoff
対象: "GPT-5.6 Luna / reasoning Max"
Issue: "iss-00392"
最終更新: "2026-09-01"
repository_evidence:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "e47c1356892857e61388c7aefb2539d2061d1b9c"
---

# Luna Max Implementation Handoff

## 1. Instruction priority

1. Entry point: Issue `plan.md`。
2. Behavior: Issue `requirement.md`。
3. Components/state/filesystem: Issue `design.md`。
4. Boundary/governance: Epic R/D/P and accepted ADR。
5. Repository root `AGENTS.md` current text applies until PR-C; final AGENTS changes are owned by S70 and must match the final contract。
6. No material Product/architecture/security/migration/CI/evidence decision by implementer。
7. Stop matrix is mandatory。
8. Agent never merges or changes required settings。

## 2. PR graph

```text
S00
 |
 +-- PR-A
 |    S10 internal
 |      -> S20 internal
 |      -> S30 ONLY PR-A main merge gate
 |    main result: old public product + dormant successor
 |
 +-- PR-B, one branch/one PR
 |    S40 internal, NO main merge
 |      -> S50 internal, NO main merge
 |      -> S60 ONLY PR-B main merge gate
 |    main result: complete final lifecycle + current gate intact
 |
 +-- PR-C, one branch/one PR
      S70 internal, NO main merge
        replacement gate/environment/AGENTS added
        old policy/workflow removed in same branch
        -> S80 ONLY PR-C main merge gate
      main result: final provider gate
```

Never offer S40/S50/S70-only merge handoff。

## 3. Path ownership matrix

### S10-S30 create

```text
src/spec_dock/provider_lifecycle/**
src/spec_dock/assets/legacy_0_2_3.json
tests/unit/infra/test_provider_lifecycle_model.py
tests/unit/infra/test_provider_lifecycle_candidate.py
tests/unit/infra/test_provider_lifecycle_filesystem.py
tests/unit/infra/test_provider_lifecycle_service.py
tests/unit/infra/test_provider_lifecycle_faults.py
tests/unit/infra/test_provider_assets.py
```

### S40-S60 modify/create/delete

```text
pyproject.toml
src/spec_dock/cli.py
src/spec_dock/context_pack.py
src/spec_dock/provider_lifecycle/**
provider/dogfood runtime uninstall wrapper pair
README.md
tests/unit/infra/test_provider_lifecycle_public_result.py
tests/unit/infra/test_provider_test_ownership.py
tests/cli_runtime/test_provider_lifecycle.py
tests/cli_runtime/test_uninstall.py
tests/cli_runtime/test_update.py
tests/integration/test_provider_lifecycle_artifacts.py
tests/integration/test_provider_lifecycle_tripwire.py
tests/platform/macos/test_provider_lifecycle_macos.py
tests/support/provider_lifecycle_tripwire/**
tests/provider_test_ownership.json
```

S60 delete old engine/tests only。S60 retain current policy consumers:

```text
tests/conftest.py
full-regression-ledger.json        # update to zero active
full-regression-timing-weights.json
scripts/quality/**
.github/workflows/provider-full-regression.yml
```

### S70-S80 PR-C ownership

Create/update:

```text
scripts/provider_gate.py
ci/linux-qualification.Dockerfile
ci/linux-qualification-environment.json
tests/unit/infra/test_provider_gate.py
scripts/static_analysis/run.sh
Makefile
.github/workflows/provider-ci.yml
AGENTS.md
README.md
provider/dogfood final pairs
#392 report.md pre-merge content
```

Delete in S70 same branch:

```text
.github/workflows/provider-full-regression.yml
tests/conftest.py
full-regression-ledger.json
full-regression-timing-weights.json
scripts/quality/full_regression_baseline.py
scripts/quality/verify_full_regression.py
scripts/quality/__init__.py if empty
fast/full marker policy
```

### No-touch

```text
spec-dock/initiatives/** except #392 report/generated lifecycle metadata
spec-dock/.gitignore
.github/workflows/ci.yml
src/spec_dock/assets/install_root/.github/workflows/ci.yml
unrelated .agents/skills/*
Issue #372 canonical/evidence
human settings/merge
release/tag/PyPI
```

## 4. Fixed path and record cheat sheet

```text
Shared container (bootstrap create only):
  spec-dock

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

Record exact keys:

```text
schema_version
state
operation
version
candidate_digest
seed_policy
skill_slots
```

Seed policies:

```text
create-if-absent:
  init/init --force on never-installed absent only

preserve-only:
  update on absent
  reinstall
  legacy migration
  update
  uninstall
```

Resume identity is exact `(operation, candidate_digest, seed_policy)` across record、stage owner、request。Never infer from seed presence。

## 5. Fresh container algorithm

```text
classify absent/real container
-> stage candidate and strict owner
-> capture root + absence/binding
-> if absent: mkdirat exclusive
-> openat O_NOFOLLOW|O_DIRECTORY
-> verify visible/held identity
-> fsync parent
-> persist created identity in stage owner
-> publish incomplete record
```

Pre-record failure:

- exact empty created dir -> descriptor-safe rmdir cleanup
- otherwise partial failure + stage-owner-bound same resume
- existing container never cleanup
- uninstall never delete container

## 6. Operation order

```text
candidate validate
-> bootstrap/bind container
-> incomplete record (seed policy fixed)
-> docs
-> templates
-> system
-> scripts
-> spec-dock skill
-> grill skill
-> create seeds only when policy=create-if-absent
-> ready record with same policy
-> cleanup
```

Uninstall uses preserve-only、detaches 4 roots/2 slots、publishes tooling-absent last。

## 7. Fault matrix additions

In addition to every root/slot/final boundary:

```text
install.after-stage-owner
install.after-container-mkdir
install.after-container-owner-update
install.before-incomplete-record
install.after-seed-spec-dock-gitignore
install.after-seed-consumer-ci
```

Every evidence row includes operation/candidate/seed policy。Fresh create policy resumes seed creation; all preserve policy paths never create seeds。Policy mismatch is pre-mutation blocked。

## 8. S60/S70 continuity checklist

### S60 must be true

- old engine/tests removed
- active approved failure 0
- ownership map self-contained verifier GREEN
- `scripts/provider_gate.py` not required
- `tests/conftest.py` present
- ledger/timing/quality scripts present
- `provider-full-regression.yml` present and GREEN
- no workflow missing consumer
- PR-B merge-ready only after S60

### S70/S80 must be true

- provider gate + environment + workflow + AGENTS added before old removal
- old policy/workflow deleted in same PR-C branch
- S70 not mergeable
- S80 qualification/context/attestation complete
- PR-C merge-ready only after S80

## 9. Specification admission

Do not use `e47c1356892857e61388c7aefb2539d2061d1b9c..POST_387_SHA` as one allowlist diff。

Use:

1. manifest hashes -> exact repo spec paths
2. owner-recorded `SPEC_FREEZE_COMMIT`
3. #387 own base/head/merge tree delta
4. implementation base containing both
5. protected drift check from spec freeze with validated #387 delta accounted

Any missing identity is stop。

## 10. Linux environment

Stable ID:

```text
specdock-linux-qualification-v1
```

Tracked descriptor/Dockerfile required。Descriptor pins base digest、runner label、arch、2 CPU、8 GiB、Python series、uv exact、lock hash。Observed fingerprint must match all 20 runs。Mismatch invalidates whole series; never combine metrics。

## 11. Required-context human operation

```text
capture before
-> new gate GREEN, old required
-> add new required, keep old
-> read back both
-> dedicated non-merge canary new gate RED
-> prove blocked
-> close canary, implementation GREEN
-> remove old provider-only
-> read back final
```

No old removal before RED proof。

## 12. Evidence graph

Tracked report:

- method、implementation summaries、terminalization、external schema/location
- no own hash
- no final head/tree
- no final source-bound artifact hashes
- no post-merge facts

After report commit/head freeze:

- build/qualify exact head
- `pre-merge-attestation-v1` external content-addressed
- human merge
- compare PR head tree OID to merge commit tree OID
- `post-merge-closure-v1` external
- SpecDock finish/GitHub close
- `epic-closure-v1` external

Never edit tracked report after head freeze to insert these facts。

## 13. Final AGENTS contract

S70 owns root `AGENTS.md`。Final must contain:

- provider-first/dogfood
- `make lint`
- `make provider-test`
- `make provider-qualify`
- direct `scripts/provider_gate.py` commands
- one pytest process/worker 1
- macOS delta/same wheel
- no ledger/skip/shard/main-push Full Regression
- human-only merge
- human-admin required setting transition

## 14. Command matrix

| Phase | Canonical command |
|---|---|
| S00-S60 ordinary | `uv run pytest -q` |
| S00-S60 current full | `uv run python -m scripts.quality.verify_full_regression --shards 4` |
| S60 ownership | `uv run pytest -q tests/unit/infra/test_provider_test_ownership.py` |
| S70 build | `uv run python scripts/provider_gate.py build ...` |
| S70 environment | `uv run python scripts/provider_gate.py verify-environment ...` |
| S70 ownership | `uv run python scripts/provider_gate.py verify-node-ownership ...` |
| S80 canonical | `make provider-test` |
| S80 qualification | `make provider-qualify` / `provider_gate.py qualify` |
| macOS | `provider_gate.py macos-delta` |
| dogfood | `spec-dock sync` then `validate` |

## 15. Stop/escalation matrix

| Condition | Action | Owner |
|---|---|---|
| spec hash/commit missing | no implementation | Product/repository owner |
| #387 delta mismatch | no implementation | Product/repository owner |
| fixed path insufficient | no allowlist expansion | Product owner |
| seed policy missing/mismatch | block before mutation | Product owner |
| fresh container cannot be bound/cleaned | fail closed/partial | filesystem safety reviewer |
| native primitive missing | fail closed | safety reviewer |
| S40/S50 offered for merge | block handoff; continue S60 | implementation owner + human merger |
| S60 references provider_gate | block PR-B | implementation owner |
| S60 removes current workflow consumer | restore consumer; block PR-B | test/CI owner |
| active failure not terminalized | no ledger approval | Product owner |
| S70 old removal before replacement | block PR-C | CI owner |
| S70 offered for merge | block; continue S80 | implementation owner + human merger |
| environment mismatch | invalidate series | CI owner |
| build count/hash mismatch | no merge | CI owner |
| new context not required before RED | stop transition | human admin |
| RED not blocking | restore before-state | human admin |
| tracked report self-reference/post-merge write | remove cycle; new head/evidence | implementation owner |
| PR head changes after attestation | discard/rerun all source-bound evidence | implementation owner |
| merge commit tree mismatch | do not finish Issue | human merger/Product owner |
| AGENTS stale | block PR-C | Product/CI owner |
| seed/protected data changed | destructive stop | Product owner |

## 16. Report contract

Tracked `report.md` contains:

1. repository evidence、manifest、SPEC_FREEZE_COMMIT、#387 admission
2. step RED/GREEN summaries
3. path ownership/mutation audit
4. record/seed policy/state matrix
5. bootstrap/fault/convergence evidence summaries
6. legacy/old-package evidence methodology
7. active failure terminalization
8. test ownership and gate continuity
9. external attestation schemas and target GitHub locations
10. remaining owner decisions: zero

It does not contain its own hash、final head/tree、final source-bound artifact hashes、merge result、Issue/Epic close result。

## 17. Owner decisions

Machine-readable owner decision list in replacement manifest is `[]`。No open decision remains。Dynamic evidence mismatch triggers stop; it does not delegate a choice to Luna。
