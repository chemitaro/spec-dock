---
種別: 要件定義書（Issue）
ID: "iss-00102"
タイトル: "Agentic TDD plan step contract"
関連GitHub: ["#102"]
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-05-20"
親: ["epic-00067", "init-local-00003"]
---

# iss-00102 Agentic TDD plan step contract — 要件定義（WHAT / WHY）

## 目的
- Issue 実装計画書と Issue 実行 workflow を、Agentic TDD に適した「計画・実装・検証・レビューの契約」として再整理する。
- 生成される Issue `plan.md` 自体を、実装エージェントが上から順に実行できる executable Agentic TDD workflow contract にする。
- `1〜3件程度` のテスト件数目安に依存せず、risk-calibrated test obligation coverage、Red/Green evidence、実装中に発見したテストの記録、plan amendment で品質を担保する。
- 追記を重ねて肥大化した template / workflow / skill / prompt / agent config の正本分離と重複削減を行い、エージェントが迷わず実行できる状態にする。

## 背景・現状
- 現状の挙動:
  - Issue 実行 workflow には `Agent-Native TDD` / `Spec-Locked Micro-Batch TDD`、step-local `具体テストケース一覧`、pre-implementation evidence、review gate、commit gate などの概念がある。
  - Issue plan template と phase plan playbook には、通常 Issue は step / behavior slice ごとに `1〜3件程度` の検証契約を書く、という目安がある。
  - `workflow_issue.md`、`phase_plan_issue.md`、`docs/authoring/issue-plan.md`、`templates/issue/plan.md`、`templates/issue/report.md`、`execute-issue.md`、`spec-dock-issue-execution/SKILL.md`、agent config が、近い契約を少しずつ重複して説明している。
  - plan template は scaffold を超えて、用語、table、gate、delegation、test bundle、docs-only/no-op、report 更新方針まで広く含んでいる。
- 現状の課題:
  - Agentic TDD の手順を docs / policy に説明しても、実装エージェントが実際に読む `plan.md` が実行可能な workflow contract になっていなければ、Red-Green-Refactor は再現よく実行されない。
  - `1〜3件程度` は、エージェントにとって上限または十分条件のように読まれやすく、risk-based coverage より件数ヒューリスティックを優先させる危険がある。
  - 「計画段階で固定する test obligation」「step 開始前に固定する concrete red / characterization seeds」「実装中に発見して report に残す discovered tests」「plan amendment が必要な仕様変更」の境界が十分に明示されていない。
  - `Spec-Locked Closure Index`、`test bundle`、`具体テストケース一覧`、`step closure contract`、`Closure Coverage`、`Closure Delta` など役割が近い用語が多く、計画作成者と実装エージェントの認知負荷を上げている。
  - docs-only / approved-no-op の代替検証や report draft update が concrete test case 欄に混在し、テスト契約と実行 evidence の責務境界が曖昧になっている。
  - `execute-issue.md` / skill / agent config が、最新の Agentic TDD 契約と完全には同期しておらず、dev-coder の “minimal necessary tests” が弱い plan と組み合わさるとテスト不足を誘発しうる。
  - 単純に説明を追加すると、既存の重複と drift が悪化する。
- 再現手順:
  1. `src/spec_dock/assets/spec_dock/templates/issue/plan.md` と `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md` の test guidance を読む。
  2. `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`、`src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`、`src/spec_dock/assets/install_root/.codex/prompts/execute-issue.md`、`src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`、agent config の実行契約を比較する。
  3. Issue plan 作成者または実装エージェントの視点で、どの文書が test obligation、concrete tests、execution gate、reviewer gate、report evidence の正本かを判断する。
- 観測点:
  - docs/templates: provider-side scaffold docs と templates の文言、重複、用語境界。
  - installed agent assets: prompt / skill / agent config の handoff、input/output、reviewer gate 指示。
  - dogfooding workspace: `spec-dock/` 側の mirror と active issue docs。
  - tests: scaffold / installed asset の内容を検証する structural assertions。
