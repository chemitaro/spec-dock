---
種別: disc
ID: "20260726t135536z-disc-init-00322-temporary-review-perspective-and-scope-charter"
タイトル: "init-00322限定 Planning Candidate Review Perspective and Scope Charter（暫定運用判断）"
状態: "superseded"
作成者: "Codex Main"
最終更新: "2026-07-26"
親: ["init-00322"]
関連:
  - "epic-00331"
  - "iss-00334"
scope: "initiative"
scope_id: "init-00322"
authority: "explicit-human-approved-provisional-direction"
adoption_status: "superseded"
canonical_status: "non-authoritative-evidence"
effective_from: "2026-07-26"
expires_when:
  - "init-00322 is completed"
  - "the Human explicitly supersedes or withdraws this provisional direction"
disposition_at_expiry: "abandoned-as-operating-authority; retained only as historical evidence"
reuse_outside_scope: "prohibited unless separately reviewed and explicitly adopted"
source_repository: "chemitaro/spec-dock"
source_branch: "iss-00334-implement-chatgpt-issue-planning-workflow"
source_commit: "7de65ae64e15cd89290a000bdadcdd4f4ae979a3"
superseded_by: "20260727t060629z-disc-init-00322-defect-only-spec-review-charter.md"
reflected_to:
  - "20260727t060629z-disc-init-00322-defect-only-spec-review-charter.md"
---

# init-00322限定 Planning Candidate Review Perspective and Scope Charter

## 1. 位置づけ

この文書は、`init-00322`でPlanning Candidateの作成・レビュー・修正を進めるための、Human承認済みの暫定的なWorking Agreementを記録するDiscussion Artifactである。

恒久ADRではない。SpecDock全体、他Initiative、将来の標準Workflowへ自動的に適用してはならない。Canonical Requirement／Design／Plan、accepted ADR、またはHumanの後続判断と矛盾する場合は、それらを優先する。

この文書の目的は、会話コンテキストだけに存在すると揮発する次の判断を保存することにある。

- Review-driven scope ratchetを停止する。
- Reviewの本質を、P0／P1の形式条件ではなく、適切なperspective、scope、authority alignmentとして定義する。
- Red Team、Blue Team、Main、Humanの責務を分離する。
- Candidateを閉じた権威ベースラインへ戻し、必要最小限の修正だけを採用する。
- 現在の暫定案を運用しながら、より良いReview設計へ更新できる余地を残す。

## 2. 有効期間と失効

### 2.1 有効範囲

- 対象Initiative: `init-00322`
- 主対象Epic: `epic-00331`
- 現在の適用Issue: `iss-00334`
- 対象活動:
  - Planning Candidate authoring
  - deterministic preflight
  - Red Team semantic review
  - Main Finding Admission
  - Blue Team revision
  - Human Gate

### 2.2 失効条件

次のいずれかで、この文書は運用authorityとして失効する。

1. `init-00322`が完了する。
2. Humanが明示的に撤回する。
3. Humanが後継Discussion／ADR／canonical policyで置換する。

失効後はhistorical evidenceとして保持するが、他Initiativeや通常運用のdefaultとして再利用しない。

### 2.3 変更方法

この方針は暫定であり、実測に基づいて変更してよい。Materialな変更は、旧本文を黙って読み替えず、後継Artifactを作成し、このArtifactを`superseded`として参照する。

## 3. 背景と問題

Candidate v1以降のレビュー／修正サイクルでは、MainがRed Teamの自己申告したP0／P1を十分にscope判定せずBlue Teamへ渡した。その結果、Candidate適合性の確認から次第に離れ、次のscope ratchetが発生した。

- reviewabilityを高める補助情報が、product requirementへ昇格した。
- defense-in-depthの提案が、blocking requirementへ昇格した。
- shared workflowや上位architectureの論点が、Issue-local Candidateへ流入した。
- traceabilityの確認が、巨大なsource ledger、owner registry、proof matrixへ拡大した。
- 一つの矛盾を直すために、新しいstate machineやallocator subsystemが追加された。
- Candidateの品質ではなく、reviewerが想像した完全性を満たすことが目的化した。

この問題の根本は、severity labelの条件が不足していたことだけではない。レビューのperspective、scope、authority、成功条件が固定されていなかったことにある。

## 4. 基本判断

### 4.1 Reviewの本質

Reviewの第一目的は、Candidateが閉じた権威ベースラインに適合し、内部矛盾がなく、対象scopeで実行可能かを判断することである。

Reviewは次を目的にしない。

