# Windows JSON readerの接続と残る受入

2026-10-02、baseline `9a97f758c9948aa638ab40c3ed34f8565c09d81c` から、`infra/json_store.py` のWindows読取経路を接続した。保存・公開adapterを完成扱いにはしない。採用済みD-03/D-05の非redirect、既存bytesとidentityの保全条件に沿った、読取だけの実装単位である。

## 実装した境界

`read_guarded_json_bytes` はWindowsでは保持した `WindowsDirectory` の親handleから、一つのbasenameをNtOpenFileで開く。中間pathやleafを絶対pathで開き直さず、reparseをたどらない。directory、reparse、複数hardlink、pipe、deviceを読取前に拒否し、同期ReadFileでEOFまで元のbytesを取得する。既存の戻り型 `(payload, exact_bytes, identity)` を維持し、Windowsのidentityはvolume番号と全FileId128を損失なく整数へ符号化する。Scope IDやUUIDを新設するものではない。

本当に存在しないparent/leafだけをNoneにする。権限不足、壊れJSON/UTF-8、query/read/openの失敗をemptyへ読み替えない。fileと親のhandleは成功・失敗とも解放する。通常編集を許すshare read/write/deleteを維持し、ACLや編集権限の変更、共通lockの追加はない。POSIX descriptor基準の `_at` APIと、未接続のWindows選択store・公開・process境界は変えていない。

## TDDと確認結果

最初のpublic reader試験は、Windows経路が未接続のdirectory adapterで停止する **1 failed（0.03秒）** を確認した。親pathが途中で差し替わるexternal API代替を使い、修正後は同じ試験を **1 passed（0.03秒）** にした。SpecDockの内部結果を代替せず、OSのhandle/APIだけを代替する。これをnative Windows成功とは呼ばない。

追加境界は日本語・emojiのpath、64KiBを超えるpayload、元bytes・128bit identity、regular/single-linkの拒否、parent/leafの不存在と権限不足の区別、破損JSON/UTF-8、未完了open・ReadFile/query失敗・異常byte count、全handle解放を検査した。公開CLIの未対応OS試験は、Windowsを既に未接続と仮定せず、未知OSを供給するfixtureへ更新した。exit5、effectsなし、tree bytes不変、独自stateなしという停止契約は保持した。

| 実行 | 実際の結果 |
|---|---|
| macOS・実Python 3.12.11 / 関連8 suite | 58 passed / 3 skipped、2.12秒、exit0 |
| macOS・実Python 3.10.15 / 同8 suite | 58 passed / 3 skipped、2.30秒、exit0。venv prefixとprovider import元をguardで照合 |
| 通常 `make lint` | Ruff300 file、mypy219 source file、exit0 |
| Windows CI設定の静的確認 | Windows platform、PR head固定、五つの実在suite、通常全pytestの維持をRuby/Psychで確認、exit0 |

3 skipは、新規の実Windows JSON/hardlink、実Windows親path置換、既存native WAIT_ABANDONEDである。CIへ追加しただけで実Windows/NTFS受入を満たしたとはしない。全件macOS/Linux・手動consoleの既存結果は各SHAで保持し、この変更を含む候補の全面合格へ転記しない。

元logsはEpicのignored Workbench `iss-00413-implementation/pytest-windows-json-{anchor-red,anchor-green,boundary,related-complete,python310-complete,public-contract}.log`、`lint-windows-json-reader{,-green,-final}.log`。最初のlintのformat一件と、API代替が不足した型検査四件も保持し、通常formatと代替の契約更新で修正した。

source SHA256: `json_store.py` = `6b6b80ed3272f650bf4cc4069bbb626335b4b152993d06b2910315fd69273053`、`windows_handles.py` = `75c9e3f6b50bde4a1fa3c544835a0a4862c8676e9651c5e612703ebe2d841bae`。

## 一次資料と次の条件

Microsoftの[NtOpenFile](https://learn.microsoft.com/en-us/windows/win32/api/winternl/nf-winternl-ntopenfile)と[NtCreateFileのoptions](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntifs/nf-ntifs-ntcreatefile)で、読取access・同期・非directory・reparse非追跡を確認した。[FILE_STANDARD_INFO](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_standard_info)でlinks/directoryを、[GetFileType](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfiletype)でdisk/pipe/deviceの区別を確認した。[ReadFile](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-readfile)と[同期EOF](https://learn.microsoft.com/en-us/windows/win32/fileio/testing-for-the-end-of-a-file)を参照した。API文書の存在は実NTFS受入ではない。

P-03の選択公開・同期・捕捉解除、各metadata/Artifact/Scope公開、init process、実Windowsの別process/NTFS試験、現在候補のStrict/FQは引き続き必要である。[接続条件](windows-adapter-connection-review.md)を保持し、D-03のdirectory同期を弱めたり、HANDLEをPOSIX fdとして渡したりしない。
