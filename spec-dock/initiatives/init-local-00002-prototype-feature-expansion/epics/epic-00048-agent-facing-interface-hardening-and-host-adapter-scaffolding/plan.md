---
種別: 計画書（Epic）
ID: "epic-00048"
タイトル: "Agent facing interface hardening and host adapter scaffolding"
関連GitHub: ["#48"]
状態: "approved"
作成者: "Codex"
最終更新: "2026-04-04"
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
  - `iss-00049` は自分が変更する protocol contract surface の runtime / provider docs / dogfooding docs / tests parity までを担当する。
  - `iss-00050` は host adapter scaffold work、adapter 起因の残件 parity、final epic parity/review を担当し、仕上げ専用 issue は作らない。
  - host-native deployment は本体 accepted scope を壊さず、後続 follow-up 2 issue で extension として扱う。
  - 各 issue は 1 つの成果責務を持ち、過細分化しない。
- exceptions:
  - architecture-level invalid artifact prevention は本 epic では扱わず follow-up。

## Issue 一覧（順序 / tranche 付き）
- iss-00049-protocol-contract-and-runtime-alignment:
  - 状態:
    - done
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
  - 状態:
    - done
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
- follow-up-a-host-native-agent-artifact-contract-and-installer-sync:
  - 状態:
    - planned
  - 目的:
    - Codex の `.codex/agents/*.toml` と GitHub Copilot の `.github/agents/*.agent.md` を thin shim として managed deployment し、manifest / source-of-truth / installer sync/prune 契約を固定する。
  - deliverable:
    - provider-side native shim assets、manifest 拡張、`src/spec_dock/cli.py` の sync/prune 追加、installer tests、host-specific artifact contract。
  - tranche:
    - tranche-3
  - closes:
    - E-RQ-002 の native shim 面
    - E-RQ-003 の host-native artifact deployment 面
  - depends on:
    - iss-00050-host-adapter-scaffold-and-final-parity
- follow-up-b-native-agent-integration-validation-and-doc-closure:
  - 状態:
    - planned
  - 目的:
    - host-native artifact を dogfooding / docs / validation / manual test に接続し、orchestrator から native agent へ委譲できることを閉じる。
  - deliverable:
    - docs refresh、dogfooding mirror 方針反映、validation/doctor 判断、manual test 記録、final review evidence。
  - tranche:
    - tranche-4
  - closes:
    - E-RQ-004 の native artifact 面
    - E-RQ-005 の follow-up closure 面
    - E-AC-002, E-AC-003, E-AC-004 の native artifact 面
  - depends on:
    - follow-up-a-host-native-agent-artifact-contract-and-installer-sync

## 既存 accepted scope と follow-up extension の読み方
- done として保持するもの:
  - `iss-00049` は protocol / runtime / docs / tests alignment の完了済み tranche として reopen しない。
  - `iss-00050` は thin adapter skill / metadata deployment / parity / final review の完了済み tranche として reopen しない。
- 追加するもの:
  - follow-up-a / follow-up-b は、host-native custom agent / subagent deployment を extension として追加する tranche である。
  - 既存 2 issue の report / close record はそのまま残し、native artifact gap を retroactive な未完了扱いにしない。
- split rationale:
  - issue 粒度は `discussions/20260404t010500z-disc-host-native-agent-deployment-gap-analysis.md` の 2 分割案に従う。
  - artifact contract / installer ownership と integration / validation closure を分け、過細分化せず 4 tranche で閉じる。

## 統合チェックポイント
- G1 decomposition review:
  - 既存 2 issue + follow-up 2 issue で E-RQ/E-AC が全て対応しているか確認。
- G2 protocol readiness:
  - protocol 変更が `iss-00049` の runtime/provider-doc/dogfooding-doc/test scope に一貫して反映されているか確認。
- G3 adapter rollout readiness:
  - adapter 配布、`iss-00050` 担当の残件 docs parity、host parity 証跡がそろっているか確認。
- G4 native artifact contract readiness:
  - native shim / manifest / installer sync-prune 契約が確定しているか確認。
- G5 native integration readiness:
  - orchestrator 委譲、manual test、docs closure がそろっているか確認。
- G9 final epic spec review:
  - E-AC closure と follow-up の明確化を確認。

## 品質ゲート
- test / observability / migration / docs:
  - `sync` / `validate` 通過。
  - installer/runtime 主要 tests 通過。
  - host 間 parity 記録。
  - docs parity 差分ゼロまたは意図差分の説明完了。
  - native artifact manual test 記録。

## ロールアウト / docs impact
- rollout order:
  - `iss-00049` -> `iss-00050` -> `follow-up-a` -> `follow-up-b`
- contract / docs refresh:
  - `iss-00049` で protocol contract surface の runtime / provider docs / dogfooding docs / tests を更新する。
  - `iss-00050` で adapter 配布と残件 parity / final review を完了する。
  - `follow-up-a` で host-native artifact 契約と installer sync/prune を追加する。
  - `follow-up-b` で integration / validation / docs closure を完了する。

## Issue readiness contract
- Issue に要求する最低条件:
  - 変更対象の責務境界が明示されている。
  - 観測コマンドと期待結果が plan/report に残る。
  - 次 issue への handoff 条件が明確。
  - native shim が thin shim であることを review 観点に含む。

## final exit contract
- E-AC closure:
  - E-AC-001..004 に対応する証跡が report に残る。
- integration / rollout complete:
  - protocol と adapter が両立し、host 間で実行導線が一致し、通常実行の第一選択が full-history になっていない。
  - orchestrator が host-native agent / subagent へ spec-dock 操作を委譲できる。
- docs impact resolved:
  - `iss-00049` 対象の protocol docs parity、`iss-00050` 対象の adapter/final parity、follow-up-a/b 対象の native artifact parity がそれぞれ完了し、final review が pass している。

## 依存 / ブロッカー
- D-001:
  - 既存 `.agents/skills` managed asset 配布機構の整合。
- D-002:
  - architecture-level invalid artifact prevention の follow-up（本 epic では非対応）。
- D-003:
  - OpenAI Codex / GitHub Copilot の host-native artifact 仕様変更が無いこと、または変更時に追随できること。

## 設計上の決定
- D-004:
  - host adapter metadata は `.agents/host-adapters/meta.json` を第一案ではなく採用決定とする。
  - `iss-00049` では artifact ごとの top-level metadata contract を固定する（`index.json`=`projection=current-future` / no new `source`、`index-all.json`=`projection=full-history` / no new `source`、`deps-issues.json`=`projection=open-issues-dependency-view` / provenance `source` 維持）。
- D-005:
  - `.agents/skills/*` を正本、`.codex/agents/*` / `.github/agents/*` を thin shim とする。
