---
種別: 実装報告書（Issue）
ID: "iss-00358"
タイトル: "Simplify Authoring Kit and Document Contracts"
関連GitHub: ["#358"]
状態: "approved"
作成者: "main orchestrator"
最終更新: "2026-08-10"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00356", "init-local-00003"]
---

# iss-00358 Simplify Authoring Kit and Document Contracts — 実装報告

## 現在の結論

- Product Ownerは2026-08-10に、親EpicのRequirement / Design / Planと、本IssueのDraft 1を承認した。
- Draft 1と承認済みinterview decisionsはevidence-onlyの入力として正本`requirement.md`、`design.md`、`plan.md`へ統合し、repository factsと独立review findingsで精度を補った。
- Requirement、Design、Planはすべてapprovedで、各phaseのfresh `spec-reviewer`がpassした。
- 2026-08-10に`issue start iss-00358`を実行し、専用branch `iss-00358-simplify-authoring-kit-and-document-contracts`とactive contextを設定した。
- E00 / M0とS01〜S04を完了した。三scopeのthin R/D/P/Report、Authoring foundation、one-plan、四Completion Guide、187件のasset contract testを実装し、M1 commit前の検証とfresh reviewを通過した。S05以降、PR、merge、`issue finish`はまだ実行していない。
- E00の初回reviewで、read-only E00とS08で初めて作るpreservation fixtureのhash要求、S10より前のDesign外owner確定要求が両立しないことを検出した。Planを最小修正し、E00をcandidate inventory / no-delete routing、S08をfull fixture / hash、S10をfinal ownerへ分離した。fresh `spec-reviewer`はP0/P1なしでpassした。
- materialな製品判断の追加はない。Profile / Assuranceを使わず、one Plan + docs-only Planning Level、thin Report、Current六種というProduct Owner承認をそのまま保持する。

## 承認済み正本

| 文書 | 状態 | 主な固定内容 |
|---|---|---|
| `requirement.md` | approved | thin R/D/P/Report、文書責務、scope layering、Planning Level、Artifact / authority、Current / Historical、preservation / handoff |
| `design.md` | approved | exact asset tree / Add-Modify contract、template / Guide link、Report exact shape、Level examples、IC-1、ownership / rollback |
| `plan.md` | approved | E00〜S99の縦スライス、`CL-358-001`〜`CL-358-015`、step-local delegation、docs-only alternative evidence、具体テストカード、review gate |

## Spec Interpretation / Decision Ledger

- `DEC-358-001`
  - Status: resolved / promoted_to_plan
  - Type: plan contradiction / execution ordering gap
  - Trigger: E00 read-only baseline実行とfresh `spec-reviewer` review。
  - Observed facts: E00はExisting full fixtureの全preservation bytes/hashとDesign外ownerの確定を要求する。一方、full fixture/testのmaterializationはS08だけに許可され、Design外handoff manifestはS10で作る計画である。現HEADにはthin Report、candidate ADR、profile-derived node-local documentを含むfull fixtureがない。
  - Options Considered: preservation baselineをS08へ移す / E00前にfixture materialization stepを追加する / 現状のままsynthetic `ABSENT`をpass扱いする。
  - Disposition: `promoted_to_plan`。E00はcandidate inventoryまで、fixture bytes/hashはS08へ移し、Design外ownerは`no-delete / owner pending S10`として扱う。synthetic `ABSENT`をpreservation baseline passにはしない。
  - Evidence: E00 `repo-analyst` follow-up、初回E00 review fail（P1 x2、P2、P3）、amended Plan fresh `spec-reviewer` pass（P0/P1なし、P2はreport同期のみ、confidence 0.99）。
  - Affected closure: `CL-358-011/013`、E00、S08、S10、M0。
  - Risk if wrong: Existing preservationを証明せずS01へ進む、またはE00で禁止されたfixture mutationを行う。
  - Needs orchestrator decision: no。Plan amendmentとfresh reviewを完了した。
- `DEC-358-002`
  - Status: resolved / clarified_in_requirement_design
  - Type: requirement / design general-rule contradiction。
  - Trigger: S04 fresh `spec-reviewer` review。
  - Observed facts: `RQ-358-001`とDesign §5.1の一般規則は全scope templateの各sectionに一行promptを要求する一方、Product Owner採用済みの`AC-358-006`、Design §5.4、Plan S04はReportの三必須sectionを空本文で開始できるexact shapeとして固定している。
  - Disposition: より具体的なReport契約を維持し、一般規則の一行prompt対象をR/D/Pへ限定した。Reportはfrontmatter、Guide link、三必須headingを持つ非zero fileで、各sectionは空本文から開始する。
  - Evidence: `EAL-358-006`、S04 initial spec review fail（P1）、修正後Requirement / Design diff、S04 asset tests。
  - Affected closure: `CL-358-001/006`、`tc-s04-001`、S04。
  - Risk if wrong: Reportへ不要なpromptを再導入してempty-valid exact shapeを壊す、または一般規則との矛盾を残す。
  - Needs orchestrator decision: no。既承認のspecific contractを変えない整合化であり、fresh spec rereviewを必須とする。
- 既存のProduct Owner判断、Option A、thin Report、Current六種は変更しない。

## Objective Alignment Ledger

| target | primary objective evidence | secondary requirement evidence | inversion risk | reviewer verdict |
|---|---|---|---|---|
| planning adoption | `requirement.md`のAuthoring Kit簡素化を`design.md`のthin asset contractと`plan.md`の利用者flowへ直接追跡した | preservation、parity、IC-1、359 / 360 handoffをprimary contractへ従属させた | none | pass |

## Evidence Adoption Ledger

| ID | adoption_status | source | target | rationale | evidence | next_action |
|---|---|---|---|---|---|---|
| EAL-358-001 | adopted | `artifacts/20260809t125148z-draft-requirement-strict-vertical-slice-requirement.md` | `requirement.md` | Product OwnerがDraft 1とOption Aを承認し、interview decisionsと親Epic契約へ照合して正本化した | `requirement.md`とfresh requirement review pass | execute approved plan |
| EAL-358-002 | adopted | `artifacts/20260809t125149z-draft-design-strict-vertical-slice-design.md` | `design.md` | approved Requirementをexact asset path、thin contract、navigation、preservation、handoffへ割り当てた | `design.md`とfresh design review pass | execute approved plan |
| EAL-358-003 | adopted | `artifacts/20260809t125150z-draft-plan-strict-vertical-slice-plan.md` | `plan.md` | Draftのvertical sliceをStrict Plan契約へ統合し、closure、ownership、docs-only verification、test cardを具体化した | `plan.md`と最終fresh plan review pass | execute approved plan |
| EAL-358-004 | adopted | `artifacts/20260808t083300z-interview-issue-profile-and-draft-routing.md` | `requirement.md` | Profile / Assuranceを完全に外し、複雑なworkflow機構を導入しない判断を固定した | `requirement.md`のProduct Owner判断とscope | execute approved plan |
| EAL-358-005 | adopted | `artifacts/20260808t085519z-interview-planning-level-authoring-architecture-adoption.md` | `requirement.md` and `design.md` | Option Aのone Plan + Base Guide + four independent Completion Guidesを固定した | `requirement.md` RQ-358-004と`design.md` §7 | execute approved plan |
| EAL-358-006 | adopted | `artifacts/20260809t025001z-interview-target-report-contract.md` | `requirement.md` and `design.md` | Reportを三必須heading + optional Notes、empty-valid、non-gatingに固定した | `requirement.md` AC-358-006と`design.md` §5.4 | execute approved plan |

