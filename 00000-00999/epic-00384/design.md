---
種別: 設計書（Epic）
ID: "epic-00384"
タイトル: "Provider Test Strategy Simplification and Execution Cost Reduction"
関連GitHub: ["#384"]
状態: "draft"
最終更新: "2026-09-01"
依存: ["requirement.md", "artifacts/20260831t152024z-adr-single-implementation-unit-and-provider-hard-cutover-policy.md"]
親: ["init-local-00003"]
正本検証:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "d18ca60b2a6ff11571ee366f71c4528dcd668d99"
---

# epic-00384 Provider Test Strategy Simplification and Execution Cost Reduction — 設計

## 1. Design intent

現行のhistorical per-file reconciliation、journal/checkpoint recovery、purge、failure approval、sharded regressionを、fixed ownershipとexternal rerun convergenceを中心とする一つのdeep contractへ置換する。設計の主眼は「少ないcode」ではなく、「誰がどのpathを変更できるか」「partial failure後に何を許可するか」「どのartifactをどのlaneが証明するか」を静的に限定することである。

## 2. Architecture

```text
public CLI: src/spec_dock/cli.py
          |
          v
public result adapter
          |
          v
provider lifecycle service
   |          |             |
   v          v             v
classifier  candidate     legacy-0.2.3 recognizer
   |          |             |
   +----------+-------------+
              |
              v
   descriptor-bound POSIX filesystem
              |
              v
  4 roots + 2 slots + fixed record
  (+ fresh-init-only seed creation)

provider source assets
  src/spec_dock/assets/spec_dock/{docs,templates,system,scripts}
  src/spec_dock/assets/install_root/.agents/skills/{spec-dock,spec-dock-grill-with-docs}

provider gate
  one build -> wheel/sdist manifest
      |             |
      v             v
  Linux canonical  macOS delta
      |
      v
  required provider context -> human merge
```

### E384-D-001 — Boundary decomposition

- `src/spec_dock/cli.py`はparser、command-to-service dispatch、human-readable error boundaryだけを所有する。
- `src/spec_dock/provider_lifecycle/`はfixed path model、candidate、filesystem safety、legacy recognizer、service、public result mappingを所有する。
- `src/spec_dock/assets/legacy_0_2_3.json`はsingle supported legacy generationのroot/slot tree digestだけを所有する。
- `scripts/provider_gate.py`はartifact build/verify、node ownership、run-series evidenceを所有し、product mutation authorityを持たない。
- `tests/provider_test_ownership.json`はcontract-to-owner-lane mappingだけを所有し、failure approval、timing weight、shard partitionを持たない。

### E384-D-002 — Provider/dogfood direction

`src/spec_dock/`を先に変更し、dogfoodはprovider lifecycleを通じて次を同期する。

- `spec-dock/{docs,templates,system,scripts}`
- `.agents/skills/spec-dock`
- `.agents/skills/spec-dock-grill-with-docs`
- `spec-dock/spec-dock.version`

Dogfoodの`spec-dock/.gitignore`と`.github/workflows/ci.yml`はconsumer-owned seedであり、provider sourceとbytesが異なってもupdate対象にしない。

## 3. Ownership model

### E384-D-003 — Persistent mutation set

| Category | Exact path | Authority |
|---|---|---|
| Disposable root | `spec-dock/docs` | valid new recordまたはexact legacy recognition |
| Disposable root | `spec-dock/templates` | 同上 |
| Disposable root | `spec-dock/system` | 同上 |
| Disposable root | `spec-dock/scripts` | 同上 |
| Disposable slot | `.agents/skills/spec-dock` | matching new markerまたはexact legacy tree |
| Disposable slot | `.agents/skills/spec-dock-grill-with-docs` | 同上 |
| State record | `spec-dock/spec-dock.version` | lifecycle serviceのみ |
| Seed creation | `spec-dock/.gitignore` | fresh `init`かつabsent時だけ |
| Seed creation | `.github/workflows/ci.yml` | fresh `init`かつabsent時だけ |

Providerはfixed rootの内部pathを個別所有しない。recordがroot ownershipを証明した後はroot全体をreplace/deleteする。recordがないfresh targetではfixed rootの存在自体をforeign collisionとしてblockする。

### E384-D-004 — Transient staging

Candidate stagingはtarget repositoryの外、同じfilesystem上のtarget parentに作る。pathは次のdeterministic formである。

