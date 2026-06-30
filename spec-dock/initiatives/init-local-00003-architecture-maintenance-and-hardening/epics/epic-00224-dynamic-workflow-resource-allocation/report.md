---
種別: レポート（Epic）
ID: "epic-00224"
タイトル: "Dynamic Workflow Resource Allocation"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["init-local-00003"]
---

# epic-00224 Dynamic Workflow Resource Allocation — レポート（進捗 / 決定 / 結果）

> このテンプレートは observed evidence slot scaffold です。Epic の進捗、採用判断、reviewer state、blocking / next action、closure / follow-up を記録する starting shape を提供しますが、workflow / compliance authority ではありません。判断の詳細と lifecycle policy は skills / docs / accepted ADRs / reviewer gates を参照し、観測した証跡だけをこの report ledger に残します。

## 進捗サマリー (必須)
- 現在地（何が完了し、何が未完か）:
  - Epic discussion artifacts と deep-consultant analysis をもとに canonical `requirement.md` を初稿化した。
  - Fresh `spec-reviewer` が requirement を pass したため、requirement phase は design phase へ昇格可能。
  - Requirement pass 済み input、draft design、source-grounding、deep-consultant analysis をもとに canonical `design.md` を初稿化した。
  - Fresh `spec-reviewer` re-review が findings なしで design を pass したため、design phase は plan phase へ昇格可能。
  - 追加提供された Agent Context Routing 情報を canonical `requirement.md` / `design.md` と draft Issue / plan seed へ反映し、fresh `spec-reviewer` が pass した。
  - Requirement / design pass 済み input と更新済み draft plan / issue slice seed をもとに canonical `plan.md` を初稿化した。
  - Fresh plan re-review が `review_status: pass` を返し、残った P2 は E-RQ-012 の formal owner を I07 に一本化する修正として反映済み。
  - T0 + I01〜I07 の Issue 実体を作成し、依存関係を登録した。
  - その後、`iss-00226 / #226` は decision-only Issue として誤った routing だったため close し、当初 5 件の Epic-scope accepted ADR へ authority を移した。後続 dogfooding corrective work で explicit review completion ADR を追加した。
  - `iss-00227 -> iss-00226` dependency を削除し、実装対象 Issue を `iss-00227`〜`iss-00233` に再整理した。
  - 各 implementation Issue の draft requirement / draft design discussion と統合レビュー用 discussion を、IC0 Epic Decision Baseline 前提へ更新した。
  - Corrective Issues `iss-00237` / `iss-00238` / `iss-00239` / `iss-00241` を Epic close-readiness ledger に取り込んだ。その後、`iss-00244` で current operational contract を `guidance <target>` stdout authority / projection human-debug-only / script-local review instruction / explicit review completion artifact model へ変更した。
  - `iss-00247 / #247` 後の manual test / follow-up analysis により、Issue `draft-design` / `draft-plan` が profile template source に route されていない gap だけでなく、artifact readiness preflight、grade-aware Issue authoring guidance、delegated specialist routing、fresh review / report evidence gate、grade-aware smoke tests まで Epic #224 の追加修正として扱う必要があると確認した。
  - `I08` 単独案は狭すぎるため superseded とし、正式な追加 corrective tranche を `R0 + G1〜G4` として Epic requirement / design / plan へ反映した。`iss-00250` は一時検討置き場として扱い、正式な Issue slice では採用しない。
  - 正式な追加 corrective Issue として `iss-00251 / #251`〜`iss-00255 / #255` を SpecDock の `new issue` で作成し、`iss-00247 -> iss-00251 -> iss-00252`、`iss-00252 -> iss-00253`、`iss-00251 / iss-00252 -> iss-00254`、`iss-00251〜iss-00254 -> iss-00255` の依存を登録した。
  - 追加 Issue ごとに draft `requirement.md` / `design.md` / `plan.md` を作成し、R0〜G4 の責務境界、親 Epic trace、依存、非対象を統合的に整えた。
  - Fresh integrated `spec-reviewer` が、Epic plan / design / report、`iss-00251`〜`iss-00255` の draft requirement / design / plan、各 `.meta.json` dependencies をレビューし、findings なし / `review_status: pass` / confidence 0.88 を返した。
- 次のマイルストーン:
  - `iss-00251` から dependency order に沿って個別 Issue 実装へ進む。
