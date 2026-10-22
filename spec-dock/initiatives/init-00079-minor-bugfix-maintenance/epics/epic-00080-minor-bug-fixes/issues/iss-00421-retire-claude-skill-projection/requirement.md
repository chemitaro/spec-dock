---
種別: 要件定義書（Issue）
ID: "iss-00421"
タイトル: "Retire the Claude Code skill projection"
関連GitHub: ["#421"]
状態: "draft"
最終更新: "2026-10-22"
親: ["epic-00080", "init-00079"]
---

# iss-00421 Retire the Claude Code skill projection — 要件定義

詳細: [Requirement Guide](../../../../../../docs/authoring/requirement.md)

## 目的
SpecDock は同梱スキルを `.agents/skills/<name>/` にだけ配置し、Claude Code への取り込みは Claude Code 側のフックとスキルに任せる。既存の `.claude/skills/spec-dock*` のコピーは、安全に退役させる。

## 背景
- iss-00418（accepted ADR `20261014t072234z-adr`）により、installer は同梱スキルを `.agents/skills/<name>/` と `.claude/skills/<name>/` の両方へコピーしている。
- 2026-10-22、product owner が `.claude` 側への配置をやめ、取り込みを Claude Code 側に委ねると決定した。決定の原文と Claude Code 側の契約は ADR `20261022t104008z-adr`（本 Issue の Artifact）に記録する。
- Claude Code 側は、`.claude/skills/<name>` → `../../.agents/skills/<name>` の相対リンクを作る。現行の installer は親チェーンの symlink で停止するため、リンクにした worktree では update・uninstall が失敗する。

## 観測可能な要件
- RQ-421-01: `installation init` は `.claude/` 配下に何も作らない。`.agents/skills/<name>/` の4ファイルは従来どおり作る。
- RQ-421-02: `installation update --backup-dir ABS --yes` は、`.claude/skills/spec-dock/` と `.claude/skills/spec-dock-grill-with-docs/` にある配布済みのファイル（既知のハッシュ）だけを、バックアップしてから除去する。共有の親、slot ディレクトリ、slot 内の未知のファイル、利用者の設定と他のスキルは保持する。空のディレクトリは残ってよい。dry-run は何も変更せず、適用後の再実行は `unchanged` になる。
- RQ-421-03: 退役対象のパスに未知の内容のファイルがあれば、update と uninstall は効果0で停止し、手動マージを求める。
- RQ-421-04: `.claude`、`.claude/skills`、`.claude/skills/<slot>` のいずれかがシンボリックリンク（リンク先がないものを含む）であれば、その slot は管理外とする。init / update / show / uninstall はエラーにならず、リンクをたどらず、リンクとリンク先を変更しない。
- RQ-421-05: uninstall は `.agents` 側の管理ファイルと、残っている `.claude` 側の既知のコピーを除去する。
- RQ-421-06: `AGENTS.md`、`README.md`、同梱の `spec-dock` SKILL.md、`overview.md` は、スキルを `.agents/skills` にだけ配置することと、Claude Code では相対リンクで取り込むことを説明する。
- RQ-421-07: この dogfooding repo の `.claude/skills/spec-dock*` を、コピーから相対リンク2本に置き換えてコミットする。
- RQ-421-08: wheel の current inventory は `.claude` のエントリを含まず、retired inventory は `.claude` 側の4エントリを含む。

## スコープ
- 対象: インベントリ、retired allowlist、update / uninstall の退役処理、`asset_layout.py`、文書、テスト、dogfood の `.claude/skills`、新しい ADR。
- 対象外:
  - Claude Code 側のフック・スキル（`~/.claude`）、`~/.agents`、他のリポジトリ
  - 他の worktree や導入先での `installation update`
  - パッケージの公開とユーザーのツール環境の更新
  - spec-dock による `.claude/skills` のリンクの作成・削除
  - grill スキルの本文（`.claude/skills/` 経由での読み込みも引き続き正しいため変更しない）
- 維持する親契約（Issue 413、AC-413-37）: 明示した1つの worktree だけを変更し、既知の静的資産だけを扱い、fail-closed で停止する。変更には `--backup-dir ABS` と `--yes` を要求し、journal と自動 rollback を持たない。

## 失敗・境界条件
- 退役対象の slot が実体ディレクトリで、その中のファイルがファイル単位の symlink、hard link、特殊ファイルなら、従来どおり停止する。
- `.claude` が通常ファイルなら、従来どおり停止する。
- 退役で除去したファイルのバックアップは、既存の update と同じく `static/<path>` に保存する。
- update はファイルごとの順次処理である。途中で失敗した場合は、既存の partial 報告で効果を示す。

## 受け入れ条件
- AC-421-01: fresh init の後、`.claude/` が存在しない。
- AC-421-02: 旧版の `.claude` コピーを持つ worktree で update すると、既知の4ファイルだけが除去され、バックアップに保存される。利用者のファイルと slot 内の未知のファイルは残る。dry-run は無変更、再実行は `unchanged`。
- AC-421-03: 退役対象の `.claude` 側ファイルが未知の内容のとき、update と uninstall は効果0で停止する。
- AC-421-04: `.claude/skills/<slot>` が `../../.agents/skills/<slot>` へのリンクのとき、init / update / show / uninstall がエラーにならない。init / update / show の前後で `.agents` 側のファイルが変わらない。uninstall は `.agents` 側を自身のパスで除去するだけで、`.claude` 側のリンクは残る。`.claude` 全体がリンクの場合も、リンク先は変わらない。
- AC-421-05: `make lint` と `uv run pytest` が通る。
- AC-421-06: 候補 wheel の CLI で、この worktree の `installation update` が `.claude` 側のコピーを除去する。相対リンクに置き換えた後も、候補 CLI の `installation show` と `installation update` がエラーにならない。

## 制約・前提
- 退役に登録するハッシュは、`.claude` 側のエントリが current inventory に記録されたことのある値（git の履歴で確認）とする。
- ユーザーのインストール済みパッケージ、`~/.claude/**`、`~/.agents/**` は変更しない。
