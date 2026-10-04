# 命名と識別子（Current）

Scope IDはGitHub番号にkind prefix `init-`、`epic-`、`iss-` を付けたものです。既存metadataのID/親/番号/refを保持し、新規ScopeにUUIDやlocal連番を追加しません。create/importのIDとcanonical pathを使い、metadataを手で作りません。

branchの既定名はIDとmetadataのslugから決め、独自対応台帳は保存しません。新規Startは--base REFが必要です。既存branchの再開は--branch NAMEを明示し、--baseを渡しません。branch create/show/switchの--nameとStartの--branchはGitで検証します。同一branchの同時checkoutはGitが、別branchの同一Scope重複はStartの観測・短い排他が防ぎます。

直接作業記録のtokenは捕捉した一fileの識別用です。Scope identity、GitHub番号、永続操作台帳ではありません。Finish/clearはその捕捉記録だけを解除し、後から始まった別対象を消しません。

ArtifactはCLIのID/pathを使います。createはtimestamp/type/title、import fileはtimestampと元basenameを基に一件のopaque fileを保存します。本文からauthorityを推測せず、採用内容をRequirement・Design・Planまたはaccepted ADRへ明示的に反映します。
