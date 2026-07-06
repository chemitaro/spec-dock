---
種別: disc
ID: "20260706t103820z-disc"
タイトル: "ChatGPT Spec Authoring Batch Workflow Redesign"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-07-06"
親: ["epic-00283"]
関連:
  - "20260706t090820z-research"
authority: "synthesized"
created_by_role: "main-orchestrator"
oracle_provider: "chatgpt-use"
oracle_session: "specdock-chatgpt-workflow-redesign"
model: "gpt-5.5-pro"
wrapper: "oracle-chatgpt"
wrapper_mode: "browser"
requested_branch: "unavailable-detached-head"
inspected_repo: "chemitaro/spec-dock"
inspected_ref: "main"
adoption_status: "unreviewed"
reflected_to: []
diff_guard_result: "not_applicable"
derived_from:
  - "chatgpt-use live run: specdock-chatgpt-workflow-redesign"
  - "previous research artifact: 20260706t090820z-research-chatgpt-oracle-advanced-analysis.md"
intended_targets:
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/report.md"
  - "future dogfood issue for ChatGPT Spec Authoring Batch"
source_paths:
  - "AGENTS.md"
  - "README.md"
  - "pyproject.toml"
  - "src/spec_dock/assets/install_root/.codex/config.toml"
  - "src/spec_dock/assets/install_root/.codex/AGENTS.md"
  - "src/spec_dock/assets/install_root/.codex/agents/*.toml"
  - "src/spec_dock/assets/install_root/.agents/skills/spec-dock-*.md"
  - "src/spec_dock/assets/spec_dock/docs/workflow*.md"
  - "src/spec_dock/assets/spec_dock/docs/phase*.md"
  - "src/spec_dock/assets/spec_dock/docs/authoring/*.md"
  - "src/spec_dock/assets/spec_dock/templates/**/*.md"
  - "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/{requirement,design,plan,report}.md"
  - "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/artifacts/20260706t090820z-research-chatgpt-oracle-advanced-analysis.md"
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/{requirement,design,plan}.md"
---

# 20260706t103820z-disc ChatGPT Spec Authoring Batch Workflow Redesign

## 位置づけ

- この artifact は、`chatgpt-use` / GPT-5.5 Pro Extended に依頼した「ChatGPT を前提に SpecDock workflow 自体を組み直せるか」の分析結果である。
- 前段 research `20260706t090820z-research` は、ChatGPT を optional oracle evidence provider として扱い、reviewer gate / canonical authority は置換しない方針を示した。
- 本 artifact はそこから一段踏み込み、ChatGPT に `design draft + plan draft + self-review + reviewer focus` を一括生成させる `Spec Authoring Batch` 案の有効性を検討する。
- この artifact は discussion / synthesis evidence であり、canonical docs、reviewer pass、phase promotion、implementation readiness を自己主張しない。

## Oracle invocation summary

- wrapper:
  - `/Users/iwasawayuuta/.codex/skills/chatgpt-use/scripts/oracle-chatgpt`
- session:
  - `specdock-chatgpt-workflow-redesign`
- dry-run:
  - 約 235,689 tokens。
  - 69 files bundled。
- live run:
  - Pro Extended selected。
  - browser slot acquired。
  - completed in approximately 9m42s。
- branch / repo:
  - local worktree was detached HEAD.
  - ChatGPT was instructed to inspect GitHub repository `chemitaro/spec-dock`; if current branch was unavailable, inspect default branch `main`.

## Executive recommendation

ChatGPT の結論は次の通り。

- `chatgpt-use` / GPT-5.5 Pro Extended を、単なる advisory evidence より一段強い **Spec Authoring Batch Engine** として導入する価値はある。
- ただし、ChatGPT output は canonical `design.md` / `plan.md` ではなく、scope-local `artifacts/` の draft package / evidence として受け取る。
- 推奨は Variant B と Variant C の中間:
  - reviewed requirement を input にする。
  - ChatGPT が requirement critique、design draft、implementation plan draft、self-review、reviewer focus、adoption map を一括生成する。
  - main orchestrator が Evidence Adoption Ledger を通じて採用・部分採用・棄却を判断する。
  - canonical `design.md` / `plan.md` は main orchestrator が再記述する。
  - fresh `spec-reviewer` は design / plan それぞれで必須にする。
- self-review は reviewer focus / preflight / risk scouting であり、`review_status` gate ではない。

## Repository facts used by ChatGPT

ChatGPT は、default branch `main` の repository files と添付 context から次を前提にした。

