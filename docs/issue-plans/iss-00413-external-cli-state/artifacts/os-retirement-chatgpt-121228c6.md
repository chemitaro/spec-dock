# GitHub connector検証結果

検証は成功しました。

- repository: `chemitaro/spec-dock`
- target branch: `codex/iss-00413-external-cli-state`
- expected SHA: `121228c6fca1fd016e7bccef009902396112ba43`
- GitHub上のbranch tip: `121228c6fca1fd016e7bccef009902396112ba43`
- SHA比較: **完全一致**
- 他branch・main・public webへのfallback: **なし**

対象commitは資料更新commitで、親は製品source候補 `2b2be5e227ddf4d067da083bba15a8ec23d21367` です。mainの `6fec3099d8759b4e5b3b393b2987534b46dfa383` は利用者提示の比較基準としてのみ扱い、main branch自体は分析根拠へ切り替えていません。

# 第三者分析の結論

## 1. Windows対応は、要求からCIまで部分的に接続されている

旧requirementは、Windowsについて「最小adapterまで設計する」と明記していました。これは未回答のOS判断ではなく、現在の利用者決定によって明示的に失効する旧要求です。attachments-bundle

現SHAでは、Windows対応は次の範囲まで入っています。

- `domain/work_target.py::PhysicalIdentity` が `posix | windows` を受理し、Windowsの128-bit file IDを許容する。
- `infra/identity.py::DirectoryIdentity` が `WindowsDirectory` とPOSIX descriptorを分岐して使用する。
- `infra/start_lock.py` が `windows_mutex_name`、`WindowsMutex`、Win32 acquire/release経路を持つ一方、POSIXでは既存directory descriptorに `flock` する。
- `infra/json_store.py::read_guarded_json_bytes` が `WindowsDirectory.read_file_bytes` に接続されている。
- `infra/windows_handles.py` に `WindowsDirectory`、`WindowsMutex`、Win32/Nt APIが実装されている。
- ただし `infra/work_target_store.py::_open` はWindowsで `NotImplementedError("Windows selection adapter is not connected yet")` を返しており、直接対象の公開・解除は未接続である。
- `provider-ci.yml` には、Ubuntu/macOSの共通distribution laneとは別に、`windows-latest` でmutex、directory、JSON readerを走らせる専用jobが追加されている。

したがって現在の状態は、**Windows対応済み**でも**単なる未着手**でもなく、identity・reader・mutex・test・CIまでは接続され、work-target writerと実Windows/NTFS受入は未完成という「実装途中」です。

## 2. 撤回後も維持すべき本体機能

Windows対応の撤回は、Issue #413の目的を撤回しません。次を維持します。

| 維持対象 | 判断 |
|---|---|
| 外部インストールCLI | 維持 |
| help/version/completionのcontext-free性 | 維持。対応OS判定より先に処理 |
| Initiative/Epic/Issue三階層 | 維持 |
| GitHub必須の新規ID、UUID廃止 | 維持 |
| 同cloneのmain/linkedだけを観測 | 維持 |
| 一worktree一直接対象 | 維持 |
| Startのbranch作成・checkout | 維持 |
| 重複確認から直接記録までの短い排他 | Linux/macOSのdirectory descriptor＋`flock` として維持 |
| 通常編集・Finish・Sync等への包括lockなし | 維持 |
| FinishのGitHub closed/completed、branch保持 | 維持 |
| 自動rollbackなし、Git原文・partial/unknown保持 | 維持 |
| Syncの複数選択観測 | 維持 |
| 独自 `.git` control、台帳、cache、daemonなし | 維持 |
| work releaseや代替管理基盤 | 追加しない |

POSIX側のdescriptor/no-follow、single-link regular file検査、正確な入力bytes、file/directory `fsync`、無上書きrename、観測済みbasenameだけの解除は、Windows撤去と無関係なデータ保全境界です。これらを削除対象へ巻き込んではいけません。現sourceでも、Windows分岐とは別にPOSIX reader、no-follow open、no-replace publication、directory `flock` が存在します。

## 3. commit単位のrevertは採用しない

履歴上のWindows commitをまとめて `git revert` する方法は適切ではありません。

- `b33b7a7174e4d46ae2aefcd44f3f9e8defa470b1` にはWindows mutexだけでなく、共通入力・時刻処理等のhardeningが同居しています。
- `8a70a8b30e69fe0bda6db6c45ef555f44411236d` にはWindows native/CI準備だけでなく、Linux/macOSにも必要な実console E2E、provenance、共通検証が同居しています。
- `3b0c69e8d61ad7ad5b01307dd301963a2cab180d` と `6032621c2bd68ab9051b8929dd17d536a4114ad7` はWindows directory/JSON接続が中心ですが、証拠・計画更新も含みます。

採用案は、**current tree上でfile/symbol単位にWindows依存を外し、各段階でPOSIX characterizationを通す外科的撤去**です。

# 残す・削除する・変更するもの

