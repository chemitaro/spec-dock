---
種別: disc
ID: "20260811t155719z-disc"
タイトル: "PR Repair Unit R357-HL1"
状態: "completed"
作成者: "Issue 357 implementation session"
最終更新: "2026-08-12"
親: ["iss-00357"]
template: "disc"
authority: "evidence"
derived_from:
  - "PR #362 Codex review comment 3759485944"
  - "Strict ChatGPT review of commit 83f636de5c29c222c7d8855cdffa159bfc8aee12"
reflected_to: []
---

# 20260811t155719z-disc PR Repair Unit R357-HL1

PR #362 の最終レビューで検出された hard-link rollback 破損を、一つの修正単位として追跡する。

## Repair contract

- source_batch: `N/A`（Storage Core の Current Artifact catalog に `pr-repair-batch` がないため、観測結果を本 Artifact に直接記録する）
- unit_id: `R357-HL1`
- root_cause_family: `active-rollback-hardlink-corruption`
- covered_ids: `OBS-357-83F-HL1`
- source_links: `https://github.com/chemitaro/spec-dock/pull/362#discussion_r3759485944`
- failure_class: `review_feedback:active-rollback-hardlink-corruption`
- decided_priority: `P1`
- merge_blocking: `yes`
- disposition: `fix-now`
- strategy_id: `STRAT-357-HL1`

## Inputs

- 統合する evidence:
  - 対象 PR: `#362`、reviewed head: `83f636de5c29c222c7d8855cdffa159bfc8aee12`。
  - GitHub Actions は同 head で全件成功したが、Codex review が P1 を一件報告した。
  - `write_json()` は既存 pathname を in-place 更新するため、管理対象 JSON が外部 pathname と hard link を共有すると、失敗前の書込みが外部 alias にも反映される。
  - rollback の `_restore_path()` は管理対象 pathname を unlink して新 inode として再作成するため、外部 alias が参照する旧 inode の変更済み bytes は復元されない。
  - 影響対象は `.agent/active.json` と `.agent/{index-all,tree-all,index,tree}.json`。symlink の target が hard link の場合も同じ問題が起きる。
  - 現行 symlink rollback tests は pathname の種別と bytes を検証するが、外部 hard-link alias の byte invariance は検証していない。
  - provider と dogfood mirror の `active_store.py` は観測時点で byte parity を維持している。

## Validity and need-to-fix

- 判定: 指摘は有効で、Issue 357 の active selection transaction が約束する失敗時の外部状態不変性に違反する。
- priority: P1。通常ファイルとして許容している入力で外部 alias を破損し得るため、merge blocker とする。
- current batch: この P1 以外に、現 head に対する新規 P0/P1 は観測されていない。

## Synthesis

- 一致する事実と未確定事項:
  - ローカル解析と Strict ChatGPT review は、根本原因が「hard link を通常ファイルとして in-place 更新し、rollback が inode topology を復元しないこと」で一致した。
  - Strict consultation は GitHub 上の exact head を検証し、GPT-5.5 Pro で実施した。
  - transaction 全体を held file descriptor 方式へ変更すれば hard-link alias の bytes を復元できるが、変更範囲と失敗経路が大きくなる。
  - 最小の安全策は、transaction の最初の mutation より前に全管理対象を検査し、通常ファイルまたは symlink target の `st_nlink > 1` を fail-closed で拒否すること。
  - `lstat` / `stat` と書込みの間の競合窓は残る。この TOCTOU は本修正で inode transaction を全面再設計しない限り閉じられず、既存のローカル信頼境界における residual risk として明示する。

## Options and trade-offs

- 選択肢と利点・制約:
  - A: held descriptor で旧 inode の bytes を復元する。hard-link topologyを保持できるが、全 write/rollback 経路の再設計となり、Issue 357 の最終修正としては過大。
  - B: mutation 前に hard-link を検出して拒否する。既存の single-link file と symlink semantics を維持しつつ、既知の破損経路を小さな差分で閉じられる。
  - C: snapshot/restore を現状のまま維持する。外部 alias の破損を許すため採用不可。

## Orchestrator disposition

