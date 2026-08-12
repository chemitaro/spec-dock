---
種別: 要件定義書（Issue）
ID: "iss-00360"
タイトル: "Cut Over Distribution and Retire Legacy Workflow Surfaces"
関連GitHub: ["#360"]
状態: "approved"
作成者: "Codex main orchestrator"
最終更新: "2026-08-13"
親: ["epic-00356", "init-local-00003"]
依存: ["iss-00357", "iss-00358", "iss-00359"]
---

# iss-00360 Cut Over Distribution and Retire Legacy Workflow Surfaces — 要件定義

## 1. 目的

SpecDockの配布物を、Epic 00356で確定したStorage Core、薄いAuthoring Kit、二つのrepo-local skillへhard cutoverする。

Fresh consumerには旧Planning / Review / Execution / Assurance / Profile / provider固有authoring / PR workflow surfaceを配布しない。Existing consumerでは、既知のSpecDock-managed旧surfaceだけをownership boundary内で除去し、Initiative / Epic / Issueのidentity、正本文書、Artifact、Discussion、ADR、既存Report、`.assurance.json`その他のhistorical evidenceを変更しない。Uninstallでも、利用者が明示的に`--remove-specs`を選ばない限り同じspec historyを保持する。

本Issueはinstaller、provider asset、dogfood projection、package artifact、fresh / update / uninstall consumer、migration docsを一つのvertical sliceとして閉じる。357〜359が定義・実装したRuntime、Authoring Kit、skill semanticsを再設計しない。

## 2. 固定された入力と現在地

### I360-RQ-001 親契約と実装基準

次を本Issueで再質問・逆転しない。

* Storage CoreのCurrent command、lifecycle、Artifact、import contractはIssue 357の承認済みR/D/Pと実装handoffを入力とする。
* Thin template、Authoring Guide、Current六種のArtifact、Historical policy、単一Issue Plan、docs-only Planning LevelはIssue 358の承認済みR/D/Pと実装handoffを入力とする。
* Currentなrepo-local skillは`spec-dock`と`spec-dock-grill-with-docs`の二つだけとし、その本文・failure contractはIssue 359の承認済みR/D/Pとexact implementation commitを入力とする。
* Planning selection、親Epicのhandoff approval、Runtime dependency readinessを別のgateとして扱う。Blocked Issueを`active set`で選択し、Requirementとinventory調査を先行できるが、それだけでDesignへのphase promotionまたはimplementation readinessを主張しない。
* Designへのphase promotionは、Epic 00356 Planで定義されたIC-1とIC-2について、Epic-local ArtifactとReportにpass evidenceが存在する場合に限る。代わりに進める場合は、親Epic Planのhuman-approved revisionを正本へ反映しなければならない。Issue 360自身の文書やreview結果でこのapprovalを自己宣言しない。
* Issue 360のformal `issue start`と実装開始は、上記handoff approvalに加え、Issue 359を含むdirect dependencyがRuntimeのdependency-only readinessを満たした後に限る。
* 人間承認前の「品質・統合・deliverable handoff用の最終Issue候補」を新規作成せず、本Issueのdependencyまたは完了条件にしない。

本要件の初回具体化はIssue 359の途中head `27b8682cb6e5262c980f3b04c7f01459a87685e9`で開始し、2026-08-13にIssue 359 final head `948d0cf0dedb84ca34e51a4adc0995820aa011f6`を含むmain merge `a6ded0d9a838b40cdcd741fa473cd264b801f245`へ再照合した。GitHub Issue 359はclosedとなり、Runtime dependency readinessは`ready=true`である。Epic Plan §6.1に従うIC-1 / IC-2は、Epic-local Artifact `20260812t174542z-disc-ic-1-core-kit-contract.md`と`20260812t174548z-disc-ic-2-skill-contract.md`およびEpic Reportへ2026-08-13のfresh verification付きで`pass`を記録した。親handoff gateは充足したが、formal `issue start`の再試行はIssue 360文書の未コミット差分を保護するcheckout safetyにより停止しており、Design / Plan reviewとStrict final reviewも別gateとして未完了である。

