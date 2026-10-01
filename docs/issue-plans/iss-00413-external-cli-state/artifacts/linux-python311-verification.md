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
