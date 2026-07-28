---
種別: 実装報告書（Issue）
ID: "iss-00334"
タイトル: "Implement ChatGPT Issue Planning Workflow"
関連GitHub: ["#334"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-27"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00331", "init-00322"]
---

# iss-00334 Implement ChatGPT Issue Planning Workflow — 実装報告

本書は Issue の観測証跡台帳である。planned requirements と implementation sequence は `requirement.md`、`design.md`、`plan.md` が所有し、本書は採用判断、reviewer verdict、実行結果、commit evidence を時系列で記録する。

2026-07-27、Humanはレビュー／修正ループによるPlanning肥大化を停止し、Blue Teamの設計前提を尊重するdefect-only reviewへ戻すよう指示した。Mainは、過去のreview由来の証明行列、重複closure graph、将来拡張向けcontractを正本から除き、四command、exact Git binding、Candidate、fresh review、Human Gate、安全なapply／publication、provider-first、JIT dogfoodに絞って三文書を再基準化した。前回の4 findingは実害を再判定し、public result、revision input、git-bound exact targets、Seed routingの四点だけを簡潔な契約として反映した。

snapshot `a0d1b4dedf68f1957a01d1fd48cd2e3a1be64b03`へのfresh defect-only ChatGPT ReviewはP0=0、P1=1のFAILだった。P1-01は親Epic E1-REQ-005に対し、P2／P3-only Reviewでもrevisionし得る直接矛盾であったため採用した。revision triggerをP0／P1だけに限定する最小修正を行った。

correction snapshot `ec801c374038e7e5ad4f31b3919440aa9b79eeaa`への別fresh closure ReviewはP0=0、P1=0のPASSで、P1-01 closed、direct regressionなしと判定した。これをcurrent Spec Authoring Gateの正式PASSとして採用する。製品実装はまだ開始していない。

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger / 必須）

| 識別子（ID） | 状態（Status） | 種別（Type） | 起票元（Raised By） | 契機 / 差分（Gap） | 検討した選択肢 | 判断 / 解釈 | 根拠（Rationale） | 処置（Disposition） | 証跡（Evidence） | フォローアップ（Follow-up） |
|---|---|---|---|---|---|---|---|---|---|---|
| D-20260726-RT001 | resolved | implementation | fresh Red Team v14 | Issue Candidate ZIP の生成 owner と create→archive review integration test が未確定 | generic packへ再構成; Issue-local packaging責務を追加 | Planner response と runtime packaging を分離し、S05を唯一の packaging owner とする | 親仕様と ADR 20 の package 義務を最小の Issue-local responsibility で閉じる | applied | `artifacts/20260726t153105z-disc-v14-red-team-finding-admission.md`; `artifacts/20260726t164628z-chatgpt-output-v15-fresh-red-team-review.md` | canonical planningへ採用済み |
| D-20260726-RT002 | resolved | scope | fresh Red Team v14 | review運用中のsame-thread continuityを恒久product contractへ昇格するか | session locatorを製品契約へ追加; 運用限定で維持 | Initiative限定の運用とし、product contractへ昇格しない | temporary charterを恒久要件へ昇格すると scope overreach になる | rejected | `artifacts/20260726t153105z-disc-v14-red-team-finding-admission.md` | product変更なし |
| D-20260726-RT003 | resolved | compatibility | fresh Red Team v14 | generic archive primitive再利用とS05 allowlistが両立しなかった | validator複製; private helper依存; bounded extension | named data-only contractを追加し、generic defaultをcharacterization testで保護する | 既存contractを再利用しつつIssue固有identityを閉じられる | applied | `artifacts/20260726t164657z-disc-v15-red-team-pass-admission.md` | S05で実装・検証する |
| D-20260727-V15-ADOPTION | resolved | operation | Human / Codex Main | PASS済みCandidate v15をcanonical pathsへ配置する | internal rootをそのまま置く; 転記; whole-file replacement | 三文書をbyte-for-byte置換し、supporting artifactsとexact ZIPをIssueへ配置した | Humanの正式配置指示、ZIP SHA、source blob parity、fresh Red PASSを確認した | applied | `artifacts/20260726t225541z-disc-v15-human-adoption-decision.md`; ZIP SHA-256 `07a2c240c9d2edee5faa58f0ad4ab09b05b542dba2e1a8d61234d479c0355fbd` | canonical reviewで独立検証する |
| D-20260727-SR001 | resolved | implementation | system-architect / spec-reviewer | Human Gate後のsupported lifecycle routeがなかった | hidden application API; Core CLI sequence; ChatGPT CLI subcommand | `spec-dock-chatgpt planning apply` を唯一の公開 late-lifecycle route とする | Skillから明示的に呼べ、mode identity、Human decision、expected HEAD、external outputを一契約で固定できる | promoted_to_design | `design.md` Public Command Design; `plan.md` S01／S06 | fresh canonical re-review |
| D-20260727-SR002 | resolved | operation | system-architect / spec-reviewer | multi-file adoptionのcrash／rollback／retry意味論がなかった | private helper依存; primitive複製; shared transaction抽出 | `scoped_file_transaction.py` を抽出し、pre-commit rollbackとpost-commit publication resumeを分離する | commit済みcanonical historyをforce/resetせず、同一operationを安全に再開できる | promoted_to_design | `design.md` Apply State Machine／Transaction Boundary; `plan.md` S06 | fault-injection testsで閉じる |
| D-20260727-SR003 | resolved | test-strategy | implementation-planner / spec-reviewer | archive classとClosure Indexが集約され未閉鎖を検出できなかった | representative cases; class別closure | REQ-022の25 class、REQ／AC／EC、PA-NF、Design riskを個別required rowにする | material obligation単位で入力、期待値、bug class、owner、evidenceを再現できる | promoted_to_plan | `plan.md` Spec-Locked Closure Index／S05 | 各required rowをReportへ閉包する |
| D-20260727-SR004 | resolved | scope | implementation-planner / spec-reviewer | S02 test ownershipとS09 live mutation boundaryが矛盾した | allowlist拡大; step分割 | S02A docs／S02B test、S09A hermetic／S09B Main-Human live gateへ分割する | role、mutable surface、credential boundaryを一致させる | promoted_to_plan | `plan.md` S02A／S02B／S09A／S09B | step順に実行する |
| D-20260727-SR005 | resolved | operation | Codex Main | standard assuranceとIssue固有の高リスクcontrolsの差分を明示する必要があった | profileを無根拠にstrictへ変更; standardのみ; issue-local overlay | authorized profileはstandardのまま、archive、transaction、public contract、live mutationにstrict相当のissue-local overlayを適用する | classifier authorityを改変せず高リスク面のclosureを強化できる | applied | `.assurance.json`; `requirement.md`; `design.md`; `plan.md`; 本書 Assurance記録 | reviewed amendmentで高リスク面が消えた場合だけoverlayを解除する |
| D-20260727-CG006 | resolved | contract | dedicated ChatGPT Blue Team | apply evidence schema、mode-neutral start gate、S01 positive oracle、S03 test ownershipが未閉鎖だった | ad-hoc JSON; Candidate-only gate; generic Git test流用; closed named contracts | `ReviewedPlanningIdentityV1`、`PlanningReviewResultV1`、`PlanningHumanDecisionV1`をclosed contract化し、archive／git-bound双方を同じdual authorization gateへ通す | exact bytes／identity／digest bindingとstatus semanticsを実装前に固定し、P1／P2をtestable closureへ変換できる | applied | `artifacts/20260727t014215z-chatgpt-blue-bounded-correction.md`; `design.md` §§3,4.3–4.6,10; `plan.md` S01／S03／S06 | remote snapshotを別fresh ChatGPT reviewerへ渡す |
| D-20260727-CG007 | resolved | contract | fresh ChatGPT Red Team / dedicated ChatGPT Blue Team | EC-005 status、public CLI identity、negative decision、Candidate controls、secret preflight、multi-owner closure、recovery lookupが未閉鎖だった | status unionを維持; broad authority registry; representative schema test; closed bounded contracts | approved adoptionとdurable rejected decision-recordを分離し、`revoked`をv1外へ置く。CLI／Candidate controls／security／closure portion／recovery workspaceをexact contract化する | RedのP1-12〜P1-16とP2-03／P2-04を、既存境界とone-Issue/one-branch/one-PRを維持して実証可能な契約へ変換する | applied | `artifacts/20260727t022302z-chatgpt-fresh-canonical-review-fail.md`; `artifacts/20260727t024714z-chatgpt-blue-bounded-correction-followup.md`; current三文書 | exact new remote HEADで別fresh Red reviewを行う |
| D-20260727-OP008 | resolved | operation | Codex Main | fresh Red promptに実在しない40文字SHAを指定した | 仕様変更; review破棄; 実行証跡として是正 | 製品仕様は変更せず、実際にreviewされたbranch HEADをFAIL evidenceとして保持し、次回は`git rev-parse HEAD`の実値をそのまま指定する | reviewerは実在するbranch HEADを解決して内容をreviewしたが、requested identity mismatch自体はblockingだった | recorded | Red artifact P1-11; requested `546245f1b0a7f8fe616fe6f13b6f4534f40d77cc`; actual `546245f1072e6d7822fc7885eff814ac1eca1dc5` | commit／push後のactual full HEADを再取得してfresh reviewへ渡す |
| D-20260727-CG009 | resolved | contract | fresh ChatGPT Red Team / same dedicated Blue Team | public status／PA-NF count、stage-only wrong-output recovery、Closure owner graph、published milestone ledgerが未閉鎖だった | status union維持; broad workspace registry; Final Exit owner portion; bounded deterministic correction | named statusを一意化しPA-NFを11 fixtureへ分割する。stage-only clean-H0 orphanとrepository-visible recoveryを分離し、broad registryなしでsame-output cleanup／wrong-output stopを定義する。summary aliasをstatelessに戻し、required owner graphをS99で閉じてからFinal Exitへhandoffする | Red findingsを実装前にtestableかつacyclicなowner contractへ変換し、P1-11〜P1-16とone-Issue／one-branch／one-PR境界を維持する | applied to bounded correction | `artifacts/20260727t033431z-chatgpt-fresh-canonical-review-fail.md`; `requirement.md`; `design.md`; `plan.md`; `report.md` | correctionをcommit／pushし、actual new full HEADで別fresh Red review |
| D-20260727-RB010 | resolved | scope | Human / Codex Main | successive reviewが改善提案をblocking defectとして取り込み、三文書が実装対象より大きくなった | 既存文書へさらに4 findingを追加; v15へ全面回帰; approved product boundaryを保った簡潔な再基準化 | approved product boundaryを維持し、実害のあるpublic result、revision input、git-bound target、Seed routingだけを閉じる三文書へ再基準化する | reviewは設計を行わず、具体的な矛盾・欠落だけを確認するというHuman指示とInitiative限定charterに一致する | applied | Initiative artifact `20260727t060629z-disc-init-00322-defect-only-spec-review-charter.md`; current三文書 | commit／push後、限定したfresh reviewを一度実施する |
| D-20260727-DR011 | resolved | contract | fresh defect-only ChatGPT reviewer | P2／P3-only ReviewでもS07がrevisionを起動でき、親Epic E1-REQ-005と矛盾した | finding全件でrevision; P0／P1だけでrevision | P0／P1だけをrevision triggerとし、P2／P3-onlyではCandidate不変とする | current design内のseverity gateだけで直接矛盾を解消できる | applied | `artifacts/20260727t070247z-chatgpt-defect-only-review-fail.json`; current三文書 | exact correction HEADでclosure review |
| D-20260727-EX012 | resolved | execution | runtime guidance / Human | plan内容はS01〜S07を持つがexecutable markerとstep具体化入力の保存契約がなく`plan-not-executable`だった | runtimeを迂回; 全stepを再肥大化; step開始前ChatGPT artifact契約を明記 | S01〜S07を実装ステップとして明示し、各step直前のChatGPT具体化artifactをbounded worker inputにする | Humanの実行指示を満たし、canonical scopeを拡張せずJIT具体化できる | applied | `plan.md#実装ステップ`; runtime guidance `plan-not-executable` | assurance再束縛後にguidance readyを確認 |
| D-20260728-S03-JIT | resolved | implementation | Human JIT contract / ChatGPT Pro | S03の文書抽出、Candidate identity、control schema、ZIP publicationに実装可能な符号化規則が必要だった | canonical amendment; 過去の拡張schema復活; bounded implementation-local v1 | 12項目をすべてimplementation-localと分類し、public semanticsやS04以降を変えない最小v1 encodingをS03 work packetで固定する | D-20260727-EX012は各step直前の具体化artifactを実装入力とし、D-20260727-RB010はcanonical planningの再肥大化を禁じる | applied as execution input | `artifacts/20260728t020250z-s03-chatgpt-implementation-work-packet.md`; source HEAD `530cca24943892dd440ca67823a9d68dfc46763d` | bounded dev-coderへ渡し、observed evidenceを記録する |
| D-20260728-S04-JIT | resolved | implementation | Human JIT contract / ChatGPT Pro | S04 initial packetはexact Review ingress、Mechanical Review binding、conversation continuity、diff budget unitをmaterial product gapとして停止した | canonical schema／CLI amendment; hidden evidence lookup; bounded internal execution input | exact Reviewをapplication-only evidence inputで明示し、Mechanicalは同Candidateのblocking Reviewをapplication gateにする。durable session identityを追加せずself-contained invocationを使い、diff budgetをdeleted＋inserted UTF-8 bytesとする | D-20260727-EX012のstep-local encoding、D-20260727-RB010のno-regrowth、D-20260726-RT002のdurable session contract却下、S04／S06 ownershipを同一ChatGPT conversationで再照合した | applied as execution input | `artifacts/20260728t033850z-s04-chatgpt-implementation-work-packet.md`; source HEAD `18006b779c70cdb13e4e5baae29ac3d79e77a954` | 17-path bounded dev-coderへ渡し、public/parser/schema変更が必要なら停止する |
| D-20260728-S05-JIT | resolved | implementation | Human JIT contract / ChatGPT Pro | S05のdual authorization、whole-file adoption、decision-only rejection、transaction rollback、planning-only commit、publication retryを実装可能な一つの境界へ具体化する必要があった | generic Git lifecycle拡張; canonical amendment; S05-local orchestration／transaction adapter | 既存S01〜S04 contractsを変更せず、application orchestrationとS05-local infra adapter、exact 5-path allowlistで閉じる | ChatGPT ProがGitHub connectorでexact remote HEADを照合し、product-contract gapなし、GO／review-waivedと判定した | applied as execution input | `artifacts/20260728t055016z-s05-chatgpt-implementation-work-packet.md`; source HEAD `2e0589e1e4ce1b123cd30d14c338d07038ed1429` | artifact／Reportをcommit・push後、bounded dev-coderへ渡す |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

