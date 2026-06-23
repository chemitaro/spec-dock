---
種別: ADR（Architecture Decision Record）
ID: "20260623t074441z-adr"
タイトル: "Fixed Skill Kernel And Compiled Runbook Authority"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
親: ["epic-00224"]
authority: "accepted"
derived_from:
  - "20260623t074452z-disc-adr-decision-synthesis-after-issue-226-closure.md"
reflected_to:
  - "../design.md"
  - "../plan.md"
  - "../report.md"
---

# 20260623t074441z-adr Fixed Skill Kernel And Compiled Runbook Authority

## ADR 化基準
- hard to reverse: yes
- surprising without context: yes
- real tradeoff: yes
- ADR として残す理由:
  - Skill を状態別に生成・編集するのではなく、固定 kernel と runtime-compiled Runbook に authority を移す判断は、複数 Issue と将来の SpecDock workflow に波及する。
  - この判断を Issue-local に隠すと、後続 agent が Skill 本文を状態別に肥大化させる実装へ戻すリスクがある。

## 結論（Decision）
- Planning / execution Skill は固定 kernel とし、現在状態の手順本体を tracked policy と runtime state から `workflow next` / `workflow status` 相当の runtime command が compiled Runbook として生成する。
- 固定 kernel は「どの source を読むか」「runtime に現在手順を問い合わせること」「authority / freshness が不十分なら停止すること」だけを持つ。
- Generated Runbook は current Issue / phase / Assurance Profile / dependency state に応じて生成されるが、tracked source of truth ではない。tracked authority は canonical docs、policy fragments、Issue metadata、accepted ADR、source binding に置く。
- Runtime は Runbook を Markdown / JSON で返し、未選択 profile の完全手順を混ぜない。`lite_candidate` は手順削減の authority ではなく、`authorized_profile` だけが手順選択 authority になる。

## 背景（Context）
- SpecDock の workflow docs / skills は、軽量 Issue と重量 Issue の両方へ厳密な gate を要求できるようになっている一方、agent が毎回長い workflow 文書を読み解くと token / wall-clock cost が増える。
- Skill 本文を Issue 状態ごとに書き換える方式は、tracked Skill 差分、レビュー対象の肥大化、古い state への binding drift を生みやすい。
- Epic の目的は品質 gate を弱めることではなく、現在状態に必要な obligation だけを deterministic に提示することである。

## 選択肢（Options considered）
- Option A: Skill に全 profile / 全 phase の詳細手順を保持する。
  - Pros: runtime 実装は薄い。
  - Cons: Skill が肥大化し、軽量 task でも重い context を常に読む。状態別の stale 手順が混ざる。
  - 棄却理由: token waste の主原因を残し、今回の Epic 目的と逆行する。
- Option B: Issue start 時に Skill を生成・編集する。
  - Pros: agent が読む手順は短くできる。
  - Cons: tracked Skill 差分が発生し、state transition と Git diff が絡む。review / rollback が難しい。
  - 棄却理由: workflow state を code-like asset mutation にしてしまう。
- Option C: Skill を固定 kernel にし、runtime が compiled Runbook を返す。
  - Pros: tracked Skill を安定化しつつ、state-specific 手順だけを提示できる。
  - Cons: Runbook compiler / state resolver / projection test が必要。
  - 採用理由: authority と ergonomics の両立が最もよい。

## 判断理由（Rationale）
- SpecDock の source of truth は canonical docs / metadata / accepted decisions に置くべきであり、agent prompt の長大化や状態別 Skill mutation に authority を散らすべきではない。
- Runtime projection なら、generated output を ignored path に置き、source hash / policy version / active state を evidence として記録できる。
- MyPy / Ruff baseline はこの ADR の feature scope ではないが、compiler / state resolver / output model は typed contract を持つ必要がある。

## 影響（Consequences）
- Positive:
  - Skill 本文を安定化でき、Issue 切替による tracked Skill 差分を防げる。
  - Agent は current state に必要な obligation へすばやく到達できる。
  - Runbook output を snapshot / golden test しやすい。
- Negative / Debt:
  - Runtime に state resolver、Runbook compiler、projection renderer、freshness check が必要になる。
  - Generated output と tracked source の境界を明確にしないと、generated artifact を authority と誤読するリスクがある。
- 影響範囲:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`
  - `src/spec_dock/assets/install_root/.agents/skills/`
  - `spec-dock/docs/workflow_*.md`
  - Dogfooding mirror under `spec-dock/`
- 移行/ロールバック:
  - Legacy Issue は strict workflow docs fallback を使える。
  - Runbook compiler が失敗する場合は fail-closed し、manual strict workflow を案内する。
- Follow-ups:
  - `iss-00228` が runtime Runbook / fixed Skill kernel を実装する。

## 非目標（Non-goals）
- 全 workflow docs を削除しない。
- Issue 状態ごとに tracked Skill を生成しない。
- Generated Runbook を canonical source of truth にしない。

## 未確定事項（Open Questions）
- Markdown projection の細部、ignored generated path naming、snapshot file layout は `iss-00228` で決める。

## 参考（References）
- `requirement.md`
- `design.md`
- `plan.md`
- `20260623t074452z-disc-adr-decision-synthesis-after-issue-226-closure.md`
