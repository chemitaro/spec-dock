---
種別: research
ID: "20261014t071357z-research"
タイトル: "Claude Code skill discovery investigation"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-10-14"
親: ["iss-00418"]
template: "research"
authority: "evidence"
derived_from: []
reflected_to: []
---

# 20261014t071357z-research Claude Code skill discovery investigation

一つの source-grounded investigation を記録します。複数の証拠を統合して選択肢を比較する場合は `disc` を使います。

## Question

- SpecDock を導入したリポジトリで、Claude Code が同梱スキル `spec-dock`・`spec-dock-grill-with-docs` を発見できないのはなぜか。
- Codex と Claude Code の両方からスキルを発見できるようにするには、どの配布方式が適切か。

## Source

- 参照先と確認日（すべて 2026-10-14）:
  - Claude Code 公式: https://code.claude.com/docs/en/skills （探索場所、symlink、置換変数、frontmatter、ライブ変更検知）
  - Claude Code 公式: https://code.claude.com/docs/en/worktrees （linked worktree と Desktop app のスキル読み込み）
  - Claude Code 公式: https://code.claude.com/docs/en/plugins （プラグインの構成・install scope・クラウドセッション）
  - Codex 公式: https://learn.chatgpt.com/docs/build-skills （旧 developers.openai.com/codex/skills からの 308 リダイレクト先）
  - 業界の先例: https://github.com/vercel-labs/skills （`npx skills` のホスト別配置表）
  - リポジトリ（`main` @ `0e7dc86841cb48d011270a1a2165cb6406ac0cea`）:
    - `src/spec_dock/asset_layout.py`
    - `src/spec_dock/runtime/infra/static_assets.py`
    - `src/spec_dock/assets/static-inventory.json`
    - `src/spec_dock/runtime/application/direct_installation.py`
    - `src/spec_dock/runtime/application/direct_static_update.py`
    - `src/spec_dock/assets/install_root/.agents/skills/**`
    - `pyproject.toml`（package-data）
    - `epic-00074-multi-host-agent-and-config-asset-expansion/requirement.md`
    - ADR `20260831t005139z-adr-disposable-provider-roots-and-fixed-skill-slots.md`（epic-00384 配下が正本。`spec-dock/adrs/` は Git 管理外のミラー symlink）
  - ローカル環境: Claude Code 2.1.299、spec-dock 0.2.4（`~/.local/bin/spec-dock`）、`~/.claude/skills`、`~/.agents/skills`、`~/.claude/scripts/sync-skills.sh`
  - 外部分析: 同じ Issue の Artifact `20261014t071419z--chatgpt-strict-claude-skill-distribution-analysis.md`（ChatGPT Strict、GPT-6 / Pro、上記 SHA を GitHub コネクタで照合済み）

## Findings

### 確認できた事実（公式文書）

- **Claude Code の探索場所**：Enterprise（managed settings 内の `.claude/skills`）、Personal（`~/.claude/skills`）、Project（`.claude/skills`。起動ディレクトリから repository root までの各親。linked worktree では worktree root で停止）、Nested（`<subdir>/.claude/skills`。そのサブディレクトリのファイルを読むか編集したときに遅延ロード）、`--add-dir` で渡したディレクトリ内の `.claude/skills`、Plugin（`/plugin-name:skill-name` に名前空間化）、claude.ai アカウントのスキル。
  - `.agents/skills` への言及はない。追加ディレクトリを指定する手段は `--add-dir` だけ。`permissions.additionalDirectories` はファイルアクセス権を与えるだけで、スキルは読まない。