`adoption_status` は `adopted`、`partially_adopted`、`rejected`、`deferred` のいずれかを用いる。`stale` または `blocked` の未解決entryはpromotionとimplementation startを止める。

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-20260726-V15-REVIEW | adopted | fresh Red Team read-only review | Candidate v15 review-cycle closure | exact Candidate identity、source HEAD、127件のpreflight、RP-01〜RP-07を独立確認したためreview evidenceとして採用した | `artifacts/20260726t164628z-chatgpt-output-v15-fresh-red-team-review.md`; `artifacts/20260726t164657z-disc-v15-red-team-pass-admission.md` | canonical reviewで現在の正本を再検証する |
| EAL-20260727-V15-ADOPTION | adopted | Human decision and reviewed Candidate ZIP | canonical `requirement.md`、`design.md`、`plan.md`、supporting artifacts | Humanの正式配置指示、source blob parity、exact ZIP SHAを満たしたためcanonical contentへ採用した | `artifacts/20260726t225541z-disc-v15-human-adoption-decision.md`; `artifacts/20260726t154840z-iss-00334-issue-planning-candidate-v15.zip` | canonical planning repairとfresh reviewを実施する |
| EAL-20260727-SPECIALISTS | adopted | system-architect and implementation-planner read-only reviews | `design.md` and `plan.md` amendment | public route、transaction、archive closure、Closure Index、step ownership、live boundaryの欠陥がsourceと整合したため全件採用した | `artifacts/20260726t235800z-review-system-architect-fail.md`; `artifacts/20260726t235801z-review-implementation-planner-fail.md` | amendmentをfresh spec-reviewerへ渡す |
| EAL-20260727-CANONICAL-FAIL | adopted | fresh spec-reviewer read-only review | canonical planning repair | 9件のP1がRequirement、Design、Plan、Assurance、Reportの実証可能な欠陥だったため全件採用した | `artifacts/20260726t235522z-review-canonical-spec-review-fail.md` | P1-01〜P1-09修正後にfresh re-reviewする |
| EAL-20260727-MAIN-REPAIR | adopted | Human-authorized Codex Main repair | `requirement.md`、`design.md`、`plan.md`、`.assurance.json`、`report.md` | ユーザーが今回に限りCodex Mainによる仕様修正を明示承認し、採用済みP1のowner文書を最小範囲で更新した | `requirement.md`; `design.md`; `plan.md`; `.assurance.json`; 本書のDecision Ledger | fresh spec-reviewerの正式判定を取得する |
| EAL-20260727-CHATGPT-REVIEW | adopted | fresh ChatGPT spec-reviewer with GitHub connector | bounded Design／Plan correction | exact remote HEADと六添付のidentityを照合し、前回P1-02〜P1-09のclosure、P1-01のschema gap、git-bound start-gate gap、S01／S03のtest ownership gapを確認した | `artifacts/20260727t004653z-chatgpt-fresh-canonical-review-fail.md` | 別のBlue Team ChatGPT threadでP1／P2を具体化し、修正後は別fresh reviewを行う |
| EAL-20260727-CHATGPT-BLUE | adopted | dedicated ChatGPT Blue Team authoring thread with GitHub connector | `design.md` and `plan.md` bounded correction | exact repository／branch／HEADとcanonical Git blobsを確認し、正式FAILの2 P1／2 P2だけをreplacement-ready blocksへ具体化した。Requirement meaningと既閉鎖controlsは変更不要と確認した | `artifacts/20260727t014215z-chatgpt-blue-bounded-correction.md`; Design／Plan diff | correction snapshotをcommit／pushし、別fresh Red Team threadで再レビューする |
| EAL-20260727-CHATGPT-RED-2 | adopted | fresh ChatGPT Red Team read-only review | snapshot `546245f1072e6d7822fc7885eff814ac1eca1dc5` | actual branch HEADとcanonical filesを読んだ正式FAILとしてP0=0、P1=6、P2=2を採用した。P1-11はMainのrequested SHA誤りでありproduct findingとしては採用しない | `artifacts/20260727t022302z-chatgpt-fresh-canonical-review-fail.md` | P1-12〜P1-16、P2-03／P2-04をBlue Teamへ渡す |
| EAL-20260727-CHATGPT-BLUE-2 | adopted | same dedicated ChatGPT Blue Team authoring conversation | Requirement／Design／Plan bounded correction | actual HEADとformal Red resultへbindし、該当findingsだけをreplacement-ready blocksへ具体化した。BlueはPASS判定やrepository mutationを行っていない | `artifacts/20260727t024714z-chatgpt-blue-bounded-correction-followup.md`; current三文書diff | assurance再束縛、commit／push後に新規Red threadでfresh review |
| EAL-20260727-CHATGPT-RED-3 | adopted | fresh ChatGPT Red Team read-only review | published snapshot `3fc0e61ef8425abc0b4a5488d51e7060b0ed03cc` | exact branch／HEADとcanonical filesを確認した正式FAILとしてP0=0、P1=3、P2=1を採用した。P1-11〜P1-16はcurrent scopeでclosed／preservedと確認された | `artifacts/20260727t033431z-chatgpt-fresh-canonical-review-fail.md` | P1-17〜P1-19、P2-05だけをsame Blue Teamへ渡す |
| EAL-20260727-CHATGPT-BLUE-3 | adopted | same dedicated ChatGPT Blue Team authoring thread | Requirement／Design／Plan／Report bounded correction | exact remote HEAD、canonical blobs、fresh Red artifactを確認し、status determinism、bounded recovery observability、acyclic owner graph、Report milestoneだけを具体化した。BlueはPASS判定、repository mutation、patch、ZIP生成を行っていない | `artifacts/20260727t035110z-chatgpt-blue-bounded-correction-followup.md`; fresh Red artifact; bounded owner-document replacement blocks | Mainがactual diff／validation／assurance rebindingを確認し、new immutable HEADで別fresh review |
| EAL-20260727-REBASELINE | partially_adopted | Human direction、approved parent scope、current repository facts | canonical Requirement／Design／Plan rebaseline | prior Blue／Red evidenceから製品境界と実害のある4点だけを採用し、追加schema、proof matrix、closure graph、再設計提案は採用しなかった | current三文書; D-20260727-RB010; Initiative defect-only review charter | validate、assurance再束縛、commit／push後にdefect-only fresh review |
| EAL-20260727-DEFECT-REVIEW | adopted | fresh ChatGPT Pro defect-only review | snapshot `a0d1b4dedf68f1957a01d1fd48cd2e3a1be64b03` | exact HEAD／three targetsへbindし、親Epicとの直接矛盾1件だけを報告したため正式review evidenceとして採用 | `artifacts/20260727t070247z-chatgpt-defect-only-review-fail.json`; SHA-256 `052fa9ea2533c301a28037cc98f7dee7cc2654429bf627e642fd4387519f0740` | P1-01 correctionをcommit／pushしclosure review |
| EAL-20260727-CLOSURE-PASS | adopted | fresh ChatGPT Pro correction reviewer | snapshot `ec801c374038e7e5ad4f31b3919440aa9b79eeaa` | P1-01 closureとdirect regressionだけを確認しP0=0、P1=0、PASSを返した | `artifacts/20260727t070853z-chatgpt-defect-only-closure-review-pass.json`; SHA-256 `1ae92cc537a06cee0be7e21a5f6eeb944a9bf735d8fbc250bfbbdc559651bd97` | Spec Authoring GateをPASSとして実装開始判断へhandoff |
| EAL-20260728-S01-PACKET | adopted | ChatGPT Pro with GitHub connector | S01 bounded implementation input | remote branchとexact HEAD `b1ee8d091deba166b805145e7367190de6a14578`を確認し、approved S01を拡張せずallowed paths、Red-first tests、実装順、停止条件、dev-coder指示へ具体化した | `artifacts/20260727t150723z-s01-chatgpt-implementation-work-packet.md`; Oracle session `iss00334-s01-implementa-brief` | bounded dev-coderへ渡し、observed evidenceをreportへ記録する |
| EAL-20260728-S02-PACKET | adopted | ChatGPT Pro with GitHub connector | S02 bounded implementation input | remote branchとexact HEAD `c597bd146c1d68e619cdc1e24b1b76dd405fe36a`を確認し、approved S02を既存Git preflight／backend／redaction primitiveの再利用、exact allowlist、Red-first tests、停止条件、dev-coder指示へ具体化した | `artifacts/20260727t161404z-s02-chatgpt-implementation-work-packet.md`; Oracle session `iss00334-s02-implementa-brief` | S02範囲内の実装local detailsだけを採用し、bounded dev-coderへ渡す |
| EAL-20260728-S03-PACKET | adopted | ChatGPT Pro with GitHub connector | S03 bounded implementation input | remote exact HEAD `530cca24943892dd440ca67823a9d68dfc46763d`を確認した。initial authority stopで特定した12項目をD-20260727-EX012に基づき再評価し、canonical／public scopeを変えない最小v1 internal encodingと11-path allowlistへ具体化した | `artifacts/20260728t020250z-s03-chatgpt-implementation-work-packet.md`; SHA-256 `efb47085457cea57fc4b83ab31f053b77793b4beaca22c86ebf73bad1aaa29e1`; sessions `iss00334-s03-implementa-brief`／`required-repository-connector-context-github-108` | bounded dev-coderへ渡し、S03範囲内のobserved evidenceを記録する |
| EAL-20260728-S04-PACKET | adopted | ChatGPT Pro with GitHub connector | S04 bounded implementation input | exact remote HEAD `18006b779c70cdb13e4e5baae29ac3d79e77a954`を確認した。initial STOPの4 gapを既存Decision LedgerとS04／S06 ownershipで再分類し、canonical／public contractを変えないinternal evidence seam、Review gate、stateless revision、17-path allowlistへ具体化した | `artifacts/20260728t033850z-s04-chatgpt-implementation-work-packet.md`; SHA-256 `4543406ad170c158ebe3ec6a5e7cea56c75c3af9eb5df1bcf6037c479e2404d3`; sessions `iss00334-s04-implementa-brief`／`required-repository-connector-context-github-109` | artifact／Reportをcommit・push後、bounded dev-coderへ渡す |
| EAL-20260728-S05-PACKET | adopted | ChatGPT Pro with GitHub connector | S05 bounded implementation input | remote branchとexact HEAD `2e0589e1e4ce1b123cd30d14c338d07038ed1429`のidentical／ahead 0／behind 0を確認し、existing S01〜S04 contractsを維持したdual authorization、safe apply transaction、retryと5-path allowlistへ具体化した | `artifacts/20260728t055016z-s05-chatgpt-implementation-work-packet.md`; SHA-256 `472e956b65277a92f53e9b85c348c0f47203f56a83b4e725d84afa9984471d51`; Oracle session `iss00334-s05-implementa-brief` | artifact／Reportをcommit・push後、bounded dev-coderへ渡す |

