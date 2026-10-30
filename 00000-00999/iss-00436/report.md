---
種別: レポート（Issue）
ID: "iss-00436"
タイトル: "Integrate Agent Rules Docs And Release"
関連GitHub: ["#436"]
最終更新: "2026-10-30"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00424", "init-00423"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

canonical モードの全体をつないで確かめ、エージェント向けの規則、使い方の文書、CLI 参照と `help` をそろえ、版を 0.3.0 にした。起点は `origin/main` の `ea3d3c9ee`。

- **規則の節**（R-436-01）：配布するスキル `src/spec_dock/assets/install_root/.agents/skills/spec-dock/SKILL.md` と `AGENTS.md` に、同じ13項目の「仕様の扱い（canonical モード）」を置いた（Epic 10章の11項目と、ID・slug・題名・既定のブランチ名、`SCOPE_KIND_CHANGED`・`SCOPE_IN_PROGRESS` の2項目。`scope move` と180秒の待ちも書いた）。2つの「破壊的なコマンド」の一覧に `canonical remove` を足した。
- **使い方の文書**（R-436-02）：配布する `spec-dock/docs/canonical.md` を新設（モードと置き場、用意と状態、ツールの設定、保存と同期、同期が止まったとき、Linux とコンテナ、構造のスナップショットとダッシュボード、制約、既定のブランチの検査、エラーと次の1手）。`docs/README.md`、`guide.md`、`migration.md`、`reference_cli.md`、リポジトリの `README.md` から参照する。`scripts/migrate-to-canonical/README.md` に `XDG_STATE_HOME` を一時にする理由を足した。
- **CLI 参照と help**（R-436-03）：`reference_cli.md` の数を53にし、canonical モードの置き場・ID・`--slug`・`--title`・既定のブランチ名・`work finish` の待ちを書いた。`cli-redesign-guide.html` に C45〜C53 を足し「全53コマンド」にした。`help` の `canonical link` の Writes に refspec、`update-ref`、登録簿、定期の実行、基準を、`scope create`・`scope import github`・`work start`・`work finish` の Preconditions に schema 4 の文を足した（引数は変えていない）。
- **エラーの一覧**（R-436-04）：`canonical.md` の表は、runtime の canonical モードのコード（定数と、字面で書かれたもの）をすべて載せ、どの行にも次の1手がある。Epic `design.md` の12章の表を実装に合わせた（`CANONICAL_SAVE_UNCONFIRMED` は 3／6、`CANONICAL_PROGRESS_MARK_FAILED` の行、runtime にない `GITHUB_STRUCTURE_INVALID` を実装の構造の異常のコードの行に置き換え、`CANONICAL_NOT_IMPLEMENTED` は0.3.0では返さない）。
- **G7**（R-436-05）：`CANONICAL_NOT_IMPLEMENTED` の経路と定数を runtime から消した。53のコマンドすべてが版4で答える。
- **横断のシナリオ**（R-436-06）：2つのクローン（状態の置き場を別にした2台のPCの代わり）で、link → 日本語の題名で作成 → 編集 → 同じPCの別のworktreeから保存前に読める → sync → 別のクローンで読める → スナップショットの使い回し → `work start`（ブランチ名 `<ID>`）→ 編集 → `work finish`（push の後に閉じる）→ 元のクローンに届く、を systemd と loop の注入で通す。
- **引き継ぎの直し**（R-436-07）：`CLAUDE_CONFIG_DIR`（相対なら判定できない）、取り込み直しの途中の `resume --push-local` の拒否、`migrate.py undo` の作業の記録なしの停止（終了コード2）、undo の後の再 register のテスト。
- **版と配布資産**（R-436-08）：`pyproject.toml`、`uv.lock`、`spec-dock/system/spec-dock-version` を 0.3.0 にし、`static-inventory.json` の7資産の前の SHA-256 を `known_old_sha256` に足し、`canonical.md` を足した。この worktree の `spec-dock/` を候補の wheel の `installation update` で上げた（宣言は版3のまま）。
- **btrfs での選択の記録**（R-436-09。実機で見つけ、統括の判断 A で直した）：`infra/work_target_store.py` が使い回したディレクトリの記述子を2回列挙していたため、btrfs では `work start` が毎回 `partial`（`SELECTION_PUBLICATION_UNKNOWN`）になっていた。毎回新しい記述子で列挙するように直した。

### AC-15 の例外と変えたテスト

