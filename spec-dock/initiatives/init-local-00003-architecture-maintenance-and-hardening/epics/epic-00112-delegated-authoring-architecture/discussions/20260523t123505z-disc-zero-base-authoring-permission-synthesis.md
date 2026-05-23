---
type: synthesis
source: codex
created_at: 2026-05-23T12:35:05+09:00
epic: epic-00112
topic: zero-base authoring permission synthesis
status: current
inputs:
  - 20260522t120437z-research-delegated-authoring-source-architecture-report.md
  - 20260522t120437z-01-research-consultant-analysis-delegated-authoring-rollout.md
  - 20260522t231450z-03-research-chatgpt-pro-delegated-authoring-deep-analysis.md
  - 20260523t123500z-research-deep-consultant-zero-base-writer-analysis.md
  - 20260523t123501z-research-deep-consultant-skeptical-writer-risk.md
  - 20260523t123502z-research-chatgpt-zero-base-workflow.md
  - 20260523t123503z-research-chatgpt-initial-research-reinterpretation.md
  - 20260523t123504z-research-chatgpt-safe-writer-harness.md
---

# Synthesis: Zero-Base Authoring Permission Analysis

## executive_decision

ゼロベースの結論は、`system-architect` / `implementation-planner` を単なる read-only adviser に留めるべきではない、というもの。

ただし、初期標準として canonical `design.md` / `plan.md` を直接編集する writer にするべきでもない。

最適な定義は次。

> `system-architect` / `implementation-planner` は、`design.md` / `plan.md` の一次候補著者である。  
> ただし、canonical artifact の直接編集者・所有者・昇格責任者ではない。

つまり、核心は「read-only か write-capable か」ではなく、次の分離である。

- content authorship: 専門 subagent が担う。
- file mutation authority: 初期標準では main orchestrator が担う。
- canonical ownership: main orchestrator が担う。
- final review: independent `spec-reviewer` と main-owned gate が担う。

## original_research_finding

過去リサーチの出発点は、ユーザーの認識通り、設計書と実装計画書の一次作成を専門 subagent に委譲する構想だった。

`20260522t120437z-research-delegated-authoring-source-architecture-report.md` は明確に次を述べている。

- 「設計書と実装計画書は、専任サブエージェントを一次作成者にした方がよい」
- 要件定義書は main orchestrator + human。
- 設計書は `system-architect`。
- 実装計画書は `implementation-planner`。
- レビューは independent `spec-reviewer`。
- ただし main orchestrator は仕様の所有者・対話責任者・統合責任者・フェーズ昇格責任者として残る。

一方で、初期 ChatGPT deep analysis の role skill contract は、`system-architect` に `Produce a draft design.md candidate` を求めつつ、`Modify design.md directly` を禁止していた。`implementation-planner` も同様に `Produce a draft plan.md candidate` としながら、`Modify plan.md directly` を禁止していた。

これは矛盾ではない。

正しい読みは、「subagent は一次候補著者であり、main orchestrator は canonical artifact writer / owner / integrator / promoter である」という分離である。

## why_adviser_only_is_insufficient

read-only adviser 固定は安全だが、今回の目的には弱い。

問題:

- `system-architect` / `implementation-planner` と `consultant` の差が曖昧になる。
- main orchestrator が結局 `design.md` / `plan.md` を再著述する。
- 専門 agent の深い分析が canonical artifact に変換される過程で文脈落ちする。
- 人間と main orchestrator は長い助言を読み、採用部分を選び、文書構造に再編する必要がある。
- 「人間の有限な認知」を節約するという harness engineering の目的に対して非効率。

したがって、read-only であっても `adviser` ではなく `draft-candidate author` として扱う必要がある。

## why_direct_canonical_writer_is_too_risky

直接 canonical writer 方式には重大なリスクがある。

- file に書けたことと、承認されたことが混同される。
- design / plan が後続実装を拘束する契約であるため、誤った canonical 化のコストが高い。
- requirement gap や design gap を subagent が silent assumption として埋め込みやすい。
- author が自分の artifact を正当化する立場になり、review independence が弱まる。
- `requirement.md` 変更、`design.md` 変更、`plan.md` 変更の stale / drift 管理が難しくなる。
- Permission Profile は有用だが、責任境界や判断権限を保証しない。

したがって、canonical `design.md` / `plan.md` direct write は初期標準にしない。

## preferred_model

推奨モデルは、non-canonical delegated draft writer である。

| Artifact | Primary content author | Canonical owner | Final promoter |
| --- | --- | --- | --- |
| `requirement.md` | main orchestrator + human | main orchestrator | main orchestrator |
| `design.md` | system-architect | main orchestrator | main orchestrator |
| `plan.md` | implementation-planner | main orchestrator | main orchestrator |
| review evidence | spec-reviewer | main orchestrator records | main orchestrator |

