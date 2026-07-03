---
種別: research
ID: "20260702t014409z-research"
タイトル: "Phase 3 Repo Context And Implementation Survey"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["epic-00270"]
関連:
  - "20260702t014409z-01"
authority: "synthesized"
derived_from:
  - "artifacts/20260702t014409z-01-phase3-v3-planning-pack-full-intake.md"
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/requirement.md"
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/design.md"
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/plan.md"
  - "src/spec_dock/assets/spec_dock/templates/initiative/{requirement,design,plan}.md"
  - "src/spec_dock/assets/spec_dock/templates/epic/{requirement,design,plan}.md"
  - "src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md"
  - "src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md"
  - "src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md"
  - "src/spec_dock/assets/spec_dock/docs/workflow_initiative.md"
  - "src/spec_dock/assets/spec_dock/docs/workflow_epic.md"
  - "src/spec_dock/assets/spec_dock/docs/phase_plan_epic.md"
reflected_to: []
---

# 20260702t014409z-research Phase 3 Repo Context And Implementation Survey

## 調査目的

V3 planning pack を `epic-00270` の canonical requirement/design/plan へ採用する前に、ZIP の全体像、現在の実装状態、ここまでの開発履歴、実装ギャップ、ユーザーへ確認すべき高影響判断を整理する。

## sources / 調査方法

- V3 ZIP の Markdown 24 ファイルを読み、raw intake artifact に全文移管した。
- `spec-dock-clarification` skill に従い、active docs、親 initiative docs、scope-local artifacts、provider-side templates、planning/execution skills、workflow docs、tests、git history を確認した。
- `./spec-dock/scripts/spec-dock active set epic-00270` で対象 Epic を active にした。
- `./spec-dock/scripts/spec-dock validate` は `nodes=172` で成功した。
- `git log --oneline --decorate --all --grep='artifact|template|planning|workflow|epic|initiative|spec-reviewer' -30` で直近履歴を確認した。

## facts / 観測できた事実

- 対象 Epic は `epic-00270 Upstream Planning Governance And Templates`。親は `init-local-00003 Architecture Maintenance and Hardening`。
- V3 ZIP は V2 を補完し、過去チャットなしでも Phase 3 の上流計画分析が復元できるように reference 8本を追加している。
- V3 の中核方針は「scope-layering / Initiative-Epic-Issue responsibility model / discovery adoption / Epic-to-Issue slicing は Epic-level design/plan で扱い、decision-only Issue にしない」。
- V3 の具体 Issue セットは6本: Initiative template redesign、Epic template redesign、planning skills/workflow docs、Epic execution handoff、smoke tests/template validation、final quality/manual tests/PR delivery。
- 親 initiative は open-ended architecture maintenance lane であり、source-of-truth、sync、naming、state boundary、dogfooding継続性の architecture concern を受け入れる設計になっている。
- 現在の Initiative templates は、目的/背景/成功指標/スコープ/境界/ステークホルダー/制約/リスク程度の汎用 scaffold で、V3 が要求する actor/stakeholder landscape、capability candidates、source-of-truth ownership、transition architecture、Epic handoff はまだ薄い。
- 現在の Epic templates は component/package/domain/contract/data/flow/state/failure/migration/test sections を持つが、V3 が要求する target capability/model envelope、lifecycle/state shared across Issues、design slice catalog、Issue handoff package、suggested Issue grade がまだ明示的ではない。
- `spec-dock-initiative-planning` と `spec-dock-epic-planning` skill は fresh `spec-reviewer` gate、decision-only container 回避、artifacts evidence、main-orchestrator canonical ownership、system-architect evidence-only を既に持つ。
- `spec-dock-epic-execution` は active Epic / active Issue / dependency state / one Issue at a time / PR merge-preparer handoff を既に持つが、V3 の Issue handoff package fields や final quality Issue との接続はより明示できる。
- `workflow_initiative.md` と `workflow_epic.md` は artifacts を新規 working artifact destination として扱い、legacy `discussions/` を preservation とする方針を既に持つ。
- 直近履歴では Phase 2 artifacts 移行が進んでいる: `feat(artifacts): artifactテンプレート基盤を追加`, `feat(artifacts)!: new artifact コマンドへ移行`, `feat(scaffold)!: 新規ノードをartifacts既定へ切り替え`, `feat(runtime): artifacts対応の検証と同期投影を追加`, `fix(delegated-authoring): 委任成果物の境界をartifactsへ移す`, `docs(workflow): artifacts向けのガイダンスに揃える`, `fix(artifacts): delegated artifactの状態判定を正規化`。
- Existing tests already contain artifact, workflow, delegated authoring, active, new artifact, validation, scaffold, and issue profile coverage. Phase 3 should add focused template/skill/workflow smoke checks rather than retesting all Issue grade behavior.