- 従来モードの処理と `.meta.json` の読み書きのコードは変えていない。例外は1つ：`infra/work_target_store.py`（従来モードの `work start` と共有）の列挙の直し（統括の判断 A）。振る舞いの契約は変えず、btrfs の上でだけ誤った `partial` が `succeeded` になる。ext4（GitHub Actions）と APFS（macOS）では出力は変わらない（下の 0.2.4 との比べで確かめた）。
- `git diff ea3d3c9ee -- tests/` で変えたテストの区分：
  - この Issue の新しいテスト：`tests/cli_runtime/test_issue436_end_to_end.py`、`test_issue436_every_command.py`、`tests/unit/infra/test_issue436_agent_rules.py`、`test_issue436_docs.py`。
  - 既存のファイルへの追加（canonical モードと移行のスクリプトと共有の infra。版3の既存のテストは変えていない）：`test_issue429_canonical_status.py`（`CLAUDE_CONFIG_DIR` の2つ）、`test_issue430_canonical_resume.py`（`--push-local` の拒否）、`tests/integration/migration/test_migrate_register.py`（undo の2つ）、`tests/unit/infra/test_work_target_store.py`（btrfs の再現）。
  - canonical モードの暫定の経路のテストの削除と書き換え（版3の振る舞いではない）：`test_issue428_canonical_mode.py`（`CANONICAL_NOT_IMPLEMENTED` を確かめていた2つ。1つは消し、1つは `CANONICAL_NOT_APPLICABLE` の文字の出力で確かめる形に）、`tests/unit/commands/test_canonical_dispatch.py`（同じく1つの部分）。
  - Epic の testability が許した変更：`tests/integration/test_issue413_assets.py`（資産の数 86→87、効果の数 87→88）、`tests/unit/infra/test_authoring_kit_assets.py`（入口の文書のリンクの許可リストに `canonical.md`）。
  - テストの部品：`tests/support/canonical_repo.py` の `isolate_user_state` が `CLAUDE_CONFIG_DIR` も消す（利用者の値がテストに入らないため）。

## Verification

