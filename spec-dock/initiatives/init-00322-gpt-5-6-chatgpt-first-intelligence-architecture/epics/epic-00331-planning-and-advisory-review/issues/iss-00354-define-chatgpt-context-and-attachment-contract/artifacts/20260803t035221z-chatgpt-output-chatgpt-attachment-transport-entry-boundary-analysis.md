## 結論

**Option Aを推奨する。**

transportで表現できないentryが一つでも含まれる場合は、operation packを変更せず、**operation全体をfail-closedで終了する**。

* 除外しない
* symlinkを解決しない
* directoryを再帰展開しない
* ZIPやtextへ自動変換しない
* transport可能なentryだけを部分送信しない

GitHubコネクタで `chemitaro/spec-dock` とブランチ `codex/iss-00354-chatgpt-context-contract` を再確認した。ブランチは指定HEAD `39c67ef736e34c0131b2a0e38b64085561571f49` と一致している。

## 選択肢比較

### A — pack不変・全体失敗（推奨）

採用済みの「attachment directoryは信頼済みであり、その内容をすべてChatGPTへ渡す」という契約と最も整合する。

transport層の責務は、packを解釈・修正することではなく、**packをそのまま表現できるか判定すること**に限定される。

表現不能entryがあるのに一部だけ送ると、作成者が意図したpackとChatGPTが受信したpackが異なる。したがって、部分成功は許可すべきでない。

### B — symlink解決・特殊ファイル除外

非推奨。

* symlinkの参照先を添付することで、pack作成時の論理構造が変わる
* 参照先変更により同じpack pathから異なるbytesが送られ得る
* special fileを黙って除外すると、ChatGPTが不完全なpackを受け取る
* directory再帰のタイミングや範囲がtransport実装依存になる
* 「すべて添付する」という採用済み契約を暗黙に弱める

### C — manifest／text／ZIPへ自動変換

不採用。

* 元entryと送信されたartifactが同一ではなくなる
* ZIP化の構造、metadata、symlink表現など新しい契約が必要になる
* directoryをmanifestだけにすると内容が失われる
* special fileのtext化は意味を定義できない
* 自動変換後のbytesを新たなevidenceとして管理する必要が生じる

変換が必要ならtransportのfallbackではなく、**pack作成工程が明示的にtransport可能なpackを生成する**べきである。

## 推奨する一問

> operation packにChatGPT／Oracle transportで直接表現できないentryが一つでもある場合、packを変更・部分送信・自動変換せず、operation全体を失敗させるOption Aを採用しますか？

* **A（推奨）**: pack不変のまま全体を失敗
* **B**: symlinkを解決し、特殊ファイルを除外して続行
* **C**: unsupported entryを自動変換して続行

## 最小failure evidence

失敗時は次だけを記録すれば足りる。

```text
operation_id
pack_identity
transport_adapter_version
failure_code
unsupported_entry_relative_path
observed_entry_type
supported_entry_types
no_attachments_sent
failed_at
```

private absolute pathやentry内容は記録不要。

推奨failure code例：

```text
unsupported_directory_entry
unsupported_symlink_entry
unsupported_special_file
unsupported_transport_type
pack_not_representable
```

複数entryが不正でも、全件列挙するか最初の一件で停止するかは後続判断にできる。

## 次にユーザーが決める最小事項

### 1. transport可能なentryの集合

少なくとも次を明示する必要がある。

* regular fileのみか
* ZIPなどのbinary regular fileも対象か
* empty fileを許可するか
* directory markerを許可するか

推奨初期値は、**Oracleがattachmentとして直接受理できるregular fileだけ**。

### 2. directoryの意味

attachment root配下のdirectoryは、次のどちらかを決める必要がある。

* directoryは単なる相対パス構造であり、その配下のファイルをscriptが列挙して渡す
* directory entry自体もtransport対象とみなし、表現不能なら失敗する

通常のfilesystem走査ではdirectory自体をattachmentにせず、その配下のfileを渡すため、ユーザーの「directory itselfがunsupported」という表現と、採用済みの「directory contentsをすべてattach」の境界を明文化する必要がある。

推奨は、**directoryはcontainerでありattachment entryではない。配下の各entryを評価する**。

### 3. symlinkがpackに存在してよいか

採用済み方針ではfilenameやsymlinkを事前検査しないため、transport時に発見される可能性がある。

決めるべきなのは次のどちらか。

* symlinkを含むpackは常にtransport不能
* Oracleがsymlink自体をattachmentとして表現できる場合だけ許可

推奨は前者。

### 4. failureの粒度

* 最初のunsupported entryで停止
* 全entryを走査してunsupported一覧を返す

推奨は、packを変更しない読み取りだけで一覧化できるなら全件報告。ただし、Oracle invocationは開始しない。

### 5. 再試行責任

失敗後に誰がpackを修正するかを定める必要がある。

推奨境界：

```text
transport:
  pack_not_representable を返すだけ

pack creator / calling operation:
  packを明示的に修正・再生成する

transport:
  修正版を新しいoperationとして送信する
```

transportが修正案を自動適用してはならない。

**暫定判断:** Option Aは、「trusted packをそのまま送る」という方針と、「transportがpackの意味や構造を変更しない」という責務境界を一致させる。これはclarification evidenceであり、canonical採用や実装許可を意味しない。
