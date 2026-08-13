---
種別: 実装計画書（Issue）
ID: "iss-00360"
タイトル: "Cut Over Distribution and Retire Legacy Workflow Surfaces"
関連GitHub: ["#360"]
状態: "draft"
作成者: "Codex main orchestrator"
最終更新: "2026-08-13"
依存: ["requirement.md", "design.md"]
親: ["epic-00356", "init-local-00003"]
planning_level: "strict"
implementation_baseline: "a6ded0d9a838b40cdcd741fa473cd264b801f245"
handoff_state: "implementation-start-blocked"
---

# iss-00360 Cut Over Distribution and Retire Legacy Workflow Surfaces — 実装計画

## 1. Planning Level

Planning Levelは`strict`とする。

本Issueはpublic distribution、existing consumer migration、known managed fileのprune、uninstall、symlink / hard link / modeを含むcross-platform filesystem safety、wheel / sdist parity、node-local historical evidenceのbyte-preservationへ同時に影響する。Partial failure時はportableなtransaction rollbackを新設せず、full preflight、phase marker、idempotent retry、post-verifyによるforward recoveryで収束させる。

次のいずれかが判明した場合は`critical`へ再評価して実装を停止する。

- Credential、secret、production data、個人情報の処理がscopeへ入る。
- Repository外write / deleteの可能性がある。
- `spec-dock/initiatives/**`またはnode-local evidenceの不可逆なrewrite / deleteが必要になる。
- Ownership evidenceなしにuser-owned fileを置換・削除しないと成立しない。
- 全mutation前のfull preflightを維持できない。

## 2. Authorityと実装開始gate

### 2.1 固定入力

| Input | Exact identity / status | Use |
|---|---|---|
| Current main | `a6ded0d9a838b40cdcd741fa473cd264b801f245` | 本Plan作成時のimplementation baseline |
| Issue 357 | PR #362 head `55a7e41df93297832f5db2b0c3abb96161355cc9`、merged / closed | Storage Coreと360 handoff keep inventory |
| Issue 358 | PR #361 head `5d1e3a4ccd09b4f6a1f5272107e6100b6f289bef`、merged / closed | Authoring Kit、preservation fixture、IC-1 content |
| Issue 359 | PR #363 head `948d0cf0dedb84ca34e51a4adc0995820aa011f6`、merged / closed | 二skill、旧18 + legacy 3 inventory、IC-2 content |
| IC-1 | `artifacts/20260812t174542z-disc-ic-1-core-kit-contract.md` = `pass` | Core / Kit handoff |
| IC-2 | `artifacts/20260812t174548z-disc-ic-2-skill-contract.md` = `pass` | Skill handoff |
| Dependency | `deps check --id iss-00360`: `ready=true`, blockers 0 | Runtime dependency-only gate |

IC-1 / IC-2はEpic Plan §6.1の文書上のhandoffであり、Runtime metadataや`ready`の意味を変更しない。未承認の品質・統合・handoff用最終Issue候補は作成もdependency登録もしない。

### 2.2 実装開始条件

実装mutationへ進む前に、次をすべて満たす。

1. Current branchがIssue 360 branchで、`origin/main`の上記baseline以降を含む。
2. Requirement / Design / Planがfresh reviewerでP0 / P1なしとなる。
3. Current branchを正しい同名upstreamへpushし、local `HEAD`とupstream SHAが一致する。
4. Formal `issue start iss-00360`が成功し、active Issueが`iss-00360`である。
5. ChatGPT-SpecReview-Strictがcleanなupstream同期済みHEADのcanonical R/D/Pを`pass`とする。

いずれかが失敗した場合は実装を開始せず、Issue reportへblocker、owner、再開条件を記録する。Issue 360自身の文書やreview結果だけでICまたはlifecycleを自己承認しない。

§2.2を満たした時点をplanning handoff / implementation-start-readyとする。実装開始後も、S10 inventory lockがpassするまでmanifest / prune logicを書かず、S20のRED testが期待理由で失敗するまでproduction behaviorを変更しない。

現在はS20の実行順をS40A / S40Bのphysical cutover後へ改訂した直後であり、Planの状態は`draft`、handoffは`implementation-start-blocked`とする。改訂後のstep本文順・依存graph・exact-upstream SHAに対するfresh `spec-reviewer`および`ChatGPT-SpecReview-Strict`のP0 / P1なし`pass`を得るまで、S10を含む実装stepを開始しない。両gate通過後にのみ、metadataを`approved` / `implementation-start-ready`へ戻す。

## 3. 実装対象inventory

詳細なTarget / obsolete / preserve契約はRequirement §2とDesign §4〜§9を正本とする。S10で現物から再生成し、次の最小境界をlockする。

### 3.1 Current Target

- Managed scaffold: `src/spec_dock/assets/spec_dock/{docs,templates,scripts,system}/**`と必須provider asset `src/spec_dock/assets/spec_dock/.gitignore`。`.gitignore`のhard-coded fallbackは削除し、package source欠損時は全mutation前にblockする。`spec-dock/spec-dock.version`は実行中package versionから生成し、root Workbench seedは`templates/root/.workbench/README.md`からFresh時だけ配置する。
- Repo-local skills: `src/spec_dock/assets/install_root/.agents/skills/{spec-dock,spec-dock-grill-with-docs}/**`。
- Retained workflow: `src/spec_dock/assets/install_root/.github/workflows/ci.yml`。Storage Coreの決定論的`sync` / `validate`だけを実行する。
- Shortcut: repo root `spec`から`spec-dock/scripts/spec-dock`へのcanonical identity。
- Generated consumer state: `spec-dock/active/**`と`spec-dock/.agent/**`。

Current file catalogのauthorityは物理provider treeである。Current pathとdigestの全量をJSONへ複製しない。

### 3.2 Obsolete managed surface

- Issue 357 handoffの`scripts/spec-dock-chatgpt`、`scripts/authoring-pack/**`、`chatgpt_*`、`issue_planning*`、Runtime各layerの`authoring_pack/**`、planning-only shared symbol / test / fixture。
- Issue 358 handoffのobsolete template、旧Current docs、旧workflow / phase / assurance / profile navigation。
- Issue 359 handoffの旧managed 18 skill、legacy 3 skill、host adapter、native agent shim、execution prompt、repo-local profile、SpecDock-installed Codex rule、agent-driven GitHub workflow。
- `.github/workflows/ci.yml`はobsoleteへ含めない。

Obsolete inventoryはprovider-private `src/spec_dock/assets/managed_distribution.json`へ、repository-relative exact file path、再現可能なhistorical identity、mutation policyだけを記録する。Directory、glob、prefix、推測digestは登録しない。Consumer-side manifestの`owner` / path自己申告は信頼せず、manifest自身がknown historical bytesであり、provider-private recordが同じtarget path + target identityを固定し、実targetも一致する場合だけ補助evidenceとして使う。

### 3.3 Preserve surface

- `spec-dock/initiatives/**`のidentity、`.meta.json`、R/D/P/Report、Artifact、Discussion、ADR、`.assurance.json`、profile由来文書、draft / repair / heavy Report、unknown node-local file。
- Root / scope Workbenchのunmanaged payload。
- User-owned external skill、`.codex/**`、`.github/**`、unrelated repository file。

Preservationはcontent、file type、mode、relative pathの不変を意味する。Generated `active/**`と`.agent/**`はhash fixture対象外とする。

## 4. 実装順序

```text
S00 gate admission
  -> S10 inventory lock
  -> S40A legacy Runtime retirement
  -> S40B shipped Target cutover
  -> S20 catalog validation tracer
  -> S25 ownership classifier / collision
  -> S30 no-follow apply / root rebind
  -> S35 version / retry admission
  -> S45 Fresh init
  -> S50 recognized update / init --force
  -> S55 obsolete prune / preservation
  -> S60 partial failure / forward retry
  -> S65 uninstall admission / dry-run
  -> S70 uninstall apply / preservation / retry
  -> S80 dogfood/package parity
  -> S85 installed consumer smoke
  -> S90 docs impact resolution
  -> S95 pre-final verification
  -> S99 three-reviewer final quality gate
  -> H10 IC-3 evidence handoff
```

各stepは一つの観測可能なbehaviorを`REDまたは事前観測 → bounded GREEN → verification → report draft → fresh reviewer → fix / re-review → result approval → commit候補または真正なapproved-no-op → post-commit clean check`で閉じる。後続stepの成功で前段failureを覆い隠さない。各stepのrequired outputはIssue reportの`Implementation Delegation Gate`、`Step Contract Closure`、`Test Contract Closure`、`Closure Coverage`、`Closure Delta`、`Reviewer Gate Status`、`Milestone / Commit Candidate Gate`である。

Runtime / CLI / infra / tests / scaffold behaviorは`dev-coder`、shipped docs / template / skill / workflow textは`doc-writer`へ委任する。Worker outputの`Ledger Note`はauthorityではなく、main orchestratorがDecision Ledgerへ採否を記録する。Codeを含むstepはfresh `code-reviewer`、docs-only stepはfresh `spec-reviewer`をpassする。Fail時はfindingだけを同じworkerまたは適切なworkerへ再委任し、focused verification後に別turnのfresh re-reviewを行う。親agentはrun-localなreport evidenceだけを直接更新し、production / test / shipped docsを直接修正しない。

