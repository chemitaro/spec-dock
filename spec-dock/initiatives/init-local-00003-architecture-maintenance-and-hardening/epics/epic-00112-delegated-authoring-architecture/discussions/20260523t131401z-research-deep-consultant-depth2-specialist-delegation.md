---
type: research
source: deep-consultant
created_at: 2026-05-23T13:14:01+09:00
epic: epic-00112
topic: depth-2 specialist delegation
status: current
---

# Deep Consultant 調査: authoring agent が子 specialist を使う depth=2 設計

## 問い

`system-architect` や `implementation-planner` が、自分だけで draft を作るのではなく、`repo-analyst`、`researcher`、`consultant`、`deep-consultant`、`spec-reviewer` などへ調査・分析・事前レビューを依頼できるようにするべきか。現在の depth=1 を維持するべきか、bounded depth=2 を採用するべきか。

## 結論

bounded depth=2 は採用候補として有効。ただし、子 agent は evidence producer に限定し、canonical artifact の編集権限を持たせない。

depth=2 の価値は、親 authoring agent の代筆ではなく、証拠面の拡張にある。親 authoring agent は、子 specialist の出力を吟味し、採用・不採用・保留を明示した上で `design.md` / `plan.md` の draft に反映する。

## 許可する delegation graph

- `system-architect -> repo-analyst`
- `system-architect -> researcher`
- `system-architect -> consultant`
- `system-architect -> deep-consultant`
- `system-architect -> spec-reviewer` as advisory preflight
- `implementation-planner -> repo-analyst`
- `implementation-planner -> researcher`
- `implementation-planner -> consultant`
- `implementation-planner -> deep-consultant`
- `implementation-planner -> spec-reviewer` as advisory preflight

## 禁止する graph

- 子 agent からさらに子 agent を呼ぶ depth=3。
- 子 specialist が `design.md` / `plan.md` / `requirement.md` を編集すること。
- `dev-coder`、patch 作成 agent、test 実行 agent、deploy agent を authoring child として呼ぶこと。
- `system-architect -> implementation-planner` や `implementation-planner -> system-architect` のような peer authoring delegation。
- 子 `spec-reviewer` に final gate authority を与えること。

## 推奨 cap

- max_depth: 2
- child は leaf-only
- 1 parent pass あたりの parallel child calls: 通常 3 まで
- 1 artifact あたりの child calls: 通常 6 まで
- deep-consultant: 1 artifact あたり 1 回を原則
- preflight review loop: 2 回まで
- parent draft iteration: 3 回までで main orchestrator へ handoff

## evidence の扱い

子 agent の出力は canonical artifact に直接混ぜない。まず structured evidence report として discussions または evidence path に保存する。

親 authoring agent は、draft artifact へ反映する際に evidence adoption ledger を更新する。

ledger は少なくとも次を持つ。

- source
- contributor_role
- claim
- disposition: adopted / partially_adopted / rejected / deferred / superseded
- target_section
- rationale
- evidence_strength
- adopted_by
- reviewed_by
- blocking

## 判断

高品質な draft を効率良く作るには bounded depth=2 が有効。ただし、depth=2 を権限拡張として扱うと責任が拡散する。採用するなら「子 agent は evidence producer、親 authoring agent が draft author、main orchestrator が final owner」という責任分界を固定する。
