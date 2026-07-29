---
種別: 実装報告書（Issue）
ID: "iss-00344"
タイトル: "Workbench Shell Scaffolding"
関連GitHub: ["#344"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-29"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00343", "init-local-00002"]
---

# iss-00344 Workbench Shell Scaffolding — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

> `report.md` は観測証跡台帳（observed evidence ledger）の scaffold です。planned requirements、evidence destination、closure 条件は `plan.md` が持ち、この文書は実際の Red / Green / Refactor evidence、発見された tests、closure delta、reviewer status、commit/no-op evidence を記録する evidence slot です。workflow / compliance authority は skills、docs、accepted ADRs、reviewer gates に置きます。

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger / 必須）

`report.md` は実装中・文書更新中に発生した material な仕様解釈、判断、plan 逸脱、tradeoff、open question、promotion / follow-up を記録する audit trail でもある。worker の raw note や作業 transcript を貼る場所ではなく、orchestrator が source docs、diff、tests、reviewer output と照合して issue-level の canonical entry に統合する。

Material な判断がない場合もこの section は残し、次を明示する。

- No material interpretation changes.
- No decision entries.

Ledger entry は次の契約値を使う。

- `Status`: `open` / `resolved` / `superseded`
- `Type`: `interpretation` / `scope` / `implementation` / `compatibility` / `test-strategy` / `operation` / `deviation` / `follow-up`
- `Disposition`: `applied` / `rejected` / `promoted_to_design` / `promoted_to_adr` / `promoted_to_plan` / `converted_to_followup` / `deferred` / `no_action` / `superseded`

完了時の意味論（completion semantics）:
- issue completion 前に `Status=open` の entry を残してはならない。
- `Status=resolved` は `Disposition`、evidence、必要な follow-up を持つ。
- `Status=superseded` または `Disposition=superseded` は置換先 entry ID を持つ。
- `Disposition=promoted_to_design` / `promoted_to_adr` / `promoted_to_plan` は昇格先 artifact と evidence を持つ。
- `Disposition=converted_to_followup` は follow-up issue / discussion / ADR candidate の参照を持つ。
- `Disposition=deferred` は scope 外である理由、blocking でない根拠、revisit 条件を持つ。
- `Disposition=no_action` は issue-local な判断で追加対応不要である理由を持つ。将来も効く durable decision を `report.md` だけに閉じ込めてはならない。

Disposition ごとの必須証跡:
- `applied`: 変更した artifact / 実装証跡と、issue-local 適用で十分な理由。
- `rejected`: 却下した選択肢、理由、blocking impact が残らない根拠。
- `promoted_to_design` / `promoted_to_adr` / `promoted_to_plan`: 昇格先 artifact 参照と証跡。
- `converted_to_followup`: follow-up issue / discussion / ADR candidate 参照と blocking / non-blocking の分類。
- `deferred`: scope-out 理由、non-blocking の根拠、revisit 条件。
- `no_action`: 判断が issue-local で durable ではない理由。
- `superseded`: 置換先 entry ID と置換理由。