各commit候補はそのstepだけのreview済み差分とreport evidenceを含む。Commit後に`git status --short`で意図しない差分がないことを確認し、`committed`または差分が本当に存在しない`approved-no-op`になるまで次stepへ進まない。Required closure、locked expectation、required値、spec linkの意味を変える必要が出た場合は実装を止め、本Planをamendしてfresh reviewへ戻る。

### S00 — Gate revalidationとlocal safety admission

作業:

- Branch、HEAD、upstream、worktree cleanliness、active context、dependency readinessを実測する。
- IC-1 / IC-2 ArtifactとEpic reportの`pass`、Issue 357〜359 final identityを再照合する。
- Formal `issue start`とStrict spec review evidenceを確認する。
- Dirty candidate docsがある場合はcheckout / reset / branch switchをしない。

Closure:

- §2.2の実装開始条件がすべてpassし、Issue reportにexact evidenceがある。
- 未承認のfinal Issue候補を作成していない。

Recovery:

- SHA / upstream mismatchは同期・再reviewへ戻す。
- Lifecycle failureはその原因を解消して`issue start`を再実行し、`--force`でdependencyを迂回しない。

Execution contract:

- Behavior / closure: implementation admissionだけを観測する。C360-AC-021、C360-SCOPE-001。
- depends_on: planning approval、push、formal start、Strict final review。unblocks: S10。
- Source / targets: canonical R/D/P/report、Epic IC artifacts / report、Git refs、active/dependency state。Production / test / provider assetは変更しない。
- Delegation / evidence: main orchestratorのread-only inspection step。Code REDはN/Aで、`active show`、`deps check`、`git status --short`、local/upstream SHA、Strict evidenceを代替証拠とする。
- Stop / output: 一件でも不一致ならreportへownerと再開条件を記録して停止する。ReportのS00 closure、Reviewer Gate Status、approved-no-op根拠を更新する。
- Reviewer / commit: planning `spec-reviewer`とStrict review evidenceを再利用せず実測する。Report差分があればcommit候補、差分がなければ確認対象とcommandを記録した`approved-no-op`。次step前にcleanを確認する。

### S10 — Exact inventory lock

作業:

- Provider / dogfood / package-data / installer init-update-uninstallのCurrent、obsolete、preserve pathを機械抽出する。
- 旧18 + legacy 3 skill、adapter / shim / config / workflow、357 planning backendのexact file inventoryを固定する。
- Historical package bytesまたは既存durable manifestから再現できるidentityだけを採用する。
- Current / obsolete / preserveのsame-path、ancestor / descendant overlapを検出する。
- Target二skillとretained CIのIssue 359 final bytesをlockする。
- `.gitignore`のprovider bytes / mode、version markerのvalid historical values、known `.agents/host-adapters/meta.json` bytesと各claimに対応するtarget identityをlockする。
- 各recognized versionのcanonical bytesと`spec-dock/scripts/spec-dock` + `spec-dock/.gitignore` anchor identityをhistorical provider / packageから再現し、exact allowlistへ固定する。

Closure:

- Pathは正規化済みrepository-relative POSIX file pathだけで、absolute、`..`、backslash、glob、directory entryがない。
- Historical identityのsourceがtraceableで、推測digestがない。
- Consumer manifest単独、`owner` field、workspace marker、version markerだけで個別file ownershipを証明できない。
- Version markerはcanonical `MAJOR.MINOR.PATCH\n`、allowlisted exact version、version-specific anchorsを満たし、newer targetのdowngradeを許可しない。
- Retained CIはCurrentだけに属する。

Recovery:

- Ownershipを再現できないobsolete candidateは削除対象にせず`preserve-and-block`へ分類し、Requirement / Design amendmentが必要なら実装を止める。

Execution contract:

- Behavior / closure: exact inventoryとhistorical evidenceの採否をlockする。C360-AC-001〜C360-AC-005、C360-AC-021、C360-RISK-UNKNOWN-OWNERSHIP。
- depends_on: S00。unblocks: S40A。
- Source / exact targets: provider / dogfood / package memberのread-only inventory、Issue 357〜359 reports、historical tags / archives、Issue report。Production sourceとmanifestはこのstepで変更しない。
- Delegation: `repo-analyst`のread-only調査へ委任し、main orchestratorが採否をreportへ記録する。推測digest、untraceable ownership、範囲外pathは採用しない。
- Concrete evidence seed: `rg --files src/spec_dock/assets spec-dock tests`とarchive / git evidenceからCurrent / obsolete / preserve / read-onlyを再構成し、same-path / ancestor overlap、二skill / CI bytes、version anchorsを照合する。
- Verification: `git diff --check`、`./spec-dock/scripts/spec-dock validate`、S10 inventoryの重複・trace source inspection。
- Stop / output: baseline drift、再現不能identity、preserve overlapはPlan/Design amendment blocker。Reportへexact inventory、source identity、採否、未採用candidateを記録する。
- Reviewer / commit: fresh `spec-reviewer`がRequirement / Designとのinventory整合を確認する。Fail後はread-only調査を再委任してfresh re-review。Report evidenceをcommit候補としpost-commit cleanを確認する。

### S40A — Legacy planning Runtime physical retirement

- Behavior / closure: 357 handoffのold-only Runtime / wrapper / import / registrationを物理削除し、retained Storage Coreを保つ。C360-AC-002、C360-RISK-OLD-ROUTE。
- depends_on: S10。unblocks: S40B。
- Source of truth: Requirement I360-RQ-003、Design §5.3〜5.4、Issue 357 reportの360 handoff。
- Exact target paths: `src/spec_dock/assets/spec_dock/scripts/spec-dock-chatgpt`、`scripts/authoring-pack/`、Runtimeの`cli/chatgpt_parser.py`、`cli/chatgpt_registry.py`、`commands/issue_planning.py`、`application/issue_planning.py`、`application/issue_planning_prompt.py`、`domain/issue_planning_candidate.py`、`domain/issue_planning_contracts.py`、`infra/issue_planning_*.py`、`presentation/issue_planning.py`、各layerの`authoring_pack/`、Design §5.4で[M]指定した`app.py`、`cli/bootstrap.py`、`application/contracts.py`、`application/ports.py`、S10 exact inventoryのold-only tests / fixtures。
- Allowed / forbidden: old-only symbol、callback、import、test / fixtureだけを削除する。`dispatch`、Storage Core bootstrap、generic Artifact port、retained use case / testの削除は禁止する。
- Implementation Delegation Gate: `dev-coder`へS10のexact Runtime/test delete manifestを渡す。Shared symbolのownerを判定できない場合は停止する。

具体テストケース一覧:

- `tc-s40a-route-absence`: removed command / parser / registry / import / wrapperへ到達できず、CLI helpにfallbackがない。現状で存在することを期待REDとする。
- `tc-s40a-retained-core`: selection、dependency lifecycle、Artifact、sync / validateのretained characterizationが削除前後でpassする。

- Bounded GREEN: old-only graphと専用test/fixtureを削除し、shared fileからold consumerだけを切る。
- Verification: `uv run pytest --run-full-regression tests/cli_runtime/test_storage_core_cli.py -q`。S40Aの検証は現行のStorage Core runtime deletion contractだけを対象とし、S40Bで追加する`test_distribution_cutover.py`へ先行依存しない。
- Refactor guardrail: retained Runtimeを移動・rename・再設計しない。
- Stop / output: retained test failureまたはS10外のshared dependency発見時は削除を止めDesign/Plan amendment。Reportへexact deletion list、retained symbols、RED/GREEN、worker noteを記録する。
- Reviewer / fix: fresh `code-reviewer`がshared-symbol safetyとfallback absenceを確認。Fail後fresh re-review。
- Commit candidate / clean: Runtime retirementと対応test/reportだけをcommitしclean確認。

### S40B — Shipped Target catalog physical cutover

- Behavior / closure: provider TargetをStorage Core / Authoring Kit / 二skill / retained CIへ縮小し、consumer mutationへ渡せる物理catalogにする。C360-AC-001、C360-AC-003、C360-AC-005、C360-RISK-OLD-ROUTE。
- depends_on: S40A。unblocks: S20。
- Source of truth: Requirement I360-RQ-002、004〜006、Design §4〜§5、Issue 358 / 359 handoff。
- Exact target paths: `src/spec_dock/assets/install_root/`、`src/spec_dock/assets/spec_dock/{docs,templates,scripts,system}/`、`src/spec_dock/assets/spec_dock/.gitignore`、`src/spec_dock/cli.py`のhard-coded gitignore fallback、`tests/unit/infra/test_authoring_kit_assets.py`、`tests/cli_runtime/test_storage_core_cli.py`、`tests/cli_runtime/test_distribution_cutover.py`。
- Allowed / forbidden: S10 exact obsolete inventoryを物理削除し、Target catalog testと必須`.gitignore` sourceを整える。Dogfood projectionの直接編集、node-local data、README / migration本文の最終編集、二skill semantic変更は禁止する。
- Implementation Delegation Gate: provider asset / scaffold behaviorを`dev-coder`へ委任する。Issue 359 final bytesとの不一致またはunknown provider fileを見つけたら停止する。

具体テストケース一覧:

- `tc-s40b-provider-catalog`: install-rootは二skill tree + `.github/workflows/ci.yml`だけ、template / docsはRequirement allowlistだけ、removed surfaceはproviderから不在となる。
- `tc-s40b-retained-identities`: 二skillがIssue 359 final sourceとbyte-identical、retained CIはStorage Coreのdeterministic commandだけ、`.gitignore`は物理package assetとして存在する。

- Bounded GREEN: exact provider additions/deletionsとfallback除去だけを行う。
- Verification: `uv run pytest --run-full-regression tests/unit/infra/test_authoring_kit_assets.py tests/cli_runtime/test_storage_core_cli.py tests/cli_runtime/test_distribution_cutover.py -q -k "target_catalog or removed_surface or retained or gitignore"`。
- Refactor guardrail: providerを正本とし、dogfoodへ別実装を作らない。
- Stop / output: Target allowlistの変更、unknown assetの削除、package-data amendmentが必要なら停止。Reportへcatalog diff、identity、absence evidence。
- Reviewer / fix: fresh `code-reviewer`がasset API、retained behavior、scopeを確認。Fail後fresh re-review。
- Commit candidate / clean: Provider catalog sliceだけをcommitしclean確認。

### S20 — Current / historical catalog validation tracer

- Behavior / closure: provider physical treeからCurrent catalogを導出し、historical-only manifestを公開plan interfaceで検証する。C360-AC-001、C360-AC-003、C360-AC-005、C360-AC-011、C360-RISK-UNKNOWN-OWNERSHIP。
- depends_on: S40B。unblocks: S25。
- Source of truth: Design §3、§4、§5、S10でlockしたexact inventory。
- Exact target paths: `src/spec_dock/managed_distribution.py` [A]、`src/spec_dock/assets/managed_distribution.json` [A]、`tests/unit/infra/test_managed_distribution.py` [A]。
- Allowed / forbidden: path grammar、physical Current derivation、historical record validationだけを実装する。Classifier、filesystem mutation、CLI接続、consumer asset削除、Current catalogのJSON全量複製は禁止する。
- Implementation Delegation Gate: `dev-coder`へ上記3 pathだけを委任する。Historical bytesを再現できない、Design schemaを変更する必要がある、またはprovider treeとpackage-dataが一致しない場合は停止する。

S20はS40Bのprovider物理cutover後に実行する。S10でlockしたbaselineのobsolete inventoryはmanifest recordのsource evidenceとして使うが、cutover前に残るobsolete provider pathをCurrent catalogとして扱わない。これにより、Design §4.2のCurrent / obsolete overlap拒否を緩めず、Current catalogはcutover済みphysical treeから導出する。

具体テストケース一覧:

- `tc-s20-public-catalog`: provider asset rootを`build_distribution_plan`のread-only seamへ渡すと、Current catalog、digest、modeが物理treeから導出され、build中のwriteが0である。Baselineではpublic seam / manifest不在を期待REDとする。
- `tc-s20-invalid-record`: absolute、`..`、backslash、glob、directory entry、bad digest、duplicate、Current / obsolete / preserve overlapを含むrecordをrejectする。
- `tc-s20-historical-source`: trace sourceを持たないdigestは採用せず、identityなしcandidateを`preserve-and-block`として表現する。

- Bounded GREEN: catalog/manifest modelとread-only buildの最小部分だけを追加する。
- Verification: `uv run pytest tests/unit/infra/test_managed_distribution.py -q -k "catalog or manifest or overlap"`。
- Refactor guardrail: CLIやoperation別moduleへvalidatorを複製しない。
- Required output / report: RED理由、GREEN command、exact record source、closure result、worker summary、changed files、unresolved risk。
- Reviewer / fix: fresh `code-reviewer`がauthority重複、path validation、deep-module boundaryを確認する。Fail時はfindingだけを同じworkerへ戻し、同じcommand後にfresh re-reviewする。
- Commit candidate / clean: S20の3 pathとreport evidenceだけをcommit候補にし、commit後`git status --short`がcleanになるまでS25へ進まない。

### S25 — Ownership classifier / Current collision

- Behavior / closure: operation × provenanceをmissing / identical / historical / unknownへ分類し、unknownをpreserve-and-blockする。C360-AC-009、C360-AC-010、C360-AC-010A、C360-AC-012、C360-RISK-UNKNOWN-OWNERSHIP、C360-RISK-DIAGNOSTIC-SANITATION。
- depends_on: S20。unblocks: S30。
- Source of truth: Requirement I360-RQ-008〜010、Design §4.2、§6.1〜6.2。
- Exact target paths: `src/spec_dock/managed_distribution.py`、`tests/unit/infra/test_managed_distribution.py`。
- Allowed / forbidden: read-only classifierとplan actionだけを追加する。Apply、prune、CLI operation分岐、consumer-side `owner` / marker単独のtrustは禁止する。
- Implementation Delegation Gate: `dev-coder`へ2 pathを委任する。Target pathのidentityをprovider-private recordで証明できなければ実装せずDesignへ戻す。

具体テストケース一覧:

- `tc-s25-current-collision`: retained CI、二skill、`spec` shortcutのmissing / current-identical / proven historical / non-identical unknownをcreate / adopt / upgrade / preserve+blockへ分ける。Unknown planはapply不可かつzero-write。
- `tc-s25-manifest-trust`: consumer manifest bytesだけ、`owner` fieldだけ、workspace/version markerだけではownershipを証明しない。Known manifest bytes + provider-private target path / identity + actual target一致だけを採用する。
- `tc-s25-obsolete`: Freshではobsolete-looking pathをunmanaged preserveし、recognized update / uninstallだけがproven exact historical identityをprune候補にする。
- `tc-s25-diagnostic-sanitize`: collision target contentにcredential風文字列とsource bytes、repository外rootに識別用absolute pathを置いても、plan diagnosticはoperation、repository-relative path、classification、reason、operator actionだけを返し、秘密候補・content・repository外absolute pathを含まない。

- Bounded GREEN: classifierとdiagnostic reasonを実装し、mutationは接続しない。
- Verification: `uv run pytest tests/unit/infra/test_managed_distribution.py -q -k "classifier or collision or ownership or diagnostic"`。
- Refactor guardrail: operation別の重複classifierを作らない。
- Stop conditions: exact pathだけで削除が必要、unknown collisionをwarn-and-continueしたくなる、またはmanifest trustを緩める必要がある場合。
- Required output / report: classification matrixのRED / GREEN、zero-write evidence、Decision Ledger note。
- Reviewer / fix: fresh `code-reviewer`。Failはbounded follow-up後にfresh re-review。
- Commit candidate / clean: S25のmodule/test/reportだけ。Commit後cleanを確認する。

### S30 — No-follow apply / repository root rebind

- Behavior / closure: validated planだけをdescriptor-relativeにapplyし、preflight後のroot / ancestor / target差し替えを検出して外部writeもpathname cleanupもしない。C360-AC-011、C360-RISK-ROOT-REBIND、C360-RISK-HARDLINK、C360-RISK-SYMLINK。
- depends_on: S25。unblocks: S35。
- Source of truth: Design §3.2、§6.2〜6.4、§13 Security。
- Exact target paths: `src/spec_dock/managed_distribution.py`、`tests/unit/infra/test_managed_distribution.py`。
- Allowed / forbidden: `PathIdentitySnapshot`、descriptor-relative no-follow rebind、held-parent staging、no-replace publish、bounded empty-parent cleanupを追加できる。Pathname-based cleanup、recursive / glob delete、symlink follow、`st_nlink > 1` mutationは禁止する。
- Implementation Delegation Gate: filesystem safetyを含むため`dev-coder`へ委任する。Platform上で安全なprimitiveを実証できなければbest-effortへ落とさずblock設計に戻る。

具体テストケース一覧:

- `tc-s30-root-rebind`: preflight後にrepository rootをrenameし、元pathnameへ別repositoryを配置する。Device / inode / `ctime_ns`差を検出し、両rootとreplacementを変更しない。
- `tc-s30-parent-target-race`: held parentまたはtargetをsymlink / 別inode / directoryへ差し替え、publish / replace / prune直前に停止する。
- `tc-s30-hardlink-no-replace`: hard link、destination出現、dangling symlinkをblockし、外部targetをfollowせずuser replacementをcleanupしない。

- Bounded GREEN: public `apply_distribution_plan`とidentity再検証だけを追加し、CLI operationは接続しない。
- Verification: `uv run pytest tests/unit/infra/test_managed_distribution.py -q -k "rebind or race or symlink or hard_link or no_replace"`。
- Refactor guardrail: test-only filesystem portをpublic interfaceへ追加しない。
- Stop conditions: root identityをpath stringだけで判定する必要、unsafe cleanup、repository外write/deleteの可能性が出た場合はcritical再評価。
- Required output / report: race setup、before/after snapshot、外部write 0、cleanup 0、platform exception。
- Reviewer / fix: fresh `code-reviewer`がTOCTOU、no-follow/no-replace、cleanup boundaryを確認。Fail後fresh re-review。
- Commit candidate / clean: S30のmodule/test/reportだけをcommitしclean確認。

### S35 — Version / retry marker admission

