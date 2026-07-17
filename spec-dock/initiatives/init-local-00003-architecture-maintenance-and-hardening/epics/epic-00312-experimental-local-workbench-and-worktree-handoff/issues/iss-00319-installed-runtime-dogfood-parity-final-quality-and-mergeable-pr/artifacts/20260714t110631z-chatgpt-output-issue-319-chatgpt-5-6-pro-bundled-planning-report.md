## 結論

Issue 319 は、**Issue 315〜318 の仕様や実装を作り直す Issue ではなく、それらを最新 `main` と統合し、package／fresh consumer／existing consumer／dogfood の全配布面で実証し、公開文書・Epic 証跡・最終三者レビュー・単一 PR の merge preparation まで閉じる final delivery Issue**として正本化するのが妥当です。添付の bundled planning prompt が要求する三部構成、変更禁止境界、最終 PR 所有を以下へ反映しています。

GitHub connector で現行ブランチを直接参照でき、Issue 319 の `.meta.json` は Issue 315〜318 の全件を依存先として持っています。 GitHub Issue 315〜318 はいずれも `closed/completed`、Issue 319 と親 Epic 312 は open です。

一方、現行の Issue 319 `requirement.md` は `draft | approved` とプレースホルダーを残す未具体化テンプレートです。 親 Epic は W5 に distribution、docs、full quality、Epic closure、単一 mergeable PR を割り当て、W5 では PR delivery を再延期できないと明記しています。

GitHub connector の比較では、取得時点の現行ブランチは `main` に対して **53 commits ahead / 31 commits behind** の diverged 状態でした。これは Codex 側でのローカル再確認前の connector observation であり、以下の計画では **最新 main の統合を full quality より前の blocking gate** とします。

---

# Requirement Draft

```yaml
---
種別: 要件定義書（Issue）
ID: "iss-00319"
タイトル: "Installed Runtime Dogfood Parity Final Quality And Mergeable PR"
関連GitHub: ["#319"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-14"
親: ["epic-00312", "init-local-00003"]
依存:
  - "iss-00315"
  - "iss-00316"
  - "iss-00317"
  - "iss-00318"
---
```

## 1. 目的

Issue 315〜318 が完成させた次の能力を、provider authority から package、fresh installed consumer、existing consumer update、dogfood へ一貫して配布する。

* `.workbench/` の Git ignore と default semantic discovery opacity。
* 明示的な scoped `workbench copy` と source-wins merge。
* `artifact import chatgpt-output` の byte-preserving、source-preserving、no-overwrite import。
* ChatGPT-first preservation checkpoint と planning skills の共有 workflow。

そのうえで、公開文書、full regression、repository-wide static quality、installed consumer の統合 manual scenario、Epic E-RQ/E-AC closure、最終 QA／code／spec review、最新 `main` との統合、PR 作成・観測・修復・merge preparation を完了する。

本 Issue は Epic の final quality／distribution Issue であり、新しい product capability や storage model を追加する Issue ではない。

## 2. 現状と開始条件

### 2.1 完了済み依存

* Issue 315: Workbench ignore／opaque traversal foundation。
* Issue 316: scoped Workbench copy／source-wins merge。
* Issue 317: byte-preserving ChatGPT output Artifact import。
* Issue 318: ChatGPT-first preservation workflow／skill integration。

Issue 315 は per-Issue PR だけを Issue 319 へ延期し、実装・テスト・レビュー・push は完了済みと記録しています。  Issue 316 も最終 distribution だけを Issue 319 へ残し、copy contract の各 closure を pass としています。 Issue 317 は full pytest、global Ruff、package／fresh update、public docs、PR を明示的に relay しています。 Issue 318 は README、reference、migration、package、fresh init/update、full quality、final reviews、PR observation を Issue 319 の残存 gate としています。

### 2.2 現在の distribution gap

* Issue 315〜318 の provider runtime／docs／skills と dogfood projection は実装されている。
* Root README と public reference docs は、新しい Workbench copy／Artifact import の利用・権限境界をまだ網羅していない。
* Candidate wheel 由来の fresh init と、pre-feature existing consumer から candidate への update を final head で実証していない。
* Full repository pytest、global static quality、最新 main 統合後の回帰、Linux publication path、最終 PR checks は未実証。
* 現行 Issue 319 canonical documents は未具体化。
* 現行ブランチに対応する PR は connector 検索時点では存在しない。

## 3. 親 trace

親 Epic は provider authority、installed consumer／dogfood parity、Workbench の non-canonical／disposable 境界、Artifact import の blank grammar coexistence を固定しています。

| Issue 319 の責務                                     | 親 requirement / acceptance            |
| ------------------------------------------------- | ------------------------------------- |
| Package、fresh init、existing update、dogfood parity | E-RQ-017–018、E-AC-011                 |
| Public help／docs と experimental boundary          | E-RQ-016、E-AC-009                     |
| Workbench ignore／opacity／deletion の再検証            | E-RQ-001–005、013、015、E-AC-001–002、010 |
| Scoped copy の installed verification              | E-RQ-006–012、014、E-AC-003–008         |
| Artifact import の installed verification          | E-RQ-019–023、E-AC-013–015             |
| Preservation workflow／authority alignment         | E-RQ-024、E-AC-016                     |
| Full quality、Epic closure、mergeable PR            | E-AC-012、全 E-RQ／E-AC 最終再検証            |

E-AC-011 は package install/update と provider-to-dogfood refresh 後の Workbench preservation と parity を要求し、E-AC-012 は全 implementation Issue 完了後の focused/full tests、static analysis、manual handoff、review、mergeable PR を要求しています。 E-AC-013〜016 は import bytes、blank naming、publication failure、ChatGPT-first workflow の最終確認を要求しています。

## 4. 継承する不変条件

1. **Provider authority first**

   * Runtime、managed docs、skills、agent definitions の正本は `src/spec_dock/assets/**`。
   * `spec-dock/**`、root `.agents/**`、root `.codex/**` 等は installed／dogfood projection。
   * Dogfood-only implementation を作らない。

2. **Workbench authority isolation**

   * `.workbench/` は Git-ignored、non-canonical、disposable。
   * Node、ADR、dependency、context、review evidence、readiness authority ではない。
   * Root Workbench の一括 copy command は作らない。

3. **Copy boundary**

   * Source は current worktree。
   * 対象は Initiative／Epic／Issue の一件。
   * Target は same-repository linked worktree の一件。
   * Destination-only を保持し、same-relative leaf は source wins。
   * No watcher、no automatic sync、no copy-back。

4. **Artifact import boundary**

   * `chatgpt-output` は import operation kind であって typed Artifact token ではない。
   * Storage identity は既存 blank Artifact。
   * Existing `new artifact blank --slug chatgpt-output-*` を禁止しない。
   * Source bytes に frontmatter、template、normalization、summary を追加しない。
   * Source は残し、formal destination を上書きしない。

5. **Preservation／EAL boundary**

   * Preservation status と adoption status は別。
   * Import success は canonical adoption、reviewer pass、execution readiness を意味しない。
   * EAL 採否は main orchestrator が記録し、fresh reviewer gate を代替しない。

6. **Final delivery boundary**

   * Issue 319 から PR delivery を別 Issue へ延期しない。
   * Mergeable／merge-prepared の主張は、PR 作成・checks・review・mergeability の観測後に限る。

## 5. 観測可能な成果

完了時には次が観測できる。

* Clean candidate wheel に必要な provider assets がすべて含まれる。
* Candidate wheel から fresh repository を初期化すると、Workbench、copy、import、workflow／skills の全 surface が利用できる。
* Pre-feature existing consumer を candidate wheel で update すると、managed assets は更新され、root／Initiative／Epic／Issue の既存 Workbench bytes は完全に保持される。
* Provider と dogfood の managed inventory／bytes が、文書化された generated cache 等の例外を除いて一致する。
* Public docs が placement、root manual selection、source-wins、no sync、byte preservation、blank coexistence、evidence-only authority、experimental status を説明する。
* Issue 315〜318 の focused contract suites、full unit／CLI／integration／full pytest、static analysis が final head で pass する。
* Fresh installed consumer を使う manual integrated scenario が、Workbench handoff → Artifact import → EAL disposition → canonical rewrite の順序を実証する。
* Epic report が E-RQ-001–024、E-AC-001–016、EAL、OAL、残存 risk を追跡する。
* Fresh QA → code → spec review が pass する。
* 最新 `main` と統合済みの単一 PR が作成され、checks／review threads／mergeability を観測し、blocking finding が残らない。

完了時に観測できてはならない。

* Root Workbench bulk copy helper。
* Automatic Workbench sync、copy-back、promotion、retention。
* File extension／MIME／secret／content classifier。
* `chatgpt-output` typed token、reserved blank prefix、template、frontmatter、sidecar。
* Existing Workbench の削除・rewrite・permission normalization。
* Body、secret-like value、absolute host path の log／PR body／report への露出。
* PR 作成前または checks 未確認時点の `merge-prepared` claim。
* ChatGPT の推測、過去の test count、worker self-claim を final pass evidence とすること。

## 6. Issue 要件

### RQ-319-001 Dependency and planning authority

* Issue 315〜318 の canonical requirement／design／plan／report と GitHub completion stateを開始条件として確認する。
* Issue 319 の requirement → fresh spec review → assurance classify／verify → design → fresh spec review → plan → fresh spec review の順序を守る。
* 本回答や添付 ChatGPT 出力を canonical authority または test pass evidence としない。

### RQ-319-002 Mainline integration

* Final distribution／quality evidence を採取する前に、current branch と最新 `main` の差を再確認する。
* Behind／diverged の場合は repository policy に従う non-destructive integration を実施し、conflict を解消する。
* Force-push、履歴破壊、未確認の semantic conflict resolution を自動選択しない。
* PR 観測中に base が進んだ場合も、同じ integration gate を再実行する。

### RQ-319-003 Package inventory and clean build

