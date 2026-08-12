---
種別: disc
ID: "20260812t151202z-disc"
タイトル: "PR Repair Unit PR363-U004 CI Inode Reuse"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-08-12"
親: ["iss-00359"]
template: "disc"
authority: "evidence"
derived_from: ["Provider CI run 31610744167"]
reflected_to: ["requirement.md", "design.md", "plan.md", "report.md"]
---

# 20260812t151202z-disc PR Repair Unit PR363-U004 CI Inode Reuse

## Repair Contract

- `source_batch`: `report.md#11`
- `unit_id`: `PR363-U004`
- `root_cause_family`: `artifact-finalization-inode-reuse`
- `covered_ids`: `PR363-CI-001`
- `source_links`: Provider CI run `31610744167` / job `94161136220`
- `failure_class`: `check_failure:provider-tests`
- `decided_priority`: `required-ci`
- `merge_blocking`: `yes`
- `disposition`: `fix-now`

## Validity Analysis

Linux runnerではArtifact fileをunlinkして同名fileを再作成した際にinodeが即時再利用された。helperは`device + inode`だけをidentityとしていたため、置換fileをoriginalと誤認してtruncate / writeし、required Provider CI testが失敗した。CI failureは再現可能で、repository外write防止に関わるためvalid。

## Need-To-Fix Decision

required Provider CIを回復し、publish後second-openの置換検知を実効化するため、このPRで修正する。

## Root Cause

inode番号をfile generationの一意識別子として扱った。filesystemはunlink後にinodeを再利用できるため、`device + inode`だけではidentity capture後の再作成を識別できない。

## Options Considered

1. Linux testだけskip: 安全欠陥を隠すため棄却。
2. size / mtimeだけを追加: user-settableで弱いため棄却。
3. `st_ctime_ns`をidentityへ追加し、truncate前のlstat / fstatで一致を要求: inode再利用時のmetadata変更を検出でき、public Artifact CLIを変えないため採用。
4. Artifact CLIへbody inputを追加: Issue 359のpublic runtime contractを拡張するため棄却。

## Recommended Design

skill-local helperの`identity`は`device`、`inode`、`ctime_ns`を返す。`finalize`は三値を必須argumentとして受け取り、parent no-follow traversal後のlstatとfile open後のfstatで三値が同一である場合だけtruncate / writeする。write後はpathが同じdevice / inodeを指すことを確認する。失敗時のpartial Artifact契約は変更しない。

## Implementation Plan

1. Linux inode再利用でもdeterministicに置換を表すtest fixtureへ調整し、`ctime_ns` mismatchをREDにする。
2. provider helperとdogfood projectionへ`ctime_ns` identity / argument / pre-write checkを追加する。
3. SKILL、R/D/P、companion、static test、report、ZIPを同じ三値contractへ揃える。
4. focused test、lint、ordinary suiteを実行し、commit / push後にPR latest headを再観測する。

## Validation Plan

helper public behavior、Issue 359 focused contract、provider / dogfood parity、lint、ordinary pytest、required Provider CI、latest-head Codex review。

## Out of Scope

Artifact CLI argument変更、automatic cleanup / retry、二件目Artifact、planning / publication / #360責務、CI retention。

## Implementation Result

provider / dogfoodのskill-local helperをbyte-identicalに更新し、`identity`のJSONと`finalize`の必須argumentへ`ctime_ns`を追加した。truncate前のlstat / fstatはdevice / inode / `ctime_ns`を比較し、write後はctime更新を許容してdevice / inodeだけを再確認する。SKILL、R/D/P、companion、static contractも同じ三値へ同期した。

## Validation Result

- pre-fix RED: helper test `5 failed, 1 passed`
- helper contract: `6 passed`
- Issue 359 focused contract: `21 passed, 618 deselected`
- `make lint`: pass
- ordinary `uv run pytest -q`: `1648 passed, 2200 skipped`
- provider / dogfood SKILL and helper parity: pass
- required Provider CI: push後に再観測

## Commit Evidence

Implementation commit: `9bfcecae75008addc6fe40c38482aad72a032e20`。provider / dogfood helper、skill contract、R/D/P、companion、ZIP、regression testを同commitへ含む。

## Re-observation Result

pending

## Residual Risk / Follow-up

`ctime_ns`はidentity captureからtruncate前までのreplacement detectorとして使用し、write後に不変であることは要求しない。
