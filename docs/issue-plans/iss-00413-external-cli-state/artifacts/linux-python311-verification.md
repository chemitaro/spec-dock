# Linux / Python 3.11の予備検証とfixture補正

対象はclean `bdf44fe26927e8534f6f108e9753cf36b12bfcfe` と、Artifact試験二行だけを追加した候補。P-12中の検証であり、通常full lint、P-13、Windows native、fresh Strict、Final Quality Gate、最終手動確認の合格ではない。

## 実行環境

- DockerのLinux container、実Python 3.11.16、uv 0.11.24、package 0.2.4。AMD64 imageをARM64 host上で実行した。CPUの仮想化・変換を介しており、物理Linux機の実績とは区別する。
- image `sha256:c514701300438939d8f2f3fd75cc57ea2eff502c1920e5cc98c713cf17452e3d`、OS `Linux-7.0.14-orbstack-00380-ga7e0a2dc9535-x86_64-with-glibc2.41`。
- sourceは既存Epic Workbench内の独立したローカルclone。HEAD、clean status、`sys.prefix=/fixture/project/.venv`、provider import元を確認した。実consumerやそのGit内の情報へ適用しない。
- sourceはhost bind mount、pytest一時fixtureはLinux tmpfs。依存とbuild backendを先に準備し、試験中は`--network none`、`UV_OFFLINE=1`、read-only container rootとする。live GitHubは利用しない。
- 初回準備の`uv sync --no-env-file`は非対応optionでexit1。helpに照合してこのoptionだけを外し、準備をexit0で完了した。これは製品Redではない。

## 初回全件と原因の切り分け

通常pytest全件は **1844 passed / 7 failed / 17 skipped、870.24秒、exit1**。七失敗を破棄せず、全文を保持した。

1. Artifactの六template試験は、ホストの`USER`環境変数があることに依存していた。containerでは未設定で、現行実装は作成者を推測せず`<YOUR_NAME>`を残す。試験内で`USER=Fixture author`を明示し、元のplaceholder・timestamp・既存evidence保全条件を維持したうえで、実際の作成者文字列もassertする。
2. Startのnative rename拒否試験は、directoryを0500にして書込み拒否を発生させる。初回containerはUID0のcapabilityでこれを迂回した。独立したnative rename probeで、初回条件は成功、`--cap-drop ALL`ではPermissionErrorを確認した。製品の権限設定は変えず、以後のLinux試験からこの迂回権限を外す。元のnative拒否試験をfakeやskipに置換しない。

test補正前、capabilityだけを外した同じ七casesは **6 failed / 1 passed、5.56秒、exit1**。Start試験だけが通り、Artifact fixtureの問題は残った。この結果を製品機能のRed→Greenに数えない。

## 補正後の実測

| 検証 | 結果 |
|---|---|
| Linux、capabilityなし、同じ七cases | **7 passed、5.53秒、exit0** |
| macOS / 既定Python 3.12、ArtifactとStartの全二suite | **139 passed、40.56秒、exit0** |
| 全source/tests Ruff check / format | 成功、311 files |
| `MYPYPATH=src` の変更test限定mypy | 成功、1 file。通常full lintの代替ではない |
| diff check | 成功 |

Linux補正候補は上記base SHAと、変更一testのSHA256 `0e140621c391b2976e72d8a0a64b6cc84a65aaac5f89446dc73690b996754479`を照合した。tracked変更はこの一fileだけ、stageされた変更なし、実効capabilityは0、`USER`はcontainer全体では未設定のままと確認した。production変更、assertion緩和、test選択・skip条件の変更はない。全件再実行は後続候補で別に完了させ、初回の1844件とfocused七件を合算してfull passと記録しない。

初回17 skipは、未導入Zshの12 cases、macOS専用named-stageの一case、Linux anonymous publicationで適用しないnamed-stage cleanupの四cases。いずれもnative成功件数に含めない。

元logsは既存Epic Workbenchの`iss-00413-implementation/pytest-linux-python311-bdf44fe2.log`、`pytest-linux-capability-isolation.log`、`pytest-linux-fixture-green.log`、`pytest-linux-fixture-macos.log`、準備の`linux-prepare-bdf44fe2.log`と`linux-prepare-bdf44fe2-2.log`へ保持する。試験用runnerとcloneは次のLinux全件検証に再利用し、完了後に所有した一時dataを整理する。

## 二回目の全件とbootstrap fixtureの補正

clean `c4c26bdb231a37c6491a5ac1d3614dde564e0ca5` を同じLinux/Python 3.11.16環境で再検証した。実効capability0、USER未設定、source/import/prefixとclean HEADを再照合した全件結果は **1839 passed / 1 failed / 17 skipped、921.27秒、exit1**。Artifact六casesとnative Start拒否は成功した。skipの内訳は初回と同じで、native成功には数えない。

