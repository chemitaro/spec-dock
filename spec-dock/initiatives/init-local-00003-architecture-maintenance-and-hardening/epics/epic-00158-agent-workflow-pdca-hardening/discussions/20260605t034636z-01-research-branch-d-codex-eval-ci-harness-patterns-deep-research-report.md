# Agent Workflow PDCA Hardening 調査報告

## 要旨

現時点の公開情報を横断すると、Codex中心の回帰ハーネスで最も再現性が高い設計は、**小さく決定的なフィクスチャ**、**機械可読な実行ログ**、**外部検証器による客観チェック**、**別レーンの主観評価**、**CI上の権限分離**を組み合わせる形です。特に重要なのは、モデルの最終メッセージを成功条件にしないことです。OpenAI公式の `codex exec --json` は実行中イベントをJSONLで流せ、`--output-schema` で最終出力をJSON Schemaに合わせられますが、これだけでは十分ではありません。最終判定は、差分、検証コマンド、生成物、ハッシュ、レビュー結果などの**外部証拠**に寄せるべきです。さらに、OpenAI自身が 2026-06-03 時点で OpenAI Evals の縮小と Promptfoo への移行を案内しており、**コードと一緒に管理できるポータブルな eval/CI ワークフロー**が現行ベストプラクティスに近い位置づけになっています。 citeturn41view3turn40view0turn24view1turn24view0

Codex固有の自動化面では、第一候補は `codex exec` と `openai/codex-action` です。前者は非対話実行、JSONLイベント、構造化出力、stdin からのプロンプト供給、セッション継続に対応し、後者は GitHub Actions 上で API キー露出を減らすためのプロキシ前提の実装を提供しています。さらに、Hooks は `UserPromptSubmit`、`PreToolUse`、`PermissionRequest`、`PostToolUse`、`PreCompact`、`PostCompact`、`Stop` などのイベントで**決定的な検査やロギング**を差し込めるため、SpecDock がやりたい「監査可能な回帰ハーネス」に非常に相性が良いです。 citeturn41view3turn41view4turn30view0turn31view5turn31view2

評価設計では、**決定的チェックと主観的チェックを混ぜない**ことが最重要です。OpenAI の Graders は `string_check`、`text_similarity`、`multi`、`python`、`score_model` を公開しており、Promptfoo も `equals`、`contains-json`、JSON Schema、JavaScript/Python assertion、model-graded metrics を提供します。これらを使って、PRブロッカーにするのは「ファイル差分」「exit code」「JUnit/pytest 成功」「JSON schema 適合」「指定ファイル未改変」「期待ツール呼び出し」などに限定し、ルーブリックや LLM-as-a-judge は nightly や quarantine 用に分離するのが安全です。OpenAI 自身も、移行時には similarity 系や judge 系の数値がシステム間で一致しない可能性を明示しており、**未校正の judge を merge gate にしない**のが妥当です。 citeturn20view0turn21view0turn21view2turn21view5turn38search2turn38search3turn40view0

CI統合では、OpenAI公式ドキュメントとCookbookが一致して、**生成ジョブと書き込みジョブの分離**を推奨しています。具体的には、Codex 実行ジョブは `contents: read` だけを持ち、チェックアウト時は `persist-credentials: false` を使い、そこで作った差分はパッチ artifact として保存し、別ジョブでだけ `contents: write` / `pull-requests: write` を与えてPR化します。GitHub 側では required status checks、rulesets、branch protection、ユニークな job 名、最新 base branch に対する検証が重要です。ローカルでは pre-commit で安価な決定的チェックを前倒しし、重い agent eval は pre-commit ではなく PR または nightly レーンへ送るのが ergonomic です。 citeturn41view3turn35view0turn26search0turn26search3turn26search7turn26search9turn26search12turn26search2

SpecDock が実装前にまず直接検証すべきポイントは明確です。**現在 pin する Codex CLI バージョンで `--json` の実イベント集合が何か**、**Codex Action の v1 で必要な output schema / output file / patch artifact が揃うか**、**Hooks が non-interactive / CI 実行でも期待どおり動くか**、**AGENTS 階層・skills 発火・compaction イベントの表面差分がないか**、**対象 runner 上で sandbox と approval の挙動がドキュメント通りか**、この五つは issue 化の前提確認です。公開 docs はかなり材料を与えていますが、`codex exec --json` については**公開された versioned schema 契約までは確認できない**ため、SpecDock 側で field-tolerant に扱う前提が安全です。これは本報告の推論です。 citeturn41view3turn30view0turn28view0turn28view1turn31view3turn44view0turn44view3

## ソースマップ

本件で重要度が高かったソースを、**第一者 OpenAI/Codex**、**公開実装例**、**隣接ツール**、**プラットフォーム基盤**に分けて整理します。日付はページに明示されたものか、リリース・更新シグナルです。証拠強度は本報告の評価です。 citeturn40view0turn41view3turn37view0turn26search0

