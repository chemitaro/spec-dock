---
種別: 計画書（Epic）
ID: "epic-00048"
タイトル: "Agent facing interface hardening and host adapter scaffolding"
関連GitHub: ["#48"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-04-02"
依存: ["requirement.md", "design.md"]
親: ["init-local-00002"]
---

# epic-00048 Agent facing interface hardening and host adapter scaffolding — 計画（Issues / Order）

## この計画で閉じる E-RQ / E-AC
- E-RQ:
  - E-RQ-001, E-RQ-002, E-RQ-003, E-RQ-004, E-RQ-005
- E-AC:
  - E-AC-001, E-AC-002, E-AC-003, E-AC-004

## Issue 分割方針
- slicing principle:
  - protocol 固定 -> adapter 実装 -> docs/final review の 3 段に分ける。
  - 各 issue は 1 つの成果責務を持ち、過細分化しない。
- exceptions:
  - architecture-level invalid artifact prevention は本 epic では扱わず follow-up。

## Issue 一覧（順序 / tranche 付き）
- iss-epic48-01-protocol-and-active-context-contract:
  - 目的:
    - `active.json` / `index-all.json` / `index.json` / `context-pack.md` の責務を docs と runtime で一致させる。
  - deliverable:
    - protocol contract 更新、active/context 生成責務整理、関連 tests。
  - tranche:
    - tranche-1
  - closes:
    - E-RQ-001, E-RQ-002 の protocol 面
    - E-AC-001
  - depends on:
    - なし
- iss-epic48-02-host-adapter-scaffold-and-installer-sync:
  - 目的:
    - Codex/Copilot 向け host adapter scaffold を `init/update` managed asset として導入する。
  - deliverable:
    - adapter files、adapter metadata、installer 配布/更新、関連 tests。
  - tranche:
    - tranche-2
  - closes:
    - E-RQ-003
    - E-AC-002, E-AC-003
  - depends on:
    - iss-epic48-01-protocol-and-active-context-contract
- iss-epic48-03-docs-parity-and-final-epic-review:
  - 目的:
    - provider/dogfooding docs parity を完成させ、epic の final spec review を閉じる。
  - deliverable:
    - docs parity 修正、実行証跡、final review record。
  - tranche:
    - tranche-3
  - closes:
    - E-RQ-004, E-RQ-005
    - E-AC-004
  - depends on:
    - iss-epic48-02-host-adapter-scaffold-and-installer-sync

## 統合チェックポイント
- G1 decomposition review:
  - 3 issue で E-RQ/E-AC が全て対応しているか確認。
- G2 integration readiness:
  - protocol 変更と adapter 配布の責務境界が崩れていないか確認。
- G3 rollout/docs impact:
  - provider/dogfooding docs と assets の差分が説明可能か確認。
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
  - issue-01 -> issue-02 -> issue-03
- contract / docs refresh:
  - issue-01 で protocol docs 更新、issue-02 で adapter docs 追加、issue-03 で parity 総仕上げ。

## Issue readiness contract
- Issue に要求する最低条件:
  - 変更対象の責務境界が明示されている。
  - 観測コマンドと期待結果が plan/report に残る。
  - 次 issue への handoff 条件が明確。

## final exit contract
- E-AC closure:
  - E-AC-001..004 に対応する証跡が report に残る。
- integration / rollout complete:
  - protocol と adapter が両立し、host 間で実行導線が一致する。
- docs impact resolved:
  - provider/dogfooding docs parity が完了し、final review が pass している。

## 依存 / ブロッカー
- D-001:
  - 既存 `.agents/skills` managed asset 配布機構の整合。
- D-002:
  - architecture-level invalid artifact prevention の follow-up（本 epic では非対応）。

## 未確定事項
- Q-001:
  - 質問:
    - host adapter metadata の配置最終決定を issue-01 で閉じるか issue-02 で閉じるか。
  - 選択肢:
    - A:
      - issue-01 で契約決定し issue-02 は実装のみ。
    - B:
      - issue-02 で実装と同時決定。
  - 推奨案:
    - A。issue-02 の実装手戻りを減らせる。
  - 影響範囲:
    - issue-01/02 の境界、tests 設計。
