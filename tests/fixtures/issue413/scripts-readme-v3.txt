# SpecDock scripts

`spec-dock/scripts/spec-dock` は、導入済みの固定外部エンジンを呼ぶ薄い shim です。CLI の仕様と全コマンドは [CLI 参照](../docs/reference_cli.md)を確認してください。正確な引数は `spec-dock help COMMAND` で確認します。

```sh
spec-dock scope create issue --backend github --parent epic-00080 --title "Cleanup"
spec-dock work start iss-00411 --base main
spec-dock active show
spec-dock artifact create --scope iss-00411 --type blank --title "Memo"
spec-dock workspace validate
spec-dock workspace sync --source cache
```

`work start` は Initiative、Epic、Issue を受け付け、依存を確認して対応ブランチへ切り替え、対象を選択します。`work finish TARGET` は対象を完了し、選択中なら対象以下の選択を解除します。選択だけを変える場合は `active set TARGET`、完了状態だけを変える場合は `scope close TARGET` です。

導入・更新は固定エンジンの `installation init/update` を使います。更新、データ移行、エンジン引継ぎ、復旧は[移行・復旧](../docs/migration.md)を参照してください。`spec-dock/.agent/` と `spec-dock/active/` は生成状態であり、一次仕様ではありません。