| 区分 | ソース | 日付・鮮度 | 主にカバーする面 | 証拠強度 | SpecDock への関連 |
|---|---|---|---|---|---|
| 第一者 OpenAI/Codex | OpenAI Codex「Non-interactive mode」 citeturn29search6turn41view3turn41view4 | 2026 公開 docs | `codex exec`、JSONL、schema 出力、stdin、CI、認証 | 強 | 非対話レーンの中核仕様 |
| 第一者 OpenAI/Codex | OpenAI Codex「Agent approvals & security」「Sandbox」 citeturn44view0turn44view2turn44view3turn44view4 | 2026 公開 docs | sandbox、approval、network、auto_review、surface 差分 | 強 | 権限・安全境界の基本設計 |
| 第一者 OpenAI/Codex | OpenAI Codex「Hooks」 citeturn30view0turn31view5turn31view2turn31view3turn31view4 | 2026 公開 docs | hook event、stdin/stdout schema、validation、continuation | 強 | trace/log capture と deterministic gate |
| 第一者 OpenAI/Codex | OpenAI Codex「AGENTS.md」「Skills」「Best practices」 citeturn28view0turn28view1turn28view2turn28view3 | 2026 公開 docs | instruction hierarchy、skill invocation、context budget | 強 | prompt/instruction 回帰設計 |
| 第一者 OpenAI/Codex | OpenAI Codex「App Server」 citeturn43view2turn43view4 | 2026 公開 docs | `review/start`、detached review、process/control event | 中〜強 | reviewer independence と review trace |
| 第一者 OpenAI/API | OpenAI API「Working with evals」「Graders」 citeturn19view4turn20view0turn21view0turn21view2turn21view5 | 2026 公開 docs | eval 構成、grader 種別、structured scoring | 強 | deterministic と subjective の分離 |
| 第一者 OpenAI/Cookbook | 「Build iterative repair loops with Codex」「Build an Agent Improvement Loop with Traces, Evals, and Codex」「Macro Evals for Agentic Systems」 citeturn24view1turn24view0turn40view1 | 2026-05 | repair/validate loop、trace→eval flywheel、macro eval patterns | 強 | PDCA ハーネス全体像 |
| 第一者 OpenAI/Cookbook | 「Build Code Review with the Codex SDK」「Use Codex CLI to automatically fix CI failures」「Building Consistent Workflows with Codex CLI & Agents SDK」 citeturn34view1turn35view0turn34view2 | 2025-09〜10 | GitHub Actions、structured outputs、CI patch flow、traceability | 強 | CI 実装テンプレート |
| 第一者 OpenAI/Cookbook | 「Moving from OpenAI Evals to Promptfoo」 citeturn40view0 | 2026-06-03 | Evals 縮小、Promptfoo への移行 | 強 | 評価基盤の選定方針 |
| 隣接ツール | Promptfoo docs: CI/CD, GitHub Action, coding-agent red-team, model drift, assertions | 2026-06 更新シグナルあり citeturn37view0turn37view1turn37view3turn37view4turn37view5turn38search0turn38search2turn38search3 | prompt regression、agent red-team、CI lanes、schema/assertions | 強 | OpenAI が推奨するコード指向 eval 実装面 |
| プラットフォーム基盤 | GitHub Docs: status checks, protected branches, rulesets, Checks API | 2026 docs citeturn26search0turn26search3turn26search7turn26search9turn26search12turn26search18 | branch protection、required checks、PR gating | 強 | merge gate と運用統制 |
| 隣接ツール | Anthropic Claude Code docs: GitHub Actions, common workflows, CLI reference | 2026 docs citeturn36search1turn36search4turn36search10 | repo guidance、worktrees、script/CI integration | 中 | Codex以外でも収束している共通パターンの比較証拠 |
| 基盤ツール | pre-commit 公式 docs citeturn26search2 | 継続更新 | ローカルの cheap deterministic gate | 強 | 開発者 ergonomics の土台 |

この表からの読み筋は単純です。**Codex 実行面は第一者ドキュメントで十分に設計可能**、**評価運用面は OpenAI 自身が Promptfoo への移行を明示**、**PR gate の強制力は GitHub の status/ruleset に依存**、という三層構造です。したがって SpecDock は、Codex を「実行エンジン」、Promptfoo などを「評価オーケストレーター」、GitHub を「統制ゲート」として分離して考えるのが自然です。 citeturn40view0turn41view3turn26search12

## Codex固有の自動化面

### 非対話実行と機械可読出力

`codex exec` は OpenAI が公式に「scripts や CI で使う非対話モード」として案内している表面です。`--json` を付けると `stdout` は JSONL イベント列になり、`thread.started`、`turn.started`、`turn.completed`、`turn.failed`、`item.*`、`error` が流れます。item には agent message、reasoning、command execution、file changes、MCP tool call、web search、plan update などが含まれます。また `--output-schema` で最終出力を JSON Schema に拘束でき、`-o` / `--output-last-message` で最終メッセージをファイルへ残せます。プロンプト自体を stdin から供給する `codex exec -` や、二段階パイプライン向けの `codex exec resume --last` も公開されています。これは regression harness の**runner 契約**としてかなり扱いやすいです。 citeturn41view3turn41view4

この表面の実務的な意味は、SpecDock が最初から「会話UIのスクリーンショット」や「最後の prose」ではなく、**event stream・structured final output・verifier artifacts**を一次証拠として持てることです。特に `--json` のイベント列があるため、実行中に何をしたか、どの turn で止まったか、コマンド実行があったか、ファイル変更が発生したかを後段で再計算できます。公開 docs は event family を示していますが、完全な versioned schema 契約までは出していません。したがって SpecDock 側では unknown field を許容し、必須なのは `type` と判定に必要な最小 subset だけに絞る設計が堅い、というのが本報告の推論です。 citeturn41view3turn30view0

### 権限、サンドボックス、認証

