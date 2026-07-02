---
種別: レポート（Epic）
ID: "epic-00270"
タイトル: "Upstream Planning Governance And Templates"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["init-local-00003"]
---

# epic-00270 Upstream Planning Governance And Templates — レポート（進捗 / 決定 / 結果）

> このテンプレートは observed evidence slot scaffold です。Epic の進捗、採用判断、reviewer state、blocking / next action、closure / follow-up を記録する starting shape を提供しますが、workflow / compliance authority ではありません。判断の詳細と lifecycle policy は skills / docs / accepted ADRs / reviewer gates を参照し、観測した証跡だけをこの report ledger に残します。

## 進捗サマリー (必須)
- 現在地（何が完了し、何が未完か）:
  - V3 planning pack を raw intake artifact として保存し、repo 実装状況と直近履歴を調査した。
  - ユーザー interview により、Issue slicing flexibility、PR delivery boundary、canonical detail level の方針を採用した。
  - V3 reference を全文貼りせず、canonical docs / split artifacts / decision candidate / future ADR 候補へ流す参照地図を作成した。
  - 完全理解・自力調査・必要最小限のユーザー質問・知識外部化を canonical authoring 前提として ADR 化した。
  - Matt Pocock 氏の `/grill-me` / `/grill-with-docs` を ChatGPT browser synthesis と primary sources で調査し、SpecDock 版への写像を research artifact に保存した。
  - Handoff package inspection は Option B を採用し、machine-checkable な構造欠落を blocking fail、意味的品質を reviewer finding とする方針を決めた。
  - `system-architect` に design / plan draft artifact の作成を委任し、採用可能な内容を main orchestrator が canonical `requirement.md` / `design.md` / `plan.md` へ再記述した。
  - Fresh `spec-reviewer` gate は Lovelace (`019f20e7-b841-77d0-894d-ad2f68bde70e`) により一度 `review_status: pass` となった。
  - その後、ユーザー補足により日本語ファースト spec / artifact authoring を Epic scope へ追加し、`requirement.md` / `design.md` / `plan.md` を日本語ファーストへ更新した。
  - 更新後の canonical set は Zeno (`019f210e-28c1-7150-99ad-c5ab59e07e3a`) により `review_status: pass` となった。残ったP2/P3の日本語説明修正はこの report 更新で反映した。
  - `plan.md` の6 Slice を actual Issue として `iss-00271` から `iss-00276` に変換し、Issue間のリレー依存を設定した。
  - 各Issueに正規 `requirement.md` を作成した。当初 canonical `design.md` / `plan.md` に置いた pre-start draft body は、後続分析により Issue-local draft artifacts へ移す対象として再分類した。
  - 当時の batch Issue planning set は Pascal (`019f212c-b416-7a31-b2c8-60b746a3ce99`) により `review_status: pass` となった。その後のADRにより canonical Issue `design.md` / `plan.md` 境界を修正したため、Pascal pass は historical evidence として扱う。
  - ローカル検証では `./spec-dock/scripts/spec-dock validate` が成功した。`deps check` は、前段Issue未完了のため `epic-00270` / `iss-00276` が blocked となり、これはリレー依存どおりの状態である。
  - Issue Start 前の `draft-design` / `draft-plan` 作成方針について再分析し、command は既存 `new artifact draft-*` primitive を強化し、actor obligation は grade-aware workflow / EAL で管理する方針を accepted ADR とした。
  - `iss-00271` から `iss-00276` の pre-start design / plan seed を Issue-local `draft-design` / `draft-plan` artifacts へ移し、canonical Issue `design.md` / `plan.md` を awaiting-assurance-compose placeholder に戻す planning correction を実施した。
  - 修正後の current planning set は Goodall (`019f21f9-b2ab-7182-8246-96997f8571d9`) により fresh `spec-reviewer` gate で `review_status: pass` となった。
  - `iss-00271` から `iss-00274` は完了済みである。現在は `iss-00275` を active にし、system-architect / implementation-planner draft を採用して正規 `design.md` / `plan.md` を具体化している。
- 次のマイルストーン:
  - `iss-00275` の正規 `requirement.md` / `design.md` / `plan.md` / `report.md` を fresh `spec-reviewer` に通し、focused tests / smoke checks の実装へ進む。
