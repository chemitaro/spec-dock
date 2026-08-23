---
種別: レポート（Issue）
ID: "iss-00369"
タイトル: "Fresh Distribution Provisioning"
関連GitHub: ["#369"]
最終更新: "2026-08-23"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00365", "init-local-00003"]
---

# Result Summary

詳細: [Report Guide](../../../../../../docs/authoring/report.md)

## Outcome

Issue 369 の fresh provisioning を、`init`、`init --force`、`update` の三つの entrypoint から同一の effective `fresh` intent として実行する構成へ切り替えた。`spec-dock` が absent、exact empty、preserved-specs の各状態で、top-level bootstrap 以外の変更を forward guard と operation journal に束縛した shared service が担当する。

fresh contract には current/scaffold/generated assets、active fallback、version、root Workbench seed、`spec-dock/initiatives`・`spec-dock/active`・`spec-dock/.agent`・`spec-dock/.workbench` と asset parent の required-directory action を含めた。recognized `update` / `init --force` の互換経路では Workbench seed の backfill を行わず、旧 fresh callback・recursive writer・plan 外 version write を fresh call graph から除去した。

P1 再レビューで検出された fresh Workbench seed の非所有 retry における構造 identity 欠落も解消した。外部に先行配置された provider-identical seed を採用する場合は、`device`・`inode`・`ctime_ns`・`link_count` を write-ahead journal へ保存し、親 directory の出現と plan digest の実行時 identity を同一契約で扱う。これにより、同一内容の別 inode 置換、link topology 変更、unknown child を非破壊のまま fail closed とし、許可された seed だけを同一 plan retry で採用できる。

## Verification

- `make lint`: pass（ruff、format check、mypy）
- `uv run pytest -q`: pass（1284 passed / 1119 skipped、implementation candidate `7605fdc19370ae581b64b6b5c302fcfdfe4925f2`）
- `./spec-dock/scripts/spec-dock validate`: pass（nodes=227）
- `git diff --check`: pass
- `uv run python spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00365-specdock-structural-integrity-rearchitecture-and-regression-baseline-recovery/issues/iss-00368-recognized-workspace-reconciliation/artifacts/verify-full-regression.py`: pass（candidate `7605fdc19370ae581b64b6b5c302fcfdfe4925f2`、raw pytest `27 failed / 2328 passed / 48 skipped`、検証器終了コード0）。27件の失敗はすべて full-regression ledger の approved failure signatures と完全一致し、前回の unexpected failure（provider-identical hard-link Workbench seed retry）は解消された。検証器は現行 candidate で27件の approved failure signatures 完全一致を確認した。

## Residual Risks / Follow-ups

- full-regression は 2403 tests（27 failed / 2328 passed / 48 skipped）を一括実行した。27件の approved failure ledger は Issue 368 から継承した本 Issue の変更範囲外であり、現行 candidate SHA 上で署名完全一致を確認済み。
- Issue 369 の fresh provisioning 変更に起因する unexpected failure/error は検出されていない。
- fresh Workbench seed の親 directory が assessment 後に出現するケースでは、pending `ensure-directory` と子 action の閉集合・exact identity を満たす場合だけ採用する。未知の子、symlink/file parent、内容変更、別 inode 置換は guard/journal を保持して拒否する。
- marker/journal の terminal cleanup failure では、journal と forward guard を残して同一 plan の再試行へ進む。異なる root、contract、plan、または未知の child は fail closed とする。
- Strict v2 の advisory P2 として、protocol-1 の pending write が最初の current publication 前に protocol-2へ昇格されない境界が残る。P0/P1ではなく、将来のprotocol migration hardeningとしてIssue 370以降で扱う。
