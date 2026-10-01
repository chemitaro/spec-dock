# 状態の観測と検証（Current）

`workspace sync` は、その時点のScopeの完了状態と、同じphysical cloneのmain/linked worktreeの直接対象を観測して返します。index/tree、generation、cache、登録台帳を保存せず、別cloneは集計しません。依存のreadinessは `dependency check` で別に確認します。

```sh
spec-dock workspace sync --source local --json
spec-dock workspace sync --source github --json
spec-dock workspace validate --json
spec-dock workspace validate --ci --json
spec-dock workspace doctor --json
```

source省略はlocalです。現在metadataを使い、GitHub未観測状態はunknownです。githubは明示的にGitHubを読みます。複数worktreeの予約と論理activeをまとめ、選択対象の現在の祖先からEpic/Initiativeを導出します。process_stateはnot_observedで、Codexが実行中だとは断定しません。

別branchへ移った予約も保持します。対象消失・破損・複数記録・アクセス不能を「未選択」と扱わず、不完全ならcomplete=falseと診断を返します。`--allow-invalid` も実体を修復しません。

通常validateはworking treeの構造を検査します。CI validateは一つの固定HEADの宣言/Scope/依存/Artifact entryを検査し、未commit本文・active・旧controlを採用しません。doctorはread-only診断です。--raw/--legacyは旧情報の分類に使い、旧engine実行やjournal再開はしません。
