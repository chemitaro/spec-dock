---
種別: 実装計画書（Issue）
ID: "iss-00055"
タイトル: "Close Linked Github Issues From Specdock Command"
関連GitHub: ["#55"]
状態: "draft | approved"
作成者: "Codex CLI"
最終更新: "2026-04-09"
依存: ["requirement.md", "design.md"]
親: ["epic-00054", "init-local-00002"]
---

# iss-00055 Close Linked Github Issues From Specdock Command — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001
  - AC-002
- EC:
  - EC-001
  - EC-002
  - EC-003
- 制約:
  - remote close-only
  - non-cascade
  - no local delete
  - additive change

## マイルストーン一覧
- M1:
  - 対象:
    - close use case / gateway seam / result contract を固定する
  - exit:
    - target node resolve、already-closed success/no-op、read-after-close race normalization、no-linked-issue / gh-failure の verification seam が test で観測可能
- M2:
  - 対象:
    - command surface / CLI text / docs refresh / final validation を閉じる
  - exit:
    - `close` command の end-to-end 導線、docs contract、final diff review が pass

## 実装順序の根拠
- 依存関係の正本:
  - `design.md` の `依存関係分析` と module/dependency UML を参照する
- sequencing rule:
  - upstream / prerequisite / lower-dependency slice から先に step を組む
  - downstream / dependent slice は前提が固まってから置く
- step ordering notes:
  - S01 で application / infra seam を固定してからでないと、S02 の command surface が stable にならない
  - S02 は S01 の contract を使って parser / registry / bootstrap / CLI renderer をつなぐ
  - S90 は command contract が固まってから docs refresh を行う
  - S99 は docs / tests / report を含む最終差分でレビューする

## ステップ一覧
- S01:
  - 観測可能な振る舞い:
    - target node の linked GitHub issue を close-only で扱う application / infra seam が整い、already-closed / read-after-close race / no-linked-issue / gh-failure の振る舞いが test で観測できる
  - closes:
    - AC-001
    - EC-001
    - EC-002
    - EC-003
  - review gate:
    - RG1
    - QG1
    - SG1
- S02:
  - 観測可能な振る舞い:
    - top-level `close` command から target 指定で close を実行でき、CLI result と `sync --github` 確認導線が一貫する
  - closes:
    - AC-001
    - AC-002
    - 制約一式
  - review gate:
    - RG2
    - QG2
    - SG2

## 要件 ↔ ステップ対応
- AC-001 -> S01, S02
- AC-002 -> S02
- EC-001 -> S01
- EC-002 -> S01
- EC-003 -> S01
- 制約(remote close-only / non-cascade / no local delete / additive change) -> S01, S02

## レビュー / QA ゲート方針
- RG1 implementation review:
  - timing:
    - S01 完了後
  - scope:
    - close use case / gateway seam / result contract / seam tests
  - commit gate:
    - pass まで review loop を回し、pass 後に `report.md` を更新して差分確認後にコミットする
- QG1 QA review:
  - timing:
    - S01 完了後
  - scope:
    - already-closed / read-after-close race / no-linked-issue / gh-failure / non-cascade の test sufficiency
  - commit gate:
    - pass まで test loop を回し、pass 後に `report.md` を更新して差分確認後にコミットする
- SG1 spec review:
  - timing:
    - S01 完了後
  - scope:
    - requirement/design どおりに close-only seam が実装できる分割になっているか
  - commit gate:
    - pass まで review loop を回し、pass 後に `report.md` を更新してドキュメントだけをコミットする
- RG2 implementation review:
  - timing:
    - S02 完了後
  - scope:
    - parser / registry / bootstrap / CLI renderer / docs refresh / integration coverage
- QG2 QA review:
  - timing:
    - S02 完了後
  - scope:
    - command end-to-end、`sync --github` 確認導線、docs parity
- SG2 spec review:
  - timing:
    - S02 完了後
  - scope:
    - issue55 単体で close contract と success verification が閉じているか
  - commit gate:
    - pass まで review loop を回し、pass 後に `report.md` を更新してドキュメントだけをコミットする

