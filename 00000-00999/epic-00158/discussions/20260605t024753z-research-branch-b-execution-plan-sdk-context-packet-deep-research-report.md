# Agent Workflow PDCA Hardening のための Codex 長時間ワークフロー設計調査

## エグゼクティブサマリー

この調査から見える最重要点は、**長時間の Codex ワークフローを安定化させるには、会話やモデル内部状態を真実源にせず、外部に永続化された計画・進捗・検証・ハンドオフ成果物を真実源にするべき**ということです。OpenAI の Codex 実行計画ガイドは、計画を「生きた文書」として扱い、理解が進むたびに更新することを推奨しています。また Codex CLI の非対話モードは、agent message、command execution、file changes、plan updates まで含む JSONL イベントを出力でき、`resume` による継続もサポートしています。対照的に、Codex の Memories はローカル生成状態であり、必須ルールの唯一の保存先として使うべきではないと公式に明記されています。さらに Responses API の compaction item は有用ですが**不透明で人間可読ではありません**。したがって SpecDock では、`PLAN.md`、`progress.log.jsonl`、`verification.json`、`handoff.packet.md` のような外部成果物を中心に据えるのが妥当です。 citeturn6view0turn11view0turn11view1turn32view0turn34search0

二つ目の要点は、**コンテキストは「全部載せ」ではなく、階層化された packet と progressive disclosure で運ぶべき**ということです。Codex の `AGENTS.md` は階層的に読み込まれ、ルートから現在ディレクトリまでの指示が順に注入されます。Skills は名前・説明・パスだけを先に見せ、必要時だけ `SKILL.md` が読み込まれる設計です。OpenAI Agents SDK の handoff も、専門家へ渡す履歴は短く具体的にし、必要なら構造化メタデータや filtered history を使う方向を示しています。これは、SpecDock の issue/epic/initiative/research/implementation/review/verification/handoff packet を「薄いヘッダ + 重い添付」方式で作る設計を強く支持します。 citeturn8view0turn30view0turn9view6turn15view4

三つ目の要点は、**進行判定をモデル自己申告ではなく、存在確認・テスト結果・承認状態で行うべき**という点です。OpenAI Cookbook の multi-agent workflow 例では、Project Manager が `REQUIREMENTS.md`、`TEST.md`、`AGENT_TASKS.md` を生成し、次の handoff に進む前に必要ファイルの存在を必ず確認しています。別の iterative repair loop 例でも、Review → Repair → Validate の三相を回し、停止条件を「検証通過」「試行上限」「改善差分停滞」「人間判断が必要」のいずれかに置いています。SpecDock の handoff も同様に、**required artifacts と validator outputs が揃うまで状態遷移させない**のが信頼性の要です。 citeturn27view2turn27view1turn26view6

四つ目の要点は、**トレースを先に取り、後から grader と回帰ハーネスに昇格させること**です。OpenAI は Agents SDK で tracing を標準搭載し、まず traces で一件一件の挙動を理解し、その後 trace grading と datasets/eval runs へ進む流れを示しています。評価データは synthetic・production・SME 注釈・historical logs を混ぜて継続的に成長させるべきだとも明言しています。ただし 2026 年時点では、旧 Evals 製品は read-only 化と shutdown が予定され、OpenAI 自身が Promptfoo への移行 cookbook を出しています。よって SpecDock の評価基盤は、**trace grading を一次系にしつつ、canonical dataset はツール非依存形式で持ち、Promptfoo へ export できる構造**にしておくのが安全です。 citeturn15view6turn20view0turn20view1turn22view6turn23search0turn25view5

| 推奨事項 | 根拠区分 | 鮮度リスク | Codex 要直接検証 |
|---|---|---|---|
| 計画・進捗・検証・ハンドオフを会話外 artifacts として永続化する | 一次ソース + 推論。実行計画ガイド、JSONL、resume、opaque compaction、memories の注意書きが根拠。 citeturn6view0turn11view0turn11view1turn32view0turn34search0 | 低 | 否 |
| packet は薄い要約と重い添付に分け、常時ロード対象を最小化する | 一次ソース + 推論。AGENTS 階層注入、Skills の progressive disclosure、handoff の filtered history が根拠。 citeturn30view0turn9view6turn36view9 | 低 | 否 |
| handoff は required files / validator pass / approval state でのみ進める | 一次ソース + 推論。Project Manager gating と repair loop stop conditions が根拠。 citeturn27view2turn26view6 | 低 | 否 |
| Codex 実行は JSONL/traces を必ず採取し、trace-level grader を組み込む | 一次ソース。CLI JSONL、Agents tracing、trace grading。 citeturn11view0turn15view6turn20view1 | 低 | 否 |
| destructive side effects は human gate を残す | 一次ソース。approval/guardrail/security docs。 citeturn11view3turn36view7turn36view8 | 低 | 否 |
| Evals 固有形式への強い依存を避け、Promptfoo export 経路を持つ | 一次ソースだが将来変動大。agent-evals は legacy Evals 参照を残す一方、datasets docs と migration cookbook は deprecation/Promptfoo を示す。 citeturn20view0turn23search0turn25view5 | 高 | はい |

