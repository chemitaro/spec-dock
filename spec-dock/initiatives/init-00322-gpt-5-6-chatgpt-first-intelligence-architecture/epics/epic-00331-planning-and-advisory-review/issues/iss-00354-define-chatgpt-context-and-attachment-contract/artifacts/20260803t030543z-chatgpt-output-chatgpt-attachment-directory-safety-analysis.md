## 結論

**Option Aを推奨する。**

operation packは、明示されたpack root配下の通常ファイルを再帰収集し、相対パスと決定的順序を維持する。内容の意味は共通処理で解釈しない。一方、ファイルシステム境界・秘匿情報・容量については機械的にfail-closedとする。

GitHubコネクタで `chemitaro/spec-dock` とブランチ `codex/iss-00354-chatgpt-context-contract` を再確認した。ブランチは指定HEAD `39c67ef736e34c0131b2a0e38b64085561571f49` と `identical` である。

## 選択肢比較

### A — 再帰収集＋機械的安全検査（推奨）

次の契約が妥当。

* 収集起点は、scriptが明示的に指定した一つのpack root
* pack root配下を再帰的に走査
* 通常ファイルだけを収集
* pack rootからのPOSIX相対パスを保持
* 相対パスのbyte順など、固定された規則で決定的に並べる
* ファイル内容の業務的意味やroleは共通collectorでは解釈しない
* unsafe path、symlink、特殊ファイル、secret-like path、件数・容量超過は拒否
* 一つでも不正なら部分添付せず、pack全体を拒否

これにより、Markdownや補助ファイルの追加・削除をコード変更なしで反映しつつ、添付対象がrepository外へ拡張される事故を防げる。

現行prompt synthesisにも、安全な相対パス、symlink拒否、regular file確認、descriptor-relative read、件数・ファイル単位・合計サイズ上限、credential-like pathやsensitive payloadの拒否が存在するため、この方向は既存防御と整合する。

### B — root直下だけを収集

安全ではあるが、operation packという抽象には不十分。

* phase別に資料をサブディレクトリへ整理できない
* ZIPや複数分類の添付構造を自然に表現できない
* ファイル増加に伴って命名が平坦化する
* 将来、collectorとは別のコードでサブディレクトリ対応を追加し、検査境界が分裂する可能性がある

hidden fileやsymlinkを除外する点は正しいが、再帰収集自体を禁止する根拠にはならない。

### C — 無検査で全添付

不採用。

* `..`、absolute path、symlink経由でpack root外のファイルを添付し得る
* socket、FIFO、deviceなどでblockや不定動作が起きる
* `.env`、credential、private keyなどを漏洩し得る
* 巨大ファイルや大量ファイルによるresource exhaustion
* traversal順が環境依存になり、manifest SHAや再現性が不安定
* 途中まで収集したpartial packが送信され得る

「内容を意味的に検査しない」と「機械的安全検査をしない」は別である。

## 推奨する一問

> operation packは、明示されたroot配下の通常ファイルを相対パス保持・決定的順序で再帰収集し、内容の意味は共通処理で解釈しない一方、root escape、symlink、特殊ファイル、unsafe name、secret denylist、件数・容量違反をfail-closedで拒否するOption Aを採用しますか？

* **A（推奨）**: 再帰収集し、機械的安全検査を行う
* **B**: root直下の通常ファイルだけを収集
* **C**: root配下を無検査で全添付

## 最小契約

### 収集対象

収集可能：

```text
regular file
safe relative path
inside explicit pack root
within count and byte limits
not denied by path/name policy
```

拒否対象：

```text
symlink
hard-link anomaly that violates identity policy
directory as attachment
socket
FIFO
block/character device
unknown special file
absolute path
"." / ".." path component
path escape
unsafe or reserved filename
credential-like or explicit denylisted path
```

