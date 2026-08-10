---
種別: 実装報告書（Issue）
ID: "iss-00357"
タイトル: "Reduce Runtime to Storage Core"
関連GitHub: ["#357"]
状態: "approved"
作成者: "main orchestrator"
最終更新: "2026-08-10"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00356", "init-local-00003"]
---

# iss-00357 Reduce Runtime to Storage Core — 実装進行報告

## 現在の結論

- Product Ownerは2026-08-10に、親EpicのRequirement / Design / Planと、本IssueのDraft 1を承認した。
- Draft 1はevidence-onlyの入力として正本`requirement.md`、`design.md`、`plan.md`へ統合し、repository factsと独立review findingsで精度を補った。
- Requirement、Design、Planはすべてapprovedで、各phaseのfresh `spec-reviewer`がpassした。
- `issue start iss-00357`を実行し、branch `iss-00357-reduce-runtime-to-storage-core`とactive contextを確立した。
- E00のread-only inventoryを実行し、retained / removed / sharedのpath、symbol、consumer、Action、ownerを確定した。
- E00のreport evidenceは2回のfresh `spec-reviewer` failを受けて修正し、3回目のfresh reviewでfindingsなしのpass（confidence 0.99）を得た。M0 commit `51b15905218706dcfa689c6765439aee30c785b2`とpost-commit clean checkを完了したため、S01へ進む。
- S01で通常CLIのparser / registry / bootstrapをStorage Core surfaceへ縮小し、focused Red / Green 12件、planning wrapper 13件、generic import 7件、lintとfresh code reviewをpassした。
- S02で`active set`をselection-onlyへ縮小し、minimal schema v2 write、legacy tolerant read、Context Packのworkflow metadata除去、各write phaseのtransactional rollbackを実装した。review 1〜5とintegration review 1 / 2のP1をすべて修正し、fresh integration review 3がfindingsなしでpass（confidence 0.98）したためS02をcloseした。
- S03で`issue start`をtarget validation→branch非依存unfinished guard→shared dependency check→checkout→active write→syncへ分離した。review 1のrepo-qualified selector P1を修正し、start `18 passed`、check_deps / deps `43 passed`、fresh re-review pass（confidence 0.98）でS03をcloseした。
- S04で`issue finish`をclose→clear→syncだけへ縮小し、authority / Report / EAL / delegated metadata readを除去した。review 1のclear非`RuntimeError` P1を修正し、focused finish `10 passed`、full lifecycle `29 passed`、fresh re-review pass（confidence 0.98）でS04をcloseした。
- M1 commit `d1c16c4dd099c94eabb6e7b2677b4dd148d6fbb6`を作成し、commit hookとpost-commit clean checkをpassした。S05はCurrent Artifact六種の作成interfaceとfilesystem safetyをRed-firstで実装した。review 1〜8のP1をidentity / held-dirfd / committed-warningへ修正し、helper full 65、mandatory 31、全race / transaction matrix、lint / parityをpassした。fresh re-review 9はfindingsなしでpass（confidence 0.95）したため、`CL-357-006`をcloseした。
- S06でHistorical timestamp typed六種、sequential三種、generic import、legacy Discussionを明示認識した。review 1〜3のP1 / P2を修正し、domain 45、focused 38 / capability skip 1、doctor 44、S05 helper 65、actual validate / doctor、lint / parityをpassした。fresh re-review 4はfindingsなしでpass（confidence 0.97）したため`CL-357-010`をcloseした。
- S07で`artifact import file`のfour-scope / opaque-byte / atomic publish / privacy契約を保持し、provider-specific `artifact import chatgpt-output` backend、ports、renderer、専用testsを削除した。focused matrixは`121 passed / 1 platform skip`、provider / dogfood Runtime parityと`git diff --check`はpassした。fresh code reviewはfindingsなしでpass（confidence 0.97）したため`CL-357-007`をcloseした。
- S08でFresh Initiative / Epic / Issueを既存scaffolder / repository mechanismのfd-aware extensionへ統一し、四canonical documentsを各一つ、`.assurance.json`なしで生成することを固定した。fresh review 1〜3を受け、通常process concurrency / handled failureとsame-UID tampering / crash recoveryの達成可能な境界をspec-reviewで固定し、mode 0700 outer transactionとheld payloadの二層staging、cross-dirfd no-replace publishへ再設計した。review 4 P2のunchanged-shebang mode parityも補正し、S08 / template 83、Fresh CLI 38 / skip 5、S09 retained 65、lint / parity / diff-check、fresh review 5をpassしたため、`CL-357-008`をcloseした。
- S09で`validate_tree.py`からdelegated authority / Evidence Adoption Ledgerのcontent gateだけを除去し、thin / heavy Report、EAL、delegated metadata、Assurance、Planning Level、legacy active extra fields、draft / repair Artifactの9-token mutationをactive / deps / start / finish / validate / doctorで内容非依存にした。各mutationの独立baselineに対するprocess / durable state完全比較、read-only surfaceのHistorical raw-byte保持、4 content-read入口のcall-zero、required Report欠損negative controlを固定した。focused `35 passed / 1 skipped`、unit file-read `10 passed`、validate / deps use-case `34 passed`、lint / parity / diff-check、fresh code review 2 / QA review 3をpassしたため、`CL-357-009`をcloseした。
- PR、merge、`issue finish`はまだ実行していない。正本のlocked expectationを変える必要が生じた場合は、該当stepを停止してR/D/P amendmentとfresh reviewへ戻る。

## 承認済み正本

| 文書 | 状態 | 主な固定内容 |
|---|---|---|
| `requirement.md` | approved | Storage Core CLI、selection-only active、start / finish順序、Current / Historical Artifact、generic import、Fresh scaffold、互換性、handoff |
| `design.md` | approved | 既存`ActiveManifestEntry` / schema v2、dependency-only readiness、partial result、module delta、migration / rollback、ownership |
| `plan.md` | approved | E00〜S99の縦スライス、`CL-357-001`〜`CL-357-015`、step-local delegation、Red / Green、具体テストカード、review gate |

## Spec Interpretation / Decision Ledger

| ID | Status | Type | Trigger | Options Considered | Disposition | Evidence | Follow-up |
|---|---|---|---|---|---|---|---|
| `DEC-357-E00-001` | resolved | ownership interpretation | 通常CLI外のshipped wrapper `spec-dock-chatgpt`が認知的Runtimeへ直接到達することをE00で確認した | 357のremoved Runtime候補に含める / 357では保持して360へhandoffする | rejected: 357での削除候補化を棄却する。RQ-357-001とAC-357-001のCurrent surfaceは通常`spec-dock` parser / registry / helpで、Design §13の明示Delete候補に別executableのissue-planning経路はない。Design §14に従い、wrapper / `chatgpt_app` / chatgpt CLI / issue-planning Runtime / direct authoring scriptsは360 ownerの`Handoff keep`とする | `requirement.md` RQ-357-001 / AC-357-001、`design.md` §13 / §14、通常`app.main` graphと独立`spec-dock-chatgpt` graphの実在照合 | H91で360向けprovider asset inventory、到達経路、hash evidenceを渡す |
| `DEC-357-EXEC-002` | resolved | execution authority interpretation | `guidance issue-execution`が`blocked / report-spec-review-missing`を返したが、正本reportにはfresh E00 review passとM0 clean evidenceがあり、ユーザーは削除予定workflow projectionに従わずapproved Planで完遂するよう指示した | generated guidanceをblockerとしてplanningへ戻す / canonical R/D/P/reportと実測Git evidenceを優先する | rejected: generated guidanceによる停止を棄却し、canonical approved Planを実行する。これはreview / test / step gateのwaiverではなく、削除対象workflow projectionのstale判定だけをauthorityから外す | `guidance issue-execution`: `state=blocked`, `reason_code=report-spec-review-missing`; report `execution E00 review 3=pass`; commit `51b1590`; post-commit clean; user instruction 2026-08-10 | S01以降はPlanのclosure、focused tests、fresh reviewer、milestone commitを維持する |
| `DEC-357-EXEC-003` | resolved | execution sequencing interpretation | S02 review 5で、minimal manifest cutover後のstart dependency / finish authority regressionが検出されたが、その最終責務はPlan S03 / S04に明示され、M1 commitもS04後である | S02へ暫定workflow logicを復元して単独close / S02 rollback修正と並行して計画済みS03→S04へ収束し統合再review | adopted: lifecycle regressionはS03 / S04のlocked expectationを直接実装して解消し、S02〜S04統合状態でS02再reviewする。S02のselection-only境界へreadiness / authorityを戻さない | Plan §4 dependency graph `S02→S03/S04`、S02 Forbidden、S03 / S04 behavior goals、M1 after S04、review 5 findings | S02-owned rollback、S03 start、S04 finish、integration testsを完了。integration review 1のreport-only P1を同期後、fresh re-reviewでclosure確定 |
| `DEC-357-S06-004` | resolved | managed Artifact candidate interpretation | baseline `artifacts/`にtimestamp風authoring-pack directoryと単一hyphen typed風`.html` attachmentがあり、非`.md`全件をmalformed候補に広げるとactual validateが失敗した | Historical catalogへ暗黙追加 / 非`.md`もunknown timestamp-intentとして診断 / 既存managed candidate境界を維持 | adopted: typed / sequential Artifact candidateは承認grammarどおり`.md`に限定し、generic importは`--<original-basename>`で拡張子を問わず認識する。単一hyphenのnon-`.md` attachmentとdirectory treeはout-of-bandでありcatalogへ追加せず、Artifact filenameとして誤分類しない | RQ-357-005のtyped / sequential `.md`例とgeneric `--` grammar、Design §9.1、baseline actual validate / doctor、既存`is_malformed_artifact_candidate`のfile-oriented境界 | S06 fixtureで`.md` unknownは診断、generic `.html`は認識、out-of-band directory / `.html`はpath / SHA-256不変を固定する |
| `DEC-357-S08-005` | resolved | step ownership interpretation | Fresh create pathはAssurance access zeroだが、bootstrap / `create_artifact_doc`にdead Assurance / ArtifactStore wiringが残る | S08でallowed pathを広げて物理削除 / S08はbehavioral non-dependencyを固定しE00 inventoryどおりS10で削除 | adopted: S08はFresh三scopeのno-Assurance behaviorとaccess zeroを固定し、dead wiringのconsumer proof / physical deletionはS10へ残す | Plan S08 allowed / forbidden paths、E00 Delete inventory、Fresh access spy、`.assurance.json` absence | S10でbootstrap / contracts / portsのconsumer逆引きとremoved module parityを確認する |
| `DEC-357-S08-006` | resolved | identity-bound publication | review 1でcanonical destinationへ直接pathname writeすると、held parent fd rollbackでもreplacement側writeを回収できないと判明した | phaseごとのpathname identity check / canonical child fdへ直接write / hidden stagingへfd-bound write後atomic publish | adopted: 一意hidden stagingをheld parent / child fdでclaimし、既存scaffolder / repositoryのbounded `*_at` extensionでcopy / rules / metaをfd-relativeに完了後、Linux / Darwin no-replace renameでcanonical名へ一度だけpublishする | review 1 P1、six-phase parent / destination replacement matrix、identity-capture fault / retry、mode parity、provider / dogfood parity | unsupported OSはpublication不能としてfail-safe。S08 fresh re-reviewでport boundary / rollback / result pathを確認する |
| `DEC-357-S08-007` | resolved | concurrency / recovery boundary | review 2 / 3でmkdir→identity取得間にcompetitor保全とowned residue zeroを同時に満たせないことを確認した。Darwin / Linuxの`mkdirat`は作成directoryのfdを返さない | syscall順序をさらに補強 / same-UID tamperingまで絶対保証 / 通常process concurrencyへ境界を明記して二層staging | adopted: held parent直下のmode 0700 outer transactionをopen-firstで保持し、そのfd内payloadを完成後にcross-dirfd no-replace publishする。通常の独立spec-dock processとhandled I/O failureを保証し、same-UID非協調tampering、SIGKILL、power loss、filesystem corruptionは境界外。tampering検知時はcleanupよりcompetitor保全を優先する | review 2 / 3 P1、Darwin `mkdirat(2)` return contract、deep-consultant impossibility analysis、no-replace capability | RQ / Design / Planへthreat / recovery boundaryを明記。fresh reviewerはliteral absolute guaranteeでなく、このbounded contractと実装を照合する |