- Candidateを理想的な汎用frameworkへ再設計する。
- reviewerの好むarchitectureへ置換する。
- 将来あり得る全failure modeを現Issueで閉じる。
- 上位scopeが所有するpolicyをIssueへ追加する。
- nonblocking improvementをPASS条件へ変換する。
- 文書量、ID数、matrix数、proof数を品質指標にする。

### 4.2 Severityは二次的な表現

P0／P1は、正しいperspectiveとscopeで発見されたmaterial nonconformanceの重大度を表す補助labelである。P0／P1の形式要件だけを厳密化しても、review perspectiveがずれていればscope ratchetは防げない。

したがって、判定順序は次とする。

1. authoritative baselineを確定する。
2. review perspectiveと対象scopeを確定する。
3. findingのscope ownerを判定する。
4. Candidate適合性へのmaterial impactを判定する。
5. 最後にseverityを付与する。

## 5. 権威ベースライン

Reviewは、次の閉じた集合だけをCandidate適合性の権威ベースラインとして使う。

1. 親Epic E1-I1のOutcome、Boundary、Non-goals。
2. Human承認済み24決定 `D-001`〜`D-024`。
3. accepted ADR。
4. 現在のrepository、branch、source HEAD。
5. live guidanceが示すauthorized profile。
6. authorized profileが要求するIssue Plan schema。
7. Main Finding Admission Gateで明示的に採用されたfinding。
8. 親Epicから直接課されたPA-NF-01〜PA-NF-10等の非機能要件。

次は、それ単独では新しいauthorityにならない。

- 過去のRed Team review。
- 過去Candidateへ追加されたREQ／AC／CL。
- reviewerのbest practice。
- Candidate自身の自己申告。
- raw ChatGPT transcript。
- self-review。
- artifactのfront matter。

## 6. Review Perspective

Red Teamは、次のperspectiveを順番に適用する。

### RP-01 Authority Conformance

Candidateが権威ベースラインから直接要求されるobligationを満たしているか確認する。権威ベースラインにない新規obligationを作らない。

### RP-02 Internal Coherence

Requirement、Design、Plan、MANIFEST、CHECKSUMS、supporting artifactsの間に、実行を阻害する矛盾がないか確認する。

### RP-03 Executability

対象IssueのOutcomeを実現するために、責務、手順、検証、Human Gate、exit conditionが実行可能な粒度で定義されているか確認する。

### RP-04 Scope Ownership

findingがIssue、Epic、Initiative、shared workflow、将来改善のどこに属するか判定する。対象Candidateのscope ownerでないfindingを、Issue-local blockerとして扱わない。

### RP-05 Proportionality

問題のmaterial impactに対して、修正が必要最小限か確認する。一つの不整合を解消するために、新しいsubsystem、state machine、registry、proof systemを追加しない。

### RP-06 Evidence Integrity

Candidate identity、source binding、MANIFEST、CHECKSUMS、path safety、必須fileの存在を確認する。これはsemantic redesignから分離したdeterministic preflightで行う。

### RP-07 Human Intent Preservation

Human承認済みのOutcome、Non-goals、24決定、JIT方針、Human Gateを、形式的完全性のために弱めたり拡張したりしていないか確認する。

## 7. Review Scope

### 7.1 In scope

- Candidate ZIPに含まれる正式文書と宣言済みartifact。
- Candidateのlogical filename、Candidate ID、SHA-256、source HEAD。
- Section 5の権威ベースライン。
- 対象branch／HEAD上の、Candidateが直接変更または依存する実装・テスト・provider projection。
- Candidateが主張するacceptanceと実装計画の対応。
- 対象Issue内で解消可能な矛盾、欠落、実行不能性。

### 7.2 Out of scope

- 親Epic／Initiativeの未承認変更。
- sibling Issueや後続Issueの詳細設計。
- shared delivery／merge／finish policyの再設計。
- 将来の全consumerを想定した一般化。
- hypothetical failureに対する網羅的hardening。
- arbitraryなsource closure completeness。
- fixed ID count、matrix count、ledger countの最大化。
- reviewerの好みだけに基づくrename、cleanup、stylistic improvement。
- Candidateを汎用proof systemへ変えること。

### 7.3 Scope外findingの扱い

Scope外findingは消さず、次のいずれかへrouteする。

- `promoted_upstream`
- `deferred_advisory`
- `clarification_required`
- `rejected_overreach`

Scope外findingをBlue Teamへの修正指示へ直接変換しない。

## 8. Role Separation

### 8.1 Blue Team

