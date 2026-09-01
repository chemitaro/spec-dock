---
種別: 設計書（Issue）
ID: "iss-00392"
タイトル: "Provider Lifecycle And Regression Gate Hard Cutover"
関連GitHub: ["#392"]
状態: "draft"
最終更新: "2026-09-01"
依存: ["requirement.md", "../../design.md", "../../artifacts/20260831t152024z-adr-single-implementation-unit-and-provider-hard-cutover-policy.md"]
親: ["epic-00384", "init-local-00003"]
正本検証:
  repository: "chemitaro/spec-dock"
  branch: "codex/epic-00384-provider-test-strategy-planning"
  sha: "91667235c6892f025a1d9ee69cf37525537a3c9e"
---

# iss-00392 Provider Lifecycle And Regression Gate Hard Cutover — 設計

## 1. Implementation architecture

### I392-D-001 — Exact production module topology

Final production layoutを次に固定する。`(new)`はverified revisionに存在しないsymbol/pathである。

```text
src/spec_dock/
  cli.py                                      # existing; parser/dispatchへ縮小
  context_pack.py                             # new; old moduleからnon-lifecycle behaviorを抽出
  provider_lifecycle/                         # new
    __init__.py
    model.py
    candidate.py
    filesystem.py
    legacy_023.py
    service.py
    public_result.py
  assets/
    legacy_0_2_3.json                         # new; single-version whole-tree digest fixture
    spec_dock/{docs,templates,system,scripts}
    install_root/.agents/skills/{spec-dock,spec-dock-grill-with-docs}
```

Final treeでは次を削除する。

```text
src/spec_dock/managed_distribution.py
src/spec_dock/assets/managed_distribution.json
```

`managed_distribution.py`に残る`_render_context_pack`とそのtransitive non-lifecycle dependencyは、behaviorを変えず`src/spec_dock/context_pack.py`の`render_context_pack()`へ移す。lifecycle type、journal、manifest、purge dependencyを持ち込まない。

### I392-D-002 — Exact symbols

`model.py`:

- `FINAL_DISTRIBUTION_VERSION = "0.2.4"`
- `INSTALLATION_RECORD_PATH = PurePosixPath("spec-dock/spec-dock.version")`
- `TOOLING_ROOTS`
- `SKILL_SLOTS`
- `FRESH_INIT_SEEDS`
- `SLOT_MARKER_NAME = ".spec-dock-provider-slot.json"`
- `LifecycleState`
- `LifecycleOperation`
- `LifecycleStatus`
- `SeedPolicy`
- `InstallRecord`
- `SlotMarker`
- `Candidate`
- `TargetObservation`
- `LifecycleAction`
- `LifecycleResult`
- `LifecycleFaultHook` protocol
- strict `parse_*` / `serialize_*` helpers

`candidate.py`:

- `build_packaged_candidate(assets_root: Path, version: str) -> Candidate`
- `materialize_candidate(candidate, stage_root)`
- `digest_candidate_entries(...)`
- `digest_tree(...)`
- `validate_staged_candidate(...)`
- `load_seed_bytes(...)`

`filesystem.py`:

- `RepositoryBinding`
- `BoundParent`
- `StagingOwner`
- `PosixProviderFilesystem`
- `lock_repository()`
- `bind_repository()`
- `bind_parent_chain()`
- `resolve_no_replace_rename()`
- `resolve_exchange_rename()`
- `rename_no_replace()`
- `rename_exchange()`
- `atomic_publish_record()`
- `publish_directory()`
- `detach_directory()`
- `create_seed_if_absent()`
- `cleanup_owned_stage()`

`legacy_023.py`:

- `Legacy023Fixture`
- `Legacy023Observation`
- `Legacy023Recognizer`
- `load_legacy_023_fixture()`
- `observe_exact_legacy_023()`

`service.py`:

- `ProviderLifecycleService`
- `classify_target()`
- `install_tooling()`
- `update_tooling()`
- `uninstall_tooling()`
- `dispatch_init()`
- `dispatch_update()`
- `resume_incomplete()`
- no-op default fault hook

