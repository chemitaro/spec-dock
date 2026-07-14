---
種別: 要件定義書（Issue）
ID: "iss-00319"
タイトル: "Installed Runtime Dogfood Parity Final Quality And Mergeable PR"
関連GitHub: ["#319"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-14"
親: ["epic-00312", "init-local-00003"]
依存: ["iss-00315", "iss-00316", "iss-00317", "iss-00318"]
---

# iss-00319 Installed Runtime Dogfood Parity Final Quality And Mergeable PR — Issue 要件定義

## 0. 文書の位置づけ

本書は、Epic 00312 の最終 distribution / quality / PR delivery Issue が満たすべき観測可能な成果、制約、受け入れ条件を定義する。具体的なファイル配置、テスト順序、repair手順は `design.md` と `plan.md` で定義する。

Issue 315〜318 の仕様・実装を再設計するのではなく、それらを provider authority から package、fresh consumer、existing consumer、dogfoodへ一貫して配布し、Epic全体の品質と単一PRのmerge preparationを閉じる。

## 1. 目的と観測可能な成果

### 1.1 目的

- Issue 315〜318 が完成させた Workbench ignore/opacity、scoped copy、byte-preserving Artifact import、ChatGPT-first preservation workflowをinstalled consumerとdogfoodで利用可能にする。
- Public docs、package/fresh init/existing update、full regression、static quality、manual integrated scenario、Epic closureをfinal headで実証する。
- Latest `main` と整合した単一PRを作成し、checks・review・mergeabilityを観測してmerge可能な状態まで準備する。

### 1.2 完了後に観測できること

- Candidate wheelに必要なprovider runtime、docs、templates、ignore asset、installed agent-tooling assetsが含まれる。
- Candidate wheelから初期化したfresh repositoryで、Workbench placement/opacity、`workbench copy`、`artifact import chatgpt-output`、ChatGPT-first planning skillsを利用できる。
- Feature導入前のexisting consumerをcandidateでupdateしても、root / Initiative / Epic / Issueの既存Workbench bytesが保持される。
- Provider authorityとdogfood projectionのinventory/bytesが、明示されたgenerated/local exceptionを除き一致する。
- Root READMEとpublic reference docsがexperimental、non-canonical、root manual selection、scoped source-wins copy、no automatic sync/copy-back、byte-preserving import、blank coexistence、evidence-only authorityを説明する。
- Issue 315〜318 のfocused contract、repository-wide regression/static、installed manual scenarioがfinal headでpassする。
- Epic reportでE-RQ-001〜024、E-AC-001〜016、EAL/OAL、残存risk、Issue/PR linkが追跡される。
- Fresh QA → code → spec reviewが順序どおりpassする。
- `main`向けPRのrequired checks、review threads、mergeabilityを観測し、blocking findingが残らない。

### 1.3 完了後に観測できてはいけないこと

- Root Workbenchの一括copy command/helper、automatic sync、copy-back、promotion、retention管理。
- Extension、language、MIME、content、secretの分類器。
- `chatgpt-output` typed token、blank prefix予約、template/frontmatter/sidecarの自動追加。
- Existing Workbenchの削除、rewrite、permission normalization。
- Workbench/Artifact本文、secret-like value、absolute host pathのlog・report・PR bodyへの露出。
- ChatGPTの推測、過去のtest count、worker self-claimだけによるpass/merge-prepared主張。
- PR作成前、checks未確認、unresolved blocking reviewがある状態でのmerge可能主張。

## 2. 背景と開始条件

### 2.1 完了済み依存

| Issue | 完了能力 | Issue 319へのrelay |
|---|---|---|
| iss-00315 | `.workbench/` ignore、default semantic discovery opacity | package/fresh/update、full quality、PR |
| iss-00316 | explicit scoped copy、source-wins merge、safety/output | installed scenario、public docs、full quality、PR |
| iss-00317 | byte-preserving `chatgpt-output` import | package/fresh/update、Linux publication、public docs、PR |
| iss-00318 | preservation branch/checkpoint/EAL workflow | public docs、installed/manual alignment、final review、PR |

GitHub Issue #315〜#318 はclosedで、Issue 319は全4 Issueへのdependencyを持つ。

### 2.2 現在のgap

- Issue 319のcanonical requirement/design/planは未具体化だった。
- Provider/dogfoodの各Issue-local parity evidenceはあるが、candidate wheel由来のfresh/existing consumerをfinal headで未実証である。
- Root/public docsとmigration/update guidanceの最終impact resolutionが未完了である。
- Full repository tests、repository-wide static、manual integrated scenario、Epic-level closure、final reviewers、PR deliveryが未完了である。
- 2026-07-14のlocal live stateで`origin/main...HEAD`はmain側31、Issue branch側53のdiverged状態であり、final quality evidence前にnon-destructive integrationが必要である。

## 3. 親スコープとtrace

### 3.1 親Epic

- Epic: `epic-00312`
- Final quality slice: W5 / DS-005
- Dependencies: W1〜W4 = Issue 315〜318
- PR policy: Issue 319はdeferred PR deliveryを再延期できない。

### 3.2 Epic requirement / acceptance trace

| Issue 319責務 | 親契約 |
|---|---|
| Workbench ignore/opacity/delete/update再検証 | E-RQ-001〜005、013、015、017〜018 / E-AC-001〜002、010〜011 |
| Scoped copy installed verification | E-RQ-006〜012、014、016 / E-AC-003〜009 |
| Artifact import installed verification | E-RQ-019〜023 / E-AC-013〜015 |
| Preservation workflow/authority alignment | E-RQ-024 / E-AC-016 |
| Distribution、full quality、Epic closure、PR | E-AC-011〜016と全E-RQ/E-AC最終再検証 |

### 3.3 再定義してはいけない境界

- Provider-side source of truthは`src/spec_dock/`、shipped scaffoldは`src/spec_dock/assets/`、installed agent-tooling authorityは`src/spec_dock/assets/install_root/`である。
- `spec-dock/`、root `.agents/`、root `.codex/`はdogfood/installed projectionであり、primary implementation authorityにしない。
- `.workbench/`はGit-ignored、non-canonical、disposableで、Node/ADR/dependency/context/review/readiness authorityではない。
- Root Workbenchは必要ファイルのmanual selection/copyだけを許し、一括copy commandの対象にしない。
- Scoped copyはcurrent source worktreeからsame-repository linked target worktreeの一scopeへone-shotで実行し、destination-only保持、source wins、no sync/copy-backを維持する。
- Artifact importは既存blank grammar/collision allocationを用い、source bytes/source fileを保持し、canonical adoptionをself-claimしない。
- Preservation statusとadoption statusを分離し、EAL採否はmain orchestratorが管理する。

## 4. Actorと代表シナリオ

| Actor | 役割 |
|---|---|
| spec-dock利用者 | fresh init / existing update / Workbench copy / Artifact importを実行する |
| Main orchestrator | EAL、manual scenario、Epic closure、PR deliveryを統括する |
| DevCoder | approved planの各stepを`gpt-5.6-sol` / reasoning `medium`で実装・repairする |
| qa/code/spec reviewer | `gpt-5.6-sol` / reasoning `medium`でfresh read-only reviewを行う |
| package/installer/runtime | provider assetsをconsumerへ配布・更新する |
| GitHub | Issue/PR/check/review/mergeabilityのexternal stateを提供する |

### SC-319-001 Fresh consumer

Candidate wheelからclean repositoryをinitし、Workbench配置、scoped copy、Artifact import、planning skill/docsが利用でき、package外のlocal sourceに依存しない。

### SC-319-002 Existing consumer update

Feature導入前consumerのroot/scoped Workbenchへsentinel bytesを置き、candidate update後もbytes/inventoryが完全一致し、managed assetsだけが更新される。

### SC-319-003 Integrated ChatGPT-first flow

Fresh installed consumerでscope-local Workbenchをlinked worktreeへcopyし、完成Markdownを`chatgpt-output` Artifactへimportし、EALで採否を記録してからcanonical rewriteする。SourceとArtifact bytesは一致し、copy/import本文は出力されない。

### SC-319-004 Final delivery

Latest main統合後のfull qualityとfresh reviewsをpassし、単一PRをpush/create/observe/repairしてblocking findingなし・mergeableを確認する。

## 5. Issue要件

### RQ-319-001 Planning authority

- ChatGPT 5.6 Proのcomplete bundled planning outputをcanonical rewrite前に`chatgpt-output` Artifactとして保存する。
- ChatGPT outputはevidence-onlyとし、requirement → fresh spec review → assurance → design → fresh spec review → plan → fresh spec reviewの順序を守る。

### RQ-319-002 Main integration

- Final distribution/quality evidence前にlocal/remote/latest main差分を再確認する。
- Behind/divergedならrepository policyに従うnon-destructive integrationを行い、semantic conflictをowning contractへrouteする。
- Force push、履歴破壊、未確認のconflict resolutionを行わない。

### RQ-319-003 Package inventory

- Clean managed temporary locationでcandidate wheelをbuildし、必要なruntime/docs/templates/ignore/install-root assetsの収録を検証する。
- Generated caches、temporary files、Workbench内容、secretsをpackageへ含めない。

### RQ-319-004 Fresh init distribution

- Candidate wheelだけを用いたfresh initでprovider assetsとcommand/workflow surfaceを利用できる。
- Local checkoutへのimplicit dependencyを許さない。

### RQ-319-005 Existing update preservation

- Pre-feature consumerへのcandidate updateでmanaged assetsを更新し、root/scoped Workbenchのpath/type/bytesを保持する。
- Workbenchをmanaged/canonical dataへ移行・正規化しない。

### RQ-319-006 Provider/dogfood parity

- Provider authorityからdogfoodへapproved refresh pathで投影し、対象inventory/bytesを比較する。
- Dogfood-only修正を禁止し、差分はprovider ownerへ戻す。

### RQ-319-007 Public documentation

- Root READMEとpublic docs/help/outputでplacement、root manual selection、scoped source-wins、no automatic sync、Artifact import、byte/source preservation、blank coexistence、experimental/non-canonical/evidence-only authorityを説明する。
- Migration/update guidanceは既存Workbenchを保持しcanonical migrationを行わないことを説明する。

### RQ-319-008 Focused and full quality

- Issue 315〜318のfocused contract suitesをfinal headで再実行する。
- Unit、CLI runtime、integration、full pytest、repository-wide configured static/format gatesを実行する。
- Failureをowning Issue/stepへrouteし、checkのskip/disableでgreen化しない。

### RQ-319-009 Cross-platform publication

- Artifact importのno-overwrite/atomic publicationをsupported platformで検証し、Linux-specific pathは利用可能なCI/runnerで実証する。
- Runner不在時は未検証をpass扱いせず、PR gate上のblocker/riskとして明示する。

### RQ-319-010 Manual integrated scenario

- Safe synthetic dataだけでWorkbench handoff → Artifact import → EAL disposition → canonical rewriteをfresh installed consumer上で実行する。
- Source survival、destination hash/bytes、no overwrite、authority boundary、body secrecyを観測する。

### RQ-319-011 Epic ledgers and closure

- Epic reportで全E-RQ/E-ACをcurrent evidenceへtraceし、EAL/OAL、Issue closure、docs impact、risk、PR linkを更新する。
- Historical evidenceとIssue319 current evidenceを区別する。

### RQ-319-012 Ordered final review

- Final QA → fresh code → fresh spec reviewを順序どおり行う。
- 全DevCoder/reviewerは`gpt-5.6-sol` / reasoning `medium`を用いる。
- Finding修復後はaffected gateをfresh rerunし、latest headへevidenceをbindする。

### RQ-319-013 PR delivery and observation

- Issue branchをpushし、`main`向け単一PRを作成する。
- Required checks、review submissions/threads、mergeability、base driftを観測し、blocking findingをrepairする。
- Issue 319からPR deliveryを別Issueへ延期しない。

### RQ-319-014 Lifecycle and claim integrity

- Commit/push/PR/check/review evidenceが揃う前に`issue finish`しない。
- Epic spec/quality closure、GitHub Epic issue close、PR mergeを区別する。
- Userの明示指示なしにPRをmergeしない。

### RQ-319-015 Data minimization

- Test/manual/report/PR outputをcontent-freeに保ち、Workbench/Artifact本文、secret-like value、absolute host pathを記録しない。
- Safe synthetic fixtureだけをversion controlへ入れる。

### RQ-319-016 Minimal change

- Distribution/docs/quality/repairに必要な最小差分だけを許す。
- Version bump、lock update、専用migration fileはcurrent contractで必要と確認された場合だけ採用する。
- New product semantics、general refactor、root helperを追加しない。

## 6. 受け入れ条件

- AC-319-001: Issue315〜318 dependency、GitHub state、canonical relay、local main divergenceが開始時に観測される。
- AC-319-002: Bundled ChatGPT outputがcanonical rewrite前にbyte-preserving Artifactとして保存され、EAL採否と分離される。
- AC-319-003: Latest main integrationがfinal quality前に完了し、conflict/behind状態が解消される。
- AC-319-004: Clean candidate wheelのinventoryに必要assetsがあり、不要/secret/Workbench contentがない。
- AC-319-005: Fresh candidate initだけで全Workbench/copy/import/workflow surfaceが利用できる。
- AC-319-006: Existing candidate update後にroot/scoped Workbenchのpath/type/bytesが不変である。
- AC-319-007: Provider/dogfoodのmanaged inventory/bytesがdocumented exceptionを除き一致する。
- AC-319-008: Public docs/help/outputがexperimental、manual root、scoped copy、no sync、byte import、authority boundaryを一貫して説明する。
- AC-319-009: Issue315〜318 focused tests、unit/CLI/integration/full pytest、configured static/format gatesがlatest headでpassする。
- AC-319-010: Supported cross-platform publication pathがpassし、未利用platformをpassと偽装しない。
- AC-319-011: Fresh installed consumer manual scenarioでcopy/import/EAL/rewriteの順序とsource/hash/body secrecyが確認される。
- AC-319-012: Epic reportの全E-RQ/E-AC、EAL/OAL、docs impact、riskにunresolved blocked/stale entryがない。
- AC-319-013: Fresh QA、code、spec reviewersが順序どおりblocking findingなしでpassする。
- AC-319-014: Single PRがpush/createされ、required checks、review threads、mergeability、base driftが観測される。
- AC-319-015: PRにunresolved blocking finding/conflictがなく、merge可能と判断できる。
- AC-319-016: `issue finish`はcommit/push/PR observation後に実行され、PR mergeは行わない。

## 7. Failure / rollback / risk signal

| Signal | Required response |
|---|---|
| Main behind/diverged/conflict | final evidence採取を停止し、non-destructive integrationとowner確認 |
| Wheel asset missing/extra | package-data/provider ownerへrouteし、fresh/update gate停止 |
| Existing Workbench byte drift | release blocker。installer/update ownerへrouteし、consumerを保持してrepair |
| Provider/dogfood mismatch | dogfood側で直接修正せずproviderへroute |
| Full/static failure | owning contractへ分類し、focused repair後にfull rerun |
| Linux publication未実証 | passにせずPR blocker/riskとして扱う |
| Manual scenario content leak | 即停止し、evidenceを公開せずsafe fixtureで再実行 |
| Reviewer finding | promotion停止、repair、fresh rerun |
| PR check/review/base drift | merge-prepared claim停止、repair/integration後に再観測 |

Rollbackは、Issue319で追加したdocs/tests/packaging repairをfocused commit単位でrevert可能に保つ。Issue315〜318のaccepted contractsをrollbackやredesignの対象にしない。Existing Workbenchを削除・再生成して回復しない。

## 8. Evidenceと採用境界

- Preserved evidence: `artifacts/20260714t110631z-chatgpt-output-issue-319-chatgpt-5-6-pro-bundled-planning-report.md`、SHA-256 `9352f5120661d61e65bc8591e466a4a69e0a55c6f871bf8d123199964b445641`、85,219 bytes。
- Adopt candidate: Parent W5/DS-005、Issue315〜318 relay、distribution topology、latest-main-before-final-quality、public docs impact、full/static/manual/final review/PR ordering。
- Partial: ChatGPTのGitHub connector observationとhistorical test countsはbaseline/risk evidenceだけに使い、current pass evidenceにしない。
- Deferred until inspected: version bump、`uv.lock`、dedicated migration file、exact Linux runner、exact required PR checks。
- Rejected: root bulk copy、automatic sync、classifier、typed `chatgpt-output`、blank reservation、ChatGPTによるpass/readiness self-claim。

## 9. Grade / readiness

- Suggested grade: M / Strict final delivery。
- Security/privacy-sensitive content本文を扱わず、content-free evidenceを強制する。
- Migration/persistence schema変更は要求しないが、existing consumer state preservationを高リスクgateとして扱う。
- Requirement fresh spec-review passとassurance classify/compose前にdesign/planをcanonical化しない。
- Blocking unknown: latest main conflict content、wheel inventory、pre-feature update baseline、Linux runner、current full/static state、PR required checks。いずれもplanで検証stepを持たせ、実行前pass claimをしない。
