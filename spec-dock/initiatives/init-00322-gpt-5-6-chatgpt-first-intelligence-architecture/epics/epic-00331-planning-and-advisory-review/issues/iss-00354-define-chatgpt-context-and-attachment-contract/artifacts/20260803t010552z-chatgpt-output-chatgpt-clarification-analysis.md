## 1. 確認できた事実

* GitHub コネクタで `chemitaro/spec-dock` を開き、ブランチ `codex/iss-00354-chatgpt-context-contract` の存在を確認した。
* 指定 HEAD `39c67ef736e34c0131b2a0e38b64085561571f49` と同ブランチを比較した結果は `identical`、`ahead_by=0`、`behind_by=0` だった。したがって、以下はこの exact HEAD に対する分析である。
* Issue #354 は OPEN であり、目的は Planning／Review／Revisionおよび一般的な ChatGPT 利用について、本文・添付・厳密添付・秘匿情報除外・出力契約を明示することにある。既存 Planning ライフサイクルの再設計、Candidate 履歴の上書き、ChatGPT によるリポジトリ変更は対象外である。
* prompt synthesis は、repository、branch、source HEAD、Issue 階層、依存情報、canonical paths、関連 source paths、operator contextを動的 identity として本文へ合成する。exact GitHub branch／HEAD の検証、default branch 代替禁止、添付の非権威性、role-specific output expectationも本文に固定されている。
* 添付分類は現状 `review-target`、`supplemental-context`、`formal-evidence` の三種類である。Planner／Semantic Revision は三文書と onboarding companion を含む単一 ZIP、Reviewer は閉じた JSON を返す契約になっている。
* Oracle adapter は invocation ごとに新規 session ID を生成する。同一 invocation の timeout／disconnectには同一 session の harvest・pollで復旧するが、phaseをまたいで既存 conversationへ follow-upする機構は確認できない。
* 本分析は clarification advice であり、canonical文書の採用・変更・実装許可を意味しない。これは添付された分析プロンプトの authority boundary と一致する。

## 2. 本文と添付の不足・矛盾

「短いゴール・identity・禁止事項を本文、詳細資料・正本・証跡を添付」という基本分離は妥当である。ただし、その二分法だけでは、Planning、Formal Review、Semantic Revisionを再現可能かつ安全に運用するには不足する。

### 本文に必須とすべき情報

本文は、人間向けの依頼要旨だけでなく、少なくとも次の**実行境界**を持つ必要がある。

* `operation_id` または phase と turn を一意に識別する ID
* role：`clarification | planner | reviewer | semantic_revision | general`
* repository／branch／source HEAD
* Issue／Epic／Initiative identity
* thread mode：`new | continue`
* 継続対象の論理 thread identity
* 添付 manifest の digest
* output expectation
* mutation・authority・fallback禁止事項

これらを添付だけに置くと、「添付欠落時に誤った role や branch で続行する」ことを本文単独では防げない。

### 添付側に不足する情報

現行の分類と SHA は有用だが、継続スレッドを導入する場合は次が必要になる。

* 添付ごとの `logical_role`
* `required | optional`
* `exact_bytes | normalized_text` の digest方式
* `applies_to_phase`
* `supersedes` または revision lineage
* Candidate／Review／source identityとの binding
* 添付欠落・重複・旧版混在時の停止条件
* confidentiality classification
* retention／再送ポリシー

特に `supplemental-context` は意味範囲が広すぎる。一般資料と「回答の正しさに必須だがレビュー対象ではない資料」を同じ分類にすると、欠落を fail-closed にすべきか判断できない。

### material な矛盾

最大の矛盾は、「同じ threadを継続する」という要求と、現行 adapter が invocation ごとに新規 sessionを作る事実である。同一 invocation 内の recovery は thread continuityではない。

また、継続 threadに過去の添付内容が残っていても、現在の入力として再検証されたことにはならない。したがって、**会話履歴は利便性のための文脈であり、current identity／exact evidenceの代替ではない**と明記すべきである。

一般 ChatGPT 利用への共通化では、Planning 固有の Candidate／canonical pathsを共通 schemaへ直埋めするのではなく、最小共通 envelope と phase-specific extensionに分ける必要がある。

## 3. スレッド継続トポロジーの選択肢

### Option A — Blue継続、RedはCandidateごとにfresh（推奨）

