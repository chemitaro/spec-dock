---
種別: 実装報告書（Issue）
ID: "iss-00334"
タイトル: "Implement ChatGPT Issue Planning Workflow"
関連GitHub: ["#334"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-30"
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
| D-20260728-S06-JIT | resolved | implementation | Human JIT contract / ChatGPT Pro | S01〜S05のprovider実装を実bootstrap、installed resource、init／update、配布物、dogfood projection、full fake E2Eへ接続する具体化が必要だった | 新public contract; generic DI; S06-local projection／integration closure | public CLI／schema／canonical三文書を変更せず、4 planning callableの実bootstrap配線、closed two-layout resource解決、fixed-sibling Review evidence、実行権限修復、provider-first projectionで閉じる | ChatGPT ProがGitHub connectorでexact remote HEADを照合し、4件のimplementation-local integration defectとclosed allowlistを特定してimplementation-ready／review-waivedと判定した | applied as execution input | `artifacts/20260728t075945z-s06-chatgpt-implementation-work-packet.md`; source HEAD `2ab5fedc7117218e2189d26eff8684455aadf33d` | artifact／Reportをcommit・push後、bounded dev-coderへ渡す |
| D-20260728-S07-JIT | blocked at Human gate | operation | Human JIT contract / ChatGPT Pro | real Issue dogfoodとDeliveryを、既完成planning docsの循環上書きや権限推定なしで実行する必要がある | archive self-adoption; git-bound decision-only adoption; live run省略 | `iss-00334`はgit-bound限定で条件付きeligible。archive applyは禁止し、initial live-run authorizationと後段exact Human decisionを別gateにする | ChatGPT ProがGitHub connectorでexact remote HEADを確認し、target／worktree／mode／evidence root／mutation scope／decisionが未固定のため`STOP_AT_HUMAN_GATE`と判定した | execution input recorded; live mutation blocked | `artifacts/20260728t100524z-s07-chatgpt-execution-work-packet.md`; source HEAD `3bc0b8bada9b07ebc85f8cf29e15e361bd204f12` | packet／Reportをcommit・pushし、read-only preflight後にHuman authorization recordを求める |
| D-20260729-OB013 | resolved | architecture boundary | Human / ChatGPT Pro / Codex Main | 現行product adapterが個人`chatgpt-use` wrapper絶対パスとwrapper固有text outputへ依存し、exact branch／Prompt／ZIP outputの製品境界を満たしていなかった | 個人wrapper依存を維持; Oracle本体を改造; provider-owned adapterからPATH Oracleをdirect argvで利用 | 計画作業ではoperator-local `chatgpt-use`を利用してよいが、製品runtimeはPATH上のOracle本体だけへ依存する。参考wrapperの知見は再実装できるが、個人path／Project／profile／config／wrapper ABIを製品契約へ持ち込まない | 配布可能性、exact source binding、複数Markdown ZIP出力を同時に満たし、既存Candidate／Review／Human Gate／apply安全境界を維持できる | applied | `artifacts/20260729t004625z-research-oracle-dependency-boundary-current-and-target-state.md`; `artifacts/20260729t-iss-00334-oracle-boundary-planning-amendment-v1.zip`; ChatGPT conversation `6a6953e8-aef0-83ee-8517-63d364bb710a` | S08以降の追加計画を順に実装する |
| D-20260729-S08-JIT | resolved | implementation | Human JIT contract / ChatGPT Pro | S08のPATH Oracle、capability preflight、single submit、same-session recovery、typed artifact snapshotをbounded worker inputへ具体化する必要があった | canonical amendment; S09以降の先取り; S08-local infra／domain work packet | canonical meaningを変えず、provider infra／domainとfocused testsだけのallowlist、17 Red seeds、実装順、stop conditionsを固定する | ChatGPT ProがGitHub connectorでexact remote HEADを確認し、現行personal wrapper／`--write-output` active dependencyと既存bootstrap seamをsource上で照合して`GO`と判定した | applied as execution input | `artifacts/20260729t054034z-s08-chatgpt-implementation-work-packet.md`; source HEAD `08aa8f564f7265a64ce772d50d56ff1fb8ffd185`; session `iss00334-s08-jit` | artifact／Reportをcommit・push後、bounded dev-coderへ渡す |
| D-20260729-S08-COMPAT | resolved | temporary compatibility | ChatGPT Pro | S08 typed Oracle outputへの置換で、S10がownerであるapplication／fakeのlegacy `transient_payload`利用が30 regression failuresとなった | S08でapplicationまで移行; typed contractを延期; S10までの非永続compatibility view | production direct adapterはtyped-onlyを維持し、domain resultだけにdeprecated／nonserialized legacy-only constructor laneとtyped bytes compatibility viewをS10まで残す。typed＋legacy、複数typed、payloadなし、non-pass payload、size／hash mismatchは拒否する | canonical三文書とS08／S10 ownershipを変えず、S08差分をboundedにGreenへ戻せる。typed Planner ZIPを未変更applicationへ渡すとfail closedしCandidate publication 0となることを確認する | applied temporarily | `artifacts/20260729t062209z-s08-chatgpt-compatibility-decision.md`; SHA-256 `ef0628876101c15c0295b861546b8b65eb9ce38c74053e3632ec66f570e10669`; session `iss00334-s08-compatibil-decision-r1` | S10でapplication／fakesをtyped outputへ移行しcompatibility laneを削除する |
| D-20260729-S08-BOUND | resolved | implementation-local resource bound | fresh ChatGPT P1-005 / dev-coder / Codex Main | S08はZIP internal root確認時の無制限展開を防ぐ必要があるが、S10の完全Candidate inventory／CRC検証を先取りできない | compressed 64 MiBだけ; entry別だけ; entry数／single／total／ratioのcentral-directory複合上限 | entry 2,048、single uncompressed 16 MiB、total uncompressed 64 MiB、compression ratio 200をentry read前に適用し、`testzip()`は実行しない | 通常のMarkdown planning bundleへ十分な余裕を残しつつ、S08の資源消費を有限化する最小実装である。public contractではなくprivate定数なので、実測Candidateに基づきS10で再評価できる | accepted as implementation-local | P1-005 tests in `tests/unit/infra/test_issue_planning_oracle_artifact.py`; EAL-20260729-S08-REVIEW-1 | S10で実Candidate evidenceと完全inventory contractに照らして維持／調整を再評価する |
| D-20260729-S09-JIT | resolved | implementation | Human JIT contract / ChatGPT Pro | S09のPrompt本文authority、exact current branch、role別output、reference-only attachment、onboarding companion義務をbounded worker inputへ具体化する必要があった | canonical amendment; S10以降の先取り; S09-local Prompt／application／infra／domain work packet | canonical meaningを変えず、9 production/resource paths＋5 focused test paths、21 Red cases、implementation sequence、12 stop conditionsを固定する | ChatGPT ProがGitHub connectorでexact remote HEAD `1bc4109c094137bd2b42f9f09273ac0451aaf59d`のidentical／ahead 0／behind 0を確認し、S08 typed/recovery seamとcurrent active Prompt defectsをsource上で照合して`GO`と判定した | applied as execution input | `artifacts/20260729t084028z-s09-chatgpt-implementation-work-packet.md`; source artifact SHA-256 `21f02add7bc395053f52f94d7a4d33048cac0ff0207ee5617ba6cd5f33f8ffd5`; session `iss00334-s09-jit-recovered-1bc4109c` | artifact commit／push後、bounded dev-coderへS09だけを渡す |
| D-20260729-S10-JIT | resolved | implementation | Human JIT contract / ChatGPT Pro | S10のtyped authoring ZIP、guide-inclusive Candidate、closed git-bound binding、same-Candidate Review／apply、Human後companion transactionをbounded worker inputへ具体化する必要があった | canonical amendment; S11 projection／distribution先取り; S10-local domain／application／infra／command work packet | canonical meaningを変えず、7 production paths＋9 test paths、closed schemas、Red matrix、implementation sequence、19 stop conditionsを固定する | ChatGPT ProがGitHub connectorでexact remote HEAD `aad5e2108b03d01c9efb506675ac58dce4845eb5`のidentical／ahead 0／behind 0を確認し、current Candidate／Review／Human／apply／recovery seamsをsource上で照合して`GO`と判定した | applied as execution input | `artifacts/20260729t104419z-s10-chatgpt-implementation-work-packet.md`; repository artifact SHA-256 `4b65f14306414684b9040a3e6e033c9690561558cdeb51421814941cdd91637c`; source transcript SHA-256 `7fb10a296328bddd89b62413cae32275b7c9c0b053485308f45b3b455f0007c4`; session `iss00334-s10-jit-aad5e210` | artifact／Report commit・push後、bounded dev-coderへS10だけを渡す |
| D-20260729-S10-ALLOWLIST | resolved | implementation ownership | ChatGPT Pro / Codex Main | S10のapplication契約を直接検証する既存test fileがwork packetのtest allowlistから漏れていた | testを除外して実装; canonical Planを改訂; S10 test allowlistへ既存1 pathだけ追加 | `tests/unit/application/test_issue_planning_apply.py`だけをS10 test allowlistへ追加し、production allowlistとcanonical三文書は変更しない | same-Candidate git-bound apply、canonical byte identity、companion transactionをS10 ownerのapplication境界で検証する既存fixtureであり、S11以降の先取りではない | applied as bounded execution input | `artifacts/20260729t120603z-s10-chatgpt-allowlist-amendment-go.md`; commit `4ecdeaf5c108a1d8cf6dd08e222bddce366b7755` | effective 10-test-path suiteで検証する |
| D-20260729-S10-REASON | resolved | test contract | ChatGPT Pro / Codex Main | wrong canonical paths caseの期待reasonが、strict Review result parsingの実際のownerと不一致だった | production reasonを変更; test caseを削除; expected reasonだけをparser contractへ同期 | paths caseだけ`review_result_rejected`を期待し、HEAD caseは`review_identity_rejected`を維持する | malformed canonical pathsはidentity照合前のstrict `PlanningReviewResult` parsingで拒否されるため、現行fail-closed順序を正しく記録する | applied | `artifacts/20260729t125606z-s10-chatgpt-reason-owner-decision-go.md`; decision commit `bff38edb5158431e23d69d03f620b12875536295`; repair commit `28155c618f04bb0dc5830b1d206eb10303baf770` | fresh S10 defect-only reviewで確認する |
| D-20260729-PROMPT-TUNING | deferred until functional implementation closure | post-implementation refactor | Human | ChatGPT 5.6 Proへ送る合成Prompt／templateを、機能実装後に公式prompting guideへ整合させて最適化する | S11前に先取り; contract変更を伴う再設計; S12後のprompt-only tuning | S11／S12の機能実装を優先し、完了後にOpenAI公式GPT-5.6 prompting guideを確認して、現行schema／authority／safety contractを変えないprompt-only refactorとしてadmissionする | 未完成の機能境界とPrompt品質を同時に動かさず、現行挙動をbaselineにして比較可能なtuningを行うため | deferred | Human direction 2026-07-29; `https://developers.openai.com/api/docs/guides/latest-model` | S12機能検証後、S13 evidence commit前にscope／evaluation corpus／acceptanceを具体化する |
| D-20260729-S11-JIT | resolved | implementation | Human JIT contract / ChatGPT Pro | S11のprovider authority、official projection、distribution、legacy test migration、denylistを一つのbounded worker inputへ具体化する必要があった | Prompt tuning先取り; S12 full/live closure; provider runtime再設計; S11 distribution/projection work packet | current provider Prompt/runtimeはfunctional authorityとしてread-onlyに保ち、4 authority docs、4 tests、Red-backed installer fallback、mechanical projection、fake PATH Oracle E2Eへ限定する | ChatGPT ProがGitHub connectorでexact remote HEAD `7e4257955af699cbad456a53cd3be06cb2871527`のidentical／ahead 0／behind 0を確認し、known S11 parity／obsolete import failureとcurrent provider/dogfood driftをsource上で照合して`GO`と判定した | applied as execution input | `artifacts/20260729t144732z-s11-chatgpt-implementation-work-packet.md`; SHA-256 `4b6604934fdb5ff6ab6c38d25253f101b1e08cb811fcad4e20f8a6db9697b2c8`; session `iss00334-s11-jit-retry` | artifact／Report commit・push後、bounded dev-coderへS11だけを渡す |
| D-20260729-S12-JIT | resolved | verification and live gate | Human JIT contract / ChatGPT Pro | S12のhermetic／distribution／static／guide／live順序と、旧S07 authorizationの現HEADへの適用可否を実行可能なwork packetへ具体化する必要があった | 旧authorizationを暗黙再利用; liveを先行; Prompt tuningを先取り; S12-local verification packet | exact pushed HEADでhermetic/read-onlyを即時開始し、real Oracle create以降はcurrent HEAD／target／evidence root／mutation scopeへbindしたrefreshed Human authorizationで停止する | ChatGPT ProがGitHub connectorでexact remote HEAD `ad36524d3d48545690cc7ef9f73a8bfe11ad11ff`のidentical／ahead 0／behind 0を確認し、Plan §22／§28.4とcurrent implementationへ照合して`GO_HERMETIC_THEN_HUMAN_GATE`と判定した | applied as execution input | `artifacts/20260729t170420z-s12-chatgpt-implementation-work-packet.md`; raw transcript SHA-256 `721a3b125455e68e6a3feedf2261cb5e100855ec1a12a0d8a93cdb3342d103ac`; session `iss00334-s12-jit`; model `requested=Pro`／`resolved=Pro`／`verified=yes` | artifact／Reportをcommit・push後、worker-safe hermetic verificationを開始し、real create前にrefreshed Human gateで停止する |
| D-20260729-S12-STATIC-REPAIR | resolved | bounded static blocker repair | S12 ChatGPT Pro continuation / Codex Main | clean HEADの`make lint`がRuff format corpusとmypy 15 errors／6 filesでfailし、PlantUML 1.2026.6 executable checkも未実証だった | baseline waiver; broad refactor; lint config緩和; exact mechanical／typing／external-tool repair | Ruff reported path setをfreezeしてmechanical formatし、provider `backend_invoke.py` 1件とtest 5件のtypingだけを修正、official updateでcounterpart 1件をprojectionする。PlantUMLは外部workspaceへchecksum検証付きで取得する | 同一S12 conversationがexact remote HEAD `6af86ac02a26970f5ca9050089cea2fab80ccff3`を確認し、public contract／schema／Prompt／canonical変更なしで`GO_BOUNDED_STATIC_REPAIR`と判定した | applied as bounded repair input | `artifacts/20260729t172438z-s12-chatgpt-static-blocker-repair-packet.md`; raw transcript SHA-256 `dfbc52e0c807b153488caf5a68b7f50662705fdc0e3925d70dca6199671378f7`; continuation session `required-repository-connector-context-github-2`; parent model evidence `requested=Pro`／`resolved=Pro`／`verified=yes` | artifact／Report commit・push後、bounded dev-coderへstatic repairだけを渡す |
| D-20260730-S014-SCOPE | resolved | review scope / threat and concurrency model | fresh Code reviewer / ChatGPT Pro / Codex Main | private `0700` workspace内部のsame-UID tampering、またはatomic replacement後の旧open FD writeをP1 retention対象にするか | current contractのP1としてretained storageを実装; cooperative lockingを追加; canonical model外として明示処分 | S014 3 findingとpost-exchange stale-FD findingはcurrent P0／P1として不採用。要件化する場合だけ独立Issueでthreat／concurrency model、retention authority、capacity／purge、cross-filesystem eligibilityを先に設計する | canonical Requirement／Designはpublic／canonical driftとexact preimageをatomic replacement boundaryまで要求するが、private same-UID security isolationや交換後旧inode write retentionを定義していない。保証は永続retained storageまたはlockingを追加しdefect-only review範囲を超える | rejected as current defect; residual risk accepted | `artifacts/20260730t202539z-disc-s014-private-same-uid-threat-scope-disposition.md`; `artifacts/20260730t202538z-pr-351-s014-private-entry-final-cas-chatgpt-concretization-not-adopted.md` | Humanがthreat／concurrency model拡張を要求した場合だけ独立Issue化。現PRのbranch mutationなし |
| D-20260730-S015-CONTENTION | resolved | review scope / repeated canonical contention | fresh Spec reviewer / Codex Main | one-shot exchange-back中に第三のatomic replacementが発生した場合、canonical pathnameが常に最新attachmentを指す保証までP1とするか | unbounded retry; cooperative locking／CAS／retained storage; bytesとevidenceを保持してrecovery_requiredで停止 | 一回の通常並行置換はS015で復元する。compensation中の再置換は全observed bytesを保持し、`recovery_required/restore_mismatch`でcommit／pushせず停止する。canonical pathnameのcontinuous-latest保証はcurrent P0／P1 scopeへ追加しない | canonical Requirement／Designは復元未確認時のfail-closed Human recoveryを要求する。継続中multi-writer下のlatest-pointer保証には新しいlocking／retention／retry architectureが必要でdefect-only reviewを超える | no_action; issue-local residual risk accepted | `artifacts/20260730t212559z-disc-s015-repeated-canonical-contention-boundary.md`; S015 fresh Spec review | 無停止multi-writer保証をHumanが要求した場合だけ独立Issue化。現PRのbranch mutationなし |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

`adoption_status` は `adopted`、`partially_adopted`、`rejected`、`deferred` のいずれかを用いる。`stale` または `blocked` の未解決entryはpromotionとimplementation startを止める。

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-20260726-V15-REVIEW | adopted | fresh Red Team read-only review | Candidate v15 review-cycle closure | exact Candidate identity、source HEAD、127件のpreflight、RP-01〜RP-07を独立確認したためreview evidenceとして採用した | `artifacts/20260726t164628z-chatgpt-output-v15-fresh-red-team-review.md`; `artifacts/20260726t164657z-disc-v15-red-team-pass-admission.md` | canonical reviewで現在の正本を再検証する |
| EAL-20260727-V15-ADOPTION | adopted | Human decision and reviewed Candidate ZIP | canonical `requirement.md`、`design.md`、`plan.md`、supporting artifacts | Humanの正式配置指示、source blob parity、exact ZIP SHAを満たしたためcanonical contentへ採用した | `artifacts/20260726t225541z-disc-v15-human-adoption-decision.md`; `artifacts/20260726t154840z-iss-00334-issue-planning-candidate-v15.zip` | canonical planning repairとfresh reviewを実施する |
| EAL-20260727-SPECIALISTS | adopted | system-architect and implementation-planner read-only reviews | `design.md` and `plan.md` amendment | public route、transaction、archive closure、Closure Index、step ownership、live boundaryの欠陥がsourceと整合したため全件採用した | `artifacts/20260726t235800z-review-system-architect-fail.md`; `artifacts/20260726t235801z-review-implementation-planner-fail.md` | amendmentをfresh spec-reviewerへ渡す |
| EAL-20260727-CANONICAL-FAIL | adopted | fresh spec-reviewer read-only review | canonical planning repair | 9件のP1がRequirement、Design、Plan、Assurance、Reportの実証可能な欠陥だったため全件採用した | `artifacts/20260726t235522z-review-canonical-spec-review-fail.md` | P1-01〜P1-09修正後にfresh re-reviewする |
| EAL-20260727-MAIN-REPAIR | adopted | Human-authorized Codex Main repair | `requirement.md`、`design.md`、`plan.md`、`.assurance.json`、`report.md` | ユーザーが今回に限りCodex Mainによる仕様修正を明示承認し、採用済みP1のowner文書を最小範囲で更新した | `requirement.md`; `design.md`; `plan.md`; `.assurance.json`; 本書のDecision Ledger | fresh spec-reviewerの正式判定を取得する |
| EAL-20260730-S014 | rejected | fresh Code review and ChatGPT Pro S014 advisory | current `iss-00334` implementation scope | same-UID private workspace tamperingのrisk分析はevidenceとして保持するが、retained-storage architectureはcanonical threat model外でありcurrent defect repairへ採用しない | `artifacts/20260730t202538z-pr-351-s014-private-entry-final-cas-chatgpt-concretization-not-adopted.md`; `artifacts/20260730t202539z-disc-s014-private-same-uid-threat-scope-disposition.md`; D-20260730-S014-SCOPE | current PRではno-action。Humanがthreat modelを拡張する場合だけ独立Issue planningへ渡す |
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
| EAL-20260728-S06-PACKET | adopted | ChatGPT Pro with GitHub connector | S06 bounded implementation input | remote branchとexact HEAD `2ab5fedc7117218e2189d26eff8684455aadf33d`のidentical／ahead 0／behind 0を確認し、provider projection、real bootstrap wiring、distribution／installed parity、3 full fake chainsをpublic contract拡張なしで具体化した | `artifacts/20260728t075945z-s06-chatgpt-implementation-work-packet.md`; SHA-256 `5899b5120b1c975d38262f8c86e929af8998133aa49747d6c7f04af029fd1bf0`; Oracle session `iss00334-s06-implementa-brief` | exact production／test allowlistとmechanical dogfood projectionをbounded dev-coderへ渡す |
| EAL-20260728-S07-PACKET | adopted | ChatGPT Pro with GitHub connector | S07 bounded execution input | remote branchとexact HEAD `3bc0b8bada9b07ebc85f8cf29e15e361bd204f12`のidentical／ahead 0／behind 0、Issue #334 open、existing PRなしを確認し、safe preflight、initial Human authorization、git-bound create／Review、exact decision／apply、Delivery境界を分離した | `artifacts/20260728t100524z-s07-chatgpt-execution-work-packet.md`; SHA-256 `7419cb1a285762edf3d442f62d118d3ced7021da5fdc8c871188b13ef0433ca4`; Oracle session `iss00334-s07-implementa-brief` | read-only preflightだけを実施し、live commandsはHuman gateで停止する |
| EAL-20260729-ORACLE-BOUNDARY | adopted | ChatGPT Pro Blue Team authoring through operator-local `chatgpt-use` | Epic Requirement／Design、Issue Requirement／Design、Issue Plan amendment | GitHub connectorでbranch `iss-00334-implement-chatgpt-issue-planning-workflow`、source HEAD `a68eefa6881440d276c2bbfe415e01417a964128`を確認し、product dependencyとplanning operator toolを分離した5文書ZIPを生成した。Mainがexact inventory、ZIP SHA、Issue Plan prefix、scope、PlantUML、SpecDock validationを独立確認した | `artifacts/20260729t-iss-00334-oracle-boundary-planning-amendment-v1.zip`; ZIP SHA-256 `9fc16cc1bc2e5ee45576a64e863448c9c1247e0ec31cce0a8d5912881ef2d552`; conversation `6a6953e8-aef0-83ee-8517-63d364bb710a`; `artifacts/20260729t020725z-review-oracle-boundary-planning-pass.json` | S08以降だけを未実施作業として扱い、S01〜S07の実施履歴を保持する |
| EAL-20260729-S08-PACKET | adopted | ChatGPT Pro with GitHub connector | S08 bounded implementation input | exact remote HEAD `08aa8f564f7265a64ce772d50d56ff1fb8ffd185`の一致とdefault branch fallback 0を確認し、approved S08をprovider infra／domain、focused tests、17 Red seeds、closed stop conditionsへ具体化した | `artifacts/20260729t054034z-s08-chatgpt-implementation-work-packet.md`; SHA-256 `4808c3dcc40d34fe187e0a6a6b90b821d81278ea25378932f83c7d00e5a7fb6e`; Oracle session `iss00334-s08-jit` | artifact／Reportをcommit・push後、bounded dev-coderへ渡す |
| EAL-20260729-S08-COMPAT | adopted | fresh ChatGPT Pro implementation decision with GitHub connector | S08 domain compatibility seam only | S08実装で発見した30 application regression failuresをexact owner splitへ照合し、S10までのbounded temporary compatibility contractだけを`GO`とした | `artifacts/20260729t062209z-s08-chatgpt-compatibility-decision.md`; SHA-256 `ef0628876101c15c0295b861546b8b65eb9ce38c74053e3632ec66f570e10669`; Oracle session `iss00334-s08-compatibil-decision-r1` | S08 fresh implementation review後に確定し、S10削除義務を維持する |
| EAL-20260729-S08-REVIEW-1 | adopted | fresh ChatGPT Pro read-only defect review with GitHub connector | pushed S08 implementation `cdfb47171d921ff9f5e28c675de75b2ae52921da` | exact branch／HEADとreview deltaを確認し、現行S08 contractを直接破る5 P1だけを報告した。改善提案、S11 integration migration、S10 compatibility除去はscope外とした | `artifacts/20260729t070100z-s08-chatgpt-fresh-code-review-fail.md`; SHA-256 `f73da5960749f3055511dd144e323c022b40ca902ac2eef1db3468d0698ad813`; session `iss00334-s08-fresh-code-review-3`; model `requested=Pro`／`resolved=Pro`／`verified=yes` | P1-001〜005をsame bounded dev-coderへ渡し、新commit／push後に別fresh ChatGPT reviewを行う |
| EAL-20260729-S08-REVIEW-2 | adopted | fresh ChatGPT Pro read-only closure review with GitHub connector | pushed S08 repair `2f2b35f10d5480a328581fcf31c857d84f3a4937` | exact branch／HEADとrepair deltaを確認し、P1-001／003／005をclosed、P1-002／004を限定的にopen、新規P0／P1 0と判定した | `artifacts/20260729t074000z-s08-chatgpt-fresh-closure-review-fail.md`; SHA-256 `36b4556c074b6c8c95fb65d61aad8e25310de20a5d109e43542051156bc544c5`; session `iss00334-s08-fresh-closure-review`; model `requested=Pro`／`resolved=Pro`／`verified=yes` | metadata `RecursionError`とPlanner typed constructor `ValueError`だけをsame workerへ戻す |
| EAL-20260729-S08-REVIEW-3 | adopted | fresh ChatGPT Pro read-only final closure review with GitHub connector | pushed S08 second repair `a297cda42fb356e91dd5c537010a83d66e199932` | exact branch／HEADのahead 0／behind 0とone-commit repair deltaを確認し、P1-001〜005をすべてclosed、新規P0／P1 0、S08 PASSと判定した | `artifacts/20260729t081648z-s08-chatgpt-final-closure-review-pass.md`; SHA-256 `802b83cd90d333424e551421a3222e28137df354cf01fee48e6e5de3a6a2a95e`; session `iss00334-s08-final-fresh-closure-2`; model `requested=Pro`／`resolved=Pro`／`verified=yes` | S08をcloseし、S09のJIT concretizationへ進む |
| EAL-20260729-S09-PACKET | adopted | ChatGPT Pro with GitHub connector | S09 bounded implementation input | exact remote HEAD `1bc4109c094137bd2b42f9f09273ac0451aaf59d`のidentical／ahead 0／behind 0とdefault branch fallback 0を確認し、approved S09をPrompt-body authority、3 role、reference-only attachment、exact branch hard failure、onboarding companion obligation、21 Red casesへ具体化した | `artifacts/20260729t084028z-s09-chatgpt-implementation-work-packet.md`; SHA-256 `21f02add7bc395053f52f94d7a4d33048cac0ff0207ee5617ba6cd5f33f8ffd5`; Oracle session `iss00334-s09-jit-recovered-1bc4109c`; artifact commit `9c8e7e58e0f422ce1b53f324cced0b07dbbd69db` | packet reviewはHuman指示により不要。exact allowlistとstop conditionsをbounded dev-coderへ渡す |
| EAL-20260729-S09-REVIEW-1 | adopted | fresh ChatGPT Pro read-only defect review with GitHub connector | pushed S09 implementation `dfb1a8e70b17ed94ddb3b4cd95e9da03a6562a43` | exact branch／HEADとbase-to-head rangeを確認し、near-match／malformed transcriptと有効ZIPの併存をsuccessへ落とすS09-R10違反1件だけをP1として報告した | `artifacts/20260729t094943z-s09-chatgpt-fresh-code-review-fail.md`; SHA-256 `00a75059cbf1cfa0ec6c5c003cb9195e3dcfac61f2d9faa979813bba45b64907`; session `iss00334-s09-fresh-defect-review`; model `requested=Pro`／`resolved=Pro`／`verified=yes` | S09-P1-001だけをsame bounded dev-coderへ戻し、新commit／push後に別fresh closure review |
| EAL-20260729-S09-REVIEW-2 | adopted | fresh ChatGPT Pro read-only closure review with GitHub connector | pushed S09 repair `bcc11ecc3ac6653c302bcc184fae8e61a52d5e87` | exact branch／HEADとone-commit repair rangeを確認し、S09-P1-001をclosed、新規P0／P1 0、S09 PASSと判定した | `artifacts/20260729t100603z-s09-chatgpt-fresh-closure-review-pass.md`; SHA-256 `47aa35441ece0710d1743127780d6b51c565a0fb3842582504a3ec05be07c080`; session `iss00334-s09-fresh-closure-bcc11ecc`; model `requested=Pro`／`resolved=Pro`／`verified=yes` | S09をcloseし、S10のJIT concretizationへ進む |
| EAL-20260729-S10-PACKET | adopted | ChatGPT Pro with GitHub connector | S10 bounded implementation input | exact remote HEAD `aad5e2108b03d01c9efb506675ac58dce4845eb5`のidentical／ahead 0／behind 0とdefault branch fallback 0を確認し、approved S10をtyped authoring ZIP、guide-inclusive Candidate、closed operation binding、same-Candidate Review／apply、Human後transactionへ具体化した | `artifacts/20260729t104419z-s10-chatgpt-implementation-work-packet.md`; repository SHA-256 `4b65f14306414684b9040a3e6e033c9690561558cdeb51421814941cdd91637c`; Oracle session `iss00334-s10-jit-aad5e210` | packet reviewはHuman指示により不要。exact allowlistとstop conditionsをbounded dev-coderへ渡す |
| EAL-20260729-S10-ALLOWLIST | adopted | fresh ChatGPT Pro implementation decision with GitHub connector | S10 application test ownership | exact branch／HEADとwork packet、Plan、existing test ownershipを照合し、既存application test 1 pathの追加だけを`GO`とした | `artifacts/20260729t120603z-s10-chatgpt-allowlist-amendment-go.md`; commit `4ecdeaf5c108a1d8cf6dd08e222bddce366b7755` | production／canonical scopeを変えずeffective 10-test-path suiteへ含める |
| EAL-20260729-S10-REASON | adopted | fresh ChatGPT Pro implementation decision with GitHub connector | one-line S10 fixture expectation | exact branch／HEADとstrict parser／identity rejection orderを照合し、paths caseの期待reason 1行だけを`GO`とした | `artifacts/20260729t125606z-s10-chatgpt-reason-owner-decision-go.md`; commit `bff38edb5158431e23d69d03f620b12875536295`; repair `28155c618f04bb0dc5830b1d206eb10303baf770`; session `iss00334-s10-reason-decision-cooldown11` | pushed HEADを別fresh defect-only reviewへ渡す |
| EAL-20260729-S10-REVIEW-1 | adopted | fresh ChatGPT Pro read-only defect review with GitHub connector | pushed S10 evidence HEAD `0c1fa6ae2c28373281390491b24c0cf8be02a42d` | exact branch／HEADとS10 contractを確認し、guide completeness gateとpre-transaction Candidate reloadの2 P1だけを報告した。設計提案、P2／P3、S11以降は除外した | `artifacts/20260729t132842z-s10-chatgpt-fresh-code-review-fail.json`; SHA-256 `7d4f5a93af51e88db7386bea3a109555aae2b4a67d8f4356799ea8e7988122af`; session `iss00334-s10-fresh-defect-review`; model `requested=Pro`／`resolved=Pro`／`verified=yes` | S10-P1-001〜002だけをsame bounded dev-coderへ戻し、新commit／push後に別fresh closure review |
| EAL-20260729-S10-REVIEW-2 | adopted | fresh ChatGPT Pro read-only closure review with GitHub connector | pushed S10 repair `13ceae2e0e027d92b25c3eaff9d62fd334db1d92` | exact branch／HEADとone-commit repairを確認し、S10-P1-002をclosed、新規P0／P1 0とした。S10-P1-001は全conceptが同一sectionを再利用できる具体的bypassが残りopen | `artifacts/20260729t135925z-s10-chatgpt-fresh-closure-review-fail.json`; SHA-256 `6347a694e27be4b44e7f7cb09a1586ebd681289001ebf2099841c97c0961b4bc`; session `iss00334-s10-fresh-closure-review`; model `requested=Pro`／`resolved=Pro`／`verified=yes` | S10-P1-001のdistinct-section enforcementだけをsame bounded dev-coderへ戻す |
| EAL-20260729-S10-REVIEW-3 | adopted | fresh ChatGPT Pro read-only final closure review with GitHub connector | pushed S10 final repair `3a7df10575d3a8247e9e175fc24c02a3583a0e4a` | exact branch／HEADとfinal two-path repairを確認し、S10-P1-001／002をclosed、新規P0／P1 0、S10 PASSと判定した | `artifacts/20260729t141413z-s10-chatgpt-final-fresh-closure-review-pass.json`; SHA-256 `02ee81d35cb29042e44a824f620c4fe64f944edac569e515548eea69b699a5ce`; session `iss00334-s10-final-fresh-closure`; model `requested=Pro`／`resolved=Pro`／`verified=yes` | S10をcloseし、S11 ChatGPT JIT concretizationへ進む |
| EAL-20260729-S11-PACKET | adopted | ChatGPT Pro with GitHub connector | S11 bounded implementation input | exact remote HEAD `7e4257955af699cbad456a53cd3be06cb2871527`のidentical／ahead 0／behind 0とdefault branch fallback 0を確認し、approved S11をprovider authority、official update projection、distribution parity、fake PATH Oracle E2E、legacy migration、denylistへ具体化した | `artifacts/20260729t144732z-s11-chatgpt-implementation-work-packet.md`; SHA-256 `4b6604934fdb5ff6ab6c38d25253f101b1e08cb811fcad4e20f8a6db9697b2c8`; Oracle session `iss00334-s11-jit-retry` | packet reviewはHuman指示により不要。exact allowlistとstop conditionsをbounded dev-coderへ渡す |
| EAL-20260729-S11-REVIEW-1 | adopted | fresh ChatGPT Pro read-only defect review with GitHub connector | pushed S11 implementation `71628137a7665e59a11b14eca367e49d49bea39c` | exact branch／HEADとS11 implementationを確認し、fake Oracle E2E guideのroadmapがS07時点で止まったままReviewer PASS／readyへ進むfalse-positive 1件だけをP1として報告した | `artifacts/20260729t161123z-s11-chatgpt-fresh-code-review-fail.json`; SHA-256 `da45157271aa0aa97ad3d7b1a63e1eda41162a1454ef9db7279ee33cf4b33921`; session `iss00334-s11-review-manual-login`; model `requested=Pro`／`resolved=Pro`／`verified=yes` | S11-P1-001だけをsame bounded dev-coderへ戻し、新commit／push後に別fresh closure review |
| EAL-20260729-S11-REVIEW-2 | adopted | fresh ChatGPT Pro read-only closure review with GitHub connector | pushed S11 repair `3277f3e50c094523443cfd772a91f6c7b44a48ca` | exact branch／HEADとone-file repairを確認し、S11-P1-001をclosed、新規P0／P1 0、S11 PASSと判定した | `artifacts/20260729t164022z-s11-chatgpt-fresh-closure-review-pass.json`; SHA-256 `91e849167a3e136f67ffeb86a50d8eaa49e3d960366b2f263d23f5720f7e90f5`; session `iss00334-s11-closure-review`; model `requested=Pro`／`resolved=Pro`／`verified=yes` | S11をcloseし、S12のJIT concretizationへ進む |
| EAL-20260729-S12-PACKET | adopted | ChatGPT Pro with GitHub connector | S12 bounded verification and live-gate input | exact remote HEAD `ad36524d3d48545690cc7ef9f73a8bfe11ad11ff`のidentical／ahead 0／behind 0を確認し、hermetic→distribution→static／guide→Human-gated liveの順序、AC-001〜025 traceability、QA／security defect-only contractを具体化した | `artifacts/20260729t170420z-s12-chatgpt-implementation-work-packet.md`; SHA-256 `721a3b125455e68e6a3feedf2261cb5e100855ec1a12a0d8a93cdb3342d103ac`; Oracle session `iss00334-s12-jit` | packet reviewはHuman指示により不要。worker-safe verificationを開始し、real create前にrefreshed authorizationを取得する |
| EAL-20260729-S12-STATIC-REPAIR | adopted | same S12 ChatGPT Pro conversation with GitHub connector | observed S12 static blockers on `6af86ac02a26970f5ca9050089cea2fab80ccff3` | exact format path freeze、one provider typing repair、five test typing repairs、official one-file projection、external PlantUML 1.2026.6 verificationへ限定した | `artifacts/20260729t172438z-s12-chatgpt-static-blocker-repair-packet.md`; SHA-256 `dfbc52e0c807b153488caf5a68b7f50662705fdc0e3925d70dca6199671378f7`; session `required-repository-connector-context-github-2` | packet reviewは不要。changed-path guard付きdev-coder repair後にMainが`make lint`とPlantUMLを独立再検証する |
| EAL-20260730-LIVE-ADOPTION | adopted | public git-bound Issue Planning lifecycle and exact Human decision | live create／fresh Review／Human decision／apply | pushed source HEAD `f488121e80fc93f01cb64fab70a06d306c903804`でCandidateを生成し、same Candidateのfresh Review PASS、exact Human decision、byte-identical canonical apply、managed companion publication、commit／push、remote parityまで完了した | Candidate `iss-00334-v1-20260730t094713z`; Candidate ZIP SHA-256 `ee0b3be840f1de1cb182db4ee9685acba7cc90d277ceffa2f628edc07a18350a`; Review result SHA-256 `2a9c115c8ca6490d4b6e596ff805e72a140599976a5082eae9a59707bf41bc5c`; decision `artifacts/20260730t102056z-planning-human-decision-7ad8e5f063bc9e13.json`; adoption commit `a4cf67bf6b8d75e5fc1eb6d67a858db1a300d915` | exact current-HEAD final combined Reviewへ進む |
| EAL-20260730-FINAL-P1-REPAIR | partially_adopted | fresh ChatGPT Pro defect-only final Review、Human boundary correction、separate Blue Team concretization | `FINAL-P1-001`／`003` bounded repair | final Reviewのslug正規化差異とReport status不整合は採用した。Oracle-native config利用自体をproduct defectとした`FINAL-P1-002`はHuman clarificationにより不採用とし、HOME／config隔離を取り消した。別Blue Team sessionからsession ID固定点、focused tests、Report追補だけを採用した。pushed repair HEADのreal Oracle createで正規形sessionとCandidate回収を確認した | `artifacts/20260730t110415z-s14-fresh-final-combined-review-fail.md`; `artifacts/20260730t111338z-disc-oracle-local-configuration-boundary-correction.md`; Review session `iss00334-final-combined-review-a4cf67bf`; Blue session `iss00334-final-p1-blue-team`; `artifacts/20260730t110128z-final-p1-repair-chatgpt-blue-team-work-packet.md`; repair `65af92d0062d47c0fcbaba7ea79d2839ae062bf9`; live Candidate SHA-256 `4b1487db62ff97271471589e4f9e4ca12667d25ea94a1fd29841c86ae3bd4ee7` | live smoke closed。Report commit／push後にfresh closure Reviewを行う |
| EAL-20260730-FINAL-CLOSURE-PASS | adopted | fresh ChatGPT Pro defect-only closure Review | exact HEAD `5bd285377161b949247f2c3a9b3c6a800b2870c0` | exact GitHub branch／HEAD、provider／projection、tests、Report、Human boundary、previous FAILを確認し、`FINAL-P1-001` closed、`FINAL-P1-002` not-applicable-by-human-decision、`FINAL-P1-003` closed、新規P0／P1 0、merge-ready recommendation trueと判定した | `artifacts/20260730t115302z-s14-fresh-final-closure-review-pass.md`; session `iss00334-final-closure-5bd28537`; model `requested=Pro`／`resolved=Pro`／`verified=yes` | artifact／Reportをcommit／pushし、ready PR作成とfixed PR observationへ進む |

## 目的整合台帳（Objective Alignment Ledger / 必須）

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| canonical planning rebaseline | create→revise→review→Human Gate→apply→publicationのwalking skeletonをREQ-001〜REQ-014で定義する | exact Git binding、immutable Candidate、read-only review、safe transaction、provider parity、JIT dogfoodを保持する | medium。簡潔化で必要contractを落とす可能性があるため、実在欠陥だけを対象にfresh reviewする | current rebaselineは未レビュー。commit／push後にdefect-only fresh reviewが必要 |
| Oracle boundary amendment | 個人wrapper依存を除去し、PATH Oracle direct adapter、exact current branch、Prompt/reference分離、Planner ZIP outputを製品契約へ固定する | S01〜S07履歴、Candidate／Review／Human Gate／apply／publication contractを保持する | low。追加作業を既存計画末尾へ限定し、改善提案による再設計をfresh reviewの対象外とした | fresh defect-only `spec-reviewer` PASS、findings 0 |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | approved parent scope、current repository facts、P1-01を照合 | P0／P1だけをrevision trigger、P2／P3-onlyはCandidate不変 | REQ-001〜014へ再基準化しP1-01を修正 | passed | no | execute approved plan |
| design | existing primitives、provider ownership、P1-01を照合 | Review severityとRevisionRequest validationのownerを確定 | 14 design sectionsへ再基準化しP1-01を修正 | passed | no | execute approved plan |
| plan | Requirement／Design、P1-01を照合 | S04とS07でP2／P3 revision 0を検証 | S01〜S07へ再基準化しP1-01を修正 | passed | no | execute approved plan |
| requirement — Oracle boundary amendment | current adapter／tests、親Epic、Oracle境界調査、ChatGPT生成ZIP | productはOracle直接依存、計画operatorは`chatgpt-use`利用可と分離 | Epic／Issue requirementへ採用 | passed | no | design／plan amendmentを有効化 |
| design — Oracle boundary amendment | provider-first source、PATH Oracle、session file artifact、exact branch、Prompt/reference、ZIP contract | 個人wrapper知見はreference-only、製品fallbackにはしない | Epic／Issue designへ採用 | passed | no | S08以降の実装へhandoff |
| plan — Oracle boundary amendment | existing plan 16,178 bytes／SHA `de7690f…`と生成prefix、S01〜S07実施履歴 | 旧計画は改稿せずEOFへS08〜S14を追記 | append-only amendmentとして採用 | passed | no | S08から順に実装 |
| requirement — onboarding companion amendment | Human decision、current canonical三文書、v2〜v4 Candidate、exact GitHub source | guideはFormal Candidate payloadだが第四のcanonical specificationではない | Epic／Issue requirementへv4を採用 | passed、v4 findings 0 | no | design／plan contractを有効化 |
| design — onboarding companion amendment | direct Oracle boundary、same-Candidate operation binding、fresh Review findings | `repository/branch`をbinding authority、`source_repository/source_branch`をCandidate source identityへ限定 | Epic／Issue designへv4を採用 | passed、v4 findings 0 | no | S08以降で実装 |
| plan — onboarding companion amendment | 38,126／47,800／55,059-byte prefix chain、v4 Plan、PlantUML 1.2026.6 | 旧計画を改稿せず、companion／binding correctionをEOFへ追記 | append-only v4 amendmentとして採用 | passed、v4 findings 0 | no | S08から順に実装 |

過去のFAILは当時のsnapshotに対する履歴として保持する。current rebaselineの判定には流用せず、new exact HEADを別fresh reviewerが限定scopeで判定する。

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）

過去のauthoring／correction provenanceはEvidence Adoption Ledgerと各artifactに保持する。current gateはrebaseline後の三文書とfresh closure PASSだけを対象にする。

| ロール（created_by_role） | 範囲（scope_id） | ドラフトパス（artifact draft path） | 参照元（source_paths） | 予定反映先（intended_targets） | 採用状態（adoption_status） | 反映先（reflected_to） | 差分ガード結果（diff_guard_result） | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果（reviewer result） | 昇格判断（promotion decision） |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Codex Main | iss-00334 planning rebaseline | `artifacts/20260727t070853z-chatgpt-defect-only-closure-review-pass.json` | `requirement.md`; `design.md`; `plan.md`; parent Epic; prior Evidence Adoption Ledger | `requirement.md`; `design.md`; `plan.md` | adopted | `requirement.md`; `design.md`; `plan.md`; `.assurance.json`; `report.md` | `git diff --check`、`spec-dock validate`、assurance verify successful | manual authoring integration | review-derived overgrowth | none | passed | execute approved plan |
| ChatGPT Pro Blue Team | iss-00334 planning amendment and parent epic boundary | `artifacts/20260729t-iss-00334-oracle-boundary-planning-amendment-v1.zip` | current Epic／Issue docs、Oracle境界調査、relevant source／tests、reference-only `chatgpt-use` skill／wrapper | Epic `requirement.md`／`design.md`; Issue `requirement.md`／`design.md`／`plan.md` | adopted | Epic／Issue canonical docs、`.assurance.json`、本Report | ZIP SHA／inventory／UTF-8、Plan prefix SHA／cmp、PlantUML 1.2026.6、`spec-dock validate`、`git diff --check` pass | whole-file integration for four docs and append-only Plan adoption | inline transcript、個人環境値、default branch fallback、実装済みclaim | none | passed | execute approved plan |

S01 ChatGPT work packetはcanonical authoring draftではなく、Human指示に基づくreview不要のstep execution inputである。したがってDelegated Draft Evidenceへは分類せず、`EAL-20260728-S01-PACKET`とImplementation Delegation Gateで追跡する。

## グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）

Assurance classifierのauthorityは`standard`である。Issue-local overlayとして、untrusted archive、public command contract、multi-file transaction、credentialed live mutationにstrict相当のclosureを追加した。overlayの解除条件は、これら高リスク面が不要になったことをowner文書で示し、assurance再分類とfresh spec reviewを通すreviewed amendmentである。

| グレード（Grade） | 必要な専門家 / 代替（required specialist / fallback） | 使用状況（usage） | 証跡（evidence） | 鮮度 spec-reviewer 判定（fresh spec-reviewer verdict） | 実行可否（execution readiness） |
|---|---|---|---|---|---|
| standard | system-architect and implementation-planner | used | prior specialist artifacts、current三文書、`artifacts/20260727t070853z-chatgpt-defect-only-closure-review-pass.json` | passed | execute approved plan |
| standard — Oracle boundary amendment | ChatGPT Pro Blue Team authoring＋fresh defect-only `spec-reviewer` | used | `artifacts/20260729t-iss-00334-oracle-boundary-planning-amendment-v1.zip`; `artifacts/20260729t020725z-review-oracle-boundary-planning-pass.json` | passed | S08から追加実装可 |

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
| S06 | per-step defect-only code review | code-reviewer | fresh for final uncommitted S06 41-path diff | passed | no | S06 commit候補へ進む | findings 0、confidence 0.96。既知baselineを除き、provider-first projection、real bootstrap、fixed-sibling evidence、installer、installed fake E2EにP0／P1なし |
| Oracle boundary planning amendment | defect-only canonical spec review | fresh `spec-reviewer` | fresh for current uncommitted five-doc amendment | passed | no | authoring gate pass。S08以降へ進める | findings 0、confidence 0.99。4契約とPlan 16,178-byte prefixを確認。`artifacts/20260729t020725z-review-oracle-boundary-planning-pass.json` |
| S08 | per-step defect-only implementation review | fresh ChatGPT Pro read-only reviewer | fresh for pushed HEAD `cdfb47171d921ff9f5e28c675de75b2ae52921da` | failed | no | 5 P1をsame bounded dev-coderへ戻し、new immutable HEADでfresh re-review | recovery executable identity、metadata invalid／nonterminal分類、ancestor symlink race、parser exception正規化、ZIP decompression bound。`artifacts/20260729t070100z-s08-chatgpt-fresh-code-review-fail.md` |
| S08 | first fresh closure review | fresh ChatGPT Pro read-only reviewer | fresh for pushed HEAD `2f2b35f10d5480a328581fcf31c857d84f3a4937` | failed | no | open 2件だけをsame workerへ戻し、new immutable HEADで別fresh closure review | P1-001／003／005 closed、新規finding 0。P1-002はmetadata JSON `RecursionError`、P1-004は制御文字rootによるtyped constructor `ValueError`がopen。`artifacts/20260729t074000z-s08-chatgpt-fresh-closure-review-fail.md` |
| S08 | final fresh closure review | fresh ChatGPT Pro read-only reviewer | fresh for pushed HEAD `a297cda42fb356e91dd5c537010a83d66e199932` | passed | no | S08をcloseし、S09のJIT concretizationへ進む | P1-001〜005 closed、新規P0／P1 0、confidence high。GitHub connectorでexact branch／HEADのahead 0／behind 0とdefault branch fallback 0を確認。`artifacts/20260729t081648z-s08-chatgpt-final-closure-review-pass.md` |
| S09 | initial per-step defect-only implementation review | fresh ChatGPT Pro read-only reviewer | fresh for pushed HEAD `dfb1a8e70b17ed94ddb3b4cd95e9da03a6562a43` | failed | no | S09-P1-001だけをsame workerへ戻し、new immutable HEADで別fresh closure review | near-match／malformed／multiple transcriptと有効authoring ZIPの矛盾状態がsuccessへ落ちるS09-R10違反。`artifacts/20260729t094943z-s09-chatgpt-fresh-code-review-fail.md` |
| S09 | final fresh closure review | fresh ChatGPT Pro read-only reviewer | fresh for pushed HEAD `bcc11ecc3ac6653c302bcc184fae8e61a52d5e87` | passed | no | S09をcloseし、S10のJIT concretizationへ進む | S09-P1-001 closed、新規P0／P1 0、confidence high。exact sentinel／矛盾artifact／正常successの直接回帰を確認。`artifacts/20260729t100603z-s09-chatgpt-fresh-closure-review-pass.md` |
| S10 | per-step defect-only implementation review | fresh ChatGPT Pro read-only reviewer | fresh for pushed HEAD `0c1fa6ae2c28373281390491b24c0cf8be02a42d` | failed | no | S10-P1-001〜002だけをsame workerへ戻し、new immutable HEADで別fresh closure review | onboarding companion completeness gateが必須概念／sectionを省略でき、applyがpreflight後のexplicit Candidate差替えをtransaction直前に再検証しない。`artifacts/20260729t132842z-s10-chatgpt-fresh-code-review-fail.json` |
| S10 | first fresh closure review | fresh ChatGPT Pro read-only reviewer | fresh for pushed HEAD `13ceae2e0e027d92b25c3eaff9d62fd334db1d92` | failed | no | open S10-P1-001だけをsame workerへ戻し、new immutable HEADで別fresh closure review | P1-002 closed、新規P0／P1 0。P1-001は全mandatory conceptを単一sectionへ集約できるbypassがopen。`artifacts/20260729t135925z-s10-chatgpt-fresh-closure-review-fail.json` |
| S10 | final fresh closure review | fresh ChatGPT Pro read-only reviewer | fresh for pushed HEAD `3a7df10575d3a8247e9e175fc24c02a3583a0e4a` | passed | no | S10をcloseし、S11のJIT concretizationへ進む | P1-001／002 closed、新規P0／P1 0、confidence high。distinct 13-section matching、single-section bypass regression、P1-002非回帰を確認。`artifacts/20260729t141413z-s10-chatgpt-final-fresh-closure-review-pass.json` |
| S11 | per-step defect-only implementation review | fresh ChatGPT Pro read-only reviewer | fresh for pushed HEAD `71628137a7665e59a11b14eca367e49d49bea39c` | failed | no | S11-P1-001だけをsame workerへ戻し、new immutable HEADで別fresh closure review | fake guideが`S01-S07 complete／S08-S14 remain`のstale roadmapでもReviewer PASS／readyへ進むfalse positive。`artifacts/20260729t161123z-s11-chatgpt-fresh-code-review-fail.json` |
| S11 | final fresh closure review | fresh ChatGPT Pro read-only reviewer | fresh for pushed HEAD `3277f3e50c094523443cfd772a91f6c7b44a48ca` | passed | no | S11をcloseし、S12のJIT concretizationへ進む | S11-P1-001 closed、新規P0／P1 0。corrected roadmap、Candidate／companion identity、archive／git-bound Review binding、ready operation SHA／byte identityを確認。`artifacts/20260729t164022z-s11-chatgpt-fresh-closure-review-pass.json` |

## Assurance記録

- `./spec-dock/scripts/spec-dock assurance classify --stage requirement --issue iss-00334 --format json`: valid。`authorized_profile=standard`、`status=provisional`としてrebaseline後の三文書へ再束縛した。
- `./spec-dock/scripts/spec-dock assurance verify --issue iss-00334 --format json`: valid。
- source binding:
  - Requirement SHA-256: `aa349869f03953fbc57c587db9eb306e131b2cfa6889713e16f795642449901b`
  - Design SHA-256: `ef344a10f0e89b87b6cdb63fa18bc5faadacd6ab4d7b8e9e40352f6e434a967a`
  - Plan SHA-256: `3948deda169b155ea94fe2691b07add4671e5c5c5bbac13c7436c021040e3125`
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
| S06 | delegated | provider projection、real bootstrap wiring、distribution／installed／dogfood parity、3 full fake E2Eのbounded implementation | dev-coder | `plan.md` S06と`artifacts/20260728t075945z-s06-chatgpt-implementation-work-packet.md`のproduction／test allowlistおよびmechanical dogfood output set | canonical三文書、S01〜S05実装、S06 work packet | Red-first wiring／resource／revision／init-update／package parity、3 fake chains、unauthorized mutation 0、S01〜S05 regressions、fresh code review、exact diff allowlist | new public contract／schema／persistence／test-only production hook、prompt rewrite、canonical amendment、allowlist外変更、real ChatGPT／GitHub、実repo planning apply、S07が必要 | Red 5件とdogfood parity RedからGreen。direct S06 96、init/update 3、E2E 3、S01〜S05 342、Core 454 passed／1 skipped／1 pre-existing baseline failure。wheel／sdist／fresh init／update／installed parity、static、validate／sync／validate、41-path allowlist、forbidden mutation 0、fresh review pass。milestone commit `9206ab28d205b654603c8ecac2db7f89ee53bdeb`をpushしclosed |
| S07 | blocked at Human gate | real Issue git-bound dogfood、exact Human decision、Delivery PRのbounded execution | dev-coder／Main／Human | `plan.md` S07と`artifacts/20260728t100524z-s07-chatgpt-execution-work-packet.md` | canonical三文書、S01〜S06実装、S07 packet、fresh pushed HEAD | exact read-only preflight、initial authorization、external evidence identity、fresh defect-only Review、Human decision、`ready`／remote parity、issue-wide reviews、PR checks | initial authorization未完備、archive self-adoption、decision推定、HEAD drift、scope外mutation、P2／P3-only revision、merge／finish | packet disposition `STOP_AT_HUMAN_GATE`。packet／Report commit後のfresh exact HEADでread-only preflightを行い、Human record取得までlive planning commandを実行しない |
| S08 | closed | PATH Oracle direct adapter、capability preflight、single submit、same-session recovery、typed artifact snapshotのbounded implementation | same dev-coder | initial allowlist内のartifact helper／focused testsとopen P1-002／004だけ | canonical三文書、S01〜S07実装履歴、Oracle boundary amendment、S08 work packet、D-20260729-S08-COMPAT、EAL-20260729-S08-REVIEW-1〜3 | exact 2 Red／Green、S08 focused、application compatibility、ruff／format／mypy、runtime denylist、validate、diff check、fresh exact-HEAD closure Review | public contract変更、S09以降、Oracle本体変更、personal wrapper／API／shell fallback、旧frame API復活、P1 closureにS10／S11実装が必要 | exact 2 RedをGreen化。focused 127、application 66、CLI 2、親combined 195、ruff、mypy、validate、denylist、diff checkがpass。second repair `a297cda42fb356e91dd5c537010a83d66e199932`をpushし、fresh ReviewでP1-001〜005 closed／new P0/P1 0／PASSを確認 |
| S09 | closed | Prompt本文authority、exact branch、role別output、reference-only attachment、onboarding companion義務のbounded implementation | same dev-coder | S09 work packetのproduction／test allowlistとP1-001 repair | canonical三文書、S01〜S08実装、S09 work packet、EAL-20260729-S09-REVIEW-1〜2 | focused regression、static、validate、diff check、fresh exact-HEAD closure Review | S10 Candidate parsing／apply、S11 projection、public contract、canonical amendment | implementation `dfb1a8e70b17ed94ddb3b4cd95e9da03a6562a43`、repair `bcc11ecc3ac6653c302bcc184fae8e61a52d5e87`をpush。focused 274、fresh closure ReviewでP1-001 closed／new P0/P1 0／PASS |
| S10 | closed | typed authoring ZIP、guide-inclusive Candidate、closed binding、same-Candidate Review／apply、Human後companion transactionのbounded implementation | same dev-coder | S10 work packetの7 production paths、effective 10 test paths、P1-001／002 bounded repairs | canonical三文書、S01〜S09実装、S10 work packet、D-20260729-S10-ALLOWLIST、D-20260729-S10-REASON、EAL-20260729-S10-REVIEW-1〜3 | effective suite、full unit attribution、static、validate、diff check、fresh exact-HEAD closure Review | S11 projection／distribution、S12+、Prompt／Oracle adapter、canonical amendment、reviewによる改善提案 | implementation `211c73e9fca6292d120686504a3d33f3f10ba387`、first repair `13ceae2e0e027d92b25c3eaff9d62fd334db1d92`、final repair `3a7df10575d3a8247e9e175fc24c02a3583a0e4a`をpush。effective 387 passed、ruff／mypy／validate／diff check pass。fresh final ReviewでP1-001／002 closed、新規P0/P1 0、PASS |
| S11 | closed | provider authority、official projection、wheel／sdist／fresh init／update、docs／test migration、denylistのbounded implementation | same dev-coder | S11 work packetのauthority 4 paths、tests 4 paths、mechanical projection 17 pathsとS11-P1-001 repair | canonical三文書、S01〜S10実装、S11 work packet、D-20260729-PROMPT-TUNING、EAL-20260729-S11-REVIEW-1〜2 | Red-first S11 tests、official update、provider/dogfood parity、fake PATH Oracle E2E、wheel／sdist／fresh init／update、denylist、second-update no-op、fresh exact-HEAD closure Review | provider Prompt semantic change、S12 live/full closure、canonical amendment、personal wrapper／Oracle source、runtime/schema redesign、allowlist外path | implementation `71628137a7665e59a11b14eca367e49d49bea39c`、P1 repair `3277f3e50c094523443cfd772a91f6c7b44a48ca`をpush。S11 focused 121、S09/S10 418、Core/lifecycle 174、wheel／sdist／fresh init/update、parity、denylist、second-update no-opがpass。fresh closure ReviewでS11-P1-001 closed、新規P0／P1 0、PASS |
| S12 | closed／PR handoff pending | full verification、first-guide evidence、fresh QA／security、new-boundary git-bound live dogfood | Main／bounded read-only workers／Human | `plan.md` S12／28.4、S12 work packet、exact live evidence | canonical三文書、S01〜S11 closure、pushed source HEAD `f488121e80fc93f01cb64fab70a06d306c903804` | hermetic／full／distribution、live create、same-Candidate Review、exact Human decision、apply、commit／push、remote parity、final closure Review | canonical三文書変更、個人wrapper product依存、merge／close／finish | initial lifecycle、repair live smoke、fresh closure Review PASSまで完了。残りはartifact／Report publication、ready PR作成、fixed PR observationだけ |

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
- S06で、installed resource resolver、fixed-sibling Review evidence、real bootstrap wiring、init／update／distribution／dogfood parity、3 full fake chainsを追加した。full suiteで観測したstructural baseline 1件、dogfood cutover snapshot 2件、Issue 75 subprocess hangは開始HEADまたはS06外であり、期待値弱化やallowlist拡張をせず既存baselineとして分離した。
- S08で、typed Oracle resultへ切り替えるとS10 ownerのapplication／fakeがlegacy `transient_payload`を要求して30件失敗した。ChatGPTのbounded decisionに従い、production adapterはtyped-onlyのまま、S10までのdeprecated／nonserialized compatibility laneをdomain resultへ限定した。
- S08実装後の通常`uv run pytest`は、`tests/integration/test_issue_planning_chatgpt_transport.py`がS08で廃止した`classify_transport_frame`をcollection時にimportして停止した。このintegration test migrationはPlan S11のprovider／projection／test migration ownerに引き継ぎ、S08 allowlistを越えて旧frame APIを復活させない。

#### ステップ契約の完了証跡（Step Contract Closure）

S01〜S06の製品実装step closure evidenceを本書のImplementation Delegation Gate、Test Contract Closure、session log、Milestone Gateへ記録した。S03はREQ-004、REQ-012のCandidate生成部分、AC-001のCandidate生成部分、AC-006、AC-011を閉じた。S04はREQ-005〜007、AC-004〜005、Review／revisionに関するREQ-012をarchive／git-bound Review、Semantic／Mechanical N+1 Candidate、fresh re-Review、external evidence、mutation／race／non-leakage testsで閉じた。S05はREQ-008〜010、AC-002〜003、AC-007〜010、EC-003〜005、PA-NF-01〜10Bをdual authorization、decision-only rejection、whole-file／git-bound apply、rollback／recovery、planning-only commit／push／retry、fake remote testsで閉じた。S06はprovider／installed／dogfood projection、public command reachability、archive／git-bound／revisionの3 fake chains、distribution parity、unauthorized mutation 0を閉じた。commit、push、post-commit cleanはMilestone Gateで追跡する。

#### テスト契約の完了証跡（Test Contract Closure）

S06 direct 96、init／update 3、full fake E2E 3、S01〜S05 regression 342を実行し全件passした。Core／lifecycle／authoring exact laneは454 passed／1 skipped／1 starting-HEAD baseline failureだった。親セッションのexact S06 laneは11 passed、ruff、mypy、provider／dogfood byte parity、validate／sync／validate、41-path allowlist、forbidden mutation 0がpassした。S08 initialはfocused infra／domain 109、application 66、CLI smoke 2がpassした。first repairはfocused 125／combined 193、second repairはfocused 127、application 66、CLI smoke 2、親combined 195がpassし、ruff、mypy、validate nodes=223、runtime denylist、diff checkもpassした。通常suiteはS11 ownerの旧integration importでcollection停止したため、S08 closureではfocused regressionを正式証跡とし、S11でsuite collectionを復旧する。S07／S09以降／S99 ownerのtest contractは未実行であり、`plan.md`の各`tc-*`とSpec-Locked Closure Indexの対応を維持して実行した事実だけを追記する。

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
- S05 milestone commit `5f2edb93ab3e9e607abecf169f8167b0bd545f38`をoriginへpushし、local／remote parity、`git show --check`、post-commit clean worktreeを確認した。
- S05 product implementation、required verification、fresh review、commit、push、post-commit clean／remote parity checkは完了した。S05をclosedとし、S06 ChatGPT具体化へ進める。
- No material implementation decisions beyond the approved plan.

### セッションログ（2026-07-28 — S06 Provider Projection and End-to-End Regression）

- S05 closure evidence commit `2ab5fedc7117218e2189d26eff8684455aadf33d`をoriginへpushし、local／remote parityとpost-commit clean worktreeを確認した。
- ChatGPT UseのChrome host preflightがBash 3.2で大きな`launchctl print`結果をhere-stringへ渡す箇所で停止した。ユーザーの明示許可に基づき、外部helper `/Users/iwasawayuuta/.agents/libexec/oracle-chrome-host-preflight`の3箇所を`printf` pipeへ最小修正し、`bash -n`と実preflightで復旧を確認した。この外部運用修正はrepository差分に含めない。
- ChatGPT Pro session `iss00334-s06-implementa-brief`はGitHub connectorでrepository、branch、default branch、exact pushed HEAD `2ab5fedc7117218e2189d26eff8684455aadf33d`を確認し、branch comparisonをidentical／ahead 0／behind 0として照合した。model selection evidenceは`requested=Pro`、`resolved=Pro`、`verified=yes`である。
- ChatGPTはS06をprojection-and-integration milestoneと解釈し、実bootstrap未配線、installed prompt resource解決、fixed-sibling Review evidence ingress、`spec-dock-chatgpt` executable-bit repairの4件をimplementation-local defectとして特定した。new public command／option／schema／generic DIは不要であり、packet statusは`implementation-ready; packet review waived`である。
- 完全なtranscriptを`artifacts/20260728t075945z-s06-chatgpt-implementation-work-packet.md`へ保存した。trailing whitespace 1箇所の機械的除去後SHA-256は`5899b5120b1c975d38262f8c86e929af8998133aa49747d6c7f04af029fd1bf0`である。これはHuman指示によりreview不要のstep execution inputであり、canonical authoring draftではない。
- packetは9 production paths、6 test paths、official updateだけで更新可能なmechanical dogfood output setを定めた。prompt resource bytesと`pyproject.toml`は具体的なRed packaging defectがない限りread-onlyであり、canonical三文書、real ChatGPT／GitHub、実repositoryへのplanning apply、S07はout-of-scopeである。
- packet／Report commits `a1c9fe124626416e5659c8796d4722e8a320945d`、artifact whitespace／SHA correction `82902e2b7dd515c85931127dcb0b6e99c39e22a4`をoriginへpushし、clean／remote parityを確認してからbounded dev-coderへ委任した。
- Red-firstではinstalled resource resolver、fixed-sibling Review evidence 2件、revise help、real bootstrap wiringの5件を失敗として観測し、official update前のdogfood parityも意図したRedだった。
- provider最小実装後、4 planning callableをreal `UseCases`へ配線し、closed two-layout resource解決、固定sibling evidence、installer executable-bit repair、通常Skill／docs workflowを実装した。公開command／option／schema、generic DI、canonical三文書、S07は変更していない。
- official `uv run python -m spec_dock.cli update .`だけでroot Skill／resources／docs／runtimeを投影した。exact changed-path allowlistは41 paths、`.assurance.json`／Portfolio mutationは0、provider／dogfood scripts・docs・Skill byte parityはpassした。
- wheel／sdist build、fresh init／help／update、isolated wheel install／update／byte parityはpassした。host `python -m venv`のensurepip failureはproduct変更なしで`uv venv`へ切り替えて検証した。
- archive Candidate→PASS→Human approval→apply→`ready`、git-bound Review→Human approval→apply→`ready`、P1 FAIL→fixed-sibling Semantic revise→new Candidate→fresh PASSの3 installed fake chainsはすべてpassし、旧Candidate、sibling／downstream Issue、Portfolio、`.assurance.json`は不変だった。
- worker検証はdirect S06 96、init／update 3、E2E 3、S01〜S05 regression 342、Core／lifecycle／authoring 454 passed／1 skipped／1 baseline failure。親独立検証はexact S06 11 passed、ruff、mypy、byte parity、validate／sync／validate nodes=222、diff、41-path allowlist、forbidden mutation 0がpassした。
- full suiteは40分24秒時点で2344 passed／76 skipped／9 failedとなり、Issue 75 unsafe-input subprocess waitが10分無進展のため中断した。失敗は開始HEADにもあるapplication→infra structural test、init-00322を未収録のdogfood cutover snapshot、旧Skill契約であり、旧Skill契約6件はテストを変更せずprovider Skillを新public workflowへ整合してpassした。残るbaselineはS06で修正・弱体化していない。
- fresh defect-only code reviewはfindings 0、`review_status: pass`、confidence 0.96。既知baselineを除き、S06差分が導入したP0／P1はないと判定した。
- 実repositoryへのplanning apply、real ChatGPT／GitHub testは実行していない。
- S06 implementation／Reportをcommit `9206ab28d205b654603c8ecac2db7f89ee53bdeb`としてoriginへpushし、`git show --check`、post-commit clean、local／remote parityを確認した。
- S06 product implementation、required verification、fresh review、commit、pushは完了した。Report-only closure commitをpushしてS06をclosedとし、S07 ChatGPT具体化へ進める。
- No material implementation decisions beyond the approved plan.

### セッションログ（2026-07-28 — S07 JIT Dogfood and Delivery）

- S06 closure evidence commit `3bc0b8bada9b07ebc85f8cf29e15e361bd204f12`をoriginへpushし、local／remote parityとpost-commit clean worktreeを確認した。
- ChatGPT Pro session `iss00334-s07-implementa-brief`はGitHub connectorでrepository、branch、default branch、exact pushed HEADを確認し、branch comparisonをidentical／ahead 0／behind 0、Issue #334 open、existing PRなしとして照合した。model selection evidenceは`requested=Pro`、`resolved=Pro`、`verified=yes`である。
- ChatGPTは`iss-00334`をgit-bound限定で条件付きeligibleと判定した。archive Candidateは実装後のcanonical三文書を循環的に置換するためadoption targetにせず、create結果はexternal evidence-only、Review／decision／applyはgit-boundでcanonical三文書byte-identicalを要求する。
- dispositionは`STOP_AT_HUMAN_GATE`である。実装／PR権限からcanonical planning apply権限を推定せず、target Issue、exact worktree、branch／start HEAD、git-bound mode、live use、external evidence root、pre／post decision mutation scope、Delivery境界を一つの`S07LiveRunAuthorizationV1`としてHumanが明示するまでlive `planning create`／`review planning`／`planning revise`／`planning apply`を実行しない。
- 完全なtranscriptを`artifacts/20260728t100524z-s07-chatgpt-execution-work-packet.md`へ保存した。trailing whitespace 1箇所の機械的除去後SHA-256は`7419cb1a285762edf3d442f62d118d3ced7021da5fdc8c871188b13ef0433ca4`である。これはreview不要のstep execution inputであり、canonical authoring draftではない。
- packet／Reportをcommit・pushした後、そのmaterializationだけを含むfresh exact HEADでread-only fetch／parity／clean／help／Issue／PR preflightを実行する。packet source HEADはChatGPTがinspectionしたimmutable baselineとして保持し、Human authorizationはpreflight後のactual pushed HEADへbindする。
- packet／Report commits `f820980560f1acf2efcb9ab0fa4a25facd617846`、artifact whitespace／SHA correction `c9fe243680d35b148a5c5bc4cc8c3339f61be819`をoriginへpushした。read-only `git fetch`はshared worktree `FETCH_HEAD`のsandbox `EPERM`後、ordinary Git metadataへのmanaged escalationで成功した。
- pushed HEAD `c9fe243680d35b148a5c5bc4cc8c3339f61be819`で、exact worktree／branch、local／origin parity 0／0、main behind 0、upstream `origin`、clean tree／index、installed runtime file／executable、rootと4 leaf helpのexit 0を確認した。Issue #334はOPEN、既存PRは0件だった。helpによるplanning backend invocationは発生していない。
- preflight evidenceをこのReport-only commitへ固定した後、actual final pushed HEADを再取得してHuman authorizationの`expected_start_head`として提示する。live planning commandは引き続き未実行である。
- initial authorization後もcreate／fresh git-bound Reviewまでで一度停止し、exact Candidate／Review identityとSHA-256を提示してHuman supplied `PlanningHumanDecisionV1` bytesを待つ。decisionをCodex／ChatGPTが生成・補完・推定してはならない。
- merge、auto-merge、branch delete、Issue close、`issue finish`はHuman-onlyでありS07でも実行しない。
- No material implementation decisions beyond the approved plan.

### セッションログ（2026-07-29 — Oracle product boundary planning amendment）

- source repository／branch／HEADは`chemitaro/spec-dock`、`iss-00334-implement-chatgpt-issue-planning-workflow`、`a68eefa6881440d276c2bbfe415e01417a964128`で、local／upstream／GitHub remote parityとclean treeを確認してからChatGPTへ渡した。
- operator planning作業はユーザーの補足どおり`chatgpt-use`を利用した。製品runtimeは`chatgpt-use`へ依存せずPATH上のOracleをprovider-owned adapterからdirect argvで利用する、という境界をPromptで明示した。
- inputは現行Epic／Issue docs、Oracle境界調査、relevant source／tests、reference-onlyの`chatgpt-use` Skill／wrapperを一つのreference ZIPへ束ねた。instructionはChatフォーム本文へ送り、exact current branchを開けない場合のdefault branch fallbackを禁止した。
- 初回session `issue-planning-amendment`は2添付の同時uploadが5分以内に完了せず、`Attachments did not finish uploading before timeout.`で終了した。prompt重複送信は行わず、2資料を一つのZIPへ統合してfresh sessionへ切り替えた。
- fresh session `issue-planning-amendment-retry`／conversation `6a6953e8-aef0-83ee-8517-63d364bb710a`は43分06秒で完了し、model selectionは`requested=Pro`、`resolved=Pro`、`verified=yes`だった。回答はZIP link一件だけで、Oracle session file artifactとして保存された。
- output ZIP `artifacts/20260729t-iss-00334-oracle-boundary-planning-amendment-v1.zip`はSHA-256 `9fc16cc1bc2e5ee45576a64e863448c9c1247e0ec31cce0a8d5912881ef2d552`、内部root `iss-00334-oracle-boundary-planning-amendment-v1/`、exact five Markdown inventoryである。
- Issue Planは旧16,178 bytes／SHA-256 `de7690f04a67a24695bf9051a0353861accf30605f5b84b7fc1439abe1061aaf`と生成prefixがbyte-identicalで、変更はEOFの§16／S08〜S14追記だけである。
- Mainは個人絶対パス混入0、product／operator boundary、exact branch、Prompt/reference分離、ZIP-only Planner出力、実施済み履歴保持を確認してcanonical docsへ採用した。
- `spec-dock validate`は222 nodesでpass、`git diff --check`、assurance classify／verify、PlantUML 1.2026.6 `-checkonly`はpassした。
- fresh defect-only `spec-reviewer`はfindings 0、`review_status: pass`、confidence 0.99。改善提案やarchitecture再設計はreview scope外とした。

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
| S05 | committed | S05 exact 5-path runtime／testsとReport execution evidence | final fresh code-reviewer pass、findings 0、confidence 0.97 | commit `5f2edb93ab3e9e607abecf169f8167b0bd545f38`、origin push成功、post-commit clean、local／remote parity | S05 closed。S06 ChatGPT work packetへ進む |
| S06 packet | committed and published | S06 ChatGPT work packetとReport execution-input evidence | packet review waived。GitHub connectorでexact source HEAD照合済み | commits `a1c9fe124626416e5659c8796d4722e8a320945d`／`82902e2b7dd515c85931127dcb0b6e99c39e22a4`、origin push成功、artifact SHA-256 `5899b5120b1c975d38262f8c86e929af8998133aa49747d6c7f04af029fd1bf0` | bounded dev-coderへ委任済み |
| S06 implementation | committed | S06 provider／tests／mechanical dogfood 41 pathsとReport execution evidence | fresh code-reviewer pass、findings 0、confidence 0.96 | commit `9206ab28d205b654603c8ecac2db7f89ee53bdeb`、origin push成功、`git show --check`、post-commit clean、local／remote parity | S06 closed。S07 ChatGPT work packetへ進む |
| S07 packet | committed and published | S07 ChatGPT execution packetとReport Human-gate evidence | packet review waived。GitHub connectorでexact source HEAD照合済み | commits `f820980560f1acf2efcb9ab0fa4a25facd617846`／`c9fe243680d35b148a5c5bc4cc8c3339f61be819`、origin push成功、artifact SHA-256 `7419cb1a285762edf3d442f62d118d3ced7021da5fdc8c871188b13ef0433ca4` | read-only preflight pass。Report-only preflight evidence commit後のactual pushed HEADでHuman authorization recordを取得 |
| S08 packet | committed and published | S08 ChatGPT work packetとReport execution-input evidence | packet review不要。ChatGPT ProがGitHub connectorでexact source HEAD照合済み | commit `ff5264689c192781d82ed05b4f02909042f3f47a`、origin push成功、artifact SHA-256 `4808c3dcc40d34fe187e0a6a6b90b821d81278ea25378932f83c7d00e5a7fb6e` | bounded dev-coderへ委任済み |
| S08 implementation | committed and closed | S08 allowlisted direct Oracle runtime／domain／tests、temporary compatibility decision、3 formal Review artifacts、Report evidence | final fresh ChatGPT Pro closure reviewでP1-001〜005 closed、新規P0／P1 0、PASS、confidence high | initial `cdfb47171d921ff9f5e28c675de75b2ae52921da`、first repair `2f2b35f10d5480a328581fcf31c857d84f3a4937`、second repair `a297cda42fb356e91dd5c537010a83d66e199932`をoriginへpush。local／remote parity 0／0 | S08 closed。S09 ChatGPT JIT concretizationへ進む |
| S09 packet | committed and published | S09 ChatGPT work packet | packet review不要。ChatGPT ProがGitHub connectorでexact source HEADのidentical／ahead 0／behind 0を確認 | commit `9c8e7e58e0f422ce1b53f324cced0b07dbbd69db`、origin push成功、artifact SHA-256 `21f02add7bc395053f52f94d7a4d33048cac0ff0207ee5617ba6cd5f33f8ffd5`、local／remote parity 0／0 | bounded dev-coderへS09だけを委任する |
| Oracle boundary planning amendment | authoring and review complete; commit pending | Epic Requirement／Design、Issue Requirement／Design／append-only Plan、Assurance、Report、source ZIP、fresh review JSON | fresh defect-only `spec-reviewer` pass、findings 0、confidence 0.99 | ZIP／prefix／PlantUML／SpecDock／assurance validation pass | focused commit／push後にS08 implementationへ進む |

### セッションログ（2026-07-29 — S08 Provider-owned Direct Oracle Adapter JIT）

- planning／Report gateの機械可読値を正規化し、`guidance issue-execution`が`state=ready`、`may_execute_approved_plan=true`、`reason_code=assurance-valid`となることを確認した。正規化commit `08aa8f564f7265a64ce772d50d56ff1fb8ffd185`はoriginへpush済みである。
- ChatGPT Pro session `iss00334-s08-jit`はGitHub connectorでrepository、current branch、exact HEAD `08aa8f564f7265a64ce772d50d56ff1fb8ffd185`の一致、ahead 0／behind 0、default branch fallback 0を確認した。model evidenceは`requested=Pro`、`resolved=Pro`、`verified=yes`。
- ChatGPTは現行adapterのpersonal wrapper絶対パス、generic backend command、`--write-output`、legacy text frame、generic transient bytes、session recovery／artifact metadata境界の欠落をsource上で確認した。S08で変更するprovider infra／domainとfocused testsだけをallowlistにし、Prompt、Candidate、installer、projection、docsをS09〜S11へ残した。
- concrete execution inputを`artifacts/20260729t054034z-s08-chatgpt-implementation-work-packet.md`へ保存した。SHA-256は`4808c3dcc40d34fe187e0a6a6b90b821d81278ea25378932f83c7d00e5a7fb6e`。artifact自体のレビューはHuman指示により不要である。
- 実装前baselineとして`uv run pytest tests/unit/infra/test_issue_planning_chatgpt.py -q`を実行し、旧transport契約の29 testsがpassすることを確認した。次はartifact／Reportをcommit・pushし、bounded `dev-coder`へS08だけを委任する。
- S08 packet／Report commit `ff5264689c192781d82ed05b4f02909042f3f47a`をoriginへpushし、local／remote parityとclean worktreeを確認してからbounded `dev-coder`へ委任した。
- workerはPATH上のOracle 0.16.1 capability／session metadataを実測し、personal wrapper／`--write-output`／shell／API fallbackなしで、direct argv、sanitized child environment、single submit、same-session harvest、typed Planner ZIP／Reviewer JSON、private bounded artifact snapshotを6-path allowlist内に実装した。
- initial S08 implementationはtyped resultへの切替でS10 ownerのapplication／fake 30件を失敗させた。fresh ChatGPT Pro session `iss00334-s08-compatibil-decision-r1`へexact current branchとowner splitを渡し、production typed-onlyを維持したS10までのtemporary compatibility contractを`GO`として取得した。
- compatibility decisionを`artifacts/20260729t062209z-s08-chatgpt-compatibility-decision.md`へ保存した。SHA-256は`ef0628876101c15c0295b861546b8b65eb9ce38c74053e3632ec66f570e10669`。domain resultはtyped＋legacy、複数typed、payloadなし、non-pass payload、size／hash mismatchを拒否し、bytesをserialization／repr／equalityから除外する。production adapterはlegacy-only successを生成しない。
- S08 focused 109、application 66、CLI smoke 2、ruff、mypy、`validate` nodes=223、runtime denylist、`git diff --check`がpassした。typed Planner ZIPを未変更applicationへ渡すと`rejected/planner_response_rejected`、Candidate publication 0となることも確認した。
- mainの高速test laneを利用した通常`uv run pytest`はcollection時に、旧integration testが廃止済み`classify_transport_frame`をimportして停止した。このtest migrationはPlan S11 ownerであり、S08で旧frame APIを復活させたりallowlist外testを書き換えたりしない。
- S08実装をcommit `cdfb47171d921ff9f5e28c675de75b2ae52921da`としてoriginへpushし、local／remote parity 0／0とclean worktreeを確認した。
- 添付付きfresh Reviewは2回とも`prompt-commit-timeout`となったが、conversation IDなし、turns 0、`userMatched=false`を確認し、正式Reviewとして採用しなかった。これは`chatgpt-use`の添付付き送信で再現したoperator-side issueとして保持する。
- 添付なしGitHub connector modeのfresh session `iss00334-s08-fresh-code-review-3`はexact branch／HEAD、review delta、repository内work packet／compatibility artifactを確認した。model evidenceは`requested=Pro`、`resolved=Pro`、`verified=yes`である。
- 正式Reviewは5 P1でFAILした。recovery subprocess前のOracle identity再検証、invalid metadataとnonterminalの分離、descriptor-rooted artifact traversal、untrusted JSON／ZIP parser failureのcontent-free正規化、ZIP central-directory boundがS08の現行fail-closed／containment contractを直接破ると判定した。
- full transcriptを`artifacts/20260729t070100z-s08-chatgpt-fresh-code-review-fail.md`へ保存した。SHA-256は`f73da5960749f3055511dd144e323c022b40ca902ac2eef1db3468d0698ad813`。reviewerはrepository mutation、patch、replacement artifactを生成していない。
- 5 P1だけをsame bounded dev-coderへ戻した。adapter 8件／artifact helper 4件のexact Redを確認し、recovery直前のPATH／path／identity再検証、missing／nonterminal／invalid state分離、rootからのdescriptor-relative `openat`／`O_NOFOLLOW` traversal、strict JSON／expected ZIP exceptionのcontent-free正規化、ZIP central-directoryのentry／size／ratio boundを実装した。
- FIFO negative fixtureはleafをblocking `O_RDONLY`で開いてsuite teardownを停止させたため、`O_NONBLOCK|O_NOFOLLOW`でopen後に`fstat` regular-file判定するよう修正した。descriptor closeもexception pathを含め明示した。
- worker最終検証はfocused 125、application 66、CLI smoke 2、ruff、mypy、format、validate nodes=223、runtime denylist、diff checkがpassした。親独立combined laneも193 passed、ruff、mypy、validate、denylist、diff checkがpassした。
- repair差分はinitial allowlistのうちruntime infra 2ファイルと対応tests 2ファイルだけで、public contract、Prompt、application、Candidate、projection、S09以降、旧frame APIには触れていない。
- repair／Report／formal FAIL artifactをcommit `2f2b35f10d5480a328581fcf31c857d84f3a4937`としてoriginへpushし、local／remote parity 0／0を確認した。
- 別fresh ChatGPT Pro closure session `iss00334-s08-fresh-closure-review`はexact branch／HEADとrepair deltaを確認した。model evidenceは`requested=Pro`、`resolved=Pro`、`verified=yes`である。
- closure ReviewはP1-001 recovery identity、P1-003 descriptor containment、P1-005 ZIP boundをclosedとし、新規P0／P1 0を確認した。一方、bounded `meta.json`のdeep nestingが`RecursionError`を漏らすP1-002と、制御文字を含むZIP rootがtyped snapshot constructorの`ValueError`を漏らすP1-004をopenとした。
- full transcriptを`artifacts/20260729t074000z-s08-chatgpt-fresh-closure-review-fail.md`へ保存した。SHA-256は`36b4556c074b6c8c95fb65d61aad8e25310de20a5d109e43542051156bc544c5`。reviewerはrepository mutation、patch、replacement artifactを生成していない。
- open 2件だけをsame bounded dev-coderへ戻した。deep nested `meta.json`の`RecursionError`、制御文字を含むPlanner ZIP rootのtyped constructor `ValueError`をexact Redで再現した。
- metadata recursionをcontent-free artifact rejectionへ正規化し、ZIP全path segmentのcontrol characterをconstructor前に拒否し、typed snapshotのexpected `ValueError`もartifact boundaryで正規化した。いずれもpublic resultは`rejected/oracle_artifact_rejected`、harvest／duplicate submit／payload／private diagnosticsは0である。
- worker最終検証はfocused 127、application 66、CLI smoke 2、ruff、format、mypy、validate nodes=223、runtime denylist、diff checkがpassした。親独立combined laneも195 passed、ruff、mypy、validate、diff checkがpassした。
- second repair差分はartifact helperとpublic adapter focused testの2パスだけで、closed P1-001／003／005、S09／S10 handoff、known S11 collection failureを変更していない。
- second repair／Report／first closure FAIL artifactをcommit `a297cda42fb356e91dd5c537010a83d66e199932`としてoriginへpushし、local／remote parity 0／0を確認した。
- operator-side `chatgpt-use`／Oracleでは、Prompt本文がcomposer DOMに存在しても送信状態が同期されない`prompt-commit-timeout`を再現した。Oracleのtrusted click後retry条件とcomposer state再同期をfocused 11 tests、build、live smoke token `ORACLE_COMPOSER_STATE_RECOVERY_OK_20260729`で検証した。一方、instruction attachment付きrunは同症状を再現したため正式Reviewとして採用せず、長いreview instructionをPrompt本文へ直接渡す運用契約に沿って添付なしfresh sessionへ切り替えた。
- fresh ChatGPT Pro session `iss00334-s08-final-fresh-closure-2`はGitHub connectorでrepository、branch、exact HEAD `a297cda42fb356e91dd5c537010a83d66e199932`、ahead 0／behind 0、default branch fallback 0を確認した。model evidenceは`requested=Pro`、`resolved=Pro`、`verified=yes`である。
- final closure ReviewはP1-001〜005をすべてclosed、新規P0／P1 0、`review_status=pass`、confidence highと判定した。repository-recorded testsはread-only connector Review内では再実行せず、local verified evidenceとして区別した。
- full transcriptを`artifacts/20260729t081648z-s08-chatgpt-final-closure-review-pass.md`へ保存した。SHA-256は`802b83cd90d333424e551421a3222e28137df354cf01fee48e6e5de3a6a2a95e`。S08をcloseし、次はS09のChatGPT JIT concretizationを行う。
- No material implementation decisions beyond the approved plan.

### セッションログ（2026-07-29 — S09 Prompt Body, Exact Branch, and Role Output Contract JIT）

- S08 closure evidence commit `93487fd2b0ae0badcda2546bfb0962c794ca5db9`とInitiative onboarding artifact commit `1bc4109c094137bd2b42f9f09273ac0451aaf59d`をoriginへpushし、local／remote parity 0／0を確認した。
- 指定`chatgpt-use` wrapperの初回S09 JITはPrompt本文がcomposer DOMに一致したまま`prompt-commit-timeout`となり、conversation IDなし／turn 0／generation 0を確認して正式入力として採用しなかった。Oracle prompt composerのstrict no-turn／exact-prompt guard後にtrusted space＋backspaceでstateを同期し、focused 13 tests、`pnpm build`、live token `ORACLE_TRUSTED_NOOP_RECOVERY_OK_20260729`を同じ指定wrapperで確認した。
- recovered ChatGPT Pro session `iss00334-s09-jit-recovered-1bc4109c`はGitHub connectorでrepository、current branch、exact HEAD `1bc4109c094137bd2b42f9f09273ac0451aaf59d`のidentical／ahead 0／behind 0、default branch fallback 0を確認した。model evidenceは`requested=Pro`、`resolved=Pro`、`verified=yes`である。
- ChatGPTはcurrent S08 adapter／typed output／artifact reader、Prompt composer、managed resources、application drift gates、focused testsをsource上で照合し、S09だけを9 production/resource paths＋5 tests、21 Red cases、12 stop conditionsへ限定して`GO`とした。S10 Candidate／ZIP parsing、S11 projection、S12+、public command、canonical amendmentは明示的に除外した。
- concrete execution inputを`artifacts/20260729t084028z-s09-chatgpt-implementation-work-packet.md`へ保存した。source transcriptのtrailing spaceをMarkdown hygieneとして除去したrepository artifact SHA-256は`21f02add7bc395053f52f94d7a4d33048cac0ff0207ee5617ba6cd5f33f8ffd5`。artifact自体のreviewはHuman指示により不要である。
- work packetをcommit `9c8e7e58e0f422ce1b53f324cced0b07dbbd69db`としてoriginへpushし、local／remote parity 0／0とclean worktreeを確認した。
- Report input commit `70b52fc790063ea0ee9c5b241d60b7f7713f743c`をoriginへpushし、work packetのbounded instructionを`dev-coder`へ渡した。
- workerは最初のRedとして未実装`PlanningOutputExpectation`の`ImportError`を確認し、13-path allowlist内だけでPlanner／Semantic Revision／Reviewerの閉じたoutput expectation、Prompt本文の`@GitHub` exact branch／HEAD gate、default branch fallback禁止、reference-only transport pack、exact `repository access failed` sentinel、Planner post-run source recheckを実装した。
- Planner／Semantic Revisionはexact logical filename／internal root／4-entry inventoryをPrompt expectationとして受け、Reviewerはread-only defect-only closed JSONを受ける。S09はZIP entry extraction／exact inventory validationを行わず、PlanどおりS10へ保持した。
- onboarding companionは三文書へ従属し、canonical precedence、direct Oracleとoperator-local `chatgpt-use`の境界、Human gate、4種類のPlantUML roleをPrompt本文で必須化した。
- 親独立検証はS09 focused 224件とS08／CLI regression 42件の計266件がpassした。worker検証ではruff、mypy、`validate` nodes=223、legacy active-contract scan、`git diff --check`もpassした。
- full unit laneは`1045 passed, 552 skipped, 2 failed`である。1件はprovider prompt resourceとS09 allowlist外のdogfooding `.agents/...` parity差、もう1件は既知のS11-owned `classify_transport_frame` integration importであり、S09ではprojectionや旧frame APIを先取り修正しない。
- `ruff format --check`は変更対象を含む既存ファイル全体のbaseline整形差分を検出した。無関係な大量整形は行わず、ruff checkと`git diff --check`をpassさせた。
- 実装と本Reportをcommit `dfb1a8e70b17ed94ddb3b4cd95e9da03a6562a43`としてoriginへpushし、local／remote parity 0／0を確認した。
- 指定`chatgpt-use` wrapperだけを用いたfresh session `iss00334-s09-fresh-defect-review`は、GitHub connectorでexact branch／HEADとbase-to-head rangeを確認した。model evidenceは`requested=Pro`、`resolved=Pro`、`verified=yes`である。
- 正式ReviewはS09-P1-001の1件でFAILした。近似sentinel、追加文、malformed／multiple transcriptと有効authoring ZIPが併存すると、exact sentinel判定をfalseとした後にZIPをsuccess受理できるS09-R10違反である。S10／S11／projection／public CLIや改善提案はfindingsから除外された。
- full transcriptを`artifacts/20260729t094943z-s09-chatgpt-fresh-code-review-fail.md`へ保存した。SHA-256は`00a75059cbf1cfa0ec6c5c003cb9195e3dcfac61f2d9faa979813bba45b64907`。reviewerはrepository mutation、patch、replacement artifactを生成していない。
- S09-P1-001だけをsame bounded dev-coderへ戻した。Planner／Semantic Revisionの近似sentinel＋有効ZIPが修正前に`pass/transport_received`となる2件のexact Redを確認した。
- file artifact併存時の近似／追加文、壊れた／重複Answer marker、複数transcriptを`rejected/oracle_artifact_rejected`へ正規化した。exact sentinel単独は`blocked/github_exact_branch_unavailable`、exact＋ZIPはrejected、通常success transcript＋ZIPはpass、Reviewer JSONとS08 privacy／same-session recoveryは維持した。
- 親独立検証はinfra focused 70件、S09／S08 broad regression 274件がpassした。worker検証ではruff、mypy、`validate` nodes=223、`git diff --check`もpassした。
- repairとformal FAIL artifact／本Reportをcommit `bcc11ecc3ac6653c302bcc184fae8e61a52d5e87`としてoriginへpushし、local／remote parity 0／0を確認した。
- 別fresh ChatGPT Pro session `iss00334-s09-fresh-closure-bcc11ecc`はGitHub connectorでexact repair HEADとone-commit rangeを確認した。model evidenceは`requested=Pro`、`resolved=Pro`、`verified=yes`である。
- closure ReviewはS09-P1-001をclosed、新規P0／P1 0、`verdict=PASS`、confidence highと判定した。exact sentinel単独、exact＋ZIP、近似／malformed／multiple transcript＋ZIP、正常success＋ZIP、Reviewer JSON／privacy／single-submit／same-session recoveryへの直接回帰は確認されなかった。
- full transcriptを`artifacts/20260729t100603z-s09-chatgpt-fresh-closure-review-pass.md`へ保存した。SHA-256は`47aa35441ece0710d1743127780d6b51c565a0fb3842582504a3ec05be07c080`。S09をcloseし、次はS10のChatGPT JIT concretizationを行う。

### セッションログ（2026-07-29 — S10 Authoring ZIP, Candidate Binding, and Managed Apply JIT）

- S09 closure evidence commit `aad5e2108b03d01c9efb506675ac58dce4845eb5`をoriginへpushし、local／remote parity 0／0とclean worktreeを確認した。
- `origin/main`をfetchして`HEAD...origin/main=76/0`を確認した。current branchはlatest remote mainを包含していたため、不要なmerge commitは作成しなかった。
- 指定`chatgpt-use` wrapperのfresh session `iss00334-s10-jit-aad5e210`はGitHub connectorでrepository、current branch、exact HEAD `aad5e2108b03d01c9efb506675ac58dce4845eb5`のidentical／ahead 0／behind 0、default branch fallback 0を確認した。model evidenceは`requested=Pro`、`resolved=Pro`、`verified=yes`である。
- ChatGPTはactive Requirement／Design／append-only Plan／Report、S09 closure、current Candidate／Review／Human／apply／recovery実装をsource上で照合し、S10だけを7 production paths＋9 test pathsへ限定して`GO`とした。
- work packetはtyped authoring ZIPのclosed four-payload extraction、guide-inclusive deterministic Candidate、`OnboardingCompanionBindingV1`／`GitBoundOperationBindingV1` closed schema、existing `--candidate`によるsame-Candidate Review／apply、canonical three-path tuple不変、Human承認後companion write／no-op／rollback／recoveryを固定した。
- S11 provider projection／dogfood sync／distribution／test migration、S12 full verification／live dogfood、S13／S14、Prompt／Oracle adapter、operator-local `chatgpt-use`／Oracle source、PlantUML product dependencyは明示的に除外した。
- concrete execution inputを`artifacts/20260729t104419z-s10-chatgpt-implementation-work-packet.md`へ保存した。添付を使用していない実行に対するunsupportedなsupplementary-attachment一文を除去し、repository artifact SHA-256は`4b65f14306414684b9040a3e6e033c9690561558cdeb51421814941cdd91637c`、source transcript SHA-256は`7fb10a296328bddd89b62413cae32275b7c9c0b053485308f45b3b455f0007c4`である。artifact自体のreviewはHuman指示により不要である。
- work packetをcommit `201c1f2790bfb665798dbf8ccb165c2c31911278`としてpushし、bounded dev-coderがS10実装をcommit `211c73e9fca6292d120686504a3d33f3f10ba387`としてpushした。typed 4-file authoring ZIP、guide-inclusive 8-entry Candidate、`OnboardingCompanionBindingV1`、closed `GitBoundOperationBindingV1`、same-Candidate git-bound Review／apply、companion write／no-op／rollback／recovery／retryを実装し、legacy active marker／transient payloadを除去した。
- work packetのtest allowlistからS10 application ownerの`tests/unit/application/test_issue_planning_apply.py`が漏れていた。指定wrapperによるfresh ChatGPT decisionを`artifacts/20260729t120603z-s10-chatgpt-allowlist-amendment-go.md`へ保存し、既存test 1 pathだけをeffective allowlistへ追加した。decision commitは`4ecdeaf5c108a1d8cf6dd08e222bddce366b7755`である。
- application fixtureをtyped bindingへ移行したcommit `7636c139565da1249ec45264e3f0b3d607ee1fce`後、wrong canonical paths caseの期待reason 1行だけが失敗した。fresh ChatGPT decisionはstrict `PlanningReviewResult` parsingがidentity照合より先に拒否する現行契約を確認し、paths caseだけ`review_result_rejected`へ同期する`GO`を返した。decision artifactは`artifacts/20260729t125606z-s10-chatgpt-reason-owner-decision-go.md`、decision commitは`bff38edb5158431e23d69d03f620b12875536295`、one-line repair commitは`28155c618f04bb0dc5830b1d206eb10303baf770`である。
- effective 10-test-path S10 suiteは384 passed、full unitは1084 passed／552 skipped／2 failedだった。2件はS11 ownerのprovider／dogfood Prompt parityとobsolete `classify_transport_frame` collectionである。`ruff check`、`spec-dock validate` nodes=223、`git diff --check`はpassした。`ruff format --check`は対象test fileの既存format差分だけでfailし、新しい1行は報告対象外だったためscope外整形を行っていない。
- 指定`chatgpt-use` wrapperの復旧では、safe recovery用`--browser-model-strategy current`をwrapperが拒否する問題を修正し、`ignore`等は引き続き拒否した。続いてOracle composerが複数行Promptの先頭1行だけを入力する問題を、Oracle checkoutの`promptComposer.ts`とfocused testで修正し、17 tests、`pnpm build`、live token `ISS00334_MULTILINE_COMPOSER_RECOVERY_OK_20260729`を指定wrapper経由で確認した。Oracle checkoutのこの2ファイルは未commitのまま保持している。
- 長いdecision送信時にChatGPTのrate-limit modalが表示され、Oracleは`prompt-commit-timeout`として誤分類した。失敗sessionはいずれもuser／assistant turn 0で、重複送信は採用されていない。約11分のcooldown後、session `iss00334-s10-reason-decision-cooldown11`がexact branch／HEADを確認して正常完了した。rate-limit modal分類、失敗tab蓄積、skill記載の`session --path` parsingはwrapper／Oracleのfollow-up課題として残る。
- 別fresh ChatGPT Pro session `iss00334-s10-fresh-defect-review`は24分19秒で完了し、GitHub connectorでexact HEAD `0c1fa6ae2c28373281390491b24c0cf8be02a42d`を確認した。model evidenceは`requested=Pro`、`resolved=Pro`、`verified=yes`である。
- 正式ReviewはP0=0、P1=2、`verdict=FAIL`、confidence highだった。S10-P1-001はguide completeness validatorが各必須概念を独立に要求せずmandatory section／non-empty bodyも検証しない欠陥、S10-P1-002はsource preflight後からtransaction開始直前までexplicit Candidate差替えを再検証しない欠陥である。設計変更、改善提案、P2／P3、S11以降はfindingsから除外された。
- formal JSONを`artifacts/20260729t132842z-s10-chatgpt-fresh-code-review-fail.json`へ保存した。SHA-256は`7d4f5a93af51e88db7386bea3a109555aae2b4a67d8f4356799ea8e7988122af`。次はこの2 P1だけをsame bounded dev-coderへ戻す。
- same bounded dev-coderが6 allowlisted pathsだけを修正し、commit `13ceae2e0e027d92b25c3eaff9d62fd334db1d92`としてpushした。親独立検証はeffective S10 suite 386 passed、Ruff、mypy、validate nodes=223、diff checkがpassした。
- 別fresh ChatGPT Pro session `iss00334-s10-fresh-closure-review`はexact repair HEADを確認し、S10-P1-002をclosed、新規P0／P1 0とした。S10-P1-001は各concept groupが同一のnon-empty sectionを再利用でき、全tokenと4 PlantUML blockを1つの`## Everything`へ集約すると通過するためopenだった。
- first closure JSONを`artifacts/20260729t135925z-s10-chatgpt-fresh-closure-review-fail.json`へ保存した。SHA-256は`6347a694e27be4b44e7f7cb09a1586ebd681289001ebf2099841c97c0961b4bc`。次はdistinct-section enforcementと単一section bypass regressionだけをsame workerへ戻す。
- same bounded dev-coderはdomain validatorとdomain testの2 pathsだけを修正した。13 mandatory concept groupsとnon-empty Markdown sectionsの一対一割当をaugmenting-path matchingで検証し、単一`## Everything`へ全tokenを集約するexact RedをGreen化した。final repair commit `3a7df10575d3a8247e9e175fc24c02a3583a0e4a`をpushし、親独立検証はeffective S10 suite 387 passed、Ruff、mypy、validate nodes=223、diff checkがpassした。
- 別fresh ChatGPT Pro session `iss00334-s10-final-fresh-closure`はexact final repair HEADを確認し、S10-P1-001／002をclosed、新規P0／P1 0、`verdict=PASS`、confidence highと判定した。
- final closure JSONを`artifacts/20260729t141413z-s10-chatgpt-final-fresh-closure-review-pass.json`へ保存した。SHA-256は`02ee81d35cb29042e44a824f620c4fe64f944edac569e515548eea69b699a5ce`。S10をcloseし、次はS11のChatGPT JIT concretizationを行う。

### セッションログ（2026-07-29 — S11 Provider Authority, Projection, Distribution, and Test Migration JIT）

- S10 closure evidence commit `7e4257955af699cbad456a53cd3be06cb2871527`をoriginへpushし、local／remote parity 0／0とclean worktreeを確認した。
- 指定`chatgpt-use` wrapperのinitial session `iss00334-s11-jit-work-packet`はPromptがconversationへ現れないpre-submit failureで終了した。正式入力として採用せず、Oracle直接操作や別ブラウザ操作を行わず、2分cooldown後に短縮した同一scopeのPromptを新規sessionへ送信した。
- fresh session `iss00334-s11-jit-retry`はGitHub connectorでrepository、current branch、exact HEADのidentical／ahead 0／behind 0、default branch fallback 0を確認した。model evidenceは`requested=Pro`、`resolved=Pro`、`verified=yes`、完了時間は25分45秒である。
- ChatGPTはprovider Prompt/runtimeをcurrent functional authorityとしてread-onlyに保ち、authority docs 4 paths、tests 4 paths、Red-backed installer fallback、official updateによるmechanical dogfood projectionへS11を限定した。known planner Prompt parity failureとobsolete `classify_transport_frame` integration importをS11 ownerとして閉じる。
- work packetはfake PATH Oracle E2E、installed Skill→repo-local CLI→Oracle subprocess、typed authoring ZIP／Review JSON、same-Candidate git-bound chain、wheel／sdist／fresh init／update parity、active product denylist、second update no-opを固定した。
- GPT-5.6 Prompt／template tuning、S12 full／live closure、S13／S14、canonical amendment、provider runtime／schema redesign、personal `chatgpt-use`／Oracle source変更は明示的に除外した。
- exact ChatGPT outputを`artifacts/20260729t144732z-s11-chatgpt-implementation-work-packet.md`へ保存した。SHA-256は`4b6604934fdb5ff6ab6c38d25253f101b1e08cb811fcad4e20f8a6db9697b2c8`。artifact自体のreviewはHuman指示により不要である。
- work packetと本Reportをcommit `ee7e7c7391258ecfb2b0730955bbcf95659caf34`としてoriginへpushし、bounded dev-coderへS11だけを委任した。
- initial Redはobsolete `classify_transport_frame` importによるcollection failure、provider／dogfood parity failure、旧wrapper形式fake E2E 3 failuresだった。migration中のtyped test mypy errorsもRedとして検出し、production contractを変更せずtest helper typingを修正した。
- authority変更はtop-level `README.md`、provider official Skill、provider docs 2 pathsの4件である。PATH `oracle`だけ、wrapper／API fallbackなし、exact branch／HEADとdefault fallback禁止、typed ZIP＋companion、closed Review JSON、same-Candidate git-bound Review／apply、Human approval前managed write 0を記載した。provider Prompt resources、runtime、schemaのsemantic変更と`src/spec_dock/cli.py`変更は0である。
- testsはCLI、legacy transport migration、fake PATH Oracle E2E、init／update distributionの4 pathsである。official `uv run python -m spec_dock.cli update .`がSkill／4 resources／docs／runtimeを17-path mechanical projectionとして同期し、projection先の手編集は行っていない。
- S11 focusedは121 passed（Prompt／adapter 89、distribution 8、CLI 13、transport 7、fake Oracle E2E 4）、S09／S10 regressionは418 collected／exit 0、authoring／Core／lifecycleは174 collected／exit 0だった。Ruff check、changed tests mypy、validate nodes=223、denylist、25-path allowlist、diff checkがpassした。
- wheel SHA-256は`c1121cedd10ea49ff4e06ce2d02714f64d412ea881ea1c561a2a1c5ab3fb3e27`、sdist SHA-256は`04f0ff0e8ea5ce822e8c044a44d9dde8f843d38a23b6cd6dc1c08901f867f495`である。wheel／sdist inventory、isolated fresh init／update、execution bit、user／unmanaged preservation、provider／dogfood byte parity、second update前後diff hash `c1d3ddda3fda7fa808f21df71bc090f7c0f7e7ca4681631a2f16c8a71e8d780f`同一を確認した。
- fake Oracle E2Eはfresh init→installed Skill→repo-local CLI→PATH fake Oracle、exactly-one submit、typed Planner ZIP＋companion、closed Review JSON、same-Candidate git-bound Review／apply、Human前mutation 0、repository-access failure時Candidate／Review／mutation 0を確認した。personal wrapper、`--write-output`、Project／profile／host、API credential inheritanceは0である。
- Main独立確認はsystem temp volumeの`ENOSPC`で初回E2E／distributionが停止した。外部volumeへpytest `--basetemp`と子process `TMPDIR`を固定して再実行し、non-distribution focusedとdistribution 8件がexit 0、provider／dogfood runtime／Skill／resources／docs byte parityがpassした。これはcode failureではなく実行環境容量不足として帰属する。
- repository-wide source mypyは開始HEAD由来の`backend_invoke.py` 1件、format checkは開始HEADからのCLI／transport／init-update差分を報告した。変更testsのmypyとRuff checkはpassし、scope外一括整形は行っていない。
- 25-path S11 implementation＋本Reportをcommit `71628137a7665e59a11b14eca367e49d49bea39c`としてoriginへpushし、local／remote parity 0／0とclean worktreeを確認した。
- dedicated managed Chromeのlogout／Cloudflare challengeをHumanが手動復旧した後、別fresh ChatGPT Pro session `iss00334-s11-review-manual-login`がexact implementation HEADを確認した。model evidenceは`requested=Pro`、`resolved=Pro`、`verified=yes`、完了時間は19分53秒である。
- 正式ReviewはP0=0、P1=1、`verdict=FAIL`、confidence highだった。S11-P1-001はfake Oracle E2E guideが`S01-S07 complete／S08-S14 remain`というstale roadmapのまま、fake Reviewer PASSとarchive／git-bound `ready`へ進むため、S11-R08とReviewer contractを実証していないfalse positiveである。S12+、Prompt tuning、既存mypy／format／ENOSPCはfindingsから除外された。
- formal JSONを`artifacts/20260729t161123z-s11-chatgpt-fresh-code-review-fail.json`へ保存した。SHA-256は`da45157271aa0aa97ad3d7b1a63e1eda41162a1454ef9db7279ee33cf4b33921`。次はS11-P1-001だけをsame bounded dev-coderへ戻す。
- same bounded dev-coderが`tests/integration/test_issue_planning_e2e.py`だけを修正し、roadmapを`S01-S10 closed／S11 review pending／S12-S14 remain`へ更新した。Candidate ZIP SHA／companion checksum、archive／git-bound PASS Review identity、ready operation companion SHA／applied bytesの直接assertionも追加した。
- Main独立確認はE2E `4 passed`、Ruff check／format check、mypy、`git diff --check`がpassした。focused repair commit `3277f3e50c094523443cfd772a91f6c7b44a48ca`をoriginへpushし、local／remote HEAD一致とclean worktreeを確認した。
- 別fresh ChatGPT Pro session `iss00334-s11-closure-review`はGitHub connectorでexact branch／HEADとparent rangeを確認し、S11-P1-001 `CLOSED`、新規P0／P1 0、`verdict=PASS`と判定した。model evidenceは`requested=Pro`、`resolved=Pro`、`verified=yes`、完了時間は5分03秒である。
- formal JSONを`artifacts/20260729t164022z-s11-chatgpt-fresh-closure-review-pass.json`へ保存した。SHA-256は`91e849167a3e136f67ffeb86a50d8eaa49e3d960366b2f263d23f5720f7e90f5`。S11をcloseし、S12のJIT concretizationへ進む。
- S11 closure evidence commit `ad36524d3d48545690cc7ef9f73a8bfe11ad11ff`をoriginへpushし、local／remote parity 0／0とclean worktreeを確認した。
- 指定`chatgpt-use` wrapperのfresh session `iss00334-s12-jit`はGitHub connectorでrepository、current branch、exact HEADのidentical／ahead 0／behind 0、default branch fallback 0を確認した。model evidenceは`requested=Pro`、`resolved=Pro`、`verified=yes`、完了時間は20分23秒である。
- ChatGPTはS12をhermetic／distribution／static／guide→refreshed Human gate→liveの順へ具体化し、`DISPOSITION: GO_HERMETIC_THEN_HUMAN_GATE`とした。旧`S07LiveRunAuthorizationV1`はolder exact HEADであり、現HEADのreal create／Review／decision／applyへ暗黙再利用しない。
- raw Browser transcriptを`artifacts/20260729t170420z-s12-chatgpt-implementation-work-packet.md`へbyte-preserving copyした。SHA-256は`721a3b125455e68e6a3feedf2261cb5e100855ec1a12a0d8a93cdb3342d103ac`。artifact自体のreviewはHuman指示により不要である。
- S12 packet／Report commit `6af86ac02a26970f5ca9050089cea2fab80ccff3`をoriginへpushし、local／remote parity 0／0とclean worktreeを確認して4系統のread-only worker verificationを開始した。
- focused A/Bは70＋289＝359 passed。staticはvalidate nodes=223、diff check、active dependency denylist、guide 4 PlantUML blocks、AC-001〜025 presenceをpassした。一方で`make lint`はRuff format対象corpusとmypy 15 errors／6 filesでfailし、PlantUML 1.2026.6 executableがlocalにないため`-checkonly`はunverifiedとなった。
- 同一S12 ChatGPT conversationへobserved static blockerだけをfollow-upし、exact remote HEAD `6af86ac02a26970f5ca9050089cea2fab80ccff3`に対する`DISPOSITION: GO_BOUNDED_STATIC_REPAIR`を得た。follow-upは同一conversationのためmodel selector再選択をskipしたが、parent sessionの`requested=Pro`／`resolved=Pro`／`verified=yes`を継続した。
- raw follow-up transcriptを`artifacts/20260729t172438z-s12-chatgpt-static-blocker-repair-packet.md`へbyte-preserving copyした。SHA-256は`dfbc52e0c807b153488caf5a68b7f50662705fdc0e3925d70dca6199671378f7`。artifact自体のreviewはHuman指示により不要である。
- static repair packetをcommit `b5814936a05dde83c586b273a915ae6a25512552`としてoriginへpushした後、bounded dev-coderがpacketの40-path effective allowlistだけを修正した。変更はRuff format、`backend_invoke.py`のmypy-safeな`cwd`引数、test typing、official updateによる11 provider／dogfood counterpart projectionに限定した。
- static repairの独立検証はRuff check／format、mypy 280 files、focused 361 passed、validate nodes=223、active dependency denylist、provider／dogfood 11／11 byte parity、diff check、40-path guardをpassした。PlantUML 1.2026.6 JAR SHA-256は`89948f14c93756c7a3fb7b69078ff37e8489fd79dd430c582b931e2f65358690`で、onboarding guideの4 diagramはすべて`-checkonly`をpassした。
- static repairをcommit `334c4876ff6996ee27e6575688853afe9a9a873c`としてoriginへpushし、local／remote parityを確認した。
- full regression／distribution観測から、3件の独立した残存blockerを特定した。Aはordinary prose中の`transcript`をraw transcriptとして期待するstale test、Bは承認済みinit-00322配下10 nodes／6 non-empty Issue dependenciesのchecked-in snapshot drift、Cはunsafe wait argumentsがPython wait engineで最終validationされずpollingへ進むhangである。
- 同一S12 ChatGPT conversationへこの3 blockerだけをfollow-upし、exact pushed source `b5814936a05dde83c586b273a915ae6a25512552`に対する`DISPOSITION: GO_BOUNDED_REGRESSION_REPAIR`を得た。write allowlistは`tests/cli_runtime/test_authoring.py`、`tests/unit/infra/test_init_update.py`、provider／dogfood `pr_observation_wait.py`のexact 4 pathsである。
- raw browser transcriptを`artifacts/20260729t180303z-s12-chatgpt-regression-blocker-repair-packet.md`へbyte-preserving copyした。repository artifactとsource transcriptのSHA-256はともに`bceed213930add009b8197cdcc5622416ae89c57b861f16164c09751e7e9873d`。packetは設計変更、canonical amendment、public CLI／schema／polling policy変更を許可せず、artifact自体のreviewはHuman指示により不要である。

## 最終品質ゲート（Final Quality Gate / 必須）

| ゲート | 対象 | 観測結果 | 証跡 / 次アクション |
|---|---|---|---|
| Docs Impact S90 | docs、templates、README、workflow、skill、migration notes | in progress | current onboarding companionのmilestone statusをfinal combined Review `SPEC-P1-001`に従って修正し、fresh exact-HEAD reviewで再確認する |
| Final QA | issue-wide obligation coverage | failed | final combined Review `QA-P1-001`。S12のhermetic／full／distribution evidenceは保持するが、refreshed Human authorizationにbindしたlive create→Review→exact Human decision→apply／remote parityが未完了 |
| Final Code Review | integrated code and tests | failed | final combined Review `CODE-P1-001`〜`003`。apply入口のarchive findings欠落、dangling symlink、application unit-test boundaryをbounded repairし、new exact HEADで再確認する |
| Final Spec Review | Requirement、Design、Plan、Report、implementation、tests、docs alignment | failed | `artifacts/20260730t020224z-chatgpt-output-s14-final-combined-review-fail.json` against exact published HEAD `bb65257155a73b621b0d0b6fb3426393c46de712`。P0 0／P1 5をbounded repair後にnew exact HEADで別fresh reviewする |
| Planning Amendment Spec Review | Oracle boundary amendmentのEpic／Issue五文書 | passed | `artifacts/20260729t020725z-review-oracle-boundary-planning-pass.json`。これは実装後のFinal Spec Reviewを代替しない |
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
- 現行product `spec-dock-chatgpt`は今回修正対象の個人wrapper依存を含むため、このamendment authoringではユーザー指定のoperator-local `chatgpt-use`を使用した。これは製品runtime contractの例外や依存として採用しない。

## 2026-07-29 — onboarding companion authoring contract amendment

### Human decision and authority

- Humanは、正確で詳細なcanonical `requirement.md`／`design.md`／`plan.md`を維持しつつ、本日加入する新メンバーが短時間で理解できるPlantUML付き説明資料を、今後のIssue Planningで毎回生成するFormal Candidate artifactへ追加するよう指示した。
- 説明資料は第四のcanonical specificationではなく、三文書に従属する`onboarding-companion`である。矛盾時は三文書を優先し、矛盾自体をdefect-only Reviewの対象とする。
- Epic `plan.md`は変更していない。Issue `plan.md`は各Candidateの直前版をbyte-identical prefixとして保持し、追加作業だけを末尾へ追記した。
- operator-side authoringにはHuman指定の`chatgpt-use`を使用した。製品runtimeはprovider-owned adapterからPATH-resolved Oracleをdirect argvで利用し、個人wrapper／Project／profile／absolute pathへ依存しない。

### GitHub-synced authoring evidence

- repository: `chemitaro/spec-dock`
- branch: `iss-00334-implement-chatgpt-issue-planning-workflow`
- source HEAD: `bf9bc26c00664795842731f665def63a16a7b78c`
- local／upstream／GitHub branch HEAD一致をauthoring前に確認した。全Promptはexact current branchを必須とし、default branch fallbackを禁止した。
- 最初の単独guide session `iss-00334-new-member-guide`はHumanの要件訂正により停止し、不採用とした。
- Blue Teamは前回Planning amendmentの継続conversationを使用した。v2／v3／v4 follow-upのselector evidenceは`resolved=(unavailable)`／`verified=no`。各fresh Reviewは`requested=Pro`、`resolved=Pro`、`verified=yes`。

### Immutable Candidate and fresh Review history

| version | Candidate ID | ZIP SHA-256 | fresh Review | disposition |
|---|---|---|---|---|
| v2 | `iss-00334-onboarding-companion-planning-amendment-v2` | `d202bf4b4d3da4d6411099fbb250c6400e34cf099cfd8b1378365b30ca37b0d8` | FAIL、P1 2件 | superseded |
| v3 | `iss-00334-onboarding-companion-planning-amendment-v3` | `95675c4a56b8c6fb43bdc8da6a1d761463615b5e84fd87002391e4823a90b279` | FAIL、P1 1件／P2 1件 | superseded |
| v4 | `iss-00334-onboarding-companion-planning-amendment-v4` | `b344117988ef6e7f71bfcabb6caf39e07adc6509d3379a57a80cbd783e64b103` | PASS、findings 0、confidence 0.98 | adopted |

- v2 Planはcurrent canonical Plan 38,126 bytes／SHA-256 `71646bb452e1e77dddf1b908f80c73ebde217e17e70df1da1c78095cb57c6d86`をprefixとして保持した。
- v3 Planはv2 Plan 47,800 bytes／SHA-256 `c320b82299a54ebaf8f1bf9f17bae3eb8efade3dce508fcddd8392192b575e05`をprefixとして保持した。
- v4 Planはv3 Plan 55,059 bytes／SHA-256 `7dcb0e3dbd630737df28d03f8ea9169f8f88243772f52cd75885b05609cd367f`をprefixとして保持した。
- 各ZIPのsingle root、exact 8-file inventory、CRC、MANIFEST、CHECKSUMS、source identityを検証した。v4の全PlantUMLはPlantUML 1.2026.6 `-checkonly`をPASSした。

### Evidence Adoption Ledger

| ID | adoption_status | source | target | rationale | reviewer | next_action |
|---|---|---|---|---|---|---|
| EAL-20260729-ONBOARDING-V2 | rejected | v2 Candidate／fresh Review | none | Reviewer Oracle boundaryとgit-bound companion bindingにP1 | FAIL | v3へ置換済み |
| EAL-20260729-ONBOARDING-V3 | rejected | v3 Candidate／fresh Review | none | binding canonical key集合とgate数表記に矛盾 | FAIL | v4へ置換済み |
| EAL-20260729-ONBOARDING-V4 | adopted | Human decision、v4 Candidate、local validation | Epic Requirement／Design、Issue Requirement／Design／Plan、Issue artifact | subordinate guide、same-Candidate binding、PlantUML obligationをexact sourceへbind | PASS、findings 0 | S08以降で実装 |

### Canonical and artifact placement

- whole-file replacement: Epic `requirement.md`／`design.md`、Issue `requirement.md`／`design.md`／`plan.md`。
- managed companion: `artifacts/20260729t044600z-guide-new-member-chatgpt-first-issue-planning.md`。
- immutable evidence: v2／v3／v4 ZIP、`20260729t034100z-review-onboarding-companion-v2-fail.json`、`20260729t044500z-review-onboarding-companion-v3-fail.json`、`20260729t052300z-review-onboarding-companion-v4-pass.json`。
- canonical placement fresh `spec-reviewer`: PASS、P0/P1 0、P2 2件はReportの現行assurance hashとphase promotion記録へ反映済み。`artifacts/20260729t053100z-review-onboarding-canonical-placement-pass.json`。
- Planning amendmentはPASS and adopted。製品実装はS08以降であり、`execution-ready`、Issue finish、PR merge、Epic completionを本amendmentでは主張しない。

## 2026-07-30 — S12 hermetic verification and GPT-5.6 Prompt tuning

- S12 Blocker A〜Mは、通常文中の`transcript` marker誤認、checked-in snapshot drift、PR observation wait validation、外部heredoc transportに限定して修正した。provider／dogfood agent-tooling 5対はbyte-identicalである。
- Blocker Nは`application/issue_planning.py`から具象infraを直接importする構造契約違反だった。application-owned `IssuePlanningDependencies`／gateway／structural views／normalized errors、bootstrap adapter、4 entrypointへのrequired dependency injectionへ修正し、全48 direct callを移行した。
- S12 focusedはA〜M＋wrapper 20 passed、Issue Planning 449 passed、Blocker N corrected 199 passed、構造境界 exact node 1 passed。`make lint`、installer/update 562 passed、wheel／sdist fresh install、provider／dogfood parity、validateがPASSした。
- 明示full regressionは`3117 passed, 76 skipped`、29分47秒でPASSした。開始／終了のbranch、HEAD、dirty exact24は一致した。
- repair commitは`8b3f90e1`と`f35fe4de`。その後`origin/main`をmerge commit `a50f9a1de7301f0c64f0f1d23092bd7ee888043e`で統合し、mainの新PR fast laneは`1092 passed, 2119 skipped`、`make lint`、wheel／sdist fresh install、provider／dogfood parityがPASSした。remote branchへpush済みである。
- ChatGPT follow-up child sessionに対する`--harvest --write-output`がparent turnを取得した一方、child sessionの`artifacts/transcript.md`には正しい回答が存在した。Blocker N corrected outputはchild transcriptから直接回収した。これは製品runtime差分ではなくoperator-side wrapperのfollow-up harvest問題として記録する。
- Blocker B〜Nとcorrected Nの各ChatGPT具体化結果は、`artifacts/20260730t011600z-chatgpt-output-s12-blocker-b.md`〜`artifacts/20260730t011613z-chatgpt-output-s12-blocker-n-corrected.md`へimmutable evidenceとして保存した。
- GPT-5.6 Prompt tuningは、公式guideのlean prompt、instruction once、representative evaluation原則に従い、exact pushed HEADを指定`chatgpt-use`で具体化した。ChatGPTはexact branch／HEAD identical、default branch unused、`GO`を確認した。
- role resourceをtask固有責務へ限定し、formal output、Human authority、mutation、sensitive-output境界をtransportへ一元化した。synthesizer、CLI、schema、adapter、canonical三文書は変更していない。
- Prompt tuning Redは3 failures、Greenはfocused 23 passed、relevant 66 passed／4 skipped、ordinary 1096 passed／2119 skipped、Ruff、build、validate nodes=227、exact9 guard、provider／dogfood 4対parityがPASSした。
- 合成PromptはPlanner 3,784→3,246、Reviewer 3,978→3,603、Revision 3,169→3,146、合計936文字（8.6%）削減した。
- blind A/BはcandidateをPlanner 99、Reviewer 99、Revision 100として3/3選択し、candidate critical failureは0だった。baseline Revisionの`as Planner`外部参照によるcritical failureを解消した。
- ChatGPT exact outputは`artifacts/20260730t011515z-chatgpt-output-gpt-5-6-prompt-tuning-work-packet.md`、評価は`artifacts/20260730t011516z-gpt-5-6-prompt-tuning-evaluation.md`へ保存した。artifact自体の追加ReviewはHuman指示により不要である。
- `chatgpt-use` wrapperが自動挿入するdefault-branch fallback文言はexact-branch-only task Promptと競合し得る。今回の回答はexact branch／HEADとdefault branch未使用を明示したため採用したが、wrapper interface改善候補として残る。
- 上記はS12のhermetic／full-regression／distribution／prompt-tuning evidenceであり、S12全体のclosureを意味しない。Plan §22が要求するrefreshed Human authorization、real PATH Oracle create、fresh Review、exact Human decision、`ready/adoption_published` apply、remote parityは未完了のため、S12はHuman gate pendingのまま保持する。

## 2026-07-30 — S14 final combined Review failure and bounded repair

- fresh ChatGPT final combined Reviewはexact pushed HEAD `bb65257155a73b621b0d0b6fb3426393c46de712`をspec／code／QAの三perspectiveで確認し、P0 0／P1 5、`FAIL`と判定した。reviewerはread-onlyで、default branch未使用、repository mutation 0、改善提案0である。
- 正式Review結果は`artifacts/20260730t020224z-chatgpt-output-s14-final-combined-review-fail.json`、別Blue Teamによる修正作業票は`artifacts/20260730t020225z-chatgpt-output-s14-blue-repair-work-packet.md`へ保存した。
- bounded repairはcurrent onboarding companion、apply入口のarchive rejection details、dangling symlink destination、application unit-test boundary、Report gate ledgerへ限定する。`CODE-P1-001`はcreate側catchではなく`run_issue_planning_apply()`のarchive Candidate load catchに残っていた`error.args[0]`推論で再現し、application-owned `IssuePlanningCandidateArchiveRejected.findings`をexact `details`へ保持する最小修正とcharacterization testで閉じる。
- repair、focused／fast／full／distribution検証、fresh current-HEAD Human authorization、live acceptance、S13 commit／pushを完了するまでS14は未admit、merge-readyは未成立とする。

## 2026-07-30 — S14 bounded repair verification and full-regression blockers

- final Review 5 P1のbounded repair後、guide／application／apply infraのfocused 4-file suiteは168 passed、`make lint`はRuff check／formatとmypy 281 filesがPASSした。provider／dogfoodの`application/issue_planning.py`と`infra/issue_planning_apply.py`はbyte-identicalで、wheel／sdist内bytesもprovider sourceと一致した。
- archive applyは`IssuePlanningCandidateArchiveRejected.findings`を`details`へ保持し、dangling symlink destinationはnon-following statでmutation前に拒否する。application unit testsはbootstrap／concrete infra importを持たないapplication-port準拠test doublesへ移行した。
- onboarding companionはS08〜S11 closed、S12 open／refreshed Human authorizationとlive acceptance待ち、S13／S14 not admittedへ訂正した。4 PlantUML diagramはPlantUML 1.2026.6 `-checkonly`をPASSした。
- exact-state full regressionはbranch／HEAD／tracked diff SHA-256を前後固定して実行し、`3 failed, 3140 passed, 76 skipped`、33分50秒だった。failureはcurrent checked-in graphに対するfrozen test snapshot 2件と、final snapshot timeout時に`polls == 2`を満たさないPR observation wait 1件で、3件ともfocused再現した。
- 別Blue Team ChatGPTはexact branch／HEADをGitHub connectorで確認し、graph 2件をvalid authoritative growthに対するtest-data drift、timeout 1件をsub-second quiet-windowの整数切捨てによるruntime defectと判定した。作業票は`artifacts/20260730t031532z-chatgpt-output-s14-full-regression-repair-work-packet.md`へ保存した。
- frozen constantsはEpic `epic-00343`、Issues `iss-00344`〜`iss-00346`、`iss-00346 -> [iss-00344, iss-00345]`だけを機械更新し、Red 2 failuresからGreen 2 passed、validate nodes=227、Ruff／format／diff checkをPASSした。checked-in metadataとassertionは変更していない。
- PR observation waitはquiet-window eligibilityとfinal-timeout stable-state判定を同じabsolute monotonic deadlineへ修正した。unchanged testはRed `polls 1 != 2`からGreen 1 passed、S430／PR observation関連41 passed、provider／dogfood byte parity、Ruff／format／diff checkをPASSした。公開schema、status／reason、timing設定、zero-check grace、wrapperは変更していない。
- 上記3 blockerを含む新しいexact-state full regressionを再実行してPASSするまで、S12 hermetic verificationとS14 final gateは未完了のまま保持する。
- 全repairと上記Report記録を除くexact tracked diff SHA-256 `adaca4ea829bcb5529d82c44da405467dd1e5c6b701c01f06ef4e361c4786a48`を前後固定して再実行し、full regressionは`3143 passed, 76 skipped, 2 warnings`、30分15秒でPASSした。prior 3 blockersのexact nodesも`3 passed`、前後のbranch／HEAD／status／staged空／tracked diff SHAは一致し、QA reviewerはP0／P1 0、PASSと判定した。
- S14 bounded production／projection／guide／test repairはcommit `666baaba`へ集約した。ReportとRed／Blue Team証跡は別のevidence-only commitとして追記し、次のlive authorizationとfresh final Reviewはそのpushed evidence HEADへbindする。
- このPASSはhermetic／full-regression gateを閉じるが、Plan §22のrefreshed Human-authorized live acceptanceと、その後のexact pushed SHAに対するfresh final combined Reviewを代替しない。

## 2026-07-30 — S12 live Oracle boundary pre-submit failure and bounded repair

- refreshed Human authorizationはclean／local-remote identical HEAD `d3473ee3d56b6f12a34952b4b426657b3269a0aa`、`git-bound`、repository外evidence root、canonical三文書byte-identical、merge／auto-merge／branch delete／Issue close／issue finish禁止へbindした。
- 最初のpublic `planning create`は`blocked/oracle_session_recovery_required`を返したが、対応する`specdock-planner-*` session、ChatGPT turn、browser tab、Candidateは0件だった。sanitized direct Oracle reproductionはuser configの`gpt-5.6-pro`を`Unknown GPT-5.6 browser variant "pro"`としてsession作成前に拒否した。
- explicit `Pro` recovery smokeは別Chrome起動を試み`ECONNREFUSED 127.0.0.1:61718`で停止した。session metadataは`promptSubmitted=null`、`chromeTargetId=null`、`conversationId=null`、`tabUrl=null`で、formal planning submissionは0件のままである。
- operator-side `chatgpt-use`でexact GitHub branch／HEADとprovider adapter、tests、個人wrapper／Oracle sourceを参照資料として共有し、製品依存はPATH-resolved Oracleだけに維持するbounded work packetを作成した。正式artifactは`artifacts/20260730t041900z-chatgpt-output-s12-live-oracle-boundary-repair-work-packet.md`、dispositionは`GO_BOUNDED_REPAIR`である。
- provider-owned adapterは`SPECDOCK_ORACLE_REMOTE_CHROME`を必須のclosed loopback endpoint contractとし、`localhost`を`127.0.0.1`へ正規化する。proxy非依存のbounded `GET /json/version`でCDP endpoint／portを検証し、この親process variableをOracle childへforwardしない。
- formal Oracle argvは`--model Pro`、`--browser-model-strategy select`、`--remote-chrome <validated-loopback>`、`--browser-no-cookie-sync`を明示する。hidden `--browser-no-cookie-sync`はOracle 0.16.1のversion contractで保証し、help-visible capability集合には加えない。personal wrapper、profile path、cookie、credential、API fallbackは導入していない。
- Redはfocused unit `53 failed`。Greenはunit `71 passed`、full-regression指定integration `4 passed`、`make lint`のRuff check／418 files format／mypy 281 files、provider／dogfood 2対byte parity、`git diff --check`がPASSした。
- 修復後のexact pushed HEADでformal createを一度だけ再実行する。timeout／disconnect後にprompt submissionが確認された場合はsame-session recoveryだけを許可し、新しいslugで再送しない。Candidate／fresh Review／exact Human decision／apply／remote parityは引き続き未完了である。

## 2026-07-30 — First live authoring ZIP rejection and bounded Prompt repair

- repaired direct Oracle boundaryをcommit `9855eda91d6f279ace07dfa3cd9ee261984476e3`としてpushし、clean／local-remote identical HEADでformal `planning create`を一度だけ実行した。
- Oracle session `specdock-planner-017b25-18192b95`はmanaged Chrome `127.0.0.1:9223`、conversation／target各1件、`promptSubmitted=true`、`requested=Pro`／`resolved=Pro`／`verified=yes`でterminal `completed`となった。underlying numbered model versionは主張しない。
- exactly one `iss-00334-issue-planning-documents.zip`を取得し、Oracle ZIP validationはPASSした。ZIP SHA-256は`d0dafe35cfe695b406a74df3f216339aa157c8ce3d6337ae50af7c249de09747`、single root内はcanonical三文書＋runtime-selected onboarding companionの4 filesだった。
- RuntimeはCandidate publication前に`rejected/archive_rejected`、details `authoring_payload_invalid`で停止した。三文書frontmatter／framingはすべてvalidで、失敗はonboarding companionのrequired distinct section assignmentだけだった。repository mutation、Candidate、Review、Human decision、applyは0件である。
- userが削除したbrowser tabはterminal後のUI tabであり、ZIPとtranscriptはOracle session artifactへ保存済みだった。同一Promptの盲目的再送は行わず、exact ZIPを元filenameのままfresh ChatGPT diagnosisへ渡した。
- diagnosis session `iss00334-authoring-zip-contract-diagnosis`はexact branch／HEADをGitHub connectorで確認し、default branch未使用、`GO_BOUNDED_PROMPT_REPAIR`と判定した。正式artifactは`artifacts/20260730t052721z-chatgpt-output-authoring-zip-contract-diagnosis.md`である。
- defectはprovider Promptがtopicsだけを列挙し、validatorの13 distinct nonempty sections／co-locationを明示しないことだった。実ZIPではCurrent／Target architectureの分割と、`ChatGPT First planning sequence`が`planning workflow`／`planning lifecycle`を含まないことが直接failureで、Purpose／Scopeはtable内tokenによる偶然の一致だった。
- Planner／Semantic Revision resourceへ同一のexact 13-H2／no split-or-merge contractを追加し、Reviewer resourceとvalidatorは変更していない。official updateでprovider／projectionのPlanner SHA-256 `3538b8c8a28dc86c6ff448b0f377e460b41bb484a9b1247f726095c733751051`、Revision `03fd129fc68b2ecc4e95897006b39ac3ae55ad57486cf25672116d3b2d8dc1d2`をbyte-identicalに同期した。
- RedはPrompt contract不在の2 failures／74 passed。GreenはPrompt＋domain unit 76 passed、Prompt budget 23 passed、full-regression指定integration 4 chains、Ruff／format／mypy、provider／projection parity、`git diff --check`がPASSした。既存character ceilingは増やしていない。
- Prompt repairをcommit／pushした新しいexact HEADで、新しいformal createを一度だけ実行する。最初のterminal invalid ZIPはimmutable failure evidenceとして保持し、上書きやCandidate化をしない。

## 2026-07-30 — Second live authoring ZIP rejection and PlantUML role-label repair

- 13-H2 Prompt repairをcommit `65e755ef80733ed28f66024bab4e31d8f6e8c427`としてpushし、clean／local-remote identical HEADで新しいformal `planning create`を一度だけ実行した。
- Oracle session `specdock-planner-a498d2-226aca9a`はmanaged Chrome `127.0.0.1:9223`、fresh conversation／target各1件、`promptSubmitted=true`、`requested=Pro`／`resolved=Pro`／`verified=yes`でterminal `completed`となった。userが削除した旧失敗tabは再利用しておらず、実行中のfresh targetが存在することもCDP一覧で確認した。
- exactly one `iss-00334-issue-planning-documents.zip`を取得した。ZIP SHA-256は`d16e2774f7a841ea0616c4204ddffbdcde61d8f4fa8f83c3c11bf0b6619b99ee`、single root内はcanonical三文書＋runtime-selected onboarding companionの4 filesである。
- RuntimeはCandidate publication前に`rejected/archive_rejected`、details `authoring_payload_invalid`で停止した。三文書はすべてparse成功し、companionもexact 13 nonempty distinct H2と4 PlantUML blocksを満たしたが、`onboarding companion PlantUML role is missing`で拒否された。repository mutation、Candidate、Review、Human decision、applyは0件である。
- 直接原因はPromptがPlantUML roleを`system-context`／`responsibility-boundary`／`planning-sequence`／`implementation-roadmap`と要求する一方、validatorがblock内の空白表記`system context`／`responsibility`または`authority boundary`／`planning sequence`または`issue planning sequence`／`implementation roadmap`または`remaining implementation roadmap`を探索するlexical contract不一致だった。
- operator-side `chatgpt-use` session `iss00334-plantuml-role-contract`はGitHub connectorでexact branch／HEAD identical、default branch未使用を確認し、`GO_BOUNDED_PROMPT_ROLE_LABEL_REPAIR`と判定した。正式artifactは`artifacts/20260730t062126z-chatgpt-output-s12-plantuml-role-label-repair-work-packet.md`である。
- Planner／Semantic Revisionのprovider Prompt 2件だけを空白role表記へ厳密置換し、official updateでprojection 2件をbyte-identicalに同期した。Reviewer、validator、character ceiling、Candidate／Review／Human／apply境界は変更していない。
- RedはPrompt unit 2 failuresでlexical mismatchを再現した。GreenはPrompt unit 23 passed、domain 54 passed、full-regression指定focused integration 4 passed、Ruff check／format、provider／projection parity、`uv build`、validate 227 nodes、`git diff --check`がPASSした。
- このbounded repairをcommit／pushした新しいclean／local-remote identical HEADで、新しいformal createを一度だけ実行する。二つの拒否済みZIPはimmutable failure evidenceとして保持し、上書きやCandidate化をしない。

## 2026-07-30 — ChatGPT First時間分析の保存と後続Issue境界

- Human提供の統合時間分析をInitiative artifact `artifacts/20260730t093657z-research-chatgpt-first-time-analysis-and-optimization.md`へ元ファイルからbyte-identicalに保存した。source／repository artifactはともに55,494 bytes、SHA-256 `2a04a1ffb7b39a6633b94bc0334044e91c72708191cb2f2c9f3573199639e8b4`である。
- 現行Requirement／Design／Plan、provider adapter、Reviewer Prompt、live dogfood evidenceを照合し、bounded ChatGPT Pro consult `iss00334-amend-or-split-decision`でもexact GitHub branch／HEAD `1b9f2c52cb8b61e3c48ec69a981f628720dfe2b5`を確認した。
- Humanは、`iss-00334`に現行accepted contractを完走不能にする実証済み欠陥だけを残し、Planning Review cross-scope hardeningとrole-based intelligence profileを後続Issueへ分離する方針を採用した。
- same-session publication raceは`REQ-020`／`AC-020`に直接結び付くため本Issueで修正する。current accepted contractへ直接結び付くP0／P1、S12〜S14、commit／push、merge-ready PRも本Issueで閉じる。
- general `planning-gap` contract、Pro／High／Extra High routing、tier telemetry、Initiative／Epic／Issue横断policyは本Issueへ追加しない。これらはHuman merge後の最新`main`から独立Issue／branch／PRで実施する。
- 永続handoffはEpic artifact `artifacts/20260730t093657z-disc-chatgpt-first-review-and-tier-follow-up-handoff.md`に保存した。後続Issue planningはこのartifactとInitiative research artifactをrequired sourceとしてcurrent parent docs、existing Issue seeds、dependency graphを再確認する。
- same-session recovery work packetはrepository外sourceとIssue Workbench内2 copiesが同じSHA-256 `2d53cbeb95bc5d7e826038ce2e4b30b1e5c6e7ad89f6ca0a1c9f92e9db08dee9`である。`artifact import chatgpt-output`は`source_ineligible`／`committed=false`でno-write拒否されたため、完全sourceをunavailableへ再分類せず、Workbench／external evidenceのままbounded implementation inputに使用する。canonical adoption、reviewer pass、readinessは主張しない。
- 旧HEADにbindしたauthoring ZIP／Candidate／Reviewは、publication race修正後のfresh current-HEAD Human decision／final assuranceへ流用しない。

## 2026-07-30 — S12 same-session publication race修正

- current HEAD `1b9f2c52cb8b61e3c48ec69a981f628720dfe2b5`ではbounded polling差分が存在しないことを再確認し、`dev-coder`へapproved work packetの積集合だけを再委任した。
- provider-owned adapterはrecovery全体を一つの`time.monotonic()` deadlineへbindし、harvest前にsame session stateを再読する。harvest timeoutは残り時間を上限とし、prompt最大1回、harvest最大1回、new session 0を維持する。
- harvestのnonzero、`TimeoutExpired`、`OSError`後もsame exact session metadataだけをpollする。terminal／invalidは即時終了し、deadline時点で未解決の場合だけ既存`blocked/oracle_session_recovery_required`へ接続する。
- Redはeventual completion 2件、shared deadline 1件、invalid metadata 3件の計6 failures。Greenはadapter unit 77 passed、artifact reader 27 passed、full-regression指定integration 4 passed in 35.45s。
- worker側で`make lint`のRuff／418 files format／mypy 281 files、provider／projection parity、`git diff --check`がPASSした。Mainもprovider／projection parity、`git diff --check`、上記77／27／4 testsを再実行してPASSを確認した。
- public command family、Candidate／Review／Human／apply契約、model selector、Prompt contractは変更していない。残存gateは新しいexact pushed HEADでのreal Oracle publication lag、Candidate、fresh Review、exact Human decision、apply／remote parityである。
- No material implementation decisions beyond the approved plan.

## 2026-07-30 — S12 live lifecycle完了とadoption publication

- pushed source HEAD `f488121e80fc93f01cb64fab70a06d306c903804`からpublic git-bound `planning create`を実行し、session `specdock-planner-2b4a16-b15e0675`が`ok/candidate_created`で完了した。publication lagをsame-session pollingで収束できることをliveで確認した。
- Candidate IDは`iss-00334-v1-20260730t094713z`、Candidate ZIP SHA-256は`ee0b3be840f1de1cb182db4ee9685acba7cc90d277ceffa2f628edc07a18350a`、operation binding SHA-256は`0a518163ba34447001bfc4b1e60d84b567a055a352f4dfbb51b1ee1f9fc0b187`である。ZIP inventory、CRC、required documents／artifactsを確認した。
- fresh git-bound Planning Reviewはsession `specdock-reviewer-2b4a16-ddf4e99f`、verdict `PASS`、findings 0。reviewed identity SHA-256は`be336298dd14b882285010097acf37afd52b61fc9789f775d7174f8d14d98b5b`、Review result SHA-256は`2a9c115c8ca6490d4b6e596ff805e72a140599976a5082eae9a59707bf41bc5c`である。
- Human decision artifact `artifacts/20260730t102056z-planning-human-decision-7ad8e5f063bc9e13.json`は上記Candidate／Review／source HEADへexact bindし、`approved`、`plan_adoption=true`、`implementation_start=true`を記録する。
- git-bound applyはoperation ID `7ad8e5f063bc9e13f6271e2dfa250dbae50f8a32cbb3d82d382be9274a038368`、result `ready/adoption_published`で完了した。canonical requirement／design／planはbyte-identicalに維持し、managed onboarding guideとdecision artifactだけをpublication対象へ加えた。
- adoption commitは`a4cf67bf6b8d75e5fc1eb6d67a858db1a300d915`。apply後のsync、227-node validate、assurance verify、clean worktree、local／remote identicalを確認した。
- 旧「残存gate」記録は当時の履歴として保持するが、このsectionがlive create、Candidate、Review、Human decision、apply／remote parityのcurrent statusをsupersedeする。

## 2026-07-30 — Final combined Review FAILとbounded closure repair

- exact adoption HEAD `a4cf67bf6b8d75e5fc1eb6d67a858db1a300d915`へfresh defect-only final combined Reviewを実行した。sessionは`iss00334-final-combined-review-a4cf67bf`、model evidenceは`requested=Pro`／`resolved=Pro`／`verified=yes`、verdictは`FAIL`である。
- `FINAL-P1-001`は`semantic_revision`のraw slugとOracle 0.16.1の`semantic-revision`正規形が一致せず、実laneがsame sessionを回収できない欠陥である。
- `FINAL-P1-002`は親`HOME`／`ORACLE_HOME_DIR`とrepository cwdによりOracle-native configを読むことを欠陥としたが、HumanはローカルOracle本体が自身の通常configを利用することは許容範囲であり、SpecDockがHOME／configを上書き・隔離すべきではないと訂正した。このfindingはproduct defectとして不採用とした。
- `FINAL-P1-003`は本Reportが上記live lifecycle完了を反映していないQA不整合であり、この追補でcurrent statusを同期した。
- 別Blue Team ChatGPT session `iss00334-final-p1-blue-team`へ3 findingだけを渡し、設計追加を禁止して最小修正を具体化した。Human correction後はsession ID固定点とReport追補だけを採用し、work packet `artifacts/20260730t110128z-final-p1-repair-chatgpt-blue-team-work-packet.md`を`partially_adopted`へ訂正した。
- Oracle local configurationの正式境界はHuman decision artifact `artifacts/20260730t111338z-disc-oracle-local-configuration-boundary-correction.md`へ保存した。SpecDockはformal必須値をdirect argvで明示し、Oracle-native configを上書き・隔離せず、personal wrapper／path／fallbackには依存しない。
- dev-coderのwrite allowlistはprovider adapter、mechanical dogfood projection、focused adapter testsに限定した。修正前Redで`semantic_revision`のOracle正規化差異を再現し、Greenでは全roleをOracle 0.16.1 custom-slug固定点にした。
- Main再検証はadapter 78 passed、artifact reader 27 passed、明示full-regression permission付きprovider／projection parity 2 passed、`make lint`（Ruff／418 files format／mypy 281 files）、227-node validate、provider／projection byte parity、`git diff --check`がPASSした。
- repair commit `65af92d0062d47c0fcbaba7ea79d2839ae062bf9`をpushしlocal／remote `0/0`を確認した。ローカルOracleの通常configを尊重した環境でpublic `planning create`を一回だけ実行し、session `specdock-planner-ff7f71-232b24f6`が同じ正規形IDのまま`completed`となった。alternate name／`-2` sibling／replacement sessionは0である。
- live resultは`ok/candidate_created`。Candidate ID `iss-00334-v1-20260730t111741z`、logical filename `20260730t111741z-iss-00334-issue-planning-candidate-v1.zip`、source HEAD `65af92d0062d47c0fcbaba7ea79d2839ae062bf9`、ZIP SHA-256 `4b1487db62ff97271471589e4f9e4ca12667d25ea94a1fd29841c86ae3bd4ee7`、operation binding SHA-256 `5fe3c7d30f804d0b9fea8f4910c5818a7c848b8bacb4a6b3457f09c9bac9cfc8`、58,165 bytesである。
- ZIPはMANIFEST、CHECKSUMS、SOURCE-BASELINE、三文書、onboarding guideを含み、`unzip -t`で全entry PASS。external output rootは`/private/tmp/codex-agent-work/501/session-20260730t094700z-iss00334-fresh-head-live-acceptance-376f2255/live-evidence/final-slug-smoke-65af92d0`で、repository mutationは0、run後もclean／remote parity `0/0`である。
- このReportをcommit／pushしたexact HEADへfresh closure Reviewを行う。merge、Issue close、branch deletion、`issue finish`は引き続きHuman-onlyかつ未実施である。

## 2026-07-30 — Fresh final closure Review PASS

- exact pushed HEAD `5bd285377161b949247f2c3a9b3c6a800b2870c0`へ別fresh ChatGPT Pro closure Reviewを実行した。sessionは`iss00334-final-closure-5bd28537`、model evidenceは`requested=Pro`／`resolved=Pro`／`verified=yes`、default branch substitution 0である。
- `FINAL-P1-001`は、closed role mapping、one session ID reuse、Oracle 0.16.1 fixed-point tests、provider／projection identical blob、live session `specdock-planner-ff7f71-232b24f6`のexact-name completionによりclosed。
- `FINAL-P1-002`はHuman decisionにより`not-applicable-by-human-decision`。Oracle-native configを尊重しながらformal必須argv、single Prompt、`shell=False`、personal wrapper／API fallback 0を維持するcurrent implementationと一致した。
- `FINAL-P1-003`は、historical pending recordsを保持したままinitial adoption、Review、Human decision、apply、repair、tests、live smoke、remote parityを後続sectionでsupersedeしたためclosed。
- verdictは`PASS`、新規P0／P1 0、`merge_ready_recommendation=true`。正式artifactは`artifacts/20260730t115302z-s14-fresh-final-closure-review-pass.md`である。
- 本artifact／Report publication後、ready PRを作成しfixed Codex reviewとGitHub Actionsを観測する。merge、Issue close、branch deletion、`issue finish`はHuman-onlyのまま実行しない。

## 2026-07-30 — PR #351 required-CI failureとbounded U001 repair

- ready PRは`https://github.com/chemitaro/spec-dock/pull/351`、base `main`、head `iss-00334-implement-chatgpt-issue-planning-workflow`、observed HEAD `555dafd6f9e1252ddf8b50cb23c275e20c263266`で作成した。
- fixed observationはtrigger comment `5130515748`を`2026-07-30T11:57:12Z`に一度だけ投稿したが、required `Provider CI / provider-tests` run `30540472689`、job `90863805552`が先に失敗したため、Codex Reviewはterminal判定前に停止した。
- failureは`test_s10_current_v4_guide_satisfies_completeness_contract`の1件だけで、fresh checkoutに存在しないGit管理外`spec-dock/active/issue` symlinkからhistorical v4 ZIPを開いて`FileNotFoundError`となった。canonical Issue artifact pathのexact ZIPはtrackedされている。
- fresh ChatGPT consultation `iss00334-pr351-ci-repair-consult`はexact branch／HEADを確認し、default branchを検査せず、one-test fixture path修正を最小の正しいrepairとして支持した。model evidenceは`requested=Pro`／`resolved=Pro`／`verified=yes`。正式advisoryは`artifacts/20260730t120701z-01-pr-351-required-ci-repair-chatgpt-consultation.md`である。
- HumanのOracle local configuration boundaryは変更しない。SpecDockはOracleの通常configを尊重し、formal必須値だけをdirect argvで明示する。U001はproduct runtime、Oracle invocation/configuration、canonical docs、ZIP bytes、CI setupを変更しない。
- dev-coderは`tests/unit/domain/test_issue_planning_candidate.py`の対象testだけを変更した。exact test `1 passed`、module `54 passed`、Main ordinary fast pytest `1141 passed, 2119 skipped`、`make lint`（Ruff／418 files format／mypy 281 files）、validate `nodes=227`、`git diff --check`がPASSした。
- repair batchは`artifacts/20260730t115808z-pr-repair-batch-pr-351-repair-batch.md`、unitは`artifacts/20260730t120701z-disc-pr-repair-unit-active-pointer-fixture.md`。このrepairをcommit／pushし、新HEADへ新しい`post-once` observationを行う。旧HEADのresume boundaryは再利用しない。
- repair commit `b70f599f1689b2867fc70699c68c3d955d1f18d5`をpushした。new-head trigger `5130652815`／`2026-07-30T12:12:09Z`のfresh observationはActions runs `30541559750`、`30541559745`、`30541556692`がすべてPASSし、Codex explicit no-findings completion、P0〜P3 0、unresolved thread 0、limitation 0、decision `passed/merge_prepared`でterminal完了した。
- observation resultのdecision fingerprintは`aca3dc1928a3abbb4ad97a85fdede23b630b0a9ac11084b6bf99c8f29ccfa2f6`。merge、auto-merge、branch deletion、Issue close、`issue finish`は未実施のままHumanへ引き渡す。

## 2026-07-30 — PR #351 P1 race closure S002〜S006

- exact pushed HEAD `6c9302ab08c7f352e85a199b65bdeb522376171c`へのfresh observationはrequired Actions 3件をPASSしたが、Review `4818771681`がCandidate output-directory TOCTOUとapply archive preimage raceをP1、`information_insufficient` typed transportをP2として報告した。P2はfollow-upに固定し、branch mutation対象へ含めていない。
- repair batchは`artifacts/20260730t115808z-pr-repair-batch-pr-351-repair-batch.md`。F002／U002とF003／U003を独立unitとして扱い、ChatGPT Blue consultationをS002〜S006で継続した。transcriptは`20260730t130735z-01-pr-351-s002-p1-repair-chatgpt-consultation.md`、`20260730t134843z-pr-351-s003-race-closure-chatgpt-consultation.md`、`20260730t141210z-pr-351-s004-backed-up-recovery-chatgpt-followup.md`、`20260730t143143z-pr-351-s005-atomic-stage-state-validation-chatgpt-followup.md`、`20260730t145257z-pr-351-s006-no-transaction-state-chatgpt-followup.md`へ保存した。
- operator-side consultationは指定`chatgpt-use` wrapperを使用し、製品runtimeの依存を増やしていない。初回S003は`requested=Pro`／`resolved=Pro`／`verified=yes`。同じBlue conversationのfollow-upはmodel再選択を行わないため`resolved=(unavailable)`／`verified=no`だが、exact current branch／HEAD identicalを各回答が確認し、default branch substitutionを禁止した。
- HumanのOracle local configuration boundaryは変更していない。PATH-resolved local Oracleが自身の通常native configを読むことを許容し、SpecDockはformal必須値だけをdirect argvで明示する。HOME／configの上書き・隔離、personal wrapper／absolute path／API fallback依存は導入していない。
- Candidate publisherはprivate stage directoryを廃止し、validated output descriptor直下のrandom hidden staged ZIPをatomic `openat(O_CREAT|O_EXCL|O_NOFOLLOW)`して成功fdをownership起点にした。write／fsync／read／review／identity derivationはfd／captured bytesへbindし、publish／cleanupはsame-objectの場合だけ行う。public Candidate schema、deterministic ZIP bytes、Candidate identity、Darwin／Linux no-replace contractは不変である。
- applyはHuman-bound canonical／companion preimageをtransaction backup前と`after_operation_recorded`直後に照合し、drift時にconcurrent bytesをrestoreしない。`BACKED_UP`はbackup snapshotからactual driftとno driftを区別してdiscard-only recoveryする。
- durable stateはclosed vocabularyへ制限し、transaction recoveryは`BACKED_UP`または`MUTATING`／`VALIDATED`／`SYNCED`／`STAGED`だけを許可する。no-transaction routeは`OPERATION_RECORDED`／`ROLLED_BACK`だけがattempt／new transactionへ進み、unknown／invalid stateとorphan publicationはevidenceを変更せず`recovery_required/restore_mismatch`で停止する。
- successful rollbackはtransaction absenceとoperation-directory durabilityを確認し、`ROLLED_BACK`をatomic記録してからだけ`rolled_back`を返す。commit resume／transaction recovery precedence、public status／reason set、operation schema／ID、`MUTATING`以降のexact restore semanticsは維持した。
- Main統合検証はCandidate infra `29 passed`、Apply unit `19 passed`、明示full-regression Apply integration `60 passed`、通常fast lane `1152 passed, 2144 skipped`、`make lint`（Ruff／418 files format／mypy 281 files）、provider／dogfood byte parity、validate `nodes=227`、`git diff --check`がPASSした。
- fresh S006 Spec／Code／QA reviewersは各P0／P1 0、PASS。reviewers側scoped regressionは`108 passed`。正式local closure evidenceは`artifacts/20260730t150254z-review-pr-351-s006-local-closure-pass.md`である。
- accepted residualはportable Darwin／Linuxにおけるfinal identity-check-to-name-operation syscall intervalと、same-credential actorが別のsemantically valid private stateへ書き換える場合である。observed replacement／invalid stateはfail closedする。
- `origin/main` fetch後の`HEAD...origin/main`は`115 0`で、このbranchはcurrent mainにbehind 0のため追加mergeは不要だった。
- この追補とimplementationをcommit／pushしたnew exact HEADへActionsとfixed Codex reviewを一度だけ再観測する。merge、auto-merge、branch deletion、Issue close、`issue finish`は引き続き実施しない。

## 2026-07-30 — PR #351 exact-head P1 closure S007

- exact pushed HEAD `91715eecf306bd0c978da922f87193151764cdcd`へのfresh observationはrequired ActionsをPASSしたが、Review `4820348714`が`apply-output-directory-toctou`、`apply-remote-ref-cas`、`candidate-stage-identity-toctou`の3件をP1として報告した。`apply-post-commit-record-gap`はP2であり、blocking repairへ含めない。raw observationは`artifacts/20260730t151634z-pr-351-observation-head-91715eec.json`へ保存した。
- operator-side指定`chatgpt-use` wrapperからfresh ChatGPT Pro session `iss00334-pr351-s007-p1-repair`を実行した。`requested=Pro`／`resolved=Pro`／`verified=yes`、exact repository／branch／HEAD確認、default branch substitution 0である。正式concretizationは`artifacts/20260730t155200z-pr-351-s007-p1-repair-chatgpt-concretization.md`へ保存した。
- wrapperの既存Blue conversation follow-upはWork mode検証不能で、fresh invocationの最初の試行はwrapper非対応`--engine`で、いずれもpre-submit停止した。重複Prompt送信はなく、正しいwrapper interfaceでfresh submissionを一度だけ行った。
- HumanのOracle configuration decisionは変更しない。PATH-resolved local Oracleは自身の通常native configを利用し、SpecDockはそれを上書き・無効化・隔離しない。formal再現性に必須の値だけを明示fieldからdirect argvへ渡し、personal wrapper path、`chatgpt-use` runtime依存、API／default-branch／alternate-profile fallbackは導入しない。
- Candidate publicationはverified staged FDをpublication authorityとした。Darwinは`fclonefileat`、Linuxは非特権環境で成立する`linkat(AT_FDCWD, /proc/self/fd/<staged-fd>, ..., AT_SYMLINK_FOLLOW)`でfinal entryを作成し、pathname fallbackを行わない。公開後finalは`O_NOFOLLOW`で開き、regular file、SHA-256、byte countを既知identityと照合する。stage／final cleanupはcaptured identity一致時だけ実施し、output directoryを`fsync`する。
- applyはapplicationがvalidated `OutputDirectoryGuard`をresume／transaction境界まで保持し、transaction開始時にdirectory FDを再取得してdevice／inodeを照合する。operation state、attempt、transaction backup／recovery、commit／publication／cleanupのevidence lifecycleは同じdirectory FD相対操作へ移した。capture前の置換はrepository／evidence mutation 0で拒否し、capture後のpathname置換時も元directory objectだけを更新する。
- initial／resume pushは同一のdedicated exact-old CAS helperへ統一した。push直前にlocal HEAD、parent、tree、branchを再証明し、sourceはexact local commit SHA、leaseは`operation.expected_head`へbindする。generic Git validatorは任意の`--force-with-lease`を引き続き拒否し、CAS失敗後はremote present／absent／unavailableを既存public status／reasonへ分類する。
- 最初のfresh local Spec／Code／QA reviewは、Linux非特権publication、resume開始時remote absent分類、application guard identityの回帰テスト不足をP1として報告した。各findingは別fresh ChatGPT Pro session `iss00334-s007-linux-publicatio`、`iss00334-s007-resume-remote`、`iss00334-s007-guard-regression`でexact branch／HEADを確認して最小work packetへ限定し、正式evidenceを同名のS007 concretization artifact 3件へ保存した。
- Linuxは`/proc/self/fd`＋`AT_SYMLINK_FOLLOW`へ修正し、real Linux syscall testでnon-rootかつ`CAP_DAC_READ_SEARCH`なし、source-name replacement後のinode／bytes同一性、no-replaceを必須化した。macOSではこの1件だけskipし、最終Linux実証はProvider CIで取得する。
- resume開始時は既存三値観測を使用し、remote absentを`blocked_remote_diverged/remote_diverged`、unavailableを`publication_pending/remote_parity_unconfirmed`へ分離した。削除済みremoteと観測不能の2 integration testsはpush／validation／sync 0、HEAD／commit evidence不変を検証する。
- application testはvalidated opaque guardがresume probeとtransaction runnerへ同じobject identityのまま渡ることを`is`で固定した。production applicationの追加変更はない。
- Main再検証はCandidate infra `34 passed, 1 skipped`、application apply `36 passed`、Apply unit `22 passed`、明示full-regression Apply integration `68 passed`、通常fast lane `1161 passed, 2153 skipped`、`make lint`（Ruff／418 files format／mypy 281 files）、provider／dogfood 5対byte parity、validate `nodes=227`、`git diff --check`がPASSした。
- fresh S008 Spec／Code／QA reviewersは各P0／P1 0、PASS。正式local closure evidenceは`artifacts/20260730t163933z-review-pr-351-s008-local-closure-pass.md`である。
- P2 `apply-post-commit-record-gap`はnon-blocking follow-upとして保持し、この指摘だけを理由にbranch mutationや再レビューを行わない。commit／push、exact code HEADへのfresh ChatGPT defect-only review、最終evidence HEADへのfixed PR observationを残存gateとする。

## 2026-07-30 — S008 exact code review PASSとlatest main統合

- S007／S008 implementation、tests、evidenceはcommit `7cc387201a48f5bd758c25fafa4df8cb20728df6`としてpushし、local／remote parity `0/0`を確認した。
- exact pushed code HEADへfresh ChatGPT Pro defect-only Reviewを実行した。session `iss00334-s008-final-review`は`requested=Pro`／`resolved=Pro`／`verified=yes`で、GitHub connectorからexact repository／branch／HEADを確認し、default branch substitution 0、P0 0、P1 0、`PASS`を返した。正式artifactは`artifacts/20260730t165620z-pr-351-s008-final-chatgpt-review-pass.md`である。
- Review後、PRが`CONFLICTING`へ変化していることを検出した。`origin/main`は先行確認後に28 commits進み、latest mainは`da38dc58693e5e4193ca31a60b9fe41ae35248e1`だった。
- latest mainをmergeし、provider／dogfoodの`application/ports.py`と`cli/bootstrap.py`の4 conflictだけを解消した。すべて加算競合であり、Issue Planning dependencies／portとmainのexplicit-file artifact import dependencies／portを両方保持した。runtime contractの削除や優先順位変更はない。
- merge commitは`99374214ebf943ceb70dc186bf782993784eb481`。merge後の検証はfast lane `1271 passed, 2167 skipped`、明示full-regression Apply integration `68 passed`、`make lint`（Ruff／425 files format／mypy 287 files）、provider／dogfood 5対byte parity、validate `nodes=227`、`git diff --check`がPASSした。
- Linux real-syscall assertionはunprivileged Provider CIでのPASSを必須とする。最終evidence publicationをcommit／pushし、exact final HEADへfixed PR observationを一度だけ行う。merge、auto-merge、branch deletion、Issue close、`issue finish`は実施しない。

## 2026-07-30 — PR #351 final-head observationとS009 bounded repair

- S008 evidence commit `be0c84a6ec3d6404700c98aaa6e81d8cceab5ea2`をpushし、local／remote parity `0/0`を確認した。このexact HEADへのfixed observationではrequired Actions 3件がすべてPASSし、Linux unprivileged real-syscall assertionもProvider CI上でPASSした。
- Review `4821379670`は、`candidate-output-path-detachment`、`archive-preimage-revalidation`、`canonical-write-ancestor-symlink-race`の3件をP1として報告した。raw observationは`artifacts/20260730t172342z-pr-351-observation-head-be0c84a6.json`へ保存した。
- `oracle-session-repository-boundary`、`mechanical-meaning-invariant-unenforced`、既存`apply-post-commit-record-gap`、incomplete-input transportはP2のnon-blocking follow-upである。これらだけを理由にbranch mutationや追加レビューを行わない。
- operator-side指定`chatgpt-use` wrapperからfresh session `iss00334-s009-three-p1`を実行した。model evidenceは`requested=Pro`／`resolved=Pro`／`verified=yes`で、GitHub connectorからrepository、branch、exact HEADを確認し、default branch substitution 0である。
- ChatGPTは3 findingをいずれもP1として維持し、Candidate修正は独立、Applyの2修正は同じdescriptor-relative mutation／rollback primitiveを所有するため`canonical-write-ancestor-symlink-race`、`archive-preimage-revalidation`の順に直列実装するwork packetへ限定した。正式concretizationは`artifacts/20260730t172342z-pr-351-s009-three-p1-chatgpt-concretization.md`である。
- HumanのOracle local configuration boundaryは変更しない。PATH-resolved local Oracleが自身の通常native configを利用することを許容し、SpecDockはHOME／configを上書き・無効化・隔離しない。作業契約上必須の値だけを明示fieldからdirect argvへ渡し、personal wrapper path、`chatgpt-use` product runtime依存、API／default-branch／alternate-profile fallbackは導入しない。
- S009 implementationはprovider authorityとfocused testsだけを手編集し、dogfood sourceはofficial updateで機械的に投影する。公開status／reason／schema、Human binding、Candidate ZIP bytes、remote push CAS、Oracle adapter／configurationは変更しない。
- Candidate publisherは、descriptor-relative publication、bytes／identity検証、stage cleanup、directory `fsync`の後、成功確定前にvisible output pathが同じdirectory objectと同じpublished entryへ接続していることをno-followで再証明する。symlink／別ordinary directoryへの差し替えは`CandidateOutputRejected`となり、descriptor側のpublished entryも既存ownership cleanupで削除する。
- Apply transactionはrepository rootからcomponent-wise `O_NOFOLLOW`でcanonical／companion／decision targetのparent FDを保持し、snapshot、mutation、rollbackをそのFDへ相対化した。parent device／inodeはprivate backup manifestへ保存し、crash recoveryで再証明できない場合は既存`recovery_required/restore_mismatch`としてwriteせず停止する。
- exact preimage検証と置換を、Darwin `renameatx_np(RENAME_SWAP)`／Linux `renameat2(RENAME_EXCHANGE)`のatomic exchange境界へ結合した。displaced entryがcaptured `FileSnapshot`と一致しなければexchange-backしてconcurrent bytesを保持し、既存`stale/apply_target_changed`へ分類する。captured absenceはdescriptor-relative no-replace publication、rollbackはprivate mutation ledgerでtransaction-owned mutationだけを逆適用する。
- deterministic RedはCandidate visible pathのsymlink／ordinary-directory切断2件、`MUTATING`遷移中のcanonical edit、canonical置換間のedit、absent companion concurrent createを再現した。ancestor swapはfinal-parent symlinkではなく上位componentのrename／replacementとして固定し、外部sentinel不変を検証する。
- Main再検証はCandidate／Apply／application focused `100 passed, 1 skipped`、明示full-regression Apply integration `73 passed`、通常fast lane `1279 passed, 2172 skipped`、`make lint`（Ruff／425 files format／mypy 287 files）、provider／dogfood Issue Planning byte parity、validate `nodes=227`、`git diff --check`がPASSした。
- official updateはIssue Planning 2ファイルに加え、latest mainでproviderのみ更新済みだった`application/import_file_artifact.py`と`domain/artifacts.py`をdogfoodへ機械投影した。4組すべてprovider sourceとbyte-identicalであり、projection先の独立編集はない。

## 2026-07-30 — PR #351 S010〜S012 bounded crash-recovery closure

- S009未コミット差分へのfresh Spec／Code／QA reviewは、Candidate rejection cleanup、absent-state rollback、staged ownership、pre-mutation durable intent、rollback progress、native ABI testの具体的なP1を確認した。改善提案、P2／P3、公開contract再設計はfindingから除外した。
- fresh ChatGPT Pro session `iss00334-s010-five-p1`は、GitHub connectorでrepository、branch、pushed HEAD `be0c84a6ec3d6404700c98aaa6e81d8cceab5ea2`を確認し、5件だけをRed／Green work packetへ具体化した。正式artifactは`artifacts/20260730t181147z-pr-351-s010-five-p1-chatgpt-concretization.md`である。
- Candidate rejection cleanupはpublic logical filenameをcheck-then-unlinkせず、private `0700` cleanup directoryへdescriptor-relative no-replace renameし、owned inodeだけを削除する。Linux／Darwin direct ABI、symbol欠落、`EEXIST`、その他errnoをunit testで固定した。
- Applyはprivate workspaceでstaged ownershipを固定し、forward mutationを`prepared`／`published`、rollbackを`rollback-prepared`としてwrite-ahead記録する。absent removalはownership-safe quarantine、rollbackはexact already-restored stateを冪等に分類し、復元済みentryを1件ずつdurably drainする。
- S010 fresh Spec／Code reviewが確認したabsent-preimage publication直後のcrashは、targetがrecorded afterでworkspace staged slotがexact absenceの場合だけpublishedとして分類し、decision／companion双方のintegration Red／Greenで閉じた。
- S010 closure Code reviewが確認したexisting-preimage reverse exchange後・workspace cleanup前のcrashは、fresh ChatGPT session `iss00334-s011-existing-rollback-workspace`で1件だけを具体化した。正式artifactは`artifacts/20260730t184838z-pr-351-s011-existing-rollback-workspace-chatgpt-concretization.md`である。outer mutation 1件を`rollback-prepared`へ更新し、pre/post exchange、post unlink、post rmdirをdescriptor-relativeに再開可能とした。
- S011 final Code reviewが確認したworkspace作成後・ledger登録前のcrashは、fresh ChatGPT session `iss00334-s012-workspace-preledger-crash`で1件だけを具体化した。正式artifactは`artifacts/20260730t191619z-pr-351-s012-workspace-preledger-crash-chatgpt-concretization.md`である。
- S012はprivate ledgerへsingleton `workspace_intent`を追加し、workspace名を`mkdir`前、workspace inodeをchild作成前、staged inodeをmode変更／write前にdurable bindする。forwardとexisting rollbackは同じprotocolを使い、complete mutation handoff後だけintentをclearする。unknown non-empty、wrong inode、extra entry、unsafe objectは全bytesとintentを保持してfail closedする。
- S012 final QAが確認したabsent rollbackの同型crash windowは、fresh ChatGPT session `iss00334-s013-absent-rollback-intent`で1件だけを具体化した。正式artifactは`artifacts/20260730t195025z-pr-351-s013-absent-rollback-intent-chatgpt-concretization.md`である。singleton intentへ`rollback-absent`を追加し、decision／companionともworkspace予約、workspace／future quarantine identity bind、`rollback-prepared` handoff、intent clearの順に統一した。
- S013統合後のMain再検証はfocused Candidate／Apply／application `148 passed, 1 skipped`、明示full-regression Apply integration `88 passed`、通常fast lane `1327 passed, 2187 skipped`、`make lint`（Ruff／425 files format／mypy 287 files）、provider／dogfood byte parity、validate `nodes=227`、`git diff --check`がPASSした。
- local closureの詳細なRed／Green、fresh review履歴、remaining gatesは`artifacts/20260730t192855z-review-pr-351-s009-s015-local-closure-evidence.md`へ保存した。S011 final Specの「ReportがS009で停止している」という指摘はこの追補で閉じる。
- HumanのOracle local configuration boundaryは変更しない。PATH-resolved local Oracleは通常native configを利用でき、SpecDockは上書き・無効化・隔離しない。formal必須値だけを明示fieldからdirect argvへ渡し、personal wrapper／`chatgpt-use` product runtime依存、API／default-branch／alternate-profile fallbackは導入しない。
- 残存gateはS013後のfresh Spec／Code／QA P0／P1 review、commit／push、exact pushed code HEADへのfresh ChatGPT defect-only review、最終evidence publicationとfixed PR observationである。merge、auto-merge、branch deletion、Issue close、`issue finish`は実施しない。

## 2026-07-30 — S014 same-UID private threat findingの非採用

- S013後のfresh Spec／QA reviewはP0／P1 0でPASSした。fresh Code reviewは、Candidate private cleanup、Apply workspace cleanup、existing rollback exchangeの最終pathname操作へ、同一UIDの敵対プロセスが能動的に差し替える3件をP1とした。
- fresh ChatGPT Pro session `iss00334-s014-private-entry-final`は3件を同じthreat model下でP1と確認した。正式advisoryは`artifacts/20260730t202538z-pr-351-s014-private-entry-final-cas-chatgpt-concretization-not-adopted.md`である。
- 回答案はowned bytesを自動削除しないprivate retained storage、retention directory、target workspaceとのsame-device適格性、永続inventoryを必要とした。これは小修正ではなく、新しいsecurity threat model、storage lifecycle、capacity／purge operationを導入するarchitecture変更である。
- canonical Requirement／Designはcanonical／public path drift、preimage、symlink／ancestor、atomic publication、rollback確認を要求するが、同一UID adversaryによるprivate `0700` namespace内部の能動改変をsecurity boundaryとして定義していない。
- defect-only reviewが未定義threat modelを追加して現行Issueを肥大化させないため、S014 3 findingはcurrent P0／P1として不採用とし、branch mutationを行わない。詳細decisionは`artifacts/20260730t202539z-disc-s014-private-same-uid-threat-scope-disposition.md`である。
- residual riskは明示して保持する。将来same-UID adversary protectionを要件化する場合は、独立Issueでthreat model、retention authority、保管期限／容量／purge、cross-filesystem eligibilityを先に設計する。
- fresh closure reviewはcanonical contract、通常並行変更、process crashへ限定し、private workspace内部を能動改変するsame-UID adversaryを現行P0／P1判定から除外する。
- 同reviewで追加された「交換前から開かれた正本FDへ交換後にwriteされたbytesを旧inode unlinkが保持しない」というfindingも、current P0／P1として不採用とした。canonical contractのexact preimage authorityはatomic replacement boundaryまでであり、交換後のstale-FD write retentionは定義していない。保証にはretained storageまたはcooperative lockingが必要で、S014と同じarchitecture拡張になる。
- D-20260730-S014-SCOPEはprivate namespace tamperingとpost-exchange stale-FD retentionの両方をcurrent scope外としてresolveし、riskは独立threat／concurrency contract候補として保持する。

## 2026-07-30 — S015 public／canonical pre-boundary CAS closure

- accepted D-20260730-S014-SCOPE下のfresh Code reviewは、scope内の通常並行変更として2件をP1とした。Candidateはdescriptor publication後・ownership capture前のpublic final replacement、Applyはexpected target open後・exchange前のatomic editor replacementである。
- fresh ChatGPT Pro session `iss00334-s015-public-canonical-final`はGitHub connectorでrepository、branch、pushed HEAD `be0c84a6ec3d6404700c98aaa6e81d8cceab5ea2`を確認し、2件だけを既存contract内のwork packetへ具体化した。正式artifactは`artifacts/20260730t211451z-pr-351-s015-public-canonical-final-cas-chatgpt-concretization.md`である。
- Candidate publication helperは`_OwnedEntry`を直接返す。Linuxは`linkat`前にverified staged FDをduplicateしてhard-link inodeへbindする。Darwinはunpredictable private capture名へcloneし、そのcloneをopenして実inodeへbindしてからdescriptor-relative no-replace renameする。callerはpublic final pathの再openをownership authorityにしない。
- Applyはexchange後のworkspace側actual displaced attachmentをidentity／snapshotで捕捉する。expected opened inodeと異なるCAS missでもcanonicalがexact staged、workspaceがexact observed displacedであることを再証明し、一度だけexchange-backする。canonicalへactual concurrent attachmentを戻し、workspaceのexact transaction stagedだけをcleanup、prepared evidenceをdiscardして既存`stale/apply_target_changed`へ分類する。
- RedはCandidate publication直後のsame-byte別inode final replacement、Apply exchange直前のbyte-different／same-byte別inode atomic editor replacementを再現した。修正前はunknown Candidate cleanupまたは`recovery_required/restore_mismatch`とunauthorized canonical replacement残留になった。
- S015統合後のMain再検証はfocused Candidate／Apply／application `153 passed, 1 skipped`、明示full-regression Apply integration `89 passed`、通常fast lane `1332 passed, 2188 skipped`、`make lint`（Ruff／425 files format／mypy 287 files）、provider／dogfood byte parity、validate `nodes=227`、`git diff --check`がPASSした。
- S014の非採用scopeは変更しない。S015はpublic／canonical atomic boundary前の通常並行変更だけを修正し、retained storage、locking、private same-UID adversary、post-exchange stale-FD retentionを導入していない。
- fresh Spec reviewが提起したexchange-back中の第三のatomic replacementは、D-20260730-S015-CONTENTIONとして処分した。現実装は第三のattachmentをprivate workspaceへ保持し、`recovery_required/restore_mismatch`でcommit／pushせず停止する。継続中multi-writer下でcanonical pathnameが常に最新attachmentを指す保証はlocking／retention／retry policyを要するため、current defect-only P0／P1 scopeへ追加しない。
- HumanのOracle local configuration boundaryは変更しない。PATH-resolved local Oracleは自身の通常native configを利用でき、SpecDockはこれを上書き・無効化・隔離・強制しない。formal workflowに必須の値だけを明示fieldからdirect argvへ渡す。
- fresh bounded Spec／Code／QA reviewは、accepted contention boundaryの直接回帰テスト欠落と、`after_diff_proof`後のworktree driftを`git add`がunauthorized staged bytesとして取り込み得るP1を確認した。QAはP0／P1 0でPASSした。
- S016は指定`chatgpt-use` wrapperのfresh session `iss00334-s016-two-p1`で2件だけを具体化した。model evidenceは`requested=Pro`／`resolved=Pro`／`verified=yes`。GitHub connectorはexact current branch／pushed base `be0c84a6ec3d6404700c98aaa6e81d8cceab5ea2`を確認し、default branchを参照していない。正式artifactは`artifacts/20260730t213150z-pr-351-s016-two-p1-chatgpt-concretization.md`である。
- S016 P1-Aはproduction behaviorを変更せず、exchange-back直前の二度目のreplacementを注入するfull-transaction characterizationを追加した。canonical B、private workspace C、backup A、operation replacement digestを保持し、`recovery_required/restore_mismatch`、local／remote HEAD不変、commit／publication evidence 0を確認した。
- S016 P1-Bはoperation authorityだけからcanonical三文書、companion、decision artifactのexpected blob OID／absenceを導出する。`git add`後のimmutable `write-tree`に対して一回のclosed `git ls-tree -r -z` parseでfive target entriesを照合し、`after_index_stage`／STAGED／commitより前にmismatchを`planning_commit_failed`へ接続する。
- Redはfive target atomic replacementが修正前`ready/adoption_published`へ到達する5 failuresと、index-only poisonが修正前local commit後`recovery_required/post_commit_workspace_changed`になる1 failureを確認した。GreenはS016 focused `7 passed`、Apply unit `79 passed`、明示full-regression Apply integration `96 passed`、Ruff check／format、provider／dogfood byte parity、`git diff --check`がPASSした。
- S016はOracle configuration behaviorを変更していない。local Oracle native configを尊重し、formal必須値だけをdirect argvへ渡すHuman boundaryは維持する。
- S016後のfresh Spec／Code／QA reviewはCode／QAがP0／P1 0でPASSした一方、Specがverified `local_tree`後からordinary `git commit`までのreal-index TOCTOUをP1とした。push前tree checkだけではunauthorized local commit生成を防げず、stop-before-commit contractを満たさないため採用した。
- S017は同じChatGPT Blue conversationを指定`chatgpt-use` wrapperでfollow-upし、verified-tree-to-local-commit bindingだけを具体化した。GitHub connectorはexact current branch／base HEADを確認しdefault branchを使用していない。follow-upはmodel再選択を行わないためrun単体の`resolved`／`verified` evidenceはunavailableであり、初回S016 sessionのverified contextを継続した。正式artifactは`artifacts/20260730t220930z-pr-351-s017-verified-tree-commit-binding-chatgpt-concretization.md`である。
- S017はoperation-private indexでpre-install hooksを実行し、verified `local_tree`とexpected parentから`commit-tree`でcommit objectを生成する。tree、single parent、changed paths、operation trailerを再証明し、exact checked-out branch refへold-value CASでinstallする。generic Git validatorの`update-ref`禁止は緩和していない。
- commit hooksは`pre-commit`、`prepare-commit-msg`、`commit-msg`、CAS install後の`post-commit`を既存順序で各1回実行する。private index mutation、reject、operation trailer removalをinstall前に拒否し、`commit.gpgsign=true`は`commit-tree -S`へ反映する。
- S017 Redは`3 failed, 3 passed`。late real-index poisonは修正前unauthorized local commit生成後`restore_mismatch`、final-proof race checkpoint不在、private-index mutationの検出遅延を確認した。Greenはfocused `7 passed`、Apply unit `83 passed`、Apply full unit＋integration `186 passed`、Ruff check／format、scoped `git diff --check`がPASSした。
- S017はOracle configuration behaviorを変更していない。PATH-resolved local Oracleの通常native configを尊重し、formal必須値だけをdirect argvへ渡すHuman boundaryを維持する。
- S017後のfresh Spec／Code／QA reviewersはすべてP0／P1 0でPASSした。Main final verificationはordinary fast lane `1346 passed, 2202 skipped`、explicit Apply full regression `103 passed`、`make lint`（Ruff／format／mypy）、provider／dogfood Apply byte parity、validate `nodes=227`、`git diff --check`がPASSした。正式local closure evidenceは`artifacts/20260730t192855z-review-pr-351-s009-s015-local-closure-evidence.md`である。
- S009〜S017 closureはcommit `2ff5c4bda05d80d68f56510b56500c88a4ce3302`としてcurrent branchへpushし、clean worktree、local／remote parity `0/0`を確認した。
- exact pushed HEADへのfresh ChatGPT Pro defect-only reviewはsession `iss00334-s017-final-review-2ff5c4bd`、`requested=Pro`／`resolved=Pro`／`verified=yes`、default branch substitution 0である。verdictはP0 0／P1 3のFAILで、正式artifactは`artifacts/20260730t231321z-review-pr-351-s017-exact-head-chatgpt-fail.json`である。
- `FINAL-P1-001`はchecked-out branch identityがref installとresume／pushへCAS-boundされず、branch switch後にoperation branchへlocal commitをinstallしたままevidenceなしで停止し得る。`FINAL-P1-002`はoperation trailer proofがsubstringでnear-match／body-only／duplicateを許す。`FINAL-P1-003`はmutable `origin` aliasのretargetによりreviewed repository以外へpushして`ready`になり得る。3件ともcurrent authority contract内のunauthorized commit／push defectとして採用する。
- Red Team sessionはread-onlyのまま終了し、修正へ再利用しない。次の修正は別fresh Blue Team sessionでこの3 findingだけを具体化する。
- 残存gateはFINAL-P1-001〜003のbounded repair、fresh local Spec／Code／QA、repair commit／push、exact repaired HEADのfresh ChatGPT review、最終evidence publicationとfixed PR observationである。

## 2026-07-31 — S018 three-P1 Blue Team具体化

- fresh Blue Teamの初回session `iss00334-final-p1-blue`は6添付のready待機が5分でtimeoutした。Oracle metadataで`promptSubmitted=false`を確認してからのみ再試行し、ChatGPTへの重複送信はない。
- 添付をtask brief、正式Red JSON、provider Apply実装の3件へ縮小し、fresh session `iss00334-final-p1-blue-retry`を実行した。model evidenceは`requested=Pro`／`resolved=Pro`／`verified=yes`で、GitHub connectorからrepository `chemitaro/spec-dock`、current branch、exact HEAD `2ff5c4bda05d80d68f56510b56500c88a4ce3302`を確認し、default branchを参照していない。
- Blue TeamはFINAL-P1-001〜003だけを、atomic checked-out branch/ref binding、single exact Git trailer proof、`operation.repository`へbindしたimmutable publication endpointとして具体化した。新しいpublic status／reason／schema、Human binding変更、Candidate／canonical bytes変更、Oracle configuration変更、S014／S015 scope再開、P2／P3提案は含まない。
- 正式work packetは`artifacts/20260730t233742z-pr-351-s018-three-p1-chatgpt-concretization.md`へbyte-preservingで保存した。修正はprovider authorityとfocused testsへ限定し、dogfoodは実装後に機械投影する。

## 2026-07-31 — S018 three-P1 implementation

- `FINAL-P1-001`はcurrent branch refのold-value CASに、Git自身がprepared phase中に保持する`.git/HEAD.lock`、raw symbolic HEAD、exact prepared inventoryの検証を結合した。ローカルGit 2.54.0では`HEAD`の`symref-verify`とreferent branch updateを同一transactionへqueueするとmultiple-updateとして拒否されるため、Git所有lock下でchecked-out branch identityを固定する方式を採用した。
- foreign `.git/HEAD.lock`はtransaction開始前にfail closedし、prepared native `reference-transaction` hook内のbranch switchはGit lock conflictで拒否する。既存native hookはprepared／committed／abortedの各phaseで1回だけ委譲し、branch／HEAD／ref proofをresume、push直前、push後、publication記録前に再証明する。
- `FINAL-P1-002`は`git interpret-trailers --parse --no-divider`を用いる単一strict parserへ統一した。terminal trailer blockにcase-sensitive exact key／exact operation IDが1件だけ存在する場合のみ許可し、near-match key／value、duplicate、body-onlyをpre-install、immutable commit proof、resumeの全経路で拒否する。
- `FINAL-P1-003`はorigin fetch／push URLが同じnormalized GitHub repositoryであり`operation.repository`と一致することを一度だけ確認し、captured exact push endpointをprivate publication authorityとした。push、CAS failure observation、post-push parity、resumeはmutable `origin` aliasを使用せず、endpointをevidence／log／public resultへ永続化しない。
- S018実装前focused Redは`13 failed, 81 deselected`。最終GreenはApply unit＋application＋explicit full integration `256 passed`、ordinary fast lane `1362 passed, 2220 skipped`、`make lint`（Ruff check／425 files format／mypy 287 files）、validate `nodes=227`、`git diff --check`がPASSした。
- official `spec-dock update .`はdirty dogfood Applyと新規`git_cli`変更をbyte-identicalに投影しなかったため、provider正本2ファイルを対応するdogfood先へwhole-file copyした。Apply SHA-256は両側`8e1502a581a2a6de3337557e3161bd3295c1e5f998d22210781bafd013fda374`、Git CLIは両側`5ace7228bb2e422922f38a101d05b0d635c60e75a468b61c1a7c94bce97f38c3`である。
- Oracle configuration behaviorは変更していない。PATH-resolved local Oracleと通常native personal／project configの利用を許容し、SpecDockはそれらを上書き・無効化・隔離・配布・fallback契約化しない。workflow必須値だけを明示fieldからdirect argvへ渡すHuman boundaryを維持する。
- fresh local Spec／Code／QA reviewはすべてP0／P1 0でPASSした。QAはS018重点35件を再実行して全件成功した。正式closure evidenceは`artifacts/20260731t001100z-review-pr-351-s018-local-closure-pass.md`である。
- 残存gateはrepair commit／push、exact repaired HEADのfresh ChatGPT defect-only review、最終evidence publicationとfixed PR observationである。

## 2026-07-31 — S018 exact-head Red Team review

- S018 closureはcommit `e1ae20d96400520d5c80168d0d799b9109853dd9`としてpushし、local／remote parity `0/0`を確認した。
- fresh Red Team初回session `iss00334-s018-exact-review`はChatGPT conversation作成前にmanaged Chrome connectionが切断された。Oracle metadataで`promptSubmitted=false`を確認してからのみ、fresh session `iss00334-s018-exact-review-retry`へ同一入力を再送した。
- retry sessionは`requested=Pro`／`resolved=Pro`／`verified=yes`で、GitHub connectorからrepository、branch、exact HEAD `e1ae20d96400520d5c80168d0d799b9109853dd9`を確認し、default branchを参照していない。
- verdictはP0 0／P1 1のFAIL。strict trailer proofとimmutable publication endpointはclosedと判定したが、push／resume／ready gateの`_operation_branch_commit_is_proven()`がsymbolic HEAD、operation branch ref、resolved HEADを独立して読むため、最初の観測直後にsame-commit alternate branchへ切り替わるとtrueを返し得る。
- このfindingはoptional hardeningではなくunauthorized push／publication evidence／readyを許し得るcurrent authority contract違反として採用する。正式artifactは`artifacts/20260731t005600z-review-pr-351-s018-exact-head-chatgpt-fail.json`である。
- Red Team sessionはread-onlyのまま終了し、修正へ再利用しない。次の修正は別fresh Blue Team sessionでこの1件だけを具体化する。

## 2026-08-02 — S019 branch-proof repair

- S019 Blue Teamのfresh ChatGPT session `iss00334-s019-blue-pro-aug2e`は`requested=Pro`／`resolved=Pro`／`verified=yes`および`promptSubmitted=true`まで到達したが、約7分の生成後にmanaged Chromeの接続が切断され、実装work packetを取得できなかった。同一会話の再オープンはstalled statusのみを返した。
- 同じBlue Team会話で行ったrecovery follow-up `iss00334-s019-blue-pro-followup`は`prompt-commit-timeout`（`userMatched=false`／`hasNewTurn=false`／`resolved=(unavailable)`）となった。fresh Red/Blue roleを混在させず、ChatGPT outputは採用していない。wrapper/browserの問題と証跡を`artifacts/20260802t005500z-pr-351-s019-branch-proof-blue-chatgpt-recovery.md`に保存した。
- formal Red finding `FINAL-P1-001`と現行sourceに基づき、`.git/HEAD.lock`を`O_EXCL`で取得する`_OperationBranchLock`を追加した。symbolic HEAD、operation branch ref、resolved HEADのcoherent proofからCAS push、remote parity、publication evidence、terminal resultまで同一lockを保持し、foreign/replaced/disappeared lockはfail closedにした。
- `_operation_branch_commit_is_proven`と`_push_operation_commit_cas`は既存lockを受け渡し、resume publicationもbranch proof前からfinal evidence/resultまでlock下で実行する。既存のpublic status/reason/schemaとOracle configuration boundaryは変更していない。
- initial／resume／already-remote-parityの3つのintegration testで、symbolic HEAD観測直後の`git checkout`が非ゼロで拒否され、operation branchとpublicationの安全性が維持されることを確認した。
- verification: explicit Apply unit/application/integration `259 passed`; ordinary fast lane `1362 passed, 2223 skipped`; `make lint`（Ruff check/format, mypy）pass; `spec-dock validate` `nodes=227`; `git diff --check` pass; provider/dogfood `issue_planning_apply.py` byte-identical。
- 次のgateはこのrepairのcommit／push、exact repaired HEADに対するfresh ChatGPT複合Spec/Code/QA review、PR observationである。merge、auto-merge、branch削除、Issue close、issue finishは行わない。

## 2026-08-02 — S019 exact-head combined ChatGPT review FAIL

- fresh read-only combined review session `iss00334-s019-combined-review-aug2-luna` は `requested=Pro`／`resolved=Pro`／`verified=yes` で実行され、GitHub connectorで repository `chemitaro/spec-dock`、current branch `iss-00334-implement-chatgpt-issue-planning-workflow`、exact HEAD `caa419afac594d445030e5b28d4f599bbbdfd892` を確認した。default branch fallbackは0件で、PR #351のHEADとlocal／remote parity `0/0`も一致した。
- SPEC／CODE／QAの3 perspectiveを一つのプロンプトで分離して確認した結果、各視点が同一のP1を1件ずつ検出し、overall `FAIL`となった。正式read-only outputは`artifacts/20260802t034500z-pr-351-s019-combined-review-fail.md`で、SHA-256は`2d9db86cb4c7987aef3a9981e17739f3c24912aff7e02c036ef2405848b60287`である。Red Teamはpatch、replacement ZIP、repository modificationを行っていない。
- `SPEC-P1-001`／`CODE-P1-001`／`QA-P1-001`の共通findingは、`_OperationBranchLock`が`--git-path HEAD`のper-worktree `HEAD.lock`だけを保護し、shared `refs/heads/<operation.branch>`を別linked worktreeから`git update-ref`で変更できる点である。proof後のliteral commit push、final proof後のpublication／readyが、branch refの変更を検出せずcurrent authority contractに反する可能性がある。
- S019 integration testsは同一worktreeの`git checkout`拒否を検証しているが、別linked worktreeからshared operation branch refを変更するred pathを検証していない。これは任意の追加confidence testではなく、記録されたS019 closure claimを反証する直接のP1再現である。
- 本FAILはS019修正の最小範囲へ限定する。仕様／アーキテクチャの再設計、P2／P3、Oracle configuration boundary、Candidate／canonical bytes、public schemaは変更しない。次はfresh Blue Team ChatGPTでこのshared-ref binding P1だけを具体化し、そのbounded修正後に新HEADで再度fresh combined reviewを行う。

## 2026-08-02 — S020 shared operation branch ref Blue Team具体化

- fresh Blue Team session `iss00334-s020-shared-ref-blue-aug2` は`requested=Pro`／`resolved=Pro`／`verified=yes`で実行され、GitHub connectorで repository `chemitaro/spec-dock`、current branch、exact HEAD `b544392990ef405548c36106d51a1414dd1719ab`、PR #351を確認した。default branch fallbackは0件である。
- 正式work packetは`artifacts/20260802t061000z-pr-351-s020-shared-ref-blue-chatgpt-work-packet.md`にwhole-file copyで保存した。SHA-256は`c1b6be6fbe488a55a9d5fc8334d072f5993eaf901e69dbbbbe129594b1d1ea64`である。
- Blue TeamはP1-001だけを、既存のper-worktree `HEAD.lock`と、長寿命の`git update-ref --stdin` prepared transactionによるshared `refs/heads/<operation.branch>` lockの複合guardとして具体化した。guardはbranch refを`verify`し`prepare`したまま保持し、push、remote parity、publication evidence、`REMOTE_PARITY`、terminal resultまで保持する。別linked worktreeの`git update-ref`は同じGit管理lockを取得できず非ゼロで拒否される。
- `HEAD.lock`の既存ownership検証に加えて、prepared child processの生存、destination ref／expected commit binding、直前assert、abort／終了検証をfail closedで追加する。guard transactionはprivate empty `core.hooksPath`で実行し、既存の実commit install transactionとnative hook delegation contractを変更しない。Gitの推測したloose-ref lock pathやmanual `refs/heads/*.lock`は使用しない。
- Red-firstでは、initial push直前、resume retry push直前、already-remote parityのpublication／ready直前の3 checkpointで、第二linked worktreeから`git update-ref`を実行するintegration testを追加する。修正前はupdateが成功し得ること、修正後は非ゼロで拒否されlocal／remote／publication／readyが正当なcommitに束縛されることを確認する。prepared protocol失敗、preimage mismatch、abort失敗、wrong binding、native hook leakageもfocused unitでfail closedを確認する。
- Blue Teamは新public status／reason／schema、Candidate／canonical bytes、Human authorization、Oracle configuration、persistent registry、daemon、retry／fairness policy、S01〜S019再設計を明示的non-goalとした。Git protocolの実対応バージョン／ref backendは実装時に検証し、unsupported／unexpected protocolはsampling fallbackせずhard failureとする。

## 2026-08-02 — S020 shared-ref guard implementation

- provider authority `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py` の`_OperationBranchLock`を拡張し、`git update-ref --stdin`のprepared transactionを固定argvで起動した。`start: ok`／`prepare: ok`をselect付きで明示確認し、`verify refs/heads/<operation.branch> <local_commit>`が保持するGit管理のshared ref lockと、同transactionが生成したper-worktree `HEAD.lock`のinode／mode／ownerをguardへbindする。
- prepared transactionがchecked-out branchでは`HEAD.lock`も生成することをGit 2.54.0で確認したため、manual `HEAD.lock`を先に作成する競合方式は採用せず、Git transaction prepare後に既存`HEAD.lock`をread-onlyでcaptureする方式へ調整した。終了時はGit transactionのlockを維持したまま`HEAD.lock`をidentity検証してunlinkし、その後`abort`を送信する。foreign／disappeared／replaced lock、protocol acknowledgement failure、child exit、abort failureはfail closedする。
- `_require_operation_branch_lock`でdestination／expected commitへのbindingとguard実体を必須化し、arbitrary objectをbranch lockとして受け付けない。push直前にも`assert_held()`を実行し、初回publish／resume／already-remote parityのproof、push、remote parity、publication evidence、terminal resultまで同一guardを保持する。既存のpublic status／reason／schema、native commit-install hook、Oracle configuration boundaryは変更していない。
- provider実装を`spec-dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py`へwhole-file projectionし、両ファイルSHA-256は`4092503865826a250ed2daa6b6445920d98f39ffa0e05cdea27557cc64c5e0c8`で一致した。
- Red-first／Green testsとして、shared branch refのprepare mismatch cleanup、unbound lock rejection、initial proof直後、resume proof直後、already-remote publication直前の第二linked worktree `git update-ref`を追加した。mutationは全て非ゼロで拒否され、authorized commitのlocal／remote parityとreadyが維持される。
- S020 implementation verification: Apply unit／application／integration `264 passed`; `make lint`（Ruff check／format、mypy）pass。次はこの実装・証跡をcommit／pushし、新HEADでfresh exact-head combined ChatGPT reviewを行う。

## 2026-08-02 — S020 exact-head combined ChatGPT review FAIL

- fresh read-only combined review session `iss00334-s020-review-aug2b` は `requested=Pro`／`resolved=Pro`／`verified=yes` で実行された。GitHub connectorは repository `chemitaro/spec-dock`、required branch `iss-00334-implement-chatgpt-issue-planning-workflow`、exact HEAD `fec2e190cce8cc1823cd65dc83cca167f7c85c73`、PR #351を確認し、default branch fallbackは0件だった。初回foreground前の同内容送信は`incomplete-capture`でターン／タブ生成前に終了したため、同じpromptを再送せず、definitely-not-committedを確認後に`ORACLE_NO_DETACH=1`で一度だけ再送した。
- SPEC／CODE／QAを分離した一つのbounded promptで確認し、3視点が同一のP1を1件ずつ検出した。overallは`FAIL`。正式read-only outputは`artifacts/20260802t081500z-pr-351-s020-combined-review-fail.md`で、SHA-256は`cf6d96a02a9516133233dee889a4e8e1d9801d3007c14a34a307f84f8f560960`。Red Teamはpatch、replacement ZIP、repository modificationを行っていない。
- `SPEC-P1-001`／`CODE-P1-001`／`QA-P1-001`の共通findingは、`_acquire_operation_branch_lock()`の例外cleanupが、prepared transactionのlock ownershipをcaptureできなかった場合も`HEAD.lock`を無条件`unlink()`する点である。foreign `HEAD.lock`が先に存在しprepareが失敗する経路で、S020 guardが所有権を証明していない他Gitプロセスのlockを削除し得る。これは既存のfail-closed repository-integrity contractに反し、initial publicationとresume publication双方で到達可能なP1である。
- QAは既存のforeign-lock testがlocal commit-install transactionで停止し、S020 publication guardの部分取得cleanupへ到達しないこと、prepare-mismatch testもforeign lockを置かないため無条件unlinkを検出できないことを確認した。したがって記録済み`264 passed`だけではこのP1を閉じない。
- S020の共有ref設計自体、provider／dogfood parity、public schema、Oracle configuration boundary、S014／S015 scopeは変更しない。次はfresh Blue Team ChatGPTでこのforeign-lock ownership cleanup P1だけを具体化し、修正後に新HEADのfresh combined reviewを行う。merge、auto-merge、branch削除、Issue close、`issue finish`は行わない。

## 2026-08-02 — S020 foreign-lock cleanup Blue Team具体化

- 既存S020 Blue Team会話 `iss00334-s020-shared-ref-blue` の保存URLへのfollow-upは、OracleがChatGPTのChat／Work modeを`conversation-unresolved`として送信前に拒否した。`promptSubmitted=false`、新しいターン／レビュー結果は存在しない。保存済みURLを`--chatgpt-url`で再接続しても同じ送信前エラーとなったため、wrapper／ChatGPT UI境界の不具合として記録する。Red Team会話は再利用していない。
- 既存Blueのwork packet、S020 formal FAIL、現行Requirement／Design／Plan、provider実装、unit／integration testsを全て引き継いだ専用Blue Team session `iss00334-s020-blue-repair`を新設し、GitHub connectorで repository `chemitaro/spec-dock`、branch `iss-00334-implement-chatgpt-issue-planning-workflow`、exact HEAD `92e1c8d843c1e1a8f04916dfd694c6cb86967c5b`、PR #351を確認した。default branch fallbackは0件、`requested=Pro`／`resolved=Pro`／`verified=yes`である。
- 正式work packetは`artifacts/20260802t090000z-pr-351-s020-foreign-lock-blue-chatgpt-work-packet.md`にwhole-file copyで保存し、SHA-256は`d76c9feb304c25e102f404c01a09aa67a693d4e8bca652eb32b5f617e6b9ccb9`である。Blue TeamはP1-001だけを、ownership capture state machineとprotocol abort／ambiguous abandonmentの分離、abort成功後のcaptured-inode限定fallback cleanupとして具体化した。
- 必須Red/Greenは、foreign `HEAD.lock`をS020 guard acquisition前に置いたdirect／initial publication／resume publicationのinode・bytes・mode・owner preservation、abort前unlink禁止、replaced／disappeared lockのabandon without unlink、successful captured-inode teardown、既存3つのlinked-worktree shared-ref testsの維持である。shared-ref lock lifecycle、public status／reason／schema、Oracle configuration boundary、S001〜S019、S014／S015 scopeは変更しない。

## 2026-08-02 — S020 foreign-lock cleanup implementation

- `_OperationBranchLock`はdescriptorとpathnameの双方でregular／owner／mode／device／inodeを再証明してから操作するようにし、所有権が未捕捉・消失・置換・child終了の場合はnormal `abort`や`unlink`を行わず、prepared transactionをabandonしてfail closedする。
- normal teardownとpartial acquisition cleanupを、`abort`成功後にのみcaptured inode限定fallback cleanupを行う経路へ分離した。`HEAD.lock`がabsentならGit cleanupを受け入れ、別inode／metadata ambiguity／abort failureは現在のpathnameを保持して`PlanningApplyRestoreMismatch`とする。S020のshared ref transaction lifetimeとinitial／resume／already-remote publication scopeは変更していない。
- provider authorityをdogfood projectionへwhole-file copyし、両ファイルのSHA-256は`5ed97772258145150c1f2da5d3ee40c585195d70da3f8dfca949b634223a79db`で一致した。
- Red/Green testsを追加した。unitではabort-before-unlink、abort failure preservation、replaced／disappeared lock abandonmentを固定し、integrationではdirect guard acquisition、successful teardown、initial publication、resume publicationのforeign lock preservationとinode／bytes／mode／ownerを固定した。既存のlinked-worktree shared-ref 3テストも維持した。
- verification: new focused 8 tests `8 passed`; complete Apply unit／application／integration `272 passed`; ordinary `uv run pytest -q` `1367 passed, 2231 skipped`; `make lint`（Ruff check／format、mypy）pass; `spec-dock validate` `nodes=227`; `git diff --check` pass。Apply lane初回実行で既存branch-switch testが一時的に1件失敗したが、単独実行と再実行でpassし、最終laneは`272 passed`である。
- 次のgateはこの実装と証跡のcommit／push、修正後exact HEADに対するfresh Red Team combined ChatGPT review、PR observation／CI確認である。foreign-lock P1が解消されるまでmerge-readyとは扱わない。merge、auto-merge、branch削除、Issue close、`issue finish`は行わない。

## 2026-08-02 — S020 foreign-lock cleanup exact-head Red Team review FAIL

- fresh read-only combined review session `iss00334-s020-foreign-review` は `requested=Pro`／`resolved=Pro`／`verified=yes` で実行された。GitHub connectorは repository `chemitaro/spec-dock`、required branch `iss-00334-implement-chatgpt-issue-planning-workflow`、exact HEAD `4abb7f8296d4dab69cd393a107ff49bd7fc77370`、PR #351を確認し、default branch fallbackは0件だった。レビューは指定したexact feature branch／HEADのみを対象とし、Red Teamはpatch、replacement ZIP、repository modificationを行っていない。
- SPEC／CODE／QAを分離した同一のP0／P1限定promptで確認した結果、3視点が同一のP1を1件ずつ検出し、overall `FAIL`となった。正式read-only outputは`artifacts/20260801t185408z-pr-351-s020-mode-compatibility-combined-review-fail.md`で、SHA-256は`4789d5343ded0aa9ed849d13d99739745f9fae532239d7b62941918be552850b`である。
- `SPEC-P1-001`／`CODE-P1-001`／`QA-P1-001`の共通findingは、`_OperationBranchLock`がGit生成lockのpermission bitsを厳密に`0600`へ限定している点である。Gitのref lock作成は`0666`にumaskを適用するため、一般的なumask `0022`では正当な`HEAD.lock`が`0644`となり、guard取得が失敗する。prepared transactionをabortせずabandonする経路では`HEAD.lock`とshared ref lockが残り得るため、通常の公開処理を阻害し、手動復旧を要求する。
- Red Teamはこのfindingを、S020の既存foreign／replaced／disappeared lock ownership修正とは独立した、通常Git環境互換性とpublication availabilityに関する具体的P1として判定した。public status／reason／schema、shared-ref guardの目的、Oracle configuration boundary、S001〜S019、Candidate／canonical bytesは変更対象に含めていない。次はfresh Blue Team ChatGPTでこのlock-mode compatibility P1だけを具体化し、修正後の新HEADで再度fresh combined reviewを行う。merge、auto-merge、branch削除、Issue close、`issue finish`は行わない。

## 2026-08-02 — S020 lock-mode compatibility Blue Team具体化

- 既存の専用Blue Team会話 `iss00334-s020-blue-repair` へのfollow-upは、送信前にOracleがChatGPTのChat／Work modeを検証できず拒否した（`promptSubmitted=false`、新しいターン／出力なし）。Red Team会話は再利用せず、wrapper／ChatGPT UI境界の問題として記録した。
- 同じS020の引き継ぎ情報（formal Red FAIL、前回Blue packet、canonical Requirement／Design／Plan、provider source、unit／integration tests）を添付したfresh Blue Team session `iss00334-s020-mode-blue`を開始し、GitHub connectorで repository `chemitaro/spec-dock`、branch `iss-00334-implement-chatgpt-issue-planning-workflow`、exact HEAD `c5439cdc139462c3c9dfa9730d3d688ee42e76d1`、PR #351を確認した。default branch fallbackは0件、`requested=Pro`／`resolved=Pro`／`verified=yes`である。
- 正式work packetは`artifacts/20260801t191908z-pr-351-s020-lock-mode-blue-chatgpt-work-packet.md`にwhole-file copyで保存し、SHA-256は`da2cbb0fb46fd8ddc8a848c8039c61fad83c782819497055094ca28361dd8cbb`である。
- Blue TeamはP1一件だけを、Gitの`0666` requestとumaskで得られたlock modeを取得時にcaptureし、descriptor／pathnameのmodeが一致し、Git互換範囲（execute／special bitなし）であることを確認した上で、後続の所有権検証・fallback cleanupではcapture済みmodeとの完全一致を要求する設計へ具体化した。`0600`を固定せず、`0022→0644`と`0077→0600`をreal Gitで確認する。production umaskの変更・chmod・読み取り、public schema、shared-ref guard lifetime、foreign／replaced／disappeared／wrong-owner／non-regularのfail-closed契約は変更しない。
- 必須Red／Greenは、real Git lock mode characterization（通常CIで実行）、initial／resume retry-push／already-remote publicationのumask `0022`成功、mode change preservation、foreign／replaced／disappeared／wrong-owner／non-regular preservation、既存linked-worktree shared-ref tests、provider／dogfood byte parityである。次はこのwork packetを実装し、provider sourceからdogfoodへwhole-file projectionした上で、focused／complete Apply／ordinary tests、lint、validate、diff checkを実行し、commit／push後に新HEADのfresh Red Team combined reviewを行う。

## 2026-08-02 — S020 lock-mode compatibility implementation

- `_OperationBranchLock`の固定`0600`判定を、Gitの`0666` requestとumaskから得られるmode（execute／special bitなし）を取得時にcaptureし、descriptor／pathnameのmode一致・owner・regular・device／inode・child生存を維持する契約へ限定的に変更した。capture後はmodeを含む全metadataの完全一致を要求し、mode変更・置換・消失・abort失敗は既存のfail-closed保持経路を通る。production umaskの変更・chmod・public schema・shared-ref transaction lifetimeは変更していない。
- provider authority `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py`をdogfood `spec-dock/scripts/spec_dock_runtime/infra/issue_planning_apply.py`へwhole-file projectionし、両ファイルSHA-256は`70b76d147e1b7d2a14aee378e83c4616add6d9a2babca1e1262bc022cc5077cf`で一致した。
- Unitではreal Gitのchild umask `0022→0644`／`0077→0600` capture、mode `0600/0644`のteardown／abort failure、capture前後のmode変更保持を追加した。Integrationではprepared lock teardown、initial publication、resume retry-push、already-remote parityをumask `0022`で実行し、`ready/adoption_published`、`REMOTE_PARITY`、local／remote parity、lock absenceを固定した。既存foreign／replaced／disappearedおよびlinked-worktree shared-ref testsも維持した。
- Verification: focused lock／publication tests `13 passed`（mode修正後の追加・既存境界）、complete Apply unit／application／integration `282 passed in 77.76s`、ordinary `uv run pytest -q` `1373 passed, 2235 skipped in 12.82s`、`make lint`（Ruff check／format、mypy 287 files）pass、`spec-dock validate` `nodes=227`、`git diff --check` pass。次のgateはこのimplementation commit／push後の新HEAD fresh Red Team combined reviewであり、P0／P1が0件になるまでmerge-readyとは扱わない。

## 2026-08-02 — S020 lock-mode compatibility exact-head Red Team review PASS

- fresh read-only combined review session `iss00334-s020-mode-red` は `requested=Pro`／`resolved=Pro`／`verified=yes` で実行された。GitHub connectorは repository `chemitaro/spec-dock`、required branch `iss-00334-implement-chatgpt-issue-planning-workflow`、exact HEAD `42e2af3fd89ac956541ede4e65992684ac86eb69`、PR #351を確認し、default branch fallbackは0件だった。branchとPR head SHAの一致も確認され、Red Teamはpatch、replacement ZIP、repository modificationを行っていない。
- SPEC／CODE／QAを分離した同一のP0／P1限定promptで確認し、各視点のP0=0／P1=0、overall `PASS`となった。正式read-only outputは`artifacts/20260801t195145z-pr-351-s020-lock-mode-combined-review-pass.md`で、SHA-256は`4468fa1bfac25b6d79030580e78589606d0f522d2341be7246301a80bcf37f2f`である。
- Red Teamは前回P1（Gitの`0666` request＋umaskで生成される`0644` `HEAD.lock`を固定`0600`判定で拒否する互換性・可用性欠陥）が、実mode capture・完全一致検証とnormal／full regression coverageで閉じたと判定した。shared-ref prepared transaction lifetime、foreign／replaced／disappeared fail-closed、public status／reason／schema、Oracle boundary、provider／dogfood parityに新たなP0／P1はない。
- exact-head review後の残存gateは、formal PASS artifact／reportのevidence commit、GitHub PR observation、CIの最新commit成功、merge-ready状態の再確認である。merge、auto-merge、branch削除、Issue close、`issue finish`は行わない。

## 2026-08-02 — PR observation current blockers and Blue Team repair packet

- PR #351をhead `97798b93bf8bf0e1b6793f3567fc1976ef2556ac`に固定して、GitHub Actionsの観測を実施した。Actions checksは成功したが、current triggerでP0×1／P1×3のレビューコメントが検出され、状態は`human_gate`となった。観測証跡は`/private/tmp/iss-00334-pr351-observation/result.json`に保存されている。既存のcarryover unresolved threadとは分離し、今回のcurrent findingsだけを修正対象とする。
- current findingsは、(1) apply時の非GitHub origin resolver例外に含まれるURL／資格情報の漏えい（P0）、(2)深いJSONの`RecursionError`が構造化`rejected`へ正規化されない（P1）、(3)review staging directoryを閉じた後にpathname renameするidentity TOCTOU（P1）、(4)Create／Review／mechanical Reviseのpublication完了後にsource guardがない（P1）である。レビューは設計の再構築やP2／P3提案ではなく、この4件に限定する。
- 最初のBlue送信はdetached workerがcapture前に終了する`incomplete-capture`となった。prompt送信・ターン生成を確認した上で、重複送信せず、fresh session `iss-00334-pr351-blue-repair`を`ORACLE_NO_DETACH=1`／`requested=Pro`でforeground再送した。GitHub connectorでrepository、current branch、exact HEAD、PR #351を確認し、default branch fallbackは0件だった。ChatGPT-Use側の回答は実装・patch・ZIP生成を行わないread-only work packetとして採用した。
- 正式Blue Team work packetは`artifacts/20260802t202000z-pr-351-observation-blue-chatgpt-work-packet.md`（SHA-256: `2012c19246b7329cf4f52ab06f6b4a1040bc9f6ad31d7248e3e7e94f9b15e4d8`）である。最小修正方針は、apply resolverをcontent-freeな`blocked/github_upstream_required`へ正規化し、共有JSON parserで`RecursionError`を`ValueError("invalid JSON")`へ変換し、publication portへ必須のcompletion guardを追加し、所有権を証明できる新規publicationだけをstale時に削除することである。Review stagingはdescriptor／device・inode／子ファイル内容を保持して検証し、置換された未知エントリは削除しない。provider／dogfood whole-file parity、既存collision／output guard／public schema、Git-bound exact branch/HEADは維持する。
- 次の作業はこの4件だけを実装し、providerからdogfoodへwhole-file projectionし、focused／complete Apply／ordinary tests、lint、validate、diff checkを実行する。実装commit／push後は、新HEADのfresh Red Team（read-only、P0／P1 concrete defects only）を行い、PASS後にPR observationを再実行する。merge、auto-merge、branch削除、Issue close、`issue finish`は行わない。

## 2026-08-02 — PR observation current blockers implementation

- applyのorigin解決で`RuntimeError`または解決不能値を受けた場合、例外本文やorigin URLを返さず、`blocked/github_upstream_required`へ正規化した。GitHub originと一致しない解決結果は従来どおり`stale/apply_target_changed`として扱う。
- 共通のstrict JSON object parserで`RecursionError`を`ValueError("invalid JSON")`へ正規化し、深い入力が構造化された計画拒否経路を迂回しないようにした。
- Candidate／Review publication portに必須のcompletion guardを追加し、最終的なatomic publicationと内容検証の後にsource freshnessを一度だけ再確認する。guard例外はcontent-freeなpublication failureへ、falseはsource-staleへ写像する。
- Candidate publicationのstale cleanupは、今回のpublicationで所有権を証明できる正確なファイルだけを削除し、同名置換や未知のentryを保持する。Review stagingは開いたdirectory descriptor、device／inode、子ファイルidentity、期待bytesをrename前後で検証し、置換されたディレクトリ・子ファイルを削除しない。
- provider authorityの5ファイルをdogfoodへwhole-file projectionし、provider／dogfoodのbyte parityを確認した。既存のpublic status／reason／schema、Candidate／canonical bytes、Git-bound branch／HEAD契約は変更していない。
- 追加・更新テストはapply origin情報秘匿、JSON recursion正規化、Candidate／Review publication guard、staging identity／cleanup、source drift mappingを対象とした。検証結果は、通常テスト`1381 passed, 2235 skipped`、`make lint` pass、`spec-dock validate` `nodes=227`、`git diff --check` passである。
- 次のgateはこの実装をcommit／pushした後の新HEADに対するfresh Red Team（read-only、P0／P1の具体的欠陥のみ）とPR observationである。Red TeamがPASSするまでmerge-readyとは扱わない。merge、auto-merge、branch削除、Issue close、`issue finish`は行わない。

## 2026-08-02 — PR observation blocker repair fresh Red Team FAIL

- fresh read-only Red Team session `iss-00334-pr351-red-20260802` は、`requested=Pro`／`resolved=Pro`／`verified=yes`で実行された。GitHub connectorで repository `chemitaro/spec-dock`、required branch `iss-00334-implement-chatgpt-issue-planning-workflow`、PR #351、exact source HEAD `d3c72b6b58f301b5609566d7cdb9e94f4d08aa2c`を確認し、repository access／head matchはPASS、default branch fallbackは0件だった。
- SPEC／CODE／QAを分離したP0／P1限定レビューで、apply origin情報秘匿、深いJSONの`RecursionError`正規化、publication completion guard、provider／dogfood parityはP0／P1なしと判定された。一方、Review cleanupのP1 `REVIEW-CLEANUP-OWNERSHIP-TOCTOU`が1件検出され、overallは`FAIL`となった。
- 指摘は、`_remove_evidence_directory_at()`がcaptured Review directoryと子identityを検証した後、quarantineへ隔離せず元pathnameの`rmdir`を行うため、最終削除直前に同名replacement directoryへ差し替えられた場合に未知replacementを削除し、owned directoryのcleanup成功を誤って返し得る点である。Red Teamは、identity-checked quarantineへのatomic移動、移動後identityの再検証、captured child／directoryだけの削除、race回帰テストを要求した。これは既存設計のcleanup ownership契約に限定したP1であり、アーキテクチャ再設計やP2／P3提案ではない。
- 正式read-only transcriptは`artifacts/20260802t222000z-pr-351-red-combined-review-fail.md`にwhole-file copyで保存した。SHA-256は`0be78b5aa436cdc9565270c75ed502667ae50b523e2dc002c0e0786f58159a60`である。Red Teamはrepository、Candidate、ZIP、artifactを変更していない。
- 次はこのP1だけを対象に、既存Red Teamスレッドを再利用しないfresh Blue Team ChatGPTでrepair packetを作成し、その後provider／dogfood修正、deterministic regression test、検証、commit／push、新HEAD fresh Red Teamを繰り返す。P0／P1が0件になるまでmerge-readyとは扱わない。merge、auto-merge、branch削除、Issue close、`issue finish`は行わない。

## 2026-08-02 — Review cleanup ownership Blue Team repair packet

- fresh Blue Team session `iss-00334-pr351-blue-cleanup` は、`requested=Pro`／`resolved=Pro`／`verified=yes`で実行され、GitHub connectorで repository `chemitaro/spec-dock`、required branch、PR #351、exact source HEAD `d3c72b6b58f301b5609566d7cdb9e94f4d08aa2c`を確認した。default branch fallbackは0件で、provider／dogfoodの対象review module blobも同一だった。
- 正式work packetは`artifacts/20260802t224000z-pr-351-review-cleanup-blue-chatgpt-work-packet.md`にwhole-file copyで保存した。SHA-256は`e6314daddbafc746f7f298dcdc957c92e087828370b4d3f54e01f87577d0d302`である。Blue TeamはP1 `REVIEW-CLEANUP-OWNERSHIP-TOCTOU`だけを対象とし、repository、artifact、patch、ZIPを変更していない。
- packetは、captured Review directoryを親descriptor相対のprivate quarantine nameへno-replace atomic moveし、移動後directory／child identityを再検証してからcaptured childだけを削除し、quarantine nameだけを`rmdir`するstate machineを指定した。元のpublic pathnameへの`rmdir`、arbitrary inventory削除、unknown replacementの削除、曖昧なcleanupを`ReviewSourceStale`として扱うことは禁止する。
- cleanup ambiguityは既存のcontent-free `blocked/review_publication_failed`、raceなしのowned cleanupだけが`stale/review_target_changed`となるよう、既存application mappingを維持する。explicit cleanupと`finally` cleanupの二重destructive attemptを避けるprivate stateも要求した。public schema、publication guard、Candidate／canonical bytes、Oracle／Git-bound boundary、provider-first projection、成功時publicationは変更しない。
- 必須テストは、identity検証直後・final cleanup直前の元名replacementをdeterministically注入し、guard-falseとguard-exceptionの双方でreplacementとcaptured owned directoryを保持し、generic publication failureへ閉じること、競合なしではquarantine cleanup後にstaleが維持されること、applicationの`OSError`／`PlanningPublicationSourceStale` mappingを固定することである。次はこのpacketだけを実装し、providerからdogfoodへwhole-file projectionしたうえで検証・commit／pushし、新HEADのfresh Red Teamへ渡す。

## 2026-08-02 — Review cleanup ownership implementation

- `issue_planning_review.py`のcleanupをquarantine-firstへ変更した。captured Review directoryを親descriptor相対のprivate no-replace nameへatomic moveし、move後のdirectory／child identityとexact inventoryを再検証してからcaptured childだけをunlinkし、quarantine nameだけを`rmdir`する。元のpublic pathnameをcleanup対象として再利用しないため、元名へ差し替えられた未知replacementを削除しない。
- publication failure／source-staleのcleanup状態を`cleanup_attempted`／`cleanup_proven`で保持し、explicit guard-falseと`finally`のdestructive cleanupを二重実行しない。owned cleanupを証明できた場合だけ`ReviewSourceStale`を維持し、publication後の曖昧なcleanupはcontent-free `OSError`として既存applicationの`blocked/review_publication_failed` mappingへ閉じる。publication前の既存staging identity rejectionは従来のValueError契約を維持した。
- Linux `renameat2(RENAME_NOREPLACE)`／Darwin `renameatx_np(RENAME_EXCL)`のprimitiveをprivate helperへ共通化し、provider authorityをdogfoodへwhole-file projectionした。provider／dogfoodの対象runtimeファイルはbyte parityを確認した。public status／reason／schema、Candidate／canonical bytes、Oracle／Git-bound boundary、成功時Review publicationは変更していない。
- deterministic infra testsを追加し、guard-false／guard-exceptionのcleanup中にquarantine nameをunknown replacementへ差し替えてもreplacementとdisplaced owned directoryを保持し、`ReviewSourceStale`を返さずgeneric `OSError`へ閉じることを確認した。既存のstaging／child／output identity testsも維持した。
- verification: review/application focused `83 passed`、関連domain／application／candidate／review／integration lane `393 passed, 1 skipped`、ordinary `uv run pytest -q` `1383 passed, 2235 skipped`、`make lint`（Ruff check／format、mypy 287 files）pass、`spec-dock validate` `nodes=227`、`git diff --check` pass、provider／dogfood parity pass。次はこの修正と正式証跡をcommit／pushし、新HEADのfresh Red TeamでP0／P1 concrete defects onlyを再確認する。PASSまでmerge-readyとは扱わない。merge、auto-merge、branch削除、Issue close、`issue finish`は行わない。

## 2026-08-02 — Quarantine destructive-operation Blue Team repair packet

- fresh Blue Team session `iss-00334-pr351-blue-destructiv` は、`requested=Pro`／`resolved=Pro`／`verified=yes`で実行され、GitHub connectorで repository `chemitaro/spec-dock`、required branch、PR #351、exact source HEAD `7ed51a133ab551ed22fd41c5856315256fcaace2`を確認した。default branch fallbackは0件、provider／dogfood blobも一致していた。
- 正式work packetは`artifacts/20260803t001000z-pr-351-quarantine-destructive-blue-chatgpt-work-packet.md`にwhole-file copyで保存した。SHA-256は`71d701c212470ddf23076213f770ff45d29982172271b89e4ece890083c3985c`である。Blue Teamは`REVIEW-QUARANTINE-DESTRUCTIVE-TOCTOU`の1件だけを対象にし、repository、artifact、patch、ZIPを変更していない。
- packetは、no-replace renameをcapture primitiveに限定し、child `stat`→`unlink`およびdirectory `stat`→`rmdir`の単純なcheck-then-deleteを禁止した。identity-conditional remove primitiveまたはuncooperative writerを排除する強制的namespace exclusivityを独立証明できないplatform／filesystemでは、entryを保持して固定`OSError("review publication failed")`へ閉じ、`ReviewSourceStale`／`review_completed`を返さない方針を指定した。
- Linux標準`unlinkat`はparent descriptorとpathnameを受ける削除APIで、expected inodeを条件にした削除契約ではない。Darwinの現行no-replace rename primitiveも同じくdelete proofではないため、unsafeなstat＋unlink／rmdir sequenceで互換性を優先せず、conditional-remove capabilityが確認できるまでfail closedとする。public status／reason／schema、ReviewSourceStale型・application mapping、成功時publication、Candidate／canonical bytes、Oracle／Git-bound boundaryは変更しない。
- 必須テストは、child post-identity replacementとempty-directory post-identity replacementをguard-false／guard-exceptionで注入し、replacement inode／bytes、captured evidence、未処理childを保持し、cleanup successとstructured staleを成立させないこと、さらにapplicationのambiguity／proven stale mappingを固定することである。次はこの方針を実装し、provider→dogfood projection、検証、commit／push、新HEAD fresh Red Teamを行う。standard capabilityがない状態でのnormal guard-falseは`blocked/review_publication_failed`となるため、この境界がcanonical contractと衝突する場合は仕様amendmentが必要になる。

## 2026-08-03 — Quarantine destructive-operation fail-closed implementation

- `_remove_evidence_directory_at()`から、identity確認後に`os.unlink`／`os.rmdir`を実行する全経路を削除した。POSIX pathname removalにはexpected device／inodeを条件にしたatomic delete契約がないため、条件付き削除を証明できない現行platformでは`False`を返し、公開済みReview evidenceを保持したままcontent-free `OSError("review publication failed")`へ閉じる。これにより、source guard false／例外のいずれも`ReviewSourceStale`や`review_completed`を誤って返さない。
- provider authority `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_review.py`をdogfood `spec-dock/scripts/spec_dock_runtime/infra/issue_planning_review.py`へwhole-file projectionした。両ファイルのSHA-256一致を確認し、成功時のno-replace publication、Candidate／canonical bytes、public status／reason／schema、Oracle／Git-bound boundaryは変更していない。
- infra回帰テストはguard false／guard exceptionと、child／empty-directory destructive operation（`unlink`／`rmdir`）の全組合せで、破壊的操作が呼ばれず、sentinel・公開済みReview result・summaryが保持され、例外本文が漏れないことを固定した。既存のstaging／output identity testsは、曖昧なcleanup時に成果物を保持する期待へ更新した。
- focused review infraは`15 passed`。次は関連complete／ordinary pytest、`make lint`、`spec-dock validate`、`git diff --check`、provider／dogfood parityを実行し、commit／push後に新HEADのfresh Red Team（P0／P1 concrete defects only）を行う。条件付き削除primitiveを導入して`ReviewSourceStale`を復活させる変更は、別の仕様amendmentとfresh reviewが必要なため本Issueでは行わない。
- 実装後の検証は、ordinary `uv run pytest -q` が`1384 passed, 2235 skipped`、`make lint`（Ruff check／format、mypy 287 files）pass、`spec-dock validate` `nodes=227`、`git diff --check` pass、provider／dogfood parity passとなった。full-regression laneは今回未実施であり、既存のpost-merge／manual gateに委ねる。

## 2026-08-03 — Quarantine destructive-operation fail-closed exact-head Red Team review PASS

- fresh read-only Red Team session `iss-00334-pr351-red-failclosed-2` は、`requested=Pro`／`resolved=Pro`／`status=already-selected`／`verified=yes`で実行された。GitHub connectorで repository `chemitaro/spec-dock`、required branch `iss-00334-implement-chatgpt-issue-planning-workflow`、PR #351、exact source HEAD `1fba52b2357931a20b5ef68bf6e40bb53dbd243a`を確認し、branch HEADとPR head SHAが一致、default-branch fallbackは未使用だった。
- Red Teamはprovider review module、dogfood projection、application mapping、focused tests、Issue canonical三文書、前回Red FAIL、Blue repair packet、reportを確認した。`_remove_evidence_directory_at()`に破壊的`unlink`／`rmdir`経路がなく、guard trueの成功publication、guard false／exceptionのcontent-free blocked mapping、sentinel／Review evidence保持、collision／output identity guardが成立すると判定した。
- P0=0、P1=0、overall `PASS`。前回`REVIEW-QUARANTINE-DESTRUCTIVE-TOCTOU`は、曖昧なcleanupを`ReviewSourceStale`へ昇格させず、`blocked/review_publication_failed`へfail closedする実装で解消された。Red Teamはpatch、replacement ZIP、repository、PR、artifactを変更していない。
- 正式read-only成果物は`artifacts/20260803t012000z-pr-351-red-failclosed-combined-review-pass.md`で、SHA-256は`e1eef986b0c9cc268b7f9f85876a476ccfe2cc1f870e423b30c923edefa344e8`である。次のgateはこのPASS証跡のcommit／push、PR #351のcurrent-head observation／CI確認、merge-ready状態の再確認である。merge、auto-merge、branch削除、Issue close、`issue finish`は行わない。

## 2026-08-03 — PR observation current-head P1 and Blue Team concretization

- PR #351のcurrent HEAD `bc7b160b0a710bf799214d0cc5f8d0a34e18672b`に対する`wait_pr_observation.sh`を、正しいexact SHAで`post-once`実行した。Actions workflow runsは3件すべてsuccessだったが、current trigger boundaryのCodex reviewはP1 `planning-source-publication-toctou`を1件選択し、`normalized_status=human_gate`となった。観測証跡は`/private/tmp/iss-00334-pr351-observation-final-correct/result.json`に保存されている。carryover unresolved thread 8件は今回のcurrent findingとは分離され、今回の修正対象には含めない。
- current P1は`_review_publication_is_current()`と`_revision_publication_is_current()`がsource evidenceを先に確認し、Candidate loader後はCandidate比較だけを返す順序により、loader中のcanonical source mutationを見逃し得る点である。これはcleanup修正とは独立した、publication前source／Candidate一致保証の具体的なP1である。
- 既存Blue Team専用スレッド`iss-00334-pr351-blue-destructiv`を継続し、chain `iss-00334-pr351-blue-destructiv -> required-repository-connector-context-github-27`でexact repository／branch／HEADを確認した。Blue TeamはP1を有効と判定し、Review／semantic revisionの双方でCandidate loader→identity／ZIP bytes比較→最終source preflightの順に並べ替える最小修正と、loader中source mutation／no-drift positiveの決定的テストを指定した。provider application file、application unit test、provider後dogfood projection以外は変更対象にしない。
- 正式Blue Team work packetは`artifacts/20260803t025000z-pr-351-source-publication-toctou-blue-work-packet.md`で、SHA-256は`0efb5127c207c0e46b36cdbd60ea6532833795580e7d6a7a3ad9a9d7b16b293e`である。follow-upのChatGPT-Use model evidenceは`requested=Pro`／`resolved=unavailable`／`verified=no`となったため、これはwrapperのfollow-upモデル証跡不具合として記録し、packetの内容はGitHub exact source確認済みadvisoryとして扱う。Blue Teamはpatch、ZIP、repository、PRを変更していない。
- 次はこのP1だけを実装し、provider→dogfood projection、loader後source recheckのdeterministic tests、verification、commit／push、新HEAD fresh Red Teamを行う。cleanup修正、public status／reason／schema、Oracle boundary、canonical三文書は再設計しない。merge、auto-merge、branch削除、Issue close、`issue finish`は行わない。

## 2026-08-03 — Planning source publication TOCTOU implementation

- `_review_publication_is_current()`と`_revision_publication_is_current()`を、Candidate／current Candidateを先にloaderで取得し、identityとexact ZIP bytesを比較した後、最後に`_source_evidence_is_current()`を実行する順序へ変更した。loader中のcanonical source mutationを最終source preflightで検出し、guard false／stale mappingへ閉じる。Candidate equality、public status／reason／schema、publisher interface、cleanup、Oracle boundaryは変更していない。
- provider authority `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`をdogfood `spec-dock/scripts/spec_dock_runtime/application/issue_planning.py`へwhole-file projectionした。provider／dogfood application blob parityを確認した。Testsは`tests/unit/application/test_issue_planning.py`だけに追加し、Review／semantic revisionのloader中source mutation negativeとno-drift positiveをparameterizedで固定した。
- 回帰テストはCandidate loader→source preflightの順序をイベント列で検証する。negativeではsource manifestをloader中に変更し、guard false／publication 0を確認する。positiveではsource不変でguard trueを確認する。旧orderingではnegativeがsource preflight→loaderとなり、検出不能になるためテストが失敗する。
- 検証結果: focused publication-guard `5 passed, 68 deselected`、関連Issue Planning lane `576 passed, 161 skipped`、ordinary `uv run pytest -q` `1388 passed, 2235 skipped`、`make lint`（Ruff check／format、mypy 287 files）pass、`spec-dock validate` `nodes=227`、`git diff --check` pass、provider／dogfood parity pass。full-regression laneは未実施で、既存post-merge／manual gateに委ねる。
- 次のgateはこの修正とBlue packet/reportのcommit／push、current HEADへbindした新規Red Team combined review、PASS後のPR observationである。前回PASSは旧HEADに対する証跡であり、今回のsource-ordering修正を含む新HEADのfresh reviewを必須とする。merge、auto-merge、branch削除、Issue close、`issue finish`は行わない。

## 2026-08-03 — Planning source publication TOCTOU exact-head Red Team review PASS

- fresh read-only Red Team session `iss-00334-pr351-red-source-2` は、`requested=Pro`／`resolved=Pro`／`status=already-selected`／`verified=yes`で実行された。最初の同一目的セッション`iss-00334-pr351-red-source`は添付9件のupload timeoutで終了したが、診断時点で`promptSubmitted=false`、`conversationId=null`、leaseなしだったため、送信未コミットを確認した。添付を5件へ縮小したfresh sessionで再開し、ChatGPT回答を取得した。
- GitHub connectorは repository `chemitaro/spec-dock`、required branch `iss-00334-implement-chatgpt-issue-planning-workflow`、PR #351、exact source HEAD `dcf15fca0dcce74da0fc0f20855b5f125dc64564`を確認した。branch HEADとPR head SHAは一致し、default-branch fallbackは未使用だった。Red Teamはrepository、Candidate、ZIP、artifact、branch、PRを変更していない。
- provider／dogfoodの`application/issue_planning.py`、application tests、application mapping、canonical Issue requirement／design／plan、Blue packet、PR diff boundaryを確認し、Candidate loader→identity／exact ZIP bytes比較→最終source preflightの順序をReview／semantic revisionの双方で検証した。loader error／Candidate mismatch／source driftはfail closedし、public status／reason／schema、publisher interface、cleanup、Oracle boundaryは変更されていない。
- 新規parameterized testsはReview／semantic revisionの双方でloader中source mutationをfalseへ閉じ、no-drift positiveでtrueを返し、イベント順`candidate_loader`→`source_preflight`を固定している。provider／dogfood blob parity、exact-head CI checks、既存のpublication mappingも確認した。Red Teamはこの順序修正が前回P1 `planning-source-publication-toctou`を解消したと判定した。
- P0=0、P1=0、overall `PASS`。正式read-only成果物は`artifacts/20260803t040000z-pr-351-red-source-check-combined-review-pass.md`で、SHA-256は`2e9e83a5e12289961a9165a790b541f6151cafb2629b4cde19568333c273a769`である。次のgateはこのPASS証跡のcommit／push、PR #351のcurrent-head observation／CI確認、merge-ready状態の再確認である。merge、auto-merge、branch削除、Issue close、`issue finish`は行わない。

## 2026-08-03 — PR observation source-check current P1s and Blue Team repair batch

- PR #351のexact HEAD `c8e1ac2c75502d94d47d097d4a6ee8e63b698a9f`に対する`wait_pr_observation.sh`を`post-once`で実行した。Actions／Provider CIは3 runすべてsuccessだったが、current trigger boundaryは`human_gate`となり、P1を2件、P2を1件検出した。観測証跡は`artifacts/20260803t050000z-pr-351-observation-source-check-human-gate.json`で、SHA-256は`91027b0729b7856ede7ee99503f9e86f98cf00c3de34741f1bcb8c1d867da2f4`である。carryover unresolved thread 8件はcurrent findingsと分離した。
- current P1は、(A) `_review_publication_is_current()`／`_revision_publication_is_current()`がsource preflight後にCandidateを再確認しないため、preflight中のCandidate replacementを成功扱いし得ること、(B) `issue_planning_prompt.py`の`_safe_source_file()`後のpathname `read_bytes()`がancestor directory replacement symlinkをfollowしてrepository外bytesを添付し得ることである。なお、同一current reviewのreview-level P1として`import_file_artifact.py`の`_rollback_bound_rules_link()`がsame identity／ctime replacementをunlinkし得る指摘も取得したため、PR内の具体的P1として同じBlue batchへ引き継いだ。P2 `archive-stale-blocker-vocabulary`はnon-blockingで、今回の修正対象から除外する。
- 既存の専用Blue Teamスレッド`iss-00334-pr351-blue-destructiv`へfollow-upし、GitHub connectorでrepository、required branch、exact HEAD、PR #351を再確認した。Blue TeamはP1-A/B/CをすべてVALIDと判定し、P1-AはCandidate→source→Candidateのbounded revalidation、P1-Bはroot descriptor相対・`O_NOFOLLOW`による安全なdescriptor read（capability不在時fail closed）、P1-Cはportable ownership proofがない`rules.md` destructive unlinkを廃止してreplacementを保持するfail-closed修正を指定した。P2、lock／linearizability claim、prompt protocol、public schema、Oracle boundary、Apply／Review cleanup、canonical三文書は変更しない。
- 正式Blue Team work packetは`artifacts/20260803t060000z-pr-351-current-observation-blue-work-packet.md`で、SHA-256は`3e9c8daba45486b7cfd079529029035e1c4166db7b3092d58117bda79bfdf1cc`である。follow-upのwrapper model evidenceは`requested=Pro`／`resolved=unavailable`／`verified=no`だったため、前回同様ChatGPT-Use follow-upのモデル証跡不具合として記録する。ただしBlue Teamはexact GitHub source確認済みのadvisory packetのみを返し、repository、PR、artifact、ZIPを変更していない。
- 次はこのP1-A/B/Cだけをprovider sourceへ実装し、provider→dogfood whole-file projection、focused／complete／ordinary tests、lint、validate、diff check、parityを通過させる。commit／push後、新しいRed Team threadでfresh reviewを実施し、P0／P1が0件になるまでmerge-readyとは扱わない。merge、auto-merge、branch削除、Issue close、`issue finish`は行わない。

## 2026-08-03 — Current observation P1-A/B/C implementation

- P1-Aは`_candidate_view_is_current()`を追加し、Review／semantic revisionの双方をCandidate初回検証→source preflight→Candidate再検証の順序へ変更した。identityまたはexact ZIP bytesのdrift、loader例外、source preflight不一致はfalseへ閉じ、Candidate/sourceのlinearizable snapshotやlockは主張していない。identity drift／ZIP drift／no-driftをReview／revision双方でparameterized testに固定し、前回のloader中source mutation回帰も維持した。
- P1-Bは`issue_planning_prompt.py`のcanonical／relevant source readをrepository root descriptor相対 traversalへ変更した。`O_DIRECTORY`／`O_NOFOLLOW`／`O_CLOEXEC`／`O_NONBLOCK`と`dir_fd`でancestor／final fileをno-followでopenし、regular fileをdescriptorからbounded readする。capability不在・identity変化・outside/symlink pathはcontent-free `ValueError`へ閉じ、`Path.read_bytes()` fallbackは追加していない。ancestor swap fail-closedと通常のattachment name/order/bytes parityをテストした。
- P1-Cは`_rollback_bound_rules_link()`のcaptured tuple一致時でもownershipをatomicに証明できないため、`rules.md`をpathname unlinkしないfail-closed挙動へ変更した。既存のartifact setup failure／not committed envelope、replacement保持、normal positive、他のsafe rollback経路を維持し、same-identity replacementで`os.unlink`が呼ばれない回帰を追加した。P2 blocker vocabulary、Oracle、CLI、domain、publisher、Review cleanup、canonical三文書は変更していない。
- provider authorityの3ファイルをdogfoodへwhole-file projectionし、SHA-256は`issue_planning.py=af3a1c3b597729572a5d45c6de44203554d3c3074c4880b6327b1b0c4165b47b`、`issue_planning_prompt.py=2e3bb3cae4274d6df1482a1d413916d4cdcacb68da6c9ad2ffe2525319619759`、`import_file_artifact.py=824f4f664fe410fa3b3a06cadc831a4f149d3f673df050f6b9360189cd015211`でprovider／dogfood一致した。
- verification: focused `test_issue_planning.py` `79 passed`、`test_issue_planning_prompt.py` `25 passed`、`test_import_file_artifact.py` `31 passed`、application全体`243 passed`、関連lane `200 passed, 5 skipped`、ordinary `uv run pytest -q` `1397 passed, 2235 skipped`、`make lint`（Ruff check／format、mypy 287 files）pass、`spec-dock validate` `nodes=227`、`git diff --check` pass。full-regression laneは未実施で、既存post-merge／manual gateに委ねる。
- 次のgateはこのP1-A/B/C実装、Blue packet、観測JSON、report追記のcommit／push後に、新しいRed Team threadでfresh read-only reviewを実施することである。P0／P1=0になるまでmerge-readyとは扱わない。merge、auto-merge、branch削除、Issue close、`issue finish`は行わない。

## 2026-08-03 — P1 fail-closed residual hardening before fresh Red review

- P1-Aのsource preflight runnerが`RuntimeError`等を返す場合も、`_source_evidence_is_current()`が例外本文を公開せずfalseへ閉じることをReview／semantic revision双方のテストで固定した。既存のstatus／reason mappingは変更していない。
- P1-Bのrepository root `lstat()`とdirectory判定をdescriptor-openのfail-closed try boundaryへ含め、root消失・replacement等の`OSError`がpathname例外として漏れずcontent-free `ValueError`へ正規化されるようにした。provider／dogfood parityを維持した。
- residual hardening verification: application planning/prompt `106 passed`、`make lint` pass、`git diff --check` pass。これらの差分を含む最終commit／push後に、新しいRed Team threadでexact final HEADをfresh reviewする。

## 2026-08-03 — Final P1-A/B/C exact-head Red Team review PASS

- fresh read-only Red Team session `iss-00334-pr351-red-final` は、`requested=Pro`／`resolved=Pro`／`status=already-selected`／`verified=yes`で実行された。GitHub connectorで repository `chemitaro/spec-dock`、required branch `iss-00334-implement-chatgpt-issue-planning-workflow`、PR #351、exact source HEAD `cccd79263cfed9ba8f05c9861c1cf22d6f825fff`を確認し、branch／PR head SHA一致、default-branch fallback未使用を確認した。Red Teamはrepository、branch、PR、artifact、ZIP、source、testsを変更していない。
- P1-AはReview／semantic revisionの両方でCandidate初回検証→source preflight→Candidate再検証、identity／exact ZIP drift、loader／preflight exceptionのfail-closedを確認した。P1-Bはroot／ancestor descriptor-relative no-follow traversal、regular-file／bounded read、capability不在fail-closed、outside bytes不混入、attachment names/order/bytes維持を確認した。P1-Cはsame identity／ctime replacementを含むrules link rollbackでdestructive unlinkがなく、既存setup failure envelope、normal positive、他のsafe rollbackを維持することを確認した。
- provider／dogfood blob parity、focused tests、canonical契約、public mapping/schema、Oracle boundary、P2 blocker vocabularyの除外を確認し、P0=0、P1=0、overall `PASS`となった。正式read-only成果物は`artifacts/20260803t070000z-pr-351-red-final-p1-abc-review-pass.md`で、SHA-256は`9d440d47d29c5852921120fa8b5c65570bdc6dcf6ed4f85191c03f171a32743a`である。
- 次のgateはこのPASS証跡のcommit／push、PR #351のcurrent-head observation／CI確認、merge-ready状態の再確認である。merge、auto-merge、branch削除、Issue close、`issue finish`は行わない。

## 2026-08-03 — Final PR observation: CI success, no current P0/P1

- 最終commit `02ec9d569f6a41f15abfc52ea16fb050a3838333`をheadに固定して`wait_pr_observation.sh`を`post-once`実行した。GitHub Actions／Provider CIは3 runすべてsuccessで、head matchも確認された。
- current trigger boundaryのCodex reviewはP0=0、P1=0、P2=1（root test environmentでdescriptor capability testをroot実行時にskipする提案）だった。review本文はP2を明示的にnon-blockingとし、PR branchを更新する理由にしてはいけないと指定しているため、今回のP1修正へ再取り込みしない。
- スクリプトのtop-level normalized statusは、current P2 threadと既存carryover unresolved threadsが残るため`human_gate`となったが、blocker policyは`non_blocking_only`でP0／P1 blockerは0件である。観測証跡は`artifacts/20260803t080000z-pr-351-observation-final-p1-abc-human-gate.json`で、SHA-256は`4f6b83b0a2cba7ea8d975c8bec11de35ec081eeaf253441b618527f62d13284d`である。
- P2／carryoverの解消、merge、auto-merge、branch削除、Issue close、`issue finish`はこのIssueの完了条件や今回の修正範囲に含めず、HumanのPR判断へ委ねる。P1-A/B/Cについてはfresh Red PASS、CI success、provider／dogfood parity、ordinary／related testsがそろっている。
