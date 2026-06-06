---
種別: research
ID: "20260605t050037z-research"
タイトル: "ChatGPT Issue Decomposition Report for Skill Docs Workflow Spine"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-05"
親: ["epic-00158"]
関連:
  - "iss-00159"
  - "20260605t044551z-research"
authority: "evidence"
source: "chatgpt-use report"
answer_now_used: false
thread_url: "https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a22552c-1a04-83a9-b39b-b5eeb6ff7129"
extraction_method: "Chrome DOM assistant message extraction; no copy button or clipboard"
completion_signal: "assistant message present; stop control absent; thinking text absent; stable after second check"
rate_limit_notice_visible_after_completion: true
---

# 20260605t050037z-research ChatGPT Issue Decomposition Report for Skill Docs Workflow Spine

## 実行メタデータ

- thread_url: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a22552c-1a04-83a9-b39b-b5eeb6ff7129
- project_boundary: Codex-only Project under for codex app
- model_visible: じっくり思考 Pro
- answer_now_used: false
- extraction_method: Chrome DOM assistant message extraction; no copy button or clipboard
- completion_signal: assistant message present; stop control absent; thinking text absent; stable after second check
- note: A request-frequency notice remained visible after completion, but the assistant response was complete and extraction succeeded.

## 位置づけ

この report は ChatGPT による issue decomposition evidence である。canonical issue backlog / requirement / design / plan ではない。

## ChatGPT 出力

1. 情報充足度

結論: issue 分解には十分です。 iss-00159 を first small issue として維持し、その後を skill-only / docs-only / harness-only / runtime-later に分けて backlog 化できます。提供パッケージには、epic / active issue / iss-00159 の scope / non-scope、skill-docs 境界、mandatory invariants、現在の skill 抜粋、推奨 section 構造が揃っています。

貼り付けられたテキスト（1 点）

GitHub 確認結果: issue #159 は public GitHub 上で open issue として確認できました。GitHub 表示上は “Make Issue Planning Skill Expose Mandatory Authoring Gates #159” で、2026-06-05 に open されています。
GitHub
 一方、指定 branch URL と指定 commit URL は 404 でした。そのため、branch 固有の worktree state は未検査であり、そこに依存する判断は提供パッケージの記述に基づく暫定判断です。
不明なサイト
+1

追加で不確実な点はありますが、issue 作成はブロックしません。

不確実性	issue 作成をブロックするか	扱い
current branch 上の実ファイル差分、dogfooding mirror の同期状態	しない	各 issue の最初の acceptance / verification に “provider asset と mirror の現状確認” を入れる
既存 test / manual harness の命名、配置、fixture 慣習	しない	harness issue の design/plan 内で inventory する
spec-reviewer が repo 内 skill として存在するか、外部 agent role としてのみ存在するか	しない	reviewer contract issue で “existing reviewer surface inventory” を最初の作業にする
runtime gate の既存 validation model と active manifest schema の完全な現状	runtime issue だけはブロック	runtime issue は後段に回し、先に docs/skills/harness で期待 contract を固定する
docs 内部の重複・矛盾の全量	しない	docs audit issue の scope にする

確認済みの補助事実: main branch 上の provider-side spec-dock-issue-planning skill は非常に短く、docs routing、canonical ownership、delegated drafts as evidence、fresh spec-reviewer pass、unresolved gaps return、report.md gate evidence を含む一方、visible step-by-step workflow spine はまだ薄い形です。
GitHub
 main branch の issue execution skill は planning artifacts readiness、non-executable plan.md as unresolved gap、step execution evidence、completion / PR merge-preparer reminders まで含みますが、flat で密な runbook です。
GitHub
 hub skill は docs source of truth、fresh reviewer pass、non-pass states are not pass、leaf routingを既に持っていますが、「mandatory spine は leaf skill に薄く置く」という今回の境界をさらに明示する余地があります。
GitHub

2. 修正項目の全体棚卸し
Skill 修正項目

spec-dock-issue-planning に mandatory workflow spine を追加する。
requirement -> fresh spec-reviewer pass -> design -> fresh spec-reviewer pass -> plan -> fresh spec-reviewer pass -> execution handoff を skill 冒頭で見える化する。

