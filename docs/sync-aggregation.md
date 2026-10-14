# 現在状態の観測と検証

`workspace sync`は、現在のScopeと依存、同じclone内のmain/linked worktreeの直接対象を、その場で観測します。index/tree、cache、世代などの保存物を再生成せず、Scope metadata、文書、Artifact、直接対象、残存する旧projectionを変更しません。詳細は[Sync参照](../src/spec_dock/assets/spec_dock/docs/reference_sync.md)と[CLI参照](../src/spec_dock/assets/spec_dock/docs/reference_cli.md)を参照します。

```sh
spec-dock workspace validate
spec-dock workspace sync --source local
spec-dock workspace sync --source github
spec-dock workspace doctor
```

既定はlocal観測です。GitHub lifecycleは未観測のunknownとして扱い、今回GitHubを読む場合に`--source github`を明示します。GitHub観測失敗やworktree観測不完全はunknown／partialのまま返し、empty・completed・完全観測とみなしません。`--source cache`は退役入力として拒否されます。

`workspace validate`は読み取り専用の構造・整合性検査です。`workspace doctor`は現在の宣言・直接記録などを診断し、自動修復しません。旧journalは明示的なraw/legacy診断の対象であり、現在の操作を再開・rollbackする制御基盤ではありません。旧Syncの集計仕様は[歴史資料](../src/spec_dock/assets/spec_dock/docs/historical/README.md)として扱います。