### I360-RQ-002 Target distribution

Fresh install後にCurrentなSpecDock product surfaceとして存在してよいものを次に限定する。

* `spec-dock/{docs,templates,scripts,system}`にあるStorage CoreとAuthoring KitのTarget asset
* `spec-dock/.gitignore`、`spec-dock/spec-dock.version`、root Workbench README、生成可能な`active/`と`.agent/`
* `.agents/skills/spec-dock/**`
* `.agents/skills/spec-dock-grill-with-docs/**`
* `.github/workflows/ci.yml`。Storage Coreの決定論的な`sync` / `validate`だけを検証し、agent、review、planning、PR orchestrationを実行しない
* repo rootの安全な`spec` shortcut

Fresh installのrepo-local skill surfaceは二skill treeだけとする。`install_root`由来の非skill surfaceは上記`ci.yml`だけを許可する。`.agents/host-adapters/**`、`.codex/**`、`.github/agents/**`、その他の`.github/workflows/**`をSpecDockのTarget distributionとして新規配置しない。

### I360-RQ-003 Storage Core physical cutover

Issue 357が「360 handoff keep」とした通常CLI外の旧planning / authoring-pack surfaceをprovider、dogfood、wheel、sdist、fresh consumerから物理的に除去する。

少なくとも次を含む。

* `scripts/spec-dock-chatgpt`
* `scripts/authoring-pack/**`
* Runtimeの`chatgpt_app.py`、`cli/chatgpt_{parser,registry}.py`
* `commands/issue_planning.py`
* `application/{issue_planning,issue_planning_prompt}.py`
* `domain/{issue_planning_candidate,issue_planning_contracts}.py`
* `infra/issue_planning_*.py`
* `presentation/issue_planning.py`
* Runtime各layerの`authoring_pack/**`
* shared bootstrap / contracts / ports / appに残るplanning専用symbolと到達経路
* 上記だけを検証していたtest、fixture、manual helper

削除後にimport、parser、registry、wrapper、docs、test、packaged memberから旧backendへ到達するfallbackを残さない。Storage Coreと共有されるsymbolまたはtestは、旧consumerだけを切り離し、retained behaviorを保持する。

### I360-RQ-004 Authoring Kit physical cutover

Target template catalogを次へ限定する。

* `templates/{initiative,epic,issue}/{requirement,design,plan,report}.md`
* `templates/{root,initiative,epic,issue}/.workbench/README.md`
* `templates/artifacts/{blank,research,interview,disc,decision-candidate,adr}.md`
* `templates/README.md`

次のprovider / dogfood managed templateはFresh distributionから除去する。

* `templates/artifacts/pr-repair-batch.md`
* `templates/discussions/**`
* `templates/assurance/**`
* `templates/issue-profiles/**`

Existing node内に既に存在する同種のArtifact、Discussion、`.assurance.json`、profile由来R/D/P、heavy ReportはHistorical user dataであり、template pruneの対象にしない。

### I360-RQ-005 Current docs cutover

Current docsは次の系統だけを入口として配布する。

* `docs/README.md`と`docs/guide.md`
* `docs/migration.md`
* `docs/authoring/{overview,requirement,design,issue-plan,report,scope-layering,artifacts,historical}.md`
* `docs/authoring/issue-plan-levels/{light,standard,strict,critical}.md`
* Current Storage Coreが参照する`docs/reference_{deps,github,naming,sync,worktree}.md`
* Artifact / scope layoutを支える`docs/rules/**`

旧Current workflowを標準導線としていた次をprovider / dogfood / package / consumerから除去する。

* `docs/authoring/{chatgpt-pack,decision-routing}.md`
* `docs/phase_*.md`
* `docs/workflow*.md`
* `docs/reference_{authoring_pack_backend,hard_cutover}.md`
* 旧導線だけを持つ`docs/github.md`

