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

## Delegated Draft Evidence (必須)
- delegated authoring use:
  - used / not used
- If not used:
  - manual authoring path / no delegated draft was used as promotion evidence.
- Lifecycle states:
  - `requested`, `produced`, `integrated`, `partially_integrated`, `rejected`, `superseded`, `blocked`, `stale`
- Promotion-ineligible states:
  - `stale`, `rejected`, `superseded`, `blocked`
- Required evidence fields:
  - role, phase, scope, consent, source artifacts, draft artifact path, status, integration result, rejected portions, blockers, reviewer result, promotion decision
- source_snapshot fields:
  - source_revision, requirement_reviewer_pass_reference, design_reviewer_pass_reference, generated_at, stale_if

| role | phase | scope | consent | source artifacts | draft artifact path | status | integration result | rejected portions | blockers | reviewer result | promotion decision |
|---|---|---|---|---|---|---|---|---|---|---|---|
| N/A | N/A | N/A | N/A | N/A | N/A | not used | manual authoring | N/A | none | N/A | no delegated draft promotion |

### Delegated Draft Failure Modes
| failure mode | expected verdict | allowed next action | report evidence path | promotion eligibility |
|---|---|---|---|---|
| missing consent | blocked / incomplete | obtain scoped consent or use manual authoring | this section | ineligible |
| missing/stale previous reviewer pass | blocked / incomplete | rerun reviewer gate | Spec Authoring Gate / reviewer evidence | ineligible |
| requirement gap during design | blocked / incomplete | return to requirement phase | decision ledger / gate evidence | ineligible |
| design gap during plan | blocked / incomplete | return to design phase | decision ledger / gate evidence | ineligible |
| role unavailable | blocked / manual path | record unavailable and continue manually if valid | this section | ineligible |
| forbidden action attempt | rejected | discard draft and record incident | this section / decision ledger | ineligible |
| stale draft | stale | regenerate or reconcile | this section | ineligible |
| superseded draft | superseded | reference replacement draft | this section | ineligible |
| missing draft evidence when delegated use is claimed | incomplete | add evidence or remove delegated-use claim | this section | ineligible |
| reviewer unavailable/denied/waived/provisional | blocked / incomplete | obtain fresh passed reviewer or record risk acceptance without promotion | reviewer gate evidence | ineligible |

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
