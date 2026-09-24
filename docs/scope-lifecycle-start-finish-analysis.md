# Initiative・Epic・Issue 共通の Start / Finish 設計検討

状態: 検討用。現行仕様の変更決定や実装完了を示す文書ではない。

## 目的

Initiative、Epic、Issue のどの階層でも、対象を active にして `<id>-<slug>` の作業ブランチを作成・checkout できる Start と、対象の作業を終了する Finish を提供する。現在の `issue start` / `issue finish` のコマンド体系も見直す。

## 現行実装で確認した事実

| 領域 | 現状 | 根拠 |
| --- | --- | --- |
| CLI | `issue start <target>` と引数なしの `issue finish` がある。`active set/show/clear` は別のコマンド群。 | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`, `commands/issue.py` |
| Start の対象 | `issue_start` は `requested.kind != "issue"` を拒否する。 | `application/issue_lifecycle.py` |
| Start の流れ | 既存 active Issue の未完了ガード、GitHub を使う依存判定、checkout、active 設定、post-sync の順。`--force` は未完了 active Issue ガードのみを迂回する。 | `application/issue_lifecycle.py` |
| ブランチ | 共通の `checkout_active_target` と `resolve_branch_decision` は node kind を限定していない。候補は `<id>-<slug>`、非 ASCII または不正 ref では `<id>`。既存ブランチは再利用する。 | `application/set_active.py`, `domain/active.py`, `docs/reference_naming.md` |
| Active | `select_active_chain` は対象の祖先を含め、対象より下位の選択を空にする。`active set` は checkout や依存判定をしない。`active clear` は全階層を解除する。 | `domain/tree.py`, `application/set_active.py` |
| Finish | active Issue を `close_node` で GitHub 上 Close または既存 Close と確認した後、全 active を解除して post-sync する。`close_node` 自体は三階層を受け付けるが、GitHub Issue に紐付かない node は拒否する。 | `application/issue_lifecycle.py`, `application/close_node.py` |
| 依存 | `deps check` は Initiative / Epic / Issue を対象にできる。readiness には子 Issue や node 依存の状態が関係する。 | `application/check_deps.py`, `domain/deps.py` |

## 設計で決める事項

1. **CLI の主語**: `issue start/finish` を `start/finish` のような階層共通コマンドへ移すか、`initiative|epic|issue start/finish` に拡張するか。現行コマンドの互換期間とエラー案内も決める。
2. **Start の対象解決とブランチ**: node ID と GitHub Issue 番号の指定をどう保ち、既存ブランチの再利用・異なる worktree での checkout 衝突・checkout 後の active 書き込み失敗をどう扱うか。
3. **Active の競合**: Issue が active のまま親 Epic / Initiative や別の sibling を Start する場合、どの未完了作業を保護するか。`--force` の適用範囲を明確にする。
4. **依存 readiness**: Epic / Initiative の計画作業を始める際、子 Issue の未完了や未解決依存まで Start を妨げるべきか。`deps check` の対象別意味を確認する。
5. **Finish の意味**: GitHub Issue の Close と active 終了を一体とするか。子 Issue が未完了でも親を Finish できるか。親を残して active をどの階層まで解除するか。ブランチの checkout・削除・マージを行うか。
6. **履歴と導入**: provider 側の CLI・use case・契約・表示・テスト・出荷ドキュメントをどう移行し、既存の dogfooding workspace と導入済み consumer にどう反映するか。

## 分析の出力条件

- 推奨する CLI 形と互換方針を、代替案と具体例で示す。
- Initiative / Epic / Issue それぞれの Start / Finish 契約を、active chain、branch、依存、GitHub Close、失敗時の部分的副作用まで定義する。
- 判断が必要な Product / Policy 上の選択を、技術上確定している事項と分ける。
- provider 側の変更箇所、必要な回帰テスト、段階的な実装順を提示する。
