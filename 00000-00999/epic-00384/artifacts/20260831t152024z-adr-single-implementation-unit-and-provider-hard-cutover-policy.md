---
種別: ADR（Architecture Decision Record）
ID: "20260831t152024z-adr"
タイトル: "Single Implementation Unit And Provider Hard Cutover Policy"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-09-01"
親: ["epic-00384"]
authority: "accepted"
accepted_authority: "accepted ADR"
accepted_at: "2026-09-01"
accepted_by: "iwasawayuuta"
mirror_eligible: true
derived_from: ["20260831t005139z-adr", "20260830t234548z-research", "20260830t235429z-disc"]
reflected_to: ["epic-00384/requirement.md", "epic-00384/design.md", "epic-00384/plan.md", "iss-00392/requirement.md", "iss-00392/design.md", "iss-00392/plan.md"]
---

# 20260831t152024z-adr Single Implementation Unit And Provider Hard Cutover Policy

## Context

Epic #384の旧計画は、調査、Product判断、lifecycle bridge、writer cutover、CI移行、最終検証を、decision-only Issue 3件とC4〜C11へ分割していた。しかし本Productでは、Issueを「実装とその検証を一体で完了・受入する一つの実装ユニット」と定義する。実装を伴わない調査・分析・意思決定、tests-only、verification-onlyの作業はIssueとして成立しない。

現行実装にはuninstall bridgeとinstall/update writerを独立してreleaseできる自然な境界がない。分割を成立させるためにP0〜P3、split/combined、cross-Issue fixture、rolling inventory receipt、required-check bindingなどを導入すると、Issue分割のためだけの中間Product contractが増える。

2026-09-01時点のexact baselineは次である。

- base SHA: `d8f9d02f2400cbc084e5ee92a5fbba339f93f015`
- package / recognized legacy workspace: `0.2.3`
- full collection: 2,710 nodes
- sorted node-set SHA-256: `f607b007d167231ed27f2a17391b0d8b3aa452d67ce6532565463e193486a04c`
- ordinary gate: `1574 passed, 1136 skipped in 57.02s`
- ordinary gate resource reference: wall 58.42s、user 24.41s、system 31.29s、CPU/wall約0.953
- approved-failure ledger: 27 entries、26 active、1 resolved
- active 26 nodes focused rerun: 26 failed in 14.69s
- GitHub ruleset API: 0 rulesets。classic branch protectionはcurrent tokenで403のためeffective required contextsは実装PR上で観測する。

## Decision

### 1. Issue境界

- Epic #384の実装Issueは`iss-00392 Provider Lifecycle And Regression Gate Hard Cutover`の1件だけとする。
- 調査、Product判断、baseline inventoryはIssue作成前のEpic authoringで完了する。
- 実装、successor tests、旧実装撤去、failure terminalization、CI切替、性能・安定性検証を`iss-00392`が一体で所有する。
- `iss-00388`〜`iss-00390`は実装前にEpicへ統合された誤ったIssue境界としてcloseする。実装済み・完了済みとは扱わない。
- C4〜C11、`DEC-*`、`FIX-*`は作らない。必要な作業は`iss-00392`内のmilestone / stepとする。

### 2. Lifecycle hard cutover

- uninstall-first bridgeや中間package generationを公開せず、legacy lifecycleからfinal simplified lifecycleへcombined hard cutoverする。
- provider-owned tooling payloadは`spec-dock/{docs,templates,system,scripts}`の4 fixed rootsと、`.agents/skills/spec-dock`、`.agents/skills/spec-dock-grill-with-docs`の2 fixed slotsに限定する。固定mutation setは4 roots、2 slots、fixed installation record、fresh init時だけの2 consumer seed作成で閉じる。
- Initiatives、nested Artifacts、`.workbench`、generated projections、unknown non-target paths、unrelated skillsは探索・正規化・削除しない。
- mutation targetのownershipが不明なら最初のtarget mutation前にpreserve-and-blockする。unknown non-targetはpreserve-and-ignoreする。
- updateはcandidate全体をstage / validateし、`docs -> templates -> system -> scripts -> skill slots`の順で置換し、ready recordを最後に書く。
- uninstallは4 rootsとvalid owned 2 slotsを除去した後もfixed installation recordを削除せず、`state=tooling-absent-preserved-data`へatomic replaceする。このdurable discriminatorにより、never-installed `absent`とuninstalled stateを区別する。
- automatic rollback、arbitrary checkpoint、cross-intent recoveryをpublic contractにしない。同じoperation・同じcandidateのexternal rerunだけを許可する。

### 3. Legacy compatibility

