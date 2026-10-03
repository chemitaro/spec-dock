# 採用Aの実装・外部CLI更新記録

基準は `b15f56585bd15b36504dd5d0c919c4f31b1ef039`。この記録は採用Aの修正後・独立レビュー前の実測であり、fresh Final Quality Gateの認定ではない。

## 修正した製品動作

GitのNUL区切りpathname検索で選択IDの現在pathを求める。tracked/untracked（ignore対象を含む）を扱い、製品側で無関係なScopeの実体を走査しない。対象/祖先のnofollow検証と既存metadata規則を維持した。現存対象重複・redirect・Gitのエラー/警告/timeoutはunavailable、対象不存在はstaleとして既知ID/refを保持する。CLIのtimeoutを対象限定callerから伝える。

外部CLIの新規導入→三階層import→commit→Startの手動確認で、標準の `epics/rules.md` をEpic directoryと誤認する既存不具合を発見した。committed_workspaceの構造判定にも正規Scope dirname規則を適用して修正した。Scope-shaped file/symlinkの拒否は維持する。最初の失敗はeffects=[]/exit3であり、同じconsumerを修正後に再開した。

## TDDと関連検証

- 公開Sync: 選択Issueに無関係なfileでexit7になるRedを再現し、同じ試験をGreenにした。
- Git警告時の不完全検索: staleとして黙って扱うRedを再現し、native警告を保持したunavailableへ修正した。
- 標準import後のStart: `committed Scope or container is not a directory` / exit3のRedを再現し、branch作成/checkoutを含むGreenにした。
- Sync/observation/Start/active/Scope publicationの関連257 tests成功、77.53秒、actual exit0。通常make lintでruff check・format・mypy成功。
- 未追跡/ignore対象、現在pathの移動、対象重複・祖先redirect・不存在、Git検索のexit/timeout/警告、無関係なlstat禁止、readonly record/metadata、別WTの無関係なfileがStartを阻害しないことを公開CLIで確認した。

## インストールした実CLIでの確認

fresh wheelをcheckout外の非editable環境へインストールした。新規consumerでinstallation initとScope importをCLI経由で実施し、そのconsumerを同じGit cloneのlinked WTとともに使用した。修正版の実consoleで8操作を確認した: help、validate、peer Issue 3 Start、main Issue 4 Start、二選択のGitHub-source Sync、同一Issueの重複Start拒否、Issue 4 Finish、解除後active確認。Startはbranch作成/checkout、Finishはcompleted Closeとbranch保持を確認した。Gitは実Git、GitHubだけ所有するfake ghで、live GitHub Closeやpytest test bodyの呼出しではない。

検証済みwheelを `uv tool install --force --offline --no-cache` で普段の外部packageへ更新した。外部の197 package filesについてwheel/provider/installed bytes一致を確認した。

- wheel SHA-256: `7ba3aed1edc3a69037ed9ce938d376b956c9ba5548eeb8b7c789637af4efbe91`
- provider file fold: `9c1bc94177342ae1814531bafe183210f46255fd0ea76b02de7cd3ab3240df52`
- `./spec -h`: exit0。
- `./spec workspace validate --json`: exit0、valid=true、240 Scope。
- `./spec active show --json`: exit0、empty。
- `./spec workspace sync --json`: exit7/effects=[]、現在WTはemptyとして読取可能。他4実WTは旧schema/protocol/selectionのためunavailable。

## 残る境界

旧FQ failのraw JSON/stateは保存する。P1 FQG-413-001は修正候補であり、独立closureは未取得。P2二件は情報のみで改修しない。fresh Code Review Strictとfresh FQ v2、同一候補SHAの全必須検証をこれから行う。

他4実WT、closed GitHub祖先#31、正式#413 import/Startは変更していない。現在WTの動作確認をmain WTの更新や正式Start成功へ転記しない。PR/merge/package公開も未実施。
