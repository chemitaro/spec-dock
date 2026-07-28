---
種別: 実装報告書（Issue）
ID: "iss-00342"
タイトル: "Reduce Unit Test And Provider CI Runtime"
関連GitHub: ["#342"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-28"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00080", "init-00079"]
---

# iss-00342 Reduce Unit Test And Provider CI Runtime — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

> `report.md` は観測証跡台帳（observed evidence ledger）の scaffold です。planned requirements、evidence destination、closure 条件は `plan.md` が持ち、この文書は実際の Red / Green / Refactor evidence、発見された tests、closure delta、reviewer status、commit/no-op evidence を記録する evidence slot です。workflow / compliance authority は skills、docs、accepted ADRs、reviewer gates に置きます。

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger / 必須）

`report.md` は実装中・文書更新中に発生した material な仕様解釈、判断、plan 逸脱、tradeoff、open question、promotion / follow-up を記録する audit trail でもある。worker の raw note や作業 transcript を貼る場所ではなく、orchestrator が source docs、diff、tests、reviewer output と照合して issue-level の canonical entry に統合する。

Materialな判断がない場合はno-decisionを明示する。本IssueではD-001〜D-005がcurrent decision ledgerである。

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
| D-001 | resolved | test-strategy | user / orchestrator | 30〜40分の完全回帰をPR merge blockerと通常開発の既定経路に残すか | A: fast/full分離; B: 全PRでfull維持; C: 判断保留 | Option Aを採用し、完全回帰は明示手動または`main` push後にのみ実行する。schedule / cronは導入しない | ユーザー回答と実測により、critical-path短縮を優先しつつfull集合を保持する方針が確定した | promoted_to_adr | `artifacts/20260728t015759z-01-interview-full-regression-merge-gate-policy.md`; `artifacts/20260728t025412z-adr-separate-fast-merge-gate-and-full-regression-execution.md` | canonical requirement / design / planへ反映 |
| D-002 | resolved | scope | orchestrator | ChatGPT候補がscheduleと旧421秒baselineを前提にした | schedule採用; schedule棄却; 再質問 | schedule案と旧性能値を棄却し、現在の実測とaccepted ADRを優先する | local-context bodyはChatGPTから未観測であり、現行実測はfull約37〜38分、ユーザーはschedule非採用を明示した | rejected | `oracle:iss00342-test-ci-planning`; ZIP SHA-256 `f300cbff69ce241e85462fd5a37fcf2ff7beacad77d8b1d40c133749783e1e01`; local source-hash reconciliation | scheduleをdesign/planへ入れない |
| D-003 | resolved | implementation | assurance classifier | requirementのpre-classification推奨はstrictだったがruntime classifierはstandardをauthorizedにした | strict維持; standard採用; reclassify | authorized profile `standard`を採用し、test omission / workflow riskはspecialist evidenceとfresh reviewsで補強する | hard triggerなし、product data/security/credential/irreversible migrationなし、rollback可能 | applied | `.assurance.json`; `assurance classify --stage requirement`; `assurance compose --artifact all` | Standard design / plan templateをauthoring |
| D-004 | resolved | test-strategy | user / ChatGPT authoring | 旧設計のdefault `-m fast`とmandatory Make facadeが、通常pytestをそのまま使いたいowner intentと矛盾した | default marker selection; permanent skip; environment `skipif`; pytest option-controlled conditional policy skip | direct ordinary pytestを維持し、`--run-full-regression`だけを明示permissionにする。`-m full_regression` aloneはpermissionにせず、flagなしselected heavyへsession-local policy skipを追加する | selectionとexecution permissionを分離し、focused longをreason付きskipにしながらlegitimate skipを解除しない | promoted_to_adr | `artifacts/20260728t105349z-03-adr-use-direct-pytest-commands-with-explicit-full-regression-opt-in.md`; ChatGPT ZIP SHA-256 `511b81980c67da9d7e6b9290c20e59959e7d0835496aecee86f170bdc4402212` | canonical amendmentとfresh review |
| D-005 | resolved | interpretation | dev-coder / orchestrator | S00のread-only characterization中、必須の`guidance issue-execution`がignored generated runbook projectionをrefreshした | filesystem writeを理由にS00をfailする; tracked/canonical差分をwrite境界として扱う | generated runbookはcanonical authorityではなく、source/test/config/workflow/docs/reportのtracked差分がなく実行前後cleanであるため、S00のread-only契約は満たす | skillがguidance実行を必須とし、projectionをauthorityとして扱わないことを明記している。実装対象とcanonical docsには変更がない | no_action | S00 worker evidence; `git status --short`実行前後clean; generated projectionはignored | issue-localな実行証跡解釈であり、product contractや将来の設計判断を変更しない |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | `partially_adopted` | research | `requirement.md` / `design.md` / `plan.md` | 現行テスト件数、局所実測、CI履歴、既存ADR境界は採用する。20 PR shadowと未確定のgate案はユーザー判断により採用しない | `artifacts/20260728t015759z-research-unit-test-and-provider-ci-runtime-investigation.md` | canonical docsへ採用範囲を明示して反映 |
| EAL-002 | `adopted` | interview | ADR / `requirement.md` / `design.md` / `plan.md` | Option A、手動＋`main` post-merge、schedule非採用、merge後事後検知というowner intentを確定した | `artifacts/20260728t015759z-01-interview-full-regression-merge-gate-policy.md` | canonical docsへ反映 |
| EAL-003 | `adopted` | discussion | `requirement.md` / `design.md` / `plan.md` | fast default laneとfull regression laneのdurable policy authorityである | `artifacts/20260728t025412z-adr-separate-fast-merge-gate-and-full-regression-execution.md` | canonical docsへ反映し`reflected_to`を更新 |
| EAL-004 | `partially_adopted` | ChatGPT authoring ZIP | `requirement.md` / `design.md` / `plan.md` | 二レーン、共通コマンド、bounded CLI smoke、event matrix、status identity、rollbackは採用する。schedule、旧421秒baseline、全unitをfastに含める案、180秒p95は棄却する | `oracle:iss00342-test-ci-planning`; ZIP SHA-256 `f300cbff69ce241e85462fd5a37fcf2ff7beacad77d8b1d40c133749783e1e01`; 22 files; pack review/stage `pass`; tree digest `cde994609b97c504f47be1c910293eeff53ab24da1d4350b0515952d9490b864`; output form `ZIP/tree`; preservation `reviewed_and_staged`; authority `evidence_only` | main orchestratorが採用claimだけを再記述しfresh reviewを取得 |
| EAL-005 | `adopted` | local checksum verification | EAL-004 source freshness | prompt packの16 source bytesは受領後のlocal checkoutとすべて一致した | source manifestに列挙した16 pathへ`shasum -a 256`を実行; source manifest `303a3ae934595a8d8d41bacddce39b5ddc49a3078cab9e7d0acd5816d1ec1f18`; HEAD=`origin/main`=`3ee6d9047506a40b938407ecfffbb341a3ca76af` | requirement authoringを続行 |
| EAL-006 | `partially_adopted` | system-architect delegated evidence | `design.md` / `plan.md` | native pytest marker、partial-safe classifier、7 required-fast nodes、専用global completeness verifier、2-file workflow、F/H partition、3 paired final measurement batch、rollbackを採用した。旧Make command facadeとdefault marker selectionはD-004/EAL-025でsupersedeした | `artifacts/20260728t041725z-delegated-draft-test-lane-architecture.md`; SHA-256 `4ecf5a906b12a1a5469cff65086421eaae6138caafd3a148be77fc51090f0792`; `specialist_status=usable`; `diff_guard_result=passed`; collection `C=2696/F=661/H=2035/U=0`; focused smoke / parity `7 passed in 2.02s`; design-R3 fresh pass | retained portionsはcurrent canonicalへ統合。command-selectionはEAL-025へ置換 |
| EAL-007 | `adopted` | assurance command evidence | requirement / design / plan source binding | authorized profileを`standard`へ統一したcurrent bytesでsource bindingを更新した。CLIは`stage=requirement`だけを受理するため、design stage相当はrequirement再classify + verifyで実施。compose dry-runはsubstantive designの上書きをfail-closeした | `assurance classify` valid、`authorized_profile=standard`、hard triggers `[]`; `assurance verify` valid; compose dry-run `substantive_content_conflict` / changed paths `[]`; `spec-dock validate` ok `nodes=213`; requirement `3e281337ad72ba52a7e52149c28ff8e6edf4520f7fc5c1bfd5ca7ddbbcf5f097`、design SHA prefix `b8e88c10` / suffix `68c7e4a`、plan `50aecab18b17a67f25867c7ff398ce8b69136b1ca225949b4efa110ca52bd8db` | fresh design re-review |
| EAL-008 | `partially_adopted` | implementation-planner delegated evidence | `plan.md` | 22 closure、TDD steps、allowed paths、known flaky、最終3-pair full batch、fresh reviews、PR 3 runs、human merge boundaryを採用し、plan-R1〜R4後はS00〜S130のstep-local contractsへ再構成した。旧step groupingとexecution-readiness self-claimは不採用のまま | `artifacts/20260728t044933z-delegated-draft-test-lane-implementation-plan.md`; SHA-256 `12140489cc982c1b3ceda9a3739fc6b6b36f3d8535e24c803115e55d7e0a75e3`; `specialist_status=usable`; `diff_guard_result=passed`; plan-R1/R2/R3/R4 remediation; fresh plan-R5 findings `[]` / pass | adopted portionsのcanonical反映とreview完了。追加actionなし |
| EAL-009 | `adopted` | planning assurance evidence before plan-R1 | requirement / design / plan source binding | initial substantive planとexact Design / Evidence ID正規化後のbytesをStandard profileへbindしたhistorical evidence。plan-R1 remediation後はEAL-010がcurrent binding | classify / verify `valid`; `authorized_profile=standard`; requirement `3e281337ad72ba52a7e52149c28ff8e6edf4520f7fc5c1bfd5ca7ddbbcf5f097`; design `dcba55f97e3159525d4b707a71f09ac6c69d6b5e2ea777e1371fdf7748470811`; plan SHA prefix `bfdc6513` / suffix `fceca4`; validate `nodes=213`; diff check pass | superseded operationally by EAL-010; historical review inputとして保持 |
| EAL-010 | `adopted` | plan-R1 remediation assurance evidence | requirement / design / plan source binding | authorization、exact closure evidence、step-local schema/cards、per-step review/Result Approval、S90/S99/PR delivery、known flaky/full-count境界を修正したdraftをStandard profileへbindしたhistorical evidence。runtime guidance診断前bytes | classify / verify `valid`; `authorized_profile=standard`; hard triggers `[]`; warningsなし; requirement `3e281337ad72ba52a7e52149c28ff8e6edf4520f7fc5c1bfd5ca7ddbbcf5f097`; design `dcba55f97e3159525d4b707a71f09ac6c69d6b5e2ea777e1371fdf7748470811`; plan SHA prefix `a2c4d51a` / suffix `faf6e`; validate `nodes=213`; tracked diff check pass; untracked plan whitespace diagnosticsなし | EAL-011のdesign path修正後にsource bindingを再refresh |
| EAL-011 | `adopted` | runtime guidance / source diagnosis | `design.md` §16.1 / planning gate | active symlinkとcanonical designは同一SHAだったが、fenced tree内の省略形Issue directory tokenをplaceholder detectorが誤認し`design-not-substantive`となった。content/state不足ではないためexact scope pathへsyntax-only展開する | `guidance issue-planning`: blocked / `design-not-substantive`; `_classify_design_text`→`_has_placeholder_code_spans`; active/canonical design SHA一致 `dcba55f97e3159525d4b707a71f09ac6c69d6b5e2ea777e1371fdf7748470811`; offending line §16.1 | designをdraftへ戻しexact path化、assurance refresh、fresh design-R4 review |
| EAL-012 | `adopted` | post-guidance-fix assurance evidence | requirement / design / plan source binding | §16.1 exact path化、design R4 pending、plan readiness update後のdraft bytesをStandard profileへbindした | classify / verify `valid`; `authorized_profile=standard`; hard triggers `[]`; warningsなし; requirement `3e281337ad72ba52a7e52149c28ff8e6edf4520f7fc5c1bfd5ca7ddbbcf5f097`; design SHA prefix `b2917cc8` / suffix `b5985c4`; plan SHA prefix `e9865087` / suffix `3260d0`; validate `nodes=213`; tracked diff check pass | design-R4 fresh passを取得。approved state反映後に再bind |
| EAL-013 | `adopted` | fresh design-R4 reviewer evidence | `design.md` / planning gate | §16.1 exact path化がscope、architecture、AC/BH/CON、DES契約を変えず、approved時にruntime classifierが`substantive`となることを確認した | fresh `spec-reviewer`; findings `[]`; `review_status=pass`; overall confidence `0.99`; reviewed design SHA prefix `b2917cc8` / suffix `b5985c4` | designをapprovedへpromoteしassurance再refresh後、plan-R2へ進む |
| EAL-014 | `adopted` | design-R4 promotion assurance evidence | requirement / design / plan source binding | design-R4 approved stateとplan-R1 remediation後のcurrent bytesをStandard profileへbindした | classify / verify `valid`; `authorized_profile=standard`; hard triggers `[]`; warningsなし; requirement `3e281337ad72ba52a7e52149c28ff8e6edf4520f7fc5c1bfd5ca7ddbbcf5f097`; design `fe31a307c9c498852e782b5d5bedab538c565c5478b040057b2a68ddbddefa9d`; plan SHA prefix `2b410115` / suffix `b277d`; design substantive; guidance `plan-not-executable`はplan draftによるexpected fail-closed; validate `nodes=213`; diff check pass | fresh plan-R2 review |
| EAL-015 | `adopted` | plan-R2 remediation assurance evidence | requirement / design / plan source binding | S05 docs freshness、S98/S100 non-circular evidence、Result Approval順、S130 lifecycle、task-local authorizationを修正したdraftをStandard profileへbindした | classify / verify `valid`; `authorized_profile=standard`; hard triggers `[]`; warningsなし; requirement `3e281337ad72ba52a7e52149c28ff8e6edf4520f7fc5c1bfd5ca7ddbbcf5f097`; design `fe31a307c9c498852e782b5d5bedab538c565c5478b040057b2a68ddbddefa9d`; plan SHA prefix `6c1490c1` / suffix `6937e`; guidance `plan-not-executable`はdraftによるexpected fail-closed; validate `nodes=213`; diff check pass | fresh plan-R3 review |
| EAL-016 | `adopted` | fresh plan-R3 reviewer evidence | `plan.md` / planning gate | future external closureをS99でfalse passにする循環、mandatory ledger commitでS05をstaleにするfreshness predicate、default fast 3入口/failure pathの具体検証欠落、stale report gateを検出した | fresh `spec-reviewer`; reviewed plan SHA prefix `6c1490c1` / suffix `6937e`; P1 3件/P2 1件; `review_status=fail`; overall confidence `0.98` | plan-R3 findingsを修正し、current bytesへassurance refresh後fresh plan-R4 review |
| EAL-017 | `adopted` | plan-R3 remediation assurance evidence | requirement / design / plan source binding | S99を15 pass + 7 pending externalへ分離しS130 final auditを追加、S05をtest-relevant manifestで固定、default fast 3入口/failure pathを具体化したcurrent draftをStandard profileへbindした | classify / verify `valid`; `authorized_profile=standard`; hard triggers `[]`; warningsなし; requirement `3e281337ad72ba52a7e52149c28ff8e6edf4520f7fc5c1bfd5ca7ddbbcf5f097`; design `fe31a307c9c498852e782b5d5bedab538c565c5478b040057b2a68ddbddefa9d`; plan SHA prefix `e87eb8c5` / suffix `b96ece`; guidance `plan-not-executable`はdraftによるexpected fail-closed; validate `nodes=213`; diff check pass | fresh plan-R4 review |
| EAL-018 | `adopted` | fresh plan-R4 reviewer evidence | `plan.md` / planning gate | R3 remediationは整合したが、dev-coder role contractが禁止する`pyproject.toml`/workflow mutationをS01/S03へ割り当てた実行不能を検出した | fresh `spec-reviewer`; reviewed plan SHA prefix `e87eb8c5` / suffix `b96ece`; P1 1件; `review_status=fail`; overall confidence `0.99`; `.codex/agents/dev-coder.toml` hard rule | config/Make/workflowをbounded utility-worker、tests/hookをdev-coderへpath分離し、assurance refresh後fresh plan-R5 review |
| EAL-019 | `adopted` | plan-R4 remediation assurance evidence | requirement / design / plan source binding | tests/hookをdev-coder、`pyproject.toml`/`Makefile`/provider workflowsをbounded utility-workerへpath分離したcurrent draftをStandard profileへbindした | classify / verify `valid`; `authorized_profile=standard`; hard triggers `[]`; warningsなし; requirement `3e281337ad72ba52a7e52149c28ff8e6edf4520f7fc5c1bfd5ca7ddbbcf5f097`; design `fe31a307c9c498852e782b5d5bedab538c565c5478b040057b2a68ddbddefa9d`; plan `2e744c753f72ee2e2ed8e8ff7b49cf8a5ffa27ebbe39c6d6622a16cfbe3e8bca`; guidance `plan-not-executable`はdraftによるexpected fail-closed; validate `nodes=213`; diff check pass | fresh plan-R5 review |
| EAL-020 | `adopted` | fresh plan-R5 reviewer evidence | `plan.md` / planning gate | R1〜R4 remediation、22 closure/24 cards、role-separated implementation、S05/S98〜S100/S130を照合し、canonical planのpromotionを承認した | fresh `spec-reviewer`; reviewed plan `2e744c753f72ee2e2ed8e8ff7b49cf8a5ffa27ebbe39c6d6622a16cfbe3e8bca`; findings `[]`; `review_status=pass`; overall confidence `0.99` | planをapprovedへpromote済み。EAL-021のapproved-state assuranceへ引き渡した |
| EAL-021 | `adopted` | approved-state final assurance evidence | requirement / design / `plan.md` source binding | plan-R5 pass反映後のapproved canonical bytesをauthorized Standard profileへ再bindし、実行契約のsource freshnessを確定した | `.assurance.json`; classify / verify `valid`; `authorized_profile=standard`; hard triggers `[]`; warningsなし; requirement `3e281337ad72ba52a7e52149c28ff8e6edf4520f7fc5c1bfd5ca7ddbbcf5f097`; design `fe31a307c9c498852e782b5d5bedab538c565c5478b040057b2a68ddbddefa9d`; plan `69b3cec7278694bd374b35a9621386be6de01c5a65f417bbd78f837f736c092a`; validate `nodes=213`; diff check pass | EAL-022のfinal planning guidanceへ引き渡した |
| EAL-022 | `adopted` | final issue-planning guidance | planning gate | report readiness、fresh review、specialist evidence、approved source bindingをruntime契約値で照合し、Issue計画の引き渡し可能状態を確認した | `guidance issue-planning`: state `ready`; next action `planning-ready`; reason `assurance-valid`; active issue `iss-00342`; `may_execute_approved_plan=false`; authorized profile `standard`; `spec-dock validate` ok `nodes=213` | planning gate完了。Issue startと実装は行わず、後続のIssue execution workflowでadmissionを別途確認する |
| EAL-023 | `partially_adopted` | ChatGPT authoring ZIP | `requirement.md` / `design.md` / `plan.md` / ADR | direct ordinary commands、`--run-full-regression` permission、conditional policy skip、marker-only非許可、legitimate skip保全、event matrix、rollbackを採用した。evidence-only frontmatter、self-review claim、詳細候補の正本byte-copyは採用しない | `oracle:iss00342-pytest-opt-in-authoring`; branch `codex/iss-00342-pytest-opt-in-planning`; source commit `2513c943fee26de16d0c0371eafeaa5a484cfd43`; ZIP SHA-256 `511b81980c67da9d7e6b9290c20e59959e7d0835496aecee86f170bdc4402212`; pack digest `466409f6203f455be53a483b5a36ac712542406a9b8106f6689739f4f392d6e1`; pack review/stage pass | main orchestratorがIssue-local draftへ要約しcanonical docsへ再記述 |
| EAL-024 | `adopted` | authoring draft adoption validation | ChatGPT draft preservation boundary | Issue-local 3 draftのpath/hash、source manifest、pack reviewをgithub-synced evidenceとして検証した。repository外review reportの初回拒否とforbidden phrase/review digest mismatchのR1拒否はno-writeで解消した | `authoring validate issue-draft-adoption` R2: status `pass`; findings/comparison `[]`; draft_count=valid_draft_count=`3`; review digest `1442414de900af53120952950d790fbdfb1cfca71a0d129a47ee397f5e2d2bfe`; source hash `f40f3dac04774c04df9a0d3fb015d59a2f250f246b5e2a9403c17139fcd14577`; canonical_written/assurance_mutated/execution_ready=`false` | EAL dispositionとcanonical rewriteへ進む |
| EAL-025 | `adopted` | accepted ADR | `requirement.md` / `design.md` / `plan.md` | accepted Option Aのevent routingを維持し、旧command-selectionだけをdirect pytest + explicit permissionへrefineするdurable decisionとして採用した | `artifacts/20260728t105349z-03-adr-use-direct-pytest-commands-with-explicit-full-regression-opt-in.md` | canonical docsへ反映しfresh review |
| EAL-026 | `adopted` | main orchestrator canonical rewrite | `requirement.md` / `design.md` / `plan.md` | old default marker/Make facade契約をowner決定とaccepted ADRに合わせて置換し、implementation scopeをhook/config/workflow/docsへ限定した | `requirement.md`; `design.md`; `plan.md`; `git diff --check`とfresh spec reviewer予定 | assurance refreshとfresh reviewer gate |
| EAL-027 | `adopted` | fresh command-interface amendment review | `requirement.md` / `design.md` / `plan.md` / `report.md` / ADR | selection/permission分離、conditional policy skip、legitimate skip保全、focused safety、event matrix、role/path ownership、closure traceability、ADR/EAL authorityをcurrent bytesで照合した | fresh `spec-reviewer`; findings `[]`; `review_status=pass`; confidence `0.99`; reviewed requirement `d6c4d2eb518500a94e5bc13fecbac9b9a9c703334f967b9798cd2aff3aa4e665`; design `0a0d94483981244d522e4555cf174fffd51b808b4f5e9d7a5b59e927a1b2cc03`; plan `d8c6d411e6f4821ac0b393faf42a7d631f42854bb954f5d380e06780bbcf080c`; report `d8be20793e8e7ebc9e809850fa5658a47f3c58041a116111e56e989e5caf81d3`; ADR `de1af0daf42f1cd6f279dc106f1aee16012bcbe69488b2544105e42fdc6192e7` | canonical docsをapprovedへpromoteしapproved bytesをassuranceへ再bind |
| EAL-028 | `adopted` | approved amendment assurance and planning guidance | requirement / design / plan source bindingとplanning gate | fresh review後のapproved bytesをauthorized Standard profileへ再bindし、計画handoff可能状態を確認した | classify dry-run/write/verify `valid`; hard triggers `[]`; requirement `1bb239d591b88f27e0672ca259639c29b0b43ab135db8257f27534dea55142cb`; design `c9df294d5c0bc62830fff231bc7b6ab343fcf24c73457e254705fc7f54487f30`; plan `21239b0b45255fcf838b9b6d774c4163c716779cefb6121c607283f88cba6eca`; validate `nodes=213`; guidance state `ready`, next action `planning-ready`, reason `assurance-valid`, `may_execute_approved_plan=false` | planning完了。Issue execution admissionは別workflowで確認する |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | PR merge gateと通常開発の既定テストを長時間完全回帰から分離する | full test集合、parity、代表的CLI contract、post-merge failure signalを保持する | low: full短縮そのものを主目的へ戻すとfast-path分離が遅れる | passed: fresh requirement re-review |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | research、現行workflow、既存ADR、GitHub run、answered interview、accepted ADR、ChatGPT ZIP、source-hash照合 | answered: Option A refined policy。open owner questionなし | EAL-001〜005へ採否を記録し、requirement-R2 findings 0を確認した | passed | no | promote |
| design | current sources、system-architect evidence、collect-only `C=2696/F=661/H=2035/U=0`、required-fast 7 node、pytest CLI `-m` override、phase design contract、runtime guidance diagnosis | answered: focused collectionではglobal inventoryを要求せずfull completenessは専用verifierへ分離。AC-008は最終measurement batch内で3 paired runs。§16.1省略pathはexact scope pathへ展開 | EAL-006を採用し、provider-only non-shipping、module dependency図、Linux tree変更計画を反映。design-R4 findings 0を確認した | passed | no | promote |
| plan | approved requirement/design、implementation-planner evidence、known flaky、performance / external observation boundaries、plan-R1〜R4 findings | answered: exactly 3はpre-merge routine measurement batchに限定する。S05 freshnessはtest-relevant manifest、S99は15 pass + 7 pending external、S130でfinal 22-closure audit。dev-coder禁止のconfig/workflowはbounded utility-workerへpath分離する | EAL-008 adopted portionsをcanonical Standard/TDD planへ再記述し、EAL-020でplan-R5 findings 0、EAL-021でapproved bytesの再bindを確認した | passed | no | execute approved plan |
| command-interface amendment | owner clarification、accepted Option A ADR、ChatGPT GitHub-synced ZIP、Issue-local draft adoption validation | answered: ordinary pytestは変更しない。long executionだけ`--run-full-regression`を要求し、marker-onlyはpermissionにしない | EAL-023〜028へ採用境界、ADR、canonical rewrite、fresh review、approved assuranceを記録した | passed: findings `[]`, confidence `0.99` | no | planning-ready。実装はIssue execution admission後 |

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）
- 委任 authoring の使用:
  - used
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
| system-architect | iss-00342 | `artifacts/20260728t041725z-delegated-draft-test-lane-architecture.md` | current requirement / ADR / research / workflow / pytest config / Makefile / relevant tests | `design.md` / `plan.md` | integrated | `design.md` | `passed`: canonical requirement/design/plan/reportの前後SHA一致、artifactのみ追加 | main orchestratorがsource-grounded部分を再記述。focused-safe guardと3 paired batch修正を統合。artifact self-claimの`unreviewed`はcanonical adoption claimに昇格させていない | 旧global hookで全required node / `H>0`を常時要求する案、full 1回表現 | なし | passed | promote |
| implementation-planner | iss-00342 | `artifacts/20260728t044933z-delegated-draft-test-lane-implementation-plan.md` | approved requirement/design、report、assurance、ADR/research/interview、phase plan contract、current tests/config/workflows/docs | `plan.md` | partially_integrated | `plan.md` | `passed`: canonical requirement/design/plan/reportのbefore/after SHA一致、artifactのみ追加 | main orchestratorが22 closureとTDD骨格を採用し、plan-R1〜R4後にS00〜S130のexact evidence、step-local schema/cards、role-separated implementation、delivery/lifecycle gatesへ再記述。artifact self-claimの`unreviewed`はcanonical adoption claimに昇格させていない | delegated artifactのexecution readiness self-claimなし。旧step groupingはcanonical contractとして不採用 | none | passed | execute approved plan |

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
- S00 baseline characterizationを完了し、current SHAでcollection 2,696件、required-fast 7件、known flaky候補1件を変更なしで再確認した。
- S01以降の実装は未着手であり、この時点ではsource、test、config、workflow、contributor docsに変更はない。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-07-28 23:43 - 23:46 JST）

