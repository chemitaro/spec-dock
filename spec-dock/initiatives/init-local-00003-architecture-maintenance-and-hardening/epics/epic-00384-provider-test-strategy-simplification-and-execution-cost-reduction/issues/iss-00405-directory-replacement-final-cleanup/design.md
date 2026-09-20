---
種別: 設計書（Issue）
ID: "iss-00405"
タイトル: "Directory Replacement Final Cleanup"
関連GitHub: ["#405"]
状態: "仕様候補draft"
最終更新: "2026-09-20"
依存: ["requirement.md"]
親: ["epic-00384", "init-local-00003"]
---

# iss-00405 Directory Replacement Final Cleanup — 設計

詳細: [Design Guide](../../../../../../docs/authoring/design.md)

補助: [Source / Symbol Map](artifacts/20260920t055027z-01-source-symbol-map.md)

> 本文は実装前の設計候補です。実装・テスト・独立レビュー・mergeは未完了です。

## 設計目標

1. provider世代認証を通常Git操作から完全に外します。
2. source commit bindingとtarget directory bindingを別の責務として表現します。
3. worktreeのno-follow/EX/inode、safe materialization、entrypoint-last、consumer hook bound cwdを最小構成で保持します。
4. node/create/importのdata-operation safetyとprivacy/security回帰を変更しません。
5. installerの6directory順次置換を変更せず、欠落しているfailure observationだけを追加します。
6. tests/docs/harnessをcurrent authorityへ揃えます。

## Current / Target

| 観点 | Current | Target |
|---|---|---|
| issue checkout | broad `assess_capabilities`がhooks/fsmonitor/sparse/attributes/full treeを拒否し、`PinnedCheckout`を二重検証 | clean check、fixed target commit、native checkout、branch/HEAD一致だけ |
| Git write | `_run_git_write`がrepository root FDへ`LOCK_SH`を取り全writeを`git_helper`へ委譲 | ordinary checkout/add/removeはdirect subprocess。target cwdが必要な`read-tree`だけhelperを使用 |
| worktree source | source root shared lock/FDをGit childへ継承 | current HEADをcommit IDへ固定。unlocked source FDはsame-filesystem probeだけに使用し、childへ渡さない |
| worktree target | no-follow/EX/device-inodeとtarget FDを保持 | 同じ安全境界を保持。target FDをcreate/remove/materialize/handoffの親処理中に保持 |
| generation witness | module global `_LAST_PINNED_CHECKOUT`と`runtime-generation-drift` | 削除。operation内部のpostconditionで完結 |
| installer | 6directory順次rmtree/copy、version-last、nontransactional | Product実装は原則KEEP。中間copy failure successorを追加 |
| docs/tests | 旧保証、marker特例、dead selector、旧責務名 | current 6directory/安全境界へ統一 |

## 主要設計判断

### DES-405-01 `git_helper.py`は削除せずtarget-bound cwd executorへ縮退する

「helperを残すか不要なら削除する」という分岐は残しません。`git_helper.py`は次の一用途だけに残します。

- `git read-tree --reset <target_commit>`を、既にno-followでopenしexclusive lockを保持しているworktree target directory descriptorをcwdとして実行する。

新しいprivate interfaceは次です。

```python
def _run_git_in_bound_cwd(
    command: list[str],
    *,
    cwd_fd: int,
) -> subprocess.CompletedProcess[str]:
    pass
```

親processは`cwd_fd`の`st_dev/st_ino`を取得し、helperへ次だけを渡します。

```text
python -m spec_dock_runtime.infra.git_helper \
  --cwd-fd <fd> \
  --expected-device <st_dev> \
  --expected-inode <st_ino> \
  -- <git-command-argv>
```

helperはdirectory/device/inodeを再検証して`os.fchdir(cwd_fd)`し、その後helper側のFDをcloseしてからchildを待ちます。Git childへFDを再継承しません。repository rootを自動openせず、`flock`せず、provider generationを認証せず、`lease-fd`という引数・error語彙を持ちません。module名はgenericでありrenameによる配布差分を増やさないため維持します。

`_run_git_in_bound_cwd`はcurrent `_runtime_scripts_root()`と`_helper_environment()`を保持し、次の形でhelper module provenanceをprovider runtimeへ固定します。

```python
subprocess.run(
    helper_argv,
    cwd=str(_runtime_scripts_root()),
    env=_helper_environment(),
    pass_fds=(cwd_fd,),
    capture_output=True,
    text=True,
    check=False,
)
```

`pass_fds`はparentからhelperへbound cwdを渡す一段だけに使用します。consumer worktree内の同名moduleをimportしないことをsuccessor testで固定します。

