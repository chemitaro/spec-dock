---
種別: レポート（Issue）
ID: "iss-00368"
タイトル: "Recognized Workspace Reconciliation"
関連GitHub: ["#368"]
最終更新: "2026-08-18"
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

## Verification

- [x] `make lint` — ruff check / format check / mypy が成功
- [x] `uv run pytest tests/unit/infra/test_managed_distribution.py` — 117 passed
- [x] `uv run pytest --run-full-regression tests/unit/infra/test_init_update.py -k 'update or force or distribution or issue_368'` — 124 passed
- [x] `uv run pytest --run-full-regression tests/cli_runtime/test_distribution_cutover.py` — Issue 368 対応後は 143 passed、1 failed。残る failure は Issue 359 retained-skill SHA golden と current provider bytes の既存不一致で、本 Issue の変更対象外
- [x] `uv run pytest` — 1053 passed、1044 policy-skipped
- [x] `./spec-dock/scripts/spec-dock validate` — `nodes=227`
- [x] `git diff --check` — 成功
- [ ] ChatGPT Final Quality Gate Strict — bounded review remediation 後の exact candidate SHA で再実施中

## Residual Risks / Follow-ups

- fresh target の同名 entrypoint は現行 compatibility route を維持しており、`iss-00369` で同じ Contract / Assessment / Kernel / Journal / Result seam へ移行する。
- deprovision、history purge、all-surface/Linux/package parity は親 Epic の順序どおり `iss-00370`〜`iss-00372` で扱う。
- full regression の既存 runtime/golden failures は本 Issue で修復しない。Issue 368 に関係する distribution cutover surface は、既存 retained-skill SHA golden 1 件を除いて通過している。