```text
<target-parent>/.spec-dock-provider-txn-<root-identity-hash>-<operation>-<candidate-digest>
```

staging rootにはstrict owner markerを置き、repository rootのdevice/inode、operation、candidate digestが一致する場合だけ再利用・cleanupする。transient pathはpersistent mutation authorityではなく、same-operation/same-candidate rerunの実装手段である。foreign collision、owner marker mismatch、symlinkはblockする。

## 4. State machine

### E384-D-005 — Observed states

```text
absent
  | install
  v
incomplete(install) -> ready
                          |
                          | update
                          v
                    incomplete(update) -> ready
                          |
                          | uninstall --apply
                          v
                 incomplete(uninstall)
                          |
                          v
              tooling-absent-preserved-data
                          |
                          | reinstall
                          v
                 incomplete(install) -> ready

exact legacy-0.2.3
  | migrate or tooling uninstall
  +-------------------------------> new-format states

unsafe / unknown evidence -> blocked (not serialized)
```

`blocked`はrecord stateではない。record/path/binding/marker/candidate evidenceから算出する。

### E384-D-006 — Record identity

`spec-dock/spec-dock.version`を再利用する理由は二つである。

1. current `0.2.3` packageがこのpathをASCII canonical versionとしてpre-mutation admissionで解析する。
2. final JSON recordはcanonical versionではないため、old packageがnative rename routeへ到達する前にfail closedする。

Final recordはstrict keysだけを許可する。

```json
{
  "schema_version": 1,
  "state": "ready",
  "operation": null,
  "version": "0.2.4",
  "candidate_digest": "<64 lowercase hex>",
  "skill_slots": {
    "spec-dock": "0.2.4",
    "spec-dock-grill-with-docs": "0.2.4"
  }
}
```

- `state`: `incomplete | ready | tooling-absent-preserved-data`
- `operation`: `incomplete`時だけ`install | update | uninstall`、その他は`null`
- `version`: operationが対象とするinstalled/final distribution version
- `candidate_digest`: fixed rootsとslot payloadのimmutable digest。seed、record、generated slot markerを含めない。
- `skill_slots`: exact two keys。additional slotを許可しない。

Canonical serializationはUTF-8、sorted keys、2-space indent、末尾LFである。unknown key、duplicate JSON key、non-regular file、hard link、oversized record、invalid UTF-8をblockする。

### E384-D-007 — Slot marker

各new-format slot直下に`.spec-dock-provider-slot.json`を生成する。

```json
{
  "schema_version": 1,
  "slot": "spec-dock",
  "version": "0.2.4",
  "candidate_digest": "<same candidate digest>"
}
```

markerはcandidate digest計算後に生成し、digest対象から除外して循環参照を避ける。new recordが存在するslotはmatching markerがある場合だけprovider-ownedである。markerless slotはlegacy recognizer以外ではforeignである。

## 5. Candidate and filesystem interfaces

### E384-D-008 — Candidate construction

Candidate sourceはcode-fixedである。