* Clean managed temporary directoryで candidate wheel を build する。
* `pyproject.toml` の package-data contract に従い、provider runtime、docs、templates、`.gitignore`、install-root skills／agent assets が wheel に含まれることを検証する。
* Generated Python cache、stale `build/` content、legacy excluded assetsを candidate authority にしない。
* Version bump、dependency追加、lockfile変更は、実際の release policy／build failure が要求しない限り行わない。

`pyproject.toml` は `assets/**/*` に加え、dotfile `.gitignore` と hidden `.agents`／`.codex`／`.github` subtree を明示的に package-data へ含めています。

### RQ-319-004 Fresh installed consumer

Candidate wheelから fresh consumerを作り、少なくとも次を確認する。

* Managed docs／templates／scripts／skills／agent assetsが導入される。
* `.workbench/` ignore ruleがroot／Initiative／Epic／Issue placementで有効。
* Default semantic discoveryがWorkbench contentを解釈しない。
* `workbench copy` help／text／JSON contractが存在する。
* `artifact import chatgpt-output` help／text／JSON contractが存在する。
* Preservation workflow／planning skill checkpoint assetsが導入される。
* `validate`が成功する。
* Installed runtimeがprovider sourceを直接参照しなくても動作する。

### RQ-319-005 Existing update and byte preservation

* Pre-feature baselineから作成したexisting consumerへcandidate wheelの`spec-dock update`を実行する。
* Root／Initiative／Epic／Issue `.workbench/**` のregular files、binary bytes、nested directories、zero-byte files、near-name pathsをupdate前後で比較する。
* Existing Workbench fileのpath、bytes、symlink state、permissionをinstallerが意図的に変更しない。
* `spec-dock/initiatives/**` のcanonical specsとexisting Artifact bodyをinstallerが置換しない。
* Managed runtime／docs／skillsはcandidateへ更新される。
* Updateをmigration、`init --force`、automatic normalizationとして表現しない。

現行installerはmanaged `docs/templates/scripts/system`を更新対象とし、`spec-dock/initiatives/**`を削除しない契約を持ちます。 `.gitignore`はprovider assetまたはfallbackから更新されます。

### RQ-319-006 Dogfood exactness

* Provider assetsを先に確定し、candidate wheel／installer経路でdogfoodへ投影する。
* Matching provider／dogfood fileはbyte exactを原則とする。
* Generated timestamps、cache、derived state等の例外は、path、理由、比較方法をreportへ明記する。
* Dogfood側だけのmanual patchを残さない。
* Candidate wheelでの更新に予期しないtracked diffが出た場合、原因を分類するまで次stepへ進まない。

### RQ-319-007 Public documentation

次の既存pathを基本更新面とする。

* `README.md`
* `src/spec_dock/assets/spec_dock/docs/README.md`
* `src/spec_dock/assets/spec_dock/docs/guide.md`
* `src/spec_dock/assets/spec_dock/docs/reference_naming.md`
* `src/spec_dock/assets/spec_dock/docs/reference_worktree.md`
* 上記4 provider docsのmatching `spec-dock/docs/**` projection。

Issue 318 もこれらを Issue 319 の exact deferred paths として列挙しています。

Docsは次を説明する。

* Root Workbench の日付bucketはconventionであり、必要fileの選択はmanual。
* Scoped copyはcurrent source、one scope、one target、source-wins、one-shot、no sync。
* Artifact importはsingle Workbench Markdown、source survival、byte-preserving、no-overwrite。
* `chatgpt-output`はimport kind、storage identityはblank。
* Template-created blankとimport resultはfilenameだけでは区別しない。
* Complete outputのpreservationはcanonical rewrite前。
* Imported evidenceはnon-canonicalで、EAL adoptionとfresh reviewが別。
* Existing Workbenchのschema/data migrationはなく、updateはmanaged assetsだけをrefreshする。

Dedicated migration／release note fileは既定では作らず、既存README／guideで十分かをdocs reviewで決定する。

### RQ-319-008 Focused Epic regression

Issue 315〜318 の実在test surfaceを、private selectorを発明せずfile-levelまたはrepositoryで確認済みselectorで実行する。

* Workbench ignore／opaque traversal／delete／update。
* Scoped copy／selector／merge／symlink／fault／presentation。
* Artifact import／blank allocation／binary publisher／fault／presentation／consumer compatibility。
* Preservation workflow／wrapper／managed asset／ZIP lane。

`tests/unit/infra/test_init_update.py` は実在する巨大な `TestInitUpdate` test surfaceであり、plan時点で未確認のmethod selectorを発明しない。

### RQ-319-009 Full and global quality

Final integrated headで次を実行する。

* `uv run pytest tests/unit`
* `uv run pytest tests/cli_runtime`
* `uv run pytest tests/integration`
* `uv run pytest`
* `make lint`
* `git diff --check`
* Issue 317からrelayされたroot `scripts/authoring-pack/` のRuff check／format check。

Repositoryの正式なlocal static gateはRuff check、Ruff format check、mypyを`src/spec_dock`と`tests`へ実行します。  Root READMEもunit、lint、integration、CLI、full pytestを現行testing commandsとして示しています。

過去の Issue report のpass countはbaseline情報であり、current final headのpassを代替しない。

### RQ-319-010 Installed integrated manual scenario

Safe synthetic contentだけを使う disposable repositoryで、candidate wheel由来のfresh consumerとlinked worktreesを作り、次を順に観測する。

1. Root Workbenchのfileはbulk copy commandへ渡せない。
2. 必要fileをmanual selectionでscoped Workbenchへ置く。
3. Source／targetに同じscope ID、異なるdirectory slugを用意する。
4. Destination-only fileを保持し、same-relative fileをsource-winsでcopyする。
5. Binary／`.env`／nested `.git`／safe symlink fixtureをcontent classificationなしで扱う。
6. Copy後のsource変更がtargetへ自動同期されない。
7. Target Workbenchのcomplete Markdownを`artifact import chatgpt-output`する。
8. Source／final hashとbyte countが一致し、sourceが残る。
9. Imported fileがexisting blank grammarとしてvalidateされる。
10. Content-free receiptをEALへ記録し、その後だけcanonical summary／rewriteを行う。
11. ImportやskillがEAL／canonical docsを自動変更していない。
12. `validate`／`sync`とdefault discoveryがWorkbench内部を解釈しない。

### RQ-319-011 Authority and secrecy

* Manual scenario、tests、PR bodyにはsafe synthetic contentのみを使う。
* File body、secret-like value、absolute temp path、raw OS exceptionをpublic result／report／PRへ貼らない。
* Repo-relative path、hash、byte count、stable statusだけを記録する。
* Imported evidenceのbody内にauthority claimがあっても信頼しない。
* Preservation status、adoption status、reviewer statusを別fieldとして扱う。

### RQ-319-012 Failure routing

Failureは最初に責務別に分類する。

| Failure family                                                                                | Owning contract |
| --------------------------------------------------------------------------------------------- | --------------- |
| Ignore、semantic traversal、installer Workbench preservation、resolver opacity                   | Issue 315       |
| Copy selector、scope resolution、source-wins、symlink／identity／mutation semantics                | Issue 316       |
| Import bytes、source survival、blank naming、collision、no-replace publication                    | Issue 317       |
| Four-branch checkpoint、skills、EAL fields、external／delegated／ZIP lane separation               | Issue 318       |
| Package inventory、fresh/update matrix、public docs、main integration、global quality、PR delivery | Issue 319       |

* Prior contract内のimplementation defectは、そのIssueのapproved requirement／designを変更せずbounded repairする。
* Prior canonical contract自体にgapがある場合は、origin Issueのrequirement／designへ戻し、fresh reviewを通すまでIssue 319 completionをblockする。
* FailureをIssue 319の新しいproduct semanticsで迂回しない。

### RQ-319-013 Epic closure

* Issue 319 reportにC319 closure、test evidence、reviewer verdict、commit／push／PR evidenceを記録する。
* Parent Epic reportにE-RQ-001–024、E-AC-001–016の最終状態を追跡する。
* Epic EALでdelegated／ChatGPT／manual／review evidenceのadopt／reject／deferを確定する。
* Epic OALで主要目的とdistribution／PR作業の主従が逆転していないことを記録する。
* `blocked`／`stale` の unresolved entryを残さない。
* Epic spec closureとGitHub Epic issueのclose／PR mergeを混同しない。PR merge自体は別途明示された権限・操作に従う。

### RQ-319-014 Final review and PR delivery

* Local final gateは必ず fresh `qa-reviewer` → fresh `code-reviewer` → fresh `spec-reviewer` の順。
* 全reviewerは`gpt-5.6-sol`、reasoning `medium`。
* Review failureはowning workerへ戻し、repair後にaffected verificationとfresh reviewerを再実行する。
* 三者pass後にcurrent branchをpushし、`main`向け単一PRを作成する。
* PR checks、review submissions、inline threads、base drift、conflict、mergeabilityを観測する。
* Repair commit後は、影響に応じてQA→code→specを再実行し、PR観測をやり直す。
* 次を満たすまで`merge-prepared`を主張しない。

  * PRがnon-draftまたはrepository policy上ready。
  * Latest headがpush済み。
  * Baseが最新またはrequired updateを完了。
  * Required checksがpass。
  * Blocking review／unresolved threadがない。
  * GitHubがconflictなし／mergeableとして観測できる。
  * Final report／Epic closureがlatest headと一致する。

### RQ-319-015 Scope discipline

追加しないもの:

* Root Workbench bulk copy／helper。
* `--from`、automatic copy、watcher、sync、copy-back。
* Content／secret／MIME／archive classifier。
* General installer refactor。
* New persistent catalog、manifest、sidecar、receipt Artifact。
* `chatgpt-output` typed token／reserved prefix。
* Import bodyのparse／normalize。
* General transaction／rollback framework。
* Arbitrary path／cross-repository copy。
* PDF／image／ZIP／directory／bundle import。
* Existing Issue 315〜318 public semanticsの再設計。

## 7. 受け入れ条件

### AC-319-001 Dependency readiness

* GitHub Issue 315〜318がcompleted。
* Issue 319 dependency metadataが全4件を指す。
* Prior reportsのdeferred delivery relayがIssue 319へ解決されている。
* Issue 319 assuranceがcurrent requirement SHAへbindされ、`status=valid`。