- `spec-dock` は dogfooding repo であり、repo documents を source of truth とする。
- provider-side source of truth は `src/spec_dock/`、local dogfooding workspace は `spec-dock/`。
- shipped scaffold / docs / templates / system files は `src/spec_dock/assets/spec_dock/{docs,templates,system}/` が provider source。
- spec authoring は `requirement -> spec-reviewer pass -> design -> spec-reviewer pass -> plan -> spec-reviewer pass -> downstream handoff` の順で進む。
- each phase promotion requires fresh `spec-reviewer` `review_status: pass`。
- delegated design / plan draft は evidence であり、fresh `spec-reviewer` pass の代替ではない。
- `spec-reviewer` / `code-reviewer` / `qa-reviewer` は authoritative `review_status` を持つ fixed output contract である。

## Workflow redesign options

| Variant | Summary | 利点 | 主リスク | 推奨 |
|---|---|---|---|---|
| A. Current + advisory only | ChatGPT output を `research` / `disc` evidence に留める | 最小リスク | 高容量 reasoning を十分使えない | fallback として維持 |
| B. Combined design+plan draft generator | reviewed requirement から design draft + plan draft を一括生成 | design-plan 整合が高まる | plan が未承認 design を先取りする | 短期本命 |
| C. Spec authoring batch | requirement critique + design + plan + self-review + reviewer focus を一回で返す | traceability / review focus が強い | output が大きく canonical adoption が雑になる | 中期本命 |
| C2. Two-pass oracle batch | 1回目 draft package、2回目 independent oracle critique | self-review より independence が高い | コスト増、fresh reviewer と混同しやすい | strict / critical 補助に有効 |
| D. ChatGPT workflow driver / manager | ChatGPT が initiative -> epic -> issue planning / repair loops を主導 | throughput 最大 | authority / availability / privacy / stale state risk 最大 | 今は不可 |
| E. Oracle preflight for execution / PR repair | CI logs / review comments / diff から repair strategy を提案 | repair 方針に有用 | secrets / private logs / stale diff | 限定採用可 |
| F. Oracle backend for `deep-consultant` | `deep-consultant` backend として ChatGPT を使う | role contract を維持したまま高品質化 | backend availability / cost | 安全な拡張先 |

ChatGPT の推奨 roadmap は、A を fallback として残し、B を minimal experiment、C を正式設計候補、D は当面採らない、というもの。

## Replacement / augmentation matrix

| Role / authority | 推奨扱い | ChatGPT が置き換えるもの | 残すもの | 理由 |
|---|---|---|---|---|
| `system-architect` | augment / optional backend | design draft generation の一部。alternatives、boundary model、dependency analysis、risk scouting | role contract、artifact provenance、diff guard、fresh `spec-reviewer` requirement照合 | `system-architect` 自体が canonical writer ではなく artifact draft role なので backend 化しやすい |
| `implementation-planner` | augment / optional backend | plan draft generation、test strategy、execution order、review gate focus | plan draft contract、traceability、implementation-readiness を claim しない boundary | planner contract は stale/insufficient design evidence を blocker にするため、その semantics は維持する |
| `spec-reviewer` | leave intact / no replacement | reviewer focus の事前生成、想定 finding の preflight | authoritative `review_status` gate | self-review は独立 review ではない |
| `code-reviewer` | leave intact | diff risk checklist、review focus、possible bug hypothesis | code review gate | approved plan と report evidence に照らす gate は維持する |
| `qa-reviewer` | leave intact | test adequacy risk preflight、missing scenario candidate | QA gate | test adequacy の authoritative `review_status` は維持する |
| `consultant` | partial replacement / backend candidate | option framing、tradeoff analysis、experiment proposal | read-only role contract、decision support discipline | ChatGPT large reasoning と親和性が高い |
| `deep-consultant` | strong backend candidate | high-impact workflow redesign / final arbitration / vendor-tooling decision support | read-only, no shell, not implementer, not reviewer boundary | long-lived architecture / workflow decisions に向く |
| main orchestrator canonical ownership | leave intact / strengthen | initial synthesis workload は減らせる | user dialogue、adoption、canonical rewrite、Promotion Record、phase promotion | canonical adoption は main orchestrator が行う |
| `dev-coder` / `doc-writer` / `spec-manager` | leave intact | implementation strategy / docs impact / command focus の提案 | mutation / command execution / shipped docs edits | browser oracle を mutation driver にしない |

## Scope-by-scope usage model

