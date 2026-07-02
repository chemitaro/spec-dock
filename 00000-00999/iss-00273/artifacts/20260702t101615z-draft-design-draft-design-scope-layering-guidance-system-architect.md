---
created_by_role: system-architect
scope_id: iss-00273
source_paths:
  - spec-dock/active/context-pack.md
  - spec-dock/active/issue/requirement.md
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
  - spec-dock/active/issue/artifacts/20260702t081004z-draft-design-scope-layering-planning-guidance-pre-start-seed.md
  - spec-dock/active/issue/artifacts/20260702t081005z-draft-plan-scope-layering-planning-guidance-pre-start-seed.md
  - spec-dock/active/epic/requirement.md
  - spec-dock/active/epic/design.md
  - spec-dock/active/epic/plan.md
  - spec-dock/active/epic/report.md
  - spec-dock/active/epic/issues/iss-00271-redesign-initiative-requirement-design-plan-templates/design.md
  - spec-dock/active/epic/issues/iss-00271-redesign-initiative-requirement-design-plan-templates/report.md
  - spec-dock/active/epic/issues/iss-00272-redesign-epic-requirement-design-plan-templates/design.md
  - spec-dock/active/epic/issues/iss-00272-redesign-epic-requirement-design-plan-templates/report.md
  - src/spec_dock/assets/spec_dock/docs/workflow_initiative.md
  - src/spec_dock/assets/spec_dock/docs/workflow_epic.md
  - src/spec_dock/assets/spec_dock/docs/workflow_clarification.md
  - src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md
  - src/spec_dock/assets/spec_dock/docs/phase_requirement.md
  - src/spec_dock/assets/spec_dock/docs/phase_design.md
  - src/spec_dock/assets/spec_dock/docs/phase_plan.md
  - src/spec_dock/assets/spec_dock/docs/phase_plan_initiative.md
  - src/spec_dock/assets/spec_dock/docs/phase_plan_epic.md
  - src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md
  - src/spec_dock/assets/spec_dock/docs/authoring/decision-routing.md
  - src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md
  - src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md
  - src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md
  - src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md
  - src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md
  - src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md
  - src/spec_dock/assets/spec_dock/templates/initiative/design.md
  - src/spec_dock/assets/spec_dock/templates/epic/plan.md
intended_targets:
  - spec-dock/active/issue/design.md
  - spec-dock/active/issue/plan.md
  - spec-dock/active/issue/report.md
adoption_status: unreviewed
reflected_to: []
diff_guard_result: passed
---

# iss-00273 Scope-layering reference と planning guidance 更新 - system-architect 設計ドラフト

この artifact は `iss-00273` の正規 `design.md` / `plan.md` へ採用するための未レビュー設計証跡です。Canonical authority、phase promotion、reviewer pass、implementation readiness は主オーケストレータと fresh `spec-reviewer` gate が所有します。

## 1. Requirement Coverage

| 要件 | 設計上の閉じ方 |
|---|---|
| `I273-AC-001` | `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md` を新規 provider-side reference とし、Initiative / Epic / Issue の責務、decision radius、authority flow、anti-rules を狭く集約する。 |
| `I273-AC-002` | workflow docs、phase docs、skills、templates には全文表を複製せず、必要箇所に 1-3 文の thin link と local implication だけを置く。 |
| `I273-AC-003` | `spec-dock-clarification` と planning skills に、source-grounded read、調査で分かることを質問しない、一問ずつの interview、採用知識の外部化を明確化する。 |
| `I273-AC-004` | `artifacts/`、research、interview、disc、delegated draft は evidence only であり、canonical adoption は docs / ADR / `report.md` EAL / reviewer gate 経由であることを reference / workflow / skills に置く。 |
| `I273-AC-005` | 日本語運用では canonical docs / artifacts 本文を日本語ファーストにし、ファイルパス、コマンド、コード識別子、SpecDock 固定語、外部固有名詞は原文保持できると明記する。 |
| `I273-AC-006` | `iss-00271` / `iss-00272` の template 接続点を、reference 作成後に dangling でない relative link へ接続する。 |
| `I273-AC-007` | link / grep / targeted pytest / validate で reference 存在、主要リンク、重複回避、artifact authority leak の不在を確認する。 |
| `I273-AC-008` | Epic planning handoff package に Issue-local `draft-design` / `draft-plan` path index、または blocked / fallback evidence を要求する。 |
| `I273-AC-009` | Epic Planning が Issue Start 前に canonical Issue `design.md` / `plan.md` 本文を作らず、pre-start seed を Issue-local artifact として扱う境界を workflow / skills に反映する。 |
| `I273-EC-001` | full responsibility table は `scope-layering.md` にだけ置き、他 surface は要約リンクに留める。 |
| `I273-EC-002` | `authority: accepted`、`adoption_status: adopted`、non-empty `reflected_to` などを raw artifact が自己主張する wording を避ける。 |
| `I273-EC-003` | DDD / EDA は既存 architecture に応じた補助語彙に留め、SpecDock 標準アーキテクチャとして書かない。 |
| `I273-EC-004` | 日本語ファーストは説明本文の方針であり、識別子や外部固有名詞の翻訳強制ではないと明記する。 |

