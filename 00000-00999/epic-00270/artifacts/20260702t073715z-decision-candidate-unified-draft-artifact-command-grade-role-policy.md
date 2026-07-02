---
種別: decision-candidate
ID: "20260702t073715z-decision-candidate"
タイトル: "Unified Draft Artifact Command and Grade Role Policy"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["epic-00270"]
関連:
  - "20260702t071230z-decision-candidate"
  - "20260702t054322z-research"
  - "20260702t060525z-research"
  - "20260702t062053z-disc"
  - "20260702t074332z-adr"
authority: "accepted via ADR"
derived_from:
  - "artifacts/20260702t071230z-decision-candidate-epic-planning-issue-draft-composition-workflow.md"
  - "artifacts/20260702t054322z-research-issue-planning-draft-strategy-analysis.md"
  - "artifacts/20260702t060525z-research-non-active-issue-draft-artifact-command-capability.md"
  - "artifacts/20260702t062053z-disc-pre-start-issue-concretization-management-model.md"
  - "Deep Consultant analysis, 2026-07-02"
  - "ChatGPT 5.5 Pro consultation, 2026-07-02"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_artifact_doc.py"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/assurance.py"
  - "spec-dock/docs/rules/issue/artifacts.md"
  - "spec-dock/docs/workflow_spec_authoring.md"
  - "spec-dock/docs/workflow_epic.md"
  - "spec-dock/docs/workflow_issue.md"
reflected_to:
  - "artifacts/20260702t074332z-adr-unified-draft-artifact-command-grade-role-policy.md"
  - "report.md"
---

# Unified Draft Artifact Command and Grade Role Policy

## 位置づけ

この artifact は、`20260702t071230z-decision-candidate-epic-planning-issue-draft-composition-workflow.md` を、ユーザー指摘、Deep Consultant、ChatGPT 5.5 Pro、現行コード確認で再分析した更新版である。

前回案は「全 grade の Issue に `draft-design` / `draft-plan` を作る」点では維持する。一方で、`composed draft` と `authored draft` を command layer で分ける考え方は弱める。最新版の判断候補では、command は profile template 由来の Issue-local draft artifact を作る機械的 surface に限定し、誰がどの深さで中身を濃くするかは workflow / skill / report evidence gate で扱う。

## 判断候補

proposed decision:

- `draft-design` / `draft-plan` 作成に、actor 別、specialist 別、深さ別の command を作らない。
- 統一 draft artifact creation surface は、現行の `new artifact draft-design --issue <issue-id>` と `new artifact draft-plan --issue <issue-id>` を中心にする。
- Epic Planning で全 downstream Issue の整合性を取る場合、Lite を含む全 grade で Issue-local `draft-design` / `draft-plan` を作成する。ただし artifact は evidence only であり、canonical `design.md` / `plan.md` ではない。
- `assurance compose` は canonical `design.md` / `plan.md` / `report.md` を更新する command として維持し、pre-start draft artifact 作成には使わない。
- `assurance compose-draft` や `issue prepare` / `epic prepare-issues` は、初期実装の必須 command にはしない。必要になった場合も、新しい意味を持つ command ではなく、既存 `new artifact draft-*` を呼ぶ thin wrapper / batch orchestration に留める。
- `composed draft` と `authored draft` の区別は command 名ではなく、同じ artifact の lifecycle / provenance / EAL state として扱う。

trigger:

- ユーザーから、system-architect / implementation-planner が作る draft も、正式版の前に作る draft も、結局は grade/profile に対応した template を出発点にするため、command を分ける意味が薄いのではないかという指摘があった。
- command は「どの actor がそのファイルを編集したか」を実質的に制御できない。actor 由来の責務は command option ではなく workflow / skill / evidence gate で管理する方が正確である。
- 既存実装にも `new artifact draft-design` / `draft-plan` があり、すでに `authorized_profile` に対応した `templates/issue-profiles/<profile>/{design,plan}.md` を render する profile-aware artifact surface になっている。

affected scope:

- Epic Planning workflow
- Issue Planning workflow
- Issue grade / authorized profile obligation
- `new artifact draft-design` / `draft-plan`
- `assurance classify`
- `assurance compose`
- Issue artifact front matter / evidence lifecycle
- `report.md` Evidence Adoption Ledger
- validation / smoke tests

## observed facts