| Scope level | ChatGPT の適切な使い方 | Output | Adoption / gates |
|---|---|---|---|
| Initiative requirement/design/plan | product strategy、success metrics、epic portfolio、architecture/feature boundary、long-lived tradeoff | `research` / `disc` / ADR candidate / roadmap critique | main orchestrator が initiative docs へ採用し、fresh `spec-reviewer` pass |
| Epic requirement/design/plan + issue decomposition | cross-issue responsibility boundary、shared vocabulary、issue slicing、dependency order、integration checkpoint、rollout risk | Epic design/plan draft package、issue decomposition table、risk map | Epic canonical docs へ採用後、fresh `spec-reviewer` pass |
| Issue requirement/design/plan + implementation handoff | reviewed requirement から design + executable plan + test strategy + reviewer focus を一括生成 | `draft-design` / `draft-plan` または composite `disc`。adoption map 付き | canonical issue docs へ再記述後、design/plan ごとに fresh `spec-reviewer` pass |
| Issue execution | implementation strategy、risk scouting、test cases candidate、review focus | handoff note / risk checklist | `dev-coder` 実装、report evidence、step reviewer gate |
| Code review / QA review | self-review, preflight, likely-bug search, missing-test candidate | reviewer focus artifact | `code-reviewer` / `qa-reviewer` の fresh pass は維持 |
| PR delivery / CI repair | CI failure log の原因仮説、repair plan、review comment clustering | `pr-repair-batch` artifact / repair strategy | dev-coder follow-up + code/QA/spec re-review |

## Future workflow proposed by ChatGPT

```text
Phase 0: Repository / Scope Handshake
  Inputs:
    - repo
    - current branch or fallback ref
    - active scope / reviewed requirement
    - source_paths allowlist
  Outputs:
    - provenance manifest
    - stale_if conditions
  Authority:
    - none; readiness evidence only
  Fallback:
    - connector unavailable => no oracle adoption; existing workflow continues

Phase 1: Requirement Lock
  Inputs:
    - user intent
    - source-grounded research / clarification
  Outputs:
    - canonical requirement.md
    - report.md Spec Authoring Gate
  Gate:
    - fresh spec-reviewer pass
  Authority:
    - main orchestrator + user clarification ownership

Phase 2: Oracle Spec Authoring Batch
  Inputs:
    - reviewer-pass requirement revision
    - parent docs / ADR / relevant source files
  Outputs:
    - composite artifact:
      - requirement critique
      - design draft
      - plan draft
      - self-critique
      - reviewer focus
      - adoption map
  Authority:
    - evidence only
  Fallback:
    - system-architect + implementation-planner or manual authoring

Phase 3: Intake Quarantine / Diff Guard
  Inputs:
    - ChatGPT package
  Outputs:
    - artifact provenance
    - privacy check
    - branch/ref/source path check
    - adoption eligibility
  Gate:
    - no canonical claims
    - no forbidden path
    - no secrets
    - no stale source

Phase 4: Canonical Adoption
  Inputs:
    - eligible oracle package
  Outputs:
    - canonical design.md
    - canonical plan.md
    - report.md Evidence Adoption Ledger
  Authority:
    - main orchestrator only
  Fallback:
    - partial adoption / reject / rerun / manual rewrite

Phase 5: Fresh Spec Review
  Inputs:
    - canonical design.md / plan.md
    - adopted evidence refs
  Outputs:
    - spec-reviewer JSON
  Gate:
    - design pass before plan authority
    - plan pass before downstream handoff

Phase 6: Execution Handoff
  Inputs:
    - approved requirement/design/plan
    - executable step contract
  Outputs:
    - dev-coder / doc-writer delegation package
  Gate:
    - report evidence gate
    - no unresolved EAL
    - required verification paths

Phase 7: Implementation + Review
  Inputs:
    - approved plan step
  Outputs:
    - code/docs changes
    - report evidence
  Gates:
    - code-reviewer / qa-reviewer / spec-reviewer as mapped
  Oracle use:
    - optional repair strategy / risk scouting only

Phase 8: PR / CI Repair Loop
  Inputs:
    - PR diff, CI logs, review comments
  Outputs:
    - pr-repair-batch artifact
    - bounded delegated repair plan
  Gates:
    - local workflow PR observation
    - fresh review after fixes
```

## Self-review and reviewer gate

ChatGPT の結論は「self-review は fresh reviewer gate を置換しない」。

理由:

