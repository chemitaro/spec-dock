# 旧Artifact composition adapterの退役

## 判断と確認範囲

RQ-413-02、D-03/D-11/D-12、P-12に従い、通常Artifact経路が使っていない `infra/artifact_ports.py` だけを退役する。全57行・四top-level symbolsを読み、全src/testsのASTで絶対・相対・子module・TYPE_CHECKING・literal import呼出しを確認した。候補外参照は0。src/tests/scripts/配布設定/CIの文字列検索でも、自身の関数と旧consumer静的inventoryの二項目以外に参照はなかった。inventoryの旧path/hashは過去資産を識別する証拠なので変更しない。

| 削除するsymbol | 理由と維持するもの |
|---|---|
| _NodeReader | 旧Portsへfs_repoを結ぶ未使用wrapper。現在のScope読取とfs_repoは保持 |
| _TemplateScaffolder | 旧Portsへtemplate_scaffolderを結ぶ未使用wrapper。現在のArtifactテンプレート処理は保持 |
| _Clock | 旧Portsへclockを結ぶ未使用wrapper。現在の作成日時・作成者の生成は保持 |
| artifact_ports | 旧PortsとFilesystemBinaryArtifactPublisherの未使用composition。現行direct_artifact/file_publicationを変更せず、別callerのあるpublisherとその試験も保持 |

このunitは既存Artifact公開・インポートの挙動変更ではない。test削除、assertion緩和、skip追加、型ignoreや収集除外は0。

## 実測と残り

- 通常wheelに旧adapterを収録しない回帰検査: **Red 1 failed、0.83秒、exit1 → Green 1 passed、17.35秒、exit0**。
- 公開Artifact、binary import ports、binary publisherの三suite: **105 passed、1 skipped、10.89秒、exit0**。skipは従来のLinux O_TMPFILE capability試験で、Darwin上のnative Linux成功ではない。
- 全source/testsのRuff check/format（306 files）、MYPYPATH=srcの変更test限定mypy、diff checkが成功。

元logsは既存Epic Workbenchの `iss-00413-implementation/pytest-artifact-adapter-retirement-{red,green,related}.log` に保持する。full lintの直近実測は前unitの30 errors/10旧filesであり、今回のfull成功を意味しない。c4c26bdbのLinux全件再検証は別の実行中候補で、このunitを含まない。残る旧source、Windows native、通常full gates、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは未変更。
