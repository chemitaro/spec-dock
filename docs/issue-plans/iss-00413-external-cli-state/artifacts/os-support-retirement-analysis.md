# Issue #413 Windows対応撤回の第三者分析

## 1. 検証境界

GitHub connectorで次を直接確認しました。

- repository: `chemitaro/spec-dock`
- target branch: `codex/iss-00413-external-cli-state`
- branch tip/full SHA: `121228c6fca1fd016e7bccef009902396112ba43`
- SHA比較: expectedと完全一致
- commit: 資料更新。親source candidateは `2b2be5e227ddf4d067da083bba15a8ec23d21367`
- main比較基準: `6fec3099d8759b4e5b3b393b2987534b46dfa383`（利用者提供。今回main branch自体へfallbackしていない）

この分析はtarget branchとその履歴だけを対象にし、別branch、public web、実consumer手編集を根拠にしていません。本呼出しでコード変更、削除、test、commit、push、PR、Issue投稿、consumer移行は行っていません。

## 2. 結論

Windows対応は、旧R/D/Pの「Linux/macOS/Windowsを最小adapterで扱う」という設計判断から、identity、Start lock、guarded JSON reader、専用test、CI laneまで実装途中で接続されています。しかしwork-targetのWindows公開・解除storeは未接続で、実Windows/NTFS合格証拠もありません。2026-10-02 JSTの最新利用者決定により、これらは完成対象ではなく撤去対象です。

Issue #413の本体である外部CLI化、Git管理領域の独自control/台帳/cache/daemon撤去、同clone必要時観測、worktreeごとの直接一件、Start-only flock、Git原文/partial、GitHub完了、Sync表示はWindows撤回と独立して維持できます。単純なcommit revertは共通POSIX修正とE2Eを巻き戻すため採用しません。

## 3. Windows要求が混入した場所

### verified facts

| 層 | 現SHAの事実 | 現在の扱い |
|---|---|---|
| requirement | 実装開始条件に「Windows用の最小adapterまで設計」と記載 | 最新決定で失効。Linux/macOSへ差替え |
| design D-03 | POSIX no-replaceとWindows non-replacement moveを並記 | Windows句だけ削除。POSIX fsync/no-follow/no-replaceを維持 |
| design D-05 | Windows VolumeSerial/FileId128、Global named mutex、WAIT_ABANDONED、NTFS受入を契約化 | 全て撤去。Linux/macOS flockだけ残す |
| domain | `PhysicalIdentity` が `Literal["posix","windows"]`、Windows hex32を受理 | posix/10進だけへ狭める |
| identity | `DirectoryIdentity` がWindowsDirectoryとPOSIX descriptorを分岐 | Windows field/import/branchを削除 |
| Start lock | `windows_mutex_name`、WindowsMutex、win32 branchが接続 | Windows symbols/branchを削除。POSIX timeout/flock/finallyを維持 |
| JSON reader | `read_guarded_json_bytes` がWindowsDirectory readerを接続 | Windows branchを削除。POSIX exact bytes/no-followを維持 |
| work-target store | Windows `_open` は `NotImplementedError`; publish/remove未接続 | Windows完成せず、専用文言を除去してsupport guardへ一本化 |
| Windows module | `infra/windows_handles.py` にWindowsDirectory/WindowsMutex/native API | file削除。compat alias/fallbackなし |
| tests | Windows mutex/directory/JSON三file、native WAIT_ABANDONED/NTFS case | 専用三fileとnative部分を削除。共有POSIX native casesを維持 |
| CI | `provider-windows-native-adapters` / windows-latest lane | job削除。Ubuntu/macOS full/distribution laneを維持 |
| schema | identity enum posix/windows、Windows hex32 branch | work-target v1のままposix限定 |
| evidence | Windows未実施・skip・調査資料 | raw evidenceとして保全し、現在のgateから外す |

### 履歴の区別

- `b33b7a7174e4d46ae2aefcd44f3f9e8defa470b1`: Windows named mutexを導入したが、同commitにtimestamp/input等の共通hardeningも同居します。
- `8a70a8b30e69fe0bda6db6c45ef555f44411236d`: Windows native/CI準備と、Linux/macOSにも必要な実console E2E・provenance・共通検証が同居します。
- `3b0c69e8d61ad7ad5b01307dd301963a2cab180d`: Windows parent-handle directory補強と証拠更新。
- `6032621c2bd68ab9051b8929dd17d536a4114ad7`: Windows JSON read接続と専用test・証拠更新。

