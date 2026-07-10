# バックエンド呼び出しリファレンス（ChatGPT backend invocation reference）

この文書は `authoring backend invoke` の薄い backend invocation contract を説明します。
SpecDock は ChatGPT / Oracle automation 本体を内包しません。導入先環境が提供する backend command を、CLI 引数または環境変数で差し替え可能な外部依存として呼び出します。

## 契約（Contract）

`authoring backend invoke` は prompt pack を backend command に渡し、invocation summary と output location を evidence として記録する command です。
この command は canonical docs を編集せず、reviewer pass、execution-ready、PR-ready、merge-ready を主張しません。

backend command は次のいずれかで指定します。

- CLI option
- `SPECDOCK_CHATGPT_COMMAND`
- `ORACLE_CHATGPT_COMMAND`

未設定の場合は fail-closed で停止し、backend command の設定が必要であることを明確に示します。
個人環境の絶対パスは SpecDock の正式 workflow や shipped docs に固定しません。既存のローカル wrapper は、利用者が自分の環境で指定できる backend の一例です。

### ChatGPT Pro と Oracle implementation の選択

SpecDock は `GPT-5.5` や `GPT-5.6` のようなモデル世代、または `Extended` のような廃止・変更されうる thinking label を固定しません。設定された backend wrapper が、現在の ChatGPT `Pro` を選択します。

Oracle-compatible backend wrapper を使う場合、`authoring backend invoke` は optional な selector を転送できます。

```bash
./spec-dock/scripts/spec-dock authoring backend invoke \
  --prompt-pack <prompt-pack-dir> \
  --output-dir <output-dir> \
  --oracle personal
```

- `--oracle` を省略した場合、selector は転送されず、backend wrapper の standard/default implementation を使います。
- `--oracle standard` または `--oracle personal` を明示した場合だけ、その2引数を backend command の直後へ転送します。
- `--backend-command`、`SPECDOCK_CHATGPT_COMMAND`、`ORACLE_CHATGPT_COMMAND` 自体に `--oracle` を含める場合は、CLI の `--oracle` と併用しません。
- Personal Oracle の checkout path、build command、browser selector implementation は利用者側 wrapper が所有し、SpecDock assets には保存しません。
- Oracle-compatibleでない汎用backendでは`--oracle`を指定しません。

## 入力（Inputs）

backend invocation の主要 input は次の通りです。

- prompt pack directory
- output directory
- evidence mode: `github-synced` または `local-context`
- optional backend command override
- optional dry-run
- metadata for branch / commit / source manifest

`github-synced` mode では、GitHub に push 済みの branch / commit を ChatGPT 側が参照できることを前提にします。
`local-context` mode では、GitHub sync を確認できない代わりに、必要な local context を prompt pack に含めます。

## 出力（Outputs）

出力は evidence です。

- invocation summary
- backend stdout / stderr の必要最小限の参照
- ChatGPT output directory
- ZIP / tree output への path
- evidence mode と source manifest

raw transcript、secret、credential、host-local absolute path は durable docs に保存しません。
保存が必要な場合も、main orchestrator が要約と採否判断だけを `report.md` の Evidence Adoption Ledger に残します。

## 失敗時の扱い（Failure handling）

- backend command 未設定: fail-closed。設定方法を示して停止する。
- GitHub sync 未確認: `local-context` を明示するか、push / sync してから `github-synced` で再実行する。
- backend failure: canonical docs を変更せず、failure summary を evidence として残す。
- output missing / unreadable: `authoring pack review` に進めない。

## 権限境界（Authority boundary）

backend invocation が成功しても、次の状態にはなりません。

- canonical adoption completed
- reviewer pass
- `.assurance.json` mutation
- `authorized_profile` decision
- execution-ready
- PR-ready
- merge-ready

これらは各 planning / execution workflow と reviewer gate が所有します。