### AC-319-002 Main integration

* Latest `origin/main...HEAD`が再確認される。
* Behind／divergedなら統合commitまたはapproved integration evidenceがある。
* Conflict repair後のfocused baselineがpassする。
* Final PR headでもbase driftが再確認される。

### AC-319-003 Clean package

* Clean wheel buildが成功する。
* Expected provider asset inventoryがwheelに存在する。
* `.gitignore`、hidden skills／agent assets、runtime modulesが欠落しない。
* Stale build／cache assetが混入しない。
* Candidate wheelだけからfresh initできる。

### AC-319-004 Fresh consumer

* Fresh consumerにWorkbench copy、Artifact import、preservation skillが導入される。
* Root／scoped Workbench ignore matrixがpassする。
* Fake Workbench metadataがvalidate／syncへ影響しない。
* Runtime help／text／JSONがexperimental／non-canonical／one-shot／no-sync境界を示す。

### AC-319-005 Existing update preservation

* Pre-feature consumerからcandidateへupdateできる。
* Four-scope Workbench sentinelのpath、hash、byte countがupdate前後で一致する。
* Canonical specs、existing imported Artifact、destination-only user contentが保持される。
* Managed assetsはcandidateへ更新される。

### AC-319-006 Provider／dogfood parity

* Provider／dogfood pair inventoryが列挙される。
* Documented exception以外はbyte exact。
* Dogfood-only implementationがない。
* Candidate update後にunexpected tracked diffがない。

### AC-319-007 Documentation

* Root README、provider docs index、guide、naming、worktree referenceが更新される。
* Matching dogfood docsがproviderと一致する。
* Required authority／migration／root/manual／copy／import／workflow boundaryが記載される。
* Typed token、automatic sync、canonical self-claimを示す誤記がない。

### AC-319-008 Focused regression

* Issue 315〜318に対応するfile-level focused suitesがfinal headでpassする。
* Private selectorや存在しないtest nameを使用しない。
* Failure時はowning contractへrouteされる。

### AC-319-009 Full quality

* Unit、CLI、integration、full pytestがfinal headでpassする。
* `make lint`がpassする。
* Relayed root authoring-pack Ruff driftが解消または再現不能としてfresh reviewerにより明示判定される。
* `git diff --check`がpassする。Byte-preserving raw evidenceの既知例外がある場合は、対象pathとhashを明記しcanonical／implementation diffから分離する。

### AC-319-010 Platform publication

* Supported Linux laneでdescriptor-bound/no-overwrite Artifact publication testsがpassするか、同等のCI evidenceが得られる。
* Safe primitiveを提供できないplatformではunsafe fallbackを使わず、既存contractどおりfail closedする。
* Platform evidenceが取得できずcross-platform claimを閉じられない場合はblocking unknownとして残す。

### AC-319-011 Manual integrated scenario

* Fresh installed consumer、two linked worktrees、different scope slug、destination-only、source-wins、rerun、no-syncが観測される。
* Artifact importのsource／final bytesが一致しsourceが残る。
* EAL disposition後にのみcanonical rewriteが行われる。
* Root Workbenchはmanual selectionのままで、bulk routeがない。

### AC-319-012 Authority／secrecy

* Output、logs、report、PRにfile body／secret／absolute temp pathがない。
* Preservationとadoptionが別状態として記録される。
* ChatGPT／command／skillがreviewer passやcanonical adoptionをself-claimしない。

### AC-319-013 Epic closure

* E-RQ-001–024、E-AC-001–016がobserved evidenceへtraceされる。
* Epic EAL／OALにunresolved blocking entryがない。
* Follow-upはowner、blocking classification、revisit conditionを持つ。

### AC-319-014 Final reviewers

* Fresh QA、code、spec reviewerが順番にpass。
* 各reviewer invocationは`gpt-5.6-sol`／`medium`。
* P0〜P2またはblocking findingが残らない。
* Repair後のstale pass claimがreportに残らない。

### AC-319-015 PR delivery／merge preparation

* `main`向け単一PRが存在する。
* Latest candidate headがpush済み。
* Checks pass、conflictなし、blocking review threadなし。
* PR descriptionがEpic／Issue trace、test evidence、manual evidence、known non-goalsを持つ。
* PR observation／repair loop完了後にだけmerge-preparedと記録する。
* Issue 319からPR deliveryを再延期しない。

## 8. 失敗条件

次のいずれかはIssue completionをblockする。

* Wheel buildまたはpackage inventory failure。
* Fresh consumerでcommand／skill／docsが欠落。
* Existing Workbenchの一byteでも意図せず変化。
* Provider／dogfood driftの未分類残存。
* Full pytest／static analysis failure。
* Linux publication pathの未検証またはunsafe fallback。
* Latest mainとのunresolved conflict／behind state。
* Manual integrated scenario failure。
* E-RQ／E-AC coverage gap。
* QA／code／spec reviewer failure。
* PR checks failure、merge conflict、unresolved blocking review。
* `blocked`／`stale` EAL entry。
* Body／secret／absolute path漏洩。
* Prior contract defectをIssue 319の新semanticで迂回した状態。

## 9. Scope

### In scope

* Current branchとlatest mainのintegration。
* Provider asset／package-data inspectionとbounded repair。
* Clean wheel build。
* Fresh init／existing update consumer matrix。
* Existing Workbench byte preservation。
* Provider／dogfood inventoryとexact projection。
* Root READMEと既存public docsのconsolidated update。
* Issue 315〜318 focused regression。
* Full pytest、lint、mypy、Ruff、diff check。
* Linux publication evidence。
* Installed manual integrated scenario。
* Issue 319／Epic reports、EAL／OAL／AC closure。
* Final QA→code→spec。
* Push、PR create、checks／review／mergeability observation、repair、merge preparation。

### Out of scope

* PR mergeそのもの。明示された権限が別途ある場合だけ実行する。
* New release publishing。
* Product semantic redesign。
* General installer cleanup／modernization。
* Persistent migration framework。
* Root Workbench command。
* Content／secret scanner。
* New import formats。
* Automatic EAL mutation。
* Cross-repository Workbench copy。

## 10. Grade／risk

### Candidate grade

* **Standard final-quality candidate**。
* 正式authorityはapproved requirement後の`assurance classify --stage requirement`結果とする。
* Profileをfrontmatterへ手入力して自己宣言しない。

### Strict再分類条件

* Public CLI semanticsの変更が必要。
* Version／release／package compatibility policyの変更が必要。
* Schema/data migrationが必要。
* New platform publication primitiveが必要。
* Credential付きexternal mutationまたはsecurity policy変更が必要。
* Existing Issue 315〜318 canonical contractの変更が必要。
* Main conflict解消がarchitecture／product semanticsへ波及する。

### 主なrisk

| Risk                              |            Grade | Mitigation                              |
| --------------------------------- | ---------------: | --------------------------------------- |
| Branchがmainからdiverged             |             High | S01で早期統合、PR前再確認                         |
| Hidden package asset欠落            |             High | Wheel inventory + fresh consumer        |
| Existing Workbench data loss      | Critical outcome | Four-scope byte sentinel                |
| Dogfood-only drift                |             High | Provider-first update + exact compare   |
| Global Ruff drift                 |           Medium | Explicit root authoring-pack lane       |
| Linux publication未実動              |             High | Linux CI/manual evidence                |
| Full suite timing flake           |           Medium | Final head rerun、原因分類、stale pass禁止      |
| PR base/check変動                   |             High | Observation/repair loop                 |
| Docsがauthorityを過剰主張               |             High | Fresh spec review                       |
| Raw evidence formatting exception |           Medium | Hash-bound exceptionをcanonical diffから分離 |

---

# Design Draft

```yaml
---
種別: 設計書（Issue）
ID: "iss-00319"
タイトル: "Installed Runtime Dogfood Parity Final Quality And Mergeable PR"
関連GitHub: ["#319"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-14"
依存: ["requirement.md"]
親: ["epic-00312", "init-local-00003"]
---
```

## 1. 設計方針

### DS-319-001 Final-delivery-only

Issue 319は新機能の設計場所ではない。Issue 315〜318のapproved contractsを入力とし、distribution、integration、quality、documentation、closure、PR deliveryだけを設計する。

修正が必要になった場合は次のいずれかに限定する。

* Distribution defect。
* Projection drift。
* Documentation gap。
* Existing contractのimplementation omission。
* Main integration conflict。
* Test／static quality defect。
* PR review finding。

Product semanticsの変更が必要ならorigin Issueまたはparent Epicへ戻す。

### DS-319-002 Provider-first authority

恒久的なmanaged implementationはprovider側を先に変更する。

```text
Provider authority
├── src/spec_dock/assets/spec_dock/**
│   ├── .gitignore
│   ├── docs/**
│   ├── templates/**
│   ├── scripts/**
│   └── system/**
└── src/spec_dock/assets/install_root/**
    ├── .agents/**
    ├── .codex/**
    └── .github/**
```

Dogfoodは次のprojectionであり、別実装ではない。

```text
Dogfood / installed projection
├── spec-dock/**
├── .agents/**
├── .codex/**
└── .github/**
```

### DS-319-003 Package-mediated verification

最終distributionはsource treeの直接比較だけでは閉じない。次の経路を別々に検証する。

```text
provider assets
    │
    ├── setuptools package-data
    │       │
    │       └── clean wheel
    │              ├── fresh consumer init
    │              ├── existing consumer update
    │              └── dogfood update/projection
    │
    └── source-level provider/dogfood comparison
```

Wheel inventoryは`pyproject.toml`のpackage-dataをauthorityとし、clean buildを使う。Stale checkout-local `build/`をproduct evidenceにしない。

## 2. 現状のdistribution境界

Installer entrypointは`spec-dock init`／`spec-dock update`だけを扱い、日常runtimeはinstalled `spec-dock/scripts/spec-dock`が担います。 Managed directoriesは`docs`、`templates`、`scripts`、`system`です。 Managed skillsにはChatGPT authoring、planning skills、PR creator／observation／merge preparerも含まれます。

