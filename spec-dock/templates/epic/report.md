---
種別: レポート（Epic）
ID: "<EPIC_ID>"
タイトル: "<EPIC_TITLE>"
状態: "draft | approved"
作成者: "<YOUR_NAME>"
最終更新: "YYYY-MM-DD"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["<INIT_ID>"]
---

# <EPIC_ID> <EPIC_TITLE> — レポート（進捗 / 決定 / 結果）

## 進捗サマリー (必須)
- 現在地（何が完了し、何が未完か）:
  - ...
- 次のマイルストーン:
  - ...
- ブロッカー:
  - ...

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）
- 委任 authoring の使用:
  - used / not used
- 未使用の場合:
  - manual authoring path / 委任ドラフトを昇格証跡として使っていない理由。
- lifecycle state（契約値）:
  - `requested`, `produced`, `integrated`, `partially_integrated`, `rejected`, `superseded`, `blocked`, `stale`
- 昇格不可 state:
  - `stale`, `rejected`, `superseded`, `blocked`
- 必須証跡 field:
  - role, phase, scope, consent, source artifacts, draft artifact path, status, integration result, rejected portions, blockers, reviewer result, promotion decision
- source_snapshot field:
  - source_revision, requirement_reviewer_pass_reference, design_reviewer_pass_reference, generated_at, stale_if
- authority metadata field:
  - status, authority, owner_role, draft_author_role, approval, source_revision, approved_revision, approved_hash
- grant keys:
  - review_input, planning_input, design_baseline, implementation_start, issue_ready, issue_finish, phase_completion
  - wildcard grant semantics are not supported; `*`, `grants.*`, `all`, and broad role authority are invalid
- Promotion Record / promotion_record field:
  - status, authority, owner_role, draft_author_role, approval, source_revision, approved_revision, approved_hash, reviewer_target_hash, promoted_at, promoted_by, promotion_decision
  - reviewer_target_hash / approved_hash mismatch or stale source_revision / approved_revision blocks promotion and downstream authority

| ロール（role） | フェーズ（phase） | 範囲（scope） | 同意（consent） | 参照元 artifact（source artifacts） | ドラフト artifact path（draft artifact path） | 状態（status） | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果（reviewer result） | 昇格判断（promotion decision） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| N/A | N/A | N/A | N/A | N/A | N/A | not used | manual authoring | N/A | none | N/A | no delegated draft promotion |

### 委任ドラフトの失敗モード（Delegated Draft Failure Modes）
| 失敗モード | 期待される判定 | 許可される次アクション | レポート証跡の記録先（report evidence destination） | 昇格可否 |
|---|---|---|---|---|
| 同意なし（missing consent） | blocked / incomplete | 範囲付き同意を取得する、または手動 authoring に戻す | この section | ineligible |
| 前段 reviewer pass 不足 / stale（missing/stale previous reviewer pass） | blocked / incomplete | レビューゲートを再実行する（rerun reviewer gate） | Spec Authoring Gate / reviewer evidence | ineligible |
| 設計中の要件 gap（requirement gap during design） | blocked / incomplete | requirement phase へ戻す | 判断台帳 / ゲート証跡（decision ledger / gate evidence） | ineligible |
| 計画中の設計 gap（design gap during plan） | blocked / incomplete | design phase へ戻す | 判断台帳 / ゲート証跡（decision ledger / gate evidence） | ineligible |
| ロール利用不可（role unavailable） | blocked / manual path | 利用不可を記録し、妥当なら手動で続行する | この section | ineligible |
| 禁止行為の試行（forbidden action attempt） | rejected | ドラフトを破棄し incident を記録する | この section / decision ledger | ineligible |
| 古いドラフト（stale draft） | stale | 再生成または差分調整する | この section | ineligible |
| 置換済みドラフト（superseded draft） | superseded | 置換先ドラフトを参照する | この section | ineligible |
| 委任使用主張に対する証跡不足（missing draft evidence when delegated use is claimed） | incomplete | 証跡を追加する、または委任使用 claim を外す | この section | ineligible |
| reviewer 利用不可 / 拒否 / waiver / provisional（reviewer unavailable/denied/waived/provisional） | blocked / incomplete | fresh な passed reviewer を取得する、または昇格なしの risk acceptance を記録する | レビューゲート証跡（reviewer gate evidence） | ineligible |

## 決定事項（ADRリンク） (必須)
- adr-xxxx-...: <1行要約>
- ...

## 完了した Issue / PR / Release (必須)
- iss-xxxx-...: Done（PR: ...）
- ...

## 受け入れ条件（E-AC）の達成状況 (必須)
- E-AC-001: Pass / Fail（証拠: ...）
- E-AC-002: ...

## ロールアウト結果（必要なら） (任意)
- 段階公開の状況:
  - ...
- 監視値（エラー率/レイテンシなど）:
  - ...
- 障害/アラート:
  - ...

## フォローアップ（別Issue化） (必須)
- iss-xxxx-...:
  - ...

## 省略/例外メモ (必須)
- 該当なし
