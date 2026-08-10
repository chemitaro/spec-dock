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
- 承認済みPlanのE00を開始し、asset / link / preservation baselineをread-onlyで収集した。S01以降のasset / test変更、PR、merge、`issue finish`はまだ実行していない。
- E00 fresh `spec-reviewer`はfailした。read-only E00とS08で初めて作るpreservation fixtureのhash要求、S10より前のDesign外owner確定要求が両立しないため、S01へ進まずIssue planningへ戻す。
- materialな製品判断の追加はない。Profile / Assuranceを使わず、one Plan + docs-only Planning Level、thin Report、Current六種というProduct Owner承認をそのまま保持する。

## 承認済み正本

| 文書 | 状態 | 主な固定内容 |
|---|---|---|
| `requirement.md` | approved | thin R/D/P/Report、文書責務、scope layering、Planning Level、Artifact / authority、Current / Historical、preservation / handoff |
| `design.md` | approved | exact asset tree / Add-Modify contract、template / Guide link、Report exact shape、Level examples、IC-1、ownership / rollback |
| `plan.md` | approved | E00〜S99の縦スライス、`CL-358-001`〜`CL-358-015`、step-local delegation、docs-only alternative evidence、具体テストカード、review gate |

## Spec Interpretation / Decision Ledger

- `DEC-358-001`
  - Status: open
  - Type: plan contradiction / execution ordering gap
  - Trigger: E00 read-only baseline実行とfresh `spec-reviewer` review。
  - Observed facts: E00はExisting full fixtureの全preservation bytes/hashとDesign外ownerの確定を要求する。一方、full fixture/testのmaterializationはS08だけに許可され、Design外handoff manifestはS10で作る計画である。現HEADにはthin Report、candidate ADR、profile-derived node-local documentを含むfull fixtureがない。
  - Options Considered: preservation baselineをS08へ移す / E00前にfixture materialization stepを追加する / 現状のままsynthetic `ABSENT`をpass扱いする。
  - Proposed disposition: `promoted_to_plan`。E00はcandidate inventoryまで、fixture bytes/hashはS08へ移し、Design外ownerは`no-delete / owner pending S10`として扱う案をplanningでreviewする。synthetic `ABSENT`をbaseline passにはしない。
  - Evidence: E00 `repo-analyst` follow-up、fresh E00 `spec-reviewer` fail（P1 x2、P2、P3、confidence 0.99）。
  - Affected closure: `CL-358-011/013`、E00、S08、S10、M0。
  - Risk if wrong: Existing preservationを証明せずS01へ進む、またはE00で禁止されたfixture mutationを行う。
  - Needs orchestrator decision: yes。Issue planningでPlan amendmentとfresh reviewが必要。
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
| plan | 承認済みR/D、Strict Plan Guide、全RQ / EC / AC、Design file-change contract、Issue 357とのIC-1境界を照合した | none | adopted | pass | no | execute approved plan |

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
| plan | final plan phase gate | spec-reviewer | fresh | pass | no | execute approved plan | findingsなし、overall confidence 0.98、全closure / step contract / test card / ownershipを確認 |
| E00 | E00 docs/spec alignment gate | spec-reviewer | fresh | fail | no | E00を閉じずbounded follow-upへ戻す | P1: synthetic / ABSENT preservation bytesとNon-Delete owner未確定。P2: active symlink source。P3: Closure Delta状態。overall confidence 0.99 |

## Workflow-Scoped Authorization

| authorization source | repo / worktree | active scope | named roles | boundary | result |
|---|---|---|---|---|---|
| ユーザーによるSpecDock workflow利用依頼と2026-08-10の文書承認 | current `spec-dock` checkout | iss-00358 planning | system-architect、implementation-planner、spec-reviewer | current repo / scope / session内のread-only planning / review。実装、外部公開、PR、mergeは含まない | pass |
| ユーザーによる2026-08-10の`issue start`と実装開始依頼 | `/Volumes/990p2t/offloaded/home/iwasawayuuta/.codex/worktrees/4bc6/spec-dock` | active `iss-00358` execution | repo-analyst、doc-writer、dev-coder、spec-reviewer、code-reviewer、qa-reviewer | approved Planのstep-local scope内の実装・検証・review。scope拡張、外部公開、PR、merge、`issue finish`は含まない | pass |

