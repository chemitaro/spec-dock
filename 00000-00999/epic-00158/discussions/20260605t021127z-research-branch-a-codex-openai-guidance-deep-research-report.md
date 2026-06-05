# Branch A Codex と OpenAI ガイダンス調査報告

## Executive summary

この報告は、**公開 Web 上の一次情報だけ**を使って、Codex 中心の開発ワークフローをどう堅牢化すべきかを整理したものです。結論を先に言うと、SpecDock が信頼できる Codex ハーネスを作るうえで最も重要なのは、**永続ルールを `AGENTS.md` とチェックイン済み文書に寄せること**、**長時間タスクの継続条件を `/goal`・計画書・進捗ログで外部化すること**、**権限を permission profile / sandbox / approval で明示的に絞ること**、そして **traces → graders → datasets/evals** の順で改善ループを組むことです。OpenAI 自身の docs は、`AGENTS.md` を「自動で読み込まれるエージェント向け README」と位置づけ、Memories は便利な補助層ではあっても、必須ルールの唯一の置き場にしてはいけないと明示しています。citeturn40view4turn10search3turn43view4

**一次情報として最も強い発見**は、Codex が repo 指示を「グローバル → repo root → 現在ディレクトリに近い階層」の順で読み込み、近い階層の指示が後勝ちで上書きされること、かつ結合された instructions には既定で **32 KiB の上限**があることです。したがって、SpecDock の「常時オンの巨大システムプロンプト」設計は、少なくとも現行 Codex の第一級設計とは噛み合いません。短く正確な `AGENTS.md`、必要ならネストした `AGENTS.override.md`、長文は別の task-specific doc に逃がす、という構成が OpenAI の現行推奨に一致します。**推論としての含意**は、SpecDock の source of truth は「セッション記憶」ではなく「ソース管理された repo 文書」であるべき、ということです。更新リスクは中程度です。Codex docs は 2026 年に高速更新されているため、細部は将来変わり得ます。citeturn43view4turn43view2turn40view4turn40view5

**長時間タスクの継続**については、Codex の Goal mode と Responses/Agents 側の compaction が中心です。`/goal` は開始プロンプトと完了条件を兼ねる durable objective であり、OpenAI は「何を達成するか」「何を変えてはいけないか」「どう検証するか」「どこで止まるか」を最初に契約として定義するよう勧めています。さらに、難しい長時間ループでは「短い progress log」を残し、評価スコアや前回の変更点、次の試行を外部化することが信頼性を上げると説明しています。Compaction は現行 OpenAI API で opaque な compaction item を返し、Codex でも長い会話の継続に使われています。**推論としての含意**は、SpecDock では issue ごとに「goal」「plan」「progress log」「verification artifact」をファイルとして残し、会話履歴だけに依存しない設計が最も筋が良い、ということです。更新リスクは中程度です。citeturn25view0turn25view1turn13search0turn36view0turn25view3turn25view2

**権限設計**についての現行一次情報はかなり明確です。Codex ローカル実行では、既定でネットワークはオフ、書き込みは workspace に制限され、approval policy が「どこで止まって聞くか」を決めます。さらに新しい permission profiles は filesystem ルールと network allow/deny を統合する least-privilege 機能ですが、**旧来の `sandbox_mode` 系設定と compose されません**。つまり、SpecDock が新 profile ベース設計に進むなら、legacy sandbox flags と混在させる設計は避けるべきです。`.agents` と `.codex` が writable root 配下で再帰的に read-only 保護される点も重要で、スキルやハーネス設定を agent 自身が勝手に書き換えにくい構造を作れます。更新リスクは中程度です。citeturn37view0turn44view0turn44view1turn44view6turn44view7

**レビューと責務分離**については、Codex 側のコードレビューは GitHub 連携で `AGENTS.md` の Review guidelines を参照でき、PR レビューは P0/P1 に集中するよう設計されています。一方、Subagents docs は「Codex は subagent を明示的に頼まれたときだけ spawn する」と説明しており、Subagents は親 sandbox policy を継承します。したがって、SpecDock で reviewer independence を本当に確保したいなら、単に「レビューしろ」と書くだけでは足りず、**read-only の reviewer custom agent を別定義にし、manager は最終決定だけを持つ**構成が適切です。Agents SDK docs 側でも `agent.asTool()` は manager が責任を持ち続けるパターン、handoff は specialist がその枝を引き取るパターンとして整理されています。更新リスクは中程度です。citeturn21view4turn21view5turn42view0turn42view3turn31view5