- ブロッカー:
  - 現時点で作業停止ブロッカーはなし。

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact やEpic判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | V3 ZIP intake | `requirement.md` / `design.md` / `plan.md` の根拠 | V3 clean pack は prior V2 intake を置き換え、この Epic に必要な upstream planning analysis を含む。 | `artifacts/20260702t014409z-01-phase3-v3-planning-pack-full-intake.md` | 必要な主張だけを canonical docs へ反映し、全文貼り付けはしない。 |
| EAL-002 | adopted | repo survey | `design.md` / `plan.md` の根拠 | 現在の repo には artifacts と Issue grade / TDD hardening がすでにあり、主な不足は Initiative / Epic upstream planning surface である。 | `artifacts/20260702t014409z-research-phase3-repo-context-implementation-survey.md` | 実装Issueのscopeと検証計画に使う。 |
| EAL-003 | adopted | user interview | `plan.md` の Issue slicing policy | V3の6 Issueは provisional baseline であり、追加Issue / 再分割は必要時だけ許可し、medium gate を通す。 | `artifacts/20260702t014409z-02-interview-phase3-first-scope-interview.md`, `artifacts/20260702t015012z-interview-phase3-issue-slicing-flexibility-criteria.md` | `plan.md` に反映し、将来の再分割証跡を記録する。 |
| EAL-004 | adopted | user interview | `requirement.md` / `plan.md` の delivery gate | この Epic は原則1PRで収める想定であり、1PR delivery が現実的でなくなる場合だけ Issue単位のPR分割を再検討する。 | `artifacts/20260702t015343z-interview-phase3-delivery-pr-boundary.md` | final quality Issue と 1PR PR-readiness gate に反映する。 |
| EAL-005 | adopted | user interview / synthesis | `design.md` / `plan.md` の reference flow | canonical docs には採用済みdecisionとhandoffを含め、詳細なV3分析は必要に応じて artifacts と ADR候補へ分割する。 | `artifacts/20260702t015700z-interview-phase3-canonical-detail-level.md`, `artifacts/20260702t020436z-01-disc-phase3-reference-adoption-map.md`, `artifacts/20260702t020436z-decision-candidate-phase3-canonical-reference-flow-decision.md` | 分割参照を使ってauthoringし、durable decisionだけADR化する。 |
| EAL-006 | adopted | deep consultant / user decision / ADR | `design.md` / `plan.md` / provider docs scope | Scope-layering publication surface は、provider-side reference `docs/authoring/scope-layering.md` 1つと、workflow / docs / skills / templates からの thin links として採用された。 | `artifacts/20260702t022727z-research-deep-consultant-scope-layering-publication-recommendation.md`, `artifacts/20260702t022907z-adr-scope-layering-reference-publication-surface.md` | accepted ADR を canonical docs に反映し、Epic plan に実装とsmoke workを割り当てる。 |
| EAL-007 | adopted | user interview | `design.md` / `plan.md` / Slice 05 acceptance criteria | scope-layering enforcement は medium strictness とし、構造的に機械検出できる違反はfail、解釈を要する問題は reviewer finding とする。 | `artifacts/20260702t023036z-interview-phase3-scope-layering-review-strictness.md` | fail / reviewer-finding の分離を design と smoke-test plan に反映する。 |
| EAL-008 | adopted | user interview | `requirement.md` / `design.md` / `plan.md` / Slice 01-02 acceptance criteria | Initiative / Epic templates は architecture-aware だが architecture-neutral とし、DDD / EDA を標準前提にせず、既存architectureが明確ならそれに合わせる。 | `artifacts/20260702t023501z-interview-phase3-ddd-eda-template-weight.md` | template design principles に反映し、DDD / EDA-only smoke expectations を避ける。 |
| EAL-009 | adopted | user decision / ADR | `requirement.md` / `design.md` / `plan.md` / Slice 01-02 acceptance criteria | architecture-neutral template authoring policy は accepted ADR として採用され、templates は DDD / EDA を標準前提にせず、明確なarchitectureへ適応する。 | `artifacts/20260702t024118z-adr-architecture-neutral-template-authoring-policy.md` | accepted ADR を canonical docs と template redesign criteria に反映する。 |
| EAL-010 | adopted | user decision / ADR | `design.md` / `plan.md` / clarification workflow / authoring gates | canonical authoring 前に完全な source-grounded understanding を作り、自力調査、必要なuser-intent gapの質問、採用知識の外部化を必須にする。 | `artifacts/20260702t024032z-interview-phase3-artifact-adoption-requiredness.md`, `artifacts/20260702t025127z-adr-complete-understanding-before-canonical-authoring.md` | clarification workflow design、Spec Authoring Gate、downstream planning skill guidance に反映する。 |
| EAL-011 | adopted | ChatGPT browser synthesis / public primary-source research | `design.md` / `plan.md` の clarification workflow model | Matt Pocock氏の `/grill-with-docs` は、一問ずつのsource-grounded grilling、codebase self-investigation、語彙やdecisionの外部化、sparse ADR、downstream authoring前のdecision preservation という望ましいバランスを示す。 | `artifacts/20260702t025127z-01-research-grill-with-docs-research.md` | SpecDock-native clarification flow の設計参考にし、`CONTEXT.md` や slash-command layout はそのままコピーしない。 |
| EAL-012 | adopted | user interview | `design.md` / `plan.md` の handoff package inspection policy | Epic execution handoff inspection は medium strictness とし、machine-checkable structural omission は blocking fail、semantic sufficiency と quality concern は reviewer finding とする。 | `artifacts/20260702t030615z-interview-phase3-handoff-package-inspection-strength.md` | fail / finding の分離を execution entrypoint design、Issue readiness contract、smoke / reviewer plan に反映する。 |
| EAL-013 | deferred | delegated draft | `design.md` / `report.md` の design authoring evidence | `system-architect` design draft は有用な構造を提供したが、diff guard が既存/並行dirty stateで失敗し、fresh prior requirement reviewer pass もなかったため、promotion evidence ではない。 | `artifacts/20260702t031957z-disc-epic-design-draft-upstream-planning-governance.md` | canonical design は main orchestrator が手動authoringした。draft は advisory provenance として残す。 |
| EAL-014 | deferred | delegated draft | `plan.md` / `report.md` の plan authoring evidence | `system-architect` plan draft は有用な構造を提供したが、delegated plan promotion prerequisites を満たしていなかったため、promotion evidence ではない。 | `artifacts/20260702t032014z-disc-epic-plan-draft-upstream-planning-governance-templates.md` | canonical plan は main orchestrator が手動authoringした。draft は advisory provenance として残す。 |
| EAL-015 | adopted | main orchestrator integration | `requirement.md` / `design.md` / `plan.md` | V3 intake、user interviews、accepted ADRs、Grill With Docs research、split disc artifacts を raw transcript dump にせず canonical Epic requirement / design / plan へ採用した。delegated drafts は構造参考のみで promotion evidence ではない。 | `requirement.md`, `design.md`, `plan.md` | EAL-017 の日本語ファースト更新後、fresh `spec-reviewer` を再実行する。 |
| EAL-016 | deferred | fresh `spec-reviewer` gate | previous `requirement.md` / `design.md` / `plan.md` / `report.md` | Lovelace は previous canonical set を review して `review_status: pass` としたが、その後に日本語ファースト spec / artifact authoring を追加したため、現在のpromotion gateではなく historical evidence として扱う。 | reviewer: `019f20e7-b841-77d0-894d-ad2f68bde70e` | 更新後の canonical set に対して fresh `spec-reviewer` を再実行する。 |
| EAL-017 | adopted | user clarification / ADR | `requirement.md` / `design.md` / `plan.md` / `report.md` | ユーザーは、現在のファイル修正だけでなく、日本語の requirement / design / plan と artifacts を作成できること自体をこの Epic scope に含めるべきだと補足した。これを accepted ADR として昇格し、canonical requirement / design / plan へ反映した。 | `artifacts/20260702t040113z-adr-japanese-first-spec-authoring-policy.md` | EAL-018 の reviewer pass により反映確認済み。 |
| EAL-018 | adopted | fresh `spec-reviewer` gate | updated `requirement.md` / `design.md` / `plan.md` / `report.md` | Zeno が日本語ファースト更新後の canonical set と指定 artifacts / ADRs / research を確認し、blocking finding なしで `review_status: pass` とした。P2/P3 の局所的な英語説明残りは、この更新で日本語へ修正した。 | reviewer: `019f210e-28c1-7150-99ad-c5ab59e07e3a` | downstream Issue scaffold / planning へ進める。 |
| EAL-019 | adopted | `spec-dock new issue` / GitHub Issue creation | `plan.md` / Issue docs | Epic plan の6 Slice を actual Issue `iss-00271` から `iss-00276` として作成し、それぞれ GitHub Issue #271-#276 に紐づけた。 | `iss-00271` / #271, `iss-00272` / #272, `iss-00273` / #273, `iss-00274` / #274, `iss-00275` / #275, `iss-00276` / #276 | batch spec-review pass 済み。`iss-00271` から順に実行する。 |
| EAL-020 | adopted | `spec-dock deps add` | Issue dependency chain | ユーザー方針どおり、IssueごとのPRではなく、`issue finish` から次の `issue start` へ進むリレー依存を設定した。 | `iss-00272 -> iss-00271`, `iss-00273 -> iss-00272`, `iss-00274 -> iss-00273`, `iss-00275 -> iss-00274`, `iss-00276 -> iss-00275` | final PR delivery は `iss-00276` だけが扱う。 |
| EAL-021 | partially_adopted | batch Issue planning authoring | `iss-00271` から `iss-00276` の `requirement.md` と Issue-local draft artifacts | Epic全体の抜け漏れ・重複を制御するため、6 Issue をまとめて正規要件と pre-start design / plan seed へ具体化した。ただし pre-start seed を canonical `design.md` / `plan.md` に置いた状態は現在のADRと矛盾するため、seed本文は Issue-local draft artifacts へ移し、canonical design / plan は placeholder に戻した。 | `issues/iss-00271-*/requirement.md`, `issues/iss-00272-*/requirement.md`, `issues/iss-00273-*/requirement.md`, `issues/iss-00274-*/requirement.md`, `issues/iss-00275-*/requirement.md`, `issues/iss-00276-*/requirement.md`, 各Issueの `artifacts/*draft-design*`, `artifacts/*draft-plan*` | Fresh `spec-reviewer` で、移行後の planning set を再確認する。 |
| EAL-022 | partially_adopted | fresh `spec-reviewer` gate | historical batch Issue planning set | Popper の初回reviewで Issue report の判断台帳不足が P1 として検出され、6件すべてに `仕様解釈・判断台帳` を追加した。再レビューで Pascal は当時の batch planning set を `review_status: pass` と判定したが、その後 accepted ADR により Issue canonical design / plan boundary を修正したため、現在のpromotion gateではなく historical consistency evidence として扱う。 | Popper: `019f2129-6a7b-7b71-b24a-6037ea886013`, Pascal: `019f212c-b416-7a31-b2c8-60b746a3ce99` | Current planning set は EAL-027 の Goodall pass で確認済み。 |
| EAL-023 | deferred | local validation commands | historical batch Issue planning set | `./spec-dock/scripts/spec-dock validate` は当時成功した。`deps check epic-00270` と `deps check iss-00276` は前段Issue未完了のため blocked を返し、リレー依存が有効であることを確認した。ただしその後に Issue draft migration と Epic docs update を行ったため、現在のvalidation evidenceとしては扱わず、historical evidence として残す。 | `spec-dock: ok (validate) nodes=178`; blockers: `iss-00271`-`iss-00275` | current validation は EAL-026 に記録する。 |
| EAL-024 | adopted | user decision / ADR | draft artifact command and grade role policy | ユーザーは、Issue Start 前の draft artifact 作成では actor 別 command を作らず、既存 `new artifact draft-design` / `draft-plan` を統一 primitive として強化し、system-architect / implementation-planner の関与は grade-aware workflow / EAL で管理する方針を採用した。 | `artifacts/20260702t073715z-decision-candidate-unified-draft-artifact-command-grade-role-policy.md`, `artifacts/20260702t074332z-adr-unified-draft-artifact-command-grade-role-policy.md` | 後続Issueで workflow docs / skills / runtime tests へ反映する。 |
| EAL-025 | adopted | planning correction | `iss-00271` から `iss-00276` の canonical `design.md` / `plan.md` と Issue-local draft artifacts | accepted ADR に従い、pre-start draft body を Issue-local `draft-design` / `draft-plan` artifacts へ移し、canonical Issue `design.md` / `plan.md` は awaiting-assurance-compose placeholder に戻した。各 Issue report に draft artifact path と Grade Specialist Evidence Gate を記録した。 | `issues/iss-00271-*/artifacts/*draft-design*`, `issues/iss-00271-*/artifacts/*draft-plan*`, `issues/iss-00272-*/artifacts/*draft-design*`, `issues/iss-00272-*/artifacts/*draft-plan*`, `issues/iss-00273-*/artifacts/*draft-design*`, `issues/iss-00273-*/artifacts/*draft-plan*`, `issues/iss-00274-*/artifacts/*draft-design*`, `issues/iss-00274-*/artifacts/*draft-plan*`, `issues/iss-00275-*/artifacts/*draft-design*`, `issues/iss-00275-*/artifacts/*draft-plan*`, `issues/iss-00276-*/artifacts/*draft-design*`, `issues/iss-00276-*/artifacts/*draft-plan*` | Goodall の fresh `spec-reviewer` pass で整合性確認済み。 |
| EAL-026 | adopted | local validation commands | current planning correction set | migration 後の canonical docs / Issue docs / report ledgers に対して `validate` を再実行し、blocking EAL が残らないことを確認した。targeted grep では canonical docs 上の `draft-before-issue-start` は検証要件の文字列としてのみ残り、canonical Issue `design.md` / `plan.md` には 12件すべて `artifact_state: awaiting-assurance-compose` が存在した。 | `./spec-dock/scripts/spec-dock validate` -> `spec-dock: ok (validate) nodes=178`; `rg 'artifact_state: awaiting-assurance-compose' ...issues/*/{design.md,plan.md}` -> 12件 | Goodall の fresh `spec-reviewer` pass で semantic consistency 確認済み。 |
| EAL-027 | adopted | fresh `spec-reviewer` gate | current Epic / Issue planning set | Goodall は current Epic requirement / design / plan / report、accepted ADR、全6 Issue の requirement / design / plan / report、draft-design / draft-plan artifacts を確認し、古い reviewer evidence、draft provenance、日本語ファースト文面、canonical placeholder boundary、責務分担、6 Issue coverage に P0/P1/P2 が残っていないと判定した。 | Goodall: `019f21f9-b2ab-7182-8246-96997f8571d9`; `review_status: pass`; `overall_confidence_score: 0.9` | `iss-00271` からリレー実行を開始する。現在は `iss-00275` active planning 中である。 |
| EAL-028 | adopted | completed Issue relay | `plan.md` / `report.md` | `iss-00271` から `iss-00274` は完了済みであり、`iss-00275` はそれらを検証入力として扱う active validation slice になった。 | completed Issues: `iss-00271`, `iss-00272`, `iss-00273`, `iss-00274`; active Issue: `iss-00275` | `iss-00275` の fresh planning review と実装へ進む。 |
| EAL-029 | partially_adopted | `iss-00275` specialist drafts | `iss-00275/design.md`, `iss-00275/plan.md`, `iss-00275/report.md` | system-architect / implementation-planner の draft は、machine / smoke / reviewer 境界、closure mapping、focused command ladder、no-PR handoff を具体化しており、正規 Issue 設計・計画へ部分採用した。final authority、reviewer pass、実行済み command claims は採用していない。 | `issues/iss-00275-*/artifacts/20260702t114631z-draft-design-system-architect-upstream-planning-validation-design.md`, `issues/iss-00275-*/artifacts/20260702t114630z-draft-plan-implementation-planner-canonical-plan-draft.md` | `iss-00275` の fresh `spec-reviewer` gate を通す。 |
| EAL-030 | adopted | fresh `spec-reviewer` gate | `iss-00275` planning set and Epic current-state references | Dewey は active Epic / Issue docs、specialist drafts、unified draft artifact ADR を確認し、`iss-00275` の AC/EC trace、machine / smoke / reviewer 境界、draft authority isolation、no-PR handoff に P0/P1/P2 がないと判定した。P3 として Epic report の古い next-action wording が指摘されたため、この更新で current state に合わせた。 | Dewey: `019f22ae-51a7-7ea2-a13c-8a2ed1806d72`; `review_status: pass`; `overall_confidence_score: 0.88` | `iss-00275` の実装へ進む。 |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | primary objective は upstream Initiative / Epic planning governance と executable downstream Issue handoff である。 | secondary requirements は、V3 reference assets の保存、controlled re-slicing、1PR delivery default、日本語ファースト spec / artifact authoring を含む。 | low | Zeno (`019f210e-28c1-7150-99ad-c5ab59e07e3a`) により `review_status: pass` |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| clarification | V3 ZIP、parent initiative docs、provider templates、planning / execution skills、workflow docs、git history、split artifacts、Matt Pocock Grill With Docs public sources、日本語ファーストuser clarification | 回答済み: six-Issue baseline は medium gate 付きで柔軟に扱う。回答済み: 原則1PR。回答済み: canonical docs は中程度の詳細で split references を使う。回答済み: complete understanding は必須で、自力調査後に user-intent gap だけ質問し、知識を外部化する。回答済み: handoff package inspection は structural blockers と semantic reviewer findings を分ける。回答済み: Japanese requirement / design / plan / report / artifacts を支援する。 | requirement / design / plan drafting のsource evidenceとして採用 | Zeno (`019f210e-28c1-7150-99ad-c5ab59e07e3a`) により `review_status: pass` | no | downstream Issue scaffold / planning へ進める。 |
| requirement | V3 ZIP、parent initiative requirement / design / plan、repo survey、accepted interviews / ADRs、split artifacts、日本語ファーストADR | blocking open question はない。Epic-level user intent decisions は解決済み。 | `requirement.md` に採用 | Zeno (`019f210e-28c1-7150-99ad-c5ab59e07e3a`) により `review_status: pass` | no | downstream Issue scaffold / planning へ進める。 |
| design | concrete `requirement.md`、accepted ADRs、split scope / template / handoff / quality artifacts、advisory system-architect design draft、日本語ファーストADR | blocking user question はない。delegated draft は promotion evidence として不適格だったため advisory input としてのみ利用した。 | main orchestrator manual authoring により `design.md` に採用 | Zeno (`019f210e-28c1-7150-99ad-c5ab59e07e3a`) により `review_status: pass` | no | downstream Issue scaffold / planning へ進める。 |
| plan | concrete `requirement.md` / `design.md`、V3 six-Issue baseline、user-approved re-slicing and delivery policy、advisory system-architect plan draft、日本語ファーストADR、unified draft artifact command ADR | blocking user question はない。actual Issue IDs は `iss-00271` から `iss-00276` として作成済み。delegated draft は promotion evidence として不適格だったため advisory input としてのみ利用した。 | main orchestrator manual authoring により `plan.md` に採用し、batch Issue planning と後続の draft artifact boundary correction へ反映 | Goodall (`019f21f9-b2ab-7182-8246-96997f8571d9`) により current planning correction 後の `review_status: pass` | no | `iss-00271` から `iss-00274` は完了済み。現在は `iss-00275` を実装へ進める。 |
| batch Issue planning | `iss-00271` から `iss-00276` の正規 `requirement.md`、Issue-local draft artifacts、placeholder canonical `design.md` / `plan.md`、Epic plan / report 更新 | 初回reviewで Issue report 判断台帳不足が見つかり、6件すべてへ判断台帳を追加済み。その後のADRにより、pre-start draft body は canonical `design.md` / `plan.md` から Issue-local artifacts へ移行した。 | Issue実行前のバトン設計として採用。要件は正本、design / plan seed は evidence-only artifact、canonical design / plan は Issue Planning で compose する。 | Goodall (`019f21f9-b2ab-7182-8246-96997f8571d9`) と Dewey (`019f22ae-51a7-7ea2-a13c-8a2ed1806d72`) により current planning / `iss-00275` planning が `review_status: pass` | no | `iss-00275` を実装し、完了後に `iss-00276` へ検証証跡を渡す。 |

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）
- 委任 authoring の使用:
  - used
