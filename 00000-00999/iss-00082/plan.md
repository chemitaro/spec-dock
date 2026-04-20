---
種別: 実装計画書（Issue）
ID: "iss-00082"
タイトル: "Fail fast on malformed node metadata"
関連GitHub: ["#82"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-04-20"
依存: ["requirement.md", "design.md"]
親: ["epic-00080", "init-00079"]
---

# iss-00082 Fail fast on malformed node metadata — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001
  - AC-002
  - AC-003
  - AC-004
- EC:
  - EC-001
  - EC-002
  - EC-003
- 制約:
  - fix scope は malformed metadata fail-fast に限定する
  - provider-side source of truth と mirror parity を維持する
  - external staging failure は non-goal のまま扱う
  - malformed 判定は `type` / `id` が `.strip()` 後に非空文字列でないケースへ閉じる

## マイルストーン一覧
- M1:
  - 対象:
    - pre-implementation spec lock
  - exit:
    - requirement / design / plan が `approved` で、SG1 spec review が `pass` になっている
- M2:
  - 対象:
    - red test 固定と provider-side fail-fast 実装
  - exit:
    - malformed `type` / `id` が RuntimeError になり targeted tests が pass する
- M3:
  - 対象:
    - mirror parity / error wording / issue evidence
  - exit:
    - dogfooding mirror が揃い、background evidence の non-goal 境界が docs に反映される
- M4:
  - 対象:
    - final validation and review closure
  - exit:
    - local validation / final diff review / final review evidence が `report.md` に残る

## 実装順序の根拠
- 依存関係の正本:
  - `design.md` の `依存関係分析` と module/dependency UML を参照する
- sequencing rule:
  - SG1 spec review で実装前 readiness を固定する
  - その後 `load_node_records()` の red test を先に固定する
  - provider-side contract を先に変え、そのあと mirror parity を揃える
- step ordering notes:
  - S00 は pre-implementation spec review gate
  - S01 は現状 bug の red test 固定
  - S02 は provider-side source of truth の修正
  - S03 は mirror parity と issue docs / report 整理
  - S90 は docs/report refresh
  - S99 は final validation and review

## ステップ一覧
- S00:
  - 観測可能な振る舞い:
    - issue docs だけで implementation-ready と判断できる
  - closes:
    - AC-004 baseline
  - review gate:
    - SG1 spec review pass
- S01:
  - 観測可能な振る舞い:
    - malformed metadata skip の現状が red test で再現される
  - closes:
    - AC-001 baseline
    - AC-002 baseline
  - review gate:
    - baseline evidence recorded in `report.md`
- S02:
  - 観測可能な振る舞い:
    - malformed `type` / `id` が RuntimeError になる
  - closes:
    - AC-001
    - AC-002
    - AC-003
    - EC-001
  - review gate:
    - RG1 implementation review pass
    - QG1 targeted tests pass
- S03:
  - 観測可能な振る舞い:
    - dogfooding mirror と docs / evidence が provider-side contract に追従する
  - closes:
    - AC-004
    - EC-002
    - EC-003
  - review gate:
    - RG1 implementation review pass
- S90:
  - 観測可能な振る舞い:
    - issue docs / report が実際の review 結果と verification scope を反映している
  - closes:
    - AC-004
  - review gate:
    - SG1 spec review pass
- S99:
  - 観測可能な振る舞い:
    - final validate / diff review / final review evidence が揃う
  - closes:
    - final exit contract
  - review gate:
    - SG1 final spec review pass
    - RG1 implementation review pass
    - QG1 QA review pass

## 要件 ↔ ステップ対応
- AC-001 -> S01, S02
- AC-002 -> S01, S02
- AC-003 -> S02
- AC-004 -> S00, S03, S90, S99
- EC-001 -> S02
- EC-002 -> S03, S99
- EC-003 -> S03

## レビュー / QA ゲート方針
- RG1 implementation review:
  - timing:
    - S02 後
    - S03 後
  - scope:
    - fail-fast contract
    - provider / mirror parity
  - commit gate:
    - pass まで review loop を回し、pass 後に `report.md` を更新して差分確認後にコミットする
- QG1 QA review:
  - timing:
    - S02 後
    - S99 前
  - scope:
    - green 状態の targeted tests
    - `validate` evidence
  - commit gate:
    - pass まで test loop を回し、pass 後に `report.md` を更新して差分確認後にコミットする
- SG1 spec review:
  - timing:
    - S00 後
    - S90 後
    - S99 前
  - scope:
    - issue scope closure
    - staging failure non-goal boundary
    - implementation readiness
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

### S01 — malformed metadata skip is fixed as a red test
- target:
  - relevant tests for `load_node_records()`
- design refs:
  - `design.md`
- step boundary:
  - missing `type` / `id` currently being skipped is demonstrated before implementation starts

#### update_plan（着手時に登録）
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — fail-fast red coverage
- purpose:
  - silent skip を bug として固定する
- files:
  - relevant tests

##### I1 — missing required metadata fields
- slice goal:
  - malformed `type` / `id` が fail すべきことを表現する

###### Red
- failing test:
  - malformed `type`
  - malformed `id`
- expected failure:
  - current implementation は `continue` してしまう

###### Green
- minimum implementation:
  - なし
- pass condition:
  - failing baseline と failure message expectation が `report.md` に記録される

###### Refactor
- 目的:
  - test naming と fixture を fail-fast intent に揃える
- guardrail:
  - production code はまだ変えない

### S02 — provider-side fail-fast contract
- target:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_repo.py`
  - relevant tests
- design refs:
  - `design.md`
- step boundary:
  - provider-side source of truth で malformed `type` / `id` が RuntimeError になる

#### B1 — minimal contract change
- purpose:
  - silent skip を RuntimeError に置き換える
- files:
  - provider-side fs repo
  - tests

##### I1 — malformed type
- slice goal:
  - malformed `type` は fail-fast

###### Red
- failing test:
  - malformed `type` regression
- expected failure:
  - current code skips

###### Green
- minimum implementation:
  - raise RuntimeError with `meta_path`
- pass condition:
  - test passes

###### Refactor
- 目的:
  - share error wording helper only if it reduces duplication
- guardrail:
  - valid-node path は変えない

##### I2 — malformed id
- slice goal:
  - malformed `id` は fail-fast

###### Red
- failing test:
  - malformed `id` regression
- expected failure:
  - current code skips

###### Green
- minimum implementation:
  - raise RuntimeError with `meta_path`
- pass condition:
  - test passes

###### Refactor
- 目的:
  - error wording consistency
- guardrail:
  - invalid-object / duplicate-id contract を壊さない

### S03 — mirror parity and issue evidence
- target:
  - `spec-dock/scripts/spec_dock_runtime/infra/fs_repo.py`
  - issue docs / report
- design refs:
  - `design.md`
- step boundary:
  - mirror parity と non-goal boundary を issue docs / report に反映する

#### B1 — parity and evidence
- purpose:
  - provider-side and mirror drift を残さない
- files:
  - dogfooding mirror
  - issue docs / report

##### I1 — parity sync
- slice goal:
  - mirror follows provider-side fail-fast contract

###### Red
- failing test:
  - changed-files parity review
- expected failure:
  - provider and mirror diverge

###### Green
- minimum implementation:
  - update mirror
- pass condition:
  - parity confirmed

###### Refactor
- 目的:
  - docs wording cleanup if needed
- guardrail:
  - do not widen scope beyond malformed metadata fail-fast

### S90 — docs impact resolution / docs refresh
- target:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md`
- design refs:
  - `design.md`
- step boundary:
  - reviewer 指摘、verification scope、optional operational evidence の扱いが issue docs に整合して反映される

#### step gate
- review:
  - SG1 spec review pass
- expected checks:
  - malformed 判定が `missing / blank / whitespace-only / non-string` に閉じている
  - `sync --github` が required completion gate から切り離されている
- report update:
  - review fail -> fix -> re-review -> pass の履歴を `report.md` に残す

### S99 — final validation and review closure
- target:
  - final diff
  - `report.md`
- design refs:
  - `design.md`
- step boundary:
  - required validation と final review evidence が complete で、optional operational evidence は分離して記録される

#### step gate
- review:
  - SG1 final spec review pass
- expected tests:
  - `./spec-dock/scripts/spec-dock validate`
  - targeted unit / runtime tests
- optional operational evidence:
  - `./spec-dock/scripts/spec-dock sync --github`
- report update:
  - final evidence、scope spill の有無、optional `sync --github` を実行しない場合の理由を残す
- commit expectation:
  - `report.md` 更新後に差分確認し、この issue scope の最終コミットまたは no-op を判断する

## 未確定事項
- なし:
  - malformed 判定、pre-implementation SG1、optional operational evidence の boundary はこの plan で固定する

## final exit contract
- AC/EC 達成:
  - malformed `type` / `id` が fail-fast し、valid metadata path と invalid-object contract は維持されている
  - provider-side source of truth と dogfooding mirror が同じ fail-fast contract を持つ
- readiness / docs impact resolved:
  - implementation 開始前に SG1 spec review が `pass` である
  - `report.md` に spec review fail -> fix -> re-review -> pass の履歴と最終 verdict が残る
- final diff approved:
  - diff は malformed metadata fail-fast issue の範囲に閉じており、external staging failure remediation を含まない