- Behavior / closure: canonical versionとoperation-specific retry markerだけをadmitし、unknown/newer/cross-root/dual stateを全mutation前に拒否する。C360-AC-010、C360-AC-011、C360-AC-015、C360-RISK-CROSS-ROOT-RETRY、C360-RISK-DOWNGRADE、C360-RISK-DUAL-MARKER、C360-RISK-POSTVERIFY。
- depends_on: S30。unblocks: S45。
- Source of truth: Design §7.3、§8.1。
- Exact target paths: `src/spec_dock/managed_distribution.py`、`src/spec_dock/cli.py`、`tests/unit/infra/test_managed_distribution.py`、`tests/unit/infra/test_init_update.py`、`tests/cli_runtime/test_distribution_cutover.py` [A]。
- Allowed / forbidden: admission / diagnostic / zero-write rejectionだけをCLIへ接続できる。Full Fresh / update / uninstall mutation、version range、downgrade、marker暗黙移行は禁止する。
- Implementation Delegation Gate: `dev-coder`へ5 pathを委任する。実行中package versionがcanonicalに確定できない場合はmutation routeをblockしたまま停止する。

具体テストケース一覧:

- `tc-s35-version`: no-follow regular/link-count-1のcanonical one-line ASCII versionについてolder / equalをadmitし、missing / malformed / BOM / CRLF / symlink / hard-link / unknown / newer / anchor mismatchをcommand別にzero-write blockする。
- `tc-s35-cross-root-replay`: repository Aのvalid distribution markerをBへcopyする。Package / operationが一致してもroot device / inode mismatchでBへのwriteを0にする。
- `tc-s35-marker-matrix`: distribution / uninstall / invalid / dual markerとoperationの組合せをDesign §8.1どおりに判定し、legacy uninstall marker schemaを変更しない。

- Bounded GREEN: version parser、anchor validation、marker schema / root binding、CLI admissionだけを実装する。
- Verification: `uv run pytest --run-full-regression tests/unit/infra/test_managed_distribution.py tests/unit/infra/test_init_update.py tests/cli_runtime/test_distribution_cutover.py -q -k "version or marker or force or cross_root"`。
- Refactor guardrail: version/marker validationをCLIへ複製しない。
- Stop conditions: version allowlistを推測する、root identityをmarkerへ格納できない、既存uninstall marker互換を破る必要がある場合。
- Required output / report: command別admission matrix、cross-root snapshot、zero-write、legacy marker compatibility。
- Reviewer / fix: fresh `code-reviewer`。Fail時は同一scopeへ修正委任しfresh re-review。
- Commit candidate / clean: S35の5 pathとreportだけをcommitしclean確認。

### S45 — Fresh init cutover

- Behavior / closure: Genuine FreshへTargetだけを配置し、unrelated / obsolete-looking external pathを保持し、Current collision時は全write前に停止する。C360-AC-001、C360-AC-005、C360-AC-006、C360-AC-010A。
- depends_on: S35。unblocks: S50。
- Source of truth: Requirement I360-RQ-002、007、009、Design §6.1、§7.1〜7.2。
- Exact target paths: `src/spec_dock/cli.py`、`src/spec_dock/managed_distribution.py`、`tests/unit/infra/test_init_update.py`、`tests/cli_runtime/test_distribution_cutover.py`。
- Allowed / forbidden: Fresh plan/apply、post-verify、root Workbench seed、generated stateだけを接続する。Obsolete prune、historical ownership推定、pre-existing Workbench rewriteは禁止する。
- Implementation Delegation Gate: `dev-coder`へ4 pathを委任する。Full preflight前のwriteまたはFreshでobsolete deleteが必要になれば停止する。

具体テストケース一覧:

- `tc-s45-empty-tracer`: empty temp repositoryにinitするとTarget catalog / bytes / modeと`spec` shortcutが揃い、再実行が収束する。Current実装の旧surface混入を期待REDとする。
- `tc-s45-unrelated`: unrelated file、obsolete skillと同名のexternal tree、native shim、unknown siblingのbefore/after identityが不変。
- `tc-s45-current-collision`: retained CI / 二skill / shortcutのidenticalはadoptし、non-identical file / symlink / directoryは保持して全write前にblockする。

- Bounded GREEN: Fresh entrypointを既存plan/applyへ接続する最小変更だけを行う。
- Verification: `uv run pytest --run-full-regression tests/unit/infra/test_init_update.py tests/cli_runtime/test_distribution_cutover.py -q -k "fresh"`。
- Refactor guardrail: Fresh専用classifierやcopy helperを増やさない。
- Stop / output: unknown collisionの上書き、obsolete prune、Target外asset配置が必要なら停止。ReportへFresh matrix、before/after、post-verify。
- Reviewer / fix: fresh `code-reviewer`。Fail後は同worker修正とfresh re-review。
- Commit candidate / clean: Fresh sliceとreportだけをcommitしclean確認。

### S50 — Recognized update / `init --force`

- Behavior / closure: recognized workspaceのCurrent assetとmanaged scaffoldをTargetへrefreshし、`init --force`を同一plan/resultへ束ねる。C360-AC-007、C360-AC-008、C360-AC-010A。
- depends_on: S45。unblocks: S55。
- Source of truth: Requirement I360-RQ-008〜010、Design §7.3。
- Exact target paths: `src/spec_dock/cli.py`、`src/spec_dock/managed_distribution.py`、`tests/unit/infra/test_init_update.py`、`tests/cli_runtime/test_distribution_cutover.py`。
- Allowed / forbidden: recognized Current create/adopt/upgradeとmanaged scaffold四root refreshを接続できる。Obsolete prune、`initiatives/**`、`.workbench/**`、unknown siblingのmutationは禁止する。
- Implementation Delegation Gate: `dev-coder`へ4 pathを委任する。Existing directoryだけをFreshへ誤降格する必要やWorkbench rewriteが必要なら停止する。

具体テストケース一覧:

- `tc-s50-recognized-update`: older / equal recognized workspaceのCurrent targetとmanaged scaffoldがproviderへ一致し、initiatives / Workbench / unknown siblingは不変。
- `tc-s50-force-parity`: recognized `init --force`のplan、diagnostic、resultが`update`と一致する。
- `tc-s50-unrecognized-force`: `spec-dock/` directoryだけのtarget、unknown/newer version、anchor mismatchはFreshへ降格せずzero-write blockする。

- Bounded GREEN: update / force entrypointを共通planへ接続し、obsolete actionはまだapplyしない。
- Verification: `uv run pytest --run-full-regression tests/unit/infra/test_init_update.py tests/cli_runtime/test_distribution_cutover.py -q -k "update and (current or managed_scaffold or force or workbench)"`。
- Refactor guardrail: updateとforceのadapter以外にbehavior差を作らない。
- Stop / output: preserve rootとのoverlap、unrecognized target mutation、Current identity rule変更が必要なら停止。Reportへparityとpreserve snapshot。
- Reviewer / fix: fresh `code-reviewer`。Fail後fresh re-review。
- Commit candidate / clean: recognized update sliceとreportだけをcommitしclean確認。

### S55 — Proven obsolete prune / unknown preservation

- Behavior / closure: proven historical obsolete exact fileだけをpruneし、modified / unknown / user-owned candidateを保持してoperation全体をblockする。C360-AC-007〜C360-AC-010、C360-AC-012、C360-RISK-UNKNOWN-OWNERSHIP。
- depends_on: S50。unblocks: S60。
- Source of truth: Requirement I360-RQ-009〜010、Design §4.2、§6、§7.3、§9、S10 exact inventory。
- Exact target paths: `src/spec_dock/managed_distribution.py`、`tests/unit/infra/test_managed_distribution.py`、`tests/cli_runtime/test_distribution_cutover.py`、Issue 358 preservation fixture paths under `tests/fixtures/authoring_kit/existing_issue/` [R/reuse; amendment only after review]。
- Allowed / forbidden: known exact file pruneとknown-empty bounded parent cleanupを追加できる。Prefix / glob / recursive delete、identityなし削除、preserve fixture rewriteは禁止する。
- Implementation Delegation Gate: `dev-coder`へmodule/testだけを委任する。S10 inventory外のpathやreproducible identityなしcandidateは実装せずblock evidenceへ回す。

具体テストケース一覧:

- `tc-s55-proven-obsolete`: direct known digestとtrusted manifest + target identityのpositive caseだけがpruneされる。
- `tc-s55-modified-unknown`: modified skill/profile/shim、invalid manifest、unknown siblingはbefore/after不変かつ全mutation前blockとなる。
- `tc-s55-preservation`: heavy Report、R/D/P、Artifact、Discussion、ADR、`.assurance.json`、opaque / profile-derived fileのpath/type/content/mode snapshotが不変。

- Bounded GREEN: obsolete action applyとbounded empty-parent cleanupだけを追加する。
- Verification: `uv run pytest --run-full-regression tests/unit/infra/test_managed_distribution.py tests/cli_runtime/test_distribution_cutover.py -q -k "obsolete or preserve or modified or unknown"`。
- Refactor guardrail: preserve fixtureを期待値へ合わせて改変しない。
- Stop / output: ownership不明の自動削除、directory delete、preserve mutationが必要なら停止。Reportへpruned / preserved exact paths、snapshot hash、diagnostic。
- Reviewer / fix: fresh `code-reviewer`がdata-loss boundaryを確認。Fail後fresh re-review。
- Commit candidate / clean: prune/preserve sliceとreportだけをcommitしclean確認。

### S60 — Partial failure / same-package forward retry