Root READMEは現時点で`new artifact`は説明するものの、`workbench copy`と`artifact import chatgpt-output`のpublic usageをまだ掲載していません。 Provider docs indexの最短command一覧にも同2 commandは未掲載です。

GuideはWorkbenchのexperimental／opaque／disposable placementを既に説明していますが、代表command一覧にはcopy/importがありません。  `reference_worktree.md`は現在create/list/show/removeだけをcommand familyとして列挙しています。

## 3. Distribution design

### DES-319-001 Baseline and main integration

1. Current HEAD、origin tracking、latest `origin/main`、merge-base、ahead/behindを記録する。
2. Prior Issue relay commitとcurrent filesを照合する。
3. Current branchがbehind／divergedなら、repository policyに従ってlatest mainを統合する。
4. Conflictは次の順に分類する。

   * Canonical spec conflict。
   * Provider asset conflict。
   * Dogfood projection conflict。
   * Test snapshot conflict。
   * Report-only conflict。
5. Product semantic conflictをautomatic resolutionしない。
6. Integration後のfocused baselineをpassさせる。
7. Final PR observation時にもbase driftを再確認する。

履歴書換えよりreview可能なintegrationを優先し、force-pushは明示承認なしに行わない。

### DES-319-002 Wheel inventory

Wheel内asset inventoryはprovider treeを起点に生成し、少なくとも次を確認する。

* `spec_dock/assets/spec_dock/.gitignore`
* `spec_dock/assets/spec_dock/docs/**`
* `spec_dock/assets/spec_dock/templates/**`
* `spec_dock/assets/spec_dock/scripts/**`
* `spec_dock/assets/spec_dock/system/**`
* `spec_dock/assets/install_root/.agents/**`
* `spec_dock/assets/install_root/.codex/**`
* `spec_dock/assets/install_root/.github/**`

比較時に除外できるもの:

* `__pycache__/`
* `*.pyc`
* Build metadataでproduct assetではないもの。
* `pyproject.toml`の明示exclude対象。

除外をwildcardだけで済ませず、reportへpath classと理由を記録する。

### DES-319-003 Fresh consumer lane

Fresh laneはcandidate wheelだけをinputにする。

```text
clean temp root
└── fresh-consumer/
    ├── .git/
    ├── spec-dock/
    ├── .agents/
    ├── .codex/
    └── .github/
```

検証順:

1. `git init`したsafe temp repositoryを作る。
2. Candidate wheelから`spec-dock init`。
3. Installed inventoryを取得。
4. Provider asset inventoryと比較。
5. Runtime helpを確認。
6. Minimal Initiative／Epic／Issue fixtureを作る。
7. Root／scoped Workbench ignoreを確認。
8. Workbench内fake metadataを置いてvalidate／sync。
9. Workbench copy／Artifact import focused smoke。
10. Installed workflow／skill tokenを検査。

Fresh laneではcheckout source treeからruntime moduleをimportしてはならない。

### DES-319-004 Existing update lane

Existing laneは可能な限りpre-feature baseline wheelから作る。

1. S00でverified pre-feature refを決める。

   * 原則: current branchとmainのverified pre-feature merge-base。
   * そのrefが既に機能を含む場合は、最新published／accepted pre-feature refへ切り替え、根拠をreportに残す。
2. Baseline wheelからexisting consumerをinit。
3. Root／Initiative／Epic／Issue Workbenchをseed。
4. Binary、zero-byte、nested、near-name、safe symlink fixtureをseed。
5. Existing canonical docs、custom unmanaged file、existing blank Artifactをseed。
6. Candidate wheelからupdate。
7. Managed assetsの更新とunmanaged bytesの不変を別々に検証。

Update失敗時に`init --force`へ逃げない。

### DES-319-005 Dogfood projection

Dogfoodへの更新はrepo-local wrapperの固定upstream経路ではなく、**今回buildしたcandidate wheel**を明示して行う。Root READMEが説明するrepo-local update wrapperは固定upstreamを使うため、未merge candidateのdistribution検証には直接使わない。

手順:

1. Provider changesをcommit候補として確定。
2. Candidate wheelを再build。
3. Candidate wheelでcurrent repository rootをupdate。
4. Expected dogfood diffだけが生じたことを確認。
5. Provider／dogfood pairをbyte compare。
6. Unexpected diffがあればstepをblock。
7. Dogfood側の手修正をproviderへ逆輸入しない。

## 4. Documentation design

| Path                                 | 設計責務                                                                                                                          |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------- |
| `README.md`                          | Installer onboarding、runtime command examples、experimental warning、update preservation                                        |
| `src/.../docs/README.md`             | Public docs indexとcopy/importへの最短導線                                                                                           |
| `src/.../docs/guide.md`              | Workbench placement、root manual selection、copy→import→EAL lifecycle                                                           |
| `src/.../docs/reference_worktree.md` | `workbench copy`をworktree lifecycleとは別command familyとして説明。Target selector parity、source=current、one scope、source-wins、no sync |
| `src/.../docs/reference_naming.md`   | `chatgpt-output` import kind、blank storage identity、basename例、typed token／prefix reservationなし                                |
| Matching `spec-dock/docs/**`         | Provider exact projection                                                                                                     |

### Documentation single-source rules

* Workflow four-branch matrixはIssue 318のshared skill／workflow docsを正本とし、public guideへ全文複製しない。
* `reference_worktree.md`はexisting worktree create/list/show/remove semanticsを変更せず、`workbench copy`がselector semanticsを再利用する別commandであることを示す。
* `reference_naming.md`はexisting blank grammarへ例を追加するだけで、type catalogへ`chatgpt-output`を追加しない。
* Migration noteは「schema/data migrationなし」「existing Workbench bytes保持」「managed assetsだけupdate」を説明する。
* Dedicated migration fileを新設するかはS05 docs inventoryで決める。既存README／guideで十分ならapproved-no-opとする。

## 5. Focused verification design

### Issue 315 lane

* `tests/unit/infra/test_init_update.py`
* `tests/unit/infra/test_runtime_fs_repo_workbench_opacity.py`
* `tests/unit/infra/test_installer_workbench_resolver_opacity.py`
* `tests/unit/infra/test_runtime_resolver_workbench_opacity.py`
* `tests/unit/domain/test_authoring_source_manifest_workbench.py`
* Relevant validate／sync／delete／worktree tests。

### Issue 316 lane

* `tests/cli_runtime/test_workbench.py`
* `tests/unit/application/test_workbench.py`
* `tests/unit/infra/test_runtime_fs_cli_workbench.py`
* `tests/unit/presentation/test_workbench.py`
* `tests/cli_runtime/test_worktree.py`

### Issue 317 lane

* `tests/cli_runtime/test_artifact_import_chatgpt_output.py`
* `tests/cli_runtime/test_artifact_import_s04.py`
* `tests/unit/application/test_binary_artifact_import_ports.py`
* `tests/unit/commands/test_artifact_import_chatgpt_output.py`
* `tests/unit/infra/test_binary_artifact_publisher.py`
* `tests/unit/presentation/test_artifact_import_chatgpt_output.py`
* Existing `new artifact`／validate／sync／ADR mirror regression。

### Issue 318 lane

* `tests/cli_runtime/test_wrappers.py`
* `tests/unit/infra/test_init_update.py`
* `tests/manual_tests/test_review_chatgpt_authoring_pack.py`
* Artifact import regression。

Issue 318 final reportではこのcombined laneを619 testsで実行したhistorical evidenceがありますが、Issue 319ではfinal headで再実行する必要があります。

## 6. Manual integrated scenario design

```text
candidate wheel
    ↓
fresh installed repository
    ├── source linked worktree
    │      ├── root .workbench/YYYY-MM-DD/
    │      └── Issue A/.workbench/
    └── target linked worktree
           └── same Issue ID / different slug/.workbench/
```

### Scenario sequence

1. Source root Workbenchへsafe Markdownを置く。
2. Root bulk routeがないことをhelp／parseで確認。
3. Agentが必要fileだけをscoped Workbenchへmanual copy。
4. Source scoped Workbenchへmixed fixtureを置く。
5. Target scoped Workbenchへdestination-only fixtureを置く。
6. Stable worktree IDで`workbench copy`。
7. Target slugがsource slugではなくtarget node recordに従うことを確認。
8. Basename／absolute selectorでrerun。
9. Destination-only、source-wins、idempotencyを確認。
10. Sourceを変更し、targetへ自動反映されないことを確認。
11. Target Workbenchのcomplete reportを`artifact import chatgpt-output`。
12. JSON receiptのrepo-relative source／destination、hash、bytes、committed stateを確認。
13. Source survivalとfinal byte equalityを確認。
14. EALへpreservation／adoptionを別fieldとして記録。
15. その後にだけcanonical summaryを作成。
16. `validate`／`sync`。
17. Workbench fake metadataがcanonical graphへ現れないことを確認。

### Manual evidence boundary

* Contentはsynthetic。
* Absolute temp pathはreportへ残さない。
* Hash／byte count／repo-relative pathだけを残す。
* Workbench sourceはGit stageしない。
* Imported safe Artifactはmanual evidenceとしてcommit可能。
* Manual successだけでfull automated gateを代替しない。

## 7. Failure routing design

### 7.1 Classification

```text
Observed failure
├── Distribution-only
│   └── Issue319で修正
├── Prior implementation omission
│   └── Issue315/316/317/318 contractへroute
├── Prior specification gap
│   └── origin requirement/design再開 + fresh review
├── Main integration conflict
│   └── ownershipを特定してbounded repair
├── Test infrastructure/flaky
│   └── reproduction + deterministic classification
└── New product requirement
    └── parent Epic/ADRへ戻しIssue319停止
```

### 7.2 Routing rules

* **Issue315へ戻す**

  * Workbench内部がdefault discoveryへ漏れる。
  * UpdateがWorkbenchを変更する。
  * Installer resolverがWorkbench metadataを採用する。
* **Issue316へ戻す**

  * Selector parity、different slug、source-wins、destination-only、mutation signal、symlink／identity guard failure。
