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

- 仕様のレビュー round-1（spec-reviewer opus / high、standard、固定 1618ab797）：合格。P0 0、P1 0、P2 1（保存される設定のファイルが効くことを確かめず、確かめ済みと書いた）、P3 1（読めない設定のテストがない）。両方を直した。結果 `.workbench/spec-review/iss-00673/round-1.json`、応答 `review-response.md`。
- round-2（同じレビュアー、固定 487276c1b）：合格。P2 1（deny・ask で偽のとき警告が原因を示さない）、P3 1（表の 6 と 16 の食い違い）。両方を直した（9ed97a284）。
- round-3（同じレビュアー、固定 9ed97a284）：**合格**。P0〜P3 0。結果 `round-3.json`、検査 `round-3.check.json`（valid、status pass）。
- 2人目（依頼書の指示、chatgpt-spec-review-strict、GPT-6 / Extra High、モデルと推論の選択の証拠 verified=yes、Oracle のセッション `required-strict-github-connector-verificati-1530`）：カタログ c3f468dac（round-1 の版）を GitHub の接続で読み、review_status pass、P0・P1 なし、P2 1（Claude Code の警告は Antigravity の中でも作業用のworktreeで出るので、案内の確かめ方『tools の status が ok』が Antigravity だけの利用者に合わない）。妥当として、案内の文書だけを直した（18cfbbd3e。仕様の .cue は変えていない）。答えは JSON が Markdown の escape（`\`、`&#x20;`）付きで返り、生の JSON の形ではなかったので、材料として扱った。round-2・3 の版は ChatGPT に再び見せていない（standard は2人目を要さない。方針どおり）。
- 合格した文書の sha256：requirement.cue `bce03aa759d413bf390248f3d6591079a9172c733dc8704a06fd6d22e8d3dcd7`、design.cue `51ffd44324d7d744e894f53d1bb545297535c80316ac71c52ed0dbddffa8adb1`、plan.cue `ebbe6b3c7bd537f46351c23c95caf6d9afdc8ed89563c355e8634b50f3e49aab`（以後 plan.cue は手順の status だけを書き換える）。

## 実物での確かめ

2026-11-20、タスク担当（Claude Opus 5.5 / medium）が、この PC の `agy` で確かめた。

- 版：`agy --version` が `1.5.12`（Homebrew の cask `antigravity-cli`、macOS、arm64）。既定のモデル（利用者の設定）は Gemini 3.8 Flash。
- 場所：一時のディレクトリ（Claude Code の scratchpad の下。利用者のホームと、`trustedWorkspaces` の外）に、`git init` の main のチェックアウトと、`git worktree add` の linked worktree を作った。main の `spec-dock/.canonical/note.txt` に印の文字列を置き、main の `spec-dock/initiatives` は `.canonical` への相対のリンク、linked の `spec-dock/initiatives` は main の `spec-dock/.canonical` への絶対のリンク（`tests/support/canonical_repo.py` と同じ形）。本物のカタログには書いていない。
- 方法：その worktree を作業ディレクトリにして `agy -p "<指示>" --print-timeout 200s`。設定は、その回だけの `--settings '<JSON>'` か `--add-dir` で与えた。利用者の `~/.gemini/` の設定のファイルは読むだけで、書き換えていない。
- 利用者の設定の変化：1〜14 の時点（10:30〜10:40 ごろ）の `~/.gemini/antigravity-cli/settings.json` は `model` と `trustedWorkspaces` だけだった。10:49 に、この作業の外で（タスク担当は書いていない）`$schema`、`agentMode`、`allowNonWorkspaceAccess: true`、`permissions`（`allow` は `command(git status)` などのコマンドだけ、`deny`、`ask`）が足された。15〜18 はこの後の状態で行った。
- 設定の項目の名前は、実行ファイルの文字列（`json:"..."` の鍵、案内の文言）から候補を拾い、実行で確かめた。