| 識別子（ID） | 状態（Status） | 種別（Type） | 起票元（Raised By） | 契機 / 差分（Gap） | 検討した選択肢 | 判断 / 解釈 | 根拠（Rationale） | 処置（Disposition） | 証跡（Evidence） | フォローアップ（Follow-up） |
|---|---|---|---|---|---|---|---|---|---|---|
| D-001 | resolved | scope | user / Epic 343 | `.gitkeep` では Workbench の用途と境界を伝えられない | `.gitkeep`; tracked README; directory only | fresh root と future node に tracked `.workbench/README.md` を生成し、既存 scope は変更しない | 親 Epic の採用済み要件とユーザー承認に一致する | applied | `../../requirement.md`; `requirement.md` | design と plan で実装・検証境界を具体化する |
| D-002 | resolved | compatibility | ChatGPT authoring / local source inspection | tracked README と ignored payload の worktree 間移動を混同するリスク | automatic copy; README 専用 copy; Git checkout + manual opaque copy | README は通常 checkout、ignored payload だけを必要時に `workbench copy` で移す | Git tracking と既存 one-shot copy の責務が分離される | applied | `artifacts/20260728t153458z-chatgpt-output-chatgpt-issue-00344-planning-candidate.md`; `requirement.md#I344-RQ-007` | requirement PASS 後に合成する `design.md` へ反映する |
| D-003 | resolved | interpretation | ChatGPT requirement review F-001 | `spec-dock artifact import file` が global installer CLI と repo-local runtime のどちらか曖昧 | installer dispatch; shorthand; repo-local exact command | repository root から `./spec-dock/scripts/spec-dock artifact import file ...` を実行する契約へ限定 | current console script と Issue 345 ownership を誤解させない | applied | `artifacts/20260728t155212z-chatgpt-output-chatgpt-issue-00344-requirement-review.md`; `requirement.md#I344-RQ-003` | fresh re-review |
| D-004 | resolved | compatibility | ChatGPT requirement review F-002/F-003 | no-backfill と source-wins copy の受け入れ条件が過大・競合 | root 全体不変; Workbench 状態限定; README filter; conditional source-wins | no-backfill の不変対象を README / Workbench state に限定し、copy は identical / divergent の2ケースへ分割 | parent Epic と現行 runtime contract に一致する | applied | `requirement.md#AC-344-005`; `requirement.md#AC-344-007A`; `requirement.md#AC-344-007B` | fresh re-review |
| D-005 | resolved | scope | ChatGPT requirement third review F-007 | root と node の共通 README が `workbench copy` の root support を示唆する | root route 追加; guidance 分離; helper scope 明示 | tracked README は root/node とも checkout、helper は Initiative/Epic/Issue の node-scoped ignored payload のみ、root ignored payload は対象外と固定 | existing CLI と親 Epic の compatibility ownership に一致する | applied | `artifacts/20260728t162105z-chatgpt-output-chatgpt-issue-00344-requirement-third-review.md`; `requirement.md#I344-RQ-007`; `requirement.md#AC-344-007C` | fresh re-review |
| D-006 | resolved | deviation | user | 通常のSub-agent reviewerではなく、各stepの前後でChatGPT-Useを全面活用する実行方法が指定された | 通常Sub-agent reviewer; ChatGPT advisoryだけ追加; reviewer責務をChatGPT-Useで実行 | reviewer名を責務契約として維持し、push済みexact commitをChatGPT-UseがJSON reviewするoverlayをplanへ追加する | 実装scopeとclosure contractを変えず、ユーザー指定の高深度reviewと過剰実装抑制を両立できる | promoted_to_plan | `plan.md#11-chatgpt-first-execution-overlay`; user instruction on 2026-07-29 | F-001〜F-004を限定修正し、新exact commitへfresh reviewする |
| D-007 | resolved | scope | user / ChatGPT-Use delivery-boundary analysis | ユーザーがIssue 344の全実装完了とmerge可能なPRを要求した一方、旧planはdogfood projection/default lane/PRをIssue 346へ一括deferしていた | 旧deferを維持; Issue 346を前倒し; Issue 344へ自身のrelease closureだけを移す | Issue 344はchanged managed assetsのprovider-first projection、default PR lane、ready PR、exact-head observationを所有し、candidate wheel/integrated dogfood/opt-in full regression/Epic-wide review/残余Epic PRはIssue 346へ残す | default suiteの既知mirror parity failureをIssue 344自身で閉じつつ、generic importとEpic integrationのvertical ownershipを維持できる | promoted_to_plan | `artifacts/20260729t052200z-chatgpt-output-issue-344-delivery-boundary-amendment-analysis.md`; `requirement.md#I344-RQ-011`; `design.md#DES-344-010`; `plan.md#s95--provider-first-dogfood-projection--default-pr-lane`; parent `../../plan.md#11-issue-344-delivery-amendment` | canonical amendmentをcommit/pushし、fresh ChatGPT-Use `spec-reviewer`責務reviewで承認する |
| D-008 | resolved | test-strategy | dev-coder / parent orchestrator | S02 baselineのfull CLI laneで8 failure。S01後はfuture nodeに`.workbench/README.md`が存在するため、旧fixtureの`.workbench`不存在前提がsetup段階で失敗した | 即時STOP; production変更; assertion緩和; allowed test内のfixture修復 | missing/empty/malformed Workbenchをtemporary fixture内で明示的に再構成し、既存error shape・atomicity・source-wins assertionを維持したtest-only repairを採用する | failureはproduction path到達前のstale fixtureで、S01のapproved shell contractとS02の既存compatibility contractを両立する最小修正である | applied | `tests/cli_runtime/test_workbench.py`; baseline `8 passed / 8 failed`; repaired full lane `18 passed`; parent rerun `18 passed` | production failureが現れた場合はfixture repairを戻しplan/designへ戻る。現時点では追加follow-upなし |
| D-009 | resolved | test-strategy | ChatGPT-Use code-reviewer / parent orchestrator | S02 candidate `f06bbc6ee383345b7fa41420998f391fe254f478` のfresh reviewでmajor 2件。empty-source fixtureはtargetも既存空directoryにしてdestination creationを観測できず、mixed opacity fixtureは通常の非ADR Markdownを欠いていた | finding却下; production変更;新規matrix追加; existing 2 test filesだけのbounded fixture repair | CR-S02-001/002を全採用。sourceをexisting empty、targetをmissingとするpreconditionを明示し、既存mixed fixtureへ`notes.md`を1件追加する | いずれもapproved TC-344-006/009の直接的な観測gapであり、productionや抽象化を変えずに修正できる | applied | failed review `artifacts/20260729t064805z-chatgpt-output-s02-code-review-f06bbc.md`; PASS re-review `artifacts/20260729t070400z-chatgpt-output-s02-code-rereview-2917610b.md`; parent rerun unit `6 passed` / full CLI `18 passed`; Ruff/format pass | fresh re-reviewでCR-S02-001/002はclosed。追加follow-upなし |
| D-010 | resolved | implementation | ChatGPT-Use S03 concretization / parent orchestrator | broad `exclude-package-data`を残したexplicit includeはsetuptools priority上成立せず、broad exclusion削除後はexisting custom sdistのstale README防御も必要。host pytest processからの`importlib.resources`はcheckoutを読む偽陽性になり得る | broad exclude維持; sdist検証をIssue 346へ延期; new build backend; existing build_py/sdistとisolated subprocessを局所拡張 | broad README patternをpyproject/setupから削除し4 exact hidden assetsをincludeする。build_pyとexisting custom sdistへ同じexact five-path predicateを適用し、installed resourceはrepository外isolated subprocessで観測する | locked five-pathやbackendを変えず、既存Issue 69 regressionとTC-344-008を同時に満たす最小実装でありplan amendmentは不要 | applied | `artifacts/20260729t072457z-chatgpt-output-s03-implementation-test-concretization-9a5c08a5.md`; local `pyproject.toml` / `setup.py` / Issue 69 helpers照合 | exact allowlist変更、新backend/dependency、repository内build output、network要求が出たらSTOPしてplanへ戻る |
| D-011 | resolved | test-strategy | dev-coder / parent orchestrator | S03 required full installer fileは`3 passed / 554 skipped / 2 failed`。failureは`spec-dock/.gitignore`と`spec-dock/templates/**`のchecked-in dogfood mirrorがS01 provider assetsへ未投影である2 exact parity nodeのみ | S03でdogfoodを手修正; S03停止; failureを隠す; approved S95へowner維持 | S03のexact distribution nodes、Issue 69 packaging regressions、static checksを閉じたcandidateを維持し、mirror projection/default lane greenはprovider-first `uv run spec-dock update .`を所有するS95へ残す | dogfood projectionはS03 forbidden pathでありS95の明示責務。fresh code reviewは`valid_s95_handoff`と判定し、S03 package config/build outputの欠陥ではないことを確認した | deferred | parent rerun exact S03 `2 passed`; full installer `3 passed / 554 skipped / 2 failed`; `artifacts/20260729t074802z-chatgpt-output-s03-code-review-59d4fdf6.md`; S95 TC-344-011 | S95でprovider-first projection後に同full file/default suiteをgreenにする。final PR前のrisk waiverではない |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | partially_adopted | ChatGPT authoring (`gpt-5.5-pro`, GitHub Connector, evidence-only) | `requirement.md` | 親 Epic と local source に整合する要件、受け入れ条件、境界を採用。実装順序と具体設計は design / plan phase まで未採用 | `artifacts/20260728t153458z-chatgpt-output-chatgpt-issue-00344-planning-candidate.md`; SHA-256 `3eec9fd0865d452aa59e6faa883fb8c07c074e606790af76b94aab255f560835`; 85,422 bytes | ChatGPT requirement review と fresh `spec-reviewer` review |
| EAL-002 | adopted | `artifact import chatgpt-output` command | Issue Artifact | Workbench に保存した ChatGPT 完全回答を opaque bytes のまま Issue Artifact へ保存した | import receipt: `status=ok`, `import_kind=chatgpt-output`, `storage_identity=blank`, `committed=true`, `cleanup_state=removed` | なし |
| EAL-003 | adopted | ChatGPT requirement review (`FAIL`, advisory) | `requirement.md`, `report.md` | F-001〜F-004 をすべて blocking finding として採用し、command boundary、no-backfill、copy compatibility、report state を修正した | `artifacts/20260728t155212z-chatgpt-output-chatgpt-issue-00344-requirement-review.md`; SHA-256 `037acab9142ae0128ef01b79ef51334edaf7c9285af6b09dec2b7f4283910be1`; 9,229 bytes | commit / push 後に fresh ChatGPT re-review と fresh `spec-reviewer` review |
| EAL-004 | adopted | ChatGPT requirement re-review (`FAIL`, advisory) | `requirement.md`, `report.md` | F-005 の残存 root-wide immutability を managed provider update 可能な境界へ修正し、F-006 の premature design promotion claim を撤回した | `artifacts/20260728t160531z-chatgpt-output-chatgpt-issue-00344-requirement-rereview.md`; SHA-256 `c0a35277c3f3322b16269bbf3d60d88043fbe8aa31da1ee9701ddf4b9c7f5ffb`; 7,890 bytes | commit / push 後に fresh ChatGPT re-review と fresh `spec-reviewer` review |
| EAL-005 | adopted | ChatGPT requirement third review (`FAIL`, advisory) | `requirement.md`, `report.md` | F-007 を採用し、root/node checkout、node-scoped copy helper、root helper exclusion を明示した | `artifacts/20260728t162105z-chatgpt-output-chatgpt-issue-00344-requirement-third-review.md`; SHA-256 `48a0cd7dae46233be5e8283d7698a6460c2c20798c55553a6d6667ea1d9cf281`; 6,133 bytes | commit / push 後に fresh ChatGPT re-review と fresh `spec-reviewer` review |
| EAL-006 | adopted | ChatGPT requirement final review (`PASS`, advisory) | `requirement.md`, `report.md` | commit `1087ea15` を connected GitHub app で確認した fresh review。blocking finding なし、F-007 と親 Epic / current copy contract の整合を確認した | `artifacts/20260728t164218z-chatgpt-output-chatgpt-issue-00344-requirement-final-review.md`; SHA-256 `756b70eb67743c7d4fa87ce98ee1e3acad9c97fefd00fd9ea192aab6beddca49`; 6,115 bytes | fresh `spec-reviewer` requirement review |
| EAL-007 | adopted | fresh `spec-reviewer` requirement review (`PASS`) | `requirement.md`, `report.md` | P0/P1なし。P2のChatGPT external evidence / delegated draft lane誤分類を修正し、requirement phaseをapprovedとした | reviewer output on commit `2e0bb6ae`; `requirement.md`; Delegated Draft Evidence row | assurance classify / design compose |
| EAL-008 | partially_adopted | ChatGPT planning candidate design section (`advisory`) | `design.md` | reviewed requirement、parent Epic、local sourceと照合し、freshness、template recursion、ignore、opacity、copy compatibility、distribution exact allowlist、docs責任をStandard designへ統合 | `artifacts/20260728t153458z-chatgpt-output-chatgpt-issue-00344-planning-candidate.md`; `.assurance.json` authorized profile `standard` | commit / push 後に ChatGPT design review と fresh `spec-reviewer` review |
| EAL-009 | adopted | ChatGPT design review (`FAIL`, advisory) | `design.md`, `report.md` | B-001〜B-003とNB-001を採用。Git trackingをpathname contractへ限定し、canonical README完全本文、generic byte-stable materialization、package inventory探索rootを設計へ固定した | `artifacts/20260728t170651z-chatgpt-output-chatgpt-issue-00344-design-review.md`; SHA-256 `53d496a9f09008f1a5623611035daf982e4f8a62a0901c80f450c55f3b49355f`; 10,259 bytes | commit / push 後に fresh ChatGPT design re-review と fresh `spec-reviewer` review |
| EAL-010 | adopted | ChatGPT design re-review (`FAIL`, advisory) | `design.md`, `report.md` | B-004/B-005とNB-002を採用。canonical本文へscope `artifacts/` destinationを追加し、wording変更をdesign amendment + fresh reviewへ統一し、template subtree相対5pathを固定した | `artifacts/20260728t172049z-chatgpt-output-chatgpt-issue-00344-design-rereview.md`; SHA-256 `99f4a67dc3917b9a10d20d8ab559d65c769e7b80c872311e079e8f2a3054fa81`; 12,450 bytes | commit / push 後に fresh ChatGPT design re-review と fresh `spec-reviewer` review |
| EAL-011 | adopted | ChatGPT design final review (`FAIL`, advisory) | `design.md`, `report.md` | B-006を採用。`setup.py` のcustom `build_py` post-build pruneをsource map、DES-344-008、責任表、TC-344-008、rollbackへ追加し、exact allowlist保存とstale nested README除去を両立させた | `artifacts/20260728t174335z-chatgpt-output-chatgpt-issue-00344-design-final-review.md`; SHA-256 `8777a0d837309d71e7326f659407afa1b6cc27c069ec7ed42e02e9d643f11b76`; 9,571 bytes | commit / push 後に fresh ChatGPT design re-review、その後 fresh `spec-reviewer` review |
| EAL-012 | adopted | ChatGPT design post-B-006 review (`PASS`, advisory) | `design.md`, `report.md` | connected GitHub appでcommit `dae3c3485cd29e63e72a3258178f186160e9ceb3`を確認したfresh review。blocking/non-blocking findingなし。active `setup.py` build boundary、exact five-path allowlist、stale nested README除去、actual post-build prune検証、rollback、Issue 344/346 ownershipを確認した | `artifacts/20260728t175913z-chatgpt-output-chatgpt-issue-00344-design-post-b006-review.md`; SHA-256 `d7d6dc3554be93d4b7f68a31e9df3791a632eda6136aac21031d28cdba15a2a5`; 8,488 bytes | fresh `spec-reviewer` design review |
| EAL-013 | adopted | fresh `spec-reviewer` design review (`PASS`) | `design.md`, `report.md` | commit `46794734b3b2067c9c3bf64508feaf1f36fdb325`を独立レビュー。findingなし。要件・親Epic・provider/build境界・exact five-path allowlist・検証・rollback・advisory laneの整合を確認し、design phaseをapprovedとした | reviewer output; `design.md`; `report.md`; commit `46794734b3b2067c9c3bf64508feaf1f36fdb325` | assurance再分類 / plan compose |
| EAL-014 | partially_adopted | ChatGPT planning candidate plan section (`advisory`) | `plan.md`, `report.md` | 3つのvertical micro-batch、Spec-Locked Closure、TDD、focused evidence、Issue 346 handoffを採用し、approved requirement/design、3-rule ignore、B-006 `setup.py` post-build prune、current Standard templateへ正規化した | `artifacts/20260728t153458z-chatgpt-output-chatgpt-issue-00344-planning-candidate.md`; SHA-256 `3eec9fd0865d452aa59e6faa883fb8c07c074e606790af76b94aab255f560835`; 85,422 bytes | commit / push 後にChatGPT plan review、その後fresh `spec-reviewer` plan review |
| EAL-015 | adopted | ChatGPT plan review (`FAIL`, advisory) | `plan.md`, `report.md` | B-001/B-002を採用。generic exact-copy実装をallowed surface/Closure/TDDへ追加し、path-agnostic unchanged-byte copyとplaceholder renderを固定した。custom build prune、temporary build、wheel/sdist/installed inventory、scoped static checksをexact test node/commandとEVDへ結び付けた | `artifacts/20260728t182343z-chatgpt-output-chatgpt-issue-00344-plan-review.md`; SHA-256 `1eeebfc9532b00c1304ce5a7c048c6ead855c2da7b3793d27b72f992a168696b`; 12,617 bytes | commit / push 後にfresh ChatGPT plan re-review、その後fresh `spec-reviewer` plan review |
| EAL-016 | adopted | ChatGPT plan re-review (`PASS`, advisory) | `plan.md`, `report.md` | connected GitHub appでcommit `1c98baabbde0cf9a7535cd91d6760012439e5e24`を確認したfresh review。B-001/B-002解消、blocking/material/non-blocking findingなし。generic exact-copyとdistribution/static実行契約、EVD、sibling/human boundaryを確認した | `artifacts/20260728t183939z-chatgpt-output-chatgpt-issue-00344-plan-rereview.md`; SHA-256 `dcb0e93513f7be284c5fed9ad87fbd6e829659b5f18f27c9582fb5fe5aa7191e`; 9,260 bytes | fresh `spec-reviewer` plan review |
| EAL-017 | adopted | fresh `spec-reviewer` plan review (`FAIL`) | `plan.md`, `report.md` | P1 4件/P2 1件を採用。各S01/S02/S03/S90/S99へstep-local delegation contract、具体テストケースcard、step closure/gate、depends/unblocks/targets/commit候補を追加し、Closure Indexをrequired/observable/locked/bug/evidenceへ拡張した。Active TDDはfresh initからGit observationまでのvertical tracerへ変更し、新規scaffolder test pathをallowed surfaceへ追加した | reviewer output on commit `f5e7f77daad6de89bd2f34a62a4abcefe40e678b`; `plan.md`; `docs/authoring/issue-plan.md`; `docs/phase_plan_issue.md` | assurance再分類、commit / push 後にfresh ChatGPT plan re-review、その後fresh `spec-reviewer` re-review |
| EAL-018 | adopted | ChatGPT plan schema re-review (`FAIL`, advisory) | `plan.md`, `report.md` | B-001〜B-003を採用。S90/S99へstep-local behavior/planned contractを追加し、S99のreport→三者review→result approval→mandatory final commit→clean checkを固定した。docs ownershipをS90へ統一し、4 canonical READMEはS01-owned/S90 read-onlyとした | `artifacts/20260728t190320z-chatgpt-output-chatgpt-issue-00344-plan-schema-rereview.md`; SHA-256 `ce0a3e4d8ebb2ada6e58cb2d6c98b37187e0d2fcdb5bcf4cae8babb992ac3a62`; 13,718 bytes | assurance再分類、commit / push 後にfresh ChatGPT plan re-review、その後fresh `spec-reviewer` re-review |
| EAL-019 | adopted | ChatGPT final plan schema review (`FAIL`, advisory) | `plan.md`, `report.md` | B-004を採用。S99のfinal commit SHAを同じcommit内のreportへ追記する循環契約を解消し、final commit前のreport ledgerとcommit後の外部引き渡し証跡を分離した。EVD-009/010はreviews/handoffのまま維持する | `artifacts/20260728t192021z-chatgpt-output-chatgpt-issue-00344-plan-final-schema-review.md`; SHA-256 `9f0d193c9e271904c8b8f302aee00b1ea6f2af02839aaa9da43328f0961d3a98`; 10,377 bytes | assurance再分類、commit / push 後にfresh ChatGPT plan re-review、その後fresh `spec-reviewer` re-review |
| EAL-020 | adopted | ChatGPT plan B-004 final review (`FAIL`, advisory) | `plan.md`, `report.md` | B-004解消PASSを確認し、追加blocking B-005/B-006を採用。S90のPython testとdocs変更をdev-coder/code-reviewer、doc-writer/spec-reviewerへ順序分離し、TC-344-005を全no-backfill triggerのexact before/after snapshotへ拡張した | `artifacts/20260728t193842z-chatgpt-output-chatgpt-issue-00344-plan-b004-final-review.md`; SHA-256 `f41eeb8198206c5f5fcbbf5d944e39dab715a235d3ba7a09424c941ba119bed0`; 15,087 bytes | assurance再分類、commit / push 後にfresh ChatGPT plan re-review、その後fresh `spec-reviewer` re-review |
| EAL-021 | adopted | ChatGPT plan B-005/B-006 final review (`FAIL`, advisory) | `plan.md`, `report.md` | B-004/B-005/B-006の主要修正PASSを確認し、B-005-R1/B-007を採用。delegated workerのcanonical report write permissionを除去してmain orchestrator統合へ戻し、Ruff check/format exact path listへ`tests/cli_runtime/test_new.py`を追加した | `artifacts/20260728t195703z-chatgpt-output-chatgpt-issue-00344-plan-b005-b006-final-review.md`; SHA-256 `14ce2594144499d708a792b9d11ec390975795380c66518b9e0eaa42da7b0194`; 14,735 bytes | assurance再分類、commit / push 後にfresh ChatGPT plan re-review、その後fresh `spec-reviewer` re-review |
| EAL-022 | adopted | ChatGPT final plan pass review (`FAIL`, advisory) | `plan.md`, `report.md` | B-001〜B-007のclosureを確認し、B-008を採用。S01/S02/S03/S90をreview→actual commit/approved-no-op→clean→close state→Result Approval→next-step admissionの順へ統一し、S99のpre-commit判断をfinal evidence commit authorizationへ限定した | `artifacts/20260728t201813z-chatgpt-output-chatgpt-issue-00344-plan-final-pass-review.md`; SHA-256 `1fced0dc948df5ee1e836f49b5de1d3ddd259d08a1af676dc1b335ac673cbd6f`; 15,114 bytes | assurance再分類、commit / push 後にfresh ChatGPT plan re-review、その後fresh `spec-reviewer` re-review |
| EAL-023 | adopted | ChatGPT plan B-008 final review (`FAIL`, advisory) | `plan.md`, `report.md` | B-001〜B-007/B-005-R1とB-008 step内部順序のclosureを確認し、B-008-R1を採用。依存グラフをS01→S02→S03→S90→S99へ一本化し、S99 predecessorをResult Approval済みかつ`committed|approved-no-op`へ固定した | `artifacts/20260728t203308z-chatgpt-output-chatgpt-issue-00344-plan-b008-final-review.md`; SHA-256 `77763002eaa0f85196948ca9afad3b9d543bc5bdff93cfc2be687842caf28f9a`; 13,529 bytes | assurance再分類、commit / push 後にfresh ChatGPT plan re-review、その後fresh `spec-reviewer` re-review |
| EAL-024 | adopted | ChatGPT terminal plan review (`PASS`, advisory) | `plan.md`, `report.md` | connected GitHub appでcommit `00ee3da37a6f75d60969989c8370cba0231adf2c`を確認したfresh terminal review。B-001〜B-008-R1/B-005-R1は全てCLOSED、blocking/non-blocking findingなし。一本道のResult Approval admission、S99 predecessor close state、external-only final evidenceを確認した | `artifacts/20260728t204554z-chatgpt-output-chatgpt-issue-00344-terminal-plan-pass.md`; SHA-256 `fa09700bc8b5bb15b130b89d1b2ef48621879dc08db2f29115c0aac612a806b9`; 14,525 bytes | fresh `spec-reviewer` plan review |
| EAL-025 | adopted | fresh `spec-reviewer` plan review (`PASS`) | `plan.md`, `report.md` | commit `85de9b37a6bacc1ddf56664ac50d3fa42ac8b8ef`を独立レビュー。blocking/material findingなし、`review_status: pass`。P3のS01 Red seed名表記差をexact nodeへ正規化し、plan phaseをapprovedとした | reviewer output; `plan.md`; terminal ChatGPT PASS artifact; parent Epic/workflow/authoring docs | assurance再分類 / planning completion。実装は本依頼のscope外 |
| EAL-026 | adopted | user-specified ChatGPT-First execution method | `plan.md`, `report.md` | step scopeとclosure contractを維持し、pre-step具体化Artifact、担当共有、push済みexact commitのJSON review、finding採否、非循環なevidence-only closure commitを追加した。fresh review PASS後にplanをapprovedへ戻した | `plan.md#11-chatgpt-first-execution-overlay`; D-006; merge commit `3829600aa304ee76c6e8dcfbe31d2b6b2511927b`; EAL-027/EAL-028 | assurance再分類後にS01 pre-step具体化を開始する |
| EAL-027 | adopted | ChatGPT-Use fresh plan amendment review (`FAIL`, advisory) | `plan.md`, `report.md` | commit `41073c582575d6af70a60a95a56203a63b07064d`をGitHub同期後にreview。F-001〜F-003をblocking/majorとして採用し、candidate review commit→fresh review→evidence-only closure commitの非循環順序、S90のrole分離、blocking/major 0のPASS条件へ限定修正した。F-004も採用し、旧PASSをstaleとしてcurrent readinessをblockedへ同期した | `artifacts/20260729t032949z-chatgpt-output-chatgpt-first-plan-review-41073c58.md`; SHA-256 `8715545fe690431dc5d9e1dc43023283a8d07e75a7e9979cff39ae8455f4f4c0`; reviewed commit `41073c582575d6af70a60a95a56203a63b07064d` | 修正をcommit/pushし、新exact SHAへfresh ChatGPT-Use `spec-reviewer`責務review |
| EAL-028 | adopted | ChatGPT-Use fresh plan amendment re-review (`PASS`, advisory) | `plan.md`, `report.md` | GitHub同期後のexact commit `a0b99765f7fac5ad384f4f81c85b50990f017fc9`をreviewし、finding 0件。F-001〜F-004の解消、非循環SHA境界、S90 role分離、blocking/major 0のPASS条件、prior PASS stale/current blocked同期、機能scopeとIssue 345/346境界不変を確認した | `artifacts/20260729t034457z-chatgpt-output-chatgpt-first-plan-rereview-a0b99765.md`; SHA-256 `9abadebc2beed093c34e399527ba3f57711154123cba1c4dbfbdc729721283f3`; reviewed commit `a0b99765f7fac5ad384f4f81c85b50990f017fc9` | planをapprovedへ戻し、assurance再分類、S01 admission |
| EAL-029 | partially_adopted | ChatGPT-Use S01 implementation/test concretization (`advisory`) | S01 implementation handoff | GitHub同期済みexact commit `f1446111ac52c6cfc1783f513ea679dbd72ab1ae`から、pre-mutation freshness、4 canonical assets、installer prune、provider/fallback 3-rule ignore、render後bytes同一時のpath-agnostic exact-copy、既存node recursion利用、Red/Green/verification観点を採用した。提示された個別test名は新規候補であり、10 caseをそのまま必須本数にはせず、approved TC-344-001/002A/B/003/004/005を最小本数で閉じる。Issue 346所有のbare full regression、package E2E、PR deliveryは採用しない | `artifacts/20260729t042156z-chatgpt-output-s01-implementation-test-concretization-f1446111.md`; SHA-256 `4830ec0323a5f87667ce0bcc35fa13974d4efcd97fe7b3bfa33e60c3d2e1e920`; source commit `f1446111ac52c6cfc1783f513ea679dbd72ab1ae` | Artifactとapproved S01 contractを`dev-coder`へ共有し、allowed paths内でRed→Green→focused verificationを実行する |
| EAL-030 | adopted | ChatGPT-Use S01 implementation review (`PASS`, advisory) | S01 review gate | GitHub同期済みexact candidate commit `a62ae20d5ad587563bf09de77b1f85d75a64c4ec`を`code-reviewer`責務でreviewし、finding 0件、scope creepなし、不要な抽象化なし、`next_action=proceed`を確認した。default fast suiteのmirror parity 2 failureはS01 defectではなくIssue 346へのdeferred integration factとして採用した | `artifacts/20260729t045553z-chatgpt-output-s01-implementation-code-review-a62ae20d.md`; SHA-256 `5bda9e6c613e7e4b6796e90569b2d84fdca019d0d1da8c8fadc52f4d12ec1f56`; reviewed commit `a62ae20d5ad587563bf09de77b1f85d75a64c4ec` | evidence-only closure commit、clean確認、S01 Result Approval |
| EAL-031 | partially_adopted | ChatGPT-Use delivery-boundary amendment analysis (`advisory`) | `requirement.md`, `design.md`, `plan.md`, parent Epic `plan.md`, `report.md` | Issue 344自身のprovider-first projection/default lane/ready PR/observationを採用し、S95とTC-344-011、EVD-012/013を追加した。Issue 346に残すcandidate wheel/integrated dogfood/opt-in full regression/Epic-wide review/残余Epic PRも採用した。提案されたIssue 346 placeholder docsの先行編集はcurrent Issue scopeを広げるため採用しない | `artifacts/20260729t052200z-chatgpt-output-issue-344-delivery-boundary-amendment-analysis.md`; SHA-256 `db258ca6f56e4b0ba7803ddda3f10cfdf8d4b3b620465b58e75a7d2becdfbf82`; 49,060 bytes; source commit `cc17c25530f8778b52b006b878c780dafeccf57f` | canonical amendmentをcommit/pushし、fresh ChatGPT-Use `spec-reviewer`責務review。旧EAL-029/030のPR/dogfood defer判断はS01当時の履歴として保持し、current delivery ownershipはD-007/EAL-031を正本とする |
| EAL-032 | adopted | ChatGPT-Use delivery-boundary amendment review (`FAIL`, advisory) | `plan.md`, parent Epic `report.md` | exact commit `59737280c085977d714797709ef0d9a6ade4412d`をreviewし、I344-AMEND-001〜003をmajor findingとして採用した。S90 unblocksをS95へ修正し、branch-changing post-PR repairがhead-bound S99 evidenceをstaleにしてowner step/local gates/三者fresh review/evidence-only closureを再実行する契約を追加し、親Epicのcurrent progress/next milestone/blockerをS01 closed・amendment re-review pendingへ同期した | `artifacts/20260729t054516z-chatgpt-output-delivery-amendment-spec-review-59737280.md`; SHA-256 `0ce40b6af53950db151523db2bd7a5845699d4b0a36065b02938b322fc0a3572`; 3,954 bytes; reviewed commit `59737280c085977d714797709ef0d9a6ade4412d` | 修正をcommit/pushし、新exact SHAへfresh ChatGPT-Use `spec-reviewer`責務re-review |
| EAL-033 | adopted | ChatGPT-Use delivery-boundary amendment re-review (`PASS`, advisory) | `requirement.md`, `design.md`, `plan.md`, parent Epic `plan.md` / `report.md` | GitHub同期済みexact commit `7ae8a957b67805294d6716b19a18e2b45808c3dc`をfresh re-reviewし、I344-AMEND-001〜003が全てclosed、finding 0、scope expansionなし、`next_action=proceed`を確認した | `artifacts/20260729t055223z-chatgpt-output-delivery-amendment-spec-rereview-7ae8a957.md`; SHA-256 `2c88c761c8c1e60c84e913d84a6787a345b50706b6ba6885fcda1fe5fc5cd5c4`; 522 bytes; reviewed commit `7ae8a957b67805294d6716b19a18e2b45808c3dc` | requirement/design/planをapprovedへ戻し、assurance再分類・verify後にS02 admission |
| EAL-034 | partially_adopted | ChatGPT-Use S02 implementation/test concretization (`advisory`) | S02 implementation handoff | GitHub同期済みexact commit `59d3d11c903a010a4fa98d0386f077a28862e70f`から、production read-only、mixed opacity fixture、linked checkoutとmanual ignored payload copyの分離、identical README no-diff、divergent README source-wins、既存root rejection/failure evidence再利用、characterization-first分類を採用した。提案されたtest名・helper形は候補であり、approved TC-344-006/007A/B/C/009を2 allowed test filesの最小差分で閉じる限り実装者が局所調整できる。各runtime commandやpayloadごとの重複matrix、inode/mtime不変、production変更は採用しない | `artifacts/20260729t061328z-chatgpt-output-s02-implementation-test-concretization-59d3d11c.md`; SHA-256 `e82db09be9a39818b58d91ea4e08a80fadca946be1c9e8916418b1cc2c853eaa`; 33,446 bytes; source commit `59d3d11c903a010a4fa98d0386f077a28862e70f` | Artifactとapproved S02 contractを`dev-coder`へ共有し、test-only characterizationとfocused verificationを実行する |
| EAL-035 | adopted | ChatGPT-Use S02 implementation review (`FAIL`, advisory) | S02 review gate / bounded fix | GitHub同期済みexact candidate `f06bbc6ee383345b7fa41420998f391fe254f478`を`code-reviewer`責務でreviewし、CR-S02-001/002のmajor 2件を全採用した。empty-source copyでmissing target creationを再観測し、mixed unit/CLI fixtureへ通常Markdownを追加した。scope expansion・不要な抽象化は要求されていない | `artifacts/20260729t064805z-chatgpt-output-s02-code-review-f06bbc.md`; SHA-256 `3e76be97fab3475c0d4de690a06dd69cb30061775a172d2e0e8c1e9928419f84`; 2,683 bytes; reviewed commit `f06bbc6ee383345b7fa41420998f391fe254f478` | bounded fixをcommit/pushし、新exact SHAへfresh ChatGPT-Use `code-reviewer`責務re-review |
| EAL-036 | adopted | ChatGPT-Use S02 implementation re-review (`PASS`, advisory) | S02 review gate | GitHub同期済みexact candidate `2917610b04a6bcb59c7b316f47d4281c8844b63a`をfresh `code-reviewer`責務でre-reviewし、CR-S02-001/002は両方closed、finding 0、scope expansionなし、不要な抽象化なし、`next_action=proceed`を確認した | `artifacts/20260729t070400z-chatgpt-output-s02-code-rereview-2917610b.md`; SHA-256 `18ecbbce292d2af0b44423549b085a1d4eb63d472cde7020e514dbd1ba784688`; 2,287 bytes; reviewed commit `2917610b04a6bcb59c7b316f47d4281c8844b63a` | evidence-only closure commit、clean確認、S02 Result Approval |
| EAL-037 | partially_adopted | ChatGPT-Use S03 implementation/test concretization (`advisory`) | S03 implementation handoff | GitHub同期済みexact source `9a5c08a5e33c0458cbdb0db9eb103e7f35513b39`から、explicit 4 hidden package-data、broad README exclusion削除、shared exact five-path build/sdist predicate、pre-prune observed six-path inventory、4-surface exact inventory/raw-byte parity、isolated installed-resource observation、existing Issue 69 helper再利用、Red/Green/verification順を採用した。提案されたhelper名/最大数は候補であり、3 allowed files内の最小局所形へ実装者が調整できる。generic framework、新backend、consumer E2E、dogfood、docs、production constantをtest expectedへimportする案は採用しない | `artifacts/20260729t072457z-chatgpt-output-s03-implementation-test-concretization-9a5c08a5.md`; SHA-256 `02e64abd7b44bb335ec744f6d569bad6f8f605c9aebfae09549ec3d9ad1c12c0`; 21,719 bytes; source commit `9a5c08a5e33c0458cbdb0db9eb103e7f35513b39` | Artifact、D-010、approved S03 contractを`dev-coder`へ共有し、3 allowed paths内でRed→Green→focused/full/static verificationを実行する |
| EAL-038 | adopted | ChatGPT-Use S03 implementation review (`PASS`, advisory) | S03 review gate | GitHub同期済みexact candidate `59d4fdf64333a537484af233ecef0138c9368aaf`を`code-reviewer`責務でreviewし、blocking/major 0、minor 1件、scope expansionなし、不要な抽象化なし、`next_action=proceed`を確認した。full installer 2 failureは`valid_s95_handoff`と判定された。CR-S03-001はreport enumだけのevidence-only修正として採用し、D-009〜011をdeclared Type/Dispositionへ正規化した | `artifacts/20260729t074802z-chatgpt-output-s03-code-review-59d4fdf6.md`; SHA-256 `8daf2ddc5d779e7de05559c31ccc031ced55956b0718b4ab8a98334dc9dab9a6`; 2,970 bytes; reviewed commit `59d4fdf64333a537484af233ecef0138c9368aaf` | evidence-only closure commit、clean確認、S03 Result Approval |
| EAL-039 | partially_adopted | ChatGPT-Use S90 implementation/test concretization (`advisory`) | S90 test/docs handoff | GitHub connectorでexact source `0efe3055860706a9f4b68ae1ddaa767371079b03`を確認した回答から、provider sourceを読む単一aggregate semantic assertion、canonical README read-only precondition、shared/role-specific guidance分離、valid Red条件、4文書の最小差分、deprecated wording disposition、Issue 345/346 availability boundaryを採用した。提案コードは参考形であり、exact prose snapshotや全4文書への同一長文強制は採用しない。canonical README内のgeneric import wordingとの過渡的緊張はS90で改変せず、shipped docsでplanned/unimplementedを明示する | `artifacts/20260729t090443z-chatgpt-output-s90-implementation-test-concretization-0efe3055.md`; SHA-256 `a0d8dbfefc933613fc6938c5de260d72eda69c820a10467bc21ab0e5e33ff20b`; 30,568 bytes; source commit `0efe3055860706a9f4b68ae1ddaa767371079b03` | Artifactとapproved S90 contractをtest lane `dev-coder`へ共有し、test-only valid Redを作成してcommit/push後にfresh ChatGPT-Use `code-reviewer`責務review |
| EAL-040 | adopted | S90 test lane valid Red | S90 test review candidate | provider 4文書を読む単一aggregate semantic assertionを追加した。`--run-full-regression` exact nodeはstale documentation semantics 37件だけで`1 failed`、canonical asset preconditionは`1 passed`。失敗はshared identity/README-only tracking 17件、fresh/future/no-backfill 3件、security/authority 6件、checkout/copy/source-wins/automation 4件、Issue 345/346 availability 4件、deprecated wording 3件に集約された。default laneの`1 skipped`は高速test policyどおり | `tests/unit/infra/test_init_update.py::TestInitUpdate::test_shipped_docs_describe_workbench_readme_boundary`; Ruff check/format、`git diff --check`、one-file allowlist pass | commit/push後にexact candidateへfresh ChatGPT-Use `code-reviewer`責務review |
| EAL-041 | adopted | ChatGPT-Use S90 test candidate review (`FAIL`, advisory) | S90 test bounded fix | GitHub connectorでexact candidate `74e4362ac16508c3d6db21eb62d6289ece1d4379`を確認したfresh `code-reviewer`責務review。CR-S90-TEST-001 blocking 1件を採用した。whole-document token bagsは逆向きのsecurity/authority/automation説明や無関係な`optional context`でも通り得るため、contract-bearing phrase/paragraph alternativesへ限定修正する。scope expansion・不要抽象化はなし | `artifacts/20260729t092536z-chatgpt-output-s90-test-code-review-74e4362a.md`; SHA-256 `c919b6770646e00b873445ea9d60cefd2f7dcf48e3a6fe98b77df47cea45c7f7`; 2,959 bytes; reviewed commit `74e4362ac16508c3d6db21eb62d6289ece1d4379` | test fileだけをbounded fixし、valid Red/static verification後に新exact SHAへfresh re-review |
| EAL-042 | adopted | ChatGPT-Use S90 test candidate re-review (`FAIL`, advisory) | S90 test second bounded fix | GitHub connectorでexact candidate `c043bad10e42d9c023f84bb0fc29dacaf8614863`を確認したfresh re-review。unrelated `optional context` false positiveとsecurity/authority/automation極性は改善したが、CR-S90-TEST-001はopen。CR-S90-TEST-R1-001 blocking 1件を採用し、日本語のoptional/node-copy/source-wins語幹を完結した肯定文へ限定修正する。parser/full-paragraph snapshotは追加しない | `artifacts/20260729t093814z-chatgpt-output-s90-test-code-rereview-c043bad1.md`; SHA-256 `31afa64b3f3261e70cc84272b9f1dbfe8d9a50642bd6f06d7c8eda43e141ab29`; 3,596 bytes; reviewed commit `c043bad10e42d9c023f84bb0fc29dacaf8614863` | test methodだけを再修正し、valid Red/static verification後に新exact SHAへfresh re-review |
| EAL-043 | adopted | ChatGPT-Use S90 test candidate second re-review (`PASS`, advisory) | S90 test lane review gate | GitHub connectorでexact candidate `a084cea911ef61524b9b24a52b7e0b22e182716e`を確認したfresh re-review。CR-S90-TEST-001とCR-S90-TEST-R1-001はclosed、finding 0、blocking/major/minor 0、scope expansion・不要抽象化なし、`next_action=proceed`。remaining Red 38件は4 provider docsだけに起因し、canonical preconditionは成立 | `artifacts/20260729t094623z-chatgpt-output-s90-test-code-rereview-2-a084cea9.md`; SHA-256 `6d4063280c76104e34c1027924089ee3a2aab1f111d6e7a03b9fd39b92ff8ec6`; 2,635 bytes; reviewed commit `a084cea911ef61524b9b24a52b7e0b22e182716e` | S90 docs laneを`doc-writer`へadmitし、4 provider docsだけでexact assertionをGreen化 |
| EAL-044 | adopted | S90 docs lane Green candidate | S90 docs review candidate | `doc-writer`がallowed 4 provider docsだけを更新し、Workbench shell/README-only tracking/no-backfill/security/authority/checkout/manual copy/root exclusion/source-wins/automation/Issue 345/346境界をrole-proportionalに記録した。exact semantic assertionとcanonical asset testは`2 passed`、deprecated 3句は0 hit、canonical Workbench README diffなし、`git diff --check` pass。skills/workflow semantic changeは不要、dogfood projectionはS95所有 | provider docs 3件と`templates/README.md`; `TC-344-007C/010`; EVD-008/010 candidate evidence | commit/push後にexact candidateへfresh ChatGPT-Use `spec-reviewer`責務review |
| EAL-045 | adopted | ChatGPT-Use S90 docs candidate review (`PASS`, advisory) | S90 docs review gate | GitHub connectorでexact candidate `5b5033068cb10af222ce820df9c4eec4a17d69e3`を確認したfresh `spec-reviewer`責務review。finding 0、blocking/major/minor 0。authority/security/copy/worktree/Issue 345/346の全境界がcorrect、scope expansionなし、`next_action=proceed`。4 canonical READMEはcandidate diff外でblob identity同一 | `artifacts/20260729t100020z-chatgpt-output-s90-docs-spec-review-5b503306.md`; SHA-256 `debe4cdf627bea28b1e9f1d239afa52acd62d0bc9958dc2b353fb36367d0bc7d`; 1,649 bytes; reviewed commit `5b5033068cb10af222ce820df9c4eec4a17d69e3` | evidence-only closure commit、clean/push確認、S90 Result Approval |
| EAL-046 | partially_adopted | ChatGPT-Use S95 implementation/test concretization (`advisory`) | S95 projection handoff | GitHub connectorでsource commit `2b4601f6e74053f3513f5fe66334c9999bf71c8b`を確認した回答から、exact 10 mirror paths、direct provider/mirror byte parity、initiatives/full Workbench filesystem snapshot、untracked direct README preflight、formal update 1回、existing parity/no-backfill nodes、`make lint`、default `uv run pytest`、failure classification、EVD-012 templateを採用した。raw path manifest/backupはrepository外・非公開とする。回答後のArtifact/report commitによりexecution headは更新されるため、`2b4601f6`固定は採用せず、実行直前のclean/pushed/local=remote headをauthorityとしprovider/expected ten-path content不変を確認する。optional test-map追加、manual fallback copy、rollback commandは必要時のdisposition候補でありprimary pathには採用しない | `artifacts/20260729t102224z-chatgpt-output-s95-implementation-test-concretization-2b4601f6.md`; SHA-256 `77c014b14524eac13473238ff2c3a211ae74991d5076c56163212790e2e1db72`; 46,210 bytes; source commit `2b4601f6e74053f3513f5fe66334c9999bf71c8b` | Artifactとapproved S95 contractを`dev-coder`へ共有し、preflight/snapshot後にformal updateを一度だけ実行 |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | fresh root と future Initiative / Epic / Issue に tracked `.workbench/README.md` を含む optional shell を生成し、existing scope を backfill しない (`I344-RQ-001`〜`I344-RQ-005`) | semantic opacity、node-scoped `workbench copy` compatibility、package parity、generic import / PR delivery の sibling Issue 境界 (`I344-RQ-006`〜`I344-RQ-010`) | low: copy/import/package の副次境界は primary shell を成立させる guardrail に限定し、root copy や generic import 実装を本 Issue へ取り込んでいない | pass: exact commit `a0b99765f7fac5ad384f4f81c85b50990f017fc9`のfresh ChatGPT-Use `spec-reviewer`責務reviewでfinding 0、scope creepなし |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | 親 Epic requirement/design/plan、provider source、package config、relevant tests、ChatGPT authoring/review Artifacts | F-001〜F-007 を canonical docs に反映。final ChatGPT review は blocking finding なし | adopted | passed | no | promote |
| design | approved requirement、parent Epic、provider source、current copy / package contracts、ChatGPT planning candidate / design reviews | B-001〜B-006、NB-001/NB-002をcanonical designへ修正し、post-B-006 fresh ChatGPT reviewとfresh `spec-reviewer` reviewで新規findingなし | adopted | passed | no | promote |
| plan | approved requirement/design、ChatGPT planning candidate、Standard assurance obligations、current provider/build/test seams、Issue plan authoring規約、delivery-boundary amendment analysis | prior findings B-001〜B-008-R1/B-005-R1、ChatGPT-First amendment F-001〜F-004、delivery amendment I344-AMEND-001〜003を解消済み | adopted | passed | no | execute approved plan |

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）
- 委任 authoring の使用:
  - used / not used
