# Scope lifecycle確認中の選択変更を拒否する回帰修正

変更前candidateは `7f531caf7552480e61fa329c8fb5c0ea7a7809aa`。旧 `test_scope_lifecycle_commands_vnext.py::test_scope_close_current_rejects_selection_change_during_prompt` を全文確認し、旧dispatcherの失敗だけを仕様廃止と見なさず、公開mainの実processへ保証を移した。Scope close/reopenの業務は維持対象であり、D-09の公開前の楽観的比較とCLIの明示確認/expect-currentを適用する。Finishの「捕捉した選択だけ解除」という別契約は変更しない。

試験では実Gitの同じWTに二つのGH-backed Initiativeを置く。Scope #1への端末確認を表示したまま、別の実CLI processでScope #2を `work start --branch main --switch-active` し、その後元の確認へyesを送る。対象と選択をfixtureだけで途中差替えせず、現行Startそのものを通す。

最初のClose試験は1 failed（1.34秒）。元processはexit0/succeededとなり、旧#1へのGitHub PATCHを送った。利用者が確認中に直接選択が変わったことを変更前に検出できていない、意味のある製品Redである。collection/旧Namespace/環境故障とは区別する。

修正はterminal確認を必要とするScope lifecycleのverify_sourceへ、自WTの捕捉済みselection status/record/handleと再読取結果の比較を追加する八行。比較失敗ならexit3とselection changed診断でremote送信前に停止する。共通Start lock、writer lease、権限・ACL、journal、別WTの状態変更は追加しない。--yesによる既存の直接実行とFinishの解除方針も変更しない。

同じClose試験は1 passed（1.31秒）。次にClose/Reopenの二casesへ展開して2 passed（2.31秒）を確認した。両方で旧remote状態・全metadata・新しい#2記録が保持され、PATCHは一回も送られなかった。既存のScope lifecycle/Finish/active/別WT writer suiteは修正後90 passed（20.90秒）。これはmacOSの実Git/PTY/processとhermetic ghの証拠で、live GitHub・Windows native・全件gate・独立Strict合格ではない。