Codex では sandbox mode と approval policy が別レイヤです。CLI/App/IDE 共通の概念として、`read-only`、`workspace-write`、`danger-full-access` の sandbox があり、approval は `untrusted`、`on-request`、`never` です。公開 docs では、ローカルの低摩擦な既定は `workspace-write` と `on-request` の組み合わせ、`read-only` は観察専用、`danger-full-access` は sandbox 境界を外すため高リスクと整理されています。一方、**non-interactive の `codex exec` はデフォルト read-only** で、CI では必要最小の明示権限を付けるよう案内されています。ここは surface ごとの差分であり、SpecDock がローカル対話と CI 非対話を同じ前提で扱うと誤ります。 citeturn44view3turn44view4turn41view3

ネットワークと承認の扱いも重要です。OpenAI のセキュリティ docs は、ローカル既定ではネットワーク off、CI では `danger-full-access` を安易に使わず、必要に応じて `workspace-write` を基本にすることを推奨しています。より広い例外が必要なときは sandbox を広げるより rules で command prefix を allow/prompt/forbid するほうが良いとも述べています。また `approvals_reviewer = "auto_review"` は承認境界を置き換えるのではなく、**承認境界上のレビュー担当を user から reviewer agent に変えるだけ**です。つまり Auto-review を使っても sandbox を広げる口実にはなりません。 citeturn44view0turn44view3turn44view5

認証面では、OpenAI は GitHub Actions で `OPENAI_API_KEY` や `CODEX_API_KEY` を job-level env として repo-controlled code に晒す運用を明確に避けるよう案内しています。その代わりに `openai/codex-action` を使い、アクション内部のプロキシ経由で Codex を動かす設計を推しています。さらに、公式の CI pattern は「Codex 実行ジョブは read 権限だけ」「差分は patch artifact 化」「PR 作成は別ジョブ」という分離です。SpecDock でも secrets が見える job と repo code を実行する job を同一視しないことが必須です。 citeturn41view3turn35view0

### Hooks、レビュー、トレース、現時点の制約

Hooks は Codex を regression harness に寄せるうえで最も強い表面です。公式 docs によれば、各 hook は JSON を stdin で受け取り、`session_id`、`transcript_path`、`cwd`、`hook_event_name`、`model` を共通入力として持ちます。`PreToolUse` と `PostToolUse` では `tool_name`、`tool_use_id`、`tool_input`、`tool_response` が取れ、`PermissionRequest` では allow/deny を返せ、`UserPromptSubmit` では追加 developer context や block を返せます。`Stop` hook は turn 完了時に continuation prompt を生成できるため、**「検証失敗ならもう一周」**という PDCA ループを Codex 自体の turn lifecycle に差し込めます。さらに docs は Hooks の典型例として custom logging/analytics engine 送信、API key の誤貼り付け防止、turn 終端 validation を明示しています。これは SpecDock の trace/log capture と deterministic validation の両方に直結します。 citeturn30view0turn31view5turn31view2turn31view3turn31view4

ただし制約もはっきりしています。公開 docs では、複数の command hooks は同一イベントで並行起動され、`async: true` な command hook はまだ未対応、`prompt` と `agent` タイプの handler は parse はするが実行されません。また `Stop` / `SubagentStop` / `PostToolUse` の block は「すでに起きたツール実行を巻き戻す」意味ではなく、**結果を feedback で置き換えて次の turn を継続する**意味です。したがって Hook は検査・追記・拒否・継続制御には強い一方、トランザクション的な rollback は別途 verifier 側で扱う必要があります。 citeturn30view0turn31view2turn31view7

レビュー面では、App Server の `review/start` が重要です。公式 docs では、レビュー対象は uncommitted changes、base branch diff、specific commit、custom instruction を取り、`delivery: "inline"` と `delivery: "detached"` を切り替えられます。detached では新 review thread が立ち、`enteredReviewMode` と `exitedReviewMode` が stream されます。これは SpecDock にとって、**実装スレッドから独立した reviewer thread を走らせる実験**、つまり reviewer independence test の構成要素です。さらに App Server は `command/exec` や experimental な `process/*` も公開していますが、`process/*` は明示的に sandbox の外で動く experimental API とされており、回帰ハーネスの標準経路に入れるべきではありません。 citeturn43view2turn43view4

OpenAI Agents SDK の tracing は Codex CLI そのものではありませんが、Codex-centered workflow を Agents SDK で包むときの near-first-party な観測面として有用です。Tracing は既定で有効で、workflow 単位の trace と agent / generation / function / guardrail / handoff span を自動収集し、必要なら custom processor で別送もできます。長時間 worker では `flush_traces()` を明示的に呼ぶパターンも公式に示されています。一方で ZDR 組織では tracing が使えない点は要注意です。SpecDock が CLI 直行にせよ Agents SDK 併用にせよ、**trace export 不能環境と trace rich 環境を両対応**にしておくべきです。 citeturn24view2turn22search2

## 公開ハーネス実装パターン

### 観測された構成と runner 契約

OpenAI Cookbook の 2026 例では、Codex を単発実行ではなく**閉ループ**として使うパターンが明確に出ています。`Build iterative repair loops with Codex` は、artifact を review し、結果をもとに repair し、validator で validate して、残課題を次回入力に戻す三相ループを headless Codex で回しています。`Build an Agent Improvement Loop with Traces, Evals, and Codex` は、trace を収集し、人手とLLMの feedback をつけ、それを Promptfoo eval に落とし、HALO で次の改善候補を順位づけして `codex_handoff.md` にまとめます。`Macro Evals for Agentic Systems` は、`trace_results.jsonl`、`eval_labels.jsonl`、`trace_bundles.zip` を別ファイルで保ち、lower-level eval と population-level pattern discovery を分けています。共通点は、**run 自体・評価ラベル・人間判断・次の変更指示を別 artifact にしていること**です。 citeturn24view1turn24view0turn40view1

