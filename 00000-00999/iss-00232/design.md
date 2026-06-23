---
種別: 設計書（Issue）
ID: "iss-00232"
タイトル: "Enforce Blocker Centric PR Repair And Rereview"
関連GitHub: ["#232"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
依存: ["requirement.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00232 Enforce Blocker Centric PR Repair And Rereview — 設計

## 全体像
- `pr_review_snapshot.py` の current Codex issue comment 解析に `blocker_policy` payload を追加する。
- Existing selected unresolved thread / changes requested の blocker 判定は維持し、priority comment policy はその前後に薄く追加する。
- Wait / merge-prepared 側は既存 `decision` payload を読むため、`decision.status` / `status_reason` / `recommended_next_action` の互換を保つ。

## 変更対象
- Provider source:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`
- Dogfooding mirror:
  - `.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`
- Tests:
  - `tests/unit/infra/test_init_update.py`

## Blocker policy model
- Input:
  - current trigger boundary 内の Codex-authored issue comments。
- Priority extraction:
  - `P0`, `P1`, `P2`, `P3` token を本文から抽出する。
- Protected domain:
  - security / privacy / data loss / permission / auth / migration / billing / financial / token / secret。
- Machine evidence:
  - `Test:`, `Repro:`, `Trace:`, `Error:`, `Assertion:`, `Command:`, `failing test`, `deterministic` などの deterministic evidence token。
- Disposition:
  - `P0` / `P1`: `blocker`
  - `P2` + protected domain + machine evidence: `promoted_blocker`
  - `P2` / `P3`: `non_blocking_followup`

## Payload contract
- `decision.blocker_policy`:
  - `status`: `blocker_present`, `non_blocking_only`, or `none`
  - `blocker_count`
  - `non_blocking_count`
  - `findings[]`
  - `blocker_fingerprints[]`
- `review.current.blocker_policy` mirrors the same policy payload.
- `decision.status_reason` additions:
  - `blocker_policy_validated_blocker`
  - `blocker_policy_no_action`

## Decision behavior
- Blocker present:
  - `decision.status=human_gate`
  - `recommended_next_action=address_review_feedback`
- Non-blocking only:
  - `decision.status=passed`
  - `recommended_next_action=merge_prepared`
- No priority token:
  - existing fallback behavior remains.

## Stagnation support
- This Issue records deterministic finding fingerprints in `blocker_policy.blocker_fingerprints`.
- Wait / repair orchestration can use stable fingerprints to detect automation-stalled without treating loop count alone as risk acceptance.
- Full operator-facing rollout of stagnation reporting is completed by I07.

## Compatibility
- Existing review thread, changes requested, pending review, no findings, fallback issue comment, and CI classification contracts remain unchanged unless a priority-bearing Codex issue comment is in the current trigger boundary.