* Clarification、Planning、Semantic Revisionは一つの Issue-local Blue threadで継続する。
* Candidate vNごとに Formal Red Team Reviewを新規 read-only threadで行う。
* Red threadには対象Candidate、identity、SHA、canonical source、review contractだけを渡す。
* FAIL時は正式 Review JSONのみをBlue threadへ戻す。
* Candidate vN+1はBlue threadで生成し、再び別のfresh Red threadでレビューする。

これは、ユーザーの再説明負荷を下げつつ、fresh Review、immutable Candidate、Blue／Red分離を保持する。

### Option B — Issue全体を一つのthreadで継続

Blue／Redを同じthreadに置く。文脈再利用は最大になるが、RedがCandidate生成過程、Blueの自己弁護、過去の修正意図に影響される。既存のfresh read-only Reviewを実質的に弱めるため、Issue #354の局所変更ではなく上位 review protocolの改訂が必要になる。非推奨。

### Option C — Clarificationのみ継続

Clarificationだけ同一threadとし、Planning、Revision、Reviewは毎回freshにする。現行 adapterとの差分は小さいが、PlanningとRevisionで大量の文脈を再送するため、ユーザー意図を十分には満たさない。

### Option Aで必要なidentity binding

Blue threadの継続可否は、少なくとも次の組で判定すべきである。

```text
repository
branch
issue_id
blue_thread_id
current_source_head
current_candidate_id（存在する場合）
attachment_manifest_sha256
last_accepted_operation_id
```

repository／branch／Issueが変われば継続禁止。HEAD変更時は無条件停止ではなく、新しいHEADを明示して完全なidentity再検証を行う。Candidate identity不一致はfail-closedとする。

## 4. 推奨する一問

**Issue #354では、どのスレッド境界を採用しますか？**

* **A（推奨）**: Clarification・Planning・Semantic Revisionは同一Blue thread、Formal ReviewはCandidateごとにfresh Red thread
* **B**: Blue／Redを含むIssue全体を同一thread
* **C**: Clarificationだけ同一thread、Planning・Revision・Reviewは毎回fresh

この一問が決まれば、thread handleの所有者、identity binding、Review隔離、fallback、テスト境界を具体化できる。添付インタビュー案も同じ判断点を特定している。

## 5. 明確化の次手

1. **上記A／B／Cの回答を記録する**
   記録物：Issue-local `interview` artifact。回答原文、回答日時、採用状態、対象Issueを保持する。

2. **thread continuity失敗時の規則を確定する**
   推奨初期値：既存threadへ接続できなければ、新規threadを作成し、current identityと必須添付を完全再送する。過去会話だけを根拠に続行しない。
   記録物：短い `disc` または同判断に付随する adoption note。

3. **context envelopeを例示する**
   共通部とphase-specific部を分け、少なくとも role、source identity、thread mode、manifest digest、output expectation、authority boundaryを含める。
   記録物：非canonicalな schema example。まだ実装 schemaとして固定しない。

4. **phaseごとのattachment matrixを作る**
   各ファイルについて classification、requiredness、digest basis、identity binding、欠落時挙動を表にする。
   記録物：source-grounded researchまたはdiscussion artifact。

5. **edge-case acceptance evidenceを列挙する**
   対象は、旧HEAD継続、Candidate取り違え、manifest不一致、添付欠落、Red thread再利用、thread handle喪失、別repositoryへの誤接続。
   記録物：canonical三文書 authoring時に採用判断できる acceptance-evidence候補。

この順序なら、回答前に `requirement.md`、`design.md`、`plan.md`を先行作成せず、必要な人間判断だけを最小化できる。

## 6. 未検証事項

* Oracle CLIまたはbrowser transportが、既存 conversationへの安定した follow-up handleを正式に提供するか。
* conversation handleの保持期間、失効条件、browser profile間の可搬性。
* follow-up時に添付を追加・置換した場合、ChatGPT側で旧添付との区別を確実に維持できるか。
* thread IDを証跡へ保存する際の秘匿性・ログ露出・retention要件。
* プロンプトで想定されている「GPT-5.6 Luna／maximum reasoning」というモデル指定。確認できた実装は Oracleへ `--model Pro` と browser-side selectionを渡しているだけであり、特定モデル名や reasoning levelを保証していない。
* Issue bodyでは親Issueが `#334`、対象Epicが `epic-00331` と記載されている一方、分析プロンプトは parent Epicを直接指定している。これは必ずしも矛盾ではないが、canonical lineage生成時には `#334` と `epic-00331` の関係をrepository上の正本から再確認する必要がある。