- self-review は authoring run と同じ model / context / objective による introspection である。
- SpecDock の reviewer gate は独立した fresh reviewer role、fixed output contract、authoritative `review_status` を要求する。
- `spec-reviewer` は findings と authoritative `review_status` を返す fixed schema であり、`review_status` は workflow gate である。

置換できるのは non-gate 用途のみ:

- `system-architect` draft の risk section。
- `implementation-planner` draft の plan blockers。
- `spec-reviewer` へ渡す focus list。
- `code-reviewer` / `qa-reviewer` へ渡す likely risk / missing-test candidates。
- Lite / Standard で specialist を使わない場合の skip reason 補助 evidence。ただし fresh `spec-reviewer` は必要。

もし将来 ChatGPT を reviewer backend にするなら、最低条件は:

- authoring run とは別の fresh session / role / context。
- reviewer contract と完全一致する fixed JSON schema。
- reviewed artifact を自身が作っていないこと。
- reviewed source paths and target revision hash が固定されていること。
- unavailable / denied / stale / schema invalid は gate fail または incomplete。
- maintainer-approved workflow contract / ADR。

ただし、それでも `self-review` は不可。可能性があるのは future `oracle-spec-reviewer` のような independent reviewer backend であり、これは architecture initiative 側の reviewer semantics 変更として扱う。

## Non-negotiable safety boundaries

| Boundary | Rule | Failure mode | Mitigation |
|---|---|---|---|
| Canonical docs authority | `requirement.md` / `design.md` / `plan.md` / `report.md` は main orchestrator single-writer | ChatGPT output が canonical と誤認される | artifact frontmatter に `adoption_status: unreviewed`, `reflected_to: []` |
| User clarification ownership | user intent / scope / acceptance に関わる質問は orchestrator が行う | ChatGPT が仮定で scope を固める | clarification candidates として返させる |
| Reviewer gate semantics | self-review は fresh reviewer gate ではない | self-review を `review_status` と誤認 | `oracle_preflight_findings` など gate 風でない名称にする |
| Evidence adoption | artifact は採用判断前は evidence | 大量 output を丸ごと design/plan に貼る | adoption map と Evidence Adoption Ledger を必須化 |
| Branch / GitHub connector correctness | branch/ref/source_paths を記録 | detached HEAD / stale main 混同 | branch-sensitive claim は低 confidence / stale 条件付き |
| Secrets / privacy | `.env*`, tokens, cookies, production dumps, customer data を attach しない | secret leakage | file denylist + pre-attach manifest + privacy review |
| Stale analysis | source revision / inspected ref / invalidation condition を持つ | 古い analysis を採用 | `stale_if` を frontmatter / report に残す |
| Availability | ChatGPT unavailable は degraded success ではない | external browser dependency で止まる | existing workflow fallback を維持 |
| Raw transcript | prompt全文・long transcript は canonical docs に置かない | private reasoning / noise / secrets 混入 | summarized evidence only |
| Workflow driver scope | ChatGPT は external reasoning engine であり manager ではない | mutation / PR / reviewer gate を混同 | driver 化は architecture initiative + ADR 後 |

## Minimal dogfood experiment

### Experiment title

`Dogfood ChatGPT Spec Authoring Batch for Design+Plan Drafts`

### Location

- First location:
  - `init-local-00002 Prototype Feature Expansion`
- Reason:
  - 初期実験は operator value / workflow capability expansion であり、source-of-truth semantics 変更ではない。
- Escalate to architecture initiative only if:
  - provider registry
  - runtime adapter
  - generic capability discovery
  - reviewer semantics changes
  - shipped product behavior changes

### Requirement to use

低リスクな real requirement:

> Define a manual `chatgpt-use` oracle evidence workflow for producing a combined design+plan draft package from a reviewed requirement, preserving canonical adoption and reviewer gates.

### Arms to compare

| Arm | Method |
|---|---|
| Baseline | Existing `system-architect` draft + main adoption + `implementation-planner` draft + main adoption |
| Oracle batch | ChatGPT one-shot requirement critique + design draft + plan draft + self-review + reviewer focus |
| Hybrid | ChatGPT batch first, then existing `system-architect` / `implementation-planner` use it as evidence |

### Metrics

| Metric | Measurement |
|---|---|
| Reviewer pass iterations | fresh `spec-reviewer` loops needed for design and plan |
| P0/P1/P2 finding count | missing traceability, scope creep, gate bypass, stale evidence |
| Adoption ratio | percent of ChatGPT claims adopted into canonical design/plan |
| Traceability coverage | RQ/AC -> design decisions -> plan steps |
| Plan executability | step order, verification, reviewer focus, closure obligations |
| Safety compliance | no canonical authority claim, no reviewer-pass claim, no secret/path leak |
| Branch correctness | inspected repo/ref/source_paths/stale_if recorded |
| Human edit burden | minor synthesis / major rewrite / reject |
| Comparative quality | spec-reviewer result versus baseline package |

