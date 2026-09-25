# 導入・一括移行・復旧

## 固定distribution

`spec-dock` はworktree外の固定distributionから実行します。repository内の `spec-dock/scripts/spec-dock` はengine locatorを検証して同じ外部engineを起動するshimです。checkoutのPython moduleやPATH上の別実装へ自動fallbackしません。`installation show` で供給元commit、digest、writer protocol、登録済みworktreeを確認します。

review済みwheelを隔離環境へ導入してから、`python -m spec_dock.fixed_bundle /absolute/path/to/fixed-engine` でworktree外の新しい固定engine directoryを作ります。出力された絶対実行pathとdigestをinventoryへ記録し、そのengineから以下の操作を行います。wheelのconsole scriptはhelp/version等の読取り確認用で、repositoryへの変更操作は固定engineの絶対実行pathを使います。

## 新規導入

```sh
spec-dock installation init /absolute/path/to/project --yes
spec-dock installation show --target /absolute/path/to/project
spec-dock workspace validate
```

導入前に対象repository、Git common directory、全worktree、既存dataを調べます。未導入の対象だけがinit可能です。失敗後はoperation IDとjournalを確認し、同じ固定distributionから `installation init PATH --resume ID --yes`、または `--rollback ID --yes` を実行します。partial stateに対して初回コマンドを盲目的に繰り返さないでください。

## 既存環境の一括切替

1. 全consumerとlinked worktreeのinventoryを取り、現在のwriter、data path、Git common directoryを照合します。旧writerを停止します。
2. 仕様・設定・tool導入先のbackupを隔離領域へ保存し、復元試験をします。同じ固定commitとbundle digestを全対象に使います。
3. `installation update --target PATH --commit SHA --maintenance --yes` で同じcommon directoryの全登録worktreeをmaintenanceにしてtool資産を更新します。
4. `workspace migrate --to-schema 3 --dry-run --json` で全登録worktreeのinventory digestと阻害要因を確認します。`specdock.migration-map/v1` のmappingをそのdigestに固定し、空の対応配列しか要らない場合も `workspace migrate --to-schema 3 --mapping-file PATH --yes` で適用します。適用時のmapping省略は受け付けません。
5. maintenance中に `installation show`、`workspace doctor`、`workspace validate` で全対象のprotocol、schema、journalを読取り確認します。全対象が同じ固定候補で検証できたら、各common directoryで `installation update --finalize --yes` を実行します。readyへの復帰後に `workspace sync --source cache` と再検証を行い、通常writerを再開します。

途中失敗では一部だけ旧writerを再開しません。journalとbackupを保存し、同じoperation IDで対象leafの `--resume ID` または `--rollback ID` を使います。別のcommitやengineを混ぜないでください。GitHub Issue状態はtool移行のrollback対象ではありません。

## 削除

```sh
spec-dock installation uninstall --target /absolute/path/to/project --yes
```

管理対象のtool資産だけを除去し、仕様履歴は残します。事前のdry-runで対象を確認し、journalとbackupのretentionを決めてください。削除後はrepository内shimでは復旧できないため、外部distributionから `installation show` と対象leafの復旧操作を行います。

## 旧版

以前の非transactionalな導入・更新・削除手順は[historical](historical/README.md)にある履歴資料です。現行engineでは使いません。
