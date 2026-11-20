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
| 19 | linked（一時のリポジトリを、利用者の `trustedWorkspaces` の中のフォルダー（この worktree の Git の外の `.workbench` の下）に作った） | なし（利用者の設定：`allowNonWorkspaceAccess: true`、`trustedWorkspaces` にその親、`permissions` はコマンドの規則だけ） | ファイルの道具の書き込みが拒まれた（『a tool required the "write_file" permission ... auto-denied』） |
| 20 | 19 と同じ | 19 に、`--settings` で 5 の規則と `command(touch)` | 読み、ファイルの道具の作成、端末の `touch` とも成功 |

既定の状態（1〜14、利用者の設定に権限の項目がなく、一時のリポジトリは信頼済みのフォルダーの外）でも、利用者が設定した後の状態（15〜20、`allowNonWorkspaceAccess: true`、信頼済みの親のフォルダー）でも、linked worktree でカタログに書くには `read_file`・`write_file` の規則が要り、規則があれば通った。案内の結論は、利用者のこれらの設定に依らない。`allowNonWorkspaceAccess: true` は、権限の規則がない状態では（6）読み書きを通したが、利用者の設定が `agentMode`・`ask`・`deny` を持つ状態では（15、19）書き込みを通さなかった。`trustedWorkspaces` は、カタログへの書き込みの可否を変えなかった（19）。

まとめ：

- R-01：linked worktree では設定が要る。`permissions.allow` の `read_file(<カタログ>)` と `write_file(<カタログ>)` で、ファイルの道具も端末の書き込みも通る（その回だけの `--settings` で確かめた）。保存の場所は、公式のスキーマのとおりユーザーの設定 `~/.gemini/antigravity-cli/settings.json` で、環境変数でもプロジェクトの設定でも動かせない。Antigravity の中は `ANTIGRAVITY_AGENT` で見分けられる。
- R-02：Claude Code の隔離セッション（`--worktree`）のような、設定を足しても書けない動き方は見つからなかった。`--sandbox` は、既定で有効な端末の制限と区別できる違いがなかった。`--mode plan` は全体として書かない計画のモードで、カタログに限った決まりは要らない。配るスキルと AGENTS.md の『仕様の扱い』は変えない。
- 確かめられなかったこと（推定で書いたこと）：
  - 保存された設定 `~/.gemini/antigravity-cli/settings.json` に規則を置いて、カタログに書けること。利用者の設定を書き換えない約束のため、直接は試していない。根拠は、スキーマ（18）、`--settings` の説明『a JSON object of settings.json keys』、ログが両方の `permissions` を同じ形で読み込むこと（17）。
  - 対話のモード（Orca が起動するふつうの `agy`）での確かめの画面の文言。print のモードは確かめの画面を出さず、自動で拒む（上の 1 の文言）ので、対話のモードでは許可を問う画面が出ると推定する。
  - `--sandbox` が、既定の端末の制限（8、9）と別に何かを変えるか。スキーマは `enableTerminalSandbox` を1回だけ有効にするものと書き、8 の結果は `--sandbox` の有無で同じだった。
- AGENTS.md の『仕様の扱い』は、配るスキルの同じ節とバイトが同じだが、生成するコードはなく、手で写したもの（`git log -- AGENTS.md`、ランタイムに AGENTS.md を書くコードはない）。

## Outcome

Antigravity の中の linked worktree で、`canonical status`（と `canonical link` の警告）が `data.tools.antigravity` の1行と警告を示し、配る案内に Antigravity の設定を書いた（`git diff 83b8ee95f 5248c23b8`）。

- S-01（タスク担当）：`canonical.md`（Antigravity の項、1行、deny・ask の優先、足さないときの症状、`--add-dir`、確かめた版と方法、信頼したフォルダーや `allowNonWorkspaceAccess` があっても規則が要ること、確かめ方）と `reference_cli.md` の C45。提供側と dogfood はバイト一致。`static-inventory.json` の2行の `sha256` を今のバイトにし、0.9.9 のバイト（canonical.md `dd91f171…`、reference_cli.md `9375d7fd…`）を `known_old_sha256` に足した。コミット 1618ab797、487276c1b、9ed97a284、18cfbbd3e、5248c23b8。
- S-02（実装担当、64f571e32）：`RuntimeEnvironment.antigravity`（`ANTIGRAVITY_AGENT`）、domain の `antigravity_user_settings`・`antigravity_setting_line`・`antigravity_allows`、application の `tools.antigravity` と警告、`isolate_user_state` が `ANTIGRAVITY_AGENT` を消す。テスト `tests/cli_runtime/test_issue673_canonical_status_antigravity.py`、`tests/unit/domain/test_canonical_tools_antigravity.py`、`tests/unit/infra/test_issue436_docs.py` の T-06。
- R-02：配るスキルと AGENTS.md の『仕様の扱い』は変えていない（設定を足しても書けない動き方がない）。
- presentation は変えていない（`CanonicalStatusData.tools` は `dict[str, object]`）。

