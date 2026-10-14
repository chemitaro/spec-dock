---
種別: 設計書（Issue）
ID: "iss-00418"
タイトル: "Fix Claude Code discovery of installed SpecDock skills"
関連GitHub: ["#418"]
状態: "draft"
最終更新: "2026-10-14"
依存: ["requirement.md"]
親: ["epic-00080", "init-00079"]
---

# iss-00418 Fix Claude Code discovery of installed SpecDock skills — 設計

詳細: [Design Guide](../../../docs/authoring/design.md)

## 設計目標
- 単一の provider 正本から、Codex と Claude Code のプロジェクト探索先へ、同じスキルを投影する。
- そのために、既存の静的インストール契約（ファイル単位のインベントリと fail-closed の init / update / uninstall / show）を、配置エントリの追加だけで再利用する。新しい資産型、ホスト検出、`$HOME` 操作は導入しない。

## Current / Target
- Current:
  - インベントリには、`.agents/skills/` 配下の4ファイルがある（`spec-dock/SKILL.md`、`spec-dock-grill-with-docs/{SKILL.md, agents/openai.yaml, scripts/finalize-artifact.py}`）。
  - allowlist は `.agents/skills/spec-dock/`・`.agents/skills/spec-dock-grill-with-docs/` の前方一致だけを許可する。
  - SKILL.md は `.agents` を前提にした記述を含む。
  - `installation show` は、ファイルが存在しなければ親を検査せずに `missing` とする。
- Target:
  - インベントリに `.claude/skills/` 配下の4エントリを加える。各エントリは、`.agents` 側と同じ source・sha256・mode・init_only を持つ。
  - allowlist は `.claude/skills` 配下の同名2 slot だけを追加で許可する。
  - SKILL.md はホスト中立の1種類にする。
  - `show` は、ファイルの有無を判定する前に親チェーンを検査する（RQ-418-08）。

```text
src/spec_dock/assets/install_root/.agents/skills/<name>/...   （唯一の正本）
        │ 同じ source を参照する2つのインベントリエントリ
        ├──▶ <worktree>/.agents/skills/<name>/...   Codex ほか
        └──▶ <worktree>/.claude/skills/<name>/...   Claude Code
```

## 責務・Interface
- `static-inventory.json`（provider 側のデータ）: 配置先の正本。`path` は配置先、`source` はパッケージ内の正本である。2つの投影の対応は、`path` の接頭辞 `.agents/skills/` と `.claude/skills/` を入れ替えた関係で表す。追加のスキーマ項目は設けない。
- `static_assets.package_static_assets()`（infra）:
  - 配置先の allowlist に、`.claude/skills/spec-dock/` と `.claude/skills/spec-dock-grill-with-docs/` を追加する。
  - `.claude/**` 全体や `.claude/skills/**` 全体は許可しない。
  - 同じ source を複数のエントリが参照することは、既存のとおり許可する。
  - `package_retired_assets()` の allowlist は変更しない（撤退時の拡張点として ADR に記録する）。
- `asset_layout.py`: 共有のパス定数として、スキルの投影ルート `SKILL_ROOTS = (".agents/skills", ".claude/skills")` を明示する。`TOOL_DIRECTORIES` はこの定数から導出する。現在この定数を参照するコードはないが、表す内容を実態とそろえる。
- `direct_installation.py` / `direct_static_update.py`（application）:
  - 投影は通常のインベントリエントリなので、init / update / uninstall のコードは変更しない。
  - init は、既存の配置先の拒否と親チェーンの検査を、`.claude` 側にも同じく適用する。
  - update は、欠落を `installation.create`、既知の旧版を `installation.change`、未知の内容を事前検査での停止として扱う。
  - uninstall は `retire_file()` でファイル単位に削除し、ディレクトリは削除しない。
- `installation show`（RQ-418-08）:
  - 各エントリについて、先に `verify_existing_parent()` を実行する。失敗（`ValueError`・`OSError`）は `unsafe` と分類する。
  - 親が安全で、ファイルがなければ `missing` とする。存在する場合の分類は既存どおりとする。
  - 状態の語彙に、ホストの種別を混ぜない。
