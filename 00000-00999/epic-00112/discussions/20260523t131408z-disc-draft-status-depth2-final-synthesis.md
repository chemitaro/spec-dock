---
type: discussion
source: orchestrator
created_at: 2026-05-23T13:14:08+09:00
epic: epic-00112
topic: final synthesis for draft-status authoring and depth-2 delegation
status: current
---

# 統合レポート: draft-status authoring と depth=2 delegation の推奨ビジョン

## 背景

この epic の当初の出発点は、main orchestrator がすべての設計・計画を自分で書くのではなく、専門 agent に責務を委譲することだった。特に `system-architect` は設計書を、`implementation-planner` は実装計画書を作成する想定があった。

一方、現在の安全設計では、これらの専門 agent は read-only に近く、draft evidence を main orchestrator に返すだけになっている。このままだと、consultant と専門 author の違いが薄くなり、委譲による認知負荷削減と品質向上が十分に得られない。

## 統合結論

最終的に目指すべき状態は、次の hybrid model である。

- `requirement.md` は main orchestrator が所有する。
- `design.md` は `system-architect` が draft として実際に作成・更新する。
- `plan.md` は `implementation-planner` が draft として実際に作成・更新する。
- draft artifact は canonical path に置くが、`authority: proposed` の間は実装根拠ではない。
- main orchestrator だけが final ownership、approval、promotion を担う。
- child specialist は depth=2 で evidence/report を作るが、canonical artifact は編集しない。
- spec-reviewer preflight は advisory、final spec-reviewer は blocking として分離する。

## 重要な修正: status だけでは足りない

今回の多段階分析で最も重要な発見は、`status: draft` だけでは安全境界として弱いという点である。

`design.md` / `plan.md` という canonical path は、それ自体が強い source-of-truth signal を持つ。そのため、draft を canonical path に置くなら、artifact の状態を次の軸で分離する必要がある。

- `status`: lifecycle state。
- `authority`: decision force。
- `grants`: downstream action permission。
- `approval`: approved revision と promotion record。

推奨する draft state は次の形。

```yaml
status: draft
authority: proposed
grants:
  review_input: true
  planning_input: true
  design_baseline: false
  implementation_start: false
  issue_ready: false
  phase_completion: false
```

approved state は、main orchestrator promotion と final spec-reviewer pass によってのみ成立する。

## depth=2 の推奨設計

depth=2 は採用する。ただし、無制限 fan-out ではない。

許可するのは、親 authoring agent が evidence を増やすために leaf specialist を呼ぶ使い方である。

許可:

- repo analysis
- external research
- deep consultation
- trade-off analysis
- advisory preflight review

禁止:

- child が canonical artifact を編集する
- child が final approval する
- child が child を呼ぶ
- implementation agent を authoring child として呼ぶ
- peer authoring agent を child として呼ぶ

## evidence adoption ledger

depth=2 を採用するなら、子 agent の output をただ discussions に溜めるだけでは不十分。親 authoring agent が何を採用し、何を採用しなかったかを trace できる ledger が必要。

推奨 fields:

- source
- contributor_role
- claim
- disposition: adopted / partially_adopted / rejected / deferred / superseded
- target_artifact
- target_section
- rationale
- evidence_strength
- adopted_by
- reviewed_by
- blocking

## context-pack と lifecycle gate

`context-pack` と lifecycle command は authority-aware である必要がある。

- review context: proposed artifact を含めてよい。
- planning context: proposed design を含めてもよいが、非権威として明示する。
- implementation context: approved plan と approved design のみ含める。
- finish / phase completion: approved artifact と promotion record のみ根拠にする。

`authority: proposed` の artifact を実装開始や issue finish に使える状態にしてはいけない。

## 推奨 implementation roadmap

1. artifact frontmatter schema を導入する。
2. `status` / `authority` / `grants` / `approval` を required にする。
3. state table validator を追加し、不正な組み合わせを拒否する。
4. evidence adoption ledger を導入する。
5. context-pack を purpose-aware / authority-aware にする。
6. lifecycle gate が approved artifact revision だけを受け付けるようにする。
7. `system-architect` / `implementation-planner` に draft artifact write 権限を付与する。
8. child specialist の出力先を evidence/report に限定する。
9. final spec-reviewer と main promotion gate を実装する。
10. dogfooding pilot で draft authoring workflow を検証する。

## いまの epic への反映方針

現在の epic は、read-only draft evidence を中心に設計されている。これは安全側の初期案としては妥当だが、ユーザーが目指す「専門 agent による自律的な設計書・計画書作成」には届かない。

このため、今後の要件・設計・計画では、次の方向へ更新するのが望ましい。

- read-only evidence agent ではなく、draft authoring agent として再定義する。
- ただし、final authority は main orchestrator に残す。
- direct canonical write 解禁は、authority-aware gate 実装後に行う。
- Permission Profile は「draft artifact write + promotion deny」を目指す。
- depth=2 は evidence producer として限定的に許可する。

## 最終判断

ベストプラクティスは「専門 agent が actual `design.md` / `plan.md` の draft を作る。ただし、承認権限は持たない。子 specialist は evidence を作る。main orchestrator が final authority を持つ」である。

このモデルは、ユーザーの有限な認知資源を守りながら、専門 agent の自律性と品質向上を両立する。ただし、`status: draft` だけでは危険であり、`authority`、`grants`、approved revision、promotion record、authority-aware context-pack / lifecycle gate まで含めて初めて安全な設計になる。