SpecDock で採るべき runner 契約も、これに近い形がよいです。最低限でも、各ケースについて「入力 repo seed」「prompt / AGENTS / skills」「Codex 実行 JSONL」「最終 structured output」「git diff / patch」「verifier 結果」「summary report」を別 artifact に分けるべきです。OpenAI 公式の CI autofix パターンも、生成物として patch artifact を保存し、書き込み権限のある別ジョブでのみ適用・PR化します。これにより「Codex が何を提案したか」と「PR として何を適用したか」を監査上分離できます。 citeturn41view3turn35view0

以下は、公開パターンを踏まえた **SpecDock 向けの推奨 fixture layout** です。これは本報告の設計提案であって、OpenAI 公式ファイル構成ではありません。根拠は上記の Cookbook 群、Promptfoo の coding-agent guide、Codex Hooks/exec docs にあります。 citeturn24view1turn24view0turn40view1turn37view3turn41view3turn30view0

```text
fixtures/
  case-001-minimal-ci-fix/
    seed/                       # 初期リポジトリ状態
    prompt.md                   # user prompt
    AGENTS.md                   # case固有 instruction
    .agents/skills/...          # 任意。skill invocation test 用
    expect/
      verifier_contract.json    # 期待する検証契約
      allowed_files.txt         # 変更許可ファイル
      forbidden_files.txt       # 改変禁止ファイル
    scripts/
      setup.sh                  # seed展開、依存解決
      verify.sh                 # 決定的検証
      redact.py                 # trace redaction
    artifacts/
      manifest.schema.json      # artifact manifest の schema
```

runner は**ケースごとに fresh checkout / fresh writable workspace** を作るべきです。Promptfoo の coding-agent guide は、実リポジトリを複数 row で再利用すると canary・tool receipts・modified verifier などで後続結果が汚染されると明記しています。この警告は Codex 固有ではありませんが、agent regression harness では極めて重要です。ワークスペース再利用は、フレークというより**設計バグ**として扱うべきです。 citeturn37view3

### 小さい決定的フィクスチャとゴールデン設計

公開資料が共通して示すのは、「現実的だが自己完結した小さい fixture」を使うことです。OpenAI の improvement loop は synthetic company data を**ランタイムに生成**して self-contained にしながら realistic な conflicting evidence を持たせています。repair loop は intentionally stale notebooks を使い、validator が信頼できる feedback source になるようにしています。macro eval は precomputed trace と label を bundled data として配り、オフラインでも再現できる形にしています。つまり golden は「自然言語の正答そのもの」より、「問題設定・検証器・期待される artifact contract」のほうに寄せるべきです。 citeturn24view0turn24view1turn40view1

OpenAI の Evals / Graders もこの方向を裏付けています。`string_check` は exact match、`multi` は複数 grader の組み合わせ、`python` は任意の deterministic grading code、`score_model` は numeric rubric を扱えます。Promptfoo 側でも deterministic metrics と JSON Schema assertion があり、Codex SDK provider では final text に対して output schema を適用できます。したがってゴールデンは、**文面の完全一致ではなく次の粒度**で作るのがよいです。出力 JSON の schema、必要 field の有無、変更してよいファイル集合、禁止ファイルの sha256 不変、検証スクリプト exit code、JUnit/pytest 成功、所定の tool call 名・引数、artifact manifest の整合性、などです。 citeturn20view0turn21view0turn21view2turn38search2turn38search11

反対に、agent の最後の prose を snapshot test するのは危険です。OpenAI の migration guide は similarity 系や LLM grader の数値がシステム間で一致しない可能性を明言していますし、Promptfoo も deterministic metrics と model-graded metrics を分けています。SpecDock の golden は「phrasing ではなく contract」を固定し、「説明文」は advisory evidence に下げるべきです。これは false confidence を避けるうえで本質的です。 citeturn40view0turn38search2turn38search6

### 指示回帰、敵対テスト、レビュー独立性

プロンプト / instruction regression では、Codex の `AGENTS.md` と skills をそのままテスト対象にできます。`AGENTS.md` は root から current working directory までを連結し、近い階層が後勝ちで override します。default cap は 32 KiB です。skills は最初に metadata だけが context に入り、full `SKILL.md` は採用時のみ読み込まれます。初期 skill list は context window の約 2% または 8,000 文字程度に制限されるので、SpecDock は **instruction hierarchy regression** として、nested AGENTS precedence、fallback filename、project_doc_max_bytes 上限、explicit skill invocation、implicit skill match、metadata truncation 時の挙動を個別 fixture 化できます。 citeturn28view0turn28view1turn28view2

コンテキスト圧縮もテスト対象です。Codex Prompting Guide は compaction を multi-hour reasoning 支援の重要改善として挙げ、Hooks は `PreCompact` / `PostCompact` イベントを公開しています。したがって long-running / handoff 系ケースでは、「compaction 前に存在した重要 instruction が compaction 後も守られるか」「compaction 後に verifier summary を再注入できるか」を regression に入れる価値があります。これは短い unit test ではなく、**圧縮を意図的に起こす synthetic conversation** で測るべきです。 citeturn34view0turn31view3