- 未使用の場合:
  - 該当なし。Design / plan draft を `system-architect` に委任した。ただし canonical docs は main orchestrator が再記述した。
- lifecycle state（契約値）:
  - `requested`, `produced`, `integrated`, `partially_integrated`, `rejected`, `superseded`, `blocked`, `stale`
- 昇格不可 state:
  - `stale`, `rejected`, `superseded`, `blocked`
- 標準出力先:
  - 対象 scope の `artifacts/` direct child にある flat Markdown
  - filename: typed artifact は `<ts>-<type>-<slug>.md` または `<ts>-<nn>-<type>-<slug>.md` を使う。blank artifact は `<ts>-<slug>.md` または `<ts>-<nn>-<slug>.md` を使う。
- 軽量 provenance:
  - `created_by_role`, `scope_id`, `source_paths`, `intended_targets`, `adoption_status: unreviewed`, `reflected_to: []`, `diff_guard_result`, fallback decision, report evidence destination, adoption ledger note
  - 互換 label: role, phase, scope, authorization source, source artifacts, draft artifact path, status, integration result, rejected portions, blockers, reviewer result, promotion decision
- 禁止 self-claim:
  - `authority: accepted`, `adoption_status: adopted`, non-empty `reflected_to`, reviewer pass, phase completion, implementation readiness