- ブロッカー:
  - 現時点でユーザー確認が必要な blocking question はなし。

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact やEpic判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | `adopted` | discussion / draft package | `requirement.md` | User-provided draft requirement の WHAT / WHY / scope / AC を canonical Epic requirement 初稿へ採用した。 | `discussions/20260623t010733z-draft-requirement-adaptive-assurance-draft-requirement.md` | fresh `spec-reviewer` |
| EAL-002 | `adopted` | discussion / decision | `requirement.md` | 新規 Epic + 複数 Issue、前提 Epic `epic-00158`、Strict / Deep の判断を requirement の前提・scope・依存へ採用した。 | `discussions/20260623t010748z-disc-epic-issue-selection-decision.md` | fresh `spec-reviewer` |
| EAL-003 | `adopted` | deep-consultant | `requirement.md` | Lite rollout は Option C 強化版を採用し、initial automatic Lite default は対象外、candidate / authorized separation と auto-lite-readiness を requirement へ反映した。 | `discussions/20260623t012043z-research-deep-consultant-lite-rollout-report.md` | fresh `spec-reviewer` |
| EAL-004 | `adopted` | discussion / draft package | `design.md` | User-provided draft design の adaptive assurance / compiled runbook / PR review policy / metrics / rollout structure を Epic-level shared design として再構成して採用した。 | `discussions/20260623t010737z-draft-design-adaptive-assurance-draft-design.md` | fresh `spec-reviewer` |
| EAL-005 | `adopted` | discussion / synthesis | `design.md` | 提供 draft 群の読み取り結果から、canonical / generated / ignored の配置、Issue slice へ渡す shared vocabulary、provider / dogfooding mirror 境界を design へ反映した。 | `discussions/20260623t010846z-disc-provided-draft-package-synthesis.md` | fresh `spec-reviewer` |
| EAL-006 | `adopted` | deep-consultant | `design.md` | Lite は `lite_candidate` と `lite_authorized` を分離し、initial automatic Lite default を Stage 3 でも有効化せず future experimental 扱いにする設計判断として採用した。 | `discussions/20260623t012043z-research-deep-consultant-lite-rollout-report.md` | fresh `spec-reviewer` |
| EAL-007 | `adopted` | spec-reviewer finding | `design.md`, `report.md` | 長期 architecture decision を候補のまま残さず、当初 4 件、Agent Context Routing 追加後は 5 件の ADR を implementation 前の required ADR として扱い、plan で実装 Issue より前に配置する設計判断へ修正した。 | design review 1 finding: ADR必須判断を候補のまま残さない; context routing update added fifth ADR | fresh re-review |
| EAL-008 | `adopted` | user-provided supplemental draft | `requirement.md`, `design.md`, draft plan / issue slice discussions | Agent Context Routing を Assurance Profile / reasoning effort とは独立した tracked policy として扱い、execution context affinity、reviewer / consultant clean-room、context minimization、freshness、observability を requirement / design / I04 seed へ反映した。 | `discussions/20260623t024533z-research-agent-context-routing-supplemental-draft.md` | fresh requirement / design re-review |
| EAL-009 | `adopted` | spec-reviewer findings | `design.md`, draft plan / issue slice discussions, `report.md` | Context returned evidence refs の観測契約、draft plan の Auto-Lite trace、pending gate の扱いを P2 指摘として受け、design / draft seed / report を補正した。 | requirement/design update review: 3 P2 findings, `review_status: pass` | no further review required before plan authoring |
| EAL-010 | `adopted` | discussion / draft plan | `plan.md` | Updated draft plan の I01〜I07 slice、dependency order、checkpoint、quality gate、rollout、final exit contract を canonical Epic plan 初稿へ採用した。Issue 実体作成と dependency mutation はまだ行っていない。 | `discussions/20260623t010749z-draft-plan-adaptive-assurance-draft-plan.md` | fresh `spec-reviewer` |
| EAL-011 | `adopted` | spec-reviewer findings | `plan.md`, `report.md` | Plan review の P1/P2 指摘を受け、E-AC-008 を stale source binding owner の I03 へ移し、PR review 系は E-AC-009〜010、PR blocker 系は E-AC-011〜013、rollout 系は E-AC-014〜016 に再整列した。Required ADR 記録も 5 件へ揃えた。 | plan review 1 findings: E-AC-008 trace mismatch, required ADR count mismatch | fresh plan re-review |
| EAL-012 | `adopted` | spec-reviewer finding | `plan.md` | Plan re-review の P1 指摘を受け、E-AC-005 を fixed Skill / clean Git owner の I02、E-AC-006 を profile-specific planning owner の I03、E-AC-007 を step routing owner の I04 へ再整列した。 | plan re-review finding: E-AC-005〜007 slice ownership mismatch | fresh plan re-review |
| EAL-013 | `adopted` | spec-reviewer finding | `plan.md`, `report.md` | Fresh plan re-review は `review_status: pass`。残った P2 を受け、E-RQ-012 の formal close を I07 に一本化し、I01 は strict-legacy detection prerequisite としてだけ記録した。 | plan re-review pass with P2: E-RQ-012 owner clarification | no further review required before Issue creation |
| EAL-014 | `partially_adopted` | spec-dock commands | `plan.md`, `design.md`, issue discussions | T0 + I01〜I07 の Issue 実体と GitHub issue #226〜#233 を作成したが、T0 / `iss-00226` は decision-only Issue routing として後続で superseded。I01〜I07 の implementation Issue 作成と dependency edge は採用する。 | `spec-dock new issue`, `spec-dock deps add`, `deps check iss-00233` | superseded T0 correction recorded in EAL-018〜020 |
| EAL-015 | `partially_adopted` | issue draft discussions | issue-local `discussions/` | 各 Issue に draft requirement / draft design を作成した。`iss-00226` drafts は historical / superseded evidence とし、implementation handoff は `iss-00227`〜`iss-00233` に限定する。 | `issues/iss-00226...iss-00233/discussions/*draft-*` | fresh decomposition re-review |
| EAL-016 | `adopted` | discussion synthesis | `design.md`, `plan.md`, issue draft review | Issue draft integration review に ownership / gap / dependency check をまとめ、後続 correction で T0 owner を Epic-scope accepted ADR へ置換した。 | `discussions/20260623t034212z-disc-issue-draft-integration-review.md` | fresh decomposition re-review |
| EAL-017 | `superseded` | spec-reviewer | issue decomposition handoff | 旧 decomposition review は T0 / `iss-00226` prerequisite を含む handoff package に対する pass だったため、ユーザー指摘と ADR authority correction により superseded。 | spec-reviewer review result 2026-06-23, confidence 0.90 | fresh decomposition re-review required |
| EAL-018 | `adopted` | user clarification + deep-consultants | `design.md`, `plan.md`, `report.md`, accepted ADRs | `iss-00226` で ADR を後続処理するのではなく、Epic planning/design 現段階で ADR-level decisions を固定する判断を採用した。3 本の deep-consultant は blocking human question なし、fail-closed/default-safe で進行可能と判定した。 | `discussions/20260623t074452z-disc-adr-decision-synthesis-after-issue-226-closure.md` | fresh decomposition re-review |
| EAL-019 | `adopted` | accepted ADR artifacts | `design.md`, `plan.md`, issue draft review | Fixed Skill Kernel、Adaptive Assurance / Lite Authorization、Step Assurance / Context Routing、Trusted Base-SHA Review、Blocker-Centric PR Closure の当初 5 件を Epic-scope accepted ADR として固定した。Trusted Base-SHA Review は後続 EAL-029 で script-local instruction source へ変更済み。 | `discussions/20260623t074441z-adr-*`, `20260623t074442z-adr-*`, `20260623t074443z-adr-*`, `20260623t074444z-adr-*`, `20260623t074447z-adr-*` | amended by EAL-029 |
| EAL-020 | `adopted` | spec-dock commands | dependency metadata, GitHub issue #226 | `iss-00226 / #226` を closed / superseded historical evidence とし、`iss-00227 -> iss-00226` dependency を command-first で削除した。 | `spec-dock close iss-00226`, `spec-dock deps remove --from iss-00227 --to iss-00226` | validate / sync / deps check |
| EAL-021 | `adopted` | spec-reviewer findings | `requirement.md`, draft plan discussion | ADR authority correction review の P1/P2 指摘を受け、Auto-Lite adoption surface を別 accepted ADR + policy version bump + rollout Issue + telemetry gate の 4 点必須に固定し、旧 draft plan の T0 tranche を superseded と明記した。 | spec-reviewer review result 2026-06-23: P1 Auto-Lite stale choice, P2 old T0 draft tranche; iss-00233 spec review P1 telemetry gate unification | fresh re-review |
| EAL-022 | `adopted` | spec-reviewer | ADR authority correction handoff | Fresh re-review は findings なしで `review_status: pass`。Auto-Lite adoption surface、T0 supersession、ADR authority correction、dependency graph、implementation handoff readiness が妥当と判定された。 | spec-reviewer re-review result 2026-06-23, confidence 0.91 | downstream Issue planning may proceed from `iss-00227` |
| EAL-023 | `superseded` | iss-00231 spec-reviewer finding | `plan.md`, `report.md`, `issues/iss-00231-*/{design.md,plan.md,report.md}` | Historical: I05 の `Policy schema / validator / max size` は Markdown policy の fixed path + base SHA + UTF-8 + 32 KiB runtime validation として一度回収していた。この base-SHA policy 方針は `20260623t074444z-adr` / `iss-00244` により script-local review instruction source へ変更済み。 | iss-00231 spec review P1: parent I05 scope contract contradicted Issue closure contract | superseded by EAL-029 |
| EAL-024 | `adopted` | iss-00232 implementation + spec-reviewer finding | `plan.md`, `report.md`, `issues/iss-00232-*/{design.md,plan.md,report.md}` | I06 の blocker-centric repair は priority disposition / promoted P2 / blocker fingerprint evidence をこの Issue で閉じ、E-AC-013 と dedicated automation-stalled operator surfacing は I07 rollout / telemetry へ defer する。 | iss-00232 blocker policy payload and focused tests; spec review P1: E-AC-013 closure contradicted I07 defer | fresh iss-00232 spec re-review |
| EAL-025 | `adopted` | iss-00233 implementation | `requirement.md`, `design.md`, `plan.md`, `issues/iss-00233-*/{requirement.md,design.md,plan.md,report.md}` | I07 は automatic Lite default を有効化せず、auto-lite readiness、strict-legacy workflow compatibility、automation-stalled operator surface、required metrics / missing metrics summary、efficiency baseline を rollout evidence として閉じる。 | iss-00233 focused tests、automation-stalled behavior test、workflow strict-legacy tests、provider/mirror parity | fresh iss-00233 reviews |
| EAL-026 | `adopted` | iss-00238 / iss-00241 S90 reconciliation | `requirement.md`, `design.md`, `plan.md`, `report.md` | Current operational handoff は `./spec-dock/scripts/spec-dock guidance <target>` stdout authority であり、`workflow next` / generated Runbook authority wording は historical/superseded として扱う。Projection files are human/debug-only non-canonical output. | `issues/iss-00238-*/report.md`, `issues/iss-00241-*/report.md`, S90 docs inspection | final spec-reviewer pass |
| EAL-027 | `superseded` | iss-00241 S01/S02 evidence | `requirement.md`, `design.md`, `plan.md`, `report.md` | 旧 Trusted base policy valid path は deterministic multiline `@codex review`; missing / invalid / oversized / unreadable / base_sha_missing は no PR comment, human gate / fail-closed, no head fallback, no bare trigger fallback として反映していた。この decision は `20260623t074444z-adr` / `iss-00244` により script-local review instruction source へ変更済み。 | `issues/iss-00241-*/report.md` S01/S02 closure evidence; `discussions/20260623t074444z-adr-trusted-base-sha-github-review-policy.md` | superseded by EAL-029 |
| EAL-028 | `adopted` | iss-00237 / iss-00238 / iss-00239 / iss-00241 corrective reports | `report.md` | Epic final close-readiness は initial implementation Issues だけでなく corrective Issues も含む必要があるため、formal supersede / pass / final reviewer pass を一つの inclusion ledger に記録する。 | corrective issue reports and S90/S99 reconciliation | final spec-reviewer pass |
| EAL-029 | `adopted` | iss-00244 dogfooding repair + ADR | `requirement.md`, `design.md`, `plan.md`, `report.md` | PR #245 dogfooding で trusted base-SHA policy と `review_completion_unknown` terminal wait の問題が露出したため、review trigger instruction source は script-local asset、review completion は explicit Codex artifact model へ変更した。旧 base-SHA policy / active `review_completion_unknown` は historical/superseded decision として扱う。 | `discussions/20260623t074444z-adr-trusted-base-sha-github-review-policy.md`; `discussions/20260628t154553z-adr-pr-observation-explicit-review-completion.md`; `issues/iss-00244-*/report.md` | implementation in iss-00244 S300-S399 |
| EAL-030 | `adopted` | manual test / focused root cause analysis | `requirement.md`, `design.md`, `plan.md` | Manual test の F-001〜F-004 は template pack 本体ではなく artifact readiness classifier の drift と判断し、E-RQ-006 / E-AC-006 を fail-closed readiness contract へ拡張した。 | `discussions/20260630t080402z-disc-manual-test-readiness-failure-root-cause-analysis.md`; `discussions/20260630t055323z-disc-issue-247-manual-test-followup-analysis.md` | formal corrective Issue `iss-00251` created; proceed through issue-level implementation |
| EAL-031 | `adopted` | ADR / grade-aware rules definition | `requirement.md`, `design.md`, `plan.md` | Grade-aware authoring rules は follow-up Issue で再設計せず、Epic-level authority として固定する判断を採用した。`W1` Issue 案は不採用とし、R0 + G1〜G4 の実装 tranche へ展開した。 | `discussions/20260630t111316z-adr-grade-aware-issue-authoring-rules.md`; `discussions/20260630t084325z-disc-grade-aware-authoring-rules-definition.md` | formal corrective Issues `iss-00252`〜`iss-00255` created; proceed through issue-level implementation |
| EAL-032 | `adopted` | draft routing research | `requirement.md`, `design.md`, `plan.md` | Issue `draft-design` / `draft-plan` が旧 Issue template を source とする gap は、G2 の delegated specialist / draft artifact routing scope として採用した。 | `discussions/20260630t112403z-research-issue-draft-artifact-profile-template-routing-analysis.md` | formal corrective Issue `iss-00253` created; proceed through issue-level implementation |
| EAL-033 | `partially_adopted` | temporary issue artifacts | `requirement.md`, `design.md`, `plan.md` | `iss-00250` の requirement / design / plan は draft routing subcase の材料として採用するが、正式な implementation Issue ID としては採用しない。`iss-00251`〜`iss-00255` の正式 Issue 証跡へ置換されるまで temporary / superseded evidence として保持し、破棄する場合はこの ledger の参照先を先に置換する。 | `issues/iss-00250-route-issue-draft-design-and-plan-through-profile-templates/{requirement.md,design.md,plan.md,report.md}` | replace temporary reference with formal Issue evidence before deletion |
| EAL-034 | `adopted` | spec-dock commands + orchestrator-integrated drafts | `plan.md`, `design.md`, `report.md`, `issues/iss-00251...iss-00255/{requirement.md,design.md,plan.md}` | R0 + G1〜G4 を正式 Issue 化し、Epic plan / design / report と個別 draft requirement / design / plan に統合した。`iss-00250` は一時置き場のままとし、正式 implementation handoff には含めない。 | `spec-dock new issue`, `spec-dock deps add`, `issues/iss-00251...iss-00255/{requirement.md,design.md,plan.md}` | passed integrated `spec-reviewer`; proceed through issue-level implementation |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | 軽量タスクにも重い gate がかかる token / wall-clock waste を、runtime compiled Runbook と Assurance Profile で減らす。 | Review safety、legacy compatibility、script-local review instruction、explicit review completion artifact model、observability。 | low: automatic Lite default を初期 scope から外し、Standard default と candidate / authorized separation を採用した。 | pass: requirement review found no blocking gap. |
| OAL-002 | Static Skill kernel + dynamic runtime Runbook により、軽量 / 重量 Issue の workflow cost を Issue facts に合わせて配分する。 | Canonical contract、source hash binding、monotonic escalation、script-local review instruction、strict-legacy fallback。 | low: `authorized_profile` だけを実行 authority とし、`lite_candidate` は telemetry に限定した。 | pass: design re-review found no findings and confirmed ADR routing fix. |
| OAL-003 | Agent Context Routing により、実行系 agent は必要な context を継承し、評価系 agent は clean-room independence を保つ。 | Tracked policy、source binding、bounded return contract、returned evidence refs observability。 | low: context mode は Runbook / policy authority とし、agent の都度判断で弱めない。 | pass: requirement/design update review returned `review_status: pass`; P2 fixes applied. |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | `workflow_epic.md`, `workflow_spec_authoring.md`, `phase_requirement.md`, `epic-00158` docs, active Epic scaffold, draft package discussions, source search, deep-consultant Lite rollout report | blocking question なし。Lite rollout は UX preference ではなく system-design best practice として deep-consultant に reroute 済み。 | draft requirement / decision / synthesis / deep-consultant report を canonical `requirement.md` へ採用。 | passed: fresh `spec-reviewer` returned no findings and `review_status: pass` with confidence 0.88. | no | promote to design phase. |
| design | reviewer-pass 済み `requirement.md`, `workflow_epic.md`, `workflow_spec_authoring.md`, `phase_design.md`, draft design, draft package synthesis, issue slice draft, deep-consultant Lite rollout report, provider / dogfooding runtime layout | blocking design question なし。Implementation parameter（review policy size, metrics retention, repo-specific hard trigger extension, future Auto-Lite adoption surface）は plan / later Issue で扱う non-blocking item とした。初回 design review で ADR 必須判断の曖昧さが P1 指摘となったため、当初 4 件、Agent Context Routing 追加後は 5 件の ADR を implementation 前 required として設計に明記した。後続 corrective work で script-local review instruction と explicit review completion ADR を追加した。 | adaptive assurance contract、compiled Runbook、candidate / authorized separation、script-local review instruction、explicit review completion、blocker-centric PR closure、tracked canonical vs ignored projection、migration / rollback / observability、required ADR before implementation を canonical `design.md` へ採用。 | passed: fresh re-review returned no findings and `review_status: pass` with confidence 0.91. | no | promote to plan phase. |
| requirement/design update | supplemental Agent Context Routing draft, existing passed requirement/design, draft issue slice I04, draft plan I04 | blocking question なし。既存 E-RQ-008 の短い context policy 要件だけでは tracked policy / packet / reviewer independence / return boundary / observability が不足していた。Fresh review の P2 指摘により returned evidence refs observability、Auto-Lite trace、pending gate 記録を補正した。 | E-RQ-015〜021、E-AC-017〜021、Agent Context Routing Architecture、Context Policy Resolver / Packet Compiler、I04 seed update、required ADR update、Auto-Lite trace update を採用。 | passed: fresh `spec-reviewer` returned `review_status: pass` with confidence 0.88; 3 P2 findings fixed. | no | promote updated requirement/design inputs to plan authoring. |
| plan | reviewer-pass 済み `requirement.md`, reviewer-pass 済み `design.md`, `workflow_epic.md`, `workflow_spec_authoring.md`, `phase_plan.md`, `phase_plan_epic.md`, updated draft plan, updated issue slice seed | blocking question なし。ユーザー指示により Issue 実体作成 / dependency mutation はこの phase では行わない。初回 plan review で E-AC-008 trace mismatch が P1、ADR 件数の古い記録が P2 として指摘され、修正済み。再レビューで E-AC-005〜007 owner mismatch が P1 として指摘され、修正済み。Fresh re-review pass 後の P2 として E-RQ-012 owner clarification があり、formal close を I07 に一本化した。その後、T0 ADR prerequisite Issue は routing correction により superseded となり、IC0 Epic Decision Baseline へ置換済み。 | IC0 Epic Decision Baseline、I01〜I07 implementation slices、E-RQ / E-AC closure matrix、dependency order、integration checkpoints、quality gates、rollout/docs impact、Issue readiness criteria、final exit contract を canonical `plan.md` へ採用。 | passed: fresh plan re-review returned `review_status: pass` with confidence 0.86; remaining P2 fixed. ADR authority correction 後の handoff は fresh re-review 待ち。 | no | promote to Issue decomposition / creation in a later turn; no Issue creation performed in this turn. |
| issue decomposition | reviewer-pass 済み Epic requirement/design/plan, created Issues `iss-00226`〜`iss-00233`, dependency metadata, issue-local draft requirement/design, integration review discussion | blocking question なし。ユーザー補足として、別 worktree の MyPy / Ruff 適用計画を implementation baseline への外部前提として扱い、draft に静的解析前提を反映した。初回 decomposition review は pass したが、ユーザー指摘により `iss-00226` decision-only Issue routing を訂正した。 | `iss-00226 / #226` を closed / superseded とし、当初 5 件の Epic-scope accepted ADR、IC0 Epic Decision Baseline、`iss-00227`〜`iss-00233` implementation handoff へ更新した。後続 corrective work で review instruction / completion ADR を更新・追加した。 | passed: fresh re-review returned no findings and `review_status: pass` with confidence 0.91. | no | Issue decomposition / ADR authority correction handoff complete; downstream Issue planning can proceed from `iss-00227`. |
| requirement/design/plan amendment | `workflow_epic.md`, `workflow_spec_authoring.md`, `phase_requirement.md`, `phase_design.md`, `phase_plan.md`, `phase_plan_epic.md`, decision routing guide, issue #247 manual test/follow-up analysis, root-cause analysis, grade-aware ADR, draft routing research, temporary `iss-00250` artifacts | blocking question なし。Issue `draft-design` / `draft-plan` source authority だけでなく、readiness preflight、grade-aware authoring rules、delegated specialist routing、fresh review / report evidence gate、smoke tests は複数 Issue の authoring backbone に関わるため、`iss-00250` ではなく Epic amendment として扱う。 | `E-RQ-006` / `E-AC-006` / `E-RQ-022` / `E-AC-022` / design components / R0 + G1〜G4 planned corrective tranche を canonical Epic artifacts へ採用。 | passed: fresh `spec-reviewer` returned `review_status: pass` with confidence 0.90; non-blocking P2 stale checkpoint wording was fixed. | no | formal corrective Issue creation completed as `iss-00251`〜`iss-00255`. |
| formal corrective issue handoff | `spec-dock new issue`, `spec-dock deps add`, Epic plan / design / report, `iss-00251`〜`iss-00255` draft requirement / design / plan | blocking question なし。個別 Issue 実装前に Epic 設計段階で draft requirement / design / plan を統合的に作成し、R0〜G4 の責務境界と依存を確認する。 | `iss-00251`〜`iss-00255` を正式 Issue として作成し、dependency registration と各 draft artifact を canonical Issue docs へ反映した。 | passed: fresh integrated `spec-reviewer` returned findings none / `review_status: pass` / confidence 0.88. | no | proceed to individual Issue implementation in dependency order. |

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）
- 委任 authoring の使用:
  - used / not used
