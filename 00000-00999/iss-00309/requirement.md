---
種別: 要件定義書（Issue）
ID: "iss-00309"
タイトル: "ChatGPT First Planning Skills And Fallback Route Redesign"
関連GitHub: ["#309"]
状態: "review-ready"
作成者: "ChatGPT GPT-5.5 Pro / Codex adopted candidate"
最終更新: "2026-07-08"
親: ["epic-00295", "init-local-00003"]
Issue Grade: "strict"
authorized_profile: "strict"
draft_authority: "evidence_only"
adoption_status: "codex_adopted_review_pending"
---

# iss-00309 ChatGPT First Planning Skills And Fallback Route Redesign — Issue 要件定義

## 0. 文書の位置づけ

この文書は、`iss-00309` の canonical `requirement.md` 候補である。ChatGPT が生成した候補を Codex が比較・検査し、`report.md` の Evidence Adoption Ledger に採用判断を記録した。必要な fresh `spec-reviewer` pass を取得するまでは、承認済み・execution-ready ではない。

この Issue は `strict` profile として扱う。理由は、installed skill surface、workflow docs、Epic plan template、installed asset distribution、Issue Planning / Epic Execution の authority boundary に影響し、複数 Issue と将来の planning workflow が依存するためである。

## 1. 結論

`iss-00309` は、SpecDock の planning route を **ChatGPT-first primary route** として再設計し、従来 planning route を **human-approved emergency backup** として `-manual` suffix の skill に分離する。

必須成果は次である。

- 既存 primary skill names を維持する。
  - `spec-dock-initiative-planning`
  - `spec-dock-epic-planning`
  - `spec-dock-issue-planning`
- 従来 route を manual backup skill として追加する。
  - `spec-dock-initiative-planning-manual`
  - `spec-dock-epic-planning-manual`
  - `spec-dock-issue-planning-manual`
- ChatGPT / browser / automation の capacity failure、timeout、一時 failure は `wait` / `retry` / `recover` を優先し、manual route へ自動 fallback しない。
- Manual route は、ChatGPT / browser / automation / provider 側に hard / unrecoverable failure があり、人間がその状態を認識して明示承認した場合だけ使える。
- Accepted ADR `artifacts/20260708t161533z-adr-chatgpt-first-option-3-plus-issue-planning-workflow.md` の Option 3+ を provider-side skills / docs / templates へ反映する。
- Epic Planning は Issue draft requirement / draft design / draft plan と dependency / boundary handoff を作るが、canonical Issue Planning は Epic Execution 中の各 Issue start 直前または直後に current repository state、prior completed Issues、dependency state、unresolved ledgers と照合して行う。
- Multi-Issue implementation Epic は final quality gate / PR delivery Issue を必須とする。single-Issue / docs-only / no-op Epic は skip rationale と completion evidence があれば separate final quality Issue を省略できる。

## 2. 背景

Parent Epic `epic-00295` は、ChatGPT authoring pack workflow を installed runtime surface と installed skill surface へ昇格する。ChatGPT output は requirement / design / plan draft、Issue slicing proposal、risk、reviewer focus、EAL candidate を生成できるが、canonical adoption、`.assurance.json` mutation、authorized_profile 決定、fresh reviewer pass、execution-ready、PR-ready、Issue / Epic completion を主張しない。

現行 current branch では、primary planning skills は ChatGPT を evidence lane として参照しているが、ChatGPT-first route を primary planning route として十分に強制していない。また、`-manual` backup skills は provider-side installed skill path にまだ存在しない。`iss-00309` の既存 `design.md` / `plan.md` は placeholder であり、strict profile に耐える具体設計・計画が必要である。

## 3. 正本・根拠

