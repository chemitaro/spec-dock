# Issue #413 製品の検証証拠と残る条件

2026-10-02更新。RQ/ACの判定条件は [要件](../requirement.md) と [対応表](acceptance-matrix.md) が正本です。この表は現在までの実行証拠であり、42 ACの全件合格やP-13完了の認定ではありません。

## 対象候補と結果

| 対象SHA・範囲 | 実行条件・結果 | 証拠と制限 |
|---|---|---|
| 75ac57604f5b95f1c50a2e7214d711bc720fb0eb / 通常全pytest | macOS arm64、実Python3.12.11、clean checkout。1900 passed / 4 skipped、388.57秒、exit0 | [Scope事前判定を含む最新全件](macos-full-75ac5760.md)。通常pytestを直接実行、実行前後のHEAD/clean/source不変を照合 |
| 同SHAの製品source / 手動console | 外部fresh venvへ通常wheelを非editable install、pip check、元provider pathを参照不能にした実consoleで14操作を個別実行 | [最新手動確認](manual-console-75ac5760.md)と[原文・観測](manual-console-75ac5760.json)。実Git、GitHub境界だけstateful fake gh。旧手動証拠は別sourceとして保持 |
| `6032621c2bd68ab9051b8929dd17d536a4114ad7` / 通常全pytest | macOS arm64、実Python 3.12.11、clean checkout。1876 passed / 4 skipped、366.99秒、exit0 | [Windows JSON読取を含む全件](macos-full-6032621c.md)。独自runnerなし。この後のScope原語確認の追加変更は含まない |
| `3b0c69e8d61ad7ad5b01307dd301963a2cab180d` / 通常全pytestと同じ選択 | macOS 27.0.1 arm64、実Python 3.12.11、clean checkout。1853 passed / 2 skipped、402.78秒、exit0 | [runner修正と全件](macos-full-3b0c69e8.md)。最初の2 failed / 1851 passed / 2 skippedも保持。製品source/testsを変更せず、ignored runnerだけを修正 |
| `1e5d2586678927866e9ec0eae804cdd4d55ff138` / 通常全pytest | macOS 27.0.1 arm64、実Python 3.12.11、clean checkout。1848 passed / 2 skipped、424.21秒、exit 0 | `pytest-macos-full-1e5d2586.log`。変更pathの比較診断を含む全件。Git Trace2は外部owned logだけへ保存し、製品のGit環境除去を変更しない。過去の不一致の原因確定とは別 |
| `8a70a8b30e69fe0bda6db6c45ef555f44411236d` / 通常全pytest | macOS 27.0.1 arm64、実Python 3.12.11、clean checkout。1 failed / 1847 passed / 2 skipped、479.73秒、exit 1 | `pytest-macos-full-8a70a8b3.log`。[比較不一致の調査](validation-readonly-investigation.md)。全件成功とは扱わない |
| 同SHA / 通常全pytest | Linux 7.0.14 / glibc 2.41 / x86_64、実Python 3.11.16、clean独立clone。1832 passed / 18 skipped、1125.68秒、exit 0 | `pytest-linux-python311-8a70a8b3.log`。固定Docker image、ネットワークなし、read-only root、capability 0、tmpfs fixture。arm64ホスト上のamd64実行であり物理Linux端末とは区別 |
| 同SHAの製品source / 手動console | 通常wheelを外部venvへ非editable install、pip check成功、コピーしたsource pathを参照不能にした実console。help→Start→重複拒否→兄弟Start→Sync→Finish→次Start→native hook部分失敗→現物確認を個別実行 | [手動確認](manual-product-smoke.md) と [原文・観測](manual-console-8a70a8b3.json)。実Git、GitHub境界だけstateful fake gh。pytestのtest bodyを手動結果に読み替えていない |
| 同SHA / native Start lockとidentity | macOSの最終三suiteは8 passed / 1 skipped、0.82秒。実Python 3.10.15のnative suiteは3 passed / 1 skipped、0.89秒。Linux全pytestでもPOSIX native casesを実行 | [native lock](native-start-lock-boundary.md)。同一clone/別clone、別process、kill後の解放。Windows限定caseのskipは成功に含めない |
| 同SHA / Windows | native Win32 mutex・directory identityのCI laneを用意 | **未実行**。NTFS/WAIT_ABANDONED/native成功の証拠なし。guarded保存adapterは未接続。[OS別状態](native-platform-status.md) |
| 製品source不変・比較診断追加 / validate | 該当validation suiteは80 passed、12.70秒、exit 0。独立40 fixtureの同一公開CLI比較も40/40成功 | 元の全件失敗の原因は未確定。再確認成功だけで失敗を撤回しない |
| 比較診断追加 / 通常make lint | Ruff check/format 298 files、mypy 217 source files、exit 0 | `lint-validation-readonly-diagnostic.log`。skip/ignore/収集除外を増やしていない |

