---
種別: レポート（Issue）
ID: "iss-00673"
関連GitHub: ["#673"]
最終更新: "2026-11-20"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## レビュー記録

（仕様のレビューの合格の後に書く）

## 実物での確かめ

2026-11-20、タスク担当（Claude Opus 5.5 / medium）が、この PC の `agy` で確かめた。

- 版：`agy --version` が `1.5.12`（Homebrew の cask `antigravity-cli`、macOS、arm64）。既定のモデル（利用者の設定）は Gemini 3.8 Flash。
- 場所：一時のディレクトリ（Claude Code の scratchpad の下。利用者のホームと、`trustedWorkspaces` の外）に、`git init` の main のチェックアウトと、`git worktree add` の linked worktree を作った。main の `spec-dock/.canonical/note.txt` に印の文字列を置き、main の `spec-dock/initiatives` は `.canonical` への相対のリンク、linked の `spec-dock/initiatives` は main の `spec-dock/.canonical` への絶対のリンク（`tests/support/canonical_repo.py` と同じ形）。本物のカタログには書いていない。
- 方法：その worktree を作業ディレクトリにして `agy -p "<指示>" --print-timeout 200s`。設定は、その回だけの `--settings '<JSON>'` か `--add-dir` で与えた。利用者の `~/.gemini/` の設定のファイルは読むだけで、書き換えていない（中身：`antigravity-cli/settings.json` は `model` と `trustedWorkspaces` だけ、`config/config.json` は plugins だけで、権限の設定はない）。
- 設定の項目の名前は、実行ファイルの文字列（`json:"..."` の鍵、案内の文言）から候補を拾い、実行で確かめた。

| # | 作業ディレクトリ | 与えた設定 | 結果 |
|---|---|---|---|
| 1 | linked | なし | ファイルの道具の読みが止まった。`jetski: no output produced — a tool required the "read_file" permission that headless mode cannot prompt for, so it was auto-denied. Add an allow-rule under permissions.allow in settings.json (e.g. read_file(<target>)).` |
| 2 | linked | なし（作業ディレクトリの中のファイル） | 読み書きとも成功 |
| 3 | linked | `--add-dir <カタログ>` | ファイルの道具の読み書き、端末の `touch` とも成功 |
| 4 | linked | `--settings '{"additionalDirectories":[...]}'` | `Error: --settings: unknown setting "additionalDirectories"`（項目がない） |
| 5 | linked | `permissions.allow: ["read_file(<カタログ>)","write_file(<カタログ>)"]` | ファイルの道具の読み書きとも成功 |
| 6 | linked | `allowNonWorkspaceAccess: true` | 読み書きとも成功（外のすべてを許す） |
| 7 | linked | 5 と `command(touch)` | ファイルの道具の作成、端末の `touch spec-dock/initiatives/...` とも成功。`--sandbox` を付けても同じ |
| 8 | linked | `command(touch)` だけ | 端末の `touch spec-dock/initiatives/...` が `Operation not permitted`（exit 1）。`touch /tmp/...` は成功。`--sandbox` の有無で同じ |
| 9 | linked | 8 に `enableTerminalSandbox: false` | 端末の `touch spec-dock/initiatives/...` が成功（8 の拒否は Antigravity の端末の制限で、既定で有効） |
| 10 | linked | 5 の規則を、作業ディレクトリの `.agents/settings.json`、`.gemini/settings.json`、`.gemini/antigravity-cli/settings.json`、`.antigravity/settings.json` に置いた（`--settings` なし） | 1 と同じく拒まれた（プロジェクトの設定としては効かない） |
| 11 | main | `command(touch)` だけ | ファイルの道具の読み書き、端末の `touch` とも成功（設定は要らない） |
| 12 | linked | 5 の規則を、カタログの親（main のチェックアウト）で | ファイルの道具の作成、端末の `touch` とも成功 |
| 13 | linked | 5 と `--mode plan` | ファイルは作られず、端末のコマンドも許可の規則があるのに拒まれた（計画のモードは全体として書かない） |
| 14 | linked | `command(env)` など | 端末のコマンドに `ANTIGRAVITY_AGENT=1`、`ANTIGRAVITY_APP_DATA_DIR=<ホーム>/.gemini/antigravity-cli`、`ANTIGRAVITY_LS_VERSION=cli-1.5.12`、`ANTIGRAVITY_CONVERSATION_ID` などが渡る |

まとめ：

- R-01：linked worktree では設定が要る。保存される設定は、ユーザーの設定 `~/.gemini/antigravity-cli/settings.json`（`ANTIGRAVITY_APP_DATA_DIR` のディレクトリ）の `permissions.allow` の `read_file(<カタログ>)` と `write_file(<カタログ>)`。この2つで、ファイルの道具も端末の書き込みも通る。プロジェクトの設定の置き場は見つからなかった。Antigravity の中は `ANTIGRAVITY_AGENT` で見分けられる。
- R-02：Claude Code の隔離セッション（`--worktree`）のような、設定を足しても書けない動き方は見つからなかった。`--sandbox` は、既定で有効な端末の制限と区別できる違いがなかった。`--mode plan` は全体として書かない計画のモードで、カタログに限った決まりは要らない。配るスキルと AGENTS.md の『仕様の扱い』は変えない。
- 確かめられなかったこと：対話のモード（Orca が起動するふつうの `agy`）での確かめの画面の文言。print のモードは確かめの画面を出さず、自動で拒む（上の 1 の文言）ので、対話のモードでは許可を問う画面が出ると推定する（推定）。
- AGENTS.md の『仕様の扱い』は、配るスキルの同じ節とバイトが同じだが、生成するコードはなく、手で写したもの（`git log -- AGENTS.md`、ランタイムに AGENTS.md を書くコードはない）。

## Outcome

## Verification

## 逸脱と判断

## Residual Risks / Follow-ups
