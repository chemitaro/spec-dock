# Agent Workflow PDCA Hardening 調査報告

## 要旨

### エグゼクティブサマリー

現行の公開情報で確認できる Codex 系ワークフローの中核は、「できるだけ多くのエージェントを勝手に動かすこと」ではなく、「明示的で狭い委譲」「役割ごとの境界」「外部化された done 条件」「継続的な検証」にあります。Codex の一次情報では、サブエージェントは自動ではなく**明示的に依頼したときだけ**起動され、深い再帰委譲は既定で抑制され、最良のカスタムエージェントは**narrow and opinionated**であるべきだとされています。長時間タスクでも、信頼性を支えるのは派手なプロンプトではなく、仕様、計画、実行 runbook、監査ログ、検証コマンドをファイルとして残す運用です。citeturn20search0turn17view0turn17view3turn6view0turn6view2

SpecDock にとって特に重要なのは、**最終回答の所有者**を先に決めることです。OpenAI Agents SDK の公開資料は、`handoff` と `agent-as-tool` を明確に分けています。`handoff` は会話の所有権を専門家へ移し、`agents as tools` は親オーケストレータが制御権を保持したまま専門家を呼び出します。したがって、「実装者・研究者・レビューアの出力を親が束ねて最終判定する」設計なら、原則は handoff よりも manager/agent-as-tool パターンのほうが適合します。citeturn34view1turn32view1turn34view2

レビュー独立性について、公開一次情報が強く示しているのは「別人格」ではなく**別境界**です。Codex の auto-review は、主エージェントとは別の reviewer agent に承認判断を委ねます。reviewer が見るのはコンパクトな transcript、関連ツール出力、正確な承認要求であり、**hidden chain-of-thought は含まれません**。さらに Codex の PR review 例は、`pr_explorer`、`reviewer`、`docs_researcher` を分離し、いずれも read-only を基本にしています。これは「自己申告を検証と見なさない」「探索と判定を別役割にする」設計の強い根拠です。citeturn23view0turn17view3turn8view5

スキル設計では、長い万能プロンプトよりも、**短い routing metadata と必要時だけ読む本体**が重視されています。Codex は skill の `name` と `description` を主なトリガ判定に使い、初期スキル一覧には文脈予算の上限があり、必要時だけ `SKILL.md` 全文を読み込みます。OpenAI の skill eval ガイドは、明示起動だけでなく暗黙起動・誤起動も含めた小さな CSV ベースの評価、`command_execution` の deterministic check、`--output-schema` による rubric JSON を推奨しています。つまり SpecDock で必要なのは「トリガを書くこと」よりも、「そのトリガが under-use と over-use の両方で崩れないことを継続的に測ること」です。citeturn22search0turn39view7turn38view0turn38view2turn38view3turn38view4turn38view5

本調査で高信頼に言えることと、SpecDock が独自に制度化すべきことは分ける必要があります。高信頼に言えるのは、**明示委譲、read-only reviewer、artifact gating、evidence anchored review、progressive disclosure、trace-based eval** です。一方で、`stale / waived / unavailable` のレビュー状態や、「一般的な PR review が常に fresh session である」という保証は、今回確認した公開一次情報では明文化されていません。これらは SpecDock 側で定義・検証すべき運用品質ラベルです。citeturn23view0turn8view0turn8view6turn17view0

### SpecDock が先に確かめるべきこと

要件化の前に Codex で直接検証すべき論点は四つあります。第一に、想定サーフェスごとに委譲挙動が同じかどうかです。公開 docs では subagents は明示起動ですが、app、CLI、IDE、GitHub review、cloud task の UI と trace 粒度は同一とは限りません。第二に、レビュー run が implementation run とどこまで状態を共有するかです。auto-review は separate reviewer ですが、一般 code review で「fresh session」が保証されるとは docs から断定できません。第三に、trace と evidentiary artifacts にどの程度の ID、diff base/head、file reference、timestamp が残るかです。第四に、skills の implicit invocation と description budget が実運用の skill catalog 量でどの程度安定するかです。citeturn18view0turn23view0turn14view0turn22search0turn38view6

## ソースマップ

### 主要ソースの整理