Current docsからremoved pathへのlinkを残さない。`docs/authoring/historical.md`は旧語彙を説明できるが、旧workflowをCurrentな操作として案内しない。

Package metadataのreadmeでもあるrepository rootの`README.md`をCurrent entrypointへ更新し、`spec-dock/docs/migration.md`へ到達可能にする。Installed側の`docs/README.md`と`docs/guide.md`からも`docs/migration.md`へlinkする。

削除対象外のMarkdownもCurrent contractとの整合対象とする。少なくとも`scripts/README.md`、`system/**/*.md`、`templates/README.md`、root / scope Workbench READMEを全文scanし、removed command、removed path、旧skill、旧phase / review / assurance routeをCurrent操作として案内するlink・command・語彙を更新する。Historical explanationとして残す語は非Currentであることを明示する。

### I360-RQ-006 Repo-local skill / agent surface cutover

Issue 359が渡した18個のmanaged skillと、3個のlegacy managed skillをobsolete inventoryとし、Target managed skill inventoryを二skillへ切り替える。

旧18 skill:

* `spec-dock-hub`
* `spec-dock-initiative-planning`
* `spec-dock-epic-planning`
* `spec-dock-epic-execution`
* `spec-dock-issue-planning`
* `spec-dock-issue-execution`
* `spec-dock-chatgpt-authoring`
* `spec-dock-initiative-planning-manual`
* `spec-dock-epic-planning-manual`
* `spec-dock-issue-planning-manual`
* `spec-dock-clarification`
* `spec-dock-adr-facilitation`
* `spec-dock-codex-adapter`
* `spec-dock-copilot-adapter`
* `git-commit-conventional-ja`
* `github-pr-observation`
* `github-pr-creator`
* `github-pr-merge-preparer`

legacy 3 skill:

* `spec-driven-tdd-workflow`
* `spec-dock-system-architect`
* `spec-dock-implementation-planner`

旧host adapter metadata、native agent shim、execution prompt、repo-local agent profile、SpecDock-installed Codex rule、agent-driven GitHub workflowをTargetから外す。Storage Coreの決定論的な`.github/workflows/ci.yml`は維持する。旧skillやshimを二skillへのwrapperとして残さない。

### I360-RQ-007 Fresh consumer

Empty repositoryとunrelated user fileを含むrepositoryへのFresh initは、Target assetだけを配置する。

Fresh consumerで次を観測できなければならない。

* single R/D/Pとthin Reportを持つscopeを作成できる
* Current六種のArtifact templateとBase + 四Completion Guideが存在する
* 二skill treeがIssue 359のprovider sourceとbyte-identicalである
* `.github/workflows/ci.yml`が存在し、Storage Coreの`sync` / `validate`以外のagent・review・planning orchestrationを含まない
* `spec-dock` wrapperだけがexecutable entrypointとして存在する
* removed Runtime / docs / template / skill / adapter / agent / agent-driven workflow surfaceが存在しない
* unrelated fileとpre-existing user-owned external skillを変更しない
* obsolete inventoryと同名のpre-existing external skillもFresh initではpruneしない
* 同じpackageからの再実行が収束する

### I360-RQ-008 Existing consumer update

Existing updateは全mutation前に、Target current path、obsolete exact path、preserve root、path type、symlink container、collisionを分類する。

Managed scaffold tree外のCurrent target（Target二skill、`.github/workflows/ci.yml`、repo rootの`spec` shortcut）は、missingなら作成し、regular fileはbyte-identical、shortcutは正規化済みlink targetとfile typeが一致するときだけno-op adoptionできる。認識済みhistorical package digest、認識済みcanonical shortcut identity、またはdurable ownership manifestがSpecDock ownershipを証明する旧版だけをTargetへ更新できる。Non-identicalかつownership不明の同名file、symlink、directoryは保持し、全mutation前に停止する。Fresh initではhistorical workspace ownershipを推定せず、missing / current-identical以外を同じく保持・停止する。

Update後は次を満たす。