### DES-405-02 ordinary Git checkoutはfixed-ref direct executionにする

`GitGateway`へ次を追加します。

```python
def checkout_fixed_ref(
    self,
    repo_root: Path,
    *,
    branch: str,
    target_commit: str,
    checkout_kind: Literal["existing", "new"],
) -> None:
    pass
```

実装順序は次です。

#### existing branch

1. `git update-ref refs/heads/<branch> <target_commit> <target_commit>`をdirect subprocessで実行し、解決後のbranch refがraceで変わっていないことをCAS no-opで確認します。
2. current branchが異なる場合だけ`git switch <branch>`を実行します。
3. `current_branch_or_none(repo_root) == branch`かつ`current_head_or_none(repo_root) == target_commit`を確認します。

#### new branch

1. `git switch -c <branch> <target_commit>`をdirect subprocessで実行します。
2. branch/HEADが期待値と一致することを確認します。

`checkout_fixed_ref`はhooks、fsmonitor、sparse、attributes、submodule、別worktreeを事前に独自分類しません。Git自身が失敗した場合はnative stderrを含む`RuntimeError`へ変換します。

### DES-405-03 checkout consumerからgeneration witnessを除去する

`application/set_active.py`は次の形へします。

```text
checkout_active_target
  -> check_ref_format_branch
  -> require_clean_working_tree
  -> existing? resolve_commit(refs/heads/<branch>) : current_head_or_none
  -> checkout_fixed_ref
  -> return BranchDecision
```

以下は削除します。

- `_LAST_PINNED_CHECKOUT`
- `last_pinned_checkout`
- `PinnedCheckout`
- `GitCapabilityAssessment`
- `assess_capabilities`
- `pinned_checkout`
- `verify_pinned_checkout`
- `runtime-generation-drift` error contract

`issue_lifecycle.issue_start`はcheckout成功後にwitnessを取り出して再検証しません。`target/active guard → dependency readiness → checkout → active state commit → post-sync`の順序は変更しません。

### DES-405-04 worktree source probeとtarget bindingを分離する

#### source側

`_open_source_shared`は削除し、次のunlocked probeへ置換します。

```python
def _open_source_directory_for_filesystem_probe(repo_root: Path) -> int:
    return _open_directory_no_follow(repo_root)
```

用途は`_require_same_filesystem(source_probe_fd, target_fd)`だけです。`flock`しません。Git childへ渡しません。filesystem一致確認後にcloseします。source contentのidentityは`target_commit`で固定します。

#### target側

以下はそのまま保持します。

- `_open_directory_no_follow`
- `_open_created_exclusive_worktree`
- `_open_exclusive_existing_worktree`
- `_verify_worktree_path_binding`
- `_open_nonlocking_worktree_bound_to_exclusive`
- `_remove_original_worktree_directory`
- target FDに対する`LOCK_EX | LOCK_NB`

`target_fd`はworktree add/materialize/entrypoint publication/consumer hook bindingが完了するまで親processが保持します。removeではGit removeとpost-remove cleanupが完了するまで保持します。

### DES-405-05 worktree Git interfaceをfixed commitとtarget FDへ縮退する

`GitGateway`のworktree interfaceは次へ変更します。

```python
def add_worktree_at_commit(
    self,
    repo_root: Path,
    *,
    path: Path,
    branch: str,
    target_commit: str,
    target_fd: int,
) -> None:
        pass

def materialize_worktree(
    self,
    repo_root: Path,
    *,
    path: Path,
    target_commit: str,
    target_fd: int,
) -> tuple[tuple[str, tuple[int, int]], ...]:
        pass

def remove_worktree(
    self,
    repo_root: Path,
    *,
    path: Path,
    force: bool,
    target_fd: int,
) -> None:
        pass
```

- `add_worktree_at_commit`はpath bindingをGit前後に確認し、`git worktree add --no-checkout -b <branch> <path> <target_commit>`をdirect subprocessで実行します。
- `materialize_worktree`は`_run_git_in_bound_cwd(["git", "read-tree", "--reset", target_commit], cwd_fd=target_fd)`を使用します。
- `remove_worktree`はtarget binding確認後にdirect subprocessで`git worktree remove`を実行します。application側のtarget FDとpost-remove inode cleanupは維持します。
- 全interfaceから`source_fd`と`lease_fd`を削除します。
- `pinned_commit`は旧generation語彙との混同を避けて`target_commit`へ統一します。

### DES-405-06 materializer固有のsecurity checkを保持する

broad full-tree gateを削除しても、次のlocal checkは削除しません。