## 2. Existing Context Findings

- Active context は `iss-00273` を approved authority として示しているが、canonical `design.md` / `plan.md` は assurance compose 後の skeleton が中心で、Issue 固有設計はまだ十分に具体化されていない。
- `iss-00273` requirement は issue grade を `strict` とし、specialist evidence と fresh reviewer gate を要求している。
- `docs/authoring/` には `decision-routing.md` と `issue-plan.md` があり、`scope-layering.md` はまだ存在しない。
- `workflow_initiative.md` / `workflow_epic.md` は scope ownership と artifacts catalog をすでに持つが、scope-layering reference への link はまだない。
- `workflow_epic.md` の handoff section は `draft-requirement` / `draft-design` を述べており、Epic design / current Epic plan が要求する `draft-design` / `draft-plan` path index とはずれがある。
- `workflow_clarification.md` と `spec-dock-clarification` skill は source-grounded grill loop の骨格をすでに持つ。`iss-00273` では SpecDock 版として、artifact authority、Japanese-first、one-question boundary を薄く補強すればよい。
- `workflow_spec_authoring.md` と phase docs は delegated draft evidence / single-writer authority / grade matrix をすでに持つ。`iss-00273` では scope-layering reference と pre-start Issue draft boundary への discoverability を足す。
- `iss-00271` / `iss-00272` は provider templates と dogfooding mirror の parity を維持し、scope-layering reference の final thin link は `iss-00273` に渡している。dangling link を避けた前段判断を尊重する。

## 3. Design Decisions

- `D273-001` `[N]`: Source of truth は provider-side `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md` とする。dogfooding `spec-dock/docs/authoring/scope-layering.md` は provider 変更後の確認 / mirror 対象であり、実装 source of truth ではない。
- `D273-002` `[N]`: Authority model は `scope-layering.md` = responsibility / decision routing reference、workflow docs = lifecycle authority、phase docs = authoring gate / phase minimum、skills = operational first-read spine、templates = authoring scaffold と分離する。
- `D273-003` `[N]`: Artifact authority は evidence only を default にする。Raw research / interview / disc / delegated draft は canonical docs、accepted ADR、または `report.md` EAL / Spec Authoring Gate に採用されるまで implementation input ではない。
- `D273-004` `[N]`: Source-grounded clarification は Matt Pocock 型 Grill-with-docs をそのまま移植せず、SpecDock の active docs、parent docs、artifacts、ADR、report EAL、one-question interview lifecycle に合わせる。
- `D273-005` `[N]`: 日本語ファースト方針は本文・説明・判断理由に適用し、識別子、path、command、SpecDock 固定語、外部固有名詞には適用しない。
- `D273-006` `[N]`: Downstream Issue handoff package は Issue-local `draft-design` / `draft-plan` path index、canonical placeholder boundary、adoption state、grade-specific specialist obligation、handoff-ready と execution-ready の区別を持つ。
- `D273-007` `[P]`: Tests はまず `tests/unit/infra/test_init_update.py` の scaffold/template/docs assertions を拡張し、必要なら docs/skill text の targeted grep を plan step に入れる。Runtime behavior 変更が出る場合だけ cli/runtime tests へ広げる。

## 4. Alternatives Considered

| 代替案 | 不採用理由 |
|---|---|
| 各 workflow / phase / skill / template に責務表全文を置く | drift と矛盾が増え、`I273-EC-001` に反する。 |
| ADR を日常参照 surface として使わせる | ADR は durable decision record であり、operational reference には重い。日常導線は `docs/authoring/scope-layering.md` が担う。 |
| Scope-layering を `workflow_spec_authoring.md` に統合する | spec authoring gate と scope responsibility model が混ざり、workflow doc が膨らむ。 |
| Runtime command behavior までこの Issue で変更する | `iss-00273` の主目的は guidance / docs / skills / templates の接続であり、readiness runtime behavior は `iss-00274` / `iss-00275` が扱う。 |
| 日本語のみを強制し、識別子も訳す | `I273-EC-004` に反し、path / command / fixed terms の可読性を落とす。 |