locked expectationの追加・変更はない。E00で見つかった通常CLI外の到達経路は、承認済みDesign §14 / H91のhandoff inventoryへ割り当てた。

## Objective Alignment Ledger

| target | primary objective evidence | secondary requirement evidence | inversion risk | reviewer verdict |
|---|---|---|---|---|
| planning adoption | `requirement.md`のStorage Core縮小と`design.md`のTarget boundaryを`plan.md`の縦スライスへ直接追跡した | compatibility、migration、handoff、step-local review / test evidenceを同じclosureへ従属させた | none | pass |

## Evidence Adoption Ledger

| ID | adoption_status | source | target | rationale | evidence | next_action |
|---|---|---|---|---|---|---|
| EAL-357-001 | adopted | `artifacts/20260809t125145z-draft-requirement-strict-vertical-slice-requirement.md` | `requirement.md` | Product OwnerがDraft 1の内容を承認し、親Epic契約と現行Runtime事実に照合して正本化した | `requirement.md`とfresh requirement review pass | execute approved plan |
| EAL-357-002 | adopted | `artifacts/20260809t125146z-draft-design-strict-vertical-slice-design.md` | `design.md` | 承認済み要件を既存layer / model / portへ割り当て、fresh design reviewの精度指摘を反映した | `design.md`とfresh design review pass | execute approved plan |
| EAL-357-003 | adopted | `artifacts/20260809t125147z-draft-plan-strict-vertical-slice-plan.md` | `plan.md` | Draftのvertical sliceをStrict Plan契約へ統合し、closure、failure、delegation、test cardを具体化した | `plan.md`と最終fresh plan review pass | execute approved plan |

未解決のstale / blocked evidenceはない。Draft artifactsは履歴証跡として保持し、正本authorityにはしない。

## Spec Authoring Gate

| phase | investigated facts | open questions / answers | adoption decision | reviewer verdict | blocking | promotion / next_action |
|---|---|---|---|---|---|---|
| requirement | 親Epic R/D/P、承認済みDraft 1、CLI / active / lifecycle / Artifact / validateの現行契約を照合した | none | adopted | pass | no | execute approved plan |
| design | 承認済みRequirement、Runtime layered architecture、既存model / ports、module ownership、failure resultを照合した | none | adopted | pass | no | execute approved plan |
| plan | 承認済みR/D、Strict Plan Guide、全RQ / EC / AC、selector / failure / parity test、step-local delegationを照合した | none | adopted | pass | no | execute approved plan |

## Delegated Draft Evidence

| created_by_role | scope_id | artifact draft path | source_paths | intended_targets | adoption_status | reflected_to | diff_guard_result | integration_result | rejected portions | blockers | reviewer result | promotion decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ChatGPT-use-strict | iss-00357 | `artifacts/20260809t125145z-draft-requirement-strict-vertical-slice-requirement.md` | 親Epic R/D/P、baseline SHA `2c75e0c02cb65a6e74040a72dc161d342d661091`、approved interview decisions | `requirement.md` | adopted | `requirement.md` | pass: canonical diff inspected and reviewer findings integrated | Draft 1 requirement integrated and repository-grounded | none | none | pass | execute approved plan |
| ChatGPT-use-strict | iss-00357 | `artifacts/20260809t125146z-draft-design-strict-vertical-slice-design.md` | `requirement.md`、親Epic Design / Plan、Runtime source layout | `design.md` | adopted | `design.md` | pass: canonical diff inspected and reviewer findings integrated | Draft 1 design integrated with exact model and module boundaries | none | none | pass | execute approved plan |
| ChatGPT-use-strict | iss-00357 | `artifacts/20260809t125147z-draft-plan-strict-vertical-slice-plan.md` | `requirement.md`、`design.md`、Strict Plan Guide、specialist evidence | `plan.md` | adopted | `plan.md` | pass: canonical diff inspected and final plan review passed | Draft 1 plan integrated as executable step-local contract | none | none | pass | execute approved plan |

## Grade Specialist Evidence Gate

| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |
|---|---|---|---|---|---|
| strict | system-architect and implementation-planner | used | system-architectの既存active model / `check_deps` / finish result / copy mechanism / import safety境界を`design.md`へ統合し、implementation-plannerのE00・S01〜S10・S90・H91・S99 slicingを`plan.md`へ統合した | pass | ready |

## Reviewer Gate Status

