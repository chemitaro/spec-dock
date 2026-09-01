---
種別: 要件定義書（Issue）
ID: "iss-00392"
タイトル: "Provider Lifecycle And Regression Gate Hard Cutover"
関連GitHub: ["#392"]
状態: "draft"
最終更新: "2026-09-01"
依存: ["iss-00387", "../../requirement.md", "../../design.md", "../../artifacts/20260831t152024z-adr-single-implementation-unit-and-provider-hard-cutover-policy.md"]
親: ["epic-00384", "init-local-00003"]
正本検証:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "ef183ae46febe52f0152431cb3a8b4846c9972fc"
---

# iss-00392 Provider Lifecycle And Regression Gate Hard Cutover — 要件定義

Normative artifacts: `artifacts/provider-lifecycle-wire-contract.md` and `artifacts/active-failure-disposition-register.md` (Issue documents use `../../artifacts/...`). Their exact wire/disposition data is not delegated to implementation.


## 1. Objective and acceptance unit

本IssueはEpic #384の唯一のimplementation-and-verification unit。4 roots、2 slots、strict record/seed policy、safe shared-container bootstrap、exact `0.2.3` migration、tooling-only uninstall、public compatibility、old contract removal、test terminalization、build-once gate、stable Linux qualification、non-cyclic closure evidenceを一つのacceptanceとして完成させる。

## 2. Numbered end-to-end contract

### I392-RQ-001 — Specification freeze and #387 admission

Implementation前にrepository evidence SHA、replacement manifest hashes、owner-recorded `SPEC_FREEZE_COMMIT`、#387 PR base/head/merge tree、implementation baseを固定する。Spec blobs mustmatchmanifest andbeancestor。#387 delta isverified fromits own graph。Repository evidence SHAからimplementation baseへのblanket diffは禁止。

### I392-RQ-002 — Exact persistent paths

Persistent authorityは4 roots、2 slots、recordのみ。Fresh `init` + absent時だけshared `spec-dock` bootstrap、two seeds、second seed exact `.github/workflows` parent creationを許可。Shared containerにはreplace/delete authorityなし。

### I392-RQ-003 — Protected data

Initiatives/artifacts/workbench/generated state outsidefixed roots、unknown paths、unrelated skills、consumer seeds、shared container unknown childrenをbyte/type/mode/link-target identicalに保つ。

### I392-RQ-004 — Final version and strict record

Final version `0.2.4`。Record exact seven keys: `schema_version,state,operation,version,candidate_digest,seed_policy,skill_slots`。Strict relations、duplicate/unknown/missing/type/size/UTF-8/link-count validation。

### I392-RQ-005 — Immutable seed-policy resume discriminator

Allowed `create-if-absent|preserve-only`。Fresh init onnever-installed absent onlycreate; update-on-absent、reinstall、legacy migration、update、uninstall preserve。One operation keepspolicy fromincomplete throughterminal。Resume requiresoperation/candidate/policy exact acrossrequest/stage/record。No seed-state inference。Tooling-absent alwayspreserve-only。

### I392-RQ-006 — Slot authority

New slot requiresmatching `.spec-dock-provider-slot.json`。Markerless onlyexact legacy recognizer。Foreign/invalid/modified/symlink block pre-mutation。

### I392-RQ-007 — Candidate

Code-fixed 4 roots/2 slots。Canonical version/path/kind/mode/content digest。Seed/record/generated marker excluded。Symlink/special/hard link/traversal reject。Source/stage digest exact。

### I392-RQ-008 — Fresh classification and shared-container bootstrap

Fresh requiresrecord/root/slots absent andcontainer absent orreal dir。Unknown non-target children allowed。Absent container iscreated onlyafterstage/preflight viaexclusive `mkdirat` andno-follow bind。Created identity stored instage owner before record。Pre-record failure exact empty cleanup; otherwisepartial/same tuple resume。Existing container nevercleanup。

### I392-RQ-009 — Classification

States `absent|legacy-0.2.3|ready|incomplete|tooling-absent-preserved-data|blocked`。Read-only evaluation ofrecord/container/binding/slot/candidate/stage/legacy recovery。Invalid JSON doesnotfall backtolegacy。

### I392-RQ-010 — Install semantics

Fresh init create policy; update-on-absent/reinstall/migration preserve policy。Stage/validate beforetarget mutation。Bootstrap/bind、incomplete record、roots、slots、authorized seeds、ready record、cleanup。

### I392-RQ-011 — Update semantics

Ready roots/slots converge whole-root。Missing repair。Marker mismatch block。Seeds/protected/container unknown children untouched。Update policy preserve-only。

### I392-RQ-012 — Atomic replacement

Absent publish/detach native no-replace、existing valid replace native exchange。Linux renameat2/macOS renameatx_np。Root lock、descriptor parents、same filesystem。No generic fallback。