- `spec-dock/docs/rules/issue/artifacts.md` は canonical `requirement.md` / `design.md` / `plan.md` / `report.md` を artifacts ではなく main orchestrator single-writer authority と定義している。
- 同じ rules は `draft-design` / `draft-plan` を Issue-only routing artifact とし、verified `.assurance.json` の `authorized_profile` に対応する profile template を source として render すると定義している。
- `create_artifact_doc.py` の現行実装は `draft-design` / `draft-plan` で valid `.assurance.json` を要求し、invalid / missing / stale では no-write fail-closed する。
- `create_artifact_doc.py` は `draft-design` / `draft-plan` について `templates/issue-profiles/<profile>/design.md` / `plan.md` を読む。actor は command input でも persistence contract でもない。
- `assurance.py` の `compose_assurance()` は profile template を canonical artifact に compose し、変更があれば canonical artifact と `.assurance.json` を更新する。これは evidence artifact 作成 surface ではない。
- `spec-dock-issue-planning` skill は grade 別に、Lite は低リスク根拠がある場合のみ、Standard は specialist 推奨、Strict / Critical は specialist 原則必須または manual fallback evidence 必須、Critical fallback は通常 blocked と定義している。
- 過去メモにも、Issue breakdown と draft planning artifacts を求められた場面で canonical issue docs と draft discussions/artifacts を混同した失敗が記録されている。この設計では、その失敗を command 増ではなく authority boundary と EAL で防ぐ。

## external consultation synthesis

Deep Consultant:

- 結論は「1つの統一 draft composition command」。actor 別、深さ別、specialist 別 command は不要。
- command は valid `.assurance.json` の `authorized_profile` に従って profile template を Issue-local artifact として生成するだけに限定するべき。
- `assurance compose` は canonical 更新 command なので Epic Planning の pre-start draft 作成には使うべきではない。
- Strict / Critical は draft の存在だけでは不足し、specialist enrichment または manual fallback evidence が必要。

ChatGPT 5.5 Pro:

- 結論は「1つの統一 draft artifact creation surface」。CLI を `composed draft` と `specialist-authored draft` に分けるべきではない。
- ただし surface 名としては、既存の `new artifact draft-design` / `draft-plan` を中心にする方がよい。`compose` は既に canonical 更新の語彙であり、`assurance compose-draft` を主導線にすると canonical/evidence 境界が曖昧になりやすい。
- specialist-authored という command 名は、実際には command が specialist を呼ぶわけでも編集者を保証するわけでもないため、fake authorship のリスクがある。
- `composed` / `authored` の違いは lifecycle / provenance state として扱い、artifact は evidence のまま `report.md` EAL で採用、部分採用、棄却、stale を管理するべき。

integrated judgment:

- Deep Consultant と ChatGPT は、command を actor 別に分けない点で一致した。
- 差分は command surface 名である。現行実装・既存 docs・command proliferation の抑制を重視し、初期実装では ChatGPT の案を強く採用する。
- したがって、最小正解は `new artifact draft-design` / `draft-plan` の強化であり、`assurance compose-draft` は導入しないか、導入しても将来の thin wrapper に限定する。

## ambiguity / constraint

- Epic Planning で複数 Issue をまとめて具体化するには、Issue Start 前でも cross-Issue 整合性を確認できる draft design / draft plan が欲しい。
- 一方で、Issue Start 前に canonical `design.md` / `plan.md` を具体化すると、正本と draft の境界が崩れる。
- command は「誰が編集したか」「どの専門家が見たか」を信頼できる形で保証できない。
- そのため、command は生成された artifact の source / profile / assurance contract を記録し、actor obligations は workflow / report / reviewer gate に置く必要がある。
- `.assurance.json` の source binding が現状では `requirement.md` / `design.md` / `plan.md` を含むため、pre-start draft のために canonical placeholders を触ると stale 判定が起きる可能性がある。この点は別途実装設計で解く必要がある。

## options considered

Option A: actor / depth 別 command を作る

- 例: `draft-design-specialist`、`compose-authored-draft`、`--by system-architect`。
- 却下理由: command が actor を実際に制御できず、authorship claim が偽の安心を生む。CLI が増え、coding agent がどの command を使うべきか迷いやすい。

Option B: `assurance compose-draft` を主導線にする

- 利点: `--artifact all` で design / plan をまとめて作りやすい。Deep Consultant はこの案を推した。
- 注意点: `assurance compose` は canonical compose の語彙として既に存在するため、draft artifact と canonical artifact の境界が曖昧になる。
- 採否: 初期実装では見送り。将来必要なら、既存 `new artifact draft-*` を呼ぶ thin wrapper とし、actor 由来の意味を持たせない。

Option C: 現行 `new artifact draft-design` / `draft-plan` を統一 primitive として強化する

- 採用。
- command は valid assurance contract と `authorized_profile` に基づき、Issue-local artifact を1つ作る。
- Epic Planning が全 Issue に対して design / plan の両 draft を必要とする場合は、workflow がこの primitive を2回呼ぶ。将来の batch wrapper はあってよいが、semantic authority はこの primitive に置く。