issue planning skill に section 構造を入れる。
推奨構造は Use this skill when / Source-of-truth boundary / Must read before acting / Entry gate / Must-follow checklist / Stop and return conditions / Evidence to record / Exit / handoff criteria / Keep out of this skill。

fresh / non-pass state の最小定義を skill に置く。
詳細 schema は docs へ逃がし、skill では “missing / stale / failed / unavailable / denied / waived / provisional is not pass” を operational gate として明記する。

canonical ownership と delegated evidence boundary を issue planning skill の gate 文脈に置く。
requirement.md / design.md / plan.md / report.md は main orchestrator-owned。delegated drafts / worker notes / discussions / research は採用されるまで evidence only。

unresolved gap の stop behavior を skill に明示する。
requirement gap は requirement / clarification に戻す。design gap は design / clarification に戻す。plan gap は plan / clarification に戻す。execution で吸収しない。

non-executable issue plan.md blocks execution handoff を skill に置く。
issue execution skill 側にも同じ invariant があるが、handoff 前の planning skill にも exit condition として必要。

provider asset と dogfooding mirror の同期方針を各 skill issue に含める。
provider source は src/spec_dock/assets/install_root/.agents/skills/、mirror は .agents/skills/ とされているため、変更対象を片側だけにしない。

貼り付けられたテキスト（1 点）

hub skill を boundary/routing に寄せて調整する。
docs は meaning/schema/detail の source、leaf skills は mandatory operational workflow spine の source、という分担を短く明示する。main branch hub は “skills stay concise” と “leaf skills own workflow details” を既に含むため、全面 rewrite ではなく境界表現の調整で足ります。
GitHub

issue execution skill を entry gate / execution loop / completion gate で sectionize する。
policy 追加ではなく、既存の重要 gate を agent が見落としにくい形へ再配置する。

clarification skill に return-to-authoring wording を足す。
現状でも concise workflow は成立しているため、過剰拡張せず、planning / prior phase へ戻す handoff 文だけを補強する。main branch clarification skill は read-source-first、一問ずつ、analysis-only / draft-only、canonical adoption through report を既に含みます。
GitHub

epic / initiative planning skills に issue planning と同型の compact parity を持たせる。
reuse-before-create、phase gates、decomposition handoff、report evidence obligations を見える化する。main branch の epic / initiative skills は fresh reviewer pass と evidence record を既に含みますが、sectioned runbook ではありません。
GitHub
+1

delegated authoring specialist skills は原則後回し。
spec-dock-system-architect と spec-dock-implementation-planner は canonical ownership、discussion-only draft、diff guard、depth=2 delegation、forbidden actions をかなり詳細に持っています。
GitHub
+1
 まず leaf planning / execution / hub の spine を固める方が効果が高いです。

Docs 修正項目

workflow_spec_authoring.md を gate semantics の authoritative doc として audit する。
main branch docs には phase sequence、fresh reviewer pass、non-pass state、canonical authority、delegated draft evidence、Promotion Record が既に詳述されています。
GitHub
 follow-up では skill 側に置く最小 spine と docs 側に置く detailed semantics の境界を整える。

workflow_issue.md を planning-to-execution handoff と completion semantics の正本として audit する。
skill 側に “do next / stop / evidence / exit” を置き、issue lifecycle の詳細 policy は docs に残す。

phase_plan_issue.md と docs/authoring/issue-plan.md を executable plan detail の正本として audit する。
skill には “non-executable plan blocks handoff” だけを置き、step field semantics、test case schema、amendment trigger、closure index は docs に置く。

workflow_clarification.md と skill handoff の整合を確認する。
unresolved ambiguity がどの phase に戻るのかを docs と skill で同じ vocabulary にする。

workflow_initiative.md / workflow_epic.md と planning skills の parity を確認する。
initiative/epic は issue-internal TDD cadence ではなく、decomposition handoff までを扱う。

guide.md または overview docs の skill/docs boundary 表現を audit する。
“skills are runbooks, not manuals” の原則を docs 側の導入説明に置く。ただし skill に docs の全文をコピーしない。

doc-writing workflow routing を明示する。
shipped docs / templates / skills / workflow text changes は doc-writing workflow を通す、という route を hub または relevant docs に置く。

Runtime 修正項目