`public_result.py`:

- `exit_code_for_result()`
- `render_init_update_success()`
- `render_public_error()`
- `uninstall_payload_from_result()`
- `render_uninstall_text()`

`cli.py`は上記service/resultだけをimportし、old `Distribution*` type、`execute_*_distribution`、purge helper、journal helperをimportしない。

## 2. Path and ownership constants

### I392-D-003 — Code-fixed path set

```python
TOOLING_ROOTS = (
    PurePosixPath("spec-dock/docs"),
    PurePosixPath("spec-dock/templates"),
    PurePosixPath("spec-dock/system"),
    PurePosixPath("spec-dock/scripts"),
)

SKILL_SLOTS = (
    PurePosixPath(".agents/skills/spec-dock"),
    PurePosixPath(".agents/skills/spec-dock-grill-with-docs"),
)

FRESH_INIT_SEEDS = (
    PurePosixPath("spec-dock/.gitignore"),
    PurePosixPath(".github/workflows/ci.yml"),
)
```

Service APIはpath list、manifest path、arbitrary action listを引数に受け取らない。全mutation pathはこれらのconstantとrecord pathからだけ生成する。

Parent creation authorityはfresh `init`の`.github/workflows/ci.yml`に対する`.github`、`.github/workflows`のabsent real-directory creationだけである。existing parentがsymlink/non-directoryならseedを作成せずblockする。ただしseed path自体が既に存在する場合はconsumer-ownedとして内容/typeを問わずpreserveし、そのためにparentを辿らない。

## 3. Data contracts

### I392-D-004 — Strict installation record

`InstallRecord` validation:

- max encoded size: 4096 bytes
- regular file、link count 1、write mode `0644`
- UTF-8、JSON object、duplicate key rejection
- exact keys: `schema_version,state,operation,version,candidate_digest,skill_slots`
- `schema_version == 1`
- versionはcanonical `0.2.4`またはlegacy uninstall stateの`0.2.3`
- digestは`[0-9a-f]{64}`
- skill slot keysはexact two names
- slot versionsはrecord versionと一致
- ready/tooling-absentでは`operation is None`
- incompleteではoperationがnon-null

Record publishはexternal stage fileをbound `spec-dock` parentへdescriptor-safe atomic renameで行い、fileとparentをfsyncする。record contentをin-place overwrite/truncateしない。

### I392-D-005 — Candidate digest

Canonical digest stream:

```text
provider-candidate-v1\n
version\0<version>\n
<logical-path>\0dir\0<mode-octal>\n
<logical-path>\0file\0<mode-octal>\0<size>\0<content-sha256>\n
...
```

- logical pathはtarget-relative POSIX path。
- entryはUTF-8 encoded logical path bytesでsortする。
- directoryとfileを含む。
- symlink/special/hard-linked fileはcandidate-invalid。
- generated slot marker、record、seedsはstream外。
- source capture後とstage materialize後に同じdigestを再計算する。
- source snapshotがcapture中に変化した場合はcandidate-invalid。

### I392-D-006 — Slot marker

Marker max size 2048 bytes、strict exact keys、mode `0644`。slot payload materialize後、candidate digestを使ってmarkerを生成する。marker自体はslot ownershipを証明するが、candidate payload digestへ自己参照しない。

## 4. Filesystem safety

### I392-D-007 — Binding and lock

- Targetはexisting real directoryでなければrequest error。
- root fdを`O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC`でopenする。
- `fcntl.flock(LOCK_EX)`で一operationを排他する。
- visible `lstat`とheld `fstat`のdevice/inode/typeを各mutation前後に一致確認する。
- parent chainはcomponentごとにdirfd-relative openし、symlinkをfollowしない。
- regular targetのlink countが1でなければblockする。
- operation中にroot/parent/target identityが変化した場合はpartial failureまたはblockedとして停止する。

### I392-D-008 — External deterministic stage

`root_identity_hash = sha256(f"{st_dev}:{st_ino}".encode()).hexdigest()[:16]`