## 実行ルール（全ステップ共通）
- plan 全体は実装着手前に承認する。
- cadence / approval policy は `workflow_issue.md` を正本とする。
- 互換参照: `Red → Green → Refactor → review → fix → re-review → report → commit/no-op`
- 各 step は 1 つの観測可能な振る舞いを単位とする。
- `block` は optional concern group。単純な step では最小 wrapper 1 個でよい。
- `iteration` は 1 回の TDD cycle とし、各 iteration は `Red → Green → Refactor` で閉じる。
- failing test は iteration ごとに 1 本ずつ進める。
- `Green` は最小実装、`Refactor` は green 維持を前提とする。
- shared minimum gate と scope-specific readiness contract / final exit contract を満たす。
- docs impact が `none` でなければ `S90` を実行する。
- 最後に `git diff <base>...HEAD` を対象に `S99 final diff review quality gate` を実施する。
- reviewer verdict は `report.md` に残す。
- 各 stage gate（SG/RG/QG）は `pass` まで回す。
- 各 stage gate の `pass` 後は、`report.md` を更新し、差分確認後に report とまとめてコミットする。
- no-op の場合のみ `report.md` に理由を残し、commit を省略できる。

## 実装ステップ

### S01 — close seam and state contract
- target:
  - application close use case
  - gateway seam
  - close-specific request/result contract
- design refs:
  - `design.md` の `依存関係分析`
  - `design.md` の `インターフェース契約`
  - `design.md` の `要件 → 設計マッピング`
- step boundary:
  - command parser / renderer / docs refresh は含めない
  - remote close-only seam と edge case handling を先に固定する

#### update_plan（着手時に登録）
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — contracts and use case
- purpose:
  - close operation を command surface から独立した seam として固定する
- files:
  - `application/contracts.py`
  - `application/ports.py`
  - `application/close_node.py`
  - `cli/bootstrap.py`
  - `infra/github_cli.py`

##### I1 — target resolve and no-linked-issue / gh-failure handling
- slice goal:
  - target node を解決し、linked issue 不在と gh failure を fail-fast で返す

###### Red
- failing test:
  - no-linked-issue error
  - gh failure leaves local tree unchanged
- expected failure:
  - close use case / gateway seam 未実装

###### Green
- minimum implementation:
  - close request/result / use case / gateway seam の最小実装
- pass condition:
  - no-linked-issue / gh-failure tests が通る

###### Refactor
- 目的:
  - Green を維持したまま、必要な範囲で構造や可読性を整える
- guardrail:
  - 振る舞いを変えない
  - この step の範囲を超えて広げない
  - 必要がなければスキップしてよい

##### I2 — already-closed success/no-op and read-after-close race normalization
- slice goal:
  - current snapshot を使った already-closed success/no-op と、close-after-read race の success/no-op 正規化を固定する

###### Red
- failing test:
  - already-closed returns success/no-op
  - read-after-close race returns success/no-op
  - non-cascade for epic / initiative target
- expected failure:
  - current-state pre-check、race normalization、result flag が未実装

###### Green
- minimum implementation:
  - `issue_view_snapshot` pre-check
  - `already_closed=True` result
  - close-after-read race を success/no-op に正規化
- pass condition:
  - already-closed / race / non-cascade tests が通る

###### Refactor
- 目的:
  - result model と close flow を簡潔に保つ
- guardrail:
  - target syntax と command surfaceを先取りしない

#### step gate
- review:
  - RG1 / SG1
- expected tests:
  - close use case / gateway seam tests
  - already-closed / read-after-close race / no-linked-issue / gh-failure / non-cascade tests
- report update:
  - reviewer verdict / test結果 / 修正内容 / no-op 理由を `./spec-dock/active/issue/report.md` に残す
- commit:
  - report 更新後に差分確認し、この stage の差分とまとめてコミットする

