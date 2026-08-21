---
種別: レポート（Issue）
ID: "iss-00369"
タイトル: "Fresh Distribution Provisioning"
関連GitHub: ["#369"]
最終更新: "2026-08-21"
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
- `uv run pytest -q`: pass（1247 passed / 1109 skipped）
- `./spec-dock/scripts/spec-dock validate`: pass（nodes=227）
- `git diff --check`: pass
- full-regression ledger: clean candidate SHA での最終実行をコミット後に実施予定。作業ツリーが dirty な状態での予備実行では 2278 passed / 48 skipped / 30 failed となり、Issue 369 による marker retry と legacy hidden workspace の期待値を追加修正した。

## Residual Risks / Follow-ups

- full-regression は 2356 tests を一括実行するため、予備実行で約3時間50分を要した。clean candidate で同じ ledger verifier を再実行し、approved failure signatures との一致を確認する。
- Issue 368 から継承した approved failure ledger の既知失敗は本 Issue の変更範囲外として維持する。
- marker/journal の terminal cleanup failure では、journal と forward guard を残して同一 plan の再試行へ進む。異なる root、contract、plan、または未知の child は fail closed とする。