| 区分 | ソース | 日付・鮮度シグナル | 主にカバーする面 | 証拠強度 | SpecDock への関連性 |
|---|---|---|---|---|---|
| 一次情報 | Codex `Subagents` / `Subagent concepts` citeturn18view0turn20search0 | 現行 live docs を 2026-06-05 時点で確認 | 明示委譲、context pollution、`max_depth`、役割分離 | 高 | 委譲方針、summary-only handoff、再帰抑制 |
| 一次情報 | Codex `AGENTS.md` guide / Best practices citeturn5view4turn39view5 | 現行 live docs | 指示境界、階層優先順位、短く実務的な repo guidance | 高 | user instructions と repo docs の分離、 source-of-truth 化 |
| 一次情報 | Codex `Agent Skills` / Best practices / changelog citeturn22search0turn39view7turn21search4 | 現行 live docs、skills launch changelog | skill trigger、progressive disclosure、implicit/explicit invocation | 高 | skill routing、trigger drift、防過剰注入 |
| 一次情報 | `Testing Agent Skills Systematically with Evals` citeturn38view0turn38view6 | 2026-01-22 | trigger eval、JSONL event checks、rubric JSON | 高 | skill compliance harness |
| 一次情報 | `Run long horizon tasks with Codex` citeturn6view0turn6view2 | 2026-02-23 | durable memory、milestone gating、continuous verification | 高 | PDCA hardening の骨格 |
| 一次情報 | Codex GitHub review docs / review pane / security diff scan citeturn8view0turn8view6turn8view5 | 現行 live docs | reviewer evidence、changed-file scope、read-only security review | 高 | reviewer independence、evidence packet |
| 一次情報 | Codex `Sandbox` / `Auto-review` docs citeturn23view1turn23view0 | 現行 live docs | sandbox boundary、approval reviewer、denial semantics | 高 | bounded delegation、waiver semantics、false-pass prevention |
| 一次情報 | Codex + Agents SDK multi-agent guide citeturn14view0turn14view1turn34view0 | 現行 live docs | PM-led gated handoff、traceability、manager vs handoff | 高 | task lifecycle boundary、handoff contract |
| OpenAI 近接一次情報 | OpenAI Agents SDK docs / repo / Swarm README citeturn32view0turn32view1turn34view1turn29search0 | 現行 docs、repo README | handoff vs agents-as-tools、historical handoff primitive | 高 | Codex-centered だが SDK 実装比較に有効 |
| 比較参照 | Anthropic Claude Code docs citeturn24search0turn24search1turn24search2turn24search10 | 現行 docs | isolated subagent context、forked skill context、hooks | 中 | fresh reviewer/session と deterministic enforcement の比較 |
| 比較参照 | LangChain / LangGraph docs citeturn26search0turn26search5turn26search2 | 現行 docs | context engineering、supervisor、subgraph I/O boundary | 中 | SpecDock 契約スキーマと orchestration separation の比較 |
| 比較参照 | Microsoft AutoGen docs citeturn28search0turn28search1turn28search7turn28search9 | 現行 docs | handoffs、shared-context swarm、termination conditions | 中 | lifecycle boundary、termination semantics の比較 |
| 公開実装例 | `hamelsmu/claude-review-loop` | 公開 GitHub 実装、2026-06-05 時点で検索確認 citeturn16search9 | independent second opinion review loop | 中 | no self-review の具体例 |
| 公開 issue 例 | `openai/codex` issue #16996 | 2026-04-07 citeturn41view0 | repo 指示と session policy の委譲衝突 | 中 | skipped delegation / fail-closed 設計の根拠 |

### 読み方

一次情報だけで十分に裏づけられるのは、**明示委譲、artifact gate、read-only reviewer、skills の progressive disclosure、sandbox と reviewer の分離、trace/eval 重視**です。比較参照は、これらをさらに厳格に運用する設計候補を示すものであり、Codex 要件そのものではありません。citeturn20search0turn22search0turn23view0turn24search0turn26search0

## Codex と OpenAI の公式ガイダンス

### 委譲とオーケストレーションの境界

Codex の現行公開 docs は、サブエージェントを**暗黙の万能分業機構**としては扱っていません。`Subagent concepts` では、Codex は subagents を自動では起動せず、明示的に「spawn two agents」「delegate this work in parallel」「use one agent per point」のように頼んだときだけ使うべきだとしています。さらに、`agents.max_depth` の既定値は `1` で、深い再帰委譲は token、latency、local resource の観点から危険だと明記されています。これは SpecDock が「委譲しない failure」と「委譲しすぎる failure」の両方を制御する必要があることを示します。citeturn20search0turn17view0

Codex のカスタム agent は `name`、`description`、`developer_instructions` を最低限持ち、`description` は「いつその agent を使うべきか」の human-facing guidance です。OpenAI 自身の例でも、良い custom agents は narrow and opinionated であり、役割から外れた仕事へ drift しないよう tool surface と指示を揃えるべきだとされています。`pr_explorer` は探索専用、`reviewer` は correctness/security/test の判定専用、`docs_researcher` は docs MCP を使う参照専用です。`code_mapper`、`browser_debugger`、`ui_fixer` の例も同じで、再現、解析、修正を別 agent に分けています。citeturn17view3turn18view0

### 指示境界と source of truth

Codex は `AGENTS.md` を**作業前に読む**と明記されています。global (`~/.codex/AGENTS.md`) と repo-level、さらにサブディレクトリの more specific file が layered に適用され、近いものが勝ちます。Best practices は、`AGENTS.md` を agent 用 README と位置付け、repo layout、run/build/test/lint commands、engineering conventions、do-not rules、done criteria を入れろとしていますが、同時に「短く実務的に」「肥大化したら task-specific markdown を参照させる」とも言っています。これは、user instructions、repo policies、task runbook を1枚に混ぜないほうがよいという強い示唆です。citeturn5view4turn39view5

長時間タスクについても、OpenAI の実例は同じ方向です。25時間の Codex run では、`Prompt.md` が goals / non-goals / hard constraints / deliverables / done-when を凍結し、`Plan.md` が milestones / acceptance criteria / validation commands / stop-and-fix を定義し、`Implement.md` が diffs scoped・plan を source of truth とする runbook を与え、`Documentation.md` が status / decisions / known issues の audit log になっていました。信頼性は「会話の記憶」ではなく「再読可能な外部ファイル」に置く、というパターンが一次情報からかなり明確に出ています。citeturn6view2turn6view0

### スキル、ツール、プロンプトの境界

Codex skills は reusable workflow の authoring format と位置付けられ、`SKILL.md` の `name` と `description` がトリガ判定の主信号です。Codex は skill の初期一覧では `name`、`description`、path だけを持ち、full `SKILL.md` は必要時だけ読み込みます。さらにこの初期一覧には文脈予算上限があり、約 2% の context window、もしくは不明時は 8,000 文字で cap され、必要なら description が短縮されます。つまり routing metadata は「短くても意味が崩れない」ことが重要で、巨大 description で trigger を頑張る設計は Codex と相性が悪いです。citeturn22search0