- 未使用の場合:
  - manual authoring path / 委任ドラフトを昇格証跡として使っていない理由。
- lifecycle state（契約値）:
  - `requested`, `produced`, `integrated`, `partially_integrated`, `rejected`, `superseded`, `blocked`, `stale`
- 昇格不可 state:
  - `stale`, `rejected`, `superseded`, `blocked`
- 標準出力先:
  - 対象 scope の `artifacts/` direct child にある flat Markdown
  - filename: typed artifacts use `<ts>-<type>-<slug>.md` or `<ts>-<nn>-<type>-<slug>.md`; blank artifacts use `<ts>-<slug>.md` or `<ts>-<nn>-<slug>.md`
- 軽量 provenance:
  - `created_by_role`, `scope_id`, `source_paths`, `intended_targets`, `adoption_status: unreviewed`, `reflected_to: []`, `diff_guard_result`, fallback decision, report evidence destination, adoption ledger note
  - 互換 label: source artifacts, draft artifact path, status, integration result, rejected portions, blockers, reviewer result, promotion decision
- 禁止 self-claim:
  - `authority: accepted`, `adoption_status: adopted`, non-empty `reflected_to`, reviewer pass, phase completion, implementation readiness
- 禁止 wildcard token:
  - `*`, `grants.*`, `all`
