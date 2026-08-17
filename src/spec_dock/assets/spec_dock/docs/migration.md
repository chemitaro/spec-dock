# 移行ガイド

このページは、既に `spec-dock` を導入しているリポジトリを現行の Storage Core 配布面へ更新するための手順です。新規導入は [全体ガイド](guide.md) を参照してください。

## 1. 更新前の確認

作業対象リポジトリで、未コミットの変更と利用者が管理する仕様データを確認します。`spec-dock update` は仕様履歴、Artifact、Discussion、ADR、Workbench の利用者データを自動変換しません。

```bash
git status --short
./spec-dock/scripts/spec-dock validate
```

## 2. 現行配布面へ更新する

通常は repo-local wrapper を使います。

```bash
./spec-dock/scripts/spec-dock update
```

別の管理対象を更新する場合はパスを明示できます。

```bash
./spec-dock/scripts/spec-dock update /path/to/project
```

更新は固定 upstream の recognized distribution を一つの計画として検証します。所有権を証明できない変更、symlink、hard-link、root の差し替え、未知の衝突は保持して書き込みを停止します。途中で停止した場合は、同じ root・package・operation に対して同じ update command を再実行してください。`spec-dock/.distribution-retry.json` が残る場合は、別の root や別 package で上書きせず、診断された対象を先に確認します。

## 3. 旧レイアウトや衝突がある場合

自動的な rename、仕様書の再構成、利用者ファイルの強制削除は行いません。まず dry-run で対象と preserve set を確認し、managed surface だけを除去する必要がある場合に限り、仕様履歴を残すモードで uninstall を実行します。

```bash
spec-dock uninstall /path/to/project
spec-dock uninstall /path/to/project --apply --keep-specs
spec-dock init /path/to/project
```

`--remove-specs` は仕様履歴を削除する明示操作です。実行前に `--keep-specs` で残すデータと unknown content を確認してください。uninstall の部分失敗では `.uninstall-retry.json` が post-verify まで残り、同じ対象へ再実行して forward recovery します。

成功した `--remove-specs` uninstall は、再初期化の境界として空の `spec-dock/` ディレクトリを残すことがあります。空境界には利用者データがないため、同じ対象で `spec-dock init /path/to/project` を実行して現行配布面を再作成できます。部分失敗のJSON / text診断に表示されるretry commandは、元の対象を失わないよう現在の作業ディレクトリからの相対パスを使います。同じ作業ディレクトリで、表示されたコマンドをそのまま再実行してください。

## 4. Artifact の取り込み

現行の generic import は `artifact import file` です。一件の明示 regular file を opaque Artifact として保存し、source は変更・削除しません。

```bash
./spec-dock/scripts/spec-dock artifact import file \
  --issue iss-00123 \
  --file path/to/evidence.md
```

既存の evidence は自動的に canonical document へ書き換えられません。採用する主張は、レビュー後に Requirement、Design、Plan、Report へ手動で反映します。

## 5. 更新後の確認

```bash
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync --no-github
./spec-dock/scripts/spec-dock --help
```

Current の入口は [docs README](README.md)、[全体ガイド](guide.md)、[Authoring Kit 概要](authoring/overview.md) です。更新後も利用者所有の仕様履歴と Workbench を保持し、Current の runtime command と二つの repo-local skill だけを使用してください。
