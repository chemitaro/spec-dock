# インストール・更新・削除

## 管理対象

SpecDockは `spec-dock/docs`、`templates`、`system`、`scripts` と、`.agents/skills/spec-dock`、`.agents/skills/spec-dock-grill-with-docs` を管理します。更新は各ディレクトリを削除し、配布元の同じ構造をそのままコピーします。内部の個別ファイルの保持や差分マージは行いません。ここに加えたローカル変更も消えます。

仕様書・成果物・Workbench・利用者設定は管理対象外です。既存のGitHub workflowも変更しません。新規workflowの自動配置は行いません。

## 初回配置

```sh
spec-dock init /path/to/project
```

未導入のspec-dockスキャフォールドを配置します。既存のspec-dockがある場合はupdateを使います。`init --force` はupdateと同じディレクトリ交換です。初回に配置した `.gitignore` は以後上書きしません。

初回initが途中失敗した場合は、原因を解消し、不完全な `spec-dock/` ディレクトリを別名または別の場所へ移して内容を保全してから、initを再実行してください。updateや `init --force` はツールだけを交換するため、欠けた初期設定（`.gitignore` など）の修復にはなりません。仕様や設定を作成済みでも、そのデータを自動削除する復旧処理はありません。

## 更新

更新中は、そのリポジトリのSpecDockコマンドを停止してください。

```sh
spec-dock update /path/to/project
```

導入先コマンドからも `./spec-dock/scripts/spec-dock update /path/to/project` で固定upstreamの外部installerを呼べます。途中失敗では新旧のコードが混在し得ます。エラー原因を解消して外部installerのupdateを最初から再実行してください。自動ロールバック、cleanup token、版ごとの移行認証はありません。旧状態記録は更新の判断に使いません。

## ツールだけの削除

```sh
spec-dock uninstall /path/to/project
spec-dock uninstall /path/to/project --apply
```

既定は変更しないdry-runです。applyは6ディレクトリとバージョン記録を削除します。仕様・成果物などは残ります。`--remove-specs` は拒否します。再導入は残ったspec-dockに対してupdateを実行できます。

## 確認

```sh
./spec-dock/scripts/spec-dock --help
./spec-dock/scripts/spec-dock validate
```

配置先のsymlinkや非ディレクトリは誤書込みを避けるため拒否します。利用者データを管理対象ディレクトリ内へ置かないでください。
