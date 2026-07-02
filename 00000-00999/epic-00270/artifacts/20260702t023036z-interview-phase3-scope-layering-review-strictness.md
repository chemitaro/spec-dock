---
種別: interview
ID: "20260702t023036z-interview"
タイトル: "Phase 3 Scope Layering Review Strictness"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["epic-00270"]
関連:
  - "20260702t022907z-adr"
  - "20260702t020503z-01-disc"
scope: "epic"
scope_id: "epic-00270"
created_at: "2026-07-02T02:30:36Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "artifacts/20260702t022907z-adr-scope-layering-reference-publication-surface.md"
  - "artifacts/20260702t022727z-research-deep-consultant-scope-layering-publication-recommendation.md"
reflected_to: []
---

# 20260702t023036z-interview Phase 3 Scope Layering Review Strictness

## 正式質問として扱う理由

- 影響する artifact:
  - `design.md`:
    - scope-layering rule を guidance として扱うか、review gate として扱うかに影響する。
  - `plan.md`:
    - Issue 05 の smoke tests / validation checks の強さに影響する。
  - `report.md`:
    - reviewer findings の disposition と waiver 条件に影響する。
- chat 上の軽微な一問では足りない理由:
  - `docs/authoring/scope-layering.md` を作るだけでは、違反をどこまでfailさせるかが決まらない。強すぎると開発が重くなり、弱すぎると参照docが読まれない。

## 質問の目的

- 対象者:
  - product maintainer / Epic owner
- 何を明確にする質問か:
  - spec-reviewer / smoke tests が scope-layering violation をどの強さで扱うべきか。
- 回答が後続判断へ与える影響:
  - reviewer checklist、template smoke tests、negative grep/smoke checks、waiver rules に影響する。

## 質問

- pressure-test question:
  - Scope-layering reference を作っても、レビューやテストが何も検出しないなら形骸化します。一方で何でもfailにすると、実用性が落ちます。どの強さがよいですか。
- 質問:
  - scope-layering violation は、reviewer / smoke tests でどの程度 fail させるべきですか。
- 回答してほしいこと:
  - A / B / C のどれに近いかを教えてください。

## source-grounded context

- 確認済みの docs / code / tests / ADR / artifacts / primary source:
  - Accepted ADR: `scope-layering.md` を1つのprovider-side referenceとして作り、既存docs/skills/templatesは薄くリンクする。
  - Deep consultant recommendation: smoke checks should detect local artifact authority leaks, duplicated full table drift, missing inbound links, template bloat, decision-only Issues treated as execution-ready, raw artifacts treated as canonical authority.
  - Existing workflow requires fresh `spec-reviewer` pass for phase promotion.
- local context で解決できたこと:
  - `scope-layering.md` の存在とリンクは smoke test で確認すべき。
  - raw artifacts を provider docs の canonical authority にしないことは強く守るべき。
  - ただし、すべての軽微な wording drift を fail にする必要はない。
- まだ人間判断が必要な理由:
  - reviewer/test strictness は開発速度と品質保証のバランスであり、repo facts だけでは決められない。

## 回答案

- Option A:
  - 軽め。`scope-layering.md` の存在と主要リンクだけを smoke test し、内容違反は reviewer warning 中心にする。
- Option B:
  - 中程度。構造上の違反はfail、解釈余地のあるものはreviewer findingにする。Fail対象は、provider docsのlocal artifact authority leak、full table duplication、required inbound link missing、templatesへの長大なscope table埋め込み、decision-only Issueをexecution-readyにする記述、raw artifactをcanonical authorityにする記述。
- Option C:
  - 強め。scope-layering違反は基本的にspec-reviewer fail / smoke test fail とし、waiver なしではphase promotion不可にする。

## Codex の分析

- 判断軸:
  - 参照docの形骸化防止。
  - 不要なfailによる作業停滞の回避。
  - テストで機械的に検出できるものと、人間/ reviewer判断が必要なものの分離。
- tradeoff:
  - Option A は軽いが、今回の設計判断が運用に効かない恐れがある。
  - Option B は、機械的に検出できる構造違反だけをfailにできるためバランスがよい。
  - Option C は強いが、抽象的なscope判断まで機械的failにすると false positive が増える。
- リスク:
  - Fail対象を広げすぎると、workflow docs の自然な説明まで禁止してしまう。
  - Warning中心にしすぎると、templatesが再び重くなったり、raw artifact authority leakが入りやすい。

## Codex の推奨案

- 推奨:
  - Option B。
- 理由:
  - Deep consultant recommendation の smoke checks と一致する。
  - 機械的に守れる境界はfail-closedにし、設計判断が必要なものはspec-reviewer findingへ残せる。
  - 既存SpecDockのfresh reviewer gate文化とも整合する。
- 未回答時の影響:
  - Issue 05 の smoke test acceptance criteria と Issue 03 の reviewer/docs guidance が固定できない。

## ユーザー回答

- answer capture:
  - Option B を採用する。
  - 機械的に検出できる構造違反は fail させ、解釈余地のあるものは reviewer finding として扱う。
- 回答:
  - Scope-layering enforcement は中程度にする。Fail対象は、provider docs の local artifact authority leak、full table duplication、required inbound link missing、templates への長大な scope table 埋め込み、decision-only Issue を execution-ready にする記述、raw artifact を canonical authority にする記述とする。
- 回答日時:
  - 2026-07-02

## 追加確認の要否

- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - Initiative/Epic templates に DDD/EDA 構造をどの程度入れるか。

## 採用判断

- adoption_status:
  - adopted
- adoption target:
  - `design.md` / `plan.md` / Issue 05 acceptance criteria / `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - Scope-layering reference を形骸化させず、かつ抽象的な判断を過剰に機械failしないバランスとして採用する。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意

- `requirement.md`:
  - Acceptance criteria の品質保証水準に影響する。
- `design.md`:
  - Scope-layering rule の enforcement model を中程度の fail/reviewer finding split として反映する。
- `plan.md`:
  - Smoke test / reviewer guidance Issue の acceptance criteria に、構造違反failとreviewer findingの境界を反映する。
- `ADR`:
  - Existing ADR に enforcement detailとして反映するか、canonical docs/reportに留めるか検討。
- reflected_to 更新方針:
  - 回答後、canonical docs と report ledger に反映した時点で更新する。
- adoption reflection:
  - Canonical docs / Issue 05 acceptance criteria / report ledger への反映は次工程。
