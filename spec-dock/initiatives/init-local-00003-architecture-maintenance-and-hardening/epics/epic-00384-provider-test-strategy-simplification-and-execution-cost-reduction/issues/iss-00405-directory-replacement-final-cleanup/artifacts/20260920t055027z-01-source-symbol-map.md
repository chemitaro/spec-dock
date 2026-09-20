---
種別: artifact
ID: "20260920t055027z-01"
タイトル: "Source Symbol Map"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-09-20"
親: ["iss-00405"]
template: "blank"
authority: "evidence"
derived_from: []
reflected_to: []
---

# iss-00405 Source / Symbol Map

- repository: `chemitaro/spec-dock`
- branch: `iss-00405-directory-replacement-final-cleanup`
- code investigation baseline SHA (not adopted specification SHA): `457faf31df8840d1f2fc87417d297dc318903fbe`
- tree: `c28295207416e186cd2c1a0c903a84bd7debc6bb`
- status: implementation未実行

The table describes the pre-implementation code baseline. Adopted specifications are the canonical R/D/P and disposition CSV at the implementation-start clean HEAD, matched to its independent review evidence.

## Exact baseline blobs

| repository path | blob SHA | current role |
|---|---|---|
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py` | c7d2f6ca4717862cf400a335bf853cb013396a49 | types |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py` | 6316439db13392620e2b6bd7fb4501e73f7b57a9 | GitGateway protocol |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py` | a857f6e3a2193b12e6b9b2f3118a9590a13ba36c | checkout consumer/global witness |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_lifecycle.py` | 875f343b29ecfd39dd051a779fa00410a4dee7a5 | issue start orchestration |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py` | 788da674368af73cd08f9b5ef3cae79715825003 | target/source binding |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py` | 9d7053a40457521278c10fa0302c6a16cf69a48a | adapter |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py` | 05d87aa5e5b2af2e449ea7b6c75f10bab3f282bf | Git execution/capability/materializer |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_helper.py` | cf81dc8c6447f6a95935d420d44324c4a16483b1 | current lease helper |
| `src/spec_dock/installer.py` | 83afeba1cc59c868bb053d039f7e29f23245c1c2 | six-directory installer |

## Consumer graph

```text
issue start
└─ application.issue_lifecycle.issue_start
   └─ application.set_active.checkout_active_target
      ├─ GitGateway.require_clean_working_tree                  KEEP
      ├─ GitGateway.resolve_commit/current_head_or_none        KEEP
      ├─ GitGateway.pinned_checkout                            DELETE
      │  ├─ infra.git_cli.assess_capabilities                  DELETE
      │  └─ infra.git_cli._run_git_write                       DELETE
      ├─ global _LAST_PINNED_CHECKOUT                          DELETE
      └─ GitGateway.checkout_fixed_ref                         ADD

worktree create
└─ application.worktree.worktree_create
   ├─ _pin_worktree_source                                     REWRITE: current HEAD only
   ├─ _open_source_shared                                      DELETE
   ├─ _open_source_directory_for_filesystem_probe              ADD: no flock/no child inheritance
   ├─ _open_created_exclusive_worktree                         KEEP
   ├─ GitGateway.add_worktree_pinned                           RENAME/REWRITE
   ├─ GitGateway.materialize_worktree                          REWRITE: target_fd only
   ├─ GitGateway.publish_worktree_entrypoint                   KEEP signature target_commit rename
   └─ _open_nonlocking_worktree_bound_to_exclusive             KEEP

worktree remove
└─ application.worktree.worktree_remove
   ├─ inventory/selector/containment                           KEEP
   ├─ _open_exclusive_existing_worktree                        KEEP
   ├─ _open_source_shared                                      DELETE
   ├─ require_clean_working_tree(target)                       KEEP
   ├─ GitGateway.remove_worktree                               REWRITE: target_fd only/direct Git
   └─ _remove_original_worktree_directory                      KEEP
```

## Interface delta

### DELETE

- `GitCapabilityAssessment`
- `PinnedCheckout`
- `GitGateway.checkout_branch`
- `GitGateway.create_and_checkout_branch`
- `GitGateway.assess_capabilities`
- `GitGateway.pinned_checkout`
- `GitGateway.verify_pinned_checkout`
- `git_cli._WRITING_GIT_COMMANDS`
- `git_cli._run_git_write`
- `git_cli.assess_capabilities`
- `git_cli.pinned_checkout`
- `git_cli.verify_pinned_checkout`
- `set_active._LAST_PINNED_CHECKOUT`
- `set_active.last_pinned_checkout`
- `worktree._open_source_shared`
- every `source_fd` / `lease_fd` parameter used only for provider repository coordination

### ADD / REWRITE

```python
# application/ports.py
class GitGateway(Protocol):
    def checkout_fixed_ref(
        self,
        repo_root: Path,
        *,
        branch: str,
        target_commit: str,
        checkout_kind: Literal["existing", "new"],
    ) -> None:
        pass

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

```python
# infra/git_cli.py
def _run_git_in_bound_cwd(
    command: list[str],
    *,
    cwd_fd: int,
) -> subprocess.CompletedProcess[str]:
    pass
```

## Binding taxonomy

| binding | representation | lifecycle | child inheritance | disposition |
|---|---|---|---|---|
| issue checkout source commit | full Git object ID `target_commit` | operation local | none | KEEP |
| worktree source filesystem probe | unlocked no-follow directory FD | same-filesystem checkまで | none | KEEP/SPLIT |
| worktree target | no-follow directory FD + EX flock + dev/inode | add/materialize/hook or remove/cleanup完了まで | helperへcwd FDだけ | KEEP |
| consumer hook cwd | nonlocking FD + expected dev/inode | terminal handoff完了まで | wrapper childへbound cwd | KEEP |
| explicit artifact source | `GuardedExplicitFileSource` descriptor | publication完了まで | publisher内部 | KEEP（別責務） |
| provider repository shared lease | root FD + SH flock | all Git write | helper/Git child | DELETE |
| provider generation witness | dataclass/global | checkout後再認証 | N/A | DELETE |

## Search completion criteria

Active sourceとdogfood runtimeの両方で次を確認します。

```bash
rg -n 'GitCapabilityAssessment|PinnedCheckout|assess_capabilities|pinned_checkout|verify_pinned_checkout|runtime-generation-drift|_LAST_PINNED_CHECKOUT|last_pinned_checkout|lease-retaining|--lease-fd' \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime \
  spec-dock/scripts/spec_dock_runtime
```

期待結果は0件です。ただし`GuardedExplicitFileSource`、create/import lock、worktree target `LOCK_EX`は削除対象ではないため、一般語`lease`/`flock`の全件0を要求しません。
