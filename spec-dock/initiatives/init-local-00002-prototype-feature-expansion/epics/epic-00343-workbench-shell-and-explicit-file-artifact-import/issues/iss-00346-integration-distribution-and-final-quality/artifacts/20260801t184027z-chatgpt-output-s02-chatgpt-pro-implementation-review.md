# S02 ChatGPT Pro implementation review

## Review scope and head binding

GitHub connector確認の結果、branch `iss-00346-integration-distribution-and-final-quality` のcurrent pushed HEADは `8dd526ab477191278c15c61a4cb32fdd58fafdc5`、S02 executable/test commitは `1650c73c53f7397cc5f29d5262479f860125c9d6`。`8dd526ab`はreport-only successorであり、production patchはない。レビュー対象はplan §9.0–§9.6、current report、S02追加を含む `tests/integration/test_epic_00343_distribution.py` とupdate/sync周辺挙動に限定した。

## Findings

### [P1] graph snapshotに`deps-raw.puml`がない

`_snapshot_graph()` は`.agent/**`、`tree-all.puml`、`tree.puml`、`deps-issues.puml`、`dashboard.md`を保存していたが、syncが生成・更新する`spec-dock/deps-raw.puml`を含めていなかった。これによりupdateがdeps-rawだけを改変してもgraph equalityがGreenになり、planのdeps preservationを閉じられない。

### [P1] updateが管理するroot install assetsのsnapshotが不足

`_snapshot_managed_assets()` は`spec-dock/{docs,templates,scripts,system}`、`.gitignore`、`spec-dock.version`だけを比較していた。top-level updateはinstall_rootから`.agents/**`、`.codex/**`、`.github/**`等も同期するため、これらの変更をguide-only delta検証が検知できない。

### [P1] successor HEADに対するS02 evidence ledgerが未完成

reportはimplementation commitを`1650c73c`と記録していたが、current pushed HEADはreport-only successor `8dd526ab`だった。またhistorical option、S02 closure ID mapping、Step/Test Contract Closure、Delegated Worker Evidenceの具体的な完了行が不足していた。

## S02 closure verdict

**fail**。P1が3件あるためS02はcloseせず、S03はblockedとする。ただしsynthetic hierarchy、README absent matrix、ignored payload、stale guide、preflight validate/sync、no-backfill、future shell、path-specific negativeの主要経路は確認できた。Issue 345の既存docs-boundary unit failureはS02差分外であり、今回のfail理由でも修正対象でもない。

## Required follow-ups

1. `deps-raw.puml`をgraph snapshotへ追加する。
2. updateが管理するroot `.agents/**`、`.codex/**`、`.github/**`等をmanaged before/after manifestへ含め、guide-only deltaを検証する。
3. reportを最新successor HEADへ再束縛し、`historical_option_used=no`、S02 test cards/closure IDs、worker/no-production-repair、Step/Test Contract Closure、reviewer gateを具体値で記録する。
4. 修正をcommit/pushし、focused/full integration、ruff、diff-check、同じbounded scopeのfresh Pro reviewを実施する。Issue 345 docs failureは変更しない。

## Uncertainty and non-findings

pytestはレビュー中に独立実行していない。報告済みの4/8 passedとunit selector結果はobserved evidenceとして扱う。S02はtest-onlyで、wheel ZIP由来のtemplate bytes、installed runtime、fixture分離、payload状態、future README equality、negative sensitivityに追加のP0やproduction regressionはない。
