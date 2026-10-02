# Scope公開で既知の未対応原語を副作用前に拒否する

2026-10-02、baseline `6032621c2bd68ab9051b8929dd17d536a4114ad7`。Windows JSON readerの接続後、保存が未接続であることの検出順を公開CLIから確認した。採用済みGitHub発行・無上書き公開・実際の部分効果の契約に沿う修正であり、新commandや編集lockを追加するものではない。

## 再現と修正

未対応platformの外部OS境界を供給すると、`scope create initiative` はfake ghへPOSTを一回送信してから、無上書きrenameの未対応を検出した。公開結果はpartial/exit6、github-create succeeded、scaffold unknownだった。実Gitと使い捨てfixtureだけを使い、本repositoryやlive GitHubを変更していない。

同じ公開境界の試験は期待exit5に対してexit6で **1 failed（0.74秒）**。OS/共有libraryの必要原語をprobe書込みなしで照合する関数を設け、実際のrenameも同じ原語選択を用いる。Scope作成/取り込みで、remote Issue読取・作成とdry-run成功判定の前に確認する。同じ試験を **1 passed（0.29秒）** にした。既知の未対応ではLOCAL_IO_FAILED/exit5、effects=[]、gh呼出し0、fixture全bytes不変となる。

最初のInitiative八caseは8 passed / 47 deselected（1.80秒）。後続のEpic試験では、親GitHub状態のGETが能力確認より先に走る8 failed / 63 deselected（3.83秒）を観測した。確認を親GETの前へ移し、同じ八caseは8 passed / 63 deselected（1.45秒）。最終の三階層・作成/取り込み・apply/dry-run・未対応platform/欠落native symbolの24 caseは、下表の関連全件に含めて成功した。OS/共有libraryを置き換えた境界試験であり、実Windowsの成功ではない。

| 確認 | 実際の結果 |
|---|---|
| macOS・実Python 3.12.11 / 関連9 suite | 287 passed / 2 skipped、68.15秒、exit0 |
| macOS・実Python 3.10.15 / 同9 suite | 287 passed / 2 skipped、68.17秒、exit0。prefixとprovider import元をguardで照合 |
| 通常make lint | Ruff300 file、mypy219 source file、exit0 |

2 skipは実Windows JSON/hardlinkと実Windows親path置換。開始前の能力確認は、特定FSの同期成立、後からの権限/identity変更、実API呼出しの成功を保証するものではない。実際の途中失敗は従来どおり部分効果を記録し、自動rollbackしない。全writerの保存対応やWindows保存の完成を示さない。

元logsはEpicのignored Workbench `pytest-scope-publication-capability-{red,green,expanded,related,python310}.log`、`lint-scope-publication-capability.log`。最終logsは同じprefixのparent-red/parent-green/related-final/python310-finalとlint-scope-publication-capability-final.log。独立診断の最初のrunner import失敗と、正常なfixture再現logも保持している。import失敗を製品のRedには数えない。

source SHA256: `json_store.py` = `ba9850a8d31176d8c5b894d77aed6d93f696fb7f8175ccfb96f19fd3f0e2ae5b`、`direct_scope_publish.py` = `cf193d6b5dc151a1622507e972fc0d224ca0bb59c18c56f55419d1075cd883f7`。

このsourceを含む[clean75ac5760の全件](macos-full-75ac5760.md)は1900 passed/4 skipped（388.57秒）、exit0。[同候補の手動14操作](manual-console-75ac5760.md)も確認した。Windows保存/各公開/processとnative受入、fresh Strict/FQは未完了。[直前の全件](macos-full-6032621c.md)と[保存adapterの接続条件](windows-adapter-connection-review.md)を保持する。
