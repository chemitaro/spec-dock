---
種別: disc
ID: "20260605t043350z-disc"
タイトル: "Agent Workflow PDCA Analysis Summary"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-05"
親: ["epic-00158"]
関連:
  - "iss-00159"
authority: "proposed"
derived_from:
  - "spec-dock/active/epic/discussions/20260605t030757z-research-chatgpt-clean-workflow-hardening-report.md"
  - "spec-dock/active/epic/discussions/20260605t033127z-research-chatgpt-gate-status-v1-design-report.md"
  - "spec-dock/active/epic/discussions/20260605t035200z-research-chatgpt-skill-docs-information-architecture-report.md"
  - "spec-dock/active/epic/discussions/20260605t035201z-research-chatgpt-empirical-skill-compliance-tests-report.md"
  - "spec-dock/active/epic/discussions/20260605t040000z-research-chatgpt-skill-rewrite-targets-report.md"
  - "spec-dock/active/epic/discussions/20260605t040338z-disc-skill-docs-workflow-spine-synthesis.md"
  - "spec-dock/active/epic/issues/iss-00159-make-issue-planning-skill-expose-mandatory-authoring-gates/requirement.md"
reflected_to:
  - "spec-dock/active/epic/issues/iss-00159-make-issue-planning-skill-expose-mandatory-authoring-gates/requirement.md"
---

# 20260605t043350z-disc Agent Workflow PDCA Analysis Summary

## 目的

この文書は、`epic-00158 Agent Workflow PDCA Hardening` でここまで行った Deep Research / ChatGPT analysis / issue planning の知見を、日本語で整理した分析レポートである。

正本としての要件・設計・計画ではなく、後続 issue を作成・設計するときの参照用 synthesis として扱う。

## 要約

現時点の最重要結論は、SpecDock の問題を「もっと厳格な gate を増やす」だけで解決しようとしないこと。

ユーザーの最新仮説は、より精密には次の通りである。

- 現在の skill は軽量で、詳細 docs を参照する構造になっている。
- この役割分担自体はよい。
- しかし、agent に必ず守ってほしい workflow が docs 側に埋もれ、複数 docs に分散している。
- agent が linked docs を開かない、または一部だけ読むと、そもそも必要な作業順序を知らない状態になる。
- したがって、agent が最初に守るべき operational workflow spine は skill 側に薄く書く。
- docs 側には、各 artifact の意味、field semantics、詳細 schema、例、概念説明を置く。

この方向性は、これまでの clean ChatGPT analysis と Deep Research の知見とも整合する。first issue としては runtime gate ではなく、`spec-dock-issue-planning` skill を operationally sufficient にする `iss-00159` が妥当である。

## 採用可能な情報源

### 採用候補として扱えるもの

- `20260605t030757z-research-chatgpt-clean-workflow-hardening-report.md`
  - contaminated output を破棄した後の clean ChatGPT workflow hardening analysis。
- `20260605t033127z-research-chatgpt-gate-status-v1-design-report.md`
  - runtime gate / status command の有用性と限界を分析したもの。
- `20260605t035200z-research-chatgpt-skill-docs-information-architecture-report.md`
  - skill と docs の情報設計を分析したもの。
- `20260605t035201z-research-chatgpt-empirical-skill-compliance-tests-report.md`
  - empirical compliance probe / regression harness の方向性を分析したもの。
- `20260605t040000z-research-chatgpt-skill-rewrite-targets-report.md`
  - どの skill から rewrite すべきかを分析したもの。
- `20260605t040338z-disc-skill-docs-workflow-spine-synthesis.md`
  - 上記 clean research を統合し、初手を `spec-dock-issue-planning` skill に絞った synthesis。
- Deep Research branch reports A-F
  - OpenAI / Codex guidance、context engineering、execution plan packet、compliance gate、eval harness、multi-agent orchestration などの一次情報・比較情報を整理したもの。

### 採用してはいけないもの

