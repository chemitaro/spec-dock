---
種別: ADR（Architecture Decision Record）
ID: "20260722t031603z-22-adr"
タイトル: "Content Addressed Candidate Identity and Mechanical Placeholder Oracle"
状態: "accepted"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-22"
親: ["init-00322"]
authority: "accepted"
accepted_authority: "user-directed Candidate v12 review resolution"
accepted_at: "2026-07-22"
accepted_by: "Human"
mirror_eligible: true
artifact_type: "adr"
derived_from:
  - "Candidate v12 Formal identity blocker"
  - "Candidate v12 findings RTV12-P2-001 and RTV12-P2-002"
reflected_to:
  - "Candidate identity contract"
  - "Human approval evidence contract"
  - "Placeholder materialization contracts"
  - "Fresh Reviewer Prompt"
---

# Content Addressed Candidate Identity and Mechanical Placeholder Oracle

## 位置づけ

Upload／browser transportは重複回避suffixを外部filenameへ付加し得る。Candidate v12はarchive filename自体をidentity tupleへ含めたため、bytesとSHAが完全一致してもFormal Reviewが`INSUFFICIENT EVIDENCE`となった。また、static ADRにあるliteral placeholder例と未解決dynamic placeholderを区別する機械契約が不足していた。

## ADR 化基準

- hard to reverse: yes。Review identity、Human approval、materialization parityへ影響する。
- surprising without context: yes。transport filenameは観測情報だがCandidate logical identityではない。
- real tradeoff: yes。strict external-name equalityを緩める代わりに、closed normalizationとcontent identityを強化する。

## 結論（Decision）

1. Candidateはlogical archive filenameをMANIFESTに保持し、version、logical filename、internal root、candidate ID、external ZIP SHA、source bindingでidentityを構成する。
2. transport filenameはobservational metadataであり、`<logical-stem>(<positive integer>).zip`だけをclosed aliasとして許可する。
3. alias受理にはnormalized name、ZIP SHA、internal root、MANIFEST identity、payload integrityの全一致を必要とする。
4. alias以外のrename、reconstruction、individual-file substitutionは`INSUFFICIENT EVIDENCE`とする。
5. Human署名recordとcanonical approval Evidenceはlogical filename、observed transport filename、ZIP SHAをすべて保持する。
6. unresolved-placeholder判定は`PLACEHOLDER-ORACLE-MAP.json`に列挙されたdynamic files／allowed tokensだけへ適用する。
7. map外fileはstatic exact bytesであり、literal placeholder examplesをsemantic inferenceで除外しない。
8. dynamic fileのundeclared token、render後remaining token、map外dynamic output、static hash mismatchをfail closedとする。

## 背景（Context）

ブラウザUIによる`(1)`等のsuffixはCandidate bytesを変更しない。一方、曖昧なrenameを無制限に許すと別Candidateの取り違えが起きる。そこで、transport aliasをclosed grammarで機械的に正規化し、content-addressed identityを中心に据える。

Placeholderについては、ADR 13がsyntax例を静的に説明する一方、Epic文書等は実際にrenderされる。全fileへのtoken scanは正しいstatic Artifactを拒否し、content-aware例外はwrapperへsemantic classifierを持ち込む。map-driven oracleが両問題を避ける。

## 選択肢（Options considered）

### 外部filename完全一致を必須とする

却下。upload transportがsuffixを付加する環境でReview不能になる。

### filenameを完全に無視する

却下。Human向けlogical identityと誤添付検出を弱める。

### closed transport alias＋content identity

採用。実運用に耐えつつfail-closedを維持する。

### 全Markdownのplaceholderを走査する

却下。static literal examplesを誤検出する。

### map-driven placeholder oracle

採用。動的surfaceだけを機械的に検証できる。

## 判断理由（Rationale）

- Browser transportの現実とimmutable identityを両立する。
- Human approvalをlogical filename＋SHAへbindできる。
- wrapperにsemantic classifierを導入しない。
- exact hashとclosed dynamic mapでparityを検証できる。

## 影響（Consequences）

### Positive

- `(1)`等のtransport aliasでFormal Reviewが不必要に停止しない。
- Human approvalのfilename traceabilityが強化される。
- static ADR examplesとdynamic bindingsを決定的に区別できる。

### Negative

- alias normalization、logical filename、transport filenameの記録が必要になる。
- dynamic fileを追加するたびにPlaceholder Oracle Mapを更新する必要がある。

### Follow-up

- Review wrapperへclosed alias normalizerを追加する。
- Human approval renderへlogical／transport filenameを追加する。
- Placeholder Oracleのpositive／negative fixturesを実装する。
