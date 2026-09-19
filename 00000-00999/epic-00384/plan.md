---
種別: 実装計画書（Epic）
ID: "epic-00384"
タイトル: "固定ディレクトリ再配置と検証の簡素化"
状態: "approved"
最終更新: "2026-09-19"
---

# Epic #384 — 再構成の実施計画

2026-09-19の明示指示を変更承認とする。現在のIssue #396ブランチで進め、新しいworktreeを作らない。実装前の基点は `851020134f460373adf00453798c49f163b08f8d`。

| 単位 | 内容 | 完了証拠 | 状態 |
|---|---|---|---|
| U0 | Epic/IssueのR/D/Pを再構成、旧契約を履歴へ | validate、差分確認、checkpoint | 作業中 |
| U1 | 小さいinstallerとruntime起動へ切替、旧lifecycle撤去 | 置換・データ不変・失敗再実行テスト、runtime smoke | 未実施 |
| U2 | provider認証の残consumerと旧テスト/policy/CIを撤去 | 全collection、通常pytest、lint、package smoke | 未実施 |
| U3 | 配布docsとdogfood同期、現行参照・PR整備 | 保護データ不変、validate、Strictレビュー、最終品質確認 | 未実施 |

単位は動作を保つまとまりでcommitする。失敗したテストを無条件に削除せず、撤去した保証のテストか、残す機能の回帰かを分類する。前者は削除し、後者は修正して検証する。チェックのためだけに新たな汎用frameworkを追加しない。

レビューは仕様差分とコード差分の新しい基点に対して行う。ChatGPTの通常コードレビューはGPT-5.6 Extra High、複雑な分析と最終品質確認はGPT-5.6 Pro。ラッパーを使用し、手動ブラウザ操作は復旧時に限る。旧レビュー合格は流用しない。

提出先はEpic統合ブランチ。Agentはmerge-ready PRで停止し、人間がmergeする。旧B3/B4性能認証は廃止し、マージ後は通常CIと動作確認を証拠とする。mainのマージも人間が行う。