**ツール統合・研究境界**については、OpenAI の一次情報は「何を agent loop の内側に置くか」をかなり明示しています。Agents SDK では、public remote server は hosted MCP、local/private server は SDK-managed MCP にして、接続・approval・network boundary を runtime 側が持つのが基本です。Codex app-server は rich client 埋め込み向けで JSON-RPC 2.0 を話し、WebSocket transport は現時点で experimental かつ unsupported と明記されています。ブラウザも、in-app browser は未認証の local/public page 向け、サインイン済み状態が必要な作業は Chrome extension と website approvals 管理の領域です。web search は local task 既定で cached mode であり、OpenAI も prompt injection 低減のため live ではなく cache を既定にしています。**推論としての含意**は、SpecDock では「live web」「signed-in browser」「private MCP」「destructive connector tool」をすべて同じ trust tier に置くべきではない、ということです。更新リスクは中から高めです。app/browser/app-server 周辺は 2026 年にかなり速く変わっています。citeturn33view6turn22view3turn22view2turn20search6turn20search1turn39view2

## Current Codex と OpenAI source map

| Source | Visible date or freshness signal | Surface covered | Evidence strength | Freshness risk | Preview or beta | SpecDock relevance |
|---|---|---|---|---|---|---|
| `Custom instructions with AGENTS.md` docs citeturn43view4turn43view2 | visible page date なし、現行 docs | `AGENTS.md` discovery, precedence, fallback names, byte cap | 高 | 中 | 明示なし | repo 指示の読み込み順と source-controlled guidance の基盤 |
| `Best practices` docs citeturn40view4turn40view5 | visible page date なし、現行 docs | `AGENTS.md` の中身、config layering、review ループ、skills 運用 | 高 | 中 | 明示なし | SpecDock の運用規約・ハーネス標準化に直結 |
| `Prompting` と `Follow a goal` docs citeturn25view0turn25view1 | visible page date なし、現行 docs | Goal mode、定義済み done、長時間タスクの契約 | 高 | 中 | `features.goals` 依存の surface-specific 部分あり | issue 単位の durable goal と milestone 設計 |
| `Compaction` API docs と `Unrolling the Codex agent loop` citeturn13search0turn36view0 | API doc は current、engineering post は 2026 | server-side compaction、opaque compaction item、Codex 自動 compaction | 高 | 中 | API surface は current、実装詳細は進化しうる | context preservation と long-run handoff の根拠 |
| `Agent approvals & security` と `Permissions` docs citeturn44view1turn44view5turn37view0 | visible page date なし、現行 docs | sandbox, approvals, auto-review, permission profiles | 高 | 中 | auto-review や profiles は surface-specific 要素あり | least privilege, reviewer routing, network policy の設計根拠 |
| `Subagents` docs citeturn42view0turn42view3 | visible page date なし、現行 docs | explicit spawn、親 sandbox 継承、custom agent files | 高 | 中 | IDE visibility は “coming soon” | subagent 境界、reviewer/read-only agent 設計 |
| `Agent Skills` docs citeturn41view0turn41view2 | visible page date なし、現行 docs | progressive disclosure、`SKILL.md`、repo/user/admin/system locations | 高 | 中 | 明示なし | prompt packaging と source-controlled workflow reuse |
| `Codex App Server` docs citeturn22view3turn22view2turn22view5 | visible page date なし、現行 docs | JSON-RPC 2.0, stdio/unix/ws, approval elicitations, experimental dynamic tools | 高 | 高 | WebSocket と dynamic tools は experimental | rich client integration の境界、SpecDock client adapter の注意点 |
| Agents SDK docs: sandbox, observability, results, evals, guardrails citeturn12search1turn34view0turn35view6turn32view2 | visible page date なし、現行 docs | harness/compute split、tracing、resumable state、eval loop | 高 | 中 | Sandbox agents は beta citeturn12search1 | Codex 周辺の control plane 設計と regression loop に最重要 |
| `Codex app/features`, `Automations`, `In-app browser`, `Chrome extension`, `Codex web` docs citeturn23view0turn23view4turn20search6turn20search1turn23view6 | current docs、feature-heavy | thread automations、background worktrees、browser boundaries、cloud background tasks | 中〜高 | 高 | browser / cloud は surface-specific | long-running continuity と web research 境界を surface ごとに分けるため |
| OpenAI engineering / cookbook: `Run long horizon tasks with Codex`, `Iterate on difficult problems`, `Agent Improvement Loop`, `Building Reliable Agents with Memory and Compaction` citeturn25view2turn25view3turn24search9turn36view3 | 2025–2026 | 実践 runbook、progress log、artifact-based evaluation、memory boundary | 中 | 中 | cookbook は implementation guidance | SpecDock の実務パターン化に強いが、docs ではなく補助根拠 |
| Open-source Codex repo policy files と GitHub issues citeturn19search0turn17search0turn15search6turn15search2turn15search4 | repo current, issues dated 2025–2026 | reviewer policy, risk taxonomy, contradiction signals | 中 | 高 | 実装変化が速い | “現行 docs を requirement に落とす前の実地検証ポイント” を示す |