## 5. Boundary / Contract Model

### Source of truth と target write scope

- Provider source of truth:
  - `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_*.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_*.md`
  - `src/spec_dock/assets/spec_dock/docs/authoring/*.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-*/SKILL.md`
  - `src/spec_dock/assets/spec_dock/templates/{initiative,epic}/...`
- Dogfooding inspection / mirror targets:
  - `spec-dock/docs/...`
  - `spec-dock/templates/{initiative,epic}/...`
- This delegated draft write scope:
  - この artifact 1 件のみ。Canonical docs、provider files、tests、templates、skills は編集しない。

### Authority model

| Surface | Authority | この Issue の扱い |
|---|---|---|
| `docs/authoring/scope-layering.md` | Scope responsibility / decision radius reference | 新規作成し、長い責務モデルと anti-rules をここへ集約する。 |
| `workflow_initiative.md` / `workflow_epic.md` / `workflow_issue.md` | lifecycle / scope-specific governance | scope-layering reference への thin link と、その workflow 固有の implication だけを足す。 |
| `phase_requirement.md` / `phase_design.md` / `phase_plan*.md` | phase minimum / authoring gate | 既存 scope ownership と delegated gate を reference へ寄せ、重複を減らす。 |
| `workflow_spec_authoring.md` | phase promotion / delegated evidence / reviewer gate | artifact authority、draft boundary、report evidence gate の正本として維持し、scope-layering へ薄く接続する。 |
| `spec-dock-clarification` skill | operational source-grounded grill loop | SpecDock-native one-question / artifact capture / adoption handoff を強める。 |
| planning skills | operational first-read spine | reference / workflow docs を読む順序と stop condition を足す。 |
| templates | starting scaffold | scope-specific prompts と thin link だけを持ち、workflow / reference の全文を複製しない。 |
| raw artifacts / delegated drafts | evidence only | canonical adoption までは implementation authority を持たない。 |

## 6. Dependency Analysis

- `iss-00273` は `iss-00271` / `iss-00272` の template vocabulary と final thin link 接続点に依存する。
- `iss-00274` は `iss-00273` の scope-layering reference、artifact authority wording、handoff-ready / execution-ready 語彙に依存する。
- `iss-00275` は reference existence、link integrity、duplicate table avoidance、artifact authority leak、日本語ファースト guidance を smoke / tests の対象にする。
- 先に `scope-layering.md` を作らないと、workflow / phase / skill / template links が dangling になるため、実装順は reference 作成を最初に置くべきである。
- Templates の追加変更は前段 Issue の実装成果に対する thin link 接続に限定する。Template contract の追加再設計が必要になった場合は scope creep として停止する。

## 7. Source of Record

正本優先順位は次の順で扱う。

1. Accepted ADR / parent Epic design decisions: D-001, D-003, D-008, D-009。
2. `epic-00270` canonical requirement / design / plan / report。
3. `iss-00273` requirement。
4. `iss-00273` canonical design / plan candidate。
5. `iss-00271` / `iss-00272` completed or in-branch implementation reports and designs。
6. Provider source files under `src/spec_dock/assets/...`。
7. Issue-local pre-start draft artifacts and this delegated artifact。

This artifact is lowest-authority evidence and does not supersede canonical docs.

## 8. Data Flow / Domain Model / Interface Contract

### Evidence-to-authority flow

```text
source-grounded read / research / interview / delegated draft
  -> disc / ADR candidate / draft artifact
    -> main orchestrator adoption decision
      -> canonical requirement/design/plan or accepted ADR
        -> report.md EAL / Spec Authoring Gate / Reviewer Gate Status
          -> downstream Issue planning / execution handoff
```

### Scope-layering reference outline

- Initiative:
  - owns strategic outcome, investment boundary, source-of-truth policy, cross-Epic operating decisions.
  - must not own Issue-level TDD cycles or file/class design.
- Epic:
  - owns cross-Issue model envelope, dependency direction, Issue slicing, handoff package, integration checkpoint.
  - must not hide Initiative decisions or replace Issue execution planning.