### I392-RQ-013 — Tooling-only uninstall

Default dry-run、apply confirmation。Valid roots/slots onlyremove。Container/user data/unknown/skills/seeds untouched。Incomplete/final preserve-only。Final tooling-absent record retained。

### I392-RQ-014 — Reinstall discriminator

Record absent vs tooling-absent durable distinction。Tooling-absent requiresroots/slots absent。Reinstall preserve-only andneverrecreates seeds。

### I392-RQ-015 — External convergence

Partial failure resume onlyexact `(operation,candidate_digest,seed_policy)` andvalid stage/container identity。Matching target no-op、owned mismatch repair。Cross tuple block。No rollback/progress list/old fallback。

### I392-RQ-016 — Exact `0.2.3` migration

Post-#387 baseline wheel providesplain marker、4 root、2 slot digests。All roots exact、slot absent/exact。Active recovery blocks。Migration/uninstall preserve-only。Fault evidence records policy。

### I392-RQ-017 — Old package mutation-zero

Final ready/tooling-absent workspaces + old commands matrix undercomposite tripwire。Events0、refusal exit、tree unchanged。Python/native positive controls precall capture。

### I392-RQ-018 — Public CLI and purge removal

Grammar preserved。Init-force state alias。Uninstall apply withoutspec mode。Keep alias。Remove-specs trap beforefilesystem observation、error code、mutation0、exit2。Existing success/wrapper/main JSON fields retained。Purge service/intent/journal/tests deleted。

### I392-RQ-019 — Typed result

Statuses/exits fixed: planned/completed/completed_with_warnings=0、blocked/partial=1、error=2。Additive JSON fields `code,seed_policy,mutation_started,bootstrap_rolled_back`。Actions fixed-set only。

### I392-RQ-020 — Test portfolio and PR-B transitional gate continuity

Pure/filesystem/CLI/artifact/macOS ownershipをuniqueにし、all active failure rowsをterminalizeしてPR-B merge時点でactive approved failures 0とする。S60 exact owned pathsには`.github/workflows/provider-ci.yml`と`tests/unit/test_provider_test_lanes.py`を含める。

S60 `provider-ci.yml`はcurrent workflow name/event/job IDs/matrix/setupを維持し、次だけをbehavior-preservingに変更する。

- `tests/unit/infra/test_managed_distribution.py` -> existing provider lifecycle model/candidate/filesystem/service/public-result/fault/assets/ownership unit tests。
- `tests/cli_runtime/test_distribution_cutover.py` -> `test_provider_lifecycle.py`、`test_uninstall.py`、`test_update.py` with current full-regression permission flags。
- `tests/integration/test_epic_00343_distribution.py` -> `test_provider_lifecycle_artifacts.py`、`test_provider_lifecycle_tripwire.py` with current permission flags。
- macOS matrix additionally runs `tests/platform/macos/test_provider_lifecycle_macos.py` only on macOS。

`tests/unit/test_provider_test_lanes.py` must assert ledger active rows `[]`、all 15 remaining rows `resolved` under current evaluator、fixed-in-place node or exact superseding successor is collected、rows 4〜15 remain absent after #387、deleted test path references are absent、workflow successor paths exist、and pytest/standalone adapters agree。The exact relation comes from `active-failure-disposition-register.md`; no generated synthetic or implementation-selected successor is permitted。S60 retains `tests/unit/test_full_regression_baseline.py` and all current policy providers。Ordinary suite、workflow-equivalent successor commands、current 4-shard verifier must all GREEN。No `scripts/provider_gate.py` dependency。

### I392-RQ-021 — Consumer-first atomic PR-C gate transition

S70 same branch adds replacement tooling/workflow/environment/AGENTS and final replacement tests before old removal。Before deleting `tests/conftest.py`、`scripts/quality/full_regression_baseline.py`、`scripts/quality/verify_full_regression.py`, it must retire or replace every remaining consumer, explicitly including `tests/unit/test_provider_test_lanes.py` and `tests/unit/test_full_regression_baseline.py`。The transitional `.github/workflows/provider-ci.yml` is rewritten to final provider-gate topology rather than deleted。

An exact pre/post inventory must prove zero imports/references to old policy modules、pytest options、ledger/timing paths in runtime/CI/tests/operator guidance, excluding Historical `spec-dock/initiatives/**`。After consumer 0, delete providers、old main-push workflow、ledger/timing/sharder/conftest/markers。Run final import absence、collection、workflow command and provider-gate tests。S70 not mergeable; S80 after qualification/context/attestation only merge。Main never broken and PR-C final gate GREEN is independent of PR-B current-gate GREEN。

### I392-RQ-022 — Build-once and platform ownership