| 種別 | パス / 識別子 | この Issue への意味 |
|---|---|---|
| Parent Epic requirement | `spec-dock/.../epic-00295-chatgpt-authoring-pack-installed-runtime/requirement.md` | ChatGPT evidence-only、installed runtime / skill surface、existing planning skill names 維持、final quality gate policy の上位要件。 |
| Parent Epic design | `spec-dock/.../epic-00295-chatgpt-authoring-pack-installed-runtime/design.md` | Scope skill plane / Authoring runtime plane / Evidence data plane / Authority plane の分離、status taxonomy、skill taxonomy、GitHub preflight、ZIP contract。 |
| Parent Epic plan | `spec-dock/.../epic-00295-chatgpt-authoring-pack-installed-runtime/plan.md` | Provider-side source-of-truth migration、skill taxonomy docs update、runtime docs update、final quality gate / PR delivery relay policy。 |
| Issue report EAL | `report.md` | EAL-001〜EAL-005 に accepted decisions が記録済み。 |
| Interview evidence | `artifacts/20260708t150402z-interview-chatgpt-first-planning-route-fallback-boundary-interview.md` | wait / retry / recover 優先、manual fallback は明示承認付き emergency backup。 |
| Interview evidence | `artifacts/20260708t151122z-interview-primary-and-fallback-skill-naming-interview.md` | 既存 skill names を ChatGPT-first primary route とし、従来 route を `-manual` suffix に退避。 |
| Interview evidence | `artifacts/20260708t152452z-interview-final-quality-gate-issue-scope-interview.md` | Multi-Issue implementation Epic の final quality Issue 必須範囲と skip 条件。 |
| Research evidence | `artifacts/20260708t154900z-research-chatgpt-first-issue-planning-timing-and-epic-execution-workflow.md` | Option 3+、draft handoff、just-in-time canonical Issue Planning、drift feedback rule、PlantUML。 |
| Accepted ADR | `artifacts/20260708t161533z-adr-chatgpt-first-option-3-plus-issue-planning-workflow.md` | Option 3+ を accepted decision として固定し、skills / docs / templates へ反映する必要がある。 |
| Provider skills | `src/spec_dock/assets/install_root/.agents/skills/` | installed skill source of truth。 |
| Provider docs | `src/spec_dock/assets/spec_dock/docs/` | installed workflow docs source of truth。 |
| Provider templates | `src/spec_dock/assets/spec_dock/templates/` | installed template source of truth。 |
| Installer registry | `src/spec_dock/cli.py` | `_MANAGED_SKILL_NAMES` に installed skill distribution order がある。 |

## 4. Scope

### 4.1 In scope

- `spec-dock-initiative-planning` / `spec-dock-epic-planning` / `spec-dock-issue-planning` を ChatGPT-first primary planning route として更新する。
- `spec-dock-initiative-planning-manual` / `spec-dock-epic-planning-manual` / `spec-dock-issue-planning-manual` を human-approved emergency backup skills として provider assets に追加する。
- `spec-dock-chatgpt-authoring` との関係を、primary planning skills から呼び出される shared evidence lane として明確化する。
- `src/spec_dock/cli.py` の managed skill registry を更新し、manual skills が installed repo へ配布されるようにする。
- Workflow docs に次を反映する。
  - ChatGPT-first primary route。
  - manual backup の承認条件。
  - Option 3+ の draft handoff / just-in-time canonical Issue Planning。
  - `handoff-ready` と `execution-ready` の分離。
  - final quality gate / PR delivery Issue policy。
- Epic plan template に次を反映する。
  - Epic classification: multi-Issue implementation / single-Issue / docs-only / no-op。
  - final quality Issue required / skipped。
  - skip rationale / completion evidence。
  - Issue-local draft path index。
  - pre-start canonical Issue boundary。
- Accepted ADR と research の PlantUML を、provider-side docs / templates の implementation plan に取り込む。
- Dogfooding workspace `spec-dock/` は provider-side update の validation / confirmation surface として扱い、必要な mirror consistency を確認する。
- Tests / static checks / manual dogfood validation を plan に固定する。

### 4.2 Out of scope

- ChatGPT に canonical docs 直接更新、`.assurance.json` mutation、authorized_profile 決定、reviewer pass 付与、execution-ready / PR-ready / merge-ready 判定をさせること。
- `authoring adopt`、`authoring create-issues-from-zip`、`authoring mark-reviewer-pass`、`authoring set-authorized-profile`、`authoring issue-execution-ready`、`authoring pr-ready` の新規実装。
- GitHub Issue / PR の自動作成・自動 close・自動 merge。
- `spec-reviewer`、`code-reviewer`、`qa-reviewer` の代替や bypass。
- 既存 workspace の retroactive migration を保証すること。
- 全 Epic への final quality Issue retroactive 強制。
- Single-Issue / docs-only / no-op Epic に separate final quality Issue を常時必須化すること。
- ChatGPT backend / browser / provider の implementation repair 自体。
- Raw transcript、credential、secret、host-local absolute path の durable repository storage。

## 5. 観測可能な成果

完了後に観測できること:

