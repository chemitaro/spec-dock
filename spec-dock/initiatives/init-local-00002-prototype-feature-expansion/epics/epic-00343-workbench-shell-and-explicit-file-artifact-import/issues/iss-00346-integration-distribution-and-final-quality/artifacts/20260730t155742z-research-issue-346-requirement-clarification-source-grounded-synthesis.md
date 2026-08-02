---
種別: research
ID: "20260730t155742z-research"
タイトル: "Issue 346 requirement clarification source-grounded synthesis"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-07-31"
親: ["iss-00346"]
関連: []
authority: "synthesized"
derived_from:
  - "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00343-workbench-shell-and-explicit-file-artifact-import/requirement.md"
  - "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00343-workbench-shell-and-explicit-file-artifact-import/design.md"
  - "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00343-workbench-shell-and-explicit-file-artifact-import/plan.md"
  - "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00343-workbench-shell-and-explicit-file-artifact-import/issues/iss-00344-workbench-shell-scaffolding/report.md"
  - "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00343-workbench-shell-and-explicit-file-artifact-import/issues/iss-00345-generic-single-file-artifact-import/report.md"
  - "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00343-workbench-shell-and-explicit-file-artifact-import/artifacts/20260728t100038z-adr-generic-imported-file-identity-and-privacy-boundary.md"
  - "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00343-workbench-shell-and-explicit-file-artifact-import/artifacts/20260730t085831z-adr-macos-generic-import-staging-cleanup-trust-boundary.md"
  - "spec-dock/initiatives/init-local-00002-prototype-feature-expansion/epics/epic-00343-workbench-shell-and-explicit-file-artifact-import/artifacts/20260730t102747z-adr-linux-anonymous-staging-trust-boundary.md"
reflected_to: []
---

# 20260730t155742z-research Issue 346 requirement clarification source-grounded synthesis

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約、用語衝突、edge case など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は artifact type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は source-grounded research evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、用語衝突、edge case、判断への含意を混ぜない。
- local context で解ける疑問は人間に聞かず、この artifact に source-grounding を残す。

## 1. 調査目的

Issue 346（Candidate 3）の役割を、親Epicの受入契約、Issue 344/345の完了・引継ぎ証跡、accepted ADR、現行配布テストから具体化する。目的は、配布・統合・最終品質を確認するIssueであることを明確にし、既存機能を再設計したり新機能を追加したりせずに、Issue planningへ渡せる検証境界を確定することである。

このartifactはsource-grounded research evidenceであり、canonical requirement/design/planではない。ここでの「採用候補」は、後続のIssue planningで正本へ明示採用・レビューされるまで拘束力を持たない。

## 2. 読んだ一次資料

- 親Epic正本: `spec-dock/active/epic/requirement.md`、`design.md`、`plan.md`。
- 先行Issue正本・実装報告: Issue 344/345の`requirement.md`、`design.md`、`plan.md`、`report.md`。
- accepted Epic ADR:
  - `20260728t100038z-adr-generic-imported-file-identity-and-privacy-boundary.md`
  - `20260730t085831z-adr-macos-generic-import-staging-cleanup-trust-boundary.md`
  - `20260730t102747z-adr-linux-anonymous-staging-trust-boundary.md`
- 現行テスト面: `tests/unit/infra/test_init_update.py`（wheel/sdist/installed-resource inventoryおよび隔離installed wheel runtimeのhelper）、`tests/cli_runtime/test_new.py`（node scaffold作成のCLI契約）。

調査は上記の記述と現行テストの構成を突合した文書調査である。wheel install、platform capability、full regressionの実行結果はこのartifactではまだ観測していない。

## 3. 確定した要件

### 3.1 ユーザー価値とin-scope（事実）

