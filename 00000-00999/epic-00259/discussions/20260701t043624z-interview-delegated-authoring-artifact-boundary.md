---
種別: interview
ID: "20260701t043624z-interview"
タイトル: "Delegated Authoring Artifact Boundary"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
親: ["epic-00259"]
関連: []
scope: "<initiative | epic | issue | local-topic>"
scope_id: "epic-00259"
created_at: "2026-07-01THH:MM:SSZ"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00259-artifacts-directory-future-only-adoption/discussions/20260701t043248z-interview-artifacts-future-only-policy-boundary.md"
  - "/Users/iwasawayuuta/.codex/attachments/dbb970bc-ae71-4b5a-a1bd-88959357eade/spec-dock-phase2-artifacts-pack.zip"
  - "src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md"
  - "src/spec_dock/assets/spec_dock/docs/phase_design.md"
  - "src/spec_dock/assets/spec_dock/docs/phase_plan.md"
  - "src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/delegated_authoring.py"
reflected_to:
  - "../artifacts/20260701t055644z-adr-artifacts-future-only-command-unification.md"
---

# 20260701t043624z-interview Delegated Authoring Artifact Boundary

## 位置づけ
- 用途: 重要判断に関わる一つの質問を、回答前の source-grounded 正式質問シートとして作成し、回答後に同じ artifact を完成 record にする。
- authority default: `proposed`。ユーザー回答と採用判断を反映した後は、必要に応じて `user-approved` または `synthesized` に更新する。
- この artifact は answer capture / adoption target / reflection の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 技術的に調べられることは先に docs / code / tests / ADR / discussions / primary source を確認する。
- 一つの `interview` artifact には one essential question / 一つの本質的な質問だけを書く。回答によって新しい高影響な曖昧さが見つかった場合は、追加質問をこの file に増やさず、次の unanswered `interview` を作成する。
- trivial な yes/no は、重要な判断、後続反映、回答証跡が必要なら `interview` を使い、そうでなければ issue comment や `scratch` で足りる。
- 回答から複数質問の synthesis が必要になったら `disc`、追加調査が必要になったら `research`、長期判断が固まったら `adr` を新規作成する。

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - Phase 2 の `artifacts/` MUST 方針に対する例外範囲。
  - `design.md`:
    - delegated authoring の write boundary、diff guard、`new doc` / `new artifact` の責務境界。
  - `plan.md`:
    - Issue 07 で skills/docs をどこまで更新するか、または follow-up Issue / Epic を切るか。
  - `ADR`:
    - Option A の future-only policy に対する explicit exception / staged migration decision。
- chat 上の軽微な一問では足りない理由:
  - 現行 workflow は delegated authoring output を `discussions/` direct child として安全境界・diff guard・consent に組み込んでおり、変更すると runtime/domain/docs/tests にまたがる。

## 質問の目的 (必須)
- 対象者:
  - spec-dock maintainer / product owner。
- 何を明確にする質問か:
  - delegated authoring / sub-agent draft / scope-local direct-write output を、Phase 2 で `artifacts/` へ移すか、例外として `discussions/` に残すか。
- 回答が後続判断へ与える影響:
  - Issue 04 / 05 / 07 / 08 の scope、ADR の exception wording、workflow_spec_authoring / phase_design / phase_plan / delegated_authoring.py の変更有無が決まる。

## 質問 (必須)
- pressure-test question:
  - Option A により「新規 generic working artifact は `artifacts/` MUST」としましたが、既存の delegated authoring output は safety-critical な `discussions/` direct-child contract を持っています。この出力を Phase 2 の対象に含めますか。
- 質問:
  - delegated authoring / sub-agent draft / scope-local direct-write output は、Phase 2 で `artifacts/` へ移行しますか。それとも `draft-*` / ADR と同じく Phase 2 の例外として `new doc` / `discussions/` に残しますか。
- 回答してほしいこと:
  - 下の Option A / B / C のどれを採用するか、または近い案を指定してください。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - `workflow_spec_authoring.md`: sub-agent authoring output は target scope `discussions/` direct child の flat Markdown とされ、`new doc` generation と diff guard に結び付いている。
  - `phase_design.md` / `phase_plan.md`: delegated design/plan draft は `discussions/` direct child に 1 ファイルだけ作成し、post-run diff guard で naming rule を確認する。
  - `delegated_authoring.py`: diff guard は `scope_dir / "discussions"` を境界として評価する。
  - ZIP pack: Phase 2 は `draft-requirement` / `draft-design` / `draft-plan` と ADR を artifact template 対象外にしているが、delegated authoring output の扱いは明示していない。
  - 先行 interview: `discussions/` は compatibility-only legacy、新規 generic working artifact は `artifacts/` MUST、`new doc` は互換のため警告・失敗なしで残す方針を採用済み。