| Target | Package source |
|---|---|
| `spec-dock/docs` | `src/spec_dock/assets/spec_dock/docs` |
| `spec-dock/templates` | `src/spec_dock/assets/spec_dock/templates` |
| `spec-dock/system` | `src/spec_dock/assets/spec_dock/system` |
| `spec-dock/scripts` | `src/spec_dock/assets/spec_dock/scripts` |
| `.agents/skills/spec-dock` | `src/spec_dock/assets/install_root/.agents/skills/spec-dock` |
| `.agents/skills/spec-dock-grill-with-docs` | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-grill-with-docs` |

Candidate builderはsource treeをno-followでcaptureし、regular fileとreal directoryだけを許可する。path traversal、absolute path、device entry、FIFO、socket、symlink、hard-linked regular fileをrejectする。executable modeを含むcanonical entry streamをsorted UTF-8 path orderでSHA-256する。headerにdigest schemaとdistribution versionを含める。

Seedsは別sourceとして読み、fresh creation bytesをvalidationするがcandidate digestへ含めない。

### E384-D-009 — Atomic publication

1. repository rootをreal directoryとしてopenし、`flock`でoperationを排他する。
2. root identityと全target parent chainを`O_NOFOLLOW | O_DIRECTORY`でbindする。
3. candidateをrepository外のsame-filesystem staging rootへmaterializeし、source digestとstaged digestを一致させる。
4. all-target preflight後、external staged recordを`spec-dock/spec-dock.version`へatomic replaceし`incomplete`を公開する。
5. `docs -> templates -> system -> scripts -> spec-dock slot -> grill slot`の順でpublishする。
   - target absent: native no-replace rename。
   - target valid existing directory: native exchange rename。old treeはstaging側へ移る。
6. fresh `init`だけ、absent seedを`O_EXCL | O_NOFOLLOW`で作成する。
7. 全target postcondition成立後、`ready` recordをatomic replaceする。
8. old treeとstagingをcleanupする。ready成立後のowned cleanup failureだけwarningへ降格できる。

Uninstallはvalid targetをstaging tombstoneへnative no-replace renameしてrepository pathをatomicにabsent化し、最後にtooling-absent recordをpublishする。

## 6. Operation flows

### E384-D-010 — Install and update

- `install_tooling`は`absent`、`tooling-absent-preserved-data`、exact legacy migrationを扱う。
- `update_tooling`は`ready`、exact legacy migrationを扱い、missing fixed targetをrepairできる。
- `update` commandがnever-installed `absent`へ実行された場合はcompatibilityのため`install_tooling`へdispatchするが、fresh-init-only seedを作成しない。
- `init --force`はobserved stateに応じてinstall/updateへdispatchし、独自mutation authorityを持たない。
- incomplete stateはrecord operationとcandidate digestが一致する場合だけresumeする。

### E384-D-011 — Uninstall and reinstall

- dry-runはrecord/path/bindingを完全にpreflightし、mutationなしでplanned actionsを返す。
- applyは`incomplete(uninstall)`を先にpublishし、4 roots、valid owned slotsをdetachする。
- user data、unknown non-target、seed、unrelated skillをtouchしない。
- final recordは`tooling-absent-preserved-data`。last installed version/digest/slot versionsを保持する。
- reinstallはnew candidateで`incomplete(install)`へ移行し、seed absenceをconsumer intentとして保持する。

## 7. Legacy migration and downgrade safety

### E384-D-012 — Exact legacy recognizer

`src/spec_dock/assets/legacy_0_2_3.json`はpost-#387 baseline artifactから生成し、次だけを持つ。

- schema version
- exact legacy version `0.2.3`
- plain marker SHA-256
- 4 root tree digests
- 2 slot tree digests
- active recovery marker exact paths

Recognizerはread-onlyで、4 rootsは全てexactを要求する。2 slotsは各々absentまたはexactを許可する。seedとconsumer dataは認識対象外である。active legacy recovery markerが一つでも存在すればblockする。

Migrationの最初のdurable writeはplain version markerをnew `incomplete` JSONへ置換することであり、この時点からold packageはfinal parser boundaryでblockされる。

### E384-D-013 — Composite tripwire

Built old wheelは`PYTHONPATH`でstartup-injected `sitecustomize`を読み込む。tripwireは次をsyscall前に捕捉する。

- target-scoped write/create/truncate/append `open`
- `os.remove/unlink/rename/replace/rmdir/mkdir/chmod/link/symlink/truncate`
- `ctypes.CDLL`から解決されたLinux `renameat2`、macOS `renameatx_np`

Native function proxyは`argtypes`/`restype` assignmentを受け付け、`__call__`でsource/destinationをdirfdから解決し、target scopeならunderlying symbolを呼ばずfailする。各platformのpositive controlは同じsymbolを直接解決・callし、event 1で阻止されることを証明する。old command matrixはevent 0でなければ失敗する。

## 8. Result and failure architecture

### E384-D-014 — Typed result

Service resultは次のstatusを持つ。

| Status | Meaning | Exit |
|---|---|---:|
| `planned` | dry-run plan成立 | 0 |
| `completed` | desired durable state成立 | 0 |
| `completed_with_warnings` | desired state成立、owned external cleanupのみ残存 | 0 |
| `blocked` | pre-mutation ownership/binding/state/candidate拒否 | 1 |
| `partial_failure` | durable mutation開始後、desired state未成立 | 1 |
| `error` | invalid requestまたはremoved operation | 2 |

`mutation_started`はincomplete recordがpublishされたかで決まる。partial failureはsame operation / same candidate retry commandを持つ。arbitrary rollback guidanceを返さない。

### E384-D-015 — Forward-fix policy

- preflight failure: mutation zero、同じIssue内でinputまたはimplementationを修正する。
- partial failure: same operation / same candidate external rerunだけを許可する。
- old-package mutation attempt: merge禁止。record/marker boundaryを同じIssueで修正して全matrixを再実行する。
- destructive defect: apply routeをfail closedにする。old engine fallback禁止。
- post-merge defect: human-reviewed revertまたはforward fix。consumer dataをrollback素材にしない。

## 9. Test and CI target

### E384-D-016 — Portfolio layers

| Layer | Owns | Must not own |
|---|---|---|
| Pure/model | state table、record schema、result mapping、path constants | real FS、subprocess、package build |
| Filesystem/service | no-follow、atomic publish、fault convergence、preservation | GitHub settings、built old wheel |
| CLI runtime | parser、wrapper forwarding、text/JSON/exit | exhaustive root/slot matrix |
| Built artifact | baseline migration、final lifecycle、old-package tripwire、artifact identity | unit-only branches |
| macOS delta | native rename/no-follow/mode/entry point | Linux-independent lifecycle duplicates |

`tests/provider_test_ownership.json`はrequirement/design trace ID、owner node、lane、representative faultを一意にmappingする。duplicate `(candidate, os, contract_id)`をrejectする。

### E384-D-017 — Provider gate topology

```text
Provider CI / provider-static-analysis
                   |
                   v
