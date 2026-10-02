# OSごとの実装・検証状態と未接続境界

## 実行済みの範囲

| 対象 | 製品source / 実証拠 | 未完了との区別 |
|---|---|---|
| macOS 27.0.1 arm64 / APFS / Python 3.12.11 | clean e11f1879の通常全件1843 passed/1 skipped、446.22秒、exit0 | 既存Linux O_TMPFILE専用skipはnative成功にしない。後続変更の全件ではない |
| Linux local tmpfs / Python 3.11.16 | clean e11f1879の通常全件1827 passed/17 skipped、1016.04秒、exit0 | ARM host上のamd64変換を使う隔離container。物理Linux機/Windows/ネットワークFSの保証へ転記しない |
| 配布wheelの実console | macOS実3.12/3.10とclean 6824b3f8のLinux実3.11でStart→重複拒否→兄弟並行→Sync→Finish→次Issue Startが成立。Linux一caseは25.04秒、exit0 | 先行fullと追加caseの件数を合算しない。GitHubは外部gh scriptによる代替境界 |
| Windows | windows_handles.pyのdirectory identity/mutexとWin32 API契約試験が存在。[実OS境界試験とWindows CI lane](native-start-lock-boundary.md)を追加 | Windows/NTFSでの実結果は未取得。work_target_storeのWindows保存、JSON/file/directory公開、project_hookのWindows process経路は未接続 |

Linuxは同一の固定image `sha256:c514701300438939d8f2f3fd75cc57ea2eff502c1920e5cc98c713cf17452e3d` を使う。read-only root、network none、cap-drop ALL、USER未設定、UV_OFFLINE=1、clean候補SHA・prefix・providerを開始時に照合した。17 skipはZsh 12、macOS専用probe 1、Linux匿名stageでは非該当のpathname cleanup 4である。

## 未接続のOSをCLI内で安全に診断する

保持するjson_storeのguarded readerはPOSIX directory descriptorを使う。未接続OSでos.O_DIRECTORYへ進んでAttributeErrorをCLI外へ漏らす経路を、公開scope showと外部OS境界の代替で再現した。最終fixtureのRedは1 failed/11 deselected（0.18秒）、exit1。通常のopen/O_RDONLYは備え、POSIX専用O_DIRECTORYだけがないOS境界で失敗した。

OS名を先に確認し、非POSIXではNotImplementedErrorを返す二行を追加した。同じ公開caseのGreenは1 passed/11 deselected（0.11秒）、exit0。CLIはLOCAL_IO_FAILED/exit5/effects=[]、stderrなしとなり、全fixture bytes/mode、.agent未作成、独自Git control未作成を検査する。実3.10の同caseは1 passed/11 deselected（0.13秒）、exit0。最初の二runはfixture境界/既存error codeの精度を修正する前のlogとして残す。

これはWindowsのreader/writerを完成させる変更ではない。未接続の境界を、ACL変更・POSIX擬装・別namespace・path-based writerへfallbackせず、GitHub writeや記録作成の前に診断する。POSIXのdirectory操作は従来どおりである。

関連Contract/query guard/store/directory identity/Windows API/direct JSON/fresh console/fresh wheel八群は61 passed（28.82秒）、exit0。provenanceのstdout保存を追加したconsole caseは1 passed（9.03秒）、exit0で、両結果を合算しない。通常make lintは全Ruff check/format（297 files）・mypy（216 source files）に成功、exit0。skip/型ignore/収集除外を追加しない。

## sourceとwheelの証拠を取り違えない

console harnessはbaseline HEADに加えて、製品sourceのtracked status、コピーした入力fileの相対名と内容hashをfoldしたSHA256、wheel hash、実Pythonとsite-packages import元を記録する。作業中のdeltaをclean HEADと同一と説明しない。pytest -sならprovenanceが元logへ残り、containerの一時FSが終了時に消えても検証したwheelを識別できる。

## Windowsの受入に残るもの

clean 31b1ffe12c36739c56375eea0a764ac2a5719d0aのLinux/Python 3.11.16で、配布consoleと未接続OS診断の二caseは2 passed（25.04秒）、exit0。copy入力SHA256はaedb8204b19e3694c0a14842b5149921d039f8731beda5eed5b8a7af189da0e4、非editable wheel SHA256はde1aa39b781e4a8e679a0dea8319dc7da21872c1329bf3b908374fd6bf6db534。製品source statusは空で、baseline HEADと候補は同一。元log pytest-linux-python311-console-platform-31b1ffe1.logに実prefix/import元・capability0・tmpfs・offlineとprovenanceを保持した。全件やWindows nativeの成功へ合算しない。

現実装の正本はinfra/identity.py、windows_handles.py、start_lock.py、work_target_store.py、json_store.py、direct_json.py、file_publication.py、directory_publication.py、project_hook.pyである。最小identity/mutex API、CLIでの未接続診断、保存/公開の接続、NTFS別process検証を別々に扱う。

設計D-03/D-05とP-03〜P-07/P-13のWindows保存/公開/強制終了・排他の受入は未完了。Global mutex取得不能時のLocal fallback、PID/mkdir lock、permission/ACL自動変更、独自.git stateは追加しない。未試験のOS/FSを対応済みと公表しないというrequirementの条件を維持する。

実装調査でMicrosoftの[CreateFileW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew)、[SetFileInformationByHandle](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-setfileinformationbyhandle)、[FILE_RENAME_INFO](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_rename_info)、[FlushFileBuffers](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-flushfilebuffers)を読取した。sharing/access、relative renameとflushのAPI条件はWindows writerの実装判断に必要だが、文書の存在をdirectory同期・NTFS writerの実測成功とは扱わない。

元logsは既存Epic Workbenchのiss-00413-implementationに保存する。主要fileはpytest-linux-python311-e11f1879.log、pytest-linux-python311-fresh-console-6824b3f8.log、pytest-unconnected-directory-platform-{red,red-2,red-3,green,related,python310}.log、lint-unconnected-directory-platform.log、lint-unconnected-directory-platform-2.log、pytest-fresh-console-provenance.log。real consumer/live GitHubは未変更であり、fresh Strict/Final Quality Gate/手動確認/P-16以降の実適用は完了していない。
