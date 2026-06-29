---
種別: 要件定義書（Epic）
ID: "epic-00224"
タイトル: "Dynamic Workflow Resource Allocation"
関連GitHub: ["#224"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
親: ["init-local-00003"]
---

# epic-00224 Dynamic Workflow Resource Allocation — 要件定義（何を、なぜ行うか）

## 変更履歴（Supersession / Amendment）

- 2026-06-29: 旧 `Trusted GitHub Codex review policy` 方針は変更済み。Review trigger instruction source は PR base SHA 上の `.github/codex/review-policy.md` ではなく、`20260623t074444z-adr Script-local Codex Review Instruction` により `github-pr-observation` script-local Markdown asset へ置換する。
- 2026-06-29: 旧 `review_completion_unknown` / quiet-window / elapsed-time による PR observation 終了方針は変更済み。Review completion は `20260628t154553z-adr PR Observation Explicit Review Completion` により current trigger boundary と expected head SHA に bind された Codex-authored completion artifact で判断する。
- 2026-06-29: 旧 `comment zero` / inline review thread zero を blocker zero とみなす暗黙前提は変更済み。`20260628t185812z-adr PR Review Body Blocker Ingestion` により selected pull request review body も blocker policy input として扱う。
- 2026-06-29: 旧 runtime-selected issue execution step / Step Assurance / Context Packet authority は変更済み。Issue execution は `20260629t003131z-adr Plan Centric Issue Execution Preflight` により `plan.md` を execution contract、`guidance issue-execution` を preflight validator とする。
- 2026-06-29: 旧 Issue-local `assurance.json` path は変更済み。Assurance Contract は `20260629t003132z-adr Hidden Assurance Contract Path` により `.assurance.json` を canonical metadata contract とする。

## 目的（Initiative との紐づき）

- Initiative 目標 / 指標:
  - `init-local-00003 Architecture Maintenance and Hardening` のうち、SpecDock の agent workflow を、品質を維持したまま token consumption と wall-clock time を削減できる構造へ移行する。
  - workflow、artifact、review、delivery の authority を chat memory や model の都度判断に依存させず、repository と runtime が検証可能な契約として保持する。
- この Epic が提供する能力:
  - Active Issue、authoring phase、Assurance Profile、current step、PR review state に応じた「現在必要な一つの Runbook」を runtime が機械生成する。
  - Issue / Step の risk と complexity に応じ、必要な agent、reasoning effort、context policy、verification、reviewer を選択する。
  - GitHub Codex review へ script-local review instruction を注入し、P0 / P1 を中心とする高価値 review を要求する。
  - P0 / P1 と機械的に検証された blocker だけを自動修正ループへ入れ、P2 / P3 による価値の低い review-push-review 反復を抑制する。
  - 既存 Issue を壊さず、新規 Issue から段階的に adaptive workflow へ移行できる。

## 背景・現状

- `epic-00158 Agent Workflow PDCA Hardening` により、skill / docs / templates / canonical artifact の責務境界と first-read workflow surface が整理された。
- 同 Epic は runtime gate、manual harness、regression enforcement を後続 PDCA work として残している。
- 現在の Issue workflow は高保証だが、軽量な Issue にも Strict 相当の planning / execution / review gate が適用されやすい。
- Requirement、design、plan の phase ごとに reviewer / specialist が直列実行され、各 implementation step でも worker、reviewer、commit gate が繰り返される。
- サブエージェントは reasoning effort の切替、context isolation、review independence に有効だが、不要な再調査と同一文書の再読が発生すると token と時間を浪費する。
- Skill が複数 workflow docs を参照するだけでは、agent が参照先を開かず mandatory workflow を落とす可能性がある。
- 反対に、Lite / Standard / Strict / Critical の完全な手順を一つの Skill に列挙すると、instruction noise と誤分岐が増える。
- GitHub Codex review は PR 品質向上に有効だが、P2 finding、修正、push、再 review の反復が delivery time の大きな割合を占める。
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
  - 現在の agent-facing operational handoff authority は `./spec-dock/scripts/spec-dock guidance <target>` の stdout に置く。
  - `.agent/runbooks/current-runbook.*` / `active/current-runbook.*` などの projection files は human/debug-only non-canonical projection であり、agent handoff authority ではない。

## ユースケース

### 正常系

- Active Issue がない状態で Issue Planning / Execution を開始すると、runtime は対象 Issue を `issue start` する手順だけを返す。
- Issue start 後、requirement が未完成なら requirement capture Runbook を返す。
- Requirement 完了後、runtime は risk facts から provisional Assurance Profile と Complexity Tier を計算する。
- Provisional classification に従って必要な design sections、architect、reasoning effort を選択する。
- Design 完了後、Assurance Contract を approved とし、plan / step obligations を compile する。
- Execution では current step に必要な worker、context inheritance、verification、reviewer だけを返す。
- Final delivery では `github-pr-observation` script-local Markdown instruction を読み、review target head SHA と instruction hash を含む deterministic `@codex review` comment を投稿する。
- Codex finding が P0 / P1 なら repair、verification、push、fresh review を行う。
- P2 / P3 だけなら原則 no-action / follow-up とし、そのためだけの修正・再 review を行わない。
- 全 blocker が閉じ、required CI と review coverage が成立したら merge-prepared とする。

### 例外 / 運用シナリオ

- Requirement / design / plan の source hash が Assurance Contract と一致しない場合、Runbook を stale として execution を block する。
- 実装中に public contract、migration、security/privacy、rollback difficulty が発見された場合、Assurance を上方 escalation する。
- Lite 適格条件に unknown が含まれる場合は Lite を authorize しない。
- Profile downgrade は自動実行せず、根拠と明示的 risk acceptance を要求する。
- Existing Issue に `assurance.json` がない場合、legacy Strict compatibility path で継続できる。
- Script-local review instruction が missing の場合、review trigger は instruction なしの deterministic `@codex review` comment を投稿し、metadata に fallback status を記録する。
- Script-local review instruction が present だが invalid / oversized / unreadable / non-UTF-8 の場合、review trigger は PR comment を投稿せず human gate / fail-closed とする。
- P2 finding が protected domain に関係し、failing regression test 等で再現された場合、validated blocker へ昇格する。
- 自動修正が停滞した場合、回数を理由に risk を受容せず `automation-stalled` / human gate へ移行する。

## エピック要件（Epic requirements）

- E-RQ-001: State-derived workflow entrypoint
  - Planning / Execution skill は現在状態を推測せず、runtime の `guidance <target>` が stdout に返す一つの guidance を実行する。
  - no-active、requirement capture、classification required、planning、execution、delivery、blocked を明確に区別する。

- E-RQ-002: Assurance Contract
  - 各 adaptive Issue は tracked `assurance.json` を持つ。
  - Profile、Complexity Tier、source binding、global obligations、step obligations、review policy、status を machine-readable に保存する。
  - Profile 名は preset であり、展開済み obligations を実行 authority とする。

- E-RQ-003: Deterministic classification
  - `lite / standard / strict / critical` を risk facts と hard trigger から決定する。
  - `routine / normal / complex / deep` を reasoning / specialist routing 用に別管理する。
  - Standard を新規 adaptive Issue の authoritative default とする。
  - Lite classification は shadow measurement 用の `lite_candidate` と、obligation reduction に使える `lite_authorized` を分離する。
  - Runtime は required Lite predicate が false または unknown、hard trigger present、source binding stale、required telemetry / policy evaluation unavailable の場合、Lite を authorize してはならない。
  - 初期 rollout では automatic Lite default を有効化しない。automatic Lite default は、別 accepted ADR、policy version bump、rollout Issue、telemetry gate による evidence-backed adoption を必要とする。

- E-RQ-004: Fixed Skill kernel
  - Issue 状態ごとに `.agents/skills/**` を差し替えない。
  - Skill は `./spec-dock/scripts/spec-dock guidance <target>` の実行、stdout guidance の遵守、blocked 時の停止だけを直接記述する。
  - mandatory path は別 Skill や複数 workflow docs の参照成功に依存しない。

- E-RQ-005: Compiled Runbook
  - runtime は current state / phase / profile / step に対応する完全な guidance を stdout に返し、必要に応じて同内容を Markdown / JSON projection として生成する。
  - Projection は `.agent/` と `active/` の generated state へ atomic に保存し、Git 差分を発生させない。
  - 未選択 Profile の手順を current Runbook へ混入させない。
  - Runbook compiler は `authorized_profile` だけを実行 authority として扱い、shadow の `lite_candidate` によって obligation を減らさない。

- E-RQ-006: Adaptive artifact composition
  - design / plan / report の必要 sections を policy fragment から合成する。
  - substantive user content を自動上書きしない。
  - escalation は必要 section の単調追加と downstream invalidation を行う。
  - downgrade による section 削除を自動実行しない。

- E-RQ-007: Step Assurance
  - 各 implementation step は change facts を持ち、issue-wide obligations との和集合から effective obligations を計算する。
  - worker role、reasoning effort、context policy、verification、reviewer、re-review 条件を compile する。
  - semantic batch を commit / review 単位とし、機械的な 1 行 1 step 分割を要求しない。

- E-RQ-008: Context policy
  - 実行系 agent は recent fork または bounded context packet を利用できる。
  - reviewer / consultant は clean-room evidence packet を利用し、author narrative や previous verdict へ不必要に anchor されない。
  - 子 agent の raw log を main へ転記せず、outcome、evidence ref、material decision、risk だけを返す。

- E-RQ-009: Script-local GitHub Codex review instruction
  - `.github/codex/review-policy.md` bootstrap asset は現行 authority として使用しない。
  - Review instruction は GitHub base branch / PR head ではなく `github-pr-observation` script-local Markdown から取得する。
  - trigger script は caller-provided arbitrary body を受け付けず、runtime が instruction と metadata から deterministic comment を合成する。
  - Review comment は instruction path、instruction hash、reviewed head SHA を記録する。

- E-RQ-010: Blocker-centric review closure
  - Valid P0 / P1 は blocker として修正または独立証拠による反証を要求する。
  - P2 / P3 は default non-blocking とし、自動修正対象にしない。
  - Protected domain かつ machine evidence がある P2 だけを validated blocker へ昇格する。
  - Comment zero ではなく verified blocker zero を終了条件とする。

- E-RQ-011: Re-review and stagnation
  - P0 / P1 / promoted blocker の code fix 後は fresh external review を要求する。
  - Non-material P2 fix だけでは新しい review trigger を投稿しない。
  - 修正回数上限は risk 受容ではなく automation-stalled への移行条件とする。
  - stale reviewed SHA の finding を current repair input に使わない。

- E-RQ-012: Compatibility and rollout
  - Existing Issue は strict-legacy として grandfather する。
  - New Issue から shadow classification、opt-in、Standard default の順で段階導入する。
  - Provider source / dogfooding mirror / installer / docs / tests を同期する。
  - rollback 時に legacy workflow へ戻せる。

- E-RQ-013: Observability
  - Agent invocation、reasoning、token、active time、test time、PR wait、review generation、finding disposition、push count を観測可能にする。
  - Generated raw event から human-readable report summary を投影できる。
  - Secret、private reasoning、raw credential を記録しない。

- E-RQ-014: Auto-Lite readiness
  - Epic 完了時点では automatic Lite default を有効化しない。
  - 将来の automatic Lite default に必要な safe predicates、shadow classification、telemetry gate、promotion 条件、rollback 条件を定義する。
  - `auto-lite-readiness report` は false positive candidates、escalation rate、P0/P1 escape、post-review blocker、wall-clock/token delta、missing metrics を確認できる。

- E-RQ-015: Tracked Agent Context Routing Policy
  - SpecDock は、sub-agent へ渡す context の種類と範囲を、Git 管理された machine-readable policy として管理する。
  - Context policy は Assurance Profile や reasoning effort とは独立した設計軸として扱う。
  - Context policy は少なくとも `recent_fork`、`bounded_packet`、`clean_room`、`minimal_packet` を表現できる。
  - Policy は agent role、step kind、change kind、Assurance Profile に応じて、context mode、fork turn count、include / exclude category、required canonical artifacts、required repository freshness checks、child agent から main agent へ返却可能な output category を定義できる。
  - Runtime は tracked policy を current Issue / current Step の Assurance Contract へ適用し、選択済み context contract を current Runbook へ展開する。
  - Agent 自身は Runbook が指定した context mode を独自に弱めたり、reviewer の clean-room 境界を解除したりしてはならない。

- E-RQ-016: Execution Context Affinity
  - Requirement、design、plan、approved decision など現在の目的遂行に必要な文脈を共有すべき実行系 agent には、`recent_fork` または `bounded_packet` を使用できる。
  - 実行系 agent は、親 agent が既に確定した目的、制約、許可された変更範囲、禁止事項、verification obligation を再調査せず利用できる。
  - Fork または packet による context 継承は、current HEAD、worktree state、対象 file の現行内容を再確認する義務を免除しない。
  - 同一 semantic batch 内では、source revision、goal、scope、risk、allowed paths が変化しない限り、同一 worker thread を継続利用できる。

- E-RQ-017: Independent Evaluation Context
  - `spec-reviewer`、`code-reviewer`、`qa-reviewer` は、author または implementer の会話履歴を継承しない `clean_room` context を使用する。
  - Reviewer には、author の推論過程ではなく、approved requirement、approved design、approved plan または step contract、base SHA、head SHA、immutable diff、relevant changed files and symbols、verification evidence、known environment limitations を渡す。
  - Reviewer へ author self-assessment、implementation transcript、private reasoning、previous reviewer verdict、review 結果を誘導する結論、rejected hypothesis の全履歴を渡してはならない。
  - Reviewer は必要な追加 file を独立して参照できるが、author narrative を authority として扱ってはならない。

- E-RQ-018: Independent Consultant Context
  - `consultant` および `deep-consultant` の first pass は、main agent の推奨案または他 agent の結論を含まない `clean_room` または `bounded_packet` で実行する。
  - First pass には decision question、objective、verified facts、constraints、evaluation criteria、unknowns だけを渡す。
  - 複数案の見解が衝突した場合に限り、second-stage arbitration として各案と反論を渡せる。
  - First pass と arbitration は別の context contract として記録する。

- E-RQ-019: Context Minimization And Main Context Protection
  - Child agent から main agent へ返却する情報は、原則として outcome、changed files、verification result、evidence reference、material decision request、remaining risk に限定する。
  - Raw shell transcript、full test log、stack trace 全体、読み込んだ全 file 一覧、failed hypothesis の全履歴、private reasoning を main agent context へ自動転記してはならない。
  - Raw evidence は必要に応じて artifact または generated event store へ保存し、main agent へは path、hash、要約だけを返す。

- E-RQ-020: Context Freshness And Invalidation
  - Context packet は canonical artifact hash、base SHA、head SHA、policy version、Assurance Contract hash へ bind する。
  - Requirement、design、plan / step contract の substantive change、branch / head SHA 変更、allowed scope 変更、new hard-risk 発見、Assurance escalation が発生した場合、既存 context packet または worker continuation を stale として扱う。
  - Stale context を使用して execution または review を続行してはならない。

- E-RQ-021: Context Policy Observability
  - 各 agent invocation について、role、reasoning effort、context mode、context policy version、context packet hash、source artifact hashes、fork turn count、included category、excluded category、returned evidence references を machine-readable evidence として記録する。
  - Private reasoning、secret、credential、raw token を記録してはならない。

## エピック受け入れ条件（Epic acceptance criteria）

- E-AC-001: No-active Runbook
  - 前提: Active Issue がない。
  - 操作: Issue Planning または Execution で `./spec-dock/scripts/spec-dock guidance issue-planning` または `issue-execution` を実行する。
  - 期待結果: `issue start <target>` または target 入力要求だけが next action として返り、authoring / implementation を開始しない。
  - 観測点: CLI JSON / Markdown、state-machine tests。

- E-AC-002: Provisional / approved classification
  - 前提: Active Issue の requirement に risk facts がある。
  - 操作: requirement-stage classify、design-stage approve を実行する。
  - 期待結果: provisional から approved へ遷移し、Profile、Complexity、reason codes、unknown facts、source hashes が保存される。
  - 観測点: `assurance.json`、schema validation、classification matrix tests。

- E-AC-003: Lite safety
  - 前提: Lite 適格条件のいずれかが false または unknown。
  - 操作: classification を実行する。
  - 期待結果: `lite_authorized` にならず、少なくとも Standard が authorized profile になる。
  - 観測点: policy unit tests、three-valued predicate tests。

- E-AC-004: Candidate / authorized separation
  - 前提: shadow classification で Lite 候補になる Issue がある。
  - 操作: Runbook compile、artifact composition、step routing を実行する。
  - 期待結果: `lite_candidate` は telemetry / report に記録されるが、explicit opt-in と evidence gate がない限り obligations は Standard 相当のまま減らない。
  - 観測点: Runbook JSON、event metrics、artifact golden tests。

- E-AC-005: Fixed Skill / clean Git
  - 前提: Issue start、classification、Runbook compile を行う。
  - 操作: Git status と generated state を確認する。
  - 期待結果: `.agents/skills/**`、managed policy/template source に Issue 切替由来の差分がなく、generated Runbook は ignored path に存在する。
  - 観測点: Git integration tests、provider/mirror inspection。

- E-AC-006: Profile-specific planning
  - 前提: Provisional Profile が異なる複数 fixture がある。
  - 操作: design / plan を compile する。
  - 期待結果: 必要 section だけが生成され、不要 Profile の workflow は含まれず、既存 substantive content は保持される。
  - 観測点: golden files、idempotence tests、no-overwrite tests。

- E-AC-007: Step routing
  - 前提: docs-only、runtime behavior、migration、security-sensitive の各 Step がある。
  - 操作: step Runbook を compile する。
  - 期待結果: worker、reasoning、context、verification、reviewers が policy どおりに異なる。
  - 観測点: step assurance matrix tests。

- E-AC-008: Stale contract block
  - 前提: approved `assurance.json` 後に requirement / design / plan が substantive 変更された。
  - 操作: execution Runbook を取得する。
  - 期待結果: stale source binding として block され、再 classification / approval が next action になる。
  - 観測点: hash invalidation tests。

- E-AC-009: Script-local review trigger
  - 前提: Open PR、expected head SHA、valid script-local review instruction がある。
  - 操作: review trigger を実行する。
  - 期待結果: script-local instruction を使用した multiline `@codex review` comment が 1 件投稿され、instruction/hash/head evidence が返る。
  - 観測点: fake GitHub contract tests、trigger JSON。

- E-AC-010: Remote policy independence
  - 前提: GitHub base branch / PR head に `.github/codex/review-policy.md` が存在する、または存在しない。
  - 操作: review trigger を実行する。
  - 期待結果: GitHub contents API で remote policy を読まず、script-local instruction または plain fallback trigger を使用する。
  - 観測点: fake GitHub call log、trigger JSON。

- E-AC-011: P2 noise suppression
  - 前提: P2 / P3 finding だけが返る。
  - 操作: PR triage を実行する。
  - 期待結果: default で no-action / follow-up となり、修正・push・fresh review を開始しない。
  - 観測点: repair policy tests、review generation history。

- E-AC-012: P2 blocker promotion
  - 前提: Protected domain に属する P2 と failing regression test がある。
  - 操作: triage を実行する。
  - 期待結果: validated blocker へ昇格し、P1 相当の repair / re-review が要求される。
  - 観測点: policy engine tests、repair batch evidence。

- E-AC-013: Automation stalled
  - 前提: 同一 finding が残る、blocker 数が減らない、repair が循環する、または既定修正回数に達する。
  - 操作: repair loop を継続する。
  - 期待結果: merge-prepared にせず automation-stalled / human gate へ遷移する。
  - 観測点: state-machine tests。

- E-AC-014: Legacy compatibility
  - 前提: `assurance.json` を持たない既存 Issue。
  - 操作: planning / execution を開始する。
  - 期待結果: strict-legacy workflow が選択され、canonical artifacts を自動改変しない。
  - 観測点: legacy fixtures。

- E-AC-015: Auto-Lite readiness without default enablement
  - 前提: shadow / opt-in telemetry が収集されている。
  - 操作: rollout readiness を確認する。
  - 期待結果: automatic Lite default は有効化されないが、future adoption に必要な predicates、telemetry gate、promotion 条件、rollback 条件が `auto-lite-readiness report` に残る。
  - 観測点: auto-lite-readiness report、event metrics、rollback runbook。

- E-AC-016: Efficiency evidence
  - 前提: 代表的な Lite / Standard / Strict fixture と過去 workflow baseline がある。
  - 操作: agent invocation、Runbook size、review generation、wall-clock proxy を比較する。
  - 期待結果: Standard / Lite で不要な specialist / reviewer 起動と P2 repair loop が減り、required quality gates は維持される。
  - 観測点: benchmark report、event metrics。

- E-AC-017: Role-specific context compilation
  - 前提: 同一 Issue 内に implementation step、code review、consultant decision の各 task がある。
  - 操作: 各 task の Runbook を compile する。
  - 期待結果: implementation worker には `recent_fork` または `bounded_packet`、code reviewer には `clean_room`、consultant first pass には main の推奨案を含まない独立 context が選択される。
  - 観測点: compiled Runbook JSON、context policy unit tests、golden context packet tests。

- E-AC-018: Reviewer independence
  - 前提: Main agent と dev-coder が実装を完了している。
  - 操作: code-reviewer 用 context packet を compile する。
  - 期待結果: approved specification、immutable diff、verification evidence は含まれ、author self-assessment、implementation transcript、previous reviewer verdict は含まれない。
  - 観測点: generated packet、inclusion / exclusion assertions。

- E-AC-019: Worker context reuse
  - 前提: 同一 semantic batch 内で goal、scope、source revisions、risk が変更されていない。
  - 操作: 次の worker action を開始する。
  - 期待結果: 既存 worker thread を継続利用でき、full repository reorientation を要求せず、current HEAD と worktree state の bounded revalidation は実行される。
  - 観測点: invocation history、repository freshness evidence、reorientation metrics。

- E-AC-020: Context invalidation
  - 前提: Context packet 生成後に design または allowed scope が substantive 変更された。
  - 操作: 既存 packet を用いて execution を開始する。
  - 期待結果: packet が stale として拒否され、再 compile が next action になる。
  - 観測点: hash mismatch test、workflow state transition。

- E-AC-021: Main context minimization
  - 前提: Child agent が複数 file の調査、test execution、失敗した仮説の検討を行った。
  - 操作: Child agent result を main agent へ返す。
  - 期待結果: main へ返るのは outcome、evidence refs、material decisions、remaining risks に限定され、raw logs と private reasoning は含まれない。
  - 観測点: return contract tests、generated event artifacts。

## スコープ

- 必須:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/` の domain / application / infra / command / presentation 拡張。
  - `src/spec_dock/assets/spec_dock/system/` の policy / schema / preset。
  - `src/spec_dock/assets/spec_dock/templates/` の assurance / workflow fragment。
  - Issue `assurance.json` contract。
  - `.agents/skills/spec-dock-issue-planning` / `spec-dock-issue-execution` の fixed kernel 化。
  - Provider-side source と dogfooding mirror。
  - Active context pack / generated Runbook。
  - `.github/codex/review-policy.md` bootstrap asset。
  - GitHub review trigger、observation、merge-preparer policy。
  - Tracked context routing policy / schema、generated context packet、role-specific return contract。
  - Legacy compatibility、doctor、validate、tests、docs。
  - Shadow / opt-in telemetry と `auto-lite-readiness report`。
- 禁止:
  - Issue 状態ごとの tracked Skill 書換え。
  - Managed Skill path への dynamic symlink 切替。
  - 初期 rollout で automatic Lite default を有効化すること。
  - `lite_candidate` だけで obligations を減らすこと。
  - PR head 上の review policy を当該 PR review に使用すること。
  - Trigger script へ arbitrary body / endpoint / raw `gh` argument を渡すこと。
  - Review 専用 P2 filter を `AGENTS.md` へ置くこと。
  - 回数上限到達を risk acceptance または merge 許可として扱うこと。
  - P2 comment zero を merge 条件にすること。
  - Generated state を canonical source にすること。
  - Reviewer / consultant first pass へ author narrative や previous verdict を渡すこと。
  - Child agent の raw logs / private reasoning を main context へ自動転記すること。
  - Legacy Issue を silent に adaptive workflow へ変換すること。
- 対象外:
  - `openai/codex-action` への本番移行。
  - Automatic Lite default の本番有効化。
  - 自動 merge、auto-merge enablement、branch deletion。
  - モデル provider を跨ぐ review ensemble の本格導入。
  - Product domain 機能の変更。
  - GitHub 以外の review provider。
  - 既存 Issue の全量 backfill。

## 境界

- 常に行う:
  - Canonical contract と generated projection を分離する。
  - Runtime command は current state を機械判定し、model に自由な workflow 選択を委ねない。
  - Required review / verification は Profile と Step obligations から導出する。
  - External review は追加 sensor、deterministic CI / policy engine を merge gate として扱う。
  - Provider source を変更し dogfooding mirror を検証する。
  - Lite は `lite_candidate` と `lite_authorized` を分離し、Runbook は authorized profile だけを実行 authority とする。
- 判断が必要:
  - Repo ごとの hard trigger 拡張をどの config surface で許可するか。
  - Review policy の最大サイズと additive focus allow-list。
  - Metrics の保持期間と report 投影粒度。
  - Automatic Lite default の将来 rollout threshold / telemetry threshold / rollback threshold。採用 surface は別 accepted ADR、policy version bump、rollout Issue、telemetry gate の 4 点を必須とすることで固定済み。
- 行わない:
  - Model の confidence だけで Profile を下げない。
  - Review priority label だけで protected-domain risk を破棄しない。
  - Generated Runbook を Git 管理しない。
  - Static Skill へ全 Profile workflow を複製しない。
  - Escalation を初期分類の安全性の代替として扱わない。

## 非機能要件

- 性能:
  - Normal `guidance <target>` は network access を必要としない。
  - Representative test repository で local classification / Runbook compile が 2 秒以内に完了することを目標とする。
  - Current Runbook は未選択 Profile の本文を含まず、bounded な context surface である。
- 信頼性 / 一貫性:
  - 同じ policy version、canonical inputs、repository state から byte-identical output を生成する。
  - Generated file は temp write + atomic replace で更新する。
  - Source hash mismatch、invalid schema、unknown hard trigger は fail-closed に扱う。
  - Compiler は substantive content を上書きしない。
  - Lite eligibility は `true / false / unknown` の three-valued policy result として扱う。
- セキュリティ:
  - 変更済み: Review policy を trusted base SHA から取得する旧方針は廃止し、script-local review instruction を使用する。
  - Reviewed PR content を untrusted input として扱う。
  - Secret、token、private reasoning、生 credential を event / report へ保存しない。
  - GitHub write は fixed review comment endpoint と deterministic body に限定する。
- 互換性:
  - Windows で symlink 権限を要求しない。
  - Existing strict workflow を compatibility path として保持する。
  - Installer update は project-owned review policy を上書きしない。
- 運用:
  - Each Issue は独立して rollback、test、review 可能な vertical capability slice とする。
  - 一つの Issue / PR へ runtime、artifact compiler、PR repair policy を全て混在させない。
  - Default switch 前に shadow / opt-in dogfooding evidence を得る。

## 依存 / 影響範囲

- 前提:
  - `epic-00158-agent-workflow-pdca-hardening`
- 影響する component:
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
  - GitHub REST / GraphQL の既存 fixed read/write surfaces。
  - GitHub Codex review behavior。
- 互換性:
  - Policy compiler が利用不可でも、legacy strict workflow を明示的に選択できる。
  - Existing PR observation JSON contract は versioned migration を行う。
  - 変更済み: Policy 変更 PR は merge 後から有効にするという旧方針は廃止し、現在の checkout にある script-local instruction 変更を同一 PR で dogfooding できるようにする。

## 未確定事項

- Blocking question:
  - なし。
  - Default 案として、new Epic、Strict / Deep、複数 Issue slice、Standard default、Lite opt-in / evidence-gated、candidate / authorized separation を採用する。
  - 変更済み: 旧 default 案に含まれていた trusted base-SHA review policy は、script-local review instruction と explicit Codex artifact completion へ置換済み。
- Non-blocking design questions:
  - Review policy maximum size の初期値。
  - Metrics retention の初期値。
  - Repo ごとの hard trigger 拡張 surface。
  - Automatic Lite default を将来有効化する際の policy adoption surface。