- complete Candidate ZIPの作成・修正だけを担当する。
- 同一の専用ChatGPT threadを継続利用し、設計判断と修正履歴を保持する。
- MainがadmitしたfindingとScope Deltaだけを受け取る。
- 旧Candidateを上書きしない。
- 新version、timestamp、Candidate ID、internal root、MANIFEST、CHECKSUMS、ZIP SHAを持つ完全置換Candidateを生成する。
- 自己判断でP2／P3、feature request、cleanupを取り込まない。

### 8.2 Red Team

- read-only conformance reviewだけを担当する。
- Candidate、repository、patch、修正版ZIPを変更・生成しない。
- Candidate versionごとにfresh ChatGPT threadを使う。
- Review threadを修正や次回Reviewに再利用しない。
- 対象Candidate ZIPを元のlogical filenameのまま直接受け取る。
- ZIPを展開し、MANIFEST、CHECKSUMS、三文書、全宣言artifactを確認する。

### 8.3 Main

- authoritative baselineを確定する。
- deterministic preflightを実行する。
- Red Team findingをBlue Teamへ直送せず、Finding Admission Gateで判定する。
- Candidate-externalなScope Deltaを管理する。
- evidenceの採用／棄却を記録する。
- filesystem mutationとGit transactionを所有する。

### 8.4 Human

- materialなscope変更を承認する。
- ambiguityへ回答する。
- Candidate adoptionとimplementation startを承認する。
- mergeを判断する。
- この暫定方針を変更・撤回・置換できる。

## 9. Review Flow

```text
authoritative baseline
  ↓
Blue Team complete Candidate
  ↓
deterministic preflight
  ↓
fresh Red Team staged semantic review
  ↓
Main Finding Admission Gate
  ├─ accepted blocker / mechanical nonconformance → Blue Team
  ├─ upstream gap → owning scope
  ├─ ambiguity → Human
  └─ advisory / overreach → Candidate revision対象外
  ↓
new immutable Candidate
  ↓
new fresh Red Team thread
```

### 9.1 Deterministic preflight

Semantic reviewの前に、少なくとも次を機械確認する。

- logical filenameと添付filenameの一致。
- Candidate ID、version、timestamp、internal root。
- external ZIP SHA-256。
- single-root archive。
- safe path、regular file、nested archive禁止。
- MANIFEST宣言と実fileの一致。
- CHECKSUMSとfile bytesの一致。
- 必須三文書の存在。
- repository、branch、source HEAD binding。

Preflight failureはsemantic findingではなく、mechanical nonconformanceとして扱う。

### 9.2 Staged semantic review

Reviewは次の順番で行う。

1. Requirement:
   - Outcome、Boundary、Non-goals、authority、acceptanceを確認する。
2. Design:
   - Requirementを満たす責務分離、data／control flow、Human Gate、failure handlingを確認する。
3. Plan:
   - Designを実行可能なstep、test seed、delegation、exit conditionへ落とせているか確認する。

Requirementでscopeが閉じていない状態でDesignの完全性を追わない。Designが閉じていない状態でPlanのproof matrixを増やさない。

## 10. Finding記録契約

次のfieldは、P0／P1を成立させること自体が目的ではない。Review perspectiveを逸脱していないことをMainが検証するための暫定guardrailである。

Material blocker候補は次を記録する。

- `authoritative_source`
- `violated_obligation`
- `candidate_evidence`
- `material_impact`
- `scope_owner`
- `minimal_in_scope_fix`

これらが不足する場合、Mainは次を確認する。

- 単なる説明不足か。
- authorityのないfeature requestか。
- scope ownerが別か。
- material impactを示せないcleanupか。
- Candidateではなくreview contractの不備か。

field不足を機械的にFAILへ変換しない。必要に応じて`invalid_review_contract`、`clarification_required`、`deferred_advisory`へrouteする。

## 11. Finding Category

- `NONCONFORMANCE`: 明示されたauthority obligationへの不適合。
- `INTERNAL_CONTRADICTION`: Candidate内部のmaterialな矛盾。
- `MISSING_REQUIRED_OBLIGATION`: 権威ベースラインが要求する必須事項の欠落。
- `UPSTREAM_GAP`: 対象Candidateではなく上位scopeが所有する欠落。
- `AMBIGUITY`: authorityまたはHuman intentの確認が必要。
- `IMPROVEMENT`: 現状でも適合するが改善余地がある。
- `FEATURE_REQUEST`: 現在のbaseline外の追加能力。
- `CLEANUP`: 文言、命名、採番、構成上の非materialな整理。