残る `test_bootstrap_keeps_a_started_hook_unknown_when_process_termination_reports_io_failure` はhook起動前のGit rev-parseが100msのCLI timeoutを超え、GIT_FAILED/exit5/effects=[]となった。意図したmake起動後の終了応答失敗には到達していない。同じclean SHAでの単独再実行は **1 passed、0.74秒、exit0** であり、常に起きる製品不具合とは判定しない。仮想化・変換を介した全件実行の負荷でもGit preflightへ到達できるよう、testの有限timeoutを2.0秒にした。hookのsleep5より短く、実際のtimeout・process-group終了・OSError・unknown効果と元assertionsを全て維持する。製品のtimeout処理は変更しない。

補正候補は旧c4c26bdbと変更一testのSHA256 `c5c094c27a08d278a8b70fe91d5caf915d26a345824bb2663fe9db99627a611a` を照合した。Linux cloneのtracked変更はこの一fileだけ、staged変更なし。direct_bootstrap.pyとproject_hook.pyのbytesは現在の主checkoutとも一致する。

| 補正候補の検証 | 実測 |
|---|---|
| Linux/Python 3.11.16、capability0、bootstrap全suite | **32 passed、20.48秒、exit0** |
| macOS/既定Python 3.12、bootstrap全suite | **32 passed、7.82秒、exit0** |
| 全Ruff check/format（304 files）、MYPYPATH=srcの変更test限定mypy、diff check | 成功。full lintの代替ではない |

test削除、assertion緩和、skip/収集除外追加、製品source変更は0。現在のadapter/Delete退役を含まない全件結果とfocused結果を合算してpassにせず、後のclean候補でfull gateを閉じる。元logsは `pytest-linux-python311-c4c26bdb.log`、`pytest-linux-hook-isolation.log`、`pytest-bootstrap-timeout-{linux,macos}.log`。全件runner/補正候補runnerと検証cloneはWorkbench内の一時dataであり、実consumerやGitHubへの変更ではない。

## 三回目のclean全件

clean `0fd8764f0b1e64778344615e04c9d6428f1b827b` の通常全pytestは **1851 passed / 17 skipped、932.00秒（15分31秒）、exit0**。同じ実Linux/Python 3.11.16、実効capability0、USER未設定、offline/no-network、Linux tmpfs fixtureで実行した。run前にclean HEAD、uv.lock/pyproject/testの主checkoutとのbytes一致、実prefix/provider import元を再確認し、元の一回のsessionを完了まで待った。

17 skipはZsh未導入の12 cases、macOS named-stage capability probeの一case、Linux匿名stageでは適用しないpathname cleanupの四cases。skip追加、test選択変更、native成功への読み替えはない。UID0でもcapabilityを全て外しており、実directory権限によるStart rename拒否もこの全件に含む。

この結果にはadapter/Delete退役とbootstrap timeout fixture補正が含まれる。後続 `7d29648d` の旧Create/Artifact writer退役・追加試験は含まれない。先行の失敗/個別試験を合算して合格にせず、このclean SHA一回のexit0だけを全件証拠とする。P-12中の予備検証であり、現在候補のfull lint、P-13、Windows native、fresh Strict、Final Quality Gate、最終手動確認の完了ではない。

元logは `iss-00413-implementation/pytest-linux-python311-0fd8764f.log`。独立clone・offline依存・runnerは必要な後続検証へ再利用し、所有した一時dataだけを後で整理する。実consumer/live GitHubは未変更。

## 四回目のclean全件と配布console

clean `e11f187931a70ce2859527bb8eaf3ffc6e8b8fc9` の通常全pytestは **1827 passed / 17 skipped、1016.04秒、exit0**。旧Create/Artifact・Active/Sync/依存チェックの退役と共有型修正を含む。実効capability0、USER未設定、offline/no-network、Linux tmpfs、候補HEAD/clean statusと実prefix/providerを元の一回のsessionで検査した。17 skipはZsh 12/macOS専用probe 1/匿名stageのpathname cleanup非該当4であり、native成功へ換算しない。

全件job終了後、同じ所有cloneを通常のlocal fetch/detached checkoutでclean `6824b3f834f076f99372ba34e64bb76bcabe0d44` へ進めた。前候補とのsrc/README/pyproject/uv.lockのdiffは0。このSHAで追加した配布consoleの一caseは **1 passed、25.04秒、exit0**。別venv・非editable wheel・offline依存解決とpip check、source path改名、実Git clone/linked WT、重複Startの無副作用拒否、兄弟Issue並行、readonly Sync、completed GET後のFinish、次Issue Startを検査した。GitHubはstateful gh process代替でありlive実績ではない。全件と追加caseを合算して別SHAの全件成功にしない。

元logsはpytest-linux-python311-e11f1879.log、pytest-linux-python311-fresh-console-6824b3f8.log。後続の非POSIX directory診断とprovenance強化はこの二runに含まれず、[OS別状態](native-platform-status.md)へ分けて記録する。Windows接続/native、現在候補のfresh Strict/Final Quality Gate/手動確認、実consumer適用は未完了。