| phase | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | evidence |
|---|---|---|---|---|---|---|---|
| requirement | requirement phase gate | spec-reviewer | fresh | pass | no | execute approved plan | parent trace、retained CLI、truth table、Historical catalog、validate boundaryを確認 |
| design | design phase gate | spec-reviewer | fresh | pass | no | execute approved plan | model owner、partial result、module dependency deltaを確認 |
| plan | final plan phase gate | spec-reviewer | fresh | pass | no | execute approved plan | findingsなし、overall confidence 0.98、全closure / failure / delegation / test cardを確認 |
| execution E00 review 1 | E00 docs/spec alignment | spec-reviewer | fresh | failed | no | S01 blocked | P1: category / Action / owner重複、report-only wrapper ownership。P2: closure ownerと外周parity evidence |
| execution E00 review 2 | E00 docs/spec alignment re-review | spec-reviewer | fresh | failed | no | S01 blocked | shared bridgeの`dispatch`、command contracts、`build_runtime`、`UseCases.planning_*`、issue-planning graphの明示不足 |
| execution E00 review 3 | E00 docs/spec alignment re-review | spec-reviewer | fresh | pass | no | proceed to M0 commit only | findingsなし、confidence 0.99。排他的symbol inventory、owner / Action、360 handoff、shared planning bridge、test consumer、parity evidenceを確認 |
| execution S01 review 1 | Storage Core CLI surface | code-reviewer | fresh | failed | no | S02 blocked | code findingなし。P1: Workflow-Scoped AuthorizationがE00限定、P2: Closure DeltaのM0 stateがstale |
| execution S01 review 2 | Storage Core CLI surface re-review | code-reviewer | fresh | pass | no | proceed to S02 | findingsなし、confidence 0.99。関連32 tests、provider / dogfood parity、no-write、scopeを確認 |
| execution S02 review 1 | selection-only active | code-reviewer | fresh | failed | no | S03 blocked | P1: S03移行前にretained `issue start` internal checkoutを破壊。P1: projection不在のlegacy snapshotをrollbackすると不要なactive projectionを生成 |
| execution S02 review 2 | selection-only active re-review | code-reviewer | fresh | failed | no | S03 blocked | P1: legacy `.work/{active,current}.json`をtext snapshotするとCRLF bytesとsymlink identityを復元できない。P2: 現在の結論のGreen件数がstale |
| execution S02 review 3 | selection-only active re-review | code-reviewer | fresh | failed | no | S03 blocked | P1: active root symlink時に外部target treeをrollbackしない。P1: `.agent/active.json`をtext snapshotするとCRLF bytesを復元できない |
| execution S02 review 4 | selection-only active re-review | code-reviewer | fresh | failed | no | S03 blocked | P1: managed agent JSONをtext / None snapshotするとCRLF / dangling symlinkを復元できない。P1: repo-qualified selectorがGit portを参照 |
| execution S02 review 5 | selection-only active re-review | code-reviewer | fresh | failed | no | integration correction required | P1: typed pathがdirectoryの場合にchildを失う。P1: issue start dependency guard regression（S03 owner）。P1: minimal manifest後のissue finish regression（S04 owner） |
| execution S03 review 1 | issue start dependency-only lifecycle | code-reviewer | fresh | failed | no | S04 blocked | P1: repo-qualified selectorがS02と不一致で、exact + legacyをambiguous、foreign unique legacyをnot foundにする |
| execution S03 review 2 | issue start dependency-only lifecycle re-review | code-reviewer | fresh | pass | no | proceed to S04 | findingsなし、confidence 0.98。start 18、deps 43、selector identity、order、force、fail-closed、parityを確認 |
| execution S04 review 1 | thin issue finish | code-reviewer | fresh | failed | no | M1 blocked | P1: clear phaseの非`RuntimeError`でpartial diagnosticが失われる。P1: Closure Coverage state矛盾。P1: M1 candidate evidence欠落 |
| execution S04 review 3 | thin issue finish re-review | code-reviewer | fresh | pass | no | proceed to S02 integration review | findingsなし、confidence 0.98。phase order / exception matrix / non-gating / report / M1 evidenceを確認 |
| execution S02〜S04 integration review 1 | active / lifecycle integration | code-reviewer | fresh | failed | no | M1 blocked | Runtime findingなし。P1: reportのS02〜S04 / Delegation / Closure Deltaが過去のpending / correction中stateを残す |
| execution S02〜S04 integration review 2 | active / lifecycle integration re-review | code-reviewer | fresh | failed | no | M1 blocked | P1: temporary Runtime importが`sys.modules`を汚染。P1: reportにstale state。P1: S03 / S04 Delegation Gate欠落 |
| execution S02〜S04 integration review 3 | active / lifecycle integration re-review | code-reviewer | fresh | pass | no | proceed to M1 commit | findingsなし、confidence 0.98。tracked diff / untracked test、149 pass / 23 skip、test isolation、ledger / delegation gateを確認 |
| execution S05 review 1 | Current Artifact creation | code-reviewer | fresh | failed | no | S06 / S07 blocked | P1: `spec-dock/initiatives` root自体が外部directoryへのsymlinkの場合、root検査をすり抜けて外部scopeへArtifact / `rules.md`を書ける |
| execution S05 review 2 | Current Artifact creation re-review | code-reviewer | fresh | failed | no | S06 / S07 blocked | review 1 P1は解消。P1: missing-rulesの既存`artifacts/`で、malformed / 99枯渇検出より先に`rules.md`を作り、failure時no-writeを破る |
| execution S05 review 3 | Current Artifact creation re-review | code-reviewer | fresh | failed | no | S06 / S07 blocked | review 1 / 2 P1は解消。P1: allocation後のsetup / render / write / post-write failureで試行作成pathをrollbackせず、destinationもatomic publishでない |
| execution S05 review 4 | Current Artifact creation re-review | code-reviewer | fresh | failed | no | S06 / S07 blocked | review 1〜3 P1は解消。P1: temp / setupの`lexists`をjournal ownershipと誤認し、競合pathを削除またはdangling symlink先へwriteし得る |
| execution S05 review 5 | Current Artifact creation re-review | code-reviewer | fresh | failed | no | S06 / S07 blocked | P1: claim後temp pathname差替えで別inodeをpublish可能。P1: rollback前のdest / temp / rules / dir差替えをboolean ownershipだけで削除可能 |
| execution S05 review 6 | Current Artifact creation re-review | code-reviewer | fresh | failed | no | S06 / S07 blocked | review 5 P1は解消。P1: preflight後に`artifacts/` pathnameを外部symlinkへ差し替えるとpathname-based temp open / publishが外部scopeへ到達する |
| execution S05 review 7 | Current Artifact creation re-review | code-reviewer | fresh | failed | no | S06 / S07 blocked | review 6 P1は解消。P1: mkdir直後の実directory replacementをpreflight identity `None`で受理。P1: committed publish後のdirfd close失敗をerror返却しretry重複を誘発 |
| execution S05 review 8 | Current Artifact creation re-review | code-reviewer | fresh | failed | no | S06 / S07 blocked | review 7 P1は解消。P1: mkdir `FileExistsError`競合branchで検証directory identityを記録せず、A→B real-directory replacementを受理する |
| execution S05 review 9 | Current Artifact creation re-review | code-reviewer | fresh | pass | no | proceed to S06 / S07 | findingsなし、confidence 0.95。mkdir競合identity、held dirfd、committed cleanup、全Current interface / safety契約を確認 |
| execution S06 review 1 | Historical recognition | code-reviewer | fresh | failed | no | S09 blocked | P1: genericは拡張子任意だが、invalid timestamp / unsafe basenameのdouble-dash non-`.md`をsuffix gateがmalformed診断から除外する |
| execution S06 review 2 | Historical recognition re-review | code-reviewer | fresh | pass | no | P2 correction before closure | P0/P1なし、confidence 0.95。P2: undecodable raw-byte generic basenameがsurrogate escape経由でvalidate / doctorを通る |
| execution S06 review 3 | Historical recognition re-review | code-reviewer | fresh | failed | no | S09 blocked | P1: raw-byte fixtureがmacOS `EPERM` capability rejectionをskipせずfocused suite failure。P2: dangling artifacts symlinkをabsent扱い。P2: report state / count不整合 |
| execution S06 review 4 | Historical recognition re-review | code-reviewer | fresh | pass | no | proceed to S07 / S09 | findingsなし、confidence 0.97。catalog、generic parser、slot ledger、validation / doctor、parity、tests / reportを確認 |
| execution S07 review 1 | Generic file import only | code-reviewer | fresh | pass | no | proceed to S09 after S08 | findingsなし、confidence 0.97。provider固有backendだけの削除、explicit-file safety、opaque bytes、atomic publication、privacy、four scopes、360 wrapperを確認。reviewer独立focusedは`99 passed / 2 platform skipped` |
| execution S08 review 1 | No-Assurance Fresh scaffold | code-reviewer | fresh | failed | no | S09 blocked | P1: dirfd claim後にpathname-based copy / rules / metaがreplacement treeへ書ける。P1: mkdir成功直後のidentity取得失敗でempty destinationが残る |
| execution S08 review 2 | No-Assurance Fresh scaffold re-review | code-reviewer | fresh | failed | no | S09 blocked | review 1 P1は解消。P1: mkdir後からchild identity確定前にhidden staging名を別empty directoryへ置換されると、name-only cleanupが競合directoryを削除し、owned stagingも残り得る |
| execution S08 review 3 | No-Assurance Fresh scaffold re-review | code-reviewer | fresh | failed | no | S09 blocked | P1: mkdir→initial stat間の置換で競合inodeをownedと誤認してwrite / publishする。P1: initial stat失敗時にowned hidden stagingが残る |
| execution S08 contract review 1 | concurrency / recovery boundary spec review | spec-reviewer | fresh | pass | no | implementation may proceed | contractはcoherent / minimalでscope内、confidence 0.97。P2: outer mkdir→identity未確定failure / tampering injectionをtc-s08-001へ明記。P2 correctionをPlanへ反映 |
| execution S08 review 4 | two-layer Fresh scaffold re-review | code-reviewer | fresh | pass | no | P2 correction before closure | P0/P1なし、confidence 0.98。P2: unchanged UTF-8 shebang templateでfd-aware copyがlegacy execute-bit付与を飛ばすためmode parityを補正する |
| execution S08 review 5 | unchanged-shebang correction re-review | code-reviewer | fresh | pass | no | proceed to S09 | findingsなし、confidence 0.98。review 4 P2解消、bytes / atime / mtime保持後の0111付与、two-layer transaction / ports / projection nonregressionを確認 |
| execution S09 code review 1 | Historical consumer invariance | code-reviewer | fresh | pass | no | QA P2 correction before closure | findingsなし、confidence 0.97。legacy content gateだけの除去、9 mutation、Core操作、byte / structure / parity、stale failure scopeを確認 |
| execution S09 QA review 1 | Historical invariance test quality | qa-reviewer | fresh | pass | no | P2 correction before closure | P0/P1なし、confidence 0.96。P2: Core結果をbaseline exact snapshotと比較する。P2: read_text以外のcontent read入口もspyで遮断する |
| execution S09 code review 2 | QA P2 correction re-review | code-reviewer | fresh | pass | no | QA P2 correction before closure | findingsなし、confidence 0.98。exact baseline / durable state、4 read入口spy、negative control、implementation parityを確認 |
| execution S09 QA review 2 | QA P2 correction re-review | qa-reviewer | fresh | pass | no | P2 correction before closure | P0/P1なし、confidence 0.95。P2: legacy active extra fieldsもread-only surfacesではraw byte exactを確認し、start / finishだけ除外する |
| execution S09 QA review 3 | legacy active raw-byte correction re-review | qa-reviewer | fresh | pass | no | proceed to M2 / S10 | findingsなし、confidence 0.98。read-only四surfaceのraw-byte保持、start / finishの正当なwrite除外、9 mutation exact baseline、4 read入口spy、negative controlを確認 |

## Workflow-Scoped Authorization

| authorization source | repo / worktree | active scope | named roles | boundary | result |
|---|---|---|---|---|---|
| ユーザーによるSpecDock workflow利用依頼と2026-08-10の実装開始依頼 | current `spec-dock` checkout | iss-00357 execution E00 | `repo-analyst`、`spec-reviewer`、`git_commit` | current repo / active Issue / current session内のE00 read-only調査、report統合、review、M0 commit。S01 source変更、外部公開、PR、merge、Issue finishは含まない | pass |
| ユーザーによる2026-08-10のapproved Plan完遂指示 | current `spec-dock` checkout | iss-00357 execution S01〜S99 | `dev-coder`、`doc-writer`、`code-reviewer`、`qa-reviewer`、`spec-reviewer`、`git_commit` | current repo / active Issue / current session内のPlan記載source / tests / docs / report、focused / final verification、step / milestone commit。scope外変更、外部公開、push、PR、merge、Issue finishは含まない | pass |

## 実装開始契約

| 最初のstep | 担当 | 入力 | 完了条件 |
|---|---|---|---|
| E00 | `repo-analyst` | approved R/D/P、baseline SHA、Runtime / tests / docs | retained / removed / shared inventoryにpath、symbol、consumer、Action、ownerが揃い、曖昧rowがない |
| S01以降 | stepごとのfresh worker | `plan.md` §8の該当contract | Redまたは代替証拠、Green、report更新、fresh reviewer passをstep単位で満たす |

Issue 358とは同時に進められる。ただしparser / registry / Runtimeは357、template prose / Authoring Guideは358のsingle writerとし、共有contractはIC-1で照合する。

## 計画時の検証結果

- Canonical Requirement review: pass。
- Canonical Design review: pass。
- Canonical Plan final review: pass、findingsなし、confidence 0.98。
- Exact-current R/D/P/report readiness review: pass、findingsなし、confidence 0.99。E00/M0のfresh `spec-reviewer` → commit → clean check契約を確認した。
- `git diff --check`: pass。
- SpecDock `workflow status --format json`: `state=ready`、`reason_code=strict-legacy-missing-assurance`、`artifact_readiness=substantive`。
- SpecDock `deps check --no-github`: `ready=true`、blockerなし。cacheは`stale=true`の警告を返したため、実装開始時に必要ならGitHub同期を更新する。
- SpecDock `validate`: pass、`nodes=221`。
- `uv run pytest tests/unit/domain/test_workflow_state.py tests/cli_runtime/test_workflow.py`: 72 passed、44 skipped。
- 正本とDraft artifactは別物として保持し、Draftをauthorityへ昇格していない。

## 実装記録

E00のread-only inventoryを開始した。source / test変更を伴うS01以降の実装は未着手である。

### E00 実行コンテキスト

- active Issue: `iss-00357`
- branch: `iss-00357-reduce-runtime-to-storage-core`
- current HEAD: `e16e97517ea3ab7287eaf6143fab2df943d71b2d`
- baseline: `2c75e0c02cb65a6e74040a72dc161d342d661091`
- baselineからHEADまでの`src/spec_dock`、`tests`、`spec-dock/scripts`差分: なし
- provider / dogfood Runtime Python manifest: `151 / 151` files、SHA-256 manifest差分なし
- E00開始前の`git status --short`: clean

### E00 Retained inventory