- Behavior / closure: phase failureをdurable markerへ記録し、同じroot / package / operationだけがidempotentに収束し、post-verify前にversion / markerを成功確定しない。C360-AC-008、C360-AC-015、C360-RISK-ROOT-REBIND、C360-RISK-CROSS-ROOT-RETRY、C360-RISK-POSTVERIFY、C360-RISK-DIAGNOSTIC-SANITATION。
- depends_on: S55。unblocks: S65。
- Source of truth: Requirement I360-RQ-012〜013、Design §6.3、§8。
- Exact target paths: `src/spec_dock/managed_distribution.py`、`src/spec_dock/cli.py`、`tests/unit/infra/test_managed_distribution.py`、`tests/cli_runtime/test_distribution_cutover.py`。
- Allowed / forbidden: init/update markerのatomic phase update、fault result、same-package forward retryを追加できる。Backward package rollback、old workflow再配置、cross-root replay、uninstall marker統合は禁止する。
- Implementation Delegation Gate: `dev-coder`へ4 pathを委任する。Filesystem error後にphaseを一意に記録できない、またはuser replacement cleanupが必要なら停止する。

具体テストケース一覧:

- `tc-s60-phase-fault`: scaffold refresh、Current copy、obsolete prune、post-verify直前/直後にfaultを注入し、last completed phase、pending actions、retry commandを返す。
- `tc-s60-root-rebind-retry`: failure後にroot / parent identityを差し替えるとretryはzero-write blockし、元pathnameのreplacementをcleanupしない。
- `tc-s60-cross-root-replay`: AのmarkerをBへreplay、別package / operationでreplayしてもBへwriteしない。Aのmarker/root identityは保持する。
- `tc-s60-postverify`: post-verify failureではversion未更新、marker保持、preserve snapshot不変。同じroot/package/operationの再実行だけがcompleteへ収束する。
- `tc-s60-diagnostic-sanitize`: fault対象にcredential風文字列、source content、repository外absolute pathを含めても、text / JSON failure resultはoperation、relative path、classification、reason、operator action、retry command、last completed phaseだけを公開する。

- Bounded GREEN: init/update recovery phaseとmarker lifecycleだけを実装する。
- Verification: `uv run pytest --run-full-regression tests/unit/infra/test_managed_distribution.py tests/cli_runtime/test_distribution_cutover.py -q -k "retry or fault or rebind or cross_root or post_verify or diagnostic"`。
- Refactor guardrail: operation全体をatomic/rollback可能と表現しない。
- Stop / output: markerにabsolute path/credentialが必要、root identityを安定検証できない、preserve setが変わる場合。Reportへfault point別result、convergence、repository B write 0を記録する。
- Reviewer / fix: fresh `code-reviewer`がrecovery、diagnostic sanitation、root bindingを確認。Fail後fresh re-review。
- Commit candidate / clean: recovery sliceとreportだけをcommitしclean確認。

### S65 — Uninstall admission / dry-run

- Behavior / closure: uninstallはdefault dry-runで全actionを表示し、apply mode / version / markerがinvalidならremoval前に停止する。C360-AC-013、C360-RISK-DUAL-MARKER。
- depends_on: S60。unblocks: S70。
- Source of truth: Requirement I360-RQ-011〜013、Design §7.4、§8.1。
- Exact target paths: `src/spec_dock/cli.py`、`src/spec_dock/managed_distribution.py`、`tests/cli_runtime/test_uninstall.py`、`tests/cli_runtime/test_distribution_cutover.py`。
- Allowed / forbidden: uninstall plan/render/admissionだけを共通classifierへ接続できる。Remove action実行、marker変更、spec deletionは禁止する。
- Implementation Delegation Gate: `dev-coder`へ4 pathを委任する。Existing public dry-runやlegacy marker rerunを破る必要があれば停止する。

具体テストケース一覧:

- `tc-s65-default-dry-run`: flagなしではCurrent / legacy / preserve actionを表示するがfilesystem writeは0。
- `tc-s65-mode-admission`: `--apply`はkeep/remove exactly-oneを要求し、missing/bothをzero-write rejectする。
- `tc-s65-version-marker`: newer / invalid / anchor mismatch、distribution / dual / invalid markerをblockし、valid legacy uninstall markerだけはversion欠損partial rerunとしてadmitする。

- Bounded GREEN: admissionとrenderだけを実装しremove callbackを呼ばない。
- Verification: `uv run pytest --run-full-regression tests/cli_runtime/test_uninstall.py tests/cli_runtime/test_distribution_cutover.py -q -k "dry_run or admission or marker"`。
- Refactor guardrail: uninstall専用ownership classifierを作らない。
- Stop / output: dry-runでwrite、ambiguous specs mode、marker暗黙変換が必要なら停止。Reportへaction listとzero-write evidence。
- Reviewer / fix: fresh `code-reviewer`。Fail後fresh re-review。
- Commit candidate / clean: admission sliceとreportだけをcommitしclean確認。

### S70 — Uninstall apply / preservation / retry

- Behavior / closure: explicit applyでproven Current / legacyだけを除去し、keep/remove boundary、unknown preservation、legacy marker-last retryを収束させる。C360-AC-009〜C360-AC-015、C360-RISK-UNKNOWN-OWNERSHIP、C360-RISK-POSTVERIFY、C360-RISK-SPECS。
- depends_on: S65。unblocks: S80。
- Source of truth: Requirement I360-RQ-009〜013、Design §6、§7.4、§8〜9。
- Exact target paths: `src/spec_dock/cli.py`、`src/spec_dock/managed_distribution.py`、`tests/cli_runtime/test_uninstall.py`、`tests/cli_runtime/test_distribution_cutover.py`、Issue 358 preservation fixture [R/reuse]。
- Allowed / forbidden: proven exact Current / legacy、generated active / agent state、explicit remove-specs targetだけを除去できる。Unknown/modified external asset、keep-specs時の`initiatives/**`、marker先行削除、recursive unknown directory deletionは禁止する。
- Implementation Delegation Gate: `dev-coder`へ4 code/test pathを委任する。Spec history boundaryまたはlegacy marker schemaを変更する必要があれば停止する。

具体テストケース一覧:

- `tc-s70-current-legacy`: current / legacy / mixed / partial / repeated consumerでproven actionだけが除去され、unknown candidateがあれば全mutation前block。
- `tc-s70-keep-remove`: keep-specsではfull preservation snapshot不変、remove-specsだけが明示spec historyを削除する。
- `tc-s70-marker-last`: 各remove phaseのfault後もlegacy markerが残り、rerunで収束し、全post-verify後に最後に除去される。
- `tc-s70-no-cleanup`: modified file、symlink、hard link、exact directoryを保持し、known empty boundary以外をcleanupしない。

- Bounded GREEN: validated uninstall planのapplyとlegacy retryだけを接続する。
- Verification: `uv run pytest --run-full-regression tests/cli_runtime/test_uninstall.py tests/cli_runtime/test_distribution_cutover.py -q -k "keep_specs or remove_specs or legacy or repeated or partial or retry"`。
- Refactor guardrail: distribution retry markerとuninstall markerを統合しない。
- Stop / output: keep-specs data mutation、unknown deletion、misleading success、marker先行削除が必要なら停止。Reportへbefore/after preservation、failure/retry、removed/preserved list。
- Reviewer / fix: fresh `code-reviewer`がdata-loss、idempotence、marker orderingを確認。Fail後fresh re-review。
- Commit candidate / clean: uninstall apply sliceとreportだけをcommitしclean確認。

### S80 — Dogfood projectionとpackage parity

- Behavior / closure: providerを唯一の正本としてdogfood、wheel、sdist、Fresh、Updatedのcatalog / bytes / modeを一致させ、removed / prohibited payloadを不在にする。C360-AC-001、C360-AC-003、C360-AC-016、C360-AC-017、C360-RISK-PACKAGE-FALLBACK。
- depends_on: S70。unblocks: S85。
- Source of truth: Requirement I360-RQ-014、Design §10、provider physical tree。
- Exact target paths: provider asset tree [R]、dogfood `spec-dock/{docs,templates,scripts,system}/`とrepo-local managed tooling [generated projection]、`tests/cli_runtime/test_distribution_cutover.py`、必要なpackage parity assertion in `tests/unit/infra/test_init_update.py`。Package-data不足が実証された場合だけPlan amendment後に`pyproject.toml`を[M]し、`setup.py`は[R]のままにする。
- Allowed / forbidden: provider commandによるdogfood sync、isolated archive build / inspection、archive由来consumer testを追加できる。Dogfoodの手動source edit、working checkout fallback、consumer側manual copyは禁止する。
- Implementation Delegation Gate: `dev-coder`へparity test / projection更新を委任する。Archive member不足時は原因をprovider/package-data ownerへ戻し、consumerを手で合わせない。

具体テストケース一覧:

- `tc-s80-provider-dogfood`: Target catalog、bytes、executable modeがsurface別exclusionを除き一致する。
- `tc-s80-archive-consumer`: wheel / sdistを別temp環境へinstallし、そのarchive bytesだけからFresh / Updated consumerを作ってprovider parityを満たす。
- `tc-s80-prohibited-scan`: removed asset、binary、cache、secret-like file、local absolute path、interaction log、unexpected hidden payloadがarchiveにもconsumerにもない。