- 自動認識するlegacy cohortはexact clean `0.2.3` workspaceだけとする。
- 実root binding、exact version / runtime digest、active legacy recovery不存在、2 skill slotsがabsentまたはexact markerless treeであることをmutation前に確認する。
- migration成功後はnew installation recordとslot markersをauthorityとし、legacy recognizerを再度参照しない。入力集合を将来拡張しない。
- active legacy journal / retry / purge recoveryは推測変換せずwrite 0でblockし、exact `0.2.3` packageまたはsource artifactでclean stateへ戻してから再実行する。
- final formatに対する旧`0.2.3`の`init --force`、`update`、tooling uninstall、`--remove-specs`はmutation-zeroでなければmergeしない。baseline `0.2.3` subprocessをtarget-scoped startup-injected composite tripwire付きで実行し、Python filesystem audit eventsに加え、exact 0.2.3が`ctypes.CDLL`から直接呼ぶLinux `renameat2`とmacOS `renameatx_np`をnative call前に遮断する。platformごとのnative positive controlをcall前に捕捉しtarget tree不変を証明した上で、composite tripwire event 0を主証拠、tree digest不変を補助的な最終状態証拠とする。失敗時はbridgeを追加せず、final marker / formatを旧engineがblockできる形へ修正する。

### 4. Consumer-owned seeds

- `spec-dock/.gitignore`とshipped `.github/workflows/ci.yml`はfresh init時だけ作るconsumer-owned seedとする。
- existing regular file、custom file、symlink、unexpected typeをfollow / overwrite / deleteしない。fresh initではwarningを許可し、provider tooling installは継続する。
- update、reinstall、tooling uninstallは両seedを変更しない。
- 両seedをinstallation completeness、candidate digest、legacy ownership anchor、uninstall allowlistから除外する。

### 5. Public CLI / purge

- `init --force`は独自の破壊authorityを持たず、stateに応じた`install_tooling` / `update_tooling` compatibility aliasとする。
- uninstallはtooling-onlyとし、`--apply`を唯一のconfirmationにする。defaultはdry-runである。
- spec-history purge capabilityを廃止し、独立purge commandも作らない。
- `--keep-specs`はdefault tooling-only uninstallと同義のcompatibility aliasとして残す。
- `--remove-specs`はpermanent non-mutating compatibility trapとして残し、全modeでmutation 0、error code `spec-history-purge-removed`、exit 2を返す。
- tooling uninstall後もfixed recordの`state=tooling-absent-preserved-data`を保持し、never-installed `absent`と区別する。このrecordからuser dataとconsumer seedsを保持したままreinstallし、fresh-init-only seedを再作成しない。

### 6. Artifact / platform / CI

- authoritative PR candidateごとに一つのpackaging command invocationでwheelとsdistを生成し、source SHAと各SHA-256を固定する。
- Linux canonical laneとmacOS delta laneは同じwheel bytesを使う。
- Linuxはsingle pytest process / worker 1でOS非依存contract、Linux boundary、wheel lifecycle、sdist minimal smokeを所有する。
- macOSはexecutable mode、symlink/no-follow、rename/replacement、installed entry pointなどのplatform deltaだけを所有し、pure/domain/common CLIを再実行しない。
- main pushの4-shard Full Regressionを廃止する。release publication workflowは本Epicで新設しない。
- required contextは既存名の再利用を第一選択とする。変更が不可避な場合だけ、同じIssue / PR内でold+new required、intentional RED canary、new-only requiredへ遷移し、unrelated contextsとhuman review gateを保持する。

## Rejected alternatives

- decision-only Issues、inventory Issue、verification-only Issueを作る。
- P0 / P1 / P2 / P3やsplit/combined pathをProduct contractにする。
- `InventoryHeadV1`、`RemovalReceiptDeltaV1`、`Provider Receipt Binding`、append-only receipt chainを構築する。
- independent purgeと`PurgeOperationRecordV1`を維持する。
- OS非依存testをLinuxとmacOSで重複実行する。
- shard / xdist / worker追加やmachine大型化だけで実行量を隠す。

## Consequences

- `iss-00392`は大きいが、一つの観測可能なcutover outcomeと一つの受入境界を持つ。内部作業はmilestone、step、必要に応じた複数PRで管理する。
- 各PRはmerge直後にreleasableでなければならない。successor proofより先に旧contractやtestsを削除しない。
- exact `0.2.3` migrationとold-package mutation-zero、5-run budget、seeded fault pack、rolling 20は実装後にしか得られないため、`iss-00392`のclose条件とする。
- classic branch protection、effective required context、merge queueはcurrent tokenで観測できない動的外部事実であり、Product判断ではない。CI transition直前にread-onlyで取得し、未確認なら外部設定を変更しない。
- implementation failureのblast radiusは大きいため、Planning Levelは`critical`とする。

## References

- `20260831t005139z-adr-disposable-provider-roots-and-fixed-skill-slots.md`
- `20260830t234548z-research-provider-test-suite-root-cause-analysis-and-redesign.md`
- `20260830t235429z-disc-provider-test-strategy-simplification-decision-analysis.md`
- `requirement.md`
- `design.md`
- `plan.md`
- `issues/iss-00392-provider-lifecycle-and-regression-gate-hard-cutover/`
