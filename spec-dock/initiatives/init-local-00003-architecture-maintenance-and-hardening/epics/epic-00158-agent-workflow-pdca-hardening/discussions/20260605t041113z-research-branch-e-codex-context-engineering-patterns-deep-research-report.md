# Agent Workflow PDCA Hardening 調査報告

## 研究要約

### エグゼクティブサマリー

2026年6月5日時点の公開一次情報を総合すると、Codex中心の長時間・多エージェント開発を安定化する鍵は、「大きいプロンプト」ではなく「小さいが更新可能な外部化状態」にあります。OpenAI/Codexの一次資料は、`AGENTS.md` による repo ローカル指示、`/plan` と `/goal` による明示的な完了契約、subagent/custom agent による雑音分離、`/compact` や `/responses/compact` による圧縮、skills による反復ワークフローの再利用、そしてレビュー済み成果物を事実の記録にする設計を一貫して支持しています。つまり、SpecDock が強化すべきなのは「会話に依存した記憶」ではなく、「repo に残る仕様・計画・進捗・証拠・引継ぎ」の体系です。 citeturn7view0turn19view1turn23view3turn7view4turn18view1turn25view7

一次情報から見える最重要原則は五つあります。第一に、指示は `system/developer/user/assistant` の階層を持ち、Codex では repo 指示が `AGENTS.md` 群として root-to-leaf で注入され、近い階層が強く効きます。第二に、長時間作業は thread の会話記憶に頼るより、`PLANS.md`、`Documentation.md`、running log、memo、handoff file などの durable artifact に状態を出す方が堅牢です。第三に、subagent は read-heavy な探索・テスト・トリアージには有効ですが、write-heavy 並列編集にはコンフリクトと文脈汚染のリスクがあります。第四に、memory は「次回どう働くか」を助ける用途に限定し、調査事実や結論は常に引用つき artifact に書くべきです。第五に、private connector、browser state、public web、repo docs は信頼境界が異なるため、同じ “context” として混ぜるのは危険です。 citeturn18view0turn21view5turn10search1turn25view6turn15view0turn35view1

SpecDock 向けの実装含意としては、少なくとも repo-root `AGENTS.md` と深い階層の override、Goal/Plan/Implement/Progress/Evidence/Handoff の分離、freshness 付き artifact reference、subagent への bounded contract、resume 時に必要な最小 packet、memory と reviewed artifact の責務分離、source scope を制御する trust matrix が必要です。逆に、アンチパターンは「全ドキュメントを最初から流し込む」「古いチャット要約を SoT 扱いする」「browser history や connector 取得結果を暗黙記憶として持ち回る」「reviewer に raw tool history や実装者の思考過程をそのまま渡す」「stop condition を定義せず keep going させる」ことです。 citeturn33view0turn25view1turn24view7turn28view4turn15view0turn23view6

### ソースマップ

| ソース | 日付・鮮度シグナル | カバー面 | 証拠強度 | SpecDock との関連 |
|---|---|---|---|---|
| OpenAI Developers「Custom instructions with AGENTS.md」 | 現行 docs、2026年時点 | repo 指示 discovery、override、byte cap、fallback 名 | 最上位の一次情報 | repo-governed instruction hierarchy と byte budget 設計の直接根拠。 citeturn7view0turn8view2turn8view6 |
| OpenAI Developers「Best practices」 | 現行 docs | prompt 構造、plan mode、AGENTS の中身、session controls | 最上位の一次情報 | Goal/Context/Constraints/Done when と `/plan`・`/compact`・`/resume` などの運用原則。 citeturn19view1turn19view5 |
| OpenAI Developers「Subagents」「Subagent concepts」 | 現行 docs | parallel delegation、custom agents、context pollution/rot | 最上位の一次情報 | multi-agent delegation の使い所、bounded task、write-heavy 並列の注意。 citeturn7view4turn10search1turn9view1turn9view6 |
| OpenAI Developers Blog「Run long horizon tasks with Codex」 | 2026-02-23 | durable project memory、milestone validation、worktrees | 一次情報だが blog | SpecDock の PDCA artifact stack と progress log 設計の実例。 citeturn21view0turn21view5 |
| OpenAI「Unrolling the Codex agent loop」 | 2026年公開 blog | role hierarchy、prompt assembly、tool boundary、auto compaction | 一次情報だが blog | Codex 実行時に何が input に入るか、何が sandbox 管轄外かの理解に必須。 citeturn18view0 |
| OpenAI Cookbook「Using Goals in Codex」 | 2026-05-09 | durable objective、verification surface、blocked stop condition | 近一次情報 | Goal ベースの completion contract を packet schema に落とす根拠。 citeturn23view3turn23view6 |
| OpenAI Cookbook「Build iterative repair loops with Codex」 | 2026-05-11 | structured phase handoff、review/repair/validate loop | 近一次情報 | bounded input/output の手本。handoff packet と evidence delta の雛形。 citeturn7view9 |
| OpenAI Cookbook「Building Reliable Agents with Memory and Compaction」 | 2026-05-01 頃の cookbook surface | compaction、memory、reviewed artifact as SoT | 近一次情報 | memory を事実 DB にしない原則と reviewed memo を SoT にする根拠。 citeturn13view0turn25view6turn25view7 |
| OpenAI Agents SDK docs「Handoffs」「Sessions」「Context」 | 現行 docs | input_filter、nested history、session memory、local-only context | 一次情報 | multi-agent handoff と app state / model-visible state の切り分けに重要。 citeturn27view0turn27view1turn27view2 |
| OpenAI Developers「Codex Prompting Guide」 | 2026-02-25 | AGENTS injection、compaction、tool preferences | 近一次情報 | direct API / Codex-like harness を作る場合の context engineering 実務に有用。 citeturn18view1turn32view4 |
| OpenAI Developers「Codex Chrome extension」「Chronicle」「Your data」 | 現行 docs | browser state、history、memories、retention | 一次情報 | trust boundary と privacy boundary の基礎。 citeturn15view0turn14search0turn11view6 |
| `openai/skills` repo と bundled skills | main branch の公開 repo | trigger rules、scope layering、context budget、connector priority | 一次に近い公開実装例 | skill design、mixed-scope routing、connector vs web の境界、簡潔性の設計指針。 citeturn35view0turn35view1turn35view2turn35view4 |

