---
種別: レポート（Issue）
ID: "iss-00411"
タイトル: "Remove retired SpecDock CLI surfaces after scope active work cutover"
関連GitHub: ["#411"]
最終更新: "2026-09-29"
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
- `eb77cd9f` の独立 clean clone で `.github/scripts/specdock-ci-validate.sh` 成功（`valid=true`、240 nodes、distribution digest `54f196586ea2ac69fd79735e6e63f0e95b3363217e78eeb024bdb666973cbbe0`）。clone は clean で導入制御領域を新規作成しなかった。既存導入済み作業場では新旧 engine pin が異なるため同 validator は停止することを確認し、CI と同じ新規 checkout 条件で判定した。
- `3c21176f170e4c1934b17927d1087c4b2ab0ecf3` の独立必須lane: `make lint` 成功、`uv run pytest -q` 1217 passed / 1 skipped、focused 24 passed。local / upstream / live GitHub SHA一致、clean。

## Final Quality Gate と補完

`1061d159df7266850c22ad700a139de88f85ab68` の正式Strict v2は10観点complete、P1 1件（`FQG-411-CI-BOUNDARY-COVERAGE`）でfail。製品guardはあるが、CIの必須負例と対象全体の無変更検証が不足していた。独立したStrict analystがtest-remediationと確認した。

既存CI integrationだけを補完し、7 casesと全target snapshot、workflow wiringを確認した。CI/entrypoint/parity 24 passed、lint成功。4種の一時的異常を全て検出し、製品script/workflowを変更せず検証記録を正確化した。これらの開発中確認に続き、コミット・プッシュ済みの `3c21176f170e4c1934b17927d1087c4b2ab0ecf3` を同じreviewerが再審査し、P1をclosedと判定した。

証拠と会話継続はIssue内 `.workbench/chatgpt-final-quality-gate-strict-v2/issue411-cleanup-restart-20260929/` に保存する。

## Residual Risks / Follow-ups

旧名の application / infra module には現行経路や現行 unit test が使う共有実装が残る。名前だけで削除せず、inventory §15 に保持理由を記した。

## 認証済みの実装と提出記録

- Final Quality Gate Strict v2: wrapper exit0、status=pass、coverage_complete=true、10観点complete、P0/P1=0、P2/P3=0。
- 認証SHA: `3c21176f170e4c1934b17927d1087c4b2ab0ecf3`。review session `fqg-v2-f5f30c6e-1bed9dec`、同じconversation `6abaed2b-a1e0-83e9-8d1f-94db74fa01dd`。GPT-5.6 Sol、Pro。
- 初回P1 `FQG-411-CI-BOUNDARY-COVERAGE` は同reviewerがclosedと判定。追加のblocker、未審査領域、未解決項目なし。
- 同SHAの独立clean clone: `valid=true`、240 nodes、digest `54f196586ea2ac69fd79735e6e63f0e95b3363217e78eeb024bdb666973cbbe0`。Git含む4656 entriesのpath/type/bytes/mode/link/directory差分0、clean、installation control未作成。
- 既存作業場の保護対象3677 entries、他のlocal branch ref、単一worktree登録はbaselineから変更なし。他導入先へのupdate、migration、Issue close、mergeは実施していない。
- 実装基点 `2ce20425e83f6f8a36853364d00042f97faa3f24` から上記認証SHAまで132 files、537行追加、63823行削除。恒久的な撤去確認harnessは追加せず、必要なCI境界testのみ補完した。

この完了記録だけを更新した提出commitも同campaignで再認証する。最終提出SHAとそのreview/test結果は同Workbenchの `review-result.json` と `test-results-final/manifest.json` から確認できる。上記SHAの認証履歴と最終提出の認証を区別し、記録更新のたびに実装を変更したとは扱わない。
