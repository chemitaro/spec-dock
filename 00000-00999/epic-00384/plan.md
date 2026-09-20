---
種別: 実装計画書（Epic）
ID: "epic-00384"
タイトル: "固定ディレクトリ再配置と検証の簡素化"
状態: "approved"
最終更新: "2026-09-20"
---

# Epic #384 — 再構成の実施計画

## 現在の実施状況

### 主要移行

固定6ディレクトリの置換方式への主要移行はIssue #396 / [PR #404](https://github.com/chemitaro/spec-dock/pull/404)で実施し、2026-09-19にmainへmerge済みです。merge commitは `400846141a946f7cb98de20d1f40361b8a238f10` です。この移行は履歴として扱い、Epic Requirement R1〜R10およびaccepted ADRは変更しません。

### 最終cleanup — Issue #405

2026-09-20のユーザー指示で作成・開始したIssue #405 `Directory Replacement Final Cleanup` は、主要移行後に残るprovider実装、test/harness、current docsのcleanupを担当します。#405の承認済みRequirement/Design/Planが実装authorityです。

| #405単位 | 状態 | 実測・残作業 |
|---|---|---|
| S0〜S3 runtime boundary | 完了 | runtime `686 passed, 24 skipped`、application/artifact `283 passed, 6 skipped`、`make lint`成功。S1〜S3候補 `f77f6f7163430d6e5f1142eec7b8f07440e259f6` はGPT-5.6 Sol Extra High Strict code review `pass`、findings 0、confidence 0.94。 |
| S4〜S5 installer/test cleanup・docs/dogfood・本Plan/Report | local verification・Strict review完了 | directory installation `11 passed`、distribution cutover `8 passed`、runtime handoff/worktree safety `9 passed`、同期後 `test_init_update.py` `58 passed`。mid-copy failure successorは現行ProductでGreen (`covered-existing`) のためinstaller sourceは変更なし。保護pathのsync前後差分は0、current-doc obsolete guarantee scanは0件。candidate `0ab3ab341cf734a032042c9beebb0fb2dba94125`のGPT-5.6 Sol Extra High Strict reviewは`pass`、findings 0、confidence 0.97。 |
| S6 integrated local qualification | 完了（local） | candidate `0d9114b038ddb78dab32bc6039b51c4d02943846`でfocused `141 passed`、full `1551 passed, 25 skipped`、`make lint`、sdist/wheel build、distribution integration `11 passed`、parity `10 passed`、SpecDock validate `nodes=237`を実測。skip理由とraw logsはIssue Reportに記録。 |
| S7 delivery gate | 進行中 | PR #406、Ubuntu/macOSを含む全PR checks、およびfresh integrated Strict reviewはcandidate `11825a335b628b195cb61ddd47abe8aaab9cfd88`でpass。Issue/Epic Reportへ実測を記録済み。final Report SHAでの必須test sequenceとFinal Quality Gate Strict v2は未実施。人間mergeは未実施。 |

S4〜S5はIssue Planどおり一つのcheckpointで完了し、candidate `0ab3ab...4125`を対象にStrict reviewを通過しました。S6のローカル実測はcandidate `0d9114...3846`に結び付きます。初回S6試行でRuff format/checkが失敗したため、test/fixture 5ファイルだけにformat-only修正を行い、新candidateで正規sequence全体を再実行しました。S7ではPR #406の必須checksとGPT-5.6 Sol Extra High integrated reviewがReport証拠更新候補`11825a335b628b195cb61ddd47abe8aaab9cfd88`でpassしました。Final Quality Gate Strict v2と、その最終候補での必須テストは未完了のため、merge-ready扱いしません。現在状態と測定詳細はIssue #405 Reportを参照してください。Issue #405のRequirement、Design、accepted ADR、historical artifactsは変更対象ではありません。

## 実施規律

- 仕様レビュー、unit review、Final Quality Gateはそれぞれレビュー対象SHAと実行証拠を固定し、過去候補のpassを流用しません。
- unit reviewはGPT-5.6 Sol Extra High、Final Quality Gate Strict v2はGPT-5.6 Sol Proを使用し、実際のUI選択を記録します。
- 失敗テストは撤去対象の旧契約か、維持する機能の回帰かを分類します。KEEP契約の回帰を削除、skip、弱化して通しません。
- provider assetsを先に変更し、dogfoodを指定CLIで同期します。`spec-dock/initiatives`はsync前後で不変であることを確認してから、親Epic `plan.md` / `report.md`だけを意図して更新します。
- checkpointごとのcommitと通常push後、fresh Strict reviewを行います。Issue #405のmergeは人間のgateに従います。

## Historical appendix: Issue #396以前の実施単位

以下は旧実施計画のU0〜U3です。状態表現は当時の計画スナップショットであり、現在の進捗 authority ではありません。上のIssue #405 S0〜S7表がcurrent sequenceです。

| 旧単位 | 当時の内容 | 当時の完了証拠・状態 |
|---|---|---|
| U0 | Epic/IssueのR/D/Pを再構成し、旧契約を履歴へ移す | validate、差分確認、checkpoint。完了（ec58f902） |
| U1 | 小さいinstallerとruntime起動へ切替、旧lifecycleを撤去 | 置換・データ不変・失敗再実行テスト、runtime smoke。旧表現: 実装済み・統合検証中 |
| U2 | provider認証の残consumerと旧テスト/policy/CIを撤去 | collection、通常pytest、lint、package smoke。旧表現: 実装済み・統合検証中 |
| U3 | 配布docsとdogfood同期、現行参照・PR整備 | 保護データ不変、validate、Strictレビュー、最終品質確認。旧表現: 未実施 |

旧計画は、動作を保つまとまりでcommitし、汎用frameworkを追加しない方針でした。Issue #405ではその基礎方針を継承し、最終cleanupを明示的なIssueへ分離しています。

Issue #395から#392へのclose-based metadata dependencyはCLIで除去し、#396から#395への依存は当時の親計画どおり維持しました。Issue lifecycle・dependency契約およびIssue状態は本更新で変更しません。
