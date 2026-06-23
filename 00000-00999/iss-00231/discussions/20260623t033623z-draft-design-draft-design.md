---
種別: 設計書ドラフト（Issue）
ID: "iss-00231"
タイトル: "Inject Trusted Base Branch Codex Review Policy"
関連GitHub: ["#231"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
親: ["epic-00224", "init-local-00003"]
---

# iss-00231 Draft Design

## 設計方針
- Review policy source is PR base SHA, not PR head。
- Trigger compiler owns deterministic comment body。
- GitHub write surface remains fixed and narrow。

## 変更対象
- Provider:
  - `domain/review_policy.py`
  - `application/compile_review_trigger.py`
  - `infra/review_policy_store.py`
  - `infra/review_generation_store.py`
  - `presentation/review_policy_text.py`
  - `src/spec_dock/assets/install_root/.github/codex/review-policy.md`
- Dogfooding mirror:
  - `.github/codex/review-policy.md`
  - review trigger evidence under `.agent/review-generations/**` ignored。

## Trigger Contract
- Inputs: repository, PR number, expected head SHA。
- Reads: current PR head, PR base SHA, `<base-sha>:.github/codex/review-policy.md`。
- Outputs: comment id, reviewed head SHA, policy base SHA, policy hash, body hash, limitations。
- Forbidden: caller body / caller policy path / raw endpoint。

## 検証
- fake GitHub base/head fixtures。
- policy validation failure paths。
- stale head test。
- deterministic body golden tests。
- existing observation compatibility。
- typed GitHub boundary for MyPy / Ruff baseline。

## Handoff
- I06 consumes review generation evidence and reviewed head binding。
- I07 validates real/fake PR rollout behavior。
