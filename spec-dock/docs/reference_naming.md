# 命名と識別子（Current）

Scope IDは `init-`、`epic-`、`iss-` で種別を表し、GitHub backendはIssue番号、local backendは `local-` を含む連番を使います。作成時のtitle/slugの制約と実際の割当結果は `scope create KIND --help` と返却されたIDで確認します。IDやArtifact pathを手で推測してmetadataを編集しないでください。

branchはScope IDとtitleから決定的な名前を割り当て、branch対応を記録します。`work start` で新しい対応branchを作るときは `--base REF` が必須です。既存の対応branchを再開するときは `--base` を渡せません。`branch create TARGET --base REF` はcheckoutせずに対応を作ります。`branch switch TARGET` は選択を変えずにcheckoutします。`--branch NAME` は明示した名前の検査後だけ使用します。

Artifactは `artifact create --scope TARGET --type TYPE --title TITLE` が生成した識別子・pathを使います。`artifact import file PATH --scope TARGET` は一件のregular fileをopaque evidenceとして保存します。正本に採用した内容はRequirement、Design、Planまたはaccepted ADRへ明示的に反映します。過去版の詳細な命名規約は[historical](historical/reference_naming.md)です。