| path / symbol | current consumer / reachability | Action | owner |
|---|---|---|---|
| `scripts/spec-dock` | `spec_dock_runtime.app::main`を起動する通常入口 | Modify in S01 | 357 |
| `app.py::{main,_parse_args,_find_repo_root_for_legacy_doctor}` | 通常CLIのparse / dispatchとdoctor fallback | Modify in S01 | 357 |
| `cli/{parser,registry}.py` | `app.main`の通常CLI parser / registry graph | Modify in S01 | 357 |
| `commands/new.py::{command_specs,_run_new_*}` | `new_{initiative,epic,issue,artifact}`。parserからregistryへ到達 | Modify in S05/S08 | 357 |
| `commands/artifact_import.py::{command_specs,ArtifactImportFileArgs,_add_file_arguments,_file_args_factory,_run_file}` | `artifact_import_file -> UseCases.import_file_artifact` | Modify in S01/S07 | 357 |
| `commands/active.py` | `active_{set,show,clear}` | Modify in S01/S02 | 357 |
| `commands/issue.py` | `issue_{start,finish}` | Modify in S03/S04 | 357 |
| `commands/deps.py` | `deps_{check,add,remove}` | Modify in S03 | 357 |
| `commands/import_cmd.py` | `import_{initiative,epic,issue}` | Keep | 357 |
| `commands/{worktree,workbench,delete,close,update,uninstall,sync,validate,doctor}.py` | Target inventoryの対応leaf | Keep | 357 |
| `application/{set_active,issue_lifecycle,check_deps}.py` | active / start / finish / dependency projection | Modify in S02/S03/S04 | 357 |
| `application/{create_node,create_artifact_doc}.py` | `new.py`のnode / Artifact leaf | Modify in S05/S08 | 357 |
| `application/{import_node,delete_node,close_node,doctor}.py` | retained command handlerから`UseCases`経由 | Modify in S04/S09 | 357 |
| `domain/{active,artifacts,deps,validation,discussion_docs}.py` | retained active / deps / Artifact / node / validation applicationのstatic import | Modify in S02/S03/S05/S06/S09 | 357 |
| `domain/ids.py`の`normalize_id_input`以外、`domain/models.py`のplanning bridge対象以外、`domain/tree.py`の`build_graph`以外 | retained ID / node / tree operations | Modify in S02/S03/S05/S09 | 357 |
| `infra/contracts.py::{ActiveManifest,ActiveManifestEntry}` | `set_active`、`active_store`、`issue_lifecycle` | Modify in S02 | 357 |
| `infra/active_store.py` | bootstrap active storeからretained active / lifecycleへ到達 | Modify in S02 | 357 |
| `presentation/{json_state,markdown,puml}.py`、`presentation/contracts.py`の`CliText`以外 | retained command / application result renderer | Modify in S01/S04/S07/S09 | 357 |
| `presentation/cli_text.py`のprovider Artifact import renderer以外 | retained command / application result renderer（explicit file branchを含む） | Modify in S01/S04/S07/S09 | 357 |
| Runtime retention / projection tests | `tests/cli_runtime/{test_active,test_issue_lifecycle,test_new,test_artifact_import_file,test_validate,test_doctor,test_wrappers}.py` | Modify in corresponding Sxx | 357 |

### E00 Shared inventory — Delete禁止

| path / symbol | retained consumer evidence | Action | owner |
|---|---|---|---|
| `application/import_file_artifact.py::import_file_artifact` | `_run_file -> UseCases.import_file_artifact` | Keep | 357 |
| `cli/dispatch.py::dispatch` | 通常`app.main`と360 `chatgpt_app.main`が同じregistry dispatchを使用 | Keep | 357 |
| `commands/contracts.py::{CommandArgs,CommandOutcome,CommandSpec,CommandRegistry}` | 通常 / ChatGPT parser・registry・command handlerが共有 | Keep | 357 |
| `app.py::_find_specdock_dir` | 通常`app.main`と360 `chatgpt_app.main`が同じrepo-local scope解決を使用 | Keep | 357 |
| `cli/bootstrap.py::{BootstrapContext,build_runtime,_NodeReader,_Clock}`のstructural assembly | 通常`app.main`と360 `chatgpt_app.main`が同じ`Ports` / `UseCases` / context、node reader、clockを構築 | Modify in S01 preserving planning callbacks | 357 |
| `application/validate_tree.py::validate_tree`、`application/sync_state.py::sync` | retained validate / sync commandと360 `build_runtime.planning_apply`のvalidation / sync callbackが共有 | Keep | 357 |
| `application/contracts.py::{ValidateTreeRequest,SyncRequest}` | retained validate / sync commandと360 `build_runtime.planning_apply` callbackが共有 | Keep | 357 |
| `domain/ids.py::normalize_id_input` | retained node / lifecycle pathと360 planning request / contract validationが共有 | Keep | 357 |
| `domain/models.py::{SpecNodeKind,SpecNodeSeed,SpecGraph}`、`domain/tree.py::build_graph` | retained graph pathと`build_runtime.load_planning_state`が共有 | Keep | 357 |
| `infra/contracts.py::{StoredMetaRecord,DirectDependencyResolution}` | retained node / deps pathと360 planning state / dependency snapshotが共有 | Keep | 357 |
| `application/ports.py::{ValidateNodeReader,Clock,Ports.node_reader,Ports.clock}` | retained validate / node / timestamp pathと360 planning state / dependenciesがnode readerとclockを共有 | Keep | 357 |
| `infra/deps_reader.py::load_direct_dependency_resolutions` | retained deps pathと360 `planning_create` dependency loaderが共有 | Keep | 357 |
| `infra/git_cli.py::origin_github_repo_slug` | retained `GitGateway`と360 issue-planning repository resolverが共有 | Keep | 357 |
| `application/contracts.py::UseCases.{create_initiative,create_epic,create_issue,create_artifact_doc,import_initiative,import_epic,import_issue,set_active,show_active,clear_active,sync,check_deps,mutate_deps,delete_node,close_node,issue_start,issue_finish,validate_tree,doctor,worktree_create,worktree_list,worktree_show,worktree_remove,workbench_copy,import_file_artifact}` | 通常registryのretained `CommandSpec.run`が同一`UseCases` instanceを使用 | Modify in S01 | 357 |
| `presentation/contracts.py::CliText` | shared dispatch、通常 / ChatGPT `CommandOutcome` rendererが使用 | Keep | 357 |
| `application/contracts.py::{FileArtifactImport*,ExplicitFileSourcePreflightRequest,ExplicitFileArtifactPublishRequest}` | `import_file_artifact.py`のrequest / result / error | Keep | 357 |
| `application/ports.py::{ExplicitFileSourceGuard,ExplicitFileArtifactPublisher}` | `import_file_artifact.py`が`Ports`経由で使用 | Keep | 357 |
| `infra/binary_artifact_publisher.py::FilesystemBinaryArtifactPublisher` | opaque byte copy、publication、source guard | Keep | 357 |
| `infra/template_scaffolder.py::copy_scaffolded_tree` | bootstrap scaffolderから`create_node.py`へ到達 | Keep | 357 |
| `infra/{fs_repo,git_cli,github_cli}.py`の上記shared symbol以外のstructural adapters | node / deps / start / finish / closeのretained path | Keep | 357 |
| `application/ports.py::{NodeRepository,IssueGateway,GitGateway,ActiveStateStore,TemplateScaffolder}` | bootstrapの対応adapter assemblyとretained use case | Keep | 357 |
| `tests/cli_runtime/test_authoring.py` | removed通常`authoring` CLI casesと360 authoring-pack direct / compatibility coverageが同居 | Modify in S01 preserving 360 cases | 357 |
| `tests/cli_runtime/test_artifact_import_s04.py`、`tests/unit/application/test_binary_artifact_import_ports.py` | provider Artifact importとretained explicit-file branchのcoverageが同居 | Modify in S07 preserving explicit-file cases | 357 |

### E00 Removed inventory — 到達性遮断後のDelete候補

| path / module | current consumer / reachability | Action | owner |
|---|---|---|---|
| `commands/assurance.py` | parser / registryのassurance四leaf | Delete candidate after S01 removes all four registry keys | 357 |
| `commands/authoring.py` | parser / registryのauthoring 11 leaf | Delete candidate after S01 removes authoring registry keys | 357 |
| `commands/workflow.py` | `guidance` / `workflow_status` | Delete candidate after S01 removes both registry keys | 357 |
| `commands/delegated_authoring.py` | delegated-authoring三leaf | Delete candidate after S01 removes all registry keys | 357 |
| `commands/artifact_import.py::{ArtifactImportChatGptOutputArgs,_add_arguments,_args_factory,_run}` | `command_specs`が生成するprovider-specific `artifact_import_chatgpt_output` keyとbootstrap wiring | Delete candidate after S01 removes key and S07 retains file branch | 357 |
| `application/import_artifact.py::import_artifact` | provider-specific command symbolだけがconsumer | Delete candidate after S01 removes `UseCases.import_artifact` wiring | 357 |
| `application/{assurance,workflow,delegated_authoring}.py` | removed command adapterとbootstrap callback | Delete candidate after S01 removes command and bootstrap consumers | 357 |
| `application/contracts.py::{ShowAssuranceRequest,ClassifyAssuranceRequest,VerifyAssuranceRequest,ComposeAssuranceRequest,WorkflowStatusRequest,WorkflowNextRequest,RunbookProjectionResult,WorkflowResult,ArtifactImportRequest,ArtifactImportResult,ArtifactImportError,UseCases.import_artifact,UseCases.show_assurance,UseCases.classify_assurance,UseCases.verify_assurance,UseCases.compose_assurance,UseCases.workflow_status,UseCases.workflow_next,UseCases.repo_root,UseCases.specdock_dir}` | removed command / delegated-authoring application contract。Runbook / WorkflowStateを含むworkflow result typeを明示 | Delete candidate after S01 removes corresponding adapters and bootstrap wiring | 357 |
| `application/ports.py::{WorkbenchSourceGuard,BinaryArtifactPublisher}` | provider-specific Artifact importだけがconsumer | Delete candidate after S07 removes provider import consumers | 357 |
| `domain/authority.py` | `set_active.py`、`issue_lifecycle.py`、`validate_tree.py`、`active_store.py`にretained consumerあり | Delete candidate after S02/S03/S04/S09 detaches every listed consumer | 357 |
| `domain/{assurance,artifact_composer}.py` | assurance commandとprofile template composer | Delete candidate after S05 removes profile/draft routing | 357 |
| `domain/delegated_authoring.py` | `application/delegated_authoring.py`だけがstatic importし、retained / 360 consumerなし | Delete candidate after S01 removes delegated-authoring command / application | 357 |
| `domain/{runbook,workflow_state}.py`、`infra/runbook_store.py` | `application/workflow.py`、`presentation/workflow.py`、bootstrap `workflow_next` wiringだけがconsumer | Delete candidate after S01 removes workflow command / wiring / contracts | 357 |
| `infra/assurance_store.py`、`infra/artifact_store.py::{ArtifactStore,IssueArtifact}` | bootstrapとprofile design / plan template path | Delete candidate after S05 removes profile template consumer | 357 |
| `presentation/{assurance_text,workflow}.py` | removed assurance / workflow command | Delete candidate after S01 removes rendering consumers | 357 |
| `presentation/cli_text.py::{render_artifact_import_text,render_artifact_import_json,render_artifact_import_error_text,render_artifact_import_error_json}` | removed provider Artifact import branchだけがconsumer | Delete candidate after S01 removes provider key and S07 retains explicit file renderers | 357 |
| `tests/cli_runtime/{test_assurance.py,test_assurance_compose.py,test_delegated_authoring.py,test_workflow.py,test_workflow_context_routing.py,test_artifact_import_chatgpt_output.py}` | removed assurance / delegated / workflow / provider import CLIだけをcover | Delete candidate after S01/S07 absence tests replace assertion role | 357 |
| `tests/unit/application/test_assurance.py`、`tests/unit/domain/{test_assurance.py,test_delegated_authoring.py,test_workflow_state.py}`、`tests/unit/infra/test_assurance_store.py`、`tests/unit/presentation/test_assurance_text.py` | removed assurance / delegated / workflow Runtimeだけをcover | Delete candidate after S01 removes corresponding Runtime | 357 |
| `tests/unit/commands/test_artifact_import_chatgpt_output.py`、`tests/unit/presentation/test_artifact_import_chatgpt_output.py` | removed provider Artifact import branchだけをcover | Delete candidate after S07 retains explicit-file tests | 357 |

