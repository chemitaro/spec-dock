---
created_by_role: system-architect
scope_id: iss-00274
source_paths:
  - "spec-dock/active/context-pack.md"
  - "spec-dock/active/issue/requirement.md"
  - "spec-dock/active/issue/design.md"
  - "spec-dock/active/issue/plan.md"
  - "spec-dock/active/issue/report.md"
  - "spec-dock/active/issue/artifacts/20260702t081006z-draft-design-epic-execution-readiness-workflow-pre-start-seed.md"
  - "spec-dock/active/issue/artifacts/20260702t081007z-draft-plan-epic-execution-readiness-workflow-pre-start-seed.md"
  - "spec-dock/active/epic/requirement.md"
  - "spec-dock/active/epic/design.md"
  - "spec-dock/active/epic/plan.md"
  - "spec-dock/active/epic/artifacts/20260702t030615z-interview-phase3-handoff-package-inspection-strength.md"
  - "spec-dock/active/epic/artifacts/20260702t022907z-adr-scope-layering-reference-publication-surface.md"
  - "spec-dock/active/epic/artifacts/20260702t025127z-adr-complete-understanding-before-canonical-authoring.md"
  - "spec-dock/active/epic/artifacts/20260702t040113z-adr-japanese-first-spec-authoring-policy.md"
  - "spec-dock/active/epic/artifacts/20260702t074332z-adr-unified-draft-artifact-command-grade-role-policy.md"
  - "src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md"
  - "src/spec_dock/assets/spec_dock/docs/workflow_epic.md"
  - "src/spec_dock/assets/spec_dock/docs/workflow_issue.md"
  - ".agents/skills/spec-dock-epic-execution/SKILL.md"
  - "src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md"
intended_targets:
  - "design.md"
adoption_status: unreviewed
reflected_to: []
diff_guard_result: passed
---

# iss-00274 system-architect design draft artifact

この artifact は、正規 `design.md` を作る main orchestrator 向けの evidence-only draft である。正規 `design.md` / `plan.md` / `report.md`、実装ファイル、テスト、skills、docs、templates は編集していない。

Source requirement revision: `spec-dock/active/issue/requirement.md`、`最終更新: "2026-07-02"`、`状態: "draft"`。

## 1. Requirement Coverage

| 要件 | 設計マッピング候補 | 正規 `design.md` へ残すべき契約 |
|---|---|---|
| `I274-AC-001` | `D274-001` Epic execution の first-read input を、reviewer-gated Epic `requirement.md` / `design.md` / `plan.md` / `report.md` と downstream Issue handoff package に広げる。 | Epic execution skill / workflow は、Issue 選択前に parent Epic planning outputs と Issue handoff package を読む。 |
| `I274-AC-002` | `D274-002` structural blocker catalog を固定する。 | missing canonical docs、missing / stale reviewer pass、missing readiness contract、missing executable plan structure、missing delegation contract、missing verification、missing reviewer focus、unresolved blocking report entries は execution へ流さない。 |
| `I274-AC-003` | `D274-003` semantic sufficiency は reviewer finding として扱う。 | acceptance criteria や test strategy の弱さは、構造が存在する限り `spec-reviewer` finding に残し、Epic execution が semantic reviewer を置き換えない。 |
| `I274-AC-004` | `D274-004` evidence / canonical authority boundary を明示する。 | raw artifact path の存在や decision-only Issue は execution-ready の根拠にしない。 |
| `I274-AC-005` | `D274-005` Issue relay と final PR delivery を分離する。 | `iss-00274` は PR を作らず、Issueごとの PR 作成を通常フローにしない。final PR delivery は `iss-00276` の責務に集約する。 |
| `I274-AC-006` | `D274-006` 日本語ファーストを execution / readiness guidance に適用する。 | docs / report / artifacts の説明本文は日本語ファースト。path / command / identifier / SpecDock 固定語は原文保持。 |
| `I274-AC-007` | `D274-007` `new artifact draft-design` / `draft-plan` を pre-start Issue handoff primitive として扱う。 | Issue-local draft artifact 作成は `new artifact draft-design --issue <issue-id>` / `new artifact draft-plan --issue <issue-id>` に寄せ、canonical docs を直接編集しない。 |
| `I274-AC-008` | `D274-008` command surface と canonical compose の責務を分離する。 | actor / specialist / depth 別 draft command は作らない。`assurance compose` は canonical compose 専用で、draft artifact 作成には使わない。 |
| `I274-AC-009` | `D274-009` handoff-ready と execution-ready を別状態として設計する。 | Strict / Critical の specialist obligation は readiness evidence gate で扱い、draft artifact 存在だけでは execution-ready にしない。 |
| `I274-EC-001` | `D274-003` / `D274-010` reviewer replacement prohibition。 | readiness check は `spec-reviewer` の代替ではない。 |
| `I274-EC-002` | `D274-002` structural blocker fail-closed。 | structural blocker がある Issue を実行可能として扱わない。 |
| `I274-EC-003` | `D274-003` reviewer finding boundary。 | semantic finding をすべて blocking にしない。 |
| `I274-EC-004` | `D274-005` / `D274-011` mutation boundary。 | PR merge、credentialed GitHub mutation、Issue close automation はこの Issue に含めない。 |