* `spec-dock/{docs,templates,scripts,system}`はTarget provider treeへrefreshされる
* known obsolete SpecDock-managed tool fileはexact-path inventoryとownership evidenceの両方に従ってpruneされる
* Target二skillとretained CIはIssue 359のno-follow / no-replace / byte-identical adoption contractを維持し、proven historical Targetだけを明示したupgrade pathで置換する
* unknown sibling、external skill、arbitrary `.codex` / `.github` fileを列挙外の名前やdirectory patternで削除しない
* node-local preserve setはrename、rewrite、mode change、deleteされない
* removed surfaceがTarget側のhelp、docs navigation、import graphへ再出現しない

`spec-dock/{docs,templates,scripts,system}`はinstaller-managed refresh surfaceであり、その中のlocal modificationをuser-owned specとして扱わない。この境界はmigration guideへ明記する。

### I360-RQ-009 Current / obsolete assetのownership policy

Current / obsolete inventoryはper-fileの正規化済みrelative path、認識可能なhistorical package digest、mutation policyを持つ。directory名、glob、prefix、exact pathだけを置換・削除のownership evidenceにしない。

Operationとprovenanceを組み合わせ、少なくとも次を区別する。

1. **genuine Fresh init**: 認識済みSpecDock workspace / ownership markerがないconsumerではobsolete pruneを実行しない。旧skillと同名のexternal skill、native agent shim、config、workflowを含め、Targetとのcollision以外の既存pathを変更しない。
2. **proven obsolete tool file**: Update、recognized workspaceへの`init --force`、uninstallでは、対象bytesが認識済みhistorical package digestと一致するか、既存のdurable SpecDock ownership manifestが当該pathを所有すると証明するときだけ、旧managed / legacy skill、host adapter、native agent shimをpruneできる。Exact pathとworkspace markerだけではcontent mismatchを削除しない。
3. **current reusable target**: `.github/workflows/ci.yml`など利用者も同じpathを使い得るTargetは、missing / current-identical / proven historical identityだけをcreate / adopt / upgradeできる。Regular fileはdigest、`spec` shortcutはfile typeと正規化済みlink targetでidentityを判定する。Non-identicalかつownership不明なら保持して全mutation前に停止する。Retained CIをobsolete inventoryへ含めず、workspace markerやpath一致だけで上書きしない。
4. **obsolete reusable file**: 旧`.codex/config.toml`、`.codex/AGENTS.md`、prompt、rule、その他のGitHub fileなどは、同じownership evidenceを満たす場合だけpruneする。不一致・symlink・判定不能は保持し、全mutation前のdiagnosticでoperator actionを示す。
5. **managed scaffold tree**: `spec-dock/{docs,templates,scripts,system}`。recognized workspaceでprovider treeへdirectory単位にrefreshする。`initiatives/**`、root Workbench payload、active source metadataをこのclassへ含めない。
6. **user-owned preserve**: 列挙済みspec history、unknown sibling、ownershipを証明できないsame-name skill / shim / config / workflow。自動置換・pruneしない。

Historical digestは実際に配布されたprovider / package bytesから再現可能でなければならず、推測値を登録しない。Ownershipを証明できないobsolete candidateが残る場合はapply前に停止し、preserved path、理由、operator actionを返す。Update / uninstallを成功扱いして「旧surfaceが完全に消えた」と報告しない。

### I360-RQ-010 Preservation contract

Updateおよびdefault uninstallで次をbyte-preserveする。

* Initiative / Epic / Issue directory、stable ID、parent chain
* `.meta.json`、GitHub linkage、direct dependency edge
* node-local `requirement.md`、`design.md`、`plan.md`、`report.md`
* Current / Historical Artifactとimport済みopaque file
* `discussions/**`
* accepted / candidate ADR
* `.assurance.json`
* profile由来文書、draft、repair、heavy Reportその他のhistorical evidence
* root / scope Workbenchのunmanaged payload
* unknown node-local file
* user-owned external skill、agent config、GitHub file、unrelated repository file

