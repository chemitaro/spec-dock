---
種別: ADR（Architecture Decision Record）
ID: "20260722t010722z-20-adr"
タイトル: "Universal Planning Candidate with Dual Review Transports and Dual Revision Lanes"
状態: "accepted"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-22"
親: ["init-00322"]
authority: "accepted"
accepted_authority: "user-approved in this ChatGPT thread"
accepted_at: "2026-07-22"
accepted_by: "Human"
mirror_eligible: true
artifact_type: "adr"
derived_from:
  - "Initiative Planning Candidate ZIP dogfooding"
  - "Universal Planning Candidate analysis"
  - "Human decision to support both ZIP-bound and Git-bound Planning Review"
reflected_to:
  - "requirement.md"
  - "design.md"
  - "plan.md"
  - "Epic 1 Requirement／Design／Plan"
  - "Epic 2 Requirement／Design／Plan"
  - "Epic 3 Requirement／Design／Plan"
---

# Universal Planning Candidate with Dual Review Transports and Dual Revision Lanes

## 位置づけ

Initiative Planningで採用したCandidate ZIP方式は、Node不在への迂回策に留まらず、未承認Planning文書をGitへ置かず、ChatGPTの横断分析能力を利用し、Codexの希少な認知資源を決定的操作へ集中させる有効な方式である。一方、canonical path、CI、GitHub inline review、merge-base等の実Git状態を必要とする場合はGit-bound Reviewが適する。

本ADRは、ZIPだけを唯一のWorkflowにせず、Initiative／Epic／Issue Planningへ共通のPlanning Candidate lifecycleを導入し、Review transportとRevision executorを独立した二軸として定義する。

## ADR 化基準

- hard to reverse: yes。Initiative／Epic／Issue Planning Skill、Review wrapper、Human Gate、canonical adoption順序へ影響する。
- surprising without context: yes。Gitへ配置せずFormal Reviewでき、かつGit-bound Reviewも同格の正式modeとして残す。
- real tradeoff: yes。Candidate／parity管理の固定費と引き換えに、未承認Git履歴、Codex token、複雑な展開／commit／push cycleを削減する。

## 結論（Decision）

1. Initiative、Epic、IssueのPlanning成果物を、canonical adoption前のimmutable **Planning Candidate**として扱う。
2. Planning CandidateのFormal Review transportは二つを正式に支援する。archive modeのlogical filenameはMANIFEST authorityであり、transport filenameのclosed`(N)`aliasはcontent identity一致時だけ許可する。
   - `archive-candidate`: exact ZIP SHAとexact source repository／branch／HEADへbindする。標準transportである。
   - `git-bound`: repository／branch／reviewed HEAD／target paths／必要なBASEまたはmerge-baseへbindする。正式fallbackである。
3. Initiative Planningは`archive-candidate`をdefaultとする。Epic／Issue Planningもpre-canonicalのsemantic iterationでは軽量Candidate ZIPをdefaultとし、Git上のpath／CI／複数Human inline review等が必要な場合だけ`git-bound`を選べる。
4. Implementation、Checkpoint、Issue Delivery、PR、Epic DeliveryのReviewはGit history／CI／merge-baseが対象であるため`git-bound`を原則必須とする。
5. Candidate packageはScopeごとに最小化する。
   - Initiative: Thin Initiative Bundle、全Epic Bundle、全Issue Boundary Map、dependency、ADR、materialization contract。
   - Epic: Epic三文書、Issue Boundary Map、関連ADR、source baseline、manifest／checksums。
   - Issue: Issue三文書、source baseline、manifest／checksums。
6. Planning CandidateのRevision laneを二つに分ける。
   - **Semantic Revision**: Requirement、Architecture、slice boundary、dependency、authority、Acceptance Criteria、Gate／Workflow等の意味変更。ChatGPT Blue Teamが完全な新Candidateを生成する。
   - **Mechanical Revision**: typo、front matter delimiter、exact path、literal count、closed placeholder、link、manifest／checksum等、意味判断不要かつ変更対象が事前に閉じる修正。Main／Codex／deterministic scriptが実行できる。