- 禁止 wildcard token:
  - `*`, `grants.*`, `all`
- 標準必須にしない field:
  - task manifest hash, Permission Profile hash, session invocation hash, probe run id, session hash
- historical note:
  - legacy `discussions/` と既存 `iss-00126` などの manifest/Profile/probe/session artifacts は grandfathered evidence として残し、削除・rename・validation failure 化しない。

| ロール（created_by_role） | 範囲（scope_id） | ドラフトパス（artifact draft path） | 参照元（source_paths） | 予定反映先（intended_targets） | 採用状態（adoption_status） | 反映先（reflected_to） | 差分ガード結果（diff_guard_result） | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果（reviewer result） | 昇格判断（promotion decision） |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| system-architect | epic-00270 | `artifacts/20260702t031957z-disc-epic-design-draft-upstream-planning-governance.md` | active epic docs、parent initiative docs、V3 intake、split artifacts、accepted ADRs、user interviews | `design.md`, `plan.md`, `report.md` | deferred | なし（[]） | failed | advisory input のみ。canonical design は main orchestrator が手動authoringした。 | direct delegated promotion、final authority claims、冗長な raw draft wording は採用しない。 | downgrade 後のblockingはない。failed diff guard により draft は promotion evidence として使えない。 | previous canonical set は reviewer pass 済み。その後の日本語ファースト更新と batch Issue planning は EAL-018 / EAL-022 で re-review 済み。 | promotion evidence ではない。reviewer は current canonical docs を評価する。 |
| system-architect | epic-00270 | `artifacts/20260702t032014z-disc-epic-plan-draft-upstream-planning-governance-templates.md` | active epic docs、parent initiative docs、V3 intake、split artifacts、accepted ADRs、report EAL | `plan.md`, `report.md` | deferred | なし（[]） | pending | advisory input のみ。canonical plan は main orchestrator が手動authoringした。 | direct delegated promotion、actual Issue creation、reviewer-pass claims は採用しない。 | downgrade 後のblockingはない。delegated promotion prerequisites を満たしていなかった。 | previous canonical set は reviewer pass 済み。その後の日本語ファースト更新と batch Issue planning は EAL-018 / EAL-022 で re-review 済み。 | promotion evidence ではない。reviewer は current canonical docs を評価する。 |

