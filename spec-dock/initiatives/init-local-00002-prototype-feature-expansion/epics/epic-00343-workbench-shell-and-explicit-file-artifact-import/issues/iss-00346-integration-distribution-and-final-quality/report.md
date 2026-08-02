---
種別: 実装報告書（Issue）
ID: "iss-00346"
タイトル: "Integration Distribution And Final Quality"
関連GitHub: ["#346"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-08-02"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00343", "init-local-00002"]
---

# iss-00346 Integration Distribution And Final Quality — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

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
| D-001 | resolved | interpretation | orchestrator | `pre-feature existing consumer`を歴史的revisionに固定すべきか不明瞭 | READMEなしvalid synthetic fixture; historical SHA固定 | 標準はREADMEなしvalid synthetic fixtureとし、歴史的revisionを使う場合だけfeature非搭載の実証とexact SHAを要求する | 親Epic E-AC-004とCandidate 3 verificationは観測対象の状態を規定し、特定revisionを必須化していない | promoted_to_plan | clarification research §4、`requirement.md` I346-ASM-002 / I346-ASM-003 / I346-RQ-004 / I346-AC-004、`design.md` §7.3、`plan.md` S02 | plan fresh reviewでclosureを確認 |
| D-002 | resolved | operation | operator | Luna・Max実装を補助するstep具体化と、sub-agent reviewerに代わるChatGPT Pro reviewのIssue-local運用が未定義 | 既定SpecDock reviewer pathを維持; Issue 346だけChatGPT Proへ置換 | Issue 346では各step開始前にcommit/push済みheadをChatGPT Proで具体化しArtifact保存する。implementation reviewはcurrent reviewer Developer Instructionsを1つのChatGPT threadへ統合する | 2026-08-02 operator instruction。製品要件・設計・ACを変えず、低authority Artifactとcanonical planに実行手続きだけを固定する | promoted_to_plan | `artifacts/20260801t152944z-disc-chatgpt-assisted-execution-agreement.md`; `plan.md` §2.3、各step §x.0、S99 | Issue 346 execution中に適用。他Issue/全体workflowへ波及させない |
| D-003 | resolved | operation | operator / orchestrator | Cheetah指定の品質ゲートとS01前段ChatGPT具体化が、正式wrapperの現行モデル選択・ブラウザ状態で実行可能か未確定 | Cheetahを実行して品質ゲートとする; formal Pro laneで代替; 失敗出力を採用せずローカル証跡を先行 | Cheetahはformal wrapperのdry-runで`gpt-5.2`へ正規化され、品質証跡として使用しない。前段具体化は前景実行へ復旧後にProで取得できたため、S01の補助Artifactを採用する。以前のdetached/incomplete-capture出力と無関係なstale出力は引き続き不採用とする | `plan.md` §2.3のmodel-evidence境界を維持し、モデル名・レビューpassを未確認のまま主張しないため | partially_adopted | `iss346-s01-prestep-aug2e`（`requested=Pro; resolved=Pro; verified=yes`）、Artifact import receipt、過去slugs (`iss346-s01-pre-step`, `iss346-s01-prestep-aug2`, `iss346-s01-followup`, `iss346-s01-prestep-tty`, `iss346-s01-wrapper-smoke`)、Cheetah dry-run、stale `iss00334` harvestの不採用記録 | S01実装をcurrent HEADで再受領し、current-head code reviewを取得する |
| D-004 | resolved | test-strategy | ChatGPT Pro pre-step / orchestrator | current HEADに対して既存S01のwheel receiptがstaleになり、sensitivity evidenceがallowlist missingだけに限定されていた | production/package repair; test-only denylist negative + installed validate; broad inventory/metadata framework | package/installer変更は行わず、allowed test pathだけにforbidden nested README・cache entryのcontrolled negativeとfresh consumer後のinstalled `validate` assertionを追加した。strict clean receiptはcanonical contractどおり維持し、コミット後にcurrent HEADで再実行した | ChatGPT Artifact EAL-005、plan §8.3/§8.5、worker diff、current focused/full test results | applied | `tests/integration/test_epic_00343_distribution.py`; commit `9c721d50eb0e4b2ca5bf16fd6f7e3b0f4a9e1c9c6`; S01 current-cycle test output | current-head ChatGPT Pro implementation reviewでscopeとtest sensitivityを確認する |
| D-005 | resolved | scope / operation | S90 ChatGPT Pro review / orchestrator | S04でaccepted provider runtime sourceがcandidate-wheel disposable consumerへ投影済みだが、チェックイン済みdogfood mirrorが遅れており、S90で同期した4 pathsが「runtime repair」と誤認され得た | revert mirror and accept stale checked-in dogfood; plan amendmentで既存provider差分のmanaged projection correctionを明示; new runtime repair | candidate-wheel updateが実測で出力する既存managed mirrorだけをprovider-firstに同期し、production repair=false・originating step=S04・status manifestを保持する。S90はruntime挙動を変更せず、projection parityとreport traceだけを完了する | S04 `I346-AC-006` / `Provider-to-Dogfood Projection Manifest`、`870846fd`、`6b815c9c`、ChatGPT S90 finding P1-1 | promoted_to_plan | `plan.md` §12.3 clarification、Issue EAL-013、S04 report projection receipt | fresh S90 spec reviewでexact-head scopeを再確認する |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | `adopted` | `research`: Issue 346 source-grounded clarification | `requirement.md`全体、`design.md` fixture/platform boundary、`plan.md` closure boundary | 親Epic、Issue 344/345、accepted ADR、現行testsを照合したIssue-local evidenceであり、追加のowner判断を必要としない | `artifacts/20260730t155742z-research-issue-346-requirement-clarification-source-grounded-synthesis.md`; adopter: main orchestrator; reviewer: fresh `spec-reviewer`; blocking: no | canonical R/D/Pへの反映とphase review完了。実装時は判断D-001を維持 |
| EAL-002 | `partially_adopted` | external ChatGPT Pro github-synced planning evidence | `requirement.md`、`design.md`、`plan.md`、オンボーディングartifact | GitHub planning baseline `2217889c31e1a8a83732c446264dec00dde77be6`を参照した4資料を、ローカルsourceとworkflow contractに照合して採用した。安定ID、scope、scenario、検証観点、説明構造は採用し、候補用frontmatter、evidence-only自己claim、candidate revisionをplanning baselineへ固定する記述、曖昧pathは不採用 | `artifacts/20260730t173917z--specdock-iss-00346-authoring-pack-corrected.zip`; onboarding `artifacts/20260730t182546z-research-issue-346-onboarding-guide-for-new-team-members.md`; pack review `pass`; tree SHA-256 `7b01a12ac95b13bcfdf4a3a60774d16c3dc666d49152658b95c2435e112b1e12`; adopter: main orchestrator; reviewer: fresh `spec-reviewer`; reflected_to: [`requirement.md`, `design.md`, `plan.md`, onboarding artifact]; blocking: no | implementation時はcanonical R/D/Pをauthorityとし、ZIPはadvisory evidenceとして保持 |
| EAL-003 | `adopted` | 2026-08-02 operator instruction and main-orchestrator synthesis | `plan.md` execution procedure、`report.md` review evidence slots | Luna・Maxの実装品質を補助しつつ過剰指定を避けるため、push先行のstep具体化、Artifact低authority、single-thread複合review、main orchestrator裁定をIssue 346限定で採用した | `artifacts/20260801t152944z-disc-chatgpt-assisted-execution-agreement.md`; adopter: main orchestrator; review exclusion: explicit operator instruction; blocking: no | 各stepでplan §2.3と§x.0を実行し、observed receipt/head/review結果を本reportへ記録 |
| EAL-004 | `rejected` | failed/stale formal ChatGPT sessions for S01 pre-step | Issue 346 S01 pre-step elaboration artifact | 新規sessionが`promptSubmitted:null`のままdetached/incomplete-captureとなり、harvestで得られた回答は別Issue 00334の内容だったため、S01の作業具体化として保存・採用しない | session diagnosticsとstale outputの内容・scope不一致を確認。Workbenchの誤出力は削除済みで、正本R/D/Pは変更していない | no further action。無関係なstale outputを採用しない判断は確定し、成功したEAL-005で置換した | blocking: no; adopter: main orchestrator; reviewer: not applicable; superseded by EAL-005 |
| EAL-005 | `adopted` | formal ChatGPT Pro S01 pre-step elaboration (`iss346-s01-prestep-aug2e`) | S01 test implementation aid | GitHub connectorでcurrent branch/HEADを確認し、canonical plan §8のtest cards・allowed pathsと整合する限定的な再受領、denylist negativeとinstalled `validate`確認を提案した。新APIやproduction repairを要求せず、R/D/Pを上書きしないため補助evidenceとして採用する | `artifacts/20260801t164728z-chatgpt-output-s01-chatgpt-pre-step-elaboration.md`; source SHA-256 `283c7854120a945c9432fae36848c6966bc1ee92a83eaf39b0c335b94f36d37b`; session model evidence `requested=Pro; resolved=Pro; verified=yes`; pushed head `75ba8f1fdec2b9cee5624dbdd2741614b4755778` | S01 current-cycle evidence、review、report bindingは完了。追加のS01作業は不要 | blocking: no; adopter: main orchestrator; reviewer: S01 ChatGPT Pro implementation review; next_action: no open action |
| EAL-006 | `adopted` | formal ChatGPT Pro S90 docs pre-step (`iss346-s90-docs-prestep`) | S90 provider docs/projection/report trace | pushed HEAD `ef467c1b84d9d7dfce64c6c4d98bcea5c560fc81`のdocs gap（Linux/macOS publication wording、fast/full lane、stale report/EAL trace）を特定し、plan §12のallowlist内で最小更新を提案した。S99完了やcanonical R/D/P変更は主張していない | `artifacts/20260802t004508z-chatgpt-output-20260802t-s90-docs-prestep.md`; SHA-256 `6a50d4a294c81ae7467ff25ae2e7956e9075bc8f0ae075670f0bfc5ba60eaec4`; 15,616 bytes; `requested=Pro; resolved=Pro; verified=yes` | provider docs、projection、status manifestを更新し、S90 fresh docs/spec reviewへ進む | blocking: no; adopter: main orchestrator; reviewer: pending; next_action: S90 review |
| EAL-007 | `adopted` | formal ChatGPT Pro S02 pre-step elaboration (`iss346-s02-prestep-aug2`) | S02 test implementation aid | candidate wheelを再利用するvalid synthetic fixture、existing scope no-backfill、future shell、illegal preexisting README negativeの4カードをcanonical plan §9と照合して採用した。production repairやplan変更は提案していない | `artifacts/20260801t181356z-chatgpt-output-s02-chatgpt-pro-pre-step-elaboration.md`; SHA-256 `acef67c55e96ba6f484ccabbd96f8b7e361565a8086ba3e25da405d01f0cad7b`; `requested=Pro; resolved=Pro; verified=yes`; pushed headはreportへ記録済み | S02 test-only evidenceへ統合済み | blocking: no; adopter: main orchestrator; reviewer: S02 ChatGPT Pro implementation review; next_action: no open action |
| EAL-008 | `adopted` | S02 ChatGPT Pro implementation/re-review chain | S02 report、test cards、review gate | 初回P1 findings（snapshot/managed asset/report binding）をtest/report-only remediationへ限定し、再レビューのP0/P1 unresolved 0を採用した。provider/runtime変更やscope expansionはない | initial Artifact `artifacts/20260801t184027z-chatgpt-output-s02-chatgpt-pro-implementation-review.md`; final Artifact `artifacts/20260801t193534z-chatgpt-output-20260802t-s02-chatgpt-pro-remediation-review.md`; final SHA-256 `37ed32f9adb3740d81cd5c5549161452576d7b516afd88498b96a18a92dd3f78`; reviewed head `e23345698c16d20fb8947a1f4b102856ffeb5bc3`; `review_status=pass` | S02 closure remains accepted; evidence is advisory and report ledger is authoritative | blocking: no; adopter: main orchestrator; reviewer: ChatGPT Pro; next_action: no open action |
| EAL-009 | `adopted` | formal ChatGPT Pro S03 pre-step elaboration (`iss346-s03-prestep-aug2`) | S03 platform/privacy test and host receipt contract | 4 target、external/nested-CWD privacy、actual cross-FS、Linux anonymous publication、macOS clone/cleanup boundaryをplan §10のcardsへ限定して整理した。hermetic代替やprovider repairは採用していない | `artifacts/20260801t195402z-chatgpt-output-20260801t-s03-chatgpt-pro-prestep-elaboration.md`; SHA-256 `503839b645ba0b83fe8ddeac5e8616d3cf28d9cb403e6f33a46d7f6acd188cc9`; `requested=Pro; resolved=Pro; verified=yes`; reviewed pushed head `d8079e71a6e951b31d506840c3a4a130e3bdcb73` | S03 bounded probe/test evidenceへ統合済み | blocking: no; adopter: main orchestrator; reviewer: S03 ChatGPT Pro implementation review chain; next_action: no open action |
| EAL-010 | `adopted` | S03 ChatGPT Pro implementation/review chain | S03 platform probe、privacy tests、report receipts | 初回・remediation・binding correctionの各FAILを、probe観測・image digest・full SHA bindingのreport/test-only修正へ限定し、binding-correction reviewのP0/P1/P2/P3=0を採用した。provider/runtime sourceは変更していない | final Artifact `artifacts/20260801t220052z-chatgpt-output-20260802t-s03-chatgpt-pro-binding-review.md`; SHA-256 `39304d870a2b39d34549c8c2d91fe815f0d86ac794577eb93da8c2634fbf4a42`; reviewed report head `f4b9b18a6d006335544bd88143fd3696710dcb3e`; probe commit `0de9687f636ef0c3a185f5e9e112fe0ca180990a`; `review_status=pass` | S03 closure remains accepted; inherited Linux/macOS ADR boundary is not expanded | blocking: no; adopter: main orchestrator; reviewer: ChatGPT Pro; next_action: no open action |
| EAL-011 | `adopted` | formal ChatGPT Pro S04 pre-step elaboration (`iss346-s04-prestep-aug2`) | S04 opaque lifecycle, projection, compatibility, dogfood test contract | filter-before-read、opaque body、slot allocation、provider-first projection、dogfood no-backfill/future shellをplan §11へ限定反映し、production repairは再現時のみとした | `artifacts/20260801t222431z-chatgpt-output-20260802t-s04-chatgpt-pro-prestep.md`; SHA-256 `3473f23ece7fd5a2fc1a42c8c204edd5de9c43d538e0034d405914628dcbe4da`; `requested=Pro; resolved=Pro; verified=yes`; reviewed head `c3da337ad10f51b75943f4856484467bb53f1272` | S04 test-only implementation and dogfood evidenceへ統合済み | blocking: no; adopter: main orchestrator; reviewer: S04 ChatGPT Pro implementation review; next_action: no open action |
| EAL-012 | `adopted` | S04 ChatGPT Pro code-review chain | S04 test oracle、opaque lifecycle、projection、dogfood privacy/no-backfill | 初回・fresh remediation FAILで示されたslot集合、raw JSON、privacy sentinel、report bindingの不足を許可されたtest/report scopeへ限定修正し、final exact-head reviewのP0/P1/P2/P3=0を採用した。production repair=falseを維持した | final Artifact `artifacts/20260802t003003z-chatgpt-output-20260802t-s04-code-review-final.md`; SHA-256 `38bad4e4b17b5ddb16542ce8566f8f63dd47fd5d1ba89413aecebf96ed2ba7be`; reviewed head `2af3a145ec1a29e05f677d13ee20d53e55f38e3f`; `review_status=pass` | S04 implementation gateはclosed。S90はこのevidenceを参照し、S99でIssue-wide reviewを再実施する | blocking: no; adopter: main orchestrator; reviewer: ChatGPT Pro; next_action: no open action |
| EAL-013 | `adopted` | S04 candidate-wheel provider-to-dogfood projection receipt | S04 dogfood projection and S90 parity trace | provider sourceの既存accepted runtime変更はS04 candidate-wheel updateでdisposable consumerへ投影済みだったが、チェックイン済みdogfood mirrorが遅れていた。S90の`870846fd`はそのmanaged mirror/status manifestをprovider-firstで同期するprojection correctionであり、新しいruntime repairではない | S04 report `Fresh-Update-Dogfood Matrix` / `Provider-to-Dogfood Projection Manifest`; `870846fda494f7ab76af0d1e913a7a508bd14099`; status manifest `6b815c9c`; source/projection parity and S04 expected paths; `production repair=false` | plan §12.3 clarificationへ反映し、S90 fresh reviewでこの境界を再確認する | blocking: no; adopter: main orchestrator; reviewer: pending S90 ChatGPT Pro spec review; next_action: S90 re-review |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | candidate wheelをfresh/update/dogfoodへ流し、Workbench shellとgeneric importの配布統合を閉じる | privacy、opaque lifecycle、既存command互換、platform boundary、docs/review/delivery | low。副次的platform検証が新機能実装へ膨張しないよう最小integration repair境界を固定 | final planning review `pass` |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | 親Epic R/D/P、Issue 344/345 report、accepted ADR 3件、clarification research、ChatGPT ZIP、現行code/tests | なし | clarificationをadopted、ChatGPT requirement候補をpartially_adopted | final verdict `(pass)`; fresh `iss346_requirement_final_rereview`; findings 0 | no | designへ昇格 `(promote)` |
| design | review済みrequirement、accepted ADR 3件、ChatGPT design候補、現行provider/build/update/runtime/test surface | なし | ChatGPT候補の責務分割・trace・test strategyをpartially_adopted。候補frontmatterと固定planning baseline表現は不採用 | final verdict `(pass)`; fresh `iss346_design_final_rereview`; findings 0 | no | planへ昇格 `(promote)` |
| plan | review済みrequirement/design、ChatGPT plan候補、現行workflow/assurance/test command surface | なし | ChatGPT候補のS01〜S04/S90/S99、closure index、test cardsをpartially_adopted。候補frontmatter、固定planning baseline、曖昧path、省略されたreview-evidence境界は不採用 | final verdict `(pass)`; fresh `iss346_planning_final_gate_review`; findings 0 | no | execute approved plan |

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）
- 委任 authoring の使用:
  - SpecDock named delegated authoring subagent: not used
  - external ChatGPT authoring evidence: used
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
| external-chatgpt-authoring | iss-00346 | `artifacts/20260730t173917z--specdock-iss-00346-authoring-pack-corrected.zip` | GitHub-synced repository/branch/planning baseline、clarification artifact、parent/upstream specs | `requirement.md`, `design.md`, `plan.md`, onboarding artifact | `partially_integrated` | [`requirement.md`, `design.md`, `plan.md`, `artifacts/20260730t182546z-research-issue-346-onboarding-guide-for-new-team-members.md`] | pack review `pass`; tree SHA-256 `7b01a12ac95b13bcfdf4a3a60774d16c3dc666d49152658b95c2435e112b1e12` | main orchestratorがローカルsourceと照合して4資料へ段階統合 | candidate用frontmatter、evidence-only自己claim、planning baselineへのcandidate固定、曖昧path | none | pass | execute approved plan |

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
- S01では、candidate wheelの受領・inventory・isolated origin・fresh consumer tracerを検証する4件の統合テストを追加した。既存のpackage/setup実装にproduction repairは不要で、wheel-installed consumerからWorkbench README配布とgeneric artifact importを確認できる。
- S01のローカル品質証跡はGreenだが、Issue固有のChatGPT Pro review gateはfresh session送信失敗のため未完了であり、S02開始前に解消する。

