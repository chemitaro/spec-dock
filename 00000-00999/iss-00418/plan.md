---
種別: 実装計画書（Issue）
ID: "iss-00418"
タイトル: "Fix Claude Code discovery of installed SpecDock skills"
関連GitHub: ["#418"]
状態: "draft"
最終更新: "2026-10-14"
依存: ["requirement.md", "design.md"]
親: ["epic-00080", "init-00079"]
---

# iss-00418 Fix Claude Code discovery of installed SpecDock skills — 実装計画

詳細: [Issue Plan Guide](../../../docs/authoring/issue-plan.md)

## Planning Level
- 選択: `strict`
- 理由:
  - consumer の worktree に新しい管理対象パス（共有の `.claude/` 配下）を加える、shipped asset API の変更である。
  - uninstall の削除対象も増える。
  - 撤退には retired inventory と allowlist の拡張が必要で、revert だけでは戻らない。
- risk factor:
  - 利用者の `.claude/` にあるホスト設定を巻き込むこと
  - 既存 consumer の update 経路
  - 両投影の不一致
  - ホスト側の探索仕様への依存
- 再評価条件: 次のいずれかが必要になったら `critical` へ再評価する。
  - `$HOME` やホスト設定への書き込み
  - fail-closed 契約の緩和
  - 利用者データの削除を伴う移行

## 目標
- Requirement の AC-418-01〜07 を、provider 優先の実装、テスト先行の回帰テスト、fresh wheel、Claude Code の実機確認で満たす。
- AC-418-08・09 は、承認された場合に同じ方法で満たす。

## 順序・依存
1. P0（ユーザーの承認）: 次の3点を確定する。承認までコードは変更しない。
   - ADR `20261014t072234z-adr` の受理
   - RQ-418-08（`show` の親チェーン検査）を範囲に含めるか
   - RQ-418-09（dogfood の更新）を範囲に含めるか
2. S01〜S03 は、この順に進める。インベントリの値は S03 の SKILL.md の確定後に決まるため、S02 は S03 の後でハッシュを再計算する。
3. S04（`show`）は S01〜S03 と独立しているので、承認された場合は並行して進めてよい。
4. S05（文書）は S03 の後に行う。
5. S06（検証）、S07（dogfood）、S08（記録と引き渡し）の順に進める。S07 は S06 の候補 wheel を使う。

## 実装step
- S01（Red）: 次のテストを先に追加し、失敗を確認する。
  - インベントリの投影対応: 集合、source・sha256・mode・init_only の一致
  - `.claude` の allowlist 外のエントリの拒否
  - provider と fresh consumer の `.claude/skills` 一致（通常ファイル、`st_nlink == 1`）
  - init による8ファイルの作成
  - `.claude` 側での既存の配置先の拒否
  - `.claude` が symlink の場合の init / update の拒否
  - 利用者の `.claude` のファイルの保持
  - 0.2.4 相当の consumer からの update（フィクスチャ `tests/fixtures/issue418/` に 0.2.4 版の SKILL.md 2つを置く）
  - `.claude` 側の未知の改変・hard link・symlink の拒否（既存の parametrize に追加する）
  - `.claude` 作成中の部分失敗と、再実行による収束
  - uninstall の件数（88）と共有ディレクトリの保持
  - `show` での `.claude` の分類
  - スキル本文の中立性
- S02（Green: 投影）:
  - `static_assets.py` の allowlist に、`.claude` の2 slot を追加する。
  - `asset_layout.py` に `SKILL_ROOTS` を追加する。
  - インベントリに `.claude` の4エントリを追加する。値はスクリプトで source から計算し、`.agents` 側と照合する。
- S03（Green: スキル本文）:
  - Design のとおり、2つの SKILL.md を中立化する。
  - `.agents` 側の sha256 を更新し、0.2.4 で配布中のハッシュを `known_old_sha256` に追加する。
  - `.claude` 側は同じ sha256 で、`known_old_sha256: []` とする。
- S04（RQ-418-08 を含める場合）: `installation show` で、欠落判定の前に `verify_existing_parent()` を実行し、失敗を `unsafe` と分類する。
- S05（文書）:
  - `README.md`、`src/spec_dock/assets/spec_dock/docs/authoring/overview.md`、`AGENTS.md` に、`.claude/skills` の投影、所有の範囲、同一バイト列のコピーの扱いを記載する。
  - 文書の資産テスト（`RESERVED_SKILL_PATHS` など）を追随させる。