## ソースマップ

このテーマでは、**一次ソースの中心は OpenAI Developers docs、OpenAI Cookbook、公式 GitHub リポジトリ**です。実務上もっとも重要な鮮度差分は、`Evals` に関する記述です。agent-evals と datasets 系 docs では依然として eval runs や Evals を参照する一方、2026-06-03 の OpenAI Cookbook では「OpenAI is winding down the Evals product and recommends Promptfoo」と明示されています。SpecDock で eval backend を固定する前に、この差分は必ず吸収すべきです。 citeturn20view0turn23search0turn25view5

| 出典 | 日付・鮮度シグナル | カバー範囲 | 証拠強度 | SpecDock への relevance |
|---|---|---|---|---|
| OpenAI Cookbook「Execution plans guide」citeturn6view0 | 2025-10-07 | PLAN.md/PLANS.md の目的、構成、更新規律 | 高 | 実行計画 artifact の一次根拠 |
| Codex docs「Non-interactive mode」citeturn11view0turn11view1 | current docs、2026-06-05 時点で参照 | `codex exec`、JSONL、resume、CI パターン | 高 | launch / monitor / resume / machine-readable capture |
| Codex docs「SDK」citeturn11view2turn12view0 | current docs | thread 開始、resume、Python JSON-RPC | 高 | 埋め込み制御と resume handle の設計根拠 |
| Codex docs「App Server」citeturn32view4 | current docs | rich client、history、approvals、streamed events、JSON-RPC | 高 | deep integration だが CI 非推奨という境界線 |
| Codex docs「Agent approvals & security」citeturn11view3turn10view14 | current docs | sandbox、approval、network allowlist、cloud two-phase runtime | 高 | human gate と least privilege 設計 |
| Codex docs「AGENTS.md」「Prompting Guide」citeturn8view0turn30view0turn30view1 | current docs + 2026-02-25 | instruction layering、compaction、avoid upfront plan/preamble trap | 高 | context packet layering、overlong instruction 対策 |
| Codex docs「Skills」「Subagents」「Hooks」「Rules」citeturn9view6turn37view0turn32view2turn11view4 | current docs | progressive disclosure、separate context、lifecycle hooks、experimental rules | 高 | packet compaction、subagent boundary、validation hooks |
| OpenAI API docs「Agents SDK tracing / running / results / guardrails / orchestration」citeturn15view6turn36view5turn36view1turn36view7turn15view4 | current docs | traces、state strategy、paused run、approval、handoff pattern | 高 | resume semantics、trace capture、handoff artifact 設計 |
| OpenAI API docs「Background / Webhooks / Conversation state / Compaction」citeturn35view0turn35view1turn35view2turn34search0 | current docs | async long-run、polling、webhooks、IDs、compaction | 高 | server-side durable continuation と compaction packet 設計 |
| OpenAI API docs「Evaluate agent workflows / Trace grading / Evaluation best practices」citeturn20view0turn20view1turn22view6turn22view7 | current docs | traces→graders→datasets→continuous evaluation | 高 | regression harness 設計の一次根拠 |
| OpenAI docs/Cookbook「Getting started with datasets」「Moving from OpenAI Evals to Promptfoo」citeturn23search0turn25view5 | current docs + 2026-06-03 | grader types、dynamic dataset、Evals deprecation、Promptfoo migration | 高 | eval backend の鮮度リスクと移行方針 |
| OpenAI Cookbook「Build iterative repair loops…」「Agent Improvement Loop…」「Building Consistent Workflows…」「Build Code Review…」citeturn27view1turn28view0turn27view2turn27view3 | 2025-10-01, 2026-05-11, 2026-05-12 | review/repair/validate loop、gated handoff、Codex handoff、structured review | 高 | packet/handoff/review/verification の具体形 |
| 公式 GitHub: `openai/codex`、`openai/codex-action`、`openai/openai-agents-python` citeturn40search13turn40search1turn40search0 | current repo landing pages | repository 名、責務、公式 repo signal | 中 | repo-level provenance の確認 |
| 二次比較: Claude Code memory / subagents docs citeturn39view0turn39view1 | current docs | concise index + topic files、separate subagent contexts | 中 | 非 Codex だが packet compaction の比較材料 |

## 実行計画と永続アーティファクト

**一次ソース判断。** 実行計画は単なる TODO リストではなく、更新規律を持つ「生きた文書」であるべきです。OpenAI の execution plans guide は、関連ファイル、前提、仮説、ステップ、検証手順を書いた plan file を作り、理解が進んだら plan 自体を更新することを勧めています。さらに、**有意な進捗の後、だいたい 1 時間ごと、あるいは blocked になった時点**で plan を更新するのがよいとしています。別の Codex guide では `/goal` に `PLAN.md` を渡し、各 milestone ごとに tests を作らせる例を示しています。これは SpecDock でも、計画を「達成条件に結びついた artifact」として扱うべきことを示します。 citeturn6view0turn9view7