## 実装開始契約

| 最初のstep | 担当 | 入力 | 完了条件 |
|---|---|---|---|
| E00 | `repo-analyst` | approved R/D/P、baseline SHA、Design §4.1 asset / link / preservation surface | 全rowにAction、owner、before hash、planned testがあり、暗黙Deleteがない |
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
| Add | `docs/authoring/report.md` | `ABSENT` | 358 S04 | report contract test |
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

暗黙Delete rowは0である。一方、thin Report、candidate ADR、profile-derived documentの実在baseline bytesと、Design §4外surfaceのsingle ownerは未確定であり、E00 stop conditionに該当する。実行したread-only commandは`git status --short`、`git branch --show-current`、`git rev-parse`、`git cat-file`、`git show`、`find`、`rg`、`sed`、`nl`、`shasum -a 256`。`No material implementation decisions beyond the approved plan.`

### Step Contract Closure

| step | closure ids | planned close condition | observed evidence | result | notes |
|---|---|---|---|---|---|
| E00 | `CL-358-010/011/013` | Design §4.1全rowにAction、owner、before hash、planned testがあり、暗黙Deleteがない | managed asset baselineは収集済み。preservationのsynthetic / ABSENT rowとNon-Delete ownerがfresh reviewで未確定と判定された | failed | bounded read-only follow-up中。解消不能ならplanningへ戻す |

### Test Contract Closure

| test id | step | evidence level | pre-implementation evidence | verification path | observed result |
|---|---|---|---|---|---|
| `tc-e00-001` | E00 | inspect-only | baseline `2c75e0c0`とcurrent `e16e9751`のasset / hash / link / copy-depthを比較 | Plan §9 E00のtree / link / hash / copy-depth inspection | fail: synthetic / ABSENT preservation bytesと未確定ownerが残り、full baselineを固定できていない |

### Delegated Worker Evidence

| step | delegated role | worker summary | changed files | tests or docs-only verification | reviewer verdict | unresolved risks | integration decision |
|---|---|---|---|---|---|---|---|
| E00 | `repo-analyst` | 35 managed/test row、21 preservation candidate row、copy-depth / link、Historical / obsolete ownershipをread-onlyで調査 | none | SHA-256 / parity / link / source-path inspectionを実施 | fail | full fixture bytesとDesign外single ownerが未確定 | evidence adopted; canonical Plan gapとしてIssue planningへ戻す |

### Implementation Delegation Gate

| step | decision | required reason | delegated role | delegated scope | source of truth | allowed changes | forbidden changes | required verification | stop conditions | output required | observed result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E00 | delegated | asset / link / preservation baselineの横断read-only分析が必要 | `repo-analyst` | Design §4.1 asset / hash / link inventory | approved `requirement.md` / `design.md` / `plan.md` | read-only repository inspectionとmainによるreport統合 | asset / source / tests / user content / metadata / deps / active / Git mutation | `tc-e00-001` inspect evidence | action / owner不明、Design外path、baseline drift | manifest、hash、link evidence、risk、next action | delegation complete / E00 failed: canonical Plan gapを検出しplanningへ戻す |

### Closure Coverage

| closure range | owner steps | planning evidence | implementation evidence | state |
|---|---|---|---|---|
| `CL-358-001`〜`CL-358-015` | E00、S01〜S10、S90、S99 | `plan.md`のClosure Indexと最終fresh Plan review pass | E00で`CL-358-010/011/013`のbaseline / pre-implementation evidenceを収集。各closureの最終closeはowner stepで行う | in progress |

### Closure Delta

| change | closure ids | reason | plan amendment required | re-review required | current result |
|---|---|---|---|---|---|
| E00 plan contradiction | `CL-358-011/013` | E00はread-onlyでfull fixture hashとowner確定を要求するが、fixture materializationはS08、handoff owner確定はS10に配置されている | yes | yes | fresh review fail。S01未着手、Issue planningへ戻す |