## S01 実装証跡（2026-08-02）

### Source Revision and Candidate Wheel Receipt

| 項目 | 観測値 |
|---|---|
| ブランチ | `iss-00346-integration-distribution-and-final-quality` |
| candidate HEAD | `3d5b0ad6f675f79b8b9c3a569091c327b8bb2295` |
| remote HEAD | `3d5b0ad6f675f79b8b9c3a569091c327b8bb2295`（一致） |
| working tree | `git status --short` 空（clean） |
| production repair | なし（test-only） |
| changed path | `tests/integration/test_epic_00343_distribution.py` |

### 実装したテストカード

| Test ID | 検証内容 | 観測結果 |
|---|---|---|
| `tc-346-s01-001` | candidate revision、clean build、pre/post HEAD同一 | pass |
| `tc-346-s01-002` | 5 README allowlist、stale/cache denylist、missing README controlled negative | pass |
| `tc-346-s01-003` | isolated wheel install、console/module origin、PYTHONPATH source fallback negative | pass |
| `tc-346-s01-004` | fresh installed shell、README byte equality、ignored payload、generic import (`canonical=false`) | pass |

### 実行コマンドと結果

```text
uv run pytest tests/integration/test_epic_00343_distribution.py --run-full-regression -q
4 passed in 5.57s

uv run pytest tests/cli_runtime/test_runtime_new_doc_s09.py -k 'workbench or readme' --run-full-regression
1 passed, 34 deselected

uv run pytest tests/unit/infra/test_init_update.py -k 'issue_69 or workbench_readme_distribution or workbench_readme_build_prune or isolated_wheel_install_runs_init_update' --run-full-regression -q
15 passed, 551 deselected in 33.53s

uv run ruff check tests/integration/test_epic_00343_distribution.py
All checks passed

git diff --check
pass
```