- 未使用の場合:
  - manual authoring path / 委任ドラフトを昇格証跡として使っていない理由。
  - この design phase では system-architect による discussion direct-write draft は使っていない。理由は、user-provided draft design / draft package synthesis / deep-consultant report が設計証跡として十分であり、追加の delegated draft cycle は同じ論点を重複させるだけだったため。Canonical `design.md` は main orchestrator が統合し、fresh `spec-reviewer` gate は省略しない。
- lifecycle state（契約値）:
  - `requested`, `produced`, `integrated`, `partially_integrated`, `rejected`, `superseded`, `blocked`, `stale`
- 昇格不可 state:
  - `stale`, `rejected`, `superseded`, `blocked`
- 標準出力先:
  - 対象 scope の `discussions/` direct child にある flat Markdown
  - filename: `<ts>-<kind>-<slug>.md` または same-second collision 用 `<ts>-<nn>-<kind>-<slug>.md`
- 軽量 provenance:
  - `created_by_role`, `scope_id`, `source_paths`, `intended_targets`, `adoption_status: unreviewed`, `reflected_to: []`, `diff_guard_result`, fallback decision, report evidence destination, adoption ledger note
  - 互換 label: source artifacts, draft artifact path, status, integration result, rejected portions, blockers, reviewer result, promotion decision