### E00 360 handoff keep — Current通常CLIの範囲外

| path / symbol | current consumer / reachability | Action | owner |
|---|---|---|---|
| `app.py`の`main` / `_parse_args` / `_find_specdock_dir` / `_find_repo_root_for_legacy_doctor`以外のlegacy helper symbols | current `main()`から未呼出しだが一部runtime testsがmonkeypatch | Handoff keep | 360 |
| `scripts/spec-dock-chatgpt` | 独立executableから`chatgpt_app.main`へ到達 | Handoff keep | 360 |
| `chatgpt_app.py::main` | `build_registry -> build_parser -> build_runtime -> dispatch` | Handoff keep | 360 |
| `cli/chatgpt_parser.py` module全体 | `build_parser` / `_bind_leaf` / `_required_spec`がplanning create / revise / apply / reviewの四keyをbind | Handoff keep | 360 |
| `cli/chatgpt_registry.py` module全体 | `build_registry`が`commands.issue_planning::command_specs()`だけをregistry化 | Handoff keep | 360 |
| `commands/issue_planning.py` module全体 | Args / factories / runners / outputを含み、ChatGPT registryからshared dispatchと`UseCases.planning_*`へ到達 | Handoff keep | 360 |
| `cli/bootstrap.py::{_IssuePlanningGateway,_planning_node_seed,planning_create,planning_revise,planning_review,planning_apply}`とnested `load_planning_state` | `build_runtime`内でissue-planning dependencies、planning graph、四callbackを構築 | Handoff keep | 360 |
| `application/contracts.py::UseCases.{planning_create,planning_revise,planning_review,planning_apply}` | `commands/issue_planning.py::_run_*`が直接呼出し | Handoff keep | 360 |
| `application/issue_planning.py` module全体 | planning request定義、create / revise / review / apply runner、validation / publication helperの定義元 | Handoff keep | 360 |
| `application/ports.py::{VerifiedIssueCandidateView,PublishedCandidateView,PublishedPlanningReviewView,ExpectedPlanningTargetsView,PlanningApplyOperationView,PlanningApplyExecutionView,IssuePlanningCandidateOutputGuard,IssuePlanningCandidateArchiveRejected,IssuePlanningCandidateBuildFailed,IssuePlanningCandidateCollision,IssuePlanningCandidateOutputRejected,IssuePlanningCandidatePublicationFailed,IssuePlanningApplyOutputRejected,IssuePlanningGateway,IssuePlanningDependencies,Ports.issue_planning}` | bootstrapが構築し`application.issue_planning`がstatic importするplanning専用view / guard / error / gateway / dependencies | Handoff keep | 360 |
| `application/issue_planning_prompt.py` | issue-planning prompt assembly | Handoff keep | 360 |
| `domain/{issue_planning_candidate,issue_planning_contracts}.py` module全体 | candidate material、planning contract validation、`PlanningCommandResult`の定義元 | Handoff keep | 360 |
| `infra/{issue_planning_apply,issue_planning_candidate,issue_planning_chatgpt,issue_planning_oracle_artifact,issue_planning_review}.py` | `_IssuePlanningGateway`とplanning closuresのcandidate / backend / review / apply operation | Handoff keep | 360 |
| `presentation/issue_planning.py` module全体 | planning command outputとreview summary | Handoff keep | 360 |
| `{application,domain,infra,presentation}/authoring_pack/**` | `application/issue_planning.py`がpreflight、authority boundary、ZIP contractをstatic import | Handoff keep | 360 |
| `tests/cli_runtime/test_chatgpt_cli.py`、`tests/{unit,integration}/**/test_issue_planning*.py` | ChatGPT parser / dispatch / UseCases / build_runtimeとissue-planning domain / infra / presentation / E2Eの専用tests | Handoff keep | 360 |
| `tests/unit/authoring_pack/**`、`tests/unit/domain/test_authoring_source_manifest_workbench.py`、`tests/manual_tests/{test_prepare_chatgpt_authoring_pack.py,test_review_chatgpt_authoring_pack.py,test_stage_chatgpt_authoring_pack.py,test_validate_issue_candidates.py}`、`tests/fixtures/authoring_pack/**` | 360 issue-planningがstatic importするauthoring-pack contracts / preflight / ZIP / compatibilityの専用test / fixture | Handoff keep | 360 |
| `scripts/authoring-pack/**` | 通常`spec-dock` parser / registry外のdirect shipped scripts | Handoff keep | 360 |
| `src/spec_dock/assets/install_root/**` managed skills | Runtime外のmanaged distribution surface | Handoff keep | 360 |

### E00 観測コマンド

- parser / registry / bootstrap、command key、wrapper、test / docs consumerを`rg`で逆引きした。
- `git diff --quiet 2c75e0c02cb65a6e74040a72dc161d342d661091..HEAD -- src/spec_dock tests spec-dock/scripts`: pass。
- provider / dogfood Runtime Python treeの`find '*.py' | sort | shasum -a 256` manifest比較: `151 / 151` files、差分なし。
- provider / dogfood `scripts/spec-dock-chatgpt`はSHA-256 `5bdaa7fa06d4d2499294e35436946ba369e99bea2122b8d19b11ce997374f082`で一致した。
- provider / dogfood `scripts/authoring-pack/**`は`13 / 13` files、sorted SHA-256 manifest差分なし。
- `domain.authority`のretained static consumerを`set_active.py`、`issue_lifecycle.py`、`validate_tree.py`、`active_store.py`で確認した。
- `spec-dock-chatgpt -> chatgpt_app.py -> cli/chatgpt_{parser,registry}.py`の通常CLI外到達経路を確認し、360 handoff keepへ一意に分類した。
- workerはrepositoryを変更していない。`No material implementation decisions beyond the approved plan.`

### S01 Storage Core CLI surface

- provider authorityとdogfood projectionの`cli/{parser,registry,bootstrap}.py`、`commands/active.py`を同一内容で更新した。
- 通常CLIから`assurance`、`authoring`、`guidance`、`workflow`、`delegated-authoring`、`artifact import chatgpt-output`のparser / registry / bootstrap wiringを除去した。backend moduleの物理削除はS10へ残した。
- `artifact import file`と、`active set`のpositional / `--id` / `--github-issue`を保持し、active setのcheckout / GitHub / force系flagを除去した。
- Red: focused full-regression許可付き実行で`3 failed, 9 passed`。root inventory、removed route到達、active set旧flag残存を検出した。
- Green: `uv run pytest --run-full-regression tests/cli_runtime/test_storage_core_cli.py tests/cli_runtime/test_wrappers.py`は`12 passed`。
- 補助Green: `tests/cli_runtime/test_chatgpt_cli.py`は`13 passed`、`tests/cli_runtime/test_artifact_import_file.py`は`7 passed`、`make lint`はruff / format / mypy pass。
- removed 6 routeとinvalid active targetは実行前後の`spec-dock/` file / symlink tree SHA-256 snapshotが一致し、no-writeを確認した。
- provider / dogfoodの変更4ファイルはbyte一致し、`git diff --check`もpassした。
- `No material implementation decisions beyond the approved plan.`

### S02 Selection-only active

- provider authorityとdogfood projectionの`application/set_active.py`、`infra/{contracts,active_store}.py`を同一内容で更新した。
- `active set`からdependency、cached status、GitHub issue gateway、authority / evidence、checkoutを除去し、blocked Issueとdependency cycleを持つgraphも選択できるようにした。
- `ActiveManifestEntry`を`id` / `path`だけへ縮小した。schema v2は維持し、legacy extra fieldsを許容して読むが、read-onlyではbytesを変えず、次のmutationで各entryを`id` / repo-relative `path`だけへminimal化する。
- Context PackからAuthority、grant、promotion、reviewer / EAL / Planning Level由来のworkflow metadataを除去した。
- `.agent/active.json`、Context Pack、active pointers、managed agent stateに加え、legacy `.work/{active,current}.json`もsnapshot対象とし、manifest / pointer / managed-stateの各phase失敗時に旧snapshotへ復元する。
- Red: S02 focused 7件の旧実装で`5 failed`。deps / Git / GitHub port参照、`ActiveManifestEntry`のextra fields、三write phaseでのlegacy manifest消失を検出した。legacy read-only byte invarianceは既存実装でpassしたためcovered-existing evidenceとした。
- Green: `uv run pytest --run-full-regression tests/cli_runtime/test_active.py tests/unit/application/test_set_active.py tests/unit/domain/test_active.py tests/unit/infra/test_active_store.py`は`29 passed, 23 skipped`。skipはretired deps / checkout semanticsで、S02 obligation replacement casesは実行済みである。
- port spyは`deps=[]`, `derived=[]`, `issue_gateway=[]`, `git=[]`、三write phaseのbefore / after byte・symlink snapshotはすべて一致した。provider / dogfood変更3fileはbyte一致し、ruff / format / `git diff --check`もpassした。
- serialized fixtureはtop-level `schema_version=2` / `updated_at`と、各active entryの`id` / `path`だけをexact assertionした。
- review 1で、S03移行前の`issue start` internal checkout破壊と、projection不在のlegacy snapshot rollbackが不要なactive projectionを生成するP1二件を検出した。公開`active set`へcheckout flagを戻さず内部requestだけを互換維持し、`active/`全体を存在状態・種別・file bytes・symlink target込みでsnapshot / restoreする修正を加えた。
- 修正後の独立Greenは、focused 4-suiteとretained lifecycle checkoutを合わせて`34 passed, 23 skipped`。projectionあり / なし×manifest / pointers / managedの6 rollback cases、内部checkout、provider / dogfood byte一致を確認した。
- review 2でlegacy `.work/{active,current}.json`のtext snapshotがCRLF bytesとsymlink identityを失うP1を検出した。両fileを存在状態・種別・raw bytes・symlink targetとして保存 / 復元する形へ統一し、CRLF regular file / symlink×projection有無×manifest / pointers / managedの12-case Red→Greenを追加した。独立再実行は`40 passed, 23 skipped`。
- review 3で、`spec-dock/active`自体がdirectory symlinkの場合にlink先treeがsnapshotされず、また`.agent/active.json`はtext snapshotのためCRLF bytesが正規化されるP1二件を検出した。root symlink identityとexternal target tree、agent manifestの種別付きsnapshot / restoreを追加した。
- review 3のP1に対し、active root symlinkのtarget文字列と参照先のmanaged childrenを別々にsnapshot / restoreし、unmanaged external contentは変更しないようにした。`.agent/active.json`も存在・種別・raw bytes・symlink target / referent stateで復元する。新規9 cases、既存legacy 12 cases、focused suiteを合わせた独立Greenは`49 passed, 23 skipped`。
- review 4で、`.agent/{index-all,tree-all,index,tree}.json`のtext / None snapshotがCRLF / dangling symlinkを復元できず、repo-qualified `--github-issue`だけがlocal Git portへ触れるP1二件を検出した。managed agent filesのtyped snapshot統一と、target / graph metadataだけによるselector解決を修正した。
- review 4のP1に対し、managed 4 JSONを存在・種別・raw bytes・symlink target / referent stateで復元し、unmanaged external siblingを触らないよう統一した。repo-qualified selectorはexact scoped候補を優先し、なければ一意なunscoped legacy候補だけをnetwork / Git非参照で解決する。0件 / 複数件は明示errorかつno-writeである。独立Greenは`63 passed, 23 skipped`。
- review 5のS02-owned P1に対し、agent active / legacy 2 / managed 4 pathがdirectoryの場合もnested file raw bytes、empty directory、symlink targetを再帰snapshot / restoreする。symlink先は走査せずlink identityだけを保持する。新規directory matrix Green後のS02 focused結果は`66 passed, 23 skipped`。
- `No material implementation decisions beyond the approved plan.`