### S01 closure mapping

| Closure | Evidence | Result |
|---|---|---|
| `CL-346-AC-001` / `CL-346-CON-001` / `CL-346-EC-001` | test receipt pre/post HEAD assertion、clean commit/push、candidate HEAD/remote一致 | pass |
| `CL-346-AC-002` / `CL-346-EC-002` | zip inventory allowlist/denylistとmissing-entry negative | pass |
| `CL-346-AC-003` / `CL-346-EC-003` | isolated venvのinstalled originとfresh shell/import tracer | pass |
| `CL-346-CON-004` | provider templateとfresh consumerのREADME byte equality、source不変、`canonical=false` | pass |

### ChatGPT-assisted gate status

- Pre-step prompt: `spec-dock/active/issue/.workbench/20260802-s01-chatgpt-prestep-prompt.md`を作成した。初回formal wrapperの新規sessionは送信前にdetached/incomplete-captureとなった。
- Recovery後のvalid pre-step: `iss346-s01-prestep-aug2e`。`requested=Pro; resolved=Pro; status=already-selected; strategy=select; verified=yes`、GitHub connector-confirmed remote HEAD `75ba8f1fdec2b9cee5624dbdd2741614b4755778`。
- 採用Artifact: `artifacts/20260801t164728z-chatgpt-output-s01-chatgpt-pre-step-elaboration.md`（SHA-256 `283c7854120a945c9432fae36848c6966bc1ee92a83eaf39eaf39b0c335b94f36d37b`、13,484 bytes、`committed=true`）。
- ChatGPTは現HEADで旧S01 wheel証跡をstaleと判定し、denylist controlled negativeとinstalled `validate`確認を、既存test-only範囲内のbounded completionとして提案した。canonical plan §8.3/§8.5と照合して採否を判断する。
- Attempted session slugs: `iss346-s01-pre-step`, `iss346-s01-prestep-aug2`, `iss346-s01-followup`, `iss346-s01-prestep-tty`, `iss346-s01-wrapper-smoke`。
- `harvest`で得られた旧回答はIssue 00334のS019内容であり、Issue 346へscope外のため採用・importしていない。
- Cheetah指定はdry-runで`gpt-5.2`へ正規化されたため、品質ゲートのモデル証跡として使用していない。
- S01 implementation ChatGPT Pro review: 初回レビュー `iss346-s01-review-aug2b` は `requested=Pro; resolved=Pro; verified=yes` で実行され、P1を3件検出して `fail`。修正後の再レビュー `iss346-s01-review-remediatio-aug2` も同じPro選択証跡で実行され、P0/P1なしの `pass`。再レビューArtifact `20260801t174834z`（SHA-256 `358037ebc3a0699b151004fd67a9a187ceffeee03631fe936b35137fc88f94c4`）を保存した。Cheetahは正式ラッパーの対応対象外であり、品質ゲート証跡には使用していない。

### S01 closure decision

valid pre-step Artifact取得後、提案したtest-only completionを反映してcurrent HEADで再build・再検証した。実装、focused/full S01、関連Workbench/readme、ruff、diff-checkはGreenである。修正後のcurrent-head ChatGPT Pro implementation reviewはP0/P1なしの `pass` で、S01をクローズしS02のpre-step gateへ進める。

### S01 current-cycle candidate receipt（2026-08-02）

| 項目 | 観測値 |
|---|---|
| ブランチ | `iss-00346-integration-distribution-and-final-quality` |
| local HEAD | `ab34700409d132f1c9cd39a2471ff6645cecca49`（S01 test correction後のreport/Artifact successor） |
| remote HEAD | `ab34700409d132f1c9cd39a2471ff6645cecca49`（一致） |
| working tree | clean（`git status --short` 空、dist/buildはignored生成物） |
| candidate wheel | pytest-managed temporary wheel（このwheelをinventory・install・origin probe・fresh consumerで共用） |
| package version | `0.2.3` |
| wheel SHA-256 | `850705a88ad8e10cf9183489384ab724ed62a138e6b993cc42f1bc398f58d539`（install対象と同一pathをfixtureで固定） |
| sorted ZIP inventory | 322 non-directory file entries、5 README allowlist、stale/cache denylist pass |
| production repair | なし。test-only bounded completion |

#### Current-cycle verification

```text
uv run pytest tests/integration/test_epic_00343_distribution.py --run-full-regression -q
4 passed in 6.36s

uv run pytest tests/cli_runtime/test_runtime_new_doc_s09.py -k 'workbench or readme' --run-full-regression -q
1 passed, 34 deselected in 0.11s

uv run pytest tests/unit/infra/test_init_update.py -k 'issue_69 or workbench_readme_distribution or workbench_readme_build_prune or isolated_wheel_install_runs_init_update or fresh_init_creates_only_tracked_root_workbench_readme' --run-full-regression -q
16 passed, 550 deselected in 33.86s

uv run ruff check tests/integration/test_epic_00343_distribution.py
All checks passed

git diff --check
pass
```

S01 focused suite was intentionally rerun only after commit/push; the worker's pre-commit run recorded `1 failed, 3 passed` solely because the strict receipt observes the in-progress `M` test file. The post-commit current-cycle run is the closure evidence. The receipt digest and inventory above are emitted by the pytest fixture for the exact wheel path passed to the installer; no separately built `dist/` wheel is used for this candidate.

### S01 initial implementation review finding and remediation

初回のChatGPT Pro実装レビュー（Artifact `20260801t172841z`、SHA-256 `02005f833935b5f4de0b070e5aecc4761cb920db66f4db7107cfb839d7379ae4`）は、現行実装に対して次のP1を指摘した。

1. `report.md` のwheel receiptが現行pushed HEADに紐付いていない。
2. receiptの `dist/` wheelと、pytestがinstall・実行したtemporary wheelの同一性が証明されていない。
3. import/validate後のignored・untracked確認と、stdout/stderr双方のprivate path漏えい確認が不足している。

これを受け、`035c45f8` で `tests/integration/test_epic_00343_distribution.py` のみを修正した。単一のinstall対象wheel pathのSHA-256をfixtureで固定し、import/validate後のsource・destination byte保持、ignored・Git index非掲載、import/validateのstdout・stderr全経路のprivate path検査を追加した。初回レビュー回答と再レビュー回答はArtifactとして保存済みで、再レビューは `2ad7071b`（report/Artifactのみの後続コミット）を現行pushed HEADとして確認し、S01 closure `pass` を返した。

### S01 reviewer-gate handoff to S02

再レビューが指摘したP2のwheel引き渡し条件は、S02開始前に次のreceiptを追加して解消する。S02で別のprovider source/test変更が入る場合は、その変更後に候補wheelを再生成し、S02固有のreceiptへ切り替える。

- candidate basename: `spec_dock-0.2.3-py3-none-any.whl`
- deterministic selection: pytest fixtureがbuild出力ディレクトリをglobし、sorted結果が1件であることを検証して選択する（`len(wheel_paths) == 1`）。選択した同一pathをSHA-256計算、installer requirements、inventory、origin probe、fresh consumer、generic import、installed `validate`へ渡す。
- exact node IDs: `test_tc_346_s01_001_candidate_wheel_receipt`, `test_tc_346_s01_002_candidate_wheel_inventory`, `test_tc_346_s01_003_isolated_wheel_origin_rejects_checkout_fallback`, `test_tc_346_s01_004_fresh_consumer_installed_shell_and_generic_import`
- physical handoff: S01再検証時に `.workbench/s01-candidate-wheel/spec_dock-0.2.3-py3-none-any.whl` へ同一wheelをコピーして保持した。保持wheelのSHA-256は `850705a88ad8e10cf9183489384ab724ed62a138e6b993cc42f1bc398f58d539`、inventoryは322 non-directory file entries、S01全4ノードは `4 passed in 6.36s`。保持wheelはWorkbench内のignoredファイルでありGit管理対象外で、S02 pre-stepでbasename/digestを再確認する。

### S02 ChatGPT pre-step evidence