- 標準必須にしない field:
  - task manifest hash, Permission Profile hash, session invocation hash, probe run id, session hash
- historical note:
  - legacy `discussions/` と既存 `iss-00126` などの manifest/Profile/probe/session artifacts は grandfathered evidence として残し、削除・rename・validation failure 化しない。

| ロール（created_by_role） | 範囲（scope_id） | ドラフトパス（artifact draft path） | 参照元（source_paths） | 予定反映先（intended_targets） | 採用状態（adoption_status） | 反映先（reflected_to） | 差分ガード結果（diff_guard_result） | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果（reviewer result） | 昇格判断（promotion decision） |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 該当なし | iss-00344 | 該当なし | 該当なし | 該当なし | not used | [] | not_run | manual authoring path: main orchestratorがcanonical docsへ統合。ChatGPT-first external evidenceをEALで採用し、重複authoringを避けるためdelegated draft laneは使用していない | 該当なし | なし | passed | execute approved plan |

### 委任ドラフトの失敗モード（Delegated Draft Failure Modes）
| 失敗モード | 期待される判定 | 許可される次アクション | レポート証跡の記録先（report evidence destination） | 昇格可否 |
|---|---|---|---|---|
| ワークフロー単位の許可証跡不足（missing workflow-scoped authorization evidence） | blocked / incomplete | ワークフロー利用依頼の authorization source と boundary を記録する、または手動 authoring に戻す | ワークフロー単位の named role 許可（Workflow-Scoped Authorization） / この section | ineligible |
| 前段 reviewer pass 不足 / stale（missing/stale previous reviewer pass） | blocked / incomplete | レビューゲートを再実行する（rerun reviewer gate） | レビューゲート証跡（Reviewer Gate Status / Final Spec Review Gate） | ineligible |
| 設計中の要件 gap（requirement gap during design） | blocked / incomplete | requirement phase へ戻す | 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger） | ineligible |
| 計画中の設計 gap（design gap during plan） | blocked / incomplete | design phase へ戻す | 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger） | ineligible |
| ロール利用不可（role unavailable） | blocked / manual path | 利用不可を記録し、妥当なら手動で続行する | この section | ineligible |
| 禁止行為の試行（forbidden action attempt） | rejected | ドラフトを破棄し incident を記録する | この section / decision ledger | ineligible |
| 古いドラフト（stale draft） | stale | 再生成または差分調整する | この section | ineligible |
| 置換済みドラフト（superseded draft） | superseded | 置換先ドラフトを参照する | この section | ineligible |
| 委任使用主張に対する証跡不足（missing draft evidence when delegated use is claimed） | incomplete | 証跡を追加する、または委任使用 claim を外す | この section | ineligible |
| reviewer 利用不可 / 拒否 / waiver / provisional（reviewer unavailable/denied/waived/provisional） | blocked / incomplete | fresh な passed reviewer を取得する、または昇格なしの risk acceptance を記録する | レビューゲート証跡（Reviewer Gate Status / Final Spec Review Gate） | ineligible |