未解決のstale / blocked evidenceはない。Draft / interview artifactsは履歴証跡として保持し、正本authorityにはしない。

## Spec Authoring Gate

| phase | investigated facts | open questions / answers | adoption decision | reviewer verdict | blocking | promotion / next_action |
|---|---|---|---|---|---|---|
| requirement | 親Epic R/D/P、承認済みDraft 1、三つのinterview decisions、現行template / docs / preservation surfaceを照合した | none | adopted | pass | no | execute approved plan |
| design | 承認済みRequirement、provider / dogfood asset tree、copy mechanism、Guide / template / Historical ownershipを照合した | none | adopted | pass | no | execute approved plan |
| plan | 承認済みR/D、全RQ / EC / AC、Design file-change contract、Issue 357とのIC-1境界、E00 / S08 / S10 ownershipを照合した | none | amended and adopted | pass | no | execute amended plan |

## Delegated Draft Evidence

| created_by_role | scope_id | artifact draft path | source_paths | intended_targets | adoption_status | reflected_to | diff_guard_result | integration_result | rejected portions | blockers | reviewer result | promotion decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ChatGPT-use-strict | iss-00358 | `artifacts/20260809t125148z-draft-requirement-strict-vertical-slice-requirement.md` | 親Epic R/D/P、baseline SHA `2c75e0c02cb65a6e74040a72dc161d342d661091`、approved interview decisions | `requirement.md` | adopted | `requirement.md` | pass: canonical diff inspected and reviewer findings integrated | Draft 1 requirement integrated with approved Option A and Report decisions | none | none | pass | execute approved plan |
| ChatGPT-use-strict | iss-00358 | `artifacts/20260809t125149z-draft-design-strict-vertical-slice-design.md` | `requirement.md`、parent Design / Plan、provider / dogfood asset inventory | `design.md` | adopted | `design.md` | pass: canonical diff inspected and reviewer findings integrated | Draft 1 design integrated with exact paths and ownership | none | none | pass | execute approved plan |
| ChatGPT-use-strict | iss-00358 | `artifacts/20260809t125150z-draft-plan-strict-vertical-slice-plan.md` | `requirement.md`、`design.md`、Strict Plan Guide、specialist evidence | `plan.md` | adopted | `plan.md` | pass: canonical diff inspected and final plan review passed | Draft 1 plan integrated as executable step-local contract | none | none | pass | execute approved plan |

## Grade Specialist Evidence Gate

| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |
|---|---|---|---|---|---|
| strict | system-architect and implementation-planner | used | system-architectのexact authoring tree / thin shape / empty-valid Report / parity / preservation / IC-1境界を`design.md`へ統合し、implementation-plannerのE00・S01〜S10・S90・S99 slicingを`plan.md`へ統合した | pass | ready |

## Reviewer Gate Status

| phase | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | evidence |
|---|---|---|---|---|---|---|---|
| requirement | requirement phase gate | spec-reviewer | fresh | pass | no | execute approved plan | parent trace、Planning Level selection、Guide semantics、full preservation surfaceを確認 |
| design | design phase gate | spec-reviewer | fresh | pass | no | execute approved plan | exact paths、Report shape、Level examples、handoff timing、file-change contractを確認 |
| plan | amended plan alignment gate | spec-reviewer | fresh | pass | no | execute amended plan | E00 candidate inventory、S08 fixture/hash、S10 final ownerの一意性を確認。P0/P1なし、overall confidence 0.99 |
| E00 | E00 docs/spec alignment gate | spec-reviewer | fresh | pass | no | E00 / M0を閉じてS01へ進む | Design §4.1 baseline、preservation candidate category、Design §4外no-delete / owner pending S10を確認。初回fail事項はPlan amendmentでrouting済み |
| S01 code | S01 docs / test gate | code-reviewer | fresh | pass | no | `CL-358-003` code evidence accepted、fresh spec reviewへ進む | findingsなし。provider / dogfood projection、責務、scope、link、provider-neutral contract、49 tests / ruff / format / diff checkを確認。confidence 0.99 |
| S01 spec | S01 semantic / scope gate | spec-reviewer | fresh | pass | no | S01 semantic evidence accepted、P2を修正してcode delta reviewへ進む | P0/P1なし。四文書責務、三scope、親scope非再定義、provider-neutral入口、parityを確認。P2 scope-aware Plan導線は修正・回帰test追加済み。confidence 0.98 |
| S01 P2 code delta | scope-aware Plan routing gate | code-reviewer | fresh | pass | no | `CL-358-003` close、S02へ進む | findingsなし。IssueとInitiative / EpicのPlan導線、6 projection files、回帰test、byte parity、report evidenceを確認。confidence 0.96 |
| S02 code | thin R/D/P template / test gate | code-reviewer | fresh | pass | no | S02 code evidence accepted | 9 R/D/P、templates README、provider / dogfood parity、118 testsを確認。P0/P1なし。snake_case禁止語彙P2は修正しfresh delta review pass。confidence 0.98 |
| S02 spec | S02 semantic / scope gate | spec-reviewer | fresh | pass | no | `CL-358-001/002`のR/D/P部分をclose、S03へ進む | Design §5.1〜§5.3との整合を確認。P0/P1なし。catalog完全一致とreport件数同期のP2を修正。confidence 0.98 |
| S02 P2 code delta | snake_case forbidden field gate | code-reviewer | fresh | pass | no | P2 close | `_`区切り3種のmutationとfalse-positive guard、全118 tests、S02 66 testsを確認。findingsなし。confidence 0.98 |
| S02 P2 spec delta | exact scope catalog gate | spec-reviewer | fresh | pass | no | P2 close、S02完了 | provider / dogfood各scopeの4 Markdown完全一致、余分なR/D/P alias mutation、Report非変更を確認。findingsなし。confidence 0.99 |
| S03 code | one-plan / Completion Guide / test gate | code-reviewer | fresh | fail | no | critical recovery P1修正とfresh rereviewが必要 | one-plan、Guide独立性、選択例、非Runtime所有を確認したが、critical recoveryを`N/A`可能と読めるP1を検出。confidence 0.96 |
| S03 spec | Planning Level semantic gate | spec-reviewer | fresh | pass | no | S03 semantic evidence accepted | Design §7、`CL-358-004/014`、impact / recovery選択、wrong-signal rejection、projection parityを確認。findingsなし。confidence 0.99 |
| S03 P1 code delta | critical recovery / N/A gate | code-reviewer | fresh | pass | no | P1 close、`CL-358-004/014` close、S04へ進む | migrationだけを理由付きN/Aにし、不可逆性と復旧手段は省略不可。mutation Red、回帰test、parityを確認。P0/P1なし、report同期P2を反映。confidence 0.99 |
| S04 code | thin Report / test gate | code-reviewer | fresh | pass | no | code evidence accepted、P2 test補強へ進む | exact shape、empty-valid、non-gating、parityを確認。generic禁止語検出不足P2だけを指摘。confidence 0.96 |
| S04 spec | Report exact shape / non-gating gate | spec-reviewer | fresh | fail | no | RQ / Design一般prompt規則の矛盾修正が必要 | 実装はDesign §5.4に一致するが、RQ-358-001 / Design §5.1の一行prompt一般規則とのP1矛盾を検出。confidence 0.99 |
| S04 P2 code delta | Report forbidden vocabulary gate | code-reviewer | fresh | pass | no | P2 close | template / Guide別detector、mandatory reviewerとneutral boundary、Grade / Assurance / delegated authoring / PR status mutationを確認。findingsなし。confidence 0.97 |
| S04 spec rereview | Report prompt exception alignment gate | spec-reviewer | fresh | pass | no | P1 close、`CL-358-001/006`のReport部分をclose | RQ-358-001 / Design §5.1へReport empty-valid例外を明記し、§5.4、DEC-358-002、assets / testsとの整合を確認。confidence 0.99 |