## Codex と OpenAI の一次情報

### 指示階層とリポジトリ文脈

**一次情報:** OpenAI の公開説明では、Responses 系の役割優先度は `system > developer > user > assistant` です。Codex はこれをベースに prompt を組み立て、`model_instructions_file` か bundled な base instructions を `instructions` に入れ、そのうえで sandbox/approval に関する developer message、`AGENTS.md` 群や skills などの user message、environment context を追加します。SpecDock が “instruction hierarchy” を要件化するなら、この優先度と Codex の実際の prompt assembly を前提にすべきで、repo ローカル文書だけで system/developer 指示を上書きできる設計にはしない方が整合的です。 citeturn18view0

**一次情報:** `AGENTS.md` は Codex が作業前に読む repo 指示の標準面です。Codex は `$CODEX_HOME` の global guidance を読んだ後、project root から current working directory まで降りながら各ディレクトリで `AGENTS.override.md`、`AGENTS.md`、`project_doc_fallback_filenames` に列挙した fallback 名を探し、各ディレクトリにつき最大1ファイルだけ取り込みます。結合順は root-to-leaf で、より近いディレクトリの指示が後ろに入るため実質的に優先されます。SpecDock では、repo 全体規約とサブツリー規約を分ける際、この挙動にそのまま寄せるのがもっとも摩擦が少ないです。 citeturn7view0turn8view6turn32view2turn32view3

**一次情報:** `AGENTS.md` の総量には既定で 32 KiB の上限があり、docs では `project_doc_max_bytes` の既定値が 32 KiB と説明されています。OpenAI の公開 GitHub issue には、この制限で `AGENTS.md` が無警告で切り詰められたという報告もあります。したがって SpecDock は、巨大な単一 instruction file を前提にせず、repo-root の要約とサブツリー別 override、そして必要時だけ読む詳細文書へのポインタに分けるべきです。これは単なる最適化ではなく、silent truncation リスクを減らす hardening です。 citeturn8view2turn4search0

**一次情報:** Codex の best practices は、良い prompt の最小構造として Goal、Context、Constraints、Done when の四点を推奨し、複雑な作業では `/plan` を使って実装前に計画を立てるよう勧めています。また `AGENTS.md` に載せる内容として、repo layout、build/test/lint commands、engineering conventions、do-not rules、そして “what done means and how to verify work” が明示されています。SpecDock では repo 指示を「規約集」にせず、「検索ルータ兼検証ルータ」にする方が Codex の設計思想に合います。 citeturn19view0turn19view1

### カスタム設定とスキル

**一次情報:** Codex の changelog では 2026-01-14 に “Custom prompts are now deprecated. Use skills for reusable instructions and workflows instead.” と明示されています。さらに skills は `~/.codex/skills` に置けば全 repo で、repo 内に置けばチーム共有で使えます。OpenAI の blog でも skill は `SKILL.md` に optional な `scripts/`、`references/`、`assets/` を持つ small package と説明され、「up front の context bloating を避けつつ richer instructions を持てる」手段として位置付けられています。したがって、その場限りの運用知識を永続化したいなら custom prompt ではなく skill に寄せるべきです。 citeturn5search4turn7view5turn11view0turn11view1

**公開実装例:** `openai/skills` の system skill では、skills は specialized knowledge / workflows / bundled resources を与える self-contained folder とされつつ、「context window is a public good」「Codex はすでにかなり賢いので、本当に必要な情報だけ足す」と強調されています。また threat-model skill の description は「明示的に threat model を頼まれたときだけ trigger し、一般的な architecture summary では trigger しない」と書かれており、良い skill description は trigger rule を狭く明確に定義することが分かります。SpecDock の skill 設計でも、手順説明より trigger 条件と除外条件を先に固定する方が drift を減らせます。 citeturn35view2turn35view4

