# Issue #411 実装確認シート

## 目的と判定

旧 CLI の実行経路、専用 test、現在形に見える古い案内を削減する。現行 44 leaf、拒否診断、固定配布、journal / recovery、migration、CI の読み取り専用検証は維持する。各項目は現物・コマンド結果・差分で判定し、削除確認のための過剰な test 基盤を追加しない。

基点: `2ce20425e83f6f8a36853364d00042f97faa3f24`。作業先: 単一 worktree の独立 clone `iss-00411-retired-cli-surface-cleanup`。

## Step 0: 境界

- [x] branch、HEAD、clean state、祖先 `d7c816d11bee1a73cb87273b15e486c3b669206c`、単一 worktree を確認。
- [x] Issue #411 は GitHub で OPEN。ユーザー data / active / control / refs の baseline は Issue 内 `.workbench/issue411-scope-baseline.json` に保存（3677 entries）。
- [x] current baseline focused tests: 83 passed。

## Step 1: 削除前の守るべき契約

- [x] 44 leaf、help、JSON、tombstone、migration、fixed entrypoint の既存 test と実行入口を確認。83 passed。
- [x] 旧 test の current invariant は installation / work / scope / artifact / migration の既存 `*_vnext` と integration suite に照合。旧 harness と同じ wire の再テストは移植しない。
- [x] 新しい test は不足した重要契約だけに限定する。Step 1 では追加なし。

## Step 2: asset 定数の分離

- [x] current caller は external CLI、installation executor / command と current installation tests。legacy callable だけ old installer behavior を使用。
- [x] `asset_layout.py` に配布パス定数を移設し、current entrypoint / installation 109 tests passed。
- [x] neutral module には定数のみ。old installer behavior は移さない。

## Step 3: 旧 test / launcher 撤去

- [x] old harness、fixture、28 leaf manifest、old-only test を削除し、current-named test の旧 setup を解消。
- [x] 旧 test family の retain / remove 理由と current coverage を inventory の §8 および実施記録に記録。
- [x] provider CI の focused caller を現行 test に変更。
- [x] test collection 1562 件（途中段階）、最終 full suite 1212 passed / 1 skipped で現行 installation / migration / safety checks を確認。

## Step 4: 旧 runtime 撤去

- [x] retired app/parser/registry/dispatch/bootstrap と old command modules の current 到達性を確認して削除。
- [x] conditional application/shared module は caller がある場合保持し、理由を inventory に記録。
- [x] fixed bundle 内の旧 app / bootstrap / installer 不在、現行 help、provider と dogfood scripts の byte parity を確認。

## Step 5: CI

- [x] `.github/workflows/ci.yml` は full SHA の固定 validator のみを実行し、sync を行わない。
- [x] current CI integration は full suite で成功。`eb77cd9f` の独立 clean clone に固定 validator を実行し `valid=true`、240 nodes、digest `54f19658…`。clone の Git 状態は clean、`.git/spec-dock` は未作成。
- [x] provider CI に削除済み test path がない。

### Step 5 補完: CI境界（2026-09-29）

- [x] P1 `FQG-411-CI-BOUNDARY-COVERAGE` を別Strict analystで分析し、既存要件のtest-remediationと確認。
- [x] 正常・full SHA mismatch・tracked/untracked dirty・short/non-hex SHA・invalid digestの7 casesを既存CI integration内で確認。
- [x] 全ケースでtarget全体のpath/type/bytes/mode/link/directory（Git/control/active/generated含む、除外なし）不変を確認。
- [x] workflowの固定validator1回・GitHub SHA・旧shim/sync不在と、script側完全HEAD比較を確認。
- [x] 4種の一時的な異常をすべてassertionで検出。production script/workflowは変更なし。CI/entrypoint/parity 24 passed、lint成功（開発中の結果）。
- [ ] 最新commitで独立test laneと同じreviewerのP1 closureを確認。

## Step 6: 文書

- [x] provider scripts README、root current docs、AGENTS を現行 CLI に更新。
- [x] dogfood projection は provider から同期し byte parity を確認。
- [x] historical / migration 資料を保持し、検討用文書に現行参照先を付記。

## Step 7: 残存参照

- [x] pyproject の削除済み test 用 mypy 例外を撤去し、workflow / docs / tests の削除先参照を検索。
- [x] inventory の conditional item を retain 理由または削除証拠で閉じる。

## Step 8: 検証

- [x] focused current checks: 83 + 109、Artifact 28、unit 724 passed / 1 skipped。
- [x] `make lint`: ruff check / format、mypy 成功。
- [x] `uv run pytest -q --maxfail=1`: 1212 passed / 1 skipped。
- [x] fixed bundle の旧ファイル不在と help、独立 clean clone での CI 検証を確認。
- [x] `git diff --check` 成功、範囲 snapshot の user data / active / control 3677 entries に差分なし。refs / worktree は commit 後に再確認。

## Step 9: 最終品質ゲート

- [ ] in-scope 変更を小さな単位で commit / push し、local・upstream・GitHub SHA を一致させる。
- [ ] ChatGPT Final Quality Gate Strict v2 の review と独立 test lane を完了。
- [ ] P0/P1 と coverage blocker があれば分析、修正、同一 reviewer で再レビュー。
- [ ] 最終差分、削除数、保持した安全境界、残余事項を報告。
