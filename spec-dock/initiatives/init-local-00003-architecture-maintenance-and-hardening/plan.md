---
種別: 計画書（Initiative）
ID: "init-local-00003"
タイトル: "Architecture Maintenance and Hardening"
関連GitHub: []
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-10"
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
    - dependency metadata unification と command mutation の architecture epic が portfolio に追加される
  - exit:
    - SoT/persistence/migration を扱う epic が initiative guardrail 付きで計画化されている

## Epic ポートフォリオ
- epic-00033-github-backed-identity-and-adr-mirror-workflow:
  - 目的:
    - GitHub mandatory identity、timestamp-based discussion/ADR naming、ADR symlink mirror workflow を単一 epic で導入する。
  - metric link:
    - Metric-002, Metric-003
  - status:
    - planned (current priority)
  - portfolio role:
    - GitHub issue #33 と連携した current epic。新 identity contract（GitHub-backed identity mandatory）への移行を担う。
- epic-00059-dependency-metadata-unification-and-command-mutation:
  - 目的:
    - dependency metadata の SoT を `.meta.json` に統合し、command-based mutation contract を導入する。
  - metric link:
    - Metric-001, Metric-003
  - status:
    - planned (next priority)
  - portfolio role:
    - source-of-truth/persistence boundary/migration を扱う architecture epic の正本。誤作成された `epic-00058` は削除済み（GitHub #58 close 済み）であり、canonical 実装先は `epic-00059` とする。

## 順序と理由
- sequencing rationale:
  - initiative では固定的な終点を持たず、epic を追加し続ける。
  - まず `epic-00033` の identity/ADR contract を完了し、次に `epic-00059` で dependency SoT 境界を統合する。
  - `epic-00059` は reader/schema -> mutation command -> downstream parity/migration -> docs/final review の順で進める。
  - `epic-00059` の hard cutover judgment は T3 integration で固定し、T4 は docs/dogfooding evidence の確認と final review に限定する。
- parallelizable:
  - 複数 epic の計画は並行可能だが、state boundary を変更する実装 epic は同時本番化しない。

## 意思決定ゲート
- G1 initiative scope review:
  - architecture concern だけを受け入れているか
- G2 epic readiness review:
  - epic が single coherent contract を持っているか
- G3 migration boundary review:
  - rebuildable workspace 前提と backward compatibility boundary が明示されているか
  - hard cutover judgment を T4 へ持ち越さず、T3 integration で固定する guardrail が保たれているか
- G9 final initiative plan review:
  - new epic が initiative goal に沿っているか

## Epic readiness contract
- Epic に要求する最低条件:
  - source-of-truth / generated artifacts / migration boundary が明記されている
  - backward compatibility をどう扱うかが明記されている
  - 実装 issue 分解と順序がある
  - hard cutover judgment を持つ epic は T3 integration までに判断と entry 条件を固定し、T4 を証跡確認に限定している

## final exit contract
- initiative は open-ended のため final close は定義しない。
- 代わりに、各 epic が initiative guardrail と整合していることを継続条件とする。
- 当面の milestone exit は `epic-00033` の計画実行着手と `epic-00059` の計画化完了。

## 依存 / ブロッカー
- D-001:
  - dogfooding workspace rebuild の運用判断
- D-002:
  - single GitHub repo 前提の維持

## 未確定事項
- なし:
  - `epic-00059` の `deps.json` hard cutover judgment は T3 integration で固定し、T4 は docs/dogfooding evidence 確認と final review に限定する。