**公開実装例:** `openai/skills` の `openai-docs` skill は scope layering の product map を持ち、one-off 制約は prompt/thread、durable repo conventions は `AGENTS.md`、trusted repo の Codex defaults は project `.codex/config.toml`、private workspace data は MCP server or app connector、mechanical enforcement は hook、定期実行は automation に置くべきだと整理しています。これは Codex/OpenAI 自身の公開 skill が採用している scope 分離であり、SpecDock の “何をどこに置くか” の設計原則として非常に有用です。 citeturn35view1

### ツール境界と長時間実行

**一次情報:** OpenAI の “Unrolling the Codex agent loop” は、Codex が sandbox を developer message として shell tool にだけ適用し、MCP など他ツールには Codex の sandbox が効かず、それぞれが独自の guardrail を担うと説明しています。Config reference でも app/connector tool には `destructive_hint` と `open_world_hint` に対する allow/deny があり、approval reviewer を `auto_review` にする設定もあります。つまり SpecDock が Codex-like harness を設計するなら、「tool は全部同じ trust 境界」という設計は誤りで、repo shell、connector、browser、web を別ポリシーに分ける必要があります。 citeturn18view0turn17view0turn17view1turn17view6

**一次情報:** Chrome extension docs は、Chrome tasks は signed-in browser state を使うため in-app browser より強力だが、page content を untrusted context として扱い、browser history は sensitive telemetry・internal URLs・search terms を含み得て、関連エントリが Codex の task context に取り込まれうると警告しています。OpenAI は separate complete record を保存しない一方、thread に入った page text、screenshots、tool calls、summaries などは OpenAI data controls の対象になります。SpecDock では browser state と browser history を SoT に近づけない設計が必要です。 citeturn15view0

**一次情報:** 長時間実行については、Codex 側では `/goal`、`/plan`、`/resume`、`/fork`、`/side`、`/compact` が thread 運用の基本面であり、Goal は persistent objective を thread に貼り付ける completion contract です。API 側では background mode が長い multi-search や reasoning task に推奨され、Responses API / Conversations API / previous_response_id / client-side sessions など複数の state 管理面があります。SpecDock が Codex を直接使うか、Agents SDK/Responses API 上に独自 orchestration を置くかで、使う durability primitive は変わりますが、「長時間タスクには thread/state object と explicit resume point が必要」という点は共通です。 citeturn20view0turn23view3turn11view5turn11view7turn27view1turn30view0

### 制約と未確定点

**一次情報と公開実装例:** いくつかの重要点は “現時点では使えるが要確認” です。subagents は current Codex releases で default enabled ですが、Codex は明示的に依頼されたときだけ spawn し、トークン消費も増えます。nested handoffs は Agents SDK では opt-in beta で default off です。IDE Extension での subagent visibility は “coming soon” とされている docs もあります。さらに `@include` で AGENTS を composable にする仕組みは 2026-04-10 時点では GitHub issue 上の提案で、公式 shipped feature としては扱えません。SpecDock はこれらを requirement の前提にせず、実機検証で surface/version を固定すべきです。 citeturn7view4turn28view1turn4search3

## コンテキスト設計の実装パターン

### ソースオブトゥルース階層

**推論だが一次情報に強く支えられる整理:** Codex向けの source-of-truth hierarchy は、少なくとも次の五層に分けると衝突が減ります。第一層は prompt/thread の one-off 制約。第二層は repo-root と subtree の `AGENTS.md`。第三層は durable objective 文書で、長時間タスクなら Goal、`Prompt.md`、`PLANS.md`、`Implement.md` のような実装・検証契約。第四層は progress log / evidence ledger / status doc。第五層は reviewer-facing memo や `codex_handoff.md` のような reviewed artifact です。OpenAI の公開 skill は mixed-scope request をこの層に分けろと書いており、long-horizon blog と ExecPlan guide は durable docs を繰り返し参照させる設計を採っています。 citeturn35view1turn21view5turn22view0turn13view3

**一次情報:** OpenAI の long-horizon 実例では `Prompt.md` が spec + deliverables、`Plan.md` が milestones + validation、`Implement.md` が runbook、`Documentation.md` が shared memory and audit log でした。Cookbook の ExecPlan も「現 working tree と単一の plan file だけを持つ novice が再開できる self-contained living document」を要求しています。つまり durable planning artifact は “説明用文書” ではなく “再開可能な実行状態” であるべきです。SpecDock は SRS/ADR とは別に、agent-run specific の self-contained living document を持つ方がよいです。 citeturn21view5turn22view0

### Context Packet

**推論:** 一次情報を合成すると、SpecDock の context packet は “現 turn に投影する最小状態” であり、Goal の六要素、running log、current milestone、evidence reference、blocked condition を含むべきです。特に Goal cookbook は outcome、verification surface、constraints、boundaries、iteration policy、blocked stop condition を明示しており、long-running use case は current best scores / last change / eval delta / next try を log に残すよう求めています。よって、以下のような packet が最小公倍数です。 citeturn23view6turn33view0