- local context で解決できたこと:
  - delegated authoring は単なる generic note ではなく、permission / consent / diff guard / evidence adoption gate の安全境界である。
  - Phase 2 でここを移す場合、docs だけでなく `delegated_authoring.py` と関連 tests も scope に入る。
- まだ人間判断が必要な理由:
  - ZIP pack の Issue 07 は skills/docs 更新を求めるが、delegated authoring の safety-critical write boundary を Phase 2 に含めるかどうかは source だけでは確定できない。

## 回答案 (必須)
- Option A:
  - Explicit exception for Phase 2: delegated authoring output は Phase 2 では既存 `new doc` / `discussions/` direct-child contract に残す。`artifacts/` MUST は generic manually-created working artifacts に適用し、delegated authoring migration は別 Issue / Epic で扱う。
- Option B:
  - Full migration in Phase 2: delegated authoring output も `new artifact` / `artifacts/` に移す。diff guard、consent wording、workflow docs、domain guard、tests をこの Epic の後続 Issue に含める。
- Option C:
  - Hybrid: manual delegated drafts は `artifacts/` に移すが、static adapter / diff guard が関わる system-architect / implementation-planner output は当面 `discussions/` に残す。

## Codex の分析 (必須)
- 判断軸:
  - Phase 2 の焦点を generic working artifact store に保つか、安全境界の再設計まで含めるか。
- tradeoff:
  - Option B は conceptual consistency が高いが、diff guard と delegated authoring safety model の再設計が必要になる。Option C は過渡期を細かく制御できるが、ルールが二重化して agent guidance が複雑になる。
- リスク:
  - delegated authoring boundary を不用意に動かすと、scope-local direct-write consent と post-run diff guard の安全性が下がる。
- 具体シナリオ / edge case:
  - `system-architect` が design draft を作成する場合、現行 docs では `new doc <type>` で `discussions/<ts>-...md` を作り、diff guard がその path だけを採用可能 evidence として確認する。

## Codex の推奨案 (必須)
- 推奨:
  - Option A。
- 理由:
  - Phase 2 の guardrail「既存 `new doc` を維持」「draft-* と ADR は対象外」と整合し、safety-critical delegated authoring contract をこの Epic に混ぜずに済む。`artifacts/` の標準化を先に完了し、delegated authoring migration は別の、より狭い設計判断として扱える。
- 未回答時の影響:
  - Issue 07 の skills/docs 更新範囲と ADR の exception wording を確定できない。

## ユーザー回答 (回答後に必須)
- answer capture:
  - Option B を採用する。
- 回答:
  - 「このEpicにおいて、アーティファクト、Artifactsディレクトリに移行をしてください。この時に必要な権限や検査や安全確認の境界ですね、などについても、バリデーションなどについても、切り替えを行ってください。」
- 回答日時:
  - 2026-07-01

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - `scratch` を artifacts template として残すか、Phase 2 では `blank` に統合して `new doc scratch` だけ legacy compatibility として残すか。

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `ADR`
  - `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - ユーザーが Option B を明示採用した。delegated authoring output も Phase 2 の `artifacts/` 移行対象に含め、permission / diff guard / validation / safety boundary も併せて切り替える。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - Phase 2 は generic manually-created working artifacts だけでなく、delegated authoring / sub-agent draft / scope-local direct-write output の標準配置も `artifacts/` へ移す。
- `design.md`:
  - delegated authoring の allowed write boundary、consent wording、diff guard、domain guard、validation は `discussions/` direct child から `artifacts/` direct child へ切り替える。
- `plan.md`:
  - Issue 07 だけでなく runtime/domain safety boundary と tests を含む後続 Issue に scope を反映する。既存 static adapter / diff guard の切替は独立した implementation slice として扱う可能性が高い。
- `ADR`:
  - Future-only adoption policy の例外ではなく、delegated authoring output も Phase 2 の migration target とする Decision を記録する。
- reflected_to 更新方針:
  - ADR draft 作成後に `reflected_to` を更新し、canonical docs へ採用した時点で report ledger に記録する。
- adoption reflection:
  - Option B は採用済み。これにより ZIP pack 原案よりも Epic scope は拡大し、delegated authoring safety model の切替も E-AC / plan に入れる必要がある。

## 条件付き補足 (必要な場合だけ)
- PlantUML 図:
  ```plantuml
  @startuml
  ' TODO: 質問依存、意思決定フロー、before/after、責務境界が必要なら追加する
  @enduml
  ```
- 詳細 tradeoff:
  - ...
- 後続 reflection proposal:
  - ...
- 追加で作る discussion docs:
    - ...
