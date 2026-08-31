---
種別: 要件定義書（Issue）
ID: "iss-00388"
タイトル: "Legacy Direct Update Window And Gitignore Seed Policy"
関連GitHub: ["#388"]
状態: "draft"
最終更新: "2026-08-31"
親: ["epic-00384", "init-local-00003"]
---

# iss-00388 Legacy Direct Update Window And Gitignore Seed Policy — 要件定義

詳細: [Requirement Guide](../../../../../../docs/authoring/requirement.md)

## 目的

4 disposable rootsと2 fixed skill slotsへのcutoverに先立ち、legacy direct-updateを認識する有限window、package / workspace compatibility、active legacy recovery、bridge sunsetと、`spec-dock/.gitignore`のinit seed / collision contractをProduct判断として確定する。実装者がhistorical compatibilityやdowngrade behaviorを推測せず、後続uninstall-first bridgeとinstall/update Issueが一意なmigration contractを実装できる状態を成果とする。

## 背景

accepted ADR `20260831t005139z-adr` はper-file historical identityをsteady stateから廃止し、marker導入前のcurrent workspaceだけを期限付きone-shot migrationで認識すると定めた。一方、対応するversion/date window、認識可能なtree evidence、sunset、4 roots外の`spec-dock/.gitignore`、`init --force`のauthorityは未決である。

現行`managed_distribution.json`にはrecognized workspace version、historical identity、obsolete exact fileが含まれる。この範囲を根拠なく無期限に移植するとEpicのstate-space縮小を失い、狭すぎると既存workspaceを更新不能または誤上書きする。

## 観測可能な要件

- fresh、current-supported、legacy-supported、legacy-expiredを相互排他的に判定できる。
- legacy-supportedはexact version/date/tree evidenceの有限集合で説明でき、sunset versionまたはdateを持つ。
- markerlessなcurrent 2 skill slotsをmigration対象とする場合、そのexact tree evidenceとcollision時の停止条件を持つ。
- `spec-dock/.gitignore`がabsent、provider-identical、consumer-modified、symlink、unexpected typeの各状態について、preserve / block / explicit overwriteの一つを決定する。
- `init --force`がcustom `.gitignore`とlegacy workspaceへ持つauthorityを明示する。
- install/updateのtext、JSON、exit codeを変更する場合、breaking changeまたはdeprecation windowを明示する。
- `P0` / `P1` / `P2` / `P3`とcanonical lifecycle state、全public operation、inspect / dry-run / apply execution modeのallow / fail-closed / N/A matrixを確定する。retry、legacy alias、`init --force`もoperationとして列挙し、support classificationは別axisとしてstateへ一意にmappingする。
- active legacy journalをbounded recovery-only adapterで扱うか、last-compatible packageへpinするかを決定する。
- legacy reader / fixtures / testsをEpic内でsunsetするか、owner / expiry付きfollow-upへ渡すかを決定する。

## スコープ

対象:

- legacy direct-updateのversion/date window
- markerless current roots / skill slotsの有限な認識条件
- one-shot migrationのsunset
- `.gitignore` init seed、collision、customization policy
- `init --force`とpublic diagnostic / compatibility policy
- accepted decision Artifactと後続Issueへのremoval receipt契約
- old packageによるnew workspace mutationの禁止とdiagnostic
- uninstall-first bridgeの有限reader contract、recovery owner、sunset owner

対象外:

- production code、tests、assets、workflowの変更
- arbitrary historical version catalogの追加
- telemetryや実利用証拠なしで「互換性不要」と推定すること
- accepted ADRの4 roots、2 slots、user-history protectionの再審議

## 失敗・境界条件

- 識別不能なworkspaceをlegacy-supportedと推定すると、未知のuser-owned contentを破壊し得る。
- legacy windowを無期限にするとhistorical identityとtestsがsteady stateへ残る。
- `.gitignore`をprovider-owned rootと同様に全量置換するとconsumer customizationを黙って失う。
- decision同士が矛盾する場合、後続install/update Issueを開始しない。

## 受け入れ条件

- [ ] fresh / current-supported / legacy-supported / legacy-expiredの判定表がaccepted authorityに記録されている。
- [ ] legacy-supportedのversionまたはdate window、tree evidence、sunsetが有限に確定している。
- [ ] `.gitignore`の全collision matrixと`init --force` authorityが確定している。
- [ ] public text / JSON / exit compatibility windowが必要な場合は具体的versionまたはdateで確定している。
- [ ] package / workspace compatibility matrixと、old packageのnew state fail-closed contractが確定している。
- [ ] exact P0 artifactが満たすmutation-zero policyと、C5 probeが成立しない場合にworkspace format / release sequenceを変更するauthorityが確定している。canonical schema / fixtureの作成・probe実行はC5が所有する。
- [ ] `package_generation × lifecycle_state × public_operation × execution_mode`の全cellにauthority、evidence、diagnostic、recovery / implementation / removal ownerがある。
- [ ] active legacy recoveryをadapterまたはlast-compatible packageのどちらが所有するか確定している。
- [ ] bridge sunsetをEpic内で行うかfollow-upへ渡すか、owner / expiryを含めて確定している。
- [ ] unknown stateのdefaultがmutation前のpreserve-and-blockである。
- [ ] 後続uninstall bridge / install-update Issueが削除するmanifest section、migration adapter、fixture、test familyがremoval receiptとして列挙されている。
- [ ] accepted decisionがEpic Requirement / Design / Planへ反映されている。

## 制約・前提

- 本Issueはdecision-onlyであり、production実装やtest削除を行わない。
- Product ownerの明示受理前に選択肢をaccepted扱いしない。
- user-owned history、unknown paths、shared `.agents/skills` parentを変更対象へ含めない。
- Issue #372のcandidate、canonical docs、acceptance evidenceを変更しない。
