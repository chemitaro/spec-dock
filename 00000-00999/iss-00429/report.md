---
種別: レポート（Issue）
ID: "iss-00429"
タイトル: "Add Canonical Catalog And Link"
関連GitHub: ["#429"]
最終更新: "2026-10-26"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00424", "init-00423"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

Epic の I-2 として、`spec-dock canonical link` と `spec-dock canonical status` を足し、後の Issue が使う契約 C3、C4、C5、C6、C11 の部品を置いた。公開の形は `design.md` のとおりである。

- **`canonical link`**（Epic の3章の手順1〜5と8）：どのチェックアウトからでも、そのクローンのカタログ（mainの `spec-dock/.canonical`、lock 済みの canonical のworktree）を見つけるか作り、`info/exclude` に無視の3行を足し、mainと実行したチェックアウトの `spec-dock/initiatives` を正しいリンク（mainは `.canonical`、作業用のworktreeは絶対パス）にする。何度実行しても同じで、2回目は `unchanged`。止まる条件（構成、git の版、マウント、ふさがった場所とリンク、別の場所のチェックアウト、書き込みの可否、移行していない仕様、接続）は、書く前にすべて確かめ、書いた後の失敗は `partial`（終了コード6）で効果を示す。新しいリポジトリでは、形式1の管理ファイルだけの親のないコミットを作って push し、同時の作成では先着のものを使う。`git clean -ffdx` の後は `git worktree add -f -f` で、mainの移動の後は `git worktree repair` で直し、`git worktree prune` は使わない。
- **`canonical status`**：12の項目（`catalog`、`link`、`exclude`、`access`、`tools`、`sync`、`changes`、`format`、`git`、`snapshot`、`dashboard`、`structure`）を返し、問題ごとに次の1手を示す。何も書かず、GitHub とリモートに問い合わせない。`sync`、`snapshot`、`dashboard`、`structure` と、`changes` の `state.json` の部分は「未対応」（I-3、I-11、I-4 が足す）。
- **ほかのコマンドから**：canonical モードの `worktree create` が、今の作成の処理の後にリンクの手順を行う。同じ手順を `link_after_command` として公開した（I-5 の `work start` が使う）。リンクの失敗は、呼ぶ側の結果を変えずに警告と次の1手で返す。
- **後の Issue の部品**：`require_linked`（`CANONICAL_NOT_LINKED`、`CANONICAL_FOREIGN_CHECKOUT`）、名前で Scope を探す `CatalogTree`、カタログの排他 `CatalogLock` と書く部品 `catalog_changes`（変更の束の版1）、canonical の中身 `CANONICAL_ROOT_FILES`、カタログに対する Git の1つの関数 `run_catalog_git`（フック、署名、fsmonitor、自動の gc を外す）、環境の判定 `RuntimeEnvironment`。
- **統括の判断で足したもの**：`spec-dock/initiatives/` の中から実行したときの `CANONICAL_INSIDE_CATALOG`、mainが版3のときにmainのリンクを置かない `CANONICAL_MAIN_NOT_MIGRATED`、移動の判定を実体で比べること（`plan.md` の「統括の判断」）。
- **配布資産**：`spec-dock/.gitignore` に無視の3行（`/.canonical/`、`/initiatives`、`!/initiatives/`）、`docs/reference_cli.md` に2つのコマンドの行（`C46 canonical link`、`C47 canonical status`。公開のコマンドは47個）、`static-inventory.json` の `sha256` と、変更の前の中身を `known_old_sha256` に足した。利用側の `spec-dock/` は変えていない（I-9、I-10）。
- **main の取り込み**（統括の指示 msg_8f0e0917a295）：`origin/main`（`e456dfc8b`。I-7 の #444 と Epic の文書の #443）を merge で取り込んだ。I-7 の `canonical check` の無視の3行を C3 の定数 `GITIGNORE_LINES` そのものにし、行と順の判定を domain の `ignore_rules_state` 1つにそろえた。順の規則は I-7 の意味（否定の行がその前の行より後ろ）にゆるめた。`IGNORE_RULES_MISSING` の次の1手は、配布資産の今か変更の前の中身なら `installation update`、利用者が変えた中身なら手での取り込みにした（`plan.md` の「main の取り込み」）。
- 実現しなかったこと：なし（I-2 の範囲で）。手順6と7、`--no-schedule`、同期の項目は計画どおり I-3 の担当である。

## Verification

（最終品質ゲートの結果は、ゲートの後に書き足す。）

### 実機の確かめ（2026-10-26）

