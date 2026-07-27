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

本書は Issue の観測証跡台帳である。planned requirements と closure contract は `plan.md` が所有し、本書は採用判断、reviewer verdict、実行結果、closure delta、commit evidence を時系列で記録する。2026-07-27 時点では snapshot `546245f1072e6d7822fc7885eff814ac1eca1dc5` に対するfresh ChatGPT Red Team reviewのFAILを受け、同一の専用Blue Team authoring threadがP1-12〜P1-16とP2-03／P2-04のbounded correctionを作成し、MainがRequirement／Design／Planへ統合した。次のfresh ChatGPT Red Team reviewは未実施であり、製品実装は開始していない。

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

## 目的整合台帳（Objective Alignment Ledger / 必須）

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| canonical planning repair | ChatGPT-first Issue Planningのcreate→revise→review→Human Gate→apply→publication→readinessが `requirement.md` REQ-001〜REQ-024 と `design.md` public routeで一貫する | closed Review／Human JSON contract、archive safety、transaction recovery、source binding、secret preflight、owner-portion closureを `plan.md` のrequired rowsへ固定した | low。security／compliance controlsはprimary lifecycleを補強し、置換していない | Red FAILをBlue correctionへ反映済み。新規fresh Red re-reviewが次の正式判定 |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | parent Initiative／Epic、accepted ADR 20／22、current runtime、formal Red FAIL、Blue follow-upを照合 | なし。EC-005 exact statusとapproved／rejected lifecycleを確定した | P1-12／P1-14のRequirement owner部分を採用 | failed | yes | new snapshotのfresh canonical re-review |
| design | command parser、runbook transaction、GitHub preflight、archive review、formal Red FAIL、same-thread Blue follow-upを照合 | なし。public CLI identity、control schemas、negative decision、deterministic recoveryを確定した | P1-12〜P1-15、P2-04のDesign owner部分を採用 | failed | yes | new snapshotのfresh canonical re-review |
| plan | Closure Index、test ownership、archive controls、PA-NF、security、recovery、Blue follow-upを照合 | なし。owner portion、secret pre-invocation、control negative matrix、durable rejection、recovery lookupを確定した | P1-12〜P1-16、P2-03／P2-04のPlan owner部分を採用 | failed | yes | new snapshotのfresh canonical re-review |

`failed` は `artifacts/20260727t022302z-chatgpt-fresh-canonical-review-fail.md` の直近正式判定を表す。修正内容の自己承認は行わず、別のfresh ChatGPT Red Team threadが再判定する。

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）

初回P1修正ではdelegated authoring draftを使用しなかった。今回のbounded correctionではChatGPT Firstへ戻し、専用Blue Team threadがGitHub上のexact snapshotを確認してreplacement-ready blocksを作成し、Mainがsource／scope／non-regressionを検証してowner文書へ統合した。

| ロール（created_by_role） | 範囲（scope_id） | ドラフトパス（artifact draft path） | 参照元（source_paths） | 予定反映先（intended_targets） | 採用状態（adoption_status） | 反映先（reflected_to） | 差分ガード結果（diff_guard_result） | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果（reviewer result） | 昇格判断（promotion decision） |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Codex Main | iss-00334 canonical planning repair | 該当なし | `artifacts/20260726t235800z-review-system-architect-fail.md`; `artifacts/20260726t235801z-review-implementation-planner-fail.md`; `artifacts/20260726t235522z-review-canonical-spec-review-fail.md` | `requirement.md`; `design.md`; `plan.md`; `.assurance.json`; `report.md` | not used | `requirement.md`; `design.md`; `plan.md`; `.assurance.json`; `report.md` | `git diff --check` successful; planning validation successful | manual authoring | none | none | failed | fresh re-review後にexecute manual-authored canonical docs |
| ChatGPT Blue Team | iss-00334 bounded planning correction | `artifacts/20260727t014215z-chatgpt-blue-bounded-correction.md` | remote HEAD `b5447aef2c4d2ad5fabbab532cb9cef0e8d397b0`; `design.md`; `plan.md`; formal FAIL artifact | `design.md`; `plan.md` | adopted | `design.md`; `plan.md`; `.assurance.json`; `report.md` | exact target headings present; `git diff --check` successful; `spec-dock validate` 222 nodes; assurance verify valid | bounded manual integration | repository mutation／patch／review verdict claims | none | failed from prior Red; Blue did not self-review | commit／push後に別fresh ChatGPT Red review |
| ChatGPT Blue Team | iss-00334 second bounded planning correction | `artifacts/20260727t024714z-chatgpt-blue-bounded-correction-followup.md` | actual remote HEAD `546245f1072e6d7822fc7885eff814ac1eca1dc5`; formal Red FAIL artifact | `requirement.md`; `design.md`; `plan.md` | adopted | `requirement.md`; `design.md`; `plan.md`; `.assurance.json`; `report.md` | P1-12〜P1-16、P2-03／P2-04だけを統合; validate／diff-check／assurance verify successful | bounded manual integration | P1-11のproduct変更、repository mutation、review verdict claims | follow-up model selector verification unavailable | failed from fresh Red; Blue did not self-review | commit／push後に別fresh ChatGPT Red review |

## グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）

Assurance classifierのauthorityは`standard`である。Issue-local overlayとして、untrusted archive、public command contract、multi-file transaction、credentialed live mutationにstrict相当のclosureを追加した。overlayの解除条件は、これら高リスク面が不要になったことをowner文書で示し、assurance再分類とfresh spec reviewを通すreviewed amendmentである。