## 実装サマリー (任意)
- S01で、fresh rootとfuture Initiative / Epic / Issueにbyte-identicalな`.workbench/README.md` shellを生成し、existing root/nodeをbackfillしないprovider-side実装を追加した。
- provider/fallback ignoreをREADME-only trackingの3-rule contractへ更新し、generic scaffolderはrender後bytesが不変なUTF-8 fileをpath非依存でexact-copyするようにした。package/build/docs/dogfood projectionは変更していない。
- S02で、Workbench semantic opacity、linked checkoutとmanual payload copy、identical/divergent README source-wins、既存failure/atomicityをtest-onlyで固定した。
- S03で、package-data、custom `build_py`、custom `sdist`をexact five-path allowlistへ揃え、source/wheel/normalized sdist/isolated installed resourcesのinventoryと4 Workbench README bytesを検証した。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-07-29 12:51 - 13:55）

#### 対象
- Step: S01
- AC/EC: AC-344-001〜005
- 計画上の出典（Planned source）:
  - `plan.md` Section 10 `M1 / S01 — Provider shell、fresh root、future node、README-only tracking`
  - closure ids: TC-344-001、TC-344-002A/B、TC-344-003、TC-344-004、TC-344-005

#### 実施内容
- GitHub同期済みcommit `f1446111ac52c6cfc1783f513ea679dbd72ab1ae`をChatGPT-Useで具体化し、EAL-029として採用境界を固定した。
- `dev-coder`へS01 allowed pathsだけを委任し、4 README assets、fresh-only root copy、installer prune allowlist、provider/fallback ignore、generic byte-stable exact-copyと最小testsを実装した。
- 親が差分、allowed paths、focused tests、Ruff、default fast suiteを再確認した。default fast suiteの2 failureは、S01で禁止されたdogfood projectionがprovider assetsへ未追随である既知のdeferred差分であり、Issue 346へ残す。
- candidate commit `a62ae20d5ad587563bf09de77b1f85d75a64c4ec`をpushし、ChatGPT-Useのfresh `code-reviewer`責務reviewでfinding 0件の`PASS`を得た。生のJSON回答をEAL-030のIssue Artifactとして保存した。

