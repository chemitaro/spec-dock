---
種別: ADR
ID: "20260831t152024z-adr"
タイトル: "Single Implementation Unit and Provider Hard Cutover Policy"
状態: "accepted"
決定日: "2026-08-31"
最終更新: "2026-09-01"
対象: ["epic-00384", "iss-00392"]
正本検証:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "b094771e089c1f31618116e84be32fcf78704409"
---

# ADR: Single Implementation Unit and Provider Hard Cutover Policy

## Context

Epic #384はdistribution lifecycle、legacy migration、public CLI、test portfolio、artifact build、provider CIを同時に変更する。Current repository evidence `b094771e089c1f31618116e84be32fcf78704409`ではlegacy per-file engine、purge、journal、failure ledger、timing sharder、main-push Full Regression、stale operator guidanceが実在する。Issue #387は別のCurrent-surface cleanupであり、これらのProduct semanticsを変更しない。

Strict reviewにより、main merge boundary、temporary policy consumers、resume seed intent、fresh container bootstrap、specification admission、evidence self-reference、required-context order、qualification environment、root operator guidanceをcross-documentで一意にする必要が確認された。

## Decision

### ADR-D1 — One implementation-and-verification Issue

Epic #384の唯一のimplementation-and-verification Issueを#392とする。Investigation、Product decision、tests、CI transition、final verificationを別Issueへ分割しない。Internal step、commit、PR、canary PRは全て#392の内部手段。

### ADR-D2 — Combined hard cutover and exact main gates

Public routeはoldまたはcomplete final lifecycleのどちらか。PR-AはS30後だけmerge、PR-BはS40/S50 internalかつS60後だけmerge、PR-CはS70 internalかつS80後だけmerge。S40/S50/S70単独merge、uninstall-first bridge、runtime toggle、dual writer、automatic old fallbackを禁止する。

### ADR-D3 — Fixed lifecycle and immutable seed policy

Persistent tooling authorityは4 roots、2 slots、`spec-dock/spec-dock.version`。Fresh `init`だけ2 seedsをabsent時に作成。Strict recordへ`seed_policy`を追加し、`(operation,candidate_digest,seed_policy)`をresume identityとする。Create-if-absentはnever-installed absentへのfresh initだけ。Update-on-absent、reinstall、legacy migration、update、uninstallはpreserve-only。Seed presenceからpolicyを推測しない。

### ADR-D4 — Safe shared-container bootstrap

`spec-dock`はshared containerでwhole-directory ownership/delete authorityを持たない。Fresh absent時だけcandidate stage/preflight後にdescriptor-bound `mkdirat`、no-follow open、identity captureを行う。Record前failureではexact empty identityだけcleanup。Cleanup不能はstage-owner-bound partial failure。Uninstallはcontainerを削除しない。

### ADR-D5 — Exact legacy boundary

Exact clean `0.2.3`だけをsingle-version root/slot digest fixtureで認識する。Active recovery、unsupported legacy、modified/foreign markerless slotは推測変換しない。Final versionは`0.2.4`、migration seed policyはpreserve-only。

### ADR-D6 — No broken gate merge state and consumer-complete deletion

PR-B/S60はold engine/testsを削除しactive failuresをterminalizeする。同じS60で`.github/workflows/provider-ci.yml`をowned pathとして、削除する`test_managed_distribution.py`、`test_distribution_cutover.py`、`test_epic_00343_distribution.py`への参照だけを、S10〜S50で成立したsuccessor unit/CLI/artifact/macOS testsへbehavior-preservingにretargetする。Workflow name、event、job IDs、matrix、setupを維持し、S70のfinal provider-gate redesignを前倒ししない。

S60は`tests/unit/test_provider_test_lanes.py`も更新し、current policy下でzero active ledger、all terminal entries、successor collection、workflow path existenceを検証する。`tests/unit/test_full_regression_baseline.py`、`tests/conftest.py`、ledger、timing、quality scripts、main-push workflowはworking consumer graphとしてS70まで保持する。S60はS70-only provider gate toolへ依存しない。PR-B merge evidenceはcurrent PR workflow GREENとcurrent main-push verifier GREENを別々に含む。

