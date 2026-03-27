---
種別: 計画書（Initiative）
ID: "init-local-00003"
タイトル: "Architecture Maintenance and Hardening"
関連GitHub: []
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-03-27"
依存: ["requirement.md", "design.md"]
---

# init-local-00003 Architecture Maintenance and Hardening — 計画（Roadmap / Epics）

## この計画が達成する Goal / Metric
- Goal:
  - `spec-dock` を継続的に使える architecture baseline へ寄せる。
  - architecture issue を継続的に追加できる open-ended initiative portfolio を維持する。
- 対象 metric:
  - requirement の Metric-001 / Metric-002 / Metric-003

## マイルストーン
- M1:
  - deliverable:
    - open-ended initiative definition が docs に固定されている
  - exit:
    - initiative requirement / design / plan が新前提に更新されている
- M2:
  - deliverable:
    - GitHub-backed identity と ADR mirror workflow の epic が requirement / design / plan まで分解されている
  - exit:
    - 新 epic が issue 5本まで計画化されている
- M3:
  - deliverable:
    - 新 contract に沿った実装 epic が継続追加できる状態になっている
  - exit:
    - initiative portfolio と epic readiness contract が明確である

## Epic ポートフォリオ
- epic-00033-github-backed-identity-and-adr-mirror-workflow:
  - 目的:
    - GitHub mandatory identity、timestamp-based discussion/ADR naming、ADR symlink mirror workflow を単一 epic で導入する。
  - metric link:
    - Metric-002, Metric-003
  - status:
    - planned (current priority)
  - portfolio role:
    - GitHub issue #33 と連携した current epic。新 contract（GitHub-backed identity mandatory）へ移行するための優先実行対象。

## 順序と理由
- sequencing rationale:
  - initiative では固定的な終点を持たず、epic を追加し続ける。
  - 当面は `epic-00033` を優先し、新 identity contract と ADR workflow を先に閉じる。
  - その後に必要な architecture concern を追加 epic として取り込む。
- parallelizable:
  - future epic は追加可能だが、contract-heavy epic は同時多発させない。

## 意思決定ゲート
- G1 initiative scope review:
  - architecture concern だけを受け入れているか
- G2 epic readiness review:
  - epic が single coherent contract を持っているか
- G3 migration boundary review:
  - rebuildable workspace 前提と backward compatibility boundary が明示されているか
- G9 final initiative plan review:
  - new epic が initiative goal に沿っているか

## Epic readiness contract
- Epic に要求する最低条件:
  - source-of-truth / generated artifacts / migration boundary が明記されている
  - backward compatibility をどう扱うかが明記されている
  - 実装 issue 分解と順序がある

## final exit contract
- initiative は open-ended のため final close は定義しない。
- 代わりに、各 epic が initiative guardrail と整合していることを継続条件とする。
- 当面の milestone exit は `epic-00033` が planning 完了すること。

## 依存 / ブロッカー
- D-001:
  - dogfooding workspace rebuild の運用判断
- D-002:
  - single GitHub repo 前提の維持

## 未確定事項
- Q-001:
  - 質問:
    - 次に追加される architecture epic の優先順位付けを initiative plan に都度反映するか。
  - 選択肢:
    - A:
      - 反映する
    - B:
      - discussion のみで扱う
  - 推奨案:
    - A
  - 影響範囲:
    - initiative portfolio maintenance