- `20260605t021857z-research-chatgpt-workflow-compliance-analysis-task-package.md`
  - 最初の ChatGPT thread で `今すぐ回答` が使われたため、得られた知見は破棄対象。
- `20260605t023441z-research-chatgpt-implementation-roadmap-task-package.md`
  - invalid report に汚染された prompt を使ったため、採用対象外。

### 未完了のもの

- `iss-00159` requirement critique 用 ChatGPT thread
  - task package: `spec-dock/active/epic/issues/iss-00159-make-issue-planning-skill-expose-mandatory-authoring-gates/discussions/20260605t041318z-research-chatgpt-requirement-critique-task-package.md`
  - ChatGPT へ送信済み。
  - `今すぐ回答` は押していない。
  - Chrome Extension 接続不良により DOM extraction が未完了。
  - 復旧後に同 thread から抽出し、report として保存する必要がある。

## 中核分析

### 1. 問題は「agent が workflow を守らない」だけではなく「workflow が最初に見えない」こと

観測された failure mode は、review skip、commit skip、sub-agent 不使用、requirement / design / plan の同時作成、review 前の phase promotion、delegated draft の canonical 化などである。

これらは単に「厳密さが足りない」というより、agent が最初に読む instruction surface に必要な workflow spine が十分に出ていないことが原因になりうる。

現在の `spec-dock-issue-planning` skill は、関連 docs への link と短い reminder を持つ。しかし step-by-step の実行順序、停止条件、evidence obligation は主に複数 docs に分散している。agent がそれらを読まなければ、正しい順序を知らないまま進めてしまう。

### 2. skill と docs の役割分担は維持する

今回の方向性は、docs を skill に丸ごと移すことではない。

適切な分担は次の通り。

- skill:
  - agent が最初に守るべき mandatory procedure。
  - phase order。
  - stop condition。
  - reviewer gate。
  - canonical ownership。
  - delegated draft の扱い。
  - report evidence obligation。
  - next docs to read。
- docs:
  - artifact の概念的意味。
  - 各 section / field の記入方法。
  - schema。
  - examples。
  - edge cases。
  - long policy。
  - historical rationale。

これにより、skill は model compliance の入口として機能し、docs は詳細 authority として残る。

### 3. first issue は runtime gate ではなく issue planning skill rewrite がよい

`gate status --json` や runtime enforcement は後続候補として有用である。しかし first issue としては重い。

理由:

- ユーザーの最新仮説は runtime enforcement ではなく instruction discoverability に向いている。
- agent が正しい workflow を知らない状態では、runtime gate は失敗検出には役立つが、初動改善には直結しにくい。
- PDCA の初手としては、小さい skill rewrite を行い、manual compliance probe で改善を観測する方がよい。

したがって、`iss-00159 Make Issue Planning Skill Expose Mandatory Authoring Gates` を first implementation issue とする判断は妥当である。

### 4. reviewer gate は「状態名」まで skill に出す

agent が `spec-reviewer` の有無や状態を曖昧に扱うと、review skip や stale review の誤採用が起きる。

skill には少なくとも次を明示するべきである。

- fresh `spec-reviewer` pass だけが phase promotion の条件である。
- missing / stale / failed / unavailable / denied / waived / provisional は pass ではない。
- non-pass の場合は、fix / re-review / clarification / prior phase return のいずれかに戻る。
- main orchestrator の provisional self-check は reviewer pass ではない。

ただし、review state の永続化や CLI enforcement はこの first issue の外に置く。

### 5. canonical artifact ownership を明示する

sub-agent や ChatGPT / Deep Research の出力は valuable evidence であるが、canonical docs ではない。

skill に必要な表現:

- canonical `requirement.md` / `design.md` / `plan.md` / `report.md` は main orchestrator owned。
- `system-architect` / `implementation-planner` / researcher / ChatGPT output は evidence または draft。
- canonical 化には main orchestrator adoption と `report.md` evidence が必要。

これにより、draft をそのまま requirement/design/plan として扱う failure を減らす。

### 6. unresolved gap は execution へ押し込まない