## Workflow-Scoped Authorization

| authorization source | repo / worktree | active scope | named roles | boundary | result |
|---|---|---|---|---|---|
| ユーザーによるSpecDock workflow利用依頼と2026-08-10の文書承認 | current `spec-dock` checkout | iss-00358 planning | system-architect、implementation-planner、spec-reviewer | current repo / scope / session内のread-only planning / review。実装、外部公開、PR、mergeは含まない | pass |
| ユーザーによる2026-08-10の`issue start`と実装開始依頼 | `/Volumes/990p2t/offloaded/home/iwasawayuuta/.codex/worktrees/4bc6/spec-dock` | active `iss-00358` execution | repo-analyst、doc-writer、dev-coder、spec-reviewer、code-reviewer、qa-reviewer | approved Planのstep-local scope内の実装・検証・review。scope拡張、外部公開、PR、merge、`issue finish`は含まない | pass |

## 実装開始契約

| 最初のstep | 担当 | 入力 | 完了条件 |
|---|---|---|---|
| E00 | `repo-analyst` | approved R/D/P、baseline SHA、Design §4.1 asset / link / preservation surface | Design §4.1 rowにAction / 358 owner / 既存hash / planned testがあり、preservation candidateはS08、Design §4外はno-delete / owner pending S10で、暗黙Deleteがない |
| S01以降 | stepごとのfresh `doc-writer` / `dev-coder` | `plan.md` §9の該当contract | Redまたはdocs-only代替証拠、Green、report更新、fresh reviewer passをstep単位で満たす |

Issue 357とは同時に進められる。358はtemplate prose / Authoring Guideのsingle writerであり、Runtime / parser / scaffold mechanismを編集しない。両者の実生成契約はS09 / IC-1で照合する。

## 計画時の検証結果

- Canonical Requirement review: pass。
- Canonical Design review: pass。
- Canonical Plan final review: pass、findingsなし、confidence 0.98。
- Exact-current R/D/P/report readiness review: pass、findingsなし、confidence 0.98。E00/M0、S09〜S90/M4、S99/M99のreview / commit / clean check契約を確認した。
- `git diff --check`: pass。
- SpecDock `workflow status --format json`: `state=ready`、`reason_code=strict-legacy-missing-assurance`、`artifact_readiness=substantive`。
- SpecDock `deps check --no-github`: `ready=true`、blockerなし。cacheは`stale=true`の警告を返したため、実装開始時に必要ならGitHub同期を更新する。
- SpecDock `validate`: pass、`nodes=221`。
- `uv run pytest tests/unit/domain/test_workflow_state.py tests/cli_runtime/test_workflow.py`: 72 passed、44 skipped。
- `docs/rules/**`はPlanの許可変更から除外し、S04はIssue 357 evidenceなしでthin Report assetだけを完了できる。
- 正本とDraft / interview artifactsは別物として保持し、evidenceをauthorityへ自動昇格していない。

## 実装記録

E00を開始し、`repo-analyst`へ承認済みPlan §9のread-only baseline調査を委任した。managed asset、copy depth、relative link、preservation fixture、Historical / obsolete ownershipを確認した結果、preservationの実在baseline bytesとDesign外single ownerが未確定であることを検出した。asset、source、tests、user content、metadata、deps、active、Git stateは変更していない。

### E00 Asset Baseline Manifest

- Baseline revision: `2c75e0c02cb65a6e74040a72dc161d342d661091`
- Current revision: `e16e97517ea3ab7287eaf6143fab2df943d71b2d`
- Provider root: `src/spec_dock/assets/spec_dock/`
- Dogfood root: `spec-dock/`
- 現存するModify assetはbaseline / current provider / current dogfoodで同一SHA-256かつbyte-exactである。
- Add assetはbaseline / current provider / current dogfoodの双方で`ABSENT`であり、未実装状態をbaselineとして固定した。

