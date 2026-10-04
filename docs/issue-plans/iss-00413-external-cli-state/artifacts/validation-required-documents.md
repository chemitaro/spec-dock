# Validateの必須Scope文書検査を維持する

基準は `1510e37bed521759b224d4631caad5d411e5f162`。旧 `application/artifact_preflight.py` と `application/validate_tree.py`、`tests/unit/application/test_validate.py` を全文確認した。既存の三階層それぞれが `requirement.md`、`design.md`、`plan.md`、`report.md` を持つ構造検査が、現行の `workspace_structure.inspect_structure` には接続されていなかった。[D-11](../design.md#d-11) / C-01の既存構造検査を維持する修正であり、本文・承認・計画レベルの新しいgateではない。このunitで旧validate graphやそのテストは削除しない。

## 実装

- `infra/scope_documents.py` はguarded directory descriptorから四文書の名前と通常fileであることだけを検査する。本文は開かず、書込み・Start lock・権限変更をしない。最後にowner directoryの物理identityを再検査する。
- `application/workspace_structure.py` から欠落・非通常fileを `REQUIRED_DOCUMENT_INVALID` として返す。scope_idとrepo-relative pathを示し、本文やリンク先は出力しない。Validate、Doctor、明示移行前の構造検査で共通利用する。
- `infra/committed_validation.py` は捕捉したHEADの四文書entryを内容なしのplaceholderとして構成する。metadata以外のblob本文をGitから取得しない。未commit文書で欠落したHEADを補完しない。
- `.meta.json` の欠落/不正は既存Scope tree readerが引き続き拒否する。
- CLI helpと配布するreference_sync.mdへ検査内容を明記し、static inventoryは該当する一行の現hashと既知旧hashだけを更新する。歴史資料のhash/pathは保持する。

## テストとfixture

公開CLIで三階層×四文書×working/HEADの24ケース、directory/symlinkへの置換4ケース、空report・不正UTF-8のdesign・過去の承認/assurance情報を判断しない2ケースを検査した。Path.openの本文読取trap、既存のcat-file取得対象制限、GitHub/Start lockの非取得検査とtree保全を用いる。

共有make_workspace/add_scope fixtureを従来の完全なScope構造へ揃えた。空Scopeを作る三fixtureは四文書も明示削除する。240件の移行fixtureには不足した文書を追加し、既存requirement本文とmetadata bytesを保全する。削除競合の三テストは、追加された文書に応じてchanged/remaining/effectの正確な一覧を更新し、未削除文書とbackupのbytes一致も検査する。期待値の訂正を製品Redとは数えない。

## 実測

| 検査 | 実結果 |
|---|---|
| 修正前の限定30ケース | 28 failed / 2 passed / 50 deselected、4.40秒、exit1。欠落/非通常fileをvalidとして返すことをassertionで再現 |
| 同じ30ケースの修正後 | 30 passed / 50 deselected、4.44秒、exit0 |
| 関連八suiteの初回 | 271 passed / 1 failed、123.21秒、exit1。240件fixtureの文書不足を検出 |
| 通常全pytestの初回 | 1863 passed / 3 failed / 1 skipped、355.05秒、exit1。三件は増えた文書に伴う削除途中の一覧期待値 |
| 三削除fixtureと240件移行の再確認 | 4 passed / 72 deselected、4.22秒、exit0 |
| Validate / Scope Deleteの全二suite | 117 passed、16.52秒、exit0 |
| 変更10 Python filesの限定mypy | MYPYPATH=src / --follow-imports=silent、exit0 |
| 通常make lint | Ruff check/format成功（311 files）。mypy 32 errors / 11旧source files（230 source files）、make exit2 |

mypyの最初の限定実行で本文trap callbackのoverload不一致一件を検出し、元Path.openと同じ引数を明示して修正した。type ignoreや収集除外を増やしていない。全pytestのskipは旧binary publisherのLinux O_TMPFILE capability testであり、Darwin上の未実行をpassへ変えない。修正後の通常全pytestはまだ再実行しておらず、117件の成功を通常full gate合格としない。

実行環境はDarwin 27.0.0 / arm64 / Python 3.12.11。native mount出力でsource checkoutの `/Volumes/990p2t` がAPFSであることを確認した。最初のdiskutil cwd probeはexit1でFSを確認できなかった。Linux/Windowsや別Pythonでの受入証拠ではない。

元logsは既存Epic Workbenchの `iss-00413-implementation/pytest-required-documents-{red,green,related,full,fixtures,validation-delete}.log` と `lint-required-documents.log` に保持する。通常full gates、残る旧graphの退役、Windows adapter/native、Python 3.10/3.11、fresh Strict、最終手動確認は継続する。実consumerのmetadata/stateとlive GitHubは未変更。