* **Issue317へ戻す**

  * Source／final bytes不一致。
  * Source loss。
  * Existing Artifact overwrite。
  * Typed token／blank reservation。
  * Descriptor-bound／no-replace publication failure。
* **Issue318へ戻す**

  * Four-branch drift。
  * Complete source failureをunavailableへ再分類。
  * External evidenceへdelegated frontmatterを要求。
  * Skillがcanonical／reviewer stateをself-claim。
* **Issue319が所有**

  * Wheel inventory。
  * Fresh／update harness。
  * Docs consolidation。
  * Dogfood parity。
  * Main conflict。
  * Full/global quality。
  * PR checks／review／mergeability。

Closed Issueを機械的にreopenするかはspec-managerのlifecycle判断とする。ただしcanonical contract gapはorigin Issueへtraceし、Issue319だけで新判断を隠さない。

## 8. Static and full-quality design

### Required commands

```bash
uv run pytest tests/unit
uv run pytest tests/cli_runtime
uv run pytest tests/integration
uv run pytest
make lint
git diff --check
```

Issue 317はroot scriptsの次のRuff driftをIssue 319へrelayしています。

```bash
uv run ruff check \
  scripts/authoring-pack/authoring_pack_review.py \
  scripts/authoring-pack/invoke_chatgpt_backend.py

uv run ruff format --check \
  scripts/authoring-pack/authoring_pack_review.py \
  scripts/authoring-pack/invoke_chatgpt_backend.py
```

### Flake policy

* Initial failureをpassとして記録しない。
* Isolated rerunはroot cause分類の補助。
* Final required laneはlatest headでpassさせる。
* Deterministic non-product flakeとしてexceptionにする場合は、reproduction evidence、scope外根拠、fresh QA／spec verdictが必要。
* Prior reportのhistorical passはcurrent evidenceではない。

## 9. Review and repair design

### Ordered local final gate

```text
Final candidate
    ↓
fresh qa-reviewer
    ↓ passed
fresh code-reviewer
    ↓ passed
fresh spec-reviewer
    ↓ passed
push
    ↓
PR create
    ↓
PR checks / review / mergeability observation
```

全DevCoder／reviewer invocationは`gpt-5.6-sol`、reasoning `medium`。

### Repair loop

```text
PR finding / failed check / base drift
    ↓
classify owning contract
    ↓
fresh DevCoder bounded repair
    ↓
affected focused tests
    ↓
required full/static lane
    ↓
fresh QA → code → spec as impact requires
    ↓
push
    ↓
PR observation again
```

Stale reviewer verdictをlatest headのpassとして再利用しない。

## 10. PR delivery／merge preparation design

PRは`main`をbase、現行Issue319 branchをheadとする単一Epic PR。

PR bodyに含める。

* Epic #312／Issue #319。
* Issue 315〜318 dependency／closure。
* Feature summary。
* Explicit non-goals。
* Package／fresh／update／dogfood evidence。
* Focused／full／static results。
* Manual integrated scenario。
* Authority／secrecy boundary。
* Known platform limitations。
* Reviewer verdict。
* Rollback。

Merge-prepared判定:

* Head SHA確定。
* Branch push済み。
* Base driftなし。
* Required checks pass。
* PR conflictなし。
* Blocking reviewなし。
* Unresolved review threadなし。
* Final reportとPR head一致。
* Epic EAL／OAL／AC closure済み。

PR mergeは本設計の自動操作には含めない。

## 11. Rollback

### Code／docs rollback

* Issue319で追加したdocs、package fix、test repairをfocused revertする。
* Prior Issueのimplemented capabilityをwhole-feature revertしない。
* Semantic defectならorigin Issue contractに従う。

### Consumer rollback

* Schema/data migrationはない。
* Existing Workbenchやimported Artifactを自動削除しない。
* Managed assetsを前wheelでupdateするか、candidate commitをrevertして新wheelをbuildする。
* Consumer user contentをrollback対象にしない。

### Dogfood rollback

* Dogfoodだけを手修正しない。
* Providerをrevertし、同じpackage／update経路でdogfoodへ再投影する。

### PR rollback

* Force-pushより追加repair／revert commitを優先する。
* PRをcloseする場合もreport／EALへ理由を記録し、merge-preparedを取消す。

## 12. Requirement trace

| Design                    | Requirement        |
| ------------------------- | ------------------ |
| DES-319-001               | RQ-319-001、002、012 |
| DES-319-002〜005           | RQ-319-003〜006     |
| Documentation design      | RQ-319-007、011、015 |
| Focused／full verification | RQ-319-008〜009     |
| Manual scenario           | RQ-319-010〜011     |
| Failure routing           | RQ-319-012         |
| Review／PR design          | RQ-319-013〜014     |
| Rollback／scope guards     | RQ-319-015         |

---

# Implementation Plan Draft

```yaml
---
種別: 実装計画書（Issue）
ID: "iss-00319"
タイトル: "Installed Runtime Dogfood Parity Final Quality And Mergeable PR"
関連GitHub: ["#319"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-14"
依存: ["requirement.md", "design.md"]
親: ["epic-00312", "init-local-00003"]
---
```

## 1. 実行原則

* **One step at a time**。
* 各stepは、変更 → verification → fresh review → commit／approved-no-op → clean確認後にだけ次へ進む。
* DevCoder、doc-writer、repo-analyst、qa-reviewer、code-reviewer、spec-reviewerは、利用可能な限り`gpt-5.6-sol`／reasoning `medium`で起動する。
* 少なくともDevCoderと全reviewerは必ず同model／effortを使い、reportへ直接観測値を記録する。
* Workerのself-claim、ChatGPTの推測、過去reportのpass countをstep closureにしない。
* Private pytest selectorを発明しない。巨大な`test_init_update.py`はfile-level実行を基本とする。
* 各stepのreport更新はorchestratorがobserved evidenceへ統合する。
* Canonical spec gap、scope expansion、destructive operation、external publish前にはstepを停止する。

## 2. 実行前 planning gate

### P-REQ Requirement promotion

1. 本Requirement Draftをcanonical `requirement.md`へ検証・再記述。
2. Fresh `spec-reviewer`。
3. Findingを修正してfresh rerun。
4. Pass後だけassurance classify。

```bash
./spec-dock/scripts/spec-dock assurance classify \
  --stage requirement \
  --issue iss-00319

./spec-dock/scripts/spec-dock assurance verify \
  --issue iss-00319 \
  --format json
```

### P-DES Design promotion

1. Approved requirementとassurance authorityを入力にDesignを確定。
2. Fresh `spec-reviewer`。
3. Pass後だけPlanへ進む。

### P-PLAN Plan promotion

1. 実在path、current commands、current test filesを再確認。
2. Closure／test IDs、worker boundaries、commit boundariesを確定。
3. Fresh `spec-reviewer`。
4. `guidance issue-execution`がreadyとなった後だけS00開始。

## 3. Spec-Locked Closure Index

| Closure ID | Close condition                                                  |
| ---------- | ---------------------------------------------------------------- |
| C319-01    | Dependency、current branch、main baseline、prior relay inventoryが確定 |
| C319-02    | Latest main integrationとpost-integration baselineがpass           |
| C319-03    | Clean wheelとpackage asset inventoryがpass                         |
| C319-04    | Fresh installed consumer matrixがpass                             |
| C319-05    | Existing updateがWorkbench／canonical bytesを保持                     |
| C319-06    | Public docsとprovider／dogfood docs parityがpass                    |
| C319-07    | Runtime／skillsのprovider→dogfood exact projectionがpass            |
| C319-08    | Issue315 focused regressionがpass                                 |
| C319-09    | Issue316 focused regressionがpass                                 |
| C319-10    | Issue317 focused regressionとplatform publicationがpass            |
| C319-11    | Issue318 focused workflow／skill／ZIP regressionがpass              |
| C319-12    | Installed manual integrated scenarioがpass                        |
| C319-13    | Full pytest／global static／diff qualityがpass                      |
| C319-14    | Epic E-RQ／E-AC、EAL／OAL、docs impactがclosed                        |
| C319-15    | Fresh QA→code→specがpass                                          |
| C319-16    | PR create／checks／review／mergeability observationがpass            |
| C319-17    | Final push／clean／lifecycle evidenceが確定                           |

## 4. Test Contract Index

| Test ID       | Closure    | Evidence level                         |
| ------------- | ---------- | -------------------------------------- |
| TC319-S00-01  | C319-01    | connector/local inventory              |
| TC319-S00-02  | C319-01    | dependency/report inspection           |
| TC319-S01-01  | C319-02    | main integration regression            |
| TC319-S02-01  | C319-03    | clean wheel build/inventory            |
| TC319-S03-01  | C319-04    | fresh consumer installed smoke         |
| TC319-S04-01  | C319-05    | baseline→candidate update preservation |
| TC319-S04-02  | C319-05    | canonical/custom content preservation  |
| TC319-S05-01  | C319-06    | docs contract inspection/tests         |
| TC319-S05-02  | C319-06    | provider/dogfood docs compare          |
| TC319-S06-01  | C319-07    | runtime/skill/agent inventory parity   |
| TC319-S07-01  | C319-08    | Issue315 focused files                 |
| TC319-S07-02  | C319-09    | Issue316 focused files                 |
| TC319-S07-03  | C319-10    | Issue317 focused files                 |
| TC319-S07-04  | C319-11    | Issue318 focused files                 |
| TC319-S08-01  | C319-12    | installed two-worktree manual scenario |
| TC319-S09-01  | C319-13    | full pytest lanes                      |
| TC319-S09-02  | C319-13    | make lint                              |
| TC319-S09-03  | C319-13    | root authoring-pack Ruff lane          |
| TC319-S09-04  | C319-10、13 | Linux publication evidence             |
| TC319-S90-01  | C319-14    | Epic AC/EAL/OAL closure inspection     |
| TC319-S99-01  | C319-15    | ordered fresh reviewers                |
| TC319-S100-01 | C319-16    | PR checks/review/mergeability          |
| TC319-S110-01 | C319-17    | push/clean/lifecycle                   |

---

## S00 — Repository、dependency、relay baseline

### 担当

