---
種別: 実装計画書（Issue）
ID: "iss-00390"
タイトル: "Retained Workflow Ownership And Artifact Platform Validation Policy"
関連GitHub: ["#390"]
状態: "draft"
最終更新: "2026-08-31"
依存: ["requirement.md", "design.md"]
親: ["epic-00384", "init-local-00003"]
---

# iss-00390 Retained Workflow Ownership And Artifact Platform Validation Policy — 実装計画

詳細: [Issue Plan Guide](../../../../../../docs/authoring/issue-plan.md)

## Planning Level

`strict`。public workflow ownership、cross-platform保証、artifact provenance、merge-required gateを決定し、誤りがconsumer file破壊またはselector omissionにつながるため。human merge gateやsecurity boundaryを変更する提案が生じた場合は親へ戻す。

## 目標

consumer workflowとprovider CIのownerを分離し、build-once artifact、Linux canonical / macOS delta、additive required-check transitionの一意なpolicy contractを完成させる。

## 順序・依存

1. current shipped workflow、provider workflows、package build、lane selectorsをinventory化する。
2. workflow ownershipとartifact / platform triggerの選択肢を作る。
3. external required-check authority、stable context、shadow threshold、C7 failure-detection / C8 required-set enforcement canary、transition / rollbackを選択肢化する。
4. Product interviewでmaterial policyを受理する。
5. accepted decision、artifact / required-check receipt contract、change / removal handoffを作る。
6. Epic docsへ反映する。

`iss-00388`、`iss-00389`とは並行可能。後続inventoryのcollection / cost取得は並行可能だが、target lane / disposition finalization、uninstall bridge、install/update cutover、CI cutoverは本Issueのacceptanceへ依存する。

## 実装step

1. `src/spec_dock/assets/install_root/.github/workflows/ci.yml`とroot `.github/workflows/*.yml`のsource / projection関係を確認する。
2. current jobsごとにtrigger、OS、artifact build、executed node family、required statusを抽出する。
3. live external stateからruleset / branch protection / merge queue、effective required context set `U + old`、review requirement、変更ownerと実行権限を確認する。
4. seed / reusable projection / excludedのownership案とlifecycle authorityを比較する。
5. wheel / sdist / Linux / macOSのtrigger、build invocation、digest、retention、reuse案を比較する。
6. `U + old -> U + old + new -> U + new`、PR / merge-group enforcement canary、old removal、事前検証済みrestoration patch、C4 receipt binding producerの権限 / eventsを含むstate machineとrollbackを比較する。
7. Product ownerへ最推奨と代替を提示し、各policyを明示受理する。
8. accepted ADRまたは追補へownershipとreceipt schemaを記録する。
9. install/update Issueが変更するshipped asset、CI shadow / retirement、external check cutoverを別receiptにする。
10. Epic Requirement / Design / Planをactual decisionへ更新する。

## 検証

- current workflow graphのjob / selector / artifact build coverageを確認する。
- targetで同一candidate・OSのowner laneが重複しないことを論理検証する。
- artifact receiptからbuild invocation countと各output digestを再計算できることを確認する。
- missing / mismatch / wrong-sourceがfailする契約を確認する。
- human PR merge gateが維持されることを確認する。
- C7 detection canaryがnew checkのREDだけを証明し、old workflow削除前にnew-only requiredを証明し、C8のold + new required段階でenforcement canaryがmergeをblockする契約を確認する。
- `./spec-dock/scripts/spec-dock validate`と`git diff --check`を実行する。

workflow executionとperformance measurementは本IssueではN/A。decision-onlyでありYAMLを変更しないためである。

## rollback

未決の間はconsumer workflowをupdate / uninstall対象へ追加せず、現行required gateを変更しない。selector omissionが疑われる場合は全correctness portfolioをsingle processで実行するfail-closed gateを後続Issueのrollback contractとし、shardやapproved failureを復活させない。

## exit / handoff

- workflow ownership、trigger、artifact identity、build count、retention、lane owner、required-check transitionが受理されている。
- change / removal receiptsがinstall/updateとCIのownerへ分離されている。
- Epic docsが更新され、後続Issueの入力が一意である。
- 未回答があれば本Issueをopenのままにし、影響する後続Issueを作成・開始しない。
