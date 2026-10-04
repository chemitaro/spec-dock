# Windows物理識別補強後のmacOS全件とrunner修正

2026-10-02、clean `3b0c69e8d61ad7ad5b01307dd301963a2cab180d` を固定した。製品sourceには[WindowsDirectoryの補強](windows-directory-anchor.md)が含まれる。macOS 27.0.1 arm64、実Python 3.12.11、現在checkoutの`.venv`とprovider import元を照合してから、通常全pytestと同じ `-q --tb=short -ra` の全件選択を実行した。

## 結果と区別

| 実行 | 実際の結果 | 判断 |
|---|---|---|
| 最初の診断runner | 2 failed / 1851 passed / 2 skipped、452.60秒、exit1 | runnerのmain guard不足でmultiprocessingの子が起動前に停止。全件合格ではない |
| 修正runnerで該当二caseだけ | 2 passed / 7 deselected、0.16秒、exit0 | 製品source・既存testの変更なしで原因箇所を確認 |
| 同じclean SHA・修正runnerの全件 | **1853 passed / 2 skipped、402.78秒、exit0** | 通常選択の全件が成功。Windows nativeや最終認定とは別 |

最初の失敗は `test_killed_metadata_replace_preserves_the_visible_boundary_without_journal[before|after]` のready通知待ちだった。stderrには `multiprocessing.spawn` → `runpy.run_path` → ignored診断runnerの「trace fileがまだ存在しない」assertionという経路が残った。子processがmain fileを再読込みするため、parentで作成済みtraceに対してassertionが再実行され、製品のchild処理に入れなかった。

Codexが用意したrunnerの実行処理を `main()` に収め、`if __name__ == '__main__'` からだけ呼ぶようにした。childの再importでGit preflightやpytest起動を繰り返さない。失敗をskipへ変更せず、製品source・tests・timeout・assertionを変更しない。最初のrunner作成内容、stdout/stderr、Trace2を保持し、修正後の二caseと全件のlogを別fileへ保存した。

実行は `uv run python <owned runner> <新しいTrace2 path>`。runnerから `pytest.main(['-q', '--tb=short', '-ra'])` を呼び、全件の収集除外やpolicy skipを加えていない。Git Trace2はcheckout外のowned logへの診断だけで、製品の全GIT_*除去は維持した。productionのsanitized Git呼出しはこのtraceに残らないため、全Git操作の観測証拠には使わない。

二skipはnative Win32 WAIT_ABANDONEDとLinux O_TMPFILE capabilityである。Windows/NTFSの保存・native受入、現在候補のCode Review Strict/Final Quality Gateは未完了。旧候補8a70a8b3のreadonly比較不一致の原因も未確定であり、今回のrunner不備と混同せず[旧調査](validation-readonly-investigation.md)を保持する。Linux全件・手動consoleは別の8a70a8b3 sourceである。

元fileはEpicのignored Workbench `iss-00413-implementation/` にある。

- `pytest-macos-full-3b0c69e8.log`、`git-trace2-macos-full-3b0c69e8.jsonl`: 最初の失敗。
- `run-macos-full-3b0c69e8-unguarded-original.py`: 最初のrunner作成内容を保存。再実行しない。
- `run-macos-full-3b0c69e8.py`: main guard付きの修正runner。
- `pytest-macos-multiprocessing-runner-fixed-3b0c69e8.log`: 該当二caseの確認。
- `pytest-macos-full-3b0c69e8-runner-fixed.log`、`git-trace2-macos-full-3b0c69e8-runner-fixed.jsonl`: 最終全件成功。
