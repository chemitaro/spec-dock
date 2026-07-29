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

- fresh init + `uninstall --apply --remove-specs`でunchanged root READMEとempty Workbench directoryが残らず、retry markerは有効なままsecond rerunが成功する。
- modified root READMEはpreserved/unmanagedとして残る。
- existing retry/idempotencyとbounded cleanup testsがpassする。
- Issue 344 aggregate、`make lint`、default `uv run pytest`がpassする。
- push後のnew exact headへfixed PR observationをpost-onceで実行する。

## ChatGPT Consultation / Orchestrator Disposition

- consultation_status: fresh
- consultation_id: `iss-00344-pr350-u001-consultati`
- bound_head_sha: `818a48303f7a59b625d10681e6a2182767828279`
- evidence: `artifacts/20260729t142442z-chatgpt-output-pr-350-u001-blocking-repair-consultation-818a4830.md`
- validity: partially-valid
- REC-001 disposition: partial-use
- adopted:
  - exact target/source mappingを既存uninstall inventoryへ追加する。
  - unchanged removal、modified preservation、payload preservation、dry-run classificationの4 cases。
  - existing exact-match helperとbounded empty-directory cleanupを再利用する。
- rejected:
  - retry markerをF001で削除またはreorderする。marker persistenceは既存idempotent rerun契約であり、root README inventory gapの原因ではない。
- strategy_delta:
  - S350-001をgeneration/uninstall inventory symmetryだけへ限定し、markerは有効なままsecond remove-specs rerunを成功させる。

## Implementation Result

- `src/spec_dock/cli.py`へprovider root Workbench READMEのexact target/source mappingを2行で追加した。
- `tests/unit/infra/test_init_update.py`へ4 focused casesを追加した。
- Red: 4 casesすべて`unmanaged` / `preserved`分類で`4 failed`。
- Green: focused `4 passed`、selected retry/cleanup/symlink `3 passed`、existing root Workbench `4 passed`。
- Aggregate: installer selection `46 passed / 518 deselected`、CLI uninstall full `8 passed`、Issue focused `11 passed`、node/copy `52 passed`。
- Static/default: `make lint` pass、default `672 passed / 2051 skipped`、diff-check pass。
- retry marker lifecycle/order、symlink/non-regular/read-error preservation、payload opacityは変更していない。

## Commit Evidence

- candidate commit pending。

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
