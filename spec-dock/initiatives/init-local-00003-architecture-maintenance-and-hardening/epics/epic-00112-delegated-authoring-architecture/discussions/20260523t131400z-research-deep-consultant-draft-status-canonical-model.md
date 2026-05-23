---
type: research
source: deep-consultant
created_at: 2026-05-23T13:14:00+09:00
epic: epic-00112
topic: draft-status canonical artifact model
status: current
---

# Deep Consultant 調査: draft 状態の canonical artifact を専門 author が作成する設計

## 問い

`system-architect` が `design.md` を、`implementation-planner` が `plan.md` を実際に作成・更新する。ただし、それらは `draft` として扱い、最終的な承認・所有権・phase promotion は main orchestrator が保持する。このモデルは、discussions 配下にメモを残すだけのモデルよりも、ソフトウェア開発ワークフローとコンテキストエンジニアリングの観点で優れているか。

## 結論

採用候補として妥当。ただし、`status: draft` だけを安全境界にしてはいけない。

推奨は次の分離である。

- canonical path: 最新の統合案が置かれている場所。
- draft status: まだ承認されていない作業状態。
- final authority: 実装開始、issue 完了、phase 完了の根拠として使える権威。

この分離があるなら、`design.md` / `plan.md` を専門 author が draft として作成するモデルは、discussions に非正規メモを残すだけのモデルよりも発見性、レビュー性、差分追跡、stale 検出、認知負荷の面で優れる。

## 理由

discussions-only モデルでは、専門 agent の出力が「どれが現在案なのか」「どこまで採用済みなのか」「main orchestrator が何を統合したのか」を追いにくい。結果として、main orchestrator と人間ユーザーの認知負荷が増え、重要な設計判断がメモ群に分散する。

一方で canonical file に draft として反映するモデルでは、現在案が常に `design.md` / `plan.md` に集約される。レビュー対象も明確になり、差分レビューと spec-reviewer の評価対象が安定する。

ただし canonical path は強い権威シグナルを持つため、draft をそのまま downstream が実装根拠として扱う危険がある。したがって、draft canonical artifact を採る場合は lifecycle command、context-pack、review gate、phase gate が draft を非権威として扱う必要がある。

## 必須ガード

- `system-architect` は `design.md` の draft 作成・更新のみ可能。
- `implementation-planner` は `plan.md` の draft 作成・更新のみ可能。
- 両者は承認状態への promotion を行えない。
- `draft` artifact は issue finish、implementation start、phase completion の根拠にできない。
- main orchestrator が final review と promotion を所有する。
- spec-reviewer の final pass が promotion の前提になる。
- 権限境界は agent instruction だけでなく、Permission Profile、diff gate、lifecycle validation で守る。

## 推奨 frontmatter

```yaml
status: draft
authority: proposed
owner_role: main-orchestrator
draft_author_role: system-architect
promotion_required_by: main-orchestrator
source_requirement_revision: "<hash-or-revision>"
evidence_index:
  - discussions/...
approval:
  approved_by: null
  approved_at: null
  approved_revision: null
```

`plan.md` では `source_design_revision` も必須にする。

## 判断

「専門 author が canonical artifact の draft を作る」は、目標に合っている。ただし、この epic の実装計画では、draft を canonical path に置くことより先に、authority-aware な validation と context-pack 分離を設計・実装する必要がある。