敵対 instruction-following については、Promptfoo の coding-agent plugin 群が比較的まとまった taxonomy を提供しています。公開 plugin には repo prompt injection、terminal output injection、secret env/file read、sandbox read/write escape、network egress bypass、delayed CI exfil、automation poisoning、steganographic exfil、verifier sabotage があり、しかも Codex SDK 向け設定例まであります。OpenAI 側の governance cookbook も、guardrail eval と red-team を別物として組み合わせるべきだと説明しています。SpecDock ではこれをそのまま「Codex requirement」とは扱わず、**adjacent comparison evidence** として「こういう adversarial suite が必要な範囲」を定義する材料に使うのが妥当です。 citeturn37view3turn37view2turn37view5turn40view2

レビュー独立性については、Codex App Server の `review/start` が detached thread を公式に許可しています。これを使えば、実装をしている main thread と、diff だけを見てレビューする detached review thread を分離できます。SpecDock が将来 reviewer independence test を設けるなら、**同じ seed / 同じ diff に対して** inline review と detached review を比較し、「main thread の prior context が reviewer を過剰に甘くしていないか」を見るのが筋です。これは公開 docs から導ける有力なテスト設計であり、本報告の推論です。 citeturn43view2turn43view4

## 評価と採点の設計

### 決定的チェックと主観チェックの分離

OpenAI の Evals docs は、eval を `data_source_config` と `testing_criteria` に分け、`string_check` のような grader で exact comparison を行う基本形を示しています。Graders docs では、tool call の function name と arguments を `multi` でまとめたり、`python` grader で任意ロジックを埋め込んだりできます。Promptfoo でも JSON schema、exact/regex/text similarity、JavaScript/Python assertions、threshold を使えます。よって SpecDock の PR gate は、**失敗したら人が納得しやすい決定的条件だけ**に寄せるべきです。具体的には、verifier exit code、禁止ファイルの不変、schema 適合、必要 artifact の存在、expected tool path、patch scope などです。 citeturn20view0turn21view0turn21view2turn38search0turn38search2turn38search3

一方、`score_model` のような judge 系は numeric score、pass threshold、score range、sampling params を持てるので、品質を見るには便利です。しかし OpenAI 自身が migration guide で「similarity-based scoring は同一数値にならない」「LLM-as-a-judge は validation が必要」と言っています。したがって judge は**merge blocker ではなく diagnosed signal**として扱うべきです。SpecDock では `gate.deterministic/*` と `eval.subjective/*` を artifact 上もレーン上も分け、後者が落ちても即 merge 拒否にはしない設計が安全です。 citeturn21view5turn20view6turn40view0

### ルーブリック、structured outputs、外部 grader

Structured outputs は、レビューでも regression でも効きます。OpenAI Cookbook の code review 例は、Codex に structured output schema を与え、inline review comment を SCM API に流し込む前提を取っています。Promptfoo の JSON guide と deterministic metrics も、まず valid JSON や schema 適合を検証し、その後必要 field を assertion するやり方を勧めています。SpecDock では subjective rubric であっても、**judge の入力は自由文、judge の出力は必ず構造化**にするべきです。例えば `{"score":0.8,"verdict":"warn","reasons":[...],"evidence_refs":[...]}` のようにしておけば、後続の集計・閾値判定・macro eval に載せやすくなります。 citeturn34view1turn38search1turn38search2

さらに、OpenAI の macro eval cookbook は lower-level eval と macro eval を分けています。これは SpecDock の agent workflow PDCA にそのまま当てはまります。まず individual run に対して「tool 選択」「policy 遵守」「review の入り方」「最終結果」の lower-level label を付け、その後に `case_type`、`run_outcome`、`eval_finding`、`behavior_pattern` のような集約ラベルで recurring failure を探すのが良いです。PR gate で全部を見る必要はありません。むしろ recurring pattern は nightly/weekly の macro lane に送ったほうが、開発者体験を壊しません。 citeturn40view1

### フレーク、長時間評価、信頼区間

公開資料は「flaky eval をゼロにする」より「レーン分離・再実行・比較」で扱う方向です。Promptfoo の drift docs は baseline を保存し、定期 scan を回し、ASR や pass rate の変化を見る運用を勧めています。best practices では multi-turn attacks、grader calibration、Retry の有効化を明示しています。OpenAI の改善系 cookbook も、1回の run 結果を絶対視せず、trace と feedback を次の eval に変換して飛輪にしています。つまり flaky or long-running agent eval は、**PR で全件直列実行するものではない**というのが公開実践の共通項です。 citeturn37view4turn37view5turn24view0

SpecDock 向けの現実的なレーン分割は、次の三層です。PR では smoke 級の deterministic fixtures だけ、merge-to-main では少し広い deterministic suite と軽い subjective spot-check、nightly では adversarial / macro / long-running を回す構成です。judge スコアは単回値ではなく、**中央値か最悪値、あるいは一定回数の pass rate**で持つべきです。`confidence band` の明示は今回の公開資料では直接見つかっていませんが、drift detection と retry を踏まえると、そのような統計的扱いが自然だというのが本報告の推論です。 citeturn37view4turn37view5

以下は、公開パターンを踏まえた **推奨スコアリング分離表** です。これは提案であり、OpenAI 公式フォーマットではありません。 citeturn20view0turn21view5turn38search2turn40view1

| レーン | 目的 | 主な判定器 | merge gate への使い方 |
|---|---|---|---|
| deterministic smoke | 壊してはいけない契約確認 | exit code、schema、hash、file allowlist、tool call check | そのまま required check |
| deterministic full | 実ワークフローの再現確認 | fixture verifier、artifact manifest、patch scope | main への必須チェック候補 |
| subjective rubric | 品質・説明責任・レビュー妥当性 | `score_model`、Promptfoo model-graded | advisory、失敗は quarantine |
| adversarial security | injection/exfil/sabotage 耐性 | Promptfoo red-team / custom attack set | nightly と drift baseline |
| macro eval | recurring pattern 発見 | lower-level labels の集計 | issue 生成と PDCA 入力 |