```yaml
context_packet:
  packet_version: 1
  task_id: epic-00158
  objective: >
    何を終わらせるのか
  verification_surface:
    - command: ...
    - artifact: ...
  constraints:
    - ...
  boundaries:
    repos: [...]
    paths_in_scope: [...]
    tools_allowed: [...]
    tools_denied: [...]
  current_state:
    milestone: ...
    status: in_progress | blocked | ready_for_review
    last_verified_at: ...
  open_blockers:
    - blocker: ...
      evidence_ref: ...
      unlock_needed: ...
  superseded_assumptions:
    - old: ...
      replaced_by: ...
      why: ...
  next_best_action: ...
  stop_condition:
    - when_blocked: ...
  evidence_refs:
    - ref_id: ...
      source_type: repo_doc | test_output | benchmark | web | connector
      freshness_at: ...
  artifact_refs:
    - path: ...
      purpose: ...
```

### Handoff Packet

**一次情報と推論:** OpenAI Agents SDK の handoff は既定では conversation history 全体を受け渡しますが、`input_filter`、`input_items`、`nest_handoff_history`、`handoff_history_mapper` で受け渡し history を削れます。Cookbook の iterative repair loop は phase ごとに Review→Repair→Validate の structured output を返し、Agent improvement loop は `codex_handoff.md` を “次の harness update のための diagnosis + ranked recommendations + evidence + implementation guidance” として残します。これを踏まえると、multi-agent handoff は “親の会話を丸ごと渡す” のではなく “bounded contract + artifact refs” にすべきです。 citeturn28view4turn7view9turn13view3

```yaml
handoff_packet:
  handoff_id: ...
  delegated_to: explorer | reviewer | validator | docs_researcher
  task_boundary:
    in_scope_paths: [...]
    out_of_scope_paths: [...]
    write_policy: read_only | scoped_write
  accepted_inputs:
    - context_packet_ref: ...
    - artifact_refs: [...]
    - freshness_requirements: [...]
  excluded_context:
    - raw_tool_history
    - stale_browser_history
    - private_connector_data_not_needed
  expected_output:
    schema: findings | patch_delta | validation_report | review_report
    required_fields:
      - summary
      - evidence_refs
      - freshness_at
      - unresolved_questions
  review_rubric:
    - correctness
    - security
    - missing_tests
  independence_mode: limited_context | diff_only | evidence_only
```

### Progress Log と Evidence Ledger

**一次情報:** “Iterate on difficult problems” は running log に current best scores、last iteration で何を変えたか、eval が何を改善/悪化と言ったか、次に何を試すかを残せと述べています。long-horizon blog の `Documentation.md` も milestone status、decisions、run/demo commands、known issues/follow-ups を shared memory と audit log にしていました。SpecDock の progress log も少なくとも iteration id、change summary、score delta、decision、next experiment を持つべきです。 citeturn33view0turn21view5

**一次情報と推論:** evidence ledger は OpenAI がその名前で定義しているわけではありませんが、Goal の verification surface、repair loop の structured delta、compliance memo の cited findings、`codex_handoff.md` の evidence-backed recommendation を合成すると、claim ごとに source ref、generated_at、validation command、result、confidence、superseded_by を残す形が自然です。特に compliance example は「不完全なら guessing ではなく open question にする」「superseded assumption を silently delete しない」としており、ledger に supersession を持たせる価値が高いです。 citeturn23view6turn7view9turn25view3

### Active Projection

**推論:** “active projection” は OpenAI の固有用語ではありませんが、Session cookbook の trimming/summarization、Codex の AGENTS root-to-leaf injection、long-running docs の durable project memory を合わせると、「全 history の再生」ではなく「次の turn に必要な slice だけを投影する」設計が本質です。SpecDock では log/ledger/plan 全体を毎回渡すのではなく、各 turn/subagent に対して objective、current checkpoint、last verified evidence、single next action、active files、open blockers だけを投影し、残りは artifact reference として保持するのが妥当です。 citeturn24view3turn24view7turn21view5turn32view2

## 段階的開示と圧縮再開

### 何を先に読み、何を後回しにするか

**一次情報と推論:** Codex の best practices は prompt に “Goal / Context / Constraints / Done when” を入れ、必要な files, folders, docs, examples, errors を明示するよう勧めます。OpenAI の skill 設計は “context window is a public good” と言い、skills も up-front に全部膨らませないことを重視します。したがって progressive disclosure の読み込み順は、まず objective と verification、次に active subtree の `AGENTS.md`、次に current milestone に関連する exact file/error/test、さらに必要なら plan の該当 section、最後に connector/web という順にすべきです。全 docs の一括投入は Codex の推奨と逆方向です。 citeturn19view0turn35view2turn11view0

**一次情報:** `AGENTS.md` は repo root から CWD までの chain だけが自動注入され、Codex は current dir に達した時点で探索を止めます。つまり Codex 自身が already progressive disclosure な discovery model を採っています。SpecDock が独自 packet/retrieval を作るなら、このモデルを壊さず、「必要な subtree だけ詳細化する」ことで Codex の mental model に合わせるべきです。 citeturn8view6turn32view2

