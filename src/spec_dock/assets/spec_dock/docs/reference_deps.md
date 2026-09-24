# 依存関係（Current）

依存edgeの正本はScope metadataの `depends_on` です。`--from` が `--to` を前提とします。追加・削除はCLIを通し、循環、曖昧ID、存在しない対象を拒否します。

```sh
spec-dock dependency list iss-00123 --view declared
spec-dock dependency list iss-00123 --view effective
spec-dock dependency check iss-00123 --source github
spec-dock dependency add --from iss-00123 --to iss-00122
spec-dock dependency remove --from iss-00123 --to iss-00122
```

`work start` は開始前に依存のreadinessを確認します。GitHub状態が取得不能・不明なら安全側で開始を拒否します。cacheを使う場合は結果の鮮度を確認し、許容できる場合だけ `--allow-stale` を明示してください。結果を確認するには `workspace validate` と `workspace sync` を実行します。過去版の詳細は[historical](historical/reference_deps.md)に保存しています。