- 採用: Option B。
- consultation disposition: `use`。
- Option A は将来の完全な inode transaction 再設計候補として残すが、本修正には採用しない。
- strategy_delta: 初回修正として、`.agent/active.json` と4つの index/tree JSON、およびそれらの symlink target を transaction 開始時に一括 preflight し、hard link を content-free な管理対象 path の診断で拒否する。rollback 実装自体は変更しない。

## Implementation plan

1. provider `infra/active_store.py` に、管理対象 pathname の通常ファイルまたは symlink target の link count を確認する bounded helper を追加する。
2. `set_active` transaction の最初の durable mutation より前に、`.agent/active.json` と4つの index/tree JSON、およびそれらの symlink target を一括検査する。
3. `st_nlink > 1` は既存の transaction error surface へ fail-closed で写像し、外部 alias path や内容を診断へ露出しない。
4. provider から dogfood mirror へ同一変更を反映し、byte parity を維持する。
5. active manifest、managed index、symlink target の hard-link casesをRed/Greenで追加する。single-link file、通常symlink、rollback既存ケースも維持する。

## Validation plan

- focused hard-link tests: HL-001 active manifest、HL-002 managed index、HL-003 symlink target。
- active store / set-active の既存 unit・CLI regression。
- `make lint`。
- provider/dogfood byte parity と `git diff --check`。
- fresh code review と QA review。
- commit/push 後、PR #362 の exact new head を再観測する。

## Out of scope

- 全 active transaction の descriptor-relative rewrite。
- hostile process が preflight 後に inode topology を変更する TOCTOU の完全排除。
- Current Artifact catalog に削除済み `pr-repair-batch` type を復活させること。

## Implementation result

- provider authority の `infra/active_store.py` へ、active transaction の snapshot 開始時に管理対象 JSON を一括検査する fail-closed guard を追加した。
- 対象は `.agent/active.json` と `.agent/{index-all,tree-all,index,tree}.json`。通常ファイルと symlink target を `Path.stat()` で確認し、regular file の `st_nlink > 1` を最初の durable mutation 前に拒否する。
- error は管理対象の repo-local path だけを示し、外部 alias path / content は露出しない。rollback 実装と transaction 順序は変更していない。
- provider から dogfood mirror へ同一変更を反映し、`cmp` で byte parity を確認した。
- Red evidence: active manifest hard link、managed index hard link、managed JSON symlink target hard link の3ケースが、修正前はすべて `DID NOT RAISE RuntimeError` で失敗した。
- Green evidence:
  - focused hard-link / single-link / symlink: `5 passed, 42 deselected`
  - active store / set-active unit・CLI: `56 passed, 37 skipped`
  - ordinary fast suite: `1642 passed, 2185 skipped`
  - `make lint`: ruff check / ruff format / mypy がすべてpass
  - `git diff --check`: pass
- fresh review evidence:
  - code review: `pass`、findings 0、confidence 0.96
  - QA review: `pass`、findings 0、confidence 0.97
  - spec review: `pass`、findings 0、confidence 0.94
- residual risk: preflight の `stat()` 後に別processがinode topologyを変更するTOCTOUは、本修正の明示的out of scopeとして残る。

## Commit and re-observation evidence

- correction commit: `e9da43c89a18ae40f0f50a316d9954762ff884df`（parent `83f636de5c29c222c7d8855cdffa159bfc8aee12`）。
- commit message: `fix(runtime): active-set hard-link問題をmutation前で検知`。
- push: `origin/iss-00357-reduce-runtime-to-storage-core`へ成功。
- GitHub Actions: exact head `e9da43c89a18ae40f0f50a316d9954762ff884df` のCI / Provider CIを含む3 workflow runがすべてsuccess。
- Codex review: `Didn't find any major issues`、reviewed commit `e9da43c89a`。
- observation: `overall_status=passed`、`recommended_next_action=merge_prepared`、head match、current-boundary actionable P0/P1 0。

## Reflection

- 本 Artifact はPR修正の限定 evidenceであり、Issue 357 の既存Requirement/Design/Planへ新しい仕様判断を追加しない。
