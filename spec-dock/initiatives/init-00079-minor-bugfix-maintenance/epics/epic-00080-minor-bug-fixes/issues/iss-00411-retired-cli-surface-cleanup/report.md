---
種別: レポート（Issue）
ID: "iss-00411"
タイトル: "Remove retired SpecDock CLI surfaces after scope active work cutover"
関連GitHub: ["#411"]
最終更新: "2026-09-28"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00080", "init-00079"]
---

# Result Summary

詳細: [Report Guide](../../../../../../docs/authoring/report.md)

## Outcome

旧 CLI の app/parser/registry/dispatch/bootstrap、旧コマンド、旧 directory installer とそれら専用の test / fixture を撤去した。現行の固定外部エンジン、44 leaf、installation / migration / journal は保持した。CI は固定 source SHA の読み取り専用 validator に統一し、現在形に見える旧案内文書を更新した。

作業単位の判断と手動確認は [inventory](artifacts/20260927t131352z--cleanup-inventory.md) と [確認シート](artifacts/20260927t154758z--implementation-checksheet.md) に記録した。

## Verification

- `uv run pytest -q --maxfail=1`: 1212 passed / 1 skipped。
- `make lint`: ruff check、ruff format、mypy 成功。
- focused entrypoint / CI / parity: 19 passed。
- 固定 bundle を構築して現行 help と旧 app/bootstrap/installer の不在を確認。
- Issue #411 以外の user data / active / control 3677 entries に差分なし。
- commit 後に clean checkout CI、refs、Final Quality Gate Strict v2 を追記する。

## Residual Risks / Follow-ups

旧名の application / infra module には現行経路や現行 unit test が使う共有実装が残る。名前だけで削除せず、inventory §15 に保持理由を記した。