したがって `git revert b33... 8a... 3b... 603...` のようなcommit単位巻戻しは、共通POSIX修正、E2E、文書履歴を不必要に失い得ます。P-18はcurrent treeでfile/symbol依存を切り、POSIX characterizationを通してから削除します。

### inference

Windows形のwork-target recordを正式に公開できるstoreは現SHAで未接続です。このためWindows identity shapeは製品として導入完了した互換契約ではないと判断します。ただし手作業fixtureや外部保全物の存在まではGitHub sourceだけで証明できないため、P-18.1のread-only scanを停止条件にします。

### unverified

- 許可対象consumer/外部backupに `platform:"windows"` recordが実在しないこと。
- Windows directory durability調査のraw exit130 logの正確なpath/hash。
- Linux `121228c6fca1fd016e7bccef009902396112ba43` のraw log保存path。件数・PATH原因・hashは利用者提供事実で、P-18実装時にCodex保有物と照合が必要です。
- 旧要求付きCode Review Strict r12の最終結果。別session進行中で、新OS範囲の最終gateではありません。

## 4. 残す・削除・変更するもの

| file / symbol / dependency | 行為 | 理由・保全条件 |
|---|---|---|
| `runtime/infra/windows_handles.py` 全体 | 削除 | Windows専用。未完成storeを完成させない |
| `identity.py::_windows`, WindowsDirectory imports/branches | 削除 | POSIX descriptorだけを正本化。verify/fstat/closeは保持 |
| `start_lock.py::windows_mutex_name`, `_mutex`, win32 acquire/release | 削除 | Start-only flockを維持し、別lockへ置換しない |
| `json_store.py` WindowsDirectory read branch | 削除 | POSIX guarded reader、exact bytes、single-link/no-followは保持 |
| `work_target_store.py` Windows-specific NotImplementedError | 変更 | support guardで業務前拒否。publish/remove本体は変更最小 |
| `work_target.py::PhysicalIdentity` | 変更 | platform=posix、device/file_id decimal。WorkTarget/Scope IDは不変 |
| `data-schema.json::$defs.identity` | 変更 | v1/$idを維持してPOSIX限定。新version不要 |
| Windows専用三test | 削除 | 非対応機能のport testをgateにしない。raw logsは保持 |
| native lock test | 部分変更 | Windows/NTFS/WAIT_ABANDONEDだけ削除。POSIX別process/kill/同clone/別cloneを保持 |
| directory identity test | 部分変更 | conditional Windows期待をPOSIX期待へ狭める |
| provider CI Windows job | 削除 | Linux/macOS support scope。既存二OS laneは減らさない |
| runtime dispatch | 最小変更 | utility後・業務前の一guard。広いOS abstractionなし |
| POSIX descriptor/no-follow/fsync/no-replace/flock | 維持・強化 | データ保全、late removal、Start-only exclusionの核心 |
| Git raw stderr/returncode、partial/unknown | 維持 | Windows撤去と無関係な確定契約 |
| Scope schema3/IDs/metadata/workspace | 変更なし | Windows identityはwork-targetだけ。consumer移行しない |
| historical R/P/evidence | 保全＋current注記 | 当時の事実を消さず、未完了Windows義務だけ失効 |

## 5. OS/FSと必要原語

### 対応範囲

- Linux: local filesystem上のdescriptor-based no-follow、fstat identity、flock、file/directory fsync、`renameat2(RENAME_NOREPLACE)`。
- macOS: APFSを主要受入FSとし、descriptor-based no-follow、fstat identity、flock、file/directory fsync、`renameatx_np(RENAME_EXCL)`。
- Python:既存下限3.10、CI 3.11、現在のmacOS 3.12証拠を分けて記録。

### 非保証

Windows、network filesystem、複数host共有mount、異OS同時mount、原語を提供しないfilesystemを対応済みとしません。原語不足を新しい管理機構で補完せず、該当業務操作を副作用前に停止します。

### utilityとwriter

help/version/completionはplatform/context-freeのままです。対応OSguardはutility dispatch後に一度だけ実行します。非対応OSの代表writerは、project/Git/GitHub/file効果前に `UNSUPPORTED_PLATFORM`、effects=[]で拒否します。Windows全leaf/native/FSのtestは要求しません。

