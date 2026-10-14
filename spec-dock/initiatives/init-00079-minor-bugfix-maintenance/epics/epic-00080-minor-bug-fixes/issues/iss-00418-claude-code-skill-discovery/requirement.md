---
種別: 要件定義書（Issue）
ID: "iss-00418"
タイトル: "Fix Claude Code discovery of installed SpecDock skills"
関連GitHub: ["#418"]
状態: "draft"
最終更新: "2026-10-14"
親: ["epic-00080", "init-00079"]
---

# iss-00418 Fix Claude Code discovery of installed SpecDock skills — 要件定義

詳細: [Requirement Guide](../../../../../../docs/authoring/requirement.md)

## 目的
SpecDock を導入した worktree で、Codex と Claude Code の両方が、同梱スキル `spec-dock`・`spec-dock-grill-with-docs` を各ホストのプロジェクト探索先から発見・利用できるようにする。

## 背景
- 現行の `installation init/update` は、2つのスキルを対象 worktree の `.agents/skills/<name>/` にだけ配置する。インベントリ（`src/spec_dock/assets/static-inventory.json`）と配置先 allowlist（`src/spec_dock/runtime/infra/static_assets.py`）も、スキルの配置先を `.agents/skills/spec-dock*` に限定している。
- 2026-10-14 に公式文書で確認した各ホストの探索先は次のとおり（調査 Artifact `20261014t071357z-research`）。
  - Codex: cwd から repository root までの各 `.agents/skills`、`$HOME/.agents/skills` など。`.claude/skills` は読まない。
  - Claude Code: project の `.claude/skills`（起動ディレクトリから repository root まで。linked worktree では worktree root で停止）、`~/.claude/skills`、プラグイン、`--add-dir` 内の `.claude/skills`。`.agents/skills` は読まない。
- そのため、Claude Code からは SpecDock のスキルが見えない。この dogfooding repo の Claude Code セッションでも、2つのスキルはスキル一覧に現れない。
- grill スキルは helper を `python3 .agents/skills/spec-dock-grill-with-docs/scripts/finalize-artifact.py` という固定パスで呼ぶ。preflight 8 は、Codex 用の `agents/openai.yaml` があることを全ホスト共通の前提として要求している。そのため、`.claude/skills` から読み込まれた場合の手順として正しくない。
- epic-00074 E-RQ-003（host 固有ディレクトリへ重複配置しない）と accepted ADR `20260831t005139z-adr` Decision 6（managed skill を `.agents/skills` の2 slot に限定する）が、現在の配置を定めている。本 Issue はこれらを新しい ADR `20261014t072234z-adr` で部分的に改訂し、Claude Code を対象に加える。

## 観測可能な要件
- RQ-418-01: `installation init` は、`.agents/skills/<name>/` と `.claude/skills/<name>/` の両方に、同梱スキルのファイルを通常ファイルとして作成する（各4ファイル、計8ファイル）。対応するファイルは、互いに、また provider の正本とバイト一致する。
- RQ-418-02: `.agents` 側だけを持つ既存の consumer は、通常の `installation update` で `.claude` 側を受け取る（`installation.create`）。同じ操作で、既知の旧版の `.agents` 側は現行版へ更新される。dry-run は何も変更せず、適用後の再実行は `unchanged` になる。
- RQ-418-03: `installation show` は、`.claude` 側の管理ファイルも、既存と同じ分類（`missing`・`current`・`known-old`・`unknown`・`unsafe`）で表示する。
- RQ-418-04: init / update / uninstall は、`.claude/` 配下のうち、管理対象の2 slot にあるインベントリのファイル以外を変更・削除しない（`.claude/settings.json`、`.claude/settings.local.json`、他のスキル、slot 内の未知のファイルなど）。
- RQ-418-05: uninstall は、両方の投影から、検証済みの管理ファイルだけを削除する。`.claude/`、`.claude/skills/`、slot ディレクトリ、未知のファイルは残す。
- RQ-418-06: スキル本文はホスト中立で、両方の投影で同一である。具体的には次を満たす。
  - grill の helper は、読み込まれたスキルディレクトリを基準に解決する。`.agents/...` の固定パスを使わない。
  - preflight は `agents/openai.yaml` を全ホスト共通の実行前提にしない。`agents/openai.yaml` は Codex 用の起動制御として引き続き同梱する。
  - `spec-dock` スキルは、静的投影として `.agents/skills` と `.claude/skills` の両方を説明する。
  - Codex 固有の言い回し（「running Codex processes」、保護対象としての `.codex/config.toml` だけの列挙）を一般化する。
- RQ-418-07: wheel は、必要な source と更新済みのインベントリを含む。fresh wheel を非 editable で導入した CLI でも、RQ-418-01 と RQ-418-02 が成り立つ。
- RQ-418-08（範囲に含めるかはユーザー判断）: `installation show` は、管理ファイルが存在しない場合も、先に親チェーンを検査する。symlink や非ディレクトリの親の下にある欠落ファイルは、`missing` ではなく `unsafe` と表示する。update 側の既存の挙動（`verify_existing_parent()` による事前検査）とそろえる。
- RQ-418-09（範囲に含めるかはユーザー判断）: この dogfooding repo の `.claude/skills` を、候補 wheel の CLI による正規の `installation update` で作成し、コミットする。

## スコープ
- 対象:
  - インベントリと配置先 allowlist
  - 同梱スキルの本文（provider 正本）
  - 配布の説明文書（`README.md`、`src/spec_dock/assets/spec_dock/docs/authoring/overview.md`、`AGENTS.md`）
  - 回帰テスト
  - 新しい ADR
  - RQ-418-08・RQ-418-09 は承認された場合のみ