**公開実装例:** `openai-docs` skill は private Google Docs、Calendar、Slack、GitHub、Notion などは web search や model memory ではなく connector/MCP を使えと書いています。これは freshness と authorization の両方の観点で重要です。SpecDock では private workspace data が必要なときだけ connector を使い、repo で再現可能な SoT は repo artifact に落とし直す運用にすべきです。connector 取得結果そのものを durable memory に再配布する設計は危険です。 citeturn35view1

### stale assumption を避ける refresh ルール

**一次情報:** Goal cookbook は verification surface が tests/benchmark/report/artifact/command output/source material のいずれかでなければならず、work は evidence に対して監査される必要があると述べています。Iterative repair loop も review/repair/validate の各 phase で最新 validation feedback を次の input にする構造です。したがって refresh ルールは “external or derived state を再利用する前に、その freshness を evidence で再検証する” です。SpecDock では各 packet の evidence ref に `freshness_at` と `validated_by` を持たせるべきです。 citeturn23view6turn7view9

**一次情報:** Codex docs は instructions が stale に見えるなら restart すべきで、instruction chain は run ごと/TUI session の開始ごとに組み直されると明記しています。つまり AGENTS の更新反映は chat memory ではなく restart semantics に依存します。SpecDock は “run middle で repo instruction を変えたらそのまま反映される” と仮定してはいけません。 citeturn8view6

### 圧縮と再開

**一次情報:** OpenAI は `/responses/compact` を long-running conversation の first-class compaction として提供しており、compaction item の `encrypted_content` を含む compacted output list を次の request に渡せます。Codex Prompting Guide では、これによって effective context window が大きく伸び、長い trajectory を context window 超えで継続できると説明しています。Codex 自身も以前は手動 `/compact` ベースでしたが、現在は auto compaction を使うと説明されています。SpecDock が API 架装で Codex-like runner を作る場合、古い ad-hoc summarization より `/responses/compact` を優先採用すべきです。 citeturn32view4turn31view1turn18view0

**一次情報:** Agents SDK の session memory は run 前に session history を prepend し、run 後に新規 items を保存しますが、`previous_response_id` や `conversation_id` と同時には使えません。session cookbook の summarizing session は `context_limit` と `keep_last_n_turns` を持ち、古い turn を summary の synthetic user→assistant pair に圧縮しつつ、直近 N turns を verbatim で保持します。SpecDock は state mechanism を一つに決めるべきで、session、conversation、previous_response_id、manual input replay を混在させない方がよいです。 citeturn27view1turn24view3

### 何に依存してはいけないか

**一次情報と推論:** OpenAI の cookbook と docs は、会話 history、memory、browser history を “働き方” の補助には使っても “記録そのもの” にはしない方向で一貫しています。compliance example では memory を shadow record にしてはいけない、Chrome docs では browser history は sensitive で malicious page content に引きずられる、Session cookbook では summarization loss/bias と context poisoning を明示しています。したがって resume/handoff の再開点は、raw chat transcript、browser tabs、private browsing residue、曖昧な memory injection に依存してはいけません。必ず reviewable artifact と freshness 付き evidence を基準に再開すべきです。 citeturn25view6turn15view0turn24view6

## マルチエージェント契約

### bounded task packet と受け入れ入出力

**一次情報:** Codex subagents は complex かつ parallelizable な work に有効ですが、OpenAI は read-heavy の exploration、tests、triage、summarization を starting point とし、write-heavy parallel workflow には慎重であるべきと明言しています。custom agents は `.codex/agents/` 以下の TOML で定義し、`name`、`description`、`developer_instructions` を必須にし、model や sandbox_mode や skills 設定は親 session から継承できます。best custom agents は narrow and opinionated であるべき、というのが一次情報の結論です。SpecDock の multi-agent は役割境界を狭くし、agent ごとに allowed tools と expected output schema を固定するのが筋です。 citeturn10search1turn9view1turn9view6

**一次情報:** OpenAI の custom-agent example では PR review を `pr_explorer`、`reviewer`、`docs_researcher` に分離しています。これは “探索” と “評価” と “外部 docs check” を混ぜない設計です。SpecDock でも implementer / explorer / validator / reviewer を同一 packet で動かすより、役割ごとに packet を変えるべきです。特に reviewer には diff と rubic と evidence refs を渡し、実装者の raw scratchpad や不要な tool noise は渡さない方が独立性が高まります。後者は一次情報からの強い推論です。 citeturn9view1turn28view4

**近一次情報:** `Build iterative repair loops with Codex` は Review が findings だけを返し、Repair が change summary と updated artifact path を返し、Validate が remaining delta を返すという structured handoff を採っています。これは multi-agent 契約にそのまま流用できます。SpecDock は agent ごとに “accepted input” と “expected output” を型で固定し、自由文の雑多な引継ぎを避けるべきです。 citeturn7view9

### freshness、独立レビュー、contamination prevention

