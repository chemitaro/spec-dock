## 結論

**Option Aを推奨する。**

* 本文は、goal・role・operation identity・source identity・authority boundary・output contract参照だけに絞る。
* phaseごとの詳細手順、出力制約、例、禁止事項は、**versioned phase-specific output-contract Markdown**へ一元化する。
* Runtime／Codexは、返却物をその契約に対して機械検証する。
* `requirement.md`／`design.md`／`plan.md`の本文構成や内容テンプレートは必要以上に固定せず、**成果物の種類、inventory、container、closed fieldsだけを強制する**。

GitHubコネクタで `chemitaro/spec-dock` とブランチ `codex/iss-00354-chatgpt-context-contract` を再確認した。ブランチは指定HEAD `39c67ef736e34c0131b2a0e38b64085561571f49` と `identical` である。

## 選択肢比較

### A — versioned output-contract添付（推奨）

本文例の責務は次に限定する。

```text
goal
role / phase
operation_id
repository / branch / source_head
scope identity
thread mode
authority / mutation constraints
output-contract attachment identity
required formal output kind
```

詳細はphase別Markdownに集約する。

* Planning／Semantic Revision
  単一ZIPを返す。ZIP内には必須三文書とonboarding companionを含める。
* Formal Review
  許可されたtop-level／finding fieldsだけを持つclosed JSONを返す。
* Clarification
  ChatGPTにformal repository artifactを作らせず、回答をCodex側がinterview／research evidenceとして捕捉する。

現行実装もPlanner／Semantic Revisionを`authoring_zip`、Reviewerを`review_json`として区別し、ZIP inventoryとclosed JSON keysを検証している。

この方式は、本文肥大化を防ぎながら、詳細手順を一つの保守可能なresourceへ集約できる。

### B — 完全な出力テンプレートを本文へ埋め込む

非推奨。

* 毎turnの本文が大きくなる。
* 同一Blue threadで古いtemplateが履歴に残る。
* resourceと本文コピーのdriftが起きる。
* phase追加やfield変更時に複数箇所の更新が必要になる。
* document内容まで固定しやすくなり、ChatGPTのauthoring能力を不必要に制限する。

特にPlanning文書の詳細見出しや文章構造を本文で過剰指定すると、「成果物の意味的品質」より「テンプレート適合」が優先される。

### C — ChatGPTに形式を選ばせ、Codexが後変換

不採用。

* 変換時に意味やlineageが変わる。
* Reviewer出力を自由文からJSONへ変換すると、severityやfinding境界をCodexが推測することになる。
* ZIP inventoryやlogical filenameを事後推定する必要がある。
* ChatGPTの出力と保存されたformal evidenceが同一でなくなる。
* malformed outputを「変換可能」として受理し、fail-closed境界を弱める。

Codexによる後変換は、文字コードやtransport framingの正規化程度に限定すべきで、semantic format conversionには使うべきではない。

## 推奨する一問

> 各phaseの詳細な出力手順と形式をversioned Markdown attachmentへ一元化し、本文はgoalと契約参照だけに絞り、Runtime／CodexがZIP inventoryまたはclosed JSON schemaを検証するOption Aを採用しますか？

選択肢：

* **A（推奨）**: versioned phase-specific output contractを添付し、formal formatを機械検証
* **B**: 完全な出力テンプレートを毎回本文へ埋め込む
* **C**: ChatGPTの自由形式出力をCodexが事後変換

## 推奨する拘束範囲

### 強制すべきもの

Planning／Semantic Revision：

```text
output kind = one ZIP
logical filename
internal root
exact required file inventory
no extra formal output
ZIP validity
file uniqueness
UTF-8 / size / path safety
```

Formal Review：

```text
output kind = one JSON object
exact top-level keys
exact finding keys
allowed severity values
verdict derivation rule
reviewed identity binding
no extra prose
```

Clarification：

```text
output kind = advisory text
operation_id binding
question / selected option / rationale capture
Codex-side interview or research artifact identity
no canonical mutation
```