## 2. Existing Context Findings

- `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md` は、`artifacts/` / delegated draft / pre-start seed は evidence であり canonical authority ではないこと、Issue は parent envelope を再定義しないことを既に定義している。
- `src/spec_dock/assets/spec_dock/docs/workflow_epic.md` は、Epic planning completion / handoff package と `new artifact draft-design` / `draft-plan` の Issue-local primitive を既に持つ。ただし Epic execution lifecycle 側の structural blocker / reviewer finding 分離はまだ薄い。
- `src/spec_dock/assets/spec_dock/docs/workflow_issue.md` は、Issue-local draft adoption、`assurance compose`、fresh reviewer gate、execution gate、report ledger を既に広く定義している。`iss-00274` ではこれを置き換えず、Epic execution から参照する入口を強めるべきである。
- `.agents/skills/spec-dock-epic-execution/SKILL.md` と `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md` は現時点で同内容。active Issue / ready Issue / `issue start` / PR handoff の coordinator flow はあるが、Issue handoff package の構造検査リスト、handoff-ready / execution-ready 分離、draft artifact primitive の責務境界は明示不足である。
- pre-start seed artifacts は有用だが、`report.md` では deferred evidence とされ、draft artifact の存在だけでは readiness にならないと記録されている。
- `new artifact draft-design` は現に Issue-local artifact を作成できる。一方、生成直後の frontmatter は canonical `design.md` template 由来であり、delegated evidence artifact として必要な provenance fields は手動補正が必要だった。この観測は runtime / template behavior の characterization 対象である。

## 3. Design Decisions

- `D274-001 [N]`: Epic execution は、active Epic / active Issue / dependency state だけでなく、reviewer-gated Epic planning outputs と downstream Issue handoff package を first-read input とする。
- `D274-002 [N]`: Epic execution は structural gate であり、machine-checkable structural blocker を fail-closed で止める。
- `D274-003 [N]`: Epic execution は semantic reviewer ではない。意味的十分性の疑義は reviewer finding として report / reviewer focus に残す。
- `D274-004 [N]`: Issue-local draft artifact は evidence-only。canonical adoption は Issue Planning EAL、`assurance compose`、fresh reviewer gate を通る。
- `D274-005 [N]`: `iss-00274` の execution lifecycle は Issue relay を整えるだけで、Issueごとの PR delivery を通常化しない。PR readiness は `iss-00276` へ渡す。
- `D274-006 [N]`: 日本語運用では execution / readiness guidance も日本語ファーストにする。
- `D274-007 [P]`: runtime behavior change は characterization-first にする。現行 `new artifact draft-*` が Issue-local作成、canonical non-mutation、metadata、assurance fail-closed を満たすなら docs / skill update に留める。不足が観測された場合だけ focused runtime tests と最小実装を追加する。
- `D274-008 [N]`: `assurance compose` は canonical compose 専用。pre-start draft artifact 作成 surface にはしない。
- `D274-009 [N]`: handoff-ready は Issue Planning へ渡せる状態、execution-ready は Issue Execution へ入れる状態として分ける。
- `D274-010 [N]`: grade別 specialist obligation は command 名ではなく workflow / skill / EAL / reviewer gate で扱う。
- `D274-011 [N]`: GitHub mutation、PR merge、reviewer-pass self-claim、issue-finish self-claim はこの Issue の設計対象外。

