# 生成状態と検証（現行）

`workspace sync` は Scope、依存、状態の観測から index/tree などの生成物を再構築します。Scope metadata、文書、Artifact、active の選択は変更しません。仕様と操作の正本は[生成状態の参照](../src/spec_dock/assets/spec_dock/docs/reference_sync.md)と[CLI 参照](../src/spec_dock/assets/spec_dock/docs/reference_cli.md)です。

```sh
spec-dock workspace validate
spec-dock workspace sync --source cache
spec-dock workspace sync --source github
spec-dock workspace doctor
```

GitHub を読む場合は `--source github` を明示します。`workspace validate` は読み取り専用の整合性検査です。`workspace doctor` は未完了 journal などを診断しますが自動修復はしません。旧 `sync [--github]` の集計仕様は[歴史資料](../src/spec_dock/assets/spec_dock/docs/historical/README.md)として扱います。