- Issue:
  - owns one observable behavior or local contract delta, implementation boundary, verification and rollback for that slice.
  - must not redefine parent envelope or treat delegated draft existence as readiness.

### Clarification contract

- Read active docs, parent docs, artifacts, ADRs, provider files, tests/templates before asking.
- Do not ask the user about source-grounded facts.
- Ask one user-intent blocker at a time through the orchestrator.
- Important questions use `interview` artifacts; facts use `research`; synthesis uses `disc`; durable decisions use ADR candidate / accepted ADR path.
- Adoption is recorded in canonical docs or `report.md` ledgers, not by artifact existence.

## 9. File / Module Change Plan

| Target | Design intent |
|---|---|
| `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md` | 新規 reference。scope ownership、decision radius、authority flow、artifact authority、Japanese-first、anti-rules を狭く整理する。 |
| `src/spec_dock/assets/spec_dock/docs/workflow_initiative.md` | Initiative が所有する判断と reference link を 1 箇所に追加する。artifact / draft catalog の詳細複製は避ける。 |
| `src/spec_dock/assets/spec_dock/docs/workflow_epic.md` | Issue handoff package を `draft-design` / `draft-plan` path index、placeholder boundary、adoption state に更新する。 |
| `src/spec_dock/assets/spec_dock/docs/workflow_issue.md` | Issue が parent envelope を再定義しないこと、Issue-local draft adoption -> assurance compose -> fresh reviewer の順を reference へ接続する。 |
| `src/spec_dock/assets/spec_dock/docs/workflow_clarification.md` | Source-grounded grill loop を SpecDock artifact / EAL / one-question boundary へ接続し、日本語ファースト artifact guidance を追加する。 |
| `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md` | 既存 delegated evidence / authority boundary を正本として維持し、scope-layering reference と pre-start draft boundary の discoverability を足す。 |
| `src/spec_dock/assets/spec_dock/docs/phase_requirement.md` / `phase_design.md` / `phase_plan*.md` | 既存 scope ownership を reference へ薄くリンクし、phase docs 内の重複を増やさない。 |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md` | first-read に `scope-layering.md` と日本語ファースト / source-grounded routing reminder を追加する。 |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md` | Issue handoff package、pre-start draft artifact boundary、thin link 接続を追加する。 |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md` | Grill loop の source-grounded behavior、one-question interview、artifact capture、adoption evidence を SpecDock wording で補強する。 |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md` | Draft artifacts は evidence only、Strict / Critical は draft existence だけで readiness にならないことを補強する。 |
| `src/spec_dock/assets/spec_dock/templates/initiative/*` / `templates/epic/*` | `iss-00271` / `iss-00272` の接続点へ non-dangling thin link を追加する。大きな template redesign はしない。 |
| `tests/unit/infra/test_init_update.py` | reference existence、template link、forbidden wording、Japanese-first boundary の focused assertions を追加する候補。 |
| `spec-dock/docs/...` / `spec-dock/templates/...` | provider-side 変更後の dogfooding mirror / validation 確認対象。 |

## 10. Migration / Compatibility / Rollback

- Migration:
  - DB や persisted runtime data の migration は不要。
  - Existing authored docs は自動変換しない。新規 scaffold / update 後の docs と skills に guidance が反映される。
- Compatibility:
  - Existing Issue grade / TDD workflow、`assurance compose`、fresh reviewer gates を維持する。
  - Legacy `discussions/` は preservation input として残し、新規 working evidence は `artifacts/` を使う。
  - `new artifact draft-design` / `draft-plan` は Issue-local evidence surface として扱い、canonical docs mutation に使わない。
- Rollback:
  - Link / wording / template / skill changes は Issue diff 単位で revert 可能。
  - `scope-layering.md` が広くなりすぎた場合は、workflow lifecycle detail を workflow docs へ戻し、reference を responsibility / routing model に狭める。
  - Artifact authority を弱める rollback は行わない。

## 11. Observability

- `report.md` Evidence Adoption Ledger:
  - この delegated draft の採否、採用した sections、採用しない sections、diff guard result、fresh reviewer result を記録する。
- Spec Authoring Gate:
  - requirement / design / plan promotion と reviewer verdict を記録する。
- Reviewer Gate Status:
  - docs / skill / template changes の spec-reviewer result を記録する。
- Verification evidence:
  - `rg` link / wording checks、focused pytest、`./spec-dock/scripts/spec-dock validate`、必要なら dogfooding read-through を report に残す。

## 12. Test Strategy

