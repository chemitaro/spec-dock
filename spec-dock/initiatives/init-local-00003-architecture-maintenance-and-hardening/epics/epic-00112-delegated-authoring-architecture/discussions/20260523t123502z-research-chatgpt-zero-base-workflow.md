---
type: research
source: chatgpt-pro
created_at: 2026-05-23T12:35:02+09:00
epic: epic-00112
topic: zero-base delegated authoring workflow
status: current
thread_url: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a119cfd-f08c-83aa-ae62-3eb3ad9c6cf8
---

# ChatGPT Pro Research: Zero-Base Delegated Authoring Workflow

## source_note

This report summarizes a ChatGPT Pro thread created through Chrome in the Codex-only ChatGPT Project. It is external analytical input and should not be treated as independently verified repo truth.

## executive_verdict

ChatGPT Pro の結論は、`system-architect` / `implementation-planner` は read-only adviser 固定ではなく delegated draft writer にすべき、というものだった。

ただし、初期・標準モードでは canonical `design.md` / `plan.md` を直接編集する writer にすべきではない。

推奨:

- 専門 subagent は artifact の一次ドラフト作成者。
- main orchestrator は canonical artifact の所有者・統合者・昇格責任者。
- `spec-reviewer` は独立 reviewer。

したがって二択ではなく、mode-based / staged authoring が妥当。

| Mode | 位置づけ | 推奨 |
| --- | --- | --- |
| M0: Read-only adviser | コメント、論点、レビュー補助のみ | 常時デフォルトにするには弱い |
| M1: Draft writer | `design.md` / `plan.md` 相当の complete candidate を作る。ただし canonical は編集しない | 理想の標準形 |
| M2: Branch / draft-path writer | 限定パス、専用 worktree、draft evidence path にだけ書く | 成熟後に導入可 |
| M3: Direct canonical writer | canonical `design.md` / `plan.md` を自律編集 | 原則非推奨 |

## original_intent

初期リサーチの「設計書と実装計画書は専任サブエージェントを一次作成者にした方がよい」は、専門 subagent が完成度の高い candidate artifact を作るべきという意味に読むのが自然。

一方、role skill contract は次を同時に置いている。

- `system-architect`: approved `requirement.md` から `design.md` candidate を作る。
- forbidden: `design.md` を直接 modify しない。
- `implementation-planner`: approved `requirement.md` / `design.md` から `plan.md` candidate を作る。
- forbidden: `plan.md` を直接 modify しない。

これは矛盾ではない。正しくは、subagent は artifact content の author であり、canonical file の mutation authority は main orchestrator である、という分離である。

## adviser_vs_writer

### read-only adviser 固定

安全だが、delegated authoring architecture としては弱い。

- canonical 誤編集はない。
- review independence は守りやすい。
- しかし main orchestrator が結局 `design.md` / `plan.md` を自分で再構成する。
- consultant と `system-architect` / `implementation-planner` の差が小さくなる。
- design / plan は断片的助言よりも全体整合した文書構造が重要。

### direct canonical writer

短期 throughput は上がるが、architecture risk が大きい。

- 書けることと承認されたことが混同される。
- user dialogue の反映責任が曖昧になる。
- unresolved question を勝手に解決しやすい。
- phase promotion と file mutation が混ざる。
- main orchestrator が integrator なのか observer なのか曖昧になる。

### delegated draft writer

最適な中間形。

- subagent は単なる助言者ではなく、`design.md` / `plan.md` としてそのまま読める candidate を作る。
- canonical 反映は main orchestrator が行う。
- draft が悪い場合は捨てられる。
- auditability と review independence を維持しやすい。

## cognitive_load_analysis

人間ユーザーの認知が有限であるなら、目標は人間に全部確認させることではない。人間と orchestrator が確認すべき対象を、構造化された少数の差分・判断点に圧縮すること。

adviser-only は、main orchestrator に authoring load が残る。

draft writer 方式では、専門 subagent が次の形まで落とす。

- 完成形に近い `design.md` candidate
- 完成形に近い `plan.md` candidate
- requirements traceability
- assumptions
- rejected alternatives
- risks
- open questions
- promotion checklist

main orchestrator と人間の仕事は、白紙から書くことではなく、candidate を評価し、差分を選び、昇格することになる。

## best_practice

ChatGPT Pro の best practice は、「read-only adviser ではなく non-canonical delegated draft writer。ただし canonical `design.md` / `plan.md` の直接編集権限は main orchestrator に残す」である。

実装上の示唆:

- role description は `adviser` ではなく `delegated draft author` とする。
- 初期 Epic では canonical direct write を許可しない。
- runtime read-only でも semantic writer にする。
- write-capable 化するなら draft path から始める。
- canonical promotion を明示的な operation にする。
- depth=2 writer chain は避け、read-only specialist に限定する。
- M2 への移行条件を gate 化する。

## final_recommendation

最終的な best practice は、read-only adviser ではなく non-canonical delegated draft writer。ただし canonical `design.md` / `plan.md` の直接編集権限は main orchestrator に残す、という設計である。

この判断は architecture 上の推論であり、実運用で確定するには、同一 requirement に対して adviser-only と draft-writer を比較し、orchestrator 編集時間、review findings 数、human clarification 数、後続 implementation defect 数を測るのがよい。

