---
種別: 設計書（Issue）
ID: "iss-00388"
タイトル: "Legacy Direct Update Window And Gitignore Seed Policy"
関連GitHub: ["#388"]
状態: "draft"
最終更新: "2026-08-31"
依存: ["requirement.md"]
親: ["epic-00384", "init-local-00003"]
---

# iss-00388 Legacy Direct Update Window And Gitignore Seed Policy — 設計

詳細: [Design Guide](../../../../../../docs/authoring/design.md)

## 設計目標

後続cutoverが実装できる有限なcompatibility modelをProduct decisionとして構造化する。steady stateのroot / slot ownershipと期限付きmigration recognitionを分離し、`.gitignore`を4 disposable rootsへ暗黙に含めない。

## Current / Target

Current:

- historical manifestとper-file identityが複数世代を認識する。
- markerless workspaceとskill slotのsupport windowが確定していない。
- `.gitignore` collisionと`init --force`のauthorityが未確定である。
- active legacy recoveryとold package / new workspaceのdowngrade behaviorが未確定である。

Target:

- `fresh | current-supported | legacy-supported | legacy-expired | unknown`の有限分類を持つ。
- legacy recognitionはexact evidenceとsunsetを持つone-shot adapterだけが所有する。
- `.gitignore`は独立したinit-seed contractを持ち、unknown / custom stateを黙って上書きしない。
- `P0` / `P1` / `P2` / `P3` compatibility matrix、recovery owner、finite bridge sunsetを持つ。
- support classificationとcanonical lifecycle stateを別axisとし、一意なmappingを持つ。

## 責務・Interface

- accepted decision Artifact: Product choice、根拠、effective window、sunset、collision matrixを正本化する。
- migration handoff: 後続install/update Issueへrecognition inputs、blocked states、削除期限を渡す。
- removal receipt: 旧manifest section、adapter、fixtures、testsの削除ownerを指定する。
- CLI handoff: text / JSON / exit compatibilityの変更が必要な場合だけ具体的windowを渡す。
- lifecycle handoff: `legacy-ready`、`ready-v2`、`updating-v2`、`legacy-recovery-active`ごとのallow / block / diagnosticをuninstall-first bridgeとinstall/update ownerへ渡す。

本Issueはproduction module interfaceを確定しない。後続Issueはaccepted decisionをrepository styleに合わせたdeep interfaceへ実装する。

## data / failure

decision matrixの各rowは少なくとも次を持つ。

```text
state
observable evidence
allowed operation
mutation authority
diagnostic
support end
package generation
workspace state
recovery owner
implementation owner
removal owner
```

evidenceが欠落・競合・不正な場合は`unknown`とし、mutation前にpreserve-and-blockする。version文字列だけでownershipを証明しない。

matrixは`package_generation × lifecycle_state × operation`をcanonical authorityとし、`absent`、`legacy-ready`、`tooling-absent-preserved-data`、`ready-v2`、`updating-v2`、`legacy-recovery-active`、`blocked`と、install、init-force、update、uninstall、purge、dry-runの全cellを埋める。exact P0 artifactを実行してnew fixtureへのmutation-zeroを確認し、実現不能な能力をdecisionで付与しない。

## 変更対象

変更するもの:

- 本IssueのRequirement / Design / Plan
- decision / interview Artifact
- decision受理後のEpic canonical docs

変更しないもの:

- `src/spec_dock/` production code
- `tests/`
- provider assets、dogfooding projection、workflows
- Issue #372

## 移行・互換性・rollback

本Issue自身はmigrationを実行しない。decisionがacceptedされるまでは現行behaviorを変更せず、後続Issueをblockする。accepted decisionに欠陥が見つかった場合は、実装開始前ならdecisionを再審議し、実装開始後ならapply routeを停止して親Epicへ戻す。

## testability

- current manifest / assets / known workspace evidenceから各decision rowを機械的に識別できるかread-onlyで確認する。
- rowの重複、未分類state、sunset欠落、unknown時のmutation許可を検出する。
- removal receiptが実在するsymbol / manifest section / test familyを指すか確認する。
- package / workspace matrixにmutation authorityの空白や複数ownerがないか確認する。

## risk

- 実利用workspace evidenceが不足したままwindowを決めること。
- migration adapterをsunsetなしでsteady stateへ残すこと。
- `.gitignore` policyを4 rootsの全量置換contractから推定すること。
- public compatibilityとfilesystem ownershipを一つの曖昧な選択へまとめること。
- active legacy recoveryを新formatへ推測変換すること。
- bridge sunsetを決めずdual-readerをsteady stateへ残すこと。