## 目的整合台帳（Objective Alignment Ledger / 必須）

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| canonical planning rebaseline | create→revise→review→Human Gate→apply→publicationのwalking skeletonをREQ-001〜REQ-014で定義する | exact Git binding、immutable Candidate、read-only review、safe transaction、provider parity、JIT dogfoodを保持する | medium。簡潔化で必要contractを落とす可能性があるため、実在欠陥だけを対象にfresh reviewする | current rebaselineは未レビュー。commit／push後にdefect-only fresh reviewが必要 |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | approved parent scope、current repository facts、P1-01を照合 | P0／P1だけをrevision trigger、P2／P3-onlyはCandidate不変 | REQ-001〜014へ再基準化しP1-01を修正 | passed | no | execute approved plan |
| design | existing primitives、provider ownership、P1-01を照合 | Review severityとRevisionRequest validationのownerを確定 | 14 design sectionsへ再基準化しP1-01を修正 | passed | no | execute approved plan |
| plan | Requirement／Design、P1-01を照合 | S04とS07でP2／P3 revision 0を検証 | S01〜S07へ再基準化しP1-01を修正 | passed | no | execute approved plan |

過去のFAILは当時のsnapshotに対する履歴として保持する。current rebaselineの判定には流用せず、new exact HEADを別fresh reviewerが限定scopeで判定する。

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）

過去のauthoring／correction provenanceはEvidence Adoption Ledgerと各artifactに保持する。current gateはrebaseline後の三文書とfresh closure PASSだけを対象にする。

| ロール（created_by_role） | 範囲（scope_id） | ドラフトパス（artifact draft path） | 参照元（source_paths） | 予定反映先（intended_targets） | 採用状態（adoption_status） | 反映先（reflected_to） | 差分ガード結果（diff_guard_result） | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果（reviewer result） | 昇格判断（promotion decision） |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Codex Main | iss-00334 planning rebaseline | `artifacts/20260727t070853z-chatgpt-defect-only-closure-review-pass.json` | `requirement.md`; `design.md`; `plan.md`; parent Epic; prior Evidence Adoption Ledger | `requirement.md`; `design.md`; `plan.md` | adopted | `requirement.md`; `design.md`; `plan.md`; `.assurance.json`; `report.md` | `git diff --check`、`spec-dock validate`、assurance verify successful | manual authoring integration | review-derived overgrowth | none | passed | execute approved plan |

S01 ChatGPT work packetはcanonical authoring draftではなく、Human指示に基づくreview不要のstep execution inputである。したがってDelegated Draft Evidenceへは分類せず、`EAL-20260728-S01-PACKET`とImplementation Delegation Gateで追跡する。

## グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）

Assurance classifierのauthorityは`standard`である。Issue-local overlayとして、untrusted archive、public command contract、multi-file transaction、credentialed live mutationにstrict相当のclosureを追加した。overlayの解除条件は、これら高リスク面が不要になったことをowner文書で示し、assurance再分類とfresh spec reviewを通すreviewed amendmentである。

| グレード（Grade） | 必要な専門家 / 代替（required specialist / fallback） | 使用状況（usage） | 証跡（evidence） | 鮮度 spec-reviewer 判定（fresh spec-reviewer verdict） | 実行可否（execution readiness） |
|---|---|---|---|---|---|
| standard | system-architect and implementation-planner | used | prior specialist artifacts、current三文書、`artifacts/20260727t070853z-chatgpt-defect-only-closure-review-pass.json` | passed | execute approved plan |

## レビューゲート状態（Reviewer Gate Status）

| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| canonical planning | ChatGPT-first canonical spec review | fresh Red Team | current for published HEAD; stale after bounded correction | failed | no | new immutable correction snapshot requires fresh review | `artifacts/20260727t033431z-chatgpt-fresh-canonical-review-fail.md`。P0=0、P1=3、P2=1。P1-17／P1-18／P1-19、P2-05 bounded correction対象。P1-11〜P1-16はpreserved |
| canonical planning rebaseline | defect-only canonical spec review | fresh reviewer | pending new exact HEAD | pending | no | implementation remains blocked until PASS | current三文書だけをreviewed targetとし、既存設計を覆す提案をfindingにしない |
| rebaseline correction | defect-only closure review | fresh ChatGPT Pro reviewer | current for `a0d1b4dedf68f1957a01d1fd48cd2e3a1be64b03`; stale after correction | failed | no | correction HEAD must close P1-01 without direct regression | `artifacts/20260727t070247z-chatgpt-defect-only-review-fail.json`。P0=0、P1=1 |
| correction closure | defect-only closure review | fresh ChatGPT Pro reviewer | current for `ec801c374038e7e5ad4f31b3919440aa9b79eeaa` | passed | no | Spec Authoring Gate PASS。new material spec changeで失効 | `artifacts/20260727t070853z-chatgpt-defect-only-closure-review-pass.json`。P0=0、P1=0、P1-01 closed |
| execution readiness | canonical spec gate | spec-reviewer | fresh | passed | no | execute approved plan | ChatGPT Pro closure PASSをspec-reviewer evidenceとして採用。plan marker追加はstep concrete artifact contractの明記だけでscope／behavior変更なし |
| S01 | per-step code review | code-reviewer | fresh for pre-fix uncommitted S01 diff | failed | no | 3 P1をbounded dev-coder follow-upで修正しfresh re-review | git-bound target／Semantic revision／Human decisionのexact identity・raw Review bindingを迂回可能 |
| S01 | per-step code re-review | code-reviewer | fresh for post-fix uncommitted S01 diff | passed | no | S01 commit候補へ進む | 3 P1 closed、archive／git-bound positive path、Review parsing、CLI surface、allowlistに直接回帰なし |
| S05 | per-step defect-only code review | code-reviewer | fresh for initial uncommitted S05 diff | failed | no | 2 P1をsame dev-coderへ戻す | post-commit recovery recordの永続化順序とunsafe operation evidence受理を指摘 |
| S05 | per-step defect-only code re-review | code-reviewer | fresh for first corrected S05 diff | failed | no | 2 P1をsame dev-coderへ戻す | application入口でH1 retryがH0 preflightに遮断され、pre-commit interruption backupが復旧されないことを指摘 |
| S05 | transaction recovery closure review | code-reviewer | fresh for final uncommitted S05 diff | passed | no | S05 commit候補へ進む | prior P1 4件closed、findings 0、confidence 0.97。同じS05契約への明確なP0／P1回帰なし |

## Assurance記録

- `./spec-dock/scripts/spec-dock assurance classify --stage requirement --issue iss-00334 --format json`: valid。`authorized_profile=standard`、`status=provisional`としてrebaseline後の三文書へ再束縛した。
- `./spec-dock/scripts/spec-dock assurance verify --issue iss-00334 --format json`: valid。
- source binding:
  - Requirement SHA-256: `989d5961d9dd059b7a1295e5b598a72341b6cf19ba1ae4b8c8b1960a2d826fe6`
  - Design SHA-256: `b71c266d9db87c5de7c1d56921a2e0113509ea9ffd030f6b39ecc81af8d911a7`
  - Plan SHA-256: `de7690f04a67a24695bf9051a0353861accf30605f5b84b7fc1439abe1061aaf`
- current profileは`standard`であり、archive safety、transaction fault、public contract、live mutationは各owner milestoneのfocused testとrequired reviewで扱う。独立したstrict overlayや重複closure graphは設けない。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-07-27 — canonical planning repair）

#### 対象

- Planning gate: P1-01〜P1-09
- 製品実装step: 未開始
- Planned source: `plan.md` Spec-Locked Closure Index、S01〜S99

#### 実施内容

- formal `system-architect`、`implementation-planner`、`spec-reviewer` のread-only findingsをIssue artifactsへ保存した。
- Requirement、Design、Planをowner別に修正した。
- Assuranceをcurrent三文書SHAへ再束縛した。
- Reportの候補版履歴を保持しつつ、readiness用templateを実値へ置換した。

#### 実行コマンド / 結果

| コマンド | 観測結果 |
|---|---|
| `./spec-dock/scripts/spec-dock validate` | pass。222 nodesを検証 |
| `git diff --check` | pass |
| `./spec-dock/scripts/spec-dock assurance classify --stage requirement --issue iss-00334 --format json` | pass。standard／provisionalをcurrent三文書へ記録 |
| `./spec-dock/scripts/spec-dock assurance verify --issue iss-00334 --format json` | pass |
| `./spec-dock/scripts/spec-dock assurance compose --artifact all --issue iss-00334 --format json --dry-run` | approved no-op。Design／Plan substantive conflict、changed pathsなし |

#### ワークフロー単位の named role 許可（Workflow-Scoped Authorization）

| 許可元（authorization source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 例外 | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| ユーザーのSpecDock workflow利用依頼と今回のCodex直接修正承認 | current `chemitaro/spec-dock` worktree | iss-00334 | current task | system-architect、implementation-planner、spec-reviewer、dev-coder、code-reviewer、qa-reviewer | active Issueとdocumented role責務。破壊的操作、scope expansion、credentialed external mutationは含めない | Issue完了、scope変更、user revocation、session終了 | Codex Mainの直接修正許可はcanonical planning repairに限定し、製品実装のworker delegation contractを変更しない | fresh spec-reviewer pass後にS01へ進む |

#### 実装委任ゲート（Implementation Delegation Gate）

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 必須検証（required verification） | 停止条件（stop conditions） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|
| S01 | delegated | shipped CLI contractとtestsのbounded implementation | dev-coder | `plan.md` S01と`artifacts/20260727t150723z-s01-chatgpt-implementation-work-packet.md`のexact allowed paths | canonical `requirement.md`、`design.md`、`plan.md`、S01 work packet | S01 Red／Green command、focused code review、diff allowlist | scope escape、test failure、new requirement gap、S02以降の実装が必要 | initial implementation 109 tests Green。fresh reviewの3 P1を同workerがbounded修正し、116 tests Green、fresh re-review pass、allowlist escape 0 |
| S02 | delegated | Git identity、bounded PlanningContext、Prompt synthesis、fixed ChatGPT Use transportのbounded implementation | dev-coder | `plan.md` S02と`artifacts/20260727t161404z-s02-chatgpt-implementation-work-packet.md`のwrite allowlist | canonical `requirement.md`、`design.md`、`plan.md`、S01実装、S02 work packet | Red-first Git／backend／security tests、S01／shared primitive regression、fresh code review、diff allowlist | public CLI／bootstrap変更、S03以降、parallel Git/subprocess framework、wrapper ABI変更、scope外pathが必要 | Red 34 failed／76 passed／0 errorsからfocused 119 passedへGreen。3 P1と残存1 P1をnegative testsで閉鎖し、final fresh reviewはfindings 0／pass。S01/shared/Core regressions、ruff、mypy、validate、diff check pass。milestone commit `796a1ce4c8b4f2161f0d646cf45f3afc6aaf40e2`をpushしclosed |
| S03 | delegated | Planner responseのstrict extraction、Issue Candidate identity、named ZIP contract、atomic no-replace publicationのbounded implementation | dev-coder | `plan.md` S03と`artifacts/20260728t020250z-s03-chatgpt-implementation-work-packet.md`の11-path write allowlist | canonical `requirement.md`、`design.md`、`plan.md`、S01／S02実装、S03 work packet | Red-first Candidate／ZIP profile／atomic publication tests、focused regression、fresh code review、diff allowlist | source HEAD mismatch、allowlist外変更、public CLI／bootstrap変更、generic ZIP default変更、atomic no-replace不能、failure後final filename残存、S04以降、secret／private raw serialization | Red 43 failed／36 passedからfocused 105 passedへGreen。fresh reviewの3 P1を同workerがexact Redで再現・修正し、focused 108 passed、S01／S02/Core 112 passed、generic archive 57 passed、fresh re-review findings 0／pass。11 changed pathsはallowlist内 |
| S04 | delegated | fresh read-only Review、exact external evidence、Semantic／Mechanical revision、N+1 immutable Candidateのbounded implementation | dev-coder | `plan.md` S04と`artifacts/20260728t033850z-s04-chatgpt-implementation-work-packet.md`の17-path write allowlist | canonical三文書、S01〜S03実装、S04 work packet | behavioral Red、archive／git-bound Review、revision／fresh re-Review fake chains、S01〜S03 regressions、fresh code review、diff allowlist | parser／commands／UseCases／closed domain schema変更、public option、evidence directory scan、durable session identity、generic archive変更、S05+、repository内Review output、allowlist外path | initial Red 120 collected／109 passed／11 failed／0 collection errorsからGreen。named closure 18 casesを追加し、fresh reviewsのP1 11件をexact negative testsで閉鎖。final S04 167、S01 101、S02 31、S03 137、ruff、mypy、validate、diff、17-path allowlist pass。final fresh review findings 0／pass |
| S05 | delegated | exact Review／Human decision binding、decision-only rejection、whole-file adoption、scoped transaction、planning-only commit／push／retryのbounded implementation | dev-coder | `plan.md` S05と`artifacts/20260728t055016z-s05-chatgpt-implementation-work-packet.md`のexact 5-path write allowlist | canonical三文書、S01〜S04実装、S05 work packet | PA-NF-01〜10B、approved／rejected positives、rollback／recovery、publication retry、fake remote integration、S01〜S04 regression、fresh code review、diff allowlist | HEAD／branch不一致、dirty worktree、allowlist外変更、public CLI／provider／generic lifecycle変更、canonical doc変更、S06／S07が必要 | initial Red 40 failedからfocused 77 passedへGreen。fresh reviewsのP1 4件をexact negative testsで閉鎖し、final findings 0／pass。PA-NF 17、retry 9、rollback／recovery 12、S01〜S04 regression 225、static、validate／sync／validate、diff、5-path allowlist pass |

