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

# <ISS_ID> <ISS_TITLE> — 実装計画（TDD: Red → Green → Refactor）

## この計画で満たす要件ID (必須)
- 対象AC: AC-001, ...
- 対象EC: EC-001, ...

## ステップ一覧（観測可能な振る舞い） (必須)
- [ ] S01: ...
- [ ] Sxx: ...（必要に応じて追加）

### 要件 ↔ ステップ対応表 (必須)
- AC-001 → S01

---

### S01 — <観測可能な振る舞い> (必須)

#### `update_plan`（着手時に登録） (必須)
- [ ] ...

#### 期待する振る舞い（Given/When/Then） (必須)
- Given: ...
- When: ...
- Then: ...

#### 作業（TDD） (必須)
- Red: ...
- Green: ...
- Refactor: ...

#### ステップ末尾（必須） (必須)
- [ ] テスト/品質ゲートを通した
- [ ] `report.md` にコマンド/結果/変更ファイルを記録した
- [ ] `update_plan` を更新し、このステップの作業ステップを完了にした

---

## 未確定事項（TBD） (必須)
- ...

## 完了条件（Definition of Done） (必須)
- 対象AC/ECがすべて満たされ、テストで保証されている
- MUST NOT / OUT OF SCOPE を破っていない

## 省略/例外メモ (必須)
- 該当なし