PR-C/S70はreplacement gate/environment/workflow/AGENTS/final testsを同一branchへ先に追加する。次に`tests/unit/test_provider_test_lanes.py`と`tests/unit/test_full_regression_baseline.py`を含む全remaining policy-module consumersをretireまたはfinal testsへ置換し、consumer 0を証明してからpolicy providers、ledger、timing、old workflowを削除する。S70単独mergeは禁止し、S80後のPR-C final gate GREENを独立に証明する。

### ADR-D7 — Build-once and stable Linux environment

One packaging invocationでwheel/sdist。Linux/macOS same wheel。Linux environment ID `specdock-linux-qualification-v1`をtracked descriptor、pinned base digest、2 CPU、8 GiB、architecture、Python/uv/lock、observed fingerprintへ束縛する。20-run中mismatchは全series invalid。

### ADR-D8 — Deterministic specification admission

Repository evidence SHAはresearch provenance。本pack manifest hashesをexact canonical/support blobsへ照合し、owner-recorded `SPEC_FREEZE_COMMIT`を固定する。#387 driftは#387 own PR/merge graphから検証し、stale repository evidence SHAからfuture main tipへのblanket diffを使わない。

### ADR-D9 — Non-cyclic evidence and tree equality

Tracked reportはpre-merge contentだけを持ち、own hash/final head/post-merge factsを含めない。Final head固定後のbuild/qualificationはcontent-addressed external pre-merge attestation。Human merge後はverified PR head tree OIDとmerge commit tree OIDを比較。SpecDock finish/Issue/Epic closeはexternal closure attestationsで、tracked reportへwritebackしない。

### ADR-D10 — No-gap required-context transition

Old requiredを保持したままnew contextをrequiredへ追加/read-backし、その後dedicated non-merge canary REDでblockingを証明する。Canary close、implementation GREEN後だけold provider-only contextを除去。Unrelated contextsとhuman review requirementを維持。

### ADR-D11 — Root operator guidance is part of cutover

Root `AGENTS.md`はPR-Cでfinal provider-gate commands、single-process policy、no ledger/skip/shard/main-push-full、provider-first/dogfood、human-only mergeへ更新する。

## Rejected alternatives

- Additional decision/test/verification Issues。
- S40/S50/S70 single merge handoff。
- PR-Bでpolicy consumersを削除しS70-only toolへ依存するtemporary broken state。
- S60で`.github/workflows/provider-ci.yml`をretargetせず、deleted test pathsを残すこと。
- S60で`tests/unit/test_provider_test_lanes.py`を更新せず、active/stale ledger assumptionsを残すこと。
- S70で`tests/unit/test_provider_test_lanes.py` / `tests/unit/test_full_regression_baseline.py`を残したままtheir provider modulesを削除すること。
- Seed policyをCLI alias、seed existence、stateから再推測。
- Generic recursive `spec-dock` bootstrap/cleanup。
- Repository evidence SHAからpost-#387 mainまでのsingle allowlist diff。
- Tracked reportへのfinal/post-merge evidence writeback。
- Merge strategyを固定せずcommit SHA equalityを要求。
- New context required化前のRED proofまたはold gate先行除去。
- Different Linux environmentsのmetrics混合。
- Final AGENTSにretired commandsを残す。
- Runtime toggle、bridge、old fallback、shard/skip/ledger approval。

## Consequences

Mainの各merge pointはworking product/gateを持つ。PR-B current workflowsとPR-C final provider gateは独立に実行可能でGREENである。Resume seed authorityはdurable。Fresh empty repositoryをsafeにbootstrapできる。Specificationと#387 implementation driftを混同しない。Evidence graphはself-referenceせずmerge strategyを正しく扱う。Required transitionにgapがない。Qualification driftを検出でき、operator guidanceがactual final systemへ一致する。

CostはPR-B/PR-C internal checkpointsをmainへmergeできないこと、external attestations/human settings operation、Linux descriptor maintenance、native primitive依存、exact `0.2.3`以外のmanual recoveryである。

## Supersession and consistency

#388〜#390はsuperseded historical nodesでありreopenしない。本ADRはEpic/Issue R/D/PとLuna handoffへ反映する。矛盾時はimplementationを停止しcanonical contractを先に整合させる。Owner decision listはempty。