Preservationはcontent、file type、mode、pathの不変を意味する。Generated `active/**`と`.agent/**`は再生成またはuninstallで除去できるため、このbyte-preserve setに含めない。

### I360-RQ-011 Uninstall

Uninstallはdry-runを既定とし、apply時はcurrent Target assetとknown legacy managed assetを同じownership policyで処理する。

* `--apply`は`--keep-specs`または`--remove-specs`の明示を要求する。
* `--keep-specs`は`spec-dock/initiatives/**`を保持する。
* `--remove-specs`だけがspec history全体の削除を許可する。
* generated `active/**`と`.agent/**`、version marker、SpecDock自身のshortcutは既存安全契約内で除去できる。
* ownershipを証明できないmodified file、unknown sibling、external skillを保持し、apply前に停止してaction listへ理由を出す。
* current、legacy、mixed、partially-updated consumerで再実行が収束する。

### I360-RQ-012 Path safetyとfailure boundary

Init / update / uninstallは次を満たす。

* repository rootから外れるabsolute path、`..`、backslash escape、glob、directory-like obsolete entryを拒否する
* managed boundaryの親componentがsymlinkまたはnon-directoryならmutation前に停止する
* exact obsolete fileがsymlinkでも外部targetを辿らずlink自身だけを扱う
* exact obsolete pathにdirectoryがある場合、recursive deletionせず停止する
* Target current pathとobsolete pathの重複・祖先子孫overlapを拒否する
* full preflightが終わる前にcopyまたはpruneを開始しない
* error出力にcredential、source content、repository外absolute evidence pathを含めない

### I360-RQ-013 Partial failureと再実行

Updateは少なくともpreflight、managed scaffold refresh、current install-root copy、obsolete prune、post-verifyを識別できる。Uninstallは既存retry marker contractを保持する。

Operationがatomicでない場合も、失敗phase、対象relative path、完了済み / 未完了の区別、再実行commandを返す。故障注入後の再実行でTargetへ収束し、node-local preserve setを変更しないことをtestで示す。証拠なしにrollback可能とは主張しない。

### I360-RQ-014 Provider / dogfood / package / consumer parity

Provider sourceを唯一の配布正本とし、次を検証する。

* provider Target assetとdogfood projectionのcatalog / bytes / executable mode
* wheelとsdistのpackage member catalogがprovider Targetと一致する
* wheel / sdistからのFresh initが同じTarget catalogを生成する
* Existing update後のmanaged Target fileがproviderと一致する
* preserve setはprovider parity対象ではなく、before / after hashとpath metadataで不変を確認する
* removed assetがprovider、dogfood、wheel、sdist、Fresh、Updatedの全surfaceで不在である

Package scanは少なくともbinary、Python cache、secret-like file、local absolute path、verbatim interaction log、unexpected hidden managed payloadを検出対象とする。

### I360-RQ-015 Integrated consumer smoke

Packageから構築したconsumerで、357〜359の代表契約を一つのmatrixとして確認する。

* blocked Issueを`active set`で選択できる
* `issue start`がunfinished active guardとdependency readinessを区別し、`--force`がdependencyを迂回しない
* omitted type / explicit `blank` / typed Artifact作成とHistorical recognition
* `artifact import file`だけがCurrent importとして動く
* Fresh thin Reportがempty-validであり、existing heavy Reportは不変である
* 二skillがdiscoverableで、旧skill fallbackがない
* external `grilling` / `domain-modeling`不足がStorage Coreのinstall / useを阻害しない
* `issue finish`のclose / clear / sync契約をstubbed GitHub boundaryで確認する
* `validate`と必要なlocal `sync`がTarget consumerで成功する

### I360-RQ-016 Migration / compatibility communication

Repository rootの`README.md`、installed `docs/{README,guide,migration}.md`は実装と同じ内容で次を説明する。