- Bounded GREEN: provider projectionとparity/assertionだけを修正する。
- Verification: `uv build`、`uv run pytest --run-full-regression tests/unit/infra/test_init_update.py tests/cli_runtime/test_distribution_cutover.py -q -k "parity or archive or package or removed_surface"`。
- Refactor guardrail: Blanket directory equalityでpreserve / generated surfaceを誤比較しない。
- Stop / output: archiveがcheckoutを参照する、prohibited content、unexpected mode差、manual consumer repairが必要なら停止。Reportへarchive hash/member catalog、parity matrix、scan結果。
- Reviewer / fix: fresh `code-reviewer`。Fail後fresh re-review。
- Commit candidate / clean: projection/parity/test/reportだけをcommitしclean確認。

### S85 — Installed consumer smoke

- Behavior / closure: package由来consumerで357〜359のretained契約が一つの利用経路として動き、external Intelligenceと旧workflowがなくてもCoreを利用できる。C360-AC-018、C360-RISK-OLD-ROUTE。
- depends_on: S80。unblocks: S90。
- Source of truth: Requirement I360-RQ-015、Design §12.4、Issue 357〜359 accepted contracts。
- Exact target paths: `tests/cli_runtime/test_distribution_cutover.py`と必要最小限のexisting Storage Core / Authoring Kit / Issue 359 test assertion。Production変更は、原因が360 integration seamである場合だけ該当owner pathへ限定する。
- Allowed / forbidden: archive-installed end-to-end smokeとstubbed GitHub adapterを追加できる。Live GitHub mutation、357〜359 semantic redesign、旧fallback復活は禁止する。
- Implementation Delegation Gate: `dev-coder`へinstalled smokeを委任する。Upstream slice defectならowner、evidence、最小integration fix範囲をreportへ出して停止する。

具体テストケース一覧:

- `tc-s85-lifecycle`: selection-only `active set`、dependency-only `issue start`、thin `issue finish`のclose / clear / syncをstubbed GitHub境界で観測する。
- `tc-s85-authoring`: omitted / explicit blank / typed Artifact、Historical recognition、`artifact import file`、Fresh thin / existing heavy Reportを確認する。
- `tc-s85-skills`: 二skillがdiscoverable、旧skill fallbackが不在、external `grilling` / `domain-modeling`欠損でもStorage Coreのinstall/useが成功する。
- `tc-s85-core`: installed consumerで`validate`とlocal `sync`がpassする。

- Bounded GREEN: test harnessと360 integration seamの最小修正だけ。
- Verification: `uv run pytest --run-full-regression tests/cli_runtime/test_distribution_cutover.py tests/cli_runtime/test_storage_core_cli.py -q -k "installed or smoke or lifecycle or artifact or skill"`。
- Refactor guardrail: live service依存やproduct-owned intelligenceを導入しない。
- Stop / output: 357〜359契約変更が必要、live mutationが必要、旧routeしか動かない場合。Reportへarchive identity、scenario result、upstream owner判断。
- Reviewer / fix: fresh `code-reviewer`。Fail後fresh re-review。
- Commit candidate / clean: installed smoke/integration fix/reportだけをcommitしclean確認。

### S90 — Docs impact resolution / docs refresh

- Behavior / closure: Current docs、help、migration、retained Markdownをactual Target / ownership / recovery contractへ一致させ、Historical以外から旧routeへのlive導線をなくす。C360-AC-004、C360-AC-019、C360-AC-020、C360-RISK-HISTORICAL-SCAN、C360-RISK-OLD-ROUTE。
- depends_on: S85。unblocks: S95。
- Source of truth: Requirement I360-RQ-005、016、Design §11、actual CLI help / manifest / recovery result。
- Exact target paths: repository root `README.md`、provider `src/spec_dock/assets/spec_dock/docs/{README,guide,migration}.md`、retained `scripts/README.md`、`system/**/*.md`、`templates/README.md`、root / scope Workbench README、対応dogfood projection、docs assertion in `tests/cli_runtime/test_distribution_cutover.py` / `tests/unit/infra/test_authoring_kit_assets.py`。
- Allowed / forbidden: Current wording/link/migrationとpath-aware scanを更新できる。Historical evidence、node-local canonical docs、R/D/P contract、旧route compatibility wrapperは禁止する。
- Implementation Delegation Gate: shipped docsを`doc-writer`へ委任し、code/test assertionが必要なら別のbounded `dev-coder` taskへ分ける。実装とdocsが不一致ならdocsで曖昧化せずowner stepへ戻す。

具体テストケース一覧:

- `tc-s90-entrypoints`: root README、installed docs README / guideからmigrationへ到達し、actual help、Target inventory、two-skill / external Intelligence、managed/preserve boundary、dry-run/retryを正しく説明する。
- `tc-s90-retained-markdown`: retained scripts/system/templates/Workbench Markdownのlive linkとCurrent語彙をpath-aware scanし、Historical pageの説明語を誤検出・改変しない。
- `tc-s90-removed-links`: removed command/path/skill/workflowへのCurrent live linkが0。

- Bounded GREEN: provider docs sourceを更新してprojectionし、必要なstructural assertionだけを追加する。
- Verification: `uv run pytest --run-full-regression tests/cli_runtime/test_distribution_cutover.py tests/unit/infra/test_authoring_kit_assets.py -q -k "docs or markdown or vocabulary or migration or link"`、actual CLI `--help`とのinspection。
- Refactor guardrail: Historical evidenceを現行wordingへ書換えない。
- Stop / output: docsが未実装behaviorを約束する、broken link、Current/Historicalを区別できない場合。Reportへdocs impact、changed entrypoint、scan / help evidence。
- Reviewer / fix: fresh `spec-reviewer`がRequirement / Design / actual behaviorとのdocs alignmentを確認。Code assertionを含む場合は該当diffにfresh `code-reviewer`も必要。Fail後は適切なworkerへ修正委任しfresh re-review。
- Commit candidate / clean: docs、projection、必要なassertion、reportだけをcommitしclean確認。Docs impact `none`は本Issueでは不可。

### S95 — Pre-final verification barrier

- Behavior / closure: 全behavior sliceのrequired verificationを統合し、S99 reviewへ渡すcleanなissue-wide candidateとcomplete report ledgerを作る。C360-AC-001〜022、全C360-RISK row。
- depends_on: S90と全stepの`committed` / legitimate `approved-no-op`。unblocks: S99。
- Source / exact targets: issue-wide implementation / tests / provider / dogfood / package / docs [R]、Issue report [M]。新しいproduct behaviorを追加しない。
- Delegation: `qa-reviewer`ではなくmain orchestratorがcommand実行とledger集約だけを行う。Failure修正はowner stepのworkerへ戻し、そのstep reviewerを再実行する。

必須検証:

1. `make lint`
2. `uv run pytest`
3. `uv run pytest --run-full-regression`
4. `uv build`とS80 archive / consumer parity command
5. Removed import / help / docs / asset absence scan
6. Markdown link / Current vocabulary scan
7. Preservation / fault / retry / diagnostic sanitation matrix
8. `./spec-dock/scripts/spec-dock validate`
9. `git diff --check`と`git status --short`

- Concrete evidence seed: 各commandのexit、test counts、archive hashes、consumer matrix、Target/obsolete/preserve inventory、before/after preservation hashをIssue reportのclosure IDsへ結ぶ。
- Close condition: required verificationがpassし、skip / platform exceptionは理由・代替証拠・residual risk付きでS99 reviewerが判定可能。Unknown obsolete、package parity未確認、preservation failure、dirty worktreeを残さない。
- Reviewer / fix: このstep自体はS99三者reviewの入力準備でありreview代替ではない。Failureは該当owner stepへ戻す。
- Commit candidate / clean: 実装差分のcatch-up commitは禁止。Report ledger差分だけをcommit候補とし、全step commitとpost-commit cleanを確認する。

### S99 — Three-reviewer final quality gate

- Behavior / closure: issue全体のテスト十分性、統合diff、仕様達成を独立三者でpassさせ、final report ledger / final commitを閉じる。C360-AC-001〜022、C360-SCOPE-001〜002、全C360-RISK row。
- depends_on: S95。unblocks: H10。
- Source / exact targets: requirement / design / plan / report、issue-wide implementation diff、tests、docs、S95 evidence [R]。Reviewer finding修正時だけowner stepのallowed pathを再開する。
- Delegation / required reviews:
  1. fresh `qa-reviewer`: risk-calibrated test obligation、integration test不足、skip / platform risk。
  2. fresh issue-wide `code-reviewer`: baselineからの統合diff、責務境界、data loss / recovery / regression / maintainability。
  3. fresh `spec-reviewer`: R/D/P/report、implementation、tests、docs、全required closureの一致。

具体確認:

- `tc-s99-closure-ledger`: required closure IDがStep Contract / Test Contract / Closure Coverageでpassまたは真正なapproved-no-opへ一対一で追跡でき、open Closure Deltaがない。
- `tc-s99-milestones`: 全implementation stepがdelegation gate、per-step reviewer pass、commitまたはapproved-no-op、post-commit clean evidenceを持つ。
- `tc-s99-no-self-approval`: IC-3、Issue/Epic close、release、未承認final Issueのpass / 実施をreportが自己宣言しない。

