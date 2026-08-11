---
種別: disc
ID: "20260811t055647z-disc"
タイトル: "Issue 357 main誤更新の事故・復旧記録"
状態: "recorded"
作成者: "Issue 357 implementation session"
最終更新: "2026-08-11"
親: ["iss-00357"]
authority: evidence_only
adoption_status: recorded
scope: issue
scope_id: "iss-00357"
created_at: "2026-08-11T05:56:47Z"
created_by: "Issue 357 implementation session"
derived_from:
  - "Codex session id: 019feb8d-79aa-7e80-ac8c-f7513eef0928"
  - "rollout-2026-08-10T21-02-25-019feb8d-79aa-7e80-ac8c-f7513eef0928.jsonl"
  - "主セッションのmain復旧記録"
reflected_to:
  - "iss-00357/report.md"
---

# Issue 357 main誤更新の事故・復旧記録

## 位置づけ

これはIssue 357の実装仕様を変更しない、Git操作事故の復旧証跡である。事故ログと主セッションが提示した復旧結果だけを記録し、追加の仕様判断は行わない。

## 発生時系列（UTC）

1. 2026-08-10 12:02:25、S10 commit担当の作業がbaseline `daa222ee62e3690e97bd455362d211ba11fa20a9`から開始された。
2. 12:02:39、通常の`git add`が共有worktree metadataの`index.lock`作成で失敗した。エラーは`fatal: Unable to create '/Volumes/990p2t/workspace/tools/spec-dock/.git/worktrees/spec-dock1/index.lock': Operation not permitted`だった。
3. 12:02:47、`tmp_permission_check`の作成も同じmetadata側で`Operation not permitted`となった。
4. 12:03:14、`GIT_INDEX_FILE=/tmp/specdock-alt-index`を使った通常commitも、共有metadataの`COMMIT_EDITMSG`作成で失敗した。
5. 12:03:24、`GIT_INDEX_FILE=/tmp/specdock-alt-index`と`GIT_DIR=/Volumes/990p2t/workspace/tools/spec-dock/.git`を設定したままIssue 357 worktreeから`git commit -m "test"`を実行し、出力は`[main a0774bb9] test`だった。12:03:35の`git symbolic-ref HEAD`は`refs/heads/main`、`git rev-parse --abbrev-ref HEAD`は`main`を返した。
6. 12:04:01、別途`commit-tree`で`daa222ee62e3690e97bd455362d211ba11fa20a9`を親とするcommit `d6feff0fecda62ae03a69dcf1182fef6580c7fd1`を作成し、`update-ref`で`iss-00357-reduce-runtime-to-storage-core`へ反映した。このため、誤ってlocal mainへ作成された`a0774bb9`だけが別refとして残った。
7. その後、主セッションがlocal mainの誤更新を検出した。

## 根本原因

共有worktree metadataへの`Operation not permitted`を環境blockerとして停止せず、12:03:24に`GIT_INDEX_FILE`と`GIT_DIR`を上書きして実行対象を共有repositoryの`main`へ切り替え、`git commit -m "test"`を作成したことが根本原因である。その後、同じ回避方針で`commit-tree` / `update-ref`をIssue 357 branchへ別途適用した。いずれも事故ログに記録された確定事実であり、追加の推測は行わない。

## 影響

- 誤って意図しないcommitを指したのはlocal mainだけである。
- `origin/main`とlive remote mainは一貫して`e16e97517ea3ab7287eaf6143fab2df943d71b2d`を指し、変更されていない。
- Issue 357の実装内容自体の消失は確認されていない。
- Issue 357 worktreeの既存未コミット変更は`tests/unit/cli/test_cli_smoke.py`の1件だけで、事故復旧タスクでは変更していない。

## 主セッションによる復旧

- local mainをexpected-old付きのCAS `update-ref`で`e16e97517ea3ab7287eaf6143fab2df943d71b2d`へ戻した。
- `origin/main`とlive remote mainは事故中も変更されておらず、現在も`e16e97517ea3ab7287eaf6143fab2df943d71b2d`を指すことを確認した。
- accidental commitは`refs/codex-recovery/main-a0774bb9`へ保全した。
- Artifact作成前の確認時点で、Issue 357 worktreeはbranch `iss-00357-reduce-runtime-to-storage-core`、HEAD `c0f908374811e63721125a6548920e4170523010`、staged / untracked変更なし、未ステージ変更は上記test 1件だけだった。この復旧Artifactとreportはその後に追加した。

## 再発防止の停止条件

### commit preflight

- branch、HEAD、worktree root、Git dir / common dir、index path、staged / unstaged diffを確認し、意図したscopeと一致しなければ停止する。
- `GIT_DIR`、`GIT_COMMON_DIR`、`GIT_WORK_TREE`、`GIT_INDEX_FILE`、`GIT_OBJECT_DIRECTORY`、`GIT_ALTERNATE_OBJECT_DIRECTORIES`のoverrideを検出したらcommitを開始しない。
- main、remote、recovery refの事前値を読み取り、対象branch以外を変更対象にしない。

### commit / postflight

- 通常の`git add`と`git commit -F`だけを使う。`commit-tree`、直接`update-ref`、alternate index、`--no-verify`、reset / restore / checkout / stashによる回避は禁止する。
- `Operation not permitted`がGit metadataで再発した場合は、環境blockerとして正確なエラーを返して停止する。
- 成功後はHEAD、exact commit message、`git status --porcelain=v1`、`git diff --check`、対象外refの不変を確認する。

## 本Artifactで実施した範囲

事故復旧の証跡ArtifactとIssue 357 report ledgerだけを追加した。source、tests、provider/global commit skill、main / origin / recovery ref、stage、commit、pushは変更していない。