- スキル本文（provider 正本、両投影で同一）:
  - `spec-dock/SKILL.md`:
    - 静的投影の説明を「root の `.agents/skills` と `.claude/skills` は、同じ provider 正本のホスト向け投影である」とする。
    - installation の説明に「管理するのは固定 slot 内の既知のファイルだけで、ホスト設定や他のスキルは管理しない」ことを加える。
    - 「running Codex processes」は「running agent processes」に一般化する。
  - `spec-dock-grill-with-docs/SKILL.md`:
    - preflight 8 では、`<skill-dir>` を「ホストが読み込んだこの `SKILL.md` のある絶対ディレクトリ」として解決する。そのうえで、`<skill-dir>/scripts/finalize-artifact.py` が、そのディレクトリ内の空でない通常ファイルであることを要求する。
    - 確定できなければ、Artifact コマンドの前に zero-write で停止する。
    - 他の探索先や `$HOME` から helper を探して代用しない。シェルの現在ディレクトリ相対で実行しない。
    - `agents/openai.yaml` は Codex の起動制御メタデータであり、実行前提ではないことを明記する。
    - 手順6・7の実行例は `python3 <skill-dir>/scripts/finalize-artifact.py ...` とする。
    - 保護対象の `.codex/config.toml` は、「ホストのエージェント設定（例: `.codex/`、`.claude/settings.json`）」に一般化する。
    - Claude Code 固有の置換変数 `${CLAUDE_SKILL_DIR}` は、本文に書かない。Codex では置換されないため、両投影を同一にできなくなる。
    - frontmatter の `disable-model-invocation: true` と `agents/openai.yaml` の `allow_implicit_invocation: false` は維持する。
    - helper の Python 実装は変更しない。対象の `--repo-root` と Artifact の安全性検査はそのまま使う。

## data / failure
- インベントリの値:
  - `.claude` 側の各エントリの sha256・mode・init_only は、対応する `.agents` 側と同じにする（現行4ファイルは mode `420`、すなわち `0644`、`init_only: false`）。
  - `known_old_sha256` は配置先ごとの履歴とする。
    - SKILL.md の内容を変えると、`.agents` 側の2エントリは、0.2.4 で配布中のハッシュを `known_old_sha256` に追加する。
    - `.claude` 側は過去に配布していないため、`[]` から始める。
- 並び順: `path` の昇順（`.agents/...` → `.claude/...` → `spec-dock/...`）を維持する。`package_static_assets()` が順序と一意性を検査する。
- 衝突時の振る舞い（既存の分岐の適用範囲を確認するもので、新しい分岐は作らない）:

  | 既存状態 | init | update | uninstall |
  |---|---|---|---|
  | `.claude/` または `.claude/skills/` が通常ディレクトリとして存在する | 共有の親として使う | 共有の親として使う | 残す |
  | 管理外のファイル（settings、他のスキル、slot 内の未知のファイル） | 変更しない | 変更しない | 変更しない |
  | 管理ファイルが現行版 | 既存の配置先として拒否する | 何もしない | バックアップして削除する |
  | 管理ファイルが、そのパスの既知の旧版 | 拒否する | バックアップして更新する | バックアップして削除する |
  | 管理ファイルが未知の内容 | 拒否する | 事前検査で停止する（手動マージ） | 事前検査で停止する |
  | 親・slot・ファイルが symlink、または特殊ファイル・hard link | 拒否する | 拒否する | 拒否する |

- 部分失敗: 既存の partial 報告（exit 6、効果ごとの `succeeded` / `unknown` / `not_attempted`）をそのまま使う。両投影の一括切り替えや自動 rollback は追加しない。

## 変更対象
- 変更する:
  - `src/spec_dock/assets/static-inventory.json`
  - `src/spec_dock/runtime/infra/static_assets.py`
  - `src/spec_dock/asset_layout.py`
  - `src/spec_dock/assets/install_root/.agents/skills/{spec-dock,spec-dock-grill-with-docs}/SKILL.md`
  - `src/spec_dock/assets/spec_dock/docs/authoring/overview.md`
  - `README.md`
  - `AGENTS.md`
  - テスト: `tests/unit/infra/test_provider_distribution.py`、`tests/unit/infra/test_authoring_kit_assets.py`、`tests/integration/test_issue413_assets.py`、`tests/integration/test_issue413_wheel.py`
  - 新規テストと 0.2.4 版スキルのフィクスチャ
  - `src/spec_dock/runtime/application/direct_installation.py` の show の分岐（RQ-418-08）
  - dogfood（RQ-418-09）の `.agents/skills/**`・`.claude/skills/**`・`spec-dock/docs/authoring/overview.md`。CLI による更新で反映する。