- 文書のレビュー①（新しいサブエージェント、opus/high、汎用。最初に専用の `spec-reviewer` 型に頼んだが入力の形式で拒まれたので、同じ依頼を汎用で出し直した）：fail（P1 3、P2 10、P3 7）。`analyze-review-findings` で分析し、F13（`--offline` がない）は反証（`cli/options.py:49` の共通の引数、`canonical_scopes.py` が扱う）、ほかは根拠ありとして直した（`3ddcb17c4` と、その後の要件・設計の直し）。
- 全体のテスト（help の直しの前、`f336a8b8f` の前の作業ツリー）：`uv run pytest` 3289 passed、8 skipped、4 failed（資産の数と入口のリンクの許可リスト。直した）。最終の結果は下の「最終品質ゲート」。
- wheel：`uv build --wheel` → 一時の venv に `spec_dock-0.3.0-py3-none-any.whl`。`spec-dock --version` は `0.3.0`、`spec-dock help` と `spec-dock canonical --help` が動く。
- 利用側の更新：候補の console で `installation update --target <この worktree> --dry-run`（10資産の予定、blockers なし）→ `--backup-dir <一時> --yes`（created 4、changed 7）。`installation show` は88資産が `current`、`spec-dock/workspace.json` は `unknown`（0.2.4 でも同じ。dogfood の版3の宣言が配布物と違うバイト列であるため。宣言は版3のまま）。`spec-dock workspace validate` succeeded、`.github/scripts/specdock-ci-validate.sh <この worktree> <この worktree> 14a897e50…` は終了コード0（`workspace validate --ci` が valid、265 nodes）。手元の `~/.local/bin/python3`（uv の単体の Python）は venv を作れないので、スクリプトは `PATH=/opt/homebrew/bin:$PATH` で実行した（環境の事情で、この変更とは無関係）。
- 0.2.4 との比べ（AC-15）：`ea3d3c9ee` の `git archive` から作った 0.2.4 の wheel と 0.3.0 の候補を、版3の作り物（このリポジトリの `ea3d3c9ee` のクローン）で同じコマンドに当てた。`scope list`、`scope show iss-00436`、`scope show iss-436`、`dependency list`、`dependency check`、`workspace validate`、`workspace validate --ci`、`workspace doctor`、`active show`、`work start --dry-run`、`canonical status`、`scope move`、`scope create --dry-run`、`scope list --help` は同じバイト列。違ったのは `workspace sync`（`observed_at` の時刻だけ）、`installation show`（`package_version` と、新しい `canonical.md` と版のファイルの分類）、`work start --help`・`work finish --help`・`scope create issue --help`（足した文）だけで、どれも先に決めた許す差。
- 実機の確かめ（AC-436-10、Epic の AC-07、AC-14、AC-18）：
  - **macOS**（Darwin 27.2.0、git 2.54、候補の wheel の外の console、一時の `HOME`・`XDG_STATE_HOME`、PATH の偽の `gh`、bare の origin。GitHub の URL の形の origin は、`remote get-url` 以外の git の呼び出しだけを bare に向ける小さな git の差し替えで残した）：`--no-schedule` と手で回す同期で、AC-02 は33秒で別のクローンに見え、AC-13 の `work finish` は裏で回る同期を待って7秒で `completed` で閉じ、AC-03 は両方のクローンで先着の版と別名ファイル1つ、競合のマーカー0。
  - **Codex のサンドボックス（macOS、codex-cli 0.163.0、一時の `CODEX_HOME`、`codex sandbox -P :workspace`）**：作業用のworktreeで `canonical status` が `tools.codex.writable=false` と正確な `writable_roots = ["<カタログ>"]` の1行（`CANONICAL_TOOL_SETTING_MISSING`）を示し、カタログへの書き込みは拒まれた。その1行を一時の `config.toml` に書いても（`-c` の上書きでも）書き込みは拒まれたまま（I-2 と同じ。この版の `codex sandbox -P :workspace` は `writable_roots` を反映しない）。
  - **Claude Code の判定（SpecDock 側、外の console、一時の `CLAUDE_CONFIG_DIR`）**：設定なしで `configured=false`、場所は `$CLAUDE_CONFIG_DIR/settings.json`、正確な1行。示された1行をそのファイルに書くと `configured=true`。相対の `CLAUDE_CONFIG_DIR` は `CANONICAL_TOOL_SETTING_UNKNOWN`。
  - **OrbStack の仮想マシン `specdock-i436-noble`（Ubuntu 24.04 arm64、git 2.43.0、systemd のユーザー、linger=yes、ホームは btrfs）**：使い捨ての仮想マシンなので HOME はそのまま（systemd のユーザーのユニットのため）、状態の置き場は一時。OrbStack が仮想マシンの `~/.ssh` に置いた利用者の鍵へのリンクは、始める前に仮想マシンの中で消した。`canonical link` が systemd を選び、`~/.config/systemd/user/spec-dock-canonical-sync.{service,timer}` を置き、約65秒ごとに `canonical sync --registered` が動いた。AC-02 は、作成の直後の編集が1秒（作成の変更の束がディレクトリ全体をすぐ保存させるため）、既存のファイルの編集がタイマーだけで36秒。AC-13 の `work finish` は2秒で閉じた。AC-03 は別名ファイル1つ、マーカー0。ユニットには `KillMode` と `TimeoutStopSec` がなく既定（control-group、90秒）。1周期は1秒未満で、変える提案はしない。
  - **Linux の Codex のサンドボックス（同じ仮想マシン、npm の codex-cli 0.166.0、ログインなし、Landlock）**：カタログへの書き込みは拒まれ（Read-only file system）、カタログのディレクトリへの `flock` は取れた（Epic の「未確認の事項」の Landlock の中の `flock` を確かめた）。
  - **Docker（python:3.12-slim、git 2.47.3、systemd なし、中でクローン）**：`canonical link` が常駐のプロセスを選び（`CANONICAL_RUNNER_RESTART` と起動し直しの1行）、AC-02 は作成の直後2秒、編集は常駐のプロセスだけで60秒、AC-13 は3秒、AC-03 は別名ファイル1つ、マーカー0。`docker restart` の後は常駐のプロセスがなく、`canonical status` が `CANONICAL_RUNNER_STOPPED`、`canonical link` で戻った。
  - **マウントしたチェックアウト**（macOS の一時のクローンをコンテナにマウント）：`canonical link` が終了コード3の `CANONICAL_FOREIGN_CHECKOUT`、効果なし、次の1手付きで止まり、ホストの `.git/worktrees` のダイジェストは変わらなかった。
  - **Git 2.38.0 ちょうど**（kernel.org の 2.38.0 をコンテナの中でソースから作った）：link、作成、同期、AC-02（32秒）、AC-13（6秒）、AC-03 が通った。
  - **btrfs の不具合の Red**：`tests/unit/infra/test_work_target_store.py` の `test_publish_confirms_its_record_where_a_drained_directory_stream_hides_new_entries` は、直しの前（保持した記述子に `os.listdir` を2回呼ぶコード）に `SelectionPublicationUnknown: published work target is not the sole valid selection` で落ち、直しの後に通った（`b1629847f` に同じコミットで入れたが、実行は直しの前に行った）。
  - **btrfs の不具合**：仮想マシンとそのコンテナで `work start` が `partial`（`SELECTION_PUBLICATION_UNKNOWN`）になり、最小の再現（btrfs では読み切った記述子の2回目の `listdir` が `[]`、tmpfs では `['x']`）で原因を特定した。直した wheel で、同じ仮想マシンで `succeeded`（終了コード0）を確かめた。
  - 片付け：仮想マシンは `orb delete -f` で消した。コンテナ4つ（`specdock-i436-loop`、`-mount`、`-git238`×2）は `docker rm -f` で消し、取得したイメージ（`python:3.12-slim`、`alpine:3.17`。どちらも始める前にはなかった）は `docker rmi` で消した。手元の CI の Lima の仮想マシン、`ci-shadow`、利用者のコンテナには触れていない。利用者の `gh` の資格情報は、どの仮想マシンとコンテナにも入れていない。
