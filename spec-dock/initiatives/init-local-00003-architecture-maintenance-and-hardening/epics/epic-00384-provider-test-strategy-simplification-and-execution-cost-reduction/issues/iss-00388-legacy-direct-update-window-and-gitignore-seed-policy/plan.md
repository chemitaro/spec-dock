---
種別: 実装計画書（Issue）
ID: "iss-00388"
タイトル: "Legacy Direct Update Window And Gitignore Seed Policy"
関連GitHub: ["#388"]
状態: "draft"
最終更新: "2026-08-31"
依存: ["requirement.md", "design.md"]
親: ["epic-00384", "init-local-00003"]
---

# iss-00388 Legacy Direct Update Window And Gitignore Seed Policy — 実装計画

詳細: [Issue Plan Guide](../../../../../../docs/authoring/issue-plan.md)

## Planning Level

`strict`。public compatibility、既存workspace migration、`init --force`、consumer-owned file collisionを決定し、誤りが後続destructive updateのblast radiusを広げるため。Product判断がfilesystem authorityやdata lossを拡張する場合は`critical`へ再評価する。

## 目標

実装者が推測せずに実装できる、有限で検証可能なlegacy / `.gitignore` decision contractとremoval handoffを完成させる。

## 順序・依存

1. accepted ADRとcurrent manifest / parser / assetのauthorityを確認する。
2. known workspace evidenceを収集し、factとassumptionを分ける。
3. legacy window、sunset、`.gitignore` matrix、`init --force`、compatibilityの選択肢を作る。
4. Product interviewで一つずつ受理する。
5. accepted decision Artifactを作成し、Epic docsへ反映する。
6. 後続install/update Issueのstart gateとremoval receiptを確定する。

`iss-00389`、`iss-00390`とはdecision inputが独立しており並行可能。後続inventoryとinstall/update cutoverは本Issueのaccepted decisionへ依存する。

## 実装step

1. `src/spec_dock/assets/managed_distribution.json`、`src/spec_dock/cli.py`、`.gitignore` asset、現行testsから状態分類とpublic surfaceを抽出する。
2. legacy候補ごとにexact version/date/tree evidence、識別不能条件、support endを記録する。
3. `.gitignore`の5状態と`init --force`を直積にせず、必要なcollision rowsだけを明示する。
4. 各material choiceについて最推奨、代替、利用者影響、migration cost、failure modeを提示してinterviewする。
5. 回答をdecision-candidateへ反映し、整合確認後にaccepted ADRまたは既存ADRの追補として受理する。
6. 後続Issueが削除するmanifest section、adapter、fixture、test familyをremoval receiptへ固定する。
7. Epic Requirement / Design / Planのgateとcandidate定義をactual decisionへ更新する。

## 検証

- decision matrixのstateが相互排他的か確認する。
- known evidenceを各rowへ割り当て、unclassified / multiple-matchが0であることを確認する。
- sunset、owner、blocked diagnostic、removal ownerの空欄が0であることを確認する。
- unknown / collisionでmutation authorityが付与されていないことを確認する。
- `./spec-dock/scripts/spec-dock validate`を実行する。
- `git diff --check`とcanonical docsのlink / ID整合を確認する。

production test、build、migration smokeは本IssueではN/A。codeを変更しないためである。

## rollback

accepted前は後続mutation Issueを開始しない。accepted後に証拠競合が見つかった場合はapply routeを停止し、decisionを再審議する。unknown stateをsupport対象へ自動昇格しない。

## exit / handoff

- Product ownerが全material choiceを明示受理している。
- accepted authority、decision matrix、sunset、removal receiptが揃っている。
- Epic docsがactual decisionへ更新されている。
- 後続install/update Issueの開始条件と入力が一意である。
- 未回答が残る場合、本Issueはdraft/openのままにし、後続Issueを作成・開始しない。
