---
種別: 実装計画書（Epic）
ID: "epic-00384"
タイトル: "Provider Test Strategy Simplification and Execution Cost Reduction"
関連GitHub: ["#384"]
状態: "draft"
最終更新: "2026-09-01"
依存: ["requirement.md", "design.md", "artifacts/20260831t152024z-adr-single-implementation-unit-and-provider-hard-cutover-policy.md"]
親: ["init-local-00003"]
正本検証:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "ef183ae46febe52f0152431cb3a8b4846c9972fc"
---

# epic-00384 Provider Test Strategy Simplification and Execution Cost Reduction — Epic計画

Normative artifacts: `artifacts/provider-lifecycle-wire-contract.md` and `artifacts/active-failure-disposition-register.md` (Issue documents use `../../artifacts/...`). Their exact wire/disposition data is not delegated to implementation.


## 1. Governance

Epic #384はProduct判断、scope、acceptance、implementation unit boundaryを管理する。実装作業は唯一のchild Issue #392で行う。#388〜#390をreopenせず、research、decision、tests、CI、final verificationを別Issueへ分割しない。

### E384-P-001 — Single-Issue boundary

- Authorized unit: `iss-00392` / GitHub #392。
- Internal step、commit、PR、canary PRは#392の実行手段であり新Issueではない。
- Failureをledger/skip/retryで承認しない。

### E384-P-002 — Specification and dependency gate

Implementation開始前に、replacement manifest hashes、owner-recorded `SPEC_FREEZE_COMMIT`、#387 own merge delta、implementation base ancestry、baseline `0.2.3` artifacts/current gatesをS00で検証する。Repository evidence SHAは調査起点に限り、future mainへのblanket diff baseにしない。

## 2. Ordered execution

1. **S00 Admission and baseline**: specification lineageと#387 deltaを分離検証。
2. **PR-A S10-S30 dormant successor**: seed policy、candidate、container bootstrap、install/update/resume。S30だけmerge gate、mainはold public product。
3. **PR-B S40-S60 combined public cutover**: S40/S50 internal、S60だけmerge gate。Complete lifecycle、`provider-lifecycle-wire-contract.md`、legacy proof、old engine removal、`active-failure-disposition-register.md`どおりのfailure terminalization、root/provider/dogfood lifecycle docs convergence、transitional `provider-ci.yml` retargetを同一PRで完了する。Current PR workflowとmain-push verifierを独立にGREENとする。
4. **PR-C S70-S80 gate cutover**: S70 internalでreplacement tooling/environment/workflow/AGENTS/test-policy docs/final testsを追加し、全policy consumersをretire/replaceした後にproviders/old machineryを同じbranchで削除する。S70 local buildはpre-freeze tooling smokeだけ。S80はtracked contentを編集せずhead freeze、final Provider CI dispatch、single Linux build artifactのdownloaded-byte qualification/macOS/sdist/attestation、required-context transitionだけを行い、その後merge。
5. **Human merge and external closure**: tree OID equality、SpecDock finish、Issue/Epic closeをexternal attestationsへ記録。

## 3. Multi-PR policy and exact merge points

| PR | Internal steps | Only permitted main merge gate | Main state after merge |
|---|---|---|---|
| PR-A | S10 -> S20 -> S30 | S30 all proof GREEN | Old public product + dormant successor。Current test/workflow intact。 |
| PR-B | S40 -> S50 -> S60 | S60 all proof GREEN | Complete final `0.2.4` lifecycle、wire contract、legacy proof、old engine removed、`active-failure-disposition-register.md` applied、root/provider/dogfood lifecycle docs final、active approved failure 0。Transitional `provider-ci.yml` and current main-push verifier independently GREEN。 |
| PR-C | S70 -> S80 | S80 exact final workflow run + required transition + external attestation | All old policy consumers retired before provider deletion、Linux `provider-build-artifacts` is the sole frozen-head producer、all consumers download identical bytes/build 0、old workflow/policy removed、root AGENTS/test-policy docs final。 |

S40、S50、S70をmain merge candidateとしてhandoffしない。PR-B merge時にS70-only toolへ依存せず、`.github/workflows/provider-ci.yml`と`tests/unit/test_provider_test_lanes.py`をS60 ownershipへ含め、current PR/main-push workflowsの全consumerを実在する状態に保つ。PR-Cではreplacement workflow/tooling/testsを追加し、`tests/unit/test_provider_test_lanes.py`と`tests/unit/test_full_regression_baseline.py`を含むall policy consumersをprovidersより先にretire/replaceした同一change setでold providers/workflowを除去する。

## 4. Human gates

### E384-P-003 — Review and merge

各PRはhuman review必須。Agentはmerge、required context、branch protectionを変更しない。

### E384-P-004 — No-gap required-context transition

Human repository adminは次の順序を厳守する。

1. before required contexts、review requirement、merge queueをcapture。
2. new `Provider CI / provider-gate`をGREEN、old requiredを維持。
3. new contextをrequiredへ追加し、oldを外さない。
4. old+new requiredをread-back。
5. dedicated non-merge canary PRでnew gateだけintentional RED。
6. canary merge blockedを確認。
7. canaryを閉じ、implementation PRをGREENへ戻す。
8. implementation PR new gate GREENをread-back。
9. old provider-only contextをremove。
10. final required set/review requirementをread-back。

Step 9を5〜8より前に実行しない。Settings unreadable、RED not blocking、unrelated diffはhard stop。

## 5. Evidence contract

### E384-P-005 — Tracked versus external evidence