`IMPROVEMENT`、`FEATURE_REQUEST`、`CLEANUP`はnonblockingである。`UPSTREAM_GAP`はowning scopeへrouteする。`AMBIGUITY`はHumanへの質問へ戻す。

## 12. Main Finding Admission Gate

Red Team reviewはBlue Teamへの直接命令ではない。Mainは各findingを次のいずれかへDispositionする。

- `accepted_blocker`
- `rejected_overreach`
- `promoted_upstream`
- `deferred_advisory`
- `mechanical_nonconformance`
- `clarification_required`
- `invalid_review_contract`

### 12.1 Admission判断

`accepted_blocker`にするのは、次を全て満たす場合である。

1. authoritative baselineに根拠がある。
2. Candidate内に具体的evidenceがある。
3. 対象IssueのOutcome、integrity、実行可能性、Human Gateをmaterialに損なう。
4. scope ownerが対象IssueまたはCandidateである。
5. 必要最小限のin-scope fixで解消できる。

これは厳格な形式審査ではなく、正しいperspectiveとscopeを保つための判断基準である。

## 13. Blue TeamへのRevision Contract

Blue Teamへ渡すのは次だけとする。

- `accepted_blocker`
- `mechanical_nonconformance`
- Humanが回答済みの`clarification_required`
- Candidate外部でMainが管理するScope Delta

渡さないもの:

- 未admitのRed Team finding。
- P2／P3という理由だけで自動採用された改善。
- upstream policy。
- general hardening。
- future feature。
- stylistic cleanup。

Revision Promptには、対象Candidateのlogical filename、SHA-256、Candidate ID、source HEADと、admit済みfindingだけを記載する。

## 14. Scope-reset Candidate方針

Candidate v2〜v12の追加事項を、次の観点で再分類する。

### 14.1 RETAIN

- Issue Planning walking skeleton。
- official Skill／CLI boundary。
- create／revise／review。
- dual transports／dual revision lanes。
- Human Gate、adoption、parity、publication、derived readiness。
- PA-NF-01〜PA-NF-10。
- sensitive-data protectionとdirect argv。
- provider／installed／dogfood parity。
- JIT dogfood。
- 一Issue・一branch・一PR・Human merge。
- single root、safe paths、regular files、MANIFEST／CHECKSUMS整合、content identity、source binding。
- strict Issue Plan schemaの意味的必須事項。

### 14.2 SIMPLIFY

- source binding:
  - transitive完全closureではなく、権威入力、直接関係する実装／test surface、現在HEADへ限定する。
- review isolation:
  - read-only、出力先分離、前後mutation guardへ限定する。
- publication／adoption:
  - 一貫した最小state transitionへ統合する。
- traceability:
  - Requirement→step、必須test、Human Gate、exit conditionの追跡へ限定する。
- archive safety:
  - 実際のarchive interfaceに必要な上限だけにする。
- installer verification:
  - shipped entrypoint、init／update parity、代表的失敗ケースに限定する。

### 14.3 REMOVE

- allocator lock／reservation／fsync／tombstone／crash-recovery subsystem。
- Candidate version／timestamp／ID自体をproduct ACにする構造。
- 固定件数を持つtransitive source ledger。
- AC sole-owner proof matrix。
- CL cardinality registry。
- card／gateのpytest item-ID完全一致。
- global authority inventory。
- 全resource surface applicability matrix。
- S00／G0 authority-transitionとreverse-prerequisite。
- internal self-reviewを正式PASS根拠にする構造。

### 14.4 UPSTREAM

- shared Issue delivery／report／HEAD cycle。
- PR／merge／finish semantics。
- lifecycle mutation／recovery。
- cross-Issue authority変更。
- 親Epic／Initiative architecture変更。

### 14.5 ADVISORY

- nonblocking wording／numbering cleanup。
- exhaustive defense-in-depth。
- future allocator hardening。
- parent acceptanceを超えるperformance／telemetry。
- 網羅的failure injection。

## 15. v12 Reviewの暫定Disposition

| Finding | Disposition | 扱い |
|---|---|---|
| RT-001 | `accepted_blocker` | conflicting pathを除去する。新しいstate machineは追加しない。 |
| RT-002 | `accepted_blocker`相当 | 過剰に閉じたauthorityを簡素化する。proof systemを拡張しない。 |
| RT-003 | `rejected_overreach` | generalized stricter ruleのauthorityは確認できない。具体的archive safety制約だけを保持する。 |
| RT-004 | `deferred_advisory` | wordingのみ。これ単独でCandidate revisionを起動しない。 |