- Candidate 3の利用者価値は、Workbench shellとgeneric single-file Artifact importを、candidate wheel、fresh/既存consumer、dogfoodで一貫して使え、blocking findingのないmergeable PRとして受け取れることである。
- 依存先はCandidate 1（Issue 344）とCandidate 2（Issue 345）であり、Candidate 3は両方の最終検証ownerである。
- このIssueが担うvertical scopeは、wheel inventory/candidate wheel、fresh consumer、pre-feature existing consumer updateとno-backfill、その後に作るnode、統合dogfood、root/nodeのmanual external-file scenario、full regression、docs parity、Epic report trace、最終レビューとPR準備である。
- Issue 344はWorkbench shellのprovider/package surfaceとsource/wheel/sdist/installed resourceの証跡を持つ。Issue 345はgeneric importのCLI・opaque lifecycle・privacy/publication契約を実装し、Candidate 3へcandidate wheel、各target、external/cross-filesystem/privacy、dogfood、full regression、Epic-wide reviewを引き継いでいる。

### 3.2 out-of-scope（事実）

- Workbenchの自動copy/sync/copy-back、watcher、directory/glob/bulk/recursive import、content parse/classification/format conversion、typed `file` token、source delete/move/overwrite、canonical artifactの自動採用は追加しない。
- Workbenchのretention/TTL/session model、directory bundle、background catalog、既存nodeの再利用・再開、利用者価値と無関係なarchitecture cleanupも対象外である。
- Candidate 3は先行Issueのmajor feature未実装を引き受けない。失敗を直す場合もcross-feature integration failureの最小修正に限る。

### 3.3 互換性・配布（事実）

- `artifact import chatgpt-output`、`new artifact`、`workbench copy`の既存public behaviorを保持する。
- provider source、packaged assets、fresh installed consumer、updated consumer、dogfood projectionで同一behaviorを提供する。
- candidate wheelはtemporary Git repositoryへinstallし、fresh root/future nodeのshellとroot/node generic importを通常権限で実測する。
- `test_init_update.py`には、candidate build artifact、wheel/sdist/installed resource inventory、隔離されたinstalled wheel runtimeを扱う既存helperがある。Issue planningではこれを優先して配布検証を構成する。

### 3.4 platform・privacy・opaque lifecycle（事実）

- generic importは明示したreadable regular file一件のみを扱い、source bytes/source fileを成功・失敗とも変更しない。repository外sourceは追加flagなしで許し、通常output/JSON/tracked provenanceにはbasename以外のabsolute path、body、hash、byte count等のcontent-derived valueを出さない。
- import結果はevidence保存であり、canonical docs/report/ADR/assuranceの採用や変更を意味しない。binary、ZIP、invalid UTF-8、NULを含むgeneric Artifactを後続のvalidate/sync/discovery/deps/contextが内容decodeせずに扱える必要がある。
- Linuxはaccepted ADRにより、`O_TMPFILE` anonymous stagingとheld-FD no-replace publicationを満たすsupported filesystemだけをsuccess laneとする。capability不足はformal destination作成前に`publication_unsupported`/`not_committed`/`safe_after_remediation`でfail closedし、named-temp、visible-probe、pathname-cleanup fallbackを使わない。sourceがdestinationと別filesystemでもsuccessを維持する。
- macOSはclone-capable laneのnormal cleanupと、final identity checkまでに観測できるmismatch/uncertainty時のretainを再確認する。accepted ADRが限定した、同一UID actorによる最終check後からunlinkまでの意図的replacementを、完全防御のpassとして主張してはならない。

### 3.5 no-backfill、修復境界、最終delivery（事実）

- existing root/Initiative/Epic/IssueにはWorkbench READMEをbackfillしない。既存consumerのupdate後に作成するnew nodeだけがREADMEを得る。dogfood update後も既存`epic-00343`はbackfillしない。
- requirement/design/ADRを変更する必要が判明した場合は、Issue内の仮定や局所修正で済ませずEpic planning repairへ戻す。
- final deliveryでは、integration/distribution evidenceへのfresh QA、Candidate 1/2/3を含むEpic base/head aggregate diffへのfresh code review、Epic closure evidenceへのfresh spec review、同じendpointのEpic-wide decision/code/spec reviewをpassまで実施する。final commit/push/PR Delivery Gate/Merge Preparation Gateを閉じ、human merge前で停止する。