## 4. Alternatives Considered

| 代替案 | 棄却 / 保留理由 | 採用する要素 |
|---|---|---|
| Epic execution を semantic reviewer 化する | `I274-EC-001` に反し、`spec-reviewer` の責務を奪う。過停止も増える。 | structural blocker と reviewer finding の分類だけを Epic execution に置く。 |
| reviewer finding もすべて blocking にする | `I274-EC-003` に反し、AC / test strategy の質的疑義まで coordinator が止めることになる。 | 構造欠落を示す場合だけ blocking に昇格する。 |
| actor / specialist 別 command を作る | accepted ADR `20260702t074332z-adr` に反する。command は authorship を保証できない。 | role obligation は report / reviewer gate で証跡化する。 |
| `assurance compose` で draft artifact も作る | canonical compose と evidence artifact creation の境界が曖昧になる。 | `new artifact draft-design` / `draft-plan` を primitive とし、将来 wrapper は thin に限定する。 |
| runtime validation を今回の主変更にする | 現時点の中心要件は skill / workflow guidance。runtime の不足は characterization 後に限定して扱うべき。 | 不足が観測された場合だけ focused runtime behavior change を追加する。 |

## 5. Boundary / Contract Model

### Structural blocker

Structural blocker は、機械的に「必要な構造がない」と判断しやすく、Issue start / Issue execution へ流すと authority leak や未計画実装を起こす欠落である。

- required canonical docs がない、template-only、または placeholder のまま execution input とされている。
- fresh reviewer pass がない、stale、または対象 revision と不一致。
- Issue readiness contract がない。
- executable plan structure がない。
- delegation contract がない。
- required verification がない。
- reviewer focus がない。
- `report.md` の Spec Authoring Gate / Evidence Adoption Ledger に unresolved blocking / stale entry がある。
- raw artifact を canonical authority として扱っている。
- decision-only Issue を execution-ready として扱っている。
- Strict / Critical で specialist evidence または認められた fallback evidence がない。

### Reviewer finding

Reviewer finding は、構造は存在するが意味的な十分性や品質に疑義がある状態である。

- acceptance criteria はあるが網羅性が弱い可能性がある。
- test strategy はあるが、integration / smoke の範囲が不足している可能性がある。
- target files は明示されているが、設計上の妥当性に疑問がある。
- artifact reference はあるが、採用理由の説明が薄い。
- 日本語ファーストの逸脱が軽微で、authority leak や実行不能に直結しない。

## 6. Dependency Analysis

```text
iss-00272 handoff package fields
  -> iss-00273 scope-layering / artifact authority / planning guidance
    -> iss-00274 Epic execution readiness guidance
      -> iss-00275 smoke tests / template validation
        -> iss-00276 final quality / PR delivery
```

- `iss-00274` は `iss-00273` の `scope-layering.md` と draft artifact boundary を前提にする。
- `iss-00275` は、この Issue が定義する structural blocker / reviewer finding 分離、handoff-ready / execution-ready 分離、draft artifact primitive の smoke 対象を受け取る。
- `iss-00276` は no per-Issue PR と final PR delivery 集約を受け取る。
- Provider-side source of truth は `src/spec_dock/assets/...`。dogfooding `.agents/...` / `spec-dock/...` は確認・mirror 対象であり、実装 source of truth ではない。

## 7. Source of Record

| 種別 | Source of record | この draft での扱い |
|---|---|---|
| Issue 要件 | `spec-dock/active/issue/requirement.md` | `I274-AC-001..009` / `I274-EC-001..004` を設計 mapping の主軸にする。 |
| Parent design | `spec-dock/active/epic/design.md` | `D-006` Option B、`D-008` Japanese-first、`D-009` draft artifact command を継承する。 |
| Accepted ADR | `20260702t022907z-adr`, `20260702t025127z-adr`, `20260702t040113z-adr`, `20260702t074332z-adr` | authority flow、source-grounded authoring、日本語ファースト、unified draft primitive の trace とする。 |
| Workflow docs | `workflow_epic.md`, `workflow_issue.md`, `scope-layering.md` | lifecycle / scope / evidence boundary の正本として参照し、重複定義を避ける。 |
| Skill entrypoint | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md` | provider-side skill 更新候補。 |
| Dogfooding skill | `.agents/skills/spec-dock-epic-execution/SKILL.md` | installed / local consumer 確認対象。 |

## 8. Data Flow / Domain Model / Interface Contract

```text
reviewer-gated Epic docs
  + Epic handoff package
  + Issue-local draft-design / draft-plan path index
  + grade-specific specialist obligation
  -> handoff-ready
  -> issue start / issue planning
  -> EAL adoption decision
  -> assurance compose canonical design.md / plan.md
  -> fresh spec-reviewer pass
  -> executable plan + no structural blockers
  -> execution-ready
