# Issue #413 文書整備の採用・検証記録（2026-10-04）

## 完了したこと

GPT-5.6 Sol / ProのChatGPT Use Strictで、GitHub上の指定branchとfull SHA `8606e132327066d56567556e336e4bc1ae6a0b17` を照合し、README、AGENTS.md、配布文書・skill・system・template、IssueのR/D/Pと人間向けHTMLを分析しました。返却された一つのZIPから22件の全文置換fileを採用しました。

[第三者分析](documentation-analysis-20261003.md)、[原応答の表示版](documentation-response-20261003.md)、[原置換manifest](documentation-replacements-manifest-20261003.json)、[変更不要とした文書](documentation-unchanged-20261003.md)を保存しています。表示版はMarkdownの行末空白だけを正規化し、受領した原応答はWorkbenchに保全しています。[取得ZIP](../../iss-00413-documentation-replacements.zip)のSHA-256は `d2e2d3305fc2cdd7212c75b86730a1a4268c2e23d1bae88194ba3269e5e80f9f` です。

主な修正は、provider開発source・外部に導入した実行package・worktreeごとの静的資産・ignoredな直接作業記録の区別、現在のArtifact import文法、Startだけの短い排他、active-noneの案内、実装とrolloutの集約表示です。新しいcommandや編集権限制御は追加していません。

配布元16資産のhashと既知旧hashを実体から更新し、公開CLIの `installation update` で現在0805 worktreeへ反映しました。手作業でconsumerや`.agents`を正本化していません。Gitの空行検査で見つかったrequirement.mdとprovider template READMEの余分な末尾空行一行だけを正規化し、原ダウンロードは不変で保持しました。pack READMEの入口と派生manifest/ZIPも現在の証拠へ更新しました。

## 既存Final Quality Gateの扱い

[原Gate](final-quality-gate-8606e132.json)は、対象SHA `8606e132327066d56567556e336e4bc1ae6a0b17`、pass、13観点、coverage complete、P0/P1=0、情報提供P2=3のまま保持しました。原文SHA-256は `133314892aef89d82d62c943bc95aeace197fdb67ef72044a62b9e535abbf0a6` です。[同SHAのCode Review](code-review-8606e132.json)と[完了証拠](completion-evidence-8606e132.json)もbyteを変更せず保存しています。

利用者の指示に従い、今回の文書差分に追加レビューやFinal Quality Gate再実施は行っていません。実行コード・test・CI・build/dependency設定の237 fileはGate対象とbyte一致します。今回の文書commitを新しいGate認定済みSHAとは表現しません。

元GateのP2三件のうちplanの集約表示を文書上修正しました。効果前mkdirの結果分類、非UTF-8 pathname診断のJSON境界は、情報提供された製品側の既知事項のままです。

## 今回の現物確認

- 文書・配布・authoring・fresh wheelの既存試験: 269 passed、actual exit 0。
- `make lint`: ruff check、ruff format、mypyがすべて成功。
- provider source・最終wheel・導入済み通常packageの197 fileがbyte一致。
- 一時consumerの86静的資産と現在consumerの85管理対象資産が配布元とbyte一致（init-only workspace宣言は現更新対象外）。
- 仕様とworkspace宣言の2636 regular fileが更新前とbyte一致。現在240 Scopeのvalidateが成功し、直接選択はemptyのまま。
- HTMLの4/4図がinline SVGとして描画。クリック・キーボード・倍率境界・focus・閉じる操作のvalidatorがactual exit 0。
- [Tailscaleの同じURL](http://100.85.74.8:8765/specdock-issue-413/explanation.html)はHTTP 200で、配信bytesと現HTML sourceが一致。

詳細な値は[文書検証JSON](documentation-verification-20261004.json)を参照してください。最初の配布試験は投影更新前のtemplate README不一致一件で停止しましたが、通常CLI反映後は成功しました。sandbox内ではChrome DevTools起動に失敗したため、許可された独立一時profileで再実施して成功しました。いずれも失敗した元logをWorkbenchに保全しています。

## 今回完了扱いにしないもの

mainとほか3 linked worktreeの移行、clone全体の完全なSync、正式Issue #413 import/Start、ancestor #31のreopen/付替え、人間merge、package publicationは実施していません。文書整備後は通常commit/pushとPR作成へ進み、提出後の最新check状態はGitHub PRを参照します。復旧planning packは引き続き実装資料の正本であり、正式Start成功の証拠ではありません。
