---
種別: ADR（Architecture Decision Record）
ID: "adr-002"
タイトル: "spec-dock 自身の開発運用に spec-dock を採用する"
状態: "accepted"
作成者: "Codex CLI"
最終更新: "2026-03-14"
親: []
---

# adr-002 spec-dock 自身の開発運用に spec-dock を採用する

## 結論（Decision） (必須)
- **決定**: `spec-dock` 自身の仕様管理、要件管理、設計管理、実装計画管理、GitHub issue 運用に `spec-dock` を段階的に採用する。
- `spec-deps/current` 配下の issue 単位文書と ADR を正本とする。
- 以後の開発運用は、会話ログや手動コピーペーストではなく、repo 内の `spec-dock` 資産を基準に進める。
- ただし導入は段階移行とし、未実装機能がある間は暫定運用ルールで補う。

## 背景（Context） (必須)
- 現在の `spec-dock` 自身の開発では、GitHub issue と issue 単位文書の連携が半手動で、会話内容をコピーして管理する簡易運用が混在している。
- 一方で `spec-dock` は `spec-dock/initiatives/**` を user asset として保持する構造を持ち、discussion / ADR / issue 管理の母体として利用しやすい。
- 今回の一連の議論により、`issue status lifecycle`、`link/unlink`、`status authority`、`doctor/dry-run` を整備すれば、開発対象そのものを自分で管理する self-hosting / dogfooding 運用が成立する見通しが明確になった。

## 選択肢（Options considered） (必須)
- Option A:
  - 概要:
    - 従来どおり、`spec-dock` 自身の開発は手動コピーペーストと GitHub issue 中心で運用する。
  - Pros:
    - 追加の運用設計が不要。
    - 既存の慣れた手順を維持できる。
  - Cons:
    - 仕様・設計・計画の正本が曖昧なまま残る。
    - `spec-dock` の dogfooding が進まず、実運用で見つかる問題が遅れる。
  - 棄却理由（棄却する場合）:
    - 今後の製品品質向上と agentic CLI としての成熟に不利。
- Option B:
  - 概要:
    - `spec-dock` 自身の開発運用を段階的に `spec-dock` へ移し、dogfooding を正式方針にする。
  - Pros:
    - 自分自身の運用で friction や欠落機能を早期発見できる。
    - issue 文書、ADR、GitHub issue、sync artifact の実利用を通じて品質改善が進む。
    - 正本が repo 内に定着する。
  - Cons:
    - bootstrap 期間中は、未実装機能を暫定運用で補う必要がある。
    - ツールの弱点が自分自身の開発速度にも影響する。
  - 棄却理由（棄却する場合）:
    - 該当なし。採用。

## 判断理由（Rationale） (必須)
- `spec-dock` は agentic CLI として育てる対象であり、実際の agent/human 共同運用で使われること自体が最も強い検証になる。
- 特に、今回論点となった `local-only issue` の完了状態、GitHub-linked issue との authority 整理、`link/unlink` の移管規則、`doctor/dry-run` の必要性は、dogfooding でこそ鮮明に検証できる。
- したがって、`spec-dock` を自分自身に適用することは、単なる運用変更ではなく、プロダクト品質改善のための中核的な意思決定である。

## 影響（Consequences） (必須)
- Positive（良い点）:
  - `spec-dock` の不足機能や不整合を、実際の開発運用の中で継続的に検出できる。
  - issue 文書、ADR、GitHub issue の関係が repo 内に固定され、会話依存が減る。
  - 今後追加する `status contract`、`close/reopen`、`link/unlink`、`doctor` の価値検証がしやすくなる。
- Negative / Debt（悪い点 / 将来負債）:
  - bootstrap 期間中は手順がやや複雑になり、暫定ルールの説明コストが発生する。
  - ツールの不足が、そのまま自分自身の運用 friction になる。
- 影響範囲（コード/テスト/運用/データ）:
  - `spec-deps/current` の運用
  - `spec-dock/initiatives/**` の今後の利用方針
  - GitHub issue と local issue 文書の扱い
- 移行/ロールバック:
  - 移行は段階的に行い、未実装期間中は手動運用を fallback として残す。
  - 問題が出た場合でも、repo 内文書を正本としつつ、GitHub issue 単独運用へ一時退避できる。
- Follow-ups（追加の Epic/Issue/ADR）:
  - `adr-003` で定める実装順序に従って、dogfooding に必要な能力を順次追加する。

## 参考（References） (任意)
- 関連 ADR:
  - [adr-003-spec-dock-agentic-cli-roadmap.md](/srv/mount/spec-dock/spec-deps/current/adrs/adr-003-spec-dock-agentic-cli-roadmap.md)
- 関連コード:
  - [cli.py](/srv/mount/spec-dock/src/spec_dock/cli.py)
  - [contracts.py](/srv/mount/spec-dock/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py)