* removed command、wrapper、docs、template、skill、adapter、agent / workflow surface
* retained Storage Core commandと新しいArtifact syntax
* `artifact import file`だけがCurrent importであること
* Planning Levelがdocs-onlyであること
* Fresh thin Reportとexisting Report preservation
* 二skill entrypointとexternal Intelligenceのoperator-owned境界
* managed scaffold内local modificationとnode-local preserve setの違い
* update時にmodified reusable fileを保持した場合の手動対応
* update / uninstallのdry-run、partial failure、retry / recovery
* Historical evidenceは保持されるがCurrent routeではないこと

## 3. 受け入れ条件

| ID | 条件 |
|---|---|
| I360-AC-001 | Fresh installのTarget catalogがI360-RQ-002と一致し、repo-local skillは二skill、非skill install-root assetはStorage Core用`.github/workflows/ci.yml`だけである |
| I360-AC-002 | 357 handoffのplanning / authoring-pack wrapper、module、shared symbol、専用test / fixtureが物理削除され、retained Storage Core testがpassする |
| I360-AC-003 | Template catalogがscope R/D/P/Report、Workbench README、Current六Artifact、READMEだけになり、obsolete templateが全配布surfaceで不在である |
| I360-AC-004 | Current docs catalogとlink graphがI360-RQ-005を満たし、removed docsへのlive linkがなく、Historical pageだけが旧語彙を非Currentとして説明する |
| I360-AC-005 | Managed skill inventoryが二skill、obsolete skill inventoryが旧18 + legacy 3で、旧skill / adapter / wrapper fallbackがない |
| I360-AC-006 | Empty / unrelated-file Fresh matrixがTarget配置、unrelated preservation、再実行収束を示し、obsolete同名external skill / native shimをpruneしない |
| I360-AC-007 | Unmodified legacy consumer updateがknown obsolete managed assetをpruneし、Target managed assetをproviderと一致させる |
| I360-AC-008 | `spec-dock/initiatives/**`のpreservation fixture全pathがupdate前後でcontent、type、mode、relative path不変である |
| I360-AC-009 | Unknown sibling / external skill / arbitrary agent or GitHub fileがupdateで変更されず、same-name skill / modified profile / native shimもownership未証明なら保持される |
| I360-AC-010 | Fresh、historical digest一致、durable manifest一致、content mismatch、ownership不明、managed scaffold、user-owned preserveのoperation × provenance policyがpositive / negative testで識別される |
| I360-AC-010A | Pre-existing `.github/workflows/ci.yml`、Target二skill、`spec` shortcutについて、missing create、current-identical adoption、proven historical upgrade、non-identical user-owned preserve-and-blockをFresh / updateで検証する |
| I360-AC-011 | Unsafe parent symlink、exact directory conflict、path escape、current / obsolete overlapが全write前にfailする |
| I360-AC-012 | Ownership未証明またはmodifiedなobsolete candidateは全mutation前に保持・診断され、旧surface完全除去のmisleading successにならない |
| I360-AC-013 | Uninstall dry-run / keep-specs / remove-specsがcurrent、legacy、mixed、partial consumerで期待どおり分類・収束する |
| I360-AC-014 | `--keep-specs` uninstallがspec history preservation fixtureを変更せず、`--remove-specs`だけが明示対象を削除する |
| I360-AC-015 | Update / pruneとuninstallの故障注入・再実行testがphase diagnostic、retry convergence、preserve set不変を示す |
| I360-AC-016 | provider / dogfood / wheel / sdist / Fresh / UpdatedのTarget catalog、bytes、mode parityとremoved-surface absenceがpassする |
| I360-AC-017 | Package scanにunexpected binary、cache、secret-like file、local absolute path、interaction log、unexpected hidden managed payloadがない |
| I360-AC-018 | Installed consumerで357〜359のintegrated smokeがpassし、external Intelligence不在でもStorage Coreが利用できる |
| I360-AC-019 | Root `README.md`とinstalled `docs/{README,guide,migration}.md`がactual help、asset inventory、ownership policy、recovery behaviorと一致し、相互にmigration入口へlinkする |
| I360-AC-020 | Retained `scripts/README.md`、`system/**/*.md`、`templates/README.md`、Workbench READMEの全文scanで、removed link / command / Current語彙が残らない |
| I360-AC-021 | Epic-local ArtifactとReportがIC-1 / IC-2 passを示すか、親Epic Planのhuman-approved revisionが存在するまで、Design promotion、formal start、implementation handoffをblockedとして扱う |
| I360-AC-022 | Issue 360のreportがexact implementation identity、consumer matrix、target / obsolete / preserve inventory、residual risk、IC-3入力を記録し、未承認の最終Issue作成やEpic完了を自己宣言しない |