* `repo-analyst`, `gpt-5.6-sol`, reasoning `medium`。
* Read-only。
* Orchestratorはreportへ観測結果だけを統合。

### 変更可能範囲

* Issue 319 `report.md`のbaseline／EAL／decision ledger。
* Canonical planning docsのreview finding修正のみ。

### 禁止範囲

* Runtime、provider assets、dogfood、tests、public docs。
* Main integration。
* PR create。
* Pass self-claim。

### 実行

```bash
git status --short
git rev-parse HEAD
git fetch origin main
git merge-base origin/main HEAD
git rev-list --left-right --count origin/main...HEAD
git diff --name-status "$(git merge-base origin/main HEAD)"..HEAD

./spec-dock/scripts/spec-dock deps check iss-00319
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock active show
./spec-dock/scripts/spec-dock assurance verify \
  --issue iss-00319 \
  --format json
```

確認対象:

* Current branchのremote/upstream存在。
* GitHub Issue 315〜318 completion。
* `.meta.json` dependencies。
* Prior Issue reportsのdeferred gate。
* Current PRの有無。
* Exact provider／dogfood changed surface。
* Current docs gaps。
* Current `main` divergence。
* Pre-feature update baseline ref候補。
* Linux CI／runner availability。
* Branch protection／required checksはPR前にはunknownとして記録。

### Close

* TC319-S00-01、TC319-S00-02。
* C319-01。

### Fresh review

* `spec-reviewer`, `gpt-5.6-sol`, `medium`。
* Baselineとscope guardのみreview。

### Commit boundary

* Report-only commitまたはapproved-no-op。
* Post-commit `git status --short` clean。

---

## S01 — Latest main integration

### 担当

* Git operation: orchestrator／spec-manager。
* Conflict repair: fresh DevCoder、`gpt-5.6-sol`／`medium`。
* Review: fresh code-reviewer。

### 変更可能範囲

* Main integrationで実際にconflictしたfiles。
* Conflict-sensitive tests。
* Issue 319 report。

### 禁止範囲

* Force-push without explicit approval。
* Unrelated cleanup。
* Product semantics変更。
* Dogfood-only resolution。
* Raw evidenceの再format。

### 実行

1. Repository policyを確認。
2. Latest `origin/main`をmergeまたはapproved integration strategyで取り込む。
3. Conflict inventoryを作る。
4. Canonical／provider／dogfood／test／report conflictを分類。
5. Prior Issue contractを保持して解消。
6. 次を実行。

```bash
git diff --check
uv run pytest -q \
  tests/cli_runtime/test_workbench.py \
  tests/cli_runtime/test_artifact_import_chatgpt_output.py \
  tests/cli_runtime/test_wrappers.py
```

Installer／snapshot conflictがある場合:

```bash
uv run pytest -q tests/unit/infra/test_init_update.py
```

### Stop conditions

* Mainがparent contractと矛盾。
* Conflictがnew product decisionを必要とする。
* Prior Issue canonical docsの変更が必要。
* Merge resultがprovider／dogfood authorityを逆転。

### Close

* TC319-S01-01。
* C319-02。

### Fresh review

* Whole integration diffをfresh code-reviewer。
* Canonical conflictがあればfresh spec-reviewerも追加。

### Commit boundary

* Integration commitまたはapproved-no-op。
* Pushはまだ必須でないが、commit後cleanを確認。

---

## S02 — Clean wheel and package inventory

### 担当

* Fresh DevCoder、`gpt-5.6-sol`／`medium`。
* Fresh code-reviewer。

### 変更可能範囲

Failureが実証された場合だけ:

* `pyproject.toml`
* `src/spec_dock/cli.py`
* `src/spec_dock/__init__.py`
* Package／installer focused tests。
* Issue 319 report。

### 禁止範囲

* Version bump without policy evidence。
* Dependency追加。
* General installer refactor。
* Managed tree ownership変更。
* Workbench migration。

### 実行

Clean managed tempへwheelをbuild。

```bash
uv build --wheel --out-dir <managed-temp>/dist
```

Wheel archiveからinventoryを取得し、provider asset setと比較する。Repositoryへ一時inventory scriptを残さない。

Focused tests:

```bash
uv run pytest -q \
  tests/unit/cli/test_cli_smoke.py \
  tests/unit/infra/test_init_update.py
```

検証:

* `.gitignore` included。
* Provider runtime included。
* Provider docs included。
* Install-root skills／agent assets included。
* No `__pycache__`／`.pyc`。
* Excluded legacy assets absent。
* Wheelからinstaller entrypointを起動可能。

### Red／Green

* Inventory missingをRed evidenceとする。
* Missing assetがなければproduction approved-no-op。
* Test追加だけで感度不足を閉じる場合もbounded change。

### Close

* TC319-S02-01。
* C319-03のpackage portion。

### Fresh review

* Package data、installer、test sensitivity。
* P0〜P2なしでpass。

### Commit boundary

* Package/test fix commitまたはapproved-no-op。
* Candidate wheelはartifactでありGit commitしない。

---

## S03 — Fresh installed consumer

### 担当

* Fresh DevCoder、`gpt-5.6-sol`／`medium`。
* Fresh code-reviewer。

### 変更可能範囲

* Installer／package focused tests。
* Distribution defectがある場合のprovider-side bounded fix。
* Issue 319 report。

### 禁止範囲

* Dogfood-only patch。
* New CLI option。
* GitHub mutation。
* Production/private content。

### 実行

```bash
uvx --no-cache \
  --from <candidate-wheel> \
  spec-dock init <managed-temp>/fresh-consumer
```

Fresh consumerで:

```bash
cd <managed-temp>/fresh-consumer
git init

./spec-dock/scripts/spec-dock workbench copy --help
./spec-dock/scripts/spec-dock artifact import chatgpt-output --help
./spec-dock/scripts/spec-dock validate
```

追加確認:

* Installed inventory。
* Provider→consumer byte compare。
* Root／scoped `.workbench/probe`の`git check-ignore`。
* Near-name negative。
* Fake `.meta.json`／ADR-like／dependency-like Workbench contentのopacity。
* Managed preservation skill／planning skillの存在。
* Runtimeがsource checkoutのPython pathなしで動く。

### Close

* TC319-S03-01。
* C319-04。
* C319-03 final。

### Fresh review

* Installed-only executionであること。
* No source checkout leakage。
* Help／authority contract。
* Package inventoryとの一致。

### Commit boundary

* Fresh test／distribution fix commitまたはapproved-no-op。
* Temp consumerはcommitしない。

---

## S04 — Existing consumer update and Workbench preservation

### 担当

* Fresh DevCoder、`gpt-5.6-sol`／`medium`。
* Fresh code-reviewer。
* Data-loss findingは即時block。

### 変更可能範囲

* `tests/unit/infra/test_init_update.py`
* Installer bounded fix。
* Package-data fix。
* Issue 319 report。

### 禁止範囲

* Workbench backup／migration。
* Initiatives tree replacement。
* `init --force` fallback。
* Test fixtureの内容分類。
* Unrelated installer cleanup。

### 実行

1. S00で決めたpre-feature refをclean temp worktreeへcheckout。
2. Baseline wheelをbuild。
3. Baseline wheelからexisting consumerをinit。
4. Root／Initiative／Epic／Issue Workbenchへbinary sentinelを配置。
5. Near-name、canonical specs、custom unmanaged skill、existing blank Artifactを配置。
6. Candidate wheelでupdate。

```bash
uvx --no-cache \
  --from <candidate-wheel> \
  spec-dock update <managed-temp>/existing-consumer
```

7. Before／after manifestを比較。
8. Managed assetsがcandidateへ更新されたことを確認。
9. `validate`／runtime help／ignore matrixを確認。
10. File-level installer suiteを実行。

```bash
uv run pytest -q tests/unit/infra/test_init_update.py
```

### Required evidence

* Four-scope sentinel SHA-256／byte count。
* Nested paths。
* Existing canonical docs hash。
* Existing Artifact hash。
* Managed asset before／after identity。
* Custom unmanaged content preservation。
* No automatic migration。

### Close

* TC319-S04-01、TC319-S04-02。
* C319-05。

### Fresh review

* Byte preservation。
* Test sensitivity。
* Installer change scope。
* Provider authority。

### Commit boundary

* Installer/test fix commitまたはapproved-no-op。
* Data-loss repairとdocs変更を同commitへ混在させない。

---

## S05 — Consolidated public documentation

### 担当

* Fresh doc-writer、`gpt-5.6-sol`／`medium`。
* Fresh spec-reviewer。

### 変更可能範囲

* `README.md`
* `src/spec_dock/assets/spec_dock/docs/README.md`
* `src/spec_dock/assets/spec_dock/docs/guide.md`
* `src/spec_dock/assets/spec_dock/docs/reference_naming.md`
* `src/spec_dock/assets/spec_dock/docs/reference_worktree.md`
* Issue 319 report。
* Dedicated migration noteはfresh spec-reviewで必要と判定された場合だけ。

### 禁止範囲

* Dogfood docsの先行手編集。
* Runtime／tests。
* Workflow four-branch matrixの複製。
* Typed `chatgpt-output` catalog。
* Automatic sync／root copy表現。
* Canonical／reviewer self-claim。

### Content checklist

* Workbench placement。
* Root date conventionとmanual selection。
* Exact `.workbench` opacity。
* `workbench copy` syntax／source-current／scope／target。
* Source-wins／destination-only／no sync。
* `artifact import chatgpt-output` syntax。
* Source survival／byte identity／no-overwrite。
* Blank storage identity／typed tokenではない。
* Template-created blank coexistence。
* Preservation-before-rewrite。
* Evidence-only／EAL／fresh reviewer。
* Existing update preservation。
* Experimental／non-canonical／disposable。
* No content safety guarantee。

### Verification

```bash
git diff --check

uv run pytest -q \
  tests/cli_runtime/test_wrappers.py \
  tests/unit/infra/test_init_update.py
```

`rg`でforbidden claim／duplicate matrixを検査する。Exact patternは実装時にcurrent wordingから決め、存在しないtest selectorをplanで固定しない。

### Close