**一次情報:** Agents SDK handoff は既定で previous conversation 全体を見せますが、`input_filter` で input を作り替えられます。`remove_all_tools` のような common filter も用意されており、nested handoff では transcript を single assistant summary に畳む beta 機能もあります。さらに docs は、handoff は single run 内に留まり、input guardrails はチェーン最初の agent にしか、output guardrails は final output agent にしか効かないと明記しています。SpecDock は “handoff したから guardrail も引き継がれる” と考えてはいけません。必要なら tool guardrails と explicit review step を各 agent に置くべきです。 citeturn28view4turn28view1

**推論:** contamination prevention の実務ルールは、少なくとも次の四つです。ひとつ目は reviewer に raw tool output や exploratory dead-end を渡さず、artifact ref と concise summary に圧縮すること。ふたつ目は freshness timestamp のない benchmark/log/doc は reviewer input に入れないこと。みっつ目は parallel write を同一 worktree/branch/file set に対して許さないこと。よっつ目は “最新 status” と “source artifact” を分離し、status だけを読み継がせないことです。これは OpenAI が書く「context pollution/rot」「shared memory and audit log」「tool history filter」の実装原則から直接導かれます。 citeturn10search1turn21view5turn28view4

## メモリ境界とプロンプト設計

### メモリと信頼境界

| コンテキスト源 | 推奨信頼度 | 役割 | SpecDock での扱い |
|---|---|---|---|
| repo の `AGENTS.md` と plan/log/memo artifact | 高 | repo 規約、完了条件、進捗、証拠 | 原則的な SoT。Git で review し、path scope と freshness を持たせる。 citeturn7view0turn21view5turn22view0turn25view7 |
| session transcript / CLI history / Responses conversation state | 中 | 継続実行の operational memory | 継続性には使うが最終記録にはしない。history persistence と retention を意識する。 citeturn17view2turn27view1turn30view0 |
| SDK `Memory()` / Codex Memories / Chronicle | 中〜低 | “どう働くか” の再利用 | fact DB にしない。調査結論や cited finding は reviewed artifact 側へ。Chronicle は broader local context を要約しうる。 citeturn25view6turn14search0turn17view3turn27view3 |
| private connector / MCP / app connector | 高だが scope 限定 | fresh private data / authorized actions | 必要時に引く。SoT 化が必要なら repo artifact に再表現する。web や memory の代替として使う。 citeturn35view1turn11view7turn11view2 |
| browser page content / Chrome profile / browser history | 低 | signed-in browser tasks | untrusted context。history は elevated risk。always-allow を避ける。 citeturn15view0 |
| public web | 中 | repo 外の最新公開事実 | freshness 取得には有効だが、repo 方針や private truth の代替にはしない。引用必須。 citeturn11view7turn35view1 |
| Deep Research などの synthesis output | 中 | 調査サマリ | **推論:** cited report として有用だが、それ自体を SoT にせず、根拠 source に遡れる形で扱う。 citeturn25view1turn13view3 |

**一次情報:** OpenAI Agents SDK の context object は LLM に送られず、純粋にローカル object です。ただし serialized `RunState` を human-in-the-loop や durable workflow に使うなら runtime metadata ごと保存されるので、`RunContextWrapper.context` に秘密を載せるなと docs は警告しています。SpecDock では “model-visible context” と “runtime-only context” と “persisted runtime state” を別型に分けるべきです。 citeturn27view2

**一次情報:** OpenAI の data controls では Responses API の application state は既定で 30 日保持、background mode は完了 polling のため約10分ディスクに保存され、Conversations API の items は 30-day TTL の対象外です。これらは user-facing feature というより retention boundary の違いなので、SpecDock がどの API 面を採用するかは privacy design に直結します。 citeturn11view6turn30view0

### スキルとプロンプト設計の推奨

**一次情報と公開実装例:** skill / prompt 設計で drift を減らしつつ autonomy を残すには、OpenAI 公開資料から少なくとも次の設計が導けます。ひとつ目は、prompt は Goal/Context/Constraints/Done when か、より一般には Role/Goal/Success criteria/Constraints/Output/Stop rules のように “何が終わりか” と “いつ止まるか” を先に書くこと。ふたつ目は、legacy chain-of-thought 時代の冗長 prompt stack を持ち込まず、細かい手順指定は本当に必要なときだけにすること。みっつ目は、反復ワークフローは skill にし、schedule は automation に分けること。よっつ目は、skill description を trigger rule と exclusion rule まで含めて書くことです。 citeturn19view0turn29search5turn11view3turn19view3turn35view4

**一次情報と公開実装例:** もう一段具体化すると、SpecDock の skill/prompt には次のルールが向いています。`AGENTS.md` には repo 常設の規約と verification/runbook の入口だけを書く。skill には reusable workflow と scripts/references を持たせる。prompt には今回 task の目的、active scope、fresh evidence、stop rule だけを載せる。hook は mechanical enforcement 専用に使い、automation は cadence を持つ follow-up に限定する。これは OpenAI 自身の docs skill が公開している scope map と一致します。 citeturn35view1turn11view0turn35view2