```text
<target.parent>/.spec-dock-provider-txn-<root_identity_hash>-<operation>-<candidate_digest>
```

Stage owner markerは`STAGE-OWNER.json`で、schema、root device/inode、operation、digestを持つ。stage pathが存在する場合:

- exact owner marker + matching operation/digest: resume用としてvalidate。
- marker missing/invalid、symlink、different root/operation/digest: block。
- cross-candidate operationはnew stageを作らずblock。

Stageはtarget tree外であるためcandidate stage/validation failure時のtarget digestは不変である。stage cleanup warningはtarget desired state成立後だけsuccess warningへ降格する。

### I392-D-009 — Native rename API

Existing target root/slot replacementはexchangeを必須とする。

| Platform | No-replace | Exchange |
|---|---|---|
| Linux | `renameat2(..., RENAME_NOREPLACE=1)` | `renameat2(..., RENAME_EXCHANGE=2)` |
| macOS | `renameatx_np(..., RENAME_EXCL=4)` | `renameatx_np(..., RENAME_SWAP=2)` |

`ctypes.CDLL(None, use_errno=True)`でsymbolをresolveし、argtypes/restypeを固定する。symbol不在、unsupported platform、EXDEV、unexpected errnoをgeneric renameへfallbackしない。fresh absent publicationとuninstall detachはno-replace、update/legacy replaceはexchangeを使う。

## 5. Target classifier

### I392-D-010 — Classification order

Classifierは次の順でread-only observationを行う。

1. root/record parent binding
2. final JSON record probe
3. final record validならstate-specific target/slot observation
4. recordがplain exact `0.2.3\n`ならlegacy recovery marker probe
5. legacy whole-tree digest validation
6. record absentならfixed-target collision probe
7. transient stage collision probe
8. resulting state or blocked reason

Record fileがJSONらしいがinvalidならlegacy fallbackしない。plain textが`0.2.3\n`以外ならunsupported legacyとしてblockする。

| State | Required postcondition |
|---|---|
| absent | record absent、all 4 roots/2 slots absent。unknown non-targetは可。 |
| legacy-0.2.3 | plain marker exact、4 roots exact、each slot absent/exact、recovery markers absent。 |
| ready | valid record。root/slot missingはrepairable、existing targetはsafe type。existing slotはmatching marker。 |
| incomplete | valid record、operation non-null。same candidate/operationだけresume。 |
| tooling-absent-preserved-data | valid record、4 roots/2 slots all absent。 |
| blocked | 上記を一意に証明できない。 |

Ready record下でroot contentが変更されていてもrootはrecord-ownedなのでupdate/uninstall可能である。ただしroot pathがsymlink/non-directoryならblockする。Slotはmarker mismatchならblockする。

## 6. Public command dispatch

### I392-D-011 — Dispatch table

`dispatch_init(force=False)`:

- absent -> install with `SeedPolicy.CREATE_IF_ABSENT`
- tooling-absent -> install with `SeedPolicy.PRESERVE_ONLY`
- incomplete install -> same-candidate resume
- otherwise -> blocked `already-initialized` or cross-intent

`dispatch_init(force=True)`:

- absent -> install + seeds
- tooling-absent -> install preserve-only
- legacy -> migrate
- ready -> update
- incomplete install/update -> matching resume
- incomplete uninstall -> cross-intent blocked

`dispatch_update()`:

- absent -> install preserve-only
- tooling-absent -> install preserve-only
- legacy -> migrate
- ready -> update
- incomplete install/update -> matching resume
- incomplete uninstall -> cross-intent blocked

`uninstall_tooling()`:

- `--remove-specs` -> filesystem-independent removed-operation error
- absent -> tooling-not-installed error
- tooling-absent -> idempotent planned/completed
- legacy/ready -> dry-run or apply
- incomplete uninstall -> matching resume
- incomplete install/update -> cross-intent blocked

## 7. Operation protocols

### I392-D-012 — Install/update protocol