- 禁止 self-claim:
  - `authority: accepted`, `adoption_status: adopted`, non-empty `reflected_to`, reviewer pass, phase completion, implementation readiness
- 禁止 wildcard token:
  - `*`, `grants.*`, `all`
- 標準必須にしない field:
  - task manifest hash, Permission Profile hash, session invocation hash, probe run id, session hash
- historical note:
  - 既存 `iss-00126` などの manifest/Profile/probe/session artifacts は grandfathered evidence として残し、削除・rename・validation failure 化しない。

| ロール（created_by_role） | 範囲（scope_id） | ドラフトパス（discussion draft path） | 参照元（source_paths） | 予定反映先（intended_targets） | 採用状態（adoption_status） | 反映先（reflected_to） | 差分ガード結果（diff_guard_result） | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果（reviewer result） | 昇格判断（promotion decision） |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | 未使用（not used） | なし（[]） | 未実行（not_run） | 手動 authoring | 該当なし | なし（none） | 該当なし | 委任ドラフト昇格なし |

### 委任ドラフトの失敗モード（Delegated Draft Failure Modes）
| 失敗モード | 期待される判定 | 許可される次アクション | レポート証跡の記録先（report evidence destination） | 昇格可否 |
|---|---|---|---|---|
| 同意なし（missing consent） | blocked / incomplete | 範囲付き同意を取得する、または手動 authoring に戻す | この section | ineligible |
| 前段 reviewer pass 不足 / stale（missing/stale previous reviewer pass） | blocked / incomplete | レビューゲートを再実行する（rerun reviewer gate） | Spec Authoring Gate / reviewer evidence | ineligible |
| 設計中の要件 gap（requirement gap during design） | blocked / incomplete | requirement phase へ戻す | 判断台帳 / ゲート証跡（decision ledger / gate evidence） | ineligible |
| 計画中の設計 gap（design gap during plan） | blocked / incomplete | design phase へ戻す | 判断台帳 / ゲート証跡（decision ledger / gate evidence） | ineligible |
| ロール利用不可（role unavailable） | blocked / manual path | 利用不可を記録し、妥当なら手動で続行する | この section | ineligible |
| 禁止行為の試行（forbidden action attempt） | rejected | ドラフトを破棄し incident を記録する | この section / decision ledger | ineligible |
| 古いドラフト（stale draft） | stale | 再生成または差分調整する | この section | ineligible |
| 置換済みドラフト（superseded draft） | superseded | 置換先ドラフトを参照する | この section | ineligible |
| 委任使用主張に対する証跡不足（missing draft evidence when delegated use is claimed） | incomplete | 証跡を追加する、または委任使用 claim を外す | この section | ineligible |
| reviewer 利用不可 / 拒否 / waiver / provisional（reviewer unavailable/denied/waived/provisional） | blocked / incomplete | fresh な passed reviewer を取得する、または昇格なしの risk acceptance を記録する | レビューゲート証跡（reviewer gate evidence） | ineligible |