- **macOS、外付けのボリューム**（scratchpad の下の一時のリポジトリと一時の bare のリポジトリ、wheel を入れた一時の venv。状態の置き場は一時）：新しいリポジトリの最初の `canonical link` が canonical を作って push し、カタログとリンクを置いた。2回目は `unchanged`。作業用のworktreeの `canonical link` は絶対パスのリンクだけを置き、そこで書いた仕様がmainから読めた。両方の `git status` は空だった。2つ目のクローンは GitHub（bare）の canonical を取り込んだ。`canonical status` は、Claude Code の設定にカタログがないことを1行で示した（利用者の `~/.claude/settings.json` を読むだけ。変えていない）。
- **Codex のサンドボックス**（codex-cli 0.163.0、seatbelt。`~/.codex/config.toml` は変えていない）：
  - `codex sandbox -P :workspace -C <作業用のworktree> -- spec-dock canonical status` は、`CODEX_SANDBOX` を見て、カタログに書けないことと `writable_roots = ["<カタログ>"]` の1行を示した。
  - 同じサンドボックスで、カタログと除外がそろっていてリンクを置くだけの `canonical link` は成功した。カタログの作成が要る新しいクローンでの `canonical link` は、`.git`、`.git/info`、`.git/worktrees` に書けないことを示して `CANONICAL_SANDBOX_DENIED` で止まり、何も書かなかった。
  - カタログへの `flock` は、サンドボックスの外が持つ間、中から取れず（BUSY）、放した後は取れた。
  - 未確認：示した `writable_roots` の1行を足した後に書けるようになること。この版の `codex sandbox` は、`-P :workspace` で `[sandbox_workspace_write].writable_roots`（`-c` の上書きと、一時の `CODEX_HOME` の両方）を反映しなかった。`-P` を付けないと、作業ディレクトリにも書けなかった。Codex の設定の形が、権限のプロファイルに変わりつつある可能性がある（I-9 の文書で確かめる）。
- **Claude Code**（`claude -p`、既定の権限モード）：作業用のworktreeから、リンク経由の `Read` は、追加の設定なし（空の `--settings`）では拒否され（`permission_denials` に `Read`）、SpecDock が示す1行だけを書いた一時の `--settings` のファイルでは読めた。未確認：同じ1行をユーザーの設定のファイル（`~/.claude/settings.json`）に書いたときの動き。一時の `HOME` では Claude Code にログインできず（`Not logged in`）、利用者の設定は変えない決まりのため。
- **Linux**（OrbStack 2.2.5 の Ubuntu 24.04 の仮想マシン `specdock-i2-test`、arm64、Git 2.43.0、Python 3.12.3）：wheel を入れて、新しいリポジトリの `canonical link`、作業用のworktreeのリンク、そこで書いた仕様がmainから読めること、カタログへの `flock` が別のプロセスと排他になること、`git clean -ffdx` の後の作り直し（`add -f -f`）、mainの移動の後の `repair` と `CANONICAL_MAIN_MOVED`、権限 555 のカタログで `CODEX_SANDBOX` を設定したときの `writable_roots` の1行を確かめた。この Issue のテスト（212件）も仮想マシンの中で通った。資格情報は写していない。確かめた後に仮想マシンを消した。
  - 未確認：Linux の Codex のサンドボックス（Landlock）の中の `os.access` と `flock`（Linux の Codex を動かしていない）。Git 2.38 での動き（手元にない。2.43 と 2.47 と 2.54 で確かめた）。
- **Docker**（`python:3.12-slim`、Git 2.47.3）：macOS で作ったカタログのあるリポジトリを、ホストと別のパス（`/work/repo`）にマウントし、コンテナの中で `canonical link` を実行すると、`CANONICAL_FOREIGN_CHECKOUT`（終了コード3、効果なし）で止まり、`canonical status` も `foreign` を示した。仕様のファイル自体はリンク経由で読めた。ホストの `.git/worktrees/` と、カタログと作業用のworktreeの `.git` ファイルは、前後で同じだった。コンテナは `--rm` で消え、取得したイメージは消した。

## Residual Risks / Follow-ups

- Codex の `writable_roots` の1行の効き目と、Claude Code の1行をユーザーの設定ファイルに書いたときの動きは未確認（上）。I-9 の使い方の文書で、Codex の今の設定の形（権限のプロファイル）を確かめる必要がある。
- Linux の Codex のサンドボックス（Landlock）では `os.access` が拒否を返さないおそれがある。その場合も、書くときの拒否を `CANONICAL_SANDBOX_DENIED` と次の1手で示すようにした。
- I-3 への引き渡し：`plan.md` の「exit / handoff」のとおり（手順6と7、`schedule` の引数、`sync_item` と `snapshot_item` の置き換え、10分の未pushの警告）。
- I-9 への申し送り：`worktree create` のヘルプと参照の文書に、canonical モードでリンクを置くことを書く。配布資産の `docs/cli-redesign-guide.html`（と利用側の写し）の「全44コマンド」と一覧が、47個（I-7 の `canonical check` と、この Issue の2つ）に追いついていない。
- `canonical link` と `canonical status` の `IGNORE_RULES_MISSING`（`spec-dock/.gitignore`）の次の1手は、設計どおり常に `installation update` である。I-7 の `canonical check` は、利用者が変えた `.gitignore` に手での取り込みを示す。そろえるかは I-9 の文書の整理で判断できる（この Issue の設計の範囲外のため変えていない）。
