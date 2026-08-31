---
種別: 要件定義書（Issue）
ID: "iss-00389"
タイトル: "Tooling Uninstall Spec History Purge And Public CLI Compatibility"
関連GitHub: ["#389"]
状態: "draft"
最終更新: "2026-08-31"
親: ["epic-00384", "init-local-00003"]
---

# iss-00389 Tooling Uninstall Spec History Purge And Public CLI Compatibility — 要件定義

詳細: [Requirement Guide](../../../../../../docs/authoring/requirement.md)

## 目的

通常uninstallをtooling-onlyにするaccepted ADRを、`--remove-specs`、独立purge、confirmation、public text / JSON / exit compatibilityまで含む一意なProduct contractへ具体化する。後続uninstall cutover Issueがuser historyへのdelete authorityを推測せず実装できる状態を成果とする。

## 背景

現行CLIは`--keep-specs`と`--remove-specs`を持ち、deprovisionとspec-history purgeを同じuninstall surfaceから選択する。accepted ADR `20260831t005139z-adr` は通常uninstallからhistory purge authorityを除外したが、`--remove-specs`を即時廃止、deprecate、独立purgeへ移行するかは未決である。

## 観測可能な要件

- 通常uninstallのdelete authorityを4 fixed roots、valid owned 2 fixed skill slots、fixed installation record / ready markerに限定する。shipped workflowはparent ADR改定とimplementation acceptance追加なしに削除しない。
- update、retry、tooling uninstallからspec-history purgeへ到達できない。
- purgeを残す場合、独立command、明示confirmation、dry-run / apply、text / JSON、exit codeを定義する。
- deprecated aliasを残す場合、silent destructive executionを禁止し、具体的sunsetを持つ。
- cleanup-pendingをsuccess、warning、partial failureのどれとして返すかを明示する。
- tooling uninstallでinstallation recordを削除した後、独立purgeがtarget authorityを証明するevidenceを明示する。
- `tooling-absent-preserved-data`からのreinstall authorityとpublic diagnosticを明示する。

## スコープ

対象:

- `--remove-specs`のremove / deprecate / independent purge判断
- destructive confirmation contract
- dry-run / apply、text / JSON、exit code、cleanup-pending semantics
- compatibility window、sunset、migration / release guidance
- post-uninstall purge eligibilityとreinstall contract
- 後続Issueが削除・置換するpublic surfaceとtestのremoval receipt

対象外:

- uninstall / purge production実装
- user historyをtooling lifecycleへ再統合すること
- silent compatibility aliasによるpurge
- accepted ADRのuser history ownership再審議

## 失敗・境界条件

- compatibility名目で`--remove-specs`をsilent purgeへmappingすると、明示authorityなしの不可逆削除になる。
- normal uninstallとpurgeのresult modelが曖昧だと、partial failureをsuccess扱いし得る。
- foreign / invalid markerやunknown rootでdelete authorityを推定してはならない。
- installation record不存在だけをpurge authorityとしてはならない。

## 受け入れ条件

- [ ] `--remove-specs`の最終形をremove / deprecate / independent purgeの一つに確定している。
- [ ] purgeを残す場合、command名、confirmation、dry-run / apply、text / JSON、exit contractが確定している。
- [ ] public compatibility windowとsunsetがversionまたはdateで確定している。
- [ ] normal uninstallからspec-history purgeへの到達経路が許可されていない。
- [ ] deprecated aliasがsilent destructive executionを行わない。
- [ ] unknown ownershipのdefaultがpreserve-and-blockである。
- [ ] tooling uninstall後のindependent purge eligibility evidenceが確定している。
- [ ] `tooling-absent-preserved-data`からのreinstall contractが確定している。
- [ ] 後続Issueのremoval receiptがpublic option、intent mapping、retry guidance、testsを列挙している。
- [ ] accepted decisionがEpic Requirement / Design / Planへ反映されている。

## 制約・前提

- 本Issueはdecision-onlyでありproduction codeを変更しない。
- destructive purge authorityを未回答から推定しない。
- user-owned Initiatives、Artifacts、`.workbench`をtooling uninstall対象へ含めない。
- Issue #372を変更しない。