Best practices と skill eval ガイドは、skill description に「何をするか」「いつ使うか」「実際にユーザーが言いそうな trigger phrase」を入れ、1 skill = 1 job に保ち、最初から全 edge case を抱え込まないように求めています。必要なら `agents/openai.yaml` で `allow_implicit_invocation: false` も設定できます。したがって、高コスト・高権限・誤起動が危険な skill は implicit invocation を切り、通常ワークフローだけ implicit にする設計が合理的です。citeturn39view0turn39view7turn22search0

ツール追加についても、Codex の best practices は「全部つなぐな」と明言しています。必要な context が repo 外にあり、変化頻度が高く、repeatable integration にしたいときにだけ MCP を使え、ツールは manual loop を本当に減らすものから入れろ、という立場です。これは skill 過密、tool 過密、agent 過密がすべて routing quality を落とすという考え方と整合します。citeturn39view1turn39view2

### レビュー、サンドボックス、長時間実行

Codex の sandbox docs は、「sandbox は技術境界、approval policy はその境界を越えるときに止まる条件」であり、両者は別の制御だと整理しています。既定の low-friction local mode は `workspace-write` + `on-request` + `approvals_reviewer=user` です。auto-review を有効にしても sandbox boundary は広がりません。これは reviewer を approval path の判定者に置き換えるだけで、権限付与機構ではありません。もし mundane な操作まで reviewer に大量承認させているなら reviewer を賢くするのではなく、boundary 側を調整すべきだと OpenAI は述べています。citeturn23view1turn23view0

auto-review は主 agent と別の reviewer agent に approval を渡します。reviewer は compact transcript、relevant tool evidence、exact approval request を見ますが、hidden assistant reasoning は見ません。拒否時は「同じ目的を workaround・indirect execution・policy circumvention で追うな」「materially safer alternative がなければ user に止まれ」という強い指示が返ります。さらに `3` 連続 denial、または同一 turn 内 rolling window `50` 件中 `10` denial で circuit breaker が発火します。これは false-pass だけでなく **review loop runaway** を防ぐ実装パターンとして重要です。citeturn23view0

長時間実行については、Codex 自体の `/plan`、`/goal`、automations、parallel threads、worktrees に加えて、OpenAI の Responses 系 API では background jobs と compaction も推奨されています。`Run long horizon tasks with Codex` では plan → edit → run tools → observe → repair → update docs の loop が示され、`Follow a goal` では `/goal` を「verifiable stopping condition を持つ persistent objective」に使うとされています。Responses 側では minutes/hours の background jobs と `/responses/compact` で long-running context を縮約する流れが提示されています。SpecDock が Codex-centered でも、長時間 orchestration 層はこの発想を借りるべきです。citeturn6view3turn5view14turn8view4turn40search0turn40search6turn40search15

## マルチエージェント設計パターン

### 役割分担とタスクライフサイクル

OpenAI の公式 multi-agent guide は、Project Manager が root artifacts を書き、その後に Designer、Frontend Developer、Backend Developer、Tester へ handoff し、**required files が存在することを確認してから**次へ進むパターンを示しています。PM は `REQUIREMENTS.md`、`TEST.md`、`AGENT_TASKS.md` を root に作成し、Designer が `/design/design_spec.md` を作るまで先に進まず、その後で frontend/backend を並列に動かし、最後に Tester へ handoff します。足りない artifact があれば owning agent に戻し、再確認する設計です。これは「agent の善意」ではなく「artifact existence gate」で lifecycle を閉じる、かなり堅い設計です。citeturn14view1

このパターンから読み取れる重要点は、**legal next action を role と artifact で制限している**ことです。Designer は design spec だけ、Frontend Developer は `/frontend` 配下の実装だけ、Backend Developer は `/backend` 配下だけ、Tester は acceptance criteria を満たすかの検証だけを担当します。しかも downstream agents には「Do not add features」「Do not assume anything not written there」「Keep it minimal and easy to run」など scope 制約が入っています。SpecDock でも main agent、implementation agent、reviewer agent、researcher、documentation writer の各 role について、次に何をしてよいかを「自由文の期待」ではなく **artifact-gated transition** として定義するのが公開ベストプラクティスに沿います。citeturn14view1turn37view0

PR review の公式例も同じ思想です。`pr_explorer` は affected code path を読むだけ、`reviewer` は correctness/security/test risk を判定するだけ、`docs_researcher` は framework/API の docs を MCP 経由で検証するだけです。`browser_debugger` も issue reproduction と screenshots / console / network evidence に留まり、`ui_fixer` は failure mode が clear になってから smallest defensible change だけを入れます。これらは「調査」「実装」「検証」を別 role に分離し、親オーケストレータがまとめる設計が current public pattern だと示しています。citeturn17view3turn18view0

### handoff と manager の使い分け

OpenAI Agents SDK quickstart は、multi-agent pattern を選ぶ前に「誰が final answer を所有するか」を決めろと言っています。`handoffs` では specialist が conversation を引き継ぎ、`agents as tools` では orchestrator が control を保持します。Sandbox Agent の docs でも同じで、handoff は同一 top-level run の active agent を変えるだけなのに対し、`Agent.as_tool(...)` は nested run を起こし、outer orchestrator から見れば1つの tool invocation に包まれます。したがって、SpecDock が reviewer、researcher、documentation writer の出力を parent が収束・整形・判定したいなら、manager-style orchestration が第一候補です。handoff は「専門家がその turn の主担当になる」場面に限定したほうが整合します。citeturn34view1turn32view1turn34view2

### 公開パターンから抽出できる有界タスク契約

以下は、公開一次情報から逆算できる**bounded task contract** の構成要素です。`rollback_notes` だけは一次情報に「必須 field」としては出ていないため、明示的に推論としています。