| check | 所有symbol | 理由 |
|---|---|---|
| pathがrelative/NUL-free/`..`なし | `_relative_components`, `_tree_entries` | target外write防止 |
| created directory witness | `_open_or_create_directory`, `_open_relative_parent` | foreign descendantとinode replacement拒否 |
| regular file exclusive create/mode/content | `_materialize_regular`, `_verify_regular_entry` | overwrite・link差替え防止 |
| symlink target safety | `_validate_link_target`, `_materialize_symlink` | target外escape防止 |
| submodule拒否 | `_materialize_tree_entry` | unsupported objectを公開しない |
| entrypoint no-replace/final publication | `_publish_entrypoint`, `publish_worktree_entrypoint` | partial treeをruntimeとして公開しない |
| HEAD/clean postcondition | `_materialize_and_verify_worktree` | fixed commit materialization確認 |

full-tree attributes、hooks、fsmonitor、sparse、autocrlf/eolのprovider generation gateは削除します。Git treeから実際に書くentry単位の安全検査は保持します。

### DES-405-07 data-operation lockとprivacy境界は無変更とする

`create_node`/`import_node`のcreate lock、`GuardedExplicitFileSource`、binary artifact publisher、active state rollback、GitHub URL redactionは変更対象外です。`lease`という一般語を一括検索置換しません。削除対象はprovider repository shared leaseだけです。

### DES-405-08 installerはProduct変更なしを第一選択とする

`src/spec_dock/installer.py::install`の順序は変更しません。

```text
preflight target/source
→ docs delete/copy
→ templates delete/copy
→ system delete/copy
→ scripts delete/copy
→ skill spec-dock delete/copy
→ skill grill-with-docs delete/copy
→ version unlink/write
```

新しいmid-copy failure testは4番目の`_copy`を具体的な注入点とします。これはProduct requirementとして「4番目」を固定するのではなく、前半成功・中間partial・後半未着手を一つのtestで同時観測するためのtest designです。

注入関数は1〜3回目をreal `_copy`へ委譲し、4回目にdestination directoryと`partial.txt`を作って`OSError`を送出します。期待観測は次です。

- command non-zero
- docs/templates/systemはsourceと一致
- scriptsはpartialでsourceと不一致
- 2 skill dirsは旧stale sentinelを保持
- versionは事前に書いた`old-version\n`のまま
- `spec-dock/initiatives/**`等のdata sentinel不変
- patch解除後の同じupdateで全6tree byte/mode一致、partial/stale不存在、current version

現行実装が最初からpassする場合はProduct codeを変更しません。

## 責務・Interface変更表

| path | symbol | 処置 | Target responsibility |
|---|---|---|---|
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py` | `GitCapabilityAssessment`, `PinnedCheckout` | DELETE | provider capability/generation witness型を削除。`WorktreeCreateResult.bound_*`, `GuardedExplicitFileSource`, `DirectoryWitness`相当のtarget/data型は保持。 |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py` | `GitGateway` | REWRITE | `checkout_fixed_ref`と`add_worktree_at_commit`へ置換。`assess_capabilities`, `pinned_checkout`, `verify_pinned_checkout`, old checkout methods、`source_fd`引数を削除。 |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py` | `_GitGateway` | REWRITE | Protocolと同じadapter差分。provider-first変更後dogfoodへ同期。 |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py` | `checkout_active_target` | REWRITE | clean check→target commit解決→`checkout_fixed_ref`。global witnessを削除し、`BranchDecision`だけを返す。 |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_lifecycle.py` | `issue_start` | REWRITE | `last_pinned_checkout`再検証を削除。guard/deps→checkout→active→sync順は保持。 |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py` | `_run_git_write` / capability / checkout | REWRITE/DELETE | shared flockとbroad gateを削除。direct fixed-ref Gitとtarget-bound cwd executorへ分離。 |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_helper.py` | module全体 | REWRITE | provider lease helperではなく単一bound cwd FDを検証してGit childを実行する限定helperへ縮退。 |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py` | create/remove/materialize flow | REWRITE | unlocked source filesystem probeとtarget EX bindingを分離。source shared flockを削除しtarget safetyを保持。 |
| `src/spec_dock/installer.py` | `install` | KEEP | Product behaviorは維持。新testがfailした場合だけ契約内の最小修正。 |

## 呼出し順

### issue start

```text
command wrapper
  → issue_lifecycle.issue_start
    → target/active guard
    → check_deps
    → set_active.checkout_active_target
      → require_clean_working_tree
      → resolve target_commit
      → GitGateway.checkout_fixed_ref
        → native Git operation
        → branch/HEAD postcondition
    → set_active
    → post_mutation_sync
```

