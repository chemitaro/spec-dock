---
種別: 要件定義書（Issue）
ID: "iss-00371"
タイトル: "Explicit Spec History Purge"
関連GitHub: ["#371"]
状態: "planned"
最終更新: "2026-08-18"
親: ["epic-00365", "init-local-00003"]
---

# iss-00371 Explicit Spec History Purge — 要件定義

詳細: [Requirement Guide](../../../../../../docs/authoring/requirement.md)

## 目的

spec history deletionを通常のupdate/deprovisionから分離し、current `spec-dock uninstall --apply --remove-specs`のexplicit authorityでのみ実行できるpurge flowとしてunified engineへ移す。利用者はdry-runで削除対象を確認し、明示apply後にspec historyを削除できる。retry、update、deprovisionが権限を暗黙拡大してはならない。

## 背景

current CLIは`--keep-specs`と`--remove-specs`をmutually exclusiveにし、uninstallをdry-run defaultとする。しかしkeep/removeは同じCLI-owned uninstall grammar/markerを共有し、minimal `.uninstall-retry.json`はoriginal authorityを記録しない。D3後はdeprovisionがnew journalへ移るため、purgeを別intent/authorityとして明示しないとhistory deletionがrecovery pathへ混入する。

## 観測可能な要件

| ID | 要件 |
|---|---|
| I371-R01 | spec history purgeはexisting `uninstall --apply --remove-specs`の組合せでのみmutation authorityを得る。new command/flagを追加しない。 |
| I371-R02 | default dry-runは削除予定のspec history、owned tooling/generated assets、preserved authority外contentを明示し、write 0件とする。 |
| I371-R03 | `--apply` without `--remove-specs`、deprovision intent、update/init、resume mismatchからspec historyを削除しない。 |
| I371-R04 | purge authorityはexplicitly defined spec history rootに限定する。repository外pathとauthority外unknown siblingを保持する。 |
| I371-R05 | purge pathのroot/parent/child identity、symlink/hardlink、path guard、writability、operation root bindingをwrite前とmutation直前に検証する。 |
| I371-R06 | blockerが一件でもあればsafe subsetを部分適用せず、operation全体をwrite前に停止する。 |
| I371-R07 | purge journalは`intent=purge`、explicit authority、plan digest、exact pre-action identitiesを記録する。deprovision journalからpurgeへresumeできない。 |
| I371-R08 | partial purgeはsame root/intent/authority/plan/compatible protocolだけがforward recoveryできる。whole-operation rollbackを保証しない。 |
| I371-R09 | current dry-run/text/JSON schema version 1/exit semanticsを維持し、purge action reasonにexplicit `remove-specs` authorityを反映する。 |
| I371-R10 | purge completion後、spec historyはabsentとなり、authority外unknown contentとrepository boundary outside sentinelはunchangedである。 |

## スコープ

### 対象

- `uninstall --remove-specs` dry-run
- `uninstall --apply --remove-specs` apply
- explicit purge intent/authority/postcondition
- spec history rootのbounded recursive removal
- purge journal/resume/authority non-escalation
- current JSON/text compatibility
- old purge branch/marker writerの削除

### 対象外

- updateによるhistory cleanup
- deprovisionからのimplicit purge
- new confirmation UI、new command/flag
- removed historyのbackup/restore product feature
- whole-operation rollback
- generic secure-delete/forensic erase
- Windows support

## 失敗・境界条件

- explicit `--apply --remove-specs`が揃わない場合はdry-run/errorであり、purge mutationを開始しない。
- purge rootがsymlink、unsafe type、root外escape、identity changedの場合はexternal contentをfollow/removeしない。
- deprovision journal、legacy marker、different planをpurge invocationでauthority upgradeしない。
- explicit purge root内のspec historyは利用者が削除を承認したdataである。authority境界外のunknown contentはpathname proximityで巻き込まない。
- partial deletion後にpre/post identityを一意判定できない場合はjournalを保持しmanual recovery guidanceを返す。
- `update`はrelease catalog changeを理由にspec history purgeを実行しない。

## 受け入れ条件

1. dry-runがspec history purge planを表示し、target treeを変更しない。
2. `--apply --remove-specs`だけがpurge journalを作成し、spec historyを削除する。
3. no apply/no mode/keep-specs/update/init/retry mismatchでhistory deletion 0件となる。
4. symlinked root/child、hardlink、parent/root rebind、unknown authority外pathでexternal mutation 0件となる。
5. deprovision journalをremove-specsでresumeするとauthority mismatchでblockされる。
6. purge journalをkeep-specs/deprovisionとしてresumeしてもplan/intent mismatchを推測修復しない。
7. partial purge fixtureがsame-plan forward recoveryで収束するかtyped manual recoveryとなる。
8. current JSON schema/one-object/action fields/guidance/exit semanticsが維持される。
9. purge対象legacy branchとlegacy marker writerが削除される。
10. focused purge/deprovision/update regressionsが成功する。

## 制約・前提

- dependency `iss-00370`のdeprovision authorityとcommon removal kernelが成立済みである。
- explicit purgeは意図されたdestructive operationだが、scope外pathの不可逆deleteが見つかった場合はPlanを`critical`へ再評価する。
- legacy `.uninstall-retry.json`にoriginal keep/remove intentがないため、purge authorityを推測しない。
- recoveryはexact pre/post identityとjournal checkpointを使い、削除済みhistoryの自動復元を約束しない。
