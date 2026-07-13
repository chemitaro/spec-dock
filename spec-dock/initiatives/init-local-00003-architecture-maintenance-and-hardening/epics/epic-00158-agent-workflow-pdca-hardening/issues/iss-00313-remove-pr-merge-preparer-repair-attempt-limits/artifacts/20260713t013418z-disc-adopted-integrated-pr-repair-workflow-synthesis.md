---
種別: disc
ID: "20260713t013418z-disc"
タイトル: "Adopted Integrated PR Repair Workflow Synthesis"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
親: ["iss-00313"]
関連: []
authority: "proposed"
derived_from:
  - "20260713t005118z-research-pr-merge-preparer-repair-limit-clarification-baseline.md"
  - "20260713t005207z-interview-same-family-repair-recurrence-continuation-policy.md"
  - "20260713t005848z-user-proposal-chatgpt-assisted-integrated-pr-repair-batch.md"
  - "20260713t011949z-research-chatgpt-consultation-integrated-pr-repair-workflow.md"
  - "20260713t012046z-interview-mandatory-chatgpt-consultation-scope.md"
  - "20260713t012618z-chatgpt-raw-integrated-pr-repair-workflow-consultation.md"
reflected_to:
  - "requirement.md authoring input"
  - "design.md authoring input"
  - "plan.md authoring input"
  - "report.md Evidence Adoption Ledger"
---

# 20260713t013418z-disc Adopted Integrated PR Repair Workflow Synthesis

## 位置づけ
- 用途: 集まった質問回答や調査をもとに、意思決定前の synthesis、選択肢、tradeoff、reflection proposal、ADR candidate triage、推奨反映先を整理する。
- authority default: `proposed`。通常は artifact type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は synthesis / reflection proposal / adoption target / ADR triage の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 人間から回答を引き出し、回答欄や未回答事項を管理する場合は `interview` を使う。
- 生ログや未整理の思考は `blank`、事実確認や外部根拠は `research`、長期判断の固定は `adr` に分ける。
- この doc は proposal / synthesis であり、issue `report.md` の observed evidence ledger ではない。採否の最終証跡は canonical docs / ADR / `report.md` Evidence Adoption Ledger に昇格する。
- doc が大きくなりすぎたら、質問回答は `interview`、事実調査は `research`、raw capture は `blank`、長期決定は `adr` へ分割する。

## 対象論点 (必須)
- 今回整理する論点:
  - Fixed repair-attempt limits撤廃、progress/stagnation契約、ChatGPT-Use mandatory consultation、runtime-owned body candidate adoption、integrated repair-batch authority、fallback、template compatibility。
- この synthesis が必要な理由:
  - Raw product-owner proposal、2件の回答、local research、ChatGPT raw reportの採用内容をcanonical Issue authoringへ一貫して渡すため。

## derived question sheets / research (必須)
- `interview`:
  - `20260713t005207z-interview-same-family-repair-recurrence-continuation-policy.md`: progress-based継続を採用。
  - `20260713t012046z-interview-mandatory-chatgpt-consultation-scope.md`: blocking/uncertainのみmandatory、clean/P2-P3-onlyは省略を採用。
- `research`:
  - `20260713t005118z-research-pr-merge-preparer-repair-limit-clarification-baseline.md`
  - `20260713t011949z-research-chatgpt-consultation-integrated-pr-repair-workflow.md`
- その他の根拠:
  - Product-owner raw proposal、ChatGPT raw browser transcript、current provider skill/templates、blocker-centric accepted ADR。

## synthesis (必須)
- 合意済みのこと:
  - P0=1、same P1=2、total=4の固定上限とsame-family immediate stopを廃止する。
  - New evidence、materially new strategy、falsifiable validation、expected observable deltaがある限り自律継続する。
  - Stagnationと既存authority/scope/external/observation/platform gatesではfail-closedで停止し、unresolved blockerをrisk acceptanceしない。
  - Blocking/uncertain completed reviewではChatGPT-Use consultationを必須にする。Cleanと明白なP2/P3-onlyは省略する。
  - ChatGPTはConsultation Receiptとschema-complete Markdown body candidateを返す。Runtime-generated front matter/H1/pathはlocal authorityとして保持する。
  - Repair batchがRaw Intake、family analysis、cross-family synthesis、integrated repair scope、design、plan、validation、results、commit/push、re-observation、progress ledgerのprimary source of truthとなる。
  - Per-family external `disc` repair unitは必須から外し、research/disc/interviewはoptional supporting evidenceとする。
  - Hard-unrecoverable consultationはhuman gate。Invocation単位の明示承認がある場合だけmanual fallbackを許可し、waiver/evidence gapをbatchへ記録する。
  - Legacy discussion templatesは今回同一body contractへ同期する。
