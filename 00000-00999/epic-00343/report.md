---
種別: レポート（Epic）
ID: "epic-00343"
タイトル: "Workbench Shell And Explicit File Artifact Import"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-28"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["init-local-00002"]
---

# epic-00343 Workbench Shell And Explicit File Artifact Import — レポート（進捗 / 決定 / 結果）

> このテンプレートは observed evidence slot scaffold です。Epic の進捗、採用判断、reviewer state、blocking / next action、closure / follow-up を記録する starting shape を提供しますが、workflow / compliance authority ではありません。判断の詳細と lifecycle policy は skills / docs / accepted ADRs / reviewer gates を参照し、観測した証跡だけをこの report ledger に残します。

## 進捗サマリー (必須)
- 現在地（何が完了し、何が未完か）:
  - 旧`epic-00312`で行ったユーザーinterview、repository調査、GitHub-synced ChatGPT Pro authoring ZIPをevidenceとして引き継いだ。
  - 親Initiative scopeとの衝突をfresh reviewで検出し、feature expansion authorityを持つ`init-local-00002`配下へ本`epic-00343`を作成した。
  - requirementは4回目のfresh reviewで`pass`し、design authoringへ昇格した。
  - system-architectのscope-local evidence draftをmain orchestratorが全件確認し、canonical `design.md`へ再記述した。9回目fresh design reviewは`pass`し、非ブロッキングP2のADR provenance metadataも補完した。planは未着手、Issue nodeは未作成である。
- 次のマイルストーン:
  - design passを入力としたplan authoringとfresh plan review pass。
  - reviewed planの3 vertical slicesに対する人間承認。
