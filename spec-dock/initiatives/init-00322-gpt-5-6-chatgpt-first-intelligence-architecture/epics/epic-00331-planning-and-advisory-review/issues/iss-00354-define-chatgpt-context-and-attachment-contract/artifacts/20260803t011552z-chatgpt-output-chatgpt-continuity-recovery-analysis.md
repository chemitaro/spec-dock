## 結論

**Option Aを推奨する。**

* verified same-thread resumeが成立する場合だけ既存Blue threadを継続する。
* thread unavailable／expired、repository・branch不一致、source HEAD不一致、attachment manifest不一致または不足の場合は、既存threadを正しい文脈として扱わない。
* 新規Blue threadへ完全なidentity/contextを再投入する。
* 複数の正当な復旧先がある、Candidate lineageを一意に決められない等の**曖昧性が残る場合だけHuman confirmationを要求する**。

GitHubコネクタで `chemitaro/spec-dock`、ブランチ `codex/iss-00354-chatgpt-context-contract` を再確認した。ブランチは指定HEAD `39c67ef736e34c0131b2a0e38b64085561571f49` と `identical` だった。

## 選択肢比較

### Option A — fail-closed＋曖昧時のみHuman確認

最も妥当。

安全性と運用性の境界が明確になる。

* 完全一致なら同一thread resume
* 不一致なら自動的にそのthreadを失効扱い
* 完全contextを持つ新規Blue threadを生成
* 復旧対象が一意でない場合だけ停止してHuman確認

「thread continuity」は利便性であり、source identityや添付証跡の代替ではない、という既存のauthority boundaryと整合する。現行実装もinvocationごとに新規sessionを生成し、同一session recoveryとphase横断continuityを別物として扱っている。

### Option B — 常に自動で新規Blue thread

安全性は比較的高いが、曖昧な状態でも機械的に進行してしまう。

たとえばCandidate v1／v2のどちらをcurrentとすべきか確定できない場合、完全contextを再送しても、誤ったlineageを完全に再現するだけになり得る。したがって「自動再作成できる条件」を厳密に定義しないOption B単独は不十分。

Option Aの非曖昧ケースにおける動作として内包するのが適切。

### Option C — すべてHuman確認

最も保守的だが過剰。

単純なthread expiryや、manifest hashの機械的な不一致まで毎回Human gateにすると、復旧可能な技術的失敗を人間判断へ押し戻す。Planning／Revisionの反復性を損ない、同一Blue threadを採用した利点も小さくなる。

## 推奨する一問

> Blue threadを検証済みの同一threadとして再開できない場合、既存threadをfail-closedで失効扱いにし、完全なidentity/contextを持つ新規Blue threadへ移行し、Candidate lineageなどが一意に確定できない場合だけHuman confirmationを要求するOption Aを採用しますか？

選択肢は次の三つで十分である。

* **A（推奨）**: verified resumeのみ許可。不一致時は完全contextで新規Blue thread。曖昧時のみHuman確認
* **B**: 不一致時は常に完全contextで自動的に新規Blue thread
* **C**: 不一致・失効の種類を問わず毎回Human確認

## 主なfailure mode

* **stale source continuation**
  threadが旧HEADの判断を保持したまま、現在HEADのPlanning／Revisionとして続行する。

* **cross-repository／cross-branch contamination**
  同じIssue番号や類似名称を理由に、別repository／branchのthreadを再利用する。

* **manifest drift**
  ファイル名が同じでも内容やSHAが変わっている、または必須添付が欠落している。

* **Candidate lineage confusion**
  Candidate v1のReview結果を、v2または別Candidateの修正根拠として扱う。

* **partial-context recovery**
  thread作成失敗後、短い本文だけを再送し、canonical資料やformal evidenceなしで続行する。

* **silent thread substitution**
  continuity失敗を記録せず、新規threadを同一threadの継続として扱う。

* **unnecessary Human blocking**
  一意に機械判定できるexpiryやhash mismatchまでHumanへ確認し、workflowを停滞させる。

## 最小evidence fields

### Source identity

```text
repository
branch
source_head
issue_id
parent_epic_id
parent_initiative_id
```

### Thread identity

```text
blue_thread_id
thread_created_at
thread_last_verified_at
thread_status
previous_blue_thread_id
resume_mode = same_thread | new_thread
resume_reason
```

`thread_status` は最低限 `active | expired | unavailable | identity_mismatch | superseded` が必要。

### Context identity

```text
context_contract_version
operation_role
operation_id
attachment_manifest_sha256
required_attachment_count
required_attachment_names
```

manifest自体には、各添付について最低限次を持たせる。

```text
logical_name
classification
source_label
sha256
required
```

現行の添付分類は `review-target`、`supplemental-context`、`formal-evidence` であり、SHAも算出されているため、この方向への拡張は既存構造と整合する。

### Candidate／Review binding

Planning前でCandidateが存在しない場合は省略可能。存在する場合は必須。

```text
candidate_id
candidate_sha256
candidate_version
formal_review_id
formal_review_sha256
formal_review_verdict
reviewed_candidate_id
```

### Decision evidence

```text
verification_result
mismatch_fields
ambiguity_detected
human_confirmation_required
human_confirmation_record_id
```

Human確認は、`ambiguity_detected=true` の場合に限定すべきである。

## fail-closed判定

次のいずれかならsame-thread resumeを拒否する。

```text
thread unavailable or expired
repository mismatch
branch mismatch
issue_id mismatch
source_head mismatch
attachment_manifest_sha256 mismatch
required attachment missing
Candidate identity mismatch
formal Review binding mismatch
```

ただし、`source_head mismatch` はIssue処理全体の永久停止を意味しない。旧threadの継続を拒否し、最新HEADの完全contextを再取得して、新規Blue threadを構成するためのトリガーとする。

**暫定判断:** Option Aは、採用済みのBlue継続／fresh Red分離を維持しながら、古い会話履歴を暗黙の正本にしない最小の復旧契約である。これはadvisory evidenceであり、canonical採用を意味しない。
