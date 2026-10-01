# SpecDock scripts

`spec-dock/scripts/spec-dock` は、PATH上の外部`spec-dock`へ引数をそのまま渡す互換shimです。標準の入口は、package managerで導入した外部`spec-dock`コマンドです。shimはGitのcontrolやrepository内のPython runtimeを必要としません。

外部consoleが見つからない場合は、packageの導入とPATHを確認してください。委譲先が自身・同じshimのコピー・既知の旧shimなら再帰を防いで停止します。旧branchのshimへ戻った場合も、外部`spec-dock`を直接実行できます。

CLIの仕様と全コマンドは[CLI参照](../docs/reference_cli.md)を確認してください。正確な引数は`spec-dock help COMMAND`で確認します。

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