この source map から見えるのは、**一次根拠の中心は docs と open-source repo**であり、**cookbook と engineering posts は運用パターンの補強**、**GitHub issues は仕様ではなく矛盾シグナル**として扱うのが妥当だということです。特に `AGENTS.md`、permissions、subagents、app-server、tracing/evals は SpecDock 要件化に直結する一方、browser、auto-review、IDE 表示まわりは変化が速いため、要件固定前の再確認が必要です。citeturn43view4turn37view0turn42view0turn22view3turn34view0turn15search6

## Terminology と Codex workflow primitives

### Terminology

| Term | First-party meaning | SpecDock での実務的な読み替え | Freshness risk |
|---|---|---|---|
| harness | OpenAI は sandbox agents docs で、harness を「agent loop、model calls、tool routing、approvals、tracing、recovery、run state を持つ control plane」と説明しています。citeturn12search1 | SpecDock の orchestrator。モデル本体ではなく、state・approval・routing・audit を司る層 | 低〜中 |
| context | Codex は `AGENTS.md`、skill metadata、会話履歴、tool outputs を prompt chain として積み、必要時に compaction します。skills は progressive disclosure で最初は name/description だけ読みます。citeturn43view4turn41view0 | 常時全文を抱えるのではなく、「必要なときだけロードされる packet 群」 | 中 |
| goal | Goal mode は persistent objective で、goal text は starting prompt 兼 completion criteria です。citeturn25view0 | issue ごとの definition of done を持つ durable contract | 中 |
| compaction | OpenAI API は context を縮約し、opaque な compaction item で prior state を引き継ぎます。Codex でも長い会話で自動 compaction を使います。citeturn13search0turn36view0 | 長大 transcript を捨ててもよい、ただし reviewed artifact は別に残す必要がある | 中 |
| approval | Codex docs では「いつ止まって聞くか」の policy。Agents SDK では interruption と resumable state を返して同じ run を再開します。citeturn44view1turn35view2turn35view6 | side effect 前の明示ゲート。新 turn を始めず “same run resume” する前提で設計 | 中 |
| sandbox | 技術的に何ができるかの境界。workspace write、read-only、network allow などを規定します。citeturn44view1turn37view0 | agent が越えられない実行境界。policy ではなく enforcement | 中 |
| review | GitHub review は PR diff を見て serious issues に集中し、`AGENTS.md` の Review guidelines を参照できます。citeturn21view4turn21view5 | “修正” と切り離された独立評価ステージにすべき | 中 |
| tool/MCP | Agents SDK は hosted MCP を public remote 用、SDK-managed local/private MCP を runtime-owned connection 用と分けています。citeturn33view6 | trust boundary ごとに tool routing を分離し、private surfaces は runtime ownership に寄せる | 中 |
| eval/trace | OpenAI は traces を先に見て、その後 graders / datasets / eval runs に進むよう勧めます。tracing は SDK で default-on です。citeturn34view0turn32view2turn32view3 | “まず運用可視化、次に回帰判定” の順に改善ループを作る | 低〜中 |