## 決定事項（ADRリンク） (必須)
- Accepted before implementation:
  - `discussions/20260623t074441z-adr-fixed-skill-kernel-compiled-runbook-authority.md`
  - `discussions/20260623t074443z-adr-adaptive-assurance-lite-authorization-monotonic-escalation.md`
  - `discussions/20260623t074442z-adr-step-assurance-resource-allocation-agent-context-routing.md`
  - `discussions/20260623t074444z-adr-trusted-base-sha-github-review-policy.md`
  - `discussions/20260623t074447z-adr-blocker-centric-pr-risk-closure-rereview.md`
- Added by corrective dogfooding work:
  - `discussions/20260628t154553z-adr-pr-observation-explicit-review-completion.md`
  - `discussions/20260630t111316z-adr-grade-aware-issue-authoring-rules.md`
- Superseded routing:
  - `iss-00226 / #226` は decision-only Issue として作成されたが closed / superseded。ADR authority は Epic-scope accepted ADR へ移動済み。

## 完了した Issue / PR / Release (必須)
- Initial implementation Issues `iss-00227`〜`iss-00233` は各 issue report の implementation / reviewer / commit evidence に基づき完了済み。
- Corrective Issues:
  - `iss-00237` / `#237`: pass
  - `iss-00238` / `#238`: pass
  - `iss-00239` / `#239`: formal supersede by `iss-00241`
  - `iss-00241` / `#241`: pass after S99 focused suite, sync/validate, manual flow, and qa/code/spec reviewer gates
