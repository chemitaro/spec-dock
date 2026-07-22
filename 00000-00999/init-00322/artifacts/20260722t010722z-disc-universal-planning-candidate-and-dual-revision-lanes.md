---
種別: disc
ID: "20260722t010722z-disc"
タイトル: "Universal Planning Candidate and Dual Review Revision Decision"
状態: "user-approved"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-22"
親: ["init-00322"]
authority: "current-effective decision evidence"
artifact_type: "disc"
derived_from:
  - "Initiative Candidate ZIP manual planning and review cycle"
  - "Forked analysis of ZIP and Git review modes"
  - "Human adoption decision on 2026-07-22"
reflected_to:
  - "ADR 20"
  - "Initiative Requirement／Design／Plan"
  - "Epic 1 Requirement／Design／Plan"
  - "Epic 2 Requirement／Design／Plan"
  - "Epic 3 Requirement／Design／Plan"
---

# Universal Planning Candidate and Dual Review Revision Decision

## 観測した事実

- Candidate ZIPを展開・canonical配置・commit・pushせずに、exact source branchとZIPをChatGPTへ渡すだけでPlanning／Review／Revision cycleを継続できた。
- Codexはfile selection、cross-document rewrite、Review context assemblyをほぼ行わず、ZIP受け渡しと決定的検証へ集中できた。
- 未承認Candidate versionをGit historyへ追加せずに、Red TeamとBlue Teamを分離できた。
- 反対に、軽微なliteral修正までChatGPTに完全再生成させるとoverheadが大きい。
- Implementation／Delivery ReviewはGit history、CI、semantic BASE、merge-baseを必要とし、ZIPだけでは代替できない。

## 現在有効な決定

1. Planning CandidateをInitiative／Epic／Issueへ一般化する。
2. ZIPを標準transportとするが、Git-bound Reviewを正式fallbackとして残す。
3. pre-canonical semantic iterationはCandidate ZIPを優先する。
4. canonical後のmechanical correctionはlocal edit＋commit／push＋Git-bound Reviewを利用できる。
5. canonical後のsemantic correctionはcurrent canonical stateから新Candidateを生成し、Candidate Reviewへ戻す。
6. Semantic RevisionはChatGPT Blue Team、Mechanical RevisionはMain／Codex／deterministic scriptが担当できる。
7. Red Teamはfinding／verdictだけを返し、修正しない。
8. Candidateの一byteでも変われば新version／new SHA／fresh Reviewとする。
9. Review mode／Revision laneの判断はPlanning Skillが行い、wrapperはsemantic判断しない。
10. Candidate-to-canonical parityを証明できる場合のみZIP PASSをcanonical stateへ引き継ぐ。

## Scope別default

| Scope／stage | Default | Formal alternative |
|---|---|---|
| Initiative Planning pre-canonical | archive-candidate ZIP | Git-bound fallback |
| Epic Planning pre-canonical | lightweight archive-candidate ZIP | Git-bound fallback |
| Issue Planning initial JIT | lightweight archive-candidate ZIP | Git-bound when repository integration is material |
| canonical mechanical revision | Git-bound | new archive candidate when isolation is preferable |
| canonical semantic revision | new archive candidate | isolated Git review branch when required |
| Checkpoint／Issue Delivery／PR／Epic Delivery | Git-bound | archive mode does not replace Git evidence |

## Mechanical Revision eligibility

次のすべてを満たす場合だけMechanical Revisionとする。

- 対象file／fieldがclosed set。
- old／new literalを編集前に列挙可能。
- Requirement、Architecture、slice boundary、dependency、authority、Acceptance Criteria、Gateを変更しない。
- 意味不変条件とdiff budgetを記録できる。
- 未変更fileのhashを保持できる。
- deterministic validationで完了を判定できる。

一つでも満たさない場合はSemantic Revisionへrouteする。

## 採用しない解釈

- ZIP方式とGit方式を別々の巨大Workflowとして実装しない。
- ZIP PASSを実装／Delivery Reviewへ流用しない。
- mechanicalという理由でfresh Reviewを省略しない。
- Reviewerへ修正させない。
- ZIP PASS後にclosed bindingを超える意味変更を行わない。