## CI統合とSpecDock候補Issue

### GitHub Actions、pre-commit、branch protection

OpenAI の公式 non-interactive / cookbook パターンは、GitHub Actions での Codex 利用についてかなり具体的です。安全側の実装は、**read-only の生成ジョブで Codex を動かし、差分だけを artifact 化し、write 権限を持つ別ジョブで PR を開く**構成です。docs では `persist-credentials: false` を付けた checkout、`contents: read` の generate job、patch artifact の受け渡し、`OPENAI_API_KEY` を open_pr job に持ち込まない設計が示されています。この分離は agent workflow harness でもそのまま採るべきです。Codex が repo-controlled code を実行するジョブと、repo に書くジョブを同一にしないことが重要です。 citeturn41view3turn35view0

GitHub 側の制約も忘れてはいけません。required status checks は protected branch / ruleset の一部として強制でき、job 名は workflow 横断でユニークである必要があります。さらに required check として扱うには、その check が最近 7 日以内に成功している必要があり、branch が base branch に追随していないと merge 前に再検証が必要になる場合があります。SpecDock が `codex-regression`, `codex-redteam`, `codex-nightly` のような check を増やすなら、**名前衝突しない運用設計**も acceptance criteria に含めるべきです。 citeturn26search0turn26search3turn26search7turn26search9turn26search12

ローカルでは pre-commit が便利ですが、用途を誤ると逆効果です。pre-commit は multi-language hook manager として、root 権限なしに hook を配布・実行できます。Codex の best practices も、AGENTS.md を pre-commit hooks、linters、type checkers と組み合わせて recurring mistakes を infrastructure で防ぐよう勧めています。したがって pre-commit に載せるべきなのは、JSON schema validation、fixture manifest lint、禁止ファイル検査、prompt/config の静的整合性などの**秒単位で終わる決定的チェック**です。agent run 自体を commit 時に走らせるのは developer ergonomics を壊します。 citeturn26search2turn28view3

### コスト、実行時間、レーン分割

Codex Prompting Guide は medium reasoning effort を一般的な対話コーディングのバランス点としつつ、長時間タスクでは high / xhigh を想定しています。公開 cookbooks も long-running autonomy や multi-hour planning を前提にしています。したがって regression harness は、**常に最高性能モデル・高 reasoning で全件実行する**構成にしないほうがよいです。PR lane では件数を小さくし、nightly でのみ広い suite と adversarial を回し、macro eval はバッチで集計するほうが、コストと待ち時間の両方に耐えます。 citeturn34view0turn32search3turn24view0

また、OpenAI が Evals から Promptfoo への移行を明示している以上、SpecDock の eval 定義は**リポジトリ同居の config**として持つのが安全です。これは将来の tool change にも強く、CI でもローカルでも同じ config を回せます。OpenAI Evals 側は移行元・履歴保存先として扱い、継続運用の一次表面にしないほうが良いです。 citeturn19view4turn40view0

### epic-00158 向けの候補Issue

以下は**最終要件ではなく、公開ソースから導いた candidate issue**です。タイトル、問題、根拠、影響箇所、受け入れ証拠だけを整理しています。SpecDock 固有のファイル名は仮置きです。 citeturn41view3turn30view0turn24view0turn37view3turn26search12

| 候補タイトル | 問題 | ソース根拠 | 影響しそうなファイル / docs | 受け入れ証拠 |
|---|---|---|---|---|
| Codex exec JSONL capture lane の追加 | Codex run の可観測性が prose 依存だと監査不能 | `--json` JSONL、item event、公的 docs citeturn41view3turn30view0 | `tools/agent-runner/*`, `docs/testing/agent-runs.md` | run ごとに JSONL が保存され、必須 event subset を parse できる |
| patch artifact 分離ジョブの導入 | 生成と repo 書き込みが同一 job だと secret 境界が弱い | OpenAI 公式 split-job pattern、GitHub rulesets citeturn41view3turn35view0turn26search9 | `.github/workflows/codex-regression.yml` | generate job は read-only、open_pr job だけ write。secret は前者に限定 |
| 最小決定的 fixture contract の策定 | 大きすぎるケースは flake と保守費用を増やす | OpenAI synthetic/offline fixtures、Promptfoo fresh checkout 警告 citeturn24view0turn40view1turn37view3 | `fixtures/*`, `docs/testing/fixtures.md` | 各 fixture に seed / verify / expected contract が揃い、fresh workspace で完走 |
| AGENTS hierarchy 回帰パック | 指示の優先順位崩れは silent regression になりやすい | AGENTS precedence、closest wins、size cap citeturn28view0turn28view2 | `fixtures/instructions/*`, `docs/testing/instructions.md` | nested AGENTS ケースで期待 precedence が再現される |
| skill invocation と compaction 回帰パック | skill metadata truncation や compaction が振る舞いを崩す可能性 | Skills progressive disclosure、Pre/PostCompact hooks、compaction support citeturn28view1turn31view3turn34view0 | `fixtures/skills/*`, `fixtures/compaction/*` | explicit/implicit skill と compaction 後の再現ケースがある |
| verifier/artifact manifest 契約の追加 | self-reported completion を成功扱いすると虚偽陽性が出る | repair loop の validate phase、structured outputs、deterministic assertions citeturn24view1turn34view1turn38search2 | `schemas/artifact-manifest.schema.json`, `scripts/verify/*` | 成功 run には manifest + verifier report + diff hash が必須 |
| adversarial instruction-following lane の追加 | prompt injection / exfil / verifier sabotage を未検査 | Promptfoo coding-agent plugins、governance guide citeturn37view3turn40view2 | `promptfoo/promptfooconfig.yaml`, `.github/workflows/redteam.yml` | nightly で adversarial suite が走り、ASR baseline が保存される |
| subjective graders nightly lane の追加 | merge gate に judge を混ぜるとノイズが高い | OpenAI graders、Promptfoo model-graded、migration caution citeturn21view5turn38search6turn40view0 | `evals/subjective/*`, `.github/workflows/nightly-evals.yml` | judge 系は nightly のみ。PR 必須 check から分離されている |
| trace redaction と retention policy 文書化 | hook/transcript/log に秘密が残る恐れ | hook の `transcript_path`、CI auth warnings、ZDR tracing 制約 citeturn31view5turn41view3turn24view2 | `docs/security/agent-traces.md`, `scripts/redact/*` | redaction ルール、保存期間、秘密検査が文書化され自動テストあり |
| detached reviewer 実験レーン | reviewer が main thread context に引っ張られる恐れ | `review/start` detached thread、公的 review events citeturn43view2turn43view4 | `experiments/reviewer-independence/*` | 同一 diff に対して inline/detached の差分比較レポートが出る |