- pre-step session: `iss346-s02-prestep-aug2`、`requested=Pro; resolved=Pro; status=already-selected; strategy=select; verified=yes`。
- Artifact: `20260801t181356z-chatgpt-output-s02-chatgpt-pro-pre-step-elaboration.md`（SHA-256 `acef67c55e96ba6f484ccabbd96f8b7e361565a8086ba3e25da405d01f0cad7b`、6,490 bytes）。
- advisory conclusion: S02はtest-only characterizationから開始し、S01のcandidate wheel/installed helpersを再利用する。valid synthetic existing hierarchy（README absent matrix、ignored payload、candidateと異なるmanaged guide）を作り、update後のno-backfill、future node shell、illegal preexisting README negativeを4カードで検証する。production repairはcandidate-wheel上の再現可能な欠陥が出た場合に限る。
- canonical plan §9.0–§9.6を優先し、ChatGPT出力はテストカード・receipt項目・停止条件の補助資料として扱う。workerはcanonical reportを編集しない。

### S02 implementation evidence (current cycle)

- executable implementation commit: `1650c73c53f7397cc5f29d5262479f860125c9d6`、snapshot remediation commit: `dfee5a4d54a880f0d5ca5fd57bb699540cb3eb9c`（いずれも`tests/integration/test_epic_00343_distribution.py`のtest-only、provider/plan/reportは変更なし）。
- verification-bound pushed HEAD: `8e2ff88af676709f4d18eab30d36e29013e715c1`、local/remote一致。`8e2ff88a`は`dfee5a4d`後のreport/Artifact-only successorである。以降の`d4ce6625`、`369200ff`および後続のreport-only evidence successorもprovider/test codeを変更していないため、実行commit・verification-bound head・report-only successor chainを分離して記録する。今回のreport-only correctionを含む新しいpushed successorを、次回ChatGPT Pro reviewの対象としてGitHub connectorで解決する。実装差分の変更パスはintegration test 1ファイルのみ。
- S02 candidate wheelはS01のinstalled fixtureを再利用し、wheel ZIPからguide/template bytesを読み込む。synthetic existing hierarchyは `init-00401` / `epic-00402` / `iss-00403`、future hierarchyは `init-00501` / `epic-00502` / `iss-00503`。
- 4つのS02 test cardは、README absent preflight、update no-backfill、future shell、path-specific illegal preexisting README negativeを検証する。production repairは不要（`production_repair_justified=false`）。

#### S02 verification receipt

```text
uv run pytest tests/integration/test_epic_00343_distribution.py \
  -k 'existing_consumer or no_backfill or future_node' --run-full-regression -q
4 passed, 4 deselected in 13.53s

uv run pytest tests/integration/test_epic_00343_distribution.py \
  --run-full-regression -q
8 passed in 15.60s

uv run pytest tests/unit/infra/test_init_update.py \
  -k 'update and workbench' --run-full-regression -q
14 passed, 1 failed, 551 deselected
```

The single unit failure is the pre-existing `test_shipped_docs_describe_workbench_readme_boundary`: it reports missing Issue 345 planned/unimplemented generic-import claims in `docs/README.md` and `docs/reference_worktree.md`. S02 changed neither provider docs nor those assertions, so it is recorded as an unrelated existing failure and not repaired in this vertical slice. `uv run ruff check tests/integration/test_epic_00343_distribution.py` and `git diff --check` passed.

#### Post-remediation verification receipt

The following commands were rerun after the `dfee5a4d` test-oracle remediation, at verification-bound pushed HEAD `8e2ff88a`. `d4ce6625` and `369200ff` are report-only successors; no provider or test code changed after the recorded verification. A fresh review is requested against the exact pushed successor created by this report-only correction, with that SHA recorded in the follow-up review Artifact and closure row.

```text
uv run pytest tests/integration/test_epic_00343_distribution.py \
  -k 'existing_consumer or no_backfill or future_node' --run-full-regression -q
4 passed, 4 deselected in 13.42s

uv run pytest tests/integration/test_epic_00343_distribution.py \
  --run-full-regression -q
8 passed in 15.03s

uv run ruff check tests/integration/test_epic_00343_distribution.py
All checks passed!

git diff --check
pass
```

#### S02 scope and gate state

The worker did not edit canonical reports or provider code. S02 implementation review is now `pass` at exact pushed head `e23345698c16d20fb8947a1f4b102856ffeb5bc3`; the review focused on synthetic fixture validity, no-backfill sensitivity, canonical/metadata/payload preservation, wheel-template equality, future-node tracking, controlled negative specificity, and scope boundedness. S03 may start after this bounded report/Artifact transcription; no provider or test code changed after the verification-bound successor.

### S02 implementation review finding and remediation

- 初回Pro review Artifact `20260801t184027z`（SHA-256 `e331fd69772aced3a6ddd25ab4da181e48c200457eb031d1c3db25c5e84d5493`）はP1を3件検出した。`deps-raw.puml`がgraph snapshotにない、root-managed install assetsのsnapshotが不足、report ledgerがsuccessor HEAD/closure rowsへ束縛されていない、という証跡上の指摘であり、production defectではない。
- `dfee5a4d54a880f0d5ca5fd57bb699540cb3eb9c` でintegration test onlyの補正を適用し、`_snapshot_graph`へ`deps-raw.puml`を追加、`_snapshot_managed_assets`へinstallerが管理するroot `.agents/**`・`.codex/**`・`.github/**`を相対path+bytesで追加した。
- `dfee5a4d54a880f0d5ca5fd57bb699540cb3eb9c` はsnapshot remediationの実装commitである。`8e2ff88a`、`d4ce6625`、`369200ff`はreport/Artifact-only successorとして扱い、今回のreport-only correction後に作成する新しいpushed successorは、次回レビューの実対象として別途記録する。implementation commit・verification-bound head・report-only successorを混同しない。
- `historical_option_used: no`。synthetic current-runtime fixtureを使用し、historical SHA/feature-absence fixtureは使用していない。

#### S02 closure ledger (fresh review pending)

| Closure / contract | Evidence | Result |
|---|---|---|
| `tc-346-s02-001` → `CL-346-CON-006`, `CL-346-EC-004`, `CL-346-EC-005`, `CL-346-EC-006` | valid synthetic fixture、4 scope README absent、payload/graph/canonical snapshot preflight、stale guide differs from wheel | pass（test evidence） |
| `tc-346-s02-002` → `CL-346-AC-004`, `CL-346-EC-005`, `CL-346-EC-006` | update後のexisting no-backfill、payload/metadata/deps/canonical equality、managed delta guide-only | pass（test evidence） |
| `tc-346-s02-003` → `CL-346-AC-005` | future `init-00501` / `epic-00502` / `iss-00503` README template byte equality・tracked、既存scope absent維持 | pass（test evidence） |
| `tc-346-s02-004` → `CL-346-AC-004`, `CL-346-EC-004` | preexisting Issue READMEを1件injectし、relative path-specific AssertionErrorを確認 | pass（negative sensitivity） |
| Step Contract Closure / S02 | 4 cards、candidate-wheel installed runtime、test-only bounded paths、historical option `no` | pass（implementation evidence） |
| Test Contract Closure / S02 | focused 4 passed、full integration 8 passed、ruff/diff-check pass | pass（implementation evidence） |
| Delegated Worker Evidence / S02 | worker changed integration test only、production repair `false`、no material implementation decisions | pass |
| ChatGPT Pro implementation review | exact pushed head `e23345698c16d20fb8947a1f4b102856ffeb5bc3`、Artifact `20260801t193534z-chatgpt-output-20260802t-s02-chatgpt-pro-remediation-review.md`、P0/P1 unresolved 0 | pass |

#### S02 implementation review result

- session: `iss346-s02-review-remediatio-aug2d`、`requested=Pro; resolved=Pro; status=already-selected; strategy=select; verified=yes`。
- reviewed head: `e23345698c16d20fb8947a1f4b102856ffeb5bc3`。`e2334569`はreport-only correctionであり、`dfee5a4d`以降のprovider/test code変更はない。
- Artifact: `20260801t193534z-chatgpt-output-20260802t-s02-chatgpt-pro-remediation-review.md`（SHA-256 `37ed32f9adb3740d81cd5c5549161452576d7b516afd88498b96a18a92dd3f78`、5,748 bytes、`import_kind=chatgpt-output`、`storage_identity=blank`）。
- verdict: `pass`。P0/P1/P2/P3はすべて0件。初回のP1（`deps-raw.puml` graph snapshot、root-managed asset snapshot、successor head/closure ledger）はすべて解消され、S02の4カードはbounded test-only scopeとして有効と判定された。S02をcloseし、S03を開始できる。

### S03 ChatGPT pre-step evidence

- pre-step session: `iss346-s03-prestep-aug2`、`requested=Pro; resolved=Pro; status=already-selected; strategy=select; verified=yes`。
- reviewed pushed head: `d8079e71a6e951b31d506840c3a4a130e3bdcb73`。S02 passのArtifact/report転記後のheadであり、S03開始前に確認した。実装開始時にHEAD/local/remote/working-treeを再確認し、移動していればこのbindingをstaleとして再取得する。
- Artifact: `20260801t195402z-chatgpt-output-20260801t-s03-chatgpt-pro-prestep-elaboration.md`（SHA-256 `503839b645ba0b83fe8ddeac5e8616d3cf28d9cb403e6f33a46d7f6acd188cc9`、43,682 bytes、`import_kind=chatgpt-output`、`storage_identity=blank`）。
- advisory decision: current-cycle candidate wheelをS01/S02 helperで再構成し、4 target generic import、absolute/nested-CWD privacy、actual cross-filesystem、Linux anonymous/no-replace、macOS clone/cleanupを順に検証する。production修正はcandidate wheelまたはactual hostで再現するcontract defectがある場合のみ許可し、既存コードが契約を満たせばtest/probe-onlyで完了する。`unavailable`・skip・hermetic simulationはactual host successに数えない。
- required host evidence: actual Linux supported publication、actual macOS clone-capable publication、`st_dev`が異なるactual cross-FS sourceを各content-free receiptへ記録する。host-local path、payload、user-file digest/count、UID/username、mutable container tagを保存しない。Linux preflightとformal link commitを分離し、macOS cleanup uncertaintyはretain/no-unlinkとし、same-UID exclusionを超える保証を主張しない。
- worker handoff: allowed pathsはplan §10.3のintegration/host probe/unit/CLI/presentation testsと列挙されたrepair-only runtime pathsに限定する。workerはcanonical report/R/D/Pを編集せず、S03 focused/host結果・changed paths・privacy matrix・production repair有無を返す。S03はhermetic Greenだけではcloseできず、全host条件とexact pushed-head ChatGPT Pro reviewが必要。