| 実行計画の必須項目 | 公式根拠 | SpecDock での候補フィールド | 鮮度リスク | 要直接検証 |
|---|---|---|---|---|
| 目的と non-goals | plan は goal, scope, assumptions を明示する living document とされる。 citeturn6view0 | `objective`, `non_goals`, `scope_boundary` | 低 | 否 |
| 前提・リスク・未解決点 | execution plans guide は assumptions と risks を早期に固定する。 citeturn6view0 | `assumptions[]`, `risks[]`, `open_questions[]` | 低 | 否 |
| milestone ごとの検証 | `/goal` ガイドは milestone ごとに tests を作る例、repair loop は validate phase を独立させる。 citeturn9view7turn27view1 | `milestones[]`, `validators[]`, `acceptance_checks[]` | 低 | 否 |
| 現在位置と次の一手 | plan updates と JSONL plan events があるため、resume cursor を明示化できる。 citeturn11view0turn11view1 | `current_step`, `next_step`, `resume_cursor` | 低 | いいえ |
| blocker と approval 待ち | paused runs は `interruptions` と resumable `state` を返す。 citeturn36view1turn36view7 | `blockers[]`, `pending_approvals[]`, `resume_handle` | 低 | 否 |
| 生成すべき artifacts | PM workflow は required file existence を gate に使う。 citeturn27view2 | `required_artifacts[]`, `handoff_exit_criteria[]` | 低 | 否 |
| source/freshness 参照 | research と handoff を durable にするには freshness tag が必要。これは compaction opaque 性・memories 非規範性からの推論。 citeturn34search0turn32view0 | `source_refs[]`, `verified_at`, `freshness_risk` | 低 | 否 |

**推論。** SpecDock では、`PLAN.md` だけでは足りません。実行計画の人間可読部分と、再開可能性を支える機械可読部分を分けるべきです。最小でも、`PLAN.md`、append-only の `progress.log.jsonl`、resumable state handle を格納する `run-state.json`、validator の実行結果を保持する `verification.json`、停止時の意思決定を残す `handoff.packet.md` が必要です。これは、Codex CLI の JSONL event stream、repair loop の `record.json`、Agents SDK の paused `state` Surface を組み合わせた設計推論です。 citeturn11view0turn26view4turn36view1

| 永続 artifact | 役割 | 生成契機 | 破棄してよいか | 根拠 |
|---|---|---|---|---|
| `PLAN.md` | 人間可読の作戦書。目的、前提、milestone、validator を保持 | run 開始前と major re-plan 時 | 完了後も保持 | execution plans guide。 citeturn6view0 |
| `progress.log.jsonl` | append-only 進捗。時刻、actor、step、result、evidence refs、next step | 各 turn 完了時、hook `Stop` 時 | 原則保持 | CLI JSONL と hooks に合う。 citeturn11view0turn32view2 |
| `run-state.json` | session/thread/conversation/previous_response_id/interruptions などの再開情報 | pause、approval、turn 完了時 | 完了後は archive 可 | SDK / Agents results / conversation state。 citeturn11view2turn36view1turn35view2 |
| `verification.json` | テスト、lint、schema checks、grader 結果 | validator 実行時 | 保持 | repair loop validate、datasets/graders。 citeturn27view1turn23search0 |
| `handoff.packet.md` | 人間向け停止要約。何が終わり、何が未了で、何で再開するか | compaction 前後、handoff、blocked 時 | 保持 | `codex_handoff.md` と compaction opaque 性。 citeturn28view0turn34search0 |

**一次ソース判断。** stop/resume は「新しい依頼を投げ直す」処理ではありません。Codex CLI は `codex exec resume --last` や session ID 指定で継続できます。Codex SDK は thread ID による resume をサポートします。Agents SDK でも paused run は `interruptions` と `state` を返し、**approval を新しい fresh turn として扱わず、同じ state から再開するべき**と明記されています。SpecDock の resume 操作は、常に `resume_handle` から復元し、元の plan/version と pair にすべきです。 citeturn11view1turn11view2turn36view1turn36view6

**避けるべき反パターン。** 第一に、巨大な自然言語プロンプトを唯一の plan にすることです。第二に、実装フェーズでも毎回「最初に plan を説明せよ」「逐次 status を返せ」と促すことです。OpenAI の Codex Prompting Guide は、upfront plan や preamble を強く求めると rollout が途中で止まりやすいと注意しています。第三に、`result.history`、session、conversation ID、`previous_response_id` を無秩序に混在させることです。Agents SDK docs は、state strategy を一会話あたり一つ選ばないと context duplication を招くと述べています。第四に、memories や Chronicle を再現性のある真実源として信用することです。公式 docs は `AGENTS.md` や checked-in docs を required team guidance の置き場にし、memories は補助レイヤと位置づけています。第五に、完了判定を agent の自己申告に依存することです。Cookbook の gated workflow と repair loop は、完了を file existence と validation で決めています。 citeturn30view1turn36view5turn32view0turn27view2turn27view1

## コンテキストパケット設計

