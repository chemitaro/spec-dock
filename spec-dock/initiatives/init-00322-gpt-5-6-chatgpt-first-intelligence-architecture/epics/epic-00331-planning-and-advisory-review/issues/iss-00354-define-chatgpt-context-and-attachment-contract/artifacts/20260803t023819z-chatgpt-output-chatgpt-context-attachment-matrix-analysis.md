## 結論

**Option Aを推奨する。**

チャット本文には、全phase共通の短いcontext envelopeだけを置く。詳細な手順、正本、証跡、レビュー対象はphase-specific attachment manifestで拘束し、必須添付の欠落・重複・SHA不一致はfail-closedにする。

GitHubコネクタで `chemitaro/spec-dock` とブランチ `codex/iss-00354-chatgpt-context-contract` を再確認した。ブランチは指定HEAD `39c67ef736e34c0131b2a0e38b64085561571f49` と `identical` である。

## 選択肢比較

### A — 短い共通本文＋phase別必須添付（推奨）

本文には次だけを置く。

* goal
* role／phase
* `operation_id`
* repository／branch／source HEAD
* Issue／Epic／Initiative scope
* thread mode
* authority／mutation constraints
* output contract
* attachment manifest digest
* 添付検証失敗時のhard-failure規則

詳細なレビュー観点や修正规則、canonical資料、Candidateなどは添付へ分離する。

この構成は、現行prompt synthesisがexact source identity、GitHub connector gate、authority boundary、role-specific output expectationを本文へ合成し、資料を添付として扱う構造と整合する。

### B — 詳細手順を本文、添付は任意

非推奨。

本文と添付の責務が曖昧になり、次の問題が起こる。

* 本文肥大化とphase間の文言drift
* 添付なしでも処理を続けてしまう
* Candidateやformal Reviewが「参考資料」扱いになる
* 同一Blue threadに残る旧本文がcurrent contractと誤認される
* prompt resourceとruntime validatorの整合を取りにくい

特にFormal ReviewでCandidate ZIPやidentity/checksumを任意添付にすると、レビュー対象の一意性を保証できない。

### C — 毎phaseで完全bundleを一つ添付

一見単純だが、phase境界が弱くなる。

* Reviewに不要なBlue Teamの調査・判断履歴を含め、独立性を損なう
* Revisionで無関係な資料まで再送し、どれが修正根拠か不明確になる
* bundle内部の権威分類が必要になり、単一bundle化だけでは契約が簡単にならない
* 同名ファイル・旧版・余分な資料の混在を検出しにくい
* サイズ増加と添付失敗の影響範囲が大きい

完全bundleはtransport単位として使用してもよいが、内部manifestでphaseごとのexact inventoryを閉じなければならない。その場合、実質的にはOption Aへ戻る。

## 推奨する一問

> 各phaseでは、短い共通context envelopeを本文に置き、phase別に定義された必須添付だけをmanifestとSHAで検証し、欠落・重複・不一致時はfail-closedにするOption Aを採用しますか？

選択肢：

* **A（推奨）**: 短い共通本文＋phase別必須添付manifest
* **B**: 詳細手順を本文へ置き、添付は任意
* **C**: 毎phaseで一つの完全bundleを添付

## 推奨phase matrix

### Clarification

必須または明示的に選択されたもの：

* research artifact
* unanswered／answered interview artifact
* 判断に必要なrelevant source
* 必要に応じてIssue bodyや上位scopeの抜粋

Clarificationではcanonical三文書の生成対象を添付するのではなく、判断根拠を添付する。まだ存在しない判断をcanonical authorityとして扱ってはならない。

### Planning

必須：

* current canonical `requirement.md`
* current canonical `design.md`
* current canonical `plan.md`
* parent Epic／Initiative scope資料
* relevant source files
* relevant tests
* 採用済みclarification evidence
* 必要ならonboarding companionのcurrent target

現行synthesisもcanonical Issue pathsと明示されたrelevant source pathsを取り込み、サイズ・件数・sensitive dataを検査している。

### Formal Review

必須かつ閉じたinventory：

* exact Candidate ZIP
* `reviewed-identity.json`
* identity digestを保持するchecksum evidence

