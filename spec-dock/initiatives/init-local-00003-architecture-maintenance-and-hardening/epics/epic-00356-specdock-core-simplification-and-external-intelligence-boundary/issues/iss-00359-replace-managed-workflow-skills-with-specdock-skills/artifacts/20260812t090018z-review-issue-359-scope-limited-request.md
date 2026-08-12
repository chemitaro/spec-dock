---

種別: 限定レビュープロンプト（Issue）
ID: "iss-00359"
タイトル: "Issue 359 P0/P1 Implementation-Readiness Review"
関連GitHub: ["#359"]
状態: "draft"
作成者: "ChatGPT-use-strict / main orchestrator"
最終更新: "2026-08-12"
依存: ["requirement.md", "design.md", "plan.md", "companion.md"]
親: ["epic-00356", "init-local-00003"]
---
# Issue 359限定レビュー依頼

## 1. Review source

次のsourceをexactに確認してからレビューすること。

* Repository: `chemitaro/spec-dock`
* Branch: `iss-00359-replace-managed-workflow-skills-with-specdock-skills`
* Full SHA: `8e10f255b3377bf879b459380f563729522e22b2`
* Issue: `iss-00359`
* GitHub Issue: `#359`

repository、branch、full SHAのいずれかを確認できない、または一致しない場合は、内容レビューを行わず`information_insufficient`とする。default branchや別branchへfallbackしない。

## 2. Review target

* `requirement.md`
* `design.md`
* `plan.md`
* `companion.md`
* `review-request.md`
* 上記が参照するexact commit上のprovider asset、dogfood projection、Current CLI、Artifact template、Codex config、installer mapping、関連test

scopeと受け入れ条件の正本は`requirement.md`とする。

skill責務、CLI分類、write boundary、provider / dogfood構造、additive materialization、`developer_instructions`変更境界の正本は`design.md`とする。

対象file、実装順序、test、完了条件、legacy inventoryの正本は`plan.md`とする。

## 3. Reviewer role

あなたはIssue #359の実装開始可否だけを判定するread-only reviewerである。

次を行う。

* exact commitの実在path、command、option、template、inventory、installer mappingとの整合を確認する
* Issue #359内の矛盾、欠落、実装不能、安全問題を確認する
* findingがある場合、exact locationと最小修正を示す
* requirement / design / plan間の責務混在を確認する
* Issue #360または親Epicの責務がIssue #359へ昇格していないことを確認する
* provider asset追加のCurrentな機械的波及が隠されていないことを確認する
* additive materializationとTarget inventory cutoverが区別されていることを確認する

次を行わない。

* repository mutation
* source、test、文書の直接修正
* 新機能、追加workflow、追加運用、追加証跡の提案
* review pass、IC-2 pass、実装完了の自己宣言
* P2 / P3 findingのR/D/Pまたはcompanionへの統合提案

## 4. 固定severity基準

### P0

Issue #359を安全に実装できず、データ破損、scope逸脱、誤ったsourceへの実装につながるblocker。

例:

* repository / branch / SHA不一致
* canonical文書、metadata、Git、GitHubを自動変更する契約
* zero-writeまたはexactly-one Artifactと両立しない処理
* external capabilityへcredentialまたはrepository writeを許す契約
* provider authorityとdogfood projectionの向きが逆
* Issue #360が所有するprune / consumer migrationをIssue #359で実行する計画

### P1

Issue #359の固定scope内で、実装または主要testを開始できない矛盾・欠落。

例:

* 二つのskillの責務が区別されていない
* Current CLI operationの分類が欠落または実装と矛盾する
* 存在しない`doctor --github`を前提としている
* bare `doctor`と、`--github-repo`、`--github-pr`、`--github-head-sha`、optional `--github-extended`を使うexternal診断が区別されていない
* grillが明示selectorなしでactive targetへfallbackできる
* `--initiative`、`--epic`、`--issue`の排他的selector契約が欠落している
* explicit routeまたはtitleが未定義
* bootstrap preflight、zero-write、exactly-one、partial recoveryのいずれかが欠落
* 四routeのpositive testまたは主要negative testが実行不能
* provider / dogfood parity対象が不明
* `install_root`の全file mappingによるadditive materializationを無視している
* additive materializationを理由にprovider assetをIssue #359から削除している
* additive materializationとTarget inventory cutover、prune、consumer migrationを混同している
* `_MANAGED_SKILL_NAMES`、`_LEGACY_MANAGED_SKILL_NAMES`、installer logic、obsolete inventoryをIssue #359で変更する計画になっている
* `developer_instructions`の削除対象と保持対象が区別されていない
* legacy inventoryまたはIC-2責務境界が欠落
* 存在しないpath、command、option、host metadataを前提としている

### P2 / P3

実装開始を妨げない文面、可読性、将来改善、追加test、追加証跡、運用上の提案。

P2 / P3は修正不要であり、R/D/P/companionへの統合を提案しない。出力では件数だけを示し、詳細を列挙しない。

## 5. 禁止事項

`requirement.md`の対象外をIssue #359へ取り込まない。

特に次を提案しない。

* canonical R/D/P Front Matter migration
* planning validatorまたはplanning create-path修復
* A/B/C commit運用
* durable CI artifact、retention、rehash
* 33シナリオの長期証跡
* full Git control-state snapshot
* Target managed inventoryのcutover
* fresh / update / uninstall consumer matrix
* installed matrix、publication、migration
* Issue #360後のrollback
* Epic運用
* installer logicの変更
* managed / legacy managed skill定数の変更
* 旧skillのprune
* その他のexternal skillのmanaged asset化
* 新しいquality gate
* P2 / P3由来の追加受け入れ条件またはtest

canonical形式上の問題を発見した場合、Issue #359の外部前提として一行で示し、product requirementまたは実装stepへ昇格させない。

## 6. 判定規則

* P0またはP1が一件でもあれば`fail`
* P0 / P1がなく、source確認が完了していれば`pass`
* sourceまたは必要事実を確認できなければ`information_insufficient`
* P2 / P3だけでは`fail`にしない
* findingはIssue #359内で必要な最小修正だけを示す
* provider assetとdogfood projectionはIssue #359の固定scopeとして扱う
* Current mappingによるadditive materialization自体をIssue #360へのscope移動理由にしない
* Target inventory cutover、prune、consumer migrationはIssue #360の責務として扱う
* IC-2のpass / failは本レビューで判定しない

## 7. 出力形式

次の形式だけを返すこと。

```markdown
## Verdict

pass | fail | information_insufficient

## Source verification

- repository: verified | unverified
- branch: verified | unverified
- full SHA: verified | mismatch | unverified

## Blocking findings

- none

または

- [P0|P1] `<file>:<section>` — `<確認した矛盾・欠落・安全問題>` — Required correction: `<Issue 359内の最小修正>`

## Scope guard

- out-of-scope responsibility promoted into Issue 359: yes | no
- Issue 360 responsibility promoted into Issue 359: yes | no
- provider asset incorrectly removed from Issue 359: yes | no
- additive materialization hidden or misclassified: yes | no
- managed inventory or installer logic changed in Issue 359: yes | no
- IC-2 pass self-declared: yes | no
- invented path, command, or option found: yes | no

## Non-blockers

- P2 count: <number>
- P3 count: <number>
- integration requested: no
```

`Blocking findings`が`none`の場合、追加提案、将来改善、称賛、要約を付けないこと。