| 区分 | file / symbol | 処置 |
|---|---|---|
| 削除 | `src/spec_dock/runtime/infra/windows_handles.py` | file全体を削除。互換aliasやdead copyは残さない |
| 削除 | `identity.py` の `_windows`、`WindowsDirectory` import/branch | POSIX descriptor、`fstat`、verify、closeを維持 |
| 削除 | `start_lock.py::windows_mutex_name`、`WindowsMutex`、win32 acquire/release | POSIX timeout、`flock`、finally解放を維持 |
| 削除 | `json_store.py` のWindows reader branch | POSIX exact-bytes/no-follow/single-link readerを維持 |
| 変更 | `work_target_store.py` のWindows専用 `NotImplementedError` | Windows storeを完成させず、公開入口のunsupported拒否へ一本化 |
| 変更 | `PhysicalIdentity` | `platform="posix"`、10進 `device` / `file_id` のみに狭める |
| 変更 | `artifacts/data-schema.json::$defs.identity` | `$id` と `specdock.work-target/v1` を維持したままPOSIX限定 |
| 削除 | `test_windows_mutex.py`、`test_windows_directory.py`、`test_windows_json_read.py` | Windows専用testを削除 |
| 部分変更 | `test_issue413_native_lock.py` | NTFS、WAIT_ABANDONED、Windows helperのみ削除。POSIX別process/kill/同clone/別cloneは保持 |
| 部分変更 | `test_directory_identity.py` | Windows conditional expectationを除去しPOSIX保全試験を保持 |
| 削除 | `provider-ci.yml::provider-windows-native-adapters` | Ubuntu/macOSの既存lane、lint、full pytest、E2Eは維持 |
| 最小変更 | utility後のbusiness dispatch | 非対応OSをGit/GitHub/file効果前に `UNSUPPORTED_PLATFORM`、`effects=[]` で拒否 |
| 変更なし | Scope schema3、Scope ID、metadata、workspace protocol | Windows work-target identityから波及させない |
| 変更なし | consumer `spec-dock/` | P-18分析時には手編集・移行・削除しない |
| 保全 | 旧Windows調査、review、測定log | raw evidenceとして残し、現在の完成義務だけ失効させる |

# work-target v1のschema判断

採用案は、**schema versionを増やさず、`specdock.work-target/v1` のidentityをPOSIX限定へ狭める**ことです。

理由は、Windows形のreader/identity/mutexは存在しても、選択recordの公開・解除writerが未接続で、実Windows/NTFS受入証拠もないためです。macOSの最新製品sourceでは1916 passed / 4 skippedですが、そのskipには実Windows専用試験が含まれ、Windows成功証拠ではありません。attachments-bundle

ただし、次の停止条件を置きます。

> provider fixture、現在の許可対象consumer、外部backupのいずれかに、実在する `specdock.work-target/v1` の `platform:"windows"` recordが見つかった場合、P-18を停止する。削除・変換せず、互換方針を別の明示決定へ戻す。

これにより、未導入のWindows形を理由なく永久互換として残すことも、実在データを黙って切り捨てることも避けます。Scope schema3、新規ID方式、workspace protocol、basename tokenには変更を広げません。

# 追加必須作業 P-18

P-18はP-13の最終実入口検証、P-14、Final Quality Gateより前の必須作業として定義しました。

| unit | 作業 | 意味のある検証・停止条件 |
|---|---|---|
| P-18.1 | 最新authority、branch/SHA、source/test/CI inventory、実record scan | SHA/branch不一致、dirty、実在Windows record、未分類callerで停止 |
| P-18.2 | POSIX work-target v1とunsupported guardを先にRed/Green化 | Windows identityが通るRed、writerが副作用へ進むRed、utilityがguardで失敗するRed |
| P-18.3 | JSON reader→identity→Start lock→store文言→`windows_handles.py` の順で撤去 | 各段階の前後でPOSIX exact bytes、no-follow、publication、late removal、flockを同じassertionで確認 |
| P-18.4 | Windows専用testとCI jobを撤去 | Ubuntu/macOS lane、POSIX native/E2E、Python 3.10/3.11試験を一緒に消すdiffで停止 |
| P-18.5 | R/D/P/schema/matrix/evidence、reference/skills、HTML、ZIPを同期 | raw review/log、report類、interview/user-decisionsを上書きしない |
| P-18.6 | Linux/macOS focused/full/lint/wheel/manual gate | candidate SHA、OS/Python/FS、wheel hash、exit、skip、raw logを環境別に記録 |

commit/review境界も、authority/schema、source撤去、test/CI撤去、資料配送、OS別証拠の5単位に分けています。一括revertや一commitへの混載は採用しません。

P-18の計画登録、正本push、後続Implementation Briefの作成をSpecDock正式Startとは呼びません。P-16の実consumer切替とP-17の正式import/Startは、人間merge後の別手順として維持しています。

# 現在の検証状態

macOSについては、親source候補 `2b2be5e227ddf4d067da083bba15a8ec23d21367` で通常full pytest 1916 passed / 4 skipped / exit 0、fresh wheel、外部noneditable venv、実console 14操作が記録されています。Windows native/NTFS、live GitHub、最終gateの全面合格ではありません。attachments-bundle

Linuxについては、利用者提供の `121228c6...` の結果を次のように保持しました。