Option D: Issue Start 後に個別 Issue Planning だけで draft を作る

- 部分採用。
- 各 Issue の正規 design / plan は Issue Planning で具体化する。
- ただし Epic Planning 段階でも全体整合性のために Issue-local draft artifact は作ってよい。これは canonical docs ではなく handoff evidence である。

## recommended command semantics

`new artifact draft-design --issue <issue-id>` / `new artifact draft-plan --issue <issue-id>`:

- explicit `--issue` で non-active Issue を対象にできる。
- active Issue であることを要求しない。
- Issue scope 以外では fail する。
- valid かつ non-stale `.assurance.json` を要求する。
- `authorized_profile` から `templates/issue-profiles/<profile>/design.md` または `plan.md` を読む。
- target Issue の `artifacts/` 配下に timestamped artifact を作る。
- canonical `requirement.md` / `design.md` / `plan.md` / `report.md` は変更しない。
- actor / specialist / depth flag を持たない。
- no-write fail-closed を徹底する。

`assurance compose`:

- canonical compose 専用として維持する。
- Epic Planning の pre-start draft artifact 作成では使わない。

future wrapper:

- `issue prepare` / `epic prepare-issues` / `compose-draft` 相当は、必要になった場合のみ導入する。
- wrapper は `.assurance.json` の作成確認、`draft-design` / `draft-plan` の連続作成、path index 出力を行うだけにする。
- wrapper は actor assignment、reviewer pass、canonical adoption を主張しない。

## lifecycle / metadata model

artifact creation 時点で artifact または companion metadata に残すべき情報:

- `artifact_type`: `draft-design` または `draft-plan`
- `authority`: `evidence`
- `not_canonical`: `true`
- `scope_type`: `issue`
- `scope_id`: Issue id
- `draft_lifecycle_state`: `template_rendered`
- `draft_origin`: `profile_template`
- `authorized_profile`: `lite | standard | strict | critical`
- `profile_basis`: `.assurance.json`
- `assurance_contract_path`
- `assurance_contract_status`: `valid`
- `source_template`
- `source_requirement_hash`
- `source_assurance_contract_hash`
- `intended_targets`: `design.md` or `plan.md`
- `adoption_status`: `unreviewed`
- `reflected_to`: `[]`

workflow / report / EAL で管理する情報:

- `draft_authoring_state`: `not_applicable | pending | orchestrator_edited | specialist_enriched | specialist_authored | manual_fallback | skipped | blocked | stale | rejected | adopted | partially_adopted`
- `responsible_role`: `main-orchestrator | system-architect | implementation-planner | manual-fallback | none`
- `specialist_obligation`: `not_applicable | optional | required | required_or_blocked`
- `specialist_result`: `produced | unavailable | denied | skipped | stale | rejected`
- `fallback_reason`
- `fallback_approval`
- `diff_guard_result`
- `evidence_adoption_ledger_entry`
- `promotion_eligibility`

重要な境界:

- artifact metadata は「何をどの profile/template から生成したか」を記録する。
- report / EAL は「誰が濃くしたか、なぜ specialist を使った/使わなかったか、採用したか」を記録する。
- canonical docs は、main orchestrator が EAL を通じて採用し、fresh `spec-reviewer` pass を得るまで更新・昇格しない。

## grade responsibilities

全 grade 共通:

- Epic Planning で downstream Issue をまとめて具体化する場合、`draft-design` と `draft-plan` は両方作る。
- draft artifact は canonical docs ではなく evidence only。
- draft artifact の存在だけでは Issue Planning 完了、Spec Authoring Gate pass、Issue execution readiness にはならない。

Lite:

- specialist obligation: `not_applicable`
- `draft-design` / `draft-plan` は薄い alignment scaffold でよい。
- system-architect / implementation-planner は不要。
- `report.md` には Lite 根拠、specialist not applicable、残リスク、fresh reviewer evidence を残す。

Standard:

- specialist obligation: `optional`
- system-architect / implementation-planner は推奨だが必須ではない。
- 使わない場合は、確認した source、skip reason、manual authoring evidence、残リスクを `report.md` に残す。
- reviewer gate と EAL が十分なら、specialist 未使用だけで blocked にはしない。

Strict:

- specialist obligation: `required_or_fallback`
- design draft は system-architect、plan draft は implementation-planner の enrichment / authorship を原則必須にする。
- unavailable / denied / host constraint の場合は manual fallback evidence を要求する。
- skip reason だけでは readiness gate を満たさない。

Critical:

- specialist obligation: `required_or_blocked`
- specialist output がない場合は原則 blocked。
- manual fallback は、明示的な risk acceptance、追加 reviewer / manual gate、rollback / safety evidence がある場合だけ例外的に許容する。
- unresolved destructive / security / privacy / external mutation risk が残る場合は進めない。

