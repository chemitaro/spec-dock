---
種別: 実装計画書（Issue）
ID: "iss-00037"
タイトル: "Migration Guardrails and Validation Hardening"
関連GitHub: ["#37"]
状態: "draft | approved"
作成者: "<YOUR_NAME>"
最終更新: "2026-03-27"
依存: ["requirement.md", "design.md"]
親: ["epic-00033", "init-local-00003"]
---

# iss-00037 Migration Guardrails and Validation Hardening — 実装計画（Execution Contract）

## この計画で満たす要件ID
- AC:
  - ...
- EC:
  - ...
- 制約:
  - ...

## マイルストーン一覧
- M1:
  - 対象:
  - exit:
- M2:
  - ...

## ステップ一覧
- S01:
  - 観測可能な振る舞い:
  - closes:
  - review gate:
- S02:
  - ...

## 要件 ↔ ステップ対応
- AC-001 -> S01
- EC-001 -> S02

## レビュー / QA ゲート方針
- RG1 implementation review:
  - timing:
  - scope:
- QG1 QA review:
  - timing:
  - scope:
- SG1 spec review:
  - timing:
  - scope:

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

## 実装ステップ

### S01 — <observable behavior>
- target:
  - ...
- design refs:
  - ...
- step boundary:
  - ...

#### update_plan（着手時に登録）
- [ ] `update_plan` に step の作業単位を登録した
- [ ] `./spec-dock/active/issue/report.md` の追記位置を決めた

#### B1 — <optional concern group>
- purpose:
  - ...
- files:
  - ...

##### I1 — <tdd cycle>
- slice goal:
  - ...

###### Red
- failing test:
  - ...
- expected failure:
  - ...

###### Green
- minimum implementation:
  - ...
- pass condition:
  - ...

###### Refactor
- cleanup target:
  - ...
- invariants to keep green:
  - ...

#### step gate
- review:
  - ...
- expected tests:
  - ...
- report update:
  - `./spec-dock/active/issue/report.md`

### Sxx — <next observable behavior>
- ...

### nested の使い方
- `step` は常に使う
- `block` は必要な時だけ分ける
- `iteration` は必要な数だけ並べる
- review / QA / docs / final diff は iteration の外に置く

### S90 — docs impact resolution / docs refresh
- 対象:
  - docs / assets / workflow / skill / none
- 対応:
  - ...

### S99 — final diff review quality gate
- branch diff scope:
  - ...
- required validation:
  - ...
- reviewer approvals:
  - ...

## 未確定事項
- Q-001:
  - 質問:
  - 選択肢:
    - A:
      - ...
    - B:
      - ...
  - 推奨案:
    - ...
  - 影響範囲:
    - ...

## final exit contract
- AC/EC 達成:
  - ...
- docs impact resolved:
  - ...
- final diff approved:
  - ...