| Action | provider / dogfood relative path | baseline SHA-256 | owner | planned test |
|---|---|---|---|---|
| Modify | `templates/initiative/requirement.md` | `a74e30027884b35c4e4042d42b8b34c9c51c206843b9ada0441a365ce6b81200` | 358 S02 | `test_authoring_kit_assets.py` |
| Modify | `templates/initiative/design.md` | `f35a7de65c038c7a381f41ce6af2100e3c66d21b39d00f10d3634f363b9d3c5c` | 358 S02 | 同上 |
| Modify | `templates/initiative/plan.md` | `f65bb64d401f066996255cd6611415d36431c36ceb3a805b6210d1130ef8200c` | 358 S02 | 同上 |
| Modify | `templates/initiative/report.md` | `affd94568ac058e4d8175d8142e96b29269ea3c58120b84b0c6957e00ecf564d` | 358 S04 | report contract test |
| Modify | `templates/epic/requirement.md` | `221052bbb960fcfb13ff8357cb0a51b1c408c85f97a51e411740d8783dd3d2b5` | 358 S02 | `test_authoring_kit_assets.py` |
| Modify | `templates/epic/design.md` | `d3a33eaa61bc5fe5c80538681028929420ed8070ce3aaaab1ae0d2de9201eee5` | 358 S02 | 同上 |
| Modify | `templates/epic/plan.md` | `5adb68c4469c2ae59ccfa8bb653205fd6171cc842bcbde12714c7023b46fe8d4` | 358 S02 | 同上 |
| Modify | `templates/epic/report.md` | `60526a51ca964021e8288eabcf500dbf749d0b547e7a70f002bcb812d913e170` | 358 S04 | report contract test |
| Modify | `templates/issue/requirement.md` | `baa26eaeea94a383c5b00ac21d02ecea156949ade96dc5bfec4f0b30c6d9aa8e` | 358 S02 | kit test + 357 IC-1 |
| Modify | `templates/issue/design.md` | `4838f34660ae63bf587f4cef1b7fd4e275dd4ebc6807395e4a50593629bf00a9` | 358 S02 | 同上 |
| Modify | `templates/issue/plan.md` | `6f0ea3b721089b494a4272da1317896ff5f547daf97c851ca125c2346ea0200e` | 358 S02/S03 | kit test + 357 IC-1 |
| Modify | `templates/issue/report.md` | `b32dfe412048ce02cc9bb7c7ee5ab78b134b0456a37aab3e531655fb292b09e3` | 358 S04 | report contract test |
| Modify | `templates/artifacts/blank.md` | `9016ecc30e70a6eabf4724ed65321dab103413a088249e089ec7727a3a6c4c1d` | 358 S05 | `test_artifact_templates.py` |
| Modify | `templates/artifacts/research.md` | `6c1aefd91f117e0c7349fd4697796a92ac3f4d41f80ba5941e0437662aae1f7b` | 358 S05 | 同上 |
| Modify | `templates/artifacts/interview.md` | `aa46c93199730c9895b488a1385eeb8c1a587869faec361fe115c482b5e0d5af` | 358 S05 | 同上 |
| Modify | `templates/artifacts/disc.md` | `468e137fa3c8e0a0882592995521d185e31a198adc6d7c961134e2eeb323dedb` | 358 S05 | 同上 |
| Modify | `templates/artifacts/decision-candidate.md` | `b58fc3e0afc818ec45b8b170ad8dcd7aebe43557886b281f3137f5fa32ba9ed5` | 358 S05 | 同上 |
| Modify | `templates/artifacts/adr.md` | `234bfae1b12c2715f83280c1527cf687a4cdd84f74f774b722418eba483c2d49` | 358 S05 | 同上 |
| Modify | `templates/README.md` | `f66e45f17217f6ab70ac7ecfae86e233028ebbe85e4e1d922f7412ca2abc5204` | 358 S05/S06 | catalog / navigation test |
| Modify | `docs/README.md` | `314bccd5ad0b68aaab31445864279db8083e391e40131e621cf0dbd8c4473d18` | 358 S06 | navigation / link test |
| Modify | `docs/guide.md` | `21fca9bcf9edc0a90185095ab0510fbaf6946c49dba9dcf8822ec326c09045cf` | 358 S06 single editor | navigation / link test |
| Modify | `docs/authoring/issue-plan.md` | `bc6f633c47143d8acac7d3714198f3ce73b09c4f8e38c1d55d9365205c171909` | 358 S03 | level / link + 357 IC-1 |
| Modify | `docs/authoring/scope-layering.md` | `3fd724638107f4334f52761297decaaa9e777d42dbe53a576a9377f2359a6167` | 358 S01 | Guide contract test |
| Add | `docs/authoring/overview.md` | `ABSENT` | 358 S01 | `test_authoring_kit_assets.py` |
| Add | `docs/authoring/requirement.md` | `ABSENT` | 358 S01 | 同上 |
| Add | `docs/authoring/design.md` | `ABSENT` | 358 S01 | 同上 |
| Add | `docs/authoring/report.md` | `ABSENT` | 358 S01 foundation / S04 exact Report contract | S01 Guide contract + S04 report contract test |
| Add | `docs/authoring/artifacts.md` | `ABSENT` | 358 S05 | artifact / catalog test |
| Add | `docs/authoring/historical.md` | `ABSENT` | 358 S06 | navigation / vocabulary test |
| Add | `docs/authoring/issue-plan-levels/light.md` | `ABSENT` | 358 S03 | level / link test |
| Add | `docs/authoring/issue-plan-levels/standard.md` | `ABSENT` | 358 S03 | 同上 |
| Add | `docs/authoring/issue-plan-levels/strict.md` | `ABSENT` | 358 S03 | 同上 |
| Add | `docs/authoring/issue-plan-levels/critical.md` | `ABSENT` | 358 S03 | 同上 |
| Add | `tests/unit/infra/test_authoring_kit_assets.py` | `ABSENT` | 358 S01-S08 | file / heading / link / vocabulary / parity / preservation |
| Modify | `tests/unit/infra/test_artifact_templates.py` | `05ad6dc5398fb08f0560b539b78aeb8b8333947b6c471747bfe482b87ce341fd` | 358 S05 | Current six / Historical split |

### E00 Copy Depth / Link Evidence

- `template_scaffolder.py`は`spec-dock/templates/<kind>/`をrootとして再帰copyし、node destinationへrelative pathを保持する。
- UTF-8 templateはplaceholder置換後にbytesが変わらなければ`copy2`、変わればrendered bytesを書き出す。
- 現行12 scope templateのMarkdown linkは0件であり、Guide linkはS02/S04で新設する。
- destination起点のGuide rootはInitiative `../../docs/authoring/`、Epic `../../../../docs/authoring/`、Issue `../../../../../../docs/authoring/`である。provider template格納位置を起点にしない。

### E00 Preservation Fixture Baseline

次表はbounded follow-upで得たS08向けcandidate manifestであり、E00のbaseline pass evidenceではない。candidate exact test pathは`tests/unit/infra/test_authoring_kit_assets.py`、fixture rootは`tests/fixtures/authoring_kit/existing_issue/`である。fixture/testは未作成で、synthetic rowのbytes/hashは未固定であるため、Plan amendmentとS08 materialization前に`CL-358-011`をclosedにしない。