### 委任ドラフトの失敗モード（Delegated Draft Failure Modes）
| 失敗モード | 期待される判定 | 許可される次アクション | レポート証跡の記録先（report evidence destination） | 昇格可否 |
|---|---|---|---|---|
| ワークフロー単位の許可証跡不足（missing workflow-scoped authorization evidence） | blocked / incomplete | ワークフロー利用依頼の authorization source と boundary を記録する、または手動 authoring に戻す | ワークフロー単位の named role 許可（Workflow-Scoped Authorization） / この section | ineligible |
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
- `artifacts/20260702t022907z-adr-scope-layering-reference-publication-surface.md`:
  - Scope-layering / Initiative-Epic-Issue責務モデルは、1つのprovider-side reference `docs/authoring/scope-layering.md` として公開し、既存workflow/docs/skills/templatesは薄くリンクする。
- `artifacts/20260702t024118z-adr-architecture-neutral-template-authoring-policy.md`:
  - Initiative/Epic templates は DDD/EDA を標準前提にせず、既存または明確化されたアーキテクチャに合わせる architecture-neutral / architecture-aware 方針を採る。
- `artifacts/20260702t025127z-adr-complete-understanding-before-canonical-authoring.md`:
  - Canonical authoring 前に完全な source-grounded understanding を作り、自力調査で分かることは人間に聞かず、必要な user intent gap だけを interview し、採用知識を artifacts / ADR / canonical docs / report ledger に外部化する。
