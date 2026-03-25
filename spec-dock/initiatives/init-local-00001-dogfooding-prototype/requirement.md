---
種別: 要件定義書（Initiative）
ID: "init-local-00001"
タイトル: "Dogfooding Prototype"
関連GitHub: []
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-03-14"
---

# init-local-00001 Dogfooding Prototype — 要件定義（WHAT / WHY）

## 目的（Outcome）
- Primary:
  - `spec-dock` 自身を `spec-dock` で管理しながら開発できる prototype を完成させる。
  - provider 側の実装と consumer 側の dogfooding workspace を一貫した運用でつなぐ。
- Secondary:
  - 実運用を通じて、agentic cli として不足している command、contract、diagnostics を早期に発見する。
  - 今後の roadmap を repo 内文書へ集約し、会話依存の管理を減らす。
  - dogfooding で見つかった課題を継続的に backlog へ投入し、prototype 完成までの改善ループを回す。

## 背景と Why now
- 現状の課題:
  - `spec-dock` の開発運用は、これまで半手動の文書管理と会話ベースの整理が混在していた。
  - local-only issue の完了状態、GitHub-linked issue との整合、link/unlink、machine-readable status contract が未整備である。
  - provider 側の source と dogfooding 中の generated workspace が同居しており、運用指針がないと誤編集しやすい。
- 影響:
  - 実運用で必要な機能が正式 backlog に落ちにくく、優先順位や実装順序がぶれやすい。
  - agent/human の両方にとって、状態遷移と GitHub 連携の扱いが分かりにくい。
- なぜ今やるか:
  - dogfooding を正式採用したため、repo 内に prototype initiative を持ち、ここを正本にして進める必要がある。
  - status lifecycle と link lifecycle を先送りにすると、dogfooding 自体が不安定になる。
- 情報源:
  - 現在の `spec-dock` runtime 構造
  - この initiative 配下の ADR
  - 現在の dogfooding workspace と AGENTS.md の運用方針

## 成功指標
- Metric-001:
  - Baseline:
    - `spec-dock` 自身の開発運用で、local-only issue の close/reopen、link/unlink、診断導線が不足している。
  - Target:
    - 本 initiative の roadmap と ADR を起点に、prototype 完成までの実装順と guardrail が固定されている。
  - 計測方法:
    - initiative 文書と ADR が current dogfooding workspace 上の正本として参照されること。
  - 判定時期:
    - 本 initiative 承認時、および prototype completion 判定時。
- Metric-002:
  - Baseline:
    - 状態遷移、authority、GitHub mutation の設計判断が文書間に分散している。
  - Target:
    - `status lifecycle`、`link/unlink`、`doctor/dry-run` の実装順序と、dogfooding で見つかった主要課題の投入先が一つの initiative に集約されている。
  - 計測方法:
    - plan.md / ADR / backlog note の整合確認。
  - 判定時期:
    - prototype completion 判定前。

## スコープ
- MUST:
  - `spec-dock` dogfooding を正式に採用し、この repo を `spec-dock` で管理する前提を固定する。
  - `status lifecycle` を product backlog の中核として扱う。
  - `link/unlink` と authority transfer の方針を固定する。
  - `machine-readable status contract` を roadmap の土台に含める。
  - `doctor`、`--dry-run`、`--explain` の診断系施策を roadmap に含める。
  - repo-safe な GitHub mutation を scope に含める。
  - existing artifact を壊さない additive migration を前提にする。
  - dogfooding で見つかったバグ、UX 問題、構造改善候補をこの initiative に継続投入できるようにする。
- MUST NOT:
  - GitHub issue を必須化して local-only issue を排除しない。
  - linked issue に local override を許す二重 authority を導入しない。
  - 既存 `status` や `.agent/index*.json` の意味を破壊的に置き換えない。
- OUT OF SCOPE:
  - PR helper
  - viewer extras / dashboard extras
  - naming / adoption extras
  - 広範な metadata automation
  - 今回の prototype 成立に直接関係しない純粋な refactor 単独施策
  - 日常運用可能な本番レベルへの到達
  - 安定運用体制の完成

## 境界
- Always:
  - provider 側の source of truth は `src/spec_dock/` に置く。
  - dogfooding workspace `spec-dock/` は利用側検証と active docs のために使う。
  - `1 issue = 1 authority` を維持する。
  - prototype 完成までをこの initiative の成功境界とする。
  - dogfooding で見つかった課題は backlog note / discussion / issue として継続投入する。
- Ask:
  - GitHub を伴う外部副作用の追加
  - 既存 artifact schema の hardening を warning から error に切り替える時
- Never:
  - hidden local history への自動巻き戻し
  - id/path の rename を伴う authority transfer
  - silent remote mutation

## ステークホルダー / 影響範囲
- 利用者:
  - `spec-dock` を利用する coding agent
  - `spec-dock` を使って仕様運用する開発者
- 運用者:
  - この repo の maintainer
  - dogfooding 運用で active docs と issue state を管理する人
- 開発者:
  - installer 側を保守する開発者
  - runtime cli を保守する開発者
- 影響システム / 領域:
  - `src/spec_dock/cli.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`
  - shipped scaffold docs/templates/system
  - local dogfooding workspace `spec-dock/`

## 非交渉制約
- 互換性:
  - existing artifact と existing consumer を壊さない additive migration を優先する。
  - 既存 `status` は残し、新 contract を追加 field として導入する。
- セキュリティ / 監査:
  - remote mutation は opt-in でのみ許可する。
  - wrong-repo risk を避ける repo-aware preflight を前提にする。
- 性能 / 可用性:
  - sync/update の信頼性を落とさない。
  - partial/stale failure を説明可能にする。
- 運用:
  - repo docs を正本とし、会話ログは正本にしない。
  - dogfooding 中でも provider と consumer の役割を混同しない。
  - prototype 完成前に見つかった課題は、この initiative の配下で継続管理する。

## リスク / 依存
- R-001:
  - `spec-dock` 自身を管理対象にすることで、未整備機能がそのまま開発速度に影響する。
- R-002:
  - status contract を誤って破壊的に変えると、既存 tests と consumer behavior に広く影響する。

## 未確定事項
- Q-001:
  - 質問:
    - GitHub-linked issue 向けの repo preflight をどの phase で最小導入するか。
  - 選択肢:
    - A:
      - Phase 3 直前に narrow preflight だけ先行導入する。
    - B:
      - Phase 4 の doctor と合わせて導入する。
  - 推奨案:
    - A。remote mutation より先に wrong-repo risk を抑える。
  - 影響範囲:
    - GitHub close/reopen の実装順と受け入れ条件。
