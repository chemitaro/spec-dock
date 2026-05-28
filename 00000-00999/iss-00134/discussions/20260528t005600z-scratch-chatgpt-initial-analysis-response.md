---
種別: scratch
ID: "scratch-20260528t005600z"
タイトル: "ChatGPT initial analysis response for Matt Pocock skills integration"
状態: "draft"
作成者: "ChatGPT via Codex"
最終更新: "2026-05-28"
親: ["iss-00134"]
関連: ["research-20260528t004419z", "scratch-20260528t004700z"]
authority: "raw"
derived_from:
  - "discussions/20260528t004700z-scratch-chatgpt-initial-analysis-prompt.md"
reflected_to: []
---

# scratch-20260528t005600z ChatGPT initial analysis response for Matt Pocock skills integration

## メモ

TL;DR

推奨結論: spec-dock は grill-me をそのまま移植するのではなく、grill-with-docs を基礎にした spec-dock 版 docs-aware clarification workflow を採用するのが最も相性が良いです。名前は暫定的に spec-dock-requirement-grill または spec-dock-docs-aware-grill がよいです。

この workflow は、Matt Pocock skills の「ユーザーとの認識ズレを質問で潰す」「質問は一つずつ」「コードや docs で答えられることは人に聞かない」「曖昧な語彙を正規化する」「ADR は重い意思決定だけに使う」という核を、spec-dock の active issue / discussions / requirement / design / plan / ADR lifecycle に合わせて再構成するものです。

今回の分析では公開 repo への追加 Web 確認は行っていません。根拠は、提示された source capture 要約、file inventory、spec-dock の active epic / issue 文脈です。source capture は Matt Pocock skills の HEAD snapshot 0288510dd61ff6ef7c2003834082ab8f2387e80e、2026-05-27T12:36:22Z として提示されています。

貼り付けられたテキスト（1 点）


なお、正確な LICENSE 内容、各 SKILL.md の逐語表現、spec-dock repository の実ファイル状態はこの回答では未確認です。

Evidence map: Matt Pocock pattern -> spec-dock surface
Matt Pocock skills の pattern	提示された evidence	spec-dock 側の対応 surface	統合方針
Small, adaptable, composable agent skills	README は “Skills For Real Engineers” として、重い process-owning system ではなく、小さく適応可能で組み合わせ可能な skill を志向すると要約されている。

貼り付けられたテキスト（1 点）

	.agents/skills/ shared layer、.codex/agents / .github/agents host-specific layer	そのまま採用。spec-dock skill も一つの巨大プロセスではなく、小さな workflow skill と phase gate に分ける。
Agent/user misalignment を interview で潰す	grill-me は plan/design について relentlessly に interview し、shared understanding まで decision tree の branch を歩く。質問は一つずつ。コードベースで答えられるなら探索する。

貼り付けられたテキスト（1 点）

	issue-local discussions/interview/、requirement.md、design.md、plan.md	変形採用。interview artifact に Q/A と rationale を記録し、requirement/design/plan に反映する。
Docs-aware grilling	grill-with-docs は CONTEXT.md の domain language と照合し、曖昧語を sharpen し、concrete scenario を議論し、code と cross-reference し、resolved terms を docs に反映し、ADR は sparingly に扱う。

貼り付けられたテキスト（1 点）

	spec-dock/active/、parent initiative/epic/issue docs、discussions/research、discussions/disc、ADR template	中核として採用・大きく変形。CONTEXT.md 単体ではなく、active issue tree + discussion artifacts + .agent generated state を context source とする。
PRD synthesis	to-prd は conversation/codebase understanding から PRD を作り、repo を探索し、domain glossary vocabulary を使い、module/test confirmation を行う。

貼り付けられたテキスト（1 点）

	issue requirement.md / design.md / plan.md、spec-manager / implementation-planner	変形採用。PRD という別成果物ではなく、spec-dock issue docs の requirement/design/plan synthesis に寄せる。
Vertical-slice issue breakdown	to-issues は PRD/plan を independently grabbable vertical slices に分割し、HITL vs AFK を区別し、dependency-ordered issues を publish する。

貼り付けられたテキスト（1 点）

	Initiative -> Epic -> Issue tree、spec-dock new issue、plan dependencies	変形採用。issue/plan の slice design と agent delegation readiness に使う。