## 16. authorized profile

2026-07-26時点のlive guidanceは次を示す。

- active Issue: `iss-00334`
- state: `requirement-capture`
- reason: `requirement-scaffold`
- `authorized_profile=strict`
- `lite_candidate=false`

したがって、v12の`authorized_profile=standard`は採用しない。

Scope-reset時は次の順序を使う。

1. strict前提でsubstantive Requirementを作成する。
2. `assurance classify --stage requirement`を実行する。
3. 生成された`.assurance.json`を確認する。
4. `assurance compose --artifact design|all`でDesign／Plan obligationを確定する。
5. Standardへの暗黙fallbackを禁止する。

live guidanceとclassification resultが矛盾する場合は、自動選択せずHumanへ戻す。

## 17. Candidate／Review証跡の状態

### 17.1 v1 baseline evidence

- logical filename: `20260723t091726z-iss-00334-issue-planning-candidate-v1.zip`
- SHA-256: `a7d4074a0b90cb97eed12023a3da60ed7e4a17b2f05b046b7e1af76b6e3a1b6a`
- 用途:
  - Human承認済み24決定の確認元。
  - wholesale rollback先ではない。

### 17.2 v12

- logical filename: `20260726t104913z-iss-00334-issue-planning-candidate-v12.zip`
- SHA-256: `edfd802e580d61fa2b224085700e37095f5074bf369539aef54582b299392082`
- 正式Review SHA-256: `ab829fbe069cb4b6605e515ea5ffded8cfee65179602762b7f0173d4fdd3c4e5`
- disposition:
  - immutable evidenceとして保持する。
  - scope bloatと`authorized_profile=standard`の矛盾があるため、そのまま採用しない。

### 17.3 保留中v13

- logical filename: `20260726t125220z-iss-00334-issue-planning-candidate-v13.zip`
- Candidate ID: `iss-00334-v13-20260726t125220z`
- SHA-256: `f5897ae4b1eeb81172e47625053beac609df5108b94a8148fc5592f3affa6349`
- source HEAD: `7de65ae64e15cd89290a000bdadcdd4f4ae979a3`
- disposition: `held_unadopted`
- v13 fresh Red Team review:
  - 中断済み。
  - 正式Review成果物なし。
  - admission対象外。

v1〜v12のCandidateと正式Reviewは、過去経緯のimmutable evidenceとして保持し、上書き・削除しない。

## 18. 再開条件

このArtifactの作成だけでは、Blue Team修正、Candidate生成、Red Team reviewを自動再開しない。

再開にはHumanによる次の確認を必要とする。

1. 本Artifactが暫定Working Agreementを適切に記録している。
2. Review perspective／scope／role separationを当面の運用として使ってよい。
3. 権威ベースラインとscope-reset分類を使って、新しいimmutable Candidateを作成してよい。

再開後も、次の順序を守る。

```text
MainがScope Deltaを確定
→ Blue Teamがscope-reset Candidateを新identityで生成
→ deterministic preflight
→ fresh Red Team review
→ Main Finding Admission
→ 必要な場合だけBlue Team修正
```

## 19. 未解決事項

- Review perspectiveの最終的な一般化:
  - このInitiativeの実測後に別途検討する。
- Red Team prompt／schemaの恒久契約:
  - この暫定運用をそのまま製品仕様へ固定しない。
- P0／P1 severity model:
  - perspectiveとscopeが安定した後に、必要であれば再設計する。
- 他Planning scopeへの適用:
  - Initiative Planning、Epic Planning、他Issue Planningへは自動展開しない。

## 20. 失効時の処置

`init-00322`完了時、このArtifactを運用authorityとして放棄する。

放棄時には次を行う。

- 本文をhistorical evidenceとして保持する。
- active workflow guidanceから参照しない。
- 他Initiativeへcopy-forwardしない。
- 実測で恒久化すべき知見がある場合だけ、新しいscopeで独立にレビューし、canonical docsまたはaccepted ADRへ採用する。
- 恒久化しなかった判断は、完了と同時に失効させる。

## 21. Authority precedence

衝突時の優先順位は次とする。

```text
explicit latest Human direction
→ accepted Initiative ADR / canonical Initiative docs
→ canonical Parent Epic docs / accepted Epic ADR
→ canonical Issue docs / disposition済みreport ledger
→ this provisional Discussion Artifact
→ Red Team output / Blue Team output / historical Candidate
```

このArtifactは、上位authorityを変更しない。Review／authoring時にHumanの暫定意図を再現するためのevidence surfaceとして使用する。