今は runtime gate を実装しない。
iss-00159 の non-scope として明示済み。先に skill/docs contract を固める。

後段で read-only gate status model を設計する。
gate status --json または同等の read model は、いきなり enforcement ではなく、まず evidence state を観測する段階にする。

後段で issue start readiness check を検討する。
reviewer-pass artifacts と executable plan.md がない場合の fail-closed / warning / incomplete のどれにするかは docs contract 固定後に決める。

後段で issue finish completion guardrails を検討する。
README 上も issue finish は lifecycle closure であり、commit / push / PR / merge / validate / test / review completion を保証しないと説明されています。
GitHub
 runtime enforcement より先に docs/skills で completion evidence contract を固定する。

active manifest / context-pack / Promotion Record consistency validation を後段化する。
これは安全重要だが scope が大きい。skill hardening とは別 issue にする。

Harness 修正項目

skill spine static checks を追加する。
provider skill と dogfooding mirror に mandatory section / invariant / docs link があることを検査する。

mirror parity check を追加する。
src/spec_dock/assets/install_root/.agents/skills/... と .agents/skills/... の差異を許容するか、同期必須にするかを明確化してテストする。

docs link check を追加する。
skill が参照する docs path が provider asset 内で存在することを検査する。

manual scenario harness を追加する。
stale reviewer、waived reviewer、delegated draft not adopted、non-executable plan、unresolved design gap、issue finish alone not completion、などの behavior scenarios を manual-tests または fixture docs にする。

runtime validation tests は後段に分離する。
runtime gate を入れる前に、read-only status と contract tests を置く。

Templates 修正項目

templates を compliance authority にしない。
report / plan template に evidence slots を置くのは可。ただし “template が満たされたから pass” にはしない。

report.md template に gate evidence の受け皿を検討する。
Spec Authoring Gate、Evidence Adoption Ledger、handoff readiness、completion evidence の slots を足す可能性がある。

plan.md template に executable plan への誘導を置く。
field semantics は docs へリンクし、template は scaffold に留める。

template update は docs/skill issue に混ぜない。
テンプレートは利用者影響が大きいため separate issue にする。

Reviewer workflow 修正項目

spec-reviewer pass の evidence contract を文書化する。
最小項目: target artifact、upstream artifacts、target hash / revision、review timestamp、review_status: pass、findings resolution、freshness condition。

non-pass state を reviewer workflow と authoring workflow の両方で同じ語彙にする。
missing / stale / failed / unavailable / denied / waived / provisional は pass ではない。

fresh の定義を runtime-independent に固定する。
まず docs で “review target と approved artifact が一致していること” 程度を contract 化し、hash/manifest enforcement は後段 runtime issue に回す。

preflight reviewer と final reviewer gate を分離する。
preflight は improvement input。final fresh reviewer pass は phase promotion gate。

reviewer unavailable / denied / waived を degraded success にしない。
risk acceptance は記録できるが promotion / execution handoff には使えない。

3. 推奨 issue backlog
E158 01 Existing iss 00159 Make Issue Planning Skill Expose Mandatory Authoring Gates

Objective: issue planning skill に最小の mandatory authoring workflow spine を追加する。

Scope: spec-dock-issue-planning の provider asset と必要なら dogfooding mirror。冒頭に Mandatory Issue Authoring Workflow 相当を置く。

Non-scope: runtime gate、CLI、validation、hub rewrite、issue execution rewrite、epic/initiative parity、manual harness、gate status --json。

Affected files: src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md; mirror が運用対象なら .agents/skills/spec-dock-issue-planning/SKILL.md。

Dependencies: なし。最初に実施。

Acceptance criteria: phase sequence、fresh pass、non-pass states、canonical ownership、delegated evidence boundary、unresolved gap return、non-executable plan.md blocks handoff、docs routing、report evidence が skill から直接読める。

Verification method: diff review、skill markdown lint、参照 docs path check、provider/mirror parity check。まだ harness がない場合は manual grep で可。

Risk / separation reason: first issue を小さくしないと、skill/docs/runtime の責務境界が崩れる。

Priority / sequencing: P0 / 1番目。

E158 02 Add Skill Spine Regression Checks

Objective: iss-00159 で追加した operational spine が将来消えないよう、軽量 regression check を追加する。