Behavior-first TDD	tdd は behavior-first red-green-refactor、vertical tracer bullet、public interfaces、horizontal “all tests then all code” の回避を重視する。

貼り付けられたテキスト（1 点）

	既存 spec-driven-tdd-workflow	ほぼそのまま採用済み surface に接続。新規 skill ではなく既存 skill の補強に使う。
Architecture deepening	improve-codebase-architecture は domain language と ADR を使い、interface/implementation/depth/seam/adapter/leverage/locality を観点に deepening opportunities を探し、visual HTML report 後に selected candidate を grill する。

貼り付けられたテキスト（1 点）

	system-architect、repo-analyst、researcher、discussions/research、discussions/disc、ADR	部分採用。観点は採用。HTML report mandatory は採用しない。
Setup skill	setup-matt-pocock-skills は repo-local setup、issue tracker、triage label vocabulary、domain docs layout を扱う。

貼り付けられたテキスト（1 点）

	spec-dock installer、provider authority src/spec_dock/assets/install_root/	限定的に変形採用。spec-dock は provider-side assets から installed layout に sync する前提なので、直接 setup script の移植は避ける。
Discussion artifact separation	spec-dock は research、disc、interview、scratch、adr を分け、research では facts / inference / unverified items / implications を分離する。

貼り付けられたテキスト（1 点）

	spec-dock/templates/discussions/	強く維持。Matt Pocock の docs update loop を spec-dock artifact taxonomy に分解する。
Recommended integration vision
結論

spec-dock に取り込むべき本質は、Matt Pocock skills の個別ファイル名や Claude plugin 形式ではなく、次の clarification-first engineering loop です。

source-grounded read
  -> unresolved decision tree
  -> one-question-at-a-time interview
  -> facts / assumptions / options separation
  -> issue docs synthesis
  -> ADR triage only for durable architectural decisions
  -> vertical-slice execution plan

これを spec-dock では、次のように実装するのがよいです。

issue start
  -> source-grounded context pass
  -> requirement grill
  -> requirement/design synthesis
  -> design grill
  -> ADR triage
  -> vertical-slice plan
  -> TDD / implementation
  -> review / finish / sync / validate
重要な設計原則
1. CONTEXT.md をそのまま spec-dock の中心にしない

Matt Pocock skills では CONTEXT.md が domain language / docs-aware grilling の中心として見えます。ただし spec-dock はすでに hierarchical spec workspace を持っています。具体的には、spec-dock/initiatives/ の Initiative -> Epic -> Issue tree、spec-dock/active/ の symlink entrance、.agent/ の generated index/tree/dependency state、templates/discussions/ の artifact model が提示されています。

貼り付けられたテキスト（1 点）

そのため、spec-dock では CONTEXT.md 単体ではなく、次を context source set として扱うべきです。

active issue docs:
  requirement.md
  design.md
  plan.md

parent context:
  active epic docs
  active initiative docs

