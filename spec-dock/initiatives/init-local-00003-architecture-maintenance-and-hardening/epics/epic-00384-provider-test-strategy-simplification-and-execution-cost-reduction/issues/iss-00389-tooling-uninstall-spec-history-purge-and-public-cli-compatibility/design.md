---
種別: 設計書（Issue）
ID: "iss-00389"
タイトル: "Tooling Uninstall Spec History Purge And Public CLI Compatibility"
関連GitHub: ["#389"]
状態: "draft"
最終更新: "2026-08-31"
依存: ["requirement.md"]
親: ["epic-00384", "init-local-00003"]
---

# iss-00389 Tooling Uninstall Spec History Purge And Public CLI Compatibility — 設計

詳細: [Design Guide](../../../../../../docs/authoring/design.md)

## 設計目標

tooling ownershipとhistory purge authorityをpublic command levelで分離し、normal uninstallから不可逆なhistory deleteへ権限昇格できないdecision modelを作る。

## Current / Target

Current:

- uninstall surfaceがdeprovisionとpurge intentを選択する。
- journal / retry / cross-intent recoveryが両intentを同じengineで扱う。
- public compatibilityとcleanup-pending semanticsが新contractに対して未確定である。

Target:

- `tooling uninstall`はfixed owned targetsだけを扱う。
- history purgeを残す場合も独立authority / commandとして扱う。
- public option、confirmation、result、sunsetがaccepted decisionに束縛される。
- post-uninstall purge eligibilityとreinstall authorityがinstallation record不存在から推測されない。

## 責務・Interface

- tooling uninstall contract: exact delete set、blocked ownership、dry-run / apply result。
- purge contract: existence、command、confirmation、authority、result。
- compatibility contract: deprecated alias、sunset、breaking / deprecation policy。
- removal handoff: old intent mapping、journal、tests、docsの後続owner。
- post-uninstall handoff: purge target evidence、`tooling-absent-preserved-data` admission、reinstall route。

## data / failure

decision tableは少なくとも`command/option`、`intent`、`confirmation`、`delete authority`、`post-uninstall evidence`、`reinstall route`、`text`、`JSON`、`exit`、`sunset`を持つ。unknown / foreign / rebound targetでは該当delete前にblockする。cleanup-pendingを成功扱いする場合もuser-visible statusと再実行方法を明示する。

## 変更対象

変更するものは本Issue docs、decision Artifact、受理後のEpic docsだけとする。`src/spec_dock/cli.py`、`managed_distribution.py`、tests、shipped docsは後続implementation Issueが変更する。

## 移行・互換性・rollback

deprecated aliasを採る場合は、non-destructive diagnosticまたは明示purge handoffを経由し、silent purgeへfallbackしない。decision未確定時は現行実装を変更せず後続Issueをblockする。

## testability

- 現行parser / intent / text / JSON / exit mappingをread-only inventory化する。
- target decisionとの全mapping差分とsunsetを確認する。
- update / retry / tooling uninstallからpurge authorityへ到達しないことを設計上のnegative pathとして確認する。
- installation record削除後もpurge eligibilityとreinstall routeが一意か確認する。

## risk

- backward compatibilityを理由に destructive aliasを残すこと。
- cleanup-pendingとpartial failureを混同すること。
- purge廃止とuser data保護を、実データ削除手段の不在という別問題と混同すること。
- installation record不存在をuser history ownershipの証明と誤認すること。
