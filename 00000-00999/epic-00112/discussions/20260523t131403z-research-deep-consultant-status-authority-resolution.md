---
type: research
source: deep-consultant
created_at: 2026-05-23T13:14:03+09:00
epic: epic-00112
topic: resolving status versus authority conflict
status: current
---

# Deep Consultant 追加分析: status と authority を分離する解決案

## 追加論点

初期分析では、draft canonical artifact model は有望とされた。一方、懐疑レビューでは `status: draft` だけでは危険とされた。この矛盾を解くため、追加で「canonical path」「status」「authority」「grants」の分離を分析した。

## 結論

採用すべきモデルは、単なる `status: draft` ではなく、次の 4 軸モデルである。

- canonical path: artifact の既定位置。最新統合案の所在地。
- status: lifecycle state。draft / in_review / ready_for_approval / approved / archived など。
- authority: decision force。proposed / approved / superseded / rejected。
- grants: downstream action に対する明示的な許可。

`design.md` / `plan.md` は canonical path に置いてよい。ただし、`authority: proposed` の間は実装根拠ではない。実装開始、issue ready、phase completion は `authority: approved` かつ該当 grants が true の場合だけ許可する。

## 推奨 frontmatter

```yaml
schema: spec-dock.artifact.v1
artifact: design
spec_id: epic-00112
status: draft
authority: proposed
canonical_role: latest_proposal
owner_role: main-orchestrator
draft_author_role: system-architect
promotion_required_by: main-orchestrator
grants:
  review_input: true
  planning_input: true
  design_baseline: false
  implementation_start: false
  issue_ready: false
  phase_completion: false
source_discussions:
  - discussions/...
evidence_ledger: discussions/evidence-adoption-ledger.md
approval:
  approved_by: null
  approved_at: null
  approved_revision: null
  promotion_record: null
```

`plan.md` では、承認済み design revision への依存を明示する。

```yaml
depends_on:
  design_revision: "<approved-design-hash>"
  design_authority: approved
```

## state table

許可する状態は whitelist にする。

| status | authority | 意味 | 実装根拠 |
|---|---|---|---|
| draft | proposed | 専門 author の作業中 draft | 不可 |
| in_review | proposed | review 中の候補 | 不可 |
| ready_for_approval | proposed | author 側は完了、main approval 待ち | 不可 |
| approved | approved | main promotion 済み | 可 |
| archived | superseded | 旧版 | 不可 |
| archived | rejected | 棄却 | 不可 |

## context-pack の分離

`context-pack` は purpose-aware にする。

- review purpose: proposed artifact を含めてよい。ただし非権威として明示する。
- planning purpose: proposed design を planning input として含めてもよいが、implementation baseline ではない。
- implementation purpose: approved plan と approved design のみ含める。
- finish / phase completion purpose: approved artifact と promotion record のみ含める。

## promotion gate

promotion では次を満たす必要がある。

- schema validation pass
- state table validation pass
- evidence adoption ledger に blocking item がない
- spec-reviewer final pass
- main orchestrator が promotion を実行
- approved revision または hash を記録
- promotion record を作成

## 判断

この解決案により、canonical draft の利点と未承認 artifact 誤用のリスクを両立できる。epic の設計は「read-only draft evidence」から「authority-aware delegated draft authoring」へ発展させる価値がある。ただし、authority-aware gate が整う前に canonical draft write を運用解禁してはいけない。