**一次ソース判断。** packet 設計の基本は、常時注入される guidance と、必要時にだけ展開される task-specific context を分けることです。`AGENTS.md` は上位から下位へ注入される repo-level guidance に向いています。Skills は progressive disclosure を採用し、必要時のみ詳細 instruction をロードします。Orchestration docs も、specialist には narrow job と short handoffDescription を勧め、必要に応じて structured metadata や filtered history を載せる方向を示しています。これに基づけば、SpecDock packet は **薄い header に contract を集約し、重い証拠は `attachments` や `artifact_manifest` で参照**するのがよいです。 citeturn30view0turn9view6turn15view4

**推論。** すべての packet は共通して、`id`、`kind`、`parent_ids`、`status`、`objective`、`constraints`、`success_checks`、`required_artifacts`、`source_refs`、`verified_at`、`freshness_risk`、`resume_handle`、`trace_refs`、`approval_policy`、`artifact_manifest_ref` を持つとよいです。これは、execution plan・gated handoff・paused state・trace capture を横断的に接合するためです。支持証拠はありますが、この schema 自体は SpecDock 側の統合推論です。 citeturn6view0turn27view2turn36view1turn15view6

| packet 種別 | 目的 | 最低限含めるべき内容 | 添付すべき重い資料 | 次状態に進むゲート | 根拠区分 |
|---|---|---|---|---|---|
| initiative packet | 戦略目的と跨 epic 制約の固定 | business objective、global constraints、priority、child epics、global risks | strategy memo、decision log | child epic 群が materialized | 推論。上位計画層のため |
| epic packet | bounded outcome の中間単位 | success definition、dependencies、milestones、shared validators | source map、cross-issue test matrix | issue packet 群と epic validators | 推論 + execution plan |
| issue packet | 実装単位の再現可能 contract | problem statement、expected behavior、affected area、acceptance、owner | repro logs、stack traces、small diff context | implementation packet 作成 | 推論 + gated workflow |
| research packet | 事実と仮説の切り分け | research question、source claims、contradictions、freshness notes、verify-needed claims | PDFs/links 抜粋、trace ids | cited findings が埋まり、未解決点が列挙済み | 一次ソース + 推論。trace/eval へ接続 |
| implementation packet | 実装 run の作戦書 | plan version、file targets、commands、sandbox/approval, required outputs、rollback note | worktree path、schema diffs、migration notes | validators 実行済み | 一次ソース + 推論。PLAN, sandbox, approvals |
| review packet | diff・artifact の独立評価 | verdict、findings、severity、file/line citations、confidence | structured review JSON、full diff、trace refs | findings が triage される | 一次ソース。structured review cookbook |
| verification packet | 実行済み check の証跡 | environment、commands、stdout/stderr refs、pass/fail、hashes | junit/xml、coverage、screenshots、grader results | all required validators pass | 一次ソース + 推論 |
| handoff/compaction packet | 長期停止・引継ぎ・compaction の人間可読要約 | what changed、what remains、why paused、resume handle、latest verified facts、stale-after | artifact manifest、pending approvals、last trace/span IDs | reviewer or next agent が resume 可能 | 一次ソース + 推論。 `codex_handoff.md`、compaction opaque、paused state |

**一次ソース判断。** handoff は ownership transfer が本当に必要なときだけ使い、bounded specialist call で済むなら manager-style の agents-as-tools を選ぶのがよいです。OpenAI は、manager が最終責任を持つなら specialists を tool として呼び、workflow を安定させる方が良いとしています。SpecDock 的には、initiative/epic/issue の outer loop は安定した manager が持ち、research/review/verification は bounded specialist packet として実行し、実装 owner が変わる場面だけ handoff packet を作るのが自然です。 citeturn16search8

**重要な推論。** handoff/compaction packet は、**compaction item の代替ではなく補完**です。Responses compaction は state を濃縮して次 turn を継続させますが、出力は opaque で人間可読ではありません。したがって、SpecDock は compaction のたびに「何を捨ててもよかったか」「何がまだ真実源として残るか」を人間可読に再表現した packet を残すべきです。Hooks に `PreCompact` / `PostCompact` があるので、この packet 生成は Codex lifecycle に機械的に差し込めます。 citeturn34search0turn32view2

## Codex と OpenAI の自動化サーフェス

**一次ソース判断。** OpenAI には、長時間ワークフローを動かすための surface が複数ありますが、役割はかなり異なります。ローカル repo 内実行なら `codex exec` か Codex SDK、rich-clients 統合なら app-server、server-side orchestration と tracing なら Agents SDK、バックグラウンド API 継続なら Responses API の background / webhooks / conversations / compaction が中核です。これらは補完関係であり、全部を一つの会話に混ぜるべきではありません。 citeturn11view0turn11view2turn32view4turn33search17turn35view0turn35view2