### worktree create

```text
worktree_create
  → clean/named branch/worktree inventory
  → target_commit = current HEAD
  → create target directory + target EX FD + inode witness
  → open unlocked source probe FD; same-filesystem確認; close source probe
  → verify target path binding
  → add_worktree_at_commit(path=worktree_path, target_commit=target_commit, target_fd=target_fd)
  → materialize_worktree(path=worktree_path, target_commit=target_commit, target_fd=target_fd)
     → target-bound cwd helperでread-tree
     → safe entry-by-entry materialization
  → verify HEAD/clean
  → publish entrypoint last
  → exclusive targetと同inodeのnonlocking bound cwd FDを取得
  → ConsumerHookRequestへdevice/inode付きでhandoff
```

### worktree remove

```text
worktree_remove
  → inventory/selector/blocker/containment
  → inventory refresh
  → target EX FD
  → bound inventory再解決 + target inode確認
  → dirty/untracked拒否
  → GitGateway.remove_worktree(path=worktree_path, force=force, target_fd=target_fd)
  → original inodeだけcleanup
```

## data / failure contract

### issue checkout

| failure | mutation境界 | observable result | recovery |
|---|---|---|---|
| dirty tree | Git mutation前 | non-zero、active/syncなし | commit/stash後に再実行 |
| target commit unavailable | Git mutation前 | non-zero、active/syncなし | ref/HEADを修復 |
| native switch/create failure | Git内部 | non-zero、active/syncなし、native detail保持 | branch/HEADを確認して再実行 |
| branch/HEAD mismatch | Git後 | non-zero、active/syncなし | `git status`, `git branch --show-current`, `git rev-parse HEAD`で確認 |
| active write failure | checkout後 | branch side effectを明示、active rollback、syncなし | existing guidanceを維持 |

### worktree

| failure | 保持する性質 |
|---|---|
| target busy/unavailable | Git mutation前にblockし、別targetを触らない |
| cross-filesystem | Git mutation前に拒否するcurrent contractを維持 |
| worktree add failure | target/branch/recordのpartial stateをerror payloadへ記録し、自動retry/cleanupしない |
| materialization failure | entrypoint未公開、partial targetを保持、明示的recoveryへ委ねる |
| target path replacement | device/inode mismatchを検知し、replacementをcleanupしない |
| hook failure | worktree create自体のresultへbest-effort `detection_failed`として記録 |

### installer

| failure | contract |
|---|---|
| source missing / target symlink | delete前に拒否 |
| middle copy I/O failure | non-zero、混在許容、version旧値、data不変 |
| retry | external installerを最初から再実行し6tree一致へ収束 |
| fresh init partial | 不完全scaffoldを利用者が別途保全してfresh init。自動削除なし |

## 変更対象