## validation / smoke tests

command-level:

- `new artifact draft-design --issue <non-active-id>` が valid `.assurance.json` で Issue-local artifact を作る。
- `new artifact draft-plan --issue <non-active-id>` が valid `.assurance.json` で Issue-local artifact を作る。
- Lite / Standard / Strict / Critical の各 profile で、対応する profile template が render される。
- missing / invalid / stale `.assurance.json` では no-write fail-closed する。
- Epic / Initiative scope で `draft-design` / `draft-plan` は fail する。
- command 実行後も canonical `requirement.md` / `design.md` / `plan.md` / `report.md` の hash が変わらない。
- command は active context を変更しない。
- actor / specialist flag がなくても workflow 上必要な情報を report / EAL で表現できる。

workflow-level:

- Lite は specialist not applicable と reviewer / EAL evidence で readiness 判定できる。
- Standard は specialist evidence または documented skip/manual evidence で readiness 判定できる。
- Strict は specialist evidence または manual fallback evidence がない場合に fail する。
- Critical は explicit fallback approval / risk acceptance なしでは blocked のままになる。
- stale / rejected / superseded / blocked draft は promotion evidence として使えない。
- pre-start draft artifact だけでは Issue canonical design / plan completion や execution readiness にならない。
- Epic handoff package は各 downstream Issue の `draft-requirement` / `draft-design` / `draft-plan` path index、または明示的な blocked / skip / fallback evidence を持つ。

## adoption target

`requirement.md`:

- Issue grade / risk facts / Japanese-first artifact authoring requirement に、全 grade draft artifact 生成と actor obligation の関係を必要な範囲で反映する。

`design.md`:

- command surface は既存 `new artifact draft-design` / `draft-plan` を中心にする。
- `assurance compose` は canonical compose 専用とし、draft artifact 作成の主導線から外す。
- `composed` / `authored` は command ではなく lifecycle / metadata / EAL state として設計する。

`plan.md`:

- first implementation では、`new artifact draft-*` 強化、assurance source binding の安定化、artifact metadata、workflow docs / skills 更新、validation tests を優先する。
- `compose-draft` / `issue prepare` / `epic prepare-issues` は optional wrapper として後続判断に回す。

`ADR`:

- command responsibility と workflow responsibility の境界は ADR 化候補である。
- 採用する場合の ADR 主旨は「draft artifact command は actor semantics を持たず、actor obligations は grade-aware workflow / EAL が担う」とする。

`report.md` Evidence Adoption Ledger:

- この判断候補を採用した場合、前回 `20260702t071230z-decision-candidate` を superseded とし、本 artifact を latest decision evidence として記録する。

## risk if wrong

- command を増やさなすぎる場合、Epic Planning で多数 Issue の draft design / draft plan path を作る操作が冗長になる。
- command を増やしすぎる場合、actor semantics を command 名に押し込んで fake authorship / authority leak を生む。
- `compose` 語彙を draft artifact に流用すると、canonical compose と evidence draft の区別が曖昧になる。
- `.assurance.json` source binding の問題を放置すると、pre-start draft 用の contract が placeholder 変更で stale になり、workflow が不安定になる。
- Lite にも draft を作る方針を過剰に重く実装すると、軽量 Issue の速度を損なう。
- Strict / Critical で draft artifact の存在だけを readiness evidence と誤認すると、専門的な設計検証が不足する。

## rollback or revisit

- `new artifact draft-*` primitive だけでは Epic Planning の反復作業が過度に冗長だと実測された場合、thin wrapper を再検討する。
- wrapper を導入する場合も、actor assignment / reviewer pass / adoption を主張しない。
- `.assurance.json` source binding を requirement-only stage と planning stage に分ける設計が固まったら、この判断候補の validation section を更新する。
- Strict / Critical の fallback が実運用で重すぎる場合、Issue grade matrix 側で調整し、command surface は変えない。

## status / disposition

status:

- accepted via ADR

disposition evidence:

- Deep Consultant と ChatGPT 5.5 Pro は、command を actor 別に分けない点で一致した。
- ChatGPT 5.5 Pro は、既存 `new artifact draft-design` / `draft-plan` を統一 surface とする案を推奨した。
- ローカルコード確認でも、`new artifact draft-*` は既に profile-aware artifact surface、`assurance compose` は canonical compose surface である。
- よって前回案のうち、`compose-draft` を主導線にする部分は superseded とし、既存 `new artifact draft-*` primitive の強化へ寄せる。
- ユーザーが方針採用を明示し、`artifacts/20260702t074332z-adr-unified-draft-artifact-command-grade-role-policy.md` として accepted ADR 化した。
