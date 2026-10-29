---
種別: 実装計画書（Issue）
ID: "iss-00436"
タイトル: "Integrate Agent Rules Docs And Release"
関連GitHub: ["#436"]
状態: "approved"
最終更新: "2026-10-30"
依存: ["requirement.md", "design.md"]
親: ["epic-00424", "init-00423"]
---

# iss-00436 Integrate Agent Rules Docs And Release — 実装計画

詳細: [Issue Plan Guide](../../../../../../docs/authoring/issue-plan.md)

## Planning Level

- standard（Epic の `plan.md` の一覧）。理由：文書とテストの追加が中心で、runtime の変更は小さな直し（4つ）と、未実装の経路の削除だけである。利用者の仕様のファイルを書く処理と、GitHub への書き込みの順は変えない。
- risk factor：配布資産の版の更新（全リポジトリの `installation update` に効く）、従来モードの回帰（AC-15）、実機の確かめで手元の CI の仮想マシンとメモリを共有すること。
- 再評価の条件：12章の表と実装の突き合わせで、表の直しでは済まない食い違い（実装の振る舞いを変える必要）が見つかったとき、または C1〜C11 の公開の形を変える必要が出たときは、止まって統括に聞く。

## 目標

- `requirement.md` の AC-436-01〜10 を満たし、0.3.0 の PR をマージできる状態にする。
- モデルと推論：実装は opus/medium（統括の指定）。独立のレビューのサブエージェントは opus/high、白紙のエージェントの試行は sonnet/medium（統括の指定）。

## 順序・依存

1. S1 文書の具体化とレビュー（この文書）。
2. S2〜S5 は互いに独立で、どの順でもよい。S6 は S2〜S5 の後（配布資産の中身が決まってから SHA-256 を更新する）。S7 は S6 の wheel を使う。S8 は全体の後。

## 実装step

- **S1**：要件・設計・計画を書き、独立のレビュー①（文書）を受けて直す。コミット。
- **S2 引き継ぎの直し（TDD）**：
  1. `migrate.py undo` の記録なしの停止（Red：記録のない `undo` と `undo --apply` が2で止まるテスト → Green）。
  2. undo の後の再 register のテスト（いまのコードで Green になるはずのテスト。Red にならなければ、取り消した作成を使い直す形に一時的に壊して落ちることを確かめてから戻す）。
  3. `resume --push-local` の拒否（Red → Green）。
  4. `CLAUDE_CONFIG_DIR`（Red → Green）。
- **S3 G7**：表のテストと53のコマンドの実行のテストを書き（Red にはならない見込み。`CANONICAL_NOT_IMPLEMENTED` の経路を消す前後で通ることを確かめる）、経路と定数を消す。
- **S4 横断のシナリオ**：`test_issue436_end_to_end.py` を systemd と loop のパラメーターで書く。落ちたら原因を調べ、runtime の不具合なら持ち主の Issue の設計に従って直す（直す範囲が設計にないなら統括に聞く）。
- **S5 文書**：規則の節（スキル、`AGENTS.md`）、`canonical.md`、4つの文書と `README.md`、`reference_cli.md`、HTML、`help` の文、`migrate` の README、Epic の12章の表。文書のテスト（`test_issue436_agent_rules.py`、`test_issue436_docs.py`）を先に書いて Red にしてから文書を書く。
- レビューの直しで配布資産の中身が変わったら、S6（SHA-256 の更新）と S7（利用側の更新）をやり直す。テストの差分の基点は `ea3d3c9ee` に固定する。
- **S6 版と配布資産**：0.3.0、`static-inventory.json` の `sha256` と `known_old_sha256`。`uv run pytest tests/unit/infra` で資産のテストを確かめる。
- **S7 外の環境と利用側**：wheel を作り、一時の環境で `--version`、`help`、`canonical --help`。その console で、この worktree の `spec-dock/` を `installation update` する（dry-run の分類を先に見る）。`installation show`、`workspace validate`、`.github/scripts/specdock-ci-validate.sh`。利用側の変更をコミット。
- **S8 実機の確かめ**：macOS（外の console の `work finish`、Codex のサンドボックス、Claude Code の一時の設定）、OrbStack の仮想マシン（systemd）、Docker のコンテナ（loop、マウント、Alpine の git 2.38）。1台ずつ動かし、消す。白紙のエージェントの試行（AC-14）。結果を `report.md` に書く。
- **S9 独立レビュー②（実装）**：`code-review` スキルで Standards と Spec の2つのサブエージェント。指摘を分析して直す。
- **S10 最終品質ゲート**：push、固定した SHA で `make lint` と `uv run pytest`、`origin/main...HEAD` の全差分を新しい2つのサブエージェントでレビュー。指摘を直したら新しい SHA でやり直す（2回目以降のレビューは差分と前の指摘の確かめに絞る）。
- **S11 PR**：`github-pr-creator` で PR（`Refs #436`）、`github-pr-checks` で CI を確かめる。`work finish` はしない。

## 検証

- 毎回：`make lint`、`uv run pytest`（全体）。
- AC ごとの確かめは `design.md` の testability の表のとおり。
- AC-15：`git diff --name-only origin/main -- tests/` の各ファイルが、この Issue の新しいテストか、Epic の testability の許された変更（コマンドの数と一覧、配布資産の一覧と値、文書の中身、版の値）に当たることを確かめ、報告書に一覧で書く。
- 実機：報告書に、環境（OS、版、git の版）、手順、結果、確かめられなかったこと（「未確認」）を書く。

## rollback

- PR のマージの前：PR を閉じる。利用側の `spec-dock/` の更新は、この worktree のコミットにだけある。
- マージの後：PR を `git revert` する。版のタグ `v0.3.0` は残るので、作り直しの要否は統括が判断する。

## security / privacy / operability

- 資格情報：仮想マシンとコンテナと実機の確かめに、利用者の `gh` の資格情報を写さない。偽の `gh` だけを使う。
- 利用者の環境：`~/.claude/settings.json`、`~/.codex/config.toml`、`~/Library/LaunchAgents/`、`~/.local/state/spec-dock/` を変えない。確かめは一時の `HOME`、`CLAUDE_CONFIG_DIR`、`CODEX_HOME`、`XDG_STATE_HOME` で行う。
- データの移行：なし（N/A）。利用側の配布資産の更新は `installation update` のバックアップを一時ディレクトリに置く。

## residual risk

- 従来モードと共有の汎用のコードには `recovery` がないものが残る（版3の出力を変えないため。撤去の後に見直す）。
- 実機で確かめられないもの（Claude Code のユーザーの設定ファイルでの動き、資格情報の要る GitHub への push）は I-10 に残る。

## exit / handoff

- 完了：AC-436-01〜10 を満たし、最終品質ゲートが同じ SHA で合格し、PR の CI が通り、マージできる状態。`work finish` は統括の指示の後。
- 統括に渡すこと：PR の URL、最終の SHA、ゲートの結果、`report.md` のパス、未確認の事項、I-10 への申し送り、Epic の9章（`CLAUDE_CONFIG_DIR`）の直しの提案。マージの後の `release-tag.yml` の `v0.3.0` の確かめは、この Issue の `report.md` に「マージの後に統括が確かめる」と書き、統括が確かめて Epic の `report.md`（か I-10 の報告書）に結果を書く。