- 情報源:
  - この要件定義書が正本であり、discussion / scratch は検討材料として扱う。古い discussion と要件が衝突する場合は、この要件定義書を優先する。
  - `spec-dock/active/issue/discussions/20260520t081426z-disc-plan-as-executable-agentic-tdd-workflow-contract.md`
  - `spec-dock/active/issue/discussions/20260520t074027z-disc-agentic-tdd-cycle-and-plan-step-contract-analysis.md`
  - `spec-dock/active/issue/discussions/20260520t075709z-disc-current-workflow-and-plan-template-remediation-analysis.md`
  - `spec-dock/active/issue/discussions/20260520t075311z-scratch-current-plan-workflow-audit-notes.md`
  - `src/spec_dock/assets/spec_dock/templates/issue/plan.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`
  - `src/spec_dock/assets/install_root/.codex/prompts/execute-issue.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `src/spec_dock/assets/install_root/.codex/agents/*.toml`

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - Issue plan を作成・レビューする人間。
  - Issue plan に従って実装する main orchestrator / dev-coder / doc-writer / utility-worker。
  - code-reviewer / qa-reviewer / spec-reviewer などの reviewer agent。
  - spec-dock を導入した consumer repo で同じ scaffold / workflow / skill を使う利用者。
- 代表シナリオ:
  - 新規 Issue の plan を作成するとき、テスト件数の目安ではなく、AC、changed contract、negative/error path、regression、invariant、manual/integration risk に基づいて test obligation を固定できる。
  - 実装エージェントが `plan.md` の step を順に辿るだけで、behavior goal、Red evidence、Green verification、Refactor / cleanup、closure evidence、review gate、commit boundary を確認しながら作業できる。
  - 実装 step に入る前に、step-local な concrete red / characterization seeds と expected red evidence を確認し、その step の Red-Green-Refactor / review / commit boundary を明確にできる。
  - 実装中に新しい bug class や仕様差分を発見したとき、report に discovered tests と closure delta を残すべきか、plan amendment で契約を更新すべきかを判断できる。
  - docs-only / template-only / skill-text-only の step では、code test と混同せず inspection / structural assertion / spec-review evidence で closure できる。

## スコープ
- 必須:
  - generated Issue `plan.md` を、単なる作業一覧や外部 workflow への参照ではなく、実装エージェント向けの executable Agentic TDD workflow contract として構造化する。
  - `1〜3件程度` のテスト件数目安を、Issue plan / phase plan の規範文から削除または非規範化し、risk-calibrated test obligation coverage へ置換する。
  - plan step / behavior slice / Agentic TDD cycle / review scope / commit boundary の関係を定義する。
  - 各 implementation step が、behavior goal、test obligation、Red evidence または正当な代替、implementation scope、Green verification、Refactor / cleanup、closure evidence、amendment trigger を表現できる schema を定義する。
  - test obligation matrix、step-local concrete red / characterization seeds、discovered tests、plan amendment rules、report evidence の責務境界を定義する。
  - `workflow_issue.md`、`docs/authoring/issue-plan.md`、`phase_plan_issue.md`、`templates/issue/plan.md`、`templates/issue/report.md`、prompt、skill、agent config の所有責務を整理する。
  - template と prompt / skill から重複説明や準仕様書化した長文を減らし、正本文書への routing を明確にする。
  - docs-only / approved-no-op / inspect-only / manual-required の verification を concrete test case と混同しない形へ整理する。
  - provider-side source と dogfooding mirror の影響を確認する。
  - scaffold / installed asset の重要文言や構造が維持されるよう、必要な regression / structural tests を追加・更新する。
- 禁止:
  - Agentic TDD の品質改善を、単なる説明追加だけで済ませない。
  - `plan.md` を従来型の作業一覧のままにし、実行規律を workflow docs / prompt / skill だけへ押し込まない。
  - テスト十分性を raw 件数だけで判定する契約を残さない。
  - `workflow_issue.md` と plan authoring docs と template が同じ policy を再定義し続ける状態を温存しない。
  - `spec-dock/` dogfooding workspace だけを変更し、provider-side source を更新しない。
- 対象外:
  - spec-dock runtime の新しい lint command や `validate --strict-docs` の本格実装。
  - Plan QA Gate の mandatory runtime validation 化。今回の Issue では plan review / reviewer config / final QA gate の観点強化までを対象にする。
  - GitHub issue / PR workflow 全体の再設計。
  - 既存 Issue docs 全件の migration。
  - Agent runtime や model selection policy の変更。
  - TDD 一般論の長文解説追加。

## 境界
- 常に行う:
  - provider-side source を正として変更し、必要に応じて dogfooding mirror の整合を確認する。
  - 文書追加より先に、正本分離、重複削減、用語整理、template の薄さを優先する。
  - Issue execution と completion policy は `workflow_issue.md`、plan authoring contract は `docs/authoring/issue-plan.md`、template は最小 scaffold という境界を保つ。
  - 変更後の workflow が、実装 agent と reviewer agent の input/output に落ちることを確認する。
- 判断が必要:
  - `hard cutover evidence contract` をどの reference doc へ分離するか。
- 行わない:
  - 既存の active / historical issue docs を一括変換しない。
  - 実装コードの挙動変更を主目的にしない。
  - テストケースの完全な issue-wide inventory を plan に義務化しない。
  - Red を必ず新規 code test に限定しない。characterization、inspect-only、manual-only、no-new-test exception は許容するが、理由と代替 evidence を必要にする。
  - 低リスク docs-only step に過剰な code test 作成を義務化しない。

## 確定判断
- `具体テストケース一覧` という見出し名は維持する。
  - 理由:
    - 既存 template / prompt / skill / reviewer docs との連続性を保つ。
    - 改名による migration ではなく、見出し直下の定義で「完全な test inventory ではなく step-local obligations / concrete seeds」と明確化する方が今回の目的に合う。
  - 実装への要求:
    - 見出し名だけで意味を判断させず、`Test Obligation Matrix`、`Concrete Red / Characterization Seeds`、`Discovered Test Ledger` との役割差を authoring docs と template に明示する。
- `phase_plan_issue.md` は thin redirect にはせず、plan philosophy + review checklist として残す。
  - 理由:
    - 既存利用者の planning guidance 導線を残しつつ、field-level 詳細と reviewer fail 条件を `docs/authoring/issue-plan.md` に寄せれば重複を減らせる。
    - `workflow_issue.md` が lifecycle / execution policy、`docs/authoring/issue-plan.md` が plan authoring contract、`templates/issue/plan.md` が scaffold という正本分離を保てる。
  - 実装への要求:
    - `phase_plan_issue.md` から重複する field-level template 記法や execution policy を削り、plan philosophy、粒度、review checklist、正本への routing に絞る。

## 非交渉制約
- `src/spec_dock/assets/spec_dock/...` は shipped scaffold docs/templates/system の provider-side source of truth として扱う。
- `src/spec_dock/assets/install_root/...` は installed agent-tooling assets の provider-side source of truth として扱う。
- `spec-dock/` は dogfooding workspace であり、必要な確認対象ではあるが primary implementation source ではない。
- 新規・変更する path は repository instruction に従い lowercase を基本にする。
- Issue plan の改善は、human-readable であるだけでなく、sub-agent に委任可能で reviewer が検証可能な契約として成立しなければならない。
- Issue `plan.md` の各 implementation step は、実装者が追加判断なしに実行でき、reviewer が step 単位で pass / fail を判断できる execution contract でなければならない。
- Agentic TDD の workflow は Red-Green-Refactor を維持する。ただし human TDD の極小粒度をそのまま強制せず、reviewable behavior slice 単位で micro-batch できる。

## 前提
- 高度な coding agent は人間より広い context を扱えるため、1つの step 内で複数の密接な micro assertion や characterization を扱える。
- それでも、テストを実装後に都合よく合わせることを避けるため、step 開始前に何を red / characterization / inspect / manual evidence とするかは明示する必要がある。
- plan 段階で必要なのは完全な test function inventory ではなく、実装を縛る十分な test obligation と representative concrete seeds である。
- `plan.md` は planned contract として Red / Green / Refactor / closure evidence の要求、記録先、closure 条件を定義し、`report.md` は observed evidence ledger として実行結果、逸脱、discovered tests、amendment 履歴を保持する。
- 実装中に新しい仕様・bug class・外部 contract・risk surface が見つかる場合は、report evidence だけで済ませず、必要に応じて plan amendment を行う。

## 受け入れ条件
- AC-001:
  - アクター: Issue plan 作成者 / spec-reviewer
  - 前提: 新規 Issue plan を作成またはレビューする。
  - 操作: plan authoring docs と template に従って test obligation と step-local concrete tests を記述する。
  - 期待結果: `1〜3件程度` の件数目安ではなく、AC、changed contract、negative/error path、regression、invariant、manual/integration risk に基づく coverage 判断ができる。
  - 観測点: `docs/authoring/issue-plan.md`、`phase_plan_issue.md`、`templates/issue/plan.md`、関連 tests。
- AC-002:
  - アクター: main orchestrator / dev-coder / doc-writer / utility-worker
  - 前提: implementation step を開始する。
  - 操作: step contract を読み、事前に red-required / covered-existing / inspect-only / manual-required の evidence 方針を確認する。
  - 期待結果: 実装前に concrete red / characterization seeds、または正当化された covered-existing / inspect-only / manual-required の evidence path が固定され、実装後の後付けテストや仕様縮小解釈を避けられる。
  - 観測点: `templates/issue/plan.md`、`execute-issue.md`、`spec-dock-issue-execution/SKILL.md`、dev-coder config。
- AC-003:
  - アクター: main orchestrator / delegated worker
  - 前提: generated Issue `plan.md` に implementation step がある。
  - 操作: 実装エージェントが step を上から順に実行する。
  - 期待結果: 各 step は behavior goal、test obligation、Red evidence または代替理由、implementation scope、Green verification、Refactor / cleanup、closure evidence requirements、report evidence destination、amendment trigger を持ち、`plan.md` だけで Agentic TDD の作業順序を実行できる。
  - 観測点: `templates/issue/plan.md`、`docs/authoring/issue-plan.md`、`execute-issue.md`、`spec-dock-issue-execution/SKILL.md`。
- AC-004:
  - アクター: qa-reviewer / code-reviewer / spec-reviewer
  - 前提: step review または final quality gate を実施する。
  - 操作: plan obligations、step evidence、report ledger、diff を照合する。
  - 期待結果: reviewer は raw 件数ではなく obligation coverage、red/green evidence、test sensitivity、missing high-value tests、docs-only verification の妥当性を判断できる。
  - 観測点: reviewer agent config、`templates/issue/report.md`、`workflow_issue.md`。
- AC-005:
  - アクター: spec-dock maintainer
  - 前提: workflow / template / prompt / skill を読む、または更新する。
  - 操作: どの文書が lifecycle policy、plan authoring contract、template scaffold、execution routing、report evidence ledger を所有するかを確認する。
  - 期待結果: `plan.md` は planned contract、`report.md` は observed evidence ledger として分離され、同じ policy や evidence authority を複数箇所で再定義しない routing が明確になっている。
  - 観測点: `workflow_issue.md`、`docs/authoring/issue-plan.md`、`phase_plan_issue.md`、`templates/issue/plan.md`、`execute-issue.md`、skill。
- AC-006:
  - アクター: consumer repo user
  - 前提: spec-dock init / update で scaffold / installed assets を受け取る。
  - 操作: generated docs/templates/prompts/skills/agent configs を確認する。
  - 期待結果: provider-side source の改善が consumer workspace に反映され、古い `1〜3件程度` 規範や重複した conflicting policy が再生成されない。
  - 観測点: installer/update tests、generated asset assertions。
- AC-007:
  - アクター: spec-reviewer / qa-reviewer
  - 前提: Issue plan または final report をレビューする。
  - 操作: 各 step の closure 状態を確認する。
  - 期待結果: plan の Red / Green / Refactor / Evidence requirements と report の observed evidence / report update / reviewer gate のいずれかが欠ける step は、明示的な no-new-test / inspect-only / manual-only exception と代替 evidence がない限り closure 不可として扱える。
  - 観測点: `templates/issue/plan.md`、`templates/issue/report.md`、reviewer agent config。

## 例外・エッジケース
- EC-001:
  - 条件: docs-only / template-only / skill-text-only の step で code test が適切でない。
  - 期待: concrete test case 欄に無理に code test を書かず、inspect-only / structural assertion / spec-review evidence / docs diff を step-local evidence として明示できる。
  - 観測点: plan template、report template、workflow reviewer gate mapping。
- EC-002:
  - 条件: 実装中に新しい bug class、仕様差分、外部 contract risk が発見される。
  - 期待: discovered test を report に記録し、既存 plan obligation の範囲外なら plan amendment または追加 step として扱える。
  - 観測点: report ledger、plan amendment rule、final QA gate。
- EC-003:
  - 条件: 複数の behavior slice を 1 step に束ねる必要がある。
  - 期待: 同じ implementation surface / validation path / review context / rollback boundary に収まる場合だけ許可し、slice ごとの red/green evidence を残す。
  - 観測点: plan authoring docs、workflow_issue.md、step closure contract。
- EC-004:
  - 条件: 低リスクの小さな変更で test obligation が少数で足りる。
  - 期待: 少数の obligation で足りることは認めるが、`1〜3件` という raw count ではなくリスクと coverage の説明で正当化する。
  - 観測点: plan template、spec-reviewer focus。

## 入力→出力例（必要時）
- EX-001:
  - 入力: `通常 Issue は step / behavior slice ごとに 1〜3件程度の検証契約を書く`
  - 出力: `各 step は AC / changed contract / failure mode / invariant / regression risk に応じて必要な test obligation を記述する。少数で足りる場合も、件数ではなく coverage rationale で説明する。`
- EX-002:
  - 入力: `具体テストケース一覧` に docs-only/no-op と report update が混在している step template。
  - 出力: concrete red / characterization seeds、docs-only verification、report evidence update、step gate を分離した step contract。
- EX-003:
  - 入力: `S01: docs を更新する` のような作業種別だけの step。
  - 出力: behavior goal、scope、Red/inspect evidence、Green verification、Refactor/cleanup、closure evidence、amendment trigger を持つ executable step。

## 用語（ドメイン語彙）
- TERM-001:
  - Agentic TDD cycle:
    - エージェントが実装前に evidence 方針を固定し、Red / characterization / inspect / manual evidence を確認してから実装し、Green / review / commit で閉じる開発サイクル。
- TERM-002:
  - Behavior slice:
    - review 可能で、観測可能な振る舞いとして閉じられる実装単位。原則として 1 implementation step と対応する。
- TERM-003:
  - Test Obligation Matrix:
    - Issue または step が満たすべき test / verification の義務を、raw test count ではなく spec link、risk、evidence level、closure evidence で追う matrix。
- TERM-004:
  - Concrete Red / Characterization Seeds:
    - 実装 step 開始前に固定する代表的なテストまたは検証シード。完全な test function inventory ではなく、実装を後付けにしないための oracle。
- TERM-005:
  - Discovered Test Ledger:
    - 実装中に発見した追加テスト、bug class、regression risk、closure delta を report に記録する ledger。
- TERM-006:
  - Plan Amendment Rules:
    - 実装中の発見が既存 plan obligation の範囲を超える場合に、plan を更新してから実装・レビューを続けるための規則。
- TERM-007:
  - Review scope:
    - code-reviewer / spec-reviewer / qa-reviewer が検証できる差分と evidence の範囲。docs-only step では code-reviewer ではなく spec-reviewer が主 reviewer になりうる。
- TERM-008:
  - Executable workflow contract:
    - 実装エージェントが外部説明を解釈し直さず、`plan.md` の step を順に実行するだけで、Agentic TDD の Red / Green / Refactor / Evidence / Closure を進められる planned contract。実行結果の正本は `report.md` に残す。
- TERM-009:
  - Amendment trigger:
    - 実装中の発見が step scope、test obligation、risk、acceptance criteria、review boundary を変えるため、実装継続前に plan 更新へ戻るべき条件。
- TERM-010:
  - Observed evidence ledger:
    - 実際に実行した Red / Green / Refactor / verification / review / amendment / discovered tests の結果を保持する `report.md` 側の記録。

## 未確定事項
- 現時点で、実装着手を止める未確定事項はない。
- `hard cutover evidence contract` の移動先は設計で file-level に決める。要件としては、標準 Issue workflow から optional / reference pattern へ分離することを求める。
