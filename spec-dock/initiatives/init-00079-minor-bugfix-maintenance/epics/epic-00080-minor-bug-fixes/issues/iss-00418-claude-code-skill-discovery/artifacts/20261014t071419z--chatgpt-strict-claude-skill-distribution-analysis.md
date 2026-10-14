# ChatGPT Strict 分析: SpecDock スキルを Claude Code から発見可能にする配布方式

外部モデルの出力（evidence）です。採用した内容は Requirement / Design / Plan / accepted ADR へ明示的に再記述してください。

## 実行情報

- 実行日: 2026-10-14
- 経路: `chatgpt-use-strict`（Oracle browser）
- Oracle session: `required-strict-github-connector-verificati-1429`
- 検証対象: `chemitaro/spec-dock` `main` @ `0e7dc86841cb48d011270a1a2165cb6406ac0cea`（ChatGPT が GitHub コネクタで branch 先端 SHA を照合済み）
- モデル選択証拠: requestedKey=gpt-6-pro, resolvedLabel=GPT-6, thinking=Pro, verified=yes
- 所要時間: 16m43s
- 注記: 回答中「ADR が 404」とあるのは、依頼側が Git 管理外のミラー symlink `spec-dock/adrs/...` を指定したため。正本は `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00384-provider-test-strategy-simplification-and-execution-cost-reduction/artifacts/20260831t005139z-adr-disposable-provider-roots-and-fixed-skill-slots.md`。

## 送信したプロンプト

````markdown
SpecDock の同梱スキルを Claude Code から認識できるようにする配布方式について、独立した設計分析を依頼します。回答は日本語の Markdown テキストでお願いします（ウィジェットやキャンバスは使わないでください）。

## 決めたいこと

SpecDock を導入したリポジトリで、Codex と Claude Code の両方が SpecDock 同梱スキル（`spec-dock`、`spec-dock-grill-with-docs`）を発見・利用できるようにするためのベストプラクティスの配布方式。

## 問題

`spec-dock installation init/update` は、パッケージ同梱のスキルを対象 worktree の `.agents/skills/<name>/` に通常ファイルとして配置する。Codex をはじめ多くのホストは `.agents/skills` を読むが、Claude Code は `.claude/skills`・`~/.claude/skills`・プラグイン・`--add-dir` 内の `.claude/skills` しか読まない。そのため SpecDock を導入しても Claude Code からはスキルが見えない。添付の facts.md に、公式ドキュメントで確認した各ホストの探索仕様と、ローカル環境の観測を記載した。

## 読んでほしいリポジトリ内の根拠（検証済みコミット上）

- `src/spec_dock/asset_layout.py`、`src/spec_dock/runtime/infra/static_assets.py`（インベントリのパス allowlist。`path` と `source` が分離されている）
- `src/spec_dock/assets/static-inventory.json`（各ファイルの sha256・mode・known_old_sha256）
- `src/spec_dock/runtime/application/direct_installation.py`（init: 既存パスがあれば拒否、親チェーンの symlink 拒否、通常ファイル publish）
- `src/spec_dock/runtime/application/direct_static_update.py`（update: インベントリに新しく増えたパスは `installation.create`、未知の改変は手動マージ要求、変更には `--backup-dir` と `--yes` が必要）
- `src/spec_dock/assets/install_root/.agents/skills/**`（スキル本体。grill スキルはリポジトリルート相対の `python3 .agents/skills/spec-dock-grill-with-docs/scripts/finalize-artifact.py` を呼び、preflight で「このスキルのディレクトリ内に `agents/openai.yaml` と `scripts/finalize-artifact.py` があること」を要求。frontmatter に Claude Code 用の `disable-model-invocation: true` が既にある）
- `spec-dock/adrs/20260831t005139z-adr-disposable-provider-roots-and-fixed-skill-slots.md`（スキルは共有 `.agents/skills` 配下の固定スロットとして管理するという accepted ADR。現実装は Issue 413 系のファイル単位インベントリ）
- `spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00074-multi-host-agent-and-config-asset-expansion/requirement.md`（過去に「shared skills は `.agents/skills/` に集約し host 固有ディレクトリへ重複配置しない」「Claude Code など追加 host の即時実装はスコープ外」と決めた。ただしこの判断は「各ホストが `.agents/skills` を読む」前提に依存していたと思われる）
- `AGENTS.md`（provider 側 `src/spec_dock/` が正、`spec-dock/` は dogfooding consumer、静的アセット変更は shipped asset API change として扱う）

## 検討中の選択肢（他にあれば追加してよい）

- A1: プロジェクト二重投影（コピー）。同じ provider source から `.agents/skills/<name>/` と `.claude/skills/<name>/` の両方へ通常ファイルとして配置し、既存インベントリ（sha256 管理、init/update/uninstall/show）で管理する。
- A2: プロジェクト二重投影（symlink）。`.claude/skills/<name>` を `../../.agents/skills/<name>` への相対 symlink にする。Claude Code はプロジェクトのスキルエントリの symlink を公式にサポート。
- B: グローバル導入。`spec-dock` の外部パッケージ側に `spec-dock skills install --user` のようなコマンドを設け、`~/.agents/skills` と `~/.claude/skills` に配置する（CLI がグローバルなので、その操作手順であるスキルもグローバルにする考え方）。wheel には post-install hook がないため明示コマンドが必要。
- C: Claude Code プラグイン（+ 必要なら Codex プラグイン）として marketplace 配布し、プロジェクトの `.claude/settings.json` で有効化する。
- D: 製品は変えず、利用者側で `--add-dir`、手動 symlink、`CLAUDE.md` からの参照などで回避する。