- 未合意 / 未確定のこと:
  - User-intent blockerはnone。Field naming、exact section ordering、verification command selectionはIssue-local design/planで決定可能。
- source-grounded に解決できたこと:
  - Existing blocker-centric ADRはfixed-count廃止とstagnation gateを支える。Runtime codeは既にartifact identity/path生成を持つため、専用adoption helperは初期必須ではない。

## 選択肢 / tradeoff (必須)
- Option A:
  - Pros:
    - Adopted hybrid。Runtime identityを守りながらChatGPTの一括分析・authoringを利用し、batch authorityを統合できる。
  - Cons:
    - Candidate coverage/adoption検査とprogress判断の明示的evidenceが必要。
- Option B:
  - Pros:
    - ChatGPTにcomplete fileを直接書かせれば操作は短い。
  - Cons:
    - Runtime-owned identity/path/authorityを壊し、unsafe/stale claimを直接canonical surfaceへ混入させるため棄却。

## reflection proposal (必須)
- canonical docs / workflow / template / skill guidance へ反映すべき候補:
  - 上記合意をIssue requirement/design/planへ採用し、provider skill、openai.yaml、skill-local template、runtime artifact/discussion templatesとmirrorsを一貫更新する。
- まだ proposal に留める理由:
  - Canonical authoringとfresh spec-reviewer gateが未実施だから。

## adoption target / 採用先候補 (必須)
- `requirement.md`:
  - Observable continuation/stagnation、mandatory consultation scope、human gates、non-goals、acceptance criteria。
- `design.md`:
  - Exact-head/source-coverage trust boundary、body-only adoption、integrated batch information architecture、progress predicate。
- `plan.md`:
  - Provider-first edits、mirror/template parity、tests、manual scenario matrix、review gates。
- `ADR`:
  - Mandatory external consultationとintegrated repair-batch authorityをlong-lived trust-boundary candidateとしてtriageする。
- `report.md` Evidence Adoption Ledger:
  - 全research/interview/raw/synthesisの採用状態、raw transcriptはadvisory evidenceであること、canonical reflection結果。

## ADR triage / ADR candidate triage (必須)
- ADR candidate か:
  - yes
- hard to reverse:
  - yes
- surprising without context:
  - yes
- real tradeoff:
  - yes
- ADR 化しない場合の反映先:
  - N/A。Issue authoring中にexisting ADR amendmentかnew ADRとしてfacilitationへrouteする。

## 推奨案 (必須)
- ChatGPT raw analysis reportのhybrid案と全3推奨回答を採用する。これは夜間の固定上限停止を解消しつつ、stagnation、source coverage、exact-head、authority gateで無意味な無限反復を防ぐため。

## 推奨反映先 (必須)
- `requirement.md`:
  - Adopted behavioral contract全体。
- `design.md`:
  - Consultation/adoption/batch/progress trust boundary。
- `plan.md`:
  - Exact file inventoryとverification matrix。
- `ADR`:
  - `spec-dock-adr-facilitation`へhandoffしてaccepted blocker-centric ADRとの関係を判断する。
- `report.md` Evidence Adoption Ledger:
  - EALに全sourceと採用理由を記録する。

## 未採用 / deferred 理由 (必須)
- 未採用:
  - Fixed counts only removal、完全無制限、complete-file direct write、analysis-only、mandatory per-family disc、family-as-fingerprint、silent automatic fallback、all-completed-review mandatory consultation。
- deferred:
  - Dedicated atomic body-adoption helper、legacy template deprecation/removal。Manual smokeで必要性が確認された場合にfollow-up候補とする。

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - 本synthesisをcanonical authoringへ採用し、ADR facilitationでdurable trust-boundaryを記録する。
- 追加で作る artifacts:
  - Canonical authoring workflowが必要とするdraft evidenceとADR candidate/ADR。