| fixture relative path | category | source | before SHA-256 | owner / planned test |
|---|---|---|---|---|
| `requirement.md` | canonical R | `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00246-dogfooding-update-runtime-mirror-sync/requirement.md` | `d7a943b0b568186b93957b77d07d01e2c58046f9bd8ad7e573f9c4f2e2ed0c8e` | 358 S08 / preservation |
| `design.md` | canonical D | `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00246-dogfooding-update-runtime-mirror-sync/design.md` | `c8ce7eee921677d7b71ffff9917cc7e494d20d64ee3ae0454b3743721766388d` | 同上 |
| `plan.md` | canonical P | `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00246-dogfooding-update-runtime-mirror-sync/plan.md` | `8d2db2a601c0d6a4459f903204f2bf1e1694fb3c1e1c31a4eb6ceb0a699c8a7a` | 同上 |
| `report-heavy.md` | heavy Report | `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00246-dogfooding-update-runtime-mirror-sync/report.md` | `1602d6e382993ab9ce24c0af790c5257b32295caa350a20f0cd83f2e59675b67` | 同上 |
| `report-thin.md` | thin Report | synthetic | `ABSENT` | 同上 |
| `artifacts/blank.md` | Current blank | `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00259-artifacts-directory-future-only-adoption/issues/iss-00268-dogfood-artifacts-without-migrating-discussions/artifacts/20260701t145916z-dogfood-blank-artifact.md` | `ca97502f2f3dfb44da9cc2b6f17d53ec178425787e5ca8f6081184e5b71e3687` | 同上 |
| `artifacts/research.md` | Current research | `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00356-specdock-core-simplification-and-external-intelligence-boundary/issues/iss-00358-simplify-authoring-kit-and-document-contracts/artifacts/20260808t082616z-research-authoring-kit-clarification.md` | `0b0c310e184ec9453fe9dfc88ffef1aa24abc9b077ca73610897858f8da020c4` | 同上 |
| `artifacts/interview.md` | Current interview | `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00356-specdock-core-simplification-and-external-intelligence-boundary/issues/iss-00358-simplify-authoring-kit-and-document-contracts/artifacts/20260808t083300z-interview-issue-profile-and-draft-routing.md` | `9292241a07bda6c3282c77ea6c3c28362bafe33408bc1501a67b97db0c05080c` | 同上 |
| `artifacts/disc.md` | Current disc | `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00356-specdock-core-simplification-and-external-intelligence-boundary/issues/iss-00358-simplify-authoring-kit-and-document-contracts/artifacts/20260809t042432z-disc-strict-clarification-authoring-handoff-358.md` | `69e01e33d6a4fda374e54b21153d8bb07f3f2a7f2d571bf8742a0fc701cbbd3d` | 同上 |
| `artifacts/decision-candidate.md` | Current decision-candidate | `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00270-upstream-planning-governance-and-templates/artifacts/20260702t071230z-decision-candidate-epic-planning-issue-draft-composition-workflow.md` | `f21a9221303207669e9b083125cba19ecc63095f6aef31e04cb68efa214409ed` | 同上 |
| `artifacts/adr.md` | Current accepted ADR | `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00259-artifacts-directory-future-only-adoption/artifacts/20260701t055644z-adr-artifacts-future-only-command-unification.md` | `45a216303a4d40ae520809de567a22fa855b12c90fddf3e3eacc64c587ceb183` | 同上 |
| `artifacts/adr-candidate.md` | candidate ADR | synthetic | `ABSENT` | 同上 |
| `artifacts/legacy/draft-requirement.md` | Historical draft | `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00356-specdock-core-simplification-and-external-intelligence-boundary/issues/iss-00358-simplify-authoring-kit-and-document-contracts/artifacts/20260809t125148z-draft-requirement-strict-vertical-slice-requirement.md` | `238a3fc61c205ba96e832214c07c21271ebb37ff3d03a8e60d31dfc5b244e1b6` | 同上 |
| `artifacts/legacy/pr-repair.md` | Historical repair | `spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00343-workbench-shell-and-explicit-file-artifact-import/issues/iss-00344-workbench-shell-scaffolding/artifacts/20260729t141053z-disc-pr-350-repair-u001-uninstall-managed-inventory.md` | `63111299f7da51fe129fb288359aa86f8a4103cd737aead4473efaf1cd2bd649` | 同上 |
| `artifacts/legacy/generic-import.zip` | generic import | `spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00343-workbench-shell-and-explicit-file-artifact-import/issues/iss-00346-integration-distribution-and-final-quality/artifacts/20260730t173917z--specdock-iss-00346-authoring-pack-corrected.zip` | `5a0252dc24db5e718a9e328b79c6f4042312d7ded54aaddafd4c7c57f48b252a` | 同上 |
| `discussions/scratch.md` | Historical scratch | `spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00107-worktree-provisioning/issues/iss-00143-manage-external-git-worktrees/discussions/20260530t000000z-scratch-external-worktree-management.md` | `13d58db407ccdb170c67f0f88a915ae7c76b97e0732a3e24165ce856d0f48200` | 同上 |
| `discussions/note.md` | Historical note | `spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00048-agent-facing-interface-hardening-and-host-adapter-scaffolding/issues/iss-00050-host-adapter-scaffold-and-final-parity/discussions/20260403t161053z-note-s03-triage-resolution.md` | `c450806f5b1c3349dc1e1bb870a1165a0a509bbbb8aa59c640790ce3e74e14c8` | 同上 |
| `discussions/legacy-discussion.md` | Discussion | `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00246-dogfooding-update-runtime-mirror-sync/discussions/20260630t083605z-pr-repair-batch-pr-repair-batch.md` | `191d3c6fe1f149cfa969981dd859a5c4b7efd7bfa69db9e4cb2fdb6f8b75f2ad` | 同上 |
| `.assurance.json` | Assurance | `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00246-dogfooding-update-runtime-mirror-sync/.assurance.json` | `f0f6ef47171ab67360ed7c26b8dc144e4ba588c7abe1234115c4373bebcca4c8` | 同上 |
| `artifacts/legacy/profile-derived-design.md` | profile-derived design | synthetic | `ABSENT` | 同上 |
| `artifacts/legacy/profile-derived-plan.md` | profile-derived plan | synthetic | `ABSENT` | 同上 |

### E00 Historical / Obsolete Non-Delete Inventory

| candidate | classification / owner |
|---|---|
| `src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md`とdogfood counterpart | no delete。Historical recognitionは357、managed pruneは360。single owner assignmentはS10 / 360 planningへ保留 |
| `src/spec_dock/assets/spec_dock/templates/discussions/{adr,disc,interview,pr-repair-batch,research,scratch}.md`とdogfood counterparts | no delete。Historical recognitionは357、managed pruneは360。single owner assignmentはS10 / 360 planningへ保留 |
| `src/spec_dock/assets/spec_dock/templates/assurance/profile-sections.json`とdogfood counterpart | no delete。Profile / Assurance mechanismは357、managed pruneは360。single owner assignmentはS10 / 360 planningへ保留 |
| `src/spec_dock/assets/spec_dock/templates/issue-profiles/{lite,standard,strict,critical}/{design,plan}.md`とdogfood counterparts | no delete。Profile routingは357、managed pruneは360。single owner assignmentはS10 / 360 planningへ保留 |
| `src/spec_dock/assets/install_root/.agents/skills/**`とinstalled counterparts | no delete。skill contract / contentは359、distribution / pruneは360。single owner assignmentはS10 / 360 planningへ保留 |
| `src/spec_dock/assets/spec_dock/docs/authoring/chatgpt-pack.md`、`src/spec_dock/assets/spec_dock/docs/authoring/decision-routing.md`、`src/spec_dock/assets/spec_dock/docs/rules/**`、`src/spec_dock/assets/spec_dock/docs/reference_*.md`、`src/spec_dock/assets/spec_dock/docs/phase_*.md`、`src/spec_dock/assets/spec_dock/docs/workflow_*.md`、`src/spec_dock/assets/spec_dock/templates/.workbench/**`とdogfood counterparts | Design §4外。no delete。exact classification / ownerは未確定で、S10 / 360 planningへ保留 |