#### 発見されたテスト / リスク（Discovered Tests）

planning repairで発見されたarchive safety、transaction fault、publication resume、live-operation boundaryのtest obligationsは、`plan.md`の`CLOS-ARC-01`〜`CLOS-ARC-25`、`CLOS-RISK-001`〜`CLOS-RISK-005`へ採用済みである。製品実装中に新しいtest／riskを発見した場合は、実装で吸収せずここへentryを追加し、materialな変更はPlan amendmentへ戻す。

- S02で、実temporary Git repositoryを使うclean／synced preflight tracer、fixed backend failure classification、ephemeral Prompt pack validationをdiscovered characterizationとして追加した。いずれもapproved S02 obligationの具体化であり、canonical closureの追加・削除・意味変更はない。
- fixed wrapperのlive ABI、実ChatGPT response framing、provider Promptのinstalled／dogfood projectionはS02 hermetic testsでは未検証であり、後続S06／S07のownerへ引き継ぐ。
- S03で、実際のS02 outer response frameを`.strip()`した後もfinal inner end markerをEOFとしてexact parseできるintegration testを追加した。S02 transport contractを変更せず、S03 extractionの既存入力境界をcharacterizeする。
- S03のmacOS atomic no-replace publicationは実行検証済みである。Linux `renameat2(RENAME_NOREPLACE)`分岐はstatic／type verificationに留まり、Linux実環境の確認は後続の統合検証へ引き継ぐ。
- S04で、fuzzy transport alias／repack／root mismatch、Review authority mismatch、Semantic malformed／nonpass、Semantic／Mechanical fresh re-Review chainの18 direct casesを追加した。既存実装で全件passし、named closureだけを補完した。
- S04のexternal Candidate／Review evidence／revision requestとgit-bound targetは、descriptor-first no-follow／nonblocking bounded read、ancestor openat traversal、immutable captured bytesへ統一した。Review evidence publicationはretained directory fd relativeのatomic no-replaceを使う。
- S04初回Redは120 collected／109 passed／11 failed／0 collection errorsだったが、一部は未実装symbol／moduleの実行時failureであり、packetが求めたassertion-only Redではない。raw Redとして記録し、strict assertion-only closureとは扱わない。後続P1はすべてexact assertion Redで再現した。
- S05で、post-commit interruption前のcommit recovery record永続化、unsafe operation evidence拒否、application入口からのsame-operation H1 publication retry、pre-commit crash後のdurable backup復旧をexact integration testsとして追加した。既存retry／transaction契約の具体化であり、canonical scope変更はない。

#### ステップ契約の完了証跡（Step Contract Closure）

S01〜S05の製品実装step closure evidenceを本書のImplementation Delegation Gate、Test Contract Closure、session log、Milestone Gateへ記録した。S03はREQ-004、REQ-012のCandidate生成部分、AC-001のCandidate生成部分、AC-006、AC-011を閉じた。S04はREQ-005〜007、AC-004〜005、Review／revisionに関するREQ-012をarchive／git-bound Review、Semantic／Mechanical N+1 Candidate、fresh re-Review、external evidence、mutation／race／non-leakage testsで閉じた。S05はREQ-008〜010、AC-002〜003、AC-007〜010、EC-003〜005、PA-NF-01〜10Bをdual authorization、decision-only rejection、whole-file／git-bound apply、rollback／recovery、planning-only commit／push／retry、fake remote testsで閉じた。commit、push、post-commit cleanはMilestone Gateで追跡する。

#### テスト契約の完了証跡（Test Contract Closure）

S05 focused 77、PA-NF 17、retry／publication 9、rollback／recovery 12、S01〜S04 regression 225を実行し全件passした。S06／S07／S99 ownerのtest contractは未実行であり、`plan.md`の各`tc-*`とSpec-Locked Closure Indexの対応を維持して実行した事実だけを追記する。

#### クロージャ網羅（Closure Coverage）

planning repairではClosure Indexのschemaとownerを確定した。実装closureは未開始であり、S99までに全`required=yes` rowのobserved evidenceをこのsectionへ集約する。

#### クロージャ差分（Closure Delta）

現時点でapproved Planからのimplementation closure deltaはない。追加、変更、削除、alias mappingが生じた場合は、理由、resolved closure、plan amendment要否、fresh re-review要否を記録する。

### セッションログ（2026-07-27 — ChatGPT First bounded correction）

#### 対象

- Reviewed snapshot: `2984c696b4c7e94cbed6fd63697a563f55fd3631`
- Blue source snapshot: `b5447aef2c4d2ad5fabbab532cb9cef0e8d397b0`
- Formal findings: P1-01、P1-10、P2-01、P2-02
- 製品実装step: 未開始

#### 実施内容

- fresh ChatGPT Red reviewの正式FAILを、別の専用ChatGPT Blue Team threadへ渡した。
- Blue TeamはGitHub connectorでrepository、branch、HEAD、canonical Git blobsを確認し、repository mutation／patch／review verdictなしでbounded replacement blocksを作成した。
- Mainはclosed Review／Human evidence schema、mode-neutral start gate、S01 positive target oracle、S03 planning-specific fixture ownershipをDesign／Planへ統合した。
- Assuranceをcurrent三文書SHAへ再束縛し、Reportへauthoring evidenceとfresh re-review gateを記録した。

#### 実行コマンド / 結果

| コマンド | 観測結果 |
|---|---|
| `chatgpt-use` session `iss00334-blue-planning-correction-r5` | pass。GitHub connectorでexact HEAD／3 canonical pathsを確認し、Pro選択証跡`verified=yes`、read-only Blue outputを取得 |
| `./spec-dock/scripts/spec-dock validate` | pass。222 nodesを検証 |
| `git diff --check` | pass |
| `./spec-dock/scripts/spec-dock assurance classify --stage requirement --issue iss-00334 --format json` | pass。standard／provisionalをcorrected三文書へ再束縛 |
| `./spec-dock/scripts/spec-dock assurance verify --issue iss-00334 --format json` | pass |
| `./spec-dock/scripts/spec-dock assurance compose --artifact all --issue iss-00334 --format json --dry-run` | approved no-op。Design／Plan substantive conflict、changed pathsなし |

#### ChatGPT Use運用上の問題

- 短文および1ファイル小容量添付は正常だったが、4ファイル・約39.7k tokensの同時投入はChatGPT UIの「リクエストが多すぎます」を発生させ、会話0／添付0のまま`prompt-commit-timeout`になった。
- wrapperの`session <slug> --path`はwrapper自身の`--path <paths...>`と衝突し、`option '--path <paths...>' argument missing`となった。
- wrapperはUI上のrate-limit noticeを専用statusで返さず、generic `prompt-commit-timeout`として報告した。
- `chatgpt-use`のdocumented identity-sensitive flowに従い、同時添付をやめ、GitHub connectorでexact remote snapshotを確立して成功した。Oracle direct実行、API fallback、別profileは使用していない。

### セッションログ（2026-07-27 — second fresh Red / same Blue correction）

#### 対象

- Actual reviewed snapshot: `546245f1072e6d7822fc7885eff814ac1eca1dc5`
- Erroneously requested snapshot: `546245f1b0a7f8fe616fe6f13b6f4534f40d77cc`
- Formal findings: P1-11〜P1-16、P2-03、P2-04
- Product correction scope: P1-12〜P1-16、P2-03、P2-04
- 製品実装step: 未開始

#### 実施内容