- `artifacts/20260702t040113z-adr-japanese-first-spec-authoring-policy.md`:
  - 日本語運用では requirement / design / plan / report / artifacts の本文を日本語ファーストで作成し、英語は識別子・固定語・外部固有名詞を中心に許容する。
- `artifacts/20260702t074332z-adr-unified-draft-artifact-command-grade-role-policy.md`:
  - Issue-local `draft-design` / `draft-plan` の作成 command は actor semantics を持たず、既存 `new artifact draft-*` primitive を強化する。system-architect / implementation-planner の関与は Issue grade に応じた workflow / EAL / reviewer gate で管理する。

## 完了した Issue / PR / Release (必須)
- 完了したIssue:
  - `iss-00271` / #271: Initiative templates
  - `iss-00272` / #272: Epic templates
  - `iss-00273` / #273: scope-layering reference / planning guidance
  - `iss-00274` / #274: Epic execution handoff / readiness
- 作成済みIssue:
  - `iss-00271` / #271: Initiative templates
  - `iss-00272` / #272: Epic templates
  - `iss-00273` / #273: scope-layering reference / planning guidance
  - `iss-00274` / #274: Epic execution handoff / readiness
  - `iss-00275` / #275: upstream planning smoke tests / validation
  - `iss-00276` / #276: final quality gate / PR delivery