### Codex workflow primitives

| Primitive | First-party finding | Codex 向け推奨解釈 | Freshness risk |
|---|---|---|---|
| Repo instructions discovery | Codex は `~/.codex` の global AGENTS から始め、repo root から現在ディレクトリまで 1 directory 1 file で instruction chain を作り、近い階層が後勝ちになります。fallback filenames と `project_doc_max_bytes` も設定可能です。citeturn43view4turn43view2 | root `AGENTS.md` は全体方針、深い階層は package-specific override に限定し、長文は別 doc に分離する | 中 |
| Long-running goals | `/goal` は durable objective で、明確な stopping condition が必要です。OpenAI は checkpoint と短い progress log を勧めています。thread automation は同じ thread context を保った heartbeat に向きます。citeturn25view1turn25view0turn23view4 | SpecDock issue は「goal」「plan」「progress log」を別 artifact 化し、必要なら thread automation で follow-up する | 中 |
| Context compaction and handoff | Codex/Responses は compaction で context を縮約できますが、OpenAI は reviewed artifact を別に残す実践も示しています。Agents SDK では `history` / `lastAgent` / `lastResponseId` / `interruptions + state` を continuation surface として区別しています。citeturn13search0turn25view2turn35view6 | “会話の継続” と “事実の保存” を分ける。保存対象はファイル、会話は compactable | 中 |
| Permission bounding | network は既定 off、Auto preset は workspace 内の read/write/cmd を許し、outside workspace や network は approval。permission profiles は least privilege だが legacy sandbox 設定と混在不可です。citeturn44view5turn44view7turn37view0 | SpecDock は profile-first に寄せ、read-only / workspace / research などの明示 profile を持つ | 中 |
| Tool access routing | skills は implicit/explicit invocation と progressive disclosure。MCP は hosted public と local/private を分離。app-server は rich client 向け、CI や automation は Codex SDK を使う、と docs は分けています。citeturn41view2turn33view6turn22view3 | Skill は workflow packaging、MCP は capability attachment、app-server は UI integration、SDK は orchestration という役割分担にする | 中〜高 |

この節を要約すると、**SpecDock が Codex に合わせるべき単位は「巨大 prompt」ではなく、`AGENTS.md`・skill・goal・plan・permission profile・trace」**です。各 primitive は OpenAI の docs 上でかなり明文化されており、ハーネス設計はそれに沿うほうが将来の surface 変化に追従しやすくなります。citeturn43view4turn41view0turn25view1turn37view0turn34view0

## Best practices for SpecDock

以下は、**一次情報**と、そこから引ける**SpecDock への推論**を分けて整理した実装指針です。

| Area | First-party basis | SpecDock recommendation | Freshness risk |
|---|---|---|---|
| Context packet design | OpenAI は `AGENTS.md` を常時 guidance、skills を progressive disclosure、long task では progress log と reviewed artifact を勧めています。citeturn40view4turn41view0turn25view3turn25view2 | issue 開始時に「goal packet」「plan packet」「verification packet」「research packet」をファイル化し、会話ではなく packet を読む前提にする | 中 |
| Skill and subagent boundary design | Skills は one job に絞るべきで、description に trigger scope を明示すべきです。Subagents は explicit spawn で、custom agents は narrow and opinionated が推奨です。citeturn41view2turn41view2turn42view3 | Skill は再利用ワークフロー、subagent は責務分離に使う。曖昧な万能 subagent は作らない | 中 |
| Spec-manager responsibilities | Agents SDK の `agent.asTool()` は manager が最終責任を維持するパターンです。Goal mode も “contract first” を要求します。citeturn31view5turn25view1 | spec-manager は goal 定義、packet 配布、delegation、gate 判定、final judgment を持ち、実装そのものは worker に寄せる | 低〜中 |
| Reviewer independence | GitHub review は serious issues に集中し、review guidance は `AGENTS.md` から読めます。Subagents は read-only sandbox を個別 custom agent に設定可能です。citeturn21view4turn42view3 | reviewer は read-only custom agent とし、fix 権限を与えない。manager が findings を受けて修正 agent に handoff する | 中 |
| Browser and web research boundaries | local Codex の web search 既定は cached。results は untrusted と扱うべきです。in-app browser は認証フロー非対応、signed-in 作業は Chrome extension と website approvals で扱います。citeturn39view2turn20search6turn20search1 | default は cached か disabled。live web と signed-in browser は明示的 policy と approval を経た時だけ許可する | 高 |
| Issue start and finish gates | OpenAI は難タスクで plan first、goal、milestone ごとの validation、artifact inspection を勧めています。citeturn26search0turn25view2turn25view3 | 開始 gate は「goal 明確化・plan 承認・permission profile 決定」。終了 gate は「検証コマンド成功・review 完了・trace 残存・artifact 更新」 | 中 |
| Reports and trace artifacts | Agents SDK は tracing default-on。OpenAI は traces から始め、次に graders/datasets/evals と言います。Codex には plaintext TUI log と session JSONL の監査経路もあります。citeturn34view0turn32view2turn43view1turn39view2 | issue ごとに final report、verification log、trace link、eval sample を残す。trace がない run は “再現不能” とみなす | 低〜中 |
| Source-controlled knowledge accumulation | OpenAI は team guidance を `AGENTS.md` / checked-in docs に置き、memory は stable preferences や workflow lessons 用としています。cookbook でも memory は fact DB にするな、と明示しています。citeturn10search3turn36view3 | “知識の蓄積” は repo の docs / skills / review guides に寄せる。memory は補助的 personalization に限定する | 低〜中 |