issue-local discussions:
  discussions/research/**
  discussions/disc/**
  discussions/interview/**
  discussions/adr/**

generated navigation/state:
  spec-dock/.agent/**

repo evidence:
  relevant source files
  relevant tests
  existing agent/tooling assets

未検証: requirement.md / design.md / plan.md の正確なファイル名は、prompt 上の「現在の issue requirement/design/plan」という記述からの推定です。実 repo での file naming は後続確認対象です。

2. “grill” は人間に質問するだけの phase ではない

Matt Pocock pattern の強みは、「人間に聞く前に、コードベースや docs から答えられることを探索する」点です。spec-dock ではこれを明示的に二段階化するべきです。

Phase A: Source-grounded pre-read
- active issue / parent epic / parent initiative を読む
- discussions/research から external facts / implementation facts を拾う
- .agent index/tree/dependency state を見る
- relevant code/tests/assets を見る
- 自力で答えられる疑問は human question にしない

Phase B: Human interview
- source からは解けない high-impact ambiguity だけを聞く
- 質問は一つずつ
- 各質問に rationale と affected artifacts を付ける
3. docs update は inline mutation ではなく artifact-mediated synthesis にする

grill-with-docs の「terms が resolved されたら CONTEXT.md を inline update」は強いパターンですが、spec-dock ではそのままやると authority が混乱します。

spec-dock 版では次のように変形するのが安全です。

interview artifact:
  Q/A, rationale, reflection target を記録

disc artifact:
  options, tradeoffs, recommendation, open questions を記録

research artifact:
  facts, inference, unverified, implications を分離

issue docs:
  requirement/design/plan に synthesis として反映

ADR:
  hard-to-reverse, surprising, real-tradeoff decisions のみ

この分解は、提示された spec-dock discussion artifact model と整合します。

貼り付けられたテキスト（1 点）

4. provider authority を絶対に守る

active epic は agent-tooling assets の source-of-truth と installed layout を揃えるものです。provider-side authority は src/spec_dock/assets/install_root/ で、install_root は consumer repo の installed layout と同型、installer は structure-preserving sync を行うという前提が提示されています。

貼り付けられたテキスト（1 点）

したがって、今回追加する skill / agent / template は dogfooding workspace 直下だけでなく、原則として provider authority に置くべきです。

Provider-side authority:
src/spec_dock/assets/install_root/.agents/skills/...
src/spec_dock/assets/install_root/.codex/agents/...
src/spec_dock/assets/install_root/spec-dock/templates/discussions/...

Installed layout:
.agents/skills/...
.codex/agents/...
spec-dock/templates/discussions/...
Grill-me vs grill-with-docs decision analysis
推奨判断

採用ベース: engineering/grill-with-docs
補助的に取り込む: productivity/grill-me の one-question-at-a-time / decision-tree walking / shared understanding loop
採用しない: grill-me の docs 非依存な汎用 interview skill としての単純移植

比較
観点	grill-me	grill-with-docs	spec-dock での判断
主目的	plan/design について user を徹底 interview	interview + docs/code/domain language cross-reference	spec-dock は spec workspace なので docs-aware が必須
質問方式	decision tree を歩く、質問は一つずつ	同左 + docs/code で確認	grill-me の質問 discipline は採用
docs 連携	弱い	CONTEXT.md、domain language、ADR と連携	CONTEXT.md を active issue tree / discussions に変換
artifact 連携	会話中心	docs update あり	spec-dock では interview / disc / research / issue docs / ADR に分解
ADR handling	明示的ではない	sparingly、hard-to-reverse / surprising / real-tradeoff	spec-dock-adr-facilitation に接続
spec-dock との相性	中	高	grill-with-docs を spec-dock 風に変形採用
spec-dock 版の名前案

第一候補:

spec-dock-requirement-grill

理由:

issue requirement/design/plan の具体化に使う phase だと分かりやすい。

grill の本質を残しつつ、spec-dock の issue lifecycle に閉じる。

汎用 interview ではなく requirement clarification に責務を限定できる。

第二候補:

spec-dock-docs-aware-grill

理由:

grill-with-docs との系譜が明確。

requirement だけでなく design review / ADR triage にも使える。

第三候補:

spec-dock-clarification-loop

理由:

“grill” という言葉の aggressive なニュアンスを避けられる。

一方で Matt Pocock pattern 由来の特徴が薄まる。

推奨は、shared skill 名を spec-dock-requirement-grill、内部 workflow 名を docs-aware clarification loop とすることです。

Candidate new skills / workflows table
種別	具体名	責務	入力	出力	artifact path 案	禁止事項
Skill	spec-dock-requirement-grill	active issue の requirement/design/plan を、source-grounded interview で具体化する。曖昧な目的、scope、acceptance criteria、non-goals、decision points を潰す。	active issue docs、parent epic/initiative docs、existing discussions、.agent index、relevant code/tests、user prompt	interview log、unresolved question list、requirement/design/plan patch proposal、ADR candidates	Provider: src/spec_dock/assets/install_root/.agents/skills/spec-dock-requirement-grill/SKILL.md; installed: .agents/skills/spec-dock-requirement-grill/SKILL.md	repo/docs で答えられることを人に聞かない。複数質問を一度に投げない。ADR を乱発しない。未確認推測を requirement に混ぜない。
Skill	spec-dock-discussion-synthesizer	interview/research/scratch から disc を作り、options/tradeoffs/recommendation/open questions に整理する。	discussions/interview/**、research/**、scratch/**、active issue docs	discussions/disc/<date>-<topic>.md、issue docs 反映案	src/spec_dock/assets/install_root/.agents/skills/spec-dock-discussion-synthesizer/SKILL.md	raw notes をそのまま結論化しない。facts と inference を混ぜない。unverified を recommendation に混入しない。
Skill	spec-dock-vertical-slice-planner	requirement/design を independently grabbable vertical slices に分け、HITL / AFK、dependency order、test strategy を明示する。	requirement/design、discussion decisions、existing plan、dependency state	updated plan、slice table、candidate child issues	.agents/skills/spec-dock-vertical-slice-planner/SKILL.md	horizontal phase 分割だけにしない。全テスト先行・全実装後追いの plan にしない。依存関係を隠さない。
Skill	spec-dock-adr-triage	design decisions のうち ADR 化すべきものだけを選別する。既存 spec-dock-adr-facilitation の front-door として働く。	design/disc、tradeoff list、architecture constraints	ADR-needed / not-needed classification、ADR draft request	.agents/skills/spec-dock-adr-triage/SKILL.md または既存 skill への section 追加	generic notes を ADR にしない。可逆・低影響・既知慣習の判断を ADR にしない。
Skill	spec-dock-context-crosscheck	CONTEXT.md 的な domain language check を spec-dock の active docs / discussions に対して行う。語彙の揺れ、未定義語、scope ambiguity を検出する。	issue docs、parent docs、discussion docs、.agent index	terminology findings、rename suggestions、glossary update proposal	.agents/skills/spec-dock-context-crosscheck/SKILL.md	spec-dock に新たな single global context authority を作らない。local issue の仮説を global term として断定しない。
Phase	issue clarify	issue start 後、requirement/design/plan の具体化前に実施する clarification gate。	active issue scaffold、parent context、source capture/research	interview + disc + updated requirement proposal	issue-local: discussions/interview/<date>-requirement-grill.md; discussions/disc/<date>-requirement-options.md	実装を開始しない。未解決の核心 ambiguity を plan に押し込めない。
Phase	design grill	design draft 後、実装前に architecture / interface / lifecycle / artifact authority の曖昧さを潰す。	design draft、research、disc、relevant source	design review questions、ADR candidates、design patch proposal	discussions/interview/<date>-design-grill.md; discussions/disc/<date>-design-tradeoffs.md	issue scope を勝手に拡張しない。ADR criteria を満たさない decision を ADR 化しない。
Discussion template	interview/grill-session.md	質問、rationale、answer、affected artifacts、follow-up、resolved/unresolved を記録する。	human Q/A	structured interview record	src/spec_dock/assets/install_root/spec-dock/templates/discussions/interview/grill-session.md	会話ログだけにしない。質問理由を省略しない。
Discussion template	disc/decision-tree.md	options/tradeoffs/recommendation/open questions を decision tree として残す。	interview/research/design	discussion artifact	spec-dock/templates/discussions/disc/decision-tree.md	recommendation と facts を混ぜない。
Agent role	requirement-grill-facilitator	Codex-specific agent として、shared skill を使って issue-local grilling を実施する。	active issue context、shared skill	questions, discussion artifacts, doc patch proposal	Provider: src/spec_dock/assets/install_root/.codex/agents/requirement-grill-facilitator.md	実装担当にならない。勝手に docs を確定しない。provider/installed authority を混同しない。
Agent role についての補足

既存 Codex agents には spec-manager、spec-reviewer、system-architect、implementation-planner、repo-analyst、researcher、consultant、deep-consultant などが提示されています。

貼り付けられたテキスト（1 点）

そのため、新 agent を増やす場合は慎重にすべきです。最小構成では、新 agent ではなく既存 consultant / deep-consultant に spec-dock-requirement-grill skill を読ませるだけでも成立します。

ただし、実運用で「要件定義の壁打ち役」を明確に呼び出したいなら、requirement-grill-facilitator を追加する価値があります。

Adopt / adapt / reject classification
Adopt as-is / ほぼそのまま採用
対象	理由
小さく composable な skill として設計する思想	spec-dock の shared skill / host-specific agent layer と相性が良い。
質問は一つずつ	interview の品質が上がり、Q/A artifact に落としやすい。
decision tree の branch を歩く	requirement/design の抜けを体系的に発見できる。
codebase/docs で答えられることは人に聞かない	spec-dock の .agent index、source tree、discussion artifacts と相性が良い。
shared understanding に達するまで曖昧さを潰す	issue requirement/design/plan scaffold を具体化する目的と一致する。
ADR は sparingly	spec-dock の ADR artifact を肥大化させない。
vertical tracer bullet / behavior-first TDD	既存 spec-driven-tdd-workflow と整合する。
Adapt / spec-dock 風に変形採用
対象	変形内容
grill-with-docs	CONTEXT.md 中心から、active issue docs + parent epic/initiative + discussions + .agent state 中心へ変換する。
grill-me	汎用 productivity skill ではなく、issue requirement/design clarification の sub-pattern として取り込む。
to-prd	PRD artifact ではなく、requirement.md / design.md / plan.md synthesis に変換する。
to-issues	GitHub issue publish 前提ではなく、spec-dock Initiative/Epic/Issue tree と vertical-slice plan に変換する。
setup-matt-pocock-skills	repo-local setup script ではなく、provider-side install_root assets と installer sync model に変換する。
improve-codebase-architecture	visual HTML report ではなく、research / disc / optional diagram / ADR triage に変換する。
CONTEXT.md inline update	spec-dock では interview/disc/research を経由し、issue docs または parent docs への patch proposal として扱う。
Triage label vocabulary	spec-dock issue metadata / planning vocabulary に変換できるが、初回統合では優先度を下げる。
Reject / 採用しない
対象	理由
Matt Pocock repo layout の直接移植	spec-dock の provider authority / installed layout / host-specific layer と衝突しやすい。
.claude-plugin/plugin.json の直接採用	spec-dock は .agents shared layer と .codex / .github host-specific assets を持つため、Claude plugin manifest をそのまま中心に置くべきではない。
executable scripts の取り込み	今回の source capture でも executable scripts は除外されている。まず Markdown skill pattern の統合に限定すべき。

貼り付けられたテキスト（1 点）


CONTEXT.md を single source of truth にすること	spec-dock は hierarchical spec workspace であり、単一 context doc 中心にすると authority が曖昧になる。
relentless grilling を stop condition なしで実装すること	user fatigue と artifact sprawl を招く。
すべての design decision を ADR 化すること	spec-dock の ADR は long-term architecture decisions 用であり、generic notes ではない。

貼り付けられたテキスト（1 点）


HTML visual report を必須成果物にすること	architecture insight の観点は有用だが、spec-dock の discussion artifact model とは別方向に成果物が増える。
issue tracker label setup の直接移植	spec-dock の CLI/workspace lifecycle に合わせた vocabulary 設計が必要。
Proposed spec-dock workflow in detail
1. Source-grounded context pass

目的:

人に聞く前に、active docs / discussions / code / .agent state で答えられることを確定する。

入力:

spec-dock/active/issue/**
spec-dock/active/epic/**
spec-dock/active/initiative/**
spec-dock/.agent/**
issue-local discussions/**
relevant source files
relevant tests
provider-side assets under src/spec_dock/assets/install_root/**

出力:

discussions/research/<date>-source-grounding-for-requirement-grill.md

内容:

Markdown
## Facts
## Inferences
## Unverified
## Implications
## Questions not worth asking because source already answers them
## Human questions still needed
2. Requirement grill

目的:

issue requirement scaffold を、実装可能で検証可能な requirement に変換する。

質問の優先順位:

scope boundary

user-visible outcome

source-of-truth / authority

artifact paths

lifecycle timing

backward compatibility

validation criteria

out of scope

expected failure modes

delegation readiness

出力:

discussions/interview/<date>-requirement-grill.md
discussions/disc/<date>-requirement-options.md
requirement.md patch proposal

質問 template:

Markdown
### Question N

**Question:**  
...

**Why this matters:**  
...

**Source-grounded context:**  
...

**Affected artifacts:**  
- requirement.md
- design.md
- plan.md
- discussions/disc/...
- ADR candidate: yes/no

**Answer:**  
...

**Resolution status:** resolved | partially-resolved | unresolved
3. Design grill

目的:

requirement は合っているが design が曖昧、または authority / lifecycle / installed layout にリスクがある箇所を潰す。

重点観点:

interface
implementation
artifact authority
provider-vs-installed layout
host-specific vs shared layer
dependency direction
validation
rollback
compatibility
ADR necessity

出力:

discussions/interview/<date>-design-grill.md
discussions/disc/<date>-design-tradeoffs.md
design.md patch proposal
ADR candidate list
4. ADR triage

ADR 化する条件:

hard-to-reverse
surprising
real tradeoff
long-term architecture consequence
cross-issue / cross-epic impact

ADR 化しないもの:

temporary implementation note
obvious local naming choice
one-off issue-local plan detail
low-impact reversible choice

出力:

discussions/disc/<date>-adr-triage.md
discussions/adr/<id>-<slug>.md only if criteria match
5. Vertical-slice plan

目的:

clarified requirement/design を independently grabbable implementation slices に変換する。

slice fields:

Markdown
| Slice | Goal | User-visible / repo-visible outcome | HITL or AFK | Dependencies | Tests | Files likely touched | Done criteria |

出力:

plan.md patch proposal
candidate child issues if needed
Risks and unresolved questions
Risks
Risk	内容	Mitigation
Over-questioning	“relentless” をそのまま実装すると user fatigue が起きる。	stop condition を定義する。high-impact ambiguity だけ聞く。
Artifact sprawl	interview/research/disc/adr が増えすぎる。	phase ごとに成果物を限定し、scratch から disc への昇格条件を明示する。
Authority confusion	CONTEXT.md 的な global doc と spec-dock hierarchical docs が競合する。	context source set を明示し、single global context を作らない。
Provider vs installed 混同	dogfooding workspace にだけ skill を置くと installer に乗らない。	active epic 前提に従い、provider-side src/spec_dock/assets/install_root/ を source-of-truth にする。
ADR inflation	grilling のたびに ADR が増える。	spec-dock-adr-triage で hard-to-reverse / surprising / real-tradeoff の gate を置く。
License/copy risk	source capture に LICENSE は含まれるが、この回答では内容未確認。	exact text copy 前に LICENSE 内容を確認する。pattern adaptation を優先する。
Host leakage	Claude plugin 前提の skill を Codex/GitHub assets に混ぜる。	.agents shared layer と .codex / .github adapters を分ける。
Implementation creep	requirement grill が実装 plan まで勝手に広げる。	phase responsibilities を分け、grill は clarification と synthesis に限定する。
Unverified source claims	capture 要約だけでは各 SKILL.md の詳細 nuance が欠ける可能性。	必要な時点で issue-local source capture 原文を読み直す。
Unresolved / 未検証

Matt Pocock skills の LICENSE 内容
Source capture に LICENSE は含まれると提示されているが、内容はこの回答では未確認。exact copy する前に確認が必要。

各 SKILL.md の逐語的な instruction structure
inventory と observed essence は提示されているが、各 Markdown 原文の詳細構造はこの回答では未確認。

spec-dock issue docs の正確な file naming
requirement.md / design.md / plan.md と表記しているが、prompt の “issue requirement/design/plan” からの推定。実ファイル名は後続確認対象。

discussion filename convention
<date>-<topic>.md は提案。既存 convention がある場合は合わせる必要がある。

CLI command として issue clarify を追加するか
まず skill/template として導入し、CLI command 化は後続判断でもよい。

新 agent を増やすか、既存 consultant / deep-consultant に skill を読ませるか
初期導入では後者が低リスク。明確な呼び出し UX が必要なら requirement-grill-facilitator を追加する。

Next follow-up prompts for deeper ChatGPT loop
P0
1. Design the actual spec-dock-requirement-grill SKILL.md
Using the captured Matt Pocock grill-me and grill-with-docs essence, draft a spec-dock-native `.agents/skills/spec-dock-requirement-grill/SKILL.md`.

Constraints:
- It must use active issue docs, discussions/research, discussions/disc, discussions/interview, and ADR triage.
- It must not rely on a global CONTEXT.md.
- It must ask one question at a time.
- It must not ask humans questions answerable from repo/docs.
- It must include stop conditions, output artifacts, and prohibitions.
2. Map CONTEXT.md semantics to spec-dock context sources
Analyze how Matt Pocock skills use CONTEXT.md conceptually, then design the spec-dock equivalent context source set.

Deliver:
- context source priority order
- what can be updated automatically
- what requires human confirmation
- how issue-local terms can or cannot become parent-level vocabulary
- risks of adding a global context file
3. Define the issue clarify lifecycle phase
Design a spec-dock `issue clarify` phase that sits after `issue start` and before implementation planning.

Deliver:
- lifecycle position
- inputs
- outputs
- discussion artifacts created
- validation checks
- whether it should be a CLI command, a prompt, a skill, or all three
P1
4. Draft discussion templates for grill workflow
Create spec-dock-native templates for:
- discussions/interview/grill-session.md
- discussions/research/source-grounding.md
- discussions/disc/decision-tree.md
- discussions/disc/adr-triage.md

Each template must separate facts, inference, unverified claims, recommendation, and open questions.
5. Decide whether to add a new Codex agent
Evaluate whether spec-dock should add `.codex/agents/requirement-grill-facilitator.md` or reuse existing consultant/deep-consultant/spec-manager agents.

Compare:
- invocation clarity
- agent sprawl
- responsibility overlap
- provider-side install_root implications
- downstream user experience
6. Adapt to-prd and to-issues into spec-dock issue docs
Map Matt Pocock `to-prd` and `to-issues` patterns into spec-dock's requirement/design/plan and Initiative/Epic/Issue tree.

Deliver:
- which sections belong in requirement
- which belong in design
- which belong in plan
- how to represent HITL vs AFK slices
- dependency ordering format
P2
7. Build ADR triage policy for grill outputs
Design a policy for deciding when a grill output should become an ADR in spec-dock.

Use these candidate criteria:
- hard-to-reverse
- surprising
- real tradeoff
- long-term architecture impact
- cross-issue consequence

Also define examples that should not become ADRs.
8. License and copy policy review
Using the captured LICENSE from Matt Pocock skills, determine what spec-dock may copy verbatim, what should be paraphrased, and what should only be used as inspiration.

Classify:
- skill names
- Markdown structure
- instruction language
- manifest/plugin metadata
- scripts
9. Dogfood iss-00134 with the proposed grill loop
Apply the proposed spec-dock-requirement-grill workflow to iss-00134 itself.

Deliver:
- source-grounded facts
- unresolved questions
- first 5 one-at-a-time interview questions
- draft requirement updates
- draft design options
- ADR candidates
Discussion artifact draft outline

The following can be copied into a spec-dock discussion artifact with light editing.

Markdown
# Research: Matt Pocock skills integration patterns for spec-dock

## Source scope

This research is based on the issue-local Matt Pocock skills source capture and the current spec-dock active issue context.

Captured Matt Pocock skills snapshot:
- commit: 0288510dd61ff6ef7c2003834082ab8f2387e80e
- date: 2026-05-27T12:36:22Z
- captured: root docs, CONTEXT.md, CLAUDE.md, LICENSE, plugin manifest, ADR, skill Markdown docs and SKILL.md files
- excluded: executable scripts

No additional public repo Web verification was performed in this analysis.

## External facts

- Matt Pocock skills are described as small, adaptable, composable skills for real engineering rather than heavy process-owning systems.
- Observed failure modes include agent/user misalignment, verbose or inconsistent domain language, weak feedback loops, and codebase entropy.
- `grill-me` performs one-question-at-a-time interview over a plan/design until shared understanding is reached.
- `grill-with-docs` adds docs awareness, domain language checking, code cross-reference, inline docs update, and sparse ADR usage.
- `to-prd` synthesizes conversation/codebase understanding into a PRD.
- `to-issues` breaks plans into vertical-slice issues and distinguishes HITL vs AFK work.
- `tdd` emphasizes behavior-first red-green-refactor and vertical tracer bullets.
- `improve-codebase-architecture` looks for deepening opportunities using interface/implementation/depth/seam/adapter/leverage/locality.

## Implementation facts

- spec-dock scaffolds a repo-local spec-driven documentation workspace.
- spec-dock uses Initiative -> Epic -> Issue hierarchy.
- `spec-dock/active/` is the active symlink entrance.
- `spec-dock/.agent/` contains generated index/tree/dependency state.
- `spec-dock/templates/discussions/` contains research/disc/interview/scratch/adr templates.
- `.agents/skills/` is the shared skill layer.
- `.codex/agents`, `.codex/prompts`, and `.github/agents` are host-specific tooling layers.
- The active epic treats `src/spec_dock/assets/install_root/` as provider-side authority.
- `install_root` is intended to match consumer repo installed layout.
- The installer performs structure-preserving sync.

## Inferences

- `grill-with-docs` is a better base than `grill-me` for spec-dock because spec-dock already has active docs, discussion artifacts, and ADR lifecycle.
- `CONTEXT.md` should not be imported as a single source of truth; its function should be mapped to active issue docs, parent docs, discussions, `.agent` state, and relevant code.
- The core integration should be a docs-aware clarification loop for issue requirement/design.
- The first concrete skill should be `spec-dock-requirement-grill`.
- The workflow should create or update interview, research, and disc artifacts before proposing requirement/design/plan changes.
- ADR creation should be gated by hard-to-reverse, surprising, real-tradeoff architectural decisions.

## Unverified claims

- Exact file names for issue requirement/design/plan docs are not verified here.
- Existing discussion filename conventions are not verified here.
- Matt Pocock skills LICENSE contents are not verified here.
- Exact wording of individual SKILL.md files is not verified here.
- Whether a new Codex agent is preferable to reusing existing consultant/deep-consultant is not yet decided.

## Implications

- Directly copying Matt Pocock repo layout is not recommended.
- Directly importing Claude plugin metadata is not recommended.
- Executable scripts should remain out of scope for the initial integration.
- The integration should focus on shared `.agents/skills` first, then optional `.codex/agents` wrappers.
- Provider-side files must be added under `src/spec_dock/assets/install_root/` to satisfy the active epic boundary.
Markdown
# Discussion: Adopt Matt Pocock grill patterns in spec-dock

## Decision under consideration

Adopt a spec-dock-native docs-aware clarification workflow inspired by Matt Pocock `grill-me` and `grill-with-docs`.

## Recommendation

Adopt `grill-with-docs` as the primary pattern, adapted into a spec-dock skill named `spec-dock-requirement-grill`.

Use `grill-me` only as a sub-pattern for:
- one-question-at-a-time interview
- decision-tree traversal
- shared-understanding stop condition
- avoiding questions answerable from repo/docs

## Option A: Directly import `grill-me`

### Pros
- Simple.
- Captures the core interview behavior.

### Cons
- Not docs-aware enough for spec-dock.
- Does not naturally use research/disc/interview/adr artifacts.
- Risks becoming chat-only rather than artifact-driven.

### Assessment
Reject as primary approach.

## Option B: Directly import `grill-with-docs`

### Pros
- Docs-aware.
- Handles domain language and ADR sparingly.
- Closer to spec-dock's documentation workflow.

### Cons
- Assumes `CONTEXT.md`.
- Inline docs update behavior needs authority controls.
- Does not directly map to spec-dock discussion artifact taxonomy.

### Assessment
Adopt only after spec-dock-specific transformation.

## Option C: Create `spec-dock-requirement-grill`

### Pros
- Preserves Matt Pocock essence while respecting spec-dock lifecycle.
- Uses active issue docs and discussion artifacts.
- Can be installed through provider-side `install_root`.
- Avoids global context authority conflict.

### Cons
- Requires new skill design and possibly new templates.
- Requires clear stop conditions.
- May overlap with existing consultant/deep-consultant unless responsibilities are explicit.

### Assessment
Recommended.

## Proposed outputs

- `.agents/skills/spec-dock-requirement-grill/SKILL.md`
- Optional `.codex/agents/requirement-grill-facilitator.md`
- `spec-dock/templates/discussions/interview/grill-session.md`
- `spec-dock/templates/discussions/research/source-grounding.md`
- `spec-dock/templates/discussions/disc/decision-tree.md`
- possible updates to existing ADR facilitation skill

## Open questions

1. Should `issue clarify` become a CLI command or remain a skill/prompt workflow?
2. Should a new Codex agent be added, or should existing consultant/deep-consultant agents use the skill?
3. What exact file naming convention should grill discussion artifacts use?
4. Should spec-dock introduce any global glossary/context file, or keep all context hierarchical and issue-local?
5. What does the Matt Pocock skills LICENSE permit for exact text reuse?

貼り付けられたテキスト（1 点）
