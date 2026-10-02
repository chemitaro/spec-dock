# Issue #413 製品の検証証拠と残る条件

2026-10-02 JSTの対応OS決定を反映した採用正本。RQ/ACの判定条件は [要件](../requirement.md)、OS authorityは[対応OS決定](os-support-decision.md)、撤去順序は[P-18](../plan.md#p-18)が正本です。この表は現在までの実行証拠を保全し、新しいOS範囲で42 ACの全件合格、P-18/P-13完了、Final Quality Gateを認定するものではありません。

## 対象候補と結果

| 対象SHA・範囲 | 実行条件・結果 | 証拠と制限 |
|---|---|---|
| `121228c6fca1fd016e7bccef009902396112ba43` / verified branch tip | GitHub connectorで `chemitaro/spec-dock` / `codex/iss-00413-external-cli-state` / full SHAを完全一致確認。commitは資料更新で、親は `2b2be5e227ddf4d067da083bba15a8ec23d21367` | P-18実装前checkpoint。source/tests/CIは親と同一という利用者提供事実を、実装開始時に再照合する |
| `121228c6fca1fd016e7bccef009902396112ba43` / Linux通常full pytest（利用者提供local evidence） | Linux x86_64、Python3.11.16。4 failed / 1884 passed / 20 skipped / 12 errors、947.99秒、exit1 | 4 failures/12 errorsはchild processがPATHからuvを見つけられない検証container設定。製品不具合ともLinux合格とも断定しない。元結果を保持し、container PATHだけを補正して再実行済み（次行参照）。before/after 324 files hash `2bcbce60d8b318761f81529c4b998fae4d43027b52470fba317143400547494e` 一致、raw log所在はCodex側で要照合 |
| 2b2be5e227ddf4d067da083bba15a8ec23d21367 / 通常全pytest | macOS arm64、実Python3.12.11、clean checkout。1916 passed / 4 skipped、434.98秒、exit0 | [Start事前判定を含む最新全件](macos-full-2b2be5e2.md)。通常pytestを直接実行し、前後のHEAD/clean/source不変を照合 |
| 同SHAの製品source / 手動console | 外部fresh venvへ通常wheelを非editable install、pip check、元provider pathを参照不能にした実consoleで14操作を個別実行 | [最新手動確認](manual-console-2b2be5e2.md)と[原文・観測](manual-console-2b2be5e2.json)。実Git、GitHub境界だけstateful fake gh・26 request。Windows/live GitHub/全leafの全面合格ではない |
| 75ac57604f5b95f1c50a2e7214d711bc720fb0eb / 通常全pytest | macOS arm64、実Python3.12.11、clean checkout。1900 passed / 4 skipped、388.57秒、exit0 | [Scope事前判定を含む先行全件](macos-full-75ac5760.md)。通常pytestを直接実行、実行前後のHEAD/clean/source不変を照合 |
| 同SHAの製品source / 手動console | 外部fresh venvへ通常wheelを非editable install、pip check、元provider pathを参照不能にした実consoleで14操作を個別実行 | [先行手動確認](manual-console-75ac5760.md)と[原文・観測](manual-console-75ac5760.json)。実Git、GitHub境界だけstateful fake gh。旧手動証拠は別sourceとして保持 |
| `6032621c2bd68ab9051b8929dd17d536a4114ad7` / 通常全pytest | macOS arm64、実Python 3.12.11、clean checkout。1876 passed / 4 skipped、366.99秒、exit0 | [Windows JSON読取を含む全件](macos-full-6032621c.md)。独自runnerなし。この後のScope原語確認の追加変更は含まない |
| `3b0c69e8d61ad7ad5b01307dd301963a2cab180d` / 通常全pytestと同じ選択 | macOS 27.0.1 arm64、実Python 3.12.11、clean checkout。1853 passed / 2 skipped、402.78秒、exit0 | [runner修正と全件](macos-full-3b0c69e8.md)。最初の2 failed / 1851 passed / 2 skippedも保持。製品source/testsを変更せず、ignored runnerだけを修正 |
| `1e5d2586678927866e9ec0eae804cdd4d55ff138` / 通常全pytest | macOS 27.0.1 arm64、実Python 3.12.11、clean checkout。1848 passed / 2 skipped、424.21秒、exit 0 | `pytest-macos-full-1e5d2586.log`。変更pathの比較診断を含む全件。Git Trace2は外部owned logだけへ保存し、製品のGit環境除去を変更しない。過去の不一致の原因確定とは別 |
| `8a70a8b30e69fe0bda6db6c45ef555f44411236d` / 通常全pytest | macOS 27.0.1 arm64、実Python 3.12.11、clean checkout。1 failed / 1847 passed / 2 skipped、479.73秒、exit 1 | `pytest-macos-full-8a70a8b3.log`。[比較不一致の調査](validation-readonly-investigation.md)。全件成功とは扱わない |
| 同SHA / 通常全pytest | Linux 7.0.14 / glibc 2.41 / x86_64、実Python 3.11.16、clean独立clone。1832 passed / 18 skipped、1125.68秒、exit 0 | `pytest-linux-python311-8a70a8b3.log`。固定Docker image、ネットワークなし、read-only root、capability 0、tmpfs fixture。arm64ホスト上のamd64実行であり物理Linux端末とは区別 |
| 同SHAの製品source / 手動console | 通常wheelを外部venvへ非editable install、pip check成功、コピーしたsource pathを参照不能にした実console。help→Start→重複拒否→兄弟Start→Sync→Finish→次Start→native hook部分失敗→現物確認を個別実行 | [手動確認](manual-product-smoke.md) と [原文・観測](manual-console-8a70a8b3.json)。実Git、GitHub境界だけstateful fake gh。pytestのtest bodyを手動結果に読み替えていない |
| 同SHA / native Start lockとidentity | macOSの最終三suiteは8 passed / 1 skipped、0.82秒。実Python 3.10.15のnative suiteは3 passed / 1 skipped、0.89秒。Linux全pytestでもPOSIX native casesを実行 | [native lock](native-start-lock-boundary.md)。同一clone/別clone、別process、kill後の解放。Windows限定caseのskipは成功に含めない |
| 同SHA / Windows（履歴証拠） | native Win32 mutex・directory identityのCI laneを用意した履歴 | **未実行**。NTFS/WAIT_ABANDONED/native成功の証拠なし。guarded保存adapterは未接続。2026-10-02の最新決定で対応義務は失効し、P-18の削除対象。[OS別状態](native-platform-status.md) |
| 製品source不変・比較診断追加 / validate | 該当validation suiteは80 passed、12.70秒、exit 0。独立40 fixtureの同一公開CLI比較も40/40成功 | 元の全件失敗の原因は未確定。再確認成功だけで失敗を撤回しない |
| 比較診断追加 / 通常make lint | Ruff check/format 298 files、mypy 217 source files、exit 0 | `lint-validation-readonly-diagnostic.log`。skip/ignore/収集除外を増やしていない |

元logはEpic配下のGit-ignored `.workbench/iss-00413-implementation/` に保持し、作業記録と結果を正本へ残します。各件数は対象候補単位であり、異なるSHAの件数を合算しません。

Linuxの18 skipはzsh不在12件、Win32限定1件、macOS stage契約1件、Linux匿名stageにpathname cleanupがない4件です。過去macOSの2 skipはWin32限定1件、Linux O_TMPFILE限定1件です。6032621cの4 skipには実Windows JSON/hardlinkと親path置換の二件も含まれます。これらを別OSでの実行成功と呼びません。

## 現在のOS範囲と証拠の読み方

- 対応OSはLinux/macOS。Windows native/store/CI passは今後のrelease gateではない。
- Windows関連commit・test・測定は、混入経路と削除理由を監査できるraw evidenceとして残す。過去ログの削除、成功/失敗の書換え、異なるSHAの件数合算をしない。
- `b33b7a71` と `8a70a8b3` にはWindows変更とLinux/macOS共通修正/E2Eが同居するため、commit単位revertを採用しない。file/symbol単位のP-18とPOSIX characterizationを先行する。
- current Code Review Strict r12は `121228c6fca1fd016e7bccef009902396112ba43` のcheckpoint分析だが旧Windows要求を添付した別sessionで完了しP1一件・failで、新OS範囲の最終gateや重複reviewではない。
- P-18実装、撤去後のLinux/macOS full/wheel/manual、fresh Strict、Final Quality Gateは未実施。PATH補正後の121228c6 fullは下記のbaseline証拠。

## 2026-10-02 後続のWindows物理directory補強（履歴証拠）

baseline ccf9637dからWindowsDirectoryを親handle基準のNtOpenFileへ変更した。[境界の記録](windows-directory-anchor.md)に二つのRed→Greenと、Mac/実3.10各21 passed/1 skipped、通常make lint成功を保存した。変更後のclean 3b0c69e8は上表のmacOS全件を成功させた。Linux/手動の8a70a8b3と製品source差分があるため、それらを後続候補の全面合格へ読み替えない。Windows保存/native受入と現在候補のStrict/FQは未完了。

続くbaseline9a97f758から[Windows JSON reader](windows-json-read.md)を接続した。関連八suiteはMac3.12/実3.10で各58 passed/3 skipped、通常lint成功。接続時は3b0c69e8の全件後のsource差分だったが、そのreaderを含むclean6032621cの通常全件は上表のとおり1876 passed/4 skipped、exit0で成功した。Windows native・保存/各公開/processとStrict/FQの合格ではない。

[Scope公開の原語確認](scope-publication-capability.md)はbaseline6032621c後の追加修正。既知の未対応をremote観測/変更とdry-run成功判定の前に検出し、関連九suiteはMac3.12/実3.10各287 passed/2 skipped、通常lint成功。その修正を含むclean75ac5760の全件は上表の1900 passed/4 skipped、exit0。sourceの関連287件へ合算せず、Windows保存/nativeとStrict/FQは未完了として扱う。

## 2026-10-02 後続Startの保存原語確認（POSIX共通証拠）

[追加修正](start-publication-capability.md)はbaseline578f27e3。既知の未対応symbolによるGit branch/checkout後のpartial6を公開CLIで再現し、公開を必要とするStartだけをGit変更前に拒否するよう修正した。三階層・apply/dry-run・platform/symbol欠落、旧記録保全と公開不要の同一Startの16組を検証。関連八suiteはMac3.12で266 passed（102.42秒）、実3.10で266 passed（102.77秒）、通常lint成功。75ac5760の全件・手動結果はこの後続sourceを含まない。後続のclean2b2be5e2は上表の通常全件1916 passed/4 skipped、手動14操作を確認し、関連266件と合算しない。実Windows保存/nativeと現在候補Strict/FQは未完了。

## 認定と実環境作業

- P-12進行中。P-18は追加計画のみで実装未着手。P-13/P-14の準備を先行していても、依存stepの完了認定とは別。
- 現在候補の新OS範囲Code Review Strict、Final Quality Gate、merge-ready PRは未完了。旧要求付きr12、仕様の独立レビューpass、過去のコードレビューpassを流用しない。
- Windows保存・native受入は未完了条件ではなく撤去対象。過去のmacOS比較不一致、Windows未実行、Linux PATH失敗の元結果を保持し、新しい成功で撤回しない。
- 人間merge後のP-16実consumer切替、P-17正式#413 import/Startは未実施。旧control/metadata/activeやWindows identityを復旧例外で手編集しない。

## 2026-10-02 採用時のCodexローカル照合

第三者の回答時点の「Linux再実行予定」「r12進行中」は、下記の実測で更新します。原本ZIP・[回答原文](os-retirement-chatgpt-121228c6.md)は変更していません。

- [限定read-only scan](os-retirement-record-scan-121228c6.json): 同cloneの7 worktreeと所有するIssue413検証consumer/backupを確認。観測した6 recordはいずれもPOSIX、Windows record 0、読取error 0、書込0。未提示の外部backupまでは調査していません。実在Windows recordが後で判明すれば変換せず停止します。
- [Linux通常全件](linux-full-121228c6.md): PATHだけ補正した同SHAの通常fullは1900 passed / 20 skipped、977.90秒、actual exit0。324 input filesの前後hash一致。
- [r12 complete batch](code-review-p06-12-analysis.md): actual exit10、P1一件、review_status=fail。invalid/unavailableの選択観測でも明示FinishがCloseへ進む不具合はPOSIXにも存在するためP-07で修正します。新OS範囲のfinal passには流用しません。
- 実装担当は利用者の継続指定GPT-6.1 Sol / Max。後続briefの著述モデルはGPT-5.6 Sol / Proで、担当設定の再決定ではありません。
- Windows source撤去と、それをimportする廃止testの削除は一つのGreenなcommitにし、壊れた収集状態をcheckpointとして提出しません。独立CI変更は別commitにします。