### S03 Issue start and dependency-only readiness

- provider authorityとdogfood projectionの`application/{contracts,issue_lifecycle,set_active}.py`、`commands/issue.py`、`presentation/cli_text.py`を同一内容で更新した。
- startの順序をtarget validation→unfinished guard→shared dependency check→checkout→active write→syncへ固定し、readinessはexisting `check_deps`を再利用した。`active set`へreadinessを戻していない。
- OPENな別active Issueはmain / Issue / non-Issue / detached branchの全てでblockし、UNKNOWN / linkなし / fetch失敗はfail-closedとする。`--force`はunfinished guardだけを迂回し、invalid targetとdirect / inherited blockerは迂回しない。
- checkout失敗時はactive write / syncを呼ばず、checkout成功後のactive persistence失敗はS02 transactional rollbackを使い、branch side effectとrecoveryを表示する。成功後のsyncは一回だけである。
- Red: 初期suiteでS03-owned `3 failed`中2件がforce dependency bypass、追加truth-table / order test後にcall-order helper 3件とmain / non-Issue branch guard 2件が失敗した。S04-owned promotion expectation 1件はwrong-step failureとして分離した。
- 独立Green: `uv run pytest --run-full-regression tests/cli_runtime/test_issue_lifecycle.py -k 'issue_start and not then_finish'`は`18 passed, 17 deselected`、`tests/unit/application/test_check_deps.py tests/unit/domain/test_deps.py`は`39 passed`。
- S03対象ruff / format / mypy、provider / dogfood変更5file byte parity、`git diff --check`はpassした。全体mypyで検出したS02 testの型注釈1件もS02 workerが補正した。
- review 1でrepo-qualified selectorがS02と異なり、exact scoped + unscoped legacy同番号をambiguous、foreign explicit repo + unique legacyをnot foundとするP1を検出した。exact scoped優先→unique unscoped fallbackへ三経路を統一し、初回resolve後はcanonical node IDをdeps / activeへ渡して再解決をなくした。追加4 selector cases後のdeps Greenは`43 passed`、startは`18 passed`を維持した。
- `No material implementation decisions beyond the approved plan.`

### S04 Thin issue finish

- provider authorityとdogfood projectionの`application/issue_lifecycle.py`を同一内容で更新し、`issue finish`を`close_node(run_post_sync=false)`→`clear_active`→`post_mutation_sync`だけへ縮小した。
- authority / promotion transition、Report / EAL、Design / Plan delegated metadataのreadとclose前transition writeを除去し、新gate / 新例外階層 / 新result contractは追加していない。
- OPENはclose→clear→syncで`already_closed=false`、CLOSEDはclose確認→clear→syncで`already_closed=true`。close失敗はactive保持 / sync未実行、clear失敗はGitHub closed確定 / active残存 / sync未実行、sync失敗はGitHub closed / active cleared / projection staleを既存result / diagnosticで区別する。
- Red: `uv run pytest --run-full-regression tests/cli_runtime/test_issue_lifecycle.py -k issue_finish`は旧`missing_authority` gate / guidanceにより`9 failed, 20 deselected`。
- Green: 同commandは`10 passed, 19 deselected`。thin / heavy Report、Assurance、EAL、Design / Plan metadataを変えてもfile-read zero、port calls / result不変、close前transition write zeroである。
- full lifecycleで残ったS01 obsolete `active set --checkout` success testをremoved flag rejection / active JSON・pointer・branch・git status・GitHub log no-writeへ置換し、独立再実行は`29 passed`。
- `make lint`、provider / dogfood parity、`git diff --check`はpassした。
- review 1でclear phaseの`PermissionError` / `OSError`がrawに漏れてpartial diagnosticを失うP1を検出した。`Exception`（`KeyboardInterrupt` / `SystemExit`を除外）をphase errorへ変換し、RuntimeError / PermissionError / OSError×OPEN / CLOSEDの6組合せでclosed確定、active残存、sync未実行、exact guidanceを固定した。finish `10 passed`、full lifecycle `29 passed`を維持した。
- `No material implementation decisions beyond the approved plan.`

### S01〜S04 Integration verification

- `uv run pytest --run-full-regression tests/cli_runtime/test_storage_core_cli.py tests/cli_runtime/test_wrappers.py`: `12 passed`。
- `uv run pytest --run-full-regression tests/cli_runtime/test_active.py tests/unit/application/test_set_active.py tests/unit/domain/test_active.py tests/unit/infra/test_active_store.py`: `65 passed, 23 skipped`。skipはretired deps / checkout semanticsで、replacement obligationsはunit / lifecycleで実行済みである。
- `uv run pytest --run-full-regression tests/cli_runtime/test_issue_lifecycle.py`: `29 passed`。
- `uv run pytest --run-full-regression tests/unit/application/test_check_deps.py tests/unit/domain/test_deps.py`: `43 passed`。
- `make lint`: ruff check / format / mypy `290 source files` pass。
- provider / dogfood対象は各stepのbyte parityを維持し、`git diff --check`もpassしている。
- integration review 2で、`test_storage_core_cli.py`のtemporary Runtime direct importがparent pytest processの`sys.modules`を汚染し、後続provider unit importを壊すP1を検出した。registry inspectionを独立Python subprocessへ移し、再現pairはRed `1 passed, 1 failed`→Green `2 passed`、Storage Core / wrapperは`12 passed`、lint / diff checkもpassした。

### Step Contract Closure

| step | closure ids | planned close condition | observed evidence | result | notes |
|---|---|---|---|---|---|
| E00 | `CL-357-001/012/013` | retained / removed / shared inventoryの全rowにpath、symbol、consumer、Action、ownerがある | 本reportのE00 inventory、provider / dogfood `151 / 151` manifest一致、baseline差分なし、動的wrapper到達性、retained authority consumer、fresh review pass、M0 commit `51b1590`、post-commit cleanを確認 | closed | baseline evidenceはS01 / S10 / H91の各owner closureへ引き継ぐ |
| S01 | `CL-357-001/015` | retainedだけが到達可能、removed routeはparser error / no-write、active selector syntaxを保持 | Red `3 failed, 9 passed`→Green `12 passed`、関連32 tests、lint、provider / dogfood変更file一致、fresh re-review pass 0.99 | closed | `CL-357-001` closed。`CL-357-015`のactive set側はpass、issue start側はS03でcloseする |
| S02 | `CL-357-002/003/015` | blocked targetをport非参照で選択し、minimal stateをtransactionalに保存する | 初回Red `5 failed / 7`。review 1〜5のS02-owned P1を各Red再現し、integration active `65 passed, 23 skipped`、fresh integration review pass 0.98 | closed | S03 / S04 correction、test isolation、ledger同期を含めてclose |
| S03 | `CL-357-004/014/015` | validation→guard→deps→checkout→active→sync、forceはguardだけ、deps projection一貫 | Redでforce bypass / branch依存 / order / selector不一致を検出。Green start `18 passed`、deps `43 passed`、lint / parity、fresh re-review pass 0.98 | closed | canonical node identityを全phaseで維持。`CL-357-004/014/015` closed |
| S04 | `CL-357-005` | close→clear→sync、phase結果とevidence independence | Red `9 failed`→Green finish `10 passed`、full lifecycle `29 passed`、clear exception 6-case、file-read / transition write zero、lint / parity、fresh review pass 0.98 | closed | `CL-357-005` closed |
| S05 | `CL-357-006` | optional positional typeでCurrent六種だけを作成し、invalid / Historical / filesystem unsafe条件ではno-write | review 1〜8 P1を修正。mkdir競合2、review 7 / body-primary / directory-swap 7、replacement 6、race / transaction / identity 11、helper full 65、mandatory 31、lint / parity、fresh review 9 pass 0.95 | closed | 極小TOCTOU、commit後closeの一時descriptor leak、process kill / power loss後orphanは非blocking残余risk |
| S06 | `CL-357-010` | explicit Historical catalogをrecognize-onlyとし、真のmalformed / duplicate / unsafeだけ診断、既存path / bytes不変 | review 1〜3 correction Green。domain 45、focused 38 / capability skip 1、doctor 44、S05 helper 65、actual validate / doctor、lint / parity、fresh review 4 pass 0.97 | closed | raw non-UTF8実診断は許容POSIX filesystemで実走。macOSはsentinel成功後EILSEQ capability skip。scope外stale force test 1件 |

### Test Contract Closure

