---
種別: 実装計画書（Issue）
ID: "iss-00396"
タイトル: "固定ディレクトリ再配置への実装切替"
状態: "approved"
最終更新: "2026-09-19"
---

# Issue #396 — 実施計画

2026-09-19の明示指示を変更承認とする。現在のIssue #396ブランチで進め、新しいworktreeを作らない。実装前の基点は `851020134f460373adf00453798c49f163b08f8d`。

| 単位 | 内容 | 完了証拠 | 状態 |
|---|---|---|---|
| U0 | Epic/IssueのR/D/Pを再構成、旧契約を履歴へ | validate、差分確認、checkpoint | 完了（ec58f902） |
| U1 | 小さいinstallerとruntime起動へ切替、旧lifecycle撤去 | 置換・データ不変・失敗再実行テスト、runtime smoke | 実装・重点検証完了、全試験・レビュー待ち |
| U2 | provider認証の残consumerと旧テスト/policy/CIを撤去 | 全collection、通常pytest、lint、package smoke | 実装・重点検証完了、全試験・レビュー待ち |
| U3 | 配布docsとdogfood同期、現行参照・PR整備 | 保護データ不変、validate、Strictレビュー、最終品質確認 | 同期・文書更新済み、レビュー待ち |

単位は動作を保つまとまりでcommitする。失敗したテストを無条件に削除せず、撤去した保証のテストか、残す機能の回帰かを分類する。前者は削除し、後者は修正して検証する。チェックのためだけに新たな汎用frameworkを追加しない。

レビューは仕様差分とコード差分の新しい基点に対して行う。ChatGPTの通常コードレビューはGPT-5.6 Extra High、複雑な分析と最終品質確認はGPT-5.6 Pro。ラッパーを使用し、手動ブラウザ操作は復旧時に限る。旧レビュー合格は流用しない。

提出先はEpic統合ブランチ。Agentはmerge-ready PRで停止し、人間がmergeする。旧B3/B4性能認証は廃止し、マージ後は通常CIと動作確認を証拠とする。mainのマージも人間が行う。

## 現在の検証記録

旧構成撤去後の初回通常pytestは1544 passed / 25 skipped / 2 failed。失敗は旧clean必須のbuild receiptと、廃止workflow seedを要求する文書テスト。両方を新契約へ更新した。最終候補の全試験・Strictレビューは別途実行し、完了を先書きしない。

#395は修正済みの履歴として参照する。OPEN維持による開始ブロックを撤去するため、#396から#395へのmetadata依存をCLIで除去した。IssueのOPEN/CLOSED状態は変更していない。

重点検証: installer/package 10 passed、runtime/Git/handoff 66 passed、配布文書・cutover 204 passed。make lint（ruff/mypy）とvalidate（236 nodes）は成功。U1/U2は起動経路と旧認証撤去が不可分のため同じcheckpointにまとめる。

再レビューで初回init失敗とupdate再試行の範囲が曖昧と判定された。ユーザーの「個別ファイル管理を不要にし、要件設計自体を削ぎ落とす」という本タスクの変更権限に基づき、R8を6ディレクトリのupdateに限定した。初回失敗は不完全ディレクトリを利用者が保全してfresh initをやり直す。状態判定・seed修復の実装は追加しない。これは外部分析の推奨Aを、元の明示指示に照合して主担当が採用した判断であり、別途のユーザー承認を得たという記録ではない。