- 新規ChatGPT Red Team threadがGitHub connectorでbranch actual HEAD、canonical五文書、prior review／Blue artifacts、repository feasibility surfacesをread-only reviewした。
- Mainが誤ったrequested SHAを指定したためP1-11が発生した。reviewerはactual branch HEADを解決して内容をreviewしたが、正式判定はP0=0、P1=6、P2=2のFAIL、S01 blockedである。
- 正式review artifactだけを既存の専用Blue Team conversationへ渡し、actual HEADへbindしたbounded correctionを作成した。
- MainはRequirement R-01〜R-03、Design D-01〜D-14、Plan P-01〜P-20の対象箇所を統合し、assuranceを再束縛した。

#### 実行コマンド / 結果

| コマンド | 観測結果 |
|---|---|
| fresh `chatgpt-use` Red session | FAIL。P0=0、P1=6、P2=2、S01 blocked。actual HEADをreview、repository mutation 0 |
| `chatgpt-use --followup iss00334-blue-planning-correction-r5` | same conversation URLでBlue authoring継続。GitHub actual HEAD確認、replacement-ready blocks取得。follow-up selector evidenceは`resolved=(unavailable); verified=no` |
| `./spec-dock/scripts/spec-dock validate` | pass。222 nodesを検証 |
| `git diff --check` | pass |
| `./spec-dock/scripts/spec-dock assurance classify --stage requirement --issue iss-00334 --format json` | pass。standard／provisionalをcurrent三文書へ再束縛 |
| `./spec-dock/scripts/spec-dock assurance verify --issue iss-00334 --format json` | pass |
| `./spec-dock/scripts/spec-dock assurance compose --artifact all --issue iss-00334 --format json --dry-run` | expected invalid。Design／Plan `substantive_content_conflict`、`changed_paths=[]`。non-dry-run未実施 |

#### 判定

- Blue outputはauthoring evidenceであり、review PASSではない。
- follow-upは同一Blue conversation URLとGitHub actual HEAD確認を保持したが、model selector再検証がunavailableだった。この制約を残し、次の正式判定は新規fresh Red Team threadだけが行う。
- 次回Red promptのsource HEADはcommit／push後に`git rev-parse HEAD`から取得したexact 40文字を貼り付け、手入力で再構成しない。

### セッションログ（2026-07-27 — third fresh Red / same Blue correction）

#### 対象

- Actual reviewed snapshot: `3fc0e61ef8425abc0b4a5488d51e7060b0ed03cc`
- Formal findings: P1-17、P1-18、P1-19、P2-05
- Product correction scope: P1-17〜P1-19、P2-05
- 製品実装step: 未開始

#### 実施内容

- 新規ChatGPT Red Team threadがGitHub connectorでexact branch／HEADとcanonical planning setをread-only reviewした。
- 正式判定はP0=0、P1=3、P2=1のFAIL、S01 blockedである。P1-11〜P1-16はclosed／preservedと確認された。
- 正式review artifactだけを既存の専用Blue Team conversationへ渡し、exact reviewed HEADへbindしたbounded correctionを作成した。
- Mainはstatus determinism、PA-NF 11 fixture、recovery workspace class、Closure owner graph、published milestone ledgerだけをowner文書へ統合した。

#### 実行コマンド / 結果

| コマンド | 観測結果 |
|---|---|
| fresh `chatgpt-use` Red session `iss00334-fresh-red-planning-review-2` | FAIL。P0=0、P1=3、P2=1、S01 blocked。Pro selector `verified=yes`、repository mutation 0 |

### セッションログ（2026-07-28 — S01 CLI Skeleton and Domain Contracts）

#### 実行入力と委任

- ChatGPT Pro session `iss00334-s01-implementa-brief`はGitHub connectorでbranch `iss-00334-implement-chatgpt-issue-planning-workflow`、source HEAD `b1ee8d091deba166b805145e7367190de6a14578`を確認した。
- 具体化結果を`artifacts/20260727t150723z-s01-chatgpt-implementation-work-packet.md`へ保存し、canonical scopeを拡張しないS01 execution inputとして採用した。Human指示に従いartifact自体のreviewは行わない。
- artifact／report-only commit `20b45946`をpush後、product source treeがChatGPT確認時点と同一であることを確認し、`dev-coder`へS01 exact allowlistを委任した。

#### Red / Green / verification evidence

| 種別 | コマンド / evidence | 観測結果 |
|---|---|---|
| Red | `test_result_rejects_invalid_success_pair` | `ready/candidate_created`を拒否しないcontract欠落により`DID NOT RAISE ValueError`、exit 1 |
| Focused tests | `uv run pytest -q tests/unit/domain/test_issue_planning_contracts.py tests/unit/application/test_issue_planning.py tests/unit/commands/test_issue_planning.py tests/unit/presentation/test_issue_planning.py tests/cli_runtime/test_chatgpt_cli.py tests/cli_runtime/test_runtime_shell_s11.py` | post-fix 116 passed、failed 0、skipped 0 |
| Help smoke | `spec-dock-chatgpt --help`; `planning create --help`; `review planning --help` | 3 commandsともexit 0。公開groupは`planning`／`review`のみ |
| Static | S01 allowed sources／testsへの`ruff check` | All checks passed |
| Type | changed runtime 8 modulesへの`mypy` | Success: no issues found |
| Canonical validation | `./spec-dock/scripts/spec-dock validate` | pass、nodes=222 |
| Diff guard | `git status --short`; `git diff --check` | 14 changed entriesはS01 allowlist内、escape 0、diff check pass |

#### Closure state

- `S01-CLI-001`〜`S01-CLI-010`、`S01-RES-001`〜`S01-RES-005`、`S01-CTX-001`〜`S01-CTX-002`、`S01-ID-001`〜`S01-ID-004`、`S01-JSON-001`〜`S01-JSON-003`、`S01-REVIEW-001`〜`S01-REVIEW-003`、`S01-REV-001`〜`S01-REV-005`、`S01-HUM-001`〜`S01-HUM-004`、`S01-RESULT-001`〜`S01-RESULT-004`、`S01-REG-001`のimplementation／test evidenceを取得した。
- production use casesはfail closedで未設定とし、fake use case以外からsuccess reasonを返さない。
- discovered characterizationとして、Issue形式IDを持つnon-Issue `StoredMetaRecord`もresolverが拒否することを確認した。
- fresh S01 `code-reviewer`は3件のP1を報告した。別Issueのgit-bound path tuple、raw Review bytesとSemantic revision object、raw Review bytes内identityとHuman decision identityの不一致が受理されるため、同じ`dev-coder`へnegative testsと最小修正を再委任する。
- bounded follow-upは4件のcontract Redを追加し、resolver-derived exact tuple、strict-parsed Review object、Human decision identity/digest bindingを閉じた。post-fix focused/Core laneは116 passed。
- fresh code re-reviewはfindings 0、`review_status: pass`。commit候補とpost-commit clean checkが未完了であるため、次stepは開始しない。
- No material implementation decisions beyond the approved plan.

### セッションログ（2026-07-28 — S02 Git Context and ChatGPT Invocation）

- S01 milestone commit `c597bd146c1d68e619cdc1e24b1b76dd405fe36a`をoriginへpushし、local／remote parityとpost-commit clean worktreeを確認した。
- ChatGPT Pro session `iss00334-s02-implementa-brief`はGitHub connectorで同branch／exact HEADを確認し、S02だけのwork packetを生成した。Promptでは既存`run_github_sync_preflight`、`invoke_backend`、authority-boundary/redactionの再利用、S03以降の禁止、no-patch／no-reviewを固定した。
- 回答を`artifacts/20260727t161404z-s02-chatgpt-implementation-work-packet.md`へ保存した。これはreview不要のstep execution inputであり、canonical authoring draftではない。
- work packetが提示したresource bound、internal result field、response frameはapproved S02の「bounded context」「source evidence」「partial response classification」を実装可能にするimplementation-local detailsとしてのみ採用する。Requirement／Design／Planの意味、public CLI、後続step境界を変更する場合は停止する。
- S02 Red-first commandは110 testsをcollectし、76 passed／34 failed／0 errorsとなった。34 failuresはGit preflight short-circuit、bounded Prompt synthesis、source identity、exact response frame／security、single backend core transient capture、transport tracerの未実装behaviorに到達した。
- bounded `dev-coder`実装後、focused lane 115 passed、S01 command／presentation／CLI regression 28 passed、shared backend／preflight regression 104 passed（312 deselected）、Git fetch policy／receipt 56 passed、Core shell 12 passedとなった。
- 親の独立再実行ではfocused＋S01 regression 143 passed、shared lanes／Core、ruff、mypy、`validate` nodes=222、`git diff --check`がpassした。16 changed pathsはS02 work packet allowlist内で、forbidden path変更は0である。
- fresh S02 `code-reviewer`は3件のP1を報告した。preflight blocker detailsのprivate path漏洩、Prompt assembly前後のsource snapshot race、branch等dynamic identityのscan欠落がS02のnon-leakage／exact source bindingを破るため、同じ`dev-coder`へnegative testsと最小修正を再委任する。
- bounded follow-upは3件のexact Redを追加し、3 failed／0 errorsを確認した。既存`SourceManifest.source_hashes`を再利用してPrompt attachment bytesをpreflight evidenceへbindし、blocker detailsをcontent-free化し、serialized dynamic identity全体をsecurity scanへ通した。
- post-fix focused laneは118 passed。親の独立再実行ではfocused＋S01 regression 146 passed、shared lanes／Core、ruff、mypy、`validate` nodes=222、`git diff --check`がpassした。
- 別fresh re-reviewでpreflight blocker non-leakageとsource snapshot raceは閉鎖したが、sensitive dynamic identityを拒否したresultが未加工`source_evidence`を保持し、`to_dict()`からbranch／upstreamを再漏洩するP1-C残存経路が見つかった。同じworkerへorchestration-level Redと最小修正を再委任する。
- residual follow-upはorchestration-level Red 1件を追加し、1 failed／0 errorsを確認した。`sensitive_input_rejected`時だけunsafeな`source_evidence`をresultから除外し、safe pathとnon-sensitive failure evidenceを維持した。
- post-fix focused laneは119 passed。親の独立再実行ではfocused＋S01 regression 147 passed、ruff、mypy、`validate` nodes=222、`git diff --check`がpassした。
- 別fresh closure reviewはfindings 0、`review_status: pass`。P1-A／B／Cのclosure、safe source evidence維持、backend short-circuitを確認した。
- S02 milestone commit `796a1ce4c8b4f2161f0d646cf45f3afc6aaf40e2`をoriginへpushし、local／remote parity、`git show --check`、post-commit clean worktreeを確認した。
- S02 product implementation、required verification、fresh review、commit、push、post-commit clean／remote parity checkは完了した。S02をclosedとし、S03 ChatGPT具体化へ進める。
- No material implementation decisions beyond the approved plan.