| surface | Launch | Monitor / resume | Trace / inspect | Eval との接続 | 向く用途 | human gate を残すべき点 | 成熟度 |
|---|---|---|---|---|---|---|---|
| Codex CLI `codex exec` | 可。CI、scheduled jobs、pipelines 向け。 citeturn10view2 | JSONL events、session resume。 citeturn11view0turn11view1 | `--json` で thread/turn/item/error を記録可。 citeturn11view0 | 直接 first-party trace UI ではないため wrapper/export が必要 | repo 内の repeatable automation | sandbox escalation、network、write outside workspace | 安定寄り |
| Codex SDK TS/Py | 可。thread start/run/resume。 citeturn11view2 | thread ID resume、turn ごとの sandbox 変更。 citeturn11view2turn12view7 | docs は stable trace schema を約束していない。**wrapper telemetry を設けるべき** | 間接。SpecDock 側で trace 化が必要 | 自前ツールへの埋め込み | write / full access / review への昇格 | 中。要検証 |
| Codex App Server | 可だが docs は「CI なら SDK を使え」と明記。 citeturn32view4 | auth、history、approvals、streamed agent events。 citeturn32view4 | WebSocket は experimental/unsupported。非 loopback は auth 注意。 citeturn32view4 | 可能だが rich client 寄り | IDE/desktop 類似の深い統合 | approvals、remote exposure | 中〜高リスク |
| Codex GitHub Action | 可。workflow から Codex 実行。 citeturn32view3turn40search1 | workflow outputs と files で監視。 | output file/schema file を残せる。 citeturn32view3turn27view3 | CI eval/gates と接続しやすい | PR review、release prep、autofix | PR 作成/merge/deploy は別 job で人間 or stricter policy | 安定寄り |
| OpenAI Agents SDK | 可。server-owned orchestration。 citeturn33search17 | sessions、run state、interruptions。 citeturn36view5turn36view1 | traces built-in、default on。 citeturn15view6turn15view7 | trace grading と自然接続。 citeturn20view0turn20view1 | multi-agent orchestration、traceable control plane | sensitive tool calls、human approvals | 安定寄り |
| Responses API background + webhooks + conversations + compaction | 可。background async。 citeturn35view0 | polling/webhooks、conversation ID / previous_response_id。 citeturn35view0turn35view1turn35view2 | logs/IDs は取れるが workflow trace は Agents SDK の方が豊か | eval dataset 作成には使えるが workflow trace は別管理が必要 | 長時間 API tasks、cross-worker continuation | publish/merge/destructive actions | 高機能だが state discipline 必須 |

**一次ソース判断。** 何を human-gated に残すべきかもかなり明確です。OpenAI は、guardrails は自動チェックに、人間レビューは cancellations、edits、shell commands、sensitive MCP actions のような side effects の前に使うとしています。Codex approval/security docs でも、network access や sandbox 外動作は approval policy で止める前提です。GitHub Action と non-interactive docs も、read-only の Codex job と write 権限 job を分離し、patch artifact の受け渡しで最小権限化するパターンを示しています。したがって SpecDock では、**PR 作成/merge/deploy、外部副作用、権限昇格、unverified schema migration、network escalation** は人間または policy engine の gate を経るべきです。 citeturn36view8turn11view3turn11view1turn32view3

**追加の有効 surface。** Hooks は `PreToolUse`、`PostToolUse`、`PreCompact`、`PostCompact`、`Stop`、`SubagentStop` など lifecycle イベントに deterministic script を差し込めるため、SpecDock の packet 更新・artifact snapshot・secret scan・custom validator 実行に非常に相性がよいです。Rules は sandbox 外 command を制御できますが experimental です。Skills は reusable workflow を progressive disclosure で配るための authoring format です。Subagents は separate context によって context pollution/context rot 対策になりますが、approval は親 policy を継承し、non-interactive で新規 approval を surfacing できない場合は失敗が親に返るため、SpecDock の parent workflow 側が error/handoff packet を受ける設計にしておく必要があります。 citeturn32view2turn11view4turn9view6turn37view0

## トレース評価回帰ハーネス

**一次ソース判断。** OpenAI の推奨順序は一貫しています。まず traces で「何が起きたか」を理解し、そのあと graders でスコア化し、repeatability が必要になったら datasets と eval runs に進みます。Trace grading は、tool choice、handoff 発生、instruction/safety violation、prompt or routing change の end-to-end 改善を見たい時に最速の方法だとされています。SpecDock が PDCA を硬化したいなら、**Check フェーズの中心は trace-level evidence に置くべき**です。 citeturn15view0turn20view0turn20view1

**推論。** Codex 中心の regression harness は、次の二層構造が最も妥当です。第一層は、毎 run で必ず採る raw evidence です。Agents SDK なら built-in traces、Codex CLI/SDK なら JSONL events + wrapper metadata を保存します。第二層は、その evidence から生成・運用する repeatable checks です。OpenAI Cookbook の improvement loop は、real traces → human/model feedback → generated evals → Codex-ready handoff という flywheel を示し、最終的に `codex_handoff.md` を残します。SpecDock でも、trace から regression case を抽出し、human-reviewed handoff artifact に落とす構造に寄せるべきです。 citeturn15view6turn11view0turn28view0