暗黙Delete rowは0である。thin Report、candidate ADR、profile-derived documentの実在baseline bytesはS08 materialization input、Design §4外surfaceのsingle ownerはS10 handoff inputとして明示されており、amended E00のstop conditionには該当しない。実行したread-only commandは`git status --short`、`git branch --show-current`、`git rev-parse`、`git cat-file`、`git show`、`find`、`rg`、`sed`、`nl`、`shasum -a 256`。`No material implementation decisions beyond the approved plan.`

### Step Contract Closure

| step | closure ids | planned close condition | observed evidence | result | notes |
|---|---|---|---|---|---|
| E00 | `CL-358-010`（`CL-358-011/013` candidate evidence） | Design §4.1 rowを固定し、preservation候補をS08、Design §4外no-delete rowをS10へroutingする | managed asset baseline、21 preservation candidate row、Design §4外no-delete / owner pending S10を収集済み | passed | `CL-358-011/013`はS08 / S10でcloseする |
| S01 | `CL-358-003` | OverviewからR/D/P/Reportと三scope責務へ到達し、provider固有workflowを必須化しない | provider / dogfoodへ8 assetを反映し、Issue Plan基礎、三scope Plan責務、scope-aware Plan導線、Current入口、全relative linkを実装 | passed | initial P1とnonblocking P2を修正し、52 focused tests、fresh code / spec review pass |
| S02 | `CL-358-001/002`（R/D/P部分） | 9 R/D/Pを最小frontmatter / heading / 一文prompt / scope別Guide linkへ置換する | provider / dogfoodの9 R/D/Pとtemplates READMEを同時更新し、旧workflow / quality gate fieldを除外。66 focused tests、全118 tests、ruff / format / diff check pass | passed | fresh code / spec review pass。Report部分はS04でcloseする |
| S03 | `CL-358-004/014` | one canonical Issue Plan、Base + 四独立Guide、impact / recovery選択例、Runtime / metadata非所有を成立させる | provider / dogfoodへBase + four Guidesを反映。6 Example ID、wrong-signal rejection、one Plan、独立link、Level別completion contractを22 testsで固定 | passed | critical recoveryのP1を修正。全140 tests、plan / level focused 43 tests、ruff / format / diff check、fresh code / spec review pass |
| S04 | `CL-358-001/006`（Report部分） | 三scopeReportをexact三heading、empty-valid、non-gatingへ置換する | provider / dogfoodの3 Report templateとReport Guideを更新。最小frontmatter、scope link、empty H2、optional Notes、forbidden ledger / gate、durable decision境界を47 testsで固定 | passed | prompt一般規則P1と禁止語P2を修正。全187 tests、report focused 53 tests、ruff / format / diff check、fresh code / spec review pass |

### Test Contract Closure

| test id | step | evidence level | pre-implementation evidence | verification path | observed result |
|---|---|---|---|---|---|
| `tc-e00-001` | E00 | inspect-only | baseline `2c75e0c0`とcurrent `e16e9751`のasset / hash / link / copy-depthを比較 | amended Plan §9 E00のtree / link / existing hash / S08-S10 routing inspection | pass: Design §4.1 baselineを固定し、未materialize categoryとpending ownerを後続へ一意にroutingした |
| `tc-s01-001` | S01 | red-required | provider / dogfoodで四Guideとnavigationが欠落 | initial implementation後に16 focused tests pass | fail: Current Overviewが旧workflow必須の`issue-plan.md`へ到達し、全link / 責務方向のtest defectも残る。S01でPlan基礎を中立化して再実装する |
| `tc-s01-001-rerun` | S01 | red-to-green repair | initial code/spec review P1:旧Issue Plan、scope別Plan不足、link / 責務方向 / mandatory検出不足。spec review P2: scope別Plan導線 | `uv run pytest tests/unit/infra/test_authoring_kit_assets.py -q`、ruff check / format、diff check | pass: 52 tests。全foundation / navigation link、section別責務方向、三scope Plan、scope-aware Plan導線、8 provider-dogfood parity、固有provider/model mandatory mutationを検出 |
| `tc-s02-001` | S02 | red-required | HEAD旧版は`artifact_state`、Assurance workflow、複数状態、作成者、長文方針をtemplateへ含み、thin contractを満たさなかった。P2 mutationはsnake_case 3件と余分なcatalog alias 3件で各`3 failed, 115 deselected`を再現 | `uv run pytest tests/unit/infra/test_authoring_kit_assets.py -k 'template and not report' -q`、全focused suite、ruff check / format、diff check | pass: S02 66 tests / 52 deselected、全118 tests。exact scope catalog、frontmatter / placeholder / `draft`、exact headings、一文prompt、rendered link、Issue限定Planning Level、禁止語彙、10 path parityを確認 |
| `tc-s03-001` | S03 | red-required | pre-S03では四Completion GuideとBaseからのlinkが未存在。level別Planはなくcanonical `plan.md`一つだけだった | `uv run pytest tests/unit/infra/test_authoring_kit_assets.py -k 'plan or level' -q`、全focused suite、link / parity / Runtime no-diff inspection | pass: one `plan.md`、Baseから四Guide、各GuideからBaseだけへのlink、必須5 section、provider / dogfood 5 path parityを確認 |
| `tc-s03-002` | S03 | red-required | pre-S03では`LEVEL-EX-POS-01`〜`03` / `NEG-01`〜`03`と選定結論tokenが未存在。critical旧曖昧文のmutationでrecovery評価をN/Aにできる欠陥を`AssertionError`で再現 | 同上。Example row、wrong-signal rejection、docs-only token、critical migration-only N/A / recovery必須をstructural assertion | pass: 6 Example ID、impact / recovery基準、standard非Runtime default、metadata非所有、critical recovery省略禁止を確認。全140 tests、focused 43 passed / 97 deselected |
| `tc-s04-001` | S04 | red-required | HEAD旧3 Reportは`状態` / `作成者`、Decision / Evidence Ledger、EAL、各種Gate、session log、progress summaryを含み、exact三heading / empty-validを満たさなかった。mandatory reviewer / generic禁止語mutationも不足を再現 | `uv run pytest tests/unit/infra/test_authoring_kit_assets.py -k report -q`、全focused suite、ruff check / format、diff check | pass: report 53 passed / 134 deselected、全187 tests。exact shape / empty body、optional Notes、scope link、4 path parity、heavy + generic禁止語、neutral reviewer境界、non-gating / durable boundaryを確認 |

### Delegated Worker Evidence

