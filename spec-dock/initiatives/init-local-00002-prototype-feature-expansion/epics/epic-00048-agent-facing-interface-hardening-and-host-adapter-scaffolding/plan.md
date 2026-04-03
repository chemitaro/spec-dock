---
種別: 計画書（Epic）
ID: "epic-00048"
タイトル: "Agent facing interface hardening and host adapter scaffolding"
関連GitHub: ["#48"]
状態: "draft"
作成者: "Codex"
最終更新: "2026-04-03"
依存: ["requirement.md", "design.md"]
親: ["init-local-00002"]
---

# epic-00048 Agent facing interface hardening and host adapter scaffolding — 計画

## この計画で満たす要件 / AC
- requirements:
  - E-RQ-001, E-RQ-002, E-RQ-003, E-RQ-004, E-RQ-005
- acceptance:
  - E-AC-001, E-AC-002, E-AC-003, E-AC-004

## Issue 分割方針
- slicing principle:
  - protocol / runtime alignment と host adapter deployment を分け、設計契約を先に固定する。
  - iss-00049 は自分が変更する protocol contract surface の runtime / provider docs / dogfooding docs / tests parity までを担当する。
  - iss-00050 は host adapter scaffold work、adapter 起因の残件 parity、final epic parity/review を担当し、仕上げ専用 issue は作らない。
  - 各 issue は 1 つの成果責務を持ち、過細分化しない。
- exceptions:
  - architecture-level invalid artifact prevention は本 epic では扱わず follow-up。

## Issue 一覧（順序 / tranche 付き）
- iss-00049-protocol-contract-and-runtime-alignment:
  - 目的:
    - `active.json` / `index.json` / `deps-issues.json` / `index-all.json` / `context-pack.md` の責務を runtime・provider docs・dogfooding docs・tests で一致させ、default working set と full-history の境界を固定する。
  - deliverable:
    - protocol contract 更新、active/context 生成責務整理、artifact ごとの `projection` / `source` contract 固定、通常実行では current-future projection を優先し full-history を第一選択にしない runtime/provider-doc/dogfooding-doc/test alignment。
  - tranche:
    - tranche-1
  - closes:
    - E-RQ-001, E-RQ-002 の protocol 面
    - E-AC-001
  - depends on:
    - なし
- iss-00050-host-adapter-scaffold-and-final-parity:
  - 目的:
    - Codex/Copilot 向け host adapter scaffold を `init/update` managed asset として導入し、adapter 起因の残件 parity と final spec review を閉じる。
  - deliverable:
    - adapter files、adapter metadata、installer 配布/更新、remaining adapter/provider-doc/dogfooding-doc parity 修正、host parity 証跡、final review record。
  - tranche:
    - tranche-2
  - closes:
    - E-RQ-003, E-RQ-004, E-RQ-005
    - E-AC-002, E-AC-003, E-AC-004
  - depends on:
    - iss-00049-protocol-contract-and-runtime-alignment

## 統合チェックポイント
- G1 decomposition review:
  - 2 issue で E-RQ/E-AC が全て対応しているか確認。
- G2 protocol readiness:
  - protocol 変更が iss-00049 の runtime/provider-doc/dogfooding-doc/test scope に一貫して反映されているか確認。
- G3 adapter rollout readiness:
  - adapter 配布、iss-00050 担当の残件 docs parity、host parity 証跡がそろっているか確認。
- G9 final epic spec review:
  - E-AC closure と follow-up の明確化を確認。

## 品質ゲート
- test / observability / migration / docs:
  - `sync` / `validate` 通過。
  - installer/runtime 主要 tests 通過。
  - host 間 parity 記録。
  - docs parity 差分ゼロまたは意図差分の説明完了。

## ロールアウト / docs impact
- rollout order:
  - issue-01 -> issue-02
- contract / docs refresh:
  - issue-01 で protocol contract surface の runtime / provider docs / dogfooding docs / tests を更新し、issue-02 で adapter 配布と残件 parity / final review を完了する。

## Issue readiness contract
- Issue に要求する最低条件:
  - 変更対象の責務境界が明示されている。
  - 観測コマンドと期待結果が plan/report に残る。
  - 次 issue への handoff 条件が明確。

## final exit contract
- E-AC closure:
  - E-AC-001..004 に対応する証跡が report に残る。
- integration / rollout complete:
  - protocol と adapter が両立し、host 間で実行導線が一致し、通常実行の第一選択が full-history になっていない。
- docs impact resolved:
  - iss-00049 対象の protocol docs parity と iss-00050 対象の adapter/final parity がそれぞれ完了し、final review が pass している。

## 依存 / ブロッカー
- D-001:
  - 既存 `.agents/skills` managed asset 配布機構の整合。
- D-002:
  - architecture-level invalid artifact prevention の follow-up（本 epic では非対応）。

## 設計上の決定
- D-003:
  - host adapter metadata は `.agents/host-adapters/meta.json` を第一案ではなく採用決定とする。
  - issue-00049 では artifact ごとの top-level metadata contract を固定する（`index.json`=`projection=current-future` / no new `source`、`index-all.json`=`projection=full-history` / no new `source`、`deps-issues.json`=`projection=open-issues-dependency-view` / provenance `source` 維持）。