- 対象外:
  - `$HOME` への書き込み（`~/.claude/skills`、`~/.agents/skills`）
  - プラグインや marketplace による配布
  - symlink による投影
  - ホスト検出による配布先の切り替え
  - Claude Code・Codex の設定ファイルの編集
  - `grilling`・`domain-modeling` の自動導入や同梱
  - 業務コマンドの Windows 対応
  - `.gitattributes` などリポジトリ全体の設定変更
  - ユーザーがインストール済みの `spec-dock` パッケージの更新
  - 他の worktree（main checkout や linked peer）の静的資産の更新
- 維持する親契約（Issue 413、AC-413-37）:
  - 明示した1つの worktree だけを変更する。
  - 既知の静的資産だけを扱う。
  - fail-closed で停止する。
  - update で変更がある場合は `--backup-dir ABS` と `--yes` を要求する。
  - journal と自動 rollback を持たない。
  - 人間による PR マージゲートを維持する。

## 失敗・境界条件
- `.claude/` や `.claude/skills/` が通常のディレクトリとして既にある場合は、共有の親として使う。中身を所有しない。
- 管理対象のパスに既にファイルがある場合:
  - init は、内容が同じでも、既存の配置先として拒否する。
  - update は、現行版なら受け入れ、既知の旧版ならバックアップ後に更新し、未知の内容なら事前検査で停止して手動マージを求める。
- `.claude`、`.claude/skills`、slot、管理ファイルが symlink・dangling symlink・hard link・特殊ファイルの場合は拒否する。正しい相対リンクでも自動では変換しない。
- 同じパスに同じバイト列があると、利用者の手動コピーか配布物かを区別できない。update で current として受け入れたファイルは、uninstall で削除対象になる。この限界を文書に明記する。
- update はファイルごとの順次公開である。途中で失敗すると、片方の投影だけが新しくなり得る。既存の partial 報告で、成功・未実行・不確実な効果を示す。
- 次のホスト側の挙動は、インストーラでは保証できない。
  - Claude Code は同名の personal スキルを project より優先する。
  - v2.1.277 以降の linked worktree は、ルートに `.claude/skills` がなければ main checkout のスキルを読む。
  - Desktop app から開始した worktree セッションは、main checkout の設定を読む。

  uninstall の保証は、対象 worktree の管理ファイルの除去までとする。

## 受け入れ条件
- AC-418-01: fresh init で `.agents/skills/<name>/**` と `.claude/skills/<name>/**` の計8ファイルが作られる。対応するファイルは、互いに、また provider 正本とバイト一致する。各ファイルは通常ファイルで、自分自身と親チェーンに symlink がない。
- AC-418-02: 0.2.4 相当の consumer（`.agents` 側が旧版で、`.claude` 側がない）に `installation update --backup-dir ABS --yes` を実行すると、次のようになる。
  - `.claude` 側の4ファイルが `installation.create` として作られる。
  - 旧版の `.agents` 側の SKILL.md は現行版に更新され、バックアップに旧版が保存される。
  - dry-run は何も変更しない。適用後の再実行は `unchanged` になる。
- AC-418-03: init / update / uninstall の前後で、次の利用者ファイルがバイト一致で保持される: `.claude/settings.json`、`.claude/settings.local.json`、`.claude/skills/<他のスキル>/SKILL.md`、slot 内の未知のファイル。また、次の場合は効果0で停止する。
  - 管理対象の `.claude` 側ファイルが未知の内容のとき、update は停止する。
  - `.claude` が symlink のとき、init と update は停止する。
- AC-418-04: uninstall は8つのスキルファイルを削除する。`.claude/`、`.claude/skills/`、未知のファイルは残る。
- AC-418-05: provider の SKILL.md について、次を満たす。
  - grill の helper の固定パス `.agents/skills/spec-dock-grill-with-docs/scripts/` がない。
  - preflight が `agents/openai.yaml` を前提にしない。
  - `agents/openai.yaml`（`allow_implicit_invocation: false`）と、frontmatter の `disable-model-invocation: true` が維持されている。
  - `spec-dock` スキルが `.claude/skills` を説明している。
- AC-418-06: 次がすべて通る。
  - `uv run pytest`
  - `make lint`
  - fresh wheel を隔離環境に導入した CLI での init・update の確認
  - `spec-dock workspace validate` の findings が0件
- AC-418-07: 候補 wheel で init した一時リポジトリで、Claude Code の新しいセッション（`claude -p`）のスキル一覧に `spec-dock` が現れる。実行できなかった場合は、その旨と理由を Report に記録する。
- AC-418-08（RQ-418-08 を含める場合）: `.claude` が symlink の worktree で、`installation show` が `.claude` 側の管理ファイルを `unsafe` と表示する。
- AC-418-09（RQ-418-09 を含める場合）: この worktree で、候補 CLI による `installation show` が両方の投影の8ファイルを `current` と表示する。`.claude/skills` は Git で追跡され、`.agents/skills` とバイト一致する。

## 制約・前提
- Codex・Claude Code の探索仕様は、2026-10-14 時点の公式文書に基づく。これが変わった場合は、ADR の見直し条件に従って再評価する。
- この Issue でそろえるのは静的配布物の版である。PATH 上の外部 CLI の版はそろえない。CLI を使う前に root と leaf の help を確認する既存の規約は維持する。
- 両方の投影は同じバイト列にする。`known_old_sha256` は配置先ごとの配布履歴であり、新設の `.claude` 側は空から始める。
- ユーザーのインストール済みパッケージ、`~/.claude/**`、`~/.agents/**` は変更しない。