- PR:
  - 未作成。PR は `iss-00276` で扱う。

## 受け入れ条件（E-AC）の達成状況 (必須)
- E-AC-001: pending
  - 実装担当Issue `iss-00271` は完了済み。最終達成判定は `iss-00276` の integrated quality gate で確認する。
- E-AC-002: pending
  - 実装担当Issue `iss-00272` は完了済み。最終達成判定は `iss-00276` の integrated quality gate で確認する。
- E-AC-003: pending
  - 実装担当Issue `iss-00273` は完了済み。最終達成判定は `iss-00276` の integrated quality gate で確認する。
- E-AC-004: pending
  - 実装担当Issue `iss-00274` は完了済み。最終達成判定は `iss-00276` の integrated quality gate で確認する。
- E-AC-005: pending
  - 実装担当Issue `iss-00275` は active planning 中。focused tests / smoke checks は未実施。
- E-AC-006: pending
  - 実装担当Issue `iss-00276` は作成済み。実装は未実施。
- E-AC-007: pending
  - `iss-00271` から `iss-00274` で反映済み。`iss-00275` / `iss-00276` で検証する。
- E-AC-008: partially_completed
  - planning correction として、`iss-00271` から `iss-00276` の pre-start design / plan seed を Issue-local draft artifacts へ移し、canonical `design.md` / `plan.md` を awaiting-assurance-compose placeholder に戻した。
  - 将来の workflow / command / validation としての固定は、`iss-00274` / `iss-00275` / `iss-00276` で扱う。

## ロールアウト結果（必要なら） (任意)
- 該当なし:
  - まだ planning authoring phase であり、runtime rollout は未実施。

## フォローアップ（別Issue化） (必須)
- なし:
  - 追加Issueは現時点では作成していない。
  - 次の作業は `iss-00275` の focused tests / smoke checks を実装し、完了後に `iss-00276` へ validation evidence を渡すこと。

## 省略/例外メモ (必須)
- 該当なし