| 契約要素 | 公開パターンでの根拠 | SpecDock への含意 |
|---|---|---|
| Objective | `/goal` は verifiable stopping condition を持つ durable objective を対象にし、PM agent も最初に Objective を持ちます。citeturn5view14turn14view1 | 各 sub-agent packet に目的文を固定し、done 条件と切り離さない |
| Scope | `Prompt.md` の goals / non-goals、security scan の target diff、`Do not add features`、`Do not make code changes` のような境界があります。citeturn6view2turn8view5turn17view3 | 目的とは別に in-scope / out-of-scope を必須化 |
| Authoritative inputs | `AGENT_TASKS.md` / `REQUIREMENTS.md` / `design_spec.md` だけを source of truth にする指示があります。citeturn14view1turn37view0 | 受理入力を列挙し、それ以外を advisory 扱いにする |
| Expected outputs | 公式例は exact file names と folder を明示しています。citeturn14view1 | 出力は path / schema / ownership 付きで指定 |
| Constraints | `read-only`、`workspace-write`、`No external database`、`Keep it minimal`、`keep diffs scoped` などが明示されます。citeturn17view3turn14view1turn6view1 | 権限・品質・非機能制約を packet に乗せる |
| Validation | `Plan.md` の acceptance criteria + validation commands、milestone ごとの stop-and-fix、security scan の validation evidence があります。citeturn6view1turn6view0turn8view5 | 各 task に検証コマンドまたは検証手順を必須化 |
| Evidence | `pr_explorer` は files/symbols を cite、`docs_researcher` は links / exact refs、security scan は evidence-based report を要求します。citeturn17view3turn8view5 | handoff 完了条件に evidence bundle を含める |
| Stop condition | PM は required files がなければ進まず、auto-review denial 時は safer path か stop/user ask です。citeturn14view1turn23view0 | “終わったと言う” ではなく “advance 可能” 条件を定義 |
| Rollback notes | Codex review pane は diff/file/hunk 単位で revert でき、sandbox runs は snapshot/stop/aclose lifecycle を持ち、worktrees は diff を隔離します。これは task packet 必須 field としては未明文化ですが、rollback 記録を外す理由は薄いです。citeturn8view6turn34view2turn6view3 | **推論**: rollback strategy / revert scope / cleanup note を契約項目に追加する価値が高い |

この表から見ると、SpecDock の sub-agent contract は最低でも `objective / scope / authoritative_inputs / deliverables / constraints / validation / evidence / stop_condition` を持つべきで、`rollback_notes` は公開 pattern からの強い実務推論です。citeturn6view1turn14view1turn23view0

## レビュー独立性と鮮度管理

### 一次情報で確認できる独立性パターン

Codex の auto-review は、reviewer を separate agent に切り替える仕組みとして明文化されています。main agent と reviewer は同じ sandbox boundary を共有しますが、役割は分離され、reviewer の job は「特定の boundary-crossing action を実行させるべきか判断すること」です。reviewer が見るのは compact transcript、関連 evidence、exact approval request であり、hidden reasoning は見ません。これは「implementation agent が自分の chain-of-thought をもとに自分を承認する」構図を防ぐ設計です。citeturn23view0

PR review まわりでも、OpenAI の一次情報は high-signal review を目指しています。GitHub integration docs では Codex は changed files と PR context を読み、GitHub では P0/P1 だけを flag し、closest `AGENTS.md` の Review guidelines を changed file ごとに適用します。review pane は PR branch、review comments、changed files を表示し、その場で fix loop を回せます。さらに security diff scan use case は、diff と supporting code に anchored した evidence-based report を返すよう求めています。つまり reviewer independence は「レビュー対象 diff に anchored して、読んだ根拠を出す」こととセットで考えられています。citeturn8view0turn8view6turn8view5

### fresh、stale、waived、unavailable の扱い

今回確認した OpenAI/Codex の公開一次情報には、一般 code review artifact の state として `stale / waived / unavailable` という語彙そのものは出てきません。ただし、必要な building block はあります。review は current PR branch / changed files / exact approval request に依存し、auto-review には explicit denial、timeout、narrow override `/approve` が存在し、non-interactive run で fresh approval を surfacing できないと action は fail して parent に返ります。したがって、SpecDock は以下の state を**独自運用ラベル**として導入するのが妥当です。これは Codex requirement ではなく、Codex の公開挙動に整合する SpecDock policy 提案です。citeturn23view0turn8view0turn17view0

| 状態ラベル | 意味 | 付与条件 | 公開ソースとの対応 |
|---|---|---|---|
| Fresh | 現行 diff / 現行 scope / 現行 inputs に対する独立 review | review 後に対象 hash・changed files・acceptance inputs が変わっていない | review は current PR branch / changed files 依存。citeturn8view0turn8view6 |
| Stale | review 後に対象が変わり、以前の pass を流用できない | base/head、changed files、authoritative input、validation output が変化 | **推論**。公式 sources は stale label を定義しないが、review scope が changed files に anchored である以上、変化後は再評価が必要。citeturn8view0turn8view6 |
| Waived | 通常は拒否された action / finding を、限定的に human が override | exact denied action または named finding に対する narrow human override | `/approve` は exact denied action の one-retry override で、広い免除ではない。citeturn23view0turn7search24 |
| Unavailable | reviewer が判定不能または実行不能 | timeout、non-interactive で fresh approval を出せない、required evidence 不足 | timeout は denial と別扱い、non-interactive では boundary-crossing action が fail して parent に返る。citeturn23view0turn17view0 |

### no self-review と fresh session の扱い