Tracked #392 `report.md`はmethod、pre-freeze implementation facts、terminalization rationale、external schema/locationを含む。Own hash、final PR head/tree、final source-bound artifact hashes、human merge、SpecDock finish/GitHub close/Epic closeを含めない。

Final report commit後にPR headをfreezeし、build/qualification/context resultsを`pre-merge-attestation-v1` canonical JSONとして新規GitHub comment/check artifactへ投稿する。Post-merge factsは`post-merge-closure-v1`、Epic closeは`epic-closure-v1`へ記録し、tracked treeへ書き戻さない。

### E384-P-006 — Evidence identity

External pre-merge attestationはrepository、Issue/PR、`SPEC_FREEZE_COMMIT`、implementation base、final PR head/tree、tracked report blob OID（external observation）、wheel/sdist hashes、candidate digest、build count、environment ID/descriptor hash/fingerprint、OS/Python/uv、commands/exits、node inventory、wall/CPU、fault/flake、required contexts before/both/final、canonical JSON SHA-256を持つ。

### E384-P-007 — Stable qualification environment

Environment IDは`specdock-linux-qualification-v1`。Tracked descriptor、pinned base digest、x86_64、2 CPU、8 GiB、Python/uv/lock、observed fingerprintを全20 runsへ束縛する。一件でもmismatchならseries invalid。別environmentのmetricsを混合しない。

### E384-P-008 — PR-B documentation and contract gates

S40/S60 own lifecycle docs listed byE384-D-025。S60 must passprovider/dogfood `cmp` andthe retired-lifecycle grep overroot README andcurrent provider/dogfood docs。`provider-lifecycle-wire-contract.md` goldens and`active-failure-disposition-register.md` exact rows aretest inputs; Luna maynotchange enum/disposition toobtainGREEN。

### E384-P-009 — Authoritative artifact workflow

S70 validates provider-gate tooling locally beforehead freeze andlabels everylocal artifact non-authoritative。S80 startsfromaclean frozenhead andusesonlythe final Provider CI workflow:

1. dispatch qualification run for exactcandidate SHA;
2. wait forconclusion;
3. verifyone `provider-build-artifacts` job andone immutable artifact identity;
4. download wheel/sdist/manifest;
5. verifyhash/source/tree andeach downstream receipt'sbuild count 0;
6. consume workflow evidence forqualification、macOS、sdist、attestation;
7. no local final build。

Any local output、different workflow run、re-upload、second producer isinvalid acceptance evidence。

## 6. Stop and forward-fix policy

次の場合、main merge gateへ進まない。

- spec hash/commit mismatch、#387 delta mismatch
- fresh container authority/cleanupが証明不能
- record/request/stage seed policy mismatch
- fixed path外のmutation authorityが必要
- old package mutation attempt
- native primitive/no-follow binding unavailable
- active failure not terminalized
- S60がS70-only toolへ依存、`.github/workflows/provider-ci.yml`にdeleted test pathが残る、`tests/unit/test_provider_test_lanes.py`がactive/stale referenceを許容する、またはcurrent workflow consumerを削除
- S70で`tests/unit/test_provider_test_lanes.py` / `tests/unit/test_full_regression_baseline.py`等のconsumerが残ったままproviderを削除、またはold removal前にreplacement gate unavailable
- environment fingerprint mismatch、build/hash/budget/fault/flake failure
- new context required前にoldを外す、RED not blocking、settings unreadable
- tracked report self-reference/post-merge writeback
- tree OID mismatch
- root/provider/dogfood lifecycle docs retain journal/retry/purge/empty-boundary guidance at S60
- wire enum/golden mismatch or failure register row/signature/successor mismatch
- S80 local final build、more than one frozen-head producer、downstream build invocation、artifact upload/download hash mismatch
- root AGENTS still documents retired policy

同じ#392でforward-fixし、新Issue、shard、skip、approved failure、old fallbackで回避しない。

## 7. Closure states

### Specification frozen

Manifest hashesと`SPEC_FREEZE_COMMIT`が一致した状態。

### Implementation complete

PR-C tracked changesとnon-self-referential reportがcomplete。Final source-bound evidenceはまだexternal取得中でもよい。

### Pre-merge attested

Final headを変更せずbuild/qualification/required gateがGREENで、content-addressed pre-merge attestationが投稿済み。

### PR merge ready

Pre-merge attested、human review、new required context、rollback情報が揃う。

### Human PR merge

Humanだけが実行。Merge commitを許容し、commit SHA equalityではなくtree OID equalityを検証。

### Issue finished

Merge tree equality後、SpecDock `issue finish`とGitHub #392 closeをexternal closure attestationへ記録。Tracked reportへ追記しない。

### Epic closed

#392 finished後、GitHub #384 closeをexternal Epic closure attestationへ記録。

## 8. Epic completion criteria

- Epic/Issue R/D/P、ADR、handoffがsame eight correction contractsを表す。
- #387 dependencyとspecification lineageを独立検証。
- Only main gates are S30/S60/S80。
- PR-Bにbroken workflow/S70-only dependencyなし。
- Seed policy、fresh container、stable Linux environment、non-cyclic evidence、`provider-lifecycle-wire-contract.md`、`active-failure-disposition-register.md`がtraceされる。
- PR-B docs are final for lifecycle; PR-C docs are final for test policy。
- Frozen-head artifact producer is exactly one Linux CI job; all downstream consumers build 0。
- Required context transitionにgate gapなし。
- Root AGENTS final policy。
- Human merge tree equals verified PR tree。
- Owner decision list empty。