## SpecDock への示唆

### epic-00158 向け candidate follow-up issues

| タイトル | 問題 | source-backed rationale | likely impacted files/docs | acceptance evidence |
|---|---|---|---|---|
| Repo 指示チェーン hardening | repo 規約が散在し、Codex が毎回同じ探索を繰り返す。 | Codex は `AGENTS.md` を root-to-leaf で読むため、repo-root と subtree override に分割した durable guidance が最も自然。32 KiB cap もあるため単一巨大ファイルは危険。 citeturn7view0turn8view2turn8view6turn4search0 | **推定:** repo-root `AGENTS.md`、subtree `AGENTS.override.md`、`.codex/config.toml` | root と深い subtree の両方で “active instruction sources” を列挙でき、重要規約が truncation されない。 citeturn8view6 |
| Context packet schema 導入 | 長時間 PDCA が chat memory 依存で、再開点が曖昧。 | Goal の六要素、running log、milestone validation を compact packet に落とすと再開性が上がる。 citeturn23view6turn33view0turn21view5 | **推定:** `docs/agent/context-packet.md`、packet schema、orchestrator serializer | packet に objective、verification、constraints、boundaries、status、blockers、next action、evidence refs、freshness が入り、subagent に同一形式で渡せる。 citeturn23view6turn28view4 |
| Handoff packet と history filter | subagent/reviewer に親 thread 全体を渡し、stale or contaminated context が混入する。 | Agents SDK は `input_filter` と nested history を提供し、repair loop は structured I/O を前提としている。 citeturn28view4turn28view1turn7view9 | **推定:** `docs/agent/handoff-packet.md`、handoff filter 実装、review agent config | reviewer handoff が raw tool history を除去し、expected output schema に沿った findings/report だけ返す。 citeturn28view5turn7view9 |
| Progress log と evidence ledger | iteration の改善/悪化理由が失われ、resume と audit が弱い。 | OpenAI は running log に best scores、last change、eval delta、next try を記録せよと推奨し、long-horizon 実例でも status/decisions/known issues を durable doc に残している。 citeturn33view0turn21view5 | **推定:** `docs/agent/progress-log.md`、`docs/agent/evidence-ledger.md`、eval artifact writer | どの change がどの metric を改善したか時系列で追え、resume 時に “次に何を試すか” が一意に分かる。 citeturn33view0 |
| Compaction と resume の二重化排除 | transcript、summary、API session の state mechanism が混在し、再現性が低い。 | `/responses/compact`、session memory、conversation/previous_response_id は併用条件が異なる。ひとつ選び、reviewed artifact を補助 SoT にすべき。 citeturn31view1turn27view1turn24view3 | **推定:** `docs/agent/resume.md`、state adapter、compaction policy docs | same task が thread/session/conversation のどれで継続されるか明示され、resume に最低必要な IDs と artifact refs が保存される。 citeturn20view0turn30view0 |
| Memory/trust boundary matrix | repo docs、memory、browser、connector、web が同列に扱われる。 | OpenAI docs は memory を fact DB にしない、browser content を untrusted とする、private data は connector を優先する、と明示する。 citeturn25view6turn15view0turn35view1 | **推定:** `docs/agent/trust-boundaries.md`、policy tests、source tags | 各 source type に trust level・citation policy・persistence policy が定義され、agent output が source tag を持つ。 citeturn35view1turn11view6 |
| 独立 reviewer agent / worktree review | implementer と reviewer が同一文脈で動き、自己正当化が混入する。 | OpenAI は PR review を explorer/reviewer/docs researcher に分け、worktrees と review surface を使う実例を示している。 citeturn9view1turn21view0turn19view5 | **推定:** `.codex/agents/reviewer.toml`、review rubric doc、separate worktree flow | reviewer が diff・evidence・rubric ベースで動き、implementation scratch context を直接読まなくてもレビューできる。 citeturn28view4turn19view5 |
| Skill trigger 監査と簡潔化 | recurring workflow が巨大 prompt に混ざり、trigger が広すぎる。 | skills は reusable workflow 用、custom prompts は deprecated、context window は public good。trigger rule は狭く設計すべき。 citeturn5search4turn11view0turn35view2turn35view4 | **推定:** `skills/*/SKILL.md`、skill lint、evals | 各 skill が explicit trigger / exclusion / output contract を持ち、token budget と trigger 誤爆率を計測できる。 citeturn35view4turn35view2 |

### アンチパターンとリスク

最も危険なアンチパターンは、長時間 workflow を “長い chat transcript” のまま維持することです。OpenAI 自身が context pollution / context rot、summarization loss/bias、context poisoning を挙げており、長いループ用 use case でも progress を “context に頼らず” 明示追跡しろと書いています。SpecDock が会話そのものを SoT にすると、resume・handoff・review のすべてが脆くなります。 citeturn10search1turn24view6turn33view1