requirement / design / plan に未解決 gap がある場合、execution assumption として吸収してはいけない。

skill には、次の戻り先を明示する必要がある。

- user intent / source uncertainty:
  - clarification。
- requirement gap:
  - requirement phase。
- design gap:
  - design phase。
- plan executability gap:
  - plan phase。

この戻り先を skill に書くことで、agent が「実装しながら決める」方向へ流れるのを抑える。

### 7. plan は executable handoff でなければならない

Issue `plan.md` は、実行者が workflow 判断を発明しなくてよい状態でなければならない。

特に必要な条件:

- step-local scope が明確。
- 担当 role / delegation boundary が明確。
- verification が各 step または完了条件に紐づく。
- evidence destination がある。
- rollback / stop condition が必要な箇所にある。
- unresolved requirement/design gap が残っていない。

この条件は詳細 schema として docs に残し、skill には handoff readiness の短い checklist として置くのがよい。

## `iss-00159` に反映済みの方向性

`iss-00159` の requirement draft には、ここまでの分析から次を反映済み。

- 対象を `spec-dock-issue-planning` skill に限定。
- mandatory workflow spine を skill に書く。
- requirement -> fresh reviewer pass -> design -> fresh reviewer pass -> plan -> fresh reviewer pass -> execution handoff の順序を可視化。
- non-pass reviewer states を pass ではないと明示。
- canonical docs は main-orchestrator-owned、delegated drafts は evidence と明示。
- unresolved gap は clarification / prior phase に戻す。
- plan は executable handoff でなければならない。
- 詳細 schema は docs に残す。
- runtime gate / CLI / validation / hub skill / issue-execution skill / manual harness は対象外。

この issue は「初手として小さく、しかし主因に直接効く」scope になっている。

## 推奨する実行順序

1. `iss-00159` requirement を formal `spec-reviewer` にかける。
2. reviewer findings があれば requirement を修正し、fresh pass まで繰り返す。
3. design で skill rewrite の構造を決める。
   - provider source:
     - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
   - dogfooding mirror:
     - `.agents/skills/spec-dock-issue-planning/SKILL.md`
   - mirror を同 issue で更新するか、update flow で反映するかを明示する。
4. design に対して fresh `spec-reviewer` pass を得る。
5. plan で `doc-writer` への bounded task を作る。
6. plan に対して fresh `spec-reviewer` pass を得る。
7. execution で skill rewrite を行う。
8. manual compliance smoke probe を行う。
   - agent が skill だけを読んだときに phase order / reviewer gate / non-pass states / canonical ownership / gap return を言えるか確認する。
9. 結果を `report.md` に evidence として残す。
10. 次の PDCA issue を選ぶ。

## 後続 issue 候補

### Hub skill の routing 改善

対象:

- `spec-driven-tdd-workflow`

狙い:

- hub skill から issue planning / issue execution / clarification / epic planning への routing を安定させる。
- leaf skill に workflow spine を置く方針と矛盾しないよう、hub は route selection と required first read に集中する。

### `spec-dock-issue-execution` skill の execution boundary 改善

対象:

- `spec-dock-issue-execution`

狙い:

- execution phase で requirement/design/plan gap を発見した時の戻り先を明示する。
- implementation agent が spec authoring 判断を発明しないようにする。

### Empirical compliance harness

狙い:

- skill rewrite が実際に agent behavior を改善したか、簡易 probe から測定する。
- under-use / over-use / stale-review acceptance / parallel-authoring violation などを scenario 化する。

初期は manual / semi-manual でよい。最初から大きな CI harness にしない。

### Runtime gate / `gate status --json`

狙い:

- spec authoring gate の状態を機械的に見えるようにする。
- reviewer pass / stale / missing / unavailable を CLI output として確認できるようにする。

位置づけ:

- first issue ではない。
- skill rewrite と manual probe の後、繰り返し failure が残る場合に着手する。

### Observability / trace evidence

狙い:

