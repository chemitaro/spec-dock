# GitHubの旧マーカー検索の退役

採用済み [D-09](../design.md#d-09) と [旧Scope発行の移行対応](test-port-scope-github-retirement.md) に従う。読取基準は `d7f47fc029d26be462d091e5fd5ad59af3ae1456`。

## 変更と保全

`GithubIssueGateway.find_by_marker` の呼び出し元は、直前unitで廃止したjournal付きScope writerと二つの旧private試験だけだった。source/testsの全文検索とASTを確認し、gatewayからこのmethod、全Issueページの走査、operation marker照合を削除した。marker作成・検索や送信意図の復元を現行writerへ移さない。

このmethod専用のarray decoder optionを削除し、GET/POST/PATCHの応答を単一Issue objectへ限定した。無効arrayはGETで確定失敗/5、createで不明/6となり、再送やID生成を行わない。dictの返値型が確定するためget/createのcastも不要になった。

`RemoteIssueError`、repository検証、`_record`、gateway初期化、`set_state` のASTは元HEADと同じ。元の残る13 test関数のASTも同じ。HTTPの確定拒否・timeout・PR・foreign identity・完了理由の区別、最小POST/PATCH payload、PATCH後の確認GETを保全する。

## 旧試験の扱い

| 旧test関数 | 判断と後継 |
|---|---|
| test_marker_scan_reads_all_pages_and_excludes_pull_requests | markerによる全Issue探索は採用仕様で廃止。単一IssueのPR/foreign/番号検証はtest_get_rejects_pull_requests_foreign_repository_and_numberへ維持。createの不明・一POSTは公開test_unknown_create_response_keeps_scope_unpublished_and_never_retries_postで維持 |
| test_marker_scan_rejects_incomplete_page | ページ走査機能だけを廃止。不正JSON形状の拒否は新test_issue_operations_reject_array_responses_without_scanning_or_retryingでGET/createの確定/不明を区別 |

新しい保証確認は旧sourceで先に2 passed（0.03秒）、refactor後の同testも2 passed（0.03秒）。既存Greenのcharacterization/refactorであり、製品Redではない。最初のPOST endpointをargv末尾（--input -）と比較したfixture期待誤りは1 passed/1 failed（0.04秒）で、--methodに続くendpointを確認するよう訂正した。元logを保持する。

## 実測と残件

- gateway・Scope create/import・公開adapter・Scope Close/Reopenの七suite：131 passed、40.62秒。
- work finish公開suite：33 passed、11.93秒。
- 全source/tests Ruff check/format：347 filesで成功。
- 変更source/test限定mypy `--follow-imports=silent`、diff check、上記AST同一性の検査：成功。
- source/runtimeとtestsでfind_by_marker / expect_array / spec-dock-operation marker参照0。pytest skipや収集除外は増やさない。

元logは既存Epic Workbenchの `iss-00413-implementation/pytest-github-marker-retirement-{before,after,related}.log` に保持する。

このunit前のclean d7f47fc0の通常make lintはRuff成功・mypy 55 errors/19 files（266 source files）、source 40/test 15 errors、make exit2で未合格。元logは `iss-00413-implementation/lint-p12-d7f47fc0.log`。旧95 errorsのsnapshotとは別である。残る旧private helpers、通常full gates、native OS/別Python、fresh Strict、最終手動確認を継続する。実consumer/live GitHubは変更しない。
