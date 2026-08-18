---
種別: 設計書（Issue）
ID: "iss-00371"
タイトル: "Explicit Spec History Purge"
関連GitHub: ["#371"]
状態: "planned"
最終更新: "2026-08-18"
依存: ["requirement.md"]
親: ["epic-00365", "init-local-00003"]
---

# iss-00371 Explicit Spec History Purge — 設計

詳細: [Design Guide](../../../../../../docs/authoring/design.md)

## 設計目標

D3のcommon deprovision engineに、別の`purge` intentとexplicit authority overlayを追加する。action/kernel/journal/resultは共有するが、authority token、allowed roots、preconditions、postconditions、resume compatibilityをdeprovisionと分ける。

## Current / Target

### Current

- argparseが`--keep-specs`/`--remove-specs`をmutually exclusiveにする。
- applyにはexactly one specs modeが必要。
- current uninstall planはremove-specs時にspec history actionを含める。
- `.uninstall-retry.json`はoriginal specs modeを記録しない。
- testsはexplicit summary、initiatives removal、modified/unknown preservation、symlink safetyを確認する。

### Target

- CLI adapterが`--apply --remove-specs`を`intent=purge`と`authority=explicit-spec-history-purge`へ正規化する。
- Contractがspec history rootsとauthority外 preservation rootsを明示する。
- plan/journal digestがintent/authority/allowed rootsを含む。
- common bounded removal kernelを使用する。
- deprovision/purge間のresumeは常にmismatchとなる。

## 責務・Interface

### Authority construction

```text
--apply + --remove-specs
  -> ExplicitPurgeAuthority(source='public-cli', confirmed=true)
```

`--remove-specs` dry-runはplanned purge intentを表現できるが、mutation authorityは持たない。`--apply`単独、`--keep-specs`、update/init、legacy marker存在だけではauthorityを作らない。

interactive confirmationを新設せず、existing two-part explicitness（`--apply`と`--remove-specs`）をconfirmation contractとする。CLI help、dry-run summary、JSON guidanceでdestructive scopeを明示する。

### Allowed roots

Contractはspec history rootをexact relative pathとして定義する。current implementation/testで確認されるrootをsource of truthとし、generic `spec-dock/`全体やprefix patternへ拡張しない。

Purge actionはallowed rootのdirectory bindingをno-followで開き、そのsubtreeだけをbounded removeする。root外sibling、repository metadata、unknown workbench/consumer contentはauthority外としてpreserveする。

### Plan and Journal

plan digestに次を含める。

- `intent=purge`
- explicit authority identity/source
- allowed spec history roots
- root binding
- contract/protocol identity
- action exact preconditions/postconditions

journal resume gateはdeprovisionよりstrictであり、authority source/intent/planがexact matchしなければwrite 0でblockする。retry commandがpurge authorityを自動付与しないよう、CLI invocationを毎回explicitに要求しjournalと照合する。

### Postcondition

- allowed spec history roots absent
- owned tooling/generated/managed targetsがplanどおりabsent/preserved
- authority外unknown content unchanged
- outside sentinel unchanged
- journal/staging state clean after success

### Legacy marker

minimal `.uninstall-retry.json`からoriginal purge authorityを再構成できない。purgeへのautomatic conversionは禁止する。legacy partial purgeのrecoveryはcurrent-compatible packageまたはhuman-verified procedureを案内し、marker削除やauthority推測で続行しない。

## data / failure

- subtree recordはroot binding、child authority digest、entry pre-action identitiesを持つ。
- regular fileのexact SHAはownership/recovery evidenceであり、index positionを使わない。
- partial tree deletionはcompleted/remaining child checkpointをjournalに残す。unknown divergenceがあればremaining removalを停止する。
- deleted history bytesのbackupは本Issueで作らない。whole-operation rollbackはnon-goal。
- error/resultはdestructive authorityとfailed/pending relative pathsをsanitizedして表現する。

## 変更対象

- common Contract/Assessment/Plan/Journalへのpurge overlay
- CLI `--remove-specs` dispatch/result mapping
- common bounded removal kernel tests
- legacy purge branch/writer removal
- uninstall JSON/text tests
- README destructive/recovery guidance

update/fresh/deprovision behaviorとpublic flags/schemaは変更しない。

## 移行・互換性・rollback

- D3 dry-run mapperをpurge planにも使用し、existing JSON semanticを維持する。
- apply cutoverとold purge branch removalを同じchangeにする。
- new purge journal開始後はsame/compatible packageでforward recoveryする。
- deprovision journal、legacy marker、different authorityをpurgeへconvertしない。
- code rollbackはnew journal開始前まで。進行中purgeの自動data restoreは提供しない。

## testability

- dry-run no-write、apply/remove-specs success
- no apply/no mode/keep-specs/update/init cannot purge
- authority digest/resume mismatch
- allowed root exact path guard
- root/child symlink、hardlink、parent/root rebind
- authority外unknown sibling/outside sentinel preservation
- partial subtree failure/checkpoint/resume
- legacy marker unconvertible
- JSON/text destructive summary and one-object contract
- absence of old purge branch/writer

## risk

- explicit deletionをcritical変更と混同するrisk:planned authorized deletion自体はstrictで扱い、authority外不可逆deleteの可能性が見つかったときcriticalへ上げる。
- allowed root拡大:exact relative rootsをContract/testで固定する。
- retry authority leak:intent/authorityをplan/journal digestに含め、cross-mode resume negative testを必須にする。
- user expectation mismatch:dry-run/help/summaryにspec history deletionを明示する。