## 6. work-target v1とschema判断

採用案は **v1を維持したPOSIX限定** です。

- POSIX recordのfield、basename token、scope_id、github_ref、selected_branch/at、identityの意味は変えません。
- Windows形はpublish/removeが未接続で実受入証拠もないため、unionを互換負債として残しません。
- Scope schema3、workspace protocol、ID採番に波及させません。
- 新しいschema/version/IDを発行しません。
- 実在Windows recordが見つかった場合は、この判断の前提が崩れるためP-18を停止し、削除/変換せず別decisionを要求します。

## 7. 既存正本・証拠の更新方針

### 全文置換を提供するfile

- `requirement.md`
- `design.md`
- `plan.md`
- `artifacts/data-schema.json`
- `artifacts/acceptance-matrix.md`
- `artifacts/implementation-acceptance-evidence.md`
- 新規 `artifacts/os-support-decision.md`
- 新規 `artifacts/os-support-retirement-analysis.md`
- 新規 `artifacts/os-support-retirement-plan.md`

### 今回全文置換しないfileと必要hunk

| file | 必要hunk | 今回上書きしない理由 |
|---|---|---|
| `artifacts/source-basis.md` | verified target SHA、親source、4 commitのWindows/共通分類、最新OS authorityへのlink | 現SHAには29,846 bytesの広いsource inventoryがあり、本呼出しでは全文を置換根拠として取得していないため、推測で既存inventoryを失わせない |
| `artifacts/traceability.json` | P-18と新artifact path、RQ/AC既存IDの追加edge。新RQ/ACは作らない | 現SHAの16,996 bytesのmachine schema/全edgeを本呼出しで全文検査していないため、既存edgeを推測で置換しない |
| `README.md` / docs reference / skills | supported OS、unsupported rejection、P-18 order | 配布static ownership/hash更新と同時にP-18で実施 |
| `explanation.html` / `index.html` | OS scope、Windows撤去、P-18→P-13順、図/目次/anchor | 共有template/JS/modal byte契約と実ブラウザ検査が必要 |
| 既存 `manifest.json` | 全採用fileの新sha256/bytes | 既存pack全体を更新する実装stepで再生成 |
| `implementation-report.md` | P-18実施後に実施者がappend | 既存巨大履歴を第三者分析で上書きしない |
| report/interview/user-decisions/raw reviews/evidence | 変更なし | authority/raw evidence保全 |

## 8. 採用条件

この分析は採用候補であり、実装開始許可ではありません。更新済み正本をtarget branchへ通常pushし、そのfull SHAを再検証した後、独立ChatGPT Implementation Brief StrictでP-18の具体command・担当・commit/review境界を確定します。P-18の完了後にP-13、P-14、FQへ進み、人間merge後だけP-16/P-17を実施します。

## 2026-10-02 採用時のCodexローカル照合

第三者の回答時点の「Linux再実行予定」「r12進行中」は、下記の実測で更新します。原本ZIP・[回答原文](os-retirement-chatgpt-121228c6.md)は変更していません。

- [限定read-only scan](os-retirement-record-scan-121228c6.json): 同cloneの7 worktreeと所有するIssue413検証consumer/backupを確認。観測した6 recordはいずれもPOSIX、Windows record 0、読取error 0、書込0。未提示の外部backupまでは調査していません。実在Windows recordが後で判明すれば変換せず停止します。
- [Linux通常全件](linux-full-121228c6.md): PATHだけ補正した同SHAの通常fullは1900 passed / 20 skipped、977.90秒、actual exit0。324 input filesの前後hash一致。
- [r12 complete batch](code-review-p06-12-analysis.md): actual exit10、P1一件、review_status=fail。invalid/unavailableの選択観測でも明示FinishがCloseへ進む不具合はPOSIXにも存在するためP-07で修正します。新OS範囲のfinal passには流用しません。
- 実装担当は利用者の継続指定GPT-6.1 Sol / Max。後続briefの著述モデルはGPT-5.6 Sol / Proで、担当設定の再決定ではありません。
- Windows source撤去と、それをimportする廃止testの削除は一つのGreenなcommitにし、壊れた収集状態をcheckpointとして提出しません。独立CI変更は別commitにします。
