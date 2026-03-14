---
種別: 計画書（Initiative）
ID: "init-local-00001"
タイトル: "Dogfooding Prototype"
関連GitHub: []
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-03-14"
依存: ["requirement.md", "design.md"]
---

# init-local-00001 Dogfooding Prototype — 計画（Roadmap / Epics）

## この計画が達成する Goal / Metric
- Goal:
  - `spec-dock` 自身を `spec-dock` で管理しながら、状態管理・authority transfer・診断系まで含む prototype を完成させる。
- 対象 metric:
  - roadmap と ADR に基づいて epic が切り出せること
  - status lifecycle と link lifecycle の実装順が固定されていること
  - dogfooding 運用で必要な最小 command 群が明確であること
  - 主要な dogfooding blocker が backlog 管理下にあること

## マイルストーン
- M1:
  - deliverable:
    - status と authority の基盤テーマが実装計画として着手可能
  - exit:
    - Epic 1 の issue 分割が完了している
- M2:
  - deliverable:
    - link/unlink と GitHub lifecycle のテーマが実装計画として着手可能
  - exit:
    - Epic 2 の issue 分割が完了している
- M3:
  - deliverable:
    - diagnostics / discovery / hardening の後半テーマが実装計画として着手可能
  - exit:
    - Epic 3-4 の issue 分割が完了している
- M4:
  - deliverable:
    - prototype completion 判定に必要な主要 blocker と remaining backlog が整理されている
  - exit:
    - prototype 完成判定が可能

## Epic ポートフォリオ
- epic-0001-status-and-authority-foundation:
  - 目的:
    - status と authority の土台を定義し、local path を先に成立させる。
  - deliverable:
    - Phase 0 に対応する machine-readable status contract
    - `authority`, `effective`, `source`, `stale`, `reconcile_action` の surface 設計
    - local-managed issue 向け close/reopen の基本方針
    - `issue show/status --json` の観測導線
    - projection/cache と authority 分離の validate 方針
  - metric link:
    - M1
  - depends on:
    - なし
- epic-0002-link-and-github-lifecycle:
  - 目的:
    - authority transfer と GitHub lifecycle を一つの設計テーマとして成立させる。
  - deliverable:
    - Phase 2 に対応する `link` / `unlink` と authority transfer
    - `unlink --adopt effective` の既定動作
    - contradiction validate と migration-safe な reject rule
    - Phase 3 に対応する GitHub close/reopen の導線
    - repo-safe preflight と remote mutation の opt-in 原則
  - metric link:
    - M2
  - depends on:
    - epic-0001-status-and-authority-foundation
- epic-0003-operability-and-diagnostics:
  - 目的:
    - dogfooding 運用で mutate 系 command を安全かつ説明可能にし、運用上の気づきを継続投入できる受け皿を持つ。
  - deliverable:
    - Phase 4 に対応する `doctor`
    - `--dry-run` の導入方針
    - `--explain` と reason code / next action の整理
    - stale / partial / blocked 状態の説明契約
    - 運用時の preflight / failure messaging の一貫化
    - debug / ux / operability 上の気づきを issue 化するための受け皿整理
  - metric link:
    - M3
  - depends on:
    - epic-0002-link-and-github-lifecycle
- epic-0004-discovery-and-hardening:
  - 目的:
    - visibility と recoverability を後半テーマとして仕上げ、dogfooding で見つかった構造改善候補を継続投入できるようにする。
  - deliverable:
    - Phase 5 に対応する `list` / `find` / `show` 系 discovery
    - status filtering と stale visibility
    - Phase 6 に対応する atomic sync/update
    - contradiction validation hardening
    - migration assist と rollback/recovery 方針
    - dogfooding feedback に基づく構造改善候補の backlog 管理
  - metric link:
    - M3
  - depends on:
    - epic-0003-operability-and-diagnostics

## 順序と理由
- sequencing rationale:
  - Phase は product rollout の順序を表す。
  - Epic はその順序を束ねる設計テーマを表す。
  - Epic は一般的に適切な大まかな設計テーマとして維持し、細かな分割は issue に落とす。
  - Issue は各 epic 内で実装可能な単位へ分割する。
  - `status contract` を mutation より先に固定し、その後 local path、authority transfer、remote mutation の順で進める。
  - diagnostics は mutation が増えるタイミングでまとめて強化し、discovery/hardening は後半テーマとして扱う。
  - dogfooding で見つかった細かなバグ、UX 問題、構造改善候補は、適切な epic の issue として継続投入する。
- parallelizable:
  - Epic 3 の一部と Epic 4 の一部は並行可能。
  - ただし Epic 2 までの authority 決定が前提になる。

## 意思決定ゲート
- G1 strategy review:
  - 4-epic 構成と Phase 順序の受け入れ確認
- G2 milestone readiness:
  - Epic 1 完了時に status contract と local mutation の整合確認
- G3 governance/docs impact:
  - Epic 2 着手前に link/unlink と GitHub mutation の guardrail を確認
- G4 operability review:
  - Epic 3 着手前に diagnostics の surface を確認
- G9 final initiative plan review:
  - Epic 4 着手前に remaining debt と hardening 範囲を見直す
- G10 prototype completion review:
  - prototype が完成し、主要な dogfooding blocker が backlog 管理下にあることを確認する

## 指標レビュー計画
- review timing:
  - 各 milestone 完了時
- dashboard / source:
  - initiative 配下の文書、ADR、epic backlog、dogfooding 実運用で得られた feedback

## ロールアウト計画
- rollout window:
  - prototype first
  - dogfooding を通じて段階導入
- release / communication:
  - repo docs と AGENTS.md を基準に共有する

## Epic readiness contract
- Epic に要求する最低条件:
  - user-facing capability が 1 つに絞られていること
  - compatibility guardrail が明記されていること
  - affected layer と tests が特定されていること

## final exit contract
- milestone exit:
  - prototype が完成し、Phase 0-6 に対する epic backlog が運用可能な粒度で整理されていること
- success metrics reviewed:
  - requirement の metric を milestone ごとに確認していること
- remaining follow-up ownership:
  - prototype 後の extras は別 initiative / epic に切り分ける
  - 主要な dogfooding blocker は backlog 管理下にあり、残課題の行き先が明確であること

## 依存 / ブロッカー
- D-001:
  - provider/source と generated workspace の責務分離が保たれること
- D-002:
  - GitHub mutation の preflight 設計が固まること

## 未確定事項
- Q-001:
  - 質問:
    - Phase 5 discovery を独立 epic にするか、Phase 4/6 に吸収するか。
  - 選択肢:
    - A:
      - discovery を diagnostics 側へ寄せる。
    - B:
      - visibility 強化として独立させる。
  - 推奨案:
    - B。観測可能性を一段として扱った方が運用上分かりやすい。
  - 影響範囲:
    - epic 粒度と並行実装の切り方。