#### 対象
- Step: S00 Baseline characterization
- AC/EC: AC-006、AC-007、CON-004
- 計画上の出典（Planned source）:
  - `plan.md` section: `S00 Baseline characterization`
  - closure ids: `CLOS-TL-AC-006`、`CLOS-TL-AC-007`、`CLOS-TL-CON-004`

#### 実施内容
- `dev-coder`へread-only characterizationを委任し、current SHAのroot collection、required-fast 7 nodes、known flaky候補を各1回観測した。
- sorted node IDsと明示skip/skipif/xfail source inventoryを正規化し、baseline SHAとtoolchainへ結び付くSHA-256 digestとして固定した。
- source/test/config/workflow/docs/reportはworker実行中read-onlyとし、実行前後のtracked worktreeがcleanであることを確認した。
- 必須runtime guidanceがignored generated runbook projectionをrefreshした可能性はD-005へ記録し、canonical/tracked差分なしとして採用した。

#### 実行コマンド / 結果
```bash
git rev-parse HEAD
# 701b7ae5cbb197e26aa69968ba53ccb9c722a873

uv run python --version
# Python 3.12.11

uv run pytest --collect-only -q -p no:cacheprovider
# exit 0; 2696 tests collected in 0.23s; baseline count delta 0

uv run pytest --collect-only -q -p no:cacheprovider \
  | awk '/^tests\/.*::/ { sub(/\r$/, ""); print }' \
  | LC_ALL=C sort \
  | uv run python -c 'import hashlib, sys; data = sys.stdin.buffer.read(); print(f"count={data.count(chr(10).encode())}"); print(f"sha256={hashlib.sha256(data).hexdigest()}")'
# exit 0; count=2696
# sha256=07ac3d3846e02d85b95edff9ec9c55240598dafa6364e458a61b5c962833859c

rg -n --no-heading --color=never \
  'pytest\.mark\.(skip|skipif|xfail)([^[:alnum:]_]|$)' tests \
  | awk '{ sub(/\r$/, ""); print }' \
  | LC_ALL=C sort \
  | uv run python -c 'import hashlib, sys; data = sys.stdin.buffer.read(); print(f"count={data.count(chr(10).encode())}"); print(f"sha256={hashlib.sha256(data).hexdigest()}")'
# exit 0; count=67
# sha256=b77e4a64ca5dd3e909f6df9f850ef312317880918884fffafa56f274d6dda3af
# explicit source occurrences: skip=67, skipif=0, xfail=0

uv run pytest --collect-only -q -p no:cacheprovider -m skip
# exit 0; 68/2696 selected, 2628 deselected
uv run pytest --collect-only -q -p no:cacheprovider -m skipif
# exit 5; 0 selected, 2696 deselected
uv run pytest --collect-only -q -p no:cacheprovider -m xfail
# exit 5; 0 selected, 2696 deselected

uv run pytest -q -p no:cacheprovider \
  tests/unit/cli/test_cli_smoke.py::TestCliSmoke::test_active_set_legacy_flag_reports_parser_error \
  tests/unit/cli/test_cli_smoke.py::TestCliSmoke::test_active_set_by_id_succeeds_through_runtime_subprocess \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_mirror_docs_match_provider_assets \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_mirror_templates_match_provider_assets \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_68_workflow_seed_matches_repo_root_ci_workflow \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_68_provider_only_workflow_is_not_shipped_via_install_root \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets
# exit 0; 7 passed in 1.87s

uv run pytest -q -p no:cacheprovider \
  tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_187_s430_final_snapshot_timeout_preserves_stable_completion_state
# exit 0; 1 passed in 2.36s
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S00 | 代替証跡（characterization-first） | current C、sorted node IDs、skip/xfail inventory、required-fast 7件、known flaky raw result | C=2696、node digest `07ac3d...859c`、marker source digest `b77e4a...a3af`、required-fast 7 passed、known flaky 1 passed | collect-only、normalized digest pipelines、exact focused commands | pass | baseline count delta 0。known flakyの1回passはflaky解消の証拠にしない |
| S00 | リファクタリング（Refactor） | read-only stepのためrefactorなし | tracked diffなし | `git status --short` | approved-no-op | source/test/config/workflow/docs/reportのworker変更なし |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S00 | runtime guidanceがignored generated projectionをrefreshした可能性 | worker observation | D-005でtracked/canonical差分なしのdiagnostic side effectとして解決 | none | no | 実行前後`git status --short` clean |
| S01 | new contract testsによりroot collectionが5件増加 | implementation | expected closure deltaとして記録 | `CLOS-TL-AC-002`,`CLOS-TL-AC-007` | no | C 2696→2701、F 661→666、H 2035据え置き。追加5件はlane contract tests |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S00 | `CLOS-TL-AC-006`,`CLOS-TL-AC-007`,`CLOS-TL-CON-004` | collection、required-fast、known flaky、coverage baselineをcurrent SHAで固定 | C=2696、node digest `07ac3d...859c`、marker inventory digest `b77e4a...a3af`、7 passed、1 passed、tracked diffなし、S00-R2 fresh review pass | pass | M0 commitとpost-commit cleanは後続欄で閉じる |
| S01 | `CLOS-TL-AC-001`,`CLOS-TL-AC-002`,`CLOS-TL-AC-006`,`CLOS-TL-AC-007`,`CLOS-TL-BH-001`,`CLOS-TL-BH-002` | partial-safe exactly-one classifier、global partition、required-fast、conflict、early marker visibility | active Red→Green、lane module 5 passed、required-fast 7 passed、C/F/H=2701/666/2035 | pass | fresh code-reviewerとM1a commit gateはpending |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| `CLOS-TL-AC-006` | S00 | yes | characterization-first + automated | research C=2696、required-fast 7 passed | collect-only + required-fast exact command | pass | current C=2696、required-fast 7 passed |
| `CLOS-TL-AC-007` | S00 | yes | characterization-first + review | research baselineとknown flaky候補 | sorted node digest、marker inventory digest、known flaky exact command | pass | node digest `07ac3d...859c`、marker digest `b77e4a...a3af`、known flakyは1回pass、reviewはpending |
| `CLOS-TL-CON-004` | S00 | yes | characterization-first + review | test weakening禁止 | `git status --short`、sorted node/marker inventory、focused result | pass | workerによるtest/config変更なし、reviewはpending |
| `CLOS-TL-AC-001` | S01 | yes | red-required | classifier欠落のexpected Red | focused/H=0 contract test | pass | Red exit 1からGreen 1 passed。S02 command/policy部分は未実装 |
| `CLOS-TL-AC-002` | S01 | yes | red-required | S00 C/F/H=2696/661/2035 | lane module + root F/H verifier | pass | C/F/H=2701/666/2035、U=0、overlap=0 |
| `CLOS-TL-AC-006` | S01 | yes | automated | required-fast exact 7 baseline | root verifier + required-fast exact command | pass | required-fast 7 nodes∈F、7 passed |
| `CLOS-TL-AC-007` | S01 | yes | red-required + review | S00 node/marker baseline | conflict/override negative tests + collection delta | pass | expected +5 lane testsのみ。fresh review pending |
| `CLOS-TL-BH-001` | S01 | yes | red-required | classifierなし | focused classification contract | pass | partial-safe classificationを確認。execution policyはS02 owner |
| `CLOS-TL-BH-002` | S01 | yes | red-required | H=2035 baseline | global verifier + marker selection | pass | H=2035を維持。full permissionはS02 owner |

- `closure id / test id` は Spec-Locked Closure Index の `id` を指す。別 alias を使う場合は `Closure Delta` で対応を記録する。

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| `CLOS-TL-AC-006` | S00 | C=2696、required-fast 7 passed | pass | current SHA `701b7ae5` |
| `CLOS-TL-AC-007` | S00 | C=2696、sorted node digest `07ac3d...859c`、known flaky exact node pass | pass | SHA `701b7ae5`、Python 3.12.11、uv 0.11.24、macOS arm64、normalization pipelineを固定しcommitから再生成可能 |
| `CLOS-TL-CON-004` | S00 | marker source 67行/digest `b77e4a...a3af`、marker collection skip=68/skipif=0/xfail=0、tracked source clean | pass | source occurrenceとparameterized item数は粒度が異なる。runtime skip数とは主張しない |
| `CLOS-TL-AC-001` | S01 | focused Red→Green、H=0 subset成功 | pass | S02 command/policy closureは未完了 |
| `CLOS-TL-AC-002` | S01 | C/F/H=2701/666/2035、U=0、overlap=0 | pass | global verifierのみがrepository completenessを要求 |
| `CLOS-TL-AC-006` | S01 | required-fast 7 nodes∈F、7 passed | pass | exact inventory不変 |
| `CLOS-TL-AC-007` | S01 | conflict/forbidden overrideはcollection nonzero、expected +5 test delta | pass | fresh review pending |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | `CLOS-TL-AC-006`,`CLOS-TL-AC-007`,`CLOS-TL-CON-004` | `tc-s00-001`,`tc-s00-002` | same | required row、locked expectation、required、spec linkに変更なし | no | no |
| added | `CLOS-TL-AC-002`,`CLOS-TL-AC-007` | `tc-s01-001`〜`tc-s01-004` | same | S01 contract test 5 itemsをfastへ追加。locked expectationとrequired-fast inventoryは不変 | no | no |

#### ワークフロー単位の named role 許可（Workflow-Scoped Authorization）
`workflow_issue.md` is the policy source for workflow-scoped authorization. This report records observed authorization source, boundary, expiry, and denied / unavailable / host conflict handling only.

Authorization source は、ユーザーによる SpecDock workflow 利用依頼でよい。範囲は active repo/worktree、active SpecDock scope、current session、SpecDock-defined named roles、documented role responsibility に限る。この section は role ごと・phase ごとの追加承認 gate ではなく、scope 内の named role 利用前に追加許可を求める根拠にしてはならない。

別途確認が必要なのは scope expansion、破壊的操作、外部公開、credential を伴う外部 mutation、private external system、SpecDock workflow 外の role 利用である。unavailable / denied / host conflict は fail-closed とし、fresh `passed` reviewer gate の代替にしてはならない。

| 許可元（authorization source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可 / host conflict 理由（denied / unavailable / host conflict reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| ユーザーによるSpecDock workflow利用依頼と`spec-dock-clarification`指定 | `/Volumes/990p2t/offloaded/home/iwasawayuuta/.codex/worktrees/09ed/spec-dock` | iss-00342 | 本Issueの現在セッション | authoring/planning: `spec-manager`、`system-architect`、`implementation-planner`、`spec-reviewer`; execution予定: `dev-coder`、`utility-worker`、`doc-writer`、`code-reviewer`、`qa-reviewer` | active repo/worktree、active iss-00342 scope、current session、各SpecDock-defined named roleのdocumented responsibilityに限定する。`utility-worker`はplanでpath限定した`pyproject.toml`とprovider workflowsのbounded config touch-upだけを担当し、`Makefile`はread-onlyとする。scope expansion、破壊的操作、外部公開、credentialed external mutation、private external system、workflow外roleは含めない | Issue完了、セッション終了、scope変更、host policy conflict、user revocationのいずれか | なし。利用拒否、role unavailable、host conflictは観測されていない | workflow内のauthoring/reviewを続行する。PR作成・push・rerun等のcredentialed external mutationは実行時にin-scope authorizationを確認し、不足時は停止する |

##### Task-local scope-local artifact direct-write authorization

read-only specialist consentと、scope-local `artifacts/` direct childへの限定書き込みを分離して記録する。次の許可はcanonical docs、implementation、Git/GitHub mutationを含まない。

| Authorization ID | 許可元 | Invocation / role | 許可されたexact output | Filename rule | 禁止path / operation | 必須post-run evidence | 結果 / 失効 |
|---|---|---|---|---|---|---|---|
| `AUTH-DD-TL-001` | ユーザーのSpecDock workflow利用依頼とworkflow-scoped named-role authorization | `/root/architect_iss00342_test_lanes` / `system-architect` | `artifacts/20260728t041725z-delegated-draft-test-lane-architecture.md` | Issue `artifacts/` direct childのtyped Markdown 1件 | canonical requirement/design/plan/report、source/tests/workflows、`.assurance.json`、Git/GitHub mutation | lightweight provenance、`adoption_status: unreviewed`、`reflected_to: []`、canonical 4文書before/after SHA、diff guard、Ledger Note | completed; diff guard passed; Issue/session/scope変更またはuser revocationで失効 |
| `AUTH-DD-TL-002` | ユーザーのSpecDock workflow利用依頼とworkflow-scoped named-role authorization | `/root/plan_iss00342_test_lanes` / `implementation-planner` | `artifacts/20260728t044933z-delegated-draft-test-lane-implementation-plan.md` | Issue `artifacts/` direct childのtyped Markdown 1件 | canonical requirement/design/plan/report、source/tests/workflows、`.assurance.json`、Git/GitHub mutation | lightweight provenance、`adoption_status: unreviewed`、`reflected_to: []`、canonical 4文書before/after SHA、diff guard、Ledger Note | completed; diff guard passed; Issue/session/scope変更またはuser revocationで失効 |

#### 実装委任ゲート（Implementation Delegation Gate）
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S00 | delegated | approved planがread-only baseline operatorを要求 | dev-coder | current SHAのcollection、required-fast、known flaky characterization | approved requirement/design/plan、research、`pyproject.toml`、`tests/**` | read-only commandsのみ | source/test/config/workflow/docs/report変更、full実行 | collect-only、required-fast 7、known flaky exact node、前後clean | C drift、required-fast欠落、unexpected failure、tracked write | command/exit/count/elapsed/SHA、risk、EVD note、Ledger Note | pass |
| S01 | delegated | tests/hookとpytest configをrole/path分離してtest-first実装するapproved contract | dev-coder + bounded utility-worker | classifier contract testsとhook / marker registryとstrictness | approved requirement/design/plan、S00 evidence、current pytest config/tests | dev-coder: `tests/conftest.py`,`tests/unit/test_provider_test_lanes.py`; utility-worker: `pyproject.toml` | workflow/docs/Make/dependency、S02 option/policy、test weakening | active Red、lane module、root F/H collection、required-fast、ruff、TOML/help、diff check | unexpected Red、focused global guard、inventory変更、allowed外diff | role別changed files、Red/Green/Refactor、commands、risk、EVD note、no-material decision | implementation pass; reviewer pending |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S00 | dev-coder | current SHAのC、required-fast 7件、known flakyをread-onlyで再観測 | none | collect-only: 2696/exit 0; node/marker digests再生成一致; required-fast: 7 passed; known flaky: 1 passed | S00-R2 passed | known flakyの1回passは解消証拠ではない | evidence accepted。projection副作用はD-005でno_action |
| S01 | dev-coder | classifier contractをRed-firstで追加しpartial-safe classifierをMinimal Green | `tests/conftest.py`,`tests/unit/test_provider_test_lanes.py` | Red exit1; Green active 1 passed; module 5 passed; required-fast 7 passed; C/F/H=2701/666/2035; ruff/diff pass | S01-R1 passed | future competing tryfirst hookはordering再検証が必要 | accepted。S02 option/policyは未実装を確認 |
| S01 | utility-worker | pytest strict markersとfast/full marker registryだけを追加 | `pyproject.toml` | TOML parse、pytest help、diff check pass | S01-R1 passed | none | accepted。default `-m fast`、dependency、Make変更なし |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| S01 | unavailable / denied / host conflict / impossible because ... | approval source / risk accepted: yes / no | `path/to/file` | ... | ... | `command` -> pass / docs-only inspection -> pass | reviewer role + passed / failed / unavailable / denied / waived / provisional | blocked / incomplete / waived with explicit risk acceptance / next action |

#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）
Lite は specialist / fallback evidence を必須化しないが、not applicable / skip reason を記録する。Standard は specialist evidence、skip reason、または manual fallback を記録する。Strict / Critical は specialist evidence または明示的な manual fallback を記録し、skip reason だけでは readiness evidence にしない。

本Issueのauthorized profileは`standard`であるため、観測対象となるStandard行だけを記録する。Lite / Strict / Criticalは本Issueに適用しておらず、未実施のreview結果を記録しない。

| グレード（Grade） | 必要な専門家 / 代替（required specialist / fallback） | 使用状況（usage） | 証跡（evidence） | 鮮度 spec-reviewer 判定（fresh spec-reviewer verdict） | 実行可否（execution readiness） |
|---|---|---|---|---|---|
| `standard` | `system-architect` + `implementation-planner` | `used` | architecture artifact `artifacts/20260728t041725z-delegated-draft-test-lane-architecture.md` SHA-256 `4ecf5a906b12a1a5469cff65086421eaae6138caafd3a148be77fc51090f0792`; planning artifact `artifacts/20260728t044933z-delegated-draft-test-lane-implementation-plan.md` SHA-256 `12140489cc982c1b3ceda9a3739fc6b6b36f3d8535e24c803115e55d7e0a75e3`; both `specialist_status=usable` / diff guard passed | passed | ready |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| requirement-R1 | requirement review | spec-reviewer | historical | failed | no | blocked | parent allocation、event matrix、未承認hard performance thresholdのP1 3件 |
| requirement-R2 | requirement re-review | spec-reviewer | fresh | passed | no | promote | 親plan追記、truth table固定、性能thresholdを非blocking targetへ修正後にfindings 0 |
| design-R1 | requirement + design review | spec-reviewer | historical | failed | no | blocked | focused collectionを壊すglobal guard、3 paired runsとfull 1回の矛盾、specialist provenance欠落のP1 3件。provider-only non-shippingとADR reflected_toのP2 2件 |
| design-R2 | requirement + design re-review | spec-reviewer | historical | failed | no | blocked | R1修正は確認済み。Standard / strict template文言の矛盾、module dependency図とLinux tree変更計画欠落のP1 2件、diagram metadataのP2 1件 |
| design-R3 | requirement + design re-review | spec-reviewer | historical | passed | N/A | proceed | P0/P1とtrace gapなし。non-blocking P2のno-decision矛盾を修正しplan authoringへ昇格 |
| design-R4 | runtime-compatible design re-review | spec-reviewer | fresh | passed | no | promote | §16.1 exact canonical path化は意味論不変。placeholder helpers false、approved時classifier substantive、findings 0 |
| plan-R1 | plan review | spec-reviewer | historical | failed | no | blocked | Workflow-Scoped Authorization、22 closureのexact evidence、step-local schema/test cards、per-step review/Result Approval、S90/S99/PR deliveryのP1 5件。known flaky redとfull exactly 3境界のP2 2件 |
| plan-R2 | plan re-review | spec-reviewer | historical | failed | no | blocked | S90によるfull evidence失効、post-final-commit evidence循環、sync/issue-finish終端欠落、Result Approval順序のP1 4件。task-local direct-write authorizationのP2 1件 |
| plan-R3 | plan re-review | spec-reviewer | historical | failed | no | blocked | S99 future-evidence closure cycle、S05 freshness predicate、default fast 3入口/failure pathのP1 3件。Delegated Draft/Grade gate stale statusのP2 1件 |
| plan-R4 | plan re-review | spec-reviewer | historical | failed | no | blocked | dev-coder role contractが禁止するconfig/workflow mutationをS01/S03へ割り当てたP1 1件 |
| plan-R5 | plan re-review | spec-reviewer | fresh | passed | no | execute approved plan | R1〜R4 remediation、22 closure/24 cards、role configs、delivery/lifecycle gatesを再確認。findings 0、confidence 0.99 |
| command-amendment-R1 | requirement / design / plan amendment review | spec-reviewer | fresh | passed | no | promote | direct ordinary pytest、explicit full permission、conditional policy skipへの改訂をcurrent bytesで確認。findings 0、confidence 0.99 |
| S00-R1 | baseline characterization review | code-reviewer | historical | failed | no | blocked | countだけでは同数node入れ替えとskip/xfail差分を検出できず、baseline manifest evidenceが不足 |
| S00-R2 | baseline characterization re-review | code-reviewer | fresh | passed | no | proceed to M0 commit | node digestとmarker inventory digestを独立再生成し一致。findings 0、confidence 0.99 |
| S01-R1 | classifier / marker config review | code-reviewer | fresh | passed | no | proceed to M1a commit | partial safety、exactly-one、required-fast/heavy規則、early marker、strict config、S02非混入を確認。findings 0、confidence 0.99 |

#### マイルストーン / commit 候補ゲート（Milestone / Commit Candidate Gate）
| マイルストーン / step | クロージャ状態（closure state） | コミット候補 / コミット範囲（commit candidate / scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S00 / M0 | committed | baseline ledger commit | `ac67751b7b32297be88196cb0825d307518f6ae2` | `git status --short` -> clean | N/A | N/A | N/A | S00-R2 fresh code-reviewer pass、required evidence、commit、cleanを確認しResult Approval |
| S01 / M1a | committed | classifier / marker config commit | `392b5bb9d4869419179fc6d53a6e29a8c36b921a` | `git status --short` -> clean | N/A | N/A | N/A | S01-R1 fresh pass、required verification、commit、cleanを確認しResult Approval |

#### 変更したファイル
- `path/to/file1` - ...
- `path/to/file2` - ...

#### コミット
- `ac67751b7b32297be88196cb0825d307518f6ae2` `test(test-lanes): 実装前テスト基準を固定`
- `392b5bb9d4869419179fc6d53a6e29a8c36b921a` `test(test-lanes): pytestテストレーン分類を追加`

#### メモ
- ...

---

### セッションログ（2026-07-28 23:55 - 2026-07-29 00:05 JST）

#### 対象
- Step: S01 Classifier / pytest marker config
- AC/EC: AC-001、AC-002、AC-006、AC-007、BH-001、BH-002
- 計画上の出典:
  - `plan.md` section: `S01 Classifier / pytest marker config`
  - concrete tests: `tc-s01-001`〜`tc-s01-004`

#### 実施内容
- `dev-coder`が`tests/unit/test_provider_test_lanes.py`へobservable classifier contractをRed-firstで追加した。
- bounded `utility-worker`が`pyproject.toml`へstrict markersと`fast` / `full_regression` registryだけを追加した。
- `dev-coder`が`tests/conftest.py`へpartial-safe exactly-one classifierを実装し、required-fast、heavy prefixes、explicit conflict / forbidden override、early marker visibilityをGreenにした。

#### Red / Green / verification

```text
Red:
uv run pytest -q -p no:cacheprovider \
  tests/unit/test_provider_test_lanes.py::test_focused_collection_does_not_require_global_inventory
-> exit 1; S01 classifier is missing: tests/conftest.py

Green:
same command
-> 1 passed in 0.09s

uv run pytest -q -p no:cacheprovider tests/unit/test_provider_test_lanes.py
-> 5 passed in 1.46s

required-fast exact 7 nodes
-> 7 passed in 1.94s

root collect-only
-> C=2701
-m fast
-> F=666, H deselected=2035
-m full_regression
-> H=2035, F deselected=666

uv run ruff check tests/conftest.py tests/unit/test_provider_test_lanes.py
-> All checks passed
uv run ruff format --check tests/conftest.py tests/unit/test_provider_test_lanes.py
-> 2 files already formatted
git diff --check
-> exit 0
```

#### Refactor / tidy

- classificationは単一hookに限定し、global completeness verifierはcontract test側に保持した。
- S02の`--run-full-regression`、conditional policy skip、permission処理は追加していない。
- dependency、Make target、default `-m fast`、workflow/docs変更はない。

---

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| docs / templates / README / workflow / skill / migration notes | yes / no | doc-writer / N/A | ... | pass / fail / blocked |

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

<!-- spec-dock:managed-section begin id="report.step-evidence" -->
## Step Evidence
- Record Red, Green, and refactor evidence for each executed step.
- Link each closure id to its observed verification result.
<!-- spec-dock:managed-section end id="report.step-evidence" -->