| グレード（Grade） | 必要な専門家 / 代替（required specialist / fallback） | 使用状況（usage） | 証跡（evidence） | 鮮度 spec-reviewer 判定（fresh spec-reviewer verdict） | 実行可否（execution readiness） |
|---|---|---|---|---|---|
| standard | system-architect and implementation-planner; ChatGPT Blue Team authoring evidence | used | prior specialist artifacts; `artifacts/20260727t014215z-chatgpt-blue-bounded-correction.md`; `artifacts/20260727t024714z-chatgpt-blue-bounded-correction-followup.md` | failed | blocked |

## レビューゲート状態（Reviewer Gate Status）

| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| canonical planning | ChatGPT-first canonical spec review | fresh Red Team | stale after correction | failed | no | fresh re-review required | `artifacts/20260727t022302z-chatgpt-fresh-canonical-review-fail.md`のP1-12〜P1-16、P2-03／P2-04をBlue correctionへ反映済み。P1-11はMainのrequested SHA誤り。別fresh threadの判定待ち |

## Assurance記録

- `./spec-dock/scripts/spec-dock assurance classify --stage requirement --issue iss-00334 --format json`: valid。`authorized_profile=standard`、`status=provisional`としてcurrent三文書へ再束縛した。
- `./spec-dock/scripts/spec-dock assurance verify --issue iss-00334 --format json`: valid。
- source binding:
  - Requirement SHA-256: `a1b2a06e25fd686fcfb85679cdc5f78a9de684ab51b1a11efba54e9f2c0cbc03`
  - Design SHA-256: `6e2adc750fb5472056e337e86856e4f803c8194839f8ca72525db35dc8e72fae`
  - Plan SHA-256: `74c1a7825db98e7c427c06649dde82bffe936d6c1a9381e83b3d87c311882531`
- `./spec-dock/scripts/spec-dock assurance compose --artifact all --issue iss-00334 --format json --dry-run`: Design／Planに`substantive_content_conflict`、`changed_paths=[]`を返した。current owner文書を上書きしないapproved no-opとして、non-dry-run composeは実施していない。
- strict相当overlayのdelta: exhaustive archive negative closure、transaction fault injection、specialist evidence、fresh spec/code/QA review、hermetic testとlive operationの分離。
- revert condition: public contract、untrusted archive、multi-file transaction、credentialed live mutationがscopeから除外されたreviewed amendmentに対し、assurance再分類とfresh spec reviewがpassした場合のみ解除する。

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
| S01 | delegated after planning pass | shipped CLI contractとtestsのbounded implementation | dev-coder | `plan.md` S01のexact targets／allowed pathsのみ | canonical `requirement.md`、`design.md`、`plan.md` | S01 Red／Green command、focused code review、diff allowlist | spec-reviewer fail、scope escape、test failure、new requirement gap | blocked。fresh planning review待ち |

#### 発見されたテスト / リスク（Discovered Tests）

planning repairで発見されたarchive safety、transaction fault、publication resume、live-operation boundaryのtest obligationsは、`plan.md`の`CLOS-ARC-01`〜`CLOS-ARC-25`、`CLOS-RISK-001`〜`CLOS-RISK-005`へ採用済みである。製品実装中に新しいtest／riskを発見した場合は、実装で吸収せずここへentryを追加し、materialな変更はPlan amendmentへ戻す。

#### ステップ契約の完了証跡（Step Contract Closure）

製品実装stepのclosure evidenceはまだ存在しない。S01開始後、各step ownerが持つ全`required=yes` rowについて、observed evidence、reviewer verdict、commit candidate、clean checkを追記する。

#### テスト契約の完了証跡（Test Contract Closure）

製品test contractはまだ実行していない。`plan.md`の各`tc-*`とSpec-Locked Closure Indexの対応を維持し、実行した事実だけを追記する。

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

## マイルストーン / commit 候補ゲート（Milestone / Commit Candidate Gate）

| マイルストーン / step | クロージャ状態（closure state） | コミット候補 / コミット範囲（commit candidate / scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | 差分確認 | 次アクション |
|---|---|---|---|---|---|
| canonical planning repair | second correction integrated; fresh review pending | Requirement、Design、Plan、Assurance、Report、fresh Red FAIL、Blue follow-up artifacts | commit pending | `git diff --check`、validate 222 nodes、assurance verify pass | new snapshotをcommit／pushし、actual full HEADで別fresh ChatGPT reviewを行う |
| S01 | not started | `plan.md` S01 exact scope | none | 製品実装差分なし | planning gate通過後にdev-coderへ委任する |

## 最終品質ゲート（Final Quality Gate / 必須）

| ゲート | 対象 | 観測結果 | 証跡 / 次アクション |
|---|---|---|---|
| Docs Impact S90 | docs、templates、README、workflow、skill、migration notes | not started | S01〜S09 closure後に判定 |
| Final QA | issue-wide obligation coverage | not started | S90後にfresh qa-reviewer |
| Final Code Review | integrated code and tests | not started | step-local review後にfresh issue-wide code-reviewer |
| Final Spec Review | Requirement、Design、Plan、Report、implementation、tests、docs alignment | failed | `artifacts/20260727t004653z-chatgpt-fresh-canonical-review-fail.md`; bounded correction後に別fresh ChatGPT review |
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
