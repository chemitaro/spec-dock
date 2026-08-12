---
種別: disc
ID: "20260812t134618z-01-disc"
タイトル: "PR Repair Unit PR363-U003 Artifact Finalization TOCTOU"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-08-12"
親: ["iss-00359"]
template: "disc"
authority: "evidence"
derived_from: []
reflected_to: ["requirement.md", "design.md", "plan.md", "report.md"]
---

# 20260812t134618z-01-disc PR Repair Unit PR363-U003 Artifact Finalization TOCTOU

## Repair Contract

- `source_batch`: `report.md#11`
- `unit_id`: `PR363-U003`
- `root_cause_family`: `artifact-finalization-toctou`
- `covered_ids`: `PR363-P1-003`
- `source_links`: PR #363 review thread `PRRT_kwDOQ99OK86YlhKX`
- `failure_class`: `review_feedback:artifact-finalization-toctou`
- `decided_priority`: `P1`
- `merge_blocking`: `yes`
- `disposition`: `fix-now`

## Validity Analysis

Artifact CLIのno-replace publish後、SKILL.mdは返却pathnameへ直接本文を書く。final pathがsymlinkへ差し替えられると、通常のpath writeはrepository外targetを上書きし得る。指摘はvalid。

## Need-To-Fix Decision

exactly-one write boundaryの安全性に直結するため、このPRでskill-local finalizationを修正する。

## Root Cause

CLI publication safetyが、別openとなる本文確定にも継続すると誤認した。返却pathのsecond-openにno-follow / inode revalidationがない。

## Options Considered

1. Artifact CLIへbody optionを追加: public runtime contractを拡張するため棄却。
2. pathnameへ直接writeし事後snapshotだけ確認: repository外writeを防げず棄却。
3. skill-local helperでrepository-relative pathをcomponent単位no-follow traversalし、lstat/open/fstat inode一致後だけ本文確定: 採用。

## Recommended Design

二skill assetのうちgrill配下へPython helperを追加する。helperは本文をstdinから先にmemoryへ読み、repo-relative direct-child Artifact pathだけを受理する。parent componentをdirfd + `O_NOFOLLOW`で開き、Artifactをlstat後に`O_NOFOLLOW`でopenし、device / inode / regular-file / link-countを再検証してからtruncate / write / fsyncする。失敗時はdelete / rename / retryしない。

## Implementation Plan

1. symlink targetとinode replacementでwriteを拒否するhelper CLI testをREDにする。
2. provider helperを実装し、dogfoodへbyte-identical projectionする。
3. SKILLのone-write protocolをhelper経由へ変更し、direct pathname writeを削除する。

## Validation Plan

success、final symlink、ancestor symlink、inode replacement、sibling不変のpublic helper test、static contract、focused regression、全体lint / pytest。

## Out of Scope

Artifact CLI argument追加、template変更、automatic cleanup / retry、second Artifact作成。

## Implementation Result

Provider / dogfoodへbyte-identicalなskill-local helperを追加した。`identity`と`finalize`の間でdevice / inodeをpinし、repo-rootから各componentをno-follow traversalする。success、final symlink、ancestor symlink、inode replacement、Current formatter prefixのpublic testがpassした。

## Validation Result

helperのpublic behavior 5件を含むIssue 359 focused contract 20件、ordinary suite 1647件、lintがpassした。包括的な最終品質ゲートはP0=0 / P1=0でpass。PR latest-head再観測はpending。

## Commit Evidence

pending

## Re-observation Result

pending

## Residual Risk / Follow-up

helper失敗後はCLI作成済みfileをpartial Artifactとして保持し、operator recoveryへ渡す。