Scope: static check。mandatory headings / keywords / docs links / provider-mirror parity を検査。

Non-scope: agent behavior simulation、runtime enforcement、docs rewrite。

Affected files: tests/ または manual-tests/ 配下の既存慣習に合わせる。必要なら installer asset tests。

Dependencies: iss-00159。

Acceptance criteria: issue planning skill が required phrases / docs links / section structure を満たすことを検査できる。mirror を更新する運用なら mirror 差分も検知できる。

Verification method: python -m unittest discover -v または既存 test command。README は unittest discovery を testing command として示しています。
GitHub

Risk / separation reason: skill text change と harness change を同じ first issue に入れると、iss-00159 が膨らむ。

Priority / sequencing: P1 / 2番目。

E158 03 Clarify Hub Routing For Mandatory Skill Spine

Objective: hub skill の boundary を “docs are detail authority, leaf skills expose mandatory operational spine” に揃える。

Scope: spec-driven-tdd-workflow の routing / boundary wording のみ。visual grouping は可。

Non-scope: leaf skill rewrite、workflow docs rewrite、runtime behavior。

Affected files: src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md; mirror if applicable.

Dependencies: iss-00159 後が望ましい。issue planning leaf の実例を hub から参照できるため。

Acceptance criteria: hub が “docs に全 workflow を押し込める” 方向に読めない。leaf routing が issue planning / execution / clarification / epic / initiative に分かる。templates are scaffolds の原則は維持。

Verification method: static skill check、manual read-through、docs link check。

Risk / separation reason: hub は全 workflow の入口なので、leaf issue と混ぜると review 対象が広がる。

Priority / sequencing: P1 / 3番目。

E158 04 Section Issue Execution Skill Gates

Objective: issue execution skill を entry gate / execution loop / evidence ledger / final handoff gate に分け、既存 policy を見落としにくくする。

Scope: sectioning and wording only。既存 invariant の再配置。issue finish は completion ではない、final PR delivery evidence before finish、non-executable plan blocks execution を見える化。

Non-scope: issue lifecycle policy change、runtime command change、plan schema duplication。

Affected files: src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md; mirror if applicable.

Dependencies: iss-00159。planning handoff gate と execution entry gate の用語を合わせる。

Acceptance criteria: skill 冒頭で execution entry readiness が分かる。実行中の step-by-step evidence obligations が分かる。completion/final gates が issue finish と混同されない。

Verification method: static section check、manual scenario review: missing reviewer pass / non-executable plan / final evidence missing。

Risk / separation reason: issue execution は既に密で、policy 追加ではなく readability refactor に限定しないと docs の複製になる。

Priority / sequencing: P1 / 4番目。

E158 05 Add Epic Initiative Planning Skill Spine Parity

Objective: initiative / epic planning skills に、issue planning と同じ minimal spine philosophy を適用する。

Scope: reuse-before-create、requirement/design/plan reviewer gates、decomposition handoff、report evidence、clarification return、docs routing。

Non-scope: issue execution TDD cadence、runtime gates、deep docs rewrite。

Affected files: spec-dock-initiative-planning/SKILL.md, spec-dock-epic-planning/SKILL.md in provider asset and mirror if applicable.

Dependencies: iss-00159; hub boundary issue が先でも後でも可。

Acceptance criteria: initiative は Epic decomposition handoff、epic は Issue decomposition handoff を明記。create/import default ではなく reuse-first が見える。fresh reviewer pass gate が sectioned。

Verification method: static skill spine check extended to initiative/epic。

Risk / separation reason: initiative/epic は issue planning と似ているが、handoff 先と reuse-before-create が異なる。issue planning と混ぜると first issue が大きすぎる。

Priority / sequencing: P1 / 5番目。

E158 06 Align Clarification Skill Return Handoffs

Objective: clarification skill の output/handoff に、戻り先 phase と adoption evidence の扱いをさらに明確にする。

Scope: small wording only。unresolved ambiguity が requirement/design/plan のどこを block するか、authoring mode への return を示す。

Non-scope: clarification workflow docs の全面 rewrite、interview schema change、new artifact kind。

Affected files: spec-dock-clarification/SKILL.md; possibly workflow_clarification.md only if wording conflict is found.

Dependencies: issue planning spine 後。

