# Issue report（placeholder / Activeなし）

現在アクティブな Issue はありません。

- ここは placeholder です（編集対象外）
- 正しい場所: `spec-dock/initiatives/**/issues/**/report.md`

## Delegated Draft Evidence Schema (reference)
- Lifecycle states: `requested`, `produced`, `integrated`, `partially_integrated`, `rejected`, `superseded`, `blocked`, `stale`
- Promotion-ineligible states: `stale`, `rejected`, `superseded`, `blocked`
- Required evidence fields: role, phase, scope, consent, source artifacts, draft artifact path, status, integration result, rejected portions, blockers, reviewer result, promotion decision
- source_snapshot fields: source_revision, requirement_reviewer_pass_reference, design_reviewer_pass_reference, generated_at, stale_if
- Failure-mode fields: expected verdict, allowed next action, report evidence path, promotion eligibility

| failure mode | expected verdict | allowed next action | report evidence path | promotion eligibility |
|---|---|---|---|---|
| missing consent | blocked / incomplete | obtain scoped consent or use manual authoring | Delegated Draft Evidence | ineligible |
| missing/stale previous reviewer pass | blocked / incomplete | rerun reviewer gate | Spec Authoring Gate / reviewer evidence | ineligible |
| requirement gap during design | blocked / incomplete | return to requirement phase | decision ledger / gate evidence | ineligible |
| design gap during plan | blocked / incomplete | return to design phase | decision ledger / gate evidence | ineligible |
| role unavailable | blocked / manual path | record unavailable and continue manually if valid | Delegated Draft Evidence | ineligible |
| forbidden action attempt | rejected | discard draft and record incident | Delegated Draft Evidence / decision ledger | ineligible |
| stale draft | stale | regenerate or reconcile | Delegated Draft Evidence | ineligible |
| superseded draft | superseded | reference replacement draft | Delegated Draft Evidence | ineligible |
| missing draft evidence when delegated use is claimed | incomplete | add evidence or remove delegated-use claim | Delegated Draft Evidence | ineligible |
| reviewer unavailable/denied/waived/provisional | blocked / incomplete | obtain fresh passed reviewer or record risk acceptance without promotion | reviewer gate evidence | ineligible |
