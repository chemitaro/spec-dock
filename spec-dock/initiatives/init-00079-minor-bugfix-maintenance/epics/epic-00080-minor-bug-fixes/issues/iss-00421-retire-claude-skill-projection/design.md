---
種別: 設計書（Issue）
ID: "iss-00421"
タイトル: "Retire the Claude Code skill projection"
関連GitHub: ["#421"]
状態: "draft"
最終更新: "2026-10-22"
依存: ["requirement.md"]
親: ["epic-00080", "init-00079"]
---

# iss-00421 Retire the Claude Code skill projection — 設計

詳細: [Design Guide](../../../../../../docs/authoring/design.md)

## 設計目標
- accepted ADR `20261022t104008z-adr` に従い、`.claude` 側の投影を既存の retired inventory の仕組みで退役させる。
- 新しい資産型やリンクの管理は加えない。追加する分岐は「リンク経由の退役 slot を管理外とする」1つだけにする。

## Current / Target
- Current:
  - current inventory に `.claude/skills/` 配下の4エントリがあり、allowlist も `.claude` の2 slot を許可する。
  - retired allowlist は `spec-dock/spec-dock.version` と `spec-dock/scripts/spec_dock_runtime/**.py` だけを許可する。
  - update / uninstall は、各エントリの親チェーンに symlink があると停止する。
- Target:
  - current inventory と allowlist から `.claude` を外す。init / show は `.claude` を見なくなる。
  - retired inventory に `.claude` 側の4エントリを加え、retired allowlist を `.claude/skills/spec-dock/` と `.claude/skills/spec-dock-grill-with-docs/` に限って拡張する。
  - update / uninstall は、退役 slot のパス（`.claude`、`.claude/skills`、`.claude/skills/<slot>`）にリンクがあれば、その slot の退役エントリを入力から外す。

## 責務・Interface
- `static-inventory.json`:
  - `files` から `.claude` の4エントリを削除する。
  - `retired` に4エントリを追加する。`known_old_sha256` は、そのパスが current inventory に記録されたことのあるハッシュ（git 履歴で確認）とする。`source_basis` は `4d25a8b4`（退役直前の main）と provider の source パスとする。
  - `spec-dock` SKILL.md と `overview.md` の本文を変えるので、`.agents/skills/spec-dock/SKILL.md` と `spec-dock/docs/authoring/overview.md` の sha256 を更新し、直前のハッシュを `known_old_sha256` に追加する。
- `static_assets.py`:
  - `package_static_assets()` の allowlist から `.claude/skills/...` を外す。
  - `package_retired_assets()` の allowlist に、`.claude` の2 slot の前方一致を加える。`.claude/**` や `.claude/skills/**` 全体は許可しない。
- `asset_layout.py`: `SKILL_ROOTS = (".agents/skills",)` に戻す。
- `direct_static_update.py`:
  - 退役エントリのループで、`_linked_host_slot(root, path)` が真ならそのエントリを飛ばす。`inputs` にも入れないので、`verify()` もリンクを見ない。
  - `_linked_host_slot` は、パスが `.claude/skills/<slot>/` 配下のときだけ、`.claude` → `.claude/skills` → `.claude/skills/<slot>` の順に `is_symlink()` を見る。存在しない段や、ディレクトリでない段で打ち切って偽を返す（通常ファイルの `.claude` は、続く `verify_existing_parent` が従来どおり拒否する）。
  - 実体の slot 内のファイル単位の symlink、hard link、未知の内容は、既存の `_read_static_file` とハッシュ照合で停止する。
- 文書: `AGENTS.md`、`README.md`、同梱 `spec-dock` SKILL.md、`overview.md` を、`.agents/skills` だけの配置と Claude Code 側の相対リンクの説明に直す。

## data / failure
- 退役エントリと登録するハッシュ:

  | path | known_old_sha256 |
  |---|---|
  | `.claude/skills/spec-dock-grill-with-docs/SKILL.md` | `acb7e66a…` |
  | `.claude/skills/spec-dock-grill-with-docs/agents/openai.yaml` | `a1499d95…` |
  | `.claude/skills/spec-dock-grill-with-docs/scripts/finalize-artifact.py` | `105f1da7…` |
  | `.claude/skills/spec-dock/SKILL.md` | `4d8befe3…`、`f8086263…` |

- 各状態での振る舞い:

  | `.claude` 側の状態 | init | show | update | uninstall |
  |---|---|---|---|---|
  | ない | 何も作らない | 表示しない | 何もしない | 何もしない |
  | 既知のコピー | 触れない | 表示しない | バックアップして除去 | バックアップして除去 |
  | 未知の内容 | 触れない | 表示しない | 停止（手動マージ） | 停止（手動マージ） |
  | slot・親がリンク | 触れない | 表示しない | 飛ばす | 飛ばす |
  | 通常ファイルの `.claude`、slot 内の symlink・hard link | 触れない | 表示しない | 停止 | 停止 |

- 除去後の空ディレクトリは残す。リンク先が `.agents` 側でも外部でも、リンク先を読まない。

## 変更対象
- 変更する: `src/spec_dock/assets/static-inventory.json`、`src/spec_dock/runtime/infra/static_assets.py`、`src/spec_dock/asset_layout.py`、`src/spec_dock/runtime/application/direct_static_update.py`、`src/spec_dock/assets/install_root/.agents/skills/spec-dock/SKILL.md`、`src/spec_dock/assets/spec_dock/docs/authoring/overview.md`、`README.md`、`AGENTS.md`、関連テスト、dogfood の `.agents/skills/spec-dock/SKILL.md`・`spec-dock/docs/authoring/overview.md`・`.claude/skills/**`。
- 変更しない: init / show の処理、`file_publication.py`、grill スキル、helper、ADR `20261014t072234z-adr` の本文。

## 移行・互換性・rollback
- 既存の利用者は、パッケージを更新してから `installation update --backup-dir ABS --yes` を実行する。既知のコピーが除去され、`.agents` 側の SKILL.md も更新される。
- `installation show` の JSON の形は変わらない。`assets` の要素数が4つ減る。
- rollback: provider を revert すれば、旧版は `.claude` 側を `installation.create` として再作成する（リンクの worktree では親チェーンで停止する）。

## testability
- unit: current inventory に `.claude` がないこと、retired の4エントリとハッシュ集合、retired allowlist が2 slot 以外の `.claude` を拒否すること、文書の記述。
- integration:
  - fresh init で `.claude` がない。既存の利用者の `.claude` は変わらない。
  - 旧版のコピーを置いた worktree で、dry-run・apply・再実行と、バックアップ・利用者ファイルの保持。
  - 未知の内容・hard link で停止（既存の parametrize を維持）。
  - slot のリンク・`.claude/skills` のリンク・`.claude` 全体のリンク・リンク先のないリンクで、init / show / update / uninstall が成功し、リンクとリンク先が変わらない。
  - uninstall の件数は 88 → 84。
- wheel: current inventory に `.claude` がなく、retired に4エントリがある。
- 手動: 候補 wheel の CLI で、この worktree の update と、リンク置換後の show / update。

## risk
- リンクをたどって `.agents` 側の正本を消す危険。grill の3ファイルは `.agents` 側と退役ハッシュが同じなので、リンクをたどると「既知のコピー」に見える。`_linked_host_slot` で入力から外し、テストで `.agents` 側の不変を確認する。
- 旧 CLI（ユーザーのツール環境の 0.2.4 は `4d25a8b4` のビルドで `.claude` 投影を含む）は、リンクの worktree で `.claude` 側を `unsafe` と表示し、update を停止する。パッケージの更新は範囲外なので、Report に残す。