- Provider-side installed skill path に primary planning skills と manual backup planning skills が存在する。
- Primary planning skill を自然に呼ぶと、ChatGPT-first evidence route を最初に検討・実行する operating spine が示される。
- Manual backup skills は description /本文で human-approved emergency backup であることを明示し、通常 route として誤用されにくい。
- `spec-dock-chatgpt-authoring` は shared evidence lane のままで、canonical authority を主張しない。
- Workflow docs は Option 3+ の draft handoff、just-in-time canonical Issue Planning、drift feedback、final quality Issue policy を説明する。
- Epic plan template は final quality Issue required / skipped、Issue draft path index、pre-start canonical boundary を持つ。
- `src/spec_dock/cli.py` の managed skill list は manual backup skills を installed asset として配布対象に含む。
- `spec-dock init` / `spec-dock update` 相当の simulation で manual backup skills と updated docs/templates が installed output に現れる。
- Tests / docs inspection により、ChatGPT output が canonical adoption、reviewer pass、execution-ready、PR-ready、merge-ready を主張しないことが確認される。

完了後に観測できてはいけないこと:

- ChatGPT / browser capacity timeout から manual route へ自動 fallback する guidance。
- Manual backup skills が primary skills より上位・推奨・通常 route として案内されること。
- `spec-dock-chatgpt-authoring` が canonical docs owner、reviewer gate owner、execution-ready owner、PR delivery owner として扱われること。
- `authoring validate ...` の `pass` を reviewer pass または execution-ready と説明すること。
- Multi-Issue implementation Epic が final quality gate / PR delivery Issue なしで delivery complete を主張すること。
- Dogfooding workspace の `spec-dock/` 更新だけで provider-side source of truth が更新済みと扱われること。

## 6. 要件

- REQ-001: Existing planning skill names `spec-dock-initiative-planning` / `spec-dock-epic-planning` / `spec-dock-issue-planning` は ChatGPT-first primary route として維持される。
- REQ-002: Manual backup skill names `spec-dock-initiative-planning-manual` / `spec-dock-epic-planning-manual` / `spec-dock-issue-planning-manual` が provider-side installed skill assets として追加される。
- REQ-003: Manual backup skills は human-approved emergency backup と明記し、hard / unrecoverable ChatGPT / browser / automation / provider failure と explicit human approval を利用条件にする。
- REQ-004: 4 tab 上限、timeout、一時 browser / ChatGPT automation failure は `wait` / `retry` / `recover` の対象であり、manual route への自動 fallback 理由にしない。
- REQ-005: `spec-dock-chatgpt-authoring` は shared evidence lane として保持され、canonical docs、reviewer gates、assurance state、execution readiness、PR delivery を所有しない。
- REQ-006: Primary planning skills は ChatGPT / Oracle ZIP/tree output、candidate reports、draft docs を evidence-only として扱い、canonical adoption は main orchestrator / planning skill の EAL disposition、canonical rewrite、fresh `spec-reviewer` pass 後に限る。
- REQ-007: Initiative Planning は Epic candidates / Epic node creation 前に human approval gate を維持する。
- REQ-008: Epic Planning は Issue slicing、dependency order、responsibility boundary、Issue draft requirement / draft design / draft plan、final quality Issue candidate / skip rationale を handoff package として扱う。
- REQ-009: Epic Planning は child Issue の canonical `requirement.md` / `design.md` / `plan.md` を全件 upfront に正式化しない。
- REQ-010: Issue Planning は単一 workflow とし、入力差分を別モードとして分岐させない。入力は `requirement-heavy` / `draft-heavy` / `context-heavy` の context framing として扱い、最終出力は常に canonical `requirement.md` / `design.md` / `plan.md` とする。
- REQ-010a: Issue Planning は Epic Execution 中の Issue start 直前または直後に、入力 context、draft、current repository state、prior completed Issues、dependency state、unresolved ledgers を照合して canonical docs へ採用・部分採用・棄却・stale / blocked 判定する。
- REQ-011: Issue-local に吸収できない drift は Epic Planning repair / clarification / ADR へ戻す。対象は sibling Issue boundary、dependency order、final quality Issue responsibility、Epic E-RQ / E-AC closure、shared architecture、workflow policy、rollout strategy である。
- REQ-012: Multi-Issue implementation Epic は final quality gate / PR delivery Issue を持つ。
- REQ-013: Single-Issue / docs-only / no-op Epic は skip rationale と completion evidence を置く場合に separate final quality Issue を省略できる。
- REQ-014: `src/spec_dock/cli.py` の `_MANAGED_SKILL_NAMES` は manual backup skills を installed managed skill として配布する。
- REQ-015: Provider-side docs under `src/spec_dock/assets/spec_dock/docs/` は primary/manual route、Option 3+、draft lifecycle、final quality policy を説明する。
- REQ-016: Provider-side templates under `src/spec_dock/assets/spec_dock/templates/` は Epic plan handoff / final quality / skip evidence / issue draft path index を持つ。
- REQ-017: Accepted ADR と research の PlantUML diagrams は implementation で provider-side workflow docs / templates へ反映され、ADR-only evidence に留まらない。
- REQ-018: Dogfooding workspace updates are validation / confirmation unless explicitly scoped as dogfooding artifacts; provider-side assets are source of truth.
- REQ-019: Documentation and skills must not present unsupported `authoring` commands as available supported behavior.
- REQ-020: Tests and checks must include installed asset distribution, docs consistency, skill presence/order, forbidden authority claims, and Option 3+ wording.

