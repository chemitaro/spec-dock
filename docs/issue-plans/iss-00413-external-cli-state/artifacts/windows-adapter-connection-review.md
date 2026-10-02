# Windows保存adapterの接続に残る技術条件

2026-10-02、clean候補1e5d2586のsourceを読取り照合した。これは接続箇所と証拠不足の記録であり、採用済みD-03/D-05やRQ/ACを変更する文書ではない。Windowsを対応済みと宣言しない。

| 境界 | sourceの現状 | 残る検証 |
|---|---|---|
| 物理directoryと開始mutex | `infra/identity.py`、`windows_handles.py`、`start_lock.py`にWindows API経路が存在 | Windows/NTFSの別process、WAIT_ABANDONED、handle解放の実結果。既存CI laneは実行待ち |
| workspaceとScopeのJSON読取 | `infra/json_store.py`のguarded parentはPOSIX descriptorを要求し、他OSでは明示停止 | Windows directory/file handleからの非redirect読取、regular・single-link・identity/bytesの観測。POSIX int fdをHANDLEと同じ原語として扱わない |
| 直接対象の保存と捕捉解除 | `infra/work_target_store.py`のWindows `_open`は未接続として停止 | D-03の排他的stage、無上書き公開、同期、正確な捕捉basenameだけの解除。古い解除が新recordを消さないこと |
| metadata/Artifact/Scopeの公開 | `direct_json.py`、`file_publication.py`、`directory_publication.py`はguarded POSIX原語を使用 | 既存の未知field/既存mode/前後identityと途中失敗の契約を維持したWindows接続。path fallbackを成功扱いしない |
| project所有のinit process | `infra/project_hook.py`はPOSIX process group以外を未接続として診断 | Windowsの実process/子process・timeoutの境界。無関係なprocessへのkillやStart共通lockの追加はしない |

## 一次資料が確認できることと、実証が必要なこと

Microsoftの[FILE_RENAME_INFO](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_rename_info)は、相対targetのRootDirectory handleと、既存targetを置換せずerrorにする指定を説明する。[SetFileInformationByHandle](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-setfileinformationbyhandle)は、操作に応じたaccessと情報classを要求する。これらはD-03のnative無上書き公開の検討根拠であり、現sourceへ接続済みという証拠ではない。

[FlushFileBuffers](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-flushfilebuffers)はfile handleにGENERIC_WRITEを要求し、volume全体のflushには管理者権限が必要とする。[File Caching](https://learn.microsoft.com/en-us/windows/win32/fileio/file-caching)は、metadataの永続化にflushまたはWRITE_THROUGHが必要と説明する。D-03のdirectory同期をどのnative操作で満たせるかは、この文書読取だけでは実証できない。volume全体flush・権限自動変更へ広げない。

## 接続前に確定させる順序

1. P-03の選択storeに必要なWindows handle/APIと、既存JSON readerとの接続をImplementation Brief Strictで具体化する。正本の同期・非redirect・無上書き条件と矛盾する提案は実装指示として採用しない。
2. 実Windows/NTFSで原語の成功・失敗・handle寿命を確認する。原語を提供できない環境でStartを安全に拒否する条件を維持し、fake APIの成功をnative成功へ変換しない。
3. 一つの公開境界ごとのRed→Greenで接続し、通常保存・遅い解除・途中停止・並行Startを検証する。Mutexの成功だけで保存の成立を認定しない。

共通registry、独自.git entry、Scope UUID、ACL変更、Local mutex fallback、通常編集を覆う共通lockは追加しない。現時点ではBriefの外部送信、保存接続、native受入とも未実施である。