hard linkは直ちに危険とは限らないが、同一inodeが複数relative pathへ現れる場合の重複・取り違えを避けるため、拒否または明示記録のどちらかを決める必要がある。最小安全策は拒否。

### 決定的順序

推奨：

```text
normalize to POSIX relative path
reject invalid Unicode / normalization ambiguity
sort by UTF-8 encoded relative path bytes
```

locale依存sort、filesystem enumeration順、mtime順は使わない。

### Hidden files

「hiddenだから一律拒否」では粗い。

* `.env`、`.git`、`.ssh`、credential系は明示deny
* operation pack markerや管理metadataなど、許可が必要なhidden fileはallowlist可能
* デフォルトはdot-prefixed path拒否でもよいが、contract上明示する

現行コードはpath componentが `.` で始まる添付名を拒否しているため、互換性を優先するなら初期版はdotfile全面拒否が安全。

## 最小evidence fields

### Pack identity

```text
operation_id
pack_root_logical_name
pack_contract_version
repository
branch
source_head
collector_version
```

private absolute root pathは証跡へ残さない。

### Collection result

```text
file_count
total_size_bytes
deterministic_order_rule
pack_manifest_sha256
collection_status
collected_at
```

### ファイルごとの記録

```text
relative_path
file_type
size_bytes
sha256
ordinal
```

`file_type`は受理後は常に`regular`になるが、検査証跡として有用。

### Safety-policy identity

```text
path_policy_version
secret_denylist_version
max_file_count
max_file_size_bytes
max_total_size_bytes
symlink_policy
special_file_policy
dotfile_policy
```

### 拒否時

```text
rejection_code
rejected_relative_path
detected_file_type
violated_policy
no_partial_pack_emitted
```

秘密らしい実内容やroot外のabsolute pathをエラーへ含めてはならない。

## 最小テスト

### Positive

* root直下の複数ファイルを決定的順序で収集
* ネストしたサブディレクトリの相対パスを保持
* 作成順が異なっても同じmanifest順・SHA
* Markdown以外の許可されたregular fileも収集
* ファイル追加・削除がコード変更なしでmanifestへ反映

### Path boundary

* `..`を含むpathを拒否
* absolute pathを拒否
* symlink fileを拒否
* symlink directory経由のroot escapeを拒否
* pack root自体がsymlinkなら拒否
* 走査中のsymlink置換・TOCTOUを拒否または検知
* Unicode正規化で衝突する二つのpathを拒否

### File type

* FIFOを開かずに拒否
* socketを拒否
* device fileを拒否
* directoryをattachmentとして扱わない
* hard-link duplicateを定義どおり拒否

### Secret boundary

* `.env`
* private key
* credential filename
* token／secretの明示denylisted path
* `.git`やprivate runtime metadata

内容スキャンを全operationへ強制しない方針でも、**明示的なpath/name denylistは維持すべき**。内容ベースのsecret scannerを使うかは別のprofileまたはpolicy判断に分離できる。

### Limits

* file countちょうど上限は成功、超過は失敗
* individual sizeちょうど上限は成功、超過は失敗
* total sizeちょうど上限は成功、超過は失敗
* 超過時にpartial packを生成しない
* zero-byte regular fileの扱いを固定

### Integrity

* 収集後・送信前にファイルが変化した場合は拒否
* manifest SHAと実添付bytesが一致
* 同一relative pathの重複を拒否
* collector error時にChatGPT invocationを開始しない

## 重要な境界

共通collectorは、次を判定しない。

* このMarkdownがPlanning手順として正しいか
* Candidate ZIPがどのversionか
* researchとinterviewの意味的関係
* 出力テンプレートの内容
* 添付がそのphaseに十分か

それらはoperation packの作成責任またはphase固有validatorの責務である。

共通collectorが保証するのは、**明示root配下の安全な通常ファイル群を、再現可能な構造とbytesで添付したこと**までに限定する。

これはclarification evidenceであり、canonical採用や実装許可を意味しない。