- Fix / re-review: 一者でもfailならfindingを該当workerへbounded再委任し、影響stepのverification / reviewerと失敗したfinal reviewerをfreshに再実行する。Waived / provisional / unavailableをpass扱いしない。
- Required output / report: Final QA Gate、Final Code Review Gate、Final Spec Review Gate、全closure、final commit scope、post-commit external evidenceの記録先。
- Commit candidate / clean: 三者pass後にfinal report ledgerだけを含むfinal commitを作る。未commit implementationを救済しない。Final hashとclean checkはcommit後のexternal delivery evidenceへ残す。

### H10 — IC-3 evidence handoff

- Behavior / closure: S99でcommit済みのIssue reportとexact implementation identityをEpic ownerへ渡し、IC-3判定可能にする。C360-AC-022。
- depends_on: S99三者passとfinal commit / clean。unblocks: Epic-owned IC-3 decision only。
- Source / targets: committed Issue reportとexternal final hash/check evidence [R]。Issue / Epic canonical docs、implementation、Epic reportは本stepで変更しない。
- Delegation / evidence: main orchestratorのread-only handoff。Code REDはN/Aで、受領対象、exact SHA、report anchor、residual riskを一箇所から辿れることをinspectionする。
- Stop / output: IC-3 pass、Issue / Epic close、release、PR merge、未承認final Issue作成を自己宣言・実行しない。Epic ownerが必要なら別scopeでEpic reportを更新する。
- Reviewer / commit: S99 final `spec-reviewer`がhandoff input completenessを確認済みであることを要求する。本stepはno repository mutationの`approved-no-op`で、external delivery evidenceだけを残す。

## 5. Consumer matrix

| Operation | Scenario | Expected result | Closure |
|---|---|---|---|
| Fresh | empty | exact Targetだけを配置 | C360-AC-001、006 |
| Fresh | unrelated / obsolete同名external | unrelatedを保持しobsolete pruneなし | C360-AC-006、009 |
| Fresh | Current-identical | no-op adoption | C360-AC-010A |
| Fresh | non-identical Current collision | preserve-and-block before write | C360-AC-010A、012 |
| Update | unmodified historical | Target refresh、proven obsolete prune、preserve不変 | C360-AC-007〜010 |
| Update | modified obsolete / Current | preserve-and-block before write | C360-AC-009、012 |
| Update | unknown sibling / arbitrary agent or GitHub file | preserve | C360-AC-009 |
| Update | managed scaffold local modification | installer-ownedとしてrefresh | C360-AC-010 |
| Update | node-local heavy Report / historical evidence | byte-preserve | C360-AC-008 |
| Update | partial marker | forward retryで収束 | C360-AC-015 |
| `init --force` | recognized workspace | Updateと同じplan / result | C360-AC-007、010A |
| `init --force` | directoryだけのunrecognized target | Freshへ誤降格せずzero-write block | C360-AC-010、011 |
| Update | valid distribution marker / same root | Same package / operationだけforward retry | C360-AC-015 |
| Update | marker root mismatch / cross-root replay | preserve-and-block before write | C360-RISK-CROSS-ROOT-RETRY |
| Update | uninstall / invalid / dual marker | preserve-and-block before write | C360-RISK-DUAL-MARKER |
| Uninstall | dry-run | action listのみ、zero-write | C360-AC-013 |
| Uninstall | apply without specs mode | fail before write | C360-AC-013 |
| Uninstall | `--keep-specs` | tooling除去、spec history保持 | C360-AC-014 |
| Uninstall | `--remove-specs` | 明示時だけspec history除去 | C360-AC-014 |
| Uninstall | legacy modified / unknown | preserve-and-block | C360-AC-009、012 |
| Uninstall | repeated / partial | idempotentに収束 | C360-AC-013、015 |
| Uninstall | distribution / invalid / dual marker | preserve-and-block before write | C360-RISK-DUAL-MARKER |

## 6. Path safety matrix

| Case | Expected | Closure |
|---|---|---|
| absolute / `..` / backslash / glob manifest path | manifest validation fail | C360-AC-011 |
| directory-like obsolete entry | manifest validation fail | C360-AC-011 |
| parent symlink / non-directory | preflight block | C360-RISK-SYMLINK |
| exact obsolete symlink | link自体をno-follow分類しknown identity必須 | C360-RISK-SYMLINK |
| exact obsolete directory | block、recursive delete禁止 | C360-AC-011 |
| Current / obsolete same path or ancestor overlap | manifest validation fail | C360-AC-011 |
| mutation target hard link | block。read-only identical adoptionだけ許可 | C360-RISK-HARDLINK |
| preflight後のrepository root rename / replacement | root device / inode / `ctime_ns`再照合で検出し、replacement / external rootへのwriteもpathname cleanupも0 | C360-RISK-ROOT-REBIND |
| preflight後のparent / target identity差し替え | 再bindで検出し、外部write / pathname cleanupなしで停止 | C360-RISK-ROOT-REBIND |
| 別rootからcopyしたvalid retry marker | root identity mismatchでzero-write block | C360-RISK-CROSS-ROOT-RETRY |
| unknown ownership | preserve-and-block before any mutation | C360-RISK-UNKNOWN-OWNERSHIP |

## 7. 順序とscope制約

- S10前にmanifest / prune logicを書かない。
- 各S20〜S90 stepのfirst REDまたは明示した代替観測が期待どおりになる前に、そのstepのproduction / shipped-doc behaviorを変更しない。
- S30の共通apply safetyとS35のadmissionをclosedにする前にFresh / update / uninstall mutationを接続しない。
- S45 / S50 / S55 / S60 / S65 / S70は同じ`managed_distribution` plan / classifier / applyを使う。
- S40A / S40Bのremoved absenceとTarget catalogがclosedになる前にconsumer mutationまたはpackage parityへ進まない。
- S80はarchiveからconsumerを作り、working checkoutへfallbackしない。
- S90 docs gateとS95 verificationを閉じる前にS99を開始しない。
- S99のqa / issue-wide code / spec三者passとfinal commitを閉じる前にH10を開始しない。
- H10は既存evidenceのread-only handoffだけを行い、IC-3 passを自己宣言しない。
- 357 Storage Core、358 Authoring Kit、359 skill semanticsのdefectやExternal capability gapをsilent scope expansionしない。
- Publication、merge、Issue close、Epic close、最終Issue node作成は対象外とする。

## 8. Spec-Locked Closure Index

この索引はテスト実装の全量一覧ではなく、変更してはならない仕様期待、観測可能な状態、guard対象、step-local closureを固定する。全rowは`required=yes`である。Row削除、locked expectation / required / spec linkの意味変更はPlan amendmentとfresh reviewを必要とする。実行結果はIssue reportの同じClosure IDを持つ`Step Contract Closure`、`Test Contract Closure`、`Closure Coverage`へ記録する。

### 8.1 Acceptance closure