原則として、Blue threadのresearch、interview、修正意図、会話履歴は添付しない。Reviewerはexact Candidateとsource identityをfresh read-onlyで検査する。Reviewer出力もclosed JSONに限定されている。 

「Candidate ZIP plus identity/checksum」だけでは、repository／branch／source HEADを検証するための本文envelopeは別途必要である。ここでいう「添付のみ」はレビュー証拠のinventoryについての限定であり、source identity gateを省略する意味ではない。

### Semantic Revision

必須：

* prior Candidate ZIP
* exact formal Review result
* reviewed identity／checksum
* preserved assumptions
* 選択された修正対象
* current repository／branch／source HEAD identity

Revisionは完全置換を行うが、Reviewで指摘されていない設計変更を自由に行うphaseではない。既存resourceもprior Candidate、formal Review evidence、selected findings、preserved assumptionsを前提としている。

## 主なリスク

### 本文と添付の二重定義

同じ命令を本文と添付の両方へ詳細に書くと、片方だけ更新される。優先順位を設けても、誤った方をモデルが参照する可能性が残る。

**対策:** 本文はidentity・authority・output・manifest参照に限定し、phase規則の詳細はversioned attachmentへ一元化する。

### 必須添付の暗黙的省略

同一Blue threadに以前の資料が残っているため、再添付を省略するケース。

**対策:** thread memoryはattachment fulfillmentとして数えない。各operationでmanifestを再検証する。

### 重複添付

同一logical roleに旧版と新版が同時に存在する。

**対策:** `logical_role`の一意性を要求し、同一roleの複数添付はfail-closed。明示的な`supersedes`があっても、transport時点では一つに正規化する。

### SHAの対象範囲不明

改行正規化後のtext SHAとexact bytesのSHAが混在する。

**対策:** `digest_basis`を必須にし、Candidate ZIPやformal evidenceは`exact_bytes`とする。

### Review contamination

Formal ReviewにBlue側の意図や過去のFAIL対応履歴を添付し、Red Teamが誘導される。

**対策:** Review inventoryをclosed allowlistにする。

### 過剰bundle

全資料を一括添付し、どれが権威を持つか不明になる。

**対策:** phase-specific inventoryとclassificationを必須化し、extra attachmentを拒否または明示的にsupplementalへ分類する。

## 最小manifest fields

### Manifest全体

```text
manifest_schema_version
operation_id
phase
repository
branch
source_head
issue_id
thread_mode
attachment_count
manifest_sha256
created_at
```

### 各添付

```text
logical_name
logical_role
classification
source_label
sha256
digest_basis
required
phase
media_type
size_bytes
```

最低限の意味は次のとおり。

* `logical_role`: `canonical_requirement`、`candidate_zip`、`formal_review`などの機械判定可能な役割
* `classification`: `review-target | formal-evidence | supplemental-context`
* `digest_basis`: `exact_bytes | utf8_normalized`
* `required`: 当該operationで欠落を許すか
* `phase`: 他phaseの添付を誤投入していないかの検証
* `source_label`: repository pathまたはartifact identity
* `sha256`: transport後のbytesとの一致確認

### Lineageがある添付

Candidate、Review、Revision evidenceには追加で次が必要。

```text
artifact_id
artifact_version
derived_from
supersedes
bound_candidate_id
bound_candidate_sha256
```

すべての添付へこれを強制する必要はない。lineageを持つformal artifactだけでよい。

## fail-closed条件

次の場合はChatGPT invocationを開始しないか、formal outputを受理しない。

```text
required attachment missing
unexpected duplicate logical_role
manifest attachment_count mismatch
declared SHA mismatch
digest_basis missing
phase mismatch
repository/branch/source_head mismatch
Candidate identity/checksum mismatch
Formal Review bound to another Candidate
closed inventoryに許可されないextra attachment
```

**暫定判断:** Option Aは、本文をrouting／identity／authority envelopeとして安定させ、phase固有の正本と証跡を検証可能な添付へ分離する。採用済みのBlue thread continuity、fail-closed recovery、fresh Red Reviewとも最も整合する。これはclarification evidenceであり、canonical採用を意味しない。
