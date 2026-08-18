---
種別: レポート（Issue）
ID: "iss-00368"
タイトル: "Recognized Workspace Reconciliation"
関連GitHub: ["#368"]
最終更新: "2026-08-19"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00365", "init-local-00003"]
---

# Result Summary

詳細: [Report Guide](../../../../../../docs/authoring/report.md)

## Outcome

- recognized target の `update` と `init --force` を `execute_recognized_distribution()` の単一路線へ切り替えた。
- read-only `WorkspaceAssessment` と blocker-free `ExecutableMutationPlan` を分離し、root / intent / contract / canonical plan digest に束縛した `.distribution-journal.json` を導入した。
- managed regular file / symlink / obsolete prune / generated version / active fallback を既存 descriptor-bound kernel で適用し、action checkpoint、staging lease、exact pre/postcondition から partial failure を forward recovery できるようにした。
- legacy `.distribution-retry.json` は、同一 root/package/operation の `preflight-complete` かつ staging lease なしの場合だけ one-way conversion し、それ以外と dual recovery state は mutation 前に拒否する。
- recognized flow から旧 scaffold callback、CLI-owned marker transition、plan 外の version write を除去し、fresh-only compatibility route は `iss-00369` の対象として到達不能のまま残した。
- README と shipped/dogfooding docs の recovery guidance を new journal contract に更新した。
- Strict bounded review で検出した journal action 改変、generated path traversal、parent rebind、plan 外 active mutation、no-op journal 作成を根因単位で修正し、回帰テストを追加した。
- Strict remediation で active fallback の generated refresh authority を事前観測した exact pointer identity に束縛し、外部・workbench symlink と asset capture 後の pointer rebind を operation 全体の write 前 blocker にした。
- Strict successor remediation で assessment と canonical plan の authority 一致を発行前に検証し、legacy marker 変換失敗時の prepared journal rollback、terminal journal の digest/action contract 再検証、recognized flow 全体の descriptor-bound root と visible identity 検証を追加した。
- retained-skill SHA failure は fixed point と Strict candidate の expected/actual 値がそれぞれ同一であることを `artifacts/retained-skill-baseline-comparison.json` に記録し、Issue 368 による回帰ではないことを再現可能にした。
- marker / journal の cleanup は対象を private quarantine 名へ no-replace rename し、移動後の exact identity が一致した場合だけ削除する。並行置換を検出した場合は置換 entry を元の予約パスへ復元して fail-closed にする。

## Verification

exact candidate の SHA と合否の正本は、当該 report 自身を含む `review_head_sha` に対して生成される Strict controller の candidate manifest / check attestation / certificate とする。report 内へ自己参照的な候補 SHA を固定せず、以下の手動確認は controller 実行前の診断証拠として区別する。

- [x] `make lint` — successor 候補 commit 前の診断で ruff check / format check / mypy が成功
- [x] `uv run pytest -q tests/unit/infra/test_managed_distribution.py` — 123 passed
- [x] `uv run pytest --run-full-regression tests/unit/infra/test_init_update.py -k 'update or force or distribution or issue_368'` — 127 passed
- [x] `uv run pytest --run-full-regression -q tests/cli_runtime/test_distribution_cutover.py` — 144 passed、1 failed。残る failure は fixed point と remediation SHA で expected/actual SHA が不変な Issue 359 retained-skill golden の既存不一致
- [x] `uv run pytest -q` — 1059 passed、1048 policy-skipped
- [x] `./spec-dock/scripts/spec-dock validate` — `nodes=227`
- [x] `git diff --check` — 成功
- Strict の最終合否は repository 外の append-only campaign ledger と certificate にのみ記録し、合否記録のために認証後の candidate を変更しない。

## Residual Risks / Follow-ups

- fresh target の同名 entrypoint は現行 compatibility route を維持しており、`iss-00369` で同じ Contract / Assessment / Kernel / Journal / Result seam へ移行する。
- deprovision、history purge、all-surface/Linux/package parity は親 Epic の順序どおり `iss-00370`〜`iss-00372` で扱う。
- full regression の既存 runtime/golden failures は本 Issue で修復しない。Issue 368 に関係する distribution cutover surface は、既存 retained-skill SHA golden 1 件を除いて通過している。