- Structural / docs checks:
  - `rg --files src/spec_dock/assets/spec_dock/docs/authoring | rg 'scope-layering\\.md$'`
  - workflow / phase / skill / template から `authoring/scope-layering.md` へ到達できること。
  - `draft-requirement` が Epic handoff の required pair として残っていないこと。少なくとも `draft-design` / `draft-plan` path index が guidance にあること。
- Negative wording checks:
  - raw artifact を canonical authority とする表現がないこと。
  - `authority: accepted` / `adoption_status: adopted` / non-empty `reflected_to` を delegated draft が自己主張する wording がないこと。
  - DDD / EDA mandatory wording がないこと。
  - 識別子翻訳強制 wording がないこと。
- Focused tests:
  - `tests/unit/infra/test_init_update.py -k spec_document_templates_keep_policy_out_of_scaffold`
  - `tests/unit/infra/test_init_update.py -k checked_in_dogfooding_mirror_templates_match_provider_assets`
  - 新規または既存 assertion で reference / link / forbidden wording を確認する。
- SpecDock validation:
  - `./spec-dock/scripts/spec-dock validate`
  - 必要なら `git diff --check`
- Reviewer focus:
  - discoverability、重複回避、artifact authority、日本語ファースト、pre-start draft boundary、downstream `iss-00274` handoff readiness。

## 13. ADR Candidates

- 追加 ADR は現時点では不要。
- 既存 accepted ADR で足りる:
  - scope-layering reference publication surface。
  - complete understanding before canonical authoring。
  - Japanese-first spec authoring。
  - unified draft artifact command and grade-role policy。
- 新 ADR が必要になる条件:
  - Scope-layering reference が provider docs を超えて runtime validation authority を持つ必要が出る。
  - `new artifact draft-*` の command contract をこの Issue で変更する必要が出る。
  - 日本語ファースト方針を machine-enforced policy にする必要が出る。

## 14. Risks

- Risk: Reference が広くなり workflow docs と二重 authority になる。
  - Mitigation: Reference は responsibility / decision radius / anti-rules に限定し、lifecycle 手順は workflow docs へ残す。
- Risk: Thin links が少なすぎて agent が reference を読まない。
  - Mitigation: workflow docs、phase docs、skills、templates の入口近くに最小 link を置く。
- Risk: Templates に scope model を複製して drift する。
  - Mitigation: template は 1 文 link と authoring prompt に留める。
- Risk: Artifact authority leak が残る。
  - Mitigation: negative grep と spec-reviewer focus に raw artifact authority wording を入れる。
- Risk: `draft-requirement` / `draft-design` の古い wording と `draft-design` / `draft-plan` の現行方針が混在する。
  - Mitigation: `workflow_epic.md` handoff section を明示的に更新し、Issue-local draft pair を正す。
- Risk: 日本語ファーストが over-translation になる。
  - Mitigation: allowed original terms の list を reference / skills / templates に置く。

## 15. Requirement Clarification Requests

none

現時点の sources では、`iss-00273` の design draft 作成を止める requirement gap はない。実装中に runtime command behavior 変更、template redesign の追加、または `draft-requirement` 継続要否が出た場合は、Issue design / plan amendment と fresh reviewer gate に戻す。

## 16. Integration Notes for Main Orchestrator

- この draft を採用する場合、`report.md` の EAL に `adoption_status`、採用 section、rejected portions、diff guard result、fresh reviewer target を記録する。
- 正規 `design.md` へは、この artifact の構造をそのまま貼らず、Issue 固有の design decisions / change surface / test strategy として再記述する。
- `plan.md` では、reference 作成を先頭 step に置き、その後 workflow / phase / skills / templates の thin link、tests / validate、review gate の順にする。
- `iss-00274` へ渡す語彙は、handoff-ready と execution-ready の区別、Issue-local `draft-design` / `draft-plan` path index、artifact evidence only、grade-specific specialist obligation。
- `iss-00275` へ渡す検証観点は、reference existence、link integrity、duplicate responsibility table absence、artifact authority leak absence、Japanese-first boundary、draft artifact boundary。
- Forbidden actions avoided: canonical docs edit、provider implementation edit、tests edit、template edit、skill edit、GitHub mutation、phase promotion、reviewer-pass claim、issue finish claim、user dialogue ownership。

diff_guard_result: passed - この delegated run では許可された Issue-local artifact 1 件のみを作成・編集し、canonical docs / implementation files / templates / tests / skills には書き込んでいない。