| test id | step | evidence level | pre-implementation evidence | verification path | observed result |
|---|---|---|---|---|---|
| `tc-e00-001` | E00 | inspect-only | baselineと現在HEADのRuntime / tests / scripts差分なし | parser / registry / wrapper / import / consumer逆引き、Runtime Python / wrapper / authoring-packのprovider / dogfood比較 | pass: symbol単位で排他的分類、Action / ownerは単一、曖昧rowゼロ、条件未達のDelete候補を明示 |
| `tc-s01-001` | S01 | red-required | 旧surfaceでroot inventory / removed routeが`3 failed` | `uv run pytest --run-full-regression tests/cli_runtime/test_storage_core_cli.py tests/cli_runtime/test_wrappers.py` | pass: `12 passed`、removed route no-write、360 wrapper保持 |
| `tc-s01-002` | S01 | red-required | 旧`active set` helpにcheckout / GitHub / force flagが残存 | 同focused suiteのselector / invalid target cases | pass: 三selector保持、旧flag不在、invalid target snapshot不変 |
| `tc-s02-001` | S02 | red-required + covered-existing | 旧実装でdeps / Git / GitHub port参照とextra fields残存を検出。legacy read-only byte invarianceは既存pass | blocked target / dependency cycle、fail-fast spies、exact schema v2 JSON、legacy read-only hashと次mutation、Context Pack forbidden token | pass: selection成功、全spy call zero、entryは`id` / `path`だけ、read-only byte不変、次mutation minimal化 |
| `tc-s02-002` | S02 | red-required | manifest / pointer / managed-state各phaseの旧rollbackでlegacy manifest消失 | 各phase injection、manifest / Context Pack / pointers / managed state / legacy `.work`のbefore / after比較 | pass: 三phaseすべてbyte・symlink snapshot一致、partial stateなし |
| `tc-s03-001/002` | S03 | red-required | selector / invalid / force / lookup limit matrixを追加 | positional / id / GitHub Issue、invalid通常 / force、port order / no-write | pass: selector互換、invalidはvalidationで停止、lookup limit維持 |
| `tc-s03-003` | S03 | red-required | force dependency bypassとbranch依存guardをRed再現 | OPEN/CLOSED/UNKNOWN/linkなし/fetch失敗×branch、direct / inherited blocker前後 | pass: branch非依存fail-closed、forceはunfinished guardだけ、shared deps結果一致 |
| `tc-s03-004/005` | S03 | red-required | checkout / active persistence failure order spyを追加 | checkout failure before/after snapshot、checkout後active failure + rollback / diagnostic | pass: premature write / syncなし、rollback一致、branch side effect / recovery明示 |
| `tc-s04-001` | S04 | red-required | 旧authority gateによりphase matrixが`9 failed` | OPEN / CLOSED、close / clear / sync failure call-orderとexact result / diagnostic | pass: focused `10 passed`、phase確定状態を区別 |
| `tc-s04-002` | S04 | red-required | legacy evidence mutation fixtureを追加 | thin / heavy Report、Assurance、EAL、delegated metadataのfile-read spy / result comparison | pass: read zero、port calls / result不変、close前write zero |
| `tc-s05-001` | S05 | red-required | `CURRENT_CREATABLE_ARTIFACT_TYPES`不在とomitted type parser failureをRed再現 | omitted / explicit blank / five typed、filename exact、same-second deterministic suffix | pass: Current六種成功、blank type tokenなし、same-secondは共有slotで決定的suffix |
| `tc-s05-002` | S05 | red-required | invalid / path / transaction、claim / inode / directory replacementに加え、review 8でmkdir競合A→B replacementをRed `1 failed`で再現 | negative CLI / domain test、before / after tree比較、partial artifact不在、competitor identityと外部tree不変、committed result明示 | pass: mkdir競合2、review 7 / body-primary / directory-swap 7、replacement 6、race / transaction / identity 11。競合directoryは検証identityに固定するがowned扱いしない |
| `tc-s06-001` | S06 | red-required | initial parser Red 18、generic Red 6 / 1、surrogate Red 1、dangling symlink Red `1 failed / 2 passed`を再現 | typed / sequential / generic / Discussion positive、malformed / duplicate / live / dangling symlink negative、前後path / SHA-256比較 | pass: domain 45、focused 38 / raw capability skip 1、doctor 44。dangling target不存在とlink target不変、全managed fixture mutationなし |
| `tc-s07-001` | S07 | covered-existing + delta | generic import既存matrixは`43 passed / 7 policy skip`。追加absence testは残存`application/import_artifact.py`を検出してRed | four scopes、UTF-8 / binary byte exact、symlink / traversal / unsafe basename / collision / publisher failure、partial / cleanup、captured output privacy、removed backend / symbol absence、360 wrapper | pass: focused `121 passed / 1 platform skip`、removed provider reachabilityなし、provider / dogfood Runtime parityと`git diff --check` pass、fresh review pass 0.97 |
| `tc-s08-001` | S08 | red-required | initial partial copy / meta Red 2、review 1〜3でpathname write、identity residue / cleanup、mkdir→initial identity窓を検出。two-layer deltaはcross-dirfd helper不在をRed `1 failed`、review 4 P2はunchanged shebang mode差`0640 / 0751`をRed `1 failed / 3 passed`で再現 | Initiative / Epic / Issue exact manifest、Assurance access spy、outer / payload 12-phase failure、canonical file / dir / symlink collision、concurrent same-ID、tampering、post-commit close、unchanged / rendered / shebang mode parity | pass: S08 / template 83、Fresh CLI 38 / skip 5、S09 retained 65、lint / parity / diff-check、fresh review 5 pass 0.98 |
| `tc-s09-001` | S09 | red-required | delegated authority / EAL parserへのfile-read spy付き8 content variantsが旧実装で8 / 8失敗。QA P2補正でtoken-only assertionとread_text-only spyの検出力不足を確認し、exact比較が`updated_at`差を検出 | 9-token個別mutation、active / deps / start / finish / validate / doctorのbaseline exact process / durable state、read-only Historical raw bytes、4 content-read入口、required Report欠損negative control | pass: focused 35 / skip 1、exact lifecycle 9、doctor / spy 18、validate / deps 34、lint / parity / diff-check、fresh code review 2 pass 0.98 / QA review 3 pass 0.98 |

### Delegated Worker Evidence

| step | delegated role | worker summary | changed files | tests or docs-only verification | reviewer verdict | unresolved risks | integration decision |
|---|---|---|---|---|---|---|---|
| E00 | `repo-analyst` | 初回inventoryを作成し、2回のreview fail後のfollow-upでsymbol単位の排他的分類、shared bridge、単一Action / owner、360 handoff keep、外周parityを確定した | none | read-only `rg` / import / manifest / wrapper / authoring-pack inspection | review 1 / 2 failed; fresh review 3 passed with no findings (0.99) | reviewer確認済みの未解決riskなし | revised evidence adopted; proceed to M0 commit |
| S01 | `dev-coder` | Red-firstで通常CLI registration / help / active selectorをStorage Coreへ縮小し、360 planning bridgeを保持した | provider / dogfood Runtime各4file、`test_storage_core_cli.py`、`test_wrappers.py` | focused Red / Green、関連32 tests、lint、no-write snapshot、projection byte比較 | review 1 report-only fail後、fresh re-review pass 0.99 | backend物理削除はS10、active内部semanticsはS02 | adopted; S01 closed |
| S02 | `dev-coder` | Red-firstでactiveからreadiness / authorityを分離し、review 1〜5のtyped rollback / selector findingsを修正した | provider / dogfood Runtime各3file、`test_active.py`、`test_issue_lifecycle.py`、`test_set_active.py`、`test_active_store.py` | 全selector spies、exact JSON、legacy byte invariance、全rollback matrix、integration active 65 / 23 skipped | S02 P1修正済み、S03/S04 pass、fresh integration review 3 pass 0.98 | unresolved Runtime riskなし | adopted; S02 closed |
| S03 | `dev-coder` | startをbranch非依存guardとshared dependency-only readinessへ移し、review P1のselector identityを統一 | provider / dogfood Runtime各6file、`test_issue_lifecycle.py`、`test_check_deps.py` | start 18、deps 43、projection正負、make lint、parity | review 1 failed; fresh re-review pass 0.98 | S04でfinish regression解消済み、未解決riskなし | adopted; S03 closed |
| S04 | `dev-coder` | finishをclose / clear / syncへ縮小し、review P1の非Runtime clear failureをphase diagnosticへ統一 | provider / dogfood `issue_lifecycle.py`、`test_issue_lifecycle.py` | Red 9→Green 10、clear 6-case、full lifecycle 29、make lint、parity | review 1 failed; fresh re-review pass 0.98 | none known | adopted; S04 closed |
| S05 | `dev-coder` | Current六種catalogとoptional positionalを実装し、review 1〜8のfilesystem P1をidentity / dirfd-bound transactionとcommitted warningへ修正 | provider / dogfood Runtime各3file、`test_new.py`、`test_runtime_new_doc_s09.py`、`test_artifacts.py` | mandatory 31、helper full 65、mkdir競合2、review 7 / body-primary / directory-swap 7、replacement 6、race / transaction / identity 11、lint / parity | review 1〜8 failed、fresh review 9 pass 0.95 | S01-retired import testsはS07 owner。極小TOCTOU / descriptor leak / process killは非blocking | adopted; S05 closed |
| S06 | `dev-coder` | Historical catalogをrecognize-only parser / ledger / doctor diagnosticへ実装し、generic-intent / out-of-band境界をfixture化 | provider / dogfood Artifact / doctor / validation、`test_artifacts.py`、`test_validate.py` | all Red controls、domain 45、focused 38 / skip 1、doctor 44、S05 helper 65、actual validate / doctor、lint / parity | review 1 failed、review 2 pass with P2、review 3 failed、review 4 pass 0.97 | raw integration capability差、scope外stale force test | adopted; S06 closed |
| S07 | `dev-coder` | generic explicit-file importと共有safety primitiveを保持し、provider-specific ChatGPT output import backend / contract / route / rendererだけを撤去 | provider / dogfood Runtime各6fileとbackend削除、provider専用test 3file削除、混在testのprovider case整理、absence delta test | Red absence、focused `121 passed / 1 platform skip`、S05 60、S06 173 collected exit 0、wrappers 9、lint / parity / diff-check | fresh review pass 0.97 | full unitのscope外stale 3件（撤去済みforce 1、旧planning fixture欠落2） | adopted; S07 closed |
| S08 | `dev-coder` | Fresh三scopeのno-Assurance経路をfd-aware outer / payload transactionとatomic cross-dirfd publicationへ補正 | provider / dogfood Runtime各5file、`test_new.py`、`test_runtime_new_s08.py`、template / dogfood consumer tests | initial Red 2、review 1〜3 P1、two-layer Red 1、mode P2 Red 1、S08 / template 83、Fresh CLI 38 / skip 5、S09 retained 65、lint / parity / diff-check | review 1 / 2 / 3 failed、review 4 pass with P2、fresh review 5 pass 0.98 | accepted boundary: same-UID tampering / crashではidentity不明hidden orphanを許容しcompetitor保全。dead wiringはS10 owner | adopted; S08 closed |
| S09 | `dev-coder` | validateからlegacy authority / EAL content gateだけを除去し、9-token E2E / file-read / structural negative matrixを追加 | provider / dogfood `validate_tree.py`、unit validate、CLI validate / doctor / lifecycle、shared S09 fixture | Red 8 / 8、focused 35 / skip 1、unit 10、validate / deps 34、legacy active exact lifecycle 9、lint / parity / diff-check | code review 2 pass 0.98、QA review 3 pass 0.98 | broader stale failures 3件はS01撤去済み`active set --force`期待 | adopted; S09 closed |

### Implementation Delegation Gate

