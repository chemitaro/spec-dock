---
種別: note
ID: "003-note"
タイトル: "Dogfooding Backlog Notes"
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-03-14"
親: ["init-local-00001"]
関連: [
  "001-adr-adopt-dogfooding.md",
  "002-adr-agentic-cli-roadmap.md"
]
---

# 003-note Dogfooding Backlog Notes

## 背景と目的 (必須)
- dogfooding しながら気づいた違和感、改善候補、将来の検討課題を継続的に追記するメモ。
- すぐに issue 化しない論点も、後で epic / issue に分解できる粒度で残す。

## 事実（観測結果） (必須)
- `discussions/rules.md` は template 側と generated 側に実体ファイルとして存在している。
- template 配下には `initiative/epics/new-epic`、`epic/issues/new-issue` の wrapper がある。
- provider 側の source と generated workspace の両方に似たファイル群があり、どちらを正本として保守するかを常に意識する必要がある。
- Git は空ディレクトリを保持できないため、template では placeholder 的なファイルや wrapper を置いて構造を維持している箇所がある。
- `spec-dock/active` は現時点で期待どおりに機能していない。
- 今回の dogfooding では initiative 作成後も `spec-dock/active/` が有効な参照先として使える状態になっていない。

## 検討メモ (任意)

### 1. `rules.md` は実体コピーではなく symlink でよいのではないか
- 論点:
  - 同じ内容の `rules.md` を複数箇所へ実体コピーすると、更新漏れや差分 drift が起きやすい。
- 仮説:
  - generated workspace 側や template 側で symlink を使えれば、単一正本に寄せられる可能性がある。
- 懸念:
  - Windows や zip 配布、scaffold 配布時の symlink 互換性は要確認。
  - installer/update/sync が symlink を安全に扱えるかも確認が必要。

### 2. `new-epic` / `new-issue` wrapper は本当に必要か
- 論点:
  - 個別ディレクトリごとに wrapper script を置くより、中央の runtime command を直接使う方が信頼性と保守性が高い可能性がある。
- 仮説:
  - `spec-dock/scripts/spec-dock new ...` に一本化できれば、distributed wrapper の管理コストを減らせる。
- 懸念:
  - wrapper が onboarding や local discoverability に効いている可能性はある。
  - 廃止するなら、docs と導線を同時に整理する必要がある。

### 3. 中央集約コードを優先し、ディレクトリ固有の実行体を減らしたい
- 論点:
  - directory-local な helper / wrapper / 実行体は、provider/source と generated workspace の差分理解を難しくする。
- 仮説:
  - command entrypoint と template source を中央集約すれば、dogfooding 中の認知負荷を下げられる。
- 検討観点:
  - 中央化しても active context の解決や UX が落ちないか。
  - docs 側だけで補えるか、それとも最小 wrapper は残すべきか。

### 4. 空ディレクトリをどう表現するか
- 論点:
  - Git が空ディレクトリを管理できないため、現在は placeholder 的なファイルや wrapper が構造保持の役割も担っている可能性がある。
- 仮説:
  - `_template.md`、`.gitkeep` 相当、README、あるいは symlink など、より意図が明確な形へ寄せられるかもしれない。
- 検討観点:
  - 利用者にとって誤解が少ないこと。
  - template / update / scaffold の互換性を壊さないこと。
  - placeholder が実行ファイルと混ざらないこと。

### 5. `active` ディレクトリ / symlink が機能していないように見える
- 論点:
  - dogfooding 開始時点で `spec-dock/active` が期待した active docs の入口として機能していない。
- 観測:
  - initiative 作成後も、`spec-dock/active/` をそのまま active な requirement/design/plan/report の参照先として使える状態になっていない。
- 仮説:
  - `active set` をまだ実行していないため未初期化の可能性はある。
  - ただし onboarding 上は「今 active が使えるのか」「初期状態ではどう見えるべきか」が分かりにくい。
- 懸念:
  - これは仕様未定ではなく、少なくとも UX 上のバグまたは不足説明として扱うべき可能性が高い。
  - dogfooding 導入直後に active 導線が使えないと、正本の入口が分かりづらくなる。

## 次アクション (必須)
- `rules.md` の配置戦略を論点化し、`copy vs symlink vs generated from single source` を比較する discussion を作る。
- `new-epic` / `new-issue` wrapper の利用実態と UX 価値を確認する。
- template 構造維持のために必要な placeholder を棚卸しし、空ディレクトリ表現の方針候補を整理する。
- `active` の初期状態と `active set` 後の期待動作を確認し、bug か仕様不足かを切り分ける。
- これらを将来の epic / issue 候補として backlog 化し、prototype 本線と extras を切り分ける。

## 参考（References） (任意)
- [rules.md](/srv/mount/spec-dock/spec-dock/initiatives/init-local-00001-dogfooding-prototype/discussions/rules.md)
- [001-adr-adopt-dogfooding.md](/srv/mount/spec-dock/spec-dock/initiatives/init-local-00001-dogfooding-prototype/discussions/001-adr-adopt-dogfooding.md)
- [002-adr-agentic-cli-roadmap.md](/srv/mount/spec-dock/spec-dock/initiatives/init-local-00001-dogfooding-prototype/discussions/002-adr-agentic-cli-roadmap.md)