| step | delegated role | worker summary | changed files | tests or docs-only verification | reviewer verdict | unresolved risks | integration decision |
|---|---|---|---|---|---|---|---|
| E00 | `repo-analyst` | 35 managed/test row、21 preservation candidate row、copy-depth / link、Historical / obsolete ownershipをread-onlyで調査 | none | SHA-256 / parity / link / source-path inspectionを実施 | pass under amended E00 contract | full fixture bytesはS08、Design外single ownerはS10のremaining obligation | evidence adopted; E00 complete and S01 unblocked |
| S01 docs | `doc-writer` | provider-neutralなOverview / R/D/P/Report / scope layeringとCurrent入口を実装し、旧skill-first矛盾を中立化 | provider / dogfoodのS01-owned 8 path | byte parity、relative link、mandatory endorsement scan、`git diff --check` | implementation correct; final gate pending | Current / Historical catalog全体はS06 | evidence adopted; testへhandoff |
| S01 tests | `dev-coder` | link、責務方向、scope別Plan / routing、navigation、parity、mandatory provider/modelのcontract testsを追加 | `tests/unit/infra/test_authoring_kit_assets.py` | 52 passed、ruff check / format pass、`git diff --check` pass | implementation correct; final code delta gate pending | inline Markdown link構文が対象 | evidence adopted; fresh delta reviewへhandoff |
| S02 docs | `doc-writer` | 三scopeのR/D/Pを最小frontmatter / heading / 一文prompt / scope別Guide linkへ置換 | provider / dogfoodの9 R/D/Pと`templates/README.md`（20 files） | 10 path byte parity、rendered link、forbidden scan、`git diff --check` pass | fresh code / spec review pass | material decisionなし | evidence adopted; S02 closed |
| S02 tests | `dev-coder` | S02 thin template matrix、snake_case禁止語彙、exact scope catalogの欠陥検出を66 testsで固定 | `tests/unit/infra/test_authoring_kit_assets.py` | 全118 passed、S02 66 passed / 52 deselected、ruff check / format、`git diff --check` pass | fresh code / spec review pass | Design §5.3またはscope catalog変更時はtemplate/test同期が必要 | evidence adopted; S02 closed |
| S03 docs | `doc-writer` | Base Guide、四Completion Guide、six example matrix、docs-only Level境界を実装し、critical N/Aをmigrationだけへ限定 | provider / dogfoodの`issue-plan.md`と`issue-plan-levels/*.md`（10 files） | 5 path byte parity、全relative link、forbidden path / term scan、`git diff --check` pass | fresh code / spec review pass | material decisionなし | evidence adopted; S03 closed |
| S03 tests | `dev-coder` | one-plan、Guide独立性、Level completion、example / wrong-signal / metadata境界、critical recovery省略禁止を22 testsで固定 | `tests/unit/infra/test_authoring_kit_assets.py` | 全140 passed、plan / level 43 passed / 97 deselected、ruff check / format、`git diff --check` pass | fresh code / spec review pass | 意味token変更時はtest同期が必要 | evidence adopted; S03 closed |
| S04 docs | `doc-writer` | 三scope Reportを最小frontmatter + exact result shapeへ置換し、Guideへempty-valid / non-gating境界を実装 | provider / dogfoodの3 Report templateとReport Guide（8 files） | 4 path parity、scope link、forbidden scan、nonempty、`git diff --check` pass | fresh code / spec review pass | 初回Guide更新のS01回帰をGuide側修復。prompt一般規則矛盾はcanonical RQ / Designで解消 | evidence adopted; S04 closed |
| S04 tests | `dev-coder` | Report exact shape、empty-valid、heavy / generic禁止語、neutral reviewer境界、non-gatingを47 testsで固定 | `tests/unit/infra/test_authoring_kit_assets.py` | 全187 passed、report 53 passed / 134 deselected、ruff check / format、`git diff --check` pass | fresh code / spec review pass | 構造 / 境界token中心で表現変更は許容 | evidence adopted; S04 closed |

### Implementation Delegation Gate

| step | decision | required reason | delegated role | delegated scope | source of truth | allowed changes | forbidden changes | required verification | stop conditions | output required | observed result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E00 | delegated | asset / link / preservation baselineの横断read-only分析が必要 | `repo-analyst` | Design §4.1 asset / hash / link inventory | approved `requirement.md` / `design.md` / amended `plan.md` | read-only repository inspectionとmainによるreport統合 | asset / source / tests / user content / metadata / deps / active / Git mutation | `tc-e00-001` inspect evidence | Design §4.1 action / 358 owner不明、baseline drift、Design §4外Delete分類 | manifest、hash、link evidence、risk、next action | delegation complete / E00 passed: S08 / S10 inputを明示しS01をunblock |
| S01 docs | delegated | shipped Authoring Guide本文とdogfood projectionの一貫編集 | `doc-writer` | S01-owned docs / navigation 8 path pair | active R/D/P、S01 contract | provider / dogfoodのS01 docsだけ | templates、Runtime、skill、installer、canonical issue docs | link / parity / mandatory scan | material path / responsibility変更 | changed docs、parity、risk | complete |
| S01 tests | delegated | S01 contractの欠陥検出を自動化 | `dev-coder` | `tests/unit/infra/test_authoring_kit_assets.py` | S01 docs、`tc-s01-001` | S01 test fileだけ | docs、templates、Runtime、他tests | focused pytest / ruff / diff check | contract外behavior変更 | changed test、Red / Green、risk | complete: 52 tests pass |
| S02 docs | delegated | shipped thin R/D/Pとdogfood projectionの一貫編集 | `doc-writer` | 9 R/D/Pとtemplates READMEの10 path pair | active R/D/P、S02 contract | S02 target templates / READMEだけ | Report / Artifact、Guide、Runtime、skill、installer、Existing nodes | catalog / link / parity / forbidden scan | Design §5外shapeまたは既存content migration | changed templates、manifest、risk | complete: 20 files、10 path parity pass |
| S02 tests | delegated | S02 contractの欠陥検出を自動化 | `dev-coder` | `tests/unit/infra/test_authoring_kit_assets.py` | S02 templates、`tc-s02-001` | S02 test fileだけ | docs、templates、Runtime、他tests | focused pytest / ruff / diff check | contract外behavior変更 | changed test、Red / Green、risk | complete: S02 66 tests、全118 pass |
| S03 docs | delegated | one-planと独立Completion Guideをprovider / dogfoodへ実装 | `doc-writer` | S03-owned Base / four Guides、必要時のみIssue Plan template | active R/D/P、S03 contract | S03 target docs / templateだけ | level別Plan、Runtime / metadata、Initiative / Epic Level、other Guide | link / parity / forbidden scan | Runtime fallback、cross-level inheritance、新classification | changed docs、example matrix、risk | complete: Base + four Guides、10 files parity pass |
| S03 tests | delegated | S03 contractの欠陥検出を自動化 | `dev-coder` | `tests/unit/infra/test_authoring_kit_assets.py` | S03 docs、`tc-s03-001/002` | S03 test fileだけ | docs、templates、Runtime、他tests | full / plan-level pytest、ruff、diff check | contract外behavior変更 | changed test、Red / Green、risk | complete: 22 tests追加、全140 pass |
| S04 docs | delegated | thin Report contractをprovider / dogfoodへ一貫実装 | `doc-writer` | three Report templates + Report Guideの4 path pair | active R/D/P、S04 contract | S04 target docs / templatesだけ | Runtime / CLI、357 files、Existing Report、other docs/templates | exact shape / link / parity / forbidden scan | Runtime変更、semantics変更、Existing migration | changed docs、shape evidence、risk | complete: 8 files、4 path parity pass |
| S04 tests | delegated | S04 contractの欠陥検出を自動化 | `dev-coder` | `tests/unit/infra/test_authoring_kit_assets.py` | S04 assets、`tc-s04-001` | S04 test fileだけ | docs、templates、Runtime、CLI / 357 tests | full / report pytest、ruff、diff check | contract外behavior変更 | changed test、Red / Green、risk | complete: 47 tests、全187 pass |