現行transport契約も、Planner／Revisionは一つのdownloadable ZIP、Reviewerは一つのclosed JSONに限定し、追加説明やinline文書、patchなどを禁止している。

### 強制しすぎないもの

* `requirement.md`の詳細な文章構成
* `design.md`の設計表現方法
* `plan.md`の作業分割粒度
* 各節の固定文言
* 不要な固定見出し数
* 内容上の結論
* 文書内の説明順序

ただし、上位canonical contractが必須見出しやdiagram roleを既に要求している場合、それをIssue #354で暗黙に解除してはならない。現行Planner／Revision resourceには、onboarding companionについて固定sectionとPlantUML要件が存在するため、三文書の自由度とcompanionの既存制約は分けて扱う必要がある。 

## 主なリスク

### Contract attachmentの欠落

本文が「添付を参照」とだけ記載し、実際には添付されていない。

**対策:** output-contract attachmentをrequired roleとしてmanifestに登録し、欠落時はinvocation前にfail-closed。

### Contract version drift

本文がv3を参照する一方、添付はv2、validatorはv1を使用する。

**対策:** body、manifest、validator evidenceの三者でcontract ID／version／SHAを一致させる。

### Markdownとvalidatorの不一致

Markdownではfieldを許可しているが、コードvalidatorは拒否する、または逆。

**対策:** Markdown contractとmachine-readable expectationを同一versionとしてbindingし、projection parity testを持つ。

### 過剰なtemplate規定

出力形式だけでなく、文書内容や設計判断まで固定する。

**対策:** contractをcontainer／inventory／schema／authority boundaryに限定し、semantic contentはcanonical sourceとChatGPT authoringへ委ねる。

### 不足した形式規定

「ZIPを返す」だけで、内部rootや必須ファイルが未指定。

**対策:** exact inventoryとlogical filenameは強制する。現行`PlanningOutputExpectation`はこの粒度まで検証している。

### Clarificationのformal evidence喪失

自由回答をチャット履歴にだけ残し、採用判断へ追跡できない。

**対策:** Codexが質問、回答原文、選択肢、日時、source identity、採用状態をinterview／research artifactへ捕捉する。

## 最小evidence fields

### Output-contract identity

```text
contract_id
contract_version
phase
contract_attachment_logical_name
contract_attachment_sha256
contract_media_type
effective_from
```

`contract_id`とversionは分離する。ファイル名だけをversion identityにしない。

### Operation binding

```text
operation_id
role
repository
branch
source_head
issue_id
thread_id
thread_mode
attachment_manifest_sha256
```

### Expected format

```text
output_kind
logical_filename
internal_root
required_inventory
allowed_extra_files
closed_top_level_keys
closed_item_keys
allowed_enum_values
max_output_count
```

phaseに不要なfieldは省略可能。

### Validation result

```text
validator_contract_id
validator_contract_version
validated_contract_sha256
received_output_sha256
format_validation_status
inventory_validation_status
identity_binding_status
validation_findings
validated_at
```

### Clarification capture

```text
question_id
question_contract_version
answer_text
selected_option
source_operation_id
captured_artifact_id
captured_artifact_sha256
adoption_status
```

## fail-closed条件

次の場合はformal outputを受理しない。

```text
output-contract attachment missing
contract ID/version/SHA mismatch
body reference and manifest mismatch
validator uses another contract version
wrong output kind
multiple formal outputs
ZIP filename or internal root mismatch
required document missing
duplicate required document
unexpected file where inventory is closed
Reviewer JSON has missing or extra keys
invalid severity or verdict
identity binding mismatch
extra prose outside closed formal output
```

## 暫定判断

Option Aは、次の三点を同時に満たす。

1. chat bodyと継続threadの肥大化を抑える
2. phase procedureを一つのMarkdown resourceとして保守する
3. document内容を過剰指定せず、formal outputだけを機械的に強制する

これはclarification evidenceであり、canonical文書への採用や実装許可を意味しない。
