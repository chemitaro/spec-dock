# 配布wheelの実consoleによる一連の作業検証

## 対象と実際の環境

- providerの基準HEAD: `e11f187931a70ce2859527bb8eaf3ffc6e8b8fc9`。製品sourceはこのHEADと一致し、新しいtest harnessは未コミット候補で実行した。
- `tests/integration/test_issue413_e2e.py` を追加した。providerを所有するfixtureへコピーしてwheelを作り、別venvへ非editable導入する。依存を省略せず、UV_OFFLINE=1の通常uv pip resolverを使い、pip checkも通す。
- build用source pathを改名し、PYTHONPATH/PYTHONHOMEを渡さず、provider外のcwdからinstalled実consoleを起動する。別の `python -I` probeでsite-packagesからのimportを照合する。実checkoutを改名しない。
- macOS 27.0.1/arm64のfixture FSはAPFS。dfとmountの対象deviceが一致した。diskutilはsandbox内でDiskManagement frameworkを利用できず、FS確認の成功には数えない。
- 実Python 3.12.11: wheel SHA256 `df80481b2befde3a0ea447826f18ea65805e612f12ca015c7966a3345100981f`、1 passed（8.73秒）、exit0。
- 実Python 3.10.15: wheel SHA256 `b5d2ec660574fca4823a4e3fb3276480ea3fee05d136178cf2fbe3f687c544b7`、1 passed（9.06秒）、exit0。隔離venv/prefixとproviderをrunnerで検査し、製品consoleはさらに別の3.10 venvを使った。

## 検証した利用者の操作

| 操作 | 実結果・守った境界 |
|---|---|
| fresh Git cloneとlinked worktreeを用意 | fixtureの三階層GitHub-backed metadataと四canonical文書をcommitし、実Gitでclone/add。別cloneのseedを同cloneの一覧へ混ぜない |
| Issue AのStart preview | Git/作業tree全file bytes・modeが不変。.agentは作らない |
| main WTでIssue AをStart | branch issue-aの作成・checkoutと直接記録一件。git statusはclean |
| linked WTで同じIssue AをStart | exit3/SCOPE_ALREADY_SELECTED/effects=[]。ref、linked WTと先行recordのbytesは不変 |
| linked WTで兄弟Issue BをStart | branch issue-bと独立record一件。共有engineや名簿を作らない |
| GitHub sourceのSync | 二つの直接Issueを表示。Initiative/Epicのdescendant_selected_count=2、Epicのdirect_selected_count=0。両WTの全file bytes・modeが不変 |
| Issue AのFinish preview | fake remoteはopen、捕捉recordも不変 |
| Issue AのFinish apply | PATCHはAのcompleted Close一回だけ。最後のGETでcompleted確認後、Aのrecordを解除。branch issue-aに留まり、Bのrecordは不変 |
| main WTでIssue CをStart | 別branch issue-cと新token一件。Aの終了後の連続作業が成立し、Bは保全 |

全Scope metadata・本文・workspace宣言・ignore bytesを保全した。各WTのgit statusはclean、記録directoryには最終file一件だけでstage残骸なし。旧active/cache/runtime copyと独自Git controlは作らない。

## 本物と代替境界の区別

Gitとinstalled consoleは実processであり、製品API/dispatchをmockしない。GitHubだけはPATH上のstateful外部gh scriptで代替し、24 GET/1 PATCHを記録する。実GitHubへは送信しておらず、live Closeや本番dogfoodの開始証拠ではない。42 AC全体、競合process/native kill、Windows、最終手動操作、Strict/FQをこの一caseから完了へ変更しない。

初回はfixtureが存在しないselector active:currentを使い1 failed（7.23秒）、exit1。leaf helpとcanonical D-07、実parserの@currentを照合し修正した。製品Redには数えない。最初の成功（10.76秒）後、依存省略installを通常offline install/pip checkへ改め、同じcaseを再実行した。試験や製品のskip/型ignore/除外を追加しない。

## 通常gateと元の証拠

このtest追加前のclean e11f1879の通常macOS/Python 3.12全pytestは1843 passed/1 skipped（446.22秒）、exit0。skipは既存Linux O_TMPFILE capability test。この全件結果に追加testの一caseを加算して新候補の全件成功とは呼ばない。

testの最終形で通常make lintはRuff check/format（297 files）とmypy（216 source files）が成功、exit0。元logs/provenance/操作JSONは既存Epic Workbenchのiss-00413-implementationへ保持した:

- pytest-macos-full-e11f1879.log
- pytest-fresh-console-lifecycle-{1,2,3}.log、pytest-fresh-console-lifecycle-python310.log
- lint-fresh-console-lifecycle.log、lint-fresh-console-lifecycle-2.log
- fresh-console-lifecycle-macos-python{312,310}.json

ここまでの記録の時点ではLinux console caseと後続受入は未完了だった。追加結果を下に記録する。

## Linuxでの追加確認とprovenance強化

clean 6824b3f8のLinux/Python 3.11.16で同じconsole caseは1 passed（25.04秒）、exit0。前候補e11f1879とのsrc/README/pyproject/uv.lockのdiffは0を確認した。全件試験はe11f1879の1827 passed/17 skipped（1016.04秒）、exit0として[別記録](linux-python311-verification.md)へ保存し、case数を合算しない。

後続harnessはbaseline HEAD、製品sourceのtracked status、コピーした入力fileの相対名/内容hashのfold、wheel hashをstdoutへ記録する。作業中のsource deltaをHEADと同一にしない。未接続directory adapterの修正候補を含むmacOS console caseは1 passed（9.03秒）、exit0。source statusはjson_store.pyの変更一件で、入力SHA256はaedb8204b19e3694c0a14842b5149921d039f8731beda5eed5b8a7af189da0e4、wheel SHA256は2db17f135866086b1608843f11a7c7c9d50ce953964b091f83dc1df20fc915d7。元logはpytest-fresh-console-provenance.log。

[OS別の状態](native-platform-status.md)と併せて解釈する。Windows保存/公開/native、現在候補のfresh Strict/Final Quality Gate/最終手動確認、実consumerへの適用は未完了。
