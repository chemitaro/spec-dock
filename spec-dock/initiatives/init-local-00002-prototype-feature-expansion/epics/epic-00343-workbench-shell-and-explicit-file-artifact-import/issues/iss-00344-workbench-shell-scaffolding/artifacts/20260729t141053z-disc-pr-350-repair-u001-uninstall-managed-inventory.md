---
種別: disc
ID: "20260729t141053z-disc"
タイトル: "PR 350 Repair Unit U001 Uninstall Managed Inventory"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-07-29"
親: ["iss-00344"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260729t141053z-disc PR 350 Repair Unit U001 Uninstall Managed Inventory

## Repair Unit Contract

- source_batch: `20260729t141008z-pr-repair-batch`
- unit_id: `U001`
- covered_ids: `R001` / `F001`
- source_links: PR #350 review comment `3675040563`、`src/spec_dock/cli.py`
- failure_class: `review_feedback:uninstall-managed-inventory`
- risk_class: `blocking`
- disposition: `fix-now`

## Validity Analysis

- findingはvalid P1である。
- fresh initは`spec-dock/.workbench/README.md`をprovider templateから生成する。
- `_build_scaffold_uninstall_sources()`はmanaged directories、`.gitignore`、`spec-dock.version`だけを列挙し、このfresh-only assetを含めない。
- その結果、unchanged READMEがunmanagedとして保存され、`--remove-specs`後にWorkbench directoryとretry stateを残し得る。

## Need-To-Fix Decision

- yes。このPRが追加したmanaged outputと公開uninstall契約の直接的な非対称であり、このPR内で閉じる。
- Workbench payload、modified README、既存scope backfill、Issue 345/346実装にはscopeを広げない。

## Root Cause

- generation inventoryとuninstall inventoryのownership gap。
- root Workbench READMEはfresh-only copyで生成される一方、uninstall source enumerationへexact path/expected bytesが登録されていない。

## Options Considered

### Option A: exact assetを既存uninstall inventoryへ追加

- Pros: 既存exact-match removalとmismatch-preservationを再利用できる。
- Pros: generation/uninstall ownershipが対称になる。
- Cons: focused removal/preservation regressionが必要。

### Option B: `.workbench`を無条件再帰削除

- Pros: 実装は単純。
- Cons: payloadや利用者変更を削除し、optional/opaque Workbench contractを破壊する。
- Decision: reject。

## Recommended Design

- provider root `.workbench/README.md`のexact relative pathとexpected bytesを`_build_scaffold_uninstall_sources()`へ追加する。
- 既存の`_add_exact_match_uninstall_action()`へ流し、unchanged fileだけをmanaged removal対象にする。
- modified READMEとpayloadは既存unmanaged preservationで残す。
- 新しい削除frameworkやrecursive Workbench ownershipは追加しない。

## Implementation Plan

- fresh ChatGPT-Use consultation完了後、`src/spec_dock/cli.py`とfocused uninstall testsだけをdev-coderへ委任する。
- defectを再現するRedを先に固定する。
- exact asset inventory追加でGreen化する。
- Issue report/repair evidence以外のcanonical specsは変更しない。

## Validation Plan

- fresh init + `uninstall --apply --remove-specs`でunchanged root README、Workbench directory、retry markerが残らない。
- modified root READMEはpreserved/unmanagedとして残る。
- existing retry/idempotencyとbounded cleanup testsがpassする。
- Issue 344 aggregate、`make lint`、default `uv run pytest`がpassする。
- push後のnew exact headへfixed PR observationをpost-onceで実行する。

## Implementation Result

- pending fresh consultation and bounded worker.

## Commit Evidence

- pending.

## Re-observation Result

- pending.

## Residual Risk / Follow-up

- cleanup orderingとempty directory/retry marker除去をfocused regressionで確認する。
- bare opt-in full regressionとcandidate-wheel consumer E2EはIssue 346所有のまま。

## ADR Triage

- ADR candidate: no
- hard to reverse: no
- surprising without context: no
- real tradeoff: no
- adoption target: repair batch、Issue report Evidence Adoption Ledger、PR observation