## 4. pre-feature existing consumerの具体的定義

### 4.1 確定した定義（推論、親Epic契約からの最小化）

「pre-feature existing consumer」は、特定の歴史的commitを必須としない。現行のconsumer契約を満たす有効なworkspaceであり、更新前に対象となる既存rootおよび既存nodeが存在し、各`.workbench/README.md`を持たないsynthetic fixtureとする。このfixtureにcandidate wheelによるupdateを適用し、既存scopeがbackfillされず、更新後に新設するnodeだけがREADMEを得ることを検証する。

この定義はE-AC-004が「READMEのないexisting root / Initiative / Epic / Issueを用意する」と定め、Candidate 3が「READMEなしpre-feature consumerをupdate」すると定めていることに基づく。歴史的な時点そのものではなく、更新前の欠如状態と有効な既存consumerであることが受入対象である。

### 4.2 歴史的commitを使用する場合の追加条件（事実からの含意）

歴史的commit/旧wheelをfixtureに使うこと自体は妨げない。ただし、当該revisionがWorkbench shell/generic importを搭載していないことを実測で確認し、使用したSHA、確認方法、candidate wheelへの更新結果をIssue reportへ記録する。単に古いSHAであることをpre-featureの根拠にしてはならない。

## 5. 受入シナリオ

以下は親Epicの受入基準とCandidate 3 verificationを、Issue planningでテストケースへ落とすためのGiven/When/Then表現にしたもの。実装詳細・fixture名・テスト配置は未決定である。

### 5.1 fresh wheel consumer

- **Given** candidate wheelをinstallできるtemporary Git repository、**When** fresh initしrootとfuture nodeを作成する、**Then** rootおよび新規nodeにtracked `.workbench/README.md`があり、README以外のWorkbench payloadはGit管理されない。
- **Given** 同じfresh consumer、**When** rootとnodeを明示targetにしてregular fileをimportする、**Then** generic `--` filename familyでopaque bytesが保存され、既存typed/blank Artifact・`chatgpt-output`契約を変更しない。

### 5.2 updated consumer / no-backfill

- **Given** 4.1のREADMEなしvalid synthetic existing consumer、**When** candidate wheelでupdate、sync、validate、active切替、Artifact/ADR作成を行う、**Then** existing root/Initiative/Epic/IssueにはREADMEが追加されず、既存Workbench stateのbytes/names/mtimesを変えない。
- **Given** update後の同consumer、**When** future nodeを作成する、**Then** 新規nodeだけが`.workbench/README.md`を得る。

### 5.3 integrated dogfood

- **Given** Candidate 1が投影したshellとCandidate 2のgeneric importを含むdogfood workspace、**When** provider-first updateを適用して既存`epic-00343`を検証する、**Then** 既存Epicはbackfillされず、validate/sync/deps/contextが成功し、shell/import/docs/CLI help/examplesのparityを確認できる。

### 5.4 external cross-filesystem import / privacy

- **Given** destinationとは別filesystemにあるexternal regular sourceとroot/node target、**When** generic importする、**Then** sourceを変更せずに成功し、output/JSON/provenanceへexternal absolute path、body、hash、byte count sentinelが漏れない。

### 5.5 opaque lifecycle / platform

- **Given** binary、ZIP、invalid UTF-8、NULを含むimport済みArtifact、**When** validate/sync/default discovery/deps/contextを実行する、**Then** body decode errorやsemantic parseなしに成功する。
- **Given** Linux supported filesystem、**When** importする、**Then** visible probe pathnameやnamed-temp fallbackなしにanonymous stagingからFD-bound no-replace commitへ進む。capability不足ならformal destinationを作らずfail closedする。
- **Given** macOS clone-capable lane、**When** normal cleanupまたは観測可能なmismatch/uncertaintyを検証する、**Then** normal cleanupまたはretain warningの既存contractを満たし、accepted ADRの限定外を安全保証として主張しない。