## 証跡スキーマと実装前確認

### 推奨 artifact / trace スキーマ

公開 docs の event surface を踏まえると、SpecDock は `codex exec --json` の raw JSONL をそのまま保存しつつ、別途**正規化 manifest**を作るのがよいです。Raw は再解析用、manifest は検索・集計・PR 表示用です。raw だけでは field drift に弱く、manifest だけでは forensic value が足りません。Hooks からは `session_id`、`transcript_path`、`cwd`、`turn_id`、`tool_name`、`tool_use_id`、`tool_input`、`tool_response` が取れ、App Server では detached review thread や review mode event も拾えます。これらを合わせれば「何を入力し、どの instruction chain で、どの tool を、どの承認状態で使い、何を変え、何で検証したか」をかなり細かく残せます。 citeturn41view3turn31view5turn31view4turn43view2turn43view4

推奨する manifest の最小 field は、`run_id`、`case_id`、`surface`、`codex_version`、`model`、`reasoning_effort`、`repo_sha`、`sandbox_mode`、`approval_policy`、`approvals_reviewer`、`prompt_hash`、`agents_chain_hashes`、`skills_selected`、`status`、`started_at`、`ended_at`、`diff_sha256`、`changed_files[]`、`verifier.status`、`verifier.exit_code`、`evidence_refs[]`、`redactions{}`、`unknown_fields{}` です。`status` は最低でも `passed / failed / blocked / error / quarantined / unknown` を持ち、**unknown を pass に昇格させない**べきです。これは公開 docs の event と security guidance を踏まえた本報告の推奨スキーマです。 citeturn41view3turn30view0turn31view2turn44view2

以下は、実装イメージの簡易例です。これは公式 schema ではなく、本報告の推奨例です。 citeturn41view3turn31view5turn43view2

```json
{
  "run_id": "run_20260605_case001",
  "case_id": "case-001-minimal-ci-fix",
  "surface": "codex-exec",
  "codex_version": "0.137.0",
  "model": "gpt-5.3-codex",
  "reasoning_effort": "medium",
  "repo_sha": "abc123...",
  "sandbox_mode": "workspace-write",
  "approval_policy": "on-request",
  "approvals_reviewer": "user",
  "prompt_hash": "sha256:...",
  "agents_chain_hashes": ["sha256:root-agents", "sha256:pkg-agents"],
  "skills_selected": ["ci-fix-skill"],
  "status": "passed",
  "started_at": "2026-06-05T01:23:45Z",
  "ended_at": "2026-06-05T01:24:12Z",
  "changed_files": ["src/foo.ts", "tests/foo.test.ts"],
  "diff_sha256": "sha256:...",
  "verifier": {
    "status": "passed",
    "exit_code": 0,
    "report_path": "artifacts/verifier-report.json"
  },
  "evidence_refs": [
    "artifacts/run.jsonl",
    "artifacts/final-output.json",
    "artifacts/patch.diff",
    "artifacts/junit.xml"
  ],
  "redactions": {
    "env_secret_hits": 0,
    "file_secret_hits": 0
  },
  "unknown_fields": {}
}
```

### アンチパターンと主要リスク

最も危険なアンチパターンは、**最後の「直しました」「終わりました」を成功証拠にすること**です。OpenAI の closed-loop 例は validate phase を必須にし、Promptfoo の coding-agent red-team も verifier sabotage を独立脅威として扱っています。成功は self-report ではなく verifier と artifacts で確定させるべきです。 citeturn24view1turn37view3

次に危険なのは、**自然言語の出力スナップショットを強く固定すること**です。OpenAI の migration guide は judge 系・similarity 系の不一致可能性を認めており、Promptfoo も deterministic と model-graded を分けています。prose snapshot は brittle で、モデル改善や phrasing variation を regression と誤検知しやすいです。ゴールデンは schema・tool call・artifact contract・verifier に寄せるべきです。 citeturn40view0turn38search2turn38search6

