## 結論

**Option Aを推奨する。**

共通context／attachment／output contractは、**product-owned ChatGPT operation全体に適用できる共通基盤**として定義する。一方、Issue #354で具体的に登録・検証するprofileは次に限定する。

* Clarification
* Planning
* Formal Review
* Semantic Revision

Implementation Brief、onboarding、将来の一般roleは、共通基盤を再利用する**後続のprofile-registration Issue**で追加する。

personal `chatgpt-use` wrapperや自由なoperator consultationは、product runtime contractの外に置く。

GitHubコネクタで `chemitaro/spec-dock` とブランチ `codex/iss-00354-chatgpt-context-contract` を再確認した。ブランチは指定HEAD `39c67ef736e34c0131b2a0e38b64085561571f49` と `identical` である。

## 選択肢比較

### A — 共通基盤は全product operation向け、具体profileは4種に限定（推奨）

最も境界が明確。

Issue #354では、再利用可能な共通契約を定義しつつ、現在source-groundedに入力・添付・出力を確定できる4 profileだけを登録する。

```text
Common contract
├── Clarification profile
├── Planning profile
├── Formal Review profile
└── Semantic Revision profile
```

将来profile：

```text
Implementation Brief
Onboarding
QA review
Code review
General advisory role
Other product-owned ChatGPT operations
```

これらはcommon contractを継承するが、それぞれ別Issueでrequired attachments、output contract、authority boundaryを登録する。

現行実装もproduct runtimeではprovider-owned direct Oracleを使用し、personal wrapperをruntime dependencyとして扱っていない。

### B — Planning／Review／Revisionだけに限定

狭すぎる。

短期実装は単純になるが、Clarificationや後続roleが別形式のcontext contractを独自に作る可能性がある。結果として、Issue #354が目指す一般化可能な入力・添付・出力境界を再度設計することになる。

ただし、**実装profileを限定する**という意味では正しい。Option Aは、共通schemaの適用可能範囲を広く定義し、今回のconcrete implementationを限定することで、この利点を包含する。

### C — personal wrapper／自由相談も含める

非推奨。

personal consultationは次の点でproduct operationと異なる。

* repository／branch／HEADが存在しない場合がある
* formal outputを必要としない
* attachment inventoryを閉じられない
* Human approvalやCandidate lifecycleを持たない
* runtime validatorを通らない
* operatorの自由な質問・探索が主目的

これをproduct contractへ含めると、共通契約を緩めるか、個人利用へ過剰な手続きを強制することになる。

`chatgpt-use` wrapperはreference／operator work surfaceとして言及してもよいが、product-owned transport、validation、evidence lifecycleの適合対象にはしない。

## 推奨する一問

> 共通context／attachment／output contractは全product-owned ChatGPT operation向けの基盤として定義し、Issue #354ではClarification・Planning・Formal Review・Semantic Revisionだけを具体profileとして登録し、その他のroleは後続Issueへ委ね、personal wrapperと自由相談は対象外とするOption Aを採用しますか？

選択肢：

* **A（推奨）**: 共通基盤は全product operation向け、今回の具体profileは4種
* **B**: 契約自体をPlanning／Review／Revisionだけに限定
* **C**: personal wrapper／自由相談も同じ契約へ含める

## Scope risks

### 共通契約の抽象化過多

将来roleを想定しすぎて、現在必要のないextension pointや複雑なschemaを作る。

**対策:** 共通部分は次に限定する。

```text
operation identity
source identity
role/profile identity
thread mode
authority constraints
attachment manifest
output-contract reference
validation result
```

Candidate、Review、canonical docsなどはprofile固有fieldとする。

### 未登録profileの暗黙利用

Implementation Briefなどが、profile未登録のままgeneral roleとしてcommon contractを利用する。

**対策:** `profile_id`を必須にし、未登録profileはproduct runtimeでfail-closedにする。

### Clarificationの過度な形式化

ClarificationまでPlanningと同じformal outputを要求し、対話性を損なう。

**対策:** Clarification profileはChatGPTの回答をadvisory textとして許可し、Codex側capture artifactをformal evidenceとする。

### Personal／product境界の混同

personal wrapperで得た回答を、そのままvalidated product evidenceとして扱う。

**対策:** provenanceに`execution_surface`と`product_owned`を持たせる。personal outputは明示的なadoption／再検証なしではproduct evidenceにならない。

### Future profileのscope creep

Issue #354内でImplementation Briefやonboardingの詳細まで決め始める。

**対策:** 今回はregistration mechanismとhandoff recordだけを定義し、各profileのrequired inventoryやoutput schemaは後続Issueへ送る。

### Common contract変更による全profile破壊

将来profile追加時にcommon schemaを非互換変更する。

**対策:** common contractとprofile contractを別versionにする。profile追加だけではcommon versionを上げない。

## 最小handoff record

後続profile-registration Issueへ渡すrecordは、最低限次を持つ。

### Profile identity

```text
profile_id
profile_version
profile_name
product_owned
execution_surface
status
```

`status`は最低限：

```text
proposed
registered
deprecated
superseded
```

### Scope

```text
operation_goal
included_use_cases
excluded_use_cases
authority_boundary
mutation_policy
human_gate
thread_topology
```

### Context envelope requirements

```text
required_body_fields
optional_body_fields
source_identity_required
thread_mode_allowed
continuity_policy
```

### Attachment contract

```text
required_attachment_roles
optional_attachment_roles
closed_or_open_inventory
duplicate_policy
digest_basis
missing_attachment_policy
sensitive_data_policy
```

### Output contract

```text
output_contract_id
output_contract_version
output_kind
required_inventory_or_schema
extra_output_policy
validator_id
```

### Evidence and lineage

```text
parent_profile_or_common_contract
common_contract_version
derived_from_issue
decision_artifact_ids
source_head_at_registration
profile_contract_sha256
```

### Validation coverage

```text
positive_test_cases
negative_test_cases
identity_mismatch_case
missing_attachment_case
duplicate_attachment_case
wrong_output_format_case
projection_parity_required
```

## Profile registration gate

後続roleは、少なくとも次が揃うまでproduct runtimeへ追加しない。

1. `profile_id`とversionが一意
2. body minimum fieldsが定義済み
3. required attachment rolesが定義済み
4. output contractがversioned attachmentとして存在
5. validatorが契約versionへbinding済み
6. failure／fallback policyが明示済み
7. authority／mutation boundaryが定義済み
8. negative testsがある

## Scope boundary

### Issue #354に含める

* 共通contract envelope
* manifestとoutput-contract参照方式
* profile registrationの最小規則
* Clarification profile
* Planning profile
* Formal Review profile
* Semantic Revision profile
* product-owned／personal境界

### 後続Issueへ送る

* Implementation Brief profile
* onboarding固有profile
* その他reviewer role
* general advisory product role
* 新しいoutput kind
* profile discovery／registry UI
* profile migration policyの高度化

### 対象外

* personal `chatgpt-use` wrapperの動作保証
* 自由なoperator consultationの入力制限
* personal conversationの保存・retention
* personal outputの自動的なcanonical adoption

**暫定判断:** Option Aは、Issue #354をPlanning専用の局所契約に閉じず、かつ未確定roleまで実装scopeへ取り込まない。共通基盤と具体profile registrationを分離するため、将来拡張性と現在のbounded scopeを両立する。これはclarification evidenceであり、canonical採用や実装許可を意味しない。
