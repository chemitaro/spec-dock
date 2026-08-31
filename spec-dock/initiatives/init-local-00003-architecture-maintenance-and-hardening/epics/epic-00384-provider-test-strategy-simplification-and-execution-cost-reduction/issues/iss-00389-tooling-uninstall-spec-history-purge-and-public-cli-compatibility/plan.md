---
種別: 実装計画書（Issue）
ID: "iss-00389"
タイトル: "Tooling Uninstall Spec History Purge And Public CLI Compatibility"
関連GitHub: ["#389"]
状態: "draft"
最終更新: "2026-08-31"
依存: ["requirement.md", "design.md"]
親: ["epic-00384", "init-local-00003"]
---

# iss-00389 Tooling Uninstall Spec History Purge And Public CLI Compatibility — 実装計画

詳細: [Issue Plan Guide](../../../../../../docs/authoring/issue-plan.md)

## Planning Level

`critical`。spec-history purgeは不可逆なuser data削除authorityを扱い、誤ったcompatibility mappingは広いdata lossを起こし得るため。purgeを完全廃止し、destructive aliasが存在しないとacceptedになった場合は実装Issue側で`strict`へ再評価できる。

## 目標

normal uninstall、任意の独立purge、post-uninstall eligibility / reinstall、public compatibilityを相互に分離し、後続実装がdelete authorityを一意に判断できるaccepted contractを完成させる。

## 順序・依存

1. 現行CLI / intent / result / retry surfaceをinventory化する。
2. remove / deprecate / independent purgeの選択肢を比較する。
3. destructive authority、post-uninstall evidence、reinstall、confirmation、sunset、result semanticsをProduct interviewで受理する。
4. accepted decisionとremoval receiptを作る。
5. Epic docsと後続uninstall Issue gateへ反映する。

`iss-00388`、`iss-00390`とは並行可能。後続inventoryのcollection / cost取得は並行可能だが、disposition / owner finalizationとuninstall cutoverは本Issueのacceptanceへ依存する。

## 実装step

1. `src/spec_dock/cli.py`と`managed_distribution.py`からuninstall / purge entrypointと到達経路を抽出する。
2. text / JSON / exit、dry-run / apply、confirmation、retry / cleanup-pendingを一覧化する。
3. installation record削除後に独立purgeが使えるtarget evidenceと、preserved-data workspaceのreinstall routeを比較する。
4. 各選択肢のdata-loss risk、compatibility cost、sunset、migration guidanceを比較する。
5. Product ownerへ最推奨と代替を提示し、material choiceを個別に受理する。
6. accepted ADRまたは追補へcommand contractとdelete authorityを記録する。
7. 後続Issueの削除対象option、intent、route、journal、test、docsをreceipt化する。
8. Epic canonical docsをactual decisionへ更新する。

## 検証

- 現行public surface inventoryとdecision matrixのcoverageを照合する。
- normal uninstall / update / retryからpurge authorityへの許可edgeが0であることを確認する。
- destructive pathすべてに明示confirmationとaccepted authorityがあることを確認する。
- post-uninstall purge evidenceとreinstall ownerの空欄が0であることを確認する。
- deprecated aliasのsunsetとnon-silent behaviorを確認する。
- `./spec-dock/scripts/spec-dock validate`と`git diff --check`を実行する。

production testとdestructive smokeは本IssueではN/A。decision-onlyであり削除操作を行わないためである。

## rollback

未受理の選択肢は実装しない。authorityが競合する場合はnormal uninstallをtooling-only / preserve-and-block側に固定し、purge実装Issueを開始しない。decision修正時もsilent destructive compatibilityを暫定策にしない。

## exit / handoff

- purgeの存在・public shape・confirmation・sunsetが明示受理されている。
- normal uninstallのdelete setが固定されている。
- result / error contractとremoval receiptが完成している。
- post-uninstall purge eligibilityとreinstall contractが完成している。
- Epic docsが更新され、後続uninstall Issueの入力が一意である。
- 未回答があれば本Issueをopenのままにし、後続Issueを作成・開始しない。