#### 実行コマンド / 結果
```bash
uv run pytest -q -ra tests/unit/infra/test_runtime_template_scaffolder.py
# 3 passed

uv run pytest -q -ra --run-full-regression \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_workbench_readme_assets_are_byte_identical_and_complete \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_fresh_init_creates_only_tracked_root_workbench_readme \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_update_and_force_init_do_not_backfill_workbench_readme \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_workbench_gitignore_tracks_only_top_level_readme
# 4 passed

uv run pytest -q -ra --run-full-regression tests/cli_runtime/test_runtime_new_doc_s09.py
# 34 passed

uv run pytest -q -ra --run-full-regression \
  tests/cli_runtime/test_new.py::TestCliNew::test_new_nodes_generate_only_workbench_readmes \
  tests/cli_runtime/test_new.py::TestCliNew::test_workbench_no_backfill_preserves_existing_scopes_across_all_triggers
# 2 passed

uv run pytest -q -ra --run-full-regression tests/unit/infra/test_init_update.py -k 'workbench or readme'
# 9 passed, 548 deselected

uv run pytest -q -ra
# 670 passed, 2042 skipped, 2 failed
# deferred failures:
# - test_checked_in_dogfooding_mirror_docs_match_provider_assets
# - test_checked_in_dogfooding_mirror_templates_match_provider_assets

uv run ruff check <S01 Python paths>
# All checks passed

uv run ruff format --check <S01 Python paths>
# 6 files already formatted

git diff --check
# pass
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S01 | 赤フェーズ（Red） | asset/root/node未生成とCRLF rewriteを対象assertionで検出 | 4 asset `FileNotFoundError`、fresh root README missing、future 3 nodeのactual `[]`、CRLF `b'first\nsecond\n' != b'first\r\nsecond\r\n'` | production変更前のexact pytest nodes | pass | collection error、fixture不足、policy skipではない |
| S01 | 緑フェーズ（Green） | TC-344-001〜005のfocused closure | scaffolder 3、installer 4、new-doc 34、public lifecycle 2、workbench/readme 9がPASS | 上記exact commands | pass | selected heavy nodesだけ`--run-full-regression`でde-skip |
| S01 | リファクタリング（Refactor） | README/path-specific abstractionを追加しない | productionは既存`_copy_file`、generic template recursion、render後bytes比較を利用。test helperだけ局所追加 | diff inspection、Ruff、format、diff-check | pass | node-kind dispatch、新frameworkなし |
| S02 | baseline / characterization | production変更前のopacity/copy contractを確認 | unit `6 passed`。ordinary CLIはpolicyで`16 skipped`。full CLIは`8 passed / 8 failed`で、8件すべてがS01後のREADME存在によるfixture setup failure | `uv run pytest tests/unit/infra/test_runtime_fs_repo_workbench_opacity.py`; `uv run pytest [--run-full-regression] tests/cli_runtime/test_workbench.py` | pass with bounded fixture repair | D-008としてtest defectを分類。production failureではない |
| S02 | 緑フェーズ（Green） | TC-344-006/007A/B/C/009のtest-only closure | mixed opacity、linked checkout/manual payload、identical no-diff、divergent source-winsがGreen。fresh review CR-S02-001/002後はmissing target creationと通常Markdownも固定。unit `6 passed`、full CLI `18 passed` | new/extended exact nodes、full two suites、reusable/root rejection regressions、bounded fix parent rerun、EAL-036 fresh re-review | pass | production変更なし |
| S02 | リファクタリング（Refactor） | productionにREADME-aware branchや新excludeを追加しない | 2 allowed test filesだけを変更。helperはkeyword-only/default-preserving、stale fixtureは期待値を緩めず再構成 | diff inspection、Ruff、format、diff-check | pass | inode/mtime/raw whole-repo equalityを追加していない |
| S03 | 赤フェーズ（Red） | TC-344-008のpackage/prune gapをactual buildで検出 | production変更前にprune snapshotの`template_readmes_before_prune`欠落、wheel inventoryが`README.md` 1件だけ | 2 exact nodesを`--run-full-regression`で実行 | pass | collection/helper failureではなくpackaging/prune contract由来の`2 failed` |
| S03 | 緑フェーズ（Green） | exact five-pathを4 surfaceで成立させstale nested READMEを除去 | pre-prune 6、post-prune 5、source/wheel/sdist/installed exact 5、4 Workbench bytes一致、Issue 69 related nodes含む`6 passed` | S03 exact 2、Issue 69 related 4、parent exact 2 rerun、EAL-038 fresh review | pass | full installerのmirror parity 2 failureは`valid_s95_handoff`としてS95へowner維持 |
| S03 | リファクタリング（Refactor） | existing build frameworkを維持 | existing Issue 69 build/install helpersを再利用し、setupの既存build_py/sdistを局所拡張。production allowlistをtest expectedへimportしていない | diff inspection、Ruff、format、Mypy、diff-check | pass | new backend/dependency/generic frameworkなし |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S01 | pre-existing rootのregular file、dangling symlink、directory symlink証跡不足 | parent implementation review | bounded test-only follow-upでentry type、bytes/link target、mtime、README非生成を追加 | TC-344-001 | no | affected exact node 1 passed |
| S01 | existing Workbench snapshotにempty directory/symlinkが不足 | parent implementation review | 4 scope fixtureへempty directoryとsupported環境のsymlinkを追加 | TC-344-005 | no | affected exact node 1 passed |
| S01 | default fast suiteでdogfood mirror parity 2件がFAIL | parent verification | S01では修正せずdeferred。provider-firstかつdogfood projectionはIssue 346 ownership | deferred Issue 346 | no | 670 passed、2042 skipped、2 failed。失敗pathは`spec-dock/.gitignore`と`spec-dock/templates/**` |
| S02 | S01後に既存CLI fixtureの`.workbench`不存在前提がstale | dev-coder baseline / parent disposition | missing/empty/malformed状態をtemporary fixture内で明示し、error/atomicity assertionは維持 | TC-344-009 | no | D-008; repaired full CLI `18 passed` |
| S02 | ordinary CLI suiteが高速lane policyで全skip | test policy observation | required evidenceは`--run-full-regression`で取得し、ordinary skipも別記録 | TC-344-007A/B/C/009 | no | ordinary `18 skipped`; full `18 passed` |
| S02 | empty-source fixtureがmissing target creationを観測せず、通常Markdownがmixed fixtureに未収載 | fresh ChatGPT-Use code review | source existing-empty / target missingのpreconditionをassertし、unit/CLI mixed fixtureへ通常Markdownを追加 | TC-344-006/009 | no | EAL-035; parent rerun unit `6 passed` / full CLI `18 passed`; EAL-036 fresh re-review PASS |
| S03 | required full installer fileのdogfood mirror parity 2 failure | dev-coder / parent rerun | S03 forbidden pathでは修正せず、approved S95 provider-first projection後にfull file/default suiteを再実行 | TC-344-011 / S95 | no | D-011; exact failuresは`spec-dock/.gitignore`と`spec-dock/templates/**` |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S01 | TC-344-001、002A/B、003、004、005 | focused tests、fresh review、candidate commit/push、evidence-only closure commit、clean、Result Approval | focused tests完了、candidate `a62ae20d5ad587563bf09de77b1f85d75a64c4ec` push済み、fresh ChatGPT-Use review `PASS` / finding 0。EAL-030と本reportをevidence-only closure commitへ含める | pass | closure commit後のactual SHAとclean確認は自己参照を避けて外部引き渡し証跡へ記録する |
| S02 | TC-344-006、007A/B/C、009 | test-only diff、full two suites、fresh review、candidate/evidence commits、clean、Result Approval | candidate `2917610b04a6bcb59c7b316f47d4281c8844b63a` push済み。parent verification unit `6 passed` / full CLI `18 passed` / Ruff/format pass。fresh ChatGPT-Use re-review `PASS` / finding 0、prior major 2件closed。EAL-036と本reportをevidence-only closure commitへ含める | pass | production変更なし。closure commit後のactual SHAとclean確認は自己参照を避けて外部引き渡し証跡へ記録する |
| S03 | TC-344-008、static quality、Issue 346 handoff | dual prune/exclude、4-surface exact inventory/bytes、stale removal、full installer、fresh review、candidate/evidence commits、clean、Result Approval | candidate `59d4fdf64333a537484af233ecef0138c9368aaf` push済み。exact `2 passed`; related `6 passed`; Ruff/format/Mypy/diff pass。fresh review `PASS`、minor enum findingをevidence-only修正、D-011は`valid_s95_handoff`。EAL-038と本reportをclosure commitへ含める | pass | allowed 3 implementation pathsのみ。S95はmirror/default laneを必ずgreenにする |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| TC-344-001 | S01 | yes | red-required | root README missing | 4 installer exact nodes | pass | fresh root生成、existing directory/file/symlink no-backfill |
| TC-344-002A | S01 | yes | red-required | future node README actual `[]` | `test_runtime_new_doc_s09.py` 34 nodes | pass | 3 kind plan/result/filesystem parity |
| TC-344-002B | S01 | yes | red-required | CRLF rewrite | scaffolder 3 exact nodes | pass | unchanged/changed/path-neutral |
| TC-344-003 | S01 | yes | red-required | 4 asset missing | asset parity + node/root output | pass | common SHA-256 `58300883820e1dfd173ab90a8205dcc44f83f29313b1bca84ad1955733cd8490` |
| TC-344-004 | S01 | yes | red-required | READMEもignore | real Git matrix | pass | regular/symlink/directory/nested/case/backup/payload/near-name |
| TC-344-005 | S01 | yes | red-required | all-trigger snapshot test missing | exact installer + lifecycle nodes | pass | 4 scopeのentry/type/bytes/link target/mtime不変、新childだけ生成 |
| TC-344-006 | S02 | yes | characterization-first | unit baseline `6 passed`; mixed fixture不足 | unit opacity + CLI mixed opacity | pass | README/通常Markdown/fake metadata/ADR/dependency/binary/invalid UTF-8、active stable fields。EAL-036 fresh PASS |
| TC-344-007A | S02 | yes | red-required connection | checkout/manual copy接続testなし | linked worktree identical README/payload test | pass | checkout直後targetはREADMEだけ、copy後payload追加、tracked diffなし。EAL-036 fresh PASS |
| TC-344-007B | S02 | yes | characterization-first | low-level source-winsのみ | public CLI divergent README test | pass | target after hashがsource beforeと一致。EAL-036 fresh PASS |
| TC-344-007C | S02 | yes | covered-existing | existing selector rejection | unpublished/root options + invalid scope nodes | pass | 5 collected cases。EAL-036 fresh PASS |
| TC-344-009 | S02 | yes | covered-existing + characterization | full CLI baseline fixture 8 failure | repaired full CLI + reusable regressions | pass | full CLI 18、reusable 6、root rejection 5、missing target creation。EAL-036 fresh PASS |
| TC-344-008 | S03 | yes | red-required | pre-prune observation欠落、wheel inventory `README.md` 1件 | exact two build nodes、Issue 69 related regression、4-surface raw bytes | pass | pre 6 / post 5、wheel/sdist `0.2.3` artifacts、canonical SHA-256 `58300883820e1dfd173ab90a8205dcc44f83f29313b1bca84ad1955733cd8490`、EAL-038 fresh PASS |

- `closure id / test id` は Spec-Locked Closure Index の `id` を指す。別 alias を使う場合は `Closure Delta` で対応を記録する。

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| TC-344-001 | S01 | EVD-001 | pass | fresh/existing root variants |
| TC-344-002A | S01 | EVD-002 | pass | 3 node matrix |
| TC-344-002B | S01 | EVD-003 | pass | generic exact-copy/render |
| TC-344-003 | S01 | EVD-003 | pass | 4 asset/content/output parity |
| TC-344-004 | S01 | EVD-004 | pass | real Git pathname matrix |
| TC-344-005 | S01 | EVD-001/EVD-002 | pass | all-trigger preservation |
| TC-344-006 | S02 | EVD-005 | pass | mixed unit/CLI semantic opacity、fresh review PASS |
| TC-344-007A | S02 | EVD-006 | pass | checkout/manual copy/identical no-diff、fresh review PASS |
| TC-344-007B | S02 | EVD-006 | pass | divergent README source-wins、fresh review PASS |
| TC-344-007C | S02/S90 | EVD-006/EVD-008 | pass | runtime rejectionと4 docs guidance Green、fresh code/spec reviews PASS |
| TC-344-009 | S02 | EVD-006 | pass | full existing copy suite and failure/atomicity、fresh review PASS |
| TC-344-008 | S03 | EVD-007 | pass | source/wheel/sdist/installed exact 5、4 raw-byte parity、stale removal、fresh review PASS |
| TC-344-010 | S90 | EVD-008 | pass | exact semantic assertion `1 passed`、deprecated wording 0 hit、fresh spec review PASS |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | TC-344-001〜005 | plan記載のexact test nodes | TC-344-001〜005 | approved closureの変更なし | no | no: candidate `a62ae20d5ad587563bf09de77b1f85d75a64c4ec`へのfresh code reviewがPASS |

#### ワークフロー単位の named role 許可（Workflow-Scoped Authorization）
`workflow_issue.md` is the policy source for workflow-scoped authorization. This report records observed authorization source, boundary, expiry, and denied / unavailable / host conflict handling only.

Authorization source は、ユーザーによる SpecDock workflow 利用依頼でよい。範囲は active repo/worktree、active SpecDock scope、current session、SpecDock-defined named roles、documented role responsibility に限る。この section は role ごと・phase ごとの追加承認 gate ではなく、scope 内の named role 利用前に追加許可を求める根拠にしてはならない。

別途確認が必要なのは scope expansion、破壊的操作、外部公開、credential を伴う外部 mutation、private external system、SpecDock workflow 外の role 利用である。unavailable / denied / host conflict は fail-closed とし、fresh `passed` reviewer gate の代替にしてはならない。

| 許可元（authorization source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可 / host conflict 理由（denied / unavailable / host conflict reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user request to execute Issue 344 with ChatGPT-First authoring/review and create a mergeable PR | `/Volumes/990p2t/offloaded/home/iwasawayuuta/.codex/worktrees/692d/spec-dock` | iss-00344 | current session | dev-coder; doc-writer (S90 only); ChatGPT-Use executing code-reviewer / spec-reviewer / qa-reviewer responsibility contracts; PR creator/observer workflow roles | active repo/worktree、active Issue、current session、approved step scope、Issue-local PR作成/観測。merge、auto-merge、branch削除、Issue finish、Issue 345/346 implementation、scope expansionは含めない | Issue 344 execution/PR observation終了 / session end / scope change / user revocation | none | delivery amendment fresh review後、S02から順に実行 |

#### 実装委任ゲート（Implementation Delegation Gate）
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | delegated | shipped scaffold、installer、generic runtime primitive、real Gitを跨ぐbounded implementation | dev-coder | approved plan S01とEAL-029の採用部分 | `spec-dock/active/issue/{requirement,design,plan}.md`、provider source | S01 allowed pathsだけ。4 README assets、`cli.py`、provider `.gitignore`、generic scaffolder、指定tests | create_node/workbench/fs adapters、generic import、root copy route、package/build/docs/dogfood、canonical docs直接編集 | Red assertion failure、focused exact nodes、real Git matrix、Ruff check/format、`git diff --check`、allowed-path diff | allowed path外変更、canonical gap、unexpected Red、S01 test skip、existing Workbench mutation、S03/Issue 345/346責務が必要 | worker summary、changed files、Red/Green/refactor、commands/results、risks、EVD-001〜004 summary、Ledger Noteまたはno-decision declaration | pass: bounded implementationとtest-only follow-up完了。親統合とfresh ChatGPT-Use review `PASS`を確認 |
| S02 | delegated | semantic opacity、Git checkout、manual copy、README source-winsをproduction変更なしで一続きに固定するbounded test work | dev-coder | approved plan S02とEAL-034の採用部分 | `spec-dock/active/issue/{requirement,design,plan}.md`、S01 evidence、2 allowed tests、read-only copy/opacity source | `tests/unit/infra/test_runtime_fs_repo_workbench_opacity.py`、`tests/cli_runtime/test_workbench.py`のみ | production、docs、package、dogfood、generic import、canonical docs直接編集、README filter/root route/new exclusion | baseline 2 suites、new/extended exact nodes、full 2 suites、reusable selected regressions、root rejection、`git diff --check`、allowed-path diff | production変更が必要、unexpected regression、S01 contract不成立、allowed path外変更、over-specified inode/mtime/raw snapshot | worker summary、characterization/Red/Green分類、inventories/hashes/Git observations、commands/results、risks、EVD-005/006 summary、Ledger Noteまたはno-decision declaration | pass: worker returnを親が検証しreview candidateへ統合 |
| S03 | delegated | package config、custom build/sdist、real wheel/sdist/installを跨ぐbounded distribution work | dev-coder | approved plan S03、EAL-037、D-010 | approved specs、S01/S02 evidence、`pyproject.toml`、`setup.py`、Issue 69 helpers | `pyproject.toml`、`setup.py`、`tests/unit/infra/test_init_update.py`のみ | runtime、docs、dogfood、dependency、generic import、new backend/framework、canonical docs直接編集 | Red exact 2、Green exact/related/full installer、Ruff/format/Mypy/diff、allowed paths、repo artifact absence | network、wheelhouse不足、新backend/dependency、five-path変更、allowed path外変更、unclassified regression | Red/Green、artifact names、4 inventories、hash/bytes、pre/post、stale absence、static results、EVD-007/010/011 summary、Ledger Note | pass: exact/related/static Green。full installer 2 failureをD-011として親がS95へowner維持しreview candidateへ統合 |
| S90 test lane | delegated | shipped guidanceのsemantic boundaryをdocs変更前に一つの観測可能なRedへ固定するbounded test work | dev-coder | approved plan S90とEAL-039の採用部分 | approved specs、canonical Workbench README、4 provider docs、S01〜S03 evidence | `tests/unit/infra/test_init_update.py`のexact test methodのみ | production、4 docs、canonical README、package、dogfood、canonical specs直接編集 | exact node `--run-full-regression` Red、canonical asset test、Ruff check/format、`git diff --check`、one-file allowlist | path/decoding/helper/canonical precondition起因のRed、allowed path外変更、runtime behavior変更が必要 | aggregate Red diagnostics、commands/results、closure status、risk、Ledger Note | pass: documentation-specific 38件だけでvalid Red。fresh review finding 2件を閉じてPASS |
| S90 docs lane | delegated | accepted semantic assertionを4 shipped operator docsの最小差分でGreen化するbounded documentation work | doc-writer | approved plan S90、EAL-039/043、accepted test | approved specs、canonical Workbench README、4 provider docs、S01〜S03 observed evidence | provider docs 3件と`templates/README.md`のみ | Python test、runtime/installer/package、canonical README/spec/report/artifact、dogfood、Issue 345/346 implementation | exact semantic assertion Green、canonical asset test、deprecated wording inspection、docs diff、canonical terminology、four-file allowlist | runtime/canonical wording変更が必要、approved meaning不明、allowed path外変更 | changed docs、Green、inspection、unresolved wording、EVD-008/010 summary、Ledger Note | pass: exact 2 tests Green、deprecated 0 hit、canonical diffなし。fresh spec review pending |
| S95 | delegated | provider-first managed mirror projectionと既存local state保護を一つのauditable transactionで閉じるbounded integration work | dev-coder | approved plan S95、EAL-046の採用部分 | approved specs、S01〜S90 evidence、provider/mirror paths、local filesystem state | exact 10 checked-in mirror pathsのみ。test-only repairは親の事前dispositionがある場合だけ | provider source、initiatives、existing Workbench、canonical specs/report/artifact、Issue 345/346、candidate wheel、bare full regression、second update | clean/pushed/local=remote、untracked README preflight、external snapshots、one formal update、exact allowlist、direct/parity/no-backfill tests、lint/default pytest、final snapshots | protected mismatch、allowlist mismatch、unexpected update noise、unrelated failure、second update必要、provider inversion | EVD-012 summary、snapshot counts/hashes/equality、update logs/hash、ten paths、tests/lint/default results、classification、Ledger Note | pending: concretization Artifactをcommit/push後にdev-coderへ共有 |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01 | dev-coder | fresh-only root/node Workbench shell、README-only ignore、generic byte-stable exact-copyを実装。親findingでroot/workbench symlink・empty directory coverageをtest-only follow-up | provider production 7 path、tests 4 path | focused installer/scaffolder/new-doc/lifecycle、Ruff、format、diff-check pass | ChatGPT-Use fresh `code-reviewer` PASS、finding 0 | default fast suiteのdogfood mirror parity 2件はIssue 346へdeferred | accepted; proceed to evidence-only closure commit |
| S02 | dev-coder | mixed semantic opacity、linked checkout/manual payload copy、identical README no-diff、divergent README source-winsをtest-onlyで固定し、S01後にstaleとなったmissing/empty/malformed fixtureを修復。fresh review major 2件に対してmissing target preconditionと通常Markdown fixtureを限定追加 | `tests/unit/infra/test_runtime_fs_repo_workbench_opacity.py`; `tests/cli_runtime/test_workbench.py` | 初回unit `6 passed`; ordinary CLI `18 skipped`（policy）; full CLI `18 passed`; reusable selected `6 passed`; root rejection `5 passed`; Ruff/format/diff-check pass。bounded fix後の親再実行もunit `6 passed` / full CLI `18 passed` / Ruff/format pass | initial fresh review `FAIL`: CR-S02-001/002 majorを全採用。candidate `2917610b04a6bcb59c7b316f47d4281c8844b63a`へのfresh re-review `PASS`、finding 0、prior 2件closed | ordinary CLIは高速lane policyでskipされるためfull検証に`--run-full-regression`が必要 | accepted; proceed to evidence-only closure commit |
| S03 | dev-coder | explicit hidden package-data、shared exact five-path build/sdist predicate、pre-prune inventory、4-surface exact inventory/raw bytesを既存Issue 69 frameworkで実装 | `pyproject.toml`; `setup.py`; `tests/unit/infra/test_init_update.py` | Red exact `2 failed`; Green exact `2 passed`; related `6 passed`; full installer `3 passed / 554 skipped / 2 failed`; Ruff/format/Mypy/diff pass。親exact `2 passed`、full/static同結果を再確認 | fresh ChatGPT-Use review `PASS`; blocking/major 0、minor enum 1件をclosure reportで解消、D-011 `valid_s95_handoff` | mirror parity 2 failureはapproved S95 ownership | accepted; proceed to evidence-only closure commit |
| S90 test lane | dev-coder | provider 4文書のshared/role-specific guidanceを一つのsemantic assertionへ集約し、canonical READMEをread-only preconditionとしてvalid Redを固定 | `tests/unit/infra/test_init_update.py` | final exact node `1 failed`（stale semantics 38件のみ）、canonical asset `1 passed`、Ruff/format/diff-check pass。default lane `1 skipped`はpolicyどおり | initial/R1 fresh review `FAIL`後、exact `a084cea911ef61524b9b24a52b7e0b22e182716e`へfresh `PASS`; prior 2件closed、finding 0 | Issue 345/346 availability変更時はdocsとtestの同時更新が必要 | accepted; docs lane admitted |
| S90 docs lane | doc-writer | 4 provider docsをshell/README-only tracking/security/authority/worktree copy/root/sibling Issue境界へ更新 | provider docs 3件、`templates/README.md` | exact docs + canonical asset `2 passed`; deprecated 3句 0 hit; canonical README diffなし; diff-check pass | exact `5b5033068cb10af222ce820df9c4eec4a17d69e3`へfresh ChatGPT-Use `spec-reviewer` PASS、finding 0 | unresolved wordingなし。dogfood projectionはS95所有 | accepted; proceed to evidence-only closure commit |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| S01 | not applicable: dev-coder delegation succeeded | risk accepted: no | none | none | none | delegated worker evidenceを親が再検証 | fresh ChatGPT-Use code-reviewer責務review required | parent implementation exception未使用 |
| S02 | not applicable: dev-coder delegation succeeded | risk accepted: no | none | none | none | delegated worker evidenceを親がunit/full CLI/Ruff/format/diff-checkで再検証 | fresh ChatGPT-Use code-reviewer責務review required | parent implementation exception未使用 |
| S03 | not applicable: dev-coder delegation succeeded | risk accepted: no | none | none | none | exact/full/Ruff/format/Mypy/diff/allowed pathsを親が再検証 | fresh ChatGPT-Use code-reviewer責務review required | parent implementation exception未使用。D-011はS95 owner handoffでありfinal risk waiverではない |
| S90 test lane | not applicable: dev-coder delegation succeeded | risk accepted: no | none | none | none | valid Red、canonical precondition、Ruff/format/diff/allowed pathを親が確認 | fresh ChatGPT-Use code-reviewer責務review required | parent implementation exception未使用 |
| S90 docs lane | not applicable: doc-writer delegation succeeded | risk accepted: no | none | none | none | exact Green、deprecated wording、canonical diff、four-file boundaryを親が確認 | fresh ChatGPT-Use spec-reviewer責務review required | parent implementation exception未使用 |

#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）
Lite は specialist / fallback evidence を必須化しないが、not applicable / skip reason を記録する。Standard は specialist evidence、skip reason、または manual fallback を記録する。Strict / Critical は specialist evidence または明示的な manual fallback を記録し、skip reason だけでは readiness evidence にしない。

| グレード（Grade） | 必要な専門家 / 代替（required specialist / fallback） | 使用状況（usage） | 証跡（evidence） | 鮮度 spec-reviewer 判定（fresh spec-reviewer verdict） | 実行可否（execution readiness） |
|---|---|---|---|---|---|
| `standard` | `implementation-planner / manual fallback` | `skipped` | skip reason: approved requirement/design/planとChatGPT planning/review Artifactsが既にあり、追加delegated draftは重複authoringになる。今回の実行overlayはmain orchestratorが限定修正した | `passed` | `ready` |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| plan amendment / S01 admission | ChatGPT-First plan amendment review | spec-reviewer | fresh | passed | no | execute approved plan | ChatGPT-Use reviewed exact commit `a0b99765f7fac5ad384f4f81c85b50990f017fc9`; finding 0。backendはChatGPT-Use、role名は責務契約 |
| S01 | implementation candidate review | code-reviewer | fresh | passed | no | proceed to evidence-only closure commit | ChatGPT-Use reviewed exact candidate `a62ae20d5ad587563bf09de77b1f85d75a64c4ec`; finding 0、scope creepなし、不要な抽象化なし。review backendはChatGPT-Use、role名は責務契約 |
| delivery amendment | Issue-local PR boundary review | spec-reviewer | superseded | failed | no | bounded fix and re-review | ChatGPT-Use reviewed exact commit `59737280c085977d714797709ef0d9a6ade4412d`; major 3件をEAL-032として全採用。新SHAへのre-review前はS02 admission不可 |
| delivery amendment re-review | Issue-local PR boundary review | spec-reviewer | fresh | passed | no | execute approved plan after assurance verify | ChatGPT-Use reviewed exact commit `7ae8a957b67805294d6716b19a18e2b45808c3dc`; finding 0、scope expansionなし |
| S02 | implementation candidate re-review | code-reviewer | fresh | passed | no | proceed to evidence-only closure commit | exact candidate `2917610b04a6bcb59c7b316f47d4281c8844b63a`をreview。CR-S02-001/002 closed、finding 0、scope expansion/不要抽象化なし |
| S03 | implementation candidate review | code-reviewer | fresh | passed | no | proceed to evidence-only closure commit | exact candidate `59d4fdf64333a537484af233ecef0138c9368aaf`をreview。blocking/major 0、minor enum 1件採用、D-011 `valid_s95_handoff` |
| S90 test lane | test-only candidate review | code-reviewer | superseded | failed | no | bounded fix and fresh re-review | exact candidate `74e4362ac16508c3d6db21eb62d6289ece1d4379`をreview。CR-S90-TEST-001 blocking 1件を採用 |
| S90 test lane R1 | test-only candidate re-review | code-reviewer | superseded | failed | no | second bounded fix and fresh re-review | exact candidate `c043bad10e42d9c023f84bb0fc29dacaf8614863`をreview。CR-S90-TEST-001 open、CR-S90-TEST-R1-001 blocking 1件を採用 |
| S90 test lane R2 | test-only candidate second re-review | code-reviewer | fresh | passed | no | admit docs lane | exact candidate `a084cea911ef61524b9b24a52b7e0b22e182716e`をreview。prior 2件closed、finding 0、blocking/major/minor 0 |
| S90 docs lane | docs candidate review | spec-reviewer | fresh | passed | no | proceed to evidence-only closure commit | exact candidate `5b5033068cb10af222ce820df9c4eec4a17d69e3`をreview。全境界correct、finding 0 |

#### マイルストーン / commit 候補ゲート（Milestone / Commit Candidate Gate）
| マイルストーン / step | クロージャ状態（closure state） | コミット候補 / コミット範囲（commit candidate / scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S01 | committed | provider implementation、S01 tests、pre-review report | review target `a62ae20d5ad587563bf09de77b1f85d75a64c4ec`; closure head `cc17c25530f8778b52b006b878c780dafeccf57f` | clean / pushedをS02 admission前に確認 | not applicable | not applicable | not applicable | not applicable |
| S02 | committed | test-only implementation、D-008/D-009、failed/PASS review Artifacts、bounded fixture fix | review target `2917610b04a6bcb59c7b316f47d4281c8844b63a`; closure head `9a5c08a5e33c0458cbdb0db9eb103e7f35513b39` | clean / pushed、local=remoteをS03 admission前に確認 | not applicable | not applicable | not applicable | not applicable |
| S03 | committed | package/build/test implementation、D-010/D-011、delegation/verification/review evidence | review target `59d4fdf64333a537484af233ecef0138c9368aaf`; EAL-038と本reportはpost-review evidence-only closure commit | closure commit後に外部引き渡し証跡で確認 | not applicable | not applicable | not applicable | not applicable |
| S90 test lane | committed | exact aggregate semantic test、EAL-040〜043、delegation/Red/review evidence | accepted review target `a084cea911ef61524b9b24a52b7e0b22e182716e` | clean / pushed、local=remote確認済み | not applicable | not applicable | not applicable | not applicable |
| S90 docs lane | committed | provider docs 4件、EAL-044/045、Green/delegation/review evidence | review target `5b5033068cb10af222ce820df9c4eec4a17d69e3`; closure head `e8df32e913d4774ab9d5a970cc3d34886bccfc4e` | clean / pushed / local=remote確認済み | not applicable | not applicable | not applicable | not applicable |

#### Step / Milestone Result Approval

| ステップ（step） | close state | closure head / clean evidence | reviewer evidence | Result Approval | 次ステップ admission |
|---|---|---|---|---|---|
| S01 | committed | `cc17c25530f8778b52b006b878c780dafeccf57f`; clean / pushed確認済み | EAL-030 fresh PASS | approved | S02 admitted |
| S02 | committed | `9a5c08a5e33c0458cbdb0db9eb103e7f35513b39`; clean / pushed / local=remote確認済み | EAL-036 fresh PASS、prior major 2件closed | approved | S03 admitted |
| S03 | committed | `0efe3055860706a9f4b68ae1ddaa767371079b03`; clean / pushed / local=remote確認済み | EAL-038 fresh PASS、minor enum findingをclosure reportで解消 | approved | S90 admitted |
| S90 | committed | `e8df32e913d4774ab9d5a970cc3d34886bccfc4e`; clean / pushed / local=remote確認済み | EAL-043 code-review PASS、EAL-045 spec-review PASS、prior blocking 2件closed | approved | S95 admitted |

#### 変更したファイル
- `src/spec_dock/cli.py` - pre-mutation freshness、fresh root copy、installer README allowlist、fallback ignore
- `src/spec_dock/assets/spec_dock/.gitignore` - README-only tracking 3-rule contract
- `src/spec_dock/assets/spec_dock/templates/{root,initiative,epic,issue}/.workbench/README.md` - 4 byte-identical canonical assets
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/template_scaffolder.py` - render後bytes同一時のpath-agnostic exact-copy
- `tests/unit/infra/test_init_update.py` - asset/root/ignore/no-backfill matrix
- `tests/unit/infra/test_runtime_template_scaffolder.py` - unchanged/changed/path-neutral bytes
- `tests/cli_runtime/test_runtime_new_doc_s09.py` - 3 node plan/result/filesystem parity
- `tests/cli_runtime/test_new.py` - README allowlist expectationとall-trigger no-backfill
- `pyproject.toml` - 4 hidden Workbench README package-dataとbroad exclusion解消
- `setup.py` - exact five-path build/sdist pruneとpre-prune observation
- `tests/unit/infra/test_init_update.py` - build prune、4-surface inventory/raw-byte、isolated installed-resource tests
- `tests/unit/infra/test_init_update.py` - S90 aggregate docs semantic assertion
- `src/spec_dock/assets/spec_dock/docs/{README.md,guide.md,reference_worktree.md}` - Workbench shell/operator境界
- `src/spec_dock/assets/spec_dock/templates/README.md` - fresh/future shell、README-only tracking、no-backfill境界

#### コミット
- S01 review target / closure head: `a62ae20d5ad587563bf09de77b1f85d75a64c4ec` / `cc17c25530f8778b52b006b878c780dafeccf57f`
- S02 review target / closure head: `2917610b04a6bcb59c7b316f47d4281c8844b63a` / `9a5c08a5e33c0458cbdb0db9eb103e7f35513b39`
- S03 review target / closure head: `59d4fdf64333a537484af233ecef0138c9368aaf` / `0efe3055860706a9f4b68ae1ddaa767371079b03`
- S90 test review target / docs review target / closure head: `a084cea911ef61524b9b24a52b7e0b22e182716e` / `5b5033068cb10af222ce820df9c4eec4a17d69e3` / `e8df32e913d4774ab9d5a970cc3d34886bccfc4e`

#### メモ
- `No material implementation decisions beyond the approved plan.`

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| provider docs 3件 + `templates/README.md`; workflow/skill/migration notesはsemantic changeなし | yes / N/A | doc-writer | exact semantic assertion + canonical asset `2 passed`; deprecated wording 0 hit; canonical README diffなし; dogfoodはS95 handoff | fresh spec-reviewer PASS、finding 0 |

### 最終 QA ゲート（Final QA Gate）
| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer | whole issue obligation coverage | added / already sufficient / not applicable | ... | pass / fail / blocked |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer | issue-wide integrated diff | ... | 0 | pass / fail / blocked |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report / implementation / tests / docs alignment | ... | 0 | pass / fail / blocked |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| ... | ... | final response / PR / issue comment / other external delivery evidence | ready / blocked |

## 遭遇した問題と解決 (任意)
- 問題: ...
  - 解決: ...

## 学んだこと (任意)
- ...

## 今後の推奨事項 (任意)
- ...

## 省略/例外メモ (必須)
- 該当なし