Acceptance criteria: clarification result が “analysis-only / draft-only / canonical authoring” と “return to relevant authoring phase” を明示する。user に聞く前に local context を読む原則は維持。

Verification method: manual read-through、scenario review: requirement ambiguity, design ambiguity, plan ambiguity。

Risk / separation reason: clarification skill は既に良い状態なので、過剰拡張を避けるため separate small issue にする。

Priority / sequencing: P2。

E158 07 Audit Spec Authoring Docs For Gate Semantics

Objective: workflow_spec_authoring.md を、fresh reviewer / non-pass states / delegated evidence / promotion record の detail authority として整理する。

Scope: docs-only。skill に置いた spine と docs の詳細説明を整合させる。矛盾・重複・曖昧な “waived” / “provisional” の扱いを audit。

Non-scope: skill rewrite、runtime enforcement、template change。

Affected files: src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md; related docs only if direct contradiction is found.

Dependencies: iss-00159 and ideally hub/leaf wording。

Acceptance criteria: skill から参照される exact semantics が docs にある。fresh の意味、non-pass states、Promotion Record、Evidence Adoption Ledger が矛盾なく読める。

Verification method: docs link check、manual contradiction checklist、reviewer gate examples if docs already support examples。

Risk / separation reason: docs は長くなりやすい。issue lifecycle docs と混ぜると “docs overhaul” になる。

Priority / sequencing: P2。

E158 08 Audit Issue Lifecycle Docs For Execution Handoff

Objective: issue planning → execution handoff と issue completion semantics を workflow_issue.md / issue plan docs に固定する。

Scope: docs-only。executable plan.md、report evidence、execution readiness、final validation/review/docs/PR delivery evidence before lifecycle closure。

Non-scope: runtime gate、issue execution skill refactor、plan template change。

Affected files: workflow_issue.md, phase_plan_issue.md, docs/authoring/issue-plan.md。

Dependencies: iss-00159; issue execution skill sectioning 前後どちらでもよいが、用語を合わせる。

Acceptance criteria: non-executable plan がなぜ handoff を block するかが docs で分かる。issue finish が completion evidence の代替ではない。plan step semantics は docs に残り、skill に重複しない。

Verification method: docs cross-reference check、manual scenario checklist。

Risk / separation reason: issue lifecycle と plan schema は近いが、skill ではなく docs の detail authority。skill issue に混ぜない。

Priority / sequencing: P2。

E158 09 Define Reviewer Gate Evidence Contract

Objective: spec-reviewer pass を promotion gate に使える最小 evidence contract と freshness rule を定義する。

Scope: docs/reviewer-workflow only。existing reviewer surface を inventory し、必要な出力項目・non-pass states・staleness conditions を docs に固定。

Non-scope: reviewer implementation change、runtime hash validation、new reviewer agent。

Affected files: likely workflow_spec_authoring.md; possibly reviewer instruction docs/skill if present after local inventory。

Dependencies: spec authoring docs audit の前後。runtime gate より前。

Acceptance criteria: “fresh pass” を agent が operationally 判断するための最小 evidence が定義される。waived / provisional / unavailable を pass と呼ばない。preflight と final gate が分離される。

Verification method: docs review、sample reviewer evidence snippet、negative examples。

Risk / separation reason: reviewer contract は runtime gate の前提。runtime issue に混ぜると enforcement details に流れる。

Priority / sequencing: P2。

E158 10 Keep Templates As Scaffolds With Evidence Slots

Objective: templates を compliance authority にせず、必要な evidence slots だけを足す。

Scope: report / plan templates の placeholders、docs links、comments。必要なら “template is scaffold” wording。

Non-scope: reviewer pass logic、runtime validation、full report schema rewrite。

Affected files: src/spec_dock/assets/spec_dock/templates/... under issue/report/plan templates; exact files require local inventory。

Dependencies: docs audit after gate/evidence vocabulary is stable。

Acceptance criteria: templates は agent/human に evidence placement を促すが、template completion alone を gate success にしない。docs への参照がある。

Verification method: template snapshot tests if any、manual scaffold review。

Risk / separation reason: templates are copied into user workspaces; accidental policy authority化の影響が大きい。

Priority / sequencing: P3。

E158 11 Add Manual Workflow Scenario Harness