```text
lock
-> classify
-> build source candidate
-> stage outside target
-> validate all target collisions/bindings
-> publish incomplete record
-> publish docs
-> publish templates
-> publish system
-> publish scripts
-> publish spec-dock skill
-> publish grill skill
-> create absent seeds only when SeedPolicy.CREATE_IF_ABSENT
-> validate full postcondition
-> publish ready record
-> cleanup owned stage
-> completed / completed_with_warnings
```

Every boundary invokes `LifecycleFaultHook(point_id, observation)` after durable step completion. Production hook is no-op. Test hook raises deterministic injected failure.

Matching target tree is no-op on resume。Exchange後にold treeがstage側へ移った場合、stage owner contractの一部としてcleanupする。

### I392-D-013 — Uninstall protocol

```text
lock
-> classify
-> produce complete dry-run action set
-> return planned when apply=false
-> publish incomplete(uninstall) record
-> detach docs
-> detach templates
-> detach system
-> detach scripts
-> detach valid spec-dock slot
-> detach valid grill slot
-> validate roots/slots absent and protected data unchanged
-> publish tooling-absent-preserved-data record
-> cleanup owned stage
-> completed / completed_with_warnings
```

Legacy uninstallはplain markerを`incomplete(uninstall)` JSONへ置換してから同じprotocolを使う。slot absentはno-op。legacy slot exact digest以外はapply前にblockする。

## 8. Legacy fixture

### I392-D-014 — `legacy_0_2_3.json`

```json
{
  "schema_version": 1,
  "version": "0.2.3",
  "record_sha256": "<sha256 of 0.2.3 LF>",
  "roots": {
    "spec-dock/docs": "<tree digest>",
    "spec-dock/templates": "<tree digest>",
    "spec-dock/system": "<tree digest>",
    "spec-dock/scripts": "<tree digest>"
  },
  "skill_slots": {
    ".agents/skills/spec-dock": "<tree digest>",
    ".agents/skills/spec-dock-grill-with-docs": "<tree digest>"
  },
  "recovery_paths": [
    "spec-dock/.distribution-retry.json",
    "spec-dock/.distribution-journal.json",
    "spec-dock/.uninstall-retry.json"
  ]
}
```

FixtureはI392-S00でpost-#387 baseline wheelをfresh initして生成し、I392-S10でprovider assetとしてcommitする。per-file identity、obsolete files、multiple versionsを追加しない。fixture generation commandとbaseline wheel hashをreportへ記録する。

## 9. Public result mapping

### I392-D-015 — CLI adapter

`init`/`update` successはcurrent formatを維持する。

```text
spec-dock: ok (init) -> <resolved target>
spec-dock: ok (update) -> <resolved target>
```

Block/partial/errorはstderrへ`error: <code>: <message>`を出力する。parser errorはargparse exit 2。

Uninstall JSON schema_version 1:

```json
{
  "schema_version": 1,
  "target": "<safe target label>",
  "mode": "dry-run",
  "apply": false,
  "specs_mode": null,
  "status": "planned",
  "code": "uninstall-planned",
  "mutation_started": false,
  "phase": "preflight",
  "last_completed_phase": "preflight",
  "retry_command": null,
  "failed_paths": [],
  "pending_paths": [],
  "summary": {},
  "actions": [],
  "guidance": [],
  "errors": []
}
```

`--keep-specs`は`specs_mode="keep"`をechoするがactions/resultはdefaultと同一。`--remove-specs`は`specs_mode="remove"`、status error、code `spec-history-purge-removed`、mutation_started false、actions empty、exit 2。

Sanitized blocked/partial payloadはtarget absolute pathやconsumer file contentを出力しない。retry commandはsame-operation/same-candidateがrepresentableな場合だけ返す。

## 10. Test architecture

### I392-D-016 — Exact final test paths

New/replacement tests:

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

Retire after successor proof:

```text
tests/unit/infra/test_managed_distribution.py
tests/unit/infra/test_init_update.py
tests/cli_runtime/test_distribution_cutover.py
tests/integration/test_epic_00343_distribution.py
```

