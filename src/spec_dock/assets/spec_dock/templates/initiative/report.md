---
種別: レポート（Initiative）
ID: "<INIT_ID>"
タイトル: "<INIT_TITLE>"
状態: "draft | approved"
作成者: "<YOUR_NAME>"
最終更新: "YYYY-MM-DD"
依存: ["requirement.md", "design.md", "plan.md"]
---

# <INIT_ID> <INIT_TITLE> — レポート（進捗 / 決定 / 結果）

## 進捗サマリー (必須)
- 現在地（何が完了し、何が未完か）:
  - ...
- 次のマイルストーン:
  - ...
- ブロッカー:
  - ...

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact やInitiative判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | 採用（`adopted`） / 部分採用（`partially_adopted`） / 棄却（`rejected`） / 延期（`deferred`） / stale（`stale`） / blocked（`blocked`） | サブエージェント（`sub-agent`） / レビュアー（`reviewer`） / 議論（`discussion`） / コマンド（`command`） / 調査（`research`） | 成果物（`artifact`） / Issue（`issue`） / フォローアップ（`follow-up`） | ... | `path` / コマンド / レビュアー指摘 | なし / フォローアップ（`follow-up`） / 再レビュー（`re-review`） / 再訪条件（`revisit condition`） |

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
  - ワイルドカード grant semantics は非対応。`*`、`grants.*`、`all`、広すぎる role authority は invalid とする。
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

## 成功指標の状況 (必須)
- 指標 1:
  - Baseline:
  - Target:
  - Current/Actual:
  - 判断（達成/未達/未判定）:
- 指標 2:
  - ...

## 変更点/差分（Planとの差分） (任意)
- 予定の変更:
  - ...
- やらないことにしたもの（理由）:
  - ...

## ロールアウト/運用観測（必要なら） (任意)
- 段階公開の状況:
  - ...
- 監視値の変化（エラー率/レイテンシなど）:
  - ...
- 障害/アラート:
  - ...

## 実装結果の要約（完了後） (任意)
- ...

## 学び (任意)
- よかったこと:
  - ...
- 改善点:
  - ...

## フォローアップ（別Issue化） (必須)
- Epic/Issue links:
  - ...

## 省略/例外メモ (必須)
- 該当なし