| step | decision | required reason | delegated role | delegated scope | source of truth | allowed changes | forbidden changes | required verification | stop conditions | output required | observed result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E00 | delegated | Runtime inventoryの横断read-only分析が必要 | `repo-analyst` | retained / removed / shared inventory | approved `requirement.md` / `design.md` / `plan.md` | read-only repository inspectionとmainによるreport統合 | source / tests / docs / metadata / deps / active / Git mutation | `tc-e00-001` inspect evidence | owner不明、公開surface変更、retained consumerを持つDelete候補 | inventory、path / symbol evidence、risk、next action | pass: source mutationなし、evidence統合済み、fresh review pass |
| S01 | delegated | CLI / Runtime / testsの複数layer変更 | `dev-coder` | Storage Core CLI surface | approved R/D/P、E00 inventory | parser / registry / bootstrap / active command args、dogfood projection、focused tests | backend削除、lifecycle / active serialization、docs / template / skill / installer、360 planning path、report | focused Red / Green、wrapper / import regression、lint、no-write | inventory変更、shared bridge破壊、scope外source | changed files、Red / Green、no-write、risk、decision note | pass: bounded diff、required tests、fresh code review pass |
| S02 | delegated | active application / persistence / testsの複数layer変更 | `dev-coder` | selection-only active | approved R/D/P、S01 pass | `set_active.py`、active contracts / store、Context Pack、dogfood projection、focused tests | issue start / finish semantics、metadata migration、通常`active set` checkout、docs / template / skills / installer、report | `tc-s02-001/002`、全selector spies、typed rollback matrix、focused / integration suite、projection parity | locked schema変更、read-only migration、readiness再導入、scope外source | changed files、Red / Green、serialized fixture、port calls、rollback、risk | all corrections / integration checks / fresh review 3 pass |
| S03 | delegated | lifecycle / deps / selector / testsの複数layer変更 | `dev-coder` | dependency-only issue start | approved R/D/P、S02 selection-only contract | lifecycle / check_deps / selector contracts / presentation / tests / dogfood projection | finish、dependency force bypass、active readiness、templates / docs / report | start truth table、deps suite、order / failure spies、projection parity、lint | unknownをfinished扱い、selector意味変更、新dependency semantics、scope外source | changed files、Red / Green、truth table、order、risk | review 1 P1修正、fresh review pass 0.98、S03 closed |
| S04 | delegated | lifecycle phase / partial result / testsの複数layer変更 | `dev-coder` | thin issue finish | approved R/D/P、minimal manifest contract | finish lifecycle / close / clear / sync / result presentation / tests / dogfood projection | start / deps、evidence parse、新completion gate、templates / docs / report | OPEN / CLOSED、三phase failure、evidence mutation、full lifecycle、lint / parity | durable state / new gate必要、phase order変更、scope外source | changed files、phase matrix、result snapshots、risk | review 1 P1修正、fresh review pass 0.98、S04 closed |
| S05 | delegated | Artifact domain / application / filesystem / testsの複数layer変更 | `dev-coder` | Current Artifact creation | approved R/D/P、S01 CLI surface | `commands/new.py`、`application/create_artifact_doc.py`、`domain/artifacts.py`、artifact store / presentation、tests、dogfood projection | template prose、Historical routing、`analysis`追加、`--type`追加、generic import、skills / installer / report | `tc-s05-001/002`、focused CLI / domain suite、before / after no-write、lint / parity | catalog / template不一致、shared primitive変更がS07へ影響、locked expectation変更 | changed files、Red / Green、type / failure matrix、risk、IC-1 note、decision note | all corrections / required checks / fresh review 9 pass、material decisionなし、S05 closed |
| S06 | delegated | Artifact parser / validation / doctor / testsの複数layer変更 | `dev-coder` | Historical recognition | approved R/D/P、S05 pass | Historical parser / ledger / structural diagnostic、tests、dogfood projection | existing file mutation、Current creation / navigation、template、generic import behavior、report | `tc-s06-001`、Artifact domain、validate / doctor、SHA-256不変、S05 regression、lint / parity | catalog外format追加、data migration、validation弱体化 | changed files、catalog matrix、Red / Green、不変hash、risk、decision note | all corrections / required checks / fresh review 4 pass、DEC-357-S06-004維持、S06 closed |
| S07 | delegated | import application / filesystem publisher / contracts / testsの複数layer変更 | `dev-coder` | Generic file import only | approved R/D/P、S05 pass | explicit-file command / use case / ports / publisher / presentation、provider-specific backend削除、tests、dogfood projection | Current create、template、Historical mutation、privacy output拡大、360 planning wrapper | `tc-s07-001`、generic import CLI / application / publisher / privacy / absence、lint / parity | opaque contract変更、新external publishing、shared primitiveまたは360 consumer破壊 | changed / deleted files、existing coverage、absence Red、Green、risk、decision note | bounded implementation / required checks / fresh review pass、material decisionなし、S07 closed |
| S08 | delegated | create-node / copy / rollback / testsの複数layer変更 | `dev-coder` | No-Assurance Fresh scaffold | approved R/D/P、358-owned template tree read-only | create-node application、existing template / node repository portのbounded fd-aware extension、focused tests、dogfood projection | template prose、Profile / Assurance、installer / skill、generic import、report | `tc-s08-001`、three-scope manifest、access spy、outer / payload failure / collision / concurrency / tampering / mode parity、lint / parity | template content mismatch、新file contract、scope外dead wiring deletion | changed files、Fresh manifest、Red / Green、rollback、IC-1 input、risk、decision note | pass: two-layer + mode correction Green、fresh review 5 pass 0.98 |
| S09 | delegated | legacy content gate除去と横断invariance testが必要 | `dev-coder` | Historical consumer invariance | approved R/D/P、S03 / S04 / S06 / S07 / S08 pass | validate / doctor structural path、必要なlegacy consumer removal、integration / unit tests、dogfood projection | fixture rewrite / delete、Historical削除、structural validation弱体化、docs / template | `tc-s09-001` mutation snapshot / file-read spy / structural negative、focused、lint / parity | data migration、meaningful structural rule変更、owner Issue不一致 | changed files、mutation matrix、negative control、risk、material decision | pass; fresh code review 2 / QA review 3、`CL-357-009` closed |

### Closure Coverage

| closure range | owner steps | planning evidence | implementation evidence | state |
|---|---|---|---|---|
| `CL-357-001` | S01 | E00 baseline registry / import inventory | removed route parser / registry / help不在、no-write、retained / 360 wrapper positive、fresh code review pass | closed |
| `CL-357-002/003` | S02 | minimal schema v2、selection-only、transactional rollback | exact `id` / `path` serialization、blocked target positive、全selector spies zero、legacy read-only byte不変、全typed rollback、S03/S04 integration checks、fresh review pass | closed |
| `CL-357-004/014/015` | S03 | lifecycle truth table、dependency-only readiness、selector / invalid no-write | start 18、deps 43、force / order / failure spies、canonical selector identity、shared check_deps / projection、fresh review pass | closed |
| `CL-357-005` | S04 | thin finish order / partial result / evidence non-gating | finish 10、full lifecycle 29、clear exception matrix、phase spies、file-read zero、provider / dogfood parity、fresh review pass | closed |
| `CL-357-012` | S10 | E00 provider / dogfood parity inventory | Runtime Python `151 / 151`、wrapper hash、authoring-pack `13 / 13`一致 | baseline evidence only; not closed |
| `CL-357-013` | H91 | E00 owner / destination inventory | 360 handoff keepのpath / symbol / reachability / parity evidence | baseline evidence only; not closed |
| `CL-357-006` | S05 | Current六種とfilesystem safety matrix | 全Current type / filesystem matrix、mandatory / lint / parity、fresh review 9 pass 0.95 | closed |
| `CL-357-010` | S06 | Historical catalog / malformed / preservation matrix | catalog / malformed / unsafe / SHA / actual repo / lint / parity、fresh review 4 pass 0.97 | closed |
| `CL-357-007` | S07 | opaque import / failure / privacy matrix | four scopes、byte exact、source safety、collision、atomic publish / cleanup、private output、removed backend absence、lint / parity、fresh review pass 0.97 | closed |
| `CL-357-008` | S08 | Fresh three-scope scaffold / rollback matrix | four-doc exact、Assurance access zero、fd-bound outer / payload、12-phase failure、canonical collision、concurrent same-ID、tampering boundary、mode / consumer parityがGreen | closed: fresh review 5 pass 0.98 |
| `CL-357-009` | S09 | legacy evidence mutation invariance | 9-token baseline exact process / durable state、read-only Historical raw-byte exact、4 content-read入口 zero、required path negative、focused / lint / parityがGreen | closed; code review 2 pass 0.98 / QA review 3 pass 0.98 |
| `CL-357-011` | S90 | docs / migration ownership | Plan S90 closure contract | not started |

### Closure Delta

| change | closure ids | reason | plan amendment required | re-review required | current result |
|---|---|---|---|---|---|
| execution sequencing only | `CL-357-002/003/004/005/014/015` | S02 review 5でS03/S04-owned lifecycle regressionを検出したため、M1前の計画済み責務へ直接収束する | no | completed | S02〜S04 closed、integration Runtime checks / test isolation / fresh review 3 pass |

### Docs Impact Resolution

| step | target | planned verification | current state |
|---|---|---|---|
| S90 | 357-owned Runtime reference / migration docs | help照合、relative-link scan、fresh spec review | not started |

### Milestone / Commit Candidate Gate

| milestone / step | reviewer verdict | commit candidate / scope | closure state | commit evidence | post-commit clean check |
|---|---|---|---|---|---|
| M0 / E00 | fresh `spec-reviewer` docs/spec alignment pass、findingsなし、confidence 0.99 | `docs(iss-00357): Runtime baseline inventoryを記録` / E00 report evidence | committed | `51b15905218706dcfa689c6765439aee30c785b2` | pass: `git status --short` clean |
| M1 / S01〜S04 | S01〜S04 closed、integration 149 pass / 23 retired skip、fresh review 3 pass 0.98 | `refactor(runtime)!: Storage Core lifecycleを縮小` / S01〜S04 source・tests・report | committed | `d1c16c4dd099c94eabb6e7b2677b4dd148d6fbb6`、hook pass、32 files | pass: commit直後`git status --short` clean |
| M99 / S99 | not reviewed because execution has not started | `docs(iss-00357): 最終実装証跡を確定` / final report ledger | planned | not created because execution has not started | not run |

## 残余リスクと停止条件

- Runtime削除対象にretained consumerが見つかった場合はE00で停止する。
- `domain.authority`とprofile Artifact経路はretained consumerが残っているため、現時点でDeleteしない。S02 / S04 / S05 / S08 / S09でconsumerを外してからS10で再判定する。
- `spec-dock-chatgpt`、issue-planning Runtime、direct authoring scripts、legacy helperは357では削除せず、360へhandoffする。
- schema v2互換、GitHub partial failure、Artifact path safety、Existing Historical preservationのlocked expectationを変えない。
- Issue 358のtemplate / Guide内容を357から修正しない。IC-1 mismatchはcontentとmechanismへ一意にroutingする。
- PR、merge、Issue close、Epic完了は別workflowであり、本報告では許可・実行しない。

## 次のアクション

S05〜S09をM2 checkpointへ確定し、S10のE00-approved unreachable module deletion / provider-dogfood parityへ進む。
