# StartのOS排他を実processで確かめる境界

この記録はP-05/P-13の準備である。Windowsの保存・公開処理、全CLI、実consumer移行の受入とは分ける。製品実装の変更はなく、既存adapterに対する実OS試験を追加したため、新機能のRed→Greenとは呼ばない。

## 通常pytestへ追加した試験

tests/integration/test_issue413_native_lock.pyは実Gitでmain/linked worktreeと別cloneを作り、実Pythonの別processからStartLockを取得する。OS APIやSpecDockオブジェクトを代替しない。

1. mainが保持中、同cloneのlinked側はtimeout0でbusy/exit3。通常解放後は同じ物理identityで取得できる。
2. 同じrepositoryから作った別cloneは独立し、他cloneの保持中でも取得できる。
3. 保持processを強制終了しても次processが取得でき、PID回収や新lock fileは不要。
4. Windows固有の一caseは、実Global mutexの未所有handleを残したうえで所有processを終了する。WindowsMutexのWAIT_ABANDONED取得・解放後に通常取得へ戻ることを確認する。

全caseでGit common-dirのentry名・種別・mode・file bytesを前後比較する。fixture用のready通知はGit外に置き、完成bytesを公開してから親processへ通知する。childはactual provider import元、Python、OSと物理identityを出力する。WindowsではGetVolumeInformationWが返す実FS名を検査し、NTFS以外を成功やskipへ変換しない。

## ローカルで実行済み

- macOS/Python 3.12.11: native suiteとidentity/Windows API契約suiteは8 passed/1 skipped（0.82秒）、exit0。
- 実Python 3.10.15: native suiteは3 passed/1 skipped（0.89秒）、exit0。prefix/providerを開始時に照合した。
- 一skipはWin32 WAIT_ABANDONEDの実OS専用caseであり、Windows合格ではない。最初の同Mac native suite 3 passed/1 skipped（0.87秒）はready通知の公開補正前として別logへ残す。
- 通常make lintは全Ruff（298 files）・mypy（217 source files）成功、exit0。型ignoreや既存収集除外を追加しない。

## CIの接続と未実行

Ubuntu/macOS配布laneと同じ五suiteのMacローカル試験は86 passed（122.39秒）、exit0。製品sourceはbaseline 15bdcd054028c1cc8fc9dcbab7344e4db36239caと同一でstatusは空。コピー入力SHA256はb07821e35492f31ba68516552f050a398d345dc8fc546e075c36c63d097576b4、実配布wheel SHA256はf8884f8d1e624fd8aa85c50f7eac763e646669df73431dab36eef7bd242c2761。元log pytest-current-distribution-parity-macos.logに実consoleのprefix/import元も保持した。新CI jobが実行されたという証拠ではない。

既存Ubuntu/macOS配布laneに実console lifecycleを追加し、-sでsource/wheel provenanceを保存する。追加Windows laneはPR headを明示checkoutし、full SHAを照合してからnative suite、directory identity、Windows API契約suiteを実行する。通常provider全pytest/lintのlaneは維持する。Windows専用caseはWindows laneではskip条件に入らない。

YAMLを既存Ruby/Psychで解析し、候補checkout、通常pytest維持、nativeの三suiteとparityのE2E指定を検査した（exit0）。actionlintはローカル未導入で、GitHub ActionsやWindows jobの実行成功とは扱わない。Windows/NTFSの実結果はまだなく、Windows store/JSON/file/directory公開とprocess hookも未接続である。

Microsoftの[Kernel object namespaces](https://learn.microsoft.com/en-us/windows/win32/termserv/kernel-object-namespaces)、[WaitForSingleObject](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-waitforsingleobject)、[GetVolumeInformationW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getvolumeinformationw)へAPI条件を照合した。WAIT_ABANDONEDは所有取得の結果であり、保護対象の内容が正常という証拠にはしない。API説明の読取と実OSでの検証結果を混同しない。

元logsは既存Epic Workbenchのiss-00413-implementation/pytest-native-lock-boundary-{macos,macos-2,python310}.log、lint-native-lock-boundary.log、provider-native-workflow-static.log。Linuxの現在候補とWindowsのnative実行は後続結果を別記録する。fresh Strict/Final Quality Gate、P-13の全受入認定、最終手動確認、実consumer適用は未完了。

## 2026-10-02以降の位置づけ

本文は記録当時の実装・試験・未実施事項を保全した履歴です。[最新OS決定](os-support-decision.md)によりWindows完成・native/NTFS受入の義務は失効しました。専用実装・test・CIは[P-18](../plan.md#p-18)で撤去します。POSIXの保全境界と既存実測は維持し、[最新baseline](implementation-acceptance-evidence.md)と区別します。