Objective: mandatory workflow spine の実運用シナリオを manual / fixture-based harness で検証可能にする。

Scope: scenario docs or tests for stale reviewer, missing reviewer, delegated draft not adopted, unresolved gap, non-executable plan, issue finish not completion。

Non-scope: runtime enforcement、agent automation benchmark、new CLI。

Affected files: manual-tests/ or tests/fixtures/ depending local convention。

Dependencies: iss-00159, skill spine checks, docs audits。

Acceptance criteria: 各 scenario が expected stop / return / evidence behavior を明示する。少なくとも issue planning と issue execution の境界を検査できる。

Verification method: manual runbook review or test runner if implemented。

Risk / separation reason: static checks だけでは agent behavior の regression を捕まえにくいが、最初から automation-heavy にすると遅い。

Priority / sequencing: P3。

E158 12 Design Gate Status Read Model

Objective: runtime enforcement の前に、gate state を read-only で表現する JSON/read model を設計する。

Scope: design/docs or prototype-only。artifacts readiness、reviewer evidence、freshness、executable plan、completion evidence の status vocabulary。

Non-scope: blocking issue start / issue finish、strict validation failure、CLI public contract commitment unless explicitly accepted。

Affected files: design docs under active issue, possibly reference_* docs later。

Dependencies: reviewer evidence contract and issue lifecycle docs。

Acceptance criteria: gate state schema が、pass/block/incomplete/stale/unavailable/waived/provisional を区別できる。runtime enforcement issue がこの schema を参照できる。

Verification method: sample JSON fixtures、negative fixture review。

Risk / separation reason: enforcement first は危険。まず観測 model を固定する。

Priority / sequencing: P4。

E158 13 Add Runtime Issue Start Readiness Check

Objective: issue execution start 前に reviewer-pass planning artifacts と executable plan.md readiness を検出する。

Scope: runtime check design and implementation, after read model。fail-closed / warn / incomplete の policy は docs contract に従う。

Non-scope: completion gate、reviewer generation、docs rewrite。

Affected files: runtime script/code under src/spec_dock/assets/spec_dock/scripts/ or package runtime modules; exact files require local inventory。

Dependencies: gate status read model、docs audits、harness fixtures。

Acceptance criteria: missing/stale reviewer evidence、draft/template-only artifacts、non-executable plan を検出できる。false positive / migration behavior が documented。

Verification method: unit tests, fixture workspace tests, validate if integrated。

Risk / separation reason: runtime blocking can break existing users; must come after docs/skills/harness。

Priority / sequencing: P4/P5。

E158 14 Add Runtime Issue Finish Completion Guardrails

Objective: issue finish が lifecycle closure であり、delivery completion evidence の代替ではないことを runtime 上も guardrail 化する。

Scope: warning/status/checklist or optional block, depending docs decision。final validation/review/docs/PR delivery evidence の presence check。

Non-scope: PR creation, merge automation, code review implementation。

Affected files: runtime command implementation and tests; exact files require local inventory。

Dependencies: issue lifecycle docs audit、gate status read model、manual scenario harness。

Acceptance criteria: issue finish 前に required completion evidence missing を検出または明示警告できる。README と docs の “finish is not completion” と矛盾しない。

Verification method: fixture tests for missing evidence / present evidence / legacy issue。

Risk / separation reason: completion policy は repo/team差が出やすい。issue start readiness と同時に入れると blast radius が大きい。

Priority / sequencing: P5。

4. iss-00159 との境界
iss-00159 に残すもの

spec-dock-issue-planning skill のみ。

冒頭付近の短い named section、例: Mandatory Issue Authoring Workflow。

requirement -> reviewer pass -> design -> reviewer pass -> plan -> reviewer pass -> execution handoff。

missing / stale / failed / unavailable / denied / waived / provisional は pass ではない。

minimal fresh definition。

canonical docs are main-orchestrator-owned。

delegated drafts / notes / discussions / research are evidence until adopted。

unresolved requirement/design/plan gaps return to clarification or relevant prior authoring phase。

non-executable issue plan.md blocks execution handoff。

lifecycle / authoring / clarification / issue-plan docs への routing。

report.md に Spec Authoring Gate / handoff readiness evidence を記録すること。