このモデルでは、`system-architect` / `implementation-planner` は次を出す。

- complete candidate content
- section-by-section replacement candidate
- unified diff candidate
- traceability map
- assumptions
- unresolved questions
- rejected alternatives
- risks
- reviewer handoff notes
- promotion checklist

そして main orchestrator は次を担う。

- candidate の採用 / 不採用 / 部分採用
- canonical docs への反映
- user dialogue への戻し
- phase promotion
- final reviewer gate
- report evidence / ledger

## permission_recommendation

権限は段階化する。

### Phase 0: read-only semantic writer

- sandbox は read-only のまま。
- ただし role semantics は adviser ではなく writer。
- subagent は `design.md` / `plan.md` の promotion-ready candidate を全文または diff 形式で返す。
- 現行の安全性を保ちながら、consultant との差を明確にする。

### Phase 1: non-canonical draft-path writer

- Permission Profile probe 後に、task-specific draft zone だけ write 許可する。
- 例:
  - `.spec-dock/drafts/<node-id>/<task-id>/system-architect/design.candidate.md`
  - `.spec-dock/drafts/<node-id>/<task-id>/implementation-planner/plan.candidate.md`
  - active target `discussions/**`
- canonical `requirement.md` / `design.md` / `plan.md` は writer から write 不可。
- implementation code、tests、`.codex/**`、workflow files、secrets、GitHub mutation は禁止。

### Phase 2: patch writer

- subagent が canonical doc に対する patch candidate を生成する。
- apply は main orchestrator。
- diff gate / preflight review / final review を必須にする。

### Phase 3: guarded canonical write trial

- これは標準 route ではなく、低リスク条件が揃った場合の後続実験。
- 新規ファイル作成、単一 active issue、requirement reviewer pass 済み、diff gate clean、rollback 可能などに限定する。
- final promotion は依然として main orchestrator owned。

## minimum_harness

write-capable draft writer へ進むには、最低限次が必要。

1. Task manifest
   - role, phase, target, input hashes, allowed write paths, forbidden paths, output contract, fallback を固定する。

2. Resolved active path
   - `spec-dock/active/...` symlink を直接信頼せず、realpath と hash を固定する。

3. Role-scoped write path
   - task-specific draft zone のみ write。
   - canonical docs と code は deny。

4. Deterministic diff gate
   - path / hash / scope / schema を LLM ではなく deterministic に検証する。

5. Preflight review
   - authoring agent が `spec-reviewer` を呼ぶ場合も advisory preflight のみ。

6. Final independent review
   - main orchestrator が canonical docs と diff に対して final review を所有する。

7. Discussion / ledger
   - candidate、source hashes、review findings、promotion decision、rejected portions を保存する。

8. Rollback / fallback
   - probe failure、diff gate failure、hash mismatch、review failure で read-only mode に戻る。

## depth2_and_specialists

depth=2 は read-only specialist に限定する。

Allowed:

- `system-architect -> repo-analyst`
- `system-architect -> researcher`
- `system-architect -> consultant`
- `system-architect -> deep-consultant`
- `system-architect -> spec-reviewer` as preflight
- `implementation-planner -> repo-analyst`
- `implementation-planner -> researcher`
- `implementation-planner -> consultant`
- `implementation-planner -> deep-consultant`
- `implementation-planner -> spec-reviewer` as preflight

Denied:

- authoring agent -> `dev-coder`
- authoring agent -> write-capable authoring agent
- child specialist -> grandchild
- recursive writer chain

## how_to_update_current_epic

現在の canonical epic は「draft-only」「main-owned canonical integration」を明確にしており、安全側として妥当である。

ただし、次の点を更新した方がよい。

1. `draft evidence` という語を `promotion-ready draft candidate` として再定義する。
2. `system-architect` / `implementation-planner` を `adviser` ではなく `delegated draft author` と明記する。
3. read-only runtime でも semantic writer であることを明記する。
4. 将来の write-capable delegation は `canonical writer` ではなく `non-canonical draft-path writer` から始めると明記する。
5. Permission Profile は security boundary ではなく workflow guard と明記する。
6. task manifest / resolved active path / role-aware diff gate / preflight review / final review / rollback を後続要件として追加する。

## final_recommendation

最終結論:

- `system-architect` / `implementation-planner` は単なる read-only adviser に留めない。
- ただし canonical `design.md` / `plan.md` の直接編集者にもしない。
- 初期標準は read-only semantic writer、つまり promotion-ready draft candidate author とする。
- 次段階で non-canonical draft-path writer を導入する。
- canonical promotion と final review は main orchestrator owned のまま維持する。

これが、専門 subagent の価値、有限な人間認知、source-of-truth discipline、review independence のすべてを最もよく両立する。