* TC319-S05-01。
* C319-06のprovider docs部分。

### Fresh review

* Public command accuracy。
* Authority boundary。
* Issue315〜318 terminology。
* Japanese-primary docs contract。
* Migration wording。
* New file必要性。

### Commit boundary

* Root README + provider docs + reportのfocused commit。
* Dogfood projectionはS06。

---

## S06 — Dogfood projection and exact inventory

### 担当

* Fresh DevCoder、`gpt-5.6-sol`／`medium`。
* Fresh code-reviewer。
* Docs部分はfresh spec-reviewer。

### 変更可能範囲

* Matching `spec-dock/docs/**`。
* Matching `spec-dock/scripts/**`。
* Matching root `.agents/**`、`.codex/**`、`.github/**`。
* `spec-dock/.gitignore`。
* Projection tests。
* Issue 319 report。

### 禁止範囲

* Provider semanticsの変更。
* Dogfood-only implementation。
* Unrelated managed asset churn。
* Current Workbench content。
* Canonical initiatives content。

### 実行

1. S05 provider commitからcandidate wheelを再build。
2. Candidate wheelでcurrent repositoryをupdate。

```bash
uvx --no-cache \
  --from <candidate-wheel> \
  spec-dock update .
```

3. `git diff --name-status`をexpected projection listと比較。
4. Provider／dogfood pairをbyte compare。
5. Tracked unexpected diffがないことを確認。
6. Dogfood runtime help／validate。

```bash
./spec-dock/scripts/spec-dock workbench copy --help
./spec-dock/scripts/spec-dock artifact import chatgpt-output --help
./spec-dock/scripts/spec-dock validate
git diff --check
```

### Close

* TC319-S05-02、TC319-S06-01。
* C319-06。
* C319-07。

### Fresh review

* Code reviewer: projection exactness、unexpected churn。
* Spec reviewer: docs parity／authority。

### Commit boundary

* Dogfood projection + parity tests + report。
* Provider docsを同commitへ戻して混在させない。

---

## S07 — Focused prior-Issue regression

### 担当

* Fresh qa-reviewer、`gpt-5.6-sol`／`medium`。
* Failure repairはowning contractのfresh DevCoder。
* Repair後fresh code-reviewer。

### 変更可能範囲

* 原則read-only。
* Failure時はorigin contractに限定したsource／test。
* Issue 319 report。

### 禁止範囲

* Testの削除／skip追加でGreen化。
* Broad refactor。
* New semantics。
* Historical passの転記だけでclose。

### Issue315 lane

```bash
uv run pytest -q \
  tests/unit/infra/test_runtime_fs_repo_workbench_opacity.py \
  tests/unit/infra/test_installer_workbench_resolver_opacity.py \
  tests/unit/infra/test_runtime_resolver_workbench_opacity.py \
  tests/unit/domain/test_authoring_source_manifest_workbench.py
```

必要に応じて関連validate／sync／delete filesを追加するが、実在pathを`git ls-files`で確認してから実行。

### Issue316 lane

```bash
uv run pytest -q \
  tests/cli_runtime/test_workbench.py \
  tests/unit/application/test_workbench.py \
  tests/unit/infra/test_runtime_fs_cli_workbench.py \
  tests/unit/presentation/test_workbench.py \
  tests/cli_runtime/test_worktree.py
```

### Issue317 lane

```bash
uv run pytest -q \
  tests/cli_runtime/test_artifact_import_chatgpt_output.py \
  tests/cli_runtime/test_artifact_import_s04.py \
  tests/unit/application/test_binary_artifact_import_ports.py \
  tests/unit/commands/test_artifact_import_chatgpt_output.py \
  tests/unit/infra/test_binary_artifact_publisher.py \
  tests/unit/presentation/test_artifact_import_chatgpt_output.py
```

### Issue318 lane

```bash
uv run pytest -q \
  tests/cli_runtime/test_wrappers.py \
  tests/manual_tests/test_review_chatgpt_authoring_pack.py
```

Installer managed asset coverageはS04のfull `test_init_update.py` evidenceを再利用できるが、current headが変わった場合は再実行する。

### Close

* TC319-S07-01〜04。
* C319-08〜11。

### Fresh review

* QAがcoverage adequacyを判定。
* Failure repairごとにfresh code-review。
* Contract driftはfresh spec-review。

### Commit boundary

* No changeならreport-only approved-no-op。
* Repairはorigin failure familyごとに独立commit。

---

## S08 — Installed manual integrated scenario

### 担当

* Main orchestrator／qa-reviewer。
* `gpt-5.6-sol`／`medium`。
* Fresh spec-reviewerがevidence／authority boundaryを確認。

### 変更可能範囲

* Managed temp repositories。
* Safe synthetic Workbench files。
* 最大限必要なsafe imported Artifact。
* Issue 319 report／Epic EAL候補。

### 禁止範囲

* Real/private content。
* Current repo Workbenchのstage。
* Automatic EAL claim。
* Runtime repairをmanual scenarioへ混在。
* Root bulk copy helper。

### 実行

1. Candidate wheelからfresh temp consumer。
2. Temp Git repositoryとtwo linked worktrees。
3. Same Issue ID／different slug fixture。
4. Root Workbenchを作り、bulk command routeがないことを確認。
5. Safe fileをmanual selectionでscoped Workbenchへ移す。
6. Mixed Workbench fixtureとtarget-only fixture。
7. `workbench copy`をstable IDで実行。
8. Rerunをabsolute pathまたはbasenameで実行。
9. Source-wins／destination-only／idempotency。
10. Source変更後のno automatic sync。
11. Target WorkbenchからArtifact import。

```bash
./spec-dock/scripts/spec-dock artifact import chatgpt-output \
  --issue <issue-id> \
  --file <repo-relative-workbench-file> \
  --title "Issue 319 Integrated Manual Evidence" \
  --json
```

12. Hash／bytes／source survival／blank naming。
13. EAL record。
14. Canonical summaryをEAL disposition後に書く。
15. `validate`／`sync`。
16. Workbench fake metadata非検出。
17. Temp cleanup。

### Evidence

* Repo-relative path。
* SHA-256。
* Byte count。
* Commit／warning state。
* Copy target identity。
* Target tree summary、body非掲載。
* Before／after canonical hash。
* EAL adoption rationale。
* No-sync observation。

### Close

* TC319-S08-01。
* C319-12。

### Fresh review

* QA: scenario completeness。
* Spec: authority／EAL／root manual／no-sync。
* Code reviewはmanual scenarioがdefectを発見しrepairした場合だけ必須。

### Commit boundary

* Safe evidence Artifactを残す場合はreportとfocused commit。
* Workbench sourceはcommitしない。

---

## S09 — Full repository and global static quality

### 担当

* Fresh qa-reviewer。
* Failure repair: fresh DevCoder。
* Static／code repair: fresh code-reviewer。
* 全員`gpt-5.6-sol`／`medium`。

### 変更可能範囲

* 実証されたfailureに直接関係するsource／test。
* Root authoring-packのformat／lint fix。
* Issue 319 report。

### 禁止範囲

* Broad cleanup。
* Test削除／無根拠skip。
* Formattingによるbyte-preserving raw artifact変更。
* New product feature。

### 実行順

```bash
uv run pytest tests/unit
uv run pytest tests/cli_runtime
uv run pytest tests/integration
uv run pytest

make lint

uv run ruff check \
  scripts/authoring-pack/authoring_pack_review.py \
  scripts/authoring-pack/invoke_chatgpt_backend.py

uv run ruff format --check \
  scripts/authoring-pack/authoring_pack_review.py \
  scripts/authoring-pack/invoke_chatgpt_backend.py

git diff --check
```

Linux lane:

```bash
uv run pytest -q \
  tests/unit/infra/test_binary_artifact_publisher.py \
  tests/cli_runtime/test_artifact_import_s04.py
```

GitHub CIで実施する場合はworkflow run／job／head SHAをreportへ記録する。

### Failure handling

* First failureを保存。
* Isolated rerunで分類。
* Product failureならorigin contractへroute。
* Timing failureでもfinal required laneをlatest headで再passさせる。
* Raw evidenceのhash-bound whitespace exceptionは対象path／hashを明示し、canonical／code diffとは分離する。

### Close

* TC319-S09-01〜04。
* C319-10 platform portion。
* C319-13。

### Fresh review

* QA: test adequacy、integration decision、platform evidence。
* Code: repairs、global diff、static quality。
* New spec implicationがあればspec-review。

### Commit boundary

* Static／test repairはbounded commit。
* Quality passだけならreport-only commitまたはapproved-no-op。

---

## S90 — Docs impact、Epic closure、ledger finalization

### 担当

* `repo-analyst` + `doc-writer`。
* Fresh spec-reviewer。
* `gpt-5.6-sol`／`medium`。

### 変更可能範囲

* Issue 319 `report.md`
* Parent Epic `requirement.md`／`design.md`／`plan.md`のmetadataまたはobserved closureに必要な最小更新。
* Parent Epic `report.md`
* Docs impact ledger。
* EAL／OAL／AC closure。
* `.assurance.json`の正規再bindが必要な場合のgenerated update。

### 禁止範囲

* Observed evidenceなしのpass。
* Parent semanticsの書換え。
* Unresolved blocking entryのdefer扱い。
* PR-ready self-claim。
* Final reviewer passの先行記録。

### 実行

* E-RQ-001–024 matrix。
* E-AC-001–016 matrix。
* Issue315–318 relayの解決先。
* Provider／package／fresh／update／dogfood evidence。
* Public docs exact path inventory。
* Manual scenario。
* Full/static quality。
* Platform evidence。
* Follow-up／risk。
* EAL／OAL。
* No-op paths。
* Rollback。
* PR delivery gateをpendingのまま正確に記録。

```bash
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync
git diff --check
```

### Close

* TC319-S90-01。
* C319-14。

### Fresh review

* Requirement／design／plan／report／implementation／tests／docs／Epic alignment。
* PR gateを未実行のままpass扱いしていないこと。

### Commit boundary

* Epic／Issue closure ledger commit。
* PR evidenceはまだ未記録。
* Post-commit clean確認。