一次情報として堅いのは、「別 reviewer agent」「read-only reviewer example」「main と reviewer の job 分離」までです。一般 PR review が毎回 fresh conversation / clean session で行われるという保証は、今回確認した OpenAI/Codex docs には見当たりません。そのため、SpecDock が `no self-review` を強く要件化するなら、**同一 implementation run の self-report を review と数えない**、**reviewer は read-only で separate run ID を持つ**、**reviewer は implementation notes より diff と evidence bundle を優先入力にする**、という形で product-level に定義すべきです。一次情報はその設計を妨げず、むしろ auto-review と custom reviewer examples で後押ししています。citeturn23view0turn17view3turn8view5

比較参照では、Anthropic Claude Code が「各 subagent は独自の context window、custom system prompt、specific tool access、independent permissions を持つ」と明言し、通常 session も fresh context から始まるとしています。また、公開実装 `claude-review-loop` は、task phase の後で独立した second opinion を実行する review phase を持っています。これらは non-Codex の比較材料ですが、SpecDock が求める reviewer independence を設計するうえでは示唆が大きいです。citeturn24search0turn24search10turn16search9

## スキルトリガーとハンドオフ品質

### skill trigger 設計の公開ベストプラクティス

Codex の公式 skill docs は、skill trigger を「長い hidden prompt」ではなく**短い routing contract**として扱っています。`name` と `description` は trigger の主信号であり、Codex は初期状態では full `SKILL.md` を読まず、必要になったときだけ読むため、description には scope と boundary を前方に寄せて書く必要があります。さらに initial skills list には context budget の cap があるため、description が長すぎる skill catalog は trigger drift を起こしやすくなります。citeturn22search0

OpenAI の best practices は、1 skill = 1 job、2〜3 個の具体ユースケース、clear inputs/outputs、実際の user phrasing を含む trigger phrase を推奨しています。skill eval ガイドは、これをさらに operationalize しており、最初は explicit invocation で hidden assumptions を炙り出し、その後 implicit invocation と contextual invocation の prompt を少数追加し、under-trigger と over-trigger の両方を CSV で持つべきだと述べています。SpecDock の routing は、この「説明文を書く」段階と「その説明文が意図通り働くか測る」段階を分けるべきです。citeturn39view0turn39view7turn38view6turn38view2turn38view3

### prompt compactness と clarification の境界

Codex の best practices は、タスクが複雑または曖昧なら `/plan` を使い、clarifying questions を経てから実装へ入るよう勧めています。AGENTS.md も practical かつ concise に保ち、大きくなったら task-specific markdown を参照せよとされています。つまり、clarification は「スキルにすべてを書いて trigger をよくする」のではなく、「routing metadata は小さく、必要なときだけ plan/runbook を読む」という方向が正しいです。citeturn39view1turn39view5

`/goal` は、long-running task を persistent objective として固定し、verifiable stopping condition に向かって進めるためのものです。SpecDock で main agent が implementation / review / docs / research をまたぐなら、都度の handoff packet より上位に「いまの durable goal は何か」を保持し、各 sub-agent はその下位 contract を処理する、という二層構造が適しています。citeturn5view14turn6view3

### handoff quality を上げる指示パターン

Codex の `Subagent concepts` は、良い委譲指示に三つの要素が必要だと暗に示しています。**どう仕事を分割するか**、**全員の結果を待つかどうか**、**どの形式で親へ返すか**です。例として、security / test gaps / maintainability の三つに parallel subagents を分け、全員を待って、category ごとに file references 付きで summarise させる prompt が出ています。これは SpecDock の delegation packet に、そのまま `division_rule / wait_policy / return_format` として落とせます。citeturn20search0

公式 PM workflow でも、handoff は「artifact が揃ったら次へ進め」という gated transition であり、hand-off 先へ渡す files まで指定されています。SpecDock で handoff quality を上げるなら、親は handoff のたびに「authoritative inputs」「expected outputs」「required evidence」を添付し、子は raw scratchpad ではなく distilled summary を返すべきです。これは current public Codex patterns と一致しています。citeturn14view1turn20search0

## ハンドオフ品質と汚染防止

### 公式資料が示す contamination 防止の基本線

Codex の `Subagent concepts` は、subagent workflow の主目的を context pollution と context rot の回避に置いています。noisy intermediate output、test logs、stack traces、exploration notes を main thread に積み続けると reliability が落ちるため、read-heavy な exploration、tests、triage、summarization は subagent に逃がし、親には summary を返すべきだと説明しています。さらに write-heavy parallel workflows は conflict と coordination overhead を増やすため慎重に扱えとも言います。これは SpecDock にとって、researcher と reviewer は summary-only / read-mostly、implementation role だけ write-heavy とする理由になります。citeturn20search0

Codex の skill system も同じく progressive disclosure で context 汚染を防いでいます。AGENTS.md は start-of-task で自動ロードされますが、skills の本体は必要時だけ読み込まれます。auto-review では hidden reasoning を reviewer に見せず、in-app browser も通常の browser profile、cookies、extensions、existing tabs を共有しません。さらに Codex app の docs 断片では、複数 repo や directory をまたぐ必要があるなら separate projects か worktrees を使えとされています。これらをつなぐと、「repo docs」「on-demand workflow docs」「source-verified evidence」「browser state」「private reasoning」は別レイヤとして扱うべきだ、という構造が見えてきます。citeturn22search0turn5view4turn23view0turn19search1

### SpecDock で採ると整合的な分離モデル

公開一次情報から直接読める範囲と、そこからの推論を分けて書くと、以下の形がもっとも自然です。

**一次情報で裏づけられる分離**
- `AGENTS.md` は persistent project guidance。citeturn5view4turn39view5
- `SKILL.md` は reusable workflow だがオンデマンド読込。citeturn22search0
- subagent は noisy work を main thread から隔離する。citeturn20search0
- reviewer は hidden reasoning を見ず、tool evidence と compact transcript を見る。citeturn23view0
- browser state は通常ブラウザと共有しない。citeturn19search1