### セッションログ（2026-07-28 — S03 Candidate Construction and Immutable Publication）

- S02 closure evidence commit `530cca24943892dd440ca67823a9d68dfc46763d`をoriginへpushし、local／remote parityとpost-commit clean worktreeを確認した。
- ChatGPT Pro initial session `iss00334-s03-implementa-brief`はGitHub connectorで同branch／exact HEAD `530cca24943892dd440ca67823a9d68dfc46763d`を確認した。model evidenceは`requested=Pro`、`resolved=Pro`、`verified=yes`である。
- initial answerはinner payload grammar、frontmatter completeness、internal root、version／filename、Candidate ID、control schema、ZIP SHA self-reference、timestamp／reproducibility、placeholder grammar、safe result keysをauthority gapとして停止した。
- current canonical三文書とD-20260727-RB010／D-20260727-EX012、過去の拡張schema evidenceを照合し、これらをcanonical requirementへ再昇格せず、同一ChatGPT conversationへimplementation-localかproduct choiceかの分類だけをfollow-upした。
- follow-up session `required-repository-connector-context-github-108`は12項目をすべてimplementation-localと分類し、exact marker grammar、current Japanese frontmatter normalization、v1 Candidate naming／controls、detached external ZIP SHA、named Issue Candidate ZIP profile、temporary buildからatomic no-replace publicationまでを11-path allowlist内へ限定した。follow-up selector evidenceは`resolved=(unavailable)`／`verified=no`だが、initial Pro verified conversationの継続である。
- replacement packetを`artifacts/20260728t020250z-s03-chatgpt-implementation-work-packet.md`へ保存した。SHA-256は`efb47085457cea57fc4b83ab31f053b77793b4beaca22c86ebf73bad1aaa29e1`である。これはreview不要のstep execution inputであり、canonical authoring draftではない。
- S03 packetはpublic CLI、bootstrap、generic ZIP default、S04以降、canonical三文書の意味を変更しない。artifact／Report commitとorigin push後にbounded dev-coderへ渡す。
- S03 packet／Report commit `386fd0c01a4003a0a860beb02463bab6ea9c6fa4`をoriginへpushし、local／remote parityとclean worktreeを確認してからdev-coderへ委任した。
- Red-first laneは79 testsをcollectし、43 failed／36 passed／0 errorsだった。failuresはCandidate domain、named ZIP profile、atomic publication、Planner inner grammar、application create orchestrationの未実装behaviorに到達し、既存S01／S02 testsはpassした。
- initial implementation後、S03 focused 105 passed、S01／S02／Core regression 112 passed、generic authoring-pack characterization 57 passed、ruff、mypy、`validate` nodes=222、`git diff --check`がpassした。差分はpacketの11-path allowlistとMainのReport integrationだけである。
- fresh defect-only code reviewは3件のP1を報告した。dependency snapshot二重取得によるPrompt／Candidate mismatch、invalid placeholder schemaの`TypeError`伝播、JSON boolean `true`のmanifest version受理であり、いずれもS03 exact binding／strict fail-closed contractを直接破るため採用した。
- bounded follow-upは3件のnegative Redを追加し、3 failedを確認した。同一dependency snapshotをtransportとpackagingへbindし、検証済みplaceholder listだけを反復し、manifest versionでboolを明示拒否した。
- post-fix親独立検証はS03 focused 108 passed、S01／S02／Core regression 112 passed、generic archive 57 passed、ruff、mypy、`validate` nodes=222、`git diff --check`がpassした。
- 別fresh re-reviewはfindings 0、`review_status: pass`、confidence 0.97。3 P1 closureと同じS03契約への明白なP0／P1回帰なしを確認した。
- S03 milestone commit `70fe45acdf0002ec399343f7d11dba0e87856700`をoriginへpushし、local／remote parity、`git show --check`、post-commit clean worktreeを確認した。
- S03 product implementation、required verification、fresh review、commit、push、post-commit clean／remote parity checkは完了した。S03をclosedとし、S04 ChatGPT具体化へ進める。
- No material implementation decisions beyond the approved plan.

### セッションログ（2026-07-28 — S04 Review and Revision）

- S03 closure evidence commit `18006b779c70cdb13e4e5baae29ac3d79e77a954`をoriginへpushし、local／remote parityとpost-commit clean worktreeを確認した。
- ChatGPT Pro initial session `iss00334-s04-implementa-brief`はGitHub connectorでrepository、branch、default branch、exact HEAD `18006b779c70cdb13e4e5baae29ac3d79e77a954`を確認した。model evidenceは`requested=Pro`、`resolved=Pro`、`verified=yes`である。
- initial answerはexact Review bytes ingress、Mechanical Review binding、same-Blue continuity、`diff_budget` unitをmaterial contract gapとして停止した。Mainはcurrent Design／Requirement、D-20260726-RT002、D-20260727-RB010、D-20260727-EX012、S04／S06 ownershipをrepositoryで再照合した。
- 同一ChatGPT conversationのfollow-up session `required-repository-connector-context-github-109`へ既存decisionと内部application seam候補を渡し、blind adoptionを禁止して再分類させた。follow-up selector evidenceは`resolved=(unavailable)`／`verified=no`だが、initial Pro verified conversationの継続である。
- replacement packetはSTOPを撤回し、exact Reviewをapplication-only `PlanningRevisionEvidenceInput`で渡すこと、Mechanicalを同Candidateのblocking Reviewでgateすること、durable session locatorを作らないself-contained Semantic invocation、`diff_budget = len(old_utf8) + len(new_utf8)`、Candidate N+1 value generalizationをimplementation-localとした。
- 完全なfollow-up transcriptを`artifacts/20260728t033850z-s04-chatgpt-implementation-work-packet.md`へ保存した。trailing whitespace 1箇所の機械的除去後SHA-256は`4543406ad170c158ebe3ec6a5e7cea56c75c3af9eb5df1bcf6037c479e2404d3`である。これはreview不要のstep execution inputであり、canonical authoring draftではない。
- packetは17-path allowlistを定め、parser／commands／UseCases／closed domain schemas／generic archive default／canonical docs／dogfood projection／S05以降をread-onlyまたはout-of-scopeとする。artifact／Report commitとorigin push後にbounded dev-coderへ渡す。
- packet／Reportはcommits `0855be99092ccd53bd44402c56eb45ff77edca76`と`1cef3f8dd924818767d8d415af89066de14eeb11`でoriginへpushした。後者はartifactのtrailing whitespace機械的除去後SHAへReport identityを訂正したcommitである。local／remote parityとclean worktreeを確認してから実装委任した。
- initial focused Redは120 collected／109 passed／11 failed／0 collection errorsだった。一部は未実装symbol／moduleの実行時failureでありassertion-only Redではないため、その留保を保持する。実装後、packetのnamed closure delta 18 casesを追加し全件pass、production follow-up fix 0だった。
- initial implementationはarchive／git-bound fresh Review、exact external evidence、Semantic／Mechanical revision、P2／P3 backend 0、N+1 Candidate、fresh re-Reviewを17-path allowlist内で実装した。
- fresh defect-only reviewsは合計11件のP1を段階的に報告した。identity canonical digest可視性、Review finding non-leakage、Review evidence output-dir race、Semantic external Review再取込scan、git-bound transient target bytes、Candidate validate/read snapshot race、FIFO／symlink／oversize external reads、ancestor directory redirect、git-bound blocking readである。
- 全P1をexact negative testsで再現し、canonical digestの明示、shared sensitive scan、retained dirfd-relative evidence publication、SourceManifest direct target binding、Candidate single-open immutable snapshot、descriptor-first bounded readers、root/repo dirfd openat traversal、captured bytesのdigest／scan／transport一本化で閉鎖した。
- final親独立検証はS04 focused 167 passed、S01 regression 101 passed、S02 regression 31 passed、S03 regression 137 passed、ruff、mypy、`validate` nodes=222、`git diff --check`、17-path allowlistがpassした。
- final fresh code reviewはfindings 0、`review_status: pass`、confidence 0.95。external inputs、git-bound targets、Candidate snapshot、Review／revision non-leakage、dirfd publicationに明白なP0／P1なしを確認した。
- S04 milestone commit `6042553343225541709f71e74eeeca549ead2089`をoriginへpushし、local／remote parity、`git show --check`、post-commit clean worktreeを確認した。
- S04 product implementation、required verification、fresh review、commit、push、post-commit clean／remote parity checkは完了した。S04をclosedとし、S05 ChatGPT具体化へ進める。
- No material implementation decisions beyond the approved plan.