### S03 implementation evidence (current cycle)

- initial implementation review: `iss346-s03-implementa-review-aug2` (`requested=Pro; resolved=Pro; verified=yes`) は5件のP1を検出してfailした。修正対象をS03のintegration test、platform probe、reportに限定し、provider/runtime sourceは変更しない方針で再実行した。初回出力はArtifact `20260801t204927z-chatgpt-output-20260802t-s03-chatgpt-pro-review-initial.md`（SHA-256 `3184b9f2446b5a6579c96e0ff1ce2e13da8bd474b684c06b6d37b39c857c5280`、8,113 bytes）へ保存した。
- remediation review: `iss346-s03-review-remediatio-aug2e` (`requested=Pro; resolved=Pro; verified=yes`) は2件のP1（probeの呼出し観測不足、Linux image digestのreceipt不足）を検出してfailした。出力はArtifact `20260801t212138z-chatgpt-output-20260802t-s03-chatgpt-pro-review-remediation.md`（SHA-256 `fdff69fd5f54d99056fffd38841abd4a775ebae1052a5ad9d9b6ea3fd332dd82`、5,855 bytes）へ保存した。provider/runtime sourceは引き続き変更しない。
- final binding review: `iss346-s03-review-final-aug2` (`requested=Pro; resolved=Pro; verified=yes`) はP0=0、P1=1でfailした。probe実装・実機結果自体は非該当で、reportに記録した0de9687fのフルSHAが誤っていたためGitHubで解決できないという束縛不備だった。出力はArtifact `20260801t214444z-chatgpt-output-20260802t-s03-chatgpt-pro-final-review.md`（SHA-256 `5486987fed615e980d6b1fa55951f61a540ea18a3be1a6bafd491315d1402170`、6,376 bytes）へ保存した。実際の到達可能なprobe commitは`0de9687f636ef0c3a185f5e9e112fe0ca180990a`であり、reportをこのSHAへ訂正してfresh reviewを再取得する。
- binding-correction review: `iss346-s03-review-binding-aug2` (`requested=Pro; resolved=Pro; verified=yes`) はP0/P1/P2/P3すべて0のpassだった。GitHub connectorで`f4b9b18a6d006335544bd88143fd3696710dcb3e`とprobe commit `0de9687f636ef0c3a185f5e9e112fe0ca180990a`の到達性、probe blob一致、candidate wheel/head bindingを確認した。出力はArtifact `20260801t220052z-chatgpt-output-20260802t-s03-chatgpt-pro-binding-review.md`（SHA-256 `39304d870a2b39d34549c8c2d91fe815f0d86ac794577eb93da8c2634fbf4a42`、9,187 bytes）へ保存した。S03はcloseし、S04 pre-step gateへ進める。
- remediation commit: `e02b953a43b303ea99e0fa200f9153f748093825`。変更は`tests/integration/test_epic_00343_distribution.py`（tc-346-s03-001〜003、controlled privacy negative、bounded public/tracked scan、portable cross-FS cleanup）と`tests/integration/iss346_platform_probe.py`（Linux/macOS safety predicate、observed cleanup/stage/fault fields）のtest-onlyで、provider/runtime sourceは変更していない。local/remote headは一致している。
- latest probe remediation commit: `0de9687f636ef0c3a185f5e9e112fe0ca180990a`。`tests/integration/iss346_platform_probe.py`だけを変更し、Linux capability-insufficientの`open`/`unlink`呼出し、macOS clone primitive/fallback呼出し、container image digestを直接観測・出力する。local/remote headはこのcommitへ一致している。
- candidate wheel receipt: `pre_head=e02b953a`、`post_head=e02b953a`、clean state。wheel basename `spec_dock-0.2.3-py3-none-any.whl`、SHA-256 `47326f1d064448009e7f7ededf272a5b51fad06ae9a481b2171903489b84309c`。candidateは同一wheelをisolated venvへinstallしている。provider/runtime bytesは前回S03 executable commit以降変化していない。
- focused verification: `uv run pytest tests/integration/test_epic_00343_distribution.py -k 's03' --run-full-regression -q` → `3 passed, 8 deselected in 9.21s`。`uv run pytest tests/unit/infra/test_binary_artifact_publisher.py -k 'explicit or privacy or cross or linux or macos or publication or cleanup' --run-full-regression -q` → `59 passed, 2 skipped, 36 deselected in 0.17s`。`uv run pytest tests/cli_runtime/test_artifact_import_file.py --run-full-regression -q` → `7 passed in 6.78s`。`uv run ruff check tests/integration/iss346_platform_probe.py tests/integration/test_epic_00343_distribution.py` → `All checks passed!`。`python -m py_compile tests/integration/iss346_platform_probe.py tests/integration/test_epic_00343_distribution.py` → pass。`git diff --check` → pass。

#### S03 actual host/platform receipt (content-free)

Receipts are bound to candidate `e02b953a` and wheel SHA-256 `47326f1d064448009e7f7ededf272a5b51fad06ae9a481b2171903489b84309c`; probe implementation is `0de9687f636ef0c3a185f5e9e112fe0ca180990a`. They record only platform/kernel, filesystem type, execution kind, immutable image binding (`sha256:...` or `not_applicable`), repo-relative probe command, stable evidence reference, and emitted boolean results; no host-local path, payload, UID/username, device number, or content-derived value is stored.

| Evidence ref | Probe | Execution / platform | Filesystem | Repo-relative command | Result / emitted evidence |
|---|---|---|---|---|---|
| `S03-HOST-MAC-001` | `macos-capability-preflight` | host / macOS Darwin 25.5.0 / Python 3.12.11 | APFS | `ISS346_PLATFORM_DEST=<destination-root> python tests/integration/iss346_platform_probe.py --probe macos-capability-preflight` | pass; `container_image_digest=not_applicable`, `fclonefileat_available=true`, `destination_clone_capable=true`, `stage_is_destination_side=true`, `stage_opened_exclusive_nofollow=true`, `parent_identity_stable=true`, `source_destination_same_device=false`, exit 0 |
| `S03-HOST-MAC-002` | `macos-clone-publication` | host / macOS Darwin 25.5.0 / Python 3.12.11 | APFS | `ISS346_PLATFORM_DEST=<destination-root> python tests/integration/iss346_platform_probe.py --probe macos-clone-publication` | pass; `container_image_digest=not_applicable`, `formal_no_replace_clone_succeeds=true`, `clone_primitive_calls=4`, `clone_primitive_succeeds=true`, `copy_or_rename_fallback_absent=true`, `copy_rename_fallback_calls=0`, `stage_device_matches_destination=true`, `owned_stage_cleanup_verified=true`, `parent_identity_stable=true`, `same_uid_exclusion_acknowledged=true`, `bytes_matched=true`, `source_unchanged=true`, `stage_is_destination_side=true`, `stage_opened_exclusive_nofollow=true`, `source_destination_same_device=false`, exit 0 |
| `S03-HOST-LINUX-001` | `linux-capability-preflight` | container / Linux 7.0.11-orbstack-00360-gc9bc4d96ac70 / Python 3.12.11 / non-root execution | destination `tmpfs`, source `overlayfs` | `ISS346_PLATFORM_DEST=<destination-root> ISS346_CONTAINER_IMAGE_DIGEST=sha256:77a36ff63e657d8ec7cd4e86e452f4cd23b6c92811696b0735226fbc0660a5b8 python tests/integration/iss346_platform_probe.py --probe linux-capability-preflight` | pass; `container_image_digest=sha256:77a36ff63e657d8ec7cd4e86e452f4cd23b6c92811696b0735226fbc0660a5b8`, `o_tmpfile_openable=true`, `anonymous_stage_regular=true`, `procfs_identity_matches_held_fd=true`, `destination_directory_fsync_succeeds=true`, `formal_no_replace_link_succeeds=false` (deferred), `source_destination_same_device=false`, exit 0 |
| `S03-HOST-LINUX-002` | `linux-supported-publication` | container / same pinned Linux image / non-root execution | destination `tmpfs`, source `overlayfs` | `ISS346_PLATFORM_DEST=<destination-root> ISS346_CONTAINER_IMAGE_DIGEST=sha256:77a36ff63e657d8ec7cd4e86e452f4cd23b6c92811696b0735226fbc0660a5b8 python tests/integration/iss346_platform_probe.py --probe linux-supported-publication` | pass; `container_image_digest=sha256:77a36ff63e657d8ec7cd4e86e452f4cd23b6c92811696b0735226fbc0660a5b8`, `formal_no_replace_link_succeeds=true`, `first_link_target_is_formal_destination=true`, `visible_stage_or_probe_absent=true`, `pathname_cleanup_absent=true`, `existing_destination_preserved=true`, `bytes_matched=true`, `source_unchanged=true`, exit 0 |
| `S03-HOST-LINUX-003` | `linux-capability-insufficient` | container / same pinned Linux image / non-root execution / fault point `linux_directory_durability` | destination `tmpfs`, source `overlayfs` | `ISS346_PLATFORM_DEST=<destination-root> ISS346_CONTAINER_IMAGE_DIGEST=sha256:77a36ff63e657d8ec7cd4e86e452f4cd23b6c92811696b0735226fbc0660a5b8 python tests/integration/iss346_platform_probe.py --probe linux-capability-insufficient` | pass; `container_image_digest=sha256:77a36ff63e657d8ec7cd4e86e452f4cd23b6c92811696b0735226fbc0660a5b8`, `formal_destination_absent=true`, `fallback_absent=true`, `fault_injected=true`, `visible_stage_open_calls=0`, `pathname_cleanup_calls=0`, `visible_stage_or_probe_absent=true`, `pathname_cleanup_absent=true`, `source_destination_same_device=false`, exit 0 |