7. Mechanical Revisionは、編集前に対象path、field、old value、new value、意味不変条件、diff budgetを列挙できる場合だけ許可する。一つでも列挙できなければSemantic Revisionへrouteする。
8. どちらのRevision laneでもCandidate bytesが変われば、新version、新filename、新internal root、新MANIFEST identity、新外部SHA、fresh independent Red-Team Reviewを必須とする。
9. Red Teamは常にreview-onlyであり、Candidate、canonical file、patch、revised ZIPを生成しない。
10. SkillがReview modeとRevision laneを意味判断する。Script／wrapperはidentity、attachment、safe extraction、hash、parity、Oracle invocation等の決定的処理だけを担う。
11. Review PASS後にはScope-specific positive Human Gateを必須とし、Issue Scopeではexact reviewed identityへbindされたHuman Issue Plan Adoption and Implementation-Start Authorization、mode-specific canonical／commit parity、required validation／planning publication後にだけ`execution-ready`へ進む。
12. Reviewed Candidateをcanonicalへ採用した後、source HEAD不変、closed binding、byte／semantic parity、Candidate外変更0、validate／sync PASSを証明できる場合、同じ内容への二度目の完全Semantic Reviewは不要とする。
13. 上記parityを証明できない、source HEADが変化した、Candidate外fileを変更した、closed bindingを超えた、validation対応で意味変更した場合は、new Candidateまたはfresh Git-bound Reviewへ戻る。
14. Placeholder final parityは`PLACEHOLDER-ORACLE-MAP.json`のdynamic file／tokenだけを検査し、static exact-hash fileのliteral examplesをsemantic inferenceしない。
15. ADR 13のexact immutable ZIP、Human SHA approval、Red／Blue separationは`archive-candidate` modeで維持する。本ADRはZIPをInitiative専用／唯一方式とする解釈を拡張し、上位のPlanning Candidate抽象を定義する。

## 背景（Context）

Initiative Candidateを複数回Review／Revisionした実運用では、ZIP一つをPlannerとReviewerへ渡すだけで、未承認文書の配置、commit、pushを行わず高度な横断Reviewを継続できた。これによりCodexはfilesystem／Gitの決定的処理へ集中できた。一方、軽微な修正までChatGPTへ完全再生成させることや、実repository path／CIが必要なReviewをZIPへ強制することは過剰である。

## 選択肢（Options considered）

### 全ScopeをGit-firstに固定

却下。未承認Planning文書とFAIL revisionがGit historyへ残り、Codex操作とtoken消費が増える。

### 全ScopeをZIP-onlyに固定

却下。CI、merge-base、path-based tooling、複数Human inline review、canonical post-adoption correctionに弱い。

### InitiativeだけZIP、Epic／Issueは常にGit-first

却下。Candidate-firstの一般的利点を下位Scopeで失い、Scopeごとに不必要に異なるWorkflowを維持する。

### Universal Candidate＋dual transport＋dual revision lanes

採用。意味作業をChatGPTへ、決定的作業をMain／Codex／scriptへ分離し、必要時だけGit実状態をFormal Review unitにできる。

## 判断理由（Rationale）

- Codexの希少tokenとcontextを、semantic file selection／cross-document rewritingではなくWorkflow制御へ集中できる。
- 未承認Candidateをcanonical repositoryへ入れずにReviewできる。
- 軽微な修正を決定的local editへrouteしつつ、immutable Review identityを維持できる。
- ZIP PASSからcanonical adoptionへcandidate-to-canonical parityを証明できる。
- Implementation／DeliveryのGit-based Review semanticsを弱めない。
- Script側へsemantic classifierを実装せず、Skill knowledgeで運用を改善できる。

## 影響（Consequences）

### Positive

- Initiative／Epic／Issue Planningの共通mental modelが得られる。
- archive reviewとGit reviewを用途に応じて選べる。
- Red／Blue Team分離が維持される。
- Candidate失敗履歴がcanonical Git historyを汚さない。
- mechanical fixのoverheadを抑えられる。

### Negative

- Candidate package、manifest、checksum、parityの固定費がScopeごとに発生する。
- mode／lane誤選択を防ぐSkill contractとReview regressionが必要になる。
- ZIP Review PASS後のdeterministic adoptionを証明できない場合はGit-bound再Reviewが必要になる。

### Follow-up

- Initiative／Epic／Issue Planning Skillへmode selectionとlane classificationを組み込む。
- Review wrapperへ`archive-candidate`と`git-bound`の入力modeを追加する。
- Scope別Candidate templateを最小構成で用意する。
- Candidate-to-canonical parity fixtureとunexpected-change detectionを実装する。