特に重要なのは、**SpecDock の context packet を source-controlled doc として残す**ことです。OpenAI の current guidance は、goal・progress log・reviewed artifact・`AGENTS.md`・skills という複数の checked-in or durable artifact を前提にしており、暗黙メモリや transient thread history を唯一の正とする方向ではありません。citeturn25view2turn25view3turn40view4turn10search3turn36view3

## Anti-patterns と contradiction signals

### Anti-patterns

| Anti-pattern | Why it conflicts with current guidance | Better pattern | Freshness risk |
|---|---|---|---|
| Overlong always-on prompt | `AGENTS.md` は practical かつ concise が推奨で、instruction chain には byte cap もあります。skills も初期リストが context の約 2% に抑えられます。citeturn40view4turn43view4turn41view1 | 常駐情報は短い `AGENTS.md`。長い手順は skills / plan docs / linked markdown に分割 | 中 |
| Hidden session memory as source of truth | OpenAI は Memories を local recall layer と位置づけ、必須 guidance は `AGENTS.md` に置けと言っています。cookbook でも Memory は unreviewed fact DB にするな、と明示しています。citeturn10search3turn36view3 | team-shared facts は checked-in artifact。memory は process lessons と preferences のみ | 低〜中 |
| Mixed read/write/review permissions | review と fix を同じ権限制御で混ぜると independence が弱くなります。Subagents は親 sandbox を継承しつつ、custom agent ごとに read-only 指定も可能です。citeturn42view3turn21view4 | reviewer は read-only custom agent、fixer は workspace-write、manager は gate 判定のみ | 中 |
| Unsupported tool assumptions | app-server WebSocket は experimental/unsupported、dynamic tools も experimental。in-app browser は未認証ページ用です。citeturn22view3turn22view5turn20search6 | stdio/unix transport を優先し、browser auth 前提の自動化は Chrome extension か別経路で扱う | 高 |
| Benchmark overfitting without artifacts | OpenAI は traces を先に見て、hard task では stopping rule と artifact inspection を入れろと言っています。citeturn32view2turn25view3 | “スコアだけ” でなく、artifact と trace をセットで回帰判定する | 低〜中 |
| Stale or unverifiable context | Codex は instruction chain を毎 run で再構築し、長時間ループでは progress log が handoff point になります。citeturn43view1turn25view3 | resume 可否は chat ではなく packet / log / report の存在で判定する | 中 |

### Surface gaps と contradiction signals

