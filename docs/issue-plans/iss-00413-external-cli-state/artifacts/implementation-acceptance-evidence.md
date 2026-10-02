# Issue #413 製品の検証証拠と残る条件

2026-10-02更新。RQ/ACの判定条件は [要件](../requirement.md) と [対応表](acceptance-matrix.md) が正本です。この表は現在までの実行証拠であり、42 ACの全件合格やP-13完了の認定ではありません。

## 対象候補と結果

| 対象SHA・範囲 | 実行条件・結果 | 証拠と制限 |
|---|---|---|
| `8a70a8b30e69fe0bda6db6c45ef555f44411236d` / 通常全pytest | macOS 27.0.1 arm64、実Python 3.12.11、clean checkout。1 failed / 1847 passed / 2 skipped、479.73秒、exit 1 | `pytest-macos-full-8a70a8b3.log`。[比較不一致の調査](validation-readonly-investigation.md)。全件成功とは扱わない |
| 同SHA / 通常全pytest | Linux 7.0.14 / glibc 2.41 / x86_64、実Python 3.11.16、clean独立clone。1832 passed / 18 skipped、1125.68秒、exit 0 | `pytest-linux-python311-8a70a8b3.log`。固定Docker image、ネットワークなし、read-only root、capability 0、tmpfs fixture。arm64ホスト上のamd64実行であり物理Linux端末とは区別 |
| 同SHAの製品source / 手動console | 通常wheelを外部venvへ非editable install、pip check成功、コピーしたsource pathを参照不能にした実console。help→Start→重複拒否→兄弟Start→Sync→Finish→次Start→native hook部分失敗→現物確認を個別実行 | [手動確認](manual-product-smoke.md) と [原文・観測](manual-console-8a70a8b3.json)。実Git、GitHub境界だけstateful fake gh。pytestのtest bodyを手動結果に読み替えていない |
| 同SHA / native Start lockとidentity | macOSの最終三suiteは8 passed / 1 skipped、0.82秒。実Python 3.10.15のnative suiteは3 passed / 1 skipped、0.89秒。Linux全pytestでもPOSIX native casesを実行 | [native lock](native-start-lock-boundary.md)。同一clone/別clone、別process、kill後の解放。Windows限定caseのskipは成功に含めない |
| 同SHA / Windows | native Win32 mutex・directory identityのCI laneを用意 | **未実行**。NTFS/WAIT_ABANDONED/native成功の証拠なし。guarded保存adapterは未接続。[OS別状態](native-platform-status.md) |
| 製品source不変・比較診断追加 / validate | 該当validation suiteは80 passed、12.70秒、exit 0。独立40 fixtureの同一公開CLI比較も40/40成功 | 元の全件失敗の原因は未確定。再確認成功だけで失敗を撤回しない |
| 比較診断追加 / 通常make lint | Ruff check/format 298 files、mypy 217 source files、exit 0 | `lint-validation-readonly-diagnostic.log`。skip/ignore/収集除外を増やしていない |

元logはEpic配下のGit-ignored `.workbench/iss-00413-implementation/` に保持し、作業記録と結果を正本へ残します。各件数は対象候補単位であり、異なるSHAの件数を合算しません。

Linuxの18 skipはzsh不在12件、Win32限定1件、macOS stage契約1件、Linux匿名stageにpathname cleanupがない4件です。macOSの2 skipはWin32限定1件、Linux O_TMPFILE限定1件です。これらを別OSでの実行成功と呼びません。

## 認定と実環境作業

- P-12進行中。P-13/P-14の試験・資料準備を先行しているが、依存stepの完了認定とは別。
- 現在候補のCode Review Strict、Final Quality Gate、merge-ready PRは未完了。仕様の独立レビューpassや過去のコードレビューpassを流用しない。
- Windows保存・native受入、macOS全件の比較不一致、最終候補の全件検査を未完了として保持する。
- 人間merge後のP-16実consumer切替、P-17正式#413 import/Startは未実施。旧control/metadata/activeを復旧例外で手編集しない。