| ハーネス層 | 設計 | 一次ソース根拠 | 推奨度 |
|---|---|---|---|
| Trace capture | run ごとに `run_id`、`plan_version`、`packet_ids`、git SHA、sandbox、approval policy、model、trace IDs、validator refs を必ず保存。Agents SDK なら traces default on、CLI なら JSONL を canonical raw log とする。 citeturn15view6turn15view7turn11view0 | traces first / JSONL events | 高 |
| Deterministic graders | file existence、JSON schema、expected tool/function 名、validator exit code、required citations/line spans を exact に見る。OpenAI datasets docs は string check・Python grader・text similarity を提供。 citeturn23search0turn22view11 | subjective judge より先 | 高 |
| Semantic/model graders | review quality、handoff clarity、expected behavior adherence など exact で測れない部分だけ `score_model` / `label model` を使う。grader hacking リスクがあるので SME spot-check を併用。 citeturn21view0turn21view6 | deterministic の二次補完 | 中〜高 |
| Dataset construction | synthetic、production feedback、domain experts、historical logs を混ぜ、edge case を見つけたら継続追加。dataset は dynamic space として運用。 citeturn22view6turn22view7turn23search0 | continuous improvement の要 | 高 |
| PR CI harness | 短い smoke tasks。read-only review / verification を中心にし、write は patch artifact のみ。Codex Action または `codex exec --json` を使い、output/schema/artifacts を upload。 citeturn11view1turn32view3turn27view3 | 低コストで regressions を早期検出 | 高 |
| Nightly harness | より長い tasks、workspace-write、repair loop、Promptfoo または trace grading batch をまわす。停止理由を `passed / max_attempts / delta_stalled / human_review_needed` に分類。 citeturn26view6turn28view0 | long-horizon regressions 用 | 高 |
| Regression triage | failing case を final output だけでなく trace segment、handoff packet、validator result まで掘る。trace grading は black-box より原因分析に向く。 citeturn20view1 | PDCA の「Act」に直結 | 高 |

**一次ソース判断。** CI セキュリティ設計はかなり具体的です。Codex docs は、CI failure の follow-up workflow で read-only 権限の Codex job を実行し、そのローカル差分を patch artifact として保存し、別 job がそれを apply して PR を開く構造を示しています。GitHub Action docs も、prompt-file と output-file ベースで repeatable tasks を workflow file から実行するパターンを推します。これは、SpecDock の regression harness で「agent が repo を直接 mutate する job」と「reviewed artifact を反映する job」を分離すべきという強い一次根拠です。 citeturn11view1turn32view3

**重要な鮮度注意。** OpenAI の datasets / eval docs はなお Evals を larger-scale path として参照しますが、2026-06-03 の OpenAI Cookbook は Evals を winding down するとし、Promptfoo を continuing/extending path として推しています。このため SpecDock は、**OpenAI trace grading を使って workflow-level 問題を見つけること**と、**Promptfoo など外部 runner に export できる canonical dataset/grader model を持つこと**を分離すべきです。Evals 固有 config を唯一の正本にしない方が安全です。 citeturn20view0turn23search0turn25view5

## 失敗モードと検出緩和

**一次ソース + 推論。** 長時間 Codex ワークフローで繰り返し壊れやすいのは、stale context、overlong instruction、hidden memory、unverifiable handoff、pause/resume drift、unguarded side effects です。OpenAI docs と Cookbook は、それぞれの断面を別々に扱っていますが、SpecDock では一つの failure taxonomy にまとめて検出器と required artifacts を設計するのがよいです。 citeturn32view0turn30view1turn37view0turn36view1turn36view8turn27view2

| failure mode | 主因 | 検出シグナル | 緩和策 | 必須 artifact |
|---|---|---|---|---|
| stale context | 古い research packet、conversation-only 指示、compaction 後の事実脱落 | 最新 commit/validator と packet 内容が食い違う、古い file path を参照 | packet に `verified_at` / `stale_after` / `git_sha` を持たせ、resume 時に authoritative files を再読込。会話だけに残した指示を禁止 | `research.packet.md`, `source-map`, `git_sha`, `handoff.packet.md` |
| overlong instruction | AGENTS/packet/添付の常時注入が膨らみ過ぎる | adherence 低下、冗長 latency、重要指示の欠落、tool truncation | AGENTS は常設規約だけ、task detail は packet 添付へ。Skills の progressive disclosure を使う。長文 tool output は truncate 方針を設ける | `artifact_manifest.json`, packet size budget, skills refs |
| hidden memory contamination | memories / Chronicle / local config による暗黙前提 | CI と開発者端末で結果が変わる、説明していない好みが反映される | automation では memories 依存を避け、required guidance は checked-in docs に置く。必要なら `--ignore-user-config` や thread-level memory control を使う | `config fingerprint`, `memory_mode`, `AGENTS.md` |
| unverifiable handoff | 完了自己申告のみで証拠がない | required files 不在、validator 未実行、review の行番号が不正確 | handoff exit を file existence / verification packet / exact citation schema に結びつける | `review.packet.json`, `verification.json`, `handoff.packet.md` |
| pause/resume drift | fresh turn で再開し、元 state を捨てる | 重複実行、approval のやり直し、context duplication | resume は `thread_id` / `session` / `state` / `previous_response_id` の正規 handle からのみ実行 | `run-state.json`, `interruptions`, `resume_handle` |
| unguarded side effects | approval/policy 境界がない | 未承認の shell/network/edit/PR merge | approvals、sandbox、network allowlist、権限分離 job | `approval log`, `policy config`, `patch artifact` |