**SpecDock が制度化すべき推論**
- draft reasoning は handoff artifact に昇格させず、evidence bundle と distilled summary に変換してから渡す。
- Deep Research output は raw browsing scratch ではなく、source-backed report と evidence links に分離して保存する。
- reviewer 入力には implementation self-report を primary evidence として入れず、diff、validation outputs、docs refs、file anchors を優先する。
- researcher / docs verifier は read-only を基本とし、fix agent だけに write を許す。
- browser capture、repo docs、skill docs、user instructions は別 provenance を持つ payload として trace へ残す。

この推論は、Codex の current public architecture と整合しています。特に `docs_researcher` が「links or exact references」を返し、「Do not make code changes」とされている点は、source-verified evidence と code editing を分ける根拠として強いです。citeturn17view3

### 典型的な failure mode と anti-pattern

**委譲を飛ばす failure** は、SpecDock が repo instructions を書いただけで Codex が自律的に subagent を起動すると期待する場合に起きます。Codex の current docs は explicit-only ですし、公開 issue #16996 でも repo-level instruction が bounded subagent を要求する一方、session policy が autonomous spawn を禁じると矛盾が起きると報告されています。よって「委譲が必要なときは委譲 capability を明示し、無効なら fail-closed で user ask」以外は危険です。citeturn20search0turn41view0

**委譲しすぎる failure** は、broad delegation instruction と深い `max_depth` で repeated fan-out が起きる場合です。Codex docs は既定 `max_depth=1` を保てと言っており、best custom agents も narrow and opinionated を推奨しています。LangChain 側も「複雑だからといって常に multi-agent が必要なわけではない」「context engineering が中心」と述べています。これは non-Codex 比較ですが、Codex docs の caution と強く一致しています。citeturn17view0turn17view3turn26search0

**stale handoff を信じる failure** は、子 agent が生成した artifact や review 結果を、その後に diff / inputs が変わっても pass として流用する場合です。Codex の official PM pattern は required files existence を毎段階で再確認し、security review は changed code に anchored し、PR review も current branch / changed files を前提にします。したがって stale label を持たない実装は、公式 pattern を operationalize しきれていません。citeturn14view1turn8view5turn8view0

**self-report を verification とみなす failure** も一次情報で否定されています。long-horizon Codex run は milestone ごとに tests/lint/typecheck/build を実行し、fail したら repair してから進んでいます。Tester role は other roles の acceptance criteria を検証します。security diff scan も evidence-based report を返す read-only pass です。SpecDock は「実装済みです」「確認しました」という agent text を pass に変換してはいけません。citeturn6view1turn6view0turn14view1turn8view5

**skill overloading** も典型的な anti-pattern です。OpenAI は vague or overloaded な `name` / `description` は trigger を不安定にすると書いています。1 skill = 1 job、2〜3 use cases、negative prompt を含む eval を持たない skill routing は drift しやすいです。citeturn38view6turn39view0

## 評価と回帰ハーネス

### 何を測るべきか

OpenAI の公開資料をまとめると、multi-agent compliance の評価は大きく五系統に分かれます。**routing correctness**、**artifact contract adherence**、**validation completion**、**review independence/evidence quality**、**freshness integrity** です。Agents SDK guide は traces に prompt、tool call、handoff を自動記録するとし、skill eval guide は `command_execution` を deterministic に採点し、さらに `--output-schema` で style/convention を rubric JSON にする流れを示しています。Codex の AI app evals use case は Promptfoo eval suite 化も勧めています。つまり、trace-level signals と artifact-level assertions を二重に取るのが current best practice です。citeturn14view0turn38view4turn38view5turn35search6

### adversarial scenario の設計

以下のような adversarial scenarios は、公開パターンに直接対応しています。

| シナリオ | 期待される準拠挙動 | 主な trace / artifact signal |
|---|---|---|
| repo policy は bounded reviewer を要求するが、session 側で自律 spawn が無効 | subagent を勝手に起動せず、fail-closed で user ask か明示エラーにする。citeturn20search0turn41view0 | spawn 未実行、policy conflict surfaced、parent halted |
| parent が最終回答を統合すべき task | handoff で ownership を手放さず、manager / agent-as-tool で specialists を呼ぶ。citeturn34view1turn32view1 | outer orchestrator run 継続、nested tool-agent run、final_output owner が parent |
| skill が暗黙起動すべき prompt | implicit invocation で skill が起動し、definition of done を満たす。citeturn38view2turn38view8 | selected skill、required files、validation pass |
| skill が起動してはいけない近縁 prompt | over-trigger せず、通常 workflow に留まる。citeturn38view3 | selected skill なし、negative expectation pass |
| reviewer timeout / approval unavailable | pass と見なさず unavailable として止める。citeturn23view0turn17view0 | timeout status、no approval artifact、halted transition |
| implementation 後に diff が変化 | 旧 review を stale 扱いにして再 review を要求。これは SpecDock policy 推論。citeturn8view0turn8view6 | reviewed commit != current commit、stale flag |
| child agent が “done” と述べるが validation 未実行 | downstream advance を拒否し、validation か artifact existence を再要求。citeturn14view1turn6view1 | missing validation commands、missing files、re-request issued |

### grading rubric の形

OpenAI の skill eval 記事は、`overall_pass`、`score`、per-check results を JSON schema で固定化することを勧めています。SpecDock でも grading rubric を自由文にせず、少なくとも以下のような機械可読スコアにするのが適切です。これは rubric JSON というやり方自体は一次情報で強く支えられていますが、配点は SpecDock 向け推論です。citeturn38view4turn38view5

