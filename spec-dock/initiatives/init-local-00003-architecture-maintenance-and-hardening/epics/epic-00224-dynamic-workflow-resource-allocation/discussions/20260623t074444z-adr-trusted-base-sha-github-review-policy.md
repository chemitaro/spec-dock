---
種別: ADR（Architecture Decision Record）
ID: "20260623t074444z-adr"
タイトル: "Trusted Base SHA GitHub Review Policy"
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

# 20260623t074444z-adr Trusted Base SHA GitHub Review Policy

## ADR 化基準
- hard to reverse: yes
- surprising without context: yes
- real tradeoff: yes
- ADR として残す理由:
  - PR head の変更に review policy を委ねない判断は security / governance boundary であり、PR review と blocker closure の複数 Issue が依存する。

## 結論（Decision）
- Codex PR review policy は PR base SHA の `.github/codex/review-policy.md` からのみ読む。
- Runtime は review trigger body を deterministic に合成する。caller-provided body、任意 endpoint、任意 path、raw `gh` args、PR head 側 policy は受け付けない。
- Trigger evidence には base SHA、head SHA、policy path、policy hash、generated body hash、review target を記録する。
- External review が required で、base policy が missing / invalid / oversized / unreadable の場合は human gate とし、head policy への fallback はしない。
- Findings already deterministically enforced by required lint, formatting, type checking, schema validation, or CI should be handled by those gates, not by Codex P2 repair loops.

## 背景（Context）
- PR head は攻撃者や誤った実装が変更できるため、そこに review policy を置くと review gate を弱められる。
- 任意 body injection を許すと、reviewer prompt / policy / scope が caller によって変わる。
- SpecDock の review gate は deterministic evidence を残し、後続の PR blocker closure と接続する必要がある。

## 選択肢（Options considered）
- Option A: PR head の policy を読む。
  - Pros: PR 内で policy 変更を同時に試せる。
  - Cons: review 対象自身が review policy を弱められる。
  - 棄却理由: trusted review gate として成立しない。
- Option B: caller が自由に review body / args を指定する。
  - Pros: 柔軟。
  - Cons: injection surface が大きく、再現性が落ちる。
  - 棄却理由: deterministic review evidence と相性が悪い。
- Option C: base SHA の fixed path から policy を読み、runtime が body を合成する。
  - Pros: trusted source と再現性を確保できる。
  - Cons: policy change 自体の rollout には base branch integration が必要。
  - 採用理由: security と reproducibility の balance が最もよい。

## 判断理由（Rationale）
- Review policy は review される差分から独立した trusted source にあるべきである。
- Deterministic body / hash evidence は、再 review、PR repair、blocker closure の入力として使いやすい。
- Static analysis で機械的に検出できる事項を reviewer P2 loop に流すと waste が増えるため、lint / type / schema / CI と review obligation を分離する。

## 影響（Consequences）
- Positive:
  - PR head から review policy を弱められない。
  - Review trigger が監査可能になる。
  - Static analysis と human/AI review の責務が分離される。
- Negative / Debt:
  - Base branch に policy bootstrap がない repo では human gate になる。
  - Policy rollout は base integration を伴う。
- 影響範囲:
  - GitHub review trigger runtime
  - installed `.github/codex/review-policy.md`
  - PR observation / blocker closure evidence
- 移行/ロールバック:
  - Missing base policy は fail-closed human gate。
  - Policy change は通常 PR で base に取り込んでから有効化する。
- Follow-ups:
  - `iss-00231` が trusted base-SHA review policy trigger を実装する。

## 非目標（Non-goals）
- `openai/codex-action` 本番移行をこの ADR で決めない。
- PR head policy を fallback として使わない。
- caller-provided raw `gh` args を review trigger に通さない。

## 未確定事項（Open Questions）
- 初期 max size、additive focus allow-list の細部は `iss-00231` で確定する。ただし base SHA fixed path / deterministic body / no head fallback は固定済み。

## 参考（References）
- `design.md`
- `plan.md`
- `20260623t074452z-disc-adr-decision-synthesis-after-issue-226-closure.md`