| Topic | First-party position | Contradiction or gap signal | What SpecDock should do |
|---|---|---|---|
| Auto-review persistence | docs は `approvals_reviewer = "auto_review"` を示し、eligible approvals を reviewer agent に流すと説明しています。citeturn44view3turn44view5turn20search13 | 2026-05 の公開 issue では、Desktop が compaction/resume 後に `auto_review` を落とすと報告されています。citeturn15search6 | hard requirement 化前に、対象 surface/version で compaction 後も reviewer routing が維持されるか実測する |
| Review guidance parity | GitHub review docs は `AGENTS.md` Review guidelines を使うと言います。citeturn21view4 | 2025-10 の公開 issue では `/review` が AGENTS を無視すると報告されました。citeturn15search2 | CLI/app/GitHub review の各 surface で、同じ review guide が効くかテスト PR で検証する |
| Implicit delegation | Subagents docs は「explicitly ask したときだけ spawn」と明言しています。citeturn42view0 | 2026-04 issue では、repo 指示と session policy の衝突が報告されています。citeturn15search4 | AGENTS だけに delegation を委ねず、manager prompt で明示 spawn を行う |
| IDE visibility | docs は subagent activity が app/CLI に出て、IDE visibility は “coming soon” と記載しています。citeturn42view0 | 2026 changelog でも handoff / subagent navigation 修正が続いています。citeturn26search5 | IDE を audit UI の主戦場にしない。少なくとも初期は app/CLI/traces を主監査面にする |
| Browser surface | in-app browser は未認証用、signed-in ブラウザは Chrome extension で approvals 管理です。citeturn20search6turn20search1 | surfaceごとの trust model が異なるため、同一 policy では扱えません。 | web research policy を cached/live/browser-auth に三分し、同じ “web” にまとめない |
| Config model | CLI・IDE・app は共有 config layers を持ちますが、permission profiles と legacy sandbox settings は compose しません。citeturn40view5turn37view0 | 古い config の混在で意図しない effective policy になり得ます。 | SpecDock docs では profile-first か legacy-first かを明示し、移行期は両方を混ぜない |

ここで重要なのは、**contradiction signals は docs を否定する証拠ではなく、“導入前に実測すべき不安定点” の印**だということです。SpecDock が requirement を固めるときは、docs を正として採用しつつ、issues が示す箇所だけを smoke test で裏取りするのが合理的です。citeturn44view3turn21view4turn42view0turn15search6turn15search2turn15search4

## Candidate follow-up issues for epic-00158

| Title | Problem | Source-backed rationale | Likely impacted files or docs | Acceptance evidence |
|---|---|---|---|---|
| Codex instruction chain を `AGENTS.md` 中心に標準化する | repo guidance が会話や人依存に散っていると再現性が落ちる | Codex は `AGENTS.md` を自動読込し、近い階層が後勝ちです。review も `AGENTS.md` の Review guidelines を参照できます。citeturn43view4turn21view4 | `AGENTS.md`、必要なら nested `AGENTS.override.md`、`docs/code_review.md` | `codex --ask-for-approval never "Show active instructions"` で期待順序が出る。GitHub の `@codex review` が review guide を反映する |
| Issue context packet と progress log を source-controlled artifact 化する | 長時間タスクが thread history 依存だと compaction や handoff に弱い | OpenAI は goal・progress log・milestone validation・Documentation.md 型 audit log を勧めます。citeturn25view1turn25view2turn25view3 | `docs/specdock/goal-template.md`、`docs/specdock/progress-log-template.md`、`PLANS.md` テンプレート | 途中中断後でも packet と log だけで再開でき、milestone ごとの検証結果が残る |
| Read-only reviewer と docs-researcher を custom agent として分離する | 実装 agent がそのまま自己レビューすると境界が曖昧 | custom agents は narrow and opinionated が推奨で、subagent ごとに read-only sandbox を持てます。citeturn42view3 | `.codex/agents/reviewer.toml`、`.codex/agents/docs-researcher.toml`、`.codex/config.toml` | reviewer が patch を出さず findings のみ返す。docs-researcher が docs 根拠だけ返す |
| Legacy sandbox 設定から permission profiles へ移行する | legacy と profile の混在は effective policy を曖昧にする | permission profiles は least privilege 向けだが、旧 sandbox 設定と compose されません。citeturn37view0 | `.codex/config.toml`、導入ガイド、必要なら `requirements.toml` 例 | effective config に legacy sandbox 設定が残らず、`*.env` deny・domain allowlist が効く |
| Trace-first の regression loop を導入する | “うまく動いた気がする” では回帰に弱い | OpenAI は traces を先に見て、その後 graders / datasets / eval runs に進めと言っています。tracing は SDK で default-on です。citeturn34view0turn32view2turn32view3 | orchestration code、`evals/`、CI/nightly docs、trace naming convention 文書 | 代表 workflow が trace を出し、grader 付き eval が定期実行され、差分比較できる |
| Web / browser / MCP research boundary policy を明文化する | “調べる” 行為の trust tier が混在しやすい | web search 既定は cached、結果は untrusted。in-app browser は未認証向け、signed-in は Chrome extension。MCP は hosted と local/private を分けるべきです。citeturn39view2turn20search6turn20search1turn33view6 | `AGENTS.md`、`docs/specdock/research-policy.md`、`.codex/config.toml`、必要なら `requirements.toml` | default が cached/disabled になり、live web・signed-in browser・private MCP には明示 policy がある |
| App-server / MCP integration contract を実験機能に依存させない | client 実装が unstable transport 依存だと保守が壊れる | app-server は rich client 向けだが、WebSocket は experimental/unsupported、dynamic tools も experimentalです。CI/automation は SDK を使うべきと docs が分けています。citeturn22view3turn22view5 | integration ADR、client adapter、schema generation scripts、transport docs | stdio/unix transport で動作し、version pin + schema regeneration 手順が定義されている |

