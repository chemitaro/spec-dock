# 標準text表示と現行開発手順の整合

## 仕様と修正

- 正文の [C-01](cli-contract.md#catalog) は `scope show` の対象/authorityと、`active show` の直接選択/導出祖先/branchを表示する契約である。
- 修正前の標準textは成功/失敗headerとeffectsだけで、Scope、Active、Doctorのtyped dataを表示していなかった。JSONで取得できても通常の操作では内容を読めない。
- `presentation/envelope.py` にFamilyData/ActiveDataと非空DiagnosticDataの表示を追加した。公開typed dataを既存redactorへ通してから読みやすく整形する。Artifact本文を読む変更ではない。
- [C-04](cli-contract.md#json) の公開JSON v2、Sync/依存の既存text、native Git stderr、exit/effectsは維持する。書込/保存/共通lock/新leafは追加しない。

## テスト先行の証拠

| 公開保証 | 新しい試験 |
|---|---|
| ScopeのID/title/GH authority/path/未観測unknownを標準textで読み、全tree不変 | test_scope_text_read_displays_the_target_authority_and_path_without_changing_files |
| empty/selected直接対象・GH ref・current branchを標準textで読み、記録不変 | test_active_text_read_displays_empty_or_selected_direct_and_current_branch |
| Doctorのfinding/unverifiedを読み、秘密値を出さない | test_text_diagnostic_displays_findings_and_unverified_items_with_secret_redaction |

同三testは製品修正前に3 failed/21 deselected（0.22秒、exit1）、修正後に3 passed/21 deselected（0.22秒、exit0）。Redでは実際のheader-only出力が原因だった。関連九suiteは176 passed（42.57秒、exit0）。CLI contract、JSON redaction、native Git、query guards、Active、依存、Sync、fresh wheel/sdist/外部consoleを含む。

## 開発手順書

AGENTS.mdの旧nested runtime/fixed bundleの案内を、通常packageとsrc/spec_dock/runtime/へ修正した。active show/scope showの返却pathで正本文書を読む。明示した復旧packは正式Startの証拠にしない。actual dogfoodへの適用は承認済みのP-16/P-17へ残す。

既存CLI contract/authoring kit二suiteは236 passed（2.37秒、exit0）。実在source pathを確認し、旧外部entrypoint名の操作案内は0。agent-firstのCLI使用、metadata手編集禁止、厳密な破壊対象指定、人間merge gateは保持した。文書変更のためだけの試験は追加しない。

全source/testsのRuff check/format（317 files）、MYPYPATH=srcを明示した変更三Python filesの限定mypy、git diff --checkが成功した。限定mypyを通常full type gateの代わりにしない。

## 外部実consoleの限定手動確認

関連suiteで作られた通常wheelのenvelope.py bytesが現sourceと一致することを再確認した。

- wheel SHA-256: `97378c2ab1a8a9d88f23c926a0a2c7b0009b267ca355f19a5b439a552830538b`
- package metadata version: `0.2.4`
- 非editable import元: provider外venvの `lib/python3.12/site-packages/spec_dock/`
- 実環境: Darwin 27.0.0 arm64、Python 3.12.11。Windows/Linuxのnative確認ではない。
- providerとconsumerの外のCWDからinstalled consoleを絶対pathで起動。PYTHONPATH/PYTHONHOMEを除去。
- 一時native Git consumerで `scope show`（text/JSON）、`active show`（empty text、selected text/JSON）の五read-only操作がexit0/stderr空。ID/GH authority/unknown/path/current branchを表示し、各操作前後の全tree digestが一致した。
- 独自.git領域を作成せず、準備した選択record bytesを保持。selected fixtureはtest準備であり製品Startではない。live GitHub/actual dogfoodを操作していない。
- 0.66秒、exit0。一時consumerを終了時に削除した。最初のscriptはcurrent_branchをcurrentと誤記してassert失敗した。製品Redへ数えず、元logを保持して項目名だけ訂正した。

## 全体gateとの区別

この小変更前のclean `32c372e156b2fc7955f2c3aad3abf2d5c4f960da` は通常全pytestで1878 passed/1 skipped（340.17秒、exit0）。元コマンドはskip理由を収集していないため理由を推測しない。同snapshotの通常make lintはRuff成功・mypy 37 errors/12旧source files（236 source files）、make exit2で未合格。新しいtext/手順変更後の全gate合格ではない。

P-12は継続中。残る旧source/testの個別退役、通常full gates、native OS/別Python、fresh Strict、最終手動検証を継続する。実dogfoodのcutoverと正式#413 Startは未実施。

## 原log

既存Epic Workbenchの `iss-00413-implementation/` に保持:

- `pytest-text-result-red.log`, `pytest-text-result-green.log`, `pytest-text-result-related.log`
- `pytest-current-operator-docs.log`
- `manual-public-text-output.log`（確認scriptの項目名誤り）, `manual-public-text-output-2.log`（成功）
- `pytest-p12-32c372e1.log`, `lint-p12-32c372e1.log`（変更前の通常gate）