- PR / Release:
  - pending: `iss-00251`〜`iss-00255` を branch baton で累積実装し、G4 後の Epic 最終品質ゲートを通過してから Epic #224 corrective tranche として単一 PR を作成する。

## 作成済み Issue / Draft Handoff
- superseded historical evidence:
  - iss-00226 / #226: Record Adaptive Workflow Authority ADRs（closed; not an implementation readiness dependency）
- implementation handoff:
- iss-00227 / #227: Introduce Assurance Contract And Classification Runtime
- iss-00228 / #228: Compile State Aware Workflow Runbooks And Fixed Skill Kernels
- iss-00229 / #229: Compose Profile Aware Planning Artifacts
- iss-00230 / #230: Compile Step Assurance Agent Routing And Context Policy
- iss-00231 / #231: Inject Trusted Base Branch Codex Review Policy
- iss-00232 / #232: Enforce Blocker Centric PR Repair And Rereview
- iss-00233 / #233: Roll Out Adaptive Workflow With Legacy Compatibility And Telemetry
- planned corrective handoff:
  - `iss-00251 / #251`: R0 Enforce Fail-Closed Issue Artifact Readiness Preflight
  - `iss-00252 / #252`: G1 Compile Grade-Aware Issue Planning Guidance
  - `iss-00253 / #253`: G2 Connect Delegated Specialist Role Routing And Draft Artifact Sources
  - `iss-00254 / #254`: G3 Add Grade-Aware Spec Review And Evidence Gates
  - `iss-00255 / #255`: G4 Add Grade-Aware Issue Authoring Smoke Tests

