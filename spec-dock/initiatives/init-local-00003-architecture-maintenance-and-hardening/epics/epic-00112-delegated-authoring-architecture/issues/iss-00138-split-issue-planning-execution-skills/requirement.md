---
種別: 要件定義書（Issue）
ID: "iss-00138"
タイトル: "Split Issue Planning and Execution Skills"
関連GitHub: ["#138"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-05-29"
親: ["epic-00112", "init-local-00003"]
---

# iss-00138 Split Issue Planning and Execution Skills — 要件定義（何を、なぜ行うか）

## 目的
- Issue workflow の入口を、要件・設計・計画を作成する planning と、承認済み計画を実装する execution に分ける。
- `spec-dock-issue-planning` を Initiative / Epic planning skill と同じ抽象度の leaf skill として追加し、既存の `workflow_spec_authoring.md`、`workflow_clarification.md`、delegated draft rules を保ったまま Issue planning の導線を明確にする。
- `spec-dock-issue-execution` は実装・検証・`report.md` 更新・PR delivery / issue finish handoff に集中させ、未解決の requirement / design / plan gap は planning / clarification へ戻す。

## 背景・現状
- 現状の挙動:
  - `spec-dock-initiative-planning` と `spec-dock-epic-planning` は requirement / design / plan planning 用の leaf skill として存在する。
  - Issue には planning 専用 skill がなく、hub skill は `spec-dock-issue-execution` を Issue-level entrypoint として案内している。
  - `workflow_spec_authoring.md` は Initiative / Epic / Issue 共通で requirement / design / plan authoring と reviewer gate を定義している。
  - `workflow_issue.md` は active issue execution、TDD step、reviewer gate、`report.md` evidence、PR delivery、`issue finish` を定義しており、同時に Issue spec authoring の入口も持つ。
- 現状の課題:
  - Initiative / Epic は planning skill、Issue は execution skill だけという構成になっており、scope 間の抽象度が揃っていない。
  - Issue の要件・設計・計画を深い clarification と組み合わせて作る入口が、skill routing 上は execution と混ざって見える。
  - `spec-dock-issue-execution` を指定したとき、未完成の requirement / design / plan を実装で補ってよいという誤解を避ける導線が弱い。
  - planning と execution を同時指定した場合の sequencing が明確でないと、spec reviewer gate や handoff readiness を飛ばす誤解が起きる。
- 観測点:
  - Skill asset:
    - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
    - `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`
    - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md`
    - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`
    - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md`
  - Docs:
    - `src/spec_dock/assets/spec_dock/docs/README.md`
    - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
    - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
    - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
  - Tests:
    - `tests/test_init_update.py`
    - `tests/cli_runtime/test_wrappers.py`
- 情報源:
  - `spec-dock/active/issue/discussions/20260529t000926z-disc-issue-planning-execution-skill-split-scope-memo.md`
  - `spec-dock/active/issue/discussions/20260529t012153z-01-research-issue-planning-execution-split-source-grounding.md`
  - `spec-dock/active/issue/discussions/20260529t012153z-interview-issue-planning-skill-authority-boundary.md`

## 対象ユーザー / 利用シナリオ
- 主な利用者:
  - spec-dock を使って Issue の requirement / design / plan を作成し、その後に実装へ進める main orchestrator。
  - Issue planning 中に `spec-dock-clarification`、`system-architect`、`implementation-planner` を組み合わせる agent。
  - 承認済み `plan.md` をもとに実装を進める execution agent。
- 代表シナリオ:
  - ユーザーが `$spec-dock-issue-planning` と `$spec-dock-clarification` を指定し、discussion memo から Issue の `requirement.md` を作成する。
  - planning phase で、設計 draft は `system-architect` が `discussions/` に作成し、main orchestrator が正式な `design.md` へ統合する。
  - planning phase で、実装計画 draft は `implementation-planner` が `discussions/` に作成し、main orchestrator が正式な `plan.md` へ統合する。
  - `plan.md` が reviewer gate を通過した後、別途 `$spec-dock-issue-execution` で実装・検証・report 更新へ進む。
  - planning と execution の両方が指定された場合も、planning artifacts と reviewer gate が整ってから execution に handoff する。

## スコープ
- 必須:
  - Provider-side install asset に `spec-dock-issue-planning` skill を追加する。
  - `spec-dock-issue-planning` は、Issue の `requirement.md` / `design.md` / `plan.md` 作成・改善・review readiness を扱う leaf skill として説明する。
  - `spec-dock-issue-planning` は `workflow_spec_authoring.md`、`workflow_clarification.md`、`workflow_issue.md`、`phase_plan_issue.md` を正本として参照する。
  - `spec-dock-issue-planning` は canonical docs の最終 ownership が main orchestrator にあることを明記する。
  - `spec-dock-issue-planning` は、設計 draft は `system-architect`、計画 draft は `implementation-planner` を使えるが、draft は既存 delegated draft rules に従い、main orchestrator が正式 docs へ統合することを明記する。
  - `spec-dock-issue-execution` は、承認済み requirement / design / plan と executable `plan.md` を前提にした execution skill として境界を明確にする。
  - `spec-dock-issue-execution` は、未解決の requirement / design / plan gap を実装で補わず、planning / clarification へ戻す stop condition を明記する。
  - `spec-driven-tdd-workflow` の routing に Issue planning / Issue execution の分離を反映する。
  - Shipped docs の skill 一覧または workflow references が、Issue planning / Issue execution の分離を示す。
  - Provider-side asset と dogfooding workspace の parity を確認できるようにする。
  - 新規 skill asset と routing docs の存在・内容を既存テストまたは追加テストで検出できるようにする。
- 禁止:
  - `spec-dock-issue-planning` に新しい canonical direct authoring authority を与えない。
  - `spec-dock-issue-planning` を `system-architect` / `implementation-planner` の代替にしない。
  - delegated draft を fresh `spec-reviewer` pass、phase promotion、implementation readiness の代替にしない。
  - planning + execution の同時指定を、reviewer gate や handoff readiness を飛ばす自動実装許可として扱わない。
  - `workflow_spec_authoring.md` と `workflow_issue.md` の既存 gate semantics を大きく変更しない。
- 対象外:
  - Permission Profile / sub-agent callability の追加実装。
  - canonical docs への delegated direct write 解禁。
  - planning から execution までの完全自動化。
  - `.github/agents` / Copilot agent support。
  - GitHub issue lifecycle command の再設計。
  - `workflow_issue.md` の completion policy / PR delivery policy の全面再設計。

## 境界
- 常に行う:
  - Issue planning は `workflow_spec_authoring.md` の phase promotion gate を守る。
  - 重要な曖昧さは `workflow_clarification.md` に従って source-grounded read と一問一答で解消する。
  - Canonical `requirement.md` / `design.md` / `plan.md` / `report.md` は main orchestrator が正式に統合する。
  - `system-architect` / `implementation-planner` の draft は既存 delegated draft evidence として扱う。
  - Execution は approved / reviewer-pass 済み planning artifacts を前提にする。
- 判断が必要:
  - `workflow_issue.md` の対応 leaf skill 表記を `spec-dock-issue-planning` と `spec-dock-issue-execution` の両方にするか、planning 側は `workflow_spec_authoring.md` / hub skill に寄せるか。
  - Dogfooding `.agents/skills` は実装中に直接更新するか、provider-side update と parity verification で反映するか。
- 行わない:
  - Requirement ownership を専門 author に移さない。
  - Final approval / phase promotion を専門 author や child reviewer に移さない。
  - Implementation work を planning skill に含めない。

## 非交渉制約
- Provider-side source of truth は `src/spec_dock/assets/install_root/` と `src/spec_dock/assets/spec_dock/` に置く。
- Dogfooding workspace は validation / parity surface として扱い、実装 source of truth にしない。
- Existing `workflow_spec_authoring.md` の fresh `spec-reviewer` pass requirement を維持する。
- Existing delegated draft rules を維持し、draft evidence は canonical authority ではない。
- `spec-dock-issue-execution` は unresolved spec gap を実装仮定で吸収してはならない。

## 前提
- `spec-dock-clarification` は first-class workflow として存在し、source-grounded read と formal interview artifact の扱いを定義済みである。
- `system-architect` と `implementation-planner` は scope-local `discussions/` への delegated draft evidence を作る既存 role skill として存在する。
- `workflow_spec_authoring.md` は Initiative / Epic / Issue 共通の requirement / design / plan authoring の正本である。
- `workflow_issue.md` は Issue execution / report / reviewer / completion policy の正本である。

## 受け入れ条件
- AC-001: Issue planning skill が追加される
  - アクター:
    - spec-dock を導入した agent。
  - 前提:
    - Provider-side install assets を確認できる。
  - 操作:
    - `.agents/skills/spec-dock-issue-planning/SKILL.md` を確認する。
  - 期待結果:
    - Skill が存在し、Issue の requirement / design / plan planning を担当する leaf skill として説明されている。
    - Skill は `workflow_spec_authoring.md`、`workflow_clarification.md`、`workflow_issue.md`、`phase_plan_issue.md` を参照する。
  - 観測点:
    - provider-side asset。
    - init/update generated asset。
    - dogfooding `.agents/skills` parity。
- AC-002: Planning skill は既存 authority boundary を保つ
  - アクター:
    - main orchestrator。
  - 前提:
    - `spec-dock-issue-planning` skill text を読む。
  - 操作:
    - Canonical docs / delegated draft / reviewer gate に関する記述を確認する。
  - 期待結果:
    - Canonical docs の正式作成・統合・promotion は main orchestrator の責務として説明されている。
    - `system-architect` と `implementation-planner` の draft は既存 delegated draft rules に従う補助 evidence として説明されている。
    - Draft は reviewer pass、phase promotion、implementation readiness の代替ではない。
  - 観測点:
    - skill text。
    - hub routing text。
- AC-003: Execution skill は implementation boundary を明確にする
  - アクター:
    - execution agent。
  - 前提:
    - `spec-dock-issue-execution` skill text を読む。
  - 操作:
    - skill の前提と stop condition を確認する。
  - 期待結果:
    - Execution は approved / reviewer-pass 済み requirement / design / plan と executable `plan.md` を前提にする。
    - 未解決 specification gap がある場合は planning / clarification へ戻す。
    - Requirement / design / plan 作成そのものは planning skill / spec authoring workflow 側へ分離されている。
  - 観測点:
    - skill text。
    - workflow docs references。
- AC-004: Hub skill が Issue planning / execution を正しく route する
  - アクター:
    - spec-driven workflow を起動する agent。
  - 前提:
    - `spec-driven-tdd-workflow` skill text を読む。
  - 操作:
    - leaf skill routing を確認する。
  - 期待結果:
    - Issue planning は `spec-dock-issue-planning` へ route される。
    - Issue execution は `spec-dock-issue-execution` へ route される。
    - `spec-dock-clarification` は planning 前後の source-grounded clarification として案内される。
    - planning + execution 同時指定時は planning gate pass / handoff readiness 後に execution へ進む sequencing が示される。
  - 観測点:
    - hub skill text。
- AC-005: Shipped docs と tests が新しい skill split を検出する
  - アクター:
    - maintainer / test suite。
  - 前提:
    - provider-side docs / tests を確認できる。
  - 操作:
    - skill 一覧、managed asset mapping、bundled routing contract、wrapper / init-update tests を確認または実行する。
  - 期待結果:
    - `spec-dock-issue-planning` が shipped skill list と managed asset expectations に含まれる。
    - `spec-dock-issue-execution` だけが Issue entrypoint として固定される古い期待が更新されている。
    - 新規 skill が init/update output と dogfooding parity で確認できる。
  - 観測点:
    - `tests/test_init_update.py`
    - `tests/cli_runtime/test_wrappers.py`
    - `spec-dock validate`
- AC-006: Existing workflow semantics は維持される
  - アクター:
    - reviewer。
  - 前提:
    - skill / docs / tests の diff を確認できる。
  - 操作:
    - `workflow_spec_authoring.md`、`workflow_issue.md`、delegated draft rules との整合を見る。
  - 期待結果:
    - Fresh `spec-reviewer` pass requirement、main orchestrator ownership、delegated draft evidence boundary、execution gap stop condition が維持されている。
    - この issue で Permission Profile / direct canonical authoring / full automation を導入していない。
  - 観測点:
    - docs diff。
    - requirement / design / plan traceability。

## 例外・エッジケース
- EC-001: `$spec-dock-issue-execution` だけが指定され、Issue docs が template または gap あり
  - 条件:
    - Active issue の `requirement.md` / `design.md` / `plan.md` が implementation-ready ではない。
  - 期待:
    - Execution は開始せず、planning / clarification へ戻す。
  - 観測点:
    - `spec-dock-issue-execution` skill の stop condition。
- EC-002: `$spec-dock-issue-planning` と `$spec-dock-issue-execution` が同時指定される
  - 条件:
    - ユーザーが簡単な要件から planning と execution をまとめて進めたい。
  - 期待:
    - Planning artifacts を作成し、必要な reviewer gate / handoff readiness を満たした後に execution へ進む。Gate を飛ばさない。
  - 観測点:
    - hub skill routing。
    - planning skill guidance。
- EC-003: `system-architect` / `implementation-planner` draft が作られる
  - 条件:
    - Issue planning 中に設計または計画 draft を委任する。
  - 期待:
    - Draft は scope-local `discussions/` evidence として扱われ、main orchestrator が採用判断を `report.md` に残して正式 docs へ統合する。
  - 観測点:
    - `workflow_spec_authoring.md` delegated draft rules。
    - `report.md` Evidence Adoption Ledger。
- EC-004: 新規 skill asset が provider-side にだけ存在する
  - 条件:
    - Dogfooding workspace または init/update output に `spec-dock-issue-planning` が反映されていない。
  - 期待:
    - Parity verification または tests が drift を検出する。
  - 観測点:
    - init/update tests。
    - dogfooding `.agents/skills`。

## 入力→出力例
- EX-001:
  - 入力:
    - User asks: `$spec-dock-issue-planning` でこの issue の requirement / design / plan を作成したい。
  - 出力:
    - Agent reads active docs / parent docs / discussions, uses `workflow_clarification.md` when needed, writes canonical docs as main orchestrator, records adoption evidence in `report.md`, and does not start implementation.
- EX-002:
  - 入力:
    - User asks: `$spec-dock-issue-execution` で実装して。
  - 出力:
    - Agent verifies `plan.md` readiness, executes behavior-slice steps, records observed evidence in `report.md`, and returns to planning / clarification if a spec gap is found.

## 用語（ドメイン語彙）
- TERM-001: `spec-dock-issue-planning`
  - Issue-level requirement / design / plan authoring entrypoint skill。既存 authoring workflow を案内する leaf skill であり、新しい canonical direct authoring authority ではない。
- TERM-002: `spec-dock-issue-execution`
  - Approved planning artifacts を前提に、implementation、verification、report evidence、delivery handoff を扱う leaf skill。
- TERM-003: delegated draft evidence
  - `system-architect` や `implementation-planner` が scope-local `discussions/` に作る draft / analysis。Canonical authority ではなく、main orchestrator の採用判断と reviewer gate が必要。
- TERM-004: handoff readiness
  - Requirement / design / plan が reviewer gate と必要な report evidence を満たし、execution skill が実装を開始できる状態。

## 未確定事項
- Q-001:
  - 質問:
    - `workflow_issue.md` の対応 leaf skill 表記を planning / execution の両方にするか、planning は `workflow_spec_authoring.md` / hub skill のみで案内するか。
  - 推奨案:
    - design phase で docs impact と routing consistency を見て決める。
  - 影響範囲:
    - docs references、tests、hub skill。
- Q-002:
  - 質問:
    - Dogfooding `.agents/skills` 側を実装中に直接更新するか、provider-side update / parity verification で反映するか。
  - 推奨案:
    - provider-first を維持し、dogfooding parity は update / inspection / tests で確認する。
  - 影響範囲:
    - dogfooding workspace diff、verification command、report evidence。