### provider-first source

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_lifecycle.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_helper.py`
- `src/spec_dock/assets/spec_dock/docs/README.md`
- `src/spec_dock/assets/spec_dock/scripts/README.md`

### tests/harness

- `tests/cli_runtime/test_generation_checkout.py`
- `tests/cli_runtime/test_runtime_handoff.py`
- `tests/cli_runtime/test_worktree.py`
- `tests/cli_runtime/test_worktree_lifecycle_coordination.py`
- `tests/cli_runtime/test_distribution_cutover.py`
- `tests/cli_runtime/conftest.py`
- `tests/cli_runtime/harness.py`
- `tests/unit/infra/test_directory_installation.py`
- `tests/unit/infra/test_init_update.py`
- `tests/unit/infra/conftest.py`

### docs / dogfood / parent

- `README.md`
- `spec-dock/docs/README.md`（provider mirror）
- `spec-dock/scripts/README.md`（provider mirror）
- `spec-dock/scripts/spec_dock_runtime/**`（provider mirror）
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/plan.md`
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/report.md`

`report.md`のIssue版はCodexが実測後に記録するため、この仕様packには含めません。

## testability

### F001の正のsuccessor

`TestCheckoutSafety::test_issue_start_accepts_clean_repo_without_provider_capability_gate`を次の5 caseでparameterizeします。

| case | setup | expected |
|---|---|---|
| `executable-hook` | `.git/hooks/post-checkout`を実行可能にし、引数をrepository外logへ記録して`exit 0` | hookが実行され、独自capability errorなし、checkout/active/sync成功 |
| `fsmonitor` | repository外の実行可能hookを`core.fsmonitor=<absolute path>`へ設定。hookはv2応答として`printf 'token\0'`を返し、changed path 0件 | clean checkとcheckoutがnative Gitで成功し、独自capability errorなし |
| `diff-attribute` | tracked `.gitattributes`へ`spec-dock/docs/README.md diff=custom`を追加してcommit | checkout/active/sync成功 |
| `merge-attribute` | tracked `.gitattributes`へ`spec-dock/docs/README.md merge=custom`を追加してcommit | checkout/active/sync成功 |
| `sparse-checkout` | `git sparse-checkout init --no-cone`後に`git sparse-checkout set '/*'`を実行し、current workspace全体を含めたまま`core.sparseCheckout=true`にする | checkout/active/sync成功 |

各caseはsetup完了後に`git status --porcelain`が空であることを先にassertします。Git自身が操作可能な無害なconfigurationだけを使い、native Git failureをprovider gate removalの失敗と混同しません。first runがGreenなら`covered-existing`、broad gate由来でRedなら予定したimplementation driverとして記録します。

### F004のsuccessor

`test_update_mid_copy_failure_is_nontransactional_and_rerunnable_without_touching_data`は前述の4th-copy注入を使用します。現行11件のpre-implementation passとは別node内容として実装後に再実行します。

### negative assertionの基準

- current command/catalogを正に確認し、他の強いtestで代替できないarchitecture boundaryはKEEPします。
- retired filename単独のabsenceで、exact catalog equalityに包含されるものはDELETEします。
- data/security boundaryを守るnegative testは、provider leaseと構造が似ていてもKEEPします。

## 移行・互換性・rollback

### migration

persistent data migrationはありません。Python internal interfaceとtest namesのhard cutoverです。公開CLI command/option、node metadata schema、active manifest、worktree JSON payload、installer target setは変更しません。

### compatibility

- existing/new issue branch behaviorは維持します。
- provider generation差異はcheckout阻害条件にしません。
- hooks/fsmonitor/attributes/sparseは独自gateから外れますが、Git自身のエラーは維持します。
- worktree JSON/error code、consumer hook result、installer exit semanticsは原則維持します。
- internal symbol互換aliasは追加しません。old types/ports/adaptersは同一commitでconsumerごと削除します。

### rollback

checkpoint commit単位でrevertします。F001 sourceだけをtest rewriteから分離して途中mergeしません。dogfood sync後に問題が出た場合は、provider source commitをrevertしてから外部installer updateを再実行し、provider/dogfood parityを戻します。旧provider generation機構を部分的に復活させるforward fixは行いません。

## security / privacy / operability

### 残るsecurity check

- Git clean precondition
- fixed commit/ref and branch/HEAD postcondition
- worktree target no-follow/EX/device-inode
- same-filesystem preflight
- materializer path/symlink/submodule/foreign-directory/file-mode checks
- entrypoint-last
- consumer hook bound cwd
- create/import lock/race/ownership
- explicit file source/publication guard
- credential redactionとcontent-free failure

### 撤去するcheck

- provider repository root shared flock
- provider generation witness/global state
- hooks/fsmonitor/sparse/attributes/autocrlf/eol/full treeのbroad capability gate
- generation drift再認証
- provider slot marker/digest/resume guarantee

### operability

repository-wide shared lockによる不要なbusy failureがなくなります。worktree target busyはtarget EX lockとして残ります。installer update中command停止は運用契約のままで、自動排他へ戻しません。

## risk

| risk | mitigation | stop condition |
|---|---|---|
| broad gate削除でunsafe materializationまで消す | materializer固有checkをsymbol単位でKEEPしfocused testを先に固定 | entrypointがpartial treeで公開される場合停止 |
| helper縮退でtarget cwd bindingが失われる | helperの唯一用途とFD/dev/inode検査をtest化 | path-based `cwd`へ戻す必要が出たらdesign再審議 |
| source lock削除でcross-filesystem判定も消す | unlocked source probe FDをsame-filesystemだけに保持 | current cross-filesystem testが維持できない場合停止 |
| test削除でsecurity regressionを失う | exact node dispositionとsuccessorをCSVで固定 | successorなしでKEEP contractが消える場合停止 |
| dogfood updateがdataへ触る | clean checkpoint後にprotected path diffを前後比較 | `spec-dock/initiatives`等へ予期しない差分が出たら停止 |
| docsが旧保証を復活 | active source scanとprovider/dogfood equality | current docsに旧保証語が残れば完了不可 |

## 未決事項

owner判断が必要な設計分岐はありません。cross-filesystem対応追加、same-EUID adversary保証、atomic installer、公開CLI変更は明示的に対象外です。実装中にこれらが必要になった場合は推測せずRequirementへ戻します。
