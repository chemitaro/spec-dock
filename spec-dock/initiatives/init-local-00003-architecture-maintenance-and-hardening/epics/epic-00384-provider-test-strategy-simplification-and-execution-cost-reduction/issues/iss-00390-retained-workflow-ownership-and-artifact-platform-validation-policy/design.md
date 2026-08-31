---
種別: 設計書（Issue）
ID: "iss-00390"
タイトル: "Retained Workflow Ownership And Artifact Platform Validation Policy"
関連GitHub: ["#390"]
状態: "draft"
最終更新: "2026-08-31"
依存: ["requirement.md"]
親: ["epic-00384", "init-local-00003"]
---

# iss-00390 Retained Workflow Ownership And Artifact Platform Validation Policy — 設計

詳細: [Design Guide](../../../../../../docs/authoring/design.md)

## 設計目標

consumer workflow ownership、provider CI lane ownership、candidate artifact identityを分離して正本化し、同じcandidate / OS / contractを一度だけ証明する後続execution graphのpolicy inputを作る。

## Current / Target

Current:

- shipped consumer workflowのlifecycle ownerが未決である。
- ordinary / parity / Full Regression間でnodeとartifact workが重複する。
- wheel / sdist / macOS triggerとbuild countの意味が未確定である。

Target:

- consumer workflowのownershipとupdate / uninstall authorityが一意である。
- artifact policyがcandidate source SHA、build invocation、output digest、reuse、retentionを定義する。
- Linux canonical laneとmacOS delta laneのcontract ownershipが排他的である。

## 責務・Interface

- workflow ownership decision: seed / projection / excludedとlifecycle authority。
- artifact policy: build trigger、invocation count、outputs、digests、transfer owner。
- platform policy: Linux canonicalとmacOS deltaの対象・trigger・budget。
- implementation handoff: shipped asset changeはinstall/update Issue、provider CI changeはCI cutover Issueが所有する。

## data / failure

artifact receiptは少なくともcandidate full SHA、build invocation ID、output kind、SHA-256、builder identity、created-at、consumer lanesを持つ。missing / mismatch / wrong sourceはtest開始前にfailする。lane receiptはexecuted node setとOSを持ち、duplicate判定可能にする。

## 変更対象

本Issue docs、decision Artifact、受理後のEpic docsだけを変更する。`.github/workflows/*.yml`、`src/spec_dock/assets/install_root/`、reporter、testsは後続Issueが変更する。

## 移行・互換性・rollback

workflow ownership decisionにdeprecationが必要なら具体的windowを持つ。未決の間はnormal update / uninstallへconsumer workflow authorityを追加せず、後続CI cutoverを開始しない。

## testability

- current workflow graphとshipped assetをread-onlyで比較する。
- 各node family / artifact buildのcurrent lane重複をpolicy inputとして可視化する。
- target ownershipがexisting pathへ一意にmappingできるか確認する。
- artifact receiptからsource / digest / build count / consumer laneを再計算できるか確認する。

## risk

- consumer workflowをprovider-ownedと誤認すること。
- platform差と単なる重複実行を混同すること。
- build countをoutput file数とcommand invocation数で曖昧にすること。
- noisy runner上のwall timeをhard quota referenceと混同すること。