### Hard fail criteria

- ChatGPT package claims `authority: accepted`, `adoption_status: adopted`, reviewer pass, phase completion, or implementation readiness.
- Output depends on files not listed in `source_paths`.
- GitHub connector / branch provenance is missing for branch-sensitive claims.
- Self-review is represented as `spec-reviewer`, `code-reviewer`, or `qa-reviewer` pass.
- Secrets / `.env*` / private customer data are included.
- Canonical docs are updated without Evidence Adoption Ledger and fresh reviewer pass.
- First canonical adoption yields P1/P0 `spec-reviewer` finding caused by oracle hallucination or scope creep.

### Pass criteria

- Package is captured as scope-local artifact with clear provenance and `adoption_status: unreviewed`.
- Main orchestrator can adopt at least 60-80% of substantive design/plan content with minor synthesis.
- Fresh `spec-reviewer` passes canonical design and plan in no more than one repair loop.
- Compared to baseline, reviewer finding severity is equal or lower, and plan executability is equal or better.
- Existing manual / delegated authoring path remains available when ChatGPT is unavailable.

## Suggested artifact / report structure

Recommended first experiment artifact:

```text
spec-dock/initiatives/init-local-00002-prototype-feature-expansion/
  artifacts/
    <ts>-disc-chatgpt-spec-authoring-batch-experiment.md
```

Recommended sections:

- frontmatter:
  - `created_by_role`
  - `oracle_provider`
  - `model`
  - `inspected_repo`
  - `inspected_ref`
  - `requested_branch`
  - `adoption_status: unreviewed`
  - `reflected_to: []`
  - `source_paths`
  - `stale_if`
- body:
  - 調査目的
  - Inputs / source paths
  - Oracle invocation summary
  - Design draft summary
  - Plan draft summary
  - Self-review findings
  - Reviewer focus suggestions
  - Adoption map
  - Rejected / risky claims
  - Stale conditions
  - Privacy / secret review
  - Comparison against baseline
  - Recommendation

Report Evidence Adoption Ledger entry should be added only after adoption decision.

## Concrete next actions recommended by ChatGPT

1. Adopt Variant B/C hybrid as the working recommendation.
   - Name it `ChatGPT Spec Authoring Batch`, not `ChatGPT reviewer` or `ChatGPT workflow driver`.
2. Create a dogfood feature issue under `init-local-00002` for a manual `chatgpt-use` batch experiment.
3. Define the batch output contract:
   - requirement critique
   - design draft
   - plan draft
   - self-review
   - reviewer focus
   - adoption map
   - provenance
   - stale_if
   - privacy review
4. Run the experiment against one reviewed requirement and compare it to `system-architect + implementation-planner`.
5. Require fresh `spec-reviewer` for canonical design and plan after adoption.
6. Record results as `disc` plus `report.md` Evidence Adoption Ledger, not as direct canonical authority.
7. Defer workflow-driver / reviewer-replacement ideas until measured evidence shows B/C improves quality without eroding gates.
8. Escalate to architecture initiative only if provider registry, runtime adapter, generic capability discovery, reviewer semantics changes, or shipped product behavior are needed.

## Orchestrator interpretation

- この分析は、前回の「optional oracle evidence provider」案を弱めるものではなく、output shape を **advisory note** から **structured authoring batch evidence** に強める提案である。
- 直接 canonical docs を ChatGPT に書かせる設計はまだ不適切。
- 一方で、`system-architect` と `implementation-planner` の draft 作成部分を、同一 ChatGPT batch の output で統合・高度化する価値は十分ある。
- 次の一手は実装ではなく、dogfood-only experiment issue を切って、実際の reviewed requirement に対して baseline / oracle batch / hybrid を比較すること。

## 反映先

- reflected_to:
  - なし。この artifact は `adoption_status: unreviewed` の discussion evidence であり、canonical docs へは未反映。
- candidate targets:
  - `spec-dock/initiatives/init-local-00002-prototype-feature-expansion/report.md`
  - future dogfood feature issue for `ChatGPT Spec Authoring Batch`
  - possible architecture follow-up under `init-local-00003` if provider registry or reviewer semantics change is proposed.