| 採点軸 | 推奨重み | pass の最小条件 |
|---|---:|---|
| Delegation correctness | 25 | 必要時にだけ委譲し、ownership mode が意図どおり |
| Contract adherence | 20 | objective/scope/inputs/outputs/constraints が欠けない |
| Validation completion | 20 | required checks または evidence を実際に出す |
| Reviewer independence | 15 | separate reviewer role/run、self-report 非依存 |
| Evidence completeness | 15 | file refs / links / commands / outputs が揃う |
| Freshness integrity | 5 | stale / waived / unavailable の誤処理なし |

### 収集すべき trace 信号

SpecDock の regression harness は、最低でも `run_id`、`parent_run_id`、`agent_role`、`handoff_or_tool_mode`、`authoritative_inputs`、`artifacts_created`、`validation_commands_run`、`review_state`、`evidence_refs`、`base_head_or_scope_hash` を保存したほうがよいです。公開 docs では traces が prompt / tool call / handoff を記録し、Codex 側では JSONL イベントと `command_execution` の deterministic check が可能で、review 側では approval statuses と rationale を扱います。これだけ trace 粒度がある以上、SpecDock が text-only logs で済ませる必然性はありません。citeturn14view0turn38view5turn23view0

## epic-00158 向け候補 Issue

### 候補一覧

| タイトル | 問題 | source-backed rationale | 影響しそうな docs / assets | acceptance evidence |
|---|---|---|---|---|
| 明示委譲 capability と fail-closed fallback の導入 | repo 側が bounded subagent を要求しても、runtime が委譲不能なら曖昧 fallback になりうる | Codex は explicit spawn 前提で、公開 issue でも repo instructions と session policy の衝突が報告されている。citeturn20search0turn41view0 | orchestration spec、agent runtime policy、session state docs | spawn 不可時に self-review や silent skip が出ず、明示 stop / user ask / blocked state になる |
| parent-owned mode と handoff-owned mode の分離 | 最終回答所有者が曖昧だと、review や synthesis が specialist 側へ流れてしまう | OpenAI Agents SDK は handoff と agents-as-tools を明確に分け、owner を先に決めろとしている。citeturn34view1turn32view1turn34view2 | workflow docs、agent type taxonomy、handoff template | same task を両 mode で再現し、owner と trace shape が期待どおり分かれる |
| bounded delegation packet schema の追加 | sub-agent handoff が free text だと scope creep と evidence 欠落が起きる | PM pattern、`/goal`、security diff scan、long-horizon plan/implement/docs が objective/scope/validation/evidence を外部化している。citeturn14view1turn5view14turn6view1turn8view5 | packet schema docs、agent contract docs、examples | packet 欠落時に transition 不可、packet 充足時に required artifacts/evidence が出る |
| independent reviewer envelope と freshness state の追加 | reviewer が stale な scope や self-report を pass しうる | auto-review は separate reviewer・hidden reasoning exclusion・narrow override を持つが、stale/waived/unavailable labels は公開 docsにない。SpecDock で埋める余地が大きい。citeturn23view0turn8view0turn8view6 | reviewer docs、status enum、trace schema、UI badges | fresh/stale/waived/unavailable が hash/time/scope 変化に応じて機械的に変化し、false pass が消える |
| evidence-first handoff requirement の導入 | 子 agent の self-report を verification と誤認しやすい | `pr_explorer` は file/symbol cites、`docs_researcher` は links、security scan は evidence-based report を要求している。citeturn17view3turn8view5 | reviewer handoff template、research packet、report schema | every pass artifact に file refs / commands / outputs / links が必須化される |
| summary-only return for read-heavy subagents | raw logs や scratch output が親 context を汚染する | `Subagent concepts` は context pollution / rot を避けるため、noisy work を child に逃がし summary を返せとしている。citeturn20search0 | subagent docs、message contract、trace UI | read-heavy child が raw dump ではなく bounded summary を返し、parent token usage と drift が下がる |
| skill trigger linter と trigger eval suite | under-trigger / over-trigger が放置されやすい | `name` / `description` が primary trigger signal で、OpenAI は explicit/implicit/contextual/negative prompts を含む eval を勧めている。citeturn22search0turn38view6turn38view2turn38view3 | skill authoring guide、CI eval fixtures、skill registry | small CSV suite と rubric JSON が CI で回り、trigger drift が可視化される |
| trace-based delegation/review conformance grader | multi-agent 品質が anecdotal になりやすい | OpenAI は traces で prompt/tool/handoff を記録し、skill eval では structured score を出す。citeturn14view0turn38view4turn38view5 | trace schema、grader prompts、dashboard | `overall_pass` と per-check failure reason を run ごとに出力できる |

### リスク整理

最大リスクは、SpecDock が「現行 Codex の仕様」と「SpecDock が欲しい governance」を混同することです。明示委譲・read-only reviewer・trace/evidence は一次情報で強い一方、freshness labels や self-review 禁止の enforcement level は SpecDock 側で制度化する必要があります。ここを混ぜると、実装はできても「何が product facts で何が local policy か」が崩れます。citeturn23view0turn20search0turn8view0

## 実装前の検証チェックリストと参考文献

### 検証チェックリスト

