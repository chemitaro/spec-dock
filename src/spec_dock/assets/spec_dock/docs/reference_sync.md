# 生成状態と検証（Current）

`workspace sync` はScope/依存/状態の観測からindex/treeなどの生成物を作り直します。正本であるScope metadata、文書、Artifact、選択状態は変更しません。GitHubを読む場合は明示的に `--source github` を指定します。

```sh
spec-dock workspace validate
spec-dock workspace sync --source cache
spec-dock workspace sync --source github
spec-dock workspace doctor
```

不正な正本状態がある場合、`--allow-invalid` は診断のための限定的な生成を許すだけです。`workspace doctor` は修復を実行しません。pending journalの操作IDと復旧方法を確認し、対象leafの `--resume` または `--rollback` を使います。旧版の集計仕様は[historical](historical/reference_sync.md)です。
