# system（ツール管理の静的資産）

このディレクトリは `spec-dock` がconsumer worktreeへ配布する、ツール管理の説明・fallback文書を置く領域です。

- ここにあるファイルはInitiative / Epic / Issueのcanonical仕様書ではありません。
- provider側の正本は `src/spec_dock/assets/spec_dock/system/` です。consumer側のこの投影は、明示したworktreeに対する `spec-dock installation update` で更新される可能性があります。
- Python runtimeはここへ配布されません。実行するのはworktree外に導入した外部 `spec-dock` packageです。

## 現在の直接対象

現在のwriterは、各worktreeのignoredな次の場所に直接対象を0件または1件だけ保存します。

```text
spec-dock/.agent/work-target/target-<32桁の不透明なtoken>.json
```

file tokenは、Finishやclearが捕捉済みの一件だけを安全に解除するための識別子です。GitHub番号から作るScope ID、UUID、operation IDではありません。直接対象の取得は `spec-dock work start TARGET ...` だけが行います。`active set` は同じ妥当な直接対象のunchanged確認に限られ、空または別対象を取得しません。

## active-none（fallback文書）

`system/active-none/` は、直接対象が無い場合、または明示されたrecovery planning packも無い場合に読む静的fallback文書です。ここにあるREADMEや空のR/D/P/Reportは、現在の選択状態そのものではなく、通常編集の許可・禁止をfilesystem permissionで強制するものでもありません。

旧consumerに `spec-dock/active/{initiative,epic,issue}` のlegacy linkが残ることはありますが、それらはCurrent writerの直接選択ではありません。現在状態は `spec-dock active show --json` とworktree自身の直接記録で確認します。