## 制約・前提

- SpecDock のスキルは、グローバル CLI の使い方に加え、worktree ごとの静的スキャフォールド（`spec-dock/docs`・`templates`・`system`）のレイアウトにも依存している。
- インストーラは「明示した 1 worktree だけを変更」「既知の静的リソースだけを扱う」「fail-closed」を契約にしている。`$HOME` への書き込みは現在の静的インストール契約の外にある。
- 業務コマンドは Linux/macOS のみサポート（Windows は UNSUPPORTED_PLATFORM）。ただし、リポジトリ自体を Windows で clone して Claude Code を使う可能性はある。
- 協業者、クラウドエージェント（Claude Code on the web、Codex cloud、CI 上のエージェント）はリポジトリの内容しか見えない。
- 人間による PR マージゲートは維持する。

## 求める出力

1. 推奨案（1 つ）とその根拠。選択肢ごとの評価（発見性、バージョン整合、協業者/クラウドでの再現性、既存インストール契約との整合、uninstall/update の安全性、Windows clone・symlink の扱い、文脈コスト、将来のホスト追加）を比較表で。
2. 推奨案を採る場合の具体的な変更点: インベントリ・allowlist・`installation show` の分類、既存利用者への update 経路、`.claude/` に利用者固有ファイルがある場合の衝突方針、uninstall 時に `.claude/` や `.claude/skills/` の空ディレクトリを残すか、2 つの投影のバイト一致を保証するテスト。
3. SKILL.md の内容で、ホスト中立にするために直すべき箇所（grill スキルのスクリプトパス、preflight 8、`agents/openai.yaml`、`.agents/skills` への言及など）。2 つの投影の内容を同一に保つべきか、ホスト別に変えるべきか。
4. epic-00074 の「host 固有ディレクトリへ重複配置しない」判断を改める扱い（新しい ADR が必要か、何を supersede するか）。
5. 推奨を覆す条件（たとえば Claude Code が `.agents/skills` を読むようになった場合の撤退手順）と、主要なリスク。

推測と、コード・公式ドキュメントで確認した事実は区別して書いてください。
````

## 添付ファイル facts.md

````markdown
# 補足証拠: エージェントホストのスキル探索仕様と観測（2026-10-14 確認）

この添付はリポジトリ外の一次情報と、ローカル環境の観測をまとめたもの。リポジトリ内容は Strict 検証済みコミットを正とする。

## 1. Claude Code（v2.1.299 で利用中）のスキル探索 — 公式 https://code.claude.com/docs/en/skills

- 探索場所（表の原文）:
  - Enterprise: managed settings ディレクトリ内の `.claude/skills/<skill-name>/SKILL.md`
  - Personal: `~/.claude/skills/<skill-name>/SKILL.md`
  - Project: `.claude/skills/<skill-name>/SKILL.md`（起動ディレクトリから repository root までの各親を探索。linked worktree では worktree root で停止）
  - Nested: `<subdir>/.claude/skills/<skill-name>/SKILL.md`（そのサブディレクトリのファイルを読んだ/編集した時点で遅延ロード）
  - Additional directory: `--add-dir` で渡したディレクトリ内の `.claude/skills/`
  - Plugin: `<plugin>/skills/<skill-name>/SKILL.md`（`/plugin-name:skill-name` で名前空間化）
- `.agents/skills` やその他 `.agents` ディレクトリへの言及なし。追加スキルディレクトリを設定する手段は `--add-dir` のみ。`permissions.additionalDirectories` はファイルアクセス権のみでスキルは読まない。
- 衝突時の優先: Enterprise > Personal > Project。プラグインスキルは名前空間が異なるため両方ロード。
- シンボリックリンク: 「enterprise / personal / project の `<skill-name>` エントリは別の場所のディレクトリへの symlink でよい。複数の場所が同じ target を指しても一度だけロード」。
- SKILL.md 置換変数: `${CLAUDE_SKILL_DIR}`（SKILL.md のあるディレクトリ）, `${CLAUDE_PROJECT_DIR}`, `$ARGUMENTS`, `${CLAUDE_PLUGIN_ROOT}`（プラグインのみ）など。
- frontmatter: `disable-model-invocation`, `user-invocable`, `allowed-tools`, `paths`（glob に一致するファイルを扱うときだけ自動ロード。Claude Code 拡張で Agent Skills 標準外）など。未知フィールドは無視。
- スキル一覧の description は全スキル分が毎ターン文脈に載る（1 スキルあたり description+when_to_use は 1,536 文字で切り詰め）。
- `~/.claude/skills`・project `.claude/skills`・`--add-dir` 内 `.claude/skills` はライブ変更検知あり。

## 2. Claude Code プラグイン — 公式 https://code.claude.com/docs/en/plugins