## inference / 推測

- この Epic の主要価値は新しい runtime command ではなく、既に完成した Issue grade/TDD surface と artifacts surface を、上流 Initiative/Epic planning へ接続すること。
- Provider-side template assets を先に変え、dogfooding mirror は sync/update impact として確認するのが既存 repo 方針と整合する。
- V3 references は canonical docs へそのまま貼るのではなく、Epic design/plan の章立て・用語・受け入れ条件・Issue slicing の根拠として採用するのがよい。
- 6 Issue は実装単位として妥当だが、canonical Epic docs の reviewer gate 前に execution-ready Issue として扱うと、V3 自身が禁止している decision-only / insufficient handoff 問題に戻る。

## unverified / 未検証事項

- `spec-reviewer` による `epic-00270` requirement/design/plan の fresh pass はまだ実行していない。
- V3 の6 Issue scaffold はまだ作成していない。
- Provider-side template update 後の `spec-dock update .` / dogfooding mirror impact はまだ未検証。
- `make lint`, `uv run pytest tests/unit`, `uv run pytest tests/cli_runtime`, full `uv run pytest`, `./spec-dock/scripts/spec-dock sync` はこの調査ターンでは未実行。
- GitHub issue `#270` の live body/state はこのターンでは未確認。

## question candidates / 質問候補

- pressure-test question として切り出すべき候補:
  - V3 の6 Issue セットを Epic plan の baseline として固定し、repo調査や reviewer findings による補正だけを許すか。それとも、canonical Epic requirement/design/plan の作成中に Issue 分割そのものを再設計する余地を残すか。
- 質問せずに解決できた候補:
  - 親 initiative は `init-local-00003` でよい。V3 と現 repo の initiative taxonomy が一致している。
  - V2 はこの具体化作業では採用しない。V3 raw intake を evidence として保存した。
  - 新規 working evidence の置き場所は `artifacts/`。legacy `discussions/` には置かない。

## terminology conflicts / 用語衝突

- V3 README / handoff はタイトルに `v2` と残っているが、ZIP root と追加 section は `v3 clean/final` を示す。作業上は V3 attachment を source とし、内包文書名の v2 は歴史的名前として扱う。
- `artifacts/*` は evidence / draft / discovery surface であり、canonical authority ではない。V3 references も artifact に移管しただけでは採用済みにはならない。
- `Epic execution` は Issue 実装を直接行うものではなく、ready Issue を一つずつ selection/routing する coordinator。V3 の final quality Issue と混同しない。

## edge cases / 具体シナリオ

- Edge case: Initiative/Epic templates に DDD/EDA sections を入れすぎる。
  - 影響: `spec-dock` が DDD-only tool に見え、一般的な docs/template workflow としての汎用性を損なう。
- Edge case: Epic plan に6 Issueを置くだけで design slice catalog / handoff package がない。
  - 影響: downstream Issue が親設計を再発見する必要があり、V3 の目的に反する。
- Edge case: final quality Issue が全作業の再設計を始める。
  - 影響: quality gate が実装 scope expansion になり、delivery readiness が曖昧になる。
- Edge case: raw V3 artifact から直接実装を始める。
  - 影響: canonical requirement/design/plan と report adoption evidence を飛ばしてしまう。

## implications / 判断への含意

- `requirement.md` は capability outcome、Phase 1/2 からの連続性、V3のscope/non-goal、E-RQ/E-AC、quality/manual delivery expectations を採用する必要がある。
- `design.md` は upstream abstraction model、discovery-to-canonical adoption、Initiative/Epic responsibility model、target template model、skill/workflow handoff modelを採用する必要がある。
- `plan.md` は6 Issueの順序、design slice to Issue mapping、suggested grade、dependency/order、Issue readiness criteria、final delivery gateを明示する必要がある。
- `report.md` は V3 raw intake、repo survey、user interview、今後の reviewer gates の採用判断を Evidence Adoption Ledger / Spec Authoring Gate に記録する必要がある。
- まずユーザー回答で6 Issue baseline adoption の方針を固定し、その後 canonical Epic docs へ採用するのが最小リスク。

## 反映先

- Planned: `epic-00270/requirement.md`
- Planned: `epic-00270/design.md`
- Planned: `epic-00270/plan.md`
- Planned: `epic-00270/report.md` Evidence Adoption Ledger / Spec Authoring Gate