follow-up に回すもの

hub skill の境界・routing 調整。

issue execution skill の sectioning。

epic / initiative planning skill parity。

clarification return wording。

docs audits。

reviewer evidence contract。

static regression harness。

manual scenario harness。

templates evidence slots。

runtime gates / read model / CLI / validation。

混ぜてはいけないもの

gate status --json。

issue start / issue finish の behavior change。

validation logic。

workflow_issue.md の completion policy rewrite。

workflow_spec_authoring.md の長文 rewrite。

all-skills rewrite。

templates を compliance authority にする変更。

reviewer implementation change。

PR / merge workflow change。

5. 最小 PDCA sequence

最小で measurable improvement を出すなら、次の 6 issue がよいです。

iss-00159 Make Issue Planning Skill Expose Mandatory Authoring Gates
最初の visible behavioral improvement。issue planning の stop/exit gate が agent に直接見える。

Add Skill Spine Regression Checks
追加した spine が消えないことを検査する。小さいが PDCA の Check を作れる。

Clarify Hub Routing For Mandatory Skill Spine
entry point で “docs only” に逃げる誤読を防ぐ。

Section Issue Execution Skill Gates
planning handoff の受け側を整える。execution が spec gap を吸収しない。

Add Epic Initiative Planning Skill Spine Parity
issue planning で得た pattern を上位 planning に展開する。ただし issue execution cadence は入れない。

Audit Issue Lifecycle Docs For Execution Handoff
skill に置いた operational gate と docs の lifecycle/detail authority を整合させる。

この sequence は runtime に触れず、skill/docs 境界を保ち、agent behavior に直接効く部分から始めます。

6. 大きすぎる issue の分割提案
誘惑案: Rewrite All Workflow Skills

大きすぎます。 次に分割すべきです。

Make Issue Planning Skill Expose Mandatory Authoring Gates

Clarify Hub Routing For Mandatory Skill Spine

Section Issue Execution Skill Gates

Add Epic Initiative Planning Skill Spine Parity

Align Clarification Skill Return Handoffs

誘惑案: Implement Runtime Gates For Agent Workflow

大きすぎます。 次に分割すべきです。

Design Gate Status Read Model

Define Reviewer Gate Evidence Contract

Add Runtime Issue Start Readiness Check

Add Runtime Issue Finish Completion Guardrails

Add Active Promotion Consistency Validation
※これは backlog に入れるなら E158 15 として別 issue。active manifest / context-pack / Promotion Record hash consistency に限定する。

誘惑案: Overhaul Workflow Docs

大きすぎます。 次に分割すべきです。

Audit Spec Authoring Docs For Gate Semantics

Audit Issue Lifecycle Docs For Execution Handoff

Audit Clarification Docs For Authoring Returns

Audit Planning Docs For Executable Plan Semantics

Update Guide For Skill Docs Boundary

誘惑案: Make Templates Enforce Compliance

方向が危険です。 分割するなら:

Keep Templates As Scaffolds With Evidence Slots

Add Report Evidence Slot Documentation

Add Template Snapshot Tests

ただし template completion を gate success と見なす設計は採用しない方がよいです。

誘惑案: Fix Reviewer Workflow

曖昧すぎます。 分割するなら:

Define Reviewer Gate Evidence Contract

Document Reviewer Non Pass States

Separate Preflight Review From Final Gate

Add Runtime Reviewer Freshness Validation
※最後だけ runtime-later。

7. 採用しない方がよい案
Runtime gate first

採用しない方がよいです。理由は、現時点では skill/docs contract がまだ固まりきっていないため、runtime が premature policy authority になります。まず skill で mandatory spine、docs で exact semantics、harness で regression を固め、その後 read-only gate status、最後に enforcement が安全です。

Copy docs into skills

採用しない方がよいです。skill は agent runbook であり、manual ではありません。skill には “Must do X / Read doc Y / Stop if Z / Record evidence in W” だけを置くべきです。schema、field semantics、examples、edge cases、historical rationale は docs に置くべきです。

Rewrite all skills at once

採用しない方がよいです。review が難しくなり、どの変更が agent behavior に効いたか測れません。issue planning → harness → hub → execution → initiative/epic parity の順に小さく回す方が PDCA になります。

Make templates compliance authorities