**一次ソース判断。** hidden memory は特に要注意です。Codex 公式 docs は、required team guidance は `AGENTS.md` や checked-in docs に置き、memories を唯一の規範にするなと明言しています。Memories は background で更新され、Chronicle は screen captures を使い、rate limits も速く消費します。これは便利な補助機能ですが、SpecDock の CI や nightly harness の再現性基盤としては不適切です。 regression 環境では、memory usage を明示的に off または記録対象にすべきです。 citeturn32view0turn32view1

**二次比較。** Claude Code の docs でも、`MEMORY.md` は concise index として startup で一部のみ読み込み、詳細は topic files に分けて必要時だけ読む設計です。また subagents は separate context により main conversation を汚さないことを主目的にしています。これは Codex requirement ではありませんが、**「常設 index は短く、重い詳細は遅延ロード」「探索サブタスクは separate context に隔離」**という設計原則が現代 coding agents で収束しつつある比較材料です。 citeturn39view0turn39view1

## SpecDock 向け候補規約と次の論点

**候補ライブラリ規約。** 以下は最終 requirements ではなく、一次ソースを踏まえた**評価用候補**です。狙いは、SpecDock を「Codex 依存の会話ツール」ではなく、「Codex を差し替え可能な deterministic control plane」にすることです。支持根拠は、execution plans、gated handoff、structured review、trace/eval flywheel、opaque compaction、memory 非規範性です。 citeturn6view0turn27view2turn27view3turn28view0turn34search0turn32view0

| 規約カテゴリ | 候補 | 根拠区分 | 鮮度リスク | 要直接検証 |
|---|---|---|---|---|
| 文書命名 | `initiative.packet.md`、`epic.packet.md`、`issue.packet.md`、`research.packet.md`、`plan.md`、`progress.log.jsonl`、`implementation.packet.md`、`review.packet.json`、`verification.json`、`handoff.packet.md`、`artifacts.manifest.json` | 推論。OpenAI Cookbook と docs の artifact 形を一貫化 | 低 | 否 |
| frontmatter | `id`, `kind`, `parent_ids`, `status`, `objective`, `constraints`, `required_artifacts`, `validators`, `source_refs`, `verified_at`, `freshness_risk`, `resume_handle`, `trace_refs`, `approval_policy`, `git_ref` | 推論。plan / paused state / trace / gating を横断 | 低 | 否 |
| status 値 | `draft`, `ready`, `active`, `blocked`, `awaiting-approval`, `awaiting-review`, `awaiting-verification`, `verified`, `handoff-ready`, `compacted`, `superseded`, `archived` | 推論 | 低 | 否 |
| source verification marker | 本文 claim ごとに `source_key`, `kind(fp/sec/inf)`, `verified_at`, `freshness_risk`, `needs_direct_verification` を持つ | 推論。research→implementation の鮮度伝播のため | 低 | 否 |
| lifecycle transition | `research → planned → active → review → verification → handoff-ready → compacted/archived`、approval/blocked は overlay 状態 | 推論。repair loop と paused runs を統合 | 低 | 否 |
| compaction rule | compaction 前後に必ず `handoff.packet.md` と `artifacts.manifest.json` を更新し、opaque compaction item に依存しない | 一次ソース + 推論 | 中 | はい |
| memory rule | normative guidance は checked-in docs/packets、memory は optional recall | 一次ソース | 低 | 否 |
| CI evidence rule | PR/nightly の各 run は raw JSONL/traces、validator 出力、review JSON、handoff packet を必須保存 | 一次ソース + 推論 | 低 | 否 |

**epic-00158 向け候補 issue。** 影響ファイルは実 repo を未確認のため、**placeholder path** として示します。目的は backlog 化のたたき台であり、最終設計ではありません。 citeturn11view0turn27view2turn28view0turn20view1