- ブロッカー:
  - requirement / design phaseのブロッカーなし。planは未review。

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact やEpic判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| ID | adoption_status | source | source_role | claim | target_artifact | target_section | rationale | evidence_strength | evidence_path | adopter | reviewer | blocking | next_action |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EAL-001 | adopted | Workbench shell interview | user | fresh root / future node shell、existing no-backfill、optional presence | `requirement.md` | 3.1、6.1、7.1 | ユーザーの確定判断を直接採用 | primary | `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00312-experimental-local-workbench-and-worktree-handoff/artifacts/20260728t054625z-interview-workbench-tracked-shell-coverage.md` | main orchestrator | fourth fresh spec-reviewer pass | no | designへtrace |
| EAL-002 | adopted | filename contract interview | user | timestamp/collision prefix + original basename/extension、title/slug/token不要 | `requirement.md` | E-RQ-014〜016、E-AC-012〜014 | ユーザーOption Aを採用し、grammar衝突だけ`--`delimiterで解消 | primary | `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00312-experimental-local-workbench-and-worktree-handoff/artifacts/20260728t060417z-interview-generic-file-import-filename-contract.md` | main orchestrator | fourth fresh spec-reviewer pass | no | designへtrace |
| EAL-003 | adopted | external file policy interview | user | explicit path authorization、追加flagなし、external path非開示 | `requirement.md` | E-RQ-010〜012、018、E-AC-009〜010、016 | ユーザーの確定判断とprivacy boundaryを採用 | primary | `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00312-experimental-local-workbench-and-worktree-handoff/artifacts/20260728t060706z-interview-external-file-import-policy.md` | main orchestrator | fourth fresh spec-reviewer pass | no | designへtrace |
| EAL-004 | adopted | Workbench copy disposition interview | user | manual one-shot helperとして維持 | `requirement.md` | 3.3、E-RQ-007、E-RQ-023、E-AC-007 | user-selected Option Cを採用 | primary | `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00312-experimental-local-workbench-and-worktree-handoff/artifacts/20260728t060909z-interview-workbench-copy-disposition.md` | main orchestrator | fourth fresh spec-reviewer pass | no | compatibility design / testへtrace |
| EAL-005 | partially_adopted | ChatGPT Pro Markdown ZIP | advisory authoring model | shell/import中心の3文書案と3 vertical candidates | `requirement.md`; future `design.md` / `plan.md` | 全体構造 / Issue seed | structure、reuse map、3 slicesを採用。旧Epic再利用、self-authority metadata、requirement内HOWは棄却 | corroborated | `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00312-experimental-local-workbench-and-worktree-handoff/artifacts/20260728t080013z-research-chatgpt-pro-epic-replanning-zip-evidence.md`; ZIP SHA-256 `ecd4c65a608ee4474fd5e06b0230150ba56106a5eee7418811367c9cbadca371` | main orchestrator | ZIP reviewer pass; requirement spec-reviewer pass | no | design / planを各fresh review |
| EAL-006 | adopted | old Epic requirement review | spec-reviewer | parent scope conflict、no-backfill AC、opaque lifecycle、ancestor symlink、WHAT/HOW分離 | Epic routing; `requirement.md` | 2、5〜7 | findingsを採用しfeature Initiativeへrouteして修正 | independent review | `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00312-experimental-local-workbench-and-worktree-handoff/report.md#2026-07-28-workbench--artifact-import-再計画のrouting` | main orchestrator | fourth fresh spec-reviewer pass | no | closed |
| EAL-007 | adopted | current repository surface analysis | repo-analyst | provider/template/import/publisher/scanner/sync factsとtyped grammar衝突 | `requirement.md`; future `design.md` | E-RQ-014、020、design reuse map | exact code/testsで確認された事実を採用 | repository-primary | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/artifacts.py`; `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py` | main orchestrator | fourth fresh spec-reviewer pass | no | designへtrace |
| EAL-008 | adopted | epic-00343 requirement reviews | spec-reviewer | source mutation分離、relative path基準、EAL/authorization、全failure privacy、post-publish state、identity | `requirement.md`; `report.md` | E-RQ-010、013〜018、E-AC-009、014〜016、EAL / authorization | 2回のfail findingsをすべて正本へ反映 | independent review | `report.md#仕様-authoring-ゲートspec-authoring-gate--必須` | main orchestrator | fourth fresh spec-reviewer pass | no | closed |
| EAL-009 | adopted | third epic-00343 requirement review | spec-reviewer | successor Epic作成authorizationと継続planning authorizationのexternal mutation境界を分離 | `report.md` | Workflow-Scoped Authorization | completed #343 mutationの明示許可・消費済み境界と、以後のnon-mutation planning境界を別recordへ修正 | independent review | `report.md#ワークフロー単位の-named-role-許可workflow-scoped-authorization` | main orchestrator | fourth fresh spec-reviewer pass | no | closed |
| EAL-010 | adopted | Epic architecture draft | system-architect | D-001〜D-009、exact source map、state/privacy/slot/opaque lifecycle、test seams | `design.md` | 1〜15 | source requirement hash一致、repo factsをmain orchestratorが再確認しcanonicalへ再記述 | repository-corroborated draft | `artifacts/20260728t083918z-disc-epic-00343-workbench-file-import-architecture-draft.md`; pre-adoption SHA-256 `b65c88a1d683f33d26ffd472511e5fab07525b8a2991cbd384e8b0d20a8c2083` | main orchestrator | fresh design spec-reviewer pending | yes | design passで解除 |
| EAL-011 | adopted | first epic-00343 design review | spec-reviewer | destination integrity failure、hidden marker package-data、delegated metadata、diagram metadata、report phase | `design.md`; draft artifact; `report.md` | D-008、diagrams、File Plan / T3〜T6、progress | 全5 findingを採用。integrity failureをwarningから分離し、explicit package-dataとdiagram ownershipを追加、draft self-adoptionを撤回 | independent review | `report.md#仕様-authoring-ゲートspec-authoring-gate--必須` | main orchestrator | fresh design re-review pending | yes | design passで解除 |
| EAL-012 | adopted | second epic-00343 design review | spec-reviewer | post-publication integrityの永続識別gap、dependency/context生成trace不足 | `design.md` | D-005、D-008〜009、state model、T3〜T5 | generic publicationをverified named tempのsame-inode exclusive hard-link commitへ限定してambiguous integrity stateを除去。deps/contextのgraph/manifest-only boundaryとbody非読込testを追加 | independent review | `report.md#仕様-authoring-ゲートspec-authoring-gate--必須` | main orchestrator | fresh design re-review pending | yes | design passで解除 |
| EAL-013 | partially_adopted | third epic-00343 design review | spec-reviewer | named-temp hard-link TOCTOU、report review state | `design.md`; `report.md` | D-005、D-008、state model、T3/T4、progress | mutable pathnameを廃止しverified FD + opened parent FDのOS primitiveへ固定。pre/post rollback案は次reviewで過剰・不完全と判明しEAL-014で置換 | independent review | `report.md#仕様-authoring-ゲートspec-authoring-gate--必須` | main orchestrator | fourth design review | no | EAL-014にsuperseded |
| EAL-014 | adopted | fourth epic-00343 design review | spec-reviewer | state diagram / commit point不一致、macOS rollback ownership / fsync gap | `design.md`; `report.md` | D-005、D-008、state model、T3/T4、threat model | rollback-based post-check設計を撤回し、FD-bound no-replace syscall成功を単一commit pointへ統一。非協調actorのcommit瞬間directory renameを明示的threat-model外とした | independent review | `report.md#仕様-authoring-ゲートspec-authoring-gate--必須` | main orchestrator | fresh design re-review pending | yes | design passで解除 |
| EAL-015 | adopted | fifth epic-00343 design review | spec-reviewer | `not_committed`存在条件、source最終検証境界、filesystem capability、親portfolio登録 | `design.md`; parent Initiative `plan.md`; `report.md` | D-005、D-008、state model、T3/T6、threat model、Epic portfolio | `not_committed`をcommand ownershipへ修正し、最終source再読後の非協調write境界を明示。Linux/macOSをfilesystem capabilityで定義し、親portfolioを正本へ登録する | independent review | `report.md#仕様-authoring-ゲートspec-authoring-gate--必須` | main orchestrator | fresh design re-review pending | yes | design passで解除 |
| EAL-016 | adopted | sixth epic-00343 design review | spec-reviewer | non-privileged Linux publication、cross-filesystem original source、不可逆contractのADR判断 | `design.md`; Epic-local ADR; `report.md` | D-005、T3/T6、ADR Candidates / Decisions | Linuxを通常権限のheld-FD `/proc/self/fd` linkへ修正し、same-filesystem制約をstaged temp/destinationだけへ限定。identity/privacy/retry contractをaccepted ADRへ分離する | independent review | `report.md#仕様-authoring-ゲートspec-authoring-gate--必須` | main orchestrator | fresh design re-review pending | yes | ADR作成・design passで解除 |
| EAL-017 | adopted | seventh epic-00343 design review | spec-reviewer | ADR decision ownerと反映先のauthority不整合 | Epic-local ADR; `report.md` | front matter、Decision、design gate | user-owned product contractとorchestrator-owned architecture contractを分離し、未着手planを`reflected_to`から除外 | independent review | `report.md#仕様-authoring-ゲートspec-authoring-gate--必須` | main orchestrator | fresh design re-review pending | yes | design passで解除 |
| EAL-018 | adopted | eighth epic-00343 design review | spec-reviewer | accepted ADRと未決候補表記の矛盾、report progress | `design.md`; `report.md` | ADR Candidates、Requirement Clarification Requests、progress | D-006/D-008の判断記録をaccepted ADRへ一本化し、review現在地を8回目finding反映済みへ更新 | independent review | `report.md#仕様-authoring-ゲートspec-authoring-gate--必須` | main orchestrator | fresh design re-review pending | yes | design passで解除 |
| EAL-019 | adopted | ninth epic-00343 design review | spec-reviewer | design gate pass、ADR provenance metadata P2 | Epic-local ADR; `report.md` | ADR front matter、design gate | `pass`を採用。architecture draftを`derived_from`、実反映済みreportを`reflected_to`へ追加し、未着手planは除外したまま維持 | independent review | ninth fresh design review result、confidence 0.96 | main orchestrator | ninth fresh spec-reviewer pass | no | plan authoringへpromote |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | fresh root / future nodeのWorkbench shellとgeneric single-file importをprimary capabilityとしてE-RQ-001〜020へ固定 | manual `workbench copy`互換、provider / dogfood parity、docs | low。copy lifecycleやChatGPT専用importへ再収束しないようnon-scopeと3-slice seedで固定 | fourth fresh requirement review pass |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | 親Initiative、旧Epic interviews/research、GitHub-synced ChatGPT ZIP、current source/tests、repo analysis | ユーザー選択は確定。旧Epicreview 5件、本Epic初回review 5件、2回目review 4件、3回目review 1件へ回答済み | interview採用、ChatGPT ZIP部分採用、review finding採用 | fourth fresh review `pass`、confidence 0.97 | no | design authoringへpromote |
| design | requirement pass、system-architect draft、current source/tests、ChatGPT ZIP reuse map、accepted ADR | blocking clarificationなし。不可逆contractはEpic-local accepted ADRへ分離済み | delegated draftと全review findingをmain orchestratorが採用・再記述。9回目P2 metadataも補完 | ninth fresh review `pass`、confidence 0.96 | no | plan authoringへpromote |
| plan | ChatGPT ZIPの3 candidate proposalとrepo analysisあり | Issue node作成は人間承認待ち | none | not reviewed | yes | implementation-planner draft後にcanonical authoring |