- `.claude-plugin/plugin.json` を持つディレクトリ。marketplace（`.claude-plugin/marketplace.json` を持つリポジトリ等）から install。
- install scope: user / project（コミットされた `.claude/settings.json` で有効化、各協業者は自分のマシンで install が必要）/ local。
- 実体は `~/.claude/plugins/` にキャッシュ。クラウドセッション（claude.ai/code）はローカル設定のプラグインを読まない。
- スキル名は `/plugin-name:skill-name` に名前空間化される。

## 3. Codex のスキル探索 — 公式 https://learn.chatgpt.com/docs/build-skills（旧 developers.openai.com/codex/skills）

- Repo: cwd から repository root までの各ディレクトリの `.agents/skills`
- User: `$HOME/.agents/skills`、Admin: `/etc/codex/skills`、System: 同梱、Plugins
- `.claude/skills` への言及なし。symlink は追従。同名スキルはマージせず両方表示。
- `agents/openai.yaml` の `policy.allow_implicit_invocation: false` で暗黙起動を抑止（明示 `$skill` は可）。
- 配布形式としては plugin を推奨（リポジトリを越える共有時）。単一リポジトリ用途は直接スキルフォルダ。

## 4. 業界の先例: vercel-labs/skills（`npx skills`） — https://github.com/vercel-labs/skills

| Agent | Project path | Global path |
|---|---|---|
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| Codex | `.agents/skills/` | `~/.agents/skills/` |
| Cursor | `.agents/skills/` | `~/.cursor/skills/` |
| Gemini CLI | `.agents/skills/` | `~/.gemini/skills/` |
| GitHub Copilot | `.agents/skills/` | `~/.copilot/skills/` |
| OpenCode | `.agents/skills/` | `~/.config/opencode/skills/` |
| Amp | `.agents/skills/` | `~/.config/agents/skills/` |

- インストール方式: Symlink（推奨、canonical copy から各エージェントへ）/ Copy（symlink 非対応時）。
- 要点: プロジェクトレベルは `.agents/skills`（多数のホスト共通）+ `.claude/skills`（Claude Code のみ）の 2 系統で足りる。グローバルレベルはホストごとにパスが分散している。

## 5. ローカル環境の観測（このマシン）

- `~/.claude/skills/` には `~/.agents/skills/*` への symlink が並ぶ。作成元は手動実行の `~/.claude/scripts/sync-skills.sh`（hook や launchd からの自動起動は見つからない）。
- そのため 2026-10-11 の同期以降に `~/.agents/skills` へ追加された 3 スキルは `~/.claude/skills` に存在しない（＝グローバル同期も「自動」ではなく、追加のたびに再実行が必要）。
- spec-dock リポジトリ自身（dogfooding consumer）では `.agents/skills/spec-dock` と `.agents/skills/spec-dock-grill-with-docs` が Git 追跡されているが `.claude/` は存在せず、Claude Code セッションのスキル一覧にこの 2 スキルは現れない（実観測）。
- spec-dock CLI は外部パッケージとしてユーザー環境にグローバルインストールされ、各リポジトリの `spec-dock/scripts/spec-dock` は PATH 経由で委譲する薄い shim。
````

## 回答（原文）

## 1. 推奨案：A1「単一 provider source から、両ホストのプロジェクトパスへ通常ファイルとして投影」

**A1 を推奨します。** スキルの正本は現在の provider source に一つだけ置き、同じ内容を `.agents/skills/<name>/` と `.claude/skills/<name>/` に配置します。これは「ホスト別にスキルを二重管理する方式」ではなく、**単一のスキルを、ホストの探索仕様に合わせて複数の固定パスへ配布する方式**です。

今回の評価では、ディスク上の重複削減よりも、リポジトリからの再現性、既存の fail-closed な更新・削除処理の再利用、管理対象の限定を優先します。

### 検証対象と確認範囲

GitHub コネクタで `GET /repos/chemitaro/spec-dock/branches/main` を取得し、`chemitaro/spec-dock` の `main` の先端が、期待値と同じ **`0e7dc86841cb48d011270a1a2165cb6406ac0cea`** であることを確認しました。その後、ルートの `AGENTS.md` を読み、リポジトリ内の参照をこのコミットに固定しています。 

ただし、指定された次の ADR は、このコミットを指定した `GitHub.fetch_file` で `404 Not Found` でした。

`spec-dock/adrs/20260831t005139z-adr-disposable-provider-roots-and-fixed-skill-slots.md`

したがって、この ADR の本文・accepted 状態・正確な決定条項は未確認です。後述の supersede 範囲は、確認できた `epic-00074` の記述と、ご提示の ADR の説明を分けて扱います。

### 推奨を支える主要な根拠

