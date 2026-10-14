---
種別: レポート（Issue）
ID: "iss-00418"
タイトル: "Fix Claude Code discovery of installed SpecDock skills"
関連GitHub: ["#418"]
最終更新: "2026-10-14"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00080", "init-00079"]
---

# Result Summary

詳細: [Report Guide](../../../../../../docs/authoring/report.md)

## Outcome

- accepted ADR `20261014t072234z-adr` に従い、単一の provider 正本（`src/spec_dock/assets/install_root/.agents/skills/`）から、`.agents/skills/<name>/` と `.claude/skills/<name>/` の両方へ、同じバイト列の通常ファイルを投影するようにした。
  - インベントリに `.claude` 側の4エントリを追加した。source・sha256・mode・init_only は `.agents` 側と同じで、`known_old_sha256` は空から始めた。
  - allowlist には `.claude/skills/spec-dock/` と `.claude/skills/spec-dock-grill-with-docs/` の2つだけを追加した。
  - init / update / uninstall の処理本体は変更していない。
- SKILL.md をホスト中立にした。
  - grill の helper は、ホストが読み込んだスキルディレクトリ（`<skill-dir>`）を基準に解決する。
  - preflight は `agents/openai.yaml` を前提にしない。
  - `spec-dock` スキルは両方の投影を説明する。
  - 0.2.4 の SKILL.md 2つと `overview.md` のハッシュを、`.agents` 側の既知の旧版に登録した。
- `installation show` は、ファイルの有無を判定する前に親チェーンを検査する。`.claude` が symlink や通常ファイルの場合は、`unsafe` と表示する（RQ-418-08）。
- 次の文書に、`.claude/skills` への投影、管理の範囲、同一バイト列のコピーの扱いを記載した: `README.md`、`AGENTS.md`、`src/spec_dock/assets/spec_dock/docs/authoring/overview.md`。
- dogfood（RQ-418-09）: 候補 wheel の CLI で、このワークツリーだけに `installation update` を実行した。
  - `.claude/skills` の4ファイルを作成した。
  - `.agents` 側の SKILL.md 2つと `spec-dock/docs/authoring/overview.md` を更新した。
  - ユーザーのインストール済みパッケージ、main checkout、他の linked worktree は変更していない。
- CI 安定化（範囲外。2026-10-14 にユーザーの承認を得てこの PR に含めた）:
  - PR #419 の最初の CI（run 38531598095）で、`test_ci_fixed_validation.py::test_ci_validator_stops_on_failed_wheel_build_without_touching_target` が失敗した。source fixture の commit 後に起動した Git の自動メンテナンス（`git maintenance run --auto --detach`）が repack を行い、テストの前後比較と競合したためである。
  - `802fdcc6` と同じ方針で、`_source_checkout` の最初の commit より前に `maintenance.auto=false` を設定した。Trace2 で自動メンテナンスが起動しないことを確認する回帰テストを、Red → Green で追加した。

## Verification

- テスト先行で進めた（Red → Green）。次のテストは、失敗を確認してから実装した。
  - provider と fresh consumer の `.claude/skills` の一致
  - スキル本文の中立性
  - 0.2.4 相当の consumer からの update（旧版ハッシュの未登録で停止 → 登録後に成功）
  - `show` の欠落時の `unsafe` 分類
  - 文書の資産テスト
- 次のテストは、既存の実装で成り立つ境界を固定するガードとして追加した。
  - allowlist 外の `.claude` の拒否。allowlist を `.claude/` に広げる変更で失敗することを確認した。
  - init での利用者の `.claude` ファイルの保持
  - symlink の `.claude` の拒否（init / update / uninstall）
  - `.claude` 側の未知の改変・hard link・symlink の拒否
  - 部分失敗の後、新しい update で収束すること
  - uninstall の件数（88）と、共有ディレクトリ・利用者ファイルの保持
- `uv run pytest`: 1941 passed, 1 skipped（commit `7b930e0e`）。dogfood 更新後に `uv run pytest tests/unit/infra`: 401 passed, 1 skipped。
- `make lint`: ruff check、ruff format、mypy とも pass。
- fresh wheel（`7b930e0e` を `git archive` で展開してビルドし、`/private/tmp` の venv に非 editable で導入）:
  - init で8ファイルが作られ、provider とバイト一致する（symlink なし、`st_nlink == 1`）。`show` は8ファイルとも current。`workspace validate` の findings は0件。
  - ベースコミット `0e7dc868` の wheel で init した consumer（`.claude/settings.json` だけを追加）に update を実行した。
    - dry-run は無変更だった。
    - 適用すると、`.agents` の SKILL.md 2つと `overview.md` が変更され、`.claude` の4ファイルが作成された。バックアップは、変更した3ファイルの旧版だけだった。
    - 利用者の settings は保持された。再実行は unchanged だった。
- Claude Code 2.1.299 の実機確認（`claude -p`、plan mode、書き込みツールを無効化、セッションを保存しない設定）:
  - 0.2.4 で init した一時リポジトリでは、起動時イベントのスキル一覧（75件）に `spec-dock` がなかった（バグの再現）。
  - 候補 wheel で init した一時リポジトリでは、スキル一覧（77件）とスラッシュコマンドに `spec-dock`・`spec-dock-grill-with-docs` の両方が現れた。
  - `spec-dock` を起動させると、`Base directory for this skill: <repo>/.claude/skills/spec-dock` が報告され、プロジェクトの投影から読み込まれたことを確認した。personal の同名スキルは存在しない。
  - モデルの回答には grill が出なかった。`disable-model-invocation: true` で説明文が文脈に載らないためと考えられ、想定どおりである。
- dogfood:
  - 候補 CLI の `installation show` で、8つのスキルファイルがすべて current だった。`unknown` の1件は、init_only の `spec-dock/workspace.json`（既存の差異）である。
  - `diff -r .agents/skills .claude/skills` と、provider との比較で、差異はなかった。
  - `spec-dock workspace validate` の findings は0件だった（インストール済み CLI・候補 CLI の両方）。
  - バックアップは `/private/tmp/spec-dock-iss418-dogfood-backup` に残している。

## Residual Risks / Follow-ups

- **ホスト側の挙動**: Claude Code は同名の personal スキルを優先する。また、`.claude/skills` を持たない linked worktree は main checkout のスキルを読み、Desktop app の worktree セッションは main checkout の設定を読む。そのため、`show` が current でも、実際のセッションが別の版を選ぶ可能性は残る。
- **他の worktree**: このリポジトリの main checkout と他の linked worktree の dogfood は未更新である。マージ後に、各 worktree で明示的に update する。
- **所有権の限界**: 同じパスに同じバイト列があると、利用者のコピーか配布物かを区別できず、uninstall で削除対象になる（文書に明記した）。
- **改行変換**: Git の改行変換（`core.autocrlf` など）による不一致は、既存の `unknown` 分類と手動マージで扱う。`.gitattributes` は変更していない。
- **既存の差異（本 Issue の範囲外）**: インストール済みの 0.2.4 パッケージは、main より新しい `spec-dock/docs/reference_cli.md`（sha256 `637bb1a1…`）を含む。そのため、インストール済みの CLI で init した consumer では、このブランチの CLI が同ファイルを `unknown` と判定する。
- **撤退**: Claude Code が `.agents/skills` を読むようになった場合は、ADR の撤退手順（retired inventory への移動と、retired allowlist の固定 slot への拡張）で `.claude` 投影を退役させる。
- **残るゲート**: 人間による PR のマージ。マージ後の `work finish`（Issue のクローズ）は別の操作である。