## ワークフロー単位の named role 許可（Workflow-Scoped Authorization）

| authorization source | repo / worktree | active scope | session | named roles / actions | boundary | expires / invalidation condition | denied / unavailable / host conflict | next action |
|---|---|---|---|---|---|---|---|---|
| ユーザーによる「必要なら新たなEpicを作成し、そのEpicをactiveにして仕切り直してよい」という明示依頼 | `chemitaro/spec-dock`; `/Volumes/990p2t/offloaded/home/iwasawayuuta/.codex/worktrees/692d/spec-dock` | source: `epic-00312`; target Initiative: `init-local-00002`; created Epic: `epic-00343` | current Codex session、2026-07-28のEpic routing operation | `spec-manager`によるInitiative active設定、GitHub Epic issue #343作成、local Epic scaffold作成、Epic active設定、branch作成 / checkout、GitHub sync | この一回のsuccessor Epic routingに必要なcredentialed GitHub mutationとlocal SpecDock mutationだけを許可。Issue node、PR、merge、close、source実装変更は含まない | #343作成・active/checkout/sync完了時に消費済み。再作成、別scope、追加external mutationには無効 | なし。#343 / `epic-00343` / branch `epic-00343-workbench-shell-and-explicit-file-artifact-import`を作成済み | 完了済みoperationとして保持。追加Epic mutationは行わない |
| ユーザーによる`spec-dock-clarification`指定、Epic再構成、ChatGPT-UseによるMarkdown ZIP authoring、fresh reviewの明示依頼 | `chemitaro/spec-dock`; `/Volumes/990p2t/offloaded/home/iwasawayuuta/.codex/worktrees/692d/spec-dock` | source evidence: `epic-00312`; canonical target: `init-local-00002 / epic-00343`; Issueなし | current Codex session、2026-07-28 | ChatGPT Pro advisory authoring、`repo-analyst`によるread-only解析、fresh `spec-reviewer`によるrequirement/design/plan review、main orchestratorによるcanonical Epic docs統合 | planning evidence生成・review・canonical authoringに限定。source実装変更、Issue node作成、追加credentialed external mutation、PR/merge/closeは含まない | user revocation、active repo/worktreeまたはEpic変更、current session終了、source HEAD変更でevidence stale、workflow boundary外のactionが必要になった時 | なし。ChatGPT follow-up wrapperのpre-submit SIGPIPEは同一browser conversationの手動follow-upで回復し、fixed ZIPをreview済み | phase順序とfresh reviewer gateを継続し、Issue作成前に人間承認を得る |

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）
- 委任 authoring の使用:
  - used。