Provider CI / provider-tests (Linux)
  - verify PR head
  - one uv build invocation -> wheel + sdist + manifest
  - install wheel
  - one canonical pytest process, worker 1
  - sdist minimal smoke
  - upload exact artifacts/evidence
                   |
                   v
Provider CI / provider-macos-delta
  - download Linux-built artifact
  - verify wheel SHA-256
  - install same wheel
  - run only macOS-owned nodes
                   |
                   v
Provider CI / provider-gate
  - aggregate both jobs
  - no tests, no rebuild
  - required context
                   |
                   v
               human review/merge
```

Qualification mode reuses one built candidate and executes canonical run 20 times sequentially。first 5 satisfy budget、all 20 satisfy flake/retry contract。required PR gateは通常1回とし、qualification evidenceはfinal PR headへ束縛する。

### E384-D-018 — Old machinery terminal state

Final treeに次を残さない。

- `src/spec_dock/managed_distribution.py`
- `src/spec_dock/assets/managed_distribution.json`
- `full-regression-ledger.json`
- `full-regression-timing-weights.json`
- `scripts/quality/full_regression_baseline.py`
- `scripts/quality/verify_full_regression.py`
- `.github/workflows/provider-full-regression.yml`
- root `tests/conftest.py`のlane/policy hooks
- `fast` / `full_regression` marker declarations
- old distribution-specific duplicate test files

Non-distribution behaviorが`managed_distribution.py`に残っている場合は、cutover前に`src/spec_dock/context_pack.py`へbehavior-preserving extractionし、old engine fileを完全に削除する。

## 10. #387 post-merge rebaseline design

### E384-D-019 — Deterministic admission

Admissionは次をrecordする。

- `AUTHORING_SHA=d18ca60b2a6ff11571ee366f71c4528dcd668d99`
- `POST_387_SHA`
- #387 issue state/merge evidence
- exact diff path list
- content-restriction checks
- current command results
- baseline `0.2.3` wheel/sdist hashes
- current node inventory and active ledger inventory

Allowed driftは#387 R/D/Pに列挙されたCurrent text、active request、package/test hygiene、#387 own report/evidenceだけである。`pyproject.toml`、`tests/conftest.py`、ledger/timingへの変更はexact restrictionを満たす場合だけ許可する。protected pathまたはunclassified diffが一つでもあればadmissionはfailする。

## 11. Traceability

| Requirement | Design |
|---|---|
| E384-RQ-001〜002 | E384-D-003〜004、008〜009 |
| E384-RQ-003〜007 | E384-D-005〜012 |
| E384-RQ-008 | E384-D-008〜009 |
| E384-RQ-009 | E384-D-010、014 |
| E384-RQ-010 | E384-D-006、012〜013 |
| E384-RQ-011〜012 | E384-D-016、018 |
| E384-RQ-013〜015 | E384-D-017〜018 |
| E384-RQ-016 | E384-D-015、017、019 |
