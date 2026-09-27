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

- [ ] old harness、fixture、28 leaf manifest、old-only test を削除し、current-named test の旧 setup を解消。
- [ ] assertion ごとの retain / remove 理由と current coverage を inventory に記録。
- [ ] provider CI の focused caller を現行 test に変更。
- [ ] test collection と現行 installation / migration / safety checks を確認。

## Step 4: 旧 runtime 撤去

- [ ] retired app/parser/registry/dispatch/bootstrap と old command modules の current 到達性を確認して削除。
- [ ] conditional application/shared module は caller がある場合保持し、理由を記録。
- [ ] fixed bundle 内の不在、現行 help / 拒否、provider と dogfood scripts の byte parity を確認。

## Step 5: CI

- [ ] `.github/workflows/ci.yml` は full SHA の固定 validator のみを実行し、sync を行わない。
- [ ] current CI integration と clean checkout の read-only / SHA / digest 境界を確認。
- [ ] provider CI に削除済み test path がない。

## Step 6: 文書

- [ ] provider scripts README、root current docs、AGENTS を現行 CLI に更新。
- [ ] dogfood projection は provider から同期し byte parity を確認。
- [ ] historical / migration 資料を保持し、現行案内との区別を確認。

## Step 7: 残存参照

- [ ] pyproject / workflow / docs / tests の削除先 import と stale current invocation を検索。
- [ ] inventory の conditional item を retain 理由または削除証拠で閉じる。

## Step 8: 検証

- [ ] focused current checks。
- [ ] `make lint`。
- [ ] `uv run pytest`。
- [ ] fixed bundle / clean checkout CI。
- [ ] `git diff --check` と範囲 snapshot 比較（user data、active、control、refs、他 worktree 無変更）。

## Step 9: 最終品質ゲート

- [ ] in-scope 変更を小さな単位で commit / push し、local・upstream・GitHub SHA を一致させる。
- [ ] ChatGPT Final Quality Gate Strict v2 の review と独立 test lane を完了。
- [ ] P0/P1 と coverage blocker があれば分析、修正、同一 reviewer で再レビュー。
- [ ] 最終差分、削除数、保持した安全境界、残余事項を報告。