| 候補 title | 問題 | source-backed rationale | likely impacted files/docs | acceptance evidence |
|---|---|---|---|---|
| Canonical plan and progress artifact を定義する | 長時間 run の現在地が会話に埋もれ、resume が fragile | living plan、JSONL events、resume session が一次根拠。 citeturn6view0turn11view0turn11view1 | `docs/agent-workflow/plan-schema.md`, `schemas/plan.schema.json`, `schemas/progress-log.schema.json` | sample `plan.md` と `progress.log.jsonl` で pause/resume を再現できる |
| Context packet schema を導入する | issue/epic/research/implementation/review が混線し stale context を招く | AGENTS layering、Skills progressive disclosure、handoff filtered history。 citeturn30view0turn9view6turn36view9 | `docs/specdock/packets.md`, `schemas/*packet*.json` | 8 種の packet サンプルで、必要情報だけを取り出せる |
| Handoff and compaction packet を hook で自動生成する | compaction 後に人間可読な再開材料が失われる | compaction item は opaque、hooks に Pre/PostCompact がある。 citeturn34search0turn32view2 | `tools/hooks/`, `docs/agent-workflow/handoff.md` | compaction 前後で `handoff.packet.md` が生成・更新され、次担当が再開できる |
| Codex runner wrapper で JSONL/run-state capture を標準化する | surface ごとの telemetry がばらつく | `codex exec --json`、SDK thread resume、Agents paused state。 citeturn11view0turn11view2turn36view1 | `tools/codex-runner/`, `docs/agent-workflow/run-state.md` | failed/paused/succeeded の各 path で同じ evidence bundle が残る |
| Structured review and verification packet を定義する | handoff が自己申告で、レビューや検証が再利用できない | code review cookbook は schema/output file と exact line citations を使う。 citeturn27view3 | `schemas/review.packet.schema.json`, `schemas/verification.schema.json`, `docs/reviewing.md` | sample diff に対し review JSON と verification JSON が生成される |
| PR smoke + nightly regression harness を分離する | 一発勝負の CI では long-horizon regressions を拾えない | continuous evaluation、read-only Codex job + patch artifact、repair loop stop conditions。 citeturn22view7turn11view1turn26view6 | `.github/workflows/agent-smoke.yml`, `.github/workflows/agent-nightly.yml`, `evals/` | PR で smoke、nightly で longer cases が成功し、artifacts が保存される |
| Memory suppression and stale-context detector を追加する | 開発者端末依存の hidden memory で再現性が壊れる | required guidance は AGENTS/docs、memories は helper layer。 citeturn32view0turn32view1 | `docs/reproducibility.md`, `tools/check-context-freshness/` | memory on/off で差が出るケースを検出し、CI でブロックできる |
| Eval backend abstraction と Promptfoo export を整備する | legacy Evals 依存は鮮度リスクが高い | agent-evals、datasets deprecation、Promptfoo migration。 citeturn20view0turn23search0turn25view5 | `evals/canonical/`, `tools/eval-export/`, `docs/evals.md` | 同じ canonical dataset を trace grading と Promptfoo の両方で使える |

**実装前の検証チェックリスト。**

- 選ぶ Codex surface ごとに version pin と event schema を固定し、`codex exec --json` の item/event 種別が wrapper 想定どおりか確認する。Cookbook の repair loop も Codex CLI version pin を推奨しています。 citeturn11view0turn27view1
- Codex SDK を使う場合、SpecDock が必要とする粒度の streamed events / trace-equivalent data を**本当に**取れるかを hands-on で確認する。現行 docs は `thread.run()` / `resumeThread()` を示す一方、trace schema までは約束していません。App Server 側には streamed agent events があるものの、CI 用ではなく deep integration 向けです。 citeturn11view2turn32view4
- state strategy を一会話一種類に固定する。`history`、session、conversation ID、`previous_response_id` の混在は避ける。 citeturn36view5
- approval pause を new turn と誤って扱わず、`interruptions` と `state` から再開できることをテストする。 citeturn36view1turn36view6
- automation で memories / Chronicle / user config / project rules をどう扱うかを明示し、再現性 test を作る。 citeturn32view0turn32view1turn11view0
- `PreCompact` / `PostCompact` / `Stop` hooks で packet 生成と validator 実行を差し込んだとき、race や duplicate updates が起きないかを確認する。matching hooks の複数起動も docs に記載があります。 citeturn32view2
- GitHub Action 系では read-only generation job と write-capable apply/open-PR job を分離し、API key が write job に流れないことを確認する。 citeturn11view1turn32view3
- review packet の file/line citations が diff と一致することを validator で強制する。公式 cookbook は「incorrect file citations and line numbers will be rejected」とまで書いています。 citeturn27view3
- eval backend は trace grading と Promptfoo export の両方で試し、legacy Evals 固有運用に lock-in しない。 citeturn20view0turn23search0turn25view5

**主要出典一覧。** 主要一次ソースは、Codex execution plans guide、Codex non-interactive mode、Codex SDK、App Server、Agent approvals & security、AGENTS.md / Prompting Guide、Skills / Subagents / Hooks、Agents SDK tracing / running / results / guardrails / orchestration、Background mode / Webhooks / Conversation state / Compaction、Evaluate agent workflows / Trace grading / Evaluation best practices、Getting started with datasets、そして 2025-2026 の OpenAI Cookbook 群です。repository provenance の補助として `openai/codex`、`openai/codex-action`、`openai/openai-agents-python` を参照しました。二次比較として Anthropic Claude Code docs の memory / subagents を限定利用しました。 citeturn6view0turn11view0turn11view2turn32view4turn11view3turn30view0turn9view6turn37view0turn15view6turn35view0turn34search0turn20view0turn23search0turn27view1turn28view0turn40search13turn40search1turn40search0turn39view0turn39view1

**不確実性と次の調査枝。** 最大の未確定点は、Codex SDK 単体で SpecDock が欲しい粒度の event/tracing surface をどこまで stable に取れるかです。現 docs では run/resume と sandbox 切替は明確ですが、workflow-level trace export の一次仕様は薄く、app-server は deep integration 向けです。次点は、Promptfoo を regression backend に据える場合の first-party trace grading との役割分担です。最後に、compaction hook と packet 生成を組み合わせたときの実運用コストと race behavior は、docs だけではなく実 repo 上の検証が必要です。これらは、SpecDock requirements へ落とす前に Codex 側で直接確認すべき論点です。 citeturn11view2turn32view4turn20view0turn25view5turn32view2turn34search0