---

## S99 — Final QA → code → spec gate

### 前提

* S00〜S90 closed。
* Current branch latest main統合済み。
* Full/static pass。
* Manual scenario pass。
* No unresolved EAL blocker。
* PRはまだ作成しない。

### Gate 1: Final QA

* `qa-reviewer`
* `gpt-5.6-sol`／`medium`
* Whole Issue／Epic obligation coverage。
* Package、fresh、update、dogfood、manual、full test、platform evidence。
* Additional integration testの要否を明示判定。

### Gate 2: Final code review

* Gate 1 pass後。
* Fresh `code-reviewer`
* `gpt-5.6-sol`／`medium`
* Merge-baseからcurrent headまでのintegrated diff。
* Provider authority、installer preservation、copy／import safety、test sensitivity、static quality。
* P0〜P2／blocking／nonblockingを分類。

### Gate 3: Final spec review

* Gate 2 pass後。
* Fresh `spec-reviewer`
* `gpt-5.6-sol`／`medium`
* Requirement／design／plan／report／Epic／implementation／tests／docs alignment。
* EAL／OAL／closure／scope／authority／PR pending state。
* Stale reviewer claimがないこと。

### Repair

いずれかがfailした場合:

1. Promotion停止。
2. Owning contractへroute。
3. Fresh DevCoder repair。
4. Affected tests。
5. Full/static impact判定。
6. Failed gateからfresh rerun。
7. Latest headに全passを再bind。

### Close

* TC319-S99-01。
* C319-15。

### Commit boundary

* Final review ledger commit。
* Reviewer自身はsourceを変更しない。
* Commit後push前clean確認。

---

## S100 — Push、PR creation、observation、repair、merge preparation

### 担当

* Orchestrator。
* Installed `github-pr-creator`、`github-pr-observation`、`github-pr-merge-preparer` workflowを利用可能。
* PR repairはfresh DevCoder／code-reviewer。
* 全reviewerは`gpt-5.6-sol`／`medium`。

### 前提

* S99三者pass。
* Current branch clean。
* Latest mainとの差を再確認。
* Required local gatesはlatest headに対してpass。

### 実行

1. Current branchをpush。
2. Upstream `0 0`を確認。
3. `main`向け単一PRを作成。
4. PR bodyへtrace／evidence／non-goals／riskを記載。
5. Checksを観測。
6. Review submissions、inline threads、mergeabilityを観測。
7. Base drift／conflictを確認。
8. Findingがあればrepair loop。
9. Repair後のfresh QA→code→specを影響に応じて実行。
10. Pushしてchecks／reviewを再観測。
11. Merge-prepared criteriaを満たした時点でreportへ記録。
12. Final report update後にheadが変わる場合は、checksをもう一度観測する。

### PR repair constraints

* Review finding単位でrepair batchを作る。
* Unrelated cleanupを入れない。
* Review commentをresolveする前にcode／test evidenceを確認。
* Base update後のsemantic conflictはorigin contractへroute。
* Checkをskip／disableしてGreen化しない。

### Close

* TC319-S100-01。
* C319-16。

### Commit boundary

* PR URL／head／checks／review evidenceのreport commit。
* Final commit hashを同じcommit本文へ自己参照しない。
* Post-push evidenceはPR、final response、Issue comment等のexternal evidenceへ記録。

---

## S110 — Final lifecycle closure

### 前提

* PR exists。
* Latest checks pass。
* Conflictなし。
* Unresolved blocking reviewなし。
* Merge-prepared。
* Issue／Epic closure reportがlatest headと一致。

### 実行

```bash
git status --short
git rev-list --left-right --count '@{upstream}...HEAD'
./spec-dock/scripts/spec-dock validate
```

* Issue 319 delivery evidenceを確定。
* `issue finish`はcommit／push／PR／checks／reviewを代替しないため、上記完了後だけ実行する。
* Epic #312のGitHub issue closeは、PR mergeまたはhuman-approved lifecycle policyと整合する時点で行う。
* PRをmergeしていない段階では「Epic spec／quality closure」と「GitHub Epic issue／code merge」を区別する。

### Close

* TC319-S110-01。
* C319-17。

---

## 5. Step commit map

| Step     | Commit candidate                                      |
| -------- | ----------------------------------------------------- |
| Planning | `docs(issue-319): final distribution計画を具体化`           |
| S00      | `docs(issue-319): distribution baselineを記録`           |
| S01      | Main integration commit／merge commitまたはapproved-no-op |
| S02      | `test(package): Workbench機能のwheel inventoryを固定`       |
| S03      | `test(installer): fresh consumer distributionを検証`     |
| S04      | `test(installer): existing Workbench byte保持を固定`       |
| S05      | `docs(workbench): copyとArtifact importの公開導線を追加`       |
| S06      | `chore(dogfood): provider assetsをcandidateから投影`       |
| S07      | Origin contract別repair commitまたはreport no-op          |
| S08      | `docs(issue-319): installed統合scenario証跡を記録`           |
| S09      | `fix(quality): Epic-wide staticとregressionを修復`        |
| S90      | `docs(epic-312): E-RQとE-AC closureを確定`                |
| S99      | `docs(issue-319): 最終三者reviewを確定`                      |
| S100     | PR delivery／repair commits                            |
| S110     | Final report／lifecycle commit                         |

---

# 根拠

* Parent EpicはW5をdistribution／docs／final quality／PRのownerとし、provider／dogfood／package parity、full regression、final reviews、PR deliveryを要求しています。
* W5ではPR deferを使えず、full QA／code／spec passが必須です。
* Rollout docsにはplacement、root manual selection、source-wins、Artifact import、preservation checkpoint、no sync、authority、experimental statusが必要です。
* Issue 318のrelayはpackage build、fresh init/update、full pytest、repository-wide static、installed manual scenario、final reviewers、PR observationを明示しています。
* Issue 317のhistorical evidenceではunit 1121、CLI 1162／75 skipまで実行済みですが、full pytestとglobal RuffはIssue 319へ残されています。
* Current public docsはWorkbench placementを一部説明済みですが、copy/import commandとconsolidated authority guidanceは不足しています。

# 仮定

1. Final PRのbaseは`main`。
2. Product release／version bumpはIssue 319 completionの必須条件ではなく、repository policyまたはbuild／PR requirementが実証した場合だけ行う。
3. Pre-feature update baselineはS00でverified refを決定する。現時点ではcurrent branchとmainのmerge-baseが候補だが、確定claimではない。
4. Existing docsでmigration guidanceを十分表現できる限り、専用migration fileを新設しない。
5. PR merge自体はmerge preparationと別操作であり、明示された権限なしには行わない。
6. Closed Issueのimplementation defectはcurrent branchでrepairできるが、canonical contract gapならorigin Issue／parentへ戻る。

# EAL 採用候補

| Candidate                                    | Proposed disposition | 理由                                                   |
| -------------------------------------------- | -------------------- | ---------------------------------------------------- |
| Parent DS-005／W5 ownership                   | `adopted`            | Canonical Epic authority                             |
| Issue315〜318 deferred path／gate inventory    | `adopted`            | Prior reviewed relay                                 |
| Provider→wheel→fresh/update→dogfood topology | `adopted`            | Package／consumer parityを直接観測可能                       |
| Latest main integrationをfull quality前に置く     | `adopted`            | Connectorでbranch divergenceを観測                       |
| Public docs exact paths                      | `adopted`            | Issue318 relayとcurrent repoで実在確認                     |
| Full pytest／make lint／root script Ruff       | `adopted`            | Current command surfaceとprior relayに一致               |
| Historical test pass count                   | `partially_adopted`  | Baseline／risk情報のみ。Current pass evidenceには不採用         |
| Dedicated migration file                     | `deferred`           | Existing README／guideで足りる可能性。S05で再判定                 |
| Version bump／uv.lock変更                       | `deferred`           | Release policy未確認。Distribution verification自体には必須でない |
| Root bulk copy／automatic sync／classifier     | `rejected`           | Parent／Issue scopeに反する                               |
| Typed `chatgpt-output`／blank reservation     | `rejected`           | Accepted coexistence contractに反する                    |
| ChatGPTによるpass／review readiness claim        | `rejected`           | Repository observationとfresh reviewerが必要             |

# 不確実性・blocking unknown

1. **Remote branch enumeration**

   * Connectorのdirect ref fetchとcompareは成功した一方、branch searchでは同名branchが列挙されなかった。
   * Connector indexing差の可能性があるため、S00でlocal `git show-ref`、upstream、remote headを再確認する。
   * Push／PR前にはblocking。

2. **Latest mainの31 commits**

   * Connector compareでは現行branchがmainより31 commits behindだったが、その全差分・conflict内容は本回答では未検証。
   * S01 integration完了までfull quality evidenceをfinal扱いしない。

3. **Candidate wheel**

   * 本回答ではwheel build／archive inventoryを実行していない。
   * Hidden package assetsの実配布は未検証。

4. **Current full test/static state**

   * Prior Issue reportsのpassはhistorical evidence。
   * Latest main integration後のcurrent headでは未実行。

5. **Linux publication**

   * Issue 317がLinux descriptor-backed no-replace pathのlive verificationをIssue 319へrelayしている。
   * Linux CI／runnerの有無は未確認。
   * Cross-platform closureにはblocking。

6. **PR policy**

   * Required checks、branch protection、merge queue、review requirementはPR作成前の本回答では未確認。
   * PR observation時にrepository source of truthとして取得する。

7. **Assurance**

   * Issue 319のcurrent requirementはplaceholderであり、approved requirement SHAへbindされたassuranceは未確認。
   * Implementation開始前のblocking gate。

# 未検証主張

* 本文中の`pass`はすべて**計画上のclose condition**であり、Issue 319の実行結果ではない。
* Branchのahead／behind countは2026年7月14日のGitHub connector observationであり、Codex側local Gitによる独立検証前。
* Test pathはGitHub current branchとprior canonical reportsで実在確認したが、各fileのcurrent collection／passは未実行。
* Current branchにPRがないことはconnector検索時点の観測であり、PR作成直前に再確認する。
