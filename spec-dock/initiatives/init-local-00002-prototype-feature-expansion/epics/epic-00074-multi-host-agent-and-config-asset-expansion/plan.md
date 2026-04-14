---
種別: 計画書（Epic）
ID: "epic-00074"
タイトル: "Multi host agent and config asset expansion"
関連GitHub: ["#74"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-04-15"
依存: ["requirement.md", "design.md"]
親: ["init-local-00002"]
---

# epic-00074 Multi host agent and config asset expansion — 計画（Issue / Order）

## この計画で閉じる E-RQ / E-AC
- E-RQ:
  - E-RQ-001
  - E-RQ-002
  - E-RQ-003
  - E-RQ-004
  - E-RQ-005
  - E-RQ-006
  - E-RQ-007
  - E-RQ-008
- E-AC:
  - E-AC-001
  - E-AC-002
  - E-AC-003
  - E-AC-004

## Issue 方針
- single-issue principle:
  - 現在の前提では、既存 `install_root` authority、installer sync/prune、host-native asset layout がすでに存在し、本 epic の主作業は「新しい managed files を正しい場所へ追加し、既存 installer で配布できるようにすること」に閉じている
  - そのため foundation contract、Codex、GitHub Copilot を別 issue に分けず、1 implementation issue の中で asset 配置、metadata 更新、tests、docs、validation をまとめて完結させる
  - 複数 issue へ分けるのは、新しい installer mechanism や runtime protocol 変更が必要になった場合に限る
- current assumption:
  - `epic-00067` completed groundwork と `epic-00048` completed baseline の上で additive change として閉じる

## Issue 一覧
- planned-issue-01-multi-host-agent-and-config-asset-install:
  - 目的:
    - 既存 installer foundation の上で Codex bootstrap `config.toml`、Codex agents、GitHub Copilot agents、shared skills を追加し、multi-host managed asset delivery を一度に成立させる
  - deliverable:
    - Codex main-agent bootstrap `config.toml`
    - Codex `.codex/agents/*.toml`
    - GitHub Copilot `.github/agents/*.agent.md`
    - shared `.agents/skills/**`
    - 必要な metadata / docs / tests / temp repo validation evidence
  - closes:
    - E-RQ-001
    - E-RQ-002
    - E-RQ-003
    - E-RQ-004
    - E-RQ-005
    - E-RQ-006
    - E-RQ-007
    - E-RQ-008
    - E-AC-001
    - E-AC-002
    - E-AC-003
    - E-AC-004
  - depends on:
    - `epic-00067` completed groundwork
    - `epic-00048` completed baseline

## 統合チェックポイント
- G1 decomposition review:
  - `epic-00074` が feature expansion に留まり、`epic-00067` の authority cleanup と `epic-00048` の completed baseline を reopen せず、単一 issue で完結できる変更範囲に収まっていることを確認する
- G2 foundation readiness:
  - managed host pack contract が Codex bootstrap config、host-specific custom agents、shared skills を扱え、current / obsolete managed path safety が docs/tests に落ちていることを確認する
- G3 Codex rollout readiness:
  - Codex pack が thin delegation boundary を壊さず、main agent config が orchestrator responsibility を担う構成で clean install と update rollout の両方に成立することを確認する
- G4 Copilot rollout readiness:
  - GitHub Copilot pack が `orchestrator` primary + `spec-manager` sibling specialist の構成で current managed file set / obsolete managed file set / unknown custom preserve の 3 条件を満たすことを確認する
- G9 final epic spec review:
  - 単一 issue 内で cross-host parity、future host extensibility note、rollout checkpoint 完了が揃い、epic close-out 可能であることを確認する

## 品質ゲート
- test / observability / migration / docs:
  - 単一 issue 内で managed ownership / prune safety の unit/integration evidence を持つ
  - 同一実装内で Codex と GitHub Copilot の clean install / update を確認する
  - final close-out 前に provider docs / dogfooding docs / tests / managed metadata の整合を確認する

## ロールアウト / docs impact
- rollout order:
  - 1 issue の中で metadata / file placement / tests / docs をまとめて更新する
  - 実装順は Codex と GitHub Copilot を分けてもよいが、完了条件は cross-host validation を含む単一 close-out とする
- contract / docs refresh:
  - host pack ごとの managed asset ownership を docs へ追加する
  - install/update guidance、managed/unmanaged boundary、future host extension note を provider/dogfooding 双方へ反映する
  - parent initiative plan ではこの epic を concrete portfolio item として管理する

## Validation / Rollout checkpoints
- checkpoint-01:
  - implementation boundary review
  - 既存 installer foundation のまま実装でき、mechanism 追加が不要であることを確認する
- checkpoint-02:
  - metadata / asset placement validation
  - Codex bootstrap `config.toml`、Codex agents、GitHub Copilot agents、shared skills の配置先と ownership が矛盾していない
- checkpoint-03:
  - Codex and Copilot clean install / update validation
  - Codex は main config で orchestrator responsibility を担い、GitHub Copilot は `.github/agents/orchestrator.agent.md` を primary にした構成で正しく配置される
- checkpoint-04:
  - cross-host prune safety validation
  - obsolete managed files だけが prune され、unknown custom files は保持される
- checkpoint-05:
  - final docs parity / dogfooding verification
  - future host extensibility note と compatibility boundary が close-out evidence に残る

## Issue readiness contract
- Issue に要求する最低条件:
  - `epic-00067` prerequisite と `epic-00048` baseline の扱いが明文化されている
  - managed/unmanaged boundary と prune safety の確認方法が書かれている
  - docs/tests/dogfooding evidence を issue 自身で回収する計画がある
  - asset 追加で閉じる範囲と、mechanism 追加が必要になった場合の再分割条件が書かれている

## final exit contract
- E-AC closure:
  - E-AC-001 は Codex host pack delivery と validation で閉じる
  - E-AC-002 は GitHub Copilot host pack delivery と update/prune evidence で閉じる
  - E-AC-003 は single issue 内の managed asset contract と future host extensibility review で閉じる
  - E-AC-004 は final docs parity / dogfooding / rollout checklist で閉じる
- integration / rollout complete:
  - Codex では main agent bootstrap config と subagent/custom agent assets、GitHub Copilot では `.github/agents/` 配下の subagent/custom agent assets が managed deployment 可能である
  - update path の obsolete managed cleanup と unknown custom preserve が確認済みである
- docs impact resolved:
  - provider docs、dogfooding docs、initiative portfolio、tests が同じ epic boundary を表現している

## 依存 / ブロッカー
- D-001:
  - `epic-00067 Installed layout aligned asset source structure for agent tooling`
- D-002:
  - `epic-00048 Agent facing interface hardening and host adapter scaffolding`
- D-003:
  - Codex CLI / GitHub Copilot の host-native config / custom agent discovery contract

## 未確定事項
- なし:
  - 現在の前提では single issue execution plan で固定する