採用しない方がよいです。templates は scaffolds です。template section が埋まっていることは reviewer pass や lifecycle completion の代替になりません。

Treat waived or provisional review as degraded success

採用しない方がよいです。waived / provisional / unavailable / denied は pass ではありません。risk acceptance は記録できても phase promotion / execution handoff の pass にはしない方が安全です。

Let delegated drafts become canonical by placement

採用しない方がよいです。delegated drafts、worker notes、research、discussions は evidence only です。main orchestrator が canonical artifacts に採用し、report.md に採否を残し、fresh reviewer pass を通すまでは authority にしません。

Treat issue finish as workflow completion

採用しない方がよいです。issue finish は lifecycle closure であり、validation / review / docs / PR delivery evidence の代替ではありません。README でも issue finish が commit / push / PR / merge / validate / test / review completion を保証しないことが説明されています。
GitHub

Use branch state assumptions as facts

採用しない方がよいです。今回、指定 branch と commit は GitHub から見えませんでした。branch 固有の状態は Codex 側 local worktree で検証する必要があります。
不明なサイト
+1

8. SpecDock issue creation notes
ASCII title constraint

SpecDock の new/import {initiative,epic,issue} title は ASCII alphanumerics plus single spaces、slug は kebab-case という制約が README に示されています。
GitHub
 そのため、issue title は英数字と単一スペースだけで作るのが安全です。避けるべき文字は :, /, -, _, (), #, &, JSON 以外の記号類です。JSON 自体は英字なので可です。

推奨 title は以下のように ASCII-safe にできます。

Make Issue Planning Skill Expose Mandatory Authoring Gates

Add Skill Spine Regression Checks

Clarify Hub Routing For Mandatory Skill Spine

Section Issue Execution Skill Gates

Add Epic Initiative Planning Skill Spine Parity

Align Clarification Skill Return Handoffs

Audit Spec Authoring Docs For Gate Semantics

Audit Issue Lifecycle Docs For Execution Handoff

Define Reviewer Gate Evidence Contract

Keep Templates As Scaffolds With Evidence Slots

Add Manual Workflow Scenario Harness

Design Gate Status Read Model

Add Runtime Issue Start Readiness Check

Add Runtime Issue Finish Completion Guardrails

初期分類

skill-only initially

Make Issue Planning Skill Expose Mandatory Authoring Gates

Clarify Hub Routing For Mandatory Skill Spine

Section Issue Execution Skill Gates

Add Epic Initiative Planning Skill Spine Parity

Align Clarification Skill Return Handoffs

docs-only initially

Audit Spec Authoring Docs For Gate Semantics

Audit Issue Lifecycle Docs For Execution Handoff

Define Reviewer Gate Evidence Contract

harness-only initially

Add Skill Spine Regression Checks

Add Manual Workflow Scenario Harness

templates-only initially

Keep Templates As Scaffolds With Evidence Slots

runtime-later

Design Gate Status Read Model

Add Runtime Issue Start Readiness Check

Add Runtime Issue Finish Completion Guardrails

requirement/design/plan が必要なもの

原則として、shipped assets を変更する issue は requirement/design/plan を持つべきです。skills、docs、templates、runtime、harness はいずれも agent workflow に影響するため、軽量でも issue-specific non-template artifacts と fresh reviewer pass を通すのが安全です。

iss-00159: 必須。small だが workflow skill の変更なので R/D/P を持つ。

skill-only follow-ups: 必須。変更は小さくても agent instruction surface を変える。

docs-only follow-ups: 必須。workflow policy/detail authority を変えるため。

harness-only follow-ups: 必須。何を regression とみなすかが workflow contract になるため。

templates-only follow-up: 必須。copied scaffold の user-facing 影響があるため。

runtime-later: 必須。fail/warn/block semantics、migration behavior、fixtures が必要。

discussion-only bootstrap で足りるもの

discussion-only bootstrap で足りるのは、asset をまだ変更しない inventory / research / comparison に限るべきです。たとえば “current branch の provider asset と dogfooding mirror の差分一覧だけを作る” なら discussion-only でもよいです。ただし、今回の backlog は broad research を追加しなくても issue 作成可能な粒度に分解できています。各 issue の最初に local inventory task を入れれば十分です。