元logはEpic配下のGit-ignored `.workbench/iss-00413-implementation/` に保持し、作業記録と結果を正本へ残します。各件数は対象候補単位であり、異なるSHAの件数を合算しません。

Linuxの18 skipはzsh不在12件、Win32限定1件、macOS stage契約1件、Linux匿名stageにpathname cleanupがない4件です。過去macOSの2 skipはWin32限定1件、Linux O_TMPFILE限定1件です。6032621cの4 skipには実Windows JSON/hardlinkと親path置換の二件も含まれます。これらを別OSでの実行成功と呼びません。

## 2026-10-02 後続のWindows物理directory補強

baseline ccf9637dからWindowsDirectoryを親handle基準のNtOpenFileへ変更した。[境界の記録](windows-directory-anchor.md)に二つのRed→Greenと、Mac/実3.10各21 passed/1 skipped、通常make lint成功を保存した。変更後のclean 3b0c69e8は上表のmacOS全件を成功させた。Linux/手動の8a70a8b3と製品source差分があるため、それらを後続候補の全面合格へ読み替えない。Windows保存/native受入と現在候補のStrict/FQは未完了。

続くbaseline9a97f758から[Windows JSON reader](windows-json-read.md)を接続した。関連八suiteはMac3.12/実3.10で各58 passed/3 skipped、通常lint成功。接続時は3b0c69e8の全件後のsource差分だったが、そのreaderを含むclean6032621cの通常全件は上表のとおり1876 passed/4 skipped、exit0で成功した。Windows native・保存/各公開/processとStrict/FQの合格ではない。

[Scope公開の原語確認](scope-publication-capability.md)はbaseline6032621c後の追加修正。既知の未対応をremote観測/変更とdry-run成功判定の前に検出し、関連九suiteはMac3.12/実3.10各287 passed/2 skipped、通常lint成功。その修正を含むclean75ac5760の全件は上表の1900 passed/4 skipped、exit0。sourceの関連287件へ合算せず、Windows保存/nativeとStrict/FQは未完了として扱う。

## 2026-10-02 後続Startの保存原語確認

[追加修正](start-publication-capability.md)はbaseline578f27e3。既知の未対応symbolによるGit branch/checkout後のpartial6を公開CLIで再現し、公開を必要とするStartだけをGit変更前に拒否するよう修正した。三階層・apply/dry-run・platform/symbol欠落、旧記録保全と公開不要の同一Startの16組を検証。関連八suiteはMac3.12で266 passed（102.42秒）、実3.10で266 passed（102.77秒）、通常lint成功。上表の75ac5760全件・手動結果はこの後続sourceを含まず、今回の266件と合算しない。実Windows保存/native、現在候補の全件・最終手動・Strict/FQは未完了。

## 認定と実環境作業

- P-12進行中。P-13/P-14の試験・資料準備を先行しているが、依存stepの完了認定とは別。
- 現在候補のCode Review Strict、Final Quality Gate、merge-ready PRは未完了。仕様の独立レビューpassや過去のコードレビューpassを流用しない。
- Windows保存・native受入、過去のmacOS比較不一致の原因、最終認定候補の全件検査を未完了として保持する。macOSの最新全件成功を過去の失敗の撤回へ使わない。
- 人間merge後のP-16実consumer切替、P-17正式#413 import/Startは未実施。旧control/metadata/activeを復旧例外で手編集しない。