- **白紙のエージェントの試行**（AC-14。この会話を知らない新しいサブエージェント、sonnet/medium、規則の節だけを渡し、macOS の一時の世界で実行）：(1) `spec-dock scope show iss-3 --json` で場所を確かめて `design.md` に追記、(2) `rg -l "B finished" spec-dock/initiatives/` でパスを明示して検索、(3) 別名ファイルの中身を `report.md` に統合して別名ファイルを `rm`、(4) 親を `scope show --json` の `parent_id`（`epic-00002`）で確かめた、(5) 終わりは `spec-dock work finish`（最大180秒待ち、止まったら `canonical status`）と答えた。Git の操作もディレクトリの名前の変更もしなかった。合格。エージェントが分からなかったと挙げた点：`work finish` に Scope の引数が要るか（`--help` を見ていない）、別名ファイルの統合の形の決まり。最初の起動は、規則の本文を埋め込み忘れたので、何も書く前に止めて起動し直した。

### 実装のレビュー②（`code-review`、範囲 `ea3d3c9ee..b9ea415bd`）

- Standards（新しいサブエージェント、opus/high）：pass。P3 が1件（ST：取り込み直しの途中の `remote_deleted` で、引数なしと `--adopt-remote` の `resume` が、拒まれる `--push-local` を案内する）。
- Spec（新しいサブエージェント、opus/high）：pass。P2 が1件（上と同じ指摘）、P3 が1件（AC-436-11 が計画の完了条件になく、Red の証拠が報告書にない）。
- 対応：`analyze-review-findings` で、どれも根拠ありと判断して直した。`resume` は、取り込み直しの途中で案内が `--push-local` になる経路でも、同じ拒否の案内（`--adopt-remote`、作り直すかは利用者に確かめる）を返す（`_refusal`。テストに引数なしと `--adopt-remote` の確かめを足した）。計画の目標と完了条件を AC-436-01〜11 にし、上に Red の記録を足した。

### 最終品質ゲート

（下に記録する）

## Residual Risks / Follow-ups

- **未確認**：Codex の `writable_roots` の1行が本物の Codex のセッションで効くこと（この版の `codex sandbox -P :workspace` は反映しない。Codex の設定の形が権限のプロファイルに移っている可能性。I-10 で利用者の設定で確かめる）。Claude Code 自身が、ユーザーの設定ファイルの1行で作業用のworktreeからカタログに書けること（利用者の設定か資格情報が要る。I-10）。本物の GitHub への push の認証（定期の実行からのものを含む。I-10）。systemd の止め方の設定が要るか（周期の途中で止める実測はしていない）。
- **統括に判断してほしいこと**：
  - Linux の Codex のサンドボックスは `CODEX_SANDBOX` を設定しない（`CODEX_SANDBOX_NETWORK_DISABLED=1` だけ。macOS は `CODEX_SANDBOX=seatbelt`）。そのため Linux の Codex の中では、`canonical status` が Codex の1行ではなく汎用の `access` の案内（「カタログの権限を確かめる」）を示す。Epic の9章の判定の前提に関わるので、この Issue では変えていない。
  - Epic の `design.md` の9章は、Claude Code のユーザーの設定を `~/.claude/settings.json` と固定で書いている。実装は `CLAUDE_CONFIG_DIR` を見るようにした（I-2 の ST-12）。9章の直しを提案する。
  - Alpine（musl）では、書くコマンドが `LOCAL_IO_FAILED`「safe JSON rename is unavailable」（`recovery` なし）で止まる（no-replace の rename がない）。対応の OS の範囲の判断が要る（この Issue の範囲外）。
- **残るリスク**：従来モードと共有の汎用のコード（`PRECONDITION_FAILED`、`SCOPE_NOT_FOUND`、`WORK_START_REQUIRED`、`LOCAL_IO_FAILED` など）には `recovery` のないものがある（版3の出力を変えないため。撤去の後に見直す）。
- **マージの後に統括が確かめること**：`release-tag.yml` が `v0.3.0` のタグを作ったこと（この Issue ではタグを作っていない）。結果は Epic の `report.md` か I-10 の報告書に書く。
- **I-10 への申し送り**：0.3.0 の wheel を利用者の環境に入れる。`canonical.md` の「ツールの設定」の1行を、利用者が本物の設定に足して確かめる。