**第一に、スキル形式の共通化と、探索ディレクトリの共通化は別の契約です。** 現在の公式文書では、Codex のリポジトリ内探索先は `.agents/skills`、Claude Code のプロジェクト探索先は `.claude/skills` です。共通形式に準拠するだけでは、同じ配置先から発見されるとは限りません。[ChatGPT Learn](https://learn.chatgpt.com/docs/build-skills)

**第二に、現行インストーラは A1 に必要な構造を既に持っています。** `package_static_assets()` は配置先の `path` とパッケージ内の `source` を分離し、配置先の重複は拒否しますが、複数エントリが同じ `source` を参照することは禁止していません。通常ファイルの公開、ハッシュによる既知版判定、バックアップ、部分失敗の報告も既存処理を利用できます。  

**第三に、スキルを worktree の静的スキャフォールドと同じ変更単位でレビューできます。** 現在のスキル自身が、外部パッケージの更新と worktree 内の静的更新を区別しています。CLI がグローバルであることは、その使い方を記述したスキルまでグローバルにする十分な理由にはなりません。特に今回は、スキルがその worktree のドキュメント、テンプレート、Artifact レイアウトに依存しています。 

ただし、**A1 がそろえるのは静的配布物の版です。PATH 上の外部 CLI の版まで自動的にそろえるわけではありません。** 既存の root／leaf help 確認と、実際に利用する CLI・スキャフォールドの互換性確認は維持する必要があります。

### 選択肢の比較

以下は、確認したコード・ホスト仕様を前提とした設計評価です。

| 評価軸 | **A1：プロジェクトコピー** | A2：プロジェクト symlink | B：グローバル導入 | C：プラグイン | D：利用者側の回避 |
|---|---|---|---|---|---|
| 発見性 | 両ホストの標準探索先に配置できます | Claude Code が対応する skill entry の symlink を利用できます | 各環境で明示導入した利用者には見えます | 導入・有効化したホストで見えます。呼び出し名も変わります | 手順の実行・維持に依存します |
| バージョン整合 | 両投影と静的スキャフォールドを同一更新・PRで扱えます | リンク先が同じため内容の分岐は起こりにくいです | 複数リポジトリ・ブランチが一つの版を共有し、静的資産とのずれが生じやすくなります | プラグイン、CLI、スキャフォールドの版を別途対応付ける必要があります | 手動同期によるずれが残ります |
| 協業者・クラウドでの再現性 | 管理ファイルをコミットすれば配布状態を再現できます | Git checkout と実行環境でリンクが再現されることが条件です | ローカル HOME への導入だけでは満たせません | project 設定のコミットだけでは導入を完結できません | 共有されないローカル設定が前提になりがちです |
| 既存インストール契約との整合 | 固定パスの追加として扱えます | リンクを管理する資産型と安全なライフサイクルの追加が必要です | HOME を変更する別契約が必要です | ホスト側の配布・設定管理を別途導入します | 製品契約は変わりませんが、製品としての問題も残ります |
| update／uninstall の安全性 | 現行の通常ファイル・ハッシュ判定を再利用できます | リンク自体とリンク先の所有権、バックアップ、削除を分ける必要があります | 更新の影響が複数リポジトリへ及びます | プラグイン更新と静的更新の整合は別問題です | 孤立したコピーやリンクが残りやすくなります |
| Windows clone | スキルファイルの配置に symlink 機能を要求しません | `core.symlinks=false` ではリンクが通常ファイルとなり、探索が壊れます | コピー方式なら配置できますが、環境ごとの導入が必要です | ホストの対応範囲に依存します | 選択した回避方法に依存します |
| 文脈コスト | 二重配置だけで各ホストの文脈が二倍になるわけではありません | A1 とほぼ同じです | 対象外のリポジトリでも候補になる範囲が広がります | 有効化スコープと同梱内容に依存します | `CLAUDE.md` への手順展開は常時文脈を増やし得ます |
| 将来のホスト追加 | 既存探索先を共有できなければ、同じ source の投影先を追加できます | リンク対応ホストには展開できますが、非対応環境への分岐が必要です | ホスト別の user path と全体更新を管理します | ホストごとの配布・検証契約が増えます | 利用者向け手順が増えます |

A2 は、Claude Code が symlink を読めないから不採用なのではありません。対応自体は添付の公式仕様整理にも記載されています。問題は、SpecDock 側が現在、親チェーンの symlink と単一リンクでない通常ファイルを拒否する設計であり、A2 の安全な導入にはインストーラの責務拡張が必要なことです。facts 

Windows については、Git が `core.symlinks=false` の場合にリンク内容を小さな通常ファイルとして checkout することが公式仕様です。A1 はこの配置上の障害を避けますが、SpecDock の業務コマンドを Windows 対応にするものではありません。[Git](https://git-scm.com/docs/git-config) 

C は一般的な再利用スキルの配布には有力です。しかし現在の Claude Code では、project scope の設定をコミットしても各協業者のインストールが必要で、クラウドセッションはリポジトリの `.claude/settings.json` で有効化されたプラグインを読み込みません。今回の「リポジトリの内容で再現する」という条件では主方式に適しません。[Claude Code](https://code.claude.com/docs/en/discover-plugins)

## 2. A1 を採る場合の具体的な変更点

### 2.1 インベントリ：provider source は増やさず、配置エントリだけを増やします

現在、スキル関連のインベントリは、通常スキルの `SKILL.md` と、grill スキルの `SKILL.md`・`agents/openai.yaml`・`scripts/finalize-artifact.py` の計4ファイルです。これに対応する次の4エントリを追加します。

```text
.claude/skills/spec-dock/SKILL.md
.claude/skills/spec-dock-grill-with-docs/SKILL.md
.claude/skills/spec-dock-grill-with-docs/agents/openai.yaml
.claude/skills/spec-dock-grill-with-docs/scripts/finalize-artifact.py
```

`src/spec_dock/assets/static-inventory.json` では、次の契約にします。

| 項目 | 推奨する扱い |
|---|---|
| `path` | `.agents/skills/...` と `.claude/skills/...` の二系統です |
| `source` | 両方とも既存の `install_root/.agents/skills/...` を参照します |
| `sha256` | 対応する両投影で同じ値です |
| `mode` | 対応する両投影で同じ値です。現行4ファイルは `420`、つまり `0644` です |
| `init_only` | 両投影とも `false` です |
| `known_old_sha256` | **配置先ごとの配布履歴**として管理します。両投影で同一にする必要はありません |

特に、**新設する `.claude` 側へ `.agents` 側の `known_old_sha256` をそのままコピーしない**方針を推奨します。そのパスに過去に正式配布していない内容まで、更新・削除可能な既知資産として扱う必要はありません。

今回 `SKILL.md` を変更する場合、`.agents` 側には現在配布しているハッシュを既知旧版として追加します。一方、初回配布の `.claude` 側の履歴は空から始めます。

provider 側に `.claude` 用の実体コピーを作る必要はありません。現在の `pyproject.toml` は `assets/install_root/.agents/**` を明示的にパッケージへ含めているため、その source を維持する設計では、`.claude` 用の package-data glob も不要です。ただし、実際の wheel に必要な source と更新済みインベントリが含まれることは配布テストで確認します。

### 2.2 allowlist：`.claude` 全体ではなく、二つの固定スロットだけを追加します

`src/spec_dock/asset_layout.py` には、二つのスキル名と `.agents/skills/<name>` の固定パスがあります。ここにホスト別の投影ルートを明示し、同じ固定スキル名から配置先を導出する構造を推奨します。

`src/spec_dock/runtime/infra/static_assets.py` の現在資産の allowlist には、次の二つだけを追加します。

```text
.claude/skills/spec-dock/
.claude/skills/spec-dock-grill-with-docs/
```

`.claude/**` や `.claude/skills/**` 全体を許可してはいけません。`.claude/settings.json`、`settings.local.json`、他のスキル、agents、hooks は今回の管理対象外です。

また、現行の `package_retired_assets()` は、旧バージョンファイルと旧 runtime の Python ファイルしか認めていません。**将来 `.claude` 投影を廃止するときは、この retired allowlist の拡張が必要です。** 初回導入だけなら今すぐ変更する必要はありませんが、撤退計画に必須の変更として記録すべきです。

### 2.3 `installation show`：既存の状態分類を維持します

現在の `installation show` はインベントリを列挙し、各ファイルを `missing`・`current`・`known-old`・`unknown`・`unsafe` に分類します。新しい `.claude` エントリも、この分類へそのまま参加させるのが最小変更です。`classification=claude` のように、状態とホスト種別を混ぜるべきではありません。

| 観測状態 | 推奨する表示 |
|---|---|
| 安全な親チェーンで対象ファイルがない | `missing` |
| 配布中のバイト列と一致する | `current` |
| そのパスの既知旧版と一致する | `known-old` |
| 安全な通常ファイルだがハッシュが未知である | `unknown` |
| 親または対象が symlink、対象がディレクトリ・特殊ファイル・複数 hard link などである | `unsafe` |

ここには一つ、追加で直す価値のある観測上の問題があります。現行 `show` は、対象ファイルが存在しない場合には親チェーンを検査せず `missing` とします。一方、更新側は先に `verify_existing_parent()` を実行します。そのため、**危険な親の下にある欠落ファイルを、`show` だけが単純な `missing` と扱う可能性があります。** `.claude` 対応では、親の安全性を確認してから欠落判定するようにそろえることを推奨します。 

なお、`current` は「現在実行しているパッケージの配布バイト列と一致する」という意味であり、Claude Code が実際にそのファイルを選択したことや、外部 CLI との完全な互換性を証明するものではありません。現行判定は mode の一致判定でもありません。

### 2.4 既存利用者の更新経路と衝突方針

既存利用者は、**外部パッケージを更新した後、対象 worktree で通常の `installation update` を行う**経路に統一します。ホスト検出による自動分岐や、Claude Code が入っているマシンだけへの配布は推奨しません。生成結果が開発者のローカル環境によって変わり、クラウドや協業者向けの配布を取りこぼすためです。

現行更新処理は、欠落したインベントリパスを `installation.create` として計画し、変更がある場合は `--backup-dir` と `--yes` を要求します。したがって、`.claude` 側の追加だけであっても既存の更新契約を維持できます。

衝突時の推奨挙動は次のとおりです。

| 既存状態 | `init`／`update` の扱い |
|---|---|
| `.claude/` や `.claude/skills/` が通常ディレクトリとして存在する | 共有の親として利用します。中身全体を所有しません |
| `settings.json`、他のスキル、未知の補助ファイルがある | インベントリ外のファイルは変更・削除しません |
| 管理対象のファイルが既に存在する | `init` は、内容が同じでも現行どおり拒否します |
| 管理対象ファイルが現在の配布バイト列と一致する | `update` は現行どおり受け入れ、変更しません |
| 管理対象ファイルが、そのパスの既知旧版である | バックアップ後に更新します |
| 管理対象ファイルが未知の内容である | 更新全体を事前検査で停止し、手動マージを要求します |
| `.claude`、`skills`、スキルスロット、対象ファイルが symlink 等である | 拒否します。正しい相対リンクでも自動変換しません |

この方針には、明示すべき所有権上の限界があります。**同じパスに同じバイト列があれば、それが利用者による手動コピーか、SpecDock が作成したものかを現行方式では区別できません。** `update` で受け入れた同一内容のファイルは、後の `uninstall` で削除対象になります。これは追加の所有権台帳を導入しない場合の、パス＋ハッシュ方式の性質です。リリースノートには、新しい管理対象パスとこの扱いを明記すべきです。

更新手順は、事前の dry-run、利用者による衝突解消、明示的な適用、`show` とバイト比較による確認、管理対象ファイルだけの PR 化とします。`.claude/` 全体を一括でコミット対象にして、利用者固有設定まで取り込む運用は避けます。

### 2.5 uninstall：共有の親ディレクトリは残します

**`.claude/` と `.claude/skills/` は、空でも残すことを推奨します。** 今回はスキルスロット内の空ディレクトリも含め、再帰的なディレクトリ清掃を追加しない方針が妥当です。

現行 uninstall は、検証済みの対象ファイルを `retire_file()` で一つずつ unlink する方式であり、ディレクトリの再帰削除は行いません。この契約を維持すれば、未知のファイルや利用者の共有領域を巻き込みません。 

ただし、**空ディレクトリを残すことも、Claude Code に対して完全に無影響ではありません。**

公式文書では、Claude Code v2.1.277 以降の linked worktree は、ルートに `.claude/skills` がない場合に main checkout のスキルを読み込みます。自身のディレクトリがある場合は、そのコピーだけを読み込みます。このため、空ディレクトリの維持は main checkout へのフォールバックを抑える結果になります。逆に削除すると、別の場所に残る同名スキルが再び見える可能性があります。[Claude Code](https://code.claude.com/docs/en/worktrees)

したがって、uninstall の保証は「対象 worktree にある、自ら管理するファイルを除去する」までとし、**ホスト全体で同名スキルを無効化する保証とは分ける**べきです。空ディレクトリの有無を、永続的な無効化機構として利用する設計にもすべきではありません。

### 2.6 バイト一致と安全性のテスト

現在の `test_provider_matches_fresh_consumer_managed_assets` は、provider と fresh consumer の `.agents/skills` を比較しています。これを両投影へ拡張します。ただし、既存の `_files()` は内容比較が中心で、ファイル型や hard link の独立性までは保証していません。

保証する不変条件は、各管理対象の相対パスについて次です。

```text
provider payload
  == .agents 側のファイルのバイト列
  == .claude 側のファイルのバイト列
```

インベントリ全体のエントリ一致を要求してはいけません。`path` と `known_old_sha256` は投影間で異なり得ます。

| テスト群 | 具体的な受け入れ条件 |
|---|---|
| インベントリ・配布物 | 両投影の対応する `source`・`sha256`・`mode`・`init_only` が一致します。パスは一意・整列済みです。fresh wheel の非 editable 環境でも必要な source を取得できます |
| fresh init | 4ファイルずつ、計8ファイルが存在し、上記のバイト一致を満たします。親・ファイルに symlink がなく、各ファイルは単一リンクの通常ファイルです |
| 既存利用者の update | 旧 `.agents` 配置から更新し、既知旧版を更新、`.claude` を作成します。dry-run は無変更、必要引数不足は無変更、成功後の再更新は unchanged です |
| 衝突・境界 | 利用者設定と他スキルを保持します。管理対象の未知改変、親の symlink、dangling symlink、特殊ファイル、hard link は拒否します。別 worktree や HOME のスキル領域は変更しません |
| uninstall | 既知の管理対象だけを削除し、未知ファイルと共有ディレクトリを保持します。未知改変を検出した場合は事前検査で停止します |
| 部分失敗 | 片方の投影更新後に失敗させ、成功・未実行・不確実な効果を正しく報告します。観測後の新しい明示操作で収束でき、自動再試行・自動 rollback をしません |
| ホスト実機 | 新規セッションで各ホストが期待する配置先を選択します。grill の明示起動制御、サブディレクトリからの helper 実行、空白を含むパス、外部依存欠落時の zero-write を確認します |

**「両投影が常時一致する」とは約束できません。** 現行更新はファイルごとの順次公開であり、複数ファイルを一括で切り替えるトランザクションではありません。保証は、パッケージ生成時と、更新成功時の検証点に置きます。途中失敗は既存の partial／バックアップ／明示的回復の契約で扱います。

また、新規ファイルの mode と既存ファイルの mode 保存は別にテストします。現行 update は既存 mode を保存するため、バイト一致と権限一致を同じ保証にまとめるべきではありません。

## 3. `SKILL.md` のホスト中立化

### 方針：両投影の内容は同一に保ちます

**今回の段階では、ホスト別に `SKILL.md` を分岐させる必要はありません。** 共通本文に加え、Claude Code と Codex それぞれの起動制御メタデータを同梱する方式を推奨します。

Agent Skills の仕様は、スキルルートからの相対参照と任意の補助ファイルを認めています。`agents/openai.yaml` が存在すること自体は、共通のスキルパッケージを維持する妨げにはなりません。[Agent Skills](https://agentskills.io/specification)

### 具体的に直す箇所

| 対象 | 推奨する修正 |
|---|---|
| 通常スキルの静的資産の説明 | `.agents/skills` だけを列挙せず、`.agents/skills` と `.claude/skills` を「同じ provider source のホスト向け投影」と説明します |
| grill の helper 実行例 | `.agents/skills/spec-dock-grill-with-docs/...` の固定パスをやめ、**今回読み込まれたスキルディレクトリ**から helper の絶対パスを解決します |
| preflight 8 | 共通の実行前提を、helper の存在・通常ファイル性・スキルディレクトリ内への包含にします。`agents/openai.yaml` の存在は全ホスト共通の実行前提から外します |
| `agents/openai.yaml` | Codex の起動制御メタデータとして両投影へ同梱します。存在・内容・ポリシー値は配布テストで保証します |
| `disable-model-invocation: true` | grill で維持します。通常の `spec-dock` スキルへ一律追加せず、現在の起動方針を保ちます |
| ホスト名・設定への言及 | `running Codex processes` のような一般化できる表現は `agent processes` 相当へ変更します。保護対象の設定は `.codex/config.toml` だけに見えないよう、ホスト設定全般を保護する記述にします |

現在の通常スキルは静的投影として `.agents/skills` のみを説明し、grill の実行例は `.agents/skills/.../finalize-artifact.py` に固定されています。また preflight 8 は YAML と helper の両方を必須にしています。以上は実際の配布 source で確認した修正対象です。 

### `skill_root` と `repo_root` を明確に分けます

必要なのは、新しい共通環境変数を仮定することではなく、次の二つを区別することです。

- `skill_root` は、今回ホストが読み込んだ `SKILL.md` の所在ディレクトリです。
- `repo_root` は、今回操作する明示的な worktree ルートです。

helper は `skill_root/scripts/finalize-artifact.py` から実行し、対象 worktree は従来どおり `--repo-root` で渡します。**スキル内の相対パスを、シェルの現在ディレクトリに対する相対パスとして実行しない**ことが重要です。

Claude Code の `${CLAUDE_SKILL_DIR}` はこの解決に利用できますが、ホストによる文字列置換であり、他ホストにも存在する共通のシェル環境変数として扱ってはいけません。共通本文では、読み込まれたスキルの絶対パスを基準に解決し、確定できなければ書き込み前に停止する方針にします。facts [Claude Code](https://code.claude.com/docs/en/skills)

片方に helper が見つからない場合に、もう片方や HOME を順番に探して代用する方式は推奨しません。異なる版の本文と helper を組み合わせる可能性があり、配布不備を隠すためです。

helper の Python 実装自体は、対象の `repo_root` と Artifact パスを引数として受け取り、親チェーン・ファイル identity・hard link 数等を検証しています。**今回のパス中立化のために、この Artifact 安全性を緩める必要はありません。**

### 起動制御と文脈コスト

grill の `agents/openai.yaml` は現在、`policy.allow_implicit_invocation: false` を持っています。Codex 公式文書でも、これは暗黙起動を抑え、明示的な `$skill` 起動を残す設定です。Claude Code 側の `disable-model-invocation: true` とともに維持します。 [ChatGPT Learn](https://learn.chatgpt.com/docs/build-skills)

添付 `facts.md` の「全スキルの description が毎ターン文脈に載る」という記述には補足が必要です。Claude Code の公式表では、`disable-model-invocation: true` のスキルは description を通常の文脈に載せません。したがって、grill まで通常スキルと同じ常時コストで数えるのは適切ではありません。facts [Claude Code](https://code.claude.com/docs/en/skills)

### 「発見できる」と「実行できる」を分けます

grill は、現在のホストのスキルカタログに **`grilling` と `domain-modeling` の両方があること**を要求しています。二つの SpecDock スキルを配布するだけでは、この依存条件は満たされません。

今回の配布方式の受け入れ条件は、まず両ホストから SpecDock スキルを発見できることです。grill の実行可能性は、外部 CLI、Python、必要な静的スキャフォールド、二つの外部スキルが利用可能であることを含む別の条件として検証します。依存スキルの自動インストールや vendoring を今回の変更へ混ぜるべきではありません。

## 4. `epic-00074` の判断を改める扱い

**新しい ADR を作成することを推奨します。** 配布先、更新・削除対象、利用者領域との境界が変わるため、単なるドキュメント修正ではなく shipped asset API change として扱うべき変更です。これはルート `AGENTS.md` の方針とも一致します。

ただし、過去の判断の理由については、次のように訂正して整理する必要があります。

> `epic-00074` が「各ホストが `.agents/skills` を読む」と誤認していたことまでは、確認した文書からは断定できません。

確認できた文書は、`E-RQ-003` で host 固有ディレクトリへの重複配置を禁止する一方、Claude Code などの追加ホストを明示的にスコープ外としています。frontmatter の状態も `draft` です。したがって、今回の変更は「誤った前提の訂正」と決めつけるより、**以前は対象外だった Claude Code を対象へ加えるため、配置制約を改訂する判断**として記録するのが正確です。

### 新しい ADR で決める範囲

新 ADR の中心となる決定は、次のようにまとめられます。

> スキルの著作・保守上の正本は一つとします。配布先はホストの探索契約に従い、必要な固定スロットへ同一内容を投影します。SpecDock が管理するのは明示インベントリのファイルであり、ホストの共有設定ディレクトリ全体ではありません。

改訂するのは、`epic-00074` の `E-RQ-003`、happy path、関連するスコープ記述のうち、**「host 固有ディレクトリへ重複配置しない」という配置制約**です。一方、単一 source、拡張可能性、未知の利用者ファイルの保持、runtime protocol をホスト側へ再実装しない境界は維持します。

過去の OUT OF SCOPE を、当時から Claude Code 対応が必須だったかのように書き換えるべきではありません。旧文書には後続決定への参照を付け、現在の配布契約は新しい要件・設計・ADR で明示する方針が妥当です。

指定された固定スロット ADR については、本文を確認できていないため正式な supersede 指定は確定できません。ご提示の説明どおりであれば、部分的に置き換える候補は「`.agents/skills` だけを唯一の配布先とする制約」であり、**固定スロット管理や共有親ディレクトリを所有しない安全境界まで廃止する必要はありません。**

また、過去の disposable root／sync-prune の考え方を理由に、現在のファイル単位インベントリへディレクトリ一括削除を再導入してはいけません。

## 5. 推奨を覆す条件、撤退手順、主要リスク

### Claude Code が `.agents/skills` を正式に読むようになった場合

その時点で `.claude` 投影を廃止する方向へ見直します。ただし、新しい一バージョンで読めることだけでは撤退条件として不十分です。

サポートする最小バージョンと利用面で、`.agents` からの探索、grill の起動制御、helper の位置解決が確認できることが必要です。移行期間中に両配置が存在する場合の重複ロードや優先順位も検証します。

撤退は、次の順序にします。

1. 対応バージョンと廃止条件を文書化し、利用者へ移行期間を設けます。
2. `.claude` の各管理ファイルを current inventory から retired inventory へ移し、そのパスに実際に配布したハッシュを登録します。
3. `package_retired_assets()` の allowlist を、必要な固定スロットに限定して拡張します。
4. 通常の `installation update` で、バックアップと `--yes` の下で既知ファイルだけを除去します。未知改変、利用者設定、共有ディレクトリは保持します。

**インベントリからエントリを消すだけでは撤退になりません。** 既存環境のファイルが管理対象から外れたまま残ります。また、古い CLI は新しい `.claude` 管理パスを知らないため、削除はその配布を認識する版で実行する必要があります。 

### それ以外の見直し条件

スキルが worktree の静的スキャフォールドから独立し、複数リポジトリで一つの版を共有しても問題がなくなった場合は、B または C を再評価できます。組織運用がプラグイン経由の導入を必須とし、クラウドを含む配布・バージョン固定を解決した場合も、C を主方式にする理由が成立します。

A2 は、対象環境が symlink を確実に再現でき、SpecDock 側にもリンクの安全な inventory・backup・update・uninstall 契約が整備され、コピーの負担が実際の問題になった場合に再評価できます。現状の4ファイルのために、先にその複雑性を追加する優先度は低いと判断します。

### 主要なリスク

**ホスト側の優先順位による別版の選択です。** Claude Code では personal の同名スキルが project より優先され、Codex では同名スキルが複数表示され得ます。したがって、ローカルの管理ファイルがすべて `current` でも、実際のセッションがそのコピーを選ぶとは限りません。受け入れ検証では、名前だけでなく読み込み元を確認する必要があります。facts facts

**worktree とホストの設定参照先が一致しない場合です。** 前述のフォールバックに加え、公式文書では Desktop app から開始する worktree セッションが main checkout 側のスキル等を読む挙動も説明されています。A1 だけで、すべての起動経路における worktree 別の版選択を保証することはできません。対象 worktree と異なる投影が選ばれた場合は、互換性を確認するか、実行を停止する条件を設けるべきです。`repo_root` をホストの設定ルートから無条件に推定してはいけません。[Claude Code](https://code.claude.com/docs/en/worktrees)

**部分更新と、既に読み込まれた指示の残存です。** ファイル更新の成功と、進行中のエージェントが新しい本文を利用することは別です。配布の受け入れ試験は新規セッションで行い、更新途中の状態で業務を継続しない運用にします。

**Git の改行変換によるハッシュ不一致です。** 通常ファイルを使っても、`core.autocrlf` 等による checkout 時の変換は残ります。インストーラが書いたバイト列、Git 内の内容、各 OS の working tree の内容は区別して検証します。LF 方針を採用する場合も、利用者のルート `.gitattributes` を静かに書き換える変更へ拡大してはいけません。[Git](https://git-scm.com/docs/git-config)

**配布ファイルの未コミットと依存環境の不足です。** A1 の協業者・クラウドでの利点は、管理対象の投影が Git に含まれることが前提です。CLI や外部依存スキルの準備まで完了したと扱わず、それぞれ別に確認します。

採用時の最小構成は、**四つの `.claude` インベントリエントリ、固定スロットの allowlist 拡張、共通 `SKILL.md` のパス中立化、衝突・部分失敗・両投影一致のテスト、新 ADR と配布ドキュメントの更新**です。HOME 操作、プラグイン導入、symlink 対応、ホスト設定の自動編集は含めません。

本回答では、リポジトリと公式文書の参照を行いました。コード変更、テスト実行、wheel の実ビルド、Codex／Claude Code の実機検証は行っていません。