## 受け入れ条件（E-AC）の達成状況 (必須)
- E-AC-001〜004: pass（証拠: iss-00227 report; assurance classification / schema / Lite safety targeted tests）
- E-AC-005: pass（証拠: iss-00228 report; workflow runbook / fixed Skill / clean Git tests）
- E-AC-006: partially passed / amended pending（証拠: iss-00229 report で profile-aware planning は pass。2026-06-30 amendment により fail-closed artifact readiness preflight は R0 で追加対応する）
- E-AC-007〜008: pass（証拠: iss-00230 / iss-00229 reports; step routing, stale source binding tests）
- E-AC-009〜012: pass（証拠: iss-00231 / iss-00232 / iss-00244 reports; trusted base-SHA review policy は script-local instruction source へ変更済み、blocker disposition, promoted P2, rereview payload tests, explicit review completion ADR）
- E-AC-013: pass（証拠: iss-00233 `test_issue_233_pr_observation_wait_exposes_automation_stalled_operator_surface`; repeated blocker fingerprint は `automation_stalled` / `human_gate` になり `merge_prepared` にならない）
- E-AC-014: pass（証拠: iss-00233 `test_workflow_next_missing_assurance_uses_strict_legacy_execution_authority`, `test_assurance_show_and_verify_strict_legacy_missing`; missing assurance は strict-legacy ready、invalid / stale assurance は fail-closed）
- E-AC-015: pass（証拠: iss-00233 Auto-Lite readiness assertions; `automatic_lite_default_enabled=false`、future adoption gates は accepted ADR / policy version bump / rollout Issue / telemetry gate）
- E-AC-016: pass（証拠: iss-00233 `auto_lite_readiness_report` efficiency baseline assertions; Lite / Standard / Strict の invocation / review generation / workflow cost proxy 差分を固定し、live telemetry 不足は missing metrics summary として明示）
- E-AC-017〜021: pass（証拠: iss-00230 report; step assurance, context routing, reviewer clean-room, bounded return contract, stale context invalidation tests）
- E-AC-022: pending（証拠: `20260630t111316z-adr` と draft routing research は採用済み。R0 + G1〜G4 の implementation / smoke / reviewer evidence 完了後に pass 判定する）

## Current Operational Contract Ledger