### セッションログ（2026-07-28 — S05 Human Gate and Apply Transaction）

- S04 closure evidence commit `2e0589e1e4ce1b123cd30d14c338d07038ed1429`をoriginへpushし、local／remote parityとpost-commit clean worktreeを確認した。
- ChatGPT Pro session `iss00334-s05-implementa-brief`はGitHub connectorでrepository、branch、default branch、exact pushed HEADを確認し、branch comparisonをidentical／ahead 0／behind 0として照合した。model evidenceは`requested=Pro`、`resolved=Pro`、`verified=yes`である。
- ChatGPTはproduct-contract gapなし、`GO / review-waived`と判定し、S01〜S04 contractを変更しないS05-local application orchestration／transaction adapterへ具体化した。
- 完全なtranscriptを`artifacts/20260728t055016z-s05-chatgpt-implementation-work-packet.md`へ保存した。SHA-256は`472e956b65277a92f53e9b85c348c0f47203f56a83b4e725d84afa9984471d51`である。これはHuman指示によりreview不要のstep execution inputであり、canonical authoring draftではない。
- packetはexact 5-path implementation allowlistを定め、closed domain contracts、generic Git lifecycle、public CLI、provider／installed assets、dogfood projection、canonical docs、S06／S07をread-onlyまたはout-of-scopeとする。
- artifact／Reportをcommit `ef13b5272b654617d585f43387c98b9313d7b980`としてoriginへpushし、clean／remote parityを確認してからbounded dev-coderへ委任した。
- initial focused Redは40 failed／0 collection errorsで、application symbolとinfra module未実装、PA-NF／transaction／fake remote contract未実装を確認した。Green実装後はfocused 70 passed、PA-NF 17、retry 3、rollback 8、S01〜S04 regression 225へ到達した。
- fresh defect-only reviewは、post-commit interruption前にcommit recovery recordが永続化されないことと、unsafe／permissiveなprecreated operation evidenceをresume対象にできる2件のP1を報告した。同workerが2 failedのexact Redを追加し、commit proofの先行永続化、owner／0700／0600／regular-file／closed-layout検証で閉じた。
- 次のfresh re-reviewは、application入口でH1 publication retryがH0 preflightに遮断されることと、pre-commit process interruption後のdurable backupを復旧しない2件のP1を報告した。同workerが5 failedのend-to-end Redを追加し、exact operation resume probeとprivate durable transaction backupのload／restore／proofで閉じた。
- final親独立検証はfocused 77、PA-NF 17、retry／publication 9、rollback／recovery 12、S01〜S04 regression 225、ruff、mypy、`validate` nodes=222、`sync --no-github --no-update-active`、再validate、`git diff --check`、exact 5-path allowlistがpassした。
- final fresh code reviewはfindings 0、`review_status: pass`、confidence 0.97。application-level H1 retry、pre-commit durable recovery、unsafe evidence fail-closedに同じS05契約への明確なP0／P1回帰なしを確認した。
- 実リポジトリへのplanning apply、planning commit、planning pushは実行していない。fake remote integrationだけを実行した。
- No material implementation decisions beyond the approved plan.

| `chatgpt-use --followup iss00334-blue-planning-correction-r5` | same Blue conversationでauthoring継続。GitHub exact HEAD確認、replacement-ready blocks取得。follow-up selector evidenceは`resolved=(unavailable); verified=no` |
| `./spec-dock/scripts/spec-dock validate` | pass。222 nodesを検証 |
| `git diff --check` | pass |
| `./spec-dock/scripts/spec-dock assurance classify --stage requirement --issue iss-00334 --format json` | pass。standard／provisionalをcorrected三文書へ再束縛 |
| `./spec-dock/scripts/spec-dock assurance verify --issue iss-00334 --format json` | pass |
| `./spec-dock/scripts/spec-dock assurance compose --artifact all --issue iss-00334 --format json --dry-run` | expected invalid。Design／Plan `substantive_content_conflict`、`changed_paths=[]`。non-dry-run未実施 |

#### 判定

- Red artifactだけが正式review evidenceであり、Blue outputはauthoring evidenceである。
- Blueはrepository mutation、patch、ZIP生成、PASS判定を行っていない。
- correctionをone immutable commitとしてpushし、actual resulting 40-character HEADを新規fresh Red Team threadへ渡す。

## マイルストーン / commit 候補ゲート（Milestone / Commit Candidate Gate）

| マイルストーン / step | クロージャ状態 | コミット候補 / 範囲 | コミットハッシュ / 最終台帳 | 差分確認 | 次アクション |
|---|---|---|---|---|---|
| second canonical correction snapshot | committed and published; fresh review failed | Requirement、Design、Plan、Assurance、Report、prior Red／Blue artifacts | `3fc0e61ef8425abc0b4a5488d51e7060b0ed03cc` | remote branch HEADとexact identicalをGitHub connectorで確認 | P1-17〜P1-19／P2-05 bounded correctionへ進む |
| third bounded correction | authoring complete; commit pending | Requirement、Design、Plan、Report、new Red artifact、Assurance rebinding | pending — Main must record actual resulting full HEAD | integration後にvalidate、diff-check、assurance verify、clean checkを実行 | one immutable commitをpushし、actual resulting 40-character HEADで別fresh Red review |
| S01 | committed | S01 allowed code／tests、mechanical artifact whitespace fix、report evidence | fresh code-reviewer pass | commit `c597bd146c1d68e619cdc1e24b1b76dd405fe36a`、origin push成功、post-commit clean、local／remote parity | S01 closed。S02 work packetへ進む |
| S02 | committed | S02 allowlisted runtime／Prompt resources／testsとreport evidence | final fresh code-reviewer pass、findings 0 | commit `796a1ce4c8b4f2161f0d646cf45f3afc6aaf40e2`、origin push成功、post-commit clean、local／remote parity | S02 closed。S03 ChatGPT work packetへ進む |
| S03 | committed | S03 allowlisted runtime／Prompt resource／testsとReport execution evidence | final fresh code-reviewer pass、findings 0、confidence 0.97 | commit `70fe45acdf0002ec399343f7d11dba0e87856700`、origin push成功、post-commit clean、local／remote parity | S03 closed。S04 ChatGPT work packetへ進む |
| S04 | committed | S04 17-path Review／revision runtime、Prompt resources、tests、Report execution evidence | final fresh code-reviewer pass、findings 0、confidence 0.95 | commit `6042553343225541709f71e74eeeca549ead2089`、origin push成功、post-commit clean、local／remote parity | S04 closed。S05 ChatGPT work packetへ進む |
| S05 | implementation complete; commit pending | S05 exact 5-path runtime／testsとReport execution evidence | final fresh code-reviewer pass、findings 0、confidence 0.97 | focused 77、PA-NF 17、retry 9、rollback 12、regression 225、static／validate／sync／diff／allowlist pass | milestone commit／push／parity後にS05をclosedとしS06 ChatGPT具体化へ進む |

## 最終品質ゲート（Final Quality Gate / 必須）

| ゲート | 対象 | 観測結果 | 証跡 / 次アクション |
|---|---|---|---|
| Docs Impact S90 | docs、templates、README、workflow、skill、migration notes | not started | S01〜S09 closure後に判定 |
| Final QA | issue-wide obligation coverage | not started | S90後にfresh qa-reviewer |
| Final Code Review | integrated code and tests | not started | step-local review後にfresh issue-wide code-reviewer |
| Final Spec Review | Requirement、Design、Plan、Report、implementation、tests、docs alignment | failed | latest: `artifacts/20260727t033431z-chatgpt-fresh-canonical-review-fail.md` against exact published HEAD `3fc0e61ef8425abc0b4a5488d51e7060b0ed03cc`; bounded correction後にnew exact HEADで別fresh review |
| Final Commit | final report ledger and issue-wide closure | blocked | S99とfresh final reviewsのpass後に実施 |

## 遭遇した問題と解決

- Candidate v15のfresh Red Team PASSはCandidate review-cycle evidenceであり、canonical readinessの代替にならない。
  - Human adoption後、fresh canonical specialistsと`spec-reviewer`を実行し、9件のP1をowner文書へ反映した。
- initial canonical placementには`.assurance.json`がなく、workflow guidanceが`design-not-substantive`を返した。
  - assurance classifyでcurrent三文書へstandard／provisionalを再束縛し、verifyをpassさせた。compose dry-runはsubstantive owner文書とのconflictを安全に検出したため書込みを行わなかった。
- review passを修正者が自己宣言するとreviewer gateが循環する。
  - 本書は直近の正式failを保持し、修正版を別のfresh `spec-reviewer`へ渡す。PASS取得後にだけauthoring、specialist、reviewer rowsを更新し、さらにfresh final reviewで統合後のReportを検証する。

## 学んだこと

- Candidate review、Human adoption、canonical review、execution readinessは別々のauthority gateとして記録しなければならない。
- post-commit publication failureはcanonical rollbackではなく、operation identityを保ったresumeとして扱う必要がある。

## 今後の推奨事項

- S01以降は`plan.md`のstep順、exact allowlist、required closure rowを守り、各stepをfresh reviewしてから次へ進む。

## 省略/例外メモ (必須)

- 今回の例外は、ユーザーがCodex Mainによるcanonical planning repairを直接承認したことだけである。製品実装のdelegation、review、Human-only live mutation gateは省略しない。