One build invocation wheel+sdist。Linux/macOS same wheel。Linux one pytest/worker1、macOS delta only、sdist Linux smoke。Hash/source mismatch fail。

### I392-RQ-023 — Stable Linux qualification environment

ID `specdock-linux-qualification-v1`。Tracked descriptor hash、pinned base digest、runner label、x86_64、2 CPU、8GiB、Python/uv/lock、observed fingerprint。Any run mismatch invalidatesseries。First5 <=600s andCPU/wall <=1.1; all20 flake0/retry0;fault detection100%。

### I392-RQ-024 — Required-context transition

Old required retained whilenew added required/read-back。Dedicated non-merge canary new gate RED/block。Canary close、implementation GREEN後only old provider context remove。Unrelated/review unchanged。Unreadable -> no mutation。

### I392-RQ-025 — Tracked report and external attestations

Tracked report committed beforehead freeze andcontainsnoown hash/final head/final source-bound hash/post-merge fact。Afterfreeze build/qualification -> canonical content-addressed pre-merge external attestation。Human merge -> tree OID equality -> post-merge closure attestation。No tracked writeback。

### I392-RQ-026 — Root AGENTS and closure

PR-C updatesroot AGENTS tofinal commands/policy、removesretired guidance、preserveshuman-only merge/human-admin settings。Tree equality iscommit tree objects。Issue finish/Epic close external closure evidence afterhuman merge。No newIssue。

### I392-RQ-027 — PR-B lifecycle documentation ownership

S40/S60 exact owned paths are `README.md` lifecycle sections、`src/spec_dock/assets/spec_dock/docs/migration.md`、`src/spec_dock/assets/spec_dock/docs/README.md`、`spec-dock/docs/migration.md`、`spec-dock/docs/README.md`。Provider source first、projection byte parity。PR-B merge時点でlegacy journal/retry、purge authority、same-compatible-newer、empty-boundary guidanceを除き、strict record、same operation/candidate/seed policy resume、tooling-only uninstall、preserve-only update/reinstall/migrationへ同期する。Root README/AGENTS/docs README test-policy textはS70。S80 content edits禁止。

### I392-RQ-028 — Exact wire contract

`../../artifacts/provider-lifecycle-wire-contract.md`のseven-key record、observed-only state、operation wire、resume/terminal relation、slot marker、service/public result field、status/code/action enum、nullability、text/JSON/exit goldenをexactに実装する。`tests/unit/infra/test_provider_lifecycle_wire_contract.py`がnormative valuesを検証し、unknown enum/default mappingをrejectする。

### I392-RQ-029 — Exact failure disposition register

`../../artifacts/active-failure-disposition-register.md`の27 row registerをS00とS60のauthorityにする。S00でsource ledgerとpost-#387 expected deltaを照合し、expected 12-row removal以外のnew/missing/signature/successor changeはS10前に停止する。S60でremaining 15 rowsをregisterどおりall resolved、active 0へ変更する。Lunaはfix/successor/retirementを再選択しない。

### I392-RQ-030 — CI-only frozen-head artifact production

Final frozen PR headのpackaging producerはLinux `provider-build-artifacts` job exactly one。One invocationでwheel/sdist/manifestを生成し`provider-candidate-<sha>`としてimmutable upload。`provider-linux-canonical`、`provider-sdist-smoke`、`provider-macos-delta`、`provider-attestation`はsame run artifactをdownload/hash-verifyし、build invocation count 0。S70 local buildはpre-freeze non-authoritative smoke。S80はworkflow dispatch/wait/download/verifyだけでlocal final buildなし。

## 3. Command/state/seed-policy matrix

| State | Invocation | Operation | Policy |
|---|---|---|---|
| absent | init / init --force | install | create-if-absent |
| absent | update | install | preserve-only |
| legacy | init-force/update | migrate | preserve-only |
| legacy | uninstall | uninstall | preserve-only |
| ready | init-force/update | update | preserve-only |
| ready | uninstall | uninstall | preserve-only |
| incomplete | exact tuple | resume | recorded exact |
| incomplete | mismatched tuple | blocked | N/A |
| tooling-absent | init/init-force/update | reinstall | preserve-only |
| tooling-absent | uninstall | idempotent | preserve-only |
| any | uninstall --remove-specs | error trap | no target observation |

## 4. Merge and closure distinction

- S30/PR-A merge ready: dormant successor only。
- S60/PR-B merge ready: complete lifecycle、legacy proof、old engine removed、active failures0、current gate intact。
- S80/PR-C merge ready: final gate/environment/AGENTS、old machinery removed、qualification/context/attestation。
- PR merged: human fact。
- Issue finished: merge tree equality + external closure + SpecDock finish。
- Epic closed: #392 finished + external Epic close evidence。
