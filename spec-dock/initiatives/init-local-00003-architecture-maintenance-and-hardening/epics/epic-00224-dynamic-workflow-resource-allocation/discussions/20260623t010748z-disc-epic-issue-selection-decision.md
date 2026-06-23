# Epic / Issue 選択判断

## 採用判断

**新規 Epic + 複数 Issue**を採用する。

親 Initiative:

```text
init-local-00003-architecture-maintenance-and-hardening
```

前提 Epic:

```text
epic-00158-agent-workflow-pdca-hardening
```

## 単一 Issue を採用しない理由

本変更は次の独立した責務境界を横断する。

- Assurance Contract と分類 policy
- runtime workflow state
- compiled runbook
- planning artifact composer
- step-level assurance と agent routing
- managed GitHub Codex review trigger
- PR blocker / repair / re-review policy
- installer、dogfooding mirror、legacy migration、observability

一つの Issue にすると、runtime、CLI、skill、template、GitHub write boundary、PR merge-prepared semantics が同じ差分に入り、次の問題が生じる。

- rollback 単位が大きすぎる
- PR review が巨大化する
- 中間状態を独立検証できない
- 一つの failure が全機能を block する
- provider source / dogfooding mirror parity の確認範囲が過大になる
- Issue の「最小実装単位」としての境界を失う

## 既存 Epic 00158 へ直接追加しない理由

`epic-00158` は、skills が first-read workflow spine、docs が詳細、templates が scaffold を所有する first-wave の context-surface 設計を正本化している。

本変更では、その成果を前提にしつつ、次の新しい設計の背骨を導入する。

- fixed Skill kernel
- runtime-compiled current runbook
- tracked Assurance Contract
- issue / step ごとの adaptive obligations
- trusted base-SHA review policy
- blocker-centric PR risk closure

これは単なる follow-up Issue ではなく、workflow authority、state、runtime contract、rollout 順を新しく定義する。既存 Epic の履歴と受け入れ条件を後から肥大化させず、前提 Epic として参照する方が監査性と完了判定が明確になる。

## Epic の Assurance

```yaml
assurance_profile: strict
complexity_tier: deep
```

理由:

- public CLI と generated state contract を変更する
- canonical artifact generation に関わる
- GitHub comment write と review observation を変更する
- merge-prepared 判定に影響する
- installer / provider / dogfooding mirror を横断する
- legacy workflow との compatibility が必要

Critical にはしない。最終 merge は引き続き人間判断であり、本 Epic 自身が production credential、payment、PII を直接処理しないため。ただし review-policy trust boundary と merge-prepared predicate は Strict 内の最重要 gate とする。