The macOS cleanup uncertainty behavior is covered by the current-head hermetic publisher suite (`59 passed, 2 skipped`); the actual clone probe records only emitted fields and does not claim an unobserved retain/no-unlink field. `unavailable` was not used for the required lanes; all actual lanes returned pass.

#### S03 closure state

- target/source matrix and external privacy cards are Green; source bytes remain unchanged, destination bytes match, existing destination bytes are preserved, and `canonical=false` is asserted for all four target selectors. The privacy helper now exercises controlled path/body/digest-count/derived-value negatives and scans captured stdout/stderr, parsed JSON, bounded `.agent` public files, and tracked files owned by the disposable consumer.
- Linux preflight/formal commit are separated; no named/visible stage or pathname cleanup is observed, and capability insufficiency fails closed before formal destination creation.
- macOS clone and cleanup trust boundary are Green; copy/rename fallback is absent, parent/stage identity and cleanup are observed, and same-UID exclusion is recorded without overclaiming.
- production repair: `false`。S03のexact-head ChatGPT Pro binding-correction reviewはpass（P0/P1/P2/P3=0）し、test/probe/reportのbounded scopeでcloseした。provider/runtime変更はなく、S04はpre-step head-binding gate後に開始できる。

### S04 ChatGPT pre-step evidence

- pre-step session: `iss346-s04-prestep-aug2`。formal wrapper model evidence: `requested=Pro; resolved=Pro; status=already-selected; strategy=select; verified=yes`。GitHub connector inspection succeeded for `chemitaro/spec-dock`; current branch `iss-00346-integration-distribution-and-final-quality` resolved to pushed HEAD `c3da337ad10f51b75943f4856484467bb53f1272` and attached blobs matched that revision.
- Artifact: `artifacts/20260801t222431z-chatgpt-output-20260802t-s04-chatgpt-pro-prestep.md`（SHA-256 `3473f23ece7fd5a2fc1a42c8c204edd5de9c43d538e0034d405914628dcbe4da`、26,553 bytes、`import_kind=chatgpt-output`、`storage_identity=blank`）。Artifactは補助evidenceであり、canonical plan §11を上書きしない。
- advisory conclusion: current production code is provisionally a no-op for S04; bounded test-only additions should close the missing opaque fixture matrix, fresh body-open spy, complete projection/context equivalence, and disposable dogfood no-backfill/future-shell plus generic import cards. Existing compatibility suites should remain unchanged; production repair is allowed only after an exact-head test reproduces a contract defect in a plan-listed repair path.
- implementation cautions adopted for execution: import generic fixtures through the public projected command before lifecycle spying; keep a fresh empty guard for the measured window and intercept `Path.open`, `builtins.open`, and `io.open`; do not read/hash generic destinations while the guard is active; normalize only named generated timestamp fields; use a fresh disposable exact-revision checkout and dynamically selected future node identifier; bind all final wheel, test, report, and review evidence to the later pushed S04 head rather than this pre-step head.
- uncertainty retained: tests were not executed by the consultation; if a required repair falls outside plan §11.3 or a legacy public contract must change, stop and return to amendment/clarification.

### S04 implementation evidence (exact pushed head)

#### Source Revision and S04 Candidate Receipt

| 項目 | 観測値 |
|---|---|
| ブランチ | `iss-00346-integration-distribution-and-final-quality` |
| S04 executable/test HEAD | `8ef9aab38d92165e865a7336f2b385126e979da3`（`test(iss-00346): S04再レビュー指摘分のテストを追加`） |
| remote executable/test HEAD | `8ef9aab38d92165e865a7336f2b385126e979da3`（一致） |
| report-only successor before remediation | `4565f183`（`0c510e21` の後続。`report.md` のみ変更） |
| fresh review target before remediation | `4565f183`（report-only successor、下記 Artifact は FAIL を記録） |
| current evidence successor | `39ea603cee09a6340515959d1541869ffd53cf9b`（report + fresh-review Artifact のみ。executable/test inputsは不変） |
| final review Artifact successor | `afe911770bf6ea97e4abb244dc7f9f2d1f886933`（final review Artifactのみ。reviewed executable/report headは下記`2af3a145`） |
| working tree | executable/test evidence commit時点は clean（Artifact/report更新中の一時差分を除く） |
| candidate wheel | `spec_dock-0.2.3-py3-none-any.whl` |
| wheel SHA-256 / size | `7fba9d9c90322d4f996c1c3ac843d23959bafbe239af9f13ef3e3528530df593` / 967,319 bytes |
| installed origin | integration fixtureのisolated venvへcandidate wheelをinstall（source checkout fallbackなし） |
| production repair | `false`（S04 remediationは許可された2 test pathのみ） |

#### Opaque Lifecycle Matrix

| Fixture | Generic target | Import | Lifecycle body-open attempts | Decode errors | Typed promotion | ADR mirror promotion |
|---|---|---:|---:|---:|---:|---:|
| binary | root | pass | 0 | 0 | false | false |
| ZIP | Initiative | pass | 0 | 0 | false | false |
| invalid UTF-8 `.md` | Epic | pass | 0 | 0 | false | false |
| NUL-bearing `.md` | Issue | pass | 0 | 0 | false | false |
| ADR-looking generic `.md` | Issue | pass | 0 | 0 | false | false |

The fixtures are imported through the projected public `artifact import file` command before measurement. The measured guard is a fresh instance after a separate sensitivity negative and intercepts `Path.open`, `Path.read_text`, `Path.read_bytes`, `builtins.open`, and `io.open`. Generic destinations are not read, hashed, decoded, or ZIP-inspected while the lifecycle guard is active. `validate`, dependency check, `sync`, active-manifest loading, and context-pack generation completed with no generic body access; ADR mirror contains only the typed baseline.

#### Projection and Context Equivalence

- Required projection path set was asserted complete: `.agent/index-all.json`, `.agent/index.json`, `.agent/tree-all.json`, `.agent/tree.json`, `.agent/deps-issues.json`, `tree-all.puml`, `tree.puml`, `deps-issues.puml`, `deps-raw.puml`, `dashboard.md`, and `active/context-pack.md`.
- Before/after generic import snapshots, dependency JSON output, context pack, typed/blank artifact names, and ADR mirror entries were equal. Only the named JSON `generated_at` field is normalized; non-JSON projections and context/deps text are exact comparisons.
- Generic filenames and body sentinels were absent from generated projections; no generic artifact became typed, blank, canonical, or an ADR mirror source.

#### Compatibility Regression Evidence

| Suite / collected nodes | Result |
|---|---|
| `tests/cli_runtime/test_artifact_import_s04.py` (including `tc-346-s04-003` generic-versus-legacy barrier race) | 27 passed（`8ef9aab38d92165e865a7336f2b385126e979da3`） |
| `tests/cli_runtime/test_artifact_import_chatgpt_output.py` | 4 passed / 11.76s |
| `tests/cli_runtime/test_workbench.py` | 18 passed / 32.53s |
| `tests/cli_runtime/test_artifact_import_file.py` | 7 passed / 7.34s |
| `tests/cli_runtime/test_runtime_new_doc_s09.py -k artifact` (6 collected nodes) | 6 passed / 0.24s |
| `tests/unit/application/test_import_file_artifact.py tests/unit/presentation/test_artifact_import_file.py` | 34 passed / 0.27s |
| `tests/integration/test_epic_00343_distribution.py -k 'dogfood or opaque or compatibility'` | 2 passed / 17.40s |
| full integration distribution file | 13 passed / 33.68s（`39ea603cee09a6340515959d1541869ffd53cf9b`のclean worktree） |

No existing public filename, result field, selector, digest/count contract, or Workbench source-wins expectation was changed. Shared-slot concurrency now includes generic import versus a legacy blank creator under a fixed clock; both outputs receive distinct slots and preserve the sentinel/source bytes.

#### Fresh-Update-Dogfood Matrix / dogfood

| Check | Result |
|---|---|
| exact disposable checkout revision | candidate HEAD above, detached and clean before update |
| existing `epic-00343/.workbench/README.md` before/after update | absent / absent |
| installed CLI update | pass |
| provider source and canonical Initiative/Epic/Issue bytes | unchanged |
| future Issue shell | pass; README byte-equal to wheel Issue template and tracked |
| generic import | pass; `storage_identity=generic`, `canonical=false`, source ignored/untracked and bytes preserved |
| projected `validate` / `sync --no-github` | pass / pass |
| exact expected status manifest | pass; only known managed runtime update paths for update-only and future node tracked subtree plus generic destination for future flow |
| disposable cleanup / real provider worktree | pass / removed; HEAD and status unchanged |

The no-backfill negative injects the forbidden Epic README in the disposable checkout and observes a path-specific assertion failure before removing it. The future-flow privacy oracle scans stdout/stderr, flattened JSON values, and bounded `.agent` provenance files; expected repository-relative source is allowed while absolute checkout/source paths, body text, digest, byte count, derived marker, and sensitive field names are rejected.

#### Provider-to-Dogfood Projection Manifest

