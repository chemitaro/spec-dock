# macOS全件試験のreadonly比較不一致

対象はclean候補 `8a70a8b30e69fe0bda6db6c45ef555f44411236d`。通常 `uv run pytest -q --tb=short -ra` は1 failed / 1847 passed / 2 skipped、479.73秒、exit 1だった。失敗を成功へ書き替えず、全件ログ `pytest-macos-full-8a70a8b3.log` を保持した。

## 失敗した観測

`test_validation_checks_committed_dependency_and_parent_structure[False-dependency]`。公開 `workspace validate --json` は期待したexit 7、`DEPENDENCY_INVALID` finding、effects=[]を返したが、fixture全体の`tree_digest`が不一致だった。

- before: `sha256:6fa1bfb48cb41acb171fd814c28c08e24b7ee14ae0b9a784b1d71878f4d0d90e`
- after: `sha256:12e60337118f7468a0646c6131a178872dc9b15a7f7a78a311c46e80b2c4059e`

元fixtureを読取り確認すると `.git/objects/pack/` にpack、index、reverse index、multi-pack-indexがあり、`.git/info/refs`・`objects/info/packs`の更新もあった。他の同じ六caseはloose objectsだった。元fixtureを保全したowned copyのdigestは上記afterと一致した。owned copyでobject表現を戻す調査はbeforeを復元できず、原因の証明には採用していない。

Gitには自動・backgroundのmaintenance機構がある（[Git GC公式文書](https://git-scm.com/docs/git-gc)、[Git maintenance公式文書](https://git-scm.com/docs/git-maintenance)）。しかし、今回は実行者・発火条件を捕捉していない。外部repack、CLIの書き込み、別の原因のどれかを断定しない。

## 再確認と次の診断

1. 独立した40の新しいGitHub-backed fixtureに同じ不正依存をcommitし、同じ公開CLIの前後で全entryのtype/mode/hashとdigestを比較。40/40無変更、exit 7。`validation-tree-diagnostic-8a70a8b3.log`。
2. 既存のdigest assertionを残し、独立したfile mode/bytesの辞書比較を追加。再発時にはhashだけでなく変更pathがpytest差分に出る。skipや例外許可を増やさず、製品sourceは変更していない。
3. validation suiteは80 passed、12.70秒、exit 0。`pytest-macos-validation-readonly-diagnostic.log`。通常lintもexit 0。

以上は再確認の証拠であり、根本原因の修正完了ではない。診断を含むclean候補で通常全件試験を再実行し、不一致が再発すれば実際の変更entryとprocess境界を特定する。`.git`を比較対象から除外したり、合格するまで結果を破棄したりしない。
