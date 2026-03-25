---
種別: 計画書（Initiative）
ID: "init-local-00001"
タイトル: "Dogfooding Prototype"
関連GitHub: []
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-03-25"
依存: ["requirement.md", "design.md"]
---

# init-local-00001 Dogfooding Prototype — 計画（Roadmap / Epics）

## この計画が達成する Goal / Metric
- Goal:
  - usable dogfooding runtime の current baseline を initiative 正本へ同期し、remaining work を安全に次の投資単位へ分解できる状態にする。
- 対象 metric:
  - requirement の Metric-001:
    - usable runtime with caveats が requirement/design/plan で一貫して読めること
  - requirement の Metric-002:
    - established capability と remaining work の境界が plan 上で明示されていること

## マイルストーン
- M1:
  - deliverable:
    - initiative 正本が 2026-03-25 時点の runtime contract に同期している
  - exit:
    - requirement/design/plan が manual rerun current-state と durable lessons を反映している
- M2:
  - deliverable:
    - current baseline と remaining follow-up の境界が epic レベルで整理されている
  - exit:
    - established / ongoing / remaining の整理に基づいて次の epic 分解判断ができる
- M3:
  - deliverable:
    - remediation / guidance / lifecycle expansion の優先順位が投資判断として比較可能になっている
  - exit:
    - remaining work の ownership が current initiative 内か follow-up initiative か判断できる
- M4:
  - deliverable:
    - prototype completion 判定と post-prototype follow-up ownership が整理されている
  - exit:
    - 「この initiative で閉じるもの」と「次へ切り出すもの」が文書上で明確である

## Epic ポートフォリオ
- epic-0001-runtime-contract-and-architecture-baseline:
  - 目的:
    - dogfooding runtime の current baseline と architecture guardrail を正本に固定する。
  - deliverable:
    - established:
      - hybrid layered architecture
      - provider/generated separation
      - usable runtime baseline (`new/active/sync/deps/import/validate/doctor`)
    - remaining:
      - architecture / contract drift を継続監視する更新運用
  - metric link:
    - Metric-001
  - depends on:
    - なし
- epic-0002-repo-scope-and-state-safety:
  - 目的:
    - repo-aware exact targeting、fail-closed ambiguity、create/recovery guardrail を prototype の中心 safety theme として維持する。
  - deliverable:
    - established:
      - canonical URL / `--id` exact resolution
      - overlap 下の bare numeric fail-closed
      - no-origin continuity for normalized metadata
      - legacy unscoped metadata を auto-heal しない境界
    - remaining:
      - manual remediation / operator guidance の ownership 決定
  - metric link:
    - Metric-001
    - Metric-002
  - depends on:
    - epic-0001-runtime-contract-and-architecture-baseline
- epic-0003-operability-diagnostics-and-parity:
  - 目的:
    - diagnostics と parity maintenance を established capability として維持し、追加改善の投資先を整理する。
  - deliverable:
    - established:
      - `doctor`
      - validate/sync の failure guidance
      - stale active recovery / readonly non-mutation
      - provider/check-in parity discipline
      - manual rerun baseline
    - remaining:
      - operator runbook / doctor guidance 強化
      - parity maintenance を継続できる verification discipline
  - metric link:
    - Metric-001
    - Metric-002
  - depends on:
    - epic-0002-repo-scope-and-state-safety
- epic-0004-remaining-lifecycle-and-follow-up-investment:
  - 目的:
    - prototype completion 後に残る lifecycle expansion / discovery / hardening を current initiative から切り離して整理する。
  - deliverable:
    - established:
      - remaining work は current baseline を壊さない additive investment として扱う方針
    - remaining:
      - manual remediation の所在
      - link/unlink / remote lifecycle expansion の優先順位
      - discovery / hardening / extras を別投資へ分ける方針
  - metric link:
    - Metric-002
  - depends on:
    - epic-0003-operability-diagnostics-and-parity

## 順序と理由
- sequencing rationale:
  - まず current baseline を正本化し、その上で repo-scope / state safety を remaining work と切り分ける。
  - diagnostics / parity はすでに成立した capability なので、「これから実装するもの」ではなく「維持と深化の対象」として扱う。
  - lifecycle expansion や extras は、current runtime を usable に保つことより優先しない。
  - prototype completion 判定は、新機能の量ではなく current baseline と remaining ownership の明確さで行う。
- parallelizable:
  - Epic 2 と Epic 3 の remaining follow-up は並行で整理できる。
  - ただし Epic 4 の ownership 判断は Epic 2/3 の結論に依存する。

## 意思決定ゲート
- G1 refresh strategy review:
  - current initiative docs を roadmap-only stance から current reality へ同期する方針を確認する
- G2 baseline contract review:
  - usable runtime baseline、repo-scope contract、diagnostics、parity guardrail の記述が揃っていることを確認する
- G3 remaining ownership review:
  - manual remediation / operator guidance / lifecycle expansion の ownership を current initiative に残すか別投資へ分離するか判断する
- G4 prototype completion review:
  - current initiative を「usable prototype の確立」で閉じられるかを確認する
- G9 final initiative plan review:
  - remaining follow-up の切り出し方と post-prototype roadmap を確認する

## 指標レビュー計画
- review timing:
  - initiative refresh 完了時
  - remaining ownership 判断時
  - prototype completion 判断時
- dashboard / source:
  - initiative requirement/design/plan
  - discussions/004, 005, 006, 007, 009
  - manual rerun evidence
  - current dogfooding runtime surface

## ロールアウト計画
- rollout window:
  - usable baseline を維持しながら remaining work を切り出す
  - unsafe automation は導入せず、fail-closed contract を保持する
- release / communication:
  - initiative docs と ADR/discussion を正本として共有する
  - operator guidance は canonical URL / `--id` 優先を前提にする

## Epic readiness contract
- Epic に要求する最低条件:
  - established capability と remaining work が分かれていること
  - 既存 baseline を壊さない guardrail が書かれていること
  - parity / repo-scope / diagnostics のどれに効く投資かが説明できること
  - post-prototype へ切り出す場合は ownership が明示されていること

## final exit contract
- milestone exit:
  - current initiative docs が current runtime baseline と remaining boundary を表現できていること
  - usable dogfooding runtime with caveats が文書上明示されていること
- success metrics reviewed:
  - requirement の Metric-001 / Metric-002 を refresh 完了時に確認していること
- remaining follow-up ownership:
  - manual remediation / operator guidance / lifecycle expansion の行き先が current initiative か follow-up initiative かで明示されていること
  - issue-28 corrective trace に戻らなくても、次の投資判断ができること

## 依存 / ブロッカー
- D-001:
  - provider/source と generated workspace の責務分離を維持すること
- D-002:
  - current manual rerun baseline を durable contract として読み替えること
- D-003:
  - parity maintenance を explicit verification discipline として扱うこと

## 未確定事項
- Q-001:
  - 質問:
    - prototype completion 判定の後、manual remediation / operator guidance を current initiative の残作業として扱うか、follow-up initiative として切り出すか。
  - 選択肢:
    - A:
      - current initiative の remaining epic として残す。
    - B:
      - current initiative は baseline establishment で閉じ、follow-up initiative を切る。
  - 推奨案:
    - B。current baseline は成立しており、残課題は次の運用改善投資として切り出した方が境界が明瞭になる。
  - 影響範囲:
    - prototype completion review
    - 次の epic / initiative backlog の構成
