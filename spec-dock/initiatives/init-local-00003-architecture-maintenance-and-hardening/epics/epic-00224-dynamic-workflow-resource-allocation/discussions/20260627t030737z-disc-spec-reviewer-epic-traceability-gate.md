---
種別: ディスカッション
ID: "20260627t030737z-review"
タイトル: "Spec Reviewer Epic Traceability Gate Review"
状態: "failed"
作成者: "spec-reviewer"
最終更新: "2026-06-27"
親: ["epic-00224"]
reviewer_role: "spec-reviewer"
review_status: "fail"
overall_confidence_score: 0.95
source_review_agent: "019f0708-b368-7b12-8c95-8de144acd95d"
source_review_nickname: "Bernoulli"
---

# Spec Reviewer Epic Traceability Gate Review

## レビュー結論

- review_status: fail
- confidence: 0.95
- scope:
  - Epic 00224 `requirement.md` / `design.md` / `plan.md` / `report.md`
  - accepted ADR discussions
  - `iss-00226`〜`iss-00239` の Issue docs / reports
  - provider / dogfooding PR observation skills and scripts
  - guidance runtime surface
  - relevant regression tests

Spec reviewer は、現在の追加監査で確認した懸念を false positive ではないと判断した。特に trusted base policy fallback、stale skill contract、Epic canonical docs と実装済み `guidance` handoff の矛盾、corrective Issue / Epic report closure evidence の不足は、Epic close readiness と PR merge-prepared readiness を止める P0 / P1 finding である。

## Findings

### P0: Trusted base policy が利用不能な場合の human gate が未実装

- affected requirement / decision:
  - E-RQ-009 Trusted GitHub Codex review policy
  - E-AC-009 Trusted review trigger
  - E-AC-010 Untrusted policy rejection
  - ADR `20260623t074444z-adr-trusted-base-sha-github-review-policy.md`