```

`handoff-ready`:

- Epic execution が target Issue を Issue Planning に渡してよい状態。
- parent trace、dependencies、readiness contract、draft artifact path / skip evidence、expected verification、reviewer focus が揃う。
- canonical Issue `design.md` / `plan.md` はまだ `awaiting-assurance-compose` でもよい。
- 実装開始を許可しない。

`execution-ready`:

- Issue Planning が evidence を採否判断し、canonical `design.md` / `plan.md` を `assurance compose` し、fresh reviewer gate を通し、executable plan と required verification を持つ状態。
- structural blocker が残らず、grade別 specialist obligation または認められた fallback evidence が揃う。
- Issue execution skill へ渡してよい。

`new artifact draft-design` / `draft-plan`:

- Issue-local `artifacts/` に evidence artifact を作る primitive。
- canonical `requirement.md` / `design.md` / `plan.md` / `report.md` を変更しない。
- author role、specialist adequacy、canonical adoption、reviewer pass は command では主張しない。

`assurance compose`:

- canonical `design.md` / `plan.md` / `report.md` を compose する surface。
- Issue-local draft artifact の作成には使わない。
- compose 後も fresh reviewer gate なしに execution-ready を主張しない。

## 9. File / Module Change Plan

| 候補 | 設計判断候補 | runtime behavior change 要否 |
|---|---|---|
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md` | First-read flow に handoff package inspection、structural blocker / reviewer finding split、handoff-ready / execution-ready 分離、no per-Issue PR を追加する。 | docs / skill text change。runtime change なし。 |
| `.agents/skills/spec-dock-epic-execution/SKILL.md` | provider source 更新後の dogfooding / installed mirror として整合確認または更新候補。 | runtime change なし。provider-first の反映方針を plan で明確化する。 |
| `src/spec_dock/assets/spec_dock/docs/workflow_epic.md` | Planning Completion / Handoff と Execution Lifecycle を接続し、Issue handoff inspection を薄く定義する。 | runtime change なし。 |
| `src/spec_dock/assets/spec_dock/docs/workflow_issue.md` | Issue Planning / execution-ready の正本として参照されること、draft adoption -> compose -> review -> execution の順序を補助する。 | runtime change なし。 |
| `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md` | 原則として変更不要。既に authority flow と anti-rules を持つ。必要なら link / wording の薄い補強に留める。 | runtime change なし。 |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/...` | `new artifact draft-*` の metadata、Issue-only、canonical non-mutation、assurance fail-closed が不足している場合だけ最小変更する。 | characterization 次第。今回の中心変更にはしない。 |
| `tests/` | docs / skill smoke と、runtime change がある場合の focused tests。 | runtime change がある場合のみ必須。 |

## 10. Migration / Compatibility / Rollback

- migration: database migration や既存 workspace layout 変更は不要。
- compatibility: existing Issue grade / TDD workflow、`assurance compose`、fresh reviewer gates を維持する。
- dogfooding: provider-side asset 更新後に local `spec-dock/` / `.agents/` への影響を確認する。確認対象であり、最初の source of truth ではない。
- rollback: skill / workflow wording の変更は PR / Issue diff 単位で revert できる。runtime behavior を追加した場合は focused tests とともに revert する。
- forbidden rollback: raw artifact authority、decision-only execution-ready、actor-specific draft command、`assurance compose` の draft artifact 化へ戻さない。

## 11. Observability

- `report.md` の Evidence Adoption Ledger に、pre-start draft artifacts、system-architect draft、implementation-planner draft、採用 / 部分採用 / 棄却 / stale / blocked の disposition を残す。
- `report.md` の Spec Authoring Gate に、structural blocker の有無、reviewer finding の扱い、fresh reviewer target revision を残す。
- implementation 後は、docs / skill diff、grep / smoke checks、必要な runtime tests、`validate` 結果を report evidence として残す。
- reviewer finding は「未実行の block」ではなく、spec-reviewer が判断すべき論点として記録する。

## 12. Test Strategy

Docs / skill only の場合:

- grep / inspection で `structural blocker`, `reviewer finding`, `handoff-ready`, `execution-ready`, `new artifact draft-design`, `new artifact draft-plan`, `assurance compose`, `iss-00276` / final PR delivery の導線を確認する。
- `.agents` と provider-side skill の drift を確認する。
- `./spec-dock/scripts/spec-dock validate` を実行する。
- `spec-reviewer` focus: lifecycle authority、canonical / evidence boundary、Option B、Japanese-first、no self-claim。

Runtime behavior を変更する場合:

- `new artifact draft-design --issue <issue-id>` / `draft-plan` が Issue-local `artifacts/` に作成し、canonical `design.md` / `plan.md` を変更しないこと。
- non-Issue scope の `draft-design` / `draft-plan` が fail-closed になること。
- missing / invalid / stale `.assurance.json` が no-write fail-closed になること。
- generated artifact metadata が evidence artifact として必要な provenance fields を持つこと。
- Strict / Critical で draft artifact 存在だけでは execution-ready にならないことを smoke / reviewer focus に含める。

## 13. ADR Candidates

- 新規 ADR 候補は現時点では `none`。
- 既存 accepted ADR で足りる:
  - `20260702t022907z-adr-scope-layering-reference-publication-surface.md`
  - `20260702t025127z-adr-complete-understanding-before-canonical-authoring.md`
  - `20260702t040113z-adr-japanese-first-spec-authoring-policy.md`
  - `20260702t074332z-adr-unified-draft-artifact-command-grade-role-policy.md`
- runtime validation semantics を provider-wide hard rule として大きく変える必要が出た場合だけ、follow-up ADR candidate を検討する。

## 14. Risks

- structural blocker と reviewer finding の境界が曖昧だと、agent が semantic finding を勝手に blocking にするか、逆に authority leak を見逃す。
- `new artifact draft-*` が artifact evidence metadata を十分に出さない場合、delegated evidence の provenance が毎回手動補正になる。
- provider-side skill と dogfooding `.agents` skill の drift があると、実際の agent entrypoint と shipped asset の挙動がずれる。
- runtime behavior change を広げすぎると、`iss-00274` が guidance update の範囲を超えて dependency / assurance redesign になり得る。
- `validate` は structural projection を見るが、semantic sufficiency を保証しないため、fresh `spec-reviewer` focus が必要である。

## 15. Requirement Clarification Requests

none。

現時点で正規 `design.md` 作成前に main orchestrator へ戻すべき未解決 product decision は見つからない。runtime behavior change の要否は、正規 plan の characterization step で判断できる実装時論点として扱える。

## 16. Integration Notes for Main Orchestrator

- この draft は `D274-001..D274-011` を正規 `design.md` の設計差分候補として採用できる。
- 正規 `design.md` では、Issue grade は requirement の pre-start handoff が `strict` としている点を優先し、生成テンプレート由来の `standard` 表記を採用しない方がよい。
- 正規 `design.md` は、pre-start seed artifact をそのまま貼らず、この draft の structural boundary と parent ADR trace を統合するのがよい。
- 正規 `plan.md` へ渡す execution candidates:
  - S1: provider-side `spec-dock-epic-execution` skill の readiness guidance 更新。
  - S2: `workflow_epic.md` / 必要な `workflow_issue.md` の薄い補強。
  - S3: runtime `new artifact draft-*` characterization。必要なら focused tests と最小実装。
  - S4: docs / skill read-through、`validate`、fresh `spec-reviewer`。
- Leaf evidence used: none。追加の sub-agent / peer authoring role は呼んでいない。
- Forbidden actions avoided: canonical docs、implementation files、tests、skills、docs、templates、GitHub state、phase promotion、reviewer pass claim、execution-ready claim は変更・主張していない。
- Unresolved requirement gaps: none。

No canonical edit, final authority, promotion, reviewer-pass, or user-dialogue ownership is claimed.