- **Claude Code の優先順位**：Enterprise > Personal > Project。プラグインのスキルは名前空間が別なので両方ロードされる。
- **Claude Code の symlink**：Enterprise / Personal / Project の `<skill-name>` エントリは別ディレクトリへの symlink でよい。同じ target は一度だけロードされる。
- **Claude Code の置換変数**：`${CLAUDE_SKILL_DIR}`（SKILL.md のあるディレクトリ）、`${CLAUDE_PROJECT_DIR}` など。Claude Code だけの文字列置換であり、他ホスト共通のシェル環境変数ではない。
- **Claude Code の frontmatter**：`disable-model-invocation`、`user-invocable`、`allowed-tools`、`paths` などに対応し、未知のフィールドは無視する。`paths` は Agent Skills 標準外の Claude Code 拡張。
- **Claude Code の worktree**：v2.1.277 以降、ルートに `.claude/skills` がない worktree は main checkout の project skills を読み込む。自前の `.claude/skills` がある worktree は、そのコピーだけを読む。Desktop app から開始した worktree セッションは、settings・hooks・skills などを main checkout のルートから読む。
- **Codex の探索場所**：cwd から repository root までの各 `.agents/skills`、`$HOME/.agents/skills`、`/etc/codex/skills`、System、Plugins。
  - `.claude/skills` への言及はない。symlink は追従する。同名スキルはマージせず両方表示する。
  - `agents/openai.yaml` の `policy.allow_implicit_invocation: false` で暗黙の起動を抑止できる（明示 `$skill` は可）。
- **業界の先例**：vercel-labs/skills では、プロジェクト配置は `.agents/skills`（Codex・Cursor・Gemini CLI・GitHub Copilot・OpenCode・Amp ほか共通）と `.claude/skills`（Claude Code）の2系統で、グローバル配置はホストごとに分散している（`~/.cursor/skills`、`~/.gemini/skills`、`~/.copilot/skills` など）。インストール方式は symlink（推奨）と copy を選べる。

### 確認できた事実（リポジトリ）

- **インベントリ**：`static-inventory.json` の各エントリは、配置先 `path` とパッケージ内 `source` を分けて持つ。`package_static_assets()` は path の重複は拒否するが、同じ source を複数エントリが参照することは禁止していない。
- **配置先の allowlist**：`static_assets.py` は、スキルの配置先を `.agents/skills/spec-dock/` と `.agents/skills/spec-dock-grill-with-docs/` の前方一致だけに制限している。retired allowlist は `spec-dock/spec-dock.version` と `spec-dock/scripts/spec_dock_runtime/*.py` だけを認める。
- **init**：配置先がすでにあれば拒否し、親チェーンの symlink も拒否する。そのうえで通常ファイルとして公開する。
- **update**：インベントリにあって配置先にないパスを `installation.create` として作成する。未知の内容は「手動マージ要求」で停止する。変更があれば `--backup-dir ABS` と `--yes` を要求する。
- **uninstall**：既知のファイルを `retire_file()` で1件ずつ削除する。ディレクトリは削除しない。
- **`installation show`**：配置先のファイルが存在しない場合、親チェーンを検査せずに `missing` と分類する。update 側は `verify_existing_parent()` を先に実行するため、両者の扱いがずれている（既存の小さな不整合で、本 Issue の主題ではない）。
- **package-data**：`pyproject.toml` は `assets/install_root/.agents/**` を明示的に含め、`__pycache__` と `*.pyc` を除外している。
- **スキル本文**：
  - `spec-dock` SKILL.md は、静的投影として「root `.agents/skills`」だけを説明している。
  - `spec-dock-grill-with-docs` SKILL.md は helper を `python3 .agents/skills/spec-dock-grill-with-docs/scripts/finalize-artifact.py` という固定パスで呼ぶ。preflight 8 は、スキルディレクトリ内に `agents/openai.yaml` と `scripts/finalize-artifact.py` があることを要求する。frontmatter にはすでに Claude Code 用の `disable-model-invocation: true` がある。
- **過去の判断**：
  - epic-00074（状態 draft）は E-RQ-003 で「shared skills は `.agents/skills/` に集約し、host 固有ディレクトリへ重複配置しない」とし、「Claude Code など追加 host の即時実装」をスコープ外にしている。
  - accepted ADR `20260831t005139z` は、スキルを共有 `.agents/skills` 配下の固定スロット2つとして管理し、親ディレクトリ全体は所有しないと決めている。現在の実装は、Issue 413 系のファイル単位インベントリ。

### 確認できた事実（ローカル環境）

- この dogfooding repo では、`.agents/skills/spec-dock*` が Git で追跡されているが `.claude/` は存在しない。Claude Code セッションのスキル一覧に、この2スキルは現れない。
- `~/.claude/skills` には `~/.agents/skills/*` への symlink が並ぶ。作成元は手動実行の `~/.claude/scripts/sync-skills.sh` で、hook などから自動起動された形跡はない。前回の同期（2026-10-11）以降に追加された `find-skills`・`orca-cli`・`orchestration` は `~/.claude/skills` に存在しない。