これらは **“今すぐ書き換えろ” ではなく、“first-party guidance に照らして優先度が高い hardening issue”** です。特に上から四つは、SpecDock が Codex を安定運用するための基盤整備として妥当性が高いです。citeturn43view4turn37view0turn42view3turn34view0

## Verification checklist, uncertainties, and sources

### Verification checklist for Codex before implementation

| Verify this finding | Why verify now | How to verify |
|---|---|---|
| `AGENTS.md` layering and closest-file precedence | ハーネスの source of truth だから | root と subdir に test `AGENTS.md` / `AGENTS.override.md` を置き、Codex に active instructions を要約させる。docs 上はこの振る舞いです。citeturn43view4 |
| Review path actually honors review guidance on your target surface | GitHub review docs と CLI historical issue に差があるため | GitHub `@codex review`、app `/review`、CLI `/review` それぞれで同じ指示が効くか test PR で比較する。citeturn21view4turn15search2 |
| `/goal` and `/plan` availability in chosen surface | feature gate や surface 差で使えないと長時間契約が崩れる | CLI / app / IDE の slash command list を確認し、必要なら `features.goals` を明示有効化する。citeturn25view0turn28search6 |
| Auto-review persistence across compaction / resume | public issue が破綻を示しているため | `approvals_reviewer = "auto_review"` で長時間スレッドを作り、compaction 後の approval が reviewer に残るかを見る。citeturn44view3turn15search6 |
| Permission profiles are active and legacy sandbox settings are absent | 混在時に意図しない effective policy になるため | effective config を見て `default_permissions` / `[permissions]` のみ使い、`sandbox_mode` 系が同一経路に残っていないことを確認する。citeturn37view0 |
| Read-only protection of `.agents` / `.codex` in your actual OS/runtime | hardening 前提が環境依存で崩れないか確認するため | workspace-write で `.agents` と `.codex` への書き込み試行を行い、保護が働くか観測する。citeturn44view6 |
| Subagent spawn semantics in your workflow | docs は explicit ask 必須としているため | manager prompt に明示 spawn 指示を入れた場合だけ subagent が起動すること、AGENTS だけでは自動 fan-out しないことを確認する。citeturn42view0turn15search4 |
| App-server transport and schema stability | WebSocket / dynamic tools は experimental | stdio か unix transport のみを採用し、`generate-ts` / `generate-json-schema` で version-aligned schema を出して commit する。citeturn22view3 |
| Web search / browser trust tiers | research policy の事故を防ぐため | cached/live/disabled、in-app browser、Chrome extension の各行為を別々に smoke test し、approval と auth の境界を確認する。citeturn39view2turn20search6turn20search1 |
| Trace and eval loop actually capture your critical workflows | regression hardening の基礎だから | representative workflow を 3 本以上流し、trace が出ること、grader が failure mode を拾うこと、dataset-based rerun が可能なことを確認する。citeturn34view0turn32view2turn32view3 |

### Uncertainties and next research branches

