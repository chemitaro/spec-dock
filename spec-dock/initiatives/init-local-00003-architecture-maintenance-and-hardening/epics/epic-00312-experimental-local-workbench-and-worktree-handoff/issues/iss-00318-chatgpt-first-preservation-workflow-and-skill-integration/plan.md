---
種別: 実装計画書（Issue）
ID: "iss-00318"
タイトル: "ChatGPT First Preservation Workflow And Skill Integration"
関連GitHub: ["#318"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-14"
依存: ["requirement.md", "design.md"]
親: ["epic-00312", "init-local-00003"]
authorized_profile: "standard"
---

# iss-00318 ChatGPT First Preservation Workflow And Skill Integration — Issue 実装計画書（Standard / TDD）

## 0. 文書の位置づけ

本書は、fresh reviewを通過した `requirement.md` と承認済み `design.md` を、順番に一つずつ実行・検証・review・commitできるstepへ変換する。ChatGPT 5.6 Proが一括生成したrequirement/design/plan候補とfresh implementation-plannerの分析はevidenceとして利用するが、runtime authority、親Epic、accepted ADR、Issue317と一致する内容だけを採用する。

実行中の観測結果、Red / Green / refactor guardrail、reviewer verdict、commit hash、逸脱は `report.md` に記録する。本書は観測済みpassを先取りせず、Issue319が所有するpublic rollout、full/global quality、最終PRを引き取らない。

## 1. 実行開始条件

- [x] `requirement.md` はPLANNING-REQ-r13でfresh `spec-reviewer` pass。
- [x] `design.md` はPLANNING-DES-r3でfresh `spec-reviewer` pass、state approved。
- [x] `.assurance.json` はruntimeが生成し、`authorized_profile=standard`、`assurance verify` valid。
- [x] Product / designのblocking open questionはない。
- [x] Issue317の`artifact import chatgpt-output` runtime、accepted ADR、Issue319 relayを確認済み。
- [x] ChatGPT 5.6 Pro complete received answerはrewrite前にArtifactへ保存済み。
- [x] 本planがPLANNING-PLAN-r3でfresh `spec-reviewer` passした。
- [x] Approved planを再bindしたassuranceとexecution guidanceが`ready` / `execute-approved-plan`を返す。

Plan reviewとassurance verificationが通るまでS00を開始しない。Profileは手編集・自己宣言せず、`.assurance.json`をauthorityとする。

## 2. 実装戦略

```text
Pre-S00 plan review / assurance
  -> S00 baseline inventory
  -> S01 provider workflow/reference contract
  -> S02 shared preservation kernel
  -> S03 thin planning-skill hooks
  -> S04 dogfood projection and automated contract verification
  -> S05 manual four-branch dogfood evidence
  -> S90 docs impact / Issue319 relay closure
  -> S99 final Issue quality gates and finish
```

- Provider-first: 恒久変更はprovider authorityを先に編集し、dogfood counterpartへexact projectionする。
- One step at a time: 各stepをreview・commitしてから次へ進む。複数stepを同時に実装しない。
- Single semantic owner: 四分岐matrixはshared skillだけが所有し、planning skillsへ複製しない。
- Contract-first TDD: 文書・skillのsemantic contractを先に固定し、S04でその契約を壊すと失敗するtestを追加する。
- No runtime expansion: Issue317 runtime source、Artifact grammar、ZIP safety runtime、delegated-authoring runtimeを変更しない。
- Report with step: reviewer evidenceと観測結果は対象変更と同じstep/commitでreportへ残す。

## 3. 変更範囲

### 3.1 許可変更面

Provider docs:

- `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
- `src/spec_dock/assets/spec_dock/docs/workflow_chatgpt_authoring_pack.md`
- `src/spec_dock/assets/spec_dock/docs/authoring/chatgpt-pack.md`

Provider skills:

- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`

Matching dogfood projection:

- `spec-dock/docs/workflow_spec_authoring.md`
- `spec-dock/docs/workflow_chatgpt_authoring_pack.md`
- `spec-dock/docs/authoring/chatgpt-pack.md`
- `.agents/skills/spec-dock-chatgpt-authoring/SKILL.md`
- `.agents/skills/spec-dock-initiative-planning/SKILL.md`
- `.agents/skills/spec-dock-epic-planning/SKILL.md`
- `.agents/skills/spec-dock-issue-planning/SKILL.md`

Focused testsは既存の次のsurfaceを優先し、必要な最小fileだけを追加・変更する。

- `tests/cli_runtime/test_wrappers.py`
- `tests/unit/infra/test_init_update.py`
- `tests/cli_runtime/test_artifact_import_chatgpt_output.py`
- `tests/manual_tests/test_review_chatgpt_authoring_pack.py`

Issue318で変更可能なtest fileは上記4件に限定する。契約を上記へ安全に追加できない場合は新規test fileを作らず、plan amendmentとfresh reviewを行う。

Active Issueでは `.assurance.json`、`report.md`、必要なplanning amendment、safe synthetic Workbench/Artifact evidenceを更新できる。

### 3.2 禁止変更

- Issue317のparser、application、publisher、presentation、Artifact allocator。
- Artifact rules/templates、typed catalog、frontmatter、sidecar、index。
- ZIP/tree review/quarantine/stage runtimeとdelegated-authoring diff guard runtime。
- Automatic capture/import、automatic EAL/canonical/assurance mutation。
- Root `README.md`、public guide/reference naming、migration/release docs。
- Package data、fresh init/updateの最終matrix、full/global regression repair。
- Issue319 canonical node、per-Issue PR、final Epic PR。
- EAL/reportへのbody、secret-like value、absolute host pathの記録。

禁止面の変更が必要になった場合は実装を止め、plan amendmentとscope reviewを先に行う。

## 4. 仕様固定クロージャ索引

| ID | Spec | 固定期待 | 主な欠陥 | Evidence | Owner |
|---|---|---|---|---|---|
| C318-01 | AC-318-001 | Complete standalone fileをrewrite前に`imported_byte_exact`で保存 | 原文消失、late preservation | contract + manual | S01/S02/S05 |
| C318-02 | AC-318-002 | Complete received inline textを無編集captureし`captured_received_text` | provider byte identityの誤主張 | contract + manual | S01/S02/S05 |
| C318-03 | AC-318-003 | Genuine unavailableだけ`skipped_inline_unavailable`、path/hash/bytesなし | fabricated provenance、gate bypass | contract + manual | S01/S02/S05 |
| C318-04 | AC-318-004 | ZIP/treeはexisting safe lane、single-file importへ流さない | unsafe ZIP bypass | characterization | S00/S01/S02/S04/S05 |
| C318-05 | AC-318-005 | `committed=false`/receipt欠落/未分類はblock、committed warningは記録してretryなし | adoption before preservation、duplicate import | red-required + manual | S02/S04/S05 |
| C318-06 | AC-318-006 | External evidenceとdelegated draftを分離しexisting guardを維持 | provenance conflation | contract + regression | S01/S04 |
| C318-07 | AC-318-007 | EALはcontent-freeで全receipt/採否fieldを持ちself-claimしない | privacy/authority leak | red-required + inspection | S01–S05 |
| C318-08 | AC-318-008 | Matrixはshared skill一箇所、三planning skillはthin hook | policy drift、重複 | structural contract | S02/S03/S04 |
| C318-09 | AC-318-009 | 7 provider/dogfood pairのexact projectionとfocused installed contract | managed asset divergence | red-required | S04 |
| C318-10 | AC-318-010 | Import/validate/sync/ADR/ZIP/delegated runtime非回帰、runtime source意味diffなし | runtime regression | characterization | S00/S04/S99 |
| C318-11 | AC-318-011 | Issue319 relay、no per-Issue PR、merge-prepared未主張 | delivery ownership loss | inspection + manual | S90/S99 |

全C318-01–11がreportのtest/review/manual evidenceへ追跡でき、unresolved `blocked` / `stale`を持たないことがIssue finish条件である。

## 5. 共通委任契約

### 5.1 Source of truth

- Reviewed Issue requirement / design / plan。
- Parent Epic requirement / design / planとaccepted ADR。
- Issue317 approved requirement / design / reportとcurrent runtime。
- Provider authorityは`src/spec_dock/assets/`、dogfoodはprojection確認面。

### 5.2 Roleとmodel

- 恒久docs/skills: `doc-writer`。
- Source/tests/projection: `dev-coder`、`gpt-5.6-sol`、reasoning `medium`。
- Spec review: fresh `spec-reviewer`、`gpt-5.6-sol`、reasoning `medium`。
- Code review: fresh `code-reviewer`、`gpt-5.6-sol`、reasoning `medium`。
- QA review: fresh `qa-reviewer`、`gpt-5.6-sol`、reasoning `medium`。
- SpecDock command/lifecycle: `spec-manager`。
- Commit/push: `utility-worker`。
- Main orchestratorはEAL disposition、canonical Issue docs、manual checkpoint、role coordinationを所有する。

### 5.3 全role共通禁止事項

- Closure expectation、親boundary、authorized profileの変更。
- Scope外file、automatic behavior、new runtime/schemaの追加。
- Body/secret/absolute pathのreport記載。
- Canonical adoption、reviewer pass、execution/finish/PR readinessのself-claim。
- 実行していないtestやreviewのpass記録。

### 5.4 必須出力と停止条件

各実装roleはchanged files、Redまたは代替evidence、Green verification、diff/refactor guardrail、unresolved risk、report用Ledger Noteを返す。次の場合は即停止する。

- Requirement/design/planのgapまたは相互矛盾。
- Runtime source、ZIP safety、delegated runtime、automatic behaviorが必要。
- Privacy/security classification、new storage grammar、Issue319 ownership変更が必要。
- Existing regressionまたはunknown Red。
- Scope外の変更なしにGreenへできない。

各stepはfresh reviewer pass後だけfocused commitし、commit後clean、push後upstream left/right `0 0`を確認する。

## 6. TDD / evidence方針

| Surface | Red分類 | Red / 代替証跡 | Green |
|---|---|---|---|
| S00 baseline | covered-existing | 現行contractとtestの観測 | baseline結果をreportへ固定 |
| Provider docs | inspect-only | 現行文書に四分岐・三lane・checkpointがないこと | semantic checklistとfresh spec review |
| Shared skill | inspect-only | 新status/branch/single-owner契約を構造点検 | structural inspection + fresh spec review。Automated assertionはS04 |
| Planning hooks | inspect-only | shared checkpoint参照の欠落を構造点検 | three callersのthin hook inspection。Automated assertionはS04 |
| Projection | red-required | provider変更後dogfood hash/byte mismatch | 7/7 byte equality |
| Runtime compatibility | covered-existing | Issue317/ZIP/delegated existing tests | focused regression pass |
| Four-branch dogfood | manual-required | safe synthetic scenarioの事前期待を記録 | receipt/exception/route/blockを観測 |

Redを作らない文書編集では、実装前gap inventoryをRed代替証跡とする。Test追加時は、そのtestが対象実装前またはprojection前に意図した理由で失敗することを確認する。無関係な既存failureは修正せず停止・分類する。

## 7. Step計画

### S00 — Baseline and contract inventory

Goal: 現行docs/skills/test surface、7 provider/dogfood pair、Issue317 runtime境界を変更前に固定する。

Owner: Main orchestrator。必要ならread-only `repo-analyst`へ調査だけを委任する。

Delegation contract:

- Input docs: approved requirement/design、本plan、Issue317 report、対象7 provider/dogfood pair、4 focused tests。
- Allowed paths: active Issue `report.md`だけ。Read-only調査対象は§3.1のprovider/dogfood/test paths。
- Forbidden changes: provider/dogfood/tests/runtime/assurance、baseline failureの修正。
- Acceptance: gap inventory、7 pair baseline、Issue317/ZIP baseline、runtime non-diffが観測済み。
- Verification/reviewer focus: exact command/result/pathをinspectionし、report-only diffはfresh `spec-reviewer`がscopeと事実性を確認。
- Output: command、exit status、pair結果、unexpected regression、Ledger Noteまたはno material decision。
- Report destination: `report.md`の`Implementation Delegation Gate`、`Step Evidence / S00`、`Step Contract Closure`、`Test Contract Closure`、`Closure Coverage`、`Closure Delta`、`Reviewer Gate Status`、`Milestone / Commit Candidate Gate`。
- Refactor guardrail: read-only結果を要約する以外の整理・renamingをしない。
- Amendment trigger: Existing regression、対象path不在、provider/dogfood baselineの説明不能なdrift。

Actions:

1. 対象docs/skillsで`imported_byte_exact`、`captured_received_text`、`skipped_inline_unavailable`、preservation checkpointを検索する。
2. 7 provider/dogfood pairのbaseline hash/byte equalityを記録する。
3. `uv run pytest tests/cli_runtime/test_artifact_import_chatgpt_output.py`と`uv run pytest tests/manual_tests/test_review_chatgpt_authoring_pack.py`を実行し、Issue317/ZIP lane baselineを記録する。
4. Runtime implementation surfaceにIssue318由来のmeaning diffがないことを確認する。

#### 具体テストケース一覧

- `tc318-s00-01` gap inventory
  - 前提: Current provider三docs/四skillsが存在する。
  - 操作: 三status、四branch、checkpoint語を7filesへ`rg`する。
  - 期待結果: 実装前gapと既存記述をfile単位で分類できる。
  - 失敗検出: 既存実装を未実装と誤認する、または対象fileを漏らす。
  - 検証方法: `rg`結果と7 path inventoryをreportへ記録。
  - 関連closure: C318-01–08。
- `tc318-s00-02` projection/runtime baseline
  - 前提: 7 provider/dogfood pairとfocused import/ZIP testsが存在する。
  - 操作: Pair byte比較と2 baseline pytest commandを実行する。
  - 期待結果: 7 pairの一致/不一致と既存testのpass/failureを変更前に確定できる。
  - 失敗検出: Pair漏れ、test未実行、既存failureのIssue318起因扱い。
  - 検証方法: `cmp`/hash、pytest exit status、runtime source diff inspection。
  - 関連closure: C318-04、C318-09–10。

Step closure contract:

- C318-01–10のbaseline gapとexisting pass/failureがreportにある。
- Unexpected regressionがない。あればS01へ進まない。
- No source diffならapproved-no-op evidenceを記録し、report-only review/commitを行う。

### S01 — Provider workflow / reference preservation contract

Goal: Provider三docsに三evidence lane、四分岐、checkpoint順序、authority/secrecy boundaryを定義する。

Owner: `doc-writer`。

Allowed: Provider三docsのみ。Skills、dogfood、runtime、public docsは禁止。

Delegation contract:

- Input docs: approved requirement/design/plan、parent DS-004、accepted ADR、Issue317 report、provider三docs。
- Allowed paths: §3.1のProvider docs三件だけ。
- Forbidden changes: skills、dogfood、tests、runtime、public/package docs、existing delegated/ZIP contractの緩和。
- Acceptance: 三lane、四branch、lifecycle order、Main authority、content-free EALが矛盾なく分担される。
- Verification/reviewer focus: semantic checklist、status exactness、cross-doc responsibility、fresh `spec-reviewer`。
- Output: changed files、gap/Green inspection、unresolved risk、Ledger Note。
- Report destination: `report.md`の`Implementation Delegation Gate`、`Step Evidence / S01`、`Step Contract Closure`、`Test Contract Closure`、`Closure Coverage`、`Closure Delta`、`Reviewer Gate Status`、`Milestone / Commit Candidate Gate`、必要時`Decision Ledger`。
- Refactor guardrail: 対象契約周辺だけを編集し、既存authoring policyを再構成しない。
- Amendment trigger: 三docsだけではmatrix owner/authorityを表現不能、またはpublic/runtime変更が必要。

Implementation contract:

- `workflow_spec_authoring.md`: output received → preservation checkpoint → EAL disposition → canonical rewrite → fresh reviewerのlifecycleを持つ。
- `workflow_chatgpt_authoring_pack.md`: standalone MarkdownとZIP/treeのroute、complete inline/unavailable exceptionを区別する。
- `authoring/chatgpt-pack.md`: 三lane、status/capture boundary、content-free EAL fieldとfailure semanticsをreference化する。
- External preserved evidenceへdelegated frontmatter/diff guardを要求せず、existing delegated/ZIP contractを緩めない。
- Main orchestratorがcapture/importと採否を実行し、shared skill/import commandはauthorityをself-claimしない。

#### 具体テストケース一覧

- `tc318-s01-01` lifecycle and four branches
  - 前提: 三provider docsに現行ChatGPT authoring契約がある。
  - 操作: Output受領からfresh reviewまでの順序と四branchを三docsの責任別に点検する。
  - 期待結果: Preservationがadoption/rewrite前で、standalone/inline/unavailable/ZIPが一意にrouteされる。
  - 失敗検出: Late preservation、ZIP single-file import、complete failureのunavailable迂回。
  - 検証方法: Structural inspectionとfresh spec review。
  - 関連closure: C318-01–05。
- `tc318-s01-02` lane/authority/secrecy
  - 前提: Existing delegated draftとZIP safety contractがある。
  - 操作: External lane追加diffをdelegated/ZIP/authority/EAL契約と照合する。
  - 期待結果: Existing guards不変、Mainだけが採否/rewrite、EALはcontent-free。
  - 失敗検出: Frontmatter要求、self-claim、body/secret/absolute path記録。
  - 検証方法: Forbidden-term inspection、`git diff --check`、fresh spec review。
  - 関連closure: C318-06–07。

Verification:

- Terminology/status exact match、lifecycle order、lane separation、forbidden claimsをstructural inspection。
- `git diff --check`。
- Fresh `spec-reviewer`。Material findingはS01内で修正しfresh rerun。

Step closure contract: C318-01–07のplanned observationsが揃い、fresh reviewer pass後にreportとfocused commit/pushする。

### S02 — Shared ChatGPT preservation kernel

Goal: `spec-dock-chatgpt-authoring`へoperational decision matrixを一箇所だけ実装する。

Owner: `doc-writer`。

Allowed: Provider shared skill一件。Planning skills、dogfood、runtimeは禁止。

Delegation contract:

- Input docs: approved requirement/design/plan、S01 reviewed provider docs、shared skill現行本文。
- Allowed paths: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md`だけ。
- Forbidden changes: planning/manual skills、dogfood、tests、runtime、EAL/canonical実書込み。
- Acceptance: Pre-classification、四branch、三status、import result matrix、stop/self-claim restrictionを一箇所で所有する。
- Verification/reviewer focus: Exact token、branch completeness、Main実行主体、single owner、fresh `spec-reviewer`。
- Output: changed file、inspection結果、S04へ渡すassertion seed、Ledger Note。
- Report destination: `report.md`の`Implementation Delegation Gate`、`Step Evidence / S02`、`Step Contract Closure`、`Test Contract Closure`、`Closure Coverage`、`Closure Delta`、`Reviewer Gate Status`、`Milestone / Commit Candidate Gate`。
- Refactor guardrail: Existing GitHub/local-context/ZIP workflowを移動・再構成せず、checkpointを最小追加する。
- Amendment trigger: Runtime automation、新status/schema、planning skillへのmatrix複製が必要。

Required branches:

1. Complete standalone: Workbench source確認→explicit import→receipt検証→`imported_byte_exact`。
2. Complete inline: complete received answerだけを無編集capture→explicit import→`captured_received_text`。Provider original bytes claim禁止。
3. Genuine unavailable inline: `skipped_inline_unavailable`、reason/owner/nonblocking/next action、path/hash/bytesなし。
4. ZIP/tree: existing review/quarantine/stage laneへrouteしsingle-file importを案内しない。

Import result matrix:

- `committed=true` + complete receipt + no warning: pass。
- `committed=true` + complete receipt + warning: pass-with-warning、warning記録、自動retryなし。
- `committed=false`、receipt欠落、eligibility failure、semantic completeness未分類: block。
- Failureをunavailableへ読み替えない。

Skillはcontractとevidence評価だけを提供し、import/EAL/canonical rewriteを代行しない。

#### 具体テストケース一覧

- `tc318-s02-01` complete source branches
  - 前提: Complete standaloneまたはcomplete received inline textがある。
  - 操作: Shared contractの分類、明示import、receipt評価、claim boundaryを追跡する。
  - 期待結果: Standaloneは`imported_byte_exact`、inlineは`captured_received_text`となる。
  - 失敗検出: Provider-original claim、capture整形、canonical rewrite先行。
  - 検証方法: Skill structural inspectionとS04 assertion seed。
  - 関連closure: C318-01–02、C318-07–08。
- `tc318-s02-02` unavailable/ZIP/failure matrix
  - 前提: Genuine unavailable、ZIP/tree、committed warning/failureの各入力がある。
  - 操作: Branchとresult matrixを契約表に照合する。
  - 期待結果: Unavailableだけexception、ZIPはexisting lane、warningは記録/no retry、failureはblock。
  - 失敗検出: Failure迂回、receipt欠落pass、自動retry、ZIP import。
  - 検証方法: Exact status/stop condition inspection、fresh spec review。
  - 関連closure: C318-03–05、C318-08。

Verification:

- Status、branch、stop condition、content-free required output、forbidden self-claimをinspection。
- 既存testへ最小のstructural assertionを先行追加できる場合はRed→Green。そうでなければS04でtest化する旨をreportへ記録。
- `git diff --check`、fresh `spec-reviewer`。

Step closure contract: C318-01–05、C318-07–08のshared-kernel obligationが揃い、fresh reviewer pass後にreportとfocused commit/pushする。

### S03 — Thin planning-skill integration

Goal: Initiative / Epic / Issue planning skillが同じshared checkpointを正しい時点で呼び、scope固有authorityを維持する。

Owner: `doc-writer`。

Allowed: Provider planning skills三件。Shared skill、manual skills、dogfood、runtimeは禁止。

Delegation contract:

- Input docs: approved requirement/design/plan、reviewed S02 shared skill、三planning skills。
- Allowed paths: §3.1のProvider planning skills三件だけ。
- Forbidden changes: shared/manual skills、dogfood、tests、runtime、matrix/status表のlocal copy。
- Acceptance: 三callerが同じcheckpointをoutput受領後・adoption/rewrite前に呼び、scope authorityとblock propagationを維持する。
- Verification/reviewer focus: Invocation placement、thinness、scope ownership、fresh `spec-reviewer`。
- Output: changed files、three-caller comparison、duplicate scan、Ledger Note。
- Report destination: `report.md`の`Implementation Delegation Gate`、`Step Evidence / S03`、`Step Contract Closure`、`Test Contract Closure`、`Closure Coverage`、`Closure Delta`、`Reviewer Gate Status`、`Milestone / Commit Candidate Gate`。
- Refactor guardrail: 既存planning operating spineを移動せず、共通呼出しを最小追加する。
- Amendment trigger: Shared skill contract不足、callerごとの異なるmatrixが必要、scope ownership変更が必要。

Contract:

- ChatGPT output受領後、claim review / EAL disposition / canonical rewrite前にshared preservation checkpointを呼ぶ。
- Shared checkpointがblockedならcanonical rewriteへ進まない。
- `skipped_inline_unavailable`はreason/owner/nonblocking/next actionの確認後だけ進める。
- 四branch/status/result matrix本文をplanning skillsへ複製しない。
- InitiativeはInitiative docsとEpic approval、EpicはEpic docsとIssue split/approval、IssueはIssue docsとexecution handoffを所有する既存境界を維持する。

#### 具体テストケース一覧

- `tc318-s03-01` invocation placement and block propagation
  - 前提: 三planning skillsがChatGPT outputとcanonical rewriteを扱う。
  - 操作: 各operating spineでshared checkpoint呼出し前後を比較する。
  - 期待結果: Output受領後・adoption/rewrite前に呼び、blocked resultで停止する。
  - 失敗検出: Late call、checkpoint bypass、unavailable理由なしの続行。
  - 検証方法: Three-file structural comparison、fresh spec review。
  - 関連closure: C318-03、C318-05、C318-08。
- `tc318-s03-02` thin caller and scope authority
  - 前提: Shared skillがmatrix authorityを持つ。
  - 操作: 三callerのbranch/status語とscope-specific handoffを比較する。
  - 期待結果: Matrix複製なしでInitiative/Epic/Issue固有authorityだけが残る。
  - 失敗検出: Four-branch local table、scope approval/handoffの消失、self-claim。
  - 検証方法: Duplicate scan、scope checklist、`git diff --check`。
  - 関連closure: C318-07–08。

Verification:

- 三skillのinvocation placement、explicit shared reference、matrix non-duplication、scope ownership、stop propagationをinspection。
- `git diff --check`、fresh `spec-reviewer`。

Step closure contract: C318-03、C318-05、C318-07–08のcaller-integration obligationが揃い、fresh reviewer pass後にreportとfocused commit/pushする。

### S04 — Dogfood projection and automated contract verification

Goal: Providerの7変更をdogfoodへexact projectionし、installed/wrapper/compatibility contractを自動検証する。

Owner: `dev-coder`（`gpt-5.6-sol` / medium）。

Delegation contract:

- Input docs: approved requirement/design/plan、reviewed S01–S03 provider assets、matching dogfood七files、4 focused tests。
- Allowed paths: §3.1のmatching dogfood七filesと4 existing test filesだけ。
- Forbidden changes: Provider semantics、Issue317/runtime source、Artifact/ZIP/delegated runtime、public/package docs、新規test file。
- Acceptance: 7/7 exact projection、contract-sensitive assertions、focused import/ZIP non-regression、runtime source meaning non-diff。
- Verification/reviewer focus: `code-reviewer`はtest sensitivity/projection/scope、`spec-reviewer`はtext alignment/single ownerを確認。
- Output: changed files、Red/alternative、Green commands、7 pair compare、runtime non-diff、Ledger Note。
- Report destination: `report.md`の`Implementation Delegation Gate`、`Step Evidence / S04`、`Step Contract Closure`、`Test Contract Closure`、`Closure Coverage`、`Closure Delta`、`Reviewer Gate Status`、`Milestone / Commit Candidate Gate`。
- Refactor guardrail: Test helper追加は4files内の再利用が明白な最小範囲だけ。Provider textをtest都合で変更しない。
- Amendment trigger: 4files外のtest、runtime/provider修正、new fixture/module、Issue319 surfaceが必要。

TDD order:

1. Existing test patternを読み、shared status/branch、checkpoint-before-rewrite、ZIP route、no self-claims、thin caller referenceを検出する最小assertionを追加する。
2. 実装/projection前または意図的に壊したfixtureで、期待理由によるRedを確認する。困難ならS00 gap + provider/dogfood mismatchをRed代替証跡として明示する。
3. Provider七filesをdogfood counterpartへ機械的に投影し、7/7 byte equalityを確認する。
4. Focused testsをGreenにする。Testを通すためprovider contractを再設計しない。
5. Runtime import source、ZIP/delegated runtimeにmeaning diffがないことを確認する。

#### 具体テストケース一覧

- `tc318-s04-01` installed preservation contract
  - 前提: S01–S03 provider変更がありdogfoodは未投影またはtest assertionが未追加。
  - 操作: Existing wrapper/init-update testへ三status、checkpoint-before-rewrite、ZIP route、no self-claim、thin caller assertionを追加する。
  - 期待結果: 実装/projection欠落時は期待理由でRed、7files投影後はGreen。
  - 失敗検出: 単なる語の一件存在だけでmatrix欠落やcaller duplicationを見逃す。
  - 検証方法: `tests/cli_runtime/test_wrappers.py`と`tests/unit/infra/test_init_update.py`。
  - 関連closure: C318-01–09。
- `tc318-s04-02` provider/dogfood identity
  - 前提: Provider七filesのreview済み変更がある。
  - 操作: 対応dogfood七filesへ投影し各pairをbyte比較する。
  - 期待結果: 7/7一致し、dogfood-only semantic editがない。
  - 失敗検出: Pair漏れ、partial projection、dogfood側の独自修正。
  - 検証方法: `cmp`またはSHA-256 pair list。
  - 関連closure: C318-09。
- `tc318-s04-03` runtime and ZIP non-regression
  - 前提: Issue317 importとauthoring-pack testがbaseline passしている。
  - 操作: Import/ZIP focused testsを再実行しruntime source diffを確認する。
  - 期待結果: Byte preservation/blank coexistence/content-free receiptとZIP safetyがpassしruntime meaning diffなし。
  - 失敗検出: Workflow変更によるruntime/ZIP回帰、scope外source edit。
  - 検証方法: 残り2 pytest command、`git diff --name-only`/review。
  - 関連closure: C318-04、C318-06、C318-10。

Required checks:

```bash
uv run pytest tests/cli_runtime/test_wrappers.py
uv run pytest tests/unit/infra/test_init_update.py
uv run pytest tests/cli_runtime/test_artifact_import_chatgpt_output.py
uv run pytest tests/manual_tests/test_review_chatgpt_authoring_pack.py
git diff --check
```

Repository-wide `uv run mypy src`はIssue319のfull/global quality gateへrelayし、Issue318ではblocking checkにしない。必要なら観測だけを行い、failureをIssue318で修正しない。

Review order:

1. Fresh `code-reviewer`: test sensitivity、projection、runtime non-diff、scope。
2. Fresh `spec-reviewer`: provider/dogfood textとrequirement/design alignment。

Step closure contract: C318-04、C318-06、C318-08–10のprojection/test obligationが揃い、code/spec両review pass後にreportとfocused commit/pushする。

### S05 — Manual four-branch dogfood evidence

Goal: Safe synthetic outputで四branchとfailure gateを観測し、preservationの後にだけEAL/canonical adoptionへ進めることを確認する。

Owner: Main orchestrator。Runtime/skill source変更なし。Synthetic Markdownにsecret/real user contentを含めない。

Delegation contract:

- Input docs: approved requirement/design/plan、reviewed S01–S04 assets/tests、Issue317 import command contract。
- Allowed paths: active Issue `.workbench/issue318-s05-standalone.md`、`.workbench/issue318-s05-inline.md`、`artifacts/<timestamp>[-<nn>]-chatgpt-output-issue-318-s05-{standalone,inline}.md`の最大2files、active Issue `report.md`。Workbenchはignored source。
- Forbidden changes: Provider/dogfood/tests/runtime、既存Artifact、canonical requirement/design/plan、real/private output。
- Acceptance: Standalone/inline/unavailable/ZIP/failureの5scenarioが期待どおり観測され、成功2件だけがsafe Artifactになる。
- Verification/reviewer focus: Source survival/hash/cmp、exception field absence、ZIP route、failure block、content-free EALをfresh `spec-reviewer`が確認。
- Output: Content-free receipt metadata、command/exit status、scenario result、Ledger Note。
- Report destination: `report.md`の`Implementation Delegation Gate`、`Step Evidence / S05`、`External Preserved Evidence`、`Evidence Adoption Ledger`、`Step Contract Closure`、`Test Contract Closure`、`Closure Coverage`、`Closure Delta`、`Reviewer Gate Status`、`Milestone / Commit Candidate Gate`。
- Refactor guardrail: Synthetic bodyをcanonicalへ採用せず、Workbench sourceをGit追加しない。Artifactは自動削除しない。
- Amendment trigger: Safe synthetic inputだけでscenarioを作れない、runtime/source変更が必要、destination pattern外へ出力される。

Scenarios:

- Standalone: Issue Workbenchのcomplete `.md`をimportし、source survival、hash/bytes一致、`imported_byte_exact`を記録。
- Inline: Safe complete inline stringを無編集capture/importし、capture fileとArtifactのbyte一致、`captured_received_text`、provider byte identity非主張を記録。
- Unavailable: Complete sourceが存在しないsynthetic caseで、`skipped_inline_unavailable`、reason/owner/nonblocking/next actionを記録し、path/hash/bytesを記録しない。
- ZIP/tree: Existing safe ZIP fixtureのreview/stage evidenceを確認し、single-file import destinationが作られていないことを記録。
- Failure: Safe eligibility failureまたは既存fault-injected `committed=false` evidenceで、canonical target未変更とunavailable迂回禁止を確認。

#### 具体テストケース一覧

- `tc318-s05-01` standalone and inline preservation
  - 前提: 上記exact Workbench source二件にsafe complete Markdownを置く。
  - 操作: 各sourceを明示importし、receipt/source/destinationを比較する。
  - 期待結果: 最大2 Artifactが作られ、source survives、hash/bytes/cmp一致、status境界が正しい。
  - 失敗検出: Move、byte差異、provider-original claim、unexpected destination。
  - 検証方法: Import JSON、`sha256`、`wc -c`、`cmp`、repo-relative path inspection。
  - 関連closure: C318-01–02、C318-07、C318-11。
- `tc318-s05-02` unavailable and failure gate
  - 前提: Complete sourceが存在しないsynthetic unavailable caseとsafe eligibility failure caseを定義する。
  - 操作: Exception recordとfailed import outcomeを評価する。
  - 期待結果: Unavailable recordはpath/hash/bytesなし、failureはrewrite/adoption blockで再分類なし。
  - 失敗検出: Fabricated receipt、failureのskip化、canonical target mutation。
  - 検証方法: Report field inspection、before/after canonical hash。
  - 関連closure: C318-03、C318-05、C318-07。
- `tc318-s05-03` ZIP existing lane
  - 前提: Existing safe ZIP fixture/review commandがある。
  - 操作: Existing review/stage evidenceを確認しsingle-file import destinationを探索する。
  - 期待結果: ZIP safety laneだけが使われ、S05 import Artifactは作られない。
  - 失敗検出: ZIP contentのsingle-file import、safety bypass。
  - 検証方法: Existing command/test evidenceとArtifact inventory。
  - 関連closure: C318-04。

EAL成功recordはoutput form、preservation status、capture boundary、`import_kind=chatgpt-output`、`storage_identity=blank`、repo-relative source/destination、SHA-256、byte count、committed/warning、exact adoption status、rationale、adopter、reviewer status、blocking、next actionを持つ。Body/secret/absolute pathは持たない。

Verification: Receipt、`sha256`、`cmp`、source survival、exception fields、ZIP routeを直接確認し、fresh `spec-reviewer`を通す。

Step closure contract: C318-01–05、C318-07、C318-11のmanual observationが揃い、fresh reviewer pass後にsafe Artifact/reportだけをfocused commit/pushする。Ignored Workbench sourceはGit管理しない。

### S90 — Docs impact and Issue319 ownership closure

Goal: 全影響pathをupdate / approved-no-op / deferへ分類し、Issue318と319の境界を閉じる。

Owner: Main orchestrator。Path inventoryのread-only確認だけを`repo-analyst`へ委任できる。

Delegation contract:

- Input docs: approved requirement/design/plan、S00–S05 evidence、Issue317 report、parent W4/W5、Issue319 node。
- Allowed paths: active Issue `report.md`だけ。Read-only inventoryは§3.1 paths、root/public/package/runtime paths。
- Forbidden changes: Provider/dogfood/tests、Issue319 docs、public/package/runtime、planning docs。
- Acceptance: 影響実pathごとにupdate/no-op/defer、owner、reason、dependency、blockingを持ち、Issue319 relayが閉じる。
- Verification/reviewer focus: Grouped wildcard漏れ、scope移送、merge-ready self-claimをfresh `spec-reviewer`が確認。
- Output: Exact path disposition、unresolved risk、Ledger Noteまたはno material decision。
- Report destination: `report.md`の`Implementation Delegation Gate`、`Step Evidence / S90`、`Step Contract Closure`、`Test Contract Closure`、`Closure Coverage`、`Closure Delta`、`Deferred PR Delivery Gate`、`Decision Ledger`、`Reviewer Gate Status`、`Milestone / Commit Candidate Gate`。
- Refactor guardrail: Inventory以外の文書再編やdeferred surfaceの先行編集をしない。
- Amendment trigger: Issue318完了にIssue319-owned changeが必要、または新しいblocking impact pathを発見。

| Surface | Disposition |
|---|---|
| Provider workflow三docs | Issue318 update |
| Provider四skills | Issue318 update |
| Matching dogfood七files | Issue318 exact projection |
| Focused wrapper/managed-asset tests | Issue318 update |
| Artifact rules/templates | approved-no-op |
| Runtime import source | approved-no-op |
| ZIP/delegated runtime | approved-no-op |
| Root README / guide / reference naming | defer Issue319 |
| Migration / release docs | defer Issue319 |
| Package/fresh init/update final matrix | defer Issue319 |
| Full pytest/global static repair | defer Issue319 |
| Final Epic PR/observation | defer Issue319 |

#### 具体テストケース一覧

- `tc318-s90-01` exact impact disposition
  - 前提: S00–S05のactual changed pathsと親W4/W5 ownershipがある。
  - 操作: Changed/considered pathを実path単位でupdate/no-op/deferへ分類する。
  - 期待結果: 全pathにowner/reason/dependency/blockingがあり、分類漏れがない。
  - 失敗検出: Wildcardだけの分類、runtime/public/packageのIssue318取り込み、owner不明。
  - 検証方法: `git diff --name-only`、planned inventory、fresh spec review。
  - 関連closure: C318-10–11。
- `tc318-s90-02` Issue319 relay boundary
  - 前提: Issue319がpublic/package/full/global/final PRを所有する。
  - 操作: Deferred PR Delivery Gateをparent planとIssue317 relayへ照合する。
  - 期待結果: Remaining gates/revisit conditionが具体的で、Issue318はPR readinessを主張しない。
  - 失敗検出: Relay漏れ、Issue319の重複実装、per-Issue PR claim。
  - 検証方法: Cross-document inspectionとfresh spec review。
  - 関連closure: C318-11。

全実pathにowner、reason、dependency、blocking/nonblocking根拠をreportへ残す。Grouped wildcardだけで閉じない。Fresh `spec-reviewer`がIssue318/319境界を確認し、updateがあればreview/commit、no-op/deferは根拠付きで記録する。

Step closure contract: C318-10–11のexact dispositionとIssue319 relayがfresh reviewer passする。Report-only/approved-no-opの場合もS90専用commitを作成し、post-commit cleanとupstream 0/0を記録する。S90のResult Approvalとcommit完了前にS99へ進まない。

### S99 — Final Issue quality gates and finish

Owner: Main orchestrator。Commands/lifecycleは`spec-manager`、reviewはfresh QA→code→spec、commit/pushは`utility-worker`へ委任する。

Delegation contract:

- Input docs: approved requirement/design/plan、completed S00–S90 report、current diff/commits、assurance/lifecycle state。
- Allowed paths: active Issue `report.md`、`.assurance.json`、review findingが要求する場合は元owner stepの明示allowed pathsだけ。Lifecycle/commit metadataは通常commandで更新する。
- Forbidden changes: New implementation、scope外remediation、Issue319/public/package/runtime、per-Issue PR。Finding修正をS99へ直接混在させない。
- Acceptance: Focused checks pass、C318-01–11 closed、QA→code→spec passed、assurance valid、finish/clean/upstream evidence完了。
- Verification/reviewer focus: QAはcoverage、codeはtest/projection/runtime non-diff、specは全artifact/authority/boundary。
- Output: Exact commands/results、three reviewer verdicts、closure table、commit/clean/upstream/lifecycle evidence。
- Report destination: `report.md`の`Implementation Delegation Gate`、`Step Evidence / S99`、`Step Contract Closure`、`Test Contract Closure`、`Closure Coverage`、`Closure Delta`、`Reviewer Gate Status`、`Milestone / Commit Candidate Gate`、`Final QA Gate`、`Final Code Review Gate`、`Final Spec Review Gate`、`Final Commit`、`Deferred PR Delivery Gate`。
- Refactor guardrail: Final gate中にcleanup/refactorしない。Findingはowning stepへ戻して修正・再review・commitする。
- Amendment trigger: Missing integration obligation、unclosed closure、new scope/architecture decision、Issue319 boundary conflict。

Required verification:

```bash
uv run pytest tests/cli_runtime/test_wrappers.py
uv run pytest tests/unit/infra/test_init_update.py
uv run pytest tests/cli_runtime/test_artifact_import_chatgpt_output.py
uv run pytest tests/manual_tests/test_review_chatgpt_authoring_pack.py
git diff --check

./spec-dock/scripts/spec-dock assurance verify --issue iss-00318 --format json
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock active show
```

`sync`は必要性を判定し、実行した場合は結果、不要ならapproved-no-op根拠をreportへ残す。Issue319が所有するfull `uv run pytest`、repository-wide `uv run mypy src`、global repairを暗黙に引き取らず、owner/dependency/nonblocking relayを記録する。

#### 具体テストケース一覧

- `tc318-s99-01` focused regression and closure
  - 前提: S00–S90がreview/commit済みでworktreeが既知状態。
  - 操作: 4 pytest、diff check、assurance/validate/active commandを順に実行しC318 tableへ結び付ける。
  - 期待結果: Blocking checks pass、C318-01–11にunresolved blocked/staleなし。
  - 失敗検出: Command未実行、結果の先取り、closure evidence欠落、global gateのIssue318取り込み。
  - 検証方法: Exit status/output、closure table、Issue319 relay inspection。
  - 関連closure: C318-01–11。
- `tc318-s99-02` final reviewer and lifecycle order
  - 前提: Focused checks pass、final diff/reportが確定している。
  - 操作: Fresh QA→code→specを順に実行し、全pass後だけcommit/push/issue finishする。
  - 期待結果: Three gates passed、clean、upstream 0/0、#318/local lifecycle complete、PRなし。
  - 失敗検出: Reviewer順序違反、failed finding未修正、finish先行、PR readiness claim。
  - 検証方法: Reviewer records、git/lifecycle command evidence。
  - 関連closure: C318-01–11。

Final reviewer order:

1. Fresh `qa-reviewer`: C318-01–11、manual four-branch、missing integration coverage。
2. Fresh issue-wide `code-reviewer`: test sensitivity、managed projection、runtime non-diff。
3. Fresh `spec-reviewer`: requirement/design/plan/report/docs/skills/tests、親/ADR/Issue317/Issue319境界、EAL/authority/secrecy。

全reviewerは`gpt-5.6-sol` / mediumを使う。いずれかが`failed`、`unavailable`、`denied`、`waived`、`provisional`ならpass扱いせず、owner stepへ戻して修正後fresh rerunする。

Step closure contract / Final gate:

- C318-01–11にunresolved `blocked` / `stale`がない。
- Material findingのdispositionが完了している。
- Assurance valid、Issue report/closure evidenceが完備している。
- Final reportをcommit/pushし、worktree clean、upstream left/right `0 0`。
- Active Issueがiss-00318と一致する。
- Per-Issue PR、PR-ready/merge-ready/merge-prepared claimを作らない。
- Spec-managerが`issue finish`を実行し、GitHub #318/local lifecycleの完了を確認する。

## 8. Deferred PR Delivery Gate

- Target: `iss-00319-installed-runtime-dogfood-parity-final-quality-and-mergeable-pr`。
- Dependency: `iss-00317 -> iss-00318 -> iss-00319`。
- Reason: Package、fresh init/update、public docs、full regression、final Epic QA/code/spec、PR deliveryを一つの最終Epic PRへ集約する。
- Claim boundary: Issue319のPR Delivery / Merge Preparation完了までPR-ready / merge-ready / merge-preparedを主張しない。
- Remaining gates: package data、fresh init/update、README/reference/migration、full pytest/global static、provider/dogfood/installed inventory、final Epic QA/code/spec、PR creation/observation/merge preparation。

## 9. Commit候補

| Step | Commit intent |
|---|---|
| Plan gate | `docs(issue-318): ChatGPT First実装計画を確定` |
| S00 | `docs(issue-318): Preservation契約のベースラインを記録` |
| S01 | `docs(chatgpt-first): 原文保存ワークフロー契約を追加` |
| S02 | `docs(chatgpt-first): 共有preservation checkpointを追加` |
| S03 | `docs(planning): ChatGPT原文保存checkpointを連携` |
| S04 | `test(chatgpt-first): preservation契約と投影を検証` |
| S05 | `docs(issue-318): preservation分岐のdogfood証跡を記録` |
| S90 | `docs(issue-318): Issue319への引継ぎ境界を確定` |
| S99 | `docs(issue-318): 最終品質ゲートを確定` |

実際のdiffが候補と異なる場合はcommit時に変更事実へ合わせる。複数stepを一つのcommitへ混在させない。

## 10. Plan closure checklist

- [x] Fresh plan `spec-reviewer` pass、promotion decision exact `promote`。
- [x] Assurance valid、planning readiness blockerなし。
- [ ] S00 baseline完了。
- [ ] S01 provider docs、fresh spec review、commit/push完了。
- [ ] S02 shared skill、fresh spec review、commit/push完了。
- [ ] S03 planning hooks、fresh spec review、commit/push完了。
- [ ] S04 projection/tests、fresh code/spec review、commit/push完了。
- [ ] S05 four-branch manual evidence、fresh spec review、commit/push完了。
- [ ] S90 impact/Issue319 relay、fresh spec review完了。
- [ ] S99 focused checksとQA→code→spec review完了。
- [ ] Report/assurance/lifecycle/clean/upstream evidence完了。

## 11. 変更履歴

- 2026-07-14: ChatGPT 5.6 Pro bundled planning evidence、fresh implementation-planner、approved requirement/designを統合し、Standard executable planとして作成。