| # | 作業ディレクトリ | 与えた設定 | 結果 |
|---|---|---|---|
| 1 | linked | なし | ファイルの道具の読みが止まった。`jetski: no output produced — a tool required the "read_file" permission that headless mode cannot prompt for, so it was auto-denied. Add an allow-rule under permissions.allow in settings.json (e.g. read_file(<target>)).` |
| 2 | linked | なし（作業ディレクトリの中のファイル） | 読み書きとも成功 |
| 3 | linked | `--add-dir <カタログ>` | ファイルの道具の読み書き、端末の `touch` とも成功 |
| 4 | linked | `--settings '{"additionalDirectories":[...]}'` | `Error: --settings: unknown setting "additionalDirectories"`（項目がない） |
| 5 | linked | `permissions.allow: ["read_file(<カタログ>)","write_file(<カタログ>)"]` | ファイルの道具の読み書きとも成功 |
| 6 | linked | `allowNonWorkspaceAccess: true` | 読み書きとも成功（外のすべてを許す）。このときの利用者の設定は `model` と `trustedWorkspaces` だけだった。16 とは、利用者の設定（`agentMode`、`ask`、`deny` など）が違う |
| 7 | linked | 5 と `command(touch)` | ファイルの道具の作成、端末の `touch spec-dock/initiatives/...` とも成功。`--sandbox` を付けても同じ |
| 8 | linked | `command(touch)` だけ | 端末の `touch spec-dock/initiatives/...` が `Operation not permitted`（exit 1）。`touch /tmp/...` は成功。`--sandbox` の有無で同じ |
| 9 | linked | 8 に `enableTerminalSandbox: false` | 端末の `touch spec-dock/initiatives/...` が成功（8 の拒否は Antigravity の端末の制限で、既定で有効） |
| 10 | linked | 5 の規則を、作業ディレクトリの `.agents/settings.json`、`.gemini/settings.json`、`.gemini/antigravity-cli/settings.json`、`.antigravity/settings.json` に置いた（`--settings` なし） | 1 と同じく拒まれた（プロジェクトの設定としては効かない） |
| 11 | main | `command(touch)` だけ | ファイルの道具の読み書き、端末の `touch` とも成功（設定は要らない） |
| 12 | linked | 5 の規則を、カタログの親（main のチェックアウト）で | ファイルの道具の作成、端末の `touch` とも成功 |
| 13 | linked | 5 と `--mode plan` | ファイルは作られず、端末のコマンドも許可の規則があるのに拒まれた（計画のモードは全体として書かない） |
| 14 | linked | `command(env)` など | 端末のコマンドに `ANTIGRAVITY_AGENT=1`、`ANTIGRAVITY_APP_DATA_DIR=<ホーム>/.gemini/antigravity-cli`、`ANTIGRAVITY_LS_VERSION=cli-1.5.12`、`ANTIGRAVITY_CONVERSATION_ID` などが渡る |
| 15 | linked | 環境変数 `ANTIGRAVITY_APP_DATA_DIR=<一時のディレクトリ>`（5 の規則の `settings.json` を置いた） | ファイルの道具の書き込みが拒まれた。`--log-file` のログでは `CLI app data directory: <ホーム>/.gemini/antigravity-cli` のままで、読み込んだ `permissions` は利用者の設定のもの（環境変数は入力として効かない） |
| 16 | linked | 15 と同じ（読みだけ） | 読みは通った。読みの規則がないので、利用者の設定の `allowNonWorkspaceAccess: true` によると考える（15 の書き込みは同じ状態で拒まれたので、それだけでは書き込みが通らない） |
| 17 | linked | 利用者の設定（10:49 以後）に、`--settings` で 5 の規則 | ファイルの道具の書き込みが成功。ログは `--settings` の規則を `CLI settings initialized: permissions=&{Allow:[read_file(...) write_file(...)] ...}` と読み込む（保存された設定の `permissions` も同じ行で読み込まれる） |
| 18 | — | 公式のスキーマ `https://antigravity.google/schemas/v1/settings.json`（利用者の設定の `$schema`） | 『stored in ~/.gemini/antigravity-cli/settings.json』。`permissions` は `allow`・`ask`・`deny`、規則は `^(command\|read_file\|write_file\|read_url\|execute_url\|mcp\|unsandboxed)\(.*\)$`、『A deny rule takes precedence over an ask rule, and an ask rule over an allow rule』。`allowNonWorkspaceAccess` は『subject to toolPermission, agentMode, and your permission rules』。`enableTerminalSandbox` は『Runs the agent's terminal commands in the terminal sandbox ... --sandbox turns it on for one session』 |

まとめ：

- R-01：linked worktree では設定が要る。`permissions.allow` の `read_file(<カタログ>)` と `write_file(<カタログ>)` で、ファイルの道具も端末の書き込みも通る（その回だけの `--settings` で確かめた）。保存の場所は、公式のスキーマのとおりユーザーの設定 `~/.gemini/antigravity-cli/settings.json` で、環境変数でもプロジェクトの設定でも動かせない。Antigravity の中は `ANTIGRAVITY_AGENT` で見分けられる。
- R-02：Claude Code の隔離セッション（`--worktree`）のような、設定を足しても書けない動き方は見つからなかった。`--sandbox` は、既定で有効な端末の制限と区別できる違いがなかった。`--mode plan` は全体として書かない計画のモードで、カタログに限った決まりは要らない。配るスキルと AGENTS.md の『仕様の扱い』は変えない。
- 確かめられなかったこと（推定で書いたこと）：
  - 保存された設定 `~/.gemini/antigravity-cli/settings.json` に規則を置いて、カタログに書けること。利用者の設定を書き換えない約束のため、直接は試していない。根拠は、スキーマ（18）、`--settings` の説明『a JSON object of settings.json keys』、ログが両方の `permissions` を同じ形で読み込むこと（17）。
  - 対話のモード（Orca が起動するふつうの `agy`）での確かめの画面の文言。print のモードは確かめの画面を出さず、自動で拒む（上の 1 の文言）ので、対話のモードでは許可を問う画面が出ると推定する。
  - `--sandbox` が、既定の端末の制限（8、9）と別に何かを変えるか。スキーマは `enableTerminalSandbox` を1回だけ有効にするものと書き、8 の結果は `--sandbox` の有無で同じだった。
- AGENTS.md の『仕様の扱い』は、配るスキルの同じ節とバイトが同じだが、生成するコードはなく、手で写したもの（`git log -- AGENTS.md`、ランタイムに AGENTS.md を書くコードはない）。

## Outcome

## Verification

## 逸脱と判断

## Residual Risks / Follow-ups