### Closure Coverage

| closure range | owner steps | planning evidence | implementation evidence | state |
|---|---|---|---|---|
| `CL-358-001`〜`CL-358-015` | E00、S01〜S10、S90、S99 | amended `plan.md`のClosure Indexとfresh Plan review pass | E00で`CL-358-010`をcloseし、`CL-358-011/013`をS08 / S10へhandoff。S01で`CL-358-003`、S02/S04で`CL-358-001/002/006`のtemplate部分、S03で`CL-358-004/014`をclose | in progress |

### Closure Delta

| change | closure ids | reason | plan amendment required | re-review required | current result |
|---|---|---|---|---|---|
| E00 plan contradiction | `CL-358-011/013` | E00はread-onlyでfull fixture hashとowner確定を要求していた | completed | completed | E00 candidate inventory、S08 fixture/hash、S10 final ownerへ分離。fresh review pass |
| S01 / S03 Plan Guide boundary | `CL-358-003/004` | S01がOverviewからPlan Guideへ到達させる一方、旧workflow依存の`issue-plan.md`をS03まで編集禁止としていた | completed | fresh spec / code delta review pass | S01でprovider-neutralなPlan基礎、Current入口、scope-aware Plan導線を実装し、S03はPlanning Level / Completion Guide詳細を所有する。52 tests pass |
| S04 Report prompt exception | `CL-358-001/006` | RQ-358-001 / Design §5.1の一般prompt規則とAC-358-006 / Design §5.4のempty-valid exact shapeが衝突した | completed | fresh spec rereview pass | 一行promptをR/D/Pへ限定し、Reportは三必須sectionを空本文で開始するspecific contractを維持 |

- `CL-358-010`のprovider / dogfood baseline manifestはread-only evidenceで充足した。
- `CL-358-011`はS08 ownerである。現HEADにないthin Report、candidate ADR、profile-derived node-local documentはS08でfixture / baseline hashをmaterializeする。
- generic importは既存tracked ZIPのSHA-256で補完したが、他の不足カテゴリは解消しない。
- `CL-358-013`に関係するDesign外surfaceは暗黙Deleteしない。Historical recognition、skill contract、distribution pruneが複数Issueに跨り、exact single-owner manifestはS10より前には確定していない。
- 再開条件は充足した。Plan amendmentとfresh spec review passによりS01へ進める。

### Issue Planning Recovery

- 2026-08-10、E00で検出したPlan gapを修正するため、repo-local `./spec-dock/scripts/spec-dock-chatgpt planning create`をexact GitHub-synced HEAD `ab1fc6d2b403c685bfb050d32479a59355e9b621`で実行した。
- external context manifestを付けた実行と外した実行はいずれも、ChatGPT送信前に`status=rejected`、`reason=planning_context_rejected`で停止した。重複submission、Candidate、Review、canonical adoptionは発生していない。
- runtimeの`parse_current_front_matter_baseline()`でexact canonical `requirement.md` / `design.md` / `plan.md`を検証した結果、`ValueError: front matter key set is invalid`を再現した。
- canonical三文書は`関連GitHub`と`承認`を持つが、Issue planning runtimeのstrict front matter schemaは両keyを受理しない。この非互換はcontext manifestやmanaged Chromeより前のhard preflight failureである。
- `関連GitHub` / `承認`を黙って削除する案は承認・traceability情報を変更し、runtime schemaを358で拡張する案はIssue scopeを越えるため採用しない。
- ChatGPT-first routeは現行canonical bytesでは継続不能。manual backupを使う場合は、hard failure evidence、recovery attempt、explicit human approval、implementation-planner evidence、fresh spec-reviewer gateを満たしてからPlanを採用する。
- 2026-08-10、Product Ownerはこれらを放棄予定の旧workflowとして使用しないことを明示し、main orchestrator自身の推論とcanonical実装計画に沿った直接修正・実装継続を指示した。以後ChatGPT-first / manual-backup planning workflowを本Issueの進行条件にしない。

### Docs Impact Resolution

| step | target | planned verification | current state |
|---|---|---|---|
| S90 | Design §4.1で358-ownedのREADME / Guide / authoring docs / templates | link / vocabulary / wording inspection、fresh spec review | not started |

### Milestone / Commit Candidate Gate

| milestone / step | reviewer verdict | commit candidate / scope | closure state | commit evidence | post-commit clean check |
|---|---|---|---|---|---|
| M0 / E00 | amended Plan fresh `spec-reviewer` pass。P0/P1なし、P2 report同期を反映 | `docs(iss-00358): E00契約をS08/S10分離へ反映` / Plan amendment + E00 report evidence | passed | `d4ca698f0257a36d81557233b9960fd2d9a95e7e` | commit後clean、GitHub upstream同一SHAを確認済み |
| M1 / S01〜S04 | fresh code / spec review pass。S03 critical P1、S04 prompt P1、禁止語P2を修正済み | `feat(authoring): thin document kitを導入` / Guide foundation + thin R/D/P/Report + Planning Levels + asset tests | ready to commit | not created | pre-commit verification pass、commit後check pending |
| M99 / S99 | not reached because S05〜S90 are unfinished | `docs(iss-00358): 最終実装証跡を確定` / final report ledger | planned | not created | not run |

## 残余リスクと停止条件

- Existing node-local content、`.assurance.json`、Profile由来文書、Historical evidenceをrewrite / rename / deleteしない。
- Planning LevelをRuntime state / metadataへ追加せず、level別canonical Planを作らない。
- Issue 357のRuntime / parser / scaffold mechanismを358から修正しない。IC-1 mismatchはcontentとmechanismへ一意にroutingする。
- Skill本文、installer inventory、obsolete assetの物理pruneは359 / 360へ渡し、本Issueで先行しない。
- PR、merge、Issue close、Epic完了は別workflowであり、本報告では許可・実行しない。

## 次のアクション

S01〜S04の実装、Green、fresh reviewを完了した。M1 commitとpost-commit checkを行い、S05のArtifact semanticsへ進む。
