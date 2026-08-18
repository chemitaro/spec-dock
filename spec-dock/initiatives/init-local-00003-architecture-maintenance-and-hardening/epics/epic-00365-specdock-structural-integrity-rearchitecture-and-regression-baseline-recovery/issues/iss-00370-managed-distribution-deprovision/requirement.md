---
種別: 要件定義書（Issue）
ID: "iss-00370"
タイトル: "Managed Distribution Deprovision"
関連GitHub: ["#370"]
状態: "planned"
最終更新: "2026-08-18"
親: ["epic-00365", "init-local-00003"]
---

# iss-00370 Managed Distribution Deprovision — 要件定義

詳細: [Requirement Guide](../../../../../../docs/authoring/requirement.md)

## 目的

current `spec-dock uninstall --apply --keep-specs` 相当の managed distribution deprovision を unified reconciliation engineへ移す。利用者はdefault/`--keep-specs` dry-runでcomplete ownership-safe deprovision planを確認し、明示apply後にtooling、generated state、proven-owned managed assetsを除去できる一方、spec historyとauthority外unknown contentを保持できる。

## 背景

exact commitではuninstallが`cli.py`内の`_UninstallAction`、独自plan/apply/postverify、descriptor-relative recursive remove、`.uninstall-retry.json`、text/JSON rendererを持つ。current testsはdry-run no mutation、keep-specs preservation、modified/unknown preservation、symlink boundary、partial failure、JSON schema version 1を固定する。D1/D2のengineとはaction grammarとrecovery protocolが別であり、lifecycle symmetryを阻害している。

## 観測可能な要件

| ID | 要件 |
|---|---|
| I370-R01 | `uninstall`はdry-runを既定とし、`--apply`にはexactly one specs modeを要求する。deprovision mutationは`--apply --keep-specs`でのみ開始する。 |
| I370-R02 | defaultまたは`--keep-specs` dry-runはread-only deprovision assessment/plan-derived resultを返し、journal、retry marker、staging、target mutationを作らない。`--remove-specs` dry-runはD4のpurge ownerとする。 |
| I370-R03 | deprovisionはowned tooling、generated state、current/historical proven managed assets、owned empty directoriesを除去し、spec historyとauthority外unknown contentを保持する。 |
| I370-R04 | all actionsのownership/mutation safetyをwrite前に評価し、blockerが一件でもあればpartial safe subsetを適用しない。 |
| I370-R05 | modified managed file、unknown file、unsafe mode/type、symlink/hardlink、parent/root rebindはpreserveまたはblockされ、repository外を変更しない。 |
| I370-R06 | applyはD1/D2と同じaction grammar、filesystem kernel、Operation Journal、ProcessResultを使う。uninstall固有第二grammarを残さない。 |
| I370-R07 | partial failureはdeprovision intent/authority/planに束縛したjournalを保持し、same-plan forward recoveryだけを許可する。 |
| I370-R08 | current `.uninstall-retry.json`の情報不足を推測で補わない。root/original intent/plan/checkpointをexactに証明できない場合はwrite前に停止する。 |
| I370-R09 | existing `uninstall --json` schema version 1、one-object stdout、field meaning、sanitized failure semantics、exit mappingを維持する。 |
| I370-R10 | deprovision completion後も`spec-dock/initiatives`以下のspec historyとunknown contentはbyte-identicalに残る。 |

## スコープ

### 対象

- default/`--keep-specs` uninstall dry-runと`--apply --keep-specs`
- deprovision intent/authority/postcondition
- owned removal/preserve/block action
- bounded descriptor-relative recursive remove
- current uninstall text/JSON compatibility mapper
- `.uninstall-retry.json` migration/fail-closed behavior
- old uninstall plan/apply/postverify/marker writerのdeprovision path削除

### 対象外

- `--remove-specs` purge dry-run/apply（`iss-00371`）
- new uninstall command/flag/schema
- spec history content migration
- generic recursive deletion library
- Windows support
- Full Regression repairs

## 失敗・境界条件

- `--apply` without specs mode、both modes、unmanaged targetはmutation前にerror。
- default/`--keep-specs` dry-runとJSON renderingはtargetを変更しない。`--remove-specs` dry-runの同じ保証はD4で固定する。
- ownershipを証明できないmanaged-looking pathはpathnameだけで削除しない。
- preserved file/rootを含むparent directoryはremoveしない。
- recursive remove中にsymlink、hardlink、identity change、unknown childを観測した場合は外部をfollowせず停止する。
- current legacy uninstall markerはoriginal keep/remove authorityを証明できないため、defaultでnew journalへ推測変換しない。
- partial apply後はjournal/postconditionに基づきforward recoveryし、spec history purgeへ昇格しない。

## 受け入れ条件

1. default/`--keep-specs` dry-runがdeprovision planned resultを返し、before/after treeがbyte-identicalである。`--remove-specs` dry-runはD4までcurrent compatibility pathを維持する。
2. `--apply --keep-specs`がowned tooling/generated/managed assetsを除去する。
3. initiatives/spec history、modified/unknown content、repository root sentinelが保持される。
4. blocker有りplanがwrite 0件で停止する。
5. symlinked boundary、hardlink、parent/root replacementがexternal deletionなしで停止する。
6. partial failure fixtureがdeprovision journalを保持し、same-plan retryで収束するかtyped manual recoveryとなる。
7. deprovision journalを`--remove-specs`でresumeしようとするとauthority mismatchでwrite 0件となる。
8. current JSON schema version 1のkeys/actions/summary/guidance/error sanitization/one-object contractがgolden testsで維持される。
9. `_UninstallAction`等deprovision対象legacy grammar/plan/apply/postverify/marker writerが削除される。
10. focused uninstall tests、managed distribution tests、init/update regressionが成功する。

## 制約・前提

- dependency `iss-00369`のsingle engineが成立済みである。
- spec history purge authorityをこのIssueに含めない。`--remove-specs`はD4までcurrent compatibility pathに留める場合も、new deprovision journalから到達不能にする。
- `.uninstall-retry.json`のcurrent payloadに存在しないfieldをfixtureやmigrationで捏造しない。
- existing JSON consumerが未確認の場合、testsで固定されたschema/semanticsを最低compatibility boundaryとする。