第三に、**同じ writable workspace を複数 test row で再利用すること**です。Promptfoo は coding agent 評価で fresh checkout を明示的に警告しています。agent はファイル、terminal receipts、generated artifacts、verifier まで書き換えるため、共有 workspace はケース間依存を生みます。回帰ハーネスとしては許容できません。 citeturn37view3

第四に、**Secrets を見える job と repo-controlled code を走らせる job を同居させること**です。OpenAI は GitHub Actions で job-level の API キー露出を避けるよう繰り返し警告し、Codex job と PR 作成 job を分離しています。これは security 問題であると同時に、回帰ハーネスの信頼性問題でもあります。secret 汚染された結果は再利用しにくいからです。 citeturn41view3turn35view0

第五に、**`danger-full-access` を標準レーンに置くこと**です。公式 docs は full access を高リスクと位置づけ、rules や writable roots での限定拡張を勧めています。標準回帰レーンは `workspace-write` を基本にし、危険権限は isolated runner や dedicated experiment lane のみに閉じ込めるべきです。 citeturn44view3turn44view4turn44view2

### 実装前の確認事項

実装に入る前に、少なくとも次の確認が必要です。いずれも公開情報から**必要性が高い**と判断できる項目です。 citeturn41view3turn30view0turn28view0turn44view0

- `codex exec --json` で、SpecDock が使う pin version の event 種別と field を実測し、parser の必須 field を最小化できているか。 citeturn41view3
- `openai/codex-action@v1` で、patch artifact・output schema・output file・sandbox 設定がターゲット runner で期待通り動くか。 citeturn41view3turn34view1
- Hooks が CI 上の non-interactive 実行でも信頼レビューや bypass 方針を含めて運用可能か。特に non-managed hooks の trust フローを確認したか。 citeturn30view0
- AGENTS の precedence、skill の明示/暗黙発火、skill metadata budget、compaction hook が現在の Codex build で再現するか。 citeturn28view0turn28view1turn31view3
- プライバシー方針として、`transcript_path`、JSONL、verifier report、artifact manifest から何を保存し、何を redaction し、どれだけ保持するかを決めたか。 citeturn31view5turn41view3turn24view2
- GitHub の required checks 名、ruleset、branch protection を最終的な workflow 名と矛盾なく設計したか。job 名一意性も確認したか。 citeturn26search3turn26search9turn26search12
- judge 系 rubric について、失敗ケースを人手で数十件レビューし、閾値・rubric 文・retry 方針を校正したか。未校正 judge を merge gate にしていないか。 citeturn40view0turn37view5
- adversarial lane について、fresh workspace 原則・canary 値・保護対象ファイル・verifier sidecar JSON の契約を定義したか。 citeturn37view3

### 主要参照ソース

本報告の核に置いたソースを再掲します。引用は本文に埋め込んでいるため、ここでは系統を整理する目的に留めます。 citeturn29search6turn30view0turn28view0turn40view0turn37view0

- OpenAI Codex docs: Non-interactive mode、Agent approvals & security、Sandbox、Hooks、AGENTS.md、Skills、Best practices、App Server。 citeturn29search6turn44view0turn44view3turn30view0turn28view0turn28view1turn28view2turn43view2
- OpenAI API docs: Working with evals、Graders。 citeturn19view4turn21view5
- OpenAI Cookbook: Build iterative repair loops with Codex、Build an Agent Improvement Loop with Traces, Evals, and Codex、Macro Evals for Agentic Systems、Build Code Review with the Codex SDK、Use Codex CLI to automatically fix CI failures、Moving from OpenAI Evals to Promptfoo。 citeturn24view1turn24view0turn40view1turn34view1turn35view0turn40view0
- OpenAI Agents SDK tracing docs。 citeturn24view2turn22search2
- Promptfoo docs: CI/CD、GitHub Action、coding-agent red-team、model drift、assertions / deterministic metrics。 citeturn37view0turn37view1turn37view3turn37view4turn38search0turn38search2turn38search3
- GitHub Docs / pre-commit: status checks、protected branches、rulesets、Checks API、pre-commit。 citeturn26search0turn26search3turn26search7turn26search12turn26search18turn26search2
- 隣接比較: Claude Code GitHub Actions / common workflows / CLI reference。非Codexだが、repo-scoped guidance、worktrees、scriptable CI の共通設計傾向を見る比較材料として参照。 citeturn36search1turn36search4turn36search10

### 不確実性と次に掘るべき枝

今回の公開調査で残った不確実性は三つです。第一に、`codex exec --json` の**versioned event schema** は確認できず、公開 docs は event family とサンプル中心です。第二に、Auto-review の surface 別細部、特に CLI / App / GitHub integration で何がどこまで等価かは、今回取得した資料だけでは十分に詰め切れていません。第三に、Codex Action の provider overlay や custom `CODEX_HOME` との衝突のような実運用エッジケースは、公開 issue はあるものの、第一者確定情報としてまでは扱いませんでした。これらは SpecDock が actual pinned version と runner で**先に実測確認**すべきです。 citeturn41view3turn44view3turn29search11

次に掘る価値が高い枝は、**Codex Action の現行 input/output 契約の実測表**、**Hooks を使った turn-end verifier の最小実装検証**、**detached reviewer thread の差分評価実験**、**Promptfoo 側の Codex SDK provider を使うか、SpecDock 独自 runner + Promptfoo assertions に分けるかの比較**、この四つです。ここは公開 docs だけではなく、SpecDock が target version で smoke 実験して初めて確証が持てる領域です。 citeturn34view1turn30view0turn43view2turn38search11