| Contract | Current authority | Projection / fallback boundary | Status | Evidence |
|---|---|---|---|---|
| Issue planning / execution handoff | `./spec-dock/scripts/spec-dock guidance issue-planning` / `issue-execution` stdout | `.agent/runbooks/current-runbook.*` / `active/current-runbook.*` are human/debug-only non-canonical projection files and are not agent handoff authority | pass | `iss-00238` report; `iss-00241` S90/S99 reconciliation; manual temp repo guidance flow |
| Historical command wording | `workflow next` is superseded command wording when it appears in historical ADR / prior issue evidence | It must not be described as the current entrypoint | pass | S90 docs inspection; final stale wording inspection |
| Review trigger instruction | Valid script-local instruction -> deterministic multiline `@codex review` with instruction path / instruction hash / reviewed head SHA | missing instruction -> plain deterministic fallback; invalid / oversized / unreadable / non-UTF-8 -> no PR comment, human gate / fail-closed. Old trusted base policy behavior is changed/superseded. | pass | `iss-00244` S100-S199 evidence; `20260623t074444z-adr` |
| Review completion observation | Current trigger/head-bound Codex submitted PR review or strict no-findings issue comment is completion proof | `completion_signal=none`, CI passed, quiet window, same fingerprint, selected comments 0, or elapsed time are not completion proof. Missing completion by deadline -> retryable timeout / wait_or_resume / observation_complete=false. | pass | `iss-00244` S300-S399 plan; `20260628t154553z-adr` |

## Corrective Issues Inclusion Ledger

| Issue | Scope | Disposition | Epic close-readiness status | Evidence |
|---|---|---|---|---|
| `iss-00237` / `#237` | Manual test routing failure analysis and routing classifier repair | included corrective issue | pass | report records Red/Green closure, reviewer gate, and commit gate evidence |
| `iss-00238` / `#238` | Stdout guidance handoff instead of generated workflow files | included corrective issue | pass | report records `guidance <target>` handoff, projection human-only boundary, reviewer gates, and S90 evidence |
| `iss-00239` / `#239` | Compose issue planning templates after assurance classification | formally superseded by `iss-00241` | formal supersede | report records `./spec-dock/scripts/spec-dock close iss-00239` exit 0 with `state=CLOSED already_closed=true`; GitHub `#239` closed at `2026-06-27T05:17:44Z` |
| `iss-00241` / `#241` | Resolve Epic traceability and review policy gate gaps | included corrective integration issue | pass | S01〜S04, S90, and S99 closure evidence recorded; focused suite, sync/validate, manual flow, and final qa/code/spec reviewer gates passed |
| `iss-00251`〜`iss-00255` / `#251`〜`#255` | Grade-aware Issue authoring / readiness corrective tranche | included planned corrective tranche | pending implementation | Formal Issue 作成と dependency registration は完了。draft requirement / design / plan を作成済み。実装・smoke・reviewer evidence 完了後に Epic close-readiness を pass 判定する |

## Epic Traceability Quality Gate Ledger

| Gate | Required audit | Status | Evidence / limitation | Next action |
|---|---|---|---|---|
| QG-006 | Step closure / reviewer gate / commit gate cross-issue audit | pass | Initial implementation issue reports and corrective issue reports are included; `iss-00239` is formal supersede; `iss-00241` S01〜S04/S90/S99 reviewer gates passed. S99 commit evidence is recorded in the issue report commit gate. | none |
| QG-007 | Context packet / clean-room / bounded return evidence audit | pass | E-AC-017〜021 point to `iss-00230` report; S99 final QA/spec reviews accepted the existing context packet, clean-room reviewer / consultant, and bounded return evidence coverage without requiring a human gate. | none |
| QG-008 | Auto-Lite readiness / automatic Lite default disabled / efficiency evidence audit | pass | E-AC-015〜016 point to `iss-00233` Auto-Lite readiness and efficiency baseline; automatic Lite default remains disabled; final QA/spec reviews accepted missing-metrics handling without requiring a human gate. | none |
| QG-009 | Grade-aware authoring / artifact readiness amendment audit | pass | E-RQ-006 / E-AC-006 / E-RQ-022 / E-AC-022 were amended to cover R0 + G1〜G4. Fresh `spec-reviewer` returned pass with confidence 0.90; non-blocking P2 stale checkpoint wording was fixed. Formal corrective Issues `iss-00251`〜`iss-00255` were created and dependency edges registered. | fresh integrated review before individual Issue execution |
| QG-010 | Formal corrective Issue handoff integration review | pass | Fresh integrated `spec-reviewer` reviewed Epic plan / design / report, `iss-00251`〜`iss-00255` draft requirement / design / plan, and `.meta.json` dependencies. Findings none, `review_status: pass`, confidence 0.88. | proceed to `iss-00251` implementation |

## ロールアウト結果（必要なら） (任意)
- 段階公開の状況:
  - 初期 rollout では automatic Lite default を有効化していない。
  - substantive Issue + missing assurance は strict-legacy compatibility path で execution-ready になる。
  - future Auto-Lite adoption は accepted ADR、policy version bump、rollout Issue、telemetry gate が揃うまで blocker として report される。
- 監視値（エラー率/レイテンシなど）:
  - live telemetry backend はこの Epic では追加していない。
  - `auto_lite_readiness` は required metrics と missing metrics summary を機械可読に出し、efficiency baseline fixture で expected cost proxy を固定する。
- 障害/アラート:
  - 該当なし。

## フォローアップ（別Issue化） (必須)
- dedicated review-instruction doctor surfacing は、この Epic では script-local instruction validation / operator evidence までを対象とし、専用 doctor command は未作成。
- production telemetry backend と automatic Lite activation tuning は、この Epic の initial rollout 対象外。採用には accepted ADR、policy version bump、rollout Issue、telemetry gate が必要。
- I06 で defer した automation-stalled operator surface は iss-00233 で resolved。
- R0 / G1 / G2 / G3 / G4 の formal Issue 作成と dependency registration は完了。次は `iss-00251`〜`iss-00255` を依存順に個別実装する。

## 省略/例外メモ (必須)
- 該当なし