`test_init_update.py`のnon-lifecycle asset/package parity assertionsは`test_provider_assets.py`へ移し、traceを維持してからold fileを削除する。

`tests/provider_test_ownership.json` schema:

- `schema_version`
- `canonical_roots`
- `canonical_exclusions`
- `macos_delta_roots`
- `contracts[]`: `contract_id`, `requirement_ids`, `owner_nodeid`, `lane`, `representative_fault`
- duplicate contract ID、duplicate owner tuple、missing node、lane intersectionをrejectする。

Root `tests/conftest.py`はfinal stateで削除する。test fixturesが必要ならlocal conftestへ配置するが、lane classification、ledger evaluation、policy skip hookを再導入しない。

### I392-D-017 — Tripwire harness

`sitecustomize.py`:

- environmentからtarget rootとevent output FD/pathを取得する。
- startup loaded sentinelを出力する。
- `sys.addaudithook`でtarget-scoped Python mutationをraise-before-callする。
- `ctypes.CDLL`をproxyし、`renameat2`/`renameatx_np` symbol wrapperを返す。
- native pathはdirfdとC stringから解決し、target scopeの場合underlying call前にeventを記録してraiseする。
- target外のvenv/cache/evidence writeは許可する。
- read operationをblockしない。

Testsはold wheelをisolated venvへinstallし、new workspaceとは別processで実行する。positive control failureはtest infrastructure failureであり、old command success扱いにしない。

## 11. Provider gate

### I392-D-018 — `scripts/provider_gate.py`

Subcommands:

- `build`: `uv build --sdist --wheel`をexactly once呼び、candidate manifestを作る。
- `verify-artifact`: source SHA、filename、size、SHA-256、build countを検査する。
- `verify-node-ownership`: ownership JSON、collection、lane intersection、duplicateを検査する。
- `canonical`: built wheelをisolated environmentへinstallし、one `python -m pytest` process、no `-n`でcanonical rootsを実行する。
- `macos-delta`: same wheelをinstallし、macOS pathsだけを実行する。
- `qualify`: same manifest/wheelで20 sequential canonical runsを行い、first 5 budget、all 20 flake/retryを評価する。
- `summarize`: machine-readable evidence JSONを生成する。

Final `.github/workflows/provider-ci.yml`:

- pull_request + explicit workflow_dispatch qualification input
- static analysis job
- Linux provider-tests job: one build、artifact verification、canonical、sdist smoke、upload
- macOS delta job: download same artifact、digest verify、delta only
- provider-gate aggregate job
- no main push trigger
- no shard matrix
- no candidate rebuild on macOS

`Makefile`は`lint`に加え`provider-test`、`provider-qualify`をthin wrapperとして持つ。`scripts/static_analysis/run.sh`は`scripts/provider_gate.py`をanalysis targetへ追加する。

## 12. Forward-fix and rollback

- Public cutover前: PRをmergeしない、またはdormant successorだけをrevertできる。
- Public cutover後: runtime old-engine fallback禁止。fail-closed patchまたはhuman-reviewed revert。
- Partial consumer operation: same operation/candidate rerun。automatic rollbackなし。
- CI setting: before captureへhumanがrestoreできるようexact JSONを保存。
- Consumer data: rollback/recoveryのために変更しない。
- Acceptance未達: 同じ#392で修正し、new Issueへ送らない。

## 13. Design traceability

| Requirement | Design |
|---|---|
| I392-RQ-001 | I392-D-018とIssue plan I392-S00 |
| I392-RQ-002〜003 | I392-D-002〜003、007〜009 |
| I392-RQ-004〜005 | I392-D-004、006、010 |
| I392-RQ-006 | I392-D-005、008 |
| I392-RQ-007 | I392-D-007、010 |
| I392-RQ-008〜013 | I392-D-011〜013 |
| I392-RQ-014〜015 | I392-D-014、017 |
| I392-RQ-016〜018 | I392-D-011、015 |
| I392-RQ-019 | I392-D-016〜017 |
| I392-RQ-020 | I392-D-018 |
