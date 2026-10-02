# Windowsの物理directoryを親handleから開く

2026-10-02、baseline `ccf9637d453a4f0d7988a7f9f3471a147c427bbd` のWindows directory adapterだけを修正した。D-02/D-05の物理識別を補強する単位であり、D-03の保存adapter接続やWindows/NTFS受入の完了ではない。

## 問題と変更

従来のWindowsDirectoryは各階層をCreateFileWの絶対pathで開いていた。既に開いた親がrenameされ、同じpathに別directoryが置かれると、次の絶対pathのopenは新しい親側の子へ進み得る。API境界の代替でこの置換を表現し、公開されたWindowsDirectory.identityが別のFileIdを返すRedを確認した。実NTFSで同じraceを再現したという記録ではない。

filesystem anchorだけをCreateFileWで開き、以後はNtOpenFileのOBJECT_ATTRIBUTES.RootDirectoryへ保持した親handleを渡して、一つの子名ずつ開くようにした。各handleでdirectory属性とreparse属性を検査し、VolumeSerialNumber/FileId128を観測する。通常編集を禁止するACLや共通lockを追加せず、share read/write/deleteは従来どおり許す。

NtOpenFileはFILE_READ_ATTRIBUTESとSYNCHRONIZE、FILE_DIRECTORY_FILE・FILE_SYNCHRONOUS_IO_NONALERT・FILE_OPEN_REPARSE_POINTを指定する。object属性はOBJ_CASE_INSENSITIVEだけで、OBJ_INHERITを設定しない。UNICODE_STRINGを明示UTF-16 LEのbytesとpointerで渡し、日本語と補助平面文字を含む名前を確認した。同期openの未完了結果を成功扱いせず、成功系statusに付属する未採用handleも閉じる。nativeエラーはRtlNtStatusToDosErrorでWin32エラーへ対応させ、path再openやnamespace/ACL変更へfallbackしない。

## 一次資料との照合

Microsoftの[NtOpenFile](https://learn.microsoft.com/en-us/windows/win32/api/winternl/nf-winternl-ntopenfile)、[OBJECT_ATTRIBUTES](https://learn.microsoft.com/en-us/windows/win32/api/ntdef/ns-ntdef-_object_attributes)に、既存directoryのopen、親handleに対する相対名、非継承の属性を照合した。[NtCreateFile](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntifs/nf-ntifs-ntcreatefile)のopen option、[UNICODE_STRING](https://learn.microsoft.com/en-us/windows/win32/api/ntdef/ns-ntdef-_unicode_string)のbyte長、[IO_STATUS_BLOCK](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/ns-wdm-_io_status_block)のunion/ULONG_PTR、[RtlNtStatusToDosError](https://learn.microsoft.com/en-us/windows/win32/api/winternl/nf-winternl-rtlntstatustodoserror)のエラー対応も確認した。文書照合は実OS成功の代替ではない。

## 実行した確認

| 範囲 | 結果 |
|---|---|
| 親path置換の一case | Red 1 failed / 0.04秒 → Green 1 passed / 0.02秒。旧実体のFileIdを保持 |
| 未完了openのhandle解放の一case | Red 1 failed / 0.04秒 → Green 1 passed / 0.02秒 |
| 最終macOS/Python 3.12の五suite | 21 passed / 1 skipped、1.49秒、exit0 |
| 同五suite・実Python 3.10.15 | 21 passed / 1 skipped、1.38秒、exit0。prefix/providerを実行前に照合 |
| 通常make lint | 全Ruff check/format 299 files、mypy 218 source files、exit0。最初のRuff二件は修正前logへ保全 |

五suiteは `tests/unit/infra/test_windows_directory.py`、`test_windows_mutex.py`、`test_directory_identity.py`、`test_start_lock.py` と `tests/integration/test_issue413_native_lock.py`。Windows APIは外部境界でのみ代替し、POSIXの別process/Git fixtureは実物を使った。reparse/non-directory拒否、UTF-16の子名、全取得handleの解放も確認した。一skipはWin32 WAIT_ABANDONEDのnative専用caseで、Windows成功に数えない。

Windows CI laneへ新しい境界suiteを加えた。実Windowsで既存の物理identity・別process・強制終了のnative suiteが通るかは、CI実行待ちである。JSON reader、work-target保存、metadata/Artifact公開、project init processのWindows接続は未完了。[接続条件](windows-adapter-connection-review.md)を維持する。

workflowはRuby/Psychで解析し、Windows platform・PR head固定・四suiteの現存path・通常全pytestの維持を静的確認した（exit0）。GitHub Actionsの実行成功とは区別する。

修正後 `src/spec_dock/runtime/infra/windows_handles.py` のSHA256は `65f1f48d2975cdb7a8ccfa1da9dc3fd7a2507264381759debb96bc424412ce64`。過去の全macOS/Linux/手動console候補とは製品source差分があるため、それらの全件件数を今回の合格へ転記しない。元logsはEpicのignored Workbench `iss-00413-implementation/pytest-windows-directory-{anchor-red,anchor-green,pending-red,pending-green,related-final,python310}.log`、`lint-windows-directory-anchor{,-green}.log` に保存した。現在候補のStrict/FQ、Windows保存/native受入、実consumer適用は未完了。
