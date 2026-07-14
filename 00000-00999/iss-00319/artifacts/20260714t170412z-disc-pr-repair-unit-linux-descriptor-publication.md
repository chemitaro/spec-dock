---
種別: disc
ID: "20260714t170412z-disc"
タイトル: "PR Repair Unit U1"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-07-14"
親: ["iss-00319"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260714t170412z-disc PR Repair Unit U1

## Repair Unit Identity

- source_batch: `20260714t154712z-pr-repair-batch`
- unit_id: `U1`
- root_cause_family: `artifact_publication.linux_descriptor_link`
- covered_ids: `R1`, `R5`
- source_links: PR #323 / Codex P1 / Provider CI run 29344650625
- failure_class: `review_feedback:linux_descriptor_publication` + `check_failure:provider-tests`
- decided_priority: `P1`
- merge_blocking: `yes`
- disposition: `fix-now`
- status: `implemented-awaiting-commit-push-reobservation`

## Late Evidence Remediation

- このArtifactはworker implementation後に、orchestration omissionを修復するため作成した。
- Worker handoffはrepair batchに記録済みのF1 / U1 / S100-R1と同等のbounded scope、root cause、implementation plan、quality gatesを入力としていた。
- ただしcanonical unit Artifactをdelegation前に作るgateを見落としており、順序準拠は主張しない。
- 本remediationは実装差分をcommitする前に、unit固有の監査・fresh spec rereviewを可能にするためのlate evidenceである。
- Commit / push / re-observationは未実施であり、fresh spec rereviewはpending。

## Validity Analysis

- Codex P1はLinux unlinked temporary-file testが実際のdescriptor publication pathを覆っていない点を指摘した。
- Provider CI run 29344650625ではnormal Linux publication 25件がすべて`publication_unsupported`となり、25 failed / 2573 passed / 75 skipped / 2 warningsだった。
- Review finding R1とrequired CI failure R5は同じLinux descriptor publication pathを指し、相互にroot-cause仮説を補強する。
- よってF1はvalidなP1 merge-blocking familyであり、test-only対応では不十分である。

## Need-To-Fix Decision

- need_to_fix: `yes`
- reason: Required Ubuntu Provider CI failureとP1 findingが残るため、PR #323をmerge-preparedにできない。
- repair boundary: F1 / U1だけをfix-nowとし、F2〜F4のP2 findingsはdeferする。

## Root Cause

- `os.link('/proc/self/fd/<fd>', absolute_destination, follow_symlinks=True)`がplain link pathを選び、procfsを跨ぐためLinuxで`publication_unsupported`になると強く推定した。
- Verified staged descriptorからdestinationへpublishする契約自体は維持し、Linux call shapeだけを`linkat` + `AT_SYMLINK_FOLLOW`相当にする必要がある。

## Options Considered

1. Test-only correction
   - 初回GPT-5.6 Pro相談の推奨だったが、normal Linux 25 failuresによりstaleとなった。
2. Copy fallback
   - Atomic descriptor publication、error mapping、no-overwrite contractを変えるため不採用。
3. Destination parent `dirfd`によるhard-link publication
   - Fresh consultation `pr323-linux-publicatio-repair-consultati-2`が推奨。既存契約を維持した最小修復として採用。

## Recommended Design

- Linuxではdestination parent directoryを開き、`os.link(proc_fd_path, destination.name, dst_dir_fd=dirfd, follow_symlinks=True)`を使う。
- CPythonを`linkat` + `AT_SYMLINK_FOLLOW` call shapeへ誘導し、procfs source descriptorからdestination parent内basenameへpublishする。
- macOS path、existing error mapping、destination no-overwriteを変更しない。
- Path replacement testはverified stageをsiblingへrenameして保持し、元pathへadversarial replacementを配置する。Unlinkだけでverified bytesを失わせない。

## Implementation Plan

1. Provider publisherにLinux destination `dst_dir_fd` / `linkat` shapeを最小実装する。
2. Dogfood runtime mirrorへexact copyする。
3. Publisher testのpath replacement fixtureをsibling rename方式へ修正する。
4. F2〜F4へbranch mutationを広げない。
5. Local gatesとfresh code/QA review後、unit Artifactをfresh spec rereviewする。
6. Pass後にcommit/pushし、fresh Ubuntu Provider CIとlatest-head Codex re-reviewを行う。

## Validation Plan

- Focused publisher tests。
- Artifact import full focused regression。
- Code reviewer combined focused regression。
- Linux call-shape mock。
- `make lint`（Ruff、format、mypy）。
- Full pytest。
- `git diff --check`。
- Provider/dogfood parity `cmp`。
- Fresh code review、fresh QA review、fresh spec rereview。
- Commit/push後のfresh Ubuntu Provider CIとlatest-head re-review。

## Out of Scope

- F2: Active Workbench symlink reconciliation。
- F3: Product-level staged Artifact replacement race修復。
- F4: Wall-clock-dependent test flake修復。
- Migration、public API拡張、copy fallback、新依存。
- PR merge。

## Implementation Result

- Bounded changed files: 3。
  - Provider publisher: Linux destination parent `dst_dir_fd` / `linkat` call shape。
  - Dogfood mirror: provider変更のexact mirror。
  - Publisher test: path replacement fixtureをverified stageのsibling renameへ修正。
- Focused publisher tests: 41 passed。
- Artifact import full focused tests: 38 passed。
- Code reviewer combined focused tests: 65 passed。
- Linux call-shape mock: 1 passed。
- `make lint`: passed。Ruff、375-file format check、mypy 246 source filesがpass。
- Full pytest: 2598 passed / 75 skipped / 2 warnings in 1597.89s。
- `git diff --check`: passed。
- Provider/dogfood parity `cmp`: passed。
- Fresh code review: passed、P0〜P3 0。
- Fresh QA review: conditional pass、P0〜P3 0。Remaining conditionはcommit/push、fresh Ubuntu Provider CI、latest-head re-reviewのみ。

## Commit Evidence

- status: `pending`
- reason: Late unit evidence remediationとfresh spec rereviewをcommit前に完了する必要がある。
- expected scope: Provider publisher、exact dogfood mirror、publisher test、repair batch、this unit Artifact。

## Re-observation Result

- status: `pending`
- required evidence: Fresh Ubuntu Provider CI、latest-head Codex re-review、required checks、review threads、mergeability、base drift。
- observation must bind to: U1 implementation/evidence commitをpushしたlatest PR #323 head。

## Residual Risk / Follow-up

- F2〜F4はP2 follow-upとしてdeferし、current repair scopeへ含めない。
- Python 3.10 local validationはenvironment availabilityに依存し、Ubuntu Provider CIをauthoritativeとする。
- Fresh spec rereviewがlate evidence remediationを承認するまで、workflow P1はopen。
- Commit/pushとfresh re-observationが完了するまで、U1はmerge-blockingのまま。
