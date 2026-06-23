---
種別: 要件定義書（Epic）
ID: "<EPIC_ID>"
タイトル: "Adaptive Assurance And Compiled Agent Workflow"
関連GitHub: ["<GITHUB_EPIC_NUMBER_OR_URL>"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-22"
親: ["init-local-00003"]
---

# <EPIC_ID> Adaptive Assurance And Compiled Agent Workflow — 要件定義（何を、なぜ行うか）

## 目的（Initiative との紐づき）

- Initiative 目標 / 指標:
  - `init-local-00003 Architecture Maintenance and Hardening` のうち、SpecDock の agent workflow を、品質を維持したまま token consumption と wall-clock time を削減できる構造へ移行する。
  - workflow、artifact、review、delivery の authority を chat memory や model の都度判断に依存させず、repository と runtime が検証可能な契約として保持する。
- この Epic が提供する能力:
  - Active Issue、authoring phase、Assurance Profile、current step、PR review state に応じた「現在必要な一つの Runbook」を runtime が機械生成する。
  - Issue / Step の risk と complexity に応じ、必要な agent、reasoning effort、context policy、verification、reviewer を選択する。
  - GitHub Codex review へ trusted base branch 上の review policy を注入し、P0 / P1 を中心とする高価値 review を要求する。
  - P0 / P1 と機械的に検証された blocker だけを自動修正ループへ入れ、P2 / P3 による価値の低い review-push-review 反復を抑制する。
  - 既存 Issue を壊さず、新規 Issue から段階的に adaptive workflow へ移行できる。

## 背景・現状

- `epic-00158 Agent Workflow PDCA Hardening` により、skill / docs / templates / canonical artifact の責務境界と first-read workflow surface が整理された。
- 同 Epic は runtime gate、manual harness、regression enforcement を後続 PDCA work として残している。
- 現在の Issue workflow は高保証だが、通常 Issue にも Strict 相当の planning / execution / review gate が適用される。
- Requirement、design、plan の phase ごとに複数 reviewer / specialist が直列実行され、各 implementation step でも worker、reviewer、commit gate が繰り返される。
- サブエージェントは reasoning effort の切替、context isolation、review independence に有効だが、不要な再調査と同一文書の再読が発生すると token と時間を浪費する。
- Skill が複数 workflow docs を参照するだけでは、agent が参照先を開かず mandatory workflow を落とす可能性がある。
- 反対に、Lite / Standard / Strict / Critical の完全な手順を一つの Skill に列挙すると、instruction noise と誤分岐が増える。
- GitHub Codex review は PR 品質向上に有効だが、P2 finding、修正、push、再review の反復が delivery time の大きな割合を占める。
- 現行の fixed `@codex review` trigger は安全な write surface を持つ一方、repository 固有の review policy を渡せない。
- PR review の成功条件を「comment がゼロ」にすると、価値の低い改善まで修正対象となり、merge-ready までの時間が不必要に増える。

## 前提 Epic / 引き継ぐ決定

- 前提:
  - `epic-00158-agent-workflow-pdca-hardening`
- 引き継ぐ決定:
  - Canonical `requirement.md` / `design.md` / `plan.md` / `report.md` は main orchestrator-owned。
  - Provider-side shipped asset が authority、dogfooding mirror は validation target。
  - Reviewer / consultant は必要に応じ fresh / clean-room context を使用する。
  - Templates は scaffold であり compliance authority ではない。
- 本 Epic で更新する責務:
  - Skill は完全な profile workflow を保持せず、runtime Runbook を取得・実行する固定 kernel となる。
  - 現在の operational workflow authority は、tracked Assurance Contract と policy から compiler が生成する current Runbook に置く。

## ユースケース

### 正常系

- Active Issue がない状態で Issue Planning / Execution を開始すると、runtime は対象 Issue を `issue start` する手順だけを返す。
- Issue start 後、requirement が未完成なら requirement capture Runbook を返す。
- Requirement 完了後、runtime は risk facts から provisional Assurance Profile と Complexity Tier を計算する。
- Provisional classification に従って必要な design sections、architect、reasoning effort を選択する。
- Design 完了後、Assurance Contract を approved とし、plan / step obligations を compile する。
- Execution では current step に必要な worker、context inheritance、verification、reviewer だけを返す。
- Final delivery では PR base SHA 上の review policy を読み、review target head SHA と policy hash を含む `@codex review` comment を投稿する。
- Codex finding が P0 / P1 なら repair、verification、push、fresh review を行う。
- P2 / P3 だけなら原則 no-action / follow-up とし、そのためだけの修正・再reviewを行わない。
- 全 blocker が閉じ、required CI と review coverage が成立したら merge-prepared とする。

### 例外 / 運用シナリオ

- Requirement / design / plan の source hash が Assurance Contract と一致しない場合、Runbook を stale として execution を block する。
- 実装中に public contract、migration、security/privacy、rollback difficulty が発見された場合、Assurance を上方 escalation する。
- Lite 適格条件に unknown が含まれる場合は Lite にしない。
- Profile downgrade は自動実行せず、根拠と明示的 risk acceptance を要求する。
- Existing Issue に `assurance.json` がない場合、legacy Strict compatibility path で継続できる。
- Review policy を PR base SHA から取得できない場合、外部review必須の workflowでは human gate とする。
- P2 finding が protected domain に関係し、failing regression test 等で再現された場合、validated blocker へ昇格する。
- 自動修正が停滞した場合、回数を理由に risk を受容せず `automation-stalled` / human gate へ移行する。

## エピック要件（Epic requirements）

- E-RQ-001: State-derived workflow entrypoint
  - Planning / Execution skill は現在状態を推測せず、runtime の `workflow next` が返す一つの Runbook を実行する。
  - no-active、requirement capture、classification required、planning、execution、delivery、blocked を明確に区別する。

- E-RQ-002: Assurance Contract
  - 各 adaptive Issue は tracked `assurance.json` を持つ。
  - Profile、Complexity Tier、source binding、global obligations、step obligations、review policy、status を machine-readable に保存する。
  - Profile 名は preset であり、展開済み obligations を実行 authority とする。

- E-RQ-003: Deterministic classification
  - `lite / standard / strict / critical`を risk facts と hard trigger から決定する。
  - `routine / normal / complex / deep`を reasoning / specialist routing 用に別管理する。
  - Standard を default とし、Lite は全適格条件が肯定的に確認された場合だけ許可する。

- E-RQ-004: Fixed Skill kernel
  - Issue状態ごとに `.agents/skills/**` を差し替えない。
  - Skill は `workflow next`の実行、stdout Runbookの遵守、blocked時の停止だけを直接記述する。
  - mandatory path は別Skillや複数workflow docsの参照成功に依存しない。

- E-RQ-005: Compiled Runbook
  - runtime は current state / phase / profile / step に対応する完全な Runbook を Markdown / JSON で生成する。
  - Runbook は `.agent/` と `active/` のgenerated stateへatomicに保存し、Git差分を発生させない。
  - 未選択Profileの手順をcurrent Runbookへ混入させない。

- E-RQ-006: Adaptive artifact composition
  - design / plan / report の必要sectionsをpolicy fragmentから合成する。
  - substantive user contentを自動上書きしない。
  - escalationは必要sectionの単調追加とdownstream invalidationを行う。
  - downgradeによるsection削除を自動実行しない。

- E-RQ-007: Step Assurance
  - 各 implementation step は change facts を持ち、issue-wide obligationsとの和集合からeffective obligationsを計算する。
  - worker role、reasoning effort、context policy、verification、reviewer、re-review条件をcompileする。
  - semantic batchをcommit / review単位とし、機械的な1行1step分割を要求しない。

- E-RQ-008: Context policy
  - 実行系agentはrecent forkまたはbounded context packetを利用できる。
  - reviewer / consultantはclean-room evidence packetを利用し、author narrativeやprevious verdictへ不必要にanchorされない。
  - 子agentのraw logをmainへ転記せず、outcome、evidence ref、material decision、riskだけを返す。

- E-RQ-009: Trusted GitHub Codex review policy
  - `.github/codex/review-policy.md`をproject-owned bootstrap assetとしてGit管理する。
  - Review policyはPR headではなくPR base SHAの固定pathから取得する。
  - trigger scriptはcaller-provided arbitrary bodyを受け付けず、runtimeがpolicyとmetadataからdeterministic commentを合成する。
  - Review commentはpolicy base SHA、policy hash、reviewed head SHAを記録する。

- E-RQ-010: Blocker-centric review closure
  - Valid P0 / P1 はblockerとして修正または独立証拠による反証を要求する。
  - P2 / P3 はdefault non-blockingとし、自動修正対象にしない。
  - Protected domainかつmachine evidenceがあるP2だけをvalidated blockerへ昇格する。
  - Comment zeroではなくverified blocker zeroを終了条件とする。

- E-RQ-011: Re-review and stagnation
  - P0 / P1 / promoted blockerのcode fix後はfresh external reviewを要求する。
  - Non-material P2 fixだけでは新しいreview triggerを投稿しない。
  - 修正回数上限はrisk受容ではなくautomation-stalledへの移行条件とする。
  - stale reviewed SHAのfindingをcurrent repair inputに使わない。

- E-RQ-012: Compatibility and rollout
  - Existing Issueはstrict-legacyとしてgrandfatherする。
  - New Issueからshadow classification、opt-in、default Standardの順で段階導入する。
  - Provider source / dogfooding mirror / installer / docs / testsを同期する。
  - rollback時にlegacy workflowへ戻せる。

- E-RQ-013: Observability
  - Agent invocation、reasoning、token、active time、test time、PR wait、review generation、finding disposition、push countを観測可能にする。
  - Generated raw eventからhuman-readable report summaryを投影できる。
  - Secret、private reasoning、raw credentialを記録しない。

## エピック受け入れ条件（Epic acceptance criteria）

- E-AC-001: No-active Runbook
  - 前提: Active Issueがない。
  - 操作: Issue PlanningまたはExecutionで`workflow next`を実行する。
  - 期待結果: `issue start <target>`またはtarget入力要求だけがnext actionとして返り、authoring / implementationを開始しない。
  - 観測点: CLI JSON / Markdown、state-machine tests。

- E-AC-002: Provisional / approved classification
  - 前提: Active Issueのrequirementにrisk factsがある。
  - 操作: requirement-stage classify、design-stage approveを実行する。
  - 期待結果: provisionalからapprovedへ遷移し、Profile、Complexity、reason codes、unknown facts、source hashesが保存される。
  - 観測点: `assurance.json`、schema validation、classification matrix tests。

- E-AC-003: Lite safety
  - 前提: Lite適格条件のいずれかがfalseまたはunknown。
  - 操作: classificationを実行する。
  - 期待結果: Liteは選択されず、少なくともStandardになる。
  - 観測点: policy unit tests。

- E-AC-004: Fixed Skill / clean Git
  - 前提: Issue start、classification、Runbook compileを行う。
  - 操作: Git statusとgenerated stateを確認する。
  - 期待結果: `.agents/skills/**`、managed policy/template sourceにIssue切替由来の差分がなく、generated Runbookはignored pathに存在する。
  - 観測点: Git integration tests、provider/mirror inspection。

- E-AC-005: Profile-specific planning
  - 前提: Provisional Profileが異なる複数fixtureがある。
  - 操作: design / planをcompileする。
  - 期待結果: 必要sectionだけが生成され、不要Profileのworkflowは含まれず、既存substantive contentは保持される。
  - 観測点: golden files、idempotence tests、no-overwrite tests。

- E-AC-006: Step routing
  - 前提: docs-only、runtime behavior、migration、security-sensitiveの各Stepがある。
  - 操作: step Runbookをcompileする。
  - 期待結果: worker、reasoning、context、verification、reviewersがpolicyどおりに異なる。
  - 観測点: step assurance matrix tests。

- E-AC-007: Stale contract block
  - 前提: approved `assurance.json`後にrequirement / design / planがsubstantive変更された。
  - 操作: execution Runbookを取得する。
  - 期待結果: stale source bindingとしてblockされ、再classification / approvalがnext actionになる。
  - 観測点: hash invalidation tests。

- E-AC-008: Trusted review trigger
  - 前提: Open PR、expected head SHA、base SHA上のvalid review policyがある。
  - 操作: review triggerを実行する。
  - 期待結果: base SHA policyを使用したmultiline `@codex review` commentが1件投稿され、policy/hash/head evidenceが返る。
  - 観測点: fake GitHub contract tests、trigger JSON。

- E-AC-009: Untrusted policy rejection
  - 前提: head branchでpolicyを弱める変更がある。
  - 操作: review triggerを実行する。
  - 期待結果: head側policyは使用されず、base SHA policyが使用される。
  - 観測点: base/head fixture tests。

- E-AC-010: P2 noise suppression
  - 前提: P2 / P3 findingだけが返る。
  - 操作: PR triageを実行する。
  - 期待結果: defaultでno-action / follow-upとなり、修正・push・fresh reviewを開始しない。
  - 観測点: repair policy tests、review generation history。

- E-AC-011: P2 blocker promotion
  - 前提: Protected domainに属するP2とfailing regression testがある。
  - 操作: triageを実行する。
  - 期待結果: validated blockerへ昇格し、P1相当のrepair / re-reviewが要求される。
  - 観測点: policy engine tests、repair batch evidence。

- E-AC-012: Automation stalled
  - 前提: 同一findingが残る、blocker数が減らない、repairが循環する、または既定修正回数に達する。
  - 操作: repair loopを継続する。
  - 期待結果: merge-preparedにせずautomation-stalled / human gateへ遷移する。
  - 観測点: state-machine tests。

- E-AC-013: Legacy compatibility
  - 前提: `assurance.json`を持たない既存Issue。
  - 操作: planning / executionを開始する。
  - 期待結果: strict-legacy workflowが選択され、canonical artifactsを自動改変しない。
  - 観測点: legacy fixtures。

- E-AC-014: Efficiency evidence
  - 前提: 代表的なLite / Standard / Strict fixtureと過去workflow baselineがある。
  - 操作: agent invocation、Runbook size、review generation、wall-clock proxyを比較する。
  - 期待結果: Standard / Liteで不要なspecialist / reviewer起動とP2 repair loopが減り、required quality gatesは維持される。
  - 観測点: benchmark report、event metrics。

## スコープ

- 必須:
  - `spec-dock/scripts/spec_dock_runtime/` のdomain / application / infra / command / presentation拡張。
  - `spec-dock/system/assurance/` のpolicy / schema / preset。
  - `spec-dock/templates/assurance/` のfragment。
  - Issue `assurance.json` contract。
  - `.agents/skills/spec-dock-issue-planning` / `spec-dock-issue-execution` のfixed kernel化。
  - Provider-side sourceとdogfooding mirror。
  - Active context pack / generated Runbook。
  - `.github/codex/review-policy.md` bootstrap asset。
  - GitHub review trigger、observation、merge-preparer policy。
  - legacy compatibility、doctor、validate、tests、docs。
- 禁止:
  - Issue状態ごとのtracked Skill書換え。
  - Managed Skill pathへのdynamic symlink切替。
  - PR head上のreview policyを当該PR reviewに使用すること。
  - Trigger scriptへarbitrary body / endpoint / raw `gh` argumentを渡すこと。
  - Review専用P2 filterを`AGENTS.md`へ置くこと。
  - 回数上限到達をrisk acceptanceまたはmerge許可として扱うこと。
  - P2 comment zeroをmerge条件にすること。
  - Generated stateをcanonical sourceにすること。
  - Legacy Issueをsilentにadaptive workflowへ変換すること。
- 対象外:
  - `openai/codex-action`への本番移行。
  - 自動merge、auto-merge enablement、branch deletion。
  - モデルproviderを跨ぐreview ensembleの本格導入。
  - Product domain機能の変更。
  - GitHub以外のreview provider。
  - 既存Issueの全量backfill。

## 境界

- 常に行う:
  - Canonical contractとgenerated projectionを分離する。
  - Runtime commandはcurrent stateを機械判定し、modelに自由なworkflow選択を委ねない。
  - Required review / verificationはProfileとStep obligationsから導出する。
  - External reviewは追加sensor、deterministic CI / policy engineをmerge gateとして扱う。
  - Provider sourceを変更しdogfooding mirrorを検証する。
- 判断が必要:
  - Lite自動選択をいつdefaultで許可するか。
  - Repoごとのhard trigger拡張をどのconfig surfaceで許可するか。
  - Review policyの最大サイズとadditive focus allow-list。
  - Metricsの保持期間とreport投影粒度。
- 行わない:
  - ModelのconfidenceだけでProfileを下げない。
  - Review priority labelだけでprotected-domain riskを破棄しない。
  - Generated RunbookをGit管理しない。
  - Static Skillへ全Profile workflowを複製しない。

## 非機能要件

- 性能:
  - Normal `workflow status / next`はnetwork accessを必要としない。
  - Representative test repositoryでlocal classification / Runbook compileが2秒以内に完了することを目標とする。
  - Current Runbookは未選択Profileの本文を含まず、boundedなcontext surfaceである。
- 信頼性 / 一貫性:
  - 同じpolicy version、canonical inputs、repository stateからbyte-identical outputを生成する。
  - Generated fileはtemp write + atomic replaceで更新する。
  - Source hash mismatch、invalid schema、unknown hard triggerはfail-closedに扱う。
  - Compilerはsubstantive contentを上書きしない。
- セキュリティ:
  - Review policyはtrusted base SHAから取得する。
  - Reviewed PR contentをuntrusted inputとして扱う。
  - Secret、token、private reasoning、生credentialをevent / reportへ保存しない。
  - GitHub writeはfixed review comment endpointとdeterministic bodyに限定する。
- 互換性:
  - Windowsでsymlink権限を要求しない。
  - Existing strict workflowをcompatibility pathとして保持する。
  - Installer updateはproject-owned review policyを上書きしない。
- 運用:
  - Each Issueは独立してrollback、test、review可能なvertical capability sliceとする。
  - 一つのIssue / PRへruntime、artifact compiler、PR repair policyを全て混在させない。
  - Default switch前にshadow / opt-in dogfooding evidenceを得る。

## 依存 / 影響範囲

- 前提:
  - `epic-00158-agent-workflow-pdca-hardening`
- 影響するcomponent:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`
  - `src/spec_dock/assets/spec_dock/system/`
  - `src/spec_dock/assets/spec_dock/templates/`
  - `src/spec_dock/assets/install_root/.agents/skills/`
  - `.agents/skills/`
  - `spec-dock/scripts/spec_dock_runtime/`
  - `spec-dock/system/`
  - `spec-dock/templates/`
  - `.github/codex/`
  - tests / docs / installer ownership metadata
- 外部依存:
  - GitHub REST / GraphQLの既存fixed read/write surfaces。
  - GitHub Codex review behavior。
- 互換性:
  - Policy compilerが利用不可でも、legacy strict workflowを明示的に選択できる。
  - Existing PR observation JSON contractはversioned migrationを行う。
  - Policy変更PRでは当該PRのhead policyを使用せず、merge後から有効にする。

## 未確定事項

- Blocking question:
  - なし。Default案として、new Epic、Strict / Deep、7 Issue slice、Standard default、Lite opt-in、trusted base-SHA review policyを採用する。
- Non-blocking design questions:
  - Review policy maximum sizeの初期値。
  - Metrics retentionの初期値。
  - Lite automatic selectionをshadow期間後に有効化する具体的な閾値。
