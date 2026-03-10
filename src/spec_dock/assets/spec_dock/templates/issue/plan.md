---
種別: 実装計画書（Issue）
ID: "<ISS_ID>"
タイトル: "<ISS_TITLE>"
関連GitHub: ["<GITHUB_ISSUE_NUMBER_OR_URL>"]
状態: "draft | approved"
作成者: "<YOUR_NAME>"
最終更新: "YYYY-MM-DD"
依存: ["requirement.md", "design.md"]
親: ["<EPIC_ID>", "<INIT_ID>"]
---

# <ISS_ID> <ISS_TITLE> — 実装計画（Execution Contract）

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
- 各 step は 1 つの観測可能な振る舞いを単位とする。
- nested は `step` を基本とし、`block` / `iteration` は必要な時だけ使う。
- 各 step は **Red → Green → Refactor → review → fix → re-review → report → commit/no-op** の順で閉じる。
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

#### B1 — <work block>
- purpose:
  - ...
- files:
  - ...

##### I1 — <iteration>
- Red:
  - ...
- Green:
  - ...
- Refactor:
  - ...

#### milestone gate
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
- `block` は必要な時だけ使う
- `iteration` は複雑な step で必要な時だけ使う

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