現時点で残る不確実性は四つあります。第一に、Codex docs の多くは visible page date を持たないため、**内容は current でも差分検知が難しい**ことです。これは changelog 監視で補うべきです。citeturn26search5turn10search4

第二に、**surface parity がまだ揃っていない**点です。subagent visibility は app/CLI 中心で、IDE は追随中です。review・browser・auto-review も surface ごとの成熟度差があります。citeturn42view0turn20search6turn20search1turn44view3

第三に、**preview / beta / experimental** な面があります。Agents SDK sandbox agents は beta、Chronicle は opt-in research preview、app-server WebSocket と dynamic tools は experimental です。これらに依存する requirement は、固定仕様として扱わず “conditional capability” に留めるべきです。citeturn12search1turn10search1turn22view3turn22view5

第四に、**公開 issue が示す contradiction signals** です。auto-review 継続性、`/review` の AGENTS 遵守、implicit delegation の扱いは、採用前に対象 version で再現確認したほうが安全です。citeturn15search6turn15search2turn15search4

次の research branch として価値が高いのは、`execution plans guide` と Codex SDK 周辺をさらに掘り、SpecDock の packet 形式と CI 回帰基盤をどう接続するかを詰めることです。また、Managed configuration と enterprise governance を使う前提があるなら、`requirements.toml` でどこまで Codex 利用を中央統制するかの別枝調査が必要です。citeturn26search0turn38view0turn28search14

### Sources used and citation list

この報告の主要根拠は次の公開一次情報です。技術仕様の中心は docs、行動パターンの補強は OpenAI engineering posts と cookbook、矛盾シグナルは open-source repo / issues です。

| Source class | Source | Notes |
|---|---|---|
| Official Codex docs | `Custom instructions with AGENTS.md` citeturn43view4turn43view2 | instruction chain, precedence, fallback names, byte cap |
| Official Codex docs | `Best practices` citeturn40view4turn40view5 | concise AGENTS, config layering, testing/review, skills |
| Official Codex docs | `Prompting` / `Follow a goal` / `Automations` citeturn25view0turn25view1turn23view4 | goal mode, durable prompt design, thread automation |
| Official Codex docs | `Agent approvals & security` / `Permissions` citeturn44view1turn44view5turn37view0 | sandbox, approvals, auto-review, least privilege |
| Official Codex docs | `Subagents` / `Skills` / `App Server` citeturn42view0turn42view3turn41view0turn22view3 | subagent boundaries, skill packaging, rich client protocol |
| Official Codex docs | `Codex app features` / `In-app browser` / `Chrome extension` / `Codex web` citeturn23view0turn20search6turn20search1turn23view6 | worktrees, browser trust boundaries, cloud background tasks |
| Official OpenAI API docs | `Compaction` / Agents SDK `Sandbox agents` / `Integrations and observability` / `Results and state` / `Guardrails and human review` / `Evaluate agent workflows` citeturn13search0turn12search1turn34view0turn35view6turn35view2turn32view2 | harness/compute split, compaction, resumable state, traces, evals |
| OpenAI engineering posts | `Unrolling the Codex agent loop` / `Run long horizon tasks with Codex` / `Harness engineering` citeturn36view0turn36view1turn25view2turn24search1 | Codex harness concepts, long-run runbook patterns |
| OpenAI Cookbook | `Build an Agent Improvement Loop with Traces, Evals, and Codex` / `Building Reliable Agents with Memory and Compaction` citeturn24search9turn36view3 | practical eval flywheel, memory boundary, reviewed artifacts |
| Open-source repo and issue signals | `openai/codex` repo, guardian policy, public issues on auto-review / AGENTS / subagent conflicts citeturn16view0turn19search0turn17search0turn15search6turn15search2turn15search4 | implementation evidence and contradiction signals only |

総合すると、**Codex 中心の reliable workflow は、repo instructions・goal contract・checked-in artifacts・least privilege・trace/eval loop を組み合わせた “外部化されたハーネス” に寄せるべき**であり、**暗黙 memory、長大 prompt、混在権限、未検証の surface parity に依存すべきではない**、というのが現在の OpenAI/Codex 一次情報から引ける最も堅い結論です。citeturn43view4turn25view1turn37view0turn34view0turn10search3