- S06（検証）: 「検証」の節のとおり。
- S07（RQ-418-09 を含める場合）:
  - S06 の候補 wheel を隔離環境に導入し、その CLI でこの worktree だけに `installation update --target <this worktree> --backup-dir <未使用の /private/tmp/...> --yes` を実行する。
  - 結果を `show` とバイト比較で確認してから、管理対象のパスだけをコミットする。
  - ユーザーのインストール済みパッケージ、main checkout、他の linked worktree は更新しない。
- S08（記録と引き渡し）:
  - ADR の受理を frontmatter に反映する（受理された場合のみ）。
  - Report に結果を記録する。
  - コミットし、PR を作成する（Issue #418 を関連付け、自動クローズしない）。
  - CI を確認する。

## 検証
- AC-418-01・03・04・05（テスト）: `uv run pytest tests/unit/infra/test_provider_distribution.py tests/unit/infra/test_authoring_kit_assets.py tests/integration/test_issue413_assets.py tests/integration/test_issue413_wheel.py` と、新規テスト。
- AC-418-02（移行）:
  - 統合テストで、フィクスチャによる 0.2.4 相当の consumer を確認する。
  - 外部確認として、ユーザーの 0.2.4 CLI（`~/.local/bin/spec-dock`。実行するだけで変更しない）で一時リポジトリに `installation init` し、候補 CLI で `installation update --backup-dir ... --yes` を実行する。結果は、作成と変更の一覧、バックアップの内容、再実行の `unchanged` で確認する。
- 失敗と回復（negative test）:
  - 未知の改変、hard link、symlink、`.claude` が symlink の場合に、効果0で停止すること
  - 部分失敗の後、新しい update で収束すること
- 回帰: `uv run pytest`（全体）、`make lint`。
- AC-418-06（fresh wheel）:
  - `uv build --wheel --out-dir <未使用の /private/tmp/...>` でビルドし、`uv venv <未使用の /private/tmp/...>` に非 editable で導入する。
  - その CLI で一時 Git リポジトリに init し、8ファイルのバイト一致を確認する。
  - `spec-dock workspace validate` の findings が0件であることを確認する。
- AC-418-07（実機）: 候補 wheel で init した一時リポジトリで、Claude Code の新しいセッション（`claude -p`）にスキル一覧を尋ね、`spec-dock` が表示されることを確認する。実行できなければ、その理由を Report に記録する。
- security / privacy / operability:
  - 影響は、利用者の `.claude/` を変更しないことに集約される。上記の保持テストと allowlist の拒否テストで確認する。
  - テストの出力にファイルの内容を出さない既存の検査を、`.claude` 側にも適用する。
  - 新しい秘密情報、ネットワーク、権限は扱わない。

## rollback
- マージ前: ブランチの revert で戻せる。
- マージ後の provider: 変更を revert して再配布する。
- `.claude` 側を受け取った consumer の forward recovery: ADR の撤退手順で行う。
  1. `.claude` の各管理ファイルを retired inventory へ移し、配布したハッシュを登録する。
  2. `package_retired_assets()` の allowlist を固定 slot に限って拡張する。
  3. 通常の update で、既知のファイルだけを除去する。

  インベントリの削除だけでは戻さない。
- dogfood（S07）: 更新のコミットを revert する。CLI のバックアップは、検証が終わるまで `/private/tmp/...` に残す。
- データ移行: N/A。利用者データ（Scope、Artifact、Workbench）は変更しない。

## exit / handoff
- 完了の条件: 次の情報を Report に残し、PR が merge 可能な状態になっていること。マージは人間が行う。
  - AC-418-01〜07（と、承認された AC-418-08・09）の実測の証拠
  - 変更したパス
  - 実行したコマンドと結果（失敗とスキップを含む）
  - コミットの SHA
  - PR の URL と CI の状態
- 残余リスク（Report と PR に明記する）:
  - ホスト側の優先順位と worktree のフォールバック
  - 同一バイト列のコピーの所有権
  - 改行変換
  - 他の worktree が未更新であること
- Issue の Finish（`work finish`）は、マージを確認した後の別の操作とし、この計画の完了条件に含めない。
