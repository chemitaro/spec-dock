# 依存関係（Current）

依存edgeの正本はScope metadataの `depends_on` です。fromがtoを前提とし、親から継承する制約もeffective viewで確認します。追加・削除はCLIを通し、循環、曖昧ID、不存在を拒否します。

```sh
spec-dock dependency list iss-00123 --view declared --json
spec-dock dependency list iss-00123 --view effective --json
spec-dock dependency check iss-00123 --source github --json
spec-dock dependency add --from iss-00123 --to iss-00122
spec-dock dependency remove --from iss-00123 --to iss-00122
```

checkのsource省略はlocalで、GitHub未観測はunknownです。キャッシュやstale許容flagは使いません。Startのreadinessはlive観測し、取得不能・不明なら開始を拒否します。readinessだけでは作業開始の許可や直接記録取得を意味しません。複数worktreeはSyncで観測します。