次に危険なのは、memory を shadow database にすることです。OpenAI cookbook は `Memory()` を unreviewed fact database として扱うな、もし結論が重要なら citations 付き reviewed artifact に書け、と非常に明確に警告しています。SpecDock では memory は preference / workflow lesson に限定し、事実・決定・証拠は evidence ledger や memo に出すべきです。 citeturn25view1turn25view6

三つ目は、multi-agent を “とりあえず並列化” することです。Codex は subagent を explicit ask でしか起動せず、write-heavy 並列は conflict と coordination overhead を増やします。さらに handoff は既定で full history を見せるため、bounded contract がないと reviewer や specialist が親 thread の雑音を引き継ぎます。 citeturn10search1turn28view4

四つ目は、trust boundary をまたぐ暗黙コンテキストです。browser history、signed-in Chrome state、Chronicle memories、private connectors は便利ですが、それぞれ exposure と retention が違います。とくに browser history は elevated risk で、malicious page content により unintended copy が起こりうると OpenAI 自身が書いています。SpecDock は “便利だから context に入れる” ではなく、“この source は何の権限・鮮度・保存条件で扱うか” を先に定義すべきです。 citeturn15view0turn14search0turn11view6

### 実装前の verification checklist

実装に入る前に、SpecDock は少なくとも次を直接検証すべきです。第一に、採用 surface が Codex CLI、Codex app、IDE extension、Responses API、Agents SDK のどれかを固定し、その version で `/goal`、`/plan`、`/compact`、subagents、skills、memories、connectors が実際に使えるかを確認すること。第二に、repo の `AGENTS.md` chain がどの path まで読み込まれ、byte cap に当たらないかを実測すること。第三に、private connector/MCP と browser surfaces が enabled な場合、それぞれの approval、allowlist/blocklist、retention を確認すること。第四に、subagent/reviewer handoff で `input_filter` や summary nesting が必要かを A/B で検証すること。第五に、session / conversation / previous_response_id / compact のうち何を state 主軸にするかを一つに決めることです。 citeturn20view0turn7view4turn8view2turn15view0turn27view1turn31view1

さらに、requirements 化の前に “surface-specific で曖昧な点” も潰すべきです。たとえば nested handoffs は beta、subagent visibility は surface 差分があり、`@include` による AGENTS composition は issue 提案段階です。これらは設計資料に “現時点の実験候補” と書くのはよいですが、MVP hard requirement には向きません。 citeturn28view1turn7view4turn4search3

### Sources used と citation list

本文の主要参照元は、OpenAI Developers の Codex docs 群、OpenAI Cookbook の Codex/Agents SDK notebooks、OpenAI blog posts、OpenAI の公開 GitHub repos (`openai/codex`, `openai/skills`, `openai/openai-cookbook`, `openai/openai-agents-python`) です。特に重要なのは、`AGENTS.md` docs、Subagents docs、Best practices、Unrolling the Codex agent loop、Run long horizon tasks with Codex、Using Goals in Codex、Build iterative repair loops with Codex、Building Reliable Agents with Memory and Compaction、Agents SDK の Handoffs/Sessions/Context docs です。 citeturn7view0turn7view4turn7view3turn18view0turn7view6turn7view8turn7view9turn13view0turn27view0turn27view1turn27view2

公開実装例としては、`openai/skills` README、`openai-docs` skill、`skill-creator` skill、`security-threat-model` skill、`codex_exec_plans.md`、Agents SDK handoff docs、Codex config/open issues も使いました。これらは一次 docs より証拠強度は一段落ちますが、「OpenAI 自身がどう実装・配布・説明しているか」を読む上で有益です。 citeturn35view0turn35view1turn35view2turn35view4turn22view0turn28view4turn4search0turn4search3

### 不確実性と次の調査枝

この調査の不確実性は主に三つです。ひとつ目は、SpecDock の実 repo 構造、既存 epic 管理面、どの Codex surface を主に使うかが未提示であること。ふたつ目は、Codex の一部機能が surface-specific または beta で、公開 docs と実環境の挙動差がありうること。みっつ目は、OpenAI が公開しているのは prompt/harness の原則と一部実装であり、内部の非公開最適化や hidden prompt composition までは前提にできないことです。よって、この報告は requirement 原案ではなく、「検証対象が明確な設計仮説集」として読むのが適切です。 citeturn7view4turn28view1turn4search3turn18view0

次の research branch として価値が高いのは、実機 eval を伴う四本です。第一に、SpecDock repo での `AGENTS.md` byte budget / nested override / fallback filename の discovery テスト。第二に、context packet と handoff packet の A/B 比較で、raw transcript 渡しと filtered packet 渡しの drift/latency/quality を比べること。第三に、reviewer independence の eval で、diff-only reviewer と shared-history reviewer の false confidence と issue recall を比べること。第四に、memory boundary の eval で、repo artifact / session summary / connector result / browser data の各 source を混ぜたときの stale fact 率と contamination 率を測ることです。これらは OpenAI の traces/evals/handoff/filter/compaction primitives と整合し、SpecDock にとって実装直前の検証価値が高いです。 citeturn13view3turn28view4turn31view1turn33view0