- Wheel/provider managed roots `docs`, `templates`, `scripts`, and `system` were compared byte-for-byte with the projected `spec-dock/{docs,templates,scripts,system}` tree after update.
- Projection parity: pass. Unexpected managed files: none.
- Update-only status manifest: `spec-dock/scripts/spec_dock_runtime/application/import_file_artifact.py` and `spec-dock/scripts/spec_dock_runtime/domain/artifacts.py` only (known provider-managed refresh paths).
- Future-flow status manifest: the same two managed refresh paths plus the dynamically created future Issue subtree (`.meta.json`, Workbench README, requirement/design/plan/report, `artifacts/rules.md`, and imported generic destination).
- Provider source writes from the consumer: zero; real provider source tree and status remained unchanged.

#### Step Contract Closure / S04

| Closure / test ID | Evidence | Result |
|---|---|---|
| `tc-346-s04-001` / `CL-346-AC-009` / `CL-346-EC-013` | five public generic imports, fresh lifecycle body-open spy, zero opens/decode errors, no ADR promotion | pass |
| `tc-346-s04-002` / `CL-346-AC-009` | complete projection/context/deps/ADR/typed set equivalence with named timestamp normalization | pass |
| `tc-346-s04-003` / `CL-346-AC-013` / `CL-346-EC-014` | compatibility suites and generic-versus-legacy shared-slot barrier race | pass |
| `tc-346-s04-004` / `CL-346-AC-006` / `CL-346-CON-004` | exact disposable update, provider→projection parity, no-backfill negative, exact status/cleanup | pass |
| `tc-346-s04-005` / `CL-346-AC-006` | future shell + ignored generic import through projected runtime, privacy scan, validate/sync, expected diff | pass |
| S04 step contract | allowed test-only paths, production repair false, real worktree clean at `8ef9aab38d92165e865a7336f2b385126e979da3` | pass（final ChatGPT Pro exact-head review PASS） |

#### Test Contract Closure / S04

- Red/alternative evidence: pre-existing S04 lifecycle tests were Green before remediation; initial ChatGPT review identified missing closure sensitivity rather than a production failure. The remediation tests are bounded negatives for body access, no-backfill, privacy, and cross-command slot races.
- Green evidence: commands and counts are recorded above; `uv run ruff check tests/cli_runtime/test_artifact_import_s04.py tests/integration/test_epic_00343_distribution.py` and `git diff --check` passed; `./spec-dock/scripts/spec-dock validate` reported `nodes=217`; `sync --no-github` completed with active unchanged.
- Refactor guardrail: no production code, generic body classifier, new snapshot framework, or canonical dogfood data was changed.

#### Delegated Worker Evidence / S04

| Role | Changed paths | Verification | Parent integration decision |
|---|---|---|---|
| `dev-coder` | `tests/cli_runtime/test_artifact_import_s04.py`, `tests/integration/test_epic_00343_distribution.py` | S04 27 passed; dogfood 2 passed; compatibility 29 passed; nearest artifact 6 passed; units 34 passed; full integration 13 passed / 33.68s; ruff/diff-check pass | accepted; test-only remediation, no material production decision beyond approved plan |

#### S04 ChatGPT Pro review gates

- Initial code review session: `iss346-s04-code-review-aug2`, exact head `89480b1ef37fa433d398ccc983dd60c716599079`, `requested=Pro; resolved=Pro; verified=yes`; Artifact `artifacts/20260801t230138z-chatgpt-output-20260802t-s04-code-review-initial.md` (SHA-256 `11a5b3627834ccfa606cde85ddcb5074861a650db2cfab2a01bd9b650a92ba49`). Verdict `FAIL` with P0=0/P1=3/P2=1/P3=0. Findings were limited to report exact-head evidence, provider projection/expected diff, generic-versus-legacy slot race, and projected dogfood privacy scan; no production defect or public contract change was identified.
- Remediation commit: `0c510e2137a6b211dd7a0d881f0c7d2190fdff97`; the first report correction `4565f183` was report-only and was the target of fresh review session `iss346-s04-fresh-review-aug2`. That review Artifact `artifacts/20260802t001217z-chatgpt-output-20260802t-s04-code-review-remediation.md`（SHA-256 `2f6b10d05d07ae0844cce3b4ff1a92e104523983bcaddc341139b3e79f8d33a0`、10,545 bytes）はP0=0、P1=2、P2=2、P3=0でFAILし、(a) reportのexecutable/test headとreviewed report-only successorの分離、(b) generic/legacy実共有slotの厳密検証、(c) JSON raw formatting保持、(d) printable body/count漏洩sentinelを要求した。
- 第二 remediation commit `8ef9aab38d92165e865a7336f2b385126e979da3` は許可された2つのtest pathだけを変更し、production parserと`scan_artifact_slot_ledger`によるslot集合検証、top-level `generated_at`だけのraw byte置換、printable body/count sentinelとcontrolled negativeを追加した。`8ef9aab38d92165e865a7336f2b385126e979da3` が現在のS04 executable/test evidence headであり、`4565f183` はその前段のreport-only successorである。`8ef9aab38d92165e865a7336f2b385126e979da3` を対象にfresh exact-head ChatGPT Pro reviewを取得し、P0〜P3全て0であることを確認するまでS04 closureを完了しない。
- final exact-head review session `iss346-s04-final-code-review` は `requested=Pro; resolved=Pro; status=already-selected; strategy=select; verified=yes`、reviewed head `2af3a145ec1a29e05f677d13ee20d53e55f38e3f`、executable/test head `8ef9aab38d92165e865a7336f2b385126e979da3`、report/evidence successor `39ea603cee09a6340515959d1541869ffd53cf9b` を確認し、P0=0、P1=0、P2=0、P3=0、`review_status=pass` を返した。Artifact `artifacts/20260802t003003z-chatgpt-output-20260802t-s04-code-review-final.md`（SHA-256 `38bad4e4b17b5ddb16542ce8566f8f63dd47fd5d1ba89413aecebf96ed2ba7be`、8,797 bytes）へ保存した。`afe911770bf6ea97e4abb244dc7f9f2d1f886933` はこのArtifactだけを追加したevidence successorであり、executable/provider/test inputsは不変である。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-07-29 HH:MM - HH:MM）

#### 対象
- Step: S01, S02, ...
- AC/EC: AC-___, EC-___
- 計画上の出典（Planned source）:
  - `plan.md` section:
  - closure ids:

#### 実施内容
- ...