- 未使用の場合:
  - 該当なし。
- lifecycle state（契約値）:
  - `requested`, `produced`, `integrated`, `partially_integrated`, `rejected`, `superseded`, `blocked`, `stale`
- 昇格不可 state:
  - `stale`, `rejected`, `superseded`, `blocked`
- 標準出力先:
  - 対象 scope の `artifacts/` direct child にある flat Markdown
  - filename: typed artifacts use `<ts>-<type>-<slug>.md` or `<ts>-<nn>-<type>-<slug>.md`; blank artifacts use `<ts>-<slug>.md` or `<ts>-<nn>-<slug>.md`
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
| ChatGPT Pro advisory authoring | `epic-00312`から`epic-00343`へroute | fixed ZIP内`epic/{requirement,design,plan}.md` | GitHub-synced commit `1aa5fd8e7f3cf899bfefa6e1cedb864c2de3dba0`、interview/research artifacts | `epic-00343` requirement/design/plan | `partially_adopted` | [`requirement.md`, `design.md`] | SpecDock ZIP review/stage/candidate validation pass。canonical diffはmain orchestrator管理 | structure、reuse map、3 slicesを統合 | 旧Epic再利用、self-authority metadata、過剰なHOW | design fresh review | requirement pass、design pending | design passまでplan promotionなし |
| system-architect | `epic-00343` design | `artifacts/20260728t083918z-disc-epic-00343-workbench-file-import-architecture-draft.md` | requirement SHA-256 `068eda6ba36aadc93884ca8791a40c4f31998bcb47050014f07d0e623391e20c`、parent docs、source/tests、ChatGPT evidence | `design.md` | `adopted` | [`design.md`] | passed。本roleのcanonical変更なし、scope-local artifact一件のみ | D-001〜D-009とsections 1〜15をmain orchestratorが再記述 | self-authority / section 16のintegration instructionは正本へ不採用 | fresh design review | pending | fresh passまでplan promotionなし |

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
- [`20260728t100038z-adr Generic Imported File Identity And Privacy Boundary`](artifacts/20260728t100038z-adr-generic-imported-file-identity-and-privacy-boundary.md): generic `--` filename family、full destination basename identity、external source privacy、postcommit retry semanticsを固定するaccepted ADR。
- 旧`epic-00312`のtemplate-free / byte-preserving publication ADRはimplementation evidenceとして参照できるが、generic importの新しいauthorityを自動付与しない。

## 完了した Issue / PR / Release (必須)
- なし。reviewed planと人間承認前のためIssue nodeを作成していない。
- GitHub Epic issue: #343。

## 受け入れ条件（E-AC）の達成状況 (必須)
- E-AC-001〜020: 未着手。planning phaseのためimplementation完了を主張しない。

## ロールアウト結果（必要なら） (任意)
- 段階公開の状況:
  - 未開始。
- 監視値（エラー率/レイテンシなど）:
  - 該当なし。
- 障害/アラート:
  - 該当なし。

## フォローアップ（別Issue化） (必須)
- なし。plan reviewと人間承認後に必要最小限のvertical Issueを作成する。

## 省略/例外メモ (必須)
- 該当なし