## 7. 受け入れ条件（Acceptance Criteria）

- AC-001: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md` describes `spec-dock-chatgpt-authoring` as the primary evidence route for non-trivial Initiative planning and keeps Initiative canonical ownership / human approval gates in Initiative Planning.
- AC-002: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md` describes ChatGPT-first Epic planning, Issue draft handoff, Issue slice approval, and Option 3+ boundaries.
- AC-003: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md` describes a single ChatGPT-first Issue Planning workflow, treats `requirement-heavy` / `draft-heavy` / `context-heavy` as input context types rather than workflow modes, and performs draft adoption against current repository state / prior Issues / dependency state / unresolved ledgers.
- AC-004: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning-manual/SKILL.md` exists and is marked human-approved emergency backup.
- AC-005: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning-manual/SKILL.md` exists and is marked human-approved emergency backup.
- AC-006: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning-manual/SKILL.md` exists and is marked human-approved emergency backup.
- AC-007: Manual backup skills state that 4 tab saturation, timeout, transient backend failure, browser startup failure, and ordinary validation rejection first require wait / retry / recover / repair, not automatic manual fallback.
- AC-008: `src/spec_dock/cli.py` `_MANAGED_SKILL_NAMES` includes the three `-manual` skills and preserves the primary skill names as the normal planning entries.
- AC-009: `spec-dock-chatgpt-authoring` remains evidence-only and does not claim canonical adoption, reviewer pass, assurance mutation, execution-ready, PR-ready, merge-ready, Issue finish, or Epic completion authority.
- AC-010: `workflow_spec_authoring.md` states that ChatGPT evidence adoption requires EAL disposition, canonical rewrite, and fresh `spec-reviewer` pass.
- AC-011: `workflow_chatgpt_authoring_pack.md` explains primary planning skills as the route owner and ChatGPT authoring as evidence lane, not workflow owner.
- AC-012: `workflow_epic.md` and `phase_plan_epic.md` explain Option 3+ Epic draft handoff, Issue draft path index, and pre-start canonical Issue boundary.
- AC-013: `workflow_issue.md`, `phase_plan_issue.md`, or `authoring/issue-plan.md` explains draft adoption lifecycle and prohibits execution from draft-only / validation-only / raw ChatGPT output.
- AC-014: `src/spec_dock/assets/spec_dock/templates/epic/plan.md` contains final quality Issue required/skipped fields, skip rationale, completion evidence, dependency-on-all-implementation-Issues guidance, and intermediate deferred PR delivery policy.
- AC-015: Multi-Issue implementation Epic path requires final quality gate / PR delivery Issue; single-Issue / docs-only / no-op skip condition is explicit.
- AC-016: Accepted ADR / research PlantUML diagrams are incorporated into workflow docs or template guidance, not only referenced from ADR.
- AC-017: Provider-side source-of-truth paths are updated before dogfooding workspace mirrors.
- AC-018: `spec-dock init` / `spec-dock update` simulation confirms primary and manual skills are installed.
- AC-019: `./spec-dock/scripts/spec-dock validate` and `git diff --check` pass after changes or failures are recorded as blockers.
- AC-020: Relevant tests under `tests/cli_runtime/` or a focused equivalent confirm managed skill distribution and docs/template consistency.
- AC-021: `report.md` receives EAL / Spec Authoring Gate / implementation evidence entries when Codex adopts this draft; this ChatGPT draft itself does not claim that adoption occurred.

## 8. 除外条件（Exclusion Criteria）