#### 実行コマンド / 結果
```bash
<command>

<result>
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S01 | 赤フェーズ / 代替証跡（Red / alternative） | red-required / covered-existing / inspect-only / manual-required | ... | `command` / 文書点検（docs inspection） / 手動記録（manual record） | pass / approved-no-op / fail / blocked | ... |
| S01 | 緑フェーズ（Green） | ... | ... | `command` / 点検（inspection） / 手動記録（manual record） | pass / fail / blocked | ... |
| S01 | リファクタリング（Refactor） | guardrail satisfied / no refactor needed | ... | 差分点検（diff inspection） / command | pass / approved-no-op / fail / blocked | ... |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S01 | none / ... | implementation / review / QA / user report | recorded / added test / deferred / amended plan | tc-001 / new | yes / no | ... |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S01 | tc-001 | ... | ... | pass / approved-no-op / fail / blocked | ... |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| tc-001 | S01 | yes | red-required / covered-existing / inspect-only / manual-required | ... | ... | pass / approved-no-op / fail / blocked | ... |

- `closure id / test id` は Spec-Locked Closure Index の `id` を指す。別 alias を使う場合は `Closure Delta` で対応を記録する。

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| tc-001 | S01 | ... | pass / approved-no-op / fail / blocked | ... |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none / added / removed / changed / alias-mapped | tc-001 | tc-001 / test-name | tc-001 | ... | yes / no | yes / no |

#### ワークフロー単位の named role 許可（Workflow-Scoped Authorization）
`workflow_issue.md` is the policy source for workflow-scoped authorization. This report records observed authorization source, boundary, expiry, and denied / unavailable / host conflict handling only.

Authorization source は、ユーザーによる SpecDock workflow 利用依頼でよい。範囲は active repo/worktree、active SpecDock scope、current session、SpecDock-defined named roles、documented role responsibility に限る。この section は role ごと・phase ごとの追加承認 gate ではなく、scope 内の named role 利用前に追加許可を求める根拠にしてはならない。

別途確認が必要なのは scope expansion、破壊的操作、外部公開、credential を伴う外部 mutation、private external system、SpecDock workflow 外の role 利用である。unavailable / denied / host conflict は fail-closed とし、fresh `passed` reviewer gate の代替にしてはならない。

| 許可元（authorization source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可 / host conflict 理由（denied / unavailable / host conflict reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| ワークフロー利用依頼 / 明示承認 / なし（user request to use SpecDock workflow / explicit approval / none） | ... | iss-00346 | 現在セッション（current session） / ... | spec-reviewer / code-reviewer / qa-reviewer / read-only specialist | 範囲: active repo/worktree、active SpecDock scope、current session、SpecDock-defined named roles、documented role responsibility。破壊的操作 / 外部公開 / credentialed external mutation / scope expansion / private external system use / out-of-workflow role は含めない | 完了 / セッション終了 / scope 変更 / host policy conflict / user revocation（issue complete / session end / scope change / host policy conflict / user revocation） | none / denied / unavailable / host conflict | 続行 / separate-confirmation exception は user に確認 / block gate / record waiver request |

#### 実装委任ゲート（Implementation Delegation Gate）
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | delegated / approved-local-execution / degraded mode | multi-layer / shipped scaffold / pattern analysis / integration / large worker scope / none | repo-analyst / dev-coder / doc-writer / N/A | ... | ... | ... | ... | ... | ... | worker summary / changed files / verification / risks / integration decision | pass / fail / blocked |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01 | dev-coder / doc-writer / repo-analyst | ... | `path/to/file` | `command` -> pass / docs-only inspection -> pass | pass / fail / unavailable / denied / waived / provisional | none / ... | accepted / rejected / needs follow-up |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| S01 | unavailable / denied / host conflict / impossible because ... | approval source / risk accepted: yes / no | `path/to/file` | ... | ... | `command` -> pass / docs-only inspection -> pass | reviewer role + passed / failed / unavailable / denied / waived / provisional | blocked / incomplete / waived with explicit risk acceptance / next action |

#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）
Lite は specialist / fallback evidence を必須化しないが、not applicable / skip reason を記録する。Standard は specialist evidence、skip reason、または manual fallback を記録する。Strict / Critical は specialist evidence または明示的な manual fallback を記録し、skip reason だけでは readiness evidence にしない。

| グレード（Grade） | 必要な専門家 / 代替（required specialist / fallback） | 使用状況（usage） | 証跡（evidence） | 鮮度 spec-reviewer 判定（fresh spec-reviewer verdict） | 実行可否（execution readiness） |
|---|---|---|---|---|---|
| `standard` | `system-architect / implementation-planner / manual fallback` | manual fallback used; named `system-architect` / `implementation-planner` not used | 既存parent Epic architecture、Issue 344/345 approved R/D/P/report、accepted ADR 3件、provider/build/update/runtime/test sourceをmain orchestratorが照合し、external ChatGPT Pro planning ZIPをadvisory draftとして採用した。新architectureを決めず既存patternを統合検証するIssueであるためnamed architecture specialistを省略。fresh `spec-reviewer` findingsはmain orchestratorが正本修正した | final verdict `(pass)`; findings 0 | ready |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| planning | final deliverables gate | spec-reviewer | fresh | pass | no | execute approved plan | `iss346_final_deliverables_rereview`; findings 0; canonical R/D/P/report and completed onboarding reviewed |
| S04 | exact-head implementation gate | ChatGPT Pro with current `code-reviewer` Developer Instructions | fresh | pass | no | close S04 | `iss346-s04-final-code-review`; reviewed head `2af3a145ec1a29e05f677d13ee20d53e55f38e3f`; P0/P1/P2/P3=0 |
| S90 | documentation/spec alignment gate | ChatGPT Pro with current `spec-reviewer` Developer Instructions | fresh | fail | yes | apply bounded report/plan trace correction and obtain fresh exact-head review | session `iss346-s90-spec-review`; reviewed head `1364d62ca7a3e0ff42e7fe771b8a869cf54697bb`; Artifact `artifacts/20260802t011550z-chatgpt-output-s90-docs-spec-review.md`; P1=3 (projection-scope interpretation, S02-S04 EAL dispositions, Candidate 3 pending/current-state contradiction) |

#### マイルストーン / commit 候補ゲート（Milestone / Commit Candidate Gate）
| マイルストーン / step | クロージャ状態（closure state） | コミット候補 / コミット範囲（commit candidate / scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S01 | committed / approved-no-op | ... | <hash or final ledger reference> | `git status --short` -> clean | ... | ... | ... | ... |
| S90 | implementation committed / review pending | provider docs + managed projection + status manifest | `fa05765177c6cee71d0cea09cb1b1a8285a89702`, `6b815c9c`, `870846fda494f7ab76af0d1e913a7a508bd14099` | each commit clean; current report update pending | docs gap resolved within allowlist; S99 not claimed | docs/projection parity, token scan, validate/sync | `git diff --check`; `cmp`; focused docs parity test | fresh S90 ChatGPT Pro spec review required |

#### 変更したファイル
- `path/to/file1` - ...
- `path/to/file2` - ...

#### コミット
- <hash> <message>

#### メモ
- ...

---

### セッションログ（2026-07-29 HH:MM - HH:MM）

#### 対象
- Step: ...
- AC/EC: ...

#### 実施内容
- ...

---

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| provider docs / managed projection / status manifest / Issue・Epic trace | yes | doc-writer + main orchestrator | pre-step Artifact `artifacts/20260802t004508z-chatgpt-output-20260802t-s90-docs-prestep.md`; provider commit `fa05765177c6cee71d0cea09cb1b1a8285a89702`; projection commit `870846fda494f7ab76af0d1e913a7a508bd14099`; status manifest commit `6b815c9c`; `cmp` parity、required-token scan、docs parity unit 1 passed、`validate nodes=217`、`sync --no-github` pass; first exact-head review Artifact `artifacts/20260802t011550z-chatgpt-output-s90-docs-spec-review.md` | first review fail（P1=3）。D-005/plan §12.3、EAL-007〜013、Epic stateをboundedに補正してfresh reviewへ戻す |

#### S90 documentation-impact resolution

- 調査時点のpushed HEADは`ef467c1b84d9d7dfce64c6c4d98bcea5c560fc81`。S90 pre-stepは既存Workbench/no-backfill/privacy/opaque文言を維持しつつ、(1) Linux `O_TMPFILE` fail-closed/no named-temp fallback、(2) macOS staged descriptor/`fclonefileat`/cleanup warningとaccepted same-UID exclusion、(3) ordinary fast laneとexplicit `--run-full-regression` lane、(4) staleなIssue/Epic EAL traceの補正を要求した。
- provider-firstで変更したファイルは`src/spec_dock/assets/spec_dock/docs/README.md`と`guide.md`のみ（`fa05765177c6cee71d0cea09cb1b1a8285a89702`）。provider→consumer updateで`spec-dock/docs/README.md`、`spec-dock/docs/guide.md`および既存provider runtimeのmanaged mirror `spec-dock/scripts/spec_dock_runtime/application/import_file_artifact.py`、`spec-dock/scripts/spec_dock_runtime/domain/artifacts.py`を同期した（`870846fda494f7ab76af0d1e913a7a508bd14099`）。S04 expected status manifestはdocs 2 pathを追加した（`6b815c9c`）。consumer docsを手編集していない。
- S04 reportのcandidate-wheel status manifestが先に示していたruntime mirrorは、S90で新規修復したものではなく、S04のaccepted provider sourceをチェックイン済みdogfoodへ遅れて同期したprojection correctionである。D-005とplan §12.3でこの境界を明示し、runtime behaviorの新規変更・production repair=falseを維持する。
- `README.md`/`guide.md`/`reference_naming.md`/`rules/root/artifacts.md`のproviderとprojectionはbyte-identical、stale `deferred.*Issue #346`文言は除去、required safety/test-lane tokensは存在する。`uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_mirror_docs_match_provider_assets -q` は1 passed、`./spec-dock/scripts/spec-dock validate` は`nodes=217`、`sync --no-github` はactive unchangedで完了した。
- S90時点ではS99を完了済みとは主張しない。S90 fresh docs/spec review後に、S99のfast/full、validate/sync、single-thread QA/code/spec review、PR handoffを実施する。

#### S90 first exact-head review disposition

- Session `iss346-s90-spec-review`は`requested=Pro; resolved=Pro; status=already-selected; strategy=select; verified=yes`で、GitHub connector経由のbranch/HEAD確認後に実行された。reviewed HEADは`1364d62ca7a3e0ff42e7fe771b8a869cf54697bb`、Artifactは`artifacts/20260802t011550z-chatgpt-output-s90-docs-spec-review.md`（SHA-256 `08f443a5430d0adadd717a92cc62593752ab5f7c1803bc9539d4c2b8ea36f762`、4,585 bytes）。
- `review_status=fail`、P1=3。指摘は、S04 projection correctionをS90非コード差分から区別するplan/report trace不足、S02〜S04 ChatGPT evidence EAL不足、S90 pendingを飛び越したEpic Candidate 3状態の矛盾であり、provider docsの文言自体はbyte/content parityを満たすと確認された。
- 3件はD-005、plan §12.3 clarification、EAL-007〜013、Epic current-state correctionでboundedに対応する。runtime behaviorやproduct contractを拡張せず、fresh exact-head S90 reviewを取得するまでS90をcloseしない。

### 最終 QA ゲート（Final QA Gate）
| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| ChatGPT Pro with current `qa-reviewer` Developer Instructions | whole issue obligation coverage | S99で実施予定 | S99 final candidateへfresh push後にsingle-thread統合review | pending |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| ChatGPT Pro with current `code-reviewer` Developer Instructions | S04 exact-head code/evidence gate | S04 final review PASS（P0〜P3=0）をArtifact化済み。S90 docs影響は別spec reviewで確認 | `iss346-s04-final-code-review`; reviewed head `2af3a145ec1a29e05f677d13ee20d53e55f38e3f`; Artifact `artifacts/20260802t003003z-chatgpt-output-20260802t-s04-code-review-final.md`; final report successor `ef467c1b` | pass（S04） |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| ChatGPT Pro with current `spec-reviewer` Developer Instructions | S90 docs/spec/report alignment | first exact-head review FAIL（P1=3）をD-005/plan/EAL/Epic traceへ限定反映し、fresh reviewへ戻る | session `iss346-s90-spec-review`; reviewed head `1364d62ca7a3e0ff42e7fe771b8a869cf54697bb`; Artifact `artifacts/20260802t011550z-chatgpt-output-s90-docs-spec-review.md`; pre-step Artifact `artifacts/20260802t004508z-chatgpt-output-20260802t-s90-docs-prestep.md` | fail; re-review required |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| S01〜S04実装・S90 docs/projection更新 | S99 final bounded report + PR handoff | latest pushed headのPRとMerge Preparation記録へ転記 | pending S99 final candidate; human merge stop | pending |

## 遭遇した問題と解決 (任意)
- 問題: ...
  - 解決: ...

## 学んだこと (任意)
- ...

## 今後の推奨事項 (任意)
- ...

## 省略/例外メモ (必須)
- 2026-08-02 operator instructionにより、Issue 346のimplementation reviewはnamed reviewer sub-agent invocationではなく、current reviewer Developer Instructionsを渡したformal `chatgpt-use`によるsingle-thread ChatGPT Pro reviewを用いる。各呼び出し前にcommit/pushとlocal/remote head一致を必須とする。
- `artifacts/20260801t152944z-disc-chatgpt-assisted-execution-agreement.md`と、このIssue-local手続きを追加する`plan.md`/`report.md`差分はreview対象外とする。canonical requirement/design/acceptanceは変更していない。
