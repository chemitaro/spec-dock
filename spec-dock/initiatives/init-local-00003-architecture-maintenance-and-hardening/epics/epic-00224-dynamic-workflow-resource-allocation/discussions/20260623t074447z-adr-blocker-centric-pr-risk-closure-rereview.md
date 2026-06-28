---
種別: ADR（Architecture Decision Record）
ID: "20260623t074447z-adr"
タイトル: "Blocker Centric PR Risk Closure And Re Review"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-06-29"
親: ["epic-00224"]
authority: "accepted"
amended_by:
  - "20260628t154553z-adr"
derived_from:
  - "20260623t074452z-disc-adr-decision-synthesis-after-issue-226-closure.md"
reflected_to:
  - "../design.md"
  - "../plan.md"
  - "../report.md"
  - "20260628t154553z-adr-pr-observation-explicit-review-completion.md"
---

# 20260623t074447z-adr Blocker Centric PR Risk Closure And Re Review

## 変更履歴（Supersession / Amendment）

- 2026-06-29: `20260628t154553z-adr PR Observation Explicit Review Completion` により、blocker-centric closure の前提となる review completion 判定が明確化された。
- この ADR は「観測済み review finding をどう blocker / non-blocking として扱うか」を決める。Review worker が完了したかどうか、`completion_signal=none`、`review_completion_unknown`、timeout/resume semantics は `20260628t154553z-adr` を authority とする。
- `review_completion_unknown` は blocker disposition や merge-prepared evidence の前提として扱わないよう変更済み。
- completion artifact が current trigger boundary と expected head SHA に bind されていない場合、blocker-centric closure はまだ評価対象に入らない。timeout / wait_or_resume は review 不要の human gate ではなく、観測 budget 到達または再開待ちの状態として扱うよう変更済み。

## ADR 化基準
- hard to reverse: yes
- surprising without context: yes
- real tradeoff: yes
- ADR として残す理由:
  - PR merge preparedness を comment zero ではなく verified blocker zero とする判断は、review cycle の cost と safety を直接左右する。

## 結論（Decision）
- Merge preparedness は `verified blocker zero + required CI + review coverage` で判断し、comment zero では判断しない。
- Valid P0 / P1 finding は blocker である。
- P2 / P3 finding は default non-blocking とし、no-action、follow-up、docs note、future issue のいずれかで disposition できる。
- P2 は protected domain に触れ、かつ deterministic machine evidence がある場合だけ validated blocker に promotion できる。Reviewer assertion alone is not machine evidence.
- Review-exempt local delta は、reviewed production behavior または trusted policy semantics に影響しないこと、deterministic local verification があること、diff evidence が記録されることを満たす場合に限る。
- Behavior-affecting code、migration、public contract、security/privacy、review policy の変更は material delta とし、external review が obligation に含まれる場合は fresh review を必要とする。
- Stagnation は human gate であり、loop count だけで risk acceptance しない。

## 背景（Context）
- AI review / PR observation では、P2 / P3 の提案まで全て直すと過剰な repair / re-review loop になりやすい。
- 一方で P2 に分類された指摘でも、protected domain と機械的証拠が揃う場合は実質 blocker になり得る。
- SpecDock は「見つかったコメントをゼロにする」ことではなく、「merge を止めるべき risk を閉じる」ことを delivery gate にする必要がある。

## 選択肢（Options considered）
- Option A: comment zero を merge gate にする。
  - Pros: 単純で説明しやすい。
  - Cons: 非本質 P2/P3 で loop が増える。
  - 棄却理由: 軽量 / 標準 task の waste を増やす。
- Option B: P0/P1 だけを常に blocker とし、P2 は無視する。
  - Pros: loop は短い。
  - Cons: protected domain の P2 を取りこぼす。
  - 棄却理由: safety が粗い。
- Option C: blocker-centric disposition にし、protected P2 だけ machine evidence で promotion する。
  - Pros: safety と cost の balance がよい。
  - Cons: protected domain / evidence の判定 model が必要。
  - 採用理由: Epic の resource allocation 目的に合う。

## 判断理由（Rationale）
- Severity label だけでは merge risk を十分に表現できない。domain と evidence を組み合わせる必要がある。
- P2/P3 を default non-blocking にすることで、AI review の改善提案をすべて修正対象にする waste を避けられる。
- Static analysis / schema / CI が deterministically enforce する事項は、その gate の failure として扱い、reviewer comment loop へ重複させない。

## 影響（Consequences）
- Positive:
  - PR repair loop が blocker に集中する。
  - P2 の扱いを deterministic evidence と protected domain によって説明できる。
  - Human gate と risk acceptance を混同しない。
- Negative / Debt:
  - Finding disposition schema、protected-domain taxonomy、machine evidence binding が必要。
  - Material delta 判定を誤ると review bypass になるため、fail-closed default が必要。
- 影響範囲:
  - PR observation / review finding ingestion
  - blocker engine
  - re-review trigger
  - merge-prepared evidence
- 移行/ロールバック:
  - Blocker engine が判定不能な場合は human gate。
  - Materiality 不明な delta は material として扱う。
- Follow-ups:
  - `iss-00232` が blocker-centric PR repair / re-review を実装する。

## 非目標（Non-goals）
- Auto-merge は扱わない。
- comment zero を required gate にしない。
- loop count だけで risk acceptance しない。

## 未確定事項（Open Questions）
- protected-domain taxonomy、fingerprint、material-delta 判定の細部は `iss-00232` で確定する。ただし blocker-centric / machine evidence / no loop-count acceptance は固定済み。

## 参考（References）
- `design.md`
- `plan.md`
- `20260623t074452z-disc-adr-decision-synthesis-after-issue-226-closure.md`