- EC-001: ChatGPT output is treated as canonical source without EAL disposition.
- EC-002: Manual route is triggered automatically by ordinary ChatGPT capacity / timeout / browser failure.
- EC-003: Manual route can be used without explicit human approval evidence.
- EC-004: Existing primary planning skill names are renamed away from ChatGPT-first route.
- EC-005: Existing old route remains mixed into primary skill operating spine without `-manual` separation.
- EC-006: Provider-side source-of-truth paths are not updated, but dogfooding mirror is updated and treated as sufficient.
- EC-007: `authoring validate ... pass` is described as reviewer pass or execution-ready.
- EC-008: Multi-Issue implementation Epic may complete PR delivery without a final quality gate / PR delivery Issue or explicit accepted exception.
- EC-009: Docs/templates omit the accepted ADR diagrams and leave Option 3+ only in Issue-local ADR.
- EC-010: Unsupported commands are advertised as available supported user commands.

## 9. Risk signals / Edge cases

| Risk / Edge case | 要求される扱い |
|---|---|
| ChatGPT browser 4 tab saturation | `wait` / `retry`。manual fallback reason にしない。 |
| ChatGPT backend command unset | Fail-closed diagnostics。`local-context` or backend setup repair; manual route only human-approved hard failure。 |
| GitHub sync preflight blocked | Repo-aware invocation は止める。明示 `local-context` evidence mode は可能だが lower-authority / EAL required。manual route 自動移行はしない。 |
| ZIP rejected by safety validation | Unsafe output は採用しない。再生成・修正・別 evidence を検討。manual route への自動 fallback はしない。 |
| Manual skill appears before primary skill in installed list | 誤用リスク。managed order / README / docs で primary を先にする。 |
| Issue Planning changes sibling boundary | Issue-local で処理せず Epic Planning repair / clarification / ADR。 |
| Final quality Issue absent in multi-Issue implementation Epic | Epic plan / validation gate で block または Epic Planning repair。 |
| Single-Issue Epic forced into separate final quality Issue | 過剰プロセス。skip rationale と issue-level quality gate evidence で許容。 |
| Dogfooding mirror updated without provider assets | Source-of-truth drift。provider assets first へ戻す。 |
| Reviewer unavailable | `unavailable` / `denied` / `waived` は reviewer pass ではない。risk acceptance がない限り promotion / readiness は block。 |

## 10. 検証要求

最低限、実装 plan は次の commands / checks を含む。

```bash
git diff --check
./spec-dock/scripts/spec-dock validate
uv run pytest tests/cli_runtime
```

Installed asset simulation は環境に応じて次のような形で確認する。

```bash
tmpdir="$(mktemp -d)"
uv run spec-dock init "$tmpdir"
test -f "$tmpdir/.agents/skills/spec-dock-initiative-planning/SKILL.md"
test -f "$tmpdir/.agents/skills/spec-dock-epic-planning/SKILL.md"
test -f "$tmpdir/.agents/skills/spec-dock-issue-planning/SKILL.md"
test -f "$tmpdir/.agents/skills/spec-dock-initiative-planning-manual/SKILL.md"
test -f "$tmpdir/.agents/skills/spec-dock-epic-planning-manual/SKILL.md"
test -f "$tmpdir/.agents/skills/spec-dock-issue-planning-manual/SKILL.md"
test -f "$tmpdir/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md"
```

必要に応じて `spec-dock update` simulation も行い、既存 managed skill の上書きと manual skill 追加を確認する。

## 11. 未確定事項

この draft 作成時点で、Issue の product decision と accepted ADR は十分に確定している。実装中に判断が必要になり得る未確定事項は次に限る。

- Manual backup skills を `_MANAGED_SKILL_NAMES` 内で primary skill の直後に置くか、planning skill cluster の後半にまとめるか。
  - 推奨: primary skill の直後または primary planning cluster の直後。ただし primary skills が user-facing order で先に見えることを必須にする。
- PlantUML diagrams を `workflow_chatgpt_authoring_pack.md`、`workflow_epic.md`、`workflow_issue.md`、`phase_plan_epic.md` のどこへ重複なく置くか。
  - 推奨: end-to-end workflow は `workflow_chatgpt_authoring_pack.md` または `workflow_epic.md`、Issue draft lifecycle は `workflow_issue.md`、Epic plan template には短い reference / checklist を置く。
- Dogfooding mirror update の範囲。
  - 推奨: provider-side assets first。dogfooding workspace update は validation / confirmation として `report.md` に記録する。
