---
種別: 要件定義書（Issue）
ID: "iss-00232"
タイトル: "Enforce Blocker Centric PR Repair And Rereview"
関連GitHub: ["#232"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
親: ["epic-00224", "init-local-00003"]
---

# iss-00232 Enforce Blocker Centric PR Repair And Rereview — 要件定義

## 目的
- PR observation の merge-prepared 判定を comment zero ではなく、verified blocker zero に寄せる。
- P0 / P1 と machine-validated promoted P2 だけを repair / re-review 対象にし、P2 / P3 の改善提案で不要な push / review loop を起こさない。

## 背景
- 既存の `github-pr-observation` は current Codex feedback、unresolved thread、changes requested を human gate へ送れる。
- 一方で Codex issue comment に含まれる P2 / P3 の改善提案は、現状では generic fallback として扱われやすく、軽量 / 標準 task の repair loop を膨らませる。
- Accepted ADR `20260623t074447z-adr-blocker-centric-pr-risk-closure-rereview.md` は、P2 / P3 default non-blocking と、protected domain + machine evidence を持つ P2 のみ blocker promotion する判断を固定している。

## スコープ
- 必須:
  - Codex の current issue comment から priority `P0`〜`P3` を検出し、`blocker_policy` payload を出す。
  - `P0` / `P1` は blocker として `human_gate` / `address_review_feedback` にする。
  - `P2` / `P3` は default non-blocking follow-up として `merge_prepared` を妨げない。
  - `P2` は protected domain と machine evidence が両方ある場合だけ `promoted_blocker` として blocker にする。
  - Finding fingerprint を payload に含め、stagnation / automation-stalled 判定に使える evidence を残す。
  - provider asset と dogfooding mirror を同期する。
- 禁止:
  - comment zero を merge gate にすること。
  - reviewer assertion alone だけで P2 を blocker に昇格すること。
  - loop count だけで risk acceptance すること。
- 対象外:
  - Auto-merge。
  - GitHub Actions / Checks の CI policy 変更。
  - 実 PR への review trigger 実行。これは Epic PR preparation で扱う。

## 非交渉制約
- 判定不能な protected risk は安全側に human gate へ送る。
- P2 / P3 only は repair push / re-review trigger を要求しない。
- Material delta 判定や review policy semantics 変更は fresh review required のまま維持する。

## 受け入れ条件
- AC-001: P2 noise suppression
  - 前提: current Codex issue comment が `P2` の改善提案のみを含み、protected domain / machine evidence を持たない。
  - 期待: `decision.status=passed`、`status_reason=blocker_policy_no_action`、`recommended_next_action=merge_prepared` になる。
- AC-002: P2 blocker promotion
  - 前提: current Codex issue comment が `P2`、protected domain、machine evidence を含む。
  - 期待: `blocker_policy.findings[].disposition=promoted_blocker` となり、`decision.status=human_gate` / `address_review_feedback` になる。
- AC-003: Existing blockers remain blockers
  - 前提: current unresolved thread または changes requested がある。
  - 期待: 既存の selected blocker / changes requested decision が維持される。
- AC-004: Fingerprint evidence
  - 前提: blocker policy finding がある。
  - 期待: finding fingerprint と blocker fingerprints が payload に含まれる。

## 例外・エッジケース
- EC-001: priority が本文から検出できない current Codex issue comment は generic fallback として扱い、安易に pass へ昇格しない。
- EC-002: P2 に protected domain だけ、または machine evidence だけがある場合は promoted blocker にしない。
- EC-003: GraphQL / review thread collection が blocking limitation を返す場合は既存どおり human gate / unknown にする。