- 4 failed / 1884 passed / 20 skipped / 12 errors、947.99秒、exit 1。
- 子processが検証containerのPATHから `uv` を見つけられない状態。
- 現時点では製品不具合ともLinux合格とも断定しない。
- 元結果を変更せず、再実行時は検証containerのPATHだけを修正する。
- provider source/testsは変更せず、324 filesのbefore/after hash一致を再確認する。

本呼出しでは、製品コード変更、製品test、commit、push、PR、Issue投稿、consumer移行を行っていません。実施したのは、GitHub connector検証、第三者分析、差替え文書生成、JSON/anchor/manifest/ZIPの静的検査です。旧要求付きCode Review Strict r12は別sessionのcheckpoint分析として扱い、新OS範囲の最終gateには流用していません。

# 生成物

## 一括ZIP

issue-413-os-support-retirement.zip[issue-413-os-support-retirement.zip](sandbox:/mnt/data/issue-413-os-support-retirement.zip)

- 単一root: `issue-413-os-support-retirement/`
- ZIP size: 112,170 bytes
- ZIP SHA-256: `31cfc245b0b393a626d02c877b029542ef4c4f845569744da1dccc5531b93a29`
- entries: 12
- manifest記載payload: 11 files。manifest自身は再帰hashを避けるため自己entryを省略し、その規則を明記
- ZIP CRC、展開後bytes、manifestの各sha256/bytes: 一致
- RQ: 18件、AC: 42件、Plan anchor: 18件
- POSIX example: schema適合
- Windows identity example: schema拒否

## 主要ファイル

| ファイル | 内容 |
|---|---|
| os-support-retirement-analysis.md[第三者分析](sandbox:/mnt/data/issue-413-os-support-retirement/docs/issue-plans/iss-00413-external-cli-state/artifacts/os-support-retirement-analysis.md) | verified facts、推論、未確認、file/symbol単位の残置・撤去判断 |
| os-support-retirement-plan.md[P-18詳細計画](sandbox:/mnt/data/issue-413-os-support-retirement/docs/issue-plans/iss-00413-external-cli-state/artifacts/os-support-retirement-plan.md) | authority、順序、Red/Green、commands、停止条件、commit/review境界 |
| os-support-decision.md[対応OS決定記録](sandbox:/mnt/data/issue-413-os-support-retirement/docs/issue-plans/iss-00413-external-cli-state/artifacts/os-support-decision.md) | 2026-10-02 JSTの最新決定と旧authorityとの関係 |
| requirement.md[requirement.md](sandbox:/mnt/data/issue-413-os-support-retirement/docs/issue-plans/iss-00413-external-cli-state/requirement.md) | RQ/AC IDを維持した完成差替え版 |
| design.md[design.md](sandbox:/mnt/data/issue-413-os-support-retirement/docs/issue-plans/iss-00413-external-cli-state/design.md) | POSIX-only設計、utility独立、file/symbol対応 |
| plan.md[plan.md](sandbox:/mnt/data/issue-413-os-support-retirement/docs/issue-plans/iss-00413-external-cli-state/plan.md) | P-01〜P-17履歴を保全しP-18をP-13前に追加 |
| data-schema.json[data-schema.json](sandbox:/mnt/data/issue-413-os-support-retirement/docs/issue-plans/iss-00413-external-cli-state/artifacts/data-schema.json) | `$id` / work-target v1を維持したPOSIX identity |
| acceptance-matrix.md[acceptance-matrix.md](sandbox:/mnt/data/issue-413-os-support-retirement/docs/issue-plans/iss-00413-external-cli-state/artifacts/acceptance-matrix.md) | 既存42 ACとP-18の対応 |
| implementation-acceptance-evidence.md[implementation-acceptance-evidence.md](sandbox:/mnt/data/issue-413-os-support-retirement/docs/issue-plans/iss-00413-external-cli-state/artifacts/implementation-acceptance-evidence.md) | macOS/Linux/Windows履歴証拠と現在の認定境界 |
| manifest.json[manifest.json](sandbox:/mnt/data/issue-413-os-support-retirement/manifest.json) | relative path、SHA-256、bytes |
| self-check.json[self-check.json](sandbox:/mnt/data/issue-413-os-support-retirement/self-check.json) | JSON、ID、anchor、リンク、ZIP検査結果 |

`artifacts/source-basis.md`、`traceability.json`、README/reference/skills、既存HTML、既存repository manifestについては、広い既存inventoryや共有templateを推測で全文上書きしないため、必要hunkと理由だけを第三者分析書に明示しました。GitHub上にはこれらを含む既存の広いartifact集合が存在するため、P-18実装時に実体を全文確認して局所更新する扱いです。

`report.md`、`implementation-report.md`、既存 `user-decisions.md`、`interview-worktree-start.md`、raw reviews、過去測定evidenceはZIPへ含めず、生成・上書きしていません。

閲覧用の本Markdownは行末空白だけ整形しています。[raw JSON](os-retirement-chatgpt-121228c6-raw.json)は元回答の完全UTF-8 bytesとSHA-256を保持します。
