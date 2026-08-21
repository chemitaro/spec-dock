---
種別: レポート（Issue）
ID: "iss-00369"
タイトル: "Fresh Distribution Provisioning"
関連GitHub: ["#369"]
最終更新: "2026-08-22"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00365", "init-local-00003"]
---

# Result Summary

詳細: [Report Guide](../../../../../../docs/authoring/report.md)

## Outcome

Issue 369 の fresh provisioning を、`init`、`init --force`、`update` の三つの entrypoint から同一の effective `fresh` intent として実行する構成へ切り替えた。`spec-dock` が absent、exact empty、preserved-specs の各状態で、top-level bootstrap 以外の変更を forward guard と operation journal に束縛した shared service が担当する。

fresh contract には current/scaffold/generated assets、active fallback、version、root Workbench seed、`spec-dock/initiatives`・`spec-dock/active`・`spec-dock/.agent`・`spec-dock/.workbench` と asset parent の required-directory action を含めた。recognized `update` / `init --force` の互換経路では Workbench seed の backfill を行わず、旧 fresh callback・recursive writer・plan 外 version write を fresh call graph から除去した。

## Verification

- `make lint`: pass（ruff、format check、mypy）
- `uv run pytest -q`: pass（1259 passed / 1119 skipped）
- `./spec-dock/scripts/spec-dock validate`: pass（nodes=227）
- `git diff --check`: pass
- `uv run python spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00365-specdock-structural-integrity-rearchitecture-and-regression-baseline-recovery/issues/iss-00368-recognized-workspace-reconciliation/artifacts/verify-full-regression.py`: pass（candidate `e7e1afffd721915df42e8c10de4322ab47e4a241`、`27 failed / 2303 passed / 48 skipped`、`14884.54s (4:08:04)`）。27件の失敗はすべて full-regression ledger の approved failure signatures と一致し、検証器は `verified 27 approved failure signatures` を出力した。

## Residual Risks / Follow-ups

- full-regression は 2378 tests（27 failed / 2303 passed / 48 skipped）を一括実行し約4時間8分を要した。27件の approved failure ledger は Issue 368 から継承した本 Issue の変更範囲外であり、candidate SHA 上で署名一致を確認済み。
- Issue 369 の fresh provisioning 変更に起因する unexpected failure/error は検出されていない。
- marker/journal の terminal cleanup failure では、journal と forward guard を残して同一 plan の再試行へ進む。異なる root、contract、plan、または未知の child は fail closed とする。