- agent / sub-agent / reviewer / ChatGPT / Deep Research output の evidence lineage を明確にする。
- source-backed findings と model-derived suggestions を区別する。
- invalidated / contaminated output を後から誤採用しない。

## 重要な設計原則

### Principle 1: workflow spine は skill、詳細 authority は docs

agent に守ってほしい順序・停止条件は skill に置く。意味・schema・例は docs に置く。

### Principle 2: strictness より discoverability を先に直す

runtime gate は有用だが、最初に agent が読む surface の問題を先に直す。

### Principle 3: reviewer pass を phase promotion の唯一の正規条件にする

fresh pass 以外は pass ではない。曖昧な self-check は promotion evidence にしない。

### Principle 4: delegated draft は evidence であり canonical ではない

sub-agent や ChatGPT output は採用判断が必要である。main orchestrator adoption と report evidence を経て初めて canonical docs に反映される。

### Principle 5: unresolved gap は戻す

execution へ押し込まず、clarification / requirement / design / plan の適切な phase へ戻す。

### Principle 6: PDCA は小さい変更から始める

最初から全 skill / runtime / harness を同時に改修しない。`spec-dock-issue-planning` の改善から始め、観測して次を選ぶ。

## リスク

### Skill が長くなりすぎる

workflow spine を書く必要はあるが、field schema や long policy を skill にコピーすると、skill が読みにくくなり、docs との二重管理も増える。

対策:

- section headings と短い checklist にする。
- 詳細は docs link に逃がす。
- acceptance criteria で over-copy を禁止する。

### Gate 偏重に戻る

`gate status --json` は魅力的だが、今回の主因は instruction discoverability である。

対策:

- first issue では runtime gate を明示的に non-scope にする。
- skill rewrite 後の probe 結果で次 issue を決める。

### Formal reviewer なしに進む

この epic 自体が workflow compliance を改善するものなので、issue authoring でも reviewer gate を飛ばすと自己矛盾になる。

対策:

- `iss-00159` requirement -> design -> plan の各 phase で fresh `spec-reviewer` pass を要求する。
- pass 前に implementation へ進めない。

### ChatGPT output の採用境界が曖昧になる

ChatGPT / Deep Research output は強い分析材料だが、contaminated output や incomplete extraction が混ざると判断を誤る。

対策:

- `今すぐ回答` 使用済み output は破棄。
- extraction 未完了 output は未採用。
- 採用時は report / discussion に evidence adoption を記録する。

## 現時点の未解決事項

- `iss-00159` requirement の formal `spec-reviewer` pass がまだない。
- requirement critique 用 ChatGPT thread の抽出が Chrome Extension 接続不良で未完了。
- `doc-writer` への実装 handoff は design / plan pass 後。
- manual compliance smoke probe の具体 scenario はまだ plan 化していない。
- Branch G/H Deep Research は task package 作成済みだが、report completion は未確認。

## 推奨する次アクション

最優先は `iss-00159` の requirement を formal review に進めること。

ただし、Chrome Extension が復旧した場合は、先に送信済み ChatGPT requirement critique thread を抽出し、必要なら requirement に軽微な修正を反映してから formal `spec-reviewer` に出すのが望ましい。

Chrome 復旧を待たずに進める場合でも、現 requirement はすでにユーザーの最新仮説をかなり反映しているため、formal review に出す価値はある。

## 結論

SpecDock の workflow compliance 改善は、まず「モデルが最初に見る instruction surface」を直すべきである。

最初の実装対象は `spec-dock-issue-planning` skill。ここに、requirement -> review -> design -> review -> plan -> review -> execution handoff の workflow spine、non-pass reviewer states、canonical ownership、gap return、report evidence obligation を短く明示する。

詳細 schema や概念説明は docs に残す。この分担により、skill は agent behavior の入口、docs は意味と詳細の authority になる。

この first issue を通して効果を観測し、次に hub skill、issue execution skill、empirical compliance harness、runtime gate の順で PDCA を続けるのが現時点の推奨である。