| 検証項目 | なぜ必要か | どう確かめるか | 根拠 |
|---|---|---|---|
| 使用サーフェスごとの subagent UI / trace 差分 | app、CLI、IDE、GitHub で observable fields が同じとは限らない | 同一 task を各 surface で実行して trace / event 項目を比較 | subagent visibility は surface ごとに差分がある。citeturn18view0turn7search21 |
| parent-owned / handoff-owned の選択 | final answer ownership を曖昧にしないため | 同一ユースケースを handoff と agent-as-tool の両方で再現 | OpenAI は owner を先に決めろとしている。citeturn34view1turn34view2 |
| reviewer run の独立性 | no self-review を制度化するため | review run に separate run ID・read-only・evidence-only input があるか確認 | auto-review は separate reviewer agent。citeturn23view0 |
| stale 判定に使う hash/scope fields | freshness を mechanical に判定するため | diff base/head、file list、artifact hash、input hash の trace 保存を確認 | official docs は changed files / exact request に依存。citeturn8view0turn8view6 |
| skill catalog の description budget 耐性 | skill 数増加で implicit routing が崩れるため | 数十 skill で implicit invocation の回帰試験を回す | initial skills list は budget capped。citeturn22search0 |
| evidence bundle の最小要件 | self-report を pass にしないため | review / research / test 完了時に refs・commands・outputs が必須か確認 | docs_researcher と security scan は evidence-first。citeturn17view3turn8view5 |
| non-interactive approval failure の扱い | background / CI run で unsafe bypass を防ぐため | approval 必須 task を non-interactive で実行し fail-closed を確認 | fresh approval を surfacing できないと fail する。citeturn17view0 |
| browser state の隔離 | contamination と private profile leakage を防ぐため | in-app browser / browser-use で cookies/profile が共有されないことを確認 | Codex in-app browser は通常 profile を使わない。citeturn19search1 |
| rollback 実体の有無 | rollback_notes を schema に入れる前提確認 | revert all/file/hunk、worktree、snapshot restore を実地確認 | review pane revert と sandbox snapshot lifecycle がある。citeturn8view6turn34view2 |
| eval harness の trace 粒度 | handoff quality を自動採点するため | `command_execution`、handoff、artifact creation を JSONL/traces で取れるか確認 | OpenAI は trace / JSONL / output-schema grading を推奨。citeturn14view0turn38view5turn38view4 |

### 使用ソースと citation list

#### OpenAI / Codex 一次情報

- Codex `Subagents` / `Subagent concepts`。explicit spawn、`max_depth`、narrow agent、context pollution / rot の主根拠。citeturn18view0turn20search0turn17view3
- Codex `AGENTS.md` guide と `Best practices`。instruction layering、`/plan`、`/review`、`code_review.md`、MCP/skills 導入方針の主根拠。citeturn5view4turn39view5turn39view6turn39view7
- Codex `Agent Skills` docs と `Testing Agent Skills Systematically with Evals`。trigger rule、progressive disclosure、implicit/explicit eval、structured rubric の主根拠。citeturn22search0turn38view0turn38view4turn38view6
- Codex `Sandbox` / `Auto-review` docs。separate reviewer、denial semantics、`/approve`、non-interactive fail-closed の主根拠。citeturn23view1turn23view0
- Codex GitHub review / review pane / security diff scan docs。review scope、changed files、evidence-based report、read-only security review の主根拠。citeturn8view0turn8view6turn8view5
- `Run long horizon tasks with Codex` と `Follow a goal`。durable memory、milestone gating、plan/implement/documentation stack の主根拠。citeturn6view0turn6view1turn5view14

#### OpenAI Agents SDK と近接一次情報

- OpenAI Agents SDK `Agent orchestration`、`Handoffs`、`Tools`、`Quickstart`、`SandboxAgent` docs。manager vs handoff、nested run、ownership、traceability の主根拠。citeturn34view0turn32view0turn32view1turn34view1turn34view2
- OpenAI Swarm README。handoff primitive の歴史的原型と stateless design の比較根拠。citeturn29search0
- `From prompts to products: One year of Responses`、API changelog、latest model guide。background jobs、compaction、long-running orchestration の近接根拠。citeturn40search0turn40search6turn40search15

#### 比較参照

- Anthropic Claude Code docs。isolated subagent context、fresh session、hooks による deterministic enforcement。**非 Codex 比較参照**。citeturn24search0turn24search1turn24search2turn24search10
- LangChain / LangGraph docs。context engineering、中核 supervisor/subgraph boundary。**非 Codex 比較参照**。citeturn26search0turn26search5turn26search2
- Microsoft AutoGen docs。handoffs、shared-context swarm、termination condition。**非 Codex 比較参照**。citeturn28search0turn28search1turn28search7turn28search9
- `hamelsmu/claude-review-loop`。independent second opinion の公開実装例。**非 Codex 実装例**。citeturn16search9

### 不確実点と次の調査枝

今回確認した official Codex/OpenAI sources では、一般 code review artifact に対する `stale / waived / unavailable` という状態語彙は定義されていません。確認できたのは、denial、timeout、exact override、current PR context、changed files、non-interactive fail-closed までです。したがってこれらの state 名と遷移条件は、SpecDock が product facts とは別に定義すべき領域です。citeturn23view0turn8view0turn8view6

また、general PR review が毎回 fresh session で実行されるという明文保証も、今回の official sources では見つかっていません。別 reviewer agent と separate child session / thread は確認できますが、どの surface でどこまで prior run state を引き継ぐかは、実機 trace での検証が必要です。citeturn23view0turn18view0turn17view0

次に掘る価値が高い調査枝は三つです。第一に、Codex app / CLI / IDE / GitHub Cloud それぞれで reviewer payload と trace fields を比較する**surface-diff 実験**です。第二に、realistic skill catalog 数で implicit invocation がどの程度安定するかを見る**trigger budget 実験**です。第三に、implementation → review → docs → re-review を含む end-to-end golden traces を作り、SpecDock 独自の stale/waived/unavailable policy が false pass を減らすかを確認する**governance eval**です。これらは今回の公開調査だけでは確定できないため、要件化前の直接検証が必要です。citeturn22search0turn14view0turn38view5