### 推測・判断候補（未採用。採否は Requirement / Design / ADR で確定する）

- **推奨（調査者・外部分析の一致）**：A1。単一の provider source から、`.agents/skills/<name>/` と `.claude/skills/<name>/` の両方へ、同じバイト列の通常ファイルとして投影する。
  - 既存のインベントリ機構（sha256、init / update / uninstall / show）をそのまま使える。
  - リポジトリにコミットすれば、協業者、Claude Code on the web、CI のエージェントにも届く。
  - スキルは CLI だけでなく、worktree ごとの静的スキャフォールド（docs / templates / rules）にも依存している。そのため、配布単位を静的資産と揃えるのが整合的。
- **退ける候補とその理由**：
  - B（グローバル導入）：`$HOME` を書き換える別契約が必要になる。wheel には post-install hook がないため、明示的なコマンドと更新のたびの再実行が要る（上記の手動同期と同じ漏れ方をする）。全リポジトリで文脈を消費する。Claude Code ではユーザー全体のスキルがプロジェクトのスキルより優先されるため、プロジェクト版を隠す危険もある。
  - C（プラグイン）：CLI と別の版管理経路が増える。呼び出し名が名前空間化される。協業者ごとにインストールが必要。クラウドセッションはローカル設定のプラグインを読まない。
  - A2（symlink）：インストーラの「symlink 拒否」設計と衝突する。Windows で `core.symlinks=false` の clone をするとリンクが壊れる。
  - D（利用者側の回避）：製品としての問題が残る。
- **A1 の具体像（候補）**：
  - インベントリに `.claude/skills/...` の4エントリを追加する。source は既存の `install_root/.agents/skills/...` で、sha256・mode も同一にする。`.claude` 側の `known_old_sha256` は空から始める。
  - allowlist には `.claude/skills/spec-dock/` と `.claude/skills/spec-dock-grill-with-docs/` だけを追加する（`.claude/**` は追加しない）。
  - uninstall では `.claude/` と `.claude/skills/` を残す。
- **SKILL.md の中立化（候補）**：
  - helper は「読み込まれたスキルディレクトリ」を基準に解決する。
  - preflight 8 から、`openai.yaml` を全ホスト共通の必須条件とする扱いを外す。
  - 静的投影の説明に `.claude/skills` を加える。
  - 「running Codex processes」や `.codex/config.toml` のようなホスト固有の言い回しを一般化する。
  - 両方の投影の内容は同一に保つ。
- **ADR（候補）**：
  - 新しい ADR で、epic-00074 の E-RQ-003 の配置制約を改訂する（Claude Code を対象に加える判断として記録する）。
  - 固定スロット ADR の「`.agents/skills` のみ」を、ホストごとの固定スロットへ拡張する。
  - 撤退条件（Claude Code が `.agents/skills` を読むようになった場合）と、retired allowlist の拡張手順を記す。

### 未検証

- A1 を実装した後、新しい Claude Code セッションで `.claude/skills/spec-dock` が実際に発見・起動されること（実機確認は未実施）。
- `disable-model-invocation: true` のスキルの description がスキル一覧の文脈に載らないこと。外部分析が公式表を根拠に指摘しているが、本調査では該当表を原文で確認していない。
- クラウドセッションが、リポジトリの `.claude/settings.json` で有効化したプラグインを読まないこと。外部分析が discover-plugins ページを根拠に指摘しているが、未確認。公式の plugins overview で確認できたのは「ローカル設定のプラグインを読まない」までである。

## Reflection

- 本 Issue の Requirement では、「Codex と Claude Code の両方が、導入済みの SpecDock スキルを各ホストのプロジェクト探索先から発見できること」を受け入れ条件にする。
- 配布方式（A1）、インベントリと allowlist の変更、uninstall の境界、SKILL.md の中立化、テスト方針は Design / Plan で確定する。
- epic-00074 E-RQ-003 と固定スロット ADR の改訂は、新しい ADR として accepted にしてから反映する。
- `installation show` の欠落判定の不整合は、本 Issue の範囲に含めるかを Requirement で判断する。