### 5.6 full regression / review / delivery

- **Given** 上記のfocused distribution evidenceと必要な最小integration repair、**When** `uv build`、通常test lane、明示許可されたfull regression、`validate`、`sync --no-github`を実行する、**Then** 結果をEpic reportのE-RQ/E-AC traceへ記録し、blocking findingを残さない。
- **Given** Epic aggregate base/head diffとclosure evidence、**When** fresh QA/code/specおよびEpic-wide decision/code/spec reviewを行う、**Then** passしたレビューとPR delivery evidenceを残し、human merge前で停止する。

## 6. 前提・制約・非目標

- provider-side implementation authorityは`src/spec_dock/`であり、`spec-dock/`はdogfood projection/validation surfaceである。
- generic importのfilename、full-basename identity、privacy、FD-bound commit point、post-commit retry不要、macOS/Linuxのplatform boundaryはaccepted ADRの契約であり、Candidate 3が再判断しない。
- Workbenchはoptional、worktree-local、disposable、non-canonicalである。存在しないscopeもvalidであり、手動`workbench copy`はexplicit one-shot source-wins helperのまま維持する。
- Issue 346は統合品質Issueであり、先行実装を拡張する場ではない。新規の対応platform、trusted helper、永続catalog、source metadataは非目標である。

## 7. 未確定事項の判定

ユーザーに確認すべき必須事項はない。親Epic、accepted ADR、先行Issueの引継ぎが、対象範囲、互換性、platform boundary、no-backfill、delivery gateをすでに定めている。

残る未決定は、synthetic fixtureの具体的な構成、既存test helperの再利用方法、platform実行環境、テストの正確な配置・命名、reportでの証跡形式などの実装詳細である。これらはIssue planningで決める。正本契約を変える必要が生じた場合は、Epic planning repairへ戻す。

## 8. canonical requirement/design/planへの採用候補

後続のIssue planningで、次を正本へ採用候補として扱う。

1. Candidate 3を「配布と統合品質の閉鎖」と定義し、major featureの追加ではなく最小integration repairに限定する。
2. pre-feature existing consumerを、READMEなしのvalid synthetic existing fixtureとして明文化する。歴史的revisionを使う場合だけ、feature非搭載の実証とSHA/report記録を追加する。
3. fresh wheel、updated consumer/no-backfill、dogfood、external cross-filesystem/privacy、opaque lifecycle、Linux/macOS boundary、full regression、review/deliveryを受入シナリオとしてtraceする。
4. Provider source/wheel/sdist/installed resourceの既存inventory helperを再利用し、candidate revisionが各consumer surfaceへ届くことを検証する。
5. requirement/design/ADRの変更を検知した場合のEpic planning repairを明示gateとして残す。

## 9. handoff

次の担当はIssue planningである。まずこのartifactの事実と推論をcanonical requirement/design/plan候補へ分離して反映し、各受入シナリオを既存テスト面に対応付ける。その後、fresh specification reviewを通し、implementation前に実行可能な計画へ固定する。

実装中にCandidate 1/2の欠落機能、accepted ADRと矛盾するplatform behavior、privacy/no-backfill違反、またはmajor refactorが必要と判明した場合は、Candidate 3で吸収せずEpic planning repairへ戻す。

## 参考（References）

- Epic requirement: E-RQ-021〜025、E-AC-004、E-AC-015〜020。
- Epic plan: Candidate 3、G3/G4、completion criteria。
- Generic import identity/privacy ADR: `20260728t100038z-adr-generic-imported-file-identity-and-privacy-boundary.md`。
- macOS/Linux staging ADR: `20260730t085831z-adr-macos-generic-import-staging-cleanup-trust-boundary.md`、`20260730t102747z-adr-linux-anonymous-staging-trust-boundary.md`。