### 実装担当

- Codex GPT-6.2 Sol / medium（dispatch ctx_378bdfc6e67b、launch.effective：codex・gpt-6.2-sol・medium）。確認の画面で止まらず、S-02 を1回で終えた。記録 `.workbench/implement/iss-00673/report.md`。

### 次の版の migration.md の節に書く文（案）

- `spec-dock canonical status --json` の `data.tools` に `antigravity` の項目（`session`、`needed`、`configured`、`sources`、`file`、`line`）が増えた。Antigravity の中（環境変数 `ANTIGRAVITY_AGENT`）の作業用のworktreeで、`~/.gemini/antigravity-cli/settings.json` の `permissions.allow` にカタログの `read_file(...)` と `write_file(...)` がないと、警告 `CANONICAL_TOOL_SETTING_MISSING`（`details.tool` は `antigravity`）と足す1行を示す。Antigravity の外では、警告と `tools.status`・`tools.next_step` は前と同じ。
- Antigravity を使う人は、作業用のworktreeで `spec-dock canonical status` が示す1行を、ユーザーの設定に1回だけ足す（`docs/canonical.md` の『ツールの設定』）。
- 配布資産では `docs/canonical.md` と `docs/reference_cli.md` が変わる。0.9.9 のバイトは既知の古い版として `installation update` で上書きできる。

## Verification

- 最終品質ゲート iss-00673-fqg-1 attempt 1（5248c23b8）：**合格**。
  - 主のレビュー（quality-gate-reviewer opus / medium）：P0〜P2 0、P3 1、coverage complete。
  - 2人目（chatgpt-code-review-strict、GPT-6 / Extra High）：P0・P1 なし、P2 1。review_status は、仕様のブランチを読めなかった証拠不足による fail（ゲートの条件ではない）。
  - `make lint`：exit 0。`uv run pytest`：exit 0（4392 passed / 7 skipped、43分10秒）。
  - closure：`.workbench/final-quality-gate/iss-00673-fqg-1/closure.md`（この worktree）。区切りのレビューは計画どおりなし。記録だけのコミットはない（記録は Git の外）。
- PR #677（https://github.com/chemitaro/spec-dock/pull/677）：head は 5248c23b8（合格のコミット）。CI はすべて合格（provider-tests 14分51秒、distribution parity の macOS・Ubuntu、check、spec-dock-check、route）。observer の結果は observable_ci PASS、merge_readiness READY、mergeStateStatus CLEAN（`.workbench/coding-task/iss-00673/ci-watch-2.jsonl`。1本目は provider-tests の途中で idle timeout になったので、上限を延ばして1本だけ走らせ直した）。マージは統括。

## 逸脱と判断

- 2人目のレビュー：standard の方針は2人目なしだが、依頼書の指示で ChatGPT（仕様のレビューは chatgpt-spec-review-strict、ゲートは chatgpt-code-review-strict）を使った。仕様のレビューの ChatGPT は round-1 の版だけを見た。
- 仕様のレビューの P2・P3 も、確かめの範囲の書き方と判定の欠けなので、直してから合格させた（round-3 で P0〜P3 0）。
- ChatGPT の仕様のレビューの P2 は、案内の文書だけで直した（18cfbbd3e）。
- 確かめの途中で、利用者の Antigravity の設定が本人によって変わった（10:49、統括が本人の設定と判断）。表の 15〜20 は変わった後の状態で行い、結論が利用者の設定に依らないことを 19・20 で確かめた。
- 統括の確認（2026-11-20）：`trustedWorkspaces` に足された2件は、この確かめによるものではない（作業ディレクトリは scratchpad の下で、`trustedWorkspaces` を渡していない）。

## Residual Risks / Follow-ups

- 保存された設定に規則を置いて書けることは、直接は確かめていない（『確かめられなかったこと』）。版を出した後、統括が実際の Orca の Antigravity のエージェントで `canonical status` と読み書きを確かめる（Epic の verification）。
- ゲートの P2（ChatGPT）：`deny`・`ask` の `read_file(*)` などを数えないので、誤って「設定あり」になる場合がある。公式の資料（https://antigravity.google/docs/permissions の global wildcard）を確かめたうえで、`*` を deny・ask では判定できない、allow では許すとして扱う小さな Issue を提案する。
- ゲートの P3：Antigravity の外で判定が null のときのテストを足すとよい。
- Antigravity の中の linked worktree では、今の Claude Code の警告も出る（Claude Code を使わない人には要らない警告）。Claude Code の警告を `CLAUDECODE` で絞るかは、別の判断（この Issue の対象外）。
- Antigravity の端末から linked worktree の Git を操作するとき（Git の情報が作業ディレクトリの外にある）の扱いは、確かめていない。
- `work finish iss-00673` は実行していない（マージの後に統括が行う）。