- 変更しない:
  - init / update / uninstall の処理本体
  - `package_retired_assets()`
  - `pyproject.toml`（`assets/install_root/.agents/**` が既に source を含む）
  - helper の Python 実装
  - `agents/openai.yaml`
  - epic-00074 と ADR `20260831t005139z-adr` の本文（改訂は新しい ADR で行い、過去の判断を書き換えない）

## 移行・互換性・rollback
- 既存の利用者は、外部パッケージを更新した後、対象 worktree で `installation update --target ABS --backup-dir ABS --yes` を実行する。これで、`.claude` 側の作成と `.agents` 側の更新が1回の操作で行われる。ホストの検出による分岐は行わない。
- 古い CLI（0.2.4 以前）は `.claude` 側を知らないため、`show` に表示せず、uninstall もしない。新しい配布物は、それを知っている版で扱う。
- `installation show` の JSON の形は変わらない。`assets` 配列の要素数が増えるだけである。
- rollback:
  - provider の変更を revert して、再配布する。
  - 既に `.claude` 側を受け取った consumer では、revert 後の CLI はそのファイルを管理外として扱う。
  - そのため、撤退は ADR の手順（retired inventory への移動と、retired allowlist の固定 slot への拡張）で行う。インベントリの削除だけでは撤退としない。

## testability
- インベントリの検査（unit）:
  - `.claude/skills/` 配下のエントリの集合が、`.agents/skills/` 配下のエントリの接頭辞を入れ替えた集合と等しい。
  - 対応するエントリの source・sha256・mode・init_only が一致する。
  - `.claude/settings.json` や `.claude/skills/other/SKILL.md` を指すエントリは、unsafe target として拒否される。
- provider と fresh consumer の一致（unit）:
  - `test_provider_matches_fresh_consumer_managed_assets` の比較対象に、`.claude/skills` を加える。
  - 8ファイルが通常ファイルで、`st_nlink == 1`、symlink を含まないことを確認する。
- installation の統合テスト（integration）:
  - init が8ファイルを作成する。
  - 既存の配置先が `.claude` 側にあると、init を拒否する。
  - `.claude` が symlink の場合、init と update を拒否する。
  - 利用者の `.claude` のファイルを保持する。
  - 0.2.4 相当の consumer からの update（フィクスチャの旧 SKILL.md と、`.claude` の欠落）で、create と change が行われ、dry-run は無変更、再実行は unchanged になる。
  - 未知の改変で停止する。
  - uninstall の削除件数（84 → 88）と、共有ディレクトリ・未知のファイルの保持。
  - `show` が `.claude` 側を分類する。
- スキル本文の検査（unit）: 固定パスがないこと、preflight の文言、起動制御メタデータの維持、`.claude/skills` の説明。
- wheel（integration）: 既存の全エントリの source・ハッシュ照合に加え、`.claude` 側の4エントリがインベントリにあることを確認する。
- 手動の外部確認:
  - fresh wheel の隔離環境で、init と、0.2.4 CLI で init した consumer の update を確認する。
  - 一時リポジトリで `claude -p` を実行し、スキル一覧を確認する。

## risk
- ホスト側の優先順位や worktree のフォールバックで、別の版が選ばれる（Requirement の失敗・境界条件を参照）。受け入れ確認は新しいセッションで行い、名前だけでなく、読み込み元のパスも確認する。
- スキルを変更するたびに、2エントリのハッシュを同時に更新する必要がある。インベントリの対応テストで、片方だけの更新を検出する。
- Git の改行変換（`core.autocrlf` など）で、checkout 後のバイト列が変わり得る。この Issue では `.gitattributes` を変更しない。不一致は既存の `unknown` 分類と手動マージで扱う。
- 協業者やクラウドでの利点は、管理対象の投影が Git にコミットされていることが前提である。文書で、両方の投影をコミットする運用を示す。