- observed evidence:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh`
  - `.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh`
  - `tests/unit/infra/test_init_update.py`
- reviewer finding:
  - Epic E-RQ-009 と accepted ADR は、base policy missing / invalid / oversized / unreadable を human gate にし、fallback review trigger を投稿しないことを要求している。
  - しかし provider / dogfooding の `trigger_codex_review.sh` は `base_sha_missing`、`too_large`、`invalid`、`missing` を warning limitation として扱い、その後 fallback body を POST し、`success=true` になり得る。
  - tests も fallback `body=@codex review` と success を期待しており、ADR と逆の仕様を固定している。
- risk:
  - accepted base policy なしで external review request が投稿され、trusted review gate が成立しない。
  - PR head に policy を追加しただけの状態で bare `@codex review` が走り、Epic が意図した base policy rollout / human gate が迂回される。
- required remediation:
  - base SHA missing / policy missing / invalid / oversized / unreadable の場合は POST しない。
  - JSON は `success=false`、`overall_status=human_gate`、blocking limitation metadata を返す。
  - head policy fallback は追加しない。
  - Issue 231 docs / reports / tests を ADR 準拠へ更新する。

### P1: PR observation skill の write contract が stale

- affected requirement / decision:
  - E-RQ-009
  - ADR `Trusted Base SHA GitHub Review Policy`
  - Fixed endpoint + deterministic body decision
- observed evidence:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - `.agents/skills/github-pr-observation/SKILL.md`
- reviewer finding:
  - accepted ADR と現在の正常系実装は、policy source、policy hash、reviewed head SHA を含む deterministic multiline body を要求している。
  - しかし provider / dogfooding の `github-pr-observation/SKILL.md` は、public write を「exactly one fixed `@codex review` body」と説明している。
- risk:
  - operator / downstream agent が wrong trigger model を採用し、trusted policy evidence と human gate を落とす。
- required remediation:
  - skill contract を fixed endpoint + runtime-composed deterministic body に更新する。
  - caller-provided body は禁止のまま維持する。
  - unusable base policy は human gate と明記する。

### P1: `guidance` stdout handoff が Epic 正本へ昇格されていない

- affected requirement / decision:
  - E-RQ-001 State-derived workflow entrypoint
  - E-RQ-004 Fixed Skill kernel
  - E-RQ-005 Compiled Runbook
  - `iss-00238` の stdout handoff / human-only projection decision
- observed evidence:
  - `requirement.md` lines 80-105
  - Epic `design.md`
  - Epic `plan.md`
  - `iss-00238` report / discussion
  - shipped Issue Planning / Execution skills
  - runtime parser and tests
- reviewer finding:
  - `iss-00238` は `guidance issue-planning` / `guidance issue-execution` を agent-facing stdout handoff として accepted / implemented し、generated runbook projection を human/debug artifact に demote している。
  - 一方で Epic requirement は skills が runtime `workflow next` を実行すると書き、Runbook が `.agent/` / `active/` に atomic saved されることを主 flow として残している。
  - Epic design / plan も `workflow next` と generated projection を main flow / gate として使っている。
- risk:
  - Epic source of truth が shipped skills、runtime parser、tests と矛盾し、後続 agent が stale handoff を実行する。
- required remediation:
  - Epic requirement / design / plan / report を `guidance <target>` stdout authority に更新する。
  - projection は human-only / debug-only / non-canonical として整理する。
  - Issue 238 の trace decisions を Epic quality gate に反映する。

### P1: Corrective Issue 239 の gate が未解決

- affected requirement / decision:
  - E-RQ-006 Adaptive artifact composition
  - issue creation scaffold / assurance compose safety decision
  - `iss-00238` report の follow-up conversion
- observed evidence:
  - `issues/iss-00239-compose-issue-planning-templates-after-assurance-classification/requirement.md`
  - `issues/iss-00239-compose-issue-planning-templates-after-assurance-classification/report.md`
- reviewer finding:
  - Issue 238 report は planning template composition risk を follow-up `iss-00239` に変換している。
  - しかし `iss-00239` は template scaffold のままで、front matter は `draft | approved`、requirement objective は placeholder、AC / EC は empty placeholders、report は未記入 scaffold である。
- risk:
  - known corrective issue を未解決のまま Epic close すると、model が assurance compose を飛ばす問題が再発する。
- required remediation:
  - `iss-00239` を authoring / review / implementation / verification まで進める。
  - もしくは non-blocking supersession / defer decision を formal に記録し、Epic report と final gates に反映する。

### P1: Epic report の completion evidence が内部矛盾している

- affected requirement / decision:
  - Epic final completion conditions
  - G9 Rollout
  - Epic-wide final quality gate
- observed evidence:
  - `report.md` front matter lines 1-6
  - `report.md` lines 147-169
- reviewer finding:
  - Epic report front matter は `状態: "draft | approved"` のまま。
  - completed issues が `なし` とされている一方、後段では E-AC-001〜021 を issue reports based pass としている。
  - later corrective issues `iss-00237` / `iss-00238` / `iss-00239` と、現在の trusted-policy fallback failure が反映されていない。
- risk:
  - downstream agent が Epic 00224 の状態を draft / complete / blocked のどれとして扱うべきか判断できない。
- required remediation:
  - Epic report を current issue completion status、corrective issue dispositions、trusted-policy gate status、reviewer verdicts、final completion evidence で再構成する。

## Traceability Table

| Requirement / ADR / discussion decision | Observed evidence | Status | Reviewer conclusion |
|---|---|---:|---|
| E-RQ-009 / ADR trusted base policy: base policy failure is human gate, no head fallback | trigger script fallback path; tests expecting fallback success | fail | P0 blocker。ADR と逆の success path が実装・テストで固定されている |
| E-RQ-009: deterministic review body with policy/hash/head evidence | happy-path trigger body includes policy metadata | partial | 正常系はあるが failure path と skill contract が未反映 |
| Fixed endpoint, no caller-provided body | trigger helper rejects raw body / unsafe args | pass-needs-regression | unsafe input rejectionは有効。deterministic body wording 更新が必要 |
| PR observation skill contract | skill says fixed body `@codex review` | fail | public contract が実装済み multiline body と ADR に合わない |
| E-RQ-001 / E-RQ-004: runtime current guidance handoff | shipped skills use `guidance issue-planning` / `guidance issue-execution`; tests assert no `workflow next` in skills | partial | 実装は進んでいるが Epic 正本が stale |
| `iss-00238` decision: `guidance <target>` not `workflow next`; no compatibility alias required | issue discussion / report / runtime tests | partial | issue local では成立。Epic canonical docs へ未昇格 |
| `iss-00238` decision: projection is human/debug only and non-blocking | runtime presentation / runbook tests | partial | 実装はあるが Epic E-RQ/E-AC の authority language が古い |
| E-RQ-006 / planning template composition safety | `iss-00239` exists | fail | known corrective issue が scaffold のまま |
| Epic final report as closure ledger | Epic report front matter and completion tables | fail | corrective issues と current blockers が未反映 |
| Current audit report `20260627t025746z-research...` | reviewer independently verified concerns | pass | false positive は確認されなかった |

## Missing Epic Quality Gates

Epic close 前に以下の gate を追加する必要がある。

1. Accepted ADR decision trace:
   - 各 ADR の Decision bullet ごとに provider implementation、dogfooding mirror、tests、skill/docs、Issue report evidence を紐付ける。
   - failure path の tests が ADR と逆仕様を固定していないかを明示的に確認する。
2. Corrective issue inclusion:
   - 初期 7 issue だけでなく、`iss-00237` / `iss-00238` / `iss-00239` を final quality gate に含める。
   - open / scaffold / draft corrective issue がある場合、Epic close を block するか formal defer / supersede decision を要求する。
3. Canonical-doc freshness:
   - 下流 issue で accepted された decision が Epic requirement / design / plan / report に戻っているかを検査する。
   - `workflow next` のような superseded term が current entrypoint として残っていないかを確認する。
4. Skill / provider / dogfooding / tests contract parity:
   - provider skill、dogfooding skill、runtime implementation、tests が同じ public contract を説明・検証していることを確認する。
5. Epic report reconciliation:
   - completed issue list、corrective issue status、blocked gate、reviewer verdict、manual test evidence、PR readiness status を一つの closure ledger に統合する。

## False Positive Review

Spec reviewer は、現在の監査 report `20260627t025746z-research-epic-quality-gate-traceability-audit.md` の主要懸念を false positive とは判断しなかった。

- trusted policy fallback: confirmed
- stale PR observation skill wording: confirmed
- Epic canonical docs stale `workflow next` / projection authority wording: confirmed
- corrective issue trace gap: confirmed
- Epic report closure inconsistency: confirmed

## Epic Readiness Judgment

- Epic close readiness: blocked
- PR merge-prepared readiness: blocked
- Required next action:
  - P0 trusted policy human gate を実装修正する。
  - PR observation skill contract を deterministic body / human gate に更新する。
  - Epic canonical docs を `guidance <target>` stdout authority と human-only projection に更新する。
  - `iss-00239` の扱いを完了 / formal defer / supersede のいずれかで閉じる。
  - Epic report を current closure ledger として再構成する。
