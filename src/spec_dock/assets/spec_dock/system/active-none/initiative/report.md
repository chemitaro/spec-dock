# イニシアチブレポート（Initiative report / placeholder / Activeなし）

現在アクティブな Initiative はありません。

- ここは placeholder です（編集対象外）
- 正しい場所: `spec-dock/initiatives/**/report.md`

## 委任ドラフト証跡 schema（Delegated Draft Evidence Schema / reference）
- lifecycle state（契約値）: `requested`, `produced`, `integrated`, `partially_integrated`, `rejected`, `superseded`, `blocked`, `stale`
- 昇格不可 state: `stale`, `rejected`, `superseded`, `blocked`
- 必須証跡 field: role, phase, scope, consent, source artifacts, draft artifact path, status, integration result, rejected portions, blockers, reviewer result, promotion decision
- source_snapshot field: source_revision, requirement_reviewer_pass_reference, design_reviewer_pass_reference, generated_at, stale_if
- authority metadata field: status, authority, owner_role, draft_author_role, approval, source_revision, approved_revision, approved_hash
- grant keys: can_write_requirement, can_write_design, can_write_plan, can_write_report, can_write_discussions, can_write_implementation, can_mark_issue_ready, can_finish_issue, can_complete_phase
- wildcard grant semantics are not supported; `*`, `can_write_*`, `all`, and broad role authority are invalid
- Promotion Record / promotion_record field: status, authority, owner_role, draft_author_role, approval, source_revision, approved_revision, approved_hash, reviewer_target_hash, promoted_at, promoted_by, promotion_decision
- reviewer_target_hash / approved_hash mismatch or stale source_revision / approved_revision blocks promotion and downstream authority
- failure-mode field: expected verdict, allowed next action, report evidence path, promotion eligibility

| 失敗モード | 期待される判定 | 許可される次アクション | report 証跡の記録先 | 昇格可否 |
|---|---|---|---|---|
| 同意なし（missing consent） | blocked / incomplete | 範囲付き同意を取得する、または手動 authoring に戻す | Delegated Draft Evidence | ineligible |
| 前段 reviewer pass 不足 / stale（missing/stale previous reviewer pass） | blocked / incomplete | reviewer gate を再実行する | Spec Authoring Gate / reviewer evidence | ineligible |
| 設計中の要件 gap（requirement gap during design） | blocked / incomplete | requirement phase へ戻す | decision ledger / gate evidence | ineligible |
| 計画中の設計 gap（design gap during plan） | blocked / incomplete | design phase へ戻す | decision ledger / gate evidence | ineligible |
| ロール利用不可（role unavailable） | blocked / manual path | 利用不可を記録し、妥当なら手動で続行する | Delegated Draft Evidence | ineligible |
| 禁止行為の試行（forbidden action attempt） | rejected | ドラフトを破棄し incident を記録する | Delegated Draft Evidence / decision ledger | ineligible |
| 古いドラフト（stale draft） | stale | 再生成または差分調整する | Delegated Draft Evidence | ineligible |
| 置換済みドラフト（superseded draft） | superseded | 置換先ドラフトを参照する | Delegated Draft Evidence | ineligible |
| 委任使用主張に対する証跡不足（missing draft evidence when delegated use is claimed） | incomplete | 証跡を追加する、または委任使用 claim を外す | Delegated Draft Evidence | ineligible |
| reviewer 利用不可 / 拒否 / waiver / provisional（reviewer unavailable/denied/waived/provisional） | blocked / incomplete | fresh な passed reviewer を取得する、または昇格なしの risk acceptance を記録する | reviewer gate evidence | ineligible |