- `CL-358-010`のprovider / dogfood baseline manifestはread-only evidenceで充足した。
- `CL-358-011`のE00 baselineは未充足である。現HEADにthin Report、candidate ADR、profile-derived node-local documentを含むExisting full fixtureがなく、E00ではfixture / test作成が禁止されている。
- generic importは既存tracked ZIPのSHA-256で補完したが、他の不足カテゴリは解消しない。
- `CL-358-013`に関係するDesign外surfaceは暗黙Deleteしない。Historical recognition、skill contract、distribution pruneが複数Issueに跨り、exact single-owner manifestはS10より前には確定していない。
- 再開条件: canonical Planを改訂し、preservation fixture / hash baselineをS08へ移すか、E00前のfixture materialization stepを追加する。Design外inventoryのowner確定時点もS10または360 planningへ明示し、fresh spec reviewをpassする。

### Issue Planning Recovery

- 2026-08-10、E00で検出したPlan gapを修正するため、repo-local `./spec-dock/scripts/spec-dock-chatgpt planning create`をexact GitHub-synced HEAD `ab1fc6d2b403c685bfb050d32479a59355e9b621`で実行した。
- external context manifestを付けた実行と外した実行はいずれも、ChatGPT送信前に`status=rejected`、`reason=planning_context_rejected`で停止した。重複submission、Candidate、Review、canonical adoptionは発生していない。
- runtimeの`parse_current_front_matter_baseline()`でexact canonical `requirement.md` / `design.md` / `plan.md`を検証した結果、`ValueError: front matter key set is invalid`を再現した。
- canonical三文書は`関連GitHub`と`承認`を持つが、Issue planning runtimeのstrict front matter schemaは両keyを受理しない。この非互換はcontext manifestやmanaged Chromeより前のhard preflight failureである。
- `関連GitHub` / `承認`を黙って削除する案は承認・traceability情報を変更し、runtime schemaを358で拡張する案はIssue scopeを越えるため採用しない。
- ChatGPT-first routeは現行canonical bytesでは継続不能。manual backupを使う場合は、hard failure evidence、recovery attempt、explicit human approval、implementation-planner evidence、fresh spec-reviewer gateを満たしてからPlanを採用する。

### Docs Impact Resolution

| step | target | planned verification | current state |
|---|---|---|---|
| S90 | Design §4.1で358-ownedのREADME / Guide / authoring docs / templates | link / vocabulary / wording inspection、fresh spec review | not started |

### Milestone / Commit Candidate Gate

| milestone / step | reviewer verdict | commit candidate / scope | closure state | commit evidence | post-commit clean check |
|---|---|---|---|---|---|
| M0 / E00 | fresh `spec-reviewer` fail。P1/P2/P3 findings未解決 | `docs(iss-00358): Authoring asset baselineを記録` / E00 report evidence | failed | not created | not run |
| M99 / S99 | not reviewed because execution has not started | `docs(iss-00358): 最終実装証跡を確定` / final report ledger | planned | not created because execution has not started | not run |

## 残余リスクと停止条件

- Existing node-local content、`.assurance.json`、Profile由来文書、Historical evidenceをrewrite / rename / deleteしない。
- Planning LevelをRuntime state / metadataへ追加せず、level別canonical Planを作らない。
- Issue 357のRuntime / parser / scaffold mechanismを358から修正しない。IC-1 mismatchはcontentとmechanismへ一意にroutingする。
- Skill本文、installer inventory、obsolete assetの物理pruneは359 / 360へ渡し、本Issueで先行しない。
- PR、merge、Issue close、Epic完了は別workflowであり、本報告では許可・実行しない。

## 次のアクション

E00の禁止変更とpreservation fixture hash要求、Design外owner確定順序の矛盾をcanonical planning gapとしてIssue planningへ戻す。ChatGPT-first preflightはcanonical front matter非互換でhard failureとなったため、manual backupへの明示承認を得てPlan amendmentとfresh spec reviewを完了するまでM0 commitとS01へ進まない。