## 4. 対象

* `src/spec_dock/cli.py`のinit / update / uninstall inventory、preflight、prune、diagnostic
* `src/spec_dock/assets/install_root/**`のTarget cutover
* `src/spec_dock/assets/spec_dock/{docs,templates,scripts,system}/**`のTarget cutover
* 対応するdogfood projection
* Issue 357が360へ渡したplanning / authoring-pack Runtime、shared symbol、test / fixture
* package-data catalogとwheel / sdist build result
* fresh / update / uninstall fixtureとpreservation fixture
* installed consumer smoke
* migration / compatibility / recovery docs
* repository root `README.md`とretained MarkdownのCurrent vocabulary / link audit
* provider / dogfood / installed parityとremoved-surface negative scan
* Issue-local R/D/P/reportとIC-3 handoff evidence

## 5. 対象外

* 357のStorage Core command / lifecycle / Artifact semanticsの再設計
* 358のAuthoring Kit文書意味・template本文の再設計
* 359の二skill本文・external capability behaviorの機能追加
* external model、browser、Oracle、`grilling`、`domain-modeling`の導入・vendor・実行
* existing node-local R/D/P/Report / Artifact / Discussion / ADRの自動変換、rename、rewrite
* existing `.assurance.json`のschema migration
* 旧skillを新skillへ委任するcompatibility wrapper
* provider固有importの代替route
* Product-owned Planning / Review / Execution / Assurance / Profile state machine
* arbitrary user-owned configを削除して完全Targetへ強制すること
* package publication、release、merge、Issue close、Epic close
* 人間未承認の最終Issue候補の作成・番号付与・dependency登録
* unrelated repository cleanupまたはarchitecture refactor

## 6. 制約・失敗時の判断

* 本IssueのPlanning Levelは`strict`を推奨する。public distribution、existing consumer migration、managed-file deletion、cross-platform filesystem safety、uninstallに影響し、回復難度が高いためである。
* Security / privacy境界、credential、production data、不可逆なuser-data deletionが対象へ入る場合は`critical`へ再評価し、実装を停止する。
* Node-local preserve pathとmanaged pathが重なる事実が見つかった場合、削除側へ推測せずDesignを修正する。
* Issue 359のfinal implementation inventoryが本書の基準SHAから変わった場合、実装前にexact inventoryとtest expectationを更新する。
* Retained Runtime / Kit / skill contract自体のdefectを見つけた場合、distribution integrationに不可欠な最小修正だけをowner付きで扱い、機能scopeを黙って360へ移さない。
* Full regressionやconsumer matrixが未実施・失敗の状態で、distribution cutover完了またはIC-3 passを主張しない。

## 7. 設計・計画への引き渡し

Designは次を具体化する。

* provider treeをcurrent inventoryの正本とし、obsolete / policyだけを二重化なく表現するmanifest構造
* host-adapter固有manifestとrequired native shim validatorの廃止方法
* Fresh / update / uninstallのpreflight、apply、post-verify、partial recovery flow
* operation × provenance policy、historical package digest、ownership未証明時のpreflight block
* 357〜359 handoffの削除 / retain / shared edit file inventory
* provider / dogfood / package / consumer parityの比較単位
* preservation fixtureとfault injection point
* docs / migration source-of-truth

Planは、依存ready再確認、inventory lock、RED test、provider cutover、dogfood projection、consumer matrix、docs、S90、S99、IC-3 handoffを、step-local closure conditionとrollback point付きで分解する。