| Closure ID | Required | Spec link | Observable input / state | Locked expectation | Bug class guarded | Evidence level | Owner step | Step-local close condition | Verification / report path |
|---|---|---|---|---|---|---|---|---|---|
| C360-AC-001 | yes | I360-AC-001 / RQ-002 | Fresh Target catalog | 二skill、retained CI、Storage Core / Kitだけ | legacy asset再配布 | filesystem + archive | S40B / S45 / S80 | 全surface catalog一致 | S45 / S80 commands; report Closure Coverage |
| C360-AC-002 | yes | I360-AC-002 / RQ-003 | import/help/file graph | 357 old planning backend不在、Core pass | fallback / shared-symbol破壊 | CLI + regression | S40A | removed absenceとretained test pass | S40A command; report Test Contract Closure |
| C360-AC-003 | yes | I360-AC-003 / RQ-004 | provider/archive template catalog | Current scope docs + Workbench + 六Artifactだけ | obsolete template混入 | catalog + archive | S40B / S80 | providerとarchiveのallowlist一致 | S40B / S80 commands |
| C360-AC-004 | yes | I360-AC-004 / RQ-005 | Current docs link graph | removed live link 0、Historicalだけ明示説明 | stale route案内 | docs scan | S90 | link / vocabulary inspection pass | S90 command; report Docs Gate |
| C360-AC-005 | yes | I360-AC-005 / RQ-006 | managed skill / adapter inventory | Target二skill、旧18 + legacy 3 / adapter / wrapper不在 | old skill fallback | catalog + consumer | S40B / S45 / S50 | provider / Fresh / Updatedのinventory一致 | S40B / S45 / S50 commands |
| C360-AC-006 | yes | I360-AC-006 / RQ-007 | empty / unrelated Fresh | Target配置、unrelated不変、obsolete pruneなし、再実行収束 | Fresh data loss | filesystem CLI | S45 | Fresh matrix全case pass | S45 command; before/after report |
| C360-AC-007 | yes | I360-AC-007 / RQ-008 | unmodified legacy workspace | proven obsolete prune、Target refresh | legacy残存 / over-delete | filesystem CLI | S50 / S55 | known legacy matrix pass | S50 / S55 commands |
| C360-AC-008 | yes | I360-AC-008 / RQ-010 | full preservation fixture | path/type/content/mode不変 | historical evidence破壊 | snapshot integration | S50 / S55 / S60 | before/after equality | S55 / S60 commands; report hashes |
| C360-AC-009 | yes | I360-AC-009 / RQ-009〜010 | unknown sibling / external / modified path | 自動mutation 0、必要時全operation block | user-owned deletion | unit + filesystem | S25 / S55 / S70 | negative matrixとsnapshot pass | respective commands |
| C360-AC-010 | yes | I360-AC-010 / RQ-009 | operation × provenance cases | create/adopt/upgrade/prune/preserve/blockを一意分類 | ownership spoof | unit + CLI | S25 / S55 / S70 | positive / negative classifier pass | S25 command; report matrix |
| C360-AC-010A | yes | I360-AC-010A / RQ-008〜009 | CI / 二skill / shortcut collision | missing/identical/historical/unknownの所定action | same-path overwrite | unit + Fresh/update | S25 / S45 / S50 | reusable Current matrix pass | S25 / S45 / S50 commands |
| C360-AC-011 | yes | I360-AC-011 / RQ-012 | unsafe path / parent / directory / overlap | 全write前fail | path escape / recursive delete | unit fault | S20 / S30 / S35 | unsafe matrix write 0 | S20 / S30 / S35 commands |
| C360-AC-012 | yes | I360-AC-012 / RQ-009 | modified / unproven obsolete | preserve + diagnostic + block、success非表示 | misleading cutover success | unit + CLI | S25 / S55 / S70 | preserved identityとblocked result | S55 / S70 commands |
| C360-AC-013 | yes | I360-AC-013 / RQ-011 | uninstall dry/current/legacy/mixed/partial/repeated | 所定classificationと収束 | uninstall drift | CLI integration | S65 / S70 | uninstall matrix pass | S65 / S70 commands |
| C360-AC-014 | yes | I360-AC-014 / RQ-011 | keep/remove specs fixture | keepは不変、removeだけ明示削除 | spec history loss | snapshot integration | S70 | both mode結果とsnapshot pass | S70 command; report hashes |
| C360-AC-015 | yes | I360-AC-015 / RQ-013 | phase fault / retry | phase診断、same-root convergence、preserve不変 | partial corruption | fault integration | S60 / S70 | 全fault pointが所定result | S60 / S70 commands |
| C360-AC-016 | yes | I360-AC-016 / RQ-014 | provider/dogfood/archive/consumers | catalog/bytes/mode parity、removed不在 | packaging drift | archive integration | S80 | 全pair parity pass | S80 build / test; report hashes |
| C360-AC-017 | yes | I360-AC-017 / RQ-014 | wheel / sdist content | prohibited payload 0 | secret/cache/log混入 | archive scan | S80 | scan pass | S80 command; report member list |
| C360-AC-018 | yes | I360-AC-018 / RQ-015 | archive-installed consumer | 357〜359 smoke pass、旧route / external dependency不要 | integration regression | end-to-end | S85 | 全scenario pass | S85 command; report matrix |
| C360-AC-019 | yes | I360-AC-019 / RQ-016 | README/help/migration | actual behaviorと一致し相互link | misleading migration | docs + CLI inspect | S90 | entrypoint / help comparison pass | S90 command; report Docs Gate |
| C360-AC-020 | yes | I360-AC-020 / RQ-005 | retained Markdown | removed Current link/command/語彙 0 | stale operational guidance | path-aware docs scan | S90 | scan pass、Historical除外適正 | S90 command |
| C360-AC-021 | yes | I360-AC-021 / RQ-001 | IC / lifecycle / review state | 全gate独立passまでimplementation block | self-admission | lifecycle evidence | S00 / S99 | exact evidenceとno bypass | S00 commands; report Reviewer Gate |
| C360-AC-022 | yes | I360-AC-022 | final Issue report / handoff | exact evidence、residual risk、IC-3 input、自己承認なし | incomplete handoff | ledger + inspect | S99 / H10 | 三者pass、final ledger、read-only handoff | S99 reviews; external H10 evidence |

### 8.2 Safety / scope closure

| Closure ID | Required | Spec link | Observable input / state | Locked expectation | Bug class guarded | Evidence level | Owner step | Step-local close condition | Verification / report path |
|---|---|---|---|---|---|---|---|---|---|
| C360-RISK-ROOT-REBIND | yes | Design §6.3 | preflight後root / parent replacement | device/inode/ctime/type差で停止、外部write/cleanup 0 | TOCTOU escape | fault unit + integration | S30 / S60 | both initial apply / retry negative pass | S30 / S60 commands |
| C360-RISK-CROSS-ROOT-RETRY | yes | Design §7.3 / §8.1 | A markerをBへreplay | root identity mismatchでB write 0 | marker replay | CLI fault | S35 / S60 | cross-root / package / operation negative pass | S35 / S60 commands |
| C360-RISK-HARDLINK | yes | Design §6.2 | mutation target `st_nlink > 1` | mutation block、read-only identical adoptだけ可 | alias mutation | unit filesystem | S30 | hard-link matrix pass | S30 command |
| C360-RISK-SYMLINK | yes | Design §6.2〜6.3 | parent/target/dangling symlink | no-follow classification、external target不変 | symlink escape | unit filesystem | S30 | symlink matrix pass | S30 command |
| C360-RISK-UNKNOWN-OWNERSHIP | yes | Design §4.2 / §6 | marker/path/owner自己申告 | evidence不十分ならpreserve-and-block | forged ownership | unit + CLI | S20 / S25 / S55 / S70 | positive trust chainとnegative cases pass | step commands |
| C360-RISK-DOWNGRADE | yes | Design §7.3 | target newer / unknown version | zero-write block | unsafe downgrade | CLI admission | S35 | version relation matrix pass | S35 command |
| C360-RISK-DUAL-MARKER | yes | Design §8.1 | distribution/uninstall/invalid/dual marker | operationを推定せずzero-write block | wrong recovery route | CLI admission | S35 / S65 | marker matrix pass | S35 / S65 commands |
| C360-RISK-POSTVERIFY | yes | Design §8 | apply済みpost-verify failure | version未確定、marker保持、success非表示 | false completion | fault integration | S60 / S70 | post-verify fault / retry pass | S60 / S70 commands |
| C360-RISK-SPECS | yes | Requirement RQ-010〜011 | keep-specs / node-local data | path/type/content/mode不変 | spec data loss | snapshot integration | S55 / S70 | full fixture equality | S55 / S70 report hashes |
| C360-RISK-PACKAGE-FALLBACK | yes | Design §10 | archive-installed consumer | working checkout参照 0 | false package parity | isolated integration | S80 | isolated consumer pass | S80 build / test evidence |
| C360-RISK-HISTORICAL-SCAN | yes | Requirement RQ-005 | Historical page / evidence | nonCurrent説明を誤削除・改変しない | evidence erasure | docs scan | S90 | allowlist-aware scan pass | S90 command |
| C360-RISK-OLD-ROUTE | yes | Requirement RQ-003〜006 | import/help/docs/skill route | removed fallback 0 | legacy reachability | negative scan + smoke | S40A / S40B / S85 / S90 | all surfaces absence | step commands |
| C360-RISK-DIAGNOSTIC-SANITATION | yes | Requirement RQ-012 / Design §3.2・§13 | credential風文字列、source bytes、repository外absolute pathを持つcollision / fault | text / JSON diagnosticにcredential、source content、repository外absolute pathを含めず、relative action / recovery情報だけを返す | secret / content / host path leakage | unit + CLI failure | S25 / S60 | positive failure resultを保ったまま禁止値の非包含assertionがpass | S25 / S60 commands; report Test Contract Closure |
| C360-SCOPE-001 | yes | Requirement §5〜6 | requested implementation scope | 357〜359再設計、external Intelligence、publication/merge/close/final Issue作成なし | silent scope expansion | diff / ledger review | S00 / S99 / H10 | out-of-scope diff/action 0 | S99 code/spec review |
| C360-SCOPE-002 | yes | Requirement §6 | critical escalation trigger | external write、credential、不可逆data deleteなら停止 | under-classified risk | review + report | all steps / S99 | triggerなし、またはcritical再計画 | Step stop evidence / S99 QA |

## 9. Exit / handoff

Implementation completeを主張できるのは次をすべて満たした場合だけである。

- §2.2のgateがpassし、S00〜S95の全stepが`committed`または正当な`approved-no-op`でclosedである。
- Provider / dogfood / wheel / sdist / Fresh / Updated parityとremoved absenceがpassする。
- Preservation fixtureがunchangedで、unknown ownershipがmisleading successにならない。
- Root README、migration、retained Markdown、CLI helpがCurrent contractと一致する。
- Integrated consumer smokeとsecurity / privacy diagnostic sanitationがpassする。
- S99でfresh `qa-reviewer`、issue-wide `code-reviewer`、`spec-reviewer`がすべてpassし、全required Closure IDとfinal report ledgerを閉じ、final commit / external clean evidenceがある。
- H10でcommit済みIC-3 inputをread-only handoffできるが、IC-3 pass、Issue / Epic close、release publication、PR merge、未承認final Issue作成を自己宣言・実行していない。

Implementation開始前の本Plan authoring完了条件は、Requirement / Design / Plan fresh review、canonical planning/report evidenceのcommit / push、formal `issue start`、active / deps / validationの再確認、clean exact-upstream SHAのChatGPT-SpecReview-Strict passである。これはS00の入場を許可するだけで、S10以降の実装closureまたはIssue completionを先取りしない。