### S02 — close command end-to-end and confirmation path
- target:
  - top-level `close` command
  - CLI text
  - docs refresh
  - integration validation
- design refs:
  - `design.md` の `既存実装 / 規約の理解`
  - `design.md` の `インターフェース契約`
  - `design.md` の `テスト戦略`
- step boundary:
  - delete / subtree logic は含めない
  - issue55 単体の close contract と success verification までで閉じる

#### B1 — command surface wiring
- purpose:
  - parser / registry / bootstrap / command args / CLI renderer を接続する
- files:
  - `cli/parser.py`
  - `cli/registry.py`
  - `commands/close.py`
  - `presentation/cli_text.py`

##### I1 — close command success path
- slice goal:
  - top-level `close` command で target 指定 close が実行できる

###### Red
- failing test:
  - `close --id iss-00055`
  - `close --github-issue 55`
- expected failure:
  - parser / registry / renderer 未実装

###### Green
- minimum implementation:
  - close command wiring
  - success/no-op renderer
- pass condition:
  - command integration tests が通る

###### Refactor
- 目的:
  - target parsing の既存利用を明確に保つ
- guardrail:
  - active/deps の target parser を複製しない

#### B2 — docs impact and validation path
- purpose:
  - close 後の観測導線と close-only 境界を docs と tests に固定する
- files:
  - `spec-dock/docs/reference_github.md`
  - provider-side docs parity files
  - affected tests

##### I1 — sync confirmation path
- slice goal:
  - close 成功時も local state unchanged を保ち、explicit `sync --github` でのみ `done` を確認する導線を固定する

###### Red
- failing test:
  - close success leaves local docs/tree/generated state unchanged
  - docs/test mismatch for close confirmation path
- expected failure:
  - close command はあっても success-path verification と confirmation guidance が不足

###### Green
- minimum implementation:
  - docs refresh
  - integration assertion for success-path local-state-unchanged
  - integration assertion for post-close sync observation
- pass condition:
  - docs/test assertions が通る

###### Refactor
- 目的:
  - close-only wording と sync confirmation wording を揃える
- guardrail:
  - issue56 の delete contract を先取りしない

#### step gate
- review:
  - RG2 / SG2
- expected tests:
  - close command integration
  - success-path local-state-unchanged
  - post-close sync observation
  - docs parity assertions
- report update:
  - reviewer verdict / test結果 / 修正内容 / no-op 理由を `./spec-dock/active/issue/report.md` に残す
- commit:
  - report 更新後に差分確認し、この stage の差分とまとめてコミットする

### nested の使い方
- `step` は常に使う
- `block` は必要な時だけ分ける
- `iteration` は必要な数だけ並べる
- review / QA / docs / final diff は iteration の外に置く

### S90 — docs impact resolution / docs refresh
- 対象:
  - docs / assets / workflow
- 対応:
  - `reference_github.md` と provider-side parity docs に close command と close 後の `sync --github` 確認導線を反映する

### S99 — final diff review quality gate
- branch diff scope:
  - issue55 の close command / tests / docs refresh 一式
- required validation:
  - issue55 targeted test suite
  - `./spec-dock/scripts/spec-dock validate`
- reviewer approvals:
  - implementation review pass
  - QA review pass
  - spec review pass
- report update:
  - final diff review verdict / closing evidence / no-op 理由を `./spec-dock/active/issue/report.md` に残す
- commit expectation:
  - `report.md` 更新後に差分確認し、追加修正があれば最終コミットを作成する。無ければ直前 gate のコミットを最終成果として扱う

## 未確定事項
- なし:
  - issue55 は close-only command とその success verification までで閉じる

## final exit contract
- AC/EC 達成:
  - AC-001 / AC-002 / EC-001 / EC-002 / EC-003 が tests / docs / CLI evidence で観測可能
- docs impact resolved:
  - close-only と explicit `sync --github` confirmation path が docs で一貫している
- final diff approved:
  - RG / QG / SG がすべて pass し、S99 final diff review が承認されている
